
import asyncio
import asyncpg
import redis.asyncio as redis
from aiogram import Bot, Dispatcher

from bot.core.config import settings
from bot.core.logging import setup_logging
from bot.handlers import start, tasks, payments
from bot.middlewares.db import DbMiddleware
from bot.middlewares.throttle import ThrottlingMiddleware

async def main():
    setup_logging()

    pool = await asyncpg.create_pool(settings.DATABASE_URL)
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Middlewares
    dp.update.middleware(DbMiddleware(pool=pool, redis_client=redis_client))
    dp.message.middleware(ThrottlingMiddleware())

    # Routers
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(payments.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
