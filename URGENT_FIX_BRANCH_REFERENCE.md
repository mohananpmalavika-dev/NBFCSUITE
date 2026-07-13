# 🚨 URGENT FIX: Branch Reference Error

## Error Found in Logs
```
sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[Lead(crm_leads)], 
expression 'Branch' failed to locate a name ('Branch').
```

## Root Cause
The `Lead` model in `crm_lead_models.py` has relationships to the `Branch` model, but:
- `Branch` is only imported when `ENABLE_BRANCH=true`
- Your config has `ENABLE_BRANCH=false`
- SQLAlchemy tries to resolve the relationship at startup and crashes

## Fix Applied
Made the Branch relationships lazy and viewonly so they don't require Branch model at startup:

```python
# Before:
branch = relationship("Branch", foreign_keys=[assigned_to_branch_id])

# After:
branch = relationship("Branch", foreign_keys=[assigned_to_branch_id], lazy="select", viewonly=True)
```

This allows the Lead model to work even when Branch module is disabled.

## Deploy Command
```bash
git add .
git commit -m "Fix: Make Branch relationships in Lead model optional for when ENABLE_BRANCH=false"
git push origin main
```

---

**This is Issue #25 - Branch relationship causing mapper initialization failure**
