# Deployment Fixes - Asset Model Import Errors

## Issue 1: Duplicate Table Definition
**Error:** `sqlalchemy.exc.InvalidRequestError: Table 'fixed_assets' is already defined`

**Root Cause:** Asset models were defined in two locations:
- `backend/shared/database/asset_models.py` (comprehensive)
- `backend/shared/database/accounting_extended_models.py` (duplicate)

**Solution:**
- Commented out duplicate model classes in `accounting_extended_models.py`:
  - `FixedAsset`
  - `AssetDepreciationSchedule`
  - `AssetTransfer`
  - `AssetMaintenance`
- Kept enum definitions for backward compatibility

**Commit:** 637998d

---

## Issue 2: Import Errors After Commenting Out Models
**Error:** `ImportError: cannot import name 'FixedAsset' from 'backend.shared.database.accounting_extended_models'`

**Root Cause:** Services were still importing asset models from the old location

**Files Updated:**
1. `backend/services/accounting/asset_service.py`
   - Changed imports from `accounting_extended_models` to `asset_models`
   - Models: `FixedAsset`, `AssetDepreciationSchedule`, `AssetTransfer`, `AssetMaintenance`
   - Kept enum imports: `AssetCategory`, `DepreciationMethod`, `AssetStatus`

2. `backend/services/accounting/asset_router.py`
   - Updated two local imports inside functions:
     - Line 404: `FixedAsset` import in `get_asset_dashboard()`
     - Line 382: `AssetMaintenance` import in maintenance history function

**Solution:**
```python
# Before
from backend.shared.database.accounting_extended_models import (
    FixedAsset, AssetDepreciationSchedule, AssetTransfer, AssetMaintenance
)

# After
from backend.shared.database.asset_models import (
    FixedAsset, AssetDepreciationSchedule, AssetTransfer, AssetMaintenance
)
from backend.shared.database.accounting_extended_models import (
    AssetCategory, DepreciationMethod, AssetStatus  # Enums stay here
)
```

**Commit:** 957dcb5

---

## Issue 3: Incorrect Class Name in Imports
**Error:** `ImportError: cannot import name 'AssetDepreciationSchedule' from 'backend.shared.database.asset_models'`

**Root Cause:** The class in `asset_models.py` is named `AssetDepreciation`, not `AssetDepreciationSchedule`

**Files Updated:**
1. `backend/services/accounting/asset_service.py`
   - Changed import from `AssetDepreciationSchedule` to `AssetDepreciation`
   - Updated return type annotation in `post_depreciation()` method
   - Updated all references in the depreciation posting logic
   - Updated return type annotation in `get_depreciation_schedule()` method
   - Updated all query references in `get_depreciation_schedule()` method

**Solution:**
```python
# Correct class name in asset_models.py
from backend.shared.database.asset_models import (
    FixedAsset,
    AssetDepreciation,  # Not AssetDepreciationSchedule
    AssetTransfer,
    AssetMaintenance
)
```

**Commit:** 25e2192, 841e038

---

## Issue 4: Incorrect Auth Module Import Path
**Error:** `ModuleNotFoundError: No module named 'backend.shared.auth'`

**Root Cause:** Multiple files were importing from incorrect path `backend.shared.auth.dependencies` instead of `backend.services.auth.dependencies`

**Files Updated (22 files):**
- `backend/crm/routes/customer_service_routes.py`
- `backend/crm/routes/marketing_routes.py`
- `backend/crm/routes/opportunity_routes.py`
- `backend/services/aml/router.py`
- `backend/services/crm/opportunity_router.py`
- `backend/services/crm/router.py`
- `backend/services/facility/building_router.py`
- `backend/services/facility/cafeteria_router.py`
- `backend/services/facility/housekeeping_router.py`
- `backend/services/facility/transport_router.py`
- `backend/services/facility/visitor_router.py`
- `backend/services/fixed_assets/router.py`
- `backend/services/hrms/ess_router.py`
- `backend/services/hrms/loan_router.py`
- `backend/services/hrms/routes/exit_routes.py`
- `backend/services/hrms/routes/performance_routes.py`
- `backend/services/legal/license_router.py`
- `backend/services/legal/litigation_router.py`
- `backend/services/legal/router.py`
- And 3 other schema files

**Solution:**
```python
# Before (incorrect)
from backend.shared.auth.dependencies import get_current_user

# After (correct)
from backend.services.auth.dependencies import get_current_user
```

**Commit:** 697f0c3

---

## Status
✅ Fixed and deployed
- Duplicate table definitions removed
- All import statements updated
- Correct class names used throughout
- Auth module import paths corrected across all modules

## Next Steps
Monitor Render deployment logs for any remaining import errors.
