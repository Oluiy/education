"""
Security Configuration and Utilities for Auth Service
JWT token handling, password hashing, and security utilities
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return {}

def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    
    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.REFRESH_SECRET_KEY or settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_token_signature(token: str) -> bool:
    """Verify token signature without decoding"""
    try:
        jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False}
        )
        return True
    except jwt.PyJWTError:
        return False

def extract_token_payload(token: str, verify_expiration: bool = True) -> Optional[Dict[str, Any]]:
    """Extract payload from token with optional expiration verification"""
    try:
        options = {"verify_exp": verify_expiration}
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options=options
        )
        return payload
    except jwt.PyJWTError:
        return None

def generate_password_reset_token(user_id: int, email: str) -> str:
    """Generate password reset token"""
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": "password_reset",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify password reset token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "password_reset":
            return None
            
        return payload
    except jwt.PyJWTError:
        return None

def generate_email_verification_token(user_id: int, email: str) -> str:
    """Generate email verification token"""
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": "email_verification",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_email_verification_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify email verification token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "email_verification":
            return None
            
        return payload
    except jwt.PyJWTError:
        return None

class PasswordValidator:
    """Password strength validator"""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength and return detailed feedback"""
        errors = []
        score = 0
        
        # Length check
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        else:
            score += 1
            
        if len(password) >= 12:
            score += 1
        
        # Character type checks
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not has_upper:
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1
            
        if not has_lower:
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1
            
        if not has_digit:
            errors.append("Password must contain at least one number")
        else:
            score += 1
            
        if not has_special:
            errors.append("Password must contain at least one special character")
        else:
            score += 1
        
        # Common password check (basic)
        common_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "1234567890"
        ]
        
        if password.lower() in common_passwords:
            errors.append("Password is too common")
            score = max(0, score - 2)
        
        # Calculate strength
        if score >= 5:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "score": score,
            "strength": strength,
            "suggestions": generate_password_suggestions(has_upper, has_lower, has_digit, has_special)
        }

def generate_password_suggestions(has_upper: bool, has_lower: bool, has_digit: bool, has_special: bool) -> List[str]:
    """Generate password improvement suggestions"""
    suggestions = []
    
    if not has_upper:
        suggestions.append("Add uppercase letters (A-Z)")
    if not has_lower:
        suggestions.append("Add lowercase letters (a-z)")
    if not has_digit:
        suggestions.append("Add numbers (0-9)")
    if not has_special:
        suggestions.append("Add special characters (!@#$%^&*)")
    
    if len(suggestions) == 0:
        suggestions.append("Consider making your password longer for better security")
    
    return suggestions

def check_password_history(user_id: int, new_password: str, password_history: List[str]) -> bool:
    """Check if password was used recently"""
    for old_password_hash in password_history:
        if verify_password(new_password, old_password_hash):
            return False  # Password was used before
    return True  # Password is new

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    import secrets
    return secrets.token_urlsafe(length)

def constant_time_compare(val1: str, val2: str) -> bool:
    """Constant time string comparison to prevent timing attacks"""
    import hmac
    return hmac.compare_digest(val1, val2)

# Rate limiting utilities
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        """Check if request is allowed within rate limit"""
        try:
            current_count = self.redis.get(key)
            
            if current_count is None:
                # First request in window
                self.redis.setex(key, window_seconds, 1)
                return True
            
            current_count = int(current_count)
            if current_count >= limit:
                return False
            
            # Increment counter
            self.redis.incr(key)
            return True
            
        except Exception:
            # If Redis is down, allow the request
            return True
    
    def get_remaining(self, key: str, limit: int) -> int:
        """Get remaining requests in current window"""
        try:
            current_count = self.redis.get(key)
            if current_count is None:
                return limit
            return max(0, limit - int(current_count))
        except Exception:
            return limit
    
    def reset_counter(self, key: str) -> None:
        """Reset rate limit counter"""
        try:
            self.redis.delete(key)
        except Exception:
            pass
