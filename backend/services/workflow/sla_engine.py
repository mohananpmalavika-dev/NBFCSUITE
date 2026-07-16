"""
SLA Execution Engine

Handles:
- Business hours calculation
- SLA tracking and monitoring
- Pause/resume functionality
- Escalation processing
- Multi-level escalation
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, time
import pytz
from enum import Enum

from backend.services.workflow.sla_models import (
    SLAConfiguration, EscalationRule, BusinessHoursConfig,
    HolidayCalendar, SLAInstance, SLAStatus, SLAType,
    TimeCalculationType, EscalationType
)


class SLAEngine:
    """SLA execution and tracking engine"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    # ==================== START SLA ====================
    
    def start_sla(
        self,
        config: SLAConfiguration,
        entity_id: int,
        workflow_instance_id: int,
        workflow_step_id: Optional[int] = None,
        holiday_calendar: Optional[HolidayCalendar] = None
    ) -> SLAInstance:
        """
        Start SLA tracking
        
        Args:
            config: SLA configuration
            entity_id: Entity being tracked
            workflow_instance_id: Workflow instance ID
            workflow_step_id: Optional workflow step ID
            holiday_calendar: Optional holiday calendar
        
        Returns:
            SLA instance
        """
        now = datetime.utcnow()
        
        # Calculate deadline
        deadline = self._calculate_deadline(
            start_time=now,
            time_value=config.time_value,
            time_unit=config.time_unit,
            calculation_type=config.calculation_type,
            business_hours_config=config.business_hours_config,
            holiday_calendar=holiday_calendar
        )
        
        # Create SLA instance
        from backend.shared.database.workflow_models import WorkflowSLA
        
        sla_instance = WorkflowSLA(
            tenant_id=self.tenant_id,
            sla_config_id=config.sla_id,
            entity_type=config.entity_type,
            entity_id=entity_id,
            workflow_instance_id=workflow_instance_id,
            workflow_step_id=workflow_step_id,
            status='active',
            start_time=now,
            deadline=deadline,
            sla_metadata={
                'config_name': config.name,
                'time_value': config.time_value,
                'time_unit': config.time_unit,
                'calculation_type': config.calculation_type,
                'warning_threshold': config.warning_threshold,
                'critical_threshold': config.critical_threshold
            }
        )
        
        self.db.add(sla_instance)
        self.db.flush()
        
        return sla_instance
    
    # ==================== BUSINESS HOURS CALCULATOR ====================
    
    def _calculate_deadline(
        self,
        start_time: datetime,
        time_value: int,
        time_unit: str,
        calculation_type: TimeCalculationType,
        business_hours_config: Optional[BusinessHoursConfig],
        holiday_calendar: Optional[HolidayCalendar]
    ) -> datetime:
        """Calculate SLA deadline considering business hours and holidays"""
        
        # Convert to total minutes
        if time_unit == 'minutes':
            total_minutes = time_value
        elif time_unit == 'hours':
            total_minutes = time_value * 60
        elif time_unit == 'days':
            total_minutes = time_value * 24 * 60
        else:
            total_minutes = time_value * 60  # Default to hours
        
        # Calendar hours - simple addition
        if calculation_type == TimeCalculationType.CALENDAR_HOURS:
            return start_time + timedelta(minutes=total_minutes)
        
        # Business hours or working days calculation
        if not business_hours_config or not business_hours_config.enabled:
            # Fallback to calendar hours
            return start_time + timedelta(minutes=total_minutes)
        
        # Calculate deadline considering business hours
        return self._calculate_business_hours_deadline(
            start_time=start_time,
            total_minutes=total_minutes,
            business_hours_config=business_hours_config,
            holiday_calendar=holiday_calendar,
            calculation_type=calculation_type
        )
    
    def _calculate_business_hours_deadline(
        self,
        start_time: datetime,
        total_minutes: int,
        business_hours_config: BusinessHoursConfig,
        holiday_calendar: Optional[HolidayCalendar],
        calculation_type: TimeCalculationType
    ) -> datetime:
        """Calculate deadline using business hours"""
        
        # Get timezone
        tz = pytz.timezone(business_hours_config.timezone)
        current_time = start_time.astimezone(tz)
        
        remaining_minutes = total_minutes
        
        while remaining_minutes > 0:
            # Get business hours for current day
            day_name = current_time.strftime('%A').lower()
            day_hours = getattr(business_hours_config, day_name, None)
            
            # Check if working day
            if not day_hours:
                # Non-working day, skip to next day
                current_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                current_time += timedelta(days=1)
                continue
            
            # Check if holiday
            if holiday_calendar and self._is_holiday(current_time.date(), holiday_calendar):
                # Holiday, skip to next day
                current_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                current_time += timedelta(days=1)
                continue
            
            # Parse business hours
            start_hour, start_min = map(int, day_hours['start'].split(':'))
            end_hour, end_min = map(int, day_hours['end'].split(':'))
            
            day_start = current_time.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
            day_end = current_time.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
            
            # If before business hours, jump to start
            if current_time < day_start:
                current_time = day_start
            
            # If after business hours, skip to next day
            if current_time >= day_end:
                current_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                current_time += timedelta(days=1)
                continue
            
            # Calculate available minutes today
            available_minutes = int((day_end - current_time).total_seconds() / 60)
            
            if remaining_minutes <= available_minutes:
                # Can complete within today
                current_time += timedelta(minutes=remaining_minutes)
                remaining_minutes = 0
            else:
                # Need more days
                remaining_minutes -= available_minutes
                current_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                current_time += timedelta(days=1)
        
        return current_time.astimezone(pytz.utc)
    
    def _is_holiday(self, date: datetime, holiday_calendar: HolidayCalendar) -> bool:
        """Check if date is a holiday"""
        date_str = date.strftime('%Y-%m-%d')
        return date_str in holiday_calendar.holidays
    
    # ==================== SLA TRACKING ====================
    
    def update_sla_status(self, sla_instance: Any) -> Dict[str, Any]:
        """Update SLA status and metrics"""
        now = datetime.utcnow()
        
        # Calculate elapsed time (excluding paused duration)
        if sla_instance.status == SLAStatus.PAUSED and sla_instance.pause_start:
            # Currently paused
            elapsed = (sla_instance.pause_start - sla_instance.start_time).total_seconds() / 60
        else:
            elapsed = (now - sla_instance.start_time).total_seconds() / 60
        
        elapsed_minutes = int(elapsed) - sla_instance.total_paused_duration
        
        # Calculate total SLA time
        total_sla_minutes = int((sla_instance.deadline - sla_instance.start_time).total_seconds() / 60)
        
        # Calculate remaining time
        if sla_instance.status == SLAStatus.PAUSED:
            # When paused, remaining time is frozen
            remaining_minutes = total_sla_minutes - elapsed_minutes
        else:
            remaining_minutes = int((sla_instance.deadline - now).total_seconds() / 60)
        
        # Calculate percentage
        sla_percentage = min(100.0, (elapsed_minutes / total_sla_minutes * 100)) if total_sla_minutes > 0 else 0.0
        
        # Update instance
        sla_instance.time_elapsed_minutes = elapsed_minutes
        sla_instance.time_remaining_minutes = remaining_minutes
        sla_instance.sla_percentage = sla_percentage
        
        # Check for breach
        if sla_instance.status == SLAStatus.ACTIVE and now > sla_instance.deadline:
            sla_instance.status = SLAStatus.BREACHED
            sla_instance.breach_time = now
            sla_instance.breach_duration_minutes = int((now - sla_instance.deadline).total_seconds() / 60)
        
        self.db.flush()
        
        return {
            'time_elapsed_minutes': elapsed_minutes,
            'time_remaining_minutes': remaining_minutes,
            'sla_percentage': sla_percentage,
            'status': sla_instance.status
        }
    
    def complete_sla(self, sla_instance: Any, success: bool = True) -> None:
        """Mark SLA as completed"""
        now = datetime.utcnow()
        
        # Update status
        if success:
            sla_instance.status = SLAStatus.MET
        else:
            sla_instance.status = SLAStatus.BREACHED
        
        sla_instance.completion_time = now
        
        # Calculate final metrics
        self.update_sla_status(sla_instance)
        
        self.db.flush()
    
    # ==================== PAUSE/RESUME ====================
    
    def pause_sla(self, sla_instance: Any, reason: Optional[str] = None) -> Dict[str, Any]:
        """Pause SLA tracking"""
        
        if sla_instance.status != SLAStatus.ACTIVE:
            return {
                'success': False,
                'error': f'Cannot pause SLA in status: {sla_instance.status}'
            }
        
        now = datetime.utcnow()
        sla_instance.status = SLAStatus.PAUSED
        sla_instance.pause_start = now
        sla_instance.pause_reason = reason
        
        self.db.flush()
        
        return {
            'success': True,
            'paused_at': now,
            'reason': reason
        }
    
    def resume_sla(self, sla_instance: Any) -> Dict[str, Any]:
        """Resume SLA tracking"""
        
        if sla_instance.status != SLAStatus.PAUSED:
            return {
                'success': False,
                'error': f'Cannot resume SLA in status: {sla_instance.status}'
            }
        
        now = datetime.utcnow()
        
        # Calculate paused duration
        if sla_instance.pause_start:
            paused_minutes = int((now - sla_instance.pause_start).total_seconds() / 60)
            sla_instance.total_paused_duration += paused_minutes
        
        # Adjust deadline
        if sla_instance.pause_start:
            pause_duration = now - sla_instance.pause_start
            sla_instance.deadline += pause_duration
        
        sla_instance.status = SLAStatus.ACTIVE
        sla_instance.pause_start = None
        
        self.db.flush()
        
        return {
            'success': True,
            'resumed_at': now,
            'paused_duration_minutes': paused_minutes if sla_instance.pause_start else 0
        }
    
    # ==================== ESCALATION PROCESSOR ====================
    
    def process_escalations(
        self,
        sla_instance: Any,
        escalation_rules: List[EscalationRule]
    ) -> List[Dict[str, Any]]:
        """Process escalation rules for SLA"""
        
        escalations_triggered = []
        
        # Sort rules by trigger time
        sorted_rules = sorted(
            escalation_rules,
            key=lambda r: r.trigger_after_hours or 0
        )
        
        for rule in sorted_rules:
            if not rule.is_active:
                continue
            
            # Check if should trigger
            should_trigger = self._should_trigger_escalation(
                sla_instance=sla_instance,
                rule=rule
            )
            
            if should_trigger:
                # Check if already triggered
                if self._is_escalation_triggered(sla_instance, rule):
                    # Check repeat settings
                    if not rule.repeat_escalation:
                        continue
                    
                    if sla_instance.escalation_count >= rule.max_escalations:
                        continue
                    
                    # Check repeat interval
                    if rule.repeat_interval_hours and sla_instance.last_escalation_time:
                        time_since_last = (datetime.utcnow() - sla_instance.last_escalation_time).total_seconds() / 3600
                        if time_since_last < rule.repeat_interval_hours:
                            continue
                
                # Trigger escalation
                result = self._trigger_escalation(sla_instance, rule)
                escalations_triggered.append(result)
        
        return escalations_triggered
    
    def _should_trigger_escalation(
        self,
        sla_instance: Any,
        rule: EscalationRule
    ) -> bool:
        """Check if escalation should trigger"""
        
        # Check by hours
        if rule.trigger_after_hours:
            elapsed_hours = sla_instance.time_elapsed_minutes / 60
            if elapsed_hours >= rule.trigger_after_hours:
                return True
        
        # Check by percentage
        if rule.trigger_after_percentage:
            if sla_instance.sla_percentage >= rule.trigger_after_percentage:
                return True
        
        return False
    
    def _is_escalation_triggered(self, sla_instance: Any, rule: EscalationRule) -> bool:
        """Check if escalation already triggered"""
        metadata = sla_instance.sla_metadata or {}
        triggered_rules = metadata.get('triggered_escalations', [])
        return rule.rule_id in triggered_rules
    
    def _trigger_escalation(
        self,
        sla_instance: Any,
        rule: EscalationRule
    ) -> Dict[str, Any]:
        """Trigger escalation action"""
        
        now = datetime.utcnow()
        
        # Update instance
        sla_instance.escalation_count += 1
        sla_instance.last_escalation_time = now
        
        # Track triggered rule
        metadata = sla_instance.sla_metadata or {}
        triggered_rules = metadata.get('triggered_escalations', [])
        triggered_rules.append(rule.rule_id)
        metadata['triggered_escalations'] = triggered_rules
        sla_instance.sla_metadata = metadata
        
        # Create escalation record
        from backend.shared.database.workflow_models import WorkflowHistory
        
        history = WorkflowHistory(
            tenant_id=self.tenant_id,
            workflow_instance_id=sla_instance.workflow_instance_id,
            workflow_step_id=sla_instance.workflow_step_id,
            event_type='sla_escalation',
            event_data={
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'escalation_type': rule.escalation_type,
                'sla_percentage': sla_instance.sla_percentage,
                'time_elapsed_minutes': sla_instance.time_elapsed_minutes,
                'actions': self._get_escalation_actions(rule)
            },
            created_at=now
        )
        self.db.add(history)
        
        # Perform escalation actions
        actions_performed = []
        
        # Send reminders
        if rule.send_reminder_to_assignee:
            actions_performed.append('reminder_sent')
            # TODO: Send notification to assignee
        
        # Notify supervisor
        if rule.notify_supervisor:
            actions_performed.append('supervisor_notified')
            # TODO: Send notification to supervisor
        
        # Notify specific users
        if rule.notify_users:
            actions_performed.append(f'notified_{len(rule.notify_users)}_users')
            # TODO: Send notifications
        
        # Hard escalation - auto transfer
        if rule.escalation_type == EscalationType.HARD:
            if rule.auto_transfer_to:
                actions_performed.append(f'transferred_to_user_{rule.auto_transfer_to}')
                # TODO: Transfer task
                sla_instance.escalated_to_users.append(rule.auto_transfer_to)
            
            elif rule.escalate_to_next_level:
                actions_performed.append('escalated_to_next_level')
                # TODO: Escalate to next level
        
        # Multi-level escalation
        if rule.escalation_type == EscalationType.MULTI_LEVEL and rule.escalation_levels:
            actions_performed.append('multi_level_escalation')
            # TODO: Process multi-level escalation
        
        self.db.flush()
        
        return {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'escalation_type': rule.escalation_type,
            'triggered_at': now,
            'actions_performed': actions_performed
        }
    
    def _get_escalation_actions(self, rule: EscalationRule) -> List[str]:
        """Get list of actions for escalation"""
        actions = []
        
        if rule.send_reminder_to_assignee:
            actions.append('Send reminder to assignee')
        if rule.notify_supervisor:
            actions.append('Notify supervisor')
        if rule.notify_users:
            actions.append(f'Notify {len(rule.notify_users)} users')
        if rule.auto_transfer_to:
            actions.append(f'Auto-transfer to user {rule.auto_transfer_to}')
        if rule.escalate_to_next_level:
            actions.append('Escalate to next level')
        
        return actions
    
    # ==================== METRICS ====================
    
    def calculate_metrics(
        self,
        entity_type: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Calculate SLA performance metrics"""
        
        from backend.shared.database.workflow_models import WorkflowSLA
        
        # Get SLA instances in period
        slas = self.db.query(WorkflowSLA).filter(
            WorkflowSLA.tenant_id == self.tenant_id,
            WorkflowSLA.entity_type == entity_type,
            WorkflowSLA.start_time >= period_start,
            WorkflowSLA.start_time <= period_end
        ).all()
        
        if not slas:
            return {
                'total_slas': 0,
                'met_slas': 0,
                'breached_slas': 0,
                'sla_compliance_rate': 0.0
            }
        
        # Count by status
        total = len(slas)
        met = len([s for s in slas if s.status == SLAStatus.MET])
        breached = len([s for s in slas if s.status == SLAStatus.BREACHED])
        active = len([s for s in slas if s.status == SLAStatus.ACTIVE])
        
        # Calculate compliance rate
        completed = met + breached
        compliance_rate = (met / completed * 100) if completed > 0 else 0.0
        
        # Calculate average completion percentage
        completed_slas = [s for s in slas if s.completion_time]
        avg_percentage = sum(s.sla_percentage for s in completed_slas) / len(completed_slas) if completed_slas else 0.0
        
        # Calculate time metrics
        avg_time = sum(s.time_elapsed_minutes for s in completed_slas) / len(completed_slas) / 60 if completed_slas else 0.0
        
        # Calculate escalation metrics
        total_escalations = sum(s.escalation_count for s in slas)
        
        return {
            'entity_type': entity_type,
            'period_start': period_start,
            'period_end': period_end,
            'total_slas': total,
            'met_slas': met,
            'breached_slas': breached,
            'active_slas': active,
            'sla_compliance_rate': round(compliance_rate, 2),
            'average_completion_percentage': round(avg_percentage, 2),
            'average_completion_time_hours': round(avg_time, 2),
            'total_escalations': total_escalations
        }
