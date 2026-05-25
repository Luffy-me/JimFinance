"""
Behavioral Analyzer - Detects financial patterns and generates explainable insights.
Analyzes spending triggers, seasonal patterns, emotional spending, and behavioral profiles.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from decimal import Decimal
import statistics
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.database import Transaction, FinancialMemory, BehavioralProfile
from app.ml.financial_intelligence.behavioral_analyzer import BehavioralAnalyzer as BaseBehavioralAnalyzer

logger = logging.getLogger(__name__)


class BehavioralAnalyzer:
    """Analyzes financial behavior to identify patterns and generate explainable insights."""
    
    def __init__(self, db: Session):
        """Initialize behavioral analyzer with database session."""
        self.db = db
        self.base_analyzer = BaseBehavioralAnalyzer(db)
    
    async def analyze_spending_patterns(
        self,
        user_id: int,
        days_back: int = 90,
    ) -> Dict:
        """
        Analyze spending patterns over time period.
        
        Args:
            user_id: User ID
            days_back: Days to analyze
            
        Returns:
            Dictionary with spending patterns and insights
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            transactions = self.db.query(Transaction).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == "expense",
                    Transaction.transaction_date >= cutoff_date
                )
            ).all()
            
            if not transactions:
                return {"patterns": [], "insights": []}
            
            # Analyze by category
            category_spending = defaultdict(list)
            for txn in transactions:
                category = txn.category.category_type if txn.category else "unknown"
                category_spending[category].append(float(txn.amount))
            
            # Calculate statistics
            patterns = []
            for category, amounts in category_spending.items():
                if amounts:
                    patterns.append({
                        "category": category,
                        "total": sum(amounts),
                        "count": len(amounts),
                        "average": statistics.mean(amounts),
                        "median": statistics.median(amounts),
                        "stdev": statistics.stdev(amounts) if len(amounts) > 1 else 0,
                        "min": min(amounts),
                        "max": max(amounts),
                    })
            
            # Analyze by month
            monthly_spending = defaultdict(float)
            for txn in transactions:
                month_key = txn.transaction_date.strftime("%Y-%m")
                monthly_spending[month_key] += float(txn.amount)
            
            # Analyze by day of week
            dow_spending = defaultdict(list)
            for txn in transactions:
                dow = txn.transaction_date.strftime("%A")
                dow_spending[dow].append(float(txn.amount))
            
            dow_patterns = {
                dow: {
                    "count": len(amounts),
                    "total": sum(amounts),
                    "average": statistics.mean(amounts),
                }
                for dow, amounts in dow_spending.items()
            }
            
            # Generate insights
            insights = self._generate_spending_insights(
                category_spending,
                monthly_spending,
                dow_patterns,
                patterns
            )
            
            return {
                "analysis_period_days": days_back,
                "transaction_count": len(transactions),
                "total_spending": sum(float(t.amount) for t in transactions),
                "by_category": patterns,
                "by_month": dict(monthly_spending),
                "by_day_of_week": dow_patterns,
                "insights": insights,
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spending patterns: {str(e)}")
            return {"patterns": [], "insights": []}
    
    async def detect_behavioral_triggers(
        self,
        user_id: int,
        days_back: int = 60,
    ) -> List[Dict]:
        """
        Detect behavioral triggers for spending.
        
        Args:
            user_id: User ID
            days_back: Days to analyze
            
        Returns:
            List of identified triggers with evidence
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get anomalous transactions
            anomalies = self.db.query(Transaction).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.is_anomaly == True,
                    Transaction.transaction_date >= cutoff_date
                )
            ).all()
            
            if not anomalies:
                return []
            
            triggers = []
            
            # Analyze temporal patterns in anomalies
            anomaly_dates = [a.transaction_date for a in anomalies]
            
            # Check for weekend clustering
            weekend_count = sum(
                1 for d in anomaly_dates if d.weekday() >= 5
            )
            if weekend_count > len(anomalies) * 0.4:
                triggers.append({
                    "trigger": "weekend_spending",
                    "confidence": min(0.95, weekend_count / len(anomalies)),
                    "description": "You tend to spend more on weekends",
                    "evidence": f"{weekend_count} out of {len(anomalies)} anomalies occurred on weekends",
                    "examples": self._get_example_transactions(anomalies, 3)
                })
            
            # Check for post-paycheck spending
            paycheck_triggers = self._detect_paycheck_triggers(user_id, anomalies)
            triggers.extend(paycheck_triggers)
            
            # Check for stress-related spending
            stress_triggers = await self._detect_stress_spending(user_id, anomalies)
            triggers.extend(stress_triggers)
            
            return triggers
            
        except Exception as e:
            logger.error(f"Error detecting behavioral triggers: {str(e)}")
            return []
    
    async def analyze_seasonal_patterns(
        self,
        user_id: int,
        months_back: int = 12,
    ) -> Dict:
        """
        Analyze seasonal spending patterns.
        
        Args:
            user_id: User ID
            months_back: Months to analyze
            
        Returns:
            Seasonal patterns and insights
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=months_back*30)
            
            transactions = self.db.query(Transaction).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == "expense",
                    Transaction.transaction_date >= cutoff_date
                )
            ).all()
            
            if not transactions:
                return {"seasonal_patterns": []}
            
            # Group by month
            monthly_patterns = defaultdict(lambda: {"spending": 0, "count": 0})
            
            for txn in transactions:
                month = txn.transaction_date.month
                monthly_patterns[month]["spending"] += float(txn.amount)
                monthly_patterns[month]["count"] += 1
            
            # Calculate averages and identify peaks
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            
            seasonal_patterns = []
            spending_values = [p["spending"] for p in monthly_patterns.values()]
            
            if spending_values:
                avg_spending = statistics.mean(spending_values)
                stdev_spending = statistics.stdev(spending_values) if len(spending_values) > 1 else 0
                
                for month_num, pattern in sorted(monthly_patterns.items()):
                    z_score = (pattern["spending"] - avg_spending) / (stdev_spending or 1)
                    
                    seasonal_patterns.append({
                        "month": month_names[month_num - 1],
                        "month_number": month_num,
                        "average_spending": pattern["spending"] / pattern["count"],
                        "total_spending": pattern["spending"],
                        "transaction_count": pattern["count"],
                        "z_score": z_score,
                        "deviation": "high" if z_score > 1 else "low" if z_score < -1 else "normal"
                    })
            
            return {"seasonal_patterns": seasonal_patterns}
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal patterns: {str(e)}")
            return {"seasonal_patterns": []}
    
    async def calculate_risk_tolerance(self, user_id: int) -> Dict:
        """
        Calculate user's risk tolerance based on financial behavior.
        
        Args:
            user_id: User ID
            
        Returns:
            Risk profile with score and classification
        """
        try:
            # Get spending volatility
            last_90_days = datetime.utcnow() - timedelta(days=90)
            transactions = self.db.query(Transaction).filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == "expense",
                    Transaction.transaction_date >= last_90_days
                )
            ).all()
            
            if not transactions:
                return {"risk_tolerance": "unknown", "risk_score": 0.5}
            
            amounts = [float(t.amount) for t in transactions]
            
            # Calculate metrics
            avg_amount = statistics.mean(amounts)
            volatility = statistics.stdev(amounts) / avg_amount if avg_amount > 0 else 0
            
            # Count anomalies
            anomaly_ratio = sum(1 for t in transactions if t.is_anomaly) / len(transactions)
            
            # Check for investment transactions
            investment_count = sum(
                1 for t in transactions if t.category and t.category.category_type == "investment"
            )
            
            # Calculate risk score
            risk_score = (
                min(volatility, 1.0) * 0.4 +  # Spending volatility
                anomaly_ratio * 0.3 +  # Anomaly frequency
                min(investment_count / 10, 1.0) * 0.3  # Investment activity
            )
            
            # Classify
            if risk_score < 0.33:
                classification = "conservative"
            elif risk_score < 0.67:
                classification = "moderate"
            else:
                classification = "aggressive"
            
            # Store or update profile
            profile = self.db.query(BehavioralProfile).filter(
                BehavioralProfile.user_id == user_id
            ).first()
            
            if profile:
                profile.risk_score = risk_score
                profile.risk_tolerance = classification
            else:
                profile = BehavioralProfile(
                    user_id=user_id,
                    risk_score=risk_score,
                    risk_tolerance=classification
                )
                self.db.add(profile)
            
            self.db.commit()
            
            return {
                "risk_tolerance": classification,
                "risk_score": risk_score,
                "spending_volatility": volatility,
                "anomaly_ratio": anomaly_ratio,
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk tolerance: {str(e)}")
            return {"risk_tolerance": "unknown", "risk_score": 0.5}
    
    def _generate_spending_insights(
        self,
        category_spending: dict,
        monthly_spending: dict,
        dow_patterns: dict,
        patterns: List[Dict]
    ) -> List[Dict]:
        """Generate explainable insights from spending analysis."""
        insights = []
        
        # Top spending categories
        if patterns:
            top_patterns = sorted(patterns, key=lambda p: p["total"], reverse=True)[:3]
            top_categories = ", ".join([p["category"] for p in top_patterns])
            insights.append({
                "type": "top_categories",
                "description": f"Your highest spending categories are: {top_categories}",
                "priority": "high"
            })
        
        # High variability categories
        for pattern in patterns:
            if pattern["stdev"] > pattern["average"] * 0.5:
                insights.append({
                    "type": "variable_spending",
                    "category": pattern["category"],
                    "description": f"Your {pattern['category']} spending is highly variable "
                                  f"(from ${pattern['min']:.2f} to ${pattern['max']:.2f})",
                    "priority": "medium"
                })
        
        return insights
    
    def _detect_paycheck_triggers(self, user_id: int, anomalies: List[Transaction]) -> List[Dict]:
        """Detect post-paycheck spending patterns."""
        triggers = []
        
        # Look for salary transactions
        salary_txns = self.db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "income",
            )
        ).all()
        
        if salary_txns:
            # Check if anomalies cluster after paycheck dates
            paycheck_dates = [t.transaction_date for t in salary_txns]
            post_paycheck_anomalies = 0
            
            for anomaly in anomalies:
                for paycheck_date in paycheck_dates:
                    days_diff = (anomaly.transaction_date - paycheck_date).days
                    if 0 < days_diff <= 7:  # Within a week of paycheck
                        post_paycheck_anomalies += 1
            
            if post_paycheck_anomalies > len(anomalies) * 0.3:
                triggers.append({
                    "trigger": "post_paycheck_spending",
                    "confidence": min(0.9, post_paycheck_anomalies / len(anomalies)),
                    "description": "You tend to spend more right after receiving your paycheck",
                    "evidence": f"{post_paycheck_anomalies} anomalies occurred within a week of paychecks",
                })
        
        return triggers
    
    async def _detect_stress_spending(
        self,
        user_id: int,
        anomalies: List[Transaction]
    ) -> List[Dict]:
        """Detect stress-related spending triggers."""
        triggers = []
        
        # Look for stress markers: multiple transactions in short time, high amounts
        if len(anomalies) > 0:
            # Check for clustering (many transactions in short period)
            dates = [a.transaction_date for a in anomalies]
            dates.sort()
            
            for i in range(len(dates) - 2):
                time_window = dates[i+2] - dates[i]
                if time_window.days <= 3:  # 3+ transactions in 3 days
                    triggers.append({
                        "trigger": "stress_or_impulse_spending",
                        "confidence": 0.7,
                        "description": "You overspend during potentially stressful periods "
                                      "(multiple purchases in short time)",
                        "evidence": f"Burst of {3} transactions in {time_window.days} days",
                    })
                    break
        
        return triggers
    
    def _get_example_transactions(
        self,
        transactions: List[Transaction],
        limit: int = 3
    ) -> List[Dict]:
        """Get example transactions for evidence."""
        examples = []
        for txn in transactions[:limit]:
            examples.append({
                "merchant": txn.merchant,
                "amount": float(txn.amount),
                "date": txn.transaction_date.isoformat() if txn.transaction_date else None,
                "category": txn.category.category_type if txn.category else "unknown"
            })
        return examples
