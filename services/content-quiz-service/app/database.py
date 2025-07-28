"""
Database Configuration and Setup
Production-ready SQLAlchemy configuration with connection pooling and security
"""

import logging
import time
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, MetaData, text, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError

from .core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy metadata and base
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Database engine with production configuration
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before use
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    echo_pool=False,
    connect_args={
        "options": "-c timezone=utc",
        "connect_timeout": 10,
        "application_name": "content-quiz-service"
    } if settings.DATABASE_URL.startswith("postgresql") else {}
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


# Connection event listeners for monitoring and security
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and security"""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=memory")
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
        cursor.close()


@event.listens_for(engine, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """Ping connection on checkout to ensure it's alive"""
    try:
        dbapi_connection.execute("SELECT 1")
    except Exception:
        # Connection is invalid, raise DisconnectionError to get a new one
        raise DisconnectionError()


@event.listens_for(engine, "before_cursor_execute")
def log_slow_queries(conn, cursor, statement, parameters, context, executemany):
    """Log execution start time for slow query detection"""
    context._query_start_time = time.time()


@event.listens_for(engine, "after_cursor_execute")
def log_slow_queries_end(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries for performance monitoring"""
    total = time.time() - context._query_start_time
    
    if total > 1.0:  # Log queries taking more than 1 second
        logger.warning(
            f"Slow query detected: {total:.2f}s - {statement[:200]}..."
            + ("..." if len(statement) > 200 else "")
        )


class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def create_tables():
        """Create all database tables"""
        try:
            # Import all models to ensure they're registered
            from .models import (
                user_models,
                content_models, 
                progress_models,
                notification_models,
                file_models,
                assistant_models,
                admin_models
            )
            
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    @staticmethod
    def check_database_connection(retries: int = 3) -> bool:
        """Check database connectivity with retries"""
        for attempt in range(retries):
            try:
                with engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                return True
            except Exception as e:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error("All database connection attempts failed")
        return False
    
    @staticmethod
    def get_database_info() -> dict:
        """Get database information and statistics"""
        try:
            with engine.connect() as connection:
                # Get basic database info
                info = {
                    "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
                    "pool_size": engine.pool.size(),
                    "checked_out_connections": engine.pool.checkedout(),
                    "pool_overflow": engine.pool.overflow(),
                    "invalid_connections": engine.pool.invalidated(),
                }
                
                # PostgreSQL specific info
                if settings.DATABASE_URL.startswith("postgresql"):
                    result = connection.execute(text("SELECT version()"))
                    info["version"] = result.scalar()
                    
                    result = connection.execute(text("SELECT current_database()"))
                    info["database"] = result.scalar()
                
                # SQLite specific info
                elif settings.DATABASE_URL.startswith("sqlite"):
                    result = connection.execute(text("SELECT sqlite_version()"))
                    info["version"] = f"SQLite {result.scalar()}"
                
                return info
                
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}


class DatabaseSession:
    """Database session management with automatic retry and cleanup"""
    
    def __init__(self, retries: int = 3):
        self.retries = retries
        self.session: Optional[Session] = None
    
    def __enter__(self) -> Session:
        """Create database session with retry logic"""
        for attempt in range(self.retries):
            try:
                self.session = SessionLocal()
                return self.session
            except Exception as e:
                logger.warning(f"Session creation attempt {attempt + 1} failed: {e}")
                if attempt < self.retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                else:
                    raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up database session"""
        if self.session:
            try:
                if exc_type:
                    self.session.rollback()
                else:
                    self.session.commit()
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
                self.session.rollback()
            finally:
                self.session.close()


# Dependency function for FastAPI
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions"""
    with DatabaseSession() as db:
        yield db


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    with DatabaseSession() as db:
        yield db


# Health check utilities
def check_database_connection() -> bool:
    """Quick database connection check"""
    return DatabaseManager.check_database_connection()


def create_tables():
    """Create database tables"""
    DatabaseManager.create_tables()


def get_database_info() -> dict:
    """Get database information"""
    return DatabaseManager.get_database_info()
