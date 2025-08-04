from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://edunerve:edunerve2024@localhost:5432/edunerve_super_admin"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
