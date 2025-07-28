"""
Content & Quiz Service Configuration
Production-ready settings with security hardening
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import secrets


class Settings(BaseSettings):
    """Production configuration settings"""
    
    # Basic service settings
    SERVICE_NAME: str = "content-quiz-service"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8002, env="PORT")
    
    # Security settings
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Database configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    
    # Redis configuration
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=1, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # CORS and security
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "edunerve.com", "*.edunerve.com"],
        env="ALLOWED_HOSTS"
    )
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001", 
            "https://edunerve.com",
            "https://app.edunerve.com"
        ],
        env="CORS_ORIGINS"
    )
    
    # External service URLs
    AUTH_SERVICE_URL: str = Field(default="http://localhost:8001", env="AUTH_SERVICE_URL")
    NOTIFICATION_SERVICE_URL: str = Field(default="http://localhost:8003", env="NOTIFICATION_SERVICE_URL")
    FILE_STORAGE_SERVICE_URL: str = Field(default="http://localhost:8004", env="FILE_STORAGE_SERVICE_URL")
    
    # Content and file settings
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".mp4", ".mp3"],
        env="ALLOWED_FILE_TYPES"
    )
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    
    # AI and OpenAI settings
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    UPLOAD_RATE_LIMIT: int = Field(default=10, env="UPLOAD_RATE_LIMIT")
    QUIZ_GENERATION_RATE_LIMIT: int = Field(default=5, env="QUIZ_GENERATION_RATE_LIMIT")
    
    # Pagination settings
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")
    
    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Quiz and content settings
    DEFAULT_QUIZ_TIME_LIMIT: int = Field(default=3600, env="DEFAULT_QUIZ_TIME_LIMIT")  # 1 hour
    MAX_QUIZ_QUESTIONS: int = Field(default=100, env="MAX_QUIZ_QUESTIONS")
    MIN_QUIZ_QUESTIONS: int = Field(default=5, env="MIN_QUIZ_QUESTIONS")
    
    # Content validation
    MIN_LESSON_CONTENT_LENGTH: int = Field(default=100, env="MIN_LESSON_CONTENT_LENGTH")
    MAX_LESSON_CONTENT_LENGTH: int = Field(default=50000, env="MAX_LESSON_CONTENT_LENGTH")
    
    # Performance settings
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    QUERY_CACHE_SIZE: int = Field(default=1000, env="QUERY_CACHE_SIZE")
    
    # Monitoring and health checks
    HEALTH_CHECK_TIMEOUT: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")
    
    @validator("CORS_ORIGINS", "ALLOWED_HOSTS", pre=True)
    def parse_comma_separated_list(cls, v):
        """Parse comma-separated string into list"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def parse_file_types(cls, v):
        """Parse comma-separated file types"""
        if isinstance(v, str):
            types = [item.strip() for item in v.split(",") if item.strip()]
            # Ensure all types start with a dot
            return [t if t.startswith('.') else f'.{t}' for t in types]
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Validate secret key strength"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v or not v.startswith(('postgresql://', 'postgresql+psycopg2://', 'sqlite:///')):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL or SQLite URL")
        return v
    
    @property
    def redis_dsn(self) -> str:
        """Build Redis DSN"""
        if self.REDIS_URL:
            return self.REDIS_URL
        
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return not self.DEBUG and os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Production configuration validation
def validate_production_config():
    """Validate configuration for production deployment"""
    errors = []
    
    if settings.DEBUG:
        errors.append("DEBUG should be False in production")
    
    if settings.SECRET_KEY == "your-secret-key-here":
        errors.append("SECRET_KEY must be changed from default value")
    
    if not settings.DATABASE_URL or "localhost" in settings.DATABASE_URL:
        errors.append("DATABASE_URL should not use localhost in production")
    
    if "localhost" in settings.REDIS_HOST and settings.is_production:
        errors.append("REDIS_HOST should not be localhost in production")
    
    if not settings.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required for AI features")
    
    if errors:
        raise ValueError(f"Production configuration errors: {'; '.join(errors)}")
    
    return True


# Environment-specific configurations
class DevelopmentConfig(Settings):
    """Development-specific configuration"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    CORS_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 1000


class TestingConfig(Settings):
    """Testing-specific configuration"""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_HOST: str = "localhost"
    RATE_LIMIT_PER_MINUTE: int = 10000


class ProductionConfig(Settings):
    """Production-specific configuration"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        validate_production_config()


def get_settings() -> Settings:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "development":
        return DevelopmentConfig()
    elif env == "testing":
        return TestingConfig()
    elif env == "production":
        return ProductionConfig()
    else:
        return Settings()
