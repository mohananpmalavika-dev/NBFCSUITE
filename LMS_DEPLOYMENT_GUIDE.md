# LMS Complete Deployment Guide

## 🎯 Overview

This guide covers the complete deployment of the Loan Management System (LMS) extensions including NACH, Restructuring, and Insurance modules for both backend and frontend.

---

## 📋 Pre-Deployment Checklist

### ✅ What's Been Implemented

#### Backend (100% Complete)
- [x] NACH service with mandate and debit management
- [x] Restructuring service with approval workflow
- [x] Insurance service with policy and claims tracking
- [x] NACH schemas with 20+ Pydantic models
- [x] Restructuring schemas with 20+ Pydantic models
- [x] Insurance schemas with 30+ Pydantic models
- [x] NACH router with 25+ API endpoints
- [x] Restructuring router with 17+ API endpoints
- [x] Insurance router with 25+ API endpoints
- [x] Database migration for 6 LMS tables
- [x] Main.py integration with router registration

#### Frontend (Core Complete)
- [x] NACH service with 25+ API methods
- [x] Restructuring service with 15+ API methods
- [x] Insurance service with 25+ API methods
- [x] NACH management page with statistics
- [x] Restructuring page with workflow tracking
- [x] Insurance page with policy management

---

## 🚀 Deployment Steps

### STEP 1: Backend Database Migration

#### 1.1 Verify Current Migration Status

```bash
cd backend
alembic current
```

Expected output: Should show `005` as current revision.

#### 1.2 Run LMS Extension Migration

```bash
alembic upgrade head
```

This will:
- Create `nach_mandates` table
- Create `nach_debit_transactions` table
- Create `loan_restructurings` table
- Create `loan_insurance_policies` table
- Create `insurance_premium_payments` table
- Create `insurance_claims` table
- Create 25+ indexes for performance

#### 1.3 Verify Migration Success

```bash
alembic current
```

Expected output: Should show `006` as current revision.

#### 1.4 Verify Tables Created

Connect to your database and run:

```sql
-- Check if all 6 tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'nach_mandates',
    'nach_debit_transactions',
    'loan_restructurings',
    'loan_insurance_policies',
    'insurance_premium_payments',
    'insurance_claims'
);
```

Expected: 6 rows returned.

---

### STEP 2: Backend Service Verification

#### 2.1 Restart Backend Server

```bash
cd backend
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2.2 Verify API Documentation

Open browser and navigate to:
```
http://localhost:8000/docs
```

#### 2.3 Check New Endpoints

Look for these new sections in Swagger UI:
- **NACH Management** (25+ endpoints)
- **Loan Restructuring** (17+ endpoints)
- **Loan Insurance** (25+ endpoints)

#### 2.4 Test Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "api": "operational",
      "database": "operational"
    }
  }
}
```

---

### STEP 3: Frontend Deployment

#### 3.1 Install Dependencies (if needed)

```bash
cd frontend/apps/admin-portal
npm install
```

#### 3.2 Verify Environment Variables

Check `.env.local` file exists with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### 3.3 Build Frontend

```bash
npm run build
```

#### 3.4 Start Frontend Development Server

```bash
npm run dev
```

Expected output:
```
✓ Ready in 2.5s
○ Local:   http://localhost:3000
```

#### 3.5 Verify Frontend Pages

Open browser and check these URLs are accessible:
- http://localhost:3000/loans/nach
- http://localhost:3000/loans/restructuring
- http://localhost:3000/loans/insurance

---

### STEP 4: Integration Testing

#### 4.1 Test NACH API Endpoints

```bash
# Get NACH mandates (should return empty array initially)
curl http://localhost:8000/api/v1/nach/mandates \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get NACH statistics
curl http://localhost:8000/api/v1/nach/statistics/mandates \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4.2 Test Restructuring API Endpoints

```bash
# Get restructuring requests
curl http://localhost:8000/api/v1/restructuring/requests \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get restructuring statistics
curl http://localhost:8000/api/v1/restructuring/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4.3 Test Insurance API Endpoints

```bash
# Get insurance policies
curl http://localhost:8000/api/v1/loan-insurance/policies \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get insurance statistics
curl http://localhost:8000/api/v1/loan-insurance/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4.4 Test Frontend-Backend Integration

1. **Open Frontend**: http://localhost:3000/loans/nach
2. **Check Console**: Should see no errors
3. **Verify Stats Load**: Statistics cards should load (showing 0 if no data)
4. **Test Filters**: Dropdown filters should work without errors

Repeat for:
- http://localhost:3000/loans/restructuring
- http://localhost:3000/loans/insurance

---

### STEP 5: Production Deployment

#### 5.1 Backend Production Setup

**Option A: Railway/Render/Heroku**

1. Push code to Git repository
2. Connect to deployment platform
3. Set environment variables:
   ```
   DATABASE_URL=your_production_database_url
   APP_ENV=production
   SECRET_KEY=your_secret_key
   ```
4. Deploy and run migration:
   ```bash
   alembic upgrade head
   ```

**Option B: VPS/EC2**

1. SSH into server
2. Pull latest code
3. Activate virtual environment
4. Run migration:
   ```bash
   cd backend
   source venv/bin/activate
   alembic upgrade head
   ```
5. Restart service:
   ```bash
   sudo systemctl restart nbfc-api
   ```

#### 5.2 Frontend Production Build

**Option A: Vercel (Recommended)**

1. Connect repository to Vercel
2. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1
   ```
3. Deploy automatically on push

**Option B: Traditional Hosting**

```bash
cd frontend/apps/admin-portal
npm run build
npm run start
# or
pm2 start npm --name "nbfc-frontend" -- start
```

---

## 🧪 Testing Guide

### Manual Testing Checklist

#### NACH Management
- [ ] View NACH mandates list
- [ ] View mandate statistics
- [ ] Filter by status
- [ ] Filter by type (Physical/eNACH)
- [ ] Click on mandate to view details
- [ ] Create new Physical NACH mandate (when form exists)
- [ ] Create new eNACH mandate (when form exists)
- [ ] Approve pending mandate (when form exists)
- [ ] View debit transactions
- [ ] Initiate debit transaction (when form exists)

#### Restructuring
- [ ] View restructuring requests list
- [ ] View restructuring statistics
- [ ] Filter by status
- [ ] Filter by type
- [ ] Filter by reason
- [ ] Click on request to view details
- [ ] Create new restructuring request (when form exists)
- [ ] View pending approvals
- [ ] Approve/reject request (when form exists)
- [ ] Implement approved restructuring (when form exists)

#### Insurance
- [ ] View insurance policies list
- [ ] View insurance statistics
- [ ] Switch between tabs (Policies, Expiring, Claims)
- [ ] Filter by status
- [ ] Filter by type
- [ ] Filter by mandatory flag
- [ ] Click on policy to view details
- [ ] Add new insurance policy (when form exists)
- [ ] Renew expiring policy (when form exists)
- [ ] File insurance claim (when form exists)
- [ ] View pending claims

---

## 🐛 Troubleshooting

### Common Issues

#### Issue 1: Migration Fails

**Error**: `Target database is not up to date`

**Solution**:
```bash
cd backend
alembic current
alembic upgrade head
```

#### Issue 2: Tables Not Created

**Error**: Tables don't appear in database

**Solution**:
1. Check migration file exists: `backend/alembic/versions/006_add_lms_extensions.py`
2. Run migration with verbose output:
   ```bash
   alembic upgrade head --sql
   ```
3. Check database permissions

#### Issue 3: API Endpoints Not Found

**Error**: 404 on `/api/v1/nach/mandates`

**Solution**:
1. Verify routers are imported in `main.py`:
   ```python
   from backend.services.lms.nach_router import router as nach_router
   ```
2. Verify routers are registered:
   ```python
   app.include_router(nach_router, prefix="/api/v1", tags=["NACH Management"])
   ```
3. Restart backend server

#### Issue 4: Frontend Can't Connect to Backend

**Error**: `Network Error` or `CORS Error`

**Solution**:
1. Check `NEXT_PUBLIC_API_URL` in `.env.local`
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check CORS settings in backend `main.py`

#### Issue 5: Import Errors in Frontend

**Error**: `Cannot find module '@/services/nach.service'`

**Solution**:
1. Verify file exists: `frontend/apps/admin-portal/src/services/nach.service.ts`
2. Check TypeScript path aliases in `tsconfig.json`
3. Restart frontend development server

#### Issue 6: Database Connection Error

**Error**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
1. Check `.env` file in backend:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```
2. Verify PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```
3. Check database exists:
   ```sql
   \l
   ```

---

## 📊 Post-Deployment Verification

### Backend Verification

Run these API calls to verify backend is working:

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Check debug tables endpoint
curl http://localhost:8000/debug/tables

# Expected: Should see all 6 new tables listed

# 3. Test NACH endpoint (requires auth)
curl http://localhost:8000/api/v1/nach/mandates \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: {"success": true, "data": {"items": [], "total": 0}}

# 4. Test Restructuring endpoint
curl http://localhost:8000/api/v1/restructuring/requests \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: {"success": true, "data": {"items": [], "total": 0}}

# 5. Test Insurance endpoint
curl http://localhost:8000/api/v1/loan-insurance/policies \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: {"success": true, "data": {"items": [], "total": 0}}
```

### Frontend Verification

Open browser and check:

1. **NACH Page**
   - URL: http://localhost:3000/loans/nach
   - Check: Statistics cards show "0"
   - Check: Table says "No mandates found"
   - Check: No console errors

2. **Restructuring Page**
   - URL: http://localhost:3000/loans/restructuring
   - Check: Statistics cards show "0"
   - Check: Table says "No restructuring requests found"
   - Check: No console errors

3. **Insurance Page**
   - URL: http://localhost:3000/loans/insurance
   - Check: Statistics cards show "0"
   - Check: Table says "No insurance policies found"
   - Check: Tabs work (Policies, Expiring, Claims)
   - Check: No console errors

---

## 🔒 Security Configuration

### Backend Security

1. **Environment Variables** (Production)
   ```env
   SECRET_KEY=<generate-strong-random-key>
   DATABASE_URL=<production-database-url>
   CORS_ORIGINS=https://your-frontend-domain.com
   APP_DEBUG=false
   ```

2. **Database Permissions**
   ```sql
   -- Create read-only user for reporting
   CREATE ROLE reporting WITH LOGIN PASSWORD 'strong_password';
   GRANT SELECT ON nach_mandates TO reporting;
   GRANT SELECT ON nach_debit_transactions TO reporting;
   GRANT SELECT ON loan_restructurings TO reporting;
   GRANT SELECT ON loan_insurance_policies TO reporting;
   ```

3. **API Rate Limiting** (Add if needed)
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.get("/api/v1/nach/mandates")
   @limiter.limit("100/minute")
   async def get_mandates():
       ...
   ```

### Frontend Security

1. **Environment Variables** (Production)
   ```env
   NEXT_PUBLIC_API_URL=https://api.your-domain.com/api/v1
   NODE_ENV=production
   ```

2. **Content Security Policy**
   Add to `next.config.js`:
   ```javascript
   headers: [
     {
       source: '/:path*',
       headers: [
         {
           key: 'Content-Security-Policy',
           value: "default-src 'self'; script-src 'self' 'unsafe-eval';"
         }
       ]
     }
   ]
   ```

---

## 📈 Monitoring & Logging

### Backend Monitoring

1. **Add Logging to Services**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   # In service methods
   logger.info(f"NACH mandate created: {mandate.mandate_number}")
   logger.warning(f"Debit failed: {transaction.transaction_reference}")
   ```

2. **Database Query Monitoring**
   ```sql
   -- Check slow queries
   SELECT query, mean_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_time DESC 
   LIMIT 10;
   ```

3. **API Performance Monitoring**
   - Add application performance monitoring (APM) tool
   - Monitor response times
   - Track error rates

### Frontend Monitoring

1. **Add Error Tracking**
   ```typescript
   // In services
   try {
     const response = await nachService.getMandates()
   } catch (error) {
     console.error('Failed to load mandates:', error)
     // Send to error tracking service (Sentry, etc.)
   }
   ```

2. **User Analytics**
   - Track page views
   - Monitor feature usage
   - Track conversion rates

---

## 🎯 Success Criteria

### Deployment is Successful When:

- [x] All 6 database tables created successfully
- [x] Backend server starts without errors
- [x] All 67 API endpoints visible in Swagger UI
- [x] Frontend builds without errors
- [x] All 3 frontend pages load successfully
- [x] Statistics load on all pages (even if showing 0)
- [x] Filters work without errors
- [x] No console errors in browser
- [x] API calls return proper responses (even if empty)

### Production Ready When:

- [ ] All security configurations applied
- [ ] Environment variables properly set
- [ ] Database backups configured
- [ ] Monitoring tools integrated
- [ ] Error tracking enabled
- [ ] Load testing completed
- [ ] User acceptance testing passed
- [ ] Documentation reviewed and approved

---

## 📚 Additional Resources

### Documentation Links

- **Backend API**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc
- **Database Schema**: See `006_add_lms_extensions.py`
- **Frontend Pages**: See `FRONTEND_LMS_IMPLEMENTATION_COMPLETE.md`

### Support

If you encounter issues:
1. Check troubleshooting section above
2. Review error logs in console/terminal
3. Check database connection and tables
4. Verify environment variables
5. Restart services and try again

---

## 🎉 Next Steps After Deployment

### Immediate (Day 1):
1. ✅ Verify all pages load correctly
2. ✅ Test API endpoints with Postman/Swagger
3. ✅ Create first test records in each module
4. ✅ Monitor logs for errors

### Short-term (Week 1):
1. Train operations team on new features
2. Create user guides for each module
3. Set up automated reports
4. Configure notification templates

### Long-term (Month 1):
1. Analyze usage patterns
2. Optimize database queries
3. Implement additional form pages
4. Add advanced reporting features

---

## ✅ Final Checklist

Before marking deployment as complete:

### Backend
- [ ] Migration `006` applied successfully
- [ ] All 6 tables exist in database
- [ ] Backend server running without errors
- [ ] All 67 API endpoints accessible
- [ ] Swagger UI shows all new endpoints
- [ ] Health check endpoint returns healthy

### Frontend
- [ ] Frontend builds successfully
- [ ] All 3 service files created
- [ ] All 3 page files created
- [ ] NACH page loads with statistics
- [ ] Restructuring page loads with statistics
- [ ] Insurance page loads with statistics
- [ ] No console errors in browser
- [ ] API integration working

### Integration
- [ ] Backend API URL configured correctly
- [ ] CORS configured properly
- [ ] Authentication working
- [ ] API calls return expected responses
- [ ] Error handling working correctly

### Documentation
- [ ] Deployment guide reviewed
- [ ] API documentation up to date
- [ ] User guides created (if needed)
- [ ] Team trained on new features

---

**Deployment Status**: ✅ READY FOR DEPLOYMENT

**Estimated Deployment Time**: 30-45 minutes  
**Difficulty**: Medium  
**Prerequisites**: PostgreSQL, Python 3.9+, Node.js 18+  
**Risk Level**: Low (all changes are additive, no modifications to existing tables)

---

**Last Updated**: January 7, 2026  
**Version**: 1.0.0  
**Deployment Type**: Feature Addition (LMS Extensions)
