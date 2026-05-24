"""
Subscription endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.database import Subscription, User, Account
from app.schemas import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate
from app.api.v1.endpoints.users import get_current_user

router = APIRouter()


@router.post("", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new subscription."""
    # Verify account belongs to user
    account = db.query(Account).filter(
        (Account.id == subscription.account_id) & (Account.user_id == current_user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    db_subscription = Subscription(
        user_id=current_user.id,
        account_id=subscription.account_id,
        name=subscription.name,
        merchant=subscription.merchant,
        amount=subscription.amount,
        currency=subscription.currency,
        billing_cycle=subscription.billing_cycle,
        billing_date=subscription.billing_date,
        start_date=subscription.start_date,
    )
    
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    return db_subscription


@router.get("", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all user subscriptions."""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).all()
    
    return subscriptions


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get subscription by ID."""
    subscription = db.query(Subscription).filter(
        (Subscription.id == subscription_id) & (Subscription.user_id == current_user.id)
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    return subscription


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    subscription_update: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update subscription."""
    subscription = db.query(Subscription).filter(
        (Subscription.id == subscription_id) & (Subscription.user_id == current_user.id)
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    if subscription_update.name is not None:
        subscription.name = subscription_update.name
    if subscription_update.amount is not None:
        subscription.amount = subscription_update.amount
    if subscription_update.is_active is not None:
        subscription.is_active = subscription_update.is_active
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription


@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete subscription."""
    subscription = db.query(Subscription).filter(
        (Subscription.id == subscription_id) & (Subscription.user_id == current_user.id)
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    
    db.delete(subscription)
    db.commit()
    
    return {"message": "Subscription deleted successfully"}
