"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Any
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication Schemas
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Account Schemas
class AccountBase(BaseModel):
    name: str
    account_type: str
    currency: str = "USD"


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    balance: Optional[Decimal] = None


class AccountResponse(AccountBase):
    id: int
    user_id: int
    balance: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_type: str
    color: str = "#808080"
    icon: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    is_default: bool

    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str
    merchant: str
    description: Optional[str] = None
    transaction_type: str
    category_id: Optional[int] = None


class TransactionCreate(TransactionBase):
    account_id: int
    transaction_date: datetime


class TransactionUpdate(BaseModel):
    merchant: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    account_id: int
    confidence_score: float
    is_recurring: bool
    is_anomaly: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Subscription Schemas
class SubscriptionBase(BaseModel):
    name: str
    merchant: str
    amount: Decimal = Field(..., gt=0)
    currency: str
    billing_cycle: str
    billing_date: int = Field(..., ge=1, le=31)


class SubscriptionCreate(SubscriptionBase):
    account_id: int
    start_date: datetime


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[Decimal] = None
    is_active: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    account_id: int
    is_active: bool
    start_date: datetime
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# Financial Memory Schemas
class FinancialMemoryBase(BaseModel):
    memory_type: str
    title: str
    description: str
    data: dict


class FinancialMemoryCreate(FinancialMemoryBase):
    pass


class FinancialMemoryResponse(FinancialMemoryBase):
    id: int
    user_id: int
    confidence_score: float
    is_validated: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Financial Goal Schemas
class FinancialGoalBase(BaseModel):
    name: str
    description: Optional[str] = None
    goal_type: str
    target_amount: Decimal = Field(..., gt=0)
    currency: str
    target_date: datetime
    priority: int = Field(default=1, ge=1, le=5)


class FinancialGoalCreate(FinancialGoalBase):
    pass


class FinancialGoalUpdate(BaseModel):
    name: Optional[str] = None
    current_progress: Optional[Decimal] = None
    is_active: Optional[bool] = None


class FinancialGoalResponse(FinancialGoalBase):
    id: int
    user_id: int
    current_progress: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_balance: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    savings_rate: float
    burn_rate: Decimal
    financial_runway_days: Optional[int]


class DashboardResponse(BaseModel):
    stats: DashboardStats
    accounts: List[AccountResponse]
    recent_transactions: List[TransactionResponse]
    subscriptions: List[SubscriptionResponse]
    financial_goals: List[FinancialGoalResponse]


# Transaction Intelligence Schemas
class ClassificationResult(BaseModel):
    """AI classification result for a transaction."""
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    is_recurring: bool = False
    is_suspicious: bool = False


class TransactionIntelligenceRequest(BaseModel):
    """Request to process transaction via intelligence pipeline."""
    text: Optional[str] = None
    merchant: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = "USD"
    description: Optional[str] = None
    account_id: int


class TransactionIntelligenceResponse(BaseModel):
    """Response from transaction intelligence processing."""
    user_id: int
    account_id: int
    merchant: str
    amount: float
    currency: str
    description: str
    transaction_date: datetime
    transaction_type: str
    category: str
    confidence_score: float
    is_recurring: bool
    tags: List[str]
    source_type: str
    raw_input: Optional[str] = None
    metadata: dict


class OCRUploadRequest(BaseModel):
    """Request to upload and process image for OCR."""
    account_id: int
    description: Optional[str] = None


class OCRUploadResponse(BaseModel):
    """Response from OCR processing."""
    extracted_text: str
    transaction: TransactionIntelligenceResponse


class MerchantMatchResult(BaseModel):
    """Result of merchant fuzzy matching."""
    original: str
    matched: Optional[str]
    confidence: float


class RecurringPatternResult(BaseModel):
    """Result of recurring pattern detection."""
    is_recurring: bool
    pattern: str
    average_interval: Optional[float]
    occurrences: int
    confidence: float


class AnomalyDetectionResult(BaseModel):
    """Result of anomaly detection."""
    is_anomaly: bool
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    z_score: Optional[float] = None


# Error Schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
