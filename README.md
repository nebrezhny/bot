# Study Helper Telegram Bot

Telegram бот, который помогает студентам решать домашние задания и экзаменационные вопросы. Отправь задачу текстом или фото — получи подробное решение с объяснением.

## Возможности

- 📝 **Текстовые задачи** — отправь описание задачи текстом
- 📸 **Фото задач** — загрузи снимок из учебника или конспекта
- 🎓 **Поддерживаемые предметы**: математика, физика, химия, программирование, русский, английский, история, биология
- 💡 **Пошаговое объяснение** — не просто ответ, а понимание метода
- ⚡ **Быстрое решение** — ответ за несколько секунд
- 💰 **Гибкое ценообразование**:
  - 5 бесплатных запросов в день
  - 50 запросов за 100 ⭐
  - Безлимит на месяц за 300 ⭐
  - Безлимит на 3 месяца за 500 ⭐

## Техстек

- **Python 3.11**
- **aiogram 3.x** — Telegram API
- **OpenAI API** (gpt-4o для фото, gpt-4o-mini для текста)
- **PostgreSQL** — хранение пользователей и истории запросов
- **Redis** — rate limiting и кеширование
- **Pydantic Settings** — управление конфигурацией

## Установка и запуск локально

### 1. Клонируй репо и перейди в папку

```bash
cd study-bot
```

### 2. Установи зависимости

```bash
pip install -r requirements.txt
```

### 3. Настрой переменные окружения

Скопируй `.env.example` в `.env` и заполни:

```bash
cp .env.example .env
```

Отредактируй `.env`:

```
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
OPENAI_API_KEY=sk-proj-xxxxx...
DATABASE_URL=postgresql://user:pass@localhost:5432/studybot
REDIS_URL=redis://localhost:6379
DAILY_COST_LIMIT_USD=3.0
PAYMENT_PROVIDER_TOKEN=390583:TEST:your_token_here
```

### 4. Запусти Docker для БД и Redis

```bash
docker compose up -d
```

Это поднимет PostgreSQL и Redis локально.

### 5. Запусти бота

```bash
python bot/main.py
```

Бот начнет слушать входящие сообщения.

## Получение токенов

### BotFather (токен бота)

1. Напиши [@BotFather](https://nebrezhny.github.io) в Telegram
2. Используй `/newbot`
3. Следуй инструкциям
4. Скопируй токен в `BOT_TOKEN`

### OpenAI API Key

1. Зарегистрируйся на [openai.com](https://nebrezhny.github.io)
2. Создай новый API key
3. Добавь в `OPENAI_API_KEY`
4. Убедись, что у аккаунта есть кредиты

### Telegram Stars (оплата)

1. Напиши [@BotFather](https://nebrezhny.github.io)
2. Используй `/mybots` → выбери бота → Bot Settings → Payments
3. Скопируй провайдер токен в `PAYMENT_PROVIDER_TOKEN`

## Структура проекта

```
study-bot/
├── bot/
│   ├── main.py                 # точка входа
│   ├── core/
│   │   ├── config.py          # конфигурация через pydantic-settings
│   │   ├── logging.py         # логирование
│   │   └── state.py           # глобальное состояние (DB, Redis)
│   ├── handlers/
│   │   ├── start.py           # /start, /help, /status
│   │   ├── payment.py         # /premium, Telegram Stars
│   │   └── solve.py           # обработка текста и фото
│   ├── services/
│   │   ├── db.py              # PostgreSQL CRUD
│   │   ├── limiter.py         # rate limiting (Redis)
│   │   ├── classifier.py      # определение предмета
│   │   └── solver.py          # взаимодействие с OpenAI
│   └── models/
│       └── schemas.py         # Pydantic модели
├── tests/
│   ├── test_classifier.py     # тесты классификатора
│   ├── test_limiter.py        # тесты лимитов
│   └── test_solver.py         # тесты решателя
├── requirements.txt           # зависимости
├── Dockerfile                 # для Railway
├── docker-compose.yml         # локальная БД + Redis
└── README.md
```

## Команды бота

| Команда | Описание |
|---------|---------|
| `/start` | Приветствие и инструкция |
| `/help` | Примеры использования |
| `/status` | Посмотреть остаток запросов и план |
| `/premium` | Выбрать и купить план |

## Как это работает

### Отправка текстовой задачи

1. Пользователь отправляет текст задачи
2. Бот проверяет лимит запросов
3. Классификатор определяет предмет
4. Solver вызывает OpenAI с промптом на русском
5. Бот отправляет решение пошагово
6. Запрос логируется в БД

### Отправка фото задачи

1. Пользователь отправляет фото
2. Бот скачивает файл с Telegram серверов
3. Проверяет лимит
4. Конвертирует фото в base64
5. Отправляет в OpenAI с vision моделью (gpt-4o)
6. Бот отправляет готовое решение
7. Логирует в БД

### Rate Limiting

**Бесплатный план:**
- 5 запросов в день
- Счетчик сбрасывается в полночь (МСК)
- Хранится в Redis

**Pack 50:**
- 50 запросов всего (не в день)
- Счетчик в БД
- Не истекает

**Unlimited:**
- Без ограничений
- Срок действия в `plan_expires_at`
- Проверяется перед каждым запросом

## Тестирование

```bash
# Запусти все тесты
python -m pytest -v

# Конкретный тест
python -m pytest tests/test_classifier.py -v

# С покрытием (если установлен pytest-cov)
python -m pytest --cov=bot
```

## Запуск на Railway

1. Создай приложение на [railway.app](https://nebrezhny.github.io)
2. Подключи репо
3. Добавь переменные окружения в Railway dashboard
4. Railway автоматически использует Dockerfile
5. Бот запустится

## Логирование

Логи выводятся в stdout с уровнем `INFO`:

```
2026-05-26 12:30:45,123 INFO aiogram.dispatcher: Starting polling
2026-05-26 12:31:15,456 INFO bot.services.solver: solving task: math, tokens: 245, cost: 0.000123
```

## Стоимость

Примерные затраты (за месяц, ~1000 запросов):

| Модель | Цена (1K токенов) | Ожидаемо за запрос |
|--------|-------------------|-------------------|
| gpt-4o-mini (текст) | $0.15 | $0.005-0.010 |
| gpt-4o-mini (фото) | $0.15 | $0.010-0.015 |
| gpt-4o (фото) | $0.30 | $0.020-0.050 |

Дневной лимит ($3) защищает от неконтролируемых затрат.

## Переменные окружения

```
BOT_TOKEN=                  # Telegram Bot Token
OPENAI_API_KEY=            # OpenAI API Key
DATABASE_URL=              # PostgreSQL строка подключения
REDIS_URL=                 # Redis URL (redis://localhost:6379)
DAILY_COST_LIMIT_USD=3.0   # Дневной лимит расходов в USD
PAYMENT_PROVIDER_TOKEN=    # Telegram Stars провайдер (опционально)
```

## Решение проблем

**Ошибка: "No module named 'bot'"**
- Убедись, что ты в папке `study-bot`
- Используй `python bot/main.py`, не `python main.py`

**Ошибка: "could not connect to server"**
- Проверь, что PostgreSQL и Redis запущены
- Проверь `DATABASE_URL` и `REDIS_URL` в `.env`

**Ошибка: "Unauthorized" от OpenAI**
- Проверь `OPENAI_API_KEY`
- Убедись, что у аккаунта есть кредиты
- Проверь лимиты в OpenAI dashboard

**Бот не отвечает**
- Проверь, что `BOT_TOKEN` правильный
- Посмотри логи в консоли
- Убедись, что интернет соединение работает

## Лицензия

MIT

## Контакт

Если есть вопросы или предложения — открывай Issue или PR.
