-- ============================================================================
-- Phase 7: Loan Servicing & Repayment
-- Migration: 024_loan_servicing_repayment.sql
-- Description: Complete loan servicing system with EMI collection, interest
--              accrual, repayment processing, and account management
-- Author: NBFCSuite Development Team
-- Date: July 3, 2026
-- ============================================================================

-- ============================================================================
-- 1. EMI Schedule Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_emi_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id) ON DELETE CASCADE,
    installment_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    principal_component DECIMAL(15, 2) NOT NULL,
    interest_component DECIMAL(15, 2) NOT NULL,
    total_emi_amount DECIMAL(15, 2) NOT NULL,
    
    -- Payment tracking
    payment_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, paid, partially_paid, overdue, waived
    paid_amount DECIMAL(15, 2) DEFAULT 0,
    paid_date DATE,
    payment_mode VARCHAR(50),
    -- cash, cheque, neft, imps, rtgs, upi, auto_debit
    transaction_reference VARCHAR(100),
    
    -- Outstanding tracking
    outstanding_principal DECIMAL(15, 2),
    outstanding_interest DECIMAL(15, 2),
    
    -- Overdue tracking
    days_overdue INTEGER DEFAULT 0,
    overdue_charges DECIMAL(15, 2) DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    CONSTRAINT unique_loan_installment UNIQUE(loan_account_id, installment_number),
    CONSTRAINT valid_emi_amounts CHECK (principal_component >= 0 AND interest_component >= 0),
    CONSTRAINT valid_payment_status CHECK (payment_status IN ('pending', 'paid', 'partially_paid', 'overdue', 'waived'))
);

CREATE INDEX idx_emi_schedule_loan ON gold_emi_schedule(loan_account_id);
CREATE INDEX idx_emi_schedule_due_date ON gold_emi_schedule(due_date);
CREATE INDEX idx_emi_schedule_status ON gold_emi_schedule(payment_status);
CREATE INDEX idx_emi_schedule_overdue ON gold_emi_schedule(days_overdue) WHERE days_overdue > 0;

COMMENT ON TABLE gold_emi_schedule IS 'EMI schedule with payment tracking';
COMMENT ON COLUMN gold_emi_schedule.payment_status IS 'Current payment status of installment';
COMMENT ON COLUMN gold_emi_schedule.days_overdue IS 'Number of days past due date';

-- ============================================================================
-- 2. Repayment Transactions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_repayment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id) ON DELETE CASCADE,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Payment details
    payment_amount DECIMAL(15, 2) NOT NULL,
    payment_mode VARCHAR(50) NOT NULL,
    -- cash, cheque, neft, imps, rtgs, upi, auto_debit, adjustment
    transaction_reference VARCHAR(100),
    bank_name VARCHAR(100),
    cheque_number VARCHAR(50),
    cheque_date DATE,
    
    -- Allocation breakdown
    principal_paid DECIMAL(15, 2) DEFAULT 0,
    interest_paid DECIMAL(15, 2) DEFAULT 0,
    overdue_interest_paid DECIMAL(15, 2) DEFAULT 0,
    penalty_paid DECIMAL(15, 2) DEFAULT 0,
    other_charges_paid DECIMAL(15, 2) DEFAULT 0,
    
    -- Status
    transaction_status VARCHAR(50) NOT NULL DEFAULT 'completed',
    -- pending, completed, bounced, reversed, cancelled
    reversal_reason TEXT,
    reversed_at TIMESTAMP,
    reversed_by_user_id VARCHAR(50),
    
    -- Processing
    processed_by_user_id VARCHAR(50) NOT NULL,
    verified_by_user_id VARCHAR(50),
    verification_date TIMESTAMP,
    branch_id VARCHAR(50),
    
    -- Metadata
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_payment_amount CHECK (payment_amount > 0),
    CONSTRAINT valid_allocation CHECK (
        principal_paid + interest_paid + overdue_interest_paid + 
        penalty_paid + other_charges_paid <= payment_amount + 0.01
    ),
    CONSTRAINT valid_transaction_status CHECK (
        transaction_status IN ('pending', 'completed', 'bounced', 'reversed', 'cancelled')
    )
);

CREATE INDEX idx_repayment_loan ON gold_repayment_transactions(loan_account_id);
CREATE INDEX idx_repayment_date ON gold_repayment_transactions(transaction_date);
CREATE INDEX idx_repayment_receipt ON gold_repayment_transactions(receipt_number);
CREATE INDEX idx_repayment_status ON gold_repayment_transactions(transaction_status);
CREATE INDEX idx_repayment_mode ON gold_repayment_transactions(payment_mode);

COMMENT ON TABLE gold_repayment_transactions IS 'All repayment transactions with allocation';
COMMENT ON COLUMN gold_repayment_transactions.receipt_number IS 'Unique receipt identifier';

-- ============================================================================
-- 3. Interest Accrual Ledger
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_interest_accrual (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id) ON DELETE CASCADE,
    accrual_date DATE NOT NULL,
    accrual_period_start DATE NOT NULL,
    accrual_period_end DATE NOT NULL,
    
    -- Principal and rate
    opening_principal DECIMAL(15, 2) NOT NULL,
    closing_principal DECIMAL(15, 2) NOT NULL,
    applicable_rate DECIMAL(8, 4) NOT NULL,
    days_in_period INTEGER NOT NULL,
    
    -- Interest calculation
    interest_accrued DECIMAL(15, 2) NOT NULL,
    cumulative_interest DECIMAL(15, 2) NOT NULL,
    
    -- Status
    accrual_status VARCHAR(50) NOT NULL DEFAULT 'posted',
    -- draft, posted, reversed
    reversed_at TIMESTAMP,
    reversal_reason TEXT,
    
    -- Metadata
    calculation_method VARCHAR(50),
    -- simple, compound, reducing_balance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    CONSTRAINT unique_loan_accrual_date UNIQUE(loan_account_id, accrual_date),
    CONSTRAINT valid_accrual_status CHECK (accrual_status IN ('draft', 'posted', 'reversed')),
    CONSTRAINT valid_interest_amount CHECK (interest_accrued >= 0)
);

CREATE INDEX idx_interest_accrual_loan ON gold_interest_accrual(loan_account_id);
CREATE INDEX idx_interest_accrual_date ON gold_interest_accrual(accrual_date);
CREATE INDEX idx_interest_accrual_status ON gold_interest_accrual(accrual_status);

COMMENT ON TABLE gold_interest_accrual IS 'Daily interest accrual tracking';
COMMENT ON COLUMN gold_interest_accrual.calculation_method IS 'Method used for interest calculation';

-- ============================================================================
-- 4. Loan Account Adjustments
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_loan_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id) ON DELETE CASCADE,
    adjustment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    adjustment_type VARCHAR(50) NOT NULL,
    -- waiver, write_off, reversal, correction, penalty, rebate
    
    -- Adjustment details
    adjustment_amount DECIMAL(15, 2) NOT NULL,
    adjustment_category VARCHAR(50) NOT NULL,
    -- principal, interest, penalty, charges
    
    -- Approval workflow
    requested_by_user_id VARCHAR(50) NOT NULL,
    approved_by_user_id VARCHAR(50),
    approval_date TIMESTAMP,
    approval_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, approved, rejected
    
    -- Justification
    reason TEXT NOT NULL,
    supporting_document_id VARCHAR(100),
    branch_id VARCHAR(50),
    
    -- Accounting impact
    debit_account VARCHAR(50),
    credit_account VARCHAR(50),
    journal_entry_id VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_adjustment_type CHECK (
        adjustment_type IN ('waiver', 'write_off', 'reversal', 'correction', 'penalty', 'rebate')
    ),
    CONSTRAINT valid_adjustment_category CHECK (
        adjustment_category IN ('principal', 'interest', 'penalty', 'charges')
    ),
    CONSTRAINT valid_approval_status CHECK (
        approval_status IN ('pending', 'approved', 'rejected')
    )
);

CREATE INDEX idx_adjustments_loan ON gold_loan_adjustments(loan_account_id);
CREATE INDEX idx_adjustments_type ON gold_loan_adjustments(adjustment_type);
CREATE INDEX idx_adjustments_status ON gold_loan_adjustments(approval_status);
CREATE INDEX idx_adjustments_date ON gold_loan_adjustments(adjustment_date);

COMMENT ON TABLE gold_loan_adjustments IS 'Loan account adjustments and waivers';
COMMENT ON COLUMN gold_loan_adjustments.adjustment_type IS 'Type of adjustment being made';

-- ============================================================================
-- 5. Prepayment/Foreclosure Records
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_loan_prepayments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id) ON DELETE CASCADE,
    prepayment_date DATE NOT NULL,
    prepayment_type VARCHAR(50) NOT NULL,
    -- part_payment, foreclosure, full_prepayment
    
    -- Amount details
    prepayment_amount DECIMAL(15, 2) NOT NULL,
    outstanding_principal_before DECIMAL(15, 2) NOT NULL,
    outstanding_interest_before DECIMAL(15, 2) NOT NULL,
    
    -- Charges
    prepayment_charges DECIMAL(15, 2) DEFAULT 0,
    prepayment_charge_percentage DECIMAL(5, 2),
    waived_charges DECIMAL(15, 2) DEFAULT 0,
    
    -- Impact
    principal_reduced DECIMAL(15, 2) NOT NULL,
    interest_recalculated BOOLEAN DEFAULT false,
    tenure_reduced_months INTEGER DEFAULT 0,
    emi_recalculated BOOLEAN DEFAULT false,
    new_emi_amount DECIMAL(15, 2),
    
    -- Status
    prepayment_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, approved, completed, rejected
    approved_by_user_id VARCHAR(50),
    approval_date TIMESTAMP,
    
    -- NOC for foreclosure
    noc_issued BOOLEAN DEFAULT false,
    noc_issued_date DATE,
    noc_number VARCHAR(50),
    
    -- Transaction
    transaction_id UUID REFERENCES gold_repayment_transactions(id),
    
    -- Metadata
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    CONSTRAINT valid_prepayment_type CHECK (
        prepayment_type IN ('part_payment', 'foreclosure', 'full_prepayment')
    ),
    CONSTRAINT valid_prepayment_status CHECK (
        prepayment_status IN ('pending', 'approved', 'completed', 'rejected')
    ),
    CONSTRAINT valid_prepayment_amount CHECK (prepayment_amount > 0)
);

CREATE INDEX idx_prepayments_loan ON gold_loan_prepayments(loan_account_id);
CREATE INDEX idx_prepayments_type ON gold_loan_prepayments(prepayment_type);
CREATE INDEX idx_prepayments_status ON gold_loan_prepayments(prepayment_status);
CREATE INDEX idx_prepayments_date ON gold_loan_prepayments(prepayment_date);

COMMENT ON TABLE gold_loan_prepayments IS 'Prepayment and foreclosure records';
COMMENT ON COLUMN gold_loan_prepayments.noc_issued IS 'No Objection Certificate for foreclosure';

-- ============================================================================
-- 6. Loan Statements
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_loan_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id) ON DELETE CASCADE,
    statement_date DATE NOT NULL,
    statement_period_start DATE NOT NULL,
    statement_period_end DATE NOT NULL,
    statement_type VARCHAR(50) NOT NULL DEFAULT 'monthly',
    -- monthly, quarterly, annual, on_demand
    
    -- Opening balances
    opening_principal DECIMAL(15, 2) NOT NULL,
    opening_interest DECIMAL(15, 2) NOT NULL,
    
    -- Transactions summary
    disbursements_amount DECIMAL(15, 2) DEFAULT 0,
    repayments_amount DECIMAL(15, 2) DEFAULT 0,
    interest_charged DECIMAL(15, 2) DEFAULT 0,
    charges_applied DECIMAL(15, 2) DEFAULT 0,
    adjustments_amount DECIMAL(15, 2) DEFAULT 0,
    
    -- Closing balances
    closing_principal DECIMAL(15, 2) NOT NULL,
    closing_interest DECIMAL(15, 2) NOT NULL,
    total_outstanding DECIMAL(15, 2) NOT NULL,
    
    -- Next EMI
    next_emi_due_date DATE,
    next_emi_amount DECIMAL(15, 2),
    
    -- Document
    statement_generated BOOLEAN DEFAULT false,
    statement_file_path VARCHAR(500),
    generated_at TIMESTAMP,
    sent_to_customer BOOLEAN DEFAULT false,
    sent_at TIMESTAMP,
    delivery_method VARCHAR(50),
    -- email, sms, post, branch_pickup
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    CONSTRAINT unique_loan_statement_period UNIQUE(loan_account_id, statement_period_start, statement_period_end),
    CONSTRAINT valid_statement_type CHECK (
        statement_type IN ('monthly', 'quarterly', 'annual', 'on_demand')
    )
);

CREATE INDEX idx_statements_loan ON gold_loan_statements(loan_account_id);
CREATE INDEX idx_statements_date ON gold_loan_statements(statement_date);
CREATE INDEX idx_statements_type ON gold_loan_statements(statement_type);

COMMENT ON TABLE gold_loan_statements IS 'Loan account statements for customers';
COMMENT ON COLUMN gold_loan_statements.statement_file_path IS 'Path to generated PDF statement';

-- ============================================================================
-- 7. Auto-Debit Mandates
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_auto_debit_mandates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id) ON DELETE CASCADE,
    mandate_reference VARCHAR(100) UNIQUE NOT NULL,
    
    -- Bank details
    customer_account_number VARCHAR(50) NOT NULL,
    customer_ifsc_code VARCHAR(20) NOT NULL,
    customer_account_holder_name VARCHAR(200) NOT NULL,
    bank_name VARCHAR(100),
    
    -- Mandate details
    mandate_type VARCHAR(50) NOT NULL,
    -- nach, emandate, standing_instruction
    mandate_amount DECIMAL(15, 2),
    mandate_frequency VARCHAR(50) NOT NULL,
    -- monthly, quarterly, one_time
    start_date DATE NOT NULL,
    end_date DATE,
    
    -- Status
    mandate_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, active, expired, cancelled, suspended
    activation_date DATE,
    cancellation_date DATE,
    cancellation_reason TEXT,
    
    -- Processing
    mandate_document_path VARCHAR(500),
    bank_approval_reference VARCHAR(100),
    bank_approval_date DATE,
    
    -- Debit tracking
    last_debit_date DATE,
    last_debit_amount DECIMAL(15, 2),
    last_debit_status VARCHAR(50),
    total_successful_debits INTEGER DEFAULT 0,
    total_failed_debits INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    CONSTRAINT valid_mandate_type CHECK (
        mandate_type IN ('nach', 'emandate', 'standing_instruction')
    ),
    CONSTRAINT valid_mandate_frequency CHECK (
        mandate_frequency IN ('monthly', 'quarterly', 'one_time')
    ),
    CONSTRAINT valid_mandate_status CHECK (
        mandate_status IN ('pending', 'active', 'expired', 'cancelled', 'suspended')
    )
);

CREATE INDEX idx_mandate_loan ON gold_auto_debit_mandates(loan_account_id);
CREATE INDEX idx_mandate_reference ON gold_auto_debit_mandates(mandate_reference);
CREATE INDEX idx_mandate_status ON gold_auto_debit_mandates(mandate_status);

COMMENT ON TABLE gold_auto_debit_mandates IS 'Auto-debit mandate setup for EMI collection';
COMMENT ON COLUMN gold_auto_debit_mandates.mandate_type IS 'Type of auto-debit facility';

-- ============================================================================
-- 8. Penalty and Charges Application
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_loan_penalties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id) ON DELETE CASCADE,
    emi_schedule_id UUID REFERENCES gold_emi_schedule(id) ON DELETE SET NULL,
    
    -- Penalty details
    penalty_date DATE NOT NULL,
    penalty_type VARCHAR(50) NOT NULL,
    -- late_payment, bounced_cheque, pre_closure, penal_interest, documentation
    
    -- Calculation
    base_amount DECIMAL(15, 2),
    penalty_rate DECIMAL(8, 4),
    penalty_amount DECIMAL(15, 2) NOT NULL,
    
    -- Status
    penalty_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, applied, waived, paid
    waived_amount DECIMAL(15, 2) DEFAULT 0,
    waived_by_user_id VARCHAR(50),
    waiver_reason TEXT,
    waiver_date DATE,
    
    -- Payment
    paid_amount DECIMAL(15, 2) DEFAULT 0,
    payment_date DATE,
    
    -- Approval for waiver
    waiver_approval_required BOOLEAN DEFAULT true,
    approved_by_user_id VARCHAR(50),
    approval_date DATE,
    
    -- Metadata
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    CONSTRAINT valid_penalty_type CHECK (
        penalty_type IN ('late_payment', 'bounced_cheque', 'pre_closure', 
                         'penal_interest', 'documentation')
    ),
    CONSTRAINT valid_penalty_status CHECK (
        penalty_status IN ('pending', 'applied', 'waived', 'paid')
    ),
    CONSTRAINT valid_penalty_amount CHECK (penalty_amount >= 0)
);

CREATE INDEX idx_penalties_loan ON gold_loan_penalties(loan_account_id);
CREATE INDEX idx_penalties_emi ON gold_loan_penalties(emi_schedule_id);
CREATE INDEX idx_penalties_type ON gold_loan_penalties(penalty_type);
CREATE INDEX idx_penalties_status ON gold_loan_penalties(penalty_status);
CREATE INDEX idx_penalties_date ON gold_loan_penalties(penalty_date);

COMMENT ON TABLE gold_loan_penalties IS 'Penalty and additional charges tracking';
COMMENT ON COLUMN gold_loan_penalties.penalty_type IS 'Type of penalty being charged';

-- ============================================================================
-- 9. Loan Renewal Records
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_loan_renewals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id),
    new_loan_account_id UUID REFERENCES gold_loan_accounts(id),
    
    -- Renewal details
    renewal_date DATE NOT NULL,
    renewal_type VARCHAR(50) NOT NULL,
    -- term_extension, interest_settlement, top_up
    
    -- Original loan details
    original_principal_outstanding DECIMAL(15, 2) NOT NULL,
    original_interest_outstanding DECIMAL(15, 2) NOT NULL,
    original_maturity_date DATE NOT NULL,
    
    -- Renewal terms
    extended_tenure_months INTEGER,
    new_maturity_date DATE,
    additional_amount DECIMAL(15, 2) DEFAULT 0,
    interest_settled_amount DECIMAL(15, 2) DEFAULT 0,
    
    -- Charges
    renewal_charges DECIMAL(15, 2) DEFAULT 0,
    waived_renewal_charges DECIMAL(15, 2) DEFAULT 0,
    
    -- Status
    renewal_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, approved, completed, rejected
    approved_by_user_id VARCHAR(50),
    approval_date DATE,
    
    -- Documentation
    renewal_agreement_signed BOOLEAN DEFAULT false,
    renewal_agreement_date DATE,
    renewal_agreement_path VARCHAR(500),
    
    -- Metadata
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    CONSTRAINT valid_renewal_type CHECK (
        renewal_type IN ('term_extension', 'interest_settlement', 'top_up')
    ),
    CONSTRAINT valid_renewal_status CHECK (
        renewal_status IN ('pending', 'approved', 'completed', 'rejected')
    )
);

CREATE INDEX idx_renewals_original_loan ON gold_loan_renewals(original_loan_account_id);
CREATE INDEX idx_renewals_new_loan ON gold_loan_renewals(new_loan_account_id);
CREATE INDEX idx_renewals_type ON gold_loan_renewals(renewal_type);
CREATE INDEX idx_renewals_status ON gold_loan_renewals(renewal_status);
CREATE INDEX idx_renewals_date ON gold_loan_renewals(renewal_date);

COMMENT ON TABLE gold_loan_renewals IS 'Loan renewal and extension records';
COMMENT ON COLUMN gold_loan_renewals.renewal_type IS 'Type of renewal being processed';

-- ============================================================================
-- 10. Repayment Allocation Rules
-- ============================================================================
CREATE TABLE IF NOT EXISTS gold_repayment_allocation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(100) NOT NULL UNIQUE,
    rule_description TEXT,
    
    -- Priority order (1 = first to allocate)
    allocation_priority_1 VARCHAR(50) NOT NULL,
    allocation_priority_2 VARCHAR(50),
    allocation_priority_3 VARCHAR(50),
    allocation_priority_4 VARCHAR(50),
    allocation_priority_5 VARCHAR(50),
    -- Values: penalty, overdue_interest, current_interest, principal, charges
    
    -- Rule applicability
    is_default BOOLEAN DEFAULT false,
    product_type VARCHAR(50),
    applicable_from_date DATE,
    applicable_to_date DATE,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    CONSTRAINT valid_allocation_priorities CHECK (
        allocation_priority_1 IN ('penalty', 'overdue_interest', 'current_interest', 'principal', 'charges')
    )
);

CREATE INDEX idx_allocation_rules_default ON gold_repayment_allocation_rules(is_default);
CREATE INDEX idx_allocation_rules_active ON gold_repayment_allocation_rules(is_active);

COMMENT ON TABLE gold_repayment_allocation_rules IS 'Rules for payment allocation order';
COMMENT ON COLUMN gold_repayment_allocation_rules.is_default IS 'Default rule for all products';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View 1: Overdue EMIs Summary
CREATE OR REPLACE VIEW gold_overdue_emis_summary AS
SELECT 
    es.loan_account_id,
    la.loan_account_number,
    la.customer_id,
    COUNT(*) as overdue_count,
    SUM(es.total_emi_amount - es.paid_amount) as total_overdue_amount,
    MAX(es.days_overdue) as max_days_overdue,
    SUM(es.overdue_charges) as total_overdue_charges,
    MIN(es.due_date) as earliest_overdue_date
FROM gold_emi_schedule es
JOIN gold_loan_accounts la ON es.loan_account_id = la.id
WHERE es.payment_status IN ('overdue', 'partially_paid')
GROUP BY es.loan_account_id, la.loan_account_number, la.customer_id;

COMMENT ON VIEW gold_overdue_emis_summary IS 'Summary of overdue EMIs by loan account';

-- View 2: Loan Portfolio Health
CREATE OR REPLACE VIEW gold_loan_portfolio_health AS
SELECT 
    la.branch_id,
    la.product_id,
    COUNT(*) as total_loans,
    SUM(la.principal_amount) as total_principal_disbursed,
    SUM(la.outstanding_principal) as total_principal_outstanding,
    SUM(la.outstanding_interest) as total_interest_outstanding,
    COUNT(CASE WHEN la.is_npa THEN 1 END) as npa_count,
    SUM(CASE WHEN la.is_npa THEN la.outstanding_principal ELSE 0 END) as npa_amount,
    COUNT(CASE WHEN la.account_status = 'active' THEN 1 END) as active_count,
    COUNT(CASE WHEN la.account_status = 'closed' THEN 1 END) as closed_count,
    AVG(la.outstanding_principal) as avg_outstanding_principal
FROM gold_loan_accounts la
GROUP BY la.branch_id, la.product_id;

COMMENT ON VIEW gold_loan_portfolio_health IS 'Portfolio health metrics by branch and product';

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger to update loan account outstanding on repayment
CREATE OR REPLACE FUNCTION update_loan_outstanding_on_repayment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.transaction_status = 'completed' THEN
        UPDATE gold_loan_accounts
        SET 
            outstanding_principal = outstanding_principal - NEW.principal_paid,
            outstanding_interest = outstanding_interest - NEW.interest_paid,
            last_payment_date = NEW.transaction_date,
            last_payment_amount = NEW.payment_amount,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.loan_account_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_loan_outstanding
AFTER INSERT OR UPDATE ON gold_repayment_transactions
FOR EACH ROW
EXECUTE FUNCTION update_loan_outstanding_on_repayment();

-- Trigger to mark EMI as overdue
CREATE OR REPLACE FUNCTION mark_emi_overdue()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.due_date < CURRENT_DATE AND NEW.payment_status = 'pending' THEN
        NEW.payment_status = 'overdue';
        NEW.days_overdue = CURRENT_DATE - NEW.due_date;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_mark_emi_overdue
BEFORE UPDATE ON gold_emi_schedule
FOR EACH ROW
EXECUTE FUNCTION mark_emi_overdue();

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Default repayment allocation rule
INSERT INTO gold_repayment_allocation_rules (
    rule_name,
    rule_description,
    allocation_priority_1,
    allocation_priority_2,
    allocation_priority_3,
    allocation_priority_4,
    allocation_priority_5,
    is_default,
    is_active
) VALUES (
    'Default Allocation Rule',
    'Standard payment allocation: Penalty > Overdue Interest > Current Interest > Principal > Other Charges',
    'penalty',
    'overdue_interest',
    'current_interest',
    'principal',
    'charges',
    true,
    true
) ON CONFLICT (rule_name) DO NOTHING;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional composite indexes for common queries
CREATE INDEX idx_emi_loan_status_due ON gold_emi_schedule(loan_account_id, payment_status, due_date);
CREATE INDEX idx_repayment_loan_date ON gold_repayment_transactions(loan_account_id, transaction_date DESC);
CREATE INDEX idx_interest_loan_date ON gold_interest_accrual(loan_account_id, accrual_date DESC);

-- ============================================================================
-- GRANTS (if needed)
-- ============================================================================

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gold_service_role;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA public TO gold_service_role;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================

COMMENT ON SCHEMA public IS 'Phase 7: Loan Servicing & Repayment - 10 tables, 2 views, complete EMI and repayment system';
