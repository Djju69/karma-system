"""
Geo router for Karma System bot.
Handles location-based features and coverage checking.
"""
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.location)
async def handle_location(message: Message, locale: str, _):
    """Handle location sharing."""
    location = message.location
    lat, lng = location.latitude, location.longitude
    
    # TODO: Check if location is within city coverage
    # city = await geo_service.check_coverage(lat, lng)
    
    # Stub implementation
    city = None  # Assume outside coverage for now
    
    if city:
        # Location is within coverage - show nearby places
        # TODO: Get nearby listings
        text = f"📍 Ваше местоположение: {lat:.4f}, {lng:.4f}\n"
        text += f"🌆 Город: {city['name']}\n\n"
        text += "🔍 Ищем ближайшие места..."
        await message.answer(text)
    else:
        # Outside coverage
        text = _("out_of_coverage")
        await message.answer(text)

@router.message(F.text == "🔙 Назад")
async def back_button(message: Message, locale: str, _):
    """Handle back button."""
    from app.bot.keyboards.reply import get_main_menu
    
    text = _("welcome_back")
    keyboard = get_main_menu()
    await message.answer(text, reply_markup=keyboard)
