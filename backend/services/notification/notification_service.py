"""
Notification Service

Core service for sending notifications across multiple channels
(SMS, Email, WhatsApp) with template support and delivery tracking.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import re

from backend.shared.database.notification_models import (
    Notification,
    NotificationTemplate,
    NotificationQueue,
    NotificationLog
)
from backend.services.notification.schemas import (
    SendNotificationRequest,
    SendFromTemplateRequest,
    NotificationResponse,
    NotificationStatus,
    NotificationChannel,
    NotificationPriority
)


class NotificationService:
    """Service for managing and sending notifications"""

    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    async def send_notification(
        self,
        request: SendNotificationRequest
    ) -> Notification:
        """
        Send a notification immediately or schedule for later.
        
        Creates notification record, validates recipient, and queues for sending.
        """
        # Generate notification number
        notification_number = await self._generate_notification_number()
        
        # Create notification
        notification = Notification(
            notification_number=notification_number,
            channel=request.channel.value,
            priority=request.priority.value,
            recipient_type=request.recipient_type.value,
            recipient_id=request.recipient_id,
            recipient_contact=request.recipient_contact,
            recipient_name=request.recipient_name,
            subject=request.subject,
            body=request.body,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            scheduled_at=request.scheduled_at,
            status=NotificationStatus.PENDING.value,
            tenant_id=self.tenant_id,
            created_by=self.user_id
        )
        
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        
        # Log creation
        await self._log_event(notification.id, "created", "Notification created")
        
        # Queue for sending (if not scheduled)
        if not request.scheduled_at or request.scheduled_at <= datetime.utcnow():
            await self._enqueue(notification.id, request.priority.value)
            notification.status = NotificationStatus.QUEUED.value
        
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification

    async def send_from_template(
        self,
        request: SendFromTemplateRequest
    ) -> Notification:
        """Send notification using a template"""
        # Get template
        template = await self._get_template_by_code(request.template_code)
        
        if not template:
            raise ValueError(f"Template '{request.template_code}' not found")
        
        if not template.is_active:
            raise ValueError(f"Template '{request.template_code}' is not active")
        
        # Render template
        rendered = await self._render_template(template, request.variables)
        
        # Create notification using rendered content
        notification_request = SendNotificationRequest(
            channel=NotificationChannel(template.channel),
            recipient_type=request.recipient_type,
            recipient_id=request.recipient_id,
            recipient_contact=request.recipient_contact,
            recipient_name=request.recipient_name,
            subject=rendered.get("subject"),
            body=rendered["body"],
            priority=request.priority or NotificationPriority(template.priority),
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            scheduled_at=request.scheduled_at
        )
        
        notification = await self.send_notification(notification_request)
        
        # Update with template reference
        notification.template_id = template.id
        notification.template_code = template.template_code
        notification.variables = request.variables
        notification.max_retries = template.max_retries if template.retry_enabled else 0
        
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification

    async def send_bulk(
        self,
        template_code: str,
        recipients: List[Dict[str, Any]],
        priority: Optional[str] = None
    ) -> List[int]:
        """Send notifications to multiple recipients"""
        notification_ids = []
        
        for recipient_data in recipients:
            try:
                request = SendFromTemplateRequest(
                    template_code=template_code,
                    recipient_type=recipient_data.get("recipient_type", "customer"),
                    recipient_id=recipient_data["recipient_id"],
                    recipient_contact=recipient_data["recipient_contact"],
                    recipient_name=recipient_data.get("recipient_name"),
                    variables=recipient_data["variables"],
                    priority=priority,
                    entity_type=recipient_data.get("entity_type"),
                    entity_id=recipient_data.get("entity_id")
                )
                
                notification = await self.send_from_template(request)
                notification_ids.append(notification.id)
            except Exception as e:
                # Log error but continue with other recipients
                print(f"Failed to send to {recipient_data.get('recipient_contact')}: {e}")
                continue
        
        return notification_ids

    async def get_notification(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        query = select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.tenant_id == self.tenant_id
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def cancel_notification(self, notification_id: int) -> Notification:
        """Cancel a pending/scheduled notification"""
        notification = await self.get_notification(notification_id)
        
        if not notification:
            raise ValueError("Notification not found")
        
        if notification.status not in [NotificationStatus.PENDING.value, NotificationStatus.QUEUED.value]:
            raise ValueError(f"Cannot cancel notification with status {notification.status}")
        
        notification.status = NotificationStatus.CANCELLED.value
        await self._log_event(notification.id, "cancelled", "Notification cancelled by user")
        
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification

    async def retry_notification(self, notification_id: int) -> Notification:
        """Manually retry a failed notification"""
        notification = await self.get_notification(notification_id)
        
        if not notification:
            raise ValueError("Notification not found")
        
        if notification.status != NotificationStatus.FAILED.value:
            raise ValueError("Only failed notifications can be retried")
        
        if notification.retry_count >= notification.max_retries:
            raise ValueError("Maximum retry attempts reached")
        
        # Re-queue
        await self._enqueue(notification.id, notification.priority)
        notification.status = NotificationStatus.QUEUED.value
        notification.next_retry_at = None
        
        await self._log_event(notification.id, "retry", "Manual retry initiated")
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification

    async def get_recipient_notifications(
        self,
        recipient_id: int,
        limit: int = 20
    ) -> List[Notification]:
        """Get notifications for a specific recipient"""
        query = select(Notification).where(
            and_(
                Notification.recipient_id == recipient_id,
                Notification.tenant_id == self.tenant_id
            )
        ).order_by(
            Notification.created_at.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # Helper methods

    async def _generate_notification_number(self) -> str:
        """Generate unique notification number"""
        now = datetime.utcnow()
        prefix = f"NTF-{now.strftime('%Y%m')}"
        
        query = select(func.count(Notification.id)).where(
            and_(
                Notification.notification_number.like(f"{prefix}%"),
                Notification.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        
        return f"{prefix}-{count + 1:06d}"

    async def _get_template_by_code(self, template_code: str) -> Optional[NotificationTemplate]:
        """Get template by code"""
        query = select(NotificationTemplate).where(
            and_(
                NotificationTemplate.template_code == template_code,
                NotificationTemplate.tenant_id == self.tenant_id,
                NotificationTemplate.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _render_template(
        self,
        template: NotificationTemplate,
        variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """Render template with variables"""
        # Simple variable substitution
        body = template.body_template
        subject = template.subject or ""
        
        # Replace {{variable}} with actual values
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            body = body.replace(placeholder, str(value))
            if subject:
                subject = subject.replace(placeholder, str(value))
        
        # Check for unreplaced variables
        unreplaced = re.findall(r'\{\{(\w+)\}\}', body)
        if unreplaced:
            raise ValueError(f"Missing values for variables: {', '.join(unreplaced)}")
        
        return {
            "subject": subject if subject else None,
            "body": body
        }

    async def _enqueue(self, notification_id: int, priority: str):
        """Add notification to queue"""
        queue_entry = NotificationQueue(
            notification_id=notification_id,
            priority=priority,
            status="queued",
            tenant_id=self.tenant_id
        )
        
        self.db.add(queue_entry)
        await self._log_event(notification_id, "queued", f"Added to {priority} priority queue")

    async def _log_event(
        self,
        notification_id: int,
        event_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log notification event"""
        log = NotificationLog(
            notification_id=notification_id,
            event_type=event_type,
            message=message,
            metadata=metadata,
            tenant_id=self.tenant_id
        )
        
        self.db.add(log)

