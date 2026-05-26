"""Core Telegram Bot Implementation"""

import logging
from typing import Optional
from telegram import Bot, Update
from telegram.error import TelegramError

from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Main Telegram Bot wrapper around python-telegram-bot library."""

    def __init__(self, token: Optional[str] = None):
        """Initialize Telegram Bot.

        Args:
            token: Telegram bot token. If None, uses TELEGRAM_BOT_TOKEN from settings.

        Raises:
            ValueError: If no token is provided and settings.TELEGRAM_BOT_TOKEN is not set.
        """
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        if not self.token:
            raise ValueError(
                "Telegram bot token not provided. "
                "Set TELEGRAM_BOT_TOKEN environment variable or pass token parameter."
            )

        self.bot = Bot(token=self.token)
        logger.info(f"Telegram Bot initialized: {self.bot.username}")

    async def get_me(self) -> dict:
        """Get bot information.

        Returns:
            Dictionary containing bot info (id, username, first_name, etc.)
        """
        try:
            me = await self.bot.get_me()
            return {
                "id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "is_bot": me.is_bot,
            }
        except TelegramError as e:
            logger.error(f"Failed to get bot info: {e}")
            raise

    async def send_message(
        self, chat_id: int, text: str, parse_mode: str = "HTML", reply_markup=None
    ) -> dict:
        """Send a message to a user.

        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Message format (HTML, Markdown, MarkdownV2)
            reply_markup: Keyboard markup for inline buttons

        Returns:
            Message data
        """
        try:
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            return {
                "message_id": message.message_id,
                "chat_id": message.chat_id,
                "text": message.text,
            }
        except TelegramError as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            raise

    async def send_photo(
        self,
        chat_id: int,
        photo: str,
        caption: str = "",
        parse_mode: str = "HTML",
        reply_markup=None,
    ) -> dict:
        """Send a photo to a user.

        Args:
            chat_id: Telegram chat ID
            photo: Photo URL or file_id
            caption: Photo caption
            parse_mode: Caption format
            reply_markup: Keyboard markup

        Returns:
            Message data
        """
        try:
            message = await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            return {
                "message_id": message.message_id,
                "chat_id": message.chat_id,
                "photo_id": message.photo[-1].file_id if message.photo else None,
            }
        except TelegramError as e:
            logger.error(f"Failed to send photo to {chat_id}: {e}")
            raise

    async def answer_callback_query(
        self, callback_query_id: str, text: str = "", show_alert: bool = False
    ) -> bool:
        """Answer a callback query from inline buttons.

        Args:
            callback_query_id: Callback query ID
            text: Notification text
            show_alert: Show as alert (true) or toast (false)

        Returns:
            Success status
        """
        try:
            await self.bot.answer_callback_query(
                callback_query_id=callback_query_id, text=text, show_alert=show_alert
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to answer callback query: {e}")
            raise

    async def edit_message_text(
        self, chat_id: int, message_id: int, text: str, reply_markup=None
    ) -> dict:
        """Edit existing message text.

        Args:
            chat_id: Telegram chat ID
            message_id: Message ID to edit
            text: New message text
            reply_markup: Keyboard markup

        Returns:
            Updated message data
        """
        try:
            message = await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            return {
                "message_id": message.message_id,
                "text": message.text,
            }
        except TelegramError as e:
            logger.error(f"Failed to edit message {message_id}: {e}")
            raise

    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Delete a message.

        Args:
            chat_id: Telegram chat ID
            message_id: Message ID to delete

        Returns:
            Success status
        """
        try:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            return True
        except TelegramError as e:
            logger.error(f"Failed to delete message {message_id}: {e}")
            raise

    async def set_webhook(self, url: str) -> bool:
        """Set webhook URL for receiving updates.

        Args:
            url: Webhook URL

        Returns:
            Success status
        """
        try:
            await self.bot.set_webhook(url=url)
            logger.info(f"Webhook set to {url}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to set webhook: {e}")
            raise

    async def delete_webhook(self) -> bool:
        """Delete webhook and switch to polling.

        Returns:
            Success status
        """
        try:
            await self.bot.delete_webhook()
            logger.info("Webhook deleted")
            return True
        except TelegramError as e:
            logger.error(f"Failed to delete webhook: {e}")
            raise

    async def get_webhook_info(self) -> dict:
        """Get current webhook information.

        Returns:
            Webhook info dictionary
        """
        try:
            info = await self.bot.get_webhook_info()
            return {
                "url": info.url,
                "has_custom_certificate": info.has_custom_certificate,
                "pending_update_count": info.pending_update_count,
                "ip_address": info.ip_address,
            }
        except TelegramError as e:
            logger.error(f"Failed to get webhook info: {e}")
            raise
