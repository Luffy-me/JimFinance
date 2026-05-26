"""Unit tests for Telegram message processor"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Message, User, Chat, PhotoSize, CallbackQuery
from telegram.ext import ContextTypes

from app.integrations.telegram.processors.message_processor import MessageProcessor


@pytest.fixture
def message_processor():
    """Fixture for MessageProcessor instance."""
    with patch('app.integrations.telegram.processors.message_processor.TransactionIntelligenceService'):
        return MessageProcessor()


@pytest.fixture
def mock_message():
    """Fixture for mock Telegram Message."""
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 123456
    message.chat = MagicMock(spec=Chat)
    message.chat.id = 123456
    message.message_id = 1
    return message


@pytest.fixture
def mock_context():
    """Fixture for mock Telegram context."""
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = AsyncMock()
    context.bot.send_message = AsyncMock()
    context.bot.edit_message_text = AsyncMock()
    return context


class TestMessageProcessor:
    """Tests for MessageProcessor class."""

    @pytest.mark.asyncio
    async def test_process_text_message_success(self, message_processor, mock_message, mock_context):
        """Test successful text message processing."""
        mock_message.text = "500 RUB coffee"
        
        with patch.object(message_processor.transaction_service, 'process_text_input') as mock_process:
            mock_process.return_value = {
                'merchant': 'coffee',
                'amount': 500,
                'currency': 'RUB',
                'category': 'food',
                'confidence_score': 0.95,
                'description': 'coffee'
            }
            
            await message_processor.process_text_message(mock_message, mock_context)
            
            mock_process.assert_called_once()
            mock_context.bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_text_message_with_inline_buttons(self, message_processor, mock_message, mock_context):
        """Test text message processing generates inline buttons."""
        mock_message.text = "Starbucks 5 USD"
        
        with patch.object(message_processor.transaction_service, 'process_text_input') as mock_process:
            mock_process.return_value = {
                'merchant': 'starbucks',
                'amount': 5.0,
                'currency': 'USD',
                'category': 'food',
                'confidence_score': 0.95,
                'description': 'morning coffee'
            }
            
            await message_processor.process_text_message(mock_message, mock_context)
            
            # Check that buttons were sent
            call_args = mock_context.bot.send_message.call_args
            assert call_args[1]['reply_markup'] is not None

    @pytest.mark.asyncio
    async def test_process_text_message_parse_failure(self, message_processor, mock_message, mock_context):
        """Test handling of parsing failure."""
        mock_message.text = "invalid transaction format"
        
        with patch.object(message_processor.transaction_service, 'process_text_input') as mock_process:
            mock_process.return_value = None
            
            await message_processor.process_text_message(mock_message, mock_context)
            
            # Should show error message
            mock_context.bot.send_message.assert_called_once()
            call_args = mock_context.bot.send_message.call_args
            assert "❌" in call_args[1]['text'] or "error" in call_args[1]['text'].lower()

    @pytest.mark.asyncio
    async def test_process_photo_message(self, message_processor, mock_message, mock_context):
        """Test photo message processing."""
        mock_photo = MagicMock(spec=PhotoSize)
        mock_photo.file_id = "test_file_id"
        mock_message.photo = [mock_photo]
        mock_message.text = None
        
        await message_processor.process_photo_message(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_document_message(self, message_processor, mock_message, mock_context):
        """Test document message processing."""
        mock_message.document = MagicMock()
        mock_message.text = None
        
        await message_processor.process_document_message(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "document" in call_args[1]['text'].lower() or "not" in call_args[1]['text'].lower()


class TestMessageProcessorCallbacks:
    """Tests for callback query processing."""

    @pytest.mark.asyncio
    async def test_handle_confirm_transaction(self, message_processor, mock_context):
        """Test transaction confirmation."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.message = MagicMock(spec=Message)
        callback_query.message.chat_id = 123456
        callback_query.message.message_id = 1
        callback_query.from_user.id = 123456
        callback_query.data = "confirm_transaction:yes"
        
        await message_processor.process_callback(
            callback_query, "confirm_transaction", ["yes"], mock_context
        )
        
        mock_context.bot.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_cancel_transaction(self, message_processor, mock_context):
        """Test transaction cancellation."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.message = MagicMock(spec=Message)
        callback_query.message.chat_id = 123456
        callback_query.message.message_id = 1
        callback_query.from_user.id = 123456
        
        await message_processor.process_callback(
            callback_query, "cancel_transaction", [], mock_context
        )
        
        mock_context.bot.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_edit_transaction(self, message_processor, mock_context):
        """Test transaction editing."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.message = MagicMock(spec=Message)
        callback_query.message.chat_id = 123456
        callback_query.message.message_id = 1
        
        await message_processor.process_callback(
            callback_query, "edit_transaction", ["manual"], mock_context
        )
        
        mock_context.bot.send_message.assert_called_once()


class TestMessageProcessorErrors:
    """Tests for error handling in MessageProcessor."""

    @pytest.mark.asyncio
    async def test_process_text_message_service_error(self, message_processor, mock_message, mock_context):
        """Test handling of service errors."""
        mock_message.text = "500 RUB coffee"
        
        with patch.object(message_processor.transaction_service, 'process_text_input') as mock_process:
            mock_process.side_effect = Exception("Service error")
            
            await message_processor.process_text_message(mock_message, mock_context)
            
            # Should show error message
            mock_context.bot.send_message.assert_called_once()
            call_args = mock_context.bot.send_message.call_args
            assert "error" in call_args[1]['text'].lower()

    @pytest.mark.asyncio
    async def test_process_photo_message_error(self, message_processor, mock_message, mock_context):
        """Test error handling for photo processing."""
        mock_photo = MagicMock(spec=PhotoSize)
        mock_photo.file_id = "test_file_id"
        mock_message.photo = [mock_photo]
        
        mock_context.bot.send_message.side_effect = Exception("API error")
        
        with pytest.raises(Exception):
            await message_processor.process_photo_message(mock_message, mock_context)
