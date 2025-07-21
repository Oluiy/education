"""
EduNerve Rate Limiting and DDoS Protection System
Advanced protection against abuse and denial of service attacks
"""

import time
import hashlib
import logging
from typing import Dict, Optional, Tuple, List
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from redis import Redis
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Types of rate limiting"""
    GLOBAL = "global"
    IP = "ip"
    USER = "user"
    ENDPOINT = "endpoint"
    API_KEY = "api_key"

@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests: int
    window: int  # seconds
    burst: int = 0  # burst allowance
    
    def __str__(self):
        return f"{self.requests}/{self.window}s"

class RateLimitConfig:
    """Rate limit configurations for different scenarios"""
    
    # Global limits
    GLOBAL_LIMIT = RateLimit(requests=1000, window=60)  # 1000 req/min globally
    
    # IP-based limits
    IP_STRICT = RateLimit(requests=60, window=60, burst=10)   # 60 req/min per IP
    IP_MODERATE = RateLimit(requests=120, window=60, burst=20) # 120 req/min per IP
    IP_LENIENT = RateLimit(requests=300, window=60, burst=50)  # 300 req/min per IP
    
    # User-based limits
    USER_BASIC = RateLimit(requests=100, window=60, burst=15)    # Basic users
    USER_PREMIUM = RateLimit(requests=500, window=60, burst=50)  # Premium users
    USER_ADMIN = RateLimit(requests=1000, window=60, burst=100)  # Admin users
    
    # Endpoint-specific limits
    AUTH_ENDPOINTS = RateLimit(requests=5, window=300, burst=2)   # 5 auth attempts per 5 min
    UPLOAD_ENDPOINTS = RateLimit(requests=10, window=60, burst=3)  # 10 uploads per min
    SEARCH_ENDPOINTS = RateLimit(requests=30, window=60, burst=10) # 30 searches per min
    API_ENDPOINTS = RateLimit(requests=100, window=60, burst=20)   # General API limits
    
    # API key limits
    API_KEY_BASIC = RateLimit(requests=1000, window=3600)    # 1000 req/hour
    API_KEY_PREMIUM = RateLimit(requests=10000, window=3600) # 10k req/hour
    
    # DDoS protection
    DDOS_DETECTION = RateLimit(requests=500, window=60)  # Trigger DDoS protection
    
    @classmethod
    def get_endpoint_limit(cls, endpoint: str) -> RateLimit:
        """Get rate limit for specific endpoint"""
        endpoint_patterns = {
            "/auth/": cls.AUTH_ENDPOINTS,
            "/login": cls.AUTH_ENDPOINTS,
            "/register": cls.AUTH_ENDPOINTS,
            "/upload": cls.UPLOAD_ENDPOINTS,
            "/search": cls.SEARCH_ENDPOINTS,
        }
        
        for pattern, limit in endpoint_patterns.items():
            if pattern in endpoint:
                return limit
        
        return cls.API_ENDPOINTS

class RedisRateLimiter:
    """Redis-based rate limiter with sliding window"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = None
        self.fallback_storage = {}  # In-memory fallback
        self._connect_redis()
    
    def _connect_redis(self):
        """Connect to Redis with fallback to in-memory storage"""
        try:
            self.redis_client = Redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connected for rate limiting")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed, using in-memory fallback: {e}")
            self.redis_client = None
    
    def _get_key(self, limit_type: RateLimitType, identifier: str, endpoint: str = None) -> str:
        """Generate Redis key for rate limiting"""
        key_parts = ["rate_limit", limit_type.value, identifier]
        if endpoint:
            key_parts.append(hashlib.md5(endpoint.encode()).hexdigest()[:8])
        return ":".join(key_parts)
    
    def _sliding_window_check(self, key: str, limit: RateLimit) -> Tuple[bool, int, int]:
        """
        Sliding window rate limiting implementation
        Returns: (allowed, current_count, reset_time)
        """
        current_time = int(time.time())
        window_start = current_time - limit.window
        
        if self.redis_client:
            try:
                # Use Redis sliding window with sorted set
                pipe = self.redis_client.pipeline()
                
                # Remove old entries
                pipe.zremrangebyscore(key, 0, window_start)
                
                # Count current requests
                pipe.zcard(key)
                
                # Add current request
                pipe.zadd(key, {str(current_time): current_time})
                
                # Set expiry
                pipe.expire(key, limit.window + 10)
                
                results = pipe.execute()
                current_count = results[1] + 1  # +1 for current request
                
                # Check if allowed
                allowed = current_count <= limit.requests + limit.burst
                reset_time = current_time + limit.window
                
                return allowed, current_count, reset_time
                
            except Exception as e:
                logger.error(f"Redis rate limit error: {e}")
                # Fallback to in-memory
                return self._memory_fallback_check(key, limit)
        else:
            return self._memory_fallback_check(key, limit)
    
    def _memory_fallback_check(self, key: str, limit: RateLimit) -> Tuple[bool, int, int]:
        """In-memory fallback rate limiting"""
        current_time = int(time.time())
        
        if key not in self.fallback_storage:
            self.fallback_storage[key] = []
        
        # Clean old entries
        self.fallback_storage[key] = [
            ts for ts in self.fallback_storage[key] 
            if ts > current_time - limit.window
        ]
        
        # Add current request
        self.fallback_storage[key].append(current_time)
        
        current_count = len(self.fallback_storage[key])
        allowed = current_count <= limit.requests + limit.burst
        reset_time = current_time + limit.window
        
        return allowed, current_count, reset_time
    
    def check_rate_limit(
        self, 
        limit_type: RateLimitType,
        identifier: str,
        limit: RateLimit,
        endpoint: str = None
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is within rate limit
        Returns: (allowed, rate_limit_info)
        """
        key = self._get_key(limit_type, identifier, endpoint)
        allowed, current_count, reset_time = self._sliding_window_check(key, limit)
        
        rate_limit_info = {
            "limit": limit.requests,
            "remaining": max(0, limit.requests - current_count),
            "reset": reset_time,
            "window": limit.window
        }
        
        return allowed, rate_limit_info

class DDoSProtection:
    """Advanced DDoS detection and protection"""
    
    def __init__(self, rate_limiter: RedisRateLimiter):
        self.rate_limiter = rate_limiter
        self.blocked_ips = set()
        self.suspicious_ips = set()
    
    def is_suspicious_request(self, request: Request) -> bool:
        """Detect suspicious request patterns"""
        suspicious_patterns = [
            # User agent patterns
            lambda req: not req.headers.get("user-agent"),
            lambda req: len(req.headers.get("user-agent", "")) > 1000,
            lambda req: "bot" in req.headers.get("user-agent", "").lower() and "google" not in req.headers.get("user-agent", "").lower(),
            
            # Request patterns
            lambda req: len(str(req.url)) > 2048,
            lambda req: req.method in ["TRACE", "CONNECT"],
            lambda req: "../../" in str(req.url),
            
            # Header patterns
            lambda req: len(req.headers) > 50,
            lambda req: any(len(v) > 8192 for v in req.headers.values()),
        ]
        
        return any(pattern(request) for pattern in suspicious_patterns)
    
    def check_ddos_protection(self, request: Request) -> Tuple[bool, str]:
        """
        Check for DDoS patterns and block if necessary
        Returns: (allowed, reason)
        """
        client_ip = self._get_client_ip(request)
        
        # Check if IP is already blocked
        if client_ip in self.blocked_ips:
            return False, "IP_BLOCKED"
        
        # Check for suspicious patterns
        if self.is_suspicious_request(request):
            self.suspicious_ips.add(client_ip)
            logger.warning(f"Suspicious request from {client_ip}: {request.url}")
        
        # Check DDoS rate limits
        allowed, rate_info = self.rate_limiter.check_rate_limit(
            RateLimitType.IP,
            client_ip,
            RateLimitConfig.DDOS_DETECTION,
            str(request.url.path)
        )
        
        if not allowed:
            # Block IP temporarily
            self.blocked_ips.add(client_ip)
            logger.warning(f"DDoS protection triggered for {client_ip}")
            
            # TODO: Implement automated IP blocking in firewall/load balancer
            return False, "DDOS_PROTECTION"
        
        return True, "ALLOWED"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP with proxy support"""
        # Check for forwarded IP headers
        forwarded_ips = [
            request.headers.get("x-forwarded-for"),
            request.headers.get("x-real-ip"),
            request.headers.get("cf-connecting-ip"),  # Cloudflare
        ]
        
        for ip_header in forwarded_ips:
            if ip_header:
                # Take first IP if comma-separated
                return ip_header.split(",")[0].strip()
        
        # Fallback to direct IP
        return request.client.host if request.client else "unknown"

class RateLimitMiddleware:
    """FastAPI middleware for rate limiting and DDoS protection"""
    
    def __init__(self):
        self.rate_limiter = RedisRateLimiter()
        self.ddos_protection = DDoSProtection(self.rate_limiter)
        
    async def __call__(self, request: Request, call_next):
        """Rate limiting middleware"""
        try:
            # DDoS protection check
            allowed, reason = self.ddos_protection.check_ddos_protection(request)
            if not allowed:
                return self._create_rate_limit_response(reason, {
                    "limit": 0,
                    "remaining": 0,
                    "reset": int(time.time()) + 3600,
                    "window": 3600
                })
            
            # Get client identifier
            client_ip = self.ddos_protection._get_client_ip(request)
            endpoint = str(request.url.path)
            
            # Check IP-based rate limit
            ip_limit = RateLimitConfig.IP_MODERATE
            allowed, rate_info = self.rate_limiter.check_rate_limit(
                RateLimitType.IP,
                client_ip,
                ip_limit,
                endpoint
            )
            
            if not allowed:
                return self._create_rate_limit_response("IP_RATE_LIMIT", rate_info)
            
            # Check endpoint-specific rate limit
            endpoint_limit = RateLimitConfig.get_endpoint_limit(endpoint)
            allowed, endpoint_rate_info = self.rate_limiter.check_rate_limit(
                RateLimitType.ENDPOINT,
                f"{client_ip}:{endpoint}",
                endpoint_limit,
                endpoint
            )
            
            if not allowed:
                return self._create_rate_limit_response("ENDPOINT_RATE_LIMIT", endpoint_rate_info)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
            response.headers["X-RateLimit-Window"] = str(rate_info["window"])
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Don't block requests if rate limiting fails
            return await call_next(request)
    
    def _create_rate_limit_response(self, reason: str, rate_info: Dict[str, int]):
        """Create rate limit exceeded response"""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": True,
                "message": "Too many requests",
                "reason": reason,
                "retry_after": rate_info.get("reset", int(time.time()) + 60) - int(time.time())
            },
            headers={
                "Retry-After": str(rate_info.get("reset", int(time.time()) + 60) - int(time.time())),
                "X-RateLimit-Limit": str(rate_info.get("limit", 0)),
                "X-RateLimit-Remaining": str(rate_info.get("remaining", 0)),
                "X-RateLimit-Reset": str(rate_info.get("reset", int(time.time()) + 60))
            }
        )

def apply_rate_limiting(app):
    """Apply rate limiting middleware to FastAPI app"""
    logger.info("🛡️ Applying rate limiting and DDoS protection...")
    
    middleware = RateLimitMiddleware()
    app.middleware("http")(middleware)
    
    logger.info("✅ Rate limiting middleware applied")

# User-based rate limiting decorator
def user_rate_limit(user_type: str = "basic"):
    """Decorator for user-based rate limiting"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract current user from kwargs or dependencies
            current_user = kwargs.get('current_user')
            if current_user:
                user_limit = {
                    "basic": RateLimitConfig.USER_BASIC,
                    "premium": RateLimitConfig.USER_PREMIUM,
                    "admin": RateLimitConfig.USER_ADMIN
                }.get(user_type, RateLimitConfig.USER_BASIC)
                
                rate_limiter = RedisRateLimiter()
                allowed, rate_info = rate_limiter.check_rate_limit(
                    RateLimitType.USER,
                    str(current_user.id),
                    user_limit
                )
                
                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="User rate limit exceeded",
                        headers={
                            "Retry-After": str(rate_info["reset"] - int(time.time())),
                            "X-RateLimit-Limit": str(rate_info["limit"]),
                            "X-RateLimit-Remaining": str(rate_info["remaining"])
                        }
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
