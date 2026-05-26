
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def main():
    if not DATABASE_URL:
        print("ОШИБКА: Переменная окружения DATABASE_URL не найдена.")
        return
        
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        print("Подключено к БД. Проверяю и исправляю схему...")
        # Эта команда безопасно добавит колонку, только если её нет.
        await conn.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS last_reset_date DATE DEFAULT CURRENT_DATE;')
        # Эта команда заполнит значение для старых строк, где оно может быть NULL
        await conn.execute('UPDATE users SET last_reset_date = CURRENT_DATE WHERE last_reset_date IS NULL;')
        print("Схема БД успешно исправлена.")
    except Exception as e:
        print(f"Произошла ошибка при исправлении схемы: {e}")
    finally:
        await conn.close()
        print("Соединение с БД закрыто.")

if __name__ == "__main__":
    asyncio.run(main())
