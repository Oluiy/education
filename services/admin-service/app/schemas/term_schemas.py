"""
Term Setup Wizard Schemas
Pydantic models for term configuration API
"""

from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time
from enum import Enum


# Enums
class TermStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class WizardStep(str, Enum):
    BASIC_INFO = "basic_info"
    SCHEDULE = "schedule"
    SUBJECTS = "subjects"
    ASSESSMENT = "assessment"
    GRADING = "grading"
    HOLIDAYS = "holidays"
    REVIEW = "review"
    COMPLETE = "complete"


class AssessmentType(str, Enum):
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    EXAM = "exam"
    PROJECT = "project"
    PARTICIPATION = "participation"


class GradeScale(str, Enum):
    PERCENTAGE = "percentage"
    LETTER = "letter"
    POINTS = "points"
    PASS_FAIL = "pass_fail"


class DayOfWeek(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


# Base schemas
class TermBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    academic_year: str = Field(..., min_length=4, max_length=20)
    start_date: date
    end_date: date
    description: Optional[str] = Field(None, max_length=1000)
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class TermCreate(TermBase):
    school_id: int
    created_by: int


class TermUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[TermStatus] = None


class TermResponse(TermBase):
    term_id: int
    school_id: int
    status: TermStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Class Schedule schemas
class ClassScheduleBase(BaseModel):
    class_name: str = Field(..., min_length=1, max_length=100)
    subject_name: str = Field(..., min_length=1, max_length=100)
    teacher_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    room: Optional[str] = Field(None, max_length=50)
    
    @validator('end_time')
    def validate_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v


class ClassScheduleCreate(ClassScheduleBase):
    term_id: int


class ClassScheduleUpdate(BaseModel):
    class_name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject_name: Optional[str] = Field(None, min_length=1, max_length=100)
    teacher_id: Optional[int] = None
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    room: Optional[str] = Field(None, max_length=50)


class ClassScheduleResponse(ClassScheduleBase):
    schedule_id: int
    term_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Assessment Configuration schemas
class AssessmentConfigBase(BaseModel):
    assessment_type: AssessmentType
    name: str = Field(..., min_length=1, max_length=200)
    weight_percentage: float = Field(..., ge=0, le=100)
    description: Optional[str] = Field(None, max_length=500)
    is_required: bool = True


class AssessmentConfigCreate(AssessmentConfigBase):
    term_id: int


class AssessmentConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    weight_percentage: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = Field(None, max_length=500)
    is_required: Optional[bool] = None


class AssessmentConfigResponse(AssessmentConfigBase):
    config_id: int
    term_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Grading Configuration schemas
class GradingConfigBase(BaseModel):
    grade_scale: GradeScale
    min_score: float = Field(..., ge=0)
    max_score: float = Field(..., gt=0)
    passing_score: float = Field(..., ge=0)
    grade_boundaries: Dict[str, float] = Field(default_factory=dict)
    
    @validator('passing_score')
    def validate_passing_score(cls, v, values):
        if 'min_score' in values and 'max_score' in values:
            if not (values['min_score'] <= v <= values['max_score']):
                raise ValueError('Passing score must be between min and max score')
        return v
    
    @validator('max_score')
    def validate_max_score(cls, v, values):
        if 'min_score' in values and v <= values['min_score']:
            raise ValueError('Max score must be greater than min score')
        return v


class GradingConfigCreate(GradingConfigBase):
    term_id: int


class GradingConfigUpdate(BaseModel):
    grade_scale: Optional[GradeScale] = None
    min_score: Optional[float] = Field(None, ge=0)
    max_score: Optional[float] = Field(None, gt=0)
    passing_score: Optional[float] = Field(None, ge=0)
    grade_boundaries: Optional[Dict[str, float]] = None


class GradingConfigResponse(GradingConfigBase):
    config_id: int
    term_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Holiday schemas
class HolidayBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    start_date: date
    end_date: date
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date cannot be before start date')
        return v


class HolidayCreate(HolidayBase):
    term_id: int


class HolidayUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)


class HolidayResponse(HolidayBase):
    holiday_id: int
    term_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Wizard Session schemas
class WizardSessionBase(BaseModel):
    current_step: WizardStep
    completed_steps: List[WizardStep] = Field(default_factory=list)
    step_data: Dict[str, Any] = Field(default_factory=dict)


class WizardSessionCreate(WizardSessionBase):
    term_id: int
    user_id: int


class WizardSessionUpdate(BaseModel):
    current_step: Optional[WizardStep] = None
    completed_steps: Optional[List[WizardStep]] = None
    step_data: Optional[Dict[str, Any]] = None


class WizardSessionResponse(WizardSessionBase):
    session_id: int
    term_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Term Template schemas
class TermTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    template_data: Dict[str, Any] = Field(default_factory=dict)
    is_public: bool = False


class TermTemplateCreate(TermTemplateBase):
    school_id: int
    created_by: int


class TermTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    template_data: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class TermTemplateResponse(TermTemplateBase):
    template_id: int
    school_id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Calendar Event schemas
class CalendarEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str] = Field(None, max_length=200)
    is_all_day: bool = False
    
    @validator('end_datetime')
    def validate_datetime(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('End datetime must be after start datetime')
        return v


class CalendarEventCreate(CalendarEventBase):
    term_id: int
    created_by: int


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    is_all_day: Optional[bool] = None


class CalendarEventResponse(CalendarEventBase):
    event_id: int
    term_id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Wizard-specific schemas
class WizardStepRequest(BaseModel):
    step: WizardStep
    data: Dict[str, Any]


class WizardStepResponse(BaseModel):
    step: WizardStep
    completed: bool
    next_step: Optional[WizardStep] = None
    validation_errors: List[str] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory=dict)


class TermSummary(BaseModel):
    term: TermResponse
    schedules_count: int
    assessments_count: int
    holidays_count: int
    events_count: int
    completion_percentage: float


class WizardProgressResponse(BaseModel):
    session: WizardSessionResponse
    progress_percentage: float
    next_step: Optional[WizardStep] = None
    available_steps: List[WizardStep]
    term_summary: Optional[TermSummary] = None


# Bulk operation schemas
class BulkScheduleCreate(BaseModel):
    schedules: List[ClassScheduleCreate]


class BulkAssessmentCreate(BaseModel):
    assessments: List[AssessmentConfigCreate]


class BulkHolidayCreate(BaseModel):
    holidays: List[HolidayCreate]


class BulkOperationResponse(BaseModel):
    successful: int
    failed: int
    errors: List[str] = Field(default_factory=list)
    created_ids: List[int] = Field(default_factory=list)
