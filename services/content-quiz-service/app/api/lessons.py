"""
Lessons API Router
Comprehensive lesson management with content delivery and progress tracking
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc

from ..database import get_db
from ..models.content_models import Lesson, Course, Subject
from ..models.progress_models import LessonProgress
from ..schemas.content_schemas import (
    LessonCreate, LessonUpdate, LessonResponse,
    LessonListResponse, LessonDetailResponse
)
from ..core.security import get_current_user_token, require_admin_role, rate_limit_check
from ..utils.pagination import paginate_query
from ..utils.cache import cache_result, invalidate_cache_pattern
from ..utils.validators import validate_lesson_data
from ..utils.file_handler import save_lesson_files, delete_lesson_files

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=LessonListResponse)
async def list_lessons(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    course_id: Optional[int] = Query(None, description="Filter by course"),
    lesson_type: Optional[str] = Query(None, description="Filter by lesson type"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty"),
    search: Optional[str] = Query(None, description="Search in lesson title and description"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: str = Query("order_index", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    List lessons with filtering, searching, and pagination
    """
    try:
        # Build query with joins for efficient loading
        query = db.query(Lesson).join(Course).join(Subject)
        
        # Apply filters
        if course_id:
            query = query.filter(Lesson.course_id == course_id)
        
        if lesson_type:
            query = query.filter(Lesson.lesson_type == lesson_type)
        
        if difficulty_level:
            query = query.filter(Lesson.difficulty_level == difficulty_level)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Lesson.title).like(search_term),
                    func.lower(Lesson.description).like(search_term),
                    func.lower(Course.name).like(search_term)
                )
            )
        
        if is_active is not None:
            query = query.filter(Lesson.is_active == is_active)
        
        # Apply school isolation (if not admin)
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id:
                query = query.filter(Subject.school_id == school_id)
        
        # Apply sorting
        if sort_by == "course_name":
            sort_column = Course.name
        elif sort_by == "subject_name":
            sort_column = Subject.name
        else:
            sort_column = getattr(Lesson, sort_by, Lesson.order_index)
        
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Add secondary sort by order_index if not primary sort
        if sort_by != "order_index":
            query = query.order_by(Lesson.order_index)
        
        # Get paginated results
        result = paginate_query(query, page, page_size)
        
        # Prepare response with progress data for current user
        lessons_with_progress = []
        user_id = current_user.get("user_id")
        
        for lesson in result["items"]:
            # Get user progress for this lesson
            progress = None
            if user_id:
                progress = db.query(LessonProgress).filter(
                    LessonProgress.lesson_id == lesson.id,
                    LessonProgress.user_id == user_id
                ).first()
            
            lesson_dict = {
                "id": lesson.id,
                "title": lesson.title,
                "description": lesson.description,
                "lesson_type": lesson.lesson_type,
                "course_id": lesson.course_id,
                "course_name": lesson.course.name,
                "subject_name": lesson.course.subject.name,
                "order_index": lesson.order_index,
                "estimated_duration": lesson.estimated_duration,
                "difficulty_level": lesson.difficulty_level,
                "is_active": lesson.is_active,
                "progress": {
                    "is_completed": progress.is_completed if progress else False,
                    "completion_percentage": progress.completion_percentage if progress else 0,
                    "time_spent": progress.time_spent if progress else 0,
                    "last_accessed": progress.last_accessed if progress else None
                } if user_id else None,
                "created_at": lesson.created_at,
                "updated_at": lesson.updated_at
            }
            lessons_with_progress.append(lesson_dict)
        
        logger.info(f"Listed {len(lessons_with_progress)} lessons for user {current_user.get('user_id')}")
        
        return LessonListResponse(
            lessons=lessons_with_progress,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
        
    except Exception as e:
        logger.error(f"Error listing lessons: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lessons"
        )


@router.get("/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(
    lesson_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    Get detailed lesson information with content and progress
    """
    try:
        # Get lesson with related data
        lesson = db.query(Lesson).options(
            joinedload(Lesson.course).joinedload(Course.subject)
        ).filter(Lesson.id == lesson_id).first()
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Check access permissions
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id and lesson.course.subject.school_id != school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this lesson"
                )
        
        # Get user progress
        user_id = current_user.get("user_id")
        progress = None
        if user_id:
            progress = db.query(LessonProgress).filter(
                LessonProgress.lesson_id == lesson.id,
                LessonProgress.user_id == user_id
            ).first()
        
        # Get next and previous lessons
        next_lesson = db.query(Lesson).filter(
            Lesson.course_id == lesson.course_id,
            Lesson.order_index > lesson.order_index,
            Lesson.is_active == True
        ).order_by(Lesson.order_index).first()
        
        previous_lesson = db.query(Lesson).filter(
            Lesson.course_id == lesson.course_id,
            Lesson.order_index < lesson.order_index,
            Lesson.is_active == True
        ).order_by(Lesson.order_index.desc()).first()
        
        # Prepare response
        response_data = {
            "id": lesson.id,
            "title": lesson.title,
            "description": lesson.description,
            "lesson_type": lesson.lesson_type,
            "content": lesson.content,
            "course_id": lesson.course_id,
            "course_name": lesson.course.name,
            "subject_name": lesson.course.subject.name,
            "order_index": lesson.order_index,
            "estimated_duration": lesson.estimated_duration,
            "difficulty_level": lesson.difficulty_level,
            "prerequisites": lesson.prerequisites or [],
            "learning_outcomes": lesson.learning_outcomes or [],
            "video_url": lesson.video_url,
            "file_urls": lesson.file_urls or [],
            "is_active": lesson.is_active,
            "next_lesson_id": next_lesson.id if next_lesson else None,
            "previous_lesson_id": previous_lesson.id if previous_lesson else None,
            "progress": {
                "is_completed": progress.is_completed if progress else False,
                "completion_percentage": progress.completion_percentage if progress else 0,
                "time_spent": progress.time_spent if progress else 0,
                "last_accessed": progress.last_accessed if progress else None
            } if user_id else None,
            "created_at": lesson.created_at,
            "updated_at": lesson.updated_at
        }
        
        # Update last accessed time for the user
        if user_id and progress:
            from datetime import datetime
            progress.last_accessed = datetime.utcnow()
            db.commit()
        
        logger.info(f"Retrieved lesson {lesson_id} for user {current_user.get('user_id')}")
        
        return LessonDetailResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving lesson {lesson_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lesson"
        )


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    request: Request,
    lesson_data: LessonCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Create a new lesson (Admin only)
    """
    try:
        # Validate lesson data
        validation_result = validate_lesson_data(lesson_data.dict())
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {', '.join(validation_result['errors'])}"
            )
        
        # Verify course exists and user has access
        course = db.query(Course).options(
            joinedload(Course.subject)
        ).filter(Course.id == lesson_data.course_id).first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        if course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this course"
            )
        
        # Check for duplicate lesson title in course
        existing_lesson = db.query(Lesson).filter(
            Lesson.title == lesson_data.title,
            Lesson.course_id == lesson_data.course_id
        ).first()
        
        if existing_lesson:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Lesson with this title already exists in the course"
            )
        
        # Get next order index if not provided
        if lesson_data.order_index is None:
            max_order = db.query(func.max(Lesson.order_index)).filter(
                Lesson.course_id == lesson_data.course_id
            ).scalar() or 0
            order_index = max_order + 1
        else:
            order_index = lesson_data.order_index
        
        # Create new lesson
        new_lesson = Lesson(
            title=lesson_data.title,
            description=lesson_data.description,
            lesson_type=lesson_data.lesson_type,
            content=lesson_data.content,
            course_id=lesson_data.course_id,
            order_index=order_index,
            estimated_duration=lesson_data.estimated_duration,
            difficulty_level=lesson_data.difficulty_level,
            prerequisites=lesson_data.prerequisites,
            learning_outcomes=lesson_data.learning_outcomes,
            created_by=current_user.get("user_id"),
            is_active=True
        )
        
        db.add(new_lesson)
        db.commit()
        db.refresh(new_lesson)
        
        # Update course lesson count
        course.lesson_count = db.query(func.count(Lesson.id)).filter(
            Lesson.course_id == course.id
        ).scalar()
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"lessons:*")
        invalidate_cache_pattern(f"course:{lesson_data.course_id}:*")
        
        logger.info(f"Created lesson {new_lesson.id} by user {current_user.get('user_id')}")
        
        return LessonResponse(
            id=new_lesson.id,
            title=new_lesson.title,
            description=new_lesson.description,
            lesson_type=new_lesson.lesson_type,
            content=new_lesson.content,
            course_id=new_lesson.course_id,
            order_index=new_lesson.order_index,
            estimated_duration=new_lesson.estimated_duration,
            difficulty_level=new_lesson.difficulty_level,
            prerequisites=new_lesson.prerequisites,
            learning_outcomes=new_lesson.learning_outcomes,
            video_url=new_lesson.video_url,
            file_urls=new_lesson.file_urls,
            is_active=new_lesson.is_active,
            created_at=new_lesson.created_at,
            updated_at=new_lesson.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lesson: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create lesson"
        )


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    request: Request,
    lesson_data: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=20))
):
    """
    Update an existing lesson (Admin only)
    """
    try:
        # Get existing lesson with course and subject
        lesson = db.query(Lesson).options(
            joinedload(Lesson.course).joinedload(Course.subject)
        ).filter(Lesson.id == lesson_id).first()
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Check school access
        if lesson.course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this lesson"
            )
        
        # Validate update data
        update_data = lesson_data.dict(exclude_unset=True)
        if update_data:
            validation_result = validate_lesson_data(update_data)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Validation failed: {', '.join(validation_result['errors'])}"
                )
        
        # Check for duplicate title if updating
        if "title" in update_data and update_data["title"] != lesson.title:
            existing_lesson = db.query(Lesson).filter(
                Lesson.title == update_data["title"],
                Lesson.course_id == lesson.course_id,
                Lesson.id != lesson_id
            ).first()
            
            if existing_lesson:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Lesson with this title already exists in the course"
                )
        
        # Update lesson fields
        for field, value in update_data.items():
            setattr(lesson, field, value)
        
        lesson.updated_by = current_user.get("user_id")
        
        db.commit()
        db.refresh(lesson)
        
        # Invalidate related caches
        invalidate_cache_pattern(f"lessons:*")
        invalidate_cache_pattern(f"lesson:{lesson_id}:*")
        invalidate_cache_pattern(f"course:{lesson.course_id}:*")
        
        logger.info(f"Updated lesson {lesson_id} by user {current_user.get('user_id')}")
        
        return LessonResponse(
            id=lesson.id,
            title=lesson.title,
            description=lesson.description,
            lesson_type=lesson.lesson_type,
            content=lesson.content,
            course_id=lesson.course_id,
            order_index=lesson.order_index,
            estimated_duration=lesson.estimated_duration,
            difficulty_level=lesson.difficulty_level,
            prerequisites=lesson.prerequisites,
            learning_outcomes=lesson.learning_outcomes,
            video_url=lesson.video_url,
            file_urls=lesson.file_urls,
            is_active=lesson.is_active,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lesson {lesson_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update lesson"
        )


@router.post("/{lesson_id}/files", response_model=Dict[str, Any])
async def upload_lesson_files(
    lesson_id: int,
    request: Request,
    files: List[UploadFile] = File(...),
    file_descriptions: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=5))
):
    """
    Upload files for a lesson (Admin only)
    """
    try:
        # Get lesson
        lesson = db.query(Lesson).options(
            joinedload(Lesson.course).joinedload(Course.subject)
        ).filter(Lesson.id == lesson_id).first()
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Check school access
        if lesson.course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this lesson"
            )
        
        # Upload files
        uploaded_files = await save_lesson_files(lesson_id, files)
        
        # Update lesson file URLs
        current_files = lesson.file_urls or []
        new_file_urls = [file_info["file_url"] for file_info in uploaded_files]
        lesson.file_urls = current_files + new_file_urls
        lesson.updated_by = current_user.get("user_id")
        
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"lesson:{lesson_id}:*")
        
        logger.info(f"Uploaded {len(uploaded_files)} files for lesson {lesson_id} by user {current_user.get('user_id')}")
        
        return {
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files),
            "lesson_file_urls": lesson.file_urls
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading files for lesson {lesson_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload files"
        )


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Delete a lesson (Admin only)
    """
    try:
        # Get lesson
        lesson = db.query(Lesson).options(
            joinedload(Lesson.course).joinedload(Course.subject)
        ).filter(Lesson.id == lesson_id).first()
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Check school access
        if lesson.course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this lesson"
            )
        
        course_id = lesson.course_id
        
        # Delete lesson files
        delete_lesson_files(lesson_id)
        
        # Delete lesson progress records
        db.query(LessonProgress).filter(
            LessonProgress.lesson_id == lesson_id
        ).delete()
        
        # Delete lesson
        db.delete(lesson)
        db.commit()
        
        # Update course lesson count
        course = db.query(Course).filter(Course.id == course_id).first()
        if course:
            course.lesson_count = db.query(func.count(Lesson.id)).filter(
                Lesson.course_id == course_id
            ).scalar()
            db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"lessons:*")
        invalidate_cache_pattern(f"lesson:{lesson_id}:*")
        invalidate_cache_pattern(f"course:{course_id}:*")
        
        logger.info(f"Deleted lesson {lesson_id} by user {current_user.get('user_id')}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lesson {lesson_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete lesson"
        )
