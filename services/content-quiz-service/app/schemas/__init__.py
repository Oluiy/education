"""
Schemas package for content-quiz service
"""

from .content_schemas import (
    SubjectCreate, SubjectUpdate, SubjectResponse,
    CourseCreate, CourseUpdate, CourseResponse,
    LessonCreate, LessonUpdate, LessonResponse,
    QuizCreate, QuizUpdate, QuizResponse,
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuizAttemptCreate, QuizAttemptResponse,
    LessonProgressCreate, LessonProgressResponse,
    ContentFileCreate, ContentFileResponse,
    ErrorResponse, PaginatedResponse
)

from .study_schemas import (
    StudySessionStart, StudySessionEnd, StudySessionUpdate, StudySessionResponse,
    StudySessionListResponse, StudyStreakResponse, StudyStreakUpdate,
    BadgeCreate, BadgeResponse, StudentBadgeResponse,
    StudyGoalCreate, StudyGoalUpdate, StudyGoalResponse,
    StudyAnalytics, StudyDashboard, TimerAction,
    StudySessionStatus, DeviceType, BadgeType
)

__all__ = [
    # Content schemas
    "SubjectCreate", "SubjectUpdate", "SubjectResponse",
    "CourseCreate", "CourseUpdate", "CourseResponse",
    "LessonCreate", "LessonUpdate", "LessonResponse",
    "QuizCreate", "QuizUpdate", "QuizResponse",
    "QuestionCreate", "QuestionUpdate", "QuestionResponse",
    "QuizAttemptCreate", "QuizAttemptResponse",
    "LessonProgressCreate", "LessonProgressResponse",
    "ContentFileCreate", "ContentFileResponse",
    "ErrorResponse", "PaginatedResponse",
    
    # Study schemas
    "StudySessionStart", "StudySessionEnd", "StudySessionUpdate", "StudySessionResponse",
    "StudySessionListResponse", "StudyStreakResponse", "StudyStreakUpdate",
    "BadgeCreate", "BadgeResponse", "StudentBadgeResponse",
    "StudyGoalCreate", "StudyGoalUpdate", "StudyGoalResponse",
    "StudyAnalytics", "StudyDashboard", "TimerAction",
    "StudySessionStatus", "DeviceType", "BadgeType"
]
