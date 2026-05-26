"""
Tests for Phase 4.2 agent database models.
Tests AgentReport, FinancialInsight, and RiskAssessment models.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.database import (
    User,
    AgentReport,
    FinancialInsight,
    RiskAssessment,
)
from app.db.base import SessionLocal, engine


@pytest.fixture
def db_session():
    """Create a test database session."""
    from app.models.database import Base
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestAgentReportModel:
    """Tests for AgentReport model."""
    
    def test_create_agent_report(self, db_session: Session, test_user: User):
        """Test creating an agent report."""
        now = datetime.utcnow()
        
        report = AgentReport(
            user_id=test_user.id,
            report_type="full_analysis",
            period_start=now - timedelta(days=30),
            period_end=now,
            executive_summary="Test summary",
            priority_level="high",
            overall_confidence=0.95,
            strategist_perspective={
                "recommendations": ["Save more"],
                "confidence_score": 0.9,
            },
            critic_perspective={
                "risk_level": "medium",
                "risk_score": 65.0,
                "confidence_score": 0.92,
            },
            key_insights=[],
            action_items=[],
            transaction_count=50,
            is_reviewed=False,
        )
        
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)
        
        assert report.id is not None
        assert report.user_id == test_user.id
        assert report.executive_summary == "Test summary"
        assert report.priority_level == "high"
        assert report.overall_confidence == 0.95
        assert report.created_at is not None
    
    def test_agent_report_user_relationship(self, db_session: Session, test_user: User):
        """Test user-report relationship."""
        now = datetime.utcnow()
        
        report1 = AgentReport(
            user_id=test_user.id,
            report_type="full_analysis",
            period_start=now - timedelta(days=30),
            period_end=now,
            executive_summary="Report 1",
            priority_level="high",
            overall_confidence=0.95,
            strategist_perspective={},
            critic_perspective={},
        )
        
        report2 = AgentReport(
            user_id=test_user.id,
            report_type="risk_only",
            period_start=now - timedelta(days=7),
            period_end=now,
            executive_summary="Report 2",
            priority_level="critical",
            overall_confidence=0.88,
            strategist_perspective={},
            critic_perspective={},
        )
        
        db_session.add_all([report1, report2])
        db_session.commit()
        
        # Refresh user to load relationships
        db_session.refresh(test_user)
        
        assert len(test_user.agent_reports) == 2
        assert all(r.user_id == test_user.id for r in test_user.agent_reports)
    
    def test_agent_report_with_insights(self, db_session: Session, test_user: User):
        """Test agent report with associated insights."""
        now = datetime.utcnow()
        
        report = AgentReport(
            user_id=test_user.id,
            report_type="full_analysis",
            period_start=now - timedelta(days=30),
            period_end=now,
            executive_summary="Test summary",
            priority_level="high",
            overall_confidence=0.95,
            strategist_perspective={},
            critic_perspective={},
        )
        
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)
        
        # Create insights linked to report
        insight = FinancialInsight(
            user_id=test_user.id,
            report_id=report.id,
            insight_type="spending_pattern",
            impact="positive",
            title="High spending on groceries",
            description="You spend more on groceries than average",
            confidence=0.85,
            priority=1,
        )
        
        db_session.add(insight)
        db_session.commit()
        
        # Verify relationship
        db_session.refresh(report)
        assert len(report.insights) == 1
        assert report.insights[0].title == "High spending on groceries"


class TestFinancialInsightModel:
    """Tests for FinancialInsight model."""
    
    def test_create_financial_insight(self, db_session: Session, test_user: User):
        """Test creating a financial insight."""
        insight = FinancialInsight(
            user_id=test_user.id,
            insight_type="budget_optimization",
            impact="positive",
            title="Reduce monthly subscriptions",
            description="You have 5 unused subscriptions",
            metric_value=Decimal("150.00"),
            metric_unit="USD",
            confidence=0.92,
            action="Cancel unused subscriptions",
            priority=2,
            is_acknowledged=False,
        )
        
        db_session.add(insight)
        db_session.commit()
        db_session.refresh(insight)
        
        assert insight.id is not None
        assert insight.user_id == test_user.id
        assert insight.insight_type == "budget_optimization"
        assert insight.impact == "positive"
        assert insight.confidence == 0.92
        assert insight.is_acknowledged is False
    
    def test_acknowledge_insight(self, db_session: Session, test_user: User):
        """Test acknowledging an insight."""
        insight = FinancialInsight(
            user_id=test_user.id,
            insight_type="savings_opportunity",
            impact="positive",
            title="Save on streaming services",
            description="Consider consolidating streaming subscriptions",
            confidence=0.87,
            is_acknowledged=False,
        )
        
        db_session.add(insight)
        db_session.commit()
        db_session.refresh(insight)
        
        # Acknowledge the insight
        insight.is_acknowledged = True
        insight.acknowledged_at = datetime.utcnow()
        db_session.commit()
        
        db_session.refresh(insight)
        assert insight.is_acknowledged is True
        assert insight.acknowledged_at is not None
    
    def test_insight_types(self, db_session: Session, test_user: User):
        """Test different insight types."""
        insight_types = [
            "spending_pattern",
            "budget_optimization",
            "savings_opportunity",
            "risk_alert",
            "goal_suggestion",
            "financial_health",
            "anomaly_detected",
            "recommendation",
        ]
        
        insights = []
        for insight_type in insight_types:
            insight = FinancialInsight(
                user_id=test_user.id,
                insight_type=insight_type,
                impact="neutral",
                title=f"Test {insight_type}",
                description=f"Description for {insight_type}",
                confidence=0.8,
            )
            insights.append(insight)
        
        db_session.add_all(insights)
        db_session.commit()
        
        # Verify all insights created
        all_insights = db_session.query(FinancialInsight).filter_by(
            user_id=test_user.id
        ).all()
        assert len(all_insights) == len(insight_types)


class TestRiskAssessmentModel:
    """Tests for RiskAssessment model."""
    
    def test_create_risk_assessment(self, db_session: Session, test_user: User):
        """Test creating a risk assessment."""
        assessment = RiskAssessment(
            user_id=test_user.id,
            risk_level="high",
            risk_score=75.0,
            financial_health_score=45.0,
            title="High expense volatility",
            description="Your spending varies significantly month to month",
            vulnerabilities=[
                {"type": "high_variance", "severity": "medium"},
            ],
            alerts=[
                {"alert": "Unusual spending pattern detected", "severity": "high"},
            ],
            critical_issues=["Potential cash flow issue"],
            recommendations=[
                "Create an emergency fund",
                "Track spending more carefully",
            ],
            confidence=0.88,
            is_acknowledged=False,
        )
        
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)
        
        assert assessment.id is not None
        assert assessment.user_id == test_user.id
        assert assessment.risk_level == "high"
        assert assessment.risk_score == 75.0
        assert assessment.financial_health_score == 45.0
        assert len(assessment.vulnerabilities) == 1
        assert len(assessment.alerts) == 1
        assert len(assessment.critical_issues) == 1
        assert len(assessment.recommendations) == 2
    
    def test_risk_levels(self, db_session: Session, test_user: User):
        """Test different risk levels."""
        risk_levels = ["low", "medium", "high", "critical"]
        
        assessments = []
        for idx, risk_level in enumerate(risk_levels):
            assessment = RiskAssessment(
                user_id=test_user.id,
                risk_level=risk_level,
                risk_score=float(25 * (idx + 1)),
                financial_health_score=100.0 - (25 * idx),
                title=f"Risk: {risk_level}",
                description=f"Assessment with {risk_level} risk",
                confidence=0.85,
            )
            assessments.append(assessment)
        
        db_session.add_all(assessments)
        db_session.commit()
        
        # Verify all assessments
        all_assessments = db_session.query(RiskAssessment).filter_by(
            user_id=test_user.id
        ).all()
        assert len(all_assessments) == len(risk_levels)
    
    def test_acknowledge_risk_assessment(self, db_session: Session, test_user: User):
        """Test acknowledging a risk assessment."""
        assessment = RiskAssessment(
            user_id=test_user.id,
            risk_level="medium",
            risk_score=55.0,
            financial_health_score=60.0,
            title="Moderate financial risk",
            description="Some financial vulnerabilities detected",
            confidence=0.82,
            is_acknowledged=False,
        )
        
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)
        
        # Acknowledge with mitigation actions
        assessment.is_acknowledged = True
        assessment.acknowledged_at = datetime.utcnow()
        assessment.mitigation_actions = {
            "actions": ["Increase emergency fund", "Reduce unnecessary spending"],
            "target_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
        db_session.commit()
        
        db_session.refresh(assessment)
        assert assessment.is_acknowledged is True
        assert assessment.acknowledged_at is not None
        assert assessment.mitigation_actions is not None
        assert "actions" in assessment.mitigation_actions


class TestReportInsightRiskRelationships:
    """Test relationships between Report, Insight, and RiskAssessment."""
    
    def test_report_cascade_delete_insights(self, db_session: Session, test_user: User):
        """Test that deleting report cascades to insights."""
        now = datetime.utcnow()
        
        report = AgentReport(
            user_id=test_user.id,
            report_type="full_analysis",
            period_start=now - timedelta(days=30),
            period_end=now,
            executive_summary="Test",
            priority_level="high",
            overall_confidence=0.95,
            strategist_perspective={},
            critic_perspective={},
        )
        
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)
        
        insight = FinancialInsight(
            user_id=test_user.id,
            report_id=report.id,
            insight_type="spending_pattern",
            impact="neutral",
            title="Test",
            description="Test",
            confidence=0.8,
        )
        
        db_session.add(insight)
        db_session.commit()
        
        report_id = report.id
        insight_id = insight.id
        
        # Delete report
        db_session.delete(report)
        db_session.commit()
        
        # Verify insight is also deleted
        deleted_insight = db_session.query(FinancialInsight).filter_by(
            id=insight_id
        ).first()
        assert deleted_insight is None
    
    def test_report_with_multiple_insights_and_risks(self, db_session: Session, test_user: User):
        """Test report with multiple insights and risk assessments."""
        now = datetime.utcnow()
        
        report = AgentReport(
            user_id=test_user.id,
            report_type="full_analysis",
            period_start=now - timedelta(days=30),
            period_end=now,
            executive_summary="Comprehensive analysis",
            priority_level="high",
            overall_confidence=0.93,
            strategist_perspective={"recommendations": ["Save more"]},
            critic_perspective={"risk_level": "medium"},
        )
        
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)
        
        # Add multiple insights
        for i in range(3):
            insight = FinancialInsight(
                user_id=test_user.id,
                report_id=report.id,
                insight_type="spending_pattern",
                impact="neutral",
                title=f"Insight {i}",
                description=f"Description {i}",
                confidence=0.8,
            )
            db_session.add(insight)
        
        # Add risk assessments
        for i in range(2):
            risk = RiskAssessment(
                user_id=test_user.id,
                report_id=report.id,
                risk_level="medium" if i == 0 else "low",
                risk_score=60.0 if i == 0 else 30.0,
                financial_health_score=70.0,
                title=f"Risk {i}",
                description=f"Risk assessment {i}",
                confidence=0.85,
            )
            db_session.add(risk)
        
        db_session.commit()
        
        # Verify relationships
        db_session.refresh(report)
        assert len(report.insights) == 3
        assert len(report.risk_assessments) == 2


class TestIndexing:
    """Test that indexes are properly set up for performance."""
    
    def test_agent_report_indexes(self, db_session: Session):
        """Test that agent report has proper indexes."""
        from sqlalchemy import inspect
        
        mapper = inspect(AgentReport)
        indexes = {idx.name: idx.expressions for idx in mapper.indexes}
        
        # Check for important indexes
        assert any('user_id' in str(idx) for idx in mapper.indexes), "user_id should be indexed"
        assert any('created_at' in str(idx) for idx in mapper.indexes), "created_at should be indexed"
        assert any('period_start' in str(idx) or 'period_end' in str(idx) 
                  for idx in mapper.indexes), "period dates should be indexed"
    
    def test_financial_insight_indexes(self, db_session: Session):
        """Test that financial insight has proper indexes."""
        from sqlalchemy import inspect
        
        mapper = inspect(FinancialInsight)
        
        # Check for important indexes
        assert any('user_id' in str(idx) for idx in mapper.indexes), "user_id should be indexed"
        assert any('insight_type' in str(idx) for idx in mapper.indexes), "insight_type should be indexed"
        assert any('created_at' in str(idx) for idx in mapper.indexes), "created_at should be indexed"
    
    def test_risk_assessment_indexes(self, db_session: Session):
        """Test that risk assessment has proper indexes."""
        from sqlalchemy import inspect
        
        mapper = inspect(RiskAssessment)
        
        # Check for important indexes
        assert any('user_id' in str(idx) for idx in mapper.indexes), "user_id should be indexed"
        assert any('risk_level' in str(idx) for idx in mapper.indexes), "risk_level should be indexed"
        assert any('created_at' in str(idx) for idx in mapper.indexes), "created_at should be indexed"
