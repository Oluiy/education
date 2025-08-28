"""
Smart Assistant Schemas
Pydantic models for AI assistant and learning recommendations
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

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
    AUDIO = "audio"
    FILE = "file"

class ResourceType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    QUIZ = "quiz"
    TEXT = "text"
    PRACTICE = "practice"
    INTERACTIVE = "interactive"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

# ========================================
# CHAT SCHEMAS
# ========================================

class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    message: str = Field(..., min_length=1, max_length=2000)
    message_type: MessageType = MessageType.TEXT
    chat_type: ChatType = ChatType.STUDY_HELP
    subject: Optional[str] = None
    topic: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    attachments: Optional[List[str]] = None  # File URLs

    @validator('message')
    def validate_message(cls, v):
        """Validate message content"""
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: int
    session_id: int
    user_id: int
    message: str
    message_type: str
    is_user_message: bool
    timestamp: datetime
    response_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    attachments: Optional[List[str]] = None

    class Config:
        from_attributes = True

class AssistantChatCreate(BaseModel):
    """Schema for creating a chat session"""
    title: Optional[str] = None
    description: Optional[str] = None
    chat_type: ChatType = ChatType.STUDY_HELP
    subject: Optional[str] = None
    topic: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    context_data: Optional[Dict[str, Any]] = None

class AssistantChatResponse(BaseModel):
    """Schema for chat session response"""
    id: int
    session_id: str
    user_id: int
    title: Optional[str]
    description: Optional[str]
    chat_type: str
    subject: Optional[str]
    topic: Optional[str]
    status: str
    message_count: int
    total_tokens_used: int
    started_at: datetime
    last_message_at: datetime
    ended_at: Optional[datetime]
    user_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    helpfulness_rating: Optional[int] = Field(None, ge=1, le=5)

    class Config:
        from_attributes = True

# ========================================
# RECOMMENDATION SCHEMAS
# ========================================

class RecommendationRequest(BaseModel):
    """Schema for recommendation requests"""
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    resource_type: Optional[ResourceType] = None
    learning_style: Optional[str] = None
    current_progress: Optional[Dict[str, Any]] = None
    weak_areas: Optional[List[str]] = None
    limit: int = Field(10, ge=1, le=50)
    include_completed: bool = False

class RecommendationResponse(BaseModel):
    """Schema for recommendation responses"""
    type: str  # video, quiz, content, practice
    title: str
    description: str
    url: Optional[str] = None
    subject: str
    topic: str
    difficulty: str
    estimated_time: int  # minutes
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    content_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)

class LearningResourceResponse(BaseModel):
    """Schema for learning resource responses"""
    id: int
    title: str
    description: str
    resource_type: str
    subject: str
    topic: str
    difficulty_level: str
    estimated_duration: int  # minutes
    url: Optional[str] = None
    file_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tags: List[str]
    learning_objectives: List[str]
    prerequisites: List[str]
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ========================================
# AI INTERACTION SCHEMAS
# ========================================

class ConceptExplanationRequest(BaseModel):
    """Schema for concept explanation requests"""
    concept: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=100)
    grade_level: Optional[str] = None
    learning_style: Optional[str] = None
    include_examples: bool = True
    include_practice_questions: bool = False
    difficulty_level: Optional[DifficultyLevel] = None

class ConceptExplanationResponse(BaseModel):
    """Schema for concept explanation responses"""
    concept: str
    subject: str
    explanation: str
    key_points: List[str]
    examples: List[Dict[str, Any]]
    practice_questions: Optional[List[Dict[str, Any]]] = None
    related_concepts: List[str]
    difficulty_level: str
    estimated_reading_time: int  # minutes
    confidence_score: float

class StudyPlanRequest(BaseModel):
    """Schema for study plan generation requests"""
    subjects: List[str] = Field(..., min_items=1, max_items=5)
    topics: Optional[List[str]] = None
    duration_weeks: int = Field(4, ge=1, le=52)
    study_hours_per_day: float = Field(2.0, ge=0.5, le=8.0)
    learning_style: Optional[str] = None
    current_progress: Optional[Dict[str, Any]] = None
    weak_areas: Optional[List[str]] = None
    goals: Optional[List[str]] = None

class StudyPlanResponse(BaseModel):
    """Schema for study plan responses"""
    plan_id: int
    title: str
    description: str
    duration_weeks: int
    total_hours: float
    subjects: List[str]
    topics: List[str]
    weekly_schedule: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    resources: List[LearningResourceResponse]
    progress_tracking: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

# ========================================
# PROGRESS ANALYSIS SCHEMAS
# ========================================

class ProgressAnalysisRequest(BaseModel):
    """Schema for progress analysis requests"""
    time_period: str = Field("week", regex=r"^(day|week|month|semester|year)$")
    subjects: Optional[List[str]] = None
    include_recommendations: bool = True
    include_weak_areas: bool = True
    include_strengths: bool = True

class ProgressAnalysisResponse(BaseModel):
    """Schema for progress analysis responses"""
    time_period: str
    overall_progress: float  # percentage
    subjects_progress: Dict[str, float]
    weak_areas: List[Dict[str, Any]]
    strengths: List[Dict[str, Any]]
    recommendations: List[RecommendationResponse]
    study_patterns: Dict[str, Any]
    improvement_areas: List[str]
    next_steps: List[str]
    generated_at: datetime

class WeakAreasAnalysis(BaseModel):
    """Schema for weak areas analysis"""
    subject: str
    topic: str
    performance_score: float
    difficulty_level: str
    recommended_resources: List[LearningResourceResponse]
    study_suggestions: List[str]
    practice_questions: List[Dict[str, Any]]
    estimated_improvement_time: int  # hours

# ========================================
# FEEDBACK SCHEMAS
# ========================================

class FeedbackRequest(BaseModel):
    """Schema for feedback requests"""
    message_id: int
    feedback_type: str = Field(..., regex=r"^(helpful|not_helpful|incorrect|inappropriate)$")
    feedback_text: Optional[str] = Field(None, max_length=500)
    rating: Optional[int] = Field(None, ge=1, le=5)

class FeedbackResponse(BaseModel):
    """Schema for feedback responses"""
    id: int
    message_id: int
    user_id: int
    feedback_type: str
    feedback_text: Optional[str]
    rating: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# ========================================
# YOUTUBE INTEGRATION SCHEMAS
# ========================================

class YouTubeVideoRequest(BaseModel):
    """Schema for YouTube video requests"""
    subject: str
    topic: str
    grade_level: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    max_duration: Optional[int] = Field(None, ge=1, le=120)  # minutes
    language: str = "en"
    limit: int = Field(10, ge=1, le=20)

class YouTubeVideoResponse(BaseModel):
    """Schema for YouTube video responses"""
    video_id: str
    title: str
    description: str
    channel_name: str
    duration: int  # seconds
    view_count: int
    like_count: int
    published_at: datetime
    thumbnail_url: str
    video_url: str
    educational_score: float  # 0-1
    relevance_score: float  # 0-1
    difficulty_level: str
    tags: List[str]

# ========================================
# AUDIO GENERATION SCHEMAS
# ========================================

class AudioSummaryRequest(BaseModel):
    """Schema for audio summary requests"""
    content_id: int
    content_type: str = Field(..., regex=r"^(lesson|quiz|concept|summary)$")
    voice_type: str = Field("neutral", regex=r"^(male|female|neutral)$")
    speed: float = Field(1.0, ge=0.5, le=2.0)
    include_transcript: bool = True

class AudioSummaryResponse(BaseModel):
    """Schema for audio summary responses"""
    audio_id: str
    content_id: int
    content_type: str
    audio_url: str
    duration: int  # seconds
    file_size: int  # bytes
    transcript: Optional[str] = None
    voice_type: str
    speed: float
    quality: str
    created_at: datetime

# ========================================
# QUIZ GENERATION SCHEMAS
# ========================================

class PracticeQuizRequest(BaseModel):
    """Schema for practice quiz generation requests"""
    subject: str
    topic: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    num_questions: int = Field(10, ge=5, le=50)
    question_types: List[str] = Field(default_factory=lambda: ["multiple_choice"])
    include_explanations: bool = True
    time_limit: Optional[int] = Field(None, ge=5, le=120)  # minutes

class PracticeQuizResponse(BaseModel):
    """Schema for practice quiz responses"""
    quiz_id: str
    title: str
    subject: str
    topic: str
    difficulty: str
    num_questions: int
    time_limit: Optional[int]
    questions: List[Dict[str, Any]]
    total_points: int
    passing_score: float
    created_at: datetime

# ========================================
# ANALYTICS SCHEMAS
# ========================================

class AssistantAnalytics(BaseModel):
    """Schema for assistant analytics"""
    total_interactions: int
    average_response_time: float  # seconds
    user_satisfaction_avg: float
    most_common_queries: List[Dict[str, Any]]
    popular_subjects: List[Dict[str, Any]]
    usage_patterns: Dict[str, Any]
    improvement_areas: List[str]
    generated_at: datetime

class UserInteractionStats(BaseModel):
    """Schema for user interaction statistics"""
    user_id: int
    total_chats: int
    total_messages: int
    average_session_length: float  # minutes
    preferred_subjects: List[str]
    common_queries: List[str]
    satisfaction_rating: float
    last_interaction: datetime
    created_at: datetime

    class Config:
        from_attributes = True
