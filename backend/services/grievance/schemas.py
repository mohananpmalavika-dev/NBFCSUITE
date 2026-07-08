"""
Grievance & Complaint Management - Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from .models import (
    ComplaintStatus,
    ComplaintPriority,
    ComplaintCategory,
    ChannelType,
    EscalationLevel,
    OmbudsmanStatus,
)


# ============================================================================
# COMPLAINT SCHEMAS
# ============================================================================

class ComplaintBase(BaseModel):
    """Base complaint schema"""
    customer_id: int
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None
    
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    
    category: ComplaintCategory
    sub_category: Optional[str] = None
    subject: str = Field(..., min_length=5, max_length=300)
    description: str = Field(..., min_length=10)
    
    channel: ChannelType
    source_reference: Optional[str] = None
    
    priority: ComplaintPriority = ComplaintPriority.MEDIUM
    tags: Optional[str] = None
    attachments: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    """Schema for creating a complaint"""
    pass


class ComplaintUpdate(BaseModel):
    """Schema for updating a complaint"""
    subject: Optional[str] = Field(None, min_length=5, max_length=300)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[ComplaintCategory] = None
    sub_category: Optional[str] = None
    priority: Optional[ComplaintPriority] = None
    status: Optional[ComplaintStatus] = None
    assigned_to: Optional[int] = None
    assigned_department: Optional[str] = None
    resolution: Optional[str] = None
    resolution_remarks: Optional[str] = None
    tags: Optional[str] = None


class ComplaintAssign(BaseModel):
    """Schema for assigning a complaint"""
    assigned_to: int
    assigned_department: Optional[str] = None
    remarks: Optional[str] = None


class ComplaintAcknowledge(BaseModel):
    """Schema for acknowledging a complaint"""
    acknowledgement_message: str
    expected_resolution_days: Optional[int] = 2


class ComplaintResolve(BaseModel):
    """Schema for resolving a complaint"""
    resolution: str = Field(..., min_length=10)
    resolution_remarks: Optional[str] = None
    compensation_amount: Optional[float] = 0


class ComplaintClose(BaseModel):
    """Schema for closing a complaint"""
    closure_remarks: Optional[str] = None
    customer_satisfaction: Optional[int] = Field(None, ge=1, le=5)


class ComplaintReopen(BaseModel):
    """Schema for reopening a complaint"""
    reopen_reason: str = Field(..., min_length=10)


class ComplaintResponse(BaseModel):
    """Response schema for complaint"""
    id: int
    complaint_number: str
    customer_id: int
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    
    category: ComplaintCategory
    sub_category: Optional[str] = None
    subject: str
    description: str
    
    channel: ChannelType
    source_reference: Optional[str] = None
    
    status: ComplaintStatus
    priority: ComplaintPriority
    
    assigned_to: Optional[int] = None
    assigned_department: Optional[str] = None
    assigned_at: Optional[datetime] = None
    
    registered_date: datetime
    acknowledged_date: Optional[datetime] = None
    target_resolution_date: Optional[datetime] = None
    actual_resolution_date: Optional[datetime] = None
    closed_date: Optional[datetime] = None
    
    sla_hours: int
    sla_breach: bool
    sla_breach_hours: int
    
    resolution: Optional[str] = None
    resolution_remarks: Optional[str] = None
    customer_satisfaction: Optional[int] = None
    
    compensation_amount: Optional[float] = None
    compensation_paid: bool
    
    escalation_level: EscalationLevel
    escalated_to_ombudsman: bool
    
    is_regulatory: bool
    is_repeat: bool
    previous_complaint_id: Optional[int] = None
    
    tags: Optional[str] = None
    attachments: Optional[str] = None
    
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COMPLAINT CHANNEL SCHEMAS
# ============================================================================

class ComplaintChannelBase(BaseModel):
    """Base channel communication schema"""
    complaint_id: int
    channel_type: ChannelType
    direction: str  # INBOUND, OUTBOUND
    subject: Optional[str] = None
    message: str
    response: Optional[str] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    is_customer_initiated: bool = True
    requires_response: bool = False
    attachments: Optional[str] = None


class ComplaintChannelCreate(ComplaintChannelBase):
    """Schema for creating channel communication"""
    pass


class ComplaintChannelResponse(ComplaintChannelBase):
    """Response schema for channel communication"""
    id: int
    communication_date: datetime
    response_sent: bool
    handled_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ESCALATION SCHEMAS
# ============================================================================

class ComplaintEscalationBase(BaseModel):
    """Base escalation schema"""
    complaint_id: int
    escalation_level: EscalationLevel
    escalation_reason: str
    reason_details: Optional[str] = None
    escalated_to: int
    escalated_to_department: Optional[str] = None


class ComplaintEscalationCreate(ComplaintEscalationBase):
    """Schema for creating escalation"""
    is_auto_escalated: bool = False


class ComplaintEscalationAcknowledge(BaseModel):
    """Schema for acknowledging escalation"""
    acknowledgement_notes: str


class ComplaintEscalationResolve(BaseModel):
    """Schema for resolving escalation"""
    resolution_notes: str
    action_taken: str


class ComplaintEscalationResponse(BaseModel):
    """Response schema for escalation"""
    id: int
    complaint_id: int
    escalation_level: EscalationLevel
    escalation_number: int
    
    escalation_reason: str
    reason_details: Optional[str] = None
    is_auto_escalated: bool
    
    escalated_from: Optional[int] = None
    escalated_to: int
    escalated_to_department: Optional[str] = None
    
    escalated_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    escalation_sla_hours: int
    escalation_sla_breach: bool
    
    status: str
    resolution_notes: Optional[str] = None
    action_taken: Optional[str] = None
    
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SLA SCHEMAS
# ============================================================================

class ComplaintSLABase(BaseModel):
    """Base SLA configuration schema"""
    category: Optional[ComplaintCategory] = None
    priority: Optional[ComplaintPriority] = None
    channel: Optional[ChannelType] = None
    
    acknowledgement_hours: int = 2
    resolution_hours: int = 48
    escalation_hours: int = 24
    
    auto_escalate: bool = True
    escalation_level_1_hours: int = 24
    escalation_level_2_hours: int = 48
    escalation_level_3_hours: int = 72
    
    send_reminder_before_hours: int = 4
    notify_customer: bool = True
    notify_manager: bool = True
    
    is_regulatory_complaint: bool = False
    regulatory_timeline_days: Optional[int] = None


class ComplaintSLACreate(ComplaintSLABase):
    """Schema for creating SLA configuration"""
    pass


class ComplaintSLAUpdate(BaseModel):
    """Schema for updating SLA configuration"""
    acknowledgement_hours: Optional[int] = None
    resolution_hours: Optional[int] = None
    escalation_hours: Optional[int] = None
    auto_escalate: Optional[bool] = None
    is_active: Optional[bool] = None


class ComplaintSLAResponse(ComplaintSLABase):
    """Response schema for SLA configuration"""
    id: int
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# OMBUDSMAN SCHEMAS
# ============================================================================

class OmbudsmanCaseBase(BaseModel):
    """Base ombudsman case schema"""
    complaint_id: int
    ombudsman_case_number: str
    ombudsman_office: str
    grounds_of_complaint: str
    documents_submitted: Optional[str] = None
    supporting_evidence: Optional[str] = None


class OmbudsmanCaseCreate(OmbudsmanCaseBase):
    """Schema for creating ombudsman case"""
    pass


class OmbudsmanCaseUpdate(BaseModel):
    """Schema for updating ombudsman case"""
    status: Optional[OmbudsmanStatus] = None
    ombudsman_office: Optional[str] = None
    grounds_of_complaint: Optional[str] = None
    documents_submitted: Optional[str] = None
    bank_response: Optional[str] = None
    notes: Optional[str] = None


class OmbudsmanCaseSubmit(BaseModel):
    """Schema for submitting to ombudsman"""
    submitted_date: datetime
    submission_reference: str


class OmbudsmanCaseHearing(BaseModel):
    """Schema for scheduling hearing"""
    hearing_date: datetime
    bank_representative: str


class OmbudsmanCaseAward(BaseModel):
    """Schema for recording award"""
    award_date: datetime
    award_details: str
    compensation_awarded: float


class OmbudsmanCaseResponse(BaseModel):
    """Response schema for ombudsman case"""
    id: int
    complaint_id: int
    ombudsman_case_number: str
    ombudsman_office: str
    
    submitted_date: Optional[datetime] = None
    submission_reference: Optional[str] = None
    grounds_of_complaint: str
    
    documents_submitted: Optional[str] = None
    supporting_evidence: Optional[str] = None
    
    status: OmbudsmanStatus
    acknowledgement_date: Optional[datetime] = None
    hearing_date: Optional[datetime] = None
    award_date: Optional[datetime] = None
    closure_date: Optional[datetime] = None
    
    award_details: Optional[str] = None
    compensation_awarded: Optional[float] = None
    compensation_paid: bool
    compensation_paid_date: Optional[datetime] = None
    
    bank_response: Optional[str] = None
    bank_response_date: Optional[datetime] = None
    bank_representative: Optional[str] = None
    
    is_appealed: bool
    appeal_filed_by: Optional[str] = None
    appeal_date: Optional[datetime] = None
    appeal_outcome: Optional[str] = None
    
    rbi_guidelines_followed: bool
    resolution_within_30_days: Optional[bool] = None
    
    notes: Optional[str] = None
    internal_remarks: Optional[str] = None
    
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD & ANALYTICS SCHEMAS
# ============================================================================

class ComplaintStatistics(BaseModel):
    """Complaint statistics for dashboard"""
    total_complaints: int = 0
    registered: int = 0
    in_progress: int = 0
    resolved: int = 0
    closed: int = 0
    escalated: int = 0
    
    sla_breached: int = 0
    within_sla: int = 0
    
    by_priority: dict = {}
    by_category: dict = {}
    by_channel: dict = {}
    by_status: dict = {}
    
    avg_resolution_hours: float = 0
    customer_satisfaction_avg: float = 0
    
    escalation_rate: float = 0
    ombudsman_cases: int = 0


class ComplaintTrends(BaseModel):
    """Complaint trends over time"""
    period: str  # DAILY, WEEKLY, MONTHLY
    data_points: List[dict] = []
    total_count: int = 0
    trend_direction: str = "STABLE"  # INCREASING, DECREASING, STABLE


# ============================================================================
# FILTER SCHEMAS
# ============================================================================

class ComplaintFilter(BaseModel):
    """Filter schema for complaints"""
    status: Optional[ComplaintStatus] = None
    priority: Optional[ComplaintPriority] = None
    category: Optional[ComplaintCategory] = None
    channel: Optional[ChannelType] = None
    assigned_to: Optional[int] = None
    customer_id: Optional[int] = None
    escalation_level: Optional[EscalationLevel] = None
    sla_breach: Optional[bool] = None
    is_regulatory: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_text: Optional[str] = None
    skip: int = 0
    limit: int = 100
