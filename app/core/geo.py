"""
Geo service for Karma System with PostGIS support.
"""
from typing import Optional, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.db.models import City

class GeoService:
    """Service for geolocation operations."""
    
    async def check_coverage(
        self, 
        db: AsyncSession, 
        lat: float, 
        lng: float
    ) -> Optional[Dict]:
        """
        Check if coordinates are within any city coverage area.
        Returns city info if within coverage, None otherwise.
        """
        try:
            # Use PostGIS to check point within polygon
            query = text("""
                SELECT id, name, slug, country_code
                FROM cities 
                WHERE is_active = true 
                AND ST_Within(
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                    coverage_area
                )
                LIMIT 1
            """)
            
            result = await db.execute(query, {"lat": lat, "lng": lng})
            row = result.fetchone()
            
            if row:
                return {
                    "id": row.id,
                    "name": row.name,
                    "slug": row.slug,
                    "country_code": row.country_code
                }
            
            return None
            
        except Exception as e:
            # Fallback: check distance to city centers
            return await self._fallback_coverage_check(db, lat, lng)
    
    async def _fallback_coverage_check(
        self, 
        db: AsyncSession, 
        lat: float, 
        lng: float
    ) -> Optional[Dict]:
        """
        Fallback coverage check using distance calculation.
        Used when PostGIS is not available.
        """
        try:
            # Simple distance check (approximate)
            query = text("""
                SELECT id, name, slug, country_code, lat, lng,
                       (6371 * acos(cos(radians(:lat)) * cos(radians(lat)) * 
                        cos(radians(lng) - radians(:lng)) + 
                        sin(radians(:lat)) * sin(radians(lat)))) AS distance
                FROM cities 
                WHERE is_active = true
                HAVING distance < 50  -- 50km radius
                ORDER BY distance
                LIMIT 1
            """)
            
            result = await db.execute(query, {"lat": lat, "lng": lng})
            row = result.fetchone()
            
            if row:
                return {
                    "id": row.id,
                    "name": row.name,
                    "slug": row.slug,
                    "country_code": row.country_code
                }
            
            return None
            
        except Exception:
            return None
    
    async def get_nearby_listings(
        self,
        db: AsyncSession,
        lat: float,
        lng: float,
        radius_km: int = 10,
        limit: int = 10
    ) -> list:
        """Get nearby listings within radius."""
        try:
            query = text("""
                SELECT l.id, l.name, l.address, l.category,
                       (6371 * acos(cos(radians(:lat)) * cos(radians(l.latitude)) * 
                        cos(radians(l.longitude) - radians(:lng)) + 
                        sin(radians(:lat)) * sin(radians(l.latitude)))) AS distance
                FROM listings l
                WHERE l.moderation_status = 'approved' 
                AND l.is_hidden = false
                AND l.latitude IS NOT NULL 
                AND l.longitude IS NOT NULL
                HAVING distance < :radius
                ORDER BY distance
                LIMIT :limit
            """)
            
            result = await db.execute(query, {
                "lat": lat, 
                "lng": lng, 
                "radius": radius_km,
                "limit": limit
            })
            
            rows = result.fetchall()
            
            return [
                {
                    "id": row.id,
                    "name": row.name,
                    "address": row.address,
                    "category": row.category,
                    "distance_km": round(row.distance, 2)
                }
                for row in rows
            ]
            
        except Exception:
            return []

# Global service instance
geo_service = GeoService()
