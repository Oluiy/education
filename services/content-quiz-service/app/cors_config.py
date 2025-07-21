"""
EduNerve Content Service - CORS Security Configuration
Environment-aware CORS settings with production security
"""

import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

class CORSConfig:
    """Secure CORS configuration based on environment"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.allowed_origins = self._get_allowed_origins()
        self.allowed_methods = self._get_allowed_methods()
        self.allowed_headers = self._get_allowed_headers()
        self.expose_headers = self._get_expose_headers()
        self.allow_credentials = self._get_allow_credentials()
        self.max_age = self._get_max_age()
    
    def _get_allowed_origins(self) -> List[str]:
        """Get allowed origins based on environment"""
        if self.environment == "production":
            # Production: Only specific domains
            origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
            origins = [origin.strip() for origin in origins if origin.strip()]
            
            if not origins:
                logger.error("🚨 CRITICAL: No ALLOWED_ORIGINS set in production!")
                raise ValueError("ALLOWED_ORIGINS must be set in production")
            
            # Validate origins
            for origin in origins:
                if "*" in origin and self.environment == "production":
                    logger.error(f"🚨 CRITICAL: Wildcard origin not allowed in production: {origin}")
                    raise ValueError("Wildcard origins not allowed in production")
            
            logger.info(f"🔒 Production CORS origins: {origins}")
            return origins
        
        elif self.environment == "staging":
            # Staging: Limited development origins
            return [
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://127.0.0.1:3000",
                "https://staging.edunerve.com"
            ]
        
        else:
            # Development: Permissive for local development
            logger.warning("⚠️ Development CORS: Permissive settings enabled")
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:3002",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
                "http://0.0.0.0:3000"
            ]
    
    def _get_allowed_methods(self) -> List[str]:
        """Get allowed HTTP methods"""
        if self.environment == "production":
            # Production: Only necessary methods
            return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        else:
            # Development: Include PATCH for testing
            return ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    
    def _get_allowed_headers(self) -> List[str]:
        """Get allowed headers"""
        return [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "Cache-Control"
        ]
    
    def _get_expose_headers(self) -> List[str]:
        """Get headers to expose to the browser"""
        return [
            "X-Total-Count",
            "X-Page-Count", 
            "X-Request-ID"
        ]
    
    def _get_allow_credentials(self) -> bool:
        """Whether to allow credentials in CORS requests"""
        return True  # Required for JWT cookies
    
    def _get_max_age(self) -> int:
        """Cache time for preflight requests"""
        if self.environment == "production":
            return 3600  # 1 hour
        else:
            return 86400  # 24 hours for development

def apply_secure_cors(app: FastAPI) -> None:
    """Apply secure CORS configuration to FastAPI app"""
    cors_config = CORSConfig()
    
    logger.info(f"🔒 Applying CORS configuration for {cors_config.environment} environment")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.allowed_origins,
        allow_credentials=cors_config.allow_credentials,
        allow_methods=cors_config.allowed_methods,
        allow_headers=cors_config.allowed_headers,
        expose_headers=cors_config.expose_headers,
        max_age=cors_config.max_age
    )
    
    logger.info("✅ Secure CORS middleware applied successfully")
    
    # Log security settings
    logger.info(f"CORS Origins: {len(cors_config.allowed_origins)} configured")
    logger.info(f"CORS Methods: {cors_config.allowed_methods}")
    logger.info(f"CORS Credentials: {cors_config.allow_credentials}")
    
    if cors_config.environment != "production":
        logger.warning("⚠️ Non-production CORS settings active")
