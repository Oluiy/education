"""
EduNerve File Storage Service - Authentication and Authorization
JWT validation and user context management
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import httpx
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

class CurrentUser:
    """Current user context"""
    def __init__(
        self,
        id: int,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        role: str,
        school_id: int,
        class_level: Optional[str] = None,
        student_id: Optional[str] = None,
        employee_id: Optional[str] = None,
        is_active: bool = True,
        permissions: Dict[str, Any] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.school_id = school_id
        self.class_level = class_level
        self.student_id = student_id
        self.employee_id = employee_id
        self.is_active = is_active
        self.permissions = permissions or {}
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return self.permissions.get(permission, False)
    
    def can_access_file(self, file_owner_id: int, file_school_id: int, access_level: str) -> bool:
        """Check if user can access a file"""
        # Owner can always access
        if file_owner_id == self.id:
            return True
        
        # School isolation
        if file_school_id != self.school_id:
            return False
        
        # Access level checks
        if access_level == "public":
            return True
        elif access_level == "school":
            return True
        elif access_level == "private":
            return False
        
        return False

async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token with auth service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/api/v1/auth/verify-token",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Verify token
    user_data = await verify_token(credentials.credentials)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Create user context
    return CurrentUser(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        role=user_data["role"],
        school_id=user_data["school_id"],
        class_level=user_data.get("class_level"),
        student_id=user_data.get("student_id"),
        employee_id=user_data.get("employee_id"),
        is_active=user_data.get("is_active", True),
        permissions=user_data.get("permissions", {})
    )

async def get_current_teacher(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Get current user if they are a teacher"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    return current_user

async def get_current_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Get current user if they are an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def check_file_access(
    current_user: CurrentUser,
    file_owner_id: int,
    file_school_id: int,
    access_level: str,
    required_permission: str = "read"
) -> bool:
    """Check if user can access a file"""
    # Check basic access
    if not current_user.can_access_file(file_owner_id, file_school_id, access_level):
        return False
    
    # Check specific permission
    if required_permission == "write":
        return current_user.has_permission("file.write") or file_owner_id == current_user.id
    elif required_permission == "delete":
        return current_user.has_permission("file.delete") or file_owner_id == current_user.id
    elif required_permission == "share":
        return current_user.has_permission("file.share") or file_owner_id == current_user.id
    
    return True

def create_file_activity_log(
    db: Session,
    file_id: str,
    user_id: int,
    action: str,
    context: Dict[str, Any] = None
):
    """Create file activity log entry"""
    from .models import FileAnalytics
    
    activity = FileAnalytics(
        file_id=file_id,
        user_id=user_id,
        school_id=context.get("school_id") if context else None,
        action=action,
        context=context or {},
        ip_address=context.get("ip_address") if context else None,
        user_agent=context.get("user_agent") if context else None,
        referrer=context.get("referrer") if context else None
    )
    
    db.add(activity)
    db.commit()

# Permission constants
class FilePermissions:
    READ = "file.read"
    WRITE = "file.write"
    DELETE = "file.delete"
    SHARE = "file.share"
    ADMIN = "file.admin"
