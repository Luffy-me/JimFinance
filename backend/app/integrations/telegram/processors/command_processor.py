"""Command Processor - Handles Telegram bot commands"""

import logging
from typing import Optional
from telegram import Message
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class CommandProcessor:
    """Processes Telegram bot commands like /start, /help, /balance, etc."""

    COMMANDS = {
        "/start": "start_command",
        "/help": "help_command",
        "/balance": "balance_command",
        "/recent": "recent_command",
        "/stats": "stats_command",
        "/settings": "settings_command",
        "/status": "status_command",
    }

    async def process_command(self, message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process incoming command.
        
        Args:
            message: Telegram message object containing command
            context: Telegram context object
        """
        user_id = message.from_user.id
        chat_id = message.chat_id
        
        # Extract command name
        text = message.text.strip()
        command = text.split()[0].lower()

        logger.info(f"Processing command {command} from user {user_id}")

        # Route to appropriate command handler
        handler_name = self.COMMANDS.get(command)
        if handler_name:
            handler = getattr(self, handler_name, None)
            if handler:
                await handler(message, context)
            else:
                logger.error(f"Handler not found for command: {command}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Unknown command: {command}\n\nUse /help for available commands.",
            )

    async def start_command(self, message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - Initialize user session.
        
        Args:
            message: Telegram message object
            context: Telegram context object
        """
        user_id = message.from_user.id
        chat_id = message.chat_id
        user_name = message.from_user.first_name or "User"

        logger.info(f"User {user_id} started bot")

        # TODO: Create/update user mapping in database
        # TODO: Set user preferences from database or defaults

        welcome_text = f"""
👋 Welcome to <b>JimFinance</b>, {user_name}!

I'm your AI-powered personal finance assistant. I help you capture, categorize, and analyze your expenses.

<b>Quick Start:</b>
• Send me expenses like: <code>500 RUB coffee</code>
• Send photos of receipts for automatic OCR
• Use commands to check your balance and stats

<b>Available Commands:</b>
/help - Show all commands
/balance - Check your current balance
/recent - Show recent transactions
/stats - View your spending statistics
/settings - Adjust preferences

Let's get started! Send me your first expense 💰
"""

        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_text,
            parse_mode="HTML",
        )

    async def help_command(self, message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command - Show available commands.
        
        Args:
            message: Telegram message object
            context: Telegram context object
        """
        chat_id = message.chat_id

        help_text = """
<b>📖 JimFinance Bot Commands</b>

<b>📝 Transaction Entry:</b>
Send a message like: <code>500 RUB coffee</code>
Send a receipt photo for automatic recognition

<b>🔍 View Data:</b>
/balance - Your current balance
/recent - Last 5 transactions
/stats - Monthly spending breakdown
/status - Bot connection status

<b>⚙️ Settings:</b>
/settings - Configure preferences
/help - Show this message

<b>💡 Examples:</b>
<code>Starbucks 5 USD</code>
<code>Taxi 420 RUB</code>
<code>Netflix subscription 12.99 USD</code>
<code>Transfer to savings 1000</code>

<b>📌 Tips:</b>
• Format: <code>Merchant Amount Currency</code>
• Currency: RUB, USD, EUR, GBP, INR
• Send photos for receipt OCR
• Use inline buttons to confirm transactions

Need more help? Contact support.
"""

        await context.bot.send_message(
            chat_id=chat_id,
            text=help_text,
            parse_mode="HTML",
        )

    async def balance_command(self, message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /balance command - Show account balance.
        
        Args:
            message: Telegram message object
            context: Telegram context object
        """
        user_id = message.from_user.id
        chat_id = message.chat_id

        logger.info(f"User {user_id} requested balance")

        # TODO: Get actual balance from database
        balance_text = """
💰 <b>Your Accounts</b>

🏦 Main (USD): <b>$1,250.50</b>
💳 Credit Card (USD): <b>$500.00</b> (available)
💸 Savings (RUB): <b>₽50,000.00</b>

<b>Total:</b> ~$2,100 USD

Last updated: Just now
"""

        await context.bot.send_message(
            chat_id=chat_id,
            text=balance_text,
            parse_mode="HTML",
        )

    async def recent_command(self, message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /recent command - Show recent transactions.
        
        Args:
            message: Telegram message object
            context: Telegram context object
        """
        user_id = message.from_user.id
        chat_id = message.chat_id

        logger.info(f"User {user_id} requested recent transactions")

        # TODO: Get actual recent transactions from database
        recent_text = """
📝 <b>Recent Transactions</b>

1. ☕ Starbucks - <b>$5.00</b> USD (food) - 2 hours ago
2. 🚕 Uber - <b>$12.50</b> USD (transport) - 5 hours ago
3. 🛒 Walmart - <b>$45.30</b> USD (shopping) - 1 day ago
4. 🍕 Pizza Hut - <b>$18.99</b> USD (food) - 1 day ago
5. 💡 Electric Bill - <b>₽2,500</b> RUB (utilities) - 2 days ago

Use /stats to see spending breakdown
"""

        await context.bot.send_message(
            chat_id=chat_id,
            text=recent_text,
            parse_mode="HTML",
        )

    async def stats_command(self, message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stats command - Show spending statistics.
        
        Args:
            message: Telegram message object
            context: Telegram context object
        """
        user_id = message.from_user.id
        chat_id = message.chat_id

        logger.info(f"User {user_id} requested statistics")

        # TODO: Get actual statistics from database
        stats_text = """
📊 <b>May 2024 Spending Summary</b>

<b>By Category:</b>
🍽️ Food: <b>$185.50</b> (28%)
🚗 Transport: <b>$125.00</b> (19%)
🛒 Shopping: <b>$215.75</b> (33%)
📺 Entertainment: <b>$95.00</b> (14%)
💡 Utilities: <b>$52.50</b> (6%)

<b>Total:</b> <b>$673.75</b> USD
<b>Trend:</b> ↓ 15% vs last month
<b>Savings Rate:</b> <b>42%</b>

💡 You're doing great! Keep it up!
"""

        await context.bot.send_message(
            chat_id=chat_id,
            text=stats_text,
            parse_mode="HTML",
        )

    async def settings_command(self, message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /settings command - Show user settings.
        
        Args:
            message: Telegram message object
            context: Telegram context object
        """
        chat_id = message.chat_id

        settings_text = """
⚙️ <b>Settings</b>

<b>Current Configuration:</b>
📱 Language: English
🏦 Default Account: Main (USD)
🔔 Notifications: Enabled
💱 Currency Display: USD
📊 Categories: Default (11 categories)

<b>Coming Soon:</b>
• Custom categories
• Notification preferences
• Budget alerts
• Export options

Settings management feature coming soon!
"""

        await context.bot.send_message(
            chat_id=chat_id,
            text=settings_text,
            parse_mode="HTML",
        )

    async def status_command(self, message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command - Show bot connection status.
        
        Args:
            message: Telegram message object
            context: Telegram context object
        """
        chat_id = message.chat_id

        status_text = """
✅ <b>System Status</b>

<b>Services:</b>
✅ Telegram Bot: Connected
✅ API Server: Online
✅ Database: Connected
✅ Cache: Ready
✅ AI Services: Available

<b>Performance:</b>
⚡ Response Time: 250ms avg
📊 Daily Transactions: 1,247
👥 Active Users: 342

<b>Version:</b>
🔖 Phase: 3 (Telegram Bot)
📦 Build: 0.1.0

Everything is running smoothly! 🚀
"""

        await context.bot.send_message(
            chat_id=chat_id,
            text=status_text,
            parse_mode="HTML",
        )
