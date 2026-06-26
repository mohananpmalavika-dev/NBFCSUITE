# TODO - Phase 2 (Expanded Operations: 3–6 months)

## Phase 2 Objectives
- Add deposit products, accounting, and CRM
- Improve operational controls and reporting
- Tighten Customer 360 so other Phase 2 services can read/write consistent risk/document/account data

---

## Execution Plan (Phase 2)

### Step 1 — Customer 360 enhancements (schema correctness + risk profile endpoints)
1. Fix schema/model mismatches in `services/customer/app/schemas.py` for `CustomerFinancialProfile*` so FastAPI responses validate correctly.
2. Add endpoint(s) to update customer risk profile atomically.
3. Add/adjust Customer 360 read endpoint(s) to include assets/liabilities/risk profile consistently.

### Step 2 — Document service expiry actions + OCR metadata shape
1. Add endpoint(s) to query expiring documents for a subject.
2. Add endpoint(s) to mark documents expired / transition status.
3. Add OCR-ingestion endpoint contract (store extracted OCR fields in `metadata`).

### Step 3 — Compliance orchestration (KYC/AML/PEP + audit trails)
1. Add endpoints to run KYC/AML/PEP checks for a customer.
2. Ensure compliance check creation writes an `AuditLog` record.
3. Standardize compliance `status` values (pending/passed/flagged/rejected).

### Step 4 — Cross-service integration contracts (lightweight)
1. Standardize minimal reference keys in each Phase 2 service:
   - `subject_type`, `subject_id`
   - `source_service`, `source_reference_id` (use existing `metadata` fields if needed)
2. Ensure customer-related records can be filtered consistently by `customer_id`.

### Step 5 — Operational controls & reporting endpoints (minimum viable)
1. Deposits: customer deposit summary endpoints (balances + statuses).
2. Accounting: reporting skeleton endpoints (trial balance placeholder based on GL/journals).
3. CRM: pipeline summary by stage.
4. Compliance: flagged summary by risk level / customer.

---

## Testing / Verification
- Run each service locally (ports per each README)
- Validate API response models (FastAPI schema correctness)
- Integration smoke tests:
  1. Create customer → upload KYC docs → run compliance check
  2. Create deposit account → get interest schedule
  3. Create journal entry → reconcile bank transaction
  4. Create document with expiry → query expiring documents

