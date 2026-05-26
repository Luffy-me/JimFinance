"""
Recession Detector - Recession probability and early warning models.

Provides:
- Recession probability scoring
- Leading indicator analysis
- Yield curve inversion detection
- Early warning signals
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class RecessionRisk(str, Enum):
    """Recession risk levels."""
    LOW = "low"  # < 20%
    MODERATE = "moderate"  # 20-50%
    HIGH = "high"  # 50-75%
    CRITICAL = "critical"  # > 75%


@dataclass
class RecessionIndicators:
    """Recession indicator values."""
    yield_curve_inversion: float  # 0-1, 1 = inverted
    unemployment_trend: float  # 0-1, 1 = increasing sharply
    gdp_growth_slowdown: float  # 0-1
    consumer_confidence_decline: float  # 0-1
    credit_spread_widening: float  # 0-1
    manufacturing_contraction: float  # 0-1
    composite_score: float  # 0-1


@dataclass
class RecessionProbability:
    """Recession probability forecast."""
    recession_probability: float  # 0-1
    risk_level: RecessionRisk
    time_horizon_months: int
    leading_indicators: List[str]  # Indicators suggesting recession
    warning_signals: List[str]  # Specific warning signals
    confidence: float
    calculation_method: str
    assumptions: List[str]


class RecessionDetector:
    """
    Detects recession probability using multiple economic indicators.
    """
    
    def __init__(self):
        """Initialize recession detector."""
        self.logger = logger
    
    def detect_recession_probability(
        self,
        yield_curve_spread: float,  # 10Y - 2Y yield spread
        unemployment_rate: float,
        unemployment_change_6m: float,  # Change in unemployment over 6 months
        gdp_growth_rate: float,
        gdp_trend: float,  # Trend: negative = slowing
        consumer_confidence_index: float,  # 0-100 scale
        confidence_trend: float,
        high_yield_spread: float,  # Credit spread (basis points)
        ism_manufacturing: float,  # 0-100 scale
        vix_index: float,  # Volatility index
    ) -> RecessionProbability:
        """
        Calculate recession probability from economic indicators.
        
        Args:
            yield_curve_spread: 10Y - 2Y spread (negative = inverted)
            unemployment_rate: Current unemployment rate (e.g., 0.04 = 4%)
            unemployment_change_6m: Change over 6 months
            gdp_growth_rate: Current GDP growth rate
            gdp_trend: Trend (-1 to 1, negative = slowing)
            consumer_confidence_index: 0-100 scale
            confidence_trend: Trend of consumer confidence
            high_yield_spread: High yield spread (basis points)
            ism_manufacturing: ISM manufacturing index (0-100)
            vix_index: VIX volatility index
            
        Returns:
            RecessionProbability forecast
        """
        indicators = self._calculate_indicator_scores(
            yield_curve_spread,
            unemployment_rate,
            unemployment_change_6m,
            gdp_growth_rate,
            gdp_trend,
            consumer_confidence_index,
            confidence_trend,
            high_yield_spread,
            ism_manufacturing,
            vix_index,
        )
        
        # Weight indicators to get recession probability
        recession_prob = self._weight_indicators(indicators)
        
        # Determine risk level
        risk_level = self._probability_to_risk_level(recession_prob)
        
        # Identify leading indicators showing stress
        leading_indicators = self._identify_leading_indicators(
            indicators, yield_curve_spread, unemployment_change_6m, gdp_trend
        )
        
        # Identify specific warning signals
        warning_signals = self._identify_warning_signals(
            indicators, recession_prob, gdp_growth_rate, ism_manufacturing
        )
        
        assumptions = [
            "Uses NBER recession dating as reference",
            "Incorporates leading economic indicators",
            "Historical correlation-based weighting",
            "Does not account for policy interventions",
            "Assumes normal market conditions",
        ]
        
        return RecessionProbability(
            recession_probability=recession_prob,
            risk_level=risk_level,
            time_horizon_months=12,  # 12-month forward
            leading_indicators=leading_indicators,
            warning_signals=warning_signals,
            confidence=0.75,
            calculation_method="Multi-indicator weighted scoring",
            assumptions=assumptions,
        )
    
    def _calculate_indicator_scores(
        self,
        yield_curve_spread: float,
        unemployment_rate: float,
        unemployment_change_6m: float,
        gdp_growth_rate: float,
        gdp_trend: float,
        consumer_confidence_index: float,
        confidence_trend: float,
        high_yield_spread: float,
        ism_manufacturing: float,
        vix_index: float,
    ) -> RecessionIndicators:
        """Calculate individual indicator scores (0-1)."""
        
        # Yield curve inversion (strong recession signal)
        # Inverted (negative) spread strongly predicts recession
        yield_inversion = max(0, min(1, -yield_curve_spread / 0.02))
        
        # Unemployment trend (increasing unemployment = recession signal)
        unemployment_score = max(0, min(1, unemployment_change_6m / 0.02))
        
        # GDP growth slowdown
        gdp_slowdown = max(0, min(1, -gdp_trend / 0.03))
        
        # Consumer confidence decline
        confidence_decline = max(0, min(1, -confidence_trend / 10.0))
        
        # Credit spread widening (recession signal)
        # Higher spread = more risk premium = more recession risk
        # Normal high yield spread: 350-400 bps, elevated: 500+
        credit_score = max(0, min(1, (high_yield_spread - 350) / 300))
        
        # Manufacturing contraction (ISM < 50 = contraction)
        manufacturing_score = max(0, min(1, (50 - ism_manufacturing) / 20))
        
        # Composite score (simple average for now)
        composite = (
            yield_inversion * 0.25 +
            unemployment_score * 0.20 +
            gdp_slowdown * 0.20 +
            confidence_decline * 0.15 +
            credit_score * 0.10 +
            manufacturing_score * 0.10
        )
        
        return RecessionIndicators(
            yield_curve_inversion=yield_inversion,
            unemployment_trend=unemployment_score,
            gdp_growth_slowdown=gdp_slowdown,
            consumer_confidence_decline=confidence_decline,
            credit_spread_widening=credit_score,
            manufacturing_contraction=manufacturing_score,
            composite_score=composite,
        )
    
    def _weight_indicators(self, indicators: RecessionIndicators) -> float:
        """Weight indicators into recession probability."""
        # Yield curve inversion is strongest signal
        base_prob = indicators.composite_score
        
        # Boost probability if multiple indicators align
        signals_present = sum([
            indicators.yield_curve_inversion > 0.5,
            indicators.unemployment_trend > 0.5,
            indicators.gdp_growth_slowdown > 0.5,
            indicators.consumer_confidence_decline > 0.5,
            indicators.credit_spread_widening > 0.5,
        ])
        
        if signals_present >= 3:
            base_prob = min(1.0, base_prob * 1.3)
        
        return base_prob
    
    def _probability_to_risk_level(self, probability: float) -> RecessionRisk:
        """Convert probability to risk level."""
        if probability < 0.20:
            return RecessionRisk.LOW
        elif probability < 0.50:
            return RecessionRisk.MODERATE
        elif probability < 0.75:
            return RecessionRisk.HIGH
        else:
            return RecessionRisk.CRITICAL
    
    def _identify_leading_indicators(
        self,
        indicators: RecessionIndicators,
        yield_spread: float,
        unemployment_change: float,
        gdp_trend: float,
    ) -> List[str]:
        """Identify leading indicators showing stress."""
        signals = []
        
        if indicators.yield_curve_inversion > 0.5:
            signals.append("Yield curve inverted (strong recession signal)")
        if indicators.unemployment_trend > 0.5:
            signals.append("Unemployment rising (labor market weakening)")
        if indicators.gdp_growth_slowdown > 0.5:
            signals.append("GDP growth slowing (economic deceleration)")
        if indicators.consumer_confidence_decline > 0.5:
            signals.append("Consumer confidence declining")
        if indicators.credit_spread_widening > 0.5:
            signals.append("Credit spreads widening (financial stress)")
        if indicators.manufacturing_contraction > 0.5:
            signals.append("Manufacturing contraction (sector weakness)")
        
        return signals
    
    def _identify_warning_signals(
        self,
        indicators: RecessionIndicators,
        recession_prob: float,
        gdp_growth: float,
        ism_manufacturing: float,
    ) -> List[str]:
        """Identify specific warning signals."""
        warnings = []
        
        if recession_prob > 0.60:
            warnings.append("High recession probability: consider defensive positioning")
        if gdp_growth < 0.01:
            warnings.append("GDP growth near zero: economic momentum weakening")
        if ism_manufacturing < 50:
            warnings.append("Manufacturing in contraction: factory activity declining")
        if indicators.credit_spread_widening > 0.7:
            warnings.append("Credit stress building: consider reducing leverage")
        
        return warnings
