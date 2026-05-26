
import asyncpg
import redis.asyncio as redis
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

from bot.repositories.user_repository import UserRepository # Импортируем наш репозиторий

class DbMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.Pool, redis_client: redis.Redis):
        super().__init__()
        self.pool = pool
        self.redis_client = redis_client
        # Создаем экземпляр репозитория один раз при инициализации
        self.user_repo = UserRepository(pool)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Передаем в обработчики сам репозиторий и redis
        # Вместо db.ensure_user() будет db.user.ensure_user()
        # или лучше сразу data["user_repo"] = self.user_repo
        data["db"] = self.user_repo # Для совместимости со старым кодом
        data["redis"] = self.redis_client
        return await handler(event, data)
