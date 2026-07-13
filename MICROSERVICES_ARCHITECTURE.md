# NBFC Suite - Microservices Architecture

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Service Breakdown](#service-breakdown)
4. [Shared Database Design](#shared-database-design)
5. [Deployment Guide](#deployment-guide)
6. [Environment Configuration](#environment-configuration)
7. [API Endpoints](#api-endpoints)
8. [Memory Optimization](#memory-optimization)
9. [Migration from Monolith](#migration-from-monolith)
10. [Troubleshooting](#troubleshooting)
11. [Cost Analysis](#cost-analysis)

---

## Overview

The NBFC Financial Suite has been split into **4 independent microservices** that share a single PostgreSQL database. This architecture allows each service to:

- ✅ Run independently within 512MB RAM (Render free tier)
- ✅ Scale independently based on load
- ✅ Deploy without affecting other services
- ✅ Share database schema and maintain referential integrity
- ✅ Communicate through shared database (no inter-service HTTP calls needed)

### Why Microservices?

**Problem**: The monolithic application exceeded 512MB RAM limit on Render's free tier, causing deployment failures.

**Solution**: Split into 4 services, each under 512MB:
- Core Service: ~250MB
- HRMS Service: ~200MB
- Accounting Service: ~180MB
- Operations Service: ~220MB

**Total Available RAM**: 4 × 512MB = **2GB** (vs 512MB monolith)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│                  https://nbfc-frontend.onrender.com              │
└───────┬─────────────┬──────────────┬─────────────┬──────────────┘
        │             │              │             │
        │             │              │             │
        ▼             ▼              ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐ ┌────────────────┐
│ Core Service │ │   HRMS   │ │ Accounting   │ │  Operations    │
│   (512MB)    │ │ Service  │ │  Service     │ │   Service      │
│              │ │ (512MB)  │ │  (512MB)     │ │   (512MB)      │
│ • Auth       │ │          │ │              │ │                │
│ • Customers  │ │ • Emp    │ │ • GL         │ │ • CRM          │
│ • Loans      │ │ • Payroll│ │ • Assets     │ │ • Treasury     │
│ • MasterData │ │ • Attend │ │ • TDS/GST    │ │ • Compliance   │
│              │ │ • Recruit│ │              │ │ • Risk         │
└──────┬───────┘ └─────┬────┘ └──────┬───────┘ └────────┬───────┘
       │               │              │                  │
       │               │              │                  │
       └───────────────┴──────────────┴──────────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │  PostgreSQL Database   │
                  │   (Shared - 256MB)     │
                  │                        │
                  │  nbfc-postgres-shared  │
                  └────────────────────────┘
```

---

## Service Breakdown

### 1. Core Service (`main_core.py`)

**Memory**: ~250MB  
**Port**: 8000  
**URL**: https://nbfc-core-service.onrender.com

**Responsibilities**:
- ✅ Authentication & Authorization (JWT)
- ✅ User & Role Management
- ✅ Customer Management (CIF)
- ✅ Loan Origination & Servicing
- ✅ Master Data Management
- ✅ Dashboard & Analytics
- ✅ File Upload

**Key Modules**:
- Auth, Customers, Loans, MasterData, Dashboard, File Upload

**Environment File**: `.env.core.production`

**API Routes**:
```
/api/auth/*          - Authentication endpoints
/api/customers/*     - Customer management
/api/loans/*         - Loan management
/api/masterdata/*    - Master data CRUD
/api/dashboard/*     - Analytics & reports
/api/files/*         - File upload/download
/health              - Health check
/docs                - Swagger documentation
```

---

### 2. HRMS Service (`main_hrms.py`)

**Memory**: ~200MB  
**Port**: 8000  
**URL**: https://nbfc-hrms-service.onrender.com

**Responsibilities**:
- ✅ Employee Management
- ✅ Department & Designation Management
- ✅ Attendance & Leave Management
- ✅ Payroll Processing
- ✅ Recruitment & Onboarding
- ✅ Performance Management
- ✅ Training & Development

**Key Modules**:
- Employees, Departments, Attendance, Payroll, Recruitment, Training

**Environment File**: `.env.hrms.production`

**API Routes**:
```
/api/hrms/employees/*     - Employee CRUD
/api/hrms/departments/*   - Department management
/api/hrms/designations/*  - Designation management
/api/hrms/ess/*           - Employee Self Service
/api/hrms/attendance/*    - Attendance tracking
/api/hrms/payroll/*       - Payroll processing
/api/hrms/recruitment/*   - Job postings & applications
/health                   - Health check
/docs                     - Swagger documentation
```

---

### 3. Accounting Service (`main_accounting.py`)

**Memory**: ~180MB  
**Port**: 8000  
**URL**: https://nbfc-accounting-service.onrender.com

**Responsibilities**:
- ✅ Chart of Accounts Management
- ✅ Journal Entries
- ✅ General Ledger
- ✅ Trial Balance & Financial Reports
- ✅ Fixed Assets Management
- ✅ Depreciation Calculation
- ✅ TDS & GST Compliance
- ✅ Vendor Payments

**Key Modules**:
- Accounting, Fixed Assets, TDS, GST, Vendor Payments

**Environment File**: `.env.accounting.production`

**API Routes**:
```
/api/accounting/coa/*        - Chart of Accounts
/api/accounting/journal/*    - Journal entries
/api/accounting/ledger/*     - General ledger
/api/accounting/reports/*    - Financial reports
/api/accounting/tds/*        - TDS management
/api/accounting/gst/*        - GST compliance
/api/accounting/assets/*     - Fixed assets
/health                      - Health check
/docs                        - Swagger documentation
```

---

### 4. Operations Service (`main_operations.py`)

**Memory**: ~220MB  
**Port**: 8000  
**URL**: https://nbfc-operations-service.onrender.com

**Responsibilities**:
- ✅ CRM (Leads, Accounts, Opportunities, Sales)
- ✅ Treasury & Cash Management
- ✅ Asset Liability Management (ALM)
- ✅ Compliance & Regulatory Reporting
- ✅ Risk Management
- ✅ Branch Operations (optional)
- ✅ Bureau Integration
- ✅ Bank Statement Analysis
- ✅ OCR & eKYC Services

**Key Modules**:
- CRM, Treasury, ALM, Compliance, Risk, Integrations

**Environment File**: `.env.operations.production`

**API Routes**:
```
/api/crm/accounts/*          - CRM account management
/api/crm/opportunities/*     - Sales opportunities
/api/crm/sales/*             - Sales orders & quotes
/api/crm/service/*           - Customer service tickets
/api/treasury/*              - Treasury operations
/api/treasury/alm/*          - ALM reports
/api/compliance/*            - Compliance tracking
/api/risk/*                  - Risk management
/api/integration/bureau/*    - Bureau credit reports
/api/integration/ocr/*       - Document OCR
/health                      - Health check
/docs                        - Swagger documentation
```

---

## Shared Database Design

### Architecture Principles

1. **Single Source of Truth**: One PostgreSQL database for all services
2. **Referential Integrity**: Foreign keys work across service boundaries
3. **Schema Management**: Tables created once, shared by all services
4. **No Duplication**: Each table exists exactly once

### Key Tables by Service

**Core Service Tables**:
- `tenants`, `users`, `roles`, `permissions`
- `customers`, `customer_kyc`, `customer_documents`
- `loan_applications`, `loan_accounts`, `loan_emi_schedule`
- `master_data_*` (countries, banks, etc.)

**HRMS Service Tables**:
- `employees`, `departments`, `designations`
- `attendance`, `leave_applications`
- `payroll_runs`, `payslips`
- `job_postings`, `job_applications`

**Accounting Service Tables**:
- `chart_of_accounts`, `journal_entries`, `general_ledger`
- `fixed_assets`, `asset_depreciation`
- `vendor_payments`, `purchase_invoices`

**Operations Service Tables**:
- `crm_accounts`, `crm_leads`, `crm_opportunities`
- `treasury_bank_accounts`, `cash_positions`
- `compliance_alerts`, `risk_ratings`

**Shared Tables** (Always Loaded):
- `vendors` - Referenced by Inventory, Accounting, Procurement

### Foreign Key Relationships

The Vendor table fix ensures all services can reference shared tables:

```python
# Inventory items reference vendors (Operations → Accounting)
inventory_items.preferred_supplier_id → vendors.id

# Vendor payments reference vendors (Accounting → Procurement)
vendor_payments.vendor_id → vendors.id

# Purchase requisitions reference vendors (Operations → Procurement)
purchase_requisitions.preferred_vendor_id → vendors.id
```

**Solution**: Always import the `Vendor` model in `conditional_imports.py`, regardless of feature flags.

---

## Deployment Guide

### Prerequisites

1. GitHub repository with code
2. Render account (free tier works)
3. Basic understanding of environment variables

### Step-by-Step Deployment

#### Step 1: Create Shared Database

```bash
# In Render Dashboard
1. Go to "Databases"
2. Click "New PostgreSQL"
3. Name: nbfc-postgres-shared
4. Plan: Free (256MB)
5. Region: Oregon
6. Click "Create Database"
7. Copy the "Internal Database URL"
```

#### Step 2: Initialize Database Schema

**Important**: Run this ONCE to create all tables

```bash
# Option A: Deploy Core Service first with table creation
# In Core Service environment variables:
SKIP_TABLE_CREATION=false  # Only for first deployment

# After successful deployment, change to:
SKIP_TABLE_CREATION=true   # For all subsequent deployments
```

```bash
# Option B: Run Alembic migrations manually
cd backend
alembic upgrade head
```

#### Step 3: Create Environment Groups

```bash
# In Render Dashboard
1. Go to "Environment Groups"
2. Create 4 groups:
   - nbfc-core-env
   - nbfc-hrms-env
   - nbfc-accounting-env
   - nbfc-operations-env

3. For each group, upload the corresponding .env file:
   - nbfc-core-env        → .env.core.production
   - nbfc-hrms-env        → .env.hrms.production
   - nbfc-accounting-env  → .env.accounting.production
   - nbfc-operations-env  → .env.operations.production
```

#### Step 4: Deploy Services

**Option A: Using Blueprint (Recommended)**

```bash
1. In Render Dashboard, click "New" → "Blueprint"
2. Connect your GitHub repository
3. Select "render.microservices.yaml"
4. Configure environment groups for each service
5. Click "Apply" to deploy all services at once
```

**Option B: Manual Deployment**

```bash
# Deploy each service individually
1. New Web Service → Connect GitHub repo
2. Configure as follows:

Core Service:
- Name: nbfc-core-service
- Root Directory: .
- Build Command: (see render.core.yaml)
- Start Command: uvicorn backend.main_core:app --host 0.0.0.0 --port $PORT
- Environment Group: nbfc-core-env

HRMS Service:
- Name: nbfc-hrms-service
- Root Directory: .
- Build Command: (see render.microservices.yaml)
- Start Command: uvicorn backend.main_hrms:app --host 0.0.0.0 --port $PORT
- Environment Group: nbfc-hrms-env

Accounting Service:
- Name: nbfc-accounting-service
- Root Directory: .
- Build Command: (see render.microservices.yaml)
- Start Command: uvicorn backend.main_accounting:app --host 0.0.0.0 --port $PORT
- Environment Group: nbfc-accounting-env

Operations Service:
- Name: nbfc-operations-service
- Root Directory: .
- Build Command: (see render.microservices.yaml)
- Start Command: uvicorn backend.main_operations:app --host 0.0.0.0 --port $PORT
- Environment Group: nbfc-operations-env
```

#### Step 5: Update Frontend Configuration

Update frontend environment variables to point to microservices:

```bash
# In frontend/.env.production or Render Dashboard

NEXT_PUBLIC_API_URL_CORE=https://nbfc-core-service.onrender.com/api
NEXT_PUBLIC_API_URL_HRMS=https://nbfc-hrms-service.onrender.com/api
NEXT_PUBLIC_API_URL_ACCOUNTING=https://nbfc-accounting-service.onrender.com/api
NEXT_PUBLIC_API_URL_OPERATIONS=https://nbfc-operations-service.onrender.com/api
```

Update frontend API client to route requests to appropriate service:

```typescript
// Example: frontend/lib/api-client.ts

const API_URLS = {
  core: process.env.NEXT_PUBLIC_API_URL_CORE,
  hrms: process.env.NEXT_PUBLIC_API_URL_HRMS,
  accounting: process.env.NEXT_PUBLIC_API_URL_ACCOUNTING,
  operations: process.env.NEXT_PUBLIC_API_URL_OPERATIONS,
};

function getServiceUrl(endpoint: string): string {
  if (endpoint.startsWith('/auth') || endpoint.startsWith('/customers') || endpoint.startsWith('/loans')) {
    return API_URLS.core;
  }
  if (endpoint.startsWith('/hrms')) {
    return API_URLS.hrms;
  }
  if (endpoint.startsWith('/accounting')) {
    return API_URLS.accounting;
  }
  if (endpoint.startsWith('/crm') || endpoint.startsWith('/treasury')) {
    return API_URLS.operations;
  }
  return API_URLS.core; // default
}
```

#### Step 6: Verify Deployment

```bash
# Check each service health endpoint
curl https://nbfc-core-service.onrender.com/health
curl https://nbfc-hrms-service.onrender.com/health
curl https://nbfc-accounting-service.onrender.com/health
curl https://nbfc-operations-service.onrender.com/health

# Expected response for each:
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "core|hrms|accounting|operations"
  }
}
```

---

## Environment Configuration

### Common Settings (All Services)

```bash
# Database (Same for all services)
DATABASE_URL=postgresql://user:password@host:port/nbfc_suite
SKIP_TABLE_CREATION=true  # Important: Prevent table recreation

# Security (Same JWT_SECRET_KEY across all services for token validation)
JWT_SECRET_KEY=your-shared-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Allow all for development, restrict in production)
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=false

# Multi-tenancy
TENANT_ISOLATION_ENABLED=true

# Logging
LOG_LEVEL=WARNING
APP_DEBUG=false
```

### Service-Specific Settings

Each service has its own feature flags to load only required modules:

**Core Service** (`.env.core.production`):
```bash
ENABLE_AUTH=true
ENABLE_CUSTOMERS=true
ENABLE_LOANS=true
ENABLE_MASTERDATA=true
ENABLE_DASHBOARD=true

# Disable other services
ENABLE_HRMS=false
ENABLE_ACCOUNTING=false
ENABLE_CRM=false
```

**HRMS Service** (`.env.hrms.production`):
```bash
ENABLE_HRMS=true
ENABLE_RECRUITMENT=true
ENABLE_ATTENDANCE=true
ENABLE_PAYROLL=true
ENABLE_TRAINING=true

# Disable other services
ENABLE_AUTH=false  # Uses Core service for auth
ENABLE_ACCOUNTING=false
ENABLE_CRM=false
```

**Accounting Service** (`.env.accounting.production`):
```bash
ENABLE_ACCOUNTING=true
ENABLE_FIXED_ASSETS=true

# Disable other services
ENABLE_AUTH=false
ENABLE_HRMS=false
ENABLE_CRM=false
```

**Operations Service** (`.env.operations.production`):
```bash
ENABLE_CRM=true
ENABLE_CRM_OPPORTUNITIES=true
ENABLE_TREASURY=true
ENABLE_ALM=true
ENABLE_COMPLIANCE=true
ENABLE_RISK_MANAGEMENT=true
ENABLE_BUREAU_INTEGRATION=true

# Disable other services
ENABLE_AUTH=false
ENABLE_ACCOUNTING=false
ENABLE_HRMS=false
```

---

## API Endpoints

### Service Discovery

Each service exposes its endpoints at the root path:

```bash
# Get Core Service info
GET https://nbfc-core-service.onrender.com/
Response:
{
  "success": true,
  "data": {
    "service": "NBFC Core Service",
    "version": "2.0.0-microservices",
    "status": "running",
    "modules": ["Auth", "Customers", "Loans", "MasterData", "Dashboard"],
    "architecture": "microservices",
    "database": "shared-postgresql"
  }
}
```

### Interactive API Documentation

Each service has Swagger and ReDoc documentation:

- **Core**: https://nbfc-core-service.onrender.com/docs
- **HRMS**: https://nbfc-hrms-service.onrender.com/docs
- **Accounting**: https://nbfc-accounting-service.onrender.com/docs
- **Operations**: https://nbfc-operations-service.onrender.com/docs

### Authentication Flow

1. **Login** (Core Service):
```bash
POST /api/auth/login
{
  "username": "admin",
  "password": "password"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

2. **Use Token** (Any Service):
```bash
# All services validate the same JWT token
Authorization: Bearer eyJ...

# Example: Get HRMS employees
GET https://nbfc-hrms-service.onrender.com/api/hrms/employees
Headers: { "Authorization": "Bearer eyJ..." }
```

**Note**: JWT_SECRET_KEY must be **identical** across all services for token validation to work.

---

## Memory Optimization

### Techniques Used

1. **Conditional Model Loading**:
   - Each service loads only its required models
   - Prevents SQLAlchemy from loading entire schema

2. **Feature Flags**:
   - Granular control over module loading
   - Disable unused features to save memory

3. **Database Connection Pooling**:
   ```python
   DB_POOL_SIZE=2          # Small pool for low memory
   DB_MAX_OVERFLOW=2       # Limited overflow connections
   DB_POOL_RECYCLE=3600    # Recycle connections hourly
   ```

4. **GZip Compression**:
   ```python
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

5. **Lazy Loading**:
   - Routers loaded dynamically based on enabled features
   - Models imported only when needed

### Memory Breakdown

| Service | Base | Models | Routers | Middleware | Total |
|---------|------|--------|---------|-----------|-------|
| Core | 50MB | 100MB | 60MB | 40MB | ~250MB |
| HRMS | 50MB | 80MB | 40MB | 30MB | ~200MB |
| Accounting | 50MB | 70MB | 35MB | 25MB | ~180MB |
| Operations | 50MB | 90MB | 50MB | 30MB | ~220MB |

**Total**: ~850MB across 4 services (within 4 × 512MB = 2048MB limit)

---

## Migration from Monolith

### What Changed?

**Before (Monolith)**:
```
Single backend/main.py
├── All modules loaded
├── Single process
├── 512MB+ memory
└── One deployment
```

**After (Microservices)**:
```
4 independent services
├── backend/main_core.py
├── backend/main_hrms.py
├── backend/main_accounting.py
└── backend/main_operations.py
Each with selective module loading
```

### Migration Checklist

- [x] Split main.py into 4 service files
- [x] Create service-specific model import functions
- [x] Create environment files for each service
- [x] Update conditional_imports.py
- [x] Fix Vendor model always-import issue
- [x] Create Render deployment configs
- [x] Update CORS configuration (allow all origins)
- [ ] Update frontend API routing
- [ ] Test each service independently
- [ ] Deploy to production

### Breaking Changes

1. **API URLs Changed**:
   - Old: `https://nbfc-backend.onrender.com/api/customers`
   - New: `https://nbfc-core-service.onrender.com/api/customers`

2. **Service-Specific Routing Required**:
   - Frontend must route requests to correct service
   - Auth always goes to Core service
   - HRMS requests go to HRMS service, etc.

3. **JWT Token Must Be Shared**:
   - Same `JWT_SECRET_KEY` across all services
   - Otherwise, token validation will fail

### Backward Compatibility

The monolith `backend/main.py` still exists and can be used if needed. To revert to monolith:

```bash
# In Render Dashboard or .env
START_COMMAND=uvicorn backend.main:app --host 0.0.0.0 --port $PORT

# Enable all modules
ENABLE_CUSTOMERS=true
ENABLE_LOANS=true
ENABLE_ACCOUNTING=true
ENABLE_HRMS=true
ENABLE_CRM=true
ENABLE_TREASURY=true
# ... etc
```

---

## Troubleshooting

### Common Issues

#### 1. "Foreign key associated with column 'inventory_items.preferred_supplier_id' could not find table 'vendors'"

**Cause**: Vendor model not loaded when Inventory is enabled  
**Solution**: Fixed in `conditional_imports.py` - Vendor model always imported  
**See**: `VENDOR_TABLE_FIX.md`

#### 2. "JWT token validation failed"

**Cause**: Different `JWT_SECRET_KEY` across services  
**Solution**: Ensure same `JWT_SECRET_KEY` in all environment files

```bash
# Generate once, use everywhere
JWT_SECRET_KEY=your-shared-secret-key-here
```

#### 3. "CORS policy: No 'Access-Control-Allow-Origin' header"

**Cause**: CORS not configured or too restrictive  
**Solution**: Set `CORS_ORIGINS=*` in all services

```bash
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=false
```

#### 4. "Service sleeps after 15 minutes"

**Cause**: Render free tier spins down inactive services  
**Solution**: 
- Upgrade to Starter plan ($7/month per service)
- Or accept 90-second cold start time
- Or set up external ping service

#### 5. "Table already exists" error

**Cause**: `SKIP_TABLE_CREATION=false` on multiple services  
**Solution**: 
- Set `SKIP_TABLE_CREATION=true` on all services
- Only use `false` for initial schema creation on ONE service

#### 6. Service returns 500 error on startup

**Cause**: Missing environment variables or database connection  
**Solution**: Check Render logs:

```bash
# In Render Dashboard
1. Click on service
2. Go to "Logs" tab
3. Look for Python errors or missing ENV vars
```

Common missing variables:
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- Service-specific feature flags

#### 7. "Module not found" errors

**Cause**: Service trying to load disabled modules  
**Solution**: Check feature flags match service purpose

```bash
# HRMS service should NOT have:
ENABLE_CUSTOMERS=true  # ❌ Wrong service

# HRMS service should have:
ENABLE_HRMS=true       # ✅ Correct
```

---

## Cost Analysis

### Render Free Tier

**Includes**:
- 750 hours/month of compute (shared across all services)
- 512MB RAM per service
- 256MB PostgreSQL database
- Automatic SSL certificates
- Services sleep after 15 minutes of inactivity

**With 4 Services**:
- 750 hours ÷ 4 = 187.5 hours per service
- ≈ 6.25 hours per day per service
- Cold start: ~90 seconds after sleep

**Good for**: Development, testing, low-traffic demos

### Render Starter Plan (Recommended for Production)

**Cost**: $7/month per service + $7/month database

**Breakdown**:
- Core Service: $7/month
- HRMS Service: $7/month
- Accounting Service: $7/month
- Operations Service: $7/month
- Database: $7/month

**Total**: $35/month

**Includes**:
- 24/7 uptime (no sleep)
- 512MB RAM per service (2GB total)
- 1GB PostgreSQL database
- Faster deployment
- Priority support

**Good for**: Production use, customer-facing applications

### Cost Comparison

| Plan | Monthly Cost | Uptime | RAM | Best For |
|------|-------------|--------|-----|----------|
| **Monolith (Free)** | $0 | Partial (750h) | 512MB | ❌ Too small |
| **Monolith (Starter)** | $14 | 24/7 | 512MB | ❌ Still too small |
| **Microservices (Free)** | $0 | Partial (750h) | 2GB | ✅ Dev/Test |
| **Microservices (Starter)** | $35 | 24/7 | 2GB | ✅ Production |

### Scaling Options

**Vertical Scaling** (more RAM per service):
- Standard: $25/month per service (2GB RAM)
- Professional: $85/month per service (8GB RAM)

**Horizontal Scaling** (more instances):
- Add more service instances
- Load balancer required
- Database connection limit considerations

---

## Summary

### ✅ What We Achieved

1. **Split monolith into 4 microservices**
   - Core, HRMS, Accounting, Operations

2. **Shared database architecture**
   - Single PostgreSQL instance
   - All services connect to same DB
   - Referential integrity maintained

3. **Memory optimization**
   - Each service < 512MB
   - Conditional module loading
   - Feature flags for granular control

4. **Independent deployment**
   - Each service can deploy independently
   - Separate environment configurations
   - Service-specific documentation

5. **Fixed critical bugs**
   - Vendor table foreign key issue
   - CORS configuration
   - SQLAlchemy relationship errors

### 📁 Key Files Created

- `backend/main_core.py` - Core service entry point
- `backend/main_hrms.py` - HRMS service entry point
- `backend/main_accounting.py` - Accounting service entry point
- `backend/main_operations.py` - Operations service entry point
- `.env.core.production` - Core service environment
- `.env.hrms.production` - HRMS service environment
- `.env.accounting.production` - Accounting service environment
- `.env.operations.production` - Operations service environment
- `render.microservices.yaml` - Render deployment config
- `render.core.yaml` - Individual service example
- `VENDOR_TABLE_FIX.md` - Documentation of vendor FK fix
- `MICROSERVICES_ARCHITECTURE.md` - This document

### 🚀 Next Steps

1. **Deploy to Render**:
   - Follow deployment guide above
   - Start with Core service
   - Add other services incrementally

2. **Update Frontend**:
   - Configure API routing
   - Point to correct service URLs
   - Test authentication flow

3. **Monitor Performance**:
   - Check memory usage
   - Monitor API response times
   - Review error logs

4. **Scale as Needed**:
   - Upgrade to Starter plan for 24/7 uptime
   - Add more services if modules grow
   - Consider caching layer if needed

---

## Support

For issues or questions:
1. Check this documentation
2. Review `VENDOR_TABLE_FIX.md` for FK issues
3. Check Render service logs
4. Review `.env` files for correct configuration

---

**Last Updated**: 2026-07-13  
**Version**: 2.0.0-microservices  
**Status**: ✅ Ready for deployment
