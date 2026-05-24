"""
Transaction endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.database import Transaction, User, Account
from app.schemas import TransactionCreate, TransactionResponse, TransactionUpdate
from app.api.v1.endpoints.users import get_current_user

router = APIRouter()


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new transaction."""
    # Verify account belongs to user
    account = db.query(Account).filter(
        (Account.id == transaction.account_id) & (Account.user_id == current_user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    db_transaction = Transaction(
        user_id=current_user.id,
        account_id=transaction.account_id,
        amount=transaction.amount,
        currency=transaction.currency,
        merchant=transaction.merchant,
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        category_id=transaction.category_id,
        transaction_date=transaction.transaction_date,
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.get("", response_model=list[TransactionResponse])
async def list_transactions(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all user transactions."""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get transaction by ID."""
    transaction = db.query(Transaction).filter(
        (Transaction.id == transaction_id) & (Transaction.user_id == current_user.id)
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update transaction."""
    transaction = db.query(Transaction).filter(
        (Transaction.id == transaction_id) & (Transaction.user_id == current_user.id)
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    if transaction_update.merchant is not None:
        transaction.merchant = transaction_update.merchant
    if transaction_update.category_id is not None:
        transaction.category_id = transaction_update.category_id
    if transaction_update.description is not None:
        transaction.description = transaction_update.description
    if transaction_update.tags is not None:
        transaction.tags = transaction_update.tags
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete transaction."""
    transaction = db.query(Transaction).filter(
        (Transaction.id == transaction_id) & (Transaction.user_id == current_user.id)
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "Transaction deleted successfully"}
