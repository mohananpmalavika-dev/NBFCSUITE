# Getting Started with Phase 8: Collections & Recovery

## Quick Start Guide

This guide will help you get started with the Collections & Recovery module in under 30 minutes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup & Installation](#setup--installation)
3. [Quick Start Examples](#quick-start-examples)
4. [Common Use Cases](#common-use-cases)
5. [API Examples](#api-examples)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+
- npm or yarn

### Required Phases
Phase 8 depends on the following phases being completed:
- ✅ Phase 6: Loan Origination & Disbursement
- ✅ Phase 7: Loan Servicing & Repayment

### Environment Variables

Add to your `.env` file:

```bash
# Database
DATABASE_URL=postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite

# Gold Service
GOLD_API_URL=http://localhost:8013

# Feature Flags
ENABLE_COLLECTIONS=true
ENABLE_FIELD_VISITS=true
ENABLE_AUCTIONS=true
```

---

## Setup & Installation

### Step 1: Run Database Migration

```bash
# Navigate to infrastructure directory
cd infra

# Run migration
psql -U nbfc_user -d nbfcsuite -f migrations/025_collections_recovery.sql

# Verify tables created
psql -U nbfc_user -d nbfcsuite -c "\dt gold_collection*"
```

Expected output:
```
 gold_collection_cases
 gold_collection_activities
 gold_collection_performance
```

### Step 2: Start Backend Service

```bash
# Navigate to gold service
cd services/gold

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the service
uvicorn app.main:app --reload --port 8013
```

Verify at: http://localhost:8013/docs

### Step 3: Start Frontend Application

```bash
# Navigate to customer app
cd apps/customer-app

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

Verify at: http://localhost:3000/gold-lending/collections/dashboard

---

## Quick Start Examples

### Example 1: Create Your First Collection Case

#### Using API (curl)

```bash
curl -X POST http://localhost:8013/api/v1/gold/collections/cases \
  -H "Content-Type: application/json" \
  -d '{
    "loan_account_id": "550e8400-e29b-41d4-a716-446655440000",
    "bucket_type": "dpd_31_60",
    "overdue_days": 45,
    "overdue_amount": 15000.00,
    "total_outstanding": 150000.00,
    "principal_overdue": 12000.00,
    "interest_overdue": 2500.00,
    "penalty_overdue": 500.00,
    "assigned_to_user_id": "660e8400-e29b-41d4-a716-446655440000",
    "priority": "high"
  }'
```

#### Using Python SDK

```python
from gold_api import GoldAPI

api = GoldAPI(base_url="http://localhost:8013")

case = api.create_collection_case({
    "loan_account_id": "550e8400-e29b-41d4-a716-446655440000",
    "bucket_type": "dpd_31_60",
    "overdue_days": 45,
    "overdue_amount": 15000.00,
    "total_outstanding": 150000.00,
    "principal_overdue": 12000.00,
    "interest_overdue": 2500.00,
    "penalty_overdue": 500.00,
    "assigned_to_user_id": "660e8400-e29b-41d4-a716-446655440000",
    "priority": "high"
})

print(f"Created case: {case['case_number']}")
```

#### Using Frontend

1. Navigate to: http://localhost:3000/gold-lending/collections/cases
2. Click "Create Case" button
3. Fill in the form with loan details
4. Click "Submit"

### Example 2: Schedule a Field Visit

```bash
curl -X POST http://localhost:8013/api/v1/gold/collections/field-visits \
  -H "Content-Type: application/json" \
  -d '{
    "collection_case_id": "CASE_ID_FROM_STEP_1",
    "visit_date": "2026-07-10",
    "visit_time": "10:00:00",
    "visit_type": "reminder",
    "visit_purpose": "Payment collection and property verification",
    "field_officer_id": "770e8400-e29b-41d4-a716-446655440000",
    "visit_address": "123 Main St, City, State"
  }'
```

### Example 3: Record Payment Promise

```bash
curl -X POST http://localhost:8013/api/v1/gold/collections/payment-promises \
  -H "Content-Type: application/json" \
  -d '{
    "collection_case_id": "CASE_ID",
    "promise_date": "2026-07-03",
    "promised_amount": 15000.00,
    "promised_payment_date": "2026-07-15",
    "promise_type": "full",
    "recorded_by_user_id": "USER_ID",
    "recording_channel": "phone"
  }'
```

### Example 4: View Collection Dashboard

```bash
# Get dashboard metrics
curl http://localhost:8013/api/v1/gold/collections/dashboard

# With date filters
curl "http://localhost:8013/api/v1/gold/collections/dashboard?from_date=2026-06-01&to_date=2026-07-03"
```

Expected response:
```json
{
  "total_cases": 150,
  "open_cases": 45,
  "in_progress_cases": 60,
  "legal_cases": 20,
  "closed_cases": 25,
  "total_outstanding": 15000000.00,
  "total_overdue": 3500000.00,
  "total_collected": 1200000.00,
  "collection_rate": 34.29,
  "bucket_0_30": 30,
  "bucket_31_60": 45,
  "bucket_61_90": 35,
  "bucket_90_plus": 25,
  "npa_cases": 15
}
```

---

## Common Use Cases

### Use Case 1: Daily Collections Workflow

**Morning Routine:**

```bash
# 1. Get today's field visits
curl "http://localhost:8013/api/v1/gold/collections/field-visits?visit_date=2026-07-03&visit_status=scheduled"

# 2. Get high-priority cases
curl "http://localhost:8013/api/v1/gold/collections/cases?priority=high&case_status=open"

# 3. Check payment promises due today
curl "http://localhost:8013/api/v1/gold/collections/payment-promises?to_date=2026-07-03&promise_status=active"
```

**During Field Visit:**

```bash
# 1. Update visit status to in_progress
curl -X PATCH http://localhost:8013/api/v1/gold/collections/field-visits/{visit_id} \
  -H "Content-Type: application/json" \
  -d '{"visit_status": "in_progress"}'

# 2. Log collection activity
curl -X POST http://localhost:8013/api/v1/gold/collections/activities \
  -H "Content-Type: application/json" \
  -d '{
    "collection_case_id": "CASE_ID",
    "activity_type": "field_visit",
    "activity_date": "2026-07-03",
    "contact_mode": "in_person",
    "disposition": "payment_collected",
    "amount_promised": 5000.00,
    "performed_by_user_id": "USER_ID"
  }'
```

**End of Day:**

```bash
# 1. Complete field visit
curl -X PATCH http://localhost:8013/api/v1/gold/collections/field-visits/{visit_id} \
  -H "Content-Type: application/json" \
  -d '{
    "visit_status": "completed",
    "customer_met": true,
    "amount_collected": 5000.00,
    "visit_outcome": "payment_collected"
  }'

# 2. Update case with next action
curl -X PATCH http://localhost:8013/api/v1/gold/collections/cases/{case_id} \
  -H "Content-Type: application/json" \
  -d '{
    "last_contact_date": "2026-07-03",
    "next_action_date": "2026-07-10"
  }'
```

### Use Case 2: Legal Notice Generation

```bash
# 1. Create legal notice
curl -X POST http://localhost:8013/api/v1/gold/collections/legal-notices \
  -H "Content-Type: application/json" \
  -d '{
    "collection_case_id": "CASE_ID",
    "notice_type": "final_demand",
    "notice_date": "2026-07-03",
    "notice_subject": "Final Demand Notice - Loan Account GL2024000001",
    "notice_content": "This is your final opportunity to clear outstanding dues...",
    "demand_amount": 150000.00,
    "response_deadline": "2026-07-18",
    "delivery_mode": "registered_post",
    "issued_by_user_id": "USER_ID"
  }'

# 2. Approve notice
curl -X PATCH http://localhost:8013/api/v1/gold/collections/legal-notices/{notice_id} \
  -H "Content-Type: application/json" \
  -d '{
    "notice_status": "approved",
    "approved_by_user_id": "MANAGER_ID",
    "approval_date": "2026-07-03"
  }'

# 3. Track delivery
curl -X PATCH http://localhost:8013/api/v1/gold/collections/legal-notices/{notice_id} \
  -H "Content-Type: application/json" \
  -d '{
    "notice_status": "delivered",
    "delivery_date": "2026-07-05",
    "tracking_number": "RR123456789IN",
    "delivery_status": "delivered"
  }'
```

### Use Case 3: Auction Management

```bash
# 1. Create auction lot
curl -X POST http://localhost:8013/api/v1/gold/collections/auction-lots \
  -H "Content-Type: application/json" \
  -d '{
    "auction_date": "2026-08-01",
    "auction_location": "Branch Auction Hall, Mumbai",
    "lot_description": "Gold ornaments from multiple defaulted loans",
    "total_gold_weight": 250.500,
    "total_items": 15,
    "reserve_price": 1500000.00,
    "starting_bid": 1200000.00,
    "bid_increment": 10000.00,
    "registration_deadline": "2026-07-25",
    "auction_type": "public",
    "created_by_user_id": "USER_ID"
  }'

# 2. Add items to lot
curl -X POST http://localhost:8013/api/v1/gold/collections/auction-lot-items \
  -H "Content-Type: application/json" \
  -d '{
    "auction_lot_id": "LOT_ID",
    "collection_case_id": "CASE_ID",
    "loan_account_id": "LOAN_ID",
    "item_number": 1,
    "gold_weight": 15.250,
    "gold_purity": 22.00,
    "estimated_value": 95000.00
  }'

# 3. Place bid
curl -X POST http://localhost:8013/api/v1/gold/collections/auction-bids \
  -H "Content-Type: application/json" \
  -d '{
    "auction_lot_id": "LOT_ID",
    "bidder_id": "BIDDER_ID",
    "bidder_name": "ABC Jewellers",
    "bid_amount": 1250000.00,
    "bid_type": "physical",
    "earnest_money_deposit": 125000.00
  }'
```

### Use Case 4: Performance Tracking

```bash
# 1. Create performance record (usually automated)
curl -X POST http://localhost:8013/api/v1/gold/collections/performance \
  -H "Content-Type: application/json" \
  -d '{
    "period_start": "2026-07-01",
    "period_end": "2026-07-31",
    "user_id": "OFFICER_ID",
    "user_name": "John Doe",
    "team_name": "Collection Team A",
    "region": "Mumbai",
    "total_cases_assigned": 50,
    "total_cases_resolved": 30,
    "total_overdue_amount": 5000000.00,
    "total_collected_amount": 3500000.00,
    "collection_percentage": 70.00,
    "total_field_visits": 45,
    "successful_field_visits": 35,
    "performance_rating": "good"
  }'

# 2. Get team performance
curl "http://localhost:8013/api/v1/gold/collections/performance?team_name=Collection%20Team%20A"

# 3. Get top performers
curl "http://localhost:8013/api/v1/gold/collections/performance?limit=10" | \
  jq 'sort_by(-.collection_percentage) | .[0:5]'
```

---

## API Examples

### Authentication

```python
import requests

# Get JWT token (if authentication is enabled)
response = requests.post(
    "http://localhost:8013/api/v1/auth/login",
    json={"username": "officer@example.com", "password": "password"}
)
token = response.json()["access_token"]

# Use token in subsequent requests
headers = {"Authorization": f"Bearer {token}"}
```

### Filtering and Pagination

```python
import requests

# Get cases with filters
params = {
    "case_status": "open",
    "bucket_type": "dpd_31_60",
    "priority": "high",
    "skip": 0,
    "limit": 50
}

response = requests.get(
    "http://localhost:8013/api/v1/gold/collections/cases",
    params=params
)

cases = response.json()
print(f"Total cases: {cases['total']}")
print(f"Page: {cases['page']} of {cases['total_pages']}")
```

### Batch Operations

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def create_activity(case_id, activity_data):
    return requests.post(
        f"http://localhost:8013/api/v1/gold/collections/activities",
        json={**activity_data, "collection_case_id": case_id}
    )

# Create multiple activities in parallel
case_ids = ["case1", "case2", "case3"]
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(create_activity, case_id, {...})
        for case_id in case_ids
    ]
    results = [f.result() for f in futures]
```

### Error Handling

```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(
        "http://localhost:8013/api/v1/gold/collections/cases",
        json=case_data,
        timeout=30
    )
    response.raise_for_status()
    case = response.json()
    print(f"Created case: {case['case_number']}")
    
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print(f"Validation error: {e.response.json()['detail']}")
    elif e.response.status_code == 404:
        print("Loan account not found")
    else:
        print(f"HTTP error: {e}")
        
except RequestException as e:
    print(f"Request failed: {e}")
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Database Connection Error

**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Verify connection string
psql postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite

# Check firewall
sudo ufw allow 5432
```

#### Issue 2: Foreign Key Constraint Error

**Symptom:**
```
IntegrityError: foreign key constraint "gold_collection_cases_loan_account_id_fkey" violated
```

**Solution:**
```bash
# Verify loan account exists
psql -d nbfcsuite -c "SELECT id FROM gold_loan_accounts WHERE id = 'YOUR_LOAN_ID';"

# If not, create test loan account first
```

#### Issue 3: Case Number Already Exists

**Symptom:**
```
IntegrityError: duplicate key value violates unique constraint "gold_collection_cases_case_number_key"
```

**Solution:**
The case_number is auto-generated. If you're seeing this error, the trigger might not be working:

```sql
-- Check sequence
SELECT last_value FROM gold_collection_cases_seq;

-- Reset if needed
ALTER SEQUENCE gold_collection_cases_seq RESTART WITH 1;
```

#### Issue 4: Frontend Not Loading

**Symptom:**
```
Error: Cannot find module 'goldApi'
```

**Solution:**
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

#### Issue 5: API Response 500

**Symptom:**
```json
{"detail": "Internal Server Error"}
```

**Solution:**
```bash
# Check backend logs
tail -f logs/gold-service.log

# Enable debug mode
export DEBUG=true
uvicorn app.main:app --reload --log-level debug
```

### Performance Optimization

#### Slow Query Performance

```sql
-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_cases_bucket_status 
ON gold_collection_cases(bucket_type, case_status);

CREATE INDEX CONCURRENTLY idx_activities_case_date 
ON gold_collection_activities(collection_case_id, activity_date DESC);

-- Analyze tables
ANALYZE gold_collection_cases;
ANALYZE gold_collection_activities;
```

#### High Memory Usage

```python
# Use pagination for large datasets
def get_all_cases():
    skip = 0
    limit = 100
    while True:
        cases = api.get_collection_cases(skip=skip, limit=limit)
        if not cases['items']:
            break
        yield from cases['items']
        skip += limit
```

---

## Next Steps

1. **Explore the Dashboard**: Visit `/gold-lending/collections/dashboard` to see analytics
2. **Create Test Data**: Use the provided sample scripts in `/scripts/seed_collections_data.py`
3. **Configure Workflows**: Set up automated notifications and escalations
4. **Integrate Systems**: Connect with SMS gateway, email service, and payment gateways
5. **Train Team**: Review technical documentation in `PHASE8_COLLECTIONS_RECOVERY.md`

---

## Additional Resources

- **Full Technical Documentation**: `PHASE8_COLLECTIONS_RECOVERY.md`
- **API Reference**: http://localhost:8013/docs
- **Video Tutorials**: [Coming Soon]
- **Support**: support@nbfcsuite.com

---

## Sample Data Scripts

### Create Sample Collection Cases

```python
# scripts/seed_collections_data.py
import requests
from datetime import date, timedelta

api_base = "http://localhost:8013/api/v1/gold/collections"

# Create 10 sample cases
for i in range(10):
    case_data = {
        "loan_account_id": f"loan-{i}",
        "bucket_type": ["dpd_0_30", "dpd_31_60", "dpd_61_90"][i % 3],
        "overdue_days": 15 + (i * 10),
        "overdue_amount": 10000 + (i * 5000),
        "total_outstanding": 100000 + (i * 10000),
        "principal_overdue": 8000 + (i * 4000),
        "interest_overdue": 1500 + (i * 800),
        "penalty_overdue": 500 + (i * 200),
        "assigned_to_user_id": f"user-{i % 3}",
        "priority": ["low", "medium", "high", "critical"][i % 4]
    }
    
    response = requests.post(f"{api_base}/cases", json=case_data)
    if response.status_code == 201:
        print(f"Created case: {response.json()['case_number']}")
```

---

**Happy Collections! 🎯**

For questions or support, reach out to the development team or check the comprehensive technical documentation.

**Version**: 1.0.0  
**Last Updated**: 2026-07-03
