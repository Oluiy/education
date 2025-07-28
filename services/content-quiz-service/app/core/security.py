"""
Security Configuration and Utilities
Production-grade security implementation for content-quiz service
"""

import os
import jwt
import bcrypt
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from passlib.hash import bcrypt
import redis
import time
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

# Redis client for token blacklisting
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
        socket_timeout=5
    )
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None


class SecurityConfig:
    """Central security configuration and utilities"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)  # JWT ID for blacklisting
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token creation failed"
            )
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Refresh token creation failed"
            )
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check if token is blacklisted
            jti = payload.get("jti")
            if jti and self.is_token_blacklisted(jti):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def blacklist_token(self, token: str) -> bool:
        """Add token to blacklist"""
        if not redis_client:
            logger.warning("Redis not available for token blacklisting")
            return False
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            exp = payload.get("exp")
            
            if jti and exp:
                # Set expiration time for blacklist entry
                ttl = exp - int(time.time())
                if ttl > 0:
                    redis_client.setex(f"blacklist:{jti}", ttl, "1")
                return True
        except Exception as e:
            logger.error(f"Token blacklisting failed: {e}")
        
        return False
    
    def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        if not redis_client:
            return False
        
        try:
            return redis_client.exists(f"blacklist:{jti}")
        except Exception as e:
            logger.error(f"Blacklist check failed: {e}")
            return False


class PasswordValidator:
    """Advanced password validation and security"""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength with detailed feedback"""
        issues = []
        score = 0
        
        # Length check
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        else:
            score += 1
        
        # Character variety checks
        if not any(c.islower() for c in password):
            issues.append("Password must contain lowercase letters")
        else:
            score += 1
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain uppercase letters")
        else:
            score += 1
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain numbers")
        else:
            score += 1
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Password must contain special characters")
        else:
            score += 1
        
        # Common password check
        common_passwords = [
            "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey"
        ]
        if password.lower() in common_passwords:
            issues.append("Password is too common")
            score -= 2
        
        # Sequential characters check
        if any(ord(password[i]) == ord(password[i+1]) - 1 and ord(password[i+1]) == ord(password[i+2]) - 1 
               for i in range(len(password) - 2)):
            issues.append("Password contains sequential characters")
            score -= 1
        
        strength_levels = {
            0: "Very Weak",
            1: "Weak", 
            2: "Fair",
            3: "Good",
            4: "Strong",
            5: "Very Strong"
        }
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": max(0, score),
            "strength": strength_levels.get(max(0, score), "Unknown")
        }
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt"""
        try:
            # Validate password first
            validation = PasswordValidator.validate_password_strength(password)
            if not validation["valid"]:
                raise ValueError(f"Password validation failed: {', '.join(validation['issues'])}")
            
            # Generate salt and hash
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password processing failed"
            )
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False


class RateLimiter:
    """Redis-based rate limiting"""
    
    def __init__(self, redis_client=redis_client):
        self.redis = redis_client
    
    def is_rate_limited(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request should be rate limited"""
        if not self.redis:
            return False
        
        try:
            current = self.redis.get(key)
            if current is None:
                # First request
                self.redis.setex(key, window, 1)
                return False
            
            if int(current) >= limit:
                return True
            
            # Increment counter
            self.redis.incr(key)
            return False
            
        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            return False
    
    def get_rate_limit_info(self, key: str, window: int = 60) -> Dict[str, int]:
        """Get current rate limit status"""
        if not self.redis:
            return {"current": 0, "ttl": 0}
        
        try:
            current = self.redis.get(key) or 0
            ttl = self.redis.ttl(key) or 0
            return {"current": int(current), "ttl": int(ttl)}
        except Exception as e:
            logger.error(f"Rate limit info failed: {e}")
            return {"current": 0, "ttl": 0}


class SecurityHeaders:
    """Security header management"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get comprehensive security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "font-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=()"
            )
        }


class ContentValidator:
    """Content security and validation"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for security"""
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        dangerous_chars = '<>:"/\\|?*'
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
        """Validate file type against allowed extensions"""
        if not filename:
            return False
        
        ext = os.path.splitext(filename.lower())[1]
        return ext in [t.lower() for t in allowed_types]
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Generate secure unique filename"""
        timestamp = str(int(time.time()))
        random_part = secrets.token_urlsafe(8)
        sanitized = ContentValidator.sanitize_filename(original_filename)
        name, ext = os.path.splitext(sanitized)
        
        return f"{timestamp}_{random_part}_{name[:50]}{ext}"


# Global security instance
security_config = SecurityConfig()
password_validator = PasswordValidator()
rate_limiter = RateLimiter()


# Dependency functions
async def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Extract and validate current user token"""
    token = credentials.credentials
    payload = security_config.verify_token(token)
    return payload


async def require_admin_role(token_data: Dict[str, Any] = Depends(get_current_user_token)) -> Dict[str, Any]:
    """Require admin role for endpoint access"""
    user_role = token_data.get("role", "")
    if user_role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return token_data


async def rate_limit_check(request: Request, limit: int = 100, window: int = 60):
    """Rate limiting dependency"""
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"
    
    if rate_limiter.is_rate_limited(key, limit, window):
        rate_info = rate_limiter.get_rate_limit_info(key, window)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {rate_info['ttl']} seconds",
            headers={
                "Retry-After": str(rate_info["ttl"]),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(max(0, limit - rate_info["current"])),
                "X-RateLimit-Reset": str(int(time.time()) + rate_info["ttl"])
            }
        )
