from aiogram import Router, F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from bot.core.config import settings

router = Router()

# In a real bot, you'd get these from a database or config
PRICES = {
    'plus': {
        'title': "Подписка 'Плюс'",
        'description': "100 запросов в месяц",
        'prices': [LabeledPrice(label='Подписка "Плюс" на 1 месяц', amount=29900)], # 299 RUB
    },
    'pro': {
        'title': "Подписка 'Про'",
        'description': "500 запросов в месяц",
        'prices': [LabeledPrice(label='Подписка "Про" на 1 месяц', amount=99900)], # 999 RUB
    }
}

@router.message(F.text == "/premium")
async def premium_handler(message: Message):
    await message.answer("Выберите тариф:")
    # In a real bot you would have inline keyboards to select a plan
    # For simplicity, we just show one
    await message.bot.send_invoice(
        chat_id=message.chat.id,
        **PRICES['plus'],
        provider_token=settings.provider_token, # You need a payment provider token
        payload='plus_1m',
        currency='RUB'
    )

@router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, pool):
    # Here you should update the user's plan in the database
    # based on message.successful_payment.invoice_payload
    await message.answer("Спасибо за оплату! Ваша подписка активна.")

