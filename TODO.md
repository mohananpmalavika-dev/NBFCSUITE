# TODO: Missing Phase 1–3 Frontend/Backend Items

> Updated: 2026-06-26

## Phase 1 (End-to-end lending workflow: LOS → FindNA → LMS → Collections)
- [x] Verify API surface matches API.md for auth/customer/los/lms/collections.
- [x] Implement/adjust Auth endpoints: `/auth/refresh` and `/auth/validate` (JWT handling) to match API.md.
- [ ] Add LOS workflow hooks:
  - [x] On `POST /applications/{id}/submit`: trigger FindNA behavior scoring (if required inputs exist).
  - [x] On approval/decision: trigger LMS booking with sanctioned details.
- [ ] Add LMS hooks:
  - [x] After booking (and/or after first payment): notify Collections to log activity / ensure assignment.
- [ ] Add Collections hooks:
  - [x] Ensure activity logging/assignment endpoints support workflow wiring.
- [ ] Add Phase-1 E2E integration test(s): create customer → KYC docs → submit LOS application → underwrite/decision → LMS booking → record payment → collections record created.

## Phase 2 (Customer 360 correctness + document expiry + compliance orchestration + reporting + key standardization)
- [x] Fix `services/customer/app/schemas.py` mismatches with DB model and router behavior.
- [x] Add/adjust atomic risk profile update endpoint(s) in customer service.
- [ ] Document expiry actions:
  - [x] Add `GET /documents/expiring` and `PUT /documents/{id}/expire` in document service.
  - [x] Enforce/standardize OCR metadata shape for document records.
- [ ] Compliance orchestration:
  - [x] Add `POST /run-checks/{customer_id}` in compliance service.
  - [x] Standardize status enums and AuditLog writes.
- [ ] Cross-service reference keys:
  - [x] Enforce `subject_type`, `subject_id`, `source_service`, `source_reference_id` across relevant models/schemas.
- [ ] Minimal reporting endpoints:
  - [x] Add/adjust summary endpoints in deposits/accounting/CRM/compliance.

## Phase 3 (FinDNA AI orchestration + persistence + exec dashboard)
- [x] Update FinDNA assistant endpoints to accept canonical inputs.
- [x] Implement persistence keys and retrieval endpoints needed for dashboard.
- [x] Add workflow hooks so LOS/LMS/Collections invoke FinDNA assistants during key state transitions.
- [x] Add dashboard aggregation endpoints (portfolio/risk/collections summaries).

## Frontend / Mobile (only after Phase 1–3 backend is verifiable)
- [x] Wire customer/loan/collection views to real backend endpoints (replace mocks where present).

## CI/CD + Local Dev
- [ ] Ensure docker-compose + ports allow all phase-1 services to run.
- [ ] Add GitHub Actions workflow: lint + unit tests + integration smoke tests.
- [ ] Run DB migrations before tests.

