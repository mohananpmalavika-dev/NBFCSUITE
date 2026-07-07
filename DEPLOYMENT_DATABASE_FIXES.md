# Deployment Database & Build Fixes

## Issue Summary
Two critical deployment issues were preventing the application from deploying successfully:

### 1. Backend Database Issue
**Error**: Foreign key constraint failure - incompatible types between `bureau_consents.customer_id` (INTEGER) and `customers.id` (UUID)

**Root Cause**: The `integration_models.py` file was using old `Integer` type for ID fields, while the rest of the application uses `UUID` as defined in `BaseModel`.

**Files Fixed**: `backend/shared/database/integration_models.py`

**Changes Made**:
- ✅ Added UUID imports: `from sqlalchemy.dialects.postgresql import UUID` and `import uuid`
- ✅ Changed all primary key `id` fields from `Integer` to `UUID(as_uuid=True)` with `default=uuid.uuid4`
- ✅ Changed all foreign key ID fields from `Integer` to `UUID(as_uuid=True)`
- ✅ Changed `tenant_id` from `Integer` to `String(50)` to match BaseModel standard

**Models Updated**:
1. **BureauReport**
   - `id`: Integer → UUID
   - `customer_id`: Integer → UUID
   - `consent_id`: Integer → UUID
   - `pulled_by`: Integer → UUID
   - `tenant_id`: Integer → String(50)

2. **BureauConsent**
   - `id`: Integer → UUID
   - `customer_id`: Integer → UUID
   - `tenant_id`: Integer → String(50)

3. **BankStatementAnalysis**
   - `id`: Integer → UUID
   - `customer_id`: Integer → UUID
   - `application_id`: Integer → UUID
   - `tenant_id`: Integer → String(50)

4. **DocumentOCRResult**
   - `id`: Integer → UUID
   - `customer_id`: Integer → UUID
   - `document_id`: Integer → UUID
   - `tenant_id`: Integer → String(50)

5. **EKYCRecord**
   - `id`: Integer → UUID
   - `customer_id`: Integer → UUID
   - `tenant_id`: Integer → String(50)

6. **DigiLockerDocument**
   - `id`: Integer → UUID
   - `customer_id`: Integer → UUID
   - `tenant_id`: Integer → String(50)

### 2. Frontend Build Issue
**Error**: TypeScript build errors in `frontend/apps/admin-portal/src/app/loans/restructuring/page.tsx`

**Root Cause**: The build command was trying to build from within the `admin-portal` directory without properly setting up the npm workspace dependencies.

**File Fixed**: `render.yaml`

**Changes Made**:
```yaml
# Before
buildCommand: cd frontend/apps/admin-portal && npm install --legacy-peer-deps && npm run build
startCommand: cd frontend/apps/admin-portal && npm start

# After
rootDir: frontend
buildCommand: npm install --legacy-peer-deps && cd apps/admin-portal && npm run build
startCommand: cd apps/admin-portal && npm start
```

**Why This Works**:
- `rootDir: frontend` - Sets the working directory to the frontend workspace root
- `npm install` runs at workspace level, installing all dependencies properly
- Then navigates to `apps/admin-portal` to run the actual build
- This ensures workspace dependencies and type definitions are resolved correctly

## Commits Made
1. **7e3b058**: "Fix: Change integration models ID fields from Integer to UUID to match Customer model schema"
2. **ac5c22c**: "Fix: Update frontend build command to use workspace root directory"

## Expected Results
- ✅ Backend should start without foreign key constraint errors
- ✅ Database tables should be created successfully with correct UUID types
- ✅ Frontend should build without TypeScript errors
- ✅ All foreign key relationships should work properly

## Testing Checklist
Once deployed, verify:
- [ ] Backend health check passes (`/health` endpoint)
- [ ] Database migrations run successfully
- [ ] Frontend builds and serves correctly
- [ ] API endpoints are accessible
- [ ] No database constraint errors in logs

## Notes
- All integration models now consistently use UUID for IDs
- This aligns with the BaseModel standard used throughout the application
- The workspace structure is now properly respected in the build process
- Future models should inherit from `BaseModel` instead of `Base` directly to ensure consistency
