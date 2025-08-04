#!/usr/bin/env python3
"""
EduNerve Super Admin Service Startup Script
Starts the super admin service for managing schools and platform analytics
"""

import uvicorn
import os
from app.main import app
from app.config import settings

if __name__ == "__main__":
    # Use PORT environment variable for Heroku compatibility
    port = int(os.environ.get("PORT", settings.SERVICE_PORT))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
