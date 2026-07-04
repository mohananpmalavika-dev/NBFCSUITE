# Phase 5 Deployment Checklist
## Vault & Packet Management System - Go-Live Readiness

**Phase**: 5 of 15  
**Status**: Ready for Deployment  
**Date**: July 3, 2026

---

## ✅ Pre-Deployment Checklist

### 1. Database Setup
- [ ] PostgreSQL 14+ installed and running
- [ ] Database `nbfc_gold_lending` created
- [ ] Migration 018 executed (Product Configuration)
- [ ] Migration 019 executed (Customer Journey)
- [ ] Migration 020 executed (Appraisal Engine)
- [ ] Migration 021 executed (Ornament Catalog)
- [ ] Migration 022 executed (Vault & Packet Management)
- [ ] All 46+ tables created successfully
- [ ] 2 database views created successfully
- [ ] Database indexes verified
- [ ] Foreign key constraints verified

**Verification Commands:**
```bash
# Check tables exist
psql -U postgres -d nbfc_gold_lending -c "\dt gold_*"

# Check views exist
psql -U postgres -d nbfc_gold_lending -c "\dv"

# Verify vault tables specifically
psql -U postgres -d nbfc_gold_lending -c "SELECT COUNT(*) FROM gold_vaults"
psql -U postgres -d nbfc_gold_lending -c "SELECT COUNT(*) FROM gold_packets"
```

---

### 2. Backend Setup
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed (`requirements.txt`)
- [ ] QR code library installed (`qrcode[pil]`)
- [ ] PIL/Pillow installed for image processing
- [ ] Database connection configured
- [ ] Environment variables set
- [ ] Service starts without errors
- [ ] API documentation accessible at `/docs`
- [ ] Health check endpoint responding

**Verification Commands:**
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep fastapi
pip list | grep sqlalchemy
pip list | grep qrcode
pip list | grep Pillow

# Start service
cd services/gold
uvicorn app.main:app --reload --port 8003

# Test API
curl http://localhost:8003/docs
curl http://localhost:8003/health
```

---

### 3. Frontend Setup
- [ ] Node.js 18+ installed
- [ ] npm dependencies installed
- [ ] Environment variables configured
- [ ] API base URL configured
- [ ] Frontend builds successfully
- [ ] Frontend starts without errors
- [ ] All 12 pages accessible
- [ ] Navigation works correctly
- [ ] API client methods tested

**Verification Commands:**
```bash
# Check Node version
node --version  # Should be 18+

# Install and start
cd apps/customer-app
npm install
npm run dev

# Access pages
# http://localhost:3000/gold-lending/vault
# http://localhost:3000/gold-lending/vault/packets
# http://localhost:3000/gold-lending/vault/audits
```

---

### 4. Phase 5 Specific Checks

#### Vault Management
- [ ] Can create vault via API
- [ ] QR code generated for vault
- [ ] Can create rack in vault
- [ ] Can create locker in rack
- [ ] Can create tray in locker
- [ ] Hierarchy displays correctly
- [ ] Vault listing page loads
- [ ] Vault detail page loads with 6 tabs

**Test Script:**
```bash
# Create vault
VAULT_ID=$(curl -X POST http://localhost:8003/api/v1/gold/vaults \
  -H "Content-Type: application/json" \
  -d '{
    "vault_code": "VLT-TEST-001",
    "vault_name": "Test Vault",
    "location": "Test Location",
    "vault_type": "high_security",
    "capacity_racks": 20,
    "security_level": "high_security",
    "manager_id": "550e8400-e29b-41d4-a716-446655440000"
  }' | jq -r '.id')

echo "Created Vault ID: $VAULT_ID"

# Verify QR code exists
curl http://localhost:8003/api/v1/gold/vaults/$VAULT_ID | jq '.qr_code'
```

#### Packet Management
- [ ] Can create packet via API
- [ ] QR code generated for packet
- [ ] Can add ornament to packet
- [ ] Can seal packet
- [ ] Packet totals calculate correctly
- [ ] Packet listing page loads
- [ ] Packet detail page loads with 5 tabs
- [ ] QR code displays and downloads

**Test Script:**
```bash
# Create packet
PACKET_ID=$(curl -X POST http://localhost:8003/api/v1/gold/packets \
  -H "Content-Type: application/json" \
  -d '{
    "packet_number": "PKT-TEST-001",
    "vault_id": "'$VAULT_ID'",
    "current_location": "VLT-TEST-001/R01/L01/T01"
  }' | jq -r '.id')

echo "Created Packet ID: $PACKET_ID"

# Verify QR code exists
curl http://localhost:8003/api/v1/gold/packets/$PACKET_ID | jq '.qr_code'
```

#### Security Seals
- [ ] Can apply seal to packet
- [ ] Seal status tracked correctly
- [ ] Can verify seal
- [ ] Can break seal with reason
- [ ] Seal lifecycle logged
- [ ] Seal management page loads

**Test Script:**
```bash
# Seal packet
curl -X POST http://localhost:8003/api/v1/gold/packets/$PACKET_ID/seal \
  -H "Content-Type: application/json" \
  -d '{
    "seal_number": "SEAL-TEST-001",
    "seal_type": "tamper_evident",
    "sealed_by": "550e8400-e29b-41d4-a716-446655440000"
  }'

# Verify seal applied
curl http://localhost:8003/api/v1/gold/packets/$PACKET_ID | jq '.seal_number'
```

#### Movement Tracking
- [ ] Can record packet movement
- [ ] GPS coordinates stored
- [ ] Movement reason documented
- [ ] Movement history displays
- [ ] Movement types validated

**Test Script:**
```bash
# Record movement
curl -X POST http://localhost:8003/api/v1/gold/packets/$PACKET_ID/movements \
  -H "Content-Type: application/json" \
  -d '{
    "movement_type": "storage",
    "to_location": "VLT-TEST-001/R01/L01/T01",
    "reason": "Initial storage test",
    "gps_coordinates": "19.0760,72.8777",
    "notes": "Test movement"
  }'

# Verify movement recorded
curl http://localhost:8003/api/v1/gold/packets/$PACKET_ID/movements
```

#### Vault Audits
- [ ] Can schedule vault audit
- [ ] Can add audit findings
- [ ] Findings categorized by severity
- [ ] Compliance score calculated
- [ ] Audit management page loads

**Test Script:**
```bash
# Schedule audit
AUDIT_ID=$(curl -X POST http://localhost:8003/api/v1/gold/vaults/$VAULT_ID/audits \
  -H "Content-Type: application/json" \
  -d '{
    "audit_type": "routine",
    "scheduled_date": "2024-12-31",
    "auditor_id": "550e8400-e29b-41d4-a716-446655440000",
    "notes": "Test audit"
  }' | jq -r '.id')

echo "Created Audit ID: $AUDIT_ID"
```

---

### 5. Integration Testing

#### Phase 3 → Phase 5 Integration
- [ ] Can create packet after appraisal
- [ ] Can add appraised ornament to packet
- [ ] Ornament status updates correctly
- [ ] Packet value reflects ornament value

#### Phase 4 → Phase 5 Integration
- [ ] Ornament profile shows packet assignment
- [ ] Ornament profile shows vault location
- [ ] Movement history syncs between catalog and vault
- [ ] GPS tracking consistent

---

### 6. Documentation Verification
- [ ] PHASE5_VAULT_PACKET_MANAGEMENT.md exists and complete
- [ ] GETTING_STARTED_PHASE5.md exists and tested
- [ ] PHASE5_COMPLETION_REPORT.md created
- [ ] PHASE5_FINAL_SUMMARY.md created
- [ ] Platform summary updated with Phase 5
- [ ] Executive summary updated with Phase 5
- [ ] Roadmap updated
- [ ] Master index updated
- [ ] Service README updated

**File Checklist:**
```bash
# Verify documentation files exist
ls -la services/gold/PHASE5_*.md
ls -la services/gold/GETTING_STARTED_PHASE5.md
ls -la PHASE5_*.md
ls -la GOLD_LENDING_*.md
```

---

### 7. Performance Testing
- [ ] API response time < 100ms (average)
- [ ] QR code generation < 50ms
- [ ] Hierarchy query < 200ms
- [ ] Inventory view query < 300ms
- [ ] Can handle 50+ concurrent requests
- [ ] Database connection pool configured
- [ ] No memory leaks detected

**Performance Test:**
```bash
# Simple load test
ab -n 1000 -c 10 http://localhost:8003/api/v1/gold/vaults

# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8003/api/v1/gold/vaults
```

---

### 8. Security Verification
- [ ] SQL injection prevention (using ORM)
- [ ] Input validation (Pydantic)
- [ ] Audit logging enabled
- [ ] User tracking in place
- [ ] GPS coordinates validated
- [ ] QR codes secure (no sensitive data)
- [ ] Seal tampering detectable

---

### 9. User Acceptance Testing (UAT)
- [ ] Operations staff can navigate UI
- [ ] Vault creation workflow clear
- [ ] Packet management intuitive
- [ ] QR codes scannable
- [ ] Movement recording straightforward
- [ ] Audit scheduling understandable
- [ ] Error messages helpful

---

## 🚀 Deployment Steps

### Step 1: Backup (Critical!)
```bash
# Backup current database
pg_dump -U postgres nbfc_gold_lending > backup_before_phase5.sql

# Backup current code
git tag phase4-complete
git commit -am "Phase 5 deployment backup"
```

### Step 2: Deploy Database Changes
```bash
# Run Phase 5 migration
psql -U postgres -d nbfc_gold_lending -f infra/migrations/022_vault_packet_management.sql

# Verify migration
psql -U postgres -d nbfc_gold_lending -c "\dt gold_vault*"
psql -U postgres -d nbfc_gold_lending -c "\dt gold_packet*"
```

### Step 3: Deploy Backend
```bash
# Install new dependencies
cd services/gold
pip install qrcode[pil]

# Restart service
# If using systemd:
sudo systemctl restart gold-lending-service

# If using docker:
docker-compose restart gold-service

# If manual:
pkill -f "uvicorn app.main"
uvicorn app.main:app --reload --port 8003 &
```

### Step 4: Deploy Frontend
```bash
# Build frontend
cd apps/customer-app
npm run build

# Deploy (method depends on hosting)
npm start
# Or copy build to web server
```

### Step 5: Smoke Tests
```bash
# Test vault creation
curl -X POST http://localhost:8003/api/v1/gold/vaults \
  -H "Content-Type: application/json" \
  -d '{"vault_code":"VLT-SMOKE-001","vault_name":"Smoke Test"}'

# Test frontend
curl http://localhost:3000/gold-lending/vault
```

### Step 6: Create Seed Data
```bash
# Create first vault
# Create first packet
# Link to existing ornament
# Verify end-to-end flow
```

---

## 📊 Post-Deployment Verification

### Immediate (First Hour)
- [ ] All API endpoints responding
- [ ] No 500 errors in logs
- [ ] Frontend pages loading
- [ ] QR codes generating
- [ ] Database queries performing well

### First Day
- [ ] Operations staff trained
- [ ] First real vault created
- [ ] First real packet created
- [ ] First ornament linked to packet
- [ ] No critical issues reported

### First Week
- [ ] 10+ vaults created
- [ ] 50+ packets created
- [ ] GPS tracking working
- [ ] Seal management in use
- [ ] First audit completed
- [ ] User feedback collected

---

## 🐛 Rollback Plan (If Needed)

### Quick Rollback
```bash
# 1. Restore database backup
psql -U postgres -d nbfc_gold_lending < backup_before_phase5.sql

# 2. Revert code
git reset --hard phase4-complete

# 3. Restart services
sudo systemctl restart gold-lending-service
```

### Partial Rollback
```bash
# If only database needs rollback:
psql -U postgres -d nbfc_gold_lending -c "
  DROP TABLE IF EXISTS gold_security_seals CASCADE;
  DROP TABLE IF EXISTS gold_vault_access_log CASCADE;
  DROP TABLE IF EXISTS gold_audit_findings CASCADE;
  DROP TABLE IF EXISTS gold_vault_audits CASCADE;
  DROP TABLE IF EXISTS gold_packet_movements CASCADE;
  DROP TABLE IF EXISTS gold_packet_ornaments CASCADE;
  DROP TABLE IF EXISTS gold_packets CASCADE;
  DROP TABLE IF EXISTS gold_vault_trays CASCADE;
  DROP TABLE IF EXISTS gold_vault_lockers CASCADE;
  DROP TABLE IF EXISTS gold_vault_racks CASCADE;
  DROP TABLE IF EXISTS gold_vaults CASCADE;
  DROP VIEW IF EXISTS vault_inventory_summary;
  DROP VIEW IF EXISTS packet_location_view;
"
```

---

## 📞 Support Contacts

### During Deployment
- **Technical Lead**: Available for technical issues
- **DBA**: Database support
- **DevOps**: Infrastructure support
- **QA Lead**: Testing support

### Post-Deployment
- **Support Team**: User issues and questions
- **Operations Lead**: Process guidance
- **Training Team**: Staff onboarding

---

## 📈 Success Metrics

### Technical Metrics
- [ ] API uptime > 99.9%
- [ ] Response time < 100ms average
- [ ] Zero critical bugs
- [ ] Database performance optimal

### Business Metrics
- [ ] 10+ vaults created in first week
- [ ] 100+ packets created in first month
- [ ] Packet retrieval time < 10 seconds
- [ ] Location accuracy > 99%
- [ ] User satisfaction > 90%

---

## 🎯 Go/No-Go Decision

### Go Criteria (All Must Be TRUE)
- ✅ All database tables created successfully
- ✅ All API endpoints tested and working
- ✅ All frontend pages accessible
- ✅ QR code generation working
- ✅ GPS tracking functional
- ✅ Security seal management operational
- ✅ Documentation complete
- ✅ Backup taken
- ✅ Rollback plan tested
- ✅ Support team ready

### No-Go Criteria (Any One TRUE = STOP)
- ❌ Critical bugs in core functionality
- ❌ Database migration failures
- ❌ API endpoints returning errors
- ❌ Frontend pages not loading
- ❌ QR codes not generating
- ❌ Performance issues detected
- ❌ Security vulnerabilities found
- ❌ No rollback plan
- ❌ Support team not ready

---

## ✅ Final Sign-Off

### Technical Team
- [ ] Technical Lead approves deployment
- [ ] Database Admin confirms migration
- [ ] QA Lead confirms testing complete
- [ ] DevOps confirms infrastructure ready

### Business Team
- [ ] Product Owner approves features
- [ ] Operations Manager confirms readiness
- [ ] Training Lead confirms staff trained
- [ ] Compliance Officer confirms audit trail

### Deployment Authorization
- [ ] All checks complete
- [ ] All sign-offs obtained
- [ ] Deployment window scheduled
- [ ] Communication sent to stakeholders

**Deployment Date**: _______________  
**Deployment Time**: _______________  
**Deployed By**: _______________  
**Approved By**: _______________

---

## 🎉 Deployment Complete!

Once deployed:
1. Monitor logs for first hour
2. Conduct smoke tests
3. Train operations staff
4. Gather user feedback
5. Document any issues
6. Plan Phase 6 kickoff

**Next Phase**: Loan Origination & Disbursement (Phase 6)

---

**Checklist Version**: 1.0  
**Phase**: 5 of 15 (33% Complete)  
**Status**: Ready for Deployment  
**Confidence**: Very High

---

*Phase 5 Deployment Checklist*  
*Enterprise Gold Lending Platform - NBFCSuite*  
*July 3, 2026*
