"""
EduNerve Notification Service - Authentication and Authorization
JWT validation and user context management
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import httpx
import os
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
    
    def can_send_notifications(self) -> bool:
        """Check if user can send notifications"""
        return self.role in ["teacher", "admin"] or self.has_permission("notification.send")
    
    def can_send_bulk_notifications(self) -> bool:
        """Check if user can send bulk notifications"""
        return self.role == "admin" or self.has_permission("notification.bulk")
    
    def can_manage_templates(self) -> bool:
        """Check if user can manage notification templates"""
        return self.role == "admin" or self.has_permission("notification.template.manage")

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

async def get_notification_sender(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Get current user if they can send notifications"""
    if not current_user.can_send_notifications():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission required to send notifications"
        )
    return current_user

async def get_bulk_notification_sender(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Get current user if they can send bulk notifications"""
    if not current_user.can_send_bulk_notifications():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission required to send bulk notifications"
        )
    return current_user

async def get_template_manager(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Get current user if they can manage templates"""
    if not current_user.can_manage_templates():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission required to manage templates"
        )
    return current_user

# Permission constants
class NotificationPermissions:
    SEND = "notification.send"
    BULK = "notification.bulk"
    TEMPLATE_MANAGE = "notification.template.manage"
    TEMPLATE_CREATE = "notification.template.create"
    SETTINGS_MANAGE = "notification.settings.manage"
    ANALYTICS_VIEW = "notification.analytics.view"
    ADMIN = "notification.admin"
