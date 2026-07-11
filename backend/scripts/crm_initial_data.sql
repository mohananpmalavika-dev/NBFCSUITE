-- ============================================================================
-- CRM Lead Management - Initial Data Setup
-- Creates default scoring rules and assignment rules
-- ============================================================================

-- ============================================================================
-- LEAD SCORING RULES
-- Default scoring logic for intelligent lead qualification
-- ============================================================================

-- Income-based Scoring Rules
INSERT INTO crm_lead_scoring_rules (
    rule_name, rule_description, rule_category, field_name, operator, field_value, 
    score_points, is_active, priority, tenant_id
) VALUES
('High Income - Premium', 'Monthly income above 1 lakh', 'demographics', 'monthly_income', 'greater_than', '100000', 20, true, 1, 'default'),
('High Income', 'Monthly income above 75K', 'demographics', 'monthly_income', 'greater_than', '75000', 15, true, 2, 'default'),
('Medium Income', 'Monthly income above 50K', 'demographics', 'monthly_income', 'greater_than', '50000', 10, true, 3, 'default'),
('Basic Income', 'Monthly income above 25K', 'demographics', 'monthly_income', 'greater_than', '25000', 5, true, 4, 'default');

-- Loan Amount Scoring Rules
INSERT INTO crm_lead_scoring_rules (
    rule_name, rule_description, rule_category, field_name, operator, field_value,
    score_points, is_active, priority, tenant_id
) VALUES
('Large Loan Requirement', 'Loan amount above 10 lakhs', 'product', 'loan_amount_required', 'greater_than', '1000000', 15, true, 1, 'default'),
('Medium Loan Requirement', 'Loan amount above 5 lakhs', 'product', 'loan_amount_required', 'greater_than', '500000', 10, true, 2, 'default'),
('Small Loan Requirement', 'Loan amount above 2 lakhs', 'product', 'loan_amount_required', 'greater_than', '200000', 5, true, 3, 'default');

-- Occupation-based Scoring Rules
INSERT INTO crm_lead_scoring_rules (
    rule_name, rule_description, rule_category, field_name, operator, field_value,
    score_points, is_active, priority, tenant_id
) VALUES
('Professional - Doctor', 'Medical professional', 'demographics', 'occupation', 'contains', 'doctor', 15, true, 1, 'default'),
('Professional - Engineer', 'Engineering professional', 'demographics', 'occupation', 'contains', 'engineer', 15, true, 1, 'default'),
('Professional - Manager', 'Management professional', 'demographics', 'occupation', 'contains', 'manager', 15, true, 1, 'default'),
('Professional - Director', 'Senior management', 'demographics', 'occupation', 'contains', 'director', 15, true, 1, 'default'),
('Business Owner', 'Self-employed business owner', 'demographics', 'occupation', 'contains', 'business', 10, true, 2, 'default'),
('Self-Employed', 'Self-employed professional', 'demographics', 'occupation', 'contains', 'self', 10, true, 2, 'default');

-- Completeness Scoring Rules
INSERT INTO crm_lead_scoring_rules (
    rule_name, rule_description, rule_category, field_name, operator, field_value,
    score_points, is_active, priority, tenant_id
) VALUES
('Email Provided', 'Lead provided email address', 'completeness', 'email', 'is_not_empty', NULL, 5, true, 1, 'default'),
('Company Details', 'Company name provided', 'completeness', 'company_name', 'is_not_empty', NULL, 5, true, 1, 'default'),
('Location Details', 'Pincode provided', 'completeness', 'pincode', 'is_not_empty', NULL, 3, true, 2, 'default');

-- Source Quality Scoring Rules
INSERT INTO crm_lead_scoring_rules (
    rule_name, rule_description, rule_category, field_name, operator, field_value,
    score_points, is_active, priority, tenant_id
) VALUES
('Quality Source - Referral', 'Lead from referral source', 'source', 'source', 'equals', 'referral', 10, true, 1, 'default'),
('Quality Source - Partner', 'Lead from partner', 'source', 'source', 'equals', 'partner', 10, true, 1, 'default'),
('Good Source - Website', 'Lead from website', 'source', 'source', 'equals', 'website', 5, true, 2, 'default'),
('Good Source - Walk-in', 'Walk-in lead', 'source', 'source', 'equals', 'walk_in', 5, true, 2, 'default');

-- ============================================================================
-- LEAD ASSIGNMENT RULES
-- Automatic lead routing and distribution
-- ============================================================================

-- Default Round Robin Assignment
INSERT INTO crm_lead_assignment_rules (
    rule_name, rule_description, priority, conditions, assignment_type,
    is_active, tenant_id
) VALUES
('Default Round Robin', 'Distribute all new leads equally across active sales team', 1, '{}', 'round_robin', true, 'default');

-- High Value Lead - Senior Sales Rep
INSERT INTO crm_lead_assignment_rules (
    rule_name, rule_description, priority, conditions, assignment_type,
    is_active, tenant_id
) VALUES
('High Value Leads - Senior Team', 'Assign high-value leads (>10L) to senior sales representatives', 1, 
'{"loan_amount_required__gte": 1000000}', 'round_robin', true, 'default');

-- Hot Lead Assignment (High Score)
INSERT INTO crm_lead_assignment_rules (
    rule_name, rule_description, priority, conditions, assignment_type,
    is_active, tenant_id
) VALUES
('Hot Leads Priority', 'Immediately assign hot leads (score >= 70) to available team', 1,
'{"lead_score__gte": 70}', 'load_balanced', true, 'default');

-- Load Balanced Assignment with Limits
INSERT INTO crm_lead_assignment_rules (
    rule_name, rule_description, priority, conditions, assignment_type,
    max_leads_per_user, is_active, tenant_id
) VALUES
('Load Balanced Distribution', 'Balance lead distribution with max 20 leads per user', 2,
'{}', 'load_balanced', 20, true, 'default');

-- ============================================================================
-- SUMMARY
-- ============================================================================

-- Total Scoring Rules: 17
-- Categories: Demographics (4), Product (3), Occupation (6), Completeness (3), Source (4)
-- 
-- Total Assignment Rules: 4
-- Strategies: Round Robin (2), Load Balanced (2)
--
-- These rules provide:
-- 1. Intelligent lead scoring (0-100 points)
-- 2. Temperature classification (Hot/Warm/Cold)
-- 3. Automatic lead distribution
-- 4. Load balancing with limits
-- 5. Priority-based assignment

-- ============================================================================
-- USAGE
-- ============================================================================
-- 
-- To apply these rules:
-- 1. Run this SQL script on your database
-- 2. Restart the backend application
-- 3. Create a test lead via API or UI
-- 4. Check that the lead gets auto-scored
-- 5. Verify that the lead gets auto-assigned
--
-- To customize:
-- 1. Modify rule_name, field_value, and score_points
-- 2. Add new rules for your business logic
-- 3. Adjust priorities to control rule execution order
-- 4. Set is_active = false to disable rules temporarily
-- 
-- ============================================================================
