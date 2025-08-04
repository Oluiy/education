from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class NotificationChannel(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    IN_APP = "in_app"

class NotificationStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NotificationPriority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(100), unique=True, nullable=False)
    notification_type = Column(String(50), nullable=False)
    subject = Column(String(255))
    message = Column(Text, nullable=False)
    html_message = Column(Text)
    sender_id = Column(Integer, ForeignKey("users.id"))
    sender_name = Column(String(100))
    sender_type = Column(String(50))
    school_id = Column(Integer)
    context = Column(JSON)
    template_id = Column(Integer, ForeignKey("notification_templates.id"))
    template_data = Column(JSON)
    priority = Column(String(20), default="normal")
    category = Column(String(50))
    status = Column(String(20), default="pending")
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    expires_at = Column(DateTime)
    notification_metadata = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy reserved name
    attachments = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    template_type = Column(String(20), nullable=False)  # email, sms, push, whatsapp
    subject = Column(String(200))
    content = Column(Text, nullable=False)
    html_content = Column(Text)
    variables = Column(JSON)  # Template variables
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationRecipient(Base):
    __tablename__ = "notification_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(String(100), unique=True, nullable=False)
    notification_id = Column(String(100), ForeignKey("notifications.notification_id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    recipient_type = Column(String(20), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    whatsapp_number = Column(String(20))
    push_token = Column(String(500))
    name = Column(String(100))
    language = Column(String(10), default="en")
    timezone = Column(String(50))
    status = Column(String(20), default="pending")
    delivered_at = Column(DateTime)
    failed_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)



class NotificationDeliveryLog(Base):
    __tablename__ = "notification_delivery_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(100), unique=True, nullable=False)
    notification_id = Column(String(100), ForeignKey("notifications.notification_id"))
    recipient_id = Column(String(100), ForeignKey("notification_recipients.recipient_id"))
    provider = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    provider_response = Column(JSON)

class BulkNotification(Base):
    __tablename__ = "bulk_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    school_id = Column(Integer)
    notification_type = Column(String(50), nullable=False)
    template_id = Column(Integer, ForeignKey("notification_templates.id"))
    target_audience = Column(JSON)
    estimated_recipients = Column(Integer, default=0)
    actual_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    scheduled_at = Column(DateTime)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    content = Column(Text, nullable=False)
    variables = Column(JSON)  # Template variables
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationQueue(Base):
    __tablename__ = "notification_queue"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    template_id = Column(Integer, ForeignKey("notification_templates.id"))
    recipient = Column(String(200), nullable=False)  # email, phone, device_token
    notification_type = Column(String(20), nullable=False)
    subject = Column(String(200))
    content = Column(Text, nullable=False)
    variables = Column(JSON)
    status = Column(String(20), default='pending')  # pending, sent, failed, retrying
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    error_message = Column(Text)
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False)
    message_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    external_message_id = Column(String(100))  # Provider's message ID
    error_message = Column(Text)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WhatsAppTemplate(Base):
    __tablename__ = "whatsapp_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    template_id = Column(String(100), unique=True, nullable=False)  # Provider template ID
    category = Column(String(50), nullable=False)  # attendance, academic, fee, etc.
    content = Column(Text, nullable=False)
    variables = Column(JSON, default=[])  # List of template variables
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    queue_id = Column(Integer, ForeignKey("notification_queue.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    notification_type = Column(String(20), nullable=False)
    recipient = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False)
    response_data = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserNotificationPreference(Base):
    __tablename__ = "user_notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    notification_type = Column(String(20), nullable=False)  # email, sms, push, whatsapp
    category = Column(String(50), nullable=False)  # quiz_results, study_reminders, etc.
    is_enabled = Column(Boolean, default=True)
    frequency = Column(String(20), default='immediate')  # immediate, daily, weekly
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
