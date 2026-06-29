# TODO - EOM-013 Financial Organization Management (FOM)

- [x] Add EOM backend DB migration for financial organization tables (cost/profit/budget/internal order + supporting tables)

- [ ] Add SQLAlchemy models for the new financial organization entities


- [ ] Add Pydantic schemas for create/list/get/update payloads and responses
- [x] Add FastAPI routers for:

  - [ ] Cost Centers CRUD + status transitions (MVP)
  - [ ] Profit Centers CRUD + status transitions (MVP)
  - [ ] Budgets CRUD (original/revised/forecast/actual as fields - MVP)
  - [ ] Internal Orders CRUD + lifecycle status transitions (Draft→Approved→Open→Active→Closed→Archived)
  - [ ] Allocations MVP endpoint (stub)
  - [ ] Financial dashboard aggregation endpoint
- [ ] Wire routers + model metadata into `services/eom/app/main.py`
- [x] Add backend tests covering cost/profit/internal-order create/list/get and dashboard

- [ ] Add customer-app frontend pages + routing for Finance workspace (dashboard/explorer/cost-centers/profit-centers/budgets/internal-orders/reports stubs)
- [ ] Add frontend API client methods for the new endpoints
- [ ] Run `pytest services/eom/tests` and basic Next.js typecheck/build checks

