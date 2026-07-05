# 🚀 QUICK START GUIDE
## Accounting & Collections Modules

**Last Updated**: January 5, 2026  
**Version**: 2.0  
**Time to Deploy**: ~10 minutes  

---

## ⚡ SUPER QUICK START (5 Steps)

### 1. Run Database Migration (2 minutes)
```bash
cd c:\NBFCSUITE
psql -U postgres -d nbfc_db -f database/migrations/add_accounting_tables_migration.sql
```

### 2. Start Backend (1 minute)
```bash
cd backend
python main.py
```

### 3. Start Frontend (1 minute)
```bash
cd frontend/apps/admin-portal
npm run dev
```

### 4. Open Browser (30 seconds)
```
Backend API:  http://localhost:8000/docs
Accounting:   http://localhost:3000/accounting
Collections:  http://localhost:3000/collections
```

### 5. Test It! (5 minutes)
- ✅ View Accounting Dashboard
- ✅ Browse Chart of Accounts
- ✅ Check Collection Dashboard
- ✅ View Overdue Accounts

**Done! You're ready to use the system!** 🎉

---

## 📖 DETAILED SETUP

### Prerequisites
- ✅ PostgreSQL installed and running
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed

### Step-by-Step Setup

#### Step 1: Database Setup

##### 1.1 Connect to PostgreSQL
```bash
psql -U postgres
```

##### 1.2 Verify Database
```sql
-- Check if database exists
\l nbfc_db

-- Connect to database
\c nbfc_db

-- List tables
\dt
```

##### 1.3 Run Migration
```bash
# Exit psql first (type \q)
cd c:\NBFCSUITE
psql -U postgres -d nbfc_db -f database/migrations/add_accounting_tables_migration.sql
```

##### 1.4 Verify Tables Created
```sql
-- Reconnect to database
psql -U postgres -d nbfc_db

-- Check new tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'chart_of_accounts',
    'journal_entries',
    'journal_entry_lines',
    'general_ledger',
    'trial_balances',
    'accounting_periods'
);

-- Should show 6 tables
```

##### 1.5 Check Default Accounts
```sql
-- View default system accounts
SELECT account_code, account_name, account_type 
FROM chart_of_accounts 
WHERE tenant_id = 1 
ORDER BY account_code;

-- Should show 15 default accounts
```

#### Step 2: Backend Setup

##### 2.1 Check Environment
```bash
cd c:\NBFCSUITE\backend

# Verify .env file exists
dir .env

# Check Python version
python --version

# Should be 3.11 or higher
```

##### 2.2 Start Backend Server
```bash
# Make sure you're in backend directory
cd c:\NBFCSUITE\backend

# Start server
python main.py
```

##### 2.3 Verify Backend Running
```
Expected Output:
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

##### 2.4 Test API Endpoints
Open browser and visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

##### 2.5 Test Accounting Statistics
```bash
# In new terminal
curl http://localhost:8000/api/v1/accounting/statistics
```

Expected Response:
```json
{
  "success": true,
  "data": {
    "total_accounts": 15,
    "active_accounts": 15,
    "total_journal_entries": 0,
    ...
  }
}
```

#### Step 3: Frontend Setup

##### 3.1 Navigate to Frontend
```bash
cd c:\NBFCSUITE\frontend\apps\admin-portal
```

##### 3.2 Install Dependencies (if not done)
```bash
npm install
```

##### 3.3 Start Development Server
```bash
npm run dev
```

Expected Output:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

##### 3.4 Open in Browser
```
http://localhost:3000/accounting
http://localhost:3000/collections
```

---

## 🧪 TESTING GUIDE

### Test 1: Accounting Dashboard
**URL**: http://localhost:3000/accounting

**What to Check**:
- ✅ Dashboard loads
- ✅ 6 metric cards display
- ✅ Recent transactions show (mock data)
- ✅ Quick actions clickable
- ✅ Responsive on mobile

**Expected**: Professional dashboard with financial metrics

---

### Test 2: Chart of Accounts
**URL**: http://localhost:3000/accounting/accounts

**What to Check**:
- ✅ Account tree displays
- ✅ Hierarchical structure visible
- ✅ Expand/collapse works
- ✅ Color coding by type
- ✅ Balances show
- ✅ Search works
- ✅ Filter by type works

**Expected**: Hierarchical account list with 8 sample accounts

---

### Test 3: Journal Entries
**URL**: http://localhost:3000/accounting/journal-entries

**What to Check**:
- ✅ Entry list displays
- ✅ Status badges show correctly
- ✅ Filter by status works
- ✅ Filter by type works
- ✅ Search works
- ✅ Summary cards show counts
- ✅ View entry button works

**Expected**: List of 5 sample journal entries

---

### Test 4: Financial Reports
**URL**: http://localhost:3000/accounting/reports

**What to Check**:
- ✅ 3 report cards display
- ✅ Click trial balance card
- ✅ Date picker works
- ✅ Generate button works
- ✅ Report displays with data
- ✅ Export button appears
- ✅ Back button works

**Expected**: Report selection and generation workflow

---

### Test 5: Collection Dashboard
**URL**: http://localhost:3000/collections

**What to Check**:
- ✅ Dashboard loads
- ✅ 4 metric cards show
- ✅ DPD buckets display (5 buckets)
- ✅ Top overdue table shows
- ✅ Quick actions work
- ✅ Priority alerts visible

**Expected**: Collection metrics and DPD bucket analysis

---

### Test 6: Overdue Accounts
**URL**: http://localhost:3000/collections/overdue

**What to Check**:
- ✅ Summary cards display
- ✅ Account table loads
- ✅ Search by name works
- ✅ Filter by bucket works
- ✅ Contact info shows
- ✅ DPD badges display
- ✅ Action buttons visible

**Expected**: List of 5 overdue accounts with full details

---

### Test 7: Collection Queue
**URL**: http://localhost:3000/collections/queue

**What to Check**:
- ✅ Priority tabs work
- ✅ Summary cards show
- ✅ Queue items display
- ✅ Tab switching works
- ✅ Action buttons visible
- ✅ Notes section shows

**Expected**: Priority-based queue with 6 items

---

### Test 8: API Endpoints

#### Test Accounting APIs
```bash
# Get statistics
curl http://localhost:8000/api/v1/accounting/statistics

# Get accounts
curl http://localhost:8000/api/v1/accounting/accounts

# Get journal entries
curl http://localhost:8000/api/v1/accounting/journal-entries
```

#### Test Collection APIs
```bash
# Get collection statistics
curl http://localhost:8000/api/v1/loans/collection/statistics

# Get overdue accounts
curl http://localhost:8000/api/v1/loans/collection/overdue-accounts
```

---

## 🐛 TROUBLESHOOTING

### Backend Issues

#### Issue: "ModuleNotFoundError"
```bash
# Solution: Install dependencies
cd backend
pip install -r requirements.txt
```

#### Issue: "Database connection failed"
```bash
# Solution: Check PostgreSQL is running
# Windows:
services.msc
# Look for PostgreSQL service

# Check connection
psql -U postgres -d nbfc_db
```

#### Issue: "Port 8000 already in use"
```bash
# Solution: Kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Frontend Issues

#### Issue: "Module not found"
```bash
# Solution: Install dependencies
cd frontend/apps/admin-portal
npm install
```

#### Issue: "Port 3000 already in use"
```bash
# Solution: Use different port
npm run dev -- -p 3001
```

#### Issue: "Cannot connect to API"
```bash
# Solution: Check backend is running
curl http://localhost:8000/health

# If not working, restart backend
cd backend
python main.py
```

### Database Issues

#### Issue: "Table does not exist"
```bash
# Solution: Run migration again
cd c:\NBFCSUITE
psql -U postgres -d nbfc_db -f database/migrations/add_accounting_tables_migration.sql
```

#### Issue: "Permission denied"
```sql
-- Solution: Grant permissions
GRANT ALL PRIVILEGES ON DATABASE nbfc_db TO your_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_user;
```

---

## 📋 VERIFICATION CHECKLIST

### Database
- [ ] PostgreSQL running
- [ ] Database `nbfc_db` exists
- [ ] 6 new tables created
- [ ] 15 default accounts inserted
- [ ] No migration errors

### Backend
- [ ] Server starts without errors
- [ ] Swagger UI accessible at /docs
- [ ] Health check passes
- [ ] Accounting stats API works
- [ ] Collection stats API works

### Frontend
- [ ] Dev server starts
- [ ] No compilation errors
- [ ] Accounting dashboard loads
- [ ] Collections dashboard loads
- [ ] All 9 pages accessible
- [ ] Mock data displays
- [ ] Responsive on mobile

### Integration
- [ ] Frontend can reach backend
- [ ] API calls work (mock data)
- [ ] No CORS errors
- [ ] No console errors

---

## 🔧 CONFIGURATION

### Backend Configuration
File: `backend/.env`

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/nbfc_db

# Application
APP_NAME="NBFC Financial Suite"
APP_ENV=development
APP_DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend Configuration
File: `frontend/apps/admin-portal/.env.local`

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME="NBFC Admin Portal"
```

---

## 📚 QUICK REFERENCE

### Important URLs
| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | http://localhost:8000 | Main API |
| Swagger UI | http://localhost:8000/docs | API Documentation |
| ReDoc | http://localhost:8000/redoc | Alternative API Docs |
| Frontend | http://localhost:3000 | Main Application |
| Accounting | http://localhost:3000/accounting | Accounting Module |
| Collections | http://localhost:3000/collections | Collections Module |

### Key Commands
```bash
# Start Backend
cd backend && python main.py

# Start Frontend
cd frontend/apps/admin-portal && npm run dev

# Run Migration
psql -U postgres -d nbfc_db -f database/migrations/add_accounting_tables_migration.sql

# Check Database
psql -U postgres -d nbfc_db

# View Logs
# Backend logs in terminal
# Frontend logs in browser console (F12)
```

### Default Credentials
```
# Update these based on your setup
Database User: postgres
Database Password: your_password
Database Name: nbfc_db

# Application
Tenant ID: 1 (default)
User ID: 1 (default for testing)
```

---

## 🎯 NEXT STEPS AFTER SETUP

### 1. Connect Real APIs
Replace mock data in frontend with actual API calls:
- Update `fetchAccounts()` functions
- Add error handling
- Add loading states

### 2. Test with Real Data
- Create actual accounts via API
- Create journal entries
- Generate real reports
- Test collection workflow

### 3. Customize
- Update branding
- Modify color schemes
- Add company logo
- Adjust layouts

### 4. Deploy
- Set up production database
- Configure production environment
- Deploy backend to server
- Deploy frontend to hosting

---

## 📞 SUPPORT

### Documentation
- `ACCOUNTING_MODULE_COMPLETE.md` - Backend details
- `FRONTEND_UI_COMPLETE.md` - Frontend details
- `COMPLETE_IMPLEMENTATION_SUMMARY.md` - Full overview

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Common Issues
Check the Troubleshooting section above for solutions to common problems.

---

## ✅ SUCCESS INDICATORS

You'll know setup is successful when:
- ✅ Backend server running without errors
- ✅ Frontend loads in browser
- ✅ Swagger UI shows 133+ endpoints
- ✅ Accounting dashboard displays metrics
- ✅ Collections dashboard shows DPD buckets
- ✅ All 9 pages are accessible
- ✅ Mock data displays correctly
- ✅ No errors in browser console
- ✅ API calls return data

**When all checked, you're ready to go!** 🚀

---

## 🎉 YOU'RE ALL SET!

Your NBFC Accounting & Collections system is now:
- ✅ Installed
- ✅ Running
- ✅ Tested
- ✅ Ready for use

**Enjoy your new enterprise-grade financial system!**

---

**End of Quick Start Guide**
