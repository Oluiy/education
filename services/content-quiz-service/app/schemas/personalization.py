"""
Personalization Quiz Schemas
Pydantic models for personalization quiz and student preferences
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class StudyTimePreference(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"

class ResourceType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    AUDIO = "audio"
    INTERACTIVE = "interactive"
    PRACTICE = "practice"

# ========================================
# PERSONALIZATION QUIZ SCHEMAS
# ========================================

class PersonalizationQuizCreate(BaseModel):
    """Schema for creating a personalization quiz"""
    learning_style: LearningStyle
    preferred_subjects: List[str] = Field(..., min_items=1, max_items=10)
    difficulty_preference: DifficultyLevel
    study_time_preference: StudyTimePreference
    resource_preferences: Dict[str, bool] = Field(..., description="Resource type preferences")
    study_goals: List[str] = Field(default_factory=list, max_items=5)
    target_score: Optional[float] = Field(None, ge=0, le=100)
    study_hours_per_day: Optional[float] = Field(2.0, ge=0.5, le=12.0)
    preferred_session_duration: Optional[int] = Field(25, ge=10, le=120)

    @validator('resource_preferences')
    def validate_resource_preferences(cls, v):
        """Validate resource preferences"""
        valid_resources = ['video', 'text', 'audio', 'interactive', 'practice']
        for key in v.keys():
            if key not in valid_resources:
                raise ValueError(f"Invalid resource type: {key}")
        return v

    @validator('preferred_subjects')
    def validate_subjects(cls, v):
        """Validate subject names"""
        if not all(subject.strip() for subject in v):
            raise ValueError("Subject names cannot be empty")
        return [subject.strip().title() for subject in v]

class PersonalizationQuizResponse(BaseModel):
    """Schema for personalization quiz response"""
    id: int
    user_id: int
    school_id: int
    learning_style: str
    preferred_subjects: List[str]
    difficulty_preference: str
    study_time_preference: str
    resource_preferences: Dict[str, bool]
    study_goals: List[str]
    target_score: Optional[float]
    study_hours_per_day: float
    preferred_session_duration: int
    learning_style_analysis: Optional[Dict[str, Any]]
    strength_areas: Optional[List[str]]
    weak_areas: Optional[List[str]]
    recommendations: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PersonalizationQuizUpdate(BaseModel):
    """Schema for updating personalization quiz"""
    learning_style: Optional[LearningStyle] = None
    preferred_subjects: Optional[List[str]] = None
    difficulty_preference: Optional[DifficultyLevel] = None
    study_time_preference: Optional[StudyTimePreference] = None
    resource_preferences: Optional[Dict[str, bool]] = None
    study_goals: Optional[List[str]] = None
    target_score: Optional[float] = Field(None, ge=0, le=100)
    study_hours_per_day: Optional[float] = Field(None, ge=0.5, le=12.0)
    preferred_session_duration: Optional[int] = Field(None, ge=10, le=120)

# ========================================
# STUDENT PREFERENCES SCHEMAS
# ========================================

class StudentPreferencesCreate(BaseModel):
    """Schema for creating student preferences"""
    preferred_learning_methods: List[str] = Field(default_factory=list)
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    study_pace: str = Field("normal", regex=r"^(slow|normal|fast)$")
    preferred_content_types: List[ResourceType] = Field(default_factory=list)
    auto_play_videos: bool = True
    show_transcripts: bool = True
    enable_audio_summaries: bool = True
    preferred_study_times: List[str] = Field(default_factory=list)
    session_duration: int = Field(25, ge=10, le=120)
    break_duration: int = Field(5, ge=1, le=30)
    daily_study_goal: int = Field(120, ge=30, le=480)
    text_to_speech_enabled: bool = False
    large_text_mode: bool = False
    high_contrast_mode: bool = False
    dyslexia_friendly_font: bool = False
    study_reminders: bool = True
    achievement_notifications: bool = True
    progress_updates: bool = True
    quiet_hours_start: str = Field("22:00", regex=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: str = Field("08:00", regex=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    preferred_language: str = Field("en", min_length=2, max_length=5)
    timezone: str = Field("UTC", min_length=3, max_length=50)

    @validator('preferred_study_times')
    def validate_study_times(cls, v):
        """Validate study time preferences"""
        valid_times = ['morning', 'afternoon', 'evening', 'night']
        for time in v:
            if time not in valid_times:
                raise ValueError(f"Invalid study time: {time}")
        return v

class StudentPreferencesResponse(BaseModel):
    """Schema for student preferences response"""
    id: int
    user_id: int
    school_id: int
    preferred_learning_methods: List[str]
    difficulty_level: str
    study_pace: str
    preferred_content_types: List[str]
    auto_play_videos: bool
    show_transcripts: bool
    enable_audio_summaries: bool
    preferred_study_times: List[str]
    session_duration: int
    break_duration: int
    daily_study_goal: int
    text_to_speech_enabled: bool
    large_text_mode: bool
    high_contrast_mode: bool
    dyslexia_friendly_font: bool
    study_reminders: bool
    achievement_notifications: bool
    progress_updates: bool
    quiet_hours_start: str
    quiet_hours_end: str
    preferred_language: str
    timezone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentPreferencesUpdate(BaseModel):
    """Schema for updating student preferences"""
    preferred_learning_methods: Optional[List[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    study_pace: Optional[str] = Field(None, regex=r"^(slow|normal|fast)$")
    preferred_content_types: Optional[List[ResourceType]] = None
    auto_play_videos: Optional[bool] = None
    show_transcripts: Optional[bool] = None
    enable_audio_summaries: Optional[bool] = None
    preferred_study_times: Optional[List[str]] = None
    session_duration: Optional[int] = Field(None, ge=10, le=120)
    break_duration: Optional[int] = Field(None, ge=1, le=30)
    daily_study_goal: Optional[int] = Field(None, ge=30, le=480)
    text_to_speech_enabled: Optional[bool] = None
    large_text_mode: Optional[bool] = None
    high_contrast_mode: Optional[bool] = None
    dyslexia_friendly_font: Optional[bool] = None
    study_reminders: Optional[bool] = None
    achievement_notifications: Optional[bool] = None
    progress_updates: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(None, regex=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, regex=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    preferred_language: Optional[str] = Field(None, min_length=2, max_length=5)
    timezone: Optional[str] = Field(None, min_length=3, max_length=50)

# ========================================
# RECOMMENDATION SCHEMAS
# ========================================

class LearningRecommendation(BaseModel):
    """Schema for learning recommendations"""
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

class RecommendationRequest(BaseModel):
    """Schema for recommendation requests"""
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    resource_type: Optional[ResourceType] = None
    limit: int = Field(10, ge=1, le=50)
    include_completed: bool = False

class RecommendationResponse(BaseModel):
    """Schema for recommendation responses"""
    recommendations: List[LearningRecommendation]
    total_count: int
    subject: Optional[str] = None
    topic: Optional[str] = None
    generated_at: datetime

# ========================================
# ANALYSIS SCHEMAS
# ========================================

class LearningStyleAnalysis(BaseModel):
    """Schema for learning style analysis"""
    primary_style: LearningStyle
    secondary_style: Optional[LearningStyle] = None
    style_percentages: Dict[str, float]
    recommendations: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]

class WeakAreasAnalysis(BaseModel):
    """Schema for weak areas analysis"""
    subject: str
    topic: str
    performance_score: float
    difficulty_level: str
    recommended_resources: List[LearningRecommendation]
    study_suggestions: List[str]

class PersonalizationSummary(BaseModel):
    """Schema for personalization summary"""
    quiz_completed: bool
    learning_style: Optional[str] = None
    preferred_subjects: List[str] = Field(default_factory=list)
    difficulty_preference: Optional[str] = None
    study_time_preference: Optional[str] = None
    resource_preferences: Dict[str, bool] = Field(default_factory=dict)
    recommendations_count: int = 0
    last_updated: Optional[datetime] = None
