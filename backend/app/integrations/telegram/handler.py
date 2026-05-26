"""Telegram Update Handler - Main entry point for processing updates"""

import logging
from typing import Dict, Optional
from telegram import Update
from telegram.ext import ContextTypes

from app.integrations.telegram.processors.message_processor import MessageProcessor
from app.integrations.telegram.processors.command_processor import CommandProcessor

logger = logging.getLogger(__name__)


class TelegramUpdateHandler:
    """Handles incoming Telegram updates and routes them to appropriate processors."""

    def __init__(self, message_processor: Optional[MessageProcessor] = None, 
                 command_processor: Optional[CommandProcessor] = None):
        """Initialize update handler.
        
        Args:
            message_processor: Custom message processor instance
            command_processor: Custom command processor instance
        """
        self.message_processor = message_processor or MessageProcessor()
        self.command_processor = command_processor or CommandProcessor()

    async def handle_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Main handler for all incoming updates.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            if update.message:
                await self._handle_message(update, context)
            elif update.callback_query:
                await self._handle_callback_query(update, context)
            elif update.edited_message:
                await self._handle_edited_message(update, context)
            else:
                logger.debug(f"Unhandled update type: {update}")
        except Exception as e:
            logger.error(f"Error handling update: {e}", exc_info=True)

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming messages (text, photo, etc).
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        message = update.message
        user_id = message.from_user.id
        chat_id = message.chat_id

        # Check if it's a command
        if message.text and message.text.startswith('/'):
            await self.command_processor.process_command(message, context)
        elif message.text:
            await self.message_processor.process_text_message(message, context)
        elif message.photo:
            await self.message_processor.process_photo_message(message, context)
        elif message.document:
            await self.message_processor.process_document_message(message, context)
        else:
            # Unsupported message type
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Unsupported message type. Please send text, photo, or use /help for available commands.",
            )

    async def _handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries from inline buttons.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        callback_query = update.callback_query
        user_id = callback_query.from_user.id

        # Answer the callback query to remove loading state
        await callback_query.answer()

        # Extract callback data
        callback_data = callback_query.data
        logger.info(f"User {user_id} triggered callback: {callback_data}")

        # Route to appropriate handler based on callback data format
        # callback_data format: "action:param1:param2"
        if ':' in callback_data:
            action, *params = callback_data.split(':')
            await self.message_processor.process_callback(
                callback_query, action, params, context
            )
        else:
            logger.warning(f"Invalid callback data format: {callback_data}")

    async def _handle_edited_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle edited messages.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        logger.debug(f"Edited message received from user {update.edited_message.from_user.id}")
        # For now, we can ignore edited messages or process them same as new messages
        pass

    @staticmethod
    def build_update_dict(update_data: Dict) -> Dict:
        """Build update dictionary from webhook request JSON.
        
        Args:
            update_data: Raw update data from Telegram webhook
            
        Returns:
            Parsed update dictionary suitable for Update object
        """
        return update_data
