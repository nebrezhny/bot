from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import ChatActions, Message

from bot.core.config import settings
from bot.core.state import db, redis
from bot.services.classifier import classify_text
from bot.services.limiter import apply_limit
from bot.services.solver import LimitExceeded, solve_photo, solve_text
from bot.services.db import Database

router = Router()
logger = logging.getLogger(__name__)


def premium_keyboard() -> dict:
    return {
        'inline_keyboard': [[{'text': 'Купить доступ', 'callback_data': 'pack_50'}]],
    }


@router.message(Command('start') | Command('help') | Command('status') | Command('premium'))
async def ignore_commands(message: Message) -> None:
    return


@router.message()
async def handle_message(message: Message) -> None:
    if db is None or redis is None:
        await message.answer('Сервис временно недоступен, попробуй позже.')
        return

    if message.photo:
        await handle_photo(message)
    elif message.text:
        await handle_text(message)
    else:
        await message.answer('Отправьте текст задачи или фото.')


async def handle_text(message: Message) -> None:
    assert db is not None and redis is not None
    user = await db.ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    allowed, reason = await apply_limit(user, redis, db)
    if not allowed:
        await message.answer(
            'Дневной лимит исчерпан (5/5).\n\n'
            'Продолжить можно с /premium:\n'
            '- 50 запросов за 100 ⭐\n'
            '- Безлимит за 300 ⭐/мес'
        )
        return

    await message.bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    subject = classify_text(message.text)
    try:
        result = await solve_text(message.text, subject, settings.openai_api_key, redis, settings.daily_cost_limit_usd)
    except LimitExceeded:
        await message.answer('сервис временно недоступен, попробуй позже')
        return
    except Exception:
        logger.exception('Solver failed')
        await message.answer('Сервис временно недоступен, попробуй позже')
        return

    await message.answer(result.response)
    await db.log_request(
        message.from_user.id,
        result.subject,
        result.input_type,
        message.text,
        result.response,
        result.tokens_used,
        result.cost_usd,
    )


async def handle_photo(message: Message) -> None:
    assert db is not None and redis is not None
    user = await db.ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    allowed, reason = await apply_limit(user, redis, db)
    if not allowed:
        await message.answer(
            'Дневной лимит исчерпан (5/5).\n\n'
            'Продолжить можно с /premium:\n'
            '- 50 запросов за 100 ⭐\n'
            '- Безлимит за 300 ⭐/мес'
        )
        return

    await message.bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    file_id = message.photo[-1].file_id
    file = await message.bot.get_file(file_id)
    image_bytes = await message.bot.download_file(file.file_path)

    try:
        result = await solve_photo(image_bytes, settings.openai_api_key, redis, settings.daily_cost_limit_usd)
    except LimitExceeded:
        await message.answer('сервис временно недоступен, попробуй позже')
        return
    except Exception:
        logger.exception('Solver failed')
        await message.answer('Сервис временно недоступен, попробуй позже')
        return

    await message.answer(result.response)
    await db.log_request(
        message.from_user.id,
        result.subject,
        result.input_type,
        'photo',
        result.response,
        result.tokens_used,
        result.cost_usd,
    )
