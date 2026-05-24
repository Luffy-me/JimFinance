"""
API v1 router - main entry point for all API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    accounts,
    transactions,
    categories,
    subscriptions,
    dashboard,
    transaction_intelligence,
    telegram,
    agents,
)

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(transaction_intelligence.router, prefix="/intelligence", tags=["transaction_intelligence"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
