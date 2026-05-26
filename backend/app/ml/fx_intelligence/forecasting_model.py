"""
Currency Forecasting Model - Predict currency movements.

Provides:
- Currency pair forecasts
- PPP-based fair value models
- Technical momentum indicators
- Risk assessment
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class ForecastDirection(str, Enum):
    """Currency forecast direction."""
    STRONG_APPRECIATE = "strong_appreciate"
    APPRECIATE = "appreciate"
    NEUTRAL = "neutral"
    DEPRECIATE = "depreciate"
    STRONG_DEPRECIATE = "strong_depreciate"


@dataclass
class CurrencyForecast:
    """Currency pair forecast."""
    currency_pair: str
    current_rate: float
    forecast_rate: float
    forecast_direction: ForecastDirection
    confidence: float
    forecast_horizon_months: int
    upside_scenario: float  # Bull case
    downside_scenario: float  # Bear case
    drivers: List[str]
    risks: List[str]
    assumptions: List[str]


class ForecastingModel:
    """
    Forecasts currency movements using fundamental and technical analysis.
    """
    
    def __init__(self):
        """Initialize forecasting model."""
        self.logger = logger
    
    def forecast_currency_pair(
        self,
        currency_pair: str,
        current_rate: float,
        interest_rate_diff: float,  # Rate in quote currency - base currency
        inflation_diff: float,
        gdp_growth_diff: float,
        trade_balance: float,
        technical_momentum: float,  # -1 to 1
        months_forward: int = 12,
    ) -> CurrencyForecast:
        """
        Forecast currency pair movement.
        
        Args:
            currency_pair: Currency pair (e.g., "USD/EUR")
            current_rate: Current spot rate
            interest_rate_diff: Interest rate differential (%)
            inflation_diff: Inflation rate differential (%)
            gdp_growth_diff: GDP growth differential (%)
            trade_balance: Trade balance position (-1 to 1)
            technical_momentum: Technical momentum (-1 to 1)
            months_forward: Forecast horizon
            
        Returns:
            CurrencyForecast with forward rate prediction
        """
        # Calculate fundamental factors
        fundamental_score = self._calculate_fundamental_score(
            interest_rate_diff, inflation_diff, gdp_growth_diff, trade_balance
        )
        
        # Combine with technical
        total_score = fundamental_score * 0.70 + technical_momentum * 0.30
        
        # Determine direction
        direction = self._score_to_direction(total_score)
        
        # Calculate forecast rate
        forecast_rate = self._calculate_forecast_rate(
            current_rate, total_score, months_forward
        )
        
        # Calculate scenarios
        upside = self._calculate_upside_scenario(current_rate, total_score, months_forward)
        downside = self._calculate_downside_scenario(current_rate, total_score, months_forward)
        
        # Identify drivers
        drivers = self._identify_drivers(
            fundamental_score, technical_momentum, interest_rate_diff, inflation_diff
        )
        
        # Identify risks
        risks = self._identify_risks(currency_pair)
        
        assumptions = [
            "Uses interest rate parity framework",
            "Incorporates PPP for long-term trends",
            "Technical momentum from recent price action",
            "Does not account for geopolitical shocks",
            "Assumes stable policy environment",
        ]
        
        return CurrencyForecast(
            currency_pair=currency_pair,
            current_rate=current_rate,
            forecast_rate=forecast_rate,
            forecast_direction=direction,
            confidence=0.65,  # FX forecasting is uncertain
            forecast_horizon_months=months_forward,
            upside_scenario=upside,
            downside_scenario=downside,
            drivers=drivers,
            risks=risks,
            assumptions=assumptions,
        )
    
    def _calculate_fundamental_score(
        self,
        interest_rate_diff: float,
        inflation_diff: float,
        gdp_growth_diff: float,
        trade_balance: float,
    ) -> float:
        """Calculate fundamental score (-1 to 1)."""
        # Normalize factors to 0-1 scale
        rate_factor = np.tanh(interest_rate_diff / 5.0)  # Saturate at ±5%
        inflation_factor = np.tanh(inflation_diff / 5.0)
        growth_factor = np.tanh(gdp_growth_diff / 5.0)
        
        # Weights
        score = (
            rate_factor * 0.40 +  # Interest rates most important
            inflation_factor * 0.30 +  # PPP
            growth_factor * 0.20 +
            trade_balance * 0.10
        )
        
        return np.clip(score, -1, 1)
    
    def _score_to_direction(self, score: float) -> ForecastDirection:
        """Convert score to direction."""
        if score > 0.50:
            return ForecastDirection.STRONG_APPRECIATE
        elif score > 0.20:
            return ForecastDirection.APPRECIATE
        elif score > -0.20:
            return ForecastDirection.NEUTRAL
        elif score > -0.50:
            return ForecastDirection.DEPRECIATE
        else:
            return ForecastDirection.STRONG_DEPRECIATE
    
    def _calculate_forecast_rate(
        self,
        current_rate: float,
        score: float,
        months: int,
    ) -> float:
        """Calculate forecast rate."""
        # Score translates to annual expected return
        annual_move = score * 0.10  # Max 10% annual move
        period_move = annual_move * (months / 12.0)
        
        forecast_rate = current_rate * (1 + period_move)
        
        return forecast_rate
    
    def _calculate_upside_scenario(
        self,
        current_rate: float,
        score: float,
        months: int,
    ) -> float:
        """Calculate bull case scenario."""
        # Bull case: favorable scenario plays out
        bull_annual_move = score * 0.15  # Max 15% annual move
        bull_move = bull_annual_move * (months / 12.0)
        
        upside = current_rate * (1 + bull_move)
        
        return upside
    
    def _calculate_downside_scenario(
        self,
        current_rate: float,
        score: float,
        months: int,
    ) -> float:
        """Calculate bear case scenario."""
        # Bear case: opposite of bull case
        bear_annual_move = -score * 0.15  # Max 15% annual move
        bear_move = bear_annual_move * (months / 12.0)
        
        downside = current_rate * (1 + bear_move)
        
        return downside
    
    def _identify_drivers(
        self,
        fundamental_score: float,
        technical_score: float,
        rate_diff: float,
        inflation_diff: float,
    ) -> List[str]:
        """Identify main drivers of forecast."""
        drivers = []
        
        if fundamental_score > 0.3:
            if rate_diff > 1.0:
                drivers.append("Interest rate differential favors appreciation")
            if inflation_diff < -1.0:
                drivers.append("Lower inflation supports currency strength (PPP)")
        elif fundamental_score < -0.3:
            if rate_diff < -1.0:
                drivers.append("Interest rate differential favors depreciation")
            if inflation_diff > 1.0:
                drivers.append("Higher inflation pressures currency (PPP)")
        
        if technical_score > 0.3:
            drivers.append("Positive technical momentum")
        elif technical_score < -0.3:
            drivers.append("Negative technical momentum")
        
        if not drivers:
            drivers.append("Mixed signals, forecast neutral")
        
        return drivers
    
    def _identify_risks(self, currency_pair: str) -> List[str]:
        """Identify risks to forecast."""
        risks = [
            "Geopolitical events can cause sudden moves",
            "Central bank policy changes",
            "Risk sentiment shifts",
            "Economic data surprises",
        ]
        
        # Currency-specific risks
        if "RUB" in currency_pair:
            risks.append("Sanctions risk on RUB")
        if "CNY" in currency_pair:
            risks.append("Chinese capital controls")
        if "JPY" in currency_pair:
            risks.append("BoJ policy changes impact carry trades")
        
        return risks
    
    def forward_curve(
        self,
        currency_pair: str,
        current_rate: float,
        interest_rate_diff: float,
        months_out: List[int] = None,
    ) -> Dict[int, float]:
        """
        Calculate forward exchange rate curve.
        
        Args:
            currency_pair: Currency pair
            current_rate: Current spot rate
            interest_rate_diff: Interest rate differential
            months_out: List of months to forecast
            
        Returns:
            Dict mapping months to forward rates
        """
        if months_out is None:
            months_out = [1, 3, 6, 12, 24]
        
        forward_curve = {}
        
        for months in months_out:
            # Interest rate parity forward
            time_factor = months / 12.0
            forward_rate = current_rate * (1 + interest_rate_diff / 100 * time_factor)
            forward_curve[months] = forward_rate
        
        return forward_curve
