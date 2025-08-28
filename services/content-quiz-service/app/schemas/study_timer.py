"""
Study Timer Schemas
Pydantic models for study session tracking and timer management
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SessionType(str, Enum):
    STUDY = "study"
    BREAK = "break"
    LONG_BREAK = "long_break"
    QUIZ = "quiz"
    READING = "reading"
    PRACTICE = "practice"

class TimerStatus(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"

# ========================================
# STUDY SESSION SCHEMAS
# ========================================

class StudySessionCreate(BaseModel):
    """Schema for creating a study session"""
    subject: Optional[str] = None
    topic: Optional[str] = None
    session_type: SessionType = SessionType.STUDY
    planned_duration: int = Field(25, ge=5, le=180)  # minutes
    goals: List[str] = Field(default_factory=list, max_items=5)
    notes: Optional[str] = None
    device_type: str = Field("web", regex=r"^(web|mobile|tablet|desktop)$")

    @validator('goals')
    def validate_goals(cls, v):
        """Validate study goals"""
        if len(v) > 5:
            raise ValueError("Maximum 5 goals allowed")
        return [goal.strip() for goal in v if goal.strip()]

class StudySessionResponse(BaseModel):
    """Schema for study session response"""
    id: int
    user_id: int
    school_id: int
    subject: Optional[str]
    topic: Optional[str]
    session_type: str
    planned_duration: int
    actual_duration: Optional[int]
    goals: List[str]
    completed_goals: List[str]
    notes: Optional[str]
    device_type: str
    start_time: datetime
    end_time: Optional[datetime]
    pause_duration: int
    status: str
    focus_rating: Optional[int] = Field(None, ge=1, le=5)
    productivity_rating: Optional[int] = Field(None, ge=1, le=5)
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudySessionUpdate(BaseModel):
    """Schema for updating study session"""
    notes: Optional[str] = None
    completed_goals: Optional[List[str]] = None
    focus_rating: Optional[int] = Field(None, ge=1, le=5)
    productivity_rating: Optional[int] = Field(None, ge=1, le=5)
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)

class StudySessionListResponse(BaseModel):
    """Schema for study session list response"""
    sessions: List[StudySessionResponse]
    total_count: int
    total_duration: int  # minutes
    average_session_length: float
    completion_rate: float

# ========================================
# STUDY TIMER SCHEMAS
# ========================================

class StudyTimerCreate(BaseModel):
    """Schema for creating a study timer"""
    timer_name: str = Field(..., min_length=1, max_length=100)
    study_duration: int = Field(25, ge=5, le=120)  # minutes
    break_duration: int = Field(5, ge=1, le=30)  # minutes
    long_break_duration: int = Field(15, ge=5, le=60)  # minutes
    sessions_before_long_break: int = Field(4, ge=1, le=10)
    auto_start_breaks: bool = True
    auto_start_sessions: bool = False
    sound_enabled: bool = True
    notifications_enabled: bool = True
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    is_default: bool = False

class StudyTimerResponse(BaseModel):
    """Schema for study timer response"""
    id: int
    user_id: int
    school_id: int
    timer_name: str
    study_duration: int
    break_duration: int
    long_break_duration: int
    sessions_before_long_break: int
    auto_start_breaks: bool
    auto_start_sessions: bool
    sound_enabled: bool
    notifications_enabled: bool
    subject_id: Optional[int]
    topic_id: Optional[int]
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudyTimerUpdate(BaseModel):
    """Schema for updating study timer"""
    timer_name: Optional[str] = Field(None, min_length=1, max_length=100)
    study_duration: Optional[int] = Field(None, ge=5, le=120)
    break_duration: Optional[int] = Field(None, ge=1, le=30)
    long_break_duration: Optional[int] = Field(None, ge=5, le=60)
    sessions_before_long_break: Optional[int] = Field(None, ge=1, le=10)
    auto_start_breaks: Optional[bool] = None
    auto_start_sessions: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    subject_id: Optional[int] = None
    topic_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

# ========================================
# STUDY STATISTICS SCHEMAS
# ========================================

class StudyStats(BaseModel):
    """Schema for study statistics"""
    total_sessions: int
    total_study_time: int  # minutes
    total_break_time: int  # minutes
    average_session_length: float  # minutes
    longest_session: int  # minutes
    shortest_session: int  # minutes
    completion_rate: float  # percentage
    focus_rating_avg: float
    productivity_rating_avg: float
    difficulty_rating_avg: float
    study_streak: int  # consecutive days
    weekly_goal_progress: float  # percentage
    monthly_goal_progress: float  # percentage
    preferred_study_times: Dict[str, int]  # time period -> count
    subject_distribution: Dict[str, int]  # subject -> minutes
    session_type_distribution: Dict[str, int]  # type -> count

class DailyStats(BaseModel):
    """Schema for daily study statistics"""
    date: datetime
    sessions_count: int
    total_study_time: int  # minutes
    total_break_time: int  # minutes
    goals_completed: int
    focus_rating_avg: float
    productivity_rating_avg: float
    difficulty_rating_avg: float
    subjects_studied: List[str]

class WeeklyStats(BaseModel):
    """Schema for weekly study statistics"""
    week_start: datetime
    week_end: datetime
    total_sessions: int
    total_study_time: int  # minutes
    average_daily_study_time: float  # minutes
    study_days: int  # days with at least one session
    completion_rate: float  # percentage
    focus_rating_avg: float
    productivity_rating_avg: float
    difficulty_rating_avg: float
    weekly_goal_achieved: bool
    daily_stats: List[DailyStats]

class MonthlyStats(BaseModel):
    """Schema for monthly study statistics"""
    month: int
    year: int
    total_sessions: int
    total_study_time: int  # minutes
    average_daily_study_time: float  # minutes
    study_days: int  # days with at least one session
    completion_rate: float  # percentage
    focus_rating_avg: float
    productivity_rating_avg: float
    difficulty_rating_avg: float
    monthly_goal_achieved: bool
    weekly_stats: List[WeeklyStats]

# ========================================
# PRODUCTIVITY SCHEMAS
# ========================================

class ProductivityScore(BaseModel):
    """Schema for productivity score calculation"""
    session_count: int
    total_time: int  # minutes
    completion_rate: float
    focus_rating_avg: float
    productivity_rating_avg: float
    consistency_score: float
    goal_achievement_rate: float
    overall_score: float  # 0-100

class ProductivityInsights(BaseModel):
    """Schema for productivity insights"""
    current_streak: int
    best_streak: int
    average_daily_study_time: float
    most_productive_time: str
    most_productive_subject: str
    improvement_areas: List[str]
    recommendations: List[str]
    weekly_trend: str  # improving, declining, stable

# ========================================
# TIMER CONTROL SCHEMAS
# ========================================

class TimerAction(BaseModel):
    """Schema for timer control actions"""
    action: str = Field(..., regex=r"^(start|pause|resume|stop|extend|skip)$")
    extend_minutes: Optional[int] = Field(None, ge=1, le=60)
    skip_to: Optional[str] = Field(None, regex=r"^(break|long_break|session)$")

    @validator('extend_minutes')
    def validate_extend(cls, v, values):
        if values.get('action') == 'extend' and v is None:
            raise ValueError('extend_minutes required for extend action')
        return v

class TimerState(BaseModel):
    """Schema for current timer state"""
    session_id: Optional[int]
    timer_id: Optional[int]
    status: TimerStatus
    current_phase: str  # study, break, long_break
    phase_start_time: datetime
    phase_duration: int  # minutes
    time_remaining: int  # seconds
    sessions_completed: int
    total_sessions: int
    is_auto_start_enabled: bool

# ========================================
# GOAL TRACKING SCHEMAS
# ========================================

class StudyGoal(BaseModel):
    """Schema for study goals"""
    goal: str = Field(..., min_length=1, max_length=200)
    target_date: Optional[datetime] = None
    priority: str = Field("medium", regex=r"^(low|medium|high)$")
    completed: bool = False
    completed_at: Optional[datetime] = None

class GoalProgress(BaseModel):
    """Schema for goal progress tracking"""
    total_goals: int
    completed_goals: int
    in_progress_goals: int
    overdue_goals: int
    completion_rate: float
    upcoming_deadlines: List[StudyGoal]
