"""
EduNerve Assistant Service - Authentication Module
"""

import os
import httpx
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Auth service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

# Security scheme
security = HTTPBearer()


class CurrentUser(BaseModel):
    """Current user model for dependency injection"""
    id: int
    email: str
    username: str
    full_name: str
    user_type: str
    is_active: bool
    school_id: int
    school_name: str
    
    @property
    def is_student(self) -> bool:
        """Check if user is a student"""
        return self.user_type == "student"
    
    @property
    def is_teacher(self) -> bool:
        """Check if user is a teacher"""
        return self.user_type == "teacher"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.user_type == "admin"


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    """
    Get current user from JWT token by calling auth service
    """
    try:
        # Call auth service to validate token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {credentials.credentials}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Auth service returned {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication credentials"
                )
            
            user_data = response.json()
            
            # Convert to CurrentUser model
            return CurrentUser(
                id=user_data["id"],
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                user_type=user_data["user_type"],
                is_active=user_data["is_active"],
                school_id=user_data["school_id"],
                school_name=user_data["school_name"]
            )
            
    except httpx.RequestError as e:
        logger.error(f"Error connecting to auth service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable"
        )
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )


async def get_current_student_user(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Get current user and ensure they are a student
    """
    if not current_user.is_student:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only accessible to students"
        )
    return current_user


async def get_current_teacher_user(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Get current user and ensure they are a teacher
    """
    if not current_user.is_teacher:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only accessible to teachers"
        )
    return current_user


async def get_current_admin_user(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Get current user and ensure they are an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only accessible to admins"
        )
    return current_user
