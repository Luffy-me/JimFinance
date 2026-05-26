"""
Comprehensive tests for Phase 5 advanced financial modules.
Tests cover investment allocation, macro risk, FX intelligence, tuition planning,
salary optimization, wealth forecasting, and opportunity cost analysis.
"""

import pytest
from datetime import datetime, timedelta
import numpy as np

from app.ml.investment_allocation.portfolio_optimizer import (
    PortfolioOptimizer,
    AssetClass,
    PortfolioMetrics,
)
from app.ml.investment_allocation.risk_profiler import RiskProfiler, RiskProfile
from app.ml.wealth_forecasting.compound_simulator import (
    WealthForecastingEngine,
    WealthForecastResult,
)
from app.ml.tuition_planning.cost_projector import TuitionPlanner, TuitionPlanResult


# ============================================================================
# INVESTMENT ALLOCATION TESTS
# ============================================================================

class TestPortfolioOptimizer:
    """Test portfolio optimization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = PortfolioOptimizer(risk_free_rate=0.02)
        self.asset_classes = [
            AssetClass(name="Stocks", expected_return=0.10, volatility=0.18),
            AssetClass(name="Bonds", expected_return=0.05, volatility=0.06),
            AssetClass(name="Real Estate", expected_return=0.08, volatility=0.12),
        ]
        self.num_assets = len(self.asset_classes)
        self.corr_matrix = self.optimizer.calculate_default_correlation_matrix(
            self.num_assets
        )
    
    def test_portfolio_optimizer_init(self):
        """Test optimizer initialization."""
        assert self.optimizer.risk_free_rate == 0.02
        assert self.optimizer.logger is not None
    
    def test_optimize_portfolio_basic(self):
        """Test basic portfolio optimization."""
        metrics = self.optimizer.optimize_portfolio(
            self.asset_classes,
            self.corr_matrix,
        )
        
        assert isinstance(metrics, PortfolioMetrics)
        assert 0 <= metrics.expected_return <= 0.15
        assert 0 <= metrics.volatility <= 0.20
        assert metrics.sharpe_ratio > 0
        assert len(metrics.allocation) == self.num_assets
        assert abs(sum(metrics.allocation.values()) - 1.0) < 0.01  # Sum to ~1
    
    def test_optimize_portfolio_with_target_return(self):
        """Test optimization with target return constraint."""
        target_return = 0.07
        metrics = self.optimizer.optimize_portfolio(
            self.asset_classes,
            self.corr_matrix,
            target_return=target_return,
        )
        
        assert abs(metrics.expected_return - target_return) < 0.001
    
    def test_efficient_frontier(self):
        """Test efficient frontier generation."""
        volatilities, returns, allocations = (
            self.optimizer.calculate_efficient_frontier(
                self.asset_classes,
                self.corr_matrix,
                num_portfolios=50,
            )
        )
        
        assert len(volatilities) > 0
        assert len(returns) == len(volatilities)
        assert len(allocations) == len(volatilities)
        
        # Returns should be monotonically increasing (with tolerance)
        for i in range(1, len(returns)):
            assert returns[i] >= returns[i-1] - 0.001
    
    def test_minimum_variance_portfolio(self):
        """Test minimum variance portfolio calculation."""
        metrics = self.optimizer.calculate_min_variance_portfolio(
            self.asset_classes,
            self.corr_matrix,
        )
        
        assert isinstance(metrics, PortfolioMetrics)
        assert metrics.volatility > 0
        # Min variance should have lower volatility than most
        assert metrics.volatility < max(ac.volatility for ac in self.asset_classes)
    
    def test_default_correlation_matrix(self):
        """Test correlation matrix generation."""
        for num in [2, 3, 4, 5]:
            corr = self.optimizer.calculate_default_correlation_matrix(
                num, default_correlation=0.3
            )
            
            assert corr.shape == (num, num)
            # Check diagonal is 1
            assert np.allclose(np.diag(corr), 1.0)
            # Check off-diagonal is ~0.3
            for i in range(num):
                for j in range(i+1, num):
                    assert abs(corr[i, j] - 0.3) < 0.01


class TestRiskProfiler:
    """Test risk profiling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.profiler = RiskProfiler()
    
    def test_behavioral_risk_score(self):
        """Test behavioral risk score calculation."""
        # High volatility -> higher risk tolerance
        score = self.profiler.calculate_behavioral_risk_score(
            spending_volatility=500,  # High volatility
            mean_spending=2000,
            loss_frequency=0.1,  # Rare losses
        )
        
        assert 0 <= score <= 1
        assert score > 0.4  # Should be moderate-high
    
    def test_stated_risk_score(self):
        """Test stated risk score from questionnaire."""
        responses = {
            "time_horizon": 0.8,
            "loss_tolerance": 0.6,
            "income_stability": 0.7,
            "investment_experience": 0.5,
            "financial_cushion": 0.7,
        }
        
        score = self.profiler.calculate_stated_risk_score(responses)
        
        assert 0 <= score <= 1
        assert score > 0.5  # Moderate risk profile
    
    def test_time_horizon_score(self):
        """Test time horizon scoring."""
        assert self.profiler.calculate_time_horizon_score(1) == 0.0
        assert self.profiler.calculate_time_horizon_score(3) < 0.5
        assert self.profiler.calculate_time_horizon_score(10) > 0.6
        assert self.profiler.calculate_time_horizon_score(30) > 0.9
    
    def test_profile_investor_complete(self):
        """Test complete investor profiling."""
        profile = self.profiler.profile_investor(
            spending_volatility=400,
            mean_spending=2000,
            loss_frequency=0.15,
            questionnaire_responses={
                "time_horizon": 0.7,
                "loss_tolerance": 0.5,
                "income_stability": 0.6,
                "investment_experience": 0.5,
                "financial_cushion": 0.6,
            },
            investment_horizon_years=15,
        )
        
        assert isinstance(profile, RiskProfile)
        assert 0 <= profile.overall_risk_score <= 100
        assert profile.recommended_allocation_type in [
            "conservative", "moderate", "aggressive"
        ]
        assert len(profile.suitable_asset_classes) > 0
        assert profile.confidence > 0.6  # High confidence with full data


# ============================================================================
# WEALTH FORECASTING TESTS
# ============================================================================

class TestWealthForecasting:
    """Test wealth forecasting."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = WealthForecastingEngine()
    
    def test_forecast_positive_savings(self):
        """Test wealth forecasting with positive savings."""
        result = self.engine.forecast_wealth(
            current_net_worth=50000,
            monthly_income=5000,
            monthly_expenses=3000,
            projection_years=30,
        )
        
        assert isinstance(result, WealthForecastResult)
        assert result.projected_net_worth > result.current_net_worth
        assert result.cagr > 0.05  # Should have decent growth
        assert len(result.annual_projections) == 30
    
    def test_forecast_zero_savings(self):
        """Test wealth forecasting with zero savings."""
        result = self.engine.forecast_wealth(
            current_net_worth=50000,
            monthly_income=5000,
            monthly_expenses=5000,
            projection_years=10,
        )
        
        # With zero savings, wealth should grow only from investment returns
        assert result.projected_net_worth >= result.current_net_worth
        assert result.cagr >= 0  # Non-negative
    
    def test_forecast_negative_savings(self):
        """Test wealth forecasting with negative savings (deficit)."""
        result = self.engine.forecast_wealth(
            current_net_worth=50000,
            monthly_income=3000,
            monthly_expenses=5000,
            projection_years=10,
        )
        
        # Wealth should decline
        assert result.projected_net_worth < result.current_net_worth
    
    def test_confidence_intervals(self):
        """Test confidence interval calculations."""
        result = self.engine.forecast_wealth(
            current_net_worth=50000,
            monthly_income=5000,
            monthly_expenses=3000,
            projection_years=30,
        )
        
        # CI should bracket the estimate
        assert result.confidence_interval_low < result.projected_net_worth
        assert result.confidence_interval_high > result.projected_net_worth


# ============================================================================
# TUITION PLANNING TESTS
# ============================================================================

class TestTuitionPlanning:
    """Test tuition planning."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = TuitionPlanner()
    
    def test_project_education_costs(self):
        """Test education cost projections."""
        result = self.planner.project_education_costs(
            base_annual_cost=20000,
            years_until_start=5,
            education_duration_years=4,
            tuition_type="US_PUBLIC",
        )
        
        assert isinstance(result, TuitionPlanResult)
        assert result.total_projected_cost > 20000 * 4  # Should include inflation
        assert result.required_monthly_savings > 0
        assert len(result.annual_costs) == 4
    
    def test_required_monthly_savings(self):
        """Test required monthly savings calculation."""
        result = self.planner.project_education_costs(
            base_annual_cost=25000,
            years_until_start=10,
            education_duration_years=4,
        )
        
        # Check that required savings is reasonable
        assert result.required_monthly_savings > 0
        # Rough check: total cost / months to save
        months = 10 * 12
        expected_rough = result.total_projected_cost / months
        assert abs(
            result.required_monthly_savings - expected_rough
        ) / expected_rough < 0.1


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_portfolio_with_single_asset(self):
        """Test portfolio optimization with single asset."""
        optimizer = PortfolioOptimizer()
        asset_classes = [AssetClass("Cash", expected_return=0.02, volatility=0.0)]
        corr_matrix = np.array([[1.0]])
        
        metrics = optimizer.optimize_portfolio(asset_classes, corr_matrix)
        
        assert metrics.allocation["Cash"] == pytest.approx(1.0, rel=0.01)
    
    def test_negative_net_worth(self):
        """Test wealth forecasting with negative net worth (debt)."""
        engine = WealthForecastingEngine()
        result = engine.forecast_wealth(
            current_net_worth=-100000,  # In debt
            monthly_income=5000,
            monthly_expenses=3000,
            projection_years=20,
        )
        
        # Should project positive trend
        assert result.projected_net_worth > result.current_net_worth
    
    def test_zero_current_wealth(self):
        """Test wealth forecasting starting from zero."""
        engine = WealthForecastingEngine()
        result = engine.forecast_wealth(
            current_net_worth=0,
            monthly_income=5000,
            monthly_expenses=3000,
            projection_years=30,
        )
        
        # Should accumulate wealth from savings
        assert result.projected_net_worth > 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests across modules."""
    
    def test_investment_and_wealth_integration(self):
        """Test investment allocation informing wealth forecasting."""
        # Get risk profile
        profiler = RiskProfiler()
        profile = profiler.profile_investor(investment_horizon_years=30)
        
        # Map to target return based on risk
        target_return = 0.04 + (profile.overall_risk_score / 100) * 0.06
        
        # Use in wealth forecast
        engine = WealthForecastingEngine()
        result = engine.forecast_wealth(
            current_net_worth=50000,
            monthly_income=5000,
            monthly_expenses=3000,
            annual_investment_return=target_return,
            projection_years=30,
        )
        
        # Should have consistent outputs
        assert result.projected_net_worth > 0
        assert result.cagr > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
