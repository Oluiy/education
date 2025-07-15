"""
EduNerve File Storage Service - Database Models
Handles file storage in database with metadata, processing, and security
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, LargeBinary, JSON, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

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

class File(Base):
    """Main file storage table with binary data in database"""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # File metadata
    original_filename = Column(String, nullable=False)
    filename = Column(String, nullable=False)  # Sanitized filename
    content_type = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Binary data stored in database
    file_data = Column(LargeBinary, nullable=False)
    file_hash = Column(String, nullable=False, index=True)  # SHA256 hash for deduplication
    
    # Ownership and access
    uploaded_by = Column(Integer, nullable=False, index=True)  # User ID
    school_id = Column(Integer, nullable=False, index=True)
    access_level = Column(String, default=AccessLevel.PRIVATE)
    
    # Context and relationships
    entity_type = Column(String, nullable=True)  # content, quiz, user_avatar, etc.
    entity_id = Column(String, nullable=True)
    tags = Column(JSON, default=list)
    
    # Processing status
    status = Column(String, default=FileStatus.UPLOADING)
    processing_log = Column(JSON, default=dict)
    
    # Security
    is_encrypted = Column(Boolean, default=False)
    virus_scanned = Column(Boolean, default=False)
    scan_result = Column(String, nullable=True)
    
    # Metadata extracted from file
    metadata = Column(JSON, default=dict)  # EXIF, dimensions, duration, etc.
    extracted_text = Column(Text, nullable=True)  # OCR results
    
    # Usage tracking
    download_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_file_user_school', 'uploaded_by', 'school_id'),
        Index('idx_file_type_created', 'file_type', 'created_at'),
        Index('idx_file_entity', 'entity_type', 'entity_id'),
        Index('idx_file_hash_size', 'file_hash', 'file_size'),
    )

class FileVersion(Base):
    """File version history for tracking changes"""
    __tablename__ = "file_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Reference to main file
    file_id = Column(String, ForeignKey("files.file_id"), nullable=False)
    
    # Version details
    version_number = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_data = Column(LargeBinary, nullable=False)
    file_hash = Column(String, nullable=False)
    
    # Version metadata
    change_description = Column(Text, nullable=True)
    changed_by = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    file = relationship("File", backref="versions")
    
    # Indexes
    __table_args__ = (
        Index('idx_version_file_number', 'file_id', 'version_number'),
    )

class FileShare(Base):
    """File sharing and access control"""
    __tablename__ = "file_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # File reference
    file_id = Column(String, ForeignKey("files.file_id"), nullable=False)
    
    # Sharing details
    shared_by = Column(Integer, nullable=False)
    shared_with = Column(JSON, nullable=True)  # List of user IDs
    shared_with_groups = Column(JSON, nullable=True)  # Groups like "class_1", "teachers"
    
    # Access control
    can_download = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    
    # Link sharing
    public_link = Column(String, nullable=True, unique=True)
    link_password = Column(String, nullable=True)
    link_expires_at = Column(DateTime, nullable=True)
    link_max_downloads = Column(Integer, nullable=True)
    link_download_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationship
    file = relationship("File", backref="shares")
    
    # Indexes
    __table_args__ = (
        Index('idx_share_file_user', 'file_id', 'shared_by'),
        Index('idx_share_public_link', 'public_link'),
    )

class FileProcessingJob(Base):
    """Background file processing jobs"""
    __tablename__ = "file_processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # File reference
    file_id = Column(String, ForeignKey("files.file_id"), nullable=False)
    
    # Job details
    job_type = Column(String, nullable=False)  # resize, compress, ocr, thumbnail, etc.
    parameters = Column(JSON, default=dict)
    
    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    
    # Results
    output_data = Column(LargeBinary, nullable=True)  # Processed file data
    output_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    file = relationship("File", backref="processing_jobs")
    
    # Indexes
    __table_args__ = (
        Index('idx_job_file_type', 'file_id', 'job_type'),
        Index('idx_job_status_created', 'status', 'created_at'),
    )

class FileCollection(Base):
    """Collections/albums of files"""
    __tablename__ = "file_collections"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Collection details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    collection_type = Column(String, nullable=False)  # album, lesson, quiz, etc.
    
    # Ownership
    created_by = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Files in collection
    file_ids = Column(JSON, default=list)  # List of file IDs
    file_count = Column(Integer, default=0)
    total_size = Column(Integer, default=0)
    
    # Access control
    access_level = Column(String, default=AccessLevel.PRIVATE)
    shared_with = Column(JSON, default=list)
    
    # Settings
    settings = Column(JSON, default=dict)
    cover_file_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_collection_user_school', 'created_by', 'school_id'),
        Index('idx_collection_type_created', 'collection_type', 'created_at'),
    )

class FileAnalytics(Base):
    """File usage analytics and statistics"""
    __tablename__ = "file_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File reference
    file_id = Column(String, ForeignKey("files.file_id"), nullable=False)
    
    # User and context
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Action details
    action = Column(String, nullable=False)  # view, download, share, edit, delete
    context = Column(JSON, default=dict)  # Additional context data
    
    # Request details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    file = relationship("File", backref="analytics")
    
    # Indexes
    __table_args__ = (
        Index('idx_analytics_file_action', 'file_id', 'action'),
        Index('idx_analytics_user_created', 'user_id', 'created_at'),
        Index('idx_analytics_school_action', 'school_id', 'action'),
    )

class FileQuota(Base):
    """File storage quotas for users and schools"""
    __tablename__ = "file_quotas"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Entity (user or school)
    entity_type = Column(String, nullable=False)  # user, school
    entity_id = Column(Integer, nullable=False)
    
    # Quota limits (in bytes)
    total_quota = Column(Integer, nullable=False)
    used_quota = Column(Integer, default=0)
    file_count_limit = Column(Integer, nullable=True)
    file_count_used = Column(Integer, default=0)
    
    # File type specific limits
    quota_by_type = Column(JSON, default=dict)  # Per file type quotas
    
    # Settings
    auto_cleanup = Column(Boolean, default=False)
    warning_threshold = Column(Integer, default=80)  # Warning at 80% usage
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_quota_entity', 'entity_type', 'entity_id'),
    )

class FileBackup(Base):
    """File backup tracking"""
    __tablename__ = "file_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    backup_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Backup details
    backup_type = Column(String, nullable=False)  # full, incremental
    backup_location = Column(String, nullable=True)  # External backup location
    
    # Files included
    file_count = Column(Integer, default=0)
    total_size = Column(Integer, default=0)
    file_list = Column(JSON, default=list)  # List of backed up file IDs
    
    # Status
    status = Column(String, default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_backup_status_created', 'status', 'created_at'),
        Index('idx_backup_type_completed', 'backup_type', 'completed_at'),
    )
