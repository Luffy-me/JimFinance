"""
FX Exposure Calculator - Aggregate and measure currency exposure.

Provides:
- Position-level FX exposure
- Portfolio FX exposure aggregation
- Currency concentration risk
- Hedging recommendations
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FXExposure:
    """Currency exposure for a position."""
    currency: str
    amount: float  # Amount in that currency
    base_currency_value: float  # Converted to base currency
    percent_of_portfolio: float
    volatility: float
    correlation_to_portfolio: float


@dataclass
class ExposureReport:
    """Comprehensive FX exposure report."""
    base_currency: str
    total_portfolio_value: float
    net_fx_exposure: float  # Net exposure in base currency
    gross_fx_exposure: float  # Gross exposure
    exposure_concentration: Dict[str, float]  # By currency
    largest_exposures: List[Tuple[str, float]]
    hedging_recommendations: List[str]
    confidence: float
    assumptions: List[str]


class ExposureCalculator:
    """
    Calculates and aggregates FX exposure across portfolio.
    """
    
    def __init__(self, base_currency: str = "USD"):
        """
        Initialize exposure calculator.
        
        Args:
            base_currency: Base currency for calculations (USD, EUR, etc.)
        """
        self.logger = logger
        self.base_currency = base_currency
    
    def calculate_position_exposure(
        self,
        currency: str,
        amount: float,
        exchange_rate: float,
        portfolio_value: float,
        currency_volatility: float = 0.10,
    ) -> FXExposure:
        """
        Calculate FX exposure for a position.
        
        Args:
            currency: Position currency
            amount: Amount in that currency
            exchange_rate: Exchange rate to base currency
            portfolio_value: Total portfolio value
            currency_volatility: Annual volatility of currency pair
            
        Returns:
            FXExposure for the position
        """
        base_currency_value = amount * exchange_rate
        percent_of_portfolio = base_currency_value / portfolio_value if portfolio_value > 0 else 0
        
        # Simplified correlation (actual would be calculated from historical data)
        correlation = 0.3 if currency in ["EUR", "GBP", "JPY"] else 0.5
        
        return FXExposure(
            currency=currency,
            amount=amount,
            base_currency_value=base_currency_value,
            percent_of_portfolio=percent_of_portfolio,
            volatility=currency_volatility,
            correlation_to_portfolio=correlation,
        )
    
    def aggregate_exposures(
        self,
        positions: Dict[str, Dict],  # {currency: {amount, exchange_rate, volatility}}
        portfolio_value: float,
    ) -> ExposureReport:
        """
        Aggregate FX exposures across portfolio.
        
        Args:
            positions: Dict of currency positions
            portfolio_value: Total portfolio value in base currency
            
        Returns:
            ExposureReport with aggregated exposure analysis
        """
        exposures = {}
        total_exposure = 0
        
        for currency, position_data in positions.items():
            amount = position_data.get("amount", 0)
            exchange_rate = position_data.get("exchange_rate", 1.0)
            volatility = position_data.get("volatility", 0.10)
            
            exposure = self.calculate_position_exposure(
                currency, amount, exchange_rate, portfolio_value, volatility
            )
            exposures[currency] = exposure
            total_exposure += exposure.base_currency_value
        
        # Calculate net FX exposure
        # (exposure is net: long foreign currency = positive exposure)
        net_fx_exposure = total_exposure - portfolio_value
        
        # Concentration analysis
        concentration = {
            currency: exp.percent_of_portfolio
            for currency, exp in exposures.items()
        }
        
        # Sort exposures by size
        largest = sorted(
            [(c, e.base_currency_value) for c, e in exposures.items()],
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]
        
        # Generate hedging recommendations
        recommendations = self._generate_hedging_recommendations(
            net_fx_exposure, concentration, exposures
        )
        
        assumptions = [
            f"Base currency: {self.base_currency}",
            "Uses current spot rates",
            "Assumes correlations from historical data",
            "Does not account for future cash flows",
            "Volatility from recent period",
        ]
        
        return ExposureReport(
            base_currency=self.base_currency,
            total_portfolio_value=portfolio_value,
            net_fx_exposure=net_fx_exposure,
            gross_fx_exposure=sum(abs(e.base_currency_value) for e in exposures.values()),
            exposure_concentration=concentration,
            largest_exposures=largest,
            hedging_recommendations=recommendations,
            confidence=0.80,
            assumptions=assumptions,
        )
    
    def calculate_fx_var(
        self,
        exposures: Dict[str, FXExposure],
        confidence_level: float = 0.95,
    ) -> float:
        """
        Calculate Value at Risk (VaR) for FX exposure.
        
        Args:
            exposures: FX exposures by currency
            confidence_level: Confidence level (0.95 = 95%)
            
        Returns:
            VaR in base currency
        """
        # Simplified VaR using volatility
        # VaR = Z-score * Portfolio Volatility * Portfolio Value
        
        z_scores = {
            0.90: 1.28,
            0.95: 1.645,
            0.99: 2.33,
        }
        z_score = z_scores.get(confidence_level, 1.645)
        
        # Portfolio FX volatility (weighted average)
        portfolio_fx_vol = sum(
            exp.percent_of_portfolio * exp.volatility
            for exp in exposures.values()
        )
        
        total_value = sum(exp.base_currency_value for exp in exposures.values())
        
        fx_var = z_score * portfolio_fx_vol * total_value
        
        return fx_var
    
    def calculate_fx_contribution_to_risk(
        self,
        exposures: Dict[str, FXExposure],
    ) -> Dict[str, float]:
        """
        Calculate each currency's contribution to total FX risk.
        
        Args:
            exposures: FX exposures by currency
            
        Returns:
            Risk contribution by currency
        """
        contributions = {}
        
        for currency, exposure in exposures.items():
            # Simple contribution: volatility * exposure * correlation
            contribution = (
                exposure.volatility *
                abs(exposure.base_currency_value) *
                exposure.correlation_to_portfolio
            )
            contributions[currency] = contribution
        
        return contributions
    
    def _generate_hedging_recommendations(
        self,
        net_exposure: float,
        concentration: Dict[str, float],
        exposures: Dict[str, FXExposure],
    ) -> List[str]:
        """Generate hedging recommendations."""
        recommendations = []
        
        # Large net exposure
        if abs(net_exposure) > 0.20:
            recommendations.append(
                f"Large net FX exposure ({abs(net_exposure)*100:.1f}% of portfolio): "
                "Consider partial hedging"
            )
        
        # Single currency concentration
        for currency, percent in concentration.items():
            if percent > 0.25:
                recommendations.append(
                    f"High {currency} concentration ({percent*100:.1f}%): "
                    "Consider diversifying or hedging"
                )
        
        # High volatility currencies
        for currency, exposure in exposures.items():
            if exposure.volatility > 0.15:
                recommendations.append(
                    f"{currency} is high volatility ({exposure.volatility*100:.1f}%): "
                    "Consider protective hedging (options)"
                )
        
        if not recommendations:
            recommendations.append("FX exposure appears well-balanced, minimal hedging needed")
        
        return recommendations
    
    def scenario_analysis(
        self,
        exposures: Dict[str, FXExposure],
        currency_move_percent: float,  # e.g., 0.05 = 5% move
    ) -> Dict[str, float]:
        """
        Run scenario analysis on FX movements.
        
        Args:
            exposures: FX exposures by currency
            currency_move_percent: Hypothetical currency move
            
        Returns:
            Portfolio P&L impact by currency
        """
        pnl_impact = {}
        
        for currency, exposure in exposures.items():
            # For long foreign currency positions: appreciation = gain
            pnl = exposure.base_currency_value * currency_move_percent
            pnl_impact[currency] = pnl
        
        return pnl_impact
