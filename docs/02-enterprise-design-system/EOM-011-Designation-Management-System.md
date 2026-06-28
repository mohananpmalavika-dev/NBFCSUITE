# EOM-011 — Designation Management System (DgMS)

## Overview

Designation Management is the second pillar of the Enterprise Workforce Architecture. If grades define level, designations define role. This module becomes the single source of truth for job titles, job families, responsibilities, approvals, competencies, recruitment, and career progression across ARTH.OS.

A designation is not just a job title. It defines:

- Job role
- Job family
- Grade mapping
- Competencies
- Responsibilities
- KPIs
- Approval authority
- Recruitment profile
- Training
- Career path

---

## Vision

Designations should become the authoritative role model for the enterprise.

Example workforce hierarchy:

```text
Enterprise
↓
Business Unit
↓
Department
↓
Grade
↓
Job Family
↓
Designation
↓
Position
↓
Employee
```

---

## Standard Job Families

ARTH.OS should ship with configurable templates such as:

```text
Executive Leadership
Business Operations
Finance
Accounting
Risk
Compliance
Audit
Technology
Infrastructure
Security
HR
Customer Service
Collections
Recovery
Legal
Treasury
Forex
Sales
Marketing
Administration
```

---

## Sample Designation Hierarchy

```text
Chief Executive Officer
↓
Chief Operating Officer
↓
Executive Vice President
↓
Vice President
↓
Assistant Vice President
↓
Senior Manager
↓
Manager
↓
Assistant Manager
↓
Senior Officer
↓
Officer
↓
Executive
↓
Associate
↓
Assistant
↓
Trainee
```

---

## Designation Dashboard

### KPIs

- Designations
- Employees
- Open Positions
- Vacancies
- Job Families
- Average Salary
- Training Compliance
- Succession Readiness

### Charts

- Employees by designation
- Designation pyramid
- Hiring trend
- Vacancy trend
- Promotion trend

---

## Workspace

```text
Dashboard
↓
Designation Directory
↓
Designation Profile
↓
Job Families
↓
Career Paths
↓
Reports
```

---

## Designation Directory

### Enterprise grid columns

- Designation Code
- Designation
- Job Family
- Grade
- Department
- Employees
- Vacancies
- Status

### Features

- Search
- Filters
- Saved views
- Bulk update
- Export

---

## Designation Profile

### Tabs

- Overview
- Responsibilities
- Competencies
- Grade Mapping
- Career Path
- KPIs
- Approvals
- Recruitment
- Training
- Documents
- Timeline
- Audit
- AI

---

## Create Designation Wizard

### Step 1 — General

Fields:

- Designation Code
- Designation Name
- Short Name
- Job Family
- Department
- Grade
- Status

### Step 2 — Organization

Fields:

- Business Unit
- Department
- Section
- Reports To
- Can Manage
- Replacement Designation

### Step 3 — Responsibilities

Fields:

- Job Description
- Primary Responsibilities
- Secondary Responsibilities
- Authority
- Decision Rights

### Step 4 — Competencies

The designation should define:

- Technical
- Leadership
- Compliance
- Communication
- Product Knowledge
- Digital Skills
- Risk Awareness

### Step 5 — Recruitment

Fields:

- Education
- Experience
- Certification
- Languages
- Skills
- Background Verification
- Medical Check

### Step 6 — Performance

Assign KPIs such as:

- Business KPI
- Operational KPI
- Customer KPI
- Financial KPI
- Learning KPI

### Step 7 — Approval Authority

Fields:

- Loan Limit
- Expense Limit
- Purchase Limit
- HR Approval
- Vendor Approval
- Travel Approval

### Step 8 — Career Path

Example:

```text
Officer → Senior Officer → Assistant Manager → Manager → Senior Manager → Vice President
```

### Step 9 — Training

Mandatory trainings:

- AML
- KYC
- Fraud
- Cyber Security
- Leadership
- Product Certification

### Step 10 — Review and Publish

Flow:

```text
Review
↓
Approval
↓
Publish
```

---

## Responsibility Matrix

Every designation should own:

- Decision rights
- Financial authority
- Operational authority
- Regulatory responsibility
- Customer responsibility

---

## Competency Matrix

Example:

| Competency | Required Level |
| --- | --- |
| Credit Analysis | Expert |
| AML | Advanced |
| Leadership | Intermediate |
| Gold Appraisal | Expert |
| Customer Relationship | Advanced |

---

## Recruitment Template

Each designation should include:

```text
Education
Experience
Certification
Mandatory Skills
Preferred Skills
Interview Panel
Assessment
Offer Workflow
```

---

## Performance Framework

Every designation should have:

```text
Objectives
↓
KPIs
↓
Scorecard
↓
Performance Rating
↓
Promotion Eligibility
```

---

## Succession Planning

Shows:

```text
Current Holder
Ready Now
Ready in 1 Year
Ready in 3 Years
Critical Vacancy Risk
```

---

## AI Features

Example capabilities:

```text
Suggest missing competencies.
↓
Recommend promotion candidates.
↓
Identify role duplication.
↓
Benchmark salary.
↓
Predict hiring demand.
↓
Recommend organizational restructuring.
```

---

## Reports

Standard reports:

- Designation Register
- Job Family Report
- Recruitment Report
- Competency Matrix
- KPI Matrix
- Succession Report
- Vacancy Report
- Promotion Pipeline
- Approval Authority Matrix

---

## Workflow

### Designation creation

```text
Draft
↓
HR Review
↓
Business Review
↓
Finance Review
↓
Executive Approval
↓
Active
```

---

## Designation Health Score

Calculated from:

- Vacancy rate
- Competency gaps
- Recruitment time
- Performance
- Succession readiness
- Training compliance

Example:

```text
Designation Health: 94%
Rating: ★★★★★
```

---

## Database Design

### Core table

### designation

| Field | Type |
| --- | --- |
| id | UUID |
| code | VARCHAR(30) |
| name | VARCHAR(200) |
| short_name | VARCHAR(100) |
| grade_id | UUID |
| job_family_id | UUID |
| department_id | UUID |
| reports_to_designation_id | UUID |
| status | ENUM |
| created_at | TIMESTAMP |

### Supporting tables

- job_family
- designation_competency
- designation_responsibility
- designation_training
- designation_recruitment
- designation_kpi
- designation_approval
- designation_career
- designation_document
- designation_audit
- designation_health

---

## APIs

```text
GET    /api/v1/designations
POST   /api/v1/designations
GET    /api/v1/designations/{id}
PUT    /api/v1/designations/{id}
PATCH  /api/v1/designations/{id}/status
GET    /api/v1/designations/{id}/competencies
GET    /api/v1/designations/{id}/career
GET    /api/v1/designations/{id}/health
```

---

## Events

```text
DESIGNATION_CREATED
DESIGNATION_UPDATED
GRADE_CHANGED
JOB_FAMILY_CHANGED
COMPETENCY_UPDATED
KPI_UPDATED
CAREER_PATH_UPDATED
HEALTH_CHANGED
```

---

## Backend Structure

```text
services/eom/designation/
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
modules/eom/designation/
├── dashboard/
├── directory/
├── profile/
├── competencies/
├── recruitment/
├── career/
├── reports/
├── settings/
└── components/
```

---

## Integration Matrix

| Module | Integration |
| --- | --- |
| HRMS | Employee designation |
| Recruitment | Job requisitions and hiring |
| Payroll | Grade-based compensation |
| Performance | KPI and appraisal templates |
| Learning | Mandatory learning paths |
| Workflow | Approval authority |
| IAM | Role suggestions and access profiles |
| Budgeting | Workforce planning |
| Analytics | Headcount and career analytics |

---

## Designation 360

Every designation should have a Designation 360 page.

### Executive View

- Headcount
- Vacancy
- Health score
- Cost to company

### People View

- Employees
- Skills
- Certifications
- Succession pipeline

### Operations View

- Responsibilities
- KPIs
- Workflow authority
- Decision rights

### Recruitment View

- Hiring pipeline
- Time-to-fill
- Candidate quality
- Offer acceptance

### AI View

- Market salary benchmarking
- Emerging skill recommendations
- Promotion candidates
- Workforce demand forecast
- Role redundancy analysis

---

## Definition of Done

Designation Management is complete when it supports:

- Job families
- Grade mapping
- Competency framework
- Recruitment templates
- Performance templates
- Career paths
- Approval authority
- Succession planning
- AI insights
- Audit trail
- Enterprise reporting

---

## Strategic Recommendation

Do not stop at designation. Introduce a Role Catalog above it.

The hierarchy becomes:

```text
Job Family → Role → Designation → Position → Employee
```

Example:

```text
Job Family: Lending
Role: Credit Analyst
Designation: Senior Credit Analyst
Position: Senior Credit Analyst - Branch 102
Employee: Rahul Nair
```

This separation provides major advantages:

- Multiple designations can share the same role
- Skills and KPIs are maintained once at the role level
- Recruitment, training, and performance become standardized
- Workforce planning becomes more accurate
- HRMS, IAM, Workflow, and Learning all consume the same role catalog

This architecture scales far better for a large enterprise than tying everything directly to designations.

---

## Next Module

The next module is EOM-012 — Position Management System.

This is arguably the most critical workforce module because:

- Employees occupy positions, not designations
- Positions belong to branches, departments, and teams
- Positions drive vacancies, recruitment, transfers, succession planning, payroll budgeting, and reporting relationships

A Position Management system built this way becomes the backbone for HRMS, Recruitment, Payroll, Workflow, Budgeting, and Organization Planning across ARTH.OS.
