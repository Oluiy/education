"""
EduNerve Authentication Service - Pydantic Schemas
Request/Response models for API endpoints
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles enum for API"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    PARENT = "parent"


# School Schemas
class SchoolBase(BaseModel):
    """Base school schema"""
    name: str = Field(..., min_length=2, max_length=200)
    code: str = Field(..., min_length=2, max_length=20)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    principal_name: Optional[str] = None


class SchoolCreate(SchoolBase):
    """Schema for creating a new school"""
    pass


class SchoolResponse(SchoolBase):
    """Schema for school responses"""
    id: int
    is_active: bool
    max_students: int
    max_teachers: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    phone: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    role: UserRole
    school_id: int
    
    # Student-specific fields
    class_level: Optional[str] = None
    student_id: Optional[str] = None
    
    # Teacher-specific fields
    employee_id: Optional[str] = None
    subjects: Optional[str] = None  # JSON string
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not v.startswith('+'):
            # Assume Nigerian number if no country code
            if len(v) == 11 and v.startswith('0'):
                v = '+234' + v[1:]
            elif len(v) == 10:
                v = '+234' + v
        return v
    
    @validator('class_level')
    def validate_class_level(cls, v, values):
        """Validate class level for students"""
        if values.get('role') == UserRole.STUDENT and not v:
            raise ValueError('Class level is required for students')
        if v and v not in ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3']:
            raise ValueError('Invalid class level')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = None
    class_level: Optional[str] = None
    student_id: Optional[str] = None
    employee_id: Optional[str] = None
    subjects: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user responses"""
    id: int
    is_active: bool
    is_verified: bool
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    school: SchoolResponse
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    school_code: Optional[str] = None  # Optional school code for multi-tenant login


class UserLoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None
    user_id: Optional[int] = None
    school_id: Optional[int] = None
    role: Optional[str] = None


class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr
    school_code: Optional[str] = None


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    success: bool = False
