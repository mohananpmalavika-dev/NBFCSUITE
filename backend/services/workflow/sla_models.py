"""
SLA & Escalation Management Models

Comprehensive SLA tracking with:
- Response time SLA
- Resolution time SLA
- Business hours calculation
- Holiday calendar integration
- Pause/resume functionality
- Multi-level escalation
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, time


class SLAType(str, Enum):
    """SLA measurement types"""
    RESPONSE_TIME = "response_time"  # Time to first response
    RESOLUTION_TIME = "resolution_time"  # Time to complete
    APPROVAL_TIME = "approval_time"  # Time to approve/reject


class TimeCalculationType(str, Enum):
    """Time calculation methods"""
    CALENDAR_HOURS = "calendar_hours"  # 24/7 including weekends
    BUSINESS_HOURS = "business_hours"  # Only business hours
    WORKING_DAYS = "working_days"  # Exclude weekends and holidays


class SLAStatus(str, Enum):
    """SLA status"""
    ACTIVE = "active"
    MET = "met"
    BREACHED = "breached"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class EscalationType(str, Enum):
    """Escalation types"""
    SOFT = "soft"  # Reminder only
    HARD = "hard"  # Auto-transfer
    NOTIFY = "notify"  # Notify supervisor
    MULTI_LEVEL = "multi_level"  # Escalate up hierarchy


class BusinessHoursConfig(BaseModel):
    """Business hours configuration"""
    enabled: bool = True
    
    # Daily hours (24-hour format)
    monday: Optional[Dict[str, str]] = {"start": "09:00", "end": "17:00"}
    tuesday: Optional[Dict[str, str]] = {"start": "09:00", "end": "17:00"}
    wednesday: Optional[Dict[str, str]] = {"start": "09:00", "end": "17:00"}
    thursday: Optional[Dict[str, str]] = {"start": "09:00", "end": "17:00"}
    friday: Optional[Dict[str, str]] = {"start": "09:00", "end": "17:00"}
    saturday: Optional[Dict[str, str]] = None  # Closed
    sunday: Optional[Dict[str, str]] = None  # Closed
    
    # Timezone
    timezone: str = "Asia/Kolkata"


class HolidayCalendar(BaseModel):
    """Holiday calendar"""
    calendar_id: str
    name: str
    holidays: List[str]  # List of dates in YYYY-MM-DD format
    
    # Country/Region
    country: str = "IN"
    region: Optional[str] = None


class SLAConfiguration(BaseModel):
    """SLA configuration"""
    sla_id: str
    name: str
    description: Optional[str] = None
    
    # Entity configuration
    entity_type: str
    workflow_step: Optional[str] = None  # Specific step or null for overall
    
    # SLA settings
    sla_type: SLAType
    
    # Time configuration
    time_value: int = Field(..., description="Time value (hours, days, etc.)")
    time_unit: str = Field("hours", description="hours, days, minutes")
    calculation_type: TimeCalculationType = TimeCalculationType.BUSINESS_HOURS
    
    # Business hours
    business_hours_config: Optional[BusinessHoursConfig] = None
    holiday_calendar_id: Optional[str] = None
    
    # Pause settings
    allow_pause: bool = True
    pause_on_customer_action: bool = True
    pause_conditions: Optional[List[Dict[str, Any]]] = None
    
    # Warning thresholds (percentage of SLA)
    warning_threshold: float = 70.0  # Warn at 70% of SLA
    critical_threshold: float = 90.0  # Critical at 90% of SLA
    
    # Active status
    is_active: bool = True


class EscalationRule(BaseModel):
    """Escalation rule configuration"""
    rule_id: str
    name: str
    description: Optional[str] = None
    
    # Trigger configuration
    trigger_after_hours: float = Field(..., description="Hours after which to escalate")
    trigger_after_percentage: Optional[float] = Field(None, description="Or percentage of SLA")
    
    # Escalation type
    escalation_type: EscalationType
    
    # Actions
    send_reminder_to_assignee: bool = True
    notify_supervisor: bool = True
    notify_users: Optional[List[int]] = None  # Specific users to notify
    notify_roles: Optional[List[str]] = None  # Roles to notify
    
    # Hard escalation settings
    auto_transfer_to: Optional[int] = Field(None, description="User ID for auto-transfer")
    transfer_to_role: Optional[str] = Field(None, description="Or role for transfer")
    escalate_to_next_level: bool = False
    
    # Multi-level escalation
    escalation_levels: Optional[List[Dict[str, Any]]] = None
    
    # Notification
    notification_template: Optional[str] = None
    email_subject: Optional[str] = None
    
    # Repeat settings
    repeat_escalation: bool = False
    repeat_interval_hours: Optional[float] = None
    max_escalations: int = 3
    
    # Active status
    is_active: bool = True


class SLAEscalationConfig(BaseModel):
    """Combined SLA and escalation configuration"""
    config_id: str
    name: str
    entity_type: str
    
    # SLA configuration
    sla: SLAConfiguration
    
    # Escalation rules (ordered by trigger time)
    escalation_rules: List[EscalationRule] = []
    
    # Overall settings
    auto_close_on_sla_breach: bool = False
    send_breach_notification: bool = True
    breach_notification_users: Optional[List[int]] = None


class SLAInstance(BaseModel):
    """Running SLA instance"""
    instance_id: int
    sla_config_id: str
    entity_type: str
    entity_id: int
    workflow_instance_id: int
    workflow_step_id: Optional[int] = None
    
    # Status
    status: SLAStatus = SLAStatus.ACTIVE
    
    # Time tracking
    start_time: datetime
    deadline: datetime
    completion_time: Optional[datetime] = None
    
    # Pause tracking
    total_paused_duration: int = 0  # Minutes
    pause_start: Optional[datetime] = None
    pause_reason: Optional[str] = None
    
    # Escalations
    escalation_count: int = 0
    last_escalation_time: Optional[datetime] = None
    escalated_to_users: List[int] = []
    
    # Metrics
    time_elapsed_minutes: int = 0
    time_remaining_minutes: int = 0
    sla_percentage: float = 0.0  # 0-100, percentage of SLA consumed
    
    # Breach info
    breach_time: Optional[datetime] = None
    breach_duration_minutes: Optional[int] = None


class SLAMetrics(BaseModel):
    """SLA performance metrics"""
    entity_type: str
    period_start: datetime
    period_end: datetime
    
    # Overall metrics
    total_slas: int
    met_slas: int
    breached_slas: int
    active_slas: int
    
    # Percentages
    sla_compliance_rate: float  # % of SLAs met
    average_completion_percentage: float  # Average % of SLA used
    
    # Time metrics
    average_completion_time_hours: float
    median_completion_time_hours: float
    average_breach_duration_hours: Optional[float] = None
    
    # Escalation metrics
    total_escalations: int
    soft_escalations: int
    hard_escalations: int
    
    # By step breakdown
    by_step: Optional[Dict[str, Dict[str, Any]]] = None


# ==================== PRE-CONFIGURED SLA TEMPLATES ====================

class SLATemplates:
    """Pre-configured SLA templates"""
    
    @staticmethod
    def loan_approval_sla() -> SLAEscalationConfig:
        """Loan approval SLA configuration"""
        return SLAEscalationConfig(
            config_id="loan_approval_sla",
            name="Loan Approval SLA",
            entity_type="loan_application",
            sla=SLAConfiguration(
                sla_id="loan_sla",
                name="Loan Approval Time",
                entity_type="loan_application",
                sla_type=SLAType.RESOLUTION_TIME,
                time_value=24,
                time_unit="hours",
                calculation_type=TimeCalculationType.BUSINESS_HOURS,
                business_hours_config=BusinessHoursConfig(
                    enabled=True,
                    timezone="Asia/Kolkata"
                ),
                warning_threshold=70.0,
                critical_threshold=90.0,
                allow_pause=True,
                pause_on_customer_action=True
            ),
            escalation_rules=[
                EscalationRule(
                    rule_id="loan_reminder_2h",
                    name="2 Hour Reminder",
                    trigger_after_hours=2.0,
                    escalation_type=EscalationType.SOFT,
                    send_reminder_to_assignee=True,
                    notify_supervisor=False,
                    notification_template="reminder_2h"
                ),
                EscalationRule(
                    rule_id="loan_supervisor_4h",
                    name="4 Hour Supervisor Notification",
                    trigger_after_hours=4.0,
                    escalation_type=EscalationType.NOTIFY,
                    send_reminder_to_assignee=True,
                    notify_supervisor=True,
                    notification_template="escalation_4h"
                ),
                EscalationRule(
                    rule_id="loan_auto_escalate_6h",
                    name="6 Hour Auto Escalation",
                    trigger_after_hours=6.0,
                    escalation_type=EscalationType.HARD,
                    escalate_to_next_level=True,
                    notification_template="auto_escalate_6h"
                )
            ],
            send_breach_notification=True
        )
    
    @staticmethod
    def kyc_verification_sla() -> SLAEscalationConfig:
        """KYC verification SLA"""
        return SLAEscalationConfig(
            config_id="kyc_verification_sla",
            name="KYC Verification SLA",
            entity_type="customer",
            sla=SLAConfiguration(
                sla_id="kyc_sla",
                name="KYC Verification Time",
                entity_type="customer",
                sla_type=SLAType.RESOLUTION_TIME,
                time_value=48,
                time_unit="hours",
                calculation_type=TimeCalculationType.BUSINESS_HOURS,
                warning_threshold=75.0,
                critical_threshold=90.0
            ),
            escalation_rules=[
                EscalationRule(
                    rule_id="kyc_reminder_24h",
                    name="24 Hour Reminder",
                    trigger_after_hours=24.0,
                    escalation_type=EscalationType.SOFT,
                    send_reminder_to_assignee=True
                ),
                EscalationRule(
                    rule_id="kyc_escalate_40h",
                    name="40 Hour Escalation",
                    trigger_after_hours=40.0,
                    escalation_type=EscalationType.HARD,
                    escalate_to_next_level=True
                )
            ]
        )
