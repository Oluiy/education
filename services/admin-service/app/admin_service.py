"""
Admin Service - Core business logic and services
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import httpx
import os
from pathlib import Path

from .models import (
    AdminUser, School, Department, AuditLog, Report, 
    SystemConfig, SystemAlert, BackgroundTask, DataExport
)
from .schemas import (
    AdminUserCreate, AdminUserUpdate, AdminUserResponse,
    SchoolCreate, SchoolUpdate, SchoolResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    ReportCreate, ReportResponse, DataExportCreate, DataExportResponse,
    SystemAlertCreate, SystemAlertResponse, AnalyticsRequest, AnalyticsResponse,
    DashboardStats
)
from .database import get_db_session
from .auth import CurrentAdminUser, create_audit_log

logger = logging.getLogger(__name__)

class AdminService:
    """Main admin service for managing school administration"""
    
    def __init__(self):
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
        self.content_service_url = os.getenv("CONTENT_QUIZ_SERVICE_URL", "http://localhost:8002")
        self.assistant_service_url = os.getenv("ASSISTANT_SERVICE_URL", "http://localhost:8003")
        self.reports_dir = Path(os.getenv("REPORTS_DIR", "reports"))
        self.reports_dir.mkdir(exist_ok=True)
        self.uploads_dir = Path(os.getenv("UPLOAD_DIR", "uploads"))
        self.uploads_dir.mkdir(exist_ok=True)
    
    async def get_dashboard_stats(
        self, 
        school_id: int, 
        current_admin: CurrentAdminUser,
        db: Session
    ) -> DashboardStats:
        """Get dashboard statistics for a school"""
        try:
            # Get basic counts from other services
            stats = await self._fetch_service_stats(school_id)
            
            # Get recent activities
            recent_activities = await self._get_recent_activities(school_id, db)
            
            # Get system health
            system_health = await self._get_system_health()
            
            # Get alerts count
            alerts_count = db.query(SystemAlert).filter(
                or_(
                    SystemAlert.school_id == school_id,
                    SystemAlert.is_system_wide == True
                ),
                SystemAlert.is_active == True
            ).count()
            
            # Get pending tasks
            pending_tasks = db.query(BackgroundTask).filter(
                BackgroundTask.school_id == school_id,
                BackgroundTask.status.in_(["pending", "running"])
            ).count()
            
            return DashboardStats(
                school_id=school_id,
                total_users=stats.get("total_users", 0),
                total_students=stats.get("total_students", 0),
                total_teachers=stats.get("total_teachers", 0),
                total_classes=stats.get("total_classes", 0),
                total_subjects=stats.get("total_subjects", 0),
                active_sessions=stats.get("active_sessions", 0),
                recent_activities=recent_activities,
                system_health=system_health,
                alerts_count=alerts_count,
                pending_tasks=pending_tasks
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            raise
    
    async def _fetch_service_stats(self, school_id: int) -> Dict[str, Any]:
        """Fetch statistics from other services"""
        stats = {}
        
        try:
            # Fetch from auth service
            async with httpx.AsyncClient() as client:
                # Get user stats
                response = await client.get(f"{self.auth_service_url}/api/v1/admin/schools/{school_id}/stats")
                if response.status_code == 200:
                    auth_stats = response.json()
                    stats.update(auth_stats)
                
                # Get content stats
                response = await client.get(f"{self.content_service_url}/api/v1/admin/schools/{school_id}/stats")
                if response.status_code == 200:
                    content_stats = response.json()
                    stats.update(content_stats)
                
                # Get assistant stats
                response = await client.get(f"{self.assistant_service_url}/api/v1/admin/schools/{school_id}/stats")
                if response.status_code == 200:
                    assistant_stats = response.json()
                    stats.update(assistant_stats)
                    
        except Exception as e:
            logger.error(f"Error fetching service stats: {str(e)}")
        
        return stats
    
    async def _get_recent_activities(self, school_id: int, db: Session) -> List[Dict[str, Any]]:
        """Get recent activities for dashboard"""
        try:
            activities = db.query(AuditLog).filter(
                AuditLog.school_id == school_id
            ).order_by(desc(AuditLog.timestamp)).limit(10).all()
            
            return [
                {
                    "id": activity.id,
                    "action": activity.action,
                    "resource_type": activity.resource_type,
                    "resource_id": activity.resource_id,
                    "timestamp": activity.timestamp,
                    "success": activity.success,
                    "admin_user_id": activity.admin_user_id
                }
                for activity in activities
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent activities: {str(e)}")
            return []
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        health = {
            "status": "healthy",
            "services": {},
            "last_check": datetime.utcnow()
        }
        
        # Check service health
        services = [
            ("auth", self.auth_service_url),
            ("content", self.content_service_url),
            ("assistant", self.assistant_service_url)
        ]
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                for service_name, service_url in services:
                    try:
                        response = await client.get(f"{service_url}/health")
                        health["services"][service_name] = {
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "response_time": response.elapsed.total_seconds() if response.elapsed else 0
                        }
                    except Exception as e:
                        health["services"][service_name] = {
                            "status": "unhealthy",
                            "error": str(e)
                        }
        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")
        
        return health
    
    async def create_school(
        self, 
        school_data: SchoolCreate, 
        current_admin: CurrentAdminUser,
        db: Session
    ) -> SchoolResponse:
        """Create a new school"""
        try:
            # Create school record
            school = School(
                school_id=school_data.school_id,
                name=school_data.name,
                code=school_data.code,
                address=school_data.address,
                phone=school_data.phone,
                email=school_data.email,
                website=school_data.website,
                principal_name=school_data.principal_name,
                principal_email=school_data.principal_email,
                established_date=school_data.established_date,
                school_type=school_data.school_type,
                settings=school_data.settings or {},
                features_enabled=school_data.features_enabled or {},
                subscription_tier=school_data.subscription_tier
            )
            
            db.add(school)
            db.commit()
            db.refresh(school)
            
            # Create audit log
            create_audit_log(
                db=db,
                admin_user_id=current_admin.id,
                school_id=school.school_id,
                action="CREATE",
                resource_type="SCHOOL",
                resource_id=str(school.id),
                new_values=school_data.dict(),
                metadata={"created_by": current_admin.username}
            )
            
            return SchoolResponse.from_orm(school)
            
        except Exception as e:
            logger.error(f"Error creating school: {str(e)}")
            raise
    
    async def update_school(
        self, 
        school_id: int,
        school_data: SchoolUpdate, 
        current_admin: CurrentAdminUser,
        db: Session
    ) -> SchoolResponse:
        """Update a school"""
        try:
            school = db.query(School).filter(School.school_id == school_id).first()
            if not school:
                raise ValueError("School not found")
            
            # Store old values for audit
            old_values = {
                "name": school.name,
                "code": school.code,
                "address": school.address,
                "phone": school.phone,
                "email": school.email,
                "website": school.website,
                "principal_name": school.principal_name,
                "principal_email": school.principal_email,
                "school_type": school.school_type,
                "settings": school.settings,
                "features_enabled": school.features_enabled,
                "subscription_tier": school.subscription_tier,
                "is_active": school.is_active,
                "is_verified": school.is_verified
            }
            
            # Update fields
            update_data = school_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(school, field, value)
            
            school.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(school)
            
            # Create audit log
            create_audit_log(
                db=db,
                admin_user_id=current_admin.id,
                school_id=school.school_id,
                action="UPDATE",
                resource_type="SCHOOL",
                resource_id=str(school.id),
                old_values=old_values,
                new_values=update_data,
                metadata={"updated_by": current_admin.username}
            )
            
            return SchoolResponse.from_orm(school)
            
        except Exception as e:
            logger.error(f"Error updating school: {str(e)}")
            raise
    
    async def get_analytics(
        self, 
        request: AnalyticsRequest, 
        current_admin: CurrentAdminUser,
        db: Session
    ) -> AnalyticsResponse:
        """Get analytics data"""
        try:
            # This would integrate with other services to get comprehensive analytics
            # For now, return basic audit log analytics
            
            query = db.query(AuditLog).filter(AuditLog.school_id == request.school_id)
            
            if request.date_range_start:
                query = query.filter(AuditLog.timestamp >= request.date_range_start)
            if request.date_range_end:
                query = query.filter(AuditLog.timestamp <= request.date_range_end)
            
            if request.metric_type == "user_activity":
                # Group by action type
                results = query.with_entities(
                    AuditLog.action,
                    func.count(AuditLog.id).label('count')
                ).group_by(AuditLog.action).all()
                
                data = [{"action": r.action, "count": r.count} for r in results]
                
            elif request.metric_type == "resource_usage":
                # Group by resource type
                results = query.with_entities(
                    AuditLog.resource_type,
                    func.count(AuditLog.id).label('count')
                ).group_by(AuditLog.resource_type).all()
                
                data = [{"resource_type": r.resource_type, "count": r.count} for r in results]
                
            else:
                # Default: activity over time
                results = query.with_entities(
                    func.date(AuditLog.timestamp).label('date'),
                    func.count(AuditLog.id).label('count')
                ).group_by(func.date(AuditLog.timestamp)).all()
                
                data = [{"date": str(r.date), "count": r.count} for r in results]
            
            # Calculate summary
            total_count = sum(item.get('count', 0) for item in data)
            
            return AnalyticsResponse(
                metric_type=request.metric_type,
                data=data,
                summary={
                    "total_count": total_count,
                    "date_range": {
                        "start": request.date_range_start,
                        "end": request.date_range_end
                    }
                },
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise
    
    async def create_system_alert(
        self, 
        alert_data: SystemAlertCreate, 
        current_admin: CurrentAdminUser,
        db: Session
    ) -> SystemAlertResponse:
        """Create a system alert"""
        try:
            alert = SystemAlert(
                school_id=alert_data.school_id,
                title=alert_data.title,
                message=alert_data.message,
                alert_type=alert_data.alert_type,
                severity=alert_data.severity,
                target_roles=alert_data.target_roles,
                target_users=alert_data.target_users,
                is_dismissible=alert_data.is_dismissible,
                auto_dismiss_after=alert_data.auto_dismiss_after,
                is_system_wide=alert_data.is_system_wide,
                expires_at=alert_data.expires_at
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # Create audit log
            create_audit_log(
                db=db,
                admin_user_id=current_admin.id,
                school_id=alert_data.school_id or 0,
                action="CREATE",
                resource_type="ALERT",
                resource_id=str(alert.id),
                new_values=alert_data.dict(),
                metadata={"created_by": current_admin.username}
            )
            
            return SystemAlertResponse.from_orm(alert)
            
        except Exception as e:
            logger.error(f"Error creating system alert: {str(e)}")
            raise
    
    async def get_audit_logs(
        self, 
        school_id: int, 
        current_admin: CurrentAdminUser,
        db: Session,
        page: int = 1,
        per_page: int = 50,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get audit logs with filtering and pagination"""
        try:
            query = db.query(AuditLog).filter(AuditLog.school_id == school_id)
            
            # Apply filters
            if action:
                query = query.filter(AuditLog.action == action)
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            if date_from:
                query = query.filter(AuditLog.timestamp >= date_from)
            if date_to:
                query = query.filter(AuditLog.timestamp <= date_to)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            logs = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(per_page).all()
            
            # Calculate pagination info
            pages = (total + per_page - 1) // per_page
            has_next = page < pages
            has_prev = page > 1
            
            return {
                "items": [
                    {
                        "id": log.id,
                        "action": log.action,
                        "resource_type": log.resource_type,
                        "resource_id": log.resource_id,
                        "timestamp": log.timestamp,
                        "success": log.success,
                        "admin_user_id": log.admin_user_id,
                        "ip_address": log.ip_address,
                        "metadata": log.metadata
                    }
                    for log in logs
                ],
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            raise
    
    async def export_data(
        self, 
        export_request: DataExportCreate, 
        current_admin: CurrentAdminUser,
        db: Session
    ) -> DataExportResponse:
        """Create data export request"""
        try:
            # Create export record
            export = DataExport(
                school_id=export_request.school_id,
                requested_by_admin_id=current_admin.id,
                export_type=export_request.export_type,
                file_format=export_request.file_format,
                date_range_start=export_request.date_range_start,
                date_range_end=export_request.date_range_end,
                filters=export_request.filters,
                status="pending",
                expires_at=datetime.utcnow() + timedelta(days=7)  # Expire in 7 days
            )
            
            db.add(export)
            db.commit()
            db.refresh(export)
            
            # TODO: Queue background task to process export
            # For now, just mark as processing
            export.status = "processing"
            db.commit()
            
            # Create audit log
            create_audit_log(
                db=db,
                admin_user_id=current_admin.id,
                school_id=export_request.school_id,
                action="EXPORT",
                resource_type="DATA",
                resource_id=str(export.id),
                new_values=export_request.dict(),
                metadata={"requested_by": current_admin.username}
            )
            
            return DataExportResponse.from_orm(export)
            
        except Exception as e:
            logger.error(f"Error creating data export: {str(e)}")
            raise

# Initialize service instance
admin_service = AdminService()
