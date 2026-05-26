from __future__ import annotations

from datetime import datetime, timezone
import logging

import psycopg
from psycopg.rows import class_row

from bot.models.schemas import User

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.conn: psycopg.AsyncConnection | None = None

    async def connect(self) -> None:
        self.conn = await psycopg.AsyncConnection.connect(self.dsn, autocommit=True)
        await self._ensure_tables()

    async def close(self) -> None:
        if self.conn is not None:
            await self.conn.close()

    async def _ensure_tables(self) -> None:
        assert self.conn is not None
        async with self.conn.cursor() as cur:
            await cur.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto;')
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    free_requests_today INT DEFAULT 0,
                    last_reset_date DATE DEFAULT CURRENT_DATE,
                    plan TEXT DEFAULT 'free',
                    plan_requests_left INT DEFAULT 0,
                    plan_expires_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS requests (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id BIGINT REFERENCES users(user_id),
                    subject TEXT,
                    input_type TEXT,
                    question TEXT,
                    answer TEXT,
                    tokens_used INT,
                    cost_usd FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS payments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id BIGINT REFERENCES users(user_id),
                    stars_amount INT,
                    plan TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                """
            )

    async def get_user(self, user_id: int) -> User | None:
        assert self.conn is not None
        async with self.conn.cursor(row_factory=class_row(User)) as cur:
            await cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            return await cur.fetchone()

    async def ensure_user(self, user_id: int, username: str | None, first_name: str | None) -> User:
        user = await self.get_user(user_id)
        if user is not None:
            return user
        assert self.conn is not None
        async with self.conn.cursor() as cur:
            await cur.execute(
                'INSERT INTO users(user_id, username, first_name) VALUES(%s, %s, %s) ON CONFLICT DO NOTHING',
                (user_id, username, first_name),
            )
        user = await self.get_user(user_id)
        if user is None:
            raise RuntimeError('failed to create user')
        return user

    async def update_user_plan(
        self,
        user_id: int,
        plan: str,
        plan_requests_left: int = 0,
        plan_expires_at: datetime | None = None,
    ) -> None:
        assert self.conn is not None
        async with self.conn.cursor() as cur:
            await cur.execute(
                'UPDATE users SET plan = %s, plan_requests_left = %s, plan_expires_at = %s WHERE user_id = %s',
                (plan, plan_requests_left, plan_expires_at, user_id),
            )

    async def decrement_pack_requests(self, user_id: int) -> None:
        assert self.conn is not None
        async with self.conn.cursor() as cur:
            await cur.execute(
                'UPDATE users SET plan_requests_left = GREATEST(plan_requests_left - 1, 0) WHERE user_id = %s',
                (user_id,),
            )

    async def increment_free_requests(self, user_id: int) -> None:
        assert self.conn is not None
        async with self.conn.cursor() as cur:
            await cur.execute(
                'UPDATE users SET free_requests_today = free_requests_today + 1, last_reset_date = CURRENT_DATE WHERE user_id = %s',
                (user_id,),
            )

    async def log_request(
        self,
        user_id: int,
        subject: str,
        input_type: str,
        question: str,
        answer: str,
        tokens_used: int,
        cost_usd: float,
    ) -> None:
        assert self.conn is not None
        async with self.conn.cursor() as cur:
            await cur.execute(
                'INSERT INTO requests(user_id, subject, input_type, question, answer, tokens_used, cost_usd) VALUES(%s, %s, %s, %s, %s, %s, %s)',
                (user_id, subject, input_type, question, answer, tokens_used, cost_usd),
            )

    async def log_payment(self, user_id: int, stars_amount: int, plan: str) -> None:
        assert self.conn is not None
        async with self.conn.cursor() as cur:
            await cur.execute(
                'INSERT INTO payments(user_id, stars_amount, plan) VALUES(%s, %s, %s)',
                (user_id, stars_amount, plan),
            )
