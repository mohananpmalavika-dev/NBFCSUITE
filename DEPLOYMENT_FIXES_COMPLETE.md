# Deployment Fixes - Complete Summary

## Date: 2026-07-08

This document summarizes all fixes applied to resolve deployment issues.

---

## 1. Frontend Build Errors - Module Resolution

### Problem
Build failed with module resolution errors in Next.js:
- `./src/services/aml.service.ts` - Can't resolve './api-client'
- `./src/services/branchService.ts` - Can't resolve './api'

### Root Cause
Two service files were using incorrect relative import paths instead of the proper alias path.

### Solution
**Files Modified:**
1. `frontend/apps/admin-portal/src/services/aml.service.ts`
   - Changed: `import { apiClient } from './api-client'`
   - To: `import { apiClient } from '@/lib/api-client'`

2. `frontend/apps/admin-portal/src/services/branchService.ts`
   - Changed: `import { apiClient } from './api'`
   - To: `import { apiClient } from '@/lib/api-client'`

### Verification
The `@/lib/api-client` path correctly points to:
`frontend/apps/admin-portal/src/lib/api-client.ts` which exports `apiClient` from `./api/client`

---

## 2. Backend SQLAlchemy Error - Duplicate Table Definition

### Problem
Backend failed to start with SQLAlchemy error:
```
Table 'cash_positions' is already defined for this MetaData instance.
```

### Root Cause
Two different model classes were using the same table name `cash_positions`:
1. `backend/shared/database/treasury_models.py` - `CashPosition` class
2. `backend/shared/database/branch_models.py` - `CashPosition` class

Both were imported in `backend/main.py`, causing a naming conflict in SQLAlchemy's metadata registry.

### Solution

#### Step 1: Renamed Treasury Model Class and Table
**File:** `backend/shared/database/treasury_models.py`
- **Class renamed:** `CashPosition` → `TreasuryCashPosition`
- **Table renamed:** `cash_positions` → `treasury_cash_positions`

#### Step 2: Updated Main Import
**File:** `backend/main.py`
- Updated import from `CashPosition` to `TreasuryCashPosition`

#### Step 3: Updated Service Files
**File:** `backend/services/treasury/cash_position_service.py`
- Updated all references from `CashPosition` to `TreasuryCashPosition`
- Updated import statement

#### Step 4: Fixed Relationships
**File:** `backend/shared/database/treasury_models.py` (TreasuryBankAccount class)
- Updated relationship: `relationship("CashPosition", ...)` → `relationship("TreasuryCashPosition", ...)`

### Impact
- **Treasury Module:** Uses `TreasuryCashPosition` model with table `treasury_cash_positions`
- **Branch Module:** Uses `CashPosition` model with table `cash_positions`
- No functional changes to either module
- Both modules can now coexist without naming conflicts

---

## Files Modified Summary

### Frontend
1. ✅ `frontend/apps/admin-portal/src/services/aml.service.ts`
2. ✅ `frontend/apps/admin-portal/src/services/branchService.ts`

### Backend
1. ✅ `backend/main.py`
2. ✅ `backend/shared/database/treasury_models.py`
3. ✅ `backend/services/treasury/cash_position_service.py`

---

## Next Steps

### Frontend Deployment
The frontend build should now succeed. Run:
```bash
cd frontend/apps/admin-portal
npm run build
```

### Backend Deployment
The backend should now start without SQLAlchemy errors. Run:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Database Migration (If Needed)
If the `cash_positions` table already exists with treasury data, you may need to:
1. Create a migration to rename existing `cash_positions` → `treasury_cash_positions`
2. Or, if the table is empty/test data, drop and recreate with proper names

---

## Testing Checklist

- [ ] Frontend builds successfully
- [ ] Backend starts without errors
- [ ] AML module loads correctly (uses aml.service.ts)
- [ ] Branch module loads correctly (uses branchService.ts)
- [ ] Treasury cash position operations work
- [ ] Branch cash position operations work

---

## Technical Notes

### Why This Happened
This is a common issue in monolithic applications where:
1. Multiple modules use similar entity names
2. ORM frameworks (like SQLAlchemy) maintain global metadata
3. Import order matters for model registration

### Prevention
For future modules:
1. Use module-specific prefixes for table names (e.g., `treasury_*`, `branch_*`)
2. Use module-specific class name prefixes for similar entities
3. Review all imports in `main.py` before adding new models
4. Run database model tests to catch conflicts early

---

**Status:** ✅ All fixes applied and ready for deployment
