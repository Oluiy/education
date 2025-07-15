"""
EduNerve Content & Quiz Service - API Routes
Content management and quiz generation endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.database import get_db
from app.models import Content, Quiz, Submission, Grade, ContentStats, QuizAttempt, Course, Lesson, CourseEnrollment, LessonProgress
from app.schemas import (
    ContentCreate, ContentResponse, ContentUpdate, QuizCreate, QuizResponse,
    QuizUpdate, AIQuizRequest, AIQuizResponse, SubmissionCreate, SubmissionResponse,
    MessageResponse, ErrorResponse, QuizStats, ContentStats as ContentStatsSchema,
    FileUploadResponse, QuizQuestion, CourseCreate, CourseResponse, CourseUpdate,
    CourseWithStats, LessonCreate, LessonResponse, LessonUpdate, EnrollmentCreate,
    EnrollmentResponse, ProgressUpdate, ProgressResponse, CourseProgressResponse
)
from app.auth import (
    get_current_user, get_current_active_user, get_current_teacher_user,
    get_current_admin_user, check_school_access, check_content_access,
    check_quiz_access, get_current_teacher, get_current_student, CurrentUser
)
from app.ai_service import quiz_generator, ai_grader, extract_keywords_from_text, summarize_content
from app.file_utils import process_content_file, text_extractor, FileUploadError
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Common exceptions
content_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Content not found"
)

quiz_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Quiz not found"
)

submission_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Submission not found"
)


# Content Management Routes
@router.post("/content/upload", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def upload_content(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    subject: str = Form(...),
    class_level: str = Form(...),
    topic: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None),
    is_public: bool = Form(False),
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Upload content file (PDF, text, etc.) and create content record
    """
    try:
        # Process file upload
        upload_result = await process_content_file(file, current_user.school_id)
        
        # Extract keywords if not provided
        content_keywords = []
        if keywords:
            content_keywords = [k.strip() for k in keywords.split(",")]
        elif upload_result.get("content_text"):
            content_keywords = extract_keywords_from_text(upload_result["content_text"])
        
        # Create content record
        content = Content(
            title=title,
            description=description,
            content_type=upload_result["content_type"],
            file_path=upload_result["local_path"],
            file_url=upload_result.get("cloud_url"),
            file_size=upload_result["file_size"],
            file_hash=upload_result["file_hash"],
            subject=subject,
            class_level=class_level,
            topic=topic,
            keywords=json.dumps(content_keywords) if content_keywords else None,
            school_id=current_user.school_id,
            uploaded_by=current_user.id,
            content_text=upload_result.get("content_text"),
            is_public=is_public
        )
        
        db.add(content)
        db.commit()
        db.refresh(content)
        
        # Create content stats record
        stats = ContentStats(
            content_id=content.id,
            school_id=current_user.school_id
        )
        db.add(stats)
        db.commit()
        
        logger.info(f"Content uploaded successfully: {content.id}")
        return content
        
    except FileUploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload content"
        )


@router.get("/content", response_model=List[ContentResponse])
async def get_content_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    subject: Optional[str] = Query(None),
    class_level: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    include_public: bool = Query(True),
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of content with filtering and search
    """
    query = db.query(Content).filter(Content.is_active == True)
    
    # Filter by school or include public content
    if include_public:
        query = query.filter(
            or_(
                Content.school_id == current_user.school_id,
                Content.is_public == True
            )
        )
    else:
        query = query.filter(Content.school_id == current_user.school_id)
    
    # Apply filters
    if subject:
        query = query.filter(Content.subject.ilike(f"%{subject}%"))
    
    if class_level:
        query = query.filter(Content.class_level == class_level)
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    if search:
        query = query.filter(
            or_(
                Content.title.ilike(f"%{search}%"),
                Content.description.ilike(f"%{search}%"),
                Content.topic.ilike(f"%{search}%")
            )
        )
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Content.created_at))
    
    # Pagination
    content_list = query.offset(skip).limit(limit).all()
    
    return content_list


@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific content by ID
    """
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.is_active == True
    ).first()
    
    if not content:
        raise content_not_found
    
    # Check access permissions
    check_content_access(current_user, content.school_id, content.is_public)
    
    # Update view count
    stats = db.query(ContentStats).filter(
        ContentStats.content_id == content_id,
        ContentStats.school_id == current_user.school_id
    ).first()
    
    if stats:
        stats.view_count += 1
        stats.last_accessed = datetime.utcnow()
        db.commit()
    
    return content


@router.put("/content/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_update: ContentUpdate,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Update content metadata
    """
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.school_id == current_user.school_id,
        Content.is_active == True
    ).first()
    
    if not content:
        raise content_not_found
    
    # Check if user can modify this content
    if content.uploaded_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own content"
        )
    
    # Update fields
    update_data = content_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "keywords" and value:
            # Convert keywords list to JSON string
            setattr(content, field, json.dumps(value))
        else:
            setattr(content, field, value)
    
    content.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(content)
    
    return content


@router.delete("/content/{content_id}", response_model=MessageResponse)
async def delete_content(
    content_id: int,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Delete content (soft delete)
    """
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.school_id == current_user.school_id,
        Content.is_active == True
    ).first()
    
    if not content:
        raise content_not_found
    
    # Check permissions
    if content.uploaded_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own content"
        )
    
    # Soft delete
    content.is_active = False
    content.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Content deleted successfully")


# Quiz Management Routes
@router.post("/quiz/create_manual", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_manual_quiz(
    quiz_data: QuizCreate,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Create quiz manually with provided questions
    """
    # Validate content access if content_id is provided
    if quiz_data.content_id:
        content = db.query(Content).filter(
            Content.id == quiz_data.content_id,
            Content.is_active == True
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated content not found"
            )
        
        check_content_access(current_user, content.school_id, content.is_public)
    
    # Calculate total questions and marks
    total_questions = len(quiz_data.questions)
    total_marks = sum(q.marks for q in quiz_data.questions)
    
    # Create quiz
    quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        quiz_type=quiz_data.quiz_type,
        difficulty_level=quiz_data.difficulty_level,
        total_questions=total_questions,
        duration_minutes=quiz_data.duration_minutes,
        subject=quiz_data.subject,
        class_level=quiz_data.class_level,
        topic=quiz_data.topic,
        school_id=current_user.school_id,
        created_by=current_user.id,
        content_id=quiz_data.content_id,
        questions=json.dumps([q.dict() for q in quiz_data.questions]),
        total_marks=total_marks,
        pass_mark=quiz_data.pass_mark,
        is_ai_generated=False
    )
    
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    logger.info(f"Manual quiz created: {quiz.id}")
    return quiz


@router.post("/quiz/generate_ai", response_model=AIQuizResponse)
async def generate_ai_quiz(
    quiz_request: AIQuizRequest,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Generate quiz using AI based on content
    """
    content_text = quiz_request.content_text
    
    # If content_id is provided, get content text
    if quiz_request.content_id:
        content = db.query(Content).filter(
            Content.id == quiz_request.content_id,
            Content.is_active == True
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        check_content_access(current_user, content.school_id, content.is_public)
        
        # Use stored content text or extract from file
        if content.content_text:
            content_text = content.content_text
        elif content.file_path:
            content_text = text_extractor.extract_text(content.file_path)
        
        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content available for quiz generation"
            )
    
    if not content_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content text is required for AI quiz generation"
        )
    
    try:
        # Generate quiz using AI
        questions, generation_prompt = quiz_generator.generate_quiz(
            content_text=content_text,
            subject=quiz_request.subject,
            class_level=quiz_request.class_level,
            topic=quiz_request.topic,
            difficulty_level=quiz_request.difficulty_level,
            quiz_type=quiz_request.quiz_type,
            num_questions=quiz_request.num_questions
        )
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate questions"
            )
        
        # Calculate total marks
        total_marks = sum(q.marks for q in questions)
        
        # Create quiz title
        quiz_title = f"AI-Generated {quiz_request.subject} Quiz - {quiz_request.class_level}"
        if quiz_request.topic:
            quiz_title += f" ({quiz_request.topic})"
        
        # Create quiz record
        quiz = Quiz(
            title=quiz_title,
            description=f"Auto-generated quiz based on uploaded content",
            quiz_type=quiz_request.quiz_type,
            difficulty_level=quiz_request.difficulty_level,
            total_questions=len(questions),
            duration_minutes=quiz_request.duration_minutes,
            subject=quiz_request.subject,
            class_level=quiz_request.class_level,
            topic=quiz_request.topic,
            school_id=current_user.school_id,
            created_by=current_user.id,
            content_id=quiz_request.content_id,
            questions=json.dumps([q.dict() for q in questions]),
            total_marks=total_marks,
            pass_mark=50.0,  # Default pass mark
            is_ai_generated=True,
            ai_prompt=generation_prompt,
            generation_model=quiz_generator.model
        )
        
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
        # Update content stats if content was used
        if quiz_request.content_id:
            stats = db.query(ContentStats).filter(
                ContentStats.content_id == quiz_request.content_id,
                ContentStats.school_id == current_user.school_id
            ).first()
            
            if stats:
                stats.quiz_generation_count += 1
                db.commit()
        
        logger.info(f"AI quiz generated: {quiz.id}")
        
        return AIQuizResponse(
            quiz_id=quiz.id,
            generation_prompt=generation_prompt,
            generated_questions=questions,
            total_questions=len(questions),
            total_marks=total_marks,
            generation_model=quiz_generator.model
        )
        
    except Exception as e:
        logger.error(f"Error generating AI quiz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )


@router.get("/quiz", response_model=List[QuizResponse])
async def get_quiz_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    subject: Optional[str] = Query(None),
    class_level: Optional[str] = Query(None),
    quiz_type: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get list of quizzes with filtering
    """
    query = db.query(Quiz).filter(
        Quiz.school_id == current_user.school_id,
        Quiz.is_active == True
    )
    
    # Apply filters
    if subject:
        query = query.filter(Quiz.subject.ilike(f"%{subject}%"))
    
    if class_level:
        query = query.filter(Quiz.class_level == class_level)
    
    if quiz_type:
        query = query.filter(Quiz.quiz_type == quiz_type)
    
    if is_published is not None:
        query = query.filter(Quiz.is_published == is_published)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Quiz.created_at))
    
    # Pagination
    quizzes = query.offset(skip).limit(limit).all()
    
    return quizzes


@router.get("/quiz/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific quiz by ID
    """
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.is_active == True
    ).first()
    
    if not quiz:
        raise quiz_not_found
    
    # Check access permissions
    check_quiz_access(current_user, quiz.school_id)
    
    # Students can only access published quizzes
    if current_user.is_student and not quiz.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quiz is not published"
        )
    
    return quiz


@router.put("/quiz/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: int,
    quiz_update: QuizUpdate,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Update quiz metadata
    """
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.school_id == current_user.school_id,
        Quiz.is_active == True
    ).first()
    
    if not quiz:
        raise quiz_not_found
    
    # Check permissions
    if quiz.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own quizzes"
        )
    
    # Update fields
    update_data = quiz_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)
    
    quiz.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(quiz)
    
    return quiz


@router.delete("/quiz/{quiz_id}", response_model=MessageResponse)
async def delete_quiz(
    quiz_id: int,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Delete quiz (soft delete)
    """
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.school_id == current_user.school_id,
        Quiz.is_active == True
    ).first()
    
    if not quiz:
        raise quiz_not_found
    
    # Check permissions
    if quiz.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own quizzes"
        )
    
    # Soft delete
    quiz.is_active = False
    quiz.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Quiz deleted successfully")


# Course Management Routes
@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """Create a new course"""
    try:
        # Create course
        db_course = Course(
            title=course.title,
            description=course.description,
            category=course.category,
            difficulty=course.difficulty,
            duration=course.duration,
            objectives=course.objectives,
            prerequisites=course.prerequisites,
            thumbnail=course.thumbnail,
            price=course.price,
            is_free=course.is_free,
            instructor_id=current_user.id,
            school_id=current_user.school_id,
            status='draft'
        )
        
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        
        logger.info(f"Course created: {db_course.title} by user {current_user.id}")
        return db_course
        
    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create course")

@router.get("/courses", response_model=List[CourseResponse])
async def get_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    status: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get courses with filtering and pagination"""
    try:
        query = db.query(Course).filter(Course.school_id == current_user.school_id)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Course.title.ilike(f"%{search}%"),
                    Course.description.ilike(f"%{search}%")
                )
            )
        
        if category:
            query = query.filter(Course.category == category)
            
        if difficulty:
            query = query.filter(Course.difficulty == difficulty)
            
        if status:
            query = query.filter(Course.status == status)
        
        # Apply pagination
        offset = (page - 1) * limit
        courses = query.offset(offset).limit(limit).all()
        
        return courses
        
    except Exception as e:
        logger.error(f"Error fetching courses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch courses")

@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific course"""
    try:
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.school_id == current_user.school_id
        ).first()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return course
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching course: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch course")

@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """Update a course"""
    try:
        # Get course
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.school_id == current_user.school_id
        ).first()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check permissions
        if current_user.role not in ['admin'] and course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own courses"
            )
        
        # Update course
        for field, value in course_update.dict(exclude_unset=True).items():
            setattr(course, field, value)
        
        course.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(course)
        
        logger.info(f"Course updated: {course.title} by user {current_user.id}")
        return course
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating course: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update course")

@router.delete("/courses/{course_id}", response_model=MessageResponse)
async def delete_course(
    course_id: int,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """Delete a course"""
    try:
        # Get course
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.school_id == current_user.school_id
        ).first()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check permissions
        if current_user.role not in ['admin'] and course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only delete your own courses"
            )
        
        # Delete course and related data
        db.delete(course)
        db.commit()
        
        logger.info(f"Course deleted: {course.title} by user {current_user.id}")
        return MessageResponse(message="Course deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting course: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete course")

@router.post("/courses/{course_id}/enroll", response_model=MessageResponse)
async def enroll_in_course(
    course_id: int,
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enroll in a course"""
    try:
        # Get course
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.school_id == current_user.school_id,
            Course.status == 'published'
        ).first()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found or not published")
        
        # Check if already enrolled
        existing_enrollment = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.student_id == current_user.id
        ).first()
        
        if existing_enrollment:
            raise HTTPException(status_code=400, detail="Already enrolled in this course")
        
        # Create enrollment
        enrollment = CourseEnrollment(
            course_id=course_id,
            student_id=current_user.id,
            enrolled_at=datetime.utcnow()
        )
        
        db.add(enrollment)
        db.commit()
        
        logger.info(f"User {current_user.id} enrolled in course {course_id}")
        return MessageResponse(message="Successfully enrolled in course")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling in course: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to enroll in course")

@router.get("/courses/{course_id}/progress", response_model=CourseProgressResponse)
async def get_course_progress(
    course_id: int,
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get course progress for current user"""
    try:
        # Check enrollment
        enrollment = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.student_id == current_user.id
        ).first()
        
        if not enrollment:
            raise HTTPException(status_code=404, detail="Not enrolled in this course")
        
        # Get course with lessons
        course = db.query(Course).filter(Course.id == course_id).first()
        lessons = db.query(Lesson).filter(Lesson.course_id == course_id).all()
        
        # Get progress data
        completed_lessons = db.query(LessonProgress).filter(
            LessonProgress.student_id == current_user.id,
            LessonProgress.lesson_id.in_([lesson.id for lesson in lessons]),
            LessonProgress.completed == True
        ).count()
        
        total_lessons = len(lessons)
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return CourseProgressResponse(
            course_id=course_id,
            student_id=current_user.id,
            progress_percentage=progress_percentage,
            completed_lessons=completed_lessons,
            total_lessons=total_lessons,
            enrollment_date=enrollment.enrolled_at,
            last_accessed=enrollment.last_accessed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get course progress")

# Statistics and Analytics Routes
@router.get("/stats/quiz/{quiz_id}", response_model=QuizStats)
async def get_quiz_stats(
    quiz_id: int,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get quiz statistics
    """
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.school_id == current_user.school_id,
        Quiz.is_active == True
    ).first()
    
    if not quiz:
        raise quiz_not_found
    
    # Get submission stats
    submissions = db.query(Submission).filter(
        Submission.quiz_id == quiz_id,
        Submission.status == "graded"
    ).all()
    
    if not submissions:
        return QuizStats(
            quiz_id=quiz_id,
            total_attempts=0,
            total_submissions=0,
            average_score=0.0,
            highest_score=0.0,
            lowest_score=0.0,
            pass_rate=0.0
        )
    
    scores = [s.total_score for s in submissions if s.total_score is not None]
    percentages = [s.percentage for s in submissions if s.percentage is not None]
    
    total_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id
    ).count()
    
    passed_count = len([p for p in percentages if p >= quiz.pass_mark])
    
    return QuizStats(
        quiz_id=quiz_id,
        total_attempts=total_attempts,
        total_submissions=len(submissions),
        average_score=sum(scores) / len(scores) if scores else 0.0,
        highest_score=max(scores) if scores else 0.0,
        lowest_score=min(scores) if scores else 0.0,
        pass_rate=(passed_count / len(submissions)) * 100 if submissions else 0.0
    )


@router.get("/stats/content/{content_id}", response_model=ContentStatsSchema)
async def get_content_stats(
    content_id: int,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get content statistics
    """
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.is_active == True
    ).first()
    
    if not content:
        raise content_not_found
    
    # Check access
    check_content_access(current_user, content.school_id, content.is_public)
    
    # Get stats
    stats = db.query(ContentStats).filter(
        ContentStats.content_id == content_id,
        ContentStats.school_id == current_user.school_id
    ).first()
    
    if not stats:
        return ContentStatsSchema(
            content_id=content_id,
            view_count=0,
            download_count=0,
            quiz_generation_count=0
        )
    
    return ContentStatsSchema(
        content_id=content_id,
        view_count=stats.view_count,
        download_count=stats.download_count,
        quiz_generation_count=stats.quiz_generation_count,
        last_accessed=stats.last_accessed
    )


# Lesson Management Routes
@router.post("/courses/{course_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    course_id: int,
    lesson: LessonCreate,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """Create a new lesson in a course"""
    try:
        # Check if course exists and user has permission
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.school_id == current_user.school_id
        ).first()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        if current_user.role not in ['admin'] and course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only add lessons to your own courses"
            )
        
        # Create lesson
        db_lesson = Lesson(
            course_id=course_id,
            title=lesson.title,
            description=lesson.description,
            duration=lesson.duration,
            order=lesson.order,
            video_url=lesson.video_url,
            content_text=lesson.content_text,
            resources=lesson.resources,
            is_published=lesson.is_published
        )
        
        db.add(db_lesson)
        db.commit()
        db.refresh(db_lesson)
        
        logger.info(f"Lesson created: {db_lesson.title} in course {course_id}")
        return db_lesson
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lesson: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create lesson")

@router.get("/courses/{course_id}/lessons", response_model=List[LessonResponse])
async def get_course_lessons(
    course_id: int,
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all lessons for a course"""
    try:
        # Check if course exists and user has access
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.school_id == current_user.school_id
        ).first()
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Get lessons
        lessons = db.query(Lesson).filter(
            Lesson.course_id == course_id
        ).order_by(Lesson.order, Lesson.created_at).all()
        
        return lessons
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lessons: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch lessons")

@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_update: LessonUpdate,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """Update a lesson"""
    try:
        # Get lesson with course
        lesson = db.query(Lesson).join(Course).filter(
            Lesson.id == lesson_id,
            Course.school_id == current_user.school_id
        ).first()
        
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Check permissions
        if current_user.role not in ['admin'] and lesson.course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only update lessons in your own courses"
            )
        
        # Update lesson
        for field, value in lesson_update.dict(exclude_unset=True).items():
            setattr(lesson, field, value)
        
        lesson.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lesson)
        
        logger.info(f"Lesson updated: {lesson.title} by user {current_user.id}")
        return lesson
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lesson: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update lesson")

@router.delete("/lessons/{lesson_id}", response_model=MessageResponse)
async def delete_lesson(
    lesson_id: int,
    current_user: CurrentUser = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """Delete a lesson"""
    try:
        # Get lesson with course
        lesson = db.query(Lesson).join(Course).filter(
            Lesson.id == lesson_id,
            Course.school_id == current_user.school_id
        ).first()
        
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Check permissions
        if current_user.role not in ['admin'] and lesson.course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only delete lessons from your own courses"
            )
        
        # Delete lesson
        db.delete(lesson)
        db.commit()
        
        logger.info(f"Lesson deleted: {lesson.title} by user {current_user.id}")
        return MessageResponse(message="Lesson deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lesson: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete lesson")

@router.post("/lessons/{lesson_id}/progress", response_model=ProgressResponse)
async def update_lesson_progress(
    lesson_id: int,
    progress_update: ProgressUpdate,
    current_user: CurrentUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update lesson progress for current user"""
    try:
        # Check if lesson exists and user has access
        lesson = db.query(Lesson).join(Course).filter(
            Lesson.id == lesson_id,
            Course.school_id == current_user.school_id
        ).first()
        
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Check if user is enrolled in the course
        enrollment = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == lesson.course_id,
            CourseEnrollment.student_id == current_user.id
        ).first()
        
        if not enrollment:
            raise HTTPException(status_code=403, detail="You must be enrolled in the course to track progress")
        
        # Get or create progress record
        progress = db.query(LessonProgress).filter(
            LessonProgress.lesson_id == lesson_id,
            LessonProgress.student_id == current_user.id
        ).first()
        
        if not progress:
            progress = LessonProgress(
                lesson_id=lesson_id,
                student_id=current_user.id,
                started_at=datetime.utcnow()
            )
            db.add(progress)
        
        # Update progress
        progress.completed = progress_update.completed
        progress.time_spent = progress_update.time_spent
        
        if progress_update.completed and not progress.completed_at:
            progress.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(progress)
        
        # Update course enrollment progress
        _update_course_progress(enrollment.id, db)
        
        logger.info(f"Progress updated for lesson {lesson_id} by user {current_user.id}")
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lesson progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update lesson progress")

def _update_course_progress(enrollment_id: int, db: Session):
    """Helper function to update course progress"""
    try:
        enrollment = db.query(CourseEnrollment).filter(
            CourseEnrollment.id == enrollment_id
        ).first()
        
        if not enrollment:
            return
        
        # Get total lessons in course
        total_lessons = db.query(Lesson).filter(
            Lesson.course_id == enrollment.course_id
        ).count()
        
        # Get completed lessons
        completed_lessons = db.query(LessonProgress).filter(
            LessonProgress.student_id == enrollment.student_id,
            LessonProgress.completed == True
        ).join(Lesson).filter(
            Lesson.course_id == enrollment.course_id
        ).count()
        
        # Update enrollment progress
        enrollment.completed_lessons = completed_lessons
        enrollment.progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        enrollment.last_accessed = datetime.utcnow()
        
        # Mark as completed if all lessons are done
        if completed_lessons == total_lessons and total_lessons > 0:
            enrollment.completed_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error updating course progress: {str(e)}")

# Health check
@router.get("/health", response_model=MessageResponse)
async def health_check():
    """Health check endpoint"""
    return MessageResponse(message="Content & Quiz Service is running")
