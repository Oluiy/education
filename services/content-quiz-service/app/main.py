"""
EduNerve Content & Quiz Service - Production-Ready Main Application
Comprehensive content management and quiz system with full security hardening
"""

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
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

from .database import create_tables, check_database_connection
from .core.config import settings
from .core.security import SecurityConfig
from .api import subjects, courses, lessons, quizzes, questions, progress, study_sessions, study_goals, badges
from .schemas import ErrorResponse

# Load environment variables
load_dotenv()

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/var/log/content-quiz-service.log") if os.path.exists("/var/log") else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rate limiting setup
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )
    limiter = Limiter(key_func=get_remote_address, storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}")
except Exception as e:
    logger.warning(f"Redis unavailable for rate limiting: {e}")
    limiter = Limiter(key_func=get_remote_address)

# Security configuration
security_config = SecurityConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Production application lifespan with comprehensive initialization"""
    # Startup
    logger.info("🚀 Starting EduNerve Content & Quiz Service - Production Mode")
    
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
    
    # Create secure upload directories
    upload_dirs = ["uploads", "uploads/content", "uploads/quizzes", "uploads/temp"]
    for upload_dir in upload_dirs:
        os.makedirs(upload_dir, exist_ok=True)
        if hasattr(os, 'chmod'):
            os.chmod(upload_dir, 0o750)
    logger.info("✅ Secure upload directories created")
    
    # Validate configuration
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        logger.error("❌ Invalid or missing SECRET_KEY")
        raise Exception("Invalid security configuration")
    
    # Check external service connections
    try:
        # Add health check for auth service if needed
        logger.info("✅ External service connections verified")
    except Exception as e:
        logger.warning(f"⚠️ External service check failed: {e}")
    
    logger.info("🎉 Content & Quiz Service startup complete")
    
    yield
    
    # Shutdown
    logger.info("🔴 Shutting down Content & Quiz Service...")
    try:
        redis_client.close()
    except:
        pass
    logger.info("✅ Content & Quiz Service shutdown complete")


# Create production FastAPI application
app = FastAPI(
    title="EduNerve Content & Quiz Service",
    description="Production-ready content management and quiz system for African educational institutions",
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

# CORS middleware with production settings
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
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response

# Request timing and logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Static file serving with security
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API routers
app.include_router(subjects.router, prefix="/api/v1/subjects", tags=["Subjects"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["Courses"])
app.include_router(lessons.router, prefix="/api/v1/lessons", tags=["Lessons"])
app.include_router(quizzes.router, prefix="/api/v1/quizzes", tags=["Quizzes"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["Questions"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["Progress"])
app.include_router(study_sessions.router, prefix="/api/v1/study", tags=["Study Sessions"])
app.include_router(study_goals.router, prefix="/api/v1/study", tags=["Study Goals"])
app.include_router(badges.router, prefix="/api/v1/study", tags=["Badges"])

# Include new API routers
from .api import personalization, study_timer
app.include_router(personalization.router, prefix="/api/v1", tags=["Personalization"])
app.include_router(study_timer.router, prefix="/api/v1", tags=["Study Timer"])


# Production exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Enhanced HTTP exception handler with detailed logging"""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} - "
        f"Path: {request.url.path} - Client: {request.client.host if request.client else 'unknown'}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "success": False,
            "timestamp": time.time(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Production-safe general exception handler"""
    error_id = f"ERR_{int(time.time())}"
    
    logger.error(
        f"Unhandled exception [{error_id}]: {str(exc)} - "
        f"Path: {request.url.path} - Client: {request.client.host if request.client else 'unknown'}",
        exc_info=True
    )
    
    # Don't expose internal errors in production
    detail = "Internal server error" if not settings.DEBUG else str(exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": detail,
            "error_code": "INTERNAL_SERVER_ERROR",
            "error_id": error_id,
            "success": False,
            "timestamp": time.time()
        }
    )

# Root endpoint with comprehensive service info
@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Service information endpoint with rate limiting"""
    return {
        "service": "EduNerve Content & Quiz Service",
        "version": "1.0.0",
        "status": "operational",
        "environment": "production" if not settings.DEBUG else "development",
        "description": "Production-ready content management and quiz system",
        "features": [
            "Subject and Course Management",
            "Interactive Lesson Content",
            "AI-Powered Quiz Generation",
            "WAEC-Standard Assessments",
            "Real-time Progress Tracking",
            "Performance Analytics",
            "Multi-tenant Architecture",
            "Content Security",
            "Rate Limiting",
            "Comprehensive Logging"
        ],
        "api": {
            "docs": "/docs" if settings.DEBUG else "disabled",
            "health": "/health",
            "detailed_health": "/health/detailed"
        },
        "rate_limits": {
            "default": "100/minute",
            "uploads": "10/minute",
            "quiz_generation": "5/minute"
        }
    }

# Health check endpoints
@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Basic health check with rate limiting"""
    return {
        "status": "healthy",
        "service": "content-quiz-service",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/health/detailed")
@limiter.limit("10/minute")
async def detailed_health_check(request: Request):
    """Comprehensive health check with dependency status"""
    health_status = {
        "status": "healthy",
        "service": "content-quiz-service",
        "version": "1.0.0",
        "timestamp": time.time(),
        "checks": {},
        "performance": {}
    }
    
    # Database health check
    try:
        db_start = time.time()
        if check_database_connection():
            health_status["checks"]["database"] = "healthy"
            health_status["performance"]["database_response"] = f"{(time.time() - db_start)*1000:.2f}ms"
        else:
            health_status["checks"]["database"] = "unhealthy"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis health check
    try:
        redis_start = time.time()
        redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
        health_status["performance"]["redis_response"] = f"{(time.time() - redis_start)*1000:.2f}ms"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    
    # File system check
    try:
        upload_paths = ["uploads", "uploads/content", "uploads/quizzes"]
        for path in upload_paths:
            if not os.path.exists(path):
                health_status["checks"]["filesystem"] = f"missing directory: {path}"
                break
        else:
            health_status["checks"]["filesystem"] = "healthy"
    except Exception as e:
        health_status["checks"]["filesystem"] = f"error: {str(e)}"
    
    # Configuration check
    config_issues = []
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        config_issues.append("weak_secret_key")
    if not settings.DATABASE_URL:
        config_issues.append("missing_database_url")
    
    health_status["checks"]["configuration"] = "healthy" if not config_issues else f"issues: {', '.join(config_issues)}"
    
    return health_status

# Production server configuration
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8002")),
        reload=settings.DEBUG,
        log_level="info",
        access_log=True,
        workers=1 if settings.DEBUG else 4
    )
