"""
Event-Driven Notification Trigger Engine

Automatically sends notifications based on business events:
- Loan approval/disbursement/due date
- Payment received/failed/overdue
- KYC pending/expired
- Customer onboarding milestones
- Compliance alerts
- System events

Features:
- Condition-based trigger evaluation
- Delayed and scheduled notifications
- Template-based notification generation
- Event subscription and handling
- Retry on failure
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import json

from backend.shared.database.notification_models import (
    NotificationTrigger, NotificationSchedule, NotificationTemplate
)
from backend.services.notification.schemas import (
    NotificationTriggerCreate, NotificationTriggerUpdate, NotificationTriggerResponse,
    NotificationScheduleCreate, NotificationScheduleUpdate, NotificationScheduleResponse,
    SendFromTemplateRequest, TriggerTestRequest, TriggerTestResponse
)
from backend.services.notification.notification_service import NotificationService

logger = logging.getLogger(__name__)


class TriggerEngine:
    """Event-driven notification trigger engine"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.notification_service = NotificationService(db, tenant_id, user_id)
    
    # ========================================================================
    # TRIGGER MANAGEMENT
    # ========================================================================
    
    async def create_trigger(
        self,
        request: NotificationTriggerCreate
    ) -> NotificationTriggerResponse:
        """Create a new notification trigger"""
        # Check if trigger_code already exists
        result = await self.db.execute(
            select(NotificationTrigger).where(
                and_(
                    NotificationTrigger.trigger_code == request.trigger_code,
                    NotificationTrigger.tenant_id == self.tenant_id,
                    NotificationTrigger.is_deleted == False
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Trigger code {request.trigger_code} already exists")
        
        # Verify template exists
        template_result = await self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.id == request.template_id,
                    NotificationTemplate.tenant_id == self.tenant_id,
                    NotificationTemplate.is_deleted == False
                )
            )
        )
        template = template_result.scalar_one_or_none()
        
        if not template:
            raise ValueError(f"Template not found: {request.template_id}")
        
        # Create trigger
        trigger = NotificationTrigger(
            trigger_code=request.trigger_code,
            trigger_name=request.trigger_name,
            description=request.description,
            event_type=request.event_type,
            entity_type=request.entity_type,
            conditions=request.conditions,
            template_id=request.template_id,
            channel=request.channel.value,
            priority=request.priority.value,
            timing_type=request.timing_type.value,
            delay_minutes=request.delay_minutes,
            schedule_time=request.schedule_time,
            recipient_config=request.recipient_config,
            is_active=request.is_active,
            is_enabled=True,
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(trigger)
        await self.db.commit()
        await self.db.refresh(trigger)
        
        logger.info(f"Trigger created: {trigger.trigger_code} - {trigger.trigger_name}")
        
        return NotificationTriggerResponse.model_validate(trigger)
    
    async def update_trigger(
        self,
        trigger_id: int,
        request: NotificationTriggerUpdate
    ) -> NotificationTriggerResponse:
        """Update trigger configuration"""
        result = await self.db.execute(
            select(NotificationTrigger).where(
                and_(
                    NotificationTrigger.id == trigger_id,
                    NotificationTrigger.tenant_id == self.tenant_id,
                    NotificationTrigger.is_deleted == False
                )
            )
        )
        trigger = result.scalar_one_or_none()
        
        if not trigger:
            raise ValueError(f"Trigger not found: {trigger_id}")
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(trigger, key):
                setattr(trigger, key, value)
        
        trigger.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(trigger)
        
        return NotificationTriggerResponse.model_validate(trigger)
    
    async def get_trigger(self, trigger_id: int) -> NotificationTriggerResponse:
        """Get trigger by ID"""
        result = await self.db.execute(
            select(NotificationTrigger).where(
                and_(
                    NotificationTrigger.id == trigger_id,
                    NotificationTrigger.tenant_id == self.tenant_id,
                    NotificationTrigger.is_deleted == False
                )
            )
        )
        trigger = result.scalar_one_or_none()
        
        if not trigger:
            raise ValueError(f"Trigger not found: {trigger_id}")
        
        return NotificationTriggerResponse.model_validate(trigger)
    
    async def list_triggers(
        self,
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[NotificationTriggerResponse]:
        """List all triggers"""
        query = select(NotificationTrigger).where(
            and_(
                NotificationTrigger.tenant_id == self.tenant_id,
                NotificationTrigger.is_deleted == False
            )
        )
        
        if event_type:
            query = query.where(NotificationTrigger.event_type == event_type)
        
        if entity_type:
            query = query.where(NotificationTrigger.entity_type == entity_type)
        
        if is_active is not None:
            query = query.where(NotificationTrigger.is_active == is_active)
        
        query = query.order_by(NotificationTrigger.created_at.desc())
        
        result = await self.db.execute(query)
        triggers = result.scalars().all()
        
        return [NotificationTriggerResponse.model_validate(t) for t in triggers]
    
    async def enable_trigger(self, trigger_id: int) -> NotificationTriggerResponse:
        """Enable trigger"""
        update = NotificationTriggerUpdate(is_enabled=True)
        return await self.update_trigger(trigger_id, update)
    
    async def disable_trigger(self, trigger_id: int) -> NotificationTriggerResponse:
        """Disable trigger"""
        update = NotificationTriggerUpdate(is_enabled=False)
        return await self.update_trigger(trigger_id, update)
    
    # ========================================================================
    # EVENT PROCESSING
    # ========================================================================
    
    async def process_event(
        self,
        event_type: str,
        entity_type: str,
        entity_id: int,
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Process an event and trigger matching notifications
        
        Args:
            event_type: Type of event (e.g., "loan_approved")
            entity_type: Entity type (e.g., "loan")
            entity_id: Entity ID
            event_data: Event data for condition evaluation and variable substitution
            
        Returns:
            List of notification results
        """
        # Get matching triggers
        result = await self.db.execute(
            select(NotificationTrigger).where(
                and_(
                    NotificationTrigger.event_type == event_type,
                    NotificationTrigger.entity_type == entity_type,
                    NotificationTrigger.is_active == True,
                    NotificationTrigger.is_enabled == True,
                    NotificationTrigger.tenant_id == self.tenant_id,
                    NotificationTrigger.is_deleted == False
                )
            )
        )
        triggers = result.scalars().all()
        
        if not triggers:
            logger.info(f"No triggers found for event {event_type} on {entity_type}")
            return []
        
        logger.info(f"Processing {len(triggers)} triggers for event {event_type}")
        
        results = []
        
        for trigger in triggers:
            try:
                # Evaluate conditions
                if not self._evaluate_conditions(trigger.conditions, event_data):
                    logger.debug(f"Trigger {trigger.trigger_code} conditions not met")
                    continue
                
                # Resolve recipient
                recipient = self._resolve_recipient(trigger.recipient_config, event_data)
                
                if not recipient:
                    logger.warning(f"Could not resolve recipient for trigger {trigger.trigger_code}")
                    continue
                
                # Prepare variables for template
                variables = self._prepare_variables(event_data)
                
                # Calculate send time
                scheduled_at = self._calculate_send_time(trigger)
                
                # Send notification
                send_request = SendFromTemplateRequest(
                    template_code=trigger.template.template_code,
                    recipient_type=recipient.get("type", "customer"),
                    recipient_id=recipient.get("id"),
                    recipient_contact=recipient.get("contact"),
                    recipient_name=recipient.get("name"),
                    variables=variables,
                    priority=trigger.priority,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    scheduled_at=scheduled_at
                )
                
                notification = await self.notification_service.send_from_template(send_request)
                
                results.append({
                    "trigger_code": trigger.trigger_code,
                    "notification_id": notification.id,
                    "notification_number": notification.notification_number,
                    "status": "success"
                })
                
                logger.info(f"Notification triggered: {trigger.trigger_code} -> {notification.notification_number}")
                
            except Exception as e:
                logger.error(f"Error processing trigger {trigger.trigger_code}: {e}")
                results.append({
                    "trigger_code": trigger.trigger_code,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def _evaluate_conditions(
        self,
        conditions: Optional[Dict[str, Any]],
        event_data: Dict[str, Any]
    ) -> bool:
        """
        Evaluate trigger conditions against event data
        
        Supports:
        - Equality: {"status": "approved"}
        - Comparison: {"amount_gt": 100000}
        - Multiple conditions (AND logic)
        """
        if not conditions:
            return True
        
        for key, expected_value in conditions.items():
            # Handle comparison operators
            if key.endswith("_gt"):
                # Greater than
                field = key[:-3]
                actual_value = event_data.get(field)
                if actual_value is None or actual_value <= expected_value:
                    return False
            elif key.endswith("_gte"):
                # Greater than or equal
                field = key[:-4]
                actual_value = event_data.get(field)
                if actual_value is None or actual_value < expected_value:
                    return False
            elif key.endswith("_lt"):
                # Less than
                field = key[:-3]
                actual_value = event_data.get(field)
                if actual_value is None or actual_value >= expected_value:
                    return False
            elif key.endswith("_lte"):
                # Less than or equal
                field = key[:-4]
                actual_value = event_data.get(field)
                if actual_value is None or actual_value > expected_value:
                    return False
            elif key.endswith("_ne"):
                # Not equal
                field = key[:-3]
                actual_value = event_data.get(field)
                if actual_value == expected_value:
                    return False
            elif key.endswith("_in"):
                # In list
                field = key[:-3]
                actual_value = event_data.get(field)
                if actual_value not in expected_value:
                    return False
            else:
                # Equality
                actual_value = event_data.get(key)
                if actual_value != expected_value:
                    return False
        
        return True
    
    def _resolve_recipient(
        self,
        recipient_config: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve recipient from configuration and event data
        
        Config examples:
        - {"type": "customer", "field": "primary_phone"}
        - {"type": "user", "id_field": "assigned_to", "contact_field": "email"}
        """
        recipient_type = recipient_config.get("type", "customer")
        
        # Get recipient ID
        id_field = recipient_config.get("id_field", "customer_id")
        recipient_id = event_data.get(id_field)
        
        if not recipient_id:
            logger.warning(f"Recipient ID not found in event data: {id_field}")
            return None
        
        # Get contact
        contact_field = recipient_config.get("contact_field", "primary_phone")
        recipient_contact = event_data.get(contact_field)
        
        if not recipient_contact:
            logger.warning(f"Recipient contact not found in event data: {contact_field}")
            return None
        
        # Get name
        name_field = recipient_config.get("name_field", "customer_name")
        recipient_name = event_data.get(name_field)
        
        return {
            "type": recipient_type,
            "id": recipient_id,
            "contact": recipient_contact,
            "name": recipient_name
        }
    
    def _prepare_variables(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare variables for template rendering from event data"""
        # Return all event data as variables
        # Templates can use any field from the event
        return event_data
    
    def _calculate_send_time(self, trigger: NotificationTrigger) -> Optional[datetime]:
        """Calculate when notification should be sent"""
        if trigger.timing_type == "immediate":
            return None
        elif trigger.timing_type == "delayed":
            return datetime.now() + timedelta(minutes=trigger.delay_minutes)
        elif trigger.timing_type == "scheduled" and trigger.schedule_time:
            # Parse schedule_time (HH:MM format)
            try:
                hour, minute = map(int, trigger.schedule_time.split(":"))
                scheduled = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If time has passed today, schedule for tomorrow
                if scheduled <= datetime.now():
                    scheduled += timedelta(days=1)
                
                return scheduled
            except Exception as e:
                logger.error(f"Error parsing schedule_time {trigger.schedule_time}: {e}")
                return None
        
        return None
    
    async def test_trigger(
        self,
        request: TriggerTestRequest
    ) -> TriggerTestResponse:
        """Test a trigger with sample data"""
        # Get trigger
        result = await self.db.execute(
            select(NotificationTrigger).where(
                and_(
                    NotificationTrigger.trigger_code == request.trigger_code,
                    NotificationTrigger.tenant_id == self.tenant_id,
                    NotificationTrigger.is_deleted == False
                )
            )
        )
        trigger = result.scalar_one_or_none()
        
        if not trigger:
            return TriggerTestResponse(
                success=False,
                would_trigger=False,
                conditions_met=False,
                recipient_resolved=False,
                errors=["Trigger not found"]
            )
        
        errors = []
        
        # Test conditions
        conditions_met = self._evaluate_conditions(trigger.conditions, request.test_data)
        
        # Test recipient resolution
        recipient = self._resolve_recipient(trigger.recipient_config, request.test_data)
        recipient_resolved = recipient is not None
        
        if not recipient_resolved:
            errors.append("Could not resolve recipient from test data")
        
        # Test template rendering
        rendered_body = None
        try:
            if recipient_resolved:
                variables = self._prepare_variables(request.test_data)
                _, rendered_body, missing = await self.notification_service.render_template(
                    trigger.template.template_code,
                    variables
                )
                if missing:
                    errors.append(f"Missing variables: {', '.join(missing)}")
        except Exception as e:
            errors.append(f"Template rendering error: {str(e)}")
        
        would_trigger = conditions_met and recipient_resolved and not errors
        
        return TriggerTestResponse(
            success=True,
            would_trigger=would_trigger,
            conditions_met=conditions_met,
            recipient_resolved=recipient_resolved,
            recipient_contact=recipient.get("contact") if recipient else None,
            rendered_body=rendered_body,
            errors=errors
        )
    
    # ========================================================================
    # SCHEDULE MANAGEMENT
    # ========================================================================
    
    async def create_schedule(
        self,
        request: NotificationScheduleCreate
    ) -> NotificationScheduleResponse:
        """Create recurring notification schedule"""
        # Verify template exists
        template_result = await self.db.execute(
            select(NotificationTemplate).where(
                and_(
                    NotificationTemplate.id == request.template_id,
                    NotificationTemplate.tenant_id == self.tenant_id,
                    NotificationTemplate.is_deleted == False
                )
            )
        )
        template = template_result.scalar_one_or_none()
        
        if not template:
            raise ValueError(f"Template not found: {request.template_id}")
        
        # Calculate next execution
        next_execution = self._calculate_next_execution(
            request.start_date,
            request.execution_time,
            request.schedule_type.value,
            request.recurrence_pattern
        )
        
        # Create schedule
        schedule = NotificationSchedule(
            schedule_name=request.schedule_name,
            schedule_type=request.schedule_type.value,
            template_id=request.template_id,
            channel=request.channel.value,
            recipient_filter=request.recipient_filter,
            start_date=request.start_date,
            end_date=request.end_date,
            execution_time=request.execution_time,
            recurrence_pattern=request.recurrence_pattern,
            next_execution_at=next_execution,
            status="active",
            is_active=True,
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        
        logger.info(f"Schedule created: {schedule.schedule_name}")
        
        return NotificationScheduleResponse.model_validate(schedule)
    
    def _calculate_next_execution(
        self,
        start_date: datetime.date,
        execution_time: str,
        schedule_type: str,
        recurrence_pattern: Optional[Dict[str, Any]]
    ) -> datetime:
        """Calculate next execution time"""
        # Parse execution time
        hour, minute = map(int, execution_time.split(":"))
        
        # Start with today if start_date is today or in the past
        base_date = max(start_date, datetime.now().date())
        next_exec = datetime.combine(base_date, datetime.min.time()).replace(
            hour=hour, minute=minute
        )
        
        # If time has passed today, move to next occurrence
        if next_exec <= datetime.now():
            if schedule_type == "daily":
                next_exec += timedelta(days=1)
            elif schedule_type == "weekly":
                next_exec += timedelta(weeks=1)
            elif schedule_type == "monthly":
                # Add one month (approximately)
                next_exec = next_exec.replace(month=next_exec.month + 1 if next_exec.month < 12 else 1)
        
        return next_exec
    
    async def update_schedule(
        self,
        schedule_id: int,
        request: NotificationScheduleUpdate
    ) -> NotificationScheduleResponse:
        """Update schedule"""
        result = await self.db.execute(
            select(NotificationSchedule).where(
                and_(
                    NotificationSchedule.id == schedule_id,
                    NotificationSchedule.tenant_id == self.tenant_id
                )
            )
        )
        schedule = result.scalar_one_or_none()
        
        if not schedule:
            raise ValueError(f"Schedule not found: {schedule_id}")
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        schedule.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return NotificationScheduleResponse.model_validate(schedule)
    
    async def list_schedules(
        self,
        is_active: Optional[bool] = None,
        status: Optional[str] = None
    ) -> List[NotificationScheduleResponse]:
        """List schedules"""
        query = select(NotificationSchedule).where(
            NotificationSchedule.tenant_id == self.tenant_id
        )
        
        if is_active is not None:
            query = query.where(NotificationSchedule.is_active == is_active)
        
        if status:
            query = query.where(NotificationSchedule.status == status)
        
        query = query.order_by(NotificationSchedule.next_execution_at.asc())
        
        result = await self.db.execute(query)
        schedules = result.scalars().all()
        
        return [NotificationScheduleResponse.model_validate(s) for s in schedules]


# ============================================================================
# EVENT TYPES REGISTRY
# ============================================================================

class EventTypes:
    """Registry of supported event types"""
    
    # Loan Events
    LOAN_APPLICATION_SUBMITTED = "loan_application_submitted"
    LOAN_APPROVED = "loan_approved"
    LOAN_REJECTED = "loan_rejected"
    LOAN_DISBURSED = "loan_disbursed"
    LOAN_EMI_DUE = "loan_emi_due"
    LOAN_EMI_OVERDUE = "loan_emi_overdue"
    LOAN_CLOSED = "loan_closed"
    
    # Payment Events
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_BOUNCED = "payment_bounced"
    
    # Customer Events
    CUSTOMER_REGISTERED = "customer_registered"
    CUSTOMER_KYC_PENDING = "customer_kyc_pending"
    CUSTOMER_KYC_APPROVED = "customer_kyc_approved"
    CUSTOMER_KYC_REJECTED = "customer_kyc_rejected"
    CUSTOMER_BIRTHDAY = "customer_birthday"
    
    # Compliance Events
    DOCUMENT_EXPIRING = "document_expiring"
    DOCUMENT_EXPIRED = "document_expired"
    MANDATE_EXPIRING = "mandate_expiring"
    
    # Deposit Events
    DEPOSIT_OPENED = "deposit_opened"
    DEPOSIT_INTEREST_CREDITED = "deposit_interest_credited"
    DEPOSIT_MATURITY_DUE = "deposit_maturity_due"
    DEPOSIT_MATURED = "deposit_matured"
    
    # System Events
    SYSTEM_ALERT = "system_alert"
    WORKFLOW_TASK_ASSIGNED = "workflow_task_assigned"
    WORKFLOW_TASK_OVERDUE = "workflow_task_overdue"
