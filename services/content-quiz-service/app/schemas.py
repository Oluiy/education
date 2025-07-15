"""
EduNerve Content & Quiz Service - Pydantic Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    """Content types enum"""
    PDF = "pdf"
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    PRESENTATION = "presentation"


class QuizType(str, Enum):
    """Quiz types enum"""
    MCQ = "mcq"
    THEORY = "theory"
    MIXED = "mixed"


class DifficultyLevel(str, Enum):
    """Difficulty levels enum"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SubmissionStatus(str, Enum):
    """Submission status enum"""
    PENDING = "pending"
    GRADED = "graded"
    REVIEWED = "reviewed"


# Content Schemas
class ContentBase(BaseModel):
    """Base content schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content_type: ContentType
    subject: str = Field(..., min_length=1, max_length=100)
    class_level: str = Field(..., min_length=1, max_length=20)
    topic: Optional[str] = None
    keywords: Optional[List[str]] = None
    is_public: bool = False
    
    @validator('class_level')
    def validate_class_level(cls, v):
        """Validate class level"""
        allowed_levels = ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3']
        if v not in allowed_levels:
            raise ValueError(f'Class level must be one of {allowed_levels}')
        return v


class ContentCreate(ContentBase):
    """Schema for creating content"""
    content_text: Optional[str] = None


class ContentUpdate(BaseModel):
    """Schema for updating content"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    class_level: Optional[str] = Field(None, min_length=1, max_length=20)
    topic: Optional[str] = None
    keywords: Optional[List[str]] = None
    is_public: Optional[bool] = None


class ContentResponse(ContentBase):
    """Schema for content responses"""
    id: int
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    school_id: int
    uploaded_by: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Quiz Question Schemas
class MCQOption(BaseModel):
    """Multiple choice question option"""
    text: str
    is_correct: bool = False


class MCQQuestion(BaseModel):
    """Multiple choice question"""
    question_id: str
    question_text: str
    options: List[MCQOption]
    marks: float = 1.0
    explanation: Optional[str] = None


class TheoryQuestion(BaseModel):
    """Theory question"""
    question_id: str
    question_text: str
    marks: float = 5.0
    suggested_answer: Optional[str] = None
    grading_criteria: Optional[List[str]] = None


class QuizQuestion(BaseModel):
    """Generic quiz question"""
    question_id: str
    question_type: str  # "mcq" or "theory"
    question_text: str
    marks: float
    options: Optional[List[MCQOption]] = None  # For MCQ
    suggested_answer: Optional[str] = None     # For theory
    grading_criteria: Optional[List[str]] = None
    explanation: Optional[str] = None


# Quiz Schemas
class QuizBase(BaseModel):
    """Base quiz schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    quiz_type: QuizType
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    subject: str = Field(..., min_length=1, max_length=100)
    class_level: str = Field(..., min_length=1, max_length=20)
    topic: Optional[str] = None
    duration_minutes: Optional[int] = None
    pass_mark: float = 50.0
    
    @validator('class_level')
    def validate_class_level(cls, v):
        """Validate class level"""
        allowed_levels = ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3']
        if v not in allowed_levels:
            raise ValueError(f'Class level must be one of {allowed_levels}')
        return v


class QuizCreate(QuizBase):
    """Schema for creating quiz"""
    content_id: Optional[int] = None
    questions: List[QuizQuestion]


class QuizUpdate(BaseModel):
    """Schema for updating quiz"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    duration_minutes: Optional[int] = None
    pass_mark: Optional[float] = None
    is_published: Optional[bool] = None


class QuizResponse(QuizBase):
    """Schema for quiz responses"""
    id: int
    total_questions: int
    total_marks: float
    content_id: Optional[int] = None
    school_id: int
    created_by: int
    is_ai_generated: bool
    is_active: bool
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    questions: List[QuizQuestion]
    
    class Config:
        from_attributes = True


# AI Quiz Generation Schemas
class AIQuizRequest(BaseModel):
    """Schema for AI quiz generation request"""
    content_id: Optional[int] = None
    content_text: Optional[str] = None
    subject: str
    class_level: str
    topic: Optional[str] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    quiz_type: QuizType = QuizType.MCQ
    num_questions: int = Field(default=10, ge=1, le=50)
    duration_minutes: Optional[int] = None
    
    @validator('content_text')
    def validate_content(cls, v, values):
        """Ensure either content_id or content_text is provided"""
        if not v and not values.get('content_id'):
            raise ValueError('Either content_id or content_text must be provided')
        return v


class AIQuizResponse(BaseModel):
    """Schema for AI quiz generation response"""
    quiz_id: int
    generation_prompt: str
    generated_questions: List[QuizQuestion]
    total_questions: int
    total_marks: float
    generation_model: str
    success: bool = True


# Submission Schemas
class SubmissionAnswer(BaseModel):
    """Individual answer in a submission"""
    question_id: str
    answer: Union[str, List[str]]  # String for theory, list for MCQ
    time_spent_seconds: Optional[int] = None


class SubmissionCreate(BaseModel):
    """Schema for creating a submission"""
    quiz_id: int
    answers: List[SubmissionAnswer]
    time_taken_minutes: Optional[int] = None


class SubmissionResponse(BaseModel):
    """Schema for submission responses"""
    id: int
    quiz_id: int
    student_id: int
    school_id: int
    answers: List[Dict[str, Any]]
    submission_time: datetime
    time_taken_minutes: Optional[int] = None
    status: SubmissionStatus
    total_score: Optional[float] = None
    percentage: Optional[float] = None
    mcq_score: Optional[float] = None
    theory_score: Optional[float] = None
    graded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Grading Schemas
class GradeCreate(BaseModel):
    """Schema for creating a grade"""
    submission_id: int
    question_id: str
    student_answer: str
    correct_answer: str
    marks_awarded: float
    max_marks: float
    ai_explanation: Optional[str] = None


class GradeResponse(BaseModel):
    """Schema for grade responses"""
    id: int
    submission_id: int
    question_id: str
    student_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    marks_awarded: float
    max_marks: float
    is_ai_graded: bool
    ai_confidence: Optional[float] = None
    ai_explanation: Optional[str] = None
    graded_at: datetime
    
    class Config:
        from_attributes = True


# File Upload Schemas
class FileUploadResponse(BaseModel):
    """Schema for file upload responses"""
    filename: str
    file_path: str
    file_url: Optional[str] = None
    file_size: int
    content_type: str
    success: bool = True


# Statistics Schemas
class QuizStats(BaseModel):
    """Quiz statistics"""
    quiz_id: int
    total_attempts: int
    total_submissions: int
    average_score: float
    highest_score: float
    lowest_score: float
    pass_rate: float


class ContentStats(BaseModel):
    """Content statistics"""
    content_id: int
    view_count: int
    download_count: int
    quiz_generation_count: int
    last_accessed: Optional[datetime] = None


# Response Schemas
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    success: bool = False


# Bulk Operations
class BulkQuizCreate(BaseModel):
    """Schema for bulk quiz creation"""
    quizzes: List[QuizCreate]


class BulkSubmissionResponse(BaseModel):
    """Schema for bulk submission responses"""
    total_processed: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]]


# Course schemas
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    difficulty: str = "beginner"
    duration: Optional[str] = None
    objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    price: float = 0.0
    is_free: bool = True
    is_featured: bool = False


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    duration: Optional[str] = None
    objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    price: Optional[float] = None
    is_free: Optional[bool] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None


class CourseResponse(CourseBase):
    id: int
    instructor_id: int
    school_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CourseWithStats(CourseResponse):
    total_lessons: int
    total_students: int
    avg_rating: Optional[float] = None
    total_duration: Optional[int] = None  # Total duration in minutes


# Lesson schemas
class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration: Optional[int] = None
    order: int = 0
    video_url: Optional[str] = None
    content_text: Optional[str] = None
    resources: Optional[List[str]] = None
    is_published: bool = False


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    order: Optional[int] = None
    video_url: Optional[str] = None
    content_text: Optional[str] = None
    resources: Optional[List[str]] = None
    is_published: Optional[bool] = None


class LessonResponse(LessonBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Enrollment schemas
class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentResponse(BaseModel):
    id: int
    course_id: int
    student_id: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    progress_percentage: float
    completed_lessons: int
    
    class Config:
        from_attributes = True


class EnrollmentWithCourse(EnrollmentResponse):
    course: CourseResponse


# Progress schemas
class ProgressUpdate(BaseModel):
    completed: bool = False
    time_spent: int = 0


class ProgressResponse(BaseModel):
    id: int
    lesson_id: int
    student_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    completed: bool
    time_spent: int
    
    class Config:
        from_attributes = True


# Course Progress Response
class CourseProgressResponse(BaseModel):
    course_id: int
    student_id: int
    progress_percentage: float
    completed_lessons: int
    total_lessons: int
    enrollment_date: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    class Config:
        from_attributes = True
