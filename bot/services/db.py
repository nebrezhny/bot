import asyncpg
from bot.models.schemas import User

async def get_user(pool: asyncpg.Pool, user_id: int) -> User | None:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        return User(**dict(row)) if row else None

async def create_user(pool: asyncpg.Pool, user_id: int, username: str, first_name: str) -> User:
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES ($1, $2, $3)",
            user_id, username, first_name
        )
        return await get_user(pool, user_id)

async def update_user_country(pool: asyncpg.Pool, user_id: int, country: str):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET country = $1 WHERE user_id = $2", country, user_id)
