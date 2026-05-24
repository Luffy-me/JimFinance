"""
Category endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.database import Category, User
from app.schemas import CategoryCreate, CategoryResponse
from app.api.v1.endpoints.users import get_current_user

router = APIRouter()


@router.post("", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new category."""
    db_category = Category(
        user_id=current_user.id,
        name=category.name,
        description=category.description,
        category_type=category.category_type,
        color=category.color,
        icon=category.icon,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all user categories."""
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get category by ID."""
    category = db.query(Category).filter(
        (Category.id == category_id) & (Category.user_id == current_user.id)
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete category."""
    category = db.query(Category).filter(
        (Category.id == category_id) & (Category.user_id == current_user.id)
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    db.delete(category)
    db.commit()
    
    return {"message": "Category deleted successfully"}
