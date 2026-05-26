"""Celery Tasks for JimFinance

Asynchronous tasks for:
- Weekly report generation
- Daily alert detection
- Notification delivery
- Subscription monitoring
- Burn rate tracking
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)


def get_celery_app():
    """Get Celery app instance."""
    from app.core.celery import app
    return app


# ============================================================================
# REPORT GENERATION TASKS
# ============================================================================

@get_celery_app().task(
    name="app.tasks.reports.generate_weekly_reports",
    bind=True,
    max_retries=3,
)
def generate_weekly_reports(self):
    """Generate weekly financial reports for all active users."""
    try:
        from app.services.report_generation import ReportGenerator
        from app.services.pdf_generation import PDFReportGenerator
        from app.db.base import SessionLocal
        from app.models.user import User
        
        logger.info("Starting weekly report generation task")
        
        db = SessionLocal()
        generator = ReportGenerator()
        pdf_generator = PDFReportGenerator()
        
        try:
            # Get all active users
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                try:
                    # Fetch user transactions and data
                    # In production: query from database
                    transactions = []  # db.query(Transaction).filter(...).all()
                    account_balance = Decimal("0")  # from user account
                    monthly_income = None  # from user profile
                    
                    # Generate report
                    report = generator.generate_weekly_report(
                        user_id=str(user.id),
                        transactions=transactions,
                        account_balance=account_balance,
                        monthly_income=monthly_income,
                    )
                    
                    # Generate PDF
                    pdf_bytes = pdf_generator.generate_weekly_report_pdf(report)
                    
                    # Queue notification delivery
                    send_report_via_telegram.delay(
                        user_id=str(user.id),
                        report_id=report.report_id,
                        report_dict=report.__dict__,
                        pdf_bytes=pdf_bytes,
                    )
                    
                    logger.info(f"Weekly report generated for user {user.id}")
                except Exception as e:
                    logger.error(f"Error generating report for user {user.id}: {e}")
                    continue
        finally:
            db.close()
        
        logger.info("Weekly report generation task completed")
        return {"status": "success", "task": "generate_weekly_reports"}
    except Exception as e:
        logger.error(f"Error in generate_weekly_reports: {e}")
        raise self.retry(exc=e, countdown=60)


# ============================================================================
# ALERT DETECTION TASKS
# ============================================================================

@get_celery_app().task(
    name="app.tasks.alerts.check_daily_spending_alerts",
    bind=True,
    max_retries=3,
)
def check_daily_spending_alerts(self):
    """Check for daily spending anomalies and send alerts."""
    try:
        from app.ml.alerts import AlertDetectionEngine
        from app.services.notifications import NotificationService
        from app.db.base import SessionLocal
        from app.models.user import User
        
        logger.info("Starting daily spending alerts check")
        
        db = SessionLocal()
        alert_engine = AlertDetectionEngine()
        notif_service = NotificationService()
        
        try:
            # Get all active users
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                try:
                    # Fetch user transactions
                    transactions = []  # In production: fetch from database
                    
                    # Detect spending anomalies
                    alerts = alert_engine.detect_spending_anomalies(transactions)
                    
                    if alerts:
                        # Queue notifications
                        notifications = notif_service.queue_notifications(
                            user_id=str(user.id),
                            alerts=alerts,
                        )
                        
                        for notif in notifications:
                            send_telegram_notification.delay(
                                user_id=str(user.id),
                                notification_dict=notif.__dict__,
                            )
                        
                        logger.info(f"Spending alerts queued for user {user.id}: {len(alerts)} alerts")
                except Exception as e:
                    logger.error(f"Error checking spending alerts for user {user.id}: {e}")
                    continue
        finally:
            db.close()
        
        logger.info("Daily spending alerts check completed")
        return {"status": "success", "task": "check_daily_spending_alerts"}
    except Exception as e:
        logger.error(f"Error in check_daily_spending_alerts: {e}")
        raise self.retry(exc=e, countdown=60)


@get_celery_app().task(
    name="app.tasks.alerts.check_burn_rate",
    bind=True,
    max_retries=3,
)
def check_burn_rate(self):
    """Check burn rate and send runway warnings."""
    try:
        from app.ml.alerts import AlertDetectionEngine
        from app.services.notifications import NotificationService
        from app.db.base import SessionLocal
        from app.models.user import User
        
        logger.info("Starting burn rate check")
        
        db = SessionLocal()
        alert_engine = AlertDetectionEngine()
        notif_service = NotificationService()
        
        try:
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                try:
                    # Fetch user data
                    transactions = []  # In production: fetch from database
                    account_balance = Decimal("0")  # From user account
                    monthly_income = None  # From user profile
                    monthly_expenses = None  # Calculate from transactions
                    
                    # Detect burn rate issues
                    alerts = alert_engine.detect_burn_rate_issues(
                        transactions=transactions,
                        account_balance=account_balance,
                        monthly_income=monthly_income,
                        monthly_expenses=monthly_expenses,
                    )
                    
                    if alerts:
                        notifications = notif_service.queue_notifications(
                            user_id=str(user.id),
                            alerts=alerts,
                        )
                        
                        for notif in notifications:
                            send_telegram_notification.delay(
                                user_id=str(user.id),
                                notification_dict=notif.__dict__,
                            )
                        
                        logger.info(f"Burn rate alerts queued for user {user.id}: {len(alerts)} alerts")
                except Exception as e:
                    logger.error(f"Error checking burn rate for user {user.id}: {e}")
                    continue
        finally:
            db.close()
        
        logger.info("Burn rate check completed")
        return {"status": "success", "task": "check_burn_rate"}
    except Exception as e:
        logger.error(f"Error in check_burn_rate: {e}")
        raise self.retry(exc=e, countdown=60)


@get_celery_app().task(
    name="app.tasks.alerts.check_subscription_waste",
    bind=True,
    max_retries=3,
)
def check_subscription_waste(self):
    """Check for subscription waste and unused subscriptions."""
    try:
        from app.ml.alerts import AlertDetectionEngine
        from app.services.notifications import NotificationService
        from app.db.base import SessionLocal
        from app.models.user import User
        
        logger.info("Starting subscription waste check")
        
        db = SessionLocal()
        alert_engine = AlertDetectionEngine()
        notif_service = NotificationService()
        
        try:
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                try:
                    # Fetch user subscriptions
                    subscriptions = []  # In production: from database
                    monthly_expenses = None  # Calculate from transactions
                    
                    # Detect subscription waste
                    alerts = alert_engine.detect_subscription_waste(
                        subscriptions=subscriptions,
                        monthly_expenses=monthly_expenses,
                    )
                    
                    if alerts:
                        notifications = notif_service.queue_notifications(
                            user_id=str(user.id),
                            alerts=alerts,
                        )
                        
                        for notif in notifications:
                            send_telegram_notification.delay(
                                user_id=str(user.id),
                                notification_dict=notif.__dict__,
                            )
                        
                        logger.info(f"Subscription alerts queued for user {user.id}: {len(alerts)} alerts")
                except Exception as e:
                    logger.error(f"Error checking subscriptions for user {user.id}: {e}")
                    continue
        finally:
            db.close()
        
        logger.info("Subscription waste check completed")
        return {"status": "success", "task": "check_subscription_waste"}
    except Exception as e:
        logger.error(f"Error in check_subscription_waste: {e}")
        raise self.retry(exc=e, countdown=60)


@get_celery_app().task(
    name="app.tasks.alerts.check_behavioral_anomalies",
    bind=True,
    max_retries=3,
)
def check_behavioral_anomalies(self):
    """Check for behavioral spending anomalies."""
    try:
        from app.ml.alerts import AlertDetectionEngine
        from app.services.notifications import NotificationService
        from app.db.base import SessionLocal
        from app.models.user import User
        
        logger.info("Starting behavioral anomalies check")
        
        db = SessionLocal()
        alert_engine = AlertDetectionEngine()
        notif_service = NotificationService()
        
        try:
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                try:
                    # Fetch user data
                    transactions = []  # In production: from database
                    behavioral_profile = {}  # In production: from database
                    
                    # Detect behavioral anomalies
                    alerts = alert_engine.detect_behavioral_anomalies(
                        transactions=transactions,
                        behavioral_profile=behavioral_profile,
                    )
                    
                    if alerts:
                        notifications = notif_service.queue_notifications(
                            user_id=str(user.id),
                            alerts=alerts,
                        )
                        
                        for notif in notifications:
                            send_telegram_notification.delay(
                                user_id=str(user.id),
                                notification_dict=notif.__dict__,
                            )
                        
                        logger.info(f"Behavioral alerts queued for user {user.id}: {len(alerts)} alerts")
                except Exception as e:
                    logger.error(f"Error checking behavioral anomalies for user {user.id}: {e}")
                    continue
        finally:
            db.close()
        
        logger.info("Behavioral anomalies check completed")
        return {"status": "success", "task": "check_behavioral_anomalies"}
    except Exception as e:
        logger.error(f"Error in check_behavioral_anomalies: {e}")
        raise self.retry(exc=e, countdown=60)


@get_celery_app().task(
    name="app.tasks.alerts.detect_savings_opportunities",
    bind=True,
    max_retries=3,
)
def detect_savings_opportunities(self):
    """Detect savings opportunities for users."""
    try:
        from app.ml.alerts import AlertDetectionEngine
        from app.services.notifications import NotificationService
        from app.db.base import SessionLocal
        from app.models.user import User
        
        logger.info("Starting savings opportunities detection")
        
        db = SessionLocal()
        alert_engine = AlertDetectionEngine()
        notif_service = NotificationService()
        
        try:
            users = db.query(User).filter(User.is_active == True).all()
            
            for user in users:
                try:
                    # Fetch user data
                    transactions = []  # In production: from database
                    subscriptions = []  # In production: from database
                    monthly_expenses = None  # Calculate from transactions
                    
                    # Detect savings opportunities
                    alerts = alert_engine.detect_savings_opportunities(
                        transactions=transactions,
                        subscriptions=subscriptions,
                        monthly_expenses=monthly_expenses,
                    )
                    
                    if alerts:
                        notifications = notif_service.queue_notifications(
                            user_id=str(user.id),
                            alerts=alerts,
                        )
                        
                        for notif in notifications:
                            send_telegram_notification.delay(
                                user_id=str(user.id),
                                notification_dict=notif.__dict__,
                            )
                        
                        logger.info(f"Savings opportunities queued for user {user.id}: {len(alerts)} alerts")
                except Exception as e:
                    logger.error(f"Error detecting savings opportunities for user {user.id}: {e}")
                    continue
        finally:
            db.close()
        
        logger.info("Savings opportunities detection completed")
        return {"status": "success", "task": "detect_savings_opportunities"}
    except Exception as e:
        logger.error(f"Error in detect_savings_opportunities: {e}")
        raise self.retry(exc=e, countdown=60)


# ============================================================================
# NOTIFICATION DELIVERY TASKS
# ============================================================================

@get_celery_app().task(
    name="app.tasks.notifications.send_telegram_notification",
    bind=True,
    max_retries=3,
)
def send_telegram_notification(self, user_id: str, notification_dict: dict):
    """Send notification via Telegram."""
    try:
        import asyncio
        from app.integrations.telegram.notification_delivery import TelegramNotificationDelivery
        
        delivery = TelegramNotificationDelivery()
        
        # Create notification object
        class Notification:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        notification = Notification(notification_dict)
        
        # In production: fetch telegram_user_id from database mapping
        telegram_user_id = 0  # Placeholder
        
        # Send async
        loop = asyncio.get_event_loop()
        success, message_id = loop.run_until_complete(
            delivery.send_alert_notification(telegram_user_id, notification)
        )
        
        if success:
            logger.info(f"Notification sent via Telegram: {message_id}")
            return {"status": "success", "message_id": message_id}
        else:
            raise Exception(f"Failed to send notification: {message_id}")
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@get_celery_app().task(
    name="app.tasks.notifications.send_report_via_telegram",
    bind=True,
    max_retries=2,
)
def send_report_via_telegram(self, user_id: str, report_id: str, report_dict: dict, pdf_bytes: bytes = None):
    """Send financial report via Telegram."""
    try:
        import asyncio
        from app.integrations.telegram.notification_delivery import TelegramNotificationDelivery
        
        delivery = TelegramNotificationDelivery()
        
        # Create report object
        class Report:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        report = Report(report_dict)
        
        # In production: fetch telegram_user_id from database mapping
        telegram_user_id = 0  # Placeholder
        
        # Send async
        loop = asyncio.get_event_loop()
        success, message_id = loop.run_until_complete(
            delivery.send_report_notification(telegram_user_id, report, pdf_bytes)
        )
        
        if success:
            logger.info(f"Report sent via Telegram: {message_id}")
            return {"status": "success", "message_id": message_id, "report_id": report_id}
        else:
            raise Exception(f"Failed to send report: {message_id}")
    except Exception as e:
        logger.error(f"Error sending report via Telegram: {e}")
        raise self.retry(exc=e, countdown=300, max_retries=2)


@get_celery_app().task(
    name="app.tasks.notifications.send_batch_notifications",
    bind=True,
    max_retries=2,
)
def send_batch_notifications(self, user_id: str, notifications: list):
    """Send batch of notifications via Telegram."""
    try:
        import asyncio
        from app.integrations.telegram.notification_delivery import TelegramNotificationDelivery
        
        delivery = TelegramNotificationDelivery()
        
        # In production: fetch telegram_user_id from database mapping
        telegram_user_id = 0  # Placeholder
        
        # Send async
        loop = asyncio.get_event_loop()
        sent, failed = loop.run_until_complete(
            delivery.send_batch_notifications(telegram_user_id, notifications)
        )
        
        logger.info(f"Batch notifications sent: {sent} sent, {failed} failed")
        return {"status": "success", "sent": sent, "failed": failed}
    except Exception as e:
        logger.error(f"Error sending batch notifications: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=2)
