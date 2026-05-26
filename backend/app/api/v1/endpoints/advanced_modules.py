"""Advanced financial modules API endpoints (Phase 5)."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.database import User
from app.api.v1.endpoints.users import get_current_user
from app.ml.investment_allocation.portfolio_optimizer import PortfolioOptimizer, AssetClass
from app.ml.investment_allocation.risk_profiler import RiskProfiler
from app.ml.wealth_forecasting.compound_simulator import WealthForecastingEngine
from app.ml.tuition_planning.cost_projector import TuitionPlanner

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# INVESTMENT ALLOCATION ENDPOINTS
# ============================================================================

@router.post("/investment/assess-risk-profile")
async def assess_risk_profile(
    spending_volatility: Optional[float] = None,
    mean_spending: Optional[float] = None,
    loss_frequency: Optional[float] = None,
    investment_horizon_years: int = 10,
    current_user: User = Depends(get_current_user),
):
    """
    Assess investor risk tolerance.
    
    Combines behavioral data with stated preferences.
    """
    try:
        profiler = RiskProfiler()
        profile = profiler.profile_investor(
            spending_volatility=spending_volatility,
            mean_spending=mean_spending,
            loss_frequency=loss_frequency,
            investment_horizon_years=investment_horizon_years,
        )
        
        return {
            "success": True,
            "data": profile.to_dict(),
        }
    except Exception as e:
        logger.error(f"Risk profile assessment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Assessment failed",
        )


@router.post("/investment/allocate")
async def generate_allocation(
    risk_score: float,
    investment_horizon_years: int = 10,
    current_user: User = Depends(get_current_user),
):
    """
    Generate optimal asset allocation.
    
    Args:
        risk_score: 0-100 risk score
        investment_horizon_years: Years until funds needed
        
    Returns:
        Optimal allocation with efficient frontier data
    """
    try:
        if not 0 <= risk_score <= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Risk score must be 0-100",
            )
        
        # Define asset classes
        asset_classes = [
            AssetClass(name="Stocks", expected_return=0.10, volatility=0.18),
            AssetClass(name="Bonds", expected_return=0.05, volatility=0.06),
            AssetClass(name="Real Estate", expected_return=0.08, volatility=0.12),
            AssetClass(name="Commodities", expected_return=0.04, volatility=0.15),
        ]
        
        # Create optimizer
        optimizer = PortfolioOptimizer(risk_free_rate=0.02)
        
        # Default correlation matrix
        corr_matrix = optimizer.calculate_default_correlation_matrix(
            len(asset_classes),
            default_correlation=0.3,
        )
        
        # Generate allocation based on risk score
        target_return = 0.04 + (risk_score / 100) * 0.06  # 4-10% based on risk
        
        metrics = optimizer.optimize_portfolio(
            asset_classes,
            corr_matrix,
            target_return=target_return,
        )
        
        # Calculate efficient frontier
        volatilities, returns, allocations = optimizer.calculate_efficient_frontier(
            asset_classes,
            corr_matrix,
            num_portfolios=50,
        )
        
        return {
            "success": True,
            "data": {
                "recommended_allocation": metrics.to_dict(),
                "efficient_frontier": {
                    "volatilities": volatilities,
                    "returns": returns,
                    "allocations": allocations,
                },
            },
        }
    except Exception as e:
        logger.error(f"Allocation generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Allocation generation failed",
        )


# ============================================================================
# WEALTH FORECASTING ENDPOINTS
# ============================================================================

@router.post("/wealth/forecast")
async def forecast_wealth(
    current_net_worth: float,
    monthly_income: float,
    monthly_expenses: float,
    projection_years: int = 30,
    current_user: User = Depends(get_current_user),
):
    """Forecast long-term wealth accumulation."""
    try:
        if projection_years < 1 or projection_years > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Projection years must be 1-50",
            )
        
        engine = WealthForecastingEngine()
        forecast = engine.forecast_wealth(
            current_net_worth=current_net_worth,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            projection_years=projection_years,
        )
        
        return {
            "success": True,
            "data": forecast.to_dict(),
        }
    except Exception as e:
        logger.error(f"Wealth forecast failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Forecast generation failed",
        )


# ============================================================================
# TUITION PLANNING ENDPOINTS
# ============================================================================

@router.post("/tuition/project-costs")
async def project_education_costs(
    base_annual_cost: float,
    years_until_start: int,
    education_duration_years: int,
    tuition_type: str = "US_PUBLIC",
    current_user: User = Depends(get_current_user),
):
    """Project future education costs with inflation."""
    try:
        planner = TuitionPlanner()
        result = planner.project_education_costs(
            base_annual_cost=base_annual_cost,
            years_until_start=years_until_start,
            education_duration_years=education_duration_years,
            tuition_type=tuition_type,
        )
        
        return {
            "success": True,
            "data": result.to_dict(),
        }
    except Exception as e:
        logger.error(f"Tuition cost projection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cost projection failed",
        )
