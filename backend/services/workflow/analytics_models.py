"""
Workflow Monitoring & Analytics Models

Comprehensive analytics models for:
- Real-time monitoring
- Workflow metrics
- Process mining
- Bottleneck detection
- User productivity
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime


class MetricPeriod(str, Enum):
    """Metric calculation period"""
    TODAY = "today"
    YESTERDAY = "yesterday"
    THIS_WEEK = "this_week"
    LAST_WEEK = "last_week"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_QUARTER = "this_quarter"
    THIS_YEAR = "this_year"
    CUSTOM = "custom"


class WorkflowStatus(str, Enum):
    """Workflow status for filtering"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BottleneckSeverity(str, Enum):
    """Bottleneck severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ==================== REAL-TIME DASHBOARD MODELS ====================

class PendingApprovalSummary(BaseModel):
    """Pending approvals summary"""
    user_id: int
    user_name: str
    total_pending: int
    high_priority: int
    medium_priority: int
    low_priority: int
    overdue_count: int
    avg_age_hours: float
    oldest_approval_days: float


class WorkflowPendingByType(BaseModel):
    """Pending workflows by type"""
    workflow_type: str
    workflow_name: str
    pending_count: int
    in_progress_count: int
    avg_completion_time_hours: float
    oldest_pending_days: float


class SLABreachAlert(BaseModel):
    """SLA breach alert"""
    alert_id: str
    workflow_instance_id: int
    workflow_name: str
    entity_type: str
    entity_id: int
    breach_time: datetime
    breach_duration_minutes: int
    assigned_to: Optional[int]
    assigned_to_name: Optional[str]
    severity: str  # warning, critical, breached
    sla_percentage: float


class BottleneckInfo(BaseModel):
    """Workflow bottleneck information"""
    step_key: str
    step_name: str
    workflow_type: str
    avg_duration_hours: float
    max_duration_hours: float
    pending_count: int
    completion_rate: float
    severity: BottleneckSeverity
    recommendation: str


class RealtimeDashboard(BaseModel):
    """Real-time dashboard data"""
    timestamp: datetime
    
    # Summary metrics
    total_active_workflows: int
    total_pending_approvals: int
    total_sla_breaches: int
    total_bottlenecks: int
    
    # Pending approvals
    pending_by_user: List[PendingApprovalSummary]
    pending_by_workflow: List[WorkflowPendingByType]
    
    # Alerts
    sla_breach_alerts: List[SLABreachAlert]
    bottlenecks: List[BottleneckInfo]
    
    # Quick stats
    avg_cycle_time_hours: float
    approval_rate: float  # % of approvals vs rejections
    completion_rate_today: float


# ==================== WORKFLOW METRICS MODELS ====================

class WorkflowTypeMetrics(BaseModel):
    """Metrics for a specific workflow type"""
    workflow_type: str
    workflow_name: str
    
    # Volume metrics
    total_workflows: int
    active_workflows: int
    completed_workflows: int
    failed_workflows: int
    cancelled_workflows: int
    
    # Performance metrics
    completion_rate: float  # % completed
    avg_cycle_time_hours: float
    median_cycle_time_hours: float
    min_cycle_time_hours: float
    max_cycle_time_hours: float
    
    # Current state
    longest_pending_days: float
    total_pending: int
    
    # Approval metrics
    approval_rate: float
    rejection_rate: float
    
    # SLA metrics
    sla_compliance_rate: float
    avg_sla_breach_duration_hours: Optional[float]


class StepMetrics(BaseModel):
    """Metrics for a workflow step"""
    step_key: str
    step_name: str
    step_type: str
    
    # Volume
    total_executions: int
    successful_executions: int
    failed_executions: int
    
    # Timing
    avg_duration_hours: float
    median_duration_hours: float
    max_duration_hours: float
    
    # Status
    currently_pending: int
    completion_rate: float
    
    # Bottleneck indicators
    is_bottleneck: bool
    bottleneck_severity: Optional[BottleneckSeverity]


class UserProductivityMetrics(BaseModel):
    """User productivity metrics"""
    user_id: int
    user_name: str
    
    # Volume
    total_tasks_assigned: int
    tasks_completed: int
    tasks_pending: int
    tasks_overdue: int
    
    # Performance
    completion_rate: float
    avg_completion_time_hours: float
    approval_rate: float  # % approved vs rejected
    
    # Productivity
    tasks_completed_today: int
    tasks_completed_this_week: int
    tasks_completed_this_month: int
    
    # Quality
    avg_response_time_hours: float
    on_time_completion_rate: float


class WorkflowMetrics(BaseModel):
    """Comprehensive workflow metrics"""
    period: MetricPeriod
    period_start: datetime
    period_end: datetime
    
    # Overall metrics
    total_workflows: int
    active_workflows: int
    completion_rate: float
    avg_cycle_time_hours: float
    
    # By type
    by_workflow_type: List[WorkflowTypeMetrics]
    
    # By step
    by_step: List[StepMetrics]
    
    # By user
    user_productivity: List[UserProductivityMetrics]
    
    # Bottlenecks
    bottlenecks: List[BottleneckInfo]


# ==================== PROCESS MINING MODELS ====================

class WorkflowPath(BaseModel):
    """Actual path taken through workflow"""
    path_id: str
    path_sequence: List[str]  # List of step keys
    frequency: int  # How many times this path was taken
    percentage: float  # % of total workflows
    avg_duration_hours: float
    is_designed_path: bool
    deviation_points: List[str]  # Steps that deviate from design


class PathDeviation(BaseModel):
    """Deviation from designed workflow"""
    workflow_instance_id: int
    designed_path: List[str]
    actual_path: List[str]
    deviation_steps: List[str]
    deviation_type: str  # skipped, added, reordered
    deviation_reason: Optional[str]
    impact_on_duration: float  # Hours added/saved


class ProcessOptimizationSuggestion(BaseModel):
    """Process optimization suggestion"""
    suggestion_id: str
    suggestion_type: str  # remove_step, parallel_execution, automation, consolidation
    priority: str  # low, medium, high
    
    # Details
    affected_steps: List[str]
    current_avg_duration_hours: float
    estimated_improvement_hours: float
    estimated_improvement_percentage: float
    
    # Description
    title: str
    description: str
    rationale: str
    implementation_effort: str  # low, medium, high
    
    # Impact
    workflows_affected_count: int
    annual_time_savings_hours: float


class ProcessMiningAnalysis(BaseModel):
    """Complete process mining analysis"""
    workflow_type: str
    analysis_date: datetime
    total_workflows_analyzed: int
    
    # Path analysis
    unique_paths: int
    most_common_path: WorkflowPath
    all_paths: List[WorkflowPath]
    designed_path_adherence_rate: float  # % following designed path
    
    # Deviation analysis
    total_deviations: int
    deviation_rate: float
    common_deviations: List[PathDeviation]
    
    # Performance
    fastest_path: WorkflowPath
    slowest_path: WorkflowPath
    avg_path_duration_hours: float
    
    # Optimization
    optimization_suggestions: List[ProcessOptimizationSuggestion]
    estimated_total_improvement_hours: float


# ==================== TREND ANALYSIS MODELS ====================

class TrendDataPoint(BaseModel):
    """Single data point in trend"""
    timestamp: datetime
    value: float
    label: str


class WorkflowTrend(BaseModel):
    """Workflow metric trend over time"""
    metric_name: str
    metric_type: str  # volume, duration, rate
    period: MetricPeriod
    
    # Data points
    data_points: List[TrendDataPoint]
    
    # Trend analysis
    trend_direction: str  # increasing, decreasing, stable
    change_percentage: float
    is_positive_trend: bool  # Depends on metric type
    
    # Statistics
    avg_value: float
    min_value: float
    max_value: float
    std_deviation: float


class ComparativeAnalysis(BaseModel):
    """Compare metrics across different dimensions"""
    comparison_type: str  # workflow_type, user, time_period
    
    # Comparison data
    categories: List[str]
    metric_name: str
    values: List[float]
    
    # Analysis
    best_performer: str
    worst_performer: str
    avg_value: float
    range_value: float


# ==================== ALERT MODELS ====================

class AlertRule(BaseModel):
    """Alert rule configuration"""
    rule_id: str
    rule_name: str
    rule_type: str  # sla_breach, bottleneck, low_productivity, high_rejection
    
    # Conditions
    metric: str
    operator: str  # gt, lt, eq, gte, lte
    threshold: float
    duration_minutes: Optional[int]  # Alert if condition persists
    
    # Actions
    notify_users: List[int]
    notify_roles: List[str]
    severity: str  # info, warning, critical
    
    # Status
    is_active: bool
    last_triggered: Optional[datetime]


class Alert(BaseModel):
    """Generated alert"""
    alert_id: str
    rule_id: str
    alert_type: str
    severity: str
    
    # Details
    title: str
    message: str
    metric_value: float
    threshold_value: float
    
    # Context
    workflow_instance_id: Optional[int]
    workflow_type: Optional[str]
    user_id: Optional[int]
    step_key: Optional[str]
    
    # Status
    triggered_at: datetime
    acknowledged: bool
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[datetime]
    resolved: bool
    resolved_at: Optional[datetime]


# ==================== EXPORT MODELS ====================

class ReportConfig(BaseModel):
    """Report configuration"""
    report_type: str  # dashboard, metrics, process_mining, trend
    period: MetricPeriod
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    
    # Filters
    workflow_types: Optional[List[str]]
    user_ids: Optional[List[int]]
    include_charts: bool = True
    include_details: bool = True
    
    # Format
    export_format: str  # pdf, excel, csv, json


class DashboardSnapshot(BaseModel):
    """Dashboard snapshot for export"""
    snapshot_id: str
    snapshot_date: datetime
    
    # Dashboard data
    dashboard: RealtimeDashboard
    metrics: WorkflowMetrics
    trends: List[WorkflowTrend]
    
    # Metadata
    generated_by: int
    report_config: ReportConfig
