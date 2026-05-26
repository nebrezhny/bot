from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from bot.models.schemas import User
from bot.services.db import Database

MOSCOW = ZoneInfo('Europe/Moscow')
FREE_LIMIT = 5
FREE_KEY = 'free_count:'


def seconds_until_moscow_midnight() -> int:
    now = datetime.now(timezone.utc).astimezone(MOSCOW)
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((tomorrow - now).total_seconds())


async def apply_limit(user: User, redis, db: Database) -> tuple[bool, str | None]:
    if user.plan == 'unlimited':
        if user.plan_expires_at and user.plan_expires_at > datetime.now(timezone.utc):
            return True, None
        return False, 'plan_expired'

    if user.plan == 'pack_50':
        if user.plan_requests_left > 0:
            await db.decrement_pack_requests(user.user_id)
            return True, None
        return False, 'pack_empty'

    if user.plan == 'free':
        key = f'{FREE_KEY}{user.user_id}'
        current = await redis.get(key)
        count = int(current or 0)
        if count < FREE_LIMIT:
            ttl = seconds_until_moscow_midnight()
            if current is None:
                await redis.set(key, 1, ex=ttl)
            else:
                await redis.incr(key)
                await redis.expire(key, ttl)
            return True, None
        return False, 'daily_limit'

    return False, 'daily_limit'


async def get_free_count(redis, user_id: int) -> int:
    current = await redis.get(f'{FREE_KEY}{user_id}')
    return int(current or 0)
