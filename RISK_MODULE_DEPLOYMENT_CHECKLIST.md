# 🚀 Risk Management Module - Deployment Checklist

## Pre-Deployment Checklist

### 1. Database Setup ✅

- [ ] **Backup existing database**
  ```bash
  pg_dump -U nbfc_admin -d nbfc_suite > backup_before_risk_module.sql
  ```

- [ ] **Review migration script**
  - File: `backend/database/migrations/create_risk_management_tables.sql`
  - Check table names, constraints, indexes
  - Verify foreign key references

- [ ] **Run migration in test environment first**
  ```bash
  psql -U nbfc_admin -d nbfc_suite_test < backend/database/migrations/create_risk_management_tables.sql
  ```

- [ ] **Verify tables created**
  ```sql
  -- Check all 7 tables exist
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name IN (
    'credit_policies',
    'risk_pricing_rules',
    'exposure_limits',
    'exposure_transactions',
    'risk_ratings',
    'early_warning_signals',
    'early_warning_alerts'
  );
  
  -- Verify indexes
  SELECT tablename, indexname FROM pg_indexes 
  WHERE tablename LIKE '%risk%' OR tablename LIKE '%credit%' OR tablename LIKE '%exposure%';
  ```

- [ ] **Run migration in production**
  ```bash
  # Create snapshot first
  # Then run migration
  psql -U nbfc_admin -d nbfc_suite < backend/database/migrations/create_risk_management_tables.sql
  ```

### 2. Backend Deployment ✅

- [ ] **Verify all files present**
  ```bash
  # Check models
  ls -la backend/shared/database/risk_models.py
  
  # Check service files
  ls -la backend/services/risk/schemas.py
  ls -la backend/services/risk/service.py
  ls -la backend/services/risk/router.py
  ```

- [ ] **Check main.py integration**
  ```bash
  # Verify imports in main.py
  grep -n "risk_models" backend/main.py
  grep -n "risk_router" backend/main.py
  grep -n "Risk Management" backend/main.py
  ```

- [ ] **Install dependencies** (if any new ones)
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

- [ ] **Run backend tests**
  ```bash
  pytest tests/test_risk_service.py -v
  pytest tests/test_risk_router.py -v
  ```

- [ ] **Start backend server**
  ```bash
  uvicorn main:app --reload
  ```

- [ ] **Verify API endpoints**
  - Open http://localhost:8000/docs
  - Look for "Risk Management" tag
  - Test a few endpoints with Swagger UI

### 3. Environment Configuration

- [ ] **Update .env file**
  ```bash
  # Add to .env
  RISK_MODULE_ENABLED=true
  RISK_RATING_MODEL_VERSION=1.0
  RISK_DEFAULT_PD_PERCENTAGE=3.5
  RISK_DEFAULT_LGD_PERCENTAGE=45.0
  RISK_EWS_BATCH_SIZE=100
  RISK_ALERT_RETENTION_DAYS=365
  ```

- [ ] **Update config.py**
  ```python
  # Verify feature flags
  FEATURE_RISK_MANAGEMENT = True
  FEATURE_RISK_BASED_PRICING = True
  FEATURE_EXPOSURE_LIMITS = True
  FEATURE_EARLY_WARNING_SYSTEM = True
  ```

### 4. Frontend Deployment ✅

- [ ] **Verify frontend files**
  ```bash
  # Types
  grep -n "CreditPolicy" frontend/apps/admin-portal/src/types/index.ts
  
  # Service
  ls -la frontend/apps/admin-portal/src/services/risk.service.ts
  
  # Pages
  ls -la frontend/apps/admin-portal/src/app/risk/page.tsx
  ls -la frontend/apps/admin-portal/src/app/risk/policies/page.tsx
  ```

- [ ] **Install frontend dependencies**
  ```bash
  cd frontend/apps/admin-portal
  npm install
  ```

- [ ] **Build frontend**
  ```bash
  npm run build
  ```

- [ ] **Start frontend**
  ```bash
  npm run dev
  ```

- [ ] **Verify pages load**
  - Navigate to http://localhost:3000/risk
  - Check dashboard loads
  - Check policies page loads

### 5. Sample Data Loading

- [ ] **Create sample credit policy**
  ```sql
  INSERT INTO credit_policies (
    tenant_id, policy_code, policy_name, policy_version,
    product_types, customer_segments, loan_categories,
    min_cibil_score, max_debt_to_income_ratio,
    min_loan_amount, max_loan_amount,
    min_age, max_age, max_age_at_maturity,
    allowed_employment_types, min_employment_months,
    max_active_loans, max_enquiries_last_3months,
    allow_defaults, allow_settlements, allow_write_offs,
    requires_bank_statement_months, requires_itr_years,
    is_active, effective_from
  ) VALUES (
    'default', 'POL-STANDARD-001', 'Standard Personal Loan Policy', '1.0',
    ARRAY['personal'], ARRAY['retail'], ARRAY['unsecured'],
    650, 50.00,
    50000, 2000000,
    21, 65, 70,
    ARRAY['salaried', 'self_employed'], 12,
    3, 5,
    false, false, false,
    6, 2,
    true, CURRENT_DATE
  );
  ```

- [ ] **Create sample pricing rule**
  ```sql
  INSERT INTO risk_pricing_rules (
    tenant_id, credit_policy_id, rule_code, rule_name, rule_priority,
    min_credit_score, max_credit_score,
    base_interest_rate, rate_adjustment, final_interest_rate,
    is_active, effective_from
  ) VALUES (
    'default', 1, 'PRICE-A-001', 'Grade A Pricing', 100,
    750, 900,
    11.00, -0.50, 10.50,
    true, CURRENT_DATE
  );
  ```

- [ ] **Create sample exposure limit**
  ```sql
  INSERT INTO exposure_limits (
    tenant_id, limit_code, limit_name, limit_type,
    limit_amount, utilized_amount, available_amount, utilization_percentage,
    warning_threshold_percentage, critical_threshold_percentage,
    breach_action, limit_period, period_start_date, period_end_date,
    is_active
  ) VALUES (
    'default', 'LIM-IND-IT-001', 'IT Industry Limit', 'industry',
    100000000, 0, 100000000, 0,
    75, 90,
    'alert', 'annual', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year',
    true
  );
  ```

- [ ] **Create sample EWS signal**
  ```sql
  INSERT INTO early_warning_signals (
    tenant_id, signal_code, signal_name, signal_category,
    severity_level, risk_weight,
    detection_rule, trigger_threshold, monitoring_period_days,
    is_active, description, recommended_action
  ) VALUES (
    'default', 'DPD-30', 'Days Past Due >= 30', 'payment_behavior',
    'high', 5,
    '{"condition": "dpd", "operator": ">=", "value": 30, "days": 1}',
    30, 30,
    true,
    'Account has reached 30 days past due',
    'Contact customer immediately and initiate collection process'
  );
  ```

### 6. User Permissions & Access Control

- [ ] **Create risk management roles**
  ```sql
  -- Risk Manager role
  INSERT INTO roles (tenant_id, role_name, role_code, description)
  VALUES ('default', 'Risk Manager', 'RISK_MGR', 'Manages credit policies and risk ratings');
  
  -- Risk Analyst role
  INSERT INTO roles (tenant_id, role_name, role_code, description)
  VALUES ('default', 'Risk Analyst', 'RISK_ANALYST', 'Monitors risk metrics and alerts');
  ```

- [ ] **Create permissions**
  ```sql
  -- Credit Policy permissions
  INSERT INTO permissions (permission_code, permission_name, module) VALUES
  ('risk.policies.view', 'View Credit Policies', 'risk_management'),
  ('risk.policies.create', 'Create Credit Policies', 'risk_management'),
  ('risk.policies.edit', 'Edit Credit Policies', 'risk_management'),
  ('risk.policies.delete', 'Delete Credit Policies', 'risk_management'),
  ('risk.policies.approve', 'Approve Credit Policies', 'risk_management');
  
  -- Risk Rating permissions
  INSERT INTO permissions (permission_code, permission_name, module) VALUES
  ('risk.ratings.view', 'View Risk Ratings', 'risk_management'),
  ('risk.ratings.create', 'Create Risk Ratings', 'risk_management'),
  ('risk.ratings.override', 'Override Risk Ratings', 'risk_management');
  
  -- Exposure Limit permissions
  INSERT INTO permissions (permission_code, permission_name, module) VALUES
  ('risk.exposure.view', 'View Exposure Limits', 'risk_management'),
  ('risk.exposure.manage', 'Manage Exposure Limits', 'risk_management');
  
  -- EWS permissions
  INSERT INTO permissions (permission_code, permission_name, module) VALUES
  ('risk.alerts.view', 'View Early Warning Alerts', 'risk_management'),
  ('risk.alerts.action', 'Take Action on Alerts', 'risk_management');
  ```

- [ ] **Assign permissions to roles**
  ```sql
  -- Risk Manager gets all permissions
  INSERT INTO role_permissions (role_id, permission_id)
  SELECT r.id, p.id 
  FROM roles r, permissions p 
  WHERE r.role_code = 'RISK_MGR' 
  AND p.module = 'risk_management';
  ```

### 7. Navigation Menu Update

- [ ] **Update navigation configuration**
  ```typescript
  // frontend/apps/admin-portal/src/lib/navigation.ts
  {
    title: 'Risk Management',
    icon: Shield,
    children: [
      {
        title: 'Dashboard',
        href: '/risk',
        icon: LayoutDashboard,
      },
      {
        title: 'Credit Policies',
        href: '/risk/policies',
        icon: FileText,
      },
      {
        title: 'Risk-Based Pricing',
        href: '/risk/pricing',
        icon: TrendingUp,
      },
      {
        title: 'Exposure Limits',
        href: '/risk/exposure',
        icon: DollarSign,
      },
      {
        title: 'Risk Ratings',
        href: '/risk/ratings',
        icon: Shield,
      },
      {
        title: 'Early Warning Alerts',
        href: '/risk/alerts',
        icon: AlertTriangle,
      },
    ],
  }
  ```

## Post-Deployment Verification

### 1. API Testing

- [ ] **Test policy evaluation**
  ```bash
  curl -X POST http://localhost:8000/api/v1/risk/policies/evaluate \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -d '{
      "customer_id": "test-customer",
      "loan_amount": 500000,
      "tenure_months": 36,
      "credit_score": 750,
      "monthly_income": 50000,
      "existing_obligations": 15000,
      "age": 32,
      "employment_type": "salaried",
      "product_type": "personal",
      "loan_category": "unsecured"
    }'
  ```

- [ ] **Test pricing calculation**
  ```bash
  curl -X POST http://localhost:8000/api/v1/risk/pricing-rules/calculate \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -d '{
      "customer_id": "test-customer",
      "loan_amount": 500000,
      "tenure_months": 36,
      "credit_score": 750,
      "employment_type": "salaried",
      "loan_category": "unsecured",
      "product_type": "personal"
    }'
  ```

- [ ] **Test dashboard summary**
  ```bash
  curl http://localhost:8000/api/v1/risk/dashboard/summary \
    -H "Authorization: Bearer YOUR_TOKEN"
  ```

### 2. Frontend Testing

- [ ] **Dashboard loads without errors**
  - Visit `/risk`
  - Check all stat cards load
  - Verify module cards display

- [ ] **Policies page works**
  - Visit `/risk/policies`
  - Verify table loads
  - Test search functionality
  - Test filters
  - Test pagination

- [ ] **API integration works**
  - Open browser console
  - Check for no errors
  - Verify API calls succeed

### 3. Performance Testing

- [ ] **Check query performance**
  ```sql
  -- Enable query timing
  \timing
  
  -- Test policy list query
  SELECT * FROM credit_policies WHERE tenant_id = 'default' AND is_active = true LIMIT 20;
  
  -- Test rating statistics
  SELECT risk_grade, COUNT(*) 
  FROM risk_ratings 
  WHERE tenant_id = 'default' AND rating_type = 'customer'
  GROUP BY risk_grade;
  
  -- Test exposure utilization
  SELECT * FROM exposure_limits 
  WHERE tenant_id = 'default' AND utilization_percentage >= 75;
  ```

- [ ] **Check API response times**
  - All endpoints should respond < 1 second
  - Dashboard summary < 500ms
  - List endpoints < 200ms

### 4. Integration Testing

- [ ] **Test with loan application**
  - Create a loan application
  - Trigger policy evaluation
  - Verify risk rating creation
  - Check exposure limit utilization

- [ ] **Test with existing customers**
  - Get customer risk rating
  - Evaluate eligibility
  - Calculate pricing

## Monitoring Setup

### 1. Database Monitoring

- [ ] **Create monitoring queries**
  ```sql
  -- Policy usage
  CREATE VIEW v_policy_usage AS
  SELECT 
    p.policy_code,
    p.policy_name,
    COUNT(DISTINCT la.id) as applications_count,
    AVG(la.credit_score) as avg_credit_score
  FROM credit_policies p
  LEFT JOIN loan_applications la ON la.credit_score >= p.min_cibil_score
  WHERE p.is_active = true
  GROUP BY p.id, p.policy_code, p.policy_name;
  
  -- Exposure utilization
  CREATE VIEW v_exposure_summary AS
  SELECT 
    limit_type,
    COUNT(*) as total_limits,
    SUM(utilized_amount) as total_utilized,
    SUM(limit_amount) as total_limit,
    AVG(utilization_percentage) as avg_utilization,
    COUNT(CASE WHEN is_breached THEN 1 END) as breached_count
  FROM exposure_limits
  WHERE is_active = true
  GROUP BY limit_type;
  
  -- Alert statistics
  CREATE VIEW v_alert_summary AS
  SELECT 
    status,
    severity_level,
    COUNT(*) as alert_count,
    AVG(EXTRACT(EPOCH FROM (resolved_at - alert_date))/3600) as avg_resolution_hours
  FROM early_warning_alerts
  WHERE alert_date >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY status, severity_level;
  ```

### 2. Application Monitoring

- [ ] **Setup logging**
  ```python
  # Add to logging configuration
  logging.getLogger('backend.services.risk').setLevel(logging.INFO)
  ```

- [ ] **Monitor key metrics**
  - Policy evaluation count/day
  - Pricing calculation count/day
  - Alert generation rate
  - Exposure breach events
  - Rating override frequency

### 3. Alerts Configuration

- [ ] **Setup critical alerts**
  - Exposure limit breach
  - Critical EWS alerts not acknowledged in 1 hour
  - High-risk customer increase > 10%
  - Policy evaluation failures

## Rollback Plan

If issues arise:

1. **Database rollback**
   ```bash
   psql -U nbfc_admin -d nbfc_suite < backup_before_risk_module.sql
   ```

2. **Code rollback**
   ```bash
   git revert <commit_hash>
   ```

3. **Disable module**
   ```bash
   # Update .env
   RISK_MODULE_ENABLED=false
   ```

## Training & Documentation

- [ ] **User training completed**
  - Risk managers trained on policy configuration
  - Analysts trained on monitoring
  - Loan officers trained on evaluation

- [ ] **Documentation published**
  - API documentation accessible
  - User guides available
  - Admin guides distributed

## Sign-off

- [ ] **Business Owner**: _____________________ Date: _______
- [ ] **Technical Lead**: _____________________ Date: _______
- [ ] **QA Lead**: _____________________ Date: _______
- [ ] **Operations**: _____________________ Date: _______

---

## Post-Go-Live (Week 1)

- [ ] Monitor error logs daily
- [ ] Review API performance metrics
- [ ] Check database query performance
- [ ] Collect user feedback
- [ ] Address critical issues immediately

## Post-Go-Live (Month 1)

- [ ] Analyze usage patterns
- [ ] Optimize slow queries
- [ ] Review and adjust policies based on data
- [ ] Plan enhancements based on feedback
- [ ] Update documentation with learnings

---

**Deployment Date**: _____________
**Go-Live Date**: _____________
**Module Version**: 1.0.0
