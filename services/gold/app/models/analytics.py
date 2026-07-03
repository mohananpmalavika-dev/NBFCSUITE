"""
Phase 14: Analytics & Business Intelligence Models
Comprehensive analytics and BI data models
"""
from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, ForeignKey, TIMESTAMP, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import uuid


class DataWarehouse(BaseModel):
    """Data warehouse configuration model"""
    __tablename__ = "data_warehouses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_code = Column(String(50), unique=True, nullable=False, index=True)
    warehouse_name = Column(String(200), nullable=False)
    warehouse_type = Column(String(50), nullable=False)
    connection_config = Column(JSONB, nullable=False)
    refresh_schedule = Column(JSONB)
    last_refresh_at = Column(TIMESTAMP(timezone=True))
    next_refresh_at = Column(TIMESTAMP(timezone=True))
    status = Column(String(20), default='ACTIVE')
    storage_size_gb = Column(Numeric(15, 2))
    row_count = Column(BigInteger, default=0)
    
    # Metadata
    tags = Column(JSONB, default=[])
    metadata = Column(JSONB, default={})
    
    # Maker-Checker
    maker_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    checker_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    maker_comment = Column(Text)
    checker_comment = Column(Text)
    approval_status = Column(String(20), default='PENDING')
    approved_at = Column(TIMESTAMP(timezone=True))
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    version = Column(Integer, default=1)


class DataSource(BaseModel):
    """Analytics data source model"""
    __tablename__ = "data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_code = Column(String(50), unique=True, nullable=False, index=True)
    source_name = Column(String(200), nullable=False)
    source_type = Column(String(50), nullable=False)
    connection_string = Column(Text)
    connection_config = Column(JSONB, nullable=False)
    authentication_type = Column(String(50))
    credentials_encrypted = Column(Text)
    
    # Data source properties
    schema_config = Column(JSONB)
    sync_frequency = Column(String(50))
    last_sync_at = Column(TIMESTAMP(timezone=True))
    next_sync_at = Column(TIMESTAMP(timezone=True))
    sync_status = Column(String(20), default='PENDING')
    
    # Performance
    avg_response_time_ms = Column(Integer)
    data_volume_gb = Column(Numeric(15, 2))
    record_count = Column(BigInteger, default=0)
    
    # Health monitoring
    health_status = Column(String(20), default='UNKNOWN')
    last_health_check_at = Column(TIMESTAMP(timezone=True))
    health_check_config = Column(JSONB)
    
    status = Column(String(20), default='ACTIVE')
    metadata = Column(JSONB, default={})
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    version = Column(Integer, default=1)
    
    # Relationships
    reports = relationship("Report", back_populates="data_source")
    alerts = relationship("AnalyticsAlert", back_populates="data_source")


class Report(BaseModel):
    """Custom report model"""
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_code = Column(String(50), unique=True, nullable=False, index=True)
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    
    # Report definition
    data_source_id = Column(UUID(as_uuid=True), ForeignKey('data_sources.id'))
    query_definition = Column(JSONB, nullable=False)
    parameters = Column(JSONB, default=[])
    
    # Visualization
    visualization_type = Column(String(50))
    visualization_config = Column(JSONB)
    layout_config = Column(JSONB)
    
    # Scheduling
    schedule_enabled = Column(Boolean, default=False)
    schedule_config = Column(JSONB)
    last_run_at = Column(TIMESTAMP(timezone=True))
    next_run_at = Column(TIMESTAMP(timezone=True))
    
    # Performance
    avg_execution_time_ms = Column(Integer)
    cache_enabled = Column(Boolean, default=True)
    cache_duration_minutes = Column(Integer, default=60)
    last_cached_at = Column(TIMESTAMP(timezone=True))
    
    # Access control
    is_public = Column(Boolean, default=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    shared_with = Column(JSONB, default=[])
    
    status = Column(String(20), default='ACTIVE')
    metadata = Column(JSONB, default={})
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    version = Column(Integer, default=1)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="reports")
    executions = relationship("ReportExecution", back_populates="report", cascade="all, delete-orphan")


class ReportExecution(BaseModel):
    """Report execution history model"""
    __tablename__ = "report_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_code = Column(String(50), unique=True, nullable=False, index=True)
    report_id = Column(UUID(as_uuid=True), ForeignKey('reports.id', ondelete='CASCADE'))
    
    # Execution details
    execution_type = Column(String(50))
    parameters_used = Column(JSONB)
    filters_applied = Column(JSONB)
    
    # Performance metrics
    started_at = Column(TIMESTAMP(timezone=True), nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True))
    execution_time_ms = Column(Integer)
    rows_returned = Column(Integer)
    data_size_kb = Column(Integer)
    
    # Results
    result_status = Column(String(20))
    result_location = Column(Text)
    result_format = Column(String(20))
    result_preview = Column(JSONB)
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSONB)
    retry_count = Column(Integer, default=0)
    
    # User context
    executed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    execution_context = Column(JSONB)
    
    metadata = Column(JSONB, default={})
    
    # Relationships
    report = relationship("Report", back_populates="executions")


class Dashboard(BaseModel):
    """Dashboard model"""
    __tablename__ = "dashboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_code = Column(String(50), unique=True, nullable=False, index=True)
    dashboard_name = Column(String(200), nullable=False)
    dashboard_type = Column(String(50), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    
    # Dashboard configuration
    layout_type = Column(String(50))
    layout_config = Column(JSONB, nullable=False)
    widgets = Column(JSONB, nullable=False)
    
    # Refresh settings
    auto_refresh = Column(Boolean, default=True)
    refresh_interval_seconds = Column(Integer, default=300)
    last_refreshed_at = Column(TIMESTAMP(timezone=True))
    
    # Filters
    global_filters = Column(JSONB, default=[])
    filter_config = Column(JSONB)
    
    # Access control
    is_public = Column(Boolean, default=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    shared_with = Column(JSONB, default=[])
    
    # Display settings
    theme = Column(String(50), default='LIGHT')
    display_config = Column(JSONB)
    mobile_optimized = Column(Boolean, default=True)
    
    # Analytics
    view_count = Column(Integer, default=0)
    last_viewed_at = Column(TIMESTAMP(timezone=True))
    avg_load_time_ms = Column(Integer)
    
    status = Column(String(20), default='ACTIVE')
    metadata = Column(JSONB, default={})
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    version = Column(Integer, default=1)


class Widget(BaseModel):
    """Dashboard widget model"""
    __tablename__ = "widgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    widget_code = Column(String(50), unique=True, nullable=False, index=True)
    widget_name = Column(String(200), nullable=False)
    widget_type = Column(String(50), nullable=False)
    
    # Data binding
    report_id = Column(UUID(as_uuid=True), ForeignKey('reports.id'))
    data_source_id = Column(UUID(as_uuid=True), ForeignKey('data_sources.id'))
    query_config = Column(JSONB)
    
    # Visualization
    chart_type = Column(String(50))
    visualization_config = Column(JSONB, nullable=False)
    color_scheme = Column(String(50))
    
    # Interactivity
    drill_down_enabled = Column(Boolean, default=False)
    drill_down_config = Column(JSONB)
    click_actions = Column(JSONB)
    
    # Refresh
    auto_refresh = Column(Boolean, default=True)
    refresh_interval_seconds = Column(Integer, default=300)
    cache_enabled = Column(Boolean, default=True)
    
    # Display
    size_config = Column(JSONB)
    position_config = Column(JSONB)
    
    status = Column(String(20), default='ACTIVE')
    metadata = Column(JSONB, default={})
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    version = Column(Integer, default=1)


class MLModel(BaseModel):
    """Machine learning model registry"""
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_code = Column(String(50), unique=True, nullable=False, index=True)
    model_name = Column(String(200), nullable=False)
    model_type = Column(String(50), nullable=False)
    algorithm = Column(String(100))
    
    # Model configuration
    framework = Column(String(50))
    version = Column(String(20), nullable=False)
    model_file_path = Column(Text)
    model_artifact_url = Column(Text)
    
    # Training details
    training_data_source_id = Column(UUID(as_uuid=True), ForeignKey('data_sources.id'))
    training_dataset_size = Column(Integer)
    training_started_at = Column(TIMESTAMP(timezone=True))
    training_completed_at = Column(TIMESTAMP(timezone=True))
    training_duration_minutes = Column(Integer)
    
    # Model performance
    accuracy_score = Column(Numeric(5, 4))
    precision_score = Column(Numeric(5, 4))
    recall_score = Column(Numeric(5, 4))
    f1_score = Column(Numeric(5, 4))
    rmse = Column(Numeric(15, 4))
    mae = Column(Numeric(15, 4))
    r2_score = Column(Numeric(5, 4))
    performance_metrics = Column(JSONB)
    
    # Hyperparameters
    hyperparameters = Column(JSONB)
    feature_importance = Column(JSONB)
    
    # Deployment
    deployment_status = Column(String(20), default='TRAINED')
    deployment_endpoint = Column(Text)
    deployed_at = Column(TIMESTAMP(timezone=True))
    
    # Usage tracking
    prediction_count = Column(Integer, default=0)
    last_prediction_at = Column(TIMESTAMP(timezone=True))
    avg_prediction_time_ms = Column(Integer)
    
    status = Column(String(20), default='ACTIVE')
    metadata = Column(JSONB, default={})
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    version = Column(Integer, default=1)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")


class Prediction(BaseModel):
    """ML model prediction history"""
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_code = Column(String(50), unique=True, nullable=False, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey('ml_models.id', ondelete='CASCADE'))
    
    # Prediction details
    input_features = Column(JSONB, nullable=False)
    prediction_result = Column(JSONB, nullable=False)
    confidence_score = Column(Numeric(5, 4))
    
    # Performance
    prediction_time_ms = Column(Integer)
    model_version = Column(String(20))
    
    # Context
    prediction_type = Column(String(50))
    business_context = Column(JSONB)
    
    # Validation
    actual_value = Column(JSONB)
    prediction_error = Column(Numeric(15, 4))
    is_accurate = Column(Boolean)
    
    # User tracking
    requested_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    request_context = Column(JSONB)
    
    metadata = Column(JSONB, default={})
    
    # Relationships
    model = relationship("MLModel", back_populates="predictions")


class DataStream(BaseModel):
    """Real-time data streaming model"""
    __tablename__ = "data_streams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stream_code = Column(String(50), unique=True, nullable=False, index=True)
    stream_name = Column(String(200), nullable=False)
    stream_type = Column(String(50), nullable=False)
    
    # Stream configuration
    connection_config = Column(JSONB, nullable=False)
    topic_name = Column(String(200))
    partition_key = Column(String(100))
    
    # Data format
    data_format = Column(String(50))
    schema_definition = Column(JSONB)
    
    # Processing
    processing_mode = Column(String(50))
    batch_size = Column(Integer, default=100)
    batch_timeout_ms = Column(Integer, default=5000)
    
    # Consumers
    consumer_groups = Column(JSONB, default=[])
    consumer_config = Column(JSONB)
    
    # Monitoring
    messages_per_second = Column(Numeric(10, 2))
    total_messages_processed = Column(BigInteger, default=0)
    last_message_at = Column(TIMESTAMP(timezone=True))
    lag_seconds = Column(Integer)
    
    # Error handling
    error_handling_strategy = Column(String(50))
    dead_letter_queue = Column(String(200))
    error_count = Column(Integer, default=0)
    
    status = Column(String(20), default='ACTIVE')
    metadata = Column(JSONB, default={})
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    version = Column(Integer, default=1)


class AnalyticsAlert(BaseModel):
    """Analytics alert configuration model"""
    __tablename__ = "analytics_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_code = Column(String(50), unique=True, nullable=False, index=True)
    alert_name = Column(String(200), nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20))
    
    # Alert configuration
    data_source_id = Column(UUID(as_uuid=True), ForeignKey('data_sources.id'))
    metric_name = Column(String(200))
    condition_config = Column(JSONB, nullable=False)
    
    # Detection settings
    evaluation_frequency_minutes = Column(Integer, default=15)
    lookback_period_minutes = Column(Integer, default=60)
    detection_algorithm = Column(String(50))
    sensitivity = Column(Numeric(3, 2), default=0.95)
    
    # Notification
    notification_channels = Column(JSONB, default=[])
    notification_template = Column(Text)
    recipients = Column(JSONB, default=[])
    
    # State management
    last_evaluated_at = Column(TIMESTAMP(timezone=True))
    next_evaluation_at = Column(TIMESTAMP(timezone=True))
    is_triggered = Column(Boolean, default=False)
    last_triggered_at = Column(TIMESTAMP(timezone=True))
    trigger_count = Column(Integer, default=0)
    
    # Suppression
    suppression_enabled = Column(Boolean, default=False)
    suppression_duration_minutes = Column(Integer)
    suppressed_until = Column(TIMESTAMP(timezone=True))
    
    status = Column(String(20), default='ACTIVE')
    metadata = Column(JSONB, default={})
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    version = Column(Integer, default=1)
    
    # Relationships
    data_source = relationship("DataSource", back_populates="alerts")
    notifications = relationship("AlertNotification", back_populates="alert", cascade="all, delete-orphan")


class AlertNotification(BaseModel):
    """Alert notification history model"""
    __tablename__ = "alert_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_code = Column(String(50), unique=True, nullable=False, index=True)
    alert_id = Column(UUID(as_uuid=True), ForeignKey('analytics_alerts.id', ondelete='CASCADE'))
    
    # Notification details
    notification_type = Column(String(50))
    recipient = Column(String(200))
    subject = Column(String(500))
    message = Column(Text)
    
    # Delivery
    sent_at = Column(TIMESTAMP(timezone=True))
    delivered_at = Column(TIMESTAMP(timezone=True))
    delivery_status = Column(String(20))
    
    # Metrics
    alert_value = Column(JSONB)
    threshold_value = Column(JSONB)
    deviation_percentage = Column(Numeric(10, 2))
    
    # Response tracking
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    acknowledged_at = Column(TIMESTAMP(timezone=True))
    resolution_notes = Column(Text)
    resolved_at = Column(TIMESTAMP(timezone=True))
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    metadata = Column(JSONB, default={})
    
    # Relationships
    alert = relationship("AnalyticsAlert", back_populates="notifications")


class DataQualityRule(BaseModel):
    """Data quality monitoring rule model"""
    __tablename__ = "data_quality_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    rule_name = Column(String(200), nullable=False)
    rule_type = Column(String(50), nullable=False)
    
    # Rule configuration
    data_source_id = Column(UUID(as_uuid=True), ForeignKey('data_sources.id'))
    table_name = Column(String(200))
    column_name = Column(String(200))
    rule_definition = Column(JSONB, nullable=False)
    
    # Validation
    validation_query = Column(Text)
    expected_value = Column(JSONB)
    tolerance = Column(Numeric(5, 4))
    
    # Execution
    execution_frequency_minutes = Column(Integer, default=60)
    last_executed_at = Column(TIMESTAMP(timezone=True))
    next_execution_at = Column(TIMESTAMP(timezone=True))
    
    # Results
    last_result_status = Column(String(20))
    pass_rate = Column(Numeric(5, 2))
    failure_count = Column(Integer, default=0)
    
    # Actions
    on_failure_action = Column(String(50))
    notification_config = Column(JSONB)
    
    status = Column(String(20), default='ACTIVE')
    metadata = Column(JSONB, default={})
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    version = Column(Integer, default=1)
