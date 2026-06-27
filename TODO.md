# TODO - CIF / Customer Creation (Tier-1 Banking/NBFC)

## Plan Approval
- [x] Review existing CIF/customer implementation
- [x] Confirm implementation approach: (A) prospects + approve→CIF + (B) dedupe/search reuse customers table
- [ ] Confirm CIF id format requirement: CIF000... sequential vs UUID acceptable

## Implementation Steps
1. [ ] Create new DB migration(s): add `prospects` and minimal prospect-related tables + links to final CIF `customers`.
2. [ ] Implement `/customers/search` endpoint supporting dedupe by: mobile, email, PAN, Aadhaar, passport, voter id, driving licence, GSTIN, CIN, customer_id.
3. [ ] Implement `/prospects` endpoint: create prospect with `status=lead`.
4. [ ] Implement prospect document/identity attachment endpoints (minimal; reuse existing upload patterns).
5. [ ] Implement `/prospects/{id}/approve` endpoint:
   - verify dedupe again
   - generate authoritative CIF `customers.id`
   - copy prospect data into customer tables
   - update prospect status → `customer`
6. [ ] Adjust existing `POST /customers` behavior:
   - ensure it cannot create duplicates
   - route to prospect flow (or reject in favor of search+prospect)
7. [ ] Update Customer 360 to reflect CIF-only; ensure no prospect-based duplication.
8. [ ] Add unit/integration tests for dedupe + approve flow.

## Verification
- [ ] Run DB migrations
- [ ] Run customer service and run tests
- [ ] Validate `Customer Search → Existing CIF` and `Customer Search → Prospect → Approved CIF` end-to-end

