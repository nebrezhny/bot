import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from bot.services.solver import solve_text


class DummyResponse:
    def __init__(self):
        self.choices = [SimpleNamespace(message=SimpleNamespace(content='**Что дано:** Тест\n\n**Метод:** Решение\n\n**Решение:** 1. Шаг\n\n**Ответ:** 42'))]
        self.usage = SimpleNamespace(total_tokens=100)


class FakeAsyncChat:
    async def create(self, **kwargs):
        return DummyResponse()


class FakeAsyncOpenAI:
    def __init__(self, *args, **kwargs):
        self.chat = SimpleNamespace(completions=FakeAsyncChat())


@pytest.mark.asyncio
async def test_solver_response_contains_required_sections(monkeypatch):
    monkeypatch.setattr('bot.services.solver.AsyncOpenAI', FakeAsyncOpenAI)
    redis = SimpleNamespace(get=AsyncMock(return_value=None), incrbyfloat=AsyncMock(return_value=0.3), expire=AsyncMock())
    result = await solve_text('найдите производную x^2', 'math', 'fake-key', redis, 3.0)
    assert '**Что дано:**' in result.response
    assert '**Метод:**' in result.response
    assert '**Решение:**' in result.response
    assert '**Ответ:**' in result.response
    assert 'Что дано' in result.response
