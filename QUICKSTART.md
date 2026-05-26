# Быстрый старт

Минимальные шаги, чтобы запустить бота локально за 5 минут.

## 1️⃣ Требования

- Python 3.11+
- Docker & Docker Compose
- Telegram & BotFather токен
- OpenAI API ключ

## 2️⃣ Получить токены

### Telegram Bot Token

1. Открой [@BotFather](https://t.me/botfather)
2. Напиши `/newbot`
3. Следуй инструкциям
4. Скопируй токен (выглядит как `123456:ABC-DEF...`)

### OpenAI API Key

1. Зарегистрируйся на [platform.openai.com](https://platform.openai.com/account/api-keys)
2. Создай новый API key
3. Скопируй его (начинается с `sk-proj-...`)

## 3️⃣ Настроить проект

```bash
# Войди в папку
cd study-bot

# Скопируй .env шаблон
cp .env.example .env

# Отредактируй .env (вставь токены)
# Используй любой редактор: nano, vim, VS Code и т.д.
nano .env
```

Отредактированный `.env` должен выглядеть так:

```
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://user:pass@localhost:5432/studybot
REDIS_URL=redis://localhost:6379
DAILY_COST_LIMIT_USD=3.0
```

## 4️⃣ Установить зависимости

```bash
pip install -r requirements.txt
```

## 5️⃣ Запустить БД

```bash
# В отдельной консоли
docker compose up -d

# Проверить
docker compose ps
```

Должны быть запущены `postgres` и `redis`.

## 6️⃣ Запустить бота

```bash
python bot/main.py
```

Должно вывести:

```
2026-05-26 12:30:45 INFO aiogram.dispatcher: Starting polling...
```

## 7️⃣ Тестировать в Telegram

Найди своего бота по имени и отправь:

```
/start
```

Бот ответит приветствием. Пришли задачу:

```
Найдите производную x^2
```

Бот решит и ответит пошагово! 🚀

## ⚠️ Частые ошибки

### "Connection refused"
- Убедись что docker запущен: `docker compose ps`
- Перезапусти: `docker compose down && docker compose up -d`

### "Unauthorized" от OpenAI
- Проверь `OPENAI_API_KEY` в `.env`
- Убедись что кредиты в OpenAI аккаунте

### "could not translate host name"
- Проверь интернет
- Проверь что Redis/PostgreSQL доступны

## 🛑 Остановить

```bash
# Остановить бота
Ctrl+C

# Остановить БД
docker compose down
```

## 📖 Дальше

- Читай [README.md](README.md) для полной документации
- Смотри [структуру проекта](README.md#структура-проекта)
- Запусти тесты: `python -m pytest -v`
