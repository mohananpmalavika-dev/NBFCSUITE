# Exit Management System - Setup Guide

**Quick Installation Guide for Exit Management Module**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Database Setup](#database-setup)
4. [Frontend Setup](#frontend-setup)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.9 or higher
- **PostgreSQL**: 13 or higher
- **Node.js**: 18 or higher
- **npm**: 9 or higher

### Check Versions

```bash
# Check Python version
python --version

# Check PostgreSQL version
psql --version

# Check Node.js version
node --version

# Check npm version
npm --version
```

---

## Backend Setup

### Step 1: Clone Repository (if not already done)

```bash
git clone <repository-url>
cd NBFCSUITE
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Backend Files

Check that these files exist:
```
backend/
├── shared/database/hrms_models.py
├── services/hrms/
│   ├── schemas/exit_schemas.py
│   ├── services/exit_service.py
│   └── routes/exit_routes.py
└── main.py
```

---

## Database Setup

### Step 1: Create Database (if not exists)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE nbfc_db;

# Create user (if needed)
CREATE USER nbfc_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nbfc_db TO nbfc_user;

# Exit psql
\q
```

### Step 2: Configure Database Connection

Create or update `.env` file in project root:

```bash
DATABASE_URL=postgresql://nbfc_user:your_password@localhost:5432/nbfc_db
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
API_V1_PREFIX=/api/v1
```

### Step 3: Run Configuration Script

This script checks database connection and migration status:

```bash
python scripts/configure_exit_management.py
```

**Expected Output:**
```
======================================================================
                  Database Connection Check                           
======================================================================

✓ Database connection successful

======================================================================
                    Migration Status Check                             
======================================================================

✓ Table 'exit_resignations' exists
✓ Table 'exit_clearances' exists
✓ Table 'exit_settlements' exists
✓ Table 'exit_settlement_components' exists
✓ Table 'exit_documents' exists
```

### Step 4: Run Migration (if tables don't exist)

```bash
# Option A: Using psql
psql -U nbfc_user -d nbfc_db -f database/migrations/add_exit_management_tables.sql

# Option B: Using configuration script (recommended)
# The script will prompt you to run migration if tables don't exist
python scripts/configure_exit_management.py
```

### Step 5: Verify Database Setup

```bash
# Connect to database
psql -U nbfc_user -d nbfc_db

# Check tables
\dt exit_*

# Check enums
\dT resignation_*

# Exit
\q
```

You should see 5 tables:
- exit_resignations
- exit_clearances
- exit_settlements
- exit_settlement_components
- exit_documents

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend/apps/admin-portal
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Configure Environment

Create `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000
```

### Step 4: Verify Frontend Files

Check that these files exist:
```
src/
├── types/exit.types.ts
├── services/exit.service.ts
└── components/exit/
    ├── ExitStatusBadge.tsx
    ├── ResignationWorkflowStepper.tsx
    ├── ClearanceChecklist.tsx
    ├── SettlementBreakdown.tsx
    └── DocumentPreview.tsx
```

---

## Configuration

### Step 1: Start Backend Server

```bash
# From project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 2: Verify API Documentation

Open browser and navigate to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Look for "HRMS - Exit Management" section with 33 endpoints.

### Step 3: Seed Sample Data (Optional)

```bash
# Create sample resignations and related data
python scripts/seed_exit_data.py
```

**Expected Output:**
```
Creating resignation for John Doe (submitted)...
  ✓ Created resignation: RES20241215001
  ✓ Created 5 clearances
  
Creating resignation for Jane Smith (approved)...
  ✓ Created resignation: RES20241215002
  ✓ Created 5 clearances
  ✓ Created settlement: FNF20241215001
  ✓ Created 3 documents

Seed Data Summary:
  Resignations: 5
  Clearances: 25
  Settlements: 3
  Documents: 9

✓ Seed data created successfully!
```

### Step 4: Start Frontend (Optional)

```bash
# From frontend/apps/admin-portal directory
npm run dev
```

Access at: http://localhost:3000

---

## Verification

### Automated Verification

Run the comprehensive verification script:

```bash
python scripts/verify_exit_deployment.py
```

This checks:
- ✓ Database tables (5 tables)
- ✓ Database enums (6 enums)
- ✓ Database indexes (20+ indexes)
- ✓ Helper functions (3 functions)
- ✓ API endpoints (33 endpoints)
- ✓ API documentation (Swagger, ReDoc)
- ✓ Backend files (5 files)
- ✓ Frontend files (7 files)

**Expected Success Rate**: 100%

### Manual Verification

#### 1. Test API Endpoint

```bash
# Get resignations list
curl -X GET "http://localhost:8000/api/v1/hrms/exit/resignations" \
  -H "accept: application/json"
```

#### 2. Check Database Records

```bash
psql -U nbfc_user -d nbfc_db -c "SELECT COUNT(*) FROM exit_resignations;"
```

#### 3. Test API with Authentication

```bash
# Login first to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"your_user","password":"your_pass"}'

# Use token in subsequent requests
curl -X GET "http://localhost:8000/api/v1/hrms/exit/dashboard/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Troubleshooting

### Issue 1: Database Connection Failed

**Error**: `could not connect to server`

**Solutions:**
1. Check PostgreSQL is running:
   ```bash
   # Linux/macOS
   sudo systemctl status postgresql
   
   # Windows
   services.msc (look for PostgreSQL service)
   ```

2. Verify connection details in `.env` file
3. Check PostgreSQL is listening on correct port (default 5432)

### Issue 2: Migration Failed

**Error**: `relation "exit_resignations" already exists`

**Solutions:**
1. Tables already exist - skip migration
2. To re-run migration, first drop existing tables:
   ```sql
   DROP TABLE IF EXISTS exit_documents CASCADE;
   DROP TABLE IF EXISTS exit_settlement_components CASCADE;
   DROP TABLE IF EXISTS exit_settlements CASCADE;
   DROP TABLE IF EXISTS exit_clearances CASCADE;
   DROP TABLE IF EXISTS exit_resignations CASCADE;
   ```

### Issue 3: API Returns 404

**Error**: `Not Found` for `/api/v1/hrms/exit/*`

**Solutions:**
1. Verify backend server is running
2. Check routes are registered in `backend/main.py`:
   ```python
   from backend.services.hrms.routes import exit_routes
   app.include_router(exit_routes.router, prefix="/api/v1/hrms/exit", tags=["HRMS - Exit Management"])
   ```
3. Restart backend server

### Issue 4: Import Errors

**Error**: `ModuleNotFoundError: No module named 'backend'`

**Solutions:**
1. Verify virtual environment is activated
2. Install dependencies: `pip install -r requirements.txt`
3. Check PYTHONPATH includes project root

### Issue 5: Frontend Build Fails

**Error**: `Cannot find module '@/types/exit.types'`

**Solutions:**
1. Verify TypeScript types file exists: `src/types/exit.types.ts`
2. Check tsconfig.json path aliases
3. Run `npm install` again
4. Clear `.next` cache: `rm -rf .next && npm run dev`

### Issue 6: Seed Data Fails

**Error**: `No employees found in database`

**Solutions:**
1. Create employees first in HRMS Employee module
2. Or modify seed script to create sample employees
3. Check tenant_id matches existing employees

---

## Quick Start Commands

### Complete Setup in One Go

```bash
# 1. Install backend dependencies
pip install -r requirements.txt

# 2. Configure and migrate database
python scripts/configure_exit_management.py

# 3. Seed sample data
python scripts/seed_exit_data.py

# 4. Verify deployment
python scripts/verify_exit_deployment.py

# 5. Start backend server
uvicorn backend.main:app --reload
```

### Verify Setup

```bash
# Run API tests
python scripts/test_exit_api.py

# Check API documentation
open http://localhost:8000/docs
```

---

## Next Steps

After successful setup:

1. **Read User Guide**: `docs/EXIT_MANAGEMENT_USER_GUIDE.md`
2. **Review API Documentation**: http://localhost:8000/docs
3. **Test Workflows**: Use seeded data to test resignation workflows
4. **Customize**: Modify templates, clearance types, or calculation logic as needed

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs: `logs/exit_management.log`
3. Check database logs: PostgreSQL logs
4. Review API documentation: http://localhost:8000/docs

---

**Setup Guide Version**: 1.0.0  
**Last Updated**: December 2024
