# Frontend API Path Fix - Missing /api/v1 Prefix

## Problem
The frontend was calling API endpoints without the `/api/v1` prefix:
- **Called**: `https://nbfc-backend-ok99.onrender.com/auth/login` ❌
- **Expected**: `https://nbfc-backend-ok99.onrender.com/api/v1/auth/login` ✓

This caused 404 errors for all API calls from the frontend.

## Root Cause
The `apiClient` in `frontend/apps/admin-portal/src/lib/api/client.ts` was using the environment variable `NEXT_PUBLIC_API_URL` directly as the base URL without adding the `/api/v1` prefix.

## Solution Applied

### Code Change
Updated `frontend/apps/admin-portal/src/lib/api/client.ts`:

**Before**:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  // ...
});
```

**After**:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1_BASE_URL = `${API_BASE_URL}/api/v1`;

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_V1_BASE_URL,
  // ...
});
```

### What This Fixes
Now all API calls automatically include the `/api/v1` prefix:
- `/auth/login` → `https://nbfc-backend-ok99.onrender.com/api/v1/auth/login` ✓
- `/auth/register` → `https://nbfc-backend-ok99.onrender.com/api/v1/auth/register` ✓
- `/customers` → `https://nbfc-backend-ok99.onrender.com/api/v1/customers` ✓
- `/loans` → `https://nbfc-backend-ok99.onrender.com/api/v1/loans` ✓
- And ALL other API endpoints ✓

## Deployment Status

**Git Status**:
- ✅ Committed: "fix: Add /api/v1 prefix to frontend API base URL"
- ✅ Pushed to GitHub: main branch
- ⏳ Frontend deployment will trigger on Render

## Verification

After the frontend deployment completes:

1. **Visit your admin portal**: `https://your-frontend.onrender.com/auth/login`
2. **Try to login** with test credentials
3. **Check browser DevTools** (F12) → Network tab
4. **Verify the API call URL** includes `/api/v1`:
   - Should see: `POST https://nbfc-backend-ok99.onrender.com/api/v1/auth/login`

## Expected Behavior After Fix

### Login Flow:
1. User enters credentials in login form
2. Frontend makes POST request to `/api/v1/auth/login`
3. Backend validates credentials
4. Backend returns JWT token and user data
5. Frontend stores token in localStorage
6. User is redirected to dashboard

### If Still Seeing Errors:

#### Error: "Network Error" or "Failed to fetch"
**Possible causes**:
1. Backend not running - Check: `https://nbfc-backend-ok99.onrender.com/health`
2. CORS not configured - Set `CORS_ORIGINS=*` in backend environment
3. DATABASE_URL not set - Backend can't start without valid database connection

#### Error: 401 Unauthorized
**Possible causes**:
1. Invalid credentials
2. User doesn't exist in database
3. Need to create admin user first

#### Error: 500 Internal Server Error
**Possible causes**:
1. Database connection issue
2. Missing tables in database
3. Check backend logs in Render dashboard

## Next Steps

### After Frontend Deployment:
1. ✅ Frontend fix deployed
2. ⏳ Test login functionality
3. If login works, create admin user (if not already created)
4. If login fails, check backend status and environment variables

### Backend Prerequisites (Must be done first):
- ✅ Code fixes deployed (Organization, ForeignKey, CORS)
- ⚠️ **Set CORS_ORIGINS=* in Render**
- ⚠️ **Set correct DATABASE_URL in Render**
- ⏳ Verify backend health endpoint works

## Admin User Creation

Once backend is fully working, create the first admin user by calling the register endpoint:

**Using curl**:
```bash
curl -X POST https://nbfc-backend-ok99.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@nbfc.com",
    "username": "admin",
    "password": "Admin@123",
    "full_name": "System Administrator"
  }'
```

**Or using Swagger UI**:
1. Go to: `https://nbfc-backend-ok99.onrender.com/docs`
2. Find POST `/api/v1/auth/register`
3. Click "Try it out"
4. Fill in the user details
5. Execute

**Default credentials suggestion**:
- Email: `admin@nbfc.com`
- Username: `admin`
- Password: `Admin@123` (change this immediately after first login!)
- Full Name: `System Administrator`

## Summary

| Component | Status | Action |
|-----------|--------|--------|
| ✅ Frontend API path | Fixed & Pushed | Wait for frontend deployment |
| ✅ Backend code fixes | Fixed & Pushed | Backend already deployed |
| ⚠️ CORS configuration | Code ready | **Set CORS_ORIGINS=* in Render** |
| ⚠️ Database connection | Not configured | **Set DATABASE_URL in Render** |
| ⏳ Admin user | Pending | Create after backend is healthy |

**Critical**: The backend must be fully healthy (CORS + DATABASE_URL configured) before the frontend login will work!
