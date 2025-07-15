"""
EduNerve API Gateway - Main Entry Point
This is the main entry point for the API Gateway service
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Import the FastAPI app
from app.main import app

# Re-export for convenience
__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=bool(os.getenv("RELOAD", "True").lower() == "true"),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True,
        use_colors=True
    )