"""
Phase 14: Analytics & Business Intelligence Schemas
Pydantic schemas for analytics and BI operations
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# =====================================================
# Data Warehouse Schemas
# =====================================================

class DataWarehouseBase(BaseModel):
    warehouse_code: str = Field(..., max_length=50)
    warehouse_name: str = Field(..., max_length=200)
    warehouse_type: str = Field(..., max_length=50)
    connection_config: Dict[str, Any]
    refresh_schedule: Optional[Dict[str, Any]] = None
    status: Optional[str] = "ACTIVE"
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}


class DataWarehouseCreate(DataWarehouseBase):
    maker_comment: Optional[str] = None


class DataWarehouseUpdate(BaseModel):
    warehouse_name: Optional[str] = Field(None, max_length=200)
    connection_config: Optional[Dict[str, Any]] = None
    refresh_schedule: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DataWarehouseApproval(BaseModel):
    checker_comment: Optional[str] = None
    approval_status: str = Field(..., pattern="^(APPROVED|REJECTED)$")


class DataWarehouseResponse(DataWarehouseBase):
    id: UUID
    last_refresh_at: Optional[datetime] = None
    next_refresh_at: Optional[datetime] = None
    storage_size_gb: Optional[Decimal] = None
    row_count: Optional[int] = 0
    maker_id: Optional[UUID] = None
    checker_id: Optional[UUID] = None
    maker_comment: Optional[str] = None
    checker_comment: Optional[str] = None
    approval_status: str
    approved_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Data Source Schemas
# =====================================================

class DataSourceBase(BaseModel):
    source_code: str = Field(..., max_length=50)
    source_name: str = Field(..., max_length=200)
    source_type: str = Field(..., max_length=50)
    connection_string: Optional[str] = None
    connection_config: Dict[str, Any]
    authentication_type: Optional[str] = Field(None, max_length=50)
    schema_config: Optional[Dict[str, Any]] = None
    sync_frequency: Optional[str] = Field(None, max_length=50)
    health_check_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = "ACTIVE"
    metadata: Optional[Dict[str, Any]] = {}


class DataSourceCreate(DataSourceBase):
    credentials_encrypted: Optional[str] = None


class DataSourceUpdate(BaseModel):
    source_name: Optional[str] = Field(None, max_length=200)
    connection_string: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    credentials_encrypted: Optional[str] = None
    schema_config: Optional[Dict[str, Any]] = None
    sync_frequency: Optional[str] = None
    health_check_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DataSourceResponse(DataSourceBase):
    id: UUID
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None
    sync_status: str
    avg_response_time_ms: Optional[int] = None
    data_volume_gb: Optional[Decimal] = None
    record_count: Optional[int] = 0
    health_status: str
    last_health_check_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Report Schemas
# =====================================================

class ReportBase(BaseModel):
    report_code: str = Field(..., max_length=50)
    report_name: str = Field(..., max_length=200)
    report_type: str = Field(..., max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    data_source_id: Optional[UUID] = None
    query_definition: Dict[str, Any]
    parameters: Optional[List[Dict[str, Any]]] = []
    visualization_type: Optional[str] = Field(None, max_length=50)
    visualization_config: Optional[Dict[str, Any]] = None
    layout_config: Optional[Dict[str, Any]] = None
    schedule_enabled: Optional[bool] = False
    schedule_config: Optional[Dict[str, Any]] = None
    cache_enabled: Optional[bool] = True
    cache_duration_minutes: Optional[int] = 60
    is_public: Optional[bool] = False
    shared_with: Optional[List[str]] = []
    status: Optional[str] = "ACTIVE"
    metadata: Optional[Dict[str, Any]] = {}


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    report_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    query_definition: Optional[Dict[str, Any]] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    visualization_config: Optional[Dict[str, Any]] = None
    layout_config: Optional[Dict[str, Any]] = None
    schedule_enabled: Optional[bool] = None
    schedule_config: Optional[Dict[str, Any]] = None
    cache_enabled: Optional[bool] = None
    is_public: Optional[bool] = None
    shared_with: Optional[List[str]] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ReportResponse(ReportBase):
    id: UUID
    owner_id: Optional[UUID] = None
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    avg_execution_time_ms: Optional[int] = None
    last_cached_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


class ReportExecuteRequest(BaseModel):
    parameters: Optional[Dict[str, Any]] = {}
    filters: Optional[Dict[str, Any]] = {}
    output_format: Optional[str] = "JSON"


# =====================================================
# Report Execution Schemas
# =====================================================

class ReportExecutionResponse(BaseModel):
    id: UUID
    execution_code: str
    report_id: UUID
    execution_type: Optional[str] = None
    parameters_used: Optional[Dict[str, Any]] = None
    filters_applied: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    rows_returned: Optional[int] = None
    data_size_kb: Optional[int] = None
    result_status: Optional[str] = None
    result_location: Optional[str] = None
    result_format: Optional[str] = None
    result_preview: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    executed_by: Optional[UUID] = None
    execution_context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Dashboard Schemas
# =====================================================

class DashboardBase(BaseModel):
    dashboard_code: str = Field(..., max_length=50)
    dashboard_name: str = Field(..., max_length=200)
    dashboard_type: str = Field(..., max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    layout_type: Optional[str] = Field(None, max_length=50)
    layout_config: Dict[str, Any]
    widgets: List[Dict[str, Any]]
    auto_refresh: Optional[bool] = True
    refresh_interval_seconds: Optional[int] = 300
    global_filters: Optional[List[Dict[str, Any]]] = []
    filter_config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = False
    shared_with: Optional[List[str]] = []
    theme: Optional[str] = "LIGHT"
    display_config: Optional[Dict[str, Any]] = None
    mobile_optimized: Optional[bool] = True
    status: Optional[str] = "ACTIVE"
    metadata: Optional[Dict[str, Any]] = {}


class DashboardCreate(DashboardBase):
    pass


class DashboardUpdate(BaseModel):
    dashboard_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    widgets: Optional[List[Dict[str, Any]]] = None
    auto_refresh: Optional[bool] = None
    refresh_interval_seconds: Optional[int] = None
    global_filters: Optional[List[Dict[str, Any]]] = None
    filter_config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    shared_with: Optional[List[str]] = None
    theme: Optional[str] = None
    display_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DashboardResponse(DashboardBase):
    id: UUID
    owner_id: Optional[UUID] = None
    last_refreshed_at: Optional[datetime] = None
    view_count: int = 0
    last_viewed_at: Optional[datetime] = None
    avg_load_time_ms: Optional[int] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Widget Schemas
# =====================================================

class WidgetBase(BaseModel):
    widget_code: str = Field(..., max_length=50)
    widget_name: str = Field(..., max_length=200)
    widget_type: str = Field(..., max_length=50)
    report_id: Optional[UUID] = None
    data_source_id: Optional[UUID] = None
    query_config: Optional[Dict[str, Any]] = None
    chart_type: Optional[str] = Field(None, max_length=50)
    visualization_config: Dict[str, Any]
    color_scheme: Optional[str] = Field(None, max_length=50)
    drill_down_enabled: Optional[bool] = False
    drill_down_config: Optional[Dict[str, Any]] = None
    click_actions: Optional[Dict[str, Any]] = None
    auto_refresh: Optional[bool] = True
    refresh_interval_seconds: Optional[int] = 300
    cache_enabled: Optional[bool] = True
    size_config: Optional[Dict[str, Any]] = None
    position_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = "ACTIVE"
    metadata: Optional[Dict[str, Any]] = {}


class WidgetCreate(WidgetBase):
    pass


class WidgetUpdate(BaseModel):
    widget_name: Optional[str] = Field(None, max_length=200)
    query_config: Optional[Dict[str, Any]] = None
    visualization_config: Optional[Dict[str, Any]] = None
    color_scheme: Optional[str] = None
    drill_down_enabled: Optional[bool] = None
    drill_down_config: Optional[Dict[str, Any]] = None
    auto_refresh: Optional[bool] = None
    refresh_interval_seconds: Optional[int] = None
    size_config: Optional[Dict[str, Any]] = None
    position_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WidgetResponse(WidgetBase):
    id: UUID
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# ML Model Schemas
# =====================================================

class MLModelBase(BaseModel):
    model_code: str = Field(..., max_length=50)
    model_name: str = Field(..., max_length=200)
    model_type: str = Field(..., max_length=50)
    algorithm: Optional[str] = Field(None, max_length=100)
    framework: Optional[str] = Field(None, max_length=50)
    version: str = Field(..., max_length=20)
    model_file_path: Optional[str] = None
    model_artifact_url: Optional[str] = None
    training_data_source_id: Optional[UUID] = None
    training_dataset_size: Optional[int] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    feature_importance: Optional[Dict[str, Any]] = None
    deployment_status: Optional[str] = "TRAINED"
    deployment_endpoint: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    metadata: Optional[Dict[str, Any]] = {}


class MLModelCreate(MLModelBase):
    pass


class MLModelUpdate(BaseModel):
    model_name: Optional[str] = Field(None, max_length=200)
    version: Optional[str] = Field(None, max_length=20)
    model_file_path: Optional[str] = None
    model_artifact_url: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    feature_importance: Optional[Dict[str, Any]] = None
    deployment_status: Optional[str] = None
    deployment_endpoint: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MLModelPerformanceUpdate(BaseModel):
    accuracy_score: Optional[Decimal] = None
    precision_score: Optional[Decimal] = None
    recall_score: Optional[Decimal] = None
    f1_score: Optional[Decimal] = None
    rmse: Optional[Decimal] = None
    mae: Optional[Decimal] = None
    r2_score: Optional[Decimal] = None
    performance_metrics: Optional[Dict[str, Any]] = None


class MLModelResponse(MLModelBase):
    id: UUID
    training_started_at: Optional[datetime] = None
    training_completed_at: Optional[datetime] = None
    training_duration_minutes: Optional[int] = None
    accuracy_score: Optional[Decimal] = None
    precision_score: Optional[Decimal] = None
    recall_score: Optional[Decimal] = None
    f1_score: Optional[Decimal] = None
    rmse: Optional[Decimal] = None
    mae: Optional[Decimal] = None
    r2_score: Optional[Decimal] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    deployed_at: Optional[datetime] = None
    prediction_count: int = 0
    last_prediction_at: Optional[datetime] = None
    avg_prediction_time_ms: Optional[int] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Prediction Schemas
# =====================================================

class PredictionRequest(BaseModel):
    input_features: Dict[str, Any]
    prediction_type: Optional[str] = "REAL_TIME"
    business_context: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    id: UUID
    prediction_code: str
    model_id: UUID
    input_features: Dict[str, Any]
    prediction_result: Dict[str, Any]
    confidence_score: Optional[Decimal] = None
    prediction_time_ms: Optional[int] = None
    model_version: Optional[str] = None
    prediction_type: Optional[str] = None
    business_context: Optional[Dict[str, Any]] = None
    requested_by: Optional[UUID] = None
    request_context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionValidation(BaseModel):
    actual_value: Dict[str, Any]
    validation_notes: Optional[str] = None


# =====================================================
# Data Stream Schemas
# =====================================================

class DataStreamBase(BaseModel):
    stream_code: str = Field(..., max_length=50)
    stream_name: str = Field(..., max_length=200)
    stream_type: str = Field(..., max_length=50)
    connection_config: Dict[str, Any]
    topic_name: Optional[str] = Field(None, max_length=200)
    partition_key: Optional[str] = Field(None, max_length=100)
    data_format: Optional[str] = Field(None, max_length=50)
    schema_definition: Optional[Dict[str, Any]] = None
    processing_mode: Optional[str] = Field(None, max_length=50)
    batch_size: Optional[int] = 100
    batch_timeout_ms: Optional[int] = 5000
    consumer_groups: Optional[List[str]] = []
    consumer_config: Optional[Dict[str, Any]] = None
    error_handling_strategy: Optional[str] = Field(None, max_length=50)
    dead_letter_queue: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = "ACTIVE"
    metadata: Optional[Dict[str, Any]] = {}


class DataStreamCreate(DataStreamBase):
    pass


class DataStreamUpdate(BaseModel):
    stream_name: Optional[str] = Field(None, max_length=200)
    connection_config: Optional[Dict[str, Any]] = None
    topic_name: Optional[str] = None
    schema_definition: Optional[Dict[str, Any]] = None
    processing_mode: Optional[str] = None
    batch_size: Optional[int] = None
    batch_timeout_ms: Optional[int] = None
    consumer_groups: Optional[List[str]] = None
    consumer_config: Optional[Dict[str, Any]] = None
    error_handling_strategy: Optional[str] = None
    dead_letter_queue: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DataStreamResponse(DataStreamBase):
    id: UUID
    messages_per_second: Optional[Decimal] = None
    total_messages_processed: int = 0
    last_message_at: Optional[datetime] = None
    lag_seconds: Optional[int] = None
    error_count: int = 0
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Analytics Alert Schemas
# =====================================================

class AnalyticsAlertBase(BaseModel):
    alert_code: str = Field(..., max_length=50)
    alert_name: str = Field(..., max_length=200)
    alert_type: str = Field(..., max_length=50)
    severity: Optional[str] = Field(None, max_length=20)
    data_source_id: Optional[UUID] = None
    metric_name: Optional[str] = Field(None, max_length=200)
    condition_config: Dict[str, Any]
    evaluation_frequency_minutes: Optional[int] = 15
    lookback_period_minutes: Optional[int] = 60
    detection_algorithm: Optional[str] = Field(None, max_length=50)
    sensitivity: Optional[Decimal] = Decimal("0.95")
    notification_channels: Optional[List[str]] = []
    notification_template: Optional[str] = None
    recipients: Optional[List[str]] = []
    suppression_enabled: Optional[bool] = False
    suppression_duration_minutes: Optional[int] = None
    status: Optional[str] = "ACTIVE"
    metadata: Optional[Dict[str, Any]] = {}


class AnalyticsAlertCreate(AnalyticsAlertBase):
    pass


class AnalyticsAlertUpdate(BaseModel):
    alert_name: Optional[str] = Field(None, max_length=200)
    severity: Optional[str] = None
    condition_config: Optional[Dict[str, Any]] = None
    evaluation_frequency_minutes: Optional[int] = None
    lookback_period_minutes: Optional[int] = None
    detection_algorithm: Optional[str] = None
    sensitivity: Optional[Decimal] = None
    notification_channels: Optional[List[str]] = None
    notification_template: Optional[str] = None
    recipients: Optional[List[str]] = None
    suppression_enabled: Optional[bool] = None
    suppression_duration_minutes: Optional[int] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalyticsAlertResponse(AnalyticsAlertBase):
    id: UUID
    last_evaluated_at: Optional[datetime] = None
    next_evaluation_at: Optional[datetime] = None
    is_triggered: bool = False
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    suppressed_until: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Alert Notification Schemas
# =====================================================

class AlertNotificationResponse(BaseModel):
    id: UUID
    notification_code: str
    alert_id: UUID
    notification_type: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    delivery_status: Optional[str] = None
    alert_value: Optional[Dict[str, Any]] = None
    threshold_value: Optional[Dict[str, Any]] = None
    deviation_percentage: Optional[Decimal] = None
    acknowledged_by: Optional[UUID] = None
    acknowledged_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class AlertAcknowledgement(BaseModel):
    resolution_notes: Optional[str] = None


# =====================================================
# Data Quality Rule Schemas
# =====================================================

class DataQualityRuleBase(BaseModel):
    rule_code: str = Field(..., max_length=50)
    rule_name: str = Field(..., max_length=200)
    rule_type: str = Field(..., max_length=50)
    data_source_id: Optional[UUID] = None
    table_name: Optional[str] = Field(None, max_length=200)
    column_name: Optional[str] = Field(None, max_length=200)
    rule_definition: Dict[str, Any]
    validation_query: Optional[str] = None
    expected_value: Optional[Dict[str, Any]] = None
    tolerance: Optional[Decimal] = None
    execution_frequency_minutes: Optional[int] = 60
    on_failure_action: Optional[str] = Field(None, max_length=50)
    notification_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = "ACTIVE"
    metadata: Optional[Dict[str, Any]] = {}


class DataQualityRuleCreate(DataQualityRuleBase):
    pass


class DataQualityRuleUpdate(BaseModel):
    rule_name: Optional[str] = Field(None, max_length=200)
    rule_definition: Optional[Dict[str, Any]] = None
    validation_query: Optional[str] = None
    expected_value: Optional[Dict[str, Any]] = None
    tolerance: Optional[Decimal] = None
    execution_frequency_minutes: Optional[int] = None
    on_failure_action: Optional[str] = None
    notification_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DataQualityRuleResponse(DataQualityRuleBase):
    id: UUID
    last_executed_at: Optional[datetime] = None
    next_execution_at: Optional[datetime] = None
    last_result_status: Optional[str] = None
    pass_rate: Optional[Decimal] = None
    failure_count: int = 0
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int

    class Config:
        from_attributes = True


# =====================================================
# Analytics Statistics Schemas
# =====================================================

class AnalyticsOverview(BaseModel):
    total_data_sources: int
    active_data_sources: int
    total_reports: int
    total_dashboards: int
    total_ml_models: int
    deployed_models: int
    total_streams: int
    active_streams: int
    active_alerts: int
    triggered_alerts: int
    total_dashboard_views: Optional[int] = 0
    total_predictions: Optional[int] = 0


class ReportExecutionMetrics(BaseModel):
    report_id: UUID
    report_code: str
    report_name: str
    report_type: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time_ms: Optional[int] = None
    max_execution_time_ms: Optional[int] = None
    min_execution_time_ms: Optional[int] = None
    avg_rows_returned: Optional[int] = None
    last_execution_at: Optional[datetime] = None


class MLModelPerformanceMetrics(BaseModel):
    model_id: UUID
    model_code: str
    model_name: str
    model_type: str
    algorithm: Optional[str] = None
    deployment_status: str
    accuracy_score: Optional[Decimal] = None
    precision_score: Optional[Decimal] = None
    recall_score: Optional[Decimal] = None
    f1_score: Optional[Decimal] = None
    prediction_count: int
    avg_prediction_time_ms: Optional[int] = None
    last_prediction_at: Optional[datetime] = None
    total_predictions_recorded: int
    avg_confidence_score: Optional[Decimal] = None
    accurate_predictions: int
    inaccurate_predictions: int


class DataStreamHealth(BaseModel):
    stream_id: UUID
    stream_code: str
    stream_name: str
    stream_type: str
    status: str
    messages_per_second: Optional[Decimal] = None
    total_messages_processed: int
    last_message_at: Optional[datetime] = None
    lag_seconds: Optional[int] = None
    error_count: int
    health_status: str
    created_at: datetime
    updated_at: datetime
