"""
EduNerve Content & Quiz Service - Main FastAPI Application
Content management and AI-powered quiz generation system
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
import logging

from app.database import create_tables
from app.routes import router
from app.schemas import ErrorResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting EduNerve Content & Quiz Service...")
    
    # Create database tables
    create_tables()
    logger.info("✅ Database tables created successfully")
    
    # Create upload directory
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    logger.info(f"✅ Upload directory created: {upload_dir}")
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("⚠️ OpenAI API key not found - AI features will be disabled")
    else:
        logger.info("✅ OpenAI API key configured")
    
    # Check auth service connection
    try:
        from app.auth import check_auth_service_health
        auth_healthy = await check_auth_service_health()
        if auth_healthy:
            logger.info("✅ Auth service connection established")
        else:
            logger.warning("⚠️ Auth service connection failed")
    except Exception as e:
        logger.warning(f"⚠️ Could not check auth service: {str(e)}")
    
    logger.info("🎉 Content & Quiz Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("🔴 Shutting down EduNerve Content & Quiz Service...")


# Create FastAPI application
app = FastAPI(
    title="EduNerve Content & Quiz Service",
    description="AI-powered content management and quiz generation system for African secondary schools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded content
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routes
app.include_router(router, prefix="/api/v1", tags=["Content & Quiz"])


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            success=False
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global general exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="Internal server error",
            error_code="INTERNAL_SERVER_ERROR",
            success=False
        ).dict()
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "EduNerve Content & Quiz Service",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-powered content management and quiz generation system",
        "features": [
            "File upload and content management",
            "AI-powered quiz generation",
            "Automatic grading (MCQ + Theory)",
            "Multi-tenant school isolation",
            "WAEC-standard question formats",
            "Performance analytics"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/health",
            "upload_content": "/api/v1/content/upload",
            "generate_quiz": "/api/v1/quiz/generate_ai",
            "submit_quiz": "/api/v1/quiz/submit"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check database connection
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check OpenAI API
    openai_status = "configured" if os.getenv("OPENAI_API_KEY") else "not configured"
    
    # Check auth service
    auth_status = "unknown"
    try:
        from app.auth import check_auth_service_health
        auth_healthy = await check_auth_service_health()
        auth_status = "healthy" if auth_healthy else "unhealthy"
    except:
        auth_status = "connection_failed"
    
    return {
        "status": "healthy",
        "service": "EduNerve Content & Quiz Service",
        "version": "1.0.0",
        "database": db_status,
        "openai": openai_status,
        "auth_service": auth_status,
        "upload_directory": "uploads" if os.path.exists("uploads") else "missing"
    }


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
