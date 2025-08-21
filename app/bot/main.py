"""
Telegram Bot main entry point for Karma System.
"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.middlewares import I18nMiddleware
from app.bot.routers import start, menu, catalog, profile, partner, qr, help_router, geo

# Load environment variables
load_dotenv('.env.example')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main bot function."""
    # Get bot token
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables")
        return

    # Initialize storage
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        try:
            storage = RedisStorage.from_url(redis_url)
            logger.info("Using Redis storage for FSM")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis, using memory storage: {e}")
            storage = MemoryStorage()
    else:
        storage = MemoryStorage()
        logger.info("Using memory storage for FSM")

    # Initialize bot and dispatcher
    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=storage)

    # Setup middlewares
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    # Include routers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(catalog.router)
    dp.include_router(profile.router)
    dp.include_router(partner.router)
    dp.include_router(qr.router)
    dp.include_router(help_router.router)
    dp.include_router(geo.router)

    # Start polling
    logger.info("Starting Karma System bot...")
    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()
        if hasattr(storage, 'close'):
            await storage.close()

if __name__ == "__main__":
    asyncio.run(main())
