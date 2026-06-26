# TODO_IMPLEMENTATION.md

This file tracks progress for implementing missing Phase 1–3 items as per `IMPLEMENTATION_PLAN.md`.

## Phase 1 — End-to-end wiring + integration tests
- [ ] Step 1: Implement workflow/event utilities (shared module) for service-to-service calls.
- [x] Step 2: Update LOS submit/decision endpoints to invoke FindNA scoring and (on approval) LMS booking.
- [x] Step 2a: Align LOS endpoint responses with API.md status transitions (draft/submitted/under_review/approved/rejected).

- [x] Step 2b: On LOS decision=approved, call LMS `/loans` to book the loan (sanctioned_amount/tenure/interest/product/application linkage).


- [ ] Step 3
- [x] Step 3a: LMS→Collections repayment activity logging on payment.
- [ ] Step 4
- [ ] Step 5: Implement Auth `/auth/refresh` and `/auth/validate` if required by `API.md`.
- [ ] Step 6: Add integration E2E test `tests/integration/test_phase1_e2e.py`.

## Phase 2 — Customer 360 correctness + expiry/compliance/reporting
- [ ] Step 1: Fix `services/customer/app/schemas.py` mismatches.
- [ ] Step 2: Add/adjust atomic customer risk profile update endpoint(s).
- [ ] Step 3: Add document expiry endpoints (`expiring` query + expire/status transitions).
- [ ] Step 4: Add compliance orchestration endpoint (`run-checks`) and enforce standardized statuses + AuditLog writing.
- [ ] Step 5: Standardize `subject_type/subject_id/source_service/source_reference_id` across services.
- [ ] Step 6: Add minimal reporting endpoints for deposits/accounting/CRM/compliance.

## Phase 3 — FinDNA orchestration + dashboard aggregation
- [ ] Step 1: Ensure FinDNA assistants persistence & stable retrieval keys.
- [ ] Step 2: Wire assistant invocations from workflow hooks.
- [ ] Step 3: Add executive dashboard aggregation endpoints.

## CI/CD / Docker Compose (minimal Phase 1 support)
- [ ] Step 1: Ensure `docker-compose.yml` can run all phase-1 services + DB.
- [ ] Step 2: Add GitHub Actions workflow for lint/unit tests.
- [ ] Step 3: Add smoke/integration steps in CI.

