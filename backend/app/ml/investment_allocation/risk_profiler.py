"""
Risk Profiler - Assess investor risk tolerance from behavioral and stated preferences.
Combines spending volatility analysis with questionnaire-based scoring.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RiskProfile:
    """User's risk tolerance profile."""
    overall_risk_score: float  # 0-100, where 0=very conservative, 100=very aggressive
    behavioral_risk_score: float  # From spending volatility
    stated_risk_score: float  # From questionnaire
    
    # Component scores
    loss_aversion: float  # 0-1, how much user dislikes losses
    volatility_tolerance: float  # 0-1, comfort with fluctuations
    time_horizon_score: float  # 0-1, based on investment horizon
    
    # Recommended allocation types
    recommended_allocation_type: str  # conservative, moderate, aggressive
    suitable_asset_classes: List[str]
    
    # Confidence
    confidence: float  # 0-1, how confident in this profile
    assumptions: List[str]
    
    timestamp: datetime
    
    def to_dict(self):
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result


class RiskProfiler:
    """
    Assess investor risk tolerance from multiple signals.
    Combines behavioral analysis with stated preferences.
    """
    
    # Default questionnaire scoring
    QUESTIONNAIRE_WEIGHTS = {
        "time_horizon": 0.25,
        "loss_tolerance": 0.25,
        "income_stability": 0.20,
        "investment_experience": 0.15,
        "financial_cushion": 0.15,
    }
    
    def __init__(self):
        """Initialize risk profiler."""
        self.logger = logger
    
    def calculate_behavioral_risk_score(
        self,
        spending_volatility: float,  # Standard deviation of spending
        mean_spending: float,
        loss_frequency: float,  # How often user has "losses" (unexpected expenses)
    ) -> float:
        """
        Calculate risk tolerance from spending behavior.
        
        Higher spending volatility suggests higher risk tolerance.
        More frequent losses suggest lower loss aversion.
        
        Args:
            spending_volatility: Standard deviation of monthly spending
            mean_spending: Average monthly spending
            loss_frequency: Frequency of unexpected expenses (0-1)
            
        Returns:
            Risk score 0-1
        """
        # Coefficient of variation (volatility as % of mean)
        cv = spending_volatility / (mean_spending + 1) if mean_spending > 0 else 0
        
        # Normalize CV to 0-1 (assuming max CV around 0.5)
        volatility_score = min(cv / 0.5, 1.0)
        
        # Loss frequency inversely related to loss aversion
        # Higher frequency of absorbing losses suggests more risk tolerance
        loss_aversion_score = 1 - min(loss_frequency, 1.0)
        
        # Composite behavioral score
        behavioral_score = 0.6 * volatility_score + 0.4 * loss_aversion_score
        
        self.logger.info(
            f"Behavioral risk: CV={cv:.3f}, volatility_score={volatility_score:.3f}, "
            f"loss_aversion={loss_aversion_score:.3f}, composite={behavioral_score:.3f}"
        )
        
        return float(behavioral_score)
    
    def calculate_stated_risk_score(
        self,
        questionnaire_responses: Dict[str, float],
    ) -> float:
        """
        Calculate risk tolerance from questionnaire responses.
        
        Args:
            questionnaire_responses: Dict with keys matching QUESTIONNAIRE_WEIGHTS
                Each value should be 0-1
                
        Returns:
            Risk score 0-1
        """
        stated_score = 0.0
        
        for key, weight in self.QUESTIONNAIRE_WEIGHTS.items():
            response = questionnaire_responses.get(key, 0.5)
            # Clamp to 0-1
            response = max(0, min(1, response))
            stated_score += weight * response
        
        self.logger.info(f"Stated risk score: {stated_score:.3f}")
        return float(stated_score)
    
    def calculate_time_horizon_score(self, years: int) -> float:
        """
        Calculate risk score adjustment based on time horizon.
        
        Longer horizons can tolerate more volatility.
        
        Args:
            years: Years until funds needed
            
        Returns:
            Time horizon score 0-1
        """
        if years < 2:
            return 0.0
        elif years < 5:
            return 0.3
        elif years < 10:
            return 0.6
        elif years < 20:
            return 0.8
        else:
            return 1.0
    
    def profile_investor(
        self,
        spending_volatility: Optional[float] = None,
        mean_spending: Optional[float] = None,
        loss_frequency: Optional[float] = None,
        questionnaire_responses: Optional[Dict[str, float]] = None,
        investment_horizon_years: int = 10,
    ) -> RiskProfile:
        """
        Create comprehensive risk profile for investor.
        
        Args:
            spending_volatility: Standard deviation of monthly spending
            mean_spending: Average monthly spending
            loss_frequency: Frequency of unexpected expenses (0-1)
            questionnaire_responses: Responses to risk questionnaire
            investment_horizon_years: Years until funds needed
            
        Returns:
            RiskProfile with overall assessment
        """
        # Calculate behavioral score
        behavioral_score = 0.5  # Default neutral
        if spending_volatility is not None and mean_spending is not None:
            behavioral_score = self.calculate_behavioral_risk_score(
                spending_volatility,
                mean_spending,
                loss_frequency or 0.2,
            )
        
        # Calculate stated score
        stated_score = 0.5  # Default neutral
        if questionnaire_responses:
            stated_score = self.calculate_stated_risk_score(questionnaire_responses)
        
        # Calculate time horizon score
        time_horizon_score = self.calculate_time_horizon_score(investment_horizon_years)
        
        # Overall score: weighted combination
        overall_score = (
            0.35 * behavioral_score +
            0.40 * stated_score +
            0.25 * time_horizon_score
        )
        
        # Loss aversion: inverse of behavioral volatility tolerance
        loss_aversion = 1 - behavioral_score
        
        # Volatility tolerance: combination of behavioral and time horizon
        volatility_tolerance = 0.5 * behavioral_score + 0.5 * time_horizon_score
        
        # Determine recommended allocation type
        if overall_score < 0.33:
            allocation_type = "conservative"
            suitable_assets = ["bonds", "cash", "dividend_stocks"]
        elif overall_score < 0.67:
            allocation_type = "moderate"
            suitable_assets = ["bonds", "stocks", "real_estate"]
        else:
            allocation_type = "aggressive"
            suitable_assets = ["stocks", "commodities", "alternative"]
        
        # Confidence depends on data quality
        confidence = 0.6
        if spending_volatility is not None and questionnaire_responses:
            confidence = 0.85  # High confidence with both signals
        elif spending_volatility is not None or questionnaire_responses:
            confidence = 0.7  # Medium confidence with one signal
        
        assumptions = [
            f"Investment horizon: {investment_horizon_years} years",
            "Behavioral data assumes past spending patterns predictive of risk tolerance",
            "Questionnaire responses assumed honest and consistent",
            "Risk profile may need adjustment with life changes",
            "Annual review recommended",
        ]
        
        profile = RiskProfile(
            overall_risk_score=overall_score * 100,
            behavioral_risk_score=behavioral_score * 100,
            stated_risk_score=stated_score * 100,
            loss_aversion=loss_aversion,
            volatility_tolerance=volatility_tolerance,
            time_horizon_score=time_horizon_score,
            recommended_allocation_type=allocation_type,
            suitable_asset_classes=suitable_assets,
            confidence=confidence,
            assumptions=assumptions,
            timestamp=datetime.utcnow(),
        )
        
        self.logger.info(f"Risk profile created: {allocation_type}, score={overall_score*100:.1f}")
        return profile
