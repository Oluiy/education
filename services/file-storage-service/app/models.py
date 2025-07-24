from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, BigInteger, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class FileStatus(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"

class FileType(enum.Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    OTHER = "other"

class AccessLevel(enum.Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100))
    file_hash = Column(String(64), unique=True)  # SHA-256 hash
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    description = Column(Text)
    tags = Column(String(500))
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FileVersion(Base):
    __tablename__ = "file_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_hash = Column(String(64))
    created_by = Column(Integer, ForeignKey("users.id"))
    change_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class FileAccess(Base):
    __tablename__ = "file_access"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    access_type = Column(String(20), default='read')  # read, write, delete
    granted_by = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FileShare(Base):
    __tablename__ = "file_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    shared_by = Column(Integer, ForeignKey("users.id"))
    share_token = Column(String(100), unique=True)
    share_type = Column(String(20), default='link')  # link, email, user
    expires_at = Column(DateTime)
    password_protected = Column(Boolean, default=False)
    password_hash = Column(String(128))
    download_limit = Column(Integer)
    download_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FileProcessingJob(Base):
    __tablename__ = "file_processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    job_type = Column(String(50), nullable=False)  # thumbnail, conversion, analysis
    status = Column(Enum(FileStatus), default=FileStatus.PROCESSING)
    progress = Column(Integer, default=0)
    result_data = Column(Text)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class FileCollection(Base):
    __tablename__ = "file_collections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class FileAnalytics(Base):
    __tablename__ = "file_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    event_type = Column(String(50), nullable=False)  # view, download, share
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class FileQuota(Base):
    __tablename__ = "file_quotas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_quota = Column(BigInteger, default=1073741824)  # 1GB default
    used_quota = Column(BigInteger, default=0)
    file_count_limit = Column(Integer, default=1000)
    current_file_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FileBackup(Base):
    __tablename__ = "file_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    backup_path = Column(String(500), nullable=False)
    backup_size = Column(BigInteger)
    backup_hash = Column(String(64))
    backup_type = Column(String(20), default='automatic')  # automatic, manual
    created_at = Column(DateTime, default=datetime.utcnow)
