# Getting Started with Phase 6
## Loan Origination & Disbursement - Quick Start Guide

**Version**: 1.0  
**Date**: July 3, 2026

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- ✅ Phase 5 (Vault & Packet Management) completed
- ✅ PostgreSQL 15+ running
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ Gold service backend running on port 8013
- ✅ Customer app frontend running on port 3000

### Step 1: Run Database Migration

```bash
# Navigate to project root
cd c:\NBFCSUITE

# Run migration
psql -U postgres -d nbfc_gold -f infra/migrations/023_loan_origination_disbursement.sql

# Verify tables created
psql -U postgres -d nbfc_gold -c "\dt gold_loan*"
```

**Expected Output**: 10 tables created

### Step 2: Restart Backend Service

```bash
# The models are already integrated
# Just restart the service

cd services/gold
uvicorn app.main:app --reload --port 8013
```

### Step 3: Access Frontend

```bash
# Frontend pages already created
# Navigate to loan applications

http://localhost:3000/gold-lending/loans
```

### Step 4: Create Your First Application

1. Click **"+ New Application"**
2. Fill in customer and product details
3. Select ornaments from inventory
4. Review and submit
5. Track application through workflow

---

## 📋 Complete Workflow Example

### Scenario: Business Loan Against Gold

**Customer**: John Doe (CUST001)  
**Branch**: Mumbai Central (BR001)  
**Requirement**: ₹1,00,000 for 12 months

### Step-by-Step Process

#### 1. Create Application (2 minutes)

```http
POST /api/v1/gold/applications
{
  "customer_id": "CUST001",
  "product_id": "GOLD_STD_01",
  "branch_id": "BR001",
  "requested_amount": 100000,
  "requested_tenure_months": 12,
  "purpose": "Business expansion",
  "ornament_ids": ["ORN001", "ORN002", "ORN003"]
}
```

**Result**: Application GLA2026070300001 created

#### 2. Submit Application (30 seconds)

```http
POST /api/v1/gold/applications/{id}/submit
{
  "submitted_by": "USER001"
}
```

**Result**: Status changes to 'submitted'

#### 3. Credit Evaluation (5 minutes)

Navigate to: `http://localhost:3000/gold-lending/loans/{id}/credit`

Fill in:
- CIBIL Score: 750
- LTV Ratio: 75%
- Risk Category: Low
- AI Recommendation: ₹95,000

**Result**: Credit evaluation complete

#### 4. Multi-Level Approval (24-72 hours)

**Level 1 - Branch Manager**:
```http
POST /api/v1/gold/approvals
{
  "application_id": "{id}",
  "approval_level": 1,
  "approver_role": "branch_manager"
}

POST /api/v1/gold/approvals/{approval_id}/decision
{
  "decision": "approved",
  "comments": "Application meets all criteria"
}
```

**Level 2 - Regional Head** (if amount > ₹1L):
- Similar approval process
- Higher authority review

**Result**: Application approved

#### 5. Loan Account Creation (automated)

Once approved, system automatically:
- Generates loan account number
- Calculates charges
- Creates repayment schedule

#### 6. Disbursement (10 minutes)

Navigate to: `http://localhost:3000/gold-lending/loans/{id}/disbursement`

Select mode: NEFT
Fill in:
- Amount: ₹1,00,000
- Account: 1234567890
- IFSC: HDFC0001234
- Beneficiary: John Doe

**Result**: Funds disbursed, status = 'disbursed'

---

## 🎯 Key Features to Test

### 1. Application Management

**Create**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/applications \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST001","product_id":"PROD001",...}'
```

**List with Filters**:
```bash
curl "http://localhost:8013/api/v1/gold/applications?status=submitted&branch_id=BR001"
```

**Get Details**:
```bash
curl http://localhost:8013/api/v1/gold/applications/{id}
```

### 2. Credit Evaluation

**Create Evaluation**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/credit-evaluations \
  -H "Content-Type: application/json" \
  -d '{"application_id":"{id}","cibil_score":750,"ltv_ratio":75.0,...}'
```

**Get Evaluation**:
```bash
curl http://localhost:8013/api/v1/gold/applications/{id}/credit-evaluation
```

### 3. Approval Workflow

**Create Approval Level**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/approvals \
  -H "Content-Type: application/json" \
  -d '{"application_id":"{id}","approval_level":1,"approver_role":"branch_manager"}'
```

**Submit Decision**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/approvals/{approval_id}/decision \
  -H "Content-Type: application/json" \
  -d '{"decision":"approved","comments":"Approved"}'
```

### 4. Disbursements

**Create Disbursement**:
```bash
curl -X POST http://localhost:8013/api/v1/gold/disbursements \
  -H "Content-Type: application/json" \
  -d '{"application_id":"{id}","disbursement_mode":"neft",...}'
```

**Get Disbursements**:
```bash
curl http://localhost:8013/api/v1/gold/applications/{id}/disbursements
```

### 5. Statistics & Summary

**Application Summary**:
```bash
curl "http://localhost:8013/api/v1/gold/applications/summary?branch_id=BR001"
```

**Loan Portfolio**:
```bash
curl "http://localhost:8013/api/v1/gold/loan-accounts/portfolio?branch_id=BR001"
```

---

## 🔍 Frontend Pages Guide

### 1. Application Listing
**URL**: `/gold-lending/loans`

**Features**:
- Filter by status, stage, branch, date range
- Summary cards showing counts
- Amount statistics
- Clickable rows for details

### 2. New Application
**URL**: `/gold-lending/loans/new`

**Steps**:
1. Enter customer and product details
2. Select ornaments to pledge
3. Review and submit

**Validations**:
- Amount within product limits
- Tenure within product range
- Sufficient collateral value (LTV check)

### 3. Application Detail
**URL**: `/gold-lending/loans/{id}`

**Tabs**:
- **Overview**: Basic details, timeline, remarks
- **Ornaments**: Pledged items, collateral value
- **Credit**: Evaluation details, risk assessment
- **Approvals**: Approval workflow status
- **Disbursement**: Fund transfer records

### 4. Credit Evaluation
**URL**: `/gold-lending/loans/{id}/credit`

**Sections**:
- Credit Bureau Data (CIBIL)
- Financial Assessment
- AI Recommendation
- Risk Assessment

### 5. Disbursement
**URL**: `/gold-lending/loans/{id}/disbursement`

**Modes**:
- NEFT/IMPS/RTGS: Bank transfer
- UPI: Instant payment
- Cheque: Physical cheque
- Cash: Branch disbursement

---

## 📊 Sample Test Data

### Test Customer IDs
```
CUST001 - High creditworthy customer
CUST002 - Medium creditworthy customer
CUST003 - Low creditworthy customer
```

### Test Product IDs
```
GOLD_STD_01 - Standard Gold Loan (8-12%)
GOLD_PREM_01 - Premium Gold Loan (6-8%)
```

### Test Branch IDs
```
BR001 - Mumbai Central
BR002 - Delhi North
BR003 - Bangalore South
```

### Sample Ornament IDs
```
ORN001 - 22K Gold Necklace (50g, ₹2,50,000)
ORN002 - 24K Gold Bangles (30g, ₹1,80,000)
ORN003 - 18K Gold Ring (10g, ₹50,000)
```

---

## 🎨 UI/UX Highlights

### Color Coding

**Status Badges**:
- 🔵 Draft: Gray
- 🔵 Submitted: Blue
- 🟡 Under Review: Yellow
- 🟢 Approved: Green
- 🔴 Rejected: Red
- 🟣 Disbursed: Purple

**Stage Badges**:
- Application: Blue
- Credit Evaluation: Yellow
- Approval: Orange
- Documentation: Indigo
- Disbursement: Green
- Completed: Gray

### Key Metrics Display

**Application Listing**:
- Total Applications
- Pending Count
- Approved Count
- Rejected Count
- Total Requested Amount
- Total Sanctioned Amount

**Application Detail**:
- Requested Amount (Blue)
- Sanctioned Amount (Green)
- Collateral Value (Gray)
- LTV Ratio (%)

---

## ⚙️ Configuration

### Product Configuration

Set up gold loan products with:
- Interest rate range
- Tenure limits
- Amount limits
- LTV limits
- Charges structure

### Approval Configuration

Configure approval hierarchy:
```python
APPROVAL_HIERARCHY = {
    "level_1": {
        "role": "branch_manager",
        "amount_limit": 100000,
        "sla_hours": 24
    },
    "level_2": {
        "role": "regional_head",
        "amount_limit": 500000,
        "sla_hours": 48
    },
    "level_3": {
        "role": "zonal_head",
        "amount_limit": None,  # No limit
        "sla_hours": 72
    }
}
```

### Disbursement Configuration

Enable/disable payment modes:
```python
DISBURSEMENT_MODES = {
    "neft": True,
    "imps": True,
    "rtgs": True,
    "upi": True,
    "cheque": True,
    "cash": False  # Disabled for security
}
```

---

## 🐛 Troubleshooting

### Issue: Migration Failed

**Error**: Table already exists

**Solution**:
```bash
# Drop existing tables (CAUTION: destroys data)
psql -U postgres -d nbfc_gold -c "DROP TABLE IF EXISTS gold_loan_applications CASCADE;"

# Re-run migration
psql -U postgres -d nbfc_gold -f infra/migrations/023_loan_origination_disbursement.sql
```

### Issue: API Endpoint Not Found

**Error**: 404 Not Found

**Solution**:
1. Verify router included in main.py
2. Check endpoint URL format
3. Restart backend service

### Issue: Frontend Page Not Loading

**Error**: Page not found

**Solution**:
1. Verify file structure: `app/gold-lending/loans/page.tsx`
2. Check Next.js routing
3. Rebuild frontend: `npm run build`

### Issue: Disbursement Fails

**Error**: Invalid bank details

**Solution**:
1. Verify IFSC code format
2. Check account number length
3. Validate beneficiary name

---

## 📞 Support

### Documentation
- Full Documentation: `PHASE6_LOAN_ORIGINATION.md`
- API Reference: See Phase 6 docs
- Database Schema: `023_loan_origination_disbursement.sql`

### Common Commands

```bash
# Check backend logs
tail -f services/gold/logs/app.log

# Check frontend logs
npm run dev  # Development mode with hot reload

# Database queries
psql -U postgres -d nbfc_gold

# Count applications
SELECT COUNT(*) FROM gold_loan_applications;

# View recent applications
SELECT * FROM gold_loan_applications ORDER BY created_at DESC LIMIT 10;
```

---

## 🎉 Success Checklist

- [ ] Database migration completed
- [ ] All 10 tables created
- [ ] Backend service running
- [ ] Frontend accessible
- [ ] Can create new application
- [ ] Can submit application
- [ ] Can perform credit evaluation
- [ ] Can approve application
- [ ] Can create disbursement
- [ ] Can view statistics

---

**Quick Start Guide - Phase 6**  
**NBFCSuite Gold Lending Platform**  
**July 3, 2026**
