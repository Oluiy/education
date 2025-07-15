"""
EduNerve File Storage Service - Pydantic Schemas
Request/Response models for file storage operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"

class FileStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    DELETED = "deleted"

class AccessLevel(str, Enum):
    PUBLIC = "public"
    SCHOOL = "school"
    DEPARTMENT = "department"
    CLASS = "class"
    PRIVATE = "private"

# === FILE SCHEMAS ===

class FileUploadRequest(BaseModel):
    """File upload request"""
    entity_type: Optional[str] = Field(None, description="Type of entity (content, quiz, user_avatar)")
    entity_id: Optional[str] = Field(None, description="ID of the entity")
    access_level: AccessLevel = Field(AccessLevel.PRIVATE, description="Access level")
    tags: Optional[List[str]] = Field(default_factory=list, description="File tags")
    description: Optional[str] = Field(None, description="File description")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")

class FileResponse(BaseModel):
    """File response model"""
    id: int
    file_id: str
    original_filename: str
    filename: str
    content_type: str
    file_type: str
    file_size: int
    file_hash: str
    uploaded_by: int
    school_id: int
    access_level: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    tags: List[str]
    status: str
    processing_log: Dict[str, Any]
    is_encrypted: bool
    virus_scanned: bool
    scan_result: Optional[str]
    metadata: Dict[str, Any]
    extracted_text: Optional[str]
    download_count: int
    last_accessed: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class FileUpdateRequest(BaseModel):
    """File update request"""
    filename: Optional[str] = Field(None, description="New filename")
    access_level: Optional[AccessLevel] = Field(None, description="New access level")
    tags: Optional[List[str]] = Field(None, description="New tags")
    description: Optional[str] = Field(None, description="New description")
    expires_at: Optional[datetime] = Field(None, description="New expiration date")

class FileSearchRequest(BaseModel):
    """File search request"""
    query: Optional[str] = Field(None, description="Search query")
    file_type: Optional[FileType] = Field(None, description="Filter by file type")
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    entity_id: Optional[str] = Field(None, description="Filter by entity ID")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    uploaded_by: Optional[int] = Field(None, description="Filter by uploader")
    date_from: Optional[datetime] = Field(None, description="Date range start")
    date_to: Optional[datetime] = Field(None, description="Date range end")
    access_level: Optional[AccessLevel] = Field(None, description="Filter by access level")
    limit: int = Field(20, ge=1, le=100, description="Number of results")
    offset: int = Field(0, ge=0, description="Results offset")

class FileSearchResponse(BaseModel):
    """File search response"""
    files: List[FileResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

# === FILE PROCESSING SCHEMAS ===

class ProcessingJobRequest(BaseModel):
    """File processing job request"""
    job_type: str = Field(..., description="Type of processing job")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Job parameters")

class ProcessingJobResponse(BaseModel):
    """Processing job response"""
    id: int
    job_id: str
    file_id: str
    job_type: str
    parameters: Dict[str, Any]
    status: str
    progress: int
    error_message: Optional[str]
    output_metadata: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# === FILE SHARING SCHEMAS ===

class FileShareRequest(BaseModel):
    """File sharing request"""
    shared_with: Optional[List[int]] = Field(None, description="List of user IDs")
    shared_with_groups: Optional[List[str]] = Field(None, description="List of groups")
    can_download: bool = Field(True, description="Allow download")
    can_edit: bool = Field(False, description="Allow edit")
    can_delete: bool = Field(False, description="Allow delete")
    can_share: bool = Field(False, description="Allow sharing")
    expires_at: Optional[datetime] = Field(None, description="Share expiration")

class PublicLinkRequest(BaseModel):
    """Public link creation request"""
    link_password: Optional[str] = Field(None, description="Link password")
    expires_at: Optional[datetime] = Field(None, description="Link expiration")
    max_downloads: Optional[int] = Field(None, description="Maximum downloads")

class FileShareResponse(BaseModel):
    """File share response"""
    id: int
    share_id: str
    file_id: str
    shared_by: int
    shared_with: Optional[List[int]]
    shared_with_groups: Optional[List[str]]
    can_download: bool
    can_edit: bool
    can_delete: bool
    can_share: bool
    public_link: Optional[str]
    link_expires_at: Optional[datetime]
    link_max_downloads: Optional[int]
    link_download_count: int
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# === FILE COLLECTION SCHEMAS ===

class FileCollectionRequest(BaseModel):
    """File collection creation request"""
    name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    collection_type: str = Field(..., description="Collection type")
    file_ids: List[str] = Field(default_factory=list, description="Initial file IDs")
    access_level: AccessLevel = Field(AccessLevel.PRIVATE, description="Access level")
    shared_with: Optional[List[int]] = Field(None, description="Users to share with")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Collection settings")
    cover_file_id: Optional[str] = Field(None, description="Cover file ID")

class FileCollectionResponse(BaseModel):
    """File collection response"""
    id: int
    collection_id: str
    name: str
    description: Optional[str]
    collection_type: str
    created_by: int
    school_id: int
    file_ids: List[str]
    file_count: int
    total_size: int
    access_level: str
    shared_with: List[int]
    settings: Dict[str, Any]
    cover_file_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FileCollectionUpdateRequest(BaseModel):
    """File collection update request"""
    name: Optional[str] = Field(None, description="New name")
    description: Optional[str] = Field(None, description="New description")
    add_files: Optional[List[str]] = Field(None, description="Files to add")
    remove_files: Optional[List[str]] = Field(None, description="Files to remove")
    access_level: Optional[AccessLevel] = Field(None, description="New access level")
    shared_with: Optional[List[int]] = Field(None, description="New sharing list")
    settings: Optional[Dict[str, Any]] = Field(None, description="New settings")
    cover_file_id: Optional[str] = Field(None, description="New cover file")

# === FILE ANALYTICS SCHEMAS ===

class FileAnalyticsRequest(BaseModel):
    """File analytics request"""
    file_ids: Optional[List[str]] = Field(None, description="Specific file IDs")
    user_id: Optional[int] = Field(None, description="Filter by user")
    date_from: Optional[datetime] = Field(None, description="Date range start")
    date_to: Optional[datetime] = Field(None, description="Date range end")
    action: Optional[str] = Field(None, description="Filter by action")
    group_by: Optional[str] = Field("day", description="Group by period")

class FileAnalyticsResponse(BaseModel):
    """File analytics response"""
    total_files: int
    total_size: int
    download_count: int
    view_count: int
    share_count: int
    file_types: Dict[str, int]
    top_files: List[Dict[str, Any]]
    usage_trends: List[Dict[str, Any]]
    storage_usage: Dict[str, Any]

# === FILE QUOTA SCHEMAS ===

class FileQuotaResponse(BaseModel):
    """File quota response"""
    id: int
    entity_type: str
    entity_id: int
    total_quota: int
    used_quota: int
    file_count_limit: Optional[int]
    file_count_used: int
    quota_by_type: Dict[str, int]
    usage_percentage: float
    auto_cleanup: bool
    warning_threshold: int
    created_at: datetime
    updated_at: datetime
    
    @validator('usage_percentage', pre=True, always=True)
    def calculate_usage_percentage(cls, v, values):
        if 'used_quota' in values and 'total_quota' in values:
            return (values['used_quota'] / values['total_quota']) * 100 if values['total_quota'] > 0 else 0
        return v
    
    class Config:
        from_attributes = True

class FileQuotaUpdateRequest(BaseModel):
    """File quota update request"""
    total_quota: Optional[int] = Field(None, description="New total quota")
    file_count_limit: Optional[int] = Field(None, description="New file count limit")
    quota_by_type: Optional[Dict[str, int]] = Field(None, description="New quota by type")
    auto_cleanup: Optional[bool] = Field(None, description="Enable auto cleanup")
    warning_threshold: Optional[int] = Field(None, description="Warning threshold")

# === BULK OPERATIONS SCHEMAS ===

class BulkFileOperation(BaseModel):
    """Bulk file operation request"""
    file_ids: List[str] = Field(..., description="List of file IDs")
    operation: str = Field(..., description="Operation type")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")

class BulkFileOperationResponse(BaseModel):
    """Bulk file operation response"""
    operation_id: str
    total_files: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]]
    results: List[Dict[str, Any]]

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
