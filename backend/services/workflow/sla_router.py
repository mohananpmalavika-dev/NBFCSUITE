"""
SLA & Escalation Management API Router

Endpoints:
- SLA configuration CRUD
- Start/stop SLA tracking
- Pause/resume SLA
- Get SLA status and metrics
- Escalation history
- Holiday calendar management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, get_tenant_id
from backend.services.workflow.sla_models import (
    SLAConfiguration, EscalationRule, BusinessHoursConfig,
    HolidayCalendar, SLAInstance, SLAMetrics, SLAStatus,
    SLAEscalationConfig, SLATemplates, SLAType, TimeCalculationType, EscalationType
)
from backend.services.workflow.sla_engine import SLAEngine


router = APIRouter(prefix="/api/workflow/sla")


# ==================== REQUEST/RESPONSE MODELS ====================

class SLAConfigCreateRequest(BaseModel):
    """Request to create SLA configuration"""
    name: str
    description: Optional[str] = None
    entity_type: str
    workflow_step: Optional[str] = None
    sla_type: SLAType
    time_value: int
    time_unit: str = "hours"
    calculation_type: TimeCalculationType = TimeCalculationType.BUSINESS_HOURS
    business_hours_config: Optional[BusinessHoursConfig] = None
    holiday_calendar_id: Optional[str] = None
    allow_pause: bool = True
    pause_on_customer_action: bool = True
    warning_threshold: float = 70.0
    critical_threshold: float = 90.0


class EscalationRuleCreateRequest(BaseModel):
    """Request to create escalation rule"""
    name: str
    description: Optional[str] = None
    trigger_after_hours: Optional[float] = None
    trigger_after_percentage: Optional[float] = None
    escalation_type: EscalationType
    send_reminder_to_assignee: bool = True
    notify_supervisor: bool = False
    notify_users: Optional[List[int]] = None
    auto_transfer_to: Optional[int] = None
    escalate_to_next_level: bool = False
    repeat_escalation: bool = False
    repeat_interval_hours: Optional[float] = None


class SLAEscalationConfigCreateRequest(BaseModel):
    """Request to create complete SLA + escalation config"""
    name: str
    entity_type: str
    sla: SLAConfigCreateRequest
    escalation_rules: List[EscalationRuleCreateRequest] = []
    send_breach_notification: bool = True


class StartSLARequest(BaseModel):
    """Request to start SLA tracking"""
    sla_config_id: str
    entity_id: int
    workflow_instance_id: int
    workflow_step_id: Optional[int] = None


class PauseSLARequest(BaseModel):
    """Request to pause SLA"""
    reason: Optional[str] = None


class HolidayCalendarCreateRequest(BaseModel):
    """Request to create holiday calendar"""
    name: str
    holidays: List[str]  # YYYY-MM-DD format
    country: str = "IN"
    region: Optional[str] = None


# ==================== SLA CONFIGURATION ENDPOINTS ====================

@router.post("/configurations", tags=["SLA Configuration"])
def create_sla_configuration(
    request: SLAEscalationConfigCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create SLA and escalation configuration"""
    
    import uuid
    
    # Generate IDs
    config_id = f"sla_{uuid.uuid4().hex[:8]}"
    sla_id = f"sla_{uuid.uuid4().hex[:8]}"
    
    # Create SLA configuration
    sla_config = SLAConfiguration(
        sla_id=sla_id,
        name=request.sla.name,
        description=request.sla.description,
        entity_type=request.entity_type,
        workflow_step=request.sla.workflow_step,
        sla_type=request.sla.sla_type,
        time_value=request.sla.time_value,
        time_unit=request.sla.time_unit,
        calculation_type=request.sla.calculation_type,
        business_hours_config=request.sla.business_hours_config,
        holiday_calendar_id=request.sla.holiday_calendar_id,
        allow_pause=request.sla.allow_pause,
        pause_on_customer_action=request.sla.pause_on_customer_action,
        warning_threshold=request.sla.warning_threshold,
        critical_threshold=request.sla.critical_threshold,
        is_active=True
    )
    
    # Create escalation rules
    escalation_rules = []
    for idx, rule_req in enumerate(request.escalation_rules):
        rule = EscalationRule(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            name=rule_req.name,
            description=rule_req.description,
            trigger_after_hours=rule_req.trigger_after_hours,
            trigger_after_percentage=rule_req.trigger_after_percentage,
            escalation_type=rule_req.escalation_type,
            send_reminder_to_assignee=rule_req.send_reminder_to_assignee,
            notify_supervisor=rule_req.notify_supervisor,
            notify_users=rule_req.notify_users,
            auto_transfer_to=rule_req.auto_transfer_to,
            escalate_to_next_level=rule_req.escalate_to_next_level,
            repeat_escalation=rule_req.repeat_escalation,
            repeat_interval_hours=rule_req.repeat_interval_hours,
            is_active=True
        )
        escalation_rules.append(rule)
    
    # Create combined config
    config = SLAEscalationConfig(
        config_id=config_id,
        name=request.name,
        entity_type=request.entity_type,
        sla=sla_config,
        escalation_rules=escalation_rules,
        send_breach_notification=request.send_breach_notification
    )
    
    # Store in database (simplified - should use proper model)
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=config_id,
        template_name=config.name,
        template_type='sla_config',
        definition={
            'config': config.dict()
        },
        is_active=True,
        created_by=current_user['id']
    )
    
    db.add(template)
    db.commit()
    
    return {
        "success": True,
        "data": {
            "config_id": config_id,
            "sla_id": sla_id,
            "name": config.name,
            "entity_type": config.entity_type,
            "sla": sla_config.dict(),
            "escalation_rules": [r.dict() for r in escalation_rules]
        }
    }


@router.get("/configurations", tags=["SLA Configuration"])
def list_sla_configurations(
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List SLA configurations"""
    
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'sla_config',
        WorkflowTemplate.is_active == True
    )
    
    if entity_type:
        # Filter by entity type in definition
        query = query.filter(
            WorkflowTemplate.definition['config']['entity_type'].astext == entity_type
        )
    
    templates = query.all()
    
    configurations = []
    for template in templates:
        config_data = template.definition.get('config', {})
        configurations.append({
            'config_id': template.template_key,
            'name': template.template_name,
            'entity_type': config_data.get('entity_type'),
            'sla': config_data.get('sla'),
            'escalation_rules': config_data.get('escalation_rules', []),
            'created_at': template.created_at
        })
    
    return {
        "success": True,
        "data": configurations
    }


@router.get("/configurations/{config_id}", tags=["SLA Configuration"])
def get_sla_configuration(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get SLA configuration details"""
    
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == config_id,
        WorkflowTemplate.template_type == 'sla_config'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="SLA configuration not found")
    
    config_data = template.definition.get('config', {})
    
    return {
        "success": True,
        "data": config_data
    }


@router.get("/templates", tags=["SLA Configuration"])
def get_sla_templates():
    """Get pre-configured SLA templates"""
    
    templates = [
        SLATemplates.loan_approval_sla(),
        SLATemplates.kyc_verification_sla()
    ]
    
    return {
        "success": True,
        "data": [t.dict() for t in templates]
    }


# ==================== SLA INSTANCE ENDPOINTS ====================

@router.post("/instances/start", tags=["SLA Tracking"])
def start_sla_tracking(
    request: StartSLARequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Start SLA tracking for workflow instance"""
    
    # Get SLA configuration
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == request.sla_config_id,
        WorkflowTemplate.template_type == 'sla_config'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="SLA configuration not found")
    
    config_data = template.definition.get('config', {})
    sla_config = SLAConfiguration(**config_data['sla'])
    
    # Get holiday calendar if specified
    holiday_calendar = None
    if sla_config.holiday_calendar_id:
        cal_template = db.query(WorkflowTemplate).filter(
            WorkflowTemplate.tenant_id == tenant_id,
            WorkflowTemplate.template_key == sla_config.holiday_calendar_id,
            WorkflowTemplate.template_type == 'holiday_calendar'
        ).first()
        
        if cal_template:
            holiday_calendar = HolidayCalendar(**cal_template.definition.get('calendar', {}))
    
    # Start SLA
    engine = SLAEngine(db, tenant_id)
    sla_instance = engine.start_sla(
        config=sla_config,
        entity_id=request.entity_id,
        workflow_instance_id=request.workflow_instance_id,
        workflow_step_id=request.workflow_step_id,
        holiday_calendar=holiday_calendar
    )
    
    db.commit()
    
    return {
        "success": True,
        "data": {
            "sla_instance_id": sla_instance.id,
            "status": sla_instance.status,
            "start_time": sla_instance.start_time,
            "deadline": sla_instance.deadline,
            "message": "SLA tracking started"
        }
    }


@router.post("/instances/{instance_id}/complete", tags=["SLA Tracking"])
def complete_sla(
    instance_id: int,
    success: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Mark SLA as completed"""
    
    from backend.shared.database.workflow_models import WorkflowSLA
    
    sla_instance = db.query(WorkflowSLA).filter(
        WorkflowSLA.id == instance_id,
        WorkflowSLA.tenant_id == tenant_id
    ).first()
    
    if not sla_instance:
        raise HTTPException(status_code=404, detail="SLA instance not found")
    
    engine = SLAEngine(db, tenant_id)
    engine.complete_sla(sla_instance, success)
    
    db.commit()
    
    return {
        "success": True,
        "data": {
            "status": sla_instance.status,
            "completion_time": sla_instance.completion_time,
            "time_elapsed_minutes": sla_instance.time_elapsed_minutes,
            "sla_percentage": sla_instance.sla_percentage
        }
    }


@router.post("/instances/{instance_id}/pause", tags=["SLA Tracking"])
def pause_sla(
    instance_id: int,
    request: PauseSLARequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Pause SLA tracking"""
    
    from backend.shared.database.workflow_models import WorkflowSLA
    
    sla_instance = db.query(WorkflowSLA).filter(
        WorkflowSLA.id == instance_id,
        WorkflowSLA.tenant_id == tenant_id
    ).first()
    
    if not sla_instance:
        raise HTTPException(status_code=404, detail="SLA instance not found")
    
    engine = SLAEngine(db, tenant_id)
    result = engine.pause_sla(sla_instance, request.reason)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    db.commit()
    
    return {
        "success": True,
        "data": result
    }


@router.post("/instances/{instance_id}/resume", tags=["SLA Tracking"])
def resume_sla(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Resume SLA tracking"""
    
    from backend.shared.database.workflow_models import WorkflowSLA
    
    sla_instance = db.query(WorkflowSLA).filter(
        WorkflowSLA.id == instance_id,
        WorkflowSLA.tenant_id == tenant_id
    ).first()
    
    if not sla_instance:
        raise HTTPException(status_code=404, detail="SLA instance not found")
    
    engine = SLAEngine(db, tenant_id)
    result = engine.resume_sla(sla_instance)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    
    db.commit()
    
    return {
        "success": True,
        "data": result
    }


@router.get("/instances/{instance_id}/status", tags=["SLA Tracking"])
def get_sla_status(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get current SLA status"""
    
    from backend.shared.database.workflow_models import WorkflowSLA
    
    sla_instance = db.query(WorkflowSLA).filter(
        WorkflowSLA.id == instance_id,
        WorkflowSLA.tenant_id == tenant_id
    ).first()
    
    if not sla_instance:
        raise HTTPException(status_code=404, detail="SLA instance not found")
    
    engine = SLAEngine(db, tenant_id)
    metrics = engine.update_sla_status(sla_instance)
    
    return {
        "success": True,
        "data": {
            "instance_id": sla_instance.id,
            "status": sla_instance.status,
            "start_time": sla_instance.start_time,
            "deadline": sla_instance.deadline,
            "completion_time": sla_instance.completion_time,
            "time_elapsed_minutes": metrics['time_elapsed_minutes'],
            "time_remaining_minutes": metrics['time_remaining_minutes'],
            "sla_percentage": metrics['sla_percentage'],
            "escalation_count": sla_instance.escalation_count,
            "total_paused_duration": sla_instance.total_paused_duration,
            "breach_time": sla_instance.breach_time,
            "breach_duration_minutes": sla_instance.breach_duration_minutes
        }
    }


@router.get("/instances", tags=["SLA Tracking"])
def list_sla_instances(
    entity_type: Optional[str] = None,
    status: Optional[str] = None,
    workflow_instance_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List SLA instances"""
    
    from backend.shared.database.workflow_models import WorkflowSLA
    
    query = db.query(WorkflowSLA).filter(
        WorkflowSLA.tenant_id == tenant_id
    )
    
    if entity_type:
        query = query.filter(WorkflowSLA.entity_type == entity_type)
    
    if status:
        query = query.filter(WorkflowSLA.status == status)
    
    if workflow_instance_id:
        query = query.filter(WorkflowSLA.workflow_instance_id == workflow_instance_id)
    
    instances = query.order_by(WorkflowSLA.start_time.desc()).limit(100).all()
    
    # Update metrics for active instances
    engine = SLAEngine(db, tenant_id)
    result_instances = []
    
    for instance in instances:
        if instance.status in [SLAStatus.ACTIVE, SLAStatus.PAUSED]:
            engine.update_sla_status(instance)
        
        result_instances.append({
            "instance_id": instance.id,
            "entity_type": instance.entity_type,
            "entity_id": instance.entity_id,
            "status": instance.status,
            "start_time": instance.start_time,
            "deadline": instance.deadline,
            "time_elapsed_minutes": instance.time_elapsed_minutes,
            "time_remaining_minutes": instance.time_remaining_minutes,
            "sla_percentage": instance.sla_percentage,
            "escalation_count": instance.escalation_count
        })
    
    return {
        "success": True,
        "data": result_instances
    }


# ==================== ESCALATION ENDPOINTS ====================

@router.post("/instances/{instance_id}/process-escalations", tags=["Escalation"])
def process_escalations(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Manually trigger escalation processing"""
    
    from backend.shared.database.workflow_models import WorkflowSLA, WorkflowTemplate
    
    sla_instance = db.query(WorkflowSLA).filter(
        WorkflowSLA.id == instance_id,
        WorkflowSLA.tenant_id == tenant_id
    ).first()
    
    if not sla_instance:
        raise HTTPException(status_code=404, detail="SLA instance not found")
    
    # Get escalation rules
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == sla_instance.sla_config_id,
        WorkflowTemplate.template_type == 'sla_config'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="SLA configuration not found")
    
    config_data = template.definition.get('config', {})
    escalation_rules = [EscalationRule(**rule) for rule in config_data.get('escalation_rules', [])]
    
    # Process escalations
    engine = SLAEngine(db, tenant_id)
    engine.update_sla_status(sla_instance)
    escalations = engine.process_escalations(sla_instance, escalation_rules)
    
    db.commit()
    
    return {
        "success": True,
        "data": {
            "escalations_triggered": len(escalations),
            "escalations": escalations
        }
    }


@router.get("/instances/{instance_id}/escalation-history", tags=["Escalation"])
def get_escalation_history(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get escalation history for SLA instance"""
    
    from backend.shared.database.workflow_models import WorkflowSLA, WorkflowHistory
    
    sla_instance = db.query(WorkflowSLA).filter(
        WorkflowSLA.id == instance_id,
        WorkflowSLA.tenant_id == tenant_id
    ).first()
    
    if not sla_instance:
        raise HTTPException(status_code=404, detail="SLA instance not found")
    
    # Get escalation history
    history = db.query(WorkflowHistory).filter(
        WorkflowHistory.tenant_id == tenant_id,
        WorkflowHistory.workflow_instance_id == sla_instance.workflow_instance_id,
        WorkflowHistory.event_type == 'sla_escalation'
    ).order_by(WorkflowHistory.created_at.desc()).all()
    
    return {
        "success": True,
        "data": [{
            "event_id": h.id,
            "created_at": h.created_at,
            "event_data": h.event_data
        } for h in history]
    }


# ==================== METRICS ENDPOINTS ====================

@router.get("/metrics", tags=["Metrics"])
def get_sla_metrics(
    entity_type: str,
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get SLA performance metrics"""
    
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=period_days)
    
    engine = SLAEngine(db, tenant_id)
    metrics = engine.calculate_metrics(entity_type, period_start, period_end)
    
    return {
        "success": True,
        "data": metrics
    }


# ==================== HOLIDAY CALENDAR ENDPOINTS ====================

@router.post("/holiday-calendars", tags=["Holiday Calendar"])
def create_holiday_calendar(
    request: HolidayCalendarCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create holiday calendar"""
    
    import uuid
    
    calendar_id = f"cal_{uuid.uuid4().hex[:8]}"
    
    calendar = HolidayCalendar(
        calendar_id=calendar_id,
        name=request.name,
        holidays=request.holidays,
        country=request.country,
        region=request.region
    )
    
    # Store in database
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=calendar_id,
        template_name=calendar.name,
        template_type='holiday_calendar',
        definition={
            'calendar': calendar.dict()
        },
        is_active=True,
        created_by=current_user['id']
    )
    
    db.add(template)
    db.commit()
    
    return {
        "success": True,
        "data": calendar.dict()
    }


@router.get("/holiday-calendars", tags=["Holiday Calendar"])
def list_holiday_calendars(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List holiday calendars"""
    
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    templates = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'holiday_calendar',
        WorkflowTemplate.is_active == True
    ).all()
    
    calendars = []
    for template in templates:
        calendar_data = template.definition.get('calendar', {})
        calendars.append(calendar_data)
    
    return {
        "success": True,
        "data": calendars
    }
