# 🔧 Render CORS Configuration Fix

## Issue
Frontend getting CORS error: `No 'Access-Control-Allow-Origin' header is present`

## Solution
Add frontend URL to backend's CORS allowed origins.

## Steps

### 1. Go to Backend Service on Render
1. Open https://dashboard.render.com
2. Click on **nbfc-backend-nv05** service

### 2. Add Environment Variable
1. Click **"Environment"** in the left sidebar
2. Click **"Add Environment Variable"**
3. Add:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `https://nbfc-frontend1.onrender.com`
4. Click **"Save Changes"**

### 3. Redeploy
1. The service will automatically redeploy after saving the environment variable
2. Wait 3-5 minutes for deployment to complete
3. Check logs for "Your service is live"

### 4. Test
1. Go to https://nbfc-frontend1.onrender.com/login
2. Try logging in with:
   - Username: `admin`
   - Password: `Admin@123456`
   - Tenant ID: `default`
3. Should work without CORS errors! ✅

## Alternative: Allow All Origins (Less Secure, for Testing Only)
If you want to allow all origins temporarily for testing:
- **Key**: `CORS_ORIGINS`
- **Value**: `*`

⚠️ **Security Warning**: Only use `*` for testing. Always specify exact origins in production.

## Verification
After deployment, check the backend logs. You should see:
```
CORS origins: https://nbfc-frontend1.onrender.com
```

## Current Configuration
- **Backend URL**: https://nbfc-backend-nv05.onrender.com
- **Frontend URL**: https://nbfc-frontend1.onrender.com
- **Required CORS Origin**: https://nbfc-frontend1.onrender.com
