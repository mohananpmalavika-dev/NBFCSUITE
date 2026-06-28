# EOM-009 — Section & Team Management System (STMS)

## Overview

Section and Team Management models how work is actually executed inside the enterprise. A department manages business capabilities, a section organizes functional work, and a team executes operational work.

This module is much more than a list of teams. It defines the practical structure of execution across operations, support, compliance, projects, and shared services.

---

## Vision

Example:

```text
Gold Loan Department
├── Gold Appraisal Section
│   ├── Team A
│   └── Team B
├── Documentation Section
│   ├── Verification Team
│   └── Scanning Team
└── Operations Section
    ├── Processing Team
    └── Disbursement Team
```

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

## Business Objectives

The module should support:

- Functional sections
- Operational teams
- Matrix teams
- Project teams
- Virtual teams
- Cross-branch teams
- Shared-service teams

---

## Section Types

```text
Operations
Sales
Support
Compliance
Audit
Technology
Finance
Administration
Quality
Training
```

---

## Team Types

```text
Permanent Team
Project Team
Task Force
Virtual Team
Cross Functional Team
Shift Team
Regional Team
Support Team
```

---

## Dashboard

### KPIs

- Sections
- Teams
- Employees
- Open Positions
- Projects
- Capacity
- Workload
- Performance
- Health Score

### Charts

- Team distribution
- Capacity utilization
- Workload trend
- Productivity
- Project allocation

---

## Workspace

```text
Dashboard
↓
Section Directory
↓
Team Directory
↓
Organization
↓
Projects
↓
Capacity
↓
Reports
```

---

## Section Directory

### Columns

- Code
- Section
- Department
- Section Head
- Employees
- Teams
- Projects
- Status

### Features

- Search
- Filters
- Saved views
- Export
- Bulk update

---

## Team Directory

### Columns

- Team Code
- Team Name
- Section
- Team Lead
- Employees
- Projects
- Capacity
- Status

---

## Section Profile

### Tabs

- Overview
- Organization
- Teams
- Employees
- Projects
- Assets
- Documents
- KPIs
- Timeline
- Audit
- AI

---

## Team Profile

### Tabs

- Overview
- Members
- Skills
- Projects
- Workload
- Capacity
- Performance
- Assets
- Calendar
- Documents
- Timeline
- Audit
- AI

---

## Create Section Wizard

### Step 1 — General

Fields:

- Section Code
- Section Name
- Department
- Type
- Status

### Step 2 — Organization

Fields:

- Section Head
- Deputy Head
- Business Unit
- Branch
- Reporting Department

### Step 3 — Operations

Fields:

- Working Calendar
- Shift
- Capacity
- Business Hours
- SLA Profile

### Step 4 — Services

Fields:

- Service Catalog
- Business Capabilities
- Workflows

### Step 5 — Review and Submit

Flow:

```text
Review
↓
Submit
```

---

## Create Team Wizard

### Step 1 — General

Fields:

- Team Code
- Team Name
- Team Type
- Section
- Status

### Step 2 — Leadership

Fields:

- Team Lead
- Deputy Lead
- Reporting Manager

### Step 3 — Operations

Fields:

- Shift
- Capacity
- Working Days
- Business Calendar
- Location

### Step 4 — Skills

Fields:

- Primary Skills
- Secondary Skills
- Certifications
- Required Competencies

### Step 5 — Projects

Assign:

- Projects
- Products
- Processes
- Customers

### Step 6 — Review and Create

Flow:

```text
Review
↓
Approval
↓
Create
```

---

## Team Capacity

Shows:

```text
Total Positions
Filled
Vacant
Available Capacity
Utilization %
Overtime
Idle %
```

---

## Skill Matrix

Each team maintains:

```text
Employee → Skills → Certification → Level → Expiry
```

Example:

```text
Gold Appraisal → Expert
KYC → Intermediate
AML → Beginner
Customer Service → Expert
```

---

## Workforce Planning

Displays:

```text
Required Employees
Current Employees
Vacancies
Forecast
Hiring Plan
```

---

## Workload Dashboard

Metrics:

```text
Assigned Tasks
Completed
Pending
Overdue
Average SLA
Productivity
```

---

## Team Calendar

Supports:

- Working days
- Shift schedule
- Leave calendar
- Training calendar
- Project calendar
- On-call schedule

---

## Project Assignment

A team can work on:

```text
Project → Task → Milestone → Sprint
```

Supports both Agile and waterfall delivery models.

---

## Matrix Organization

Employees can belong to multiple organizational contexts:

```text
Department → Operations Team → Project Team
```

Example:

```text
HR Department → Payroll Team → ERP Migration Team
```

---

## Team KPIs

Examples:

- SLA
- Productivity
- Customer Satisfaction
- Quality
- Turnaround Time
- Error Rate
- Revenue
- Collections

---

## Team Health Score

Calculated using:

- Capacity utilization
- Productivity
- SLA compliance
- Employee satisfaction
- Attrition
- Training completion
- Project delivery
- Audit findings

Example:

```text
Health: 95%
Rating: ★★★★★
```

---

## Workflow

### Team creation

```text
Draft
↓
Department Approval
↓
HR Approval
↓
Operations Approval
↓
Active
```

---

## AI Features

Example capabilities:

```text
Find overloaded teams.
↓
Recommend staffing.
↓
Predict burnout.
↓
Optimize team allocation.
↓
Suggest skill training.
↓
Recommend cross-functional collaboration.
↓
Forecast hiring requirements.
```

---

## Reports

Standard reports:

- Section Register
- Team Register
- Capacity Report
- Skill Matrix
- Workforce Plan
- Team Performance
- Productivity Report
- Team Health
- Project Allocation
- Training Matrix

---

## Database Tables

```text
section
section_head
section_document
section_workflow
section_audit
team
team_member
team_skill
team_capacity
team_project
team_calendar
team_asset
team_kpi
team_health
team_ai
```

---

## APIs

```text
GET    /api/v1/sections
POST   /api/v1/sections
GET    /api/v1/sections/{id}
PUT    /api/v1/sections/{id}
GET    /api/v1/teams
POST   /api/v1/teams
GET    /api/v1/teams/{id}
PUT    /api/v1/teams/{id}
GET    /api/v1/teams/{id}/capacity
GET    /api/v1/teams/{id}/workload
GET    /api/v1/teams/{id}/health
```

---

## Events

```text
SECTION_CREATED
SECTION_UPDATED
TEAM_CREATED
TEAM_UPDATED
TEAM_LEAD_ASSIGNED
MEMBER_ADDED
MEMBER_REMOVED
CAPACITY_UPDATED
SKILL_UPDATED
TEAM_HEALTH_CHANGED
```

---

## Backend Structure

```text
services/eom/section/
├── domain/
├── application/
├── infrastructure/
├── api/
└── tests/

services/eom/team/
├── domain/
├── application/
├── infrastructure/
├── api/
└── tests/
```

---

## Frontend Structure

```text
modules/eom/section/
├── dashboard/
├── directory/
├── profile/
├── reports/
└── components/

modules/eom/team/
├── dashboard/
├── directory/
├── profile/
├── capacity/
├── workload/
├── reports/
└── components/
```

---

## Integration Matrix

| Module | Usage |
| --- | --- |
| HRMS | Employee assignment and workforce planning |
| Workflow | Team approvals and task routing |
| Projects | Project and sprint assignment |
| CRM | Customer ownership teams |
| Collections | Collection squads |
| Lending | Loan processing teams |
| Gold Loan | Gold appraisal teams |
| Deposits | Deposit operations teams |
| ITSM | Support teams |
| Analytics | Productivity dashboards |

---

## Team 360

Each team should have a dedicated Team 360 page.

### Executive View

- Capacity
- Health
- Productivity
- KPIs

### People View

- Members
- Skills
- Vacancies
- Attendance

### Operations View

- Tasks
- Workload
- SLA
- Backlog

### Financial View

- Budget
- Cost
- Overtime
- Utilization

### Project View

- Active projects
- Milestones
- Risks

### AI View

- Staffing recommendations
- Skill gaps
- Burnout prediction
- Performance insights

---

## Definition of Done

Section and Team Management is complete when it supports:

- Configurable sections and teams
- Matrix and project-based organizations
- Capacity planning
- Skill matrices
- Workforce forecasting
- Workload management
- Team 360
- AI recommendations
- Workflow integration
- Audit trail

---

## EOM Roadmap Progress

| Module | Status |
| --- | --- |
| EOM-001 Enterprise | Complete |
| EOM-002 Brand | Complete |
| EOM-003 Legal Entity | Complete |
| EOM-004 Business Unit | Complete |
| EOM-005 Geography | Complete |
| EOM-007 Branch | Complete |
| EOM-008 Department | Complete |
| EOM-009 Section & Team | Complete |
| EOM-010 Grade Management | Next |
| EOM-011 Designation Management | Pending |
| EOM-012 Position Management | Pending |
| EOM-013 Cost Center | Pending |
| EOM-014 Profit Center | Pending |
| EOM-015 Organization Explorer | Pending |

---

## Strategic Recommendation

Before implementing HRMS employee onboarding, finish Grades, Designations, and Position Management. These three modules define the workforce structure that every employee record, payroll calculation, approval workflow, and reporting relationship depends on.

They should be treated as Position Architecture rather than just HR master data. Each position should carry organizational, financial, operational, and competency metadata so that HRMS, budgeting, workflow, and succession planning all reference the same authoritative model.
