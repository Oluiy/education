"""
EduNerve Notification Service - Background Processing
Handles background task processing for notifications
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from . import models
from .database import get_db
from .notification_service import NotificationService
import os
import signal
import threading
import time

# Configure logging
logger = logging.getLogger(__name__)

class NotificationProcessor:
    """Background processor for handling notification queues"""
    
    def __init__(self):
        self.running = False
        self.worker_id = f"worker_{os.getpid()}"
        self.tasks = []
        self.shutdown_event = threading.Event()
        
    async def start(self):
        """Start the background processor"""
        if self.running:
            logger.warning("Processor already running")
            return
        
        self.running = True
        logger.info(f"Starting notification processor {self.worker_id}")
        
        # Start multiple processing tasks
        self.tasks = [
            asyncio.create_task(self._process_queue_worker("emergency_priority")),
            asyncio.create_task(self._process_queue_worker("urgent_priority")),
            asyncio.create_task(self._process_queue_worker("high_priority")),
            asyncio.create_task(self._process_queue_worker("normal_priority")),
            asyncio.create_task(self._process_queue_worker("low_priority")),
            asyncio.create_task(self._cleanup_worker()),
            asyncio.create_task(self._analytics_worker()),
            asyncio.create_task(self._retry_failed_worker())
        ]
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("Processor tasks cancelled")
        except Exception as e:
            logger.error(f"Error in processor: {str(e)}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the background processor"""
        if not self.running:
            return
        
        logger.info(f"Stopping notification processor {self.worker_id}")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks = []
        logger.info("Notification processor stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown_event.set()
        self.running = False
    
    async def _process_queue_worker(self, queue_name: str):
        """Worker for processing specific queue"""
        logger.info(f"Starting queue worker for {queue_name}")
        
        # Different intervals for different priorities
        intervals = {
            "emergency_priority": 5,   # 5 seconds
            "urgent_priority": 10,     # 10 seconds
            "high_priority": 15,       # 15 seconds
            "normal_priority": 30,     # 30 seconds
            "low_priority": 60         # 1 minute
        }
        
        interval = intervals.get(queue_name, 30)
        
        while self.running:
            try:
                db = next(get_db())
                try:
                    service = NotificationService(db)
                    
                    # Process queue
                    result = await service.process_queue(
                        queue_name=queue_name,
                        batch_size=self._get_batch_size(queue_name)
                    )
                    
                    if result["processed"] > 0:
                        logger.info(
                            f"Queue {queue_name}: processed {result['processed']}, "
                            f"success {result['success']}, failed {result['failed']}"
                        )
                    
                    # Handle errors
                    if result["errors"]:
                        logger.error(f"Queue {queue_name} errors: {result['errors']}")
                    
                finally:
                    db.close()
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in queue worker {queue_name}: {str(e)}")
                await asyncio.sleep(interval * 2)  # Wait longer on error
        
        logger.info(f"Queue worker {queue_name} stopped")
    
    async def _cleanup_worker(self):
        """Worker for cleaning up old records"""
        logger.info("Starting cleanup worker")
        
        while self.running:
            try:
                db = next(get_db())
                try:
                    await self._cleanup_old_records(db)
                finally:
                    db.close()
                
                # Run cleanup every hour
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup worker: {str(e)}")
                await asyncio.sleep(3600)
        
        logger.info("Cleanup worker stopped")
    
    async def _analytics_worker(self):
        """Worker for updating analytics"""
        logger.info("Starting analytics worker")
        
        while self.running:
            try:
                db = next(get_db())
                try:
                    await self._update_daily_analytics(db)
                finally:
                    db.close()
                
                # Run analytics update every 15 minutes
                await asyncio.sleep(900)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analytics worker: {str(e)}")
                await asyncio.sleep(900)
        
        logger.info("Analytics worker stopped")
    
    async def _retry_failed_worker(self):
        """Worker for retrying failed notifications"""
        logger.info("Starting retry worker")
        
        while self.running:
            try:
                db = next(get_db())
                try:
                    await self._retry_failed_notifications(db)
                finally:
                    db.close()
                
                # Run retry every 5 minutes
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in retry worker: {str(e)}")
                await asyncio.sleep(300)
        
        logger.info("Retry worker stopped")
    
    def _get_batch_size(self, queue_name: str) -> int:
        """Get batch size for queue"""
        batch_sizes = {
            "emergency_priority": 20,
            "urgent_priority": 30,
            "high_priority": 50,
            "normal_priority": 100,
            "low_priority": 200
        }
        return batch_sizes.get(queue_name, 50)
    
    async def _cleanup_old_records(self, db: Session):
        """Clean up old records"""
        try:
            # Define retention periods
            retention_periods = {
                "delivery_logs": 90,      # 90 days
                "queue_completed": 30,    # 30 days
                "analytics": 365,         # 1 year
                "notifications": 180      # 6 months
            }
            
            # Clean up old delivery logs
            cutoff_date = datetime.utcnow() - timedelta(days=retention_periods["delivery_logs"])
            deleted_logs = db.query(models.NotificationDeliveryLog).filter(
                models.NotificationDeliveryLog.attempted_at < cutoff_date
            ).delete()
            
            # Clean up completed queue items
            cutoff_date = datetime.utcnow() - timedelta(days=retention_periods["queue_completed"])
            deleted_queue = db.query(models.NotificationQueue).filter(
                and_(
                    models.NotificationQueue.status == "completed",
                    models.NotificationQueue.processing_completed < cutoff_date
                )
            ).delete()
            
            # Clean up old analytics (keep aggregated data)
            cutoff_date = datetime.utcnow() - timedelta(days=retention_periods["analytics"])
            deleted_analytics = db.query(models.NotificationAnalytics).filter(
                models.NotificationAnalytics.date < cutoff_date.date()
            ).delete()
            
            # Clean up old notifications (keep important ones)
            cutoff_date = datetime.utcnow() - timedelta(days=retention_periods["notifications"])
            deleted_notifications = db.query(models.Notification).filter(
                and_(
                    models.Notification.created_at < cutoff_date,
                    models.Notification.priority.in_(["low", "normal"])  # Keep high priority
                )
            ).delete()
            
            db.commit()
            
            if any([deleted_logs, deleted_queue, deleted_analytics, deleted_notifications]):
                logger.info(
                    f"Cleanup completed: {deleted_logs} logs, {deleted_queue} queue items, "
                    f"{deleted_analytics} analytics, {deleted_notifications} notifications"
                )
            
        except Exception as e:
            logger.error(f"Error in cleanup: {str(e)}")
            db.rollback()
    
    async def _update_daily_analytics(self, db: Session):
        """Update daily analytics"""
        try:
            # Get today's date
            today = datetime.utcnow().date()
            
            # Get all schools with notifications today
            schools = db.query(models.Notification.school_id).filter(
                models.Notification.created_at >= today
            ).distinct().all()
            
            for (school_id,) in schools:
                # Get or create analytics record
                analytics = db.query(models.NotificationAnalytics).filter(
                    and_(
                        models.NotificationAnalytics.school_id == school_id,
                        models.NotificationAnalytics.date == today
                    )
                ).first()
                
                if not analytics:
                    analytics = models.NotificationAnalytics(
                        school_id=school_id,
                        date=today
                    )
                    db.add(analytics)
                
                # Update analytics with current data
                await self._calculate_school_analytics(db, analytics, school_id, today)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating analytics: {str(e)}")
            db.rollback()
    
    async def _calculate_school_analytics(self, db: Session, analytics: models.NotificationAnalytics, 
                                        school_id: int, date: datetime.date):
        """Calculate analytics for a school"""
        try:
            # Get notifications for the day
            notifications = db.query(models.Notification).filter(
                and_(
                    models.Notification.school_id == school_id,
                    models.Notification.created_at >= date,
                    models.Notification.created_at < date + timedelta(days=1)
                )
            ).all()
            
            # Calculate totals
            total_sent = 0
            total_delivered = 0
            total_failed = 0
            
            type_counts = {
                "email": 0,
                "sms": 0,
                "whatsapp": 0,
                "push": 0,
                "voice": 0
            }
            
            priority_counts = {
                "emergency": 0,
                "urgent": 0,
                "high": 0,
                "normal": 0,
                "low": 0
            }
            
            for notification in notifications:
                recipients = db.query(models.NotificationRecipient).filter(
                    models.NotificationRecipient.notification_id == notification.notification_id
                ).all()
                
                recipient_count = len(recipients)
                delivered_count = sum(1 for r in recipients if r.status == "delivered")
                failed_count = sum(1 for r in recipients if r.status == "failed")
                
                total_sent += recipient_count
                total_delivered += delivered_count
                total_failed += failed_count
                
                # Update type counts
                if notification.notification_type in type_counts:
                    type_counts[notification.notification_type] += recipient_count
                
                # Update priority counts
                if notification.priority in priority_counts:
                    priority_counts[notification.priority] += recipient_count
            
            # Update analytics
            analytics.total_sent = total_sent
            analytics.total_delivered = total_delivered
            analytics.total_failed = total_failed
            
            analytics.email_sent = type_counts["email"]
            analytics.sms_sent = type_counts["sms"]
            analytics.whatsapp_sent = type_counts["whatsapp"]
            analytics.push_sent = type_counts["push"]
            analytics.voice_sent = type_counts["voice"]
            
            analytics.emergency_sent = priority_counts["emergency"]
            analytics.high_priority_sent = priority_counts["high"]
            analytics.normal_sent = priority_counts["normal"]
            analytics.low_priority_sent = priority_counts["low"]
            
            analytics.updated_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error calculating analytics: {str(e)}")
    
    async def _retry_failed_notifications(self, db: Session):
        """Retry failed notifications that can be retried"""
        try:
            # Get failed notifications that can be retried
            failed_notifications = db.query(models.Notification).filter(
                and_(
                    models.Notification.status == "failed",
                    models.Notification.retry_count < 3,
                    or_(
                        models.Notification.last_retry.is_(None),
                        models.Notification.last_retry < datetime.utcnow() - timedelta(minutes=30)
                    )
                )
            ).limit(50).all()
            
            for notification in failed_notifications:
                try:
                    # Update retry count
                    notification.retry_count += 1
                    notification.last_retry = datetime.utcnow()
                    notification.status = "queued"
                    
                    # Create new queue item
                    queue_item = models.NotificationQueue(
                        notification_id=notification.notification_id,
                        queue_name=f"{notification.priority}_priority",
                        priority=self._get_priority_value(notification.priority),
                        max_retries=1,  # One retry attempt
                        metadata={
                            "retry_attempt": notification.retry_count,
                            "original_failure": True
                        }
                    )
                    
                    db.add(queue_item)
                    
                    logger.info(
                        f"Retrying notification {notification.notification_id} "
                        f"(attempt {notification.retry_count})"
                    )
                    
                except Exception as e:
                    logger.error(f"Error retrying notification {notification.notification_id}: {str(e)}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error in retry worker: {str(e)}")
            db.rollback()
    
    def _get_priority_value(self, priority: str) -> int:
        """Get numeric priority value"""
        priority_map = {
            "emergency": 5,
            "urgent": 4,
            "high": 3,
            "normal": 2,
            "low": 1
        }
        return priority_map.get(priority, 2)

class NotificationScheduler:
    """Handles scheduled notifications"""
    
    def __init__(self):
        self.running = False
        self.scheduler_task = None
    
    async def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        logger.info("Starting notification scheduler")
        
        self.scheduler_task = asyncio.create_task(self._schedule_worker())
        
        try:
            await self.scheduler_task
        except asyncio.CancelledError:
            logger.info("Scheduler cancelled")
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        logger.info("Stopping notification scheduler")
        self.running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Notification scheduler stopped")
    
    async def _schedule_worker(self):
        """Worker for processing scheduled notifications"""
        logger.info("Starting scheduler worker")
        
        while self.running:
            try:
                db = next(get_db())
                try:
                    await self._process_scheduled_notifications(db)
                finally:
                    db.close()
                
                # Check every minute
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler worker: {str(e)}")
                await asyncio.sleep(60)
        
        logger.info("Scheduler worker stopped")
    
    async def _process_scheduled_notifications(self, db: Session):
        """Process notifications scheduled for now"""
        try:
            now = datetime.utcnow()
            
            # Get notifications scheduled for now
            scheduled_notifications = db.query(models.Notification).filter(
                and_(
                    models.Notification.scheduled_at <= now,
                    models.Notification.status == "pending"
                )
            ).all()
            
            for notification in scheduled_notifications:
                try:
                    # Create queue item
                    queue_item = models.NotificationQueue(
                        notification_id=notification.notification_id,
                        queue_name=f"{notification.priority}_priority",
                        priority=self._get_priority_value(notification.priority),
                        metadata={
                            "scheduled": True,
                            "original_scheduled_at": notification.scheduled_at.isoformat()
                        }
                    )
                    
                    db.add(queue_item)
                    
                    # Update notification status
                    notification.status = "queued"
                    
                    logger.info(f"Queued scheduled notification {notification.notification_id}")
                    
                except Exception as e:
                    logger.error(f"Error queuing scheduled notification {notification.notification_id}: {str(e)}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error processing scheduled notifications: {str(e)}")
            db.rollback()
    
    def _get_priority_value(self, priority: str) -> int:
        """Get numeric priority value"""
        priority_map = {
            "emergency": 5,
            "urgent": 4,
            "high": 3,
            "normal": 2,
            "low": 1
        }
        return priority_map.get(priority, 2)

# Global processor instance
processor = NotificationProcessor()
scheduler = NotificationScheduler()

async def start_background_services():
    """Start all background services"""
    logger.info("Starting background services")
    
    # Start both processor and scheduler
    await asyncio.gather(
        processor.start(),
        scheduler.start()
    )

async def stop_background_services():
    """Stop all background services"""
    logger.info("Stopping background services")
    
    await asyncio.gather(
        processor.stop(),
        scheduler.stop()
    )

if __name__ == "__main__":
    # For testing the background processor
    asyncio.run(start_background_services())
