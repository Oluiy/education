"""
EduNerve Sync & Messaging Service - Database Models
Handles offline sync, messaging, notifications, and real-time communication
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

class SyncStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"

class MessageType(str, Enum):
    CHAT = "chat"
    NOTIFICATION = "notification"
    ANNOUNCEMENT = "announcement"
    ALERT = "alert"
    SYSTEM = "system"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    DELETED = "deleted"

class SyncRecord(Base):
    """Tracks data synchronization between offline and online states"""
    __tablename__ = "sync_records"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    device_id = Column(String, nullable=False, index=True)
    
    # Sync details
    entity_type = Column(String, nullable=False)  # user, content, quiz, etc.
    entity_id = Column(String, nullable=False)
    operation = Column(String, nullable=False)  # create, update, delete
    
    # Data
    data = Column(JSON, nullable=False)
    metadata = Column(JSON, default=dict)
    
    # Status and timing
    status = Column(String, default=SyncStatus.PENDING)
    priority = Column(Integer, default=1)  # 1=high, 2=medium, 3=low
    retry_count = Column(Integer, default=0)
    last_retry = Column(DateTime, nullable=True)
    
    # Conflict resolution
    conflict_data = Column(JSON, nullable=True)
    resolution_strategy = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_sync_user_status', 'user_id', 'status'),
        Index('idx_sync_school_entity', 'school_id', 'entity_type'),
        Index('idx_sync_device_created', 'device_id', 'created_at'),
    )

class Message(Base):
    """Handles all types of messages and communications"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Message details
    message_type = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    
    # Participants
    sender_id = Column(Integer, nullable=False, index=True)
    sender_name = Column(String, nullable=False)
    sender_type = Column(String, nullable=False)  # user, system, admin
    
    # Recipients
    recipient_ids = Column(JSON, nullable=False)  # List of user IDs
    recipient_groups = Column(JSON, nullable=True)  # Groups like "class_1", "teachers"
    
    # Context
    school_id = Column(Integer, nullable=False, index=True)
    context = Column(JSON, nullable=True)  # Additional context data
    
    # Attachments
    attachments = Column(JSON, nullable=True)
    
    # Status and delivery
    status = Column(String, default=MessageStatus.SENT)
    delivery_status = Column(JSON, default=dict)  # Per-recipient delivery status
    read_status = Column(JSON, default=dict)  # Per-recipient read status
    
    # Threading
    thread_id = Column(String, nullable=True, index=True)
    parent_message_id = Column(String, nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_message_sender_school', 'sender_id', 'school_id'),
        Index('idx_message_type_created', 'message_type', 'created_at'),
        Index('idx_message_thread_created', 'thread_id', 'created_at'),
    )

class Notification(Base):
    """Handles push notifications and system notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Notification details
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False)
    category = Column(String, nullable=True)
    
    # Target
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    device_tokens = Column(JSON, nullable=True)  # FCM tokens
    
    # Content
    data = Column(JSON, nullable=True)  # Additional data
    action_url = Column(String, nullable=True)
    actions = Column(JSON, nullable=True)  # Action buttons
    
    # Delivery
    status = Column(String, default=NotificationStatus.PENDING)
    delivery_attempts = Column(Integer, default=0)
    last_attempt = Column(DateTime, nullable=True)
    
    # Timing
    scheduled_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_user_status', 'user_id', 'status'),
        Index('idx_notification_school_type', 'school_id', 'notification_type'),
        Index('idx_notification_scheduled', 'scheduled_at'),
    )

class DeviceRegistration(Base):
    """Tracks user devices for push notifications and sync"""
    __tablename__ = "device_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    
    # User and school
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Device info
    device_type = Column(String, nullable=False)  # mobile, tablet, desktop
    platform = Column(String, nullable=False)  # ios, android, web
    app_version = Column(String, nullable=True)
    os_version = Column(String, nullable=True)
    
    # Push notification tokens
    fcm_token = Column(String, nullable=True)
    apns_token = Column(String, nullable=True)
    web_push_subscription = Column(JSON, nullable=True)
    
    # Sync settings
    sync_enabled = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)
    sync_settings = Column(JSON, default=dict)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_device_user_active', 'user_id', 'is_active'),
        Index('idx_device_school_platform', 'school_id', 'platform'),
        Index('idx_device_last_seen', 'last_seen'),
    )

class SyncConflict(Base):
    """Handles data conflicts during synchronization"""
    __tablename__ = "sync_conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    conflict_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Related sync record
    sync_record_id = Column(Integer, ForeignKey("sync_records.id"), nullable=False)
    
    # Conflict details
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    
    # Conflicting data
    local_data = Column(JSON, nullable=False)
    remote_data = Column(JSON, nullable=False)
    
    # Resolution
    resolution_strategy = Column(String, nullable=True)  # manual, auto_local, auto_remote
    resolved_data = Column(JSON, nullable=True)
    resolved_by = Column(Integer, nullable=True)  # User ID who resolved
    
    # Status
    is_resolved = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    sync_record = relationship("SyncRecord", backref="conflicts")

class MessageThread(Base):
    """Manages message threads and conversations"""
    __tablename__ = "message_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Thread details
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    thread_type = Column(String, nullable=False)  # chat, group, announcement
    
    # Participants
    participants = Column(JSON, nullable=False)  # List of user IDs
    created_by = Column(Integer, nullable=False)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Settings
    is_locked = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    allow_attachments = Column(Boolean, default=True)
    
    # Counters
    message_count = Column(Integer, default=0)
    participant_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_thread_school_type', 'school_id', 'thread_type'),
        Index('idx_thread_created_by', 'created_by'),
        Index('idx_thread_last_message', 'last_message_at'),
    )

class OfflineData(Base):
    """Stores data for offline access"""
    __tablename__ = "offline_data"
    
    id = Column(Integer, primary_key=True, index=True)
    data_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # User and device
    user_id = Column(Integer, nullable=False, index=True)
    device_id = Column(String, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Data details
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    
    # Caching
    cache_key = Column(String, nullable=False, index=True)
    cache_duration = Column(Integer, default=86400)  # 24 hours
    
    # Status
    is_encrypted = Column(Boolean, default=False)
    compression_type = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_offline_user_entity', 'user_id', 'entity_type'),
        Index('idx_offline_device_cache', 'device_id', 'cache_key'),
        Index('idx_offline_expires', 'expires_at'),
    )

class WebSocketConnection(Base):
    """Tracks active WebSocket connections"""
    __tablename__ = "websocket_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # User and device
    user_id = Column(Integer, nullable=False, index=True)
    device_id = Column(String, nullable=False)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Connection details
    socket_id = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_ping = Column(DateTime, nullable=True)
    
    # Subscriptions
    subscriptions = Column(JSON, default=list)  # List of channels/topics
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    disconnected_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_websocket_user_active', 'user_id', 'is_active'),
        Index('idx_websocket_school_active', 'school_id', 'is_active'),
        Index('idx_websocket_last_ping', 'last_ping'),
    )
