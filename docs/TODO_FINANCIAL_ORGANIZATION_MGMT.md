# TODO - EOM-013 Financial Organization Management (FOM)

- [x] Add EOM backend DB migration for financial organization tables (cost/profit/budget/internal order + supporting tables)

- [x] Add SQLAlchemy models for the new financial organization entities

- [x] Add Pydantic schemas for create/list/get/update payloads and responses

- [x] Add FastAPI routers for:

  - [x] Cost Centers CRUD + status transitions (MVP)
  - [x] Profit Centers CRUD + status transitions (MVP)
  - [x] Budgets CRUD (original/revised/forecast/actual as fields - MVP)
  - [x] Internal Orders CRUD + lifecycle status transitions (Draft -> Approved -> Open -> Active -> Closed -> Archived)
  - [x] Allocations MVP endpoint (stub)
  - [x] Financial dashboard aggregation endpoint

- [x] Wire routers + model metadata into `services/eom/app/main.py`

- [x] Add backend tests covering cost/profit/internal-order create/list/get and dashboard

- [x] Add customer-app frontend pages + routing for Finance workspace (dashboard/explorer/cost-centers/profit-centers/budgets/internal-orders/reports stubs)

- [x] Add frontend API client methods for the new endpoints

- [x] Run `pytest services/eom/tests` and basic Next.js typecheck/build checks
