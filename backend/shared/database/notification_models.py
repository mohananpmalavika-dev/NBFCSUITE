"""
Notification System Models

Models for managing automated notifications including:
- Notification Templates
- Notification Logs (tracking sent notifications)
- Notification Preferences
- Notification Schedules
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base
import enum


class NotificationType(str, enum.Enum):
    """Notification type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationChannel(str, enum.Enum):
    """Notification channel enumeration"""
    RENT_DUE_REMINDER = "rent_due_reminder"
    LEASE_EXPIRY_ALERT = "lease_expiry_alert"
    PAYMENT_RECEIVED = "payment_received"
    MAINTENANCE_UPDATE = "maintenance_update"
    UTILITY_BILL_DUE = "utility_bill_due"
    PAYMENT_OVERDUE = "payment_overdue"
    LEASE_RENEWAL_REMINDER = "lease_renewal_reminder"


class NotificationStatus(str, enum.Enum):
    """Notification status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"


class NotificationTemplate(Base):
    """
    Notification Template
    
    Predefined templates for various notification types with placeholders
    for dynamic content substitution.
    """
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Template Identification
    template_code = Column(String(100), unique=True, nullable=False, index=True)
    template_name = Column(String(200), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False, index=True)
    notification_type = Column(Enum(NotificationType), nullable=False)
    
    # Template Content
    subject = Column(String(500))  # For email
    body_template = Column(Text, nullable=False)  # Template with placeholders
    sms_template = Column(Text)  # SMS specific template (shorter)
    
    # Template Variables
    available_variables = Column(JSON)  # List of available variables for substitution
    # Example: ["tenant_name", "property_name", "due_date", "amount"]
    
    # Configuration
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Scheduling
    send_days_before = Column(Integer)  # Days before event to send notification
    send_at_time = Column(String(10))  # Time to send (HH:MM format)
    
    # Additional Settings
    cc_emails = Column(JSON)  # Additional CC recipients
    bcc_emails = Column(JSON)  # BCC recipients
    attachments = Column(JSON)  # Attachment references
    
    # Branding
    email_header_image = Column(String(500))
    email_footer_text = Column(Text)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    notification_logs = relationship("NotificationLog", back_populates="template", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<NotificationTemplate {self.template_code} - {self.channel}>"


class NotificationLog(Base):
    """
    Notification Log
    
    Tracks all notifications sent by the system including delivery status,
    timestamps, and recipient details.
    """
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Notification Details
    template_id = Column(Integer, ForeignKey("notification_templates.id"), index=True)
    channel = Column(Enum(NotificationChannel), nullable=False, index=True)
    notification_type = Column(Enum(NotificationType), nullable=False, index=True)
    
    # Recipient Details
    recipient_type = Column(String(50))  # tenant, property_manager, admin
    recipient_id = Column(String(100))  # Customer ID, User ID, etc.
    recipient_name = Column(String(200))
    recipient_email = Column(String(200))
    recipient_phone = Column(String(20))
    
    # Content
    subject = Column(String(500))
    body = Column(Text)
    sms_content = Column(Text)
    
    # Related Records
    property_id = Column(Integer, ForeignKey("properties.id"))
    lease_id = Column(Integer, ForeignKey("leases.id"))
    rent_payment_id = Column(Integer, ForeignKey("rent_payments.id"))
    maintenance_id = Column(Integer, ForeignKey("property_maintenance.id"))
    
    # Delivery Status
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    sent_at = Column(DateTime, index=True)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    failed_at = Column(DateTime)
    
    # Error Handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime)
    
    # External References
    external_message_id = Column(String(200))  # ID from email/SMS provider
    provider_name = Column(String(100))  # SendGrid, Twilio, etc.
    
    # Tracking
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    
    # Additional Data
    additional_data = Column(JSON)  # Additional context data (renamed from metadata to avoid SQLAlchemy conflict)
    variables_used = Column(JSON)  # Variable values used in template
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    template = relationship("NotificationTemplate", back_populates="notification_logs")
    
    def __repr__(self):
        return f"<NotificationLog {self.id} - {self.channel} - {self.status}>"


class NotificationPreference(Base):
    """
    Notification Preferences
    
    User/Tenant preferences for receiving notifications. Allows users to
    opt-in/opt-out of specific notification types.
    """
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Preference Owner
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), index=True)
    
    # Preferences by Channel
    rent_due_reminder_enabled = Column(Boolean, default=True)
    lease_expiry_alert_enabled = Column(Boolean, default=True)
    payment_received_enabled = Column(Boolean, default=True)
    maintenance_update_enabled = Column(Boolean, default=True)
    utility_bill_due_enabled = Column(Boolean, default=True)
    payment_overdue_enabled = Column(Boolean, default=True)
    lease_renewal_reminder_enabled = Column(Boolean, default=True)
    
    # Channel Preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=False)
    in_app_enabled = Column(Boolean, default=True)
    
    # Timing Preferences
    preferred_notification_time = Column(String(10))  # HH:MM format
    timezone = Column(String(50), default="UTC")
    
    # Email Preferences
    email_address = Column(String(200))
    alternate_email = Column(String(200))
    
    # SMS Preferences
    phone_number = Column(String(20))
    alternate_phone = Column(String(20))
    
    # Frequency Control
    daily_digest_enabled = Column(Boolean, default=False)
    weekly_summary_enabled = Column(Boolean, default=False)
    
    # Do Not Disturb
    dnd_enabled = Column(Boolean, default=False)
    dnd_start_time = Column(String(10))  # HH:MM
    dnd_end_time = Column(String(10))  # HH:MM
    
    # Language
    preferred_language = Column(String(10), default="en")
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, index=True)
    
    def __repr__(self):
        return f"<NotificationPreference user:{self.user_id}>"


class NotificationSchedule(Base):
    """
    Notification Schedule
    
    Defines when automated notifications should be triggered.
    Used by scheduler jobs to determine which notifications to send.
    """
    __tablename__ = "notification_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Schedule Identification
    schedule_name = Column(String(200), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False, index=True)
    
    # Schedule Configuration
    is_active = Column(Boolean, default=True, index=True)
    frequency = Column(String(50), nullable=False)  # daily, weekly, monthly, once
    # Options: daily, weekly, monthly, once, cron
    
    # Timing
    run_at_time = Column(String(10))  # HH:MM format
    days_before_event = Column(Integer)  # For reminder notifications
    
    # Cron Expression (for advanced scheduling)
    cron_expression = Column(String(100))
    
    # Target Filters
    property_ids = Column(JSON)  # Specific properties (empty = all)
    lease_status = Column(JSON)  # Filter by lease status
    
    # Last Execution
    last_run_at = Column(DateTime, index=True)
    last_run_status = Column(String(50))  # success, failed
    last_run_count = Column(Integer)  # Number of notifications sent
    last_run_error = Column(Text)
    
    # Next Execution
    next_run_at = Column(DateTime, index=True)
    
    # Statistics
    total_runs = Column(Integer, default=0)
    total_notifications_sent = Column(Integer, default=0)
    total_failures = Column(Integer, default=0)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    def __repr__(self):
        return f"<NotificationSchedule {self.schedule_name} - {self.channel}>"


class NotificationQueue(Base):
    """
    Notification Queue
    
    Queue for pending notifications to be processed by background workers.
    Enables bulk processing and rate limiting.
    """
    __tablename__ = "notification_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Queue Details
    notification_log_id = Column(Integer, ForeignKey("notification_logs.id"), index=True)
    priority = Column(Integer, default=5, index=True)  # 1=highest, 10=lowest
    
    # Status
    status = Column(String(50), default="queued", index=True)
    # Status: queued, processing, completed, failed
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=False, index=True)
    processed_at = Column(DateTime)
    
    # Processing
    worker_id = Column(String(100))
    attempts = Column(Integer, default=0)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    def __repr__(self):
        return f"<NotificationQueue {self.id} - {self.status}>"



class Notification(Base):
    """
    Notification Model (Alias for Notification Log for backward compatibility)
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Notification Details
    template_id = Column(Integer, ForeignKey("notification_templates.id"), index=True, nullable=True)
    channel = Column(Enum(NotificationChannel), nullable=True, index=True)
    notification_type = Column(Enum(NotificationType), nullable=False, index=True)
    
    # Recipient Details
    recipient_id = Column(String(100))
    recipient_email = Column(String(200))
    recipient_phone = Column(String(20))
    
    # Content
    subject = Column(String(500))
    body = Column(Text)
    
    # Status
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    sent_at = Column(DateTime, index=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.notification_type}>"


class NotificationAnalytics(Base):
    """Notification Analytics for tracking delivery metrics"""
    __tablename__ = "notification_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    date = Column(DateTime, nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), index=True)
    notification_type = Column(Enum(NotificationType), index=True)
    
    # Metrics
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<NotificationAnalytics {self.date}>"


class NotificationProvider(Base):
    """Notification Provider Configuration"""
    __tablename__ = "notification_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    provider_name = Column(String(100), nullable=False)
    provider_type = Column(Enum(NotificationType), nullable=False)
    api_key = Column(Text)
    api_secret = Column(Text)
    configuration = Column(JSON)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<NotificationProvider {self.provider_name}>"


class NotificationProviderLog(Base):
    """Notification Provider API Call Logs"""
    __tablename__ = "notification_provider_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    provider_id = Column(Integer, ForeignKey("notification_providers.id"))
    notification_log_id = Column(Integer, ForeignKey("notification_logs.id"))
    
    request_data = Column(JSON)
    response_data = Column(JSON)
    status_code = Column(Integer)
    is_success = Column(Boolean)
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<NotificationProviderLog {self.id}>"


class NotificationDeliveryReport(Base):
    """Notification Delivery Report from providers"""
    __tablename__ = "notification_delivery_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    notification_log_id = Column(Integer, ForeignKey("notification_logs.id"))
    external_message_id = Column(String(200))
    
    delivery_status = Column(String(50))
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    bounced_at = Column(DateTime)
    
    provider_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<NotificationDeliveryReport {self.id}>"


class NotificationTrigger(Base):
    """Notification Trigger Configuration"""
    __tablename__ = "notification_triggers"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    trigger_name = Column(String(200), nullable=False)
    trigger_event = Column(String(100), nullable=False)
    template_id = Column(Integer, ForeignKey("notification_templates.id"))
    
    is_active = Column(Boolean, default=True)
    conditions = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<NotificationTrigger {self.trigger_name}>"



class DLTEntity(Base):
    """DLT Entity Registration"""
    __tablename__ = "dlt_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    entity_id = Column(String(100), unique=True, nullable=False)
    entity_name = Column(String(200), nullable=False)
    telecom_operator = Column(String(100))
    registration_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DLTEntity {self.entity_name}>"


class DLTTemplate(Base):
    """DLT Template Registration"""
    __tablename__ = "dlt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    template_id = Column(String(100), unique=True, nullable=False)
    template_content = Column(Text, nullable=False)
    template_type = Column(String(50))
    entity_id = Column(Integer, ForeignKey("dlt_entities.id"))
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DLTTemplate {self.template_id}>"


class DLTConsent(Base):
    """DLT Consent Records"""
    __tablename__ = "dlt_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    phone_number = Column(String(20), nullable=False)
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime)
    consent_source = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DLTConsent {self.phone_number}>"
