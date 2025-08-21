"""
QR code API routes.
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.core.services.qr_service import qr_service

router = APIRouter()

class QRRedeemRequest(BaseModel):
    jti: str
    user_id: int

@router.post("/redeem")
async def redeem_qr(
    request: QRRedeemRequest,
    db: AsyncSession = Depends(get_db)
):
    """Redeem QR code by JTI."""
    try:
        result = await qr_service.redeem_qr(db, request.jti, request.user_id)
        if result:
            return {"success": True, "message": "QR code redeemed successfully"}
        else:
            raise HTTPException(status_code=400, detail="QR code already redeemed or expired")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/validate/{jti}")
async def validate_qr(
    jti: str,
    db: AsyncSession = Depends(get_db)
):
    """Validate QR code without redeeming."""
    try:
        qr_issue = await qr_service.get_qr_by_jti(db, jti)
        if qr_issue:
            return {
                "valid": True,
                "status": qr_issue.status,
                "expires_at": qr_issue.expires_at,
                "listing_id": qr_issue.listing_id
            }
        else:
            return {"valid": False, "message": "QR code not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/image/{jti}")
async def get_qr_image(
    jti: str,
    db: AsyncSession = Depends(get_db)
):
    """Get QR code image."""
    try:
        qr_image = await qr_service.generate_qr_image(jti)
        return Response(content=qr_image, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
