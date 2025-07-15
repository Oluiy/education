"""
EduNerve Assistant Service - Main FastAPI Application
Personalized AI assistant for students with multimedia learning resources
"""

from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uvicorn
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from .database import create_tables, get_db
from .models import StudyPlan, StudyResource, StudentActivity, LearningAnalytics
from .schemas import (
    StudyPlanCreate, StudyPlanResponse, StudyResourceRequest, StudyResourceResponse,
    StudentActivityCreate, LearningAnalyticsResponse, MessageResponse, ErrorResponse
)
from .auth import get_current_user, get_current_student_user, CurrentUser
from .assistant_service import AssistantService
from .ai_service import AIService
from .audio_service import AudioService
from .youtube_service import YouTubeService

# Initialize services
assistant_service = AssistantService()
ai_service = AIService()
audio_service = AudioService()
youtube_service = YouTubeService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting EduNerve Assistant Service...")
    
    # Create database tables
    create_tables()
    logger.info("✅ Database tables created successfully")
    
    # Create audio storage directory
    audio_dir = os.getenv('AUDIO_STORAGE_PATH', 'audio_files')
    os.makedirs(audio_dir, exist_ok=True)
    
    logger.info("✅ Assistant Service startup complete")
    yield
    
    # Shutdown
    logger.info("🔽 Shutting down Assistant Service...")
    await youtube_service.close_session()
    logger.info("✅ Assistant Service shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="EduNerve Assistant Service",
    description="Personalized AI assistant for students with multimedia learning resources",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for audio content
audio_dir = os.getenv('AUDIO_STORAGE_PATH', 'audio_files')
if os.path.exists(audio_dir):
    app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "assistant-service"}

# === STUDY PLAN ENDPOINTS ===

@app.post("/api/v1/assistant/study-plan", response_model=StudyPlanResponse)
async def create_study_plan(
    request: StudyPlanCreate,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Create a personalized study plan for a student"""
    try:
        study_plan = await assistant_service.generate_study_plan(
            user_id=current_user.id,
            school_id=current_user.school_id,
            subject=request.subject,
            grade_level=request.grade_level,
            learning_objectives=request.learning_objectives,
            duration_weeks=request.duration_weeks,
            db=db
        )
        
        return study_plan
        
    except Exception as e:
        logger.error(f"Error creating study plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create study plan")

@app.get("/api/v1/assistant/study-plans", response_model=List[StudyPlanResponse])
async def get_study_plans(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get all study plans for current student"""
    try:
        plans = db.query(StudyPlan).filter(
            StudyPlan.user_id == current_user.id,
            StudyPlan.school_id == current_user.school_id
        ).order_by(desc(StudyPlan.created_at)).all()
        
        return [
            StudyPlanResponse(
                id=plan.id,
                title=plan.title,
                subject=plan.subject,
                grade_level=plan.grade_level,
                learning_objectives=plan.learning_objectives,
                duration_weeks=plan.duration_weeks,
                plan_content=plan.plan_content,
                status=plan.status,
                created_at=plan.created_at,
                updated_at=plan.updated_at
            )
            for plan in plans
        ]
        
    except Exception as e:
        logger.error(f"Error getting study plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get study plans")

@app.get("/api/v1/assistant/study-plan/{plan_id}", response_model=StudyPlanResponse)
async def get_study_plan(
    plan_id: int,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get a specific study plan"""
    try:
        plan = db.query(StudyPlan).filter(
            StudyPlan.id == plan_id,
            StudyPlan.user_id == current_user.id,
            StudyPlan.school_id == current_user.school_id
        ).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Study plan not found")
        
        return StudyPlanResponse(
            id=plan.id,
            title=plan.title,
            subject=plan.subject,
            grade_level=plan.grade_level,
            learning_objectives=plan.learning_objectives,
            duration_weeks=plan.duration_weeks,
            plan_content=plan.plan_content,
            status=plan.status,
            created_at=plan.created_at,
            updated_at=plan.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting study plan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get study plan")

# === STUDY RESOURCE ENDPOINTS ===

@app.post("/api/v1/assistant/resources", response_model=List[StudyResourceResponse])
async def generate_study_resources(
    request: StudyResourceRequest,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Generate comprehensive study resources for a topic"""
    try:
        resources = await assistant_service.generate_study_resources(
            request=request,
            user_id=current_user.id,
            school_id=current_user.school_id,
            db=db
        )
        
        return resources
        
    except Exception as e:
        logger.error(f"Error generating resources: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate study resources")

@app.get("/api/v1/assistant/resources", response_model=List[StudyResourceResponse])
async def get_study_resources(
    topic: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get study resources for current student"""
    try:
        query = db.query(StudyResource).filter(
            StudyResource.user_id == current_user.id,
            StudyResource.school_id == current_user.school_id
        )
        
        if topic:
            query = query.filter(StudyResource.topic.ilike(f"%{topic}%"))
        if subject:
            query = query.filter(StudyResource.subject == subject)
        if content_type:
            query = query.filter(StudyResource.content_type == content_type)
        
        resources = query.order_by(desc(StudyResource.created_at)).limit(50).all()
        
        return [
            StudyResourceResponse(
                id=resource.id,
                title=resource.title,
                content_type=resource.content_type,
                topic=resource.topic,
                subject=resource.subject,
                grade_level=resource.grade_level,
                difficulty_level=resource.difficulty_level,
                content=resource.content,
                keywords=resource.keywords,
                metadata=resource.metadata,
                created_at=resource.created_at
            )
            for resource in resources
        ]
        
    except Exception as e:
        logger.error(f"Error getting resources: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get study resources")

@app.get("/api/v1/assistant/resources/{resource_id}", response_model=StudyResourceResponse)
async def get_study_resource(
    resource_id: int,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get a specific study resource"""
    try:
        resource = db.query(StudyResource).filter(
            StudyResource.id == resource_id,
            StudyResource.user_id == current_user.id,
            StudyResource.school_id == current_user.school_id
        ).first()
        
        if not resource:
            raise HTTPException(status_code=404, detail="Study resource not found")
        
        return StudyResourceResponse(
            id=resource.id,
            title=resource.title,
            content_type=resource.content_type,
            topic=resource.topic,
            subject=resource.subject,
            grade_level=resource.grade_level,
            difficulty_level=resource.difficulty_level,
            content=resource.content,
            keywords=resource.keywords,
            metadata=resource.metadata,
            created_at=resource.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resource: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get study resource")

# === AUDIO ENDPOINTS ===

@app.get("/api/v1/assistant/audio/{filename}")
async def get_audio_file(
    filename: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Serve audio files"""
    try:
        audio_path = os.path.join(audio_dir, filename)
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving audio file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve audio file")

# === ACTIVITY TRACKING ENDPOINTS ===

@app.post("/api/v1/assistant/activity", response_model=MessageResponse)
async def track_activity(
    request: StudentActivityCreate,
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Track student learning activity"""
    try:
        await assistant_service.track_student_activity(
            user_id=current_user.id,
            school_id=current_user.school_id,
            activity_type=request.activity_type,
            activity_data=request.activity_data,
            db=db
        )
        
        return MessageResponse(message="Activity tracked successfully")
        
    except Exception as e:
        logger.error(f"Error tracking activity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track activity")

@app.get("/api/v1/assistant/activities", response_model=List[Dict[str, Any]])
async def get_student_activities(
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get student learning activities"""
    try:
        activities = db.query(StudentActivity).filter(
            StudentActivity.user_id == current_user.id,
            StudentActivity.school_id == current_user.school_id
        ).order_by(desc(StudentActivity.timestamp)).limit(limit).all()
        
        return [
            {
                "id": activity.id,
                "activity_type": activity.activity_type,
                "activity_data": activity.activity_data,
                "timestamp": activity.timestamp
            }
            for activity in activities
        ]
        
    except Exception as e:
        logger.error(f"Error getting activities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get activities")

# === ANALYTICS ENDPOINTS ===

@app.get("/api/v1/assistant/analytics", response_model=LearningAnalyticsResponse)
async def get_learning_analytics(
    current_user: CurrentUser = Depends(get_current_student_user),
    db: Session = Depends(get_db)
):
    """Get student learning analytics"""
    try:
        analytics = db.query(LearningAnalytics).filter(
            LearningAnalytics.user_id == current_user.id,
            LearningAnalytics.school_id == current_user.school_id
        ).first()
        
        if not analytics:
            # Create default analytics
            analytics = LearningAnalytics(
                user_id=current_user.id,
                school_id=current_user.school_id,
                analytics_data={
                    'total_study_time': 0,
                    'subjects_studied': [],
                    'average_quiz_score': 0,
                    'learning_preferences': {},
                    'strength_areas': [],
                    'improvement_areas': []
                }
            )
            db.add(analytics)
            db.commit()
            db.refresh(analytics)
        
        return LearningAnalyticsResponse(
            user_id=analytics.user_id,
            school_id=analytics.school_id,
            analytics_data=analytics.analytics_data,
            updated_at=analytics.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get learning analytics")

# === VIDEO SEARCH ENDPOINTS ===

@app.get("/api/v1/assistant/videos/search")
async def search_educational_videos(
    query: str = Query(..., description="Search query for educational videos"),
    max_results: int = Query(10, ge=1, le=20),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Search for educational videos"""
    try:
        videos = await youtube_service.search_educational_videos(
            query=query,
            max_results=max_results
        )
        
        return {"videos": videos}
        
    except Exception as e:
        logger.error(f"Error searching videos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search videos")

# === EXCEPTION HANDLERS ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            status_code=500
        ).dict()
    )

# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
