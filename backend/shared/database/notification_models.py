"""
Notification Service Database Models

Models for multi-channel notifications (SMS/Email/WhatsApp),
template management, delivery tracking, and analytics.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, Numeric, JSON, Index
from sqlalchemy.sql import func
from datetime import datetime
from backend.shared.database.connection import Base


class NotificationTemplate(Base):
    """
    Notification templates for reusable content.
    Supports variable substitution for dynamic content.
    """
    __tablename__ = "notification_templates"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_code = Column(String(50), unique=True, nullable=False, index=True)

    # Template Details
    template_name = Column(String(200), nullable=False)
    channel = Column(String(20), nullable=False, index=True)
    # Channels: sms, email, whatsapp
    category = Column(String(50), nullable=False, index=True)
    # Categories: transactional, marketing, otp, alert

    # Content
    subject = Column(String(500), nullable=True)  # For email
    body_template = Column(Text, nullable=False)
    # Template with {{variables}}, e.g., "Dear {{customer_name}}, your loan..."

    # Variables
    variables = Column(JSON, nullable=True)
    # List of allowed variables: ["customer_name", "loan_amount", "due_date"]
    example_data = Column(JSON, nullable=True)
    # Example variable values for testing

    # Configuration
    priority = Column(String(20), default="medium")  # high, medium, low
    retry_enabled = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    retry_interval_seconds = Column(Integer, default=300)  # 5 minutes

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_notification_templates_channel_active', 'channel', 'is_active'),
        Index('idx_notification_templates_tenant_active', 'tenant_id', 'is_active'),
    )


class Notification(Base):
    """
    Individual notification records.
    Tracks complete lifecycle from creation to delivery.
    """
    __tablename__ = "notifications"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    notification_number = Column(String(50), unique=True, nullable=False, index=True)

    # Template Reference
    template_id = Column(Integer, nullable=True, index=True)
    template_code = Column(String(50), nullable=True)

    # Channel & Priority
    channel = Column(String(20), nullable=False, index=True)  # sms, email, whatsapp
    priority = Column(String(20), default="medium", index=True)  # high, medium, low

    # Recipient Information
    recipient_type = Column(String(50), nullable=False)  # customer, user, admin
    recipient_id = Column(Integer, nullable=False, index=True)
    recipient_contact = Column(String(200), nullable=False)  # Phone number or email
    recipient_name = Column(String(200), nullable=True)

    # Content
    subject = Column(String(500), nullable=True)  # For email
    body = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # Actual values used in rendering

    # Entity Reference (for context)
    entity_type = Column(String(50), nullable=True)  # loan, customer, payment, etc.
    entity_id = Column(Integer, nullable=True)

    # Scheduling
    scheduled_at = Column(DateTime, nullable=True, index=True)
    # If NULL, send immediately
    sent_at = Column(DateTime, nullable=True)

    # Status
    status = Column(String(50), default="pending", index=True)
    # pending, queued, sending, sent, failed, cancelled

    # Delivery Tracking
    delivery_status = Column(String(50), nullable=True)
    # delivered, failed, bounced, undelivered, pending
    delivery_time = Column(DateTime, nullable=True)

    # Provider Details
    provider = Column(String(50), nullable=True)  # twilio, sendgrid, whatsapp_business
    provider_message_id = Column(String(200), nullable=True, index=True)
    provider_response = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Retry Mechanism
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime, nullable=True)
    next_retry_at = Column(DateTime, nullable=True, index=True)
    max_retries = Column(Integer, default=3)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_notifications_status_priority', 'status', 'priority'),
        Index('idx_notifications_recipient', 'recipient_type', 'recipient_id'),
        Index('idx_notifications_entity', 'entity_type', 'entity_id'),
        Index('idx_notifications_created_at', 'created_at'),
    )


class NotificationQueue(Base):
    """
    Queue for batch processing of notifications.
    Priority-based processing with FIFO within priority.
    """
    __tablename__ = "notification_queue"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Notification Reference
    notification_id = Column(Integer, nullable=False, index=True)

    # Queue Details
    priority = Column(String(20), nullable=False, index=True)  # high, medium, low
    queue_time = Column(DateTime, default=func.now(), nullable=False, index=True)

    # Processing Status
    status = Column(String(50), default="queued", index=True)
    # queued, processing, processed, failed
    processing_started_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)

    # Worker Info
    worker_id = Column(String(50), nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_notification_queue_status_priority', 'status', 'priority', 'queue_time'),
    )


class NotificationLog(Base):
    """
    Detailed event logs for notifications.
    Provides complete audit trail for troubleshooting.
    """
    __tablename__ = "notification_logs"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Notification Reference
    notification_id = Column(Integer, nullable=False, index=True)

    # Log Details
    event_type = Column(String(50), nullable=False, index=True)
    # created, queued, sending, sent, delivered, failed, retry, cancelled
    event_time = Column(DateTime, default=func.now(), nullable=False)

    # Event Details
    message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    # Additional context like provider response, error details, etc.

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)


class NotificationAnalytics(Base):
    """
    Aggregated analytics for notification performance.
    Time-series data for monitoring and reporting.
    """
    __tablename__ = "notification_analytics"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Time Period
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=True)  # 0-23 for hourly metrics

    # Breakdown Dimensions
    channel = Column(String(20), nullable=False, index=True)
    category = Column(String(50), nullable=True)
    priority = Column(String(20), nullable=True)

    # Volume Metrics
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_bounced = Column(Integer, default=0)
    total_pending = Column(Integer, default=0)

    # Rate Metrics
    delivery_rate = Column(Numeric(5, 2), default=0)  # Percentage
    failure_rate = Column(Numeric(5, 2), default=0)  # Percentage

    # Performance Metrics
    avg_delivery_time_seconds = Column(Integer, default=0)
    min_delivery_time_seconds = Column(Integer, nullable=True)
    max_delivery_time_seconds = Column(Integer, nullable=True)

    # Retry Metrics
    total_retries = Column(Integer, default=0)
    retry_success_count = Column(Integer, default=0)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_notification_analytics_date_channel', 'date', 'channel'),
        Index('idx_notification_analytics_tenant_date', 'tenant_id', 'date'),
    )

