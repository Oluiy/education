"""
Content Viewer Models
Models for tracking content viewing progress and analytics
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class ContentType(enum.Enum):
    """Content type enumeration"""
    PDF = "pdf"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"


class ViewStatus(enum.Enum):
    """View status enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


class ContentView(Base):
    """
    Content viewing tracking model
    Tracks user interaction with content files
    """
    __tablename__ = "content_views"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    
    # Content details
    content_type = Column(String(20), nullable=False)
    content_title = Column(String(255), nullable=True)
    content_duration = Column(Integer, nullable=True)  # seconds for video/audio
    content_pages = Column(Integer, nullable=True)     # pages for PDF
    
    # Viewing progress
    view_status = Column(String(20), default=ViewStatus.NOT_STARTED.value, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    current_position = Column(Float, default=0.0, nullable=False)  # seconds or page number
    total_view_time = Column(Integer, default=0, nullable=False)   # total seconds viewed
    
    # Session tracking
    session_count = Column(Integer, default=0, nullable=False)
    first_viewed_at = Column(DateTime, nullable=True)
    last_viewed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Analytics
    view_quality_score = Column(Float, nullable=True)  # Engagement score
    notes = Column(Text, nullable=True)
    bookmarks = Column(Text, nullable=True)  # JSON string of bookmarks
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    file = relationship("File", back_populates="content_views")
    view_sessions = relationship("ViewSession", back_populates="content_view")
    
    def calculate_progress(self):
        """Calculate viewing progress percentage"""
        if self.content_type == ContentType.VIDEO.value or self.content_type == ContentType.AUDIO.value:
            if self.content_duration and self.content_duration > 0:
                return min(100, (self.current_position / self.content_duration) * 100)
        elif self.content_type == ContentType.PDF.value:
            if self.content_pages and self.content_pages > 0:
                return min(100, (self.current_position / self.content_pages) * 100)
        return 0
    
    def update_status(self):
        """Update view status based on progress"""
        progress = self.calculate_progress()
        
        if progress == 0:
            self.view_status = ViewStatus.NOT_STARTED.value
        elif progress >= 95:  # Consider 95% as completed
            self.view_status = ViewStatus.COMPLETED.value
            if not self.completed_at:
                self.completed_at = datetime.utcnow()
        else:
            self.view_status = ViewStatus.IN_PROGRESS.value
        
        self.progress_percentage = progress


class ViewSession(Base):
    """
    Individual viewing session tracking
    Tracks each time user opens content
    """
    __tablename__ = "view_sessions"

    id = Column(Integer, primary_key=True, index=True)
    content_view_id = Column(Integer, ForeignKey("content_views.id"), nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Session details
    session_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    session_end = Column(DateTime, nullable=True)
    session_duration = Column(Integer, nullable=True)  # seconds
    
    # Progress tracking
    start_position = Column(Float, default=0.0, nullable=False)
    end_position = Column(Float, nullable=True)
    progress_made = Column(Float, default=0.0, nullable=False)
    
    # Engagement metrics
    interactions = Column(Integer, default=0, nullable=False)  # clicks, scrolls, etc.
    pauses = Column(Integer, default=0, nullable=False)
    seeks = Column(Integer, default=0, nullable=False)        # for video/audio
    
    # Device info
    device_type = Column(String(20), nullable=True)
    browser = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    content_view = relationship("ContentView", back_populates="view_sessions")
    
    def calculate_engagement_score(self):
        """Calculate engagement score for this session"""
        if not self.session_duration or self.session_duration == 0:
            return 0
        
        # Base score from duration (longer = better engagement)
        duration_score = min(self.session_duration / 60, 30)  # Max 30 points for 1+ min
        
        # Interaction score
        interaction_score = min(self.interactions * 2, 40)    # Max 40 points
        
        # Penalty for too many pauses (indicates distraction)
        pause_penalty = min(self.pauses * 3, 20)             # Max 20 penalty
        
        # Progress score
        progress_score = self.progress_made * 30 / 100       # Max 30 points for 100% progress
        
        score = duration_score + interaction_score + progress_score - pause_penalty
        return max(0, min(100, score))


class ContentBookmark(Base):
    """
    Content bookmarks for quick navigation
    """
    __tablename__ = "content_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    content_view_id = Column(Integer, ForeignKey("content_views.id"), nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Bookmark details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    position = Column(Float, nullable=False)  # seconds or page number
    bookmark_type = Column(String(20), default="manual", nullable=False)  # manual, auto, note
    
    # Visual marker
    color = Column(String(7), default="#FFD700", nullable=False)
    icon = Column(String(50), nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_view = relationship("ContentView")


class ContentNote(Base):
    """
    User notes on content
    """
    __tablename__ = "content_notes"

    id = Column(Integer, primary_key=True, index=True)
    content_view_id = Column(Integer, ForeignKey("content_views.id"), nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Note details
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    position = Column(Float, nullable=True)  # Optional position reference
    
    # Formatting
    is_private = Column(Boolean, default=True, nullable=False)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_view = relationship("ContentView")


class ViewerSettings(Base):
    """
    User-specific viewer preferences
    """
    __tablename__ = "viewer_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False, unique=True)
    
    # PDF settings
    pdf_zoom_level = Column(Float, default=1.0, nullable=False)
    pdf_page_mode = Column(String(20), default="single", nullable=False)  # single, double, continuous
    pdf_theme = Column(String(20), default="light", nullable=False)       # light, dark, sepia
    
    # Video settings
    video_quality = Column(String(10), default="auto", nullable=False)    # auto, 480p, 720p, 1080p
    video_speed = Column(Float, default=1.0, nullable=False)               # 0.5x to 2.0x
    video_autoplay = Column(Boolean, default=False, nullable=False)
    video_subtitles = Column(Boolean, default=False, nullable=False)
    
    # Audio settings
    audio_speed = Column(Float, default=1.0, nullable=False)
    audio_quality = Column(String(10), default="auto", nullable=False)
    audio_repeat = Column(Boolean, default=False, nullable=False)
    
    # General settings
    auto_bookmark = Column(Boolean, default=True, nullable=False)          # Auto-bookmark on exit
    save_position = Column(Boolean, default=True, nullable=False)          # Save viewing position
    show_progress = Column(Boolean, default=True, nullable=False)          # Show progress indicators
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContentQuizTrigger(Base):
    """
    Quiz triggers based on content viewing progress
    """
    __tablename__ = "content_quiz_triggers"

    id = Column(Integer, primary_key=True, index=True)
    content_view_id = Column(Integer, ForeignKey("content_views.id"), nullable=False)
    quiz_id = Column(Integer, nullable=False)  # Reference to quiz in content-quiz service
    
    # Trigger conditions
    trigger_percentage = Column(Float, nullable=False)  # e.g., 50.0 for 50%
    trigger_position = Column(Float, nullable=True)     # Specific position (optional)
    
    # Status
    is_triggered = Column(Boolean, default=False, nullable=False)
    triggered_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    quiz_score = Column(Float, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    content_view = relationship("ContentView")
