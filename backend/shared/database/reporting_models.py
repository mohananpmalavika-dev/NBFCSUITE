"""
Reporting & Analytics Data Models
Comprehensive reporting infrastructure for NBFC operations
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text, JSON,
    ForeignKey, Index, DECIMAL, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

from backend.shared.database.models import BaseModel


# ============================================
# ENUMS
# ============================================

class ReportCategory(str, enum.Enum):
    """Report categories"""
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


class ReportFrequency(str, enum.Enum):
    """Report generation frequency"""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"


class ReportStatus(str, enum.Enum):
    """Report generation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DashboardType(str, enum.Enum):
    """Dashboard types"""
    EXECUTIVE = "executive"
    OPERATIONS = "operations"
    RISK = "risk"
    COLLECTION = "collection"
    BRANCH = "branch"
    TREASURY = "treasury"
    HR = "hr"
    CUSTOM = "custom"


class VisualizationType(str, enum.Enum):
    """Chart/visualization types"""
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
# REPORT TEMPLATES
# ============================================

class ReportTemplate(BaseModel):
    """Pre-built report templates (100+ reports)"""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # Template details
    report_code = Column(String(50), unique=True, nullable=False, index=True)
    report_name = Column(String(200), nullable=False)
    report_description = Column(Text)
    category = Column(SQLEnum(ReportCategory), nullable=False)
    sub_category = Column(String(100))
    
    # Report configuration
    query_template = Column(Text, nullable=False)  # SQL query template
    parameters = Column(JSONB)  # Required/optional parameters
    default_filters = Column(JSONB)  # Default filter values
    sort_order = Column(JSONB)  # Default sort configuration
    
    # Display configuration
    columns = Column(JSONB, nullable=False)  # Column definitions
    summary_fields = Column(JSONB)  # Summary/totals configuration
    visualization_config = Column(JSONB)  # Chart configuration
    
    # Scheduling
    frequency = Column(SQLEnum(ReportFrequency), default=ReportFrequency.ON_DEMAND)
    schedule_config = Column(JSONB)  # Cron expression and config
    
    # Access control
    is_public = Column(Boolean, default=False)
    allowed_roles = Column(JSONB)  # List of role IDs
    required_permissions = Column(JSONB)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System template vs custom
    version = Column(String(20), default="1.0")
    
    # Relationships
    generated_reports = relationship("GeneratedReport", back_populates="template")
    scheduled_reports = relationship("ScheduledReport", back_populates="template")
    
    __table_args__ = (
        Index('idx_report_template_category', 'tenant_id', 'category'),
        Index('idx_report_template_active', 'tenant_id', 'is_active'),
    )


class CustomReportBuilder(BaseModel):
    """Custom report builder configurations"""
    __tablename__ = "custom_report_builder"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # Report details
    report_name = Column(String(200), nullable=False)
    report_description = Column(Text)
    category = Column(SQLEnum(ReportCategory))
    
    # Data source
    data_sources = Column(JSONB, nullable=False)  # Tables/views to query
    joins = Column(JSONB)  # Join configurations
    
    # Fields
    selected_fields = Column(JSONB, nullable=False)  # Selected columns
    calculated_fields = Column(JSONB)  # Custom calculated fields
    
    # Filters
    filters = Column(JSONB)  # WHERE conditions
    grouping = Column(JSONB)  # GROUP BY fields
    aggregations = Column(JSONB)  # SUM, AVG, COUNT, etc.
    
    # Display
    sort_order = Column(JSONB)
    limit_rows = Column(Integer)
    visualization_type = Column(SQLEnum(VisualizationType))
    visualization_config = Column(JSONB)
    
    # Ownership
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    shared_with = Column(JSONB)  # List of user IDs
    is_public = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_saved = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_custom_report_tenant', 'tenant_id', 'is_active'),
        Index('idx_custom_report_creator', 'tenant_id', 'created_by'),
    )


# ============================================
# REPORT GENERATION & EXECUTION
# ============================================

class GeneratedReport(BaseModel):
    """Generated report instances"""
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # Report reference
    template_id = Column(Integer, ForeignKey("report_templates.id"))
    custom_report_id = Column(Integer, ForeignKey("custom_report_builder.id"))
    
    # Generation details
    report_name = Column(String(200), nullable=False)
    report_category = Column(SQLEnum(ReportCategory))
    generation_date = Column(DateTime, default=datetime.utcnow)
    
    # Parameters used
    parameters = Column(JSONB)
    filters = Column(JSONB)
    date_range_start = Column(Date)
    date_range_end = Column(Date)
    
    # Results
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    row_count = Column(Integer)
    execution_time_ms = Column(Integer)  # Query execution time
    
    # Output
    result_data = Column(JSONB)  # For small reports
    file_url = Column(String(500))  # For large reports (S3/file storage)
    file_format = Column(String(20))  # pdf, xlsx, csv, json
    file_size_bytes = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    error_details = Column(JSONB)
    
    # Access tracking
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    accessed_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)
    
    # Retention
    expires_at = Column(DateTime)  # Auto-delete after expiry
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="generated_reports")
    
    __table_args__ = (
        Index('idx_generated_report_date', 'tenant_id', 'generation_date'),
        Index('idx_generated_report_status', 'tenant_id', 'status'),
        Index('idx_generated_report_expiry', 'tenant_id', 'expires_at'),
    )


class ScheduledReport(BaseModel):
    """Scheduled report executions"""
    __tablename__ = "scheduled_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # Report configuration
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=False)
    report_name = Column(String(200), nullable=False)
    
    # Schedule
    frequency = Column(SQLEnum(ReportFrequency), nullable=False)
    cron_expression = Column(String(100))  # For custom schedules
    schedule_time = Column(String(10))  # HH:MM format
    schedule_day = Column(Integer)  # Day of week/month
    timezone = Column(String(50), default="UTC")
    
    # Parameters
    parameters = Column(JSONB)
    filters = Column(JSONB)
    
    # Delivery
    delivery_method = Column(JSONB)  # email, sftp, api, etc.
    recipients = Column(JSONB)  # Email addresses or API endpoints
    file_format = Column(String(20), default="pdf")
    
    # Status
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime)
    last_run_status = Column(SQLEnum(ReportStatus))
    next_run_at = Column(DateTime)
    run_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Owner
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="scheduled_reports")
    
    __table_args__ = (
        Index('idx_scheduled_report_next_run', 'tenant_id', 'is_active', 'next_run_at'),
    )


# ============================================
# DASHBOARDS
# ============================================

class Dashboard(BaseModel):
    """Executive dashboards and custom dashboards"""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # Dashboard details
    dashboard_name = Column(String(200), nullable=False)
    dashboard_description = Column(Text)
    dashboard_type = Column(SQLEnum(DashboardType), nullable=False)
    
    # Layout configuration
    layout_config = Column(JSONB)  # Grid layout, responsive config
    theme = Column(String(50), default="default")
    
    # Access control
    is_default = Column(Boolean, default=False)  # Default for role
    is_public = Column(Boolean, default=False)
    allowed_roles = Column(JSONB)
    
    # Owner
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_system = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    # Relationships
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_dashboard_type', 'tenant_id', 'dashboard_type', 'is_active'),
    )


class DashboardWidget(BaseModel):
    """Dashboard widgets/panels"""
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # Widget placement
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    position = Column(JSONB, nullable=False)  # x, y, width, height
    
    # Widget details
    widget_title = Column(String(200), nullable=False)
    widget_type = Column(SQLEnum(VisualizationType), nullable=False)
    
    # Data source
    data_source_type = Column(String(50))  # report, query, api
    report_template_id = Column(Integer, ForeignKey("report_templates.id"))
    custom_query = Column(Text)
    api_endpoint = Column(String(500))
    
    # Data configuration
    parameters = Column(JSONB)
    filters = Column(JSONB)
    refresh_interval_seconds = Column(Integer, default=300)  # 5 minutes
    
    # Visualization config
    visualization_config = Column(JSONB)  # Chart-specific settings
    color_scheme = Column(String(50))
    
    # Display options
    show_legend = Column(Boolean, default=True)
    show_labels = Column(Boolean, default=True)
    show_tooltip = Column(Boolean, default=True)
    
    # Interaction
    drill_down_config = Column(JSONB)  # Drill-down navigation
    click_action = Column(String(50))  # navigate, filter, modal
    
    # Status
    is_active = Column(Boolean, default=True)
    last_updated_at = Column(DateTime)
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")
    
    __table_args__ = (
        Index('idx_widget_dashboard', 'dashboard_id', 'is_active'),
    )


# ============================================
# PREDICTIVE ANALYTICS
# ============================================

class PredictiveModel(BaseModel):
    """Machine learning models for predictive analytics"""
    __tablename__ = "predictive_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # Model details
    model_name = Column(String(200), nullable=False)
    model_description = Column(Text)
    model_type = Column(String(100))  # classification, regression, clustering, etc.
    use_case = Column(String(100))  # credit_risk, churn, default, fraud, etc.
    
    # Model configuration
    algorithm = Column(String(100))  # random_forest, xgboost, neural_network, etc.
    features = Column(JSONB, nullable=False)  # Input features
    target_variable = Column(String(100))  # Output variable
    
    # Training
    training_data_query = Column(Text)
    training_date = Column(DateTime)
    training_records = Column(Integer)
    training_duration_seconds = Column(Integer)
    
    # Performance metrics
    accuracy = Column(DECIMAL(5, 4))
    precision_score = Column(DECIMAL(5, 4))
    recall = Column(DECIMAL(5, 4))
    f1_score = Column(DECIMAL(5, 4))
    roc_auc = Column(DECIMAL(5, 4))
    rmse = Column(DECIMAL(10, 4))
    mae = Column(DECIMAL(10, 4))
    r_squared = Column(DECIMAL(5, 4))
    
    # Model storage
    model_file_url = Column(String(500))  # S3/file storage
    model_version = Column(String(50))
    framework = Column(String(50))  # scikit-learn, tensorflow, pytorch
    
    # Deployment
    is_deployed = Column(Boolean, default=False)
    deployment_date = Column(DateTime)
    api_endpoint = Column(String(500))
    
    # Monitoring
    prediction_count = Column(Integer, default=0)
    last_prediction_at = Column(DateTime)
    average_prediction_time_ms = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=True)
    needs_retraining = Column(Boolean, default=False)
    next_training_date = Column(Date)
    
    # Relationships
    predictions = relationship("ModelPrediction", back_populates="model")
    
    __table_args__ = (
        Index('idx_predictive_model_type', 'tenant_id', 'model_type', 'is_active'),
    )


class ModelPrediction(BaseModel):
    """Prediction results from ML models"""
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # Prediction reference
    model_id = Column(Integer, ForeignKey("predictive_models.id"), nullable=False)
    entity_type = Column(String(50))  # customer, loan, application, etc.
    entity_id = Column(String(100))
    
    # Input
    input_features = Column(JSONB, nullable=False)
    prediction_date = Column(DateTime, default=datetime.utcnow)
    
    # Output
    predicted_value = Column(DECIMAL(15, 4))
    predicted_class = Column(String(100))
    probability = Column(DECIMAL(5, 4))  # Confidence score
    confidence_interval = Column(JSONB)  # Lower and upper bounds
    
    # Explanation
    feature_importance = Column(JSONB)  # SHAP values or similar
    explanation = Column(Text)
    
    # Validation
    actual_value = Column(DECIMAL(15, 4))  # For model accuracy tracking
    actual_class = Column(String(100))
    is_correct = Column(Boolean)
    
    # Performance
    prediction_time_ms = Column(Integer)
    
    # Relationships
    model = relationship("PredictiveModel", back_populates="predictions")
    
    __table_args__ = (
        Index('idx_prediction_model', 'tenant_id', 'model_id', 'prediction_date'),
        Index('idx_prediction_entity', 'tenant_id', 'entity_type', 'entity_id'),
    )


# ============================================
# REPORT ANALYTICS & METRICS
# ============================================

class ReportAnalytics(BaseModel):
    """Track report usage and performance"""
    __tablename__ = "report_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    
    # Report reference
    template_id = Column(Integer, ForeignKey("report_templates.id"))
    custom_report_id = Column(Integer, ForeignKey("custom_report_builder.id"))
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"))
    
    # Usage metrics
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    
    # Performance metrics
    avg_execution_time_ms = Column(Integer)
    min_execution_time_ms = Column(Integer)
    max_execution_time_ms = Column(Integer)
    avg_row_count = Column(Integer)
    
    # Access metrics
    unique_users = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    
    # Time period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Last updated
    last_calculated_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_report_analytics_period', 'tenant_id', 'period_start', 'period_end'),
    )


class UserReportPreference(BaseModel):
    """User-specific report preferences"""
    __tablename__ = "user_report_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Preferences
    favorite_reports = Column(JSONB)  # List of report IDs
    favorite_dashboards = Column(JSONB)  # List of dashboard IDs
    default_dashboard_id = Column(Integer, ForeignKey("dashboards.id"))
    
    # Default settings
    default_file_format = Column(String(20), default="pdf")
    default_date_range = Column(String(50), default="last_30_days")
    
    # Display preferences
    items_per_page = Column(Integer, default=50)
    theme = Column(String(50), default="light")
    
    # Notification preferences
    notify_on_completion = Column(Boolean, default=True)
    notify_on_failure = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_user_preference', 'tenant_id', 'user_id', unique=True),
    )
