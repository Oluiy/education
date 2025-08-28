"""
Study Timer API
Handles study session tracking and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from ..database import get_db
from ..models.content_models import StudySession, StudyTimer
from ..schemas.study_timer import (
    StudySessionCreate,
    StudySessionResponse,
    StudyTimerCreate,
    StudyTimerResponse,
    StudyStats,
    StudySessionUpdate
)
from ..auth import get_current_student_user, CurrentUser
from ..services.study_timer_service import StudyTimerService

router = APIRouter(prefix="/api/v1/study-timer", tags=["Study Timer"])
logger = logging.getLogger(__name__)

study_timer_service = StudyTimerService()

@router.post("/start", response_model=StudySessionResponse)
async def start_study_session(
    session_data: StudySessionCreate,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Start a new study session"""
    try:
        session = await study_timer_service.start_session(
            session_data=session_data,
            current_user=current_user,
            db=db
        )
        return StudySessionResponse.from_orm(session)
    except Exception as e:
        logger.error(f"Error starting study session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start study session"
        )

@router.post("/pause/{session_id}", response_model=StudySessionResponse)
async def pause_study_session(
    session_id: int,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Pause an active study session"""
    try:
        session = await study_timer_service.pause_session(
            session_id=session_id,
            current_user=current_user,
            db=db
        )
        return StudySessionResponse.from_orm(session)
    except Exception as e:
        logger.error(f"Error pausing study session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause study session"
        )

@router.post("/resume/{session_id}", response_model=StudySessionResponse)
async def resume_study_session(
    session_id: int,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Resume a paused study session"""
    try:
        session = await study_timer_service.resume_session(
            session_id=session_id,
            current_user=current_user,
            db=db
        )
        return StudySessionResponse.from_orm(session)
    except Exception as e:
        logger.error(f"Error resuming study session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume study session"
        )

@router.post("/complete/{session_id}", response_model=StudySessionResponse)
async def complete_study_session(
    session_id: int,
    session_update: StudySessionUpdate,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Complete a study session"""
    try:
        session = await study_timer_service.complete_session(
            session_id=session_id,
            session_update=session_update,
            current_user=current_user,
            db=db
        )
        return StudySessionResponse.from_orm(session)
    except Exception as e:
        logger.error(f"Error completing study session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete study session"
        )

@router.get("/sessions", response_model=List[StudySessionResponse])
async def get_study_sessions(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """Get user's study sessions"""
    try:
        sessions = await study_timer_service.get_sessions(
            current_user=current_user,
            db=db,
            limit=limit,
            offset=offset
        )
        return [StudySessionResponse.from_orm(session) for session in sessions]
    except Exception as e:
        logger.error(f"Error getting study sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get study sessions"
        )

@router.get("/sessions/{session_id}", response_model=StudySessionResponse)
async def get_study_session(
    session_id: int,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get a specific study session"""
    try:
        session = await study_timer_service.get_session(
            session_id=session_id,
            current_user=current_user,
            db=db
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study session not found"
            )
        return StudySessionResponse.from_orm(session)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting study session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get study session"
        )

@router.get("/stats", response_model=StudyStats)
async def get_study_stats(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db),
    period: str = "week"  # day, week, month, year
):
    """Get study statistics for the user"""
    try:
        stats = await study_timer_service.get_stats(
            current_user=current_user,
            db=db,
            period=period
        )
        return stats
    except Exception as e:
        logger.error(f"Error getting study stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get study statistics"
        )

@router.get("/active", response_model=StudySessionResponse)
async def get_active_session(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get user's currently active study session"""
    try:
        session = await study_timer_service.get_active_session(
            current_user=current_user,
            db=db
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active study session found"
            )
        return StudySessionResponse.from_orm(session)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get active study session"
        )

@router.post("/timer", response_model=StudyTimerResponse)
async def create_study_timer(
    timer_data: StudyTimerCreate,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Create a new study timer"""
    try:
        timer = await study_timer_service.create_timer(
            timer_data=timer_data,
            current_user=current_user,
            db=db
        )
        return StudyTimerResponse.from_orm(timer)
    except Exception as e:
        logger.error(f"Error creating study timer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create study timer"
        )

@router.get("/timers", response_model=List[StudyTimerResponse])
async def get_study_timers(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get user's study timers"""
    try:
        timers = await study_timer_service.get_timers(
            current_user=current_user,
            db=db
        )
        return [StudyTimerResponse.from_orm(timer) for timer in timers]
    except Exception as e:
        logger.error(f"Error getting study timers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get study timers"
        )

@router.get("/productivity-score", response_model=dict)
async def get_productivity_score(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get user's study productivity score"""
    try:
        score = await study_timer_service.calculate_productivity_score(
            current_user=current_user,
            db=db
        )
        return {"productivity_score": score}
    except Exception as e:
        logger.error(f"Error calculating productivity score: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate productivity score"
        )
