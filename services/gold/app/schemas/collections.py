"""
Gold Lending - Collections & Recovery Schemas
Phase 8: Complete collections, recovery, legal, and auction management
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


# ============================================================================
# COLLECTION CASE SCHEMAS
# ============================================================================

class CollectionCaseBase(BaseModel):
    """Base schema for collection case"""
    loan_account_id: UUID
    case_status: str = Field(default="open", pattern="^(open|in_progress|legal|npa|closed|settled)$")
    bucket_type: str = Field(..., pattern="^(dpd_0_30|dpd_31_60|dpd_61_90|dpd_90_plus|npa)$")
    overdue_days: int = Field(..., ge=0)
    overdue_amount: Decimal = Field(..., ge=0, decimal_places=2)
    total_outstanding: Decimal = Field(..., ge=0, decimal_places=2)
    principal_overdue: Decimal = Field(..., ge=0, decimal_places=2)
    interest_overdue: Decimal = Field(..., ge=0, decimal_places=2)
    penalty_overdue: Decimal = Field(..., ge=0, decimal_places=2)
    assigned_to_user_id: UUID
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    last_contact_date: Optional[date] = None
    next_action_date: Optional[date] = None


class CollectionCaseCreate(CollectionCaseBase):
    """Schema for creating a collection case"""
    pass


class CollectionCaseUpdate(BaseModel):
    """Schema for updating a collection case"""
    case_status: Optional[str] = Field(None, pattern="^(open|in_progress|legal|npa|closed|settled)$")
    bucket_type: Optional[str] = Field(None, pattern="^(dpd_0_30|dpd_31_60|dpd_61_90|dpd_90_plus|npa)$")
    overdue_days: Optional[int] = Field(None, ge=0)
    overdue_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    total_outstanding: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    principal_overdue: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    interest_overdue: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    penalty_overdue: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    assigned_to_user_id: Optional[UUID] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    last_contact_date: Optional[date] = None
    next_action_date: Optional[date] = None
    closure_reason: Optional[str] = None


class CollectionCaseResponse(CollectionCaseBase):
    """Schema for collection case response"""
    id: UUID
    case_number: str
    assigned_at: datetime
    closure_reason: Optional[str] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CollectionCaseDetail(CollectionCaseResponse):
    """Detailed collection case with related entities"""
    activities_count: int = 0
    field_visits_count: int = 0
    promises_count: int = 0
    legal_notices_count: int = 0
    recovery_actions_count: int = 0


# ============================================================================
# COLLECTION ACTIVITY SCHEMAS
# ============================================================================

class CollectionActivityBase(BaseModel):
    """Base schema for collection activity"""
    collection_case_id: UUID
    activity_type: str = Field(..., pattern="^(call|sms|email|whatsapp|field_visit|legal_notice|payment_received)$")
    activity_date: date
    activity_time: Optional[time] = None
    contact_mode: str = Field(..., pattern="^(phone|mobile|email|whatsapp|in_person|postal)$")
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_number: Optional[str] = Field(None, max_length=20)
    disposition: str = Field(..., pattern="^(contacted|not_reachable|promised_to_pay|partial_payment|dispute|refused|legal_action|settled)$")
    discussion_summary: Optional[str] = None
    amount_promised: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    promise_date: Optional[date] = None
    next_followup_date: Optional[date] = None
    performed_by_user_id: UUID
    location_lat: Optional[Decimal] = Field(None, ge=-90, le=90, decimal_places=8)
    location_lon: Optional[Decimal] = Field(None, ge=-180, le=180, decimal_places=8)


class CollectionActivityCreate(CollectionActivityBase):
    """Schema for creating a collection activity"""
    pass


class CollectionActivityResponse(CollectionActivityBase):
    """Schema for collection activity response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# FIELD VISIT SCHEMAS
# ============================================================================

class FieldVisitBase(BaseModel):
    """Base schema for field visit"""
    collection_case_id: UUID
    visit_date: date
    visit_time: Optional[time] = None
    visit_type: str = Field(..., pattern="^(courtesy|reminder|demand|legal|repossession|verification)$")
    visit_purpose: str
    visit_status: str = Field(default="scheduled", pattern="^(scheduled|in_progress|completed|cancelled|rescheduled)$")
    field_officer_id: UUID
    visit_address: str
    location_lat: Optional[Decimal] = Field(None, ge=-90, le=90, decimal_places=8)
    location_lon: Optional[Decimal] = Field(None, ge=-180, le=180, decimal_places=8)
    customer_met: bool = False
    person_met: Optional[str] = Field(None, max_length=100)
    person_relation: Optional[str] = Field(None, max_length=50)
    discussion_summary: Optional[str] = None
    property_verification: Optional[str] = None
    collateral_inspection: Optional[str] = None
    neighborhood_feedback: Optional[str] = None
    amount_collected: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    payment_receipt_no: Optional[str] = Field(None, max_length=50)
    photos_attached: bool = False
    visit_outcome: Optional[str] = Field(None, pattern="^(payment_collected|promise_obtained|customer_absent|dispute|legal_required|settled)$")
    next_visit_date: Optional[date] = None
    visit_expenses: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    expense_approved: bool = False


class FieldVisitCreate(FieldVisitBase):
    """Schema for creating a field visit"""
    pass


class FieldVisitUpdate(BaseModel):
    """Schema for updating a field visit"""
    visit_status: Optional[str] = Field(None, pattern="^(scheduled|in_progress|completed|cancelled|rescheduled)$")
    customer_met: Optional[bool] = None
    person_met: Optional[str] = Field(None, max_length=100)
    person_relation: Optional[str] = Field(None, max_length=50)
    discussion_summary: Optional[str] = None
    property_verification: Optional[str] = None
    collateral_inspection: Optional[str] = None
    neighborhood_feedback: Optional[str] = None
    amount_collected: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    payment_receipt_no: Optional[str] = Field(None, max_length=50)
    photos_attached: Optional[bool] = None
    visit_outcome: Optional[str] = Field(None, pattern="^(payment_collected|promise_obtained|customer_absent|dispute|legal_required|settled)$")
    next_visit_date: Optional[date] = None
    expense_approved: Optional[bool] = None


class FieldVisitResponse(FieldVisitBase):
    """Schema for field visit response"""
    id: UUID
    visit_number: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



# ============================================================================
# PAYMENT PROMISE SCHEMAS
# ============================================================================

class PaymentPromiseBase(BaseModel):
    """Base schema for payment promise"""
    collection_case_id: UUID
    promise_date: date
    promised_amount: Decimal = Field(..., ge=0, decimal_places=2)
    promised_payment_date: date
    promise_type: str = Field(..., pattern="^(full|partial|installment|settlement)$")
    promise_mode: Optional[str] = Field(None, pattern="^(cash|cheque|online|card|ecs)$")
    recorded_by_user_id: UUID
    recording_channel: str = Field(..., pattern="^(phone|field_visit|email|whatsapp|in_branch)$")
    promise_status: str = Field(default="active", pattern="^(active|kept|broken|partial|cancelled)$")
    amount_received: Decimal = Field(default=0, ge=0, decimal_places=2)
    payment_date: Optional[date] = None
    breach_reason: Optional[str] = None
    followup_required: bool = True
    reminder_sent: bool = False
    reminder_date: Optional[date] = None
    notes: Optional[str] = None


class PaymentPromiseCreate(PaymentPromiseBase):
    """Schema for creating a payment promise"""
    pass


class PaymentPromiseUpdate(BaseModel):
    """Schema for updating a payment promise"""
    promise_status: Optional[str] = Field(None, pattern="^(active|kept|broken|partial|cancelled)$")
    amount_received: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    payment_date: Optional[date] = None
    breach_reason: Optional[str] = None
    followup_required: Optional[bool] = None
    reminder_sent: Optional[bool] = None
    reminder_date: Optional[date] = None
    notes: Optional[str] = None


class PaymentPromiseResponse(PaymentPromiseBase):
    """Schema for payment promise response"""
    id: UUID
    promise_number: str
    fulfillment_percentage: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RECOVERY ACTION SCHEMAS
# ============================================================================

class RecoveryActionBase(BaseModel):
    """Base schema for recovery action"""
    collection_case_id: UUID
    action_type: str = Field(..., pattern="^(reminder|notice|repossession|seizure|auction_prep|legal_filing|settlement)$")
    action_date: date
    action_status: str = Field(default="planned", pattern="^(planned|approved|in_progress|completed|cancelled|failed)$")
    initiated_by_user_id: UUID
    approved_by_user_id: Optional[UUID] = None
    approval_date: Optional[date] = None
    action_description: str
    legal_basis: Optional[str] = None
    notice_period_days: Optional[int] = Field(None, ge=0)
    notice_sent_date: Optional[date] = None
    action_location: Optional[str] = None
    recovery_team: Optional[str] = None
    assets_recovered: Optional[str] = None
    estimated_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    actual_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    custody_location: Optional[str] = Field(None, max_length=200)
    custody_person: Optional[str] = Field(None, max_length=100)
    police_assistance: bool = False
    police_station: Optional[str] = Field(None, max_length=100)
    fir_number: Optional[str] = Field(None, max_length=50)
    customer_response: Optional[str] = None
    completion_date: Optional[date] = None
    expenses_incurred: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    outcome: Optional[str] = Field(None, pattern="^(successful|partial|failed|disputed|legal_challenge|settled)$")
    photos_attached: bool = False
    documents_attached: bool = False


class RecoveryActionCreate(RecoveryActionBase):
    """Schema for creating a recovery action"""
    pass


class RecoveryActionUpdate(BaseModel):
    """Schema for updating a recovery action"""
    action_status: Optional[str] = Field(None, pattern="^(planned|approved|in_progress|completed|cancelled|failed)$")
    approved_by_user_id: Optional[UUID] = None
    approval_date: Optional[date] = None
    assets_recovered: Optional[str] = None
    actual_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    custody_location: Optional[str] = Field(None, max_length=200)
    custody_person: Optional[str] = Field(None, max_length=100)
    police_assistance: Optional[bool] = None
    police_station: Optional[str] = Field(None, max_length=100)
    fir_number: Optional[str] = Field(None, max_length=50)
    customer_response: Optional[str] = None
    completion_date: Optional[date] = None
    expenses_incurred: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    outcome: Optional[str] = Field(None, pattern="^(successful|partial|failed|disputed|legal_challenge|settled)$")
    photos_attached: Optional[bool] = None
    documents_attached: Optional[bool] = None


class RecoveryActionResponse(RecoveryActionBase):
    """Schema for recovery action response"""
    id: UUID
    action_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# LEGAL NOTICE SCHEMAS
# ============================================================================

class LegalNoticeBase(BaseModel):
    """Base schema for legal notice"""
    collection_case_id: UUID
    notice_type: str = Field(..., pattern="^(reminder|demand|final_demand|legal_action|arbitration|suit_filing|auction_notice)$")
    notice_date: date
    notice_status: str = Field(default="draft", pattern="^(draft|approved|issued|delivered|acknowledged|responded|expired)$")
    issued_by_user_id: UUID
    approved_by_user_id: Optional[UUID] = None
    approval_date: Optional[date] = None
    legal_firm: Optional[str] = Field(None, max_length=200)
    lawyer_name: Optional[str] = Field(None, max_length=100)
    lawyer_contact: Optional[str] = Field(None, max_length=20)
    notice_subject: str
    notice_content: str
    demand_amount: Decimal = Field(..., ge=0, decimal_places=2)
    response_deadline: date
    delivery_mode: str = Field(..., pattern="^(registered_post|courier|hand_delivery|email|publication)$")
    delivery_date: Optional[date] = None
    tracking_number: Optional[str] = Field(None, max_length=50)
    delivery_status: Optional[str] = Field(None, pattern="^(pending|in_transit|delivered|refused|unclaimed|returned)$")
    acknowledgment_received: bool = False
    acknowledgment_date: Optional[date] = None
    customer_response: Optional[str] = None
    response_date: Optional[date] = None
    response_type: Optional[str] = Field(None, pattern="^(payment|partial_payment|dispute|settlement_offer|legal_challenge|no_response)$")
    followup_required: bool = True
    next_action: Optional[str] = Field(None, max_length=30)
    next_action_date: Optional[date] = None
    legal_expenses: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    documents_attached: bool = False


class LegalNoticeCreate(LegalNoticeBase):
    """Schema for creating a legal notice"""
    pass


class LegalNoticeUpdate(BaseModel):
    """Schema for updating a legal notice"""
    notice_status: Optional[str] = Field(None, pattern="^(draft|approved|issued|delivered|acknowledged|responded|expired)$")
    approved_by_user_id: Optional[UUID] = None
    approval_date: Optional[date] = None
    delivery_date: Optional[date] = None
    tracking_number: Optional[str] = Field(None, max_length=50)
    delivery_status: Optional[str] = Field(None, pattern="^(pending|in_transit|delivered|refused|unclaimed|returned)$")
    acknowledgment_received: Optional[bool] = None
    acknowledgment_date: Optional[date] = None
    customer_response: Optional[str] = None
    response_date: Optional[date] = None
    response_type: Optional[str] = Field(None, pattern="^(payment|partial_payment|dispute|settlement_offer|legal_challenge|no_response)$")
    next_action: Optional[str] = Field(None, max_length=30)
    next_action_date: Optional[date] = None
    legal_expenses: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class LegalNoticeResponse(LegalNoticeBase):
    """Schema for legal notice response"""
    id: UUID
    notice_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



# ============================================================================
# AUCTION LOT SCHEMAS
# ============================================================================

class AuctionLotBase(BaseModel):
    """Base schema for auction lot"""
    auction_date: date
    auction_location: str = Field(..., max_length=200)
    lot_status: str = Field(default="planned", pattern="^(planned|approved|advertised|open|closed|sold|unsold|cancelled)$")
    lot_description: str
    total_gold_weight: Decimal = Field(..., ge=0, decimal_places=3)
    total_items: int = Field(..., ge=0)
    reserve_price: Decimal = Field(..., ge=0, decimal_places=2)
    starting_bid: Decimal = Field(..., ge=0, decimal_places=2)
    bid_increment: Decimal = Field(..., ge=0, decimal_places=2)
    registration_deadline: date
    auction_start_time: Optional[time] = None
    auction_end_time: Optional[time] = None
    auction_type: str = Field(..., pattern="^(public|private|online|sealed_bid|spot_sale)$")
    auctioneer_name: Optional[str] = Field(None, max_length=100)
    auctioneer_license: Optional[str] = Field(None, max_length=50)
    winning_bid_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    winning_bidder_id: Optional[UUID] = None
    payment_deadline: Optional[date] = None
    payment_received: bool = False
    payment_date: Optional[date] = None
    handover_date: Optional[date] = None
    handover_completed: bool = False
    auction_expenses: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    net_realization: Optional[Decimal] = Field(None, decimal_places=2)
    created_by_user_id: UUID
    approved_by_user_id: Optional[UUID] = None
    approval_date: Optional[date] = None


class AuctionLotCreate(AuctionLotBase):
    """Schema for creating an auction lot"""
    pass


class AuctionLotUpdate(BaseModel):
    """Schema for updating an auction lot"""
    lot_status: Optional[str] = Field(None, pattern="^(planned|approved|advertised|open|closed|sold|unsold|cancelled)$")
    auction_date: Optional[date] = None
    auction_location: Optional[str] = Field(None, max_length=200)
    lot_description: Optional[str] = None
    auction_start_time: Optional[time] = None
    auction_end_time: Optional[time] = None
    auctioneer_name: Optional[str] = Field(None, max_length=100)
    auctioneer_license: Optional[str] = Field(None, max_length=50)
    winning_bid_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    winning_bidder_id: Optional[UUID] = None
    payment_deadline: Optional[date] = None
    payment_received: Optional[bool] = None
    payment_date: Optional[date] = None
    handover_date: Optional[date] = None
    handover_completed: Optional[bool] = None
    auction_expenses: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    net_realization: Optional[Decimal] = Field(None, decimal_places=2)
    approved_by_user_id: Optional[UUID] = None
    approval_date: Optional[date] = None


class AuctionLotResponse(AuctionLotBase):
    """Schema for auction lot response"""
    id: UUID
    lot_number: str
    bid_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuctionLotDetail(AuctionLotResponse):
    """Detailed auction lot with items and bids"""
    items_count: int = 0
    bids_count: int = 0
    highest_bid: Optional[Decimal] = None
    lowest_bid: Optional[Decimal] = None


# ============================================================================
# AUCTION LOT ITEM SCHEMAS
# ============================================================================

class AuctionLotItemBase(BaseModel):
    """Base schema for auction lot item"""
    auction_lot_id: UUID
    collection_case_id: UUID
    loan_account_id: UUID
    item_number: int = Field(..., ge=1)
    item_description: Optional[str] = None
    gold_weight: Decimal = Field(..., ge=0, decimal_places=3)
    gold_purity: Decimal = Field(..., ge=0, le=100, decimal_places=2)
    estimated_value: Decimal = Field(..., ge=0, decimal_places=2)
    customer_notified: bool = False
    notification_date: Optional[date] = None
    customer_objection: Optional[str] = None


class AuctionLotItemCreate(AuctionLotItemBase):
    """Schema for creating an auction lot item"""
    pass


class AuctionLotItemUpdate(BaseModel):
    """Schema for updating an auction lot item"""
    item_description: Optional[str] = None
    customer_notified: Optional[bool] = None
    notification_date: Optional[date] = None
    customer_objection: Optional[str] = None


class AuctionLotItemResponse(AuctionLotItemBase):
    """Schema for auction lot item response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AUCTION BID SCHEMAS
# ============================================================================

class AuctionBidBase(BaseModel):
    """Base schema for auction bid"""
    auction_lot_id: UUID
    bidder_id: UUID
    bidder_name: str = Field(..., max_length=100)
    bidder_contact: Optional[str] = Field(None, max_length=20)
    bid_amount: Decimal = Field(..., ge=0, decimal_places=2)
    bid_status: str = Field(default="active", pattern="^(active|accepted|rejected|withdrawn|expired)$")
    bid_type: str = Field(..., pattern="^(online|physical|sealed|proxy)$")
    earnest_money_deposit: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    emd_status: Optional[str] = Field(None, pattern="^(pending|received|verified|refunded|forfeited)$")
    emd_receipt_no: Optional[str] = Field(None, max_length=50)
    bid_rank: Optional[int] = Field(None, ge=1)
    is_winning_bid: bool = False
    rejection_reason: Optional[str] = None


class AuctionBidCreate(AuctionBidBase):
    """Schema for creating an auction bid"""
    pass


class AuctionBidUpdate(BaseModel):
    """Schema for updating an auction bid"""
    bid_status: Optional[str] = Field(None, pattern="^(active|accepted|rejected|withdrawn|expired)$")
    earnest_money_deposit: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    emd_status: Optional[str] = Field(None, pattern="^(pending|received|verified|refunded|forfeited)$")
    emd_receipt_no: Optional[str] = Field(None, max_length=50)
    bid_rank: Optional[int] = Field(None, ge=1)
    is_winning_bid: Optional[bool] = None
    rejection_reason: Optional[str] = None


class AuctionBidResponse(AuctionBidBase):
    """Schema for auction bid response"""
    id: UUID
    bid_number: str
    bid_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COMMUNICATION LOG SCHEMAS
# ============================================================================

class CommunicationLogBase(BaseModel):
    """Base schema for communication log"""
    collection_case_id: UUID
    communication_type: str = Field(..., pattern="^(call|sms|email|whatsapp|letter|telegram)$")
    communication_date: datetime = Field(default_factory=datetime.utcnow)
    direction: str = Field(..., pattern="^(inbound|outbound)$")
    from_party: Optional[str] = Field(None, max_length=100)
    to_party: Optional[str] = Field(None, max_length=100)
    contact_number: Optional[str] = Field(None, max_length=20)
    email_address: Optional[str] = Field(None, max_length=100)
    subject: Optional[str] = Field(None, max_length=200)
    message_content: Optional[str] = None
    communication_status: str = Field(default="sent", pattern="^(draft|sent|delivered|failed|bounced)$")
    delivery_status: Optional[str] = Field(None, pattern="^(pending|delivered|read|failed|undelivered)$")
    response_received: bool = False
    response_content: Optional[str] = None
    response_date: Optional[datetime] = None
    template_used: Optional[str] = Field(None, max_length=100)
    campaign_id: Optional[str] = Field(None, max_length=50)
    initiated_by_user_id: UUID
    cost: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    attachments_count: int = Field(default=0, ge=0)


class CommunicationLogCreate(CommunicationLogBase):
    """Schema for creating a communication log"""
    pass


class CommunicationLogUpdate(BaseModel):
    """Schema for updating a communication log"""
    communication_status: Optional[str] = Field(None, pattern="^(draft|sent|delivered|failed|bounced)$")
    delivery_status: Optional[str] = Field(None, pattern="^(pending|delivered|read|failed|undelivered)$")
    response_received: Optional[bool] = None
    response_content: Optional[str] = None
    response_date: Optional[datetime] = None


class CommunicationLogResponse(CommunicationLogBase):
    """Schema for communication log response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# SETTLEMENT OFFER SCHEMAS
# ============================================================================

class SettlementOfferBase(BaseModel):
    """Base schema for settlement offer"""
    collection_case_id: UUID
    offer_date: date
    offered_by: str = Field(..., pattern="^(customer|company|negotiated)$")
    offer_type: str = Field(..., pattern="^(one_time|installment|partial_waiver|full_waiver|restructure)$")
    total_outstanding: Decimal = Field(..., ge=0, decimal_places=2)
    settlement_amount: Decimal = Field(..., ge=0, decimal_places=2)
    waiver_amount: Decimal = Field(..., ge=0, decimal_places=2)
    waiver_percentage: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    payment_terms: Optional[str] = None
    payment_schedule: Optional[str] = None
    validity_date: date
    offer_status: str = Field(default="pending", pattern="^(pending|approved|rejected|accepted|expired|completed|breached)$")
    approved_by_user_id: Optional[UUID] = None
    approval_level: Optional[str] = Field(None, pattern="^(manager|senior_manager|head|ceo|board)$")
    approval_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    acceptance_date: Optional[date] = None
    agreement_signed: bool = False
    agreement_date: Optional[date] = None
    payment_received: Decimal = Field(default=0, ge=0, decimal_places=2)
    payment_status: str = Field(default="pending", pattern="^(pending|partial|completed|defaulted)$")
    completion_date: Optional[date] = None
    created_by_user_id: UUID


class SettlementOfferCreate(SettlementOfferBase):
    """Schema for creating a settlement offer"""
    pass


class SettlementOfferUpdate(BaseModel):
    """Schema for updating a settlement offer"""
    offer_status: Optional[str] = Field(None, pattern="^(pending|approved|rejected|accepted|expired|completed|breached)$")
    approved_by_user_id: Optional[UUID] = None
    approval_level: Optional[str] = Field(None, pattern="^(manager|senior_manager|head|ceo|board)$")
    approval_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    acceptance_date: Optional[date] = None
    agreement_signed: Optional[bool] = None
    agreement_date: Optional[date] = None
    payment_received: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    payment_status: Optional[str] = Field(None, pattern="^(pending|partial|completed|defaulted)$")
    completion_date: Optional[date] = None


class SettlementOfferResponse(SettlementOfferBase):
    """Schema for settlement offer response"""
    id: UUID
    offer_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COLLECTION PERFORMANCE SCHEMAS
# ============================================================================

class CollectionPerformanceBase(BaseModel):
    """Base schema for collection performance"""
    period_start: date
    period_end: date
    user_id: UUID
    user_name: str = Field(..., max_length=100)
    team_name: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    total_cases_assigned: int = Field(default=0, ge=0)
    total_cases_resolved: int = Field(default=0, ge=0)
    total_cases_escalated: int = Field(default=0, ge=0)
    total_overdue_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    total_collected_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    collection_percentage: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    total_field_visits: int = Field(default=0, ge=0)
    successful_field_visits: int = Field(default=0, ge=0)
    total_calls_made: int = Field(default=0, ge=0)
    contactable_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    promise_kept_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    total_promises_obtained: int = Field(default=0, ge=0)
    promises_kept: int = Field(default=0, ge=0)
    promises_broken: int = Field(default=0, ge=0)
    legal_notices_sent: int = Field(default=0, ge=0)
    recovery_actions_taken: int = Field(default=0, ge=0)
    average_resolution_days: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    bucket_0_30_resolved: int = Field(default=0, ge=0)
    bucket_31_60_resolved: int = Field(default=0, ge=0)
    bucket_61_90_resolved: int = Field(default=0, ge=0)
    bucket_90_plus_resolved: int = Field(default=0, ge=0)
    performance_rating: Optional[str] = Field(None, pattern="^(poor|below_average|average|good|excellent|outstanding)$")
    incentive_earned: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class CollectionPerformanceCreate(CollectionPerformanceBase):
    """Schema for creating collection performance record"""
    pass


class CollectionPerformanceUpdate(BaseModel):
    """Schema for updating collection performance"""
    total_cases_assigned: Optional[int] = Field(None, ge=0)
    total_cases_resolved: Optional[int] = Field(None, ge=0)
    total_cases_escalated: Optional[int] = Field(None, ge=0)
    total_overdue_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    total_collected_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    collection_percentage: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    total_field_visits: Optional[int] = Field(None, ge=0)
    successful_field_visits: Optional[int] = Field(None, ge=0)
    total_calls_made: Optional[int] = Field(None, ge=0)
    contactable_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    promise_kept_rate: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    total_promises_obtained: Optional[int] = Field(None, ge=0)
    promises_kept: Optional[int] = Field(None, ge=0)
    promises_broken: Optional[int] = Field(None, ge=0)
    legal_notices_sent: Optional[int] = Field(None, ge=0)
    recovery_actions_taken: Optional[int] = Field(None, ge=0)
    average_resolution_days: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    bucket_0_30_resolved: Optional[int] = Field(None, ge=0)
    bucket_31_60_resolved: Optional[int] = Field(None, ge=0)
    bucket_61_90_resolved: Optional[int] = Field(None, ge=0)
    bucket_90_plus_resolved: Optional[int] = Field(None, ge=0)
    performance_rating: Optional[str] = Field(None, pattern="^(poor|below_average|average|good|excellent|outstanding)$")
    incentive_earned: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class CollectionPerformanceResponse(CollectionPerformanceBase):
    """Schema for collection performance response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# LIST RESPONSE SCHEMAS
# ============================================================================

class CollectionCaseList(BaseModel):
    """Paginated list of collection cases"""
    items: List[CollectionCaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class FieldVisitList(BaseModel):
    """Paginated list of field visits"""
    items: List[FieldVisitResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuctionLotList(BaseModel):
    """Paginated list of auction lots"""
    items: List[AuctionLotResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# DASHBOARD & STATISTICS SCHEMAS
# ============================================================================

class CollectionDashboard(BaseModel):
    """Collection dashboard statistics"""
    total_cases: int
    open_cases: int
    in_progress_cases: int
    legal_cases: int
    closed_cases: int
    total_outstanding: Decimal
    total_overdue: Decimal
    total_collected: Decimal
    collection_rate: Decimal
    bucket_0_30: int
    bucket_31_60: int
    bucket_61_90: int
    bucket_90_plus: int
    npa_cases: int


class CaseStatistics(BaseModel):
    """Individual case statistics"""
    case_id: UUID
    total_activities: int
    total_field_visits: int
    total_promises: int
    promises_kept: int
    promises_broken: int
    total_legal_notices: int
    total_recovery_actions: int
    days_in_collection: int
    last_activity_date: Optional[date] = None
