# 🆓 Deploy FREE in 15 Minutes (No Credit Card!)

## 🎯 Easiest FREE Stack

- **Database**: Neon.tech (Free PostgreSQL)
- **Backend**: Cyclic.sh (Free hosting)  
- **Frontend**: Vercel (Free hosting)

**Total: $0, No credit card required!**

---

## 📋 Step-by-Step

### STEP 1: Create Free Database (3 minutes)

1. Go to: https://console.neon.tech/signup
2. Click "Sign up with GitHub"
3. Create new project:
   - Name: `nbfc-suite`
   - Region: Choose nearest
   - Click "Create Project"
4. **Copy Connection String**:
   - Dashboard → Connection Details
   - Copy the connection string
   - Should look like: `postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb`
   - **Save this!** You'll need it in Step 2

---

### STEP 2: Generate Secret Keys (1 minute)

Open PowerShell and run this **TWICE**:

```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

**Save both outputs**:
- First output → SECRET_KEY
- Second output → JWT_SECRET_KEY

---

### STEP 3: Push Code to GitHub (5 minutes)

If not already on GitHub:

```bash
cd c:\NBFCSUITE

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: NBFC Suite"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/nbfc-suite.git
git branch -M main
git push -u origin main
```

---

### STEP 4: Deploy Backend on Cyclic (3 minutes)

1. Go to: https://app.cyclic.sh
2. Click "Sign in with GitHub"
3. Click "Link Your Own" button
4. Select your `nbfc-suite` repository
5. Click "Connect"
6. **Configure**:
   - Cyclic auto-detects everything
7. **Add Environment Variables**:
   - Click "Variables" tab
   - Add these (one by one):
     ```
     DATABASE_URL=<paste-neon-connection-string-from-step-1>
     SECRET_KEY=<first-key-from-step-2>
     JWT_SECRET_KEY=<second-key-from-step-2>
     JWT_ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     CORS_ORIGINS=*
     APP_ENV=production
     LOG_LEVEL=INFO
     ENABLE_SWAGGER=true
     ```
8. Click "Deploy"
9. Wait 2-3 minutes for build
10. **Copy your backend URL**: `https://YOUR-APP.cyclic.app`

**Test it**:
- Health: `https://YOUR-APP.cyclic.app/health`
- API Docs: `https://YOUR-APP.cyclic.app/docs`

---

### STEP 5: Run Database Migrations (2 minutes)

Cyclic doesn't have a shell, so we'll modify the code to run migrations on startup:

**Option A: Quick Fix** - Add to `backend/main.py`:

```python
# Add at the top
import subprocess

# Add after app = FastAPI(...) 
@app.on_event("startup")
async def startup_event():
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
    except:
        pass  # Migrations might already be run
```

**Option B: Manual** - Use Neon's SQL Editor:
1. Go to Neon dashboard
2. SQL Editor tab
3. Copy-paste schema from `backend/alembic/versions/*.py`
4. Execute

For now, let's use **Option A** - it's simpler!

---

### STEP 6: Deploy Frontend on Vercel (3 minutes)

1. Go to: https://vercel.com/signup
2. Click "Continue with GitHub"
3. Click "Import Project"
4. Select your `nbfc-suite` repository
5. **Configure**:
   - Framework Preset: Next.js
   - Root Directory: `frontend/apps/admin-portal`
   - Build Command: `npm install --legacy-peer-deps && npm run build`
   - Output Directory: `.next`
6. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://YOUR-CYCLIC-APP.cyclic.app/api/v1
   ```
   (Use your backend URL from Step 4)
7. Click "Deploy"
8. Wait 3-5 minutes
9. **Copy your frontend URL**: `https://YOUR-APP.vercel.app`

---

## 🎉 SUCCESS!

Your application is now live!

### Your URLs:
- **Frontend**: `https://YOUR-APP.vercel.app`
- **Backend**: `https://YOUR-APP.cyclic.app`
- **API Docs**: `https://YOUR-APP.cyclic.app/docs`
- **Database**: Managed by Neon

### Default Login:
- **Username**: `admin`
- **Password**: `admin123`

*(You'll need to create this user - see below)*

---

## 👤 Create Admin User

Since Cyclic doesn't have shell access, we'll create a signup endpoint temporarily:

Add this to `backend/main.py`:

```python
@app.post("/api/v1/setup/admin")
async def create_admin():
    """Temporary endpoint to create admin - REMOVE IN PRODUCTION"""
    from services.auth.service import AuthService
    from shared.database.connection import get_db
    
    async for db in get_db():
        service = AuthService(db)
        try:
            user = await service.create_user(
                email="admin@nbfcsuite.com",
                username="admin",
                password="Admin@123",
                first_name="System",
                last_name="Administrator",
                is_superuser=True
            )
            return {"message": "Admin created", "email": user.email}
        except Exception as e:
            return {"message": "Admin might already exist", "error": str(e)}
```

Then:
1. Push changes to GitHub
2. Cyclic auto-deploys
3. Visit: `https://YOUR-APP.cyclic.app/api/v1/setup/admin`
4. Admin user created!
5. **Remove this endpoint** from code and redeploy

---

## ✅ Verification Checklist

- [ ] Backend health check works
- [ ] API docs accessible
- [ ] Frontend loads
- [ ] Can login
- [ ] Dashboard displays
- [ ] No console errors

---

## 🔧 If Something Fails

### Backend won't start:
1. Check Cyclic logs (Logs tab)
2. Verify DATABASE_URL is correct
3. Check all environment variables are set

### Frontend can't reach backend:
1. Verify NEXT_PUBLIC_API_URL is correct
2. Should be: `https://your-backend.cyclic.app/api/v1`
3. Check CORS_ORIGINS is set to `*` in backend

### Database connection error:
1. Verify Neon connection string
2. Make sure it starts with `postgresql://`
3. Check database is active in Neon dashboard

---

## 💰 Cost Breakdown

| Service | Cost | Limits |
|---------|------|--------|
| **Neon** | FREE | 512MB storage, 1 compute unit |
| **Cyclic** | FREE | Unlimited apps, auto-sleep |
| **Vercel** | FREE | 100GB bandwidth, unlimited sites |
| **Total** | $0 | Perfect for demo/testing! |

---

## 🚀 Upgrade Options (Later)

When you outgrow free tier:

- **Neon Pro**: $19/month (3GB storage)
- **Cyclic Pro**: No paid tier yet (all free!)
- **Vercel Pro**: $20/month (no sleep, analytics)

---

## 📊 Alternative Free Options

If Cyclic doesn't work:

### Backend:
- **Koyeb**: https://app.koyeb.com (similar to Cyclic)
- **Glitch**: https://glitch.com (code editor included)
- **Deta Space**: https://deta.space (free Python hosting)

### Database:
- **Supabase**: https://supabase.com (500MB free)
- **ElephantSQL**: https://elephantsql.com (20MB free)

---

## 🎯 Quick Reference

### Neon Dashboard:
https://console.neon.tech

### Cyclic Dashboard:
https://app.cyclic.sh

### Vercel Dashboard:
https://vercel.com/dashboard

### View Logs:
- Cyclic: Dashboard → Logs tab
- Vercel: Dashboard → Deployments → Logs

---

## 🎉 You Did It!

Your NBFC Financial Suite is now live on the internet for FREE!

**Share your URLs**:
- Frontend: `https://YOUR-APP.vercel.app`
- API Docs: `https://YOUR-APP.cyclic.app/docs`

**Next Steps**:
1. Test all features
2. Share with stakeholders
3. Get feedback
4. Iterate and improve

---

**Total Time**: 15-20 minutes  
**Total Cost**: $0  
**Credit Card**: Not needed  
**Status**: ✅ LIVE!  

**Congratulations! 🎉**

---

**Last Updated**: July 6, 2026  
**Platform**: Neon + Cyclic + Vercel  
**Cost**: FREE Forever (within limits)
