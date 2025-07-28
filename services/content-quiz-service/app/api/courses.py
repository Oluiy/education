"""
Courses API Router
Comprehensive course management with curriculum organization
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc

from ..database import get_db
from ..models.content_models import Course, Subject, Lesson, Quiz
from ..schemas.content_schemas import (
    CourseCreate, CourseUpdate, CourseResponse,
    CourseListResponse, CourseDetailResponse, 
    LessonSummaryResponse, QuizSummaryResponse
)
from ..core.security import get_current_user_token, require_admin_role, rate_limit_check
from ..utils.pagination import paginate_query
from ..utils.cache import cache_result, invalidate_cache_pattern
from ..utils.validators import validate_course_data
from ..utils.file_handler import save_course_thumbnail, delete_course_files

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=CourseListResponse)
async def list_courses(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    subject_id: Optional[int] = Query(None, description="Filter by subject"),
    search: Optional[str] = Query(None, description="Search in course name and description"),
    level: Optional[str] = Query(None, description="Filter by course level"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    List courses with filtering, searching, and pagination
    """
    try:
        # Build query with joins for efficient loading
        query = db.query(Course).join(Subject)
        
        # Apply filters
        if subject_id:
            query = query.filter(Course.subject_id == subject_id)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Course.name).like(search_term),
                    func.lower(Course.description).like(search_term),
                    func.lower(Subject.name).like(search_term)
                )
            )
        
        if level:
            query = query.filter(Course.level == level)
        
        if is_active is not None:
            query = query.filter(Course.is_active == is_active)
        
        # Apply school isolation (if not admin)
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id:
                query = query.filter(Subject.school_id == school_id)
        
        # Apply sorting
        if sort_by == "subject_name":
            sort_column = Subject.name
        else:
            sort_column = getattr(Course, sort_by, Course.name)
        
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Add secondary sort by order_index
        query = query.order_by(Course.order_index)
        
        # Get paginated results
        result = paginate_query(query, page, page_size)
        
        # Prepare response with additional data
        courses_with_details = []
        for course in result["items"]:
            # Get lesson and quiz counts
            lesson_count = db.query(func.count(Lesson.id)).filter(
                Lesson.course_id == course.id,
                Lesson.is_active == True
            ).scalar()
            
            quiz_count = db.query(func.count(Quiz.id)).filter(
                Quiz.course_id == course.id,
                Quiz.is_active == True
            ).scalar()
            
            # Get enrollment count (if implemented)
            enrollment_count = 0  # Would come from enrollment service
            
            course_dict = {
                "id": course.id,
                "name": course.name,
                "description": course.description,
                "subject_id": course.subject_id,
                "subject_name": course.subject.name,
                "level": course.level,
                "duration_hours": course.duration_hours,
                "order_index": course.order_index,
                "lesson_count": lesson_count,
                "quiz_count": quiz_count,
                "enrollment_count": enrollment_count,
                "thumbnail_url": course.thumbnail_url,
                "difficulty": course.difficulty,
                "prerequisites": course.prerequisites,
                "learning_objectives": course.learning_objectives,
                "is_active": course.is_active,
                "created_at": course.created_at,
                "updated_at": course.updated_at
            }
            courses_with_details.append(course_dict)
        
        logger.info(f"Listed {len(courses_with_details)} courses for user {current_user.get('user_id')}")
        
        return CourseListResponse(
            courses=courses_with_details,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
        
    except Exception as e:
        logger.error(f"Error listing courses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve courses"
        )


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_id: int,
    request: Request,
    include_lessons: bool = Query(False, description="Include lessons in response"),
    include_quizzes: bool = Query(False, description="Include quizzes in response"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    Get detailed course information
    """
    try:
        # Get course with subject
        course = db.query(Course).options(
            joinedload(Course.subject)
        ).filter(Course.id == course_id).first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Check access permissions
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id and course.subject.school_id != school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this course"
                )
        
        # Get lesson and quiz counts
        lesson_count = db.query(func.count(Lesson.id)).filter(
            Lesson.course_id == course.id
        ).scalar()
        
        quiz_count = db.query(func.count(Quiz.id)).filter(
            Quiz.course_id == course.id
        ).scalar()
        
        # Prepare response
        response_data = {
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "level": course.level,
            "subject_id": course.subject_id,
            "subject_name": course.subject.name,
            "order_index": course.order_index,
            "estimated_duration": course.estimated_duration,
            "thumbnail_url": course.thumbnail_url,
            "prerequisite_courses": course.prerequisite_courses or [],
            "learning_objectives": course.learning_objectives or [],
            "is_active": course.is_active,
            "lesson_count": lesson_count,
            "quiz_count": quiz_count,
            "created_at": course.created_at,
            "updated_at": course.updated_at
        }
        
        # Include lessons if requested
        if include_lessons:
            lessons = db.query(Lesson).filter(
                Lesson.course_id == course.id,
                Lesson.is_active == True
            ).order_by(Lesson.order_index, Lesson.title).all()
            
            response_data["lessons"] = [
                LessonSummaryResponse(
                    id=lesson.id,
                    title=lesson.title,
                    description=lesson.description,
                    order_index=lesson.order_index,
                    lesson_type=lesson.lesson_type,
                    estimated_duration=lesson.estimated_duration,
                    difficulty_level=lesson.difficulty_level,
                    is_active=lesson.is_active
                )
                for lesson in lessons
            ]
        
        # Include quizzes if requested
        if include_quizzes:
            quizzes = db.query(Quiz).filter(
                Quiz.course_id == course.id,
                Quiz.is_active == True
            ).order_by(Quiz.order_index, Quiz.title).all()
            
            response_data["quizzes"] = [
                QuizSummaryResponse(
                    id=quiz.id,
                    title=quiz.title,
                    description=quiz.description,
                    quiz_type=quiz.quiz_type,
                    time_limit=quiz.time_limit,
                    total_questions=quiz.total_questions,
                    passing_score=quiz.passing_score,
                    is_active=quiz.is_active
                )
                for quiz in quizzes
            ]
        
        logger.info(f"Retrieved course {course_id} for user {current_user.get('user_id')}")
        
        return CourseDetailResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving course {course_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve course"
        )


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    request: Request,
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Create a new course (Admin only)
    """
    try:
        # Validate course data
        validation_result = validate_course_data(course_data.dict())
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {', '.join(validation_result['errors'])}"
            )
        
        # Verify subject exists and user has access
        subject = db.query(Subject).filter(Subject.id == course_data.subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        if subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this subject"
            )
        
        # Check for duplicate course name in subject
        existing_course = db.query(Course).filter(
            Course.name == course_data.name,
            Course.subject_id == course_data.subject_id
        ).first()
        
        if existing_course:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course with this name already exists in the subject"
            )
        
        # Get next order index if not provided
        if course_data.order_index is None:
            max_order = db.query(func.max(Course.order_index)).filter(
                Course.subject_id == course_data.subject_id
            ).scalar() or 0
            order_index = max_order + 1
        else:
            order_index = course_data.order_index
        
        # Create new course
        new_course = Course(
            name=course_data.name,
            description=course_data.description,
            level=course_data.level,
            subject_id=course_data.subject_id,
            order_index=order_index,
            estimated_duration=course_data.estimated_duration,
            prerequisite_courses=course_data.prerequisite_courses,
            learning_objectives=course_data.learning_objectives,
            created_by=current_user.get("user_id"),
            is_active=True
        )
        
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        
        # Invalidate related caches
        invalidate_cache_pattern(f"courses:*")
        invalidate_cache_pattern(f"subject:{course_data.subject_id}:*")
        
        logger.info(f"Created course {new_course.id} by user {current_user.get('user_id')}")
        
        return CourseResponse(
            id=new_course.id,
            name=new_course.name,
            description=new_course.description,
            level=new_course.level,
            subject_id=new_course.subject_id,
            order_index=new_course.order_index,
            estimated_duration=new_course.estimated_duration,
            thumbnail_url=new_course.thumbnail_url,
            prerequisite_courses=new_course.prerequisite_courses,
            learning_objectives=new_course.learning_objectives,
            is_active=new_course.is_active,
            created_at=new_course.created_at,
            updated_at=new_course.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create course"
        )


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    request: Request,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=20))
):
    """
    Update an existing course (Admin only)
    """
    try:
        # Get existing course with subject
        course = db.query(Course).options(
            joinedload(Course.subject)
        ).filter(Course.id == course_id).first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Check school access
        if course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this course"
            )
        
        # Validate update data
        update_data = course_data.dict(exclude_unset=True)
        if update_data:
            validation_result = validate_course_data(update_data)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Validation failed: {', '.join(validation_result['errors'])}"
                )
        
        # Check for duplicate name if updating
        if "name" in update_data and update_data["name"] != course.name:
            existing_course = db.query(Course).filter(
                Course.name == update_data["name"],
                Course.subject_id == course.subject_id,
                Course.id != course_id
            ).first()
            
            if existing_course:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Course with this name already exists in the subject"
                )
        
        # Update course fields
        for field, value in update_data.items():
            setattr(course, field, value)
        
        course.updated_by = current_user.get("user_id")
        
        db.commit()
        db.refresh(course)
        
        # Invalidate related caches
        invalidate_cache_pattern(f"courses:*")
        invalidate_cache_pattern(f"course:{course_id}:*")
        invalidate_cache_pattern(f"subject:{course.subject_id}:*")
        
        logger.info(f"Updated course {course_id} by user {current_user.get('user_id')}")
        
        return CourseResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            level=course.level,
            subject_id=course.subject_id,
            order_index=course.order_index,
            estimated_duration=course.estimated_duration,
            thumbnail_url=course.thumbnail_url,
            prerequisite_courses=course.prerequisite_courses,
            learning_objectives=course.learning_objectives,
            is_active=course.is_active,
            created_at=course.created_at,
            updated_at=course.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating course {course_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update course"
        )


@router.post("/{course_id}/thumbnail", response_model=Dict[str, str])
async def upload_course_thumbnail(
    course_id: int,
    request: Request,
    thumbnail: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=5))
):
    """
    Upload course thumbnail image (Admin only)
    """
    try:
        # Get course
        course = db.query(Course).options(
            joinedload(Course.subject)
        ).filter(Course.id == course_id).first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Check school access
        if course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this course"
            )
        
        # Save thumbnail
        thumbnail_url = await save_course_thumbnail(course_id, thumbnail)
        
        # Update course
        course.thumbnail_url = thumbnail_url
        course.updated_by = current_user.get("user_id")
        
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"course:{course_id}:*")
        
        logger.info(f"Uploaded thumbnail for course {course_id} by user {current_user.get('user_id')}")
        
        return {"thumbnail_url": thumbnail_url}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading thumbnail for course {course_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload thumbnail"
        )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    request: Request,
    force: bool = Query(False, description="Force delete even if lessons/quizzes exist"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Delete a course (Admin only)
    """
    try:
        # Get course
        course = db.query(Course).options(
            joinedload(Course.subject)
        ).filter(Course.id == course_id).first()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Check school access
        if course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this course"
            )
        
        # Check for existing content
        lesson_count = db.query(func.count(Lesson.id)).filter(
            Lesson.course_id == course_id
        ).scalar()
        
        quiz_count = db.query(func.count(Quiz.id)).filter(
            Quiz.course_id == course_id
        ).scalar()
        
        if (lesson_count > 0 or quiz_count > 0) and not force:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete course with {lesson_count} lessons and {quiz_count} quizzes. Use force=true to delete anyway."
            )
        
        # If force delete, remove all associated content
        if force:
            if lesson_count > 0:
                db.query(Lesson).filter(Lesson.course_id == course_id).delete()
            if quiz_count > 0:
                db.query(Quiz).filter(Quiz.course_id == course_id).delete()
        
        # Delete course files
        delete_course_files(course_id)
        
        # Delete course
        db.delete(course)
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"courses:*")
        invalidate_cache_pattern(f"course:{course_id}:*")
        invalidate_cache_pattern(f"subject:{course.subject_id}:*")
        
        logger.info(f"Deleted course {course_id} by user {current_user.get('user_id')}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting course {course_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete course"
        )
