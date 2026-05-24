"""
Transaction Intelligence Engine.

Modules:
- text_processor: Text normalization and parsing
- matchers: Merchant matching, recurring/anomaly detection
- classifier: AI and rule-based classification
"""

from app.ml.transaction_intelligence.text_processor import TextNormalizer, TransactionParser
from app.ml.transaction_intelligence.matchers import (
    MerchantMatcher,
    RecurringDetector,
    AnomalyDetector,
    DuplicateDetector,
)
from app.ml.transaction_intelligence.classifier import (
    AITransactionClassifier,
    RuleBasedClassifier,
)

__all__ = [
    "TextNormalizer",
    "TransactionParser",
    "MerchantMatcher",
    "RecurringDetector",
    "AnomalyDetector",
    "DuplicateDetector",
    "AITransactionClassifier",
    "RuleBasedClassifier",
]
