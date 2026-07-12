# Pydantic v2 Compatibility Fix

## Issue Found
During verification, discovered Pydantic v2 incompatibility:
```
pydantic.errors.PydanticUserError: `regex` is removed. use `pattern` instead
```

## Root Cause
Pydantic v2 changed the Field parameter name from `regex` to `pattern` for string pattern validation.

## Fix Applied ✅
Replaced `regex=` with `pattern=` in all Field definitions:

### Files Modified:
1. `backend/services/hrms/loan_schemas.py` (4 occurrences)
   - Line 196: LoanApprovalAction.action
   - Line 204: LoanDisbursementRequest.disbursement_mode
   - Line 302: LoanTransactionCreate.transaction_type
   - Line 341: LoanClosureRequest.closure_reason

2. `backend/services/hrms/schemas/exit_schemas.py` (1 occurrence)
   - Line 672: sort_order field

### Changes Made:
```python
# BEFORE (Pydantic v1 syntax)
Field(..., regex="^(approve|reject)$")

# AFTER (Pydantic v2 syntax)
Field(..., pattern="^(approve|reject)$")
```

## Why This Matters
- Pydantic v2 is stricter about parameter names
- Using old syntax causes runtime errors on import
- This would have blocked deployment even after model fixes

## Status
✅ All Pydantic v2 incompatibilities fixed
✅ Total changes: 5 Field definitions across 2 files

## Impact
- No functional changes
- Same validation logic
- Just parameter name update for Pydantic v2 compatibility

---
**Status:** ✅ Fixed
**Files Modified:** 2
**Total Changes:** 5 Field definitions
