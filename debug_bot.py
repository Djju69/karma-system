"""
Диагностика проблем с ботом.
"""
import asyncio
import os
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv('.env.example')

async def debug_bot():
    """Полная диагностика бота."""
    print("=== ДИАГНОСТИКА БОТА ===")
    
    # 1. Проверка переменных окружения
    print("\n1. Переменные окружения:")
    bot_token = os.getenv('BOT_TOKEN')
    database_url = os.getenv('DATABASE_URL')
    redis_url = os.getenv('REDIS_URL')
    
    print(f"   BOT_TOKEN: {'OK' if bot_token else 'ОТСУТСТВУЕТ'}")
    print(f"   DATABASE_URL: {'OK' if database_url else 'ОТСУТСТВУЕТ'}")
    print(f"   REDIS_URL: {'OK' if redis_url else 'ОТСУТСТВУЕТ'}")
    
    if not bot_token:
        print("ERROR: BOT_TOKEN не найден!")
        return
    
    # 2. Проверка подключения к Telegram
    print("\n2. Подключение к Telegram:")
    try:
        from aiogram import Bot
        bot = Bot(token=bot_token)
        me = await bot.get_me()
        print(f"   OK: @{me.username} (ID: {me.id})")
        await bot.session.close()
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 3. Проверка импортов
    print("\n3. Проверка импортов:")
    try:
        from app.bot.main import main
        print("   OK: app.bot.main импортируется")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 4. Проверка базы данных (если доступна)
    print("\n4. База данных:")
    if database_url:
        try:
            from sqlalchemy.ext.asyncio import create_async_engine
            engine = create_async_engine(database_url)
            async with engine.begin() as conn:
                result = await conn.execute("SELECT 1")
                print("   OK: Подключение к БД работает")
            await engine.dispose()
        except Exception as e:
            print(f"   WARNING: {e}")
    else:
        print("   SKIP: DATABASE_URL не задан")
    
    # 5. Проверка Redis (если доступен)
    print("\n5. Redis:")
    if redis_url:
        try:
            import redis.asyncio as redis
            r = redis.from_url(redis_url)
            await r.ping()
            print("   OK: Подключение к Redis работает")
            await r.close()
        except Exception as e:
            print(f"   WARNING: {e}")
    else:
        print("   SKIP: REDIS_URL не задан")
    
    print("\n=== ДИАГНОСТИКА ЗАВЕРШЕНА ===")

if __name__ == "__main__":
    asyncio.run(debug_bot())
