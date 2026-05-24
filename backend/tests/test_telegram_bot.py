"""Unit tests for Telegram bot core classes"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Bot, Update, Message, User, Chat
from telegram.error import TelegramError

from app.integrations.telegram.bot import TelegramBot
from app.integrations.telegram.handler import TelegramUpdateHandler


class TestTelegramBot:
    """Tests for TelegramBot class."""

    @pytest.fixture
    def bot(self):
        """Fixture for TelegramBot instance."""
        with patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token_12345'}):
            with patch('app.integrations.telegram.bot.Bot'):
                return TelegramBot(token='test_token_12345')

    @pytest.mark.asyncio
    async def test_bot_initialization(self, bot):
        """Test bot initialization."""
        assert bot.token == 'test_token_12345'
        assert bot.bot is not None

    @pytest.mark.asyncio
    async def test_get_me(self, bot):
        """Test getting bot information."""
        bot.bot.get_me = AsyncMock()
        bot.bot.get_me.return_value = MagicMock(
            id=123456789,
            username='test_bot',
            first_name='TestBot',
            is_bot=True,
        )
        
        result = await bot.get_me()
        
        assert result['id'] == 123456789
        assert result['username'] == 'test_bot'
        assert result['is_bot'] is True

    @pytest.mark.asyncio
    async def test_send_message(self, bot):
        """Test sending a message."""
        bot.bot.send_message = AsyncMock()
        bot.bot.send_message.return_value = MagicMock(
            message_id=1,
            chat_id=123456,
            text='Test message',
        )
        
        result = await bot.send_message(
            chat_id=123456,
            text='Test message',
            parse_mode='HTML'
        )
        
        assert result['message_id'] == 1
        assert result['text'] == 'Test message'
        bot.bot.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_photo(self, bot):
        """Test sending a photo."""
        bot.bot.send_photo = AsyncMock()
        mock_photo = MagicMock()
        mock_photo.file_id = 'photo_123'
        bot.bot.send_photo.return_value = MagicMock(
            message_id=1,
            chat_id=123456,
            photo=[mock_photo],
        )
        
        result = await bot.send_photo(
            chat_id=123456,
            photo='photo_url',
            caption='Test photo'
        )
        
        assert result['message_id'] == 1
        bot.bot.send_photo.assert_called_once()

    @pytest.mark.asyncio
    async def test_answer_callback_query(self, bot):
        """Test answering callback query."""
        bot.bot.answer_callback_query = AsyncMock()
        
        result = await bot.answer_callback_query(
            callback_query_id='callback_123',
            text='Success',
            show_alert=False
        )
        
        assert result is True
        bot.bot.answer_callback_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_edit_message_text(self, bot):
        """Test editing message text."""
        bot.bot.edit_message_text = AsyncMock()
        bot.bot.edit_message_text.return_value = MagicMock(
            message_id=1,
            text='Updated text',
        )
        
        result = await bot.edit_message_text(
            chat_id=123456,
            message_id=1,
            text='Updated text'
        )
        
        assert result['message_id'] == 1
        bot.bot.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_message(self, bot):
        """Test deleting a message."""
        bot.bot.delete_message = AsyncMock()
        
        result = await bot.delete_message(chat_id=123456, message_id=1)
        
        assert result is True
        bot.bot.delete_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_webhook(self, bot):
        """Test setting webhook."""
        bot.bot.set_webhook = AsyncMock()
        
        result = await bot.set_webhook('https://example.com/webhook')
        
        assert result is True
        bot.bot.set_webhook.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_webhook(self, bot):
        """Test deleting webhook."""
        bot.bot.delete_webhook = AsyncMock()
        
        result = await bot.delete_webhook()
        
        assert result is True
        bot.bot.delete_webhook.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_webhook_info(self, bot):
        """Test getting webhook info."""
        bot.bot.get_webhook_info = AsyncMock()
        bot.bot.get_webhook_info.return_value = MagicMock(
            url='https://example.com/webhook',
            has_custom_certificate=False,
            pending_update_count=0,
            ip_address='192.168.1.1',
        )
        
        result = await bot.get_webhook_info()
        
        assert result['url'] == 'https://example.com/webhook'
        assert result['pending_update_count'] == 0

    @pytest.mark.asyncio
    async def test_send_message_error(self, bot):
        """Test error handling in send_message."""
        bot.bot.send_message = AsyncMock(side_effect=TelegramError("API Error"))
        
        with pytest.raises(TelegramError):
            await bot.send_message(chat_id=123456, text='Test')


class TestTelegramUpdateHandler:
    """Tests for TelegramUpdateHandler class."""

    @pytest.fixture
    def handler(self):
        """Fixture for TelegramUpdateHandler."""
        with patch('app.integrations.telegram.handler.MessageProcessor'):
            with patch('app.integrations.telegram.handler.CommandProcessor'):
                return TelegramUpdateHandler()

    @pytest.fixture
    def mock_context(self):
        """Fixture for mock context."""
        return AsyncMock()

    @pytest.fixture
    def mock_update(self):
        """Fixture for mock update."""
        return MagicMock(spec=Update)

    @pytest.mark.asyncio
    async def test_handle_text_message(self, handler, mock_context, mock_update):
        """Test handling text message."""
        mock_message = MagicMock(spec=Message)
        mock_message.text = "Hello bot"
        mock_update.message = mock_message
        mock_update.callback_query = None
        mock_update.edited_message = None
        
        await handler.handle_update(mock_update, mock_context)
        
        handler.message_processor.process_text_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_command(self, handler, mock_context, mock_update):
        """Test handling command."""
        mock_message = MagicMock(spec=Message)
        mock_message.text = "/start"
        mock_update.message = mock_message
        mock_update.callback_query = None
        mock_update.edited_message = None
        
        await handler.handle_update(mock_update, mock_context)
        
        handler.command_processor.process_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_callback_query(self, handler, mock_context, mock_update):
        """Test handling callback query."""
        mock_callback = MagicMock()
        mock_callback.data = "confirm_transaction:yes"
        mock_callback.from_user.id = 123456
        mock_update.message = None
        mock_update.callback_query = mock_callback
        mock_update.edited_message = None
        
        await handler.handle_update(mock_update, mock_context)
        
        handler.message_processor.process_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_update_error(self, handler, mock_context, mock_update):
        """Test error handling in update processing."""
        mock_update.message = MagicMock()
        mock_update.message.text = "/start"
        mock_update.callback_query = None
        mock_update.edited_message = None
        
        handler.command_processor.process_command = AsyncMock(side_effect=Exception("Handler error"))
        
        # Should handle error gracefully
        await handler.handle_update(mock_update, mock_context)
        
        # No exception should be raised


class TestTelegramBotInitialization:
    """Tests for TelegramBot initialization."""

    def test_bot_init_with_token(self):
        """Test bot initialization with provided token."""
        with patch('app.integrations.telegram.bot.Bot'):
            bot = TelegramBot(token='custom_token_123')
            assert bot.token == 'custom_token_123'

    def test_bot_init_missing_token(self):
        """Test bot initialization without token raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                TelegramBot()

    def test_bot_init_with_env_token(self):
        """Test bot initialization uses environment token."""
        with patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'env_token_456'}):
            with patch('app.integrations.telegram.bot.Bot'):
                with patch('app.integrations.telegram.bot.settings') as mock_settings:
                    mock_settings.TELEGRAM_BOT_TOKEN = 'env_token_456'
                    bot = TelegramBot()
                    assert bot.token == 'env_token_456'
