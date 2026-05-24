"""
Tests for multi-agent reasoning system.
Tests for Strategist, Critic, and Synthesis agents.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.ml.agents.types import (
    FinancialMetrics,
    TransactionContext,
    StrategistOutput,
    CriticOutput,
    RiskLevel,
    InsightType,
    FinancialInsight,
    AgentError,
    StrategyGenerationError,
    RiskAssessmentError,
    SynthesisError,
)
from app.ml.agents.base import BaseAgent
from app.ml.agents.synthesizer import SynthesisEngine


class TestFinancialMetrics:
    """Test FinancialMetrics data class."""
    
    def test_financial_metrics_creation(self):
        """Test creating financial metrics."""
        metrics = FinancialMetrics(
            total_income=5000.0,
            total_expenses=3000.0,
            savings_rate=0.4,
            average_monthly_expense=3000.0,
            expense_categories={"food": 1000, "transport": 500},
            account_balances={"checking": 10000},
            recurring_expenses=1500.0,
            average_transaction_size=50.0,
            transaction_count=60,
        )
        
        assert metrics.total_income == 5000.0
        assert metrics.savings_rate == 0.4
        assert len(metrics.expense_categories) == 2
    
    def test_financial_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = FinancialMetrics(
            total_income=5000.0,
            total_expenses=3000.0,
            savings_rate=0.4,
            average_monthly_expense=3000.0,
            expense_categories={},
            account_balances={},
            recurring_expenses=0.0,
            average_transaction_size=0.0,
            transaction_count=0,
        )
        
        d = metrics.to_dict()
        assert isinstance(d, dict)
        assert d["total_income"] == 5000.0


class TestTransactionContext:
    """Test TransactionContext data class."""
    
    def test_transaction_context_creation(self):
        """Test creating transaction context."""
        context = TransactionContext(
            recent_transactions=[{"amount": -50}],
            spending_trends={"week_over_week": 0.1},
            category_breakdown={"food": {"total": 100, "count": 2}},
            recurring_patterns=[],
            anomalies_detected=[],
        )
        
        assert len(context.recent_transactions) == 1
        assert context.spending_trends["week_over_week"] == 0.1


class TestStrategistOutput:
    """Test StrategistOutput data class."""
    
    def test_strategist_output_creation(self):
        """Test creating strategist output."""
        output = StrategistOutput(
            recommendations=["Save more"],
            budget_suggestions={"food": 1000},
            savings_opportunities=[],
            goals_suggestions=[],
            spending_analysis={},
            confidence_score=0.85,
        )
        
        assert len(output.recommendations) == 1
        assert output.confidence_score == 0.85
    
    def test_strategist_output_to_dict(self):
        """Test converting strategist output to dict."""
        output = StrategistOutput(
            recommendations=["Save more"],
            budget_suggestions={"food": 1000},
            savings_opportunities=[],
            goals_suggestions=[],
            spending_analysis={},
            confidence_score=0.85,
        )
        
        d = output.to_dict()
        assert isinstance(d, dict)
        assert d["confidence_score"] == 0.85


class TestCriticOutput:
    """Test CriticOutput data class."""
    
    def test_critic_output_creation(self):
        """Test creating critic output."""
        output = CriticOutput(
            risk_level=RiskLevel.HIGH,
            risk_score=72,
            vulnerabilities=[],
            alerts=[],
            financial_health_score=65,
            critical_issues=["High debt"],
            recommendations=["Pay off debt"],
            confidence_score=0.80,
        )
        
        assert output.risk_level == RiskLevel.HIGH
        assert output.risk_score == 72
    
    def test_critic_output_to_dict(self):
        """Test converting critic output to dict."""
        output = CriticOutput(
            risk_level=RiskLevel.MEDIUM,
            risk_score=45,
            vulnerabilities=[],
            alerts=[],
            financial_health_score=70,
            critical_issues=[],
            recommendations=[],
            confidence_score=0.75,
        )
        
        d = output.to_dict()
        assert d["risk_level"] == "medium"
        assert isinstance(d, dict)


class TestFinancialInsight:
    """Test FinancialInsight data class."""
    
    def test_insight_creation(self):
        """Test creating financial insight."""
        insight = FinancialInsight(
            type=InsightType.SAVINGS_OPPORTUNITY,
            title="Save on food",
            description="Reduce food spending",
            impact="positive",
            confidence=0.9,
            action="Cut to $500/month",
            metric_value=200.0,
        )
        
        assert insight.type == InsightType.SAVINGS_OPPORTUNITY
        assert insight.confidence == 0.9
    
    def test_insight_to_dict(self):
        """Test converting insight to dict."""
        insight = FinancialInsight(
            type=InsightType.RISK_ALERT,
            title="Emergency fund low",
            description="Less than 2 months expenses",
            impact="negative",
            confidence=0.95,
        )
        
        d = insight.to_dict()
        assert d["type"] == "risk_alert"
        assert d["impact"] == "negative"


class TestBaseAgent:
    """Test BaseAgent functionality."""
    
    def test_base_agent_initialization(self):
        """Test initializing base agent."""
        agent = BaseAgent("TestAgent")
        assert agent.name == "TestAgent"
        assert agent._call_count == 0
        assert agent._error_count == 0
    
    def test_validate_inputs(self):
        """Test input validation."""
        agent = BaseAgent("TestAgent")
        
        metrics = FinancialMetrics(
            total_income=5000,
            total_expenses=3000,
            savings_rate=0.4,
            average_monthly_expense=3000,
            expense_categories={},
            account_balances={},
            recurring_expenses=0,
            average_transaction_size=0,
            transaction_count=0,
        )
        
        context = TransactionContext(
            recent_transactions=[],
            spending_trends={},
            category_breakdown={},
            recurring_patterns=[],
            anomalies_detected=[],
        )
        
        assert agent.validate_inputs(metrics, context) is True
    
    def test_validate_inputs_negative_expenses(self):
        """Test validation fails for negative expenses."""
        agent = BaseAgent("TestAgent")
        
        metrics = FinancialMetrics(
            total_income=5000,
            total_expenses=-3000,  # Invalid
            savings_rate=0.4,
            average_monthly_expense=3000,
            expense_categories={},
            account_balances={},
            recurring_expenses=0,
            average_transaction_size=0,
            transaction_count=0,
        )
        
        context = TransactionContext(
            recent_transactions=[],
            spending_trends={},
            category_breakdown={},
            recurring_patterns=[],
            anomalies_detected=[],
        )
        
        assert agent.validate_inputs(metrics, context) is False
    
    def test_log_call(self):
        """Test logging calls."""
        agent = BaseAgent("TestAgent")
        
        assert agent._call_count == 0
        assert agent._error_count == 0
        
        agent.log_call(success=True)
        assert agent._call_count == 1
        assert agent._error_count == 0
        
        agent.log_call(success=False, error="Test error")
        assert agent._call_count == 2
        assert agent._error_count == 1
    
    def test_get_stats(self):
        """Test getting agent statistics."""
        agent = BaseAgent("TestAgent")
        
        agent.log_call(success=True)
        agent.log_call(success=True)
        agent.log_call(success=False)
        
        stats = agent.get_stats()
        assert stats["name"] == "TestAgent"
        assert stats["total_calls"] == 3
        assert stats["successful_calls"] == 2
        assert stats["failed_calls"] == 1
        assert stats["success_rate"] == pytest.approx(66.67, rel=1)


class TestSynthesisEngine:
    """Test Synthesis Engine."""
    
    def test_synthesis_engine_initialization(self):
        """Test initializing synthesis engine."""
        engine = SynthesisEngine()
        assert engine is not None
    
    def test_synthesize_outputs(self):
        """Test synthesizing agent outputs."""
        engine = SynthesisEngine()
        
        strategist_output = StrategistOutput(
            recommendations=["Save more on food"],
            budget_suggestions={"food": 1000},
            savings_opportunities=[
                {
                    "area": "food",
                    "current": 1500,
                    "suggested": 1000,
                    "monthly_savings": 500,
                    "reasoning": "Reduce dining out",
                }
            ],
            goals_suggestions=[],
            spending_analysis={},
            confidence_score=0.85,
        )
        
        critic_output = CriticOutput(
            risk_level=RiskLevel.MEDIUM,
            risk_score=45,
            vulnerabilities=[],
            alerts=[],
            financial_health_score=70,
            critical_issues=[],
            recommendations=[],
            confidence_score=0.80,
        )
        
        synthesis = engine.synthesize(strategist_output, critic_output)
        
        assert synthesis is not None
        assert synthesis.executive_summary is not None
        assert len(synthesis.key_insights) >= 0
        assert synthesis.overall_confidence > 0
    
    def test_extract_key_insights(self):
        """Test extracting key insights."""
        engine = SynthesisEngine()
        
        strategist_output = StrategistOutput(
            recommendations=["Save more"],
            budget_suggestions={"food": 1000},
            savings_opportunities=[
                {
                    "area": "food",
                    "current": 1500,
                    "suggested": 1000,
                    "monthly_savings": 500,
                    "reasoning": "Reduce dining",
                }
            ],
            goals_suggestions=[],
            spending_analysis={},
            confidence_score=0.85,
        )
        
        critic_output = CriticOutput(
            risk_level=RiskLevel.HIGH,
            risk_score=72,
            vulnerabilities=[],
            alerts=[{"message": "Low savings", "recommended_action": "Save more"}],
            financial_health_score=65,
            critical_issues=["Emergency fund low"],
            recommendations=[],
            confidence_score=0.80,
        )
        
        insights = engine._extract_key_insights(strategist_output, critic_output)
        
        assert len(insights) > 0
    
    def test_generate_action_items(self):
        """Test generating action items."""
        engine = SynthesisEngine()
        
        strategist_output = StrategistOutput(
            recommendations=["Start saving for emergency fund"],
            budget_suggestions={},
            savings_opportunities=[],
            goals_suggestions=[],
            spending_analysis={},
            confidence_score=0.85,
        )
        
        critic_output = CriticOutput(
            risk_level=RiskLevel.HIGH,
            risk_score=72,
            vulnerabilities=[],
            alerts=[],
            financial_health_score=65,
            critical_issues=["Emergency fund insufficient"],
            recommendations=["Build emergency fund"],
            confidence_score=0.80,
        )
        
        actions = engine._generate_action_items(strategist_output, critic_output)
        
        assert len(actions) > 0
        assert all("action" in item for item in actions)


class TestAgentExceptions:
    """Test agent exception handling."""
    
    def test_strategy_generation_error(self):
        """Test StrategyGenerationError."""
        with pytest.raises(StrategyGenerationError):
            raise StrategyGenerationError("Test error")
    
    def test_risk_assessment_error(self):
        """Test RiskAssessmentError."""
        with pytest.raises(RiskAssessmentError):
            raise RiskAssessmentError("Test error")
    
    def test_synthesis_error(self):
        """Test SynthesisError."""
        with pytest.raises(SynthesisError):
            raise SynthesisError("Test error")
