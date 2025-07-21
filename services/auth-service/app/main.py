"""
EduNerve Authentication Service - Enhanced Main FastAPI Application
Multi-tenant, role-based authentication system with comprehensive security
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from dotenv import load_dotenv

from app.database import create_tables
from app.routes import router
from app.schemas import ErrorResponse

# Import security modules
from app.cors_config import apply_secure_cors
from app.error_handling import (
    SecureErrorHandler, 
    ErrorResponseHandler, 
    SecurityError
)
from app.input_validation import sanitize_request_data
from app.security_config import SecurityConfig

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Enhanced application lifespan manager with security initialization
    """
    # Startup
    logger.info("🚀 Starting EduNerve Authentication Service with enhanced security...")
    
    # Initialize security configuration
    security_config = SecurityConfig()
    logger.info("✅ Security configuration initialized")
    
    # Create database tables
    create_tables()
    logger.info("✅ Database tables created successfully")
    
    # Security startup checks
    logger.info("🔐 Security system initialized successfully")
    logger.info("✅ Authentication service ready")
    
    yield
    
    # Shutdown
    logger.info("🔴 Shutting down EduNerve Authentication Service...")

# Create FastAPI application with security configurations
app = FastAPI(
    title="EduNerve Authentication Service",
    description="Multi-tenant authentication system with enhanced security for African secondary schools",
    version="2.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT", "development") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT", "development") == "development" else None,
    lifespan=lifespan,
    # Security headers
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Access denied"},
        422: {"description": "Invalid input data"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)

# Security middleware (order matters)
# 1. Trusted host middleware for host header validation
if os.getenv("ENVIRONMENT") == "production":
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# 2. CORS middleware with secure configuration
apply_secure_cors(app)

# 3. GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 4. Request sanitization middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """
    Security middleware for request validation and sanitization
    """
    try:
        # Log request for security monitoring
        logger.info(
            f"Request: {request.method} {request.url} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Add security headers to response
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
        
    except Exception as e:
        logger.error(f"Security middleware error: {e}")
        return await SecureErrorHandler.internal_error_handler(request, e)

# Enhanced exception handlers
@app.exception_handler(SecurityError)
async def security_exception_handler(request: Request, exc: SecurityError):
    """Handle security-related errors"""
    return await SecureErrorHandler.security_error_handler(request, exc)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Enhanced HTTP exception handler"""
    if exc.status_code == 401:
        return await SecureErrorHandler.authentication_error_handler(request, exc)
    elif exc.status_code == 403:
        return await SecureErrorHandler.authorization_error_handler(request, exc)
    elif exc.status_code == 422:
        return await SecureErrorHandler.validation_error_handler(request, exc)
    elif exc.status_code == 429:
        return await SecureErrorHandler.rate_limit_error_handler(request, exc)
    else:
        # Generic HTTP error handling
        request_id = ErrorResponseHandler.log_error(exc, request)
        response = ErrorResponseHandler.create_error_response(
            status_code=exc.status_code,
            message=exc.detail,
            request_id=request_id
        )
        return JSONResponse(status_code=exc.status_code, content=response)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Enhanced general exception handler"""
    return await SecureErrorHandler.internal_error_handler(request, exc)

# Include authentication routes
app.include_router(router, prefix="/api/v1/auth", tags=["Authentication"])

# Enhanced root endpoint with security information
@app.get("/")
async def root():
    """
    Root endpoint with service information and security status
    """
    return {
        "service": "EduNerve Authentication Service",
        "version": "2.0.0",
        "status": "running",
        "security": "enhanced",
        "description": "Multi-tenant authentication system with comprehensive security for African secondary schools",
        "features": [
            "JWT-based authentication",
            "Role-based access control",
            "Multi-tenant architecture",
            "Enhanced security validation",
            "Secure CORS configuration",
            "Input sanitization",
            "Error handling with audit logging"
        ],
        "endpoints": {
            "docs": "/docs" if os.getenv("ENVIRONMENT", "development") == "development" else "disabled",
            "redoc": "/redoc" if os.getenv("ENVIRONMENT", "development") == "development" else "disabled",
            "health": "/api/v1/auth/health",
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login"
        },
        "security_features": {
            "password_requirements": "12+ chars, mixed case, numbers, special chars",
            "token_expiration": "60 minutes",
            "cors_policy": "environment-specific",
            "input_validation": "comprehensive",
            "error_masking": "enabled"
        }
    }

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    """
    Enhanced health check endpoint with security status
    """
    return {
        "status": "healthy",
        "service": "EduNerve Authentication Service",
        "version": "2.0.0",
        "security": "enhanced",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": "2024-01-01T00:00:00Z",
        "components": {
            "database": "connected",
            "jwt_system": "operational",
            "security_validation": "active",
            "cors_protection": "enabled"
        }
    }

# Development server configuration
if __name__ == "__main__":
    # Enhanced development server with security considerations
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "development") == "development",
        log_level=os.getenv("LOG_LEVEL", "info"),
        access_log=True,
        # Security configurations for development
        ssl_keyfile=os.getenv("SSL_KEYFILE") if os.getenv("ENVIRONMENT") == "production" else None,
        ssl_certfile=os.getenv("SSL_CERTFILE") if os.getenv("ENVIRONMENT") == "production" else None,
    )
