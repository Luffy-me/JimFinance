"""
Reasoning Memory Service - Persistent storage and retrieval of debate records.

Stores past financial decision debates and enables:
- Learning from past decisions
- Finding similar past debates
- Tracking decision outcomes
- Improving recommendation confidence
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.database import ReasoningMemory
from app.ml.agents.orchestrator import DebateRecord

logger = logging.getLogger(__name__)


class ReasoningMemoryService:
    """Manages persistent storage and retrieval of reasoning/debate records."""
    
    def __init__(self):
        """Initialize memory service."""
        self.logger = logger
    
    def store_debate_record(
        self,
        db: Session,
        user_id: int,
        debate_record: DebateRecord,
        quantitative_analysis: Dict[str, Any],
        scenario_analysis: Dict[str, Any],
        decision_type: str = "purchase",
        country: str = "US",
        inflation_scenario: str = "moderate",
    ) -> Optional[ReasoningMemory]:
        """
        Store a debate record for future reference and learning.
        
        Args:
            db: Database session
            user_id: User ID
            debate_record: Complete debate record from orchestrator
            quantitative_analysis: Results from quantitative engine
            scenario_analysis: Scenario analysis results
            decision_type: Type of decision (purchase, investment, etc.)
            country: Country for inflation context
            inflation_scenario: Inflation scenario used
            
        Returns:
            Created ReasoningMemory record or None if failed
        """
        try:
            # Extract positions from debate record
            strategist_pos = None
            critic_pos = None
            strategist_chain = None
            critic_chain = None
            
            if debate_record.positions:
                for pos in debate_record.positions:
                    if "strategist" in pos.agent_name.lower():
                        strategist_pos = pos.analysis
                        strategist_chain = pos.reasoning_chain
                    elif "critic" in pos.agent_name.lower():
                        critic_pos = pos.analysis
                        critic_chain = pos.reasoning_chain
            
            # Extract decision context
            context = debate_record.decision_context or {}
            
            # Create memory record
            memory = ReasoningMemory(
                user_id=user_id,
                decision_id=debate_record.decision_id,
                decision_name=context.get("decision_name", "Unnamed Decision"),
                decision_description=context.get("description", ""),
                decision_type=decision_type,
                purchase_price=context.get("purchase_price"),
                monthly_payment=context.get("monthly_payment"),
                months_to_pay=context.get("months_to_pay", 1),
                user_monthly_income=context.get("monthly_income", 0),
                user_monthly_expenses=context.get("monthly_expenses", 0),
                user_current_balance=context.get("current_balance", 0),
                user_recurring_expenses=context.get("recurring_expenses", 0),
                strategist_position=strategist_pos,
                critic_position=critic_pos,
                synthesis=debate_record.synthesis,
                strategist_reasoning_chain=strategist_chain,
                critic_reasoning_chain=critic_chain,
                quantitative_analysis=quantitative_analysis,
                scenario_analysis=scenario_analysis,
                final_recommendation=debate_record.final_recommendation,
                confidence_score=debate_record.synthesis.get("overall_confidence", 0.5) if debate_record.synthesis else 0.5,
                inflation_scenario=inflation_scenario,
                country=country,
            )
            
            db.add(memory)
            db.commit()
            db.refresh(memory)
            
            self.logger.info(f"Stored debate record {debate_record.decision_id} for user {user_id}")
            return memory
            
        except Exception as e:
            self.logger.error(f"Failed to store debate record: {e}")
            db.rollback()
            return None
    
    def find_similar_debates(
        self,
        db: Session,
        user_id: int,
        decision_type: str,
        purchase_price: Optional[float] = None,
        monthly_income: Optional[float] = None,
        limit: int = 5,
        days_back: int = 365,
    ) -> List[ReasoningMemory]:
        """
        Find similar past debates for learning/comparison.
        
        Args:
            db: Database session
            user_id: User ID
            decision_type: Type of decision to match
            purchase_price: Optional price range to filter
            monthly_income: Optional income level to filter
            limit: Maximum number of results
            days_back: How far back to search
            
        Returns:
            List of similar debate records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = db.query(ReasoningMemory).filter(
            (ReasoningMemory.user_id == user_id) &
            (ReasoningMemory.decision_type == decision_type) &
            (ReasoningMemory.created_at >= cutoff_date)
        )
        
        # Filter by price range if provided
        if purchase_price:
            price_tolerance = purchase_price * 0.3  # ±30%
            query = query.filter(
                (ReasoningMemory.purchase_price >= purchase_price - price_tolerance) &
                (ReasoningMemory.purchase_price <= purchase_price + price_tolerance)
            )
        
        # Filter by income level if provided
        if monthly_income:
            income_tolerance = monthly_income * 0.3  # ±30%
            query = query.filter(
                (ReasoningMemory.user_monthly_income >= monthly_income - income_tolerance) &
                (ReasoningMemory.user_monthly_income <= monthly_income + income_tolerance)
            )
        
        results = query.order_by(
            ReasoningMemory.created_at.desc()
        ).limit(limit).all()
        
        self.logger.info(f"Found {len(results)} similar debates for user {user_id}")
        return results
    
    def get_debate_record(
        self,
        db: Session,
        user_id: int,
        decision_id: str,
    ) -> Optional[ReasoningMemory]:
        """
        Retrieve a specific debate record.
        
        Args:
            db: Database session
            user_id: User ID for access control
            decision_id: Decision ID to retrieve
            
        Returns:
            ReasoningMemory record or None
        """
        return db.query(ReasoningMemory).filter(
            (ReasoningMemory.user_id == user_id) &
            (ReasoningMemory.decision_id == decision_id)
        ).first()
    
    def record_outcome(
        self,
        db: Session,
        user_id: int,
        decision_id: str,
        outcome: str,
        notes: str = "",
    ) -> bool:
        """
        Record the actual outcome of a decision.
        
        Args:
            db: Database session
            user_id: User ID
            decision_id: Decision ID
            outcome: "purchased", "not_purchased", "regretted", "satisfied"
            notes: Optional notes about the outcome
            
        Returns:
            True if successful, False otherwise
        """
        try:
            memory = self.get_debate_record(db, user_id, decision_id)
            if not memory:
                self.logger.warning(f"Decision {decision_id} not found")
                return False
            
            memory.actual_outcome = outcome
            memory.outcome_date = datetime.utcnow()
            memory.outcome_notes = notes
            
            db.commit()
            self.logger.info(f"Recorded outcome for decision {decision_id}: {outcome}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record outcome: {e}")
            db.rollback()
            return False
    
    def get_decision_statistics(
        self,
        db: Session,
        user_id: int,
        days_back: int = 365,
    ) -> Dict[str, Any]:
        """
        Get statistics on past decisions and their outcomes.
        
        Args:
            db: Database session
            user_id: User ID
            days_back: How far back to analyze
            
        Returns:
            Statistics dictionary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        records = db.query(ReasoningMemory).filter(
            (ReasoningMemory.user_id == user_id) &
            (ReasoningMemory.created_at >= cutoff_date)
        ).all()
        
        if not records:
            return {"total_decisions": 0}
        
        # Calculate statistics
        outcomes = {}
        confidence_scores = []
        recommendations = {}
        
        for record in records:
            # Outcome statistics
            if record.actual_outcome:
                outcomes[record.actual_outcome] = outcomes.get(record.actual_outcome, 0) + 1
            
            # Confidence statistics
            if record.confidence_score:
                confidence_scores.append(record.confidence_score)
            
            # Recommendation statistics
            if record.final_recommendation:
                recommendations[record.final_recommendation] = recommendations.get(
                    record.final_recommendation, 0
                ) + 1
        
        return {
            "total_decisions": len(records),
            "decisions_with_outcomes": sum(outcomes.values()),
            "outcomes": outcomes,
            "average_confidence": (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores else 0
            ),
            "recommendations": recommendations,
            "decision_types": self._count_decision_types(records),
            "period_days": days_back,
        }
    
    def get_recommendation_accuracy(
        self,
        db: Session,
        user_id: int,
        recommendation: str = "recommended",
        days_back: int = 365,
    ) -> Dict[str, Any]:
        """
        Calculate accuracy of specific recommendation type.
        
        Args:
            db: Database session
            user_id: User ID
            recommendation: Recommendation type to analyze
            days_back: Analysis period
            
        Returns:
            Accuracy statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        records = db.query(ReasoningMemory).filter(
            (ReasoningMemory.user_id == user_id) &
            (ReasoningMemory.final_recommendation == recommendation) &
            (ReasoningMemory.actual_outcome != None) &
            (ReasoningMemory.created_at >= cutoff_date)
        ).all()
        
        if not records:
            return {
                "recommendation": recommendation,
                "sample_size": 0,
                "insufficient_data": True,
            }
        
        positive_outcomes = sum(
            1 for r in records
            if r.actual_outcome in ["purchased", "satisfied"]
        )
        
        return {
            "recommendation": recommendation,
            "sample_size": len(records),
            "positive_outcomes": positive_outcomes,
            "accuracy": positive_outcomes / len(records) if records else 0,
            "average_confidence": (
                sum(r.confidence_score for r in records) / len(records)
                if records else 0
            ),
        }
    
    @staticmethod
    def _count_decision_types(records: List[ReasoningMemory]) -> Dict[str, int]:
        """Count decision types in records."""
        counts = {}
        for record in records:
            counts[record.decision_type] = counts.get(record.decision_type, 0) + 1
        return counts
