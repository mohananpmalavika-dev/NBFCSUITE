# Bank Reconciliation - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Create a Reconciliation
```bash
POST /api/v1/treasury/reconciliation
{
  "bank_account_id": 1,
  "reconciliation_date": "2026-01-07",
  "period_start_date": "2026-01-01",
  "period_end_date": "2026-01-07",
  "book_balance": 1000000.00,
  "bank_balance": 995000.00,
  "notes": "Month-end reconciliation"
}
```

### Step 2: Import Bank Statements
```bash
POST /api/v1/treasury/reconciliation/bank-statements/bulk-import
{
  "bank_account_id": 1,
  "import_batch_id": "BATCH-20260107-001",
  "statements": [
    {
      "transaction_date": "2026-01-05",
      "description": "Customer payment",
      "credit_amount": 50000.00,
      "balance": 1000000.00
    }
  ]
}
```

### Step 3: Add Outstanding Items
```bash
POST /api/v1/treasury/reconciliation/1/items
{
  "item_type": "outstanding_cheque",
  "item_date": "2026-01-07",
  "description": "Cheque #123456 not cleared",
  "amount": 5000.00,
  "is_debit": true
}
```

### Step 4: Submit for Approval
```bash
POST /api/v1/treasury/reconciliation/1/submit
```

### Step 5: Approve
```bash
POST /api/v1/treasury/reconciliation/1/approve
{
  "approval_notes": "Reviewed and approved"
}
```

---

## 📱 Frontend URLs

- **List:** http://localhost:3000/treasury/reconciliation
- **Create:** http://localhost:3000/treasury/reconciliation/create
- **View:** http://localhost:3000/treasury/reconciliation/{id}

---

## 🔑 Key Concepts

### Reconciliation Status Flow
```
DRAFT → IN_PROGRESS → MATCHED → PENDING_APPROVAL → APPROVED
                                                  ↘ REJECTED
```

### Item Types
- `outstanding_cheque` - Cheques issued but not cleared
- `deposit_in_transit` - Deposits made but not reflected
- `bank_charges` - Bank fees not in books
- `interest_earned` - Interest not recorded
- `direct_debit` - Direct debits not recorded
- `direct_credit` - Direct credits not recorded
- `error_correction` - Errors requiring adjustment
- `other` - Other reconciliation items

---

## 💡 Common Use Cases

### Monthly Reconciliation
1. Create reconciliation for the month
2. Import bank statements
3. Add outstanding items
4. Review difference
5. Submit and approve

### Statement Matching
1. Import statements
2. Use auto-match for automatic matching
3. Manually match remaining items
4. Track matched vs unmatched

### Difference Investigation
1. Get reconciliation details
2. View difference breakdown by type
3. Add missing items
4. Verify and approve

---

## 🛠️ Development

### Backend Service
```python
from backend.services.treasury.reconciliation_service import ReconciliationService

service = ReconciliationService(db, tenant_id, user_id)
reconciliation = service.create_reconciliation(data)
```

### Frontend Service
```typescript
import { reconciliationService } from '@/services/treasury.service'

const reconciliations = await reconciliationService.getReconciliations()
const detail = await reconciliationService.getReconciliation(id)
```

---

## 📊 Statistics

Get overall statistics:
```bash
GET /api/v1/treasury/reconciliation/statistics/summary
```

Get difference breakdown:
```bash
GET /api/v1/treasury/reconciliation/1/difference-breakdown
```

---

## 🔐 Security

- All endpoints require JWT authentication
- Multi-tenant isolation (automatic)
- Status-based access control
- Immutable approved records
- Complete audit trail

---

## 📚 Documentation

- Full API docs: http://localhost:8000/docs
- Detailed guide: TREASURY_WEEK3_RECONCILIATION_COMPLETE.md
- Overall status: TREASURY_COMPLETE_STATUS.md

---

**Version:** 1.0  
**Last Updated:** January 7, 2026  
**Status:** Production-Ready
