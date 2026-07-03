"""
Gold Lending - Collections & Recovery Models
Phase 8: Complete collections, recovery, legal, and auction management
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, Time, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class CollectionCase(Base):
    """Collection case tracking for overdue loans"""
    __tablename__ = "gold_collection_cases"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    loan_account_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_loan_accounts.id"), nullable=False)
    case_number = Column(String(50), unique=True, nullable=False)
    case_status = Column(String(20), nullable=False, default="open")
    bucket_type = Column(String(20), nullable=False)
    overdue_days = Column(Integer, nullable=False)
    overdue_amount = Column(Numeric(15, 2), nullable=False)
    total_outstanding = Column(Numeric(15, 2), nullable=False)
    principal_overdue = Column(Numeric(15, 2), nullable=False)
    interest_overdue = Column(Numeric(15, 2), nullable=False)
    penalty_overdue = Column(Numeric(15, 2), nullable=False)
    assigned_to_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    priority = Column(String(20), nullable=False, default="medium")
    last_contact_date = Column(Date, nullable=True)
    next_action_date = Column(Date, nullable=True)
    closure_reason = Column(Text, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    loan_account = relationship("LoanAccount", back_populates="collection_cases")
    activities = relationship("CollectionActivity", back_populates="collection_case", cascade="all, delete-orphan")
    field_visits = relationship("FieldVisit", back_populates="collection_case", cascade="all, delete-orphan")
    payment_promises = relationship("PaymentPromise", back_populates="collection_case", cascade="all, delete-orphan")
    recovery_actions = relationship("RecoveryAction", back_populates="collection_case", cascade="all, delete-orphan")
    legal_notices = relationship("LegalNotice", back_populates="collection_case", cascade="all, delete-orphan")
    auction_lot_items = relationship("AuctionLotItem", back_populates="collection_case", cascade="all, delete-orphan")
    communication_logs = relationship("CommunicationLog", back_populates="collection_case", cascade="all, delete-orphan")
    settlement_offers = relationship("SettlementOffer", back_populates="collection_case", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            case_status.in_(['open', 'in_progress', 'legal', 'npa', 'closed', 'settled']),
            name="chk_case_status"
        ),
        CheckConstraint(
            bucket_type.in_(['dpd_0_30', 'dpd_31_60', 'dpd_61_90', 'dpd_90_plus', 'npa']),
            name="chk_bucket_type"
        ),
        CheckConstraint(
            priority.in_(['low', 'medium', 'high', 'critical']),
            name="chk_priority"
        ),
    )


class CollectionActivity(Base):
    """Collection follow-up activities and customer interactions"""
    __tablename__ = "gold_collection_activities"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_case_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_collection_cases.id"), nullable=False)
    activity_type = Column(String(30), nullable=False)
    activity_date = Column(Date, nullable=False)
    activity_time = Column(Time, nullable=True)
    contact_mode = Column(String(20), nullable=False)
    contact_person = Column(String(100), nullable=True)
    contact_number = Column(String(20), nullable=True)
    disposition = Column(String(30), nullable=False)
    discussion_summary = Column(Text, nullable=True)
    amount_promised = Column(Numeric(15, 2), nullable=True)
    promise_date = Column(Date, nullable=True)
    next_followup_date = Column(Date, nullable=True)
    performed_by_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    location_lat = Column(Numeric(10, 8), nullable=True)
    location_lon = Column(Numeric(11, 8), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    collection_case = relationship("CollectionCase", back_populates="activities")

    __table_args__ = (
        CheckConstraint(
            activity_type.in_(['call', 'sms', 'email', 'whatsapp', 'field_visit', 'legal_notice', 'payment_received']),
            name="chk_activity_type"
        ),
        CheckConstraint(
            contact_mode.in_(['phone', 'mobile', 'email', 'whatsapp', 'in_person', 'postal']),
            name="chk_contact_mode"
        ),
        CheckConstraint(
            disposition.in_(['contacted', 'not_reachable', 'promised_to_pay', 'partial_payment', 'dispute', 'refused', 'legal_action', 'settled']),
            name="chk_disposition"
        ),
    )



class FieldVisit(Base):
    """Field visit tracking for collection cases"""
    __tablename__ = "gold_field_visits"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_case_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_collection_cases.id"), nullable=False)
    visit_number = Column(String(30), unique=True, nullable=False)
    visit_date = Column(Date, nullable=False)
    visit_time = Column(Time, nullable=True)
    visit_type = Column(String(30), nullable=False)
    visit_purpose = Column(Text, nullable=False)
    visit_status = Column(String(20), nullable=False, default="scheduled")
    field_officer_id = Column(PGUUID(as_uuid=True), nullable=False)
    visit_address = Column(Text, nullable=False)
    location_lat = Column(Numeric(10, 8), nullable=True)
    location_lon = Column(Numeric(11, 8), nullable=True)
    customer_met = Column(Boolean, default=False)
    person_met = Column(String(100), nullable=True)
    person_relation = Column(String(50), nullable=True)
    discussion_summary = Column(Text, nullable=True)
    property_verification = Column(Text, nullable=True)
    collateral_inspection = Column(Text, nullable=True)
    neighborhood_feedback = Column(Text, nullable=True)
    amount_collected = Column(Numeric(15, 2), nullable=True)
    payment_receipt_no = Column(String(50), nullable=True)
    photos_attached = Column(Boolean, default=False)
    visit_outcome = Column(String(30), nullable=True)
    next_visit_date = Column(Date, nullable=True)
    visit_expenses = Column(Numeric(10, 2), nullable=True)
    expense_approved = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    collection_case = relationship("CollectionCase", back_populates="field_visits")

    __table_args__ = (
        CheckConstraint(
            visit_type.in_(['courtesy', 'reminder', 'demand', 'legal', 'repossession', 'verification']),
            name="chk_visit_type"
        ),
        CheckConstraint(
            visit_status.in_(['scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled']),
            name="chk_visit_status"
        ),
        CheckConstraint(
            visit_outcome.in_(['payment_collected', 'promise_obtained', 'customer_absent', 'dispute', 'legal_required', 'settled']),
            name="chk_visit_outcome"
        ),
    )


class PaymentPromise(Base):
    """Customer payment promise tracking"""
    __tablename__ = "gold_payment_promises"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_case_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_collection_cases.id"), nullable=False)
    promise_number = Column(String(30), unique=True, nullable=False)
    promise_date = Column(Date, nullable=False)
    promised_amount = Column(Numeric(15, 2), nullable=False)
    promised_payment_date = Column(Date, nullable=False)
    promise_type = Column(String(20), nullable=False)
    promise_mode = Column(String(20), nullable=True)
    recorded_by_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    recording_channel = Column(String(20), nullable=False)
    promise_status = Column(String(20), nullable=False, default="active")
    amount_received = Column(Numeric(15, 2), default=0)
    payment_date = Column(Date, nullable=True)
    fulfillment_percentage = Column(Numeric(5, 2), nullable=True)
    breach_reason = Column(Text, nullable=True)
    followup_required = Column(Boolean, default=True)
    reminder_sent = Column(Boolean, default=False)
    reminder_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    collection_case = relationship("CollectionCase", back_populates="payment_promises")

    __table_args__ = (
        CheckConstraint(
            promise_type.in_(['full', 'partial', 'installment', 'settlement']),
            name="chk_promise_type"
        ),
        CheckConstraint(
            promise_mode.in_(['cash', 'cheque', 'online', 'card', 'ecs']),
            name="chk_promise_mode"
        ),
        CheckConstraint(
            promise_status.in_(['active', 'kept', 'broken', 'partial', 'cancelled']),
            name="chk_promise_status"
        ),
        CheckConstraint(
            recording_channel.in_(['phone', 'field_visit', 'email', 'whatsapp', 'in_branch']),
            name="chk_recording_channel"
        ),
    )


class RecoveryAction(Base):
    """Recovery and repossession action tracking"""
    __tablename__ = "gold_recovery_actions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_case_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_collection_cases.id"), nullable=False)
    action_number = Column(String(30), unique=True, nullable=False)
    action_type = Column(String(30), nullable=False)
    action_date = Column(Date, nullable=False)
    action_status = Column(String(20), nullable=False, default="planned")
    initiated_by_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    approved_by_user_id = Column(PGUUID(as_uuid=True), nullable=True)
    approval_date = Column(Date, nullable=True)
    action_description = Column(Text, nullable=False)
    legal_basis = Column(Text, nullable=True)
    notice_period_days = Column(Integer, nullable=True)
    notice_sent_date = Column(Date, nullable=True)
    action_location = Column(Text, nullable=True)
    recovery_team = Column(Text, nullable=True)
    assets_recovered = Column(Text, nullable=True)
    estimated_value = Column(Numeric(15, 2), nullable=True)
    actual_value = Column(Numeric(15, 2), nullable=True)
    custody_location = Column(String(200), nullable=True)
    custody_person = Column(String(100), nullable=True)
    police_assistance = Column(Boolean, default=False)
    police_station = Column(String(100), nullable=True)
    fir_number = Column(String(50), nullable=True)
    customer_response = Column(Text, nullable=True)
    completion_date = Column(Date, nullable=True)
    expenses_incurred = Column(Numeric(10, 2), nullable=True)
    outcome = Column(String(30), nullable=True)
    photos_attached = Column(Boolean, default=False)
    documents_attached = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    collection_case = relationship("CollectionCase", back_populates="recovery_actions")

    __table_args__ = (
        CheckConstraint(
            action_type.in_(['reminder', 'notice', 'repossession', 'seizure', 'auction_prep', 'legal_filing', 'settlement']),
            name="chk_action_type"
        ),
        CheckConstraint(
            action_status.in_(['planned', 'approved', 'in_progress', 'completed', 'cancelled', 'failed']),
            name="chk_action_status"
        ),
        CheckConstraint(
            outcome.in_(['successful', 'partial', 'failed', 'disputed', 'legal_challenge', 'settled']),
            name="chk_outcome"
        ),
    )



class LegalNotice(Base):
    """Legal notice and demand letter management"""
    __tablename__ = "gold_legal_notices"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_case_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_collection_cases.id"), nullable=False)
    notice_number = Column(String(50), unique=True, nullable=False)
    notice_type = Column(String(30), nullable=False)
    notice_date = Column(Date, nullable=False)
    notice_status = Column(String(20), nullable=False, default="draft")
    issued_by_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    approved_by_user_id = Column(PGUUID(as_uuid=True), nullable=True)
    approval_date = Column(Date, nullable=True)
    legal_firm = Column(String(200), nullable=True)
    lawyer_name = Column(String(100), nullable=True)
    lawyer_contact = Column(String(20), nullable=True)
    notice_subject = Column(Text, nullable=False)
    notice_content = Column(Text, nullable=False)
    demand_amount = Column(Numeric(15, 2), nullable=False)
    response_deadline = Column(Date, nullable=False)
    delivery_mode = Column(String(20), nullable=False)
    delivery_date = Column(Date, nullable=True)
    tracking_number = Column(String(50), nullable=True)
    delivery_status = Column(String(20), nullable=True)
    acknowledgment_received = Column(Boolean, default=False)
    acknowledgment_date = Column(Date, nullable=True)
    customer_response = Column(Text, nullable=True)
    response_date = Column(Date, nullable=True)
    response_type = Column(String(30), nullable=True)
    followup_required = Column(Boolean, default=True)
    next_action = Column(String(30), nullable=True)
    next_action_date = Column(Date, nullable=True)
    legal_expenses = Column(Numeric(10, 2), nullable=True)
    documents_attached = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    collection_case = relationship("CollectionCase", back_populates="legal_notices")

    __table_args__ = (
        CheckConstraint(
            notice_type.in_(['reminder', 'demand', 'final_demand', 'legal_action', 'arbitration', 'suit_filing', 'auction_notice']),
            name="chk_notice_type"
        ),
        CheckConstraint(
            notice_status.in_(['draft', 'approved', 'issued', 'delivered', 'acknowledged', 'responded', 'expired']),
            name="chk_notice_status"
        ),
        CheckConstraint(
            delivery_mode.in_(['registered_post', 'courier', 'hand_delivery', 'email', 'publication']),
            name="chk_delivery_mode"
        ),
        CheckConstraint(
            delivery_status.in_(['pending', 'in_transit', 'delivered', 'refused', 'unclaimed', 'returned']),
            name="chk_delivery_status"
        ),
        CheckConstraint(
            response_type.in_(['payment', 'partial_payment', 'dispute', 'settlement_offer', 'legal_challenge', 'no_response']),
            name="chk_response_type"
        ),
    )


class AuctionLot(Base):
    """Auction lot management for recovered collateral"""
    __tablename__ = "gold_auction_lots"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    lot_number = Column(String(50), unique=True, nullable=False)
    auction_date = Column(Date, nullable=False)
    auction_location = Column(String(200), nullable=False)
    lot_status = Column(String(20), nullable=False, default="planned")
    lot_description = Column(Text, nullable=False)
    total_gold_weight = Column(Numeric(10, 3), nullable=False)
    total_items = Column(Integer, nullable=False)
    reserve_price = Column(Numeric(15, 2), nullable=False)
    starting_bid = Column(Numeric(15, 2), nullable=False)
    bid_increment = Column(Numeric(10, 2), nullable=False)
    registration_deadline = Column(Date, nullable=False)
    auction_start_time = Column(Time, nullable=True)
    auction_end_time = Column(Time, nullable=True)
    auction_type = Column(String(20), nullable=False)
    auctioneer_name = Column(String(100), nullable=True)
    auctioneer_license = Column(String(50), nullable=True)
    winning_bid_amount = Column(Numeric(15, 2), nullable=True)
    winning_bidder_id = Column(PGUUID(as_uuid=True), nullable=True)
    bid_count = Column(Integer, default=0)
    payment_deadline = Column(Date, nullable=True)
    payment_received = Column(Boolean, default=False)
    payment_date = Column(Date, nullable=True)
    handover_date = Column(Date, nullable=True)
    handover_completed = Column(Boolean, default=False)
    auction_expenses = Column(Numeric(10, 2), nullable=True)
    net_realization = Column(Numeric(15, 2), nullable=True)
    created_by_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    approved_by_user_id = Column(PGUUID(as_uuid=True), nullable=True)
    approval_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lot_items = relationship("AuctionLotItem", back_populates="auction_lot", cascade="all, delete-orphan")
    bids = relationship("AuctionBid", back_populates="auction_lot", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            lot_status.in_(['planned', 'approved', 'advertised', 'open', 'closed', 'sold', 'unsold', 'cancelled']),
            name="chk_lot_status"
        ),
        CheckConstraint(
            auction_type.in_(['public', 'private', 'online', 'sealed_bid', 'spot_sale']),
            name="chk_auction_type"
        ),
    )


class AuctionLotItem(Base):
    """Individual items within auction lots"""
    __tablename__ = "gold_auction_lot_items"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    auction_lot_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_auction_lots.id"), nullable=False)
    collection_case_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_collection_cases.id"), nullable=False)
    loan_account_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_loan_accounts.id"), nullable=False)
    item_number = Column(Integer, nullable=False)
    item_description = Column(Text, nullable=True)
    gold_weight = Column(Numeric(10, 3), nullable=False)
    gold_purity = Column(Numeric(5, 2), nullable=False)
    estimated_value = Column(Numeric(15, 2), nullable=False)
    customer_notified = Column(Boolean, default=False)
    notification_date = Column(Date, nullable=True)
    customer_objection = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    auction_lot = relationship("AuctionLot", back_populates="lot_items")
    collection_case = relationship("CollectionCase", back_populates="auction_lot_items")
    loan_account = relationship("LoanAccount", back_populates="auction_lot_items")

    __table_args__ = (
        UniqueConstraint('auction_lot_id', 'item_number', name='uq_lot_item'),
    )


class AuctionBid(Base):
    """Auction bid tracking"""
    __tablename__ = "gold_auction_bids"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    auction_lot_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_auction_lots.id"), nullable=False)
    bid_number = Column(String(30), unique=True, nullable=False)
    bidder_id = Column(PGUUID(as_uuid=True), nullable=False)
    bidder_name = Column(String(100), nullable=False)
    bidder_contact = Column(String(20), nullable=True)
    bid_amount = Column(Numeric(15, 2), nullable=False)
    bid_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    bid_status = Column(String(20), nullable=False, default="active")
    bid_type = Column(String(20), nullable=False)
    earnest_money_deposit = Column(Numeric(15, 2), nullable=True)
    emd_status = Column(String(20), nullable=True)
    emd_receipt_no = Column(String(50), nullable=True)
    bid_rank = Column(Integer, nullable=True)
    is_winning_bid = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    auction_lot = relationship("AuctionLot", back_populates="bids")

    __table_args__ = (
        CheckConstraint(
            bid_status.in_(['active', 'accepted', 'rejected', 'withdrawn', 'expired']),
            name="chk_bid_status"
        ),
        CheckConstraint(
            bid_type.in_(['online', 'physical', 'sealed', 'proxy']),
            name="chk_bid_type"
        ),
        CheckConstraint(
            emd_status.in_(['pending', 'received', 'verified', 'refunded', 'forfeited']),
            name="chk_emd_status"
        ),
    )



class CommunicationLog(Base):
    """Communication history for collection cases"""
    __tablename__ = "gold_communication_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_case_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_collection_cases.id"), nullable=False)
    communication_type = Column(String(20), nullable=False)
    communication_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    direction = Column(String(10), nullable=False)
    from_party = Column(String(100), nullable=True)
    to_party = Column(String(100), nullable=True)
    contact_number = Column(String(20), nullable=True)
    email_address = Column(String(100), nullable=True)
    subject = Column(String(200), nullable=True)
    message_content = Column(Text, nullable=True)
    communication_status = Column(String(20), nullable=False, default="sent")
    delivery_status = Column(String(20), nullable=True)
    response_received = Column(Boolean, default=False)
    response_content = Column(Text, nullable=True)
    response_date = Column(DateTime, nullable=True)
    template_used = Column(String(100), nullable=True)
    campaign_id = Column(String(50), nullable=True)
    initiated_by_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    cost = Column(Numeric(8, 2), nullable=True)
    attachments_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    collection_case = relationship("CollectionCase", back_populates="communication_logs")

    __table_args__ = (
        CheckConstraint(
            communication_type.in_(['call', 'sms', 'email', 'whatsapp', 'letter', 'telegram']),
            name="chk_communication_type"
        ),
        CheckConstraint(
            direction.in_(['inbound', 'outbound']),
            name="chk_direction"
        ),
        CheckConstraint(
            communication_status.in_(['draft', 'sent', 'delivered', 'failed', 'bounced']),
            name="chk_communication_status"
        ),
        CheckConstraint(
            delivery_status.in_(['pending', 'delivered', 'read', 'failed', 'undelivered']),
            name="chk_delivery_status"
        ),
    )


class SettlementOffer(Base):
    """Settlement negotiation and offer tracking"""
    __tablename__ = "gold_settlement_offers"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_case_id = Column(PGUUID(as_uuid=True), ForeignKey("gold_collection_cases.id"), nullable=False)
    offer_number = Column(String(30), unique=True, nullable=False)
    offer_date = Column(Date, nullable=False)
    offered_by = Column(String(20), nullable=False)
    offer_type = Column(String(20), nullable=False)
    total_outstanding = Column(Numeric(15, 2), nullable=False)
    settlement_amount = Column(Numeric(15, 2), nullable=False)
    waiver_amount = Column(Numeric(15, 2), nullable=False)
    waiver_percentage = Column(Numeric(5, 2), nullable=True)
    payment_terms = Column(Text, nullable=True)
    payment_schedule = Column(Text, nullable=True)
    validity_date = Column(Date, nullable=False)
    offer_status = Column(String(20), nullable=False, default="pending")
    approved_by_user_id = Column(PGUUID(as_uuid=True), nullable=True)
    approval_level = Column(String(20), nullable=True)
    approval_date = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    acceptance_date = Column(Date, nullable=True)
    agreement_signed = Column(Boolean, default=False)
    agreement_date = Column(Date, nullable=True)
    payment_received = Column(Numeric(15, 2), default=0)
    payment_status = Column(String(20), default="pending")
    completion_date = Column(Date, nullable=True)
    created_by_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    collection_case = relationship("CollectionCase", back_populates="settlement_offers")

    __table_args__ = (
        CheckConstraint(
            offered_by.in_(['customer', 'company', 'negotiated']),
            name="chk_offered_by"
        ),
        CheckConstraint(
            offer_type.in_(['one_time', 'installment', 'partial_waiver', 'full_waiver', 'restructure']),
            name="chk_offer_type"
        ),
        CheckConstraint(
            offer_status.in_(['pending', 'approved', 'rejected', 'accepted', 'expired', 'completed', 'breached']),
            name="chk_offer_status"
        ),
        CheckConstraint(
            approval_level.in_(['manager', 'senior_manager', 'head', 'ceo', 'board']),
            name="chk_approval_level"
        ),
        CheckConstraint(
            payment_status.in_(['pending', 'partial', 'completed', 'defaulted']),
            name="chk_payment_status"
        ),
    )


class CollectionPerformance(Base):
    """Collection team performance metrics"""
    __tablename__ = "gold_collection_performance"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    user_name = Column(String(100), nullable=False)
    team_name = Column(String(100), nullable=True)
    region = Column(String(50), nullable=True)
    total_cases_assigned = Column(Integer, default=0)
    total_cases_resolved = Column(Integer, default=0)
    total_cases_escalated = Column(Integer, default=0)
    total_overdue_amount = Column(Numeric(15, 2), default=0)
    total_collected_amount = Column(Numeric(15, 2), default=0)
    collection_percentage = Column(Numeric(5, 2), nullable=True)
    total_field_visits = Column(Integer, default=0)
    successful_field_visits = Column(Integer, default=0)
    total_calls_made = Column(Integer, default=0)
    contactable_rate = Column(Numeric(5, 2), nullable=True)
    promise_kept_rate = Column(Numeric(5, 2), nullable=True)
    total_promises_obtained = Column(Integer, default=0)
    promises_kept = Column(Integer, default=0)
    promises_broken = Column(Integer, default=0)
    legal_notices_sent = Column(Integer, default=0)
    recovery_actions_taken = Column(Integer, default=0)
    average_resolution_days = Column(Numeric(8, 2), nullable=True)
    bucket_0_30_resolved = Column(Integer, default=0)
    bucket_31_60_resolved = Column(Integer, default=0)
    bucket_61_90_resolved = Column(Integer, default=0)
    bucket_90_plus_resolved = Column(Integer, default=0)
    performance_rating = Column(String(20), nullable=True)
    incentive_earned = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            performance_rating.in_(['poor', 'below_average', 'average', 'good', 'excellent', 'outstanding']),
            name="chk_performance_rating"
        ),
        UniqueConstraint('user_id', 'period_start', 'period_end', name='uq_performance_period'),
    )
