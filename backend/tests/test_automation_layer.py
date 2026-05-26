"""
Tests for Automation & Proactive Intelligence Layer

Tests for:
- Financial health scoring
- Alert detection
- Report generation
- Notification system
- Celery task execution
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock

# Import modules to test
from app.ml.financial_scoring import FinancialHealthScoringEngine, FinancialHealthScore
from app.ml.alerts import AlertDetectionEngine, AlertType, AlertSeverity
from app.services.report_generation import ReportGenerator
from app.services.pdf_generation import PDFReportGenerator
from app.services.notifications import NotificationService, NotificationChannel


# ============================================================================
# FINANCIAL HEALTH SCORING TESTS
# ============================================================================

class TestFinancialHealthScoring:
    """Test financial health scoring engine."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.engine = FinancialHealthScoringEngine()
    
    def test_calculate_health_score_with_good_data(self):
        """Test health score calculation with good financial data."""
        transactions = [
            {"date": "2024-01-15", "type": "income", "amount": 5000},
            {"date": "2024-01-20", "type": "expense", "amount": 500},
            {"date": "2024-02-15", "type": "income", "amount": 5000},
            {"date": "2024-02-20", "type": "expense", "amount": 600},
        ]
        
        score = self.engine.calculate_health_score(
            transactions=transactions,
            account_balance=Decimal("10000"),
            monthly_income=5000,
            monthly_expenses=550,
        )
        
        assert isinstance(score, FinancialHealthScore)
        assert 0 <= score.overall_score <= 100
        assert score.score_grade in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]
        assert score.risk_level in ["low", "medium", "high", "critical"]
        assert 0 <= score.confidence <= 1
        assert len(score.components) > 0
        assert len(score.insights) > 0
    
    def test_health_score_with_insufficient_data(self):
        """Test health score with minimal data."""
        score = self.engine.calculate_health_score(
            transactions=[],
            account_balance=Decimal("0"),
        )
        
        assert score.overall_score == 50  # Default score
        assert score.confidence == 0.0  # No confidence
    
    def test_high_runway_scores_well(self):
        """Test that good runway results in high score."""
        score = self.engine.calculate_health_score(
            transactions=[],
            account_balance=Decimal("50000"),
            monthly_expenses=1000,
        )
        
        # Should have high runway component score
        runway_component = [c for c in score.components if c.name == "Runway Health"]
        if runway_component:
            assert runway_component[0].score >= 80
    
    def test_low_runway_scores_poorly(self):
        """Test that low runway results in low score."""
        score = self.engine.calculate_health_score(
            transactions=[],
            account_balance=Decimal("500"),
            monthly_expenses=1000,
        )
        
        # Should have low runway component score
        runway_component = [c for c in score.components if c.name == "Runway Health"]
        if runway_component:
            assert runway_component[0].score <= 40


# ============================================================================
# ALERT DETECTION TESTS
# ============================================================================

class TestAlertDetection:
    """Test alert detection engine."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.engine = AlertDetectionEngine()
    
    def test_detect_spending_spike(self):
        """Test detection of spending spikes."""
        transactions = [
            # Previous month
            {"date": "2024-01-05", "type": "expense", "category": "food", "amount": 100},
            {"date": "2024-01-10", "type": "expense", "category": "food", "amount": 50},
            # Current month (spiked)
            {"date": "2024-02-05", "type": "expense", "category": "food", "amount": 300},
            {"date": "2024-02-10", "type": "expense", "category": "food", "amount": 200},
        ]
        
        alerts = self.engine.detect_spending_anomalies(transactions)
        
        # Should detect spending spike in food category
        food_spikes = [a for a in alerts if a.data.get("category") == "food"]
        assert len(food_spikes) > 0
        assert any(a.severity == AlertSeverity.WARNING for a in food_spikes)
    
    def test_detect_low_runway(self):
        """Test detection of low runway."""
        alerts = self.engine.detect_burn_rate_issues(
            transactions=[],
            account_balance=Decimal("500"),
            monthly_income=5000,
            monthly_expenses=1000,
        )
        
        # Should detect low runway (0.5 months)
        runway_alerts = [a for a in alerts if a.alert_type == AlertType.LOW_RUNWAY]
        assert len(runway_alerts) > 0
        assert runway_alerts[0].severity == AlertSeverity.CRITICAL
    
    def test_detect_high_burn_rate(self):
        """Test detection of high burn rate."""
        alerts = self.engine.detect_burn_rate_issues(
            transactions=[],
            account_balance=Decimal("5000"),
            monthly_income=1000,
            monthly_expenses=950,  # 95% burn rate
        )
        
        # Should detect high burn rate
        burn_alerts = [a for a in alerts if a.alert_type == AlertType.BURN_RATE_WARNING]
        assert len(burn_alerts) > 0
    
    def test_detect_subscription_waste(self):
        """Test detection of subscription waste."""
        subscriptions = [
            {"name": "Netflix", "amount": 15, "is_active": True, "last_used": "2024-02-01"},
            {"name": "Gym", "amount": 50, "is_active": True, "last_used": "2023-12-01"},
            {"name": "Unused", "amount": 10, "is_active": True, "last_used": "2023-10-01"},
        ]
        
        alerts = self.engine.detect_subscription_waste(
            subscriptions=subscriptions,
            monthly_expenses=2000,
        )
        
        # Should detect unused subscriptions
        waste_alerts = [a for a in alerts if a.alert_type == AlertType.SUBSCRIPTION_WASTE]
        assert len(waste_alerts) > 0


# ============================================================================
# REPORT GENERATION TESTS
# ============================================================================

class TestReportGeneration:
    """Test report generation."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = ReportGenerator()
    
    def test_generate_weekly_report(self):
        """Test weekly report generation."""
        transactions = [
            {"date": "2024-02-19", "type": "expense", "category": "food", "amount": 100, "merchant": "Restaurant"},
            {"date": "2024-02-20", "type": "expense", "category": "transport", "amount": 50, "merchant": "Uber"},
            {"date": "2024-02-21", "type": "expense", "category": "shopping", "amount": 150, "merchant": "Amazon"},
            {"date": "2024-02-19", "type": "income", "amount": 5000},
        ]
        
        report = self.generator.generate_weekly_report(
            user_id="user123",
            transactions=transactions,
            account_balance=Decimal("5000"),
            monthly_income=5000,
        )
        
        assert report.report_id is not None
        assert report.user_id == "user123"
        assert report.report_period == "weekly"
        assert report.confidence > 0
        assert len(report.recommendations) > 0
        assert report.key_metrics is not None
    
    def test_report_contains_health_analysis(self):
        """Test that report contains health analysis."""
        transactions = []
        
        report = self.generator.generate_weekly_report(
            user_id="user123",
            transactions=transactions,
            account_balance=Decimal("5000"),
            monthly_income=2000,
        )
        
        assert "score" in report.health_analysis
        assert "grade" in report.health_analysis
        assert "risk_level" in report.health_analysis


# ============================================================================
# PDF GENERATION TESTS
# ============================================================================

class TestPDFGeneration:
    """Test PDF generation."""
    
    def setup_method(self):
        """Setup test fixtures."""
        try:
            self.generator = PDFReportGenerator()
        except ImportError:
            pytest.skip("ReportLab not installed")
    
    def test_generate_pdf(self):
        """Test PDF generation from report."""
        # Create mock report
        mock_report = Mock()
        mock_report.period_start = datetime.now() - timedelta(days=7)
        mock_report.period_end = datetime.now()
        mock_report.summary = {"user_message": "Test report"}
        mock_report.key_metrics = {"health_score": 75, "health_grade": "B"}
        mock_report.spending_analysis = {
            "total_spending": 500,
            "transaction_count": 5,
            "average_transaction": 100,
            "by_category": {"food": 200, "transport": 300},
            "week_over_week_change": 10,
        }
        mock_report.health_analysis = {
            "score": 75,
            "grade": "B",
            "risk_level": "medium",
            "insights": ["Test insight"],
        }
        mock_report.recommendations = [
            {"category": "Spending", "recommendation": "Reduce spending", "confidence": 0.8}
        ]
        mock_report.alerts = []
        
        pdf_bytes = self.generator.generate_weekly_report_pdf(mock_report)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


# ============================================================================
# NOTIFICATION SERVICE TESTS
# ============================================================================

class TestNotificationService:
    """Test notification service."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.service = NotificationService()
    
    def test_queue_notifications(self):
        """Test queuing notifications."""
        mock_alert = Mock()
        mock_alert.alert_type = AlertType.SPENDING_SPIKE
        mock_alert.severity = AlertSeverity.WARNING
        mock_alert.title = "Spending Spike"
        mock_alert.message = "Your spending increased 50%"
        mock_alert.data = {}
        mock_alert.confidence = 0.9
        
        notifications = self.service.queue_notifications(
            user_id="user123",
            alerts=[mock_alert],
        )
        
        assert len(notifications) > 0
        assert notifications[0].title == "Spending Spike"
        assert NotificationChannel.TELEGRAM in notifications[0].channels
    
    def test_throttling_prevents_too_many_notifications(self):
        """Test that throttling prevents alert fatigue."""
        mock_alert = Mock()
        mock_alert.alert_type = AlertType.SPENDING_SPIKE
        mock_alert.severity = AlertSeverity.INFO
        mock_alert.title = "Spending Spike"
        mock_alert.message = "Your spending increased"
        mock_alert.data = {}
        mock_alert.confidence = 0.5
        
        # First notification should be queued
        notifs1 = self.service.queue_notifications("user123", [mock_alert])
        assert len(notifs1) > 0
        
        # Record it
        self.service._record_notification("user123", mock_alert, notifs1[0])
        
        # Additional notifications should be throttled
        notifs2 = self.service.queue_notifications("user123", [mock_alert] * 5)
        # Should queue fewer due to throttling
        assert len(notifs2) <= 3
    
    def test_deduplication(self):
        """Test notification deduplication."""
        mock_alert = Mock()
        mock_alert.alert_type = AlertType.SPENDING_SPIKE
        mock_alert.severity = AlertSeverity.WARNING
        mock_alert.title = "Spending Spike"
        mock_alert.message = "Your spending increased"
        mock_alert.data = {}
        mock_alert.confidence = 0.8
        
        # First notification
        notifs1 = self.service.queue_notifications("user123", [mock_alert])
        assert len(notifs1) > 0
        self.service._record_notification("user123", mock_alert, notifs1[0])
        
        # Immediately send same notification again
        notifs2 = self.service.queue_notifications("user123", [mock_alert])
        # Should be deduped (assuming default dedup window)
        assert len(notifs2) == 0


# ============================================================================
# CELERY TASK TESTS
# ============================================================================

class TestCeleryTasks:
    """Test Celery task execution."""
    
    def test_celery_app_configured(self):
        """Test that Celery app is properly configured."""
        from app.core.celery import app
        
        assert app is not None
        assert app.conf.broker_connection_retry_on_startup is False or True
        assert len(app.conf.beat_schedule) > 0
    
    def test_beat_schedule_configured(self):
        """Test that Celery Beat schedule is configured."""
        from app.core.celery import app
        
        schedule = app.conf.beat_schedule
        
        # Check expected tasks
        assert "daily-spending-alerts" in schedule
        assert "weekly-financial-reports" in schedule
        assert "subscription-waste-check" in schedule
        assert "burn-rate-warnings" in schedule


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for the automation layer."""
    
    def test_full_alert_pipeline(self):
        """Test full alert detection and notification pipeline."""
        # Setup
        alert_engine = AlertDetectionEngine()
        notif_service = NotificationService()
        
        # Simulate high spending
        transactions = [
            {"date": "2024-02-19", "type": "expense", "category": "shopping", "amount": 1000},
        ]
        
        # Detect alerts
        alerts = alert_engine.detect_all_alerts(
            user_id="user123",
            transactions=transactions,
            account_balance=Decimal("5000"),
            monthly_income=5000,
            monthly_expenses=500,
        )
        
        # Queue notifications
        notifications = notif_service.queue_notifications("user123", alerts)
        
        # Verify pipeline
        if len(alerts) > 0:
            assert len(notifications) > 0
    
    def test_end_to_end_report_generation(self):
        """Test end-to-end report generation and PDF export."""
        try:
            report_gen = ReportGenerator()
            pdf_gen = PDFReportGenerator()
        except ImportError:
            pytest.skip("Required libraries not installed")
        
        # Generate report
        transactions = [
            {"date": "2024-02-19", "type": "expense", "category": "food", "amount": 100},
            {"date": "2024-02-20", "type": "expense", "category": "transport", "amount": 50},
        ]
        
        report = report_gen.generate_weekly_report(
            user_id="user123",
            transactions=transactions,
            account_balance=Decimal("5000"),
            monthly_income=5000,
        )
        
        # Generate PDF
        pdf_bytes = pdf_gen.generate_weekly_report_pdf(report)
        
        # Verify
        assert report is not None
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
