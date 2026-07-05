# 🏦 Loan Management Module - Complete Design

**Date**: July 4, 2026  
**Status**: 🚀 Starting Implementation  
**Priority**: HIGH - Core Business Feature

---

## 🎯 Module Overview

The Loan Management module is the **heart of the NBFC Suite**. It handles the complete loan lifecycle from application to closure, including credit assessment, approval workflows, disbursement, EMI management, and collections.

### Business Value
- **Revenue Generation**: Core lending operations
- **Risk Management**: Credit scoring and assessment
- **Compliance**: RBI regulations and reporting
- **Customer Experience**: Fast, transparent loan processing

---

## 📋 Features Breakdown

### Phase 1: Loan Products & Application (Week 1)
1. **Loan Product Configuration**
   - Product types (personal, business, gold, vehicle, home)
   - Interest rate schemes (flat, reducing, EMI-based)
   - Tenure options (months)
   - Eligibility criteria (income, age, CIBIL)
   - Processing fees and charges
   - Documentation requirements

2. **Loan Application**
   - Multi-step application form
   - Customer selection (with auto-complete)
   - Loan amount and tenure selection
   - Co-applicants (from family members)
   - Guarantors (from family members)
   - Bank account for disbursement
   - Document checklist
   - Application submission

### Phase 2: Credit Assessment & Approval (Week 2)
3. **Credit Scoring Engine**
   - CIBIL score integration
   - Income assessment
   - Debt-to-income ratio
   - Employment stability
   - Existing loans check
   - Property valuation (for secured loans)
   - Auto risk rating

4. **Approval Workflow**
   - Multi-level approval matrix
   - Credit officer review
   - Manager approval
   - Senior management approval (high value)
   - Rejection with reasons
   - Conditional approval
   - Approval notes and comments

### Phase 3: Disbursement & EMI (Week 3)
5. **Loan Disbursement**
   - Sanction letter generation
   - Loan agreement
   - Disbursement approval
   - Fund transfer to customer account
   - Disbursement confirmation
   - Loan account creation

6. **EMI Calculation & Scheduling**
   - Multiple calculation methods
   - EMI schedule generation
   - Principal and interest breakdown
   - Payment due dates
   - Advance EMI support
   - Partial prepayment handling

### Phase 4: Repayment & Collections (Week 4)
7. **Repayment Management**
   - Payment recording
   - Payment allocation (principal, interest, charges)
   - Receipt generation
   - Payment reconciliation
   - Early settlement calculations

8. **Collections & Overdue**
   - Overdue bucket management (0-30, 30-60, 60-90, 90+)
   - Penal interest calculation
   - Collection queue generation
   - SMS/Email reminders
   - Field agent assignment
   - Follow-up tracking

---

## 🗄️ Database Schema

### 1. Loan Products Table
```sql
CREATE TABLE loan_products (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(50) NOT NULL, -- personal, business, gold, vehicle, home
    loan_category VARCHAR(50) NOT NULL, -- secured, unsecured
    
    -- Interest Configuration
    interest_rate_type VARCHAR(50) NOT NULL, -- flat, reducing, compound
    min_interest_rate DECIMAL(5,2) NOT NULL,
    max_interest_rate DECIMAL(5,2) NOT NULL,
    default_interest_rate DECIMAL(5,2) NOT NULL,
    
    -- Loan Amount
    min_loan_amount DECIMAL(15,2) NOT NULL,
    max_loan_amount DECIMAL(15,2) NOT NULL,
    
    -- Tenure
    min_tenure_months INTEGER NOT NULL,
    max_tenure_months INTEGER NOT NULL,
    allowed_tenures INTEGER[], -- [6, 12, 18, 24, 36, 48, 60]
    
    -- Fees & Charges
    processing_fee_type VARCHAR(50) NOT NULL, -- fixed, percentage
    processing_fee_value DECIMAL(15,2) NOT NULL,
    documentation_charges DECIMAL(15,2),
    insurance_applicable BOOLEAN DEFAULT false,
    insurance_percentage DECIMAL(5,2),
    
    -- Penal Interest
    penal_interest_rate DECIMAL(5,2) NOT NULL,
    grace_period_days INTEGER DEFAULT 3,
    
    -- Eligibility Criteria
    min_age INTEGER DEFAULT 21,
    max_age INTEGER DEFAULT 65,
    min_monthly_income DECIMAL(15,2),
    min_cibil_score INTEGER DEFAULT 650,
    employment_types VARCHAR[], -- ['salaried', 'self_employed', 'business']
    
    -- Documentation
    required_documents INTEGER[], -- Document type IDs
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    
    -- Description
    description TEXT,
    features TEXT[],
    terms_and_conditions TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE INDEX idx_loan_products_tenant ON loan_products(tenant_id);
CREATE INDEX idx_loan_products_type ON loan_products(product_type);
CREATE INDEX idx_loan_products_active ON loan_products(is_active) WHERE is_deleted = false;
```

### 2. Loan Applications Table
```sql
CREATE TABLE loan_applications (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    application_number VARCHAR(50) UNIQUE NOT NULL, -- APP-YYYYMM-XXXX
    
    -- Customer & Product
    customer_id INTEGER NOT NULL,
    loan_product_id INTEGER NOT NULL,
    
    -- Loan Details
    requested_amount DECIMAL(15,2) NOT NULL,
    approved_amount DECIMAL(15,2),
    tenure_months INTEGER NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    
    -- EMI Calculation
    emi_amount DECIMAL(15,2),
    total_interest DECIMAL(15,2),
    total_repayment DECIMAL(15,2),
    
    -- Purpose
    loan_purpose_id INTEGER,
    purpose_description TEXT,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    -- draft, submitted, under_review, credit_assessment, 
    -- pending_approval, approved, rejected, disbursed, cancelled
    
    sub_status VARCHAR(100),
    status_reason TEXT,
    
    -- Workflow
    current_approver_id INTEGER,
    approval_level INTEGER DEFAULT 0,
    
    -- Dates
    application_date DATE NOT NULL,
    submission_date DATE,
    approval_date DATE,
    rejection_date DATE,
    disbursement_date DATE,
    
    -- Credit Assessment
    credit_score INTEGER,
    debt_to_income_ratio DECIMAL(5,2),
    monthly_income DECIMAL(15,2),
    monthly_obligations DECIMAL(15,2),
    risk_rating VARCHAR(50), -- low, medium, high, very_high
    
    -- Documents
    documents_verified BOOLEAN DEFAULT false,
    kyc_verified BOOLEAN DEFAULT false,
    
    -- Fees
    processing_fee DECIMAL(15,2),
    documentation_charges DECIMAL(15,2),
    insurance_amount DECIMAL(15,2),
    other_charges DECIMAL(15,2),
    total_deductions DECIMAL(15,2),
    net_disbursement DECIMAL(15,2),
    
    -- Disbursement Details
    disbursement_bank_account_id INTEGER,
    disbursement_mode VARCHAR(50), -- neft, rtgs, imps, cheque
    disbursement_reference VARCHAR(100),
    
    -- Notes
    applicant_remarks TEXT,
    internal_notes TEXT,
    rejection_reason TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_application_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_application_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_application_product FOREIGN KEY (loan_product_id) REFERENCES loan_products(id),
    CONSTRAINT fk_application_purpose FOREIGN KEY (loan_purpose_id) REFERENCES loan_purposes(id),
    CONSTRAINT fk_disbursement_account FOREIGN KEY (disbursement_bank_account_id) 
        REFERENCES customer_bank_accounts(id)
);

CREATE INDEX idx_applications_tenant ON loan_applications(tenant_id);
CREATE INDEX idx_applications_customer ON loan_applications(customer_id);
CREATE INDEX idx_applications_status ON loan_applications(status);
CREATE INDEX idx_applications_number ON loan_applications(application_number);
CREATE INDEX idx_applications_date ON loan_applications(application_date);
```

### 3. Loan Application Co-Applicants
```sql
CREATE TABLE loan_application_co_applicants (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_application_id INTEGER NOT NULL,
    family_member_id INTEGER NOT NULL,
    co_applicant_type VARCHAR(50) NOT NULL, -- co_applicant, guarantor
    is_primary BOOLEAN DEFAULT false,
    relationship VARCHAR(100),
    monthly_income DECIMAL(15,2),
    occupation VARCHAR(200),
    consent_given BOOLEAN DEFAULT false,
    consent_date DATE,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_co_applicant_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_co_applicant_application FOREIGN KEY (loan_application_id) 
        REFERENCES loan_applications(id),
    CONSTRAINT fk_co_applicant_family FOREIGN KEY (family_member_id) 
        REFERENCES customer_family_members(id)
);

CREATE INDEX idx_co_applicants_application ON loan_application_co_applicants(loan_application_id);
```

### 4. Loan Application Documents
```sql
CREATE TABLE loan_application_documents (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_application_id INTEGER NOT NULL,
    document_type_id INTEGER NOT NULL,
    customer_document_id INTEGER, -- Link to existing customer document
    document_number VARCHAR(100),
    file_path VARCHAR(500),
    file_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending', -- pending, verified, rejected
    verified_by INTEGER,
    verified_at TIMESTAMP,
    remarks TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_app_doc_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_app_doc_application FOREIGN KEY (loan_application_id) 
        REFERENCES loan_applications(id),
    CONSTRAINT fk_app_doc_type FOREIGN KEY (document_type_id) REFERENCES document_types(id),
    CONSTRAINT fk_app_doc_customer_doc FOREIGN KEY (customer_document_id) 
        REFERENCES customer_documents(id)
);

CREATE INDEX idx_app_docs_application ON loan_application_documents(loan_application_id);
```

### 5. Loan Approval Workflow
```sql
CREATE TABLE loan_approval_workflows (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_application_id INTEGER NOT NULL,
    approval_level INTEGER NOT NULL,
    approver_role VARCHAR(100) NOT NULL, -- credit_officer, manager, senior_manager
    approver_id INTEGER,
    
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, approved, rejected, returned, escalated
    
    action_date TIMESTAMP,
    decision VARCHAR(50), -- approve, reject, return, request_more_info
    comments TEXT,
    conditions TEXT[], -- Approval conditions
    
    -- Limits
    max_approval_amount DECIMAL(15,2),
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_workflow_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_workflow_application FOREIGN KEY (loan_application_id) 
        REFERENCES loan_applications(id)
);

CREATE INDEX idx_workflows_application ON loan_approval_workflows(loan_application_id);
CREATE INDEX idx_workflows_approver ON loan_approval_workflows(approver_id, status);
```

### 6. Loan Accounts
```sql
CREATE TABLE loan_accounts (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_account_number VARCHAR(50) UNIQUE NOT NULL, -- LN-YYYYMM-XXXX
    
    -- Application Link
    loan_application_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    loan_product_id INTEGER NOT NULL,
    
    -- Loan Details
    sanctioned_amount DECIMAL(15,2) NOT NULL,
    disbursed_amount DECIMAL(15,2) NOT NULL,
    outstanding_principal DECIMAL(15,2) NOT NULL,
    outstanding_interest DECIMAL(15,2) NOT NULL,
    outstanding_charges DECIMAL(15,2) DEFAULT 0,
    total_outstanding DECIMAL(15,2) NOT NULL,
    
    -- Terms
    tenure_months INTEGER NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    emi_amount DECIMAL(15,2) NOT NULL,
    emi_day INTEGER NOT NULL, -- Day of month for EMI
    
    -- Dates
    disbursement_date DATE NOT NULL,
    first_emi_date DATE NOT NULL,
    last_emi_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    closure_date DATE,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    -- active, overdue, npa, closed, settled, written_off
    
    overdue_days INTEGER DEFAULT 0,
    dpd INTEGER DEFAULT 0, -- Days Past Due
    
    -- Collections
    last_payment_date DATE,
    last_payment_amount DECIMAL(15,2),
    next_due_date DATE,
    next_due_amount DECIMAL(15,2),
    
    -- NPA Classification
    npa_status VARCHAR(50), -- standard, sub_standard, doubtful, loss
    npa_date DATE,
    
    -- Prepayment
    prepayment_allowed BOOLEAN DEFAULT true,
    prepayment_charges_percentage DECIMAL(5,2),
    
    -- Penal Interest
    penal_interest_outstanding DECIMAL(15,2) DEFAULT 0,
    
    -- Accounting
    interest_accrued DECIMAL(15,2) DEFAULT 0,
    interest_received DECIMAL(15,2) DEFAULT 0,
    principal_received DECIMAL(15,2) DEFAULT 0,
    
    -- Notes
    internal_notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_loan_account_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_loan_account_application FOREIGN KEY (loan_application_id) 
        REFERENCES loan_applications(id),
    CONSTRAINT fk_loan_account_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_loan_account_product FOREIGN KEY (loan_product_id) REFERENCES loan_products(id)
);

CREATE INDEX idx_loan_accounts_tenant ON loan_accounts(tenant_id);
CREATE INDEX idx_loan_accounts_customer ON loan_accounts(customer_id);
CREATE INDEX idx_loan_accounts_status ON loan_accounts(status);
CREATE INDEX idx_loan_accounts_number ON loan_accounts(loan_account_number);
CREATE INDEX idx_loan_accounts_overdue ON loan_accounts(overdue_days) WHERE overdue_days > 0;
```

### 7. EMI Schedule
```sql
CREATE TABLE loan_emi_schedules (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_account_id INTEGER NOT NULL,
    
    -- EMI Details
    installment_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    
    -- Amount Breakdown
    emi_amount DECIMAL(15,2) NOT NULL,
    principal_component DECIMAL(15,2) NOT NULL,
    interest_component DECIMAL(15,2) NOT NULL,
    
    -- Balance
    opening_principal DECIMAL(15,2) NOT NULL,
    closing_principal DECIMAL(15,2) NOT NULL,
    
    -- Payment Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending, paid, partially_paid, overdue, waived
    
    paid_amount DECIMAL(15,2) DEFAULT 0,
    paid_principal DECIMAL(15,2) DEFAULT 0,
    paid_interest DECIMAL(15,2) DEFAULT 0,
    payment_date DATE,
    
    -- Overdue
    overdue_days INTEGER DEFAULT 0,
    penal_interest DECIMAL(15,2) DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_emi_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_emi_loan_account FOREIGN KEY (loan_account_id) REFERENCES loan_accounts(id),
    
    UNIQUE (loan_account_id, installment_number)
);

CREATE INDEX idx_emi_loan_account ON loan_emi_schedules(loan_account_id);
CREATE INDEX idx_emi_due_date ON loan_emi_schedules(due_date);
CREATE INDEX idx_emi_status ON loan_emi_schedules(status);
CREATE INDEX idx_emi_overdue ON loan_emi_schedules(overdue_days) WHERE overdue_days > 0;
```

### 8. Loan Repayments
```sql
CREATE TABLE loan_repayments (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_account_id INTEGER NOT NULL,
    
    receipt_number VARCHAR(50) UNIQUE NOT NULL, -- RCP-YYYYMM-XXXX
    
    -- Payment Details
    payment_date DATE NOT NULL,
    payment_amount DECIMAL(15,2) NOT NULL,
    payment_mode VARCHAR(50) NOT NULL, -- cash, cheque, neft, rtgs, upi
    
    -- Allocation
    allocated_to_principal DECIMAL(15,2) NOT NULL,
    allocated_to_interest DECIMAL(15,2) NOT NULL,
    allocated_to_penal_interest DECIMAL(15,2) DEFAULT 0,
    allocated_to_charges DECIMAL(15,2) DEFAULT 0,
    
    -- Reference
    reference_number VARCHAR(100),
    bank_name VARCHAR(200),
    transaction_date DATE,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'success',
    -- success, pending, failed, reversed
    
    reversal_reason TEXT,
    reversed_at TIMESTAMP,
    reversed_by INTEGER,
    
    -- Receipt
    receipt_generated BOOLEAN DEFAULT false,
    receipt_url VARCHAR(500),
    
    -- EMI Links
    emi_schedule_ids INTEGER[], -- Which EMIs this payment covers
    
    -- Notes
    remarks TEXT,
    collected_by INTEGER,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    
    CONSTRAINT fk_repayment_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_repayment_loan_account FOREIGN KEY (loan_account_id) 
        REFERENCES loan_accounts(id)
);

CREATE INDEX idx_repayments_loan_account ON loan_repayments(loan_account_id);
CREATE INDEX idx_repayments_date ON loan_repayments(payment_date);
CREATE INDEX idx_repayments_receipt ON loan_repayments(receipt_number);
```

---

## 🔧 Business Logic

### 1. EMI Calculation Methods

#### Flat Rate Method
```
Monthly EMI = (Principal × Rate × Tenure) / (12 × 100) + (Principal / Tenure)
Total Interest = Principal × Rate × Tenure / 100
```

#### Reducing Balance Method
```
Monthly EMI = P × R × (1+R)^N / ((1+R)^N - 1)
Where:
  P = Principal
  R = Monthly Interest Rate (Annual Rate / 12 / 100)
  N = Number of months
```

### 2. Overdue & Penal Interest
```
Penal Interest = Overdue Amount × Penal Rate × Days / 365
DPD (Days Past Due) = Current Date - Due Date (if > 0)
```

### 3. NPA Classification
- **Standard**: 0-90 days overdue
- **Sub-Standard**: 90-180 days overdue
- **Doubtful**: 180-365 days overdue
- **Loss**: 365+ days overdue

### 4. Payment Allocation Priority
1. Penal interest
2. Regular interest
3. Principal
4. Other charges

---

## 📊 Key Metrics & KPIs

### Portfolio Metrics
- Total loans disbursed
- Outstanding portfolio
- Average loan size
- Active loans count
- Closed loans count

### Quality Metrics
- NPAs (amount & percentage)
- Collection efficiency
- Average DPD
- Bucket-wise distribution (0-30, 30-60, 60-90, 90+)

### Performance Metrics
- Disbursement turnaround time
- Approval rate
- Rejection reasons analysis
- Product-wise performance

---

## 🎨 UI/UX Flow

### Loan Application Journey
```
1. Product Selection
   └── Browse products → Compare → Select

2. Application Form (6 Steps)
   ├── Step 1: Loan Details (amount, tenure, purpose)
   ├── Step 2: Customer Selection (search, autocomplete)
   ├── Step 3: Co-applicants (add from family)
   ├── Step 4: Bank Account (for disbursement)
   ├── Step 5: Documents (upload/link)
   └── Step 6: Review & Submit

3. Credit Assessment
   └── Auto-calculate credit score → Risk rating

4. Approval Workflow
   └── Level 1 → Level 2 → Level 3 (if needed)

5. Disbursement
   └── Generate agreement → Approve → Disburse

6. Active Loan
   └── View EMI schedule → Make payments → Track
```

---

## 🚀 Implementation Plan

### Week 1: Products & Application Backend
**Day 1-2**: Database schema + migrations
**Day 3-4**: Loan product models & service
**Day 5-7**: Application models & service

### Week 2: Credit & Approval Backend
**Day 1-2**: Credit scoring service
**Day 3-5**: Approval workflow engine
**Day 6-7**: Testing & refinement

### Week 3: Disbursement & EMI Backend
**Day 1-3**: Loan account & EMI service
**Day 4-5**: Disbursement service
**Day 6-7**: Testing & integration

### Week 4: Repayment & Frontend
**Day 1-2**: Repayment service
**Day 3-7**: Frontend pages (all)

---

## ✅ Ready to Start!

**Next Steps:**
1. Create database models
2. Build loan product service
3. Build application service
4. Create API endpoints
5. Build frontend pages

Let's begin with the backend foundation! 🚀
