from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SubscriptionPlan(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class SchoolStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    CANCELLED = "cancelled"

# Request schemas
class SchoolCreate(BaseModel):
    name: str
    domain: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_person: Optional[str] = None
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE

class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    contact_person: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    status: Optional[SchoolStatus] = None

class SchoolAdminCreate(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str
    role: str = "principal"
    permissions: Optional[Dict[str, Any]] = None
    is_primary: bool = False

# Response schemas
class SchoolResponse(BaseModel):
    id: int
    name: str
    domain: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    contact_person: Optional[str]
    subscription_plan: SubscriptionPlan
    status: SchoolStatus
    total_students: int
    total_teachers: int
    total_admins: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SchoolAdminResponse(BaseModel):
    id: int
    school_id: int
    user_id: int
    email: str
    full_name: str
    role: str
    is_primary: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlatformStatsResponse(BaseModel):
    total_schools: int
    active_schools: int
    new_schools_today: int
    total_users: int
    total_students: int
    total_teachers: int
    total_admins: int
    active_users_today: int
    monthly_revenue: float
    total_revenue: float
    avg_response_time: float
    uptime_percentage: float
    date: datetime
    
    class Config:
        from_attributes = True

class RevenueStatsResponse(BaseModel):
    monthly_revenue: float
    total_revenue: float
    revenue_by_plan: Dict[str, float]
    subscription_count: Dict[str, int]
    growth_rate: float

class SchoolListResponse(BaseModel):
    schools: List[SchoolResponse]
    total_count: int
    page: int
    per_page: int
