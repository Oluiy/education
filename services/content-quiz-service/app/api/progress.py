"""
Progress API Router
User progress tracking for quizzes and content completion
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc

from ..database import get_db
from ..models.progress_models import QuizProgress, CourseProgress, LessonProgress
from ..models.content_models import Quiz, Course, Lesson, Subject
from ..schemas.progress_schemas import (
    QuizProgressResponse, CourseProgressResponse, LessonProgressResponse,
    ProgressSummaryResponse, ProgressStatsResponse
)
from ..core.security import get_current_user_token, require_admin_role, rate_limit_check
from ..utils.pagination import paginate_query
from ..utils.cache import cache_result, invalidate_cache_pattern

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/quiz/{quiz_id}", response_model=QuizProgressResponse)
async def get_quiz_progress(
    quiz_id: int,
    request: Request,
    user_id: Optional[int] = Query(None, description="User ID (admin only)"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    Get quiz progress for a user
    """
    try:
        # Determine which user's progress to get
        target_user_id = user_id if user_id and current_user.get("role") in ["admin", "super_admin"] else current_user.get("user_id")
        
        if not target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID required"
            )
        
        # Get quiz progress
        progress = db.query(QuizProgress).options(
            joinedload(QuizProgress.quiz).joinedload(Quiz.course).joinedload(Course.subject)
        ).filter(
            QuizProgress.user_id == target_user_id,
            QuizProgress.quiz_id == quiz_id
        ).first()
        
        if not progress:
            # Check if quiz exists
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
            
            # Return empty progress
            return QuizProgressResponse(
                user_id=target_user_id,
                quiz_id=quiz_id,
                quiz_title=quiz.title,
                course_id=quiz.course_id,
                course_name=quiz.course.name,
                subject_name=quiz.course.subject.name,
                status="not_started",
                score=None,
                max_score=None,
                percentage=None,
                is_passed=False,
                attempts=0,
                time_spent=0,
                started_at=None,
                completed_at=None,
                created_at=None,
                updated_at=None
            )
        
        # Check access permissions
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id and progress.quiz.course.subject.school_id != school_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this quiz progress"
                )
        
        logger.info(f"Retrieved quiz progress for quiz {quiz_id}, user {target_user_id}")
        
        return QuizProgressResponse(
            user_id=progress.user_id,
            quiz_id=progress.quiz_id,
            quiz_title=progress.quiz.title,
            course_id=progress.course_id,
            course_name=progress.quiz.course.name,
            subject_name=progress.quiz.course.subject.name,
            status=progress.status,
            score=progress.score,
            max_score=progress.max_score,
            percentage=progress.percentage,
            is_passed=progress.is_passed,
            attempts=progress.attempts,
            time_spent=progress.time_spent,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            created_at=progress.created_at,
            updated_at=progress.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quiz progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quiz progress"
        )


@router.get("/course/{course_id}", response_model=CourseProgressResponse)
async def get_course_progress(
    course_id: int,
    request: Request,
    user_id: Optional[int] = Query(None, description="User ID (admin only)"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=100))
):
    """
    Get course progress for a user including all lessons and quizzes
    """
    try:
        # Determine which user's progress to get
        target_user_id = user_id if user_id and current_user.get("role") in ["admin", "super_admin"] else current_user.get("user_id")
        
        if not target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID required"
            )
        
        # Get course
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
        
        # Get course progress
        progress = db.query(CourseProgress).filter(
            CourseProgress.user_id == target_user_id,
            CourseProgress.course_id == course_id
        ).first()
        
        # Get lesson progress
        lesson_progress = db.query(LessonProgress).options(
            joinedload(LessonProgress.lesson)
        ).filter(
            LessonProgress.user_id == target_user_id,
            LessonProgress.course_id == course_id
        ).all()
        
        # Get quiz progress
        quiz_progress = db.query(QuizProgress).options(
            joinedload(QuizProgress.quiz)
        ).filter(
            QuizProgress.user_id == target_user_id,
            QuizProgress.course_id == course_id
        ).all()
        
        # Calculate overall progress
        total_lessons = db.query(func.count(Lesson.id)).filter(
            Lesson.course_id == course_id,
            Lesson.is_active == True
        ).scalar()
        
        total_quizzes = db.query(func.count(Quiz.id)).filter(
            Quiz.course_id == course_id,
            Quiz.is_active == True
        ).scalar()
        
        completed_lessons = len([lp for lp in lesson_progress if lp.status == "completed"])
        completed_quizzes = len([qp for qp in quiz_progress if qp.status == "completed"])
        
        total_items = total_lessons + total_quizzes
        completed_items = completed_lessons + completed_quizzes
        completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0
        
        # Determine overall status
        if completion_percentage == 100:
            overall_status = "completed"
        elif completion_percentage > 0:
            overall_status = "in_progress"
        else:
            overall_status = "not_started"
        
        # Calculate time spent
        total_time_spent = sum(lp.time_spent or 0 for lp in lesson_progress) + sum(qp.time_spent or 0 for qp in quiz_progress)
        
        logger.info(f"Retrieved course progress for course {course_id}, user {target_user_id}")
        
        return CourseProgressResponse(
            user_id=target_user_id,
            course_id=course_id,
            course_name=course.name,
            subject_name=course.subject.name,
            status=overall_status,
            completion_percentage=round(completion_percentage, 2),
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            total_quizzes=total_quizzes,
            completed_quizzes=completed_quizzes,
            time_spent=total_time_spent,
            lesson_progress=[
                {
                    "lesson_id": lp.lesson_id,
                    "lesson_title": lp.lesson.title,
                    "status": lp.status,
                    "completion_percentage": lp.completion_percentage,
                    "time_spent": lp.time_spent,
                    "completed_at": lp.completed_at
                }
                for lp in lesson_progress
            ],
            quiz_progress=[
                {
                    "quiz_id": qp.quiz_id,
                    "quiz_title": qp.quiz.title,
                    "status": qp.status,
                    "score": qp.score,
                    "percentage": qp.percentage,
                    "is_passed": qp.is_passed,
                    "attempts": qp.attempts,
                    "completed_at": qp.completed_at
                }
                for qp in quiz_progress
            ],
            started_at=progress.started_at if progress else None,
            completed_at=progress.completed_at if progress else None,
            created_at=progress.created_at if progress else None,
            updated_at=progress.updated_at if progress else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving course progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve course progress"
        )


@router.get("/summary", response_model=ProgressSummaryResponse)
async def get_progress_summary(
    request: Request,
    user_id: Optional[int] = Query(None, description="User ID (admin only)"),
    subject_id: Optional[int] = Query(None, description="Filter by subject"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user_token),
    _: None = Depends(lambda r: rate_limit_check(r, limit=50))
):
    """
    Get comprehensive progress summary for a user
    """
    try:
        # Determine which user's progress to get
        target_user_id = user_id if user_id and current_user.get("role") in ["admin", "super_admin"] else current_user.get("user_id")
        
        if not target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID required"
            )
        
        # Build base queries
        course_query = db.query(Course).join(Subject)
        lesson_query = db.query(Lesson).join(Course).join(Subject)
        quiz_query = db.query(Quiz).join(Course).join(Subject)
        
        # Apply school isolation (if not admin)
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            school_id = current_user.get("school_id")
            if school_id:
                course_query = course_query.filter(Subject.school_id == school_id)
                lesson_query = lesson_query.filter(Subject.school_id == school_id)
                quiz_query = quiz_query.filter(Subject.school_id == school_id)
        
        # Apply subject filter
        if subject_id:
            course_query = course_query.filter(Subject.id == subject_id)
            lesson_query = lesson_query.filter(Subject.id == subject_id)
            quiz_query = quiz_query.filter(Subject.id == subject_id)
        
        # Get totals
        total_courses = course_query.filter(Course.is_active == True).count()
        total_lessons = lesson_query.filter(Lesson.is_active == True).count()
        total_quizzes = quiz_query.filter(Quiz.is_active == True).count()
        
        # Get completed counts
        completed_courses = db.query(func.count(CourseProgress.id)).filter(
            CourseProgress.user_id == target_user_id,
            CourseProgress.status == "completed"
        ).scalar()
        
        completed_lessons = db.query(func.count(LessonProgress.id)).filter(
            LessonProgress.user_id == target_user_id,
            LessonProgress.status == "completed"
        ).scalar()
        
        completed_quizzes = db.query(func.count(QuizProgress.id)).filter(
            QuizProgress.user_id == target_user_id,
            QuizProgress.status == "completed"
        ).scalar()
        
        # Get in progress counts
        in_progress_courses = db.query(func.count(CourseProgress.id)).filter(
            CourseProgress.user_id == target_user_id,
            CourseProgress.status == "in_progress"
        ).scalar()
        
        in_progress_lessons = db.query(func.count(LessonProgress.id)).filter(
            LessonProgress.user_id == target_user_id,
            LessonProgress.status == "in_progress"
        ).scalar()
        
        # Calculate percentages
        course_completion_rate = (completed_courses / total_courses * 100) if total_courses > 0 else 0
        lesson_completion_rate = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        quiz_completion_rate = (completed_quizzes / total_quizzes * 100) if total_quizzes > 0 else 0
        
        # Get total time spent
        total_time_lessons = db.query(func.sum(LessonProgress.time_spent)).filter(
            LessonProgress.user_id == target_user_id
        ).scalar() or 0
        
        total_time_quizzes = db.query(func.sum(QuizProgress.time_spent)).filter(
            QuizProgress.user_id == target_user_id
        ).scalar() or 0
        
        total_time_spent = total_time_lessons + total_time_quizzes
        
        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_lesson_completions = db.query(func.count(LessonProgress.id)).filter(
            LessonProgress.user_id == target_user_id,
            LessonProgress.completed_at >= week_ago
        ).scalar()
        
        recent_quiz_completions = db.query(func.count(QuizProgress.id)).filter(
            QuizProgress.user_id == target_user_id,
            QuizProgress.completed_at >= week_ago
        ).scalar()
        
        # Get average quiz scores
        avg_quiz_score = db.query(func.avg(QuizProgress.percentage)).filter(
            QuizProgress.user_id == target_user_id,
            QuizProgress.status == "completed"
        ).scalar() or 0
        
        logger.info(f"Retrieved progress summary for user {target_user_id}")
        
        return ProgressSummaryResponse(
            user_id=target_user_id,
            total_courses=total_courses,
            completed_courses=completed_courses,
            in_progress_courses=in_progress_courses,
            course_completion_rate=round(course_completion_rate, 2),
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            in_progress_lessons=in_progress_lessons,
            lesson_completion_rate=round(lesson_completion_rate, 2),
            total_quizzes=total_quizzes,
            completed_quizzes=completed_quizzes,
            quiz_completion_rate=round(quiz_completion_rate, 2),
            total_time_spent=total_time_spent,
            recent_lesson_completions=recent_lesson_completions,
            recent_quiz_completions=recent_quiz_completions,
            average_quiz_score=round(avg_quiz_score, 2),
            last_activity=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving progress summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress summary"
        )


@router.get("/stats", response_model=ProgressStatsResponse)
async def get_progress_stats(
    request: Request,
    subject_id: Optional[int] = Query(None, description="Filter by subject"),
    course_id: Optional[int] = Query(None, description="Filter by course"),
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role),
    _: None = Depends(lambda r: rate_limit_check(r, limit=20))
):
    """
    Get detailed progress statistics (Admin only)
    """
    try:
        school_id = current_user.get("school_id")
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build base query with school isolation
        base_filter = []
        if school_id:
            base_filter.append(Subject.school_id == school_id)
        
        if subject_id:
            base_filter.append(Subject.id == subject_id)
        
        if course_id:
            base_filter.append(Course.id == course_id)
        
        # Get completion stats
        lesson_completions = db.query(
            func.date(LessonProgress.completed_at).label('date'),
            func.count(LessonProgress.id).label('count')
        ).join(Lesson).join(Course).join(Subject).filter(
            LessonProgress.completed_at >= start_date,
            LessonProgress.status == "completed",
            *base_filter
        ).group_by(func.date(LessonProgress.completed_at)).all()
        
        quiz_completions = db.query(
            func.date(QuizProgress.completed_at).label('date'),
            func.count(QuizProgress.id).label('count')
        ).join(Quiz).join(Course).join(Subject).filter(
            QuizProgress.completed_at >= start_date,
            QuizProgress.status == "completed",
            *base_filter
        ).group_by(func.date(QuizProgress.completed_at)).all()
        
        # Get average scores by subject
        subject_scores = db.query(
            Subject.name.label('subject_name'),
            func.avg(QuizProgress.percentage).label('avg_score'),
            func.count(QuizProgress.id).label('quiz_count')
        ).join(Course).join(Quiz).join(QuizProgress).filter(
            QuizProgress.status == "completed",
            QuizProgress.completed_at >= start_date,
            *base_filter
        ).group_by(Subject.name).all()
        
        # Get top performing students
        top_students = db.query(
            QuizProgress.user_id,
            func.avg(QuizProgress.percentage).label('avg_score'),
            func.count(QuizProgress.id).label('quiz_count')
        ).join(Quiz).join(Course).join(Subject).filter(
            QuizProgress.status == "completed",
            QuizProgress.completed_at >= start_date,
            *base_filter
        ).group_by(QuizProgress.user_id).order_by(
            func.avg(QuizProgress.percentage).desc()
        ).limit(10).all()
        
        # Get course completion rates
        course_stats = db.query(
            Course.name.label('course_name'),
            Course.id.label('course_id'),
            func.count(CourseProgress.id.distinct()).label('enrolled_count'),
            func.sum(func.case([(CourseProgress.status == 'completed', 1)], else_=0)).label('completed_count')
        ).outerjoin(CourseProgress).join(Subject).filter(
            Course.is_active == True,
            *base_filter
        ).group_by(Course.id, Course.name).all()
        
        logger.info(f"Retrieved progress stats for school {school_id}")
        
        return ProgressStatsResponse(
            period_days=days,
            total_lesson_completions=sum(lc.count for lc in lesson_completions),
            total_quiz_completions=sum(qc.count for qc in quiz_completions),
            daily_lesson_completions={str(lc.date): lc.count for lc in lesson_completions},
            daily_quiz_completions={str(qc.date): qc.count for qc in quiz_completions},
            subject_performance=[
                {
                    "subject_name": ss.subject_name,
                    "average_score": round(float(ss.avg_score), 2),
                    "quiz_count": ss.quiz_count
                }
                for ss in subject_scores
            ],
            top_students=[
                {
                    "user_id": ts.user_id,
                    "average_score": round(float(ts.avg_score), 2),
                    "quiz_count": ts.quiz_count
                }
                for ts in top_students
            ],
            course_completion_rates=[
                {
                    "course_id": cs.course_id,
                    "course_name": cs.course_name,
                    "enrolled_count": cs.enrolled_count or 0,
                    "completed_count": int(cs.completed_count or 0),
                    "completion_rate": round((int(cs.completed_count or 0) / (cs.enrolled_count or 1)) * 100, 2) if cs.enrolled_count else 0
                }
                for cs in course_stats
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving progress stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress statistics"
        )
