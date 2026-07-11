# HRMS Loans & Advances - Quick Reference Guide

## 🚀 Quick Start (5 Minutes)

### 1. Run Database Migration
```bash
cd backend
alembic upgrade head
```

### 2. Configure Loan Policies
```bash
python scripts/configure_loan_policies.py 1
```

### 3. Verify Setup
```sql
SELECT COUNT(*) FROM hrms_loan_policies WHERE is_active = true;
-- Should return 8 policies
```

**Done!** The module is ready to use.

---

## 📋 Common Tasks

### For Employees

#### Apply for a Loan
1. Go to **HRMS → Loans & Advances → Apply for Loan**
2. Fill loan details (type, amount, tenure, purpose)
3. Check eligibility
4. Enter bank details
5. Review and submit

#### Check Loan Status
- **My Loans** → View list of all applications
- Click **View** to see detailed status
- Check approval workflow progress

#### View EMI Schedule
- Open loan details
- Click **View EMI Schedule**
- See all upcoming and paid EMIs

### For Managers/HR/Finance

#### Approve Loans
1. Go to **Loan Approval Dashboard**
2. Select your approval tab (Manager/HR/Finance)
3. Review application details
4. Click **Approve** or **Reject**
5. Add comments (required for rejection)

#### Disburse Loan (Finance Only)
1. View approved loan
2. Click **Disburse**
3. Enter disbursement date and mode
4. Confirm disbursement
5. EMI schedule generated automatically

### For HR Admin

#### Monitor Loans
```sql
-- Dashboard Query
SELECT 
  status,
  COUNT(*) as count,
  SUM(loan_amount) as total_amount
FROM hrms_employee_loans
WHERE tenant_id = 1 AND is_deleted = false
GROUP BY status;
```

#### Check Overdue EMIs
```sql
SELECT 
  e.employee_name,
  l.loan_code,
  emi.emi_due_date,
  emi.emi_amount,
  emi.days_overdue
FROM hrms_loan_emi_schedule emi
JOIN hrms_employee_loans l ON emi.loan_id = l.id
JOIN hrms_employees e ON l.employee_id = e.id
WHERE emi.status = 'pending' 
  AND emi.emi_due_date < CURRENT_DATE
ORDER BY emi.days_overdue DESC;
```

---

## 🔧 Configuration

### Modify Loan Policy

```sql
-- Update interest rate
UPDATE hrms_loan_policies
SET interest_rate = 12.00
WHERE policy_code = 'POL-PERSONAL-001';

-- Update max loan amount
UPDATE hrms_loan_policies
SET max_loan_amount = 750000.00
WHERE policy_code = 'POL-VEHICLE-001';

-- Disable a loan type
UPDATE hrms_loan_policies
SET is_active = false
WHERE loan_type = 'festival_advance';
```

### Add New Loan Policy

```python
from backend.shared.database.loan_models import LoanPolicy, LoanType
from decimal import Decimal
import uuid

policy = LoanPolicy(
    id=uuid.uuid4(),
    tenant_id=1,
    policy_code="POL-CUSTOM-001",
    policy_name="Custom Loan",
    loan_type=LoanType.OTHER,
    min_service_months=6,
    min_loan_amount=Decimal("25000"),
    max_loan_amount=Decimal("250000"),
    max_emi_as_salary_percentage=Decimal("35.00"),
    interest_rate=Decimal("10.00"),
    min_tenure_months=12,
    max_tenure_months=48,
    repayment_frequency="monthly",
    is_active=True
)
db.add(policy)
db.commit()
```

---

## 📊 API Endpoints

### Employee APIs
```
POST   /api/v1/hrms/loans/check-eligibility
POST   /api/v1/hrms/loans/calculate-emi
POST   /api/v1/hrms/loans/applications
GET    /api/v1/hrms/loans/applications
GET    /api/v1/hrms/loans/applications/{id}
PUT    /api/v1/hrms/loans/applications/{id}
POST   /api/v1/hrms/loans/applications/{id}/submit
POST   /api/v1/hrms/loans/applications/{id}/cancel
GET    /api/v1/hrms/loans/applications/{id}/emi-schedule
GET    /api/v1/hrms/loans/my-summary
```

### Approval APIs
```
POST   /api/v1/hrms/loans/approvals/{id}/manager
POST   /api/v1/hrms/loans/approvals/{id}/hr
POST   /api/v1/hrms/loans/approvals/{id}/finance
```

### Admin APIs
```
GET    /api/v1/hrms/loans/all
GET    /api/v1/hrms/loans/dashboard-stats
POST   /api/v1/hrms/loans/disbursements/{id}
POST   /api/v1/hrms/loans/applications/{id}/foreclose
```

---

## 🔍 Troubleshooting

### Issue: EMI not deducted in payroll

**Check:**
```sql
-- Verify EMI is pending
SELECT * FROM hrms_loan_emi_schedule
WHERE loan_id = 'xxx' AND status = 'pending'
  AND emi_due_date BETWEEN '2024-01-01' AND '2024-01-31';

-- Check loan is active
SELECT status FROM hrms_employee_loans WHERE id = 'xxx';
```

**Fix:**
- Ensure loan status is 'active'
- Verify EMI due date is in payroll month
- Check payroll integration code

### Issue: Eligibility check fails

**Check:**
```sql
-- Verify active policy exists
SELECT * FROM hrms_loan_policies
WHERE loan_type = 'personal' AND is_active = true;

-- Check employee service
SELECT 
  EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_joining)) * 12 + 
  EXTRACT(MONTH FROM AGE(CURRENT_DATE, date_of_joining)) as service_months
FROM hrms_employees WHERE id = 'xxx';
```

**Fix:**
- Activate relevant policy
- Verify employee service duration
- Check salary details are configured

### Issue: Loan not closing after final EMI

**Check:**
```sql
-- Verify all EMIs paid
SELECT status, COUNT(*)
FROM hrms_loan_emi_schedule
WHERE loan_id = 'xxx'
GROUP BY status;
```

**Manual Close:**
```sql
UPDATE hrms_employee_loans
SET 
  status = 'closed',
  closure_date = CURRENT_DATE,
  closure_reason = 'fully_paid',
  total_outstanding = 0.00
WHERE id = 'xxx';
```

---

## 📈 Reports

### Monthly Loan Report
```sql
SELECT 
  DATE_TRUNC('month', application_date) as month,
  loan_type,
  COUNT(*) as applications,
  SUM(loan_amount) as total_amount,
  SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
  SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
FROM hrms_employee_loans
WHERE tenant_id = 1 
  AND application_date >= '2024-01-01'
GROUP BY DATE_TRUNC('month', application_date), loan_type
ORDER BY month DESC, loan_type;
```

### Collection Report
```sql
SELECT 
  DATE_TRUNC('month', payment_date) as month,
  SUM(amount_paid) as total_collected,
  SUM(principal_paid) as principal_collected,
  SUM(interest_paid) as interest_collected,
  COUNT(DISTINCT loan_id) as active_loans
FROM hrms_loan_emi_schedule
WHERE status = 'paid' 
  AND payment_date >= '2024-01-01'
GROUP BY DATE_TRUNC('month', payment_date)
ORDER BY month DESC;
```

### Overdue Analysis
```sql
SELECT 
  e.department_id,
  d.department_name,
  COUNT(DISTINCT l.id) as overdue_loans,
  SUM(emi.emi_amount) as overdue_amount,
  AVG(emi.days_overdue) as avg_days_overdue
FROM hrms_loan_emi_schedule emi
JOIN hrms_employee_loans l ON emi.loan_id = l.id
JOIN hrms_employees e ON l.employee_id = e.id
LEFT JOIN hrms_departments d ON e.department_id = d.id
WHERE emi.status = 'overdue'
GROUP BY e.department_id, d.department_name
ORDER BY overdue_amount DESC;
```

---

## 🔐 Permissions

### Setup Roles
```sql
-- Manager: Can approve at first level
INSERT INTO permissions (role, resource, action)
VALUES ('manager', 'loans', 'approve_manager');

-- HR: Can approve at second level
INSERT INTO permissions (role, resource, action)
VALUES ('hr', 'loans', 'approve_hr');

-- Finance: Can approve and disburse
INSERT INTO permissions (role, resource, action)
VALUES 
  ('finance', 'loans', 'approve_finance'),
  ('finance', 'loans', 'disburse');

-- Employee: Can apply and view own
INSERT INTO permissions (role, resource, action)
VALUES 
  ('employee', 'loans', 'apply'),
  ('employee', 'loans', 'view_own');
```

---

## 🎯 Best Practices

### For Policy Configuration
- ✅ Set realistic interest rates based on market
- ✅ Configure appropriate eligibility criteria
- ✅ Keep max EMI % reasonable (30-40% of salary)
- ✅ Review and update policies quarterly

### For Approvals
- ✅ Review eligibility before approving
- ✅ Verify employee salary can handle EMI
- ✅ Check active loan count
- ✅ Add meaningful comments
- ✅ Process within 48 hours

### For Monitoring
- ✅ Review overdue EMIs daily
- ✅ Send reminders 3 days before due date
- ✅ Generate monthly collection reports
- ✅ Analyze loan portfolio regularly

---

## 🆘 Support

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Not eligible for loan" | Failed eligibility check | Check service duration, salary, active loans |
| "Only draft applications can be submitted" | Wrong status | Create new application |
| "Loan is not pending approval" | Already processed | Check current status |
| "Only approved loans can be disbursed" | Not yet approved | Complete approval workflow |

### Getting Help
1. Check this quick reference
2. Review setup guide: `HRMS_LOANS_SETUP_GUIDE.md`
3. Check implementation summary: `HRMS_LOANS_IMPLEMENTATION_SUMMARY.md`
4. View API docs: `/docs` endpoint

---

## 📞 Quick Contact

**Database Issues:** Check migration and table structure  
**API Issues:** Review backend logs and endpoint documentation  
**UI Issues:** Check browser console and component props  
**Business Logic:** Review service layer and eligibility rules

---

## ✅ Daily Checklist

### Morning
- [ ] Check pending approvals
- [ ] Review overdue EMIs
- [ ] Process yesterday's applications

### End of Day
- [ ] Generate daily report
- [ ] Send EMI reminders
- [ ] Update dashboard statistics

### Month End
- [ ] Process payroll with EMI deductions
- [ ] Generate monthly collection report
- [ ] Review loan portfolio
- [ ] Update policies if needed

---

**Last Updated:** January 2024  
**Version:** 1.0  
**Module Status:** Production Ready ✅
