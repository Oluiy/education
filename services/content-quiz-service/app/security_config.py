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
                raise ValueError(f"🚨 CRITICAL: {env_var} not set in production!")
            
            # Generate secure secret for development
            secret = secrets.token_urlsafe(length)
            logger.warning(f"🔐 Generated secure {env_var} for development")
        
        return secret
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def hash_secret(self, secret: str) -> str:
        """Hash secret using SHA-256"""
        return hashlib.sha256(secret.encode()).hexdigest()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        fernet = Fernet(self.encryption_key)
        return fernet.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        fernet = Fernet(self.encryption_key)
        return fernet.decrypt(encrypted_data.encode()).decode()

# Global security configuration instance
security_config = SecurityConfig()

def get_jwt_config() -> Dict[str, any]:
    """Get JWT configuration with secure defaults"""
    return {
        "secret_key": security_config.jwt_secret_key,
        "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
        "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        "refresh_token_expire_days": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        "issuer": os.getenv("JWT_ISSUER", "edunerve-content"),
        "audience": os.getenv("JWT_AUDIENCE", "edunerve-services")
    }

def get_security_headers() -> Dict[str, str]:
    """Get security headers for HTTP responses"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY", 
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
    }

def is_production() -> bool:
    """Check if running in production environment"""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"
