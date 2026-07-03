"""
Reporting and Analytics Models
Phase 9: Reporting & Analytics
"""
from sqlalchemy import (
    Column, BigInteger, String, Text, Boolean, Integer, 
    Date, Time, DateTime, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class ReportDefinition(Base):
    """Report definition and configuration"""
    __tablename__ = "report_definitions"

    id = Column(BigInteger, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False, index=True)  # financial, operational, regulatory
    report_type = Column(String(50), nullable=False, index=True)  # standard, custom, ad_hoc
    data_source = Column(String(100))
    query_template = Column(Text)
    output_formats = Column(JSONB, default=["pdf", "excel", "csv"])
    parameters = Column(JSONB)
    filters = Column(JSONB)
    columns = Column(JSONB)
    sorting = Column(JSONB)
    grouping = Column(JSONB)
    aggregations = Column(JSONB)
    styling = Column(JSONB)
    access_roles = Column(JSONB)
    is_active = Column(Boolean, default=True, index=True)
    is_system = Column(Boolean, default=False)
    created_by = Column(BigInteger, ForeignKey("users.id"))
    updated_by = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

    # Relationships
    templates = relationship("ReportTemplate", back_populates="report_definition", cascade="all, delete-orphan")
    schedules = relationship("ReportSchedule", back_populates="report_definition", cascade="all, delete-orphan")
    executions = relationship("ReportExecution", back_populates="report_definition", cascade="all, delete-orphan")
    report_parameters = relationship("ReportParameter", back_populates="report_definition", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            category.in_(['financial', 'operational', 'regulatory', 'custom', 'compliance', 'audit']),
            name='chk_report_category'
        ),
        CheckConstraint(
            report_type.in_(['standard', 'custom', 'ad_hoc', 'regulatory', 'statutory']),
            name='chk_report_type'
        ),
    )


class ReportTemplate(Base):
    """Report templates for different output formats"""
    __tablename__ = "report_templates"

    id = Column(BigInteger, primary_key=True, index=True)
    report_definition_id = Column(BigInteger, ForeignKey("report_definitions.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    template_type = Column(String(50), nullable=False, index=True)  # pdf, excel, html
    template_content = Column(Text)
    header_content = Column(Text)
    footer_content = Column(Text)
    styles = Column(Text)
    page_size = Column(String(20), default='A4')
    orientation = Column(String(20), default='portrait')
    margins = Column(JSONB)
    fonts = Column(JSONB)
    colors = Column(JSONB)
    logo_url = Column(String(500))
    watermark = Column(Text)
    is_default = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

    # Relationships
    report_definition = relationship("ReportDefinition", back_populates="templates")
    schedules = relationship("ReportSchedule", back_populates="template")
    executions = relationship("ReportExecution", back_populates="template")

    __table_args__ = (
        CheckConstraint(
            template_type.in_(['pdf', 'excel', 'html', 'email', 'csv', 'json']),
            name='chk_template_type'
        ),
        CheckConstraint(
            page_size.in_(['A4', 'A3', 'Letter', 'Legal', 'Tabloid']),
            name='chk_page_size'
        ),
        CheckConstraint(
            orientation.in_(['portrait', 'landscape']),
            name='chk_orientation'
        ),
    )


class ReportSchedule(Base):
    """Scheduled report execution configurations"""
    __tablename__ = "report_schedules"

    id = Column(BigInteger, primary_key=True, index=True)
    report_definition_id = Column(BigInteger, ForeignKey("report_definitions.id"), nullable=False, index=True)
    template_id = Column(BigInteger, ForeignKey("report_templates.id"), index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    schedule_type = Column(String(50), nullable=False)  # daily, weekly, monthly
    frequency = Column(String(100))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    execution_time = Column(Time, default='00:00:00')
    timezone = Column(String(50), default='UTC')
    parameters = Column(JSONB)
    output_format = Column(String(20), default='pdf')
    delivery_method = Column(String(50))
    delivery_config = Column(JSONB)
    recipients = Column(JSONB)
    status = Column(String(20), default='active', index=True)
    last_execution_at = Column(DateTime)
    next_execution_at = Column(DateTime, index=True)
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(BigInteger, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

    # Relationships
    report_definition = relationship("ReportDefinition", back_populates="schedules")
    template = relationship("ReportTemplate", back_populates="schedules")
    executions = relationship("ReportExecution", back_populates="schedule")

    __table_args__ = (
        CheckConstraint(
            schedule_type.in_(['daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'cron', 'on_demand']),
            name='chk_schedule_type'
        ),
        CheckConstraint(
            status.in_(['active', 'paused', 'completed', 'failed', 'disabled']),
            name='chk_schedule_status'
        ),
    )


class ReportExecution(Base):
    """Report execution history and results"""
    __tablename__ = "report_executions"

    id = Column(BigInteger, primary_key=True, index=True)
    report_definition_id = Column(BigInteger, ForeignKey("report_definitions.id"), nullable=False, index=True)
    schedule_id = Column(BigInteger, ForeignKey("report_schedules.id"), index=True)
    template_id = Column(BigInteger, ForeignKey("report_templates.id"), index=True)
    execution_type = Column(String(50), nullable=False)  # scheduled, manual, api
    parameters = Column(JSONB)
    filters = Column(JSONB)
    status = Column(String(20), default='pending', index=True)
    output_format = Column(String(20))
    file_path = Column(String(500))
    file_size = Column(BigInteger)
    file_url = Column(String(500))
    started_at = Column(DateTime)
    completed_at = Column(DateTime, index=True)
    duration_seconds = Column(Integer)
    rows_processed = Column(Integer)
    error_message = Column(Text)
    error_details = Column(JSONB)
    executed_by = Column(BigInteger, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSONB)

    # Relationships
    report_definition = relationship("ReportDefinition", back_populates="executions")
    schedule = relationship("ReportSchedule", back_populates="executions")
    template = relationship("ReportTemplate", back_populates="executions")
    exports = relationship("ReportExport", back_populates="execution", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            execution_type.in_(['scheduled', 'manual', 'api', 'batch']),
            name='chk_execution_type'
        ),
        CheckConstraint(
            status.in_(['pending', 'running', 'completed', 'failed', 'cancelled', 'timeout']),
            name='chk_execution_status'
        ),
    )


class ReportParameter(Base):
    """Report parameter definitions"""
    __tablename__ = "report_parameters"

    id = Column(BigInteger, primary_key=True, index=True)
    report_definition_id = Column(BigInteger, ForeignKey("report_definitions.id"), nullable=False, index=True)
    parameter_name = Column(String(100), nullable=False, index=True)
    parameter_label = Column(String(200), nullable=False)
    parameter_type = Column(String(50), nullable=False)  # string, number, date, select
    data_type = Column(String(50))
    default_value = Column(Text)
    is_required = Column(Boolean, default=False)
    validation_rules = Column(JSONB)
    options = Column(JSONB)
    options_query = Column(Text)
    depends_on = Column(String(100))
    display_order = Column(Integer, default=0, index=True)
    help_text = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

    # Relationships
    report_definition = relationship("ReportDefinition", back_populates="report_parameters")

    __table_args__ = (
        CheckConstraint(
            parameter_type.in_(['string', 'number', 'date', 'daterange', 'datetime', 'select', 'multiselect', 'boolean', 'autocomplete']),
            name='chk_parameter_type'
        ),
        UniqueConstraint('report_definition_id', 'parameter_name', name='uq_report_parameter'),
    )


class ReportExport(Base):
    """Generated report files and exports"""
    __tablename__ = "report_exports"

    id = Column(BigInteger, primary_key=True, index=True)
    execution_id = Column(BigInteger, ForeignKey("report_executions.id"), nullable=False, index=True)
    export_format = Column(String(20), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size = Column(BigInteger)
    file_url = Column(String(500))
    download_count = Column(Integer, default=0)
    last_downloaded_at = Column(DateTime)
    expires_at = Column(DateTime, index=True)
    is_public = Column(Boolean, default=False)
    access_token = Column(String(255), index=True)
    status = Column(String(20), default='available', index=True)
    created_by = Column(BigInteger, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB)

    # Relationships
    execution = relationship("ReportExecution", back_populates="exports")

    __table_args__ = (
        CheckConstraint(
            export_format.in_(['pdf', 'excel', 'csv', 'json', 'xml', 'html']),
            name='chk_export_format'
        ),
        CheckConstraint(
            status.in_(['available', 'expired', 'deleted', 'processing']),
            name='chk_export_status'
        ),
    )




class DashboardDefinition(Base):
    """Dashboard layout and configuration"""
    __tablename__ = "dashboard_definitions"

    id = Column(BigInteger, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    dashboard_type = Column(String(50), nullable=False, index=True)  # executive, operational, analytical
    category = Column(String(50), index=True)
    layout = Column(JSONB)
    theme = Column(JSONB)
    refresh_interval = Column(Integer)
    access_roles = Column(JSONB)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0, index=True)
    created_by = Column(BigInteger, ForeignKey("users.id"))
    updated_by = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

    # Relationships
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            dashboard_type.in_(['executive', 'operational', 'analytical', 'custom', 'realtime']),
            name='chk_dashboard_type'
        ),
    )


class DashboardWidget(Base):
    """Dashboard widget definitions"""
    __tablename__ = "dashboard_widgets"

    id = Column(BigInteger, primary_key=True, index=True)
    dashboard_id = Column(BigInteger, ForeignKey("dashboard_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    widget_type = Column(String(50), nullable=False, index=True)  # chart, table, metric
    chart_type = Column(String(50))  # line, bar, pie, area
    title = Column(String(200), nullable=False)
    description = Column(Text)
    data_source = Column(String(100))
    query = Column(Text)
    parameters = Column(JSONB)
    filters = Column(JSONB)
    position = Column(JSONB, nullable=False)  # {x, y, width, height}
    styling = Column(JSONB)
    refresh_interval = Column(Integer)
    drill_down = Column(JSONB)
    is_visible = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

    # Relationships
    dashboard = relationship("DashboardDefinition", back_populates="widgets")

    __table_args__ = (
        CheckConstraint(
            widget_type.in_(['chart', 'table', 'metric', 'gauge', 'map', 'list', 'kpi', 'sparkline', 'progress']),
            name='chk_widget_type'
        ),
    )


class DataSnapshot(Base):
    """Point-in-time data snapshots for historical analysis"""
    __tablename__ = "data_snapshots"

    id = Column(BigInteger, primary_key=True, index=True)
    snapshot_type = Column(String(50), nullable=False, index=True)  # daily, weekly, monthly
    snapshot_date = Column(Date, nullable=False, index=True)
    snapshot_period = Column(String(50), index=True)  # Q1-2026, 2026-01
    entity_type = Column(String(50), nullable=False, index=True)  # portfolio, collections
    metrics = Column(JSONB, nullable=False)
    aggregations = Column(JSONB)
    comparisons = Column(JSONB)
    trends = Column(JSONB)
    status = Column(String(20), default='active', index=True)
    created_by = Column(BigInteger, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB)

    __table_args__ = (
        CheckConstraint(
            snapshot_type.in_(['daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'adhoc']),
            name='chk_snapshot_type'
        ),
        CheckConstraint(
            status.in_(['active', 'archived', 'superseded']),
            name='chk_snapshot_status'
        ),
        UniqueConstraint('snapshot_type', 'snapshot_date', 'entity_type', name='uq_snapshot'),
    )


class AnalyticsMetric(Base):
    """Business metrics and KPI definitions"""
    __tablename__ = "analytics_metrics"

    id = Column(BigInteger, primary_key=True, index=True)
    metric_code = Column(String(100), unique=True, nullable=False, index=True)
    metric_name = Column(String(200), nullable=False)
    metric_category = Column(String(50), nullable=False, index=True)  # portfolio, collection, risk
    metric_type = Column(String(50), nullable=False, index=True)  # count, sum, average, percentage
    description = Column(Text)
    calculation_formula = Column(Text)
    unit = Column(String(50))  # currency, percentage, count
    data_source = Column(String(100))
    aggregation_level = Column(String(50))  # branch, product, customer_segment
    time_granularity = Column(String(50))  # daily, weekly, monthly
    threshold_warning = Column(Numeric(15, 2))
    threshold_critical = Column(Numeric(15, 2))
    target_value = Column(Numeric(15, 2))
    trend_direction = Column(String(20))  # higher_better, lower_better
    is_kpi = Column(Boolean, default=False, index=True)
    display_format = Column(String(50))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB)

    __table_args__ = (
        CheckConstraint(
            metric_category.in_(['portfolio', 'collection', 'risk', 'finance', 'operations', 'compliance', 'customer']),
            name='chk_metric_category'
        ),
        CheckConstraint(
            metric_type.in_(['count', 'sum', 'average', 'percentage', 'ratio', 'rate', 'index']),
            name='chk_metric_type'
        ),
        CheckConstraint(
            trend_direction.in_(['higher_better', 'lower_better', 'neutral']),
            name='chk_trend_direction'
        ),
    )
