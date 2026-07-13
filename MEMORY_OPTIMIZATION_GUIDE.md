# Memory Optimization Guide for Render Free Tier

## Quick Start - Deploy with Minimal Memory

### Step 1: Update Environment Variables on Render

Add these environment variables to your Render service:

```env
# Core Settings (Keep These)
ENABLE_AUTH=true
ENABLE_DASHBOARD=true
ENABLE_CUSTOMERS=true
ENABLE_LOANS=true
ENABLE_MASTERDATA=true

# Disable Heavy Modules (Set to false)
ENABLE_ACCOUNTING=false
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

# Database Pool Settings (Optimized for Free Tier)
DB_POOL_SIZE=2
DB_MAX_OVERFLOW=3
```

### Step 2: Create Conditional Router Loading in main.py

The `config.py` file I created has all the feature flags. Now we need to modify `main.py` to only load routers when their feature flag is enabled.

## Memory Savings Breakdown

| Module Category | Est. Memory | Status | Savings |
|----------------|-------------|--------|---------|
| Core (Auth, Dashboard, Customers, Loans) | ~200MB | ✅ Keep | 0MB |
| Accounting | ~30MB | ❌ Disable | 30MB |
| Deposits | ~25MB | ❌ Disable | 25MB |
| Gold/Vehicle/Property Loans | ~40MB | ❌ Disable | 40MB |
| Workflow & Rules Engine | ~30MB | ❌ Disable | 30MB |
| Integration Services | ~35MB | ❌ Disable | 35MB |
| HRMS Full Suite | ~50MB | ❌ Disable | 50MB |
| CRM Full Suite | ~40MB | ❌ Disable | 40MB |
| Legal & Compliance | ~25MB | ❌ Disable | 25MB |
| Treasury & ALM | ~30MB | ❌ Disable | 30MB |
| Facility & DMS | ~20MB | ❌ Disable | 20MB |
| **Total Potential Savings** | | | **~325MB** |

**Result:** From ~525MB → **~200MB** (fits comfortably in 512MB free tier!)

## Implementation Options

### Option A: Quick Fix - Environment Variables Only (Recommended)

**Pros:**
- No code changes needed
- Easy to toggle features
- Instant deployment

**Cons:**
- All models still loaded into memory (can't fully disable)
- Saves ~100-150MB (may not be enough)

**Steps:**
1. Add all the environment variables above to Render
2. Redeploy
3. Monitor memory usage

### Option B: Code Modification - Conditional Import (Maximum Savings)

**Pros:**
- Maximum memory savings (~325MB)
- Models not loaded if feature disabled
- Fits easily in free tier

**Cons:**
- Requires code changes to main.py
- More complex to implement

**Steps:**
1. Modify `main.py` to wrap all imports in `if settings.ENABLE_*` checks
2. Wrap `app.include_router()` calls in same checks
3. Deploy modified version

## Option B - Implementation Example

Here's how to modify `main.py` for conditional loading:

```python
# In main.py, replace static imports with conditional ones:

# Before:
from backend.services.accounting.router import router as accounting_router
app.include_router(accounting_router, prefix="/api/v1", tags=["Accounting"])

# After:
if settings.ENABLE_ACCOUNTING:
    from backend.services.accounting.router import router as accounting_router
    app.include_router(accounting_router, prefix="/api/v1", tags=["Accounting"])
```

## Quick Test - Verify Memory Usage

After deploying, check memory:

```bash
# In Render shell or logs
ps aux | grep uvicorn
```

Look for the RSS (Resident Set Size) column - should be under 400MB.

## Gradual Enablement Strategy

Once deployed with minimal modules, gradually enable more:

### Week 1: Core Operations
- ✅ Auth, Dashboard, Customers, Loans, Master Data
- Memory: ~200MB

### Week 2: Add Accounting
- ✅ Enable ENABLE_ACCOUNTING=true
- Memory: ~230MB

### Week 3: Add Deposits
- ✅ Enable ENABLE_DEPOSITS=true
- Memory: ~255MB

### Week 4: Add Specialized Loans
- ✅ Enable ENABLE_GOLD_LOANS=true
- Memory: ~275MB

Continue this pattern, monitoring memory after each addition.

## Monitoring & Alerts

Set up alerts in Render:
1. Memory usage > 450MB = Warning
2. Memory usage > 480MB = Critical
3. Memory usage > 500MB = Disable last enabled module

## Rollback Plan

If memory issues persist:

1. **Immediate:** Disable all optional modules
2. **Short-term:** Only enable 2-3 most critical modules
3. **Long-term:** Upgrade to Starter plan ($7/month)

## Alternative Solutions

### 1. Multi-Service Architecture
Split into multiple Render services:
- **Service 1:** Core (Auth, Customers, Loans) - Free tier
- **Service 2:** HRMS - Free tier
- **Service 3:** CRM - Free tier

Each stays under 512MB, but you manage 3 deployments.

### 2. Serverless Functions
Move heavy operations to:
- AWS Lambda (free tier: 1M requests/month)
- Vercel Functions (free tier included)
- Cloudflare Workers

### 3. Optimize Database Queries
Reduce model loading:
- Use `defer()` for large columns
- Lazy load relationships
- Query only needed fields

## Expected Results

### Before Optimization
```
Memory Usage: 525MB
Status: ❌ Out of Memory
Deploy: Failed
```

### After Option A (Environment Variables)
```
Memory Usage: ~380MB
Status: ✅ Running
Deploy: Success
Modules: Core only
```

### After Option B (Conditional Imports)
```
Memory Usage: ~200-250MB
Status: ✅ Running
Deploy: Success
Modules: Core + 2-3 additional
Headroom: 260MB available
```

## Next Steps

1. **Try Option A first** (easiest)
   - Add environment variables to Render
   - Redeploy
   - Check logs for memory usage

2. **If Option A fails, implement Option B**
   - I can help modify main.py
   - Add conditional imports
   - Test locally first

3. **If still over limit**
   - Consider multi-service architecture
   - Or upgrade to paid plan ($7/month)

## Need Help?

I can create the modified `main.py` with conditional loading if Option A doesn't work. Just let me know!

---

**Recommendation:** Start with Option A (environment variables). It's the quickest test and might be enough to get under 512MB.
