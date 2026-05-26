import redis.asyncio as redis
from bot.core.config import settings

async def check_budget() -> bool:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    cost = await r.get("total_cost") or 0
    return float(cost) < settings.DAILY_COST_LIMIT_USD

async def reserve_cost(estimated_cost: float) -> bool:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    async with r.pipeline() as pipe:
        await pipe.incrbyfloat("total_cost", estimated_cost)
        total_cost = await pipe.execute()
        if total_cost[-1] > settings.DAILY_COST_LIMIT_USD:
            await r.incrbyfloat("total_cost", -estimated_cost) # Rollback
            return False
    return True

async def adjust_cost(actual_cost: float, estimated_cost: float):
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    await r.incrbyfloat("total_cost", actual_cost - estimated_cost)
