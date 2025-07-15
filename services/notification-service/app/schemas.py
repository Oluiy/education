"""
EduNerve Notification Service - Pydantic Schemas
Request/Response models for notification operations
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, time
from enum import Enum
import phonenumbers

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

# === NOTIFICATION RECIPIENT SCHEMAS ===

class NotificationRecipientBase(BaseModel):
    """Base recipient model"""
    user_id: Optional[int] = Field(None, description="User ID if registered user")
    recipient_type: RecipientType = Field(..., description="Type of recipient")
    name: str = Field(..., description="Recipient name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    whatsapp_number: Optional[str] = Field(None, description="WhatsApp number")
    push_token: Optional[str] = Field(None, description="Push notification token")
    language: str = Field("en", description="Preferred language")
    timezone: str = Field("UTC", description="Timezone")

    @validator('phone', 'whatsapp_number')
    def validate_phone_number(cls, v):
        if v:
            try:
                parsed = phonenumbers.parse(v, None)
                if not phonenumbers.is_valid_number(parsed):
                    raise ValueError('Invalid phone number')
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            except phonenumbers.NumberParseException:
                raise ValueError('Invalid phone number format')
        return v

class NotificationRecipientCreate(NotificationRecipientBase):
    """Create recipient model"""
    pass

class NotificationRecipientResponse(NotificationRecipientBase):
    """Recipient response model"""
    id: int
    recipient_id: str
    notification_id: str
    status: NotificationStatus
    delivery_attempts: int
    last_attempt: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    failed_reason: Optional[str]
    external_id: Optional[str]
    provider_response: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# === NOTIFICATION SCHEMAS ===

class NotificationBase(BaseModel):
    """Base notification model"""
    notification_type: NotificationType = Field(..., description="Type of notification")
    subject: Optional[str] = Field(None, description="Notification subject")
    message: str = Field(..., description="Notification message")
    html_message: Optional[str] = Field(None, description="HTML message content")
    sender_name: Optional[str] = Field(None, description="Sender name")
    sender_type: str = Field("system", description="Sender type")
    priority: NotificationPriority = Field(NotificationPriority.NORMAL, description="Priority level")
    category: Optional[str] = Field(None, description="Notification category")
    template_id: Optional[str] = Field(None, description="Template ID")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Template data")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled send time")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="Attachments")

class NotificationCreate(NotificationBase):
    """Create notification model"""
    recipients: List[NotificationRecipientCreate] = Field(..., description="List of recipients")

class NotificationUpdate(BaseModel):
    """Update notification model"""
    subject: Optional[str] = Field(None, description="New subject")
    message: Optional[str] = Field(None, description="New message")
    html_message: Optional[str] = Field(None, description="New HTML message")
    priority: Optional[NotificationPriority] = Field(None, description="New priority")
    scheduled_at: Optional[datetime] = Field(None, description="New scheduled time")
    expires_at: Optional[datetime] = Field(None, description="New expiration time")
    status: Optional[NotificationStatus] = Field(None, description="New status")

class NotificationResponse(NotificationBase):
    """Notification response model"""
    id: int
    notification_id: str
    sender_id: Optional[int]
    school_id: int
    status: NotificationStatus
    retry_count: int
    last_retry: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    recipients: List[NotificationRecipientResponse]

    class Config:
        from_attributes = True

# === QUICK NOTIFICATION SCHEMAS ===

class QuickNotificationRequest(BaseModel):
    """Quick notification for simple use cases"""
    type: NotificationType = Field(..., description="Notification type")
    recipients: List[str] = Field(..., description="List of emails/phones/user IDs")
    subject: Optional[str] = Field(None, description="Subject")
    message: str = Field(..., description="Message")
    priority: NotificationPriority = Field(NotificationPriority.NORMAL, description="Priority")
    school_id: Optional[int] = Field(None, description="School ID")
    
class BulkNotificationRequest(BaseModel):
    """Bulk notification request"""
    type: NotificationType = Field(..., description="Notification type")
    subject: Optional[str] = Field(None, description="Subject")
    message: str = Field(..., description="Message")
    template_id: Optional[str] = Field(None, description="Template ID")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Template data")
    target_audience: Dict[str, Any] = Field(..., description="Target audience criteria")
    priority: NotificationPriority = Field(NotificationPriority.NORMAL, description="Priority")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled time")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")

# === TEMPLATE SCHEMAS ===

class NotificationTemplateBase(BaseModel):
    """Base template model"""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    template_type: NotificationType = Field(..., description="Template type")
    subject_template: Optional[str] = Field(None, description="Subject template")
    message_template: str = Field(..., description="Message template")
    html_template: Optional[str] = Field(None, description="HTML template")
    language: str = Field("en", description="Template language")
    translations: Optional[Dict[str, Dict[str, str]]] = Field(None, description="Translations")
    variables: Optional[List[str]] = Field(None, description="Template variables")
    category: Optional[str] = Field(None, description="Template category")

class NotificationTemplateCreate(NotificationTemplateBase):
    """Create template model"""
    pass

class NotificationTemplateUpdate(BaseModel):
    """Update template model"""
    name: Optional[str] = Field(None, description="New name")
    description: Optional[str] = Field(None, description="New description")
    subject_template: Optional[str] = Field(None, description="New subject template")
    message_template: Optional[str] = Field(None, description="New message template")
    html_template: Optional[str] = Field(None, description="New HTML template")
    translations: Optional[Dict[str, Dict[str, str]]] = Field(None, description="New translations")
    variables: Optional[List[str]] = Field(None, description="New variables")
    is_active: Optional[bool] = Field(None, description="Active status")

class NotificationTemplateResponse(NotificationTemplateBase):
    """Template response model"""
    id: int
    template_id: str
    school_id: Optional[int]
    is_system_template: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# === SETTINGS SCHEMAS ===

class NotificationSettingsBase(BaseModel):
    """Base settings model"""
    email_enabled: bool = Field(True, description="Enable email notifications")
    sms_enabled: bool = Field(True, description="Enable SMS notifications")
    whatsapp_enabled: bool = Field(True, description="Enable WhatsApp notifications")
    push_enabled: bool = Field(True, description="Enable push notifications")
    voice_enabled: bool = Field(False, description="Enable voice notifications")
    academic_notifications: bool = Field(True, description="Enable academic notifications")
    administrative_notifications: bool = Field(True, description="Enable administrative notifications")
    emergency_notifications: bool = Field(True, description="Enable emergency notifications")
    marketing_notifications: bool = Field(False, description="Enable marketing notifications")
    quiet_hours_start: Optional[str] = Field(None, description="Quiet hours start (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Quiet hours end (HH:MM)")
    timezone: str = Field("UTC", description="User timezone")
    language: str = Field("en", description="Preferred language")
    auto_translate: bool = Field(True, description="Auto-translate messages")
    digest_mode: bool = Field(False, description="Enable digest mode")
    digest_frequency: str = Field("daily", description="Digest frequency")

    @validator('quiet_hours_start', 'quiet_hours_end')
    def validate_time_format(cls, v):
        if v:
            try:
                time.fromisoformat(v)
            except ValueError:
                raise ValueError('Invalid time format, use HH:MM')
        return v

class NotificationSettingsUpdate(NotificationSettingsBase):
    """Update settings model"""
    pass

class NotificationSettingsResponse(NotificationSettingsBase):
    """Settings response model"""
    id: int
    user_id: int
    school_id: int
    user_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# === CONTACT SCHEMAS ===

class NotificationContactBase(BaseModel):
    """Base contact model"""
    contact_type: str = Field(..., description="Contact type")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    whatsapp_number: Optional[str] = Field(None, description="WhatsApp number")
    is_primary: bool = Field(False, description="Primary contact")
    is_active: bool = Field(True, description="Active status")

class NotificationContactCreate(NotificationContactBase):
    """Create contact model"""
    pass

class NotificationContactUpdate(BaseModel):
    """Update contact model"""
    contact_type: Optional[str] = Field(None, description="Contact type")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    whatsapp_number: Optional[str] = Field(None, description="WhatsApp number")
    is_primary: Optional[bool] = Field(None, description="Primary contact")
    is_active: Optional[bool] = Field(None, description="Active status")

class NotificationContactResponse(NotificationContactBase):
    """Contact response model"""
    id: int
    contact_id: str
    user_id: int
    school_id: int
    email_verified: bool
    phone_verified: bool
    whatsapp_verified: bool
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime]

    class Config:
        from_attributes = True

# === ANALYTICS SCHEMAS ===

class NotificationAnalyticsRequest(BaseModel):
    """Analytics request model"""
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    notification_type: Optional[NotificationType] = Field(None, description="Filter by type")
    school_id: Optional[int] = Field(None, description="Filter by school")
    group_by: str = Field("day", description="Group by period")

class NotificationAnalyticsResponse(BaseModel):
    """Analytics response model"""
    total_sent: int
    total_delivered: int
    total_read: int
    total_failed: int
    delivery_rate: float
    read_rate: float
    failure_rate: float
    by_type: Dict[str, int]
    by_priority: Dict[str, int]
    by_status: Dict[str, int]
    trends: List[Dict[str, Any]]
    avg_delivery_time: float
    avg_read_time: float
    cost_summary: Optional[Dict[str, Any]]

# === WEBHOOK SCHEMAS ===

class WebhookEvent(BaseModel):
    """Webhook event model"""
    event_type: str = Field(..., description="Event type")
    notification_id: str = Field(..., description="Notification ID")
    recipient_id: Optional[str] = Field(None, description="Recipient ID")
    status: str = Field(..., description="Status")
    timestamp: datetime = Field(..., description="Event timestamp")
    provider: str = Field(..., description="Provider name")
    provider_data: Optional[Dict[str, Any]] = Field(None, description="Provider data")

# === BULK OPERATION SCHEMAS ===

class BulkNotificationResponse(BaseModel):
    """Bulk notification response"""
    campaign_id: str
    name: str
    description: Optional[str]
    created_by: int
    school_id: int
    notification_type: str
    status: str
    estimated_recipients: int
    actual_recipients: int
    progress: int
    sent_count: int
    delivered_count: int
    failed_count: int
    created_at: datetime
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

# === SEARCH AND FILTER SCHEMAS ===

class NotificationSearchRequest(BaseModel):
    """Notification search request"""
    query: Optional[str] = Field(None, description="Search query")
    notification_type: Optional[NotificationType] = Field(None, description="Filter by type")
    status: Optional[NotificationStatus] = Field(None, description="Filter by status")
    priority: Optional[NotificationPriority] = Field(None, description="Filter by priority")
    sender_id: Optional[int] = Field(None, description="Filter by sender")
    date_from: Optional[datetime] = Field(None, description="Date from")
    date_to: Optional[datetime] = Field(None, description="Date to")
    limit: int = Field(20, ge=1, le=100, description="Results limit")
    offset: int = Field(0, ge=0, description="Results offset")

class NotificationSearchResponse(BaseModel):
    """Notification search response"""
    notifications: List[NotificationResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

# === COMMON SCHEMAS ===

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

# === DELIVERY STATUS SCHEMAS ===

class DeliveryStatusResponse(BaseModel):
    """Delivery status response"""
    notification_id: str
    total_recipients: int
    sent: int
    delivered: int
    read: int
    failed: int
    pending: int
    delivery_rate: float
    read_rate: float
    failure_rate: float
    last_updated: datetime
