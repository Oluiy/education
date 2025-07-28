"""
File Storage Models for EduNerve Platform
File management, uploads, and media processing
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class FileType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    CODE = "code"
    OTHER = "other"

class FileStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    AVAILABLE = "available"
    FAILED = "failed"
    DELETED = "deleted"
    QUARANTINED = "quarantined"

class AccessLevel(str, Enum):
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"
    RESTRICTED = "restricted"

class StorageProvider(str, Enum):
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    CLOUDFLARE_R2 = "cloudflare_r2"

class File(Base):
    """Core file model"""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # File identification
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), index=True)  # SHA-256 hash
    
    # File metadata
    file_type = Column(String(20), default=FileType.OTHER.value)
    mime_type = Column(String(100))
    file_extension = Column(String(10))
    file_size = Column(BigInteger)  # Size in bytes
    
    # Storage details
    storage_provider = Column(String(50), default=StorageProvider.LOCAL.value)
    bucket_name = Column(String(100))
    storage_key = Column(String(500))  # Provider-specific key/path
    
    # URLs and access
    public_url = Column(String(500))
    signed_url = Column(String(1000))  # Temporary signed URL
    signed_url_expires_at = Column(DateTime)
    cdn_url = Column(String(500))  # CDN URL for faster access
    
    # Access control
    access_level = Column(String(20), default=AccessLevel.PRIVATE.value)
    is_public = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    
    # Processing status
    status = Column(String(20), default=FileStatus.UPLOADING.value)
    processing_progress = Column(Float, default=0.0)  # 0-100%
    
    # Media-specific metadata
    media_metadata = Column(JSON)  # Dimensions, duration, etc.
    thumbnail_url = Column(String(500))
    preview_url = Column(String(500))
    
    # Content classification
    tags = Column(JSON)  # User-defined tags
    categories = Column(JSON)  # System categories
    description = Column(Text)
    alt_text = Column(String(500))  # For accessibility
    
    # Usage tracking
    referenced_by = Column(JSON)  # List of entities using this file
    last_accessed_at = Column(DateTime)
    
    # Security and compliance
    is_scanned = Column(Boolean, default=False)
    scan_results = Column(JSON)  # Virus scan, content moderation results
    encryption_key_id = Column(String(100))
    
    # Versioning
    version = Column(Integer, default=1)
    parent_file_id = Column(Integer, ForeignKey("files.id"))
    
    # Timestamps
    upload_started_at = Column(DateTime, default=datetime.utcnow)
    upload_completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)  # Soft delete
    
    # Relationships
    parent_file = relationship("File", remote_side=[id])
    versions = relationship("File", remote_side=[parent_file_id])
    shares = relationship("FileShare", back_populates="file")
    processing_jobs = relationship("FileProcessingJob", back_populates="file")

class FileShare(Base):
    """File sharing and permissions"""
    __tablename__ = "file_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    shared_by_user_id = Column(Integer, ForeignKey("users.id"))
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Share details
    share_token = Column(String(100), unique=True, index=True)
    share_name = Column(String(200))
    
    # Permissions
    can_view = Column(Boolean, default=True)
    can_download = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    
    # Access control
    password_protected = Column(Boolean, default=False)
    password_hash = Column(String(128))
    max_downloads = Column(Integer)  # Null = unlimited
    download_count = Column(Integer, default=0)
    
    # Expiration
    expires_at = Column(DateTime)
    
    # Tracking
    last_accessed_at = Column(DateTime)
    access_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    file = relationship("File", back_populates="shares")

class FileFolder(Base):
    """File organization folders"""
    __tablename__ = "file_folders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    parent_folder_id = Column(Integer, ForeignKey("file_folders.id"))
    
    # Folder details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    icon = Column(String(100))  # Icon identifier
    
    # Organization
    path = Column(String(1000))  # Full folder path
    depth = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    
    # Permissions
    is_public = Column(Boolean, default=False)
    access_level = Column(String(20), default=AccessLevel.PRIVATE.value)
    
    # Statistics
    file_count = Column(Integer, default=0)
    total_size = Column(BigInteger, default=0)
    
    # Status
    is_system_folder = Column(Boolean, default=False)  # Default folders
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_folder = relationship("FileFolder", remote_side=[id])
    subfolders = relationship("FileFolder", remote_side=[parent_folder_id])
    folder_files = relationship("FileFolderMapping", back_populates="folder")

class FileFolderMapping(Base):
    """File to folder relationships"""
    __tablename__ = "file_folder_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    folder_id = Column(Integer, ForeignKey("file_folders.id"))
    
    # Position in folder
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    folder = relationship("FileFolder", back_populates="folder_files")

class FileProcessingJob(Base):
    """File processing and transformation jobs"""
    __tablename__ = "file_processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    
    # Job details
    job_type = Column(String(50))  # thumbnail, transcode, extract_text, etc.
    job_name = Column(String(200))
    processor = Column(String(50))  # ffmpeg, imagemagick, etc.
    
    # Job configuration
    input_parameters = Column(JSON)
    output_parameters = Column(JSON)
    processing_options = Column(JSON)
    
    # Status tracking
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    progress = Column(Float, default=0.0)  # 0-100%
    
    # Results
    output_file_id = Column(Integer, ForeignKey("files.id"))
    output_metadata = Column(JSON)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    processing_duration = Column(Integer)  # in seconds
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Resource usage
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    file = relationship("File", back_populates="processing_jobs", foreign_keys=[file_id])
    output_file = relationship("File", foreign_keys=[output_file_id])

class FileTemplate(Base):
    """File templates for common file types"""
    __tablename__ = "file_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # assignment, worksheet, etc.
    
    # Template file
    template_file_id = Column(Integer, ForeignKey("files.id"))
    preview_image_id = Column(Integer, ForeignKey("files.id"))
    
    # Template metadata
    file_type = Column(String(20))
    tags = Column(JSON)
    usage_instructions = Column(Text)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    
    # Status
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FileComment(Base):
    """Comments on files for collaboration"""
    __tablename__ = "file_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    parent_comment_id = Column(Integer, ForeignKey("file_comments.id"))
    
    # Comment content
    content = Column(Text, nullable=False)
    
    # Position (for image/video annotations)
    position_x = Column(Float)  # X coordinate (percentage)
    position_y = Column(Float)  # Y coordinate (percentage)
    timestamp = Column(Float)  # For video comments (seconds)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_by_user_id = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_comment = relationship("FileComment", remote_side=[id])
    replies = relationship("FileComment", remote_side=[parent_comment_id])

class FileAccessLog(Base):
    """File access logging for security and analytics"""
    __tablename__ = "file_access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Access details
    action = Column(String(50))  # view, download, upload, delete, share
    access_method = Column(String(50))  # web, api, mobile_app
    
    # Request context
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    referer = Column(String(500))
    
    # Results
    success = Column(Boolean, default=True)
    error_message = Column(String(500))
    response_size = Column(BigInteger)  # Bytes transferred
    
    # Performance
    processing_time = Column(Float)  # in seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)

class FileQuota(Base):
    """User file storage quotas"""
    __tablename__ = "file_quotas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Quota limits
    max_storage_bytes = Column(BigInteger, default=1073741824)  # 1GB default
    max_files = Column(Integer, default=1000)
    max_file_size_bytes = Column(BigInteger, default=104857600)  # 100MB default
    
    # Current usage
    used_storage_bytes = Column(BigInteger, default=0)
    file_count = Column(Integer, default=0)
    
    # Calculated fields
    storage_percentage = Column(Float, default=0.0)
    
    # Features
    can_share_publicly = Column(Boolean, default=True)
    can_use_cdn = Column(Boolean, default=True)
    max_share_expiry_days = Column(Integer, default=30)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
