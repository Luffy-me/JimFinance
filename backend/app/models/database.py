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
    financial_decisions = relationship("FinancialDecision", back_populates="user", cascade="all, delete-orphan")
    decision_analyses = relationship("DecisionAnalysis", back_populates="user", cascade="all, delete-orphan")


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


# ==================== PHASE 4: FINANCIAL DECISIONS ====================


class FinancialDecision(Base):
    """User's financial decisions (e.g., purchase affordability analysis)."""
    
    __tablename__ = "financial_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Decision metadata
    decision_id = Column(String, unique=True, index=True)  # UUID
    decision_name = Column(String)  # "iPhone Purchase"
    description = Column(Text)
    decision_type = Column(String)  # "lump_sum", "financed"
    
    # Financial parameters
    purchase_price = Column(DECIMAL(15, 2))
    monthly_payment = Column(DECIMAL(15, 2), nullable=True)
    months_to_pay = Column(Integer, nullable=True)
    
    # Analysis metadata
    analysis_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    days_of_data_used = Column(Integer)
    
    # Results storage
    quantitative_analysis = Column(JSON)  # Full quantitative analysis result
    scenario_analysis = Column(JSON)  # Conservative/balanced/aggressive scenarios
    affordability_verdict = Column(String)  # "highly_recommended", "recommended", "neutral", etc.
    confidence_score = Column(Float)  # 0-1
    
    # Agent debate (if available)
    debate_record = Column(JSON, nullable=True)  # Full debate record
    agent_positions = Column(JSON, nullable=True)  # Individual agent positions
    
    # User interaction
    user_acknowledged = Column(Boolean, default=False)
    user_notes = Column(Text, nullable=True)
    decision_made = Column(Boolean, default=False)  # Did user proceed?
    actual_purchase = Column(Boolean, nullable=True)  # Whether they actually bought
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="financial_decisions")
    analyses = relationship("DecisionAnalysis", back_populates="decision", cascade="all, delete-orphan")


class DecisionAnalysis(Base):
    """Stored analysis results for a financial decision."""
    
    __tablename__ = "decision_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    decision_id = Column(Integer, ForeignKey("financial_decisions.id"), index=True)
    
    # Analysis type
    analysis_type = Column(String)  # "quantitative", "affordability", "scenario", "debate"
    
    # Metrics
    savings_rate = Column(Float, nullable=True)
    burn_rate = Column(Float, nullable=True)
    runway_months = Column(Float, nullable=True)
    
    # Affordability details
    can_afford_lump_sum = Column(Boolean, nullable=True)
    can_afford_financed = Column(Boolean, nullable=True)
    balance_after_purchase = Column(DECIMAL(15, 2), nullable=True)
    
    # Scenario details
    scenario_type = Column(String, nullable=True)  # "conservative", "balanced", "aggressive"
    scenario_runway = Column(Float, nullable=True)
    scenario_stress_level = Column(String, nullable=True)
    
    # Impact assessment
    impact_on_runway = Column(Float, nullable=True)
    impact_on_savings_rate = Column(Float, nullable=True)
    
    # Assumptions and reasoning
    assumptions = Column(JSON)  # List of key assumptions
    reasoning_chain = Column(JSON, nullable=True)  # Step-by-step reasoning
    confidence = Column(Float)  # 0-1
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="decision_analyses")
    decision = relationship("FinancialDecision", back_populates="analyses")


class ReasoningMemory(Base):
    """
    Stores debate records and reasoning chains for past financial decisions.
    Enables learning from similar decisions and improving recommendations.
    """
    __tablename__ = "reasoning_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Decision context
    decision_id = Column(String, index=True)
    decision_name = Column(String)
    decision_description = Column(Text)
    decision_type = Column(String)  # "purchase", "investment", "spending_cut", etc.
    
    # Decision parameters
    purchase_price = Column(DECIMAL(15, 2), nullable=True)
    monthly_payment = Column(DECIMAL(15, 2), nullable=True)
    months_to_pay = Column(Integer, nullable=True)
    
    # Financial context at time of decision
    user_monthly_income = Column(DECIMAL(15, 2))
    user_monthly_expenses = Column(DECIMAL(15, 2))
    user_current_balance = Column(DECIMAL(15, 2))
    user_recurring_expenses = Column(DECIMAL(15, 2))
    
    # Debate record
    strategist_position = Column(JSON)  # Strategist's analysis and recommendation
    critic_position = Column(JSON)  # Critic's analysis and recommendation
    synthesis = Column(JSON)  # Final synthesized recommendation
    
    # Reasoning chains (for visualization)
    strategist_reasoning_chain = Column(JSON)  # Step-by-step reasoning
    critic_reasoning_chain = Column(JSON)  # Step-by-step reasoning
    
    # Quantitative analysis results
    quantitative_analysis = Column(JSON)  # Savings rate, runway, affordability, etc.
    scenario_analysis = Column(JSON)  # Conservative/balanced/aggressive scenarios
    
    # Final recommendation
    final_recommendation = Column(String)  # "highly_recommended", "recommended", "neutral", "not_recommended", "strongly_not_recommended"
    confidence_score = Column(Float)  # 0-1
    
    # Outcomes (for learning)
    actual_outcome = Column(String, nullable=True)  # "purchased", "not_purchased", "regretted", "satisfied"
    outcome_date = Column(DateTime(timezone=True), nullable=True)
    outcome_notes = Column(Text, nullable=True)
    
    # Metadata
    inflation_scenario = Column(String, default="moderate")  # low, moderate, high
    country = Column(String, default="US")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="reasoning_memories")


# ============================================================================
# NOTIFICATION MODELS
# ============================================================================

class Notification(Base):
    """Notification records for users."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Notification details
    title = Column(String)
    message = Column(Text)
    notification_type = Column(String, index=True)  # alert type
    
    # Delivery
    channels = Column(JSON)  # ["telegram", "email", "in_app"]
    status = Column(String, default="pending")  # pending, sent, delivered, failed
    
    # Content
    data = Column(JSON)  # Alert-specific data
    confidence = Column(Float)  # 0-1
    
    # Delivery tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", backref="notifications")


class UserNotificationPreference(Base):
    """User notification preferences."""
    __tablename__ = "user_notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    
    # Settings
    notifications_enabled = Column(Boolean, default=True)
    min_confidence = Column(Float, default=0.5)
    
    # Alert types
    alert_types = Column(JSON)  # Dict of alert_type: enabled
    
    # Channels
    channels = Column(JSON)  # Dict of channel: enabled
    
    # Quiet hours
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String, nullable=True)  # HH:MM format
    quiet_hours_end = Column(String, nullable=True)
    
    # Digest settings
    digest_frequency = Column(String, default="daily")  # immediate, daily, weekly
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="notification_preferences", uselist=False)


class FinancialAlert(Base):
    """Financial alerts detected for users."""
    __tablename__ = "financial_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Alert details
    alert_type = Column(String, index=True)  # spending_spike, burn_rate_warning, etc.
    severity = Column(String)  # info, warning, critical
    title = Column(String)
    message = Column(Text)
    
    # Alert data
    data = Column(JSON)
    confidence = Column(Float)
    recommendation = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    acknowledged_by_user = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", backref="financial_alerts")


# ============================================================================
# REPORT MODELS
# ============================================================================

class FinancialReport(Base):
    """Generated financial reports."""
    __tablename__ = "financial_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Period
    report_period = Column(String)  # "weekly", "monthly"
    period_start = Column(DateTime(timezone=True), index=True)
    period_end = Column(DateTime(timezone=True), index=True)
    
    # Report content
    summary = Column(JSON)
    key_metrics = Column(JSON)
    spending_analysis = Column(JSON)
    income_analysis = Column(JSON, nullable=True)
    trend_analysis = Column(JSON)
    health_analysis = Column(JSON)
    recommendations = Column(JSON)
    
    # Charts and visualizations
    charts = Column(JSON)
    
    # Metadata
    confidence = Column(Float)
    pdf_path = Column(String, nullable=True)  # Path to generated PDF
    
    # Delivery tracking
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    viewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="financial_reports")


class ReportDelivery(Base):
    """Report delivery history."""
    __tablename__ = "report_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("financial_reports.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Delivery details
    channel = Column(String)  # "telegram", "email"
    status = Column(String)  # "pending", "sent", "delivered", "failed"
    
    # Tracking
    message_id = Column(String, nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("FinancialReport", backref="deliveries")
    user = relationship("User", backref="report_deliveries")


# ============================================================================
# AUTOMATION RULES MODELS
# ============================================================================

class AutomationRule(Base):
    """Automation rules for alerts and actions."""
    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Rule details
    name = Column(String)
    description = Column(Text, nullable=True)
    
    # Condition
    condition_type = Column(String)  # "spending_spike", "low_balance", etc.
    condition_value = Column(JSON)  # Threshold and parameters
    
    # Action
    action_type = Column(String)  # "notify", "categorize", "archive"
    action_value = Column(JSON)  # Action parameters
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Tracking
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    trigger_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="automation_rules")


class TelegramUserMapping(Base):
    """Maps Telegram users to JimFinance users."""
    __tablename__ = "telegram_user_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    telegram_user_id = Column(Integer, unique=True, index=True)
    telegram_username = Column(String, nullable=True, index=True)
    
    # Connection
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Tracking
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="telegram_mapping", uselist=False)


# ============================================================================
# NOTIFICATION DELIVERY HISTORY
# ============================================================================

class NotificationDeliveryLog(Base):
    """Log of notification delivery attempts."""
    __tablename__ = "notification_delivery_logs"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Delivery attempt
    channel = Column(String)
    status = Column(String)  # "sent", "failed", "retry"
    
    # Details
    message_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Tracking
    attempt_number = Column(Integer, default=1)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    notification = relationship("Notification", backref="delivery_logs")
    user = relationship("User", backref="notification_delivery_logs")


# ============================================================================
# PHASE 5: ADVANCED FINANCIAL MODULES
# ============================================================================

class InvestmentProfile(Base):
    """User's investment profile and asset allocation preferences."""
    __tablename__ = "investment_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, unique=True)
    
    # Risk tolerance (0-100)
    risk_tolerance = Column(Integer, default=50)
    behavioral_risk_score = Column(Float, default=0.5)  # From spending volatility
    
    # Time horizons
    investment_horizon_years = Column(Integer, default=10)
    emergency_fund_months = Column(Integer, default=3)
    
    # Goals
    goals = Column(JSON, default={})  # {goal_name: target_amount}
    constraints = Column(JSON, default={})  # Portfolio constraints
    
    # Asset allocation preferences
    target_allocation = Column(JSON, nullable=True)  # {asset_class: percentage}
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="investment_profile")


class AssetClassMetrics(Base):
    """Historical performance metrics for asset classes."""
    __tablename__ = "asset_class_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_class = Column(String, index=True)  # equity, bonds, real_estate, commodities, etc.
    
    # Performance data
    date = Column(DateTime(timezone=True), index=True)
    annual_return = Column(Float)  # 0.07 = 7%
    volatility = Column(Float)  # 0.15 = 15%
    sharpe_ratio = Column(Float)
    
    # Correlation to other assets
    correlations = Column(JSON)  # {asset_class: correlation}
    
    # Historical price
    price = Column(DECIMAL(20, 8))
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AllocationRecommendation(Base):
    """Recommended asset allocation for user."""
    __tablename__ = "allocation_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Allocation
    allocation = Column(JSON)  # {asset_class: percentage}
    allocation_type = Column(String)  # "strategic", "tactical"
    
    # Metrics
    expected_return = Column(Float)
    expected_volatility = Column(Float)
    sharpe_ratio = Column(Float)
    confidence = Column(Float)
    
    # Reasoning
    assumptions = Column(JSON)
    recommendations = Column(JSON)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="allocation_recommendations")


class RebalancingEvent(Base):
    """Track rebalancing decisions and outcomes."""
    __tablename__ = "rebalancing_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Allocation drift
    current_allocation = Column(JSON)
    target_allocation = Column(JSON)
    drift_percentage = Column(JSON)  # {asset_class: drift}
    
    # Rebalancing recommendation
    recommended_trades = Column(JSON)
    tax_implications = Column(JSON)
    
    # Status
    status = Column(String, default="suggested")  # suggested, executed, skipped
    
    # Tracking
    suggested_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="rebalancing_events")


class MacroIndicator(Base):
    """Macroeconomic indicators time series."""
    __tablename__ = "macro_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Indicator details
    indicator_code = Column(String, index=True)  # GDP, CPI, UNEMPLOYMENT, etc.
    country = Column(String, index=True)
    
    # Data
    date = Column(DateTime(timezone=True), index=True)
    value = Column(Float)
    previous_value = Column(Float, nullable=True)
    change_percentage = Column(Float, nullable=True)
    
    # Metadata
    source = Column(String)  # FRED, ECB, etc.
    unit = Column(String)  # percentage, basis points, etc.
    
    # Tracking
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())


class RiskScenario(Base):
    """Macroeconomic scenario definitions and stress tests."""
    __tablename__ = "risk_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Scenario definition
    scenario_type = Column(String)  # recession, stagflation, deflation, rate_shock
    severity = Column(String)  # mild, moderate, severe
    
    # Macro assumptions
    gdp_growth_change = Column(Float)  # percentage point change
    inflation_change = Column(Float)
    unemployment_change = Column(Float)
    rate_change = Column(Float)  # basis points
    
    # Personal finance impact
    income_impact = Column(Float)  # percentage change
    expense_impact = Column(Float)
    portfolio_impact = Column(Float)
    investment_return_change = Column(Float)
    
    # Recommendations
    recommendations = Column(JSON)
    action_items = Column(JSON)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="risk_scenarios")


class PortfolioExposure(Base):
    """Macro factor exposures of user's portfolio."""
    __tablename__ = "portfolio_exposures"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Macro factors
    interest_rate_sensitivity = Column(Float)  # Beta to interest rates
    equity_beta = Column(Float)
    inflation_sensitivity = Column(Float)
    currency_exposure = Column(JSON)  # {currency: percentage}
    
    # Risk metrics
    value_at_risk = Column(Float)  # 95% VaR
    conditional_var = Column(Float)  # Expected shortfall
    
    # Tracking
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="portfolio_exposures")


class MacroAlert(Base):
    """Risk alerts based on macro indicators."""
    __tablename__ = "macro_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Alert details
    alert_type = Column(String)  # recession_warning, inflation_spike, rate_risk
    risk_level = Column(String)  # low, medium, high, critical
    
    # Signal
    trigger_indicator = Column(String)
    trigger_value = Column(Float)
    threshold = Column(Float)
    
    # Recommendation
    recommended_action = Column(String)
    urgency = Column(Integer)  # 1-10
    
    # Status
    acknowledged = Column(Boolean, default=False)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="macro_alerts")


class ExchangeRate(Base):
    """FX exchange rate time series."""
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Currency pair
    base_currency = Column(String, index=True)
    quote_currency = Column(String, index=True)
    
    # Rate data
    date = Column(DateTime(timezone=True), index=True)
    rate = Column(DECIMAL(15, 6))
    bid = Column(DECIMAL(15, 6))
    ask = Column(DECIMAL(15, 6))
    
    # Volatility
    daily_volatility = Column(Float)
    
    # Tracking
    source = Column(String)  # market_data_provider
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())


class CurrencyExposure(Base):
    """User's currency exposure across assets."""
    __tablename__ = "currency_exposures"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Exposure details
    currency = Column(String, index=True)
    asset_class = Column(String)
    
    # Amount exposure
    amount = Column(DECIMAL(20, 2))
    percentage_of_portfolio = Column(Float)
    
    # Risk
    volatility = Column(Float)
    hedge_ratio = Column(Float, default=0.0)  # Percentage hedged
    
    # Tracking
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="currency_exposures")


class FXForecast(Base):
    """Currency movement forecasts."""
    __tablename__ = "fx_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Currency pair
    base_currency = Column(String, index=True)
    quote_currency = Column(String, index=True)
    
    # Forecast
    forecast_date = Column(DateTime(timezone=True), index=True)
    forecasted_rate = Column(DECIMAL(15, 6))
    confidence = Column(Float)
    
    # Direction
    direction = Column(String)  # up, down, neutral
    probability_up = Column(Float)
    
    # Methodology
    methodology = Column(String)  # technical, fundamental, composite
    factors = Column(JSON)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HedgingPosition(Base):
    """Active FX hedges and risk management positions."""
    __tablename__ = "hedging_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Hedge details
    currency_pair = Column(String)
    hedge_type = Column(String)  # forward, option, diversification
    
    # Position
    notional_amount = Column(DECIMAL(20, 2))
    cost = Column(DECIMAL(20, 2))
    effectiveness = Column(Float)  # 0-1
    
    # Status
    status = Column(String)  # active, closed, expired
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="hedging_positions")


class TuitionPlan(Base):
    """User's education planning profile."""
    __tablename__ = "tuition_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, unique=True)
    
    # Education details
    education_level = Column(String)  # highschool, undergraduate, graduate
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Costs
    estimated_total_cost = Column(DECIMAL(20, 2))
    annual_cost = Column(DECIMAL(20, 2))
    
    # Financing
    target_savings = Column(DECIMAL(20, 2))
    financial_aid = Column(DECIMAL(20, 2), default=0)
    scholarships = Column(DECIMAL(20, 2), default=0)
    
    # Plan details
    savings_strategy = Column(JSON)  # Investment recommendation
    loan_strategy = Column(JSON)  # Loan details
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="tuition_plans")


class EducationCost(Base):
    """Education cost projections."""
    __tablename__ = "education_costs"
    
    id = Column(Integer, primary_key=True, index=True)
    tuition_plan_id = Column(Integer, ForeignKey("tuition_plans.id"), index=True)
    
    # Cost breakdown
    year = Column(Integer)
    tuition = Column(DECIMAL(20, 2))
    fees = Column(DECIMAL(20, 2))
    books = Column(DECIMAL(20, 2))
    living_expenses = Column(DECIMAL(20, 2))
    other_costs = Column(DECIMAL(20, 2))
    
    # Inflation adjusted
    nominal_total = Column(DECIMAL(20, 2))
    real_total = Column(DECIMAL(20, 2))
    
    # Inflation assumption
    inflation_rate = Column(Float)  # 0.03 = 3%
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tuition_plan = relationship("TuitionPlan", backref="cost_projections")


class LoanScenario(Base):
    """Student loan scenario analysis."""
    __tablename__ = "loan_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Loan details
    principal = Column(DECIMAL(20, 2))
    interest_rate = Column(Float)  # 0.05 = 5%
    repayment_years = Column(Integer)
    
    # Scenario
    scenario_type = Column(String)  # standard, income_driven, accelerated
    
    # Calculations
    monthly_payment = Column(DECIMAL(20, 2))
    total_interest = Column(DECIMAL(20, 2))
    total_cost = Column(DECIMAL(20, 2))
    
    # Comparison
    vs_scenario = Column(String, nullable=True)  # For comparison
    interest_saved = Column(DECIMAL(20, 2), nullable=True)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="loan_scenarios")


class SalaryProfile(Base):
    """User's compensation history and profile."""
    __tablename__ = "salary_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, unique=True)
    
    # Current compensation
    base_salary = Column(DECIMAL(20, 2))
    annual_bonus = Column(DECIMAL(20, 2), default=0)
    stock_options = Column(DECIMAL(20, 2), default=0)
    
    # Benefits
    benefits_value = Column(DECIMAL(20, 2), default=0)
    retirement_match = Column(DECIMAL(20, 2), default=0)
    
    # Job details
    job_title = Column(String)
    company_size = Column(String)  # startup, small, medium, large, enterprise
    industry = Column(String)
    years_experience = Column(Integer)
    
    # Career
    education_level = Column(String)
    certifications = Column(JSON)  # List of certifications
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="salary_profiles")


class MarketData(Base):
    """Job market salary and compensation benchmarks."""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Position details
    job_title = Column(String, index=True)
    industry = Column(String, index=True)
    location = Column(String, index=True)
    
    # Salary data
    p25_salary = Column(DECIMAL(20, 2))
    median_salary = Column(DECIMAL(20, 2))
    p75_salary = Column(DECIMAL(20, 2))
    
    # Additional comp
    average_bonus = Column(Float)  # Percentage
    average_equity = Column(Float)  # Percentage
    
    # Compensation package
    total_comp_p50 = Column(DECIMAL(20, 2))
    
    # Tracking
    data_year = Column(Integer)
    source = Column(String)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())


class NegotiationStrategy(Base):
    """Recommended salary negotiation strategies."""
    __tablename__ = "negotiation_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Job target
    target_job_title = Column(String)
    target_company = Column(String, nullable=True)
    
    # Market analysis
    market_median = Column(DECIMAL(20, 2))
    user_percentile = Column(Float)  # 0-100
    market_gap = Column(DECIMAL(20, 2))  # How much below market
    
    # Strategy
    negotiation_points = Column(JSON)  # List of talking points
    leverage = Column(JSON)  # Evidence and credentials
    ask_range = Column(JSON)  # {low: amount, high: amount}
    
    # Risk assessment
    success_probability = Column(Float)
    risk_level = Column(String)  # low, medium, high
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="negotiation_strategies")


class CareerProjection(Base):
    """Long-term career and earnings projections."""
    __tablename__ = "career_projections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Projection
    projection_years = Column(Integer)  # 10, 20, 30
    career_path = Column(String)  # individual_contributor, manager, executive
    
    # Year-by-year
    projections = Column(JSON)  # [{year: 1, salary: X, bonus: Y, equity: Z}]
    
    # Assumptions
    annual_raise = Column(Float)  # 0.03 = 3%
    promotion_frequency_years = Column(Integer)
    promotion_salary_bump = Column(Float)
    
    # Alternatives
    alternatives = Column(JSON)  # Compare different career paths
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="career_projections")


class WealthForecast(Base):
    """Long-term wealth projections (30-year horizon)."""
    __tablename__ = "wealth_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Forecast parameters
    projection_years = Column(Integer)
    time_horizon = Column(String)  # short (1-3y), medium (3-10y), long (10+y)
    
    # Starting point
    current_net_worth = Column(DECIMAL(20, 2))
    current_cash_flow = Column(DECIMAL(20, 2))  # Monthly net
    
    # Year-by-year forecast
    annual_projections = Column(JSON)  # [{year: N, net_worth: X, income: Y, expenses: Z}]
    
    # Metrics
    expected_final_net_worth = Column(DECIMAL(20, 2))
    cagr = Column(Float)  # Compound annual growth rate
    confidence_interval_low = Column(DECIMAL(20, 2))
    confidence_interval_high = Column(DECIMAL(20, 2))
    
    # Assumptions
    assumptions = Column(JSON)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="wealth_forecasts")


class Milestone(Base):
    """Financial milestones with achievement probabilities."""
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Milestone details
    milestone_name = Column(String)  # first_home, retirement, financial_independence
    target_amount = Column(DECIMAL(20, 2))
    target_date = Column(DateTime(timezone=True))
    
    # Progress
    current_progress = Column(DECIMAL(20, 2))
    progress_percentage = Column(Float)  # 0-1
    
    # Probability
    achievement_probability = Column(Float)  # 0-1
    confidence = Column(Float)
    
    # Scenarios
    optimistic_date = Column(DateTime(timezone=True))
    pessimistic_date = Column(DateTime(timezone=True))
    
    # Status
    achieved = Column(Boolean, default=False)
    achieved_date = Column(DateTime(timezone=True), nullable=True)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="milestones")


class MonteCarloResult(Base):
    """Monte Carlo simulation results for probabilistic forecasting."""
    __tablename__ = "monte_carlo_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Simulation details
    simulation_type = Column(String)  # wealth, retirement, goal_achievement
    num_simulations = Column(Integer)
    
    # Results distribution
    percentile_10 = Column(DECIMAL(20, 2))
    percentile_25 = Column(DECIMAL(20, 2))
    percentile_50 = Column(DECIMAL(20, 2))  # Median
    percentile_75 = Column(DECIMAL(20, 2))
    percentile_90 = Column(DECIMAL(20, 2))
    
    # Statistics
    mean_outcome = Column(DECIMAL(20, 2))
    std_dev = Column(DECIMAL(20, 2))
    success_rate = Column(Float)  # 0-1
    
    # Paths
    simulation_paths = Column(JSON)  # Subset of paths for visualization
    
    # Assumptions
    assumptions = Column(JSON)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="monte_carlo_results")


class DecisionOpportunityCost(Base):
    """Opportunity cost analysis for financial decisions."""
    __tablename__ = "decision_opportunity_costs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Decision
    decision_name = Column(String)
    description = Column(Text)
    
    # Alternatives
    alternatives = Column(JSON)  # [{name: X, cost: Y, opportunity_cost: Z}]
    
    # Analysis
    selected_alternative = Column(String, nullable=True)
    opportunity_cost = Column(DECIMAL(20, 2))  # Cost of next best alternative
    
    # TCO breakdown
    direct_costs = Column(JSON)
    indirect_costs = Column(JSON)
    total_cost = Column(DECIMAL(20, 2))
    
    # Regret risk
    regret_probability = Column(Float)
    regret_magnitude = Column(DECIMAL(20, 2))  # Potential loss if wrong
    
    # Tracking
    decision_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    outcome_date = Column(DateTime(timezone=True), nullable=True)
    actual_outcome = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", backref="opportunity_costs")
