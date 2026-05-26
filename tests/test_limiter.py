from datetime import datetime, timezone, timedelta

import pytest
from unittest.mock import AsyncMock

from bot.models.schemas import User
from bot.services.db import Database
from bot.services.limiter import apply_limit


@pytest.mark.asyncio
async def test_free_user_allowed():
    user = User(
        user_id=1,
        username='test',
        first_name='Test',
        created_at=datetime.now(timezone.utc),
        free_requests_today=0,
        last_reset_date=datetime.now(timezone.utc),
        plan='free',
        plan_requests_left=0,
        plan_expires_at=None,
    )
    redis = AsyncMock()
    redis.get.return_value = None
    redis.set = AsyncMock()
    redis.incr = AsyncMock()
    redis.expire = AsyncMock()
    db = AsyncMock(spec=Database)

    allowed, reason = await apply_limit(user, redis, db)
    assert allowed
    assert reason is None
    redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_free_user_denied():
    user = User(
        user_id=2,
        username='test',
        first_name='Test',
        created_at=datetime.now(timezone.utc),
        free_requests_today=5,
        last_reset_date=datetime.now(timezone.utc),
        plan='free',
        plan_requests_left=0,
        plan_expires_at=None,
    )
    redis = AsyncMock()
    redis.get.return_value = '5'
    db = AsyncMock(spec=Database)

    allowed, reason = await apply_limit(user, redis, db)
    assert not allowed
    assert reason == 'daily_limit'


@pytest.mark.asyncio
async def test_pack50_user_allowed():
    user = User(
        user_id=3,
        username='test',
        first_name='Test',
        created_at=datetime.now(timezone.utc),
        free_requests_today=0,
        last_reset_date=datetime.now(timezone.utc),
        plan='pack_50',
        plan_requests_left=10,
        plan_expires_at=None,
    )
    redis = AsyncMock()
    db = AsyncMock(spec=Database)

    allowed, reason = await apply_limit(user, redis, db)
    assert allowed
    assert reason is None
    db.decrement_pack_requests.assert_awaited_once_with(user.user_id)


@pytest.mark.asyncio
async def test_pack50_user_denied():
    user = User(
        user_id=4,
        username='test',
        first_name='Test',
        created_at=datetime.now(timezone.utc),
        free_requests_today=0,
        last_reset_date=datetime.now(timezone.utc),
        plan='pack_50',
        plan_requests_left=0,
        plan_expires_at=None,
    )
    redis = AsyncMock()
    db = AsyncMock(spec=Database)

    allowed, reason = await apply_limit(user, redis, db)
    assert not allowed
    assert reason == 'pack_empty'


@pytest.mark.asyncio
async def test_unlimited_user_allowed():
    future = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=1)
    user = User(
        user_id=5,
        username='test',
        first_name='Test',
        created_at=datetime.now(timezone.utc),
        free_requests_today=0,
        last_reset_date=datetime.now(timezone.utc),
        plan='unlimited',
        plan_requests_left=0,
        plan_expires_at=future,
    )
    redis = AsyncMock()
    db = AsyncMock(spec=Database)

    allowed, reason = await apply_limit(user, redis, db)
    assert allowed
    assert reason is None


@pytest.mark.asyncio
async def test_unlimited_user_denied_expired():
    past = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=1)
    user = User(
        user_id=6,
        username='test',
        first_name='Test',
        created_at=datetime.now(timezone.utc),
        free_requests_today=0,
        last_reset_date=datetime.now(timezone.utc),
        plan='unlimited',
        plan_requests_left=0,
        plan_expires_at=past,
    )
    redis = AsyncMock()
    db = AsyncMock(spec=Database)

    allowed, reason = await apply_limit(user, redis, db)
    assert not allowed
    assert reason == 'plan_expired'
