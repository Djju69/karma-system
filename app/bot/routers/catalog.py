"""
Catalog router for Karma System bot.
Handles category browsing, pagination, and filters.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.keyboards.inline import get_pagination, get_listing_card
from app.core.services.catalog_service import catalog_service
from app.core.authz import authz_service

router = Router()

@router.callback_query(F.data.regexp(r"^pg:(restaurants|spa|transport|hotels|tours):[0-9]+$"))
async def show_category_page(callback: CallbackQuery, locale: str, _):
    """Handle category pagination: ^pg:(restaurants|spa|transport|hotels|tours):[0-9]+$"""
    # Parse callback data
    parts = callback.data.split(":")
    category = parts[1]
    page = int(parts[2])
    
    # TODO: Get user's city from database
    # user = await user_service.get_user(callback.from_user.id)
    # city_id = user.city_id if user else 1  # Default city
    city_id = 1  # Stub: Nha Trang
    
    # TODO: Get from database session
    # db = get_db_session()
    db = None  # Stub for now
    
    if not db:
        await callback.answer("⚠️ Временная ошибка сервиса")
        return
    
    try:
        # Get catalog page
        filters = {}  # Will be populated from callback data if needed
        items, total_count, current_page, total_pages = await catalog_service.get_page(
            db, city_id, category, page, per_page=5, filters=filters
        )
        
        if not items:
            text = _("catalog_empty")
            await callback.message.edit_text(text)
            await callback.answer()
            return
        
        # Build response text
        header = _("catalog_header", count=total_count, page=current_page, pages=total_pages)
        
        # Format items
        items_text = []
        for item in items:
            item_text = f"**{item['name']}** • {item.get('district', '')}\n"
            item_text += f"📍 {item['address']}\n"
            if item.get('phone'):
                item_text += f"☎ {item['phone']}\n"
            items_text.append(item_text)
        
        text = header + "\n\n" + "\n\n".join(items_text)
        
        # Create inline keyboard with pagination and item buttons
        keyboard_buttons = []
        
        # Add item view buttons (5 per page)
        for i, item in enumerate(items):
            row_buttons = []
            row_buttons.append({
                "text": f"{i+1}. ℹ️",
                "callback_data": f"act:view:{item['id']}"
            })
            keyboard_buttons.append(row_buttons)
        
        # Add pagination
        pagination_keyboard = get_pagination(category, current_page, total_pages)
        
        # Combine keyboards
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        combined_buttons = []
        
        # Add item buttons
        for buttons_row in keyboard_buttons:
            combined_buttons.append([
                InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"])
                for btn in buttons_row
            ])
        
        # Add pagination buttons
        combined_buttons.extend(pagination_keyboard.inline_keyboard)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=combined_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
        
    except Exception as e:
        await callback.answer("⚠️ Ошибка загрузки каталога")
        # TODO: Log error

@router.callback_query(F.data.regexp(r"^filt:restaurants:(asia|europe|street|vege|all)$"))
async def filter_restaurants(callback: CallbackQuery, locale: str, _):
    """Handle restaurant filters: ^filt:restaurants:(asia|europe|street|vege|all)$"""
    # Parse filter
    filter_value = callback.data.split(":")[-1]
    
    # TODO: Get user's city from database
    city_id = 1  # Stub: Nha Trang
    
    # TODO: Get from database session
    db = None  # Stub for now
    
    if not db:
        await callback.answer("⚠️ Временная ошибка сервиса")
        return
    
    try:
        # Apply filter
        filters = {}
        if filter_value != "all":
            filters["sub_slug"] = filter_value
        
        # Get filtered results (page 1)
        items, total_count, current_page, total_pages = await catalog_service.get_page(
            db, city_id, "restaurants", 1, per_page=5, filters=filters
        )
        
        # Build response (same as pagination handler)
        if not items:
            text = _("catalog_empty")
            await callback.message.edit_text(text)
            await callback.answer()
            return
        
        header = _("catalog_header", count=total_count, page=current_page, pages=total_pages)
        
        items_text = []
        for item in items:
            item_text = f"**{item['name']}** • {item.get('district', '')}\n"
            item_text += f"📍 {item['address']}\n"
            if item.get('phone'):
                item_text += f"☎ {item['phone']}\n"
            items_text.append(item_text)
        
        text = header + "\n\n" + "\n\n".join(items_text)
        
        # Create keyboard with filtered pagination
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        combined_buttons = []
        
        # Add item buttons
        for i, item in enumerate(items):
            combined_buttons.append([
                InlineKeyboardButton(text=f"{i+1}. ℹ️", callback_data=f"act:view:{item['id']}")
            ])
        
        # Add pagination with filter
        pagination_keyboard = get_pagination("restaurants", current_page, total_pages)
        combined_buttons.extend(pagination_keyboard.inline_keyboard)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=combined_buttons)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
        
    except Exception as e:
        await callback.answer("⚠️ Ошибка применения фильтра")

@router.callback_query(F.data.regexp(r"^act:view:[0-9]+$"))
async def view_listing(callback: CallbackQuery, locale: str, _):
    """Handle listing view: ^act:view:[0-9]+$"""
    # Parse listing ID
    listing_id = int(callback.data.split(":")[-1])
    
    # TODO: Get from database session
    db = None  # Stub for now
    
    if not db:
        await callback.answer("⚠️ Временная ошибка сервиса")
        return
    
    try:
        # Get listing details
        listing = await catalog_service.get_listing(db, listing_id)
        
        if not listing:
            await callback.answer("⚠️ Карточка не найдена")
            return
        
        # Check moderation status
        if listing['moderation_status'] == 'pending':
            text = _("moderation_pending")
            await callback.message.edit_text(text)
            await callback.answer()
            return
        elif listing['moderation_status'] == 'rejected':
            text = _("moderation_rejected")
            await callback.message.edit_text(text)
            await callback.answer()
            return
        elif listing['is_hidden']:
            text = _("hidden_listing")
            await callback.message.edit_text(text)
            await callback.answer()
            return
        
        # Format listing details
        text = _("card_description",
                description=listing['description'],
                address=listing['address'],
                district=listing.get('district', ''),
                phone=listing.get('phone', ''))
        
        # Check if user can create QR
        # TODO: Get user from database
        user = {"id": callback.from_user.id, "role": "user"}  # Stub
        can_create_qr = authz_service.can_create_qr(user, listing)
        
        # Create keyboard
        keyboard = get_listing_card(
            listing_id=listing['id'],
            gmaps_url=listing.get('gmaps_url', ''),
            can_create_qr=can_create_qr
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        await callback.answer("⚠️ Ошибка загрузки карточки")

@router.callback_query(F.data.regexp(r"^contact:[0-9]+$"))
async def contact_listing(callback: CallbackQuery, locale: str, _):
    """Handle contact request."""
    listing_id = int(callback.data.split(":")[-1])
    
    # TODO: Get listing contact info from database
    contact = "@example_contact"  # Stub
    
    text = _("contact_info", contact=contact)
    await callback.answer(text, show_alert=True)

@router.callback_query(F.data.regexp(r"^book:[0-9]+$"))
async def book_listing(callback: CallbackQuery, locale: str, _):
    """Handle booking request."""
    listing_id = int(callback.data.split(":")[-1])
    
    # TODO: Save booking request to database
    
    text = _("booking_confirmed")
    await callback.answer(text, show_alert=True)
