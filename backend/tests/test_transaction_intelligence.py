"""
Tests for transaction intelligence modules.
"""

import pytest
from datetime import datetime, timedelta

from app.ml.transaction_intelligence.text_processor import TextNormalizer, TransactionParser
from app.ml.transaction_intelligence.matchers import (
    MerchantMatcher,
    RecurringDetector,
    AnomalyDetector,
    DuplicateDetector,
)
from app.ml.transaction_intelligence.classifier import RuleBasedClassifier


class TestTextNormalizer:
    """Test text normalization."""
    
    def test_normalize_text(self):
        """Test basic text normalization."""
        normalizer = TextNormalizer()
        
        result = normalizer.normalize_text("  HELLO  WORLD  ")
        assert result == "hello world"
    
    def test_extract_currency(self):
        """Test currency extraction."""
        normalizer = TextNormalizer()
        
        assert normalizer.extract_currency("500 RUB") == "RUB"
        assert normalizer.extract_currency("$100") == "USD"
        assert normalizer.extract_currency("€50") == "EUR"
        assert normalizer.extract_currency("no currency here") is None
    
    def test_extract_amount(self):
        """Test amount extraction."""
        normalizer = TextNormalizer()
        
        assert normalizer.extract_amount("500 RUB") == 500.0
        assert normalizer.extract_amount("120.50 USD") == 120.5
        assert normalizer.extract_amount("1,234.56") == 1234.56
    
    def test_clean_merchant_name(self):
        """Test merchant name cleaning."""
        normalizer = TextNormalizer()
        
        result = normalizer.clean_merchant_name("(STARBUCKS) COFFEE SHOP")
        assert "starbucks" in result.lower()
    
    def test_detect_language(self):
        """Test language detection."""
        normalizer = TextNormalizer()
        
        assert normalizer.detect_language("Привет мир") == "ru"
        assert normalizer.detect_language("Hello world") == "en"


class TestTransactionParser:
    """Test transaction parsing."""
    
    def test_parse_simple_input(self):
        """Test parsing simple transaction input."""
        result = TransactionParser.parse_simple_input("Taxi 420 RUB")
        
        assert result["merchant"] is not None
        assert result["amount"] == 420.0
        assert result["currency"] == "RUB"
    
    def test_parse_with_amount_and_merchant(self):
        """Test parsing with separate amount and merchant."""
        result = TransactionParser.parse_simple_input("1500 RUB Pyaterochka")
        
        assert result["amount"] == 1500.0
        assert result["currency"] == "RUB"
        assert "pyaterochka" in result["merchant"].lower() if result["merchant"] else True
    
    def test_parse_bank_notification(self):
        """Test parsing bank SMS format."""
        text = "Card XXXX SPENDING -500 RUB at STARBUCKS on 24.11.2023"
        result = TransactionParser.parse_bank_notification(text)
        
        assert result["amount"] == 500.0
        assert result["currency"] == "RUB"


class TestMerchantMatcher:
    """Test merchant matching."""
    
    def test_exact_match(self):
        """Test exact merchant match."""
        known_merchants = ["Starbucks", "McDonald's", "Uber"]
        matcher = MerchantMatcher(known_merchants)
        
        match, confidence = matcher.find_best_match("starbucks")
        assert match == "starbucks" or match == "Starbucks"
        assert confidence > 0.8
    
    def test_fuzzy_match(self):
        """Test fuzzy matching."""
        known_merchants = ["Starbucks Coffee", "McDonald's Restaurant"]
        matcher = MerchantMatcher(known_merchants)
        
        match, confidence = matcher.find_best_match("Starbux")
        assert match is not None
        assert confidence > 0.5
    
    def test_no_match_below_threshold(self):
        """Test no match when below threshold."""
        matcher = MerchantMatcher(["Starbucks"])
        
        match, confidence = matcher.find_best_match("Random Store", threshold=0.9)
        assert match is None


class TestRecurringDetector:
    """Test recurring payment detection."""
    
    def test_monthly_recurring(self):
        """Test detection of monthly recurring payment."""
        transactions = [
            {
                "amount": 99.99,
                "merchant": "Netflix",
                "date": datetime.now() - timedelta(days=60),
            },
            {
                "amount": 99.99,
                "merchant": "Netflix",
                "date": datetime.now() - timedelta(days=30),
            },
            {
                "amount": 99.99,
                "merchant": "Netflix",
                "date": datetime.now(),
            },
        ]
        
        is_recurring, pattern, metadata = RecurringDetector.detect_recurring(transactions)
        
        assert is_recurring is True
        assert "month" in pattern.lower()
    
    def test_weekly_recurring(self):
        """Test detection of weekly recurring payment."""
        transactions = [
            {
                "amount": 50.0,
                "merchant": "Gym",
                "date": datetime.now() - timedelta(days=14),
            },
            {
                "amount": 50.0,
                "merchant": "Gym",
                "date": datetime.now() - timedelta(days=7),
            },
            {
                "amount": 50.0,
                "merchant": "Gym",
                "date": datetime.now(),
            },
        ]
        
        is_recurring, pattern, metadata = RecurringDetector.detect_recurring(transactions)
        
        assert is_recurring is True
        assert "week" in pattern.lower()
    
    def test_irregular_not_recurring(self):
        """Test that irregular transactions are not detected as recurring."""
        transactions = [
            {
                "amount": 100.0,
                "merchant": "Random Store",
                "date": datetime.now() - timedelta(days=60),
            },
            {
                "amount": 50.0,
                "merchant": "Random Store",
                "date": datetime.now() - timedelta(days=30),
            },
            {
                "amount": 200.0,
                "merchant": "Random Store",
                "date": datetime.now(),
            },
        ]
        
        is_recurring, pattern, metadata = RecurringDetector.detect_recurring(transactions)
        
        assert is_recurring is False


class TestAnomalyDetector:
    """Test anomaly detection."""
    
    def test_detect_high_amount_anomaly(self):
        """Test detection of unusually high amount."""
        historical = [
            {"amount": 50.0, "merchant": "Cafe"},
            {"amount": 60.0, "merchant": "Cafe"},
            {"amount": 55.0, "merchant": "Cafe"},
            {"amount": 58.0, "merchant": "Cafe"},
            {"amount": 52.0, "merchant": "Cafe"},
        ] * 2  # Repeat to have enough data
        
        transaction = {
            "amount": 500.0,
            "merchant": "Cafe",
            "category": "food",
        }
        
        is_anomaly, score = AnomalyDetector.detect_anomaly(transaction, historical)
        
        assert is_anomaly is True
        assert score > 0.5
    
    def test_normal_transaction_not_anomaly(self):
        """Test that normal transactions are not flagged."""
        historical = [
            {"amount": 50.0, "merchant": "Cafe"},
            {"amount": 60.0, "merchant": "Cafe"},
            {"amount": 55.0, "merchant": "Cafe"},
        ] * 3
        
        transaction = {
            "amount": 52.0,
            "merchant": "Cafe",
            "category": "food",
        }
        
        is_anomaly, score = AnomalyDetector.detect_anomaly(transaction, historical)
        
        assert is_anomaly is False


class TestDuplicateDetector:
    """Test duplicate transaction detection."""
    
    def test_exact_duplicate_within_timeframe(self):
        """Test detection of exact duplicate."""
        now = datetime.now()
        recent = [
            {
                "amount": 50.0,
                "merchant": "Starbucks",
                "date": now - timedelta(minutes=5),
                "id": 1,
            }
        ]
        
        transaction = {
            "amount": 50.0,
            "merchant": "Starbucks",
            "date": now,
        }
        
        is_dup, dup_id = DuplicateDetector.is_duplicate(transaction, recent)
        
        assert is_dup is True
        assert dup_id == 1
    
    def test_no_duplicate_different_merchant(self):
        """Test that different merchants are not considered duplicates."""
        now = datetime.now()
        recent = [
            {
                "amount": 50.0,
                "merchant": "Starbucks",
                "date": now - timedelta(minutes=5),
                "id": 1,
            }
        ]
        
        transaction = {
            "amount": 50.0,
            "merchant": "Cafe",
            "date": now,
        }
        
        is_dup, dup_id = DuplicateDetector.is_duplicate(transaction, recent)
        
        assert is_dup is False


class TestRuleBasedClassifier:
    """Test rule-based transaction classifier."""
    
    def test_classify_food(self):
        """Test classification of food transaction."""
        result = RuleBasedClassifier.classify("Starbucks Coffee", "Morning coffee")
        
        assert result["category"] == "food"
        assert result["confidence"] > 0.7
    
    def test_classify_transport(self):
        """Test classification of transport transaction."""
        result = RuleBasedClassifier.classify("Uber Taxi", "Ride home")
        
        assert result["category"] == "transport"
        assert result["confidence"] > 0.7
    
    def test_classify_entertainment(self):
        """Test classification of entertainment transaction."""
        result = RuleBasedClassifier.classify("Netflix Premium", "Monthly subscription")
        
        assert result["category"] == "entertainment"
        assert result["confidence"] > 0.7
    
    def test_classify_shopping(self):
        """Test classification of shopping transaction."""
        result = RuleBasedClassifier.classify("Amazon.com", "Online purchase")
        
        assert result["category"] == "shopping"
        assert result["confidence"] > 0.7
    
    def test_classify_utilities(self):
        """Test classification of utilities transaction."""
        result = RuleBasedClassifier.classify("Электроэнергия", "Electric bill")
        
        assert result["category"] == "utilities"
        assert result["confidence"] > 0.7
    
    def test_classify_other_when_no_match(self):
        """Test that unknown merchants are classified as 'other'."""
        result = RuleBasedClassifier.classify("XYZ Random Store 123", "Unknown")
        
        assert result["category"] == "other"


# Integration tests
class TestTransactionIntelligenceIntegration:
    """Integration tests for the full pipeline."""
    
    def test_text_to_transaction_pipeline(self):
        """Test full pipeline from text to transaction."""
        text = "Starbucks 5 USD"
        
        normalizer = TextNormalizer()
        parser = TransactionParser()
        classifier = RuleBasedClassifier()
        
        # Parse
        parsed = parser.parse_simple_input(text)
        assert parsed["merchant"] is not None
        assert parsed["amount"] == 5.0
        
        # Classify
        classification = classifier.classify(parsed["merchant"])
        assert classification["category"] == "food"
    
    def test_multiple_merchants_matching(self):
        """Test matching multiple merchant variations."""
        matcher = MerchantMatcher(["Starbucks", "McDonald's", "Uber"])
        
        variations = ["sbux", "mcdonalds", "Uber Eats"]
        
        for variation in variations:
            match, confidence = matcher.find_best_match(variation, threshold=0.5)
            assert match is not None, f"Failed to match {variation}"
