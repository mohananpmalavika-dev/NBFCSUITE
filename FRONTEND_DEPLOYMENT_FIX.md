# 🔧 Frontend Deployment Fix

## ❌ Problem
Frontend build fails with:
- `Cannot find module 'tailwindcss'`
- Missing components

**Root Cause**: `--legacy-peer-deps` removes devDependencies including tailwindcss

---

## ✅ Solution

### **Update Build Command in Render**

#### Step 1: Go to Frontend Service Settings
1. Render Dashboard → Click your **nbfc-frontend** service
2. Click **"Settings"** (left sidebar)
3. Scroll to **"Build & Deploy"** section

#### Step 2: Update Build Command

**Change Build Command from**:
```
npm install --legacy-peer-deps && npm run build
```

**To**:
```
npm install && npm run build
```

**Or better** (uses lockfile):
```
npm ci && npm run build
```

#### Step 3: Save and Redeploy
1. Click **"Save Changes"** (bottom of page)
2. Go back to main service page
3. Click **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## 🎯 Complete Frontend Configuration

Use these exact settings in Render:

### **General Settings**:
```
Name: nbfc-frontend
Branch: main
Root Directory: frontend/apps/admin-portal
```

### **Build & Deploy**:
```
Build Command: npm ci && npm run build

Publish Directory: .next

Auto-Deploy: Yes
```

### **Environment Variables**:
```
NODE_ENV=production

NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com/api/v1
```
*(Replace with your actual backend URL)*

---

## 📋 Alternative: Manual Build Test

If you want to test locally first:

```bash
cd c:\NBFCSUITE\frontend\apps\admin-portal

# Clean install
npm ci

# Build
npm run build

# If build succeeds locally, it will succeed on Render
```

---

## ⚠️ Common Issues

### Issue 1: "npm ci requires package-lock.json"

**Fix**: Generate it locally first:
```bash
cd c:\NBFCSUITE\frontend\apps\admin-portal
npm install
git add package-lock.json
git commit -m "Add package-lock.json"
git push
```

Then use `npm ci` in Render

### Issue 2: Still can't find tailwindcss

**Fix**: Make sure tailwindcss is in package.json:
```json
"devDependencies": {
  "tailwindcss": "^3.4.0",
  ...
}
```

It's already there ✅, so `npm install` should work

### Issue 3: Module resolution errors

**Fix**: Make sure tsconfig.json has correct paths:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## 🚀 Quick Deploy Steps

### Complete Steps:

1. ✅ **Update Build Command** (in Render settings)
   ```
   npm ci && npm run build
   ```

2. ✅ **Verify Environment Variable**
   ```
   NEXT_PUBLIC_API_URL=<your-backend-url>/api/v1
   ```

3. ✅ **Clear Cache & Deploy**
   - Manual Deploy → Clear build cache & deploy

4. ⏳ **Wait** (10-15 minutes)

5. ✅ **Verify** frontend loads

---

## 🎯 Expected Result

After fixing build command, you should see:

```
✓ Linting and checking validity of types
✓ Creating an optimized production build
✓ Compiled successfully
✓ Collecting page data
✓ Generating static pages
✓ Finalizing page optimization

Route (app)                              Size     First Load JS
┌ ○ /                                    1.2 kB         85.2 kB
├ ○ /customers                           2.5 kB         87.5 kB
...

○  (Static)  prerendered as static content

Build successful! 🎉
```

---

## 💡 Why npm ci is Better

| Command | Pros | Cons |
|---------|------|------|
| `npm install --legacy-peer-deps` | Ignores peer deps | ❌ Removes devDependencies |
| `npm install` | Installs everything | ⚠️ May have peer warnings |
| `npm ci` | Clean install, faster | ✅ Requires package-lock.json |

**Recommendation**: Use `npm ci` if you have package-lock.json, otherwise `npm install`

---

## 📊 Deployment Timeline

```
Now:        Update build command in Render
+1 min:     Clear cache & deploy
+10 mins:   Build completing
+12 mins:   ✅ Frontend deployed!
+15 mins:   Test & verify
```

---

## ✅ Verification Steps

After deployment succeeds:

1. **Check Build Logs**
   - Should see: "✓ Compiled successfully"
   - Should see: "Build successful 🎉"

2. **Test Frontend URL**
   ```
   https://nbfc-frontend-xxx.onrender.com
   ```
   - Should load the app
   - May take 30-60 secs first time (free tier)

3. **Test Backend Connection**
   - Frontend should connect to backend
   - Check browser console (F12) for errors
   - No CORS errors

4. **Test Login**
   - Create admin user first (via backend API docs)
   - Then login on frontend

---

## 🎯 Complete Status

After this fix:

- ✅ Backend: Live and operational
- ✅ Database: Tables created via auto-migration
- ⏳ Frontend: Deploying with fixed build command
- 🎯 App: Will be fully operational!

---

## 📞 If Build Still Fails

1. **Copy the error message** from Render logs
2. **Check for**:
   - Missing dependencies
   - TypeScript errors
   - Next.js configuration issues

3. **Common fixes**:
   - Verify all dependencies in package.json
   - Check tsconfig.json paths
   - Verify next.config.js is valid

---

## 🎉 Next Steps

Once frontend deploys successfully:

1. ✅ **Test Health**
   - Frontend loads
   - Backend connects
   - No console errors

2. 👤 **Create Admin User**
   - Use backend `/docs` endpoint
   - POST to `/auth/register`
   - Create admin account

3. 🔐 **Test Login**
   - Go to frontend
   - Login with admin credentials
   - Access dashboard

4. 🎉 **GO LIVE!**
   - Your NBFC Suite is fully operational!
   - Share URLs with stakeholders
   - Start using the application!

---

**Status**: Build command fix ready  
**Action**: Update in Render dashboard  
**Time**: 1 minute to update, 10-15 minutes to build  
**Next**: Create admin user & go live! 🚀

---

**Last Updated**: July 6, 2026  
**Issue**: Frontend build command  
**Fix**: Use `npm ci` or `npm install` without `--legacy-peer-deps`
