# Phase 13 - Integration Hub: Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying Phase 13 (Integration Hub) to production environments.

---

## Prerequisites

- PostgreSQL 14+ database
- Python 3.11+ with FastAPI
- Next.js 14+ application running
- Database migration tools
- Access to production environment

---

## Deployment Steps

### 1. Database Migration

#### Step 1.1: Backup Current Database
```bash
# Create backup before migration
pg_dump -U nbfc_user -d nbfcsuite > backup_before_phase13_$(date +%Y%m%d_%H%M%S).sql
```

#### Step 1.2: Run Phase 13 Migration
```bash
# Navigate to infra directory
cd infra/migrations

# Run migration script
psql -U nbfc_user -d nbfcsuite -f 030_integration_hub.sql

# Expected output:
# CREATE TABLE (8 tables)
# CREATE VIEW (4 views)
# CREATE TRIGGER (8 triggers)
# CREATE INDEX (80+ indexes)
```

#### Step 1.3: Verify Migration
```bash
# Check tables created
psql -U nbfc_user -d nbfcsuite -c "\dt integration_*"

# Should show:
# integration_providers
# integration_configurations
# integration_endpoints
# integration_logs
# api_keys
# webhooks
# webhook_deliveries
# message_queue

# Check views
psql -U nbfc_user -d nbfcsuite -c "\dv *integration*"

# Check indexes
psql -U nbfc_user -d nbfcsuite -c "\di integration_*"
```

### 2. Backend Deployment

#### Step 2.1: Update Dependencies
```bash
# No new dependencies required for Phase 13
# All dependencies already in requirements.txt
```

#### Step 2.2: Verify Backend Files
```bash
# Check files exist
ls -la services/gold/app/models/integration.py
ls -la services/gold/app/schemas/integration.py
ls -la services/gold/app/routers/integration.py

# Files are already integrated in main.py
# No manual registration needed
```

#### Step 2.3: Restart Backend Service
```bash
# Restart FastAPI service
supervisorctl restart gold-service

# Or if using systemd
systemctl restart gold-service

# Or if running directly
pkill -f "uvicorn.*gold"
uvicorn services.gold.app.main:app --reload
```

#### Step 2.4: Verify Backend Endpoints
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test integration endpoints
curl http://localhost:8000/api/v1/gold/integration/providers

# Should return: []  (empty array, no providers yet)
```

### 3. Frontend Deployment

#### Step 3.1: Build Frontend
```bash
# Navigate to customer app
cd apps/customer-app

# Install dependencies (if needed)
npm install

# Build production bundle
npm run build

# Expected output: Build successful
```

#### Step 3.2: Deploy Frontend
```bash
# If using PM2
pm2 restart customer-app

# If using Docker
docker-compose restart customer-app

# If using systemd
systemctl restart customer-app
```

#### Step 3.3: Verify Frontend
```bash
# Test dashboard page
curl http://localhost:3000/gold-lending/integration/dashboard

# Should return HTML page
```

---

## Configuration

### 1. Environment Variables

Add the following to your environment configuration:

```bash
# .env or environment config
DATABASE_URL=postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Integration-specific settings
INTEGRATION_TIMEOUT_SECONDS=30
WEBHOOK_RETRY_MAX_ATTEMPTS=5
MESSAGE_QUEUE_POLL_INTERVAL=10
API_KEY_ENCRYPTION_KEY=<your-encryption-key>
```

### 2. Initial Data Setup

#### Create Default Providers
```sql
-- Insert common integration providers
INSERT INTO integration_providers (
    provider_code, provider_name, category, description, 
    auth_type, is_active
) VALUES
('CORE_BANK', 'Core Banking System', 'core_banking', 'Main core banking integration', 'api_key', true),
('PAYMENT_GW', 'Payment Gateway', 'payment', 'Payment processing gateway', 'oauth2', true),
('SMS_GATEWAY', 'SMS Service', 'messaging', 'SMS notification service', 'api_key', true),
('EMAIL_SVC', 'Email Service', 'messaging', 'Email notification service', 'api_key', true);
```

---

## Testing

### 1. Backend API Tests

```bash
# Test Provider endpoints
curl -X POST http://localhost:8000/api/v1/gold/integration/providers \
  -H "Content-Type: application/json" \
  -d '{
    "provider_code": "TEST_PROVIDER",
    "provider_name": "Test Provider",
    "category": "test",
    "auth_type": "api_key",
    "is_active": true
  }'

# Test Configuration endpoints
curl -X POST http://localhost:8000/api/v1/gold/integration/configurations \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": 1,
    "config_name": "Test Config",
    "environment": "development",
    "base_url": "https://api.test.com",
    "auth_config": {},
    "timeout_seconds": 30,
    "retry_config": {"max_retries": 3},
    "status": "active",
    "created_by": 1
  }'

# Test Statistics endpoint
curl http://localhost:8000/api/v1/gold/integration/statistics/integration
```

### 2. Frontend Tests

```bash
# Navigate to dashboard
# Browser: http://localhost:3000/gold-lending/integration/dashboard

# Should display:
# - Total requests count
# - Average response time
# - Active configurations
# - Pending messages
# - Provider performance table
# - Webhook health metrics
# - Queue summary
```

### 3. Integration Tests

```bash
# Create provider, config, and test end-to-end flow

# 1. Create provider
PROVIDER_ID=$(curl -X POST http://localhost:8000/api/v1/gold/integration/providers \
  -H "Content-Type: application/json" \
  -d '{"provider_code":"E2E_TEST","provider_name":"E2E Test","category":"test","auth_type":"api_key","is_active":true}' \
  | jq -r '.provider_id')

# 2. Create configuration
CONFIG_ID=$(curl -X POST http://localhost:8000/api/v1/gold/integration/configurations \
  -H "Content-Type: application/json" \
  -d "{\"provider_id\":$PROVIDER_ID,\"config_name\":\"E2E Config\",\"environment\":\"test\",\"base_url\":\"https://test.com\",\"auth_config\":{},\"timeout_seconds\":30,\"retry_config\":{},\"status\":\"pending\",\"created_by\":1}" \
  | jq -r '.config_id')

# 3. Approve configuration
curl -X POST http://localhost:8000/api/v1/gold/integration/configurations/$CONFIG_ID/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by":2}'

# 4. Create API key
curl -X POST http://localhost:8000/api/v1/gold/integration/api-keys \
  -H "Content-Type: application/json" \
  -d "{\"config_id\":$CONFIG_ID,\"key_name\":\"E2E Key\",\"key_value\":\"test_key_123\",\"permissions\":{},\"is_active\":true,\"created_by\":1}"

# 5. Verify statistics
curl http://localhost:8000/api/v1/gold/integration/statistics/integration
```

---

## Monitoring

### 1. Database Monitoring

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'integration_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check integration activity
SELECT 
    COUNT(*) as total_logs,
    status,
    DATE(request_timestamp) as log_date
FROM integration_logs
GROUP BY status, DATE(request_timestamp)
ORDER BY log_date DESC;

-- Check webhook performance
SELECT * FROM webhook_performance_view;

-- Check queue status
SELECT * FROM queue_status_view;
```

### 2. Application Monitoring

```bash
# Check API endpoint response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/gold/integration/providers

# Monitor logs
tail -f /var/log/gold-service/integration.log

# Check error rates
grep "ERROR" /var/log/gold-service/integration.log | wc -l
```

### 3. Performance Metrics

```sql
-- Average response times by provider
SELECT 
    p.provider_name,
    COUNT(l.log_id) as total_calls,
    AVG(l.response_time) as avg_response_ms,
    MAX(l.response_time) as max_response_ms
FROM integration_logs l
JOIN integration_configurations c ON l.config_id = c.config_id
JOIN integration_providers p ON c.provider_id = p.provider_id
WHERE l.request_timestamp > NOW() - INTERVAL '1 day'
GROUP BY p.provider_name
ORDER BY avg_response_ms DESC;

-- Webhook delivery success rate
SELECT 
    COUNT(CASE WHEN status = 'success' THEN 1 END)::float / COUNT(*) * 100 as success_rate,
    AVG(response_time) as avg_response_ms
FROM webhook_deliveries
WHERE sent_at > NOW() - INTERVAL '1 day';
```

---

## Troubleshooting

### Issue 1: Migration Fails

**Problem:** Migration script fails with constraint errors

**Solution:**
```bash
# Check for existing tables
psql -U nbfc_user -d nbfcsuite -c "\dt integration_*"

# If tables exist, drop and recreate
psql -U nbfc_user -d nbfcsuite -c "DROP TABLE IF EXISTS integration_logs CASCADE"
# Repeat for all tables, then rerun migration
```

### Issue 2: Backend Won't Start

**Problem:** Import errors for integration module

**Solution:**
```bash
# Verify files exist
ls -la services/gold/app/models/integration.py
ls -la services/gold/app/schemas/integration.py
ls -la services/gold/app/routers/integration.py

# Check Python path
cd services/gold
python -c "from app.models import integration; print('OK')"

# Reinstall if needed
pip install -e .
```

### Issue 3: API Endpoints Return 404

**Problem:** Integration endpoints not found

**Solution:**
```bash
# Verify router is registered in main.py
grep "integration" services/gold/app/main.py

# Should see:
# from .routers import ... integration
# app.include_router(integration.router)

# Restart service
supervisorctl restart gold-service
```

### Issue 4: Frontend Dashboard Blank

**Problem:** Dashboard shows no data

**Solution:**
```bash
# Check API connectivity
curl http://localhost:8000/api/v1/gold/integration/statistics/integration

# Check browser console for errors
# Open DevTools -> Console

# Verify API base URL
grep NEXT_PUBLIC_API_URL .env.local
```

### Issue 5: Slow Performance

**Problem:** API endpoints slow to respond

**Solution:**
```sql
-- Check missing indexes
SELECT 
    schemaname || '.' || tablename AS table,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename LIKE 'integration_%';

-- Analyze tables
ANALYZE integration_providers;
ANALYZE integration_configurations;
ANALYZE integration_logs;

-- Check for long-running queries
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
AND query LIKE '%integration_%';
```

---

## Rollback Procedure

If deployment fails and rollback is required:

### 1. Restore Database
```bash
# Stop application
supervisorctl stop gold-service

# Restore from backup
psql -U nbfc_user -d nbfcsuite < backup_before_phase13_YYYYMMDD_HHMMSS.sql

# Restart application
supervisorctl start gold-service
```

### 2. Revert Code Changes
```bash
# Revert to previous commit
git log --oneline | head -20
git revert <commit-hash>

# Rebuild and restart
npm run build
pm2 restart customer-app
```

---

## Post-Deployment Checklist

- [ ] Database migration successful
- [ ] All tables created
- [ ] All views created
- [ ] All triggers active
- [ ] All indexes created
- [ ] Backend service restarted
- [ ] API endpoints responding
- [ ] Frontend deployed
- [ ] Dashboard accessible
- [ ] Initial providers created
- [ ] Test integration created
- [ ] Monitoring configured
- [ ] Logs being generated
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] Team notified

---

## Security Considerations

### 1. API Key Encryption

```python
# Implement encryption for API keys
from cryptography.fernet import Fernet

# Generate key (do this once, store securely)
encryption_key = Fernet.generate_key()

# Encrypt API keys before storage
cipher_suite = Fernet(encryption_key)
encrypted_key = cipher_suite.encrypt(api_key.encode())

# Decrypt when needed
decrypted_key = cipher_suite.decrypt(encrypted_key).decode()
```

### 2. Access Control

```sql
-- Grant minimal permissions
GRANT SELECT, INSERT, UPDATE ON integration_providers TO app_user;
GRANT SELECT, INSERT ON integration_logs TO app_user;

-- Revoke DELETE on sensitive tables
REVOKE DELETE ON api_keys FROM app_user;
```

### 3. Rate Limiting

```python
# Implement rate limiting in router
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@router.get("/providers", dependencies=[Depends(RateLimiter(times=100, seconds=60))])
async def get_providers():
    # Rate limited to 100 requests per minute
    pass
```

---

## Maintenance

### Daily Tasks
- Monitor error logs
- Check webhook delivery success rate
- Review queue status
- Check API response times

### Weekly Tasks
- Review integration statistics
- Analyze provider performance
- Clean up old logs (>90 days)
- Rotate API keys as needed

### Monthly Tasks
- Review and update configurations
- Audit API key usage
- Optimize database indexes
- Update documentation

---

## Support

For issues or questions:
- **Technical Lead:** Phase 13 Integration Team
- **Documentation:** See PHASE13_COMPLETION_REPORT.md
- **API Reference:** /api/docs (Swagger UI)

---

**Last Updated:** July 3, 2026  
**Version:** 1.0  
**Phase:** 13 - Integration Hub
