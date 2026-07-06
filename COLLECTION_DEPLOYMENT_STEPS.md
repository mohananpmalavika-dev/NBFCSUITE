# Collection Management System - Deployment Steps

## 📋 Overview

This document provides step-by-step instructions to deploy the Collection Management System to production.

**Status**: Frontend Complete, Backend API Routers Pending  
**Estimated Deployment Time**: 3-4 weeks  
**Risk Level**: Medium (integration work required)

---

## 🎯 Deployment Checklist

### Phase 1: Backend API Development ⏳ (2 weeks)
- [ ] Create 5 API router files
- [ ] Implement all CRUD endpoints
- [ ] Add authentication/authorization
- [ ] Create database migration script
- [ ] Test endpoints with Postman
- [ ] Document APIs with Swagger

### Phase 2: Integration ⏳ (1 week)
- [ ] Register routers in main.py
- [ ] Run database migration
- [ ] Update frontend navigation
- [ ] Configure API client
- [ ] Test end-to-end workflows
- [ ] Fix integration issues

### Phase 3: Testing & QA ⏳ (1 week)
- [ ] Unit testing
- [ ] Integration testing
- [ ] User acceptance testing
- [ ] Performance testing
- [ ] Security testing
- [ ] Bug fixes


### Phase 4: Production Deployment ⏳ (3 days)
- [ ] Deploy to staging
- [ ] Smoke testing
- [ ] Production deployment
- [ ] Post-deployment verification
- [ ] Monitor for issues

---

## 📦 Step-by-Step Deployment Guide

## PHASE 1: Backend API Development (Days 1-10)

### Step 1.1: Create Collection Strategy Router
**Time**: 2 days  
**File**: `backend/services/collection/strategy_router.py`

**Tasks**:
```python
# 1. Create router file
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .strategy_service import CollectionStrategyService
from .schemas import (
    StrategyCreate, StrategyUpdate, StrategyResponse,
    StrategyExecutionRequest, StrategyExecutionResponse
)
from ..auth.dependencies import get_current_user, get_db

router = APIRouter(
    prefix="/api/v1/collection/strategies",
    tags=["collection-strategies"]
)

# 2. Implement endpoints
@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    data: StrategyCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CollectionStrategyService(db)
    return service.create_strategy(data, current_user.id)

@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    active: bool = None,
    product_type: str = None,
    db: Session = Depends(get_db)
):
    service = CollectionStrategyService(db)
    return service.get_strategies(active=active, product_type=product_type)

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    db: Session = Depends(get_db)
):
    service = CollectionStrategyService(db)
    strategy = service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: str,
    data: StrategyUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CollectionStrategyService(db)
    return service.update_strategy(strategy_id, data, current_user.id)

@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CollectionStrategyService(db)
    service.delete_strategy(strategy_id)
    return {"message": "Strategy deleted successfully"}

@router.post("/{strategy_id}/execute", response_model=StrategyExecutionResponse)
async def execute_strategy(
    strategy_id: str,
    data: StrategyExecutionRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CollectionStrategyService(db)
    return service.execute_strategy(strategy_id, data, current_user.id)
```

**Testing**:
```bash
# Test with curl
curl -X POST http://localhost:8000/api/v1/collection/strategies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Strategy", "min_dpd": 0, "max_dpd": 30}'

curl http://localhost:8000/api/v1/collection/strategies
```


### Step 1.2: Create Field Agent Router
**Time**: 2 days  
**File**: `backend/services/collection/field_agent_router.py`

**Similar structure, key endpoints**:
- POST `/field-agents` - Create agent
- GET `/field-agents` - List agents
- GET `/field-agents/{id}` - Get agent
- PUT `/field-agents/{id}` - Update agent
- POST `/field-agents/{id}/territories` - Assign territory
- POST `/field-agents/{id}/cases` - Assign cases
- POST `/visits` - Create visit
- GET `/visits` - List visits
- PUT `/visits/{id}` - Update visit

### Step 1.3: Create Promise Router
**Time**: 1.5 days  
**File**: `backend/services/collection/promise_router.py`

**Key endpoints**:
- POST `/promises` - Create promise
- GET `/promises` - List promises
- GET `/promises/{id}` - Get promise
- POST `/promises/{id}/fulfill` - Mark fulfilled
- POST `/promises/{id}/break` - Mark broken
- POST `/promises/{id}/reschedule` - Reschedule

### Step 1.4: Create Legal Router
**Time**: 2 days  
**File**: `backend/services/collection/legal_router.py`

**Key endpoints**:
- POST `/legal/notices` - Create notice
- GET `/legal/notices` - List notices
- GET `/legal/notices/{id}` - Get notice
- PUT `/legal/notices/{id}/delivery` - Update delivery
- POST `/legal/cases` - Create case
- GET `/legal/cases` - List cases
- GET `/legal/cases/{id}` - Get case
- POST `/legal/cases/{id}/hearings` - Add hearing


### Step 1.5: Create Settlement Router
**Time**: 1.5 days  
**File**: `backend/services/collection/settlement_router.py`

**Key endpoints**:
- POST `/settlement/proposals` - Create proposal
- GET `/settlement/proposals` - List proposals
- GET `/settlement/proposals/{id}` - Get proposal
- POST `/settlement/proposals/{id}/approve` - Approve
- POST `/settlement/proposals/{id}/reject` - Reject
- POST `/settlement/proposals/{id}/payments` - Record payment

### Step 1.6: Create Database Migration
**Time**: 1 day  
**File**: `backend/alembic/versions/008_add_collection_tables.py`

**Commands**:
```bash
# Generate migration
cd backend
alembic revision --autogenerate -m "Add collection management tables"

# Review generated migration file
# Edit if needed

# Test migration
alembic upgrade head

# Test rollback
alembic downgrade -1

# Re-apply
alembic upgrade head
```

**Verify tables created**:
```sql
-- Check tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'collection_%';

-- Expected tables:
-- collection_strategies
-- collection_strategy_actions
-- collection_strategy_executions
-- collection_field_agents
-- collection_territories
-- collection_agent_territories
-- collection_visits
-- collection_payment_promises
-- collection_promise_follow_ups
-- collection_legal_notices
-- collection_legal_cases
-- collection_case_hearings
-- collection_settlement_proposals
-- collection_settlement_payments
-- collection_templates
```


### Step 1.7: Register Routers in Main App
**Time**: 0.5 days  
**File**: `backend/main.py`

**Changes**:
```python
# Add imports
from services.collection.strategy_router import router as strategy_router
from services.collection.field_agent_router import router as field_agent_router
from services.collection.promise_router import router as promise_router
from services.collection.legal_router import router as legal_router
from services.collection.settlement_router import router as settlement_router

# Register routers
app.include_router(strategy_router)
app.include_router(field_agent_router)
app.include_router(promise_router)
app.include_router(legal_router)
app.include_router(settlement_router)
```

**Test server startup**:
```bash
cd backend
uvicorn main:app --reload

# Check OpenAPI docs
# Open: http://localhost:8000/docs
# Verify all collection endpoints are listed
```

---

## PHASE 2: Frontend Integration (Days 11-15)

### Step 2.1: Update Navigation Menu
**Time**: 0.5 days  
**File**: `frontend/apps/admin-portal/src/components/navigation/sidebar.tsx` (or similar)

**Add Collection Menu**:
```typescript
{
  title: "Collections",
  icon: CollectionIcon, // or "💰"
  href: "/collections",
  children: [
    { title: "Dashboard", href: "/collections" },
    { title: "Strategies", href: "/collections/strategies" },
    { title: "Field Agents", href: "/collections/field-agents" },
    { title: "Promises", href: "/collections/promises" },
    { title: "Legal & Recovery", href: "/collections/legal" },
    { title: "Settlement/OTS", href: "/collections/settlement" },
    { title: "Templates", href: "/collections/templates" },
  ]
}
```


### Step 2.2: Configure API Client
**Time**: 0.5 days  
**File**: `frontend/apps/admin-portal/src/lib/api/client.ts`

**Create/Update API client configuration**:
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

**Update collection API to use client**:
```typescript
// frontend/apps/admin-portal/src/lib/api/collection.ts
import apiClient from './client';

export const collectionApi = {
  async createStrategy(data: any) {
    const response = await apiClient.post('/api/v1/collection/strategies', data);
    return response.data;
  },
  // ... rest of the functions
};
```


### Step 2.3: Environment Configuration
**Time**: 0.5 days  

**Backend - Update .env**:
```bash
# backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/nbfc_db
JWT_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000,https://your-domain.com

# SMS Gateway
SMS_GATEWAY_URL=https://sms-provider.com/api
SMS_API_KEY=your-sms-api-key

# Email Service
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Collection Settings
COLLECTION_AUTO_EXECUTE=true
COLLECTION_REMINDER_DAYS=3,1
MAX_CASES_PER_AGENT=50
```

**Frontend - Update .env.local**:
```bash
# frontend/apps/admin-portal/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=NBFC Collection System
NEXT_PUBLIC_SUPPORT_EMAIL=support@nbfc.com
```

### Step 2.4: Test End-to-End Workflows
**Time**: 2 days

**Test Case 1: Collection Strategy Creation**
```
1. Login to admin portal
2. Navigate to /collections/strategies
3. Click "New Strategy"
4. Fill form:
   - Name: Test Strategy
   - DPD Range: 0-30
   - Product: Personal Loan
5. Add SMS action on Day 1
6. Save strategy
7. Verify saved in database
8. Execute strategy
9. Verify loans matched and actions created
```

**Test Case 2: Field Agent Assignment**
```
1. Navigate to /collections/field-agents
2. Create new agent
3. Assign territory with pincodes
4. Assign 5 test cases
5. Verify agent can see cases
6. Record a test visit
7. Check visit saved correctly
```


**Test Case 3: Promise Tracking**
```
1. Navigate to /collections/promises
2. Create new promise (₹50,000, due in 3 days)
3. Wait for due date alert
4. Mark as fulfilled
5. Verify status updated
6. Check analytics updated
```

**Test Case 4: Legal Notice Generation**
```
1. Navigate to /collections/legal
2. Create demand notice
3. Select template
4. Fill customer details
5. Generate PDF
6. Send notice
7. Track delivery status
```

**Test Case 5: Settlement Workflow**
```
1. Navigate to /collections/settlement
2. Create new proposal
3. Fill outstanding: ₹7,00,000
4. Set settlement: ₹5,50,000
5. Calculate NPV
6. Submit for approval
7. Login as approver
8. Review and approve
9. Record payment
10. Mark complete
```

### Step 2.5: Fix Integration Issues
**Time**: 2 days

**Common issues to check**:
- CORS errors - Update CORS settings in backend
- Authentication failures - Verify JWT token flow
- API endpoint mismatches - Check route paths
- Data format issues - Verify request/response schemas
- Null pointer errors - Add proper error handling
- Loading states - Ensure proper loading indicators

---

## PHASE 3: Testing & QA (Days 16-20)

### Step 3.1: Unit Testing - Backend
**Time**: 2 days

**Test services**:
```python
# tests/test_collection_strategy_service.py
import pytest
from services.collection.strategy_service import CollectionStrategyService

def test_create_strategy(db_session):
    service = CollectionStrategyService(db_session)
    data = {
        "name": "Test Strategy",
        "min_dpd": 0,
        "max_dpd": 30,
        "priority": 5
    }
    result = service.create_strategy(data, "user123")
    assert result.id is not None
    assert result.name == "Test Strategy"

def test_execute_strategy(db_session):
    service = CollectionStrategyService(db_session)
    # Test strategy execution logic
    pass
```

**Run tests**:
```bash
cd backend
pytest tests/test_collection* -v
```


### Step 3.2: Integration Testing
**Time**: 2 days

**Test API endpoints**:
```python
# tests/test_collection_api.py
from fastapi.testclient import TestClient

def test_create_strategy_endpoint(client: TestClient, auth_headers):
    response = client.post(
        "/api/v1/collection/strategies",
        json={
            "name": "API Test Strategy",
            "min_dpd": 0,
            "max_dpd": 30
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "API Test Strategy"

def test_get_strategies(client: TestClient, auth_headers):
    response = client.get(
        "/api/v1/collection/strategies",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Step 3.3: User Acceptance Testing (UAT)
**Time**: 2 days

**UAT Test Plan**:
```
Module: Collection Strategies
Tester: Collection Manager
Date: [Date]

Test Cases:
☐ Create strategy with multiple actions
☐ Edit existing strategy
☐ Delete inactive strategy
☐ Execute strategy on test portfolio
☐ View execution results
☐ Check action logs

Status: Pass/Fail
Issues: [List any issues]
```

**UAT for each module**:
- Collection Strategies (5 test cases)
- Field Agents (8 test cases)
- Payment Promises (6 test cases)
- Legal & Recovery (10 test cases)
- Settlement/OTS (7 test cases)
- Templates (4 test cases)


### Step 3.4: Performance Testing
**Time**: 1 day

**Load Testing**:
```bash
# Install k6 or locust
pip install locust

# Create load test script
# locustfile.py
from locust import HttpUser, task, between

class CollectionUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_strategies(self):
        self.client.get("/api/v1/collection/strategies")
    
    @task
    def create_promise(self):
        self.client.post("/api/v1/collection/promises", json={
            "loan_account_id": "LA-2024-001",
            "promised_amount": 50000,
            "promise_date": "2024-02-01"
        })

# Run test
locust -f locustfile.py --host=http://localhost:8000
```

**Performance Metrics**:
- Response time: <500ms for 95% requests
- Throughput: 100 requests/second
- Error rate: <1%
- Database queries: <10 per request

### Step 3.5: Security Testing
**Time**: 1 day

**Security Checklist**:
```
☐ SQL Injection - Test with malicious inputs
☐ XSS - Test form inputs and outputs
☐ CSRF - Verify CSRF tokens
☐ Authentication - Test unauthorized access
☐ Authorization - Test role-based access
☐ Data Encryption - Verify sensitive data encrypted
☐ API Rate Limiting - Test API abuse prevention
☐ Input Validation - Test invalid data handling
```

**Tools**:
- OWASP ZAP for vulnerability scanning
- Burp Suite for penetration testing
- Security headers checker

---

## PHASE 4: Production Deployment (Days 21-23)

### Step 4.1: Staging Deployment
**Time**: 1 day

**Deploy Backend to Staging**:
```bash
# 1. Build Docker image
cd backend
docker build -t nbfc-collection-api:staging .

# 2. Push to registry
docker push your-registry/nbfc-collection-api:staging

# 3. Deploy to staging server
ssh staging-server
docker pull your-registry/nbfc-collection-api:staging
docker-compose up -d

# 4. Run migrations
docker exec nbfc-api alembic upgrade head

# 5. Verify services
curl http://staging-api.nbfc.com/health
```


**Deploy Frontend to Staging**:
```bash
# 1. Build frontend
cd frontend/apps/admin-portal
npm run build

# 2. Deploy to staging
# Option A: Vercel
vercel --prod --env staging

# Option B: Docker
docker build -t nbfc-collection-frontend:staging .
docker push your-registry/nbfc-collection-frontend:staging

# 3. Verify deployment
curl https://staging.nbfc.com/collections
```

### Step 4.2: Smoke Testing on Staging
**Time**: 0.5 days

**Smoke Test Checklist**:
```
☐ Can login to application
☐ Collection menu visible
☐ Can create new strategy
☐ Can view field agents
☐ Can create promise
☐ Can access legal module
☐ Can create settlement proposal
☐ API responses within acceptable time
☐ No console errors
☐ No 500 errors in logs
```

### Step 4.3: Production Deployment
**Time**: 0.5 days

**Pre-deployment Checklist**:
```
☐ All tests passing
☐ Staging validated
☐ Database backup taken
☐ Rollback plan ready
☐ Monitoring setup
☐ Alert system configured
☐ Support team notified
☐ Deployment window scheduled
```

**Production Deployment Steps**:
```bash
# 1. Maintenance mode (optional)
# Display maintenance page to users

# 2. Backup database
pg_dump -h prod-db -U user nbfc_db > backup_$(date +%Y%m%d).sql

# 3. Deploy backend
docker pull your-registry/nbfc-collection-api:prod
docker-compose down
docker-compose up -d

# 4. Run migrations
docker exec nbfc-api alembic upgrade head

# 5. Deploy frontend
cd frontend/apps/admin-portal
npm run build
npm run deploy:prod

# 6. Verify deployment
curl https://api.nbfc.com/health
curl https://app.nbfc.com/collections

# 7. Exit maintenance mode
# Remove maintenance page

# 8. Monitor logs
docker logs -f nbfc-api
```


### Step 4.4: Post-Deployment Verification
**Time**: 1 day

**Verification Steps**:
```
1. Health Check
   ☐ API health endpoint responding
   ☐ Frontend loading correctly
   ☐ Database connections working

2. Functionality Check
   ☐ Can login
   ☐ Can create strategy
   ☐ Can assign field agent
   ☐ Can record promise
   ☐ Can generate legal notice
   ☐ Can create settlement

3. Integration Check
   ☐ SMS gateway working
   ☐ Email service working
   ☐ Payment gateway working (if applicable)
   ☐ External APIs responding

4. Performance Check
   ☐ Page load time <3 seconds
   ☐ API response time <500ms
   ☐ No memory leaks
   ☐ CPU usage normal

5. Monitoring Check
   ☐ Application logs flowing
   ☐ Error tracking active
   ☐ Alerts configured
   ☐ Dashboards showing data
```

---

## 🔍 Monitoring & Maintenance

### Application Monitoring

**Setup Monitoring Tools**:
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

**Key Metrics to Monitor**:
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx errors)
- Database connection pool
- Memory usage
- CPU usage
- Disk space

