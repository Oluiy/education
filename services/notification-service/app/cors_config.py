"""
EduNerve CORS Security Configuration
Secure Cross-Origin Resource Sharing configuration with environment-specific settings
"""

import os
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class CORSConfig:
    """Secure CORS configuration with environment-specific settings"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate CORS configuration for security"""
        cors_origins = os.getenv("CORS_ORIGINS", "")
        
        if self.environment == "production":
            if "*" in cors_origins:
                raise ValueError("🚨 CRITICAL: Wildcard CORS not allowed in production!")
            if not cors_origins:
                raise ValueError("🚨 CRITICAL: CORS_ORIGINS must be specified in production!")
        
        if "*" in cors_origins and self.environment != "development":
            logger.warning("⚠️ Wildcard CORS detected - security risk!")
    
    def get_allowed_origins(self) -> List[str]:
        """Get allowed origins based on environment"""
        cors_origins = os.getenv("CORS_ORIGINS", "")
        
        if self.environment == "development":
            # Allow common development origins
            default_origins = [
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001"
            ]
            
            if cors_origins:
                custom_origins = [origin.strip() for origin in cors_origins.split(",")]
                return list(set(default_origins + custom_origins))
            return default_origins
        
        elif self.environment == "staging":
            # Staging specific origins
            staging_origins = [
                "https://staging.edunerve.com",
                "https://staging-api.edunerve.com"
            ]
            
            if cors_origins:
                custom_origins = [origin.strip() for origin in cors_origins.split(",")]
                return staging_origins + custom_origins
            return staging_origins
        
        elif self.environment == "production":
            # Production - must be explicitly configured
            if not cors_origins:
                raise ValueError("CORS_ORIGINS must be set in production")
            
            production_origins = [origin.strip() for origin in cors_origins.split(",")]
            
            # Validate production origins
            for origin in production_origins:
                if not origin.startswith(("https://", "http://localhost")):
                    logger.warning(f"⚠️ Non-HTTPS origin in production: {origin}")
            
            return production_origins
        
        else:
            # Custom environment
            if cors_origins:
                return [origin.strip() for origin in cors_origins.split(",")]
            return ["http://localhost:3000"]
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get complete CORS configuration"""
        allowed_origins = self.get_allowed_origins()
        
        config = {
            "allow_origins": allowed_origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": [
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "X-CSRF-Token",
                "X-Request-ID"
            ],
            "expose_headers": [
                "X-Request-ID", 
                "X-Rate-Limit-Remaining",
                "X-Rate-Limit-Reset"
            ],
            "max_age": 600  # 10 minutes
        }
        
        # Log CORS configuration for security audit
        logger.info(f"🔒 CORS configured for {self.environment}")
        logger.info(f"   Allowed origins: {len(allowed_origins)} origins")
        if self.environment == "development":
            logger.info(f"   Origins: {allowed_origins}")
        
        return config
    
    def apply_cors_middleware(self, app):
        """Apply CORS middleware to FastAPI app"""
        cors_config = self.get_cors_config()
        
        app.add_middleware(
            CORSMiddleware,
            **cors_config
        )
        
        logger.info("✅ CORS security middleware applied")


# Global CORS configuration
cors_config = CORSConfig()

# Export functions
def get_cors_config() -> Dict[str, Any]:
    """Get CORS configuration"""
    return cors_config.get_cors_config()

def apply_secure_cors(app):
    """Apply secure CORS to FastAPI app"""
    return cors_config.apply_cors_middleware(app)
