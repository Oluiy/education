"""
Term Setup Models
Models for academic term setup and configuration
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
import json

Base = declarative_base()


class TermStatus(enum.Enum):
    """Term status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class WizardStep(enum.Enum):
    """Wizard step enumeration"""
    BASIC_INFO = "basic_info"
    ACADEMIC_CALENDAR = "academic_calendar"
    CLASS_SCHEDULE = "class_schedule"
    ASSESSMENT_CONFIG = "assessment_config"
    GRADING_SYSTEM = "grading_system"
    HOLIDAYS = "holidays"
    REVIEW = "review"


class Term(Base):
    """
    Academic term model
    Represents a school term/semester
    """
    __tablename__ = "terms"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True, nullable=False)
    
    # Basic info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    academic_year = Column(String(20), nullable=False)  # e.g., "2024/2025"
    term_number = Column(Integer, nullable=False)       # 1, 2, 3 for first, second, third term
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    registration_start = Column(Date, nullable=True)
    registration_end = Column(Date, nullable=True)
    
    # Status
    status = Column(String(20), default=TermStatus.DRAFT.value, nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)
    
    # Configuration
    total_weeks = Column(Integer, nullable=True)
    working_days_per_week = Column(Integer, default=5, nullable=False)
    periods_per_day = Column(Integer, default=8, nullable=False)
    period_duration = Column(Integer, default=40, nullable=False)  # minutes
    
    # Settings (JSON field for flexible configuration)
    settings = Column(JSON, default=dict, nullable=False)
    
    # Wizard tracking
    wizard_completed = Column(Boolean, default=False, nullable=False)
    completed_steps = Column(JSON, default=list, nullable=False)
    current_step = Column(String(20), default=WizardStep.BASIC_INFO.value, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)  # User ID
    
    # Relationships
    class_schedules = relationship("ClassSchedule", back_populates="term")
    assessments = relationship("Assessment", back_populates="term")
    holidays = relationship("Holiday", back_populates="term")
    grading_configs = relationship("GradingConfig", back_populates="term")
    
    def is_step_completed(self, step: str) -> bool:
        """Check if a wizard step is completed"""
        return step in (self.completed_steps or [])
    
    def complete_step(self, step: str):
        """Mark a wizard step as completed"""
        if not self.completed_steps:
            self.completed_steps = []
        if step not in self.completed_steps:
            self.completed_steps.append(step)
    
    def get_next_step(self) -> str:
        """Get the next wizard step"""
        all_steps = [step.value for step in WizardStep]
        current_index = all_steps.index(self.current_step)
        
        if current_index < len(all_steps) - 1:
            return all_steps[current_index + 1]
        return self.current_step  # Already at last step


class ClassSchedule(Base):
    """
    Class scheduling configuration
    """
    __tablename__ = "class_schedules"

    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    
    # Class info
    class_name = Column(String(100), nullable=False)
    class_level = Column(String(20), nullable=False)  # e.g., "JSS1", "SS2"
    section = Column(String(10), nullable=True)       # e.g., "A", "B"
    
    # Schedule template
    schedule_template = Column(JSON, nullable=False)  # Weekly schedule
    
    # Settings
    max_students = Column(Integer, nullable=True)
    class_teacher_id = Column(Integer, nullable=True)
    classroom = Column(String(50), nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    term = relationship("Term", back_populates="class_schedules")


class AssessmentConfig(Base):
    """
    Assessment configuration for the term
    """
    __tablename__ = "assessment_configs"

    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    
    # Assessment types and weights
    assessment_types = Column(JSON, nullable=False)  # e.g., {"CA1": 10, "CA2": 10, "Exam": 80}
    
    # Timing
    ca1_start_week = Column(Integer, nullable=True)
    ca1_end_week = Column(Integer, nullable=True)
    ca2_start_week = Column(Integer, nullable=True)
    ca2_end_week = Column(Integer, nullable=True)
    exam_start_week = Column(Integer, nullable=True)
    exam_end_week = Column(Integer, nullable=True)
    
    # Configuration
    passing_grade = Column(Float, default=40.0, nullable=False)
    max_score = Column(Float, default=100.0, nullable=False)
    
    # Settings
    allow_retakes = Column(Boolean, default=False, nullable=False)
    auto_calculate = Column(Boolean, default=True, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GradingConfig(Base):
    """
    Grading system configuration
    """
    __tablename__ = "grading_configs"

    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    
    # Grading system
    system_name = Column(String(100), nullable=False)  # e.g., "Nigerian Secondary School System"
    grading_scale = Column(JSON, nullable=False)       # Grade boundaries and meanings
    
    # Settings
    use_letter_grades = Column(Boolean, default=True, nullable=False)
    use_gpa = Column(Boolean, default=False, nullable=False)
    gpa_scale = Column(Float, default=4.0, nullable=True)
    
    # Comments
    auto_generate_comments = Column(Boolean, default=True, nullable=False)
    comment_templates = Column(JSON, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    term = relationship("Term", back_populates="grading_configs")


class Holiday(Base):
    """
    School holidays and important dates
    """
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    
    # Holiday info
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Type
    holiday_type = Column(String(20), nullable=False)  # public, school, exam, break
    is_school_closure = Column(Boolean, default=True, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    term = relationship("Term", back_populates="holidays")


class WizardSession(Base):
    """
    Track wizard session progress
    """
    __tablename__ = "wizard_sessions"

    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    
    # Session info
    session_token = Column(String(255), nullable=False, unique=True)
    current_step = Column(String(20), nullable=False)
    
    # Data
    step_data = Column(JSON, default=dict, nullable=False)  # Store data for each step
    validation_errors = Column(JSON, default=dict, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # Session expiry


class TermTemplate(Base):
    """
    Pre-defined term templates for quick setup
    """
    __tablename__ = "term_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    country = Column(String(50), nullable=False)
    education_level = Column(String(50), nullable=False)  # primary, secondary, tertiary
    
    # Template data
    template_data = Column(JSON, nullable=False)
    
    # Settings
    is_public = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, nullable=False)


class CalendarEvent(Base):
    """
    Calendar events for the term
    """
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    term_id = Column(Integer, nullable=False)
    school_id = Column(Integer, index=True, nullable=False)
    
    # Event info
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False)  # academic, exam, holiday, meeting, etc.
    
    # Timing
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(String(10), nullable=True)  # HH:MM format
    end_time = Column(String(10), nullable=True)
    is_all_day = Column(Boolean, default=False, nullable=False)
    
    # Participants
    target_audience = Column(JSON, nullable=True)  # ["students", "teachers", "parents"]
    specific_classes = Column(JSON, nullable=True)  # Specific class IDs
    
    # Settings
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(JSON, nullable=True)  # For recurring events
    send_reminders = Column(Boolean, default=True, nullable=False)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(Integer, nullable=False)
