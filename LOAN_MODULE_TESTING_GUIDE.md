# 🧪 Loan Module - Complete Testing Guide

**Date**: July 5, 2026  
**Module**: Loan Management (Phases 1-3)  
**Status**: Ready for End-to-End Testing

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Test Data Setup](#test-data-setup)
3. [Phase 1: Products & Applications](#phase-1-products--applications)
4. [Phase 2: Credit Assessment & Approval](#phase-2-credit-assessment--approval)
5. [Phase 3: Disbursement & Accounts](#phase-3-disbursement--accounts)
6. [Complete End-to-End Flow](#complete-end-to-end-flow)
7. [Edge Cases & Error Scenarios](#edge-cases--error-scenarios)

---

## Prerequisites

### 1. Database Setup
```bash
# Run loan tables migration
psql -U postgres -d nbfc_suite -f database/migrations/add_loan_tables_migration.sql
```

### 2. Authentication
```bash
# Login to get token
POST /api/auth/login
{
  "username": "admin@example.com",
  "password": "Admin@123"
}

# Save the access_token for all subsequent requests
export TOKEN="your_access_token_here"
```

### 3. Required Master Data
- At least 1 loan purpose
- At least 3 document types
- Bank master data (for IFSC lookup)

### 4. Required Customer Data
- At least 1 customer with:
  - Complete KYC
  - At least 1 verified bank account
  - CIBIL score (set manually for testing)
  - Monthly income information

---

## Test Data Setup

### Create Test Loan Purpose (if not exists)
```bash
POST /api/master-data/loan-purposes
{
  "purpose_name": "Personal Loan",
  "purpose_code": "PL",
  "description": "For personal needs",
  "is_active": true
}
```

### Create Test Customer (if not exists)
```bash
POST /api/customers
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "mobile": "9876543210",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "customer_type": "individual",
  "cibil_score": 750,
  "monthly_income": 50000.00
}

# Add verified bank account
POST /api/customers/1/bank-accounts
{
  "account_number": "1234567890",
  "account_holder_name": "John Doe",
  "ifsc_code": "HDFC0001234",
  "bank_name": "HDFC Bank",
  "branch_name": "Mumbai Main",
  "account_type": "savings",
  "is_primary": true,
  "status": "verified"
}
```

---

## Phase 1: Products & Applications

### Step 1: Create Loan Product

**Endpoint**: `POST /api/loans/products`

**Request**:
```json
{
  "product_code": "PL24",
  "product_name": "Personal Loan - 24 Months",
  "product_type": "personal",
  "loan_category": "unsecured",
  "interest_rate_type": "reducing",
  "min_interest_rate": 10.50,
  "max_interest_rate": 18.00,
  "default_interest_rate": 12.00,
  "min_loan_amount": 50000,
  "max_loan_amount": 1000000,
  "min_tenure_months": 6,
  "max_tenure_months": 60,
  "allowed_tenures": [6, 12, 18, 24, 36, 48, 60],
  "processing_fee_type": "percentage",
  "processing_fee_value": 2.0,
  "documentation_charges": 500.00,
  "insurance_applicable": true,
  "insurance_percentage": 1.0,
  "penal_interest_rate": 2.00,
  "grace_period_days": 3,
  "min_age": 21,
  "max_age": 65,
  "min_monthly_income": 25000.00,
  "min_cibil_score": 650,
  "employment_types": ["salaried", "self_employed"],
  "required_documents": [1, 2, 3],
  "is_active": true,
  "is_featured": true,
  "description": "Quick personal loan up to ₹10 lakhs",
  "features": ["Quick approval", "Minimal documentation", "Flexible tenure"],
  "terms_and_conditions": "Standard terms apply"
}
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "product_code": "PL24",
    "product_name": "Personal Loan - 24 Months",
    ...
  },
  "message": "Loan product created successfully"
}
```

**Save**: `product_id = 1`

### Step 2: Calculate EMI (Optional)

**Endpoint**: `POST /api/loans/products/calculate-emi`

**Request**:
```json
{
  "loan_amount": 500000,
  "interest_rate": 12.0,
  "tenure_months": 24,
  "interest_rate_type": "reducing"
}
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "loan_amount": 500000.00,
    "interest_rate": 12.00,
    "tenure_months": 24,
    "emi_amount": 23539.00,
    "total_interest": 64936.00,
    "total_repayment": 564936.00,
    "processing_fee": 10000.00,
    "net_disbursement": 490000.00
  }
}
```

### Step 3: Check Eligibility (Optional)

**Endpoint**: `GET /api/loans/products/1/check-eligibility`

**Query Parameters**:
- `customer_age=30`
- `customer_income=50000`
- `customer_cibil=750`
- `requested_amount=500000`

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "eligible": true,
    "eligibility_details": {
      "age_check": {"eligible": true, "reason": "Age is within range"},
      "income_check": {"eligible": true, "reason": "Income meets minimum"},
      "cibil_check": {"eligible": true, "reason": "CIBIL score is good"},
      "amount_check": {"eligible": true, "reason": "Amount is within limits"}
    }
  }
}
```

### Step 4: Create Loan Application

**Endpoint**: `POST /api/loans/applications`

**Request**:
```json
{
  "customer_id": 1,
  "loan_product_id": 1,
  "requested_amount": 500000.00,
  "tenure_months": 24,
  "loan_purpose_id": 1,
  "purpose_description": "Home renovation",
  "disbursement_bank_account_id": 1,
  "disbursement_mode": "neft",
  "applicant_remarks": "Need funds urgently"
}
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "application_number": "APP-202607-0001",
    "customer_id": 1,
    "loan_product_id": 1,
    "requested_amount": 500000.00,
    "tenure_months": 24,
    "interest_rate": 12.00,
    "emi_amount": 23539.00,
    "total_interest": 64936.00,
    "total_repayment": 564936.00,
    "processing_fee": 10000.00,
    "insurance_amount": 5000.00,
    "documentation_charges": 500.00,
    "total_deductions": 15500.00,
    "net_disbursement": 484500.00,
    "status": "draft",
    "application_date": "2026-07-05",
    ...
  },
  "message": "Loan application created successfully"
}
```

**Save**: `application_id = 1`

### Step 5: Submit Application

**Endpoint**: `POST /api/loans/applications/1/submit`

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "application_number": "APP-202607-0001",
    "status": "submitted",
    "submission_date": "2026-07-05",
    ...
  },
  "message": "Application submitted successfully"
}
```

---

## Phase 2: Credit Assessment & Approval

### Step 6: Calculate Credit Score

**Endpoint**: `POST /api/loans/credit-assessment/1/calculate`

**Request**:
```json
{
  "monthly_income": 50000.00,
  "monthly_obligations": 10000.00
}
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "application_id": 1,
    "credit_score": 82,
    "risk_rating": "low",
    "factors": {
      "cibil_score": 750,
      "cibil_points": 40.0,
      "monthly_income": 50000.00,
      "income_points": 25.0,
      "debt_to_income_ratio": 20.00,
      "dti_points": 18.0,
      "employment_type": "salaried",
      "employment_points": 10.0,
      "age": 36,
      "age_points": 5.0
    },
    "recommendation": "Loan can be approved"
  }
}
```

### Step 7: Initiate Approval Workflow

**Endpoint**: `POST /api/loans/approval/1/initiate`

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "application_id": 1,
    "status": "pending_approval",
    "approval_levels": 1,
    "current_level": 1,
    "workflow": [
      {
        "level": 1,
        "approver_role": "Credit Officer",
        "max_approval_amount": 500000.00,
        "status": "pending"
      }
    ]
  },
  "message": "Approval workflow initiated"
}
```

### Step 8: Get Pending Approvals

**Endpoint**: `GET /api/loans/approval/pending`

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "pending_approvals": [
      {
        "application_id": 1,
        "application_number": "APP-202607-0001",
        "customer_name": "John Doe",
        "requested_amount": 500000.00,
        "approval_level": 1,
        "approver_role": "Credit Officer",
        "submitted_date": "2026-07-05",
        "credit_score": 82,
        "risk_rating": "low"
      }
    ],
    "total": 1
  }
}
```

### Step 9: Approve Application

**Endpoint**: `POST /api/loans/approval/1/approve`

**Request**:
```json
{
  "comments": "Approved. Good credit profile.",
  "conditions": ["Customer to provide salary slips"]
}
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "application_id": 1,
    "application_number": "APP-202607-0001",
    "status": "approved",
    "approved_amount": 500000.00,
    "approval_date": "2026-07-05",
    "approved_by": "Credit Officer",
    "comments": "Approved. Good credit profile."
  },
  "message": "Application approved successfully"
}
```

---

## Phase 3: Disbursement & Accounts

### Step 10: Generate Sanction Letter

**Endpoint**: `POST /api/loans/disbursement/1/sanction-letter`

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "sanction_number": "SL-202607-000001",
    "sanction_date": "2026-07-05",
    "application_number": "APP-202607-0001",
    "customer_name": "John Doe",
    "customer_id": "CUS-202607-0001",
    "product_name": "Personal Loan - 24 Months",
    "sanctioned_amount": 500000.00,
    "tenure_months": 24,
    "interest_rate": 12.00,
    "emi_amount": 23539.00,
    "processing_fee": 10000.00,
    "documentation_charges": 500.00,
    "insurance_amount": 5000.00,
    "total_deductions": 15500.00,
    "net_disbursement": 484500.00,
    "total_interest": 64936.00,
    "total_repayment": 564936.00,
    "validity_days": 30,
    "expiry_date": "2026-08-04",
    "terms_and_conditions": "Standard terms apply"
  },
  "message": "Sanction letter generated successfully"
}
```

### Step 11: Approve Disbursement

**Endpoint**: `POST /api/loans/disbursement/1/approve`

**Request**:
```json
{
  "bank_account_id": 1,
  "disbursement_date": "2026-07-05",
  "disbursement_mode": "neft",
  "emi_start_day": 5,
  "remarks": "Disbursed via NEFT to primary account"
}
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "loan_account_number": "LN-202607-0001",
    "application_number": "APP-202607-0001",
    "customer_id": 1,
    "disbursement_amount": 484500.00,
    "disbursement_date": "2026-07-05",
    "disbursement_mode": "neft",
    "disbursement_reference": "DISB-20260705143022",
    "bank_account": {
      "account_number": "1234567890",
      "bank_name": "HDFC Bank",
      "ifsc_code": "HDFC0001234",
      "account_holder_name": "John Doe"
    },
    "emi_details": {
      "emi_amount": 23539.00,
      "first_emi_date": "2026-08-05",
      "last_emi_date": "2028-07-05",
      "emi_day": 5,
      "total_emis": 24
    },
    "status": "disbursed",
    "message": "Loan disbursed successfully"
  },
  "message": "Loan disbursed successfully"
}
```

**Save**: `loan_account_number = "LN-202607-0001"`

### Step 12: Get Loan Account Details

**Endpoint**: `GET /api/loans/disbursement/accounts/1?include_schedule=true`

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "loan_account_number": "LN-202607-0001",
    "customer_id": 1,
    "sanctioned_amount": 500000.00,
    "disbursed_amount": 484500.00,
    "outstanding_principal": 500000.00,
    "outstanding_interest": 0.00,
    "total_outstanding": 500000.00,
    "tenure_months": 24,
    "interest_rate": 12.00,
    "emi_amount": 23539.00,
    "emi_day": 5,
    "disbursement_date": "2026-07-05",
    "first_emi_date": "2026-08-05",
    "last_emi_date": "2028-07-05",
    "next_due_date": "2026-08-05",
    "next_due_amount": 23539.00,
    "status": "active",
    "overdue_days": 0,
    "dpd": 0,
    "emi_schedule": [
      {
        "installment_number": 1,
        "due_date": "2026-08-05",
        "emi_amount": 23539.00,
        "principal_component": 18372.33,
        "interest_component": 5166.67,
        "opening_principal": 500000.00,
        "closing_principal": 481627.67,
        "status": "pending",
        "paid_amount": 0.00,
        "overdue_days": 0,
        "penal_interest": 0.00
      }
      // ... 23 more installments
    ]
  },
  "message": "Loan account retrieved successfully"
}
```

### Step 13: Get Portfolio Statistics

**Endpoint**: `GET /api/loans/disbursement/statistics`

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "total_loans_disbursed": 1,
    "total_disbursed_amount": 484500.00,
    "total_outstanding_amount": 500000.00,
    "active_loans": 1,
    "overdue_loans": 0,
    "average_loan_size": 484500.00,
    "status_breakdown": {
      "active": 1
    },
    "collection_efficiency": 0.00
  },
  "message": "Statistics retrieved successfully"
}
```

---

## Complete End-to-End Flow

### Quick Test Script (All Steps)

```bash
# Set your auth token
export TOKEN="your_token_here"
export BASE_URL="http://localhost:8000/api"

# Step 1: Create Product
curl -X POST "$BASE_URL/loans/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @product.json

# Step 2: Create Application
curl -X POST "$BASE_URL/loans/applications" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @application.json

# Step 3: Submit Application
curl -X POST "$BASE_URL/loans/applications/1/submit" \
  -H "Authorization: Bearer $TOKEN"

# Step 4: Calculate Credit Score
curl -X POST "$BASE_URL/loans/credit-assessment/1/calculate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"monthly_income": 50000, "monthly_obligations": 10000}'

# Step 5: Initiate Approval
curl -X POST "$BASE_URL/loans/approval/1/initiate" \
  -H "Authorization: Bearer $TOKEN"

# Step 6: Approve Application
curl -X POST "$BASE_URL/loans/approval/1/approve" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comments": "Approved"}'

# Step 7: Generate Sanction Letter
curl -X POST "$BASE_URL/loans/disbursement/1/sanction-letter" \
  -H "Authorization: Bearer $TOKEN"

# Step 8: Disburse Loan
curl -X POST "$BASE_URL/loans/disbursement/1/approve" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @disbursement.json

# Step 9: Get Loan Account
curl -X GET "$BASE_URL/loans/disbursement/accounts/1?include_schedule=true" \
  -H "Authorization: Bearer $TOKEN"

# Step 10: Get Statistics
curl -X GET "$BASE_URL/loans/disbursement/statistics" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Edge Cases & Error Scenarios

### 1. Double Disbursement Attempt
```bash
# Try to disburse same application again
POST /api/loans/disbursement/1/approve
```
**Expected**: `400 Bad Request - "Loan account already exists for this application"`

### 2. Wrong Bank Account
```bash
# Use bank account from different customer
POST /api/loans/disbursement/1/approve
{
  "bank_account_id": 999,  // Doesn't belong to customer
  ...
}
```
**Expected**: `400 Bad Request - "Bank account not found or does not belong to customer"`

### 3. Unverified Bank Account
```bash
# Use unverified account
```
**Expected**: `400 Bad Request - "Bank account must be verified for disbursement"`

### 4. Unapproved Application
```bash
# Try to disburse without approval
POST /api/loans/disbursement/1/approve  // Application status is 'draft'
```
**Expected**: `400 Bad Request - "Loan application is not approved"`

### 5. Approval Without Authority
```bash
# Regular user trying to approve ₹10L loan
POST /api/loans/approval/1/approve  // Needs Manager level
```
**Expected**: `403 Forbidden - "Insufficient approval authority"`

### 6. Credit Score Below Threshold
```bash
# CIBIL score 550 (minimum is 650)
POST /api/loans/credit-assessment/1/calculate
```
**Expected**: `200 OK` with `eligible: false` and recommendation to reject

### 7. DTI Ratio Too High
```bash
# Monthly income: 30000, Obligations: 20000 (DTI = 66%)
POST /api/loans/credit-assessment/1/calculate
{
  "monthly_income": 30000,
  "monthly_obligations": 20000
}
```
**Expected**: `200 OK` with low credit score and high risk rating

### 8. Loan Amount Out of Range
```bash
# Requested amount: 2000000 (product max: 1000000)
POST /api/loans/applications
{
  "requested_amount": 2000000,
  ...
}
```
**Expected**: `400 Bad Request - "Requested amount exceeds product maximum"`

### 9. Future Disbursement Date
```bash
# Disbursement date 10 days in future
POST /api/loans/disbursement/1/approve
{
  "disbursement_date": "2026-07-15",  // >7 days in future
  ...
}
```
**Expected**: `422 Validation Error - "Disbursement date cannot be more than 7 days in future"`

### 10. Invalid EMI Start Day
```bash
# EMI day = 30 (only 1-28 allowed)
POST /api/loans/disbursement/1/approve
{
  "emi_start_day": 30,
  ...
}
```
**Expected**: `422 Validation Error - "emi_start_day must be between 1 and 28"`

---

## 📊 Expected Database State After Complete Flow

### loan_products
- 1 record with product_code = "PL24"

### loan_applications
- 1 record with status = "disbursed"
- application_number = "APP-202607-0001"

### loan_approval_workflows
- 1 record with status = "approved"
- approval_level = 1

### loan_accounts
- 1 record with status = "active"
- loan_account_number = "LN-202607-0001"

### loan_emi_schedules
- 24 records (one for each installment)
- All with status = "pending"

---

## ✅ Success Criteria

After running the complete flow:

1. ✅ Loan product created and active
2. ✅ Loan application created with auto-generated number
3. ✅ Credit score calculated (should be 82 with test data)
4. ✅ Approval workflow completed
5. ✅ Sanction letter generated
6. ✅ Loan account created with unique number
7. ✅ 24 EMI schedule records created
8. ✅ Application status changed to "disbursed"
9. ✅ All outstanding balances correctly set
10. ✅ Portfolio statistics showing 1 active loan

---

## 🚀 Next Steps

Once Phase 3 testing is complete:

1. **Phase 4: Repayment Recording** - Record EMI payments
2. **Phase 4: Payment Allocation** - Auto-allocate to principal/interest
3. **Phase 4: Overdue Calculation** - Auto-calculate penal interest
4. **Phase 4: Collection Queue** - Generate collection tasks
5. **Phase 4: Prepayment** - Handle prepayment and foreclosure

---

**Testing Guide Complete!** 🎉

For issues or questions, refer to:
- `LOAN_MODULE_DESIGN.md` - Complete design spec
- `LOAN_PHASE3_COMPLETE.md` - Phase 3 achievements
- `LOAN_MODULE_PROGRESS.md` - Progress tracker
