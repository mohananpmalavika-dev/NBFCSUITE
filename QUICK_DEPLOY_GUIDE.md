# Quick Deployment Guide - NBFC Suite

## 🚀 Deploy in 10 Minutes

### Prerequisites
- GitHub account with repository
- Render account (free tier)
- Vercel account (free tier) OR use Render for frontend too

---

## Step 1: Push to GitHub (2 min)

```bash
cd c:\NBFCSUITE
git add .
git commit -m "Fix: All deployment issues resolved - ready for production"
git push origin main
```

---

## Step 2: Deploy Backend to Render (4 min)

### A. Create PostgreSQL Database
1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"PostgreSQL"**
3. Name: `nbfcsuite-db`
4. Click **"Create Database"**
5. **Copy the External Database URL** (you'll need this)

### B. Deploy Backend Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `nbfcsuite-backend`
   - **Environment**: `Python 3`
   - **Root Directory**: leave empty
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   
4. **Environment Variables** (click "Advanced" → "Add Environment Variable"):
   ```
   DATABASE_URL = [paste the PostgreSQL URL from step A]
   JWT_SECRET_KEY = [generate random 32+ character string]
   APP_ENV = production
   CORS_ORIGINS = *
   ```

5. Click **"Create Web Service"**
6. Wait for deployment (3-5 minutes)
7. **Copy the backend URL** (e.g., `https://nbfcsuite-backend.onrender.com`)

---

## Step 3: Deploy Frontend (4 min)

### Option A: Vercel (Recommended)

1. Go to https://vercel.com/
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend/apps/admin-portal`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

5. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL = [your backend URL from Step 2]
   ```

6. Click **"Deploy"**
7. Wait for deployment (2-3 minutes)

### Option B: Render Static Site

1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `nbfcsuite-frontend`
   - **Root Directory**: `frontend/apps/admin-portal`
   - **Build Command**: `npm install && npm run build && npm run export`
   - **Publish Directory**: `out`

4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL = [your backend URL from Step 2]
   ```

5. Click **"Create Static Site"**

---

## Step 4: Update CORS (1 min)

Go back to your backend on Render:
1. Click on your backend service
2. Go to **"Environment"**
3. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS = https://your-frontend-url.vercel.app
   ```
4. Save (service will automatically redeploy)

---

## Step 5: Verify Deployment (1 min)

### Backend Health Check
Visit: `https://your-backend.onrender.com/health`

Should return:
```json
{"status": "healthy"}
```

### API Documentation
Visit: `https://your-backend.onrender.com/docs`

Should show Swagger UI

### Frontend
Visit your frontend URL

Should load the login page

---

## 🎉 Done!

Your NBFC Suite is now deployed and running!

---

## Troubleshooting

### Backend Issues

**Problem**: Service won't start
**Check**: 
- Render logs for error messages
- Verify `DATABASE_URL` is set correctly
- Ensure `JWT_SECRET_KEY` is set

**Problem**: Database connection error
**Solution**:
- Verify PostgreSQL database is running
- Check DATABASE_URL format: `postgresql://user:pass@host/dbname`

### Frontend Issues

**Problem**: Can't reach API
**Check**:
- Browser console for errors
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings on backend

**Problem**: CORS errors
**Solution**:
- Update `CORS_ORIGINS` in backend with exact frontend URL
- Don't use `*` in production with credentials

---

## Post-Deployment Tasks

### Create Admin User
SSH into Render backend or use dashboard shell:
```bash
python -c "
from backend.scripts.create_admin import create_admin_user
create_admin_user('admin@nbfc.com', 'YourSecurePassword123!')
"
```

### Run Database Migrations
```bash
alembic upgrade head
```

---

## URLs to Save

- Backend API: `https://your-backend.onrender.com`
- Backend Docs: `https://your-backend.onrender.com/docs`
- Frontend: `https://your-frontend.vercel.app`
- Database: [Render Dashboard → PostgreSQL]

---

## Default Login (After Creating Admin)

- Email: `admin@nbfc.com`
- Password: [whatever you set]

---

## Need Help?

Check these files for detailed information:
- `DEPLOYMENT_CHECKLIST.md` - Comprehensive deployment guide
- `ALL_ISSUES_FIXED_SUMMARY.md` - Complete list of fixes
- `BACKEND_FIXES_COMPLETE.md` - Backend-specific details

---

## Environment Variables Reference

### Backend (Required)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET_KEY=your-random-secret-min-32-chars
```

### Backend (Optional but Recommended)
```bash
APP_ENV=production
LOG_LEVEL=INFO
ENABLE_SWAGGER=true
ENABLE_REDOC=true
CORS_ORIGINS=https://your-frontend.vercel.app
CORS_ALLOW_CREDENTIALS=true
```

### Frontend
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NODE_ENV=production
```

---

## Free Tier Limits

### Render Free Tier
- **Web Services**: 750 hours/month (sleeps after 15min inactivity)
- **PostgreSQL**: 1GB storage, 97 connection limit
- **Bandwidth**: 100GB/month

### Vercel Free Tier
- **Bandwidth**: 100GB/month
- **Serverless Executions**: 100GB-hours
- **Deployments**: Unlimited

---

*Deployment time: ~10 minutes*
*Total cost: $0 (using free tiers)*
