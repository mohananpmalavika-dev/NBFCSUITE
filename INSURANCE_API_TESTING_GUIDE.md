# Insurance & Bancassurance API Testing Guide

## Quick Start Testing

### 1. Start the Server
```bash
cd c:\NBFCSUITE\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access API Documentation
Open browser: `http://localhost:8000/docs`

This provides interactive Swagger UI to test all endpoints.

---

## Test Sequence (Typical Workflow)

### Step 1: Create an Agent
```bash
POST /api/v1/insurance/agents
{
  "agent_code": "AGT001",
  "agent_name": "Rajesh Kumar",
  "agent_type": "employee",
  "email": "rajesh@example.com",
  "mobile": "9876543210",
  "default_commission_rate": 5.0,
  "tds_applicable": true
}
```

### Step 2: Create a Policy
```bash
POST /api/v1/insurance/policies
{
  "policy_type": "life",
  "customer_id": "customer-uuid-here",
  "customer_name": "John Doe",
  "insured_name": "John Doe",
  "insured_dob": "1990-01-01T00:00:00Z",
  "insured_age": 34,
  "insurance_company": "LIC",
  "product_name": "Jeevan Anand",
  "sum_assured": 1000000,
  "policy_term_years": 20,
  "premium_paying_term_years": 20,
  "premium_amount": 50000,
  "premium_frequency": "annually",
  "policy_start_date": "2024-01-01T00:00:00Z",
  "policy_end_date": "2044-01-01T00:00:00Z",
  "first_premium_date": "2024-01-01T00:00:00Z",
  "agent_id": "agent-uuid-from-step1",
  "agent_name": "Rajesh Kumar",
  "channel": "bancassurance"
}
```
**Response:** Returns policy with `policy_number` like `POL-LIFE-20240108-0001`

### Step 3: Activate Policy (Generates Premium Schedule)
```bash
POST /api/v1/insurance/policies/{policy_id}/activate
```
This will:
- Change status from DRAFT to ACTIVE
- Generate premium entries based on frequency
- Set next premium due date

### Step 4: List Premiums for the Policy
```bash
GET /api/v1/insurance/premiums?policy_id={policy_id}
```
You'll see all generated premium entries with due dates.

### Step 5: Record Premium Payment
```bash
POST /api/v1/insurance/premiums/{premium_id}/pay
{
  "payment_date": "2024-01-15T00:00:00Z",
  "payment_amount": 50000,
  "payment_method": "online",
  "payment_reference": "TXN123456",
  "transaction_id": "TXNID123456",
  "collected_by_name": "Branch Manager"
}
```
This will:
- Mark premium as PAID
- Update policy's total_premium_paid
- Update policy's outstanding_premium
- Set next_premium_due_date

### Step 6: Calculate First Year Commission
```bash
POST /api/v1/insurance/commissions/calculate/first-year?policy_id={policy_id}&agent_id={agent_id}
```
Automatically calculates commission based on annual premium and agent's rate.

### Step 7: Approve Commission
```bash
POST /api/v1/insurance/commissions/{commission_id}/approve
{
  "approved_by": "manager-uuid",
  "approved_by_name": "Branch Manager",
  "approval_remarks": "Approved for payment"
}
```

### Step 8: Pay Commission
```bash
POST /api/v1/insurance/commissions/{commission_id}/pay
{
  "payment_method": "neft",
  "payment_reference": "NEFT123456",
  "paid_amount": 2500,
  "payment_remarks": "Paid to agent account"
}
```

### Step 9: Register a Claim
```bash
POST /api/v1/insurance/claims
{
  "policy_id": "{policy_id}",
  "claim_type": "death",
  "claim_amount": 1000000,
  "incident_date": "2024-06-01T00:00:00Z",
  "incident_description": "Accidental death on highway",
  "incident_location": "Mumbai-Pune Highway",
  "claimant_name": "Jane Doe",
  "claimant_relationship": "Spouse",
  "claimant_contact": "9876543210",
  "documents_submitted": [
    {"type": "death_certificate", "url": "https://..."},
    {"type": "fir_copy", "url": "https://..."}
  ]
}
```
**Response:** Returns claim with `claim_number` like `CLM-DEATH-20240108-0001`

### Step 10: Process the Claim

**Mark Under Review:**
```bash
POST /api/v1/insurance/claims/{claim_id}/review?remarks=Claim under review by assessor
```

**Assess the Claim:**
```bash
POST /api/v1/insurance/claims/{claim_id}/assess
{
  "assessed_amount": 980000,
  "assessment_remarks": "Deducting outstanding premium",
  "documents_verified": true,
  "deductions": 20000,
  "deduction_details": {"outstanding_premium": 20000}
}
```

**Approve the Claim:**
```bash
POST /api/v1/insurance/claims/{claim_id}/approve
{
  "approved_amount": 980000,
  "approval_remarks": "Approved for settlement",
  "target_settlement_date": "2024-06-30T00:00:00Z"
}
```

**Settle the Claim:**
```bash
POST /api/v1/insurance/claims/{claim_id}/settle
{
  "settlement_amount": 980000,
  "settlement_method": "neft",
  "settlement_reference": "NEFT789456",
  "settlement_remarks": "Settled to nominee account"
}
```

---

## Statistics and Reports

### Policy Statistics
```bash
GET /api/v1/insurance/policies/stats/summary
```
Returns:
- Total policies by status
- Active, lapsed, matured counts
- Sum assured totals
- Premium collection status
- Policies by type

### Premium Statistics
```bash
GET /api/v1/insurance/premiums/stats/summary
# Or for specific policy:
GET /api/v1/insurance/premiums/stats/summary?policy_id={policy_id}
```
Returns:
- Total premiums (paid, due, overdue)
- Collection amounts
- Collection rate
- Outstanding amounts

### Claim Statistics
```bash
GET /api/v1/insurance/claims/stats/summary
```
Returns:
- Claims by status and type
- Claimed, assessed, approved, settled amounts
- Average processing time
- Settlement rate

### Commission Statistics
```bash
GET /api/v1/insurance/commissions/stats/summary
# Or for specific agent:
GET /api/v1/insurance/commissions/stats/summary?agent_id={agent_id}
```
Returns:
- Commissions by status
- Total commission amounts
- Paid vs outstanding
- Top performing agents

---

## Filtering Examples

### Filter Policies
```bash
# Active life policies
GET /api/v1/insurance/policies?policy_type=life&policy_status=active

# All policies for a customer
GET /api/v1/insurance/policies?customer_id={customer_id}

# All policies for an agent
GET /api/v1/insurance/policies?agent_id={agent_id}

# Lapsed policies
GET /api/v1/insurance/policies?is_lapsed=true
```

### Filter Premiums
```bash
# Due premiums
GET /api/v1/insurance/premiums/status/due

# Overdue premiums
GET /api/v1/insurance/premiums/status/overdue

# Paid premiums in date range
GET /api/v1/insurance/premiums?premium_status=paid&from_due_date=2024-01-01&to_due_date=2024-12-31
```

### Filter Claims
```bash
# Death claims under review
GET /api/v1/insurance/claims?claim_type=death&claim_status=under_review

# All claims for a policy
GET /api/v1/insurance/claims?policy_id={policy_id}

# Claims registered in date range
GET /api/v1/insurance/claims?from_claimed_date=2024-01-01&to_claimed_date=2024-12-31
```

### Filter Commissions
```bash
# Approved commissions
GET /api/v1/insurance/commissions?commission_status=approved

# Agent's commissions
GET /api/v1/insurance/commissions?agent_id={agent_id}

# First year commissions
GET /api/v1/insurance/commissions?commission_type=first_year
```

---

## Batch Operations

### Generate Monthly Premiums (Scheduled Job)
```bash
POST /api/v1/insurance/premiums/batch/generate
{
  "generation_date": "2024-02-01T00:00:00Z",
  "frequency": "monthly"
}
```
Generates premium entries for all active monthly policies.

### Mark Overdue Premiums (Scheduled Job)
```bash
POST /api/v1/insurance/premiums/batch/mark-overdue
```
Automatically marks premiums past grace period as OVERDUE.

### Calculate Renewal Commissions (Scheduled Job)
```bash
POST /api/v1/insurance/commissions/batch/calculate
{
  "calculation_period": "Jan-2024",
  "commission_type": "renewal"
}
```
Calculates commissions for all paid premiums in the period.

---

## Pagination

All list endpoints support pagination:
```bash
GET /api/v1/insurance/policies?skip=0&limit=10
GET /api/v1/insurance/premiums?skip=10&limit=10
GET /api/v1/insurance/claims?skip=0&limit=25
```

---

## Error Handling

### Common Error Codes
- **400 Bad Request:** Validation error, business rule violation
- **404 Not Found:** Policy, premium, claim, or commission not found
- **422 Unprocessable Entity:** Invalid data format

### Example Error Response
```json
{
  "success": false,
  "error": {
    "code": "POLICY_NOT_FOUND",
    "message": "Policy not found"
  }
}
```

---

## Testing with Postman

### 1. Import Collection
Create a Postman collection with these endpoints:
- Import from OpenAPI spec at `/openapi.json`
- Or manually add endpoints

### 2. Set Environment Variables
```
base_url = http://localhost:8000
api_version = v1
auth_token = your-jwt-token-here
tenant_id = your-tenant-id
```

### 3. Set Headers
```
Authorization: Bearer {{auth_token}}
X-Tenant-ID: {{tenant_id}}
Content-Type: application/json
```

---

## Testing with curl

### Create Policy
```bash
curl -X POST "http://localhost:8000/api/v1/insurance/policies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "policy_type": "life",
    "customer_id": "uuid",
    "customer_name": "John Doe",
    "insured_name": "John Doe",
    "insured_dob": "1990-01-01T00:00:00Z",
    "insured_age": 34,
    "insurance_company": "LIC",
    "product_name": "Jeevan Anand",
    "sum_assured": 1000000,
    "policy_term_years": 20,
    "premium_paying_term_years": 20,
    "premium_amount": 50000,
    "premium_frequency": "annually",
    "policy_start_date": "2024-01-01T00:00:00Z",
    "policy_end_date": "2044-01-01T00:00:00Z",
    "first_premium_date": "2024-01-01T00:00:00Z",
    "agent_id": "uuid",
    "channel": "bancassurance"
  }'
```

### List Policies
```bash
curl -X GET "http://localhost:8000/api/v1/insurance/policies" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Sample Data for Testing

### Policy Types
- `life` - Life Insurance
- `health` - Health Insurance
- `general` - General Insurance
- `motor` - Motor Insurance
- `endowment` - Endowment Policy
- `term` - Term Insurance
- `ulip` - Unit Linked Insurance
- `pension` - Pension Plans

### Premium Frequencies
- `monthly` - Monthly premiums
- `quarterly` - Quarterly premiums
- `half_yearly` - Half-yearly premiums
- `annually` - Annual premiums
- `single` - Single premium

### Claim Types
- `death` - Death claim
- `maturity` - Maturity claim
- `surrender` - Surrender value
- `health` - Health claim
- `accident` - Accident claim
- `damage` - Damage claim
- `theft` - Theft claim
- `other` - Other claims

### Payment Methods
- `cash` - Cash payment
- `cheque` - Cheque payment
- `online` - Online payment
- `neft` - NEFT transfer
- `rtgs` - RTGS transfer
- `upi` - UPI payment

---

## Troubleshooting

### Issue: 404 on All Endpoints
**Solution:** Ensure server is running and base URL is correct.

### Issue: Authentication Error
**Solution:** Ensure JWT token is valid and passed in Authorization header.

### Issue: Validation Error on Create
**Solution:** Check required fields match schema. Use `/docs` to see schema.

### Issue: Foreign Key Error
**Solution:** Ensure referenced entities (customer, agent, policy) exist before creating dependent entities.

---

## Next Steps

1. **Run Migration:** `alembic upgrade head`
2. **Start Server:** `uvicorn main:app --reload`
3. **Test APIs:** Use `/docs` or Postman
4. **Check Stats:** Verify statistics endpoints
5. **Test Workflows:** Follow the step-by-step sequence above

---

**Happy Testing! 🚀**
