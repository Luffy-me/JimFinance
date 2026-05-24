# Phase 3: Telegram Bot - Complete Documentation

## Overview

Phase 3 implements the **Telegram Bot Interface** for JimFinance, enabling users to capture and manage transactions conversationally through Telegram. This phase integrates seamlessly with Phase 2's Transaction Intelligence Engine.

## Architecture

```
┌─────────────────────────────────────────────────┐
│         Telegram User                            │
│    (Sends messages/photos)                       │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│    Telegram Bot API                              │
│    (Webhook: POST /api/v1/telegram/webhook)     │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│    TelegramUpdateHandler                         │
│    - Routes updates to processors                │
│    - Message validation                          │
└────────────────┬─────────────────────────────────┘
                 │
       ┌─────────┼─────────┐
       │         │         │
       ▼         ▼         ▼
    Commands  Messages  Callbacks
       │         │         │
       └─────────┼─────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│    Message & Command Processors                  │
│    - Text parsing                                │
│    - Photo OCR handling                          │
│    - Command execution                           │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│    Telegram Service Layer                        │
│    - User management                             │
│    - Transaction processing                      │
│    - Analytics & stats                           │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│    Phase 2: Transaction Intelligence Engine      │
│    - Text normalization                          │
│    - Category classification                     │
│    - Duplicate detection                         │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│    Database & Services                           │
│    - User accounts                               │
│    - Transactions                                │
│    - Categories & preferences                    │
└──────────────────────────────────────────────────┘
```

## Core Components

### 1. TelegramBot Class (`app/integrations/telegram/bot.py`)

Wrapper around the `python-telegram-bot` library providing core bot operations.

**Key Methods:**
- `get_me()` - Get bot information
- `send_message()` - Send text messages with HTML/Markdown
- `send_photo()` - Send photos with captions
- `answer_callback_query()` - Handle inline button clicks
- `edit_message_text()` - Edit existing messages
- `set_webhook()` - Setup webhook for receiving updates
- `delete_webhook()` - Switch to polling mode
- `get_webhook_info()` - Get current webhook status

**Usage:**
```python
from app.integrations.telegram.bot import TelegramBot

bot = TelegramBot()
await bot.send_message(
    chat_id=123456,
    text="<b>Hello</b> world!",
    parse_mode="HTML"
)
```

### 2. TelegramUpdateHandler (`app/integrations/telegram/handler.py`)

Routes incoming updates to appropriate processors.

**Features:**
- Routes messages, callbacks, and edited messages
- Command vs regular message detection
- Error handling and logging
- Update validation

**Key Methods:**
- `handle_update()` - Main entry point for all updates
- `_handle_message()` - Process text/photo messages
- `_handle_callback_query()` - Process button clicks
- `_handle_edited_message()` - Handle message edits

### 3. MessageProcessor (`app/integrations/telegram/processors/message_processor.py`)

Handles text messages, photos, and generates confirmations.

**Features:**
- Text message parsing for transactions
- Photo upload handling
- Inline button confirmation flows
- Transaction confirmation/cancellation logic

**Key Methods:**
- `process_text_message()` - Parse expense messages
- `process_photo_message()` - Handle receipt photos
- `process_document_message()` - Handle documents
- `process_callback()` - Handle button interactions
- `_send_transaction_confirmation()` - Show confirmation UI

### 4. CommandProcessor (`app/integrations/telegram/processors/command_processor.py`)

Implements bot commands for user interactions.

**Supported Commands:**
- `/start` - Initialize bot and show welcome message
- `/help` - Show command help
- `/balance` - Display account balances
- `/recent` - Show last 5 transactions
- `/stats` - Monthly spending breakdown
- `/settings` - User preferences
- `/status` - Bot and system status

### 5. Telegram Service Layer (`app/services/telegram_service.py`)

High-level service for transaction and user management.

**Services:**
- `TelegramUserService` - User mapping and preferences
- `TelegramTransactionService` - Transaction operations
- `TelegramAnalyticsService` - Statistics and insights

## API Endpoints

### Webhook Endpoint
```
POST /api/v1/telegram/webhook
```
Receives incoming Telegram updates (messages, button clicks, etc).

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/telegram/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456,
    "message": {
      "message_id": 1,
      "date": 1234567890,
      "chat": {"id": 123456, "type": "private"},
      "from": {"id": 123456, "username": "user"},
      "text": "500 RUB coffee"
    }
  }'
```

### Setup Webhook
```
POST /api/v1/telegram/webhook/setup
Content-Type: application/json

{
  "url": "https://yourdomain.com/api/v1/telegram/webhook"
}

Response:
{
  "status": "success",
  "message": "Webhook configured successfully",
  "webhook_url": "https://yourdomain.com/api/v1/telegram/webhook"
}
```

### Get Webhook Info
```
GET /api/v1/telegram/webhook/info

Response:
{
  "status": "success",
  "webhook": {
    "url": "https://yourdomain.com/api/v1/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "ip_address": "192.168.1.1"
  }
}
```

### Delete Webhook
```
DELETE /api/v1/telegram/webhook

Response:
{
  "status": "success",
  "message": "Webhook deleted successfully"
}
```

### Get Bot Info
```
GET /api/v1/telegram/bot/info

Response:
{
  "status": "success",
  "bot_id": 123456789,
  "username": "jimfinance_bot",
  "first_name": "JimFinance",
  "is_bot": true
}
```

### Send Test Message
```
POST /api/v1/telegram/message/send?chat_id=123456&text=Hello%20World&parse_mode=HTML

Response:
{
  "status": "success",
  "message": {
    "message_id": 1,
    "chat_id": 123456,
    "text": "Hello World"
  }
}
```

### Health Check
```
GET /api/v1/telegram/health

Response:
{
  "status": "healthy",
  "service": "telegram_bot",
  "bot_username": "jimfinance_bot",
  "timestamp": "2024-05-24T18:37:55.251Z"
}
```

## User Workflow

### 1. Starting the Bot
```
User: /start
Bot: 👋 Welcome to JimFinance! I'm your AI-powered personal finance assistant...
```

### 2. Capturing an Expense
```
User: Starbucks 5 USD
Bot: ✅ Transaction Captured
     💰 Amount: 5.00 USD
     🏪 Merchant: starbucks
     🏷️ Category: food
     🎯 Confidence: 95%
     [✅ Confirm] [❌ Cancel] [✏️ Edit]
User: [clicks Confirm]
Bot: ✅ Transaction confirmed and saved!
```

### 3. Viewing Balance
```
User: /balance
Bot: 💰 Your Accounts
     🏦 Main (USD): $1,250.50
     💳 Credit Card (USD): $500.00 (available)
     💸 Savings (RUB): ₽50,000.00
     Total: ~$2,100 USD
```

### 4. Checking Stats
```
User: /stats
Bot: 📊 May 2024 Spending Summary
     🍽️ Food: $185.50 (28%)
     🚗 Transport: $125.00 (19%)
     ...
     💡 You're doing great! Keep it up!
```

## Message Format Examples

### Expense Capture Format
Users can send expenses in flexible formats:

```
• 500 RUB coffee
• Starbucks 5 USD
• Taxi 12.50
• Netflix subscription 12.99 USD
• Transfer to savings 1000
• 100 EUR shopping at Zara
```

**Parser handles:**
- Amount (with or without currency)
- Merchant name
- Optional description
- Multiple currencies (USD, RUB, EUR, GBP, INR)

### Receipt Photos
Users can send photos of receipts:
- Auto-OCR extraction (coming soon)
- Automatic categorization
- Duplicate detection

## Configuration

### Environment Variables
```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/api/v1/telegram/webhook
```

### Settings in Code
```python
from app.core.config import settings

# Telegram configuration
settings.TELEGRAM_BOT_TOKEN  # Bot token
settings.TELEGRAM_WEBHOOK_URL  # Webhook URL
```

## Security Considerations

1. **Webhook URL**: Must be HTTPS in production
2. **Bot Token**: Secure in environment variables
3. **Rate Limiting**: TODO - Implement to prevent abuse
4. **User Validation**: TODO - Verify Telegram signature
5. **Data Encryption**: Sensitive data stored securely

## Error Handling

### Message Processing Errors
```
Invalid format → Show usage examples
Parsing failure → Ask user to clarify
API error → Graceful degradation
```

### User Feedback
- ✅ Success messages with details
- ❌ Error messages with hints
- ℹ️ Info messages for status
- ⚠️ Warning messages for issues

## Testing

### Unit Tests
```bash
pytest backend/tests/test_telegram_processors.py -v
pytest backend/tests/test_telegram_handlers.py -v
```

### Integration Tests
```bash
pytest backend/tests/test_telegram_integration.py -v
```

### Manual Testing
1. Get bot token from @BotFather on Telegram
2. Set `TELEGRAM_BOT_TOKEN` in `.env`
3. Start bot: `python -m uvicorn main:app --reload`
4. Send test messages via Telegram

## Deployment

### Production Setup
1. Get HTTPS certificate
2. Setup webhook URL
3. Configure environment variables
4. Deploy using Docker or Kubernetes

### Local Development
```bash
# Delete webhook for polling mode
DELETE /api/v1/telegram/webhook

# Run locally with polling
python -m uvicorn main:app --reload
```

## Future Enhancements

1. **Photo OCR** - Automatic receipt reading
2. **Recurring Subscriptions** - Track monthly bills
3. **Budget Alerts** - Notify when spending exceeds budget
4. **Expense Splitting** - Share expenses with friends
5. **Voice Messages** - Support audio transcription
6. **Scheduled Reports** - Weekly/monthly summaries
7. **Inline Queries** - Quick transaction search
8. **Multi-language** - Full localization support
9. **Web App Integration** - Telegram Mini App
10. **Advanced Analytics** - AI-powered insights

## Troubleshooting

### Webhook not receiving updates
- Check webhook URL is HTTPS
- Verify TELEGRAM_BOT_TOKEN is correct
- Use `/api/v1/telegram/webhook/info` to check status
- Try deleting and re-setting webhook

### Messages not being processed
- Check bot logs for errors
- Verify update handler is properly configured
- Ensure transaction service is working

### Transaction not created
- Check Phase 2 transaction intelligence service
- Verify account_id exists
- Check database connectivity

## API Documentation

Full API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## References

- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Phase 2: Transaction Intelligence](./PHASE2_TRANSACTION_INTELLIGENCE.md)
- [Architecture Overview](./ARCHITECTURE.md)
