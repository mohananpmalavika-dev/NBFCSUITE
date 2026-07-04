# TODO — EOM-010 Grade Management System (GMS)

## Backend
- [x] Verify `services/eom/app/routers/grade.py` exists and exposes all required grade APIs.
- [x] Verify `services/eom/app/main.py` includes the grade router.
- [x] Review `services/eom/tests/test_grade_api.py` coverage.

## Frontend — Grade Directory + Profile
- [x] Verify directory page exists: `apps/customer-app/app/eom/grades/page.tsx`.
- [ ] Implement Grade Profile tabs data rendering + save actions:

  - [ ] salary (GET/PUT)
  - [ ] benefits (GET/PUT)
  - [ ] leave (GET/PUT)
  - [ ] competencies (GET/PUT)
  - [ ] training (GET/PUT)
  - [ ] approvals (GET/PUT)
  - [ ] career (GET/PUT)
  - [ ] documents (GET/PUT)
  - [ ] timeline (GET)
  - [ ] audit (GET)
  - [ ] ai (GET)
  - [ ] overview improvements (tie health + issues)

## Frontend — Create Grade Wizard
- [ ] Replace current wizard scaffold with full Step 1–10 flow (including review/submit).
- [ ] Wire wizard step persistence through `/eom/grades/{id}/profile` or tab endpoints.

## Frontend — Dashboard
- [ ] Add grades dashboard workspace route and KPIs/charts.

## Tests
- [ ] Add/extend frontend smoke tests if repo provides a strategy.
- [ ] Ensure backend grade tests pass independently (targeted run).

