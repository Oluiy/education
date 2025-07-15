"""
EduNerve Content & Quiz Service - Database Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.database import Base


class ContentType(PyEnum):
    """Content types"""
    PDF = "pdf"
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    PRESENTATION = "presentation"


class QuizType(PyEnum):
    """Quiz types"""
    MCQ = "mcq"
    THEORY = "theory"
    MIXED = "mixed"


class DifficultyLevel(PyEnum):
    """Difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SubmissionStatus(PyEnum):
    """Submission status"""
    PENDING = "pending"
    GRADED = "graded"
    REVIEWED = "reviewed"


class CourseStatus(PyEnum):
    """Course status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CourseDifficulty(PyEnum):
    """Course difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Content(Base):
    """Content model for storing notes, PDFs, and other materials"""
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)
    
    # File information
    file_path = Column(String(500), nullable=True)  # Local or cloud path
    file_url = Column(String(500), nullable=True)   # Public URL
    file_size = Column(Integer, nullable=True)      # Size in bytes
    file_hash = Column(String(64), nullable=True)   # For deduplication
    
    # Educational metadata
    subject = Column(String(100), nullable=False)
    class_level = Column(String(20), nullable=False)  # JSS1, JSS2, SS1, etc.
    topic = Column(String(200), nullable=True)
    keywords = Column(Text, nullable=True)  # JSON array of keywords
    
    # Multi-tenant
    school_id = Column(Integer, nullable=False)
    uploaded_by = Column(Integer, nullable=False)  # User ID
    
    # Content text (extracted from PDF or direct input)
    content_text = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # Can be shared across schools
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    quizzes = relationship("Quiz", back_populates="content")


class Quiz(Base):
    """Quiz model for storing questions and assessments"""
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Quiz configuration
    quiz_type = Column(Enum(QuizType), nullable=False, default=QuizType.MCQ)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False, default=DifficultyLevel.MEDIUM)
    total_questions = Column(Integer, nullable=False, default=0)
    duration_minutes = Column(Integer, nullable=True)  # Time limit
    
    # Educational metadata
    subject = Column(String(100), nullable=False)
    class_level = Column(String(20), nullable=False)
    topic = Column(String(200), nullable=True)
    
    # Multi-tenant
    school_id = Column(Integer, nullable=False)
    created_by = Column(Integer, nullable=False)  # User ID
    
    # Content association
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=True)
    
    # Quiz questions (JSON structure)
    questions = Column(JSON, nullable=False)  # Array of question objects
    
    # Grading configuration
    total_marks = Column(Float, nullable=False, default=0.0)
    pass_mark = Column(Float, nullable=False, default=50.0)
    
    # AI generation metadata
    is_ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text, nullable=True)
    generation_model = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    content = relationship("Content", back_populates="quizzes")
    submissions = relationship("Submission", back_populates="quiz")


class Submission(Base):
    """Student quiz submissions"""
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(Integer, nullable=False)  # User ID
    school_id = Column(Integer, nullable=False)
    
    # Submission data
    answers = Column(JSON, nullable=False)  # Student answers
    submission_time = Column(DateTime(timezone=True), server_default=func.now())
    time_taken_minutes = Column(Integer, nullable=True)
    
    # Grading
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING)
    total_score = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)
    
    # Detailed scores
    mcq_score = Column(Float, nullable=True)
    theory_score = Column(Float, nullable=True)
    
    # AI grading for theory questions
    ai_feedback = Column(JSON, nullable=True)  # AI-generated feedback
    teacher_feedback = Column(Text, nullable=True)
    
    # Timestamps
    graded_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="submissions")
    grades = relationship("Grade", back_populates="submission")


class Grade(Base):
    """Individual question grades within a submission"""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_id = Column(String(50), nullable=False)  # Question identifier within quiz
    
    # Grading details
    student_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    marks_awarded = Column(Float, nullable=False, default=0.0)
    max_marks = Column(Float, nullable=False)
    
    # AI grading details
    is_ai_graded = Column(Boolean, default=False)
    ai_confidence = Column(Float, nullable=True)  # 0-1 confidence score
    ai_explanation = Column(Text, nullable=True)
    
    # Manual review
    is_manually_reviewed = Column(Boolean, default=False)
    reviewer_id = Column(Integer, nullable=True)  # Teacher user ID
    review_notes = Column(Text, nullable=True)
    
    # Timestamps
    graded_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    submission = relationship("Submission", back_populates="grades")


class QuizAttempt(Base):
    """Track quiz attempts for analytics"""
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(Integer, nullable=False)
    school_id = Column(Integer, nullable=False)
    
    # Attempt details
    attempt_number = Column(Integer, nullable=False, default=1)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_timed_out = Column(Boolean, default=False)
    
    # Device info for offline sync
    device_id = Column(String(100), nullable=True)
    sync_status = Column(String(20), default="synced")  # synced, pending, failed


class ContentStats(Base):
    """Content usage statistics"""
    __tablename__ = "content_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False)
    school_id = Column(Integer, nullable=False)
    
    # Statistics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    quiz_generation_count = Column(Integer, default=0)
    
    # Timestamps
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Course(Base):
    """Course model for organizing content and lessons"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    difficulty = Column(Enum(CourseDifficulty), nullable=False, default=CourseDifficulty.BEGINNER)
    duration = Column(String(50), nullable=True)  # e.g., "8 weeks", "3 months"
    
    # Course content
    objectives = Column(JSON, nullable=True)  # Learning objectives array
    prerequisites = Column(JSON, nullable=True)  # Prerequisites array
    thumbnail = Column(String(500), nullable=True)
    
    # Pricing
    price = Column(Float, nullable=False, default=0.0)
    is_free = Column(Boolean, default=True)
    
    # Multi-tenant and ownership
    instructor_id = Column(Integer, nullable=False)  # Teacher who created the course
    school_id = Column(Integer, nullable=False)
    
    # Status
    status = Column(Enum(CourseStatus), nullable=False, default=CourseStatus.DRAFT)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    """Lesson model for course content"""
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in minutes
    order = Column(Integer, nullable=False, default=0)  # Lesson order in course
    
    # Content
    video_url = Column(String(500), nullable=True)
    content_text = Column(Text, nullable=True)
    resources = Column(JSON, nullable=True)  # Array of resource URLs
    
    # Status
    is_published = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    progress = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")


class CourseEnrollment(Base):
    """Course enrollment tracking"""
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    student_id = Column(Integer, nullable=False)  # User ID
    
    # Enrollment details
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    completed_lessons = Column(Integer, default=0)
    
    # Relationships
    course = relationship("Course", back_populates="enrollments")


class LessonProgress(Base):
    """Individual lesson progress tracking"""
    __tablename__ = "lesson_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    student_id = Column(Integer, nullable=False)  # User ID
    
    # Progress details
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed = Column(Boolean, default=False)
    time_spent = Column(Integer, default=0)  # Time spent in minutes
    
    # Relationships
    lesson = relationship("Lesson", back_populates="progress")
