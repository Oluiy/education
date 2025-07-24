"""
EduNerve Security Configuration - Centralized Security Management
Cryptographically secure secret generation and validation
"""

import os
import secrets
import hashlib
from typing import Dict, Optional
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class SecurityConfig:
    """Centralized security configuration with secure defaults"""
    
    def __init__(self):
        self._validate_environment()
        self._setup_secrets()
    
    def _validate_environment(self):
        """Validate that we're not using default/weak secrets"""
        weak_secrets = [
            "your-super-secret-jwt-key-change-this-in-production",
            "your-fallback-secret-key-change-this",
            "your-secret-key-here",
            "secret",
            "password",
            "admin"
        ]
        
        jwt_secret = os.getenv("JWT_SECRET_KEY", "")
        if jwt_secret in weak_secrets or len(jwt_secret) < 32:
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("🚨 CRITICAL: Weak JWT secret detected in production!")
            logger.warning("⚠️ Using weak JWT secret - ONLY acceptable in development")
    
    def _setup_secrets(self):
        """Setup cryptographically secure secrets"""
        self.jwt_secret_key = self._get_or_generate_secret("JWT_SECRET_KEY", 64)
        self.encryption_key = self._get_or_generate_secret("ENCRYPTION_KEY", 32)
        self.session_secret = self._get_or_generate_secret("SESSION_SECRET", 32)
        self.csrf_secret = self._get_or_generate_secret("CSRF_SECRET", 32)
    
    def _get_or_generate_secret(self, env_var: str, length: int) -> str:
        """Get secret from environment or generate secure one"""
        secret = os.getenv(env_var)
        
        if not secret or len(secret) < length:
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError(f"🚨 {env_var} must be set in production!")
            
            # Generate secure secret for development
            secure_secret = secrets.token_urlsafe(length)
            logger.warning(f"🔑 Generated secure {env_var} for development: {secure_secret[:16]}...")
            return secure_secret
        
        return secret
    
    def get_jwt_config(self) -> Dict[str, str]:
        """Get JWT configuration"""
        return {
            "secret_key": self.jwt_secret_key,
            "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
            "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            "refresh_token_expire_days": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        }
    
    def get_encryption_key(self) -> bytes:
        """Get encryption key for sensitive data"""
        return self.encryption_key.encode()
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> str:
        """Secure password hashing with salt"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA-256
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                     password.encode('utf-8'), 
                                     salt.encode('utf-8'), 
                                     100000)  # 100k iterations
        return f"{salt}${pwdhash.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = hashed.split('$')
            pwdhash = hashlib.pbkdf2_hmac('sha256',
                                         password.encode('utf-8'),
                                         salt.encode('utf-8'),
                                         100000)
            return pwdhash.hex() == stored_hash
        except ValueError:
            return False

# Global security instance
security_config = SecurityConfig()

# Export configuration functions
def get_jwt_secret() -> str:
    """Get JWT secret key"""
    return security_config.jwt_secret_key

def get_jwt_config() -> Dict[str, str]:
    """Get complete JWT configuration"""
    return security_config.get_jwt_config()

def get_encryption_key() -> bytes:
    """Get encryption key"""
    return security_config.get_encryption_key()

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(length)

def get_security_headers() -> Dict[str, str]:
    """Get security headers for HTTP responses"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()"
    }
