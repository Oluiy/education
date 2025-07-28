"""
Progress Analytics Models
Advanced models for tracking learning progress and analytics
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class StudentProgress(Base):
    """
    Comprehensive student progress tracking
    """
    __tablename__ = "student_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    subject_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    
    # Progress metrics
    total_lessons = Column(Integer, default=0)
    completed_lessons = Column(Integer, default=0)
    total_quizzes = Column(Integer, default=0)
    completed_quizzes = Column(Integer, default=0)
    average_quiz_score = Column(Float, default=0.0)
    time_spent_minutes = Column(Integer, default=0)
    
    # Learning analytics
    learning_velocity = Column(Float, default=0.0)  # lessons/day
    retention_rate = Column(Float, default=0.0)    # % of knowledge retained
    difficulty_preference = Column(String(20), default="intermediate")
    preferred_learning_time = Column(String(50))   # e.g., "morning", "afternoon"
    
    # Engagement metrics
    login_frequency = Column(Float, default=0.0)   # days active per week
    session_duration_avg = Column(Integer, default=0)  # average session minutes
    help_requests = Column(Integer, default=0)
    resource_downloads = Column(Integer, default=0)
    
    # Performance trends
    performance_trend = Column(String(20), default="stable")  # improving, declining, stable
    last_activity_date = Column(DateTime)
    completion_prediction = Column(Float, default=0.0)  # predicted completion %
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_student_progress_user_subject', 'user_id', 'subject_id'),
        Index('idx_student_progress_school_course', 'school_id', 'course_id'),
        Index('idx_student_progress_performance', 'performance_trend', 'completion_prediction'),
    )


class LearningSession(Base):
    """
    Individual learning session tracking
    """
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Session details
    session_type = Column(String(50), nullable=False)  # lesson, quiz, practice, review
    content_id = Column(Integer, nullable=False)  # lesson_id, quiz_id, etc.
    content_type = Column(String(50), nullable=False)
    
    # Time tracking
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer, default=0)
    active_time_minutes = Column(Integer, default=0)  # time actually engaged
    
    # Interaction metrics
    clicks = Column(Integer, default=0)
    scrolls = Column(Integer, default=0)
    pauses = Column(Integer, default=0)
    video_plays = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    
    # Performance in session
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    help_requests = Column(Integer, default=0)
    completion_status = Column(String(20), default="in_progress")
    
    # Device and context
    device_type = Column(String(50))  # desktop, mobile, tablet
    browser = Column(String(100))
    ip_address = Column(String(45))
    location = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for analytics
    __table_args__ = (
        Index('idx_session_user_time', 'user_id', 'start_time'),
        Index('idx_session_content', 'content_type', 'content_id'),
        Index('idx_session_school_date', 'school_id', 'start_time'),
    )


class LearningPath(Base):
    """
    Personalized learning paths for students
    """
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Path details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    path_type = Column(String(50), default="personalized")  # recommended, custom, remedial
    
    # Content sequence
    subjects = Column(JSON)  # List of subject IDs in order
    courses = Column(JSON)   # List of course IDs in order
    lessons = Column(JSON)   # List of lesson IDs in order
    quizzes = Column(JSON)   # List of quiz IDs in order
    
    # Progress tracking
    current_position = Column(Integer, default=0)
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    
    # Difficulty and pacing
    difficulty_level = Column(String(20), default="intermediate")
    estimated_duration_days = Column(Integer, default=30)
    recommended_daily_time = Column(Integer, default=60)  # minutes
    
    # Adaptive features
    adapt_to_performance = Column(Boolean, default=True)
    skip_mastered_content = Column(Boolean, default=True)
    include_remedial_content = Column(Boolean, default=True)
    
    # Status
    status = Column(String(20), default="active")  # active, completed, paused, abandoned
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    started_at = Column(DateTime)
    expected_completion = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Achievement(Base):
    """
    Student achievements and badges
    """
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Achievement details
    achievement_type = Column(String(50), nullable=False)  # badge, certificate, milestone
    achievement_name = Column(String(200), nullable=False)
    achievement_description = Column(Text)
    
    # Achievement criteria
    category = Column(String(50))  # academic, engagement, progress, special
    difficulty = Column(String(20), default="bronze")  # bronze, silver, gold, platinum
    points_awarded = Column(Integer, default=0)
    
    # Context
    subject_id = Column(Integer)
    course_id = Column(Integer)
    quiz_id = Column(Integer)
    
    # Requirements met
    criteria_met = Column(JSON)  # Details of what was accomplished
    verification_data = Column(JSON)  # Proof/evidence of achievement
    
    # Sharing and display
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    
    # Timestamps
    earned_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # For time-limited achievements
    created_at = Column(DateTime, default=datetime.utcnow)


class PerformanceAlert(Base):
    """
    Automated alerts for performance issues or milestones
    """
    __tablename__ = "performance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # warning, success, milestone, intervention
    alert_title = Column(String(200), nullable=False)
    alert_message = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Context
    subject_id = Column(Integer)
    course_id = Column(Integer)
    trigger_data = Column(JSON)  # Data that triggered the alert
    
    # Recommendations
    recommended_actions = Column(JSON)  # List of suggested actions
    resources_suggested = Column(JSON)  # Helpful resources
    
    # Status
    status = Column(String(20), default="active")  # active, acknowledged, resolved, dismissed
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_methods = Column(JSON)  # email, in-app, sms
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningAnalytics(Base):
    """
    Aggregated learning analytics and insights
    """
    __tablename__ = "learning_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Time period
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Subject/Course context
    subject_id = Column(Integer)
    course_id = Column(Integer)
    
    # Engagement metrics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    
    # Content consumption
    lessons_completed = Column(Integer, default=0)
    quizzes_completed = Column(Integer, default=0)
    total_time_spent = Column(Integer, default=0)  # minutes
    avg_session_duration = Column(Float, default=0.0)
    
    # Performance metrics
    avg_quiz_score = Column(Float, default=0.0)
    pass_rate = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    dropout_rate = Column(Float, default=0.0)
    
    # Device and access patterns
    mobile_usage_percent = Column(Float, default=0.0)
    peak_usage_hour = Column(Integer, default=14)  # 2 PM
    weekend_usage_percent = Column(Float, default=0.0)
    
    # Geographic insights
    top_locations = Column(JSON)  # Most active locations
    
    # Generated insights
    insights = Column(JSON)  # AI-generated insights and recommendations
    trends = Column(JSON)    # Identified trends and patterns
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for reporting
    __table_args__ = (
        Index('idx_analytics_school_period', 'school_id', 'period_type', 'period_start'),
        Index('idx_analytics_subject_time', 'subject_id', 'period_start'),
    )


class StudyGroup(Base):
    """
    Collaborative learning groups
    """
    __tablename__ = "study_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Group details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    group_type = Column(String(50), default="study")  # study, project, peer_support
    
    # Academic context
    subject_id = Column(Integer)
    course_id = Column(Integer)
    grade_level = Column(String(20))
    
    # Group settings
    max_members = Column(Integer, default=10)
    is_public = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    
    # Activity tracking
    member_count = Column(Integer, default=0)
    active_members = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    avg_session_duration = Column(Integer, default=0)
    
    # Performance
    group_avg_score = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    collaboration_score = Column(Float, default=0.0)
    
    # Management
    created_by = Column(Integer, nullable=False)
    moderators = Column(JSON)  # List of user IDs
    
    # Status
    status = Column(String(20), default="active")  # active, inactive, archived
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
