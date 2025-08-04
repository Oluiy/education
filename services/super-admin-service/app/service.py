from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from .models import School, SchoolAdmin, SchoolSubscription, PlatformStats, SubscriptionPlan, SchoolStatus
from .schemas import SchoolCreate, SchoolUpdate, SchoolAdminCreate
from datetime import datetime, timedelta
from typing import List, Optional, Dict

class SuperAdminService:
    
    def __init__(self, db: Session):
        self.db = db
    
    # School management
    def create_school(self, school_data: SchoolCreate, admin_data: SchoolAdminCreate) -> School:
        """Create a new school with its primary admin"""
        
        # Check if domain already exists
        existing_school = self.db.query(School).filter(School.domain == school_data.domain).first()
        if existing_school:
            raise ValueError(f"School with domain {school_data.domain} already exists")
        
        # Create school
        school = School(**school_data.dict())
        school.status = SchoolStatus.PENDING
        self.db.add(school)
        self.db.flush()
        
        # Create school admin
        admin = SchoolAdmin(
            school_id=school.id,
            **admin_data.dict(),
            is_primary=True
        )
        self.db.add(admin)
        
        # Update school admin count
        school.total_admins = 1
        
        self.db.commit()
        self.db.refresh(school)
        return school
    
    def get_schools(self, skip: int = 0, limit: int = 100, status: Optional[SchoolStatus] = None) -> List[School]:
        """Get list of schools with pagination"""
        query = self.db.query(School)
        
        if status:
            query = query.filter(School.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_school_by_id(self, school_id: int) -> Optional[School]:
        """Get school by ID"""
        return self.db.query(School).filter(School.id == school_id).first()
    
    def update_school(self, school_id: int, school_data: SchoolUpdate) -> Optional[School]:
        """Update school details"""
        school = self.get_school_by_id(school_id)
        if not school:
            return None
        
        update_data = school_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(school, field, value)
        
        school.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(school)
        return school
    
    def suspend_school(self, school_id: int, reason: str = None) -> Optional[School]:
        """Suspend a school"""
        school = self.get_school_by_id(school_id)
        if not school:
            return None
        
        school.status = SchoolStatus.SUSPENDED
        school.suspended_at = datetime.utcnow()
        school.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(school)
        return school
    
    def activate_school(self, school_id: int) -> Optional[School]:
        """Activate a school"""
        school = self.get_school_by_id(school_id)
        if not school:
            return None
        
        school.status = SchoolStatus.ACTIVE
        school.activated_at = datetime.utcnow()
        school.updated_at = datetime.utcnow()
        school.suspended_at = None
        
        self.db.commit()
        self.db.refresh(school)
        return school
    
    # Analytics and stats
    def get_platform_stats(self) -> Optional[PlatformStats]:
        """Get latest platform statistics"""
        return self.db.query(PlatformStats).order_by(desc(PlatformStats.date)).first()
    
    def calculate_current_stats(self) -> Dict:
        """Calculate current platform statistics"""
        today = datetime.utcnow().date()
        
        # School metrics
        total_schools = self.db.query(School).count()
        active_schools = self.db.query(School).filter(School.status == SchoolStatus.ACTIVE).count()
        new_schools_today = self.db.query(School).filter(
            func.date(School.created_at) == today
        ).count()
        
        # Subscription metrics
        subscriptions = self.db.query(SchoolSubscription).filter(
            SchoolSubscription.status == "active"
        ).all()
        
        monthly_revenue = sum(sub.amount for sub in subscriptions if sub.billing_cycle == "monthly")
        yearly_revenue = sum(sub.amount for sub in subscriptions if sub.billing_cycle == "yearly")
        total_revenue = monthly_revenue + (yearly_revenue / 12)  # Normalize to monthly
        
        return {
            "total_schools": total_schools,
            "active_schools": active_schools,
            "new_schools_today": new_schools_today,
            "monthly_revenue": monthly_revenue,
            "total_revenue": total_revenue,
            "date": datetime.utcnow()
        }
    
    def get_revenue_stats(self) -> Dict:
        """Get detailed revenue statistics"""
        subscriptions = self.db.query(SchoolSubscription).filter(
            SchoolSubscription.status == "active"
        ).all()
        
        revenue_by_plan = {}
        subscription_count = {}
        
        for plan in SubscriptionPlan:
            plan_subs = [s for s in subscriptions if s.plan == plan]
            revenue_by_plan[plan.value] = sum(s.amount for s in plan_subs)
            subscription_count[plan.value] = len(plan_subs)
        
        total_revenue = sum(revenue_by_plan.values())
        monthly_revenue = sum(s.amount for s in subscriptions if s.billing_cycle == "monthly")
        
        # Calculate growth rate (simplified)
        last_month = datetime.utcnow().replace(day=1) - timedelta(days=1)
        previous_month_revenue = self.db.query(PlatformStats).filter(
            func.date_trunc('month', PlatformStats.date) == last_month.replace(day=1)
        ).first()
        
        growth_rate = 0.0
        if previous_month_revenue and previous_month_revenue.monthly_revenue > 0:
            growth_rate = ((monthly_revenue - previous_month_revenue.monthly_revenue) / 
                          previous_month_revenue.monthly_revenue) * 100
        
        return {
            "monthly_revenue": monthly_revenue,
            "total_revenue": total_revenue,
            "revenue_by_plan": revenue_by_plan,
            "subscription_count": subscription_count,
            "growth_rate": growth_rate
        }
    
    def update_school_user_counts(self, school_id: int, students: int = 0, teachers: int = 0, admins: int = 0):
        """Update user counts for a school"""
        school = self.get_school_by_id(school_id)
        if school:
            if students > 0:
                school.total_students = students
            if teachers > 0:
                school.total_teachers = teachers
            if admins > 0:
                school.total_admins = admins
            
            school.updated_at = datetime.utcnow()
            self.db.commit()
    
    def get_school_admins(self, school_id: int) -> List[SchoolAdmin]:
        """Get all admins for a school"""
        return self.db.query(SchoolAdmin).filter(
            and_(SchoolAdmin.school_id == school_id, SchoolAdmin.is_active == True)
        ).all()
