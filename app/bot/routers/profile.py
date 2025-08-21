"""
Profile router for Karma System bot.
Handles user profile management (city, language, policy).
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.keyboards.inline import get_cities, get_language_selection, get_policy_accept
from app.core.services.city_service import city_service

router = Router()

@router.callback_query(F.data == "profile:city")
async def profile_city(callback: CallbackQuery, locale: str, _):
    """Handle city selection in profile."""
    # TODO: Get from database session
    db = None  # Stub for now
    
    if not db:
        await callback.answer("⚠️ Временная ошибка сервиса")
        return
    
    try:
        # Get all cities
        cities = await city_service.get_all_cities(db)
        
        text = _("city_select")
        keyboard = get_cities(cities)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        await callback.answer("⚠️ Ошибка загрузки городов")

@router.callback_query(F.data.regexp(r"^city:set:[0-9]+$"))
async def set_city(callback: CallbackQuery, locale: str, _):
    """Handle city selection: ^city:set:[0-9]+$"""
    city_id = int(callback.data.split(":")[-1])
    
    # TODO: Get from database session
    db = None  # Stub for now
    
    if not db:
        await callback.answer("⚠️ Временная ошибка сервиса")
        return
    
    try:
        # Get city info
        city = await city_service.get_city_by_id(db, city_id)
        
        if not city:
            await callback.answer("⚠️ Город не найден")
            return
        
        # TODO: Update user city in database
        # await user_service.update_city(callback.from_user.id, city_id)
        
        text = _("city_selected", city=city['name'])
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        await callback.answer("⚠️ Ошибка установки города")

@router.callback_query(F.data == "profile:lang")
async def profile_language(callback: CallbackQuery, locale: str, _):
    """Handle language selection in profile."""
    text = _("language_select")
    keyboard = get_language_selection()
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "profile:policy")
async def profile_policy(callback: CallbackQuery, locale: str, _):
    """Handle policy acceptance in profile."""
    text = _("policy_text")
    keyboard = get_policy_accept()
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "profile:notify")
async def profile_notifications(callback: CallbackQuery, locale: str, _):
    """Handle notification settings (partner only)."""
    # TODO: Implement notification settings
    await callback.answer("🔔 Настройки уведомлений в разработке")

@router.callback_query(F.data == "partner:become")
async def become_partner(callback: CallbackQuery, locale: str, _):
    """Handle partner registration start."""
    # This will be handled by partner router
    from app.bot.routers.partner import start_partner_registration
    await start_partner_registration(callback, locale, _)
