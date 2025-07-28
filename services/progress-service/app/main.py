"""
Progress Service
Advanced progress tracking and analytics for educational content
"""

from fastapi import FastAPI, HTTPException, Request, status, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import os
import time
import redis
from dotenv import load_dotenv
import logging
from typing import Dict, List, Any, Optional

# Local imports
from .database import create_tables, check_database_connection
from .core.config import settings
from .core.security import SecurityConfig, get_current_user_token, require_admin_role, rate_limit_check
from .api import progress_analytics, learning_paths, achievements
from .schemas import ErrorResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/var/log/progress-service.log") if os.path.exists("/var/log") else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rate limiting setup
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB + 2,  # Different DB for progress service
        decode_responses=True
    )
    limiter = Limiter(key_func=get_remote_address, storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB + 2}")
except Exception as e:
    logger.warning(f"Redis unavailable for rate limiting: {e}")
    limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting EduNerve Progress Service")
    
    # Database initialization
    if not check_database_connection():
        logger.error("❌ Database connection failed")
        raise Exception("Cannot connect to database")
    
    try:
        create_tables()
        logger.info("✅ Database tables verified/created")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Redis connection check
    try:
        redis_client.ping()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
    
    logger.info("🎉 Progress Service startup complete")
    
    yield
    
    # Shutdown
    logger.info("🔴 Shutting down Progress Service...")
    try:
        redis_client.close()
    except:
        pass
    logger.info("✅ Progress Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="EduNerve Progress Service",
    description="Advanced progress tracking and learning analytics for African educational institutions",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# Security middlewares
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include API routers
app.include_router(progress_analytics.router, prefix="/api/v1/analytics", tags=["Progress Analytics"])
app.include_router(learning_paths.router, prefix="/api/v1/learning-paths", tags=["Learning Paths"])
app.include_router(achievements.router, prefix="/api/v1/achievements", tags=["Achievements"])


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        db_healthy = check_database_connection()
        
        # Check Redis
        redis_healthy = True
        try:
            redis_client.ping()
        except:
            redis_healthy = False
        
        status_code = status.HTTP_200_OK if db_healthy and redis_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "healthy" if db_healthy and redis_healthy else "unhealthy",
                "database": "connected" if db_healthy else "disconnected",
                "redis": "connected" if redis_healthy else "disconnected",
                "timestamp": time.time()
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code,
            path=str(request.url.path)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error" if not settings.DEBUG else str(exc),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            path=str(request.url.path)
        ).dict()
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "EduNerve Progress Service",
        "version": "1.0.0",
        "description": "Advanced progress tracking and learning analytics",
        "status": "operational",
        "docs_url": "/docs" if settings.DEBUG else None
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )
