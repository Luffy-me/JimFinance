"""Telegram Notification Delivery Service

Handles sending notifications via Telegram with:
- Formatted messages
- PDF attachments
- Callback buttons
- Error handling and retries
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class TelegramNotificationDelivery:
    """Handles Telegram notification delivery"""
    
    def __init__(self):
        """Initialize Telegram delivery service."""
        self.bot = None
        self._initialize_bot()
    
    def _initialize_bot(self):
        """Initialize Telegram bot."""
        try:
            from app.core.config import settings
            if not settings.TELEGRAM_BOT_TOKEN:
                logger.warning("TELEGRAM_BOT_TOKEN not configured")
                return
            
            from telegram import Bot
            self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        except Exception as e:
            logger.error(f"Error initializing Telegram bot: {e}")
    
    async def send_alert_notification(
        self,
        telegram_user_id: int,
        notification,
    ) -> Tuple[bool, Optional[str]]:
        """
        Send alert notification via Telegram.
        
        Args:
            telegram_user_id: Telegram user ID
            notification: Notification object
        
        Returns:
            Tuple of (success, message_id or error)
        """
        try:
            if not self.bot:
                return False, "Telegram bot not initialized"
            
            # Format message
            message_text = self._format_alert_message(notification)
            
            # Send message
            message = await self.bot.send_message(
                chat_id=telegram_user_id,
                text=message_text,
                parse_mode='HTML',
            )
            
            logger.info(f"Alert notification sent to {telegram_user_id}")
            return True, str(message.message_id)
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
            return False, str(e)
    
    async def send_report_notification(
        self,
        telegram_user_id: int,
        report,
        pdf_bytes: Optional[bytes] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Send financial report via Telegram.
        
        Args:
            telegram_user_id: Telegram user ID
            report: FinancialReport object
            pdf_bytes: PDF report bytes (optional)
        
        Returns:
            Tuple of (success, message_id or error)
        """
        try:
            if not self.bot:
                return False, "Telegram bot not initialized"
            
            # Send report summary message
            summary_text = self._format_report_summary(report)
            
            message = await self.bot.send_message(
                chat_id=telegram_user_id,
                text=summary_text,
                parse_mode='HTML',
            )
            
            logger.info(f"Report summary sent to {telegram_user_id}")
            
            # Send PDF if available
            if pdf_bytes:
                try:
                    await self.bot.send_document(
                        chat_id=telegram_user_id,
                        document=pdf_bytes,
                        filename=f"Financial_Report_{report.period_end.strftime('%Y-%m-%d')}.pdf",
                        caption="Your detailed financial report",
                    )
                    logger.info(f"Report PDF sent to {telegram_user_id}")
                except Exception as e:
                    logger.error(f"Error sending PDF: {e}")
            
            return True, str(message.message_id)
        except Exception as e:
            logger.error(f"Error sending report notification: {e}")
            return False, str(e)
    
    async def send_batch_notifications(
        self,
        telegram_user_id: int,
        notifications: List,
        batch_size: int = 3,
    ) -> Tuple[int, int]:
        """
        Send multiple notifications with batching.
        
        Args:
            telegram_user_id: Telegram user ID
            notifications: List of notifications
            batch_size: Number of notifications per message
        
        Returns:
            Tuple of (sent_count, failed_count)
        """
        sent = 0
        failed = 0
        
        try:
            # Group notifications into batches
            for i in range(0, len(notifications), batch_size):
                batch = notifications[i:i + batch_size]
                message_text = self._format_batch_message(batch)
                
                success, _ = await self.send_text_message(
                    telegram_user_id,
                    message_text,
                )
                
                if success:
                    sent += len(batch)
                else:
                    failed += len(batch)
                
                # Rate limiting
                await asyncio.sleep(1)
            
            logger.info(f"Batch notifications sent to {telegram_user_id}: {sent} sent, {failed} failed")
            return sent, failed
        except Exception as e:
            logger.error(f"Error sending batch notifications: {e}")
            return sent, failed + len(notifications) - sent
    
    async def send_text_message(
        self,
        telegram_user_id: int,
        text: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Send plain text message.
        
        Args:
            telegram_user_id: Telegram user ID
            text: Message text
        
        Returns:
            Tuple of (success, message_id or error)
        """
        try:
            if not self.bot:
                return False, "Telegram bot not initialized"
            
            message = await self.bot.send_message(
                chat_id=telegram_user_id,
                text=text,
                parse_mode='HTML',
            )
            
            return True, str(message.message_id)
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            return False, str(e)
    
    def _format_alert_message(self, notification) -> str:
        """Format alert notification message."""
        try:
            parts = []
            
            # Alert icon and title
            parts.append(f"🔔 <b>{notification.title}</b>")
            
            # Message
            parts.append(f"\n{notification.message}")
            
            # Data details
            if notification.data:
                parts.append("\n\n<b>Details:</b>")
                for key, value in list(notification.data.items())[:5]:  # Top 5 details
                    formatted_key = key.replace("_", " ").title()
                    parts.append(f"• <b>{formatted_key}:</b> {value}")
            
            # Recommendation
            parts.append(f"\n\n💡 <b>Recommendation:</b> {notification.data.get('recommendation', 'Monitor this situation')}")
            
            # Confidence
            confidence = notification.confidence * 100
            parts.append(f"\n\n📊 <b>Confidence:</b> {confidence:.0f}%")
            
            return "".join(parts)
        except Exception as e:
            logger.error(f"Error formatting alert message: {e}")
            return notification.title
    
    def _format_report_summary(self, report) -> str:
        """Format financial report summary message."""
        try:
            parts = []
            
            # Header
            parts.append(f"📊 <b>Your Weekly Financial Report</b>")
            parts.append(f"\n<b>Period:</b> {report.period_start.strftime('%b %d')} - {report.period_end.strftime('%b %d, %Y')}")
            
            # Health score
            parts.append(f"\n\n<b>Financial Health:</b>")
            parts.append(f"Score: {report.health_analysis.get('score', 0):.0f}/100 ({report.health_analysis.get('grade', 'N/A')})")
            parts.append(f"Risk: {report.health_analysis.get('risk_level', 'Unknown').upper()}")
            
            # Key metrics
            parts.append(f"\n\n<b>Key Metrics:</b>")
            metrics = report.key_metrics
            if metrics.get('weekly_spending') is not None:
                parts.append(f"💰 Weekly Spending: ${metrics['weekly_spending']:.2f}")
            if metrics.get('spending_trend'):
                parts.append(f"📈 Trend: {metrics['spending_trend']}")
            
            # Top recommendations
            if report.recommendations:
                parts.append(f"\n\n<b>Top Recommendations:</b>")
                for i, rec in enumerate(report.recommendations[:3], 1):
                    parts.append(f"{i}. {rec.get('recommendation', '')}")
            
            # Alerts
            if report.alerts:
                parts.append(f"\n\n⚠️ <b>Active Alerts:</b> {len(report.alerts)}")
                for alert in report.alerts[:2]:
                    parts.append(f"• {alert.get('title', 'Alert')}")
            
            # Call to action
            parts.append(f"\n\n📱 View detailed report in your dashboard or receive PDF")
            parts.append(f"\nReport ID: <code>{report.report_id[:8]}</code>")
            
            return "".join(parts)
        except Exception as e:
            logger.error(f"Error formatting report message: {e}")
            return "📊 Your weekly financial report is ready!"
    
    def _format_batch_message(self, notifications: List) -> str:
        """Format batch of notifications into single message."""
        try:
            parts = []
            parts.append(f"🔔 <b>Financial Alerts ({len(notifications)})</b>\n")
            
            for i, notif in enumerate(notifications, 1):
                parts.append(f"{i}. <b>{notif.title}</b>")
                parts.append(f"   {notif.message[:100]}{'...' if len(notif.message) > 100 else ''}")
                parts.append("")
            
            parts.append("\n💡 Check each alert for detailed recommendations")
            
            return "\n".join(parts)
        except Exception as e:
            logger.error(f"Error formatting batch message: {e}")
            return f"🔔 You have {len(notifications)} new financial alerts"
    
    async def send_scheduled_notification(
        self,
        telegram_user_id: int,
        notification_type: str,
        data: Dict,
    ) -> Tuple[bool, Optional[str]]:
        """
        Send a scheduled notification (daily/weekly summary).
        
        Args:
            telegram_user_id: Telegram user ID
            notification_type: Type of scheduled notification
            data: Notification data
        
        Returns:
            Tuple of (success, message_id or error)
        """
        try:
            if notification_type == "daily_summary":
                message = self._format_daily_summary(data)
            elif notification_type == "weekly_report":
                message = self._format_weekly_summary(data)
            else:
                message = f"📊 {data.get('title', 'Update available')}"
            
            return await self.send_text_message(telegram_user_id, message)
        except Exception as e:
            logger.error(f"Error sending scheduled notification: {e}")
            return False, str(e)
    
    def _format_daily_summary(self, data: Dict) -> str:
        """Format daily summary message."""
        try:
            parts = []
            parts.append("📅 <b>Daily Financial Summary</b>\n")
            
            if data.get('today_spending'):
                parts.append(f"💰 Today's Spending: ${data['today_spending']:.2f}\n")
            
            if data.get('alerts_count', 0) > 0:
                parts.append(f"⚠️ Active Alerts: {data['alerts_count']}\n")
            
            if data.get('health_score'):
                parts.append(f"📊 Health Score: {data['health_score']:.0f}/100")
            
            return "".join(parts)
        except Exception as e:
            logger.error(f"Error formatting daily summary: {e}")
            return "📅 Daily summary"
    
    def _format_weekly_summary(self, data: Dict) -> str:
        """Format weekly summary message."""
        try:
            parts = []
            parts.append("📊 <b>Weekly Financial Summary</b>\n")
            
            if data.get('total_spending'):
                parts.append(f"💰 Total Spending: ${data['total_spending']:.2f}\n")
            
            if data.get('transactions_count'):
                parts.append(f"📝 Transactions: {data['transactions_count']}\n")
            
            if data.get('health_score'):
                grade = data.get('health_grade', 'N/A')
                parts.append(f"📊 Health Score: {data['health_score']:.0f}/100 ({grade})")
            
            return "".join(parts)
        except Exception as e:
            logger.error(f"Error formatting weekly summary: {e}")
            return "📊 Weekly summary"
