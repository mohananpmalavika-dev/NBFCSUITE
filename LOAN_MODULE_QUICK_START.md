# 🚀 Loan Module - Quick Start Guide

**Status**: Backend Complete - Ready to Test!  
**Date**: July 4, 2026

---

## 📋 What's Ready

✅ **Loan Product Management** - Create, configure, manage loan products  
✅ **Loan Applications** - Apply for loans with auto-calculations  
✅ **EMI Calculator** - Calculate EMI with multiple methods  
✅ **Eligibility Checker** - Validate customer eligibility  
✅ **22 API Endpoints** - Complete REST API

---

## 🔧 Setup Steps

### 1. Install Dependencies
```powershell
# Navigate to backend
cd backend

# Install Python packages (if not already installed)
pip install python-dateutil
```

### 2. Create Database Migration
```powershell
# Create migration for loan tables
alembic revision -m "add loan management tables"

# Edit the migration file and add:
# from shared.database.loan_models import *
# Base.metadata.create_all(bind=op.get_bind())

# Run migration
alembic upgrade head
```

### 3. Register Loan Router
Edit `backend/main.py` and add:
```python
from services.loan import router as loan_router

# Add to app
app.include_router(loan_router, prefix="/api/v1")
```

### 4. Start Backend Server
```powershell
# From backend directory
uvicorn main:app --reload --port 8000
```

---

## 🧪 Testing the API

### Test 1: Create a Loan Product

**Request**:
```bash
POST http://localhost:8000/api/v1/loans/products
Content-Type: application/json

{
  "product_code": "PL001",
  "product_name": "Personal Loan - Quick",
  "product_type": "personal",
  "loan_category": "unsecured",
  "interest_rate_type": "reducing",
  "min_interest_rate": 10.5,
  "max_interest_rate": 18.0,
  "default_interest_rate": 12.0,
  "min_loan_amount": 50000,
  "max_loan_amount": 1000000,
  "min_tenure_months": 6,
  "max_tenure_months": 60,
  "allowed_tenures": [6, 12, 18, 24, 36, 48, 60],
  "processing_fee_type": "percentage",
  "processing_fee_value": 2.0,
  "documentation_charges": 500,
  "insurance_applicable": false,
  "penal_interest_rate": 2.0,
  "grace_period_days": 3,
  "min_age": 21,
  "max_age": 65,
  "min_monthly_income": 25000,
  "min_cibil_score": 650,
  "employment_types": ["salaried", "self_employed"],
  "description": "Quick personal loan for salaried individuals",
  "features": [
    "Quick disbursement in 24 hours",
    "Minimal documentation",
    "Flexible repayment tenure",
    "No collateral required"
  ],
  "is_active": true,
  "is_featured": true,
  "display_order": 1
}
```

**Expected Response**: Product created with ID and all details

---

### Test 2: Calculate EMI

**Request**:
```bash
POST http://localhost:8000/api/v1/loans/products/calculate-emi
Content-Type: application/json

{
  "loan_amount": 500000,
  "interest_rate": 12.0,
  "tenure_months": 36,
  "interest_rate_type": "reducing"
}
```

**Expected Response**:
```json
{
  "loan_amount": 500000.00,
  "interest_rate": 12.00,
  "tenure_months": 36,
  "emi_amount": 16607.00,
  "total_interest": 97852.00,
  "total_repayment": 597852.00
}
```

---

### Test 3: Generate EMI Schedule

**Request**:
```bash
POST http://localhost:8000/api/v1/loans/products/1/generate-schedule
Content-Type: application/json

{
  "loan_amount": 500000,
  "interest_rate": 12.0,
  "tenure_months": 12,
  "interest_rate_type": "reducing"
}
```

**Expected Response**: Complete 12-month EMI schedule with principal/interest breakdown

---

### Test 4: Check Customer Eligibility

**Request**:
```bash
POST http://localhost:8000/api/v1/loans/products/1/check-eligibility?customer_age=30&customer_income=50000&customer_cibil=720&requested_amount=500000
```

**Expected Response**:
```json
{
  "eligible": true,
  "product_name": "Personal Loan - Quick",
  "product_code": "PL001",
  "errors": [],
  "message": "Customer is eligible"
}
```

---

### Test 5: Create Loan Application

**Request**:
```bash
POST http://localhost:8000/api/v1/loans/applications
Content-Type: application/json

{
  "customer_id": 1,
  "loan_product_id": 1,
  "requested_amount": 500000,
  "tenure_months": 36,
  "loan_purpose_id": 1,
  "purpose_description": "Home renovation",
  "disbursement_bank_account_id": 1,
  "disbursement_mode": "neft",
  "applicant_remarks": "Need funds urgently for home renovation"
}
```

**Expected Response**: Application created with auto-calculated EMI, fees, and application number (APP-202607-0001)

---

### Test 6: Add Co-Applicant

**Request** (when creating application):
```bash
POST http://localhost:8000/api/v1/loans/applications
Content-Type: application/json

{
  "customer_id": 1,
  "loan_product_id": 1,
  "requested_amount": 750000,
  "tenure_months": 48,
  "disbursement_bank_account_id": 1,
  "co_applicants": [
    {
      "family_member_id": 1,
      "co_applicant_type": "co_applicant",
      "is_primary": false,
      "monthly_income": 40000,
      "occupation": "Software Engineer",
      "consent_given": true,
      "consent_date": "2026-07-04"
    },
    {
      "family_member_id": 2,
      "co_applicant_type": "guarantor",
      "is_primary": false,
      "monthly_income": 60000,
      "occupation": "Business Owner",
      "consent_given": true,
      "consent_date": "2026-07-04"
    }
  ]
}
```

**Expected Response**: Application with co-applicants created

---

### Test 7: List Applications

**Request**:
```bash
GET http://localhost:8000/api/v1/loans/applications?page=1&page_size=20
```

**Expected Response**: Paginated list of applications with customer and product details

---

### Test 8: Get Application Statistics

**Request**:
```bash
GET http://localhost:8000/api/v1/loans/applications/stats
```

**Expected Response**:
```json
{
  "total_applications": 5,
  "draft": 2,
  "submitted": 1,
  "under_review": 1,
  "pending_approval": 0,
  "approved": 1,
  "rejected": 0,
  "disbursed": 0,
  "total_requested_amount": 2500000.00,
  "total_approved_amount": 500000.00,
  "average_loan_amount": 500000.00,
  "approval_rate": 100.00
}
```

---

### Test 9: Submit Application

**Request**:
```bash
POST http://localhost:8000/api/v1/loans/applications/1/submit
```

**Expected Response**: Application status changed to "submitted"

---

### Test 10: Update Application

**Request**:
```bash
PUT http://localhost:8000/api/v1/loans/applications/1
Content-Type: application/json

{
  "requested_amount": 600000,
  "tenure_months": 48,
  "internal_notes": "Increased loan amount as per customer request"
}
```

**Expected Response**: Application updated with recalculated EMI

---

## 📊 Sample Data to Create

### 1. Create Multiple Products
```json
// Product 1: Personal Loan
{
  "product_code": "PL001",
  "product_name": "Personal Loan - Quick",
  "product_type": "personal",
  "loan_category": "unsecured",
  "interest_rate_type": "reducing",
  "default_interest_rate": 12.0,
  "min_loan_amount": 50000,
  "max_loan_amount": 1000000,
  "min_tenure_months": 6,
  "max_tenure_months": 60,
  "processing_fee_type": "percentage",
  "processing_fee_value": 2.0,
  "penal_interest_rate": 2.0,
  "min_cibil_score": 650
}

// Product 2: Business Loan
{
  "product_code": "BL001",
  "product_name": "Business Loan - SME",
  "product_type": "business",
  "loan_category": "secured",
  "interest_rate_type": "reducing",
  "default_interest_rate": 10.5,
  "min_loan_amount": 500000,
  "max_loan_amount": 10000000,
  "min_tenure_months": 12,
  "max_tenure_months": 84,
  "processing_fee_type": "fixed",
  "processing_fee_value": 10000,
  "penal_interest_rate": 2.5,
  "min_cibil_score": 700
}

// Product 3: Gold Loan
{
  "product_code": "GL001",
  "product_name": "Gold Loan - Instant",
  "product_type": "gold",
  "loan_category": "secured",
  "interest_rate_type": "flat",
  "default_interest_rate": 8.0,
  "min_loan_amount": 10000,
  "max_loan_amount": 5000000,
  "min_tenure_months": 3,
  "max_tenure_months": 24,
  "processing_fee_type": "percentage",
  "processing_fee_value": 1.0,
  "penal_interest_rate": 1.5,
  "min_cibil_score": 600
}
```

---

## 🔍 API Endpoint Reference

### Loan Products
```
POST   /api/v1/loans/products                           Create product
GET    /api/v1/loans/products                           List products
GET    /api/v1/loans/products/active                    Active products
GET    /api/v1/loans/products/featured                  Featured products
GET    /api/v1/loans/products/code/{code}               Get by code
GET    /api/v1/loans/products/{id}                      Get by ID
PUT    /api/v1/loans/products/{id}                      Update product
DELETE /api/v1/loans/products/{id}                      Delete product
POST   /api/v1/loans/products/calculate-emi             Calculate EMI
POST   /api/v1/loans/products/{id}/generate-schedule    EMI schedule
POST   /api/v1/loans/products/{id}/check-eligibility    Check eligibility
```

### Loan Applications
```
POST   /api/v1/loans/applications                       Create application
GET    /api/v1/loans/applications/stats                 Statistics
GET    /api/v1/loans/applications                       List applications
GET    /api/v1/loans/applications/number/{number}       Get by number
GET    /api/v1/loans/applications/{id}                  Get by ID
PUT    /api/v1/loans/applications/{id}                  Update
POST   /api/v1/loans/applications/{id}/submit           Submit
GET    /api/v1/loans/applications/customer/{id}/applications  Customer apps
```

---

## 🎯 Common Use Cases

### Use Case 1: Customer Applies for Loan
1. Customer browses featured products: `GET /loans/products/featured`
2. Customer selects product and calculates EMI: `POST /loans/products/calculate-emi`
3. Customer views EMI schedule: `POST /loans/products/{id}/generate-schedule`
4. System checks eligibility: `POST /loans/products/{id}/check-eligibility`
5. Customer creates application: `POST /loans/applications`
6. Customer adds co-applicant (spouse): Include in application JSON
7. Customer submits application: `POST /loans/applications/{id}/submit`

### Use Case 2: Loan Officer Reviews Application
1. View pending applications: `GET /loans/applications?status=submitted`
2. View application details: `GET /loans/applications/{id}`
3. Check customer history: `GET /loans/applications/customer/{id}/applications`
4. Review EMI schedule: Already calculated and stored
5. Proceed to approval workflow (Phase 2)

### Use Case 3: Manager Views Dashboard
1. Get statistics: `GET /loans/applications/stats`
2. Filter by product: `GET /loans/applications?product_id=1`
3. Filter by date range: `GET /loans/applications?from_date=2026-07-01&to_date=2026-07-31`
4. Search by customer: `GET /loans/applications?search=John`

---

## 🐛 Troubleshooting

### Error: "Product code already exists"
- Each product needs a unique code
- Use different codes like PL001, PL002, BL001, etc.

### Error: "Customer not eligible"
- Check customer's age, income, CIBIL score
- Verify they meet product's eligibility criteria
- Adjust product criteria or customer details

### Error: "Tenure must be between X and Y"
- Product has tenure limits
- Choose tenure from `allowed_tenures` array
- Or within `min_tenure_months` to `max_tenure_months`

### Error: "Disbursement bank account required"
- Application needs a bank account ID for disbursement
- Create bank account first in customer module
- Link it in application creation

### Error: "Family member not found"
- Co-applicants must be from customer's family members
- Add family member first in customer module
- Then use that family_member_id

---

## ✅ Verification Checklist

After testing, verify:

- [ ] Can create loan products
- [ ] Can calculate EMI (flat, reducing)
- [ ] Can generate EMI schedule
- [ ] Can check eligibility
- [ ] Can create application with auto-calculations
- [ ] Can add co-applicants
- [ ] Can submit application
- [ ] Can update application (draft only)
- [ ] Can list applications with filters
- [ ] Can view application details
- [ ] Application number auto-generates
- [ ] EMI auto-calculates
- [ ] Fees auto-calculate
- [ ] Statistics are accurate

---

## 📚 Next Phase

Once testing is complete, we'll move to **Phase 2: Credit Assessment & Approval**:
- Credit scoring engine
- Multi-level approval workflow
- Status transitions
- Conditional approvals

---

**Status**: ✅ Ready to Test | 🧪 22 Endpoints Available | 🚀 Let's Go!
