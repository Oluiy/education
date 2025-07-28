"""
Content and Quiz Models for EduNerve Platform
Comprehensive content management with courses, lessons, quizzes, and progress tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"

class QuizType(str, Enum):
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    EXAM = "exam"
    WAEC = "waec"
    JAMB = "jamb"
    NECO = "neco"

class Subject(Base):
    """Subject categories"""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True)  # MATH, ENG, PHY, etc.
    description = Column(Text)
    icon = Column(String(100))  # emoji or icon identifier
    color = Column(String(7))  # hex color code
    
    # Educational level
    grade_levels = Column(JSON)  # ["grade-9", "grade-10", "grade-11", "grade-12"]
    exam_types = Column(JSON)  # ["waec", "jamb", "neco"]
    
    # Status
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    courses = relationship("Course", back_populates="subject")
    topics = relationship("Topic", back_populates="subject")

class Topic(Base):
    """Topic within subjects"""
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Content organization
    display_order = Column(Integer, default=0)
    difficulty_level = Column(String(20), default=DifficultyLevel.BEGINNER.value)
    estimated_duration = Column(Integer)  # in minutes
    
    # Learning objectives
    objectives = Column(JSON)  # List of learning objectives
    prerequisites = Column(JSON)  # List of prerequisite topic IDs
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="topics")
    lessons = relationship("Lesson", back_populates="topic")
    quizzes = relationship("Quiz", back_populates="topic")

class Course(Base):
    """Course structure"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    
    # Course metadata
    thumbnail_url = Column(String(255))
    banner_url = Column(String(255))
    instructor_name = Column(String(100))
    instructor_bio = Column(Text)
    
    # Course structure
    difficulty_level = Column(String(20), default=DifficultyLevel.BEGINNER.value)
    estimated_duration = Column(Integer)  # total minutes
    total_lessons = Column(Integer, default=0)
    total_quizzes = Column(Integer, default=0)
    
    # Content tags
    tags = Column(JSON)  # ["algebra", "equations", "problem-solving"]
    grade_levels = Column(JSON)  # ["grade-9", "grade-10"]
    
    # Pricing and access
    is_free = Column(Boolean, default=True)
    price = Column(Float, default=0.0)
    
    # Status
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = relationship("Subject", back_populates="courses")
    lessons = relationship("Lesson", back_populates="course")
    enrollments = relationship("CourseEnrollment", back_populates="course")

class Lesson(Base):
    """Individual lessons within courses"""
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content = Column(Text)  # HTML content
    
    # Lesson metadata
    content_type = Column(String(20), default=ContentType.TEXT.value)
    video_url = Column(String(255))
    video_duration = Column(Integer)  # in seconds
    thumbnail_url = Column(String(255))
    
    # Organization
    display_order = Column(Integer, default=0)
    estimated_duration = Column(Integer)  # in minutes
    difficulty_level = Column(String(20), default=DifficultyLevel.BEGINNER.value)
    
    # Learning objectives
    objectives = Column(JSON)
    prerequisites = Column(JSON)
    
    # Resources
    attachments = Column(JSON)  # File attachments
    external_links = Column(JSON)  # External resources
    
    # Status
    is_published = Column(Boolean, default=False)
    is_preview = Column(Boolean, default=False)  # Free preview lesson
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    topic = relationship("Topic", back_populates="lessons")
    progress = relationship("LessonProgress", back_populates="lesson")

class Quiz(Base):
    """Quiz and assessment structure"""
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    
    # Quiz configuration
    quiz_type = Column(String(20), default=QuizType.PRACTICE.value)
    difficulty_level = Column(String(20), default=DifficultyLevel.BEGINNER.value)
    
    # Timing and attempts
    time_limit = Column(Integer)  # in minutes
    max_attempts = Column(Integer, default=3)
    passing_score = Column(Float, default=70.0)  # percentage
    
    # Question configuration
    total_questions = Column(Integer, default=0)
    randomize_questions = Column(Boolean, default=True)
    show_correct_answers = Column(Boolean, default=True)
    immediate_feedback = Column(Boolean, default=True)
    
    # Exam-specific fields (WAEC, JAMB, NECO)
    exam_year = Column(Integer)
    exam_board = Column(String(20))  # WAEC, JAMB, NECO
    paper_number = Column(String(10))  # Paper 1, Paper 2, etc.
    
    # Status
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    topic = relationship("Topic", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    attempts = relationship("QuizAttempt", back_populates="quiz")

class Question(Base):
    """Individual quiz questions"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default="multiple_choice")  # multiple_choice, true_false, essay
    
    # Question metadata
    difficulty_level = Column(String(20), default=DifficultyLevel.BEGINNER.value)
    points = Column(Float, default=1.0)
    explanation = Column(Text)
    
    # Media content
    image_url = Column(String(255))
    audio_url = Column(String(255))
    
    # Organization
    display_order = Column(Integer, default=0)
    category = Column(String(100))  # algebra, geometry, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question")
    responses = relationship("QuestionResponse", back_populates="question")

class QuestionOption(Base):
    """Answer options for questions"""
    __tablename__ = "question_options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    explanation = Column(Text)
    
    # Organization
    display_order = Column(Integer, default=0)
    option_label = Column(String(5))  # A, B, C, D
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship("Question", back_populates="options")

class CourseEnrollment(Base):
    """User course enrollment tracking"""
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    
    # Enrollment status
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    last_accessed_at = Column(DateTime)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    lessons_completed = Column(Integer, default=0)
    quizzes_completed = Column(Integer, default=0)
    current_lesson_id = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    course = relationship("Course", back_populates="enrollments")

class LessonProgress(Base):
    """User lesson progress tracking"""
    __tablename__ = "lesson_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    
    # Progress details
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    last_position = Column(Integer, default=0)  # Video position in seconds
    
    # Status
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)  # in seconds
    
    # Relationships
    lesson = relationship("Lesson", back_populates="progress")

class QuizAttempt(Base):
    """User quiz attempt records"""
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    
    # Attempt details
    attempt_number = Column(Integer, default=1)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Results
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    passed = Column(Boolean, default=False)
    
    # Timing
    time_spent = Column(Integer)  # in seconds
    time_limit = Column(Integer)  # in seconds
    
    # Status
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    responses = relationship("QuestionResponse", back_populates="attempt")

class QuestionResponse(Base):
    """User responses to individual questions"""
    __tablename__ = "question_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    
    # Response data
    selected_option_id = Column(Integer, ForeignKey("question_options.id"))
    response_text = Column(Text)  # For essay questions
    is_correct = Column(Boolean, default=False)
    points_earned = Column(Float, default=0.0)
    
    # Timing
    time_spent = Column(Integer)  # in seconds
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("Question", back_populates="responses")
