from __future__ import annotations

import base64
import logging
from datetime import datetime, timedelta, timezone

from openai import AsyncOpenAI

from bot.models.schemas import SolveResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a knowledgeable tutor helping a student understand how to solve a problem.
Your goal is to explain the solution clearly, not just give the answer.

Always respond in Russian.

Response format (always follow this structure):
**Что дано:**
[briefly restate what is given]

**Метод:**
[which method/formula/approach and WHY this one]

**Решение:**
[step-by-step, each step numbered, each step explained in plain language]

**Ответ:**
[final answer, clearly highlighted]

**Проверка:**
[how to verify the answer is correct — skip if not applicable]

Rules:
- Write like a good teacher explains at the board
- Use examples if the concept is complex
- If the problem is unclear or incomplete, ask one clarifying question
- Never add unnecessary filler text
- Keep math formulas readable (use Unicode symbols: ², √, π, ≤, ≥, ±)
- For programming tasks: always include working code with comments
- If you genuinely cannot solve the task, say so honestly

Subject context: {subject}
Student level: {level}
"""

MODEL_PRICES = {
    'gpt-4o': 0.003,
    'gpt-4o-mini': 0.0005,
}
DEFAULT_LEVEL = 'school'


class LimitExceeded(Exception):
    pass


def get_model(input_type: str, subject: str) -> str:
    if input_type == 'photo':
        return 'gpt-4o'
    if subject == 'programming':
        return 'gpt-4o'
    return 'gpt-4o-mini'


def build_prompt(question: str, input_type: str, subject: str) -> str:
    if input_type == 'photo':
        return f"Реши задачу по фото. Изображение закодировано в base64. Вопрос: {question}"
    return f"Реши задачу. Вопрос: {question}"


async def ensure_spend_limit(redis, cost: float, daily_limit: float) -> None:
    if cost <= 0:
        return
    key = 'daily_spend_usd'
    current = await redis.get(key)
    total = float(current or 0.0)
    if total + cost > daily_limit:
        raise LimitExceeded('daily spend limit reached')
    new_total = await redis.incrbyfloat(key, cost)
    if current is None:
        ttl = int((datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1) - datetime.now(timezone.utc)).total_seconds())
        await redis.expire(key, ttl)
    if new_total > daily_limit:
        raise LimitExceeded('daily spend limit reached')


async def solve_text(
    question: str,
    subject: str,
    api_key: str,
    redis,
    daily_limit: float,
) -> SolveResult:
    model = get_model('text', subject)
    prompt = build_prompt(question, 'text', subject)
    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT.format(subject=subject, level=DEFAULT_LEVEL)},
            {'role': 'user', 'content': prompt},
        ],
        temperature=0.2,
    )
    text = response.choices[0].message.content
    usage = getattr(response, 'usage', None)
    tokens = int(getattr(usage, 'total_tokens', 0) or 0)
    cost = tokens / 1000 * MODEL_PRICES.get(model, 0.0)
    await ensure_spend_limit(redis, cost, daily_limit)
    return SolveResult(
        response=text,
        subject=subject,
        input_type='text',
        tokens_used=tokens,
        cost_usd=round(cost, 6),
    )


async def solve_photo(
    image_data: bytes,
    api_key: str,
    redis,
    daily_limit: float,
) -> SolveResult:
    model = get_model('photo', 'other')
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                'role': 'system',
                'content': SYSTEM_PROMPT.format(subject='other', level=DEFAULT_LEVEL)
            },
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_base64',
                        'media_type': 'image/jpeg',
                        'image_base64': image_base64,
                    },
                    {
                        'type': 'text',
                        'text': 'Реши задачу по этому фото.',
                    }
                ],
            }
        ],
        temperature=0.2,
    )
    text = response.choices[0].message.content
    usage = getattr(response, 'usage', None)
    tokens = int(getattr(usage, 'total_tokens', 0) or 0)
    cost = tokens / 1000 * MODEL_PRICES.get(model, 0.0)
    await ensure_spend_limit(redis, cost, daily_limit)
    return SolveResult(
        response=text,
        subject='other',
        input_type='photo',
        tokens_used=tokens,
        cost_usd=round(cost, 6),
    )
