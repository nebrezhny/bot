from aiogram import Router, F
from aiogram.types import Message
from bot.services import solver
from bot.services.db import get_user
from asyncpg import Pool

router = Router()


@router.message(F.text & ~F.text.startswith('/'))
async def text_task_handler(message: Message, pool: Pool):
    user = await get_user(pool, message.from_user.id)
    if not user or not user.country:
        await message.answer("Пожалуйста, сначала выберите страну с помощью /start")
        return

    thinking_message = await message.answer("Думаю...")
    answer, subject, tokens, cost = await solver.solve_task(message.text, user.country)
    await thinking_message.edit_text(answer, disable_web_page_preview=True)


@router.message(F.photo)
async def photo_task_handler(message: Message, pool: Pool):
    user = await get_user(pool, message.from_user.id)
    if not user or not user.country:
        await message.answer("Пожалуйста, сначала выберите страну с помощью /start")
        return

    thinking_message = await message.answer("Анализирую фото...")
    file_path = f"/tmp/{message.photo[-1].file_id}.jpg"
    await message.bot.download(file=message.photo[-1].file_id, destination=file_path)

    question = message.caption if message.caption else "Реши задачу на фото"

    answer, subject, tokens, cost = await solver.solve_task(
        question, user.country, file_path
    )
    await thinking_message.edit_text(answer, disable_web_page_preview=True)
