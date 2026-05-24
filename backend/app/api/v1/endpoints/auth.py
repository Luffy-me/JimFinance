"""
Authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.database import User
from app.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_token_pair

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Return tokens
    return create_token_pair(db_user.id, db_user.email, db_user.username)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login user."""
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Return tokens
    return create_token_pair(user.id, user.email, user.username)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token: str):
    """Refresh access token using refresh token."""
    # TODO: Implement refresh token logic
    pass


@router.post("/logout")
async def logout():
    """Logout user."""
    # TODO: Implement logout logic (token blacklist)
    return {"message": "Successfully logged out"}
