"""
Start router for Karma System bot.
Handles /start command with language selection and policy acceptance.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.inline import get_language_selection, get_policy_accept
from app.bot.keyboards.reply import get_main_menu

router = Router()

@router.message(CommandStart())
async def start_command(message: Message, locale: str, _):
    """Handle /start command."""
    user_id = message.from_user.id
    
    # TODO: Check if user exists in database and get their settings
    # For now, assume new user and show language selection
    
    # Check if user has selected language and accepted policy
    # This would normally come from database
    has_language = False  # TODO: Get from DB
    has_policy = False    # TODO: Get from DB
    
    if not has_language:
        # New user - show language selection
        text = _("welcome_new")
        keyboard = get_language_selection()
        await message.answer(text, reply_markup=keyboard)
    elif not has_policy:
        # Has language but no policy - show policy
        text = _("policy_text")
        keyboard = get_policy_accept()
        await message.answer(text, reply_markup=keyboard)
    else:
        # Existing user - show welcome back
        text = _("welcome_back")
        keyboard = get_main_menu()
        await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data.regexp(r"^lang:set:(ru|en|vi|ko)$"))
async def set_language(callback: CallbackQuery, locale: str, _):
    """Handle language selection."""
    # Extract language from callback data
    selected_lang = callback.data.split(":")[-1]
    
    # TODO: Save language to database
    # await user_service.update_language(callback.from_user.id, selected_lang)
    
    # Show policy acceptance
    text = _("policy_text", selected_lang)
    keyboard = get_policy_accept()
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "policy:accept")
async def accept_policy(callback: CallbackQuery, locale: str, _):
    """Handle policy acceptance."""
    # TODO: Save policy acceptance to database
    # await user_service.accept_policy(callback.from_user.id)
    
    # Show confirmation and main menu
    text = _("policy_accepted")
    await callback.message.edit_text(text)
    
    # Send main menu
    keyboard = get_main_menu()
    menu_text = _("welcome_back")
    await callback.message.answer(menu_text, reply_markup=keyboard)
    
    await callback.answer()
