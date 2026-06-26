# NBFCSUITE API Reference

Complete reference for all microservice APIs in the NBFC Operating System.

## Base URLs

- **Local Development**: `http://localhost:8000` (per service on different ports)
- **Docker Compose**: `http://localhost:{service_port}`
- **Production**: `https://api.nbfcsuite.io` (to be determined)

## Authentication

All endpoints (except `/health`, `/ready`, `/auth/login`) require JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Get Access Token

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Services

### 1. Auth Service

**Port:** `8000`
**Base URL:** `http://localhost:8000`

#### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/users` | Create user |
| GET | `/auth/users` | List users |
| GET | `/auth/users/{id}` | Get user profile |
| PUT | `/auth/users/{id}` | Update user |
| DELETE | `/auth/users/{id}` | Delete user |

#### Roles & Permissions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/roles` | Create role |
| GET | `/auth/roles` | List roles |
| GET | `/auth/roles/{id}` | Get role |
| POST | `/auth/roles/{id}/permissions` | Assign permission to role |

#### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login & get token |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/validate` | Validate token |

**Example:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "pass"}'
```

---

### 2. Customer Service

**Port:** `8001`
**Base URL:** `http://localhost:8001`

#### Customer Profile (CIF)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/customers` | Create customer |
| GET | `/customers/{id}` | Get customer (360 view) |
| PUT | `/customers/{id}` | Update customer |
| GET | `/customers` | List customers |
| POST | `/customers/{id}/documents` | Upload KYC document |
| POST | `/customers/{id}/kyc` | Initiate KYC verification |

**Customer 360 Response Example:**
```json
{
  "id": "cust-001",
  "first_name": "John",
  "email": "john@example.com",
  "kyc_status": "approved",
  "loans": [
    {"id": "loan-001", "status": "active", "amount": 500000}
  ],
  "behavior_score": 75.5,
  "risk_level": "medium"
}
```

---

### 3. LOS (Loan Origination System)

**Port:** `8002`
**Base URL:** `http://localhost:8002`

#### Loan Applications

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/applications` | Submit loan application |
| GET | `/applications/{id}` | Get application status |
| PUT | `/applications/{id}` | Update application |
| POST | `/applications/{id}/documents` | Upload document |
| POST | `/applications/{id}/submit` | Submit for underwriting |
| GET | `/applications/{id}/scorecard` | Get application scorecard |

**Create Application Request:**
```json
{
  "customer_id": "cust-001",
  "product_code": "PL001",
  "amount": 500000,
  "tenure_months": 36
}
```

**Application Status Response:**
```json
{
  "id": "app-001",
  "customer_id": "cust-001",
  "status": "under_review",
  "applied_amount": 500000,
  "sanctioned_amount": null,
  "scorecard": {
    "credit_score": 750,
    "behavior_score": 72.5,
    "fraud_score": 15.2
  }
}
```

---

### 4. LMS (Loan Management System)

**Port:** `8003`
**Base URL:** `http://localhost:8003`

#### Loan Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/loans` | Book a loan |
| GET | `/loans/{id}` | Get loan details |
| GET | `/loans/{id}/schedule` | Get EMI schedule |
| POST | `/loans/{id}/payment` | Record payment |
| POST | `/loans/{id}/foreclose` | Foreclose loan |
| POST | `/loans/{id}/topup` | Top-up loan |

**Book Loan Request:**
```json
{
  "application_id": "app-001",
  "sanctioned_amount": 500000,
  "tenure_months": 36,
  "interest_rate": 12.5,
  "product_code": "PL001"
}
```

**EMI Schedule Response:**
```json
[
  {
    "emi_number": 1,
    "due_date": "2026-07-26",
    "emi_amount": 15800,
    "principal": 13200,
    "interest": 2600,
    "status": "pending"
  }
]
```

---

### 5. Collections Service

**Port:** `8004`
**Base URL:** `http://localhost:8004`

#### Collection Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/buckets` | List DPD buckets with loan counts |
| GET | `/buckets/{bucket_id}/loans` | Get assignments in a bucket |
| POST | `/assignments` | Assign a delinquent loan to a collector |
| GET | `/assignments` | List assignments by collector, branch, or status |
| GET | `/loan/{loan_id}/status` | Get collection status and latest activity |
| POST | `/loan/{loan_id}/activity` | Log call, visit, PTP, or other activity |
| POST | `/loan/{loan_id}/settlement-offer` | Create a settlement offer |
| POST | `/loan/{loan_id}/npa-classification` | Classify a delinquent loan as NPA |

**Assign Loans Request:**
```json
{
  "loan_account_id": "loan-001",
  "customer_id": "cust-001",
  "collector_user_id": "user-collector-01",
  "branch_id": "branch-001",
  "days_past_due": 45,
  "outstanding_amount": 25000,
  "priority": "high"
}
```

**Collection Activity Log:**
```json
{
  "activity_type": "call",
  "notes": "Customer promised to pay ₹10,000 by 30th",
  "promised_amount": 10000,
  "promised_date": "2026-07-30"
}
```

---

### 6. Deposits Service

**Port:** `8007`
**Base URL:** `http://localhost:8007`

#### Deposit Products, Accounts & Statements

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/deposit-types` | List CASA, FD, and RD product masters |
| POST | `/deposit-accounts` | Open a deposit account |
| GET | `/deposit-accounts` | List deposit accounts by customer or status |
| GET | `/deposit-accounts/{account_id}` | Get deposit account details |
| GET | `/deposit-accounts/{account_id}/interest-schedule` | Calculate interest and maturity value |
| POST | `/deposit-accounts/{account_id}/transactions` | Post credit, debit, interest, or fee |
| GET | `/deposit-accounts/{account_id}/transactions` | List account transactions |
| GET | `/deposit-accounts/{account_id}/statement` | Get statement between two dates |
| POST | `/deposit-accounts/{account_id}/standing-instructions` | Add a standing instruction |

**Open Deposit Account Request:**
```json
{
  "customer_id": "cust-001",
  "deposit_type_code": "FD",
  "principal_amount": 100000,
  "start_date": "2026-01-01T00:00:00"
}
```

**Post Transaction Request:**
```json
{
  "transaction_type": "credit",
  "amount": 5000,
  "description": "Top-up",
  "reference": "DEP-1",
  "transaction_date": "2026-02-01T00:00:00"
}
```

---

### 7. HRMS Service

**Port:** `8012`
**Base URL:** `http://localhost:8012`

#### Employee Master

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/employees` | Create an employee profile |
| GET | `/employees` | List employees by branch, department, or status |
| GET | `/employees/{employee_id}` | Get employee details |
| PUT | `/employees/{employee_id}` | Update employee profile, status, or IAM mapping |
| POST | `/employees/{employee_id}/assign-branch` | Assign an employee to a branch |

**Create Employee Request:**
```json
{
  "employee_number": "EMP-001",
  "first_name": "Anika",
  "last_name": "Rao",
  "email": "anika.rao@example.com",
  "phone": "9999999002",
  "designation": "Collection Officer",
  "department": "Collections",
  "branch_id": "branch-001",
  "user_id": "user-collector-01",
  "joining_date": "2026-01-10T00:00:00"
}
```

---

### 8. FinDNA / AI Service

**Port:** `8005`
**Base URL:** `http://localhost:8005`

#### Behavioral Scoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/score/behavior` | Compute behavioral score and risk indicators |
| POST | `/score/fraud` | Detect fraud indicators for customer/application |
| GET | `/behavioral-score/{customer_id}` | Retrieve stored behavioral score summary |
| POST | `/embeddings` | Generate profile embeddings for semantic search |
| POST | `/predict/churn` | Predict customer churn probability |
| POST | `/underwriting-assistant/{application_id}` | Generate underwriting recommendations for a loan application |
| POST | `/collections-assistant/{customer_id}` | Generate collections outreach strategy |
| POST | `/relationship-manager/{customer_id}` | Generate conversational relationship guidance |

**Behavioral Score Request:**
```json
{
  "customer_id": "cust-001",
  "income_data": {
    "monthly_income": 75000,
    "annual_salary": 900000
  },
  "bank_statement_url": "s3://bucket/statement.pdf"
}
```

**Behavioral Score Response:**
```json
{
  "score": 78.5,
  "risk_level": "low",
  "default_probability_90d": 0.08,
  "explanations": {
    "decision_behavior": "Customer pays bills consistently after reminders",
    "spending_psychology": "Moderate discretionary spending",
    "repayment_discipline": "Strong track record of on-time payments"
  }
}

**Underwriting Assistant Request:**
```json
{
  "customer_id": "cust-001",
  "application_id": "app-001",
  "context_text": "Evaluate loan eligibility for a salaried customer with stable income."
}
```

**Underwriting Assistant Response:**
```json
{
  "customer_id": "cust-001",
  "application_id": "app-001",
  "summary": "This application shows stable income, moderate credit utilization, and a low likelihood of early delinquency.",
  "recommendation": "Recommend approval with a conservative tenure and monthly EMI monitoring.",
  "risk_indicators": [
    "Credit utilization near 50%",
    "Shorter credit history than preferred",
    "Additional documentation needed for GST-linked income"
  ],
  "action_plan": {
    "verify_bank_statements": "Review bank statement and income verification documents.",
    "monitor_disbursement": "Track first three EMIs closely after disbursal.",
    "confirm_collateral": "Validate collateral/submission documents before booking."
  },
  "insights": {
    "credit_recommendation": "Offer a tiered personal loan product with 17% APR.",
    "risk_summary": "Overall risk is medium; keep exposure limited to 20% of customer’s monthly income."
  }
}
``````

---

## Error Responses

All services follow a consistent error response format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "User already exists",
    "details": {
      "field": "username",
      "constraint": "unique"
    }
  }
}
```

### Common Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `INVALID_REQUEST` | 400 | Validation error |
| `CONFLICT` | 409 | Resource already exists |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Service Communication Patterns

### Synchronous (REST/HTTP)

Services call each other directly via REST:

```
Customer Service → LOS Service → FinDNA Service
```

### Asynchronous (Event-Driven)

Services publish domain events to a message queue (Kafka/RabbitMQ):

```
LMS Service (loan paid) → Event: "payment.received" → Collections Service
LOS Service (app submitted) → Event: "application.submitted" → Notifications Service
```

---

## Rate Limiting

- **Public endpoints**: 100 requests per minute per IP
- **Authenticated endpoints**: 1000 requests per minute per user
- **Admin endpoints**: 10000 requests per minute

Rate limit headers in response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1656230400
```

---

## Pagination

List endpoints support pagination:

```
GET /customers?skip=0&limit=20
GET /loans?skip=20&limit=20
```

Response:
```json
{
  "items": [...],
  "total": 1000,
  "skip": 0,
  "limit": 20
}
```

---

## Versioning

APIs are versioned in the URL path:

```
/v1/customers
/v2/customers  (future breaking changes)
```

Current version: `v1`

---

## Webhooks (Planned)

Services will support webhooks for asynchronous notifications:

```
POST /webhooks/subscribe
{
  "event": "application.approved",
  "callback_url": "https://myapp.com/callback"
}
```

---

## OpenAPI Specifications

Interactive API documentation available at:
- **Auth**: `http://localhost:8000/docs`
- **Customer**: `http://localhost:8001/docs`
- **LOS**: `http://localhost:8002/docs`
- **LMS**: `http://localhost:8003/docs`
- **Collections**: `http://localhost:8004/docs`
- **FinDNA**: `http://localhost:8005/docs`
- **Deposits**: `http://localhost:8007/docs`
- **Accounting**: `http://localhost:8008/docs`
- **CRM**: `http://localhost:8009/docs`
- **Document**: `http://localhost:8010/docs`
- **Compliance**: `http://localhost:8011/docs`

YAML specs available in `design/openapi-*.yaml`

---

Last updated: 2026-06-26
