"""
Menu router for Karma System bot.
Handles main menu interactions (reply keyboard).
"""
from aiogram import Router, F
from aiogram.types import Message

from app.bot.keyboards.inline import get_categories, get_profile_guest, get_profile_partner
from app.bot.keyboards.reply import get_location_request

router = Router()

@router.message(F.text == "🗂 Категории")
async def menu_categories(message: Message, locale: str, _):
    """Handle categories menu button."""
    text = _("menu_categories")
    keyboard = get_categories()
    await message.answer(text, reply_markup=keyboard)

@router.message(F.text == "👤 Личный кабинет")
async def menu_profile(message: Message, locale: str, _):
    """Handle profile menu button."""
    user_id = message.from_user.id
    
    # TODO: Get user role from database
    # user = await user_service.get_user(user_id)
    # is_partner = user and user.role == 'partner'
    is_partner = False  # Stub for now
    
    if is_partner:
        text = _("menu_profile_partner")
        keyboard = get_profile_partner()
    else:
        text = _("menu_profile_guest")
        keyboard = get_profile_guest()
    
    await message.answer(text, reply_markup=keyboard)

@router.message(F.text == "📍 Районы/Рядом")
async def menu_nearby(message: Message, locale: str, _):
    """Handle nearby menu button."""
    text = _("menu_nearby")
    keyboard = get_location_request()
    await message.answer(text, reply_markup=keyboard)

@router.message(F.text == "❓ Помощь")
async def menu_help(message: Message, locale: str, _):
    """Handle help menu button."""
    import os
    
    # Get PDF URL based on user language
    pdf_key = f"PDF_USER_{locale.upper()}"
    pdf_url = os.getenv(pdf_key, os.getenv("PDF_USER_RU", "#"))
    support = os.getenv("SUPPORT_TG", "https://t.me/karma_system_official")
    
    text = _("menu_help", pdf_url=pdf_url, support=support)
    await message.answer(text)
