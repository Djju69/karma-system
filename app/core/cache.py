"""
Redis cache management for Karma System.
"""
import json
import hashlib
from typing import Any, Optional, Dict, List
import redis.asyncio as redis
from redis.exceptions import RedisError
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Redis cache service with fallback."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.connected = False
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            self.connected = True
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.connected or not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache get error for key {key}: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL."""
        if not self.connected or not self.redis:
            return False
        
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            await self.redis.setex(key, ttl, serialized)
            return True
        except (RedisError, TypeError) as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.connected or not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except RedisError as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> bool:
        """Delete keys matching pattern."""
        if not self.connected or not self.redis:
            return False
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return True
        except RedisError as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return False
    
    async def publish(self, channel: str, message: str) -> bool:
        """Publish message to channel."""
        if not self.connected or not self.redis:
            return False
        
        try:
            await self.redis.publish(channel, message)
            return True
        except RedisError as e:
            logger.error(f"Cache publish error for channel {channel}: {e}")
            return False
    
    async def invalidate_city_cache(self, city_id: int):
        """Invalidate catalog cache for city with fallback."""
        try:
            # Try PUB/SUB first
            success = await self.publish(f"cache_invalidate:{city_id}", "1")
            if not success:
                # Fallback: direct deletion
                pattern = f"catalog:{city_id}:*"
                await self.delete_pattern(pattern)
                logger.info(f"Fallback cache invalidation for city {city_id}")
        except Exception as e:
            logger.error(f"Cache invalidation error for city {city_id}: {e}")
    
    def make_filters_hash(self, filters: Optional[Dict] = None) -> str:
        """Generate hash for filters to use in cache key."""
        if not filters:
            return "none"
        
        filters_str = json.dumps(filters, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(filters_str.encode()).hexdigest()[:8]
    
    def make_catalog_key(self, city_id: int, category: str, page: int, filters: Optional[Dict] = None) -> str:
        """Generate catalog cache key."""
        filters_hash = self.make_filters_hash(filters)
        return f"catalog:{city_id}:{category}:{page}:{filters_hash}"

# Global cache instance
cache_service: Optional[CacheService] = None

async def get_cache() -> CacheService:
    """Get cache service instance."""
    global cache_service
    if cache_service is None:
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        cache_service = CacheService(redis_url)
        await cache_service.connect()
    return cache_service
