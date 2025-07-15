"""
EduNerve Notification Service - Core Business Logic
Handles notification processing, queuing, and delivery management
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from . import models, schemas
from .providers import (
    SMSProvider, WhatsAppProvider, EmailProvider, 
    PushProvider, VoiceProvider
)
from .database import get_db
import uuid
import os
from jinja2 import Template
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class NotificationResult:
    """Result of notification processing"""
    success: bool
    notification_id: str
    total_recipients: int
    queued_count: int
    errors: List[str]
    provider_responses: List[Dict[str, Any]]

class NotificationService:
    """Core notification service for handling all notification operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.providers = {
            "sms": SMSProvider(),
            "whatsapp": WhatsAppProvider(),
            "email": EmailProvider(),
            "push": PushProvider(),
            "voice": VoiceProvider()
        }
    
    async def create_notification(
        self, 
        notification_data: schemas.NotificationCreate,
        school_id: int,
        sender_id: Optional[int] = None
    ) -> NotificationResult:
        """Create and process a new notification"""
        try:
            # Create notification record
            notification = models.Notification(
                notification_id=str(uuid.uuid4()),
                notification_type=notification_data.notification_type,
                subject=notification_data.subject,
                message=notification_data.message,
                html_message=notification_data.html_message,
                sender_id=sender_id,
                sender_name=notification_data.sender_name,
                sender_type=notification_data.sender_type,
                school_id=school_id,
                context=notification_data.context,
                template_id=notification_data.template_id,
                template_data=notification_data.template_data,
                priority=notification_data.priority,
                category=notification_data.category,
                scheduled_at=notification_data.scheduled_at,
                expires_at=notification_data.expires_at,
                metadata=notification_data.metadata or {},
                attachments=notification_data.attachments
            )
            
            self.db.add(notification)
            self.db.flush()  # Get the ID without committing
            
            # Process template if provided
            if notification_data.template_id:
                await self._apply_template(notification, notification_data.template_data)
            
            # Create recipient records
            recipients_created = []
            for recipient_data in notification_data.recipients:
                recipient = models.NotificationRecipient(
                    recipient_id=str(uuid.uuid4()),
                    notification_id=notification.notification_id,
                    user_id=recipient_data.user_id,
                    recipient_type=recipient_data.recipient_type,
                    email=recipient_data.email,
                    phone=recipient_data.phone,
                    whatsapp_number=recipient_data.whatsapp_number,
                    push_token=recipient_data.push_token,
                    name=recipient_data.name,
                    language=recipient_data.language,
                    timezone=recipient_data.timezone
                )
                
                self.db.add(recipient)
                recipients_created.append(recipient)
            
            self.db.commit()
            
            # Queue for processing
            queued_count = 0
            if notification_data.scheduled_at is None or notification_data.scheduled_at <= datetime.utcnow():
                queued_count = await self._queue_notification(notification)
            
            # Update analytics
            await self._update_analytics(school_id, notification_data.notification_type, len(recipients_created))
            
            return NotificationResult(
                success=True,
                notification_id=notification.notification_id,
                total_recipients=len(recipients_created),
                queued_count=queued_count,
                errors=[],
                provider_responses=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to create notification: {str(e)}")
            self.db.rollback()
            return NotificationResult(
                success=False,
                notification_id="",
                total_recipients=0,
                queued_count=0,
                errors=[str(e)],
                provider_responses=[]
            )
    
    async def send_quick_notification(
        self, 
        request: schemas.QuickNotificationRequest,
        school_id: int,
        sender_id: Optional[int] = None
    ) -> NotificationResult:
        """Send a quick notification to recipients"""
        try:
            # Convert quick request to full notification
            recipients = []
            for recipient in request.recipients:
                recipient_data = schemas.NotificationRecipientCreate(
                    name=recipient,
                    recipient_type=schemas.RecipientType.STUDENT,
                    email=recipient if "@" in recipient else None,
                    phone=recipient if not "@" in recipient else None
                )
                recipients.append(recipient_data)
            
            notification_data = schemas.NotificationCreate(
                notification_type=request.type,
                subject=request.subject,
                message=request.message,
                priority=request.priority,
                recipients=recipients
            )
            
            return await self.create_notification(notification_data, school_id, sender_id)
            
        except Exception as e:
            logger.error(f"Failed to send quick notification: {str(e)}")
            return NotificationResult(
                success=False,
                notification_id="",
                total_recipients=0,
                queued_count=0,
                errors=[str(e)],
                provider_responses=[]
            )
    
    async def send_bulk_notification(
        self, 
        request: schemas.BulkNotificationRequest,
        school_id: int,
        sender_id: Optional[int] = None
    ) -> NotificationResult:
        """Send bulk notification to target audience"""
        try:
            # Create bulk notification campaign
            campaign = models.BulkNotification(
                campaign_id=str(uuid.uuid4()),
                name=f"Bulk {request.type} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                description=f"Bulk notification: {request.subject or request.message[:50]}...",
                created_by=sender_id,
                school_id=school_id,
                notification_type=request.type,
                template_id=request.template_id,
                target_audience=request.target_audience,
                scheduled_at=request.scheduled_at,
                expires_at=request.expires_at,
                status="processing"
            )
            
            self.db.add(campaign)
            self.db.flush()
            
            # Get recipients based on target audience
            recipients = await self._get_bulk_recipients(request.target_audience, school_id)
            campaign.estimated_recipients = len(recipients)
            campaign.actual_recipients = len(recipients)
            
            # Create notification for bulk processing
            notification_data = schemas.NotificationCreate(
                notification_type=request.type,
                subject=request.subject,
                message=request.message,
                template_id=request.template_id,
                template_data=request.template_data,
                priority=request.priority,
                scheduled_at=request.scheduled_at,
                expires_at=request.expires_at,
                recipients=recipients,
                metadata={"bulk_campaign_id": campaign.campaign_id}
            )
            
            result = await self.create_notification(notification_data, school_id, sender_id)
            
            # Update campaign status
            campaign.status = "completed" if result.success else "failed"
            campaign.sent_count = result.queued_count
            campaign.completed_at = datetime.utcnow()
            
            self.db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send bulk notification: {str(e)}")
            return NotificationResult(
                success=False,
                notification_id="",
                total_recipients=0,
                queued_count=0,
                errors=[str(e)],
                provider_responses=[]
            )
    
    async def process_queue(self, queue_name: str = "normal", batch_size: int = 100) -> Dict[str, Any]:
        """Process notifications in the queue"""
        try:
            # Get pending queue items
            queue_items = (
                self.db.query(models.NotificationQueue)
                .filter(
                    and_(
                        models.NotificationQueue.status == "pending",
                        models.NotificationQueue.queue_name == queue_name,
                        or_(
                            models.NotificationQueue.next_retry.is_(None),
                            models.NotificationQueue.next_retry <= datetime.utcnow()
                        )
                    )
                )
                .order_by(models.NotificationQueue.priority.desc(), models.NotificationQueue.queued_at)
                .limit(batch_size)
                .all()
            )
            
            results = {
                "processed": 0,
                "success": 0,
                "failed": 0,
                "errors": []
            }
            
            for queue_item in queue_items:
                try:
                    # Mark as processing
                    queue_item.status = "processing"
                    queue_item.processing_started = datetime.utcnow()
                    queue_item.worker_id = f"worker_{os.getpid()}"
                    self.db.commit()
                    
                    # Process notification
                    success = await self._process_notification_item(queue_item)
                    
                    # Update queue item
                    if success:
                        queue_item.status = "completed"
                        queue_item.processing_completed = datetime.utcnow()
                        results["success"] += 1
                    else:
                        queue_item.retry_count += 1
                        if queue_item.retry_count >= queue_item.max_retries:
                            queue_item.status = "failed"
                        else:
                            queue_item.status = "pending"
                            queue_item.next_retry = datetime.utcnow() + timedelta(minutes=5 * queue_item.retry_count)
                        results["failed"] += 1
                    
                    results["processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing queue item {queue_item.id}: {str(e)}")
                    results["errors"].append(str(e))
                    
                    # Reset queue item status
                    queue_item.status = "pending"
                    queue_item.processing_started = None
                    queue_item.worker_id = None
                
                self.db.commit()
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing queue: {str(e)}")
            return {
                "processed": 0,
                "success": 0,
                "failed": 0,
                "errors": [str(e)]
            }
    
    async def get_notification_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get notification status and delivery details"""
        try:
            notification = (
                self.db.query(models.Notification)
                .filter(models.Notification.notification_id == notification_id)
                .first()
            )
            
            if not notification:
                return None
            
            # Get recipient statuses
            recipients = (
                self.db.query(models.NotificationRecipient)
                .filter(models.NotificationRecipient.notification_id == notification_id)
                .all()
            )
            
            # Get delivery logs
            delivery_logs = (
                self.db.query(models.NotificationDeliveryLog)
                .filter(models.NotificationDeliveryLog.notification_id == notification_id)
                .order_by(models.NotificationDeliveryLog.attempted_at.desc())
                .all()
            )
            
            # Calculate statistics
            total_recipients = len(recipients)
            delivered_count = sum(1 for r in recipients if r.status == "delivered")
            failed_count = sum(1 for r in recipients if r.status == "failed")
            pending_count = sum(1 for r in recipients if r.status in ["pending", "queued", "processing"])
            
            return {
                "notification_id": notification_id,
                "status": notification.status,
                "type": notification.notification_type,
                "subject": notification.subject,
                "message": notification.message,
                "priority": notification.priority,
                "created_at": notification.created_at,
                "sent_at": notification.sent_at,
                "delivered_at": notification.delivered_at,
                "statistics": {
                    "total_recipients": total_recipients,
                    "delivered": delivered_count,
                    "failed": failed_count,
                    "pending": pending_count,
                    "delivery_rate": (delivered_count / total_recipients * 100) if total_recipients > 0 else 0
                },
                "recipients": [
                    {
                        "recipient_id": r.recipient_id,
                        "name": r.name,
                        "email": r.email,
                        "phone": r.phone,
                        "status": r.status,
                        "delivered_at": r.delivered_at,
                        "failed_reason": r.failed_reason
                    }
                    for r in recipients
                ],
                "delivery_logs": [
                    {
                        "log_id": log.log_id,
                        "provider": log.provider,
                        "status": log.status,
                        "attempted_at": log.attempted_at,
                        "completed_at": log.completed_at,
                        "error_message": log.error_message
                    }
                    for log in delivery_logs
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting notification status: {str(e)}")
            return None
    
    async def _apply_template(self, notification: models.Notification, template_data: Optional[Dict[str, Any]]):
        """Apply template to notification"""
        try:
            template = (
                self.db.query(models.NotificationTemplate)
                .filter(models.NotificationTemplate.template_id == notification.template_id)
                .first()
            )
            
            if not template:
                logger.warning(f"Template {notification.template_id} not found")
                return
            
            # Render templates
            if template.subject_template and template_data:
                subject_template = Template(template.subject_template)
                notification.subject = subject_template.render(**template_data)
            
            if template.message_template and template_data:
                message_template = Template(template.message_template)
                notification.message = message_template.render(**template_data)
            
            if template.html_template and template_data:
                html_template = Template(template.html_template)
                notification.html_message = html_template.render(**template_data)
            
        except Exception as e:
            logger.error(f"Error applying template: {str(e)}")
    
    async def _queue_notification(self, notification: models.Notification) -> int:
        """Queue notification for processing"""
        try:
            # Determine queue priority
            priority_map = {
                "emergency": 5,
                "urgent": 4,
                "high": 3,
                "normal": 2,
                "low": 1
            }
            
            queue_name = f"{notification.priority}_priority"
            priority = priority_map.get(notification.priority, 2)
            
            # Create queue item
            queue_item = models.NotificationQueue(
                queue_id=str(uuid.uuid4()),
                notification_id=notification.notification_id,
                queue_name=queue_name,
                priority=priority,
                max_retries=3,
                metadata={
                    "notification_type": notification.notification_type,
                    "school_id": notification.school_id,
                    "recipient_count": len(notification.recipients)
                }
            )
            
            self.db.add(queue_item)
            self.db.commit()
            
            # Update notification status
            notification.status = "queued"
            self.db.commit()
            
            return 1
            
        except Exception as e:
            logger.error(f"Error queuing notification: {str(e)}")
            return 0
    
    async def _process_notification_item(self, queue_item: models.NotificationQueue) -> bool:
        """Process a single notification from the queue"""
        try:
            # Get notification
            notification = (
                self.db.query(models.Notification)
                .filter(models.Notification.notification_id == queue_item.notification_id)
                .first()
            )
            
            if not notification:
                logger.error(f"Notification {queue_item.notification_id} not found")
                return False
            
            # Update notification status
            notification.status = "processing"
            self.db.commit()
            
            # Get recipients
            recipients = (
                self.db.query(models.NotificationRecipient)
                .filter(models.NotificationRecipient.notification_id == notification.notification_id)
                .all()
            )
            
            # Process each recipient
            success_count = 0
            for recipient in recipients:
                try:
                    success = await self._send_to_recipient(notification, recipient)
                    if success:
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error sending to recipient {recipient.recipient_id}: {str(e)}")
            
            # Update notification status
            if success_count == len(recipients):
                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
            elif success_count > 0:
                notification.status = "partially_sent"
            else:
                notification.status = "failed"
            
            self.db.commit()
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error processing notification item: {str(e)}")
            return False
    
    async def _send_to_recipient(self, notification: models.Notification, recipient: models.NotificationRecipient) -> bool:
        """Send notification to a single recipient"""
        try:
            # Update recipient status
            recipient.status = "processing"
            recipient.delivery_attempts += 1
            recipient.last_attempt = datetime.utcnow()
            self.db.commit()
            
            # Get the appropriate provider
            provider = self.providers.get(notification.notification_type)
            if not provider:
                logger.error(f"No provider for notification type: {notification.notification_type}")
                recipient.status = "failed"
                recipient.failed_reason = f"No provider for {notification.notification_type}"
                self.db.commit()
                return False
            
            # Determine recipient address
            recipient_address = self._get_recipient_address(notification.notification_type, recipient)
            if not recipient_address:
                recipient.status = "failed"
                recipient.failed_reason = f"No valid address for {notification.notification_type}"
                self.db.commit()
                return False
            
            # Send notification
            result = await provider.send(
                recipient=recipient_address,
                message=notification.message,
                subject=notification.subject,
                html_message=notification.html_message,
                attachments=notification.attachments
            )
            
            # Create delivery log
            delivery_log = models.NotificationDeliveryLog(
                log_id=str(uuid.uuid4()),
                notification_id=notification.notification_id,
                recipient_id=recipient.recipient_id,
                provider=provider.get_provider_name(),
                provider_id=result.get("provider_id"),
                attempt_number=recipient.delivery_attempts,
                status="sent" if result.get("success") else "failed",
                response_code=result.get("response_code"),
                response_message=result.get("error", "Success"),
                response_data=result,
                completed_at=datetime.utcnow()
            )
            
            self.db.add(delivery_log)
            
            # Update recipient status
            if result.get("success"):
                recipient.status = "sent"
                recipient.external_id = result.get("provider_id")
                recipient.provider_response = result
            else:
                recipient.status = "failed"
                recipient.failed_reason = result.get("error", "Unknown error")
            
            self.db.commit()
            
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"Error sending to recipient: {str(e)}")
            
            # Update recipient status
            recipient.status = "failed"
            recipient.failed_reason = str(e)
            self.db.commit()
            
            return False
    
    def _get_recipient_address(self, notification_type: str, recipient: models.NotificationRecipient) -> Optional[str]:
        """Get the appropriate recipient address based on notification type"""
        if notification_type == "email":
            return recipient.email
        elif notification_type == "sms":
            return recipient.phone
        elif notification_type == "whatsapp":
            return recipient.whatsapp_number or recipient.phone
        elif notification_type == "push":
            return recipient.push_token
        elif notification_type == "voice":
            return recipient.phone
        return None
    
    async def _get_bulk_recipients(self, target_audience: Dict[str, Any], school_id: int) -> List[schemas.NotificationRecipientCreate]:
        """Get recipients for bulk notification based on target audience criteria"""
        # This is a simplified implementation
        # In a real system, you'd query user databases based on criteria
        recipients = []
        
        # Example criteria processing
        if target_audience.get("all_students"):
            # Get all students from auth service or user database
            # This would require integration with user management
            pass
        
        if target_audience.get("specific_users"):
            user_ids = target_audience["specific_users"]
            # Get user contact information
            pass
        
        if target_audience.get("user_types"):
            user_types = target_audience["user_types"]
            # Get users by type
            pass
        
        # For now, return empty list
        return recipients
    
    async def _update_analytics(self, school_id: int, notification_type: str, recipient_count: int):
        """Update notification analytics"""
        try:
            today = datetime.utcnow().date()
            
            # Get or create analytics record
            analytics = (
                self.db.query(models.NotificationAnalytics)
                .filter(
                    and_(
                        models.NotificationAnalytics.school_id == school_id,
                        models.NotificationAnalytics.date == today
                    )
                )
                .first()
            )
            
            if not analytics:
                analytics = models.NotificationAnalytics(
                    school_id=school_id,
                    date=today
                )
                self.db.add(analytics)
            
            # Update counters
            analytics.total_sent += recipient_count
            
            if notification_type == "email":
                analytics.email_sent += recipient_count
            elif notification_type == "sms":
                analytics.sms_sent += recipient_count
            elif notification_type == "whatsapp":
                analytics.whatsapp_sent += recipient_count
            elif notification_type == "push":
                analytics.push_sent += recipient_count
            elif notification_type == "voice":
                analytics.voice_sent += recipient_count
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating analytics: {str(e)}")
