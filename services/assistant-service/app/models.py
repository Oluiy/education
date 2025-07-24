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
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudyResource(Base):
    __tablename__ = "study_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    resource_type = Column(String(50), nullable=False)  # video, article, pdf, etc.
    url = Column(String(500))
    content = Column(Text)
    subject = Column(String(100))
    difficulty_level = Column(String(20))
    tags = Column(String(500))
    rating = Column(Float, default=0.0)
    view_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(100), index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    context = Column(JSON)
    feedback_rating = Column(Integer)  # 1-5 rating
    created_at = Column(DateTime, default=datetime.utcnow)

class StudyPlan(Base):
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    subjects = Column(JSON)  # List of subjects
    difficulty_level = Column(String(20))
    estimated_duration = Column(Integer)  # in days
    goals = Column(JSON)
    progress = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudentActivity(Base):
    __tablename__ = "student_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String(50), nullable=False)  # study, quiz, assignment, etc.
    activity_data = Column(JSON)
    duration = Column(Integer)  # in minutes
    score = Column(Float)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class LearningAnalytics(Base):
    __tablename__ = "learning_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String(100))
    total_study_time = Column(Integer, default=0)  # in minutes
    average_score = Column(Float, default=0.0)
    topics_covered = Column(JSON)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
