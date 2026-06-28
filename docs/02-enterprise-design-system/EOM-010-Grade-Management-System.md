# EOM-010 — Grade Management System (GMS)

## Overview

Grade Management is far more important than most ERP systems make it. In SAP, Oracle, Workday, and SuccessFactors, grades determine salary bands, approvals, benefits, entitlements, training, and career progression. For ARTH.OS, grades should be treated as an Enterprise Workforce Architecture module.

A grade is not merely a payroll level. It defines:

- Career level
- Salary band
- Approval authority
- Benefits
- Leave rules
- Training requirements
- Competencies
- Promotion rules
- Position eligibility
- Risk level

---

## Vision

A grade becomes the authoritative layer for workforce structure and operating authority.

Example grade structure:

```text
Executive Grades
├── G1
├── G2
├── G3

Officer Grades
├── O1
├── O2
├── O3

Manager Grades
├── M1
├── M2
├── M3

Leadership
├── L1
├── L2
├── L3

Executive Leadership
└── CXO
```

This structure should be fully configurable.

---

## Enterprise Hierarchy

```text
Enterprise
↓
Business Unit
↓
Department
↓
Grade
↓
Designation
↓
Position
↓
Employee
```

---

## Business Objectives

The module should support:

- Configurable grade hierarchy
- Salary structures
- Benefits and leave entitlements
- Competency framework
- Career paths
- Succession planning
- Approval authority matrix
- Training requirements
- AI insights
- Audit trail
- Enterprise reporting

---

## Grade Dashboard

### KPIs

- Grades
- Salary Bands
- Employees
- Vacancies
- Promotions
- Training
- Certification
- Performance
- Succession Readiness

### Charts

- Employee distribution
- Grade pyramid
- Salary distribution
- Promotion trend
- Succession coverage

---

## Workspace

```text
Dashboard
↓
Grade Directory
↓
Grade Profile
↓
Salary Structure
↓
Competencies
↓
Career Path
↓
Reports
```

---

## Grade Directory

### Columns

- Grade Code
- Grade Name
- Level
- Employees
- Salary Band
- Promotion Level
- Status

### Features

- Search
- Filters
- Saved views
- Bulk update
- Export

---

## Grade Profile

### Tabs

- Overview
- Salary
- Benefits
- Competencies
- Career Path
- Training
- Approvals
- Documents
- Timeline
- Audit
- AI

---

## Create Grade Wizard

### Step 1 — General

Fields:

- Grade Code
- Grade Name
- Level
- Category
- Status
- Description

### Step 2 — Salary Band

Fields:

- Minimum Salary
- Mid Salary
- Maximum Salary
- Currency
- Increment Policy
- Bonus Eligibility

### Step 3 — Benefits

Fields:

- Medical
- Insurance
- Travel
- Accommodation
- Mobile
- Vehicle Allowance
- Stock Option
- Gratuity

### Step 4 — Leave

Fields:

- Annual Leave
- Sick Leave
- Casual Leave
- Maternity
- Paternity
- Special Leave

### Step 5 — Competencies

Fields:

- Leadership
- Technical
- Compliance
- Communication
- Digital Skills
- Risk Awareness

Levels:

- Beginner
- Intermediate
- Advanced
- Expert

### Step 6 — Training

Mandatory training examples:

- AML
- KYC
- Cyber Security
- POS
- HR
- RBI Compliance
- Product Training

### Step 7 — Approval Authority

Fields:

- Loan Limit
- Expense Limit
- Purchase Limit
- HR Approval
- Finance Approval

Example:

```text
M3 can approve loans up to ₹25 Lakhs
```

### Step 8 — Career Path

Example:

```text
O1 → O2 → O3 → M1 → M2 → M3
```

### Step 9 — Documents

Upload:

- Policy
- Salary Matrix
- Promotion Rules
- Competency Framework

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

## Salary Band

Displays:

```text
Minimum
Target
Maximum
Current Employees
Average Salary
Median Salary
```

---

## Benefits Matrix

Every grade owns:

```text
Insurance
Medical
Leave
Travel
Vehicle
Bonus
Mobile
Laptop
WFH
Relocation
```

---

## Approval Matrix

Example:

| Grade | Loan | Purchase | HR | Expense |
| --- | --- | --- | --- | --- |
| O1 | ₹50K | ₹25K | No | ₹10K |
| M1 | ₹5L | ₹2L | Yes | ₹50K |
| M3 | ₹25L | ₹10L | Yes | ₹2L |
| L1 | ₹1Cr | ₹50L | Yes | ₹10L |

---

## Competency Matrix

Example:

| Competency | Required Level |
| --- | --- |
| Leadership | Advanced |
| Credit Analysis | Expert |
| RBI Compliance | Advanced |
| AML | Advanced |
| Customer Service | Expert |

---

## Career Framework

Each grade defines:

```text
Entry
↓
Promotion
↓
Succession
↓
Retirement
```

Supports multiple career tracks.

---

## Succession Planning

Shows:

```text
Current Grade
Potential Successor
Readiness
Training Required
```

---

## Grade Health Score

Calculated from:

- Vacancies
- Training completion
- Competency gaps
- Promotion backlog
- Salary deviations
- Succession readiness

Example:

```text
Grade Health: 93%
Rating: ★★★★★
```

---

## Workflow

### Grade creation

```text
Draft
↓
HR Review
↓
Finance Review
↓
Executive Approval
↓
Active
```

---

## AI Features

Example capabilities:

```text
Recommend salary band.
↓
Find salary anomalies.
↓
Suggest promotion candidates.
↓
Identify competency gaps.
↓
Forecast hiring needs.
↓
Recommend training.
↓
Predict attrition risk.
```

---

## Reports

Standard reports:

- Grade Register
- Salary Band Report
- Competency Matrix
- Promotion Report
- Succession Report
- Training Compliance
- Benefits Matrix
- Approval Authority Matrix
- Grade Health Report

---

## Database Tables

```text
grade
grade_salary
grade_benefit
grade_leave
grade_competency
grade_training
grade_approval
grade_career
grade_document
grade_health
grade_ai
grade_audit
```

---

## APIs

```text
GET    /api/v1/grades
POST   /api/v1/grades
GET    /api/v1/grades/{id}
PUT    /api/v1/grades/{id}
PATCH  /api/v1/grades/{id}/status
GET    /api/v1/grades/{id}/salary
GET    /api/v1/grades/{id}/career
GET    /api/v1/grades/{id}/health
```

---

## Events

```text
GRADE_CREATED
GRADE_UPDATED
GRADE_ACTIVATED
SALARY_BAND_UPDATED
BENEFITS_UPDATED
CAREER_PATH_UPDATED
SUCCESSION_UPDATED
GRADE_HEALTH_CHANGED
```

---

## Backend Structure

```text
services/eom/grade/
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
modules/eom/grade/
├── dashboard/
├── directory/
├── profile/
├── salary/
├── competencies/
├── career/
├── reports/
├── settings/
└── components/
```

---

## Integration Matrix

| Module | Integration |
| --- | --- |
| HRMS | Employee grade assignment |
| Payroll | Salary bands and increments |
| Performance | Promotion eligibility |
| Learning | Mandatory training |
| Workflow | Approval authority |
| Lending | Loan approval limits |
| Procurement | Purchase approval limits |
| Risk | Segregation of duties |
| Budget | Workforce planning |
| Analytics | Grade distribution and forecasting |

---

## Grade 360

Every grade should have a complete Grade 360 view.

### Executive View

- Headcount
- Salary distribution
- Vacancies
- Health score

### Financial View

- Salary band
- Budget impact
- Benefits cost
- Increment analysis

### Talent View

- Competencies
- Certifications
- Succession pipeline
- Promotion readiness

### Operations View

- Approval limits
- Delegation rules
- Workflow authority

### AI View

- Market salary benchmarking
- Internal pay equity analysis
- Attrition prediction
- Promotion recommendations
- Skill gap analysis

---

## Definition of Done

Grade Management is complete when it supports:

- Configurable grade hierarchy
- Salary band management
- Benefits and leave entitlements
- Competency framework
- Career paths
- Succession planning
- Approval authority matrix
- Training requirements
- AI insights
- Audit trail
- Enterprise reporting

---

## Strategic Recommendation

Grades should not be treated as HR-only data. They should become the Enterprise Authority Layer.

Every grade should centrally control:

- Salary eligibility
- Approval authority
- Financial delegation
- Procurement authority
- Credit approval limits
- Access level recommendations
- Training obligations
- Compliance certifications
- Succession readiness

This eliminates duplicated configuration across HRMS, Lending, Procurement, Accounting, and Workflow.

---

## Next Module

The next module is EOM-011 — Designation Management System.

This will define:

- Enterprise designation hierarchy
- Job families
- Job roles
- Role catalog
- Functional versus administrative designations
- Competency mapping
- Grade mapping
- Position mapping
- Salary recommendations
- Recruitment templates
- Performance expectations
- Career ladders
- AI-driven role recommendations

Together with grades and positions, this forms the complete enterprise workforce architecture used by HR, payroll, workflow, and authorization modules.
