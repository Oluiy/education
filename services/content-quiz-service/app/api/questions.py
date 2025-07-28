"""
Questions API Router
Comprehensive question management for quizzes with various question types
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, File, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc

from ..database import get_db
from ..models.content_models import Quiz, Question, Course, Subject
from ..schemas.content_schemas import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionListResponse, QuestionBulkCreate,
    QuestionImportResponse
)
from ..core.security import get_current_user_token, require_admin_role, rate_limit_check
from ..utils.pagination import paginate_query
from ..utils.cache import cache_result, invalidate_cache_pattern
from ..utils.validators import validate_question_data
from ..utils.file_handler import process_question_import_file

import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=QuestionListResponse)
async def list_questions(
    request: Request,
    quiz_id: int = Query(..., description="Quiz ID to get questions for"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    question_type: Optional[str] = Query(None, description="Filter by question type"),
    search: Optional[str] = Query(None, description="Search in question text"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: str = Query("order_index", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    List questions for a specific quiz
    """
    try:
        # Get quiz and verify access
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
        
        # Build query
        query = db.query(Question).filter(Question.quiz_id == quiz_id)
        
        # Apply filters
        if question_type:
            query = query.filter(Question.question_type == question_type)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                func.lower(Question.question_text).like(search_term)
            )
        
        if is_active is not None:
            query = query.filter(Question.is_active == is_active)
        
        # Apply sorting
        sort_column = getattr(Question, sort_by, Question.order_index)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Get paginated results
        result = paginate_query(query, page, page_size)
        
        # Prepare response
        questions = [
            {
                "id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "options": question.options,
                "correct_answer": question.correct_answer if user_role in ["admin", "super_admin"] else None,
                "points": question.points,
                "order_index": question.order_index,
                "explanation": question.explanation,
                "difficulty": question.difficulty,
                "tags": question.tags,
                "is_active": question.is_active,
                "created_at": question.created_at,
                "updated_at": question.updated_at
            }
            for question in result["items"]
        ]
        
        logger.info(f"Listed {len(questions)} questions for quiz {quiz_id}")
        
        return QuestionListResponse(
            questions=questions,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing questions for quiz {quiz_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve questions"
        )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    request: Request,
    include_answer: bool = Query(False, description="Include correct answer (admin only)"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    Get a specific question by ID
    """
    try:
        # Get question with quiz and course data
        question = db.query(Question).options(
            joinedload(Question.quiz).joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Question.id == question_id).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Check access permissions
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id and question.quiz.course.subject.school_id != school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this question"
                )
        
        # Prepare response
        response_data = {
            "id": question.id,
            "quiz_id": question.quiz_id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "options": question.options,
            "points": question.points,
            "order_index": question.order_index,
            "explanation": question.explanation,
            "difficulty": question.difficulty,
            "tags": question.tags,
            "is_active": question.is_active,
            "created_at": question.created_at,
            "updated_at": question.updated_at
        }
        
        # Include correct answer if admin or specifically requested by admin
        if include_answer and user_role in ["admin", "super_admin"]:
            response_data["correct_answer"] = question.correct_answer
        
        logger.info(f"Retrieved question {question_id} for user {current_user.get('user_id')}")
        
        return QuestionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving question {question_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve question"
        )


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    request: Request,
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Create a new question (Admin only)
    """
    try:
        # Validate question data
        validation_result = validate_question_data(question_data.dict())
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {', '.join(validation_result['errors'])}"
            )
        
        # Verify quiz exists and user has access
        quiz = db.query(Quiz).options(
            joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Quiz.id == question_data.quiz_id).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        if quiz.course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this quiz"
            )
        
        # Get next order index if not provided
        if question_data.order_index is None:
            max_order = db.query(func.max(Question.order_index)).filter(
                Question.quiz_id == question_data.quiz_id
            ).scalar() or 0
            order_index = max_order + 1
        else:
            order_index = question_data.order_index
        
        # Create new question
        new_question = Question(
            quiz_id=question_data.quiz_id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            points=question_data.points,
            order_index=order_index,
            explanation=question_data.explanation,
            difficulty=question_data.difficulty,
            tags=question_data.tags,
            created_by=current_user.get("user_id"),
            is_active=True
        )
        
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        
        # Update quiz question count
        quiz.question_count = db.query(func.count(Question.id)).filter(
            Question.quiz_id == quiz.id,
            Question.is_active == True
        ).scalar()
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"quiz:{question_data.quiz_id}:*")
        invalidate_cache_pattern(f"questions:*")
        
        logger.info(f"Created question {new_question.id} by user {current_user.get('user_id')}")
        
        return QuestionResponse(
            id=new_question.id,
            quiz_id=new_question.quiz_id,
            question_text=new_question.question_text,
            question_type=new_question.question_type,
            options=new_question.options,
            correct_answer=new_question.correct_answer,
            points=new_question.points,
            order_index=new_question.order_index,
            explanation=new_question.explanation,
            difficulty=new_question.difficulty,
            tags=new_question.tags,
            is_active=new_question.is_active,
            created_at=new_question.created_at,
            updated_at=new_question.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating question: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create question"
        )


@router.post("/bulk", response_model=List[QuestionResponse])
async def create_questions_bulk(
    request: Request,
    bulk_data: QuestionBulkCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=5))
):
    """
    Create multiple questions in bulk (Admin only)
    """
    try:
        # Verify quiz exists and user has access
        quiz = db.query(Quiz).options(
            joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Quiz.id == bulk_data.quiz_id).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        if quiz.course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this quiz"
            )
        
        # Validate all questions
        for i, question_data in enumerate(bulk_data.questions):
            validation_result = validate_question_data(question_data.dict())
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question {i+1} validation failed: {', '.join(validation_result['errors'])}"
                )
        
        # Get starting order index
        max_order = db.query(func.max(Question.order_index)).filter(
            Question.quiz_id == bulk_data.quiz_id
        ).scalar() or 0
        
        # Create all questions
        created_questions = []
        for i, question_data in enumerate(bulk_data.questions):
            new_question = Question(
                quiz_id=bulk_data.quiz_id,
                question_text=question_data.question_text,
                question_type=question_data.question_type,
                options=question_data.options,
                correct_answer=question_data.correct_answer,
                points=question_data.points,
                order_index=max_order + i + 1,
                explanation=question_data.explanation,
                difficulty=question_data.difficulty,
                tags=question_data.tags,
                created_by=current_user.get("user_id"),
                is_active=True
            )
            
            db.add(new_question)
            created_questions.append(new_question)
        
        db.commit()
        
        # Update quiz question count
        quiz.question_count = db.query(func.count(Question.id)).filter(
            Question.quiz_id == quiz.id,
            Question.is_active == True
        ).scalar()
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"quiz:{bulk_data.quiz_id}:*")
        invalidate_cache_pattern(f"questions:*")
        
        logger.info(f"Created {len(created_questions)} questions in bulk by user {current_user.get('user_id')}")
        
        return [
            QuestionResponse(
                id=question.id,
                quiz_id=question.quiz_id,
                question_text=question.question_text,
                question_type=question.question_type,
                options=question.options,
                correct_answer=question.correct_answer,
                points=question.points,
                order_index=question.order_index,
                explanation=question.explanation,
                difficulty=question.difficulty,
                tags=question.tags,
                is_active=question.is_active,
                created_at=question.created_at,
                updated_at=question.updated_at
            )
            for question in created_questions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating questions in bulk: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create questions in bulk"
        )


@router.post("/import", response_model=QuestionImportResponse)
async def import_questions(
    request: Request,
    quiz_id: int,
    file: UploadFile = File(...),
    format_type: str = Query("json", description="Import format: json, csv, xlsx"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=2))
):
    """
    Import questions from file (Admin only)
    """
    try:
        # Verify quiz exists and user has access
        quiz = db.query(Quiz).options(
            joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Quiz.id == quiz_id).first()
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        if quiz.course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this quiz"
            )
        
        # Validate file type
        if format_type not in ["json", "csv", "xlsx"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported format type"
            )
        
        # Process the import file
        result = await process_question_import_file(
            file, format_type, quiz_id, current_user.get("user_id"), db
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Import failed: {result['error']}"
            )
        
        # Update quiz question count
        quiz.question_count = db.query(func.count(Question.id)).filter(
            Question.quiz_id == quiz.id,
            Question.is_active == True
        ).scalar()
        db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"quiz:{quiz_id}:*")
        invalidate_cache_pattern(f"questions:*")
        
        logger.info(f"Imported {result['imported_count']} questions for quiz {quiz_id} by user {current_user.get('user_id')}")
        
        return QuestionImportResponse(
            imported_count=result["imported_count"],
            skipped_count=result["skipped_count"],
            error_count=result["error_count"],
            errors=result["errors"],
            success=result["success"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing questions for quiz {quiz_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to import questions"
        )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    request: Request,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Update an existing question (Admin only)
    """
    try:
        # Get existing question
        question = db.query(Question).options(
            joinedload(Question.quiz).joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Question.id == question_id).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Check access permissions
        if question.quiz.course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this question"
            )
        
        # Validate question data if provided
        if hasattr(question_data, 'question_text') and question_data.question_text is not None:
            validation_result = validate_question_data(question_data.dict(exclude_unset=True))
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Validation failed: {', '.join(validation_result['errors'])}"
                )
        
        # Update question fields
        update_data = question_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(question, field):
                setattr(question, field, value)
        
        question.updated_at = datetime.utcnow()
        question.updated_by = current_user.get("user_id")
        
        db.commit()
        db.refresh(question)
        
        # Invalidate related caches
        invalidate_cache_pattern(f"quiz:{question.quiz_id}:*")
        invalidate_cache_pattern(f"questions:*")
        
        logger.info(f"Updated question {question_id} by user {current_user.get('user_id')}")
        
        return QuestionResponse(
            id=question.id,
            quiz_id=question.quiz_id,
            question_text=question.question_text,
            question_type=question.question_type,
            options=question.options,
            correct_answer=question.correct_answer,
            points=question.points,
            order_index=question.order_index,
            explanation=question.explanation,
            difficulty=question.difficulty,
            tags=question.tags,
            is_active=question.is_active,
            created_at=question.created_at,
            updated_at=question.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating question {question_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update question"
        )


@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=10))
):
    """
    Delete a question (Admin only)
    """
    try:
        # Get question
        question = db.query(Question).options(
            joinedload(Question.quiz).joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(Question.id == question_id).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        # Check access permissions
        if question.quiz.course.subject.school_id != current_user.get("school_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this question"
            )
        
        quiz_id = question.quiz_id
        
        # Soft delete (mark as inactive)
        question.is_active = False
        question.updated_at = datetime.utcnow()
        question.updated_by = current_user.get("user_id")
        
        db.commit()
        
        # Update quiz question count
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if quiz:
            quiz.question_count = db.query(func.count(Question.id)).filter(
                Question.quiz_id == quiz.id,
                Question.is_active == True
            ).scalar()
            db.commit()
        
        # Invalidate related caches
        invalidate_cache_pattern(f"quiz:{quiz_id}:*")
        invalidate_cache_pattern(f"questions:*")
        
        logger.info(f"Deleted question {question_id} by user {current_user.get('user_id')}")
        
        return {"message": "Question deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question {question_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete question"
        )
