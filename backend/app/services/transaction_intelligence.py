"""
Main Transaction Intelligence Service.
Orchestrates OCR, text processing, classification, and transaction enrichment.
"""

import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from io import BytesIO
from pathlib import Path

from app.ml.ocr.processor import OCRProcessor
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

logger = logging.getLogger(__name__)


class TransactionIntelligenceService:
    """
    Main service for transaction intelligence pipeline.
    
    Pipeline:
    1. Input (text, image, or raw data)
    2. OCR/extraction
    3. Normalization
    4. Merchant matching
    5. AI classification
    6. Duplicate/anomaly detection
    7. Recurring pattern detection
    8. Output structured transaction
    """
    
    def __init__(
        self,
        gemini_api_key: str = None,
        known_merchants: List[str] = None,
    ):
        """
        Initialize transaction intelligence service.
        
        Args:
            gemini_api_key: API key for Gemini classification
            known_merchants: List of known merchants for fuzzy matching
        """
        self.ocr_processor = OCRProcessor(use_paddle=True)
        self.merchant_matcher = MerchantMatcher(known_merchants)
        self.ai_classifier = AITransactionClassifier(gemini_api_key)
        self.rule_classifier = RuleBasedClassifier()
        
        self.normalizer = TextNormalizer()
        self.parser = TransactionParser()
    
    def process_text_input(
        self,
        text: str,
        user_id: int,
        account_id: int,
        source_type: str = "telegram",
    ) -> Dict:
        """
        Process raw text input and return structured transaction.
        
        Args:
            text: Raw text input (e.g., "Taxi 420 RUB")
            user_id: User ID
            account_id: Account ID
            source_type: Source type (telegram, manual, etc.)
        
        Returns:
            Structured transaction dict
        """
        logger.info(f"Processing text input: {text}")
        
        # Parse text
        parsed = self.parser.parse_simple_input(text)
        
        # Enrich with intelligence
        transaction = self._enrich_transaction(
            parsed,
            user_id=user_id,
            account_id=account_id,
            source_type=source_type,
        )
        
        return transaction
    
    def process_image_input(
        self,
        image_path: str | Path,
        user_id: int,
        account_id: int,
        source_type: str = "ocr",
    ) -> Dict:
        """
        Process image input (receipt, bank notification screenshot).
        
        Args:
            image_path: Path to image file
            user_id: User ID
            account_id: Account ID
            source_type: Source type (ocr, etc.)
        
        Returns:
            Structured transaction dict
        """
        logger.info(f"Processing image: {image_path}")
        
        # Extract text from image
        text = self.ocr_processor.extract_text_from_image(image_path)
        
        if not text or len(text) < 3:
            logger.warning(f"No text extracted from image: {image_path}")
            return self._create_empty_transaction(user_id, account_id, source_type)
        
        # Parse extracted text
        parsed = self.parser.parse_simple_input(text)
        
        # Enrich with intelligence
        transaction = self._enrich_transaction(
            parsed,
            user_id=user_id,
            account_id=account_id,
            source_type=source_type,
            raw_image_text=text,
        )
        
        return transaction
    
    def process_bytes_input(
        self,
        image_bytes: bytes,
        user_id: int,
        account_id: int,
        source_type: str = "ocr",
    ) -> Dict:
        """
        Process image bytes (from API upload).
        
        Args:
            image_bytes: Image data as bytes
            user_id: User ID
            account_id: Account ID
            source_type: Source type
        
        Returns:
            Structured transaction dict
        """
        logger.info(f"Processing {len(image_bytes)} bytes of image data")
        
        # Extract text from bytes
        text = self.ocr_processor.extract_text_from_bytes(image_bytes)
        
        if not text or len(text) < 3:
            logger.warning("No text extracted from image bytes")
            return self._create_empty_transaction(user_id, account_id, source_type)
        
        # Parse extracted text
        parsed = self.parser.parse_simple_input(text)
        
        # Enrich with intelligence
        transaction = self._enrich_transaction(
            parsed,
            user_id=user_id,
            account_id=account_id,
            source_type=source_type,
            raw_image_text=text,
        )
        
        return transaction
    
    def _enrich_transaction(
        self,
        parsed: Dict,
        user_id: int,
        account_id: int,
        source_type: str,
        raw_image_text: str = None,
    ) -> Dict:
        """
        Enrich parsed transaction with AI intelligence.
        
        Args:
            parsed: Parsed transaction dict
            user_id: User ID
            account_id: Account ID
            source_type: Source type
            raw_image_text: Raw text from OCR (optional)
        
        Returns:
            Enriched transaction dict
        """
        merchant = parsed.get("merchant") or "Unknown"
        amount = parsed.get("amount") or 0.0
        currency = parsed.get("currency") or "USD"
        description = parsed.get("description")
        date = parsed.get("date") or datetime.now()
        
        # Try to match merchant to known merchants
        best_match, match_confidence = self.merchant_matcher.find_best_match(merchant)
        if best_match:
            merchant = best_match
        
        # Classify transaction (AI with fallback to rule-based)
        classification = self._classify_transaction(merchant, amount, currency, description)
        
        # Build transaction object
        transaction = {
            "user_id": user_id,
            "account_id": account_id,
            "merchant": merchant,
            "amount": amount,
            "currency": currency,
            "description": description or "",
            "transaction_date": date,
            "transaction_type": "expense" if amount < 0 else "income" if amount > 0 else "transfer",
            "source_type": source_type,
            "raw_input": parsed.get("raw_input"),
            "category": classification.get("category"),
            "confidence_score": float(classification.get("confidence", 0.5)),
            "is_recurring": classification.get("is_recurring", False),
            "tags": self._generate_tags(merchant, classification),
            "metadata": {
                "classification_reasoning": classification.get("reasoning"),
                "merchant_confidence": float(match_confidence),
                "raw_extracted_text": raw_image_text,
            }
        }
        
        return transaction
    
    def _classify_transaction(
        self,
        merchant: str,
        amount: float,
        currency: str,
        description: str = None,
    ) -> Dict:
        """
        Classify transaction using AI with rule-based fallback.
        
        Args:
            merchant: Merchant name
            amount: Transaction amount
            currency: Currency
            description: Optional description
        
        Returns:
            Classification result dict
        """
        # Try rule-based first (faster, deterministic)
        rule_result = self.rule_classifier.classify(merchant, description)
        
        # If rule-based has low confidence, try AI
        if rule_result.get("confidence", 0) < 0.7:
            try:
                ai_result = self.ai_classifier.classify_transaction(
                    merchant=merchant,
                    amount=amount,
                    currency=currency,
                    description=description,
                )
                
                # Use AI result if it has higher confidence
                if ai_result.get("confidence", 0) > rule_result.get("confidence", 0):
                    return ai_result
            except Exception as e:
                logger.warning(f"AI classification failed, using rule-based: {e}")
        
        return rule_result
    
    @staticmethod
    def _generate_tags(merchant: str, classification: Dict) -> List[str]:
        """
        Generate tags for transaction.
        
        Args:
            merchant: Merchant name
            classification: Classification result
        
        Returns:
            List of tags
        """
        tags = []
        
        # Add category as tag
        category = classification.get("category")
        if category and category != "other":
            tags.append(category)
        
        # Add merchant-based tags
        merchant_lower = (merchant or "").lower()
        
        if "online" in merchant_lower:
            tags.append("online")
        if any(x in merchant_lower for x in ["uber", "яндекс", "taxi"]):
            tags.append("ride-sharing")
        if any(x in merchant_lower for x in ["amazon", "aliexpress", "ebay"]):
            tags.append("marketplace")
        
        # Add recurring tag
        if classification.get("is_recurring"):
            tags.append("recurring")
        
        return list(set(tags))  # Remove duplicates
    
    @staticmethod
    def _create_empty_transaction(
        user_id: int,
        account_id: int,
        source_type: str,
    ) -> Dict:
        """Create empty transaction when extraction fails."""
        return {
            "user_id": user_id,
            "account_id": account_id,
            "merchant": "Unknown",
            "amount": 0.0,
            "currency": "USD",
            "description": "Failed to extract transaction data",
            "transaction_date": datetime.now(),
            "transaction_type": "transfer",
            "source_type": source_type,
            "raw_input": "",
            "category": "other",
            "confidence_score": 0.0,
            "is_recurring": False,
            "tags": [],
            "metadata": {
                "extraction_failed": True,
            }
        }
    
    def check_duplicate(
        self,
        transaction: Dict,
        recent_transactions: List[Dict],
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if transaction is a duplicate.
        
        Args:
            transaction: Transaction to check
            recent_transactions: Recent transactions to compare against
        
        Returns:
            Tuple of (is_duplicate, duplicate_transaction_id)
        """
        return DuplicateDetector.is_duplicate(transaction, recent_transactions)
    
    def check_anomaly(
        self,
        transaction: Dict,
        historical_transactions: List[Dict],
    ) -> Tuple[bool, float]:
        """
        Check if transaction is anomalous.
        
        Args:
            transaction: Transaction to check
            historical_transactions: Historical transactions for comparison
        
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        return AnomalyDetector.detect_anomaly(transaction, historical_transactions)
    
    def check_recurring(
        self,
        transactions: List[Dict],
        merchant: str = None,
    ) -> Tuple[bool, str, Dict]:
        """
        Check if transactions form a recurring pattern.
        
        Args:
            transactions: List of transactions with same merchant
            merchant: Optional merchant to filter by
        
        Returns:
            Tuple of (is_recurring, pattern, metadata)
        """
        return RecurringDetector.detect_recurring(transactions, merchant)
