from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from .database import get_db
from .service import SuperAdminService
from .schemas import (
    SchoolCreate, SchoolUpdate, SchoolResponse, SchoolAdminCreate,
    PlatformStatsResponse, RevenueStatsResponse
)
from .models import SchoolStatus

app = FastAPI(
    title="EduNerve Super Admin Service",
    description="Super Admin service for managing schools and platform statistics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for super admin service
def get_super_admin_service(db: Session = Depends(get_db)):
    return SuperAdminService(db)

@app.get("/")
async def root():
    return {"message": "EduNerve Super Admin Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "super-admin-service"}

# School management endpoints
@app.post("/schools", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    school_data: SchoolCreate,
    admin_data: SchoolAdminCreate,
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Create a new school with primary admin"""
    try:
        school = service.create_school(school_data, admin_data)
        return school
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create school")

@app.get("/schools", response_model=List[SchoolResponse])
async def get_schools(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[SchoolStatus] = None,
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Get list of schools with pagination"""
    schools = service.get_schools(skip=skip, limit=limit, status=status)
    return schools

@app.get("/schools/{school_id}", response_model=SchoolResponse)
async def get_school(
    school_id: int,
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Get school by ID"""
    school = service.get_school_by_id(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school

@app.put("/schools/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: int,
    school_data: SchoolUpdate,
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Update school details"""
    school = service.update_school(school_id, school_data)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school

@app.patch("/schools/{school_id}/suspend")
async def suspend_school(
    school_id: int,
    reason: Optional[str] = None,
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Suspend a school"""
    school = service.suspend_school(school_id, reason)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return {"message": "School suspended successfully", "school_id": school_id}

@app.patch("/schools/{school_id}/activate")
async def activate_school(
    school_id: int,
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Activate a school"""
    school = service.activate_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return {"message": "School activated successfully", "school_id": school_id}

# Analytics endpoints
@app.get("/analytics/platform", response_model=PlatformStatsResponse)
async def get_platform_analytics(
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Get platform statistics"""
    stats = service.get_platform_stats()
    if not stats:
        # Return current calculated stats if no historical data
        current_stats = service.calculate_current_stats()
        return PlatformStatsResponse(**current_stats)
    return stats

@app.get("/analytics/revenue", response_model=RevenueStatsResponse)
async def get_revenue_analytics(
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Get revenue statistics"""
    revenue_stats = service.get_revenue_stats()
    return RevenueStatsResponse(**revenue_stats)

@app.get("/analytics/current")
async def get_current_stats(
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Get current platform statistics"""
    return service.calculate_current_stats()

# School admin management
@app.get("/schools/{school_id}/admins")
async def get_school_admins(
    school_id: int,
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Get all admins for a school"""
    school = service.get_school_by_id(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    admins = service.get_school_admins(school_id)
    return admins

@app.patch("/schools/{school_id}/user-counts")
async def update_school_user_counts(
    school_id: int,
    students: Optional[int] = None,
    teachers: Optional[int] = None,
    admins: Optional[int] = None,
    service: SuperAdminService = Depends(get_super_admin_service)
):
    """Update user counts for a school"""
    school = service.get_school_by_id(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    service.update_school_user_counts(
        school_id,
        students=students or 0,
        teachers=teachers or 0,
        admins=admins or 0
    )
    
    return {"message": "User counts updated successfully", "school_id": school_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
