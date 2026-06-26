# TODO.md — Phase 4: Enterprise Readiness & Ecosystem (Months 20–24)

## Planned Deliverables

### A) Full-Fledged Accounting Module
- [ ] Standardize tenant scoping across **all** accounting endpoints (no cross-tenant reads/writes; fix uniqueness rules).
- [ ] Harden GL account uniqueness to be **per tenant** (and adjust code accordingly).
- [ ] Add robust automated GL posting contract:
  - [ ] idempotency key support
  - [ ] posting status (posted/reversed/failed)
  - [ ] source linkage via `source_module/source_event/source_reference`
- [ ] Implement period-aware financial statement generation:
  - [ ] Trial Balance by date/period
  - [ ] P&L by date/period with correct revenue/expense classification
  - [ ] Balance Sheet by date/period with correct asset/liability/equity rollups
- [ ] Add GST/TDS MVP:
  - [ ] tax master data per tenant
  - [ ] tax computation breakdown
  - [ ] generation of corresponding journal lines (not only tax amount)
- [ ] Extend OpenAPI spec for accounting to reflect new endpoints/inputs.

### B) Advanced CRM & Reporting
- [ ] Add Report Builder backend:
  - [ ] report definition schema
  - [ ] execute report endpoint with server-side validation
  - [ ] initial support for CRM data sources
- [ ] Add Dashboard Builder backend:
  - [ ] dashboard/widget schema
  - [ ] render/resolve dashboard endpoint
- [ ] Provide CEO Command Center default dashboard config.
- [ ] Extend CRM OpenAPI spec.

### C) Multi-Tenancy Architecture
- [ ] Add tenant configuration + branding backend data model (MVP).
- [ ] Ensure auth/RBAC context carries `tenant_id` and services enforce it consistently.
- [ ] Add tenant_id indexes where missing.
- [ ] Add/adjust migrations for new accounting/CRM tables.

## Follow-up / Validation
- [ ] Run integration tests in `tests/integration/test_microservices.py`.
- [ ] Add an end-to-end scenario covering:
  - [ ] create lead → opportunity → CRM report
  - [ ] trigger posting → generate Trial Balance for the same tenant
- [ ] Validate tenant isolation using two tenants with overlapping identifiers.

