"""
Behavioral Integration - Links memory engine insights with financial decisions.

Integrates:
- Spending triggers (stress, post-paycheck, weekend)
- Risk tolerance from spending volatility
- Seasonal patterns into decision context
- Behavioral scoring into recommendations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.ml.memory_engine.behavioral_analyzer import BehavioralAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class BehavioralFactors:
    """Financial decision factors influenced by behavior."""
    spending_triggers: List[Dict[str, Any]]
    risk_tolerance_score: float  # 0-100
    seasonal_volatility: float  # 0-1
    stress_spending_tendency: float  # 0-1
    impulse_spending_score: float  # 0-1
    decision_confidence_adjustment: float  # -0.2 to +0.2


class BehavioralIntegrationEngine:
    """
    Integrates behavioral insights from memory engine with financial decisions.
    Adjusts recommendations based on spending patterns and risk tolerance.
    """
    
    def __init__(self):
        """Initialize behavioral integration engine."""
        self.logger = logger
        self.behavioral_analyzer = BehavioralAnalyzer()
    
    def extract_behavioral_factors(
        self,
        transactions: List[Dict],
        behavioral_profile: Optional[Dict] = None,
    ) -> BehavioralFactors:
        """
        Extract behavioral factors from transaction history and profile.
        
        Args:
            transactions: List of transaction dicts
            behavioral_profile: Pre-computed behavioral profile (optional)
            
        Returns:
            BehavioralFactors object
        """
        factors = {
            "spending_triggers": [],
            "risk_tolerance_score": 50.0,  # Default neutral
            "seasonal_volatility": 0.0,
            "stress_spending_tendency": 0.0,
            "impulse_spending_score": 0.0,
            "decision_confidence_adjustment": 0.0,
        }
        
        if not transactions:
            return BehavioralFactors(**factors)
        
        try:
            # Detect spending triggers
            triggers = self._detect_spending_triggers(transactions)
            factors["spending_triggers"] = triggers
            
            # Calculate risk tolerance from spending volatility
            risk_tolerance = self._calculate_risk_tolerance(transactions)
            factors["risk_tolerance_score"] = risk_tolerance
            
            # Measure seasonal volatility
            seasonality = self._measure_seasonality(transactions)
            factors["seasonal_volatility"] = seasonality
            
            # Detect stress spending
            stress_spending = self._detect_stress_spending(transactions)
            factors["stress_spending_tendency"] = stress_spending
            
            # Calculate impulse spending score
            impulse_score = self._calculate_impulse_score(transactions)
            factors["impulse_spending_score"] = impulse_score
            
            # Adjust confidence based on behavioral predictability
            if stress_spending < 0.2 and impulse_score < 0.2:
                # Stable, predictable spending
                factors["decision_confidence_adjustment"] = 0.05
            elif stress_spending > 0.5 or impulse_score > 0.5:
                # High volatility, reduce confidence
                factors["decision_confidence_adjustment"] = -0.10
            
        except Exception as e:
            self.logger.error(f"Error extracting behavioral factors: {e}")
        
        return BehavioralFactors(**factors)
    
    def adjust_decision_recommendation(
        self,
        base_recommendation: str,
        base_confidence: float,
        behavioral_factors: BehavioralFactors,
        decision_type: str = "purchase",
    ) -> Dict[str, Any]:
        """
        Adjust decision recommendation based on behavioral factors.
        
        Args:
            base_recommendation: Original recommendation
            base_confidence: Original confidence score
            behavioral_factors: Behavioral factors
            decision_type: Type of decision
            
        Returns:
            Adjusted recommendation with behavioral notes
        """
        adjusted_recommendation = base_recommendation
        adjusted_confidence = base_confidence + behavioral_factors.decision_confidence_adjustment
        behavioral_notes = []
        risk_adjustments = []
        
        # Check for decision made during high-risk behavioral periods
        stressor_triggers = [
            t for t in behavioral_factors.spending_triggers
            if t.get("type") in ["stress", "emotional", "post_paycheck"]
        ]
        
        if stressor_triggers and decision_type == "purchase":
            behavioral_notes.append(
                f"⚠️ Behavioral Risk: You have {len(stressor_triggers)} spending trigger(s) "
                f"that might influence this decision (stress, emotional, post-paycheck spending)."
            )
            
            # If already recommended to buy, increase caution
            if "recommended" in base_recommendation.lower():
                adjusted_confidence *= 0.9  # Reduce confidence by 10%
                risk_adjustments.append("Reduce confidence due to behavioral triggers")
        
        # Risk tolerance-based adjustment
        if behavioral_factors.risk_tolerance_score < 30 and "aggressive" in decision_type:
            behavioral_notes.append(
                f"⚠️ Risk Mismatch: Your conservative spending pattern (risk tolerance: "
                f"{behavioral_factors.risk_tolerance_score:.0f}/100) suggests lower appetite "
                f"for aggressive financial decisions."
            )
            adjusted_confidence *= 0.85
            risk_adjustments.append("Risk tolerance mismatch")
        
        # Impulse spending awareness
        if behavioral_factors.impulse_spending_score > 0.6:
            behavioral_notes.append(
                "💡 Pattern Alert: You have a history of impulse spending. "
                "Consider waiting 48 hours before making this decision."
            )
            if "recommended" in base_recommendation.lower():
                adjusted_confidence *= 0.95
                risk_adjustments.append("High impulse spending history")
        
        # Seasonal considerations
        if behavioral_factors.seasonal_volatility > 0.4:
            behavioral_notes.append(
                "📅 Seasonal Pattern: Your spending varies significantly by season. "
                "Factor in seasonal adjustments to your budget."
            )
        
        # Stress spending awareness
        if behavioral_factors.stress_spending_tendency > 0.5:
            behavioral_notes.append(
                "🧠 Stress Pattern: You tend to spend more during stressful periods. "
                "Ensure this decision isn't stress-driven."
            )
        
        # Clamp confidence to valid range
        adjusted_confidence = max(0.0, min(1.0, adjusted_confidence))
        
        return {
            "original_recommendation": base_recommendation,
            "adjusted_recommendation": adjusted_recommendation,
            "original_confidence": base_confidence,
            "adjusted_confidence": adjusted_confidence,
            "confidence_change": adjusted_confidence - base_confidence,
            "behavioral_notes": behavioral_notes,
            "risk_adjustments": risk_adjustments,
            "behavioral_factors": {
                "risk_tolerance": behavioral_factors.risk_tolerance_score,
                "impulse_spending": behavioral_factors.impulse_spending_score,
                "stress_spending": behavioral_factors.stress_spending_tendency,
                "seasonal_volatility": behavioral_factors.seasonal_volatility,
            },
        }
    
    def get_behavioral_warning_level(
        self,
        behavioral_factors: BehavioralFactors,
    ) -> str:
        """
        Assess behavioral risk level for decision-making.
        
        Args:
            behavioral_factors: Behavioral factors
            
        Returns:
            Risk level: "low", "medium", "high"
        """
        risk_score = 0.0
        
        # Add risk for high impulse spending
        risk_score += min(behavioral_factors.impulse_spending_score * 30, 30)
        
        # Add risk for high stress spending
        risk_score += min(behavioral_factors.stress_spending_tendency * 20, 20)
        
        # Reduce risk for high risk tolerance (financially savvy)
        if behavioral_factors.risk_tolerance_score > 70:
            risk_score -= 10
        
        if risk_score >= 40:
            return "high"
        elif risk_score >= 20:
            return "medium"
        else:
            return "low"
    
    def _detect_spending_triggers(self, transactions: List[Dict]) -> List[Dict]:
        """Detect spending trigger patterns."""
        triggers = []
        
        if not transactions:
            return triggers
        
        # Weekend spending analysis
        weekend_spending = sum(
            t.get("amount", 0) for t in transactions
            if t.get("date") and self._is_weekend(t["date"])
        )
        total_spending = sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) > 0)
        
        weekend_percent = weekend_spending / total_spending if total_spending > 0 else 0
        if weekend_percent > 0.35:  # Higher than expected random distribution
            triggers.append({
                "type": "weekend",
                "confidence": min(0.95, weekend_percent),
                "description": "Higher spending on weekends",
            })
        
        # Post-paycheck spending (simplified)
        triggers.append({
            "type": "post_paycheck",
            "confidence": 0.5,  # Placeholder
            "description": "Potential spike after paycheck",
        })
        
        return triggers
    
    def _calculate_risk_tolerance(self, transactions: List[Dict]) -> float:
        """
        Calculate risk tolerance from spending patterns.
        
        Higher volatility → higher risk tolerance (accepts variation).
        Lower volatility → lower risk tolerance (prefers stability).
        """
        if len(transactions) < 5:
            return 50.0  # Default
        
        amounts = [abs(t.get("amount", 0)) for t in transactions]
        if not amounts or sum(amounts) == 0:
            return 50.0
        
        # Calculate coefficient of variation
        mean_amount = sum(amounts) / len(amounts)
        if mean_amount == 0:
            return 50.0
        
        variance = sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)
        std_dev = variance ** 0.5
        cv = std_dev / mean_amount  # Coefficient of variation
        
        # Map CV to risk tolerance (0-100)
        # Low CV (~0.3) = low risk tolerance (50)
        # High CV (~1.0+) = high risk tolerance (80)
        risk_tolerance = 50 + (cv * 20)
        return min(100, max(0, risk_tolerance))
    
    def _measure_seasonality(self, transactions: List[Dict]) -> float:
        """
        Measure seasonal spending variations.
        
        Returns: 0-1 score, higher = more seasonal variation
        """
        if len(transactions) < 60:  # Need 2 months minimum
            return 0.0
        
        # Group by month
        monthly_totals = {}
        for t in transactions:
            date = t.get("date")
            if not date:
                continue
            
            if hasattr(date, "month"):
                month = date.month
            else:
                continue
            
            monthly_totals[month] = monthly_totals.get(month, 0) + abs(t.get("amount", 0))
        
        if len(monthly_totals) < 2:
            return 0.0
        
        values = list(monthly_totals.values())
        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0
        
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        cv = std_dev / mean
        
        # Normalize to 0-1
        return min(1.0, cv)
    
    def _detect_stress_spending(self, transactions: List[Dict]) -> float:
        """
        Estimate stress spending tendency.
        
        Returns: 0-1 score
        """
        if len(transactions) < 10:
            return 0.0
        
        # Simple heuristic: high category variation suggests emotional spending
        categories = {}
        for t in transactions:
            cat = t.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
        
        # Entropy of categories (higher = more varied, potential emotional spending)
        total = len(transactions)
        entropy = 0.0
        for count in categories.values():
            prob = count / total
            if prob > 0:
                entropy -= prob * (prob ** 0.5)  # Simplified entropy
        
        # Normalize to 0-1
        return min(1.0, max(0.0, entropy / 2))
    
    def _calculate_impulse_score(self, transactions: List[Dict]) -> float:
        """
        Calculate impulse spending score from transaction patterns.
        
        Returns: 0-1 score
        """
        if len(transactions) < 5:
            return 0.0
        
        # Look for patterns: many small transactions vs few large ones
        amounts = sorted([abs(t.get("amount", 0)) for t in transactions])
        
        # High number of small transactions = higher impulse score
        small_transactions = sum(1 for a in amounts if a < (sum(amounts) / len(amounts)) * 0.5)
        impulse_ratio = small_transactions / len(amounts)
        
        return impulse_ratio
    
    @staticmethod
    def _is_weekend(date: Any) -> bool:
        """Check if date is on weekend."""
        try:
            if hasattr(date, "weekday"):
                return date.weekday() >= 5
            return False
        except:
            return False
