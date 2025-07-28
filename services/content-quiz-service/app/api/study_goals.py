"""
Study Goals API Endpoints
REST API for managing student study goals and achievements
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..core.security import get_current_user_token, rate_limit_check
from ..models import StudyGoal
from ..schemas import (
    StudyGoalCreate, StudyGoalUpdate, StudyGoalResponse
)
from ..services.study_service import StudyGoalService

router = APIRouter()


@router.post("/goals", response_model=StudyGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_study_goal(
    goal_data: StudyGoalCreate,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=10))
):
    """
    Create a new study goal for the current user
    """
    try:
        goal = StudyGoalService.create_goal(
            db=db,
            student_id=current_user["user_id"],
            school_id=current_user["school_id"],
            goal_data=goal_data
        )
        
        return StudyGoalResponse.from_orm(goal)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create study goal: {str(e)}"
        )


@router.get("/goals", response_model=List[StudyGoalResponse])
async def get_study_goals(
    active_only: bool = Query(False),
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get study goals for current user
    """
    try:
        goals = StudyGoalService.get_student_goals(
            db=db,
            student_id=current_user["user_id"],
            active_only=active_only
        )
        
        return [StudyGoalResponse.from_orm(goal) for goal in goals]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get study goals: {str(e)}"
        )


@router.get("/goals/{goal_id}", response_model=StudyGoalResponse)
async def get_study_goal(
    goal_id: int,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get specific study goal by ID
    """
    goal = db.query(StudyGoal).filter(
        StudyGoal.id == goal_id,
        StudyGoal.student_id == current_user["user_id"]
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study goal not found"
        )
    
    return StudyGoalResponse.from_orm(goal)


@router.put("/goals/{goal_id}", response_model=StudyGoalResponse)
async def update_study_goal(
    goal_id: int,
    update_data: StudyGoalUpdate,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=20))
):
    """
    Update a study goal
    """
    try:
        goal = db.query(StudyGoal).filter(
            StudyGoal.id == goal_id,
            StudyGoal.student_id == current_user["user_id"]
        ).first()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study goal not found"
            )
        
        # Update fields
        if update_data.title is not None:
            goal.title = update_data.title
        if update_data.description is not None:
            goal.description = update_data.description
        if update_data.target_minutes is not None:
            goal.target_minutes = update_data.target_minutes
        if update_data.target_sessions is not None:
            goal.target_sessions = update_data.target_sessions
        if update_data.end_date is not None:
            goal.end_date = update_data.end_date
        
        goal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(goal)
        
        return StudyGoalResponse.from_orm(goal)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update study goal: {str(e)}"
        )


@router.delete("/goals/{goal_id}")
async def delete_study_goal(
    goal_id: int,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=10))
):
    """
    Delete a study goal
    """
    try:
        goal = db.query(StudyGoal).filter(
            StudyGoal.id == goal_id,
            StudyGoal.student_id == current_user["user_id"]
        ).first()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study goal not found"
            )
        
        db.delete(goal)
        db.commit()
        
        return {"message": "Study goal deleted successfully", "goal_id": goal_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete study goal: {str(e)}"
        )
