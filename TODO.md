# TODO — Phase 2 (Customer 360 correctness + expiry/compliance/reporting)

## Step 1: Fix `services/customer/app/schemas.py` mismatches
- [x] Inspect customer schemas + customer router response models
- [x] Align request/response models with actual DB fields
- [x] Ensure risk/financial profile types validate correctly


## Step 2: Add/adjust atomic customer risk profile update endpoint(s)
- [ ] Inspect customer router risk update endpoints
- [ ] Implement single-transaction atomic update + validation
- [ ] Ensure response matches updated schema

## Step 3: Add document expiry endpoints
- [ ] Inspect document service model/status fields
- [ ] Implement `GET /documents/expiring` (expiry_date + filters)
- [ ] Implement `PUT /documents/{id}/expire` (status transitions)

## Step 4: Compliance orchestration endpoint (`run-checks`)
- [ ] Inspect compliance models/status enums + AuditLog write path
- [ ] Implement `POST /run-checks/{customer_id}` orchestration
- [ ] Standardize compliance statuses + ensure AuditLog includes standardized subject/source keys

## Step 5: Standardize cross-service subject/reference keys
- [ ] Identify all schema fields: `subject_type/subject_id/source_service/source_reference_id`
- [ ] Update affected services/endpoints to use canonical naming
- [ ] Add/adjust minimal serialization/mapping where needed

## Step 6: Minimal reporting endpoints
- [ ] Add deposits/accounting/CRM/compliance summary endpoints
- [ ] Ensure endpoints return consistent minimal aggregates

## Verification
- [ ] Run tests (`pytest -q`)
- [ ] Smoke test endpoints per `API.md`

