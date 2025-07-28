"""
Study Session Service
Business logic for study session management, analytics, and badges
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import logging

from ..models.study_models import (
    StudySession, StudyStreak, Badge, StudentBadge, StudyGoal,
    StudySessionStatus, BadgeType
)
from ..schemas.study_schemas import (
    StudySessionStart, StudySessionEnd, StudySessionUpdate,
    StudyGoalCreate, StudyGoalUpdate, BadgeCreate,
    StudyAnalytics, StudyDashboard
)

logger = logging.getLogger(__name__)


class StudySessionService:
    """Service for managing study sessions and related analytics"""
    
    @staticmethod
    def start_session(
        db: Session,
        student_id: int,
        school_id: int,
        session_data: StudySessionStart
    ) -> StudySession:
        """Start a new study session"""
        try:
            # Check for existing active session
            existing_session = db.query(StudySession).filter(
                StudySession.student_id == student_id,
                StudySession.status == StudySessionStatus.ACTIVE.value
            ).first()
            
            if existing_session:
                # Auto-end the existing session
                StudySessionService.end_session(
                    db, existing_session.id, student_id,
                    StudySessionEnd(status=StudySessionStatus.TIMEOUT)
                )
            
            # Create new session
            session = StudySession(
                student_id=student_id,
                school_id=school_id,
                subject_id=session_data.subject_id,
                lesson_id=session_data.lesson_id,
                quiz_id=session_data.quiz_id,
                planned_duration=session_data.planned_duration,
                device_type=session_data.device_type.value,
                is_auto_tracked=session_data.is_auto_tracked,
                notes=session_data.notes,
                status=StudySessionStatus.ACTIVE.value
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            logger.info(f"Started study session {session.id} for student {student_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start study session: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def end_session(
        db: Session,
        session_id: int,
        student_id: int,
        end_data: StudySessionEnd
    ) -> StudySession:
        """End an active study session"""
        try:
            session = db.query(StudySession).filter(
                StudySession.id == session_id,
                StudySession.student_id == student_id,
                StudySession.status == StudySessionStatus.ACTIVE.value
            ).first()
            
            if not session:
                raise ValueError("Active session not found")
            
            # Update session
            session.end_time = datetime.utcnow()
            session.actual_duration = session.calculate_duration()
            session.status = end_data.status.value
            session.interruptions = end_data.interruptions
            
            if end_data.notes:
                session.notes = end_data.notes
            
            # Calculate focus score
            session.focus_score = session.calculate_focus_score()
            
            db.commit()
            
            # Update streak and check for badges
            StudySessionService._update_streak(db, student_id, session.school_id, session)
            StudySessionService._check_badges(db, student_id, session.school_id, session)
            StudySessionService._update_goals(db, student_id, session)
            
            logger.info(f"Ended study session {session_id} for student {student_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to end study session: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def get_active_session(db: Session, student_id: int) -> Optional[StudySession]:
        """Get active study session for student"""
        return db.query(StudySession).filter(
            StudySession.student_id == student_id,
            StudySession.status == StudySessionStatus.ACTIVE.value
        ).first()
    
    @staticmethod
    def get_session_history(
        db: Session,
        student_id: int,
        limit: int = 50,
        offset: int = 0,
        subject_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[StudySession]:
        """Get study session history for student"""
        query = db.query(StudySession).filter(
            StudySession.student_id == student_id
        )
        
        if subject_id:
            query = query.filter(StudySession.subject_id == subject_id)
        
        if start_date:
            query = query.filter(StudySession.start_time >= start_date)
        
        if end_date:
            query = query.filter(StudySession.start_time <= end_date + timedelta(days=1))
        
        return query.order_by(desc(StudySession.start_time)).offset(offset).limit(limit).all()
    
    @staticmethod
    def timeout_expired_sessions(db: Session) -> int:
        """Timeout sessions that have been active for more than 4 hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=4)
            
            expired_sessions = db.query(StudySession).filter(
                StudySession.status == StudySessionStatus.ACTIVE.value,
                StudySession.start_time <= cutoff_time
            ).all()
            
            count = 0
            for session in expired_sessions:
                session.end_time = datetime.utcnow()
                session.actual_duration = session.calculate_duration()
                session.status = StudySessionStatus.TIMEOUT.value
                session.focus_score = session.calculate_focus_score()
                count += 1
            
            db.commit()
            logger.info(f"Timed out {count} expired study sessions")
            return count
            
        except Exception as e:
            logger.error(f"Failed to timeout expired sessions: {e}")
            db.rollback()
            return 0
    
    @staticmethod
    def _update_streak(
        db: Session,
        student_id: int,
        school_id: int,
        session: StudySession
    ):
        """Update student study streak"""
        try:
            streak = db.query(StudyStreak).filter(
                StudyStreak.student_id == student_id,
                StudyStreak.school_id == school_id
            ).first()
            
            if not streak:
                streak = StudyStreak(
                    student_id=student_id,
                    school_id=school_id,
                    week_start_date=datetime.utcnow()
                )
                db.add(streak)
            
            # Update streak
            streak.update_streak(session.start_time)
            
            # Update statistics
            streak.total_sessions += 1
            streak.total_minutes += session.actual_duration or 0
            
            if streak.total_sessions > 0:
                streak.average_session_duration = streak.total_minutes / streak.total_sessions
            
            # Update weekly progress
            if session.actual_duration:
                streak.weekly_completed_minutes += session.actual_duration
                
                # Reset weekly progress if new week
                if streak.week_start_date:
                    days_since_week_start = (datetime.utcnow() - streak.week_start_date).days
                    if days_since_week_start >= 7:
                        streak.reset_weekly_progress()
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update streak: {e}")
            db.rollback()
    
    @staticmethod
    def _check_badges(
        db: Session,
        student_id: int,
        school_id: int,
        session: StudySession
    ):
        """Check and award badges based on session"""
        try:
            streak = db.query(StudyStreak).filter(
                StudyStreak.student_id == student_id,
                StudyStreak.school_id == school_id
            ).first()
            
            if not streak:
                return
            
            # Get all badges
            badges = db.query(Badge).all()
            
            # Get already earned badges
            earned_badge_ids = {
                badge.badge_id for badge in db.query(StudentBadge).filter(
                    StudentBadge.student_id == student_id
                ).all()
            }
            
            # Check each badge
            for badge in badges:
                if badge.id in earned_badge_ids:
                    continue
                
                earned = False
                achievement_value = 0
                
                if badge.badge_type == BadgeType.STREAK.value:
                    if badge.requirement_type == "consecutive_days":
                        if streak.current_streak >= badge.requirement_value:
                            earned = True
                            achievement_value = streak.current_streak
                
                elif badge.badge_type == BadgeType.DURATION.value:
                    if badge.requirement_type == "single_session_minutes":
                        if session.actual_duration and session.actual_duration >= badge.requirement_value:
                            earned = True
                            achievement_value = session.actual_duration
                    elif badge.requirement_type == "total_minutes":
                        if streak.total_minutes >= badge.requirement_value:
                            earned = True
                            achievement_value = streak.total_minutes
                
                elif badge.badge_type == BadgeType.FOCUS.value:
                    if badge.requirement_type == "focus_score":
                        if session.focus_score and session.focus_score >= badge.requirement_value:
                            earned = True
                            achievement_value = int(session.focus_score)
                
                elif badge.badge_type == BadgeType.CONSISTENCY.value:
                    if badge.requirement_type == "total_sessions":
                        if streak.total_sessions >= badge.requirement_value:
                            earned = True
                            achievement_value = streak.total_sessions
                
                if earned:
                    student_badge = StudentBadge(
                        student_id=student_id,
                        school_id=school_id,
                        badge_id=badge.id,
                        study_session_id=session.id,
                        achievement_value=achievement_value
                    )
                    db.add(student_badge)
                    logger.info(f"Awarded badge {badge.name} to student {student_id}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to check badges: {e}")
            db.rollback()
    
    @staticmethod
    def _update_goals(db: Session, student_id: int, session: StudySession):
        """Update student study goals progress"""
        try:
            # Get active goals
            active_goals = db.query(StudyGoal).filter(
                StudyGoal.student_id == student_id,
                StudyGoal.is_achieved == False,
                StudyGoal.end_date >= datetime.utcnow()
            ).all()
            
            for goal in active_goals:
                if session.actual_duration:
                    goal.completed_minutes += session.actual_duration
                goal.completed_sessions += 1
                
                # Check if goal is achieved
                if (goal.completed_minutes >= goal.target_minutes and
                    (not goal.target_sessions or goal.completed_sessions >= goal.target_sessions)):
                    goal.is_achieved = True
                    goal.achieved_at = datetime.utcnow()
                    logger.info(f"Goal {goal.id} achieved by student {student_id}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update goals: {e}")
            db.rollback()
    
    @staticmethod
    def get_analytics(db: Session, student_id: int, school_id: int) -> StudyAnalytics:
        """Get comprehensive study analytics for student"""
        try:
            # Get streak data
            streak = db.query(StudyStreak).filter(
                StudyStreak.student_id == student_id,
                StudyStreak.school_id == school_id
            ).first()
            
            if not streak:
                # Return empty analytics
                return StudyAnalytics(
                    total_sessions=0,
                    total_minutes=0,
                    average_session_duration=0,
                    current_streak=0,
                    longest_streak=0,
                    weekly_progress=0,
                    monthly_minutes=0,
                    focus_score_average=0,
                    most_studied_subject=None,
                    preferred_device="web",
                    badges_earned=0,
                    goals_achieved=0,
                    weekly_minutes_by_day={},
                    subject_distribution={}
                )
            
            # Monthly minutes
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_sessions = db.query(StudySession).filter(
                StudySession.student_id == student_id,
                StudySession.start_time >= month_start,
                StudySession.status.in_([StudySessionStatus.COMPLETED.value, StudySessionStatus.TIMEOUT.value])
            ).all()
            
            monthly_minutes = sum(s.actual_duration or 0 for s in monthly_sessions)
            
            # Average focus score
            focus_scores = [s.focus_score for s in monthly_sessions if s.focus_score is not None]
            focus_score_average = sum(focus_scores) / len(focus_scores) if focus_scores else 0
            
            # Most studied subject (this would need subject relationship)
            # For now, returning None
            most_studied_subject = None
            
            # Preferred device
            device_counts = {}
            for session in monthly_sessions:
                device_counts[session.device_type] = device_counts.get(session.device_type, 0) + 1
            preferred_device = max(device_counts, key=device_counts.get) if device_counts else "web"
            
            # Badges earned
            badges_earned = db.query(StudentBadge).filter(
                StudentBadge.student_id == student_id
            ).count()
            
            # Goals achieved
            goals_achieved = db.query(StudyGoal).filter(
                StudyGoal.student_id == student_id,
                StudyGoal.is_achieved == True
            ).count()
            
            # Weekly progress
            weekly_progress = 0
            if streak.weekly_target_minutes > 0:
                weekly_progress = (streak.weekly_completed_minutes / streak.weekly_target_minutes) * 100
            
            return StudyAnalytics(
                total_sessions=streak.total_sessions,
                total_minutes=streak.total_minutes,
                average_session_duration=streak.average_session_duration,
                current_streak=streak.current_streak,
                longest_streak=streak.longest_streak,
                weekly_progress=min(100, weekly_progress),
                monthly_minutes=monthly_minutes,
                focus_score_average=round(focus_score_average, 1),
                most_studied_subject=most_studied_subject,
                preferred_device=preferred_device,
                badges_earned=badges_earned,
                goals_achieved=goals_achieved,
                weekly_minutes_by_day={},  # Would need detailed implementation
                subject_distribution={}    # Would need subject relationship
            )
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            raise


class StudyGoalService:
    """Service for managing study goals"""
    
    @staticmethod
    def create_goal(
        db: Session,
        student_id: int,
        school_id: int,
        goal_data: StudyGoalCreate
    ) -> StudyGoal:
        """Create a new study goal"""
        try:
            goal = StudyGoal(
                student_id=student_id,
                school_id=school_id,
                title=goal_data.title,
                description=goal_data.description,
                target_minutes=goal_data.target_minutes,
                target_sessions=goal_data.target_sessions,
                start_date=goal_data.start_date,
                end_date=goal_data.end_date
            )
            
            db.add(goal)
            db.commit()
            db.refresh(goal)
            
            logger.info(f"Created study goal {goal.id} for student {student_id}")
            return goal
            
        except Exception as e:
            logger.error(f"Failed to create study goal: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def get_student_goals(
        db: Session,
        student_id: int,
        active_only: bool = False
    ) -> List[StudyGoal]:
        """Get study goals for student"""
        query = db.query(StudyGoal).filter(StudyGoal.student_id == student_id)
        
        if active_only:
            query = query.filter(
                StudyGoal.is_achieved == False,
                StudyGoal.end_date >= datetime.utcnow()
            )
        
        return query.order_by(desc(StudyGoal.created_at)).all()


class BadgeService:
    """Service for managing badges"""
    
    @staticmethod
    def create_badge(db: Session, badge_data: BadgeCreate) -> Badge:
        """Create a new badge"""
        try:
            badge = Badge(
                name=badge_data.name,
                description=badge_data.description,
                badge_type=badge_data.badge_type.value,
                requirement_value=badge_data.requirement_value,
                requirement_type=badge_data.requirement_type,
                icon_url=badge_data.icon_url,
                color=badge_data.color,
                rarity=badge_data.rarity
            )
            
            db.add(badge)
            db.commit()
            db.refresh(badge)
            
            logger.info(f"Created badge {badge.id}: {badge.name}")
            return badge
            
        except Exception as e:
            logger.error(f"Failed to create badge: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def get_student_badges(db: Session, student_id: int) -> List[StudentBadge]:
        """Get badges earned by student"""
        return db.query(StudentBadge).filter(
            StudentBadge.student_id == student_id
        ).order_by(desc(StudentBadge.earned_at)).all()
