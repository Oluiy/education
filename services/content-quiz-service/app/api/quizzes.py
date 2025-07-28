"""
Quizzes API Router
Comprehensive quiz management with AI-powered generation and automated grading
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc

from ..database import get_db
from ..models.content_models import Quiz, Course, Subject, Question, QuizSubmission
from ..models.progress_models import QuizProgress
from ..schemas.content_schemas import (
    QuizCreate, QuizUpdate, QuizResponse,
    QuizListResponse, QuizDetailResponse,
    QuizSubmissionCreate, QuizSubmissionResponse
)
from ..core.security import get_current_user_token, require_admin_role, rate_limit_check
from ..utils.pagination import paginate_query
from ..utils.cache import cache_result, invalidate_cache_pattern
from ..utils.validators import validate_quiz_data
from ..utils.quiz_grader import grade_quiz_submission
from ..utils.ai_quiz_generator import generate_quiz_questions

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=QuizListResponse)
async def list_quizzes(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    course_id: Optional[int] = Query(None, description="Filter by course"),
    quiz_type: Optional[str] = Query(None, description="Filter by quiz type"),
    search: Optional[str] = Query(None, description="Search in quiz title and description"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: str = Query("order_index", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    List quizzes with filtering, searching, and pagination
    """
    try:
        # Build query with joins for efficient loading
        query = db.query(Quiz).join(Course).join(Subject)
        
        # Apply filters
        if course_id:
            query = query.filter(Quiz.course_id == course_id)
        
        if quiz_type:
            query = query.filter(Quiz.quiz_type == quiz_type)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Quiz.title).like(search_term),
                    func.lower(Quiz.description).like(search_term),
                    func.lower(Course.name).like(search_term)
                )
            )
        
        if is_active is not None:
            query = query.filter(Quiz.is_active == is_active)
        
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
            sort_column = getattr(Quiz, sort_by, Quiz.order_index)
        
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Add secondary sort by order_index if not primary sort
        if sort_by != "order_index":
            query = query.order_by(Quiz.order_index)
        
        # Get paginated results
        result = paginate_query(query, page, page_size)
        
        # Prepare response with submission data for current user
        quizzes_with_submissions = []
        user_id = current_user.get("user_id")
        
        for quiz in result["items"]:
            # Get user's latest submission for this quiz
            submission = None
            if user_id:
                submission = db.query(QuizSubmission).filter(
                    QuizSubmission.quiz_id == quiz.id,
                    QuizSubmission.user_id == user_id
                ).order_by(QuizSubmission.submitted_at.desc()).first()
            
            quiz_dict = {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "quiz_type": quiz.quiz_type,
                "course_id": quiz.course_id,
                "course_name": quiz.course.name,
                "subject_name": quiz.course.subject.name,
                "time_limit": quiz.time_limit,
                "passing_score": quiz.passing_score,
                "total_questions": quiz.total_questions,
                "question_count": quiz.question_count,
                "order_index": quiz.order_index,
                "is_active": quiz.is_active,
                "user_submission": {
                    "id": submission.id if submission else None,
                    "score": submission.score if submission else None,
                    "is_passed": submission.is_passed if submission else None,
                    "submitted_at": submission.submitted_at if submission else None,
                    "time_taken": submission.time_taken if submission else None
                } if user_id else None,
                "created_at": quiz.created_at,
                "updated_at": quiz.updated_at
            }
            quizzes_with_submissions.append(quiz_dict)
        
        logger.info(f"Listed {len(quizzes_with_submissions)} quizzes for user {current_user.get('user_id')}")
        
        return QuizListResponse(
            quizzes=quizzes_with_submissions,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
        
    except Exception as e:
        logger.error(f"Error listing quizzes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quizzes"
        )


@router.get("/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz(
    quiz_id: int,
    request: Request,
    include_questions: bool = Query(False, description="Include questions in response"),
    randomize: bool = Query(False, description="Randomize question order"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    Get detailed quiz information with optional questions
    """
    try:
        # Get quiz with related data
        quiz = db.query(Quiz).options(
            joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Quiz.id == quiz_id).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Check access permissions
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id and quiz.course.subject.school_id != school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this quiz"
                )
        
        # Check if user has already submitted (for non-admin users)
        user_id = current_user.get("user_id")
        latest_submission = None
        if user_id and user_role not in ["admin", "super_admin"]:
            latest_submission = db.query(QuizSubmission).filter(
                QuizSubmission.quiz_id == quiz.id,
                QuizSubmission.user_id == user_id
            ).order_by(QuizSubmission.submitted_at.desc()).first()
        
        # Prepare response
        response_data = {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "quiz_type": quiz.quiz_type,
            "course_id": quiz.course_id,
            "course_name": quiz.course.name,
            "subject_name": quiz.course.subject.name,
            "lesson_id": quiz.lesson_id,
            "time_limit": quiz.time_limit,
            "passing_score": quiz.passing_score,
            "total_questions": quiz.total_questions,
            "question_count": quiz.question_count,
            "order_index": quiz.order_index,
            "instructions": quiz.instructions,
            "randomize_questions": quiz.randomize_questions,
            "show_results_immediately": quiz.show_results_immediately,
            "is_active": quiz.is_active,
            "user_submission": {
                "id": latest_submission.id if latest_submission else None,
                "score": latest_submission.score if latest_submission else None,
                "is_passed": latest_submission.is_passed if latest_submission else None,
                "submitted_at": latest_submission.submitted_at if latest_submission else None,
                "time_taken": latest_submission.time_taken if latest_submission else None,
                "can_retake": quiz.allow_retakes if latest_submission else True
            } if user_id else None,
            "created_at": quiz.created_at,
            "updated_at": quiz.updated_at
        }
        
        # Include questions if requested and user hasn't submitted (or is admin)
        if include_questions and (not latest_submission or user_role in ["admin", "super_admin"]):
            questions = db.query(Question).filter(
                Question.quiz_id == quiz.id,
                Question.is_active == True
            ).order_by(Question.order_index).all()
            
            # Randomize questions if requested and quiz allows it
            if randomize and quiz.randomize_questions:
                import random
                questions = list(questions)
                random.shuffle(questions)
            
            response_data["questions"] = [
                {
                    "id": question.id,
                    "question_text": question.question_text,
                    "question_type": question.question_type,
                    "options": question.options if question.question_type == "multiple_choice" else None,
                    "points": question.points,
                    "order_index": question.order_index,
                    "explanation": question.explanation if user_role in ["admin", "super_admin"] else None
                }
                for question in questions
            ]
        
        logger.info(f"Retrieved quiz {quiz_id} for user {current_user.get('user_id')}")
        
        return QuizDetailResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quiz {quiz_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quiz"
        )


@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    request: Request,
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Create a new quiz (Admin only)
    """
    try:
        # Validate quiz data
        validation_result = validate_quiz_data(quiz_data.dict())
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {', '.join(validation_result['errors'])}"
            )
        
        # Verify course exists and user has access
        course = db.query(Course).options(
            joinedload(Course.subject)
        ).filter(Course.id == quiz_data.course_id).first()
        
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
        
        # Check for duplicate quiz title in course
        existing_quiz = db.query(Quiz).filter(
            Quiz.title == quiz_data.title,
            Quiz.course_id == quiz_data.course_id
        ).first()
        
        if existing_quiz:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Quiz with this title already exists in the course"
            )
        
        # Get next order index if not provided
        if quiz_data.order_index is None:
            max_order = db.query(func.max(Quiz.order_index)).filter(
                Quiz.course_id == quiz_data.course_id
            ).scalar() or 0
            order_index = max_order + 1
        else:
            order_index = quiz_data.order_index
        
        # Create new quiz
        new_quiz = Quiz(
            title=quiz_data.title,
            description=quiz_data.description,
            quiz_type=quiz_data.quiz_type,
            course_id=quiz_data.course_id,
            lesson_id=quiz_data.lesson_id,
            time_limit=quiz_data.time_limit,
            passing_score=quiz_data.passing_score,
            total_questions=quiz_data.total_questions,
            order_index=order_index,
            instructions=quiz_data.instructions,
            randomize_questions=quiz_data.randomize_questions,
            show_results_immediately=quiz_data.show_results_immediately,
            created_by=current_user.get("user_id"),
            is_active=True,
            question_count=0
        )
        
        db.add(new_quiz)
        db.commit()
        db.refresh(new_quiz)
        
        # Update course quiz count
        course.quiz_count = db.query(func.count(Quiz.id)).filter(
            Quiz.course_id == course.id
        ).scalar()
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"quizzes:*")
        invalidate_cache_pattern(f"course:{quiz_data.course_id}:*")
        
        logger.info(f"Created quiz {new_quiz.id} by user {current_user.get('user_id')}")
        
        return QuizResponse(
            id=new_quiz.id,
            title=new_quiz.title,
            description=new_quiz.description,
            quiz_type=new_quiz.quiz_type,
            course_id=new_quiz.course_id,
            lesson_id=new_quiz.lesson_id,
            time_limit=new_quiz.time_limit,
            passing_score=new_quiz.passing_score,
            total_questions=new_quiz.total_questions,
            question_count=new_quiz.question_count,
            order_index=new_quiz.order_index,
            instructions=new_quiz.instructions,
            randomize_questions=new_quiz.randomize_questions,
            show_results_immediately=new_quiz.show_results_immediately,
            is_active=new_quiz.is_active,
            created_at=new_quiz.created_at,
            updated_at=new_quiz.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating quiz: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quiz"
        )


@router.post("/{quiz_id}/submit", response_model=QuizSubmissionResponse)
async def submit_quiz(
    quiz_id: int,
    request: Request,
    submission_data: QuizSubmissionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=5))
):
    """
    Submit quiz answers for grading
    """
    try:
        # Get quiz
        quiz = db.query(Quiz).options(
            joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Quiz.id == quiz_id).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Check access permissions
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id and quiz.course.subject.school_id != school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this quiz"
                )
        
        user_id = current_user.get("user_id")
        
        # Check if user has already submitted and retakes are not allowed
        if not quiz.allow_retakes:
            existing_submission = db.query(QuizSubmission).filter(
                QuizSubmission.quiz_id == quiz_id,
                QuizSubmission.user_id == user_id
            ).first()
            
            if existing_submission:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Quiz already submitted and retakes are not allowed"
                )
        
        # Validate submission data
        if submission_data.quiz_id != quiz_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quiz ID mismatch"
            )
        
        # Create submission record
        new_submission = QuizSubmission(
            quiz_id=quiz_id,
            user_id=user_id,
            answers=submission_data.answers,
            time_taken=submission_data.time_taken,
            submitted_at=datetime.utcnow()
        )
        
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        
        # Grade the submission in background
        background_tasks.add_task(
            grade_quiz_submission,
            new_submission.id,
            quiz_id,
            submission_data.answers
        )
        
        logger.info(f"Quiz {quiz_id} submitted by user {user_id}")
        
        return QuizSubmissionResponse(
            id=new_submission.id,
            quiz_id=new_submission.quiz_id,
            user_id=new_submission.user_id,
            answers=new_submission.answers,
            time_taken=new_submission.time_taken,
            score=new_submission.score,
            is_passed=new_submission.is_passed,
            feedback=new_submission.feedback,
            submitted_at=new_submission.submitted_at,
            created_at=new_submission.created_at,
            updated_at=new_submission.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting quiz {quiz_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit quiz"
        )


@router.post("/{quiz_id}/generate-ai-questions", response_model=Dict[str, Any])
async def generate_ai_quiz_questions(
    quiz_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    topic: str = Query(..., description="Topic for question generation"),
    num_questions: int = Query(5, ge=1, le=20, description="Number of questions to generate"),
    difficulty: str = Query("intermediate", description="Difficulty level"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=2))
):
    """
    Generate AI-powered quiz questions (Admin only)
    """
    try:
        # Get quiz
        quiz = db.query(Quiz).options(
            joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Quiz.id == quiz_id).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        # Check school access
        if quiz.course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this quiz"
            )
        
        # Generate questions in background
        background_tasks.add_task(
            generate_quiz_questions,
            quiz_id,
            topic,
            num_questions,
            difficulty,
            current_user.get("user_id")
        )
        
        logger.info(f"AI question generation started for quiz {quiz_id} by user {current_user.get('user_id')}")
        
        return {
            "message": "AI question generation started",
            "quiz_id": quiz_id,
            "topic": topic,
            "num_questions": num_questions,
            "difficulty": difficulty,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting AI question generation for quiz {quiz_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start AI question generation"
        )
