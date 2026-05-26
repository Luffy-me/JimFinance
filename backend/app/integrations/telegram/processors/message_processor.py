"""Message Processor - Handles text, photo, and other message types"""

import logging
from typing import Optional, Tuple
from telegram import Message, CallbackQuery
from telegram.ext import ContextTypes

from app.services.transaction_intelligence import TransactionIntelligenceService
from app.core.config import settings

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Processes different types of Telegram messages and creates transactions."""

    def __init__(self):
        """Initialize message processor."""
        self.transaction_service = TransactionIntelligenceService()

    async def process_text_message(
        self, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Process incoming text message for transaction creation.
        
        Args:
            message: Telegram message object
            context: Telegram context object
        """
        user_id = message.from_user.id
        chat_id = message.chat_id
        text = message.text.strip()

        logger.info(f"Processing text message from user {user_id}: {text[:50]}...")

        try:
            # TODO: Get real user_id from Telegram user mapping
            # For now, use a placeholder
            jimfinance_user_id = user_id
            jimfinance_account_id = 1  # TODO: Get from user preferences

            # Process text using transaction intelligence service
            transaction = self.transaction_service.process_text_input(
                text=text,
                user_id=jimfinance_user_id,
                account_id=jimfinance_account_id,
            )

            if transaction:
                # Send confirmation message with inline buttons for confirmation
                await self._send_transaction_confirmation(
                    chat_id, message.message_id, transaction, context
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Could not parse transaction. Please try again with format: '500 RUB coffee' or 'Taxi 420'",
                )
        except Exception as e:
            logger.error(f"Error processing text message: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Error processing transaction. Please try again.",
            )

    async def process_photo_message(
        self, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Process photo message for OCR receipt processing.
        
        Args:
            message: Telegram message object with photo
            context: Telegram context object
        """
        user_id = message.from_user.id
        chat_id = message.chat_id

        logger.info(f"Processing photo message from user {user_id}")

        try:
            # Get photo file_id
            photo_file_id = message.photo[-1].file_id
            
            # TODO: Download photo and process with OCR
            # For now, send a placeholder response
            await context.bot.send_message(
                chat_id=chat_id,
                text="📸 Processing receipt... (feature coming soon)",
            )
        except Exception as e:
            logger.error(f"Error processing photo message: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Error processing photo. Please try again.",
            )

    async def process_document_message(
        self, message: Message, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Process document message (PDF, etc).
        
        Args:
            message: Telegram message object with document
            context: Telegram context object
        """
        user_id = message.from_user.id
        chat_id = message.chat_id

        logger.info(f"Processing document message from user {user_id}")

        await context.bot.send_message(
            chat_id=chat_id,
            text="📄 Document processing not yet supported. Please send a photo or text message.",
        )

    async def process_callback(
        self,
        callback_query: CallbackQuery,
        action: str,
        params: list,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Process callback query from inline buttons.
        
        Args:
            callback_query: Telegram callback query object
            action: Callback action name
            params: Callback parameters
            context: Telegram context object
        """
        user_id = callback_query.from_user.id
        message = callback_query.message

        logger.info(f"Processing callback {action} from user {user_id}")

        if action == "confirm_transaction":
            await self._handle_confirm_transaction(callback_query, params, context)
        elif action == "cancel_transaction":
            await self._handle_cancel_transaction(callback_query, context)
        elif action == "edit_transaction":
            await self._handle_edit_transaction(callback_query, params, context)
        else:
            logger.warning(f"Unknown callback action: {action}")

    async def _send_transaction_confirmation(
        self, chat_id: int, reply_to_message_id: int, transaction: dict, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Send transaction confirmation message with inline buttons.
        
        Args:
            chat_id: Telegram chat ID
            reply_to_message_id: Message ID to reply to
            transaction: Transaction data
            context: Telegram context object
        """
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        # Format transaction summary
        summary = f"""
✅ <b>Transaction Captured</b>

💰 Amount: <b>{transaction.get('amount')} {transaction.get('currency', 'USD')}</b>
🏪 Merchant: <b>{transaction.get('merchant', 'Unknown')}</b>
🏷️ Category: <b>{transaction.get('category', 'Other')}</b>
📝 Description: <i>{transaction.get('description', 'N/A')}</i>
🎯 Confidence: <b>{transaction.get('confidence_score', 0):.1%}</b>
"""

        # Create inline buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data="confirm_transaction:yes"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_transaction:no"),
            ],
            [
                InlineKeyboardButton("✏️ Edit", callback_data="edit_transaction:manual"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=summary,
            parse_mode="HTML",
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
        )

    async def _handle_confirm_transaction(
        self, callback_query: CallbackQuery, params: list, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle transaction confirmation.
        
        Args:
            callback_query: Telegram callback query object
            params: Callback parameters
            context: Telegram context object
        """
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text="✅ Transaction confirmed and saved!",
            parse_mode="HTML",
        )

    async def _handle_cancel_transaction(
        self, callback_query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle transaction cancellation.
        
        Args:
            callback_query: Telegram callback query object
            context: Telegram context object
        """
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text="❌ Transaction cancelled.",
            parse_mode="HTML",
        )

    async def _handle_edit_transaction(
        self, callback_query: CallbackQuery, params: list, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle transaction editing.
        
        Args:
            callback_query: Telegram callback query object
            params: Callback parameters
            context: Telegram context object
        """
        await context.bot.send_message(
            chat_id=callback_query.message.chat_id,
            text="✏️ Edit feature coming soon. For now, please send a new transaction.",
        )
