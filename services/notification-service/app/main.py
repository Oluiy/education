"""
EduNerve Notification Service - FastAPI Application
Main application for handling notification requests and management
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import os
from contextlib import asynccontextmanager

from . import models, schemas
from .database import engine, get_db
from .auth import verify_token, get_current_user
from .notification_service import NotificationService
from .security_config import SecurityConfig
from .cors_config import apply_secure_cors
from .error_handling import SecureErrorHandler
from api.notifications import router as notifications_router
import uvicorn

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('notification_service.log')
    ]
)
logger = logging.getLogger(__name__)

# Global variables for background tasks
notification_processor_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting EduNerve Notification Service...")
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)
    
    # Start background task processor
    global notification_processor_task
    notification_processor_task = asyncio.create_task(notification_processor())
    
    yield
    
    # Shutdown
    logger.info("Shutting down EduNerve Notification Service...")
    
    # Cancel background task
    if notification_processor_task:
        notification_processor_task.cancel()
        try:
            await notification_processor_task
        except asyncio.CancelledError:
            pass

# Create FastAPI app
app = FastAPI(
    title="EduNerve Notification Service",
    description="AI-powered notification service for educational institutions",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize security configuration
security_config = SecurityConfig()

# Apply secure CORS configuration
apply_secure_cors(app)

# Add secure error handlers
error_handler = SecureErrorHandler()
error_handler.add_handlers(app)

# Include routers
app.include_router(notifications_router)

# Security
security = HTTPBearer()

# Dependency to get current user with school context
async def get_current_user_with_school(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current user with school context"""
    user_info = await get_current_user(credentials, db)
    return user_info

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "EduNerve Notification Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# === NOTIFICATION ENDPOINTS ===

@app.post("/notifications", response_model=schemas.NotificationResponse)
async def create_notification(
    notification: schemas.NotificationCreate,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Create a new notification"""
    try:
        service = NotificationService(db)
        
        result = await service.create_notification(
            notification_data=notification,
            school_id=user["school_id"],
            sender_id=user["user_id"]
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create notification: {', '.join(result.errors)}"
            )
        
        # Get the created notification
        created_notification = db.query(models.Notification).filter(
            models.Notification.notification_id == result.notification_id
        ).first()
        
        return schemas.NotificationResponse.from_orm(created_notification)
        
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )

@app.post("/notifications/quick")
async def send_quick_notification(
    request: schemas.QuickNotificationRequest,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Send a quick notification"""
    try:
        service = NotificationService(db)
        
        result = await service.send_quick_notification(
            request=request,
            school_id=user["school_id"],
            sender_id=user["user_id"]
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send notification: {', '.join(result.errors)}"
            )
        
        return {
            "success": True,
            "notification_id": result.notification_id,
            "recipients": result.total_recipients,
            "queued": result.queued_count
        }
        
    except Exception as e:
        logger.error(f"Error sending quick notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )

@app.post("/notifications/bulk")
async def send_bulk_notification(
    request: schemas.BulkNotificationRequest,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Send bulk notification to target audience"""
    try:
        service = NotificationService(db)
        
        result = await service.send_bulk_notification(
            request=request,
            school_id=user["school_id"],
            sender_id=user["user_id"]
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send bulk notification: {', '.join(result.errors)}"
            )
        
        return {
            "success": True,
            "notification_id": result.notification_id,
            "recipients": result.total_recipients,
            "queued": result.queued_count
        }
        
    except Exception as e:
        logger.error(f"Error sending bulk notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send bulk notification"
        )

@app.get("/notifications/{notification_id}")
async def get_notification(
    notification_id: str,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Get notification details and status"""
    try:
        service = NotificationService(db)
        
        notification_data = await service.get_notification_status(notification_id)
        
        if not notification_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return notification_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification"
        )

@app.get("/notifications")
async def list_notifications(
    skip: int = 0,
    limit: int = 100,
    notification_type: Optional[str] = None,
    status: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """List notifications for the school"""
    try:
        query = db.query(models.Notification).filter(
            models.Notification.school_id == user["school_id"]
        )
        
        if notification_type:
            query = query.filter(models.Notification.notification_type == notification_type)
        
        if status:
            query = query.filter(models.Notification.status == status)
        
        notifications = (
            query.order_by(models.Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [schemas.NotificationResponse.from_orm(n) for n in notifications]
        
    except Exception as e:
        logger.error(f"Error listing notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list notifications"
        )

@app.put("/notifications/{notification_id}")
async def update_notification(
    notification_id: str,
    update_data: schemas.NotificationUpdate,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Update notification"""
    try:
        notification = db.query(models.Notification).filter(
            models.Notification.notification_id == notification_id,
            models.Notification.school_id == user["school_id"]
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(notification, field, value)
        
        notification.updated_at = datetime.utcnow()
        db.commit()
        
        return schemas.NotificationResponse.from_orm(notification)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification"
        )

@app.delete("/notifications/{notification_id}")
async def cancel_notification(
    notification_id: str,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Cancel a notification"""
    try:
        notification = db.query(models.Notification).filter(
            models.Notification.notification_id == notification_id,
            models.Notification.school_id == user["school_id"]
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        if notification.status in ["sent", "delivered", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel notification in current status"
            )
        
        notification.status = "cancelled"
        notification.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Notification cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel notification"
        )

# === TEMPLATE ENDPOINTS ===

@app.post("/templates", response_model=schemas.NotificationTemplateResponse)
async def create_template(
    template: schemas.NotificationTemplateCreate,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Create a notification template"""
    try:
        db_template = models.NotificationTemplate(
            **template.dict(),
            school_id=user["school_id"]
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return schemas.NotificationTemplateResponse.from_orm(db_template)
        
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template"
        )

@app.get("/templates")
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    template_type: Optional[str] = None,
    category: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """List notification templates"""
    try:
        query = db.query(models.NotificationTemplate).filter(
            models.NotificationTemplate.school_id == user["school_id"],
            models.NotificationTemplate.is_active == True
        )
        
        if template_type:
            query = query.filter(models.NotificationTemplate.template_type == template_type)
        
        if category:
            query = query.filter(models.NotificationTemplate.category == category)
        
        templates = (
            query.order_by(models.NotificationTemplate.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [schemas.NotificationTemplateResponse.from_orm(t) for t in templates]
        
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list templates"
        )

@app.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Get a specific template"""
    try:
        template = db.query(models.NotificationTemplate).filter(
            models.NotificationTemplate.template_id == template_id,
            models.NotificationTemplate.school_id == user["school_id"]
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return schemas.NotificationTemplateResponse.from_orm(template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get template"
        )

@app.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    template_update: schemas.NotificationTemplateUpdate,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Update a template"""
    try:
        template = db.query(models.NotificationTemplate).filter(
            models.NotificationTemplate.template_id == template_id,
            models.NotificationTemplate.school_id == user["school_id"]
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Update fields
        update_dict = template_update.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        db.commit()
        
        return schemas.NotificationTemplateResponse.from_orm(template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template"
        )

@app.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Delete a template"""
    try:
        template = db.query(models.NotificationTemplate).filter(
            models.NotificationTemplate.template_id == template_id,
            models.NotificationTemplate.school_id == user["school_id"]
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        template.is_active = False
        template.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template"
        )

# === ANALYTICS ENDPOINTS ===

@app.get("/analytics/summary")
async def get_analytics_summary(
    days: int = 30,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Get notification analytics summary"""
    try:
        start_date = datetime.utcnow().date() - timedelta(days=days)
        
        analytics = db.query(models.NotificationAnalytics).filter(
            models.NotificationAnalytics.school_id == user["school_id"],
            models.NotificationAnalytics.date >= start_date
        ).all()
        
        # Aggregate data
        total_sent = sum(a.total_sent for a in analytics)
        total_delivered = sum(a.total_delivered for a in analytics)
        total_failed = sum(a.total_failed for a in analytics)
        
        by_type = {
            "email": sum(a.email_sent for a in analytics),
            "sms": sum(a.sms_sent for a in analytics),
            "whatsapp": sum(a.whatsapp_sent for a in analytics),
            "push": sum(a.push_sent for a in analytics),
            "voice": sum(a.voice_sent for a in analytics)
        }
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().date().isoformat(),
                "days": days
            },
            "summary": {
                "total_sent": total_sent,
                "total_delivered": total_delivered,
                "total_failed": total_failed,
                "delivery_rate": (total_delivered / total_sent * 100) if total_sent > 0 else 0
            },
            "by_type": by_type,
            "daily_data": [
                {
                    "date": a.date.isoformat(),
                    "sent": a.total_sent,
                    "delivered": a.total_delivered,
                    "failed": a.total_failed
                }
                for a in analytics
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics"
        )

# === SETTINGS ENDPOINTS ===

@app.get("/settings")
async def get_notification_settings(
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Get user notification settings"""
    try:
        settings = db.query(models.NotificationSettings).filter(
            models.NotificationSettings.user_id == user["user_id"],
            models.NotificationSettings.school_id == user["school_id"]
        ).first()
        
        if not settings:
            # Create default settings
            settings = models.NotificationSettings(
                user_id=user["user_id"],
                school_id=user["school_id"],
                user_type=user.get("user_type", "student")
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return schemas.NotificationSettingsResponse.from_orm(settings)
        
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get settings"
        )

@app.put("/settings")
async def update_notification_settings(
    settings_update: schemas.NotificationSettingsUpdate,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Update user notification settings"""
    try:
        settings = db.query(models.NotificationSettings).filter(
            models.NotificationSettings.user_id == user["user_id"],
            models.NotificationSettings.school_id == user["school_id"]
        ).first()
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Settings not found"
            )
        
        # Update fields
        update_dict = settings_update.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(settings, field, value)
        
        settings.updated_at = datetime.utcnow()
        db.commit()
        
        return schemas.NotificationSettingsResponse.from_orm(settings)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings"
        )

# === BACKGROUND TASKS ===

async def notification_processor():
    """Background task to process notification queue"""
    while True:
        try:
            # Process different priority queues
            for queue in ["emergency_priority", "urgent_priority", "high_priority", "normal_priority", "low_priority"]:
                db = next(get_db())
                try:
                    service = NotificationService(db)
                    result = await service.process_queue(queue_name=queue, batch_size=50)
                    
                    if result["processed"] > 0:
                        logger.info(f"Processed {result['processed']} notifications from {queue} queue")
                    
                finally:
                    db.close()
            
            # Wait before next processing cycle
            await asyncio.sleep(30)  # Process every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in notification processor: {str(e)}")
            await asyncio.sleep(60)  # Wait longer on error

# === ADMIN ENDPOINTS ===

@app.post("/admin/process-queue")
async def process_queue_manually(
    queue_name: str = "normal",
    batch_size: int = 100,
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Manually process notification queue (admin only)"""
    try:
        # Check if user is admin
        if user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        service = NotificationService(db)
        result = await service.process_queue(queue_name=queue_name, batch_size=batch_size)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing queue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process queue"
        )

@app.get("/admin/queue-status")
async def get_queue_status(
    user: Dict[str, Any] = Depends(get_current_user_with_school),
    db: Session = Depends(get_db)
):
    """Get queue status (admin only)"""
    try:
        # Check if user is admin
        if user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get queue statistics
        queue_stats = db.query(
            models.NotificationQueue.status,
            models.NotificationQueue.queue_name,
            func.count(models.NotificationQueue.id).label("count")
        ).group_by(
            models.NotificationQueue.status,
            models.NotificationQueue.queue_name
        ).all()
        
        return [
            {
                "queue_name": stat.queue_name,
                "status": stat.status,
                "count": stat.count
            }
            for stat in queue_stats
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting queue status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get queue status"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info"
    )
