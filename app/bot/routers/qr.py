"""
QR router for Karma System bot.
Handles QR code creation and management.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
import io

from app.core.authz import authz_service

router = Router()

@router.callback_query(F.data.regexp(r"^qr:create:[0-9]+$"))
async def create_qr(callback: CallbackQuery, locale: str, _):
    """Handle QR creation: ^qr:create:[0-9]+$"""
    listing_id = int(callback.data.split(":")[-1])
    
    # TODO: Get user and listing from database
    # user = await user_service.get_user(callback.from_user.id)
    # listing = await catalog_service.get_listing(db, listing_id)
    
    user = {"id": callback.from_user.id, "role": "user"}  # Stub
    listing = {"id": listing_id, "moderation_status": "approved", "is_hidden": False, "user_id": callback.from_user.id}  # Stub
    
    # Check permissions
    if not authz_service.can_create_qr(user, listing):
        text = _("qr_no_permission")
        await callback.answer(text, show_alert=True)
        return
    
    try:
        # TODO: Create QR code
        # token, png_bytes = await qr_service.create_qr(user['id'], listing_id)
        
        # Stub: Create simple QR placeholder
        png_bytes = create_qr_placeholder(listing_id)
        
        # Send QR as photo
        photo = BufferedInputFile(png_bytes, filename=f"qr_{listing_id}.png")
        caption = _("qr_created")
        
        await callback.message.answer_photo(photo, caption=caption)
        await callback.answer()
        
    except Exception as e:
        await callback.answer("⚠️ Ошибка создания QR-кода")

def create_qr_placeholder(listing_id: int) -> bytes:
    """Create QR code placeholder (stub implementation)."""
    # This is a stub - in real implementation would use qrcode library
    # and Fernet encryption
    
    # Create simple PNG placeholder
    from PIL import Image, ImageDraw, ImageFont
    
    # Create white image
    img = Image.new('RGB', (200, 200), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([10, 10, 190, 190], outline='black', width=2)
    
    # Add text
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    text = f"QR Code\nListing #{listing_id}\n24h validity"
    draw.text((20, 80), text, fill='black', font=font)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()
