"""
Study Session API Endpoints
REST API for study session management, timer, analytics, and badges
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ..database import get_db
from ..core.security import get_current_user_token, rate_limit_check
from ..models import StudySession, StudyStreak
from ..schemas import (
    StudySessionStart, StudySessionEnd, StudySessionUpdate, StudySessionResponse,
    StudySessionListResponse, StudyStreakResponse, StudyStreakUpdate,
    BadgeCreate, BadgeResponse, StudentBadgeResponse,
    StudyGoalCreate, StudyGoalUpdate, StudyGoalResponse,
    StudyAnalytics, StudyDashboard, TimerAction
)
from ..services.study_service import (
    StudySessionService, StudyGoalService, BadgeService
)
from ..utils.pagination import paginate_query
from ..utils.cache import cache_result, clear_cache_pattern

router = APIRouter()


# Study Session Timer Endpoints
@router.post("/sessions/start", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
async def start_study_session(
    session_data: StudySessionStart,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=10))
):
    """
    Start a new study session
    Automatically ends any existing active session
    """
    try:
        session = StudySessionService.start_session(
            db=db,
            student_id=current_user["user_id"],
            school_id=current_user["school_id"],
            session_data=session_data
        )
        
        # Clear cache for user analytics
        background_tasks.add_task(
            clear_cache_pattern,
            f"study_analytics_{current_user['user_id']}_*"
        )
        
        return StudySessionResponse.from_orm(session)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start study session: {str(e)}"
        )


@router.post("/sessions/{session_id}/end", response_model=StudySessionResponse)
async def end_study_session(
    session_id: int,
    end_data: StudySessionEnd,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=20))
):
    """
    End an active study session
    Calculates duration, focus score, and awards badges
    """
    try:
        session = StudySessionService.end_session(
            db=db,
            session_id=session_id,
            student_id=current_user["user_id"],
            end_data=end_data
        )
        
        # Clear cache for user analytics
        background_tasks.add_task(
            clear_cache_pattern,
            f"study_analytics_{current_user['user_id']}_*"
        )
        
        return StudySessionResponse.from_orm(session)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to end study session: {str(e)}"
        )


@router.get("/sessions/active", response_model=Optional[StudySessionResponse])
async def get_active_session(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get currently active study session for user
    """
    session = StudySessionService.get_active_session(
        db=db,
        student_id=current_user["user_id"]
    )
    
    if session:
        # Check if session should be timed out
        if session.is_expired():
            session = StudySessionService.end_session(
                db=db,
                session_id=session.id,
                student_id=current_user["user_id"],
                end_data=StudySessionEnd(status="timeout")
            )
            return None
        
        return StudySessionResponse.from_orm(session)
    
    return None


@router.put("/sessions/{session_id}", response_model=StudySessionResponse)
async def update_study_session(
    session_id: int,
    update_data: StudySessionUpdate,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=30))
):
    """
    Update study session details (notes, interruptions, etc.)
    """
    try:
        session = db.query(StudySession).filter(
            StudySession.id == session_id,
            StudySession.student_id == current_user["user_id"]
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study session not found"
            )
        
        # Update fields
        if update_data.notes is not None:
            session.notes = update_data.notes
        if update_data.interruptions is not None:
            session.interruptions = update_data.interruptions
        if update_data.focus_score is not None:
            session.focus_score = update_data.focus_score
        
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        
        return StudySessionResponse.from_orm(session)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update study session: {str(e)}"
        )


@router.post("/sessions/{session_id}/control")
async def control_timer(
    session_id: int,
    action: TimerAction,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=20))
):
    """
    Control timer actions: pause, resume, extend
    """
    try:
        session = db.query(StudySession).filter(
            StudySession.id == session_id,
            StudySession.student_id == current_user["user_id"],
            StudySession.status == "active"
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active study session not found"
            )
        
        if action.action == "extend" and action.extend_minutes:
            if session.planned_duration:
                session.planned_duration += action.extend_minutes
            else:
                session.planned_duration = action.extend_minutes
        
        session.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": f"Timer {action.action} successful", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to control timer: {str(e)}"
        )


# Study Session History
@router.get("/sessions", response_model=StudySessionListResponse)
async def get_study_sessions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    subject_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get paginated study session history for current user
    """
    try:
        sessions = StudySessionService.get_session_history(
            db=db,
            student_id=current_user["user_id"],
            limit=per_page,
            offset=(page - 1) * per_page,
            subject_id=subject_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get total count
        total_query = db.query(StudySession).filter(
            StudySession.student_id == current_user["user_id"]
        )
        
        if subject_id:
            total_query = total_query.filter(StudySession.subject_id == subject_id)
        if start_date:
            total_query = total_query.filter(StudySession.start_time >= start_date)
        if end_date:
            total_query = total_query.filter(StudySession.start_time <= end_date)
        
        total = total_query.count()
        pages = (total + per_page - 1) // per_page
        
        return StudySessionListResponse(
            sessions=[StudySessionResponse.from_orm(s) for s in sessions],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get study sessions: {str(e)}"
        )


# Analytics Endpoints
@router.get("/analytics", response_model=StudyAnalytics)
@cache_result(expiry=300)  # Cache for 5 minutes
async def get_study_analytics(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive study analytics for current user
    """
    try:
        analytics = StudySessionService.get_analytics(
            db=db,
            student_id=current_user["user_id"],
            school_id=current_user["school_id"]
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/dashboard", response_model=StudyDashboard)
@cache_result(expiry=60)  # Cache for 1 minute
async def get_study_dashboard(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get study dashboard with current session, streak, goals, and badges
    """
    try:
        # Get current session
        current_session = StudySessionService.get_active_session(
            db=db,
            student_id=current_user["user_id"]
        )
        
        # Get streak
        streak = db.query(StudyStreak).filter(
            StudyStreak.student_id == current_user["user_id"],
            StudyStreak.school_id == current_user["school_id"]
        ).first()
        
        # Get recent sessions
        recent_sessions = StudySessionService.get_session_history(
            db=db,
            student_id=current_user["user_id"],
            limit=5
        )
        
        # Get recent badges
        recent_badges = BadgeService.get_student_badges(
            db=db,
            student_id=current_user["user_id"]
        )[:5]
        
        # Get active goals
        active_goals = StudyGoalService.get_student_goals(
            db=db,
            student_id=current_user["user_id"],
            active_only=True
        )
        
        # Get analytics
        analytics = StudySessionService.get_analytics(
            db=db,
            student_id=current_user["user_id"],
            school_id=current_user["school_id"]
        )
        
        return StudyDashboard(
            current_session=StudySessionResponse.from_orm(current_session) if current_session else None,
            streak=StudyStreakResponse.from_orm(streak) if streak else None,
            recent_sessions=[StudySessionResponse.from_orm(s) for s in recent_sessions],
            recent_badges=[StudentBadgeResponse.from_orm(b) for b in recent_badges],
            active_goals=[StudyGoalResponse.from_orm(g) for g in active_goals],
            analytics=analytics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get dashboard: {str(e)}"
        )


# Study Streak Endpoints
@router.get("/streak", response_model=StudyStreakResponse)
async def get_study_streak(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get study streak information for current user
    """
    streak = db.query(StudyStreak).filter(
        StudyStreak.student_id == current_user["user_id"],
        StudyStreak.school_id == current_user["school_id"]
    ).first()
    
    if not streak:
        # Create initial streak record
        streak = StudyStreak(
            student_id=current_user["user_id"],
            school_id=current_user["school_id"],
            week_start_date=datetime.utcnow()
        )
        db.add(streak)
        db.commit()
        db.refresh(streak)
    
    return StudyStreakResponse.from_orm(streak)


@router.put("/streak", response_model=StudyStreakResponse)
async def update_study_streak(
    update_data: StudyStreakUpdate,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=10))
):
    """
    Update study streak targets
    """
    try:
        streak = db.query(StudyStreak).filter(
            StudyStreak.student_id == current_user["user_id"],
            StudyStreak.school_id == current_user["school_id"]
        ).first()
        
        if not streak:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study streak not found"
            )
        
        streak.weekly_target_minutes = update_data.weekly_target_minutes
        streak.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(streak)
        
        return StudyStreakResponse.from_orm(streak)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update streak: {str(e)}"
        )


# Background task to timeout expired sessions
@router.post("/admin/timeout-expired")
async def timeout_expired_sessions(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to timeout expired study sessions
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        count = StudySessionService.timeout_expired_sessions(db)
        return {"message": f"Timed out {count} expired sessions"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to timeout sessions: {str(e)}"
        )
