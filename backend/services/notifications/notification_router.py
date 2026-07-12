"""
Notification Management Router
API endpoints for notification templates, preferences, logs, and manual triggers
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel

from backend.shared.database.connection import get_db
from backend.shared.database.notification_models import (
    NotificationTemplate, NotificationLog, NotificationPreference,
    NotificationType, NotificationChannel, NotificationStatus
)
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User
from .notification_service import get_notification_service

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


# ============================================
# PYDANTIC SCHEMAS
# ============================================

class NotificationTemplateCreate(BaseModel):
    template_code: str
    template_name: str
    channel: str
    notification_type: str
    subject: Optional[str] = None
    body_template: str
    sms_template: Optional[str] = None
    available_variables: Optional[dict] = None
    send_days_before: Optional[int] = None
    send_at_time: Optional[str] = None
    priority: str = "normal"


class NotificationTemplateUpdate(BaseModel):
    template_name: Optional[str] = None
    subject: Optional[str] = None
    body_template: Optional[str] = None
    sms_template: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[str] = None


class NotificationPreferenceUpdate(BaseModel):
    rent_due_reminder_enabled: Optional[bool] = None
    lease_expiry_alert_enabled: Optional[bool] = None
    payment_received_enabled: Optional[bool] = None
    maintenance_update_enabled: Optional[bool] = None
    utility_bill_due_enabled: Optional[bool] = None
    payment_overdue_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None


class ManualNotificationSend(BaseModel):
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    channel: str
    subject: Optional[str] = None
    message: str
    property_id: Optional[int] = None
    lease_id: Optional[int] = None


# ============================================
# TEMPLATE ENDPOINTS
# ============================================

@router.get("/templates", response_model=dict)
async def get_notification_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    channel: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notification templates"""
    
    query = select(NotificationTemplate).where(
        and_(
            NotificationTemplate.tenant_id == current_user.tenant_id,
            NotificationTemplate.is_deleted == False
        )
    )
    
    if channel:
        query = query.where(NotificationTemplate.channel == channel)
    if is_active is not None:
        query = query.where(NotificationTemplate.is_active == is_active)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(NotificationTemplate.created_at.desc())
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    items = []
    for template in templates:
        items.append({
            "id": template.id,
            "template_code": template.template_code,
            "template_name": template.template_name,
            "channel": template.channel.value,
            "notification_type": template.notification_type.value,
            "subject": template.subject,
            "is_active": template.is_active,
            "priority": template.priority,
            "send_days_before": template.send_days_before,
            "created_at": template.created_at.isoformat()
        })
    
    return {
        "success": True,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }


@router.get("/templates/{template_id}", response_model=dict)
async def get_notification_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification template details"""
    
    result = await db.execute(
        select(NotificationTemplate).where(
            and_(
                NotificationTemplate.id == template_id,
                NotificationTemplate.tenant_id == current_user.tenant_id,
                NotificationTemplate.is_deleted == False
            )
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "success": True,
        "data": {
            "id": template.id,
            "template_code": template.template_code,
            "template_name": template.template_name,
            "channel": template.channel.value,
            "notification_type": template.notification_type.value,
            "subject": template.subject,
            "body_template": template.body_template,
            "sms_template": template.sms_template,
            "available_variables": template.available_variables,
            "is_active": template.is_active,
            "priority": template.priority,
            "send_days_before": template.send_days_before,
            "send_at_time": template.send_at_time,
            "created_at": template.created_at.isoformat()
        }
    }


@router.post("/templates", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_notification_template(
    template_data: NotificationTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification template"""
    
    # Check if template code already exists
    result = await db.execute(
        select(NotificationTemplate).where(
            NotificationTemplate.template_code == template_data.template_code
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template with code {template_data.template_code} already exists"
        )
    
    template = NotificationTemplate(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **template_data.model_dump()
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return {
        "success": True,
        "message": "Notification template created successfully",
        "data": {"id": template.id, "template_code": template.template_code}
    }


@router.put("/templates/{template_id}", response_model=dict)
async def update_notification_template(
    template_id: int,
    template_data: NotificationTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification template"""
    
    result = await db.execute(
        select(NotificationTemplate).where(
            and_(
                NotificationTemplate.id == template_id,
                NotificationTemplate.tenant_id == current_user.tenant_id,
                NotificationTemplate.is_deleted == False
            )
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    template.updated_by = current_user.id
    template.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Notification template updated successfully"
    }


# ============================================
# PREFERENCE ENDPOINTS
# ============================================

@router.get("/preferences", response_model=dict)
async def get_notification_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user notification preferences"""
    
    result = await db.execute(
        select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == current_user.id,
                NotificationPreference.tenant_id == current_user.tenant_id,
                NotificationPreference.is_deleted == False
            )
        )
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        # Create default preferences
        preference = NotificationPreference(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id
        )
        db.add(preference)
        await db.commit()
        await db.refresh(preference)
    
    return {
        "success": True,
        "data": {
            "id": preference.id,
            "rent_due_reminder_enabled": preference.rent_due_reminder_enabled,
            "lease_expiry_alert_enabled": preference.lease_expiry_alert_enabled,
            "payment_received_enabled": preference.payment_received_enabled,
            "maintenance_update_enabled": preference.maintenance_update_enabled,
            "utility_bill_due_enabled": preference.utility_bill_due_enabled,
            "payment_overdue_enabled": preference.payment_overdue_enabled,
            "email_enabled": preference.email_enabled,
            "sms_enabled": preference.sms_enabled,
            "email_address": preference.email_address,
            "phone_number": preference.phone_number
        }
    }


@router.put("/preferences", response_model=dict)
async def update_notification_preferences(
    preference_data: NotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user notification preferences"""
    
    result = await db.execute(
        select(NotificationPreference).where(
            and_(
                NotificationPreference.user_id == current_user.id,
                NotificationPreference.tenant_id == current_user.tenant_id,
                NotificationPreference.is_deleted == False
            )
        )
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        # Create new preferences
        preference = NotificationPreference(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            **preference_data.model_dump(exclude_unset=True)
        )
        db.add(preference)
    else:
        # Update existing
        update_data = preference_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preference, field, value)
        preference.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Notification preferences updated successfully"
    }


# ============================================
# NOTIFICATION LOG ENDPOINTS
# ============================================

@router.get("/logs", response_model=dict)
async def get_notification_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    channel: Optional[str] = None,
    status: Optional[str] = None,
    notification_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification logs with filtering"""
    
    query = select(NotificationLog).where(
        and_(
            NotificationLog.tenant_id == current_user.tenant_id,
            NotificationLog.is_deleted == False
        )
    )
    
    if channel:
        query = query.where(NotificationLog.channel == channel)
    if status:
        query = query.where(NotificationLog.status == status)
    if notification_type:
        query = query.where(NotificationLog.notification_type == notification_type)
    if start_date:
        query = query.where(NotificationLog.created_at >= start_date)
    if end_date:
        query = query.where(NotificationLog.created_at <= end_date)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(desc(NotificationLog.created_at))
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    items = []
    for log in logs:
        items.append({
            "id": log.id,
            "channel": log.channel.value,
            "notification_type": log.notification_type.value,
            "recipient_name": log.recipient_name,
            "recipient_email": log.recipient_email,
            "recipient_phone": log.recipient_phone,
            "subject": log.subject,
            "status": log.status.value,
            "sent_at": log.sent_at.isoformat() if log.sent_at else None,
            "error_message": log.error_message,
            "created_at": log.created_at.isoformat()
        })
    
    return {
        "success": True,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    }


@router.get("/logs/statistics", response_model=dict)
async def get_notification_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics"""
    
    # Total notifications
    total_result = await db.execute(
        select(func.count(NotificationLog.id)).where(
            and_(
                NotificationLog.tenant_id == current_user.tenant_id,
                NotificationLog.is_deleted == False
            )
        )
    )
    total = total_result.scalar()
    
    # By status
    status_result = await db.execute(
        select(
            NotificationLog.status,
            func.count(NotificationLog.id)
        ).where(
            and_(
                NotificationLog.tenant_id == current_user.tenant_id,
                NotificationLog.is_deleted == False
            )
        ).group_by(NotificationLog.status)
    )
    by_status = {row[0].value: row[1] for row in status_result.all()}
    
    # By channel
    channel_result = await db.execute(
        select(
            NotificationLog.channel,
            func.count(NotificationLog.id)
        ).where(
            and_(
                NotificationLog.tenant_id == current_user.tenant_id,
                NotificationLog.is_deleted == False
            )
        ).group_by(NotificationLog.channel)
    )
    by_channel = {row[0].value: row[1] for row in channel_result.all()}
    
    # By type
    type_result = await db.execute(
        select(
            NotificationLog.notification_type,
            func.count(NotificationLog.id)
        ).where(
            and_(
                NotificationLog.tenant_id == current_user.tenant_id,
                NotificationLog.is_deleted == False
            )
        ).group_by(NotificationLog.notification_type)
    )
    by_type = {row[0].value: row[1] for row in type_result.all()}
    
    return {
        "success": True,
        "data": {
            "total_notifications": total,
            "by_status": by_status,
            "by_channel": by_channel,
            "by_type": by_type
        }
    }


# ============================================
# MANUAL NOTIFICATION ENDPOINTS
# ============================================

@router.post("/send", response_model=dict)
async def send_manual_notification(
    notification_data: ManualNotificationSend,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a manual notification"""
    
    notification_service = get_notification_service()
    
    # Send notification
    results = await notification_service.send_notification(
        notification_type=NotificationType.EMAIL.value,
        recipient_email=notification_data.recipient_email,
        recipient_phone=notification_data.recipient_phone,
        subject=notification_data.subject,
        body_template=notification_data.message,
        sms_template=notification_data.message,
        variables={}
    )
    
    # Log notifications
    for channel, result in results.items():
        if result:
            log = NotificationLog(
                tenant_id=current_user.tenant_id,
                channel=NotificationChannel[notification_data.channel.upper()],
                notification_type=NotificationType.EMAIL if channel == 'email' else NotificationType.SMS,
                recipient_type='manual',
                recipient_email=notification_data.recipient_email if channel == 'email' else None,
                recipient_phone=notification_data.recipient_phone if channel == 'sms' else None,
                subject=notification_data.subject,
                body=notification_data.message,
                sms_content=notification_data.message if channel == 'sms' else None,
                property_id=notification_data.property_id,
                lease_id=notification_data.lease_id,
                status=NotificationStatus.SENT if result.get('success') else NotificationStatus.FAILED,
                sent_at=datetime.utcnow() if result.get('success') else None,
                failed_at=datetime.utcnow() if not result.get('success') else None,
                error_message=result.get('error'),
                external_message_id=result.get('message_id'),
                provider_name=result.get('provider'),
                created_by=current_user.id
            )
            db.add(log)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Notification sent successfully",
        "data": results
    }


@router.get("/channels", response_model=dict)
async def get_notification_channels():
    """Get available notification channels"""
    
    channels = [
        {"value": "rent_due_reminder", "label": "Rent Due Reminder"},
        {"value": "lease_expiry_alert", "label": "Lease Expiry Alert"},
        {"value": "payment_received", "label": "Payment Received"},
        {"value": "maintenance_update", "label": "Maintenance Update"},
        {"value": "utility_bill_due", "label": "Utility Bill Due"},
        {"value": "payment_overdue", "label": "Payment Overdue"},
        {"value": "lease_renewal_reminder", "label": "Lease Renewal Reminder"}
    ]
    
    return {
        "success": True,
        "data": channels
    }
