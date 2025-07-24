"""
Admin Service Database Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class SystemRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    PRINCIPAL = "principal"
    VICE_PRINCIPAL = "vice_principal"
    DEPARTMENT_HEAD = "department_head"
    COORDINATOR = "coordinator"

class AdminUser(Base):
    """Admin users with extended privileges"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Reference to auth service user
    school_id = Column(Integer, index=True)
    
    # Admin-specific fields
    system_role = Column(SQLEnum(SystemRole), default=SystemRole.SCHOOL_ADMIN)
    permissions = Column(JSON)  # Detailed permissions
    departments = Column(JSON)  # Assigned departments
    
    # Profile information
    employee_id = Column(String, unique=True, index=True)
    job_title = Column(String)
    phone = Column(String)
    emergency_contact = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="admin_user")
    reports = relationship("Report", back_populates="created_by_admin")

class School(Base):
    """Extended school information for admin management"""
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, unique=True, index=True)  # Reference to auth service
    
    # School details
    name = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    address = Column(Text)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    
    # Administrative info
    principal_name = Column(String)
    principal_email = Column(String)
    established_date = Column(DateTime)
    school_type = Column(String)  # public, private, charter, etc.
    
    # Configuration
    settings = Column(JSON)  # School-specific settings
    features_enabled = Column(JSON)  # Feature toggles
    subscription_tier = Column(String, default="basic")
    
    # Statistics
    total_students = Column(Integer, default=0)
    total_teachers = Column(Integer, default=0)
    total_classes = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    departments = relationship("Department", back_populates="school")
    reports = relationship("Report", back_populates="school")

class Department(Base):
    """School departments/subjects"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    
    name = Column(String, index=True)
    code = Column(String, index=True)
    description = Column(Text)
    
    # Department head
    head_user_id = Column(Integer)  # Reference to auth service user
    head_name = Column(String)
    head_email = Column(String)
    
    # Configuration
    budget = Column(Float)
    settings = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="departments")

class AuditLog(Base):
    """System audit logs"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Action details
    action = Column(String, index=True)
    resource_type = Column(String, index=True)
    resource_id = Column(String, index=True)
    
    # Request details
    ip_address = Column(String)
    user_agent = Column(String)
    request_method = Column(String)
    request_url = Column(String)
    
    # Data
    old_values = Column(JSON)
    new_values = Column(JSON)
    audit_metadata = Column(JSON)
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    admin_user = relationship("AdminUser", back_populates="audit_logs")

class Report(Base):
    """Generated reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    created_by_admin_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Report details
    title = Column(String, index=True)
    description = Column(Text)
    report_type = Column(String, index=True)  # student_performance, attendance, etc.
    
    # Parameters
    date_range_start = Column(DateTime)
    date_range_end = Column(DateTime)
    filters = Column(JSON)
    parameters = Column(JSON)
    
    # File information
    file_path = Column(String)
    file_format = Column(String)  # pdf, xlsx, csv
    file_size = Column(Integer)
    
    # Status
    status = Column(String, default="generating")  # generating, completed, failed
    progress = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    school = relationship("School", back_populates="reports")
    created_by_admin = relationship("AdminUser", back_populates="reports")

class SystemConfig(Base):
    """System-wide configuration"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSON)
    description = Column(Text)
    
    # Metadata
    is_public = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)
    data_type = Column(String)  # string, integer, boolean, json, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemAlert(Base):
    """System-wide alerts and notifications"""
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True)  # null for system-wide alerts
    
    # Alert details
    title = Column(String, index=True)
    message = Column(Text)
    alert_type = Column(String, index=True)  # info, warning, error, success
    severity = Column(String, default="medium")  # low, medium, high, critical
    
    # Targeting
    target_roles = Column(JSON)  # Which roles should see this alert
    target_users = Column(JSON)  # Specific users to notify
    
    # Display settings
    is_dismissible = Column(Boolean, default=True)
    auto_dismiss_after = Column(Integer)  # Minutes
    
    # Status
    is_active = Column(Boolean, default=True)
    is_system_wide = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class BackgroundTask(Base):
    """Background task tracking"""
    __tablename__ = "background_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True)
    created_by_admin_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Task details
    task_id = Column(String, unique=True, index=True)
    task_type = Column(String, index=True)
    task_name = Column(String)
    description = Column(Text)
    
    # Parameters
    parameters = Column(JSON)
    
    # Status
    status = Column(String, default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0)
    result = Column(JSON)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    created_by_admin = relationship("AdminUser")

class DataExport(Base):
    """Data export requests"""
    __tablename__ = "data_exports"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True)
    requested_by_admin_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Export details
    export_type = Column(String, index=True)  # students, teachers, grades, etc.
    file_format = Column(String)  # csv, xlsx, json
    
    # Filters
    date_range_start = Column(DateTime)
    date_range_end = Column(DateTime)
    filters = Column(JSON)
    
    # File information
    file_path = Column(String)
    file_size = Column(Integer)
    download_count = Column(Integer, default=0)
    
    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)  # When the file will be deleted
    
    # Relationships
    requested_by_admin = relationship("AdminUser")
