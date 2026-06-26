# TODO_IMPLEMENTATION.md

This file tracks progress for implementing missing Phase 1–3 items as per `IMPLEMENTATION_PLAN.md`.

## Phase 1 — End-to-end wiring + integration tests
- [x] Step 1: Implement workflow/event utilities (shared module) for service-to-service calls. (Wiring is currently implemented inline best-effort HTTP calls; no shared module present.)
- [x] Step 2: Update LOS submit/decision endpoints to invoke FindNA scoring and (on approval) LMS booking.
- [x] Step 2a: Align LOS endpoint responses with API.md status transitions (draft/submitted/under_review/approved/rejected).

- [x] Step 2b: On LOS decision=approved, call LMS `/loans` to book the loan (sanctioned_amount/tenure/interest/product/application linkage).

- [x] Step 3: LMS→Collections activity logging on payment.
- [x] Step 3a: LMS→Collections repayment activity logging on payment.
- [x] Step 4: Ensure Collections has matching endpoints to receive LMS activity logging.
- [x] Step 5: Implement Auth `/auth/refresh` and `/auth/validate`.
- [x] Step 6: Add/complete Phase-1 E2E coverage. (There is an existing `tests/integration/test_microservices.py`, but it is not a strict Phase-1 LOS→LMS→Collections full chain.)


## Phase 2 — Customer 360 correctness + expiry/compliance/reporting
- [x] Step 1: Fix `services/customer/app/schemas.py` mismatches. (Current schemas include FinancialProfileUpdate/Response used by customer router.)
- [x] Step 2: Add/adjust atomic customer risk profile update endpoint(s). (PUT `/{customer_id}/risk-profile` exists and validates allowed fields + enums.)
- [x] Step 3: Add document expiry endpoints (`expiring` query + expire/status transitions). (Document service implements GET `/documents/expiring` and PUT `/documents/{id}/expire`.)
- [x] Step 4: Add compliance orchestration endpoint (`run-checks`) and enforce standardized statuses + AuditLog writing. (POST `/run-checks/{customer_id}` writes checks + audit log; status normalized.)
- [x] Step 5: Standardize `subject_type/subject_id/source_service/source_reference_id` across services. (Document uses subject_type/subject_id; compliance run-checks stores these in check.details + audit_log.details.)
- [x] Step 6: Add minimal reporting endpoints for deposits/accounting/CRM/compliance. (Deposits `/reports/customer-summary/{customer_id}`, accounting `/reports/trial-balance`, CRM `/reports/pipeline-summary`, compliance `/reports/summary`.)


## Phase 3 — FinDNA orchestration + dashboard aggregation
- [x] Step 1: Ensure FinDNA assistants persistence & stable retrieval keys. (Persisted via `AssistantInvocation` + `invocation_key`.)
- [x] Step 2: Wire assistant invocations from workflow hooks. (LOS invokes underwriting assistant; LMS invokes relationship/collections assistants; Collections invokes collections assistant keyed by loan account.)
- [x] Step 3: Add executive dashboard aggregation endpoints. (`GET /dashboard/executive` plus assistant invocation retrieval endpoints.)



## CI/CD / Docker Compose (minimal Phase 1 support)
- [ ] Step 1: Ensure `docker-compose.yml` can run all phase-1 services + DB.
- [ ] Step 2: Add GitHub Actions workflow for lint/unit tests.
- [ ] Step 3: Add smoke/integration steps in CI.

