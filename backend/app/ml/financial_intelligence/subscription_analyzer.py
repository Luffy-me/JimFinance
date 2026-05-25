"""
Subscription Analysis Engine - Recurring payment pattern detection and optimization.

Identifies subscriptions, analyzes trends, and detects churn risk.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class SubscriptionProfile:
    """Complete subscription analysis profile."""
    name: str
    merchant: str
    category: str
    amount: float
    currency: str
    billing_cycle: str  # daily, weekly, monthly, quarterly, yearly
    estimated_yearly_cost: float
    first_occurrence: datetime
    last_occurrence: datetime
    occurrence_count: int
    confidence_score: float
    is_active: bool
    churn_risk: float  # 0-1, probability of cancellation
    price_trend: float  # % change
    cost_effectiveness_score: float  # 0-100
    optimization_opportunities: List[str]
    tags: List[str]


class SubscriptionAnalyzer:
    """Analyzes subscription and recurring payment patterns."""
    
    # Common subscription billing cycles (days)
    BILLING_CYCLES = {
        'daily': 1,
        'weekly': 7,
        'bi-weekly': 14,
        'monthly': 30,
        'quarterly': 91,
        'semi-annual': 182,
        'yearly': 365,
    }
    
    # Subscription keywords
    SUBSCRIPTION_PATTERNS = [
        'subscription', 'premium', 'monthly', 'yearly', 'annual', 'membership',
        'recurring', 'auto-renew', 'billing date', 'cycle',
    ]
    
    # Free/low-cost subscription budget threshold
    LOW_COST_THRESHOLD = 5.0
    
    def __init__(self):
        """Initialize subscription analyzer."""
        self.logger = logger
    
    def detect_subscriptions(
        self,
        transactions: List[Dict],
    ) -> List[SubscriptionProfile]:
        """
        Detect recurring subscription patterns from transactions.
        
        Args:
            transactions: List of transaction dicts
        
        Returns:
            List of SubscriptionProfile objects
        """
        if not transactions:
            return []
        
        # Group by merchant
        merchant_groups = self._group_by_merchant(transactions)
        
        subscriptions = []
        for merchant, merchant_txns in merchant_groups.items():
            subscription = self._analyze_merchant_for_subscriptions(merchant, merchant_txns)
            if subscription:
                subscriptions.append(subscription)
        
        return subscriptions
    
    def _group_by_merchant(self, transactions: List[Dict]) -> Dict[str, List[Dict]]:
        """Group transactions by merchant."""
        groups = defaultdict(list)
        
        for txn in transactions:
            merchant = txn.get('merchant', 'Unknown')
            if merchant:
                merchant = merchant.lower().strip()
                groups[merchant].append(txn)
        
        return groups
    
    def _analyze_merchant_for_subscriptions(
        self,
        merchant: str,
        transactions: List[Dict],
    ) -> Optional[SubscriptionProfile]:
        """
        Analyze merchant transactions for subscription pattern.
        
        Subscription indicators:
        - Regular frequency (consistent interval)
        - Consistent amounts
        - Frequent occurrence (at least 3 times)
        """
        if len(transactions) < 3:
            return None
        
        # Extract dates and amounts
        dates = []
        amounts = []
        categories = []
        
        for txn in transactions:
            try:
                date = self._to_datetime(txn.get('transaction_date', txn.get('date')))
                if date:
                    dates.append(date)
                    amounts.append(float(txn.get('amount', 0)))
                    categories.append(txn.get('category', 'other'))
            except (ValueError, TypeError):
                continue
        
        if len(dates) < 3 or not amounts:
            return None
        
        # Sort by date
        sorted_pairs = sorted(zip(dates, amounts))
        dates = [d for d, _ in sorted_pairs]
        amounts = [a for _, a in sorted_pairs]
        
        # Detect pattern
        billing_cycle, confidence = self._detect_billing_cycle(dates)
        
        if confidence < 0.5 or billing_cycle is None:
            return None  # Not a clear subscription pattern
        
        # Check for consistent amounts
        avg_amount = sum(amounts) / len(amounts)
        if avg_amount == 0:
            return None
        
        amount_consistency = self._calculate_consistency(amounts)
        if amount_consistency < 0.6:
            return None  # Amounts too inconsistent
        
        # This looks like a subscription
        is_active = self._is_active(dates)
        yearly_cost = avg_amount * (365 / self.BILLING_CYCLES.get(billing_cycle, 30))
        
        churn_risk = self._calculate_churn_risk(dates, is_active)
        price_trend = self._calculate_price_trend(amounts)
        cost_effectiveness = self._calculate_cost_effectiveness(
            yearly_cost, merchant, avg_amount
        )
        
        optimization_ops = self._identify_optimization_opportunities(
            merchant, yearly_cost, avg_amount
        )
        
        tags = self._generate_tags(merchant, billing_cycle, yearly_cost)
        
        primary_category = self._determine_primary_category(categories)
        
        return SubscriptionProfile(
            name=self._generate_subscription_name(merchant, billing_cycle),
            merchant=merchant,
            category=primary_category,
            amount=round(avg_amount, 2),
            currency='USD',
            billing_cycle=billing_cycle,
            estimated_yearly_cost=round(yearly_cost, 2),
            first_occurrence=dates[0],
            last_occurrence=dates[-1],
            occurrence_count=len(dates),
            confidence_score=round(confidence, 2),
            is_active=is_active,
            churn_risk=round(churn_risk, 2),
            price_trend=round(price_trend, 2),
            cost_effectiveness_score=round(cost_effectiveness, 1),
            optimization_opportunities=optimization_ops,
            tags=tags,
        )
    
    def _detect_billing_cycle(
        self,
        dates: List[datetime],
    ) -> Tuple[Optional[str], float]:
        """
        Detect billing cycle from transaction dates.
        
        Returns:
            (billing_cycle_name, confidence_score)
        """
        if len(dates) < 2:
            return None, 0.0
        
        dates = sorted(dates)
        intervals = []
        
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i-1]).days
            if interval > 0:
                intervals.append(interval)
        
        if not intervals:
            return None, 0.0
        
        # Calculate mean and standard deviation
        mean_interval = statistics.mean(intervals)
        
        if len(intervals) >= 2:
            try:
                std_dev = statistics.stdev(intervals)
                coefficient_of_variation = std_dev / mean_interval if mean_interval > 0 else 0
            except statistics.StatisticsError:
                coefficient_of_variation = 0.0
        else:
            coefficient_of_variation = 0.0
        
        # Match to known cycles
        best_match = None
        best_confidence = 0.0
        
        for cycle_name, cycle_days in self.BILLING_CYCLES.items():
            # Allow 15% tolerance
            tolerance = cycle_days * 0.15
            
            if abs(mean_interval - cycle_days) <= tolerance:
                # Consistency check
                if coefficient_of_variation <= 0.2:  # Low variation
                    confidence = 1.0 - (abs(mean_interval - cycle_days) / cycle_days) - (coefficient_of_variation * 0.2)
                else:
                    confidence = max(0.4, 1.0 - (coefficient_of_variation * 0.5))
                
                # Higher confidence for cycles we see multiple times
                confidence *= (min(len(dates), 12) / 12)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = cycle_name
        
        return best_match, best_confidence
    
    def _calculate_consistency(self, amounts: List[float]) -> float:
        """
        Calculate consistency of transaction amounts (0-1).
        
        Lower variance = higher consistency = higher score.
        """
        if len(amounts) < 2 or not amounts:
            return 0.0
        
        avg = sum(amounts) / len(amounts)
        if avg == 0:
            return 0.0
        
        try:
            variance = statistics.variance(amounts)
            std_dev = variance ** 0.5
            coefficient_of_variation = std_dev / avg
            
            # Convert to 0-1 score (lower CV = higher score)
            # CV of 0-0.05 = 1.0 score
            # CV of 0.05-0.15 = 0.7-1.0 score
            # CV of 0.15-0.5 = 0.3-0.7 score
            # CV > 0.5 = < 0.3 score
            
            if coefficient_of_variation <= 0.05:
                return 1.0
            elif coefficient_of_variation <= 0.15:
                return 0.7 + (0.3 * (1 - (coefficient_of_variation - 0.05) / 0.1))
            elif coefficient_of_variation <= 0.5:
                return 0.3 + (0.4 * (1 - (coefficient_of_variation - 0.15) / 0.35))
            else:
                return max(0.0, 0.3 - (coefficient_of_variation - 0.5) * 0.3)
        except (statistics.StatisticsError, ZeroDivisionError):
            return 0.0
    
    def _is_active(self, dates: List[datetime]) -> bool:
        """Determine if subscription is currently active."""
        if not dates:
            return False
        
        last_date = max(dates)
        days_since_last = (datetime.now() - last_date).days
        
        # If last occurrence was within 60 days, consider it active
        return days_since_last <= 60
    
    def _calculate_churn_risk(self, dates: List[datetime], is_active: bool) -> float:
        """
        Calculate churn risk (probability of cancellation).
        
        Risk factors:
        - Increasing gaps between payments
        - Inactivity
        - Downward price trend
        """
        if len(dates) < 2:
            return 0.0
        
        dates = sorted(dates)
        
        # Check for increasing gaps
        intervals = []
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i-1]).days
            intervals.append(interval)
        
        # Trend in gaps
        gap_risk = 0.0
        if len(intervals) >= 2:
            trend = intervals[-1] - intervals[0]
            if trend > 10:  # Gaps increasing
                gap_risk = 0.4
            elif trend > 5:
                gap_risk = 0.2
        
        # Inactivity risk
        inactivity_risk = 0.0
        if is_active:
            inactivity_risk = 0.0
        else:
            days_since_last = (datetime.now() - dates[-1]).days
            if days_since_last > 90:
                inactivity_risk = 0.6
            elif days_since_last > 60:
                inactivity_risk = 0.3
        
        # Combine risks
        total_risk = min(1.0, (gap_risk + inactivity_risk) / 2)
        
        return total_risk
    
    def _calculate_price_trend(self, amounts: List[float]) -> float:
        """Calculate price trend as % change."""
        if len(amounts) < 2:
            return 0.0
        
        avg_first_half = sum(amounts[:len(amounts)//2]) / max(1, len(amounts)//2)
        avg_second_half = sum(amounts[len(amounts)//2:]) / max(1, len(amounts) - len(amounts)//2)
        
        if avg_first_half == 0:
            return 0.0
        
        return ((avg_second_half - avg_first_half) / avg_first_half) * 100
    
    def _calculate_cost_effectiveness(
        self,
        yearly_cost: float,
        merchant: str,
        avg_amount: float,
    ) -> float:
        """
        Calculate cost effectiveness score (0-100).
        
        Factors:
        - Cost relative to category (30%)
        - Usage frequency (30%)
        - Price trend (20%)
        - Value perception (20%)
        """
        score = 50.0  # Base score
        
        # Cost analysis (30%)
        if avg_amount < self.LOW_COST_THRESHOLD:
            score += 30
        elif avg_amount < 15:
            score += 20
        elif avg_amount < 50:
            score += 10
        else:
            score -= min((avg_amount - 50) / 10, 20)
        
        # Value perception (20%)
        # Common high-value subscriptions
        high_value_merchants = {
            'netflix', 'spotify', 'adobe', 'microsoft', 'github',
            'aws', 'digital ocean', 'stripe',
        }
        
        if any(m in merchant.lower() for m in high_value_merchants):
            score += 20
        
        return max(0, min(100, score))
    
    def _identify_optimization_opportunities(
        self,
        merchant: str,
        yearly_cost: float,
        monthly_cost: float,
    ) -> List[str]:
        """Identify ways to optimize subscription costs."""
        opportunities = []
        
        # High-cost subscriptions
        if yearly_cost > 200:
            opportunities.append('Consider annual payment for discount')
            opportunities.append('Evaluate if subscription is still needed')
        
        # Duplicate subscriptions
        merchant_lower = merchant.lower()
        
        streaming_services = ['netflix', 'hulu', 'disney', 'amazon prime', 'hbo']
        if any(s in merchant_lower for s in streaming_services):
            opportunities.append('Check for duplicate streaming subscriptions')
        
        music_services = ['spotify', 'apple music', 'amazon music']
        if any(s in merchant_lower for s in music_services):
            opportunities.append('Compare music subscription costs')
        
        # Low-usage subscriptions
        if monthly_cost > 0 and yearly_cost > 50 and yearly_cost < 100:
            opportunities.append('Low-cost subscription - review usage frequency')
        
        return opportunities
    
    def _generate_tags(
        self,
        merchant: str,
        billing_cycle: str,
        yearly_cost: float,
    ) -> List[str]:
        """Generate descriptive tags for subscription."""
        tags = [billing_cycle]
        
        if yearly_cost > 200:
            tags.append('expensive')
        elif yearly_cost < 50:
            tags.append('affordable')
        
        merchant_lower = merchant.lower()
        
        # Category tags
        if any(s in merchant_lower for s in ['netflix', 'hulu', 'disney', 'amazon prime']):
            tags.append('streaming')
        elif any(s in merchant_lower for s in ['spotify', 'apple music', 'amazon music']):
            tags.append('music')
        elif any(s in merchant_lower for s in ['adobe', 'figma', 'sketch']):
            tags.append('design')
        elif any(s in merchant_lower for s in ['github', 'gitlab', 'bitbucket']):
            tags.append('development')
        elif any(s in merchant_lower for s in ['gym', 'fitness', 'peloton']):
            tags.append('fitness')
        
        return tags
    
    def _generate_subscription_name(self, merchant: str, billing_cycle: str) -> str:
        """Generate friendly subscription name."""
        # Capitalize merchant name
        name = merchant.title()
        
        # Add cycle info if not monthly
        if billing_cycle != 'monthly':
            name += f' ({billing_cycle.title()})'
        
        return name
    
    def _determine_primary_category(self, categories: List[str]) -> str:
        """Determine primary category."""
        if not categories:
            return 'subscriptions'
        
        from collections import Counter
        counter = Counter(c.lower() for c in categories)
        most_common = counter.most_common(1)[0][0]
        
        return most_common if most_common else 'subscriptions'
    
    def _to_datetime(self, date_obj) -> Optional[datetime]:
        """Convert various date formats to datetime."""
        if isinstance(date_obj, datetime):
            return date_obj
        elif isinstance(date_obj, str):
            try:
                return datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    return datetime.strptime(date_obj, '%Y-%m-%d')
                except (ValueError, TypeError):
                    return None
        return None
    
    def analyze_subscription_costs(
        self,
        subscriptions: List[SubscriptionProfile],
    ) -> Dict:
        """
        Analyze overall subscription spending.
        
        Returns:
            Summary dict with costs and insights
        """
        if not subscriptions:
            return {
                'total_monthly': 0.0,
                'total_yearly': 0.0,
                'subscription_count': 0,
                'active_count': 0,
                'at_risk_count': 0,
                'optimization_potential': 0.0,
            }
        
        total_monthly = sum(s.amount for s in subscriptions)
        total_yearly = sum(s.estimated_yearly_cost for s in subscriptions)
        active_count = sum(1 for s in subscriptions if s.is_active)
        at_risk_count = sum(1 for s in subscriptions if s.churn_risk > 0.3)
        
        # Optimization potential (sum of opportunities)
        optimization_potential = sum(1 for s in subscriptions if s.optimization_opportunities)
        
        return {
            'total_monthly': round(total_monthly, 2),
            'total_yearly': round(total_yearly, 2),
            'subscription_count': len(subscriptions),
            'active_count': active_count,
            'inactive_count': len(subscriptions) - active_count,
            'at_risk_count': at_risk_count,
            'optimization_opportunities': optimization_potential,
            'subscriptions': [
                {
                    'name': s.name,
                    'amount': s.amount,
                    'yearly_cost': s.estimated_yearly_cost,
                    'is_active': s.is_active,
                    'churn_risk': s.churn_risk,
                    'recommendations': s.optimization_opportunities,
                }
                for s in subscriptions
            ],
        }
