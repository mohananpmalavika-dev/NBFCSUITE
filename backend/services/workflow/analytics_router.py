"""
Workflow Analytics & Monitoring API Router

Endpoints for:
- Real-time dashboard
- Workflow metrics
- Process mining
- User productivity
- Bottleneck detection
- Trend analysis
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, get_tenant_id
from backend.services.workflow.analytics_models import (
    RealtimeDashboard, WorkflowMetrics, ProcessMiningAnalysis,
    WorkflowTrend, MetricPeriod
)
from backend.services.workflow.analytics_engine import AnalyticsEngine


router = APIRouter(prefix="/api/workflow/analytics")


# ==================== REAL-TIME DASHBOARD ====================

@router.get("/dashboard", tags=["Dashboard"])
def get_realtime_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get real-time monitoring dashboard"""
    engine = AnalyticsEngine(db, tenant_id)
    dashboard = engine.get_realtime_dashboard()
    
    return {
        "success": True,
        "data": dashboard.dict()
    }


@router.get("/dashboard/pending-approvals", tags=["Dashboard"])
def get_pending_approvals(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get pending approvals (by user or all)"""
    engine = AnalyticsEngine(db, tenant_id)
    
    if user_id:
        approvals = engine._get_user_pending_approvals(user_id)
    else:
        approvals = engine._get_pending_by_user()
    
    return {
        "success": True,
        "data": [a.dict() for a in approvals]
    }


@router.get("/dashboard/sla-breaches", tags=["Dashboard"])
def get_sla_breaches(
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get SLA breach alerts"""
    engine = AnalyticsEngine(db, tenant_id)
    alerts = engine._get_sla_breach_alerts()
    
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    
    return {
        "success": True,
        "data": [a.dict() for a in alerts]
    }


@router.get("/dashboard/bottlenecks", tags=["Dashboard"])
def get_bottlenecks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get workflow bottlenecks"""
    engine = AnalyticsEngine(db, tenant_id)
    bottlenecks = engine._identify_bottlenecks()
    
    return {
        "success": True,
        "data": [b.dict() for b in bottlenecks]
    }


# ==================== WORKFLOW METRICS ====================

@router.get("/metrics", tags=["Metrics"])
def get_workflow_metrics(
    period: MetricPeriod = MetricPeriod.THIS_MONTH,
    workflow_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get comprehensive workflow metrics"""
    engine = AnalyticsEngine(db, tenant_id)
    
    # Determine period dates
    if period == MetricPeriod.CUSTOM and start_date and end_date:
        period_start, period_end = start_date, end_date
    else:
        period_start, period_end = engine._get_period_dates(period)
    
    metrics = engine.get_workflow_metrics(period_start, period_end, workflow_type)
    
    return {
        "success": True,
        "data": metrics.dict()
    }


@router.get("/metrics/workflow-types", tags=["Metrics"])
def get_workflow_type_metrics(
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get metrics by workflow type"""
    engine = AnalyticsEngine(db, tenant_id)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    metrics = engine.get_workflow_type_metrics(start_date, end_date)
    
    return {
        "success": True,
        "data": [m.dict() for m in metrics]
    }


@router.get("/metrics/steps", tags=["Metrics"])
def get_step_metrics(
    workflow_type: Optional[str] = None,
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get metrics by workflow step"""
    engine = AnalyticsEngine(db, tenant_id)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    metrics = engine.get_step_metrics(start_date, end_date, workflow_type)
    
    return {
        "success": True,
        "data": [m.dict() for m in metrics]
    }


@router.get("/metrics/user-productivity", tags=["Metrics"])
def get_user_productivity(
    user_id: Optional[int] = None,
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get user productivity metrics"""
    engine = AnalyticsEngine(db, tenant_id)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    if user_id:
        metrics = [engine.get_user_productivity(user_id, start_date, end_date)]
    else:
        metrics = engine.get_all_user_productivity(start_date, end_date)
    
    return {
        "success": True,
        "data": [m.dict() for m in metrics]
    }


# ==================== PROCESS MINING ====================

@router.get("/process-mining/{workflow_type}", tags=["Process Mining"])
def get_process_mining_analysis(
    workflow_type: str,
    period_days: int = 90,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get process mining analysis for workflow type"""
    engine = AnalyticsEngine(db, tenant_id)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    analysis = engine.analyze_process(workflow_type, start_date, end_date)
    
    return {
        "success": True,
        "data": analysis.dict()
    }


@router.get("/process-mining/{workflow_type}/paths", tags=["Process Mining"])
def get_workflow_paths(
    workflow_type: str,
    period_days: int = 90,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get all execution paths for workflow"""
    engine = AnalyticsEngine(db, tenant_id)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    paths = engine.analyze_workflow_paths(workflow_type, start_date, end_date)
    
    return {
        "success": True,
        "data": [p.dict() for p in paths]
    }


@router.get("/process-mining/{workflow_type}/deviations", tags=["Process Mining"])
def get_path_deviations(
    workflow_type: str,
    period_days: int = 90,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get workflow path deviations"""
    engine = AnalyticsEngine(db, tenant_id)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    deviations = engine.analyze_deviations(workflow_type, start_date, end_date)
    
    return {
        "success": True,
        "data": [d.dict() for d in deviations]
    }


@router.get("/process-mining/{workflow_type}/optimization", tags=["Process Mining"])
def get_optimization_suggestions(
    workflow_type: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get process optimization suggestions"""
    engine = AnalyticsEngine(db, tenant_id)
    suggestions = engine.generate_optimization_suggestions(workflow_type)
    
    return {
        "success": True,
        "data": [s.dict() for s in suggestions]
    }


# ==================== TREND ANALYSIS ====================

@router.get("/trends/{metric_name}", tags=["Trends"])
def get_metric_trend(
    metric_name: str,
    period: MetricPeriod = MetricPeriod.THIS_MONTH,
    workflow_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get trend data for specific metric"""
    engine = AnalyticsEngine(db, tenant_id)
    period_start, period_end = engine._get_period_dates(period)
    
    trend = engine.get_metric_trend(metric_name, period_start, period_end, workflow_type)
    
    return {
        "success": True,
        "data": trend.dict()
    }


@router.get("/trends/comparison", tags=["Trends"])
def get_comparative_analysis(
    comparison_type: str,  # workflow_type, user, time_period
    metric_name: str,
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get comparative analysis"""
    engine = AnalyticsEngine(db, tenant_id)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    comparison = engine.get_comparative_analysis(
        comparison_type, metric_name, start_date, end_date
    )
    
    return {
        "success": True,
        "data": comparison.dict()
    }


# ==================== QUICK STATS ====================

@router.get("/quick-stats", tags=["Dashboard"])
def get_quick_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get quick statistics for dashboard cards"""
    from backend.shared.database.workflow_models import WorkflowInstance, WorkflowTask
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    stats = {
        "total_active": self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == tenant_id,
            WorkflowInstance.status.in_(['pending', 'in_progress'])
        ).count(),
        
        "completed_today": self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == tenant_id,
            WorkflowInstance.status == 'completed',
            WorkflowInstance.completed_at >= today_start
        ).count(),
        
        "pending_approvals": self.db.query(WorkflowTask).filter(
            WorkflowTask.tenant_id == tenant_id,
            WorkflowTask.status == 'pending',
            WorkflowTask.task_type == 'approval'
        ).count(),
        
        "overdue_tasks": self.db.query(WorkflowTask).filter(
            WorkflowTask.tenant_id == tenant_id,
            WorkflowTask.status == 'pending',
            WorkflowTask.due_date < now
        ).count()
    }
    
    return {
        "success": True,
        "data": stats
    }
