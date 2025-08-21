"""
Partners API routes.
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List

from app.db.database import get_db
from app.core.services.partners_service import partners_service
from app.core.authz import require_role, UserRole

router = APIRouter()

class PartnerApplicationRequest(BaseModel):
    contact_name: str
    contact_phone: str
    contact_email: Optional[str] = None
    telegram_username: Optional[str] = None
    business_name: str
    business_address: str
    city_id: int
    category: str
    description: Optional[str] = None
    website: Optional[str] = None
    instagram: Optional[str] = None
    average_check: Optional[int] = None

class WebAuthRequest(BaseModel):
    email: str
    password: str

@router.post("/applications")
async def create_application(
    application: PartnerApplicationRequest,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create partner application."""
    try:
        result = await partners_service.create_application(
            db=db,
            user_id=user_id,
            contact_name=application.contact_name,
            contact_phone=application.contact_phone,
            business_name=application.business_name,
            business_address=application.business_address,
            city_id=application.city_id,
            category=application.category,
            description=application.description,
            contact_email=application.contact_email,
            telegram_username=application.telegram_username,
            website=application.website,
            instagram=application.instagram,
            average_check=application.average_check
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web-auth")
async def create_web_auth(
    auth_data: WebAuthRequest,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Create web authentication for partner."""
    try:
        result = await partners_service.create_web_auth(
            db=db,
            user_id=user_id,
            email=auth_data.email,
            password=auth_data.password
        )
        if result:
            return {"success": True, "message": "Web auth created"}
        else:
            raise HTTPException(status_code=400, detail="Failed to create web auth")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/applications/{application_id}/approve")
async def approve_application(
    application_id: int,
    admin_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Approve partner application."""
    try:
        result = await partners_service.approve_application(
            db=db,
            application_id=application_id,
            admin_user_id=admin_user_id
        )
        if result:
            return {"success": True, "message": "Application approved"}
        else:
            raise HTTPException(status_code=404, detail="Application not found or already processed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/applications/{application_id}/reject")
async def reject_application(
    application_id: int,
    reason: str = Body(..., embed=True),
    admin_user_id: int = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """Reject partner application."""
    try:
        result = await partners_service.reject_application(
            db=db,
            application_id=application_id,
            reason=reason,
            admin_user_id=admin_user_id
        )
        if result:
            return {"success": True, "message": "Application rejected"}
        else:
            raise HTTPException(status_code=404, detail="Application not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/listings/{user_id}")
async def get_partner_listings(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get partner's listings."""
    try:
        listings = await partners_service.get_partner_listings(db, user_id)
        return {"listings": listings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
