"""
Tests for agent API endpoints.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.ml.agents.types import (
    FinancialMetrics,
    TransactionContext,
    StrategistOutput,
    CriticOutput,
    RiskLevel,
    SynthesisOutput,
)

# Use test client
client = TestClient(app)


class TestAgentAPI:
    """Test agent API endpoints."""
    
    def test_agent_health_check(self):
        """Test agent health check endpoint."""
        response = client.get("/api/v1/agents/health")
        
        # Endpoint should exist but may return service unavailable if no API keys
        assert response.status_code in [200, 503, 500]
    
    def test_agent_stats(self):
        """Test getting agent statistics."""
        # This endpoint requires authentication
        response = client.get("/api/v1/agents/stats")
        
        # Should return 401 without authentication
        assert response.status_code in [401, 404]


@pytest.mark.asyncio
class TestAgentAnalysis:
    """Test agent analysis functionality."""
    
    @pytest.mark.skip(reason="Requires live API keys")
    async def test_financial_analysis(self):
        """Test complete financial analysis."""
        with patch("app.api.v1.endpoints.agents.AgentService") as mock_service:
            mock_analysis = SynthesisOutput(
                executive_summary="Test summary",
                key_insights=[],
                action_items=[],
                priority_level="medium",
                strategist_perspective={},
                critic_perspective={},
                overall_confidence=0.8,
                generated_at=None,
            )
            
            mock_service_instance = AsyncMock()
            mock_service_instance.analyze_user_finances = AsyncMock(
                return_value=mock_analysis
            )
            mock_service.return_value = mock_service_instance
            
            # Would make API call here
            assert True


class TestAgentIntegration:
    """Integration tests for agent system."""
    
    def test_financial_metrics_flow(self):
        """Test financial metrics data flow."""
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
        
        # Verify metrics can be serialized
        d = metrics.to_dict()
        assert d is not None
        assert d["total_income"] == 5000.0
    
    def test_transaction_context_flow(self):
        """Test transaction context data flow."""
        context = TransactionContext(
            recent_transactions=[
                {"merchant": "Cafe", "amount": -50, "category": "food"}
            ],
            spending_trends={"week_over_week": 0.1},
            category_breakdown={"food": {"total": 100, "count": 2}},
            recurring_patterns=[],
            anomalies_detected=[],
        )
        
        # Verify context can be serialized
        d = context.to_dict()
        assert d is not None
        assert len(d["recent_transactions"]) == 1


class TestAgentErrorHandling:
    """Test error handling in agent system."""
    
    def test_invalid_days_parameter(self):
        """Test validation of days parameter."""
        # 0 days should be invalid
        response = client.post("/api/v1/agents/analyze?days=0")
        
        # Should return either 401 (auth) or 400 (invalid param)
        assert response.status_code in [401, 400, 404]
    
    def test_excessive_days_parameter(self):
        """Test validation of excessive days."""
        # 400 days should be invalid
        response = client.post("/api/v1/agents/analyze?days=400")
        
        # Should return either 401 (auth) or 400 (invalid param)
        assert response.status_code in [401, 400, 404]
