# EOM-008 — Department Management System (DMS)

## Overview

Department Management is one of the most reused modules in the entire platform. Unlike most ERP systems, a department in ARTH.OS is not just an HR concept. It is a business capability.

A department owns:

- People
- Budget
- Cost center
- Profit center
- Services
- Workflows
- KPIs
- SLAs
- Assets
- AI metrics

This makes Department Management a core enterprise service.

---

## Vision

Departments are organizational capabilities.

Example:

```text
Enterprise
↓
Branch
↓
Operations
↓
Loan Operations
↓
Gold Loan Operations
↓
Gold Appraisal Team
```

Every department can contain:

- Sections
- Teams
- Positions
- Employees
- Budgets
- Assets
- Workflows

---

## Enterprise Hierarchy

```text
Enterprise
↓
Business Unit
↓
Branch
↓
Department
↓
Section
↓
Team
↓
Position
↓
Employee
```

---

## Standard Departments

Default templates:

```text
HR
Finance
Accounts
Operations
Loans
Gold Loan
Deposits
Collections
Recovery
Treasury
Forex
CRM
Customer Service
IT
Legal
Compliance
Internal Audit
Risk
Procurement
Administration
Marketing
Training
Digital Banking
```

---

## Department Dashboard

### KPIs

- Departments
- Employees
- Vacancies
- Budget
- Actual Expense
- SLA
- Pending Workflows
- Assets
- Projects
- AI Score

### Charts

- Employee distribution
- Budget utilization
- SLA performance
- Workload trend
- Productivity
- Leave trend

---

## Department Workspace

```text
Dashboard
↓
Department Directory
↓
Department Profile
↓
Organization
↓
Employees
↓
Budget
↓
Services
↓
Assets
↓
Reports
```

---

## Department Directory

### Enterprise grid columns

- Department Code
- Department Name
- Branch
- Business Unit
- Department Head
- Employees
- Vacancies
- Budget
- Status
- Health

### Features

- Search
- Filters
- Saved views
- Bulk update
- Export
- AI search

---

## Department Profile

### Tabs

- Overview
- Organization
- Employees
- Sections
- Teams
- Positions
- Budget
- Assets
- Services
- Projects
- Documents
- Workflows
- Reports
- Timeline
- Audit
- AI

---

## Create Department Wizard

### Step 1 — General

Fields:

- Department Code
- Department Name
- Display Name
- Department Type
- Business Unit
- Branch
- Status

### Step 2 — Hierarchy

Fields:

- Parent Department
- Level
- Department Head
- Reporting Department
- Assistant Head

### Step 3 — Financial Mapping

Fields:

- Cost Center
- Profit Center
- Budget Owner
- GL Mapping
- Expense Category

### Step 4 — Operations

Fields:

- Working Hours
- Shift
- Business Calendar
- Service Window
- Capacity
- SLA Profile

### Step 5 — Organization

Fields:

- Sections
- Teams
- Positions
- Employee Capacity
- Approval Hierarchy

### Step 6 — Services

Example:

```text
HR
↓
Recruitment
↓
Payroll
↓
Attendance
↓
Performance
```

Each department owns its service catalog.

### Step 7 — Assets

Assign:

- Laptops
- Vehicles
- Furniture
- Software Licenses
- Equipment

### Step 8 — Documents

Upload:

- Department SOP
- Policies
- Manuals
- Organization Chart
- Budget
- Compliance Documents

### Step 9 — Review and Create

Flow:

```text
Review
↓
Approval
↓
Create
```

---

## Department Organization

```text
Department Head
↓
Section
↓
Team
↓
Position
↓
Employee
```

---

## Department Budget

Supports:

```text
Annual
↓
Quarterly
↓
Monthly
↓
Actual
↓
Forecast
↓
Variance
```

---

## Department Services

Every department owns services.

### Operations

- Loan Processing
- Disbursement
- Collection Support

### HR

- Recruitment
- Payroll
- Training

### Finance

- Accounting
- Budget
- Taxation

---

## SLA Management

Every service has:

```text
Target
↓
Actual
↓
Breach
↓
Penalty
↓
Escalation
```

---

## Department Projects

Track:

- Projects
- Tasks
- Milestones
- Budget
- Timeline

---

## Department Assets

Displays:

- Computers
- Software
- Vehicles
- Furniture
- Mobile Devices
- Licenses

---

## Department Performance

### KPIs

- Employee Productivity
- SLA
- Budget
- Revenue
- Expenses
- Projects
- Training
- Attendance

---

## Department Health Score

Calculated from:

- Budget variance
- SLA compliance
- Vacancy rate
- Employee productivity
- Audit findings
- Workflow backlog
- Asset utilization
- Compliance status

Example:

```text
Department Health: 92%
Rating: ★★★★★
```

---

## Workflow

### Department creation

```text
Draft
↓
HR Review
↓
Finance Review
↓
Operations Review
↓
Enterprise Approval
↓
Active
```

---

## AI Features

Example capabilities:

```text
Show overloaded departments.
↓
Recommend more employees.
↓
Find unused assets.
↓
Predict staffing requirements.
↓
Analyze SLA failures.
↓
Suggest department restructuring.
↓
Recommend automation opportunities.
```

---

## Reports

Standard reports:

- Department Register
- Budget vs Actual
- Employee Register
- Position Register
- Asset Register
- SLA Report
- Project Report
- Productivity Report
- Department Health
- Service Performance

---

## Database Design

### Core table

### department

| Field | Type |
| --- | --- |
| id | UUID |
| branch_id | UUID |
| business_unit_id | UUID |
| code | VARCHAR(30) |
| name | VARCHAR(200) |
| parent_department_id | UUID |
| head_employee_id | UUID |
| cost_center_id | UUID |
| profit_center_id | UUID |
| status | ENUM |
| created_at | TIMESTAMP |

### Supporting tables

- department_service
- department_budget
- department_asset
- department_document
- department_position
- department_section
- department_team
- department_project
- department_workflow
- department_kpi
- department_sla
- department_ai
- department_audit

---

## APIs

```text
GET    /api/v1/departments
POST   /api/v1/departments
GET    /api/v1/departments/{id}
PUT    /api/v1/departments/{id}
PATCH  /api/v1/departments/{id}/status
GET    /api/v1/departments/{id}/dashboard
GET    /api/v1/departments/{id}/analytics
GET    /api/v1/departments/{id}/health
```

---

## Events

```text
DEPARTMENT_CREATED
DEPARTMENT_UPDATED
HEAD_ASSIGNED
SERVICE_ADDED
BUDGET_UPDATED
POSITION_CREATED
SLA_BREACHED
HEALTH_CHANGED
```

---

## Backend Structure

```text
services/eom/department/
├── domain/
├── application/
├── infrastructure/
├── api/
├── analytics/
├── ai/
├── events/
└── tests/
```

---

## Frontend Structure

```text
modules/eom/department/
├── dashboard/
├── directory/
├── create/
├── profile/
├── budget/
├── services/
├── assets/
├── analytics/
├── reports/
├── settings/
└── components/
```

---

## Integration Matrix

| Module | Integration |
| --- | --- |
| HRMS | Employee assignment and reporting structure |
| Accounting | Cost center, profit center, budget, GL mapping |
| Lending | Loan operations ownership |
| Deposits | Deposit operations ownership |
| Treasury | Treasury operations |
| CRM | Customer service ownership |
| Procurement | Purchase approvals |
| Asset Management | Asset ownership |
| Workflow Engine | Department approval chains |
| Document Management | SOPs and policies |
| AI Platform | Capacity planning and recommendations |

---

## Department 360

Instead of opening multiple screens, every department should have a Department 360 page with synchronized views.

### Executive View

- Budget
- Headcount
- Productivity
- Health score

### Financial View

- Budget vs actual
- Cost center
- Profit center
- Expenses

### People View

- Employees
- Vacancies
- Skills
- Performance

### Operations View

- Service catalog
- SLA
- Workflow backlog
- Projects

### Risk View

- Audit findings
- Compliance gaps
- Pending actions
- Policy violations

### Asset View

- Equipment
- Software
- Licenses
- Utilization

### AI View

- Staffing forecast
- Automation opportunities
- Workload prediction
- Efficiency recommendations

---

## Maturity Levels

| Level | Capability |
| --- | --- |
| Level 1 | Department master data |
| Level 2 | Budget and financial ownership |
| Level 3 | Service catalog and SLAs |
| Level 4 | Analytics and health scoring |
| Level 5 | AI-driven optimization and capacity planning |

---

## Definition of Done

Department Management is complete when it provides:

- Department hierarchy
- Section and team management
- Financial mappings
- Service catalog
- Budget ownership
- Asset ownership
- Workflow integration
- Department 360
- Health scoring
- AI insights
- Audit trail
- Enterprise reporting

---

## Strategic Recommendation

This is where ARTH.OS can extend beyond traditional ERP systems.

Instead of treating departments only as organizational units, introduce a Business Capability Registry.

Each department should explicitly own:

- Business capabilities such as loan processing, payroll, or treasury settlement
- Service catalog
- SLAs and OLAs
- Responsible applications
- Data ownership
- Business rules
- Regulatory responsibilities
- AI models used by that department

This makes ARTH.OS not just an ERP, but an Enterprise Operating System where every business capability has a clear owner, measurable performance, and governance.

---

## Next Package

The next logical module is EOM-009 — Section & Team Management, where ARTH.OS should model:

- Sections
- Teams
- Squad structures
- Reporting lines
- Matrix organizations
- Workforce capacity
- Skill-based teams
- Team KPIs
- Team workloads
- Cross-functional project teams

That completes the people and organizational hierarchy before moving into grades, designations, and position management.
