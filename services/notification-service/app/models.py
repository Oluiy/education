"""
EduNerve Notification Service - Database Models
Handles all types of notifications: SMS, WhatsApp, Email, Push, Voice
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    VOICE = "voice"
    IN_APP = "in_app"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class RecipientType(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    PARENT = "parent"
    ADMIN = "admin"
    STAFF = "staff"
    GROUP = "group"
    SCHOOL = "school"

class Notification(Base):
    """Main notification table for all types of notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Notification details
    notification_type = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    html_message = Column(Text, nullable=True)
    
    # Sender information
    sender_id = Column(Integer, nullable=True)
    sender_name = Column(String, nullable=True)
    sender_type = Column(String, nullable=False)  # system, admin, teacher, etc.
    
    # School and context
    school_id = Column(Integer, nullable=False, index=True)
    context = Column(JSON, nullable=True)  # Additional context data
    
    # Template information
    template_id = Column(String, nullable=True)
    template_data = Column(JSON, nullable=True)
    
    # Priority and category
    priority = Column(String, default=NotificationPriority.NORMAL)
    category = Column(String, nullable=True)  # academic, administrative, emergency, etc.
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Status and tracking
    status = Column(String, default=NotificationStatus.PENDING)
    retry_count = Column(Integer, default=0)
    last_retry = Column(DateTime, nullable=True)
    
    # Notification metadata
    notification_metadata = Column(JSON, default=dict)
    attachments = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    recipients = relationship("NotificationRecipient", back_populates="notification")
    delivery_logs = relationship("NotificationDeliveryLog", back_populates="notification")
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_school_type', 'school_id', 'notification_type'),
        Index('idx_notification_status_scheduled', 'status', 'scheduled_at'),
        Index('idx_notification_priority_created', 'priority', 'created_at'),
        Index('idx_notification_sender_created', 'sender_id', 'created_at'),
    )

class NotificationRecipient(Base):
    """Individual recipients for notifications"""
    __tablename__ = "notification_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Notification reference
    notification_id = Column(String, ForeignKey("notifications.notification_id"), nullable=False)
    
    # Recipient details
    user_id = Column(Integer, nullable=True)
    recipient_type = Column(String, nullable=False)
    
    # Contact information
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    whatsapp_number = Column(String, nullable=True)
    push_token = Column(String, nullable=True)
    
    # Recipient metadata
    name = Column(String, nullable=False)
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    
    # Delivery status per recipient
    status = Column(String, default=NotificationStatus.PENDING)
    delivery_attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime, nullable=True)
    
    # Delivery details
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    failed_reason = Column(String, nullable=True)
    
    # External provider details
    external_id = Column(String, nullable=True)  # Provider-specific ID
    provider_response = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notification = relationship("Notification", back_populates="recipients")
    
    # Indexes
    __table_args__ = (
        Index('idx_recipient_notification_user', 'notification_id', 'user_id'),
        Index('idx_recipient_type_status', 'recipient_type', 'status'),
        Index('idx_recipient_phone_email', 'phone', 'email'),
    )

class NotificationTemplate(Base):
    """Templates for different types of notifications"""
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Template details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String, nullable=False)  # email, sms, whatsapp, push
    
    # Template content
    subject_template = Column(String, nullable=True)
    message_template = Column(Text, nullable=False)
    html_template = Column(Text, nullable=True)
    
    # Localization
    language = Column(String, default="en")
    translations = Column(JSON, default=dict)
    
    # Template metadata
    variables = Column(JSON, default=list)  # List of template variables
    category = Column(String, nullable=True)
    
    # Usage and context
    school_id = Column(Integer, nullable=True)  # Null for system templates
    is_system_template = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_template_type_school', 'template_type', 'school_id'),
        Index('idx_template_category_active', 'category', 'is_active'),
    )

class NotificationDeliveryLog(Base):
    """Detailed delivery logs for notifications"""
    __tablename__ = "notification_delivery_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Notification reference
    notification_id = Column(String, ForeignKey("notifications.notification_id"), nullable=False)
    recipient_id = Column(String, nullable=True)
    
    # Delivery details
    provider = Column(String, nullable=False)  # twilio, firebase, etc.
    provider_id = Column(String, nullable=True)  # External provider ID
    
    # Attempt details
    attempt_number = Column(Integer, default=1)
    status = Column(String, nullable=False)
    
    # Response details
    response_code = Column(String, nullable=True)
    response_message = Column(Text, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    # Timing
    attempted_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Error details
    error_type = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    notification = relationship("Notification", back_populates="delivery_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_delivery_log_notification', 'notification_id'),
        Index('idx_delivery_log_status_attempted', 'status', 'attempted_at'),
        Index('idx_delivery_log_provider', 'provider'),
    )

class NotificationQueue(Base):
    """Queue for processing notifications"""
    __tablename__ = "notification_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    queue_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Notification reference
    notification_id = Column(String, nullable=False)
    
    # Queue details
    queue_name = Column(String, nullable=False)  # high_priority, normal, low_priority
    priority = Column(Integer, default=1)
    
    # Processing status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    worker_id = Column(String, nullable=True)
    
    # Timing
    queued_at = Column(DateTime, default=datetime.utcnow)
    processing_started = Column(DateTime, nullable=True)
    processing_completed = Column(DateTime, nullable=True)
    
    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry = Column(DateTime, nullable=True)
    
    # Queue metadata
    queue_metadata = Column(JSON, default=dict)
    
    # Indexes
    __table_args__ = (
        Index('idx_queue_status_priority', 'status', 'priority'),
        Index('idx_queue_name_queued', 'queue_name', 'queued_at'),
        Index('idx_queue_next_retry', 'next_retry'),
    )

class NotificationSettings(Base):
    """User notification preferences and settings"""
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User details
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    user_type = Column(String, nullable=False)  # student, teacher, parent, admin
    
    # Contact preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)
    whatsapp_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    voice_enabled = Column(Boolean, default=False)
    
    # Category preferences
    academic_notifications = Column(Boolean, default=True)
    administrative_notifications = Column(Boolean, default=True)
    emergency_notifications = Column(Boolean, default=True)
    marketing_notifications = Column(Boolean, default=False)
    
    # Timing preferences
    quiet_hours_start = Column(String, nullable=True)  # HH:MM format
    quiet_hours_end = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    
    # Language and localization
    language = Column(String, default="en")
    auto_translate = Column(Boolean, default=True)
    
    # Advanced settings
    digest_mode = Column(Boolean, default=False)
    digest_frequency = Column(String, default="daily")  # daily, weekly
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_settings_user_school', 'user_id', 'school_id'),
        Index('idx_settings_type_school', 'user_type', 'school_id'),
    )

class NotificationAnalytics(Base):
    """Analytics and metrics for notifications"""
    __tablename__ = "notification_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time and scope
    date = Column(DateTime, nullable=False)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Notification metrics
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_read = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    
    # By type
    email_sent = Column(Integer, default=0)
    sms_sent = Column(Integer, default=0)
    whatsapp_sent = Column(Integer, default=0)
    push_sent = Column(Integer, default=0)
    voice_sent = Column(Integer, default=0)
    
    # By priority
    emergency_sent = Column(Integer, default=0)
    high_priority_sent = Column(Integer, default=0)
    normal_sent = Column(Integer, default=0)
    low_priority_sent = Column(Integer, default=0)
    
    # Performance metrics
    avg_delivery_time = Column(Integer, default=0)  # seconds
    avg_read_time = Column(Integer, default=0)  # seconds
    
    # Cost metrics
    total_cost = Column(String, nullable=True)  # JSON string for different currencies
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_analytics_date_school', 'date', 'school_id'),
    )

class NotificationContact(Base):
    """Contact information for notifications"""
    __tablename__ = "notification_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # User reference
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Contact details
    contact_type = Column(String, nullable=False)  # primary, secondary, emergency
    
    # Contact information
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    whatsapp_number = Column(String, nullable=True)
    
    # Verification status
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    whatsapp_verified = Column(Boolean, default=False)
    
    # Preferences
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_contact_user_school', 'user_id', 'school_id'),
        Index('idx_contact_type_active', 'contact_type', 'is_active'),
        Index('idx_contact_email_phone', 'email', 'phone'),
    )

class BulkNotification(Base):
    """Bulk notification campaigns"""
    __tablename__ = "bulk_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Campaign details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Creator and school
    created_by = Column(Integer, nullable=False)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Campaign settings
    notification_type = Column(String, nullable=False)
    template_id = Column(String, nullable=True)
    
    # Recipients
    target_audience = Column(JSON, nullable=False)  # Selection criteria
    estimated_recipients = Column(Integer, default=0)
    actual_recipients = Column(Integer, default=0)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Status and progress
    status = Column(String, default="draft")  # draft, scheduled, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    
    # Results
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_bulk_school_status', 'school_id', 'status'),
        Index('idx_bulk_created_by', 'created_by'),
        Index('idx_bulk_scheduled', 'scheduled_at'),
    )
