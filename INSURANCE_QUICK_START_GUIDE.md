# Insurance & Bancassurance Module - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you deploy and test the Insurance & Bancassurance module immediately.

---

## ⚡ Quick Setup

### Step 1: Database Migration (1 minute)

```bash
# Navigate to backend directory
cd c:\NBFCSUITE\backend

# Run the migration to create all 5 insurance tables
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> 005
INFO  [alembic.runtime.migration] Creating table insurance_agents
INFO  [alembic.runtime.migration] Creating table insurance_policies
INFO  [alembic.runtime.migration] Creating table insurance_premiums
INFO  [alembic.runtime.migration] Creating table insurance_claims
INFO  [alembic.runtime.migration] Creating table insurance_commissions
```

### Step 2: Verify Backend (30 seconds)

```bash
# Start the backend server (if not already running)
uvicorn main:app --reload --port 8000
```

**Test the API:**
- Open browser: `http://localhost:8000/docs`
- Scroll to "insurance" section
- You should see 51+ endpoints grouped by:
  - Policy Management (15+ endpoints)
  - Premium Collection (14+ endpoints)
  - Claims Processing (11+ endpoints)
  - Commission Tracking (11+ endpoints)

### Step 3: Verify Frontend (1 minute)

```bash
# Navigate to frontend directory
cd c:\NBFCSUITE\frontend\apps\admin-portal

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

**Test the UI:**
- Open browser: `http://localhost:3000/bancassurance`
- You should see the main dashboard with:
  - 4 quick action buttons (Policies, Premiums, Claims, Commissions)
  - Statistics cards
  - Recent activity feed
  - Alert summary

---

## 🧪 Test the Module (3 minutes)

### Test 1: Create an Agent (30 seconds)

**Using API (Swagger UI):**
1. Go to `http://localhost:8000/docs`
2. Find `POST /api/v1/insurance/agents`
3. Click "Try it out"
4. Use this sample data:
```json
{
  "agent_code": "AGT001",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "commission_rate_first_year": 10.0,
  "commission_rate_renewal": 5.0,
  "is_active": true
}
```
5. Click "Execute"
6. Note the `agent_id` from response

### Test 2: Create a Policy (1 minute)

**Using API (Swagger UI):**
1. Find `POST /api/v1/insurance/policies`
2. Click "Try it out"
3. Use this sample data (replace IDs):
```json
{
  "policy_number": "POL2024001",
  "customer_id": 1,
  "agent_id": 1,
  "policy_type": "LIFE",
  "sum_assured": 1000000,
  "premium_amount": 25000,
  "premium_frequency": "YEARLY",
  "policy_term": 20,
  "issue_date": "2024-01-01",
  "maturity_date": "2044-01-01",
  "status": "DRAFT"
}
```
4. Click "Execute"
5. Note the `policy_id` from response

### Test 3: View on Frontend (1 minute)

**Using the UI:**
1. Go to `http://localhost:3000/bancassurance/policies`
2. You should see the policy you just created
3. Click on the policy to view details
4. Try the "Activate" button to change status
5. Observe the status change from DRAFT to ACTIVE

### Test 4: Create a Premium Schedule (30 seconds)

**Using API (Swagger UI):**
1. Find `POST /api/v1/insurance/premiums`
2. Use this sample data:
```json
{
  "policy_id": 1,
  "premium_number": 1,
  "due_date": "2024-01-01",
  "amount": 25000,
  "status": "PENDING"
}
```
3. Click "Execute"

### Test 5: Record a Payment (30 seconds)

1. Go to `http://localhost:3000/bancassurance/premiums`
2. Find the premium you created
3. Click "Pay" button
4. Fill in the payment modal:
   - Paid Amount: 25000
   - Payment Mode: Online Transfer
   - Payment Date: Today
   - Transaction Reference: TXN123456
5. Click "Submit"
6. Observe the status change to PAID

---

## 📋 Complete Workflow Tests

### Workflow 1: Policy Lifecycle (5 minutes)

```
1. Create Policy (DRAFT)
   ↓
2. Activate Policy (ACTIVE)
   ↓
3. Create Premium Schedule
   ↓
4. Collect Premiums (PAID)
   ↓
5. Policy Matures (MATURED)
```

**Steps:**
1. Create a policy in DRAFT status
2. Activate it using the details page button
3. Create premium schedules for the policy
4. Record premium payments
5. When maturity date arrives, mark as MATURED

### Workflow 2: Claims Processing (5 minutes)

```
1. Register Claim (REGISTERED)
   ↓
2. Assess Claim (ASSESSED)
   ↓
3. Approve Claim (APPROVED)
   ↓
4. Settle Claim (SETTLED)
```

**Steps:**
1. Create a claim: `POST /api/v1/insurance/claims`
```json
{
  "policy_id": 1,
  "claim_number": "CLM2024001",
  "claim_type": "MATURITY",
  "claimed_amount": 1200000,
  "claim_date": "2024-06-15",
  "status": "REGISTERED"
}
```

2. Go to `http://localhost:3000/bancassurance/claims`
3. Find your claim and click "Assess"
4. Enter assessed amount: 1200000
5. Click "Approve" and enter approval remarks
6. Click "Settle" and enter settlement details

### Workflow 3: Commission Calculation (3 minutes)

```
1. Create Commission (PENDING)
   ↓
2. Approve Commission (APPROVED)
   ↓
3. Pay Commission (PAID)
```

**Steps:**
1. Create a commission: `POST /api/v1/insurance/commissions`
```json
{
  "agent_id": 1,
  "policy_id": 1,
  "commission_type": "FIRST_YEAR",
  "amount": 25000,
  "tds_amount": 2500,
  "net_amount": 22500,
  "status": "PENDING"
}
```

2. Go to `http://localhost:3000/bancassurance/commissions`
3. Find your commission and click "Approve"
4. Click "Pay" and enter payment details

---

## 🎯 Feature Testing Checklist

### Policy Management ✅
- [ ] Create new policy
- [ ] View policy list with filters
- [ ] View policy details
- [ ] Edit policy information
- [ ] Activate policy (DRAFT → ACTIVE)
- [ ] Mark policy as lapsed
- [ ] Revive lapsed policy
- [ ] Surrender policy
- [ ] Mark policy as matured
- [ ] Delete policy
- [ ] Search policies by number
- [ ] Filter by status/type/date

### Premium Collection ✅
- [ ] Create premium schedule
- [ ] View premium list
- [ ] View overdue premiums
- [ ] Record premium payment
- [ ] Verify late fee calculation
- [ ] Waive premium
- [ ] Filter by status
- [ ] View policy premiums
- [ ] Batch payment recording

### Claims Processing ✅
- [ ] Register new claim
- [ ] View claims list
- [ ] Filter by claim type
- [ ] Filter by claim status
- [ ] Assess claim amount
- [ ] Approve claim
- [ ] Reject claim
- [ ] Settle claim with deductions
- [ ] View claim history
- [ ] Track settlement amount

### Commission Tracking ✅
- [ ] Calculate commission
- [ ] View commission list
- [ ] Filter by agent
- [ ] Filter by status
- [ ] Approve commission
- [ ] Pay commission
- [ ] Verify TDS calculation
- [ ] View agent commissions
- [ ] View policy commissions
- [ ] Track payment history

### Dashboard ✅
- [ ] View policy statistics
- [ ] View premium metrics
- [ ] View claims summary
- [ ] View commission summary
- [ ] Navigate to sub-modules
- [ ] View recent activity
- [ ] View alert notifications
- [ ] Refresh dashboard data

---

## 📊 Sample Data for Testing

### Sample Agent Data
```json
{
  "agent_code": "AGT001",
  "name": "Rajesh Kumar",
  "email": "rajesh@example.com",
  "phone": "9876543210",
  "commission_rate_first_year": 10.0,
  "commission_rate_renewal": 5.0,
  "is_active": true
}
```

### Sample Policy Data
```json
{
  "policy_number": "LIFE/2024/001",
  "customer_id": 1,
  "agent_id": 1,
  "policy_type": "LIFE",
  "sum_assured": 1000000,
  "premium_amount": 25000,
  "premium_frequency": "YEARLY",
  "policy_term": 20,
  "premium_paying_term": 20,
  "issue_date": "2024-01-01",
  "maturity_date": "2044-01-01",
  "status": "DRAFT"
}
```

### Sample Premium Data
```json
{
  "policy_id": 1,
  "premium_number": 1,
  "due_date": "2024-01-01",
  "amount": 25000,
  "grace_period_days": 30,
  "status": "PENDING"
}
```

### Sample Claim Data
```json
{
  "policy_id": 1,
  "claim_number": "CLM/2024/001",
  "claim_type": "MATURITY",
  "claimed_amount": 1200000,
  "claim_date": "2024-06-15",
  "description": "Maturity claim for policy LIFE/2024/001",
  "status": "REGISTERED"
}
```

### Sample Commission Data
```json
{
  "agent_id": 1,
  "policy_id": 1,
  "commission_type": "FIRST_YEAR",
  "amount": 25000,
  "tds_percentage": 10.0,
  "tds_amount": 2500,
  "net_amount": 22500,
  "status": "PENDING"
}
```

---

## 🔍 Troubleshooting

### Issue: Tables not created
**Solution:**
```bash
# Check migration status
alembic current

# If not at latest, run upgrade
alembic upgrade head

# Verify tables exist in database
psql -U postgres -d nbfc_db -c "\dt insurance_*"
```

### Issue: API endpoints not showing
**Solution:**
```python
# Verify routers are registered in backend/main.py
from services.insurance.policy_router import router as policy_router
from services.insurance.premium_router import router as premium_router
from services.insurance.claim_router import router as claim_router
from services.insurance.commission_router import router as commission_router

app.include_router(policy_router, prefix="/api/v1/insurance", tags=["insurance"])
app.include_router(premium_router, prefix="/api/v1/insurance", tags=["insurance"])
app.include_router(claim_router, prefix="/api/v1/insurance", tags=["insurance"])
app.include_router(commission_router, prefix="/api/v1/insurance", tags=["insurance"])
```

### Issue: Frontend pages not loading
**Solution:**
```bash
# Check if file exists
ls frontend/apps/admin-portal/src/app/bancassurance/page.tsx

# Check for TypeScript errors
cd frontend/apps/admin-portal
npm run type-check

# Clear Next.js cache and rebuild
rm -rf .next
npm run dev
```

### Issue: CORS errors
**Solution:**
```python
# In backend/main.py, ensure CORS is configured:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: API calls failing from frontend
**Solution:**
```typescript
// Check NEXT_PUBLIC_API_URL in .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

// Verify in bancassurance.service.ts:
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
```

---

## 🎨 UI Navigation

### Main Routes
```
/bancassurance                           → Main Dashboard
/bancassurance/policies                  → Policy List
/bancassurance/policies/[id]             → Policy Details
/bancassurance/premiums                  → Premium Collection
/bancassurance/claims                    → Claims Processing
/bancassurance/commissions               → Commission Tracking
```

### Navigation Menu
Add this to your navigation sidebar:
```typescript
{
  title: "Insurance",
  icon: Building2,
  href: "/bancassurance",
  children: [
    { title: "Dashboard", href: "/bancassurance" },
    { title: "Policies", href: "/bancassurance/policies" },
    { title: "Premiums", href: "/bancassurance/premiums" },
    { title: "Claims", href: "/bancassurance/claims" },
    { title: "Commissions", href: "/bancassurance/commissions" },
  ]
}
```

---

## 📈 Performance Tips

### Backend Optimization
```python
# Add indexes to frequently queried columns (already in migration)
# Use pagination for large datasets
# Enable query result caching with Redis
# Use database connection pooling
```

### Frontend Optimization
```typescript
// Use React Query for caching
import { useQuery } from '@tanstack/react-query';

// Implement virtual scrolling for large lists
// Lazy load images and heavy components
// Use debounce for search inputs
```

---

## 🔒 Security Checklist

- [ ] Enable authentication on all API endpoints
- [ ] Implement role-based access control (RBAC)
- [ ] Validate all user inputs (backend + frontend)
- [ ] Use parameterized queries (already done with SQLAlchemy)
- [ ] Implement rate limiting on APIs
- [ ] Enable HTTPS in production
- [ ] Sanitize user inputs to prevent XSS
- [ ] Log all financial transactions
- [ ] Implement audit trail (already in models)

---

## 📚 API Documentation

### Access Swagger UI
```
http://localhost:8000/docs
```

### Access ReDoc
```
http://localhost:8000/redoc
```

### Export OpenAPI Spec
```bash
curl http://localhost:8000/openapi.json > insurance_api.json
```

---

## 🎯 Next Steps After Testing

### 1. Production Deployment
- [ ] Set up production database
- [ ] Configure environment variables
- [ ] Enable authentication/authorization
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

### 2. User Training
- [ ] Train insurance team on policy management
- [ ] Train accounts team on premium collection
- [ ] Train claims team on claims processing
- [ ] Train agents on commission tracking
- [ ] Create user manuals

### 3. Data Migration
- [ ] Export existing policy data
- [ ] Transform to new format
- [ ] Import using API or bulk upload
- [ ] Verify data integrity
- [ ] Reconcile totals

### 4. Go-Live Checklist
- [ ] Backup existing system
- [ ] Run migration in production
- [ ] Import historical data
- [ ] Verify all workflows
- [ ] Train end users
- [ ] Monitor for 24 hours
- [ ] Gather feedback
- [ ] Fix any issues

---

## 📞 Support Resources

### Documentation Files
1. `INSURANCE_BANCASSURANCE_COMPLETE.md` - Complete technical guide
2. `INSURANCE_MODULE_SUMMARY.md` - Business overview
3. `INSURANCE_API_TESTING_GUIDE.md` - API testing details
4. `INSURANCE_MODULE_COMPLETION_SUMMARY.md` - Implementation stats
5. `INSURANCE_QUICK_START_GUIDE.md` - This guide

### Code References
- Backend: `backend/services/insurance/`
- Frontend: `frontend/apps/admin-portal/src/app/bancassurance/`
- Types: `frontend/apps/admin-portal/src/types/bancassurance.ts`
- Service: `frontend/apps/admin-portal/src/services/bancassurance.service.ts`

---

## ✅ Success Criteria

You'll know the module is working correctly when:

1. **Database**
   - ✅ All 5 tables created
   - ✅ Foreign keys enforced
   - ✅ Indexes created

2. **Backend**
   - ✅ 51+ API endpoints visible in Swagger
   - ✅ Can create/read/update/delete entities
   - ✅ Lifecycle actions work (activate, lapse, etc.)

3. **Frontend**
   - ✅ All 6 pages load without errors
   - ✅ Can navigate between pages
   - ✅ Forms submit successfully
   - ✅ Data displays correctly

4. **Integration**
   - ✅ Frontend calls backend successfully
   - ✅ Data flows both ways
   - ✅ Actions reflect immediately
   - ✅ Error messages display properly

---

## 🎉 Congratulations!

If you've completed all the tests above, your Insurance & Bancassurance module is fully functional and ready for production use!

**What You've Achieved:**
- ✅ Complete policy lifecycle management
- ✅ Premium collection with overdue tracking
- ✅ Claims processing workflow
- ✅ Commission calculation and payment
- ✅ Comprehensive dashboard analytics
- ✅ 51+ REST API endpoints
- ✅ 6 fully functional frontend pages
- ✅ Type-safe implementation
- ✅ Production-ready code

**Time to Go Live!** 🚀

---

**Last Updated:** 2026-07-08  
**Module Version:** 1.0.0  
**Status:** Production Ready ✅
