"""
Personalization Quiz API
Handles student learning preferences and recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..database import get_db
from ..models.content_models import PersonalizationQuiz, StudentPreferences
from ..schemas.personalization import (
    PersonalizationQuizCreate,
    PersonalizationQuizResponse,
    StudentPreferencesCreate,
    StudentPreferencesResponse,
    LearningRecommendation,
    RecommendationRequest
)
from ..auth import get_current_student_user, CurrentUser
from ..services.personalization_service import PersonalizationService

router = APIRouter(prefix="/api/v1/personalization", tags=["Personalization"])
logger = logging.getLogger(__name__)

personalization_service = PersonalizationService()

@router.post("/quiz", response_model=PersonalizationQuizResponse)
async def create_personalization_quiz(
    quiz_data: PersonalizationQuizCreate,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Create a new personalization quiz for a student"""
    try:
        quiz = await personalization_service.create_quiz(
            quiz_data=quiz_data,
            current_user=current_user,
            db=db
        )
        return PersonalizationQuizResponse.from_orm(quiz)
    except Exception as e:
        logger.error(f"Error creating personalization quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create personalization quiz"
        )

@router.get("/quiz/{quiz_id}", response_model=PersonalizationQuizResponse)
async def get_personalization_quiz(
    quiz_id: int,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get a specific personalization quiz"""
    try:
        quiz = await personalization_service.get_quiz(
            quiz_id=quiz_id,
            current_user=current_user,
            db=db
        )
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personalization quiz not found"
            )
        return PersonalizationQuizResponse.from_orm(quiz)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting personalization quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get personalization quiz"
        )

@router.post("/preferences", response_model=StudentPreferencesResponse)
async def save_student_preferences(
    preferences: StudentPreferencesCreate,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Save student learning preferences"""
    try:
        saved_preferences = await personalization_service.save_preferences(
            preferences=preferences,
            current_user=current_user,
            db=db
        )
        return StudentPreferencesResponse.from_orm(saved_preferences)
    except Exception as e:
        logger.error(f"Error saving student preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save student preferences"
        )

@router.get("/preferences", response_model=StudentPreferencesResponse)
async def get_student_preferences(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get current student preferences"""
    try:
        preferences = await personalization_service.get_preferences(
            current_user=current_user,
            db=db
        )
        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student preferences not found"
            )
        return StudentPreferencesResponse.from_orm(preferences)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get student preferences"
        )

@router.post("/recommendations", response_model=List[LearningRecommendation])
async def get_learning_recommendations(
    request: RecommendationRequest,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get personalized learning recommendations"""
    try:
        recommendations = await personalization_service.get_recommendations(
            request=request,
            current_user=current_user,
            db=db
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get learning recommendations"
        )

@router.get("/learning-style", response_model=dict)
async def get_learning_style_analysis(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get student's learning style analysis"""
    try:
        analysis = await personalization_service.analyze_learning_style(
            current_user=current_user,
            db=db
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing learning style: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze learning style"
        )

@router.get("/weak-areas", response_model=List[dict])
async def get_weak_areas(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get student's weak areas based on quiz performance"""
    try:
        weak_areas = await personalization_service.identify_weak_areas(
            current_user=current_user,
            db=db
        )
        return weak_areas
    except Exception as e:
        logger.error(f"Error identifying weak areas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to identify weak areas"
        )
