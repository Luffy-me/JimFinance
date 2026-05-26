"""
Behavioral Analysis Module - Spending behavior clustering and pattern detection.

Analyzes spending behavior patterns, lifestyle changes, and budget constraints.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from collections import Counter
from dataclasses import dataclass
import statistics

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class BehaviorInsight:
    """Single behavioral insight."""
    insight_type: str  # lifestyle_inflation, discretionary_spike, budget_constraint, etc.
    title: str
    description: str
    metric_value: Optional[float]
    metric_unit: Optional[str]
    confidence: float  # 0-1
    recommendation: str
    time_period: str


class BehavioralAnalyzer:
    """Analyzes spending behavior and patterns."""
    
    # Category classification
    ESSENTIAL_CATEGORIES = {'food', 'transport', 'utilities', 'healthcare'}
    DISCRETIONARY_CATEGORIES = {'entertainment', 'shopping', 'subscriptions'}
    
    # Thresholds for detection
    LIFESTYLE_INFLATION_THRESHOLD = 0.15  # 15% increase
    SPENDING_SPIKE_THRESHOLD = 2.0  # 2x normal
    BUDGET_CONSTRAINT_THRESHOLD = 0.80  # Spending 80%+ of income
    
    def __init__(self):
        """Initialize behavioral analyzer."""
        self.logger = logger
    
    def analyze_behavior(
        self,
        transactions: List[Dict],
        monthly_income: Optional[float] = None,
    ) -> List[BehaviorInsight]:
        """
        Analyze spending behavior and generate insights.
        
        Args:
            transactions: Historical transactions
            monthly_income: Average monthly income
        
        Returns:
            List of BehaviorInsight objects
        """
        if not transactions:
            return []
        
        df = self._prepare_dataframe(transactions)
        
        if df.empty:
            return []
        
        insights = []
        
        # Detect lifestyle inflation
        lifestyle_insights = self._detect_lifestyle_changes(df)
        insights.extend(lifestyle_insights)
        
        # Detect discretionary spending spikes
        discretionary_insights = self._detect_spending_spikes(df)
        insights.extend(discretionary_insights)
        
        # Detect budget constraints
        if monthly_income:
            constraint_insights = self._detect_budget_constraints(df, monthly_income)
            insights.extend(constraint_insights)
        
        # Detect category shifting
        category_insights = self._detect_category_shifts(df)
        insights.extend(category_insights)
        
        # Detect spending patterns
        pattern_insights = self._detect_spending_patterns(df)
        insights.extend(pattern_insights)
        
        return insights
    
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
    
    def _detect_lifestyle_changes(self, df: pd.DataFrame) -> List[BehaviorInsight]:
        """Detect lifestyle inflation or deflation."""
        insights = []
        
        if len(df) < 60:  # Need at least 2 months
            return insights
        
        df = df.copy()
        df['year_month'] = df['transaction_date'].dt.to_period('M')
        
        # Monthly totals
        monthly_totals = df.groupby('year_month')['amount'].sum()
        
        if len(monthly_totals) < 2:
            return insights
        
        # Compare first 50% to last 50%
        mid = len(monthly_totals) // 2
        first_half_avg = monthly_totals.iloc[:mid].mean()
        second_half_avg = monthly_totals.iloc[mid:].mean()
        
        if first_half_avg == 0:
            return insights
        
        change = (second_half_avg - first_half_avg) / first_half_avg
        
        if change > self.LIFESTYLE_INFLATION_THRESHOLD:
            insights.append(BehaviorInsight(
                insight_type='lifestyle_inflation',
                title='Spending is increasing',
                description=f'Your spending has increased by {change*100:.1f}% over time. This could indicate lifestyle inflation.',
                metric_value=change * 100,
                metric_unit='%',
                confidence=0.7,
                recommendation='Review discretionary spending and consider budget adjustment.',
                time_period='over_all_time',
            ))
        elif change < -self.LIFESTYLE_INFLATION_THRESHOLD:
            insights.append(BehaviorInsight(
                insight_type='lifestyle_deflation',
                title='Spending is decreasing',
                description=f'Your spending has decreased by {abs(change)*100:.1f}%. Great budgeting discipline!',
                metric_value=abs(change) * 100,
                metric_unit='%',
                confidence=0.8,
                recommendation='Maintain your current spending discipline and consider increasing savings.',
                time_period='over_all_time',
            ))
        
        return insights
    
    def _detect_spending_spikes(self, df: pd.DataFrame) -> List[BehaviorInsight]:
        """Detect unusual spending spikes."""
        insights = []
        
        if len(df) < 10:
            return insights
        
        df = df.copy()
        
        # Analyze by category
        for category in df['category'].unique():
            category_df = df[df['category'] == category]
            
            if len(category_df) < 3:
                continue
            
            amounts = category_df['amount'].values
            
            # Calculate mean and std dev
            mean = statistics.mean(amounts)
            if len(amounts) > 1:
                std_dev = statistics.stdev(amounts)
            else:
                std_dev = 0
            
            # Find outliers (> 2 std devs above mean)
            threshold = mean + (2 * std_dev)
            
            outliers = category_df[category_df['amount'] > threshold]
            
            if len(outliers) > 0:
                latest_spike = outliers.iloc[-1]
                spike_amount = latest_spike['amount']
                spike_multiple = spike_amount / mean if mean > 0 else 0
                
                if spike_multiple > self.SPENDING_SPIKE_THRESHOLD:
                    insights.append(BehaviorInsight(
                        insight_type='spending_spike',
                        title=f'Unusual {category} spending detected',
                        description=f'Spent ${spike_amount:.2f} on {category}, {spike_multiple:.1f}x your typical amount.',
                        metric_value=spike_amount,
                        metric_unit='USD',
                        confidence=0.8,
                        recommendation='This may be a one-time purchase. Monitor for patterns.',
                        time_period='recent',
                    ))
        
        return insights
    
    def _detect_budget_constraints(
        self,
        df: pd.DataFrame,
        monthly_income: float,
    ) -> List[BehaviorInsight]:
        """Detect signs of budget constraints."""
        insights = []
        
        if monthly_income <= 0:
            return insights
        
        df = df.copy()
        df['year_month'] = df['transaction_date'].dt.to_period('M')
        
        # Monthly totals
        monthly_totals = df.groupby('year_month')['amount'].sum()
        
        # Calculate spending as % of income
        spending_ratios = monthly_totals / monthly_income
        
        # Check for consistently high spending
        high_spending_months = (spending_ratios > self.BUDGET_CONSTRAINT_THRESHOLD).sum()
        total_months = len(spending_ratios)
        
        if total_months > 0:
            high_spending_ratio = high_spending_months / total_months
            
            if high_spending_ratio > 0.5:  # More than 50% of months
                insights.append(BehaviorInsight(
                    insight_type='budget_constraint',
                    title='Consistently high spending relative to income',
                    description=f'In {high_spending_months}/{total_months} months, spending exceeded {self.BUDGET_CONSTRAINT_THRESHOLD*100:.0f}% of income.',
                    metric_value=high_spending_ratio * 100,
                    metric_unit='%',
                    confidence=0.75,
                    recommendation='Consider increasing income or reducing discretionary spending.',
                    time_period='recent_trend',
                ))
        
        return insights
    
    def _detect_category_shifts(self, df: pd.DataFrame) -> List[BehaviorInsight]:
        """Detect shifts in spending between categories."""
        insights = []
        
        if len(df) < 60:  # Need at least 2 months
            return insights
        
        df = df.copy()
        df['year_month'] = df['transaction_date'].dt.to_period('M')
        
        # Monthly category totals
        category_monthly = df.groupby(['year_month', 'category'])['amount'].sum()
        
        # For each category, check for significant changes
        categories = df['category'].unique()
        
        for category in categories:
            if category not in category_monthly.index.get_level_values(1):
                continue
            
            cat_data = category_monthly[category]
            
            if len(cat_data) < 2:
                continue
            
            # Compare first and last periods
            first_avg = cat_data.iloc[:len(cat_data)//2].mean()
            last_avg = cat_data.iloc[len(cat_data)//2:].mean()
            
            if first_avg == 0:
                continue
            
            change = (last_avg - first_avg) / first_avg
            
            if abs(change) > 0.25:  # 25% significant shift
                direction = 'increased' if change > 0 else 'decreased'
                insights.append(BehaviorInsight(
                    insight_type='category_shift',
                    title=f'{category.capitalize()} spending {direction}',
                    description=f'{category.capitalize()} spending has {direction} by {abs(change)*100:.1f}%.',
                    metric_value=abs(change) * 100,
                    metric_unit='%',
                    confidence=0.65,
                    recommendation=f'Review your {category} spending pattern to ensure it aligns with your goals.',
                    time_period='over_time',
                ))
        
        return insights
    
    def _detect_spending_patterns(self, df: pd.DataFrame) -> List[BehaviorInsight]:
        """Detect discretionary vs essential spending patterns."""
        insights = []
        
        df = df.copy()
        
        # Categorize spending
        df['spending_type'] = df['category'].apply(
            lambda x: 'essential' if x in self.ESSENTIAL_CATEGORIES else 'discretionary'
        )
        
        # Calculate ratios
        essential = df[df['spending_type'] == 'essential']['amount'].sum()
        discretionary = df[df['spending_type'] == 'discretionary']['amount'].sum()
        total = essential + discretionary
        
        if total == 0:
            return insights
        
        essential_ratio = essential / total
        discretionary_ratio = discretionary / total
        
        if essential_ratio < 0.5:
            insights.append(BehaviorInsight(
                insight_type='high_discretionary_ratio',
                title='High discretionary spending ratio',
                description=f'Only {essential_ratio*100:.1f}% of spending is on essentials. {discretionary_ratio*100:.1f}% is discretionary.',
                metric_value=discretionary_ratio * 100,
                metric_unit='%',
                confidence=0.8,
                recommendation='Consider reducing discretionary spending to improve financial health.',
                time_period='overall',
            ))
        elif essential_ratio > 0.8:
            insights.append(BehaviorInsight(
                insight_type='high_essential_ratio',
                title='Essential-focused spending',
                description=f'{essential_ratio*100:.1f}% of spending is on essentials. This is financially conservative.',
                metric_value=essential_ratio * 100,
                metric_unit='%',
                confidence=0.8,
                recommendation='You have a healthy balance. Small discretionary spending is fine.',
                time_period='overall',
            ))
        
        return insights
    
    def cluster_spending_behavior(
        self,
        transactions: List[Dict],
    ) -> Dict[str, any]:
        """
        Cluster spending into behavioral types.
        
        Returns dict with behavior clusters and characteristics.
        """
        if not transactions:
            return {'clusters': {}}
        
        df = self._prepare_dataframe(transactions)
        
        if df.empty:
            return {'clusters': {}}
        
        # Analyze by transaction size
        amounts = df['amount'].values
        median = statistics.median(amounts)
        
        clusters = {
            'micro_transactions': df[df['amount'] < median * 0.25],
            'small_transactions': df[(df['amount'] >= median * 0.25) & (df['amount'] < median * 0.75)],
            'medium_transactions': df[(df['amount'] >= median * 0.75) & (df['amount'] < median * 1.5)],
            'large_transactions': df[df['amount'] >= median * 1.5],
        }
        
        return {
            'clusters': {
                cluster_name: {
                    'count': len(cluster_df),
                    'total_amount': round(float(cluster_df['amount'].sum()), 2),
                    'average_amount': round(float(cluster_df['amount'].mean()), 2),
                    'percentage_of_total': round(
                        cluster_df['amount'].sum() / df['amount'].sum() * 100, 2
                    ),
                    'typical_categories': list(cluster_df['category'].value_counts().head(3).index),
                }
                for cluster_name, cluster_df in clusters.items()
                if not cluster_df.empty
            },
            'median_transaction': round(median, 2),
            'total_transactions': len(df),
        }
