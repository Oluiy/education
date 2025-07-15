"""
EduNerve Sync & Messaging Service - Pydantic Schemas
Data validation and serialization for API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums
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

# Base Response Models
class MessageResponse(BaseModel):
    message: str
    status: str = "success"

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    status: str = "error"

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# Sync Record Schemas
class SyncRecordBase(BaseModel):
    entity_type: str
    entity_id: str
    operation: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}
    priority: int = 1
    resolution_strategy: Optional[str] = None

class SyncRecordCreate(SyncRecordBase):
    user_id: int
    school_id: int
    device_id: str

class SyncRecordUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[SyncStatus] = None
    priority: Optional[int] = None
    resolution_strategy: Optional[str] = None

class SyncRecordResponse(SyncRecordBase):
    id: int
    sync_id: str
    user_id: int
    school_id: int
    device_id: str
    status: SyncStatus
    retry_count: int
    last_retry: Optional[datetime] = None
    conflict_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    message_type: MessageType
    subject: Optional[str] = None
    content: str
    recipient_ids: List[int]
    recipient_groups: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    thread_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class MessageCreate(MessageBase):
    sender_id: int
    sender_name: str
    sender_type: str
    school_id: int

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[MessageStatus] = None
    expires_at: Optional[datetime] = None

class MessageResponse(MessageBase):
    id: int
    message_id: str
    sender_id: int
    sender_name: str
    sender_type: str
    school_id: int
    status: MessageStatus
    delivery_status: Dict[str, Any]
    read_status: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationBase(BaseModel):
    title: str
    body: str
    notification_type: str
    category: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    actions: Optional[List[Dict[str, Any]]] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class NotificationCreate(NotificationBase):
    user_id: int
    school_id: int
    device_tokens: Optional[List[str]] = None

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    status: Optional[NotificationStatus] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    id: int
    notification_id: str
    user_id: int
    school_id: int
    device_tokens: Optional[List[str]] = None
    status: NotificationStatus
    delivery_attempts: int
    last_attempt: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Device Registration Schemas
class DeviceRegistrationBase(BaseModel):
    device_type: str
    platform: str
    app_version: Optional[str] = None
    os_version: Optional[str] = None
    fcm_token: Optional[str] = None
    apns_token: Optional[str] = None
    web_push_subscription: Optional[Dict[str, Any]] = None
    sync_enabled: bool = True
    sync_settings: Optional[Dict[str, Any]] = {}

class DeviceRegistrationCreate(DeviceRegistrationBase):
    device_id: str
    user_id: int
    school_id: int

class DeviceRegistrationUpdate(BaseModel):
    device_type: Optional[str] = None
    platform: Optional[str] = None
    app_version: Optional[str] = None
    os_version: Optional[str] = None
    fcm_token: Optional[str] = None
    apns_token: Optional[str] = None
    web_push_subscription: Optional[Dict[str, Any]] = None
    sync_enabled: Optional[bool] = None
    sync_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_online: Optional[bool] = None

class DeviceRegistrationResponse(DeviceRegistrationBase):
    id: int
    device_id: str
    user_id: int
    school_id: int
    is_active: bool
    is_online: bool
    last_sync: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Sync Conflict Schemas
class SyncConflictBase(BaseModel):
    entity_type: str
    entity_id: str
    local_data: Dict[str, Any]
    remote_data: Dict[str, Any]
    resolution_strategy: Optional[str] = None
    resolved_data: Optional[Dict[str, Any]] = None

class SyncConflictCreate(SyncConflictBase):
    sync_record_id: int

class SyncConflictUpdate(BaseModel):
    resolution_strategy: Optional[str] = None
    resolved_data: Optional[Dict[str, Any]] = None
    resolved_by: Optional[int] = None
    is_resolved: Optional[bool] = None

class SyncConflictResponse(SyncConflictBase):
    id: int
    conflict_id: str
    sync_record_id: int
    resolved_by: Optional[int] = None
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Message Thread Schemas
class MessageThreadBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thread_type: str
    participants: List[int]
    is_locked: bool = False
    is_private: bool = False
    allow_attachments: bool = True

class MessageThreadCreate(MessageThreadBase):
    created_by: int
    school_id: int

class MessageThreadUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    participants: Optional[List[int]] = None
    is_locked: Optional[bool] = None
    is_private: Optional[bool] = None
    allow_attachments: Optional[bool] = None

class MessageThreadResponse(MessageThreadBase):
    id: int
    thread_id: str
    created_by: int
    school_id: int
    message_count: int
    participant_count: int
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Offline Data Schemas
class OfflineDataBase(BaseModel):
    entity_type: str
    entity_id: str
    data: Dict[str, Any]
    cache_key: str
    cache_duration: int = 86400
    is_encrypted: bool = False
    compression_type: Optional[str] = None

class OfflineDataCreate(OfflineDataBase):
    user_id: int
    device_id: str
    school_id: int

class OfflineDataUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None
    cache_duration: Optional[int] = None
    expires_at: Optional[datetime] = None

class OfflineDataResponse(OfflineDataBase):
    id: int
    data_id: str
    user_id: int
    device_id: str
    school_id: int
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None

    class Config:
        from_attributes = True

# WebSocket Connection Schemas
class WebSocketConnectionBase(BaseModel):
    socket_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    subscriptions: List[str] = []

class WebSocketConnectionCreate(WebSocketConnectionBase):
    user_id: int
    device_id: str
    school_id: int

class WebSocketConnectionUpdate(BaseModel):
    is_active: Optional[bool] = None
    last_ping: Optional[datetime] = None
    subscriptions: Optional[List[str]] = None

class WebSocketConnectionResponse(WebSocketConnectionBase):
    id: int
    connection_id: str
    user_id: int
    device_id: str
    school_id: int
    is_active: bool
    last_ping: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    disconnected_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Bulk Operation Schemas
class BulkSyncRequest(BaseModel):
    sync_records: List[SyncRecordCreate]
    device_id: str
    user_id: int
    school_id: int

class BulkSyncResponse(BaseModel):
    successful: List[SyncRecordResponse]
    failed: List[Dict[str, Any]]
    conflicts: List[SyncConflictResponse]
    total: int
    processed: int

class BulkMessageRequest(BaseModel):
    messages: List[MessageCreate]
    thread_id: Optional[str] = None

class BulkMessageResponse(BaseModel):
    successful: List[MessageResponse]
    failed: List[Dict[str, Any]]
    total: int
    processed: int

# Sync Status Schemas
class SyncStatusRequest(BaseModel):
    device_id: str
    user_id: int
    school_id: int
    last_sync: Optional[datetime] = None

class SyncStatusResponse(BaseModel):
    pending_syncs: int
    conflicts: int
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    sync_enabled: bool
    offline_mode: bool

# Real-time Event Schemas
class RealTimeEvent(BaseModel):
    event_type: str
    data: Dict[str, Any]
    user_id: int
    school_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Statistics Schemas
class SyncStats(BaseModel):
    total_syncs: int
    pending_syncs: int
    completed_syncs: int
    failed_syncs: int
    conflicts: int
    average_sync_time: float
    last_sync: Optional[datetime] = None

class MessagingStats(BaseModel):
    total_messages: int
    sent_messages: int
    delivered_messages: int
    read_messages: int
    active_threads: int
    active_connections: int

class ServiceStats(BaseModel):
    sync_stats: SyncStats
    messaging_stats: MessagingStats
    active_devices: int
    offline_devices: int
    pending_notifications: int
