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

