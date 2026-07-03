-- ============================================================================
-- Phase 8: Collections & Recovery Management
-- ============================================================================
-- Description: Complete collections and recovery system with overdue management,
--              field visits, payment promises, recovery actions, legal notices,
--              auction management, and communication tracking
-- Version: 1.0
-- Date: 2026-07-03
-- ============================================================================

-- ============================================================================
-- 1. COLLECTION CASES
-- ============================================================================
-- Tracks overdue loans under collection management
CREATE TABLE gold_collection_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id),
    case_number VARCHAR(50) NOT NULL UNIQUE,
    case_status VARCHAR(20) NOT NULL DEFAULT 'open',
    bucket_type VARCHAR(20) NOT NULL, -- dpd_0_30, dpd_31_60, dpd_61_90, dpd_90_plus
    overdue_days INTEGER NOT NULL,
    overdue_amount DECIMAL(15,2) NOT NULL,
    total_outstanding DECIMAL(15,2) NOT NULL,
    principal_overdue DECIMAL(15,2) NOT NULL,
    interest_overdue DECIMAL(15,2) NOT NULL,
    penalty_overdue DECIMAL(15,2) NOT NULL,
    assigned_to_user_id UUID NOT NULL,
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    last_contact_date DATE,
    next_action_date DATE,
    closure_reason TEXT,
    closed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_case_status CHECK (case_status IN ('open', 'in_progress', 'legal', 'npa', 'closed', 'settled')),
    CONSTRAINT chk_bucket_type CHECK (bucket_type IN ('dpd_0_30', 'dpd_31_60', 'dpd_61_90', 'dpd_90_plus', 'npa')),
    CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high', 'critical'))
);

CREATE INDEX idx_collection_cases_loan ON gold_collection_cases(loan_account_id);
CREATE INDEX idx_collection_cases_status ON gold_collection_cases(case_status);
CREATE INDEX idx_collection_cases_assigned ON gold_collection_cases(assigned_to_user_id);
CREATE INDEX idx_collection_cases_bucket ON gold_collection_cases(bucket_type);
CREATE INDEX idx_collection_cases_priority ON gold_collection_cases(priority);

COMMENT ON TABLE gold_collection_cases IS 'Collection cases for overdue loan management';


-- ============================================================================
-- 2. COLLECTION ACTIVITIES
-- ============================================================================
-- Tracks all collection activities and follow-ups
CREATE TABLE gold_collection_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    activity_type VARCHAR(30) NOT NULL,
    activity_date DATE NOT NULL,
    activity_time TIME,
    contact_mode VARCHAR(20) NOT NULL,
    contact_person VARCHAR(100),
    contact_number VARCHAR(20),
    disposition VARCHAR(30) NOT NULL,
    discussion_summary TEXT,
    amount_promised DECIMAL(15,2),
    promise_date DATE,
    next_followup_date DATE,
    performed_by_user_id UUID NOT NULL,
    location_lat DECIMAL(10,8),
    location_lon DECIMAL(11,8),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_activity_type CHECK (activity_type IN ('call', 'sms', 'email', 'whatsapp', 'field_visit', 'legal_notice', 'payment_received')),
    CONSTRAINT chk_contact_mode CHECK (contact_mode IN ('phone', 'mobile', 'email', 'whatsapp', 'in_person', 'postal')),
    CONSTRAINT chk_disposition CHECK (disposition IN ('contacted', 'not_reachable', 'promised_to_pay', 'partial_payment', 'dispute', 'refused', 'legal_action', 'settled'))
);

CREATE INDEX idx_collection_activities_case ON gold_collection_activities(collection_case_id);
CREATE INDEX idx_collection_activities_date ON gold_collection_activities(activity_date);
CREATE INDEX idx_collection_activities_type ON gold_collection_activities(activity_type);
CREATE INDEX idx_collection_activities_user ON gold_collection_activities(performed_by_user_id);

COMMENT ON TABLE gold_collection_activities IS 'All collection follow-up activities and customer interactions';

-- ============================================================================
-- 3. FIELD VISITS
-- ============================================================================
-- Tracks field visits to customer locations
CREATE TABLE gold_field_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    visit_number VARCHAR(30) NOT NULL UNIQUE,
    visit_date DATE NOT NULL,
    visit_time TIME,
    visit_type VARCHAR(30) NOT NULL,
    visit_purpose TEXT NOT NULL,
    visit_status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    field_officer_id UUID NOT NULL,
    visit_address TEXT NOT NULL,
    location_lat DECIMAL(10,8),
    location_lon DECIMAL(11,8),
    customer_met BOOLEAN DEFAULT false,
    person_met VARCHAR(100),
    person_relation VARCHAR(50),
    discussion_summary TEXT,
    property_verification TEXT,
    collateral_inspection TEXT,
    neighborhood_feedback TEXT,
    amount_collected DECIMAL(15,2),
    payment_receipt_no VARCHAR(50),
    photos_attached BOOLEAN DEFAULT false,
    visit_outcome VARCHAR(30),
    next_visit_date DATE,
    visit_expenses DECIMAL(10,2),
    expense_approved BOOLEAN DEFAULT false,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_visit_type CHECK (visit_type IN ('courtesy', 'reminder', 'demand', 'legal', 'repossession', 'verification')),
    CONSTRAINT chk_visit_status CHECK (visit_status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled')),
    CONSTRAINT chk_visit_outcome CHECK (visit_outcome IN ('payment_collected', 'promise_obtained', 'customer_absent', 'dispute', 'legal_required', 'settled'))
);

CREATE INDEX idx_field_visits_case ON gold_field_visits(collection_case_id);
CREATE INDEX idx_field_visits_date ON gold_field_visits(visit_date);
CREATE INDEX idx_field_visits_status ON gold_field_visits(visit_status);
CREATE INDEX idx_field_visits_officer ON gold_field_visits(field_officer_id);

COMMENT ON TABLE gold_field_visits IS 'Field visit tracking for collection cases';


-- ============================================================================
-- 4. PAYMENT PROMISES
-- ============================================================================
-- Tracks customer payment promises and commitments
CREATE TABLE gold_payment_promises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    promise_number VARCHAR(30) NOT NULL UNIQUE,
    promise_date DATE NOT NULL,
    promised_amount DECIMAL(15,2) NOT NULL,
    promised_payment_date DATE NOT NULL,
    promise_type VARCHAR(20) NOT NULL,
    promise_mode VARCHAR(20),
    recorded_by_user_id UUID NOT NULL,
    recording_channel VARCHAR(20) NOT NULL,
    promise_status VARCHAR(20) NOT NULL DEFAULT 'active',
    amount_received DECIMAL(15,2) DEFAULT 0,
    payment_date DATE,
    fulfillment_percentage DECIMAL(5,2),
    breach_reason TEXT,
    followup_required BOOLEAN DEFAULT true,
    reminder_sent BOOLEAN DEFAULT false,
    reminder_date DATE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_promise_type CHECK (promise_type IN ('full', 'partial', 'installment', 'settlement')),
    CONSTRAINT chk_promise_mode CHECK (promise_mode IN ('cash', 'cheque', 'online', 'card', 'ecs')),
    CONSTRAINT chk_promise_status CHECK (promise_status IN ('active', 'kept', 'broken', 'partial', 'cancelled')),
    CONSTRAINT chk_recording_channel CHECK (recording_channel IN ('phone', 'field_visit', 'email', 'whatsapp', 'in_branch'))
);

CREATE INDEX idx_payment_promises_case ON gold_payment_promises(collection_case_id);
CREATE INDEX idx_payment_promises_date ON gold_payment_promises(promised_payment_date);
CREATE INDEX idx_payment_promises_status ON gold_payment_promises(promise_status);
CREATE INDEX idx_payment_promises_user ON gold_payment_promises(recorded_by_user_id);

COMMENT ON TABLE gold_payment_promises IS 'Customer payment promises and commitment tracking';


-- ============================================================================
-- 5. RECOVERY ACTIONS
-- ============================================================================
-- Tracks recovery and repossession actions
CREATE TABLE gold_recovery_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    action_number VARCHAR(30) NOT NULL UNIQUE,
    action_type VARCHAR(30) NOT NULL,
    action_date DATE NOT NULL,
    action_status VARCHAR(20) NOT NULL DEFAULT 'planned',
    initiated_by_user_id UUID NOT NULL,
    approved_by_user_id UUID,
    approval_date DATE,
    action_description TEXT NOT NULL,
    legal_basis TEXT,
    notice_period_days INTEGER,
    notice_sent_date DATE,
    action_location TEXT,
    recovery_team TEXT,
    assets_recovered TEXT,
    estimated_value DECIMAL(15,2),
    actual_value DECIMAL(15,2),
    custody_location VARCHAR(200),
    custody_person VARCHAR(100),
    police_assistance BOOLEAN DEFAULT false,
    police_station VARCHAR(100),
    fir_number VARCHAR(50),
    customer_response TEXT,
    completion_date DATE,
    expenses_incurred DECIMAL(10,2),
    outcome VARCHAR(30),
    photos_attached BOOLEAN DEFAULT false,
    documents_attached BOOLEAN DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_action_type CHECK (action_type IN ('reminder', 'notice', 'repossession', 'seizure', 'auction_prep', 'legal_filing', 'settlement')),
    CONSTRAINT chk_action_status CHECK (action_status IN ('planned', 'approved', 'in_progress', 'completed', 'cancelled', 'failed')),
    CONSTRAINT chk_outcome CHECK (outcome IN ('successful', 'partial', 'failed', 'disputed', 'legal_challenge', 'settled'))
);

CREATE INDEX idx_recovery_actions_case ON gold_recovery_actions(collection_case_id);
CREATE INDEX idx_recovery_actions_date ON gold_recovery_actions(action_date);
CREATE INDEX idx_recovery_actions_status ON gold_recovery_actions(action_status);
CREATE INDEX idx_recovery_actions_type ON gold_recovery_actions(action_type);

COMMENT ON TABLE gold_recovery_actions IS 'Recovery and repossession action tracking';


-- ============================================================================
-- 6. LEGAL NOTICES
-- ============================================================================
-- Tracks legal notices and demand letters
CREATE TABLE gold_legal_notices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    notice_number VARCHAR(50) NOT NULL UNIQUE,
    notice_type VARCHAR(30) NOT NULL,
    notice_date DATE NOT NULL,
    notice_status VARCHAR(20) NOT NULL DEFAULT 'draft',
    issued_by_user_id UUID NOT NULL,
    approved_by_user_id UUID,
    approval_date DATE,
    legal_firm VARCHAR(200),
    lawyer_name VARCHAR(100),
    lawyer_contact VARCHAR(20),
    notice_subject TEXT NOT NULL,
    notice_content TEXT NOT NULL,
    demand_amount DECIMAL(15,2) NOT NULL,
    response_deadline DATE NOT NULL,
    delivery_mode VARCHAR(20) NOT NULL,
    delivery_date DATE,
    tracking_number VARCHAR(50),
    delivery_status VARCHAR(20),
    acknowledgment_received BOOLEAN DEFAULT false,
    acknowledgment_date DATE,
    customer_response TEXT,
    response_date DATE,
    response_type VARCHAR(30),
    followup_required BOOLEAN DEFAULT true,
    next_action VARCHAR(30),
    next_action_date DATE,
    legal_expenses DECIMAL(10,2),
    documents_attached BOOLEAN DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_notice_type CHECK (notice_type IN ('reminder', 'demand', 'final_demand', 'legal_action', 'arbitration', 'suit_filing', 'auction_notice')),
    CONSTRAINT chk_notice_status CHECK (notice_status IN ('draft', 'approved', 'issued', 'delivered', 'acknowledged', 'responded', 'expired')),
    CONSTRAINT chk_delivery_mode CHECK (delivery_mode IN ('registered_post', 'courier', 'hand_delivery', 'email', 'publication')),
    CONSTRAINT chk_delivery_status CHECK (delivery_status IN ('pending', 'in_transit', 'delivered', 'refused', 'unclaimed', 'returned')),
    CONSTRAINT chk_response_type CHECK (response_type IN ('payment', 'partial_payment', 'dispute', 'settlement_offer', 'legal_challenge', 'no_response'))
);

CREATE INDEX idx_legal_notices_case ON gold_legal_notices(collection_case_id);
CREATE INDEX idx_legal_notices_date ON gold_legal_notices(notice_date);
CREATE INDEX idx_legal_notices_status ON gold_legal_notices(notice_status);
CREATE INDEX idx_legal_notices_type ON gold_legal_notices(notice_type);

COMMENT ON TABLE gold_legal_notices IS 'Legal notices and demand letter management';


-- ============================================================================
-- 7. AUCTION LOTS
-- ============================================================================
-- Tracks gold auction lots for recovered collateral
CREATE TABLE gold_auction_lots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lot_number VARCHAR(50) NOT NULL UNIQUE,
    auction_date DATE NOT NULL,
    auction_location VARCHAR(200) NOT NULL,
    lot_status VARCHAR(20) NOT NULL DEFAULT 'planned',
    lot_description TEXT NOT NULL,
    total_gold_weight DECIMAL(10,3) NOT NULL,
    total_items INTEGER NOT NULL,
    reserve_price DECIMAL(15,2) NOT NULL,
    starting_bid DECIMAL(15,2) NOT NULL,
    bid_increment DECIMAL(10,2) NOT NULL,
    registration_deadline DATE NOT NULL,
    auction_start_time TIME,
    auction_end_time TIME,
    auction_type VARCHAR(20) NOT NULL,
    auctioneer_name VARCHAR(100),
    auctioneer_license VARCHAR(50),
    winning_bid_amount DECIMAL(15,2),
    winning_bidder_id UUID,
    bid_count INTEGER DEFAULT 0,
    payment_deadline DATE,
    payment_received BOOLEAN DEFAULT false,
    payment_date DATE,
    handover_date DATE,
    handover_completed BOOLEAN DEFAULT false,
    auction_expenses DECIMAL(10,2),
    net_realization DECIMAL(15,2),
    created_by_user_id UUID NOT NULL,
    approved_by_user_id UUID,
    approval_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_lot_status CHECK (lot_status IN ('planned', 'approved', 'advertised', 'open', 'closed', 'sold', 'unsold', 'cancelled')),
    CONSTRAINT chk_auction_type CHECK (auction_type IN ('public', 'private', 'online', 'sealed_bid', 'spot_sale'))
);

CREATE INDEX idx_auction_lots_date ON gold_auction_lots(auction_date);
CREATE INDEX idx_auction_lots_status ON gold_auction_lots(lot_status);
CREATE INDEX idx_auction_lots_type ON gold_auction_lots(auction_type);

COMMENT ON TABLE gold_auction_lots IS 'Auction lot management for recovered gold collateral';


-- ============================================================================
-- 8. AUCTION LOT ITEMS
-- ============================================================================
-- Links collection cases to auction lots
CREATE TABLE gold_auction_lot_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auction_lot_id UUID NOT NULL REFERENCES gold_auction_lots(id),
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id),
    item_number INTEGER NOT NULL,
    item_description TEXT,
    gold_weight DECIMAL(10,3) NOT NULL,
    gold_purity DECIMAL(5,2) NOT NULL,
    estimated_value DECIMAL(15,2) NOT NULL,
    customer_notified BOOLEAN DEFAULT false,
    notification_date DATE,
    customer_objection TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_lot_item UNIQUE (auction_lot_id, item_number)
);

CREATE INDEX idx_auction_lot_items_lot ON gold_auction_lot_items(auction_lot_id);
CREATE INDEX idx_auction_lot_items_case ON gold_auction_lot_items(collection_case_id);
CREATE INDEX idx_auction_lot_items_loan ON gold_auction_lot_items(loan_account_id);

COMMENT ON TABLE gold_auction_lot_items IS 'Individual items within auction lots';


-- ============================================================================
-- 9. AUCTION BIDS
-- ============================================================================
-- Tracks bids received during auctions
CREATE TABLE gold_auction_bids (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auction_lot_id UUID NOT NULL REFERENCES gold_auction_lots(id),
    bid_number VARCHAR(30) NOT NULL UNIQUE,
    bidder_id UUID NOT NULL,
    bidder_name VARCHAR(100) NOT NULL,
    bidder_contact VARCHAR(20),
    bid_amount DECIMAL(15,2) NOT NULL,
    bid_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    bid_status VARCHAR(20) NOT NULL DEFAULT 'active',
    bid_type VARCHAR(20) NOT NULL,
    earnest_money_deposit DECIMAL(15,2),
    emd_status VARCHAR(20),
    emd_receipt_no VARCHAR(50),
    bid_rank INTEGER,
    is_winning_bid BOOLEAN DEFAULT false,
    rejection_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_bid_status CHECK (bid_status IN ('active', 'accepted', 'rejected', 'withdrawn', 'expired')),
    CONSTRAINT chk_bid_type CHECK (bid_type IN ('online', 'physical', 'sealed', 'proxy')),
    CONSTRAINT chk_emd_status CHECK (emd_status IN ('pending', 'received', 'verified', 'refunded', 'forfeited'))
);

CREATE INDEX idx_auction_bids_lot ON gold_auction_bids(auction_lot_id);
CREATE INDEX idx_auction_bids_bidder ON gold_auction_bids(bidder_id);
CREATE INDEX idx_auction_bids_status ON gold_auction_bids(bid_status);
CREATE INDEX idx_auction_bids_time ON gold_auction_bids(bid_time);

COMMENT ON TABLE gold_auction_bids IS 'Auction bid tracking and management';


-- ============================================================================
-- 10. COMMUNICATION LOGS
-- ============================================================================
-- Comprehensive communication history for collection cases
CREATE TABLE gold_communication_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    communication_type VARCHAR(20) NOT NULL,
    communication_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    direction VARCHAR(10) NOT NULL,
    from_party VARCHAR(100),
    to_party VARCHAR(100),
    contact_number VARCHAR(20),
    email_address VARCHAR(100),
    subject VARCHAR(200),
    message_content TEXT,
    communication_status VARCHAR(20) NOT NULL DEFAULT 'sent',
    delivery_status VARCHAR(20),
    response_received BOOLEAN DEFAULT false,
    response_content TEXT,
    response_date TIMESTAMP,
    template_used VARCHAR(100),
    campaign_id VARCHAR(50),
    initiated_by_user_id UUID NOT NULL,
    cost DECIMAL(8,2),
    attachments_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_communication_type CHECK (communication_type IN ('call', 'sms', 'email', 'whatsapp', 'letter', 'telegram')),
    CONSTRAINT chk_direction CHECK (direction IN ('inbound', 'outbound')),
    CONSTRAINT chk_communication_status CHECK (communication_status IN ('draft', 'sent', 'delivered', 'failed', 'bounced')),
    CONSTRAINT chk_delivery_status CHECK (delivery_status IN ('pending', 'delivered', 'read', 'failed', 'undelivered'))
);

CREATE INDEX idx_communication_logs_case ON gold_communication_logs(collection_case_id);
CREATE INDEX idx_communication_logs_date ON gold_communication_logs(communication_date);
CREATE INDEX idx_communication_logs_type ON gold_communication_logs(communication_type);
CREATE INDEX idx_communication_logs_status ON gold_communication_logs(communication_status);

COMMENT ON TABLE gold_communication_logs IS 'Complete communication history for collection cases';


-- ============================================================================
-- 11. SETTLEMENT OFFERS
-- ============================================================================
-- Tracks settlement negotiations and offers
CREATE TABLE gold_settlement_offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    offer_number VARCHAR(30) NOT NULL UNIQUE,
    offer_date DATE NOT NULL,
    offered_by VARCHAR(20) NOT NULL,
    offer_type VARCHAR(20) NOT NULL,
    total_outstanding DECIMAL(15,2) NOT NULL,
    settlement_amount DECIMAL(15,2) NOT NULL,
    waiver_amount DECIMAL(15,2) NOT NULL,
    waiver_percentage DECIMAL(5,2),
    payment_terms TEXT,
    payment_schedule TEXT,
    validity_date DATE NOT NULL,
    offer_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    approved_by_user_id UUID,
    approval_level VARCHAR(20),
    approval_date DATE,
    rejection_reason TEXT,
    acceptance_date DATE,
    agreement_signed BOOLEAN DEFAULT false,
    agreement_date DATE,
    payment_received DECIMAL(15,2) DEFAULT 0,
    payment_status VARCHAR(20) DEFAULT 'pending',
    completion_date DATE,
    created_by_user_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_offered_by CHECK (offered_by IN ('customer', 'company', 'negotiated')),
    CONSTRAINT chk_offer_type CHECK (offer_type IN ('one_time', 'installment', 'partial_waiver', 'full_waiver', 'restructure')),
    CONSTRAINT chk_offer_status CHECK (offer_status IN ('pending', 'approved', 'rejected', 'accepted', 'expired', 'completed', 'breached')),
    CONSTRAINT chk_approval_level CHECK (approval_level IN ('manager', 'senior_manager', 'head', 'ceo', 'board')),
    CONSTRAINT chk_payment_status CHECK (payment_status IN ('pending', 'partial', 'completed', 'defaulted'))
);

CREATE INDEX idx_settlement_offers_case ON gold_settlement_offers(collection_case_id);
CREATE INDEX idx_settlement_offers_date ON gold_settlement_offers(offer_date);
CREATE INDEX idx_settlement_offers_status ON gold_settlement_offers(offer_status);

COMMENT ON TABLE gold_settlement_offers IS 'Settlement offer and negotiation tracking';


-- ============================================================================
-- 12. COLLECTION PERFORMANCE
-- ============================================================================
-- Tracks collection team and individual performance metrics
CREATE TABLE gold_collection_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    user_id UUID NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    team_name VARCHAR(100),
    region VARCHAR(50),
    total_cases_assigned INTEGER DEFAULT 0,
    total_cases_resolved INTEGER DEFAULT 0,
    total_cases_escalated INTEGER DEFAULT 0,
    total_overdue_amount DECIMAL(15,2) DEFAULT 0,
    total_collected_amount DECIMAL(15,2) DEFAULT 0,
    collection_percentage DECIMAL(5,2),
    total_field_visits INTEGER DEFAULT 0,
    successful_field_visits INTEGER DEFAULT 0,
    total_calls_made INTEGER DEFAULT 0,
    contactable_rate DECIMAL(5,2),
    promise_kept_rate DECIMAL(5,2),
    total_promises_obtained INTEGER DEFAULT 0,
    promises_kept INTEGER DEFAULT 0,
    promises_broken INTEGER DEFAULT 0,
    legal_notices_sent INTEGER DEFAULT 0,
    recovery_actions_taken INTEGER DEFAULT 0,
    average_resolution_days DECIMAL(8,2),
    bucket_0_30_resolved INTEGER DEFAULT 0,
    bucket_31_60_resolved INTEGER DEFAULT 0,
    bucket_61_90_resolved INTEGER DEFAULT 0,
    bucket_90_plus_resolved INTEGER DEFAULT 0,
    performance_rating VARCHAR(20),
    incentive_earned DECIMAL(10,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_performance_rating CHECK (performance_rating IN ('poor', 'below_average', 'average', 'good', 'excellent', 'outstanding')),
    CONSTRAINT uq_performance_period UNIQUE (user_id, period_start, period_end)
);

CREATE INDEX idx_collection_performance_user ON gold_collection_performance(user_id);
CREATE INDEX idx_collection_performance_period ON gold_collection_performance(period_start, period_end);
CREATE INDEX idx_collection_performance_team ON gold_collection_performance(team_name);

COMMENT ON TABLE gold_collection_performance IS 'Collection team performance metrics and KPIs';


-- ============================================================================
-- VIEWS
-- ============================================================================

-- Active Collection Cases Summary
CREATE OR REPLACE VIEW vw_active_collection_cases AS
SELECT 
    cc.id,
    cc.case_number,
    cc.case_status,
    cc.bucket_type,
    cc.overdue_days,
    cc.overdue_amount,
    cc.total_outstanding,
    cc.assigned_to_user_id,
    cc.priority,
    cc.last_contact_date,
    cc.next_action_date,
    la.account_number,
    la.customer_id,
    la.loan_amount,
    la.outstanding_principal,
    COUNT(DISTINCT ca.id) as total_activities,
    COUNT(DISTINCT fv.id) as total_field_visits,
    COUNT(DISTINCT pp.id) as total_promises,
    SUM(CASE WHEN pp.promise_status = 'kept' THEN pp.amount_received ELSE 0 END) as total_promise_amount,
    MAX(ca.activity_date) as last_activity_date,
    MAX(fv.visit_date) as last_visit_date
FROM gold_collection_cases cc
JOIN gold_loan_accounts la ON cc.loan_account_id = la.id
LEFT JOIN gold_collection_activities ca ON cc.id = ca.collection_case_id
LEFT JOIN gold_field_visits fv ON cc.id = fv.collection_case_id
LEFT JOIN gold_payment_promises pp ON cc.id = pp.collection_case_id
WHERE cc.case_status IN ('open', 'in_progress', 'legal')
GROUP BY cc.id, cc.case_number, cc.case_status, cc.bucket_type, cc.overdue_days,
         cc.overdue_amount, cc.total_outstanding, cc.assigned_to_user_id, cc.priority,
         cc.last_contact_date, cc.next_action_date, la.account_number, la.customer_id,
         la.loan_amount, la.outstanding_principal;

COMMENT ON VIEW vw_active_collection_cases IS 'Summary view of all active collection cases with key metrics';


-- Collection Performance Dashboard
CREATE OR REPLACE VIEW vw_collection_dashboard AS
SELECT 
    cc.bucket_type,
    COUNT(DISTINCT cc.id) as total_cases,
    COUNT(DISTINCT CASE WHEN cc.case_status = 'open' THEN cc.id END) as open_cases,
    COUNT(DISTINCT CASE WHEN cc.case_status = 'in_progress' THEN cc.id END) as in_progress_cases,
    COUNT(DISTINCT CASE WHEN cc.case_status = 'legal' THEN cc.id END) as legal_cases,
    COUNT(DISTINCT CASE WHEN cc.case_status = 'closed' THEN cc.id END) as closed_cases,
    SUM(cc.total_outstanding) as total_outstanding,
    SUM(cc.overdue_amount) as total_overdue,
    COUNT(DISTINCT ca.id) as total_activities,
    COUNT(DISTINCT fv.id) as total_field_visits,
    COUNT(DISTINCT pp.id) as total_promises,
    SUM(CASE WHEN pp.promise_status = 'kept' THEN pp.amount_received ELSE 0 END) as total_collected,
    COUNT(DISTINCT ln.id) as total_legal_notices,
    COUNT(DISTINCT ra.id) as total_recovery_actions,
    AVG(cc.overdue_days) as avg_overdue_days
FROM gold_collection_cases cc
LEFT JOIN gold_collection_activities ca ON cc.id = ca.collection_case_id
LEFT JOIN gold_field_visits fv ON cc.id = fv.collection_case_id
LEFT JOIN gold_payment_promises pp ON cc.id = pp.collection_case_id
LEFT JOIN gold_legal_notices ln ON cc.id = ln.collection_case_id
LEFT JOIN gold_recovery_actions ra ON cc.id = ra.collection_case_id
GROUP BY cc.bucket_type;

COMMENT ON VIEW vw_collection_dashboard IS 'Collection dashboard with bucket-wise metrics';


-- Auction Lot Summary
CREATE OR REPLACE VIEW vw_auction_lots_summary AS
SELECT 
    al.id,
    al.lot_number,
    al.auction_date,
    al.lot_status,
    al.auction_type,
    al.total_gold_weight,
    al.total_items,
    al.reserve_price,
    al.starting_bid,
    al.winning_bid_amount,
    al.bid_count,
    COUNT(DISTINCT ali.id) as item_count,
    COUNT(DISTINCT ab.id) as total_bids,
    MAX(ab.bid_amount) as highest_bid,
    MIN(ab.bid_amount) as lowest_bid,
    al.net_realization,
    CASE 
        WHEN al.winning_bid_amount IS NOT NULL THEN 
            ((al.winning_bid_amount - al.reserve_price) / al.reserve_price * 100)
        ELSE NULL
    END as realization_percentage
FROM gold_auction_lots al
LEFT JOIN gold_auction_lot_items ali ON al.id = ali.auction_lot_id
LEFT JOIN gold_auction_bids ab ON al.id = ab.auction_lot_id
GROUP BY al.id, al.lot_number, al.auction_date, al.lot_status, al.auction_type,
         al.total_gold_weight, al.total_items, al.reserve_price, al.starting_bid,
         al.winning_bid_amount, al.bid_count, al.net_realization;

COMMENT ON VIEW vw_auction_lots_summary IS 'Auction lot summary with bid details and realization';


-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update collection case on activity
CREATE OR REPLACE FUNCTION update_collection_case_on_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE gold_collection_cases
    SET last_contact_date = NEW.activity_date,
        next_action_date = NEW.next_followup_date,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.collection_case_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_case_on_activity
AFTER INSERT ON gold_collection_activities
FOR EACH ROW
EXECUTE FUNCTION update_collection_case_on_activity();

COMMENT ON TRIGGER trg_update_case_on_activity ON gold_collection_activities 
IS 'Updates collection case contact dates on new activity';


-- Update promise status on payment
CREATE OR REPLACE FUNCTION update_promise_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.payment_date IS NOT NULL AND OLD.payment_date IS NULL THEN
        NEW.fulfillment_percentage := (NEW.amount_received / NEW.promised_amount * 100);
        
        IF NEW.amount_received >= NEW.promised_amount THEN
            NEW.promise_status := 'kept';
        ELSIF NEW.amount_received > 0 THEN
            NEW.promise_status := 'partial';
        ELSIF NEW.promised_payment_date < CURRENT_DATE THEN
            NEW.promise_status := 'broken';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_promise_status
BEFORE UPDATE ON gold_payment_promises
FOR EACH ROW
EXECUTE FUNCTION update_promise_status();

COMMENT ON TRIGGER trg_update_promise_status ON gold_payment_promises 
IS 'Automatically updates promise status based on payment received';


-- Update auction lot bid count
CREATE OR REPLACE FUNCTION update_auction_bid_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE gold_auction_lots
    SET bid_count = (
        SELECT COUNT(*) 
        FROM gold_auction_bids 
        WHERE auction_lot_id = NEW.auction_lot_id 
        AND bid_status = 'active'
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.auction_lot_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_auction_bid_count
AFTER INSERT ON gold_auction_bids
FOR EACH ROW
EXECUTE FUNCTION update_auction_bid_count();

COMMENT ON TRIGGER trg_update_auction_bid_count ON gold_auction_bids 
IS 'Updates bid count on auction lot when new bid is placed';


-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Insert sample collection cases
INSERT INTO gold_collection_cases (
    loan_account_id,
    case_number,
    case_status,
    bucket_type,
    overdue_days,
    overdue_amount,
    total_outstanding,
    principal_overdue,
    interest_overdue,
    penalty_overdue,
    assigned_to_user_id,
    priority
) VALUES 
(
    (SELECT id FROM gold_loan_accounts WHERE account_number = 'GL2024000001' LIMIT 1),
    'CC2024000001',
    'open',
    'dpd_31_60',
    45,
    15000.00,
    150000.00,
    12000.00,
    2500.00,
    500.00,
    gen_random_uuid(),
    'high'
) ON CONFLICT DO NOTHING;

COMMENT ON TABLE gold_collection_cases IS 'Phase 8: Collections & Recovery - Complete collection case management';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
