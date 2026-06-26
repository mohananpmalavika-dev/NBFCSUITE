-- Phase 1 hardening: link IAM users to the organization hierarchy for data scoping.
-- These nullable columns allow one user to be scoped at the most specific relevant level.

ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_id UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS zone_id UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS region_id UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS area_id UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS branch_id UUID;

CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_zone_id ON users(zone_id);
CREATE INDEX IF NOT EXISTS idx_users_region_id ON users(region_id);
CREATE INDEX IF NOT EXISTS idx_users_area_id ON users(area_id);
CREATE INDEX IF NOT EXISTS idx_users_branch_id ON users(branch_id);
