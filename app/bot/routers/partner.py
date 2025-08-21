"""
Partner router for Karma System bot.
Handles partner registration FSM and partner-specific actions.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.fsm.partner_registration import PartnerRegistration
from app.bot.keyboards.inline import get_partner_categories, get_restaurant_subcategories

router = Router()

async def start_partner_registration(callback: CallbackQuery, locale: str, _, state: FSMContext = None):
    """Start partner registration FSM."""
    if state is None:
        # This shouldn't happen, but handle gracefully
        await callback.answer("⚠️ Ошибка инициализации регистрации")
        return
    
    # Set FSM state
    await state.set_state(PartnerRegistration.company_data)
    
    text = _("fsm.partner_company")
    await callback.message.edit_text(text)
    await callback.answer()

@router.message(PartnerRegistration.company_data)
async def partner_company_data(message: Message, state: FSMContext, locale: str, _):
    """Handle company name input."""
    company_name = message.text.strip()
    
    if len(company_name) < 2:
        await message.answer("⚠️ Название компании слишком короткое")
        return
    
    # Save company name
    await state.update_data(company_name=company_name)
    
    # Ask for phone
    text = _("fsm.partner_phone")
    await message.answer(text)
    
    # Move to next state
    await state.set_state(PartnerRegistration.description)

@router.message(PartnerRegistration.description)
async def partner_description(message: Message, state: FSMContext, locale: str, _):
    """Handle phone and description input."""
    data = await state.get_data()
    
    if 'phone' not in data:
        # First message is phone
        phone = message.text.strip()
        if len(phone) < 10:
            await message.answer("⚠️ Некорректный номер телефона")
            return
        
        await state.update_data(phone=phone)
        
        # Ask for description
        text = _("fsm.partner_description")
        await message.answer(text)
        return
    
    # Second message is description
    description = message.text.strip()
    if len(description) < 10:
        await message.answer("⚠️ Описание слишком короткое")
        return
    
    await state.update_data(description=description)
    
    # Ask for category
    text = _("fsm.partner_category")
    keyboard = get_partner_categories()
    await message.answer(text, reply_markup=keyboard)
    
    await state.set_state(PartnerRegistration.offer_details)

@router.callback_query(F.data.regexp(r"^fsm:category:(restaurants|spa|transport|hotels|tours)$"), PartnerRegistration.offer_details)
async def partner_category(callback: CallbackQuery, state: FSMContext, locale: str, _):
    """Handle category selection."""
    category = callback.data.split(":")[-1]
    await state.update_data(category=category)
    
    if category == "restaurants":
        # Ask for restaurant subcategory
        text = "🍽 Выберите тип кухни:"
        keyboard = get_restaurant_subcategories()
        await callback.message.edit_text(text, reply_markup=keyboard)
    else:
        # Skip subcategory for other categories
        await state.update_data(sub_slug=None)
        await ask_offer_details(callback, state, locale, _)
    
    await callback.answer()

@router.callback_query(F.data.regexp(r"^fsm:sub:(asia|europe|street|vege)$"), PartnerRegistration.offer_details)
async def partner_subcategory(callback: CallbackQuery, state: FSMContext, locale: str, _):
    """Handle restaurant subcategory selection."""
    sub_slug = callback.data.split(":")[-1]
    await state.update_data(sub_slug=sub_slug)
    
    await ask_offer_details(callback, state, locale, _)
    await callback.answer()

async def ask_offer_details(callback: CallbackQuery, state: FSMContext, locale: str, _):
    """Ask for offer details."""
    text = _("fsm.partner_offer")
    await callback.message.edit_text(text)
    await state.set_state(PartnerRegistration.confirmation)

@router.message(PartnerRegistration.confirmation)
async def partner_confirmation(message: Message, state: FSMContext, locale: str, _):
    """Handle offer details and create application."""
    offer_details = message.text.strip()
    
    if len(offer_details) < 10:
        await message.answer("⚠️ Описание условий слишком короткое")
        return
    
    await state.update_data(offer_details=offer_details)
    
    # TODO: Save partner application to database
    data = await state.get_data()
    # await partner_service.create_application(
    #     user_id=message.from_user.id,
    #     company_name=data['company_name'],
    #     phone=data['phone'],
    #     description=data['description'],
    #     category=data['category'],
    #     sub_slug=data.get('sub_slug'),
    #     offer_details=data['offer_details']
    # )
    
    # Confirmation message
    text = _("fsm.partner_confirmation")
    await message.answer(text)
    
    # Ask for web auth credentials
    text = _("fsm.partner_email")
    await message.answer(text)
    
    await state.set_state(PartnerRegistration.web_auth)

@router.message(PartnerRegistration.web_auth)
async def partner_web_auth(message: Message, state: FSMContext, locale: str, _):
    """Handle web authentication setup."""
    data = await state.get_data()
    
    if 'email' not in data:
        # First message is email
        email = message.text.strip()
        if '@' not in email or '.' not in email:
            await message.answer("⚠️ Некорректный email")
            return
        
        await state.update_data(email=email)
        
        # Ask for password
        text = _("fsm.partner_password")
        await message.answer(text)
        return
    
    # Second message is password
    password = message.text.strip()
    if len(password) < 6:
        await message.answer("⚠️ Пароль слишком короткий (минимум 6 символов)")
        return
    
    await state.update_data(password=password)
    
    # TODO: Create partner auth record
    # await partner_service.create_web_auth(
    #     user_id=message.from_user.id,
    #     email=data['email'],
    #     password=password
    # )
    
    # Complete registration
    text = _("fsm.partner_complete")
    await message.answer(text)
    
    # Clear FSM state
    await state.clear()

@router.callback_query(F.data == "qr:scan")
async def scan_qr(callback: CallbackQuery, locale: str, _):
    """Handle QR scanning (partner/admin only)."""
    # TODO: Check if user is partner or admin
    # user = await user_service.get_user(callback.from_user.id)
    # if not authz_service.can_scan_qr(user):
    #     await callback.answer("⛔ Доступ запрещен")
    #     return
    
    text = _("qr_scan_prompt")
    
    # Add WebApp button for QR scanning
    import os
    webapp_url = os.getenv("WEBAPP_QR_URL", "https://example.com/qr-scan")
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📷 Открыть сканер", web_app=WebAppInfo(url=webapp_url))]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
