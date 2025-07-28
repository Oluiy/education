"""
Caching Utilities
Redis-based caching with advanced features and fallback mechanisms
"""

import json
import pickle
import hashlib
import logging
from typing import Any, Optional, List, Dict, Callable, Union
from functools import wraps
import time
import redis
from ..core.config import settings

logger = logging.getLogger(__name__)

# Redis client setup
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=False,  # We'll handle encoding ourselves
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("Redis cache client initialized successfully")
except Exception as e:
    logger.warning(f"Redis not available: {e}. Caching will be disabled.")
    redis_client = None
    REDIS_AVAILABLE = False


class CacheManager:
    """Advanced cache management with Redis backend"""
    
    def __init__(self, redis_client=redis_client, default_ttl=3600):
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.available = REDIS_AVAILABLE
        
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            # Try JSON first for simple types
            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(value, default=str).encode('utf-8')
            else:
                # Fall back to pickle for complex objects
                return pickle.dumps(value)
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            try:
                # Fall back to pickle
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"Deserialization failed: {e}")
                return None
    
    def _generate_key(self, key: str, prefix: str = "edunerve") -> str:
        """Generate namespaced cache key"""
        return f"{prefix}:{settings.SERVICE_NAME}:{key}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        if not self.available:
            return default
        
        try:
            cache_key = self._generate_key(key)
            data = self.redis.get(cache_key)
            
            if data is None:
                return default
            
            return self._deserialize(data)
            
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.available:
            return False
        
        try:
            cache_key = self._generate_key(key)
            serialized = self._serialize(value)
            
            if ttl is None:
                ttl = self.default_ttl
            
            return self.redis.setex(cache_key, ttl, serialized)
            
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.available:
            return False
        
        try:
            cache_key = self._generate_key(key)
            return bool(self.redis.delete(cache_key))
            
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.available:
            return 0
        
        try:
            cache_pattern = self._generate_key(pattern)
            keys = self.redis.keys(cache_pattern)
            
            if keys:
                return self.redis.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Cache delete pattern failed for {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.available:
            return False
        
        try:
            cache_key = self._generate_key(key)
            return bool(self.redis.exists(cache_key))
            
        except Exception as e:
            logger.error(f"Cache exists check failed for key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key"""
        if not self.available:
            return False
        
        try:
            cache_key = self._generate_key(key)
            return bool(self.redis.expire(cache_key, ttl))
            
        except Exception as e:
            logger.error(f"Cache expire failed for key {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get time to live for key"""
        if not self.available:
            return -1
        
        try:
            cache_key = self._generate_key(key)
            return self.redis.ttl(cache_key)
            
        except Exception as e:
            logger.error(f"Cache TTL check failed for key {key}: {e}")
            return -1
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value"""
        if not self.available:
            return None
        
        try:
            cache_key = self._generate_key(key)
            return self.redis.incr(cache_key, amount)
            
        except Exception as e:
            logger.error(f"Cache increment failed for key {key}: {e}")
            return None
    
    def get_multi(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        if not self.available:
            return {}
        
        try:
            cache_keys = [self._generate_key(key) for key in keys]
            values = self.redis.mget(cache_keys)
            
            result = {}
            for i, value in enumerate(values):
                if value is not None:
                    result[keys[i]] = self._deserialize(value)
            
            return result
            
        except Exception as e:
            logger.error(f"Cache get_multi failed: {e}")
            return {}
    
    def set_multi(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache"""
        if not self.available:
            return False
        
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            pipeline = self.redis.pipeline()
            
            for key, value in mapping.items():
                cache_key = self._generate_key(key)
                serialized = self._serialize(value)
                pipeline.setex(cache_key, ttl, serialized)
            
            pipeline.execute()
            return True
            
        except Exception as e:
            logger.error(f"Cache set_multi failed: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache entries for this service"""
        if not self.available:
            return False
        
        try:
            pattern = self._generate_key("*")
            keys = self.redis.keys(pattern)
            
            if keys:
                self.redis.delete(*keys)
            
            logger.info(f"Cleared {len(keys)} cache entries")
            return True
            
        except Exception as e:
            logger.error(f"Cache clear_all failed: {e}")
            return False


# Global cache manager instance
cache = CacheManager()


def cache_result(
    key_template: str = None,
    ttl: int = 3600,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results
    
    Args:
        key_template: Template for cache key (can use {arg_name} placeholders)
        ttl: Time to live in seconds
        key_builder: Custom function to build cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache.available:
                return func(*args, **kwargs)
            
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            elif key_template:
                # Get function signature for argument mapping
                import inspect
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                try:
                    cache_key = key_template.format(**bound_args.arguments)
                except KeyError as e:
                    logger.warning(f"Cache key template missing argument: {e}")
                    cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            else:
                # Default key based on function name and arguments
                args_hash = hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()
                cache_key = f"{func.__name__}:{args_hash}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)
            
            if result is not None:
                cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key: str) -> bool:
    """Invalidate specific cache key"""
    return cache.delete(key)


def invalidate_cache_pattern(pattern: str) -> int:
    """Invalidate all cache keys matching pattern"""
    return cache.delete_pattern(pattern)


def warm_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Warm cache with a value"""
    return cache.set(key, value, ttl)


class CacheStats:
    """Cache statistics and monitoring"""
    
    @staticmethod
    def get_info() -> Dict[str, Any]:
        """Get Redis cache information"""
        if not cache.available:
            return {"status": "unavailable"}
        
        try:
            info = cache.redis.info()
            return {
                "status": "available",
                "memory_used": info.get("used_memory_human"),
                "memory_peak": info.get("used_memory_peak_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds")
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    def get_hit_ratio() -> float:
        """Calculate cache hit ratio"""
        if not cache.available:
            return 0.0
        
        try:
            info = cache.redis.info()
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            
            if hits + misses == 0:
                return 0.0
            
            return hits / (hits + misses)
        except Exception:
            return 0.0
    
    @staticmethod
    def get_service_keys_count() -> int:
        """Get count of keys for this service"""
        if not cache.available:
            return 0
        
        try:
            pattern = cache._generate_key("*")
            return len(cache.redis.keys(pattern))
        except Exception:
            return 0


# Specific cache functions for common patterns
def cache_user_data(user_id: int, data: Dict[str, Any], ttl: int = 1800) -> bool:
    """Cache user-specific data"""
    return cache.set(f"user:{user_id}:data", data, ttl)


def get_cached_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """Get cached user data"""
    return cache.get(f"user:{user_id}:data")


def cache_quiz_results(quiz_id: int, user_id: int, results: Dict[str, Any]) -> bool:
    """Cache quiz results"""
    return cache.set(f"quiz:{quiz_id}:user:{user_id}:results", results, 7200)  # 2 hours


def get_cached_quiz_results(quiz_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Get cached quiz results"""
    return cache.get(f"quiz:{quiz_id}:user:{user_id}:results")


def cache_course_progress(course_id: int, user_id: int, progress: Dict[str, Any]) -> bool:
    """Cache course progress"""
    return cache.set(f"progress:course:{course_id}:user:{user_id}", progress, 3600)


def get_cached_course_progress(course_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Get cached course progress"""
    return cache.get(f"progress:course:{course_id}:user:{user_id}")


# Export commonly used functions
__all__ = [
    "cache",
    "cache_result", 
    "invalidate_cache",
    "invalidate_cache_pattern",
    "warm_cache",
    "CacheStats",
    "cache_user_data",
    "get_cached_user_data",
    "cache_quiz_results",
    "get_cached_quiz_results",
    "cache_course_progress",
    "get_cached_course_progress"
]
