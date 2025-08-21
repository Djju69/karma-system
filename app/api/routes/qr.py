"""
QR code API routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.services.qr_service import QRService

router = APIRouter()

@router.post("/redeem/{qr_code}")
async def redeem_qr(
    qr_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Redeem QR code."""
    try:
        qr_service = QRService()
        result = await qr_service.redeem_qr(db, qr_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/validate/{qr_code}")
async def validate_qr(
    qr_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Validate QR code without redeeming."""
    try:
        qr_service = QRService()
        result = await qr_service.validate_qr(db, qr_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
