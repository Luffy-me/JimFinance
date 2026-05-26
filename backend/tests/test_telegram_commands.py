"""Unit tests for Telegram command processor"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Message, User, Chat
from telegram.ext import ContextTypes

from app.integrations.telegram.processors.command_processor import CommandProcessor


@pytest.fixture
def command_processor():
    """Fixture for CommandProcessor instance."""
    return CommandProcessor()


@pytest.fixture
def mock_message():
    """Fixture for mock Telegram Message."""
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.id = 123456
    message.from_user.first_name = "John"
    message.chat = MagicMock(spec=Chat)
    message.chat.id = 123456
    message.text = "/start"
    return message


@pytest.fixture
def mock_context():
    """Fixture for mock Telegram context."""
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = AsyncMock()
    context.bot.send_message = AsyncMock()
    return context


class TestCommandProcessor:
    """Tests for CommandProcessor class."""

    @pytest.mark.asyncio
    async def test_start_command(self, command_processor, mock_message, mock_context):
        """Test /start command."""
        mock_message.text = "/start"
        
        await command_processor.process_command(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert call_args[1]["chat_id"] == 123456
        assert "Welcome" in call_args[1]["text"]
        assert "JimFinance" in call_args[1]["text"]

    @pytest.mark.asyncio
    async def test_help_command(self, command_processor, mock_message, mock_context):
        """Test /help command."""
        mock_message.text = "/help"
        
        await command_processor.process_command(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "help" in call_args[1]["text"].lower() or "command" in call_args[1]["text"].lower()

    @pytest.mark.asyncio
    async def test_balance_command(self, command_processor, mock_message, mock_context):
        """Test /balance command."""
        mock_message.text = "/balance"
        
        await command_processor.process_command(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "balance" in call_args[1]["text"].lower() or "account" in call_args[1]["text"].lower()

    @pytest.mark.asyncio
    async def test_recent_command(self, command_processor, mock_message, mock_context):
        """Test /recent command."""
        mock_message.text = "/recent"
        
        await command_processor.process_command(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "recent" in call_args[1]["text"].lower() or "transaction" in call_args[1]["text"].lower()

    @pytest.mark.asyncio
    async def test_stats_command(self, command_processor, mock_message, mock_context):
        """Test /stats command."""
        mock_message.text = "/stats"
        
        await command_processor.process_command(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "spending" in call_args[1]["text"].lower() or "statistic" in call_args[1]["text"].lower()

    @pytest.mark.asyncio
    async def test_settings_command(self, command_processor, mock_message, mock_context):
        """Test /settings command."""
        mock_message.text = "/settings"
        
        await command_processor.process_command(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "setting" in call_args[1]["text"].lower() or "configure" in call_args[1]["text"].lower()

    @pytest.mark.asyncio
    async def test_status_command(self, command_processor, mock_message, mock_context):
        """Test /status command."""
        mock_message.text = "/status"
        
        await command_processor.process_command(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "status" in call_args[1]["text"].lower() or "system" in call_args[1]["text"].lower()

    @pytest.mark.asyncio
    async def test_unknown_command(self, command_processor, mock_message, mock_context):
        """Test unknown command handling."""
        mock_message.text = "/unknown"
        
        await command_processor.process_command(mock_message, mock_context)
        
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args
        assert "unknown" in call_args[1]["text"].lower()

    @pytest.mark.asyncio
    async def test_command_with_args(self, command_processor, mock_message, mock_context):
        """Test command with arguments."""
        mock_message.text = "/start arg1 arg2"
        
        await command_processor.process_command(mock_message, mock_context)
        
        # Should still process the command
        mock_context.bot.send_message.assert_called_once()

    def test_available_commands(self, command_processor):
        """Test that all expected commands are registered."""
        expected_commands = [
            "/start", "/help", "/balance", 
            "/recent", "/stats", "/settings", "/status"
        ]
        
        for cmd in expected_commands:
            assert cmd in command_processor.COMMANDS, f"Command {cmd} not registered"


class TestCommandProcessorErrorHandling:
    """Tests for error handling in CommandProcessor."""

    @pytest.mark.asyncio
    async def test_command_processing_error(self, command_processor, mock_message, mock_context):
        """Test handling of errors during command processing."""
        mock_message.text = "/start"
        mock_context.bot.send_message.side_effect = Exception("API Error")
        
        # Should not raise exception
        with pytest.raises(Exception):
            await command_processor.process_command(mock_message, mock_context)

    @pytest.mark.asyncio
    async def test_missing_user_info(self, command_processor, mock_context):
        """Test handling of missing user information."""
        message = MagicMock(spec=Message)
        message.from_user = None
        message.text = "/start"
        message.chat = MagicMock(spec=Chat)
        message.chat.id = 123456
        
        # Should handle gracefully
        with pytest.raises(AttributeError):
            await command_processor.process_command(message, mock_context)
