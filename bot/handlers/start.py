from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.core.state import db

router = Router()

START_TEXT = (
    'Привет! Я помогу решить любое учебное задание.\n\n'
    'Просто отправь:\n'
    '- фото задачи из учебника\n'
    '- или напиши задачу текстом\n\n'
    'Поддерживаю: математику, физику, химию, программирование, русский, английский и другие предметы.\n\n'
    'У тебя 5 бесплатных запросов в день.\n'
    '/status — посмотреть остаток\n'
    '/premium — расширить лимит'
)

HELP_TEXT = (
    'Отправь задачу текстом или фото, и я объясню решение шаг за шагом.\n'
    'Например:\n'
    '- "найдите производную x^2"\n'
    '- "напишите функцию на python, которая считает факториал"\n'
    '- фотографию задачи из учебника\n\n'
    '/status — посмотреть остаток\n'
    '/premium — расширить лимит'
)


def premium_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Премиум', callback_data='premium')],
    ])


@router.message(Command('start'))
async def cmd_start(message: Message) -> None:
    await message.answer(START_TEXT)


@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(Command('status'))
async def cmd_status(message: Message) -> None:
    if db is None:
        await message.answer('Сервис временно недоступен, попробуй позже.')
        return
    user = await db.ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    if user.plan == 'free':
        text = (
            '📊 Твой аккаунт:\n\n'
            'План: Бесплатный\n'
            f'Осталось сегодня: {max(0, 5 - user.free_requests_today)} из 5\n\n'
            '/premium — получить больше запросов'
        )
    elif user.plan == 'pack_50':
        text = (
            '📊 Твой аккаунт:\n\n'
            'План: 50 запросов\n'
            f'Осталось: {user.plan_requests_left}\n\n'
            '/premium — получить больше запросов'
        )
    else:
        expires = user.plan_expires_at.strftime('%d %B %Y') if user.plan_expires_at else 'неизвестно'
        text = (
            '📊 Твой аккаунт:\n\n'
            'План: Безлимит\n'
            f'Действует до: {expires}\n\n'
            f'Запросов сегодня: {user.free_requests_today}\n\n'
            '/premium — получить больше запросов'
        )
    await message.answer(text)
