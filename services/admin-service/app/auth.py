"""
Authentication and authorization for Admin Service
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import jwt
import os
from dotenv import load_dotenv
from pydantic import BaseModel

from .database import get_db
from .models import AdminUser, SystemRole

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Security scheme
security = HTTPBearer()

class CurrentUser(BaseModel):
    """Current user information"""
    id: int
    email: str
    username: str
    role: str
    school_id: Optional[int] = None
    is_active: bool = True
    permissions: Optional[dict] = None

class CurrentAdminUser(BaseModel):
    """Current admin user information"""
    id: int
    user_id: int
    email: str
    username: str
    role: str
    school_id: int
    system_role: SystemRole
    permissions: Optional[dict] = None
    departments: Optional[list] = None
    is_active: bool = True
    is_verified: bool = True

def decode_jwt_token(token: str) -> dict:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    
    # Extract user information from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return CurrentUser(
        id=int(user_id),
        email=payload.get("email", ""),
        username=payload.get("username", ""),
        role=payload.get("role", ""),
        school_id=payload.get("school_id"),
        is_active=payload.get("is_active", True),
        permissions=payload.get("permissions", {})
    )

def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CurrentAdminUser:
    """Get current admin user with admin privileges"""
    
    # Check if user has admin role
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get admin user record
    admin_user = db.query(AdminUser).filter(
        AdminUser.user_id == current_user.id,
        AdminUser.is_active == True
    ).first()
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user not found or inactive"
        )
    
    if not admin_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user not verified"
        )
    
    return CurrentAdminUser(
        id=admin_user.id,
        user_id=admin_user.user_id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        school_id=admin_user.school_id,
        system_role=admin_user.system_role,
        permissions=admin_user.permissions or {},
        departments=admin_user.departments or [],
        is_active=admin_user.is_active,
        is_verified=admin_user.is_verified
    )

def get_current_super_admin(
    current_admin: CurrentAdminUser = Depends(get_current_admin_user)
) -> CurrentAdminUser:
    """Get current super admin user"""
    if current_admin.system_role != SystemRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_admin

def get_current_school_admin(
    current_admin: CurrentAdminUser = Depends(get_current_admin_user)
) -> CurrentAdminUser:
    """Get current school admin user"""
    allowed_roles = [
        SystemRole.SUPER_ADMIN,
        SystemRole.SCHOOL_ADMIN,
        SystemRole.PRINCIPAL,
        SystemRole.VICE_PRINCIPAL
    ]
    
    if current_admin.system_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School admin access required"
        )
    return current_admin

def check_permission(
    current_admin: CurrentAdminUser,
    permission: str,
    resource_id: Optional[str] = None
) -> bool:
    """Check if admin user has specific permission"""
    
    # Super admin has all permissions
    if current_admin.system_role == SystemRole.SUPER_ADMIN:
        return True
    
    # Check permissions dictionary
    permissions = current_admin.permissions or {}
    
    # Check general permission
    if permission in permissions:
        return permissions[permission]
    
    # Check resource-specific permission
    if resource_id:
        resource_permissions = permissions.get(f"{permission}_{resource_id}", {})
        if resource_permissions:
            return resource_permissions
    
    return False

def require_permission(permission: str, resource_id: Optional[str] = None):
    """Decorator to require specific permission"""
    def decorator(current_admin: CurrentAdminUser = Depends(get_current_admin_user)):
        if not check_permission(current_admin, permission, resource_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_admin
    return decorator

def check_school_access(
    current_admin: CurrentAdminUser,
    school_id: int
) -> bool:
    """Check if admin user has access to specific school"""
    
    # Super admin has access to all schools
    if current_admin.system_role == SystemRole.SUPER_ADMIN:
        return True
    
    # Check if it's the admin's school
    return current_admin.school_id == school_id

def require_school_access(school_id: int):
    """Decorator to require access to specific school"""
    def decorator(current_admin: CurrentAdminUser = Depends(get_current_admin_user)):
        if not check_school_access(current_admin, school_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this school is not allowed"
            )
        return current_admin
    return decorator

def check_department_access(
    current_admin: CurrentAdminUser,
    department_id: str
) -> bool:
    """Check if admin user has access to specific department"""
    
    # Super admin and school admin have access to all departments
    if current_admin.system_role in [SystemRole.SUPER_ADMIN, SystemRole.SCHOOL_ADMIN]:
        return True
    
    # Check if department is in admin's assigned departments
    departments = current_admin.departments or []
    return department_id in departments

def create_audit_log(
    db: Session,
    admin_user_id: int,
    school_id: int,
    action: str,
    resource_type: str,
    resource_id: str,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    metadata: Optional[dict] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_method: Optional[str] = None,
    request_url: Optional[str] = None
):
    """Create audit log entry"""
    from .models import AuditLog
    
    audit_log = AuditLog(
        school_id=school_id,
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        metadata=metadata,
        success=success,
        error_message=error_message,
        ip_address=ip_address,
        user_agent=user_agent,
        request_method=request_method,
        request_url=request_url
    )
    
    db.add(audit_log)
    db.commit()
    
    return audit_log
