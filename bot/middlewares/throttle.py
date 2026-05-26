from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from bot.services import db as user_db
import datetime

class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
        user = await user_db.get_user(data["pool"], event.from_user.id)

        if not user:
            await user_db.create_user(data["pool"], event.from_user.id, event.from_user.username, event.from_user.first_name)
            await event.answer("Добро пожаловать! Выберите вашу страну, чтобы я мог адаптировать ответы.")
            # Here you should initiate a state for country selection
            return

        if user.last_reset_date < datetime.date.today():
            async with data["pool"].acquire() as conn:
                await conn.execute("UPDATE users SET free_requests_today = 0, last_reset_date = CURRENT_DATE WHERE user_id = $1", user.user_id)
            user.free_requests_today = 0

        if user.plan == 'free' and user.free_requests_today >= 3:
            await event.answer("Вы исчерпали свой дневной лимит бесплатных запросов. Оформите подписку /premium, чтобы получить больше.")
            return
        
        if user.plan != 'free' and user.plan_requests_left <= 0:
             await event.answer("Вы исчерпали свой лимит запросов по подписке. Оформите новую /premium, чтобы получить больше.")
             return

        async with data["pool"].acquire() as conn:
            if user.plan == 'free':
                await conn.execute("UPDATE users SET free_requests_today = free_requests_today + 1 WHERE user_id = $1", user.user_id)
            else:
                await conn.execute("UPDATE users SET plan_requests_left = plan_requests_left - 1 WHERE user_id = $1", user.user_id)


        return await handler(event, data)
