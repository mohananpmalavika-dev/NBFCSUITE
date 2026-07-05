# 🎯 Render.com Simple Deployment (FREE)

**No Credit Card Required | 20-30 Minutes**

---

## 🎯 What You'll Deploy

- **Backend**: FastAPI on Render
- **Database**: PostgreSQL on Render (FREE)
- **Frontend**: Static site on Render

**All on one platform, all FREE!**

---

## 📋 Before You Start

### 1. Generate Keys (2 minutes)

Open PowerShell and run this **TWO TIMES**:

```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

**Save in Notepad**:
```
SECRET_KEY: <first output>
JWT_SECRET_KEY: <second output>
```

### 2. Push to GitHub

```bash
cd c:\NBFCSUITE

git init
git add .
git commit -m "Deploy: NBFC Suite"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/nbfc-suite.git
git push -u origin main
```

---

## 🚀 Step 1: Sign Up (2 minutes)

1. Go to: **https://dashboard.render.com/register**
2. Click: **"Sign up with GitHub"**
3. Authorize Render

---

## 🗄️ Step 2: Create Database (3 minutes)

1. Dashboard → **"New +"** → **"PostgreSQL"**

2. **Fill in**:
   ```
   Name: nbfc-postgres
   Database: nbfc_db
   User: nbfc_user  
   Region: Oregon (US West)
   PostgreSQL Version: 15
   Plan: Free
   ```

3. Click: **"Create Database"**

4. Wait 1-2 minutes for creation

5. **Copy Connection String**:
   - Click on the database
   - Go to **"Info"** tab
   - Find **"Internal Database URL"**
   - Click copy icon
   - **Paste in Notepad** - you'll need this!

---

## 🖥️ Step 3: Deploy Backend (10 minutes)

1. Dashboard → **"New +"** → **"Web Service"**

2. **Connect Repository**:
   - Click **"Connect a repository"**
   - If first time: Click **"Connect GitHub"** → Authorize
   - Find: **"nbfc-suite"**
   - Click **"Connect"**

3. **Configure**:
   ```
   Name: nbfc-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.render.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

4. **Click "Advanced"**:
   - **Python Version**: Type `3.11.9`
   - **Health Check Path**: Type `/health`

5. **Environment Variables** (click "Add Environment Variable" for each):
   ```
   Name: PYTHON_VERSION
   Value: 3.11.9

   Name: DATABASE_URL
   Value: <paste your database Internal URL from Step 2>

   Name: SECRET_KEY
   Value: <your first generated key>

   Name: JWT_SECRET_KEY
   Value: <your second generated key>

   Name: JWT_ALGORITHM
   Value: HS256

   Name: ACCESS_TOKEN_EXPIRE_MINUTES
   Value: 30

   Name: CORS_ORIGINS
   Value: *

   Name: APP_ENV
   Value: production

   Name: LOG_LEVEL
   Value: INFO

   Name: ENABLE_SWAGGER
   Value: true
   ```

6. Click: **"Create Web Service"**

7. **Wait 10-15 minutes** for build (watch logs)

8. Once deployed, **copy your backend URL**:
   - Top of page: `https://nbfc-backend-xxxx.onrender.com`
   - **Save this URL!**

---

## 🔧 Step 4: Run Migrations (2 minutes)

1. Go to your backend service
2. Click: **"Shell"** tab (right side)
3. Wait for shell to connect
4. Run:
   ```bash
   alembic upgrade head
   ```
5. You should see: `Running upgrade -> xxx, Initial migration`

---

## 🌐 Step 5: Deploy Frontend (10 minutes)

1. Dashboard → **"New +"** → **"Static Site"**

2. **Connect Repository**:
   - Click **"Connect a repository"**
   - Find: **"nbfc-suite"** (same repo)
   - Click **"Connect"**

3. **Configure**:
   ```
   Name: nbfc-frontend
   Branch: main
   Root Directory: frontend/apps/admin-portal
   Build Command: npm install --legacy-peer-deps && npm run build
   Publish Directory: .next
   ```

4. **Environment Variables**:
   ```
   Name: NODE_ENV
   Value: production

   Name: NEXT_PUBLIC_API_URL
   Value: https://nbfc-backend-xxxx.onrender.com/api/v1
   ```
   **(Use your backend URL from Step 3!)**

5. Click: **"Create Static Site"**

6. **Wait 10-15 minutes** for build

7. Once deployed, **copy your frontend URL**:
   - Top of page: `https://nbfc-frontend-xxxx.onrender.com`

---

## 👤 Step 6: Create Admin User (3 minutes)

### Option A: Using API Docs (Easiest)

1. Go to: `https://nbfc-backend-xxxx.onrender.com/docs`
   - ⚠️ First load takes 30-60 seconds (free tier wakes up)

2. Find: **`POST /api/v1/auth/register`**

3. Click: **"Try it out"**

4. Fill in:
   ```json
   {
     "email": "admin@nbfcsuite.com",
     "username": "admin",
     "password": "Admin@123",
     "first_name": "System",
     "last_name": "Administrator"
   }
   ```

5. Click: **"Execute"**

6. Should return: `200` success

### Option B: Using Shell

1. Backend service → **"Shell"** tab
2. Run:
   ```python
   python -c "
   import asyncio
   from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
   from sqlalchemy.orm import sessionmaker
   from services.auth.service import AuthService
   import os
   
   async def create():
       engine = create_async_engine(os.getenv('DATABASE_URL'))
       SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
       async with SessionLocal() as db:
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
   
   asyncio.run(create())
   "
   ```

---

## 🎉 SUCCESS!

### Your Live URLs:

| Service | URL | Test |
|---------|-----|------|
| **Frontend** | `https://nbfc-frontend-xxxx.onrender.com` | Open in browser |
| **Backend** | `https://nbfc-backend-xxxx.onrender.com` | Visit `/health` |
| **API Docs** | `https://nbfc-backend-xxxx.onrender.com/docs` | Try APIs |
| **Database** | Render Dashboard | View in dashboard |

### Login:
```
URL: https://nbfc-frontend-xxxx.onrender.com
Username: admin
Password: Admin@123
```

---

## ✅ Verification

Test these:

- [ ] Backend health: `/health` returns `{"status":"healthy"}`
- [ ] API docs: `/docs` loads with Swagger UI
- [ ] Frontend: Main page loads
- [ ] Login: Can login with admin/Admin@123
- [ ] Dashboard: Displays correctly
- [ ] No errors: Check browser console (F12)

---

## ⚠️ Free Tier Limitations

- **Services sleep** after 15 minutes of inactivity
- **First request** after sleep takes 30-60 seconds
- **750 hours/month** (enough for 1 service running 24/7)
- **Database**: 90 days retention, then deleted if inactive

**Good for**: Demos, testing, portfolio projects  
**Upgrade when**: You get real users or need 24/7 uptime

---

## 🔧 Troubleshooting

### Backend won't start:
1. Check build logs (Dashboard → Service → Logs)
2. Verify Python version is `3.11.9`
3. Check all environment variables are set
4. Verify DATABASE_URL is correct

### Frontend can't reach backend:
1. Check `NEXT_PUBLIC_API_URL` in frontend env
2. Must be: `https://your-backend.onrender.com/api/v1`
3. Include `/api/v1` at the end!

### Database connection error:
1. Verify database is running (Dashboard → Database)
2. Use **Internal Database URL** (not External)
3. Check DATABASE_URL env var in backend

### Services are slow:
- First request after 15 minutes of inactivity is slow
- This is normal on free tier
- Use UptimeRobot.com (free) to ping your service every 5 minutes

---

## 💡 Pro Tips

1. **Keep services awake**: Use UptimeRobot to ping every 5 minutes
2. **View logs**: Dashboard → Service → Logs tab
3. **Redeploy**: Push to GitHub = auto-redeploy
4. **Custom domain**: Possible on free tier (Settings → Custom Domain)
5. **Monitor**: Dashboard → Service → Metrics

---

## 💰 Cost

- **Current**: $0 (FREE)
- **Upgrade**: $7/month per service for no-sleep
- **Database**: FREE (no upgrade needed for small apps)

---

## 🚀 What's Next?

1. **Test thoroughly** - Click through all features
2. **Share with stakeholders** - Send them your frontend URL
3. **Get feedback** - See what users think
4. **Monitor usage** - Check Render dashboard regularly
5. **Consider upgrading** - When you outgrow free tier

---

## 📱 Share Your Success!

Your NBFC Suite is live on the internet!

**Share these links**:
- **Main App**: `https://nbfc-frontend-xxxx.onrender.com`
- **API Docs**: `https://nbfc-backend-xxxx.onrender.com/docs`

---

**Congratulations! Your app is deployed! 🎉**

---

**Last Updated**: July 6, 2026  
**Platform**: Render.com  
**Cost**: FREE  
**Credit Card**: Not Required  
**Time**: 20-30 minutes  
**Status**: ✅ WORKING
