# TODO - EP-014 Enterprise Identity & Access Management (IAM)

## Step 1 — Repo reconnaissance
- [x] Read existing IAM spec: `docs/02-enterprise-design-system/EOM-014-Enterprise-Identity-and-Access-Management-IAM.md`
- [x] Inspect current auth-service implementation: `services/auth/app/main.py`, `security.py`, `models.py`, `schemas.py`
- [x] Inspect auth DB migrations relevant to IAM: `infra/migrations/*.sql`

## Step 2 — Backend security backbone (vertical slice foundation)
- [ ] Add/standardize immutable audit events across login/logout/refresh/OTP/session/role/permission/policy/approval/key/oauth flows
- [ ] Implement permission-based enforcement helper (require_permission) and policy enforcement (AttributePolicy) MVP
- [ ] Complete MFA flow in login (MFA required + OTP verify step)
- [ ] Complete session/device persistence (Device upsert + richer session metadata)

## Step 3 — Privileged access + delegation
- [ ] Add delegation model + endpoints (create + auto expiration + authorization checks)
- [ ] Add privileged access/break-glass MVP stubs and approval enforcement
- [ ] Ensure approval authority is enforced for sensitive actions

## Step 4 — Security dashboard + reports APIs
- [ ] Implement `GET /auth/security/dashboard` with required KPIs (MVP-friendly)
- [ ] Add security events aggregation endpoint if needed by UI

## Step 5 — Frontend vertical slice (apps/customer-app)
- [ ] Build IAM dashboard page(s)
- [ ] Build Users/Profiles page with tabs (Overview/Identity/Organization/Roles/Permissions/Devices/Sessions/Delegation/Security/Timeline/Audit/AI)
- [ ] Build User creation wizard steps (Identity, Organization, Access, Security, Review)

## Step 6 — Integration + run
- [ ] Wire frontend to auth-service endpoints
- [ ] Run backend and frontend smoke checks
- [ ] Ensure CI/tests pass

