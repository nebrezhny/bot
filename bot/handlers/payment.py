from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging

from aiogram import Router
from aiogram.filters import Command, CallbackQuery, Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Message, PreCheckoutQuery

from bot.core.config import settings
from bot.core.state import db
from bot.services.db import Database

router = Router()
logger = logging.getLogger(__name__)

PLAN_OPTIONS = {
    'pack_50': {'title': '50 запросов — 100 ⭐', 'amount': 10000, 'stars': 100, 'plan': 'pack_50', 'expires': None},
    'unlimited_30': {'title': 'Безлимит на месяц — 300 ⭐', 'amount': 30000, 'stars': 300, 'plan': 'unlimited', 'expires_days': 30},
    'unlimited_90': {'title': 'Безлимит на 3 месяца — 500 ⭐', 'amount': 50000, 'stars': 500, 'plan': 'unlimited', 'expires_days': 90},
}


@router.message(Command('premium'))
async def cmd_premium(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=option['title'], callback_data=key)]
        for key, option in PLAN_OPTIONS.items()
    ])
    await message.answer(
        '💎 Расширить доступ\n\nВыбери подходящий вариант:\n\n'
        '[50 запросов — 100 ⭐]\n'
        '[Безлимит на месяц — 300 ⭐]\n'
        '[Безлимит на 3 месяца — 500 ⭐]\n\n'
        'Оплата через Telegram Stars — безопасно, без карты.',
        reply_markup=keyboard,
    )


@router.callback_query(Text(startswith='pack_50') | Text(startswith='unlimited_'))
async def create_invoice(query: CallbackQuery) -> None:
    plan_key = query.data
    option = PLAN_OPTIONS.get(plan_key)
    if option is None or settings.payment_provider_token is None:
        await query.answer('Ошибка оплаты, проверьте настройки.', show_alert=True)
        return

    invoice = LabeledPrice(label=option['title'], amount=option['amount'])
    await query.message.answer_invoice(
        title='Study Helper',
        description=option['title'],
        payload=plan_key,
        provider_token=settings.payment_provider_token,
        currency='XTR',
        prices=[invoice],
    )
    await query.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@router.message(lambda message: message.successful_payment is not None)
async def successful_payment(message: Message) -> None:
    payment = message.successful_payment
    payload = payment.invoice_payload
    option = PLAN_OPTIONS.get(payload)
    if option is None or db is None:
        await message.answer('Не удалось применить план, напишите позже.')
        return

    expires_at = None
    if option['plan'] == 'unlimited':
        days = option['expires_days']
        expires_at = datetime.now(timezone.utc) + timedelta(days=days)

    await db.update_user_plan(
        message.from_user.id,
        option['plan'],
        plan_requests_left=50 if option['plan'] == 'pack_50' else 0,
        plan_expires_at=expires_at,
    )
    await db.log_payment(message.from_user.id, option['stars'], option['plan'])

    if option['plan'] == 'pack_50':
        text = 'Ваш план обновлён: 50 запросов. Используйте их в любое время.'
    else:
        text = f'Ваш план обновлён: безлимит до {expires_at.strftime("%d %B %Y")}. '
        text += 'Можете отправлять задачи без ограничений.'

    await message.answer(text)
