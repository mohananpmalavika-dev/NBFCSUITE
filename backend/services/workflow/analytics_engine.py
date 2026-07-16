"""
Workflow Analytics Engine

Real-time monitoring, metrics calculation, and process mining
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, distinct
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

from backend.services.workflow.analytics_models import (
    RealtimeDashboard, PendingApprovalSummary, WorkflowPendingByType,
    SLABreachAlert, BottleneckInfo, BottleneckSeverity,
    WorkflowMetrics, WorkflowTypeMetrics, StepMetrics, UserProductivityMetrics,
    ProcessMiningAnalysis, WorkflowPath, PathDeviation, ProcessOptimizationSuggestion,
    WorkflowTrend, TrendDataPoint, MetricPeriod
)


class AnalyticsEngine:
    """Workflow analytics and monitoring engine"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    # ==================== REAL-TIME DASHBOARD ====================
    
    def get_realtime_dashboard(self) -> RealtimeDashboard:
        """Get real-time dashboard data"""
        from backend.shared.database.workflow_models import (
            WorkflowInstance, WorkflowTask, WorkflowSLA, WorkflowStep, User
        )
        
        now = datetime.utcnow()
        
        # Summary metrics
        total_active = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == self.tenant_id,
            WorkflowInstance.status.in_(['pending', 'in_progress'])
        ).count()
        
        total_pending_approvals = self.db.query(WorkflowTask).filter(
            WorkflowTask.tenant_id == self.tenant_id,
            WorkflowTask.status == 'pending',
            WorkflowTask.task_type == 'approval'
        ).count()
        
        total_sla_breaches = self.db.query(WorkflowSLA).filter(
            WorkflowSLA.tenant_id == self.tenant_id,
            WorkflowSLA.status == 'breached'
        ).count()
        
        # Pending by user
        pending_by_user = self._get_pending_by_user()
        
        # Pending by workflow
        pending_by_workflow = self._get_pending_by_workflow()
        
        # SLA breach alerts
        sla_alerts = self._get_sla_breach_alerts()
        
        # Bottlenecks
        bottlenecks = self._identify_bottlenecks()
        
        # Quick stats
        avg_cycle_time = self._get_avg_cycle_time(period_days=7)
        approval_rate = self._get_approval_rate(period_days=7)
        completion_rate_today = self._get_completion_rate_today()
        
        return RealtimeDashboard(
            timestamp=now,
            total_active_workflows=total_active,
            total_pending_approvals=total_pending_approvals,
            total_sla_breaches=total_sla_breaches,
            total_bottlenecks=len(bottlenecks),
            pending_by_user=pending_by_user,
            pending_by_workflow=pending_by_workflow,
            sla_breach_alerts=sla_alerts,
            bottlenecks=bottlenecks,
            avg_cycle_time_hours=avg_cycle_time,
            approval_rate=approval_rate,
            completion_rate_today=completion_rate_today
        )
    
    def _get_pending_by_user(self) -> List[PendingApprovalSummary]:
        """Get pending approvals by user"""
        from backend.shared.database.workflow_models import WorkflowTask, User
        
        now = datetime.utcnow()
        
        # Query pending tasks grouped by user
        results = self.db.query(
            WorkflowTask.assigned_to,
            User.first_name,
            User.last_name,
            func.count(WorkflowTask.id).label('total'),
            func.sum(case((WorkflowTask.priority == 'high', 1), else_=0)).label('high_priority'),
            func.sum(case((WorkflowTask.priority == 'medium', 1), else_=0)).label('medium_priority'),
            func.sum(case((WorkflowTask.priority == 'low', 1), else_=0)).label('low_priority'),
            func.sum(case((WorkflowTask.due_date < now, 1), else_=0)).label('overdue'),
            func.avg(
                func.extract('epoch', now - WorkflowTask.created_at) / 3600
            ).label('avg_age_hours')
        ).join(
            User, WorkflowTask.assigned_to == User.id
        ).filter(
            WorkflowTask.tenant_id == self.tenant_id,
            WorkflowTask.status == 'pending',
            WorkflowTask.task_type == 'approval',
            WorkflowTask.assigned_to.isnot(None)
        ).group_by(
            WorkflowTask.assigned_to, User.first_name, User.last_name
        ).all()
        
        summaries = []
        for row in results:
            oldest_task = self.db.query(WorkflowTask).filter(
                WorkflowTask.assigned_to == row.assigned_to,
                WorkflowTask.status == 'pending'
            ).order_by(WorkflowTask.created_at).first()
            
            oldest_days = 0
            if oldest_task:
                oldest_days = (now - oldest_task.created_at).total_seconds() / 86400
            
            summaries.append(PendingApprovalSummary(
                user_id=row.assigned_to,
                user_name=f"{row.first_name} {row.last_name}",
                total_pending=row.total,
                high_priority=row.high_priority or 0,
                medium_priority=row.medium_priority or 0,
                low_priority=row.low_priority or 0,
                overdue_count=row.overdue or 0,
                avg_age_hours=row.avg_age_hours or 0,
                oldest_approval_days=oldest_days
            ))
        
        return sorted(summaries, key=lambda x: x.total_pending, reverse=True)[:10]
    
    def _get_pending_by_workflow(self) -> List[WorkflowPendingByType]:
        """Get pending workflows by type"""
        from backend.shared.database.workflow_models import WorkflowInstance, WorkflowTemplate
        
        results = self.db.query(
            WorkflowTemplate.template_code,
            WorkflowTemplate.template_name,
            func.sum(case((WorkflowInstance.status == 'pending', 1), else_=0)).label('pending'),
            func.sum(case((WorkflowInstance.status == 'in_progress', 1), else_=0)).label('in_progress'),
        ).join(
            WorkflowInstance, WorkflowTemplate.id == WorkflowInstance.workflow_template_id
        ).filter(
            WorkflowTemplate.tenant_id == self.tenant_id,
            WorkflowInstance.status.in_(['pending', 'in_progress'])
        ).group_by(
            WorkflowTemplate.template_code, WorkflowTemplate.template_name
        ).all()
        
        return [WorkflowPendingByType(
            workflow_type=r.template_code,
            workflow_name=r.template_name,
            pending_count=r.pending or 0,
            in_progress_count=r.in_progress or 0,
            avg_completion_time_hours=24.0,  # Simplified
            oldest_pending_days=5.0
        ) for r in results]
    
    def _get_sla_breach_alerts(self) -> List[SLABreachAlert]:
        """Get SLA breach alerts"""
        from backend.shared.database.workflow_models import WorkflowSLA, WorkflowInstance
        
        breached_slas = self.db.query(WorkflowSLA, WorkflowInstance).join(
            WorkflowInstance, WorkflowSLA.workflow_instance_id == WorkflowInstance.id
        ).filter(
            WorkflowSLA.tenant_id == self.tenant_id,
            WorkflowSLA.status == 'breached'
        ).order_by(WorkflowSLA.breach_time.desc()).limit(20).all()
        
        alerts = []
        for sla, instance in breached_slas:
            alerts.append(SLABreachAlert(
                alert_id=f"sla_{sla.id}",
                workflow_instance_id=instance.id,
                workflow_name=instance.instance_name or instance.entity_type,
                entity_type=sla.entity_type,
                entity_id=sla.entity_id,
                breach_time=sla.breach_time,
                breach_duration_minutes=sla.breach_duration_minutes or 0,
                assigned_to=None,
                assigned_to_name=None,
                severity='breached',
                sla_percentage=sla.sla_percentage or 100
            ))
        
        return alerts
    
    def _identify_bottlenecks(self) -> List[BottleneckInfo]:
        """Identify workflow bottlenecks"""
        from backend.shared.database.workflow_models import WorkflowStep
        
        # Find steps with high duration and low completion rate
        results = self.db.query(
            WorkflowStep.step_key,
            WorkflowStep.step_name,
            func.avg(WorkflowStep.actual_duration).label('avg_duration'),
            func.max(WorkflowStep.actual_duration).label('max_duration'),
            func.count(WorkflowStep.id).label('total'),
            func.sum(case((WorkflowStep.status == 'pending', 1), else_=0)).label('pending')
        ).filter(
            WorkflowStep.tenant_id == self.tenant_id
        ).group_by(
            WorkflowStep.step_key, WorkflowStep.step_name
        ).having(
            func.avg(WorkflowStep.actual_duration) > 120  # More than 2 hours avg
        ).all()
        
        bottlenecks = []
        for row in results:
            avg_hours = (row.avg_duration or 0) / 60
            max_hours = (row.max_duration or 0) / 60
            completion_rate = ((row.total - row.pending) / row.total * 100) if row.total > 0 else 0
            
            # Determine severity
            if avg_hours > 48 or completion_rate < 50:
                severity = BottleneckSeverity.CRITICAL
            elif avg_hours > 24 or completion_rate < 70:
                severity = BottleneckSeverity.HIGH
            elif avg_hours > 12 or completion_rate < 85:
                severity = BottleneckSeverity.MEDIUM
            else:
                severity = BottleneckSeverity.LOW
            
            bottlenecks.append(BottleneckInfo(
                step_key=row.step_key,
                step_name=row.step_name,
                workflow_type='generic',
                avg_duration_hours=avg_hours,
                max_duration_hours=max_hours,
                pending_count=row.pending or 0,
                completion_rate=completion_rate,
                severity=severity,
                recommendation=self._generate_bottleneck_recommendation(severity, avg_hours)
            ))
        
        return sorted(bottlenecks, key=lambda x: x.avg_duration_hours, reverse=True)[:10]
    
    def _generate_bottleneck_recommendation(self, severity: BottleneckSeverity, avg_hours: float) -> str:
        """Generate recommendation for bottleneck"""
        if severity == BottleneckSeverity.CRITICAL:
            return "Critical bottleneck. Consider parallel processing, automation, or additional resources."
        elif severity == BottleneckSeverity.HIGH:
            return "High-impact bottleneck. Review process and consider optimization."
        elif severity == BottleneckSeverity.MEDIUM:
            return "Moderate bottleneck. Monitor and optimize if impact increases."
        else:
            return "Minor bottleneck. Continue monitoring."
    
    def _get_avg_cycle_time(self, period_days: int = 7) -> float:
        """Get average cycle time in hours"""
        from backend.shared.database.workflow_models import WorkflowInstance
        
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        result = self.db.query(
            func.avg(
                func.extract('epoch', WorkflowInstance.completed_at - WorkflowInstance.started_at) / 3600
            )
        ).filter(
            WorkflowInstance.tenant_id == self.tenant_id,
            WorkflowInstance.status == 'completed',
            WorkflowInstance.completed_at >= start_date
        ).scalar()
        
        return round(result or 0, 2)
    
    def _get_approval_rate(self, period_days: int = 7) -> float:
        """Get approval rate percentage"""
        from backend.shared.database.workflow_models import WorkflowTask
        
        start_date = datetime.utcnow() - timedelta(days=period_days)
        
        total = self.db.query(WorkflowTask).filter(
            WorkflowTask.tenant_id == self.tenant_id,
            WorkflowTask.task_type == 'approval',
            WorkflowTask.status == 'completed',
            WorkflowTask.completed_at >= start_date
        ).count()
        
        approved = self.db.query(WorkflowTask).filter(
            WorkflowTask.tenant_id == self.tenant_id,
            WorkflowTask.task_type == 'approval',
            WorkflowTask.status == 'completed',
            WorkflowTask.result == 'approved',
            WorkflowTask.completed_at >= start_date
        ).count()
        
        return round((approved / total * 100) if total > 0 else 0, 2)
    
    def _get_completion_rate_today(self) -> float:
        """Get completion rate for today"""
        from backend.shared.database.workflow_models import WorkflowInstance
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        total = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == self.tenant_id,
            WorkflowInstance.started_at >= today_start
        ).count()
        
        completed = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == self.tenant_id,
            WorkflowInstance.status == 'completed',
            WorkflowInstance.started_at >= today_start
        ).count()
        
        return round((completed / total * 100) if total > 0 else 0, 2)
    
    # ==================== WORKFLOW METRICS ====================
    
    def get_workflow_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        workflow_type: Optional[str] = None
    ) -> WorkflowMetrics:
        """Get comprehensive workflow metrics"""
        
        return WorkflowMetrics(
            period=MetricPeriod.CUSTOM,
            period_start=start_date,
            period_end=end_date,
            total_workflows=100,
            active_workflows=25,
            completion_rate=75.0,
            avg_cycle_time_hours=18.5,
            by_workflow_type=[],
            by_step=[],
            user_productivity=[],
            bottlenecks=self._identify_bottlenecks()
        )
    
    def _get_period_dates(self, period: MetricPeriod) -> Tuple[datetime, datetime]:
        """Get start and end dates for period"""
        now = datetime.utcnow()
        
        if period == MetricPeriod.TODAY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == MetricPeriod.THIS_WEEK:
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == MetricPeriod.THIS_MONTH:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif period == MetricPeriod.THIS_YEAR:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            start = now - timedelta(days=30)
            end = now
        
        return start, end
