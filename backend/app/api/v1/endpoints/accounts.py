"""
Account endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.database import Account, User
from app.schemas import AccountCreate, AccountResponse, AccountUpdate
from app.api.v1.endpoints.users import get_current_user

router = APIRouter()


@router.post("", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new account."""
    db_account = Account(
        user_id=current_user.id,
        name=account.name,
        account_type=account.account_type,
        currency=account.currency,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account


@router.get("", response_model=list[AccountResponse])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all user accounts."""
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get account by ID."""
    account = db.query(Account).filter(
        (Account.id == account_id) & (Account.user_id == current_user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update account."""
    account = db.query(Account).filter(
        (Account.id == account_id) & (Account.user_id == current_user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    if account_update.name is not None:
        account.name = account_update.name
    if account_update.balance is not None:
        account.balance = account_update.balance
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete account."""
    account = db.query(Account).filter(
        (Account.id == account_id) & (Account.user_id == current_user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    db.delete(account)
    db.commit()
    
    return {"message": "Account deleted successfully"}
