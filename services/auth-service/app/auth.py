"""
EduNerve Authentication Service - Authentication Utilities
JWT token creation, password hashing, and authentication helpers
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db
from app.models import User, UserRole
from app.schemas import TokenData

# Load environment variables
load_dotenv()

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()

# Authentication exceptions
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough permissions",
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify JWT token and extract user data
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        school_id: int = payload.get("school_id")
        role: str = payload.get("role")
        
        if email is None or user_id is None:
            raise credentials_exception
            
        token_data = TokenData(
            email=email,
            user_id=user_id,
            school_id=school_id,
            role=role
        )
        return token_data
    except JWTError:
        raise credentials_exception


def authenticate_user(db: Session, email: str, password: str, school_code: Optional[str] = None) -> Optional[User]:
    """
    Authenticate user with email and password
    """
    query = db.query(User).filter(User.email == email, User.is_active == True)
    
    # If school code is provided, filter by school
    if school_code:
        query = query.join(User.school).filter(User.school.has(code=school_code))
    
    user = query.first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    user = db.query(User).filter(
        User.id == token_data.user_id,
        User.is_active == True
    ).first()
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (additional check for account status)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: list[UserRole]):
    """
    Decorator factory to require specific user roles
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise permission_exception
        return current_user
    
    return role_checker


def require_same_school(current_user: User = Depends(get_current_active_user)):
    """
    Ensure user can only access resources from their own school
    """
    def school_checker(school_id: int) -> bool:
        if current_user.school_id != school_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: different school"
            )
        return True
    
    return school_checker


# Role-based dependencies
def get_current_admin_user(current_user: User = Depends(require_role([UserRole.ADMIN]))) -> User:
    """Get current admin user"""
    return current_user


def get_current_teacher_user(current_user: User = Depends(require_role([UserRole.TEACHER, UserRole.ADMIN]))) -> User:
    """Get current teacher or admin user"""
    return current_user


def get_current_student_user(current_user: User = Depends(require_role([UserRole.STUDENT]))) -> User:
    """Get current student user"""
    return current_user


def generate_verification_token(user_id: int) -> str:
    """
    Generate email/phone verification token
    """
    data = {
        "user_id": user_id,
        "purpose": "verification",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_verification_token(token: str) -> Optional[int]:
    """
    Verify email/phone verification token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        purpose: str = payload.get("purpose")
        
        if user_id is None or purpose != "verification":
            return None
            
        return user_id
    except JWTError:
        return None
