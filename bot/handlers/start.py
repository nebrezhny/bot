
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# from bot.core.state import db # <--- УДАЛЯЕМ ЭТУ СТРОКУ

router = Router()

# Определяем состояния (FSM)
class UserState(StatesGroup):
    choosing_country = State()

# --- Клавиатуры ---
def country_selection_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🇷🇺 Россия", callback_data="country_russia")],
        [InlineKeyboardButton(text="🇰🇿 Казахстан", callback_data="country_kazakhstan")],
        [InlineKeyboardButton(text="🇺🇦 Украина", callback_data="country_ukraine")],
        [InlineKeyboardButton(text="🌐 Другая страна", callback_data="country_other")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Тексты сообщений ---
WELCOME_TEXT = "Добро пожаловать! Выберите вашу страну, чтобы я мог адаптировать ответы."
COUNTRY_SELECTED_TEXT = "Отлично! Ваша страна сохранена. Теперь вы можете задать мне любой учебный вопрос."
GREETING_TEXT = "Привет! Чем могу помочь сегодня? Просто отправьте мне задачу."

@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext, db) -> None: # db передается через middleware
    if db is None:
        await message.answer('Сервис временно недоступен, попробуйте позже.')
        return

    user = await db.ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    # Если страна еще не выбрана, запрашиваем ее
    if not user.country:
        await message.answer(WELCOME_TEXT, reply_markup=country_selection_keyboard())
        await state.set_state(UserState.choosing_country)
    else:
        await message.answer(GREETING_TEXT.format(first_name=message.from_user.first_name))

@router.callback_query(StateFilter(UserState.choosing_country))
async def select_country(callback: CallbackQuery, state: FSMContext, db) -> None: # db передается через middleware
    if not callback.data or not callback.data.startswith("country_"):
        await callback.answer("Что-то пошло не так. Попробуйте снова.", show_alert=True)
        return

    country_code = callback.data.split("_")[1]
    
    # Сохраняем страну в базу данных
    await db.update_user_country(callback.from_user.id, country_code)

    # Отвечаем пользователю и сбрасываем состояние
    await callback.message.edit_text(COUNTRY_SELECTED_TEXT)
    await state.clear()
    await callback.answer() # Закрываем "часики" на кнопке

# Команды /help и /status из старого файла, чтобы ничего не сломать
HELP_TEXT = (
    'Отправь задачу текстом или фото, и я объясню решение шаг за шагом.\n'
    'Например:\n'
    '- "найдите производную x^2"\n'
    '- "напишите функцию на python, которая считает факториал"\n'
    '- фотографию задачи из учебника\n\n'
    '/status — посмотреть остаток\n'
    '/premium — расширить лимит'
)

@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)

@router.message(Command('status'))
async def cmd_status(message: Message, db) -> None: # db передается через middleware
    if db is None:
        await message.answer('Сервис временно недоступен, попробуйте позже.')
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

