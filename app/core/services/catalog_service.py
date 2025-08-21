"""
Catalog service for Karma System.
"""
import hashlib
import json
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.db.models import Listing, City, Category, PartnerStatus
from app.core.cache import get_cache

class CatalogService:
    """Service for catalog operations with caching."""
    
    def __init__(self):
        self.cache = None
    
    async def _get_cache(self):
        """Get cache service instance."""
        if self.cache is None:
            self.cache = await get_cache()
        return self.cache
    
    def _make_filters_hash(self, filters: Optional[Dict] = None) -> str:
        """Generate hash for filters to use in cache key."""
        if not filters:
            return "none"
        
        filters_str = json.dumps(filters, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(filters_str.encode()).hexdigest()[:8]
    
    async def get_page(
        self,
        db: AsyncSession,
        city_id: int,
        category: str,
        page: int = 1,
        per_page: int = 5,
        filters: Optional[Dict] = None
    ) -> Tuple[List[Dict], int, int, int]:
        """
        Get paginated catalog with caching.
        Returns: (items, total_count, current_page, total_pages)
        """
        cache = await self._get_cache()
        filters_hash = self._make_filters_hash(filters)
        cache_key = f"catalog:{city_id}:{category}:{page}:{filters_hash}"
        
        # Try cache first
        cached_result = await cache.get(cache_key)
        if cached_result:
            return (
                cached_result['items'],
                cached_result['total_count'],
                cached_result['current_page'],
                cached_result['total_pages']
            )
        
        # Build query
        query = select(Listing).where(
            and_(
                Listing.city_id == city_id,
                Listing.category == category,
                Listing.moderation_status == 'approved',
                Listing.is_hidden == False
            )
        ).options(
            selectinload(Listing.city),
            selectinload(Listing.partner_profile)
        ).order_by(
            Listing.priority_level.desc(),
            Listing.created_at.desc()
        )
        
        # Apply filters
        if filters and category == "restaurants":
            sub_slug = filters.get('sub_slug')
            if sub_slug and sub_slug != 'all':
                query = query.where(Listing.sub_slug == sub_slug)
        
        # Get total count
        count_query = select(func.count(Listing.id)).where(
            and_(
                Listing.city_id == city_id,
                Listing.category == category,
                Listing.moderation_status == 'approved',
                Listing.is_hidden == False
            )
        )
        
        if filters and category == "restaurants":
            sub_slug = filters.get('sub_slug')
            if sub_slug and sub_slug != 'all':
                count_query = count_query.where(Listing.sub_slug == sub_slug)
        
        total_count = await db.scalar(count_query)
        total_pages = (total_count + per_page - 1) // per_page
        
        # Get paginated results
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await db.execute(query)
        listings = result.scalars().all()
        
        # Convert to dict format
        items = []
        for listing in listings:
            items.append({
                'id': listing.id,
                'name': listing.name,
                'description': listing.description,
                'address': listing.address,
                'district': listing.district,
                'phone': listing.phone,
                'gmaps_url': listing.gmaps_url,
                'brand_logo_url': listing.brand_logo_url,
                'category': listing.category,
                'sub_slug': listing.sub_slug,
                'partner_id': listing.partner_profile_id,
                'user_id': listing.user_id
            })
        
        # Cache result
        result_data = {
            'items': items,
            'total_count': total_count,
            'current_page': page,
            'total_pages': total_pages
        }
        
        await cache.set(cache_key, result_data, ttl=300)  # 5 minutes
        
        return items, total_count, page, total_pages
    
    async def get_listing(self, db: AsyncSession, listing_id: int) -> Optional[Dict]:
        """Get single listing by ID."""
        query = select(Listing).where(Listing.id == listing_id).options(
            selectinload(Listing.city),
            selectinload(Listing.partner_profile)
        )
        
        result = await db.execute(query)
        listing = result.scalar_one_or_none()
        
        if not listing:
            return None
        
        return {
            'id': listing.id,
            'name': listing.name,
            'description': listing.description,
            'address': listing.address,
            'district': listing.district,
            'phone': listing.phone,
            'gmaps_url': listing.gmaps_url,
            'brand_logo_url': listing.brand_logo_url,
            'category': listing.category,
            'sub_slug': listing.sub_slug,
            'moderation_status': listing.moderation_status,
            'is_hidden': listing.is_hidden,
            'partner_id': listing.partner_profile_id,
            'user_id': listing.user_id,
            'city': listing.city.name if listing.city else None
        }
    
    async def invalidate_cache(self, city_id: int):
        """Invalidate catalog cache for city."""
        cache = await self._get_cache()
        await cache.invalidate_city_cache(city_id)

# Global service instance
catalog_service = CatalogService()
