from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class SchoolStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    CANCELLED = "cancelled"

class School(Base):
    __tablename__ = 'schools'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    domain = Column(String(100), unique=True, nullable=False, index=True)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    contact_person = Column(String(100))
    
    # Subscription details
    subscription_plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    status = Column(Enum(SchoolStatus), default=SchoolStatus.PENDING)
    
    # Analytics data
    total_students = Column(Integer, default=0)
    total_teachers = Column(Integer, default=0)
    total_admins = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = Column(DateTime)
    suspended_at = Column(DateTime)

class SchoolAdmin(Base):
    __tablename__ = 'school_admins'
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    user_id = Column(Integer, nullable=False)  # Reference to auth service user
    email = Column(String(100), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="principal")
    permissions = Column(JSON)
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    school = relationship("School", backref="admins")

class SchoolSubscription(Base):
    __tablename__ = 'school_subscriptions'
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    amount = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    
    starts_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    status = Column(String(20), default="active")
    
    # Payment details
    payment_method = Column(String(50))
    last_payment_date = Column(DateTime)
    next_billing_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    school = relationship("School", backref="subscriptions")

class PlatformStats(Base):
    __tablename__ = 'platform_stats'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # School metrics
    total_schools = Column(Integer, default=0)
    active_schools = Column(Integer, default=0)
    new_schools_today = Column(Integer, default=0)
    
    # User metrics
    total_users = Column(Integer, default=0)
    total_students = Column(Integer, default=0)
    total_teachers = Column(Integer, default=0)
    total_admins = Column(Integer, default=0)
    active_users_today = Column(Integer, default=0)
    
    # Revenue metrics
    monthly_revenue = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    
    # Performance metrics
    avg_response_time = Column(Float, default=0.0)
    uptime_percentage = Column(Float, default=100.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemAlert(Base):
    __tablename__ = 'system_alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # error, warning, info
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    source_service = Column(String(50))
    school_id = Column(Integer, ForeignKey('schools.id'))
    
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="active")  # active, resolved, ignored
    
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    school = relationship("School", backref="alerts")
