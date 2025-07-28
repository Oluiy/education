"""
Content Viewer Schemas
Pydantic schemas for content viewer API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    PDF = "pdf"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"


class ViewStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


class BookmarkType(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"
    NOTE = "note"


# Content View Schemas
class ContentViewCreate(BaseModel):
    """Schema for creating a content view"""
    file_id: int
    content_type: ContentType
    content_title: Optional[str] = None
    content_duration: Optional[int] = Field(None, ge=0)
    content_pages: Optional[int] = Field(None, ge=1)


class ContentViewUpdate(BaseModel):
    """Schema for updating content view progress"""
    current_position: Optional[float] = Field(None, ge=0)
    view_status: Optional[ViewStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)
    interactions: Optional[int] = Field(None, ge=0)
    pauses: Optional[int] = Field(None, ge=0)
    seeks: Optional[int] = Field(None, ge=0)


class ContentViewResponse(BaseModel):
    """Schema for content view response"""
    id: int
    user_id: int
    school_id: int
    file_id: int
    content_type: str
    content_title: Optional[str]
    content_duration: Optional[int]
    content_pages: Optional[int]
    view_status: str
    progress_percentage: float
    current_position: float
    total_view_time: int
    session_count: int
    first_viewed_at: Optional[datetime]
    last_viewed_at: Optional[datetime]
    completed_at: Optional[datetime]
    view_quality_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# View Session Schemas
class ViewSessionStart(BaseModel):
    """Schema for starting a view session"""
    content_view_id: int
    start_position: float = Field(0.0, ge=0)
    device_type: Optional[str] = Field(None, max_length=20)
    browser: Optional[str] = Field(None, max_length=100)


class ViewSessionEnd(BaseModel):
    """Schema for ending a view session"""
    end_position: Optional[float] = Field(None, ge=0)
    interactions: int = Field(0, ge=0)
    pauses: int = Field(0, ge=0)
    seeks: int = Field(0, ge=0)


class ViewSessionResponse(BaseModel):
    """Schema for view session response"""
    id: int
    content_view_id: int
    user_id: int
    session_start: datetime
    session_end: Optional[datetime]
    session_duration: Optional[int]
    start_position: float
    end_position: Optional[float]
    progress_made: float
    interactions: int
    pauses: int
    seeks: int
    device_type: Optional[str]
    browser: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Bookmark Schemas
class BookmarkCreate(BaseModel):
    """Schema for creating a bookmark"""
    content_view_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    position: float = Field(..., ge=0)
    bookmark_type: BookmarkType = BookmarkType.MANUAL
    color: str = Field("#FFD700", regex=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)


class BookmarkUpdate(BaseModel):
    """Schema for updating a bookmark"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    position: Optional[float] = Field(None, ge=0)
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)


class BookmarkResponse(BaseModel):
    """Schema for bookmark response"""
    id: int
    content_view_id: int
    user_id: int
    title: str
    description: Optional[str]
    position: float
    bookmark_type: str
    color: str
    icon: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Note Schemas
class NoteCreate(BaseModel):
    """Schema for creating a note"""
    content_view_id: int
    title: Optional[str] = Field(None, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)
    position: Optional[float] = Field(None, ge=0)
    is_private: bool = True
    tags: Optional[str] = Field(None, max_length=500)


class NoteUpdate(BaseModel):
    """Schema for updating a note"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    position: Optional[float] = Field(None, ge=0)
    is_private: Optional[bool] = None
    tags: Optional[str] = Field(None, max_length=500)


class NoteResponse(BaseModel):
    """Schema for note response"""
    id: int
    content_view_id: int
    user_id: int
    title: Optional[str]
    content: str
    position: Optional[float]
    is_private: bool
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Viewer Settings Schemas
class ViewerSettingsUpdate(BaseModel):
    """Schema for updating viewer settings"""
    # PDF settings
    pdf_zoom_level: Optional[float] = Field(None, ge=0.5, le=5.0)
    pdf_page_mode: Optional[str] = Field(None, regex=r'^(single|double|continuous)$')
    pdf_theme: Optional[str] = Field(None, regex=r'^(light|dark|sepia)$')
    
    # Video settings
    video_quality: Optional[str] = Field(None, regex=r'^(auto|480p|720p|1080p)$')
    video_speed: Optional[float] = Field(None, ge=0.5, le=2.0)
    video_autoplay: Optional[bool] = None
    video_subtitles: Optional[bool] = None
    
    # Audio settings
    audio_speed: Optional[float] = Field(None, ge=0.5, le=2.0)
    audio_quality: Optional[str] = Field(None, regex=r'^(auto|low|medium|high)$')
    audio_repeat: Optional[bool] = None
    
    # General settings
    auto_bookmark: Optional[bool] = None
    save_position: Optional[bool] = None
    show_progress: Optional[bool] = None


class ViewerSettingsResponse(BaseModel):
    """Schema for viewer settings response"""
    id: int
    user_id: int
    pdf_zoom_level: float
    pdf_page_mode: str
    pdf_theme: str
    video_quality: str
    video_speed: float
    video_autoplay: bool
    video_subtitles: bool
    audio_speed: float
    audio_quality: str
    audio_repeat: bool
    auto_bookmark: bool
    save_position: bool
    show_progress: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class ViewingAnalytics(BaseModel):
    """Schema for viewing analytics"""
    total_content_viewed: int
    total_view_time: int  # seconds
    average_session_duration: float
    completion_rate: float
    most_viewed_content_type: str
    daily_view_time: Dict[str, int]
    weekly_progress: Dict[str, float]
    content_type_distribution: Dict[str, int]
    engagement_score: float


class ContentViewDashboard(BaseModel):
    """Schema for content view dashboard"""
    current_content: Optional[ContentViewResponse]
    recent_views: List[ContentViewResponse]
    bookmarks: List[BookmarkResponse]
    notes: List[NoteResponse]
    analytics: ViewingAnalytics


# Progress Update Schema
class ProgressUpdate(BaseModel):
    """Schema for updating viewing progress"""
    position: float = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    interaction_type: Optional[str] = Field(None, max_length=50)  # play, pause, seek, scroll
    quality_change: Optional[str] = None
    speed_change: Optional[float] = None


# Streaming Schema
class StreamingRequest(BaseModel):
    """Schema for streaming content request"""
    file_id: int
    quality: Optional[str] = "auto"
    start_position: Optional[float] = 0
    device_type: Optional[str] = "web"


class StreamingResponse(BaseModel):
    """Schema for streaming response"""
    stream_url: str
    content_type: str
    duration: Optional[int]
    file_size: Optional[int]
    quality_options: List[str]
    subtitle_tracks: List[Dict[str, str]]
    thumbnail_url: Optional[str]


# Quiz Trigger Schema
class QuizTriggerCreate(BaseModel):
    """Schema for creating quiz trigger"""
    content_view_id: int
    quiz_id: int
    trigger_percentage: float = Field(..., ge=0, le=100)
    trigger_position: Optional[float] = Field(None, ge=0)


class QuizTriggerResponse(BaseModel):
    """Schema for quiz trigger response"""
    id: int
    content_view_id: int
    quiz_id: int
    trigger_percentage: float
    trigger_position: Optional[float]
    is_triggered: bool
    triggered_at: Optional[datetime]
    is_completed: bool
    quiz_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
