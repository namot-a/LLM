"""Telegram bot with improved error handling and user experience."""
import asyncio
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
import httpx
from app.config import settings
from app.logger import get_logger
from app.exceptions import TelegramError
from app.db import get_db
from app.models import TelegramUser
from sqlalchemy import select

logger = get_logger(__name__)

router = APIRouter()

# Bot setup
bot = Bot(settings.telegram_bot_token)
dp = Dispatcher()


async def is_user_allowed(user_id: int) -> bool:
    """Check if user is allowed to use the bot (check database)."""
    try:
        async for db in get_db():
            result = await db.execute(
                select(TelegramUser).where(
                    TelegramUser.user_id == user_id,
                    TelegramUser.is_active == True
                )
            )
            user = result.scalar_one_or_none()
            return user is not None
    except Exception as e:
        logger.error("Error checking user access", user_id=user_id, error=str(e))
        # Fallback to env check if DB fails
        allowed_users = set(settings.get_allowed_user_ids()) if settings.get_allowed_user_ids() else None
        if allowed_users is None:
            return True
        return user_id in allowed_users


def create_feedback_keyboard(message_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for feedback."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👍 Хорошо", callback_data=f"feedback_good_{message_id}"),
            InlineKeyboardButton(text="👎 Плохо", callback_data=f"feedback_bad_{message_id}")
        ]
    ])


async def send_typing_action(chat_id: int) -> None:
    """Send typing action to user."""
    try:
        await bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception as e:
        logger.warning("Failed to send typing action", chat_id=chat_id, error=str(e))


async def call_api(query: str, user_id: int) -> dict:
    """Call the API to process the query."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{settings.api_url}/api/v1/query",
                json={
                    "question": query,
                    "telegram_user_id": user_id,
                    "include_sources": True
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error("API timeout", user_id=user_id, query=query[:100])
            raise TelegramError("API request timeout")
        except httpx.HTTPStatusError as e:
            logger.error("API HTTP error", status_code=e.response.status_code, user_id=user_id)
            raise TelegramError(f"API error: {e.response.status_code}")
        except Exception as e:
            logger.error("API call failed", error=str(e), user_id=user_id)
            raise TelegramError("API call failed")


async def format_response(data: dict) -> str:
    """Format API response for Telegram."""
    answer = data.get("answer", "Извините, не удалось получить ответ.")
    sources = data.get("sources", [])
    
    if not sources:
        return answer
    
    # Format sources
    sources_text = "\n\n📚 **Источники:**\n"
    for i, source in enumerate(sources[:3], 1):  # Limit to 3 sources
        title = source.get("title", "Без названия")
        url = source.get("url", "")
        section = source.get("section", "")
        
        if section:
            sources_text += f"{i}. [{title}]({url}) — {section}\n"
        else:
            sources_text += f"{i}. [{title}]({url})\n"
    
    return answer + sources_text


@dp.message(Command("start"))
async def handle_start(message: types.Message):
    """Handle /start command - fully error-resistant."""
    try:
        user_id = message.from_user.id
        
        # Check if user is allowed
        if not await is_user_allowed(user_id):
            try:
                await message.reply(
                    "🚫 Доступ ограничен. Обратитесь к администратору для получения доступа к боту.",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            return
        
        welcome_text = (
            "👋 Привет! Я консультирую по регламентам в компании HuntIT.\n\n"
            "Задай свой вопрос, и я найду релевантную информацию в наших документах.\n\n"
            "Например:\n"
            "• Как провести собеседование?\n"
            "• Какие требования к внешнему виду?\n"
            "• Как назначить скрининг?\n\n"
            "Просто напиши свой вопрос! 🤖"
        )
        
        try:
            await message.reply(welcome_text, parse_mode="Markdown")
            logger.info("Start command processed", user_id=user_id)
        except Exception as e:
            logger.error("Error sending start message", error=str(e), user_id=user_id)
            
    except Exception as e:
        logger.error("Critical error in start handler", error=str(e))
        # Bot must never crash


@dp.message()
async def handle_message(message: types.Message):
    """Handle incoming messages - fully error-resistant."""
    user_id = None
    try:
        user_id = message.from_user.id
        
        # Check if it's a private chat
        if message.chat.type not in ("private",):
            return
        
        # Check if user is allowed
        if not await is_user_allowed(user_id):
            try:
                await message.reply(
                    "🚫 Доступ ограничен. Обратитесь к администратору для получения доступа к боту.",
                    parse_mode="Markdown"
                )
            except Exception:
                pass  # Ignore if can't send response
            return
        
        # Check if message has text
        text = (message.text or "").strip()
        if not text:
            try:
                await message.reply("Пожалуйста, отправьте текстовое сообщение с вашим вопросом.")
            except Exception:
                pass
            return
        
        # Check message length
        if len(text) > 1000:
            try:
                await message.reply("Сообщение слишком длинное. Пожалуйста, сократите вопрос до 1000 символов.")
            except Exception:
                pass
            return
        
        logger.info("Processing message", user_id=user_id, message_length=len(text))
        
        # Send typing action
        try:
            await send_typing_action(message.chat.id)
        except Exception:
            pass  # Non-critical
        
        # Call API
        try:
            data = await call_api(text, user_id)
        except TelegramError as e:
            try:
                await message.reply(f"❌ Ошибка обработки запроса: {str(e)}")
            except Exception:
                pass
            return
        except Exception as e:
            logger.error("API call error", error=str(e), user_id=user_id)
            try:
                await message.reply("❌ Ошибка обработки запроса. Попробуйте позже.")
            except Exception:
                pass
            return
        
        # Format and send response
        try:
            response_text = await format_response(data)
            
            # Try to send with Markdown first
            try:
                await message.reply(
                    response_text,
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                    reply_markup=create_feedback_keyboard(message.message_id)
                )
                logger.info("Response sent with Markdown", user_id=user_id, response_length=len(response_text))
            except TelegramBadRequest as markdown_error:
                # If Markdown fails, try without it
                logger.warning("Markdown parse failed, sending as plain text", error=str(markdown_error))
                await message.reply(
                    response_text,
                    disable_web_page_preview=True,
                    reply_markup=create_feedback_keyboard(message.message_id)
                )
                logger.info("Response sent as plain text", user_id=user_id)
            
        except TelegramBadRequest as e:
            logger.error("Telegram bad request", error=str(e), user_id=user_id)
            try:
                # Last resort - send simple error message
                await message.reply("Получен ответ, но не удалось отправить. Попробуйте переформулировать вопрос.")
            except Exception:
                pass
        except Exception as e:
            logger.error("Error sending response", error=str(e), user_id=user_id)
            try:
                await message.reply("❌ Произошла ошибка. Попробуйте позже.")
            except Exception:
                pass
        
    except Exception as e:
        logger.error("Critical error in message handler", error=str(e), user_id=user_id)
        # Try to send error message but don't crash if it fails
        try:
            if message and message.chat:
                await message.reply("❌ Произошла критическая ошибка. Бот продолжает работу.")
        except Exception:
            pass  # Bot must never crash


@dp.callback_query()
async def handle_callback_query(callback_query: types.CallbackQuery):
    """Handle callback queries (feedback buttons) - fully error-resistant."""
    user_id = None
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        if not data.startswith("feedback_"):
            try:
                await callback_query.answer("Неизвестная команда")
            except Exception:
                pass
            return
        
        # Parse feedback data
        parts = data.split("_")
        if len(parts) != 3:
            try:
                await callback_query.answer("Ошибка в данных")
            except Exception:
                pass
            return
        
        rating = parts[1]  # "good" or "bad"
        message_id = int(parts[2])
        
        # Submit feedback via API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.api_url}/api/v1/feedback",
                    json={
                        "message_id": message_id,
                        "rating": rating,
                        "comment": None
                    },
                    params={"telegram_user_id": user_id}
                )
                response.raise_for_status()
        except Exception as e:
            logger.error("Failed to submit feedback", error=str(e), user_id=user_id)
            try:
                await callback_query.answer("❌ Ошибка отправки отзыва")
            except Exception:
                pass
            return
        
        # Update button text
        try:
            if rating == "good":
                await callback_query.answer("✅ Спасибо за положительный отзыв!")
            else:
                await callback_query.answer("❌ Спасибо за отзыв. Мы учтем ваше мнение.")
            
            # Remove keyboard
            await callback_query.message.edit_reply_markup(reply_markup=None)
            
            logger.info("Feedback submitted", user_id=user_id, rating=rating, message_id=message_id)
        except Exception as e:
            logger.error("Error updating callback", error=str(e), user_id=user_id)
        
    except Exception as e:
        logger.error("Critical error in callback handler", error=str(e), user_id=user_id)
        try:
            if callback_query:
                await callback_query.answer("❌ Ошибка обработки отзыва")
        except Exception:
            pass  # Bot must never crash


@router.post(f"/telegram/webhook/{{secret}}")
async def telegram_webhook(secret: str, request: Request):
    """Handle Telegram webhook."""
    try:
        if secret != settings.webhook_secret_path:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        data = await request.json()
        update = Update.model_validate(data)
        
        # Process update
        await dp.feed_update(bot, update)
        
        return {"ok": True}
        
    except Exception as e:
        logger.error("Webhook error", error=str(e))
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def set_webhook():
    """Set Telegram webhook URL."""
    try:
        webhook_url = f"{settings.api_url}/telegram/webhook/{settings.webhook_secret_path}"
        await bot.set_webhook(url=webhook_url)
        logger.info("Webhook set", url=webhook_url)
    except Exception as e:
        logger.error("Failed to set webhook", error=str(e))


async def delete_webhook():
    """Delete Telegram webhook."""
    try:
        await bot.delete_webhook()
        logger.info("Webhook deleted")
    except Exception as e:
        logger.error("Failed to delete webhook", error=str(e))
