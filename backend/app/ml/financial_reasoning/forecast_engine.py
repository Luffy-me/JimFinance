"""
Inflation-Adjusted Forecasting Engine - Real value projections with CPI modeling.

Provides:
- Real vs. nominal value calculations
- Future purchasing power projections
- Inflation-adjusted runway analysis
- Historical and forward CPI modeling
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class InflationScenario(str, Enum):
    """Inflation scenarios for forecasting."""
    LOW = "low"  # 1% annual
    MODERATE = "moderate"  # 3% annual (historical average)
    HIGH = "high"  # 5% annual
    HYPERINFLATION = "hyperinflation"  # 10%+ annual


@dataclass
class InflationAssumption:
    """Inflation assumption configuration."""
    scenario: InflationScenario
    annual_rate: float  # 0.01 = 1%
    start_date: datetime
    country: str = "US"
    
    def to_dict(self):
        return asdict(self)


@dataclass
class PurchasingPowerMetric:
    """Purchasing power metric with confidence."""
    timestamp: datetime
    real_value: float  # Inflation-adjusted
    nominal_value: float  # Raw value
    purchasing_power_loss: float  # Percentage
    confidence: float
    calculation_method: str
    assumptions: List[str]


class InflationIndexProvider:
    """Historical and forward-looking inflation indices."""
    
    # Historical CPI annual rates (simplified, country-specific)
    HISTORICAL_US_CPI = {
        2023: 0.0328,  # 3.28%
        2022: 0.0801,  # 8.01%
        2021: 0.0470,  # 4.70%
        2020: 0.0124,  # 1.24%
        2019: 0.0181,  # 1.81%
    }
    
    # Historical RUB inflation (high inflation period)
    HISTORICAL_RUB_CPI = {
        2023: 0.072,   # 7.2%
        2022: 0.130,   # 13.0%
        2021: 0.060,   # 6.0%
        2020: 0.033,   # 3.3%
    }
    
    # Central bank forward guidance (2024-2026)
    FORWARD_GUIDANCE = {
        "US": {2024: 0.025, 2025: 0.025, 2026: 0.025},
        "RU": {2024: 0.035, 2025: 0.025, 2026: 0.025},
        "EU": {2024: 0.020, 2025: 0.020, 2026: 0.020},
    }
    
    @staticmethod
    def get_historical_rate(year: int, country: str = "US") -> Optional[float]:
        """Get historical inflation rate for year."""
        if country == "US":
            return InflationIndexProvider.HISTORICAL_US_CPI.get(year)
        elif country in ["RU", "RUS"]:
            return InflationIndexProvider.HISTORICAL_RUB_CPI.get(year)
        return None
    
    @staticmethod
    def get_forward_rate(year: int, country: str = "US") -> Optional[float]:
        """Get forward-looking inflation guidance."""
        guidance = InflationIndexProvider.FORWARD_GUIDANCE.get(country)
        return guidance.get(year) if guidance else None


class ForecastingEngine:
    """
    Inflation-adjusted financial forecasting.
    Projects real purchasing power and nominal values over time.
    """
    
    def __init__(self, country: str = "US"):
        """
        Initialize forecasting engine.
        
        Args:
            country: Country code for inflation data (US, RU, EU)
        """
        self.logger = logger
        self.country = country
        self.index_provider = InflationIndexProvider()
    
    def nominal_to_real(
        self,
        nominal_amount: float,
        start_date: datetime,
        end_date: datetime,
        inflation_scenario: InflationScenario = InflationScenario.MODERATE,
    ) -> PurchasingPowerMetric:
        """
        Convert nominal amount to real (inflation-adjusted) value.
        
        Args:
            nominal_amount: Original nominal amount
            start_date: Date of original amount
            end_date: Date to project to
            inflation_scenario: Inflation assumption scenario
            
        Returns:
            PurchasingPowerMetric with real value
        """
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        years = months / 12.0
        
        # Get cumulative inflation rate
        cumulative_rate = self._calculate_cumulative_inflation(
            start_date, end_date, inflation_scenario
        )
        
        # Calculate real value: nominal / (1 + inflation_rate)
        real_value = nominal_amount / (1 + cumulative_rate)
        purchasing_power_loss = (nominal_amount - real_value) / nominal_amount
        
        assumptions = [
            f"Inflation scenario: {inflation_scenario.value}",
            f"Country: {self.country}",
            f"Period: {years:.1f} years",
            "Assumes annual compounding",
        ]
        
        return PurchasingPowerMetric(
            timestamp=end_date,
            real_value=real_value,
            nominal_value=nominal_amount,
            purchasing_power_loss=purchasing_power_loss,
            confidence=0.85 if years <= 5 else 0.70,  # Lower confidence for long horizons
            calculation_method=f"nominal / (1 + cumulative_inflation)",
            assumptions=assumptions,
        )
    
    def real_to_nominal(
        self,
        real_amount: float,
        start_date: datetime,
        end_date: datetime,
        inflation_scenario: InflationScenario = InflationScenario.MODERATE,
    ) -> PurchasingPowerMetric:
        """
        Convert real amount to nominal (future) value.
        
        Args:
            real_amount: Original real (today's) amount
            start_date: Today's date
            end_date: Date to project to
            inflation_scenario: Inflation assumption scenario
            
        Returns:
            PurchasingPowerMetric with nominal value needed
        """
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        years = months / 12.0
        
        # Get cumulative inflation rate
        cumulative_rate = self._calculate_cumulative_inflation(
            start_date, end_date, inflation_scenario
        )
        
        # Calculate nominal value: real * (1 + inflation_rate)
        nominal_value = real_amount * (1 + cumulative_rate)
        purchasing_power_loss = (nominal_value - real_amount) / real_amount
        
        assumptions = [
            f"Inflation scenario: {inflation_scenario.value}",
            f"Country: {self.country}",
            f"Period: {years:.1f} years",
            "Assumes annual compounding",
        ]
        
        return PurchasingPowerMetric(
            timestamp=end_date,
            real_value=real_amount,
            nominal_value=nominal_value,
            purchasing_power_loss=purchasing_power_loss,
            confidence=0.85 if years <= 5 else 0.70,
            calculation_method="real * (1 + cumulative_inflation)",
            assumptions=assumptions,
        )
    
    def inflation_adjusted_runway(
        self,
        current_balance: float,
        monthly_expenses: float,
        inflation_scenario: InflationScenario = InflationScenario.MODERATE,
        months: int = 60,
    ) -> Dict:
        """
        Calculate runway with inflation adjustment.
        
        Projects how long money lasts accounting for both:
        1. Declining balance (spending)
        2. Declining purchasing power (inflation)
        
        Args:
            current_balance: Starting balance
            monthly_expenses: Current monthly expenses (nominal)
            inflation_scenario: Inflation assumption
            months: Months to project
            
        Returns:
            Runway analysis with inflation impact
        """
        if monthly_expenses <= 0 or current_balance <= 0:
            return {"error": "Invalid inputs"}
        
        annual_inflation = self._get_inflation_rate(inflation_scenario)
        monthly_inflation_rate = (1 + annual_inflation) ** (1/12) - 1
        
        # Project balance month by month
        projections = []
        balance = current_balance
        real_balance = current_balance
        
        for month in range(months):
            # Apply spending
            balance -= monthly_expenses
            
            # Apply inflation to remaining balance (purchasing power loss)
            real_balance = balance / ((1 + monthly_inflation_rate) ** (month + 1))
            
            projections.append({
                "month": month,
                "nominal_balance": max(0, balance),
                "real_balance": max(0, real_balance),
                "real_spending_power": real_balance / current_balance if current_balance > 0 else 0,
            })
            
            if balance <= 0:
                break
        
        # Find runway (when balance exhausted)
        nominal_runway = next(
            (p["month"] for p in projections if p["nominal_balance"] <= 0),
            months
        )
        
        # Real runway (accounting for inflation)
        real_runway = next(
            (p["month"] for p in projections if p["real_balance"] <= 0),
            months
        )
        
        return {
            "nominal_runway_months": nominal_runway,
            "real_runway_months": real_runway,
            "runway_reduction_months": nominal_runway - real_runway,
            "inflation_impact_percent": (
                (nominal_runway - real_runway) / nominal_runway * 100
                if nominal_runway > 0 else 0
            ),
            "scenario": inflation_scenario.value,
            "projections": projections,
            "confidence": 0.80,
        }
    
    def purchase_affordability_inflation_adjusted(
        self,
        purchase_price_today: float,
        months_until_purchase: int = 12,
        monthly_income: float = 0,
        monthly_expenses: float = 0,
        current_balance: float = 0,
        inflation_scenario: InflationScenario = InflationScenario.MODERATE,
    ) -> Dict:
        """
        Analyze purchase affordability accounting for inflation.
        
        Shows:
        - What the item will cost in future (nominal)
        - How much to save (in today's dollars)
        - Real vs. nominal affordability
        
        Args:
            purchase_price_today: Price today in local currency
            months_until_purchase: How many months away
            monthly_income: Monthly income
            monthly_expenses: Monthly expenses
            current_balance: Starting balance
            inflation_scenario: Inflation assumption
            
        Returns:
            Affordability analysis with inflation impact
        """
        today = datetime.utcnow()
        purchase_date = today + timedelta(days=30 * months_until_purchase)
        
        # What will the item cost (nominal)?
        future_price = self.real_to_nominal(
            purchase_price_today,
            today,
            purchase_date,
            inflation_scenario,
        )
        
        # How much to save (in today's dollars)
        monthly_savings = monthly_income - monthly_expenses
        total_savings_nominal = current_balance + (monthly_savings * months_until_purchase)
        
        # What's the real purchasing power of savings?
        total_savings_real = self.nominal_to_real(
            total_savings_nominal,
            today,
            purchase_date,
            inflation_scenario,
        )
        
        # Affordability assessment
        can_afford_nominal = total_savings_nominal >= future_price.nominal_value
        can_afford_real = total_savings_real.real_value >= purchase_price_today
        
        return {
            "purchase_analysis": {
                "price_today": purchase_price_today,
                "price_at_purchase_date": {
                    "nominal": future_price.nominal_value,
                    "real": future_price.real_value,
                    "inflation_impact": future_price.purchasing_power_loss * 100,
                },
                "months_until_purchase": months_until_purchase,
            },
            "savings_analysis": {
                "current_balance": current_balance,
                "monthly_savings": monthly_savings,
                "total_savings_by_purchase_date": {
                    "nominal": total_savings_nominal,
                    "real": total_savings_real.real_value,
                },
            },
            "affordability": {
                "can_afford_nominal": can_afford_nominal,
                "can_afford_real": can_afford_real,
                "shortfall_nominal": max(0, future_price.nominal_value - total_savings_nominal),
                "inflation_adjusted_shortfall": (
                    max(0, purchase_price_today - total_savings_real.real_value)
                ),
            },
            "scenario": inflation_scenario.value,
            "confidence": future_price.confidence,
        }
    
    def _calculate_cumulative_inflation(
        self,
        start_date: datetime,
        end_date: datetime,
        scenario: InflationScenario,
    ) -> float:
        """Calculate cumulative inflation rate between dates."""
        cumulative = 0.0
        current_date = start_date
        
        while current_date.year < end_date.year or (
            current_date.year == end_date.year and current_date.month < end_date.month
        ):
            year = current_date.year
            
            # Try historical rate first
            rate = self.index_provider.get_historical_rate(year, self.country)
            
            # Fall back to forward guidance
            if rate is None:
                rate = self.index_provider.get_forward_rate(year, self.country)
            
            # Fall back to scenario
            if rate is None:
                rate = self._get_inflation_rate(scenario)
            
            cumulative = (1 + cumulative) * (1 + rate) - 1
            current_date = current_date.replace(year=current_date.year + 1)
        
        # Handle partial year
        months_in_last_year = (end_date.year - current_date.year + 1) * 12 + (
            end_date.month - current_date.month
        )
        if months_in_last_year > 0:
            year_rate = self._get_inflation_rate(scenario)
            monthly_rate = (1 + year_rate) ** (1/12) - 1
            cumulative = (1 + cumulative) * ((1 + monthly_rate) ** months_in_last_year) - 1
        
        return max(0, cumulative)  # Ensure non-negative
    
    @staticmethod
    def _get_inflation_rate(scenario: InflationScenario) -> float:
        """Get annual inflation rate for scenario."""
        rates = {
            InflationScenario.LOW: 0.01,
            InflationScenario.MODERATE: 0.03,
            InflationScenario.HIGH: 0.05,
            InflationScenario.HYPERINFLATION: 0.10,
        }
        return rates.get(scenario, 0.03)
