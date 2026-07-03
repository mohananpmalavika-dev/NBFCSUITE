# Phase 7: Loan Servicing & Repayment - Quick Start Guide

## Overview

This guide helps you quickly set up and use the Phase 7 Loan Servicing & Repayment features.

---

## Table of Contents

1. [Quick Setup](#quick-setup)
2. [Common Workflows](#common-workflows)
3. [API Examples](#api-examples)
4. [Frontend Usage](#frontend-usage)
5. [Troubleshooting](#troubleshooting)

---

## Quick Setup

### 1. Database Setup

```bash
# Run Phase 7 migration
cd infra
psql -U postgres -d gold_lending -f migrations/024_loan_servicing_repayment.sql
```

**What it creates**:
- 10 tables for servicing operations
- 2 views for portfolio analytics
- 2 triggers for automatic updates
- Indexes for performance

### 2. Start Backend Service

```bash
cd services/gold
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8013
```

**Verify**:
```bash
curl http://localhost:8013/health
# Should return: {"status": "healthy"}
```

### 3. Start Frontend

```bash
cd apps/customer-app
npm install
npm run dev
```

**Access**:
- EMI Schedule: http://localhost:3000/gold-lending/servicing/emi-schedule
- Repayments: http://localhost:3000/gold-lending/servicing/repayments
- Portfolio: http://localhost:3000/gold-lending/servicing/portfolio

---

## Common Workflows

### Workflow 1: Record a Repayment

**Steps**:
1. Navigate to Repayments page
2. Click "+ Record Payment"
3. Fill in details:
   - Loan Account ID
   - Payment Date
   - Payment Mode (Cash/UPI/NEFT, etc.)
   - Amount Paid
   - Transaction Reference
4. Submit for verification
5. Checker verifies the payment
6. System updates loan outstanding automatically

**API Call**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/repayments \
  -H "Content-Type: application/json" \
  -d '{
    "loan_account_id": "loan-uuid-here",
    "transaction_date": "2026-07-03",
    "payment_mode": "cash",
    "amount_paid": 10000.00,
    "principal_paid": 8000.00,
    "interest_paid": 2000.00,
    "transaction_reference": "CASH-20260703-001",
    "created_by_user_id": "user-uuid-here"
  }'
```

### Workflow 2: Generate EMI Schedule

**Steps**:
1. Go to EMI Schedule page
2. Enter Loan Account ID
3. Click "Generate Schedule"
4. System creates EMI entries based on:
   - Loan amount
   - Interest rate
   - Tenure
   - Repayment frequency
5. View generated schedule

**API Call**:
```bash
curl -X POST "http://localhost:8013/api/v1/gold/emi-schedule?loan_account_id=loan-uuid-here"
```

### Workflow 3: Daily Interest Accrual

**Steps**:
1. Navigate to Interest Accrual page
2. Click "Bulk Accrual"
3. Enter loan account IDs (comma-separated)
4. Select accrual date
5. System calculates daily interest for all accounts
6. Interest gets added to outstanding

**API Call**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/interest-accrual/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "loan_account_ids": ["loan1-uuid", "loan2-uuid"],
    "accrual_date": "2026-07-03"
  }'
```

### Workflow 4: Process Prepayment

**Steps**:
1. Go to Prepayments page
2. Click "+ New Prepayment"
3. Select prepayment type:
   - Part Payment
   - Foreclosure
   - Full Prepayment
4. Enter prepayment amount
5. System calculates:
   - Principal reduction
   - Interest waived
   - Prepayment charges
   - New outstanding
6. Submit for approval
7. Approver reviews and approves
8. Outstanding gets updated

**API Call**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/prepayments \
  -H "Content-Type: application/json" \
  -d '{
    "loan_account_id": "loan-uuid-here",
    "prepayment_date": "2026-07-03",
    "prepayment_type": "part_payment",
    "prepayment_amount": 50000.00,
    "principal_reduced": 48000.00,
    "prepayment_charges": 2000.00,
    "outstanding_after_prepayment": 50000.00,
    "created_by_user_id": "user-uuid-here"
  }'
```

### Workflow 5: Create Adjustment (Waiver)

**Steps**:
1. Navigate to Adjustments page
2. Click "+ New Adjustment"
3. Select adjustment type (Waiver/Write-off)
4. Select category (Principal/Interest/Penalty)
5. Enter amount and reason
6. Submit for approval
7. Approver reviews request
8. On approval, adjustment is posted

**API Call**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/adjustments \
  -H "Content-Type: application/json" \
  -d '{
    "loan_account_id": "loan-uuid-here",
    "adjustment_date": "2026-07-03",
    "adjustment_type": "waiver",
    "adjustment_category": "interest",
    "adjustment_amount": 5000.00,
    "reason": "Customer facing financial hardship",
    "requested_by_user_id": "user-uuid-here"
  }'
```

### Workflow 6: Setup Auto-Debit Mandate

**Steps**:
1. Go to Mandates page
2. Click "+ New Mandate"
3. Enter loan account details
4. Select mandate type (NACH/E-Mandate)
5. Enter bank account details:
   - Account number
   - Bank name
   - IFSC code
   - Account holder name
6. Set mandate amount and frequency
7. Submit to bank for registration
8. Track mandate status

**API Call**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/mandates \
  -H "Content-Type: application/json" \
  -d '{
    "loan_account_id": "loan-uuid-here",
    "mandate_type": "nach",
    "bank_account_number": "1234567890",
    "bank_name": "HDFC Bank",
    "ifsc_code": "HDFC0001234",
    "account_holder_name": "John Doe",
    "mandate_amount": 15000.00,
    "mandate_frequency": "monthly",
    "mandate_start_date": "2026-08-01",
    "mandate_end_date": "2028-07-31"
  }'
```

### Workflow 7: Generate Loan Statement

**Steps**:
1. Navigate to Statements page
2. Click "+ New Statement"
3. Enter loan account ID
4. Select statement type:
   - Monthly
   - Quarterly
   - Annual
   - On-Demand
5. Select period dates
6. System generates statement with:
   - Opening/closing balance
   - All transactions
   - Interest charged/paid
   - Summary
7. Download PDF

**API Call**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/statements \
  -H "Content-Type: application/json" \
  -d '{
    "loan_account_id": "loan-uuid-here",
    "statement_type": "monthly",
    "statement_period_start": "2026-06-01",
    "statement_period_end": "2026-06-30",
    "opening_principal": 100000.00,
    "closing_principal": 92000.00
  }'
```

### Workflow 8: Monitor Portfolio Health

**Steps**:
1. Go to Portfolio Health Dashboard
2. View key metrics:
   - Total active loans
   - Total outstanding
   - Overdue amount
   - NPA amount
3. Check DPD buckets:
   - 0-30 days (Current)
   - 31-60 days (Early stage)
   - 61-90 days (High risk)
   - 90+ days (NPA)
4. Monitor collection efficiency
5. Use quick action links for follow-up

**API Call**:
```bash
curl http://localhost:8013/api/v1/gold/loan-accounts/portfolio
```

---

## API Examples

### Get EMI Schedule

```bash
# Get all EMIs for a loan
curl "http://localhost:8013/api/v1/gold/emi-schedule/loan-uuid-here"

# Get only overdue EMIs
curl "http://localhost:8013/api/v1/gold/emi-schedule/loan-uuid-here/overdue"

# Get EMI summary
curl "http://localhost:8013/api/v1/gold/emi-schedule/loan-uuid-here/summary"
```

**Response**:
```json
{
  "total_emis": 12,
  "paid_emis": 3,
  "pending_emis": 9,
  "overdue_emis": 1,
  "total_emi_amount": 120000.00,
  "total_paid": 30000.00,
  "total_outstanding": 90000.00,
  "next_emi_date": "2026-08-01",
  "next_emi_amount": 10000.00
}
```

### List Repayments with Filters

```bash
# All repayments for a loan
curl "http://localhost:8013/api/v1/gold/repayments?loan_account_id=loan-uuid-here"

# Filter by payment mode
curl "http://localhost:8013/api/v1/gold/repayments?payment_mode=upi"

# Filter by date range
curl "http://localhost:8013/api/v1/gold/repayments?from_date=2026-06-01&to_date=2026-06-30"

# Filter by status
curl "http://localhost:8013/api/v1/gold/repayments?transaction_status=pending"
```

### Verify Repayment

```bash
curl -X POST http://localhost:8013/api/v1/gold/repayments/txn-uuid-here/verify \
  -H "Content-Type: application/json" \
  -d '{
    "verified_by_user_id": "checker-uuid-here"
  }'
```

### Reverse Repayment

```bash
curl -X POST http://localhost:8013/api/v1/gold/repayments/txn-uuid-here/reverse \
  -H "Content-Type: application/json" \
  -d '{
    "reversed_by_user_id": "user-uuid-here",
    "reversal_reason": "Payment bounced - insufficient funds"
  }'
```

### Get Interest Accruals

```bash
# Get accruals for a loan
curl "http://localhost:8013/api/v1/gold/interest-accrual/loan-uuid-here"

# Filter by date range
curl "http://localhost:8013/api/v1/gold/interest-accrual/loan-uuid-here?from_date=2026-06-01&to_date=2026-06-30"
```

### List Adjustments

```bash
# All adjustments
curl "http://localhost:8013/api/v1/gold/adjustments"

# Filter by loan
curl "http://localhost:8013/api/v1/gold/adjustments?loan_account_id=loan-uuid-here"

# Filter by type
curl "http://localhost:8013/api/v1/gold/adjustments?adjustment_type=waiver"

# Filter by approval status
curl "http://localhost:8013/api/v1/gold/adjustments?approval_status=pending"
```

### Approve Adjustment

```bash
curl -X POST http://localhost:8013/api/v1/gold/adjustments/adj-uuid-here/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approved_by_user_id": "approver-uuid-here",
    "approval_status": "approved"
  }'
```

### Bulk Statement Generation

```bash
curl -X POST http://localhost:8013/api/v1/gold/statements/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "loan_account_ids": ["loan1-uuid", "loan2-uuid", "loan3-uuid"],
    "period_start": "2026-06-01",
    "period_end": "2026-06-30",
    "statement_type": "monthly"
  }'
```

---

## Frontend Usage

### Access Pages

**EMI Schedule Management**:
```
http://localhost:3000/gold-lending/servicing/emi-schedule
```

**Repayment Collections**:
```
http://localhost:3000/gold-lending/servicing/repayments
```

**Interest Accrual Dashboard**:
```
http://localhost:3000/gold-lending/servicing/interest
```

**Adjustments Management**:
```
http://localhost:3000/gold-lending/servicing/adjustments
```

**Prepayment Processing**:
```
http://localhost:3000/gold-lending/servicing/prepayments
```

**Statement Generation**:
```
http://localhost:3000/gold-lending/servicing/statements
```

**Auto-Debit Mandates**:
```
http://localhost:3000/gold-lending/servicing/mandates
```

**Portfolio Health Dashboard**:
```
http://localhost:3000/gold-lending/servicing/portfolio
```

### Key Features in UI

**EMI Schedule Page**:
- ✅ Generate EMI schedule
- ✅ View payment status
- ✅ Filter by status
- ✅ Show overdue only
- ✅ EMI summary cards
- ✅ Overdue days tracking

**Repayments Page**:
- ✅ Record new payment
- ✅ Multi-mode support (Cash, UPI, NEFT, etc.)
- ✅ Verify payments
- ✅ Reverse payments
- ✅ Filter by date/mode/status
- ✅ Payment summary statistics

**Interest Page**:
- ✅ Create manual accrual
- ✅ Bulk accrual processing
- ✅ Interest calculator
- ✅ Date range filtering
- ✅ Cumulative tracking

**Adjustments Page**:
- ✅ Create adjustment request
- ✅ Maker-checker workflow
- ✅ Multiple types (Waiver, Write-off, etc.)
- ✅ Approve/Reject actions
- ✅ Audit trail

**Prepayments Page**:
- ✅ Record prepayment
- ✅ Type selection (Part/Full/Foreclosure)
- ✅ Charge calculation
- ✅ Approval workflow
- ✅ Outstanding recalculation

**Statements Page**:
- ✅ Single statement generation
- ✅ Bulk generation
- ✅ Multiple types (Monthly/Quarterly/Annual)
- ✅ Download capability
- ✅ Transaction history

**Mandates Page**:
- ✅ Setup new mandate
- ✅ Bank account details
- ✅ Multiple types (NACH/E-Mandate/SI)
- ✅ Frequency configuration
- ✅ Status tracking

**Portfolio Page**:
- ✅ Key metrics dashboard
- ✅ NPA tracking
- ✅ DPD bucket analysis
- ✅ Collection efficiency
- ✅ Health score indicator
- ✅ Visual analytics
- ✅ Quick action links

---

## Troubleshooting

### Issue: EMI Schedule Not Generating

**Symptom**: Click "Generate Schedule" but nothing happens

**Causes & Solutions**:
1. **Loan not active**
   ```sql
   SELECT loan_status FROM gold_loan_accounts WHERE id = 'loan-uuid';
   -- Should be 'active'
   ```

2. **Disbursement not complete**
   ```sql
   SELECT disbursement_status FROM gold_disbursements 
   WHERE loan_account_id = 'loan-uuid';
   -- Should be 'disbursed'
   ```

3. **Schedule already exists**
   ```sql
   SELECT COUNT(*) FROM gold_emi_schedule WHERE loan_account_id = 'loan-uuid';
   -- If > 0, schedule exists. Delete to regenerate.
   ```

### Issue: Payment Not Updating Outstanding

**Symptom**: Repayment recorded but outstanding unchanged

**Causes & Solutions**:
1. **Payment not verified**
   ```sql
   SELECT transaction_status FROM gold_repayment_transactions WHERE id = 'txn-uuid';
   -- Should be 'completed', not 'pending'
   ```
   **Fix**: Verify the payment through UI or API

2. **Trigger not working**
   ```sql
   -- Check if trigger exists
   SELECT tgname FROM pg_trigger WHERE tgname = 'update_loan_outstanding_on_repayment';
   ```
   **Fix**: Re-run migration to create trigger

### Issue: Interest Accrual Mismatch

**Symptom**: Calculated interest doesn't match expectation

**Causes & Solutions**:
1. **Wrong principal balance**
   ```sql
   SELECT outstanding_principal FROM gold_loan_accounts WHERE id = 'loan-uuid';
   ```
   **Fix**: Ensure principal is updated after each payment

2. **Incorrect interest rate**
   ```sql
   SELECT interest_rate FROM gold_loan_accounts WHERE id = 'loan-uuid';
   ```
   **Fix**: Verify rate from product configuration

3. **Days calculation**
   - Formula: `(Principal × Rate × Days) / (365 × 100)`
   - Check days_in_period is correct (usually 1 for daily)

### Issue: Adjustment Not Getting Approved

**Symptom**: Approval button doesn't work

**Causes & Solutions**:
1. **Wrong approval status**
   ```sql
   SELECT approval_status FROM gold_loan_adjustments WHERE id = 'adj-uuid';
   -- Should be 'pending'
   ```

2. **User permissions**
   - Ensure user has 'checker' or 'approver' role
   - Maker cannot approve own request

### Issue: Portfolio Dashboard Shows No Data

**Symptom**: Dashboard is empty or shows zero values

**Causes & Solutions**:
1. **No active loans**
   ```sql
   SELECT COUNT(*) FROM gold_loan_accounts WHERE loan_status = 'active';
   ```

2. **View not created**
   ```sql
   SELECT * FROM gold_loan_portfolio_health;
   ```
   **Fix**: Re-run migration to create view

3. **Branch filter applied**
   - Clear branch filter to see all loans

### Issue: Mandate Status Not Updating

**Symptom**: Mandate stays in 'pending' status

**Causes & Solutions**:
1. **Manual activation required**
   ```sql
   UPDATE gold_auto_debit_mandates 
   SET mandate_status = 'active', activated_at = NOW()
   WHERE id = 'mandate-uuid';
   ```

2. **Bank confirmation pending**
   - Wait for bank registration response
   - Check mandate_reference for tracking

### Database Queries for Debugging

**Check loan servicing status**:
```sql
SELECT 
    la.loan_account_number,
    la.outstanding_principal,
    la.outstanding_interest,
    COUNT(DISTINCT es.id) as total_emis,
    COUNT(DISTINCT rt.id) as total_repayments,
    SUM(rt.amount_paid) as total_paid
FROM gold_loan_accounts la
LEFT JOIN gold_emi_schedule es ON es.loan_account_id = la.id
LEFT JOIN gold_repayment_transactions rt ON rt.loan_account_id = la.id
WHERE la.id = 'loan-uuid-here'
GROUP BY la.id, la.loan_account_number, la.outstanding_principal, la.outstanding_interest;
```

**Find overdue loans**:
```sql
SELECT 
    loan_account_id,
    overdue_count,
    total_overdue_amount,
    max_overdue_days
FROM gold_overdue_emis_summary
WHERE max_overdue_days > 30
ORDER BY max_overdue_days DESC;
```

**Check repayment allocation**:
```sql
SELECT 
    transaction_date,
    amount_paid,
    principal_paid,
    interest_paid,
    penalty_paid,
    transaction_status
FROM gold_repayment_transactions
WHERE loan_account_id = 'loan-uuid-here'
ORDER BY transaction_date DESC;
```

---

## Next Steps

1. **Explore Phase 6**: Loan Origination & Disbursement
   - See how loans are created before servicing

2. **Configure Products**: Set up repayment rules
   - EMI frequency
   - Interest calculation method
   - Prepayment charges
   - Penalty rules

3. **Setup Users & Roles**: Configure access control
   - Makers for transaction entry
   - Checkers for verification
   - Approvers for adjustments

4. **Test Workflows**: Try complete scenarios
   - Loan disbursement → EMI generation → Payment → Closure
   - Overdue handling → Penalty → Collection
   - Prepayment → Outstanding recalculation

5. **Monitor Portfolio**: Use dashboard regularly
   - Track collection efficiency
   - Monitor NPA levels
   - Identify problem accounts

---

## Additional Resources

- **Full Documentation**: `PHASE7_LOAN_SERVICING.md`
- **API Reference**: http://localhost:8013/docs
- **Phase 6 Docs**: `PHASE6_LOAN_ORIGINATION.md`
- **Overall Roadmap**: `GOLD_LENDING_ROADMAP.md`

---

**Version**: 1.0  
**Last Updated**: July 3, 2026  
**Status**: ✅ Ready for Use
