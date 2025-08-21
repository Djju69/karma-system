"""
Reply keyboards for Karma System bot.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """Get main menu reply keyboard (fixed layout)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🗂 Категории"),
                KeyboardButton(text="👤 Личный кабинет")
            ],
            [
                KeyboardButton(text="📍 Районы/Рядом"),
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )

def get_location_request() -> ReplyKeyboardMarkup:
    """Get location request keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Отправить геолокацию", request_location=True)],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
