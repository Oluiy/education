"""
Notification Models for EduNerve Platform
Comprehensive notification system with multiple channels and preferences
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class NotificationType(str, Enum):
    SYSTEM = "system"
    STUDY_REMINDER = "study_reminder"
    QUIZ_AVAILABLE = "quiz_available"
    ACHIEVEMENT = "achievement"
    COURSE_UPDATE = "course_update"
    SOCIAL = "social"
    MARKETING = "marketing"
    SECURITY = "security"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Notification(Base):
    """Core notification model"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Notification content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    short_message = Column(String(500))  # For SMS/push notifications
    
    # Notification metadata
    notification_type = Column(String(50), default=NotificationType.SYSTEM.value)
    priority = Column(String(20), default=NotificationPriority.MEDIUM.value)
    category = Column(String(50))  # study, quiz, achievement, etc.
    
    # Content and actions
    data = Column(JSON)  # Additional data payload
    action_url = Column(String(500))  # Deep link or action URL
    image_url = Column(String(255))
    icon = Column(String(100))  # emoji or icon identifier
    
    # Scheduling
    scheduled_for = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Status tracking
    status = Column(String(20), default=NotificationStatus.PENDING.value)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    
    # Delivery channels
    channels = Column(JSON)  # List of delivery channels
    
    # Grouping and threading
    group_id = Column(String(100))  # For grouping related notifications
    thread_id = Column(String(100))  # For conversation threading
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deliveries = relationship("NotificationDelivery", back_populates="notification")

class NotificationDelivery(Base):
    """Notification delivery tracking per channel"""
    __tablename__ = "notification_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"))
    
    # Delivery details
    channel = Column(String(20), nullable=False)  # email, sms, push, in_app
    recipient = Column(String(255))  # email address, phone number, device token
    
    # Status tracking
    status = Column(String(20), default=NotificationStatus.PENDING.value)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Timing
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    failed_at = Column(DateTime)
    next_retry_at = Column(DateTime)
    
    # Response tracking
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    unsubscribed_at = Column(DateTime)
    
    # Error handling
    error_message = Column(Text)
    error_code = Column(String(50))
    
    # Provider details
    provider = Column(String(50))  # firebase, sendgrid, twilio, etc.
    provider_message_id = Column(String(255))
    provider_response = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notification = relationship("Notification", back_populates="deliveries")

class NotificationTemplate(Base):
    """Reusable notification templates"""
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template identification
    template_key = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Template content
    title_template = Column(String(500))
    message_template = Column(Text)
    short_message_template = Column(String(500))
    
    # Template metadata
    notification_type = Column(String(50))
    priority = Column(String(20), default=NotificationPriority.MEDIUM.value)
    category = Column(String(50))
    
    # Channel-specific templates
    email_subject_template = Column(String(500))
    email_body_template = Column(Text)
    sms_template = Column(String(500))
    push_title_template = Column(String(200))
    push_body_template = Column(String(500))
    
    # Template configuration
    supported_channels = Column(JSON)  # List of supported channels
    default_channels = Column(JSON)  # Default channels for this template
    variables = Column(JSON)  # List of template variables
    
    # Scheduling defaults
    default_delay = Column(Integer)  # Default delay in minutes
    expiry_duration = Column(Integer)  # Default expiry in hours
    
    # Status
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Global preferences
    notifications_enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))  # HH:MM format
    timezone = Column(String(50), default='UTC')
    
    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    
    # Frequency preferences
    email_frequency = Column(String(20), default='immediate')  # immediate, daily, weekly
    digest_enabled = Column(Boolean, default=True)
    digest_frequency = Column(String(20), default='daily')  # daily, weekly
    digest_time = Column(String(5), default='09:00')  # HH:MM format
    
    # Content preferences by type
    study_reminders = Column(Boolean, default=True)
    quiz_notifications = Column(Boolean, default=True)
    achievement_notifications = Column(Boolean, default=True)
    course_updates = Column(Boolean, default=True)
    social_notifications = Column(Boolean, default=True)
    marketing_notifications = Column(Boolean, default=False)
    security_notifications = Column(Boolean, default=True)
    
    # Advanced preferences
    group_similar_notifications = Column(Boolean, default=True)
    smart_scheduling = Column(Boolean, default=True)  # AI-optimized timing
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationSchedule(Base):
    """Scheduled notification jobs"""
    __tablename__ = "notification_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Schedule details
    title = Column(String(200), nullable=False)
    template_key = Column(String(100), ForeignKey("notification_templates.template_key"))
    
    # Scheduling configuration
    schedule_type = Column(String(20))  # once, daily, weekly, monthly, cron
    cron_expression = Column(String(100))  # For complex schedules
    
    # Timing
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    next_run_at = Column(DateTime)
    last_run_at = Column(DateTime)
    
    # Recurrence (for simple schedules)
    days_of_week = Column(JSON)  # [1, 2, 3] for Mon, Tue, Wed
    time_of_day = Column(String(5))  # HH:MM format
    interval_minutes = Column(Integer)  # For interval-based schedules
    
    # Content data
    template_data = Column(JSON)  # Data to populate template variables
    
    # Status
    is_active = Column(Boolean, default=True)
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationRule(Base):
    """Automated notification rules and triggers"""
    __tablename__ = "notification_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Rule identification
    rule_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # Trigger configuration
    trigger_event = Column(String(100))  # user_registered, quiz_completed, etc.
    trigger_conditions = Column(JSON)  # Conditions that must be met
    
    # Target audience
    target_user_conditions = Column(JSON)  # User filtering conditions
    target_roles = Column(JSON)  # List of user roles
    
    # Notification configuration
    template_key = Column(String(100))
    delay_minutes = Column(Integer, default=0)
    
    # Rule behavior
    max_executions_per_user = Column(Integer)  # Limit per user
    cooldown_hours = Column(Integer)  # Minimum time between notifications
    
    # Status
    is_active = Column(Boolean, default=True)
    total_executions = Column(Integer, default=0)
    last_executed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationDigest(Base):
    """Daily/weekly notification digests"""
    __tablename__ = "notification_digests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Digest details
    digest_type = Column(String(20))  # daily, weekly
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Content
    total_notifications = Column(Integer, default=0)
    unread_notifications = Column(Integer, default=0)
    notification_summary = Column(JSON)  # Summary by category
    
    # Digest content
    digest_title = Column(String(200))
    digest_content = Column(Text)  # HTML content
    
    # Status
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class NotificationAnalytics(Base):
    """Notification performance analytics"""
    __tablename__ = "notification_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Analytics period
    date = Column(DateTime, nullable=False)
    notification_type = Column(String(50))
    channel = Column(String(20))
    
    # Metrics
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_unsubscribed = Column(Integer, default=0)
    
    # Calculated rates
    delivery_rate = Column(Float, default=0.0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    failure_rate = Column(Float, default=0.0)
    unsubscribe_rate = Column(Float, default=0.0)
    
    # Performance metrics
    average_delivery_time = Column(Float)  # in seconds
    average_open_time = Column(Float)  # in seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
