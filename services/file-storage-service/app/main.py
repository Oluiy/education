"""
EduNerve File Storage Service - Main FastAPI Application
Database-based file storage with processing, security, and management
"""

from fastapi import FastAPI, HTTPException, Request, Depends, Query, UploadFile, File as FastAPIFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uvicorn
import os
import logging
import io
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from .database import create_tables, get_db
from .models import File, FileShare, FileCollection, FileQuota, FileAnalytics
from .schemas import (
    FileUploadRequest, FileResponse, FileUpdateRequest, FileSearchRequest,
    FileShareRequest, FileShareResponse, FileCollectionRequest, FileCollectionResponse,
    FileAnalyticsRequest, FileAnalyticsResponse, FileQuotaResponse,
    MessageResponse, ErrorResponse, BulkFileOperation, BulkFileOperationResponse
)
from .auth import get_current_user, get_current_teacher, get_current_admin, CurrentUser
from .file_service import file_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting EduNerve File Storage Service...")
    
    # Create database tables
    create_tables()
    logger.info("✅ Database tables created successfully")
    
    # Create required directories
    os.makedirs("temp", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    
    logger.info("✅ File Storage Service startup complete")
    yield
    
    # Shutdown
    logger.info("🔽 Shutting down File Storage Service...")
    logger.info("✅ File Storage Service shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="EduNerve File Storage Service",
    description="Database-based file storage with processing, security, and management",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "file-storage-service"}

# === FILE UPLOAD ENDPOINTS ===

@app.post("/api/v1/files/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    access_level: str = Query("private"),
    tags: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a single file"""
    try:
        # Parse tags
        tag_list = tags.split(",") if tags else []
        
        # Create upload request
        upload_request = FileUploadRequest(
            entity_type=entity_type,
            entity_id=entity_id,
            access_level=access_level,
            tags=tag_list,
            description=description
        )
        
        # Upload file
        file_response = await file_service.upload_file(
            file=file,
            request=upload_request,
            current_user=current_user,
            db=db
        )
        
        return file_response
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

@app.post("/api/v1/files/upload-multiple", response_model=List[FileResponse])
async def upload_multiple_files(
    files: List[UploadFile] = FastAPIFile(...),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    access_level: str = Query("private"),
    tags: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload multiple files"""
    try:
        # Check file count limit
        max_files = int(os.getenv("MAX_BULK_FILES", "10"))
        if len(files) > max_files:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {max_files} files allowed per upload"
            )
        
        # Parse tags
        tag_list = tags.split(",") if tags else []
        
        # Create upload request
        upload_request = FileUploadRequest(
            entity_type=entity_type,
            entity_id=entity_id,
            access_level=access_level,
            tags=tag_list
        )
        
        # Upload files
        uploaded_files = []
        for file in files:
            try:
                file_response = await file_service.upload_file(
                    file=file,
                    request=upload_request,
                    current_user=current_user,
                    db=db
                )
                uploaded_files.append(file_response)
            except Exception as e:
                logger.error(f"Error uploading file {file.filename}: {str(e)}")
                # Continue with other files
        
        return uploaded_files
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading multiple files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload files")

# === FILE MANAGEMENT ENDPOINTS ===

@app.get("/api/v1/files/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file metadata"""
    try:
        return await file_service.get_file(file_id, current_user, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get file")

@app.get("/api/v1/files/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download file"""
    try:
        file_data, filename, content_type = await file_service.download_file(
            file_id, current_user, db
        )
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download file")

@app.put("/api/v1/files/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: str,
    request: FileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update file metadata"""
    try:
        return await file_service.update_file(file_id, request, current_user, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update file")

@app.delete("/api/v1/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete file"""
    try:
        return await file_service.delete_file(file_id, current_user, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete file")

# === FILE SEARCH ENDPOINTS ===

@app.post("/api/v1/files/search")
async def search_files(
    request: FileSearchRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search files"""
    try:
        return await file_service.search_files(request, current_user, db)
    except Exception as e:
        logger.error(f"Error searching files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search files")

@app.get("/api/v1/files")
async def list_files(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List files with filters"""
    try:
        search_request = FileSearchRequest(
            entity_type=entity_type,
            entity_id=entity_id,
            file_type=file_type,
            limit=limit,
            offset=offset
        )
        
        return await file_service.search_files(search_request, current_user, db)
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list files")

# === FILE SHARING ENDPOINTS ===

@app.post("/api/v1/files/{file_id}/share", response_model=FileShareResponse)
async def share_file(
    file_id: str,
    request: FileShareRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share file with users or groups"""
    try:
        # Check if file exists and user has access
        file_record = db.query(File).filter(File.file_id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        if file_record.uploaded_by != current_user.id and not current_user.has_permission("file.share"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create share record
        share_record = FileShare(
            file_id=file_id,
            shared_by=current_user.id,
            shared_with=request.shared_with,
            shared_with_groups=request.shared_with_groups,
            can_download=request.can_download,
            can_edit=request.can_edit,
            can_delete=request.can_delete,
            can_share=request.can_share,
            expires_at=request.expires_at
        )
        
        db.add(share_record)
        db.commit()
        db.refresh(share_record)
        
        return FileShareResponse.from_orm(share_record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sharing file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to share file")

@app.get("/api/v1/files/{file_id}/shares", response_model=List[FileShareResponse])
async def get_file_shares(
    file_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file shares"""
    try:
        # Check if file exists and user has access
        file_record = db.query(File).filter(File.file_id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        if file_record.uploaded_by != current_user.id and not current_user.has_permission("file.share"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        shares = db.query(FileShare).filter(FileShare.file_id == file_id).all()
        return [FileShareResponse.from_orm(share) for share in shares]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file shares: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get file shares")

# === FILE COLLECTIONS ENDPOINTS ===

@app.post("/api/v1/collections", response_model=FileCollectionResponse)
async def create_collection(
    request: FileCollectionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create file collection"""
    try:
        collection = FileCollection(
            name=request.name,
            description=request.description,
            collection_type=request.collection_type,
            created_by=current_user.id,
            school_id=current_user.school_id,
            file_ids=request.file_ids,
            file_count=len(request.file_ids),
            access_level=request.access_level,
            shared_with=request.shared_with or [],
            settings=request.settings,
            cover_file_id=request.cover_file_id
        )
        
        db.add(collection)
        db.commit()
        db.refresh(collection)
        
        return FileCollectionResponse.from_orm(collection)
        
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create collection")

@app.get("/api/v1/collections", response_model=List[FileCollectionResponse])
async def list_collections(
    collection_type: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List file collections"""
    try:
        query = db.query(FileCollection).filter(
            FileCollection.school_id == current_user.school_id
        )
        
        if collection_type:
            query = query.filter(FileCollection.collection_type == collection_type)
        
        # Access control
        if current_user.role != "admin":
            query = query.filter(
                (FileCollection.created_by == current_user.id) |
                (FileCollection.access_level.in_(["public", "school"])) |
                (FileCollection.shared_with.contains([current_user.id]))
            )
        
        collections = query.all()
        return [FileCollectionResponse.from_orm(collection) for collection in collections]
        
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list collections")

# === FILE ANALYTICS ENDPOINTS ===

@app.get("/api/v1/files/analytics", response_model=FileAnalyticsResponse)
async def get_file_analytics(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file analytics"""
    try:
        # Basic analytics
        query = db.query(File).filter(
            File.school_id == current_user.school_id,
            File.status != "deleted"
        )
        
        if date_from:
            query = query.filter(File.created_at >= date_from)
        if date_to:
            query = query.filter(File.created_at <= date_to)
        
        files = query.all()
        
        # Calculate metrics
        total_files = len(files)
        total_size = sum(f.file_size for f in files)
        total_downloads = sum(f.download_count for f in files)
        
        # File types distribution
        file_types = {}
        for file in files:
            file_types[file.file_type] = file_types.get(file.file_type, 0) + 1
        
        # Top files
        top_files = sorted(files, key=lambda f: f.download_count, reverse=True)[:10]
        
        return FileAnalyticsResponse(
            total_files=total_files,
            total_size=total_size,
            download_count=total_downloads,
            view_count=0,  # Would need to calculate from analytics
            share_count=0,  # Would need to calculate from shares
            file_types=file_types,
            top_files=[{
                "file_id": f.file_id,
                "filename": f.original_filename,
                "downloads": f.download_count,
                "size": f.file_size
            } for f in top_files],
            usage_trends=[],  # Would need time-series data
            storage_usage={
                "total_size": total_size,
                "file_count": total_files,
                "average_size": total_size / total_files if total_files > 0 else 0
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

# === FILE QUOTA ENDPOINTS ===

@app.get("/api/v1/files/quota", response_model=FileQuotaResponse)
async def get_user_quota(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user file quota"""
    try:
        quota = db.query(FileQuota).filter(
            FileQuota.entity_type == "user",
            FileQuota.entity_id == current_user.id
        ).first()
        
        if not quota:
            # Create default quota if not exists
            quota = FileQuota(
                entity_type="user",
                entity_id=current_user.id,
                total_quota=1073741824,  # 1GB default
                used_quota=0,
                file_count_limit=1000,
                file_count_used=0
            )
            db.add(quota)
            db.commit()
            db.refresh(quota)
        
        return FileQuotaResponse.from_orm(quota)
        
    except Exception as e:
        logger.error(f"Error getting quota: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get quota")

# === BULK OPERATIONS ENDPOINTS ===

@app.post("/api/v1/files/bulk", response_model=BulkFileOperationResponse)
async def bulk_file_operation(
    request: BulkFileOperation,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform bulk operations on files"""
    try:
        operation_id = f"bulk_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        results = []
        errors = []
        successful = 0
        failed = 0
        
        for file_id in request.file_ids:
            try:
                if request.operation == "delete":
                    await file_service.delete_file(file_id, current_user, db)
                    results.append({"file_id": file_id, "status": "deleted"})
                    successful += 1
                elif request.operation == "update":
                    update_request = FileUpdateRequest(**request.parameters)
                    await file_service.update_file(file_id, update_request, current_user, db)
                    results.append({"file_id": file_id, "status": "updated"})
                    successful += 1
                else:
                    errors.append({"file_id": file_id, "error": "Unknown operation"})
                    failed += 1
                    
            except Exception as e:
                errors.append({"file_id": file_id, "error": str(e)})
                failed += 1
        
        return BulkFileOperationResponse(
            operation_id=operation_id,
            total_files=len(request.file_ids),
            successful=successful,
            failed=failed,
            errors=errors,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Error in bulk operation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk operation")

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True
    )
