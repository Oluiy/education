from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Content(Base):
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content_type = Column(String(50), nullable=False)  # video, document, quiz, etc.
    content_url = Column(String(500))
    content_metadata = Column(JSON)
    tags = Column(String(500))
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced
    estimated_duration = Column(Integer)  # in minutes
    is_published = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Quiz(Base):
    __tablename__ = "quiz"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content_id = Column(Integer, ForeignKey("content.id"))
    time_limit = Column(Integer)  # in minutes
    passing_score = Column(Float, default=70.0)
    max_attempts = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"))
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)  # multiple_choice, true_false, short_answer
    correct_answer = Column(Text, nullable=False)
    options = Column(JSON)  # For multiple choice questions
    points = Column(Integer, default=1)
    explanation = Column(Text)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Float)
    max_score = Column(Float)
    percentage = Column(Float)
    time_taken = Column(Integer)  # in minutes
    is_completed = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    answers = Column(JSON)  # Store user answers

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    submission_type = Column(String(50))  # assignment, project, etc.
    file_path = Column(String(500))
    submission_text = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    is_graded = Column(Boolean, default=False)

class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    grade_value = Column(Float)
    max_grade = Column(Float)
    feedback = Column(Text)
    graded_by = Column(Integer, ForeignKey("users.id"))
    graded_at = Column(DateTime, default=datetime.utcnow)

class ContentStats(Base):
    __tablename__ = "content_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"))
    view_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_time_spent = Column(Integer, default=0)  # in minutes
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    instructor_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String(100))
    difficulty_level = Column(String(20))
    duration = Column(Integer)  # in hours
    price = Column(Float, default=0.0)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String(200), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"))
    order_index = Column(Integer, default=0)
    duration = Column(Integer)  # in minutes
    is_preview = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    progress_percentage = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    is_completed = Column(Boolean, default=False)
    time_spent = Column(Integer, default=0)  # in minutes
    completed_at = Column(DateTime)
    last_accessed = Column(DateTime, default=datetime.utcnow)
