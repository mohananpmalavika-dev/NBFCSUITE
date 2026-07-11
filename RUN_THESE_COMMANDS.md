# 🚀 CRM Integration - RUN THESE COMMANDS NOW!

## ✅ What's Already Done

### Backend Integration ✅ COMPLETE
- ✅ Router imported in `main.py` (line ~594)
- ✅ Router registered in `main.py` (line ~928)
- ✅ Models imported in `main.py` (line ~149)
- ✅ All code files created (15 files)
- ✅ Helper scripts ready (3 scripts)

**You don't need to edit `main.py` - I already did it!**

---

## 🎯 Execute These 3 Commands (5 minutes total)

### Command 1: Create Database Tables (2 min)

Open PowerShell/Terminal and run:

```powershell
cd c:\NBFCSUITE\backend
python create_crm_tables.py
```

**Expected Output:**
```
✅ Models imported successfully
✅ Tables created successfully!
✅ Found 5 CRM tables:
   - crm_leads
   - crm_lead_followups
   - crm_lead_activities
   - crm_lead_scoring_rules
   - crm_lead_assignment_rules
```

---

### Command 2: Load Initial Data (1 min)

```powershell
python load_crm_initial_data.py
```

**Expected Output:**
```
✅ Added 17 scoring rules
✅ Added 4 assignment rules
✅ SUCCESS! Initial data loaded.
```

---

### Command 3: Restart Backend (30 sec)

Stop your current server (Ctrl+C), then:

```powershell
python -m uvicorn main:app --reload
```

**Verify:** Open http://localhost:8000/docs

Look for section: **"CRM - Lead Management"** with 20+ endpoints

---

## ✅ Verification (1 minute)

### Test 1: Check API Docs

Open: http://localhost:8000/docs

Scroll down and find: **"CRM - Lead Management"**

You should see these endpoints:
- POST /api/crm/leads
- GET /api/crm/leads/{id}
- GET /api/crm/leads
- POST /api/crm/leads/{id}/assign
- POST /api/crm/leads/{id}/qualify
- POST /api/crm/leads/{id}/convert
- And 14 more...

---

### Test 2: Create a Test Lead

Open PowerShell and run:

```powershell
curl -X POST http://localhost:8000/api/crm/leads `
  -H "Content-Type: application/json" `
  -d '{\"source\":\"website\",\"first_name\":\"Test\",\"last_name\":\"User\",\"mobile\":\"9876543210\",\"email\":\"test@example.com\",\"monthly_income\":75000,\"loan_amount_required\":500000}'
```

**Expected Response:**
```json
{
  "id": 1,
  "lead_code": "LD-260711-0001",  ← Auto-generated!
  "full_name": "Test User",
  "lead_score": 45,  ← Auto-calculated!
  "lead_temperature": "warm",  ← Auto-classified!
  "status": "new",
  "assigned_to_user_id": 5  ← Auto-assigned!
}
```

**✅ SUCCESS!** If you see auto-generated code, auto-score, and auto-assignment, everything works!

---

## 🎨 Optional: Add Frontend Routes (5 minutes)

### Step 1: Find Your Routing File

Look for one of these files:
- `frontend/apps/admin-portal/src/App.tsx`
- `frontend/apps/admin-portal/src/routes.tsx`
- `frontend/src/App.tsx`

### Step 2: Add Imports

Add at the top:

```typescript
import LeadDashboard from './pages/crm/LeadDashboard';
import LeadsPage from './pages/crm/LeadsPage';
import LeadDetailPage from './pages/crm/LeadDetailPage';
```

### Step 3: Add Routes

Inside your `<Routes>` component:

```typescript
<Route path="/crm">
  <Route path="dashboard" element={<LeadDashboard />} />
  <Route path="leads" element={<LeadsPage />} />
  <Route path="leads/:id" element={<LeadDetailPage />} />
</Route>
```

### Step 4: Add to Navigation

In your sidebar/menu component:

```typescript
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

### Step 5: Test Frontend

1. Navigate to: http://localhost:3000/crm/dashboard
2. Should see: Statistics cards with lead metrics
3. Navigate to: http://localhost:3000/crm/leads
4. Should see: Table with filters and "Create Lead" button

---

## 🎉 You're Done!

### What You Now Have

✅ **Backend API** (20+ endpoints)
- Multi-channel lead capture
- Intelligent lead scoring
- Smart lead assignment
- Follow-up tracking
- Dashboard analytics

✅ **Database** (5 tables)
- Complete schema with indexes
- 17 scoring rules loaded
- 4 assignment rules loaded

✅ **Frontend** (6 pages - optional)
- Dashboard with statistics
- Leads list with filters
- Lead detail page
- Create lead modal
- Follow-up timeline
- Activity log

---

## 📊 Quick Test Checklist

Run these to verify everything works:

### Backend Tests

```powershell
# Test 1: Check tables
# (Open pgAdmin or DBeaver and run:)
SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'crm_%';
# Should return: 5 tables

# Test 2: Check scoring rules
SELECT COUNT(*) FROM crm_lead_scoring_rules WHERE is_active = true;
# Should return: 17

# Test 3: Check assignment rules
SELECT COUNT(*) FROM crm_lead_assignment_rules WHERE is_active = true;
# Should return: 4

# Test 4: Get dashboard stats
curl http://localhost:8000/api/crm/leads/dashboard/stats
# Should return JSON with statistics
```

### Frontend Tests (if routes added)

1. ✅ Navigate to `/crm/dashboard` - Should show statistics
2. ✅ Navigate to `/crm/leads` - Should show leads table
3. ✅ Click "Create Lead" - Modal should open
4. ✅ Fill form and submit - Lead should be created
5. ✅ Click on a lead - Detail page should open

---

## 🆘 Troubleshooting

### Issue: "python: command not found"

**Solution:** Use `py` instead:
```powershell
py create_crm_tables.py
py load_crm_initial_data.py
py -m uvicorn main:app --reload
```

### Issue: "No module named 'backend'"

**Solution:** Make sure you're in the backend directory:
```powershell
cd c:\NBFCSUITE\backend
python create_crm_tables.py
```

### Issue: Tables not created

**Solution:** Check database connection in `.env` file, or run SQL manually:
```sql
-- Open backend/scripts/crm_initial_data.sql in pgAdmin
-- And execute the CREATE TABLE statements
```

### Issue: API endpoints not showing

**Solution:**
1. Make sure backend restarted successfully
2. Check for errors in terminal
3. Clear browser cache
4. Try incognito mode

### Issue: Frontend routes not working

**Solution:**
1. Verify imports are correct
2. Check file paths
3. Look for errors in browser console (F12)

---

## 📚 Documentation

All detailed documentation is available:

| File | Purpose |
|------|---------|
| `INTEGRATION_COMPLETE_SUMMARY.md` | What's done & what to do |
| `CRM_FINAL_STATUS.md` | Complete status report |
| `EXECUTE_INTEGRATION_NOW.md` | Detailed execution guide |
| `CRM_QUICK_COMMANDS.md` | Command reference |
| `CRM_SETUP_COMPLETE.md` | Full setup guide |

---

## ✅ Success Criteria

You'll know everything is working when:

1. ✅ Backend docs show "CRM - Lead Management" section
2. ✅ 5 CRM tables exist in database
3. ✅ 17 scoring rules + 4 assignment rules loaded
4. ✅ Can create lead via API
5. ✅ Lead gets auto-scored (see `lead_score`)
6. ✅ Lead gets auto-assigned (see `assigned_to_user_id`)
7. ✅ Lead code auto-generated (LD-YYMMDD-XXXX)
8. ✅ Dashboard shows statistics (if frontend added)

---

## 🚀 Summary

**Time Required:** 5 minutes
**Commands to Run:** 3
**Files to Edit:** 1 (optional - routing file)
**Result:** Full CRM system with lead capture, scoring, assignment, and tracking!

**Start with Command 1 above!** ⬆️

---

**Last Updated:** July 11, 2026  
**Status:** ✅ READY TO EXECUTE  
**Estimated Time:** 5 minutes
