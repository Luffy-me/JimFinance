"""Notification Service

Manages notification queue and delivery:
- Alert notification handling
- Notification throttling and deduplication
- User notification preferences
- Notification history tracking
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


@dataclass
class Notification:
    """Individual notification"""
    notification_id: str
    user_id: str
    title: str
    message: str
    notification_type: str  # alert type
    channels: List[NotificationChannel]
    status: NotificationStatus
    data: Dict
    confidence: float
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_reason: Optional[str] = None


class NotificationService:
    """Manages notification queue and delivery"""
    
    # Throttle configuration (notifications per alert type per day)
    THROTTLE_CONFIG = {
        "spending_spike": 3,
        "burn_rate_warning": 2,
        "subscription_waste": 1,
        "savings_opportunity": 2,
        "behavioral_anomaly": 3,
        "low_runway": 1,
        "high_volatility": 2,
    }
    
    # Minimum time between notifications of same type (minutes)
    DEDUPLICATION_WINDOW = {
        "spending_spike": 60,  # 1 hour
        "burn_rate_warning": 360,  # 6 hours
        "subscription_waste": 1440,  # 24 hours
        "savings_opportunity": 1440,  # 24 hours
        "behavioral_anomaly": 60,  # 1 hour
        "low_runway": 360,  # 6 hours
        "high_volatility": 120,  # 2 hours
    }
    
    def __init__(self):
        """Initialize notification service."""
        # In production, this would use Redis or a database
        self.notification_history = {}  # In-memory cache for demo
    
    def queue_notifications(
        self,
        user_id: str,
        alerts: List,
        user_preferences: Optional[Dict] = None,
    ) -> List[Notification]:
        """
        Queue notifications for alerts.
        
        Args:
            user_id: User identifier
            alerts: List of alerts to notify
            user_preferences: User notification preferences
        
        Returns:
            List of queued Notification objects
        """
        queued = []
        
        try:
            user_preferences = user_preferences or self._get_default_preferences()
            
            for alert in alerts:
                # Check if notification should be sent
                if not self._should_send_notification(user_id, alert, user_preferences):
                    logger.debug(f"Notification throttled for user {user_id}, alert {alert.alert_type}")
                    continue
                
                # Create notification
                notification = self._create_notification(user_id, alert, user_preferences)
                if notification:
                    queued.append(notification)
                    
                    # Track in history
                    self._record_notification(user_id, alert, notification)
            
            logger.info(f"Queued {len(queued)} notifications for user {user_id}")
            return queued
        except Exception as e:
            logger.error(f"Error queuing notifications for user {user_id}: {e}")
            return []
    
    def _should_send_notification(
        self,
        user_id: str,
        alert,
        user_preferences: Dict,
    ) -> bool:
        """Determine if notification should be sent."""
        try:
            # Check if notifications are enabled
            if not user_preferences.get("notifications_enabled", True):
                return False
            
            # Check if alert type is enabled
            enabled_types = user_preferences.get("alert_types", {})
            if alert.alert_type.value not in enabled_types or not enabled_types[alert.alert_type.value]:
                return False
            
            # Check confidence threshold
            min_confidence = user_preferences.get("min_confidence", 0.5)
            if alert.confidence < min_confidence:
                return False
            
            # Check throttling
            alert_type = alert.alert_type.value
            recent_count = self._count_recent_notifications(user_id, alert_type, days=1)
            max_per_day = self.THROTTLE_CONFIG.get(alert_type, 5)
            
            if recent_count >= max_per_day:
                return False
            
            # Check deduplication window
            dedup_window = self.DEDUPLICATION_WINDOW.get(alert_type, 60)
            if self._has_recent_similar_notification(user_id, alert, minutes=dedup_window):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking if notification should be sent: {e}")
            return False
    
    def _create_notification(
        self,
        user_id: str,
        alert,
        user_preferences: Dict,
    ) -> Optional[Notification]:
        """Create a notification from an alert."""
        try:
            import uuid
            
            # Get channels for this alert type
            channels_config = user_preferences.get("channels", {})
            channels = []
            
            if channels_config.get("telegram", True):
                channels.append(NotificationChannel.TELEGRAM)
            if channels_config.get("email", False):
                channels.append(NotificationChannel.EMAIL)
            if channels_config.get("in_app", True):
                channels.append(NotificationChannel.IN_APP)
            
            if not channels:
                return None
            
            return Notification(
                notification_id=str(uuid.uuid4()),
                user_id=user_id,
                title=alert.title,
                message=alert.message,
                notification_type=alert.alert_type.value,
                channels=channels,
                status=NotificationStatus.PENDING,
                data=alert.data,
                confidence=alert.confidence,
                created_at=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    def _record_notification(
        self,
        user_id: str,
        alert,
        notification: Notification,
    ):
        """Record notification in history."""
        try:
            key = f"{user_id}:{alert.alert_type.value}"
            if key not in self.notification_history:
                self.notification_history[key] = []
            
            self.notification_history[key].append({
                "notification_id": notification.notification_id,
                "created_at": notification.created_at.isoformat(),
                "alert_hash": hashlib.md5(alert.message.encode()).hexdigest(),
            })
            
            # Keep only last 100 notifications
            if len(self.notification_history[key]) > 100:
                self.notification_history[key] = self.notification_history[key][-100:]
        except Exception as e:
            logger.error(f"Error recording notification: {e}")
    
    def _count_recent_notifications(
        self,
        user_id: str,
        alert_type: str,
        days: int = 1,
    ) -> int:
        """Count notifications of a type in the last N days."""
        try:
            key = f"{user_id}:{alert_type}"
            if key not in self.notification_history:
                return 0
            
            cutoff = datetime.now() - timedelta(days=days)
            count = 0
            
            for record in self.notification_history[key]:
                try:
                    created = datetime.fromisoformat(record["created_at"])
                    if created > cutoff:
                        count += 1
                except Exception:
                    continue
            
            return count
        except Exception as e:
            logger.error(f"Error counting recent notifications: {e}")
            return 0
    
    def _has_recent_similar_notification(
        self,
        user_id: str,
        alert,
        minutes: int = 60,
    ) -> bool:
        """Check if similar notification was sent recently."""
        try:
            alert_type = alert.alert_type.value
            key = f"{user_id}:{alert_type}"
            
            if key not in self.notification_history:
                return False
            
            alert_hash = hashlib.md5(alert.message.encode()).hexdigest()
            cutoff = datetime.now() - timedelta(minutes=minutes)
            
            for record in self.notification_history[key]:
                try:
                    created = datetime.fromisoformat(record["created_at"])
                    if created > cutoff and record.get("alert_hash") == alert_hash:
                        return True
                except Exception:
                    continue
            
            return False
        except Exception as e:
            logger.error(f"Error checking for recent similar notification: {e}")
            return False
    
    def _get_default_preferences(self) -> Dict:
        """Get default notification preferences."""
        return {
            "notifications_enabled": True,
            "min_confidence": 0.5,
            "alert_types": {
                "spending_spike": True,
                "burn_rate_warning": True,
                "subscription_waste": True,
                "savings_opportunity": True,
                "behavioral_anomaly": True,
                "low_runway": True,
                "high_volatility": True,
            },
            "channels": {
                "telegram": True,
                "email": False,
                "in_app": True,
            },
            "quiet_hours": {
                "enabled": False,
                "start": "22:00",
                "end": "08:00",
            },
        }
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user notification preferences."""
        # In production, would fetch from database
        return self._get_default_preferences()
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update user notification preferences."""
        try:
            # In production, would save to database
            logger.info(f"Updated preferences for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            return False
    
    def mark_sent(self, notification_id: str) -> bool:
        """Mark notification as sent."""
        try:
            # In production, would update database
            logger.info(f"Notification {notification_id} marked as sent")
            return True
        except Exception as e:
            logger.error(f"Error marking notification as sent: {e}")
            return False
    
    def mark_delivered(self, notification_id: str) -> bool:
        """Mark notification as delivered."""
        try:
            # In production, would update database
            logger.info(f"Notification {notification_id} marked as delivered")
            return True
        except Exception as e:
            logger.error(f"Error marking notification as delivered: {e}")
            return False
    
    def mark_failed(self, notification_id: str, reason: str) -> bool:
        """Mark notification as failed."""
        try:
            logger.warning(f"Notification {notification_id} failed: {reason}")
            return True
        except Exception as e:
            logger.error(f"Error marking notification as failed: {e}")
            return False
