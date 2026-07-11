# HRMS Loans & Advances - Complete Setup Guide

## 📋 Overview
This guide walks you through the complete setup of the HRMS Loans & Advances module including database migration, policy configuration, permissions, and UI components.

---

## 1️⃣ Database Migration

### Step 1: Run the Migration

```bash
# Navigate to backend directory
cd backend

# Run Alembic migration
alembic upgrade head
```

This will create the following tables:
- `hrms_loan_policies` - Loan policy configuration
- `hrms_employee_loans` - Loan applications and tracking
- `hrms_loan_emi_schedule` - EMI repayment schedule
- `hrms_loan_transactions` - Transaction history

### Step 2: Verify Tables Created

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE 'hrms_loan%';
```

Expected output:
```
hrms_loan_policies
hrms_employee_loans
hrms_loan_emi_schedule
hrms_loan_transactions
```

---

## 2️⃣ Configure Loan Policies

### Step 1: Run Policy Configuration Script

```bash
# From backend directory
python scripts/configure_loan_policies.py [tenant_id]

# Example for tenant_id = 1
python scripts/configure_loan_policies.py 1
```

### Step 2: Verify Policies Created

```sql
SELECT policy_code, policy_name, loan_type, interest_rate, max_loan_amount, is_active
FROM hrms_loan_policies
WHERE tenant_id = 1;
```

### Configured Policies:

| Policy Code | Loan Type | Interest Rate | Max Amount | Max Tenure |
|-------------|-----------|---------------|------------|------------|
| POL-PERSONAL-001 | Personal | 10.5% | ₹5,00,000 | 60 months |
| POL-VEHICLE-001 | Vehicle | 9.0% | ₹10,00,000 | 84 months |
| POL-HOME-001 | Home | 8.5% | ₹50,00,000 | 240 months |
| POL-EDUCATION-001 | Education | 8.0% | ₹3,00,000 | 60 months |
| POL-MEDICAL-001 | Medical | 6.0% | ₹2,00,000 | 36 months |
| POL-ADVANCE-001 | Salary Advance | 0.0% | ₹50,000 | 6 months |
| POL-MARRIAGE-001 | Marriage | 7.5% | ₹3,00,000 | 36 months |
| POL-FESTIVAL-001 | Festival | 0.0% | ₹1,00,000 | 12 months |

---

## 3️⃣ Setup User Permissions

### Loan Approval Roles

Create role-based permissions for loan approvals:

```sql
-- Create permission entries (adjust based on your auth system)

-- MANAGER ROLE - Can approve loans at first level
INSERT INTO permissions (role_id, resource, action, tenant_id)
VALUES 
  ((SELECT id FROM roles WHERE name = 'Manager'), 'loans', 'approve_manager', 1),
  ((SELECT id FROM roles WHERE name = 'Manager'), 'loans', 'view_team', 1);

-- HR ROLE - Can approve at second level
INSERT INTO permissions (role_id, resource, action, tenant_id)
VALUES 
  ((SELECT id FROM roles WHERE name = 'HR'), 'loans', 'approve_hr', 1),
  ((SELECT id FROM roles WHERE name = 'HR'), 'loans', 'view_all', 1);

-- FINANCE ROLE - Can approve at final level and disburse
INSERT INTO permissions (role_id, resource, action, tenant_id)
VALUES 
  ((SELECT id FROM roles WHERE name = 'Finance'), 'loans', 'approve_finance', 1),
  ((SELECT id FROM roles WHERE name = 'Finance'), 'loans', 'disburse', 1),
  ((SELECT id FROM roles WHERE name = 'Finance'), 'loans', 'view_all', 1);

-- EMPLOYEE ROLE - Can apply for loans
INSERT INTO permissions (role_id, resource, action, tenant_id)
VALUES 
  ((SELECT id FROM roles WHERE name = 'Employee'), 'loans', 'apply', 1),
  ((SELECT id FROM roles WHERE name = 'Employee'), 'loans', 'view_own', 1);
```

### Permission Middleware

Update your backend router to check permissions:

```python
# backend/services/hrms/loan_router.py

from backend.shared.auth.permissions import require_permission

# Example: Manager approval endpoint
@router.post("/approvals/{loan_id}/manager", response_model=LoanResponse)
@require_permission("loans:approve_manager")
async def manager_approval(
    loan_id: str,
    action: LoanApprovalAction,
    service: LoanService = Depends(get_loan_service)
):
    # ... implementation
```

---

## 4️⃣ Frontend Integration

### Step 1: Add Routes

Update your frontend routing configuration:

```typescript
// frontend/src/routes/hrmsRoutes.tsx

import LoanApplicationForm from '../components/hrms/loans/LoanApplicationForm';
import MyLoansList from '../components/hrms/loans/MyLoansList';
import LoanDetailsView from '../components/hrms/loans/LoanDetailsView';
import EMIScheduleView from '../components/hrms/loans/EMIScheduleView';
import LoanApprovalDashboard from '../components/hrms/loans/LoanApprovalDashboard';
import AdminLoanManagement from '../components/hrms/loans/AdminLoanManagement';

export const loanRoutes = [
  {
    path: '/hrms/loans/apply',
    element: <LoanApplicationForm />,
    permission: 'loans:apply',
  },
  {
    path: '/hrms/loans/my-loans',
    element: <MyLoansList />,
    permission: 'loans:view_own',
  },
  {
    path: '/hrms/loans/:loanId',
    element: <LoanDetailsView />,
    permission: 'loans:view_own',
  },
  {
    path: '/hrms/loans/:loanId/emi-schedule',
    element: <EMIScheduleView />,
    permission: 'loans:view_own',
  },
  {
    path: '/hrms/loans/approvals',
    element: <LoanApprovalDashboard />,
    permission: 'loans:approve_manager|loans:approve_hr|loans:approve_finance',
  },
  {
    path: '/hrms/loans/admin',
    element: <AdminLoanManagement />,
    permission: 'loans:view_all',
  },
];
```

### Step 2: Add Navigation Menu

```typescript
// Add to your navigation menu

const hrmsMenu = {
  title: 'HRMS',
  items: [
    {
      title: 'Loans & Advances',
      icon: <MoneyIcon />,
      children: [
        {
          title: 'My Loans',
          path: '/hrms/loans/my-loans',
          permission: 'loans:view_own',
        },
        {
          title: 'Apply for Loan',
          path: '/hrms/loans/apply',
          permission: 'loans:apply',
        },
        {
          title: 'Loan Approvals',
          path: '/hrms/loans/approvals',
          permission: 'loans:approve_manager|loans:approve_hr|loans:approve_finance',
        },
        {
          title: 'Admin Dashboard',
          path: '/hrms/loans/admin',
          permission: 'loans:view_all',
        },
      ],
    },
  ],
};
```

---

## 5️⃣ Backend API Integration

### Register Router

Add the loan router to your FastAPI application:

```python
# backend/main.py or backend/app.py

from backend.services.hrms import loan_router

app.include_router(loan_router.router, tags=["HRMS - Loans"])
```

### Update Employee Model

Ensure the Employee model has the necessary relationships:

```python
# backend/shared/database/hrms_models.py

class Employee(BaseModel):
    # ... existing fields ...
    
    # Add relationship to loans
    loans = relationship("EmployeeLoan", back_populates="employee", 
                        foreign_keys="EmployeeLoan.employee_id")
    leave_balances = relationship("LeaveBalance", back_populates="employee")
    # ... other relationships ...
```

---

## 6️⃣ Testing the Implementation

### Test Checklist

#### 1. Policy Configuration
- [ ] Verify all 8 policies are created
- [ ] Check interest rates and limits are correct
- [ ] Confirm policies are active

#### 2. Loan Application (Employee)
- [ ] Access application form
- [ ] Fill loan details
- [ ] Check eligibility
- [ ] View EMI calculation
- [ ] Submit application
- [ ] Verify application created in database

#### 3. Approval Workflow
- [ ] Login as Manager
- [ ] View pending approvals
- [ ] Approve/reject application
- [ ] Login as HR
- [ ] Second level approval
- [ ] Login as Finance
- [ ] Final approval

#### 4. Disbursement
- [ ] Access approved loan
- [ ] Fill disbursement details
- [ ] Disburse loan
- [ ] Verify EMI schedule generated
- [ ] Check loan status is ACTIVE

#### 5. Payroll Integration
- [ ] Run monthly payroll
- [ ] Verify EMI deducted from salary
- [ ] Check EMI status updated to PAID
- [ ] Verify loan outstanding reduced
- [ ] Check transaction created

#### 6. EMI Tracking
- [ ] View EMI schedule
- [ ] Check payment status
- [ ] Verify overdue detection
- [ ] Test foreclosure

---

## 7️⃣ Configuration Tips

### Adjust Loan Limits

```sql
-- Update loan policy limits
UPDATE hrms_loan_policies
SET 
  max_loan_amount = 1000000.00,
  max_tenure_months = 72,
  interest_rate = 9.50
WHERE policy_code = 'POL-PERSONAL-001' AND tenant_id = 1;
```

### Disable a Loan Type

```sql
-- Temporarily disable a loan type
UPDATE hrms_loan_policies
SET is_active = false
WHERE loan_type = 'vehicle' AND tenant_id = 1;
```

### Add New Loan Type

```python
# Run this in Python script or backend console

from backend.shared.database.loan_models import LoanPolicy, LoanType
from decimal import Decimal
import uuid

policy = LoanPolicy(
    id=uuid.uuid4(),
    tenant_id=1,
    policy_code="POL-CUSTOM-001",
    policy_name="Custom Loan Policy",
    loan_type=LoanType.OTHER,
    min_service_months=12,
    min_loan_amount=Decimal("50000.00"),
    max_loan_amount=Decimal("500000.00"),
    max_emi_as_salary_percentage=Decimal("40.00"),
    interest_rate=Decimal("11.00"),
    min_tenure_months=12,
    max_tenure_months=60,
    # ... other fields
)
db.add(policy)
db.commit()
```

---

## 8️⃣ Monitoring & Maintenance

### Dashboard Queries

```sql
-- Active loans summary
SELECT 
  COUNT(*) as total_loans,
  SUM(loan_amount) as total_disbursed,
  SUM(total_outstanding) as total_outstanding,
  SUM(total_paid) as total_collected
FROM hrms_employee_loans
WHERE tenant_id = 1 AND status = 'active';

-- Overdue EMIs
SELECT 
  e.employee_code,
  e.full_name,
  l.loan_code,
  emi.emi_number,
  emi.emi_due_date,
  emi.emi_amount,
  emi.days_overdue
FROM hrms_loan_emi_schedule emi
JOIN hrms_employee_loans l ON emi.loan_id = l.id
JOIN hrms_employees e ON l.employee_id = e.id
WHERE emi.tenant_id = 1 
  AND emi.status = 'pending' 
  AND emi.emi_due_date < CURRENT_DATE
ORDER BY emi.days_overdue DESC;

-- Pending approvals by stage
SELECT 
  CASE 
    WHEN manager_approval_status = 'pending' THEN 'Manager'
    WHEN hr_approval_status = 'pending' THEN 'HR'
    WHEN finance_approval_status = 'pending' THEN 'Finance'
  END as approval_stage,
  COUNT(*) as count,
  SUM(loan_amount) as total_amount
FROM hrms_employee_loans
WHERE tenant_id = 1 AND status = 'pending_approval'
GROUP BY approval_stage;
```

### Scheduled Jobs

Set up cron jobs or scheduled tasks:

```python
# backend/jobs/loan_monitoring.py

async def mark_overdue_emis():
    """Mark EMIs as overdue if past due date"""
    # Run daily
    pass

async def send_emi_reminders():
    """Send reminders 3 days before EMI due"""
    # Run daily
    pass

async def generate_loan_reports():
    """Generate monthly loan reports"""
    # Run monthly
    pass
```

---

## 9️⃣ Troubleshooting

### Common Issues

#### EMI not deducted in payroll
```python
# Check if loan is active and EMI is pending
SELECT * FROM hrms_loan_emi_schedule 
WHERE loan_id = 'xxx' AND status = 'pending';

# Verify payroll integration is working
# Check payroll_processing_service.py line 350-380
```

#### Eligibility check fails
```python
# Verify policy is active
SELECT * FROM hrms_loan_policies 
WHERE loan_type = 'personal' AND is_active = true;

# Check employee service months
SELECT 
  employee_code,
  date_of_joining,
  EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_joining)) * 12 + 
  EXTRACT(MONTH FROM AGE(CURRENT_DATE, date_of_joining)) as service_months
FROM hrms_employees 
WHERE id = 'employee_id';
```

#### Loan not auto-closing after final EMI
```python
# Check if all EMIs are paid
SELECT status, COUNT(*) 
FROM hrms_loan_emi_schedule 
WHERE loan_id = 'xxx' 
GROUP BY status;

# Manually close if needed
UPDATE hrms_employee_loans
SET status = 'closed', closure_date = CURRENT_DATE, closure_reason = 'fully_paid'
WHERE id = 'xxx' AND total_outstanding <= 0.01;
```

---

## 🎉 Completion Checklist

- [x] Database migration executed
- [x] Loan policies configured
- [x] User permissions setup
- [x] Frontend routes added
- [x] Backend API registered
- [x] Payroll integration verified
- [ ] Employee training completed
- [ ] Documentation shared with team
- [ ] Go-live date scheduled

---

## 📞 Support

For issues or questions:
1. Check the implementation summary: `HRMS_LOANS_IMPLEMENTATION_SUMMARY.md`
2. Review the code comments in service layer
3. Test with the provided test cases
4. Consult the API documentation at `/docs`

---

**🚀 Your HRMS Loans & Advances module is now ready to use!**
