"""
EduNerve Authentication Service - Main FastAPI Application
Multi-tenant, role-based authentication system for African schools
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.database import create_tables
from app.routes import router
from app.schemas import ErrorResponse

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    print("🚀 Starting EduNerve Authentication Service...")
    create_tables()
    print("✅ Database tables created successfully")
    
    yield
    
    # Shutdown
    print("🔴 Shutting down EduNerve Authentication Service...")


# Create FastAPI application
app = FastAPI(
    title="EduNerve Authentication Service",
    description="Multi-tenant authentication system for African secondary schools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(router, prefix="/api/v1/auth", tags=["Authentication"])


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global HTTP exception handler
    """
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
    """
    Global general exception handler
    """
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
    """
    Root endpoint with service information
    """
    return {
        "service": "EduNerve Authentication Service",
        "version": "1.0.0",
        "status": "running",
        "description": "Multi-tenant authentication system for African secondary schools",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/auth/health",
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "EduNerve Auth Service",
        "version": "1.0.0"
    }


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
