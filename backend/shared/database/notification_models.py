"""
Notification & Communication Engine Database Models

Complete multi-channel notification system with:
- SMS, Email, WhatsApp, Push notifications
- TRAI DLT compliance for SMS
- Event-driven triggers
- Template management with versioning
- Delivery tracking and analytics
- Provider integration (Twilio, MSG91, SendGrid, WhatsApp, Firebase)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, Numeric, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
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
    event_metadata = Column(JSON, nullable=True)
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


# ============================================================================
# TRAI DLT COMPLIANCE MODELS
# ============================================================================

class DLTEntity(Base):
    """
    TRAI DLT Entity Registration.
    Principal Entities (PEs) registered with telecom operators.
    """
    __tablename__ = "dlt_entities"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Entity Details
    entity_id = Column(String(50), unique=True, nullable=False, index=True)
    # DLT Entity ID from telecom operator
    entity_name = Column(String(200), nullable=False)
    entity_type = Column(String(50), nullable=False)
    # government, implicit, explicit

    # Registration Details
    telecom_operator = Column(String(50), nullable=False)
    # Airtel, Jio, Vodafone, BSNL
    registration_date = Column(Date, nullable=False)
    entity_status = Column(String(50), default="active", index=True)
    # active, suspended, expired

    # Contact Details
    contact_person = Column(String(200), nullable=True)
    contact_email = Column(String(200), nullable=True)
    contact_phone = Column(String(20), nullable=True)

    # Header/Sender ID
    approved_headers = Column(JSON, nullable=True)
    # List of approved sender IDs: ["NBFCFN", "LOANPL"]

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)


class DLTTemplate(Base):
    """
    TRAI DLT Template Registration.
    Pre-approved SMS content templates.
    """
    __tablename__ = "dlt_templates"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # DLT Details
    dlt_template_id = Column(String(50), unique=True, nullable=False, index=True)
    # Template ID from DLT platform
    dlt_entity_id = Column(Integer, ForeignKey('dlt_entities.id'), nullable=False, index=True)

    # Template Details
    template_name = Column(String(200), nullable=False)
    template_type = Column(String(50), nullable=False)
    # transactional, promotional, service_explicit, service_implicit
    content_template = Column(Text, nullable=False)
    # Registered content with {#var#} placeholders

    # Variables
    variables = Column(JSON, nullable=True)
    # List of variables in template

    # Approval Details
    approval_status = Column(String(50), default="pending", index=True)
    # pending, approved, rejected
    approved_date = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Telecom Operator
    telecom_operator = Column(String(50), nullable=False)

    # Usage Tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Internal Template Link
    notification_template_id = Column(Integer, ForeignKey('notification_templates.id'), nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)

    # Relationships
    dlt_entity = relationship("DLTEntity", backref="templates")


class DLTConsent(Base):
    """
    Customer consent for promotional/marketing SMS.
    Required by TRAI regulations.
    """
    __tablename__ = "dlt_consents"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Customer Details
    customer_id = Column(Integer, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)

    # Consent Details
    consent_type = Column(String(50), nullable=False)
    # promotional, transactional, service_implicit
    consent_status = Column(String(50), default="active", index=True)
    # active, revoked, expired

    # Consent Source
    consent_source = Column(String(100), nullable=False)
    # web_form, mobile_app, call_center, branch
    consent_date = Column(DateTime, nullable=False)
    consent_ip_address = Column(String(50), nullable=True)
    consent_proof = Column(Text, nullable=True)
    # URL to consent form, recording, etc.

    # Revocation Details
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(Integer, nullable=True)
    revocation_reason = Column(Text, nullable=True)

    # Expiry
    expiry_date = Column(Date, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_dlt_consent_customer_type', 'customer_id', 'consent_type'),
        Index('idx_dlt_consent_phone_status', 'phone_number', 'consent_status'),
    )


# ============================================================================
# EVENT-DRIVEN TRIGGER SYSTEM
# ============================================================================

class NotificationTrigger(Base):
    """
    Event-based notification triggers.
    Define when notifications should be automatically sent.
    """
    __tablename__ = "notification_triggers"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Trigger Details
    trigger_code = Column(String(50), unique=True, nullable=False, index=True)
    trigger_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Event Configuration
    event_type = Column(String(100), nullable=False, index=True)
    # loan_approved, payment_due, payment_received, kyc_pending, etc.
    entity_type = Column(String(50), nullable=False)
    # loan, customer, payment, deposit

    # Trigger Conditions
    conditions = Column(JSON, nullable=True)
    # {"status": "approved", "amount_gt": 100000}

    # Template Configuration
    template_id = Column(Integer, ForeignKey('notification_templates.id'), nullable=False)
    channel = Column(String(20), nullable=False)
    priority = Column(String(20), default="medium")

    # Timing
    timing_type = Column(String(50), default="immediate")
    # immediate, scheduled, delayed
    delay_minutes = Column(Integer, default=0)
    # For delayed notifications
    schedule_time = Column(String(20), nullable=True)
    # Time of day: "09:00", "14:30"

    # Recipient Configuration
    recipient_config = Column(JSON, nullable=False)
    # {"type": "customer", "field": "primary_phone"}

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_enabled = Column(Boolean, default=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)

    # Relationships
    template = relationship("NotificationTemplate", backref="triggers")

    # Indexes
    __table_args__ = (
        Index('idx_notification_triggers_event', 'event_type', 'is_active'),
    )


class NotificationSchedule(Base):
    """
    Scheduled notifications for future delivery.
    Supports recurring notifications.
    """
    __tablename__ = "notification_schedules"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Schedule Details
    schedule_name = Column(String(200), nullable=False)
    schedule_type = Column(String(50), nullable=False)
    # one_time, daily, weekly, monthly

    # Template Reference
    template_id = Column(Integer, ForeignKey('notification_templates.id'), nullable=False)
    channel = Column(String(20), nullable=False)

    # Recipients
    recipient_filter = Column(JSON, nullable=False)
    # {"customer_status": "active", "loan_status": "disbursed"}

    # Timing
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    execution_time = Column(String(20), nullable=False)
    # "09:00", "15:30"

    # Recurrence Pattern
    recurrence_pattern = Column(JSON, nullable=True)
    # {"days": [1,2,3,4,5]} for weekdays
    # {"day_of_month": 1} for monthly on 1st

    # Execution Tracking
    last_executed_at = Column(DateTime, nullable=True)
    next_execution_at = Column(DateTime, nullable=True, index=True)
    execution_count = Column(Integer, default=0)

    # Status
    status = Column(String(50), default="active", index=True)
    # active, paused, completed, cancelled
    is_active = Column(Boolean, default=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    template = relationship("NotificationTemplate", backref="schedules")


# ============================================================================
# PROVIDER CONFIGURATION MODELS
# ============================================================================

class NotificationProvider(Base):
    """
    Third-party notification provider configuration.
    Supports multiple providers per channel.
    """
    __tablename__ = "notification_providers"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Provider Details
    provider_code = Column(String(50), unique=True, nullable=False, index=True)
    provider_name = Column(String(200), nullable=False)
    provider_type = Column(String(50), nullable=False)
    # twilio, msg91, sendgrid, aws_ses, whatsapp_business, firebase

    # Channel Support
    supported_channels = Column(JSON, nullable=False)
    # ["sms", "whatsapp"] or ["email"]

    # Configuration
    api_endpoint = Column(String(500), nullable=True)
    api_key = Column(Text, nullable=True)  # Encrypted
    api_secret = Column(Text, nullable=True)  # Encrypted
    additional_config = Column(JSON, nullable=True)
    # Provider-specific settings

    # Rate Limits
    rate_limit_per_second = Column(Integer, default=10)
    rate_limit_per_minute = Column(Integer, default=100)
    rate_limit_per_hour = Column(Integer, default=1000)

    # Priority & Failover
    priority = Column(Integer, default=1)
    # Lower number = higher priority
    is_primary = Column(Boolean, default=True)
    fallback_provider_id = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_enabled = Column(Boolean, default=True)
    health_status = Column(String(50), default="healthy")
    # healthy, degraded, down
    last_health_check = Column(DateTime, nullable=True)

    # Usage Tracking
    total_sent = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)


class NotificationProviderLog(Base):
    """
    Provider-specific delivery logs.
    Tracks API calls and responses.
    """
    __tablename__ = "notification_provider_logs"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # References
    notification_id = Column(Integer, ForeignKey('notifications.id'), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey('notification_providers.id'), nullable=False, index=True)

    # Request Details
    request_time = Column(DateTime, default=func.now(), nullable=False)
    request_payload = Column(JSON, nullable=True)
    request_headers = Column(JSON, nullable=True)

    # Response Details
    response_time = Column(DateTime, nullable=True)
    response_status_code = Column(Integer, nullable=True)
    response_payload = Column(JSON, nullable=True)
    response_headers = Column(JSON, nullable=True)

    # Provider Message ID
    provider_message_id = Column(String(200), nullable=True, index=True)

    # Error Details
    is_success = Column(Boolean, default=False)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Performance
    response_time_ms = Column(Integer, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Relationships
    notification = relationship("Notification", backref="provider_logs")
    provider = relationship("NotificationProvider", backref="logs")


class NotificationDeliveryReport(Base):
    """
    Delivery reports from providers (webhooks/callbacks).
    Real-time delivery status updates.
    """
    __tablename__ = "notification_delivery_reports"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # References
    notification_id = Column(Integer, ForeignKey('notifications.id'), nullable=True, index=True)
    provider_message_id = Column(String(200), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey('notification_providers.id'), nullable=False)

    # Delivery Status
    delivery_status = Column(String(50), nullable=False, index=True)
    # delivered, failed, bounced, rejected, undelivered
    delivery_time = Column(DateTime, nullable=False)

    # Additional Details
    delivery_metadata = Column(JSON, nullable=True)
    # Provider-specific delivery details
    error_code = Column(String(50), nullable=True)
    error_description = Column(Text, nullable=True)

    # Webhook Details
    webhook_received_at = Column(DateTime, default=func.now(), nullable=False)
    webhook_payload = Column(JSON, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Relationships
    notification = relationship("Notification", backref="delivery_reports")
    provider = relationship("NotificationProvider", backref="delivery_reports")

