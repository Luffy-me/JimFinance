"""
Celery configuration for JimFinance
Handles asynchronous task queue with Redis broker
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
app = Celery(
    "jimfinance",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Load configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    result_expires=3600,  # Results expire after 1 hour
)

# Celery Beat Schedule - Periodic tasks
app.conf.beat_schedule = {
    # Daily alerts at 9 AM UTC
    "daily-spending-alerts": {
        "task": "app.tasks.alerts.check_daily_spending_alerts",
        "schedule": crontab(hour=9, minute=0),
    },
    # Weekly reports every Monday at 8 AM UTC
    "weekly-financial-reports": {
        "task": "app.tasks.reports.generate_weekly_reports",
        "schedule": crontab(day_of_week=1, hour=8, minute=0),
    },
    # Subscription waste check every Sunday at 10 AM UTC
    "subscription-waste-check": {
        "task": "app.tasks.alerts.check_subscription_waste",
        "schedule": crontab(day_of_week=6, hour=10, minute=0),
    },
    # Burn rate warnings daily at 8:30 AM UTC
    "burn-rate-warnings": {
        "task": "app.tasks.alerts.check_burn_rate",
        "schedule": crontab(hour=8, minute=30),
    },
    # Behavioral alerts check daily at 9:30 AM UTC
    "behavioral-alerts": {
        "task": "app.tasks.alerts.check_behavioral_anomalies",
        "schedule": crontab(hour=9, minute=30),
    },
    # Savings opportunity detection weekly Friday at 7 AM UTC
    "savings-opportunities": {
        "task": "app.tasks.alerts.detect_savings_opportunities",
        "schedule": crontab(day_of_week=4, hour=7, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    logger.info(f"Celery task request: {self.request!r}")
    print(f"Debug task executed: {self.request}")
