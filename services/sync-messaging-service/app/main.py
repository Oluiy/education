"""
EduNerve Sync & Messaging Service - Main FastAPI Application
Offline synchronization, messaging, notifications, and real-time communication
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
import uvicorn
import os
import logging
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from .database import create_tables, get_db, DatabaseManager
from .models import (
    SyncRecord, Message, Notification, DeviceRegistration,
    SyncConflict, MessageThread, OfflineData, WebSocketConnection,
    SyncStatus, MessageType, NotificationStatus
)
from .schemas import (
    SyncRecordCreate, SyncRecordUpdate, SyncRecordResponse,
    MessageCreate, MessageUpdate, MessageResponse,
    NotificationCreate, NotificationUpdate, NotificationResponse,
    DeviceRegistrationCreate, DeviceRegistrationUpdate, DeviceRegistrationResponse,
    SyncConflictResponse, MessageThreadCreate, MessageThreadResponse,
    OfflineDataCreate, OfflineDataResponse, WebSocketConnectionResponse,
    BulkSyncRequest, BulkSyncResponse, BulkMessageRequest, BulkMessageResponse,
    SyncStatusRequest, SyncStatusResponse, RealTimeEvent,
    MessageResponse, ErrorResponse, PaginatedResponse, SyncStats, MessagingStats, ServiceStats
)
from .auth import (
    get_current_user, get_current_active_user, get_current_verified_user,
    get_student_user, get_teacher_user, get_admin_user, CurrentUser
)
from .sync_messaging_service import sync_messaging_service
from .websocket_manager import connection_manager, event_broadcaster

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting EduNerve Sync & Messaging Service...")
    
    # Create database tables
    create_tables()
    logger.info("✅ Database tables created successfully")
    
    # Create required directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("sync_data", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    logger.info("✅ Sync & Messaging Service startup complete")
    yield
    
    # Shutdown
    logger.info("🔽 Shutting down Sync & Messaging Service...")
    logger.info("✅ Sync & Messaging Service shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="EduNerve Sync & Messaging Service",
    description="Offline synchronization, messaging, notifications, and real-time communication",
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_healthy = DatabaseManager.check_connection()
    connection_stats = connection_manager.get_connection_stats()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "sync-messaging-service",
        "database": "connected" if db_healthy else "disconnected",
        "websocket_connections": connection_stats
    }

# === WEBSOCKET ENDPOINTS ===

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time communication"""
    connection_id = str(uuid.uuid4())
    
    try:
        # Validate user token (simplified for demo)
        # In production, use proper JWT validation
        user_data = {"id": user_id, "user_id": user_id, "school_id": 1, "role": "student"}
        current_user = CurrentUser(user_data)
        
        # Store connection in database
        ws_connection = WebSocketConnection(
            connection_id=connection_id,
            user_id=user_id,
            device_id=f"web_{connection_id}",
            school_id=current_user.school_id,
            socket_id=connection_id,
            last_ping=datetime.utcnow()
        )
        
        db.add(ws_connection)
        db.commit()
        
        # Accept connection
        await connection_manager.connect(websocket, connection_id, current_user)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Update last ping
                ws_connection.last_ping = datetime.utcnow()
                db.commit()
                
                # Handle message
                await connection_manager.handle_message(message, connection_id, current_user)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {connection_id}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    
    finally:
        # Cleanup
        connection_manager.disconnect(connection_id, user_id, current_user.school_id)
        
        # Update database
        ws_connection.is_active = False
        ws_connection.disconnected_at = datetime.utcnow()
        db.commit()

# === SYNC ENDPOINTS ===

@app.post("/api/v1/sync/records", response_model=SyncRecordResponse)
async def create_sync_record(
    sync_data: SyncRecordCreate,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Create a new sync record"""
    try:
        sync_record = await sync_messaging_service.create_sync_record(
            sync_data=sync_data,
            current_user=current_user,
            db=db
        )
        return SyncRecordResponse.from_orm(sync_record)
        
    except Exception as e:
        logger.error(f"Error creating sync record: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create sync record")

@app.get("/api/v1/sync/records", response_model=List[SyncRecordResponse])
async def get_sync_records(
    device_id: Optional[str] = Query(None),
    status: Optional[SyncStatus] = Query(None),
    entity_type: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get sync records for current user"""
    try:
        query = db.query(SyncRecord).filter(
            SyncRecord.user_id == current_user.user_id,
            SyncRecord.school_id == current_user.school_id
        )
        
        if device_id:
            query = query.filter(SyncRecord.device_id == device_id)
        
        if status:
            query = query.filter(SyncRecord.status == status)
        
        if entity_type:
            query = query.filter(SyncRecord.entity_type == entity_type)
        
        sync_records = query.order_by(desc(SyncRecord.created_at)).offset(offset).limit(limit).all()
        return [SyncRecordResponse.from_orm(record) for record in sync_records]
        
    except Exception as e:
        logger.error(f"Error getting sync records: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sync records")

@app.post("/api/v1/sync/process/{sync_id}", response_model=SyncRecordResponse)
async def process_sync_record(
    sync_id: str,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Process a pending sync record"""
    try:
        sync_record = await sync_messaging_service.process_sync_record(
            sync_id=sync_id,
            current_user=current_user,
            db=db
        )
        return SyncRecordResponse.from_orm(sync_record)
        
    except Exception as e:
        logger.error(f"Error processing sync record: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process sync record")

@app.post("/api/v1/sync/bulk", response_model=BulkSyncResponse)
async def bulk_sync(
    bulk_request: BulkSyncRequest,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Process multiple sync records in bulk"""
    try:
        result = await sync_messaging_service.bulk_sync(
            bulk_request=bulk_request,
            current_user=current_user,
            db=db
        )
        return BulkSyncResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in bulk sync: {str(e)}")
        raise HTTPException(status_code=500, detail="Bulk sync failed")

@app.get("/api/v1/sync/status", response_model=SyncStatusResponse)
async def get_sync_status(
    device_id: str = Query(...),
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get synchronization status for user/device"""
    try:
        status = await sync_messaging_service.get_sync_status(
            user_id=current_user.user_id,
            device_id=device_id,
            school_id=current_user.school_id,
            db=db
        )
        return status
        
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sync status")

@app.get("/api/v1/sync/pending", response_model=List[SyncRecordResponse])
async def get_pending_syncs(
    device_id: str = Query(...),
    limit: int = Query(100, le=500),
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get pending sync records for a device"""
    try:
        syncs = await sync_messaging_service.get_pending_syncs(
            user_id=current_user.user_id,
            device_id=device_id,
            school_id=current_user.school_id,
            db=db,
            limit=limit
        )
        return [SyncRecordResponse.from_orm(sync) for sync in syncs]
        
    except Exception as e:
        logger.error(f"Error getting pending syncs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get pending syncs")

# === MESSAGE ENDPOINTS ===

@app.post("/api/v1/messages", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Send a new message"""
    try:
        message = await sync_messaging_service.send_message(
            message_data=message_data,
            current_user=current_user,
            db=db
        )
        return MessageResponse.from_orm(message)
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@app.get("/api/v1/messages", response_model=List[MessageResponse])
async def get_messages(
    thread_id: Optional[str] = Query(None),
    message_type: Optional[MessageType] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get messages for current user"""
    try:
        messages = await sync_messaging_service.get_messages(
            user_id=current_user.user_id,
            school_id=current_user.school_id,
            thread_id=thread_id,
            message_type=message_type,
            limit=limit,
            offset=offset,
            db=db
        )
        return [MessageResponse.from_orm(message) for message in messages]
        
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@app.put("/api/v1/messages/{message_id}/read", response_model=MessageResponse)
async def mark_message_read(
    message_id: str,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Mark a message as read"""
    try:
        success = await sync_messaging_service.mark_message_read(
            message_id=message_id,
            user_id=current_user.user_id,
            db=db
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Get updated message
        message = db.query(Message).filter(Message.message_id == message_id).first()
        return MessageResponse.from_orm(message)
        
    except Exception as e:
        logger.error(f"Error marking message read: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to mark message read")

@app.post("/api/v1/messages/bulk", response_model=BulkMessageResponse)
async def send_bulk_messages(
    bulk_request: BulkMessageRequest,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Send multiple messages in bulk"""
    try:
        successful = []
        failed = []
        
        for message_data in bulk_request.messages:
            try:
                message = await sync_messaging_service.send_message(
                    message_data=message_data,
                    current_user=current_user,
                    db=db
                )
                successful.append(MessageResponse.from_orm(message))
                
            except Exception as e:
                failed.append({
                    "message_data": message_data.dict(),
                    "error": str(e)
                })
        
        return BulkMessageResponse(
            successful=successful,
            failed=failed,
            total=len(bulk_request.messages),
            processed=len(successful) + len(failed)
        )
        
    except Exception as e:
        logger.error(f"Error in bulk message send: {str(e)}")
        raise HTTPException(status_code=500, detail="Bulk message send failed")

# === NOTIFICATION ENDPOINTS ===

@app.post("/api/v1/notifications", response_model=NotificationResponse)
async def send_notification(
    notification_data: NotificationCreate,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Send a push notification"""
    try:
        notification = await sync_messaging_service.send_notification(
            notification_data=notification_data,
            current_user=current_user,
            db=db
        )
        return NotificationResponse.from_orm(notification)
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send notification")

@app.get("/api/v1/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    status: Optional[NotificationStatus] = Query(None),
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get notifications for current user"""
    try:
        query = db.query(Notification).filter(
            Notification.user_id == current_user.user_id,
            Notification.school_id == current_user.school_id
        )
        
        if status:
            query = query.filter(Notification.status == status)
        
        notifications = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
        return [NotificationResponse.from_orm(notification) for notification in notifications]
        
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")

@app.put("/api/v1/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    try:
        notification = db.query(Notification).filter(
            Notification.notification_id == notification_id,
            Notification.user_id == current_user.user_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)
        
        return NotificationResponse.from_orm(notification)
        
    except Exception as e:
        logger.error(f"Error marking notification read: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to mark notification read")

# === DEVICE MANAGEMENT ENDPOINTS ===

@app.post("/api/v1/devices/register", response_model=DeviceRegistrationResponse)
async def register_device(
    device_data: DeviceRegistrationCreate,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Register a new device"""
    try:
        device = await sync_messaging_service.register_device(
            device_data=device_data,
            current_user=current_user,
            db=db
        )
        return DeviceRegistrationResponse.from_orm(device)
        
    except Exception as e:
        logger.error(f"Error registering device: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register device")

@app.get("/api/v1/devices", response_model=List[DeviceRegistrationResponse])
async def get_user_devices(
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get all devices for current user"""
    try:
        devices = db.query(DeviceRegistration).filter(
            DeviceRegistration.user_id == current_user.user_id,
            DeviceRegistration.school_id == current_user.school_id
        ).all()
        
        return [DeviceRegistrationResponse.from_orm(device) for device in devices]
        
    except Exception as e:
        logger.error(f"Error getting user devices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user devices")

@app.put("/api/v1/devices/{device_id}", response_model=DeviceRegistrationResponse)
async def update_device(
    device_id: str,
    device_update: DeviceRegistrationUpdate,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Update device registration"""
    try:
        device = db.query(DeviceRegistration).filter(
            DeviceRegistration.device_id == device_id,
            DeviceRegistration.user_id == current_user.user_id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Update fields
        for field, value in device_update.dict(exclude_unset=True).items():
            setattr(device, field, value)
        
        device.updated_at = datetime.utcnow()
        device.last_seen = datetime.utcnow()
        
        db.commit()
        db.refresh(device)
        
        return DeviceRegistrationResponse.from_orm(device)
        
    except Exception as e:
        logger.error(f"Error updating device: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update device")

# === OFFLINE DATA ENDPOINTS ===

@app.post("/api/v1/offline/store", response_model=OfflineDataResponse)
async def store_offline_data(
    offline_data: OfflineDataCreate,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Store data for offline access"""
    try:
        data = await sync_messaging_service.store_offline_data(
            offline_data=offline_data,
            current_user=current_user,
            db=db
        )
        return OfflineDataResponse.from_orm(data)
        
    except Exception as e:
        logger.error(f"Error storing offline data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store offline data")

@app.get("/api/v1/offline/data", response_model=List[OfflineDataResponse])
async def get_offline_data(
    device_id: str = Query(...),
    entity_type: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get offline data for a device"""
    try:
        query = db.query(OfflineData).filter(
            OfflineData.user_id == current_user.user_id,
            OfflineData.device_id == device_id,
            OfflineData.school_id == current_user.school_id
        )
        
        if entity_type:
            query = query.filter(OfflineData.entity_type == entity_type)
        
        # Only return non-expired data
        query = query.filter(
            or_(
                OfflineData.expires_at.is_(None),
                OfflineData.expires_at > datetime.utcnow()
            )
        )
        
        offline_data = query.all()
        return [OfflineDataResponse.from_orm(data) for data in offline_data]
        
    except Exception as e:
        logger.error(f"Error getting offline data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get offline data")

# === REAL-TIME EVENT ENDPOINTS ===

@app.post("/api/v1/events/broadcast")
async def broadcast_event(
    event: RealTimeEvent,
    current_user: CurrentUser = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Broadcast a real-time event"""
    try:
        await event_broadcaster.broadcast_event(event)
        return MessageResponse(message="Event broadcasted successfully")
        
    except Exception as e:
        logger.error(f"Error broadcasting event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to broadcast event")

# === STATISTICS ENDPOINTS ===

@app.get("/api/v1/stats", response_model=ServiceStats)
async def get_service_stats(
    current_user: CurrentUser = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get service statistics (admin only)"""
    try:
        # Sync stats
        total_syncs = db.query(SyncRecord).filter(
            SyncRecord.school_id == current_user.school_id
        ).count()
        
        pending_syncs = db.query(SyncRecord).filter(
            SyncRecord.school_id == current_user.school_id,
            SyncRecord.status == SyncStatus.PENDING
        ).count()
        
        completed_syncs = db.query(SyncRecord).filter(
            SyncRecord.school_id == current_user.school_id,
            SyncRecord.status == SyncStatus.COMPLETED
        ).count()
        
        failed_syncs = db.query(SyncRecord).filter(
            SyncRecord.school_id == current_user.school_id,
            SyncRecord.status == SyncStatus.FAILED
        ).count()
        
        conflicts = db.query(SyncConflict).join(SyncRecord).filter(
            SyncRecord.school_id == current_user.school_id,
            SyncConflict.is_resolved == False
        ).count()
        
        # Message stats
        total_messages = db.query(Message).filter(
            Message.school_id == current_user.school_id
        ).count()
        
        active_threads = db.query(MessageThread).filter(
            MessageThread.school_id == current_user.school_id
        ).count()
        
        # Device stats
        active_devices = db.query(DeviceRegistration).filter(
            DeviceRegistration.school_id == current_user.school_id,
            DeviceRegistration.is_active == True,
            DeviceRegistration.is_online == True
        ).count()
        
        offline_devices = db.query(DeviceRegistration).filter(
            DeviceRegistration.school_id == current_user.school_id,
            DeviceRegistration.is_active == True,
            DeviceRegistration.is_online == False
        ).count()
        
        # Notification stats
        pending_notifications = db.query(Notification).filter(
            Notification.school_id == current_user.school_id,
            Notification.status == NotificationStatus.PENDING
        ).count()
        
        # Connection stats
        connection_stats = connection_manager.get_connection_stats()
        
        return ServiceStats(
            sync_stats=SyncStats(
                total_syncs=total_syncs,
                pending_syncs=pending_syncs,
                completed_syncs=completed_syncs,
                failed_syncs=failed_syncs,
                conflicts=conflicts,
                average_sync_time=0.0  # Calculate if needed
            ),
            messaging_stats=MessagingStats(
                total_messages=total_messages,
                sent_messages=total_messages,  # Simplified
                delivered_messages=total_messages,  # Simplified
                read_messages=total_messages,  # Simplified
                active_threads=active_threads,
                active_connections=connection_stats["total_connections"]
            ),
            active_devices=active_devices,
            offline_devices=offline_devices,
            pending_notifications=pending_notifications
        )
        
    except Exception as e:
        logger.error(f"Error getting service stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get service stats")

# === ADMIN ENDPOINTS ===

@app.post("/api/v1/admin/cleanup")
async def cleanup_data(
    current_user: CurrentUser = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Clean up expired and old data (admin only)"""
    try:
        result = DatabaseManager.cleanup_expired_data()
        return MessageResponse(
            message=f"Cleanup completed: {result.get('expired_offline_data', 0)} offline data, "
                   f"{result.get('old_notifications', 0)} notifications, "
                   f"{result.get('inactive_connections', 0)} connections cleaned"
        )
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Cleanup failed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
