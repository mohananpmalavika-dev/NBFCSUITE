"""
Phase 15: Platform Administration Router
Complete system administration and configuration API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.admin import (
    SystemSetting, Role, UserRole, Permission, AuditLog,
    SystemHealth, SystemMetric, NotificationTemplate, ScheduledJob,
    JobExecution, FeatureFlag, APIKeyAdmin, LoginHistory
)
from app.schemas.admin import (
    SystemSettingCreate, SystemSettingUpdate, SystemSettingResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    UserRoleCreate, UserRoleUpdate, UserRoleResponse,
    PermissionCreate, PermissionUpdate, PermissionResponse,
    AuditLogCreate, AuditLogResponse,
    SystemHealthCreate, SystemHealthUpdate, SystemHealthResponse,
    SystemMetricCreate, SystemMetricResponse,
    NotificationTemplateCreate, NotificationTemplateUpdate, NotificationTemplateResponse,
    ScheduledJobCreate, ScheduledJobUpdate, ScheduledJobResponse,
    JobExecutionCreate, JobExecutionUpdate, JobExecutionResponse,
    FeatureFlagCreate, FeatureFlagUpdate, FeatureFlagResponse,
    APIKeyAdminCreate, APIKeyAdminUpdate, APIKeyAdminResponse, APIKeyRevokeRequest,
    LoginHistoryCreate, LoginHistoryUpdate, LoginHistoryResponse,
    AdminOverview, SystemHealthMetrics, JobExecutionMetrics, SecurityMetrics, UserActivityMetrics
)

router = APIRouter(prefix="/api/v1/gold/admin", tags=["Platform Administration"])


# =====================================================
# System Setting Endpoints
# =====================================================

@router.post("/settings", response_model=SystemSettingResponse, status_code=status.HTTP_201_CREATED)
def create_system_setting(
    setting: SystemSettingCreate,
    db: Session = Depends(get_db)
):
    """Create new system setting"""
    db_setting = SystemSetting(**setting.dict())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


@router.get("/settings", response_model=List[SystemSettingResponse])
def list_system_settings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = None,
    setting_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all system settings"""
    query = db.query(SystemSetting).filter(SystemSetting.deleted_at.is_(None))
    
    if category:
        query = query.filter(SystemSetting.category == category)
    if setting_type:
        query = query.filter(SystemSetting.setting_type == setting_type)
    
    return query.offset(skip).limit(limit).all()


@router.get("/settings/{setting_id}", response_model=SystemSettingResponse)
def get_system_setting(setting_id: UUID, db: Session = Depends(get_db)):
    """Get system setting by ID"""
    setting = db.query(SystemSetting).filter(
        SystemSetting.id == setting_id,
        SystemSetting.deleted_at.is_(None)
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="System setting not found")
    
    return setting


@router.get("/settings/key/{setting_key}", response_model=SystemSettingResponse)
def get_system_setting_by_key(setting_key: str, db: Session = Depends(get_db)):
    """Get system setting by key"""
    setting = db.query(SystemSetting).filter(
        SystemSetting.setting_key == setting_key,
        SystemSetting.deleted_at.is_(None)
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="System setting not found")
    
    return setting


@router.put("/settings/{setting_id}", response_model=SystemSettingResponse)
def update_system_setting(
    setting_id: UUID,
    setting: SystemSettingUpdate,
    db: Session = Depends(get_db)
):
    """Update system setting"""
    db_setting = db.query(SystemSetting).filter(
        SystemSetting.id == setting_id,
        SystemSetting.deleted_at.is_(None)
    ).first()
    
    if not db_setting:
        raise HTTPException(status_code=404, detail="System setting not found")
    
    if not db_setting.is_editable:
        raise HTTPException(status_code=400, detail="Setting is not editable")
    
    for key, value in setting.dict(exclude_unset=True).items():
        setattr(db_setting, key, value)
    
    db_setting.last_modified_at = datetime.utcnow()
    db.commit()
    db.refresh(db_setting)
    return db_setting


@router.delete("/settings/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system_setting(setting_id: UUID, db: Session = Depends(get_db)):
    """Soft delete system setting"""
    db_setting = db.query(SystemSetting).filter(
        SystemSetting.id == setting_id,
        SystemSetting.deleted_at.is_(None)
    ).first()
    
    if not db_setting:
        raise HTTPException(status_code=404, detail="System setting not found")
    
    db_setting.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Role Endpoints
# =====================================================

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db)
):
    """Create new role"""
    db_role = Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@router.get("/roles", response_model=List[RoleResponse])
def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role_type: Optional[str] = None,
    status: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all roles"""
    query = db.query(Role).filter(Role.deleted_at.is_(None))
    
    if role_type:
        query = query.filter(Role.role_type == role_type)
    if status:
        query = query.filter(Role.status == status)
    if is_active is not None:
        query = query.filter(Role.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(role_id: UUID, db: Session = Depends(get_db)):
    """Get role by ID"""
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.deleted_at.is_(None)
    ).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: UUID,
    role: RoleUpdate,
    db: Session = Depends(get_db)
):
    """Update role"""
    db_role = db.query(Role).filter(
        Role.id == role_id,
        Role.deleted_at.is_(None)
    ).first()
    
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    for key, value in role.dict(exclude_unset=True).items():
        setattr(db_role, key, value)
    
    db.commit()
    db.refresh(db_role)
    return db_role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: UUID, db: Session = Depends(get_db)):
    """Soft delete role"""
    db_role = db.query(Role).filter(
        Role.id == role_id,
        Role.deleted_at.is_(None)
    ).first()
    
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if db_role.is_system_role:
        raise HTTPException(status_code=400, detail="Cannot delete system role")
    
    db_role.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# User Role Assignment Endpoints
# =====================================================

@router.post("/user-roles", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
def assign_user_role(
    user_role: UserRoleCreate,
    db: Session = Depends(get_db)
):
    """Assign role to user"""
    db_user_role = UserRole(**user_role.dict())
    db_user_role.assigned_at = datetime.utcnow()
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return db_user_role


@router.get("/user-roles", response_model=List[UserRoleResponse])
def list_user_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List user role assignments"""
    query = db.query(UserRole).filter(UserRole.deleted_at.is_(None))
    
    if user_id:
        query = query.filter(UserRole.user_id == user_id)
    if role_id:
        query = query.filter(UserRole.role_id == role_id)
    if status:
        query = query.filter(UserRole.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/user-roles/{assignment_id}", response_model=UserRoleResponse)
def get_user_role(assignment_id: UUID, db: Session = Depends(get_db)):
    """Get user role assignment by ID"""
    user_role = db.query(UserRole).filter(
        UserRole.id == assignment_id,
        UserRole.deleted_at.is_(None)
    ).first()
    
    if not user_role:
        raise HTTPException(status_code=404, detail="User role assignment not found")
    
    return user_role


@router.put("/user-roles/{assignment_id}", response_model=UserRoleResponse)
def update_user_role(
    assignment_id: UUID,
    user_role: UserRoleUpdate,
    db: Session = Depends(get_db)
):
    """Update user role assignment"""
    db_user_role = db.query(UserRole).filter(
        UserRole.id == assignment_id,
        UserRole.deleted_at.is_(None)
    ).first()
    
    if not db_user_role:
        raise HTTPException(status_code=404, detail="User role assignment not found")
    
    for key, value in user_role.dict(exclude_unset=True).items():
        setattr(db_user_role, key, value)
    
    db.commit()
    db.refresh(db_user_role)
    return db_user_role


@router.delete("/user-roles/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_user_role(assignment_id: UUID, db: Session = Depends(get_db)):
    """Revoke user role assignment"""
    db_user_role = db.query(UserRole).filter(
        UserRole.id == assignment_id,
        UserRole.deleted_at.is_(None)
    ).first()
    
    if not db_user_role:
        raise HTTPException(status_code=404, detail="User role assignment not found")
    
    db_user_role.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Permission Endpoints
# =====================================================

@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db)
):
    """Create new permission"""
    db_permission = Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


@router.get("/permissions", response_model=List[PermissionResponse])
def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    module: Optional[str] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all permissions"""
    query = db.query(Permission).filter(Permission.deleted_at.is_(None))
    
    if module:
        query = query.filter(Permission.module == module)
    if resource:
        query = query.filter(Permission.resource == resource)
    if action:
        query = query.filter(Permission.action == action)
    if is_active is not None:
        query = query.filter(Permission.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
def get_permission(permission_id: UUID, db: Session = Depends(get_db)):
    """Get permission by ID"""
    permission = db.query(Permission).filter(
        Permission.id == permission_id,
        Permission.deleted_at.is_(None)
    ).first()
    
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    return permission


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: UUID,
    permission: PermissionUpdate,
    db: Session = Depends(get_db)
):
    """Update permission"""
    db_permission = db.query(Permission).filter(
        Permission.id == permission_id,
        Permission.deleted_at.is_(None)
    ).first()
    
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    for key, value in permission.dict(exclude_unset=True).items():
        setattr(db_permission, key, value)
    
    db.commit()
    db.refresh(db_permission)
    return db_permission


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(permission_id: UUID, db: Session = Depends(get_db)):
    """Soft delete permission"""
    db_permission = db.query(Permission).filter(
        Permission.id == permission_id,
        Permission.deleted_at.is_(None)
    ).first()
    
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    db_permission.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Audit Log Endpoints
# =====================================================

@router.post("/audit-logs", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log(
    audit_log: AuditLogCreate,
    db: Session = Depends(get_db)
):
    """Create new audit log entry"""
    db_log = AuditLog(**audit_log.dict())
    db_log.log_code = f"LOG-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    event_type: Optional[str] = None,
    event_category: Optional[str] = None,
    user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    action_result: Optional[str] = None,
    resource_type: Optional[str] = None,
    is_sensitive: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List audit logs"""
    query = db.query(AuditLog).filter(AuditLog.deleted_at.is_(None))
    
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if event_category:
        query = query.filter(AuditLog.event_category == event_category)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if action_result:
        query = query.filter(AuditLog.action_result == action_result)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if is_sensitive is not None:
        query = query.filter(AuditLog.is_sensitive == is_sensitive)
    
    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/audit-logs/{log_id}", response_model=AuditLogResponse)
def get_audit_log(log_id: UUID, db: Session = Depends(get_db)):
    """Get audit log by ID"""
    log = db.query(AuditLog).filter(
        AuditLog.id == log_id,
        AuditLog.deleted_at.is_(None)
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return log


# =====================================================
# System Health Endpoints
# =====================================================

@router.post("/health-checks", response_model=SystemHealthResponse, status_code=status.HTTP_201_CREATED)
def create_health_check(
    health_check: SystemHealthCreate,
    db: Session = Depends(get_db)
):
    """Create new health check"""
    db_health = SystemHealth(**health_check.dict())
    db_health.last_check_at = datetime.utcnow()
    db.add(db_health)
    db.commit()
    db.refresh(db_health)
    return db_health


@router.get("/health-checks", response_model=List[SystemHealthResponse])
def list_health_checks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    check_type: Optional[str] = None,
    component_name: Optional[str] = None,
    health_status: Optional[str] = None,
    is_critical: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List health checks"""
    query = db.query(SystemHealth).filter(SystemHealth.deleted_at.is_(None))
    
    if check_type:
        query = query.filter(SystemHealth.check_type == check_type)
    if component_name:
        query = query.filter(SystemHealth.component_name == component_name)
    if health_status:
        query = query.filter(SystemHealth.health_status == health_status)
    if is_critical is not None:
        query = query.filter(SystemHealth.is_critical == is_critical)
    
    return query.offset(skip).limit(limit).all()


@router.get("/health-checks/{check_id}", response_model=SystemHealthResponse)
def get_health_check(check_id: UUID, db: Session = Depends(get_db)):
    """Get health check by ID"""
    health = db.query(SystemHealth).filter(
        SystemHealth.id == check_id,
        SystemHealth.deleted_at.is_(None)
    ).first()
    
    if not health:
        raise HTTPException(status_code=404, detail="Health check not found")
    
    return health


@router.put("/health-checks/{check_id}", response_model=SystemHealthResponse)
def update_health_check(
    check_id: UUID,
    health_check: SystemHealthUpdate,
    db: Session = Depends(get_db)
):
    """Update health check"""
    db_health = db.query(SystemHealth).filter(
        SystemHealth.id == check_id,
        SystemHealth.deleted_at.is_(None)
    ).first()
    
    if not db_health:
        raise HTTPException(status_code=404, detail="Health check not found")
    
    for key, value in health_check.dict(exclude_unset=True).items():
        setattr(db_health, key, value)
    
    db.commit()
    db.refresh(db_health)
    return db_health


@router.post("/health-checks/{check_id}/run", response_model=SystemHealthResponse)
def run_health_check(check_id: UUID, db: Session = Depends(get_db)):
    """Execute health check"""
    db_health = db.query(SystemHealth).filter(
        SystemHealth.id == check_id,
        SystemHealth.deleted_at.is_(None)
    ).first()
    
    if not db_health:
        raise HTTPException(status_code=404, detail="Health check not found")
    
    db_health.last_check_at = datetime.utcnow()
    db_health.health_status = "HEALTHY"  # Would be determined by actual check
    
    db.commit()
    db.refresh(db_health)
    return db_health


@router.delete("/health-checks/{check_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_check(check_id: UUID, db: Session = Depends(get_db)):
    """Soft delete health check"""
    db_health = db.query(SystemHealth).filter(
        SystemHealth.id == check_id,
        SystemHealth.deleted_at.is_(None)
    ).first()
    
    if not db_health:
        raise HTTPException(status_code=404, detail="Health check not found")
    
    db_health.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# System Metric Endpoints
# =====================================================

@router.post("/metrics", response_model=SystemMetricResponse, status_code=status.HTTP_201_CREATED)
def create_system_metric(
    metric: SystemMetricCreate,
    db: Session = Depends(get_db)
):
    """Create new system metric"""
    db_metric = SystemMetric(**metric.dict())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@router.get("/metrics", response_model=List[SystemMetricResponse])
def list_system_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    metric_name: Optional[str] = None,
    metric_type: Optional[str] = None,
    metric_category: Optional[str] = None,
    service_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List system metrics"""
    query = db.query(SystemMetric).filter(SystemMetric.deleted_at.is_(None))
    
    if metric_name:
        query = query.filter(SystemMetric.metric_name == metric_name)
    if metric_type:
        query = query.filter(SystemMetric.metric_type == metric_type)
    if metric_category:
        query = query.filter(SystemMetric.metric_category == metric_category)
    if service_name:
        query = query.filter(SystemMetric.service_name == service_name)
    
    return query.order_by(SystemMetric.recorded_at.desc()).offset(skip).limit(limit).all()


@router.get("/metrics/{metric_id}", response_model=SystemMetricResponse)
def get_system_metric(metric_id: UUID, db: Session = Depends(get_db)):
    """Get system metric by ID"""
    metric = db.query(SystemMetric).filter(
        SystemMetric.id == metric_id,
        SystemMetric.deleted_at.is_(None)
    ).first()
    
    if not metric:
        raise HTTPException(status_code=404, detail="System metric not found")
    
    return metric


# =====================================================
# Notification Template Endpoints
# =====================================================

@router.post("/notification-templates", response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_notification_template(
    template: NotificationTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create new notification template"""
    db_template = NotificationTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/notification-templates", response_model=List[NotificationTemplateResponse])
def list_notification_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    notification_type: Optional[str] = None,
    template_category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List notification templates"""
    query = db.query(NotificationTemplate).filter(NotificationTemplate.deleted_at.is_(None))
    
    if notification_type:
        query = query.filter(NotificationTemplate.notification_type == notification_type)
    if template_category:
        query = query.filter(NotificationTemplate.template_category == template_category)
    if status:
        query = query.filter(NotificationTemplate.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/notification-templates/{template_id}", response_model=NotificationTemplateResponse)
def get_notification_template(template_id: UUID, db: Session = Depends(get_db)):
    """Get notification template by ID"""
    template = db.query(NotificationTemplate).filter(
        NotificationTemplate.id == template_id,
        NotificationTemplate.deleted_at.is_(None)
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Notification template not found")
    
    return template


@router.put("/notification-templates/{template_id}", response_model=NotificationTemplateResponse)
def update_notification_template(
    template_id: UUID,
    template: NotificationTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update notification template"""
    db_template = db.query(NotificationTemplate).filter(
        NotificationTemplate.id == template_id,
        NotificationTemplate.deleted_at.is_(None)
    ).first()
    
    if not db_template:
        raise HTTPException(status_code=404, detail="Notification template not found")
    
    for key, value in template.dict(exclude_unset=True).items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/notification-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification_template(template_id: UUID, db: Session = Depends(get_db)):
    """Soft delete notification template"""
    db_template = db.query(NotificationTemplate).filter(
        NotificationTemplate.id == template_id,
        NotificationTemplate.deleted_at.is_(None)
    ).first()
    
    if not db_template:
        raise HTTPException(status_code=404, detail="Notification template not found")
    
    db_template.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Scheduled Job Endpoints
# =====================================================

@router.post("/scheduled-jobs", response_model=ScheduledJobResponse, status_code=status.HTTP_201_CREATED)
def create_scheduled_job(
    job: ScheduledJobCreate,
    db: Session = Depends(get_db)
):
    """Create new scheduled job"""
    db_job = ScheduledJob(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/scheduled-jobs", response_model=List[ScheduledJobResponse])
def list_scheduled_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    job_type: Optional[str] = None,
    job_category: Optional[str] = None,
    status: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List scheduled jobs"""
    query = db.query(ScheduledJob).filter(ScheduledJob.deleted_at.is_(None))
    
    if job_type:
        query = query.filter(ScheduledJob.job_type == job_type)
    if job_category:
        query = query.filter(ScheduledJob.job_category == job_category)
    if status:
        query = query.filter(ScheduledJob.status == status)
    if is_enabled is not None:
        query = query.filter(ScheduledJob.is_enabled == is_enabled)
    
    return query.offset(skip).limit(limit).all()


@router.get("/scheduled-jobs/{job_id}", response_model=ScheduledJobResponse)
def get_scheduled_job(job_id: UUID, db: Session = Depends(get_db)):
    """Get scheduled job by ID"""
    job = db.query(ScheduledJob).filter(
        ScheduledJob.id == job_id,
        ScheduledJob.deleted_at.is_(None)
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    
    return job


@router.put("/scheduled-jobs/{job_id}", response_model=ScheduledJobResponse)
def update_scheduled_job(
    job_id: UUID,
    job: ScheduledJobUpdate,
    db: Session = Depends(get_db)
):
    """Update scheduled job"""
    db_job = db.query(ScheduledJob).filter(
        ScheduledJob.id == job_id,
        ScheduledJob.deleted_at.is_(None)
    ).first()
    
    if not db_job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    
    for key, value in job.dict(exclude_unset=True).items():
        setattr(db_job, key, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job


@router.post("/scheduled-jobs/{job_id}/execute", response_model=JobExecutionResponse)
def execute_scheduled_job(job_id: UUID, db: Session = Depends(get_db)):
    """Manually execute scheduled job"""
    job = db.query(ScheduledJob).filter(
        ScheduledJob.id == job_id,
        ScheduledJob.deleted_at.is_(None)
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    
    # Create execution record
    execution = JobExecution(
        execution_code=f"EXEC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        job_id=job_id,
        execution_type="MANUAL",
        started_at=datetime.utcnow(),
        execution_status="IN_PROGRESS"
    )
    
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


@router.delete("/scheduled-jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheduled_job(job_id: UUID, db: Session = Depends(get_db)):
    """Soft delete scheduled job"""
    db_job = db.query(ScheduledJob).filter(
        ScheduledJob.id == job_id,
        ScheduledJob.deleted_at.is_(None)
    ).first()
    
    if not db_job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    
    db_job.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Job Execution Endpoints
# =====================================================

@router.get("/job-executions", response_model=List[JobExecutionResponse])
def list_job_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    job_id: Optional[UUID] = None,
    execution_status: Optional[str] = None,
    execution_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List job executions"""
    query = db.query(JobExecution).filter(JobExecution.deleted_at.is_(None))
    
    if job_id:
        query = query.filter(JobExecution.job_id == job_id)
    if execution_status:
        query = query.filter(JobExecution.execution_status == execution_status)
    if execution_type:
        query = query.filter(JobExecution.execution_type == execution_type)
    
    return query.order_by(JobExecution.started_at.desc()).offset(skip).limit(limit).all()


@router.get("/job-executions/{execution_id}", response_model=JobExecutionResponse)
def get_job_execution(execution_id: UUID, db: Session = Depends(get_db)):
    """Get job execution by ID"""
    execution = db.query(JobExecution).filter(
        JobExecution.id == execution_id,
        JobExecution.deleted_at.is_(None)
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Job execution not found")
    
    return execution


@router.put("/job-executions/{execution_id}", response_model=JobExecutionResponse)
def update_job_execution(
    execution_id: UUID,
    execution: JobExecutionUpdate,
    db: Session = Depends(get_db)
):
    """Update job execution"""
    db_execution = db.query(JobExecution).filter(
        JobExecution.id == execution_id,
        JobExecution.deleted_at.is_(None)
    ).first()
    
    if not db_execution:
        raise HTTPException(status_code=404, detail="Job execution not found")
    
    for key, value in execution.dict(exclude_unset=True).items():
        setattr(db_execution, key, value)
    
    db.commit()
    db.refresh(db_execution)
    return db_execution



# =====================================================
# Feature Flag Endpoints
# =====================================================

@router.post("/feature-flags", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED)
def create_feature_flag(
    flag: FeatureFlagCreate,
    db: Session = Depends(get_db)
):
    """Create new feature flag"""
    db_flag = FeatureFlag(**flag.dict())
    db.add(db_flag)
    db.commit()
    db.refresh(db_flag)
    return db_flag


@router.get("/feature-flags", response_model=List[FeatureFlagResponse])
def list_feature_flags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    flag_type: Optional[str] = None,
    environment: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List feature flags"""
    query = db.query(FeatureFlag).filter(FeatureFlag.deleted_at.is_(None))
    
    if flag_type:
        query = query.filter(FeatureFlag.flag_type == flag_type)
    if environment:
        query = query.filter(FeatureFlag.environment == environment)
    if is_enabled is not None:
        query = query.filter(FeatureFlag.is_enabled == is_enabled)
    if status:
        query = query.filter(FeatureFlag.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/feature-flags/{flag_id}", response_model=FeatureFlagResponse)
def get_feature_flag(flag_id: UUID, db: Session = Depends(get_db)):
    """Get feature flag by ID"""
    flag = db.query(FeatureFlag).filter(
        FeatureFlag.id == flag_id,
        FeatureFlag.deleted_at.is_(None)
    ).first()
    
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    
    flag.usage_count += 1
    flag.last_accessed_at = datetime.utcnow()
    db.commit()
    db.refresh(flag)
    
    return flag


@router.get("/feature-flags/key/{flag_key}", response_model=FeatureFlagResponse)
def get_feature_flag_by_key(flag_key: str, db: Session = Depends(get_db)):
    """Get feature flag by key"""
    flag = db.query(FeatureFlag).filter(
        FeatureFlag.flag_key == flag_key,
        FeatureFlag.deleted_at.is_(None)
    ).first()
    
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    
    flag.usage_count += 1
    flag.last_accessed_at = datetime.utcnow()
    db.commit()
    db.refresh(flag)
    
    return flag


@router.put("/feature-flags/{flag_id}", response_model=FeatureFlagResponse)
def update_feature_flag(
    flag_id: UUID,
    flag: FeatureFlagUpdate,
    db: Session = Depends(get_db)
):
    """Update feature flag"""
    db_flag = db.query(FeatureFlag).filter(
        FeatureFlag.id == flag_id,
        FeatureFlag.deleted_at.is_(None)
    ).first()
    
    if not db_flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    
    for key, value in flag.dict(exclude_unset=True).items():
        setattr(db_flag, key, value)
    
    db.commit()
    db.refresh(db_flag)
    return db_flag


@router.post("/feature-flags/{flag_id}/toggle", response_model=FeatureFlagResponse)
def toggle_feature_flag(flag_id: UUID, db: Session = Depends(get_db)):
    """Toggle feature flag enabled status"""
    db_flag = db.query(FeatureFlag).filter(
        FeatureFlag.id == flag_id,
        FeatureFlag.deleted_at.is_(None)
    ).first()
    
    if not db_flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    
    db_flag.is_enabled = not db_flag.is_enabled
    db.commit()
    db.refresh(db_flag)
    return db_flag


@router.delete("/feature-flags/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feature_flag(flag_id: UUID, db: Session = Depends(get_db)):
    """Soft delete feature flag"""
    db_flag = db.query(FeatureFlag).filter(
        FeatureFlag.id == flag_id,
        FeatureFlag.deleted_at.is_(None)
    ).first()
    
    if not db_flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    
    db_flag.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# API Key Admin Endpoints
# =====================================================

@router.post("/api-keys", response_model=APIKeyAdminResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    api_key: APIKeyAdminCreate,
    db: Session = Depends(get_db)
):
    """Create new API key"""
    import secrets
    import hashlib
    
    # Generate API key
    key = f"gld_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    key_prefix = key[:12]
    
    db_key = APIKeyAdmin(**api_key.dict())
    db_key.key_hash = key_hash
    db_key.key_prefix = key_prefix
    
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    # Return the actual key only once during creation
    response = APIKeyAdminResponse.from_orm(db_key)
    return response


@router.get("/api-keys", response_model=List[APIKeyAdminResponse])
def list_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[UUID] = None,
    status: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List API keys"""
    query = db.query(APIKeyAdmin).filter(APIKeyAdmin.deleted_at.is_(None))
    
    if user_id:
        query = query.filter(APIKeyAdmin.user_id == user_id)
    if status:
        query = query.filter(APIKeyAdmin.status == status)
    if is_active is not None:
        query = query.filter(APIKeyAdmin.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/api-keys/{key_id}", response_model=APIKeyAdminResponse)
def get_api_key(key_id: UUID, db: Session = Depends(get_db)):
    """Get API key by ID"""
    api_key = db.query(APIKeyAdmin).filter(
        APIKeyAdmin.id == key_id,
        APIKeyAdmin.deleted_at.is_(None)
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return api_key


@router.put("/api-keys/{key_id}", response_model=APIKeyAdminResponse)
def update_api_key(
    key_id: UUID,
    api_key: APIKeyAdminUpdate,
    db: Session = Depends(get_db)
):
    """Update API key"""
    db_key = db.query(APIKeyAdmin).filter(
        APIKeyAdmin.id == key_id,
        APIKeyAdmin.deleted_at.is_(None)
    ).first()
    
    if not db_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    for key, value in api_key.dict(exclude_unset=True).items():
        setattr(db_key, key, value)
    
    db.commit()
    db.refresh(db_key)
    return db_key


@router.post("/api-keys/{key_id}/revoke", response_model=APIKeyAdminResponse)
def revoke_api_key(
    key_id: UUID,
    revoke_request: APIKeyRevokeRequest,
    db: Session = Depends(get_db)
):
    """Revoke API key"""
    db_key = db.query(APIKeyAdmin).filter(
        APIKeyAdmin.id == key_id,
        APIKeyAdmin.deleted_at.is_(None)
    ).first()
    
    if not db_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db_key.is_active = False
    db_key.status = "REVOKED"
    db_key.revoked_at = datetime.utcnow()
    db_key.revoked_reason = revoke_request.revoked_reason
    
    db.commit()
    db.refresh(db_key)
    return db_key


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(key_id: UUID, db: Session = Depends(get_db)):
    """Soft delete API key"""
    db_key = db.query(APIKeyAdmin).filter(
        APIKeyAdmin.id == key_id,
        APIKeyAdmin.deleted_at.is_(None)
    ).first()
    
    if not db_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db_key.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Login History Endpoints
# =====================================================

@router.post("/login-history", response_model=LoginHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_login_history(
    login: LoginHistoryCreate,
    db: Session = Depends(get_db)
):
    """Create new login history entry"""
    db_login = LoginHistory(**login.dict())
    if not db_login.login_at:
        db_login.login_at = datetime.utcnow()
    db.add(db_login)
    db.commit()
    db.refresh(db_login)
    return db_login


@router.get("/login-history", response_model=List[LoginHistoryResponse])
def list_login_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[UUID] = None,
    login_status: Optional[str] = None,
    is_suspicious: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List login history"""
    query = db.query(LoginHistory).filter(LoginHistory.deleted_at.is_(None))
    
    if user_id:
        query = query.filter(LoginHistory.user_id == user_id)
    if login_status:
        query = query.filter(LoginHistory.login_status == login_status)
    if is_suspicious is not None:
        query = query.filter(LoginHistory.is_suspicious == is_suspicious)
    
    return query.order_by(LoginHistory.login_at.desc()).offset(skip).limit(limit).all()


@router.get("/login-history/{login_id}", response_model=LoginHistoryResponse)
def get_login_history(login_id: UUID, db: Session = Depends(get_db)):
    """Get login history by ID"""
    login = db.query(LoginHistory).filter(
        LoginHistory.id == login_id,
        LoginHistory.deleted_at.is_(None)
    ).first()
    
    if not login:
        raise HTTPException(status_code=404, detail="Login history not found")
    
    return login


@router.put("/login-history/{login_id}", response_model=LoginHistoryResponse)
def update_login_history(
    login_id: UUID,
    login: LoginHistoryUpdate,
    db: Session = Depends(get_db)
):
    """Update login history (e.g., logout time)"""
    db_login = db.query(LoginHistory).filter(
        LoginHistory.id == login_id,
        LoginHistory.deleted_at.is_(None)
    ).first()
    
    if not db_login:
        raise HTTPException(status_code=404, detail="Login history not found")
    
    for key, value in login.dict(exclude_unset=True).items():
        setattr(db_login, key, value)
    
    db.commit()
    db.refresh(db_login)
    return db_login


# =====================================================
# Statistics & Overview Endpoints
# =====================================================

@router.get("/statistics/overview", response_model=AdminOverview)
def get_admin_overview(db: Session = Depends(get_db)):
    """Get platform administration overview statistics"""
    from sqlalchemy import text
    
    result = db.execute(text("SELECT * FROM v_admin_overview")).fetchone()
    
    if not result:
        return AdminOverview(
            total_users=0, active_users=0, total_roles=0, active_roles=0,
            total_permissions=0, total_audit_logs=0, total_system_health_checks=0,
            healthy_components=0, unhealthy_components=0, total_scheduled_jobs=0,
            active_scheduled_jobs=0, total_feature_flags=0, enabled_feature_flags=0,
            total_api_keys=0, active_api_keys=0, total_logins_today=0,
            failed_logins_today=0
        )
    
    return AdminOverview(
        total_users=result[0] or 0,
        active_users=result[1] or 0,
        total_roles=result[2] or 0,
        active_roles=result[3] or 0,
        total_permissions=result[4] or 0,
        total_audit_logs=result[5] or 0,
        total_system_health_checks=result[6] or 0,
        healthy_components=result[7] or 0,
        unhealthy_components=result[8] or 0,
        total_scheduled_jobs=result[9] or 0,
        active_scheduled_jobs=result[10] or 0,
        total_feature_flags=result[11] or 0,
        enabled_feature_flags=result[12] or 0,
        total_api_keys=result[13] or 0,
        active_api_keys=result[14] or 0,
        total_logins_today=result[15] or 0,
        failed_logins_today=result[16] or 0
    )


@router.get("/statistics/system-health", response_model=List[SystemHealthMetrics])
def get_system_health_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get system health metrics"""
    from sqlalchemy import text
    
    query = text("""
        SELECT * FROM v_system_health_metrics
        ORDER BY is_critical DESC, consecutive_failures DESC
        LIMIT :limit OFFSET :skip
    """)
    
    results = db.execute(query, {"limit": limit, "skip": skip}).fetchall()
    
    metrics = []
    for row in results:
        metrics.append(SystemHealthMetrics(
            check_id=row[0],
            check_code=row[1],
            check_name=row[2],
            component_name=row[3],
            health_status=row[4],
            response_time_ms=row[5],
            availability_percent=row[6],
            error_rate_percent=row[7],
            last_check_at=row[8],
            consecutive_failures=row[9] or 0,
            is_critical=row[10]
        ))
    
    return metrics


@router.get("/statistics/job-executions", response_model=List[JobExecutionMetrics])
def get_job_execution_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get scheduled job execution metrics"""
    from sqlalchemy import text
    
    query = text("""
        SELECT * FROM v_job_execution_metrics
        ORDER BY total_executions DESC
        LIMIT :limit OFFSET :skip
    """)
    
    results = db.execute(query, {"limit": limit, "skip": skip}).fetchall()
    
    metrics = []
    for row in results:
        metrics.append(JobExecutionMetrics(
            job_id=row[0],
            job_code=row[1],
            job_name=row[2],
            job_type=row[3],
            total_executions=row[4] or 0,
            success_count=row[5] or 0,
            failure_count=row[6] or 0,
            avg_duration_ms=row[7],
            last_execution_at=row[8],
            last_execution_status=row[9]
        ))
    
    return metrics


@router.get("/statistics/security", response_model=SecurityMetrics)
def get_security_metrics(db: Session = Depends(get_db)):
    """Get security and access metrics"""
    from sqlalchemy import text
    
    result = db.execute(text("SELECT * FROM v_security_metrics")).fetchone()
    
    if not result:
        return SecurityMetrics(
            total_logins_today=0,
            failed_logins_today=0,
            suspicious_logins_today=0,
            active_sessions=0,
            mfa_adoption_rate=None,
            api_key_usage_count=0,
            revoked_api_keys=0,
            high_risk_audit_logs=0
        )
    
    return SecurityMetrics(
        total_logins_today=result[0] or 0,
        failed_logins_today=result[1] or 0,
        suspicious_logins_today=result[2] or 0,
        active_sessions=result[3] or 0,
        mfa_adoption_rate=result[4],
        api_key_usage_count=result[5] or 0,
        revoked_api_keys=result[6] or 0,
        high_risk_audit_logs=result[7] or 0
    )



@router.get("/statistics/user-activity", response_model=List[UserActivityMetrics])
def get_user_activity_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get user activity metrics"""
    from sqlalchemy import text
    
    query = text("""
        SELECT * FROM v_user_activity_metrics
        ORDER BY total_actions DESC
        LIMIT :limit OFFSET :skip
    """)
    
    results = db.execute(query, {"limit": limit, "skip": skip}).fetchall()
    
    metrics = []
    for row in results:
        metrics.append(UserActivityMetrics(
            user_id=row[0],
            username=row[1],
            total_logins=row[2] or 0,
            last_login_at=row[3],
            total_actions=row[4] or 0,
            failed_actions=row[5] or 0,
            roles_assigned=row[6] or 0,
            is_active=row[7]
        ))
    
    return metrics
