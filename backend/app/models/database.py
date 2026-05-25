"""
Database models for JimFinance.
Core entities: User, Account, Transaction, Category, Subscription, etc.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON, Numeric, DECIMAL, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class Currency(str, Enum):
    """Supported currencies."""
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    INR = "INR"
    GBP = "GBP"


class TransactionCategory(str, Enum):
    """Transaction categories."""
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


class TransactionType(str, Enum):
    """Transaction types."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class AccountType(str, Enum):
    """Account types."""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"
    CASH = "cash"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    financial_memory = relationship("FinancialMemory", back_populates="user", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("FinancialGoal", back_populates="user", cascade="all, delete-orphan")
    agent_reports = relationship("AgentReport", back_populates="user", cascade="all, delete-orphan")
    financial_insights = relationship("FinancialInsight", back_populates="user", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="user", cascade="all, delete-orphan")
    financial_health_reports = relationship("FinancialHealthReport", back_populates="user", cascade="all, delete-orphan")
    merchant_profiles = relationship("MerchantProfile", back_populates="user", cascade="all, delete-orphan")
    subscription_profiles = relationship("SubscriptionProfile", back_populates="user", cascade="all, delete-orphan")
    forecast_records = relationship("ForecastRecord", back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    """User financial accounts."""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    account_type = Column(SQLEnum(AccountType))
    currency = Column(SQLEnum(Currency), default=Currency.USD)
    balance = Column(DECIMAL(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class Category(Base):
    """Transaction categories."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    category_type = Column(SQLEnum(TransactionCategory))
    color = Column(String, default="#808080")
    icon = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    """Financial transactions."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    amount = Column(DECIMAL(15, 2), index=True)
    currency = Column(SQLEnum(Currency))
    merchant = Column(String, index=True)
    description = Column(String, nullable=True)
    transaction_type = Column(SQLEnum(TransactionType))
    
    transaction_date = Column(DateTime(timezone=True), index=True)
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(String, nullable=True)  # daily, weekly, monthly, yearly
    
    confidence_score = Column(Float, default=1.0)  # AI confidence in categorization
    is_duplicate = Column(Boolean, default=False)
    source_type = Column(String, default="manual")  # manual, telegram, ocr, api
    raw_input = Column(Text, nullable=True)
    
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, nullable=True)
    
    tags = Column(JSON, default=[])
    metadata = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


class Subscription(Base):
    """Recurring subscriptions."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), index=True)
    
    name = Column(String, index=True)
    merchant = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    amount = Column(DECIMAL(15, 2))
    currency = Column(SQLEnum(Currency))
    billing_cycle = Column(String)  # monthly, yearly, weekly, etc.
    billing_date = Column(Integer)  # day of month, 1-31
    
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    auto_renew = Column(Boolean, default=True)
    cancellation_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")


class FinancialMemory(Base):
    """Persistent financial memory and behavioral insights with vector embeddings."""
    __tablename__ = "financial_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Memory classification
    memory_type = Column(String, index=True)  # spending_pattern, emotional_spending, salary_cycle, 
                                               # recurring_expense, subscription, behavioral_trigger, 
                                               # seasonal_spending, financial_goal, user_priority, risk_tolerance
    memory_category = Column(String, index=True)  # Fine-grained categorization
    title = Column(String, index=True)
    description = Column(Text)
    
    # Core memory content
    data = Column(JSON)  # Structured financial data
    transaction_ids = Column(JSON, default=[])  # References to source transactions
    
    # Vector embedding for semantic search
    embedding = Column(Vector(1536), nullable=True)  # OpenAI embedding dimension (1536 for text-embedding-3-small)
    embedding_model = Column(String, default="text-embedding-3-small")
    
    # Memory scoring and weighting
    confidence_score = Column(Float, default=0.8)  # AI confidence in memory extraction
    is_validated = Column(Boolean, default=False)  # User-validated memory
    impact_score = Column(Float, default=0.5)  # Financial impact quantification (0-1)
    relevance_score = Column(Float, default=0.5)  # Current relevance score
    retrieval_count = Column(Integer, default=0)  # How many times retrieved (for popularity ranking)
    
    # Temporal tracking
    memory_date = Column(DateTime(timezone=True), index=True)  # When this memory occurred
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)  # Last retrieval time
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Behavioral context
    contextual_data = Column(JSON, default={})  # Additional context: emotional_state, external_factors, etc.
    behavioral_tags = Column(JSON, default=[])  # e.g., ["stress_spending", "seasonal", "impulsive"]
    
    # Relationships
    user = relationship("User", back_populates="financial_memory")


class MemoryInteraction(Base):
    """Track memory retrieval patterns for ranking and insights."""
    __tablename__ = "memory_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, ForeignKey("financial_memory.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Interaction metadata
    context = Column(String)  # transaction_categorization, behavioral_analysis, anomaly_detection, etc.
    retrieval_score = Column(Float)  # Score assigned during this retrieval
    relevance_feedback = Column(Float, nullable=True)  # User feedback on relevance (-1, 0, 1)
    
    retrieved_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class BehavioralProfile(Base):
    """Longitudinal behavioral profile with spending patterns and triggers."""
    __tablename__ = "behavioral_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    
    # Risk profile
    risk_tolerance = Column(String)  # conservative, moderate, aggressive
    risk_score = Column(Float, default=0.5)  # 0-1 scale
    
    # Behavioral characteristics
    spending_triggers = Column(JSON, default=[])  # e.g., ["stress", "weekend", "after_paycheck"]
    seasonal_patterns = Column(JSON, default={})  # Monthly spending variations
    emotional_spending_tendency = Column(Float, default=0.5)  # 0-1 scale
    
    # Financial priorities (user-set)
    priorities = Column(JSON, default=[])  # e.g., ["savings", "investments", "debt_reduction"]
    priority_weights = Column(JSON, default={})  # Weighted priorities
    
    # Longitudinal metrics
    avg_spending_per_month = Column(DECIMAL(15, 2), nullable=True)
    spending_volatility = Column(Float, nullable=True)  # Standard deviation of spending
    max_comfortable_transaction = Column(DECIMAL(15, 2), nullable=True)
    
    # Profile timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    profile_last_refined_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")


class Forecast(Base):
    """Financial forecasts and projections."""
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    forecast_type = Column(String)  # cashflow, spending, income, runway, etc.
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    predicted_value = Column(DECIMAL(15, 2))
    confidence_interval_low = Column(DECIMAL(15, 2), nullable=True)
    confidence_interval_high = Column(DECIMAL(15, 2), nullable=True)
    confidence_score = Column(Float)
    
    methodology = Column(String)  # ARIMA, Prophet, ML-based, etc.
    parameters = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="forecasts")


class FinancialGoal(Base):
    """User financial goals."""
    __tablename__ = "financial_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    goal_type = Column(String)  # savings, investment, debt_payoff, etc.
    
    target_amount = Column(DECIMAL(15, 2))
    current_progress = Column(DECIMAL(15, 2), default=0)
    currency = Column(SQLEnum(Currency))
    
    target_date = Column(DateTime(timezone=True))
    priority = Column(Integer, default=1)  # 1=low, 5=high
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="goals")


class AgentReport(Base):
    """Historical agent analysis reports (SynthesisOutput storage)."""
    __tablename__ = "agent_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Report metadata
    report_type = Column(String, default="full_analysis")  # full_analysis, strategy_only, risk_only
    period_start = Column(DateTime(timezone=True), index=True)
    period_end = Column(DateTime(timezone=True), index=True)
    
    # Synthesis output
    executive_summary = Column(Text)
    priority_level = Column(String)  # critical, high, medium, low
    overall_confidence = Column(Float)
    
    # Agent perspectives stored as JSON
    strategist_perspective = Column(JSON)  # StrategistOutput
    critic_perspective = Column(JSON)  # CriticOutput
    
    # Key findings
    key_insights = Column(JSON, default=[])  # List of FinancialInsight dicts
    action_items = Column(JSON, default=[])  # List of action items
    
    # Analysis metrics
    financial_metrics = Column(JSON, nullable=True)  # FinancialMetrics
    transaction_count = Column(Integer, default=0)
    
    # Status and tracking
    is_reviewed = Column(Boolean, default=False)
    user_feedback = Column(JSON, nullable=True)  # User feedback on report
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="agent_reports")
    insights = relationship("FinancialInsight", back_populates="report", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="report", cascade="all, delete-orphan")


class FinancialInsight(Base):
    """Individual financial insights extracted from agent analysis."""
    __tablename__ = "financial_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    report_id = Column(Integer, ForeignKey("agent_reports.id"), nullable=True, index=True)
    
    # Insight classification
    insight_type = Column(String, index=True)  # spending_pattern, budget_optimization, savings_opportunity, etc.
    impact = Column(String)  # positive, negative, neutral
    
    # Content
    title = Column(String, index=True)
    description = Column(Text)
    
    # Quantitative data
    metric_value = Column(DECIMAL(15, 2), nullable=True)
    metric_unit = Column(String, nullable=True)  # USD, %, number, etc.
    confidence = Column(Float, default=0.8)
    
    # Recommendations
    action = Column(Text, nullable=True)
    priority = Column(Integer, nullable=True)  # 1-5
    
    # Tracking
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="financial_insights")
    report = relationship("AgentReport", back_populates="insights")


class RiskAssessment(Base):
    """Risk assessments from Critic Agent analysis."""
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    report_id = Column(Integer, ForeignKey("agent_reports.id"), nullable=True, index=True)
    
    # Risk classification
    risk_level = Column(String, index=True)  # low, medium, high, critical
    risk_score = Column(Float)  # 0-100
    
    # Health metrics
    financial_health_score = Column(Float)  # 0-100
    
    # Risk details
    title = Column(String, index=True)
    description = Column(Text)
    
    # Risk factors
    vulnerabilities = Column(JSON, default=[])  # List of vulnerability dicts
    alerts = Column(JSON, default=[])  # List of alert dicts
    critical_issues = Column(JSON, default=[])  # List of critical issues
    
    # Recommendations
    recommendations = Column(JSON, default=[])  # List of recommendation strings
    confidence = Column(Float)
    
    # Response tracking
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    mitigation_actions = Column(JSON, nullable=True)  # User's mitigation actions
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="risk_assessments")
    report = relationship("AgentReport", back_populates="risk_assessments")


class FinancialHealthReport(Base):
    """Periodic financial health snapshots from Phase 5 intelligence engine."""
    __tablename__ = "financial_health_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Report metadata
    report_period_start = Column(DateTime(timezone=True), index=True)
    report_period_end = Column(DateTime(timezone=True), index=True)
    
    # Financial metrics
    savings_rate = Column(Float)  # %
    burn_rate_monthly = Column(DECIMAL(15, 2))  # USD/month
    cashflow_smoothness = Column(Float)  # 0-100
    financial_health_score = Column(Float)  # 0-100
    volatility_score = Column(Float)  # 0-100
    
    # Analysis data
    metrics_json = Column(JSON)  # Full metrics dict from engine
    merchant_analysis = Column(JSON)  # Top merchants
    subscription_analysis = Column(JSON)  # Subscriptions found
    cashflow_analysis = Column(JSON)  # Cashflow metrics
    runway_analysis = Column(JSON)  # Runway projections
    behavioral_insights = Column(JSON, default=[])  # Insights array
    
    # Confidence scoring
    overall_confidence = Column(Float)
    
    # Status tracking
    is_reviewed = Column(Boolean, default=False)
    user_feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="financial_health_reports")


class MerchantProfile(Base):
    """Merchant spending profiles and analysis."""
    __tablename__ = "merchant_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Merchant identification
    merchant_name = Column(String, index=True)
    merchant_normalized = Column(String, index=True)  # Normalized name
    category = Column(String)
    
    # Spending analysis
    transaction_count = Column(Integer)
    total_spent = Column(DECIMAL(15, 2))
    average_transaction = Column(DECIMAL(15, 2))
    min_transaction = Column(DECIMAL(15, 2))
    max_transaction = Column(DECIMAL(15, 2))
    
    # Time analysis
    first_transaction_date = Column(DateTime(timezone=True))
    last_transaction_date = Column(DateTime(timezone=True))
    frequency_days = Column(Float)  # Average days between visits
    
    # Price analysis
    price_trend = Column(Float)  # % change
    price_volatility = Column(Float)  # Std dev
    
    # Characteristics
    is_likely_subscription = Column(Boolean, default=False)
    is_loyalty_program = Column(Boolean, default=False)
    merchant_risk_score = Column(Float)  # 0-100, lower is better
    
    # Confidence and metadata
    confidence_score = Column(Float)
    tags = Column(JSON, default=[])
    
    # Tracking
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="merchant_profiles")


class SubscriptionProfile(Base):
    """Detected subscription and recurring payment profiles."""
    __tablename__ = "subscription_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Subscription identification
    subscription_name = Column(String, index=True)
    merchant = Column(String)
    category = Column(String)
    
    # Financial data
    amount = Column(DECIMAL(15, 2))
    currency = Column(SQLEnum(Currency), default=Currency.USD)
    billing_cycle = Column(String)  # daily, weekly, monthly, yearly, etc.
    estimated_yearly_cost = Column(DECIMAL(15, 2))
    
    # Pattern analysis
    first_occurrence = Column(DateTime(timezone=True))
    last_occurrence = Column(DateTime(timezone=True))
    occurrence_count = Column(Integer)
    confidence_score = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    churn_risk = Column(Float)  # 0-1, probability of cancellation
    
    # Trends and analysis
    price_trend = Column(Float)  # % change
    cost_effectiveness_score = Column(Float)  # 0-100
    optimization_opportunities = Column(JSON, default=[])
    tags = Column(JSON, default=[])
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscription_profiles")


class ForecastRecord(Base):
    """Historical forecast records for comparison and validation."""
    __tablename__ = "forecast_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Forecast metadata
    forecast_created_at = Column(DateTime(timezone=True), index=True)
    forecast_category = Column(String)  # 'spending', 'income', 'category_specific'
    forecast_for_category = Column(String, nullable=True)  # Specific category if applicable
    
    # Forecast data
    forecast_periods = Column(JSON)  # Array of {period, value, lower, upper, confidence}
    methodology = Column(String)  # 'exponential_smoothing', 'arima', etc.
    
    # Historical metrics
    historical_months = Column(Integer)
    average_historical = Column(DECIMAL(15, 2))
    trend_direction = Column(String)  # 'increasing', 'decreasing', 'stable'
    trend_percentage = Column(Float)
    seasonality_strength = Column(Float)
    
    # Accuracy tracking
    actual_values = Column(JSON, nullable=True)  # Actual values as they become available
    forecast_accuracy = Column(Float, nullable=True)  # MAPE or similar metric
    is_validated = Column(Boolean, default=False)
    
    # Status
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="forecast_records")
