"""
Tests for Phase 4 Financial Reasoning Engine.
Comprehensive tests for quantitative analysis, scenarios, and decision analysis.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from app.ml.financial_reasoning.quantitative_engine import (
    QuantitativeEngine,
    QuantitativeMetric,
)
from app.ml.financial_reasoning.scenario_analyzer import (
    ScenarioAnalyzer,
    ScenarioType,
)
from app.ml.financial_reasoning.probability_engine import ProbabilityEngine
from app.ml.financial_reasoning.decision_analyzer import DecisionAnalyzer


class TestQuantitativeEngine:
    """Tests for QuantitativeEngine."""
    
    def setup_method(self):
        """Setup for each test."""
        self.engine = QuantitativeEngine()
    
    def test_savings_rate_calculation_positive(self):
        """Test positive savings rate calculation."""
        metric = self.engine.calculate_savings_rate(
            monthly_income=5000,
            monthly_expenses=3000,
        )
        
        assert metric is not None
        assert metric.value == 0.4  # 40% savings rate
        assert metric.confidence > 0.7
        assert metric.value >= metric.lower_bound
        assert metric.value <= metric.upper_bound
    
    def test_savings_rate_calculation_negative(self):
        """Test negative savings rate (overspending)."""
        metric = self.engine.calculate_savings_rate(
            monthly_income=3000,
            monthly_expenses=4000,
        )
        
        assert metric is not None
        assert metric.value == -1/3  # Negative savings rate
        assert metric.confidence > 0.7
    
    def test_savings_rate_zero_income(self):
        """Test with zero income (error case)."""
        metric = self.engine.calculate_savings_rate(
            monthly_income=0,
            monthly_expenses=1000,
        )
        
        assert metric.confidence == 0.0  # Should be error metric
    
    def test_burn_rate_calculation(self):
        """Test burn rate calculation from transactions."""
        transactions = [
            {
                "amount": -100,
                "date": datetime.utcnow() - timedelta(days=i),
                "type": "expense",
            }
            for i in range(30)
        ]
        
        burn_rate, trend = self.engine.calculate_burn_rate(
            transactions=transactions,
            days_span=30,
        )
        
        assert burn_rate.value > 0
        assert burn_rate.confidence > 0.7
        assert trend is not None
    
    def test_runway_calculation(self):
        """Test runway calculation."""
        metric = self.engine.calculate_runway(
            current_balance=10000,
            monthly_burn_rate=1000,
        )
        
        assert metric.value == 10  # 10 months runway
        assert metric.confidence >= 0.8
    
    def test_runway_infinite(self):
        """Test infinite runway (no burn)."""
        metric = self.engine.calculate_runway(
            current_balance=10000,
            monthly_burn_rate=0,
        )
        
        assert metric.value == float('inf')
    
    def test_cashflow_velocity(self):
        """Test cashflow velocity calculation."""
        transactions = [
            {
                "amount": 1000 if i % 2 == 0 else -500,
                "date": datetime.utcnow() - timedelta(days=i),
            }
            for i in range(30)
        ]
        
        metric = self.engine.calculate_cashflow_velocity(
            transactions=transactions,
            days_span=30,
        )
        
        assert metric.value > 0
        assert metric.confidence > 0.7
    
    def test_spending_volatility(self):
        """Test spending volatility calculation."""
        transactions = [
            {
                "amount": -100 if i % 3 == 0 else -500,
                "date": datetime.utcnow() - timedelta(days=i),
            }
            for i in range(30)
        ]
        
        metric = self.engine.calculate_spending_volatility(
            transactions=transactions,
        )
        
        assert metric.value >= 0
        assert metric.confidence > 0.7


class TestScenarioAnalyzer:
    """Tests for ScenarioAnalyzer."""
    
    def setup_method(self):
        """Setup for each test."""
        self.analyzer = ScenarioAnalyzer()
    
    def test_generate_three_scenarios(self):
        """Test generation of three scenarios."""
        scenarios = self.analyzer.generate_scenarios(
            monthly_income=5000,
            monthly_expenses=3000,
            current_balance=15000,
        )
        
        assert len(scenarios) == 3
        types = [s.type for s in scenarios]
        assert ScenarioType.CONSERVATIVE in types
        assert ScenarioType.BALANCED in types
        assert ScenarioType.AGGRESSIVE in types
    
    def test_scenario_properties(self):
        """Test scenario properties are set correctly."""
        scenarios = self.analyzer.generate_scenarios(
            monthly_income=5000,
            monthly_expenses=3000,
            current_balance=15000,
        )
        
        for scenario in scenarios:
            assert scenario.probability > 0
            assert scenario.probability <= 1
            assert scenario.confidence > 0
            assert scenario.confidence <= 1
            assert len(scenario.assumptions) > 0
            assert len(scenario.action_items) > 0
    
    def test_conservative_scenario(self):
        """Test conservative scenario is more pessimistic."""
        scenarios = self.analyzer.generate_scenarios(
            monthly_income=5000,
            monthly_expenses=3000,
            current_balance=15000,
        )
        
        conservative = next(s for s in scenarios if s.type == ScenarioType.CONSERVATIVE)
        balanced = next(s for s in scenarios if s.type == ScenarioType.BALANCED)
        
        # Conservative should have shorter or equal runway
        assert conservative.projected_runway_months <= balanced.projected_runway_months
    
    def test_affordability_analysis_lump_sum(self):
        """Test affordability analysis for lump sum purchase."""
        result = self.analyzer.affordability_analysis(
            purchase_price=5000,
            current_balance=20000,
            monthly_income=5000,
            monthly_expenses=3000,
            emergency_fund_target=9000,
        )
        
        assert "scenarios" in result
        assert "conservative" in result["scenarios"]
        assert "balanced" in result["scenarios"]
    
    def test_affordability_analysis_financed(self):
        """Test affordability analysis for financed purchase."""
        result = self.analyzer.affordability_analysis(
            purchase_price=30000,
            monthly_payment=600,
            months_to_pay=60,
            current_balance=20000,
            monthly_income=5000,
            monthly_expenses=3000,
        )
        
        assert "scenarios" in result
        assert result["purchase_type"] == "financed"


class TestProbabilityEngine:
    """Tests for ProbabilityEngine."""
    
    def setup_method(self):
        """Setup for each test."""
        self.engine = ProbabilityEngine(num_simulations=1000)
    
    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation runs successfully."""
        result = self.engine.run_monte_carlo_simulation(
            initial_balance=10000,
            monthly_income_mean=5000,
            monthly_income_std=500,
            monthly_expenses_mean=3000,
            monthly_expenses_std=200,
            months_to_simulate=12,
        )
        
        assert "simulations" in result
        assert result["simulations"] == 1000
        assert "probability_positive_end" in result
        assert "probability_never_negative" in result
        assert 0 <= result["probability_positive_end"] <= 1
    
    def test_income_distribution_estimation(self):
        """Test income distribution estimation."""
        income_history = [4800, 5000, 5200, 5100, 4900]
        
        dist = self.engine.estimate_income_distribution(income_history)
        
        assert dist.mean > 0
        assert dist.std_dev >= 0
        assert dist.percentile_5 <= dist.percentile_50
        assert dist.percentile_50 <= dist.percentile_95
    
    def test_expense_distribution_estimation(self):
        """Test expense distribution estimation."""
        expense_history = [2800, 3000, 3200, 3100, 2900]
        
        dist = self.engine.estimate_expense_distribution(expense_history)
        
        assert dist.mean > 0
        assert dist.std_dev >= 0
        assert dist.percentile_5 <= dist.percentile_50
        assert dist.percentile_50 <= dist.percentile_95
    
    def test_event_probability(self):
        """Test event probability calculation."""
        prob = self.engine.calculate_event_probability(
            event_threshold=3500,
            mean=3000,
            std_dev=200,
            direction="above",
        )
        
        assert 0 <= prob <= 1
        # Should be fairly high probability
        assert prob > 0.2
    
    def test_confidence_score_from_data(self):
        """Test confidence score from data quality."""
        score = self.engine.confidence_score_from_data_quality(
            data_points=100,
            data_span_days=90,
            data_freshness_days=1,
        )
        
        assert 0 <= score <= 1
        assert score > 0.5  # Should be decent confidence


class TestDecisionAnalyzer:
    """Tests for DecisionAnalyzer."""
    
    def setup_method(self):
        """Setup for each test."""
        self.analyzer = DecisionAnalyzer()
    
    def test_analyze_lump_sum_decision_affordable(self):
        """Test analysis of affordable lump sum purchase."""
        result = self.analyzer.analyze_decision(
            decision_name="Laptop Purchase",
            decision_description="Buy a MacBook Pro",
            purchase_price=2000,
            monthly_income=5000,
            monthly_expenses=3000,
            current_balance=20000,
            recurring_expenses=2500,
            transactions=[
                {
                    "amount": -100 if i % 2 == 0 else 5000,
                    "date": datetime.utcnow() - timedelta(days=i),
                    "type": "expense" if i % 2 == 0 else "income",
                }
                for i in range(30)
            ],
        )
        
        assert result is not None
        assert "decision" in result
        assert result["decision"]["name"] == "Laptop Purchase"
        assert "recommendation" in result
        assert "affordability" in result
        assert "financial_impacts" in result
    
    def test_analyze_financed_decision(self):
        """Test analysis of financed purchase."""
        result = self.analyzer.analyze_decision(
            decision_name="Car Purchase",
            decision_description="Buy a used car",
            purchase_price=15000,
            monthly_payment=300,
            months_to_pay=60,
            monthly_income=5000,
            monthly_expenses=3000,
            current_balance=5000,
            transactions=[],
        )
        
        assert result is not None
        assert "scenario_analysis" in result
        assert len(result["scenario_analysis"]) == 3
    
    def test_affordability_check_unaffordable(self):
        """Test detection of unaffordable purchase."""
        result = self.analyzer.analyze_decision(
            decision_name="Expensive Watch",
            decision_description="Buy luxury watch",
            purchase_price=50000,
            monthly_income=3000,
            monthly_expenses=2500,
            current_balance=5000,
            transactions=[],
        )
        
        assert result is not None
        recommendation = result["recommendation"]["level"]
        # Should recommend against or be neutral at best
        assert recommendation in ["not_recommended", "strongly_not_recommended", "neutral"]
    
    def test_decision_with_minimal_data(self):
        """Test decision analysis with minimal transaction data."""
        result = self.analyzer.analyze_decision(
            decision_name="Test Purchase",
            decision_description="Minimal data test",
            purchase_price=1000,
            monthly_income=5000,
            monthly_expenses=3000,
            current_balance=10000,
            transactions=[],  # Empty
        )
        
        # Should still produce analysis even with minimal data
        assert result is not None
        assert "recommendation" in result


class TestIntegration:
    """Integration tests for Phase 4 components."""
    
    def test_full_decision_pipeline(self):
        """Test full decision analysis pipeline."""
        analyzer = DecisionAnalyzer()
        
        # Simulate realistic financial data
        transactions = [
            {
                "amount": -100 - (i % 10) * 20,
                "date": datetime.utcnow() - timedelta(days=i),
                "type": "expense",
            }
            for i in range(30)
        ] + [
            {
                "amount": 5000,
                "date": datetime.utcnow() - timedelta(days=i),
                "type": "income",
            }
            for i in range(0, 30, 30)
        ]
        
        # Analyze a realistic decision
        result = analyzer.analyze_decision(
            decision_name="iPhone 15 Pro",
            decision_description="New smartphone purchase",
            purchase_price=1200,
            monthly_income=5000,
            monthly_expenses=3000,
            current_balance=15000,
            recurring_expenses=2000,
            transactions=transactions,
            emergency_fund_months=6,
        )
        
        # Verify complete analysis
        assert result is not None
        assert "decision" in result
        assert "financial_snapshot" in result
        assert "affordability" in result
        assert "financial_impacts" in result
        assert "scenario_analysis" in result
        assert "recommendation" in result
        assert "assumptions" in result
    
    def test_scenario_comparison(self):
        """Test comparison of scenarios."""
        scenario_analyzer = ScenarioAnalyzer()
        
        scenarios = scenario_analyzer.generate_scenarios(
            monthly_income=5000,
            monthly_expenses=3000,
            current_balance=20000,
        )
        
        # Extract runways
        conservative_runway = next(
            s.projected_runway_months for s in scenarios 
            if s.type == ScenarioType.CONSERVATIVE
        )
        balanced_runway = next(
            s.projected_runway_months for s in scenarios 
            if s.type == ScenarioType.BALANCED
        )
        aggressive_runway = next(
            s.projected_runway_months for s in scenarios 
            if s.type == ScenarioType.AGGRESSIVE
        )
        
        # Verify ordering
        assert conservative_runway <= balanced_runway
        assert balanced_runway <= aggressive_runway


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
