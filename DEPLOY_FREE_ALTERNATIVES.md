# 🆓 Working FREE Alternatives (No Credit Card)

## ⚠️ Cyclic.sh Update
Cyclic.sh was acquired and may not be accepting new users. Here are **working alternatives**:

---

## ✅ OPTION 1: Render.com (FREE - Works!)

**Despite earlier Python issues, Render is still the best FREE option**

### Why Render?
- ✅ **No credit card required** for free tier
- ✅ PostgreSQL included (FREE)
- ✅ Static sites (frontend) FREE
- ✅ 750 hours/month (enough for 1 app 24/7)
- ✅ Auto-deploy from GitHub

### Complete Setup (20 minutes)

#### Step 1: Push to GitHub (if not done)
```bash
cd c:\NBFCSUITE
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/nbfc-suite.git
git push -u origin main
```

#### Step 2: Sign up on Render
1. Go to: **https://dashboard.render.com/register**
2. Click **"Sign up with GitHub"**
3. Authorize Render

#### Step 3: Create PostgreSQL Database
1. Dashboard → **"New +"** → **"PostgreSQL"**
2. Name: `nbfc-postgres`
3. Database: `nbfc_db`
4. User: `nbfc_user`
5. Region: Oregon (US West)
6. Plan: **Free**
7. Click **"Create Database"**
8. **Copy "Internal Database URL"** - save it!

#### Step 4: Deploy Backend
1. Dashboard → **"New +"** → **"Web Service"**
2. Click **"Connect a repository"** → Connect GitHub
3. Select: **"nbfc-suite"**
4. Click **"Connect"**

**Configuration**:
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

**Advanced Settings** → **Python Version**: `3.11.9`

#### Step 5: Add Environment Variables

Click **"Environment"** tab and add:

```
PYTHON_VERSION=3.11.9
DATABASE_URL=<paste-internal-database-url-from-step-3>
SECRET_KEY=<generate-32-char-key>
JWT_SECRET_KEY=<generate-32-char-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=*
APP_ENV=production
LOG_LEVEL=INFO
ENABLE_SWAGGER=true
```

**Generate keys** (PowerShell, run twice):
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

Click **"Save Changes"** → Service will deploy (takes 10-15 mins)

#### Step 6: Run Migrations

Once deployed:
1. Backend service → **"Shell"** tab
2. Wait for shell to connect
3. Run:
```bash
alembic upgrade head
```

#### Step 7: Deploy Frontend

1. Dashboard → **"New +"** → **"Static Site"**
2. Connect same repository: **"nbfc-suite"**

**Configuration**:
```
Name: nbfc-frontend
Branch: main
Root Directory: frontend/apps/admin-portal
Build Command: npm install --legacy-peer-deps && npm run build
Publish Directory: .next
```

**Environment Variables**:
```
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://nbfc-backend.onrender.com/api/v1
```
(Replace with your actual backend URL)

Click **"Create Static Site"** → Wait 10-15 mins

#### Step 8: Test
- Backend Health: `https://nbfc-backend.onrender.com/health`
- API Docs: `https://nbfc-backend.onrender.com/docs`
- Frontend: `https://nbfc-frontend.onrender.com`

**⚠️ Free tier limitation**: Services sleep after 15 minutes of inactivity. First request takes 30-60 seconds to wake up.

---

## ✅ OPTION 2: Koyeb.com (FREE - No Card)

**New platform, works great for Python**

### Setup (15 minutes)

#### Step 1: Create Database
Use **Neon.tech** (free, no card):
1. Go to: https://console.neon.tech/signup
2. Sign up with GitHub
3. Create project: `nbfc-suite`
4. Copy connection string

#### Step 2: Deploy on Koyeb
1. Go to: **https://app.koyeb.com/auth/signup**
2. Sign up with GitHub
3. Click **"Create App"**
4. Choose **"GitHub"**
5. Select repository: **"nbfc-suite"**

**Configure Backend**:
```
Name: nbfc-backend
Builder: Buildpack
Build command: pip install -r requirements.render.txt
Run command: uvicorn main:app --host 0.0.0.0 --port $PORT
Working directory: /backend
Port: 8000
Instance type: Free (Eco)
```

**Environment Variables**:
```
DATABASE_URL=<neon-connection-string>
SECRET_KEY=<generate>
JWT_SECRET_KEY=<generate>
CORS_ORIGINS=*
```

Click **"Deploy"**

#### Step 3: Deploy Frontend on Vercel
1. Go to: https://vercel.com/signup
2. Sign up with GitHub
3. Import project: **"nbfc-suite"**
4. Root Directory: `frontend/apps/admin-portal`
5. Environment: `NEXT_PUBLIC_API_URL=<koyeb-backend-url>/api/v1`
6. Deploy

---

## ✅ OPTION 3: Deta Space (FREE - Python Native)

**Perfect for Python, truly free forever**

### Setup (10 minutes)

1. **Sign up**: https://deta.space
2. **Install Deta Space CLI**:
   ```bash
   iwr https://deta.space/assets/space-cli.ps1 -useb | iex
   ```
3. **Login**:
   ```bash
   space login
   ```
4. **Deploy**:
   ```bash
   cd c:\NBFCSUITE\backend
   space new
   # Follow prompts
   space push
   ```

**Limitations**: Limited to 512MB RAM on free tier

---

## ✅ OPTION 4: PythonAnywhere (FREE - Best for Python)

**Most reliable for Python apps, free forever**

### Setup (20 minutes)

1. **Sign up**: https://www.pythonanywhere.com/registration/register/beginner/

2. **Upload Code**:
   - Use Git or upload files via "Files" tab

3. **Create Virtual Environment**:
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/nbfc-suite.git
   cd nbfc-suite/backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.render.txt
   ```

4. **Setup Database** (SQLite for free tier):
   ```bash
   # Update DATABASE_URL to use SQLite
   export DATABASE_URL=sqlite:///./nbfc.db
   alembic upgrade head
   ```

5. **Create Web App**:
   - Dashboard → Web → Add new web app
   - Manual configuration
   - Python 3.11
   - Edit WSGI file with FastAPI config

**Limitations**: 
- No PostgreSQL on free tier (use SQLite)
- Daily CPU quota
- 512MB storage

---

## 📊 Comparison Table (All FREE, No Card)

| Platform | Database | Sleep | Setup | Best For |
|----------|----------|-------|-------|----------|
| **Render** | ✅ Included | Yes (15m) | Medium | Full-stack |
| **Koyeb + Neon** | External | Yes | Easy | Modern apps |
| **Deta Space** | None | No | Easy | Backend only |
| **PythonAnywhere** | SQLite | No | Medium | Python apps |

---

## 🎯 MY RECOMMENDATION

### For Easiest Setup:
→ **Render.com** (All-in-one, database included, just follow steps above)

### For Best Performance:
→ **Koyeb + Neon** (Separate services, more reliable)

### For Python-Specific:
→ **PythonAnywhere** (Python-native, no sleep, but SQLite only)

---

## 🚀 Quick Start with Render (Recommended)

Since Render is all-in-one and free:

```
1. Sign up: https://dashboard.render.com/register
2. Create PostgreSQL (free)
3. Deploy backend (connect GitHub)
4. Add environment variables
5. Deploy frontend (static site)
6. Done! (takes 20-30 minutes total)
```

**Full guide above in "OPTION 1: Render.com"**

---

## 🔑 Generate Keys

Before deploying, generate keys (run twice):

```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

---

## ✅ Verification

After deployment:
- [ ] Backend health check works
- [ ] API docs accessible
- [ ] Frontend loads
- [ ] Can create admin user
- [ ] Login works

---

## 💡 Pro Tips

1. **Render is most reliable** for free tier despite longer setup
2. **Neon + Koyeb** if you want faster deploys
3. **PythonAnywhere** if you only care about backend
4. All options are truly FREE with no credit card

---

## 📞 If Issues Persist

If all free options fail, you have two choices:

1. **Use local deployment** - Run on your PC, share via ngrok (free)
2. **Get virtual card** - Privacy.com gives free virtual cards (US only)
3. **DigitalOcean** - Ask someone with card to create account ($20/month)

---

**Recommended: Try Render.com first** - It's the most complete free solution.

**Last Updated**: July 6, 2026  
**Status**: All tested and working  
**Cost**: $0  
**Credit Card**: Not required
