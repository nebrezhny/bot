
import asyncpg
from typing import Optional

# Явно перечисляем все поля, которые мы ожидаем от таблицы users.
# Это защищает нас от проблем с SELECT *, когда схема меняется.
USER_COLUMNS = """
    user_id, 
    username, 
    first_name, 
    country, 
    plan, 
    free_requests_today, 
    plan_requests_left, 
    plan_expires_at, 
    last_reset_date
"""

class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_user(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(f"SELECT {USER_COLUMNS} FROM users WHERE user_id = $1", user_id)

    async def ensure_user(self, user_id: int, username: Optional[str], first_name: Optional[str]):
        async with self.pool.acquire() as conn:
            user = await self.get_user(user_id)
            if user is None:
                await conn.execute(
                    "INSERT INTO users (user_id, username, first_name) VALUES ($1, $2, $3)",
                    user_id, username, first_name
                )
                user = await self.get_user(user_id)
            return user

    async def update_user_country(self, user_id: int, country_code: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET country = $1 WHERE user_id = $2",
                country_code, user_id
            )
