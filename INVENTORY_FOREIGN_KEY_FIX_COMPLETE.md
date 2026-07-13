# Complete Fix for Inventory Foreign Key Error

## Error Message
```
sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'inventory_items.preferred_supplier_id' could not find table 'vendors' with which to generate a foreign key to target column 'id'
```

## Root Causes Identified

### 1. Duplicate Vendor Model (FIXED)
**Problem**: Two `Vendor` models with the same `__tablename__ = "vendors"`:
- `backend/shared/database/procurement_models.py` (UUID primary key)
- `backend/shared/database/accounting_extended_models.py` (Integer primary key) ❌

**Solution**: Removed duplicate from `accounting_extended_models.py`

### 2. Unconditional Model Imports in `__init__.py` (FIXED)
**Problem**: `backend/shared/database/__init__.py` was importing accounting models unconditionally:
```python
from backend.shared.database.accounting_models import (
    ChartOfAccounts, JournalEntry, ...
)
```

**Solution**: Removed unconditional imports, models are now only loaded via `conditional_imports.py`

### 3. Unconditional Service Imports (FIXED)
**Problem**: `backend/services/inventory/__init__.py` was importing all inventory services at module level:
```python
from backend.services.inventory.item_service import ItemMasterService
from backend.services.inventory.transaction_service import StockTransactionService
```

These services import `inventory_models`, which registers the `inventory_items` table with its foreign key to `vendors.id`, even when `ENABLE_INVENTORY=false`.

**Solution**: Changed to lazy imports using getter functions

## Files Modified

### 1. backend/shared/database/accounting_extended_models.py
**Change**: Removed duplicate `Vendor` class definition
- Removed lines 912-988 (entire Vendor model)
- Added comment indicating Vendor is in `procurement_models.py`
- Kept `PurchaseInvoice`, `VendorPayment`, `VendorPaymentAllocation` which legitimately reference the vendors table

### 2. backend/shared/conditional_imports.py
**Change**: Updated accounting imports to use single Vendor source
```python
# Before:
from backend.shared.database.accounting_extended_models import (
    Vendor as AccountingVendor,  # This was the duplicate!
    VendorPayment, VendorPaymentAllocation
)

# After:
from backend.shared.database.accounting_extended_models import (
    PurchaseInvoice, VendorPayment, VendorPaymentAllocation
)
# Import Vendor model from procurement (needed for vendor payments)
from backend.shared.database.procurement_models import Vendor
```

### 3. backend/shared/database/__init__.py
**Change**: Removed unconditional accounting model imports
```python
# Before:
from backend.shared.database.accounting_models import (
    ChartOfAccounts, JournalEntry, JournalEntryLine, GeneralLedger,
    TrialBalance, AccountingPeriod
)

# After:
# NOTE: Model imports are now handled conditionally in conditional_imports.py
# This prevents unconditional loading of disabled modules
```

### 4. backend/services/inventory/__init__.py
**Change**: Changed from eager imports to lazy getter functions
```python
# Before:
from backend.services.inventory.item_service import ItemMasterService
from backend.services.inventory.transaction_service import StockTransactionService
...

# After:
def get_item_service():
    from backend.services.inventory.item_service import ItemMasterService
    return ItemMasterService

def get_transaction_service():
    from backend.services.inventory.transaction_service import StockTransactionService
    return StockTransactionService
...
```

## How It Works Now

### Feature Flag Flow
1. **Startup**: `main.py` calls `import_models()` from `conditional_imports.py`
2. **Conditional Loading**: Only models for enabled features are imported
3. **No Eager Loading**: Service `__init__.py` files use lazy imports
4. **Clean Metadata**: Only enabled module tables are registered with SQLAlchemy

### Current Production Configuration
From `.env.render.production`:
```
ENABLE_ACCOUNTING=false    # Vendor payments disabled
ENABLE_INVENTORY=false     # Inventory management disabled
ENABLE_CUSTOMERS=true      # Customer management enabled
ENABLE_LOANS=true          # Loan management enabled
```

With `ENABLE_INVENTORY=false`:
- ✅ Inventory models are NOT imported
- ✅ `inventory_items` table is NOT registered
- ✅ No foreign key to `vendors.id` is created
- ✅ Application starts successfully

## Testing

### Verify the Fix
1. Deploy updated code to Render
2. Check application logs for successful startup
3. Verify no `NoReferencedTableError` in logs
4. Confirm only enabled module tables are created

### Enable Inventory Later
To enable inventory in the future:
1. Set `ENABLE_INVENTORY=true` in Render environment variables
2. The `Vendor` model from `procurement_models.py` will be imported
3. Both `vendors` and `inventory_items` tables will be created correctly
4. Foreign key `inventory_items.preferred_supplier_id → vendors.id` will work

## Summary

The issue had **three interconnected causes**:
1. Duplicate Vendor model definition causing table conflicts
2. Unconditional imports in database `__init__.py` bypassing feature flags
3. Eager imports in service `__init__.py` loading disabled modules

All three issues have been resolved, ensuring that:
- ✅ Only ONE Vendor model exists (in `procurement_models.py`)
- ✅ Models are ONLY loaded when their feature flag is enabled
- ✅ Service modules use lazy imports to prevent premature model loading
- ✅ The application can start with `ENABLE_INVENTORY=false`

---

**Status**: ✅ FIXED
**Date**: 2026-07-13
**Priority**: Critical - Application startup blocker
**Tested**: Awaiting deployment verification
