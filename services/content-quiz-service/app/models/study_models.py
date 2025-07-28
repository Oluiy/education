"""
Study Session Timer Models
Tracks student study sessions with analytics and badges
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

Base = declarative_base()


class StudySessionStatus(enum.Enum):
    """Study session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class DeviceType(enum.Enum):
    """Device type enumeration"""
    WEB = "web"
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


class StudySession(Base):
    """
    Study session tracking model
    Logs individual study sessions with timing and analytics
    """
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    
    # Session details
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=True)
    
    # Timing
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    planned_duration = Column(Integer, nullable=True)  # minutes
    actual_duration = Column(Integer, nullable=True)  # minutes
    
    # Session data
    status = Column(String(20), default=StudySessionStatus.ACTIVE.value, nullable=False)
    device_type = Column(String(20), default=DeviceType.WEB.value, nullable=False)
    is_auto_tracked = Column(Boolean, default=False, nullable=False)
    
    # Study content
    notes = Column(Text, nullable=True)
    focus_score = Column(Float, nullable=True)  # 0-100 based on activity
    interruptions = Column(Integer, default=0, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="study_sessions")
    lesson = relationship("Lesson", back_populates="study_sessions")
    quiz = relationship("Quiz", back_populates="study_sessions")
    student_badges = relationship("StudentBadge", back_populates="study_session")
    
    def calculate_duration(self):
        """Calculate session duration in minutes"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return 0
    
    def is_expired(self):
        """Check if session should be timed out (4 hours)"""
        if self.status == StudySessionStatus.ACTIVE.value:
            elapsed = datetime.utcnow() - self.start_time
            return elapsed > timedelta(hours=4)
        return False
    
    def calculate_focus_score(self):
        """Calculate focus score based on session metrics"""
        if not self.actual_duration:
            return 0
        
        # Base score from duration (longer sessions get higher base score)
        base_score = min(self.actual_duration / 60 * 20, 60)  # Max 60 from duration
        
        # Penalty for interruptions
        interruption_penalty = min(self.interruptions * 5, 30)
        
        # Bonus for planned vs actual duration alignment
        alignment_bonus = 0
        if self.planned_duration and self.actual_duration:
            deviation = abs(self.planned_duration - self.actual_duration) / self.planned_duration
            if deviation < 0.2:  # Within 20% of planned
                alignment_bonus = 20
        
        score = max(0, min(100, base_score - interruption_penalty + alignment_bonus))
        return round(score, 1)


class StudyStreak(Base):
    """
    Study streak tracking for badges and motivation
    """
    __tablename__ = "study_streaks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    
    # Streak data
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_study_date = Column(DateTime, nullable=True)
    
    # Weekly targets
    weekly_target_minutes = Column(Integer, default=420, nullable=False)  # 7 hours default
    weekly_completed_minutes = Column(Integer, default=0, nullable=False)
    week_start_date = Column(DateTime, nullable=True)
    
    # Statistics
    total_sessions = Column(Integer, default=0, nullable=False)
    total_minutes = Column(Integer, default=0, nullable=False)
    average_session_duration = Column(Float, default=0.0, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def update_streak(self, session_date: datetime):
        """Update streak based on new session"""
        if not self.last_study_date:
            self.current_streak = 1
            self.longest_streak = 1
        else:
            # Check if session is on consecutive day
            last_date = self.last_study_date.date()
            session_date_only = session_date.date()
            
            if session_date_only == last_date + timedelta(days=1):
                self.current_streak += 1
                self.longest_streak = max(self.longest_streak, self.current_streak)
            elif session_date_only > last_date + timedelta(days=1):
                self.current_streak = 1
            # Same day sessions don't change streak
        
        self.last_study_date = session_date
    
    def reset_weekly_progress(self):
        """Reset weekly progress for new week"""
        self.weekly_completed_minutes = 0
        self.week_start_date = datetime.utcnow()


class BadgeType(enum.Enum):
    """Badge type enumeration"""
    STREAK = "streak"
    DURATION = "duration"
    CONSISTENCY = "consistency"
    FOCUS = "focus"
    MILESTONE = "milestone"


class Badge(Base):
    """
    Available badges for study achievements
    """
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    badge_type = Column(String(20), nullable=False)
    
    # Requirements
    requirement_value = Column(Integer, nullable=False)  # e.g., 7 for 7-day streak
    requirement_type = Column(String(50), nullable=False)  # e.g., "consecutive_days"
    
    # Display
    icon_url = Column(String(255), nullable=True)
    color = Column(String(7), default="#FFD700", nullable=False)  # Gold default
    rarity = Column(String(20), default="common", nullable=False)  # common, rare, epic, legendary
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    student_badges = relationship("StudentBadge", back_populates="badge")


class StudentBadge(Base):
    """
    Badges earned by students
    """
    __tablename__ = "student_badges"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    study_session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=True)
    
    # Achievement details
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    achievement_value = Column(Integer, nullable=False)  # The value that earned the badge
    is_displayed = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    badge = relationship("Badge", back_populates="student_badges")
    study_session = relationship("StudySession", back_populates="student_badges")


class StudyGoal(Base):
    """
    Student study goals and targets
    """
    __tablename__ = "study_goals"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    
    # Goal details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_minutes = Column(Integer, nullable=False)
    target_sessions = Column(Integer, nullable=True)
    
    # Timeline
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Progress
    completed_minutes = Column(Integer, default=0, nullable=False)
    completed_sessions = Column(Integer, default=0, nullable=False)
    is_achieved = Column(Boolean, default=False, nullable=False)
    achieved_at = Column(DateTime, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def progress_percentage(self):
        """Calculate goal progress percentage"""
        if self.target_minutes == 0:
            return 0
        return min(100, (self.completed_minutes / self.target_minutes) * 100)
    
    def is_expired(self):
        """Check if goal deadline has passed"""
        return datetime.utcnow() > self.end_date
