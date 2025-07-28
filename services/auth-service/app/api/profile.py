"""
User Profile and Settings API Endpoints
Complete user profile management, settings, and personalization
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from ..database import get_db
from ..models.user_models import (
    User, UserProfile, UserSettings, UserStats, UserActivity, 
    UserAchievement
)
from ..api.auth import verify_token, security
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(prefix="/profile", tags=["user-profile"])

# Pydantic models
class ProfileResponse(BaseModel):
    id: int
    user_id: int
    avatar_url: Optional[str]
    bio: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    country: Optional[str]
    city: Optional[str]
    school: Optional[str]
    grade_level: Optional[str]
    subjects_of_interest: Optional[List[str]]
    learning_style: Optional[str]
    study_goals: Optional[List[str]]
    quiz_completed: bool
    quiz_results: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    social_links: Optional[Dict[str, str]]

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=1000)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    school: Optional[str] = None
    grade_level: Optional[str] = None
    subjects_of_interest: Optional[List[str]] = None
    learning_style: Optional[str] = None
    study_goals: Optional[List[str]] = None
    social_links: Optional[Dict[str, str]] = None

class SettingsResponse(BaseModel):
    id: int
    user_id: int
    profile_visibility: str
    show_activity_status: bool
    show_email: bool
    show_phone: bool
    email_notifications: bool
    sms_notifications: bool
    push_notifications: bool
    notification_frequency: str
    default_study_duration: int
    default_break_duration: int
    sound_enabled: bool
    theme: str
    language: str
    difficulty_level: str
    content_type_preference: Optional[List[str]]
    auto_play_videos: bool

class SettingsUpdateRequest(BaseModel):
    profile_visibility: Optional[str] = None
    show_activity_status: Optional[bool] = None
    show_email: Optional[bool] = None
    show_phone: Optional[bool] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    notification_frequency: Optional[str] = None
    default_study_duration: Optional[int] = Field(None, ge=5, le=120)
    default_break_duration: Optional[int] = Field(None, ge=1, le=30)
    sound_enabled: Optional[bool] = None
    theme: Optional[str] = None
    language: Optional[str] = None
    difficulty_level: Optional[str] = None
    content_type_preference: Optional[List[str]] = None
    auto_play_videos: Optional[bool] = None

class UserStatsResponse(BaseModel):
    id: int
    user_id: int
    total_study_time: float
    study_streak: int
    longest_streak: int
    sessions_completed: int
    quizzes_taken: int
    quizzes_passed: int
    average_score: float
    total_points_earned: int
    courses_enrolled: int
    courses_completed: int
    lessons_completed: int
    assignments_submitted: int
    login_count: int
    last_activity_date: Optional[datetime]
    active_days_count: int

class PersonalizationQuizRequest(BaseModel):
    responses: Dict[str, Any]
    learning_style_results: Dict[str, Any]
    interests: List[str]
    goals: List[str]
    difficulty_preference: str

class AchievementResponse(BaseModel):
    id: int
    achievement_id: str
    title: str
    description: str
    icon: str
    category: str
    is_earned: bool
    earned_at: Optional[datetime]
    points_awarded: int
    current_progress: float
    criteria_value: float

# Profile endpoints
@router.get("/", response_model=ProfileResponse)
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    user = await verify_token(credentials.credentials, db)
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        # Create default profile if not exists
        profile = UserProfile(
            user_id=user.id,
            created_at=datetime.utcnow()
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender,
        country=profile.country,
        city=profile.city,
        school=profile.school,
        grade_level=profile.grade_level,
        subjects_of_interest=profile.subjects_of_interest or [],
        learning_style=profile.learning_style,
        study_goals=profile.study_goals or [],
        quiz_completed=profile.quiz_completed,
        quiz_results=profile.quiz_results,
        recommendations=profile.recommendations,
        social_links=profile.social_links or {}
    )

@router.put("/", response_model=ProfileResponse)
async def update_user_profile(
    profile_data: ProfileUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    user = await verify_token(credentials.credentials, db)
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id, created_at=datetime.utcnow())
        db.add(profile)
    
    # Update profile fields
    update_data = profile_data.dict(exclude_unset=True)
    
    # Update user's full name if provided
    if "full_name" in update_data:
        user.full_name = update_data.pop("full_name")
        # Split name
        name_parts = user.full_name.split(" ", 1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    # Update profile fields
    for field, value in update_data.items():
        if hasattr(profile, field):
            setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    
    # Log activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="profile_update",
        activity_title="Profile updated",
        activity_description="User updated profile information",
        metadata={"updated_fields": list(update_data.keys())},
        created_at=datetime.utcnow()
    )
    db.add(activity)
    
    db.commit()
    db.refresh(profile)
    
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender,
        country=profile.country,
        city=profile.city,
        school=profile.school,
        grade_level=profile.grade_level,
        subjects_of_interest=profile.subjects_of_interest or [],
        learning_style=profile.learning_style,
        study_goals=profile.study_goals or [],
        quiz_completed=profile.quiz_completed,
        quiz_results=profile.quiz_results,
        recommendations=profile.recommendations,
        social_links=profile.social_links or {}
    )

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Upload user avatar"""
    user = await verify_token(credentials.credentials, db)
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # In production, upload to cloud storage (S3, etc.)
    # For now, simulate upload
    avatar_url = f"/uploads/avatars/{user.id}_{file.filename}"
    
    # Update profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id, created_at=datetime.utcnow())
        db.add(profile)
    
    profile.avatar_url = avatar_url
    profile.updated_at = datetime.utcnow()
    
    # Log activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="avatar_upload",
        activity_title="Avatar uploaded",
        activity_description="User uploaded new avatar",
        metadata={"filename": file.filename, "avatar_url": avatar_url},
        created_at=datetime.utcnow()
    )
    db.add(activity)
    
    db.commit()
    
    return {"avatar_url": avatar_url, "message": "Avatar uploaded successfully"}

# Settings endpoints
@router.get("/settings", response_model=SettingsResponse)
async def get_user_settings(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user settings"""
    user = await verify_token(credentials.credentials, db)
    
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        # Create default settings
        settings = UserSettings(
            user_id=user.id,
            created_at=datetime.utcnow()
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return SettingsResponse(
        id=settings.id,
        user_id=settings.user_id,
        profile_visibility=settings.profile_visibility,
        show_activity_status=settings.show_activity_status,
        show_email=settings.show_email,
        show_phone=settings.show_phone,
        email_notifications=settings.email_notifications,
        sms_notifications=settings.sms_notifications,
        push_notifications=settings.push_notifications,
        notification_frequency=settings.notification_frequency,
        default_study_duration=settings.default_study_duration,
        default_break_duration=settings.default_break_duration,
        sound_enabled=settings.sound_enabled,
        theme=settings.theme,
        language=settings.language,
        difficulty_level=settings.difficulty_level,
        content_type_preference=settings.content_type_preference or [],
        auto_play_videos=settings.auto_play_videos
    )

@router.put("/settings", response_model=SettingsResponse)
async def update_user_settings(
    settings_data: SettingsUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update user settings"""
    user = await verify_token(credentials.credentials, db)
    
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        settings = UserSettings(user_id=user.id, created_at=datetime.utcnow())
        db.add(settings)
    
    # Update settings
    update_data = settings_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(settings, field):
            setattr(settings, field, value)
    
    settings.updated_at = datetime.utcnow()
    
    # Log activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="settings_update",
        activity_title="Settings updated",
        activity_description="User updated account settings",
        metadata={"updated_fields": list(update_data.keys())},
        created_at=datetime.utcnow()
    )
    db.add(activity)
    
    db.commit()
    db.refresh(settings)
    
    return SettingsResponse(
        id=settings.id,
        user_id=settings.user_id,
        profile_visibility=settings.profile_visibility,
        show_activity_status=settings.show_activity_status,
        show_email=settings.show_email,
        show_phone=settings.show_phone,
        email_notifications=settings.email_notifications,
        sms_notifications=settings.sms_notifications,
        push_notifications=settings.push_notifications,
        notification_frequency=settings.notification_frequency,
        default_study_duration=settings.default_study_duration,
        default_break_duration=settings.default_break_duration,
        sound_enabled=settings.sound_enabled,
        theme=settings.theme,
        language=settings.language,
        difficulty_level=settings.difficulty_level,
        content_type_preference=settings.content_type_preference or [],
        auto_play_videos=settings.auto_play_videos
    )

# Stats and achievements endpoints
@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    user = await verify_token(credentials.credentials, db)
    
    stats = db.query(UserStats).filter(UserStats.user_id == user.id).first()
    if not stats:
        stats = UserStats(user_id=user.id, created_at=datetime.utcnow())
        db.add(stats)
        db.commit()
        db.refresh(stats)
    
    return UserStatsResponse(
        id=stats.id,
        user_id=stats.user_id,
        total_study_time=stats.total_study_time,
        study_streak=stats.study_streak,
        longest_streak=stats.longest_streak,
        sessions_completed=stats.sessions_completed,
        quizzes_taken=stats.quizzes_taken,
        quizzes_passed=stats.quizzes_passed,
        average_score=stats.average_score,
        total_points_earned=stats.total_points_earned,
        courses_enrolled=stats.courses_enrolled,
        courses_completed=stats.courses_completed,
        lessons_completed=stats.lessons_completed,
        assignments_submitted=stats.assignments_submitted,
        login_count=stats.login_count,
        last_activity_date=stats.last_activity_date,
        active_days_count=stats.active_days_count
    )

@router.get("/achievements", response_model=List[AchievementResponse])
async def get_user_achievements(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user achievements"""
    user = await verify_token(credentials.credentials, db)
    
    achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == user.id
    ).all()
    
    return [
        AchievementResponse(
            id=achievement.id,
            achievement_id=achievement.achievement_id,
            title=achievement.title,
            description=achievement.description,
            icon=achievement.icon,
            category=achievement.category,
            is_earned=achievement.is_earned,
            earned_at=achievement.earned_at,
            points_awarded=achievement.points_awarded,
            current_progress=achievement.current_progress,
            criteria_value=achievement.criteria_value
        )
        for achievement in achievements
    ]

@router.post("/personalization-quiz")
async def complete_personalization_quiz(
    quiz_data: PersonalizationQuizRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Complete personalization quiz"""
    user = await verify_token(credentials.credentials, db)
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id, created_at=datetime.utcnow())
        db.add(profile)
    
    # Store quiz results
    profile.quiz_completed = True
    profile.quiz_results = quiz_data.responses
    profile.learning_style = quiz_data.learning_style_results.get("primary_style")
    profile.subjects_of_interest = quiz_data.interests
    profile.study_goals = quiz_data.goals
    profile.updated_at = datetime.utcnow()
    
    # Generate personalized recommendations
    recommendations = generate_recommendations(quiz_data)
    profile.recommendations = recommendations
    
    # Log activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="personalization_quiz",
        activity_title="Personalization quiz completed",
        activity_description="User completed personalization quiz",
        metadata={"learning_style": quiz_data.learning_style_results.get("primary_style")},
        created_at=datetime.utcnow()
    )
    db.add(activity)
    
    db.commit()
    
    return {
        "message": "Personalization quiz completed successfully",
        "recommendations": recommendations
    }

def generate_recommendations(quiz_data: PersonalizationQuizRequest) -> Dict[str, Any]:
    """Generate personalized recommendations based on quiz results"""
    # This would be more sophisticated in production
    return {
        "study_schedule": {
            "sessions_per_day": 3 if quiz_data.difficulty_preference == "intensive" else 2,
            "session_duration": 45 if quiz_data.difficulty_preference == "intensive" else 25,
            "break_duration": 10 if quiz_data.difficulty_preference == "intensive" else 5
        },
        "content_types": quiz_data.learning_style_results.get("recommended_content", []),
        "subject_focus": quiz_data.interests[:3],  # Top 3 interests
        "learning_path": f"Personalized path for {quiz_data.learning_style_results.get('primary_style', 'balanced')} learner"
    }
