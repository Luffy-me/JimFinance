"""
Dashboard endpoints.
Aggregate financial data and statistics.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.base import get_db
from app.models.database import (
    User,
    Account,
    Transaction,
    Subscription,
    FinancialGoal,
    TransactionType,
)
from app.schemas import DashboardResponse, DashboardStats
from app.api.v1.endpoints.users import get_current_user

router = APIRouter()


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get dashboard data for current user."""
    # Get accounts
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    
    # Calculate stats
    total_balance = sum(acc.balance for acc in accounts) if accounts else Decimal(0)
    
    # Monthly income (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_income_result = db.query(func.sum(Transaction.amount)).filter(
        (Transaction.user_id == current_user.id)
        & (Transaction.transaction_type == TransactionType.INCOME)
        & (Transaction.transaction_date >= thirty_days_ago)
    ).scalar()
    monthly_income = Decimal(monthly_income_result or 0)
    
    # Monthly expenses (last 30 days)
    monthly_expenses_result = db.query(func.sum(Transaction.amount)).filter(
        (Transaction.user_id == current_user.id)
        & (Transaction.transaction_type == TransactionType.EXPENSE)
        & (Transaction.transaction_date >= thirty_days_ago)
    ).scalar()
    monthly_expenses = Decimal(monthly_expenses_result or 0)
    
    # Savings rate
    if monthly_income > 0:
        savings_rate = float((monthly_income - monthly_expenses) / monthly_income)
    else:
        savings_rate = 0.0
    
    # Burn rate (daily average expenses)
    burn_rate = monthly_expenses / 30 if monthly_expenses > 0 else Decimal(0)
    
    # Financial runway (days until empty)
    if burn_rate > 0:
        runway_days = int(total_balance / burn_rate)
    else:
        runway_days = None
    
    stats = DashboardStats(
        total_balance=total_balance,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        savings_rate=savings_rate,
        burn_rate=burn_rate,
        financial_runway_days=runway_days,
    )
    
    # Get recent transactions
    recent_transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.transaction_date.desc())
        .limit(10)
        .all()
    )
    
    # Get subscriptions
    subscriptions = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.id)
        .all()
    )
    
    # Get financial goals
    goals = (
        db.query(FinancialGoal)
        .filter(FinancialGoal.user_id == current_user.id)
        .all()
    )
    
    return DashboardResponse(
        stats=stats,
        accounts=accounts,
        recent_transactions=recent_transactions,
        subscriptions=subscriptions,
        financial_goals=goals,
    )
