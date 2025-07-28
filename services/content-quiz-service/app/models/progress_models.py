"""
Study Session and Progress Models for EduNerve Platform
Pomodoro timer, study sessions, and learning analytics
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class SessionType(str, Enum):
    STUDY = "study"
    BREAK = "break"
    LONG_BREAK = "long_break"
    QUIZ = "quiz"
    READING = "reading"
    PRACTICE = "practice"

class SessionStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StudySession(Base):
    """Pomodoro study sessions"""
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Session configuration
    session_type = Column(String(20), default=SessionType.STUDY.value)
    planned_duration = Column(Integer)  # in minutes
    actual_duration = Column(Integer)  # in minutes
    
    # Session content
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    
    # Session details
    title = Column(String(200))
    description = Column(Text)
    goals = Column(JSON)  # List of session goals
    
    # Timing
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    paused_duration = Column(Integer, default=0)  # total pause time in seconds
    
    # Status and tracking
    status = Column(String(20), default=SessionStatus.PLANNED.value)
    completed_goals = Column(JSON)  # List of completed goals
    notes = Column(Text)
    
    # Performance metrics
    focus_rating = Column(Integer)  # 1-5 rating
    productivity_rating = Column(Integer)  # 1-5 rating
    difficulty_rating = Column(Integer)  # 1-5 rating
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    breaks = relationship("StudyBreak", back_populates="session")
    activities = relationship("SessionActivity", back_populates="session")

class StudyBreak(Base):
    """Break periods during study sessions"""
    __tablename__ = "study_breaks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("study_sessions.id"))
    
    # Break details
    break_type = Column(String(20), default=SessionType.BREAK.value)
    planned_duration = Column(Integer)  # in minutes
    actual_duration = Column(Integer)  # in minutes
    
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Break activities
    activities = Column(JSON)  # ["walk", "water", "snack"]
    notes = Column(Text)
    
    # Relationships
    session = relationship("StudySession", back_populates="breaks")

class SessionActivity(Base):
    """Activities performed during study sessions"""
    __tablename__ = "session_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("study_sessions.id"))
    
    # Activity details
    activity_type = Column(String(50))  # reading, note_taking, quiz, practice
    activity_name = Column(String(200))
    duration = Column(Integer)  # in seconds
    
    # Content reference
    resource_type = Column(String(50))  # lesson, quiz, external
    resource_id = Column(Integer)
    
    # Performance
    completion_percentage = Column(Float, default=0.0)
    quality_rating = Column(Integer)  # 1-5 rating
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    session = relationship("StudySession", back_populates="activities")

class StudyPlan(Base):
    """User study plans and schedules"""
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Plan details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Timeline
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    target_hours_per_day = Column(Float, default=2.0)
    target_sessions_per_day = Column(Integer, default=4)
    
    # Content coverage
    subjects = Column(JSON)  # List of subject IDs
    topics = Column(JSON)  # List of topic IDs
    goals = Column(JSON)  # List of learning goals
    
    # Plan status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    milestones = relationship("StudyMilestone", back_populates="plan")

class StudyMilestone(Base):
    """Milestones within study plans"""
    __tablename__ = "study_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id"))
    
    # Milestone details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target_date = Column(DateTime)
    
    # Requirements
    required_sessions = Column(Integer)
    required_hours = Column(Float)
    required_topics = Column(JSON)  # List of topic IDs
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    completion_percentage = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plan = relationship("StudyPlan", back_populates="milestones")

class LearningPath(Base):
    """Personalized learning paths"""
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Path details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    difficulty_level = Column(String(20))
    
    # Path structure
    total_lessons = Column(Integer, default=0)
    total_quizzes = Column(Integer, default=0)
    estimated_duration = Column(Integer)  # in hours
    
    # Progress tracking
    current_step = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    lessons_completed = Column(Integer, default=0)
    quizzes_completed = Column(Integer, default=0)
    
    # Personalization
    learning_style = Column(String(50))  # visual, auditory, kinesthetic
    pace = Column(String(20))  # slow, medium, fast
    preferences = Column(JSON)  # Content type preferences
    
    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    steps = relationship("LearningPathStep", back_populates="path")

class LearningPathStep(Base):
    """Individual steps in learning paths"""
    __tablename__ = "learning_path_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"))
    
    # Step details
    step_number = Column(Integer, nullable=False)
    title = Column(String(200))
    description = Column(Text)
    
    # Content reference
    content_type = Column(String(50))  # lesson, quiz, exercise
    content_id = Column(Integer)
    estimated_duration = Column(Integer)  # in minutes
    
    # Requirements
    prerequisites = Column(JSON)  # List of prerequisite step IDs
    required_score = Column(Float)  # Minimum score to pass
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    attempts = Column(Integer, default=0)
    best_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    path = relationship("LearningPath", back_populates="steps")

class ProgressSnapshot(Base):
    """Daily/weekly progress snapshots"""
    __tablename__ = "progress_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Snapshot details
    date = Column(DateTime, nullable=False)
    period_type = Column(String(20))  # daily, weekly, monthly
    
    # Study metrics
    total_study_time = Column(Float, default=0.0)  # in hours
    sessions_completed = Column(Integer, default=0)
    average_session_duration = Column(Float, default=0.0)
    
    # Content progress
    lessons_completed = Column(Integer, default=0)
    quizzes_taken = Column(Integer, default=0)
    average_quiz_score = Column(Float, default=0.0)
    
    # Performance metrics
    focus_rating = Column(Float, default=0.0)  # average 1-5
    productivity_rating = Column(Float, default=0.0)  # average 1-5
    streak_days = Column(Integer, default=0)
    
    # Goals and achievements
    daily_goal_met = Column(Boolean, default=False)
    weekly_goal_met = Column(Boolean, default=False)
    achievements_earned = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class StudyStreak(Base):
    """Study streak tracking"""
    __tablename__ = "study_streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Streak details
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    # Streak requirements
    min_study_time = Column(Float, default=0.5)  # minimum hours per day
    min_sessions = Column(Integer, default=1)  # minimum sessions per day
    
    # Status
    is_active = Column(Boolean, default=True)
    last_study_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudyGoal(Base):
    """User study goals"""
    __tablename__ = "study_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Goal details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    goal_type = Column(String(50))  # daily, weekly, monthly, exam_prep
    
    # Target metrics
    target_study_hours = Column(Float)
    target_sessions = Column(Integer)
    target_lessons = Column(Integer)
    target_quiz_score = Column(Float)
    
    # Timeline
    start_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime, nullable=False)
    
    # Progress
    current_progress = Column(Float, default=0.0)  # percentage
    is_achieved = Column(Boolean, default=False)
    achieved_at = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
