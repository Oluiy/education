"""
EduNerve Enhanced Authentication System
Secure JWT token management with proper validation and error handling
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import jwt
import time
import hashlib
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, UserRole
from app.security_config import get_jwt_config
from app.schemas import TokenData

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)  # Don't auto-error, we'll handle it

# JWT configuration
jwt_config = get_jwt_config()
SECRET_KEY = jwt_config["secret_key"]
ALGORITHM = jwt_config["algorithm"]
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_config["access_token_expire_minutes"]

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token with enhanced security
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add security claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": hashlib.sha256(f"{data.get('sub')}{time.time()}".encode()).hexdigest()[:16],  # JWT ID
        "iss": "edunerve-auth",  # Issuer
        "aud": "edunerve-services"  # Audience
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info(f"🔑 Token created for user: {data.get('sub')}")
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """
    Verify JWT token with enhanced validation
    """
    try:
        # Decode with full validation
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            audience="edunerve-services",
            issuer="edunerve-auth"
        )
        
        # Extract claims
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        school_id: int = payload.get("school_id")
        role: str = payload.get("role")
        jti: str = payload.get("jti")
        
        # Validate required claims
        if not all([email, user_id, role]):
            logger.warning(f"🚨 Token missing required claims: {payload}")
            raise AuthenticationError("Invalid token: missing claims")
        
        # Additional security checks
        issued_at = payload.get("iat")
        if issued_at and datetime.utcnow().timestamp() - issued_at > 86400:  # 24 hours
            logger.warning(f"🚨 Very old token used: {email}")
        
        token_data = TokenData(
            email=email,
            user_id=user_id,
            school_id=school_id,
            role=role,
            jti=jti
        )
        
        return token_data
        
    except jwt.ExpiredSignatureError:
        logger.warning("🚨 Expired token used")
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"🚨 Invalid token: {str(e)}")
        raise AuthenticationError("Invalid token")
    except Exception as e:
        logger.error(f"🚨 Token verification error: {str(e)}")
        raise AuthenticationError("Token verification failed")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user with proper error handling
    """
    # Check if credentials are provided
    if not credentials:
        logger.warning("🚨 No credentials provided")
        raise AuthenticationError("Authentication credentials required")
    
    # Verify token
    try:
        token_data = verify_token(credentials.credentials)
    except AuthenticationError:
        raise  # Re-raise authentication errors
    except Exception as e:
        logger.error(f"🚨 Unexpected auth error: {str(e)}")
        raise AuthenticationError("Authentication failed")
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        logger.warning(f"🚨 User not found: {token_data.user_id}")
        raise AuthenticationError("User not found")
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"🚨 Inactive user attempted access: {user.email}")
        raise AuthenticationError("Account is inactive")
    
    # Verify token data matches user
    if user.email != token_data.email:
        logger.warning(f"🚨 Token/user email mismatch: {token_data.email} != {user.email}")
        raise AuthenticationError("Invalid token")
    
    # Update last activity
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info(f"✅ User authenticated: {user.email}")
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user with additional checks
    """
    if not current_user.is_active:
        raise AuthenticationError("Account is inactive")
    
    if not current_user.is_verified:
        raise AuthenticationError("Account is not verified")
    
    return current_user

def require_role(allowed_roles: list[UserRole]):
    """
    Decorator factory to require specific user roles
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            logger.warning(f"🚨 Role access denied: {current_user.email} ({current_user.role}) tried to access {allowed_roles}")
            raise AuthorizationError(f"Role {current_user.role.value} not authorized")
        return current_user
    
    return role_checker

def require_same_school(target_school_id: int):
    """
    Ensure user can only access resources from their own school
    """
    def school_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.school_id != target_school_id:
            logger.warning(f"🚨 Cross-school access attempt: {current_user.email} tried to access school {target_school_id}")
            raise AuthorizationError("Access denied: different school")
        return current_user
    
    return school_checker

# Role-based dependencies with proper error handling
async def get_current_admin_user(current_user: User = Depends(require_role([UserRole.ADMIN]))) -> User:
    """Get current admin user"""
    return current_user

async def get_current_teacher_user(current_user: User = Depends(require_role([UserRole.TEACHER, UserRole.ADMIN]))) -> User:
    """Get current teacher or admin user"""
    return current_user

async def get_current_student_user(current_user: User = Depends(require_role([UserRole.STUDENT]))) -> User:
    """Get current student user"""
    return current_user

# Optional authentication for public endpoints
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise (for public endpoints)
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except AuthenticationError:
        return None
    except Exception as e:
        logger.error(f"🚨 Optional auth error: {str(e)}")
        return None
