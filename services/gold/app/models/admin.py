"""
Phase 15: Platform Administration Models
System administration and configuration models
"""
from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, ForeignKey, TIMESTAMP, BigInteger, Time
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import uuid


class SystemSetting(BaseModel):
    """System configuration setting model"""
    __tablename__ = "system_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    is_editable = Column(Boolean, default=True)
    requires_restart = Column(Boolean, default=False)
    validation_rules = Column(JSONB)
    default_value = Column(Text)
    
    # Audit
    last_modified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    last_modified_at = Column(TIMESTAMP(timezone=True))
    change_history = Column(JSONB, default=[])
    
    # Metadata
    metadata = Column(JSONB, default={})


class Role(BaseModel):
    """User role model"""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_code = Column(String(50), unique=True, nullable=False, index=True)
    role_name = Column(String(100), nullable=False)
    description = Column(Text)
    role_type = Column(String(50), nullable=False)
    is_system_role = Column(Boolean, default=False)
    
    # Permissions
    permissions = Column(JSONB, default=[])
    resource_access = Column(JSONB, default={})
    
    # Hierarchy
    parent_role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'))
    hierarchy_level = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default='ACTIVE')
    
    # Limits
    max_users = Column(Integer)
    current_user_count = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    user_assignments = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class UserRole(BaseModel):
    """User-role assignment model"""
    __tablename__ = "user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    
    # Assignment details
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    assigned_at = Column(TIMESTAMP(timezone=True))
    expires_at = Column(TIMESTAMP(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default='ACTIVE')
    
    # Scope
    scope_type = Column(String(50))
    scope_value = Column(String(100))
    
    # Metadata
    assignment_reason = Column(Text)
    metadata = Column(JSONB, default={})
    
    # Relationships
    role = relationship("Role", back_populates="user_assignments")


class Permission(BaseModel):
    """System permission model"""
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_code = Column(String(100), unique=True, nullable=False, index=True)
    permission_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Categorization
    module = Column(String(50), nullable=False)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    
    # Permission type
    permission_type = Column(String(50), default='STANDARD')
    risk_level = Column(String(20))
    
    # Requirements
    requires_approval = Column(Boolean, default=False)
    requires_mfa = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    metadata = Column(JSONB, default={})


class AuditLog(BaseModel):
    """Audit log model"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    log_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Event details
    event_type = Column(String(100), nullable=False)
    event_category = Column(String(50), nullable=False)
    event_name = Column(String(200), nullable=False)
    event_description = Column(Text)
    
    # User context
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    username = Column(String(100))
    user_ip_address = Column(String(50))
    user_agent = Column(Text)
    
    # Resource details
    resource_type = Column(String(100))
    resource_id = Column(String(100))
    resource_name = Column(String(200))
    
    # Action details
    action = Column(String(50), nullable=False)
    action_result = Column(String(20), nullable=False)
    
    # Data changes
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    changes = Column(JSONB)
    
    # Request details
    request_id = Column(String(100))
    session_id = Column(String(100))
    transaction_id = Column(String(100))
    
    # System context
    application_name = Column(String(100))
    module_name = Column(String(100))
    service_name = Column(String(100))
    
    # Location
    branch_id = Column(String(50))
    department = Column(String(100))
    
    # Security
    security_level = Column(String(20))
    requires_review = Column(Boolean, default=False)
    is_sensitive = Column(Boolean, default=False)
    
    # Error details
    error_message = Column(Text)
    error_code = Column(String(50))
    stack_trace = Column(Text)
    
    # Performance
    duration_ms = Column(Integer)
    
    # Metadata
    metadata = Column(JSONB, default={})
    tags = Column(JSONB, default=[])


class SystemHealth(BaseModel):
    """System health check model"""
    __tablename__ = "system_health"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    check_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Check details
    check_name = Column(String(200), nullable=False)
    check_type = Column(String(50), nullable=False)
    component_name = Column(String(100), nullable=False)
    
    # Health status
    health_status = Column(String(20), nullable=False)
    previous_status = Column(String(20))
    status_changed_at = Column(TIMESTAMP(timezone=True))
    
    # Metrics
    response_time_ms = Column(Integer)
    availability_percent = Column(Numeric(5, 2))
    error_rate_percent = Column(Numeric(5, 2))
    success_rate_percent = Column(Numeric(5, 2))
    
    # Thresholds
    warning_threshold = Column(JSONB)
    critical_threshold = Column(JSONB)
    
    # Check execution
    last_check_at = Column(TIMESTAMP(timezone=True), nullable=False)
    next_check_at = Column(TIMESTAMP(timezone=True))
    check_frequency_minutes = Column(Integer, default=5)
    
    # Results
    check_result = Column(JSONB)
    check_message = Column(Text)
    check_details = Column(JSONB)
    
    # Error tracking
    consecutive_failures = Column(Integer, default=0)
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    
    # Alert configuration
    alert_enabled = Column(Boolean, default=True)
    alert_channels = Column(JSONB, default=[])
    alert_recipients = Column(JSONB, default=[])
    
    # Status
    is_enabled = Column(Boolean, default=True)
    is_critical = Column(Boolean, default=False)
    
    # Metadata
    metadata = Column(JSONB, default={})


class SystemMetric(BaseModel):
    """System performance metric model"""
    __tablename__ = "system_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metric identity
    metric_name = Column(String(100), nullable=False)
    metric_type = Column(String(50), nullable=False)
    metric_category = Column(String(50), nullable=False)
    
    # Metric value
    metric_value = Column(Numeric(20, 4), nullable=False)
    metric_unit = Column(String(50))
    
    # Dimensions
    service_name = Column(String(100))
    module_name = Column(String(100))
    endpoint = Column(String(200))
    
    # Labels
    labels = Column(JSONB, default={})
    tags = Column(JSONB, default=[])
    
    # Time details
    recorded_at = Column(TIMESTAMP(timezone=True), nullable=False)
    time_bucket = Column(String(20))
    
    # Aggregation
    is_aggregated = Column(Boolean, default=False)
    sample_count = Column(Integer)
    min_value = Column(Numeric(20, 4))
    max_value = Column(Numeric(20, 4))
    avg_value = Column(Numeric(20, 4))
    sum_value = Column(Numeric(20, 4))
    
    # Metadata
    metadata = Column(JSONB, default={})


class NotificationTemplate(BaseModel):
    """Notification template model"""
    __tablename__ = "notification_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_code = Column(String(50), unique=True, nullable=False, index=True)
    template_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Template details
    notification_type = Column(String(50), nullable=False)
    template_category = Column(String(50), nullable=False)
    
    # Content
    subject_template = Column(Text)
    body_template = Column(Text, nullable=False)
    html_template = Column(Text)
    
    # Template engine
    template_engine = Column(String(50), default='JINJA2')
    template_variables = Column(JSONB, default=[])
    
    # Localization
    language = Column(String(10), default='en')
    supports_localization = Column(Boolean, default=False)
    
    # Delivery settings
    priority = Column(String(20), default='NORMAL')
    retry_policy = Column(JSONB)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    status = Column(String(20), default='ACTIVE')
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(TIMESTAMP(timezone=True))
    
    # Version control
    version = Column(String(20), default='1.0')
    parent_template_id = Column(UUID(as_uuid=True), ForeignKey('notification_templates.id'))
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))


class ScheduledJob(BaseModel):
    """Scheduled job model"""
    __tablename__ = "scheduled_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_code = Column(String(50), unique=True, nullable=False, index=True)
    job_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Job details
    job_type = Column(String(50), nullable=False)
    job_category = Column(String(50), nullable=False)
    
    # Execution
    handler_class = Column(String(200), nullable=False)
    handler_method = Column(String(100), nullable=False)
    parameters = Column(JSONB, default={})
    
    # Schedule
    schedule_expression = Column(String(100))
    interval_minutes = Column(Integer)
    scheduled_time = Column(Time)
    
    # Execution window
    execution_window_start = Column(Time)
    execution_window_end = Column(Time)
    
    # Status
    is_enabled = Column(Boolean, default=True)
    status = Column(String(20), default='SCHEDULED')
    
    # Execution tracking
    last_execution_at = Column(TIMESTAMP(timezone=True))
    last_execution_status = Column(String(20))
    last_execution_duration_ms = Column(Integer)
    last_execution_error = Column(Text)
    next_execution_at = Column(TIMESTAMP(timezone=True))
    
    # Statistics
    total_executions = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_duration_ms = Column(Integer)
    
    # Retry policy
    max_retries = Column(Integer, default=3)
    retry_delay_minutes = Column(Integer, default=5)
    current_retry_count = Column(Integer, default=0)
    
    # Timeout
    timeout_minutes = Column(Integer, default=60)
    
    # Alerts
    alert_on_failure = Column(Boolean, default=True)
    alert_recipients = Column(JSONB, default=[])
    
    # Priority
    priority = Column(Integer, default=5)
    
    # Dependencies
    depends_on_jobs = Column(JSONB, default=[])
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    executions = relationship("JobExecution", back_populates="job", cascade="all, delete-orphan")


class JobExecution(BaseModel):
    """Job execution history model"""
    __tablename__ = "job_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_code = Column(String(50), unique=True, nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey('scheduled_jobs.id', ondelete='CASCADE'))
    
    # Execution details
    execution_type = Column(String(50), nullable=False)
    started_at = Column(TIMESTAMP(timezone=True), nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True))
    duration_ms = Column(Integer)
    
    # Status
    execution_status = Column(String(20), nullable=False)
    
    # Results
    execution_result = Column(JSONB)
    rows_processed = Column(Integer)
    records_created = Column(Integer)
    records_updated = Column(Integer)
    records_deleted = Column(Integer)
    
    # Error details
    error_message = Column(Text)
    error_details = Column(JSONB)
    stack_trace = Column(Text)
    
    # Resource usage
    cpu_usage_percent = Column(Numeric(5, 2))
    memory_usage_mb = Column(Numeric(10, 2))
    
    # Logs
    execution_logs = Column(Text)
    log_file_path = Column(Text)
    
    # Triggered by
    triggered_by_user = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    trigger_context = Column(JSONB)
    
    # Retry info
    is_retry = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    parent_execution_id = Column(UUID(as_uuid=True), ForeignKey('job_executions.id'))
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    # Relationships
    job = relationship("ScheduledJob", back_populates="executions")


class FeatureFlag(BaseModel):
    """Feature flag model"""
    __tablename__ = "feature_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flag_key = Column(String(100), unique=True, nullable=False, index=True)
    flag_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Flag details
    flag_type = Column(String(50), default='BOOLEAN')
    flag_value = Column(Text, nullable=False)
    default_value = Column(Text)
    
    # Status
    is_enabled = Column(Boolean, default=False)
    status = Column(String(20), default='DRAFT')
    
    # Targeting
    targeting_rules = Column(JSONB, default=[])
    rollout_percentage = Column(Integer, default=0)
    
    # Scope
    scope = Column(String(50), default='GLOBAL')
    scope_values = Column(JSONB, default=[])
    
    # Environment
    environment = Column(String(50), default='PRODUCTION')
    
    # Lifecycle
    start_date = Column(TIMESTAMP(timezone=True))
    end_date = Column(TIMESTAMP(timezone=True))
    
    # Tracking
    usage_count = Column(Integer, default=0)
    last_accessed_at = Column(TIMESTAMP(timezone=True))
    
    # Dependencies
    depends_on_flags = Column(JSONB, default=[])
    
    # Metadata
    metadata = Column(JSONB, default={})
    tags = Column(JSONB, default=[])
    
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))


class APIKeyAdmin(BaseModel):
    """API key management model"""
    __tablename__ = "api_keys_admin"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_name = Column(String(200), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    key_prefix = Column(String(20), nullable=False)
    
    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    application_name = Column(String(200))
    
    # Permissions
    allowed_permissions = Column(JSONB, default=[])
    allowed_resources = Column(JSONB, default=[])
    scope = Column(String(50), default='FULL')
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=1000)
    rate_limit_per_hour = Column(Integer, default=10000)
    rate_limit_per_day = Column(Integer, default=100000)
    
    # IP restrictions
    allowed_ip_addresses = Column(JSONB, default=[])
    ip_whitelist_enabled = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default='ACTIVE')
    
    # Expiry
    expires_at = Column(TIMESTAMP(timezone=True))
    
    # Usage tracking
    last_used_at = Column(TIMESTAMP(timezone=True))
    usage_count = Column(Integer, default=0)
    
    # Rotation
    rotation_policy = Column(JSONB)
    last_rotated_at = Column(TIMESTAMP(timezone=True))
    next_rotation_at = Column(TIMESTAMP(timezone=True))
    
    # Security
    requires_mfa = Column(Boolean, default=False)
    allowed_endpoints = Column(JSONB, default=[])
    
    # Metadata
    description = Column(Text)
    metadata = Column(JSONB, default={})
    
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    revoked_at = Column(TIMESTAMP(timezone=True))
    revoked_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    revoked_reason = Column(Text)


class LoginHistory(BaseModel):
    """Login history model"""
    __tablename__ = "login_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User details
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    username = Column(String(100))
    
    # Login details
    login_type = Column(String(50), nullable=False)
    login_status = Column(String(20), nullable=False)
    
    # Session
    session_id = Column(String(100))
    session_duration_minutes = Column(Integer)
    
    # Location
    ip_address = Column(String(50))
    user_agent = Column(Text)
    device_type = Column(String(50))
    device_name = Column(String(100))
    browser = Column(String(100))
    os = Column(String(100))
    
    # Geolocation
    country = Column(String(100))
    city = Column(String(100))
    latitude = Column(Numeric(10, 6))
    longitude = Column(Numeric(10, 6))
    
    # Security
    is_suspicious = Column(Boolean, default=False)
    risk_score = Column(Integer)
    risk_factors = Column(JSONB)
    
    # MFA
    mfa_used = Column(Boolean, default=False)
    mfa_method = Column(String(50))
    
    # Failure details
    failure_reason = Column(Text)
    failure_count = Column(Integer, default=0)
    
    # Logout
    logout_at = Column(TIMESTAMP(timezone=True))
    logout_reason = Column(String(50))
    
    # Metadata
    metadata = Column(JSONB, default={})
    
    login_at = Column(TIMESTAMP(timezone=True))
