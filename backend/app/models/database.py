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
    """Persistent financial memory and behavioral insights."""
    __tablename__ = "financial_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    memory_type = Column(String, index=True)  # spending_pattern, behavior, insight, goal, etc.
    title = Column(String)
    description = Column(Text)
    data = Column(JSON)
    
    confidence_score = Column(Float, default=0.8)
    is_validated = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="financial_memory")


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
