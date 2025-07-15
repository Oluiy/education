"""
EduNerve Sync & Messaging Service - Core Service Logic
Handles synchronization, messaging, and real-time communication
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import uuid
import logging
import asyncio
from fastapi import HTTPException

from .models import (
    SyncRecord, Message, Notification, DeviceRegistration,
    SyncConflict, MessageThread, OfflineData, WebSocketConnection,
    SyncStatus, MessageType, NotificationStatus, MessageStatus
)
from .schemas import (
    SyncRecordCreate, SyncRecordUpdate, MessageCreate, MessageUpdate,
    NotificationCreate, DeviceRegistrationCreate, DeviceRegistrationUpdate,
    SyncConflictCreate, MessageThreadCreate, OfflineDataCreate,
    WebSocketConnectionCreate, BulkSyncRequest, SyncStatusResponse,
    RealTimeEvent
)
from .auth import CurrentUser

# Configure logging
logger = logging.getLogger(__name__)

class SyncMessagingService:
    """Core service for sync and messaging operations"""
    
    # === SYNC OPERATIONS ===
    
    async def create_sync_record(
        self,
        sync_data: SyncRecordCreate,
        current_user: CurrentUser,
        db: Session
    ) -> SyncRecord:
        """Create a new sync record"""
        try:
            sync_record = SyncRecord(
                user_id=sync_data.user_id,
                school_id=sync_data.school_id,
                device_id=sync_data.device_id,
                entity_type=sync_data.entity_type,
                entity_id=sync_data.entity_id,
                operation=sync_data.operation,
                data=sync_data.data,
                metadata=sync_data.metadata,
                priority=sync_data.priority,
                resolution_strategy=sync_data.resolution_strategy
            )
            
            db.add(sync_record)
            db.commit()
            db.refresh(sync_record)
            
            logger.info(f"Created sync record {sync_record.sync_id} for user {current_user.user_id}")
            return sync_record
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating sync record: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create sync record")
    
    async def process_sync_record(
        self,
        sync_id: str,
        current_user: CurrentUser,
        db: Session
    ) -> SyncRecord:
        """Process a pending sync record"""
        try:
            sync_record = db.query(SyncRecord).filter(
                SyncRecord.sync_id == sync_id,
                SyncRecord.user_id == current_user.user_id
            ).first()
            
            if not sync_record:
                raise HTTPException(status_code=404, detail="Sync record not found")
            
            if sync_record.status != SyncStatus.PENDING:
                raise HTTPException(status_code=400, detail="Sync record not pending")
            
            # Update status to processing
            sync_record.status = SyncStatus.PROCESSING
            db.commit()
            
            # Process based on operation type
            success = await self._execute_sync_operation(sync_record, db)
            
            if success:
                sync_record.status = SyncStatus.COMPLETED
                sync_record.synced_at = datetime.utcnow()
            else:
                sync_record.status = SyncStatus.FAILED
                sync_record.retry_count += 1
                sync_record.last_retry = datetime.utcnow()
            
            db.commit()
            db.refresh(sync_record)
            
            return sync_record
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing sync record: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to process sync record")
    
    async def get_pending_syncs(
        self,
        user_id: int,
        device_id: str,
        school_id: int,
        db: Session,
        limit: int = 100
    ) -> List[SyncRecord]:
        """Get pending sync records for a user/device"""
        try:
            syncs = db.query(SyncRecord).filter(
                SyncRecord.user_id == user_id,
                SyncRecord.device_id == device_id,
                SyncRecord.school_id == school_id,
                SyncRecord.status.in_([SyncStatus.PENDING, SyncStatus.FAILED])
            ).order_by(
                asc(SyncRecord.priority),
                asc(SyncRecord.created_at)
            ).limit(limit).all()
            
            return syncs
            
        except Exception as e:
            logger.error(f"Error getting pending syncs: {str(e)}")
            return []
    
    async def bulk_sync(
        self,
        bulk_request: BulkSyncRequest,
        current_user: CurrentUser,
        db: Session
    ) -> Dict[str, Any]:
        """Process multiple sync records in bulk"""
        try:
            successful = []
            failed = []
            conflicts = []
            
            for sync_data in bulk_request.sync_records:
                try:
                    # Check for conflicts
                    conflict = await self._check_sync_conflict(sync_data, db)
                    if conflict:
                        conflicts.append(conflict)
                        continue
                    
                    # Create sync record
                    sync_record = await self.create_sync_record(sync_data, current_user, db)
                    
                    # Process immediately
                    processed_record = await self.process_sync_record(
                        sync_record.sync_id, current_user, db
                    )
                    successful.append(processed_record)
                    
                except Exception as e:
                    failed.append({
                        "sync_data": sync_data.dict(),
                        "error": str(e)
                    })
            
            return {
                "successful": successful,
                "failed": failed,
                "conflicts": conflicts,
                "total": len(bulk_request.sync_records),
                "processed": len(successful) + len(failed) + len(conflicts)
            }
            
        except Exception as e:
            logger.error(f"Error in bulk sync: {str(e)}")
            raise HTTPException(status_code=500, detail="Bulk sync failed")
    
    async def get_sync_status(
        self,
        user_id: int,
        device_id: str,
        school_id: int,
        db: Session
    ) -> SyncStatusResponse:
        """Get synchronization status for a user/device"""
        try:
            # Get pending syncs count
            pending_syncs = db.query(SyncRecord).filter(
                SyncRecord.user_id == user_id,
                SyncRecord.device_id == device_id,
                SyncRecord.school_id == school_id,
                SyncRecord.status == SyncStatus.PENDING
            ).count()
            
            # Get conflicts count
            conflicts = db.query(SyncConflict).join(SyncRecord).filter(
                SyncRecord.user_id == user_id,
                SyncRecord.device_id == device_id,
                SyncRecord.school_id == school_id,
                SyncConflict.is_resolved == False
            ).count()
            
            # Get last sync
            last_sync_record = db.query(SyncRecord).filter(
                SyncRecord.user_id == user_id,
                SyncRecord.device_id == device_id,
                SyncRecord.school_id == school_id,
                SyncRecord.status == SyncStatus.COMPLETED
            ).order_by(desc(SyncRecord.synced_at)).first()
            
            last_sync = last_sync_record.synced_at if last_sync_record else None
            
            # Get device registration
            device = db.query(DeviceRegistration).filter(
                DeviceRegistration.device_id == device_id,
                DeviceRegistration.user_id == user_id
            ).first()
            
            return SyncStatusResponse(
                pending_syncs=pending_syncs,
                conflicts=conflicts,
                last_sync=last_sync,
                sync_enabled=device.sync_enabled if device else True,
                offline_mode=not (device.is_online if device else False)
            )
            
        except Exception as e:
            logger.error(f"Error getting sync status: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get sync status")
    
    # === MESSAGE OPERATIONS ===
    
    async def send_message(
        self,
        message_data: MessageCreate,
        current_user: CurrentUser,
        db: Session
    ) -> Message:
        """Send a new message"""
        try:
            # Create message
            message = Message(
                message_type=message_data.message_type,
                subject=message_data.subject,
                content=message_data.content,
                sender_id=message_data.sender_id,
                sender_name=message_data.sender_name,
                sender_type=message_data.sender_type,
                recipient_ids=message_data.recipient_ids,
                recipient_groups=message_data.recipient_groups,
                school_id=message_data.school_id,
                context=message_data.context,
                attachments=message_data.attachments,
                thread_id=message_data.thread_id,
                parent_message_id=message_data.parent_message_id,
                scheduled_at=message_data.scheduled_at,
                expires_at=message_data.expires_at
            )
            
            # Set sent time if not scheduled
            if not message_data.scheduled_at:
                message.sent_at = datetime.utcnow()
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            # Update thread if exists
            if message.thread_id:
                await self._update_thread_stats(message.thread_id, db)
            
            # Send real-time notifications
            await self._send_realtime_notifications(message, db)
            
            logger.info(f"Message {message.message_id} sent by user {current_user.user_id}")
            return message
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error sending message: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to send message")
    
    async def get_messages(
        self,
        user_id: int,
        school_id: int,
        thread_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 50,
        offset: int = 0,
        db: Session = None
    ) -> List[Message]:
        """Get messages for a user"""
        try:
            query = db.query(Message).filter(
                or_(
                    Message.sender_id == user_id,
                    Message.recipient_ids.contains([user_id])
                ),
                Message.school_id == school_id
            )
            
            if thread_id:
                query = query.filter(Message.thread_id == thread_id)
            
            if message_type:
                query = query.filter(Message.message_type == message_type)
            
            messages = query.order_by(desc(Message.created_at)).offset(offset).limit(limit).all()
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []
    
    async def mark_message_read(
        self,
        message_id: str,
        user_id: int,
        db: Session
    ) -> bool:
        """Mark a message as read by a user"""
        try:
            message = db.query(Message).filter(Message.message_id == message_id).first()
            if not message:
                return False
            
            # Update read status
            read_status = message.read_status or {}
            read_status[str(user_id)] = datetime.utcnow().isoformat()
            message.read_status = read_status
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error marking message read: {str(e)}")
            return False
    
    # === NOTIFICATION OPERATIONS ===
    
    async def send_notification(
        self,
        notification_data: NotificationCreate,
        current_user: CurrentUser,
        db: Session
    ) -> Notification:
        """Send a push notification"""
        try:
            notification = Notification(
                title=notification_data.title,
                body=notification_data.body,
                notification_type=notification_data.notification_type,
                category=notification_data.category,
                user_id=notification_data.user_id,
                school_id=notification_data.school_id,
                device_tokens=notification_data.device_tokens,
                data=notification_data.data,
                action_url=notification_data.action_url,
                actions=notification_data.actions,
                scheduled_at=notification_data.scheduled_at,
                expires_at=notification_data.expires_at
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Send immediately if not scheduled
            if not notification_data.scheduled_at:
                await self._deliver_notification(notification, db)
            
            logger.info(f"Notification {notification.notification_id} created for user {notification_data.user_id}")
            return notification
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error sending notification: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to send notification")
    
    # === DEVICE MANAGEMENT ===
    
    async def register_device(
        self,
        device_data: DeviceRegistrationCreate,
        current_user: CurrentUser,
        db: Session
    ) -> DeviceRegistration:
        """Register a new device"""
        try:
            # Check if device already exists
            existing_device = db.query(DeviceRegistration).filter(
                DeviceRegistration.device_id == device_data.device_id
            ).first()
            
            if existing_device:
                # Update existing device
                for field, value in device_data.dict(exclude_unset=True).items():
                    setattr(existing_device, field, value)
                
                existing_device.updated_at = datetime.utcnow()
                existing_device.is_active = True
                existing_device.last_seen = datetime.utcnow()
                
                db.commit()
                db.refresh(existing_device)
                return existing_device
            
            # Create new device
            device = DeviceRegistration(
                device_id=device_data.device_id,
                user_id=device_data.user_id,
                school_id=device_data.school_id,
                device_type=device_data.device_type,
                platform=device_data.platform,
                app_version=device_data.app_version,
                os_version=device_data.os_version,
                fcm_token=device_data.fcm_token,
                apns_token=device_data.apns_token,
                web_push_subscription=device_data.web_push_subscription,
                sync_enabled=device_data.sync_enabled,
                sync_settings=device_data.sync_settings,
                last_seen=datetime.utcnow()
            )
            
            db.add(device)
            db.commit()
            db.refresh(device)
            
            logger.info(f"Device {device.device_id} registered for user {current_user.user_id}")
            return device
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error registering device: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to register device")
    
    # === OFFLINE DATA MANAGEMENT ===
    
    async def store_offline_data(
        self,
        offline_data: OfflineDataCreate,
        current_user: CurrentUser,
        db: Session
    ) -> OfflineData:
        """Store data for offline access"""
        try:
            # Check if data already exists
            existing_data = db.query(OfflineData).filter(
                OfflineData.cache_key == offline_data.cache_key,
                OfflineData.user_id == offline_data.user_id,
                OfflineData.device_id == offline_data.device_id
            ).first()
            
            if existing_data:
                # Update existing data
                existing_data.data = offline_data.data
                existing_data.cache_duration = offline_data.cache_duration
                existing_data.expires_at = datetime.utcnow() + timedelta(seconds=offline_data.cache_duration)
                existing_data.updated_at = datetime.utcnow()
                
                db.commit()
                db.refresh(existing_data)
                return existing_data
            
            # Create new offline data
            data = OfflineData(
                user_id=offline_data.user_id,
                device_id=offline_data.device_id,
                school_id=offline_data.school_id,
                entity_type=offline_data.entity_type,
                entity_id=offline_data.entity_id,
                data=offline_data.data,
                cache_key=offline_data.cache_key,
                cache_duration=offline_data.cache_duration,
                is_encrypted=offline_data.is_encrypted,
                compression_type=offline_data.compression_type,
                expires_at=datetime.utcnow() + timedelta(seconds=offline_data.cache_duration)
            )
            
            db.add(data)
            db.commit()
            db.refresh(data)
            
            return data
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing offline data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to store offline data")
    
    # === HELPER METHODS ===
    
    async def _execute_sync_operation(
        self,
        sync_record: SyncRecord,
        db: Session
    ) -> bool:
        """Execute the actual sync operation"""
        try:
            # This would contain the actual logic to sync data
            # with other services based on entity_type and operation
            
            # Placeholder implementation
            await asyncio.sleep(0.1)  # Simulate processing time
            return True
            
        except Exception as e:
            logger.error(f"Error executing sync operation: {str(e)}")
            return False
    
    async def _check_sync_conflict(
        self,
        sync_data: SyncRecordCreate,
        db: Session
    ) -> Optional[SyncConflict]:
        """Check if sync operation would cause a conflict"""
        try:
            # Check for existing records with same entity
            existing_sync = db.query(SyncRecord).filter(
                SyncRecord.entity_type == sync_data.entity_type,
                SyncRecord.entity_id == sync_data.entity_id,
                SyncRecord.status.in_([SyncStatus.PENDING, SyncStatus.PROCESSING])
            ).first()
            
            if existing_sync:
                # Create conflict record
                conflict = SyncConflict(
                    sync_record_id=existing_sync.id,
                    entity_type=sync_data.entity_type,
                    entity_id=sync_data.entity_id,
                    local_data=sync_data.data,
                    remote_data=existing_sync.data
                )
                
                db.add(conflict)
                db.commit()
                db.refresh(conflict)
                
                return conflict
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking sync conflict: {str(e)}")
            return None
    
    async def _update_thread_stats(
        self,
        thread_id: str,
        db: Session
    ):
        """Update message thread statistics"""
        try:
            thread = db.query(MessageThread).filter(
                MessageThread.thread_id == thread_id
            ).first()
            
            if thread:
                # Update message count
                message_count = db.query(Message).filter(
                    Message.thread_id == thread_id
                ).count()
                
                thread.message_count = message_count
                thread.last_message_at = datetime.utcnow()
                thread.updated_at = datetime.utcnow()
                
                db.commit()
                
        except Exception as e:
            logger.error(f"Error updating thread stats: {str(e)}")
    
    async def _send_realtime_notifications(
        self,
        message: Message,
        db: Session
    ):
        """Send real-time notifications for new message"""
        try:
            # This would integrate with WebSocket service
            # to send real-time notifications to connected users
            
            # Get active connections for recipients
            active_connections = db.query(WebSocketConnection).filter(
                WebSocketConnection.user_id.in_(message.recipient_ids),
                WebSocketConnection.is_active == True
            ).all()
            
            # Send notification to each active connection
            for connection in active_connections:
                # Placeholder for WebSocket notification
                logger.info(f"Sending real-time notification to connection {connection.connection_id}")
                
        except Exception as e:
            logger.error(f"Error sending real-time notifications: {str(e)}")
    
    async def _deliver_notification(
        self,
        notification: Notification,
        db: Session
    ):
        """Deliver push notification"""
        try:
            # Get device tokens for user
            devices = db.query(DeviceRegistration).filter(
                DeviceRegistration.user_id == notification.user_id,
                DeviceRegistration.is_active == True
            ).all()
            
            for device in devices:
                # Send push notification based on platform
                if device.platform == "android" and device.fcm_token:
                    # Send FCM notification
                    pass
                elif device.platform == "ios" and device.apns_token:
                    # Send APNS notification
                    pass
                elif device.platform == "web" and device.web_push_subscription:
                    # Send web push notification
                    pass
            
            # Update notification status
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            notification.delivery_attempts += 1
            notification.last_attempt = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error delivering notification: {str(e)}")
            notification.status = NotificationStatus.FAILED
            db.commit()

# Create service instance
sync_messaging_service = SyncMessagingService()
