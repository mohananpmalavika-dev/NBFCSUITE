# Swagger "Failed to Fetch" Error - Fix Guide

## Problem
You're seeing "Failed to fetch" errors in the Swagger UI (`/docs`) when trying to execute API calls. This is a CORS (Cross-Origin Resource Sharing) issue.

## Root Cause
The `CORS_ORIGINS` setting in your backend only allows `http://localhost:3000,http://localhost:3001`, but your Swagger UI is trying to make requests from your Render deployment URL.

## Solution

### Option 1: Allow All Origins (Quick Fix for Testing)

Add this environment variable in **Render Dashboard → Your Web Service → Environment**:

```bash
CORS_ORIGINS=*
```

**Pros**: Works immediately, good for testing
**Cons**: Less secure (allows any origin)

### Option 2: Specific Origins (Recommended for Production)

Add your specific Render URLs:

```bash
CORS_ORIGINS=https://your-backend.onrender.com,https://your-frontend.onrender.com,http://localhost:3000
```

Replace:
- `your-backend.onrender.com` with your actual backend Render URL
- `your-frontend.onrender.com` with your actual frontend Render URL

**Pros**: More secure, only allows trusted origins
**Cons**: Need to update when adding new frontends

### How to Set Environment Variable in Render:

1. Go to https://dashboard.render.com
2. Click on your **Backend Web Service**
3. Click on **"Environment"** in the left sidebar
4. Click **"Add Environment Variable"**
5. Set:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `*` (or your specific URLs comma-separated)
6. Click **"Save Changes"**
7. Render will automatically restart your service

### Verification

After the deployment completes:

1. Go to your Swagger docs: `https://your-backend.onrender.com/docs`
2. Try the `/health` endpoint (click "Try it out" → "Execute")
3. You should now see a successful response instead of "Failed to fetch"

## Code Changes Already Applied

I've updated `backend/main.py` to:
- Support wildcard (`*`) in CORS_ORIGINS
- Automatically disable credentials when using wildcard (required by CORS spec)

**Committed**: "fix: Allow wildcard CORS origins for Swagger docs access"
**Status**: Pushed to GitHub, deployment will trigger

## Testing After Fix

Once deployed, test these endpoints in Swagger UI:

1. **GET /health** - Should return healthy status
2. **GET /** - Should return API information  
3. **POST /api/v1/auth/register** - Create a test user (after DATABASE_URL is fixed)

## Still Seeing Errors?

If you still see "Failed to fetch" after setting CORS_ORIGINS:

### Check 1: Verify the backend is actually running
Visit: `https://your-backend.onrender.com/health`

**Expected response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": 1720526400.0,
    "services": {
      "api": "operational",
      "database": "operational",
      "cache": "operational"
    }
  }
}
```

If you see this, the backend is running and CORS should work after setting the environment variable.

### Check 2: Verify DATABASE_URL is Set

If the backend is not starting, it's likely the DATABASE_URL issue. Check the deployment logs in Render for errors like:
- "Name or service not known"
- "Could not connect to database"

Follow the instructions in `DEPLOYMENT_FIX_SUMMARY.md` to fix the DATABASE_URL.

### Check 3: Browser Console Errors

Open browser DevTools (F12) → Console tab
Look for specific CORS errors that show which origin is being blocked.

## Summary

**Immediate Action Required**:
1. ✅ Code fix pushed (CORS wildcard support)
2. ⏳ Wait for Render to deploy
3. ⚠️ **Set CORS_ORIGINS=* in Render environment variables**
4. ⏳ Wait for automatic restart
5. ✅ Test Swagger UI

**If still not working, check DATABASE_URL next (see DEPLOYMENT_FIX_SUMMARY.md)**
