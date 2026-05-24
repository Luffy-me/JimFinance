"""Telegram Bot API Endpoints"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.integrations.telegram.bot import TelegramBot
from app.integrations.telegram.handler import TelegramUpdateHandler
from telegram import Update
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Initialize bot and handler
telegram_bot = TelegramBot()
update_handler = TelegramUpdateHandler()


class WebhookSetupRequest(BaseModel):
    """Request model for setting up webhook."""
    url: str


class WebhookSetupResponse(BaseModel):
    """Response model for webhook setup."""
    status: str
    message: str
    webhook_url: str


class BotInfoResponse(BaseModel):
    """Response model for bot info."""
    status: str
    bot_id: int
    username: str
    first_name: str
    is_bot: bool


@router.post("/webhook", status_code=200)
async def telegram_webhook(request: Request) -> Dict[str, Any]:
    """
    Receive Telegram webhook updates.

    This endpoint receives incoming Telegram messages and updates.
    Telegram sends a POST request with the update data.

    Args:
        request: FastAPI request object

    Returns:
        JSON response indicating success
    """
    try:
        # Get JSON data from request
        data = await request.json()

        # Verify it's a valid update (basic validation)
        if "update_id" not in data:
            logger.warning("Received invalid update data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid update data",
            )

        # Parse update
        update = Update.de_json(data, telegram_bot.bot)

        if update:
            logger.debug(f"Received update {update.update_id}")
            
            # Process update asynchronously
            # Note: In production, this should be queued to a task processor
            try:
                from telegram.ext import ContextTypes
                # Create a minimal context
                # In production, use proper ApplicationContext
                class MockContext:
                    def __init__(self, bot):
                        self.bot = bot
                
                context = MockContext(telegram_bot.bot)
                await update_handler.handle_update(update, context)
            except Exception as e:
                logger.error(f"Error processing update: {e}", exc_info=True)
        else:
            logger.warning("Failed to parse update")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error in webhook endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/webhook/setup", response_model=WebhookSetupResponse)
async def setup_webhook(payload: WebhookSetupRequest) -> WebhookSetupResponse:
    """
    Setup Telegram webhook for receiving updates.

    Instead of polling for updates, Telegram will send POST requests to this URL.

    Args:
        payload: Webhook setup request with URL

    Returns:
        Webhook setup response

    Example:
        POST /api/v1/telegram/webhook/setup
        {
            "url": "https://yourapi.com/api/v1/telegram/webhook"
        }
    """
    try:
        webhook_url = payload.url
        logger.info(f"Setting up webhook: {webhook_url}")

        # Set webhook on Telegram servers
        await telegram_bot.set_webhook(webhook_url)

        return WebhookSetupResponse(
            status="success",
            message="Webhook configured successfully",
            webhook_url=webhook_url,
        )
    except Exception as e:
        logger.error(f"Failed to setup webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to setup webhook: {str(e)}",
        )


@router.get("/webhook/info")
async def get_webhook_info() -> Dict[str, Any]:
    """
    Get current webhook information.

    Returns:
        Webhook status and configuration
    """
    try:
        info = await telegram_bot.get_webhook_info()
        return {
            "status": "success",
            "webhook": info,
        }
    except Exception as e:
        logger.error(f"Failed to get webhook info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get webhook info",
        )


@router.delete("/webhook")
async def delete_webhook() -> Dict[str, Any]:
    """
    Delete webhook and switch to polling mode.

    This is useful for local development or testing.

    Returns:
        Status of webhook deletion
    """
    try:
        logger.info("Deleting webhook")
        await telegram_bot.delete_webhook()

        return {
            "status": "success",
            "message": "Webhook deleted successfully",
        }
    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete webhook",
        )


@router.get("/bot/info", response_model=BotInfoResponse)
async def get_bot_info() -> BotInfoResponse:
    """
    Get bot information.

    Returns:
        Bot details (ID, username, etc)
    """
    try:
        info = await telegram_bot.get_me()
        return BotInfoResponse(
            status="success",
            bot_id=info["id"],
            username=info["username"],
            first_name=info["first_name"],
            is_bot=info["is_bot"],
        )
    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get bot info",
        )


@router.post("/message/send")
async def send_message(
    chat_id: int, text: str, parse_mode: str = "HTML"
) -> Dict[str, Any]:
    """
    Send a test message to a chat.

    This is useful for testing the bot connection.

    Args:
        chat_id: Telegram chat ID
        text: Message text
        parse_mode: Message format (HTML, Markdown, etc)

    Returns:
        Message details
    """
    try:
        result = await telegram_bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
        )
        return {
            "status": "success",
            "message": result,
        }
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send message: {str(e)}",
        )


@router.get("/health")
async def telegram_health() -> Dict[str, Any]:
    """
    Health check for Telegram bot integration.

    Returns:
        Health status
    """
    try:
        # Try to get bot info to verify connection
        info = await telegram_bot.get_me()
        return {
            "status": "healthy",
            "service": "telegram_bot",
            "bot_username": info["username"],
            "timestamp": None,  # TODO: Add timestamp
        }
    except Exception as e:
        logger.error(f"Telegram health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "telegram_bot",
            "error": str(e),
        }
