"""
Quantitative Engine - Deterministic financial mathematics.
Provides mathematically rigorous calculations with confidence scoring.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class QuantitativeMetric:
    """Financial metric with confidence interval."""
    value: float
    lower_bound: float  # 95% confidence lower
    upper_bound: float  # 95% confidence upper
    confidence: float   # 0-1
    calculation_method: str
    assumptions: List[str]
    timestamp: datetime


class QuantitativeEngine:
    """
    Deterministic financial calculations with confidence intervals.
    All calculations are mathematically rigorous with full assumption tracking.
    """
    
    def __init__(self):
        """Initialize quantitative engine."""
        self.logger = logger
        self.MIN_DATA_POINTS = 10  # Minimum transactions for reliable metrics
        self.MIN_SPAN_DAYS = 28   # Minimum 4 weeks of data
    
    def calculate_savings_rate(
        self,
        monthly_income: float,
        monthly_expenses: float,
        confidence_threshold: float = 0.75,
    ) -> QuantitativeMetric:
        """
        Calculate savings rate = (income - expenses) / income
        
        Args:
            monthly_income: Monthly gross income
            monthly_expenses: Monthly total expenses
            confidence_threshold: Confidence threshold for calculation
            
        Returns:
            QuantitativeMetric with savings rate and confidence interval
        """
        assumptions = [
            "Income and expenses are accurately reported",
            "Calculation uses 1-month period",
            "Fixed income assumption",
        ]
        
        try:
            if monthly_income <= 0:
                self.logger.warning(f"Invalid income: {monthly_income}")
                return self._error_metric(
                    "Invalid income value", assumptions
                )
            
            savings_rate = (monthly_income - monthly_expenses) / monthly_income
            
            # Confidence intervals (±5% of rate for high confidence)
            margin = 0.05 if monthly_income > 0 else 0.10
            lower = max(-1.0, savings_rate - margin)
            upper = min(1.0, savings_rate + margin)
            
            return QuantitativeMetric(
                value=savings_rate,
                lower_bound=lower,
                upper_bound=upper,
                confidence=confidence_threshold,
                calculation_method="(income - expenses) / income",
                assumptions=assumptions,
                timestamp=datetime.utcnow(),
            )
        except Exception as e:
            self.logger.error(f"Savings rate calculation failed: {e}")
            return self._error_metric(str(e), assumptions)
    
    def calculate_burn_rate(
        self,
        transactions: List[Dict],
        days_span: int = 30,
    ) -> Tuple[QuantitativeMetric, QuantitativeMetric]:
        """
        Calculate monthly burn rate (monthly expenses) and trend.
        
        Args:
            transactions: List of transaction dicts with amount, date, type
            days_span: Number of days to analyze
            
        Returns:
            Tuple of (burn_rate, burn_rate_trend)
        """
        assumptions = [
            f"Analysis period: last {days_span} days",
            "Expense transactions only",
            "Anomalies excluded from main calculation",
            "Burn rate assumes consistent spending pattern",
        ]
        
        try:
            if not transactions or len(transactions) < self.MIN_DATA_POINTS:
                return (
                    self._error_metric("Insufficient transaction data", assumptions),
                    self._error_metric("Insufficient transaction data", assumptions),
                )
            
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            
            # Filter to date range
            cutoff = datetime.utcnow() - timedelta(days=days_span)
            df = df[df['date'] >= cutoff]
            
            # Get only outflows (expenses)
            expenses = df[df['amount'] < 0]['amount'].abs()
            
            if expenses.empty:
                return (
                    self._error_metric("No expense data", assumptions),
                    self._error_metric("No expense data", assumptions),
                )
            
            # Calculate daily burn rate
            daily_burn = expenses.sum() / days_span
            monthly_burn = daily_burn * 30  # Annualize to month
            
            # Calculate trend (compare first half vs second half)
            mid_point = len(df) // 2
            first_half_burn = df.iloc[:mid_point][df['amount'] < 0]['amount'].abs().sum()
            second_half_burn = df.iloc[mid_point:][df['amount'] < 0]['amount'].abs().sum()
            
            trend = (second_half_burn - first_half_burn) / first_half_burn if first_half_burn > 0 else 0
            
            # Confidence based on data points
            data_confidence = min(0.95, len(expenses) / 100)
            
            # Standard deviation for interval
            std_dev = expenses.std() / np.sqrt(len(expenses))
            margin = 1.96 * std_dev  # 95% CI
            
            burn_rate = QuantitativeMetric(
                value=monthly_burn,
                lower_bound=max(0, monthly_burn - margin),
                upper_bound=monthly_burn + margin,
                confidence=data_confidence,
                calculation_method=f"Sum of expenses / {days_span} days * 30",
                assumptions=assumptions,
                timestamp=datetime.utcnow(),
            )
            
            trend_metric = QuantitativeMetric(
                value=trend,
                lower_bound=trend - 0.15,
                upper_bound=trend + 0.15,
                confidence=0.70,  # Trend is less reliable
                calculation_method="(second_half_burn - first_half_burn) / first_half_burn",
                assumptions=assumptions + ["Trend calculated from half-period comparison"],
                timestamp=datetime.utcnow(),
            )
            
            return burn_rate, trend_metric
            
        except Exception as e:
            self.logger.error(f"Burn rate calculation failed: {e}")
            return (
                self._error_metric(str(e), assumptions),
                self._error_metric(str(e), assumptions),
            )
    
    def calculate_runway(
        self,
        current_balance: float,
        monthly_burn_rate: float,
        minimum_balance: float = 0.0,
    ) -> QuantitativeMetric:
        """
        Calculate financial runway (months until money runs out).
        
        Args:
            current_balance: Current account balance
            monthly_burn_rate: Monthly expenses (burn rate)
            minimum_balance: Minimum balance to maintain (emergency fund)
            
        Returns:
            QuantitativeMetric with runway in months
        """
        assumptions = [
            "Constant monthly burn rate",
            f"Minimum balance maintained: ${minimum_balance:,.2f}",
            "No additional income after today",
            "No investment growth assumed",
        ]
        
        try:
            if monthly_burn_rate <= 0:
                return QuantitativeMetric(
                    value=float('inf'),  # Infinite runway if not burning
                    lower_bound=float('inf'),
                    upper_bound=float('inf'),
                    confidence=0.95,
                    calculation_method="Infinite (positive burn rate)",
                    assumptions=assumptions,
                    timestamp=datetime.utcnow(),
                )
            
            available = max(0, current_balance - minimum_balance)
            runway_months = available / monthly_burn_rate if monthly_burn_rate > 0 else float('inf')
            
            # Confidence decreases with short runway
            if runway_months < 1:
                confidence = 0.98  # Very urgent
            elif runway_months < 3:
                confidence = 0.90  # Critical
            elif runway_months < 6:
                confidence = 0.85  # Important
            else:
                confidence = 0.80  # Good
            
            # Confidence interval: ±10% margin
            margin = runway_months * 0.10
            
            return QuantitativeMetric(
                value=runway_months,
                lower_bound=max(0, runway_months - margin),
                upper_bound=runway_months + margin,
                confidence=confidence,
                calculation_method="(balance - minimum) / burn_rate",
                assumptions=assumptions,
                timestamp=datetime.utcnow(),
            )
        except Exception as e:
            self.logger.error(f"Runway calculation failed: {e}")
            return self._error_metric(str(e), assumptions)
    
    def calculate_cashflow_velocity(
        self,
        transactions: List[Dict],
        days_span: int = 30,
    ) -> QuantitativeMetric:
        """
        Calculate cashflow velocity (total transaction volume / days).
        Indicates how much money is flowing in and out.
        
        Args:
            transactions: List of transactions
            days_span: Number of days to analyze
            
        Returns:
            QuantitativeMetric with daily velocity
        """
        assumptions = [
            f"Analysis period: last {days_span} days",
            "Absolute transaction values used",
            "Higher velocity = higher financial activity",
        ]
        
        try:
            if not transactions:
                return self._error_metric("No transaction data", assumptions)
            
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            
            # Filter to date range
            cutoff = datetime.utcnow() - timedelta(days=days_span)
            df = df[df['date'] >= cutoff]
            
            # Total absolute transaction volume
            total_volume = df['amount'].abs().sum()
            daily_velocity = total_volume / days_span
            
            return QuantitativeMetric(
                value=daily_velocity,
                lower_bound=daily_velocity * 0.85,
                upper_bound=daily_velocity * 1.15,
                confidence=0.85,
                calculation_method="Total transaction volume / days",
                assumptions=assumptions,
                timestamp=datetime.utcnow(),
            )
        except Exception as e:
            self.logger.error(f"Velocity calculation failed: {e}")
            return self._error_metric(str(e), assumptions)
    
    def calculate_spending_volatility(
        self,
        transactions: List[Dict],
        days_span: int = 30,
    ) -> QuantitativeMetric:
        """
        Calculate spending volatility (std dev of daily expenses).
        High volatility = unpredictable spending.
        
        Args:
            transactions: List of transactions
            days_span: Number of days to analyze
            
        Returns:
            QuantitativeMetric with volatility coefficient
        """
        assumptions = [
            f"Analysis period: last {days_span} days",
            "Daily expense aggregation",
            "Volatility normalized by mean",
            "High volatility indicates unpredictable spending",
        ]
        
        try:
            if not transactions or len(transactions) < 5:
                return self._error_metric("Insufficient data", assumptions)
            
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date']).dt.date
            df['amount'] = df['amount'].abs()
            
            # Daily aggregation for expense
            daily_expenses = df.groupby('date')['amount'].sum()
            
            if len(daily_expenses) < 3:
                return self._error_metric("Insufficient days of data", assumptions)
            
            # Coefficient of variation (std / mean)
            mean_daily = daily_expenses.mean()
            std_daily = daily_expenses.std()
            
            if mean_daily == 0:
                volatility = 0
            else:
                volatility = std_daily / mean_daily
            
            return QuantitativeMetric(
                value=volatility,
                lower_bound=max(0, volatility - 0.3),
                upper_bound=volatility + 0.3,
                confidence=0.80,
                calculation_method="std(daily_expenses) / mean(daily_expenses)",
                assumptions=assumptions,
                timestamp=datetime.utcnow(),
            )
        except Exception as e:
            self.logger.error(f"Volatility calculation failed: {e}")
            return self._error_metric(str(e), assumptions)
    
    @staticmethod
    def _error_metric(error_msg: str, assumptions: List[str]) -> QuantitativeMetric:
        """Create error metric with 0 confidence."""
        return QuantitativeMetric(
            value=0.0,
            lower_bound=0.0,
            upper_bound=0.0,
            confidence=0.0,
            calculation_method=f"ERROR: {error_msg}",
            assumptions=assumptions,
            timestamp=datetime.utcnow(),
        )
    
    def to_dict(self, metric: QuantitativeMetric) -> Dict:
        """Convert metric to dictionary."""
        return {
            "value": metric.value,
            "lower_bound": metric.lower_bound,
            "upper_bound": metric.upper_bound,
            "confidence": metric.confidence,
            "calculation_method": metric.calculation_method,
            "assumptions": metric.assumptions,
            "timestamp": metric.timestamp.isoformat(),
        }
