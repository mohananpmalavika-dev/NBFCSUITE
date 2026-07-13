# 🚀 Deploy Minimal Version - Step by Step

## What I've Created

✅ **`backend/main_minimal.py`** - Memory-optimized version with only core modules

### Modules Included (Only These Load):
1. ✅ **Authentication** - User login, JWT tokens, permissions
2. ✅ **Dashboard** - Main dashboard statistics
3. ✅ **Master Data** - Countries, banks, currencies, etc.
4. ✅ **Customers** - Customer management (CIF)
5. ✅ **Loans** - Loan origination and management

### Modules NOT Loaded (Saves ~300MB):
❌ Accounting, Deposits, Gold Loans, HRMS, CRM, Treasury, Compliance, Legal, etc.

**Expected Memory Usage:** ~200-250MB (well under 512MB limit!)

---

## How to Deploy on Render

### Step 1: Update Start Command

1. Go to **Render Dashboard** (https://dashboard.render.com)
2. Click on your web service
3. Go to **Settings** tab
4. Find **Start Command** section
5. Change from:
   ```
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
   
   To:
   ```
   uvicorn backend.main_minimal:app --host 0.0.0.0 --port $PORT
   ```

6. Click **Save Changes**

### Step 2: Trigger Deploy

1. Go to **Manual Deploy** tab
2. Click **Deploy latest commit**
3. Or commit and push if you have auto-deploy enabled

### Step 3: Monitor Deployment

Watch the logs for:

```
🚀 Starting NBFC Financial Suite API (MINIMAL MODE)...
Environment: production
Modules Loaded: Core, MasterData, Customers, Loans ONLY
✅ Core routers registered: Auth, Dashboard, MasterData, Customers, Loans
```

### Step 4: Verify Success

Check for:
- ✅ No "Out of memory" error
- ✅ Application starts successfully
- ✅ Health check returns 200 OK

Test the endpoints:
- **Health:** https://your-app.onrender.com/health
- **Docs:** https://your-app.onrender.com/docs
- **Root:** https://your-app.onrender.com/

---

## Expected Results

### Memory Usage
```
Before (main.py):      ~525MB ❌ Out of memory
After (main_minimal):  ~220MB ✅ Under limit
Savings:               ~305MB ✅ 58% reduction!
```

### Available APIs
```
✅ Authentication       /api/v1/auth/*
✅ Dashboard            /api/v1/dashboard/*
✅ Master Data          /api/v1/masterdata/*
✅ Customers           /api/v1/customers/*
✅ Loans               /api/v1/loans/*
```

### Unavailable APIs (For Now)
```
❌ Accounting
❌ Deposits
❌ HRMS
❌ CRM
❌ Treasury
... (all other modules)
```

---

## Adding More Modules Later

Once deployed successfully, you can gradually add modules:

### Option 1: Add One Module at a Time

Edit `main_minimal.py` and add imports + routers:

```python
# Add at model import section
from backend.shared.database.accounting_models import (
    ChartOfAccounts, JournalEntry, JournalEntryLine
)

# Add at router import section
from backend.services.accounting.router import router as accounting_router

# Add at router registration
app.include_router(accounting_router, prefix="/api/v1", tags=["Accounting"])
```

Commit, push, and monitor memory usage.

### Option 2: Switch Back to Full Version

When you upgrade Render plan to 1GB+ RAM:

1. Change start command back to:
   ```
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```

2. All modules will be available again

---

## Troubleshooting

### If Deploy Still Fails with Memory Error

1. **Check Start Command** - Make sure it says `main_minimal:app`
2. **Check Logs** - Look for which module is consuming memory
3. **Further Optimization** - Remove customer bureau/ekyc routers temporarily

### If Specific Features Don't Work

Normal! Those modules aren't loaded. You can:
1. Add that specific module to `main_minimal.py`
2. Or upgrade to full version with more RAM

### If You Need a Missing Module Urgently

Tell me which one and I'll add it to `main_minimal.py` for you!

---

## Testing Checklist

After deployment, test these:

- [ ] Can access docs at `/docs`
- [ ] Can login via `/api/v1/auth/login`
- [ ] Dashboard loads at `/api/v1/dashboard`
- [ ] Can create customer at `/api/v1/customers`
- [ ] Can create loan at `/api/v1/loans`
- [ ] Memory stays under 400MB (check logs/metrics)

---

## Gradual Module Addition Strategy

### Week 1: Core Only (Current)
- Memory: ~220MB
- Modules: Auth, Dashboard, MasterData, Customers, Loans

### Week 2: Add Customer Enhancements
```python
# Add customer timeline, bureau, ekyc
from backend.services.customer.timeline_router import router as customer_timeline_router
from backend.services.customer.bureau_router import router as customer_bureau_router
from backend.services.customer.ekyc_router import router as customer_ekyc_router

app.include_router(customer_timeline_router, prefix="/api/v1", tags=["Customer Timeline"])
app.include_router(customer_bureau_router, prefix="/api/v1", tags=["Credit Bureau"])
app.include_router(customer_ekyc_router, prefix="/api/v1", tags=["eKYC"])
```
- Memory: ~250MB

### Week 3: Add Accounting
```python
from backend.shared.database.accounting_models import (
    ChartOfAccounts, JournalEntry, JournalEntryLine, GeneralLedger
)
from backend.services.accounting.router import router as accounting_router
app.include_router(accounting_router, prefix="/api/v1", tags=["Accounting"])
```
- Memory: ~280MB

Continue this pattern, monitoring memory after each addition.

---

## Quick Commands Reference

### Check Current Start Command
```bash
# In Render dashboard, Settings > Start Command
```

### View Memory Usage in Logs
```bash
# Look for lines like:
# Memory usage: 245MB / 512MB
```

### Revert to Full Version
```bash
# Change start command to:
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

---

## 🎉 Success Criteria

You'll know it worked when:
1. ✅ Deployment completes without "Out of memory" error
2. ✅ App starts and responds to health checks
3. ✅ Can login and access core APIs
4. ✅ Memory usage shows ~200-250MB in metrics

---

## Need Help?

If anything goes wrong:
1. Check the deployment logs in Render
2. Verify the start command is correct
3. Test the health endpoint
4. Ask me for help!

**Ready to deploy? Follow Step 1 above!** 🚀
