"""
Agent Service - Orchestrates multi-agent reasoning system.
Handles data collection, agent coordination, and result synthesis.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.database import (
    User,
    Transaction,
    Account,
    Category,
)
from app.ml.agents.types import (
    FinancialMetrics,
    TransactionContext,
    StrategistOutput,
    CriticOutput,
    SynthesisOutput,
    FinancialInsight,
)
from app.ml.agents.strategist import StrategistAgent
from app.ml.agents.critic import CriticAgent
from app.ml.agents.synthesizer import SynthesisEngine

logger = logging.getLogger(__name__)


class AgentService:
    """Orchestrates multi-agent reasoning system."""
    
    def __init__(self):
        """Initialize Agent Service."""
        self.logger = logging.getLogger(f"{__name__}.AgentService")
        self.strategist = None
        self.critic = None
        self.synthesizer = SynthesisEngine()
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize AI agents."""
        try:
            self.strategist = StrategistAgent()
            self.logger.info("✓ Strategist Agent initialized")
        except Exception as e:
            self.logger.warning(f"✗ Failed to initialize Strategist: {e}")
        
        try:
            self.critic = CriticAgent()
            self.logger.info("✓ Critic Agent initialized")
        except Exception as e:
            self.logger.warning(f"✗ Failed to initialize Critic: {e}")
    
    async def analyze_user_finances(
        self,
        user_id: int,
        db: Session,
        days: int = 30,
    ) -> Optional[SynthesisOutput]:
        """
        Perform complete financial analysis for user.
        
        Args:
            user_id: User ID
            db: Database session
            days: Days of history to analyze
            
        Returns:
            Synthesized analysis or None if analysis failed
        """
        try:
            # Fetch user data
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                self.logger.error(f"User {user_id} not found")
                return None
            
            # Collect financial metrics and context
            financial_metrics = self._get_financial_metrics(user_id, db, days)
            transaction_context = self._get_transaction_context(user_id, db, days)
            
            if not financial_metrics or not transaction_context:
                self.logger.error(f"Failed to collect data for user {user_id}")
                return None
            
            # Run agents if available
            strategist_output = None
            critic_output = None
            
            if self.strategist:
                try:
                    self.logger.info(f"Running Strategist for user {user_id}")
                    strategist_result = await self.strategist.analyze(
                        financial_metrics,
                        transaction_context,
                        user_id,
                    )
                    strategist_output = StrategistOutput(**strategist_result)
                except Exception as e:
                    self.logger.warning(f"Strategist analysis failed: {e}")
            
            if self.critic:
                try:
                    self.logger.info(f"Running Critic for user {user_id}")
                    critic_result = await self.critic.analyze(
                        financial_metrics,
                        transaction_context,
                        user_id,
                    )
                    critic_output = CriticOutput(**critic_result)
                except Exception as e:
                    self.logger.warning(f"Critic analysis failed: {e}")
            
            # If we have both outputs, synthesize
            if strategist_output and critic_output:
                try:
                    synthesis = self.synthesizer.synthesize(
                        strategist_output,
                        critic_output,
                    )
                    self.logger.info(f"Analysis complete for user {user_id}")
                    return synthesis
                except Exception as e:
                    self.logger.error(f"Synthesis failed: {e}")
                    return None
            
            self.logger.warning("Incomplete agent analysis - skipping synthesis")
            return None
            
        except Exception as e:
            self.logger.error(f"Financial analysis failed: {e}")
            return None
    
    def _get_financial_metrics(
        self,
        user_id: int,
        db: Session,
        days: int,
    ) -> Optional[FinancialMetrics]:
        """
        Collect financial metrics for user.
        
        Args:
            user_id: User ID
            db: Database session
            days: Days of history
            
        Returns:
            FinancialMetrics or None
        """
        try:
            # Get transactions in period
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            transactions = db.query(Transaction).filter(
                (Transaction.user_id == user_id) &
                (Transaction.transaction_date >= cutoff_date)
            ).all()
            
            # Get accounts for user
            accounts = db.query(Account).filter(
                Account.user_id == user_id
            ).all()
            
            if not transactions or not accounts:
                return None
            
            # Calculate metrics
            total_income = sum(
                t.amount for t in transactions 
                if t.amount > 0 and t.category and t.category.type == "income"
            )
            total_expenses = sum(
                abs(t.amount) for t in transactions 
                if t.amount < 0
            )
            
            # Savings rate
            if total_income > 0:
                savings_rate = (total_income - total_expenses) / total_income
            else:
                savings_rate = 0.0
            
            # Average monthly expense
            avg_monthly = total_expenses / (days / 30.0) if days > 0 else 0
            
            # Category breakdown
            category_breakdown = self._calculate_category_breakdown(transactions)
            
            # Account balances
            account_balances = {
                acc.name: float(acc.current_balance or 0)
                for acc in accounts
            }
            
            # Recurring expenses
            recurring_transactions = [
                t for t in transactions 
                if t.is_recurring
            ]
            recurring_expenses = sum(
                abs(t.amount) for t in recurring_transactions
            )
            
            # Average transaction size
            avg_trans_size = (
                total_expenses / len(transactions)
                if transactions 
                else 0
            )
            
            return FinancialMetrics(
                total_income=total_income,
                total_expenses=total_expenses,
                savings_rate=savings_rate,
                average_monthly_expense=avg_monthly,
                expense_categories=category_breakdown,
                account_balances=account_balances,
                recurring_expenses=recurring_expenses,
                average_transaction_size=avg_trans_size,
                transaction_count=len(transactions),
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get financial metrics: {e}")
            return None
    
    def _get_transaction_context(
        self,
        user_id: int,
        db: Session,
        days: int,
    ) -> Optional[TransactionContext]:
        """
        Collect transaction context for user.
        
        Args:
            user_id: User ID
            db: Database session
            days: Days of history
            
        Returns:
            TransactionContext or None
        """
        try:
            # Get transactions
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            transactions = db.query(Transaction).filter(
                (Transaction.user_id == user_id) &
                (Transaction.transaction_date >= cutoff_date)
            ).order_by(Transaction.transaction_date.desc()).all()
            
            if not transactions:
                return None
            
            # Format recent transactions
            recent_trans = [
                {
                    "merchant": t.merchant or "Unknown",
                    "amount": float(t.amount),
                    "category": t.category.name if t.category else "Unknown",
                    "date": t.transaction_date.isoformat(),
                }
                for t in transactions[:10]
            ]
            
            # Calculate trends
            trends = self._calculate_spending_trends(transactions)
            
            # Category breakdown
            category_breakdown = self._calculate_category_breakdown_detailed(
                transactions
            )
            
            # Recurring patterns
            recurring = [
                {
                    "merchant": t.merchant or "Unknown",
                    "amount": float(t.amount),
                    "frequency": t.recurrence_frequency or "unknown",
                }
                for t in transactions
                if t.is_recurring
            ][:5]
            
            # Anomalies (placeholder)
            anomalies = []
            
            return TransactionContext(
                recent_transactions=recent_trans,
                spending_trends=trends,
                category_breakdown=category_breakdown,
                recurring_patterns=recurring,
                anomalies_detected=anomalies,
                time_period=f"{days}_days",
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get transaction context: {e}")
            return None
    
    @staticmethod
    def _calculate_category_breakdown(
        transactions: List[Transaction],
    ) -> Dict[str, float]:
        """Calculate spending by category."""
        breakdown = {}
        
        for trans in transactions:
            if trans.amount < 0 and trans.category:
                category = trans.category.name
                breakdown[category] = (
                    breakdown.get(category, 0) + abs(trans.amount)
                )
        
        return breakdown
    
    @staticmethod
    def _calculate_category_breakdown_detailed(
        transactions: List[Transaction],
    ) -> Dict[str, Dict[str, float]]:
        """Calculate detailed category breakdown."""
        breakdown = {}
        
        for trans in transactions:
            if trans.category:
                category = trans.category.name
                if category not in breakdown:
                    breakdown[category] = {
                        "total": 0,
                        "count": 0,
                        "average": 0,
                    }
                
                amount = abs(trans.amount)
                breakdown[category]["total"] += amount
                breakdown[category]["count"] += 1
                breakdown[category]["average"] = (
                    breakdown[category]["total"] / 
                    breakdown[category]["count"]
                )
        
        return breakdown
    
    @staticmethod
    def _calculate_spending_trends(
        transactions: List[Transaction],
    ) -> Dict[str, float]:
        """Calculate spending trends."""
        if len(transactions) < 2:
            return {}
        
        trends = {}
        
        # Week-over-week trend
        this_week = sum(
            abs(t.amount) for t in transactions
            if (datetime.utcnow() - t.transaction_date).days <= 7 and t.amount < 0
        )
        last_week = sum(
            abs(t.amount) for t in transactions
            if (datetime.utcnow() - t.transaction_date).days > 7
            and (datetime.utcnow() - t.transaction_date).days <= 14
            and t.amount < 0
        )
        
        if last_week > 0:
            trends["week_over_week"] = (this_week - last_week) / last_week
        
        return trends
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all agents.
        
        Returns:
            Agent statistics
        """
        stats = {
            "strategist": (
                self.strategist.get_stats() 
                if self.strategist 
                else {"status": "not_initialized"}
            ),
            "critic": (
                self.critic.get_stats() 
                if self.critic 
                else {"status": "not_initialized"}
            ),
        }
        
        return stats
