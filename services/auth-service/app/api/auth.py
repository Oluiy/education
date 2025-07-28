"""
Authentication API Endpoints for EduNerve Platform
Complete authentication system with user management, profiles, and security
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import bcrypt
import secrets
import redis
from pydantic import BaseModel, EmailStr, Field
from ..database import get_db
from ..models.user_models import (
    User, UserProfile, UserSettings, UserStats, UserActivity, 
    UserAchievement, EmailVerification, PasswordReset, AuthSession
)
from ..core.security import create_access_token, verify_password, hash_password
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

# Pydantic models for request/response
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = "student"

class UserLogin(BaseModel):
    username_or_email: str
    password: str
    remember_me: bool = False

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    school: Optional[str] = None
    grade_level: Optional[str] = None
    subjects_of_interest: Optional[List[str]] = None

class UserSettingsRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    default_study_duration: Optional[int] = None

# Authentication endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            created_at=datetime.utcnow()
        )
        
        # Split full name
        name_parts = user_data.full_name.split(" ", 1)
        new_user.first_name = name_parts[0]
        new_user.last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        db.add(new_user)
        db.flush()  # Get the user ID
        
        # Create default profile
        profile = UserProfile(
            user_id=new_user.id,
            created_at=datetime.utcnow()
        )
        db.add(profile)
        
        # Create default settings
        settings_obj = UserSettings(
            user_id=new_user.id,
            created_at=datetime.utcnow()
        )
        db.add(settings_obj)
        
        # Create stats record
        stats = UserStats(
            user_id=new_user.id,
            created_at=datetime.utcnow()
        )
        db.add(stats)
        
        # Log registration activity
        activity = UserActivity(
            user_id=new_user.id,
            activity_type="user_registration",
            activity_title="User registered",
            activity_description=f"New user {user_data.username} registered",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            created_at=datetime.utcnow()
        )
        db.add(activity)
        
        db.commit()
        
        # Send verification email (background task)
        background_tasks.add_task(send_verification_email, new_user.email, new_user.id, db)
        
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            created_at=new_user.created_at,
            last_login=new_user.last_login
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == user_data.username_or_email) | 
        (User.email == user_data.username_or_email)
    ).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create tokens
    access_token_expires = timedelta(hours=24 if user_data.remember_me else 1)
    refresh_token_expires = timedelta(days=30 if user_data.remember_me else 7)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    # Create session record
    session_token_id = secrets.token_urlsafe(32)
    auth_session = AuthSession(
        user_id=user.id,
        token_id=session_token_id,
        refresh_token=refresh_token,
        device_info={
            "user_agent": request.headers.get("user-agent", ""),
            "platform": "web"
        },
        ip_address=request.client.host,
        expires_at=datetime.utcnow() + refresh_token_expires,
        created_at=datetime.utcnow()
    )
    db.add(auth_session)
    
    # Update user last login
    user.last_login = datetime.utcnow()
    
    # Update stats
    stats = db.query(UserStats).filter(UserStats.user_id == user.id).first()
    if stats:
        stats.login_count += 1
        stats.last_activity_date = datetime.utcnow()
    
    # Log login activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="user_login",
        activity_title="User logged in",
        activity_description=f"User {user.username} logged in",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        success=True,
        created_at=datetime.utcnow()
    )
    db.add(activity)
    
    db.commit()
    
    # Cache user session in Redis
    redis_client.setex(
        f"session:{session_token_id}",
        int(refresh_token_expires.total_seconds()),
        str(user.id)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(access_token_expires.total_seconds()),
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login
        )
    )

@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout user and invalidate tokens"""
    try:
        # Decode token to get user info
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        
        # Find and deactivate session
        session = db.query(AuthSession).filter(
            AuthSession.user_id == user_id,
            AuthSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            # Remove from Redis cache
            redis_client.delete(f"session:{session.token_id}")
        
        # Log logout activity
        activity = UserActivity(
            user_id=user_id,
            activity_type="user_logout",
            activity_title="User logged out",
            activity_description="User logged out",
            success=True,
            created_at=datetime.utcnow()
        )
        db.add(activity)
        
        db.commit()
        
        return {"message": "Successfully logged out"}
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    user = await verify_token(credentials.credentials, db)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login
    )

# Helper functions
async def verify_token(token: str, db: Session) -> User:
    """Verify JWT token and return user"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def send_verification_email(email: str, user_id: int, db: Session):
    """Send email verification (background task)"""
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    verification = EmailVerification(
        user_id=user_id,
        email=email,
        token=verification_token,
        expires_at=expires_at,
        created_at=datetime.utcnow()
    )
    db.add(verification)
    db.commit()
    
    # Here you would send the actual email
    # For now, just log it
    print(f"Verification email sent to {email} with token {verification_token}")

# Include this router in the main auth service app
