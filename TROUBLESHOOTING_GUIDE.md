# Troubleshooting Guide - Post Import Fix

## Quick Diagnostic

If deployment fails after the import fix, use this guide to diagnose and resolve issues.

---

## Scenario 1: Still Getting Import Errors ❌

### Symptoms
```
ModuleNotFoundError: No module named 'X'
ImportError: cannot import name 'Y'
```

### Diagnosis
```bash
# Check if all files were committed
git status

# Check recent commits
git log -1 --stat
```

### Solution
```bash
# If files weren't committed:
git add backend/services/
git commit -m "fix: correct import paths"
git push origin main

# If different module is missing, check the actual error:
# Look at the file path in the error and fix that import
```

---

## Scenario 2: Database Connection Error 🗄️

### Symptoms
```
could not connect to server
could not translate host name
Connection refused
```

### Diagnosis
- Check Render dashboard → Database service
- Verify DATABASE_URL is set

### Solution A: Check Environment Variables
1. Go to Render dashboard
2. Select `nbfc-backend` service
3. Go to "Environment" tab
4. Verify `DATABASE_URL` is set (should be auto-populated from database)

### Solution B: Database Not Running
1. Check database service status
2. Restart database service if stopped
3. Wait for database to be fully online
4. Redeploy backend service

---

## Scenario 3: Migration/Alembic Errors 🔄

### Symptoms
```
alembic upgrade head failed
revision not found
Can't locate revision
```

### Diagnosis
```bash
# Check alembic version
cd backend
alembic current
alembic history
```

### Solution A: Skip Pre-Deploy Command
In `render.yaml`, comment out or remove:
```yaml
# preDeployCommand: cd backend && alembic upgrade head
```

### Solution B: Force Table Recreation
Set environment variable in Render:
```
DROP_ALL_TABLES=true
```
**⚠️ WARNING**: This will delete all data!

### Solution C: Skip Table Creation
If tables already exist:
```
SKIP_TABLE_CREATION=true
```

---

## Scenario 4: Foreign Key / Table Errors 🔗

### Symptoms
```
NoReferencedTableError
table "xyz" does not exist
foreign key constraint
```

### Diagnosis
- Database has old tables from previous schema
- New tables reference missing tables

### Solution A: Clean Slate (Development Only)
```
DROP_ALL_TABLES=true
SKIP_TABLE_CREATION=false
```
Redeploy to recreate all tables fresh.

### Solution B: Skip Table Creation
If you have a database backup or production data:
```
SKIP_TABLE_CREATION=true
```

### Solution C: Manual Migration
```bash
# Connect to database
# Drop specific problematic tables
# Let Render recreate them
```

---

## Scenario 5: Memory Errors (Free Tier) 💾

### Symptoms
```
Killed
Out of memory
Cannot allocate memory
Process exited unexpectedly
```

### Diagnosis
- Check Render logs for "Killed" message
- Free tier has 512MB RAM limit

### Solution
Already implemented in `main_minimal.py`:
- Only core modules loaded
- ~200MB memory usage

If still exceeding:
1. Check if conditional imports are working
2. Verify `main_minimal.py` is being used
3. Check `startCommand` in `render.yaml`:
   ```yaml
   startCommand: uvicorn backend.main_minimal:app --host 0.0.0.0 --port $PORT
   ```

---

## Scenario 6: Port Binding Issues 🔌

### Symptoms
```
No open ports detected
Failed to bind to port
Address already in use
```

### Diagnosis
- Render expects app to bind to $PORT
- Default Render port: 10000

### Solution
Verify `startCommand` includes `--port $PORT`:
```yaml
startCommand: uvicorn backend.main_minimal:app --host 0.0.0.0 --port $PORT
```

---

## Scenario 7: CORS Errors 🌐

### Symptoms
```
CORS policy blocked
Access-Control-Allow-Origin missing
```

### Diagnosis
- Frontend can't connect to backend
- CORS origins not configured

### Solution
Check/update environment variable:
```
CORS_ORIGINS=https://nbfc-frontend.onrender.com,http://localhost:3000
```

In code (`main_minimal.py`), verify:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Scenario 8: Health Check Failing ❤️

### Symptoms
```
Health check failed
/health endpoint not responding
```

### Diagnosis
```bash
# Test health endpoint directly
curl https://nbfc-backend.onrender.com/health
```

### Solution A: Verify Health Endpoint
Check `main_minimal.py` has:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Solution B: Update render.yaml
```yaml
healthCheckPath: /health
```

### Solution C: Disable Health Check (Temporarily)
In Render dashboard:
1. Go to service settings
2. Set health check path to empty
3. Redeploy

---

## Scenario 9: Dependency Installation Errors 📦

### Symptoms
```
ERROR: Could not find a version that satisfies
ERROR: No matching distribution found
pip install failed
```

### Diagnosis
- Package not available for Python 3.11
- Conflicting dependencies

### Solution A: Check Python Version
In `render.yaml`:
```yaml
envVars:
  - key: PYTHON_VERSION
    value: 3.11.9
```

### Solution B: Update Requirements
```bash
# Check requirements file
cat backend/requirements.render.txt

# Test locally
pip install -r backend/requirements.render.txt
```

### Solution C: Use Different Requirements File
In `render.yaml`:
```yaml
buildCommand: pip install -r backend/requirements.linux.txt
```

---

## Scenario 10: Build Timeout ⏱️

### Symptoms
```
Build exceeded time limit
Build failed: timeout
```

### Diagnosis
- Build takes too long (>10 minutes on free tier)
- Installing too many packages

### Solution A: Optimize Build Command
```yaml
buildCommand: |
  find . -type d -name __pycache__ -exec rm -rf {} + || true &&
  pip install --upgrade pip &&
  pip install --no-cache-dir -r backend/requirements.render.txt
```

### Solution B: Simplify Dependencies
Use minimal requirements file with only essential packages.

---

## General Debugging Commands

### Check Service Logs
```bash
# In Render dashboard
1. Go to nbfc-backend service
2. Click "Logs" tab
3. Look for errors in red
```

### Test Locally
```bash
# Run the exact startup command locally
cd c:\NBFCSUITE
uvicorn backend.main_minimal:app --host 0.0.0.0 --port 8000
```

### Verify Environment
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Test imports
python verify_imports.py
```

### Manual Deploy Test
```bash
# Test build command locally
pip install --no-cache-dir -r backend/requirements.render.txt

# Test start command
uvicorn backend.main_minimal:app --host 0.0.0.0 --port 8000
```

---

## Emergency Rollback

If everything fails and you need to rollback:

```bash
# Revert the last commit
git revert HEAD

# Or reset to previous commit
git reset --hard HEAD~1

# Force push (use with caution)
git push origin main --force
```

---

## Getting More Help

### Log Analysis
1. Copy full error from Render logs
2. Look for the root cause (first error)
3. Check error type (Import, Database, Memory, etc.)
4. Use corresponding section in this guide

### Environment Check
```bash
# List all environment variables in Render dashboard
# Compare with .env.example
# Ensure all required vars are set
```

### Database Check
```bash
# In Render dashboard
1. Check database service status
2. Check connection string format
3. Test database connectivity
```

---

## Success Checklist

After resolving issues, verify:

- [ ] Service status: "Live" ✅
- [ ] Health check: Passing ✅
- [ ] No errors in logs ✅
- [ ] API docs accessible at `/docs` ✅
- [ ] Test endpoint responds ✅
- [ ] Frontend can connect ✅

---

**Last Updated**: July 16, 2026
**Related Docs**: 
- DEPLOY_AFTER_FIX.md
- DEPLOYMENT_IMPORT_FIX_COMPLETE.md
- IMPORT_FIX_SUMMARY.md
