"""
Wealth Forecasting Engine - Multi-dimensional wealth projections.
Models wealth accumulation incorporating income, expenses, investments, and debt.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class WealthProjection:
    """Annual wealth projection data point."""
    year: int
    net_worth: float
    income: float
    expenses: float
    savings: float
    investment_returns: float
    debt_balance: float


@dataclass
class WealthForecastResult:
    """Long-term wealth forecast (30-year horizon)."""
    projection_years: int
    current_net_worth: float
    projected_net_worth: float
    cagr: float  # Compound annual growth rate
    confidence_interval_low: float
    confidence_interval_high: float
    confidence: float
    
    # Year-by-year
    annual_projections: List[WealthProjection]
    
    # Key milestones
    milestone_dates: Dict[str, datetime]  # e.g., {'financial_independence': datetime}
    
    assumptions: List[str]
    recommendations: List[str]
    timestamp: datetime
    
    def to_dict(self):
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        result["milestone_dates"] = {
            k: v.isoformat() for k, v in self.milestone_dates.items()
        }
        result["annual_projections"] = [
            asdict(p) for p in self.annual_projections
        ]
        return result


class WealthForecastingEngine:
    """
    Advanced wealth projections incorporating all financial dimensions.
    Projects wealth over 30+ years with confidence intervals.
    """
    
    def __init__(self):
        """Initialize wealth forecasting engine."""
        self.logger = logger
    
    def forecast_wealth(
        self,
        current_net_worth: float,
        monthly_income: float,
        monthly_expenses: float,
        annual_investment_return: float = 0.07,
        annual_inflation: float = 0.03,
        investment_growth_confidence: float = 0.8,
        projection_years: int = 30,
    ) -> WealthForecastResult:
        """
        Project wealth growth over specified period.
        
        Args:
            current_net_worth: Starting net worth
            monthly_income: Average monthly income
            monthly_expenses: Average monthly expenses
            annual_investment_return: Expected annual return on investments
            annual_inflation: Expected annual inflation
            investment_growth_confidence: Confidence in investment returns (0-1)
            projection_years: Years to project
            
        Returns:
            WealthForecastResult with projections
        """
        # Initialize arrays
        net_worths = []
        projections = []
        
        # Sensitivity analysis
        pessimistic_return = annual_investment_return * 0.6
        optimistic_return = annual_investment_return * 1.4
        
        current_nw = current_net_worth
        current_nw_pessimistic = current_net_worth
        current_nw_optimistic = current_net_worth
        
        annual_savings = (monthly_income - monthly_expenses) * 12
        
        for year in range(1, projection_years + 1):
            # Annual savings
            current_nw += annual_savings
            current_nw_pessimistic += annual_savings
            current_nw_optimistic += annual_savings
            
            # Investment returns (only on positive balance)
            if current_nw > 0:
                current_nw *= (1 + annual_investment_return)
                current_nw_pessimistic *= (1 + pessimistic_return)
                current_nw_optimistic *= (1 + optimistic_return)
            
            # Inflation adjustment (optional - for "real" projections)
            # Typically we project nominal values
            
            investment_return_amount = current_nw * annual_investment_return
            
            projection = WealthProjection(
                year=year,
                net_worth=current_nw,
                income=monthly_income * 12,
                expenses=monthly_expenses * 12,
                savings=annual_savings,
                investment_returns=investment_return_amount,
                debt_balance=0.0,  # Simplified, would need actual debt tracking
            )
            
            projections.append(projection)
            net_worths.append(current_nw)
        
        # Calculate CAGR
        if current_net_worth > 0:
            cagr = (current_nw / current_net_worth) ** (1 / projection_years) - 1
        else:
            cagr = 0.0
        
        # Confidence intervals (95%)
        std_dev = (current_nw_optimistic - current_nw_pessimistic) / (2 * 1.96)
        ci_low = current_nw - 1.96 * std_dev
        ci_high = current_nw + 1.96 * std_dev
        
        # Identify milestones
        milestone_dates = {}
        if current_net_worth > 0:
            # Financial independence: typically 25x annual expenses
            fi_target = (monthly_expenses * 12) * 25
            for proj in projections:
                if proj.net_worth >= fi_target:
                    milestone_dates["financial_independence"] = datetime.utcnow()
                    break
        
        assumptions = [
            f"Constant annual income: ${monthly_income:,.0f}/month",
            f"Constant annual expenses: ${monthly_expenses:,.0f}/month",
            f"Investment return: {annual_investment_return*100:.1f}% annually",
            f"Inflation: {annual_inflation*100:.1f}% annually",
            "No major life events or emergencies",
            "Stable employment",
        ]
        
        recommendations = self._generate_recommendations(
            current_nw,
            annual_savings,
            annual_investment_return,
            cagr,
        )
        
        confidence = 0.7  # Medium confidence for long-term forecasts
        if projection_years <= 5:
            confidence = 0.85
        elif projection_years >= 20:
            confidence = 0.5
        
        result = WealthForecastResult(
            projection_years=projection_years,
            current_net_worth=current_net_worth,
            projected_net_worth=current_nw,
            cagr=cagr,
            confidence_interval_low=ci_low,
            confidence_interval_high=ci_high,
            confidence=confidence,
            annual_projections=projections,
            milestone_dates=milestone_dates,
            assumptions=assumptions,
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
        )
        
        return result
    
    def _generate_recommendations(
        self,
        projected_nw: float,
        annual_savings: float,
        annual_return: float,
        cagr: float,
    ) -> List[str]:
        """Generate recommendations based on forecast."""
        recommendations = []
        
        if annual_savings <= 0:
            recommendations.append(
                "Critical: Expenses exceed income. Adjust spending or increase income immediately."
            )
        elif annual_savings < 5000:
            recommendations.append("Increase savings rate to accelerate wealth growth.")
        else:
            recommendations.append(f"Strong savings rate: {annual_savings/12:,.0f}/month")
        
        if annual_return < 0.05:
            recommendations.append(
                "Consider higher-yielding investments aligned with your risk tolerance."
            )
        elif annual_return > 0.10:
            recommendations.append(
                "Verify investment return assumptions are realistic and diversified."
            )
        
        if cagr > 0.05:
            recommendations.append(
                "Strong wealth growth trajectory. Ensure proper diversification."
            )
        
        return recommendations
