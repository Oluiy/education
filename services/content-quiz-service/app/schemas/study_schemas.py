"""
Study Session Schemas
Pydantic schemas for study session API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class StudySessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class DeviceType(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


class BadgeType(str, Enum):
    STREAK = "streak"
    DURATION = "duration"
    CONSISTENCY = "consistency"
    FOCUS = "focus"
    MILESTONE = "milestone"


# Study Session Schemas
class StudySessionStart(BaseModel):
    """Schema for starting a study session"""
    subject_id: Optional[int] = None
    lesson_id: Optional[int] = None
    quiz_id: Optional[int] = None
    planned_duration: Optional[int] = Field(None, ge=1, le=480)  # 1 minute to 8 hours
    device_type: DeviceType = DeviceType.WEB
    is_auto_tracked: bool = False
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('planned_duration')
    def validate_duration(cls, v):
        if v is not None and (v < 1 or v > 480):
            raise ValueError('Planned duration must be between 1 and 480 minutes')
        return v


class StudySessionEnd(BaseModel):
    """Schema for ending a study session"""
    notes: Optional[str] = Field(None, max_length=1000)
    interruptions: int = Field(0, ge=0, le=100)
    status: StudySessionStatus = StudySessionStatus.COMPLETED

    @validator('interruptions')
    def validate_interruptions(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Interruptions must be between 0 and 100')
        return v


class StudySessionUpdate(BaseModel):
    """Schema for updating a study session"""
    notes: Optional[str] = Field(None, max_length=1000)
    interruptions: Optional[int] = Field(None, ge=0, le=100)
    focus_score: Optional[float] = Field(None, ge=0, le=100)


class StudySessionResponse(BaseModel):
    """Schema for study session response"""
    id: int
    student_id: int
    school_id: int
    subject_id: Optional[int]
    lesson_id: Optional[int]
    quiz_id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    planned_duration: Optional[int]
    actual_duration: Optional[int]
    status: str
    device_type: str
    is_auto_tracked: bool
    notes: Optional[str]
    focus_score: Optional[float]
    interruptions: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Study Streak Schemas
class StudyStreakResponse(BaseModel):
    """Schema for study streak response"""
    id: int
    student_id: int
    school_id: int
    current_streak: int
    longest_streak: int
    last_study_date: Optional[datetime]
    weekly_target_minutes: int
    weekly_completed_minutes: int
    week_start_date: Optional[datetime]
    total_sessions: int
    total_minutes: int
    average_session_duration: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudyStreakUpdate(BaseModel):
    """Schema for updating study streak targets"""
    weekly_target_minutes: int = Field(..., ge=60, le=10080)  # 1 hour to 1 week

    @validator('weekly_target_minutes')
    def validate_target(cls, v):
        if v < 60 or v > 10080:
            raise ValueError('Weekly target must be between 60 and 10080 minutes')
        return v


# Badge Schemas
class BadgeCreate(BaseModel):
    """Schema for creating a badge"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    badge_type: BadgeType
    requirement_value: int = Field(..., ge=1)
    requirement_type: str = Field(..., min_length=1, max_length=50)
    icon_url: Optional[str] = Field(None, max_length=255)
    color: str = Field("#FFD700", regex=r'^#[0-9A-Fa-f]{6}$')
    rarity: str = Field("common", regex=r'^(common|rare|epic|legendary)$')


class BadgeResponse(BaseModel):
    """Schema for badge response"""
    id: int
    name: str
    description: str
    badge_type: str
    requirement_value: int
    requirement_type: str
    icon_url: Optional[str]
    color: str
    rarity: str
    created_at: datetime

    class Config:
        from_attributes = True


class StudentBadgeResponse(BaseModel):
    """Schema for student badge response"""
    id: int
    student_id: int
    school_id: int
    badge_id: int
    study_session_id: Optional[int]
    earned_at: datetime
    achievement_value: int
    is_displayed: bool
    badge: BadgeResponse

    class Config:
        from_attributes = True


# Study Goal Schemas
class StudyGoalCreate(BaseModel):
    """Schema for creating a study goal"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    target_minutes: int = Field(..., ge=30, le=43200)  # 30 minutes to 30 days
    target_sessions: Optional[int] = Field(None, ge=1, le=1000)
    start_date: datetime
    end_date: datetime

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @validator('target_minutes')
    def validate_target_minutes(cls, v):
        if v < 30 or v > 43200:
            raise ValueError('Target minutes must be between 30 and 43200')
        return v


class StudyGoalUpdate(BaseModel):
    """Schema for updating a study goal"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    target_minutes: Optional[int] = Field(None, ge=30, le=43200)
    target_sessions: Optional[int] = Field(None, ge=1, le=1000)
    end_date: Optional[datetime] = None


class StudyGoalResponse(BaseModel):
    """Schema for study goal response"""
    id: int
    student_id: int
    school_id: int
    title: str
    description: Optional[str]
    target_minutes: int
    target_sessions: Optional[int]
    start_date: datetime
    end_date: datetime
    completed_minutes: int
    completed_sessions: int
    is_achieved: bool
    achieved_at: Optional[datetime]
    progress_percentage: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class StudyAnalytics(BaseModel):
    """Schema for study analytics"""
    total_sessions: int
    total_minutes: int
    average_session_duration: float
    current_streak: int
    longest_streak: int
    weekly_progress: float
    monthly_minutes: int
    focus_score_average: float
    most_studied_subject: Optional[str]
    preferred_device: str
    badges_earned: int
    goals_achieved: int
    weekly_minutes_by_day: Dict[str, int]
    subject_distribution: Dict[str, int]


class StudySessionListResponse(BaseModel):
    """Schema for paginated study session list"""
    sessions: List[StudySessionResponse]
    total: int
    page: int
    per_page: int
    pages: int


class StudyDashboard(BaseModel):
    """Schema for study dashboard data"""
    current_session: Optional[StudySessionResponse]
    streak: StudyStreakResponse
    recent_sessions: List[StudySessionResponse]
    recent_badges: List[StudentBadgeResponse]
    active_goals: List[StudyGoalResponse]
    analytics: StudyAnalytics


# Timer Control Schemas
class TimerAction(BaseModel):
    """Schema for timer control actions"""
    action: str = Field(..., regex=r'^(pause|resume|extend)$')
    extend_minutes: Optional[int] = Field(None, ge=1, le=120)

    @validator('extend_minutes')
    def validate_extend(cls, v, values):
        if values.get('action') == 'extend' and v is None:
            raise ValueError('extend_minutes required for extend action')
        return v
