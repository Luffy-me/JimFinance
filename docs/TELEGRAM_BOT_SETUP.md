# Telegram Bot Setup Guide

This guide explains how to set up and run the JimFinance Telegram Bot.

## Prerequisites

- Python 3.11+
- A Telegram account
- The JimFinance backend running (see DEVELOPMENT.md)

## Step 1: Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send the command `/newbot`
3. Follow the prompts to create a new bot:
   - Choose a name (e.g., "JimFinance Bot")
   - Choose a username (e.g., "jimfinance_bot") - must end with "_bot"
4. BotFather will send you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyzABCdefGHI`

## Step 2: Configure Environment

1. Open `.env` file in the project root
2. Add or update:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/api/v1/telegram/webhook
```

For local development (without HTTPS):
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
# Leave TELEGRAM_WEBHOOK_URL empty for polling mode
```

## Step 3: Run the Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

The API should be available at `http://localhost:8000`

## Step 4: Set Up Webhook (Production Only)

For production with HTTPS:

```bash
curl -X POST http://localhost:8000/api/v1/telegram/webhook/setup \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourdomain.com/api/v1/telegram/webhook"
  }'
```

## Step 5: Test the Bot

### Option A: Test via Telegram (Local Development)

1. Go to your Telegram bot (@BotFather told you the username)
2. Send `/start`
3. Bot should respond with welcome message
4. Send a message like `500 RUB coffee` to test transaction capture

### Option B: Test via API

Get bot info:
```bash
curl http://localhost:8000/api/v1/telegram/bot/info
```

Send a test message:
```bash
curl -X POST "http://localhost:8000/api/v1/telegram/message/send?chat_id=YOUR_CHAT_ID&text=Hello%20World"
```

Check health:
```bash
curl http://localhost:8000/api/v1/telegram/health
```

## Testing Workflow

### 1. Basic Message Flow
```
User: Starbucks 5 USD
Bot: ✅ Transaction Captured
     💰 Amount: 5.00 USD
     🏪 Merchant: starbucks
     🏷️ Category: food
     🎯 Confidence: 95%
     [✅ Confirm] [❌ Cancel] [✏️ Edit]
```

### 2. Command Testing
- `/start` - Welcome message
- `/help` - Show available commands
- `/balance` - Show account balance
- `/recent` - Show last 5 transactions
- `/stats` - Show monthly stats
- `/settings` - Show preferences
- `/status` - Show system status

### 3. Receipt Photo Testing (Coming Soon)
- Send a photo of a receipt
- Bot should extract text via OCR
- Show confirmation with extracted details

## Running Tests

```bash
# Run all Telegram tests
pytest backend/tests/test_telegram_*.py -v

# Run specific test file
pytest backend/tests/test_telegram_commands.py -v

# Run specific test
pytest backend/tests/test_telegram_commands.py::TestCommandProcessor::test_start_command -v

# Run with coverage
pytest backend/tests/test_telegram_*.py --cov=app.integrations.telegram --cov=app.services.telegram_service
```

## Troubleshooting

### Bot not responding
1. Check `TELEGRAM_BOT_TOKEN` is correct
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check logs: `tail -f backend/logs/app.log`

### Messages not being received
1. For webhooks: Check webhook URL is HTTPS and publicly accessible
2. For polling: Make sure bot is connected to Telegram API
3. Check Telegram bot settings: `curl http://localhost:8000/api/v1/telegram/webhook/info`

### Transaction not being created
1. Check transaction intelligence service is working
2. Verify message format: `merchant amount currency`
3. Check database connection

### Port 8000 already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
python -m uvicorn main:app --reload --port 8001
```

## Development Tips

### Debug Mode
Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python -m uvicorn main:app --reload
```

### Mock Testing
Use the test suite to mock Telegram API responses:
```bash
pytest backend/tests/test_telegram_messages.py::TestMessageProcessor::test_process_text_message_success -v
```

### Database State
To reset database:
```bash
# Backup current database
cp backend/jimfinance.db backend/jimfinance.db.bak

# Delete database (will be recreated)
rm backend/jimfinance.db

# Restart backend
python -m uvicorn main:app --reload
```

## API Endpoints Reference

### Webhook
```
POST /api/v1/telegram/webhook
```
Receives Telegram updates (automatic)

### Setup Webhook
```
POST /api/v1/telegram/webhook/setup
{
  "url": "https://yourdomain.com/api/v1/telegram/webhook"
}
```

### Get Webhook Info
```
GET /api/v1/telegram/webhook/info
```

### Delete Webhook
```
DELETE /api/v1/telegram/webhook
```

### Get Bot Info
```
GET /api/v1/telegram/bot/info
```

### Send Message
```
POST /api/v1/telegram/message/send?chat_id=123456&text=Hello&parse_mode=HTML
```

### Health Check
```
GET /api/v1/telegram/health
```

## Production Deployment

### Requirements
1. HTTPS certificate (valid SSL/TLS)
2. Public domain/IP
3. Firewall rules allowing inbound on port 443

### Steps
1. Set up HTTPS reverse proxy (nginx, etc.)
2. Configure `TELEGRAM_WEBHOOK_URL` to HTTPS endpoint
3. Set `TELEGRAM_BOT_TOKEN` from environment
4. Call webhook setup: `POST /api/v1/telegram/webhook/setup`
5. Monitor webhook info: `GET /api/v1/telegram/webhook/info`

### Example nginx config
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/v1/telegram/webhook {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Next Steps

1. **Phase 3.1**: Finalize webhook setup and authentication
2. **Phase 3.2**: Implement receipt OCR integration
3. **Phase 3.3**: Add confirmation workflows
4. **Phase 3.4**: Implement advanced commands
5. **Phase 3.5**: Add user preferences and settings

## Support

- API Documentation: `/docs`
- Telegram Bot API: https://core.telegram.org/bots/api
- python-telegram-bot: https://docs.python-telegram-bot.org/

## Security Notes

⚠️ **Important:**
- Never commit `TELEGRAM_BOT_TOKEN` to git
- Always use HTTPS for webhooks in production
- Validate webhook requests (implement signature verification)
- Use environment variables for all secrets
- Rotate bot token if compromised

## References

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Library](https://docs.python-telegram-bot.org/)
- [JimFinance Architecture](./ARCHITECTURE.md)
- [Phase 2: Transaction Intelligence](./PHASE2_TRANSACTION_INTELLIGENCE.md)
- [Development Guide](./DEVELOPMENT.md)
