"""
Admin Service Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums
class SystemRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    PRINCIPAL = "principal"
    VICE_PRINCIPAL = "vice_principal"
    DEPARTMENT_HEAD = "department_head"
    COORDINATOR = "coordinator"

class AlertType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Admin User Schemas
class AdminUserCreate(BaseModel):
    user_id: int
    school_id: int
    system_role: SystemRole = SystemRole.SCHOOL_ADMIN
    permissions: Optional[Dict[str, Any]] = None
    departments: Optional[List[str]] = None
    employee_id: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None

class AdminUserUpdate(BaseModel):
    system_role: Optional[SystemRole] = None
    permissions: Optional[Dict[str, Any]] = None
    departments: Optional[List[str]] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class AdminUserResponse(BaseModel):
    id: int
    user_id: int
    school_id: int
    system_role: SystemRole
    permissions: Optional[Dict[str, Any]]
    departments: Optional[List[str]]
    employee_id: Optional[str]
    job_title: Optional[str]
    phone: Optional[str]
    emergency_contact: Optional[Dict[str, Any]]
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# School Schemas
class SchoolCreate(BaseModel):
    school_id: int
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    principal_name: Optional[str] = None
    principal_email: Optional[EmailStr] = None
    established_date: Optional[datetime] = None
    school_type: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    features_enabled: Optional[Dict[str, Any]] = None
    subscription_tier: str = "basic"

class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    principal_name: Optional[str] = None
    principal_email: Optional[EmailStr] = None
    established_date: Optional[datetime] = None
    school_type: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    features_enabled: Optional[Dict[str, Any]] = None
    subscription_tier: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class SchoolResponse(BaseModel):
    id: int
    school_id: int
    name: str
    code: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    principal_name: Optional[str]
    principal_email: Optional[str]
    established_date: Optional[datetime]
    school_type: Optional[str]
    settings: Optional[Dict[str, Any]]
    features_enabled: Optional[Dict[str, Any]]
    subscription_tier: str
    total_students: int
    total_teachers: int
    total_classes: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Department Schemas
class DepartmentCreate(BaseModel):
    school_id: int
    name: str
    code: str
    description: Optional[str] = None
    head_user_id: Optional[int] = None
    head_name: Optional[str] = None
    head_email: Optional[EmailStr] = None
    budget: Optional[float] = None
    settings: Optional[Dict[str, Any]] = None

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    head_user_id: Optional[int] = None
    head_name: Optional[str] = None
    head_email: Optional[EmailStr] = None
    budget: Optional[float] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class DepartmentResponse(BaseModel):
    id: int
    school_id: int
    name: str
    code: str
    description: Optional[str]
    head_user_id: Optional[int]
    head_name: Optional[str]
    head_email: Optional[str]
    budget: Optional[float]
    settings: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Audit Log Schemas
class AuditLogCreate(BaseModel):
    school_id: int
    admin_user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_url: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    school_id: int
    admin_user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_method: Optional[str]
    request_url: Optional[str]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    success: bool
    error_message: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

# Report Schemas
class ReportCreate(BaseModel):
    school_id: int
    title: str
    description: Optional[str] = None
    report_type: str
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    file_format: str = "pdf"

class ReportResponse(BaseModel):
    id: int
    school_id: int
    created_by_admin_id: int
    title: str
    description: Optional[str]
    report_type: str
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]
    filters: Optional[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]
    file_path: Optional[str]
    file_format: str
    file_size: Optional[int]
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

# System Alert Schemas
class SystemAlertCreate(BaseModel):
    school_id: Optional[int] = None
    title: str
    message: str
    alert_type: AlertType = AlertType.INFO
    severity: str = "medium"
    target_roles: Optional[List[str]] = None
    target_users: Optional[List[int]] = None
    is_dismissible: bool = True
    auto_dismiss_after: Optional[int] = None
    is_system_wide: bool = False
    expires_at: Optional[datetime] = None

class SystemAlertResponse(BaseModel):
    id: int
    school_id: Optional[int]
    title: str
    message: str
    alert_type: AlertType
    severity: str
    target_roles: Optional[List[str]]
    target_users: Optional[List[int]]
    is_dismissible: bool
    auto_dismiss_after: Optional[int]
    is_active: bool
    is_system_wide: bool
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

# Background Task Schemas
class BackgroundTaskCreate(BaseModel):
    school_id: int
    task_type: str
    task_name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class BackgroundTaskResponse(BaseModel):
    id: int
    school_id: int
    created_by_admin_id: int
    task_id: str
    task_type: str
    task_name: str
    description: Optional[str]
    parameters: Optional[Dict[str, Any]]
    status: str
    progress: int
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

# Data Export Schemas
class DataExportCreate(BaseModel):
    school_id: int
    export_type: str
    file_format: str = "csv"
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None

class DataExportResponse(BaseModel):
    id: int
    school_id: int
    requested_by_admin_id: int
    export_type: str
    file_format: str
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]
    filters: Optional[Dict[str, Any]]
    file_path: Optional[str]
    file_size: Optional[int]
    download_count: int
    status: str
    progress: int
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

# System Config Schemas
class SystemConfigCreate(BaseModel):
    key: str
    value: Any
    description: Optional[str] = None
    is_public: bool = False
    is_required: bool = False
    data_type: str = "string"

class SystemConfigUpdate(BaseModel):
    value: Optional[Any] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_required: Optional[bool] = None

class SystemConfigResponse(BaseModel):
    id: int
    key: str
    value: Any
    description: Optional[str]
    is_public: bool
    is_required: bool
    data_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Analytics Schemas
class AnalyticsRequest(BaseModel):
    school_id: int
    metric_type: str
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None
    group_by: Optional[str] = None

class AnalyticsResponse(BaseModel):
    metric_type: str
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    generated_at: datetime

# Dashboard Schemas
class DashboardStats(BaseModel):
    school_id: int
    total_users: int
    total_students: int
    total_teachers: int
    total_classes: int
    total_subjects: int
    active_sessions: int
    recent_activities: List[Dict[str, Any]]
    system_health: Dict[str, Any]
    alerts_count: int
    pending_tasks: int

# Utility Schemas
class MessageResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class BulkOperationResponse(BaseModel):
    total_processed: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]]
