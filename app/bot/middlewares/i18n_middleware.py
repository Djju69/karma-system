"""
I18n middleware for Karma System bot.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from app.bot.i18n import i18n

class I18nMiddleware(BaseMiddleware):
    """Middleware for internationalization."""
    
    def __init__(self):
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process event with i18n context."""
        user: User = data.get("event_from_user")
        
        if user:
            # Get user language from database or use default
            # For now, use language_code from Telegram user
            locale = getattr(user, 'language_code', 'ru')
            
            # Validate and normalize locale
            if locale and len(locale) >= 2:
                locale = locale[:2].lower()
                if not i18n.is_supported(locale):
                    locale = i18n.default_locale
            else:
                locale = i18n.default_locale
            
            # Add locale to handler data
            data["locale"] = locale
            data["i18n"] = i18n
            
            # Add translation function
            data["_"] = lambda key, **kwargs: i18n.get(key, locale, **kwargs)
        
        return await handler(event, data)
