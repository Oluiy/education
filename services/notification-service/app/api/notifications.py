"""
Notification API endpoints for SMS and WhatsApp
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, validator
import logging
import asyncio

from services.termii_service import termii_service, parent_summary_service, MessageResult

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# Pydantic models
class SMSRequest(BaseModel):
    to: str
    message: str
    sender_id: Optional[str] = None
    message_type: str = "plain"
    
    @validator('to')
    def validate_phone(cls, v):
        if not v or len(v.replace('+', '').replace(' ', '').replace('-', '')) < 10:
            raise ValueError('Invalid phone number')
        return v
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 918:  # SMS character limit
            raise ValueError('Message too long (max 918 characters)')
        return v


class WhatsAppRequest(BaseModel):
    to: str
    message: Optional[str] = None
    template_name: Optional[str] = None
    template_params: Optional[Dict[str, str]] = None
    
    @validator('to')
    def validate_phone(cls, v):
        if not v or len(v.replace('+', '').replace(' ', '').replace('-', '')) < 10:
            raise ValueError('Invalid phone number')
        return v
    
    class Config:
        extra = "forbid"


class BulkSMSRequest(BaseModel):
    recipients: List[str]
    message: str
    sender_id: Optional[str] = None
    
    @validator('recipients')
    def validate_recipients(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Recipients list cannot be empty')
        if len(v) > 1000:
            raise ValueError('Too many recipients (max 1000)')
        return v


class ParentSummaryRequest(BaseModel):
    student_ids: Optional[List[int]] = None  # None means all students
    method: str = "sms"  # "sms" or "whatsapp"
    custom_message: Optional[str] = None
    
    @validator('method')
    def validate_method(cls, v):
        if v not in ["sms", "whatsapp"]:
            raise ValueError('Method must be "sms" or "whatsapp"')
        return v


class NotificationResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    status: str = "unknown"
    cost: Optional[float] = None


class BulkNotificationResponse(BaseModel):
    total_sent: int
    successful: int
    failed: int
    results: List[NotificationResponse]


# API endpoints
@router.post("/sms/send", response_model=NotificationResponse)
async def send_sms(request: SMSRequest):
    """
    Send SMS message via Termii
    """
    try:
        result = await termii_service.send_sms(
            to=request.to,
            message=request.message,
            sender_id=request.sender_id,
            message_type=request.message_type
        )
        
        return NotificationResponse(
            success=result.success,
            message_id=result.message_id,
            error=result.error,
            status=result.status,
            cost=result.cost
        )
    
    except Exception as e:
        logger.error(f"SMS send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp/send", response_model=NotificationResponse)
async def send_whatsapp(request: WhatsAppRequest):
    """
    Send WhatsApp message via Termii
    """
    try:
        if not request.message and not request.template_name:
            raise HTTPException(
                status_code=400,
                detail="Either message or template_name must be provided"
            )
        
        result = await termii_service.send_whatsapp(
            to=request.to,
            message=request.message or "",
            template_name=request.template_name,
            template_params=request.template_params
        )
        
        return NotificationResponse(
            success=result.success,
            message_id=result.message_id,
            error=result.error,
            status=result.status
        )
    
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sms/bulk", response_model=BulkNotificationResponse)
async def send_bulk_sms(request: BulkSMSRequest, background_tasks: BackgroundTasks):
    """
    Send bulk SMS messages
    """
    try:
        # For large bulk sends, use background tasks
        if len(request.recipients) > 100:
            background_tasks.add_task(
                _send_bulk_sms_background,
                request.recipients,
                request.message,
                request.sender_id
            )
            
            return BulkNotificationResponse(
                total_sent=len(request.recipients),
                successful=0,
                failed=0,
                results=[NotificationResponse(
                    success=True,
                    status="queued",
                    message_id="bulk_queued"
                )]
            )
        
        # For smaller sends, process immediately
        results = await termii_service.send_bulk_sms(
            recipients=request.recipients,
            message=request.message,
            sender_id=request.sender_id
        )
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        response_results = [
            NotificationResponse(
                success=r.success,
                message_id=r.message_id,
                error=r.error,
                status=r.status,
                cost=r.cost
            ) for r in results
        ]
        
        return BulkNotificationResponse(
            total_sent=len(request.recipients),
            successful=successful,
            failed=failed,
            results=response_results
        )
    
    except Exception as e:
        logger.error(f"Bulk SMS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{message_id}")
async def get_message_status(message_id: str):
    """
    Get delivery status of a message
    """
    try:
        status = await termii_service.get_delivery_status(message_id)
        return status
    
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance")
async def get_account_balance():
    """
    Get Termii account balance
    """
    try:
        balance = await termii_service.get_account_balance()
        return balance
    
    except Exception as e:
        logger.error(f"Balance check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/validate")
async def validate_configuration():
    """
    Validate Termii configuration
    """
    try:
        config_status = termii_service.validate_config()
        return {
            "configured": all(config_status.values()),
            "details": config_status
        }
    
    except Exception as e:
        logger.error(f"Config validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parent-summary/send", response_model=BulkNotificationResponse)
async def send_parent_summaries(
    request: ParentSummaryRequest,
    background_tasks: BackgroundTasks
):
    """
    Send weekly summaries to parents
    """
    try:
        # Calculate current week
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Get student-parent data (mock for now)
        student_parent_list = _get_student_parent_data(request.student_ids)
        
        if not student_parent_list:
            raise HTTPException(
                status_code=404,
                detail="No student-parent data found"
            )
        
        # Use background task for bulk sending
        background_tasks.add_task(
            _send_parent_summaries_background,
            student_parent_list,
            week_start,
            week_end,
            request.method
        )
        
        return BulkNotificationResponse(
            total_sent=len(student_parent_list),
            successful=0,
            failed=0,
            results=[NotificationResponse(
                success=True,
                status="queued",
                message_id="parent_summaries_queued"
            )]
        )
    
    except Exception as e:
        logger.error(f"Parent summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parent-summary/preview/{student_id}")
async def preview_parent_summary(student_id: int):
    """
    Preview weekly summary for a student
    """
    try:
        # Calculate current week
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Generate summary
        summary = await parent_summary_service.generate_summary(
            student_id=student_id,
            week_start=week_start,
            week_end=week_end,
            db_session=None
        )
        
        # Format message
        message = parent_summary_service.format_summary_message(
            summary=summary,
            student_name=f"Student {student_id}"  # Would get actual name
        )
        
        return {
            "student_id": student_id,
            "summary_data": summary,
            "formatted_message": message,
            "message_length": len(message)
        }
    
    except Exception as e:
        logger.error(f"Summary preview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp/template")
async def create_whatsapp_template(
    name: str,
    language: str,
    category: str,
    components: List[Dict[str, Any]]
):
    """
    Create WhatsApp message template
    """
    try:
        result = await termii_service.create_whatsapp_template(
            name=name,
            language=language,
            category=category,
            components=components
        )
        return result
    
    except Exception as e:
        logger.error(f"Template creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Background task functions
async def _send_bulk_sms_background(
    recipients: List[str],
    message: str,
    sender_id: Optional[str]
):
    """
    Background task for bulk SMS sending
    """
    try:
        logger.info(f"Starting bulk SMS send to {len(recipients)} recipients")
        
        results = await termii_service.send_bulk_sms(
            recipients=recipients,
            message=message,
            sender_id=sender_id
        )
        
        successful = sum(1 for r in results if r.success)
        logger.info(f"Bulk SMS completed: {successful}/{len(recipients)} successful")
        
    except Exception as e:
        logger.error(f"Background bulk SMS error: {e}")


async def _send_parent_summaries_background(
    student_parent_list: List[Dict[str, Any]],
    week_start: datetime,
    week_end: datetime,
    method: str
):
    """
    Background task for parent summary sending
    """
    try:
        logger.info(f"Starting parent summaries to {len(student_parent_list)} parents")
        
        results = await parent_summary_service.send_bulk_parent_summaries(
            student_parent_list=student_parent_list,
            week_start=week_start,
            week_end=week_end,
            method=method
        )
        
        successful = sum(1 for r in results if r.success)
        logger.info(f"Parent summaries completed: {successful}/{len(results)} successful")
        
    except Exception as e:
        logger.error(f"Background parent summary error: {e}")


def _get_student_parent_data(student_ids: Optional[List[int]]) -> List[Dict[str, Any]]:
    """
    Get student-parent contact data
    This would integrate with the user service or database
    """
    # Mock data for now
    mock_data = [
        {
            "student_id": 1,
            "student_name": "John Doe",
            "parent_phone": "2348123456789",
            "parent_name": "Jane Doe"
        },
        {
            "student_id": 2,
            "student_name": "Mary Smith",
            "parent_phone": "2348123456790",
            "parent_name": "Bob Smith"
        }
    ]
    
    if student_ids:
        return [item for item in mock_data if item["student_id"] in student_ids]
    
    return mock_data


# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    config_status = termii_service.validate_config()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "termii_configured": config_status["api_key_configured"],
        "features": {
            "sms": config_status["api_key_configured"] and config_status["sender_id_configured"],
            "whatsapp": config_status["api_key_configured"] and config_status["whatsapp_sender_configured"],
            "parent_summaries": True
        }
    }
