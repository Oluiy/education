"""
EduNerve Assistant Service - Pydantic Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ResourceType(str, Enum):
    """Resource types"""
    VIDEO = "video"
    AUDIO = "audio"
    QUIZ = "quiz"
    TEXT = "text"
    PRACTICE = "practice"


class ActivityType(str, Enum):
    """Learning activity types"""
    STUDY = "study"
    QUIZ = "quiz"
    VIDEO_WATCH = "video_watch"
    AUDIO_LISTEN = "audio_listen"
    PRACTICE = "practice"


class LearningStyle(str, Enum):
    """Learning styles"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    MIXED = "mixed"


# Resource Generation Schemas
class ResourceGenerationRequest(BaseModel):
    """Request for generating learning resources"""
    content_id: Optional[int] = None
    content_text: Optional[str] = None
    subject: str
    class_level: str
    topic: Optional[str] = None
    resource_types: Optional[List[ResourceType]] = None
    
    @validator('content_text')
    def validate_content(cls, v, values):
        """Ensure either content_id or content_text is provided"""
        if not v and not values.get('content_id'):
            raise ValueError('Either content_id or content_text must be provided')
        return v


class StudyResourceCreate(BaseModel):
    """Schema for creating study resources"""
    resource_type: str = Field(..., description="Type of resource (video, audio, quiz, text, practice)")
    resource_title: str = Field(..., description="Title of the resource")
    resource_description: Optional[str] = Field(None, description="Description of the resource")
    resource_url: str = Field(..., description="URL or path to the resource")
    subject: str = Field(..., description="Subject area")
    class_level: str = Field(..., description="Class level (e.g., SS1, SS2, SS3)")
    topic: Optional[str] = Field(None, description="Specific topic")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Related keywords")
    difficulty_level: Optional[str] = Field("medium", description="Difficulty level")
    estimated_duration_minutes: Optional[int] = Field(None, description="Estimated duration in minutes")
    source_type: str = Field("manual", description="How the resource was created")


class StudyResourceResponse(BaseModel):
    """Study resource response"""
    id: int
    resource_type: str
    resource_title: str
    resource_description: Optional[str] = None
    resource_url: str
    subject: str
    class_level: str
    topic: Optional[str] = None
    keywords: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    source_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssistantPlanResponse(BaseModel):
    """Assistant plan response"""
    id: int
    student_id: int
    subject: str
    class_level: str
    topic: Optional[str] = None
    plan_content: str
    plan_type: str
    content_id: Optional[int] = None
    status: str
    created_at: datetime
    resources: List[StudyResourceResponse] = []
    
    class Config:
        from_attributes = True


# Study Plan Schemas
class StudyPlanRequest(BaseModel):
    """Request for creating a study plan"""
    subject: str
    class_level: str
    topics: List[str]
    duration_weeks: int = Field(default=4, ge=1, le=52)
    study_hours_per_day: float = Field(default=2.0, ge=0.5, le=8.0)
    weak_areas: Optional[List[str]] = None
    learning_style: Optional[LearningStyle] = None
    
    @validator('class_level')
    def validate_class_level(cls, v):
        """Validate class level"""
        allowed_levels = ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3']
        if v not in allowed_levels:
            raise ValueError(f'Class level must be one of {allowed_levels}')
        return v


class StudyPlanCreate(BaseModel):
    """Schema for creating a study plan"""
    subject: str
    class_level: str
    topics: List[str]
    duration_weeks: int = Field(default=4, ge=1, le=52)
    study_hours_per_day: float = Field(default=2.0, ge=0.5, le=8.0)
    weak_areas: Optional[List[str]] = None
    learning_style: Optional[LearningStyle] = None
    user_id: Optional[int] = None
    
    @validator('class_level')
    def validate_class_level(cls, v):
        """Validate class level"""
        allowed_levels = ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3']
        if v not in allowed_levels:
            raise ValueError(f'Class level must be one of {allowed_levels}')
        return v


class StudyPlanResponse(BaseModel):
    """Study plan response"""
    plan_id: int
    plan_content: str
    subject: str
    class_level: str
    topics: List[str]
    duration_weeks: int
    created_at: datetime


# Learning Activity Schemas
class LearningActivityCreate(BaseModel):
    """Create learning activity"""
    activity_type: ActivityType
    activity_data: Optional[Dict[str, Any]] = None
    subject: str
    class_level: str
    topic: Optional[str] = None
    duration_minutes: Optional[int] = None
    score: Optional[float] = None


class LearningActivityResponse(BaseModel):
    """Learning activity response"""
    id: int
    student_id: int
    activity_type: str
    activity_data: Optional[Dict[str, Any]] = None
    subject: str
    class_level: str
    topic: Optional[str] = None
    duration_minutes: Optional[int] = None
    score: Optional[float] = None
    completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Student Preference Schemas
class StudentPreferenceUpdate(BaseModel):
    """Update student preferences"""
    preferred_subjects: Optional[List[str]] = None
    learning_style: Optional[LearningStyle] = None
    difficulty_preference: Optional[str] = None
    preferred_resource_types: Optional[List[ResourceType]] = None
    study_time_preference: Optional[str] = None
    session_duration_preference: Optional[int] = None
    text_to_speech_enabled: Optional[bool] = None
    large_text_mode: Optional[bool] = None
    high_contrast_mode: Optional[bool] = None


class StudentPreferenceResponse(BaseModel):
    """Student preference response"""
    id: int
    student_id: int
    preferred_subjects: Optional[List[str]] = None
    learning_style: Optional[str] = None
    difficulty_preference: Optional[str] = None
    preferred_resource_types: Optional[List[str]] = None
    study_time_preference: Optional[str] = None
    session_duration_preference: Optional[int] = None
    text_to_speech_enabled: bool
    large_text_mode: bool
    high_contrast_mode: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# AI Interaction Schemas
class AIInteractionRequest(BaseModel):
    """AI interaction request"""
    interaction_type: str
    request_data: Dict[str, Any]
    subject: Optional[str] = None
    class_level: Optional[str] = None
    topic: Optional[str] = None


class AIInteractionResponse(BaseModel):
    """AI interaction response"""
    id: int
    interaction_type: str
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    subject: Optional[str] = None
    class_level: Optional[str] = None
    topic: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# YouTube Resource Schemas
class YouTubeVideoResult(BaseModel):
    """YouTube video search result"""
    video_id: str
    title: str
    description: str
    thumbnail_url: str
    channel_title: str
    duration: Optional[str] = None
    view_count: Optional[int] = None
    published_at: Optional[datetime] = None


class YouTubeSearchRequest(BaseModel):
    """YouTube search request"""
    query: str
    max_results: int = Field(default=5, ge=1, le=50)
    subject: Optional[str] = None
    class_level: Optional[str] = None


# Audio Generation Schemas
class AudioGenerationRequest(BaseModel):
    """Audio generation request"""
    text: str = Field(..., max_length=10000)
    voice_name: Optional[str] = None
    language_code: Optional[str] = None
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0)


class AudioGenerationResponse(BaseModel):
    """Audio generation response"""
    audio_url: str
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None
    voice_name: str
    language_code: str


# Analytics Schemas
class StudentAnalytics(BaseModel):
    """Student learning analytics"""
    student_id: int
    total_study_time_minutes: int
    total_activities: int
    completed_activities: int
    average_score: Optional[float] = None
    favorite_subjects: List[str]
    preferred_resource_types: List[str]
    learning_streak_days: int
    last_activity_date: Optional[datetime] = None


class ResourceAnalytics(BaseModel):
    """Resource usage analytics"""
    resource_id: int
    resource_title: str
    resource_type: str
    total_users: int
    total_access_count: int
    average_completion_rate: float
    average_time_spent_minutes: float
    user_ratings: List[int]
    average_rating: float


# Common Response Schemas
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    success: bool = False


class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


# Bulk Operations
class BulkResourceRequest(BaseModel):
    """Bulk resource generation request"""
    requests: List[ResourceGenerationRequest]


class BulkResourceResponse(BaseModel):
    """Bulk resource generation response"""
    total_requested: int
    successful: int
    failed: int
    results: List[AssistantPlanResponse]
    errors: List[Dict[str, Any]]


class StudyResourceRequest(BaseModel):
    """Request for study resource generation"""
    resource_type: ResourceType
    subject: str
    class_level: str
    topic: str
    difficulty_level: Optional[str] = "medium"
    user_id: Optional[int] = None
    
    @validator('class_level')
    def validate_class_level(cls, v):
        """Validate class level"""
        allowed_levels = ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3']
        if v not in allowed_levels:
            raise ValueError(f'Class level must be one of {allowed_levels}')
        return v
    
    @validator('difficulty_level')
    def validate_difficulty(cls, v):
        """Validate difficulty level"""
        allowed_levels = ['easy', 'medium', 'hard']
        if v not in allowed_levels:
            raise ValueError(f'Difficulty level must be one of {allowed_levels}')
        return v

class StudentActivityCreate(BaseModel):
    """Schema for creating student activity"""
    activity_type: ActivityType
    subject: str
    topic: str
    duration_minutes: int = Field(ge=1, le=480)
    score: Optional[float] = Field(None, ge=0, le=100)
    difficulty_level: Optional[str] = "medium"
    user_id: Optional[int] = None
    completed: bool = False
    
    @validator('difficulty_level')
    def validate_difficulty(cls, v):
        """Validate difficulty level"""
        allowed_levels = ['easy', 'medium', 'hard']
        if v not in allowed_levels:
            raise ValueError(f'Difficulty level must be one of {allowed_levels}')
        return v

class LearningAnalyticsResponse(BaseModel):
    """Response for learning analytics"""
    user_id: int
    total_study_time: int
    subjects_studied: List[str]
    topics_mastered: List[str]
    average_score: float
    improvement_areas: List[str]
    study_streak: int
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True
