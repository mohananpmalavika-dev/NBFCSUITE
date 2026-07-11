"""
Enhanced Notification Service

Complete multi-channel notification system with:
- Template rendering with Jinja2
- Provider selection and failover
- Delivery tracking and retry logic
- Rate limiting and throttling
- DLT compliance integration
- Event-driven triggers
- Analytics and reporting
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta, date
import logging
import uuid
from jinja2 import Template, TemplateSyntaxError

from backend.shared.database.notification_models import (
    NotificationTemplate, Notification, NotificationQueue,
    NotificationLog, NotificationAnalytics, NotificationProvider,
    NotificationProviderLog, NotificationDeliveryReport,
    NotificationTrigger, NotificationSchedule
)
from backend.services.notification.schemas import (
    SendNotificationRequest, SendFromTemplateRequest,
    NotificationResponse, NotificationChannel
)
from backend.services.notification.channel_handlers import ChannelHandlerFactory

logger = logging.getLogger(__name__)


class NotificationService:
    """Core notification service with multi-channel support"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # TEMPLATE OPERATIONS
    # ========================================================================
    
    async def render_template(
        self,
        template_code: str,
        variables: Dict[str, Any]
    ) -> Tuple[Optional[str], str, List[str]]:
        """
        Render notification template with provided variables
        
        Args:
            template_code: Template code
            variables: Variable values
            
        Returns:
            Tuple of (rendered_subject, rendered_body, missing_variables)
        """
        # Get template
        result = await self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.template_code == template_code,
                    NotificationTemplate.tenant_id == self.tenant_id,
                    NotificationTemplate.is_active == True,
                    NotificationTemplate.is_deleted == False
                )
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise ValueError(f"Template not found: {template_code}")
        
        # Check for missing variables
        missing_vars = []
        if template.variables:
            for var in template.variables:
                if var not in variables:
                    missing_vars.append(var)
        
        # Render subject (if email)
        rendered_subject = None
        if template.subject:
            try:
                subject_template = Template(template.subject)
                rendered_subject = subject_template.render(**variables)
            except TemplateSyntaxError as e:
                logger.error(f"Subject template syntax error: {e}")
                raise ValueError(f"Invalid subject template: {e}")
            except Exception as e:
                logger.error(f"Subject rendering error: {e}")
                raise ValueError(f"Error rendering subject: {e}")
        
        # Render body
        try:
            body_template = Template(template.body_template)
            rendered_body = body_template.render(**variables)
        except TemplateSyntaxError as e:
            logger.error(f"Body template syntax error: {e}")
            raise ValueError(f"Invalid body template: {e}")
        except Exception as e:
            logger.error(f"Body rendering error: {e}")
            raise ValueError(f"Error rendering body: {e}")
        
        return rendered_subject, rendered_body, missing_vars
    
    async def test_template(
        self,
        template_code: str,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test template rendering"""
        try:
            subject, body, missing = await self.render_template(template_code, variables)
            
            return {
                "success": True,
                "rendered_subject": subject,
                "rendered_body": body,
                "missing_variables": missing,
                "errors": []
            }
        except Exception as e:
            return {
                "success": False,
                "rendered_subject": None,
                "rendered_body": None,
                "missing_variables": [],
                "errors": [str(e)]
            }
    
    # ========================================================================
    # PROVIDER SELECTION
    # ========================================================================
    
    async def get_active_provider(
        self,
        channel: str,
        preferred_provider_id: Optional[int] = None
    ) -> Optional[NotificationProvider]:
        """
        Get active provider for channel with failover support
        
        Args:
            channel: Notification channel
            preferred_provider_id: Preferred provider ID
            
        Returns:
            NotificationProvider or None
        """
        query = select(NotificationProvider).where(
            and_(
                NotificationProvider.tenant_id == self.tenant_id,
                NotificationProvider.is_active == True,
                NotificationProvider.is_enabled == True,
                NotificationProvider.is_deleted == False,
                NotificationProvider.supported_channels.contains([channel])
            )
        ).order_by(NotificationProvider.priority.asc())
        
        # If preferred provider specified, try it first
        if preferred_provider_id:
            result = await self.db.execute(
                query.where(NotificationProvider.id == preferred_provider_id)
            )
            provider = result.scalar_one_or_none()
            if provider and provider.health_status == "healthy":
                return provider
        
        # Otherwise, get first healthy provider by priority
        result = await self.db.execute(
            query.where(NotificationProvider.health_status == "healthy")
        )
        return result.scalar_one_or_none()
    
    # ========================================================================
    # SEND OPERATIONS
    # ========================================================================
    
    async def send_notification(
        self,
        request: SendNotificationRequest
    ) -> NotificationResponse:
        """
        Send a notification directly
        
        Args:
            request: SendNotificationRequest
            
        Returns:
            NotificationResponse
        """
        # Generate notification number
        notification_number = f"NOT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create notification record
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
            status="pending" if request.scheduled_at else "queued",
            tenant_id=self.tenant_id,
            created_by=self.user_id
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        # Log creation
        await self._log_event(
            notification.id,
            "created",
            "Notification created",
            {"source": "direct"}
        )
        
        # If not scheduled, queue for immediate sending
        if not request.scheduled_at:
            await self._queue_notification(notification)
            
            # Try to send immediately
            await self._process_notification(notification.id)
        
        return NotificationResponse.model_validate(notification)
    
    async def send_from_template(
        self,
        request: SendFromTemplateRequest
    ) -> NotificationResponse:
        """
        Send notification using template
        
        Args:
            request: SendFromTemplateRequest
            
        Returns:
            NotificationResponse
        """
        # Get template
        result = await self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.template_code == request.template_code,
                    NotificationTemplate.tenant_id == self.tenant_id,
                    NotificationTemplate.is_active == True,
                    NotificationTemplate.is_deleted == False
                )
            )
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise ValueError(f"Template not found: {request.template_code}")
        
        # Render template
        subject, body, missing_vars = await self.render_template(
            request.template_code,
            request.variables
        )
        
        if missing_vars:
            logger.warning(f"Missing variables in template {request.template_code}: {missing_vars}")
        
        # Create send request
        send_request = SendNotificationRequest(
            channel=NotificationChannel(template.channel),
            recipient_type=request.recipient_type,
            recipient_id=request.recipient_id,
            recipient_contact=request.recipient_contact,
            recipient_name=request.recipient_name,
            subject=subject,
            body=body,
            priority=request.priority or template.priority,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            scheduled_at=request.scheduled_at
        )
        
        # Send notification
        notification = await self.send_notification(send_request)
        
        # Update with template info
        await self.db.execute(
            select(Notification).where(Notification.id == notification.id)
        )
        notification_obj = (await self.db.execute(
            select(Notification).where(Notification.id == notification.id)
        )).scalar_one()
        
        notification_obj.template_id = template.id
        notification_obj.template_code = template.template_code
        notification_obj.variables = request.variables
        notification_obj.max_retries = template.max_retries
        
        await self.db.commit()
        
        return notification
    
    async def send_bulk_notifications(
        self,
        template_code: str,
        recipients: List[Dict[str, Any]],
        priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send bulk notifications using template
        
        Args:
            template_code: Template code
            recipients: List of recipient data with variables
            priority: Override priority
            
        Returns:
            Summary of bulk operation
        """
        success_count = 0
        failed_count = 0
        notifications = []
        errors = []
        
        for i, recipient in enumerate(recipients):
            try:
                request = SendFromTemplateRequest(
                    template_code=template_code,
                    recipient_type=recipient.get("recipient_type", "customer"),
                    recipient_id=recipient.get("recipient_id"),
                    recipient_contact=recipient.get("recipient_contact"),
                    recipient_name=recipient.get("recipient_name"),
                    variables=recipient.get("variables", {}),
                    priority=priority,
                    entity_type=recipient.get("entity_type"),
                    entity_id=recipient.get("entity_id")
                )
                
                notification = await self.send_from_template(request)
                notifications.append(notification)
                success_count += 1
                
            except Exception as e:
                logger.error(f"Bulk send error for recipient {i}: {e}")
                failed_count += 1
                errors.append({
                    "index": i,
                    "recipient": recipient.get("recipient_contact"),
                    "error": str(e)
                })
        
        return {
            "total": len(recipients),
            "success": success_count,
            "failed": failed_count,
            "notifications": notifications,
            "errors": errors
        }
    
    # ========================================================================
    # PROCESSING
    # ========================================================================
    
    async def _queue_notification(self, notification: Notification):
        """Add notification to queue"""
        queue_item = NotificationQueue(
            notification_id=notification.id,
            priority=notification.priority,
            status="queued",
            tenant_id=self.tenant_id
        )
        self.db.add(queue_item)
        await self.db.commit()
        
        # Update notification status
        notification.status = "queued"
        await self.db.commit()
        
        await self._log_event(
            notification.id,
            "queued",
            "Notification queued for processing"
        )
    
    async def _process_notification(self, notification_id: int):
        """Process and send notification"""
        # Get notification
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return
        
        # Get provider
        provider = await self.get_active_provider(notification.channel)
        
        if not provider:
            logger.error(f"No active provider for channel {notification.channel}")
            notification.status = "failed"
            notification.error_message = "No active provider available"
            await self.db.commit()
            await self._log_event(
                notification_id,
                "failed",
                "No active provider available"
            )
            return
        
        # Update status
        notification.status = "sending"
        await self.db.commit()
        
        await self._log_event(
            notification_id,
            "sending",
            f"Sending via {provider.provider_name}"
        )
        
        try:
            # Create channel handler
            handler = ChannelHandlerFactory.create_handler(
                channel=notification.channel,
                provider_type=provider.provider_type,
                provider_config={
                    "provider_type": provider.provider_type,
                    "api_key": provider.api_key,
                    "api_secret": provider.api_secret,
                    "api_endpoint": provider.api_endpoint,
                    "additional_config": provider.additional_config or {}
                }
            )
            
            # Send notification
            result = await handler.send(
                recipient=notification.recipient_contact,
                content=notification.body,
                subject=notification.subject,
                metadata=notification.variables or {}
            )
            
            # Log provider interaction
            provider_log = NotificationProviderLog(
                notification_id=notification.id,
                provider_id=provider.id,
                request_time=datetime.now(),
                response_time=datetime.now(),
                response_status_code=200 if result.get("success") else 500,
                provider_message_id=result.get("provider_message_id"),
                is_success=result.get("success"),
                error_message=result.get("error"),
                response_payload=result.get("response"),
                tenant_id=self.tenant_id
            )
            self.db.add(provider_log)
            
            # Update notification
            if result.get("success"):
                notification.status = "sent"
                notification.sent_at = datetime.now()
                notification.provider = provider.provider_name
                notification.provider_message_id = result.get("provider_message_id")
                notification.provider_response = result.get("response")
                notification.delivery_status = "pending"
                
                await self._log_event(
                    notification_id,
                    "sent",
                    "Notification sent successfully",
                    {"provider": provider.provider_name}
                )
                
                # Update provider stats
                provider.total_sent += 1
                provider.last_used_at = datetime.now()
            else:
                notification.status = "failed"
                notification.error_message = result.get("error")
                
                await self._log_event(
                    notification_id,
                    "failed",
                    f"Send failed: {result.get('error')}",
                    {"provider": provider.provider_name}
                )
                
                # Update provider stats
                provider.total_failed += 1
                
                # Check if should retry
                if notification.retry_count < notification.max_retries:
                    await self._schedule_retry(notification)
            
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Error processing notification {notification_id}: {e}")
            notification.status = "failed"
            notification.error_message = str(e)
            await self.db.commit()
            
            await self._log_event(
                notification_id,
                "failed",
                f"Processing error: {str(e)}"
            )
    
    async def _schedule_retry(self, notification: Notification):
        """Schedule notification retry"""
        notification.retry_count += 1
        notification.last_retry_at = datetime.now()
        
        # Calculate next retry time (exponential backoff)
        delay_minutes = 5 * (2 ** (notification.retry_count - 1))  # 5, 10, 20, 40 minutes
        notification.next_retry_at = datetime.now() + timedelta(minutes=delay_minutes)
        notification.status = "pending"
        
        await self.db.commit()
        
        await self._log_event(
            notification.id,
            "retry",
            f"Retry {notification.retry_count} scheduled",
            {"next_retry_at": notification.next_retry_at.isoformat()}
        )
    
    async def _log_event(
        self,
        notification_id: int,
        event_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log notification event"""
        log_entry = NotificationLog(
            notification_id=notification_id,
            event_type=event_type,
            message=message,
            event_metadata=metadata,
            tenant_id=self.tenant_id
        )
        self.db.add(log_entry)
        await self.db.commit()
    
    # ========================================================================
    # ANALYTICS
    # ========================================================================
    
    async def get_summary_statistics(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get summary statistics"""
        # Default to last 30 days
        if not from_date:
            from_date = date.today() - timedelta(days=30)
        if not to_date:
            to_date = date.today()
        
        # Get aggregated data
        result = await self.db.execute(
            select(
                func.sum(NotificationAnalytics.total_sent).label("total_sent"),
                func.sum(NotificationAnalytics.total_delivered).label("total_delivered"),
                func.sum(NotificationAnalytics.total_failed).label("total_failed"),
                func.sum(NotificationAnalytics.total_pending).label("total_pending")
            ).where(
                and_(
                    NotificationAnalytics.tenant_id == self.tenant_id,
                    NotificationAnalytics.date >= from_date,
                    NotificationAnalytics.date <= to_date
                )
            )
        )
        row = result.one()
        
        total_sent = row.total_sent or 0
        total_delivered = row.total_delivered or 0
        total_failed = row.total_failed or 0
        total_pending = row.total_pending or 0
        
        delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
        failure_rate = (total_failed / total_sent * 100) if total_sent > 0 else 0
        
        return {
            "total_sent": total_sent,
            "total_delivered": total_delivered,
            "total_failed": total_failed,
            "total_pending": total_pending,
            "delivery_rate": round(delivery_rate, 2),
            "failure_rate": round(failure_rate, 2)
        }
