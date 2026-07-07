# Quick Deployment Fix Guide

## Issue Summary
Your deployment was failing due to:
1. **Frontend**: Module resolution errors in service files
2. **Backend**: SQLAlchemy duplicate table definition error

## ✅ All Fixes Applied

### Frontend Fixes (2 files)
```
✓ frontend/apps/admin-portal/src/services/aml.service.ts
✓ frontend/apps/admin-portal/src/services/branchService.ts
```
**Change:** Updated import paths from relative to alias (`@/lib/api-client`)

### Backend Fixes (3 files)
```
✓ backend/main.py
✓ backend/shared/database/treasury_models.py
✓ backend/services/treasury/cash_position_service.py
```
**Change:** Renamed `CashPosition` → `TreasuryCashPosition` in treasury module to avoid conflict with branch module

## Deployment Commands

### For Render.com (or similar)

The deployment should now work automatically. The build commands will execute:

**Frontend:**
```bash
npm install
npm run build
```

**Backend:**
```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Manual Testing Locally

**Frontend:**
```bash
cd frontend/apps/admin-portal
npm install
npm run build
npm start
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## What Was Fixed

### 1. Module Resolution Errors
- **Problem**: TypeScript couldn't find API client modules
- **Cause**: Using `./api-client` and `./api` instead of proper alias
- **Fix**: Changed to `@/lib/api-client` (standardized across project)

### 2. Duplicate Table Error
- **Problem**: Two models trying to use same table name `cash_positions`
- **Cause**: Both Treasury and Branch modules had a `CashPosition` model
- **Fix**: Separated them:
  - Treasury: `TreasuryCashPosition` → table `treasury_cash_positions`
  - Branch: `CashPosition` → table `cash_positions`

## Verification Checklist

After deployment, verify:

- [ ] Frontend builds without errors
- [ ] Backend starts without SQLAlchemy errors
- [ ] Can access admin portal homepage
- [ ] AML module loads (uses fixed aml.service.ts)
- [ ] Branch module loads (uses fixed branchService.ts)
- [ ] Treasury cash position endpoints work
- [ ] Branch operations work

## If Issues Persist

### Frontend Build Fails
1. Check build logs for any new module resolution errors
2. Verify `tsconfig.json` has proper path aliases
3. Clear build cache: `rm -rf .next && npm run build`

### Backend Fails to Start
1. Check for other duplicate table names in logs
2. Verify all imports in `backend/main.py`
3. Check database connection settings

### Database Migration Needed?
If you have existing data in `cash_positions` table from treasury module:
```sql
-- Rename existing table
ALTER TABLE cash_positions RENAME TO treasury_cash_positions;
```

## Contact Points

- **Build Logs**: Check Render.com dashboard or CI/CD logs
- **Database**: Verify connection string in environment variables
- **Environment Variables**: Ensure `NEXT_PUBLIC_API_URL` and database configs are set

---

**Status**: ✅ Ready for deployment
**Date**: 2026-07-08
**Fixes Applied**: 5 files modified
