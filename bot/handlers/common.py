from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from bot.services import db as user_db

router = Router()


@router.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext, pool):
    await state.clear()
    user = await user_db.get_user(pool, message.from_user.id)
    if user and user.country:
        await message.answer(
            f"Привет, {message.from_user.first_name}! Чем могу помочь?",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif not user:
         user_db.create_user(pool, message.from_user.id, message.from_user.username, message.from_user.first_name)
         await message.answer("Добро пожаловать! Выберите вашу страну, чтобы я мог адаптировать ответы.")
         # Here you should initiate a state for country selection
    else: # User exists but country is not set
        await message.answer("Пожалуйста, выберите вашу страну.")
        # Here you should initiate a state for country selection


@router.message(F.text == "/help")
async def help_handler(message: Message):
    await message.answer(
        "Просто отправь мне текст или фото своей задачи, и я помогу ее решить."
    )
