# DEPOSIT MANAGEMENT API DOCUMENTATION

## 📚 Complete API Reference

**Base URL:** `http://localhost:8000/api/v1/deposit`

**Authentication:** All endpoints require JWT Bearer token

---

## 📦 TABLE OF CONTENTS

1. [Product Management APIs](#product-management-apis) (13 endpoints)
2. [Account Management APIs](#account-management-apis) (18 endpoints)
3. [Interest Management APIs](#interest-management-apis) (15 endpoints)
4. [Passbook APIs](#passbook-apis) (5 endpoints) ✨ NEW
5. [Statement APIs](#statement-apis) (6 endpoints) ✨ NEW
6. [Certificate APIs](#certificate-apis) (6 endpoints) ✨ NEW
7. [Batch Operation APIs](#batch-operation-apis) (10 endpoints) ✨ NEW
8. [Reports & Analytics APIs](#reports--analytics-apis) (10 endpoints) ✨ NEW
9. [Notification APIs](#notification-apis) (6 endpoints) ✨ NEW
10. [Advanced Operations APIs](#advanced-operations-apis) (12 endpoints) ✨ NEW
11. [Regulatory Compliance APIs](#regulatory-compliance-apis) (5 endpoints) ✨ NEW

**Total: 106 API Endpoints**

---

## 1. PRODUCT MANAGEMENT APIS

### 1.1 Create Product
```http
POST /product
Content-Type: application/json
Authorization: Bearer <token>

{
  "product_code": "FD-12M-7.5",
  "product_name": "12 Month Fixed Deposit - 7.5%",
  "product_type": "fd",
  "interest_rate": 7.5,
  "interest_calculation_method": "compound",
  "interest_calculation_frequency": "quarterly",
  "min_deposit_amount": 10000,
  "max_deposit_amount": 10000000,
  "min_tenure_days": 365,
  "max_tenure_days": 365,
  "premature_withdrawal_allowed": true,
  "premature_withdrawal_penalty": 1.0,
  "tds_applicable": true,
  "tds_rate": 10.0
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "product_code": "FD-12M-7.5",
  "product_name": "12 Month Fixed Deposit - 7.5%",
  "product_type": "fd",
  "interest_rate": 7.5,
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### 1.2 List Products
```http
GET /product?product_type=fd&is_active=true&skip=0&limit=10
```

### 1.3 Get Product by ID
```http
GET /product/{product_id}
```

### 1.4 Update Product
```http
PUT /product/{product_id}
```

### 1.5 Delete Product
```http
DELETE /product/{product_id}
```

### 1.6 Calculate Maturity
```http
POST /product/calculate-maturity
{
  "product_id": 1,
  "principal_amount": 100000,
  "tenure_days": 365
}
```

**Response:**
```json
{
  "principal": 100000.0,
  "interest": 7500.0,
  "maturity_amount": 107500.0,
  "rate": 7.5,
  "product_code": "FD-12M-7.5",
  "calculation_method": "compound",
  "total_days": 365
}
```

### 1.7 Check Eligibility
```http
POST /product/check-eligibility
{
  "product_id": 1,
  "amount": 5000,
  "tenure_days": 180
}
```

### 1.8 Calculate Premature Closure
```http
POST /product/calculate-premature-closure
{
  "product_id": 1,
  "principal_amount": 100000,
  "days_held": 180,
  "interest_rate": 7.5
}
```

### 1.9 Get Product Statistics
```http
GET /product/{product_id}/statistics
```

### 1.10 Activate Product
```http
POST /product/{product_id}/activate
```

### 1.11 Deactivate Product
```http
POST /product/{product_id}/deactivate
```

### 1.12 Get Interest Rates
```http
GET /product/interest-rates?product_type=fd
```

### 1.13 Bulk Update Products
```http
POST /product/bulk-update
{
  "product_ids": [1, 2, 3],
  "updates": {
    "interest_rate": 8.0
  }
}
```

---

## 2. ACCOUNT MANAGEMENT APIS

### 2.1 Open Account
```http
POST /account
{
  "customer_id": 123,
  "deposit_product_id": 1,
  "principal_amount": 100000,
  "tenure_days": 365,
  "auto_renewal": false,
  "nominee_name": "Jane Doe",
  "nominee_relationship": "Spouse",
  "nominee_dob": "1990-05-15",
  "payment_mode": "cash"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "account_number": "DEP-202501-0001",
  "account_type": "fd",
  "principal_amount": 100000.0,
  "current_balance": 100000.0,
  "interest_rate": 7.5,
  "opening_date": "2025-01-15",
  "maturity_date": "2026-01-15",
  "maturity_amount": 107500.0,
  "status": "active"
}
```

### 2.2 Get Account Details
```http
GET /account/{account_id}
```

### 2.3 List Accounts
```http
GET /account?customer_id=123&account_type=fd&status=active&skip=0&limit=10
```

### 2.4 Make Deposit
```http
POST /account/deposit
{
  "account_id": 1,
  "amount": 5000,
  "payment_mode": "upi",
  "reference_number": "UPI123456",
  "remarks": "Additional deposit"
}
```

### 2.5 Make Withdrawal
```http
POST /account/withdraw
{
  "account_id": 1,
  "amount": 2000,
  "payment_mode": "cash",
  "remarks": "Emergency withdrawal"
}
```

### 2.6 Pay RD Installment
```http
POST /account/pay-installment
{
  "account_id": 1,
  "amount": 5000,
  "payment_mode": "auto_debit",
  "reference_number": "SI-123"
}
```

### 2.7 Close Account (Maturity)
```http
POST /account/{account_id}/close
```

### 2.8 Close Account (Premature)
```http
POST /account/{account_id}/close-premature
{
  "closure_reason": "Urgent financial need"
}
```

### 2.9 Update Account
```http
PUT /account/{account_id}
{
  "auto_renewal": true,
  "nominee_name": "John Doe Jr."
}
```

### 2.10 Get Account Summary
```http
GET /account/{account_id}/summary
```

### 2.11 Get Transaction History
```http
GET /account/{account_id}/transactions?from_date=2025-01-01&to_date=2025-01-31
```

### 2.12 Get Account Balance
```http
GET /account/{account_id}/balance
```

### 2.13 Transfer Account
```http
POST /account/{account_id}/transfer
{
  "new_customer_id": 456,
  "reason": "Account transfer",
  "transfer_date": "2025-01-15"
}
```

### 2.14 Freeze Account
```http
POST /account/{account_id}/freeze
{
  "freeze_type": "full",
  "reason": "Legal hold"
}
```

### 2.15 Unfreeze Account
```http
POST /account/{account_id}/unfreeze
{
  "freeze_id": 1,
  "reason": "Legal hold lifted"
}
```

### 2.16 Mark Lien
```http
POST /account/{account_id}/mark-lien
{
  "lien_amount": 50000,
  "reason": "Loan collateral",
  "reference": "LOAN-123"
}
```

### 2.17 Release Lien
```http
POST /account/{account_id}/release-lien
{
  "lien_id": 1,
  "reason": "Loan repaid"
}
```

### 2.18 Add Joint Holder
```http
POST /account/{account_id}/add-joint-holder
{
  "customer_id": 789,
  "holder_type": "joint",
  "operation_mode": "either_or"
}
```

---

## 3. INTEREST MANAGEMENT APIS

### 3.1 Calculate Interest
```http
POST /interest/calculate
{
  "account_id": 1,
  "from_date": "2025-01-01",
  "to_date": "2025-01-31"
}
```

**Response:**
```json
{
  "interest": 617.81,
  "days": 31,
  "rate": 7.5,
  "method": "compound",
  "tds_details": {
    "applicable": true,
    "rate": 10.0,
    "amount": 61.78
  },
  "net_interest": 556.03
}
```

### 3.2 Post Interest
```http
POST /interest/post
{
  "account_id": 1,
  "from_date": "2025-01-01",
  "to_date": "2025-01-31"
}
```

### 3.3 Get Interest Calculations
```http
GET /interest/calculations/{account_id}?from_date=2025-01-01&to_date=2025-12-31
```

### 3.4 Get Interest Summary
```http
GET /interest/summary/{account_id}?financial_year=2024-2025
```

### 3.5 Get Interest History
```http
GET /interest/history/{account_id}?skip=0&limit=10
```

### 3.6 Get Pending Interest
```http
GET /interest/pending?account_type=savings
```

### 3.7 Post Interest to Account
```http
POST /interest/{calculation_id}/post-to-account
```

### 3.8 Batch Calculate Interest
```http
POST /interest/batch-calculate
{
  "account_type": "savings",
  "product_id": 1
}
```

### 3.9 Recalculate Interest
```http
POST /interest/recalculate
{
  "account_id": 1,
  "from_date": "2025-01-01",
  "to_date": "2025-01-31"
}
```

### 3.10 Get TDS Summary
```http
GET /interest/tds-summary/{account_id}?financial_year=2024-2025
```

### 3.11 Mark Interest as Posted
```http
POST /interest/{calculation_id}/mark-posted
```

### 3.12 Get Interest Rate History
```http
GET /interest/rate-history/{account_id}
```

### 3.13 Get Accrued Interest
```http
GET /interest/accrued/{account_id}?as_of_date=2025-01-31
```

### 3.14 Schedule Interest Posting
```http
POST /interest/schedule-posting
{
  "account_type": "savings",
  "posting_date": "2025-02-01"
}
```

### 3.15 Get Next Interest Date
```http
GET /interest/next-date/{account_id}
```

---

## 4. PASSBOOK APIS ✨ NEW

### 4.1 Get Passbook Entries
```http
GET /passbook/{account_id}/entries?from_date=2025-01-01&to_date=2025-01-31&skip=0&limit=100
```

**Response:**
```json
{
  "account_number": "DEP-202501-0001",
  "account_type": "savings",
  "customer_name": "John Doe",
  "entries": [
    {
      "id": 1,
      "entry_date": "2025-01-15",
      "particulars": "Opening Deposit",
      "withdrawal_amount": 0.0,
      "deposit_amount": 100000.0,
      "balance": 100000.0,
      "printed": false
    }
  ],
  "total_count": 1,
  "skip": 0,
  "limit": 100
}
```

### 4.2 Mark Entries as Printed
```http
POST /passbook/{account_id}/mark-printed
{
  "entry_ids": [1, 2, 3]
}
```

### 4.3 Generate Passbook PDF
```http
GET /passbook/{account_id}/pdf?from_date=2025-01-01&to_date=2025-01-31&unprinted_only=false
```

**Response:** PDF file download

### 4.4 Get Passbook Summary
```http
GET /passbook/{account_id}/summary
```

**Response:**
```json
{
  "account_number": "DEP-202501-0001",
  "passbook_issued": true,
  "total_entries": 50,
  "printed_entries": 40,
  "unprinted_entries": 10,
  "last_print_date": "2025-01-30T10:30:00Z"
}
```

### 4.5 Issue Passbook
```http
POST /passbook/{account_id}/issue
```

---

## 5. STATEMENT APIS ✨ NEW

### 5.1 Generate Statement
```http
POST /statement
{
  "account_id": 1,
  "from_date": "2025-01-01",
  "to_date": "2025-01-31"
}
```

**Response:**
```json
{
  "account": {
    "account_number": "DEP-202501-0001",
    "account_type": "savings",
    "product_name": "Savings Account"
  },
  "period": {
    "from_date": "2025-01-01",
    "to_date": "2025-01-31"
  },
  "opening_balance": 100000.0,
  "closing_balance": 105617.81,
  "total_deposits": 5000.0,
  "total_withdrawals": 2000.0,
  "total_interest": 617.81,
  "transactions": [...]
}
```

### 5.2 Generate Statement PDF
```http
GET /statement/{account_id}/pdf?from_date=2025-01-01&to_date=2025-01-31
```

**Response:** PDF file download

### 5.3 Generate Statement Excel
```http
GET /statement/{account_id}/excel?from_date=2025-01-01&to_date=2025-01-31
```

**Response:** Excel file download

### 5.4 Email Statement
```http
POST /statement/{account_id}/email?from_date=2025-01-01&to_date=2025-01-31&email_address=customer@email.com
```

### 5.5 Get Quarterly Statement
```http
GET /statement/{account_id}/quarterly?year=2025&quarter=1&format=pdf
```

### 5.6 Get Annual Statement
```http
GET /statement/{account_id}/annual?year=2024&format=excel
```

---

## 6. CERTIFICATE APIS ✨ NEW

### 6.1 Generate Interest Certificate
```http
POST /certificate/interest
{
  "account_id": 1,
  "financial_year": "2024-2025"
}
```

**Response:**
```json
{
  "account": {
    "account_number": "DEP-202501-0001",
    "account_type": "fd"
  },
  "financial_year": "2024-2025",
  "period": {
    "start": "2024-04-01",
    "end": "2025-03-31"
  },
  "summary": {
    "total_interest": 7500.0,
    "total_tds": 750.0,
    "net_interest": 6750.0
  },
  "calculations": [...]
}
```

### 6.2 Generate Interest Certificate PDF
```http
GET /certificate/{account_id}/interest/pdf?financial_year=2024-2025
```

**Response:** PDF file download

### 6.3 Generate TDS Certificate
```http
GET /certificate/{account_id}/tds-certificate?financial_year=2024-2025&quarter=1&format=pdf
```

**Response:** Form 16A PDF download

### 6.4 Mark Certificate as Issued
```http
POST /certificate/{account_id}/issue-certificate
```

### 6.5 Get Interest Summary
```http
GET /certificate/{account_id}/interest-summary?financial_year=2024-2025
```

### 6.6 Get TDS Summary
```http
GET /certificate/tds-summary?financial_year=2024-2025&quarter=1
```

---

## 7. BATCH OPERATION APIS ✨ NEW

### 7.1 Process Maturity Batch
```http
POST /batch/maturity/process?maturity_date=2025-01-31&days_ahead=0
```

**Response:**
```json
{
  "total_accounts": 50,
  "processed": 48,
  "renewed": 30,
  "closed": 18,
  "errors": [...]
}
```

### 7.2 Calculate TDS Batch
```http
POST /batch/tds/calculate?financial_year=2024-2025&quarter=4
```

### 7.3 Check Dormant Accounts
```http
POST /batch/dormancy/check?inactive_months=24
```

### 7.4 Apply Penalties Batch
```http
POST /batch/penalties/apply?penalty_type=rd_missed
```

### 7.5 Process MIS Payout
```http
POST /batch/mis-payout/process?payout_month=2025-02-01
```

### 7.6 Get Batch Job Status
```http
GET /batch/status/{job_id}
```

### 7.7 Bulk Close Accounts
```http
POST /batch/bulk/close-accounts
{
  "account_ids": [1, 2, 3],
  "closure_reason": "Bulk closure"
}
```

### 7.8 Schedule Interest Posting
```http
POST /batch/interest/schedule-posting?posting_date=2025-02-01&account_type=savings
```

### 7.9 Reactivate Dormant Account
```http
POST /batch/dormancy/reactivate/{account_id}
```

### 7.10 Execute Standing Instructions
```http
POST /batch/standing-instructions/execute?instruction_type=auto_debit
```

---

## 8. REPORTS & ANALYTICS APIS ✨ NEW

### 8.1 Get Dashboard
```http
GET /reports/dashboard
```

**Response:**
```json
{
  "summary": {
    "total_accounts": 1500,
    "active_accounts": 1350,
    "total_principal": 150000000.0,
    "total_balance": 162500000.0,
    "total_interest": 12500000.0
  },
  "by_type": [
    {
      "account_type": "fd",
      "count": 800,
      "balance": 100000000.0
    },
    {
      "account_type": "savings",
      "count": 500,
      "balance": 50000000.0
    }
  ],
  "maturity_alerts": {
    "maturing_soon": 45
  },
  "today_transactions": {
    "count": 120,
    "amount": 2500000.0
  }
}
```

### 8.2 Get Deposit Summary
```http
GET /reports/summary?from_date=2025-01-01&to_date=2025-01-31&account_type=fd
```

### 8.3 Get Maturity Calendar
```http
GET /reports/maturity-calendar?from_date=2025-02-01&to_date=2025-02-28
```

**Response:**
```json
{
  "period": {
    "from": "2025-02-01",
    "to": "2025-02-28"
  },
  "total_accounts": 45,
  "total_maturity_amount": 5000000.0,
  "accounts": [
    {
      "account_number": "DEP-202501-0001",
      "maturity_date": "2025-02-15",
      "maturity_amount": 107500.0,
      "auto_renewal": false,
      "days_to_maturity": 15
    }
  ]
}
```

### 8.4 Get Interest Accrual Report
```http
GET /reports/interest-accrual?from_date=2025-01-01&to_date=2025-01-31&account_type=fd
```

### 8.5 Get Aging Analysis
```http
GET /reports/aging-analysis?as_of_date=2025-01-31
```

### 8.6 Get Product Performance
```http
GET /reports/product-performance?from_date=2024-01-01&to_date=2024-12-31
```

### 8.7 Get Dormancy Report
```http
GET /reports/dormancy-report
```

### 8.8 Get TDS Summary
```http
GET /reports/tds-summary?financial_year=2024-2025&quarter=1
```

### 8.9 Get Transaction Volume
```http
GET /reports/transaction-volume?from_date=2025-01-01&to_date=2025-01-31&group_by=day
```

### 8.10 Get Concentration Report
```http
GET /reports/concentration?as_of_date=2025-01-31
```

---

## 9. NOTIFICATION APIS ✨ NEW

### 9.1 Send Maturity Reminders
```http
POST /notification/maturity-reminders?days_before=30
```

### 9.2 Send RD Installment Reminders
```http
POST /notification/rd-reminders?days_before=3
```

### 9.3 Send Minimum Balance Alerts
```http
POST /notification/min-balance-alerts
```

### 9.4 Send Interest Credit Notifications
```http
POST /notification/interest-credit?posting_date=2025-01-31
```

### 9.5 Send Dormancy Warnings
```http
POST /notification/dormancy-warnings?inactive_months=18
```

### 9.6 Send Custom Notification
```http
POST /notification/custom
{
  "account_ids": [1, 2, 3],
  "subject": "Important Notice",
  "message": "Your account statement is ready",
  "channels": ["email", "sms"]
}
```

---

## 10. ADVANCED OPERATIONS APIS ✨ NEW

### 10.1-10.12 (Freeze, Lien, Transfer, Joint Account operations)
See Account Management section 2.14-2.18 for these endpoints.

---

## 11. REGULATORY COMPLIANCE APIS ✨ NEW

### 11.1 Generate RBI Return
```http
GET /regulatory/rbi-return?return_date=2025-01-31&return_type=quarterly
```

### 11.2 Generate DICGC Report
```http
GET /regulatory/dicgc-report?reporting_date=2025-01-31
```

### 11.3 Get Concentration Report
```http
GET /regulatory/concentration?as_of_date=2025-01-31
```

### 11.4 Get KYC Compliance Report
```http
GET /regulatory/kyc-compliance
```

### 11.5 Get Compliance Dashboard
```http
GET /regulatory/compliance-dashboard
```

---

## 📊 Response Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate entry) |
| 422 | Unprocessable Entity |
| 500 | Internal Server Error |

---

## 🔐 Authentication

All endpoints require JWT token in Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Token payload should include:
```json
{
  "user_id": "123",
  "tenant_id": "1",
  "roles": ["admin"],
  "exp": 1704067200
}
```

---

## ⚡ Rate Limits

| Endpoint Type | Rate Limit |
|--------------|------------|
| Read operations | 1000 req/min |
| Write operations | 100 req/min |
| Batch operations | 10 req/hour |
| Report generation | 20 req/min |
| PDF generation | 50 req/min |

---

## 📝 Common Error Responses

### Validation Error (400)
```json
{
  "success": false,
  "error": "Validation error",
  "details": {
    "field": "amount",
    "message": "Amount must be greater than 0"
  }
}
```

### Not Found (404)
```json
{
  "success": false,
  "error": "Account not found",
  "details": {
    "account_id": 999
  }
}
```

### Business Logic Error (422)
```json
{
  "success": false,
  "error": "Insufficient balance for withdrawal",
  "details": {
    "available_balance": 5000.0,
    "requested_amount": 10000.0
  }
}
```

---

## 🎯 Best Practices

1. **Pagination**: Always use `skip` and `limit` for list endpoints
2. **Date Filters**: Use ISO 8601 format (YYYY-MM-DD)
3. **Idempotency**: Use unique reference numbers for transactions
4. **Error Handling**: Always check response status and handle errors
5. **Timeouts**: Set reasonable timeouts (30s for reports, 5s for others)
6. **Retry Logic**: Implement exponential backoff for failed requests

---

## 📚 Additional Resources

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Postman Collection**: Available on request
- **SDK Libraries**: Python, JavaScript SDKs available

---

*API Documentation Version 1.0*
*Last Updated: January 2026*
*Total Endpoints: 106*
