"""
EduNerve File Storage Service - Core Business Logic
Handles file operations, processing, and management
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from typing import Optional, List, Dict, Any, BinaryIO
import hashlib
import magic
import os
import uuid
from datetime import datetime, timedelta
from PIL import Image
import io
import json
import asyncio
from cryptography.fernet import Fernet
import base64

from .models import (
    File, FileVersion, FileShare, FileProcessingJob, 
    FileCollection, FileAnalytics, FileQuota, FileBackup,
    FileStatus, FileType, AccessLevel
)
from .schemas import (
    FileUploadRequest, FileResponse, FileUpdateRequest,
    FileSearchRequest, FileShareRequest, ProcessingJobRequest,
    FileCollectionRequest, FileAnalyticsRequest, FileQuotaResponse
)
from .auth import CurrentUser, create_file_activity_log

class FileStorageService:
    """Core file storage service with database storage"""
    
    def __init__(self):
        self.encryption_key = os.getenv("ENCRYPTION_KEY", "").encode()
        self.cipher = Fernet(base64.urlsafe_b64encode(self.encryption_key.ljust(32)[:32])) if self.encryption_key else None
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "50485760"))  # 50MB
        self.allowed_types = os.getenv("ALLOWED_FILE_TYPES", "").split(",") if os.getenv("ALLOWED_FILE_TYPES") else []
    
    def _get_file_type(self, content_type: str) -> FileType:
        """Determine file type from content type"""
        if content_type.startswith("image/"):
            return FileType.IMAGE
        elif content_type.startswith("video/"):
            return FileType.VIDEO
        elif content_type.startswith("audio/"):
            return FileType.AUDIO
        elif content_type in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            return FileType.DOCUMENT
        elif content_type in ["application/zip", "application/x-rar-compressed", "application/x-7z-compressed"]:
            return FileType.ARCHIVE
        else:
            return FileType.OTHER
    
    def _calculate_file_hash(self, file_data: bytes) -> str:
        """Calculate SHA256 hash of file data"""
        return hashlib.sha256(file_data).hexdigest()
    
    def _encrypt_file_data(self, file_data: bytes) -> bytes:
        """Encrypt file data if encryption is enabled"""
        if self.cipher and os.getenv("ENCRYPTION_ENABLED", "True").lower() == "true":
            return self.cipher.encrypt(file_data)
        return file_data
    
    def _decrypt_file_data(self, encrypted_data: bytes, is_encrypted: bool) -> bytes:
        """Decrypt file data if it's encrypted"""
        if is_encrypted and self.cipher:
            return self.cipher.decrypt(encrypted_data)
        return encrypted_data
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path separators and dangerous characters
        safe_chars = "-_.() "
        sanitized = "".join(c for c in filename if c.isalnum() or c in safe_chars)
        return sanitized[:255]  # Limit length
    
    def _extract_metadata(self, file_data: bytes, content_type: str) -> Dict[str, Any]:
        """Extract metadata from file"""
        metadata = {
            "size": len(file_data),
            "content_type": content_type
        }
        
        try:
            if content_type.startswith("image/"):
                # Extract image metadata
                image = Image.open(io.BytesIO(file_data))
                metadata.update({
                    "width": image.width,
                    "height": image.height,
                    "format": image.format,
                    "mode": image.mode
                })
                
                # Extract EXIF data
                if hasattr(image, '_getexif') and image._getexif():
                    exif = image._getexif()
                    metadata["exif"] = {k: v for k, v in exif.items() if isinstance(v, (str, int, float))}
                    
        except Exception as e:
            metadata["extraction_error"] = str(e)
        
        return metadata
    
    async def upload_file(
        self,
        file: UploadFile,
        request: FileUploadRequest,
        current_user: CurrentUser,
        db: Session
    ) -> FileResponse:
        """Upload a file to database storage"""
        
        # Read file data
        file_data = await file.read()
        file_size = len(file_data)
        
        # Validate file size
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size {file_size} exceeds maximum allowed size {self.max_file_size}"
            )
        
        # Detect content type
        content_type = magic.from_buffer(file_data, mime=True)
        
        # Validate file type
        if self.allowed_types and content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {content_type} not allowed"
            )
        
        # Check quota
        await self._check_quota(current_user.id, current_user.school_id, file_size, db)
        
        # Check for duplicate files
        file_hash = self._calculate_file_hash(file_data)
        existing_file = db.query(File).filter(
            File.file_hash == file_hash,
            File.school_id == current_user.school_id,
            File.status != FileStatus.DELETED
        ).first()
        
        if existing_file:
            # Return existing file if identical
            return FileResponse.from_orm(existing_file)
        
        # Extract metadata
        metadata = self._extract_metadata(file_data, content_type)
        
        # Encrypt file data if needed
        encrypted_data = self._encrypt_file_data(file_data)
        is_encrypted = len(encrypted_data) != len(file_data)
        
        # Create file record
        file_record = File(
            file_id=str(uuid.uuid4()),
            original_filename=file.filename,
            filename=self._sanitize_filename(file.filename),
            content_type=content_type,
            file_type=self._get_file_type(content_type),
            file_size=file_size,
            file_data=encrypted_data,
            file_hash=file_hash,
            uploaded_by=current_user.id,
            school_id=current_user.school_id,
            access_level=request.access_level,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            tags=request.tags or [],
            status=FileStatus.UPLOADING,
            is_encrypted=is_encrypted,
            metadata=metadata,
            expires_at=request.expires_at
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        # Update quota
        await self._update_quota(current_user.id, current_user.school_id, file_size, 1, db)
        
        # Create activity log
        create_file_activity_log(
            db=db,
            file_id=file_record.file_id,
            user_id=current_user.id,
            action="upload",
            context={"school_id": current_user.school_id}
        )
        
        # Update status to completed
        file_record.status = FileStatus.COMPLETED
        db.commit()
        
        # Schedule background processing if needed
        if content_type.startswith("image/"):
            await self._schedule_image_processing(file_record.file_id, db)
        
        return FileResponse.from_orm(file_record)
    
    async def get_file(
        self,
        file_id: str,
        current_user: CurrentUser,
        db: Session
    ) -> FileResponse:
        """Get file metadata"""
        
        file_record = db.query(File).filter(
            File.file_id == file_id,
            File.status != FileStatus.DELETED
        ).first()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access
        if not current_user.can_access_file(
            file_record.uploaded_by,
            file_record.school_id,
            file_record.access_level
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update last accessed
        file_record.last_accessed = datetime.utcnow()
        db.commit()
        
        # Create activity log
        create_file_activity_log(
            db=db,
            file_id=file_id,
            user_id=current_user.id,
            action="view",
            context={"school_id": current_user.school_id}
        )
        
        return FileResponse.from_orm(file_record)
    
    async def download_file(
        self,
        file_id: str,
        current_user: CurrentUser,
        db: Session
    ) -> tuple[bytes, str, str]:
        """Download file data"""
        
        file_record = db.query(File).filter(
            File.file_id == file_id,
            File.status != FileStatus.DELETED
        ).first()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access
        if not current_user.can_access_file(
            file_record.uploaded_by,
            file_record.school_id,
            file_record.access_level
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Decrypt file data if needed
        file_data = self._decrypt_file_data(file_record.file_data, file_record.is_encrypted)
        
        # Update download count
        file_record.download_count += 1
        file_record.last_accessed = datetime.utcnow()
        db.commit()
        
        # Create activity log
        create_file_activity_log(
            db=db,
            file_id=file_id,
            user_id=current_user.id,
            action="download",
            context={"school_id": current_user.school_id}
        )
        
        return file_data, file_record.original_filename, file_record.content_type
    
    async def update_file(
        self,
        file_id: str,
        request: FileUpdateRequest,
        current_user: CurrentUser,
        db: Session
    ) -> FileResponse:
        """Update file metadata"""
        
        file_record = db.query(File).filter(
            File.file_id == file_id,
            File.status != FileStatus.DELETED
        ).first()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access
        if file_record.uploaded_by != current_user.id and not current_user.has_permission("file.write"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update fields
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "filename":
                value = self._sanitize_filename(value)
            setattr(file_record, field, value)
        
        file_record.updated_at = datetime.utcnow()
        db.commit()
        
        # Create activity log
        create_file_activity_log(
            db=db,
            file_id=file_id,
            user_id=current_user.id,
            action="update",
            context={"school_id": current_user.school_id, "changes": update_data}
        )
        
        return FileResponse.from_orm(file_record)
    
    async def delete_file(
        self,
        file_id: str,
        current_user: CurrentUser,
        db: Session
    ) -> Dict[str, str]:
        """Delete a file"""
        
        file_record = db.query(File).filter(
            File.file_id == file_id,
            File.status != FileStatus.DELETED
        ).first()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check access
        if file_record.uploaded_by != current_user.id and not current_user.has_permission("file.delete"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Soft delete
        file_record.status = FileStatus.DELETED
        file_record.updated_at = datetime.utcnow()
        db.commit()
        
        # Update quota
        await self._update_quota(current_user.id, current_user.school_id, -file_record.file_size, -1, db)
        
        # Create activity log
        create_file_activity_log(
            db=db,
            file_id=file_id,
            user_id=current_user.id,
            action="delete",
            context={"school_id": current_user.school_id}
        )
        
        return {"message": "File deleted successfully"}
    
    async def search_files(
        self,
        request: FileSearchRequest,
        current_user: CurrentUser,
        db: Session
    ) -> Dict[str, Any]:
        """Search files"""
        
        query = db.query(File).filter(
            File.school_id == current_user.school_id,
            File.status != FileStatus.DELETED
        )
        
        # Apply filters
        if request.query:
            query = query.filter(
                File.original_filename.ilike(f"%{request.query}%")
            )
        
        if request.file_type:
            query = query.filter(File.file_type == request.file_type)
        
        if request.entity_type:
            query = query.filter(File.entity_type == request.entity_type)
        
        if request.entity_id:
            query = query.filter(File.entity_id == request.entity_id)
        
        if request.tags:
            for tag in request.tags:
                query = query.filter(File.tags.contains([tag]))
        
        if request.uploaded_by:
            query = query.filter(File.uploaded_by == request.uploaded_by)
        
        if request.date_from:
            query = query.filter(File.created_at >= request.date_from)
        
        if request.date_to:
            query = query.filter(File.created_at <= request.date_to)
        
        if request.access_level:
            query = query.filter(File.access_level == request.access_level)
        
        # Apply access control
        if current_user.role != "admin":
            query = query.filter(
                (File.uploaded_by == current_user.id) |
                (File.access_level.in_(["public", "school"]))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        files = query.offset(request.offset).limit(request.limit).all()
        
        return {
            "files": [FileResponse.from_orm(file) for file in files],
            "total": total,
            "limit": request.limit,
            "offset": request.offset,
            "has_more": total > request.offset + request.limit
        }
    
    async def _check_quota(self, user_id: int, school_id: int, file_size: int, db: Session):
        """Check if user has quota for file upload"""
        
        # Get user quota
        user_quota = db.query(FileQuota).filter(
            FileQuota.entity_type == "user",
            FileQuota.entity_id == user_id
        ).first()
        
        if user_quota and user_quota.used_quota + file_size > user_quota.total_quota:
            raise HTTPException(
                status_code=413,
                detail="User quota exceeded"
            )
        
        # Get school quota
        school_quota = db.query(FileQuota).filter(
            FileQuota.entity_type == "school",
            FileQuota.entity_id == school_id
        ).first()
        
        if school_quota and school_quota.used_quota + file_size > school_quota.total_quota:
            raise HTTPException(
                status_code=413,
                detail="School quota exceeded"
            )
    
    async def _update_quota(self, user_id: int, school_id: int, size_change: int, count_change: int, db: Session):
        """Update quota usage"""
        
        # Update user quota
        user_quota = db.query(FileQuota).filter(
            FileQuota.entity_type == "user",
            FileQuota.entity_id == user_id
        ).first()
        
        if user_quota:
            user_quota.used_quota += size_change
            user_quota.file_count_used += count_change
            user_quota.updated_at = datetime.utcnow()
        
        # Update school quota
        school_quota = db.query(FileQuota).filter(
            FileQuota.entity_type == "school",
            FileQuota.entity_id == school_id
        ).first()
        
        if school_quota:
            school_quota.used_quota += size_change
            school_quota.file_count_used += count_change
            school_quota.updated_at = datetime.utcnow()
        
        db.commit()
    
    async def _schedule_image_processing(self, file_id: str, db: Session):
        """Schedule image processing job"""
        
        job = FileProcessingJob(
            job_id=str(uuid.uuid4()),
            file_id=file_id,
            job_type="image_processing",
            parameters={"generate_thumbnail": True, "optimize": True}
        )
        
        db.add(job)
        db.commit()

# Initialize service
file_service = FileStorageService()
