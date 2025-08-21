"""
Inline keyboards for Karma System bot.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def get_language_selection() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang:set:ru"),
            InlineKeyboardButton(text="English 🇬🇧", callback_data="lang:set:en")
        ],
        [
            InlineKeyboardButton(text="Tiếng Việt 🇻🇳", callback_data="lang:set:vi"),
            InlineKeyboardButton(text="한국어 🇰🇷", callback_data="lang:set:ko")
        ]
    ])

def get_policy_accept() -> InlineKeyboardMarkup:
    """Get policy acceptance keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ПРИНЯТЬ ✅", callback_data="policy:accept")]
    ])

def get_categories() -> InlineKeyboardMarkup:
    """Get categories selection keyboard (exactly 5)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽 Рестораны и кафе", callback_data="pg:restaurants:1"),
            InlineKeyboardButton(text="🧖‍♀️ SPA и массаж", callback_data="pg:spa:1")
        ],
        [
            InlineKeyboardButton(text="🚗 Аренда транспорта", callback_data="pg:transport:1"),
            InlineKeyboardButton(text="🏨 Отели", callback_data="pg:hotels:1")
        ],
        [
            InlineKeyboardButton(text="🚶‍♂️ Экскурсии", callback_data="pg:tours:1")
        ]
    ])

def get_restaurant_filters() -> InlineKeyboardMarkup:
    """Get restaurant filters keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🥢 Азиатская", callback_data="filt:restaurants:asia"),
            InlineKeyboardButton(text="🍝 Европейская", callback_data="filt:restaurants:europe")
        ],
        [
            InlineKeyboardButton(text="🌭 Стрит-фуд", callback_data="filt:restaurants:street"),
            InlineKeyboardButton(text="🥗 Вегетарианская", callback_data="filt:restaurants:vege")
        ],
        [
            InlineKeyboardButton(text="🔎 Показать все", callback_data="filt:restaurants:all")
        ]
    ])

def get_profile_guest() -> InlineKeyboardMarkup:
    """Get guest profile keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧑‍💼 Стать партнёром", callback_data="partner:become")],
        [
            InlineKeyboardButton(text="🌆 Город", callback_data="profile:city"),
            InlineKeyboardButton(text="🌐 Язык", callback_data="profile:lang")
        ],
        [InlineKeyboardButton(text="📄 Политика", callback_data="profile:policy")]
    ])

def get_profile_partner() -> InlineKeyboardMarkup:
    """Get partner profile keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧾 Сканировать QR", callback_data="qr:scan")],
        [
            InlineKeyboardButton(text="🌆 Город", callback_data="profile:city"),
            InlineKeyboardButton(text="🔔 Уведомления", callback_data="profile:notify")
        ],
        [
            InlineKeyboardButton(text="🌐 Язык", callback_data="profile:lang"),
            InlineKeyboardButton(text="📄 Политика", callback_data="profile:policy")
        ]
    ])

def get_listing_card(listing_id: int, gmaps_url: str, can_create_qr: bool = False) -> InlineKeyboardMarkup:
    """Get listing card keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="Показать на карте", url=gmaps_url),
            InlineKeyboardButton(text="Связаться", callback_data=f"contact:{listing_id}")
        ],
        [InlineKeyboardButton(text="Записаться", callback_data=f"book:{listing_id}")]
    ]
    
    if can_create_qr:
        buttons.append([InlineKeyboardButton(text="🎫 Создать QR", callback_data=f"qr:create:{listing_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_pagination(category: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Get pagination keyboard."""
    buttons = []
    
    # Navigation buttons
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"pg:{category}:{page-1}"))
    
    nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"pg:{category}:{page+1}"))
    
    buttons.append(nav_row)
    
    # Add filters for restaurants
    if category == "restaurants":
        buttons.extend(get_restaurant_filters().inline_keyboard)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cities(cities: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Get cities selection keyboard."""
    buttons = []
    for city in cities:
        buttons.append([InlineKeyboardButton(
            text=city['name'], 
            callback_data=f"city:set:{city['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_partner_categories() -> InlineKeyboardMarkup:
    """Get partner categories for FSM."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽 Рестораны", callback_data="fsm:category:restaurants"),
            InlineKeyboardButton(text="🧖‍♀️ SPA", callback_data="fsm:category:spa")
        ],
        [
            InlineKeyboardButton(text="🚗 Транспорт", callback_data="fsm:category:transport"),
            InlineKeyboardButton(text="🏨 Отели", callback_data="fsm:category:hotels")
        ],
        [
            InlineKeyboardButton(text="🚶‍♂️ Экскурсии", callback_data="fsm:category:tours")
        ]
    ])

def get_restaurant_subcategories() -> InlineKeyboardMarkup:
    """Get restaurant subcategories for FSM."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🥢 Азиатская", callback_data="fsm:sub:asia"),
            InlineKeyboardButton(text="🍝 Европейская", callback_data="fsm:sub:europe")
        ],
        [
            InlineKeyboardButton(text="🌭 Стрит-фуд", callback_data="fsm:sub:street"),
            InlineKeyboardButton(text="🥗 Вегетарианская", callback_data="fsm:sub:vege")
        ]
    ])
