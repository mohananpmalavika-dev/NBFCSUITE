"""
Notification Service Pydantic Schemas

Request and response schemas for notifications, templates, and analytics.
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ==================== ENUMS ====================

class NotificationChannel(str, Enum):
    """Notification channels"""
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NotificationCategory(str, Enum):
    """Notification categories"""
    TRANSACTIONAL = "transactional"
    MARKETING = "marketing"
    OTP = "otp"
    ALERT = "alert"
    REMINDER = "reminder"


class NotificationStatus(str, Enum):
    """Notification status"""
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeliveryStatus(str, Enum):
    """Delivery status"""
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    UNDELIVERED = "undelivered"
    PENDING = "pending"


class RecipientType(str, Enum):
    """Recipient types"""
    CUSTOMER = "customer"
    USER = "user"
    ADMIN = "admin"


# ==================== TEMPLATE SCHEMAS ====================

class NotificationTemplateCreate(BaseModel):
    """Schema for creating notification template"""
    template_code: str = Field(..., max_length=50, description="Unique template code")
    template_name: str = Field(..., max_length=200, description="Template name")
    channel: NotificationChannel = Field(..., description="Notification channel")
    category: NotificationCategory = Field(..., description="Template category")
    subject: Optional[str] = Field(None, max_length=500, description="Email subject")
    body_template: str = Field(..., description="Template body with {{variables}}")
    variables: Optional[List[str]] = Field(None, description="List of allowed variables")
    example_data: Optional[Dict[str, Any]] = Field(None, description="Example values")
    priority: NotificationPriority = Field(NotificationPriority.MEDIUM)
    retry_enabled: bool = Field(True)
    max_retries: int = Field(3, ge=0, le=10)
    retry_interval_seconds: int = Field(300, ge=60, le=3600)
    is_active: bool = Field(True)


class NotificationTemplateUpdate(BaseModel):
    """Schema for updating template"""
    template_name: Optional[str] = Field(None, max_length=200)
    subject: Optional[str] = Field(None, max_length=500)
    body_template: Optional[str] = None
    variables: Optional[List[str]] = None
    example_data: Optional[Dict[str, Any]] = None
    priority: Optional[NotificationPriority] = None
    retry_enabled: Optional[bool] = None
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_interval_seconds: Optional[int] = Field(None, ge=60, le=3600)
    is_active: Optional[bool] = None


class NotificationTemplateResponse(BaseModel):
    """Response schema for template"""
    id: int
    template_code: str
    template_name: str
    channel: str
    category: str
    subject: Optional[str]
    body_template: str
    variables: Optional[List[str]]
    example_data: Optional[Dict[str, Any]]
    priority: str
    retry_enabled: bool
    max_retries: int
    retry_interval_seconds: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateTestRequest(BaseModel):
    """Request to test a template"""
    template_code: str = Field(..., description="Template code to test")
    variables: Dict[str, Any] = Field(..., description="Variable values")


class TemplateTestResponse(BaseModel):
    """Response for template test"""
    success: bool
    rendered_subject: Optional[str]
    rendered_body: str
    missing_variables: List[str] = []
    errors: List[str] = []


# ==================== NOTIFICATION SCHEMAS ====================

class SendNotificationRequest(BaseModel):
    """Request to send a notification"""
    channel: NotificationChannel = Field(..., description="Notification channel")
    recipient_type: RecipientType = Field(..., description="Recipient type")
    recipient_id: int = Field(..., description="Recipient ID")
    recipient_contact: str = Field(..., description="Phone or email")
    recipient_name: Optional[str] = Field(None, description="Recipient name")
    subject: Optional[str] = Field(None, max_length=500, description="Subject (for email)")
    body: str = Field(..., description="Notification body")
    priority: NotificationPriority = Field(NotificationPriority.MEDIUM)
    entity_type: Optional[str] = Field(None, description="Related entity type")
    entity_id: Optional[int] = Field(None, description="Related entity ID")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule for later")
    
    class Config:
        json_schema_extra = {
            "example": {
                "channel": "sms",
                "recipient_type": "customer",
                "recipient_id": 12345,
                "recipient_contact": "+919876543210",
                "recipient_name": "John Doe",
                "body": "Your loan application has been approved!",
                "priority": "high"
            }
        }


class SendFromTemplateRequest(BaseModel):
    """Request to send using template"""
    template_code: str = Field(..., description="Template code")
    recipient_type: RecipientType = Field(..., description="Recipient type")
    recipient_id: int = Field(..., description="Recipient ID")
    recipient_contact: str = Field(..., description="Phone or email")
    recipient_name: Optional[str] = Field(None, description="Recipient name")
    variables: Dict[str, Any] = Field(..., description="Variable values")
    priority: Optional[NotificationPriority] = Field(None, description="Override priority")
    entity_type: Optional[str] = Field(None, description="Related entity type")
    entity_id: Optional[int] = Field(None, description="Related entity ID")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule for later")


class BulkNotificationRequest(BaseModel):
    """Request to send bulk notifications"""
    template_code: str = Field(..., description="Template code")
    recipients: List[Dict[str, Any]] = Field(..., description="List of recipients with variables")
    priority: Optional[NotificationPriority] = Field(None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_code": "EMI_REMINDER",
                "recipients": [
                    {
                        "recipient_id": 1,
                        "recipient_contact": "+919876543210",
                        "recipient_name": "John Doe",
                        "variables": {"customer_name": "John", "emi_amount": "15000", "due_date": "2026-08-05"}
                    }
                ],
                "priority": "high"
            }
        }


class NotificationResponse(BaseModel):
    """Response schema for notification"""
    id: int
    notification_number: str
    channel: str
    priority: str
    recipient_type: str
    recipient_id: int
    recipient_contact: str
    recipient_name: Optional[str]
    subject: Optional[str]
    body: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    status: str
    delivery_status: Optional[str]
    delivery_time: Optional[datetime]
    retry_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationDetails(NotificationResponse):
    """Extended notification details"""
    template_code: Optional[str]
    variables: Optional[Dict[str, Any]]
    provider: Optional[str]
    provider_message_id: Optional[str]
    error_message: Optional[str]
    last_retry_at: Optional[datetime]
    next_retry_at: Optional[datetime]


# ==================== ANALYTICS SCHEMAS ====================

class NotificationSummary(BaseModel):
    """Summary statistics"""
    total_sent: int
    total_delivered: int
    total_failed: int
    total_pending: int
    delivery_rate: float
    failure_rate: float


class ChannelStatistics(BaseModel):
    """Statistics by channel"""
    channel: str
    total_sent: int
    total_delivered: int
    total_failed: int
    delivery_rate: float
    avg_delivery_time_seconds: int


class DeliveryRateTrend(BaseModel):
    """Delivery rate over time"""
    date: date
    channel: str
    total_sent: int
    delivery_rate: float


class FailedNotification(BaseModel):
    """Failed notification info"""
    id: int
    notification_number: str
    channel: str
    recipient_contact: str
    error_message: Optional[str]
    retry_count: int
    failed_at: datetime


# ==================== FILTER SCHEMAS ====================

class NotificationListFilters(BaseModel):
    """Filters for listing notifications"""
    channel: Optional[NotificationChannel] = None
    status: Optional[NotificationStatus] = None
    recipient_type: Optional[RecipientType] = None
    recipient_id: Optional[int] = None
    priority: Optional[NotificationPriority] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class TemplateListFilters(BaseModel):
    """Filters for listing templates"""
    channel: Optional[NotificationChannel] = None
    category: Optional[NotificationCategory] = None
    is_active: Optional[bool] = True


# ==================== DLT COMPLIANCE SCHEMAS ====================

class DLTEntityType(str, Enum):
    """DLT Entity Types"""
    GOVERNMENT = "government"
    IMPLICIT = "implicit"
    EXPLICIT = "explicit"


class DLTTemplateType(str, Enum):
    """DLT Template Types"""
    TRANSACTIONAL = "transactional"
    PROMOTIONAL = "promotional"
    SERVICE_EXPLICIT = "service_explicit"
    SERVICE_IMPLICIT = "service_implicit"


class DLTEntityCreate(BaseModel):
    """Schema for creating DLT entity"""
    entity_id: str = Field(..., max_length=50, description="DLT Entity ID from operator")
    entity_name: str = Field(..., max_length=200, description="Entity name")
    entity_type: DLTEntityType = Field(..., description="Entity type")
    telecom_operator: str = Field(..., max_length=50, description="Telecom operator")
    registration_date: date = Field(..., description="Registration date")
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    approved_headers: Optional[List[str]] = Field(None, description="Approved sender IDs")


class DLTEntityUpdate(BaseModel):
    """Schema for updating DLT entity"""
    entity_name: Optional[str] = Field(None, max_length=200)
    entity_type: Optional[DLTEntityType] = None
    entity_status: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    approved_headers: Optional[List[str]] = None


class DLTEntityResponse(BaseModel):
    """Response schema for DLT entity"""
    id: int
    entity_id: str
    entity_name: str
    entity_type: str
    telecom_operator: str
    registration_date: date
    entity_status: str
    contact_person: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    approved_headers: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DLTTemplateCreate(BaseModel):
    """Schema for creating DLT template"""
    dlt_template_id: str = Field(..., max_length=50, description="Template ID from DLT")
    dlt_entity_id: int = Field(..., description="DLT Entity reference")
    template_name: str = Field(..., max_length=200, description="Template name")
    template_type: DLTTemplateType = Field(..., description="Template type")
    content_template: str = Field(..., description="Content with {#var#} placeholders")
    variables: Optional[List[str]] = Field(None, description="Variable list")
    telecom_operator: str = Field(..., max_length=50)
    notification_template_id: Optional[int] = Field(None, description="Link to internal template")


class DLTTemplateUpdate(BaseModel):
    """Schema for updating DLT template"""
    template_name: Optional[str] = None
    approval_status: Optional[str] = None
    approved_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    is_active: Optional[bool] = None
    notification_template_id: Optional[int] = None


class DLTTemplateResponse(BaseModel):
    """Response schema for DLT template"""
    id: int
    dlt_template_id: str
    dlt_entity_id: int
    template_name: str
    template_type: str
    content_template: str
    variables: Optional[List[str]]
    approval_status: str
    approved_date: Optional[date]
    rejection_reason: Optional[str]
    telecom_operator: str
    usage_count: int
    last_used_at: Optional[datetime]
    is_active: bool
    notification_template_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DLTConsentType(str, Enum):
    """DLT Consent Types"""
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    SERVICE_IMPLICIT = "service_implicit"


class DLTConsentSource(str, Enum):
    """Consent Sources"""
    WEB_FORM = "web_form"
    MOBILE_APP = "mobile_app"
    CALL_CENTER = "call_center"
    BRANCH = "branch"


class DLTConsentCreate(BaseModel):
    """Schema for recording DLT consent"""
    customer_id: int = Field(..., description="Customer ID")
    phone_number: str = Field(..., max_length=20, description="Phone number")
    consent_type: DLTConsentType = Field(..., description="Consent type")
    consent_source: DLTConsentSource = Field(..., description="Where consent was obtained")
    consent_date: datetime = Field(..., description="Consent timestamp")
    consent_ip_address: Optional[str] = Field(None, max_length=50)
    consent_proof: Optional[str] = Field(None, description="URL or reference to proof")
    expiry_date: Optional[date] = Field(None, description="Consent expiry")


class DLTConsentResponse(BaseModel):
    """Response schema for DLT consent"""
    id: int
    customer_id: int
    phone_number: str
    consent_type: str
    consent_status: str
    consent_source: str
    consent_date: datetime
    consent_ip_address: Optional[str]
    revoked_at: Optional[datetime]
    revocation_reason: Optional[str]
    expiry_date: Optional[date]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DLTConsentRevoke(BaseModel):
    """Schema for revoking consent"""
    revocation_reason: Optional[str] = Field(None, description="Reason for revocation")


class DLTComplianceCheck(BaseModel):
    """Check DLT compliance for sending SMS"""
    customer_id: int
    phone_number: str
    template_code: str


class DLTComplianceResponse(BaseModel):
    """DLT compliance check result"""
    is_compliant: bool
    has_consent: bool
    has_dlt_template: bool
    dlt_template_id: Optional[str]
    dlt_entity_id: Optional[str]
    issues: List[str] = []
    warnings: List[str] = []


# ==================== NOTIFICATION TRIGGER SCHEMAS ====================

class TriggerTimingType(str, Enum):
    """Trigger timing types"""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    DELAYED = "delayed"


class NotificationTriggerCreate(BaseModel):
    """Schema for creating notification trigger"""
    trigger_code: str = Field(..., max_length=50, description="Unique trigger code")
    trigger_name: str = Field(..., max_length=200, description="Trigger name")
    description: Optional[str] = Field(None, description="Trigger description")
    event_type: str = Field(..., max_length=100, description="Event type to trigger on")
    entity_type: str = Field(..., max_length=50, description="Entity type")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Trigger conditions")
    template_id: int = Field(..., description="Notification template ID")
    channel: NotificationChannel = Field(..., description="Channel")
    priority: NotificationPriority = Field(NotificationPriority.MEDIUM)
    timing_type: TriggerTimingType = Field(TriggerTimingType.IMMEDIATE)
    delay_minutes: int = Field(0, ge=0, description="Delay in minutes")
    schedule_time: Optional[str] = Field(None, max_length=20, description="Schedule time HH:MM")
    recipient_config: Dict[str, Any] = Field(..., description="Recipient configuration")
    is_active: bool = Field(True)


class NotificationTriggerUpdate(BaseModel):
    """Schema for updating trigger"""
    trigger_name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    priority: Optional[NotificationPriority] = None
    timing_type: Optional[TriggerTimingType] = None
    delay_minutes: Optional[int] = Field(None, ge=0)
    schedule_time: Optional[str] = None
    recipient_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_enabled: Optional[bool] = None


class NotificationTriggerResponse(BaseModel):
    """Response schema for trigger"""
    id: int
    trigger_code: str
    trigger_name: str
    description: Optional[str]
    event_type: str
    entity_type: str
    conditions: Optional[Dict[str, Any]]
    template_id: int
    channel: str
    priority: str
    timing_type: str
    delay_minutes: int
    schedule_time: Optional[str]
    recipient_config: Dict[str, Any]
    is_active: bool
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TriggerTestRequest(BaseModel):
    """Request to test a trigger"""
    trigger_code: str = Field(..., description="Trigger code")
    test_data: Dict[str, Any] = Field(..., description="Test event data")


class TriggerTestResponse(BaseModel):
    """Response for trigger test"""
    success: bool
    would_trigger: bool
    conditions_met: bool
    recipient_resolved: bool
    recipient_contact: Optional[str]
    rendered_body: Optional[str]
    errors: List[str] = []


# ==================== NOTIFICATION SCHEDULE SCHEMAS ====================

class ScheduleType(str, Enum):
    """Schedule types"""
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class NotificationScheduleCreate(BaseModel):
    """Schema for creating notification schedule"""
    schedule_name: str = Field(..., max_length=200, description="Schedule name")
    schedule_type: ScheduleType = Field(..., description="Schedule type")
    template_id: int = Field(..., description="Template ID")
    channel: NotificationChannel = Field(..., description="Channel")
    recipient_filter: Dict[str, Any] = Field(..., description="Recipient filter criteria")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    execution_time: str = Field(..., max_length=20, description="Execution time HH:MM")
    recurrence_pattern: Optional[Dict[str, Any]] = Field(None, description="Recurrence pattern")


class NotificationScheduleUpdate(BaseModel):
    """Schema for updating schedule"""
    schedule_name: Optional[str] = None
    recipient_filter: Optional[Dict[str, Any]] = None
    end_date: Optional[date] = None
    execution_time: Optional[str] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class NotificationScheduleResponse(BaseModel):
    """Response schema for schedule"""
    id: int
    schedule_name: str
    schedule_type: str
    template_id: int
    channel: str
    recipient_filter: Dict[str, Any]
    start_date: date
    end_date: Optional[date]
    execution_time: str
    recurrence_pattern: Optional[Dict[str, Any]]
    last_executed_at: Optional[datetime]
    next_execution_at: Optional[datetime]
    execution_count: int
    status: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== PROVIDER CONFIGURATION SCHEMAS ====================

class ProviderType(str, Enum):
    """Provider types"""
    TWILIO = "twilio"
    MSG91 = "msg91"
    SENDGRID = "sendgrid"
    AWS_SES = "aws_ses"
    WHATSAPP_BUSINESS = "whatsapp_business"
    FIREBASE = "firebase"


class NotificationProviderCreate(BaseModel):
    """Schema for creating provider"""
    provider_code: str = Field(..., max_length=50, description="Unique provider code")
    provider_name: str = Field(..., max_length=200, description="Provider name")
    provider_type: ProviderType = Field(..., description="Provider type")
    supported_channels: List[NotificationChannel] = Field(..., description="Supported channels")
    api_endpoint: Optional[str] = Field(None, max_length=500)
    api_key: Optional[str] = Field(None, description="API key (will be encrypted)")
    api_secret: Optional[str] = Field(None, description="API secret (will be encrypted)")
    additional_config: Optional[Dict[str, Any]] = Field(None, description="Provider config")
    rate_limit_per_second: int = Field(10, ge=1)
    rate_limit_per_minute: int = Field(100, ge=1)
    rate_limit_per_hour: int = Field(1000, ge=1)
    priority: int = Field(1, ge=1, description="Lower = higher priority")
    is_primary: bool = Field(True)
    fallback_provider_id: Optional[int] = None


class NotificationProviderUpdate(BaseModel):
    """Schema for updating provider"""
    provider_name: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    additional_config: Optional[Dict[str, Any]] = None
    rate_limit_per_second: Optional[int] = Field(None, ge=1)
    rate_limit_per_minute: Optional[int] = Field(None, ge=1)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1)
    priority: Optional[int] = Field(None, ge=1)
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    is_enabled: Optional[bool] = None


class NotificationProviderResponse(BaseModel):
    """Response schema for provider"""
    id: int
    provider_code: str
    provider_name: str
    provider_type: str
    supported_channels: List[str]
    api_endpoint: Optional[str]
    rate_limit_per_second: int
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    priority: int
    is_primary: bool
    is_active: bool
    is_enabled: bool
    health_status: str
    last_health_check: Optional[datetime]
    total_sent: int
    total_failed: int
    last_used_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProviderHealthCheck(BaseModel):
    """Provider health check result"""
    provider_id: int
    provider_name: str
    health_status: str
    response_time_ms: Optional[int]
    last_check: datetime
    error_message: Optional[str]


# ==================== DELIVERY REPORT SCHEMAS ====================

class DeliveryReportWebhook(BaseModel):
    """Webhook payload for delivery reports"""
    provider_message_id: str = Field(..., description="Provider message ID")
    delivery_status: DeliveryStatus = Field(..., description="Delivery status")
    delivery_time: datetime = Field(..., description="Delivery timestamp")
    delivery_metadata: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_description: Optional[str] = None


class DeliveryReportResponse(BaseModel):
    """Response schema for delivery report"""
    id: int
    notification_id: Optional[int]
    provider_message_id: str
    provider_id: int
    delivery_status: str
    delivery_time: datetime
    delivery_metadata: Optional[Dict[str, Any]]
    error_code: Optional[str]
    error_description: Optional[str]
    webhook_received_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ANALYTICS & REPORTING SCHEMAS ====================

class ProviderPerformance(BaseModel):
    """Provider performance metrics"""
    provider_id: int
    provider_name: str
    total_sent: int
    total_delivered: int
    total_failed: int
    delivery_rate: float
    avg_response_time_ms: int
    last_24h_sent: int
    health_status: str


class ChannelUsageReport(BaseModel):
    """Channel usage report"""
    date: date
    channel: str
    total_sent: int
    total_delivered: int
    total_failed: int
    delivery_rate: float
    avg_delivery_time_seconds: int
    cost_estimate: Optional[float] = None


class NotificationCostEstimate(BaseModel):
    """Cost estimate for notifications"""
    channel: str
    total_notifications: int
    estimated_cost: float
    currency: str = "INR"
    cost_per_message: float


class AnalyticsDashboard(BaseModel):
    """Complete analytics dashboard"""
    summary: NotificationSummary
    by_channel: List[ChannelStatistics]
    by_provider: List[ProviderPerformance]
    recent_failures: List[FailedNotification]
    delivery_trends: List[DeliveryRateTrend]


# ==================== BATCH OPERATIONS ====================

class BatchOperationStatus(str, Enum):
    """Batch operation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BatchNotificationStatus(BaseModel):
    """Batch notification status"""
    batch_id: str
    status: BatchOperationStatus
    total_count: int
    processed_count: int
    success_count: int
    failed_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    errors: List[str] = []

