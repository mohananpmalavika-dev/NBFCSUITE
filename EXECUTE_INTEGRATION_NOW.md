# CRM Integration - Execute Now!

## ✅ Status: Ready to Execute

All code has been written and integrated. Follow these steps to complete the setup.

---

## 🚀 Step 1: Database Migration

### Option A: Using Alembic (Recommended)

Open a terminal in the backend directory and run:

```bash
cd c:/NBFCSUITE/backend
alembic upgrade head
```

**If alembic is not installed:**
```bash
pip install alembic
alembic upgrade head
```

### Option B: Using SQL Directly

If Alembic doesn't work, execute the migration SQL directly:

1. Open your database tool (pgAdmin, DBeaver, or psql)
2. Connect to your database
3. Open the file: `c:/NBFCSUITE/backend/alembic/versions/add_crm_lead_management.py`
4. Extract the SQL from the `upgrade()` function
5. Execute it manually

### Option C: Using Python Script

Create and run this Python script:

```python
# File: c:/NBFCSUITE/backend/create_crm_tables.py

import asyncio
from sqlalchemy import text
from backend.shared.database.connection import engine

async def create_crm_tables():
    """Create CRM tables manually"""
    
    # Read the migration file
    with open('alembic/versions/add_crm_lead_management.py', 'r') as f:
        content = f.read()
    
    print("Creating CRM tables...")
    
    # Create tables using SQLAlchemy
    from backend.shared.database.crm_lead_models import (
        Lead, LeadFollowUp, LeadActivity, 
        LeadScoringRule, LeadAssignmentRule
    )
    from backend.shared.database.connection import Base
    
    async with engine.begin() as conn:
        # Create only CRM tables
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(
                bind=sync_conn,
                tables=[
                    Lead.__table__,
                    LeadFollowUp.__table__,
                    LeadActivity.__table__,
                    LeadScoringRule.__table__,
                    LeadAssignmentRule.__table__
                ],
                checkfirst=True
            )
        )
    
    print("✅ CRM tables created successfully!")
    
    # Verify
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'crm_%'")
        )
        tables = [row[0] for row in result]
        print(f"✅ Created {len(tables)} tables: {tables}")

if __name__ == "__main__":
    asyncio.run(create_crm_tables())
```

Then run:
```bash
cd c:/NBFCSUITE/backend
python create_crm_tables.py
```

---

## ✅ Step 2: Verify Backend Integration

### Check 1: Models are imported ✅
The CRM models are already imported in `backend/main.py` at line ~149:
```python
# 23. CRM Lead Management models
from backend.shared.database.crm_lead_models import (
    Lead, LeadFollowUp, LeadActivity, LeadScoringRule, LeadAssignmentRule
)
```

### Check 2: Router is imported ✅
The CRM router is already imported in `backend/main.py` at line ~594:
```python
# NEW: CRM Lead Management Module
from backend.services.crm.router import router as crm_router
```

### Check 3: Router is registered ✅
The CRM router is already registered in `backend/main.py` at line ~928:
```python
app.include_router(crm_router, tags=["CRM - Lead Management"])
```

**✅ Backend integration is COMPLETE! Just restart your server.**

---

## 🔄 Step 3: Restart Backend Server

```bash
# Stop current server (Ctrl+C)
cd c:/NBFCSUITE/backend
python -m uvicorn main:app --reload
```

After restart, visit: **http://localhost:8000/docs**

You should see a new section called **"CRM - Lead Management"** with 20+ endpoints!

---

## 📊 Step 4: Load Initial Data

### Method 1: Using psql

```bash
psql -U postgres -d your_database_name -f c:/NBFCSUITE/backend/scripts/crm_initial_data.sql
```

### Method 2: Using pgAdmin

1. Open pgAdmin
2. Connect to your database
3. Right-click on your database → Query Tool
4. Click "Open File" → Navigate to `c:/NBFCSUITE/backend/scripts/crm_initial_data.sql`
5. Click "Execute" (F5)

### Method 3: Using DBeaver

1. Open DBeaver
2. Connect to your database
3. Click "SQL Editor" → "Open SQL Script"
4. Select `c:/NBFCSUITE/backend/scripts/crm_initial_data.sql`
5. Click "Execute SQL Script"

### Method 4: Copy & Paste

1. Open `c:/NBFCSUITE/backend/scripts/crm_initial_data.sql`
2. Copy all content
3. Paste into your database query tool
4. Execute

---

## 🎨 Step 5: Add Frontend Routes

### Find your routing file

Common locations:
- `frontend/apps/admin-portal/src/App.tsx`
- `frontend/apps/admin-portal/src/routes.tsx`
- `frontend/apps/admin-portal/src/app/routes.tsx`

### Add these imports:

```typescript
import LeadDashboard from './pages/crm/LeadDashboard';
import LeadsPage from './pages/crm/LeadsPage';
import LeadDetailPage from './pages/crm/LeadDetailPage';
```

### Add these routes:

```typescript
// Inside your <Routes> component
<Route path="/crm">
  <Route path="dashboard" element={<LeadDashboard />} />
  <Route path="leads" element={<LeadsPage />} />
  <Route path="leads/:id" element={<LeadDetailPage />} />
</Route>
```

### Add to navigation menu:

```typescript
// In your sidebar/navigation component
{
  key: 'crm',
  icon: <UserOutlined />,
  label: 'CRM',
  children: [
    {
      key: 'crm-dashboard',
      label: 'Dashboard',
      path: '/crm/dashboard'
    },
    {
      key: 'crm-leads',
      label: 'Leads',
      path: '/crm/leads'
    }
  ]
}
```

---

## ✅ Step 6: Verification Checklist

### Backend Verification

```bash
# 1. Check if CRM tables exist
psql -U postgres -d your_database -c "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'crm_%';"

# Expected output: 5 tables
# - crm_leads
# - crm_lead_followups
# - crm_lead_activities
# - crm_lead_scoring_rules
# - crm_lead_assignment_rules

# 2. Check if initial data loaded
psql -U postgres -d your_database -c "SELECT COUNT(*) FROM crm_lead_scoring_rules;"
# Expected: 17

psql -U postgres -d your_database -c "SELECT COUNT(*) FROM crm_lead_assignment_rules;"
# Expected: 4

# 3. Test API endpoint
curl http://localhost:8000/api/crm/leads/dashboard/stats
# Should return JSON with statistics
```

### Frontend Verification

1. Navigate to: `http://localhost:3000/crm/dashboard`
2. Should see: Dashboard with statistics cards
3. Navigate to: `http://localhost:3000/crm/leads`
4. Should see: Leads table with filters

---

## 🧪 Step 7: Create Test Lead

### Using API (curl):

```bash
curl -X POST http://localhost:8000/api/crm/leads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "source": "website",
    "first_name": "John",
    "last_name": "Doe",
    "mobile": "9876543210",
    "email": "john.doe@example.com",
    "product_interest": "Personal Loan",
    "loan_amount_required": 500000,
    "monthly_income": 75000,
    "occupation": "Software Engineer",
    "company_name": "Tech Corp"
  }'
```

### Expected Response:

```json
{
  "id": 1,
  "lead_code": "LD-260711-0001",
  "full_name": "John Doe",
  "mobile": "9876543210",
  "email": "john.doe@example.com",
  "lead_score": 55,
  "lead_temperature": "warm",
  "status": "new",
  "assigned_to_user_id": 5,
  "created_at": "2026-07-11T..."
}
```

**Notice:**
- ✅ `lead_score` is auto-calculated (55 points)
- ✅ `lead_temperature` is auto-classified (warm)
- ✅ `lead_code` is auto-generated (LD-260711-0001)
- ✅ `assigned_to_user_id` is auto-assigned (if you have active users)

---

## 🎯 Quick Test Using Frontend

1. Go to: `http://localhost:3000/crm/leads`
2. Click "Create Lead" button
3. Fill in the form:
   - Source: Website
   - First Name: Test
   - Last Name: User
   - Mobile: 9876543210
   - Email: test@example.com
   - Product Interest: Personal Loan
   - Loan Amount: 500000
   - Monthly Income: 75000
4. Click Submit
5. Lead should appear in the table with:
   - Auto-generated code
   - Calculated score
   - Temperature indicator
   - Assigned to someone

---

## 📈 Step 8: Monitor the System

### Dashboard Statistics

Visit: `http://localhost:3000/crm/dashboard`

You should see:
- Total Leads
- New Leads
- Contacted Leads
- Qualified Leads
- Converted Leads
- Hot Leads
- Overdue Follow-ups
- Today's Follow-ups

### Check Scoring

```sql
SELECT 
    lead_code,
    full_name,
    lead_score,
    lead_temperature,
    score_breakdown
FROM crm_leads
ORDER BY lead_score DESC
LIMIT 10;
```

### Check Assignment

```sql
SELECT 
    u.full_name as assigned_to,
    COUNT(*) as lead_count
FROM crm_leads l
LEFT JOIN users u ON l.assigned_to_user_id = u.id
WHERE l.status NOT IN ('converted', 'lost')
GROUP BY u.id, u.full_name;
```

---

## 🎉 Success Indicators

✅ **You're fully set up when:**

1. [ ] Backend shows "CRM - Lead Management" in `/docs`
2. [ ] 5 CRM tables exist in database
3. [ ] 17 scoring rules loaded
4. [ ] 4 assignment rules loaded
5. [ ] Frontend routes work (`/crm/dashboard`, `/crm/leads`)
6. [ ] Can create a lead via UI
7. [ ] Lead gets auto-scored
8. [ ] Lead gets auto-assigned
9. [ ] Dashboard shows statistics
10. [ ] Can view lead details and create follow-ups

---

## 🆘 Troubleshooting

### Issue: Alembic not found

**Solution:**
```bash
pip install alembic
# or
pip install -r requirements.txt
```

### Issue: Tables not created

**Solution:**
Use Option C from Step 1 (Python script) or execute SQL manually

### Issue: No endpoints in /docs

**Solution:**
1. Verify imports in main.py (they're already there)
2. Restart backend server
3. Clear browser cache
4. Try in incognito mode

### Issue: Frontend routes not working

**Solution:**
1. Check if imports are correct
2. Verify route paths
3. Check browser console for errors
4. Ensure React Router is properly configured

### Issue: Lead not scoring

**Solution:**
```sql
-- Check if rules exist
SELECT * FROM crm_lead_scoring_rules WHERE is_active = true;

-- If no rules, load initial data again
```

---

## 📞 Need Help?

1. Check the logs:
   - Backend: Console output
   - Frontend: Browser console (F12)
   - Database: PostgreSQL logs

2. Review documentation:
   - `CRM_LEAD_MANAGEMENT_IMPLEMENTATION.md`
   - `CRM_INTEGRATION_GUIDE.md`
   - `CRM_SETUP_COMPLETE.md`

3. Verify all files are in place:
   - Backend: 5 files in `backend/services/crm/`
   - Frontend: 6 files in `frontend/apps/admin-portal/src/pages/crm/`
   - Migration: 1 file in `backend/alembic/versions/`

---

## ✅ Final Checklist

- [ ] Step 1: Run database migration
- [ ] Step 2: Verify backend integration (already done)
- [ ] Step 3: Restart backend server
- [ ] Step 4: Load initial data (scoring + assignment rules)
- [ ] Step 5: Add frontend routes
- [ ] Step 6: Verify everything works
- [ ] Step 7: Create test lead
- [ ] Step 8: Monitor system

**Once all checkboxes are ticked, you're LIVE! 🚀**

---

**Last Updated:** July 11, 2026  
**Status:** Ready for Execution  
**Estimated Time:** 15-20 minutes
