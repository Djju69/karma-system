"""
QR service for Karma System with Fernet encryption.
"""
import os
import uuid
import qrcode
import io
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from PIL import Image, ImageDraw

from app.db.models import QRIssue

class QRService:
    """Service for QR code generation and redemption."""
    
    def __init__(self):
        self.fernet_key = self._get_fernet_key()
        self.fernet = Fernet(self.fernet_key) if self.fernet_key else None
    
    def _get_fernet_key(self) -> Optional[bytes]:
        """Get Fernet key from environment."""
        hex_key = os.getenv('FERNET_KEY_HEX')
        if not hex_key or len(hex_key) != 64:
            return None
        
        try:
            # Convert 64 hex chars to 32 bytes
            key_bytes = bytes.fromhex(hex_key)
            # Convert to Fernet format (base64)
            import base64
            return base64.urlsafe_b64encode(key_bytes)
        except Exception:
            return None
    
    async def create_qr(
        self, 
        db: AsyncSession, 
        user_id: int, 
        listing_id: int,
        karma_amount: int = 100,
        order_amount: Optional[int] = None,
        description: Optional[str] = None
    ) -> Tuple[str, bytes]:
        """
        Create QR code with Fernet encryption.
        Returns: (token, png_bytes)
        """
        if not self.fernet:
            raise ValueError("Fernet encryption not configured")
        
        # Generate unique JTI
        jti = uuid.uuid4().hex
        
        # Set expiration (24 hours)
        exp_at = datetime.utcnow() + timedelta(hours=24)
        
        # Create QR issue record
        qr_issue = QRIssue(
            jti=jti,
            user_id=user_id,
            listing_id=listing_id,
            karma_amount=karma_amount,
            order_amount=order_amount,
            description=description,
            exp_at=exp_at,
            status='issued'
        )
        
        db.add(qr_issue)
        await db.commit()
        
        # Encrypt JTI (payload contains only JTI)
        token = self.fernet.encrypt(jti.encode()).decode()
        
        # Generate QR code PNG
        png_bytes = self._generate_qr_png(token, listing_id)
        
        return token, png_bytes
    
    async def redeem(
        self, 
        db: AsyncSession, 
        token: str, 
        redeemed_by_partner_id: int
    ) -> Dict[str, any]:
        """
        Redeem QR code atomically.
        Returns: {success: bool, reason?: str, qr_issue?: dict}
        """
        if not self.fernet:
            return {"success": False, "reason": "invalid_token"}
        
        try:
            # Decrypt token to get JTI
            jti = self.fernet.decrypt(token.encode()).decode()
        except Exception:
            return {"success": False, "reason": "invalid_token"}
        
        # Atomic redemption with single SQL query
        query = (
            update(QRIssue)
            .where(
                QRIssue.jti == jti,
                QRIssue.status == 'issued',
                QRIssue.exp_at >= datetime.utcnow()
            )
            .values(
                status='redeemed',
                redeemed_at=datetime.utcnow(),
                redeemed_by_partner_id=redeemed_by_partner_id
            )
            .returning(QRIssue)
        )
        
        result = await db.execute(query)
        qr_issue = result.scalar_one_or_none()
        
        if qr_issue:
            await db.commit()
            return {
                "success": True,
                "qr_issue": {
                    "id": qr_issue.id,
                    "karma_amount": qr_issue.karma_amount,
                    "order_amount": qr_issue.order_amount,
                    "description": qr_issue.description,
                    "user_id": qr_issue.user_id,
                    "listing_id": qr_issue.listing_id
                }
            }
        else:
            # Check specific failure reason
            check_query = select(QRIssue).where(QRIssue.jti == jti)
            check_result = await db.execute(check_query)
            existing = check_result.scalar_one_or_none()
            
            if not existing:
                return {"success": False, "reason": "not_found"}
            elif existing.status == 'redeemed':
                return {"success": False, "reason": "already_redeemed"}
            elif existing.exp_at < datetime.utcnow():
                return {"success": False, "reason": "expired"}
            else:
                return {"success": False, "reason": "invalid_state"}
    
    def _generate_qr_png(self, token: str, listing_id: int) -> bytes:
        """Generate QR code PNG with logo overlay."""
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(token)
        qr.make(fit=True)
        
        # Create QR image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.convert('RGB')
        
        # Add logo overlay (optional)
        try:
            # Simple text overlay instead of logo for now
            from PIL import ImageFont, ImageDraw
            draw = ImageDraw.Draw(qr_img)
            
            # Add small text in corner
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            text = f"#{listing_id}"
            draw.text((10, 10), text, fill='black', font=font)
            
        except Exception:
            pass  # Skip overlay if fails
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        qr_img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    async def get_user_qr_codes(
        self, 
        db: AsyncSession, 
        user_id: int, 
        status: Optional[str] = None
    ) -> list:
        """Get user's QR codes."""
        query = select(QRIssue).where(QRIssue.user_id == user_id)
        
        if status:
            query = query.where(QRIssue.status == status)
        
        query = query.order_by(QRIssue.created_at.desc())
        
        result = await db.execute(query)
        qr_issues = result.scalars().all()
        
        return [
            {
                "id": qr.id,
                "jti": qr.jti,
                "listing_id": qr.listing_id,
                "karma_amount": qr.karma_amount,
                "status": qr.status,
                "exp_at": qr.exp_at,
                "created_at": qr.created_at,
                "redeemed_at": qr.redeemed_at
            }
            for qr in qr_issues
        ]

# Global service instance
qr_service = QRService()
