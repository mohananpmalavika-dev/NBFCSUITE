"""
Reporting & Analytics Pydantic Schemas
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ============================================
# ENUMS
# ============================================

class ReportCategory(str, Enum):
    PORTFOLIO = "portfolio"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    REGULATORY = "regulatory"
    RISK = "risk"
    COLLECTION = "collection"
    CUSTOMER = "customer"
    BRANCH = "branch"
    EMPLOYEE = "employee"
    ACCOUNTING = "accounting"
    TREASURY = "treasury"
    DEPOSIT = "deposit"
    COMPLIANCE = "compliance"
    EXECUTIVE = "executive"


class ReportFrequency(str, Enum):
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"


class ReportStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DashboardType(str, Enum):
    EXECUTIVE = "executive"
    OPERATIONS = "operations"
    RISK = "risk"
    COLLECTION = "collection"
    BRANCH = "branch"
    TREASURY = "treasury"
    HR = "hr"
    CUSTOM = "custom"


class VisualizationType(str, Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    DONUT_CHART = "donut_chart"
    AREA_CHART = "area_chart"
    SCATTER_CHART = "scatter_chart"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    KPI_CARD = "kpi_card"
    TABLE = "table"
    PIVOT_TABLE = "pivot_table"
    TREEMAP = "treemap"
    FUNNEL = "funnel"


# ============================================
# REPORT TEMPLATE SCHEMAS
# ============================================

class ReportTemplateBase(BaseModel):
    report_code: str
    report_name: str
    report_description: Optional[str] = None
    category: ReportCategory
    sub_category: Optional[str] = None
    query_template: str
    parameters: Optional[Dict[str, Any]] = None
    default_filters: Optional[Dict[str, Any]] = None
    sort_order: Optional[Dict[str, Any]] = None
    columns: Dict[str, Any]
    summary_fields: Optional[Dict[str, Any]] = None
    visualization_config: Optional[Dict[str, Any]] = None
    frequency: ReportFrequency = ReportFrequency.ON_DEMAND
    schedule_config: Optional[Dict[str, Any]] = None
    is_public: bool = False
    allowed_roles: Optional[List[str]] = None
    required_permissions: Optional[List[str]] = None


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateUpdate(BaseModel):
    report_name: Optional[str] = None
    report_description: Optional[str] = None
    query_template: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    default_filters: Optional[Dict[str, Any]] = None
    columns: Optional[Dict[str, Any]] = None
    visualization_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class ReportTemplateResponse(ReportTemplateBase):
    id: int
    tenant_id: str
    is_active: bool
    is_system: bool
    version: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================
# REPORT GENERATION SCHEMAS
# ============================================

class GenerateReportRequest(BaseModel):
    template_id: Optional[int] = None
    custom_report_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    file_format: str = "pdf"  # pdf, xlsx, csv, json


class GeneratedReportResponse(BaseModel):
    id: int
    tenant_id: str
    template_id: Optional[int]
    report_name: str
    report_category: Optional[ReportCategory]
    generation_date: datetime
    status: ReportStatus
    row_count: Optional[int]
    execution_time_ms: Optional[int]
    result_data: Optional[Dict[str, Any]]
    file_url: Optional[str]
    file_format: str
    file_size_bytes: Optional[int]
    error_message: Optional[str]
    generated_by: str
    accessed_count: int
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# CUSTOM REPORT BUILDER SCHEMAS
# ============================================

class CustomReportBuilderCreate(BaseModel):
    report_name: str
    report_description: Optional[str] = None
    category: Optional[ReportCategory] = None
    data_sources: Dict[str, Any]
    joins: Optional[Dict[str, Any]] = None
    selected_fields: Dict[str, Any]
    calculated_fields: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    grouping: Optional[Dict[str, Any]] = None
    aggregations: Optional[Dict[str, Any]] = None
    sort_order: Optional[Dict[str, Any]] = None
    limit_rows: Optional[int] = None
    visualization_type: Optional[VisualizationType] = None
    visualization_config: Optional[Dict[str, Any]] = None
    is_public: bool = False
    shared_with: Optional[List[str]] = None


class CustomReportBuilderUpdate(BaseModel):
    report_name: Optional[str] = None
    report_description: Optional[str] = None
    data_sources: Optional[Dict[str, Any]] = None
    selected_fields: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    visualization_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class CustomReportBuilderResponse(BaseModel):
    id: int
    tenant_id: str
    report_name: str
    report_description: Optional[str]
    category: Optional[ReportCategory]
    data_sources: Dict[str, Any]
    selected_fields: Dict[str, Any]
    visualization_type: Optional[VisualizationType]
    is_public: bool
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================
# DASHBOARD SCHEMAS
# ============================================

class DashboardCreate(BaseModel):
    dashboard_name: str
    dashboard_description: Optional[str] = None
    dashboard_type: DashboardType
    layout_config: Optional[Dict[str, Any]] = None
    theme: str = "default"
    is_public: bool = False
    allowed_roles: Optional[List[str]] = None


class DashboardUpdate(BaseModel):
    dashboard_name: Optional[str] = None
    dashboard_description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    theme: Optional[str] = None
    is_active: Optional[bool] = None


class DashboardResponse(BaseModel):
    id: int
    tenant_id: str
    dashboard_name: str
    dashboard_description: Optional[str]
    dashboard_type: DashboardType
    layout_config: Optional[Dict[str, Any]]
    theme: str
    is_default: bool
    is_public: bool
    is_system: bool
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DashboardWidgetCreate(BaseModel):
    dashboard_id: int
    position: Dict[str, Any]  # {x, y, width, height}
    widget_title: str
    widget_type: VisualizationType
    data_source_type: str  # report, query, api
    report_template_id: Optional[int] = None
    custom_query: Optional[str] = None
    api_endpoint: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    refresh_interval_seconds: int = 300
    visualization_config: Optional[Dict[str, Any]] = None
    color_scheme: Optional[str] = None


class DashboardWidgetUpdate(BaseModel):
    position: Optional[Dict[str, Any]] = None
    widget_title: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    visualization_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DashboardWidgetResponse(BaseModel):
    id: int
    dashboard_id: int
    position: Dict[str, Any]
    widget_title: str
    widget_type: VisualizationType
    data_source_type: str
    visualization_config: Optional[Dict[str, Any]]
    refresh_interval_seconds: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# PREDICTIVE ANALYTICS SCHEMAS
# ============================================

class PredictiveModelCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_name: str
    model_description: Optional[str] = None
    model_type: str  # classification, regression, clustering
    use_case: str  # credit_risk, churn, default, fraud
    algorithm: str  # random_forest, xgboost, neural_network
    features: Dict[str, Any]
    target_variable: str
    training_data_query: str


class PredictiveModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    tenant_id: str
    model_name: str
    model_description: Optional[str]
    model_type: str
    use_case: str
    algorithm: str
    features: Dict[str, Any]
    accuracy: Optional[float]
    precision_score: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    is_deployed: bool
    is_active: bool
    created_at: datetime


class PredictionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: int
    entity_type: str  # customer, loan, application
    entity_id: str
    input_features: Dict[str, Any]


class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)
    
    id: int
    model_id: int
    entity_type: str
    entity_id: str
    predicted_value: Optional[float]
    predicted_class: Optional[str]
    probability: Optional[float]
    feature_importance: Optional[Dict[str, Any]]
    explanation: Optional[str]
    prediction_date: datetime
    prediction_time_ms: Optional[int]


# ============================================
# SCHEDULED REPORT SCHEMAS
# ============================================

class ScheduledReportCreate(BaseModel):
    template_id: int
    report_name: str
    frequency: ReportFrequency
    cron_expression: Optional[str] = None
    schedule_time: Optional[str] = None  # HH:MM
    schedule_day: Optional[int] = None
    timezone: str = "UTC"
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    delivery_method: Dict[str, Any]  # {type: "email", recipients: [...]}
    file_format: str = "pdf"


class ScheduledReportResponse(BaseModel):
    id: int
    tenant_id: str
    template_id: int
    report_name: str
    frequency: ReportFrequency
    schedule_time: Optional[str]
    is_active: bool
    last_run_at: Optional[datetime]
    last_run_status: Optional[ReportStatus]
    next_run_at: Optional[datetime]
    run_count: int
    failure_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# ANALYTICS SCHEMAS
# ============================================

class ReportAnalyticsResponse(BaseModel):
    template_id: Optional[int]
    report_name: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    avg_execution_time_ms: Optional[int]
    unique_users: int
    total_views: int
    total_downloads: int
    period_start: date
    period_end: date

    class Config:
        from_attributes = True


class DashboardAnalyticsResponse(BaseModel):
    dashboard_id: int
    dashboard_name: str
    total_views: int
    unique_users: int
    avg_session_duration_seconds: Optional[int]
    most_viewed_widget: Optional[str]
    period_start: date
    period_end: date

    class Config:
        from_attributes = True


# ============================================
# PAGINATION SCHEMAS
# ============================================

class PaginatedReportTemplates(BaseModel):
    items: List[ReportTemplateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedGeneratedReports(BaseModel):
    items: List[GeneratedReportResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedDashboards(BaseModel):
    items: List[DashboardResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
