"""
Smart Assistant API
Handles AI-powered learning recommendations and chat
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..database import get_db
from ..models.assistant_models import AssistantChat, LearningResource
from ..schemas.assistant import (
    ChatMessageCreate,
    ChatMessageResponse,
    LearningResourceResponse,
    RecommendationRequest,
    RecommendationResponse,
    AssistantChatCreate,
    AssistantChatResponse
)
from ..auth import get_current_user, CurrentUser
from ..services.assistant_service import AssistantService

router = APIRouter(prefix="/api/v1/assistant", tags=["Smart Assistant"])
logger = logging.getLogger(__name__)

assistant_service = AssistantService()

@router.post("/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    message: ChatMessageCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the AI assistant"""
    try:
        response = await assistant_service.process_chat_message(
            message=message,
            current_user=current_user,
            db=db
        )
        return ChatMessageResponse.from_orm(response)
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/chat/history", response_model=List[ChatMessageResponse])
async def get_chat_history(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get chat history for the user"""
    try:
        messages = await assistant_service.get_chat_history(
            current_user=current_user,
            db=db,
            limit=limit,
            offset=offset
        )
        return [ChatMessageResponse.from_orm(msg) for msg in messages]
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat history"
        )

@router.post("/recommend", response_model=List[RecommendationResponse])
async def get_learning_recommendations(
    request: RecommendationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered learning recommendations"""
    try:
        recommendations = await assistant_service.get_recommendations(
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

@router.get("/resources", response_model=List[LearningResourceResponse])
async def get_learning_resources(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    resource_type: Optional[str] = None
):
    """Get curated learning resources"""
    try:
        resources = await assistant_service.get_learning_resources(
            current_user=current_user,
            db=db,
            subject=subject,
            topic=topic,
            resource_type=resource_type
        )
        return [LearningResourceResponse.from_orm(resource) for resource in resources]
    except Exception as e:
        logger.error(f"Error getting learning resources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get learning resources"
        )

@router.post("/resources/youtube", response_model=List[dict])
async def get_youtube_recommendations(
    subject: str,
    topic: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get YouTube video recommendations"""
    try:
        videos = await assistant_service.get_youtube_recommendations(
            subject=subject,
            topic=topic,
            current_user=current_user,
            db=db
        )
        return videos
    except Exception as e:
        logger.error(f"Error getting YouTube recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get YouTube recommendations"
        )

@router.post("/resources/audio", response_model=List[dict])
async def get_audio_summaries(
    content_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate audio summaries for content"""
    try:
        summaries = await assistant_service.generate_audio_summaries(
            content_id=content_id,
            current_user=current_user,
            db=db
        )
        return summaries
    except Exception as e:
        logger.error(f"Error generating audio summaries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate audio summaries"
        )

@router.post("/quiz/generate", response_model=dict)
async def generate_practice_quiz(
    subject: str,
    topic: str,
    difficulty: str = "medium",
    num_questions: int = 10,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a practice quiz based on weak areas"""
    try:
        quiz = await assistant_service.generate_practice_quiz(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            current_user=current_user,
            db=db
        )
        return quiz
    except Exception as e:
        logger.error(f"Error generating practice quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate practice quiz"
        )

@router.get("/progress/analysis", response_model=dict)
async def get_progress_analysis(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI analysis of student progress"""
    try:
        analysis = await assistant_service.analyze_progress(
            current_user=current_user,
            db=db
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing progress: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze progress"
        )

@router.get("/weak-areas", response_model=List[dict])
async def get_weak_areas(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-identified weak areas"""
    try:
        weak_areas = await assistant_service.identify_weak_areas(
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

@router.post("/study-plan", response_model=dict)
async def generate_study_plan(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate personalized study plan"""
    try:
        study_plan = await assistant_service.generate_study_plan(
            current_user=current_user,
            db=db
        )
        return study_plan
    except Exception as e:
        logger.error(f"Error generating study plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate study plan"
        )

@router.get("/concept-explanation", response_model=dict)
async def get_concept_explanation(
    concept: str,
    subject: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI explanation of a concept"""
    try:
        explanation = await assistant_service.explain_concept(
            concept=concept,
            subject=subject,
            current_user=current_user,
            db=db
        )
        return explanation
    except Exception as e:
        logger.error(f"Error explaining concept: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to explain concept"
        )

@router.post("/feedback", response_model=dict)
async def provide_feedback(
    message_id: int,
    feedback_type: str,  # helpful, not_helpful, incorrect
    feedback_text: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Provide feedback on assistant responses"""
    try:
        result = await assistant_service.save_feedback(
            message_id=message_id,
            feedback_type=feedback_type,
            feedback_text=feedback_text,
            current_user=current_user,
            db=db
        )
        return result
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save feedback"
        )
