# EOM-012 — Enterprise Position Management System (EPMS)

## Overview

Position Management is one of the most important foundations of the entire HRMS architecture. Employees are temporary; positions are permanent. This module becomes the backbone for understanding vacancies, ownership, authority, budget, transfers, promotions, reporting structures, and succession planning.

The guiding principle is simple:

```text
Employee → Position → Department → Branch
```

Never assign employees directly to departments.

---

## Philosophy

Every role in the enterprise should be modeled as a position that can be filled, vacated, transferred, budgeted, and monitored over time.

This makes transfers, vacancies, promotions, and budgeting easier and more reliable.

---

## Enterprise Hierarchy

```text
Enterprise
↓
Legal Entity
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

Everything ultimately ends at position.

---

## What is a Position?

A position is not simply a title such as Manager. It is a unique organizational unit such as:

```text
Branch Manager - Branch 1001
Operations Department
Gold Loan Business Unit
Grade M2
Reports to Regional Manager
```

Each position is unique and has a lifecycle.

---

## Position Architecture

Every position should contain the following architectural domains:

```text
Organization
Financial
People
Workflow
Security
Analytics
AI
```

---

## Position Dashboard

### KPIs

- Total Positions
- Filled
- Vacant
- Frozen
- Abolished
- Critical Positions
- Temporary Positions
- Succession Ready
- Average Vacancy Days
- Position Health

### Charts

- Filled vs vacant
- Organization pyramid
- Vacancy trend
- Retirement forecast
- Hiring forecast
- Position cost

---

## Position Workspace

```text
Dashboard
↓
Position Directory
↓
Position Explorer
↓
Position Profile
↓
Vacancies
↓
Recruitment
↓
Succession
↓
Budget
↓
Reports
```

---

## Position Directory

### Enterprise grid columns

- Position Code
- Position Name
- Department
- Branch
- Grade
- Designation
- Employee
- Status
- Vacancy Health

### Features

- Search
- Filters
- Saved views
- Bulk actions
- Export
- AI search

---

## Position Explorer

Interactive tree structure:

```text
CEO
│
├── COO
│   └── Regional Head
│       └── Branch Manager
│           └── Operations Manager
│               └── Officer
│                   └── Executive
```

Features:

- Drag and drop
- Expand and collapse
- Search
- Move positions

---

## Position Profile

### Tabs

- Overview
- Organization
- Employee
- Vacancy
- Budget
- Competencies
- Approvals
- Recruitment
- Succession
- Training
- Performance
- Documents
- Timeline
- Audit
- AI

---

## Create Position Wizard

### Step 1 — General

Fields:

- Position Code
- Position Name
- Designation
- Grade
- Status

### Step 2 — Organization

Fields:

- Enterprise
- Legal Entity
- Business Unit
- Branch
- Department
- Section
- Team

### Step 3 — Reporting

Fields:

- Reports To
- Direct Reports
- Functional Manager
- Administrative Manager
- Matrix Manager

### Step 4 — Financial

Fields:

- Cost Center
- Profit Center
- Salary Budget
- Allowance Budget
- Recruitment Budget

### Step 5 — Competencies

Fields:

- Technical
- Leadership
- Compliance
- Communication
- Digital
- Behavioral

### Step 6 — Recruitment

Fields:

- Replacement Required
- Recruitment Type
- Hiring SLA
- Interview Panel
- Assessment

### Step 7 — Approval Authority

Fields:

- Loan Approval
- Expense
- Purchase
- HR
- Finance
- Vendor
- Travel

### Step 8 — Performance

Assign:

- KPIs
- Objectives
- Scorecard
- Bonus Rules

### Step 9 — Documents

Upload:

- Job Description
- SOP
- Authority Matrix
- Hiring Guide

### Step 10 — Review and Create

Flow:

```text
Review
↓
Approval
↓
Create
```

---

## Position Types

The system should support:

```text
Permanent
Temporary
Contract
Project
Shared
Virtual
Acting
Seasonal
Intern
```

---

## Vacancy Management

The lifecycle should display:

```text
Filled
↓
Vacant
↓
Approved
↓
Recruitment
↓
Offer
↓
Joining
↓
Filled
```

---

## Position Budget

Each position should own:

```text
Salary
Bonus
Benefits
Training
Equipment
Recruitment
```

---

## Position Authority

Defines:

```text
Loan Approval
Purchase
Expense
Leave Approval
Recruitment Approval
Vendor Approval
```

This authority belongs to the position, not the employee.

---

## Position Security

The model should link with IAM:

```text
Position
↓
Suggested Role
↓
Permissions
↓
Approval Rights
```

---

## Succession Planning

Displays:

```text
Current Holder
Successor 1
Successor 2
Readiness
Training Plan
```

---

## Position Competencies

Example:

```text
Credit Analysis → Expert
AML → Advanced
Leadership → Intermediate
Collections → Advanced
```

---

## Position Performance

Shows:

```text
KPIs
Objectives
Performance
Promotion
Bonus
```

---

## Position Health Score

Calculated using:

- Vacancy
- Attrition
- Competency gaps
- Budget
- Succession
- Performance
- Recruitment delay
- Training completion

Example:

```text
Position Health: 97%
Rating: ★★★★★
```

---

## Position 360

The most important screen is a complete Position 360 view.

### Executive

- Position
- Budget
- Health
- Status

### Employee

- Current holder
- History
- Transfers
- Attendance
- Leave

### Financial

- Salary budget
- Benefits
- Cost

### Organization

- Reports to
- Subordinates
- Matrix
- Department
- Branch

### Recruitment

- Vacancy
- Candidates
- Interview
- Offer

### Succession

- Ready now
- Ready in 1 year
- Ready in 3 years

### AI

Examples:

- Recommend successor
- Predict resignation
- Suggest salary correction
- Recommend promotion
- Find duplicate positions
- Optimize hierarchy
- Predict retirement

---

## Organization Chart

Interactive organization structure:

```text
CEO
↓
COO
↓
Regional Head
↓
Branch Manager
↓
Operations Manager
↓
Officer
↓
Executive
```

Supports drag and drop.

---

## Workforce Planning

Displays:

```text
Required Positions
Filled
Vacant
Forecast
Hiring
Retirement
Transfer
```

---

## Position Workflow

```text
Create
↓
HR
↓
Finance
↓
Operations
↓
Executive
↓
Active
```

---

## Reports

Standard reports:

- Position Register
- Vacancy Report
- Organization Chart
- Succession Report
- Workforce Plan
- Salary Budget
- Position Cost
- Retirement Forecast
- Hiring Forecast
- Position Health

---

## Database Tables

```text
position
position_hierarchy
position_budget
position_competency
position_authority
position_document
position_employee
position_history
position_recruitment
position_successor
position_performance
position_health
position_ai
position_audit
```

---

## APIs

```text
GET    /api/v1/positions
POST   /api/v1/positions
GET    /api/v1/positions/{id}
PUT    /api/v1/positions/{id}
PATCH  /api/v1/positions/{id}/status
GET    /api/v1/positions/{id}/organization
GET    /api/v1/positions/{id}/budget
GET    /api/v1/positions/{id}/health
GET    /api/v1/positions/{id}/successors
```

---

## Events

```text
POSITION_CREATED
POSITION_UPDATED
POSITION_FILLED
POSITION_VACATED
POSITION_TRANSFERRED
POSITION_ABOLISHED
POSITION_BUDGET_UPDATED
POSITION_SUCCESSOR_ASSIGNED
POSITION_HEALTH_CHANGED
```

---

## Backend Structure

```text
services/eom/position/
├── domain/
├── application/
├── infrastructure/
├── api/
├── analytics/
├── ai/
├── workflow/
└── tests/
```

---

## Frontend Structure

```text
modules/eom/position/
├── dashboard/
├── directory/
├── explorer/
├── profile/
├── recruitment/
├── succession/
├── budget/
├── analytics/
├── reports/
├── settings/
└── components/
```

---

## Integration Matrix

| Module | Integration |
| --- | --- |
| HRMS | Employee assignment and transfers |
| Recruitment | Vacancy and hiring |
| Payroll | Position budget and salary |
| Performance | KPIs and objectives |
| Learning | Competency development |
| IAM | Role and access provisioning |
| Workflow | Approval authority |
| Budgeting | Workforce cost planning |
| Analytics | Headcount and capacity planning |

---

## Position 360 (Digital Position Twin)

Each position should expose a complete operational model.

### Organization View

- Reporting hierarchy
- Department
- Branch
- Business unit

### Financial View

- Salary budget
- Benefits
- Recruitment cost
- Total cost of ownership

### People View

- Current holder
- Previous holders
- Successors
- Competencies

### Operations View

- KPIs
- Approval limits
- Decision rights
- Workload

### Risk View

- Vacancy risk
- Single-point dependency
- Compliance requirements
- Segregation-of-duties conflicts

### AI View

- Successor recommendations
- Internal mobility candidates
- Retirement prediction
- Attrition probability
- Organization optimization suggestions

---

## Definition of Done

Position Management is complete when it provides:

- Position hierarchy
- Vacancy lifecycle
- Recruitment integration
- Budget ownership
- Competency framework
- Approval authority
- Succession planning
- Position 360
- AI insights
- Audit trail
- Enterprise reporting

---

## Workforce Architecture (Now Complete)

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
Grade
↓
Job Family
↓
Role
↓
Designation
↓
Position
↓
Employee
```

This hierarchy becomes the backbone for HRMS, Payroll, Recruitment, Performance, Learning, Workflow, IAM, and Budgeting.

---

## What Comes Next

At this point, the organization and workforce foundation is largely complete. The next strategic module should be EOM-013 — Cost Center and Financial Organization Management, expanding beyond a simple cost center master to include:

- Cost center hierarchy
- Profit center hierarchy
- Responsibility centers
- Budget centers
- Revenue centers
- Internal orders
- Financial ownership
- GL mappings
- Budget allocation
- Inter-company allocations
- Approval ownership
- Financial organization 360
- AI-based cost optimization

This establishes the financial organizational backbone before implementing the full Accounting and General Ledger module.
