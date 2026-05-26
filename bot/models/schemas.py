from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    created_at: datetime
    free_requests_today: int
    last_reset_date: datetime
    plan: str
    plan_requests_left: int
    plan_expires_at: Optional[datetime]


class SolveResult(BaseModel):
    response: str
    subject: str
    input_type: str
    tokens_used: int
    cost_usd: float


class PaymentResult(BaseModel):
    user_id: int
    plan: str
    stars_amount: int
    expires_at: Optional[datetime]
