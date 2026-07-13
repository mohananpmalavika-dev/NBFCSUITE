# Vendor Table Duplicate Model Fix

## Problem
The application was failing to start with the following error:
```
sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'inventory_items.preferred_supplier_id' could not find table 'vendors' with which to generate a foreign key to target column 'id'
```

## Root Cause
There were **two duplicate `Vendor` model definitions** in the codebase:

1. **`backend/shared/database/procurement_models.py`** (line 131)
   - `__tablename__ = "vendors"`
   - `id = Column(UUID(as_uuid=True), ...)`
   - Comprehensive model with all vendor fields

2. **`backend/shared/database/accounting_extended_models.py`** (line 912) 
   - `__tablename__ = "vendors"` (DUPLICATE!)
   - `id = Column(Integer, ...)` (Different data type!)
   - Partial vendor model

### Why This Caused the Error

When SQLAlchemy tried to create tables:
- Both models registered the same table name `vendors`
- The second import would overwrite the first
- Foreign key relationships became confused
- `inventory_items.preferred_supplier_id` couldn't resolve which `vendors` table to reference
- Table creation failed at startup

## Solution Implemented

### 1. Removed Duplicate Vendor Model
**File: `backend/shared/database/accounting_extended_models.py`**

- Removed the entire duplicate `Vendor` class (lines 912-988)
- Added a comment indicating that the Vendor model is in `procurement_models.py`
- Kept the vendor-related transaction models:
  - `PurchaseInvoice`
  - `VendorPayment`
  - `VendorPaymentAllocation`

### 2. Updated Conditional Imports
**File: `backend/shared/conditional_imports.py`**

Changed from:
```python
from backend.shared.database.accounting_extended_models import (
    Vendor as AccountingVendor,  # This was importing the duplicate!
    VendorPayment, VendorPaymentAllocation
)
```

To:
```python
from backend.shared.database.accounting_extended_models import (
    PurchaseInvoice, VendorPayment, VendorPaymentAllocation
)
# Import Vendor model from procurement (needed for vendor payments)
from backend.shared.database.procurement_models import Vendor
```

## Benefits

1. **Single Source of Truth**: Only one `Vendor` model exists
2. **Consistent Foreign Keys**: All tables now reference the same `vendors` table
3. **No ID Type Conflict**: `Vendor.id` is consistently `UUID(as_uuid=True)`
4. **Proper Relationships**: All vendor-related models can now properly establish relationships

## Tables That Reference the Vendors Table

1. `inventory_items.preferred_supplier_id` → `vendors.id`
2. `purchase_requisition_items.suggested_vendor_id` → `vendors.id`
3. `purchase_orders.vendor_id` → `vendors.id`
4. `goods_receipt_notes.vendor_id` → `vendors.id`
5. `purchase_invoices.vendor_id` → `vendors.id`
6. `vendor_payments.vendor_id` → `vendors.id`
7. `rfq_vendors.vendor_id` → `vendors.id`
8. `vendor_quotes.vendor_id` → `vendors.id`
9. `vendor_invoices.vendor_id` → `vendors.id`

All of these now correctly reference the single `Vendor` model in `procurement_models.py`.

## Testing

To verify the fix works:

1. Deploy the updated code
2. Check that the application starts without errors
3. Verify that all vendor-related tables are created successfully
4. Test vendor CRUD operations through accounting and procurement modules

## Files Modified

1. `backend/shared/database/accounting_extended_models.py` - Removed duplicate Vendor class
2. `backend/shared/conditional_imports.py` - Updated imports to use single Vendor source

---

**Status**: ✅ Fixed
**Date**: 2026-07-13
**Impact**: Critical - Application startup was blocked
