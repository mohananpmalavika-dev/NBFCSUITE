# IMPLEMENTATION_PLAN.md

## Scope
Implement missing Phase 1–3 items in this repo by converting phase objectives into concrete engineering tasks (endpoint behavior + DB state transitions + service-to-service wiring).

## Information Gathered
- **Phase definitions**: `plan.md`
  - Phase 1: auth/customer + LOS MVP + LMS MVP + collections MVP + shared infra + end-to-end lending flow.
  - Phase 2: deposits + accounting + CRM + document expiry/OCR + compliance orchestration + customer 360 correctness.
  - Phase 3: FinDNA AI capabilities (behavioral scoring, assistants) + exec dashboard.
- **Phase 2 concrete TODOs**: `TODO.md`
  - Fix `services/customer/app/schemas.py` mismatches for customer financial/risk profile.
  - Add atomic risk profile update endpoint(s).
  - Document expiry actions + OCR metadata shape.
  - Compliance orchestration (run checks, write AuditLog, standardize status enums).
  - Standardize cross-service reference keys.
  - Minimal reporting endpoints.
- **Expected API surface**: `API.md`
  - Lists per-service endpoints (auth/customers/los/lms/collections/findna/etc.).
- **Service code inspected (from previous tool reads)**:
  - `services/auth/app/main.py` endpoints: login, user CRUD, roles (no refresh/validate endpoints implemented despite API.md mentioning them).
  - `services/customer/app/routers/customer.py` endpoints: customer CRUD, addresses, KYC document upload, financial profile and risk profile endpoints.
  - `services/los/app/main.py` provides application CRUD, submit, underwrite, decision, scorecard.
  - `services/lms/app/main.py` provides loan booking, EMI schedule, record payments, foreclosure quote.
  - `services/collections/app/main.py` provides bucket + assignment + activity logging + settlement offer + NPA classification.
  - `services/document/app/main.py` provides generic document CRUD with metadata + expiry_date.
  - `services/findna/app/main.py` provides behavior/fraud/churn/assistants + embeddings, explanations (mostly mock/simulated).
  - `services/compliance/app/main.py` provides watchlist, compliance checks, audit logs (but no orchestration endpoints as described in TODO.md).
  - `services/crm/app/main.py`, `services/accounting/app/main.py`, `services/deposits/app/main.py` exist with basic CRUD/reporting stubs.

## Key Implementation Gaps Identified (Phase 1–3)
### Phase 1 (Foundation & Core Architecture)
1. **Event-driven / workflow wiring for end-to-end flow**
   - Ensure LOS state transitions can trigger:
     - FindNA scoring (behavior/fraud) generation
     - LMS booking on approval
     - Collections bucket/assignment on disbursal/payment/delinquency
   - Current services are isolated (no explicit inter-service orchestration/webhook/event consumption verified in the inspected code).
2. **Integration tests + E2E**
   - Add a minimal integration suite validating: create customer → KYC docs → LOS application → submit → underwrite/decision → LMS booking → payment posting → collections record creation.
3. **Service consistency**
   - Align endpoint names/paths with `API.md` (e.g., auth refresh/validate and various path mismatches are probable).
4. **Docker Compose readiness**
   - Ensure local run works across all phase-1 services (auth/customer/los/lms/collections + DB).

### Phase 2 (Expanded Operations)
1. **Customer 360 schema/model correctness**
   - Fix `services/customer/app/schemas.py` to match DB model and runtime response validation (explicitly called out in TODO.md Step 1).
2. **Atomic customer risk profile update endpoint(s)**
   - Add endpoint(s) that update risk fields consistently (and optionally related document status updates).
3. **Document expiry actions + OCR ingestion contract**
   - Add endpoints to list expiring docs and transition expiry status.
   - Standardize OCR metadata fields in `metadata`.
4. **Compliance orchestration**
   - Add endpoints to run KYC/AML/PEP checks and write AuditLog.
   - Standardize compliance status values.
5. **Cross-service reference keys**
   - Enforce `subject_type`, `subject_id`, `source_service`, `source_reference_id` fields for documents/records.
6. **Operational reporting endpoints**
   - Add minimal summary endpoints across deposits/accounting/CRM/compliance aligned to Phase 2 objectives.

### Phase 3 (AI & Behavioral Intelligence)
1. **AI orchestration and real pipeline scaffolding**
   - Replace/augment mock assistants with calls that read required inputs from LOS/LMS/Collections/customer profile.
   - Add orchestration hooks so assistants are invoked automatically in workflow states.
2. **Persistence & retrieval correctness**
   - Ensure FinDNA stores outputs with stable keys and can be queried by customer/application.
3. **Executive dashboard backing endpoints**
   - Add APIs (and optionally minimal frontend wiring) that aggregate portfolio, risk, and collections.
4. **LangGraph/feature store scaffolding**
   - If ML pipeline is not ready, implement interface stubs + workflow engine integration placeholders.

## Plan (by file/service)
### Phase 1: End-to-end workflow + tests
1. **Create shared workflow/event utilities**
   - New module: `services/<service>/app/workflow.py` (or shared package) implementing:
     - trigger points and HTTP calls to downstream services (or domain event publishing if later message bus is introduced).
2. **LOS integration hooks**
   - Update `services/los/app/main.py`:
     - On `POST /applications/{id}/submit`: trigger FindNA behavior scoring (if customer_id present) and store results.
     - On `POST /applications/{id}/decision` when approved: call LMS `/loans` booking with sanctioned details.
3. **LMS integration hooks**
   - Update `services/lms/app/main.py`:
     - On `POST /loans/{loan_id}/payment`: call Collections to log activity and update bucket assignment rules (minimal initial behavior).
4. **Collections integration hooks**
   - Update `services/collections/app/main.py`:
     - Add endpoints expected by workflow wiring (if not already present) such as:
       - log activity and ensure assignment existence.
5. **Auth consistency**
   - Update `services/auth/app/main.py`:
     - Implement `/auth/refresh` and `/auth/validate` to match `API.md`.
     - Add JWT-protected dependencies for secured endpoints (optional if API.md expects auth everywhere).
6. **Integration tests**
   - Create `tests/integration/test_phase1_e2e.py` validating end-to-end flow.

### Phase 2: Customer 360 correctness + orchestration + expiry/compliance/reporting
1. **Fix customer schemas**
   - Update `services/customer/app/schemas.py` so `FinancialProfileUpdate`/`FinancialProfileResponse` types match the DB model and router behavior.
2. **Atomic risk profile endpoint**
   - Update `services/customer/app/routers/customer.py`:
     - Ensure risk update validates and updates a consistent subset atomically.
3. **Document expiry**
   - Update `services/document/app/main.py`:
     - Add `GET /documents/expiring` and `PUT /documents/{id}/expire` endpoints.
     - Add OCR ingestion endpoint contract or at minimum enforce metadata schema.
4. **Compliance orchestration**
   - Update `services/compliance/app/main.py`:
     - Add `POST /run-checks/{customer_id}` that creates compliance checks and writes audit log.
     - Add status enum validation (pending/passed/flagged/rejected).
5. **Cross-service key contract**
   - Update customer/document/compliance schemas/models to store `subject_type/subject_id/source_service/source_reference_id`.
6. **Reporting endpoints**
   - Update `services/deposits/app/main.py`, `services/accounting/app/main.py`, `services/crm/app/main.py`, `services/compliance/app/main.py` with minimal summary endpoints.

### Phase 3: FinDNA orchestration + executive dashboard APIs
1. **FinDNA workflow interfaces**
   - Update `services/findna/app/main.py`:
     - Ensure assistant endpoints accept canonical inputs.
     - Add persistence keys and implement missing GET endpoints as needed for Phase 3 dashboard.
2. **Connect workflow hooks**
   - Update LOS/LMS/Collections to call FinDNA assistants in workflow state transitions.
3. **Executive dashboard aggregation endpoints**
   - Add new service endpoint(s) (either in `findna` or a new lightweight `reporting` module) to aggregate:
     - portfolio health
     - risk summary
     - collections summary

### Docker Compose / CI/CD (minimal for Phase 1 success)
1. **Docker Compose**
   - Update `docker-compose.yml` and service Dockerfiles/ports so all phase-1 services can run locally.
2. **Minimal CI**
   - Add GitHub Actions workflow for lint + unit tests + integration smoke tests.

## Dependent Files to be Edited (high level)
- `services/los/app/main.py`
- `services/lms/app/main.py`
- `services/collections/app/main.py`
- `services/auth/app/main.py`
- `services/customer/app/schemas.py`
- `services/customer/app/routers/customer.py`
- `services/document/app/main.py`
- `services/compliance/app/main.py`
- `services/deposits/app/main.py`
- `services/accounting/app/main.py`
- `services/crm/app/main.py`
- `services/findna/app/main.py`
- `tests/integration/*`
- `docker-compose.yml`
- add `.github/workflows/ci.yml`

## Follow-up Steps (after implementation)
1. Run DB migrations (existing SQL scripts in `infra/migrations/`).
2. Start services with Docker Compose.
3. Run integration tests:
   - `pytest -q` (and ensure DB connectivity)
4. Validate E2E flow via API calls (create customer, submit LOS, underwrite, decision, book loan, payment, collections activity).

<ask_followup_question>
Confirm acceptance criteria for Phase 1–3 as described below:
- Phase 1: End-to-end API flow is verifiable end-to-end across LOS → FindNA → LMS → Collections.
- Phase 2: Customer risk profile update + document expiry + compliance orchestration + standardized keys + basic reporting endpoints work and return consistent data.
- Phase 3: FinDNA assistants store/retrieve outputs and are invoked by workflow hooks; dashboard aggregation APIs return correct aggregates.
Reply: “Confirm” to proceed implementing Phase 1–3 backend first (CI/CD + frontend/mobile later).
</ask_followup_question>

