"""
Content Management Schemas
Pydantic models for content and quiz system validation and serialization
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum


# Enums for content types
class LessonTypeEnum(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    PDF = "pdf"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"


class QuizTypeEnum(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    MATCHING = "matching"
    ORDERING = "ordering"


class DifficultyLevelEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class GradeLevelEnum(str, Enum):
    JSS1 = "JSS1"
    JSS2 = "JSS2"
    JSS3 = "JSS3"
    SS1 = "SS1"
    SS2 = "SS2"
    SS3 = "SS3"


# Base schemas
class BaseContentSchema(BaseModel):
    """Base schema for all content"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


# Subject schemas
class SubjectBase(BaseModel):
    """Base subject schema"""
    name: str = Field(..., min_length=3, max_length=200, description="Subject name")
    code: str = Field(..., min_length=2, max_length=10, description="Subject code")
    description: Optional[str] = Field(None, max_length=1000, description="Subject description")
    grade_level: Optional[GradeLevelEnum] = Field(None, description="Target grade level")
    color_theme: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")
    icon: Optional[str] = Field(None, max_length=100, description="Icon identifier")
    
    @validator('code')
    def validate_code(cls, v):
        return v.upper().strip()
    
    @validator('name')
    def validate_name(cls, v):
        return v.strip()


class SubjectCreate(SubjectBase):
    """Schema for creating a subject"""
    pass


class SubjectUpdate(BaseModel):
    """Schema for updating a subject"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    code: Optional[str] = Field(None, min_length=2, max_length=10)
    description: Optional[str] = Field(None, max_length=1000)
    grade_level: Optional[GradeLevelEnum] = None
    color_theme: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    
    @validator('code')
    def validate_code(cls, v):
        return v.upper().strip() if v else v
    
    @validator('name')
    def validate_name(cls, v):
        return v.strip() if v else v


class SubjectResponse(SubjectBase, BaseContentSchema):
    """Schema for subject response"""
    id: int
    is_active: bool
    course_count: Optional[int] = 0


class SubjectDetailResponse(SubjectResponse):
    """Detailed subject response with optional courses"""
    courses: Optional[List[Dict[str, Any]]] = None


class SubjectListResponse(BaseModel):
    """Schema for paginated subject list"""
    subjects: List[SubjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Course schemas
class CourseBase(BaseModel):
    """Base course schema"""
    name: str = Field(..., min_length=3, max_length=200, description="Course name")
    description: Optional[str] = Field(None, min_length=10, max_length=1000, description="Course description")
    level: Optional[DifficultyLevelEnum] = Field(None, description="Course difficulty level")
    order_index: Optional[int] = Field(None, ge=0, description="Display order")
    estimated_duration: Optional[int] = Field(None, gt=0, le=10080, description="Duration in minutes")
    prerequisite_courses: Optional[List[int]] = Field(default_factory=list, description="Prerequisite course IDs")
    learning_objectives: Optional[List[str]] = Field(default_factory=list, description="Learning objectives")
    
    @validator('name')
    def validate_name(cls, v):
        return v.strip()
    
    @validator('learning_objectives')
    def validate_objectives(cls, v):
        if v:
            return [obj.strip() for obj in v if obj and obj.strip()]
        return []


class CourseCreate(CourseBase):
    """Schema for creating a course"""
    subject_id: int = Field(..., gt=0, description="Subject ID")


class CourseUpdate(BaseModel):
    """Schema for updating a course"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    level: Optional[DifficultyLevelEnum] = None
    order_index: Optional[int] = Field(None, ge=0)
    estimated_duration: Optional[int] = Field(None, gt=0, le=10080)
    prerequisite_courses: Optional[List[int]] = None
    learning_objectives: Optional[List[str]] = None
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        return v.strip() if v else v
    
    @validator('learning_objectives')
    def validate_objectives(cls, v):
        if v:
            return [obj.strip() for obj in v if obj and obj.strip()]
        return v


class CourseResponse(CourseBase, BaseContentSchema):
    """Schema for course response"""
    id: int
    subject_id: int
    thumbnail_url: Optional[str] = None
    is_active: bool
    lesson_count: Optional[int] = 0
    quiz_count: Optional[int] = 0


class CourseDetailResponse(CourseResponse):
    """Detailed course response with optional content"""
    subject_name: str
    lessons: Optional[List[Dict[str, Any]]] = None
    quizzes: Optional[List[Dict[str, Any]]] = None


class CourseListResponse(BaseModel):
    """Schema for paginated course list"""
    courses: List[Dict[str, Any]]  # Using Dict to include subject_name
    total: int
    page: int
    page_size: int
    total_pages: int


# Lesson schemas
class LessonBase(BaseModel):
    """Base lesson schema"""
    title: str = Field(..., min_length=3, max_length=200, description="Lesson title")
    description: Optional[str] = Field(None, max_length=1000, description="Lesson description")
    lesson_type: LessonTypeEnum = Field(..., description="Type of lesson")
    content: Optional[str] = Field(None, min_length=50, max_length=50000, description="Lesson content")
    order_index: Optional[int] = Field(None, ge=0, description="Display order")
    estimated_duration: Optional[int] = Field(None, gt=0, le=480, description="Duration in minutes")
    difficulty_level: Optional[DifficultyLevelEnum] = Field(None, description="Difficulty level")
    prerequisites: Optional[List[int]] = Field(default_factory=list, description="Prerequisite lesson IDs")
    learning_outcomes: Optional[List[str]] = Field(default_factory=list, description="Learning outcomes")
    
    @validator('title')
    def validate_title(cls, v):
        return v.strip()
    
    @validator('learning_outcomes')
    def validate_outcomes(cls, v):
        if v:
            return [outcome.strip() for outcome in v if outcome and outcome.strip()]
        return []


class LessonCreate(LessonBase):
    """Schema for creating a lesson"""
    course_id: int = Field(..., gt=0, description="Course ID")


class LessonUpdate(BaseModel):
    """Schema for updating a lesson"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    lesson_type: Optional[LessonTypeEnum] = None
    content: Optional[str] = Field(None, min_length=50, max_length=50000)
    order_index: Optional[int] = Field(None, ge=0)
    estimated_duration: Optional[int] = Field(None, gt=0, le=480)
    difficulty_level: Optional[DifficultyLevelEnum] = None
    prerequisites: Optional[List[int]] = None
    learning_outcomes: Optional[List[str]] = None
    is_active: Optional[bool] = None
    
    @validator('title')
    def validate_title(cls, v):
        return v.strip() if v else v


class LessonResponse(LessonBase, BaseContentSchema):
    """Schema for lesson response"""
    id: int
    course_id: int
    video_url: Optional[str] = None
    file_urls: Optional[List[str]] = Field(default_factory=list)
    is_active: bool


class LessonSummaryResponse(BaseModel):
    """Summary lesson response for course details"""
    id: int
    title: str
    description: Optional[str]
    order_index: Optional[int]
    lesson_type: LessonTypeEnum
    estimated_duration: Optional[int]
    difficulty_level: Optional[DifficultyLevelEnum]
    is_active: bool


class LessonDetailResponse(LessonResponse):
    """Detailed lesson response"""
    course_name: str
    subject_name: str
    next_lesson_id: Optional[int] = None
    previous_lesson_id: Optional[int] = None


class LessonListResponse(BaseModel):
    """Schema for paginated lesson list"""
    lessons: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


# Quiz schemas
class QuizBase(BaseModel):
    """Base quiz schema"""
    title: str = Field(..., min_length=3, max_length=200, description="Quiz title")
    description: Optional[str] = Field(None, max_length=1000, description="Quiz description")
    quiz_type: QuizTypeEnum = Field(..., description="Type of quiz")
    time_limit: Optional[int] = Field(None, gt=0, le=480, description="Time limit in minutes")
    passing_score: Optional[float] = Field(None, ge=0, le=100, description="Passing score percentage")
    total_questions: Optional[int] = Field(None, gt=0, le=200, description="Total number of questions")
    order_index: Optional[int] = Field(None, ge=0, description="Display order")
    instructions: Optional[str] = Field(None, max_length=2000, description="Quiz instructions")
    randomize_questions: Optional[bool] = Field(default=False, description="Randomize question order")
    show_results_immediately: Optional[bool] = Field(default=True, description="Show results after submission")
    
    @validator('title')
    def validate_title(cls, v):
        return v.strip()


class QuizCreate(QuizBase):
    """Schema for creating a quiz"""
    course_id: int = Field(..., gt=0, description="Course ID")
    lesson_id: Optional[int] = Field(None, gt=0, description="Associated lesson ID")


class QuizUpdate(BaseModel):
    """Schema for updating a quiz"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    quiz_type: Optional[QuizTypeEnum] = None
    time_limit: Optional[int] = Field(None, gt=0, le=480)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    total_questions: Optional[int] = Field(None, gt=0, le=200)
    order_index: Optional[int] = Field(None, ge=0)
    instructions: Optional[str] = Field(None, max_length=2000)
    randomize_questions: Optional[bool] = None
    show_results_immediately: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @validator('title')
    def validate_title(cls, v):
        return v.strip() if v else v


class QuizResponse(QuizBase, BaseContentSchema):
    """Schema for quiz response"""
    id: int
    course_id: int
    lesson_id: Optional[int]
    question_count: Optional[int] = 0
    is_active: bool


class QuizSummaryResponse(BaseModel):
    """Summary quiz response for course details"""
    id: int
    title: str
    description: Optional[str]
    quiz_type: QuizTypeEnum
    time_limit: Optional[int]
    total_questions: Optional[int]
    passing_score: Optional[float]
    is_active: bool


class QuizDetailResponse(QuizResponse):
    """Detailed quiz response"""
    course_name: str
    subject_name: str
    questions: Optional[List[Dict[str, Any]]] = None


class QuizListResponse(BaseModel):
    """Schema for paginated quiz list"""
    quizzes: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


# Question schemas
class QuestionBase(BaseModel):
    """Base question schema"""
    question_text: str = Field(..., min_length=10, max_length=2000, description="Question text")
    question_type: str = Field(..., description="Type of question")
    points: Optional[float] = Field(default=1.0, gt=0, description="Points for correct answer")
    order_index: Optional[int] = Field(None, ge=0, description="Question order")
    explanation: Optional[str] = Field(None, max_length=1000, description="Answer explanation")
    difficulty_level: Optional[DifficultyLevelEnum] = None
    
    @validator('question_text')
    def validate_question_text(cls, v):
        return v.strip()


class MultipleChoiceQuestion(QuestionBase):
    """Multiple choice question schema"""
    options: List[str] = Field(..., min_items=2, max_items=10, description="Answer options")
    correct_answer: int = Field(..., ge=0, description="Index of correct answer")
    
    @validator('options')
    def validate_options(cls, v):
        return [opt.strip() for opt in v if opt and opt.strip()]
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v, values):
        if 'options' in values and v >= len(values['options']):
            raise ValueError('Correct answer index out of range')
        return v


class TrueFalseQuestion(QuestionBase):
    """True/false question schema"""
    correct_answer: bool = Field(..., description="Correct answer")


class ShortAnswerQuestion(QuestionBase):
    """Short answer question schema"""
    correct_answers: List[str] = Field(..., min_items=1, description="Acceptable answers")
    case_sensitive: Optional[bool] = Field(default=False, description="Case sensitive matching")
    
    @validator('correct_answers')
    def validate_answers(cls, v):
        return [ans.strip() for ans in v if ans and ans.strip()]


class EssayQuestion(QuestionBase):
    """Essay question schema"""
    min_words: Optional[int] = Field(None, gt=0, description="Minimum word count")
    max_words: Optional[int] = Field(None, gt=0, description="Maximum word count")
    
    @root_validator
    def validate_word_counts(cls, values):
        min_words = values.get('min_words')
        max_words = values.get('max_words')
        if min_words and max_words and min_words > max_words:
            raise ValueError('Minimum words cannot be greater than maximum words')
        return values


# Progress and submission schemas
class ProgressBase(BaseModel):
    """Base progress schema"""
    user_id: int
    completion_percentage: float = Field(..., ge=0, le=100)
    time_spent: int = Field(default=0, ge=0, description="Time spent in minutes")
    last_accessed: Optional[datetime] = None


class CourseProgressResponse(ProgressBase, BaseContentSchema):
    """Course progress response"""
    course_id: int
    lessons_completed: int = 0
    quizzes_completed: int = 0
    total_lessons: int = 0
    total_quizzes: int = 0
    current_lesson_id: Optional[int] = None


class LessonProgressResponse(ProgressBase, BaseContentSchema):
    """Lesson progress response"""
    lesson_id: int
    is_completed: bool = False


class QuizSubmissionBase(BaseModel):
    """Base quiz submission schema"""
    quiz_id: int
    answers: Dict[str, Any] = Field(..., description="User answers")
    time_taken: Optional[int] = Field(None, ge=0, description="Time taken in minutes")


class QuizSubmissionCreate(QuizSubmissionBase):
    """Schema for creating quiz submission"""
    pass


class QuizSubmissionResponse(QuizSubmissionBase, BaseContentSchema):
    """Quiz submission response"""
    id: int
    user_id: int
    score: Optional[float] = None
    is_passed: Optional[bool] = None
    feedback: Optional[str] = None
    submitted_at: datetime


# File upload schemas
class FileUploadResponse(BaseModel):
    """File upload response"""
    filename: str
    file_url: str
    file_size: int
    content_type: str
    upload_timestamp: datetime


class BulkUploadResponse(BaseModel):
    """Bulk file upload response"""
    uploaded_files: List[FileUploadResponse]
    failed_uploads: List[Dict[str, str]]
    total_files: int
    successful_uploads: int


# Search and filter schemas
class ContentSearchRequest(BaseModel):
    """Content search request"""
    query: str = Field(..., min_length=1, max_length=200)
    content_types: Optional[List[str]] = None
    subject_ids: Optional[List[int]] = None
    difficulty_levels: Optional[List[DifficultyLevelEnum]] = None
    grade_levels: Optional[List[GradeLevelEnum]] = None


class ContentSearchResponse(BaseModel):
    """Content search response"""
    results: List[Dict[str, Any]]
    total_results: int
    search_time: float
    suggestions: Optional[List[str]] = None


# Error response schemas
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None
    success: bool = False
    timestamp: Optional[datetime] = None
