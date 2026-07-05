"""
Notification Service API Router

REST API endpoints for notifications, templates, and analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.notification.notification_service import NotificationService
from backend.services.notification.template_service import TemplateService
from backend.services.notification.schemas import *

router = APIRouter()


# ==================== TEMPLATE ENDPOINTS ====================

@router.post("/notifications/templates", response_model=dict, tags=["Notification Templates"])
async def create_template(
    template: NotificationTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Create a new notification template.
    
    Templates support variable substitution using {{variable_name}} syntax.
    """
    try:
        service = TemplateService(db, tenant_id, current_user["id"])
        created_template = await service.create_template(template)
        return success_response(NotificationTemplateResponse.from_orm(created_template).dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/notifications/templates", response_model=dict, tags=["Notification Templates"])
async def list_templates(
    channel: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List notification templates with filters"""
    service = TemplateService(db, tenant_id, current_user["id"])
    templates, total = await service.list_templates(
        channel=channel,
        category=category,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    
    return success_response({
        "total": total,
        "skip": skip,
        "limit": limit,
        "templates": [NotificationTemplateResponse.from_orm(t).dict() for t in templates]
    })


@router.get("/notifications/templates/{template_id}", response_model=dict, tags=["Notification Templates"])
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get template details"""
    service = TemplateService(db, tenant_id, current_user["id"])
    template = await service.get_template(template_id)
    
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    
    return success_response(NotificationTemplateResponse.from_orm(template).dict())


@router.put("/notifications/templates/{template_id}", response_model=dict, tags=["Notification Templates"])
async def update_template(
    template_id: int,
    update_data: NotificationTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Update a template"""
    try:
        service = TemplateService(db, tenant_id, current_user["id"])
        template = await service.update_template(template_id, update_data)
        return success_response(NotificationTemplateResponse.from_orm(template).dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/notifications/templates/{template_id}", response_model=dict, tags=["Notification Templates"])
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Delete a template"""
    service = TemplateService(db, tenant_id, current_user["id"])
    success = await service.delete_template(template_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    
    return success_response({"message": "Template deleted successfully"})


# ==================== NOTIFICATION ENDPOINTS ====================

@router.post("/notifications/send", response_model=dict, tags=["Notifications"])
async def send_notification(
    request: SendNotificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Send a notification immediately or schedule for later.
    
    Supports SMS, Email, and WhatsApp channels.
    """
    try:
        service = NotificationService(db, tenant_id, current_user["id"])
        notification = await service.send_notification(request)
        return success_response(NotificationResponse.from_orm(notification).dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/notifications/send-template", response_model=dict, tags=["Notifications"])
async def send_from_template(
    request: SendFromTemplateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Send notification using a template.
    
    Renders template with provided variables and sends.
    """
    try:
        service = NotificationService(db, tenant_id, current_user["id"])
        notification = await service.send_from_template(request)
        return success_response(NotificationResponse.from_orm(notification).dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/notifications/send-bulk", response_model=dict, tags=["Notifications"])
async def send_bulk_notifications(
    request: BulkNotificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Send notifications to multiple recipients.
    
    Useful for EMI reminders, marketing campaigns, etc.
    """
    try:
        service = NotificationService(db, tenant_id, current_user["id"])
        notification_ids = await service.send_bulk(
            request.template_code,
            request.recipients,
            request.priority.value if request.priority else None
        )
        
        return success_response({
            "total_sent": len(notification_ids),
            "notification_ids": notification_ids
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/notifications/{notification_id}", response_model=dict, tags=["Notifications"])
async def get_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get notification details"""
    service = NotificationService(db, tenant_id, current_user["id"])
    notification = await service.get_notification(notification_id)
    
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    return success_response(NotificationResponse.from_orm(notification).dict())


@router.post("/notifications/{notification_id}/cancel", response_model=dict, tags=["Notifications"])
async def cancel_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Cancel a pending or scheduled notification"""
    try:
        service = NotificationService(db, tenant_id, current_user["id"])
        notification = await service.cancel_notification(notification_id)
        return success_response({
            "notification_id": notification.id,
            "status": notification.status,
            "message": "Notification cancelled successfully"
        })
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/notifications/{notification_id}/retry", response_model=dict, tags=["Notifications"])
async def retry_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Manually retry a failed notification"""
    try:
        service = NotificationService(db, tenant_id, current_user["id"])
        notification = await service.retry_notification(notification_id)
        return success_response({
            "notification_id": notification.id,
            "status": notification.status,
            "message": "Notification queued for retry"
        })
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/notifications/recipient/{recipient_id}", response_model=dict, tags=["Notifications"])
async def get_recipient_notifications(
    recipient_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get notifications for a specific recipient"""
    service = NotificationService(db, tenant_id, current_user["id"])
    notifications = await service.get_recipient_notifications(recipient_id, limit)
    
    return success_response({
        "recipient_id": recipient_id,
        "total": len(notifications),
        "notifications": [NotificationResponse.from_orm(n).dict() for n in notifications]
    })


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/notifications/analytics/summary", response_model=dict, tags=["Notification Analytics"])
async def get_notification_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get overall notification statistics.
    
    Returns summary of sent, delivered, failed notifications.
    """
    # Placeholder - would query NotificationAnalytics table
    return success_response({
        "total_sent": 0,
        "total_delivered": 0,
        "total_failed": 0,
        "total_pending": 0,
        "delivery_rate": 0.0,
        "failure_rate": 0.0
    })


@router.get("/notifications/analytics/by-channel", response_model=dict, tags=["Notification Analytics"])
async def get_channel_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get statistics broken down by channel"""
    # Placeholder
    return success_response({
        "channels": []
    })

