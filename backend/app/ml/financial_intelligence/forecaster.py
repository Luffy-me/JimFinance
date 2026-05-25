"""
Forecasting Engine - Monthly spending forecasts with confidence intervals.

Provides ARIMA-like and Prophet-like forecasting capabilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Forecast:
    """Single forecast data point."""
    period: str  # YYYY-MM format
    forecasted_value: float
    lower_confidence_bound: float
    upper_confidence_bound: float
    confidence_level: float


@dataclass
class CategoryForecast:
    """Forecast for a spending category."""
    category: str
    forecasts: List[Forecast]
    trend: float  # % change direction
    seasonality: float  # Seasonality strength 0-1
    methodology: str


class ForecastingEngine:
    """Provides spending forecasts using time series analysis."""
    
    # Forecast horizon
    DEFAULT_FORECAST_MONTHS = 12
    MIN_HISTORICAL_MONTHS = 3
    
    def __init__(self):
        """Initialize forecasting engine."""
        self.logger = logger
    
    def forecast_spending(
        self,
        transactions: List[Dict],
        forecast_months: int = DEFAULT_FORECAST_MONTHS,
        category: Optional[str] = None,
    ) -> Dict[str, any]:
        """
        Generate spending forecast for next N months.
        
        Args:
            transactions: Historical transactions
            forecast_months: Number of months to forecast
            category: Specific category to forecast, or None for overall
        
        Returns:
            Dict with forecasts and analysis
        """
        df = self._prepare_dataframe(transactions)
        
        if df.empty:
            return self._empty_forecast()
        
        # Filter by category if specified
        if category:
            df = df[df['category'].str.lower() == category.lower()]
            if df.empty:
                return self._empty_forecast()
        
        # Generate monthly time series
        monthly_ts = self._create_monthly_timeseries(df)
        
        if len(monthly_ts) < self.MIN_HISTORICAL_MONTHS:
            return self._insufficient_data_forecast()
        
        # Simple forecast using exponential smoothing
        forecasts = self._forecast_exponential_smoothing(
            monthly_ts,
            periods=forecast_months,
        )
        
        # Analyze trend and seasonality
        trend = self._calculate_trend(monthly_ts)
        seasonality = self._detect_seasonality_strength(monthly_ts)
        
        return {
            'category': category or 'all',
            'historical_months': len(monthly_ts),
            'forecast_months': forecast_months,
            'last_known_value': round(float(monthly_ts.iloc[-1]), 2),
            'average_historical': round(float(monthly_ts.mean()), 2),
            'trend_direction': 'increasing' if trend > 0.05 else 'decreasing' if trend < -0.05 else 'stable',
            'trend_percentage': round(trend * 100, 2),
            'seasonality_strength': round(seasonality, 2),
            'forecasts': forecasts,
            'methodology': 'exponential_smoothing_with_confidence_intervals',
        }
    
    def _prepare_dataframe(self, transactions: List[Dict]) -> pd.DataFrame:
        """Prepare transactions as DataFrame."""
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        
        # Standardize columns
        df['transaction_date'] = pd.to_datetime(
            df.get('transaction_date') or df.get('date'),
            errors='coerce'
        )
        df['amount'] = pd.to_numeric(df.get('amount'), errors='coerce')
        df['transaction_type'] = df.get('transaction_type', df.get('type', 'expense')).str.lower()
        df['category'] = df.get('category', 'other').str.lower()
        
        # Keep only expenses
        df = df[df['transaction_type'].isin(['expense', 'transfer_out'])]
        
        # Remove invalid rows
        df = df.dropna(subset=['transaction_date', 'amount'])
        df = df.sort_values('transaction_date')
        
        return df
    
    def _create_monthly_timeseries(self, df: pd.DataFrame) -> pd.Series:
        """Create monthly time series from transactions."""
        if df.empty:
            return pd.Series()
        
        df = df.copy()
        df['year_month'] = df['transaction_date'].dt.to_period('M')
        
        monthly = df.groupby('year_month')['amount'].sum()
        
        return monthly
    
    def _forecast_exponential_smoothing(
        self,
        timeseries: pd.Series,
        periods: int = 12,
        alpha: float = 0.3,
    ) -> List[Dict]:
        """
        Simple exponential smoothing forecast.
        
        Uses exponential smoothing with confidence intervals.
        """
        if len(timeseries) < 1:
            return []
        
        values = timeseries.values.astype(float)
        
        # Calculate smoothed series
        smoothed = [values[0]]
        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[i-1]
            smoothed.append(smoothed_value)
        
        # Last level for forecasting
        level = smoothed[-1]
        
        # Calculate residuals for confidence intervals
        residuals = [values[i] - smoothed[i] for i in range(len(values))]
        residual_std = np.std(residuals) if len(residuals) > 1 else 0
        
        # Generate forecasts
        forecasts = []
        current_date = timeseries.index[-1].to_timestamp()
        
        for i in range(1, periods + 1):
            forecast_date = current_date + pd.DateOffset(months=i)
            period_str = forecast_date.strftime('%Y-%m')
            
            # Point forecast
            point_forecast = level
            
            # Confidence intervals (95%)
            # Standard error increases with forecast horizon
            se = residual_std * np.sqrt(1 + (i / len(values)))
            lower = point_forecast - 1.96 * se
            upper = point_forecast + 1.96 * se
            
            forecasts.append({
                'period': period_str,
                'forecasted_value': round(max(0, float(point_forecast)), 2),
                'lower_confidence_bound': round(max(0, float(lower)), 2),
                'upper_confidence_bound': round(float(upper), 2),
                'confidence_level': 0.95,
            })
        
        return forecasts
    
    def _calculate_trend(self, timeseries: pd.Series) -> float:
        """
        Calculate trend direction and magnitude.
        
        Returns % change from first to last period.
        """
        if len(timeseries) < 2:
            return 0.0
        
        values = timeseries.values
        first = values[0]
        last = values[-1]
        
        if first == 0:
            return 0.0
        
        return (last - first) / first
    
    def _detect_seasonality_strength(self, timeseries: pd.Series) -> float:
        """
        Detect strength of seasonality (0-1).
        
        Returns coefficient of variation of seasonal indices.
        """
        if len(timeseries) < 12:
            return 0.0  # Need at least 12 months
        
        # Calculate seasonal indices
        indices = self._calculate_seasonal_indices(timeseries)
        
        if not indices:
            return 0.0
        
        # Coefficient of variation of indices
        mean_index = np.mean(list(indices.values()))
        if mean_index == 0:
            return 0.0
        
        variance = np.var(list(indices.values()))
        std_dev = np.sqrt(variance)
        cv = std_dev / mean_index
        
        # Convert to 0-1 scale
        return min(1.0, cv)
    
    def _calculate_seasonal_indices(self, timeseries: pd.Series) -> Dict[int, float]:
        """Calculate seasonal indices by month."""
        indices = {}
        
        # Group by month
        values = timeseries.values
        periods = timeseries.index
        
        month_groups = {}
        for i, period in enumerate(periods):
            month = int(str(period).split('-')[1])
            if month not in month_groups:
                month_groups[month] = []
            month_groups[month].append(values[i])
        
        # Calculate average for each month
        overall_mean = np.mean(values)
        
        for month, month_values in month_groups.items():
            month_avg = np.mean(month_values)
            if overall_mean > 0:
                indices[month] = month_avg / overall_mean
            else:
                indices[month] = 1.0
        
        return indices
    
    def forecast_by_category(
        self,
        transactions: List[Dict],
        forecast_months: int = DEFAULT_FORECAST_MONTHS,
    ) -> Dict[str, any]:
        """
        Generate forecasts for each spending category.
        
        Returns dict with forecasts per category.
        """
        df = self._prepare_dataframe(transactions)
        
        if df.empty:
            return {'categories': {}}
        
        # Get unique categories
        categories = df['category'].unique()
        
        results = {}
        for category in categories:
            category_forecast = self.forecast_spending(
                transactions,
                forecast_months=forecast_months,
                category=category,
            )
            
            if category_forecast.get('forecasts'):
                results[category] = category_forecast
        
        return {
            'categories': results,
            'total_categories': len(results),
            'forecast_months': forecast_months,
        }
    
    def _empty_forecast(self) -> Dict:
        """Return empty forecast."""
        return {
            'category': 'all',
            'forecasts': [],
            'error': 'Insufficient data',
        }
    
    def _insufficient_data_forecast(self) -> Dict:
        """Return insufficient data forecast."""
        return {
            'category': 'all',
            'forecasts': [],
            'error': f'Need at least {self.MIN_HISTORICAL_MONTHS} months of historical data',
            'recommendation': 'Add more transactions to generate accurate forecasts',
        }
    
    def forecast_income(
        self,
        transactions: List[Dict],
        forecast_months: int = DEFAULT_FORECAST_MONTHS,
    ) -> Dict[str, any]:
        """
        Generate income forecast.
        
        Similar to spending forecast but for income transactions.
        """
        if not transactions:
            return self._empty_forecast()
        
        df = pd.DataFrame(transactions)
        
        # Standardize columns
        df['transaction_date'] = pd.to_datetime(
            df.get('transaction_date') or df.get('date'),
            errors='coerce'
        )
        df['amount'] = pd.to_numeric(df.get('amount'), errors='coerce')
        df['transaction_type'] = df.get('transaction_type', df.get('type', 'income')).str.lower()
        
        # Keep only income
        df = df[df['transaction_type'].isin(['income', 'transfer_in'])]
        
        # Remove invalid rows
        df = df.dropna(subset=['transaction_date', 'amount'])
        
        if df.empty:
            return {
                'category': 'income',
                'forecasts': [],
                'error': 'No income transactions found',
            }
        
        df = df.sort_values('transaction_date')
        
        # Create monthly time series
        df['year_month'] = df['transaction_date'].dt.to_period('M')
        monthly_ts = df.groupby('year_month')['amount'].sum()
        
        if len(monthly_ts) < self.MIN_HISTORICAL_MONTHS:
            return self._insufficient_data_forecast()
        
        # Generate forecasts
        forecasts = self._forecast_exponential_smoothing(monthly_ts, periods=forecast_months)
        
        trend = self._calculate_trend(monthly_ts)
        
        return {
            'category': 'income',
            'historical_months': len(monthly_ts),
            'forecast_months': forecast_months,
            'last_known_value': round(float(monthly_ts.iloc[-1]), 2),
            'average_historical': round(float(monthly_ts.mean()), 2),
            'trend_direction': 'increasing' if trend > 0.05 else 'decreasing' if trend < -0.05 else 'stable',
            'trend_percentage': round(trend * 100, 2),
            'forecasts': forecasts,
            'methodology': 'exponential_smoothing_with_confidence_intervals',
        }
