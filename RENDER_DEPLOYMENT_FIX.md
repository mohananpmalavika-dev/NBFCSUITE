# 🔧 Render Deployment Fix Guide

## Problem
Your deployment is failing because:
1. **Pillow 10.1.0** doesn't work with Python 3.14
2. **Python 3.14** is too new (released Oct 2024, not fully supported)
3. Missing **runtime.txt** to specify Python version

## ✅ Solution Applied

I've fixed the following files:
1. ✅ `backend/requirements.txt` - Updated Pillow version
2. ✅ `backend/runtime.txt` - Created to specify Python 3.11.9
3. ✅ `render.yaml` - Created blueprint for one-click deployment

---

## 🚀 Quick Deploy on Render (Fixed)

### Method 1: Using Blueprint (Recommended)

1. **Push Changes to GitHub**
   ```bash
   cd c:\NBFCSUITE
   git add .
   git commit -m "Fix: Add Render deployment config with Python 3.11"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to https://dashboard.render.com/
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will read `render.yaml` and create all services automatically
   - Click "Apply" to deploy

### Method 2: Manual Setup (If Blueprint Doesn't Work)

#### Step 1: Deploy Backend

1. **Create Web Service**
   - Dashboard → "New +" → "Web Service"
   - Connect GitHub repo
   
2. **Configure Backend**
   ```
   Name: nbfc-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install --upgrade pip && pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

3. **Environment Variables** (Add in Render Dashboard)
   ```
   PYTHON_VERSION=3.11.9
   SECRET_KEY=<generate-random-32-chars>
   JWT_SECRET_KEY=<generate-random-32-chars>
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   CORS_ORIGINS=https://your-frontend.onrender.com
   APP_ENV=production
   LOG_LEVEL=INFO
   ENABLE_SWAGGER=true
   ```

4. **Advanced Settings**
   - Python Version: `3.11.9` (critical!)
   - Health Check Path: `/health`
   - Auto-Deploy: Yes

#### Step 2: Create Database

1. **New PostgreSQL Database**
   - Dashboard → "New +" → "PostgreSQL"
   - Name: `nbfc-postgres`
   - Region: Same as backend (Oregon)
   - Plan: Free

2. **Get Connection String**
   - Copy the "Internal Database URL"
   - Add to backend environment variables:
     ```
     DATABASE_URL=<internal-database-url>
     ```

#### Step 3: Deploy Frontend

1. **Create Web Service**
   - Dashboard → "New +" → "Web Service"
   - Connect same GitHub repo

2. **Configure Frontend**
   ```
   Name: nbfc-frontend
   Region: Oregon (US West)
   Branch: main
   Root Directory: frontend/apps/admin-portal
   Runtime: Node
   Build Command: npm install --legacy-peer-deps && npm run build
   Start Command: npm start
   Instance Type: Free
   ```

3. **Environment Variables**
   ```
   NODE_ENV=production
   NEXT_PUBLIC_API_URL=https://nbfc-backend.onrender.com/api/v1
   ```

---

## 🔑 Generate Secure Keys

Before deploying, generate secure keys:

### On Windows (PowerShell):
```powershell
# Generate SECRET_KEY
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# Generate JWT_SECRET_KEY
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### On Linux/Mac:
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32
```

---

## 📝 Post-Deployment Steps

### 1. Run Database Migrations

Once backend is deployed, run migrations via Render Shell:

```bash
# In Render Dashboard → Backend Service → Shell tab
cd backend
alembic upgrade head
```

### 2. Create Admin User

```bash
# In Render Shell
python -c "
import asyncio
from backend.services.auth.service import AuthService
from backend.shared.database.connection import get_db

async def create_admin():
    async for db in get_db():
        service = AuthService(db)
        user = await service.create_user(
            email='admin@nbfcsuite.com',
            username='admin',
            password='Admin@123',
            first_name='System',
            last_name='Administrator',
            is_superuser=True
        )
        print(f'Admin created: {user.email}')

asyncio.run(create_admin())
"
```

### 3. Test Deployment

```bash
# Test backend health
curl https://nbfc-backend.onrender.com/health

# Test API docs
# Visit: https://nbfc-backend.onrender.com/docs

# Test frontend
# Visit: https://nbfc-frontend.onrender.com
```

---

## 🐛 Common Issues & Fixes

### Issue 1: "Pillow build failed"
**Fix**: ✅ Already fixed in `runtime.txt` (Python 3.11.9)

### Issue 2: "Module 'backend' not found"
**Fix**: Update start command:
```bash
# Instead of: uvicorn backend.main:app
# Use: uvicorn main:app
```

### Issue 3: "Database connection failed"
**Fix**: 
- Ensure DATABASE_URL is set correctly
- Use "Internal Database URL" from Render Postgres
- Format: `postgresql://user:pass@host/dbname`

### Issue 4: "CORS errors in browser"
**Fix**: Update CORS_ORIGINS environment variable:
```
CORS_ORIGINS=https://your-frontend.onrender.com,http://localhost:3000
```

### Issue 5: "Frontend can't reach backend"
**Fix**: Update frontend environment variable:
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api/v1
```

### Issue 6: "Build timeout"
**Fix**: 
- Render free tier has 15-minute build timeout
- If timeout occurs, try again (Render caches dependencies)
- Or reduce dependencies in requirements.txt

---

## 💡 Important Notes

### Free Tier Limitations
- ⚠️ Services sleep after 15 minutes of inactivity
- ⚠️ First request after sleep takes 30-60 seconds
- ⚠️ 750 hours/month free (enough for 1 service 24/7)
- ⚠️ Database: 90 days retention, then deleted

### Recommended for Production
- Upgrade to Starter ($7/month) for:
  - ✅ No sleep
  - ✅ Better performance
  - ✅ Custom domain
  - ✅ More resources

---

## 🔄 Updating Your Deployment

After code changes:

```bash
# 1. Commit changes
git add .
git commit -m "Update: description of changes"
git push origin main

# 2. Render auto-deploys (if enabled)
# Or manually deploy from Render Dashboard
```

---

## 📊 Monitor Your Deployment

### View Logs
- Dashboard → Service → Logs tab
- Real-time streaming logs
- Filter by error/warning

### Check Metrics
- Dashboard → Service → Metrics tab
- CPU usage
- Memory usage
- Response times

### Set Alerts
- Dashboard → Service → Settings → Notifications
- Email alerts for:
  - Deployment failures
  - Service downtime
  - High resource usage

---

## 🎯 URLs After Deployment

Your application will be available at:

| Service | URL |
|---------|-----|
| **Frontend** | `https://nbfc-frontend.onrender.com` |
| **Backend API** | `https://nbfc-backend.onrender.com` |
| **API Docs** | `https://nbfc-backend.onrender.com/docs` |
| **ReDoc** | `https://nbfc-backend.onrender.com/redoc` |
| **Health Check** | `https://nbfc-backend.onrender.com/health` |

---

## 🌟 Custom Domain (Optional)

To use your own domain:

1. **Add Domain in Render**
   - Dashboard → Service → Settings → Custom Domain
   - Add: `app.yourdomain.com`

2. **Update DNS Records**
   ```
   Type: CNAME
   Name: app
   Value: nbfc-frontend.onrender.com
   TTL: 3600
   ```

3. **Update Environment Variables**
   ```
   CORS_ORIGINS=https://app.yourdomain.com
   ```

---

## 🚀 Alternative: Deploy to Railway (Faster)

If Render continues to have issues:

### Railway.app (Simpler, Faster)

1. **Sign up**: https://railway.app
2. **New Project** → Deploy from GitHub
3. **Add Services**:
   - PostgreSQL (from template)
   - Your app (auto-detected)
4. **Configure Variables**:
   - Railway auto-injects DATABASE_URL
   - Add SECRET_KEY, JWT_SECRET_KEY
5. **Deploy**: Automatic!

**Advantages**:
- ✅ Faster builds (5-10 minutes vs 15+ on Render)
- ✅ Better free tier ($5 credit/month)
- ✅ Simpler configuration
- ✅ Better performance

---

## 📞 Need Help?

### Render Documentation
- https://render.com/docs
- https://render.com/docs/deploy-fastapi
- https://render.com/docs/deploy-nextjs

### Troubleshooting
1. Check build logs in Render Dashboard
2. Verify all environment variables are set
3. Test database connection
4. Check CORS configuration
5. Verify Python version (must be 3.11.9)

### Contact
If issues persist, I can:
1. ✅ Help debug specific errors
2. ✅ Create Railway deployment config
3. ✅ Setup alternative hosting (DigitalOcean, AWS)
4. ✅ Optimize requirements.txt further

---

## ✅ Deployment Checklist

Before deploying:

- [x] Updated requirements.txt (Pillow version fixed)
- [x] Created runtime.txt (Python 3.11.9)
- [x] Created render.yaml (blueprint config)
- [ ] Pushed changes to GitHub
- [ ] Generated SECRET_KEY and JWT_SECRET_KEY
- [ ] Created Render account
- [ ] Deployed backend + database
- [ ] Ran database migrations
- [ ] Created admin user
- [ ] Deployed frontend
- [ ] Updated CORS origins
- [ ] Tested all endpoints
- [ ] Verified login works

---

## 🎉 Success Criteria

Your deployment is successful when:
1. ✅ Backend health check returns 200 OK
2. ✅ API docs accessible at /docs
3. ✅ Frontend loads without errors
4. ✅ Login works (admin/Admin@123)
5. ✅ No CORS errors in browser console
6. ✅ Dashboard displays correctly

---

**Next Step**: Push your code to GitHub and deploy! 🚀

```bash
cd c:\NBFCSUITE
git add .
git commit -m "Deploy: Add Render configuration and fix dependencies"
git push origin main
```

Then visit: https://dashboard.render.com/

**Last Updated**: July 6, 2026  
**Status**: Ready to Deploy! ✅
