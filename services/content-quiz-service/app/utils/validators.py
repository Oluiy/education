"""
Data Validation Utilities
Comprehensive validation for educational content and user data
"""

import re
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import mimetypes
import os


class ValidationResult:
    """Validation result container"""
    
    def __init__(self, valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning"""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


class ContentValidator:
    """Validator for educational content"""
    
    # Valid content types
    VALID_LESSON_TYPES = ["video", "text", "pdf", "interactive", "quiz", "assignment"]
    VALID_QUIZ_TYPES = ["multiple_choice", "true_false", "short_answer", "essay", "matching", "ordering"]
    VALID_DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced", "expert"]
    VALID_GRADE_LEVELS = ["SS1", "SS2", "SS3", "JSS1", "JSS2", "JSS3"]
    
    # Content length limits
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200
    MIN_DESCRIPTION_LENGTH = 10
    MAX_DESCRIPTION_LENGTH = 1000
    MIN_CONTENT_LENGTH = 50
    MAX_CONTENT_LENGTH = 50000
    
    @staticmethod
    def validate_subject_data(data: Dict[str, Any]) -> ValidationResult:
        """Validate subject data"""
        result = ValidationResult()
        
        # Required fields
        required_fields = ["name", "code"]
        for field in required_fields:
            if field not in data or not data[field]:
                result.add_error(f"Field '{field}' is required")
        
        # Validate name
        if "name" in data:
            name = data["name"].strip()
            if len(name) < ContentValidator.MIN_TITLE_LENGTH:
                result.add_error(f"Subject name must be at least {ContentValidator.MIN_TITLE_LENGTH} characters")
            elif len(name) > ContentValidator.MAX_TITLE_LENGTH:
                result.add_error(f"Subject name must not exceed {ContentValidator.MAX_TITLE_LENGTH} characters")
        
        # Validate code
        if "code" in data:
            code = data["code"].strip().upper()
            if not re.match(r'^[A-Z0-9]{2,10}$', code):
                result.add_error("Subject code must be 2-10 alphanumeric characters")
        
        # Validate description
        if "description" in data and data["description"]:
            desc = data["description"].strip()
            if len(desc) > ContentValidator.MAX_DESCRIPTION_LENGTH:
                result.add_error(f"Description must not exceed {ContentValidator.MAX_DESCRIPTION_LENGTH} characters")
        
        # Validate grade level
        if "grade_level" in data and data["grade_level"]:
            if data["grade_level"] not in ContentValidator.VALID_GRADE_LEVELS:
                result.add_error(f"Invalid grade level. Must be one of: {', '.join(ContentValidator.VALID_GRADE_LEVELS)}")
        
        # Validate color theme (if provided)
        if "color_theme" in data and data["color_theme"]:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', data["color_theme"]):
                result.add_error("Color theme must be a valid hex color code (e.g., #FF5733)")
        
        return result
    
    @staticmethod
    def validate_course_data(data: Dict[str, Any]) -> ValidationResult:
        """Validate course data"""
        result = ValidationResult()
        
        # Required fields
        required_fields = ["name", "subject_id"]
        for field in required_fields:
            if field not in data or not data[field]:
                result.add_error(f"Field '{field}' is required")
        
        # Validate name
        if "name" in data:
            name = data["name"].strip()
            if len(name) < ContentValidator.MIN_TITLE_LENGTH:
                result.add_error(f"Course name must be at least {ContentValidator.MIN_TITLE_LENGTH} characters")
            elif len(name) > ContentValidator.MAX_TITLE_LENGTH:
                result.add_error(f"Course name must not exceed {ContentValidator.MAX_TITLE_LENGTH} characters")
        
        # Validate description
        if "description" in data and data["description"]:
            desc = data["description"].strip()
            if len(desc) < ContentValidator.MIN_DESCRIPTION_LENGTH:
                result.add_error(f"Description must be at least {ContentValidator.MIN_DESCRIPTION_LENGTH} characters")
            elif len(desc) > ContentValidator.MAX_DESCRIPTION_LENGTH:
                result.add_error(f"Description must not exceed {ContentValidator.MAX_DESCRIPTION_LENGTH} characters")
        
        # Validate level
        if "level" in data and data["level"]:
            if data["level"] not in ContentValidator.VALID_DIFFICULTY_LEVELS:
                result.add_error(f"Invalid level. Must be one of: {', '.join(ContentValidator.VALID_DIFFICULTY_LEVELS)}")
        
        # Validate estimated duration
        if "estimated_duration" in data and data["estimated_duration"] is not None:
            duration = data["estimated_duration"]
            if not isinstance(duration, int) or duration < 1:
                result.add_error("Estimated duration must be a positive integer (minutes)")
            elif duration > 10080:  # 1 week in minutes
                result.add_warning("Estimated duration seems very long (over 1 week)")
        
        # Validate order index
        if "order_index" in data and data["order_index"] is not None:
            if not isinstance(data["order_index"], int) or data["order_index"] < 0:
                result.add_error("Order index must be a non-negative integer")
        
        # Validate prerequisite courses
        if "prerequisite_courses" in data and data["prerequisite_courses"]:
            prereqs = data["prerequisite_courses"]
            if not isinstance(prereqs, list):
                result.add_error("Prerequisite courses must be a list of course IDs")
            else:
                for prereq in prereqs:
                    if not isinstance(prereq, int) or prereq < 1:
                        result.add_error("Each prerequisite course ID must be a positive integer")
        
        # Validate learning objectives
        if "learning_objectives" in data and data["learning_objectives"]:
            objectives = data["learning_objectives"]
            if not isinstance(objectives, list):
                result.add_error("Learning objectives must be a list of strings")
            else:
                for i, obj in enumerate(objectives):
                    if not isinstance(obj, str) or len(obj.strip()) < 10:
                        result.add_error(f"Learning objective {i+1} must be at least 10 characters")
        
        return result
    
    @staticmethod
    def validate_lesson_data(data: Dict[str, Any]) -> ValidationResult:
        """Validate lesson data"""
        result = ValidationResult()
        
        # Required fields
        required_fields = ["title", "course_id", "lesson_type"]
        for field in required_fields:
            if field not in data or not data[field]:
                result.add_error(f"Field '{field}' is required")
        
        # Validate title
        if "title" in data:
            title = data["title"].strip()
            if len(title) < ContentValidator.MIN_TITLE_LENGTH:
                result.add_error(f"Lesson title must be at least {ContentValidator.MIN_TITLE_LENGTH} characters")
            elif len(title) > ContentValidator.MAX_TITLE_LENGTH:
                result.add_error(f"Lesson title must not exceed {ContentValidator.MAX_TITLE_LENGTH} characters")
        
        # Validate lesson type
        if "lesson_type" in data:
            if data["lesson_type"] not in ContentValidator.VALID_LESSON_TYPES:
                result.add_error(f"Invalid lesson type. Must be one of: {', '.join(ContentValidator.VALID_LESSON_TYPES)}")
        
        # Validate content
        if "content" in data and data["content"]:
            content = data["content"].strip()
            if len(content) < ContentValidator.MIN_CONTENT_LENGTH:
                result.add_error(f"Lesson content must be at least {ContentValidator.MIN_CONTENT_LENGTH} characters")
            elif len(content) > ContentValidator.MAX_CONTENT_LENGTH:
                result.add_error(f"Lesson content must not exceed {ContentValidator.MAX_CONTENT_LENGTH} characters")
        
        # Validate difficulty level
        if "difficulty_level" in data and data["difficulty_level"]:
            if data["difficulty_level"] not in ContentValidator.VALID_DIFFICULTY_LEVELS:
                result.add_error(f"Invalid difficulty level. Must be one of: {', '.join(ContentValidator.VALID_DIFFICULTY_LEVELS)}")
        
        # Validate estimated duration
        if "estimated_duration" in data and data["estimated_duration"] is not None:
            duration = data["estimated_duration"]
            if not isinstance(duration, int) or duration < 1:
                result.add_error("Estimated duration must be a positive integer (minutes)")
            elif duration > 480:  # 8 hours
                result.add_warning("Estimated duration seems very long (over 8 hours)")
        
        # Validate order index
        if "order_index" in data and data["order_index"] is not None:
            if not isinstance(data["order_index"], int) or data["order_index"] < 0:
                result.add_error("Order index must be a non-negative integer")
        
        return result
    
    @staticmethod
    def validate_quiz_data(data: Dict[str, Any]) -> ValidationResult:
        """Validate quiz data"""
        result = ValidationResult()
        
        # Required fields
        required_fields = ["title", "course_id", "quiz_type"]
        for field in required_fields:
            if field not in data or not data[field]:
                result.add_error(f"Field '{field}' is required")
        
        # Validate title
        if "title" in data:
            title = data["title"].strip()
            if len(title) < ContentValidator.MIN_TITLE_LENGTH:
                result.add_error(f"Quiz title must be at least {ContentValidator.MIN_TITLE_LENGTH} characters")
            elif len(title) > ContentValidator.MAX_TITLE_LENGTH:
                result.add_error(f"Quiz title must not exceed {ContentValidator.MAX_TITLE_LENGTH} characters")
        
        # Validate quiz type
        if "quiz_type" in data:
            if data["quiz_type"] not in ContentValidator.VALID_QUIZ_TYPES:
                result.add_error(f"Invalid quiz type. Must be one of: {', '.join(ContentValidator.VALID_QUIZ_TYPES)}")
        
        # Validate time limit
        if "time_limit" in data and data["time_limit"] is not None:
            time_limit = data["time_limit"]
            if not isinstance(time_limit, int) or time_limit < 1:
                result.add_error("Time limit must be a positive integer (minutes)")
            elif time_limit > 480:  # 8 hours
                result.add_warning("Time limit seems very long (over 8 hours)")
        
        # Validate passing score
        if "passing_score" in data and data["passing_score"] is not None:
            score = data["passing_score"]
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                result.add_error("Passing score must be a number between 0 and 100")
        
        # Validate total questions
        if "total_questions" in data and data["total_questions"] is not None:
            total = data["total_questions"]
            if not isinstance(total, int) or total < 1:
                result.add_error("Total questions must be a positive integer")
            elif total > 200:
                result.add_warning("Very large number of questions (over 200)")
        
        return result


class FileValidator:
    """Validator for file uploads"""
    
    # Allowed file types and sizes
    ALLOWED_IMAGE_TYPES = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    ALLOWED_VIDEO_TYPES = [".mp4", ".avi", ".mov", ".wmv", ".flv"]
    ALLOWED_AUDIO_TYPES = [".mp3", ".wav", ".ogg", ".m4a"]
    ALLOWED_DOCUMENT_TYPES = [".pdf", ".doc", ".docx", ".txt", ".rtf"]
    
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_DOCUMENT_SIZE = 25 * 1024 * 1024  # 25MB
    
    @staticmethod
    def validate_file(filename: str, file_size: int, content_type: str = None) -> ValidationResult:
        """Validate uploaded file"""
        result = ValidationResult()
        
        if not filename:
            result.add_error("Filename is required")
            return result
        
        # Get file extension
        ext = os.path.splitext(filename.lower())[1]
        
        # Validate file extension
        all_allowed = (
            FileValidator.ALLOWED_IMAGE_TYPES +
            FileValidator.ALLOWED_VIDEO_TYPES +
            FileValidator.ALLOWED_AUDIO_TYPES +
            FileValidator.ALLOWED_DOCUMENT_TYPES
        )
        
        if ext not in all_allowed:
            result.add_error(f"File type '{ext}' is not allowed")
            return result
        
        # Validate file size based on type
        if ext in FileValidator.ALLOWED_IMAGE_TYPES:
            if file_size > FileValidator.MAX_IMAGE_SIZE:
                result.add_error(f"Image file too large. Maximum size: {FileValidator.MAX_IMAGE_SIZE // (1024*1024)}MB")
        elif ext in FileValidator.ALLOWED_VIDEO_TYPES:
            if file_size > FileValidator.MAX_VIDEO_SIZE:
                result.add_error(f"Video file too large. Maximum size: {FileValidator.MAX_VIDEO_SIZE // (1024*1024)}MB")
        elif ext in FileValidator.ALLOWED_AUDIO_TYPES:
            if file_size > FileValidator.MAX_AUDIO_SIZE:
                result.add_error(f"Audio file too large. Maximum size: {FileValidator.MAX_AUDIO_SIZE // (1024*1024)}MB")
        elif ext in FileValidator.ALLOWED_DOCUMENT_TYPES:
            if file_size > FileValidator.MAX_DOCUMENT_SIZE:
                result.add_error(f"Document file too large. Maximum size: {FileValidator.MAX_DOCUMENT_SIZE // (1024*1024)}MB")
        
        # Validate content type if provided
        if content_type:
            expected_type = mimetypes.guess_type(filename)[0]
            if expected_type and not content_type.startswith(expected_type.split('/')[0]):
                result.add_warning(f"Content type mismatch. Expected: {expected_type}, Got: {content_type}")
        
        # Security checks
        dangerous_extensions = [".exe", ".bat", ".sh", ".php", ".asp", ".jsp"]
        if ext in dangerous_extensions:
            result.add_error(f"Dangerous file type '{ext}' is not allowed")
        
        # Check for suspicious filenames
        if any(char in filename for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']):
            result.add_error("Filename contains invalid characters")
        
        return result
    
    @staticmethod
    def validate_image_file(filename: str, file_size: int) -> ValidationResult:
        """Validate image file specifically"""
        result = FileValidator.validate_file(filename, file_size)
        
        ext = os.path.splitext(filename.lower())[1]
        if ext not in FileValidator.ALLOWED_IMAGE_TYPES:
            result.add_error(f"Only image files are allowed: {', '.join(FileValidator.ALLOWED_IMAGE_TYPES)}")
        
        return result


class UserDataValidator:
    """Validator for user data"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (Nigerian format)"""
        if not phone:
            return False
        
        # Remove spaces and dashes
        phone = re.sub(r'[\s-]', '', phone)
        
        # Nigerian phone patterns
        patterns = [
            r'^\+234[789][01]\d{8}$',  # +234 format
            r'^234[789][01]\d{8}$',    # 234 format
            r'^0[789][01]\d{8}$',      # 0 format
            r'^[789][01]\d{8}$'        # Direct format
        ]
        
        return any(re.match(pattern, phone) for pattern in patterns)
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> ValidationResult:
        """Validate name field"""
        result = ValidationResult()
        
        if not name or not name.strip():
            result.add_error(f"{field_name} is required")
            return result
        
        name = name.strip()
        
        if len(name) < 2:
            result.add_error(f"{field_name} must be at least 2 characters")
        
        if len(name) > 50:
            result.add_error(f"{field_name} must not exceed 50 characters")
        
        if not re.match(r'^[a-zA-Z\s\'-]+$', name):
            result.add_error(f"{field_name} contains invalid characters")
        
        return result


# Convenience functions
def validate_subject_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate subject data and return result as dict"""
    return ContentValidator.validate_subject_data(data).to_dict()


def validate_course_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate course data and return result as dict"""
    return ContentValidator.validate_course_data(data).to_dict()


def validate_lesson_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate lesson data and return result as dict"""
    return ContentValidator.validate_lesson_data(data).to_dict()


def validate_quiz_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate quiz data and return result as dict"""
    return ContentValidator.validate_quiz_data(data).to_dict()


def validate_file_upload(filename: str, file_size: int, content_type: str = None) -> Dict[str, Any]:
    """Validate file upload and return result as dict"""
    return FileValidator.validate_file(filename, file_size, content_type).to_dict()


# Export commonly used validators
__all__ = [
    "ValidationResult",
    "ContentValidator",
    "FileValidator", 
    "UserDataValidator",
    "validate_subject_data",
    "validate_course_data",
    "validate_lesson_data",
    "validate_quiz_data",
    "validate_file_upload"
]
