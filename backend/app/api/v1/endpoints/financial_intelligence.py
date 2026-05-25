"""
Financial Intelligence API endpoints.

Provides REST endpoints for all financial intelligence analysis and reporting.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.database import User, Account, Transaction, FinancialHealthReport
from app.api.v1.endpoints.users import get_current_user
from app.services.financial_intelligence_service import FinancialIntelligenceService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_intelligence_service() -> FinancialIntelligenceService:
    """Get financial intelligence service instance."""
    return FinancialIntelligenceService()


def _get_user_transactions(
    user_id: int,
    db: Session,
) -> list:
    """Get all transactions for a user as dicts."""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    
    return [
        {
            'id': t.id,
            'amount': float(t.amount),
            'merchant': t.merchant,
            'category': t.category.category_type if t.category else 'other',
            'transaction_type': t.transaction_type,
            'transaction_date': t.transaction_date,
            'description': t.description,
            'date': t.transaction_date,
        }
        for t in transactions
    ]


def _get_user_monthly_income(
    user_id: int,
    db: Session,
) -> Optional[float]:
    """Calculate average monthly income."""
    income_transactions = db.query(Transaction).filter(
        (Transaction.user_id == user_id) &
        (Transaction.transaction_type.in_(['income', 'transfer_in']))
    ).all()
    
    if not income_transactions:
        return None
    
    total_income = sum(float(t.amount) for t in income_transactions)
    months = len(set((t.transaction_date.year, t.transaction_date.month) for t in income_transactions))
    
    if months == 0:
        return None
    
    return total_income / months


@router.get("/intelligence/metrics")
async def get_financial_metrics(
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: FinancialIntelligenceService = Depends(get_intelligence_service),
):
    """
    Get financial health metrics for user.
    
    Returns:
    - Savings rate with confidence
    - Burn rate analysis
    - Financial health score
    - Volatility metrics
    """
    try:
        # Get transactions
        transactions = _get_user_transactions(current_user.id, db)
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transactions found for analysis",
            )
        
        # Get account balance
        if account_id:
            account = db.query(Account).filter(
                (Account.id == account_id) & (Account.user_id == current_user.id)
            ).first()
            if not account:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
            account_balance = account.balance
        else:
            # Use total balance from all accounts
            accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
            account_balance = sum(a.balance for a in accounts)
        
        # Get metrics
        metrics = service.get_metrics_summary(transactions, account_balance)
        
        return {
            'status': 'success',
            'data': metrics,
            'timestamp': db.query(Transaction).filter(
                Transaction.user_id == current_user.id
            ).order_by(Transaction.transaction_date.desc()).first().transaction_date if transactions else None,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting financial metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating financial metrics",
        )


@router.get("/intelligence/merchants")
async def get_merchant_analysis(
    top_n: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: FinancialIntelligenceService = Depends(get_intelligence_service),
):
    """
    Get merchant spending analysis.
    
    Returns:
    - Top merchants by spending
    - Merchant categorization
    - Loyalty program detection
    - Risk scoring
    """
    try:
        transactions = _get_user_transactions(current_user.id, db)
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transactions found for analysis",
            )
        
        analysis = service.get_merchant_insights(transactions, top_n=top_n)
        
        return {
            'status': 'success',
            'data': analysis,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting merchant analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing merchants",
        )


@router.get("/intelligence/subscriptions")
async def get_subscription_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: FinancialIntelligenceService = Depends(get_intelligence_service),
):
    """
    Get subscription and recurring payment analysis.
    
    Returns:
    - Detected subscriptions
    - Monthly/yearly costs
    - Churn risk scoring
    - Optimization opportunities
    """
    try:
        transactions = _get_user_transactions(current_user.id, db)
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transactions found for analysis",
            )
        
        analysis = service.get_subscription_insights(transactions)
        
        return {
            'status': 'success',
            'data': analysis,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing subscriptions",
        )


@router.get("/intelligence/cashflow")
async def get_cashflow_analysis(
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: FinancialIntelligenceService = Depends(get_intelligence_service),
):
    """
    Get cashflow pattern analysis.
    
    Returns:
    - Inflow/outflow velocity
    - Cashflow smoothness score
    - Seasonality detection
    - Peak and trough spending periods
    """
    try:
        transactions = _get_user_transactions(current_user.id, db)
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transactions found for analysis",
            )
        
        # Get account balance if specified
        account_balance = None
        if account_id:
            account = db.query(Account).filter(
                (Account.id == account_id) & (Account.user_id == current_user.id)
            ).first()
            if account:
                account_balance = account.balance
        
        analysis = service.get_cashflow_insights(transactions, account_balance)
        
        return {
            'status': 'success',
            'data': analysis,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cashflow analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing cashflow",
        )


@router.get("/intelligence/runway")
async def get_runway_analysis(
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: FinancialIntelligenceService = Depends(get_intelligence_service),
):
    """
    Get financial runway analysis with scenarios.
    
    Returns:
    - Primary scenario runway (months/days)
    - Optimistic and pessimistic scenarios
    - Emergency fund analysis
    - Sustainability score
    - Actionable recommendations
    """
    try:
        transactions = _get_user_transactions(current_user.id, db)
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transactions found for analysis",
            )
        
        # Get account balance
        if account_id:
            account = db.query(Account).filter(
                (Account.id == account_id) & (Account.user_id == current_user.id)
            ).first()
            if not account:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
            account_balance = account.balance
        else:
            accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
            account_balance = sum(a.balance for a in accounts)
        
        # Get monthly income
        monthly_income = _get_user_monthly_income(current_user.id, db)
        
        analysis = service.get_runway_analysis(
            transactions=transactions,
            account_balance=account_balance,
            monthly_income=monthly_income,
        )
        
        return {
            'status': 'success',
            'data': analysis,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting runway analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating runway",
        )


@router.get("/intelligence/forecast")
async def get_spending_forecast(
    months: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: FinancialIntelligenceService = Depends(get_intelligence_service),
):
    """
    Get spending forecast for next N months.
    
    Returns:
    - Monthly spending predictions
    - Confidence intervals
    - Trend direction
    - Seasonality strength
    """
    try:
        if not (3 <= months <= 24):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forecast months must be between 3 and 24",
            )
        
        transactions = _get_user_transactions(current_user.id, db)
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transactions found for forecasting",
            )
        
        forecast = service.get_forecast(transactions, forecast_months=months)
        
        return {
            'status': 'success',
            'data': forecast,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forecast: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating forecast",
        )


@router.get("/intelligence/behavior")
async def get_behavioral_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: FinancialIntelligenceService = Depends(get_intelligence_service),
):
    """
    Get behavioral spending insights.
    
    Returns:
    - Spending behavior patterns
    - Lifestyle inflation detection
    - Budget constraint signals
    - Discretionary vs essential spending
    """
    try:
        transactions = _get_user_transactions(current_user.id, db)
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transactions found for analysis",
            )
        
        # Get monthly income
        monthly_income = _get_user_monthly_income(current_user.id, db)
        
        insights = service.get_behavioral_insights(transactions, monthly_income)
        
        return {
            'status': 'success',
            'data': insights,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting behavioral analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing behavior",
        )


@router.get("/intelligence/health-report")
async def get_comprehensive_health_report(
    account_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: FinancialIntelligenceService = Depends(get_intelligence_service),
):
    """
    Get comprehensive financial health report.
    
    Combines all intelligence modules into single report.
    
    Returns:
    - All financial metrics
    - Merchant and subscription analysis
    - Cashflow and runway analysis
    - Spending forecasts
    - Behavioral insights
    - Overall health score and recommendations
    """
    try:
        transactions = _get_user_transactions(current_user.id, db)
        
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transactions found for report generation",
            )
        
        # Get account balance
        if account_id:
            account = db.query(Account).filter(
                (Account.id == account_id) & (Account.user_id == current_user.id)
            ).first()
            if not account:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
            account_balance = account.balance
        else:
            accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
            account_balance = sum(a.balance for a in accounts)
        
        # Get monthly income
        monthly_income = _get_user_monthly_income(current_user.id, db)
        
        # Generate comprehensive report
        report = service.generate_comprehensive_report(
            transactions=transactions,
            account_balance=account_balance,
            monthly_income=monthly_income,
        )
        
        # Optionally store in database
        try:
            health_report = FinancialHealthReport(
                user_id=current_user.id,
                report_period_start=min(t['transaction_date'] for t in transactions),
                report_period_end=max(t['transaction_date'] for t in transactions),
                savings_rate=report.get('metrics', {}).get('savings_rate', {}).get('value'),
                burn_rate_monthly=report.get('metrics', {}).get('burn_rate', {}).get('value'),
                financial_health_score=report.get('metrics', {}).get('financial_health_score', {}).get('value'),
                metrics_json=report,
                overall_confidence=0.8,
            )
            db.add(health_report)
            db.commit()
        except Exception as e:
            logger.warning(f"Could not store health report in database: {e}")
        
        return {
            'status': 'success',
            'data': report,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating health report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating comprehensive report",
        )
