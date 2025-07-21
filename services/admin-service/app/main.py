"""
EduNerve Admin Service - Main FastAPI Application
School administration, user management, analytics, and system oversight
"""

from fastapi import FastAPI, HTTPException, Request, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
import uvicorn
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
# Import security modules
from app.cors_config import apply_secure_cors
from app.error_handling import (
    SecureErrorHandler, 
    ErrorResponseHandler, 
    SecurityError
)
from app.security_config import SecurityConfig, get_security_headers

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from .database import create_tables, get_db
from .models import (
    AdminUser, School, Department, AuditLog, Report, 
    SystemConfig, SystemAlert, BackgroundTask, DataExport
)
from .schemas import (
    AdminUserCreate, AdminUserUpdate, AdminUserResponse,
    SchoolCreate, SchoolUpdate, SchoolResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    AuditLogResponse, ReportCreate, ReportResponse,
    SystemAlertCreate, SystemAlertResponse, SystemConfigCreate, SystemConfigUpdate, SystemConfigResponse,
    DataExportCreate, DataExportResponse, AnalyticsRequest, AnalyticsResponse,
    DashboardStats, MessageResponse, ErrorResponse, PaginatedResponse
)
from .auth import (
    get_current_user, get_current_admin_user, get_current_super_admin, 
    get_current_school_admin, CurrentUser, CurrentAdminUser, create_audit_log
)
from .admin_service import admin_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting EduNerve Admin Service...")
    
    # Create database tables
    create_tables()
    logger.info("✅ Database tables created successfully")
    
    # Create required directories
    os.makedirs("reports", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    logger.info("✅ Admin Service startup complete")
    yield
    
    # Shutdown
    logger.info("🔽 Shutting down Admin Service...")
    logger.info("✅ Admin Service shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="EduNerve Admin Service",
    description="School administration, user management, analytics, and system oversight",
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

# Mount static files
app.mount("/reports", StaticFiles(directory="reports"), name="reports")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "admin-service"}

# === DASHBOARD ENDPOINTS ===

@app.get("/api/v1/admin/dashboard", response_model=DashboardStats)
async def get_dashboard(
    current_admin: CurrentAdminUser = Depends(get_current_school_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    try:
        dashboard = await admin_service.get_dashboard_stats(
            school_id=current_admin.school_id,
            current_admin=current_admin,
            db=db
        )
        return dashboard
        
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

# === SCHOOL MANAGEMENT ENDPOINTS ===

@app.post("/api/v1/admin/schools", response_model=SchoolResponse)
async def create_school(
    school_data: SchoolCreate,
    current_admin: CurrentAdminUser = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new school (super admin only)"""
    try:
        school = await admin_service.create_school(
            school_data=school_data,
            current_admin=current_admin,
            db=db
        )
        return school
        
    except Exception as e:
        logger.error(f"Error creating school: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create school")

@app.get("/api/v1/admin/schools", response_model=List[SchoolResponse])
async def get_schools(
    current_admin: CurrentAdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get schools (super admin sees all, others see only their school)"""
    try:
        if current_admin.system_role.value == "super_admin":
            schools = db.query(School).all()
        else:
            schools = db.query(School).filter(School.school_id == current_admin.school_id).all()
        
        return [SchoolResponse.from_orm(school) for school in schools]
        
    except Exception as e:
        logger.error(f"Error getting schools: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get schools")

@app.get("/api/v1/admin/schools/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: int,
    current_admin: CurrentAdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get school details"""
    try:
        # Check access
        if current_admin.system_role.value != "super_admin" and current_admin.school_id != school_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        school = db.query(School).filter(School.school_id == school_id).first()
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        
        return SchoolResponse.from_orm(school)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting school: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get school")

@app.put("/api/v1/admin/schools/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: int,
    school_data: SchoolUpdate,
    current_admin: CurrentAdminUser = Depends(get_current_school_admin),
    db: Session = Depends(get_db)
):
    """Update school details"""
    try:
        # Check access
        if current_admin.system_role.value != "super_admin" and current_admin.school_id != school_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        school = await admin_service.update_school(
            school_id=school_id,
            school_data=school_data,
            current_admin=current_admin,
            db=db
        )
        return school
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating school: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update school")

# === ADMIN USER MANAGEMENT ENDPOINTS ===

@app.post("/api/v1/admin/users", response_model=AdminUserResponse)
async def create_admin_user(
    user_data: AdminUserCreate,
    current_admin: CurrentAdminUser = Depends(get_current_school_admin),
    db: Session = Depends(get_db)
):
    """Create a new admin user"""
    try:
        # Check if user already exists
        existing_user = db.query(AdminUser).filter(
            AdminUser.user_id == user_data.user_id,
            AdminUser.school_id == user_data.school_id
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Admin user already exists")
        
        # Create admin user
        admin_user = AdminUser(
            user_id=user_data.user_id,
            school_id=user_data.school_id,
            system_role=user_data.system_role,
            permissions=user_data.permissions or {},
            departments=user_data.departments or [],
            employee_id=user_data.employee_id,
            job_title=user_data.job_title,
            phone=user_data.phone,
            emergency_contact=user_data.emergency_contact or {}
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Create audit log
        create_audit_log(
            db=db,
            admin_user_id=current_admin.id,
            school_id=user_data.school_id,
            action="CREATE",
            resource_type="ADMIN_USER",
            resource_id=str(admin_user.id),
            new_values=user_data.dict()
        )
        
        return AdminUserResponse.from_orm(admin_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create admin user")

@app.get("/api/v1/admin/users", response_model=List[AdminUserResponse])
async def get_admin_users(
    school_id: Optional[int] = Query(None),
    current_admin: CurrentAdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin users"""
    try:
        query = db.query(AdminUser)
        
        if current_admin.system_role.value == "super_admin":
            if school_id:
                query = query.filter(AdminUser.school_id == school_id)
        else:
            query = query.filter(AdminUser.school_id == current_admin.school_id)
        
        admin_users = query.all()
        return [AdminUserResponse.from_orm(user) for user in admin_users]
        
    except Exception as e:
        logger.error(f"Error getting admin users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get admin users")

# === DEPARTMENT MANAGEMENT ENDPOINTS ===

@app.post("/api/v1/admin/departments", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate,
    current_admin: CurrentAdminUser = Depends(get_current_school_admin),
    db: Session = Depends(get_db)
):
    """Create a new department"""
    try:
        # Check access
        if current_admin.system_role.value != "super_admin" and current_admin.school_id != department_data.school_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if department already exists
        existing_dept = db.query(Department).filter(
            Department.school_id == department_data.school_id,
            Department.code == department_data.code
        ).first()
        
        if existing_dept:
            raise HTTPException(status_code=400, detail="Department with this code already exists")
        
        # Create department
        department = Department(
            school_id=department_data.school_id,
            name=department_data.name,
            code=department_data.code,
            description=department_data.description,
            head_user_id=department_data.head_user_id,
            head_name=department_data.head_name,
            head_email=department_data.head_email,
            budget=department_data.budget,
            settings=department_data.settings or {}
        )
        
        db.add(department)
        db.commit()
        db.refresh(department)
        
        # Create audit log
        create_audit_log(
            db=db,
            admin_user_id=current_admin.id,
            school_id=department_data.school_id,
            action="CREATE",
            resource_type="DEPARTMENT",
            resource_id=str(department.id),
            new_values=department_data.dict()
        )
        
        return DepartmentResponse.from_orm(department)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating department: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create department")

@app.get("/api/v1/admin/departments", response_model=List[DepartmentResponse])
async def get_departments(
    school_id: Optional[int] = Query(None),
    current_admin: CurrentAdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get departments"""
    try:
        query = db.query(Department)
        
        if current_admin.system_role.value == "super_admin":
            if school_id:
                query = query.filter(Department.school_id == school_id)
        else:
            query = query.filter(Department.school_id == current_admin.school_id)
        
        departments = query.all()
        return [DepartmentResponse.from_orm(dept) for dept in departments]
        
    except Exception as e:
        logger.error(f"Error getting departments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get departments")

# === ANALYTICS ENDPOINTS ===

@app.post("/api/v1/admin/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    request: AnalyticsRequest,
    current_admin: CurrentAdminUser = Depends(get_current_school_admin),
    db: Session = Depends(get_db)
):
    """Get analytics data"""
    try:
        # Check access
        if current_admin.system_role.value != "super_admin" and current_admin.school_id != request.school_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        analytics = await admin_service.get_analytics(
            request=request,
            current_admin=current_admin,
            db=db
        )
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

# === AUDIT LOG ENDPOINTS ===

@app.get("/api/v1/admin/audit-logs", response_model=PaginatedResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_admin: CurrentAdminUser = Depends(get_current_school_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs"""
    try:
        logs = await admin_service.get_audit_logs(
            school_id=current_admin.school_id,
            current_admin=current_admin,
            db=db,
            page=page,
            per_page=per_page,
            action=action,
            resource_type=resource_type,
            date_from=date_from,
            date_to=date_to
        )
        
        return PaginatedResponse(**logs)
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get audit logs")

# === SYSTEM ALERT ENDPOINTS ===

@app.post("/api/v1/admin/alerts", response_model=SystemAlertResponse)
async def create_system_alert(
    alert_data: SystemAlertCreate,
    current_admin: CurrentAdminUser = Depends(get_current_school_admin),
    db: Session = Depends(get_db)
):
    """Create a system alert"""
    try:
        alert = await admin_service.create_system_alert(
            alert_data=alert_data,
            current_admin=current_admin,
            db=db
        )
        return alert
        
    except Exception as e:
        logger.error(f"Error creating system alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create system alert")

@app.get("/api/v1/admin/alerts", response_model=List[SystemAlertResponse])
async def get_system_alerts(
    is_active: Optional[bool] = Query(True),
    current_admin: CurrentAdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system alerts"""
    try:
        query = db.query(SystemAlert).filter(
            or_(
                SystemAlert.school_id == current_admin.school_id,
                SystemAlert.is_system_wide == True
            )
        )
        
        if is_active is not None:
            query = query.filter(SystemAlert.is_active == is_active)
        
        alerts = query.order_by(desc(SystemAlert.created_at)).all()
        return [SystemAlertResponse.from_orm(alert) for alert in alerts]
        
    except Exception as e:
        logger.error(f"Error getting system alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system alerts")

# === DATA EXPORT ENDPOINTS ===

@app.post("/api/v1/admin/exports", response_model=DataExportResponse)
async def create_data_export(
    export_request: DataExportCreate,
    current_admin: CurrentAdminUser = Depends(get_current_school_admin),
    db: Session = Depends(get_db)
):
    """Create data export request"""
    try:
        # Check access
        if current_admin.system_role.value != "super_admin" and current_admin.school_id != export_request.school_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        export = await admin_service.export_data(
            export_request=export_request,
            current_admin=current_admin,
            db=db
        )
        return export
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating data export: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create data export")

@app.get("/api/v1/admin/exports", response_model=List[DataExportResponse])
async def get_data_exports(
    current_admin: CurrentAdminUser = Depends(get_current_school_admin),
    db: Session = Depends(get_db)
):
    """Get data exports"""
    try:
        exports = db.query(DataExport).filter(
            DataExport.school_id == current_admin.school_id
        ).order_by(desc(DataExport.created_at)).all()
        
        return [DataExportResponse.from_orm(export) for export in exports]
        
    except Exception as e:
        logger.error(f"Error getting data exports: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get data exports")

# === SYSTEM CONFIG ENDPOINTS ===

@app.get("/api/v1/admin/config", response_model=List[SystemConfigResponse])
async def get_system_config(
    current_admin: CurrentAdminUser = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get system configuration (super admin only)"""
    try:
        configs = db.query(SystemConfig).all()
        return [SystemConfigResponse.from_orm(config) for config in configs]
        
    except Exception as e:
        logger.error(f"Error getting system config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system config")

@app.post("/api/v1/admin/config", response_model=SystemConfigResponse)
async def create_system_config(
    config_data: SystemConfigCreate,
    current_admin: CurrentAdminUser = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Create system configuration (super admin only)"""
    try:
        config = SystemConfig(
            key=config_data.key,
            value=config_data.value,
            description=config_data.description,
            is_public=config_data.is_public,
            is_required=config_data.is_required,
            data_type=config_data.data_type
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        return SystemConfigResponse.from_orm(config)
        
    except Exception as e:
        logger.error(f"Error creating system config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create system config")

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
    port = int(os.getenv("PORT", 8004))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
