"""
Listings API routes.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.database import get_db
from app.core.services.catalog_service import CatalogService

router = APIRouter()

@router.get("/")
async def get_listings(
    city_id: int = Query(..., description="City ID"),
    category: str = Query(..., description="Category slug"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Items per page"),
    restaurant_sub_slug: Optional[str] = Query(None, description="Restaurant filter"),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated listings."""
    try:
        service = CatalogService()
        filters = {}
        if restaurant_sub_slug:
            filters["restaurant_sub_slug"] = restaurant_sub_slug
            
        result = await service.get_listings(
            db, city_id, category, page, per_page, filters
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{listing_id}")
async def get_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get single listing by ID."""
    try:
        service = CatalogService()
        listing = await service.get_listing_by_id(db, listing_id)
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        return listing
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
