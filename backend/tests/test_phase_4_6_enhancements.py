"""
Tests for Phase 4.6 enhancements:
- Inflation-adjusted forecasting
- Reasoning memory system
- Advanced scenarios
- Behavioral integration
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from app.ml.financial_reasoning.forecast_engine import (
    ForecastingEngine,
    InflationScenario,
)
from app.ml.financial_reasoning.advanced_scenarios import (
    EmploymentShockAnalyzer,
    TaxImpactAnalyzer,
    DebtScenarioAnalyzer,
    TaxRegime,
)
from app.ml.reasoning_memory.behavioral_integration import (
    BehavioralIntegrationEngine,
)


class TestForecastingEngine:
    """Tests for inflation-adjusted forecasting."""
    
    def setup_method(self):
        """Setup for each test."""
        self.engine = ForecastingEngine(country="US")
    
    def test_nominal_to_real_conversion(self):
        """Test converting nominal to real value."""
        today = datetime.utcnow()
        future = today + timedelta(days=365)
        
        metric = self.engine.nominal_to_real(
            nominal_amount=1000,
            start_date=today,
            end_date=future,
            inflation_scenario=InflationScenario.MODERATE,
        )
        
        assert metric.real_value < metric.nominal_value
        assert metric.purchasing_power_loss > 0
        assert metric.confidence > 0.7
    
    def test_real_to_nominal_conversion(self):
        """Test converting real to nominal value."""
        today = datetime.utcnow()
        future = today + timedelta(days=365)
        
        metric = self.engine.real_to_nominal(
            real_amount=1000,
            start_date=today,
            end_date=future,
            inflation_scenario=InflationScenario.MODERATE,
        )
        
        assert metric.nominal_value > metric.real_value
        assert metric.purchasing_power_loss > 0
    
    def test_inflation_adjusted_runway(self):
        """Test runway calculation with inflation."""
        result = self.engine.inflation_adjusted_runway(
            current_balance=10000,
            monthly_expenses=500,
            inflation_scenario=InflationScenario.MODERATE,
            months=60,
        )
        
        assert "nominal_runway_months" in result
        assert "real_runway_months" in result
        assert result["real_runway_months"] <= result["nominal_runway_months"]
    
    def test_purchase_affordability_inflation_adjusted(self):
        """Test purchase affordability with inflation."""
        result = self.engine.purchase_affordability_inflation_adjusted(
            purchase_price_today=1200,
            months_until_purchase=12,
            monthly_income=5000,
            monthly_expenses=3000,
            current_balance=5000,
        )
        
        assert "purchase_analysis" in result
        assert "savings_analysis" in result
        assert "affordability" in result
        assert "can_afford_nominal" in result["affordability"]


class TestEmploymentShockAnalyzer:
    """Tests for employment shock scenarios."""
    
    def setup_method(self):
        """Setup for each test."""
        self.analyzer = EmploymentShockAnalyzer()
    
    def test_job_loss_scenario(self):
        """Test job loss impact analysis."""
        scenario = self.analyzer.model_job_loss(
            current_monthly_income=5000,
            monthly_expenses=3000,
            current_balance=15000,
        )
        
        assert scenario.scenario_name == "Job Loss"
        assert scenario.scenario_type == "employment"
        assert scenario.runway_months > 0
        assert len(scenario.recommendations) > 0
    
    def test_salary_cut_scenario(self):
        """Test salary cut impact analysis."""
        scenario = self.analyzer.model_salary_cut(
            current_monthly_income=5000,
            monthly_expenses=3000,
            current_balance=10000,
            salary_reduction_percent=0.20,
            duration_months=6,
        )
        
        assert scenario.scenario_name == "20% Salary Cut for 6 Months"
        assert scenario.scenario_income < scenario.baseline_income


class TestTaxImpactAnalyzer:
    """Tests for tax impact analysis."""
    
    def setup_method(self):
        """Setup for each test."""
        self.us_analyzer = TaxImpactAnalyzer(TaxRegime.US)
        self.russia_analyzer = TaxImpactAnalyzer(TaxRegime.RUSSIA)
    
    def test_us_net_income_calculation(self):
        """Test US net income calculation."""
        result = self.us_analyzer.calculate_net_income(
            gross_income=50000,
            deductions=6000,
        )
        
        assert result["gross_income"] == 50000
        assert result["net_income"] < 50000
        assert result["effective_tax_rate"] > 0
    
    def test_russia_net_income_calculation(self):
        """Test Russian tax calculation."""
        result = self.russia_analyzer.calculate_net_income(
            gross_income=100000,
            deductions=0,
        )
        
        # Russia has 13% flat tax
        assert abs(result["effective_tax_rate"] - 0.13) < 0.01
    
    def test_income_tax_scenario(self):
        """Test tax scenario analysis."""
        scenario = self.us_analyzer.income_tax_scenario(
            current_gross_income=60000,
            monthly_expenses=3000,
            current_balance=15000,
            projected_income_change=0.20,  # 20% raise
        )
        
        assert scenario.scenario_income > scenario.baseline_income
        assert len(scenario.recommendations) > 0


class TestDebtScenarioAnalyzer:
    """Tests for debt scenarios."""
    
    def setup_method(self):
        """Setup for each test."""
        self.analyzer = DebtScenarioAnalyzer()
    
    def test_student_loan_scenario(self):
        """Test student loan impact."""
        scenario = self.analyzer.model_student_loan(
            loan_amount=100000,
            monthly_expenses=3000,
            monthly_income=5000,
            current_balance=5000,
        )
        
        assert scenario.scenario_type == "loan"
        assert scenario.scenario_expenses > scenario.baseline_expenses
        assert scenario.recovery_timeline_months == 120  # 10 years
    
    def test_credit_card_debt_scenario(self):
        """Test credit card debt impact."""
        scenario = self.analyzer.model_credit_card_debt(
            balance=5000,
            monthly_expenses=2000,
            monthly_income=4000,
            current_balance=1000,
        )
        
        assert scenario.scenario_type == "loan"
        assert scenario.stress_level == "high"
        assert scenario.recovery_timeline_months > 0


class TestBehavioralIntegration:
    """Tests for behavioral integration."""
    
    def setup_method(self):
        """Setup for each test."""
        self.engine = BehavioralIntegrationEngine()
    
    def test_behavioral_factors_extraction(self):
        """Test extracting behavioral factors from transactions."""
        transactions = [
            {"amount": 50, "date": datetime.utcnow() - timedelta(days=i), "category": "food"}
            for i in range(30)
        ]
        
        factors = self.engine.extract_behavioral_factors(transactions)
        
        assert factors.risk_tolerance_score > 0
        assert factors.impulse_spending_score >= 0
        assert factors.stress_spending_tendency >= 0
    
    def test_recommendation_adjustment(self):
        """Test behavioral adjustment of recommendations."""
        transactions = [
            {"amount": 100, "date": datetime.utcnow(), "category": "food"},
        ]
        
        factors = self.engine.extract_behavioral_factors(transactions)
        
        result = self.engine.adjust_decision_recommendation(
            base_recommendation="recommended",
            base_confidence=0.8,
            behavioral_factors=factors,
        )
        
        assert "adjusted_recommendation" in result
        assert "adjusted_confidence" in result
        assert "behavioral_notes" in result
    
    def test_behavioral_warning_level(self):
        """Test behavioral warning level assessment."""
        transactions = [
            {"amount": 20, "date": datetime.utcnow() - timedelta(days=i), "category": "misc"}
            for i in range(50)
        ]
        
        factors = self.engine.extract_behavioral_factors(transactions)
        warning_level = self.engine.get_behavioral_warning_level(factors)
        
        assert warning_level in ["low", "medium", "high"]
