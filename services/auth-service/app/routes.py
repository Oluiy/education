"""
EduNerve Authentication Service - API Routes
Authentication endpoints for registration, login, and user management
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_db
from app.models import User, School, UserRole
from app.schemas import (
    UserCreate, UserResponse, UserLogin, UserLoginResponse, UserUpdate,
    SchoolCreate, SchoolResponse, MessageResponse, ErrorResponse,
    PasswordReset, PasswordResetConfirm, TokenData
)
from app.auth import (
    authenticate_user, create_access_token, get_password_hash,
    get_current_user, get_current_active_user, get_current_admin_user,
    get_current_teacher_user, require_role, ACCESS_TOKEN_EXPIRE_MINUTES,
    generate_verification_token, verify_verification_token
)

# Create router
router = APIRouter()

# Exception handlers
user_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)

school_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="School not found"
)

email_already_exists = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already registered"
)

invalid_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password"
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user (Student, Teacher, or Admin)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise email_already_exists
    
    # Verify school exists
    school = db.query(School).filter(School.id == user.school_id).first()
    if not school:
        raise school_not_found
    
    # Check if school is active
    if not school.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="School is not active"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        role=user.role,
        school_id=user.school_id,
        class_level=user.class_level,
        student_id=user.student_id,
        employee_id=user.employee_id,
        subjects=user.subjects
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=UserLoginResponse)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token
    """
    # Authenticate user
    user = authenticate_user(
        db=db,
        email=user_credentials.email,
        password=user_credentials.password,
        school_code=user_credentials.school_code
    )
    
    if not user:
        raise invalid_credentials
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "school_id": user.school_id,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=user
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (same school only)
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.school_id == current_user.school_id
    ).first()
    
    if not user:
        raise user_not_found
    
    return user


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    class_level: Optional[str] = None,
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get users from the same school (Teachers and Admins only)
    """
    query = db.query(User).filter(User.school_id == current_user.school_id)
    
    # Filter by role if provided
    if role:
        query = query.filter(User.role == role)
    
    # Filter by class level if provided
    if class_level:
        query = query.filter(User.class_level == class_level)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/students", response_model=List[UserResponse])
async def get_students(
    skip: int = 0,
    limit: int = 100,
    class_level: Optional[str] = None,
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get students from the same school (Teachers and Admins only)
    """
    query = db.query(User).filter(
        User.school_id == current_user.school_id,
        User.role == UserRole.STUDENT
    )
    
    # Filter by class level if provided
    if class_level:
        query = query.filter(User.class_level == class_level)
    
    students = query.offset(skip).limit(limit).all()
    return students


@router.get("/teachers", response_model=List[UserResponse])
async def get_teachers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get teachers from the same school (Admins only)
    """
    teachers = db.query(User).filter(
        User.school_id == current_user.school_id,
        User.role == UserRole.TEACHER
    ).offset(skip).limit(limit).all()
    
    return teachers


@router.post("/schools", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    school: SchoolCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new school (For system setup only)
    """
    # Check if school code already exists
    existing_school = db.query(School).filter(School.code == school.code).first()
    if existing_school:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="School code already exists"
        )
    
    # Create new school
    db_school = School(
        name=school.name,
        code=school.code,
        address=school.address,
        phone=school.phone,
        email=school.email,
        principal_name=school.principal_name
    )
    
    db.add(db_school)
    db.commit()
    db.refresh(db_school)
    
    return db_school


@router.get("/schools", response_model=List[SchoolResponse])
async def get_schools(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all schools (For system overview)
    """
    schools = db.query(School).offset(skip).limit(limit).all()
    return schools


@router.get("/schools/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: int,
    db: Session = Depends(get_db)
):
    """
    Get school by ID
    """
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise school_not_found
    
    return school


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete/deactivate user (Admins only, same school)
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.school_id == current_user.school_id
    ).first()
    
    if not user:
        raise user_not_found
    
    # Don't allow admin to delete themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Soft delete by deactivating user
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="User deactivated successfully")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify user email address
    """
    user_id = verify_verification_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise user_not_found
    
    user.email_verified = True
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    current_user: User = Depends(get_current_active_user)
):
    """
    Resend email verification token
    """
    if current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new verification token
    token = generate_verification_token(current_user.id)
    
    # TODO: Send email with verification link
    # For now, just return the token (in production, send via email)
    
    return MessageResponse(
        message=f"Verification email sent. Token: {token}"
    )


# Health check endpoint
@router.get("/health", response_model=MessageResponse)
async def health_check():
    """
    Health check endpoint
    """
    return MessageResponse(message="EduNerve Auth Service is running")


# Stats endpoint for admins
@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get school statistics (Admins only)
    """
    school_id = current_user.school_id
    
    # Count users by role
    total_students = db.query(User).filter(
        User.school_id == school_id,
        User.role == UserRole.STUDENT,
        User.is_active == True
    ).count()
    
    total_teachers = db.query(User).filter(
        User.school_id == school_id,
        User.role == UserRole.TEACHER,
        User.is_active == True
    ).count()
    
    total_admins = db.query(User).filter(
        User.school_id == school_id,
        User.role == UserRole.ADMIN,
        User.is_active == True
    ).count()
    
    # Count by class level
    class_counts = {}
    for class_level in ['JSS1', 'JSS2', 'JSS3', 'SS1', 'SS2', 'SS3']:
        count = db.query(User).filter(
            User.school_id == school_id,
            User.class_level == class_level,
            User.is_active == True
        ).count()
        class_counts[class_level] = count
    
    return {
        "school_id": school_id,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_admins": total_admins,
        "class_distribution": class_counts,
        "total_users": total_students + total_teachers + total_admins
    }
