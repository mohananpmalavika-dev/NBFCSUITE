"""
Reporting and Analytics Schemas
Phase 9: Reporting & Analytics
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal


# =====================================================
# Report Definition Schemas
# =====================================================

class ReportDefinitionBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: str = Field(..., max_length=50)
    report_type: str = Field(..., max_length=50)
    data_source: Optional[str] = Field(None, max_length=100)
    query_template: Optional[str] = None
    output_formats: Optional[List[str]] = Field(default=["pdf", "excel", "csv"])
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[Dict[str, Any]] = None
    sorting: Optional[Dict[str, Any]] = None
    grouping: Optional[Dict[str, Any]] = None
    aggregations: Optional[Dict[str, Any]] = None
    styling: Optional[Dict[str, Any]] = None
    access_roles: Optional[List[str]] = None
    is_active: Optional[bool] = True


class ReportDefinitionCreate(ReportDefinitionBase):
    pass


class ReportDefinitionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    report_type: Optional[str] = Field(None, max_length=50)
    data_source: Optional[str] = Field(None, max_length=100)
    query_template: Optional[str] = None
    output_formats: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[Dict[str, Any]] = None
    sorting: Optional[Dict[str, Any]] = None
    grouping: Optional[Dict[str, Any]] = None
    aggregations: Optional[Dict[str, Any]] = None
    styling: Optional[Dict[str, Any]] = None
    access_roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ReportDefinitionResponse(ReportDefinitionBase):
    id: int
    is_system: bool
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# =====================================================
# Report Template Schemas
# =====================================================

class ReportTemplateBase(BaseModel):
    report_definition_id: int
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    template_type: str = Field(..., max_length=50)
    template_content: Optional[str] = None
    header_content: Optional[str] = None
    footer_content: Optional[str] = None
    styles: Optional[str] = None
    page_size: Optional[str] = Field("A4", max_length=20)
    orientation: Optional[str] = Field("portrait", max_length=20)
    margins: Optional[Dict[str, Any]] = None
    fonts: Optional[Dict[str, Any]] = None
    colors: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    watermark: Optional[str] = None
    is_default: Optional[bool] = False
    is_active: Optional[bool] = True


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    template_type: Optional[str] = Field(None, max_length=50)
    template_content: Optional[str] = None
    header_content: Optional[str] = None
    footer_content: Optional[str] = None
    styles: Optional[str] = None
    page_size: Optional[str] = Field(None, max_length=20)
    orientation: Optional[str] = Field(None, max_length=20)
    margins: Optional[Dict[str, Any]] = None
    fonts: Optional[Dict[str, Any]] = None
    colors: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    watermark: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class ReportTemplateResponse(ReportTemplateBase):
    id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# =====================================================
# Report Schedule Schemas
# =====================================================

class ReportScheduleBase(BaseModel):
    report_definition_id: int
    template_id: Optional[int] = None
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    schedule_type: str = Field(..., max_length=50)
    frequency: Optional[str] = Field(None, max_length=100)
    start_date: date
    end_date: Optional[date] = None
    execution_time: Optional[time] = Field(default=time(0, 0, 0))
    timezone: Optional[str] = Field("UTC", max_length=50)
    parameters: Optional[Dict[str, Any]] = None
    output_format: Optional[str] = Field("pdf", max_length=20)
    delivery_method: Optional[str] = Field(None, max_length=50)
    delivery_config: Optional[Dict[str, Any]] = None
    recipients: Optional[List[str]] = None
    is_active: Optional[bool] = True


class ReportScheduleCreate(ReportScheduleBase):
    pass


class ReportScheduleUpdate(BaseModel):
    template_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    schedule_type: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    execution_time: Optional[time] = None
    timezone: Optional[str] = Field(None, max_length=50)
    parameters: Optional[Dict[str, Any]] = None
    output_format: Optional[str] = Field(None, max_length=20)
    delivery_method: Optional[str] = Field(None, max_length=50)
    delivery_config: Optional[Dict[str, Any]] = None
    recipients: Optional[List[str]] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class ReportScheduleResponse(ReportScheduleBase):
    id: int
    status: str
    last_execution_at: Optional[datetime]
    next_execution_at: Optional[datetime]
    execution_count: int
    success_count: int
    failure_count: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# =====================================================
# Report Execution Schemas
# =====================================================

class ReportExecutionBase(BaseModel):
    report_definition_id: int
    schedule_id: Optional[int] = None
    template_id: Optional[int] = None
    execution_type: str = Field(..., max_length=50)
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    output_format: Optional[str] = Field(None, max_length=20)


class ReportExecutionCreate(ReportExecutionBase):
    pass


class ReportExecutionUpdate(BaseModel):
    status: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = None
    file_url: Optional[str] = Field(None, max_length=500)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    rows_processed: Optional[int] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


class ReportExecutionResponse(ReportExecutionBase):
    id: int
    status: str
    file_path: Optional[str]
    file_size: Optional[int]
    file_url: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    rows_processed: Optional[int]
    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]
    executed_by: Optional[int]
    created_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ReportExecuteRequest(BaseModel):
    """Request to execute a report"""
    report_definition_id: int
    template_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    output_format: Optional[str] = "pdf"


# =====================================================
# Report Parameter Schemas
# =====================================================

class ReportParameterBase(BaseModel):
    report_definition_id: int
    parameter_name: str = Field(..., max_length=100)
    parameter_label: str = Field(..., max_length=200)
    parameter_type: str = Field(..., max_length=50)
    data_type: Optional[str] = Field(None, max_length=50)
    default_value: Optional[str] = None
    is_required: Optional[bool] = False
    validation_rules: Optional[Dict[str, Any]] = None
    options: Optional[List[Dict[str, Any]]] = None
    options_query: Optional[str] = None
    depends_on: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = 0
    help_text: Optional[str] = None
    is_active: Optional[bool] = True


class ReportParameterCreate(ReportParameterBase):
    pass


class ReportParameterUpdate(BaseModel):
    parameter_label: Optional[str] = Field(None, max_length=200)
    parameter_type: Optional[str] = Field(None, max_length=50)
    data_type: Optional[str] = Field(None, max_length=50)
    default_value: Optional[str] = None
    is_required: Optional[bool] = None
    validation_rules: Optional[Dict[str, Any]] = None
    options: Optional[List[Dict[str, Any]]] = None
    options_query: Optional[str] = None
    depends_on: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = None
    help_text: Optional[str] = None
    is_active: Optional[bool] = None


class ReportParameterResponse(ReportParameterBase):
    id: int
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True



# =====================================================
# Report Export Schemas
# =====================================================

class ReportExportBase(BaseModel):
    execution_id: int
    export_format: str = Field(..., max_length=20)
    file_name: str = Field(..., max_length=255)
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = None
    file_url: Optional[str] = Field(None, max_length=500)
    expires_at: Optional[datetime] = None
    is_public: Optional[bool] = False


class ReportExportCreate(ReportExportBase):
    pass


class ReportExportUpdate(BaseModel):
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = None
    file_url: Optional[str] = Field(None, max_length=500)
    download_count: Optional[int] = None
    last_downloaded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: Optional[str] = None


class ReportExportResponse(ReportExportBase):
    id: int
    download_count: int
    last_downloaded_at: Optional[datetime]
    access_token: Optional[str]
    status: str
    created_by: Optional[int]
    created_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# =====================================================
# Dashboard Definition Schemas
# =====================================================

class DashboardDefinitionBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    dashboard_type: str = Field(..., max_length=50)
    category: Optional[str] = Field(None, max_length=50)
    layout: Optional[Dict[str, Any]] = None
    theme: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = None
    access_roles: Optional[List[str]] = None
    is_default: Optional[bool] = False
    is_active: Optional[bool] = True
    display_order: Optional[int] = 0


class DashboardDefinitionCreate(DashboardDefinitionBase):
    pass


class DashboardDefinitionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    dashboard_type: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)
    layout: Optional[Dict[str, Any]] = None
    theme: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = None
    access_roles: Optional[List[str]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class DashboardDefinitionResponse(DashboardDefinitionBase):
    id: int
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# =====================================================
# Dashboard Widget Schemas
# =====================================================

class DashboardWidgetBase(BaseModel):
    dashboard_id: int
    widget_type: str = Field(..., max_length=50)
    chart_type: Optional[str] = Field(None, max_length=50)
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    data_source: Optional[str] = Field(None, max_length=100)
    query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    position: Dict[str, Any] = Field(..., description="Grid position {x, y, width, height}")
    styling: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = None
    drill_down: Optional[Dict[str, Any]] = None
    is_visible: Optional[bool] = True
    display_order: Optional[int] = 0


class DashboardWidgetCreate(DashboardWidgetBase):
    pass


class DashboardWidgetUpdate(BaseModel):
    widget_type: Optional[str] = Field(None, max_length=50)
    chart_type: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    data_source: Optional[str] = Field(None, max_length=100)
    query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None
    styling: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = None
    drill_down: Optional[Dict[str, Any]] = None
    is_visible: Optional[bool] = None
    display_order: Optional[int] = None


class DashboardWidgetResponse(DashboardWidgetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class DashboardWithWidgetsResponse(DashboardDefinitionResponse):
    """Dashboard with nested widgets"""
    widgets: List[DashboardWidgetResponse] = []


# =====================================================
# Data Snapshot Schemas
# =====================================================

class DataSnapshotBase(BaseModel):
    snapshot_type: str = Field(..., max_length=50)
    snapshot_date: date
    snapshot_period: Optional[str] = Field(None, max_length=50)
    entity_type: str = Field(..., max_length=50)
    metrics: Dict[str, Any] = Field(..., description="Snapshot metrics")
    aggregations: Optional[Dict[str, Any]] = None
    comparisons: Optional[Dict[str, Any]] = None
    trends: Optional[Dict[str, Any]] = None
    status: Optional[str] = "active"


class DataSnapshotCreate(DataSnapshotBase):
    pass


class DataSnapshotUpdate(BaseModel):
    metrics: Optional[Dict[str, Any]] = None
    aggregations: Optional[Dict[str, Any]] = None
    comparisons: Optional[Dict[str, Any]] = None
    trends: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class DataSnapshotResponse(DataSnapshotBase):
    id: int
    created_by: Optional[int]
    created_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# =====================================================
# Analytics Metric Schemas
# =====================================================

class AnalyticsMetricBase(BaseModel):
    metric_code: str = Field(..., max_length=100)
    metric_name: str = Field(..., max_length=200)
    metric_category: str = Field(..., max_length=50)
    metric_type: str = Field(..., max_length=50)
    description: Optional[str] = None
    calculation_formula: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=50)
    data_source: Optional[str] = Field(None, max_length=100)
    aggregation_level: Optional[str] = Field(None, max_length=50)
    time_granularity: Optional[str] = Field(None, max_length=50)
    threshold_warning: Optional[Decimal] = None
    threshold_critical: Optional[Decimal] = None
    target_value: Optional[Decimal] = None
    trend_direction: Optional[str] = Field(None, max_length=20)
    is_kpi: Optional[bool] = False
    display_format: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = 0
    is_active: Optional[bool] = True


class AnalyticsMetricCreate(AnalyticsMetricBase):
    pass


class AnalyticsMetricUpdate(BaseModel):
    metric_name: Optional[str] = Field(None, max_length=200)
    metric_category: Optional[str] = Field(None, max_length=50)
    metric_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    calculation_formula: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=50)
    data_source: Optional[str] = Field(None, max_length=100)
    aggregation_level: Optional[str] = Field(None, max_length=50)
    time_granularity: Optional[str] = Field(None, max_length=50)
    threshold_warning: Optional[Decimal] = None
    threshold_critical: Optional[Decimal] = None
    target_value: Optional[Decimal] = None
    trend_direction: Optional[str] = Field(None, max_length=20)
    is_kpi: Optional[bool] = None
    display_format: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class AnalyticsMetricResponse(AnalyticsMetricBase):
    id: int
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class MetricValueResponse(BaseModel):
    """Metric value with metadata"""
    metric_code: str
    metric_name: str
    value: Any
    unit: Optional[str]
    trend: Optional[str] = None  # 'up', 'down', 'stable'
    change_percentage: Optional[Decimal] = None
    previous_value: Optional[Any] = None
    status: Optional[str] = None  # 'normal', 'warning', 'critical'


# =====================================================
# Report Generation Schemas
# =====================================================

class ReportGenerationRequest(BaseModel):
    """Request to generate a report"""
    report_code: str
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    output_format: Optional[str] = "pdf"
    template_id: Optional[int] = None
    delivery_method: Optional[str] = None
    delivery_config: Optional[Dict[str, Any]] = None


class ReportGenerationResponse(BaseModel):
    """Response from report generation"""
    execution_id: int
    status: str
    message: str
    file_url: Optional[str] = None
    estimated_completion: Optional[datetime] = None


# =====================================================
# Dashboard Analytics Schemas
# =====================================================

class DashboardAnalyticsRequest(BaseModel):
    """Request for dashboard analytics data"""
    dashboard_code: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None
    aggregation: Optional[str] = None


class WidgetDataResponse(BaseModel):
    """Widget data response"""
    widget_id: int
    widget_type: str
    title: str
    data: Any
    metadata: Optional[Dict[str, Any]] = None


class DashboardAnalyticsResponse(BaseModel):
    """Dashboard analytics response"""
    dashboard_id: int
    dashboard_name: str
    widgets: List[WidgetDataResponse]
    generated_at: datetime


# =====================================================
# Report Catalog Schemas
# =====================================================

class ReportCatalogItem(BaseModel):
    """Report catalog item for listing"""
    id: int
    code: str
    name: str
    description: Optional[str]
    category: str
    report_type: str
    is_system: bool
    parameter_count: int = 0
    last_execution: Optional[datetime] = None
    execution_count: int = 0
    avg_duration: Optional[int] = None


class ReportCatalogResponse(BaseModel):
    """Report catalog response"""
    total_count: int
    reports: List[ReportCatalogItem]


# =====================================================
# Analytics Query Schemas
# =====================================================

class AnalyticsQueryRequest(BaseModel):
    """Request for analytics query"""
    metric_codes: List[str]
    date_from: date
    date_to: date
    group_by: Optional[str] = None  # 'day', 'week', 'month', 'branch', 'product'
    filters: Optional[Dict[str, Any]] = None


class AnalyticsQueryResponse(BaseModel):
    """Analytics query response"""
    metrics: List[MetricValueResponse]
    time_series: Optional[List[Dict[str, Any]]] = None
    aggregations: Optional[Dict[str, Any]] = None


# =====================================================
# Schedule Management Schemas
# =====================================================

class SchedulePauseRequest(BaseModel):
    """Request to pause a schedule"""
    reason: Optional[str] = None


class ScheduleResumeRequest(BaseModel):
    """Request to resume a schedule"""
    next_execution_at: Optional[datetime] = None


class ScheduleExecuteNowRequest(BaseModel):
    """Request to execute a schedule immediately"""
    override_parameters: Optional[Dict[str, Any]] = None


# =====================================================
# Export Management Schemas
# =====================================================

class ExportDownloadRequest(BaseModel):
    """Request to download an export"""
    access_token: Optional[str] = None


class ExportShareRequest(BaseModel):
    """Request to share an export"""
    recipients: List[str]
    message: Optional[str] = None
    expires_in_days: Optional[int] = 7


class ExportShareResponse(BaseModel):
    """Response from export share"""
    share_url: str
    access_token: str
    expires_at: datetime
