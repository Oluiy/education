import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://edunerve_user:password@localhost/edunerve_db")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # Service configuration
    SERVICE_NAME = "super-admin-service"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8009"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # External services
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    ADMIN_SERVICE_URL = os.getenv("ADMIN_SERVICE_URL", "http://localhost:8002")
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8003")
    
    # Email configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    # Heroku deployment
    PORT = os.getenv("PORT", "8009")
    
    class Config:
        case_sensitive = True

settings = Settings()
