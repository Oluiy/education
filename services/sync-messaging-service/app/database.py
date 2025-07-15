"""
EduNerve Sync & Messaging Service - Database Configuration
SQLAlchemy setup with support for both SQLite and PostgreSQL
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sync_messaging.db")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
    logger.info("Using SQLite database")
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
    logger.info("Using PostgreSQL database")

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Metadata
metadata = MetaData()

def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    """
    try:
        # Import models to ensure they're registered
        from .models import (
            SyncRecord, Message, Notification, DeviceRegistration,
            SyncConflict, MessageThread, OfflineData, WebSocketConnection
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def drop_tables():
    """
    Drop all database tables (for testing)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
        
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        raise

def reset_database():
    """
    Reset database by dropping and recreating all tables
    """
    try:
        drop_tables()
        create_tables()
        logger.info("Database reset successfully")
        
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise

# Database utilities
class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def check_connection():
        """Check database connection"""
        try:
            with engine.connect() as connection:
                connection.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False
    
    @staticmethod
    def get_table_counts():
        """Get row counts for all tables"""
        try:
            with SessionLocal() as db:
                from .models import (
                    SyncRecord, Message, Notification, DeviceRegistration,
                    SyncConflict, MessageThread, OfflineData, WebSocketConnection
                )
                
                counts = {
                    "sync_records": db.query(SyncRecord).count(),
                    "messages": db.query(Message).count(),
                    "notifications": db.query(Notification).count(),
                    "device_registrations": db.query(DeviceRegistration).count(),
                    "sync_conflicts": db.query(SyncConflict).count(),
                    "message_threads": db.query(MessageThread).count(),
                    "offline_data": db.query(OfflineData).count(),
                    "websocket_connections": db.query(WebSocketConnection).count()
                }
                
                return counts
                
        except Exception as e:
            logger.error(f"Error getting table counts: {str(e)}")
            return {}
    
    @staticmethod
    def cleanup_expired_data():
        """Clean up expired data"""
        try:
            with SessionLocal() as db:
                from datetime import datetime, timedelta
                from .models import OfflineData, Notification, WebSocketConnection
                
                # Clean up expired offline data
                expired_cutoff = datetime.utcnow()
                expired_offline = db.query(OfflineData).filter(
                    OfflineData.expires_at < expired_cutoff
                ).delete()
                
                # Clean up old notifications (30 days)
                notification_cutoff = datetime.utcnow() - timedelta(days=30)
                old_notifications = db.query(Notification).filter(
                    Notification.created_at < notification_cutoff,
                    Notification.status.in_(["sent", "delivered", "read"])
                ).delete()
                
                # Clean up inactive websocket connections (1 hour)
                connection_cutoff = datetime.utcnow() - timedelta(hours=1)
                inactive_connections = db.query(WebSocketConnection).filter(
                    WebSocketConnection.last_ping < connection_cutoff,
                    WebSocketConnection.is_active == True
                ).update({"is_active": False, "disconnected_at": datetime.utcnow()})
                
                db.commit()
                
                logger.info(f"Cleanup completed: {expired_offline} offline data, {old_notifications} notifications, {inactive_connections} connections")
                
                return {
                    "expired_offline_data": expired_offline,
                    "old_notifications": old_notifications,
                    "inactive_connections": inactive_connections
                }
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return {}

# Initialize database
def init_database():
    """Initialize database on startup"""
    try:
        # Check connection
        if not DatabaseManager.check_connection():
            raise Exception("Cannot connect to database")
        
        # Create tables
        create_tables()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
