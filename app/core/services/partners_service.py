"""
Partners service for Karma System.
"""
import hashlib
import os
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.db.models import (
    User, PartnerProfile, PartnerAuth, PartnerApplication, 
    Listing, UserRole, PartnerStatus
)

class PartnersService:
    """Service for partner operations."""
    
    async def create_application(
        self,
        db: AsyncSession,
        user_id: int,
        contact_name: str,
        contact_phone: str,
        business_name: str,
        business_address: str,
        city_id: int,
        category: str,
        description: Optional[str] = None,
        contact_email: Optional[str] = None,
        telegram_username: Optional[str] = None,
        website: Optional[str] = None,
        instagram: Optional[str] = None,
        average_check: Optional[int] = None,
        category_id: Optional[int] = None
    ) -> Dict:
        """Create partner application."""
        
        # Hash phone number
        phone_hash = self._hash_phone(contact_phone)
        
        application = PartnerApplication(
            contact_name=contact_name,
            contact_phone=phone_hash,
            contact_email=contact_email,
            telegram_username=telegram_username,
            business_name=business_name,
            business_address=business_address,
            city_id=city_id,
            category_id=category_id,
            description=description,
            website=website,
            instagram=instagram,
            average_check=average_check,
            status=PartnerStatus.PENDING
        )
        
        db.add(application)
        await db.commit()
        await db.refresh(application)
        
        return {
            "id": application.id,
            "status": application.status,
            "created_at": application.created_at
        }
    
    async def create_web_auth(
        self,
        db: AsyncSession,
        user_id: int,
        email: str,
        password: str
    ) -> bool:
        """Create web authentication for partner."""
        try:
            # Hash password
            password_hash = self._hash_password(password)
            
            auth = PartnerAuth(
                user_id=user_id,
                email=email,
                password_hash=password_hash
            )
            
            db.add(auth)
            await db.commit()
            return True
            
        except Exception:
            await db.rollback()
            return False
    
    async def approve_application(
        self,
        db: AsyncSession,
        application_id: int,
        admin_user_id: int
    ) -> bool:
        """Approve partner application and create partner profile."""
        try:
            # Get application
            query = select(PartnerApplication).where(
                PartnerApplication.id == application_id
            )
            result = await db.execute(query)
            application = result.scalar_one_or_none()
            
            if not application or application.status != PartnerStatus.PENDING:
                return False
            
            # Update user role to partner
            await db.execute(
                update(User)
                .where(User.id == application.user_id)
                .values(role=UserRole.PARTNER)
            )
            
            # Create partner profile
            profile = PartnerProfile(
                user_id=application.user_id,
                company_name=application.business_name,
                phone_hash=application.contact_phone,
                settings={},
                notify={
                    "qr": True,
                    "moderation": True,
                    "block": True,
                    "system": True
                }
            )
            db.add(profile)
            
            # Create listing
            listing = Listing(
                city_id=application.city_id,
                partner_profile_id=profile.id,
                user_id=application.user_id,
                category=application.category,
                name=application.business_name,
                description=application.description,
                address=application.business_address,
                phone=application.contact_phone,
                moderation_status='approved',
                is_hidden=False
            )
            db.add(listing)
            
            # Update application status
            application.status = PartnerStatus.ACTIVE
            application.processed_at = datetime.utcnow()
            application.partner_id = profile.id
            
            await db.commit()
            
            # Invalidate cache
            from app.core.services.catalog_service import catalog_service
            await catalog_service.invalidate_cache(application.city_id)
            
            return True
            
        except Exception:
            await db.rollback()
            return False
    
    async def reject_application(
        self,
        db: AsyncSession,
        application_id: int,
        reason: str,
        admin_user_id: int
    ) -> bool:
        """Reject partner application."""
        try:
            query = (
                update(PartnerApplication)
                .where(PartnerApplication.id == application_id)
                .values(
                    status=PartnerStatus.REJECTED,
                    rejection_reason=reason,
                    processed_at=datetime.utcnow()
                )
            )
            
            await db.execute(query)
            await db.commit()
            return True
            
        except Exception:
            await db.rollback()
            return False
    
    async def get_partner_listings(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[Dict]:
        """Get partner's listings."""
        query = (
            select(Listing)
            .where(Listing.user_id == user_id)
            .options(selectinload(Listing.city))
            .order_by(Listing.created_at.desc())
        )
        
        result = await db.execute(query)
        listings = result.scalars().all()
        
        return [
            {
                "id": listing.id,
                "name": listing.name,
                "category": listing.category,
                "moderation_status": listing.moderation_status,
                "is_hidden": listing.is_hidden,
                "city": listing.city.name if listing.city else None,
                "created_at": listing.created_at
            }
            for listing in listings
        ]
    
    def _hash_phone(self, phone: str) -> str:
        """Hash phone number with salt."""
        salt = os.getenv('PHONE_SALT', 'default_salt')
        return hashlib.sha256((phone + salt).encode()).hexdigest()
    
    def _hash_password(self, password: str) -> str:
        """Hash password."""
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def _verify_password(self, password: str, hash: str) -> bool:
        """Verify password against hash."""
        import bcrypt
        return bcrypt.checkpw(password.encode(), hash.encode())

# Global service instance
partners_service = PartnersService()
