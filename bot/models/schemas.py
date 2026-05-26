from pydantic import BaseModel
from typing import Optional
import datetime

class User(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: str
    country: Optional[str] = None
    created_at: datetime.datetime
    free_requests_today: int
    last_reset_date: datetime.date
    plan: str
    plan_requests_left: int
    plan_expires_at: Optional[datetime.datetime] = None

class Request(BaseModel):
    user_id: int
    subject: str
    input_type: str
    question: str
    answer: str
    tokens_used: int
    cost_usd: float

class Payment(BaseModel):
    user_id: int
    stars_amount: int
    plan: str
