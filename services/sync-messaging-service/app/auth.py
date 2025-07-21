"""
EduNerve Sync & Messaging Service - Authentication
JWT token validation and user authentication
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import os
import httpx
import logging
from datetime import datetime
from dotenv import load_dotenv
# Import security modules
from app.security_config import get_jwt_config, SecurityConfig
from app.input_validation import InputValidator
from app.error_handling import SecurityError, ErrorResponseHandler


# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

# Security
security = HTTPBearer()

class CurrentUser:
    """Current authenticated user data"""
    def __init__(self, user_data: Dict[str, Any]):
        self.id = user_data.get("id")
        self.user_id = user_data.get("user_id") or user_data.get("id")
        self.email = user_data.get("email")
        self.username = user_data.get("username")
        self.full_name = user_data.get("full_name")
        self.school_id = user_data.get("school_id")
        self.role = user_data.get("role", "student")
        self.permissions = user_data.get("permissions", [])
        self.is_active = user_data.get("is_active", True)
        self.is_verified = user_data.get("is_verified", False)

def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        return None

async def verify_token_with_auth_service(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify token with auth service
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Token verification failed: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error verifying token with auth service: {str(e)}")
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Get current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # First try to decode token locally
        payload = decode_jwt_token(token)
        if not payload:
            # If local decode fails, verify with auth service
            user_data = await verify_token_with_auth_service(token)
            if not user_data:
                raise credentials_exception
        else:
            # Use payload data
            user_data = payload
        
        # Create current user object
        current_user = CurrentUser(user_data)
        
        if not current_user.user_id:
            raise credentials_exception
        
        return current_user
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise credentials_exception

async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_verified_user(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> CurrentUser:
    """
    Get current verified user
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unverified user"
        )
    return current_user

def check_permission(user: CurrentUser, required_permission: str) -> bool:
    """
    Check if user has required permission
    """
    if not user.permissions:
        return False
    
    # Admin and teacher roles have elevated permissions
    if user.role in ["admin", "teacher", "school_admin"]:
        return True
    
    return required_permission in user.permissions

def require_permission(permission: str):
    """
    Decorator to require specific permission
    """
    def permission_dependency(current_user: CurrentUser = Depends(get_current_verified_user)):
        if not check_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return permission_dependency

def require_role(role: str):
    """
    Decorator to require specific role
    """
    def role_dependency(current_user: CurrentUser = Depends(get_current_verified_user)):
        if current_user.role != role and current_user.role not in ["admin", "school_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        return current_user
    
    return role_dependency

def require_school_access(school_id: int):
    """
    Check if user has access to specific school
    """
    def school_dependency(current_user: CurrentUser = Depends(get_current_verified_user)):
        # Super admins have access to all schools
        if current_user.role == "admin":
            return current_user
        
        # Users can only access their own school
        if current_user.school_id != school_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this school denied"
            )
        return current_user
    
    return school_dependency

# User type dependencies
async def get_student_user(
    current_user: CurrentUser = Depends(get_current_verified_user)
) -> CurrentUser:
    """Get current student user"""
    if current_user.role not in ["student", "admin", "school_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user

async def get_teacher_user(
    current_user: CurrentUser = Depends(get_current_verified_user)
) -> CurrentUser:
    """Get current teacher user"""
    if current_user.role not in ["teacher", "admin", "school_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    return current_user

async def get_admin_user(
    current_user: CurrentUser = Depends(get_current_verified_user)
) -> CurrentUser:
    """Get current admin user"""
    if current_user.role not in ["admin", "school_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Utility functions
def create_user_context(user: CurrentUser) -> Dict[str, Any]:
    """
    Create user context for logging and tracking
    """
    return {
        "user_id": user.user_id,
        "school_id": user.school_id,
        "role": user.role,
        "timestamp": datetime.utcnow().isoformat()
    }

async def validate_device_access(user: CurrentUser, device_id: str) -> bool:
    """
    Validate if user has access to specific device
    """
    # In a real implementation, you would check if the device belongs to the user
    # For now, we'll assume all devices belong to the user
    return True

async def log_user_activity(
    user: CurrentUser,
    action: str,
    resource: str,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log user activity for audit purposes
    """
    try:
        activity_log = {
            "user_id": user.user_id,
            "school_id": user.school_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # In a real implementation, you would save this to a logging service
        logger.info(f"User activity: {activity_log}")
        
    except Exception as e:
        logger.error(f"Error logging user activity: {str(e)}")

# Optional authentication for public endpoints
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[CurrentUser]:
    """
    Get current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_jwt_token(token)
        
        if payload:
            return CurrentUser(payload)
    except Exception as e:
        logger.warning(f"Optional authentication failed: {str(e)}")
    
    return None
