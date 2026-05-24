"""
Merchant matching and recognition using fuzzy logic.
"""

import logging
from typing import Optional, List, Tuple
from difflib import SequenceMatcher
from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


# Common merchant aliases and patterns
MERCHANT_ALIASES = {
    "starbucks": ["sbux", "starb", "starbuck"],
    "mcdonald's": ["mcdonalds", "mcd", "mcp", "mcdonalds's"],
    "uber": ["uber eats", "uber trip"],
    "yandex": ["яндекс", "yandex.taxi", "yandex taxi"],
    "sber": ["sberbank", "сбербанк"],
    "gazprombank": ["gazprom", "gpb"],
    "alfa bank": ["alfabank", "alfa-bank"],
    "raiffeisenbank": ["raiffeisen"],
    "ozon": ["ozon.ru"],
    "wildberries": ["wb"],
    "aliexpress": ["ali"],
    "amazon": ["amz", "amzn"],
    "airbnb": ["airb"],
    "booking": ["booking.com"],
    "netflix": ["nflx"],
    "spotify": ["spotify premium"],
    "gym": ["fitness", "спортзал"],
}

# Common merchant categories for pattern matching
CATEGORY_PATTERNS = {
    "food": [
        r"(pizza|cafe|restaurant|burger|sushi|shawarma|kebab|food|grocery|supermarket|"
        r"мак|пятер|пиццерия|кафе|ресторан|доставка|еда)",
    ],
    "transport": [
        r"(taxi|uber|uber eats|яндекс.такси|газелька|metro|метро|"
        r"автобус|трамвай|ж/д|железная дорога)",
    ],
    "entertainment": [
        r"(cinema|кино|театр|concert|кинотеатр|netflix|spotify|discord|youtube|"
        r"gaming|игр|развлечени)",
    ],
    "shopping": [
        r"(mall|shop|store|магазин|торговый|склад|amazon|aliexpress|"
        r"ozon|wildberries|market|маркет)",
    ],
    "utilities": [
        r"(электро|вода|газ|интернет|телефон|услуга|коммунальные|ЖКХ|"
        r"power|water|internet|phone|utilities)",
    ],
    "healthcare": [
        r"(аптека|pharmacy|doctor|врач|больница|hospital|медицина|"
        r"clinic|клиника|med)",
    ],
    "subscriptions": [
        r"(subscription|подписка|premium|plus|pro|monthly|ежемесячно|"
        r"auto-renewal|автоматич)",
    ],
}


class MerchantMatcher:
    """Match and recognize merchants using fuzzy logic."""
    
    def __init__(self, known_merchants: List[str] = None):
        """
        Initialize matcher with known merchants.
        
        Args:
            known_merchants: List of known merchant names to match against
        """
        self.known_merchants = set(m.lower() for m in (known_merchants or []))
        self.merchant_cache = {}
    
    def find_best_match(
        self, merchant: str, threshold: float = 0.6
    ) -> Tuple[Optional[str], float]:
        """
        Find best matching merchant from known merchants.
        
        Args:
            merchant: Merchant name to match
            threshold: Similarity threshold (0-1)
        
        Returns:
            Tuple of (best_match, confidence_score)
        """
        if not merchant or not self.known_merchants:
            return None, 0.0
        
        merchant_lower = merchant.lower().strip()
        
        # Check cache first
        if merchant_lower in self.merchant_cache:
            return self.merchant_cache[merchant_lower]
        
        best_match = None
        best_score = 0.0
        
        for known in self.known_merchants:
            # Calculate similarity
            score = self._calculate_similarity(merchant_lower, known)
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = known
        
        result = (best_match, best_score)
        self.merchant_cache[merchant_lower] = result
        
        return result
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings (0-1)."""
        # Sequence matcher ratio
        ratio = SequenceMatcher(None, text1, text2).ratio()
        
        # Check for exact substring matches (higher weight)
        if text1 in text2 or text2 in text1:
            ratio = max(ratio, 0.8)
        
        return ratio
    
    def add_merchant(self, merchant: str) -> None:
        """Add new merchant to known merchants."""
        if merchant:
            self.known_merchants.add(merchant.lower().strip())
            self.merchant_cache.clear()
    
    def add_merchants(self, merchants: List[str]) -> None:
        """Add multiple merchants."""
        for merchant in merchants:
            self.add_merchant(merchant)


class RecurringDetector:
    """Detect recurring/subscription transactions."""
    
    @staticmethod
    def detect_recurring(
        transactions: List[dict],
        merchant: str = None,
        min_occurrences: int = 2,
    ) -> Tuple[bool, str, dict]:
        """
        Detect if transactions form a recurring pattern.
        
        Args:
            transactions: List of transaction dicts with 'amount', 'date'
            merchant: Optional merchant to filter by
            min_occurrences: Minimum occurrences to consider recurring
        
        Returns:
            Tuple of (is_recurring, pattern, metadata)
        """
        if len(transactions) < min_occurrences:
            return False, "insufficient_data", {}
        
        # Filter by merchant if specified
        if merchant:
            transactions = [
                t for t in transactions
                if t.get("merchant", "").lower() == merchant.lower()
            ]
        
        if len(transactions) < min_occurrences:
            return False, "insufficient_data_merchant", {}
        
        # Sort by date
        sorted_txns = sorted(transactions, key=lambda t: t.get("date", datetime.now()))
        
        # Check for same amount and pattern
        amount = sorted_txns[0].get("amount")
        if not all(t.get("amount") == amount for t in sorted_txns):
            return False, "varying_amounts", {}
        
        # Calculate intervals between transactions
        intervals = []
        for i in range(1, len(sorted_txns)):
            date1 = sorted_txns[i - 1].get("date", datetime.now())
            date2 = sorted_txns[i].get("date", datetime.now())
            
            if isinstance(date1, str):
                date1 = datetime.fromisoformat(date1)
            if isinstance(date2, str):
                date2 = datetime.fromisoformat(date2)
            
            interval_days = (date2 - date1).days
            intervals.append(interval_days)
        
        if not intervals:
            return False, "no_intervals", {}
        
        # Detect pattern from intervals
        avg_interval = sum(intervals) / len(intervals)
        pattern, is_recurring = RecurringDetector._classify_pattern(
            intervals, avg_interval
        )
        
        metadata = {
            "average_interval": avg_interval,
            "intervals": intervals,
            "amount": float(amount) if amount else None,
            "occurrences": len(sorted_txns),
            "confidence": RecurringDetector._calculate_confidence(intervals),
        }
        
        return is_recurring, pattern, metadata
    
    @staticmethod
    def _classify_pattern(intervals: List[int], avg_interval: float) -> Tuple[str, bool]:
        """Classify recurring pattern from intervals."""
        # Allow 20% variance
        variance_threshold = 0.2
        
        patterns = [
            (7, "weekly", 3),
            (14, "biweekly", 5),
            (30, "monthly", 5),
            (365, "yearly", 30),
        ]
        
        for expected_interval, pattern_name, variance in patterns:
            if abs(avg_interval - expected_interval) <= variance:
                return pattern_name, True
        
        # If intervals are consistent but don't match known patterns
        std_dev = (sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)) ** 0.5
        if std_dev < avg_interval * variance_threshold:
            return f"every_{int(round(avg_interval))}_days", True
        
        return "irregular", False
    
    @staticmethod
    def _calculate_confidence(intervals: List[int]) -> float:
        """Calculate confidence in recurring pattern (0-1)."""
        if len(intervals) < 2:
            return 0.0
        
        avg = sum(intervals) / len(intervals)
        variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
        std_dev = variance ** 0.5
        
        # Lower coefficient of variation = higher confidence
        cv = std_dev / avg if avg > 0 else 0
        
        # Convert to confidence: high cv = low confidence
        confidence = max(0.0, 1.0 - cv)
        
        # Also consider number of occurrences
        occurrence_bonus = min(0.3, len(intervals) * 0.1)
        
        return min(1.0, confidence + occurrence_bonus)


class AnomalyDetector:
    """Detect anomalous transactions."""
    
    @staticmethod
    def detect_anomaly(
        transaction: dict,
        historical_transactions: List[dict] = None,
    ) -> Tuple[bool, float]:
        """
        Detect if transaction is anomalous.
        
        Args:
            transaction: Transaction dict with 'amount', 'merchant', 'category'
            historical_transactions: List of historical transaction dicts
        
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if not historical_transactions or len(historical_transactions) < 10:
            return False, 0.0
        
        amount = float(transaction.get("amount", 0))
        merchant = transaction.get("merchant", "").lower()
        category = transaction.get("category", "").lower()
        
        # Filter historical by merchant if available
        if merchant:
            similar_txns = [
                t for t in historical_transactions
                if t.get("merchant", "").lower() == merchant
            ]
        else:
            similar_txns = historical_transactions
        
        if not similar_txns:
            return False, 0.0
        
        # Calculate statistics
        amounts = [float(t.get("amount", 0)) for t in similar_txns]
        avg_amount = sum(amounts) / len(amounts)
        variance = sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)
        std_dev = variance ** 0.5
        
        # Z-score for amount
        z_score = abs((amount - avg_amount) / std_dev) if std_dev > 0 else 0
        
        # Anomaly if z-score > 3 (typical threshold)
        is_anomaly = z_score > 3
        anomaly_score = min(1.0, z_score / 5.0)  # Normalize to 0-1
        
        return is_anomaly, anomaly_score


class DuplicateDetector:
    """Detect duplicate transactions."""
    
    @staticmethod
    def is_duplicate(
        transaction: dict,
        recent_transactions: List[dict],
        time_window_minutes: int = 60,
        amount_threshold: float = 0.01,  # 1% variance
    ) -> Tuple[bool, Optional[int]]:
        """
        Detect if transaction is a duplicate of recent transactions.
        
        Args:
            transaction: Transaction dict
            recent_transactions: List of recent transaction dicts
            time_window_minutes: Time window to check duplicates
            amount_threshold: Allowed variance in amount
        
        Returns:
            Tuple of (is_duplicate, duplicate_transaction_id)
        """
        amount = float(transaction.get("amount", 0))
        txn_date = transaction.get("date", datetime.now())
        merchant = transaction.get("merchant", "").lower()
        
        if isinstance(txn_date, str):
            txn_date = datetime.fromisoformat(txn_date)
        
        for recent_txn in recent_transactions:
            recent_amount = float(recent_txn.get("amount", 0))
            recent_date = recent_txn.get("date", datetime.now())
            recent_merchant = recent_txn.get("merchant", "").lower()
            
            if isinstance(recent_date, str):
                recent_date = datetime.fromisoformat(recent_date)
            
            # Check time window
            time_diff = abs((txn_date - recent_date).total_seconds() / 60)
            if time_diff > time_window_minutes:
                continue
            
            # Check amount (within threshold)
            amount_diff = abs(amount - recent_amount) / amount if amount > 0 else 0
            if amount_diff > amount_threshold:
                continue
            
            # Check merchant
            if merchant and recent_merchant and merchant != recent_merchant:
                continue
            
            # This is likely a duplicate
            return True, recent_txn.get("id")
        
        return False, None
