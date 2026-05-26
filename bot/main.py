from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from redis.asyncio import Redis

from bot.core.config import settings
from bot.core.logging import setup_logging
import bot.core.state as state
from bot.services.db import Database
from bot.handlers.start import router as start_router
from bot.handlers.payment import router as payment_router
from bot.handlers.solve import router as solve_router


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    db_state = Database(settings.database_url)
    await db_state.connect()
    redis_state = Redis.from_url(settings.redis_url, decode_responses=True)
    state.db = db_state
    state.redis = redis_state
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(payment_router)
    dp.include_router(solve_router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await db_state.close()
        await redis_state.close()


if __name__ == '__main__':
    asyncio.run(main())
