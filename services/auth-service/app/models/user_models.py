"""
Enhanced User Models for EduNerve Platform
Comprehensive user management with profiles, settings, and activity tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"

class User(Base):
    """Core user model with authentication data"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(20))
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    role = Column(String(20), default=UserRole.STUDENT.value)
    
    # Timestamps
    last_login = Column(DateTime)
    password_changed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    stats = relationship("UserStats", back_populates="user", uselist=False)
    activities = relationship("UserActivity", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")

class UserProfile(Base):
    """Extended user profile information"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Personal information
    avatar_url = Column(String(255))
    bio = Column(Text)
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    country = Column(String(50))
    city = Column(String(50))
    timezone = Column(String(50), default='UTC')
    
    # Educational information
    school = Column(String(100))
    grade_level = Column(String(20))
    subjects_of_interest = Column(JSON)  # List of subjects
    learning_style = Column(String(50))  # Visual, Auditory, Reading/Writing, Kinesthetic
    study_goals = Column(JSON)  # List of goals
    
    # Personalization quiz results
    quiz_completed = Column(Boolean, default=False)
    quiz_results = Column(JSON)  # Store quiz responses and analysis
    recommendations = Column(JSON)  # Personalized recommendations
    
    # Social links
    social_links = Column(JSON)  # {"linkedin": "url", "twitter": "url", etc.}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")

class UserSettings(Base):
    """User preferences and settings"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Privacy settings
    profile_visibility = Column(String(20), default='public')  # public, friends, private
    show_activity_status = Column(Boolean, default=True)
    show_email = Column(Boolean, default=False)
    show_phone = Column(Boolean, default=False)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    notification_frequency = Column(String(20), default='immediate')  # immediate, daily, weekly
    
    # Study preferences
    default_study_duration = Column(Integer, default=25)  # Pomodoro minutes
    default_break_duration = Column(Integer, default=5)
    sound_enabled = Column(Boolean, default=True)
    theme = Column(String(20), default='light')  # light, dark, auto
    language = Column(String(10), default='en')
    
    # Content preferences
    difficulty_level = Column(String(20), default='medium')
    content_type_preference = Column(JSON)  # video, text, interactive, etc.
    auto_play_videos = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="settings")

class UserStats(Base):
    """User statistics and progress tracking"""
    __tablename__ = "user_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Study statistics
    total_study_time = Column(Float, default=0.0)  # in hours
    study_streak = Column(Integer, default=0)  # consecutive days
    longest_streak = Column(Integer, default=0)
    sessions_completed = Column(Integer, default=0)
    
    # Quiz statistics
    quizzes_taken = Column(Integer, default=0)
    quizzes_passed = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    total_points_earned = Column(Integer, default=0)
    
    # Course statistics
    courses_enrolled = Column(Integer, default=0)
    courses_completed = Column(Integer, default=0)
    lessons_completed = Column(Integer, default=0)
    assignments_submitted = Column(Integer, default=0)
    
    # Engagement metrics
    login_count = Column(Integer, default=0)
    last_activity_date = Column(DateTime)
    active_days_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="stats")

class UserActivity(Base):
    """Activity log for user actions"""
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Activity details
    activity_type = Column(String(50))  # login, quiz_attempt, course_enrollment, etc.
    activity_title = Column(String(200))
    activity_description = Column(Text)
    
    # Context data
    resource_type = Column(String(50))  # course, quiz, assignment, etc.
    resource_id = Column(Integer)
    metadata = Column(JSON)  # Additional context data
    
    # Performance data
    score = Column(Float)
    duration = Column(Integer)  # in seconds
    success = Column(Boolean, default=True)
    
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activities")

class UserAchievement(Base):
    """User achievements and badges"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Achievement details
    achievement_id = Column(String(50))  # unique identifier for achievement type
    title = Column(String(100))
    description = Column(Text)
    icon = Column(String(100))  # emoji or icon identifier
    category = Column(String(50))  # study_time, quiz_score, streak, etc.
    
    # Achievement criteria
    criteria_type = Column(String(50))  # threshold, completion, consistency
    criteria_value = Column(Float)
    current_progress = Column(Float, default=0.0)
    
    # Status
    is_earned = Column(Boolean, default=False)
    earned_at = Column(DateTime)
    points_awarded = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="achievements")

class EmailVerification(Base):
    """Email verification tokens"""
    __tablename__ = "email_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String(100))
    token = Column(String(255), unique=True, index=True)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PasswordReset(Base):
    """Password reset tokens"""
    __tablename__ = "password_resets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String(100))
    token = Column(String(255), unique=True, index=True)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuthSession(Base):
    """JWT session management"""
    __tablename__ = "auth_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token_id = Column(String(255), unique=True, index=True)
    refresh_token = Column(String(255), unique=True, index=True)
    device_info = Column(JSON)  # browser, OS, etc.
    ip_address = Column(String(45))
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)

class DeviceToken(Base):
    """Firebase/Push notification device tokens"""
    __tablename__ = "device_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(500), unique=True)
    device_type = Column(String(20))  # ios, android, web
    device_info = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)
