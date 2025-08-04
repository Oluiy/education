from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"

class School(Base):
    __tablename__ = 'schools'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String, unique=True, index=True, nullable=False)
    address = Column(String, nullable=True)
    contact_email = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)  # NULL for super admin
    username = Column(String(50), index=True, nullable=False)
    email = Column(String(100), index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    role = Column(String(20), nullable=False, default=UserRole.STUDENT.value)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    profile_data = Column(JSON, default={})  # Student ID, Parent info, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", backref="users")
    
    # Ensure username+school_id combination is unique (allows same username across schools)
    __table_args__ = (
        {'extend_existing': True}
    )

class UserRoleAssignment(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    school_id = Column(Integer, ForeignKey("schools.id"))
    role_name = Column(String(50), nullable=False)
    permissions = Column(JSON, default={})  # JSON object of permissions
    granted_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="role_assignments")
    school = relationship("School", backref="role_assignments")
    granted_by_user = relationship("User", foreign_keys=[granted_by])

class AuthSession(Base):
    __tablename__ = "auth_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    token = Column(String(500), unique=True, index=True)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    device_info = Column(JSON, default={})  # Browser, IP, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="sessions")
    school = relationship("School", backref="sessions")

class PasswordReset(Base):
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reset_token = Column(String(100), unique=True)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
