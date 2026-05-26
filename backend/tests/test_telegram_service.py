"""Unit tests for Telegram service layer"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.telegram_service import (
    TelegramUserService,
    TelegramTransactionService,
    TelegramAnalyticsService,
)


@pytest.fixture
def user_service():
    """Fixture for TelegramUserService."""
    return TelegramUserService()


@pytest.fixture
def transaction_service():
    """Fixture for TelegramTransactionService."""
    with patch('app.services.telegram_service.TransactionIntelligenceService'):
        return TelegramTransactionService()


@pytest.fixture
def analytics_service():
    """Fixture for TelegramAnalyticsService."""
    return TelegramAnalyticsService()


class TestTelegramUserService:
    """Tests for TelegramUserService."""

    @pytest.mark.asyncio
    async def test_get_or_create_user_mapping(self, user_service):
        """Test getting or creating user mapping."""
        result = await user_service.get_or_create_user_mapping(123456, "testuser")
        
        assert result is not None
        assert result['telegram_user_id'] == 123456
        assert result['telegram_username'] == "testuser"
        assert 'jimfinance_user_id' in result
        assert result['is_active'] is True

    @pytest.mark.asyncio
    async def test_get_user_preferences(self, user_service):
        """Test retrieving user preferences."""
        result = await user_service.get_user_preferences(123456)
        
        assert result is not None
        assert 'language' in result
        assert 'default_currency' in result
        assert 'default_account_id' in result
        assert 'notifications_enabled' in result
        assert result['language'] == 'en'

    @pytest.mark.asyncio
    async def test_update_user_preferences(self, user_service):
        """Test updating user preferences."""
        preferences = {
            'language': 'ru',
            'default_currency': 'RUB',
        }
        
        result = await user_service.update_user_preferences(123456, preferences)
        
        assert result is True


class TestTelegramTransactionService:
    """Tests for TelegramTransactionService."""

    @pytest.mark.asyncio
    async def test_process_expense_message_success(self, transaction_service):
        """Test successful expense message processing."""
        with patch.object(transaction_service.transaction_intelligence, 'process_text_input') as mock_process:
            mock_process.return_value = {
                'merchant': 'starbucks',
                'amount': 5.0,
                'currency': 'USD',
                'category': 'food',
                'confidence_score': 0.95,
            }
            
            result = await transaction_service.process_expense_message(
                123456, "Starbucks 5 USD"
            )
            
            assert result is not None
            assert result['merchant'] == 'starbucks'
            assert result['amount'] == 5.0

    @pytest.mark.asyncio
    async def test_process_expense_message_error(self, transaction_service):
        """Test error handling in expense processing."""
        with patch.object(transaction_service.transaction_intelligence, 'process_text_input') as mock_process:
            mock_process.side_effect = Exception("Processing error")
            
            result = await transaction_service.process_expense_message(
                123456, "invalid input"
            )
            
            assert result is None

    @pytest.mark.asyncio
    async def test_confirm_transaction(self, transaction_service):
        """Test transaction confirmation."""
        result = await transaction_service.confirm_transaction(123456, "txn_123")
        
        assert result is True

    @pytest.mark.asyncio
    async def test_get_recent_transactions(self, transaction_service):
        """Test retrieving recent transactions."""
        result = await transaction_service.get_recent_transactions(123456, limit=5)
        
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_recent_transactions_error(self, transaction_service):
        """Test error handling when retrieving transactions."""
        with patch('app.services.telegram_service.TransactionIntelligenceService') as mock_service:
            mock_service.side_effect = Exception("Database error")
            
            result = await transaction_service.get_recent_transactions(123456)
            
            assert result == []


class TestTelegramAnalyticsService:
    """Tests for TelegramAnalyticsService."""

    @pytest.mark.asyncio
    async def test_get_monthly_stats(self, analytics_service):
        """Test getting monthly statistics."""
        result = await analytics_service.get_monthly_stats(123456)
        
        assert result is not None
        assert 'total_spent' in result
        assert 'by_category' in result
        assert 'transaction_count' in result
        assert result['currency'] == 'USD'

    @pytest.mark.asyncio
    async def test_get_balance(self, analytics_service):
        """Test getting account balance."""
        result = await analytics_service.get_balance(123456)
        
        assert result is not None
        assert 'accounts' in result
        assert isinstance(result['accounts'], list)
        assert len(result['accounts']) > 0

    @pytest.mark.asyncio
    async def test_get_insights(self, analytics_service):
        """Test getting financial insights."""
        result = await analytics_service.get_insights(123456)
        
        assert result is not None
        assert 'savings_rate' in result
        assert 'spending_trend' in result
        assert 'insights' in result
        assert isinstance(result['insights'], list)

    @pytest.mark.asyncio
    async def test_get_monthly_stats_error(self, analytics_service):
        """Test error handling in stats calculation."""
        with patch('app.services.telegram_service.datetime') as mock_datetime:
            mock_datetime.side_effect = Exception("Calculation error")
            
            result = await analytics_service.get_monthly_stats(123456)
            
            assert result is None


class TestTelegramServiceIntegration:
    """Integration tests for Telegram services."""

    @pytest.mark.asyncio
    async def test_user_service_integration(self, user_service):
        """Test user service workflow."""
        # Create user mapping
        mapping = await user_service.get_or_create_user_mapping(123456, "testuser")
        assert mapping['is_active']
        
        # Get preferences
        prefs = await user_service.get_user_preferences(123456)
        assert prefs['language'] == 'en'
        
        # Update preferences
        result = await user_service.update_user_preferences(
            123456, {'language': 'ru'}
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_transaction_service_workflow(self, transaction_service):
        """Test transaction service workflow."""
        # Process expense
        with patch.object(transaction_service.transaction_intelligence, 'process_text_input') as mock_process:
            mock_process.return_value = {
                'merchant': 'test',
                'amount': 100,
                'currency': 'USD',
                'category': 'food',
                'confidence_score': 0.9,
            }
            
            txn = await transaction_service.process_expense_message(
                123456, "Test 100 USD"
            )
            assert txn is not None
            
            # Confirm transaction
            confirmed = await transaction_service.confirm_transaction(123456, "txn_1")
            assert confirmed is True

    @pytest.mark.asyncio
    async def test_analytics_service_workflow(self, analytics_service):
        """Test analytics service workflow."""
        # Get stats
        stats = await analytics_service.get_monthly_stats(123456)
        assert stats is not None
        assert stats['total_spent'] > 0
        
        # Get balance
        balance = await analytics_service.get_balance(123456)
        assert balance is not None
        assert len(balance['accounts']) > 0
        
        # Get insights
        insights = await analytics_service.get_insights(123456)
        assert insights is not None
        assert len(insights['insights']) > 0
