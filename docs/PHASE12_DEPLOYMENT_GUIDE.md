# Phase 12: Audit & Compliance - Deployment Guide

**Version:** 1.0  
**Date:** July 3, 2026  
**Status:** Production Ready

---

## Pre-Deployment Checklist

### Environment Requirements
- [ ] PostgreSQL 15+ installed and running
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Git repository access
- [ ] Database credentials configured

### Backup Requirements
- [ ] Database backup created
- [ ] Code repository tagged
- [ ] Configuration backed up
- [ ] Rollback plan prepared

---

## Deployment Steps

### Phase 1: Database Deployment

#### Step 1.1: Verify Database Connection
```bash
# Test connection
psql -U nbfc_user -h localhost -d nbfcsuite -c "SELECT version();"
```

#### Step 1.2: Run Migration
```bash
# Navigate to project root
cd c:\NBFCSUITE

# Run migration script
psql -U nbfc_user -d nbfcsuite -f infra/migrations/029_audit_compliance.sql
```

#### Step 1.3: Verify Tables Created
```sql
-- Check tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%audit%' OR table_name LIKE '%compliance%';

-- Expected output: 10 tables
-- - audit_trails
-- - compliance_rules
-- - compliance_violations
-- - audit_schedules
-- - audit_executions
-- - audit_findings
-- - regulatory_reports
-- - compliance_certifications
-- - policy_acknowledgements
-- - data_retention_logs
```

#### Step 1.4: Verify Views
```sql
-- Check views
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public' 
AND table_name LIKE 'vw_%audit%' OR table_name LIKE 'vw_%compliance%';

-- Expected output: 4 views
```

#### Step 1.5: Verify Triggers
```sql
-- Check triggers
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public' 
AND (trigger_name LIKE '%audit%' OR trigger_name LIKE '%compliance%');

-- Expected output: 7 triggers
```

#### Step 1.6: Test Query Performance
```sql
-- Test audit trail query
EXPLAIN ANALYZE 
SELECT * FROM audit_trails 
WHERE event_type = 'CREATE' 
LIMIT 100;

-- Verify index usage
```

---

### Phase 2: Backend Deployment

#### Step 2.1: Navigate to Backend
```bash
cd services/gold
```

#### Step 2.2: Install/Update Dependencies
```bash
# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2.3: Verify Model Integration
```bash
# Check if models are importable
python -c "from app.models.audit_compliance import AuditTrail; print('✅ Models OK')"
```

#### Step 2.4: Verify Schema Integration
```bash
# Check if schemas are importable
python -c "from app.schemas.audit_compliance import AuditTrailCreate; print('✅ Schemas OK')"
```

#### Step 2.5: Verify Router Integration
```bash
# Check if router is importable
python -c "from app.routers.audit_compliance import router; print('✅ Router OK')"
```

#### Step 2.6: Start Backend Service
```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8013

# Production mode
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8013
```

#### Step 2.7: Verify Backend Health
```bash
# Test health endpoint
curl http://localhost:8013/health

# Expected output: {"status": "ok"}
```

#### Step 2.8: Test API Endpoints
```bash
# Test audit trails endpoint
curl http://localhost:8013/api/v1/gold/audit-compliance/audit-trails

# Test compliance rules endpoint
curl http://localhost:8013/api/v1/gold/audit-compliance/compliance-rules

# Test statistics endpoint
curl http://localhost:8013/api/v1/gold/audit-compliance/statistics/audit-trails
```

---

### Phase 3: Frontend Deployment

#### Step 3.1: Navigate to Frontend
```bash
cd ../../apps/customer-app
```

#### Step 3.2: Integrate API Methods
```bash
# Option 1: Manual copy-paste
# Open phase12_audit_api.ts and copy contents to goldApi.ts

# Option 2: Automated append (review before using)
type app\gold-lending\phase12_audit_api.ts >> app\gold-lending\goldApi.ts
```

#### Step 3.3: Install Dependencies
```bash
npm install
```

#### Step 3.4: Build Frontend
```bash
# Development build
npm run dev

# Production build
npm run build
```

#### Step 3.5: Verify Pages Exist
```bash
# Check page files
dir app\gold-lending\audit-compliance\dashboard\page.tsx
dir app\gold-lending\audit-compliance\compliance\page.tsx
dir app\gold-lending\audit-compliance\audits\page.tsx
dir app\gold-lending\audit-compliance\reports\page.tsx
dir app\gold-lending\audit-compliance\certifications\page.tsx
dir app\gold-lending\audit-compliance\policies\page.tsx
```

#### Step 3.6: Start Frontend
```bash
# Development mode
npm run dev

# Production mode
npm run start
```

#### Step 3.7: Verify Frontend Access
```bash
# Open browser to:
# http://localhost:3000/gold-lending/audit-compliance/dashboard
```

---

### Phase 4: Integration Testing

#### Step 4.1: Test Audit Trail Creation
```bash
curl -X POST http://localhost:8013/api/v1/gold/audit-compliance/audit-trails \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "CREATE",
    "event_category": "loan_origination",
    "entity_type": "loan_application",
    "entity_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "123e4567-e89b-12d3-a456-426614174001",
    "action_status": "success",
    "event_data": {"amount": 50000}
  }'
```

#### Step 4.2: Test Compliance Rule Creation
```bash
curl -X POST http://localhost:8013/api/v1/gold/audit-compliance/compliance-rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_code": "LTV_001",
    "rule_name": "Maximum LTV Ratio",
    "rule_category": "lending",
    "rule_type": "threshold",
    "severity_level": "high",
    "rule_description": "LTV must not exceed 75%",
    "is_active": true
  }'
```

#### Step 4.3: Test Listing with Filters
```bash
# Test audit trail filtering
curl "http://localhost:8013/api/v1/gold/audit-compliance/audit-trails?event_type=CREATE&limit=10"

# Test compliance violation filtering
curl "http://localhost:8013/api/v1/gold/audit-compliance/compliance-violations?severity_level=high"
```

#### Step 4.4: Test Statistics Endpoints
```bash
# Audit trail statistics
curl http://localhost:8013/api/v1/gold/audit-compliance/statistics/audit-trails

# Compliance statistics
curl http://localhost:8013/api/v1/gold/audit-compliance/statistics/compliance
```

#### Step 4.5: Test Frontend Pages
- [ ] Navigate to dashboard: `/audit-compliance/dashboard`
- [ ] Verify metrics display
- [ ] Navigate to compliance: `/audit-compliance/compliance`
- [ ] Test filtering
- [ ] Navigate to audits: `/audit-compliance/audits`
- [ ] Test tabs
- [ ] Navigate to reports: `/audit-compliance/reports`
- [ ] Verify report list
- [ ] Navigate to certifications: `/audit-compliance/certifications`
- [ ] Check certification cards
- [ ] Navigate to policies: `/audit-compliance/policies`
- [ ] Verify acknowledgement list

---

### Phase 5: Post-Deployment Verification

#### Step 5.1: Database Verification
```sql
-- Check row counts
SELECT 
  (SELECT COUNT(*) FROM audit_trails) as audit_count,
  (SELECT COUNT(*) FROM compliance_rules) as rules_count,
  (SELECT COUNT(*) FROM compliance_violations) as violations_count;
```

#### Step 5.2: API Health Check
```bash
# Check all endpoints are responding
curl http://localhost:8013/api/v1/gold/audit-compliance/audit-trails
curl http://localhost:8013/api/v1/gold/audit-compliance/compliance-rules
curl http://localhost:8013/api/v1/gold/audit-compliance/compliance-violations
curl http://localhost:8013/api/v1/gold/audit-compliance/audit-schedules
curl http://localhost:8013/api/v1/gold/audit-compliance/audit-executions
curl http://localhost:8013/api/v1/gold/audit-compliance/audit-findings
curl http://localhost:8013/api/v1/gold/audit-compliance/regulatory-reports
curl http://localhost:8013/api/v1/gold/audit-compliance/compliance-certifications
curl http://localhost:8013/api/v1/gold/audit-compliance/policy-acknowledgements
curl http://localhost:8013/api/v1/gold/audit-compliance/data-retention-logs
```

#### Step 5.3: Performance Check
```bash
# Run load test (requires Apache Bench or similar)
ab -n 1000 -c 10 http://localhost:8013/api/v1/gold/audit-compliance/audit-trails
```

#### Step 5.4: Log Verification
```bash
# Check application logs
tail -f logs/app.log

# Check error logs
tail -f logs/error.log
```

---

## Configuration

### Environment Variables

Create/update `.env` file in `services/gold/`:

```env
# Database
DATABASE_URL=postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite

# API
API_V1_PREFIX=/api/v1/gold
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

Create/update `.env.local` in `apps/customer-app/`:

```env
# API Base URL
NEXT_PUBLIC_GOLD_API_URL=http://localhost:8013

# Feature Flags
NEXT_PUBLIC_AUDIT_COMPLIANCE_ENABLED=true
```

---

## Rollback Procedure

### If Database Issues:
```sql
-- Drop tables (in reverse order due to foreign keys)
DROP TABLE IF EXISTS data_retention_logs CASCADE;
DROP TABLE IF EXISTS policy_acknowledgements CASCADE;
DROP TABLE IF EXISTS compliance_certifications CASCADE;
DROP TABLE IF EXISTS regulatory_reports CASCADE;
DROP TABLE IF EXISTS audit_findings CASCADE;
DROP TABLE IF EXISTS audit_executions CASCADE;
DROP TABLE IF EXISTS audit_schedules CASCADE;
DROP TABLE IF EXISTS compliance_violations CASCADE;
DROP TABLE IF EXISTS compliance_rules CASCADE;
DROP TABLE IF EXISTS audit_trails CASCADE;

-- Drop views
DROP VIEW IF EXISTS vw_regulatory_report_summary CASCADE;
DROP VIEW IF EXISTS vw_audit_execution_summary CASCADE;
DROP VIEW IF EXISTS vw_compliance_violation_summary CASCADE;
DROP VIEW IF EXISTS vw_audit_trail_summary CASCADE;

-- Restore from backup
pg_restore -U nbfc_user -d nbfcsuite backup_file.dump
```

### If Backend Issues:
```bash
# Stop service
pkill -f "uvicorn app.main:app"

# Revert Git changes
git checkout HEAD~1 services/gold/

# Restart service
cd services/gold
uvicorn app.main:app --reload
```

### If Frontend Issues:
```bash
# Stop frontend
# Ctrl+C in terminal

# Revert changes
git checkout HEAD~1 apps/customer-app/

# Rebuild and restart
cd apps/customer-app
npm run build
npm run start
```

---

## Monitoring

### Key Metrics to Monitor

1. **API Response Times**
   - Audit trail queries: < 200ms
   - Statistics endpoints: < 500ms
   - List endpoints with filters: < 300ms

2. **Database Performance**
   - Query execution time: < 100ms
   - Index hit ratio: > 95%
   - Connection pool usage: < 80%

3. **Error Rates**
   - 4xx errors: < 1%
   - 5xx errors: < 0.1%
   - Database errors: 0

4. **System Resources**
   - CPU usage: < 70%
   - Memory usage: < 80%
   - Disk I/O: < 70%

### Alerts to Configure

- [ ] Critical violations created
- [ ] Regulatory reports overdue
- [ ] Certifications expiring soon
- [ ] API error rate spike
- [ ] Database connection failures
- [ ] High response times

---

## Support & Troubleshooting

### Common Issues

**Issue:** Tables not created
**Solution:** Check PostgreSQL logs, verify user permissions, re-run migration

**Issue:** API endpoints return 404
**Solution:** Verify router is registered in main.py, restart backend service

**Issue:** Frontend pages not loading
**Solution:** Check Next.js build output, verify routes exist, check console errors

**Issue:** Slow query performance
**Solution:** Run ANALYZE on tables, verify indexes are used, check query plans

---

## Post-Deployment Tasks

- [ ] Configure monitoring and alerts
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Update documentation
- [ ] Train users on new features
- [ ] Schedule user acceptance testing
- [ ] Plan for Phase 13 deployment

---

## Success Criteria

Deployment is successful when:
- ✅ All database tables created
- ✅ All API endpoints responding
- ✅ All frontend pages accessible
- ✅ Integration tests passing
- ✅ Performance metrics met
- ✅ No critical errors in logs
- ✅ Monitoring configured
- ✅ Backup procedures in place

---

**Deployment Guide Version:** 1.0  
**Last Updated:** July 3, 2026  
**Prepared By:** AI Development Team  
**Status:** READY FOR PRODUCTION DEPLOYMENT
