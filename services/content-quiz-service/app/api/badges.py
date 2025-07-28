"""
Badge Management API Endpoints
REST API for managing achievement badges
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..core.security import get_current_user_token, require_admin_role, rate_limit_check
from ..models import Badge, StudentBadge
from ..schemas import (
    BadgeCreate, BadgeResponse, StudentBadgeResponse
)
from ..services.study_service import BadgeService

router = APIRouter()


@router.post("/badges", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
async def create_badge(
    badge_data: BadgeCreate,
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=5))
):
    """
    Create a new achievement badge (Admin only)
    """
    try:
        badge = BadgeService.create_badge(db=db, badge_data=badge_data)
        return BadgeResponse.from_orm(badge)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create badge: {str(e)}"
        )


@router.get("/badges", response_model=List[BadgeResponse])
async def get_all_badges(
    badge_type: Optional[str] = Query(None),
    rarity: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get all available badges
    """
    try:
        query = db.query(Badge)
        
        if badge_type:
            query = query.filter(Badge.badge_type == badge_type)
        if rarity:
            query = query.filter(Badge.rarity == rarity)
        
        badges = query.all()
        return [BadgeResponse.from_orm(badge) for badge in badges]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get badges: {str(e)}"
        )


@router.get("/my-badges", response_model=List[StudentBadgeResponse])
async def get_my_badges(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get badges earned by current user
    """
    try:
        badges = BadgeService.get_student_badges(
            db=db,
            student_id=current_user["user_id"]
        )
        
        return [StudentBadgeResponse.from_orm(badge) for badge in badges]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user badges: {str(e)}"
        )


@router.get("/badges/{badge_id}", response_model=BadgeResponse)
async def get_badge(
    badge_id: int,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """
    Get specific badge details
    """
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Badge not found"
        )
    
    return BadgeResponse.from_orm(badge)


@router.put("/my-badges/{badge_id}/display")
async def toggle_badge_display(
    badge_id: int,
    display: bool = Query(...),
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
    _: None = Depends(lambda: rate_limit_check(limit=20))
):
    """
    Toggle badge display on user profile
    """
    try:
        student_badge = db.query(StudentBadge).filter(
            StudentBadge.badge_id == badge_id,
            StudentBadge.student_id == current_user["user_id"]
        ).first()
        
        if not student_badge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Badge not found in user collection"
            )
        
        student_badge.is_displayed = display
        db.commit()
        
        return {
            "message": f"Badge display {'enabled' if display else 'disabled'}",
            "badge_id": badge_id,
            "displayed": display
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update badge display: {str(e)}"
        )
