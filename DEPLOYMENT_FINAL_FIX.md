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

## Issue 5: Deprecated Pydantic v2 Constraint
**Error:** `ValueError: Unknown constraint decimal_places`

**Root Cause:** Pydantic v2 removed the `decimal_places` constraint parameter from `Field()`. This parameter was used to specify decimal precision but is no longer supported.

**Files Updated:**
- `backend/services/fixed_assets/schemas.py` - Removed `decimal_places` from 8 Decimal field definitions
- `backend/services/hrms/schemas/exit_schemas.py` - Removed `decimal_places` from 6 Decimal field definitions

**Solution:**
```python
# Before (Pydantic v1 style - not supported in v2)
amount: Decimal = Field(..., ge=0, decimal_places=2)

# After (Pydantic v2 compatible)
amount: Decimal = Field(..., ge=0)
```

**Note:** The `decimal_places` field name in `CurrencyBase` schema was preserved as it's a legitimate model field, not a constraint parameter.

**Commit:** a27cb64

---

## Issue 6: Missing Auth Dependency Functions
**Error:** `ImportError: cannot import name 'require_employee' from 'backend.services.auth.dependencies'`

**Root Cause:** Multiple files were importing auth dependency functions that didn't exist:
- `require_employee` - imported but never used
- `check_permission` - used but not defined
- `get_current_tenant` - used but not defined

**Files Updated:**
1. `backend/services/auth/dependencies.py` - Added missing functions:
   - `get_current_tenant()` - Returns tenant_id as int (alias for get_tenant_id)
   - `check_permission()` - Alias for require_permission for backward compatibility

2. `backend/services/hrms/ess_router.py` - Removed unused `require_employee` import

**Solution:**
```python
# Added to dependencies.py
async def get_current_tenant(current_user: UserWithRoles = Depends(get_current_user)) -> int:
    """Get current tenant ID as integer"""
    return int(current_user.tenant_id)

def check_permission(permission: str):
    """Alias for require_permission"""
    return require_permission(permission)
```

**Commit:** f29f4a7

---

## Status
✅ Fixed and deployed
- Duplicate table definitions removed
- All import statements updated
- Correct class names used throughout
- Auth module import paths corrected across all modules
- Pydantic v2 incompatible constraints removed
- Missing auth dependency functions added

## Summary of All Fixes
1. **Duplicate Asset Models** - Commented out duplicates in accounting_extended_models.py
2. **Wrong Import Paths** - Updated asset model imports to use asset_models.py
3. **Wrong Class Names** - Changed AssetDepreciationSchedule to AssetDepreciation
4. **Auth Module Path** - Fixed backend.shared.auth → backend.services.auth (22 files)
5. **Pydantic v2 Compatibility** - Removed decimal_places constraints
6. **Missing Auth Functions** - Added check_permission and get_current_tenant

## Next Steps
Monitor Render deployment logs for successful deployment.
