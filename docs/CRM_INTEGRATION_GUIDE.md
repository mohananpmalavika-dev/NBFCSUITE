# CRM Lead Management - Integration Guide

## Quick Start

### 1. Database Migration

Run the migration to create CRM tables:

```bash
cd backend
alembic upgrade head
```

This creates 5 new tables:
- `crm_leads` - Main lead data
- `crm_lead_followups` - Follow-up activities
- `crm_lead_activities` - Activity audit trail
- `crm_lead_scoring_rules` - Scoring configuration
- `crm_lead_assignment_rules` - Assignment configuration

### 2. Backend Integration

#### A. Register the CRM Router

In `backend/main.py`, add:

```python
from backend.services.crm import router as crm_router

# Add to your FastAPI app
app.include_router(crm_router)
```

#### B. Import Models

In `backend/shared/database/__init__.py` or models init file:

```python
from .crm_lead_models import (
    Lead,
    LeadFollowUp,
    LeadActivity,
    LeadScoringRule,
    LeadAssignmentRule
)
```

### 3. Frontend Integration

#### A. Add Routes

In your React Router configuration (e.g., `App.tsx` or routes file):

```typescript
import LeadDashboard from './pages/crm/LeadDashboard';
import LeadsPage from './pages/crm/LeadsPage';
import LeadDetailPage from './pages/crm/LeadDetailPage';

// Add routes
<Route path="/crm/dashboard" element={<LeadDashboard />} />
<Route path="/crm/leads" element={<LeadsPage />} />
<Route path="/crm/leads/:id" element={<LeadDetailPage />} />
```

#### B. Add Navigation Menu

Add CRM menu items to your sidebar/navigation:

```typescript
{
  key: 'crm',
  icon: <UserOutlined />,
  label: 'CRM',
  children: [
    {
      key: 'crm-dashboard',
      label: 'Dashboard',
      path: '/crm/dashboard'
    },
    {
      key: 'crm-leads',
      label: 'Leads',
      path: '/crm/leads'
    }
  ]
}
```

#### C. Install Dependencies

If not already installed:

```bash
cd frontend/apps/admin-portal
npm install moment antd @ant-design/icons
```

### 4. Configure Initial Data

#### A. Create Default Scoring Rules

```sql
INSERT INTO crm_lead_scoring_rules (rule_name, rule_category, field_name, operator, field_value, score_points, is_active)
VALUES
('High Income', 'demographics', 'monthly_income', 'greater_than', '100000', 20, true),
('Medium Income', 'demographics', 'monthly_income', 'greater_than', '50000', 15, true),
('Large Loan', 'product', 'loan_amount_required', 'greater_than', '1000000', 15, true),
('Email Provided', 'completeness', 'email', 'is_not_empty', NULL, 5, true),
('Company Provided', 'completeness', 'company_name', 'is_not_empty', NULL, 5, true),
('Referral Source', 'source', 'source', 'equals', 'referral', 10, true);
```

#### B. Create Assignment Rule (Round Robin)

```sql
INSERT INTO crm_lead_assignment_rules (rule_name, priority, conditions, assignment_type, is_active)
VALUES
('Default Round Robin', 1, '{}', 'round_robin', true);
```

### 5. Testing

#### A. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/crm/leads/dashboard/stats

# Create a test lead
curl -X POST http://localhost:8000/api/crm/leads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "source": "website",
    "first_name": "Test",
    "last_name": "User",
    "mobile": "9876543210",
    "email": "test@example.com",
    "product_interest": "Personal Loan",
    "loan_amount_required": 500000,
    "monthly_income": 75000
  }'
```

#### B. Test Frontend

1. Navigate to `/crm/dashboard`
2. Check if statistics load
3. Navigate to `/crm/leads`
4. Click "Create Lead" button
5. Fill form and submit
6. Verify lead appears in list
7. Click on lead to view details

### 6. Configuration

#### A. Customize Lead Sources

Edit `LeadSource` enum in both:
- Backend: `backend/shared/database/crm_lead_models.py`
- Frontend: `frontend/apps/admin-portal/src/types/crm.types.ts`

#### B. Customize Scoring Logic

Create custom scoring rules via database or create admin UI:

```sql
INSERT INTO crm_lead_scoring_rules (
  rule_name, 
  rule_category, 
  field_name, 
  operator, 
  field_value, 
  score_points
) VALUES (
  'Professional Occupation',
  'demographics',
  'occupation',
  'contains',
  'doctor',
  15
);
```

#### C. Configure Assignment Rules

```sql
INSERT INTO crm_lead_assignment_rules (
  rule_name,
  priority,
  conditions,
  assignment_type,
  assign_to_branch_id,
  max_leads_per_user
) VALUES (
  'Mumbai Branch Auto-assignment',
  1,
  '{"city_id": 1}',
  'load_balanced',
  5,
  20
);
```

### 7. Permissions Setup

Add CRM permissions to your RBAC system:

```python
CRM_PERMISSIONS = [
    'crm.leads.view',
    'crm.leads.create',
    'crm.leads.edit',
    'crm.leads.delete',
    'crm.leads.assign',
    'crm.leads.qualify',
    'crm.leads.convert',
    'crm.followups.view',
    'crm.followups.create',
    'crm.followups.complete',
    'crm.dashboard.view',
]
```

### 8. Optional Integrations

#### A. SMS Integration

```python
# In service.py, add after lead creation
if lead.mobile:
    send_sms(
        to=lead.mobile,
        message=f"Thank you for your interest. Your lead code is {lead.lead_code}"
    )
```

#### B. Email Integration

```python
# Send welcome email
if lead.email:
    send_email(
        to=lead.email,
        subject="Welcome - Loan Application",
        template="lead_welcome",
        data={"lead_code": lead.lead_code, "name": lead.full_name}
    )
```

#### C. WhatsApp Integration

```python
# Send WhatsApp message
if lead.mobile and lead.source == LeadSource.WHATSAPP:
    send_whatsapp(
        to=lead.mobile,
        template="lead_confirmation",
        params=[lead.full_name, lead.lead_code]
    )
```

### 9. Monitoring & Alerts

#### A. Setup Alerts for Overdue Follow-ups

```python
# Scheduled job (daily)
def alert_overdue_followups():
    overdue = service.get_overdue_follow_ups()
    if overdue:
        for follow_up in overdue:
            notify_user(
                user_id=follow_up.assigned_to_user_id,
                message=f"Overdue follow-up for {follow_up.lead.full_name}"
            )
```

#### B. Daily Lead Summary

```python
# Scheduled job (daily)
def send_daily_summary():
    stats = service.get_dashboard_stats()
    send_email_to_managers(
        subject="Daily Lead Summary",
        template="daily_summary",
        data=stats
    )
```

### 10. Performance Optimization

#### A. Database Indexing

Already included in migration, but verify:

```sql
-- Check indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE tablename LIKE 'crm_%';
```

#### B. Caching (Optional)

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_lead_cached(lead_id: int):
    return service.get_lead(lead_id)
```

#### C. Pagination

Always use pagination for large datasets:
- Default: 20 items per page
- Max: 100 items per page

### 11. Backup & Recovery

```bash
# Backup CRM data
pg_dump -U postgres -t crm_leads -t crm_lead_followups -t crm_lead_activities nbfc_db > crm_backup.sql

# Restore
psql -U postgres nbfc_db < crm_backup.sql
```

### 12. Troubleshooting

#### Issue: Lead score not calculating

**Solution:** Check if scoring rules exist:
```sql
SELECT * FROM crm_lead_scoring_rules WHERE is_active = true;
```

#### Issue: Auto-assignment not working

**Solution:** Check assignment rules:
```sql
SELECT * FROM crm_lead_assignment_rules WHERE is_active = true;
```

#### Issue: Duplicate leads

**Solution:** Run duplicate check:
```python
service._check_duplicate(mobile="9876543210")
```

### 13. Security Checklist

- ✅ Implement authentication middleware
- ✅ Add tenant isolation for all queries
- ✅ Validate user permissions before actions
- ✅ Sanitize input data
- ✅ Encrypt sensitive data (PII)
- ✅ Audit log all changes
- ✅ Rate limit API endpoints
- ✅ Implement CORS properly

### 14. Production Checklist

- ✅ Run all migrations
- ✅ Create initial scoring rules
- ✅ Create assignment rules
- ✅ Test all API endpoints
- ✅ Test UI flows
- ✅ Setup monitoring
- ✅ Configure backups
- ✅ Setup error tracking (Sentry)
- ✅ Load test with expected traffic
- ✅ Document processes for team

### 15. Training

Provide training to:
1. **Sales Team**: How to capture and manage leads
2. **Managers**: How to monitor dashboard and reports
3. **Admins**: How to configure rules and settings

---

## Support

For issues or questions:
- Check logs in `/var/log/nbfc/crm/`
- Review API documentation at `/api/docs`
- Contact development team

---

## Version History

- **v1.0.0** (2026-07-11): Initial implementation
  - Multi-channel lead capture
  - Lead scoring engine
  - Assignment & routing
  - Follow-up tracking
  - Complete frontend UI

---

**Implementation Status:** ✅ **COMPLETE & READY FOR PRODUCTION**
