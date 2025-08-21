"""
Partners API routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.services.partners_service import PartnersService

router = APIRouter()

@router.get("/stats/{partner_id}")
async def get_partner_stats(
    partner_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get partner statistics."""
    try:
        service = PartnersService()
        stats = await service.get_partner_stats(db, partner_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/approve/{partner_id}")
async def approve_partner(
    partner_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Approve partner registration."""
    try:
        service = PartnersService()
        result = await service.approve_partner(db, partner_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/reject/{partner_id}")
async def reject_partner(
    partner_id: int,
    reason: str,
    db: AsyncSession = Depends(get_db)
):
    """Reject partner registration."""
    try:
        service = PartnersService()
        result = await service.reject_partner(db, partner_id, reason)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
