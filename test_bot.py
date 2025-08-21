"""
Простой тест для проверки работы бота локально.
"""
import asyncio
import os
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv('.env.example')

async def test_bot():
    """Тест подключения к Telegram API."""
    from aiogram import Bot
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("ERROR BOT_TOKEN не найден в .env.example")
        return
    
    bot = Bot(token=bot_token)
    
    try:
        # Получить информацию о боте
        me = await bot.get_me()
        print(f"OK Бот подключен: @{me.username}")
        print(f"   ID: {me.id}")
        print(f"   Имя: {me.first_name}")
        
        # Проверить webhook
        webhook_info = await bot.get_webhook_info()
        print(f"   Webhook URL: {webhook_info.url or 'Не установлен'}")
        
    except Exception as e:
        print(f"ERROR Ошибка подключения: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_bot())
