# Phase 3 Telegram Bot - Quick Reference Guide

## 🚀 Quick Start

1. **Get Bot Token**
   - Talk to @BotFather on Telegram
   - Create new bot, get token

2. **Configure**
   ```bash
   echo "TELEGRAM_BOT_TOKEN=your_token_here" >> .env
   ```

3. **Run Backend**
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

4. **Test Bot**
   - Open Telegram and find your bot
   - Send `/start`

## 📡 API Endpoints

### Core Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/telegram/webhook` | POST | Receive Telegram updates |
| `/api/v1/telegram/webhook/setup` | POST | Setup webhook URL |
| `/api/v1/telegram/webhook/info` | GET | Get webhook status |
| `/api/v1/telegram/webhook` | DELETE | Delete webhook |
| `/api/v1/telegram/bot/info` | GET | Get bot information |
| `/api/v1/telegram/health` | GET | Health check |
| `/api/v1/telegram/message/send` | POST | Send test message |

### Example Requests

**Setup Webhook:**
```bash
curl -X POST http://localhost:8000/api/v1/telegram/webhook/setup \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/api/v1/telegram/webhook"}'
```

**Get Bot Info:**
```bash
curl http://localhost:8000/api/v1/telegram/bot/info
```

**Send Message:**
```bash
curl -X POST "http://localhost:8000/api/v1/telegram/message/send?chat_id=123456&text=Hello%20World"
```

**Check Health:**
```bash
curl http://localhost:8000/api/v1/telegram/health
```

## 🤖 Bot Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/start` | Initialize bot | `/start` |
| `/help` | Show help | `/help` |
| `/balance` | Check balance | `/balance` |
| `/recent` | Recent transactions | `/recent` |
| `/stats` | Monthly stats | `/stats` |
| `/settings` | Preferences | `/settings` |
| `/status` | System status | `/status` |

## 💬 Message Format

Send expenses as:
```
[Merchant] [Amount] [Currency] [Description]
```

Examples:
- `Starbucks 5 USD coffee`
- `500 RUB taxi`
- `Netflix 12.99 USD subscription`
- `Uber 25 EUR dinner in Paris`

## 📁 File Structure

```
backend/
├── app/
│   ├── integrations/
│   │   └── telegram/
│   │       ├── bot.py                 # Core bot wrapper
│   │       ├── handler.py             # Update handler
│   │       └── processors/
│   │           ├── message_processor.py
│   │           └── command_processor.py
│   ├── api/v1/endpoints/
│   │   └── telegram.py                # API endpoints
│   └── services/
│       └── telegram_service.py        # Business logic
├── tests/
│   ├── test_telegram_bot.py
│   ├── test_telegram_commands.py
│   ├── test_telegram_messages.py
│   └── test_telegram_service.py
└── docs/
    ├── PHASE3_TELEGRAM_BOT.md
    ├── TELEGRAM_BOT_SETUP.md
    └── PHASE3_ROADMAP.md
```

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/test_telegram*.py -v

# Run specific test
pytest backend/tests/test_telegram_commands.py::TestCommandProcessor::test_start_command -v

# Run with coverage
pytest backend/tests/test_telegram*.py --cov=app.integrations.telegram
```

## 🔧 Configuration

### Environment Variables
```bash
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/api/v1/telegram/webhook
```

### Supported Currencies
- USD (US Dollar)
- RUB (Russian Ruble)
- EUR (Euro)
- GBP (British Pound)
- INR (Indian Rupee)

### Supported Categories
- food (🍽️)
- transport (🚗)
- entertainment (📺)
- utilities (💡)
- healthcare (⚕️)
- shopping (🛒)
- subscriptions (📺)
- salary (💰)
- investment (📈)
- transfer (💸)
- other (❓)

## 🐛 Troubleshooting

**Bot not responding?**
- Check token is correct
- Verify backend is running
- Check logs: `tail -f backend/logs/app.log`

**Webhook errors?**
- Must be HTTPS in production
- Domain must be public
- Check webhook info: `GET /api/v1/telegram/webhook/info`

**Transaction not saved?**
- Verify message format
- Check database connection
- Review logs for parsing errors

## 📚 Documentation

- **Full Docs**: [PHASE3_TELEGRAM_BOT.md](./PHASE3_TELEGRAM_BOT.md)
- **Setup Guide**: [TELEGRAM_BOT_SETUP.md](./TELEGRAM_BOT_SETUP.md)
- **Roadmap**: [PHASE3_ROADMAP.md](./PHASE3_ROADMAP.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)

## 🔐 Security

- ✅ No stack traces in error messages
- ✅ Token stored in environment variables
- ✅ HTTPS required for webhooks
- ✅ Input validation enabled
- ⚠️ TODO: Webhook signature verification
- ⚠️ TODO: Rate limiting per user

## 📊 Status

- **Phase 3.1**: ✅ COMPLETE (Core Infrastructure)
- **Phase 3.2**: ⏳ PENDING (Receipt OCR)
- **Phase 3.3**: ⏳ PENDING (Confirmation Workflows)
- **Phase 3.4**: ⏳ PENDING (Advanced Commands)
- **Phase 3.5**: ⏳ PENDING (User Preferences)

See [PHASE3_ROADMAP.md](./PHASE3_ROADMAP.md) for details on remaining phases.

## 🎯 Next Steps

1. Deploy backend with HTTPS
2. Set webhook URL to production endpoint
3. Test transaction capture end-to-end
4. Begin Phase 3.2: Receipt OCR Integration
5. Add more advanced commands and features

## 📞 Support

- Issues: GitHub Issues
- Questions: Check documentation
- Telegram Bot API: https://core.telegram.org/bots/api
- python-telegram-bot: https://docs.python-telegram-bot.org/

---

**Last Updated**: May 24, 2024  
**Status**: Phase 3.1 Complete ✅
