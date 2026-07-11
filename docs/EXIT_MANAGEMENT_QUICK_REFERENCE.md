# Exit Management - Quick Reference Card

**Quick reference for common operations and API endpoints**

---

## Quick Commands

### Setup & Configuration
```bash
# Configure module
python scripts/configure_exit_management.py

# Seed sample data
python scripts/seed_exit_data.py

# Test API
python scripts/test_exit_api.py

# Verify deployment
python scripts/verify_exit_deployment.py

# Start server
uvicorn backend.main:app --reload
```

---

## API Base URL

```
http://localhost:8000/api/v1/hrms/exit
```

---

## Common Workflows

### 1. Create Resignation

**POST** `/resignations`

```json
{
  "employee_id": "uuid",
  "resignation_type": "voluntary",
  "resignation_date": "2024-12-15",
  "last_working_date": "2025-01-15",
  "notice_period_days": 30,
  "reason_category": "Better Opportunity",
  "reason_details": "Joining new company with better role"
}
```

### 2. Manager Review

**POST** `/resignations/{id}/manager-review`

```json
{
  "manager_comments": "Reviewed and recommend approval",
  "manager_recommendation": "approve"
}
```

### 3. Approve Resignation

**POST** `/resignations/{id}/approve`

```json
{
  "approval_comments": "Approved",
  "actual_last_working_date": "2025-01-15"
}
```

### 4. Complete Clearance

**POST** `/clearances/{id}/complete`

```json
{
  "clearance_remarks": "All items cleared",
  "supporting_documents": "{\"file1.pdf\": \"url\"}"
}
```

### 5. Calculate Settlement

**POST** `/settlements/{id}/calculate`

```json
{
  "basic_salary_amount": 50000,
  "leave_encashment_amount": 10000,
  "gratuity_amount": 100000,
  "tds_amount": 8000
}
```

### 6. Generate Document

**POST** `/resignations/{id}/documents/generate`

```json
{
  "document_type": "experience_letter",
  "template_name": "default",
  "document_number": "EXP2024001",
  "issue_place": "Mumbai"
}
```

---

## Status Enums

### Resignation Status
- `submitted` - Initial submission
- `under_review` - Manager/HR reviewing
- `approved` - Approved by all
- `rejected` - Rejected
- `withdrawn` - Employee withdrew
- `completed` - Exit completed
- `cancelled` - Cancelled

### Clearance Status
- `pending` - Not started
- `in_progress` - In progress
- `completed` - Completed
- `not_applicable` - N/A
- `waived` - Waived

### Settlement Status
- `pending` - Not calculated
- `calculated` - Calculated
- `approved` - Approved
- `processing` - Payment in process
- `paid` - Payment complete
- `on_hold` - On hold
- `rejected` - Rejected

---

## Default Clearances

1. **IT Department** - IT Assets
2. **Admin Department** - Administrative
3. **Finance Department** - Financial
4. **HR Department** - HR
5. **Reporting Manager** - Handover

---

## Settlement Components

### Earnings
- Basic Salary
- Leave Encashment
- Gratuity
- Bonus
- Incentives
- Reimbursements

### Deductions
- Notice Pay Recovery
- Loan Recovery
- Advance Recovery
- Asset Loss Recovery
- TDS
- Professional Tax

---

## Document Types

- `resignation_letter` - Resignation Letter
- `acceptance_letter` - Acceptance Letter
- `experience_letter` - Experience Letter
- `relieving_letter` - Relieving Letter
- `service_certificate` - Service Certificate
- `noc` - No Objection Certificate
- `clearance_form` - Clearance Form
- `fnf_statement` - Full & Final Statement

---

## Filters & Pagination

### Query Parameters

```
?page=1
&per_page=20
&sort_by=created_at
&sort_order=desc
&status=approved
&employee_id=uuid
&resignation_date_from=2024-01-01
&resignation_date_to=2024-12-31
```

---

## Authentication

### Get Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'
```

### Use Token
```bash
curl -X GET "http://localhost:8000/api/v1/hrms/exit/resignations" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Database Quick Queries

```sql
-- Count resignations by status
SELECT status, COUNT(*) 
FROM exit_resignations 
GROUP BY status;

-- Pending clearances
SELECT * FROM exit_clearances 
WHERE status = 'pending';

-- Settlements pending payment
SELECT * FROM exit_settlements 
WHERE status IN ('approved', 'processing');

-- Overdue clearances
SELECT * FROM exit_clearances 
WHERE is_overdue = true;

-- Today's exits
SELECT * FROM exit_resignations 
WHERE last_working_date = CURRENT_DATE;
```

---

## Component Usage (Frontend)

### ExitStatusBadge
```tsx
import { ExitStatusBadge } from '@/components/exit';

<ExitStatusBadge 
  status={resignation.status} 
  type="resignation" 
  size="md" 
/>
```

### ResignationWorkflowStepper
```tsx
import { ResignationWorkflowStepper } from '@/components/exit';

<ResignationWorkflowStepper 
  currentStatus={resignation.status} 
/>
```

### ClearanceChecklist
```tsx
import { ClearanceChecklist } from '@/components/exit';

<ClearanceChecklist 
  clearances={clearances}
  onComplete={handleComplete}
/>
```

### SettlementBreakdown
```tsx
import { SettlementBreakdown } from '@/components/exit';

<SettlementBreakdown 
  settlement={settlement}
  components={components}
  showDetails={true}
/>
```

### DocumentPreview
```tsx
import { DocumentPreview } from '@/components/exit';

<DocumentPreview 
  document={document}
  onDownload={handleDownload}
  onApprove={handleApprove}
/>
```

---

## Service Layer Usage (Frontend)

```typescript
import { exitManagementService } from '@/services/exit.service';

// List resignations
const resignations = await exitManagementService.resignations.list({
  status: 'approved',
  page: 1,
  per_page: 20
});

// Create resignation
const newResignation = await exitManagementService.resignations.create({
  employee_id: 'uuid',
  resignation_date: '2024-12-15',
  last_working_date: '2025-01-15',
  reason_details: 'New opportunity'
});

// Manager review
await exitManagementService.resignations.managerReview(id, {
  manager_comments: 'Approved',
  manager_recommendation: 'approve'
});

// Get dashboard stats
const stats = await exitManagementService.dashboard.getStats();
```

---

## Common Calculations

### Leave Encashment
```
Leave Encashment = Encashable Leaves × Daily Rate
Daily Rate = Monthly Salary / 30
```

### Gratuity (India)
```
Gratuity = (Last Drawn Salary × Years of Service × 15) / 26
Eligible after 5 years of continuous service
```

### Notice Pay Recovery
```
Recovery = Shortfall Days × Daily Rate
Daily Rate = Monthly Salary / 30
```

---

## Error Codes

- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

---

## Logs Location

- Backend: `logs/exit_management.log`
- Database: PostgreSQL logs directory
- Frontend: Browser console

---

## Useful URLs

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Frontend**: http://localhost:3000

---

## File Locations

### Backend
```
backend/
├── shared/database/hrms_models.py
├── services/hrms/
│   ├── schemas/exit_schemas.py
│   ├── services/exit_service.py
│   └── routes/exit_routes.py
└── main.py
```

### Frontend
```
frontend/apps/admin-portal/src/
├── types/exit.types.ts
├── services/exit.service.ts
└── components/exit/
```

### Scripts
```
scripts/
├── configure_exit_management.py
├── seed_exit_data.py
├── test_exit_api.py
└── verify_exit_deployment.py
```

### Database
```
database/migrations/add_exit_management_tables.sql
```

---

## Performance Tips

1. **Use Pagination**: Always paginate large lists
2. **Filter Early**: Apply filters at API level
3. **Index Usage**: Queries use 20+ optimized indexes
4. **Lazy Load**: Load related data only when needed
5. **Cache Dashboard**: Cache dashboard stats for 5 minutes

---

## Security Checklist

- ✓ JWT authentication enabled
- ✓ Role-based access control
- ✓ Tenant isolation
- ✓ Input validation
- ✓ SQL injection prevention
- ✓ XSS protection
- ✓ Audit trails
- ✓ Soft delete support

---

## Backup Commands

```bash
# Backup resignations
pg_dump -U nbfc_user -d nbfc_db -t exit_resignations > resignations_backup.sql

# Backup settlements
pg_dump -U nbfc_user -d nbfc_db -t exit_settlements > settlements_backup.sql

# Full exit module backup
pg_dump -U nbfc_user -d nbfc_db -t 'exit_*' > exit_module_backup.sql

# Restore
psql -U nbfc_user -d nbfc_db < exit_module_backup.sql
```

---

## Statistics Queries

```sql
-- Resignations this month
SELECT COUNT(*) FROM exit_resignations 
WHERE resignation_date >= DATE_TRUNC('month', CURRENT_DATE);

-- Average settlement amount
SELECT AVG(net_payable) FROM exit_settlements 
WHERE status = 'paid';

-- Clearance completion rate
SELECT 
  (COUNT(*) FILTER (WHERE status = 'completed')::FLOAT / COUNT(*)) * 100 
FROM exit_clearances;

-- Top resignation reasons
SELECT reason_category, COUNT(*) 
FROM exit_resignations 
GROUP BY reason_category 
ORDER BY COUNT(*) DESC 
LIMIT 5;
```

---

**Quick Reference Version**: 1.0.0  
**Last Updated**: December 2024
