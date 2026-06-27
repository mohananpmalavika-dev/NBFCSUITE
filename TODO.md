# TODO - EOM / NBFC Brand & Branch Hierarchy

## Step 1: Plan confirmation
- [x] Confirm implementing EOM using new tables: eom_zones/eom_regions/eom_areas/eom_clusters/eom_branches (non-breaking for legacy schema).

## Step 2: Create DB migration
- [x] Add `infra/migrations/024_create_eom_tables.sql` with:

  - brands, legal_entities, business_units
  - eom_zones, eom_regions, eom_areas, eom_clusters
  - eom_branches
  - departments, employees, employee_hierarchy
  - customer_branch_mapping
  - optional MVP: branch_limits, branch_vaults, branch_gl_mapping

## Step 3: ORM models
- [ ] Update `services/customer/app/models.py` with SQLAlchemy models for the EOM tables.

## Step 4: Schemas + API endpoints
- [ ] Add `services/customer/app/schemas_eom.py` (or equivalent) with request/response models.
- [ ] Add `services/customer/app/routers/eom.py` implementing Super Admin-only create endpoints for:
  - brands, legal-entities, business-units, zones, regions, areas, clusters, branches, departments

## Step 5: Wire router
- [ ] Update `services/customer/app/main.py` to register `/eom` router.

## Step 6: Consistency check for tenant/user hierarchy scoping
- [ ] Resolve potential type mismatch for `users.*_id` (UUID vs VARCHAR(36)) during migration.

## Step 7: Run migrations + smoke tests
- [ ] Run DB migrations.
- [ ] Run unit/integration tests.

