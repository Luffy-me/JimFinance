"""
Text processing and normalization for transaction data.
"""

import re
from typing import Tuple, Optional
from datetime import datetime
import unicodedata


class TextNormalizer:
    """Normalize and clean raw transaction text input."""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text: lowercase, remove extra spaces, unicode normalization."""
        if not text:
            return ""
        
        # Unicode normalization (NFD -> remove combining characters)
        text = unicodedata.normalize("NFKD", text)
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        
        # Remove non-ASCII-safe characters except Cyrillic and common symbols
        text = re.sub(r"[^\w\s\-.,руб$€£¥₹₽\(\)\[\]]", "", text, flags=re.UNICODE)
        
        return text.strip()
    
    @staticmethod
    def remove_extra_spaces(text: str) -> str:
        """Remove extra spaces and normalize whitespace."""
        return re.sub(r"\s+", " ", text).strip()
    
    @staticmethod
    def clean_merchant_name(merchant: str) -> str:
        """Clean and standardize merchant names."""
        if not merchant:
            return ""
        
        merchant = TextNormalizer.normalize_text(merchant)
        
        # Remove common prefixes
        prefixes = [
            r"^(the|at|shop|store|cafe|restaurant|bar|cafe|www\.|https?://)",
            r"(\(.*?\)|\[.*?\])",  # Remove parentheses content
        ]
        
        for prefix in prefixes:
            merchant = re.sub(prefix, "", merchant, flags=re.IGNORECASE).strip()
        
        # Remove duplicated words
        words = merchant.split()
        seen = set()
        unique_words = []
        for word in words:
            if word.lower() not in seen:
                unique_words.append(word)
                seen.add(word.lower())
        
        merchant = " ".join(unique_words)
        
        return merchant
    
    @staticmethod
    def extract_currency(text: str) -> Optional[str]:
        """Extract currency code from text."""
        currency_patterns = {
            "RUB": r"(руб|rub|р\.|₽)",
            "USD": r"(\$|usd|доллар)",
            "EUR": r"(€|eur|евро)",
            "GBP": r"(£|gbp|фунт)",
            "INR": r"(₹|inr|рупия)",
        }
        
        text_lower = text.lower()
        for currency_code, pattern in currency_patterns.items():
            if re.search(pattern, text_lower):
                return currency_code
        
        return None
    
    @staticmethod
    def extract_amount(text: str) -> Optional[float]:
        """Extract numeric amount from text."""
        # Match various number formats: 123.45, 123,45, 123
        amount_pattern = r"(\d+[.,]\d{1,2}|\d+)"
        
        # Find all matches and return the largest (likely the transaction amount)
        matches = re.findall(amount_pattern, text)
        if matches:
            # Convert to float, handling both . and , as decimal separator
            amount_str = matches[0].replace(",", ".")
            try:
                return float(amount_str)
            except ValueError:
                return None
        
        return None
    
    @staticmethod
    def extract_date(text: str) -> Optional[datetime]:
        """Extract date from text (various formats)."""
        date_patterns = [
            (r"(\d{1,2})[./\-](\d{1,2})[./\-](\d{2,4})", "%d/%m/%Y"),
            (r"(\d{1,2})[./\-](\d{1,2})[./\-](\d{4})", "%d/%m/%Y"),
            (r"(\d{4})[./\-](\d{1,2})[./\-](\d{1,2})", "%Y/%m/%d"),
        ]
        
        for pattern, date_format in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(0)
                    return datetime.strptime(date_str, date_format)
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def remove_special_characters(text: str) -> str:
        """Remove special characters, keeping alphanumeric and basic punctuation."""
        return re.sub(r"[^\w\s\-.,]", "", text, flags=re.UNICODE)
    
    @staticmethod
    def tokenize_text(text: str) -> list[str]:
        """Split text into tokens (words)."""
        tokens = re.findall(r"\b\w+\b", text.lower())
        return tokens
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Simple language detection (Russian or English)."""
        cyrillic_count = len(re.findall(r"[а-яё]", text.lower()))
        latin_count = len(re.findall(r"[a-z]", text.lower()))
        
        if cyrillic_count > latin_count:
            return "ru"
        elif latin_count > cyrillic_count:
            return "en"
        else:
            return "mixed"


class TransactionParser:
    """Parse raw transaction input into structured format."""
    
    @staticmethod
    def parse_simple_input(text: str) -> dict:
        """
        Parse simple transaction input like 'Taxi 420' or '1500 RUB Pyaterochka'.
        Returns dict with extracted fields.
        """
        normalizer = TextNormalizer()
        
        # Normalize input
        text = normalizer.normalize_text(text)
        
        # Extract fields
        result = {
            "raw_input": text,
            "merchant": None,
            "amount": None,
            "currency": None,
            "description": None,
        }
        
        # Try to extract amount
        amount = normalizer.extract_amount(text)
        if amount:
            result["amount"] = amount
        
        # Try to extract currency
        currency = normalizer.extract_currency(text)
        if currency:
            result["currency"] = currency
        
        # Try to extract date
        date = normalizer.extract_date(text)
        if date:
            result["date"] = date
        
        # Extract merchant name (text without numbers)
        merchant_words = []
        for word in text.split():
            # Skip numbers and currency symbols
            if not re.match(r"^[\d\.,₽$€£¥₹()]+$", word):
                merchant_words.append(word)
        
        if merchant_words:
            merchant = " ".join(merchant_words)
            result["merchant"] = normalizer.clean_merchant_name(merchant)
        
        return result
    
    @staticmethod
    def parse_bank_notification(text: str) -> dict:
        """
        Parse Russian bank SMS/notification format.
        Example: 'Card XXXX SPENDING -500 RUB at PIAZZA on 24.11.2023 23:45'
        """
        normalizer = TextNormalizer()
        
        result = {
            "raw_input": text,
            "merchant": None,
            "amount": None,
            "currency": None,
            "description": None,
            "date": None,
        }
        
        # Extract currency and amount
        currency = normalizer.extract_currency(text)
        if currency:
            result["currency"] = currency
        
        amount = normalizer.extract_amount(text)
        if amount:
            result["amount"] = amount
        
        # Extract date
        date = normalizer.extract_date(text)
        if date:
            result["date"] = date
        
        # Extract merchant (usually after 'at' or similar)
        merchant_match = re.search(r"(?:at|на|в)\s+([A-Za-zа-яА-ЯёЁ\s]+?)(?:\s+on|\s+в|$)", text, re.IGNORECASE)
        if merchant_match:
            merchant = merchant_match.group(1).strip()
            result["merchant"] = normalizer.clean_merchant_name(merchant)
        
        return result
