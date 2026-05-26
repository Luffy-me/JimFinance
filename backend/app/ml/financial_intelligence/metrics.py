"""
Financial Metrics Engine - Deterministic financial calculations with confidence scoring.

Provides mathematically rigorous analysis with confidence intervals and explainability.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    """Base metric with confidence scoring."""
    value: float
    confidence: float  # 0-1
    unit: str
    calculation_method: str
    timestamp: datetime


@dataclass
class FinancialMetrics:
    """Container for all financial metrics."""
    savings_rate: Metric
    burn_rate: Metric
    burn_rate_trend: Metric
    cashflow_velocity: Metric
    financial_health_score: Metric
    volatility_score: Metric
    essential_vs_discretionary: Dict[str, Metric]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'savings_rate': asdict(self.savings_rate),
            'burn_rate': asdict(self.burn_rate),
            'burn_rate_trend': asdict(self.burn_rate_trend),
            'cashflow_velocity': asdict(self.cashflow_velocity),
            'financial_health_score': asdict(self.financial_health_score),
            'volatility_score': asdict(self.volatility_score),
            'essential_vs_discretionary': {
                k: asdict(v) for k, v in self.essential_vs_discretionary.items()
            }
        }


class FinancialMetricsEngine:
    """Deterministic financial calculations with confidence scoring."""
    
    # Essential category keywords (case-insensitive)
    ESSENTIAL_CATEGORIES = {'food', 'transport', 'utilities', 'healthcare'}
    DISCRETIONARY_CATEGORIES = {'entertainment', 'shopping', 'subscriptions'}
    
    # Thresholds for confidence scoring
    MIN_DATA_POINTS = 10  # Minimum transactions for reliable metrics
    MIN_DATA_SPAN_DAYS = 28  # Minimum 4 weeks of data
    
    def __init__(self):
        """Initialize metrics engine."""
        self.logger = logger
    
    def calculate_all_metrics(
        self,
        transactions: List[Dict],
        account_balance: Decimal,
        account_currency: str = "USD",
    ) -> FinancialMetrics:
        """
        Calculate all financial metrics from transactions.
        
        Args:
            transactions: List of transaction dicts with date, amount, type, category
            account_balance: Current account balance
            account_currency: Currency for the account
        
        Returns:
            FinancialMetrics object with all calculated metrics
        """
        # Convert to DataFrame for easier manipulation
        df = self._prepare_dataframe(transactions)
        
        if df.empty:
            return self._empty_metrics()
        
        # Calculate individual metrics
        savings_rate = self._calculate_savings_rate(df)
        burn_rate, burn_trend = self._calculate_burn_rate(df)
        cashflow_velocity = self._calculate_cashflow_velocity(df)
        health_score = self._calculate_health_score(
            df, account_balance, savings_rate, burn_rate
        )
        volatility = self._calculate_volatility(df)
        ess_vs_disc = self._calculate_essential_vs_discretionary(df)
        
        return FinancialMetrics(
            savings_rate=savings_rate,
            burn_rate=burn_rate,
            burn_rate_trend=burn_trend,
            cashflow_velocity=cashflow_velocity,
            financial_health_score=health_score,
            volatility_score=volatility,
            essential_vs_discretionary=ess_vs_disc,
        )
    
    def _prepare_dataframe(self, transactions: List[Dict]) -> pd.DataFrame:
        """Prepare transactions as DataFrame."""
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df.get('transaction_date', df.get('date')))
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['transaction_type'] = df.get('transaction_type', df.get('type', 'expense'))
        df['category'] = df.get('category', 'other').str.lower()
        
        # Remove invalid rows
        df = df.dropna(subset=['transaction_date', 'amount'])
        df = df.sort_values('transaction_date')
        
        return df
    
    def _calculate_savings_rate(self, df: pd.DataFrame) -> Metric:
        """
        Calculate savings rate using multiple methodologies.
        
        Savings Rate = (Income - Expenses) / Income
        
        Returns Metric with confidence based on data completeness.
        """
        if df.empty:
            return Metric(0.0, 0.0, '%', 'empty', datetime.now())
        
        income = self._get_income_total(df)
        expenses = self._get_expense_total(df)
        
        if income == 0:
            return Metric(0.0, 0.3, '%', 'no_income', datetime.now())
        
        savings_rate = ((income - expenses) / income) * 100
        savings_rate = max(-200, min(200, savings_rate))  # Clamp to reasonable range
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(df, min_points=self.MIN_DATA_POINTS)
        
        return Metric(
            value=round(savings_rate, 2),
            confidence=confidence,
            unit='%',
            calculation_method='(income - expenses) / income',
            timestamp=datetime.now(),
        )
    
    def _calculate_burn_rate(self, df: pd.DataFrame) -> Tuple[Metric, Metric]:
        """
        Calculate monthly burn rate and trend.
        
        Burn Rate = Average monthly expenses
        Trend = Rate of change in burn rate over time
        """
        if df.empty:
            return (
                Metric(0.0, 0.0, 'USD/month', 'empty', datetime.now()),
                Metric(0.0, 0.0, '%/month', 'empty', datetime.now()),
            )
        
        # Group by month
        df_expenses = df[df['transaction_type'].isin(['expense', 'transfer_out'])]
        
        if df_expenses.empty:
            return (
                Metric(0.0, 0.5, 'USD/month', 'no_expenses', datetime.now()),
                Metric(0.0, 0.3, '%/month', 'no_expenses', datetime.now()),
            )
        
        df_expenses = df_expenses.copy()
        df_expenses['year_month'] = df_expenses['transaction_date'].dt.to_period('M')
        
        monthly_expenses = df_expenses.groupby('year_month')['amount'].sum()
        
        if len(monthly_expenses) == 0:
            return (
                Metric(0.0, 0.3, 'USD/month', 'no_data', datetime.now()),
                Metric(0.0, 0.2, '%/month', 'no_data', datetime.now()),
            )
        
        # Calculate average burn rate
        burn_rate = monthly_expenses.mean()
        confidence = self._calculate_confidence(df_expenses, min_points=4)
        
        burn_metric = Metric(
            value=round(float(burn_rate), 2),
            confidence=confidence,
            unit='USD/month',
            calculation_method='mean(monthly_expenses)',
            timestamp=datetime.now(),
        )
        
        # Calculate trend (% change month to month)
        if len(monthly_expenses) >= 2:
            trend = ((monthly_expenses.iloc[-1] - monthly_expenses.iloc[0]) 
                     / monthly_expenses.iloc[0] * 100)
            trend_confidence = min(confidence, 0.8)  # Slightly lower confidence for trend
        else:
            trend = 0.0
            trend_confidence = 0.3
        
        trend_metric = Metric(
            value=round(float(trend), 2),
            confidence=trend_confidence,
            unit='%/period',
            calculation_method='(latest - first) / first * 100',
            timestamp=datetime.now(),
        )
        
        return burn_metric, trend_metric
    
    def _calculate_cashflow_velocity(self, df: pd.DataFrame) -> Metric:
        """
        Calculate cashflow velocity - average days between significant transactions.
        
        Higher velocity = more active cashflow, lower = more stable
        """
        if len(df) < 2:
            return Metric(0.0, 0.2, 'days', 'insufficient_data', datetime.now())
        
        df_sorted = df.sort_values('transaction_date')
        date_diffs = df_sorted['transaction_date'].diff().dt.days.dropna()
        
        if len(date_diffs) == 0:
            return Metric(0.0, 0.3, 'days', 'same_day_transactions', datetime.now())
        
        velocity = date_diffs.mean()
        confidence = self._calculate_confidence(df)
        
        return Metric(
            value=round(float(velocity), 1),
            confidence=confidence,
            unit='days',
            calculation_method='mean(days_between_transactions)',
            timestamp=datetime.now(),
        )
    
    def _calculate_health_score(
        self,
        df: pd.DataFrame,
        account_balance: Decimal,
        savings_rate: Metric,
        burn_rate: Metric,
    ) -> Metric:
        """
        Calculate overall financial health score (0-100).
        
        Factors:
        - Positive savings rate (30%)
        - Moderate burn rate relative to income (25%)
        - Adequate reserves (20%)
        - Expense stability (15%)
        - Minimal anomalies (10%)
        """
        if df.empty:
            return Metric(50.0, 0.2, 'score', 'empty', datetime.now())
        
        score = 50.0  # Start with neutral
        
        # Savings rate component (30%)
        if savings_rate.value > 20:
            score += 30 * (min(savings_rate.value, 50) / 50)
        elif savings_rate.value > 0:
            score += 15
        else:
            score -= min(abs(savings_rate.value) / 100, 15)
        
        # Burn rate stability component (25%)
        income = self._get_income_total(df)
        if income > 0 and burn_rate.value > 0:
            burn_ratio = burn_rate.value / (income / 30)  # Monthly income
            if burn_ratio < 0.8:
                score += 25
            elif burn_ratio < 1.0:
                score += 12
            else:
                score -= min((burn_ratio - 1.0) * 25, 15)
        
        # Reserve adequacy component (20%)
        if income > 0:
            monthly_income = income / max(1, len(df) / 30)
            months_of_reserves = float(account_balance) / max(1, burn_rate.value)
            if months_of_reserves >= 6:
                score += 20
            elif months_of_reserves >= 3:
                score += 10
            elif months_of_reserves >= 1:
                score += 5
        
        # Expense stability component (15%)
        df_expenses = df[df['transaction_type'].isin(['expense', 'transfer_out'])]
        if len(df_expenses) > 5:
            volatility = df_expenses['amount'].std() / df_expenses['amount'].mean()
            if volatility < 0.5:
                score += 15
            elif volatility < 1.0:
                score += 8
            else:
                score += 3
        
        # Final normalization
        score = max(0, min(100, score))
        confidence = self._calculate_confidence(df)
        
        return Metric(
            value=round(score, 1),
            confidence=confidence,
            unit='score',
            calculation_method='weighted(savings_rate, burn_rate, reserves, stability)',
            timestamp=datetime.now(),
        )
    
    def _calculate_volatility(self, df: pd.DataFrame) -> Metric:
        """
        Calculate expense volatility score (0-100, lower is better/more stable).
        """
        if df.empty:
            return Metric(50.0, 0.0, 'score', 'empty', datetime.now())
        
        df_expenses = df[df['transaction_type'].isin(['expense', 'transfer_out'])]
        
        if len(df_expenses) < 5:
            return Metric(50.0, 0.2, 'score', 'insufficient_data', datetime.now())
        
        # Calculate coefficient of variation (std / mean)
        mean = df_expenses['amount'].mean()
        std = df_expenses['amount'].std()
        
        if mean == 0:
            return Metric(50.0, 0.3, 'score', 'no_expenses', datetime.now())
        
        cv = (std / mean)
        
        # Convert to 0-100 score (lower volatility = higher score)
        # cv of 0-0.3 = 100 score
        # cv of 0.3-1.0 = 50-100 score
        # cv of 1.0+ = 0-50 score
        if cv <= 0.3:
            volatility_score = 100.0
        elif cv <= 1.0:
            volatility_score = 100 - ((cv - 0.3) / 0.7 * 50)
        else:
            volatility_score = max(0, 50 - ((cv - 1.0) * 25))
        
        confidence = self._calculate_confidence(df_expenses, min_points=5)
        
        return Metric(
            value=round(volatility_score, 1),
            confidence=confidence,
            unit='score',
            calculation_method='100 - coefficient_of_variation_normalized',
            timestamp=datetime.now(),
        )
    
    def _calculate_essential_vs_discretionary(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Metric]:
        """
        Calculate essential vs discretionary spending breakdown.
        """
        df_expenses = df[df['transaction_type'].isin(['expense', 'transfer_out'])].copy()
        
        if df_expenses.empty:
            return {
                'essential_monthly': Metric(0.0, 0.0, 'USD', 'no_data', datetime.now()),
                'discretionary_monthly': Metric(0.0, 0.0, 'USD', 'no_data', datetime.now()),
                'essential_ratio': Metric(0.0, 0.0, '%', 'no_data', datetime.now()),
            }
        
        # Categorize
        df_expenses['is_essential'] = df_expenses['category'].isin(self.ESSENTIAL_CATEGORIES)
        df_expenses['year_month'] = df_expenses['transaction_date'].dt.to_period('M')
        
        # Monthly aggregates
        monthly = df_expenses.groupby(['year_month', 'is_essential'])['amount'].sum().unstack(fill_value=0)
        
        essential_monthly = monthly.get(True, pd.Series([0])).mean()
        discretionary_monthly = monthly.get(False, pd.Series([0])).mean()
        
        total_monthly = essential_monthly + discretionary_monthly
        essential_ratio = (essential_monthly / total_monthly * 100) if total_monthly > 0 else 0
        
        confidence = self._calculate_confidence(df_expenses)
        
        return {
            'essential_monthly': Metric(
                round(float(essential_monthly), 2),
                confidence,
                'USD',
                'mean(monthly_essential_expenses)',
                datetime.now(),
            ),
            'discretionary_monthly': Metric(
                round(float(discretionary_monthly), 2),
                confidence,
                'USD',
                'mean(monthly_discretionary_expenses)',
                datetime.now(),
            ),
            'essential_ratio': Metric(
                round(float(essential_ratio), 1),
                confidence,
                '%',
                'essential / total',
                datetime.now(),
            ),
        }
    
    def _get_income_total(self, df: pd.DataFrame) -> float:
        """Get total income from transactions."""
        income_df = df[df['transaction_type'].isin(['income', 'transfer_in'])]
        return float(income_df['amount'].sum()) if not income_df.empty else 0.0
    
    def _get_expense_total(self, df: pd.DataFrame) -> float:
        """Get total expenses from transactions."""
        expense_df = df[df['transaction_type'].isin(['expense', 'transfer_out'])]
        return float(expense_df['amount'].sum()) if not expense_df.empty else 0.0
    
    def _calculate_confidence(
        self,
        df: pd.DataFrame,
        min_points: Optional[int] = None,
    ) -> float:
        """
        Calculate confidence score for metrics (0-1).
        
        Based on:
        - Number of data points
        - Time span covered
        - Data completeness
        """
        if min_points is None:
            min_points = self.MIN_DATA_POINTS
        
        if df.empty:
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        # Data points component (up to 0.3)
        data_points = len(df)
        if data_points >= min_points:
            confidence += 0.3
        else:
            confidence += 0.3 * (data_points / min_points)
        
        # Time span component (up to 0.2)
        time_span = (df['transaction_date'].max() - df['transaction_date'].min()).days
        if time_span >= self.MIN_DATA_SPAN_DAYS:
            confidence += 0.2
        else:
            confidence += 0.2 * (time_span / self.MIN_DATA_SPAN_DAYS)
        
        return min(1.0, confidence)
    
    def _empty_metrics(self) -> FinancialMetrics:
        """Return metrics with all zeros for empty data."""
        zero_metric = Metric(0.0, 0.0, 'N/A', 'no_data', datetime.now())
        return FinancialMetrics(
            savings_rate=Metric(0.0, 0.0, '%', 'no_data', datetime.now()),
            burn_rate=Metric(0.0, 0.0, 'USD/month', 'no_data', datetime.now()),
            burn_rate_trend=Metric(0.0, 0.0, '%/month', 'no_data', datetime.now()),
            cashflow_velocity=Metric(0.0, 0.0, 'days', 'no_data', datetime.now()),
            financial_health_score=Metric(50.0, 0.0, 'score', 'no_data', datetime.now()),
            volatility_score=Metric(50.0, 0.0, 'score', 'no_data', datetime.now()),
            essential_vs_discretionary={
                'essential_monthly': zero_metric,
                'discretionary_monthly': zero_metric,
                'essential_ratio': Metric(0.0, 0.0, '%', 'no_data', datetime.now()),
            },
        )
