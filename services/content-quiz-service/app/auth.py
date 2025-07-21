"""
EduNerve Content & Quiz Service - Enhanced Authentication & Authorization
JWT token verification and user management with enhanced security
"""

import os
import httpx
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging
import jwt
import time

# Import security modules
from app.security_config import get_jwt_config, SecurityConfig
from app.input_validation import InputValidator
from app.error_handling import SecurityError, ErrorResponseHandler
from app.schemas import TokenData

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced security configuration
security_config = SecurityConfig()
jwt_config = get_jwt_config()

# Authentication configuration
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000/api/v1/auth")
security = HTTPBearer()

# Enhanced JWT Configuration
SECRET_KEY = jwt_config["secret_key"]
ALGORITHM = jwt_config["algorithm"]
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_config["access_token_expire_minutes"]

# Enhanced exceptions with security logging
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required",
    headers={"WWW-Authenticate": "Bearer"},
)

permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access denied",
)


class AuthService:
    """Service for handling authentication with the auth microservice"""
    
    def __init__(self):
        self.base_url = AUTH_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token with auth service"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{self.base_url}/me", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Token verification failed: {response.status_code}")
                raise credentials_exception
                
        except httpx.RequestError as e:
            logger.error(f"Auth service connection error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise credentials_exception
    
    async def get_user_by_id(self, user_id: int, token: str) -> Dict[str, Any]:
        """Get user details by ID"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{self.base_url}/users/{user_id}", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}")
            return None
    
    async def check_user_permissions(self, user_data: Dict[str, Any], required_roles: list) -> bool:
        """Check if user has required permissions"""
        user_role = user_data.get("role")
        return user_role in required_roles


# Global auth service instance
auth_service = AuthService()


# User data model
class CurrentUser:
    """Current user information from JWT token"""
    
    def __init__(self, user_data: Dict[str, Any]):
        self.id = user_data.get("id")
        self.email = user_data.get("email")
        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")
        self.role = user_data.get("role")
        self.school_id = user_data.get("school_id")
        self.class_level = user_data.get("class_level")
        self.is_active = user_data.get("is_active", True)
        self.raw_data = user_data
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_student(self) -> bool:
        """Check if user is a student"""
        return self.role == "student"
    
    @property
    def is_teacher(self) -> bool:
        """Check if user is a teacher"""
        return self.role == "teacher"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == "admin"
    
    def can_access_school(self, school_id: int) -> bool:
        """Check if user can access resources from a specific school"""
        return self.school_id == school_id


# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """Get current authenticated user"""
    token = credentials.credentials
    user_data = await auth_service.verify_token(token)
    
    if not user_data or not user_data.get("is_active"):
        raise credentials_exception
    
    return CurrentUser(user_data)


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: list[str]):
    """Decorator to require specific user roles"""
    def role_checker(current_user: CurrentUser = Depends(get_current_active_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise permission_exception
        return current_user
    
    return role_checker


def require_same_school(current_user: CurrentUser = Depends(get_current_active_user)):
    """Ensure user can only access resources from their own school"""
    def school_checker(school_id: int) -> bool:
        if not current_user.can_access_school(school_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: different school"
            )
        return True
    
    return school_checker


# Role-based dependencies
async def get_current_admin_user(
    current_user: CurrentUser = Depends(require_role(["admin"]))
) -> CurrentUser:
    """Get current admin user"""
    return current_user


async def get_current_teacher_user(
    current_user: CurrentUser = Depends(require_role(["teacher", "admin"]))
) -> CurrentUser:
    """Get current teacher or admin user"""
    return current_user


async def get_current_student_user(
    current_user: CurrentUser = Depends(require_role(["student"]))
) -> CurrentUser:
    """Get current student user"""
    return current_user


# Utility functions
def check_school_access(user: CurrentUser, resource_school_id: int) -> bool:
    """Check if user can access a resource from a specific school"""
    if user.school_id != resource_school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: resource belongs to different school"
        )
    return True


def check_content_access(user: CurrentUser, content_school_id: int, is_public: bool = False) -> bool:
    """Check if user can access content"""
    if is_public:
        return True  # Public content can be accessed by anyone
    
    return check_school_access(user, content_school_id)


def check_quiz_access(user: CurrentUser, quiz_school_id: int) -> bool:
    """Check if user can access quiz"""
    return check_school_access(user, quiz_school_id)


# Optional: Cache user data to reduce auth service calls
class UserCache:
    """Simple in-memory cache for user data"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from cache"""
        if user_id in self.cache:
            data, timestamp = self.cache[user_id]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[user_id]
        return None
    
    def set(self, user_id: int, data: Dict[str, Any]):
        """Set user data in cache"""
        self.cache[user_id] = (data, time.time())
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()


# Global user cache
user_cache = UserCache()


# Health check for auth service
async def check_auth_service_health() -> bool:
    """Check if auth service is healthy"""
    try:
        response = await auth_service.client.get(f"{AUTH_SERVICE_URL}/health")
        return response.status_code == 200
    except:
        return False


def verify_token(token: str) -> TokenData:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        school_id: int = payload.get("school_id")
        
        if user_id is None or email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(user_id=user_id, email=email, role=role, school_id=school_id)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Get current user from token"""
    token = credentials.credentials
    return verify_token(token)


def get_current_teacher(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Get current user and verify they are a teacher"""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    return current_user


def get_current_student(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Get current user and verify they are a student"""
    if current_user.role not in ["student", "teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user


def get_current_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Get current user and verify they are an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
