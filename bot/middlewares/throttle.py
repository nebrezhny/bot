
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
import datetime

class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
        db = data.get("db")
        if not db:
            return await handler(event, data)

        user = await db.ensure_user(event.from_user.id, event.from_user.username, event.from_user.first_name)

        # --- ИСПРАВЛЕНИЕ --- 
        # Убеждаемся, что user.last_reset_date - это объект date, а не None
        last_reset = user.last_reset_date if user.last_reset_date else datetime.date.today()

        if last_reset < datetime.date.today():
        # ---------------------
            async with db.pool.acquire() as conn:
                await conn.execute("UPDATE users SET free_requests_today = 0, last_reset_date = CURRENT_DATE WHERE user_id = $1", user.user_id)
            # Обновляем объект user, чтобы не делать еще один запрос к БД
            user = await db.get_user(user.user_id) 

        if user.plan == 'free' and user.free_requests_today >= 5:
            await event.answer("Вы исчерпали свой дневной лимит бесплатных запросов. Оформите подписку /premium, чтобы получить больше.")
            return
        
        if user.plan != 'free' and user.plan_requests_left is not None and user.plan_requests_left <= 0:
             await event.answer("Вы исчерпали свой лимит запросов по подписке. Оформите новую /premium, чтобы получить больше.")
             return

        async with db.pool.acquire() as conn:
            if user.plan == 'free':
                await conn.execute("UPDATE users SET free_requests_today = free_requests_today + 1 WHERE user_id = $1", user.user_id)
            else:
                # Уменьшаем счетчик только если он не None
                if user.plan_requests_left is not None:
                    await conn.execute("UPDATE users SET plan_requests_left = plan_requests_left - 1 WHERE user_id = $1", user.user_id)

        return await handler(event, data)
