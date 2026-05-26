import asyncpg
import redis.asyncio as redis
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from bot.core.config import settings

class DbMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.Pool, redis_client: redis.Redis):
        super().__init__()
        self.pool = pool
        self.redis_client = redis_client

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["pool"] = self.pool
        data["redis"] = self.redis_client
        return await handler(event, data)
