-- Migration 006: Insert seed data (roles, permissions, loan products)
-- Created: 2026-06-26

-- Insert default roles
INSERT INTO roles (id, name, description) VALUES
    ('role-admin', 'admin', 'Administrator with full access'),
    ('role-user', 'user', 'Regular user/customer'),
    ('role-lender', 'lender', 'Loan officer / Lender'),
    ('role-collector', 'collector', 'Collections officer'),
    ('role-underwriter', 'underwriter', 'Underwriter for loan approval'),
    ('role-manager', 'manager', 'Branch/Department manager')
ON CONFLICT (name) DO NOTHING;

-- Insert permissions
INSERT INTO permissions (id, name, description) VALUES
    ('perm-view-customer', 'view_customer', 'View customer profile'),
    ('perm-edit-customer', 'edit_customer', 'Edit customer profile'),
    ('perm-create-application', 'create_application', 'Create loan application'),
    ('perm-approve-application', 'approve_application', 'Approve loan application'),
    ('perm-reject-application', 'reject_application', 'Reject loan application'),
    ('perm-view-loan', 'view_loan', 'View loan details'),
    ('perm-collect-payment', 'collect_payment', 'Collect payment'),
    ('perm-manage-collections', 'manage_collections', 'Manage collections workflow')
ON CONFLICT (name) DO NOTHING;

-- Assign permissions to roles
INSERT INTO role_permissions (role_id, permission_id) VALUES
    ('role-admin', 'perm-view-customer'),
    ('role-admin', 'perm-edit-customer'),
    ('role-admin', 'perm-create-application'),
    ('role-admin', 'perm-approve-application'),
    ('role-lender', 'perm-view-customer'),
    ('role-lender', 'perm-create-application'),
    ('role-underwriter', 'perm-view-customer'),
    ('role-underwriter', 'perm-approve-application'),
    ('role-underwriter', 'perm-reject-application'),
    ('role-collector', 'perm-view-loan'),
    ('role-collector', 'perm-collect-payment'),
    ('role-collector', 'perm-manage-collections')
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Insert default loan products
INSERT INTO loan_products (id, product_code, product_name, product_type, min_amount, max_amount, min_tenor, max_tenor, base_rate, processing_fee_percent, is_active) VALUES
    ('prod-personal-001', 'PL001', 'Basic Personal Loan', 'personal_loan', 50000, 500000, 12, 60, 10.5, 2.0, TRUE),
    ('prod-personal-002', 'PL002', 'Premium Personal Loan', 'personal_loan', 500000, 2000000, 12, 84, 9.5, 1.5, TRUE),
    ('prod-home-001', 'HL001', 'Home Loan', 'home_loan', 1000000, 50000000, 120, 360, 7.5, 1.0, TRUE),
    ('prod-auto-001', 'AL001', 'Auto Loan', 'auto_loan', 200000, 5000000, 24, 84, 9.0, 1.5, TRUE),
    ('prod-gold-001', 'GL001', 'Gold Loan', 'gold_loan', 10000, 500000, 6, 24, 12.0, 1.0, TRUE),
    ('prod-education-001', 'EL001', 'Education Loan', 'education_loan', 100000, 5000000, 84, 240, 8.5, 1.0, TRUE)
ON CONFLICT (product_code) DO NOTHING;

-- Insert sample collection buckets
INSERT INTO collection_buckets (id, bucket_name, min_dpd, max_dpd) VALUES
    ('bucket-0-30', '0-30 DPD', 0, 30),
    ('bucket-30-60', '30-60 DPD', 31, 60),
    ('bucket-60-90', '60-90 DPD', 61, 90),
    ('bucket-90plus', '90+ DPD', 91, 999)
ON CONFLICT (bucket_name) DO NOTHING;
