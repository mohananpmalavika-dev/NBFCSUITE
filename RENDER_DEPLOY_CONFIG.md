# Render Deployment Configuration

## Quick Setup for 512MB Free Tier

### 1. Build Command
```bash
pip install -r backend/requirements.txt
```

### 2. Start Command
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### 3. Environment Variables

Copy and paste these into Render Dashboard → Environment:

```bash
# ============================================
# REQUIRED - Must Set These
# ============================================
DATABASE_URL=YOUR_POSTGRES_URL_HERE
JWT_SECRET_KEY=YOUR_RANDOM_SECRET_KEY_MIN_32_CHARS

# ============================================
# APPLICATION SETTINGS
# ============================================
APP_NAME=NBFC Financial Suite
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0

# ============================================
# DATABASE OPTIMIZATION (512MB RAM)
# ============================================
DB_ECHO=false
DB_POOL_SIZE=1
DB_MAX_OVERFLOW=1
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ============================================
# SECURITY
# ============================================
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# CORS (Update with your frontend URL)
# ============================================
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true

# ============================================
# API DOCUMENTATION
# ============================================
ENABLE_SWAGGER=true
ENABLE_REDOC=true

# ============================================
# CORE MODULES (ALWAYS ENABLED)
# ============================================
ENABLE_AUTH=true
ENABLE_DASHBOARD=true
ENABLE_MASTERDATA=true

# ============================================
# ESSENTIAL BUSINESS MODULES
# Enable only what you need
# ============================================
ENABLE_CUSTOMERS=true
ENABLE_LOANS=true
ENABLE_ACCOUNTING=false

# ============================================
# OPTIONAL MODULES (DISABLED FOR MEMORY)
# Set to true only if needed and memory permits
# ============================================
ENABLE_DEPOSITS=false
ENABLE_GOLD_LOANS=false
ENABLE_VEHICLE_LOANS=false
ENABLE_PROPERTY_LOANS=false
ENABLE_WORKFLOW=false
ENABLE_RULES_ENGINE=false
ENABLE_DECISION_ENGINE=false
ENABLE_NOTIFICATIONS=false
ENABLE_BUREAU_INTEGRATION=false
ENABLE_BANK_STATEMENT=false
ENABLE_OCR=false
ENABLE_EKYC=false
ENABLE_DIGILOCKER=false
ENABLE_COMPLIANCE=false
ENABLE_RISK_MANAGEMENT=false
ENABLE_TREASURY=false
ENABLE_ALM=false
ENABLE_BRANCH=false
ENABLE_HRMS=false
ENABLE_RECRUITMENT=false
ENABLE_ATTENDANCE=false
ENABLE_PAYROLL=false
ENABLE_TRAINING=false
ENABLE_FIXED_ASSETS=false
ENABLE_INVENTORY=false
ENABLE_CRM=false
ENABLE_CRM_OPPORTUNITIES=false
ENABLE_CRM_SALES=false
ENABLE_CRM_SERVICE=false
ENABLE_LEGAL=false
ENABLE_LITIGATION=false
ENABLE_LICENSE=false
ENABLE_DMS=false
ENABLE_FACILITY=false
ENABLE_REPORTING=false
ENABLE_INSURANCE=false
ENABLE_NACH=false
ENABLE_RESTRUCTURING=false
ENABLE_LOAN_INSURANCE=false

# ============================================
# MULTI-TENANCY
# ============================================
TENANT_ISOLATION_ENABLED=true

# ============================================
# FILE UPLOAD
# ============================================
MAX_UPLOAD_SIZE=5242880
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png
```

---

## Step-by-Step Deployment

### Step 1: Create PostgreSQL Database
1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `nbfcsuite-db`
3. Click **"Create Database"**
4. Copy the **External Database URL**

### Step 2: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name:** `nbfcsuite-backend`
   - **Environment:** `Python 3`
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`

### Step 3: Add Environment Variables
1. Click **"Advanced"**
2. Click **"Add Environment Variable"**
3. Copy the environment variables above
4. **Important:** Update these:
   - `DATABASE_URL`: Paste your PostgreSQL URL from Step 1
   - `JWT_SECRET_KEY`: Generate a random 32+ character string
   - `CORS_ORIGINS`: Set to your frontend URL (or keep `*` for testing)

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (3-5 minutes)
3. Check logs for any errors

### Step 5: Verify Deployment
1. Visit: `https://your-service.onrender.com/health`
   - Should return: `{"status": "healthy"}`

2. Visit: `https://your-service.onrender.com/docs`
   - Should show API documentation

---

## Monitoring

### Check Memory Usage
1. Go to your service in Render Dashboard
2. Click **"Metrics"** tab
3. Watch **"Memory"** graph
4. Should stay under 410MB (80% of 512MB)

### Check Logs
1. Click **"Logs"** tab
2. Look for:
   ```
   Loading core modules...
   Loading masterdata module...
   Loading customer module...
   Loading loan module...
   Total routers loaded: X
   ```

### Expected Startup Logs
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:backend.main: Loading API routers based on enabled features...
INFO:backend.shared.conditional_imports: Loading core modules...
INFO:backend.shared.conditional_imports: Loading masterdata module...
INFO:backend.shared.conditional_imports: Loading customer module...
INFO:backend.shared.conditional_imports: Loading loan module...
INFO:backend.shared.conditional_imports: Total routers loaded: 6
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:PORT
```

---

## Troubleshooting

### Problem: Out of Memory Error
**Solution:**
1. Make sure only essential modules are enabled
2. Check `DB_POOL_SIZE=1`
3. Check `LOG_LEVEL=WARNING`
4. Disable `ENABLE_ACCOUNTING` if not needed

### Problem: Port Binding Error
**Solution:**
- Ensure start command uses `$PORT` variable (not hardcoded 8000)
- Render automatically sets this

### Problem: Database Connection Error
**Check:**
1. `DATABASE_URL` is correctly set
2. Database is running (check PostgreSQL service)
3. Database URL format: `postgresql://user:pass@host:5432/dbname`

### Problem: App Crashes on Startup
**Check Logs For:**
1. Import errors → missing dependencies
2. Configuration errors → wrong env vars
3. Database errors → check connection

---

## Scaling Options

### When to Upgrade?

**Upgrade to Starter ($7/month) when:**
- Need 24/7 uptime (free tier sleeps after 15min)
- Need more modules (8-15 modules)
- Have real users

**Upgrade to Standard ($25/month) when:**
- Need all features
- 500+ active users
- Production workloads

**Upgrade to Pro ($85/month) when:**
- 2000+ active users
- Mission-critical
- Need high availability

---

## Post-Deployment Checklist

- [ ] Health endpoint responds
- [ ] API docs accessible
- [ ] Database connection works
- [ ] Can create/login user
- [ ] Memory usage < 410MB
- [ ] No errors in logs
- [ ] Frontend can connect (update CORS if needed)
- [ ] Test core API endpoints

---

## Useful Commands

### Generate JWT Secret
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Test Database Connection Locally
```bash
python -c "from backend.shared.database.connection import engine; print('Connected!' if engine else 'Failed')"
```

### Check Enabled Modules Locally
```bash
python -c "from backend.shared.conditional_imports import get_enabled_routers; print(f'{len(get_enabled_routers())} modules enabled')"
```

---

## Support Resources

- **Render Docs:** https://render.com/docs
- **Render Status:** https://status.render.com/
- **Community:** https://community.render.com/

---

## Quick Reference

| Setting | Value | Purpose |
|---------|-------|---------|
| DB_POOL_SIZE | 1 | Minimize memory |
| DB_MAX_OVERFLOW | 1 | Limit connections |
| LOG_LEVEL | WARNING | Reduce log volume |
| ENABLE_* | false | Disable unused modules |
| Instance Type | Free | 512MB RAM |

---

**Ready to Deploy!** 🚀

Follow the steps above and your NBFC Suite will be running on Render's free tier with optimized memory usage.
