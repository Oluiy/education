"""
Content Viewer Service
Business logic for content viewing, progress tracking, and analytics
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta, date
import logging
import json
from io import BytesIO

from ..models.viewer_models import (
    ContentView, ViewSession, ContentBookmark, ContentNote,
    ViewerSettings, ContentQuizTrigger, ContentType, ViewStatus
)
from ..schemas.viewer_schemas import (
    ContentViewCreate, ContentViewUpdate, ViewSessionStart, ViewSessionEnd,
    BookmarkCreate, NoteCreate, ViewerSettingsUpdate, ProgressUpdate,
    ViewingAnalytics
)

logger = logging.getLogger(__name__)


class ContentViewerService:
    """Service for managing content viewing and progress tracking"""
    
    @staticmethod
    def create_content_view(
        db: Session,
        user_id: int,
        school_id: int,
        view_data: ContentViewCreate
    ) -> ContentView:
        """Create a new content view record"""
        try:
            # Check if view already exists for this user and file
            existing_view = db.query(ContentView).filter(
                ContentView.user_id == user_id,
                ContentView.file_id == view_data.file_id
            ).first()
            
            if existing_view:
                return existing_view
            
            # Create new content view
            content_view = ContentView(
                user_id=user_id,
                school_id=school_id,
                file_id=view_data.file_id,
                content_type=view_data.content_type.value,
                content_title=view_data.content_title,
                content_duration=view_data.content_duration,
                content_pages=view_data.content_pages
            )
            
            db.add(content_view)
            db.commit()
            db.refresh(content_view)
            
            logger.info(f"Created content view {content_view.id} for user {user_id}")
            return content_view
            
        except Exception as e:
            logger.error(f"Failed to create content view: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def start_view_session(
        db: Session,
        user_id: int,
        session_data: ViewSessionStart,
        ip_address: Optional[str] = None
    ) -> ViewSession:
        """Start a new viewing session"""
        try:
            # Get content view
            content_view = db.query(ContentView).filter(
                ContentView.id == session_data.content_view_id,
                ContentView.user_id == user_id
            ).first()
            
            if not content_view:
                raise ValueError("Content view not found")
            
            # Create view session
            session = ViewSession(
                content_view_id=session_data.content_view_id,
                user_id=user_id,
                start_position=session_data.start_position,
                device_type=session_data.device_type,
                browser=session_data.browser,
                ip_address=ip_address
            )
            
            db.add(session)
            
            # Update content view
            content_view.session_count += 1
            if not content_view.first_viewed_at:
                content_view.first_viewed_at = datetime.utcnow()
            content_view.last_viewed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            
            logger.info(f"Started view session {session.id} for content {session_data.content_view_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start view session: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def end_view_session(
        db: Session,
        session_id: int,
        user_id: int,
        end_data: ViewSessionEnd
    ) -> ViewSession:
        """End a viewing session"""
        try:
            session = db.query(ViewSession).filter(
                ViewSession.id == session_id,
                ViewSession.user_id == user_id,
                ViewSession.session_end.is_(None)
            ).first()
            
            if not session:
                raise ValueError("Active session not found")
            
            # Update session
            session.session_end = datetime.utcnow()
            session.session_duration = int((session.session_end - session.session_start).total_seconds())
            session.end_position = end_data.end_position or session.start_position
            session.progress_made = max(0, session.end_position - session.start_position)
            session.interactions = end_data.interactions
            session.pauses = end_data.pauses
            session.seeks = end_data.seeks
            
            # Update content view
            content_view = session.content_view
            content_view.current_position = session.end_position or session.start_position
            content_view.total_view_time += session.session_duration
            content_view.update_status()
            
            # Calculate and update quality score
            engagement_score = session.calculate_engagement_score()
            if content_view.view_quality_score is None:
                content_view.view_quality_score = engagement_score
            else:
                # Running average
                sessions_count = content_view.session_count
                content_view.view_quality_score = (
                    (content_view.view_quality_score * (sessions_count - 1) + engagement_score) / sessions_count
                )
            
            db.commit()
            db.refresh(session)
            
            # Check for quiz triggers
            ContentViewerService._check_quiz_triggers(db, content_view)
            
            logger.info(f"Ended view session {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to end view session: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def update_progress(
        db: Session,
        content_view_id: int,
        user_id: int,
        progress_data: ProgressUpdate
    ) -> ContentView:
        """Update viewing progress in real-time"""
        try:
            content_view = db.query(ContentView).filter(
                ContentView.id == content_view_id,
                ContentView.user_id == user_id
            ).first()
            
            if not content_view:
                raise ValueError("Content view not found")
            
            # Update position and progress
            content_view.current_position = progress_data.position
            content_view.last_viewed_at = progress_data.timestamp
            content_view.update_status()
            
            db.commit()
            db.refresh(content_view)
            
            return content_view
            
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def get_user_content_views(
        db: Session,
        user_id: int,
        content_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ContentView]:
        """Get content views for user"""
        query = db.query(ContentView).filter(ContentView.user_id == user_id)
        
        if content_type:
            query = query.filter(ContentView.content_type == content_type)
        
        if status:
            query = query.filter(ContentView.view_status == status)
        
        return query.order_by(desc(ContentView.last_viewed_at)).offset(offset).limit(limit).all()
    
    @staticmethod
    def create_bookmark(
        db: Session,
        user_id: int,
        bookmark_data: BookmarkCreate
    ) -> ContentBookmark:
        """Create a content bookmark"""
        try:
            # Verify content view belongs to user
            content_view = db.query(ContentView).filter(
                ContentView.id == bookmark_data.content_view_id,
                ContentView.user_id == user_id
            ).first()
            
            if not content_view:
                raise ValueError("Content view not found")
            
            bookmark = ContentBookmark(
                content_view_id=bookmark_data.content_view_id,
                user_id=user_id,
                title=bookmark_data.title,
                description=bookmark_data.description,
                position=bookmark_data.position,
                bookmark_type=bookmark_data.bookmark_type.value,
                color=bookmark_data.color,
                icon=bookmark_data.icon
            )
            
            db.add(bookmark)
            db.commit()
            db.refresh(bookmark)
            
            logger.info(f"Created bookmark {bookmark.id} for user {user_id}")
            return bookmark
            
        except Exception as e:
            logger.error(f"Failed to create bookmark: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def create_note(
        db: Session,
        user_id: int,
        note_data: NoteCreate
    ) -> ContentNote:
        """Create a content note"""
        try:
            # Verify content view belongs to user
            content_view = db.query(ContentView).filter(
                ContentView.id == note_data.content_view_id,
                ContentView.user_id == user_id
            ).first()
            
            if not content_view:
                raise ValueError("Content view not found")
            
            note = ContentNote(
                content_view_id=note_data.content_view_id,
                user_id=user_id,
                title=note_data.title,
                content=note_data.content,
                position=note_data.position,
                is_private=note_data.is_private,
                tags=note_data.tags
            )
            
            db.add(note)
            db.commit()
            db.refresh(note)
            
            logger.info(f"Created note {note.id} for user {user_id}")
            return note
            
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def get_or_create_settings(
        db: Session,
        user_id: int
    ) -> ViewerSettings:
        """Get or create viewer settings for user"""
        try:
            settings = db.query(ViewerSettings).filter(
                ViewerSettings.user_id == user_id
            ).first()
            
            if not settings:
                settings = ViewerSettings(user_id=user_id)
                db.add(settings)
                db.commit()
                db.refresh(settings)
            
            return settings
            
        except Exception as e:
            logger.error(f"Failed to get/create settings: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def update_settings(
        db: Session,
        user_id: int,
        settings_data: ViewerSettingsUpdate
    ) -> ViewerSettings:
        """Update viewer settings"""
        try:
            settings = ContentViewerService.get_or_create_settings(db, user_id)
            
            # Update fields
            for field, value in settings_data.dict(exclude_unset=True).items():
                setattr(settings, field, value)
            
            settings.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(settings)
            
            return settings
            
        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def get_viewing_analytics(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> ViewingAnalytics:
        """Get viewing analytics for user"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get content views in period
            content_views = db.query(ContentView).filter(
                ContentView.user_id == user_id,
                ContentView.first_viewed_at >= start_date
            ).all()
            
            # Get view sessions in period
            view_sessions = db.query(ViewSession).filter(
                ViewSession.user_id == user_id,
                ViewSession.session_start >= start_date
            ).all()
            
            # Calculate metrics
            total_content_viewed = len(content_views)
            total_view_time = sum(cv.total_view_time for cv in content_views)
            
            # Average session duration
            active_sessions = [s for s in view_sessions if s.session_duration]
            avg_session_duration = (
                sum(s.session_duration for s in active_sessions) / len(active_sessions)
                if active_sessions else 0
            )
            
            # Completion rate
            completed_views = len([cv for cv in content_views if cv.view_status == ViewStatus.COMPLETED.value])
            completion_rate = (completed_views / total_content_viewed * 100) if total_content_viewed > 0 else 0
            
            # Most viewed content type
            content_type_counts = {}
            for cv in content_views:
                content_type_counts[cv.content_type] = content_type_counts.get(cv.content_type, 0) + 1
            most_viewed_content_type = max(content_type_counts, key=content_type_counts.get) if content_type_counts else "none"
            
            # Engagement score
            quality_scores = [cv.view_quality_score for cv in content_views if cv.view_quality_score is not None]
            engagement_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return ViewingAnalytics(
                total_content_viewed=total_content_viewed,
                total_view_time=total_view_time,
                average_session_duration=avg_session_duration,
                completion_rate=completion_rate,
                most_viewed_content_type=most_viewed_content_type,
                daily_view_time={},  # Would need detailed implementation
                weekly_progress={},  # Would need detailed implementation
                content_type_distribution=content_type_counts,
                engagement_score=engagement_score
            )
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            raise
    
    @staticmethod
    def _check_quiz_triggers(db: Session, content_view: ContentView):
        """Check and trigger quizzes based on viewing progress"""
        try:
            triggers = db.query(ContentQuizTrigger).filter(
                ContentQuizTrigger.content_view_id == content_view.id,
                ContentQuizTrigger.is_triggered == False
            ).all()
            
            for trigger in triggers:
                should_trigger = False
                
                # Check percentage trigger
                if content_view.progress_percentage >= trigger.trigger_percentage:
                    should_trigger = True
                
                # Check position trigger
                if trigger.trigger_position and content_view.current_position >= trigger.trigger_position:
                    should_trigger = True
                
                if should_trigger:
                    trigger.is_triggered = True
                    trigger.triggered_at = datetime.utcnow()
                    logger.info(f"Triggered quiz {trigger.quiz_id} for content view {content_view.id}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to check quiz triggers: {e}")
            db.rollback()


class StreamingService:
    """Service for content streaming and delivery"""
    
    @staticmethod
    def generate_stream_url(
        file_id: int,
        user_id: int,
        quality: str = "auto",
        token: Optional[str] = None
    ) -> str:
        """Generate secure streaming URL"""
        # This would integrate with your file storage system
        # For now, returning a placeholder
        base_url = "/api/v1/content/stream"
        return f"{base_url}/{file_id}?quality={quality}&user={user_id}&token={token or 'temp'}"
    
    @staticmethod
    def get_quality_options(content_type: str, file_size: int) -> List[str]:
        """Get available quality options for content"""
        if content_type == ContentType.VIDEO.value:
            # Based on file size, determine available qualities
            options = ["auto"]
            if file_size > 100_000_000:  # > 100MB
                options.extend(["1080p", "720p", "480p"])
            elif file_size > 50_000_000:  # > 50MB
                options.extend(["720p", "480p"])
            else:
                options.append("480p")
            return options
        elif content_type == ContentType.AUDIO.value:
            return ["auto", "high", "medium", "low"]
        else:
            return ["auto"]
    
    @staticmethod
    def generate_thumbnail(file_id: int, position: float = 0) -> Optional[str]:
        """Generate thumbnail for video content"""
        # This would integrate with video processing service
        # For now, returning placeholder
        return f"/api/v1/content/{file_id}/thumbnail?t={position}"
