# EOM-004 — Business Unit Management (BUM)

## Overview

Business Unit Management is the bridge between enterprise structure and business operations. It defines the operating lines of the enterprise, each with its own leadership, products, budgets, branches, employees, KPIs, and financial accountability.

This is one of the core architectural layers of ARTH.OS because modern banking and NBFC enterprises are not organized only by geography or legal entity, but also by business line and profit responsibility.

---

## Purpose

A Business Unit represents an operational line of business with its own objectives, budgets, products, and KPIs.

Example enterprise structure:

```text
ARTH Enterprise
├── Retail Finance
├── Gold Loan
├── Deposits
├── Treasury
├── Forex
├── Collections
├── Insurance
├── Wealth Management
├── Microfinance
├── Shared Services
└── Digital Banking
```

Each business unit can have:

- Its own head
- Its own budget
- Its own products
- Its own branches
- Its own employees
- Its own KPIs
- Its own profit and loss accountability
- Its own workflows

---

## Business Objectives

Business Unit Management should support:

- Multi-business-unit enterprise structures
- Cross-functional ownership
- Product ownership
- Budget ownership
- Profit responsibility
- KPI responsibility
- Resource allocation
- Business analytics

---

## Hierarchy

```text
Enterprise → Legal Entity → Brand → Business Group (Optional) → Business Unit → Division (Optional) → Department → Team
```

---

## Standard Business Unit Templates

For an NBFC, ARTH.OS should ship with configurable templates such as:

```text
Retail Lending
Gold Loan
Vehicle Loan
Mortgage
MSME
Personal Loan
Deposits
Treasury
Forex
Collections
Recovery
Customer Service
Operations
Finance
HR
Risk
Compliance
Legal
IT
Marketing
Internal Audit
Procurement
```

Templates should be configurable by enterprise and legal entity.

---

## Business Unit Dashboard

### KPIs

- Business Units
- Employees
- Branches
- Revenue
- Profit
- Customers
- Products
- Budget Utilization
- Target Achievement

### Charts

- Revenue trend
- Business mix
- Branch distribution
- Employee distribution
- Profit trend
- Budget vs actual

---

## Workspace

```text
Dashboard
↓
Business Unit Directory
↓
Business Unit Profile
↓
Products
↓
Branches
↓
Departments
↓
Budgets
↓
Reports
```

---

## Business Unit Directory

### Columns

- BU Code
- Business Unit
- BU Head
- Legal Entity
- Products
- Branches
- Employees
- Status
- Performance Score

### Features

- Search
- Filters
- Saved views
- Bulk actions
- Export

---

## Business Unit Profile

### Tabs

- Overview
- Organization
- Products
- Branches
- Departments
- Employees
- Budgets
- KPIs
- Financials
- Workflows
- Documents
- Timeline
- Audit
- AI Insights

---

## Create Business Unit Wizard

### Step 1 — General

Fields:

- BU Code
- Business Unit Name
- Display Name
- Type
- Category
- Status
- Description

### Step 2 — Ownership

Fields:

- Enterprise
- Brand
- Legal Entity
- Business Group
- Business Head
- Deputy Head
- Functional Head

### Step 3 — Products

Select supported products.

Example:

```text
✓ Gold Loan
✓ Personal Loan
✗ Forex
✗ Treasury
```

### Step 4 — Financial Setup

Fields:

- Budget Owner
- Cost Center
- Profit Center
- Currency
- Budget Cycle
- Revenue Target
- Expense Target

### Step 5 — Operations

Fields:

- Operating Countries
- Regions
- Areas
- Branches
- Working Hours
- Business Calendar

### Step 6 — KPIs

Assign KPIs such as:

- Disbursement
- Collections
- NPA
- Customer Satisfaction
- Branch Productivity
- Profit Margin

### Step 7 — Workflow

Assign default workflows such as:

- Loan Approval Workflow
- Expense Workflow
- Recruitment Workflow
- Purchase Workflow

### Step 8 — Documents

Upload documents such as:

- Operating Manual
- Policy
- SOP
- Budget
- Organization Chart

### Step 9 — Review and Activation

Flow:

```text
Review
↓
Validation
↓
Approval
↓
Activate
```

---

## Business Unit Organization

Each business unit contains:

```text
Business Head
↓
Departments
↓
Sections
↓
Teams
↓
Employees
```

---

## Product Mapping

Every product belongs to one or more business units.

Example:

| Product | Business Unit |
| --- | --- |
| Gold Loan | Gold Loan |
| Personal Loan | Retail Lending |
| Fixed Deposit | Deposits |
| Treasury Bills | Treasury |
| Forex Remittance | Forex |

---

## Branch Mapping

Example:

```text
Gold Loan BU
↓
Branch 101
↓
Branch 102
↓
Branch 250
```

A branch may support multiple business units, with one designated as the primary owner.

---

## Budget Management

Every business unit should have:

```text
Annual Budget
↓
Quarterly Budget
↓
Monthly Budget
↓
Actual
↓
Variance
```

---

## Performance Dashboard

Shows:

- Revenue
- Expenses
- Profit
- Customer Growth
- Employee Productivity
- Product Performance
- SLA Compliance
- NPA Ratio (where applicable)

---

## Workflow Integration

Example workflow:

```text
Create BU
↓
Operations Review
↓
Finance Review
↓
Enterprise Approval
↓
Active
```

---

## Business Calendar

Configure:

- Working days
- Holidays
- Financial calendar
- Operational calendar
- Product launch calendar

---

## AI Features

Example AI capabilities:

```text
Show underperforming business units.
↓
Recommend staffing.
↓
Budget variance analysis.
↓
Product mix optimization.
↓
Predict next quarter revenue.
↓
Suggest branch expansion.
```

---

## Reports

Standard reports should include:

- Business Unit Register
- Budget vs Actual
- Profitability Report
- KPI Achievement
- Branch Allocation
- Product Allocation
- Employee Distribution
- Workflow Performance
- Business Health Report

---

## Permission Matrix

| Role | Access |
| --- | --- |
| Enterprise Admin | All |
| Business Head | Assigned BU |
| CFO | Financial Tabs |
| HR Head | Organization Tabs |
| Auditor | Read Only |
| Branch Manager | Assigned Branch Data |

---

## Business Unit Health Score

The health score should be calculated from:

- Budget utilization
- KPI achievement
- Employee vacancies
- Workflow SLA
- Audit findings
- Customer satisfaction
- Financial performance

Example:

```text
Business Unit Health: 88%
Rating: ★★★★☆
```

---

## Database Design

### Core Table

### business_unit

| Field | Type |
| --- | --- |
| id | UUID |
| enterprise_id | UUID |
| legal_entity_id | UUID |
| brand_id | UUID |
| code | VARCHAR(30) |
| name | VARCHAR(200) |
| type | ENUM |
| business_head_id | UUID |
| cost_center_id | UUID |
| profit_center_id | UUID |
| status | ENUM |
| created_at | TIMESTAMP |

### Supporting Tables

- business_unit_product
- business_unit_branch
- business_unit_department
- business_unit_budget
- business_unit_kpi
- business_unit_calendar
- business_unit_document
- business_unit_workflow
- business_unit_settings
- business_unit_audit

---

## APIs

```text
GET    /api/v1/eom/business-units
POST   /api/v1/eom/business-units
GET    /api/v1/eom/business-units/{id}
PUT    /api/v1/eom/business-units/{id}
PATCH  /api/v1/eom/business-units/{id}/status
GET    /api/v1/eom/business-units/{id}/analytics
GET    /api/v1/eom/business-units/{id}/health
GET    /api/v1/eom/business-units/{id}/kpis
```

---

## Events

```text
BUSINESS_UNIT_CREATED
BUSINESS_UNIT_UPDATED
BUSINESS_UNIT_ACTIVATED
BUSINESS_HEAD_CHANGED
PRODUCT_ASSIGNED
BRANCH_ASSIGNED
BUDGET_UPDATED
KPI_UPDATED
BUSINESS_UNIT_HEALTH_CHANGED
```

---

## Backend Structure

```text
services/eom/business-unit/
├── domain/
├── application/
├── infrastructure/
├── api/
├── events/
├── integrations/
└── tests/
```

---

## Frontend Structure

```text
modules/eom/business-unit/
├── dashboard/
├── list/
├── create/
├── details/
├── budget/
├── analytics/
├── reports/
├── settings/
├── components/
└── hooks/
```

---

## Integration Points

Business Unit Management should integrate with:

- HRMS for employee assignment
- Accounting for cost and profit centers and budgets
- Lending for product ownership
- Deposits
- Treasury
- CRM
- Workflow Engine
- Document Management
- Analytics
- AI Platform

---

## Definition of Done

Business Unit Management is complete when it supports:

- Multi-business structures
- Product ownership
- Budget ownership
- Branch allocation
- KPI ownership
- Workflow integration
- Financial reporting
- Health scoring
- Audit trail
- AI insights

---

## Enterprise Recommendation

Instead of treating a Business Unit as only an organizational level, it should be modeled as a Business Performance Hub.

Every Business Unit should provide five synchronized views:

### 1. Business View

- Products
- Services
- Customers
- Market segments

### 2. Financial View

- Revenue
- Expenses
- Profit
- Budget
- Forecast

### 3. Operations View

- Branches
- Employees
- Capacity
- SLA
- Workflow performance

### 4. Risk View

- NPA (for lending)
- Audit issues
- Compliance exceptions
- Operational incidents

### 5. Strategy View

- Annual targets
- OKRs
- Growth initiatives
- AI recommendations
- Benchmarking against other business units

This makes Business Units active management entities rather than static master data, giving executives a real-time view of enterprise performance.

---

## Next Package

The next package should be EOM-005 — Geographic Organization Management, covering:

- Country
- State/Province
- District
- City
- Zone
- Region
- Area
- Cluster

This becomes the geographic backbone for branch management, customer assignment, collections, sales, field operations, and logistics across ARTH.OS.
