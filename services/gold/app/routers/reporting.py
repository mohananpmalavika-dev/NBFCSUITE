"""
Reporting and Analytics Router
Phase 9: Reporting & Analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date

from ..database import get_db
from ..models.reporting import (
    ReportDefinition, ReportTemplate, ReportSchedule, ReportExecution,
    ReportParameter, ReportExport, DashboardDefinition, DashboardWidget,
    DataSnapshot, AnalyticsMetric
)
from ..schemas.reporting import (
    ReportDefinitionCreate, ReportDefinitionUpdate, ReportDefinitionResponse,
    ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateResponse,
    ReportScheduleCreate, ReportScheduleUpdate, ReportScheduleResponse,
    ReportExecutionCreate, ReportExecutionUpdate, ReportExecutionResponse,
    ReportParameterCreate, ReportParameterUpdate, ReportParameterResponse,
    ReportExportCreate, ReportExportUpdate, ReportExportResponse,
    DashboardDefinitionCreate, DashboardDefinitionUpdate, DashboardDefinitionResponse,
    DashboardWidgetCreate, DashboardWidgetUpdate, DashboardWidgetResponse,
    DataSnapshotCreate, DataSnapshotUpdate, DataSnapshotResponse,
    AnalyticsMetricCreate, AnalyticsMetricUpdate, AnalyticsMetricResponse,
    ReportExecuteRequest, ReportGenerationRequest, ReportGenerationResponse,
    DashboardAnalyticsRequest, DashboardAnalyticsResponse, WidgetDataResponse,
    ReportCatalogResponse, ReportCatalogItem, AnalyticsQueryRequest,
    AnalyticsQueryResponse, MetricValueResponse, DashboardWithWidgetsResponse,
    SchedulePauseRequest, ScheduleResumeRequest, ScheduleExecuteNowRequest,
    ExportShareRequest, ExportShareResponse
)

router = APIRouter(prefix="/api/v1/gold/reporting", tags=["reporting"])


# =====================================================
# Report Definitions Endpoints
# =====================================================

@router.post("/definitions", response_model=ReportDefinitionResponse, status_code=201)
def create_report_definition(
    definition: ReportDefinitionCreate,
    db: Session = Depends(get_db)
):
    """Create a new report definition"""
    # Check for duplicate code
    existing = db.query(ReportDefinition).filter(
        ReportDefinition.code == definition.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Report code already exists")
    
    db_definition = ReportDefinition(**definition.model_dump())
    db.add(db_definition)
    db.commit()
    db.refresh(db_definition)
    return db_definition


@router.get("/definitions", response_model=List[ReportDefinitionResponse])
def list_report_definitions(
    category: Optional[str] = None,
    report_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_system: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List report definitions with filters"""
    query = db.query(ReportDefinition)
    
    if category:
        query = query.filter(ReportDefinition.category == category)
    if report_type:
        query = query.filter(ReportDefinition.report_type == report_type)
    if is_active is not None:
        query = query.filter(ReportDefinition.is_active == is_active)
    if is_system is not None:
        query = query.filter(ReportDefinition.is_system == is_system)
    
    query = query.order_by(ReportDefinition.name)
    return query.offset(skip).limit(limit).all()


@router.get("/definitions/{definition_id}", response_model=ReportDefinitionResponse)
def get_report_definition(definition_id: int, db: Session = Depends(get_db)):
    """Get report definition by ID"""
    definition = db.query(ReportDefinition).filter(
        ReportDefinition.id == definition_id
    ).first()
    if not definition:
        raise HTTPException(status_code=404, detail="Report definition not found")
    return definition


@router.get("/definitions/by-code/{code}", response_model=ReportDefinitionResponse)
def get_report_definition_by_code(code: str, db: Session = Depends(get_db)):
    """Get report definition by code"""
    definition = db.query(ReportDefinition).filter(
        ReportDefinition.code == code
    ).first()
    if not definition:
        raise HTTPException(status_code=404, detail="Report definition not found")
    return definition


@router.put("/definitions/{definition_id}", response_model=ReportDefinitionResponse)
def update_report_definition(
    definition_id: int,
    definition: ReportDefinitionUpdate,
    db: Session = Depends(get_db)
):
    """Update report definition"""
    db_definition = db.query(ReportDefinition).filter(
        ReportDefinition.id == definition_id
    ).first()
    if not db_definition:
        raise HTTPException(status_code=404, detail="Report definition not found")
    
    if db_definition.is_system:
        raise HTTPException(status_code=403, detail="Cannot modify system reports")
    
    update_data = definition.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_definition, field, value)
    
    db.commit()
    db.refresh(db_definition)
    return db_definition


@router.delete("/definitions/{definition_id}", status_code=204)
def delete_report_definition(definition_id: int, db: Session = Depends(get_db)):
    """Delete report definition"""
    definition = db.query(ReportDefinition).filter(
        ReportDefinition.id == definition_id
    ).first()
    if not definition:
        raise HTTPException(status_code=404, detail="Report definition not found")
    
    if definition.is_system:
        raise HTTPException(status_code=403, detail="Cannot delete system reports")
    
    db.delete(definition)
    db.commit()
    return None


# =====================================================
# Report Templates Endpoints
# =====================================================

@router.post("/templates", response_model=ReportTemplateResponse, status_code=201)
def create_report_template(
    template: ReportTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new report template"""
    db_template = ReportTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/templates", response_model=List[ReportTemplateResponse])
def list_report_templates(
    report_definition_id: Optional[int] = None,
    template_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List report templates"""
    query = db.query(ReportTemplate)
    
    if report_definition_id:
        query = query.filter(ReportTemplate.report_definition_id == report_definition_id)
    if template_type:
        query = query.filter(ReportTemplate.template_type == template_type)
    if is_active is not None:
        query = query.filter(ReportTemplate.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
def get_report_template(template_id: int, db: Session = Depends(get_db)):
    """Get report template by ID"""
    template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/templates/{template_id}", response_model=ReportTemplateResponse)
def update_report_template(
    template_id: int,
    template: ReportTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update report template"""
    db_template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id
    ).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/templates/{template_id}", status_code=204)
def delete_report_template(template_id: int, db: Session = Depends(get_db)):
    """Delete report template"""
    template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    return None



# =====================================================
# Report Schedules Endpoints
# =====================================================

@router.post("/schedules", response_model=ReportScheduleResponse, status_code=201)
def create_report_schedule(
    schedule: ReportScheduleCreate,
    db: Session = Depends(get_db)
):
    """Create a new report schedule"""
    db_schedule = ReportSchedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.get("/schedules", response_model=List[ReportScheduleResponse])
def list_report_schedules(
    report_definition_id: Optional[int] = None,
    status: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List report schedules"""
    query = db.query(ReportSchedule)
    
    if report_definition_id:
        query = query.filter(ReportSchedule.report_definition_id == report_definition_id)
    if status:
        query = query.filter(ReportSchedule.status == status)
    if is_active is not None:
        query = query.filter(ReportSchedule.is_active == is_active)
    
    query = query.order_by(desc(ReportSchedule.created_at))
    return query.offset(skip).limit(limit).all()


@router.get("/schedules/{schedule_id}", response_model=ReportScheduleResponse)
def get_report_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Get report schedule by ID"""
    schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.put("/schedules/{schedule_id}", response_model=ReportScheduleResponse)
def update_report_schedule(
    schedule_id: int,
    schedule: ReportScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update report schedule"""
    db_schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    update_data = schedule.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.post("/schedules/{schedule_id}/pause", response_model=ReportScheduleResponse)
def pause_report_schedule(
    schedule_id: int,
    request: SchedulePauseRequest,
    db: Session = Depends(get_db)
):
    """Pause a report schedule"""
    schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule.status = 'paused'
    db.commit()
    db.refresh(schedule)
    return schedule


@router.post("/schedules/{schedule_id}/resume", response_model=ReportScheduleResponse)
def resume_report_schedule(
    schedule_id: int,
    request: ScheduleResumeRequest,
    db: Session = Depends(get_db)
):
    """Resume a report schedule"""
    schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule.status = 'active'
    if request.next_execution_at:
        schedule.next_execution_at = request.next_execution_at
    db.commit()
    db.refresh(schedule)
    return schedule


@router.post("/schedules/{schedule_id}/execute", response_model=ReportExecutionResponse)
def execute_schedule_now(
    schedule_id: int,
    request: ScheduleExecuteNowRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Execute a schedule immediately"""
    schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Create execution record
    execution = ReportExecution(
        report_definition_id=schedule.report_definition_id,
        schedule_id=schedule.id,
        template_id=schedule.template_id,
        execution_type='manual',
        parameters=request.override_parameters or schedule.parameters,
        output_format=schedule.output_format,
        status='pending',
        started_at=datetime.utcnow()
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # In production, this would trigger actual report generation
    # background_tasks.add_task(generate_report, execution.id)
    
    return execution


@router.delete("/schedules/{schedule_id}", status_code=204)
def delete_report_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Delete report schedule"""
    schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    return None


# =====================================================
# Report Executions Endpoints
# =====================================================

@router.post("/executions", response_model=ReportExecutionResponse, status_code=201)
def create_report_execution(
    execution: ReportExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and start a report execution"""
    db_execution = ReportExecution(
        **execution.model_dump(),
        status='pending',
        started_at=datetime.utcnow()
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    
    # In production, trigger actual report generation
    # background_tasks.add_task(generate_report, db_execution.id)
    
    return db_execution


@router.get("/executions", response_model=List[ReportExecutionResponse])
def list_report_executions(
    report_definition_id: Optional[int] = None,
    schedule_id: Optional[int] = None,
    status: Optional[str] = None,
    execution_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List report executions with filters"""
    query = db.query(ReportExecution)
    
    if report_definition_id:
        query = query.filter(ReportExecution.report_definition_id == report_definition_id)
    if schedule_id:
        query = query.filter(ReportExecution.schedule_id == schedule_id)
    if status:
        query = query.filter(ReportExecution.status == status)
    if execution_type:
        query = query.filter(ReportExecution.execution_type == execution_type)
    if date_from:
        query = query.filter(ReportExecution.created_at >= date_from)
    if date_to:
        query = query.filter(ReportExecution.created_at <= date_to)
    
    query = query.order_by(desc(ReportExecution.created_at))
    return query.offset(skip).limit(limit).all()


@router.get("/executions/{execution_id}", response_model=ReportExecutionResponse)
def get_report_execution(execution_id: int, db: Session = Depends(get_db)):
    """Get report execution by ID"""
    execution = db.query(ReportExecution).filter(
        ReportExecution.id == execution_id
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.put("/executions/{execution_id}", response_model=ReportExecutionResponse)
def update_report_execution(
    execution_id: int,
    execution: ReportExecutionUpdate,
    db: Session = Depends(get_db)
):
    """Update report execution"""
    db_execution = db.query(ReportExecution).filter(
        ReportExecution.id == execution_id
    ).first()
    if not db_execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    update_data = execution.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_execution, field, value)
    
    db.commit()
    db.refresh(db_execution)
    return db_execution


@router.post("/executions/{execution_id}/cancel", response_model=ReportExecutionResponse)
def cancel_report_execution(execution_id: int, db: Session = Depends(get_db)):
    """Cancel a running report execution"""
    execution = db.query(ReportExecution).filter(
        ReportExecution.id == execution_id
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.status not in ['pending', 'running']:
        raise HTTPException(
            status_code=400,
            detail="Can only cancel pending or running executions"
        )
    
    execution.status = 'cancelled'
    execution.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(execution)
    return execution



# =====================================================
# Report Parameters Endpoints
# =====================================================

@router.post("/parameters", response_model=ReportParameterResponse, status_code=201)
def create_report_parameter(
    parameter: ReportParameterCreate,
    db: Session = Depends(get_db)
):
    """Create a new report parameter"""
    db_parameter = ReportParameter(**parameter.model_dump())
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter


@router.get("/parameters", response_model=List[ReportParameterResponse])
def list_report_parameters(
    report_definition_id: int,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List report parameters for a definition"""
    query = db.query(ReportParameter).filter(
        ReportParameter.report_definition_id == report_definition_id
    )
    
    if is_active is not None:
        query = query.filter(ReportParameter.is_active == is_active)
    
    query = query.order_by(ReportParameter.display_order)
    return query.all()


@router.get("/parameters/{parameter_id}", response_model=ReportParameterResponse)
def get_report_parameter(parameter_id: int, db: Session = Depends(get_db)):
    """Get report parameter by ID"""
    parameter = db.query(ReportParameter).filter(
        ReportParameter.id == parameter_id
    ).first()
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    return parameter


@router.put("/parameters/{parameter_id}", response_model=ReportParameterResponse)
def update_report_parameter(
    parameter_id: int,
    parameter: ReportParameterUpdate,
    db: Session = Depends(get_db)
):
    """Update report parameter"""
    db_parameter = db.query(ReportParameter).filter(
        ReportParameter.id == parameter_id
    ).first()
    if not db_parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    
    update_data = parameter.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_parameter, field, value)
    
    db.commit()
    db.refresh(db_parameter)
    return db_parameter


@router.delete("/parameters/{parameter_id}", status_code=204)
def delete_report_parameter(parameter_id: int, db: Session = Depends(get_db)):
    """Delete report parameter"""
    parameter = db.query(ReportParameter).filter(
        ReportParameter.id == parameter_id
    ).first()
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    
    db.delete(parameter)
    db.commit()
    return None


# =====================================================
# Report Exports Endpoints
# =====================================================

@router.post("/exports", response_model=ReportExportResponse, status_code=201)
def create_report_export(
    export: ReportExportCreate,
    db: Session = Depends(get_db)
):
    """Create a new report export"""
    db_export = ReportExport(**export.model_dump())
    db.add(db_export)
    db.commit()
    db.refresh(db_export)
    return db_export


@router.get("/exports", response_model=List[ReportExportResponse])
def list_report_exports(
    execution_id: Optional[int] = None,
    export_format: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List report exports"""
    query = db.query(ReportExport)
    
    if execution_id:
        query = query.filter(ReportExport.execution_id == execution_id)
    if export_format:
        query = query.filter(ReportExport.export_format == export_format)
    if status:
        query = query.filter(ReportExport.status == status)
    
    query = query.order_by(desc(ReportExport.created_at))
    return query.offset(skip).limit(limit).all()


@router.get("/exports/{export_id}", response_model=ReportExportResponse)
def get_report_export(export_id: int, db: Session = Depends(get_db)):
    """Get report export by ID"""
    export = db.query(ReportExport).filter(
        ReportExport.id == export_id
    ).first()
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    return export


@router.get("/exports/{export_id}/download")
def download_report_export(export_id: int, db: Session = Depends(get_db)):
    """Download report export file"""
    export = db.query(ReportExport).filter(
        ReportExport.id == export_id
    ).first()
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    
    if export.status != 'available':
        raise HTTPException(status_code=400, detail="Export not available")
    
    # Update download count
    export.download_count += 1
    export.last_downloaded_at = datetime.utcnow()
    db.commit()
    
    # In production, return actual file
    return {"file_url": export.file_url, "file_name": export.file_name}


@router.post("/exports/{export_id}/share", response_model=ExportShareResponse)
def share_report_export(
    export_id: int,
    request: ExportShareRequest,
    db: Session = Depends(get_db)
):
    """Share report export with recipients"""
    export = db.query(ReportExport).filter(
        ReportExport.id == export_id
    ).first()
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    
    # Generate share token
    import secrets
    access_token = secrets.token_urlsafe(32)
    
    # In production, send emails to recipients and create share record
    share_url = f"https://app.example.com/reports/shared/{export_id}?token={access_token}"
    
    return ExportShareResponse(
        share_url=share_url,
        access_token=access_token,
        expires_at=datetime.utcnow()
    )


@router.delete("/exports/{export_id}", status_code=204)
def delete_report_export(export_id: int, db: Session = Depends(get_db)):
    """Delete report export"""
    export = db.query(ReportExport).filter(
        ReportExport.id == export_id
    ).first()
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    
    export.status = 'deleted'
    db.commit()
    return None


# =====================================================
# Dashboard Definitions Endpoints
# =====================================================

@router.post("/dashboards", response_model=DashboardDefinitionResponse, status_code=201)
def create_dashboard(
    dashboard: DashboardDefinitionCreate,
    db: Session = Depends(get_db)
):
    """Create a new dashboard definition"""
    # Check for duplicate code
    existing = db.query(DashboardDefinition).filter(
        DashboardDefinition.code == dashboard.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Dashboard code already exists")
    
    db_dashboard = DashboardDefinition(**dashboard.model_dump())
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


@router.get("/dashboards", response_model=List[DashboardDefinitionResponse])
def list_dashboards(
    dashboard_type: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List dashboard definitions"""
    query = db.query(DashboardDefinition)
    
    if dashboard_type:
        query = query.filter(DashboardDefinition.dashboard_type == dashboard_type)
    if category:
        query = query.filter(DashboardDefinition.category == category)
    if is_active is not None:
        query = query.filter(DashboardDefinition.is_active == is_active)
    
    query = query.order_by(DashboardDefinition.display_order)
    return query.offset(skip).limit(limit).all()


@router.get("/dashboards/{dashboard_id}", response_model=DashboardWithWidgetsResponse)
def get_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    """Get dashboard with widgets"""
    dashboard = db.query(DashboardDefinition).filter(
        DashboardDefinition.id == dashboard_id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.get("/dashboards/by-code/{code}", response_model=DashboardWithWidgetsResponse)
def get_dashboard_by_code(code: str, db: Session = Depends(get_db)):
    """Get dashboard by code with widgets"""
    dashboard = db.query(DashboardDefinition).filter(
        DashboardDefinition.code == code
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.put("/dashboards/{dashboard_id}", response_model=DashboardDefinitionResponse)
def update_dashboard(
    dashboard_id: int,
    dashboard: DashboardDefinitionUpdate,
    db: Session = Depends(get_db)
):
    """Update dashboard definition"""
    db_dashboard = db.query(DashboardDefinition).filter(
        DashboardDefinition.id == dashboard_id
    ).first()
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    update_data = dashboard.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dashboard, field, value)
    
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


@router.delete("/dashboards/{dashboard_id}", status_code=204)
def delete_dashboard(dashboard_id: int, db: Session = Depends(get_db)):
    """Delete dashboard definition"""
    dashboard = db.query(DashboardDefinition).filter(
        DashboardDefinition.id == dashboard_id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    db.delete(dashboard)
    db.commit()
    return None



# =====================================================
# Dashboard Widgets Endpoints
# =====================================================

@router.post("/dashboards/{dashboard_id}/widgets", response_model=DashboardWidgetResponse, status_code=201)
def create_dashboard_widget(
    dashboard_id: int,
    widget: DashboardWidgetCreate,
    db: Session = Depends(get_db)
):
    """Create a new dashboard widget"""
    # Verify dashboard exists
    dashboard = db.query(DashboardDefinition).filter(
        DashboardDefinition.id == dashboard_id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    db_widget = DashboardWidget(**widget.model_dump())
    db.add(db_widget)
    db.commit()
    db.refresh(db_widget)
    return db_widget


@router.get("/dashboards/{dashboard_id}/widgets", response_model=List[DashboardWidgetResponse])
def list_dashboard_widgets(
    dashboard_id: int,
    is_visible: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List widgets for a dashboard"""
    query = db.query(DashboardWidget).filter(
        DashboardWidget.dashboard_id == dashboard_id
    )
    
    if is_visible is not None:
        query = query.filter(DashboardWidget.is_visible == is_visible)
    
    query = query.order_by(DashboardWidget.display_order)
    return query.all()


@router.get("/widgets/{widget_id}", response_model=DashboardWidgetResponse)
def get_dashboard_widget(widget_id: int, db: Session = Depends(get_db)):
    """Get dashboard widget by ID"""
    widget = db.query(DashboardWidget).filter(
        DashboardWidget.id == widget_id
    ).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget


@router.put("/widgets/{widget_id}", response_model=DashboardWidgetResponse)
def update_dashboard_widget(
    widget_id: int,
    widget: DashboardWidgetUpdate,
    db: Session = Depends(get_db)
):
    """Update dashboard widget"""
    db_widget = db.query(DashboardWidget).filter(
        DashboardWidget.id == widget_id
    ).first()
    if not db_widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    update_data = widget.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_widget, field, value)
    
    db.commit()
    db.refresh(db_widget)
    return db_widget


@router.delete("/widgets/{widget_id}", status_code=204)
def delete_dashboard_widget(widget_id: int, db: Session = Depends(get_db)):
    """Delete dashboard widget"""
    widget = db.query(DashboardWidget).filter(
        DashboardWidget.id == widget_id
    ).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    db.delete(widget)
    db.commit()
    return None


@router.get("/widgets/{widget_id}/data", response_model=WidgetDataResponse)
def get_widget_data(
    widget_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    filters: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get data for a specific widget"""
    widget = db.query(DashboardWidget).filter(
        DashboardWidget.id == widget_id
    ).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    # In production, execute widget query and return actual data
    # This is a placeholder response
    return WidgetDataResponse(
        widget_id=widget.id,
        widget_type=widget.widget_type,
        title=widget.title,
        data={"message": "Widget data would be generated here"},
        metadata={"query_time_ms": 150}
    )


# =====================================================
# Data Snapshots Endpoints
# =====================================================

@router.post("/snapshots", response_model=DataSnapshotResponse, status_code=201)
def create_data_snapshot(
    snapshot: DataSnapshotCreate,
    db: Session = Depends(get_db)
):
    """Create a new data snapshot"""
    db_snapshot = DataSnapshot(**snapshot.model_dump())
    db.add(db_snapshot)
    db.commit()
    db.refresh(db_snapshot)
    return db_snapshot


@router.get("/snapshots", response_model=List[DataSnapshotResponse])
def list_data_snapshots(
    snapshot_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List data snapshots"""
    query = db.query(DataSnapshot)
    
    if snapshot_type:
        query = query.filter(DataSnapshot.snapshot_type == snapshot_type)
    if entity_type:
        query = query.filter(DataSnapshot.entity_type == entity_type)
    if date_from:
        query = query.filter(DataSnapshot.snapshot_date >= date_from)
    if date_to:
        query = query.filter(DataSnapshot.snapshot_date <= date_to)
    if status:
        query = query.filter(DataSnapshot.status == status)
    
    query = query.order_by(desc(DataSnapshot.snapshot_date))
    return query.offset(skip).limit(limit).all()


@router.get("/snapshots/{snapshot_id}", response_model=DataSnapshotResponse)
def get_data_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    """Get data snapshot by ID"""
    snapshot = db.query(DataSnapshot).filter(
        DataSnapshot.id == snapshot_id
    ).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


@router.put("/snapshots/{snapshot_id}", response_model=DataSnapshotResponse)
def update_data_snapshot(
    snapshot_id: int,
    snapshot: DataSnapshotUpdate,
    db: Session = Depends(get_db)
):
    """Update data snapshot"""
    db_snapshot = db.query(DataSnapshot).filter(
        DataSnapshot.id == snapshot_id
    ).first()
    if not db_snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    update_data = snapshot.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_snapshot, field, value)
    
    db.commit()
    db.refresh(db_snapshot)
    return db_snapshot


@router.delete("/snapshots/{snapshot_id}", status_code=204)
def delete_data_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    """Delete data snapshot"""
    snapshot = db.query(DataSnapshot).filter(
        DataSnapshot.id == snapshot_id
    ).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    db.delete(snapshot)
    db.commit()
    return None


# =====================================================
# Analytics Metrics Endpoints
# =====================================================

@router.post("/metrics", response_model=AnalyticsMetricResponse, status_code=201)
def create_analytics_metric(
    metric: AnalyticsMetricCreate,
    db: Session = Depends(get_db)
):
    """Create a new analytics metric"""
    # Check for duplicate code
    existing = db.query(AnalyticsMetric).filter(
        AnalyticsMetric.metric_code == metric.metric_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Metric code already exists")
    
    db_metric = AnalyticsMetric(**metric.model_dump())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


@router.get("/metrics", response_model=List[AnalyticsMetricResponse])
def list_analytics_metrics(
    metric_category: Optional[str] = None,
    metric_type: Optional[str] = None,
    is_kpi: Optional[bool] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List analytics metrics"""
    query = db.query(AnalyticsMetric)
    
    if metric_category:
        query = query.filter(AnalyticsMetric.metric_category == metric_category)
    if metric_type:
        query = query.filter(AnalyticsMetric.metric_type == metric_type)
    if is_kpi is not None:
        query = query.filter(AnalyticsMetric.is_kpi == is_kpi)
    if is_active is not None:
        query = query.filter(AnalyticsMetric.is_active == is_active)
    
    query = query.order_by(AnalyticsMetric.display_order)
    return query.offset(skip).limit(limit).all()


@router.get("/metrics/{metric_id}", response_model=AnalyticsMetricResponse)
def get_analytics_metric(metric_id: int, db: Session = Depends(get_db)):
    """Get analytics metric by ID"""
    metric = db.query(AnalyticsMetric).filter(
        AnalyticsMetric.id == metric_id
    ).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.get("/metrics/by-code/{code}", response_model=AnalyticsMetricResponse)
def get_analytics_metric_by_code(code: str, db: Session = Depends(get_db)):
    """Get analytics metric by code"""
    metric = db.query(AnalyticsMetric).filter(
        AnalyticsMetric.metric_code == code
    ).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.put("/metrics/{metric_id}", response_model=AnalyticsMetricResponse)
def update_analytics_metric(
    metric_id: int,
    metric: AnalyticsMetricUpdate,
    db: Session = Depends(get_db)
):
    """Update analytics metric"""
    db_metric = db.query(AnalyticsMetric).filter(
        AnalyticsMetric.id == metric_id
    ).first()
    if not db_metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    update_data = metric.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_metric, field, value)
    
    db.commit()
    db.refresh(db_metric)
    return db_metric


@router.delete("/metrics/{metric_id}", status_code=204)
def delete_analytics_metric(metric_id: int, db: Session = Depends(get_db)):
    """Delete analytics metric"""
    metric = db.query(AnalyticsMetric).filter(
        AnalyticsMetric.id == metric_id
    ).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    db.delete(metric)
    db.commit()
    return None


# =====================================================
# Report Generation & Analytics Endpoints
# =====================================================

@router.post("/generate", response_model=ReportGenerationResponse)
def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate a report by code"""
    # Find report definition
    definition = db.query(ReportDefinition).filter(
        ReportDefinition.code == request.report_code
    ).first()
    if not definition:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Create execution record
    execution = ReportExecution(
        report_definition_id=definition.id,
        template_id=request.template_id,
        execution_type='api',
        parameters=request.parameters,
        filters=request.filters,
        output_format=request.output_format,
        status='pending',
        started_at=datetime.utcnow()
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # In production, trigger actual report generation
    # background_tasks.add_task(generate_report_file, execution.id)
    
    return ReportGenerationResponse(
        execution_id=execution.id,
        status='pending',
        message='Report generation started',
        estimated_completion=datetime.utcnow()
    )


@router.get("/catalog", response_model=ReportCatalogResponse)
def get_report_catalog(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get report catalog with statistics"""
    query = db.query(ReportDefinition).filter(
        ReportDefinition.is_active == True
    )
    
    if category:
        query = query.filter(ReportDefinition.category == category)
    
    definitions = query.all()
    
    catalog_items = []
    for definition in definitions:
        # Get execution stats
        executions = db.query(ReportExecution).filter(
            ReportExecution.report_definition_id == definition.id
        ).all()
        
        parameters = db.query(ReportParameter).filter(
            ReportParameter.report_definition_id == definition.id
        ).count()
        
        last_execution = max(
            [e.completed_at for e in executions if e.completed_at],
            default=None
        )
        
        avg_duration = None
        if executions:
            durations = [e.duration_seconds for e in executions if e.duration_seconds]
            if durations:
                avg_duration = sum(durations) // len(durations)
        
        catalog_items.append(ReportCatalogItem(
            id=definition.id,
            code=definition.code,
            name=definition.name,
            description=definition.description,
            category=definition.category,
            report_type=definition.report_type,
            is_system=definition.is_system,
            parameter_count=parameters,
            last_execution=last_execution,
            execution_count=len(executions),
            avg_duration=avg_duration
        ))
    
    return ReportCatalogResponse(
        total_count=len(catalog_items),
        reports=catalog_items
    )


@router.post("/analytics/query", response_model=AnalyticsQueryResponse)
def query_analytics(
    request: AnalyticsQueryRequest,
    db: Session = Depends(get_db)
):
    """Query analytics data for metrics"""
    # In production, execute actual metric calculations
    # This is a placeholder response
    
    metrics = []
    for code in request.metric_codes:
        metric_def = db.query(AnalyticsMetric).filter(
            AnalyticsMetric.metric_code == code
        ).first()
        if metric_def:
            metrics.append(MetricValueResponse(
                metric_code=code,
                metric_name=metric_def.metric_name,
                value=0,  # Calculated value would go here
                unit=metric_def.unit,
                trend='stable',
                change_percentage=0.0
            ))
    
    return AnalyticsQueryResponse(
        metrics=metrics,
        time_series=[],
        aggregations={}
    )


@router.post("/dashboards/{dashboard_code}/analytics", response_model=DashboardAnalyticsResponse)
def get_dashboard_analytics(
    dashboard_code: str,
    request: DashboardAnalyticsRequest,
    db: Session = Depends(get_db)
):
    """Get analytics data for a dashboard"""
    dashboard = db.query(DashboardDefinition).filter(
        DashboardDefinition.code == dashboard_code
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Get widgets and their data
    widgets = db.query(DashboardWidget).filter(
        DashboardWidget.dashboard_id == dashboard.id,
        DashboardWidget.is_visible == True
    ).order_by(DashboardWidget.display_order).all()
    
    widget_data = []
    for widget in widgets:
        # In production, execute widget queries
        widget_data.append(WidgetDataResponse(
            widget_id=widget.id,
            widget_type=widget.widget_type,
            title=widget.title,
            data={"placeholder": "Widget data"}
        ))
    
    return DashboardAnalyticsResponse(
        dashboard_id=dashboard.id,
        dashboard_name=dashboard.name,
        widgets=widget_data,
        generated_at=datetime.utcnow()
    )
