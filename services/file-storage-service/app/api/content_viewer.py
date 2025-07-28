"""
Content Viewer API Endpoints
REST API for content viewing, streaming, progress tracking, and analytics
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request, status
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import os
import mimetypes

from ..database import get_db
from ..auth import get_current_user, CurrentUser
from ..models.viewer_models import ContentView, ViewSession, ContentBookmark, ContentNote
from ..schemas.viewer_schemas import (
    ContentViewCreate, ContentViewUpdate, ContentViewResponse,
    ViewSessionStart, ViewSessionEnd, ViewSessionResponse,
    BookmarkCreate, BookmarkUpdate, BookmarkResponse,
    NoteCreate, NoteUpdate, NoteResponse,
    ViewerSettingsUpdate, ViewerSettingsResponse,
    ProgressUpdate, StreamingRequest, StreamingResponse,
    ViewingAnalytics, ContentViewDashboard
)
from ..services.viewer_service import ContentViewerService, StreamingService

router = APIRouter()


# Content View Management
@router.post("/views", response_model=ContentViewResponse, status_code=status.HTTP_201_CREATED)
async def create_content_view(
    view_data: ContentViewCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new content view record
    """
    try:
        content_view = ContentViewerService.create_content_view(
            db=db,
            user_id=current_user.user_id,
            school_id=current_user.school_id,
            view_data=view_data
        )
        
        return ContentViewResponse.from_orm(content_view)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create content view: {str(e)}"
        )


@router.get("/views", response_model=List[ContentViewResponse])
async def get_content_views(
    content_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get content views for current user
    """
    try:
        content_views = ContentViewerService.get_user_content_views(
            db=db,
            user_id=current_user.user_id,
            content_type=content_type,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return [ContentViewResponse.from_orm(cv) for cv in content_views]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get content views: {str(e)}"
        )


@router.get("/views/{view_id}", response_model=ContentViewResponse)
async def get_content_view(
    view_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific content view by ID
    """
    content_view = db.query(ContentView).filter(
        ContentView.id == view_id,
        ContentView.user_id == current_user.user_id
    ).first()
    
    if not content_view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content view not found"
        )
    
    return ContentViewResponse.from_orm(content_view)


@router.put("/views/{view_id}/progress", response_model=ContentViewResponse)
async def update_viewing_progress(
    view_id: int,
    progress_data: ProgressUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update viewing progress in real-time
    """
    try:
        content_view = ContentViewerService.update_progress(
            db=db,
            content_view_id=view_id,
            user_id=current_user.user_id,
            progress_data=progress_data
        )
        
        return ContentViewResponse.from_orm(content_view)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update progress: {str(e)}"
        )


# View Session Management
@router.post("/sessions/start", response_model=ViewSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_view_session(
    session_data: ViewSessionStart,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new viewing session
    """
    try:
        # Get client IP
        ip_address = request.client.host if request.client else None
        
        session = ContentViewerService.start_view_session(
            db=db,
            user_id=current_user.user_id,
            session_data=session_data,
            ip_address=ip_address
        )
        
        return ViewSessionResponse.from_orm(session)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start session: {str(e)}"
        )


@router.post("/sessions/{session_id}/end", response_model=ViewSessionResponse)
async def end_view_session(
    session_id: int,
    end_data: ViewSessionEnd,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    End a viewing session
    """
    try:
        session = ContentViewerService.end_view_session(
            db=db,
            session_id=session_id,
            user_id=current_user.user_id,
            end_data=end_data
        )
        
        return ViewSessionResponse.from_orm(session)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to end session: {str(e)}"
        )


# Content Streaming
@router.get("/stream/{file_id}")
async def stream_content(
    file_id: int,
    quality: str = Query("auto"),
    range_header: Optional[str] = Query(None, alias="Range"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stream content with byte-range support
    """
    try:
        # Verify user has access to file
        from ..models import File
        file_record = db.query(File).filter(
            File.id == file_id,
            File.school_id == current_user.school_id
        ).first()
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Get file path (this would be from your file storage)
        file_path = f"uploads/{file_record.filename}"  # Simplified
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        # Get file info
        file_size = os.path.getsize(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        
        # Handle range requests for video streaming
        start = 0
        end = file_size - 1
        
        if range_header:
            range_match = range_header.replace("bytes=", "").split("-")
            if range_match[0]:
                start = int(range_match[0])
            if range_match[1]:
                end = int(range_match[1])
        
        # Create streaming response
        def generate_chunks():
            with open(file_path, "rb") as file:
                file.seek(start)
                remaining = end - start + 1
                while remaining:
                    chunk_size = min(8192, remaining)  # 8KB chunks
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        
        # Set response headers
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
        }
        
        status_code = 206 if range_header else 200
        
        return StreamingResponse(
            generate_chunks(),
            status_code=status_code,
            headers=headers,
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to stream content: {str(e)}"
        )


@router.get("/view/pdf/{file_id}")
async def view_pdf(
    file_id: int,
    page: int = Query(1, ge=1),
    zoom: float = Query(1.0, ge=0.1, le=5.0),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    View PDF content with page navigation
    """
    try:
        # Verify file access and type
        from ..models import File
        file_record = db.query(File).filter(
            File.id == file_id,
            File.school_id == current_user.school_id,
            File.content_type == "application/pdf"
        ).first()
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file not found"
            )
        
        # Return file for PDF.js viewer
        file_path = f"uploads/{file_record.filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=file_record.original_filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to view PDF: {str(e)}"
        )


@router.get("/view/video/{file_id}")
async def view_video(
    file_id: int,
    quality: str = Query("auto"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get video streaming information
    """
    try:
        # Verify file access and type
        from ..models import File
        file_record = db.query(File).filter(
            File.id == file_id,
            File.school_id == current_user.school_id
        ).first()
        
        if not file_record or not file_record.content_type.startswith("video/"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file not found"
            )
        
        # Generate streaming info
        stream_url = StreamingService.generate_stream_url(
            file_id=file_id,
            user_id=current_user.user_id,
            quality=quality
        )
        
        quality_options = StreamingService.get_quality_options(
            content_type="video",
            file_size=file_record.file_size or 0
        )
        
        thumbnail_url = StreamingService.generate_thumbnail(file_id)
        
        return {
            "stream_url": stream_url,
            "content_type": file_record.content_type,
            "duration": None,  # Would need metadata extraction
            "file_size": file_record.file_size,
            "quality_options": quality_options,
            "subtitle_tracks": [],  # Would need subtitle detection
            "thumbnail_url": thumbnail_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get video info: {str(e)}"
        )


@router.get("/view/audio/{file_id}")
async def view_audio(
    file_id: int,
    quality: str = Query("auto"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audio streaming information
    """
    try:
        # Verify file access and type
        from ..models import File
        file_record = db.query(File).filter(
            File.id == file_id,
            File.school_id == current_user.school_id
        ).first()
        
        if not file_record or not file_record.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found"
            )
        
        # Generate streaming info
        stream_url = StreamingService.generate_stream_url(
            file_id=file_id,
            user_id=current_user.user_id,
            quality=quality
        )
        
        quality_options = StreamingService.get_quality_options(
            content_type="audio",
            file_size=file_record.file_size or 0
        )
        
        return {
            "stream_url": stream_url,
            "content_type": file_record.content_type,
            "duration": None,  # Would need metadata extraction
            "file_size": file_record.file_size,
            "quality_options": quality_options,
            "subtitle_tracks": [],
            "thumbnail_url": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get audio info: {str(e)}"
        )


# Bookmarks Management
@router.post("/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a content bookmark
    """
    try:
        bookmark = ContentViewerService.create_bookmark(
            db=db,
            user_id=current_user.user_id,
            bookmark_data=bookmark_data
        )
        
        return BookmarkResponse.from_orm(bookmark)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create bookmark: {str(e)}"
        )


@router.get("/bookmarks", response_model=List[BookmarkResponse])
async def get_bookmarks(
    content_view_id: Optional[int] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user bookmarks
    """
    try:
        query = db.query(ContentBookmark).filter(
            ContentBookmark.user_id == current_user.user_id
        )
        
        if content_view_id:
            query = query.filter(ContentBookmark.content_view_id == content_view_id)
        
        bookmarks = query.order_by(ContentBookmark.position).all()
        return [BookmarkResponse.from_orm(b) for b in bookmarks]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get bookmarks: {str(e)}"
        )


# Notes Management
@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a content note
    """
    try:
        note = ContentViewerService.create_note(
            db=db,
            user_id=current_user.user_id,
            note_data=note_data
        )
        
        return NoteResponse.from_orm(note)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create note: {str(e)}"
        )


@router.get("/notes", response_model=List[NoteResponse])
async def get_notes(
    content_view_id: Optional[int] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user notes
    """
    try:
        query = db.query(ContentNote).filter(
            ContentNote.user_id == current_user.user_id
        )
        
        if content_view_id:
            query = query.filter(ContentNote.content_view_id == content_view_id)
        
        notes = query.order_by(ContentNote.created_at.desc()).all()
        return [NoteResponse.from_orm(n) for n in notes]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get notes: {str(e)}"
        )


# Viewer Settings
@router.get("/settings", response_model=ViewerSettingsResponse)
async def get_viewer_settings(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user viewer settings
    """
    try:
        settings = ContentViewerService.get_or_create_settings(
            db=db,
            user_id=current_user.user_id
        )
        
        return ViewerSettingsResponse.from_orm(settings)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get settings: {str(e)}"
        )


@router.put("/settings", response_model=ViewerSettingsResponse)
async def update_viewer_settings(
    settings_data: ViewerSettingsUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user viewer settings
    """
    try:
        settings = ContentViewerService.update_settings(
            db=db,
            user_id=current_user.user_id,
            settings_data=settings_data
        )
        
        return ViewerSettingsResponse.from_orm(settings)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update settings: {str(e)}"
        )


# Analytics
@router.get("/analytics", response_model=ViewingAnalytics)
async def get_viewing_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get viewing analytics for user
    """
    try:
        analytics = ContentViewerService.get_viewing_analytics(
            db=db,
            user_id=current_user.user_id,
            days=days
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get analytics: {str(e)}"
        )


# Dashboard
@router.get("/dashboard", response_model=ContentViewDashboard)
async def get_content_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get content viewing dashboard
    """
    try:
        # Get recent views
        recent_views = ContentViewerService.get_user_content_views(
            db=db,
            user_id=current_user.user_id,
            limit=5
        )
        
        # Get bookmarks
        bookmarks = db.query(ContentBookmark).filter(
            ContentBookmark.user_id == current_user.user_id
        ).order_by(ContentBookmark.created_at.desc()).limit(10).all()
        
        # Get notes
        notes = db.query(ContentNote).filter(
            ContentNote.user_id == current_user.user_id
        ).order_by(ContentNote.created_at.desc()).limit(5).all()
        
        # Get analytics
        analytics = ContentViewerService.get_viewing_analytics(
            db=db,
            user_id=current_user.user_id,
            days=7  # Last week
        )
        
        return ContentViewDashboard(
            current_content=None,  # Would need to track current active content
            recent_views=[ContentViewResponse.from_orm(cv) for cv in recent_views],
            bookmarks=[BookmarkResponse.from_orm(b) for b in bookmarks],
            notes=[NoteResponse.from_orm(n) for n in notes],
            analytics=analytics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get dashboard: {str(e)}"
        )
