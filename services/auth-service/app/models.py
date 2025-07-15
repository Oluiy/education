"""
EduNerve Authentication Service - Database Models
Multi-tenant architecture with school-based separation
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.database import Base


class UserRole(PyEnum):
    """User roles in the EduNerve system"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    PARENT = "parent"  # For future parent app


class School(Base):
    """
    School model for multi-tenancy
    Each user belongs to a school
    """
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)  # School identifier
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    principal_name = Column(String(100), nullable=True)
    
    # School settings
    is_active = Column(Boolean, default=True)
    max_students = Column(Integer, default=1000)
    max_teachers = Column(Integer, default=50)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="school")


class User(Base):
    """
    User model supporting Students, Teachers, and Admins
    Multi-tenant with school_id foreign key
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Personal information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    
    # Role and school association
    role = Column(Enum(UserRole), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    
    # Student-specific fields
    class_level = Column(String(20), nullable=True)  # e.g., "SS1", "SS2", "SS3"
    student_id = Column(String(20), nullable=True)  # School-specific student ID
    
    # Teacher-specific fields
    employee_id = Column(String(20), nullable=True)  # School-specific employee ID
    subjects = Column(Text, nullable=True)  # JSON string of subjects taught
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    school = relationship("School", back_populates="users")
    
    @property
    def full_name(self):
        """Return full name of the user"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role == UserRole.STUDENT
    
    @property
    def is_teacher(self):
        """Check if user is a teacher"""
        return self.role == UserRole.TEACHER
    
    @property
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == UserRole.ADMIN
