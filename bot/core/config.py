from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    openai_api_key: str
    database_url: str
    redis_url: str
    daily_cost_limit_usd: float = 3.0
    payment_provider_token: str | None = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
