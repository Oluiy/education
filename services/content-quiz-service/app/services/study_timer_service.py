"""
Study Timer Service
Business logic for study session tracking and timer management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import logging
import json

from ..models.content_models import StudySession, StudyTimer
from ..schemas.study_timer import (
    StudySessionCreate, StudySessionUpdate, StudySessionResponse,
    StudyTimerCreate, StudyTimerUpdate, StudyTimerResponse,
    StudyStats, DailyStats, WeeklyStats, MonthlyStats,
    ProductivityScore, ProductivityInsights, TimerAction, TimerState
)
from ..auth import CurrentUser

logger = logging.getLogger(__name__)

class StudyTimerService:
    """Service for managing study sessions and timers"""
    
    async def start_session(
        self,
        session_data: StudySessionCreate,
        current_user: CurrentUser,
        db: Session
    ) -> StudySession:
        """Start a new study session"""
        try:
            # Check if user has an active session
            active_session = await self.get_active_session(current_user, db)
            if active_session:
                raise ValueError("User already has an active session")
            
            # Create new session
            session = StudySession(
                user_id=current_user.user_id,
                school_id=current_user.school_id,
                subject=session_data.subject,
                topic=session_data.topic,
                session_type=session_data.session_type.value,
                planned_duration=session_data.planned_duration,
                goals=session_data.goals,
                notes=session_data.notes,
                device_type=session_data.device_type,
                start_time=datetime.utcnow(),
                status="active"
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            return session
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error starting study session: {str(e)}")
            raise
    
    async def pause_session(
        self,
        session_id: int,
        current_user: CurrentUser,
        db: Session
    ) -> StudySession:
        """Pause an active study session"""
        try:
            session = await self.get_session(session_id, current_user, db)
            if not session:
                raise ValueError("Session not found")
            
            if session.status != "active":
                raise ValueError("Session is not active")
            
            session.status = "paused"
            session.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            
            return session
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error pausing study session: {str(e)}")
            raise
    
    async def resume_session(
        self,
        session_id: int,
        current_user: CurrentUser,
        db: Session
    ) -> StudySession:
        """Resume a paused study session"""
        try:
            session = await self.get_session(session_id, current_user, db)
            if not session:
                raise ValueError("Session not found")
            
            if session.status != "paused":
                raise ValueError("Session is not paused")
            
            session.status = "active"
            session.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            
            return session
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error resuming study session: {str(e)}")
            raise
    
    async def complete_session(
        self,
        session_id: int,
        session_update: StudySessionUpdate,
        current_user: CurrentUser,
        db: Session
    ) -> StudySession:
        """Complete a study session"""
        try:
            session = await self.get_session(session_id, current_user, db)
            if not session:
                raise ValueError("Session not found")
            
            if session.status not in ["active", "paused"]:
                raise ValueError("Session cannot be completed")
            
            # Update session data
            session.end_time = datetime.utcnow()
            session.status = "completed"
            session.actual_duration = self._calculate_duration(session.start_time, session.end_time)
            
            # Update optional fields
            if session_update.notes:
                session.notes = session_update.notes
            if session_update.completed_goals:
                session.completed_goals = session_update.completed_goals
            if session_update.focus_rating:
                session.focus_rating = session_update.focus_rating
            if session_update.productivity_rating:
                session.productivity_rating = session_update.productivity_rating
            if session_update.difficulty_rating:
                session.difficulty_rating = session_update.difficulty_rating
            
            session.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            
            return session
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error completing study session: {str(e)}")
            raise
    
    async def get_session(
        self,
        session_id: int,
        current_user: CurrentUser,
        db: Session
    ) -> Optional[StudySession]:
        """Get a specific study session"""
        try:
            session = db.query(StudySession).filter(
                and_(
                    StudySession.id == session_id,
                    StudySession.user_id == current_user.user_id
                )
            ).first()
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting study session: {str(e)}")
            raise
    
    async def get_sessions(
        self,
        current_user: CurrentUser,
        db: Session,
        limit: int = 20,
        offset: int = 0
    ) -> List[StudySession]:
        """Get user's study sessions"""
        try:
            sessions = db.query(StudySession).filter(
                StudySession.user_id == current_user.user_id
            ).order_by(desc(StudySession.created_at)).offset(offset).limit(limit).all()
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting study sessions: {str(e)}")
            raise
    
    async def get_active_session(
        self,
        current_user: CurrentUser,
        db: Session
    ) -> Optional[StudySession]:
        """Get user's currently active study session"""
        try:
            session = db.query(StudySession).filter(
                and_(
                    StudySession.user_id == current_user.user_id,
                    StudySession.status == "active"
                )
            ).first()
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting active session: {str(e)}")
            raise
    
    async def get_stats(
        self,
        current_user: CurrentUser,
        db: Session,
        period: str = "week"
    ) -> StudyStats:
        """Get study statistics for the user"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if period == "day":
                start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "week":
                start_date = end_date - timedelta(days=7)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=7)
            
            # Get sessions in date range
            sessions = db.query(StudySession).filter(
                and_(
                    StudySession.user_id == current_user.user_id,
                    StudySession.created_at >= start_date,
                    StudySession.created_at <= end_date
                )
            ).all()
            
            # Calculate statistics
            total_sessions = len(sessions)
            total_study_time = sum(s.actual_duration or 0 for s in sessions if s.actual_duration)
            total_break_time = sum(s.break_duration or 0 for s in sessions if s.break_duration)
            
            if total_sessions > 0:
                average_session_length = total_study_time / total_sessions
                longest_session = max(s.actual_duration or 0 for s in sessions)
                shortest_session = min(s.actual_duration or 0 for s in sessions if s.actual_duration)
                completion_rate = len([s for s in sessions if s.status == "completed"]) / total_sessions * 100
                
                # Calculate average ratings
                focus_ratings = [s.focus_rating for s in sessions if s.focus_rating]
                productivity_ratings = [s.productivity_rating for s in sessions if s.productivity_rating]
                difficulty_ratings = [s.difficulty_rating for s in sessions if s.difficulty_rating]
                
                focus_rating_avg = sum(focus_ratings) / len(focus_ratings) if focus_ratings else 0
                productivity_rating_avg = sum(productivity_ratings) / len(productivity_ratings) if productivity_ratings else 0
                difficulty_rating_avg = sum(difficulty_ratings) / len(difficulty_ratings) if difficulty_ratings else 0
            else:
                average_session_length = 0
                longest_session = 0
                shortest_session = 0
                completion_rate = 0
                focus_rating_avg = 0
                productivity_rating_avg = 0
                difficulty_rating_avg = 0
            
            # Calculate study streak
            study_streak = await self._calculate_study_streak(current_user, db)
            
            # Calculate goal progress
            weekly_goal_progress = await self._calculate_goal_progress(current_user, db, "week")
            monthly_goal_progress = await self._calculate_goal_progress(current_user, db, "month")
            
            # Calculate distributions
            preferred_study_times = await self._calculate_study_time_distribution(sessions)
            subject_distribution = await self._calculate_subject_distribution(sessions)
            session_type_distribution = await self._calculate_session_type_distribution(sessions)
            
            return StudyStats(
                total_sessions=total_sessions,
                total_study_time=total_study_time,
                total_break_time=total_break_time,
                average_session_length=average_session_length,
                longest_session=longest_session,
                shortest_session=shortest_session,
                completion_rate=completion_rate,
                focus_rating_avg=focus_rating_avg,
                productivity_rating_avg=productivity_rating_avg,
                difficulty_rating_avg=difficulty_rating_avg,
                study_streak=study_streak,
                weekly_goal_progress=weekly_goal_progress,
                monthly_goal_progress=monthly_goal_progress,
                preferred_study_times=preferred_study_times,
                subject_distribution=subject_distribution,
                session_type_distribution=session_type_distribution
            )
            
        except Exception as e:
            logger.error(f"Error getting study stats: {str(e)}")
            raise
    
    async def create_timer(
        self,
        timer_data: StudyTimerCreate,
        current_user: CurrentUser,
        db: Session
    ) -> StudyTimer:
        """Create a new study timer"""
        try:
            # If this is set as default, unset other default timers
            if timer_data.is_default:
                db.query(StudyTimer).filter(
                    and_(
                        StudyTimer.user_id == current_user.user_id,
                        StudyTimer.is_default == True
                    )
                ).update({"is_default": False})
            
            timer = StudyTimer(
                user_id=current_user.user_id,
                school_id=current_user.school_id,
                timer_name=timer_data.timer_name,
                study_duration=timer_data.study_duration,
                break_duration=timer_data.break_duration,
                long_break_duration=timer_data.long_break_duration,
                sessions_before_long_break=timer_data.sessions_before_long_break,
                auto_start_breaks=timer_data.auto_start_breaks,
                auto_start_sessions=timer_data.auto_start_sessions,
                sound_enabled=timer_data.sound_enabled,
                notifications_enabled=timer_data.notifications_enabled,
                subject_id=timer_data.subject_id,
                topic_id=timer_data.topic_id,
                is_default=timer_data.is_default
            )
            
            db.add(timer)
            db.commit()
            db.refresh(timer)
            
            return timer
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating study timer: {str(e)}")
            raise
    
    async def get_timers(
        self,
        current_user: CurrentUser,
        db: Session
    ) -> List[StudyTimer]:
        """Get user's study timers"""
        try:
            timers = db.query(StudyTimer).filter(
                StudyTimer.user_id == current_user.user_id
            ).order_by(desc(StudyTimer.is_default), StudyTimer.timer_name).all()
            
            return timers
            
        except Exception as e:
            logger.error(f"Error getting study timers: {str(e)}")
            raise
    
    async def update_timer(
        self,
        timer_id: int,
        timer_data: StudyTimerUpdate,
        current_user: CurrentUser,
        db: Session
    ) -> Optional[StudyTimer]:
        """Update a study timer"""
        try:
            timer = db.query(StudyTimer).filter(
                and_(
                    StudyTimer.id == timer_id,
                    StudyTimer.user_id == current_user.user_id
                )
            ).first()
            
            if not timer:
                return None
            
            # If setting as default, unset other default timers
            if timer_data.is_default:
                db.query(StudyTimer).filter(
                    and_(
                        StudyTimer.user_id == current_user.user_id,
                        StudyTimer.is_default == True,
                        StudyTimer.id != timer_id
                    )
                ).update({"is_default": False})
            
            # Update fields
            update_data = timer_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(timer, field, value)
            
            timer.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(timer)
            
            return timer
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating study timer: {str(e)}")
            raise
    
    async def delete_timer(
        self,
        timer_id: int,
        current_user: CurrentUser,
        db: Session
    ) -> bool:
        """Delete a study timer"""
        try:
            timer = db.query(StudyTimer).filter(
                and_(
                    StudyTimer.id == timer_id,
                    StudyTimer.user_id == current_user.user_id
                )
            ).first()
            
            if not timer:
                return False
            
            db.delete(timer)
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting study timer: {str(e)}")
            raise
    
    async def calculate_productivity_score(
        self,
        current_user: CurrentUser,
        db: Session
    ) -> float:
        """Calculate user's study productivity score"""
        try:
            # Get recent sessions (last 30 days)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            sessions = db.query(StudySession).filter(
                and_(
                    StudySession.user_id == current_user.user_id,
                    StudySession.created_at >= start_date,
                    StudySession.created_at <= end_date,
                    StudySession.status == "completed"
                )
            ).all()
            
            if not sessions:
                return 0.0
            
            # Calculate productivity factors
            total_time = sum(s.actual_duration or 0 for s in sessions)
            completion_rate = len(sessions) / len(sessions)  # All completed sessions
            focus_avg = sum(s.focus_rating or 0 for s in sessions) / len(sessions) if any(s.focus_rating for s in sessions) else 0
            productivity_avg = sum(s.productivity_rating or 0 for s in sessions) / len(sessions) if any(s.productivity_rating for s in sessions) else 0
            
            # Calculate consistency (sessions per day)
            session_dates = set(s.created_at.date() for s in sessions)
            consistency_score = len(session_dates) / 30.0  # Days with sessions / total days
            
            # Calculate goal achievement (mock - would integrate with goal system)
            goal_achievement_rate = 0.8  # Mock value
            
            # Weighted productivity score
            productivity_score = (
                (total_time / 100) * 0.2 +  # Time factor
                completion_rate * 0.2 +     # Completion factor
                (focus_avg / 5) * 0.2 +     # Focus factor
                (productivity_avg / 5) * 0.2 +  # Productivity factor
                consistency_score * 0.1 +   # Consistency factor
                goal_achievement_rate * 0.1  # Goal factor
            ) * 100
            
            return min(max(productivity_score, 0.0), 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating productivity score: {str(e)}")
            raise
    
    async def get_productivity_insights(
        self,
        current_user: CurrentUser,
        db: Session
    ) -> ProductivityInsights:
        """Get productivity insights for user"""
        try:
            # Get recent sessions
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            sessions = db.query(StudySession).filter(
                and_(
                    StudySession.user_id == current_user.user_id,
                    StudySession.created_at >= start_date,
                    StudySession.created_at <= end_date
                )
            ).all()
            
            # Calculate current streak
            current_streak = await self._calculate_study_streak(current_user, db)
            
            # Calculate best streak (mock - would need historical data)
            best_streak = max(current_streak, 7)  # Mock value
            
            # Calculate average daily study time
            session_dates = {}
            for session in sessions:
                date_key = session.created_at.date()
                if date_key not in session_dates:
                    session_dates[date_key] = 0
                session_dates[date_key] += session.actual_duration or 0
            
            if session_dates:
                average_daily_study_time = sum(session_dates.values()) / len(session_dates)
            else:
                average_daily_study_time = 0
            
            # Find most productive time
            time_distribution = await self._calculate_study_time_distribution(sessions)
            most_productive_time = max(time_distribution.items(), key=lambda x: x[1])[0] if time_distribution else "morning"
            
            # Find most productive subject
            subject_distribution = await self._calculate_subject_distribution(sessions)
            most_productive_subject = max(subject_distribution.items(), key=lambda x: x[1])[0] if subject_distribution else "General"
            
            # Generate improvement areas
            improvement_areas = []
            if average_daily_study_time < 60:  # Less than 1 hour
                improvement_areas.append("Increase daily study time")
            if current_streak < 3:
                improvement_areas.append("Build consistent study habits")
            if not any(s.focus_rating and s.focus_rating >= 4 for s in sessions):
                improvement_areas.append("Improve focus during sessions")
            
            # Generate recommendations
            recommendations = []
            if average_daily_study_time < 60:
                recommendations.append("Try studying in shorter, more frequent sessions")
            if current_streak < 3:
                recommendations.append("Set a daily study reminder")
            if not any(s.focus_rating and s.focus_rating >= 4 for s in sessions):
                recommendations.append("Use the Pomodoro technique to improve focus")
            
            # Determine weekly trend
            weekly_trend = "stable"  # Mock - would calculate from historical data
            
            return ProductivityInsights(
                current_streak=current_streak,
                best_streak=best_streak,
                average_daily_study_time=average_daily_study_time,
                most_productive_time=most_productive_time,
                most_productive_subject=most_productive_subject,
                improvement_areas=improvement_areas,
                recommendations=recommendations,
                weekly_trend=weekly_trend
            )
            
        except Exception as e:
            logger.error(f"Error getting productivity insights: {str(e)}")
            raise
    
    # Private helper methods
    
    def _calculate_duration(self, start_time: datetime, end_time: datetime) -> int:
        """Calculate duration in minutes"""
        duration = end_time - start_time
        return int(duration.total_seconds() / 60)
    
    async def _calculate_study_streak(self, current_user: CurrentUser, db: Session) -> int:
        """Calculate current study streak in days"""
        try:
            # Get all completed sessions
            sessions = db.query(StudySession).filter(
                and_(
                    StudySession.user_id == current_user.user_id,
                    StudySession.status == "completed"
                )
            ).order_by(desc(StudySession.created_at)).all()
            
            if not sessions:
                return 0
            
            # Group sessions by date
            session_dates = set(s.created_at.date() for s in sessions)
            session_dates = sorted(session_dates, reverse=True)
            
            # Calculate streak
            streak = 0
            current_date = datetime.utcnow().date()
            
            for session_date in session_dates:
                if current_date - session_date == timedelta(days=streak):
                    streak += 1
                else:
                    break
            
            return streak
            
        except Exception as e:
            logger.error(f"Error calculating study streak: {str(e)}")
            return 0
    
    async def _calculate_goal_progress(self, current_user: CurrentUser, db: Session, period: str) -> float:
        """Calculate goal progress percentage"""
        try:
            # Mock goal progress calculation
            # In production, this would integrate with goal tracking system
            if period == "week":
                return 75.0  # Mock 75% weekly goal progress
            elif period == "month":
                return 60.0  # Mock 60% monthly goal progress
            else:
                return 50.0  # Default 50%
                
        except Exception as e:
            logger.error(f"Error calculating goal progress: {str(e)}")
            return 0.0
    
    async def _calculate_study_time_distribution(self, sessions: List[StudySession]) -> Dict[str, int]:
        """Calculate study time distribution by time of day"""
        try:
            distribution = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
            
            for session in sessions:
                hour = session.created_at.hour
                if 6 <= hour < 12:
                    distribution["morning"] += 1
                elif 12 <= hour < 17:
                    distribution["afternoon"] += 1
                elif 17 <= hour < 22:
                    distribution["evening"] += 1
                else:
                    distribution["night"] += 1
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating study time distribution: {str(e)}")
            return {}
    
    async def _calculate_subject_distribution(self, sessions: List[StudySession]) -> Dict[str, int]:
        """Calculate study time distribution by subject"""
        try:
            distribution = {}
            
            for session in sessions:
                subject = session.subject or "General"
                duration = session.actual_duration or 0
                distribution[subject] = distribution.get(subject, 0) + duration
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating subject distribution: {str(e)}")
            return {}
    
    async def _calculate_session_type_distribution(self, sessions: List[StudySession]) -> Dict[str, int]:
        """Calculate study time distribution by session type"""
        try:
            distribution = {}
            
            for session in sessions:
                session_type = session.session_type or "study"
                distribution[session_type] = distribution.get(session_type, 0) + 1
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating session type distribution: {str(e)}")
            return {}
