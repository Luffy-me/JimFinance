"""
Merchant Intelligence System - Merchant analysis, categorization, and profiling.

Analyzes spending patterns by merchant, price trends, and loyalty programs.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter, defaultdict
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)


@dataclass
class MerchantProfile:
    """Complete merchant analysis profile."""
    merchant_name: str
    category: str
    transaction_count: int
    total_spent: float
    average_transaction: float
    min_transaction: float
    max_transaction: float
    first_transaction_date: datetime
    last_transaction_date: datetime
    frequency_days: float  # Average days between visits
    price_trend: float  # % change in average price
    price_volatility: float  # Std dev of prices
    is_likely_subscription: bool
    is_loyalty_program: bool
    merchant_risk_score: float  # 0-100, lower is better
    confidence_score: float
    tags: List[str]


class MerchantIntelligenceSystem:
    """Analyzes merchant spending patterns and characteristics."""
    
    # Common subscription merchants and keywords
    SUBSCRIPTION_KEYWORDS = {
        'netflix', 'spotify', 'apple', 'amazon prime', 'hulu', 'disney',
        'subscription', 'monthly', 'recurring', 'membership', 'gym',
        'premium', 'patreon', 'adobe', 'microsoft', 'github', 'slack',
        'dropbox', 'figma', 'notion', 'lastpass', 'vpn', 'cloudflare',
    }
    
    # Loyalty program keywords
    LOYALTY_KEYWORDS = {
        'starbucks', 'costco', 'trader joes', 'whole foods', 'amazon',
        'walmart', 'target', 'rewards', 'frequent buyer', 'loyalty',
        'members only', 'club',
    }
    
    # High-risk merchant indicators
    HIGH_RISK_KEYWORDS = {
        'casino', 'gambling', 'poker', 'slots', 'betting',
        'payday loan', 'check cashing', 'liquor', 'tobacco',
    }
    
    def __init__(self):
        """Initialize merchant intelligence system."""
        self.logger = logger
    
    def profile_merchants(
        self,
        transactions: List[Dict],
    ) -> Dict[str, MerchantProfile]:
        """
        Profile all merchants from transaction history.
        
        Args:
            transactions: List of transaction dicts with merchant, amount, date, category
        
        Returns:
            Dictionary of merchant_name -> MerchantProfile
        """
        if not transactions:
            return {}
        
        # Group transactions by merchant
        merchants = self._group_by_merchant(transactions)
        profiles = {}
        
        for merchant_name, merchant_txns in merchants.items():
            if merchant_txns:
                profiles[merchant_name] = self._profile_single_merchant(merchant_name, merchant_txns)
        
        return profiles
    
    def _group_by_merchant(self, transactions: List[Dict]) -> Dict[str, List[Dict]]:
        """Group transactions by merchant (normalized name)."""
        merchants = defaultdict(list)
        
        for txn in transactions:
            merchant = txn.get('merchant', 'Unknown')
            if merchant and merchant.strip():
                merchant_norm = self._normalize_merchant_name(merchant)
                merchants[merchant_norm].append(txn)
        
        return merchants
    
    def _normalize_merchant_name(self, name: str) -> str:
        """Normalize merchant name for grouping."""
        name = name.lower().strip()
        # Remove common suffixes
        for suffix in [' llc', ' inc', ' ltd', ' corp', ' co', '.com', '.net']:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()
        return name
    
    def _profile_single_merchant(
        self,
        merchant_name: str,
        transactions: List[Dict],
    ) -> MerchantProfile:
        """Profile a single merchant."""
        if not transactions:
            return self._empty_profile(merchant_name)
        
        # Extract amounts and dates
        amounts = []
        dates = []
        categories = []
        
        for txn in transactions:
            try:
                amount = float(txn.get('amount', 0))
                if amount > 0:
                    amounts.append(amount)
                    dates.append(txn.get('transaction_date', txn.get('date')))
                    categories.append(txn.get('category', 'other'))
            except (ValueError, TypeError):
                continue
        
        if not amounts or not dates:
            return self._empty_profile(merchant_name)
        
        # Convert dates to datetime
        dates = [self._to_datetime(d) for d in dates]
        dates = [d for d in dates if d is not None]
        
        if not dates:
            dates = [datetime.now()]
        
        dates.sort()
        
        # Calculate metrics
        total_spent = sum(amounts)
        avg_transaction = total_spent / len(amounts)
        min_transaction = min(amounts)
        max_transaction = max(amounts)
        first_date = dates[0]
        last_date = dates[-1]
        
        # Frequency analysis
        frequency_days = self._calculate_frequency(dates)
        
        # Price trend analysis
        price_trend = self._calculate_price_trend(amounts)
        
        # Volatility
        price_volatility = self._calculate_volatility(amounts)
        
        # Subscription detection
        is_subscription = self._detect_subscription(amounts, merchant_name, frequency_days)
        
        # Loyalty program detection
        is_loyalty = self._detect_loyalty_program(merchant_name, amounts)
        
        # Risk score
        risk_score = self._calculate_risk_score(merchant_name, amounts, avg_transaction)
        
        # Confidence score
        confidence = self._calculate_confidence(len(transactions))
        
        # Generate tags
        tags = self._generate_tags(merchant_name, amounts, frequency_days, is_subscription)
        
        # Determine primary category
        primary_category = self._determine_category(categories, merchant_name)
        
        return MerchantProfile(
            merchant_name=merchant_name,
            category=primary_category,
            transaction_count=len(transactions),
            total_spent=round(total_spent, 2),
            average_transaction=round(avg_transaction, 2),
            min_transaction=round(min_transaction, 2),
            max_transaction=round(max_transaction, 2),
            first_transaction_date=first_date,
            last_transaction_date=last_date,
            frequency_days=round(frequency_days, 1),
            price_trend=round(price_trend, 2),
            price_volatility=round(price_volatility, 2),
            is_likely_subscription=is_subscription,
            is_loyalty_program=is_loyalty,
            merchant_risk_score=round(risk_score, 1),
            confidence_score=round(confidence, 2),
            tags=tags,
        )
    
    def _calculate_frequency(self, dates: List[datetime]) -> float:
        """Calculate average days between transactions."""
        if len(dates) < 2:
            return 0.0
        
        dates = sorted(dates)
        intervals = []
        
        for i in range(1, len(dates)):
            interval = (dates[i] - dates[i-1]).days
            if interval > 0:  # Exclude same-day transactions
                intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        return statistics.mean(intervals)
    
    def _calculate_price_trend(self, amounts: List[float]) -> float:
        """
        Calculate price trend as % change.
        
        Positive = prices increasing, Negative = prices decreasing
        """
        if len(amounts) < 2:
            return 0.0
        
        # Compare first half average to second half average
        mid = len(amounts) // 2
        first_half_avg = sum(amounts[:mid]) / len(amounts[:mid])
        second_half_avg = sum(amounts[mid:]) / len(amounts[mid:])
        
        if first_half_avg == 0:
            return 0.0
        
        trend = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        return trend
    
    def _calculate_volatility(self, amounts: List[float]) -> float:
        """Calculate price volatility (standard deviation)."""
        if len(amounts) < 2:
            return 0.0
        
        try:
            return statistics.stdev(amounts)
        except statistics.StatisticsError:
            return 0.0
    
    def _detect_subscription(
        self,
        amounts: List[float],
        merchant_name: str,
        frequency_days: float,
    ) -> bool:
        """
        Detect if merchant is likely a subscription.
        
        Indicators:
        - Merchant name contains subscription keywords
        - Regular frequency (10-35 days)
        - Consistent amounts (low volatility)
        """
        merchant_lower = merchant_name.lower()
        
        # Keyword match
        if any(keyword in merchant_lower for keyword in self.SUBSCRIPTION_KEYWORDS):
            return True
        
        # Frequency pattern (monthly-ish = 25-35 days, weekly = 5-10 days)
        if not (5 <= frequency_days <= 35):
            return False
        
        # Consistency check
        if len(amounts) >= 3:
            avg = sum(amounts) / len(amounts)
            if avg > 0:
                coefficient_of_variation = (self._calculate_volatility(amounts) / avg)
                # Low volatility = subscription-like
                if coefficient_of_variation < 0.15:
                    return True
        
        return False
    
    def _detect_loyalty_program(
        self,
        merchant_name: str,
        amounts: List[float],
    ) -> bool:
        """Detect if merchant has loyalty program."""
        merchant_lower = merchant_name.lower()
        
        # Keyword match
        if any(keyword in merchant_lower for keyword in self.LOYALTY_KEYWORDS):
            return True
        
        return False
    
    def _calculate_risk_score(
        self,
        merchant_name: str,
        amounts: List[float],
        avg_amount: float,
    ) -> float:
        """
        Calculate merchant risk score (0-100, lower is better).
        
        Risk factors:
        - High-risk category keywords (40 points)
        - Very high individual transactions (20 points)
        - High price volatility (15 points)
        - Unusual patterns (25 points)
        """
        risk_score = 0.0
        
        merchant_lower = merchant_name.lower()
        
        # High-risk category
        if any(keyword in merchant_lower for keyword in self.HIGH_RISK_KEYWORDS):
            risk_score += 40
        
        # Transaction amount risk
        if avg_amount > 500:
            risk_score += 20
        elif avg_amount > 200:
            risk_score += 10
        
        # Volatility risk
        if len(amounts) >= 2:
            volatility = self._calculate_volatility(amounts)
            avg = sum(amounts) / len(amounts)
            if avg > 0:
                cv = volatility / avg
                if cv > 1.5:
                    risk_score += 15
        
        # Unusual patterns
        if len(amounts) > 1:
            max_amount = max(amounts)
            min_amount = min(amounts)
            if min_amount > 0:
                ratio = max_amount / min_amount
                if ratio > 5:
                    risk_score += 10
        
        return min(100.0, risk_score)
    
    def _calculate_confidence(self, transaction_count: int) -> float:
        """Calculate confidence score for merchant profile."""
        # More transactions = higher confidence
        if transaction_count >= 10:
            return 1.0
        elif transaction_count >= 5:
            return 0.8
        elif transaction_count >= 3:
            return 0.6
        else:
            return 0.4
    
    def _generate_tags(
        self,
        merchant_name: str,
        amounts: List[float],
        frequency_days: float,
        is_subscription: bool,
    ) -> List[str]:
        """Generate descriptive tags for merchant."""
        tags = []
        
        if is_subscription:
            tags.append('subscription')
        
        if frequency_days > 0:
            if 5 <= frequency_days <= 10:
                tags.append('weekly')
            elif 20 <= frequency_days <= 35:
                tags.append('monthly')
            elif frequency_days > 35:
                tags.append('occasional')
        
        if len(amounts) > 0:
            avg = sum(amounts) / len(amounts)
            if avg > 500:
                tags.append('high-value')
            elif avg < 20:
                tags.append('low-value')
        
        if self._calculate_volatility(amounts) > 50:
            tags.append('variable-pricing')
        
        return tags
    
    def _determine_category(self, categories: List[str], merchant_name: str) -> str:
        """Determine primary category for merchant."""
        if not categories:
            return 'other'
        
        # Use most common category
        counter = Counter(categories)
        most_common = counter.most_common(1)[0][0]
        
        return most_common.lower() if most_common else 'other'
    
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
    
    def _empty_profile(self, merchant_name: str) -> MerchantProfile:
        """Return empty profile for merchant."""
        return MerchantProfile(
            merchant_name=merchant_name,
            category='other',
            transaction_count=0,
            total_spent=0.0,
            average_transaction=0.0,
            min_transaction=0.0,
            max_transaction=0.0,
            first_transaction_date=datetime.now(),
            last_transaction_date=datetime.now(),
            frequency_days=0.0,
            price_trend=0.0,
            price_volatility=0.0,
            is_likely_subscription=False,
            is_loyalty_program=False,
            merchant_risk_score=0.0,
            confidence_score=0.0,
            tags=[],
        )
    
    def analyze_spending_by_merchant(
        self,
        transactions: List[Dict],
        top_n: int = 10,
    ) -> Dict[str, any]:
        """
        Analyze top spending merchants.
        
        Args:
            transactions: List of transactions
            top_n: Number of top merchants to return
        
        Returns:
            Analysis dict with top merchants and insights
        """
        profiles = self.profile_merchants(transactions)
        
        # Sort by total spent
        sorted_merchants = sorted(
            profiles.items(),
            key=lambda x: x[1].total_spent,
            reverse=True
        )
        
        top_merchants = sorted_merchants[:top_n]
        
        total_merchant_spending = sum(p.total_spent for p in profiles.values())
        
        return {
            'total_unique_merchants': len(profiles),
            'total_merchant_spending': round(total_merchant_spending, 2),
            'top_merchants': [
                {
                    'merchant': p.merchant_name,
                    'category': p.category,
                    'total_spent': p.total_spent,
                    'average_transaction': p.average_transaction,
                    'transaction_count': p.transaction_count,
                    'is_subscription': p.is_likely_subscription,
                    'risk_score': p.merchant_risk_score,
                    'tags': p.tags,
                }
                for _, p in top_merchants
            ],
            'subscription_count': sum(1 for p in profiles.values() if p.is_likely_subscription),
            'high_risk_count': sum(1 for p in profiles.values() if p.merchant_risk_score > 50),
        }
