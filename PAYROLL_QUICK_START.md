# HRMS Payroll Management - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### 1. Run Database Migration
```bash
# Execute migration script
psql -U postgres -d nbfc_suite < database/migrations/add_payroll_tables_migration.sql
```

### 2. Start Backend Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 3. Start Frontend Server
```bash
cd frontend/apps/admin-portal
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Payroll Dashboard: http://localhost:3000/payroll/dashboard

---

## 📱 Common User Tasks

### Setup Salary Components
1. Go to Payroll → Components
2. Click **"+ Create Component"**
3. Enter details (code, name, type, calculation)
4. Save component

### Create Salary Structure
1. Go to Payroll → Structures
2. Click **"+ Create Structure"**
3. Enter structure details (name, grade, department)
4. Select components and configure calculations
5. Save structure

### Assign Salary to Employee
1. Go to Payroll → Employee Salaries
2. Select employee
3. Choose salary structure
4. Enter CTC and bank details
5. Set effective date
6. Save assignment

### Run Monthly Payroll
1. Go to Payroll → Processing
2. Click **"+ Create Payroll Run"**
3. Select month and year
4. Click **"Process Payroll"**
5. Review payslips
6. Click **"Approve Payroll"**
7. Generate payment file

### View Payslip
1. Go to Payroll → Payslips
2. Filter by employee/month
3. Click on payslip to view details
4. Download PDF

### Check Statutory Compliance
1. Go to Payroll → Statutory
2. View PF, ESI, PT, TDS tabs
3. Check payment status
4. Download compliance reports

---

## 🔧 API Quick Reference

### Base URL
```
http://localhost:8000/api/payroll
```

### Authentication
```bash
# Add Authorization header
Authorization: Bearer <token>
```

### Common Endpoints

#### Create Salary Component
```bash
POST /components
{
  "component_code": "BASIC",
  "component_name": "Basic Salary",
  "component_type": "EARNING",
  "calculation_type": "FIXED",
  "is_taxable": true,
  "is_part_of_ctc": true
}
```

#### Create Salary Structure
```bash
POST /structures
{
  "structure_code": "STD-001",
  "structure_name": "Standard Structure",
  "effective_from": "2026-01-01",
  "components": [
    {
      "component_id": 1,
      "calculation_type": "FIXED",
      "default_value": 30000
    }
  ]
}
```

#### Assign Salary to Employee
```bash
POST /employee-salaries
{
  "employee_id": 123,
  "structure_id": 1,
  "ctc_annual": 600000,
  "gross_monthly": 50000,
  "net_monthly": 45000,
  "effective_from": "2026-01-01"
}
```

#### Create Payroll Run
```bash
POST /runs
{
  "run_name": "January 2026 Payroll",
  "payroll_month": 1,
  "payroll_year": 2026,
  "pay_date": "2026-01-31",
  "period_start_date": "2026-01-01",
  "period_end_date": "2026-01-31"
}
```

#### Process Payroll
```bash
POST /runs/{run_id}/process
{
  "payroll_run_id": 1,
  "employee_ids": null  // null = process all
}
```

#### Approve Payroll
```bash
POST /runs/{run_id}/approve
{
  "approval_remarks": "Approved for payment"
}
```

---

## 📊 Dashboard Overview

### Statistics Cards
- **Total Employees:** Active employees with salary assignments
- **Active Structures:** Number of active salary structures
- **Pending Runs:** Payroll runs awaiting processing/approval
- **Current Month:** Status of current month payroll
- **Statutory Pending:** Outstanding PF/ESI/PT/TDS payments
- **Pending Form 16:** Form 16 certificates to be issued

### Recent Activities
- Latest payroll runs
- Pending approvals
- Recent payslips generated
- Statutory payments due

---

## 🎯 Key Features

### Salary Management
✅ Flexible salary components (earnings, deductions, employer contributions)  
✅ Multiple calculation types (fixed, % of basic/gross/CTC, formula)  
✅ Reusable salary structures  
✅ Employee salary assignments with effective dates  
✅ Bank details and tax regime configuration  

### Payroll Processing
✅ Monthly payroll execution  
✅ Attendance integration (days worked, LOP)  
✅ Automatic statutory calculations (PF, ESI, PT, TDS)  
✅ Payslip generation with detailed breakdown  
✅ Multi-stage approval workflow  

### Statutory Compliance
✅ **PF:** 12% employee + 12% employer (ceiling: ₹15,000)  
✅ **ESI:** 0.75% employee + 3.25% employer (ceiling: ₹21,000)  
✅ **PT:** Slab-based calculation (state-specific)  
✅ **TDS:** Income tax calculation with deductions  
✅ Compliance record generation  
✅ Challan tracking and payment status  

### Reports & Documents
✅ Payslip PDF generation  
✅ Form 16 annual tax certificate  
✅ Statutory compliance reports  
✅ Payment file generation (NEFT, RTGS, CSV)  
✅ Monthly payroll summary  

---

## 🔐 Default Configuration

### Statutory Limits (India)
- **PF Ceiling:** ₹15,000
- **PF Rate:** 12% employee + 12% employer
- **ESI Ceiling:** ₹21,000
- **ESI Rate:** 0.75% employee + 3.25% employer
- **PT:** State-specific slabs
- **TDS:** Income tax slabs with 4% education cess

### System Components
Pre-configured components:
- BASIC - Basic Salary
- HRA - House Rent Allowance
- CONVEYANCE - Conveyance Allowance
- SPECIAL - Special Allowance
- MEDICAL - Medical Allowance
- PF_EMP - PF Employee Contribution
- ESI_EMP - ESI Employee Contribution
- PT - Professional Tax
- TDS - Tax Deducted at Source

---

## 📝 Sample Data

### Sample Salary Structure
```json
{
  "structure_name": "Software Engineer - L1",
  "structure_code": "SE-L1",
  "grade_level": "L1",
  "department": "Engineering",
  "effective_from": "2026-01-01",
  "components": [
    {
      "component_id": 1,
      "calculation_type": "FIXED",
      "default_value": 30000,
      "is_mandatory": true,
      "display_order": 1
    },
    {
      "component_id": 2,
      "calculation_type": "PERCENTAGE_OF_BASIC",
      "percentage": 40,
      "is_mandatory": true,
      "display_order": 2
    }
  ]
}
```

### Sample Employee Salary Assignment
```json
{
  "employee_id": 123,
  "structure_id": 1,
  "ctc_annual": 720000,
  "gross_monthly": 60000,
  "net_monthly": 52500,
  "bank_name": "HDFC Bank",
  "bank_account_number": "50100123456789",
  "bank_ifsc_code": "HDFC0001234",
  "tax_regime": "OLD",
  "pan_number": "ABCDE1234F",
  "effective_from": "2026-01-01"
}
```

---

## 🐛 Quick Troubleshooting

### Issue: Payroll processing fails
**Solution:** 
- Ensure all employees have active salary assignments
- Check effective dates overlap with payroll period
- Verify attendance data is available

### Issue: Statutory calculation incorrect
**Solution:**
- Check PF/ESI ceilings in service configuration
- Verify component calculation types
- Review state-specific PT slabs

### Issue: Payslip PDF not generating
**Solution:**
- Check PDF generation service is running
- Verify file storage path permissions
- Ensure template files are present

### Issue: Payment file empty
**Solution:**
- Ensure payroll is approved
- Verify employees have bank details
- Check payment status filters

---

## 📞 Need Help?

### Documentation
- Full Documentation: `PAYROLL_MODULE_COMPLETE.md`
- API Reference: http://localhost:8000/docs

### Common URLs
- Dashboard: `/payroll/dashboard`
- Components: `/payroll/components`
- Structures: `/payroll/structures`
- Processing: `/payroll/processing`
- Payslips: `/payroll/payslips`
- Statutory: `/payroll/statutory`

---

## ✅ Pre-Flight Checklist

Before running first payroll:
- [ ] Database migration completed
- [ ] Salary components created
- [ ] Salary structures defined
- [ ] Employees assigned salaries
- [ ] Bank details configured
- [ ] Tax regime selected
- [ ] Attendance data available
- [ ] Test payroll run executed
- [ ] Statutory calculations verified
- [ ] Approval workflow tested

---

**Quick Start Version:** 1.0  
**Last Updated:** July 8, 2026  
**Status:** Ready to Use (Backend Complete, Frontend Pending)
