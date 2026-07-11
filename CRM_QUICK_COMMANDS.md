# CRM Lead Management - Quick Command Reference

## 🚀 One-Time Setup Commands

### 1. Run Database Migration
```bash
cd c:/NBFCSUITE/backend
alembic upgrade head
```

### 2. Load Initial Data
```bash
# Using psql
psql -U postgres -d nbfc_db -f scripts/crm_initial_data.sql

# Or execute SQL directly in pgAdmin/DBeaver
# Open: backend/scripts/crm_initial_data.sql
# Execute all statements
```

### 3. Restart Backend
```bash
# Stop current server (Ctrl+C)
# Then restart
cd c:/NBFCSUITE/backend
python -m uvicorn main:app --reload
```

### 4. Verify Installation
```bash
# Check API docs
# Open: http://localhost:8000/docs
# Look for "CRM - Lead Management" section
```

---

## 📝 Testing Commands

### Test API Endpoints

```bash
# Get Dashboard Stats
curl http://localhost:8000/api/crm/leads/dashboard/stats

# Create Test Lead
curl -X POST http://localhost:8000/api/crm/leads \
  -H "Content-Type: application/json" \
  -d '{
    "source": "website",
    "first_name": "Test",
    "last_name": "User",
    "mobile": "9876543210",
    "email": "test@example.com",
    "product_interest": "Personal Loan",
    "loan_amount_required": 500000,
    "monthly_income": 75000
  }'

# List Leads
curl http://localhost:8000/api/crm/leads?page=1&page_size=20

# Get Lead Details
curl http://localhost:8000/api/crm/leads/1
```

---

## 🔍 Verification Queries

### Check Tables Created
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE 'crm_%'
ORDER BY table_name;
```

### Check Scoring Rules
```sql
SELECT rule_name, score_points, is_active 
FROM crm_lead_scoring_rules 
WHERE is_active = true
ORDER BY priority;
```

### Check Assignment Rules
```sql
SELECT rule_name, assignment_type, is_active
FROM crm_lead_assignment_rules
WHERE is_active = true
ORDER BY priority;
```

### View Leads
```sql
SELECT 
    lead_code, 
    full_name, 
    mobile, 
    source, 
    lead_score, 
    lead_temperature, 
    status,
    assigned_to_user_id
FROM crm_leads
ORDER BY created_at DESC
LIMIT 10;
```

---

## 🛠️ Configuration Commands

### Update Scoring Rule
```sql
UPDATE crm_lead_scoring_rules
SET score_points = 25, is_active = true
WHERE rule_name = 'High Income - Premium';
```

### Add New Scoring Rule
```sql
INSERT INTO crm_lead_scoring_rules (
    rule_name, rule_category, field_name, operator,
    field_value, score_points, is_active, tenant_id
) VALUES (
    'Custom Rule', 'demographics', 'monthly_income',
    'greater_than', '150000', 25, true, 'default'
);
```

### Disable Rule
```sql
UPDATE crm_lead_scoring_rules
SET is_active = false
WHERE rule_name = 'Your Rule Name';
```

---

## 📊 Monitoring Queries

### Today's Leads
```sql
SELECT status, COUNT(*) as count, AVG(lead_score) as avg_score
FROM crm_leads
WHERE DATE(created_at) = CURRENT_DATE
GROUP BY status;
```

### Overdue Follow-ups
```sql
SELECT 
    l.lead_code,
    l.full_name,
    f.scheduled_date,
    f.subject
FROM crm_lead_followups f
JOIN crm_leads l ON f.lead_id = l.id
WHERE f.status = 'pending'
  AND f.scheduled_date < NOW()
ORDER BY f.scheduled_date;
```

### Conversion Rate
```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN is_converted THEN 1 ELSE 0 END) as converted,
    ROUND(100.0 * SUM(CASE WHEN is_converted THEN 1 ELSE 0 END) / COUNT(*), 2) as rate
FROM crm_leads
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';
```

### Lead Distribution
```sql
SELECT 
    u.full_name,
    COUNT(*) as lead_count,
    AVG(l.lead_score) as avg_score
FROM crm_leads l
JOIN users u ON l.assigned_to_user_id = u.id
WHERE l.status NOT IN ('converted', 'lost')
GROUP BY u.id, u.full_name
ORDER BY lead_count DESC;
```

---

## 🔧 Troubleshooting Commands

### Check Migration Status
```bash
cd c:/NBFCSUITE/backend
alembic current
alembic history
```

### Reset Migration (if needed)
```bash
# WARNING: This will drop all data!
alembic downgrade base
alembic upgrade head
```

### Check Backend Logs
```bash
# In backend directory
tail -f logs/app.log

# Or check console output when running with --reload
```

### Test Database Connection
```python
# In Python console
from backend.shared.database.connection import engine

async def test():
    async with engine.connect() as conn:
        result = await conn.execute("SELECT 1")
        print(result.scalar())

import asyncio
asyncio.run(test())
```

---

## 🎯 Quick Actions

### Bulk Import Test Leads (SQL)
```sql
-- Create 10 test leads
INSERT INTO crm_leads (
    lead_code, source, first_name, last_name, mobile, email,
    product_interest, loan_amount_required, monthly_income,
    lead_score, lead_temperature, status, tenant_id
)
SELECT 
    'LD-260711-' || LPAD(generate_series::text, 4, '0'),
    'website',
    'Test' || generate_series,
    'User' || generate_series,
    '98765432' || LPAD(generate_series::text, 2, '0'),
    'test' || generate_series || '@example.com',
    'Personal Loan',
    500000 + (generate_series * 10000),
    50000 + (generate_series * 5000),
    40 + (generate_series % 40),
    CASE WHEN (40 + (generate_series % 40)) >= 70 THEN 'hot'
         WHEN (40 + (generate_series % 40)) >= 40 THEN 'warm'
         ELSE 'cold' END,
    'new',
    'default'
FROM generate_series(1, 10);
```

### Delete Test Data
```sql
-- WARNING: Only run in development!
DELETE FROM crm_leads WHERE lead_code LIKE 'LD-260711-%';
```

### Reset Sequences
```sql
-- If you need to reset auto-increment IDs
ALTER SEQUENCE crm_leads_id_seq RESTART WITH 1;
ALTER SEQUENCE crm_lead_followups_id_seq RESTART WITH 1;
ALTER SEQUENCE crm_lead_activities_id_seq RESTART WITH 1;
```

---

## 📱 Frontend URLs

```
Dashboard:     http://localhost:3000/crm/dashboard
Leads List:    http://localhost:3000/crm/leads
Lead Details:  http://localhost:3000/crm/leads/1
API Docs:      http://localhost:8000/docs
```

---

## 🆘 Need Help?

### Documentation Files:
- `CRM_LEAD_MANAGEMENT_IMPLEMENTATION.md` - Technical details
- `CRM_INTEGRATION_GUIDE.md` - Step-by-step setup
- `CRM_COMPLETE_SUMMARY.md` - Business overview
- `CRM_SETUP_COMPLETE.md` - Complete setup guide
- `CRM_QUICK_COMMANDS.md` - This file

### Check Logs:
- Backend: Console output or `logs/app.log`
- Database: PostgreSQL logs
- Frontend: Browser console (F12)

### Common Issues:
1. **Migration fails** → Check database connection
2. **API not showing** → Restart backend, clear cache
3. **No scoring** → Verify scoring rules exist
4. **No assignment** → Check assignment rules and active users

---

**Quick Start:** Just run the 4 setup commands at the top and you're ready! 🚀
