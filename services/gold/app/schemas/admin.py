"""
Phase 15: Platform Administration Schemas
Pydantic schemas for system administration and configuration
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, time
from decimal import Decimal
from uuid import UUID


# =====================================================
# System Setting Schemas
# =====================================================

class SystemSettingBase(BaseModel):
    setting_key: str = Field(..., max_length=100)
    setting_value: str
    setting_type: str = Field(..., max_length=50)
    category: str = Field(..., max_length=50)
    description: Optional[str] = None
    is_encrypted: Optional[bool] = False
    is_editable: Optional[bool] = True
    requires_restart: Optional[bool] = False
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class SystemSettingCreate(SystemSettingBase):
    pass


class SystemSettingUpdate(BaseModel):
    setting_value: Optional[str] = None
    description: Optional[str] = None
    is_editable: Optional[bool] = None
    requires_restart: Optional[bool] = None
    validation_rules: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class SystemSettingResponse(SystemSettingBase):
    id: UUID
    last_modified_by: Optional[UUID] = None
    last_modified_at: Optional[datetime] = None
    change_history: Optional[List[Dict[str, Any]]] = []
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Role Schemas
# =====================================================

class RoleBase(BaseModel):
    role_code: str = Field(..., max_length=50)
    role_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    role_type: str = Field(..., max_length=50)
    is_system_role: Optional[bool] = False
    permissions: Optional[List[str]] = []
    resource_access: Optional[Dict[str, Any]] = {}
    parent_role_id: Optional[UUID] = None
    hierarchy_level: Optional[int] = 0
    is_active: Optional[bool] = True
    status: Optional[str] = "ACTIVE"
    max_users: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = {}


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    resource_access: Optional[Dict[str, Any]] = None
    parent_role_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    max_users: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class RoleResponse(RoleBase):
    id: UUID
    current_user_count: int = 0
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# User Role Assignment Schemas
# =====================================================

class UserRoleBase(BaseModel):
    user_id: UUID
    role_id: UUID
    assigned_by: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    status: Optional[str] = "ACTIVE"
    scope_type: Optional[str] = Field(None, max_length=50)
    scope_value: Optional[str] = Field(None, max_length=100)
    assignment_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    scope_type: Optional[str] = None
    scope_value: Optional[str] = None
    assignment_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UserRoleResponse(UserRoleBase):
    id: UUID
    assigned_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Permission Schemas
# =====================================================

class PermissionBase(BaseModel):
    permission_code: str = Field(..., max_length=100)
    permission_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    module: str = Field(..., max_length=50)
    resource: str = Field(..., max_length=100)
    action: str = Field(..., max_length=50)
    permission_type: Optional[str] = "STANDARD"
    risk_level: Optional[str] = Field(None, max_length=20)
    requires_approval: Optional[bool] = False
    requires_mfa: Optional[bool] = False
    is_active: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = {}


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    permission_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    risk_level: Optional[str] = None
    requires_approval: Optional[bool] = None
    requires_mfa: Optional[bool] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class PermissionResponse(PermissionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Audit Log Schemas
# =====================================================

class AuditLogBase(BaseModel):
    event_type: str = Field(..., max_length=100)
    event_category: str = Field(..., max_length=50)
    event_name: str = Field(..., max_length=200)
    event_description: Optional[str] = None
    user_id: Optional[UUID] = None
    username: Optional[str] = Field(None, max_length=100)
    user_ip_address: Optional[str] = Field(None, max_length=50)
    user_agent: Optional[str] = None
    resource_type: Optional[str] = Field(None, max_length=100)
    resource_id: Optional[str] = Field(None, max_length=100)
    resource_name: Optional[str] = Field(None, max_length=200)
    action: str = Field(..., max_length=50)
    action_result: str = Field(..., max_length=20)
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = Field(None, max_length=100)
    session_id: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    application_name: Optional[str] = Field(None, max_length=100)
    module_name: Optional[str] = Field(None, max_length=100)
    service_name: Optional[str] = Field(None, max_length=100)
    branch_id: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    security_level: Optional[str] = Field(None, max_length=20)
    requires_review: Optional[bool] = False
    is_sensitive: Optional[bool] = False
    error_message: Optional[str] = None
    error_code: Optional[str] = Field(None, max_length=50)
    stack_trace: Optional[str] = None
    duration_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogResponse(AuditLogBase):
    id: UUID
    log_code: str
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# System Health Schemas
# =====================================================

class SystemHealthBase(BaseModel):
    check_code: str = Field(..., max_length=50)
    check_name: str = Field(..., max_length=200)
    check_type: str = Field(..., max_length=50)
    component_name: str = Field(..., max_length=100)
    health_status: str = Field(..., max_length=20)
    response_time_ms: Optional[int] = None
    availability_percent: Optional[Decimal] = None
    error_rate_percent: Optional[Decimal] = None
    success_rate_percent: Optional[Decimal] = None
    warning_threshold: Optional[Dict[str, Any]] = None
    critical_threshold: Optional[Dict[str, Any]] = None
    check_frequency_minutes: Optional[int] = 5
    check_result: Optional[Dict[str, Any]] = None
    check_message: Optional[str] = None
    check_details: Optional[Dict[str, Any]] = None
    alert_enabled: Optional[bool] = True
    alert_channels: Optional[List[str]] = []
    alert_recipients: Optional[List[str]] = []
    is_enabled: Optional[bool] = True
    is_critical: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = {}


class SystemHealthCreate(SystemHealthBase):
    pass


class SystemHealthUpdate(BaseModel):
    check_name: Optional[str] = Field(None, max_length=200)
    health_status: Optional[str] = None
    response_time_ms: Optional[int] = None
    availability_percent: Optional[Decimal] = None
    error_rate_percent: Optional[Decimal] = None
    success_rate_percent: Optional[Decimal] = None
    warning_threshold: Optional[Dict[str, Any]] = None
    critical_threshold: Optional[Dict[str, Any]] = None
    check_frequency_minutes: Optional[int] = None
    check_result: Optional[Dict[str, Any]] = None
    check_message: Optional[str] = None
    check_details: Optional[Dict[str, Any]] = None
    alert_enabled: Optional[bool] = None
    alert_channels: Optional[List[str]] = None
    alert_recipients: Optional[List[str]] = None
    is_enabled: Optional[bool] = None
    is_critical: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class SystemHealthResponse(SystemHealthBase):
    id: UUID
    previous_status: Optional[str] = None
    status_changed_at: Optional[datetime] = None
    last_check_at: datetime
    next_check_at: Optional[datetime] = None
    consecutive_failures: int = 0
    last_error: Optional[str] = None
    error_count: int = 0
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# System Metric Schemas
# =====================================================

class SystemMetricBase(BaseModel):
    metric_name: str = Field(..., max_length=100)
    metric_type: str = Field(..., max_length=50)
    metric_category: str = Field(..., max_length=50)
    metric_value: Decimal
    metric_unit: Optional[str] = Field(None, max_length=50)
    service_name: Optional[str] = Field(None, max_length=100)
    module_name: Optional[str] = Field(None, max_length=100)
    endpoint: Optional[str] = Field(None, max_length=200)
    labels: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    recorded_at: datetime
    time_bucket: Optional[str] = Field(None, max_length=20)
    is_aggregated: Optional[bool] = False
    sample_count: Optional[int] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    avg_value: Optional[Decimal] = None
    sum_value: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = {}


class SystemMetricCreate(SystemMetricBase):
    pass


class SystemMetricResponse(SystemMetricBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Notification Template Schemas
# =====================================================

class NotificationTemplateBase(BaseModel):
    template_code: str = Field(..., max_length=50)
    template_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    notification_type: str = Field(..., max_length=50)
    template_category: str = Field(..., max_length=50)
    subject_template: Optional[str] = None
    body_template: str
    html_template: Optional[str] = None
    template_engine: Optional[str] = "JINJA2"
    template_variables: Optional[List[str]] = []
    language: Optional[str] = "en"
    supports_localization: Optional[bool] = False
    priority: Optional[str] = "NORMAL"
    retry_policy: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = True
    is_default: Optional[bool] = False
    status: Optional[str] = "ACTIVE"
    version: Optional[str] = "1.0"
    parent_template_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = {}


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    subject_template: Optional[str] = None
    body_template: Optional[str] = None
    html_template: Optional[str] = None
    template_variables: Optional[List[str]] = None
    language: Optional[str] = None
    supports_localization: Optional[bool] = None
    priority: Optional[str] = None
    retry_policy: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    status: Optional[str] = None
    version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    id: UUID
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version_db: int = Field(..., alias='version')

    class Config:
        from_attributes = True
        populate_by_name = True


# =====================================================
# Scheduled Job Schemas
# =====================================================

class ScheduledJobBase(BaseModel):
    job_code: str = Field(..., max_length=50)
    job_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    job_type: str = Field(..., max_length=50)
    job_category: str = Field(..., max_length=50)
    handler_class: str = Field(..., max_length=200)
    handler_method: str = Field(..., max_length=100)
    parameters: Optional[Dict[str, Any]] = {}
    schedule_expression: Optional[str] = Field(None, max_length=100)
    interval_minutes: Optional[int] = None
    scheduled_time: Optional[time] = None
    execution_window_start: Optional[time] = None
    execution_window_end: Optional[time] = None
    is_enabled: Optional[bool] = True
    status: Optional[str] = "SCHEDULED"
    max_retries: Optional[int] = 3
    retry_delay_minutes: Optional[int] = 5
    timeout_minutes: Optional[int] = 60
    alert_on_failure: Optional[bool] = True
    alert_recipients: Optional[List[str]] = []
    priority: Optional[int] = 5
    depends_on_jobs: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}


class ScheduledJobCreate(ScheduledJobBase):
    pass


class ScheduledJobUpdate(BaseModel):
    job_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    schedule_expression: Optional[str] = None
    interval_minutes: Optional[int] = None
    scheduled_time: Optional[time] = None
    execution_window_start: Optional[time] = None
    execution_window_end: Optional[time] = None
    is_enabled: Optional[bool] = None
    status: Optional[str] = None
    max_retries: Optional[int] = None
    retry_delay_minutes: Optional[int] = None
    timeout_minutes: Optional[int] = None
    alert_on_failure: Optional[bool] = None
    alert_recipients: Optional[List[str]] = None
    priority: Optional[int] = None
    depends_on_jobs: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ScheduledJobResponse(ScheduledJobBase):
    id: UUID
    last_execution_at: Optional[datetime] = None
    last_execution_status: Optional[str] = None
    last_execution_duration_ms: Optional[int] = None
    last_execution_error: Optional[str] = None
    next_execution_at: Optional[datetime] = None
    total_executions: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_duration_ms: Optional[int] = None
    current_retry_count: int = 0
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Job Execution Schemas
# =====================================================

class JobExecutionBase(BaseModel):
    execution_code: str = Field(..., max_length=50)
    job_id: UUID
    execution_type: str = Field(..., max_length=50)
    started_at: datetime
    execution_status: str = Field(..., max_length=20)
    execution_result: Optional[Dict[str, Any]] = None
    rows_processed: Optional[int] = None
    records_created: Optional[int] = None
    records_updated: Optional[int] = None
    records_deleted: Optional[int] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    cpu_usage_percent: Optional[Decimal] = None
    memory_usage_mb: Optional[Decimal] = None
    execution_logs: Optional[str] = None
    log_file_path: Optional[str] = None
    triggered_by_user: Optional[UUID] = None
    trigger_context: Optional[Dict[str, Any]] = None
    is_retry: Optional[bool] = False
    retry_count: Optional[int] = 0
    parent_execution_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = {}


class JobExecutionCreate(JobExecutionBase):
    pass


class JobExecutionUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    execution_status: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    rows_processed: Optional[int] = None
    records_created: Optional[int] = None
    records_updated: Optional[int] = None
    records_deleted: Optional[int] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    cpu_usage_percent: Optional[Decimal] = None
    memory_usage_mb: Optional[Decimal] = None
    execution_logs: Optional[str] = None
    log_file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class JobExecutionResponse(JobExecutionBase):
    id: UUID
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Feature Flag Schemas
# =====================================================

class FeatureFlagBase(BaseModel):
    flag_key: str = Field(..., max_length=100)
    flag_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    flag_type: Optional[str] = "BOOLEAN"
    flag_value: str
    default_value: Optional[str] = None
    is_enabled: Optional[bool] = False
    status: Optional[str] = "DRAFT"
    targeting_rules: Optional[List[Dict[str, Any]]] = []
    rollout_percentage: Optional[int] = 0
    scope: Optional[str] = "GLOBAL"
    scope_values: Optional[List[str]] = []
    environment: Optional[str] = "PRODUCTION"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    depends_on_flags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []


class FeatureFlagCreate(FeatureFlagBase):
    pass


class FeatureFlagUpdate(BaseModel):
    flag_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    flag_value: Optional[str] = None
    default_value: Optional[str] = None
    is_enabled: Optional[bool] = None
    status: Optional[str] = None
    targeting_rules: Optional[List[Dict[str, Any]]] = None
    rollout_percentage: Optional[int] = None
    scope: Optional[str] = None
    scope_values: Optional[List[str]] = None
    environment: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    depends_on_flags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class FeatureFlagResponse(FeatureFlagBase):
    id: UUID
    usage_count: int = 0
    last_accessed_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# API Key Admin Schemas
# =====================================================

class APIKeyAdminBase(BaseModel):
    key_name: str = Field(..., max_length=200)
    user_id: Optional[UUID] = None
    application_name: Optional[str] = Field(None, max_length=200)
    allowed_permissions: Optional[List[str]] = []
    allowed_resources: Optional[List[str]] = []
    scope: Optional[str] = "FULL"
    rate_limit_per_minute: Optional[int] = 1000
    rate_limit_per_hour: Optional[int] = 10000
    rate_limit_per_day: Optional[int] = 100000
    allowed_ip_addresses: Optional[List[str]] = []
    ip_whitelist_enabled: Optional[bool] = False
    is_active: Optional[bool] = True
    status: Optional[str] = "ACTIVE"
    expires_at: Optional[datetime] = None
    requires_mfa: Optional[bool] = False
    allowed_endpoints: Optional[List[str]] = []
    rotation_policy: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class APIKeyAdminCreate(APIKeyAdminBase):
    pass


class APIKeyAdminUpdate(BaseModel):
    key_name: Optional[str] = Field(None, max_length=200)
    allowed_permissions: Optional[List[str]] = None
    allowed_resources: Optional[List[str]] = None
    scope: Optional[str] = None
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    allowed_ip_addresses: Optional[List[str]] = None
    ip_whitelist_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    expires_at: Optional[datetime] = None
    requires_mfa: Optional[bool] = None
    allowed_endpoints: Optional[List[str]] = None
    rotation_policy: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class APIKeyAdminResponse(APIKeyAdminBase):
    id: UUID
    key_hash: str
    key_prefix: str
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    last_rotated_at: Optional[datetime] = None
    next_rotation_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[UUID] = None
    revoked_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


class APIKeyRevokeRequest(BaseModel):
    revoked_reason: Optional[str] = None


# =====================================================
# Login History Schemas
# =====================================================

class LoginHistoryBase(BaseModel):
    user_id: Optional[UUID] = None
    username: Optional[str] = Field(None, max_length=100)
    login_type: str = Field(..., max_length=50)
    login_status: str = Field(..., max_length=20)
    session_id: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=50)
    user_agent: Optional[str] = None
    device_type: Optional[str] = Field(None, max_length=50)
    device_name: Optional[str] = Field(None, max_length=100)
    browser: Optional[str] = Field(None, max_length=100)
    os: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    is_suspicious: Optional[bool] = False
    risk_score: Optional[int] = None
    risk_factors: Optional[Dict[str, Any]] = None
    mfa_used: Optional[bool] = False
    mfa_method: Optional[str] = Field(None, max_length=50)
    failure_reason: Optional[str] = None
    failure_count: Optional[int] = 0
    metadata: Optional[Dict[str, Any]] = {}


class LoginHistoryCreate(LoginHistoryBase):
    login_at: Optional[datetime] = None


class LoginHistoryUpdate(BaseModel):
    session_duration_minutes: Optional[int] = None
    logout_at: Optional[datetime] = None
    logout_reason: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict[str, Any]] = None


class LoginHistoryResponse(LoginHistoryBase):
    id: UUID
    session_duration_minutes: Optional[int] = None
    logout_at: Optional[datetime] = None
    logout_reason: Optional[str] = None
    login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Admin Statistics Schemas
# =====================================================

class AdminOverview(BaseModel):
    total_users: int
    active_users: int
    total_roles: int
    active_roles: int
    total_permissions: int
    total_audit_logs: int
    total_system_health_checks: int
    healthy_components: int
    unhealthy_components: int
    total_scheduled_jobs: int
    active_scheduled_jobs: int
    total_feature_flags: int
    enabled_feature_flags: int
    total_api_keys: int
    active_api_keys: int
    total_logins_today: int
    failed_logins_today: int


class SystemHealthMetrics(BaseModel):
    check_id: UUID
    check_code: str
    check_name: str
    component_name: str
    health_status: str
    response_time_ms: Optional[int] = None
    availability_percent: Optional[Decimal] = None
    error_rate_percent: Optional[Decimal] = None
    last_check_at: datetime
    consecutive_failures: int
    is_critical: bool


class JobExecutionMetrics(BaseModel):
    job_id: UUID
    job_code: str
    job_name: str
    job_type: str
    total_executions: int
    success_count: int
    failure_count: int
    avg_duration_ms: Optional[int] = None
    last_execution_at: Optional[datetime] = None
    last_execution_status: Optional[str] = None


class SecurityMetrics(BaseModel):
    total_logins_today: int
    failed_logins_today: int
    suspicious_logins_today: int
    active_sessions: int
    mfa_adoption_rate: Optional[Decimal] = None
    api_key_usage_count: int
    revoked_api_keys: int
    high_risk_audit_logs: int


class UserActivityMetrics(BaseModel):
    user_id: UUID
    username: str
    total_logins: int
    last_login_at: Optional[datetime] = None
    total_actions: int
    failed_actions: int
    roles_assigned: int
    is_active: bool
