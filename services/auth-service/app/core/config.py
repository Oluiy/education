"""
Configuration Settings for Auth Service
Environment variables and application settings
"""

import os
from pydantic import BaseSettings, validator
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "EduNerve Auth Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    REFRESH_SECRET_KEY: Optional[str] = os.getenv("REFRESH_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 1
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/edunerve_auth"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis settings (supports REDIS_URL for Heroku)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Rate limiting
    LOGIN_RATE_LIMIT: int = 5  # requests per minute
    REGISTER_RATE_LIMIT: int = 3  # requests per minute
    PASSWORD_RESET_RATE_LIMIT: int = 3  # requests per hour
    
    # Email settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@edunerve.com")
    
    # File upload settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # External services
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    NOTIFICATION_SERVICE_URL: str = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8003")
    
    # CORS settings (can override via ALLOWED_ORIGINS env: comma-separated)
    ALLOWED_ORIGINS: list = []

    @validator("ALLOWED_ORIGINS", pre=True, always=True)
    def build_allowed_origins(cls, v):  # type: ignore
        env_val = os.getenv("ALLOWED_ORIGINS")
        if env_val:
            return [o.strip() for o in env_val.split(",") if o.strip()]
        # default fallback
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "https://edunerve.com",
            "https://app.edunerve.com"
        ]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Session settings
    SESSION_TIMEOUT_HOURS: int = 24
    MAX_ACTIVE_SESSIONS: int = 5
    
    # Password policy
    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 128
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_NUMBERS: bool = True
    REQUIRE_SPECIAL_CHARS: bool = True
    PASSWORD_HISTORY_COUNT: int = 5
    
    # Account lockout
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    
    # Two-factor authentication
    TOTP_ISSUER: str = "EduNerve"
    BACKUP_CODES_COUNT: int = 10
    
    # Monitoring and health checks
    HEALTH_CHECK_TIMEOUT: int = 30
    METRICS_ENABLED: bool = True
    
    # Development settings
    AUTO_RELOAD: bool = False
    SHOW_DOCS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Validation
def validate_settings():
    """Validate critical settings"""
    errors = []
    
    if settings.SECRET_KEY == "your-secret-key-change-in-production":
        errors.append("SECRET_KEY must be changed in production")
    
    if len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY should be at least 32 characters long")
    
    if not settings.DATABASE_URL.startswith(("postgresql://", "sqlite:///")):
        errors.append("DATABASE_URL must be a valid database connection string")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

# Environment-specific configurations
def get_environment() -> str:
    """Get current environment"""
    return os.getenv("ENVIRONMENT", "development")

def is_production() -> bool:
    """Check if running in production"""
    return get_environment().lower() == "production"

def is_development() -> bool:
    """Check if running in development"""
    return get_environment().lower() == "development"

def is_testing() -> bool:
    """Check if running in testing"""
    return get_environment().lower() == "testing"

# Database configuration
def get_database_config():
    """Get database configuration"""
    return {
        "url": settings.DATABASE_URL,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "echo": is_development(),  # Enable SQL logging in development
    }

# Redis configuration
def get_redis_config():
    """Get Redis configuration"""
    if settings.REDIS_URL:
        # Parse redis://[:password@]host:port/db
        # Basic manual parse to avoid adding external deps
        import re
        pattern = r"redis://(?:(?P<pw>[^:@]+)@)?(?P<host>[^:/]+)(?::(?P<port>\d+))?(?:/(?P<db>\d+))?"
        match = re.match(pattern, settings.REDIS_URL)
        if match:
            gd = match.groupdict()
            return {
                "host": gd.get("host", settings.REDIS_HOST),
                "port": int(gd.get("port") or settings.REDIS_PORT),
                "db": int(gd.get("db") or settings.REDIS_DB),
                "password": gd.get("pw") or settings.REDIS_PASSWORD,
                "decode_responses": True,
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
                "retry_on_timeout": True,
            }
    config = {
        "host": settings.REDIS_HOST,
        "port": settings.REDIS_PORT,
        "db": settings.REDIS_DB,
        "decode_responses": True,
        "socket_timeout": 5,
        "socket_connect_timeout": 5,
        "retry_on_timeout": True,
    }
    if settings.REDIS_PASSWORD:
        config["password"] = settings.REDIS_PASSWORD
    return config

# CORS configuration
def get_cors_config():
    """Get CORS configuration"""
    return {
        "allow_origins": settings.ALLOWED_ORIGINS,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
    }

# Logging configuration
def get_logging_config():
    """Get logging configuration"""
    return {
        "level": settings.LOG_LEVEL,
        "format": settings.LOG_FORMAT,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "auth-service.log",
                "level": "INFO",
                "formatter": "default",
            }
        } if is_production() else {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
            }
        }
    }

# Security headers configuration
def get_security_headers():
    """Get security headers"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

# Rate limiting configuration
def get_rate_limit_config():
    """Get rate limiting configuration"""
    return {
        "login": {
            "limit": settings.LOGIN_RATE_LIMIT,
            "window": 60,  # 1 minute
        },
        "register": {
            "limit": settings.REGISTER_RATE_LIMIT,
            "window": 60,  # 1 minute
        },
        "password_reset": {
            "limit": settings.PASSWORD_RESET_RATE_LIMIT,
            "window": 3600,  # 1 hour
        },
        "general": {
            "limit": 100,
            "window": 60,  # 1 minute
        }
    }

# Feature flags
FEATURE_FLAGS = {
    "email_verification_required": True,
    "two_factor_auth_enabled": False,
    "social_login_enabled": False,
    "password_strength_meter": True,
    "account_lockout_enabled": True,
    "session_management": True,
    "audit_logging": True,
    "metrics_collection": True,
}

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURE_FLAGS.get(feature_name, False)
