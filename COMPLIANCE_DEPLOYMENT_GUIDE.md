# CRILC & SMA Compliance - Deployment Guide

## 🚀 Quick Start Deployment

### Prerequisites
- PostgreSQL database running
- Python 3.9+ installed
- Node.js 18+ installed
- Backend and frontend environments configured

---

## 📋 Step-by-Step Deployment

### Step 1: Backend Database Migration

```bash
# Navigate to backend directory
cd c:\NBFCSUITE\backend

# Check current migration status
alembic current

# Apply compliance migration
alembic upgrade head

# Verify migration applied
alembic current
# Expected output: 008 (head)

# Check tables created
psql -d nbfcsuite -c "\dt *compliance*"
# Should show 7 tables:
# - crilc_borrowers
# - crilc_facilities
# - sma_tracking
# - sma_status_history
# - crilc_quarterly_returns
# - sma_quarterly_reports
# - compliance_alerts
```

### Step 2: Backend Restart

```bash
# Option 1: Using systemd (Production)
systemctl restart nbfcsuite-backend
systemctl status nbfcsuite-backend

# Option 2: Direct Python (Development)
cd c:\NBFCSUITE\backend
python main.py

# Option 3: Using Uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Verify Backend APIs

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test SMA dashboard endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/compliance/sma/dashboard

# Test large credits endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/compliance/crilc/borrowers?limit=10

# Expected: JSON responses with data or empty arrays
```

### Step 4: Frontend Setup

```bash
# Navigate to frontend
cd c:\NBFCSUITE\frontend\apps\admin-portal

# Install dependencies (if not already done)
npm install

# Build frontend
npm run build

# Start production server
npm run start

# OR for development
npm run dev
```

### Step 5: Verify Frontend Pages

Open browser and navigate to:
- ✅ http://localhost:3000/compliance/sma-dashboard
- ✅ http://localhost:3000/compliance/large-credits
- ✅ http://localhost:3000/compliance/sma-tracking
- ✅ http://localhost:3000/compliance/alerts
- ✅ http://localhost:3000/compliance/quarterly-reports

Check:
- [ ] Pages load without errors
- [ ] Navigation menu shows "Compliance" section
- [ ] API calls are successful (check Network tab)
- [ ] No console errors

### Step 6: Initial Data Setup

```bash
# Run initial large credit identification
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "threshold_amount": 50000000,
    "as_on_date": "2024-01-20",
    "include_group_exposure": true
  }' \
  http://localhost:8000/api/v1/compliance/crilc/identify-large-credits

# Calculate initial SMA status
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "as_on_date": "2024-01-20",
    "calculate_provisions": true
  }' \
  http://localhost:8000/api/v1/compliance/sma/calculate
```

### Step 7: Configure Scheduled Jobs

Create cron jobs for automated operations:

```bash
# Edit crontab
crontab -e

# Add the following lines:

# Daily SMA calculation at 2 AM
0 2 * * * cd /path/to/NBFCSUITE && /path/to/python -m backend.jobs.calculate_daily_sma >> /var/log/nbfc/sma-calc.log 2>&1

# Update alert status at 6 AM
0 6 * * * cd /path/to/NBFCSUITE && /path/to/python -m backend.jobs.update_compliance_alerts >> /var/log/nbfc/alerts.log 2>&1

# Monthly large credit identification on 1st at 3 AM
0 3 1 * * cd /path/to/NBFCSUITE && /path/to/python -m backend.jobs.identify_large_credits >> /var/log/nbfc/large-credits.log 2>&1

# Save and exit
```

### Step 8: User Permissions Setup

Configure user permissions in the system:

```sql
-- Grant compliance permissions to compliance officer role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'Compliance Officer'
AND p.name IN (
    'compliance.read',
    'compliance.write',
    'compliance.approve'
);

-- Grant submit permission to compliance head role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'Compliance Head'
AND p.name = 'compliance.submit';
```

---

## ✅ Verification Checklist

### Backend Verification

- [ ] **Migration Applied**
  ```bash
  alembic current | grep "008"
  ```

- [ ] **Tables Created**
  ```bash
  psql -d nbfcsuite -c "\dt *compliance*" | wc -l
  # Should return 7 or more
  ```

- [ ] **Backend Running**
  ```bash
  curl http://localhost:8000/health
  # Should return: {"status":"healthy"}
  ```

- [ ] **API Endpoints Accessible**
  ```bash
  curl -I http://localhost:8000/api/v1/compliance/sma/dashboard
  # Should return: 200 OK or 401 Unauthorized (if auth required)
  ```

- [ ] **Router Registered**
  ```bash
  curl http://localhost:8000/openapi.json | grep -c "compliance"
  # Should return a number > 0
  ```

### Frontend Verification

- [ ] **Build Successful**
  ```bash
  npm run build
  # Should complete without errors
  ```

- [ ] **Pages Accessible**
  - Navigate to each compliance page
  - All pages load without 404 errors
  - No console errors in browser DevTools

- [ ] **Navigation Working**
  - "Compliance" menu item visible in sidebar
  - All 5 sub-menu items present
  - Clicking navigates to correct pages

- [ ] **API Integration**
  - Open DevTools Network tab
  - Navigate to dashboard
  - Check for API calls to `/api/v1/compliance/*`
  - Verify responses are successful (200 status)

- [ ] **UI Components**
  - Cards display properly
  - Tables render data
  - Buttons are clickable
  - Dialogs open/close correctly
  - Forms validate inputs

### Integration Verification

- [ ] **End-to-End Flow 1: SMA Dashboard**
  1. Navigate to `/compliance/sma-dashboard`
  2. Verify statistics display
  3. Change date filter
  4. Click refresh button
  5. Check data updates

- [ ] **End-to-End Flow 2: Calculate SMA**
  1. Navigate to `/compliance/sma-tracking`
  2. Click "Calculate SMA Status"
  3. Enter date
  4. Click "Calculate"
  5. Verify success toast
  6. Check tracking table updates

- [ ] **End-to-End Flow 3: Generate Report**
  1. Navigate to `/compliance/quarterly-reports`
  2. Click "Generate New Return"
  3. Fill in form
  4. Click "Generate"
  5. Verify return appears in table
  6. Check status is "draft"

- [ ] **End-to-End Flow 4: Resolve Alert**
  1. Navigate to `/compliance/alerts`
  2. Find an open alert
  3. Click "Resolve"
  4. Enter resolution notes
  5. Click "Resolve Alert"
  6. Verify alert status changes

---

## 🔧 Troubleshooting

### Backend Issues

**Issue: Migration fails**
```bash
# Check database connection
psql -d nbfcsuite -c "SELECT version();"

# Check for conflicts
alembic history

# Rollback if needed
alembic downgrade -1

# Reapply
alembic upgrade head
```

**Issue: API returns 404**
```bash
# Check if router is registered
grep -r "compliance_router" backend/main.py

# Check logs
tail -f /var/log/nbfc/backend.log

# Restart backend
systemctl restart nbfcsuite-backend
```

**Issue: Permission denied**
```bash
# Check user permissions
SELECT u.email, r.name, p.name
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE p.name LIKE 'compliance%';
```

### Frontend Issues

**Issue: Pages show 404**
```bash
# Check file exists
ls -la frontend/apps/admin-portal/src/app/\(dashboard\)/compliance/

# Rebuild
npm run build

# Clear Next.js cache
rm -rf .next
npm run dev
```

**Issue: API calls fail**
```javascript
// Check API base URL in browser console
console.log(process.env.NEXT_PUBLIC_API_URL)

// Check network tab for failed requests
// Verify CORS settings in backend
```

**Issue: Types not found**
```bash
# Check types file exists
ls -la frontend/apps/admin-portal/src/types/compliance.types.ts

# Restart TypeScript server in VSCode
# Cmd/Ctrl + Shift + P -> "TypeScript: Restart TS Server"
```

---

## 📊 Performance Optimization

### Backend

```python
# Add indexes if needed
CREATE INDEX idx_sma_tracking_composite 
ON sma_tracking(tenant_id, as_on_date, current_sma_status);

# Optimize queries
# Use select_related for foreign keys
# Use prefetch_related for many-to-many

# Enable query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Frontend

```bash
# Enable production build optimizations
npm run build -- --profile

# Analyze bundle size
npm run analyze

# Optimize images (if any)
npm run optimize-images
```

---

## 🔐 Security Hardening

### Backend Security

```python
# Ensure HTTPS in production
# In main.py or config
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Frontend Security

```javascript
// Environment variables
// Never expose sensitive data
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

// Content Security Policy
// Add to next.config.js
headers: [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; ..."
  }
]
```

---

## 📈 Monitoring Setup

### Application Monitoring

```bash
# Install monitoring agent
pip install prometheus-fastapi-instrumentator

# Add to main.py
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

# Access metrics
curl http://localhost:8000/metrics
```

### Log Monitoring

```bash
# Centralized logging
tail -f /var/log/nbfc/backend.log | grep "compliance"

# Error tracking
grep -i "error" /var/log/nbfc/backend.log | grep "compliance"

# Alert on critical errors
# Setup log monitoring tool (e.g., ELK, Splunk)
```

---

## 🎓 User Training

### For Compliance Officers

1. **Daily Tasks**
   - Check SMA Dashboard every morning
   - Review and resolve open alerts
   - Monitor accounts in SMA-2 status

2. **Weekly Tasks**
   - Review SMA tracking trends
   - Follow up on high-severity alerts
   - Check provision calculations

3. **Monthly Tasks**
   - Run large credit identification (1st of month)
   - Review and clean up resolved alerts
   - Prepare for quarterly reporting

4. **Quarterly Tasks**
   - Generate CRILC quarterly return
   - Generate SMA quarterly report
   - Review and approve returns
   - Submit to RBI by deadline (15th)

### Training Materials

- User guide: `docs/COMPLIANCE_QUICK_REFERENCE.md`
- Video tutorials: (to be created)
- FAQ document: (to be created)
- Contact: compliance@company.com

---

## ✅ Go-Live Checklist

### Pre-Go-Live

- [ ] All backend tests passed
- [ ] All frontend tests passed
- [ ] Database backup taken
- [ ] Rollback plan documented
- [ ] Monitoring setup complete
- [ ] Logs configured
- [ ] Users trained
- [ ] Permissions configured
- [ ] Cron jobs scheduled

### Go-Live Day

- [ ] Deploy during maintenance window
- [ ] Apply database migration
- [ ] Restart backend services
- [ ] Deploy frontend build
- [ ] Run smoke tests
- [ ] Verify all pages load
- [ ] Test critical workflows
- [ ] Monitor logs for errors
- [ ] Notify users of new feature

### Post-Go-Live

- [ ] Monitor for 24 hours
- [ ] Check cron job execution
- [ ] Verify data accuracy
- [ ] Collect user feedback
- [ ] Address any issues
- [ ] Update documentation
- [ ] Conduct retrospective

---

## 📞 Support

**Technical Issues**: tech-support@company.com  
**Compliance Questions**: compliance@company.com  
**Emergency Hotline**: [Phone Number]  
**Documentation**: See README files in respective directories

---

**Deployment Guide Version**: 1.0.0  
**Last Updated**: January 20, 2024  
**Status**: Production Ready
