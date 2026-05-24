"""
AI-powered transaction classification using Gemini Pro.
"""

import logging
import json
from typing import Optional, Dict
from enum import Enum

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

logger = logging.getLogger(__name__)


class ClassificationResult(str, Enum):
    """Classification results."""
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    SHOPPING = "shopping"
    SUBSCRIPTIONS = "subscriptions"
    SALARY = "salary"
    INVESTMENT = "investment"
    TRANSFER = "transfer"
    OTHER = "other"


class AITransactionClassifier:
    """Classify transactions using Google Gemini Pro."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize classifier with Gemini API.
        
        Args:
            api_key: Google API key (if None, uses GOOGLE_API_KEY env var)
        """
        if not HAS_GEMINI:
            logger.warning("Gemini not available. AI classification will use rule-based fallback.")
            self.model = None
            return
        
        if api_key:
            genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel("gemini-pro")
        self.classification_prompt_template = """
You are an expert financial transaction classifier. Analyze the following transaction and classify it into one of these categories:
- food: dining, groceries, food delivery
- transport: taxi, public transit, fuel, car
- entertainment: movies, games, events, hobbies
- utilities: electricity, water, internet, phone
- healthcare: medical, pharmacy, fitness
- shopping: retail, online stores, clothing
- subscriptions: recurring services, memberships
- salary: income, freelance work, bonuses
- investment: stocks, crypto, funds
- transfer: internal transfers, ATM withdrawals
- other: anything else

Transaction Details:
- Merchant: {merchant}
- Amount: {amount} {currency}
- Description: {description}
- Date: {date}

Respond in JSON format:
{{
    "category": "<category>",
    "confidence": <0.0-1.0>,
    "reasoning": "<brief explanation>",
    "is_recurring": <true/false>,
    "is_suspicious": <true/false>
}}

Be precise and consider context. For Russian merchants, translate to understand the category.
"""
    
    def classify_transaction(
        self,
        merchant: str,
        amount: float,
        currency: str,
        description: str = None,
        date: str = None,
    ) -> Dict:
        """
        Classify a transaction using Gemini Pro.
        
        Args:
            merchant: Merchant name
            amount: Transaction amount
            currency: Currency code (RUB, USD, etc.)
            description: Optional description
            date: Optional transaction date
        
        Returns:
            Dict with classification result
        """
        if not self.model:
            return {
                "category": "other",
                "confidence": 0.0,
                "reasoning": "Gemini not available, use rule-based classifier",
            }
        
        try:
            prompt = self.classification_prompt_template.format(
                merchant=merchant or "Unknown",
                amount=amount,
                currency=currency,
                description=description or "No description",
                date=date or "Unknown date",
            )
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            response_text = response.text.strip()
            
            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                
                # Validate result
                if "category" not in result:
                    result["category"] = "other"
                if "confidence" not in result:
                    result["confidence"] = 0.5
                if "reasoning" not in result:
                    result["reasoning"] = "Classification performed by Gemini Pro"
                
                return result
            else:
                logger.warning(f"Could not parse Gemini response: {response_text}")
                return {
                    "category": "other",
                    "confidence": 0.0,
                    "reasoning": "Failed to parse classification response",
                }
        
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {
                "category": "other",
                "confidence": 0.0,
                "reasoning": f"Classification error: {str(e)}",
            }
    
    def batch_classify(
        self,
        transactions: list[Dict],
    ) -> list[Dict]:
        """
        Classify multiple transactions.
        
        Args:
            transactions: List of transaction dicts
        
        Returns:
            List of classification results
        """
        results = []
        for txn in transactions:
            result = self.classify_transaction(
                merchant=txn.get("merchant"),
                amount=txn.get("amount"),
                currency=txn.get("currency", "USD"),
                description=txn.get("description"),
                date=txn.get("date"),
            )
            results.append(result)
        
        return results
    
    def classify_with_fallback(
        self,
        merchant: str,
        amount: float,
        currency: str,
        fallback_category: str = "other",
    ) -> Dict:
        """
        Classify with fallback to deterministic classification.
        
        Args:
            merchant: Merchant name
            amount: Transaction amount
            currency: Currency code
            fallback_category: Category to use if AI fails
        
        Returns:
            Classification result
        """
        try:
            result = self.classify_transaction(merchant, amount, currency)
            
            # If low confidence, try deterministic approach
            if result.get("confidence", 0) < 0.5:
                fallback_result = self._deterministic_classify(merchant, amount, currency)
                if fallback_result.get("confidence", 0) > result.get("confidence", 0):
                    return fallback_result
            
            return result
        
        except Exception as e:
            logger.error(f"Classification fallback activated: {e}")
            return self._deterministic_classify(merchant, amount, currency)
    
    @staticmethod
    def _deterministic_classify(
        merchant: str,
        amount: float,
        currency: str,
    ) -> Dict:
        """
        Deterministic classification based on patterns.
        Fallback when AI classification fails.
        
        Args:
            merchant: Merchant name
            amount: Transaction amount
            currency: Currency code
        
        Returns:
            Classification result
        """
        merchant_lower = (merchant or "").lower()
        
        patterns = {
            "food": [
                "pizza", "cafe", "restaurant", "burger", "sushi", "shawarma",
                "grocery", "supermarket", "мак", "пятер", "пиццерия", "кафе",
                "доставка еды", "coffee", "starbucks", "sbux",
            ],
            "transport": [
                "taxi", "uber", "яндекс", "metro", "метро", "автобус",
                "трамвай", "ж/д", "газелька", "fuel", "petrol", "газ",
            ],
            "entertainment": [
                "cinema", "кино", "театр", "netflix", "spotify", "discord",
                "youtube", "gaming", "игр", "развлечени",
            ],
            "shopping": [
                "mall", "shop", "store", "магазин", "amazon", "aliexpress",
                "ozon", "wildberries", "маркет", "market",
            ],
            "utilities": [
                "электро", "вода", "газ", "интернет", "телефон",
                "power", "water", "internet", "phone", "жкх", "коммунальные",
            ],
            "healthcare": [
                "аптека", "pharmacy", "doctor", "врач", "больница",
                "hospital", "медицина", "clinic", "клиника",
            ],
            "subscriptions": [
                "subscription", "подписка", "premium", "plus", "pro",
                "monthly", "ежемесячно",
            ],
            "salary": [
                "salary", "freelance", "зарплата", "фриланс", "payment",
                "payroll", "бонус", "перевод", "bonus",
            ],
        }
        
        for category, keywords in patterns.items():
            for keyword in keywords:
                if keyword in merchant_lower:
                    return {
                        "category": category,
                        "confidence": 0.7,
                        "reasoning": f"Matched keyword '{keyword}' in merchant name",
                    }
        
        # Amount-based heuristics
        if 500 <= amount <= 5000:
            return {
                "category": "food",
                "confidence": 0.3,
                "reasoning": "Amount suggests food/dining based on typical range",
            }
        
        return {
            "category": "other",
            "confidence": 0.5,
            "reasoning": "No specific pattern matched",
        }


class RuleBasedClassifier:
    """Rule-based transaction classifier (deterministic, faster)."""
    
    # Category rules as keyword patterns
    CATEGORY_RULES = {
        "food": [
            r"(pizza|cafe|coffee|starbucks|sbux|restaurant|burger|sushi|shawarma|kebab|food|grocery|supermarket|"
            r"мак|пятер|пиццерия|кафе|ресторан|доставка|еда|столовая|паб|бар|крафт|coffeehouse|bistro|deli)"
        ],
        "transport": [
            r"(taxi|uber|яндекс\.такси|газелька|metro|метро|"
            r"автобус|трамвай|ж/д|железная|fuel|petrol|газ|бензин|рж|жд|транспорт|парковка)"
        ],
        "entertainment": [
            r"(cinema|кино|театр|concert|кинотеатр|netflix|spotify|discord|youtube|"
            r"gaming|игр|развлечени|парк|клуб|бильярд|боулинг|кино|музей)"
        ],
        "shopping": [
            r"(mall|shop|store|магазин|торговый|склад|amazon|aliexpress|"
            r"ozon|wildberries|market|маркет|мегамаркет|универсам|outlet)"
        ],
        "utilities": [
            r"(электро|вода|газ|интернет|телефон|услуга|коммунальные|жкх|"
            r"power|water|internet|phone|utilities|связь|провайдер)"
        ],
        "healthcare": [
            r"(аптека|pharmacy|doctor|врач|больница|hospital|медицина|"
            r"clinic|клиника|med|дентист|стоматолог|psychologist)"
        ],
        "subscriptions": [
            r"(subscription|подписка|premium|plus|pro|monthly|ежемесячно|"
            r"auto-renewal|автоматич|регулярная|recurring)"
        ],
        "salary": [
            r"(salary|зарплата|фриланс|freelance|оплата|платеж|возврат|"
            r"перевод|коллега|employer|работодатель|income)"
        ],
        "investment": [
            r"(stock|крипто|crypto|bitcoin|ethereum|инвест|фонд|etf|"
            r"бирж|акций|облига|брокер|trading)"
        ],
    }
    
    @classmethod
    def classify(
        cls,
        merchant: str,
        description: str = None,
    ) -> Dict:
        """
        Classify transaction using rules.
        
        Args:
            merchant: Merchant name
            description: Optional description
        
        Returns:
            Classification result
        """
        import re
        
        text = (merchant or "") + " " + (description or "")
        text_lower = text.lower()
        
        best_category = "other"
        best_confidence = 0.0
        
        for category, patterns in cls.CATEGORY_RULES.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Exact keyword match gets higher confidence
                    confidence = 0.85
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_category = category
                    
                    break
        
        return {
            "category": best_category,
            "confidence": best_confidence,
            "reasoning": f"Matched rule-based pattern for {best_category}",
        }
