"""
AI Assistant Models for EduNerve Platform
Chat sessions, conversation history, and AI interactions
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class ChatType(str, Enum):
    STUDY_HELP = "study_help"
    HOMEWORK_ASSISTANCE = "homework_assistance"
    CONCEPT_EXPLANATION = "concept_explanation"
    QUIZ_PREPARATION = "quiz_preparation"
    CAREER_GUIDANCE = "career_guidance"
    GENERAL = "general"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    VOICE = "voice"
    SYSTEM = "system"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ChatSession(Base):
    """AI Chat sessions"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Session identification
    session_id = Column(String(100), unique=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    
    # Session metadata
    chat_type = Column(String(50), default=ChatType.STUDY_HELP.value)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    
    # AI Configuration
    ai_model = Column(String(100), default="gpt-3.5-turbo")
    system_prompt = Column(Text)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1000)
    
    # Session context
    context_data = Column(JSON)  # Additional context for AI
    learning_objectives = Column(JSON)  # What user wants to learn
    difficulty_level = Column(String(20))
    
    # Status tracking
    status = Column(String(20), default=ChatStatus.ACTIVE.value)
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Quality metrics
    user_satisfaction = Column(Integer)  # 1-5 rating
    helpfulness_rating = Column(Integer)  # 1-5 rating
    session_feedback = Column(Text)
    
    # Features used
    features_used = Column(JSON)  # ["image_analysis", "document_upload", etc.]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session")
    feedback = relationship("SessionFeedback", back_populates="session")

class ChatMessage(Base):
    """Individual messages in chat sessions"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    
    # Message identification
    message_id = Column(String(100), unique=True, index=True)
    parent_message_id = Column(Integer, ForeignKey("chat_messages.id"))
    
    # Message content
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default=MessageType.TEXT.value)
    
    # Metadata
    tokens_used = Column(Integer, default=0)
    processing_time = Column(Float)  # in seconds
    model_used = Column(String(100))
    
    # Content analysis
    intent = Column(String(100))  # question, explanation_request, etc.
    confidence = Column(Float)  # AI confidence in response
    sentiment = Column(String(20))  # positive, negative, neutral
    
    # Attachments and media
    attachments = Column(JSON)  # File attachments
    image_urls = Column(JSON)  # Image URLs
    document_refs = Column(JSON)  # Referenced documents
    
    # Response quality
    flagged = Column(Boolean, default=False)
    flag_reason = Column(String(200))
    
    # User interaction
    liked = Column(Boolean)
    disliked = Column(Boolean)
    copied = Column(Boolean, default=False)
    shared = Column(Boolean, default=False)
    
    # Context preservation
    context_window = Column(JSON)  # Previous messages used for context
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    parent_message = relationship("ChatMessage", remote_side=[id])
    child_messages = relationship("ChatMessage", remote_side=[parent_message_id])

class SessionFeedback(Base):
    """User feedback on chat sessions"""
    __tablename__ = "session_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Overall ratings
    overall_rating = Column(Integer)  # 1-5 stars
    helpfulness = Column(Integer)  # 1-5
    accuracy = Column(Integer)  # 1-5
    clarity = Column(Integer)  # 1-5
    speed = Column(Integer)  # 1-5
    
    # Specific feedback
    positive_aspects = Column(JSON)  # ["clear explanations", "good examples"]
    negative_aspects = Column(JSON)  # ["too complex", "missing context"]
    improvement_suggestions = Column(Text)
    
    # Detailed comments
    comments = Column(Text)
    would_recommend = Column(Boolean)
    
    # Follow-up
    follow_up_needed = Column(Boolean, default=False)
    follow_up_reason = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="feedback")

class AIPromptTemplate(Base):
    """Reusable AI prompt templates"""
    __tablename__ = "ai_prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template identification
    template_name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200))
    description = Column(Text)
    category = Column(String(50))  # study_help, explanation, etc.
    
    # Prompt content
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text)
    
    # Configuration
    suggested_model = Column(String(100))
    suggested_temperature = Column(Float, default=0.7)
    suggested_max_tokens = Column(Integer, default=1000)
    
    # Template variables
    variables = Column(JSON)  # List of variables that can be substituted
    example_values = Column(JSON)  # Example values for variables
    
    # Usage and performance
    usage_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Versioning
    version = Column(String(20), default="1.0")
    parent_template_id = Column(Integer, ForeignKey("ai_prompt_templates.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_template = relationship("AIPromptTemplate", remote_side=[id])
    versions = relationship("AIPromptTemplate", remote_side=[parent_template_id])

class ConversationContext(Base):
    """Context management for conversations"""
    __tablename__ = "conversation_contexts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    
    # Context identification
    context_key = Column(String(100))  # "current_topic", "learning_goal", etc.
    context_value = Column(JSON)  # The actual context data
    
    # Context metadata
    priority = Column(Integer, default=1)  # Higher = more important
    expiry_messages = Column(Integer)  # Expire after N messages
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIAnalytics(Base):
    """Analytics for AI assistant usage"""
    __tablename__ = "ai_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    date = Column(DateTime, nullable=False)
    hour = Column(Integer)  # 0-23 for hourly analytics
    
    # Usage metrics
    total_sessions = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    
    # Performance metrics
    average_response_time = Column(Float, default=0.0)
    average_session_duration = Column(Float, default=0.0)
    average_messages_per_session = Column(Float, default=0.0)
    
    # Quality metrics
    average_user_rating = Column(Float, default=0.0)
    helpfulness_score = Column(Float, default=0.0)
    accuracy_score = Column(Float, default=0.0)
    
    # Content analysis
    top_subjects = Column(JSON)  # Most discussed subjects
    common_intents = Column(JSON)  # Most common user intents
    popular_features = Column(JSON)  # Most used features
    
    # Error tracking
    error_rate = Column(Float, default=0.0)
    timeout_rate = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class StudyRecommendation(Base):
    """AI-generated study recommendations"""
    __tablename__ = "study_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Recommendation details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    recommendation_type = Column(String(50))  # topic, course, practice, etc.
    
    # Target content
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    content_ids = Column(JSON)  # List of recommended content IDs
    
    # Recommendation context
    reason = Column(Text)  # Why this was recommended
    confidence = Column(Float)  # AI confidence in recommendation
    priority = Column(Integer, default=1)  # 1=highest, 5=lowest
    
    # Personalization factors
    based_on_performance = Column(Boolean, default=False)
    based_on_interests = Column(Boolean, default=False)
    based_on_goals = Column(Boolean, default=False)
    based_on_gaps = Column(Boolean, default=False)
    
    # User interaction
    viewed = Column(Boolean, default=False)
    viewed_at = Column(DateTime)
    accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime)
    dismissed = Column(Boolean, default=False)
    dismissed_at = Column(DateTime)
    
    # Effectiveness tracking
    followed_through = Column(Boolean, default=False)
    outcome_rating = Column(Integer)  # 1-5 if followed through
    
    # Expiration
    expires_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIModelUsage(Base):
    """Track usage of different AI models"""
    __tablename__ = "ai_model_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model identification
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    provider = Column(String(50))  # openai, anthropic, google, etc.
    
    # Usage tracking
    date = Column(DateTime, nullable=False)
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    
    # Performance metrics
    average_response_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    error_count = Column(Integer, default=0)
    
    # Cost tracking
    estimated_cost = Column(Float, default=0.0)
    cost_per_token = Column(Float, default=0.0)
    
    # Quality metrics
    average_user_rating = Column(Float, default=0.0)
    flagged_responses = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConversationExport(Base):
    """Exported conversation data"""
    __tablename__ = "conversation_exports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    
    # Export details
    export_format = Column(String(20))  # json, markdown, pdf, html
    export_filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    
    # Export options
    include_system_messages = Column(Boolean, default=False)
    include_timestamps = Column(Boolean, default=True)
    include_metadata = Column(Boolean, default=False)
    
    # Status
    export_status = Column(String(20), default="pending")  # pending, completed, failed
    download_count = Column(Integer, default=0)
    
    # Expiration
    expires_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
