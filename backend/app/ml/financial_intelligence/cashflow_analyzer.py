"""
Cashflow Analysis Module - Inflow/outflow velocity and seasonality detection.

Analyzes cashflow patterns, velocity, and smoothness.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class CashflowMetrics:
    """Container for cashflow analysis metrics."""
    inflow_velocity: float  # Days between income transactions
    outflow_velocity: float  # Days between expenses
    cashflow_smoothness: float  # 0-100, higher = more stable
    peak_spending_month: str
    peak_spending_amount: float
    trough_spending_month: str
    trough_spending_amount: float
    liquidity_ratio: float  # Current balance / avg monthly burn
    has_seasonality: bool
    seasonality_pattern: Dict[str, float]  # Month -> avg spending
    average_monthly_inflow: float
    average_monthly_outflow: float
    inflow_consistency: float  # 0-1, higher = more consistent
    outflow_consistency: float  # 0-1, higher = more consistent


class CashflowAnalyzer:
    """Analyzes cashflow patterns and characteristics."""
    
    def __init__(self):
        """Initialize cashflow analyzer."""
        self.logger = logger
    
    def analyze_cashflow(
        self,
        transactions: List[Dict],
        account_balance: Decimal = None,
    ) -> CashflowMetrics:
        """
        Analyze cashflow patterns from transactions.
        
        Args:
            transactions: List of transaction dicts
            account_balance: Current account balance (for liquidity ratio)
        
        Returns:
            CashflowMetrics object with all analysis
        """
        if not transactions:
            return self._empty_metrics()
        
        # Prepare DataFrame
        df = self._prepare_dataframe(transactions)
        
        if df.empty:
            return self._empty_metrics()
        
        # Separate inflows and outflows
        inflows = df[df['transaction_type'].isin(['income', 'transfer_in'])]
        outflows = df[df['transaction_type'].isin(['expense', 'transfer_out'])]
        
        # Calculate velocity
        inflow_velocity = self._calculate_velocity(inflows)
        outflow_velocity = self._calculate_velocity(outflows)
        
        # Smoothness analysis
        smoothness = self._calculate_smoothness(df)
        
        # Seasonality analysis
        peak_month, peak_amount = self._find_peak_month(outflows)
        trough_month, trough_amount = self._find_trough_month(outflows)
        
        # Seasonality pattern
        has_seasonality, seasonality = self._detect_seasonality(outflows)
        
        # Liquidity ratio
        liquidity = self._calculate_liquidity_ratio(account_balance, outflows)
        
        # Flow consistency
        inflow_consistency = self._calculate_consistency(inflows)
        outflow_consistency = self._calculate_consistency(outflows)
        
        # Monthly averages
        avg_inflow = self._calculate_average_monthly(inflows)
        avg_outflow = self._calculate_average_monthly(outflows)
        
        return CashflowMetrics(
            inflow_velocity=round(inflow_velocity, 1),
            outflow_velocity=round(outflow_velocity, 1),
            cashflow_smoothness=round(smoothness, 1),
            peak_spending_month=peak_month,
            peak_spending_amount=round(peak_amount, 2),
            trough_spending_month=trough_month,
            trough_spending_amount=round(trough_amount, 2),
            liquidity_ratio=round(liquidity, 2),
            has_seasonality=has_seasonality,
            seasonality_pattern=seasonality,
            average_monthly_inflow=round(avg_inflow, 2),
            average_monthly_outflow=round(avg_outflow, 2),
            inflow_consistency=round(inflow_consistency, 2),
            outflow_consistency=round(outflow_consistency, 2),
        )
    
    def _prepare_dataframe(self, transactions: List[Dict]) -> pd.DataFrame:
        """Prepare transactions as DataFrame."""
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        
        # Standardize column names
        df['transaction_date'] = pd.to_datetime(
            df.get('transaction_date') or df.get('date'),
            errors='coerce'
        )
        df['amount'] = pd.to_numeric(df.get('amount'), errors='coerce')
        df['transaction_type'] = df.get('transaction_type', df.get('type', 'expense')).str.lower()
        
        # Remove invalid rows
        df = df.dropna(subset=['transaction_date', 'amount'])
        df = df.sort_values('transaction_date')
        
        return df
    
    def _calculate_velocity(self, flow_df: pd.DataFrame) -> float:
        """Calculate velocity (average days between transactions)."""
        if len(flow_df) < 2:
            return 0.0
        
        dates = sorted(flow_df['transaction_date'].unique())
        
        if len(dates) < 2:
            return 0.0
        
        intervals = []
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i-1]).days
            if interval > 0:
                intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        return statistics.mean(intervals)
    
    def _calculate_smoothness(self, df: pd.DataFrame) -> float:
        """
        Calculate cashflow smoothness (0-100).
        
        Measures consistency of cash inflows and outflows.
        Higher score = more stable/predictable cashflow.
        """
        outflows = df[df['transaction_type'].isin(['expense', 'transfer_out'])]
        
        if len(outflows) < 3:
            return 50.0
        
        # Group by month
        outflows = outflows.copy()
        outflows['year_month'] = outflows['transaction_date'].dt.to_period('M')
        
        monthly_totals = outflows.groupby('year_month')['amount'].sum()
        
        if len(monthly_totals) < 2:
            return 50.0
        
        # Calculate coefficient of variation
        mean = monthly_totals.mean()
        if mean == 0:
            return 50.0
        
        std = monthly_totals.std()
        cv = std / mean
        
        # Convert to 0-100 score
        # CV of 0-0.1 = 100
        # CV of 0.1-0.3 = 80-100
        # CV of 0.3-0.5 = 60-80
        # CV of 0.5-1.0 = 20-60
        # CV > 1.0 = 0-20
        
        if cv <= 0.1:
            return 100.0
        elif cv <= 0.3:
            return 80 + ((0.3 - cv) / 0.2 * 20)
        elif cv <= 0.5:
            return 60 + ((0.5 - cv) / 0.2 * 20)
        elif cv <= 1.0:
            return 20 + ((1.0 - cv) / 0.5 * 40)
        else:
            return max(0, 20 - ((cv - 1.0) * 10))
    
    def _find_peak_month(self, outflows: pd.DataFrame) -> Tuple[str, float]:
        """Find month with highest spending."""
        if outflows.empty:
            return 'N/A', 0.0
        
        outflows = outflows.copy()
        outflows['year_month'] = outflows['transaction_date'].dt.to_period('M')
        
        monthly = outflows.groupby('year_month')['amount'].sum()
        
        if monthly.empty:
            return 'N/A', 0.0
        
        peak_period = monthly.idxmax()
        peak_amount = monthly.max()
        
        return str(peak_period), float(peak_amount)
    
    def _find_trough_month(self, outflows: pd.DataFrame) -> Tuple[str, float]:
        """Find month with lowest spending."""
        if outflows.empty:
            return 'N/A', 0.0
        
        outflows = outflows.copy()
        outflows['year_month'] = outflows['transaction_date'].dt.to_period('M')
        
        monthly = outflows.groupby('year_month')['amount'].sum()
        
        if monthly.empty:
            return 'N/A', 0.0
        
        trough_period = monthly.idxmin()
        trough_amount = monthly.min()
        
        return str(trough_period), float(trough_amount)
    
    def _detect_seasonality(self, outflows: pd.DataFrame) -> Tuple[bool, Dict[str, float]]:
        """
        Detect if spending has seasonal patterns.
        
        Returns:
            (has_seasonality, month_pattern_dict)
        """
        if outflows.empty or len(outflows) < 12:
            return False, {}
        
        outflows = outflows.copy()
        outflows['month'] = outflows['transaction_date'].dt.month
        outflows['year_month'] = outflows['transaction_date'].dt.to_period('M')
        
        # Get average spending by calendar month
        monthly_avg = outflows.groupby('month')['amount'].mean()
        
        if len(monthly_avg) < 3:
            return False, {}
        
        # Calculate seasonality coefficient
        overall_mean = monthly_avg.mean()
        if overall_mean == 0:
            return False, {}
        
        # Seasonality index: ratio of month avg to overall avg
        seasonality_index = (monthly_avg / overall_mean).to_dict()
        
        # Check if there's significant variation
        values = list(seasonality_index.values())
        if len(values) > 1:
            std_dev = statistics.stdev(values)
            coefficient_of_variation = std_dev / statistics.mean(values)
            
            # Significant seasonality if CV > 0.15
            has_seasonality = coefficient_of_variation > 0.15
        else:
            has_seasonality = False
        
        # Convert month numbers to names
        month_names = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
        
        pattern = {month_names[m]: round(v, 2) for m, v in seasonality_index.items()}
        
        return has_seasonality, pattern
    
    def _calculate_liquidity_ratio(
        self,
        account_balance,
        outflows: pd.DataFrame,
    ) -> float:
        """
        Calculate liquidity ratio (balance / avg monthly burn).
        
        Months of runway at current burn rate.
        """
        if account_balance is None or outflows.empty:
            return 0.0
        
        account_balance = float(account_balance)
        
        if account_balance <= 0:
            return 0.0
        
        avg_monthly_outflow = self._calculate_average_monthly(outflows)
        
        if avg_monthly_outflow == 0:
            return 999.0  # Infinite
        
        return account_balance / avg_monthly_outflow
    
    def _calculate_consistency(self, flow_df: pd.DataFrame) -> float:
        """
        Calculate flow consistency (0-1).
        
        Measures how consistent the flow amounts are.
        """
        if len(flow_df) < 2:
            return 0.0
        
        amounts = flow_df['amount'].values
        
        if len(amounts) == 0 or sum(amounts) == 0:
            return 0.0
        
        try:
            mean = statistics.mean(amounts)
            if mean == 0:
                return 0.0
            
            std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
            cv = std_dev / mean
            
            # Convert CV to 0-1 consistency score
            # CV of 0-0.2 = 1.0
            # CV of 0.2-0.5 = 0.6-1.0
            # CV of 0.5-1.0 = 0.2-0.6
            # CV > 1.0 = 0-0.2
            
            if cv <= 0.2:
                return 1.0
            elif cv <= 0.5:
                return 0.6 + ((0.5 - cv) / 0.3 * 0.4)
            elif cv <= 1.0:
                return 0.2 + ((1.0 - cv) / 0.5 * 0.4)
            else:
                return max(0.0, 0.2 - ((cv - 1.0) * 0.1))
        except (statistics.StatisticsError, ZeroDivisionError):
            return 0.0
    
    def _calculate_average_monthly(self, flow_df: pd.DataFrame) -> float:
        """Calculate average monthly flow amount."""
        if flow_df.empty:
            return 0.0
        
        flow_df = flow_df.copy()
        flow_df['year_month'] = flow_df['transaction_date'].dt.to_period('M')
        
        monthly_totals = flow_df.groupby('year_month')['amount'].sum()
        
        if len(monthly_totals) == 0:
            return 0.0
        
        return float(monthly_totals.mean())
    
    def _empty_metrics(self) -> CashflowMetrics:
        """Return empty metrics for no transactions."""
        return CashflowMetrics(
            inflow_velocity=0.0,
            outflow_velocity=0.0,
            cashflow_smoothness=50.0,
            peak_spending_month='N/A',
            peak_spending_amount=0.0,
            trough_spending_month='N/A',
            trough_spending_amount=0.0,
            liquidity_ratio=0.0,
            has_seasonality=False,
            seasonality_pattern={},
            average_monthly_inflow=0.0,
            average_monthly_outflow=0.0,
            inflow_consistency=0.0,
            outflow_consistency=0.0,
        )
    
    def identify_peak_spending_opportunities(
        self,
        transactions: List[Dict],
    ) -> Dict[str, any]:
        """
        Identify spending peaks and opportunities for smoothing.
        
        Returns analysis of spending patterns.
        """
        df = self._prepare_dataframe(transactions)
        
        if df.empty:
            return {'opportunities': []}
        
        outflows = df[df['transaction_type'].isin(['expense', 'transfer_out'])]
        
        # Group by category and month
        outflows = outflows.copy()
        outflows['year_month'] = outflows['transaction_date'].dt.to_period('M')
        outflows['category'] = outflows.get('category', 'other').str.lower()
        
        # Find peak categories and months
        category_monthly = outflows.groupby(['year_month', 'category'])['amount'].sum()
        
        opportunities = []
        
        if not category_monthly.empty:
            # Get top spending peaks
            top_peaks = category_monthly.nlargest(5)
            
            for (month, category), amount in top_peaks.items():
                opportunities.append({
                    'month': str(month),
                    'category': category,
                    'amount': round(float(amount), 2),
                    'type': 'peak_spending',
                })
        
        return {
            'peak_opportunities': opportunities,
            'total_count': len(opportunities),
        }
