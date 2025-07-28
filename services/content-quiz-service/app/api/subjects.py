"""
Subjects API Router
Comprehensive subject management for educational content organization
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..database import get_db
from ..models.content_models import Subject, Course
from ..schemas.content_schemas import (
    SubjectCreate, SubjectUpdate, SubjectResponse, 
    SubjectListResponse, SubjectDetailResponse
)
from ..core.security import get_current_user_token, require_admin_role, rate_limit_check
from ..utils.pagination import paginate_query
from ..utils.cache import cache_result, invalidate_cache_pattern
from ..utils.validators import validate_subject_data

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=SubjectListResponse)
async def list_subjects(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in subject name and description"),
    grade_level: Optional[str] = Query(None, description="Filter by grade level"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    List subjects with filtering, searching, and pagination
    """
    try:
        # Build query
        query = db.query(Subject)
        
        # Apply filters
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Subject.name).like(search_term),
                    func.lower(Subject.description).like(search_term),
                    func.lower(Subject.code).like(search_term)
                )
            )
        
        if grade_level:
            query = query.filter(Subject.grade_level == grade_level)
        
        if is_active is not None:
            query = query.filter(Subject.is_active == is_active)
        
        # Apply school isolation (if not admin)
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id:
                query = query.filter(Subject.school_id == school_id)
        
        # Apply sorting
        sort_column = getattr(Subject, sort_by, Subject.name)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Get paginated results
        result = paginate_query(query, page, page_size)
        
        # Add course count for each subject
        subjects_with_counts = []
        for subject in result["items"]:
            course_count = db.query(func.count(Course.id)).filter(
                Course.subject_id == subject.id
            ).scalar()
            
            subject_dict = {
                "id": subject.id,
                "name": subject.name,
                "code": subject.code,
                "description": subject.description,
                "grade_level": subject.grade_level,
                "color_theme": subject.color_theme,
                "icon": subject.icon,
                "is_active": subject.is_active,
                "course_count": course_count,
                "created_at": subject.created_at,
                "updated_at": subject.updated_at
            }
            subjects_with_counts.append(subject_dict)
        
        logger.info(f"Listed {len(subjects_with_counts)} subjects for user {current_user.get('user_id')}")
        
        return SubjectListResponse(
            subjects=subjects_with_counts,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
        
    except Exception as e:
        logger.error(f"Error listing subjects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subjects"
        )


@router.get("/{subject_id}", response_model=SubjectDetailResponse)
async def get_subject(
    subject_id: int,
    request: Request,
    include_courses: bool = Query(False, description="Include courses in response"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    Get detailed subject information
    """
    try:
        # Get subject
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Check access permissions
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id and subject.school_id != school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this subject"
                )
        
        # Get course count
        course_count = db.query(func.count(Course.id)).filter(
            Course.subject_id == subject.id
        ).scalar()
        
        # Prepare response
        response_data = {
            "id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "grade_level": subject.grade_level,
            "color_theme": subject.color_theme,
            "icon": subject.icon,
            "is_active": subject.is_active,
            "course_count": course_count,
            "created_at": subject.created_at,
            "updated_at": subject.updated_at
        }
        
        # Include courses if requested
        if include_courses:
            courses = db.query(Course).filter(
                Course.subject_id == subject.id,
                Course.is_active == True
            ).order_by(Course.order_index, Course.name).all()
            
            response_data["courses"] = [
                {
                    "id": course.id,
                    "name": course.name,
                    "description": course.description,
                    "level": course.level,
                    "order_index": course.order_index,
                    "estimated_duration": course.estimated_duration,
                    "lesson_count": course.lesson_count,
                    "is_active": course.is_active
                }
                for course in courses
            ]
        
        logger.info(f"Retrieved subject {subject_id} for user {current_user.get('user_id')}")
        
        return SubjectDetailResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving subject {subject_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subject"
        )


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    request: Request,
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Create a new subject (Admin only)
    """
    try:
        # Validate subject data
        validation_result = validate_subject_data(subject_data.dict())
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {', '.join(validation_result['errors'])}"
            )
        
        # Check for duplicate subject code
        existing_subject = db.query(Subject).filter(
            Subject.code == subject_data.code,
            Subject.school_id == current_user.get("school_id")
        ).first()
        
        if existing_subject:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Subject with this code already exists"
            )
        
        # Create new subject
        new_subject = Subject(
            name=subject_data.name,
            code=subject_data.code,
            description=subject_data.description,
            grade_level=subject_data.grade_level,
            color_theme=subject_data.color_theme,
            icon=subject_data.icon,
            school_id=current_user.get("school_id"),
            created_by=current_user.get("user_id"),
            is_active=True
        )
        
        db.add(new_subject)
        db.commit()
        db.refresh(new_subject)
        
        # Invalidate related caches
        invalidate_cache_pattern(f"subjects:*")
        
        logger.info(f"Created subject {new_subject.id} by user {current_user.get('user_id')}")
        
        return SubjectResponse(
            id=new_subject.id,
            name=new_subject.name,
            code=new_subject.code,
            description=new_subject.description,
            grade_level=new_subject.grade_level,
            color_theme=new_subject.color_theme,
            icon=new_subject.icon,
            is_active=new_subject.is_active,
            created_at=new_subject.created_at,
            updated_at=new_subject.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subject: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subject"
        )


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    request: Request,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=20))
):
    """
    Update an existing subject (Admin only)
    """
    try:
        # Get existing subject
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Check school access
        if subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this subject"
            )
        
        # Validate update data
        update_data = subject_data.dict(exclude_unset=True)
        if update_data:
            validation_result = validate_subject_data(update_data)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Validation failed: {', '.join(validation_result['errors'])}"
                )
        
        # Check for duplicate code if updating
        if "code" in update_data and update_data["code"] != subject.code:
            existing_subject = db.query(Subject).filter(
                Subject.code == update_data["code"],
                Subject.school_id == current_user.get("school_id"),
                Subject.id != subject_id
            ).first()
            
            if existing_subject:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Subject with this code already exists"
                )
        
        # Update subject fields
        for field, value in update_data.items():
            setattr(subject, field, value)
        
        subject.updated_by = current_user.get("user_id")
        
        db.commit()
        db.refresh(subject)
        
        # Invalidate related caches
        invalidate_cache_pattern(f"subjects:*")
        invalidate_cache_pattern(f"subject:{subject_id}:*")
        
        logger.info(f"Updated subject {subject_id} by user {current_user.get('user_id')}")
        
        return SubjectResponse(
            id=subject.id,
            name=subject.name,
            code=subject.code,
            description=subject.description,
            grade_level=subject.grade_level,
            color_theme=subject.color_theme,
            icon=subject.icon,
            is_active=subject.is_active,
            created_at=subject.created_at,
            updated_at=subject.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subject {subject_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subject"
        )


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: int,
    request: Request,
    force: bool = Query(False, description="Force delete even if courses exist"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Delete a subject (Admin only)
    """
    try:
        # Get subject
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Check school access
        if subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this subject"
            )
        
        # Check for existing courses
        course_count = db.query(func.count(Course.id)).filter(
            Course.subject_id == subject_id
        ).scalar()
        
        if course_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete subject with {course_count} courses. Use force=true to delete anyway."
            )
        
        # If force delete, remove all associated courses
        if force and course_count > 0:
            db.query(Course).filter(Course.subject_id == subject_id).delete()
        
        # Delete subject
        db.delete(subject)
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"subjects:*")
        invalidate_cache_pattern(f"subject:{subject_id}:*")
        
        logger.info(f"Deleted subject {subject_id} by user {current_user.get('user_id')}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting subject {subject_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete subject"
        )


@router.post("/{subject_id}/toggle-status", response_model=SubjectResponse)
async def toggle_subject_status(
    subject_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=20))
):
    """
    Toggle subject active status (Admin only)
    """
    try:
        # Get subject
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Check school access
        if subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this subject"
            )
        
        # Toggle status
        subject.is_active = not subject.is_active
        subject.updated_by = current_user.get("user_id")
        
        db.commit()
        db.refresh(subject)
        
        # Invalidate related caches
        invalidate_cache_pattern(f"subjects:*")
        invalidate_cache_pattern(f"subject:{subject_id}:*")
        
        logger.info(f"Toggled subject {subject_id} status to {subject.is_active} by user {current_user.get('user_id')}")
        
        return SubjectResponse(
            id=subject.id,
            name=subject.name,
            code=subject.code,
            description=subject.description,
            grade_level=subject.grade_level,
            color_theme=subject.color_theme,
            icon=subject.icon,
            is_active=subject.is_active,
            created_at=subject.created_at,
            updated_at=subject.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling subject {subject_id} status: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle subject status"
        )


@router.get("/{subject_id}/statistics", response_model=Dict[str, Any])
async def get_subject_statistics(
    subject_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=50))
):
    """
    Get comprehensive statistics for a subject
    """
    try:
        # Get subject
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Check access permissions
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id and subject.school_id != school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this subject"
                )
        
        # Get statistics
        stats = {
            "subject_id": subject_id,
            "total_courses": db.query(func.count(Course.id)).filter(Course.subject_id == subject_id).scalar(),
            "active_courses": db.query(func.count(Course.id)).filter(
                Course.subject_id == subject_id,
                Course.is_active == True
            ).scalar(),
        }
        
        logger.info(f"Retrieved statistics for subject {subject_id}")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving subject {subject_id} statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subject statistics"
        )
