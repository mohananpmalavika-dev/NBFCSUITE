# Phase 7: Loan Servicing & Repayment - Technical Documentation

## Overview

**Phase**: 7 of 15  
**Module**: Loan Servicing & Repayment Management  
**Status**: ✅ Complete  
**Completion Date**: July 3, 2026

This phase implements comprehensive loan servicing capabilities including EMI management, repayment processing, interest accrual, loan adjustments, prepayments, statement generation, auto-debit mandates, penalty management, and portfolio health monitoring.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [API Endpoints](#api-endpoints)
6. [Business Logic](#business-logic)
7. [Integration Points](#integration-points)
8. [Security & Compliance](#security--compliance)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Guide](#deployment-guide)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (Next.js)                  │
├─────────────────────────────────────────────────────────────┤
│  • EMI Schedule Management    • Repayment Collections        │
│  • Interest Accrual Dashboard • Adjustments Management       │
│  • Prepayment Processing      • Statement Generation         │
│  • Auto-Debit Mandates        • Portfolio Health Dashboard   │
└─────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  • 40+ REST Endpoints         • Request Validation           │
│  • Business Logic Processing  • Response Formatting          │
│  • Error Handling             • Audit Logging                │
└─────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                        │
├─────────────────────────────────────────────────────────────┤
│  • EMI Calculation           • Payment Allocation            │
│  • Interest Computation      • Adjustment Approval           │
│  • Prepayment Processing     • Statement Generation          │
│  • Mandate Management        • Portfolio Analytics           │
└─────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                  Data Access Layer (SQLAlchemy)              │
├─────────────────────────────────────────────────────────────┤
│  • 10 ORM Models             • Transaction Management        │
│  • Query Optimization        • Connection Pooling            │
└─────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                  Database Layer (PostgreSQL)                 │
├─────────────────────────────────────────────────────────────┤
│  • 10 Tables                 • 2 Views                       │
│  • 2 Triggers                • Indexes & Constraints         │
│  • Audit Trail               • Data Integrity                │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

1. **EMI Management**
   - Automated schedule generation
   - Payment tracking and allocation
   - Overdue detection and monitoring
   - Partial payment handling

2. **Repayment Processing**
   - Multi-mode payment collection (Cash, Cheque, NEFT, IMPS, RTGS, UPI)
   - Maker-checker verification
   - Reversal capabilities
   - Payment allocation rules

3. **Interest Accrual**
   - Daily interest computation
   - Reducing balance method
   - Cumulative tracking
   - Bulk processing support

4. **Loan Adjustments**
   - Waiver management
   - Write-off processing
   - Penalty adjustments
   - Maker-checker approval

5. **Prepayment & Foreclosure**
   - Part payment processing
   - Full prepayment handling
   - Foreclosure management
   - Prepayment charge calculation

6. **Statement Generation**
   - Monthly/Quarterly/Annual statements
   - On-demand generation
   - Bulk processing
   - Transaction history

7. **Auto-Debit Mandates**
   - NACH setup
   - E-Mandate configuration
   - Standing instructions
   - Mandate lifecycle management

8. **Portfolio Health Monitoring**
   - NPA tracking
   - DPD bucket analysis
   - Collection efficiency
   - Portfolio quality indicators

---

## Database Schema

### Tables Created (10)

#### 1. gold_emi_schedule
```sql
CREATE TABLE gold_emi_schedule (
    id UUID PRIMARY KEY,
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    emi_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    principal_amount DECIMAL(15,2) NOT NULL,
    interest_amount DECIMAL(15,2) NOT NULL,
    total_emi_amount DECIMAL(15,2) NOT NULL,
    outstanding_principal DECIMAL(15,2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending',
    paid_amount DECIMAL(15,2) DEFAULT 0,
    paid_date DATE,
    paid_principal DECIMAL(15,2),
    paid_interest DECIMAL(15,2),
    waived_amount DECIMAL(15,2),
    penalty_amount DECIMAL(15,2),
    overdue_days INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Stores EMI schedule with payment tracking  
**Key Features**: Payment status tracking, partial payments, overdue calculation

#### 2. gold_repayment_transactions
```sql
CREATE TABLE gold_repayment_transactions (
    id UUID PRIMARY KEY,
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    transaction_date DATE NOT NULL,
    payment_mode VARCHAR(20) NOT NULL,
    amount_paid DECIMAL(15,2) NOT NULL,
    principal_paid DECIMAL(15,2) NOT NULL,
    interest_paid DECIMAL(15,2) NOT NULL,
    penalty_paid DECIMAL(15,2) DEFAULT 0,
    other_charges_paid DECIMAL(15,2) DEFAULT 0,
    transaction_reference VARCHAR(100) NOT NULL UNIQUE,
    transaction_status VARCHAR(20) DEFAULT 'pending',
    payment_source VARCHAR(50),
    receipt_number VARCHAR(50),
    created_by_user_id UUID NOT NULL,
    verified_by_user_id UUID,
    verified_at TIMESTAMP,
    reversal_reason TEXT,
    reversed_by_user_id UUID,
    reversed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Records all repayment transactions  
**Key Features**: Multi-component payment, verification workflow, reversal support

#### 3. gold_interest_accrual
```sql
CREATE TABLE gold_interest_accrual (
    id UUID PRIMARY KEY,
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    accrual_date DATE NOT NULL,
    principal_balance DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    days_in_period INTEGER NOT NULL,
    interest_accrued DECIMAL(15,2) NOT NULL,
    cumulative_interest DECIMAL(15,2) NOT NULL,
    accrual_status VARCHAR(20) DEFAULT 'posted',
    reversal_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Daily interest accrual ledger  
**Key Features**: Reducing balance calculation, cumulative tracking


#### 4. gold_loan_adjustments
```sql
CREATE TABLE gold_loan_adjustments (
    id UUID PRIMARY KEY,
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    adjustment_date DATE NOT NULL,
    adjustment_type VARCHAR(20) NOT NULL,
    adjustment_category VARCHAR(20) NOT NULL,
    adjustment_amount DECIMAL(15,2) NOT NULL,
    reason TEXT NOT NULL,
    approval_status VARCHAR(20) DEFAULT 'pending',
    requested_by_user_id UUID NOT NULL,
    approved_by_user_id UUID,
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Manages loan adjustments with maker-checker workflow  
**Types**: Waiver, Write-off, Reversal, Correction, Penalty, Rebate

#### 5. gold_loan_prepayments
```sql
CREATE TABLE gold_loan_prepayments (
    id UUID PRIMARY KEY,
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    prepayment_date DATE NOT NULL,
    prepayment_type VARCHAR(20) NOT NULL,
    prepayment_amount DECIMAL(15,2) NOT NULL,
    principal_reduced DECIMAL(15,2) NOT NULL,
    interest_waived DECIMAL(15,2) DEFAULT 0,
    prepayment_charges DECIMAL(15,2) DEFAULT 0,
    outstanding_after_prepayment DECIMAL(15,2) NOT NULL,
    prepayment_status VARCHAR(20) DEFAULT 'pending',
    created_by_user_id UUID NOT NULL,
    approved_by_user_id UUID,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Tracks prepayments and foreclosures  
**Types**: Part Payment, Foreclosure, Full Prepayment

#### 6. gold_loan_statements
```sql
CREATE TABLE gold_loan_statements (
    id UUID PRIMARY KEY,
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    statement_type VARCHAR(20) NOT NULL,
    statement_period_start DATE NOT NULL,
    statement_period_end DATE NOT NULL,
    opening_principal DECIMAL(15,2) NOT NULL,
    closing_principal DECIMAL(15,2) NOT NULL,
    total_credits DECIMAL(15,2) DEFAULT 0,
    total_debits DECIMAL(15,2) DEFAULT 0,
    interest_charged DECIMAL(15,2) DEFAULT 0,
    interest_paid DECIMAL(15,2) DEFAULT 0,
    penalties_charged DECIMAL(15,2) DEFAULT 0,
    statement_generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statement_url TEXT
);
```

**Purpose**: Loan account statement generation  
**Types**: Monthly, Quarterly, Annual, On-Demand

#### 7. gold_auto_debit_mandates
```sql
CREATE TABLE gold_auto_debit_mandates (
    id UUID PRIMARY KEY,
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    mandate_type VARCHAR(30) NOT NULL,
    bank_account_number VARCHAR(50) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    ifsc_code VARCHAR(11) NOT NULL,
    account_holder_name VARCHAR(200) NOT NULL,
    mandate_amount DECIMAL(15,2) NOT NULL,
    mandate_frequency VARCHAR(20) NOT NULL,
    mandate_start_date DATE NOT NULL,
    mandate_end_date DATE NOT NULL,
    mandate_status VARCHAR(20) DEFAULT 'pending',
    mandate_reference VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activated_at TIMESTAMP
);
```

**Purpose**: Auto-debit mandate management  
**Types**: NACH, E-Mandate, Standing Instruction

#### 8. gold_loan_penalties
```sql
CREATE TABLE gold_loan_penalties (
    id UUID PRIMARY KEY,
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    penalty_type VARCHAR(30) NOT NULL,
    penalty_date DATE NOT NULL,
    penalty_amount DECIMAL(15,2) NOT NULL,
    waived_amount DECIMAL(15,2) DEFAULT 0,
    reason TEXT NOT NULL,
    created_by_user_id UUID NOT NULL,
    waived_by_user_id UUID,
    waived_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Penalty tracking and management  
**Types**: Late Payment, Bounced Cheque, Pre-closure, Penal Interest

#### 9. gold_loan_renewals
```sql
CREATE TABLE gold_loan_renewals (
    id UUID PRIMARY KEY,
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    renewal_type VARCHAR(30) NOT NULL,
    renewal_date DATE NOT NULL,
    old_maturity_date DATE NOT NULL,
    new_maturity_date DATE NOT NULL,
    interest_settled DECIMAL(15,2) DEFAULT 0,
    charges_collected DECIMAL(15,2) DEFAULT 0,
    created_by_user_id UUID NOT NULL,
    approved_by_user_id UUID,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Loan renewal and extension tracking  
**Types**: Term Extension, Interest Settlement, Full Renewal

#### 10. gold_repayment_allocation_rules
```sql
CREATE TABLE gold_repayment_allocation_rules (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES gold_products(id),
    allocation_priority INTEGER NOT NULL,
    allocation_component VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Defines payment allocation sequence  
**Components**: Penalty → Charges → Interest → Principal

### Views Created (2)

#### 1. gold_overdue_emis_summary
```sql
CREATE VIEW gold_overdue_emis_summary AS
SELECT 
    loan_account_id,
    COUNT(*) as overdue_count,
    SUM(total_emi_amount - paid_amount) as total_overdue_amount,
    MIN(due_date) as oldest_overdue_date,
    MAX(overdue_days) as max_overdue_days
FROM gold_emi_schedule
WHERE payment_status IN ('overdue', 'partially_paid')
  AND due_date < CURRENT_DATE
GROUP BY loan_account_id;
```

#### 2. gold_loan_portfolio_health
```sql
CREATE VIEW gold_loan_portfolio_health AS
SELECT 
    COUNT(*) as total_active_loans,
    SUM(outstanding_principal) as total_outstanding,
    SUM(CASE WHEN overdue_days > 0 THEN outstanding_principal ELSE 0 END) as total_overdue,
    COUNT(CASE WHEN is_npa THEN 1 END) as npa_loans,
    SUM(CASE WHEN is_npa THEN outstanding_principal ELSE 0 END) as npa_amount,
    COUNT(CASE WHEN overdue_days BETWEEN 0 AND 30 THEN 1 END) as dpd_0_30,
    COUNT(CASE WHEN overdue_days BETWEEN 31 AND 60 THEN 1 END) as dpd_31_60,
    COUNT(CASE WHEN overdue_days BETWEEN 61 AND 90 THEN 1 END) as dpd_61_90,
    COUNT(CASE WHEN overdue_days > 90 THEN 1 END) as dpd_90_plus
FROM gold_loan_accounts
WHERE loan_status = 'active';
```

### Triggers Created (2)

#### 1. update_loan_outstanding_on_repayment
```sql
CREATE OR REPLACE FUNCTION update_loan_outstanding()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.transaction_status = 'completed' THEN
        UPDATE gold_loan_accounts
        SET outstanding_principal = outstanding_principal - NEW.principal_paid,
            outstanding_interest = outstanding_interest - NEW.interest_paid,
            total_paid = total_paid + NEW.amount_paid,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.loan_account_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_loan_outstanding_on_repayment
    AFTER INSERT OR UPDATE ON gold_repayment_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_loan_outstanding();
```

#### 2. mark_emi_overdue
```sql
CREATE OR REPLACE FUNCTION mark_emi_overdue()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.due_date < CURRENT_DATE AND NEW.payment_status = 'pending' THEN
        NEW.payment_status := 'overdue';
        NEW.overdue_days := CURRENT_DATE - NEW.due_date;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER mark_emi_overdue
    BEFORE UPDATE ON gold_emi_schedule
    FOR EACH ROW
    EXECUTE FUNCTION mark_emi_overdue();
```

---

## Backend Implementation

### Models (10 SQLAlchemy Models)

Location: `services/gold/app/models/repayment.py`

**Models**:
1. `EMISchedule` - EMI schedule tracking
2. `RepaymentTransaction` - Payment transactions
3. `InterestAccrual` - Interest computation
4. `LoanAdjustment` - Adjustments and waivers
5. `LoanPrepayment` - Prepayment records
6. `LoanStatement` - Account statements
7. `AutoDebitMandate` - Auto-debit setup
8. `LoanPenalty` - Penalty tracking
9. `LoanRenewal` - Renewal records
10. `RepaymentAllocationRule` - Allocation rules

### Schemas (40+ Pydantic Schemas)

Location: `services/gold/app/schemas/repayment.py`

**Schema Categories**:
- **Base Schemas**: Core data structures
- **Create Schemas**: Request validation
- **Response Schemas**: API responses
- **Update Schemas**: Modification requests
- **Summary Schemas**: Aggregated data
- **Enums**: Status and type definitions

### API Router

Location: `services/gold/app/routers/repayment.py`

**Endpoint Groups** (40+ endpoints):
1. EMI Schedule (6 endpoints)
2. Repayment Transactions (7 endpoints)
3. Interest Accrual (3 endpoints)
4. Loan Adjustments (3 endpoints)
5. Prepayments (3 endpoints)
6. Statements (3 endpoints)
7. Auto-Debit Mandates (3 endpoints)
8. Penalties (3 endpoints)
9. Renewals (3 endpoints)
10. Allocation Rules (2 endpoints)
11. Summary & Analytics (4 endpoints)

---

## Frontend Implementation

### Pages (8 Complete Pages)

Location: `apps/customer-app/app/gold-lending/servicing/`

#### 1. EMI Schedule Management
**File**: `emi-schedule/page.tsx`  
**Features**:
- EMI schedule visualization
- Payment status tracking
- Overdue EMI monitoring
- Schedule generation
- Payment allocation display
- Summary dashboard

#### 2. Repayment Collections
**File**: `repayments/page.tsx`  
**Features**:
- Payment recording form
- Multi-mode payment support
- Verification workflow
- Reversal capabilities
- Payment history
- Summary statistics

#### 3. Interest Accrual Dashboard
**File**: `interest/page.tsx`  
**Features**:
- Daily accrual tracking
- Bulk accrual processing
- Interest calculation
- Cumulative tracking
- Date range filtering

#### 4. Adjustments Management
**File**: `adjustments/page.tsx`  
**Features**:
- Adjustment request form
- Maker-checker approval
- Waiver management
- Write-off processing
- Audit trail

#### 5. Prepayment Processing
**File**: `prepayments/page.tsx`  
**Features**:
- Part payment recording
- Foreclosure management
- Prepayment charges
- Approval workflow
- Outstanding recalculation

#### 6. Statement Generation
**File**: `statements/page.tsx`  
**Features**:
- Statement generation form
- Bulk processing
- Multiple statement types
- Download capabilities
- Transaction history

#### 7. Auto-Debit Mandates
**File**: `mandates/page.tsx`  
**Features**:
- Mandate setup form
- Bank account linkage
- NACH/E-Mandate support
- Mandate lifecycle tracking
- Status management

#### 8. Portfolio Health Dashboard
**File**: `portfolio/page.tsx`  
**Features**:
- Portfolio KPIs
- NPA tracking
- DPD bucket analysis
- Collection efficiency
- Health score indicators
- Quick action links

### API Integration

Location: `apps/customer-app/app/gold-lending/goldApi.ts`

**Added 40+ API Methods**:
```typescript
// EMI Schedule
generateEMISchedule()
getEMISchedule()
getOverdueEMIs()
updateEMISchedule()
getEMISummary()

// Repayments
createRepayment()
getRepayments()
getRepayment()
verifyRepayment()
reverseRepayment()
getRepaymentSummary()

// Interest Accrual
createInterestAccrual()
getInterestAccruals()
bulkInterestAccrual()

// ... and 27 more methods
```

---

## API Endpoints

### Base URL
```
/api/v1/gold
```

### EMI Schedule Endpoints

#### Generate EMI Schedule
```http
POST /emi-schedule?loan_account_id={id}
```

#### Get EMI Schedule
```http
GET /emi-schedule/{loan_account_id}?payment_status={status}
```

#### Get Overdue EMIs
```http
GET /emi-schedule/{loan_account_id}/overdue
```

#### Update EMI Schedule
```http
PATCH /emi-schedule/{schedule_id}
```

#### Get EMI Summary
```http
GET /emi-schedule/{loan_account_id}/summary
```

### Repayment Endpoints

#### Create Repayment
```http
POST /repayments
Content-Type: application/json

{
  "loan_account_id": "uuid",
  "transaction_date": "2026-07-03",
  "payment_mode": "cash",
  "amount_paid": 10000.00,
  "principal_paid": 8000.00,
  "interest_paid": 2000.00,
  "transaction_reference": "TXN123456"
}
```

#### List Repayments
```http
GET /repayments?loan_account_id={id}&payment_mode={mode}&from_date={date}
```

#### Verify Repayment
```http
POST /repayments/{transaction_id}/verify
Content-Type: application/json

{
  "verified_by_user_id": "uuid"
}
```

#### Reverse Repayment
```http
POST /repayments/{transaction_id}/reverse
Content-Type: application/json

{
  "reversed_by_user_id": "uuid",
  "reversal_reason": "Payment bounced"
}
```

### Interest Accrual Endpoints

#### Create Interest Accrual
```http
POST /interest-accrual
Content-Type: application/json

{
  "loan_account_id": "uuid",
  "accrual_date": "2026-07-03",
  "principal_balance": 100000.00,
  "interest_rate": 12.00,
  "days_in_period": 1,
  "interest_accrued": 32.88
}
```

#### Bulk Interest Accrual
```http
POST /interest-accrual/bulk
Content-Type: application/json

{
  "loan_account_ids": ["uuid1", "uuid2"],
  "accrual_date": "2026-07-03"
}
```

### Adjustment Endpoints

#### Create Adjustment
```http
POST /adjustments
Content-Type: application/json

{
  "loan_account_id": "uuid",
  "adjustment_date": "2026-07-03",
  "adjustment_type": "waiver",
  "adjustment_category": "interest",
  "adjustment_amount": 5000.00,
  "reason": "Customer hardship case"
}
```

#### Approve Adjustment
```http
POST /adjustments/{adjustment_id}/approve
Content-Type: application/json

{
  "approved_by_user_id": "uuid",
  "approval_status": "approved"
}
```

---

## Business Logic

### EMI Calculation

**Formula**: Equal Monthly Installment (Reducing Balance)
```
EMI = [P × r × (1+r)^n] / [(1+r)^n - 1]

Where:
P = Principal amount
r = Monthly interest rate (annual rate / 12 / 100)
n = Loan tenure in months
```

**Implementation**:
```python
def calculate_emi(principal, annual_rate, tenure_months):
    monthly_rate = annual_rate / 12 / 100
    emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / \
          ((1 + monthly_rate) ** tenure_months - 1)
    return round(emi, 2)
```

### Interest Accrual

**Method**: Daily Reducing Balance
```
Daily Interest = (Principal × Annual Rate × Days) / (365 × 100)
```

**Implementation**:
```python
def calculate_daily_interest(principal, annual_rate, days=1):
    daily_rate = annual_rate / 365 / 100
    interest = principal * daily_rate * days
    return round(interest, 2)
```

### Payment Allocation

**Priority Order**:
1. Penalty & Charges
2. Interest Due
3. Principal Due
4. Advance Principal

**Implementation**:
```python
def allocate_payment(amount, outstanding_penalty, outstanding_interest, 
                     outstanding_principal):
    allocation = {
        'penalty': 0,
        'interest': 0,
        'principal': 0
    }
    
    # Allocate to penalty first
    if amount > 0 and outstanding_penalty > 0:
        allocation['penalty'] = min(amount, outstanding_penalty)
        amount -= allocation['penalty']
    
    # Then to interest
    if amount > 0 and outstanding_interest > 0:
        allocation['interest'] = min(amount, outstanding_interest)
        amount -= allocation['interest']
    
    # Finally to principal
    if amount > 0 and outstanding_principal > 0:
        allocation['principal'] = min(amount, outstanding_principal)
    
    return allocation
```

### Overdue Calculation

**DPD (Days Past Due)**:
```python
def calculate_dpd(due_date):
    if due_date >= datetime.now().date():
        return 0
    return (datetime.now().date() - due_date).days
```

**NPA Classification**:
- Standard: DPD < 90 days
- NPA: DPD >= 90 days

### Prepayment Charge

**Formula**:
```
Prepayment Charge = Principal Prepaid × Charge Rate
```

**Implementation**:
```python
def calculate_prepayment_charge(prepaid_principal, charge_rate_percent):
    charge = prepaid_principal * (charge_rate_percent / 100)
    return round(charge, 2)
```

---

## Integration Points

### Integration with Phase 6 (Loan Origination)

**Dependencies**:
- Loan account data from `gold_loan_accounts`
- Disbursement information for EMI calculation
- Customer and product details

**Touch Points**:
- Post-disbursement EMI generation
- Outstanding balance updates
- Loan status transitions

### Integration with Future Phases

**Potential Integrations**:
- **Collections Module**: Overdue loan data feed
- **Accounting**: GL postings for repayments
- **Reporting**: Portfolio analytics data
- **Notifications**: Payment reminders, overdue alerts
- **Customer Portal**: Self-service payment tracking

### External System Integration

**Payment Gateways**:
- UPI integration for digital payments
- NEFT/RTGS confirmation
- Cheque clearing status

**NACH/E-Mandate**:
- Bank mandate registration
- Auto-debit execution
- Mandate status updates

---

## Security & Compliance

### Authentication & Authorization

**Role-Based Access**:
- **Maker**: Create repayments, adjustments, prepayments
- **Checker**: Verify and approve transactions
- **Viewer**: Read-only access to reports
- **Admin**: Full access including reversals

### Audit Trail

**Logged Events**:
- All repayment transactions
- Adjustment approvals/rejections
- Prepayment processing
- Payment reversals
- Mandate changes

**Audit Fields**:
- `created_by_user_id`
- `approved_by_user_id`
- `verified_by_user_id`
- `reversed_by_user_id`
- Timestamps for all actions

### Data Validation

**Input Validation**:
- Amount validations (non-negative, reasonable limits)
- Date validations (not future dates for payments)
- Status transitions (workflow enforcement)
- Reference uniqueness

### Regulatory Compliance

**RBI Guidelines**:
- NPA classification (90 DPD)
- Loan classification standards
- Interest calculation methods
- Recovery procedures

**Audit Requirements**:
- Complete transaction trail
- Maker-checker segregation
- Reversal justification
- Statement generation

---

## Testing Strategy

### Unit Tests

**Test Coverage**:
- EMI calculation accuracy
- Interest accrual computation
- Payment allocation logic
- Overdue calculation
- Prepayment charge calculation

### Integration Tests

**Scenarios**:
- End-to-end repayment flow
- Bulk interest accrual
- Adjustment approval workflow
- Statement generation
- Mandate lifecycle

### API Tests

**Endpoints to Test**:
- All CRUD operations
- Authentication and authorization
- Error handling
- Validation rules
- Response formats

### Performance Tests

**Load Testing**:
- Bulk accrual processing (1000+ loans)
- Concurrent payment processing
- Statement generation at scale
- Portfolio health calculation

---

## Deployment Guide

### Prerequisites

1. **Database Migration**
   ```bash
   # Apply Phase 7 migration
   alembic upgrade head
   ```

2. **Environment Variables**
   ```bash
   GOLD_API_URL=http://localhost:8013
   DATABASE_URL=postgresql://user:pass@localhost:5432/gold_lending
   ```

### Deployment Steps

1. **Backend Deployment**
   ```bash
   cd services/gold
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8013
   ```

2. **Frontend Deployment**
   ```bash
   cd apps/customer-app
   npm install
   npm run build
   npm start
   ```

3. **Database Seeding**
   ```bash
   # Seed allocation rules
   python scripts/seed_allocation_rules.py
   ```

### Health Checks

**API Health**:
```bash
curl http://localhost:8013/health
```

**Database Connectivity**:
```bash
curl http://localhost:8013/api/v1/gold/health/db
```

---

## Statistics

### Code Metrics

**Backend**:
- Models: 10 files (~500 lines)
- Schemas: 40+ schemas (~650 lines)
- Routers: 40+ endpoints (~900 lines)
- **Total Backend**: ~2,050 lines

**Frontend**:
- Pages: 8 complete pages (~4,500 lines)
- API Methods: 40+ methods (~400 lines)
- **Total Frontend**: ~4,900 lines

**Database**:
- Tables: 10
- Views: 2
- Triggers: 2
- Migration: ~900 lines

**Documentation**:
- Technical docs: This file
- Quick start guide: Separate file
- **Total Documentation**: ~2,000 lines

### **Grand Total: ~10,350 lines of code**

---

## Future Enhancements

### Phase 7.1 - Advanced Features
- Predictive analytics for defaults
- Machine learning for collection optimization
- Automated follow-up workflows
- SMS/Email payment reminders

### Phase 7.2 - Integration Enhancements
- Real-time payment gateway integration
- NACH mandate automation
- WhatsApp payment links
- QR code-based payments

### Phase 7.3 - Analytics Enhancements
- Portfolio stress testing
- Vintage analysis
- Cohort performance tracking
- Collection efficiency optimization

---

## Support & Maintenance

### Common Issues

**Issue**: EMI schedule not generating
**Solution**: Verify loan account is in 'active' status and disbursement is complete

**Issue**: Payment allocation incorrect
**Solution**: Check allocation rules configuration for the product

**Issue**: Interest accrual mismatch
**Solution**: Verify principal balance and interest rate in loan account

### Contact

For technical support or questions:
- **Email**: support@goldlending.com
- **Documentation**: /docs/phase7
- **API Reference**: /api/docs

---

**Document Version**: 1.0  
**Last Updated**: July 3, 2026  
**Status**: ✅ Complete
