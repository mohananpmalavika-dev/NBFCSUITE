# Memory Optimization Plan for Render Free Tier

## Current Issue
Application uses >512MB RAM, exceeding Render's free tier limit.

## Root Cause Analysis

### Main Memory Consumers in `backend/main.py`:
1. **36+ module imports at startup** - Loading ALL models from ALL modules
2. **All SQLAlchemy models loaded into memory** - Even unused ones
3. **Heavy middleware stack**
4. **All routers imported eagerly**

## Optimization Strategy

### Phase 1: Lazy Model Loading (Quick Win - Est. 100-150MB savings)
**Current:** All 36 model modules imported at startup  
**Solution:** Only import core models, lazy-load others

### Phase 2: Conditional Router Loading (Est. 50-100MB savings)
**Current:** All routers loaded regardless of usage  
**Solution:** Load only essential routers, make others optional

### Phase 3: Database Connection Optimization (Est. 20-30MB savings)
**Current:** Default connection pool settings  
**Solution:** Reduce pool size for free tier

### Phase 4: Middleware Optimization (Est. 10-20MB savings)
**Current:** All middleware loaded  
**Solution:** Disable non-essential middleware in production

## Implementation

### Step 1: Create Minimal Main.py
Load only essential modules needed for API to start:
- Core models (User, Tenant, Role)
- Authentication
- 2-3 most critical business modules

### Step 2: Environment-Based Loading
Add environment variable to control which modules load:
```python
ENABLE_HRMS = os.getenv("ENABLE_HRMS", "false") == "true"
ENABLE_CRM = os.getenv("ENABLE_CRM", "false") == "true"
# Only load if enabled
```

### Step 3: Optimize Database Settings
Reduce connection pool for free tier:
```python
pool_size=2  # down from 5
max_overflow=3  # down from 10
```

### Step 4: Add Memory Profiling
Monitor memory usage to verify savings

## Files to Modify

1. ✅ `backend/main.py` - Lazy loading logic
2. ✅ `backend/shared/database/connection.py` - Pool size reduction
3. ✅ `backend/shared/config.py` - Add feature flags
4. ✅ Create `backend/main_minimal.py` - Lightweight version for testing

## Expected Results

### Before Optimization
- Memory: >512MB
- Status: ❌ Out of memory

### After Phase 1
- Memory: ~380-420MB
- Status: ✅ Should fit in 512MB

### After All Phases
- Memory: ~300-350MB
- Status: ✅ Comfortable margin

## Risk Assessment

**Low Risk:**
- Lazy loading (only loads when needed)
- Database pool reduction (may affect performance under load, but acceptable for free tier)

**Medium Risk:**
- Conditional module loading (need to ensure all dependencies are met)

## Rollback Plan

If optimization causes issues:
1. Keep original `main.py` as `main_full.py`
2. Test with `main_minimal.py` first
3. Gradually enable modules
4. Revert if needed

## Next Steps

1. Create `main_minimal.py` with only core modules
2. Test deployment with minimal version
3. Gradually enable modules based on memory budget
4. Monitor and adjust

Would you like me to proceed with creating the optimized version?
