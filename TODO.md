# TODO.md — Phase 4: Enterprise Readiness & Ecosystem (Months 20–24)

## Planned Deliverables

### A) Full-Fledged Accounting Module
- [x] Standardize tenant scoping across **all** accounting endpoints (no cross-tenant reads/writes; fix uniqueness rules).
- [x] Harden GL account uniqueness to be **per tenant** (and adjust code accordingly).
- [x] Add robust automated GL posting contract:
  - [x] idempotency key support
  - [x] posting status (posted/reversed/failed)
  - [x] source linkage via `source_module/source_event/source_reference`
- [x] Implement period-aware financial statement generation:
  - [x] Trial Balance by date/period
  - [x] P&L by date/period with correct revenue/expense classification
  - [x] Balance Sheet by date/period with correct asset/liability/equity rollups
- [x] Add GST/TDS MVP:
  - [x] tax master data per tenant
  - [x] tax computation breakdown
  - [x] generation of corresponding journal lines (not only tax amount)
- [x] Extend OpenAPI spec for accounting to reflect new endpoints/inputs.

### B) Advanced CRM & Reporting
- [x] Add Report Builder backend:
  - [x] report definition schema
  - [x] execute report endpoint with server-side validation
  - [x] initial support for CRM data sources
- [x] Add Dashboard Builder backend:
  - [x] dashboard/widget schema
  - [x] render/resolve dashboard endpoint
- [x] Provide CEO Command Center default dashboard config.
- [x] Extend CRM OpenAPI spec.

### C) Multi-Tenancy Architecture
- [x] Add tenant configuration + branding backend data model (MVP).
- [x] Ensure auth/RBAC context carries `tenant_id` and services enforce it consistently.
- [x] Add tenant_id indexes where missing.
- [x] Add/adjust migrations for new accounting/CRM tables.

## Follow-up / Validation
- [ ] Run integration tests in `tests/integration/test_microservices.py` (attempted; local services timed out).
- [x] Add an end-to-end scenario covering:
  - [x] create lead → opportunity → CRM report
  - [x] trigger posting → generate Trial Balance for the same tenant
- [x] Validate tenant isolation using two tenants with overlapping identifiers.

