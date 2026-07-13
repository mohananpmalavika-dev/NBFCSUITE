# How to Apply Memory Optimization

## OPTION A: Quick Fix (Try This First!)

### Step 1: Add Environment Variables to Render

1. Go to your Render dashboard
2. Click on your web service
3. Go to "Environment" tab
4. Add these variables:

```
ENABLE_ACCOUNTING=false
ENABLE_DEPOSITS=false
ENABLE_GOLD_LOANS=false
ENABLE_VEHICLE_LOANS=false
ENABLE_PROPERTY_LOANS=false
ENABLE_WORKFLOW=false
ENABLE_RULES_ENGINE=false
ENABLE_DECISION_ENGINE=false
ENABLE_BUREAU_INTEGRATION=false
ENABLE_COMPLIANCE=false
ENABLE_TREASURY=false
ENABLE_HRMS=false
ENABLE_CRM=false
ENABLE_LEGAL=false
ENABLE_DMS=false
ENABLE_FACILITY=false
ENABLE_REPORTING=false
ENABLE_INSURANCE=false
DB_POOL_SIZE=2
DB_MAX_OVERFLOW=3
```

### Step 2: Manual Deploy
Click "Manual Deploy" → "Deploy latest commit"

### Step 3: Check Logs
Watch for:
- Memory usage in logs
- "Out of memory" errors
- Successful startup

**Expected Result:** Memory usage should drop by ~100-150MB

---

## OPTION B: Code Modification (If Option A Fails)

This requires modifying `main.py` to conditionally load routers.

### Files to Modify:

1. **backend/shared/config.py** ✅ (Already created with feature flags)
2. **backend/main.py** (Need to add conditional imports)

### The Change Pattern:

Replace unconditional imports:
```python
from backend.services.accounting.router import router as accounting_router
app.include_router(accounting_router, prefix="/api/v1", tags=["Accounting"])
```

With conditional imports:
```python
if settings.ENABLE_ACCOUNTING:
    from backend.services.accounting.router import router as accounting_router
    app.include_router(accounting_router, prefix="/api/v1", tags=["Accounting"])
```

### Sections to Modify in main.py:

1. **Model Imports (Lines 30-250)** - Wrap in `if` statements
2. **Router Imports (Lines 790-890)** - Wrap in `if` statements  
3. **Router Registration (Lines 950-1200)** - Wrap in `if` statements

---

## OPTION C: Create Minimal main.py

Create a new file `backend/main_minimal.py` with only core modules, then update Render to use it.

### Advantages:
- Keep original main.py intact
- Easy to switch back
- Test minimal version separately

### Steps:

1. I create `main_minimal.py` with only:
   - Auth
   - Dashboard
   - Customers
   - Loans
   - Master Data

2. Update `render.yaml` or start command:
   ```yaml
   startCommand: uvicorn backend.main_minimal:app --host 0.0.0.0 --port $PORT
   ```

3. Deploy and test

**Expected Memory:** ~200-250MB (well under 512MB!)

---

## Which Option Should You Choose?

### Choose Option A if:
- ✅ You want quickest solution
- ✅ You're okay with partial memory savings
- ✅ You might need all modules later
- **Effort:** 5 minutes
- **Savings:** ~100-150MB

### Choose Option B if:
- ✅ Option A didn't work
- ✅ You want maximum memory savings
- ✅ You know which modules you need
- **Effort:** 30-60 minutes (I can help!)
- **Savings:** ~200-300MB

### Choose Option C if:
- ✅ Option A didn't work
- ✅ You only need core functionality
- ✅ You want simplest long-term solution
- **Effort:** 15 minutes (I create the file)
- **Savings:** ~300-350MB

---

## My Recommendation

**Try them in order:**

1. **Start with Option A** (5 min) → Check if memory is under 512MB
2. **If that fails, try Option C** (15 min) → Minimal main.py
3. **If you need more modules, do Option B** (60 min) → Conditional loading

---

## What Would You Like Me to Do?

I can help you with:

### ✅ Option A (Immediate)
- I'll give you the exact list of environment variables to add
- You paste them in Render and redeploy
- We check logs together

### ✅ Option C (Quick Win)
- I'll create `main_minimal.py` with only core modules
- You update the start command
- Deploy and test

### ✅ Option B (Maximum Control)
- I'll modify your main.py with conditional loading
- You review the changes
- Deploy with full control over which modules load

**Which option would you like to try first?**
