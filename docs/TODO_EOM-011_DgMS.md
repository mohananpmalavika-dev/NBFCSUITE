# TODO — EOM-011 Designation Management System (DgMS)

## Plan approval: proceed

### Step 1 — Backend model extensions
- [ ] Extend `services/eom/app/models_designation.py` (or add new models) for:
  - designation_competency, designation_responsibility, designation_recruitment,
  - designation_kpi, designation_approval, designation_career, designation_training,
  - minimal designation_document, designation_health scaffolding.

### Step 2 — Backend schema extensions
- [ ] Update `services/eom/app/schemas_designation.py` with request/response models for the supporting resources.

### Step 3 — Backend API endpoints
- [ ] Update `services/eom/app/routers/designations.py` with endpoints:
  - `GET /eom/designations/{id}/competencies`
  - `GET /eom/designations/{id}/career`
  - `GET /eom/designations/{id}/health`
  - plus MVP `POST/PUT` endpoints for competencies, responsibilities, recruitment, kpis, approvals, training, career.

### Step 4 — Migrations
- [ ] Add new Alembic migration creating the new supporting tables.

### Step 5 — Backend tests
- [ ] Extend `services/eom/tests/test_designations_api.py` to cover:
  - creating/fetching competencies
  - health endpoint returns score/rating/issues

### Step 6 — Frontend routes & tabs scaffold
- [ ] Add Next.js pages:
  - `apps/customer-app/app/eom/designations/page.tsx` (directory)
  - `apps/customer-app/app/eom/designations/[id]/page.tsx` (designation 360 scaffold)
  - `apps/customer-app/app/eom/designations/[id]/components/tabs.tsx`
  - `apps/customer-app/app/eom/designations/[id]/components/DesignationTabs.tsx`

### Step 7 — Frontend wiring to endpoints
- [ ] Wire overview, competencies, career, health tabs to backend endpoints (best-effort, minimal rendering).

### Step 8 — Frontend minimal “new designation” wizard
- [ ] Add `apps/customer-app/app/eom/designations/new/page.tsx` with steps 1-3:
  - General, Organization, Responsibilities
  - Save draft (status=draft) and publish (status=active) wiring.

### Step 9 — Run tests/build
- [ ] Run `pytest -q` (or at least EOM tests) and `npm test/build` for customer-app.

