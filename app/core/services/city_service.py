"""
City service for Karma System.
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import City

class CityService:
    """Service for city operations."""
    
    async def get_all_cities(self, db: AsyncSession) -> List[Dict]:
        """Get all active cities."""
        query = select(City).where(City.is_active == True).order_by(City.name)
        result = await db.execute(query)
        cities = result.scalars().all()
        
        return [
            {
                'id': city.id,
                'name': city.name,
                'slug': city.slug,
                'country_code': city.country_code,
                'is_default': city.is_default
            }
            for city in cities
        ]
    
    async def get_default_city(self, db: AsyncSession) -> Optional[Dict]:
        """Get default city."""
        query = select(City).where(City.is_default == True)
        result = await db.execute(query)
        city = result.scalar_one_or_none()
        
        if city:
            return {
                'id': city.id,
                'name': city.name,
                'slug': city.slug,
                'country_code': city.country_code,
                'is_default': city.is_default
            }
        return None
    
    async def get_city_by_id(self, db: AsyncSession, city_id: int) -> Optional[Dict]:
        """Get city by ID."""
        query = select(City).where(City.id == city_id)
        result = await db.execute(query)
        city = result.scalar_one_or_none()
        
        if city:
            return {
                'id': city.id,
                'name': city.name,
                'slug': city.slug,
                'country_code': city.country_code,
                'is_default': city.is_default
            }
        return None
    
    async def get_city_by_slug(self, db: AsyncSession, slug: str) -> Optional[Dict]:
        """Get city by slug."""
        query = select(City).where(City.slug == slug)
        result = await db.execute(query)
        city = result.scalar_one_or_none()
        
        if city:
            return {
                'id': city.id,
                'name': city.name,
                'slug': city.slug,
                'country_code': city.country_code,
                'is_default': city.is_default
            }
        return None
    
    async def set_default_city(self, db: AsyncSession, city_id: int) -> bool:
        """Set default city (admin only)."""
        try:
            # Remove default from all cities
            await db.execute(
                update(City).values(is_default=False)
            )
            
            # Set new default
            await db.execute(
                update(City).where(City.id == city_id).values(is_default=True)
            )
            
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            return False

# Global service instance
city_service = CityService()
