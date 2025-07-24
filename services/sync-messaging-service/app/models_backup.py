from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class SyncStatus(str, Enum):
    PENDING = "pending"
    SYNCED = "synced"
    COMPLETED = "completed"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    VOICE = "voice"
    VIDEO = "video"

class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class SyncRecord(Base):
    __tablename__ = "sync_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    entity_type = Column(String(50), nullable=False)  # message, notification, etc.
    entity_id = Column(Integer, nullable=False)
    operation = Column(String(20), nullable=False)  # create, update, delete
    sync_status = Column(String(20), default='pending')  # pending, synced, failed
    device_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    sync_data = Column(JSON)
    retry_count = Column(Integer, default=0)
    last_error = Column(Text)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default='text')  # text, image, file, system
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    message_metadata = Column(JSON)
    thread_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    room_type = Column(String(20), default='group')  # direct, group, study_group
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    max_participants = Column(Integer, default=50)
    settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatRoomMember(Base):
    __tablename__ = "chat_room_members"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(20), default='member')  # admin, moderator, member
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default='info')
    status = Column(String(20), default='pending')
    priority = Column(String(20), default='normal')
    data = Column(JSON)
    read_at = Column(DateTime)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class DeviceRegistration(Base):
    __tablename__ = "device_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String(255), unique=True, index=True)
    device_type = Column(String(50))
    push_token = Column(String(500))
    device_info = Column(JSON)
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class MessageThread(Base):
    __tablename__ = "message_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    thread_type = Column(String(50), default='direct')
    participants = Column(JSON)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class SyncConflict(Base):
    __tablename__ = "sync_conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    conflict_type = Column(String(50), nullable=False)
    local_version = Column(JSON)
    remote_version = Column(JSON)
    resolved = Column(Boolean, default=False)
    resolution_strategy = Column(String(50))
    resolved_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class OfflineData(Base):
    __tablename__ = "offline_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String(255))
    data_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime)

class WebSocketConnection(Base):
    __tablename__ = "websocket_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    connection_id = Column(String(255), unique=True)
    device_id = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_ping = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    content = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    is_read = Column(Boolean, default=False)
    notification_metadata = Column(JSON)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class DeviceRegistration(Base):
    __tablename__ = "device_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_token = Column(String(500), nullable=False)
    device_type = Column(String(20), nullable=False)  # ios, android, web
    device_info = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SyncConflict(Base):
    __tablename__ = "sync_conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    local_data = Column(JSON)
    server_data = Column(JSON)
    conflict_type = Column(String(50), nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class MessageThread(Base):
    __tablename__ = "message_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(100), unique=True, nullable=False)
    participants = Column(JSON)  # List of user IDs
    thread_type = Column(String(20), default='direct')  # direct, group
    last_message_id = Column(Integer, ForeignKey("messages.id"))
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OfflineData(Base):
    __tablename__ = "offline_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    data_type = Column(String(50), nullable=False)
    data_content = Column(JSON)
    operation = Column(String(20), nullable=False)  # create, update, delete
    is_synced = Column(Boolean, default=False)
    device_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime)

class WebSocketConnection(Base):
    __tablename__ = "websocket_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    connection_id = Column(String(100), unique=True, nullable=False)
    device_info = Column(JSON)
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    disconnected_at = Column(DateTime)
