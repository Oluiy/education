"""
Admin Models for EduNerve Platform
Administrative functions, user management, system monitoring
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    CONTENT_MANAGER = "content_manager"
    SUPPORT_AGENT = "support_agent"

class ActionType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    APPROVE = "approve"
    REJECT = "reject"
    SUSPEND = "suspend"
    RESTORE = "restore"

class SystemStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"
    OUTAGE = "outage"

class AdminUser(Base):
    """Admin user accounts with elevated privileges"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Admin details
    admin_role = Column(String(50), default=AdminRole.ADMIN.value)
    department = Column(String(100))
    employee_id = Column(String(50))
    
    # Permissions
    permissions = Column(JSON)  # List of specific permissions
    restricted_areas = Column(JSON)  # Areas admin cannot access
    
    # Access control
    ip_whitelist = Column(JSON)  # Allowed IP addresses
    requires_2fa = Column(Boolean, default=True)
    session_timeout = Column(Integer, default=3600)  # seconds
    
    # Status
    is_active = Column(Boolean, default=True)
    is_suspended = Column(Boolean, default=False)
    suspension_reason = Column(Text)
    
    # Audit trail
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    approved_by = Column(Integer, ForeignKey("admin_users.id"))
    last_login = Column(DateTime)
    last_activity = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_admin = relationship("AdminUser", remote_side=[id], foreign_keys=[created_by])
    approved_by_admin = relationship("AdminUser", remote_side=[id], foreign_keys=[approved_by])
    actions = relationship("AdminAction", back_populates="admin")

class AdminAction(Base):
    """Log of all admin actions for audit trail"""
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Action details
    action_type = Column(String(50), nullable=False)
    resource_type = Column(String(100))  # user, course, quiz, etc.
    resource_id = Column(Integer)
    
    # Action description
    action_description = Column(Text)
    affected_fields = Column(JSON)  # Fields that were changed
    old_values = Column(JSON)  # Previous values
    new_values = Column(JSON)  # New values
    
    # Context
    reason = Column(Text)  # Reason for the action
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Impact
    affected_users = Column(JSON)  # List of user IDs affected
    severity = Column(String(20))  # low, medium, high, critical
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    admin = relationship("AdminUser", back_populates="actions")

class UserModerationAction(Base):
    """User moderation actions (warnings, suspensions, bans)"""
    __tablename__ = "user_moderation_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Action details
    action_type = Column(String(50))  # warning, suspension, ban, restriction
    reason = Column(Text, nullable=False)
    violation_type = Column(String(100))  # spam, inappropriate_content, etc.
    
    # Evidence and context
    evidence_urls = Column(JSON)  # Screenshots, links, etc.
    reported_by_users = Column(JSON)  # User IDs who reported
    related_content = Column(JSON)  # Content IDs related to violation
    
    # Action parameters
    duration_days = Column(Integer)  # For temporary actions
    restrictions = Column(JSON)  # Specific restrictions applied
    
    # Status
    is_active = Column(Boolean, default=True)
    appealed = Column(Boolean, default=False)
    appeal_status = Column(String(20))  # pending, approved, rejected
    appeal_reason = Column(Text)
    
    # Timeline
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_until = Column(DateTime)
    appealed_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentModerationQueue(Base):
    """Queue for content that needs moderation"""
    __tablename__ = "content_moderation_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content details
    content_type = Column(String(50))  # course, quiz, comment, file, etc.
    content_id = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))  # Content creator
    
    # Moderation details
    reason_for_review = Column(String(100))  # user_report, auto_flagged, etc.
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Content snapshot
    content_snapshot = Column(JSON)  # Snapshot of content at time of flagging
    content_url = Column(String(500))
    
    # Reports and flags
    report_count = Column(Integer, default=0)
    reporter_ids = Column(JSON)  # Users who reported this content
    auto_flag_reasons = Column(JSON)  # Automated detection reasons
    
    # Moderation status
    status = Column(String(20), default="pending")  # pending, approved, rejected, escalated
    assigned_to = Column(Integer, ForeignKey("admin_users.id"))
    reviewed_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # Decision
    decision = Column(String(50))  # approved, removed, edited, restricted
    decision_reason = Column(Text)
    required_changes = Column(Text)
    
    # Timeline
    flagged_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime)
    reviewed_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemMonitoring(Base):
    """System health and performance monitoring"""
    __tablename__ = "system_monitoring"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Monitoring details
    timestamp = Column(DateTime, default=datetime.utcnow)
    service_name = Column(String(100))  # auth-service, content-service, etc.
    metric_name = Column(String(100))  # cpu_usage, memory_usage, response_time
    
    # Metric values
    value = Column(Float)
    unit = Column(String(20))  # percentage, seconds, MB, etc.
    
    # Status
    status = Column(String(20), default=SystemStatus.OPERATIONAL.value)
    threshold_warning = Column(Float)
    threshold_critical = Column(Float)
    
    # Additional data
    metadata = Column(JSON)  # Additional monitoring data
    
    # Alerting
    alert_sent = Column(Boolean, default=False)
    alert_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("admin_users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemAlert(Base):
    """System alerts and notifications for admins"""
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Alert details
    alert_type = Column(String(50))  # performance, security, error, maintenance
    severity = Column(String(20))  # info, warning, error, critical
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Source information
    source_service = Column(String(100))
    source_component = Column(String(100))
    
    # Alert data
    alert_data = Column(JSON)  # Detailed alert information
    affected_users = Column(Integer)  # Number of affected users
    
    # Resolution
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    acknowledged_by = Column(Integer, ForeignKey("admin_users.id"))
    acknowledged_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("admin_users.id"))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Timeline
    first_occurrence = Column(DateTime, default=datetime.utcnow)
    last_occurrence = Column(DateTime, default=datetime.utcnow)
    occurrence_count = Column(Integer, default=1)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSON)  # email, slack, sms
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FeatureFlag(Base):
    """Feature flags for gradual rollouts"""
    __tablename__ = "feature_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Feature details
    flag_key = Column(String(100), unique=True, nullable=False)
    name = Column(String(200))
    description = Column(Text)
    
    # Flag configuration
    is_enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Float, default=0.0)  # 0-100%
    
    # Targeting
    target_user_roles = Column(JSON)  # Specific user roles
    target_user_ids = Column(JSON)  # Specific user IDs
    target_conditions = Column(JSON)  # Complex targeting conditions
    
    # Environment
    environment = Column(String(50), default="production")
    
    # Metadata
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # Timeline
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdminDashboardWidget(Base):
    """Customizable dashboard widgets for admins"""
    __tablename__ = "admin_dashboard_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Widget details
    widget_type = Column(String(50))  # chart, metric, list, etc.
    widget_title = Column(String(200))
    widget_config = Column(JSON)  # Widget-specific configuration
    
    # Layout
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=1)
    height = Column(Integer, default=1)
    
    # Data source
    data_source = Column(String(100))  # API endpoint or data source
    refresh_interval = Column(Integer, default=300)  # seconds
    
    # Display options
    is_visible = Column(Boolean, default=True)
    show_title = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BulkOperation(Base):
    """Track bulk operations performed by admins"""
    __tablename__ = "bulk_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Operation details
    operation_type = Column(String(50))  # bulk_update, bulk_delete, bulk_import
    operation_name = Column(String(200))
    description = Column(Text)
    
    # Target data
    target_type = Column(String(100))  # users, courses, quizzes, etc.
    target_criteria = Column(JSON)  # Criteria for selecting targets
    target_count = Column(Integer)  # Number of items affected
    
    # Operation data
    operation_data = Column(JSON)  # Data for the operation
    
    # Progress tracking
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    progress_percentage = Column(Float, default=0.0)
    processed_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Results
    results_summary = Column(JSON)  # Summary of results
    error_details = Column(JSON)  # Details of any errors
    
    # Timeline
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_duration = Column(Integer)  # in seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemBackup(Base):
    """System backup tracking"""
    __tablename__ = "system_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Backup details
    backup_type = Column(String(50))  # full, incremental, differential
    backup_name = Column(String(200))
    description = Column(Text)
    
    # Backup scope
    databases = Column(JSON)  # List of databases backed up
    file_paths = Column(JSON)  # List of file paths backed up
    
    # Backup file details
    backup_file_path = Column(String(500))
    backup_file_size = Column(Integer)  # in bytes
    compression_ratio = Column(Float)
    
    # Backup status
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    progress_percentage = Column(Float, default=0.0)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_checksum = Column(String(64))
    verification_date = Column(DateTime)
    
    # Retention
    retention_days = Column(Integer, default=30)
    auto_delete_after = Column(DateTime)
    
    # Timeline
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
