# Vendor Table Foreign Key Fix

## Problem
The application was failing to start with this error:
```
sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'inventory_items.preferred_supplier_id' could not find table 'vendors' with which to generate a foreign key to target column 'id'
```

## Root Cause
The `inventory_items` table has a foreign key reference to the `vendors` table:
```python
preferred_supplier_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)
```

However, the `Vendor` model was only being imported conditionally when either:
- `ENABLE_ACCOUNTING=true` 
- `ENABLE_INVENTORY=true`

In deployment configurations where both were disabled, the `vendors` table was never created, causing SQLAlchemy to fail when trying to set up the foreign key constraint.

## Solution
**Always import the Vendor model**, regardless of feature flags, since multiple modules reference it:
- Inventory module (`inventory_items.preferred_supplier_id`)
- Accounting module (vendor payments)
- Procurement module (purchase requisitions, orders)

## Changes Made

### File: `backend/shared/conditional_imports.py`

1. **Added Vendor import to core models section** (always imported):
```python
# 1b. Vendor model (ALWAYS IMPORTED - referenced by multiple modules)
logger.info("Importing Vendor model (shared across modules)...")
from backend.shared.database.procurement_models import Vendor
```

2. **Removed duplicate Vendor imports** from:
   - Accounting section (line ~110)
   - Inventory section (line ~180)

## Impact
- ✅ Vendor table will always be created, regardless of feature flags
- ✅ Inventory module can reference vendors safely
- ✅ Accounting vendor payments will work correctly
- ✅ All microservices can share the same database schema
- ✅ No breaking changes - backward compatible

## Microservices Architecture Implications
This fix is essential for the microservices split because:
1. **Shared Database**: All services use the same PostgreSQL database
2. **Cross-module References**: Tables can reference each other across service boundaries
3. **Schema Consistency**: Core shared tables (like vendors) must exist for foreign keys to work

## Testing
After deployment, verify:
1. Application starts without SQLAlchemy errors
2. Vendor table exists in the database
3. Inventory items can be created with `preferred_supplier_id`
4. Accounting vendor payments function correctly

## Related Files
- `backend/shared/database/procurement_models.py` - Vendor model definition
- `backend/shared/database/inventory_models.py` - References Vendor
- `backend/shared/database/accounting_extended_models.py` - References Vendor
- `backend/shared/conditional_imports.py` - Import logic (FIXED)
