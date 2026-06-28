# EOM-013 — Financial Organization Management (FOM)

## Overview

Financial Organization Management is the enterprise backbone for all money-related ownership, accountability, budgeting, and profitability across ARTH.OS. It is not a simple cost center master. It is a cross-functional financial operating model used by accounting, GL, budgeting, treasury, procurement, HRMS, assets, projects, CRM, lending, deposits, and gold loan operations.

The module defines who owns money, who spends money, who earns money, who is accountable, and how financial responsibility is structured across the enterprise.

---

## Vision

A financial organization defines:

- who owns money
- who spends money
- who earns money
- who is accountable
- how budgets are controlled
- how profitability is measured
- how financial performance is governed across the enterprise

---

## Financial Hierarchy

```text
Enterprise
↓
Legal Entity
↓
Business Unit
↓
Branch
↓
Financial Organization
├── Cost Center
├── Profit Center
├── Budget Center
├── Revenue Center
├── Responsibility Center
├── Investment Center
├── Internal Order
└── Project
```

---

## Financial Objects

### Cost Center

Responsible for expenses.

Example:

```text
HR
IT
Operations
Marketing
Admin
```

### Profit Center

Responsible for profitability.

Example:

```text
Gold Loan
Personal Loan
Deposits
Treasury
Forex
```

### Budget Center

Owns budgets.

Example:

```text
Operations Budget
Marketing Budget
IT Budget
```

### Revenue Center

Tracks income.

Example:

```text
Loan Processing
Interest Income
Forex Income
Locker Income
```

### Responsibility Center

Business accountability.

Example:

```text
Regional Office
Branch
Call Center
Collections
```

### Investment Center

Tracks capital investment.

Example:

```text
Corporate Office
Technology
Infrastructure
```

### Internal Orders

Temporary financial tracking.

Example:

```text
New Branch Setup
Branch Renovation
ERP Implementation
Marketing Campaign
Audit Project
```

---

## Financial Dashboard

### KPIs

- Cost Centers
- Profit Centers
- Budgets
- Revenue
- Expenses
- Profit
- Budget Variance
- ROI
- Health Score

### Charts

- Cost by Department
- Revenue by Business Unit
- Profit by Branch
- Budget Utilization
- Forecast vs Actual

---

## Workspace

```text
Dashboard
↓
Financial Explorer
↓
Cost Centers
↓
Profit Centers
↓
Budgets
↓
Internal Orders
↓
Reports
```

---

## Financial Explorer

```text
Enterprise
↓
Business Unit
↓
Branch
↓
Cost Center
↓
GL
↓
Expenses
```

Features:

- Interactive tree view
- Drill-down navigation
- Parent-child hierarchy
- Cross-functional financial context

---

## Cost Center Profile

### Tabs

- Overview
- Budget
- Expenses
- Assets
- Employees
- Projects
- Approvals
- Timeline
- Audit
- AI

---

## Profit Center Profile

### Tabs

- Overview
- Revenue
- Expenses
- Profit
- KPIs
- Forecast
- Timeline
- AI

---

## Budget Center Profile

Displays:

```text
Budget
↓
Allocated
↓
Committed
↓
Actual
↓
Available
```

---

## Create Cost Center Wizard

### Step 1 — General

Fields:

- Code
- Name
- Category
- Status
- Description

### Step 2 — Organization

Fields:

- Enterprise
- Legal Entity
- Business Unit
- Branch
- Department

### Step 3 — Financial

Fields:

- Parent Cost Center
- Budget Owner
- GL Mapping
- Currency

### Step 4 — Budget

Fields:

- Annual Budget
- Quarterly Budget
- Monthly Budget
- Approval Limits

### Step 5 — Review

- Review summary
- Approval route
- Create and activate

---

## Cost Allocation

Supports:

- Direct
- Percentage
- Headcount
- Revenue
- Floor Area
- Transaction Volume
- Activity Based Costing (ABC)

---

## Budget Management

Supports:

```text
Original Budget
↓
Revised Budget
↓
Committed
↓
Actual
↓
Variance
↓
Forecast
```

---

## Internal Orders

Lifecycle:

```text
Draft
↓
Approved
↓
Open
↓
Active
↓
Closed
↓
Archived
```

---

## Financial Ownership

Every financial object has:

- Owner
- Approver
- Reviewer
- Auditor

---

## Financial Calendar

Supports:

- Financial Year
- Accounting Periods
- Budget Cycle
- Forecast Cycle
- Closing Calendar

---

## Budget Approval Workflow

```text
Department
↓
Finance
↓
CFO
↓
Approved
```

---

## Budget Versioning

Supports:

```text
Original
↓
Revision 1
↓
Revision 2
↓
Forecast
↓
Actual
```

---

## Profitability Analysis

Displays:

```text
Revenue
↓
Direct Cost
↓
Indirect Cost
↓
Gross Profit
↓
Operating Profit
↓
Net Profit
```

---

## Allocation Rules

Examples:

```text
IT Expenses → Allocate → All Departments → By Employee Count
```

or

```text
Rent → Allocate → Branches → By Floor Area
```

---

## AI Features

Examples:

```text
Recommend budget reduction
↓
Detect unusual expenses
↓
Predict budget overrun
↓
Suggest cost allocation
↓
Find inefficient cost centers
↓
Recommend restructuring
↓
Forecast profitability
```

---

## Reports

Standard reports:

- Cost Center Register
- Profit Center Register
- Budget Report
- Budget Variance
- Allocation Report
- Internal Order Report
- Revenue Report
- Profitability Report
- Financial Organization Health

---

## Financial Health Score

Calculated using:

- Budget variance
- Revenue achievement
- Expense control
- Allocation accuracy
- Audit findings
- Forecast accuracy

Example:

```text
Financial Health Score: 95% ★★★★★
```

---

## Database Tables

```text
cost_center
profit_center
budget_center
revenue_center
investment_center
responsibility_center
internal_order
budget
budget_version
allocation_rule
allocation_result
financial_owner
financial_calendar
financial_health
financial_ai
financial_audit
```

---

## APIs

```text
GET    /api/v1/finance/cost-centers
POST   /api/v1/finance/cost-centers
GET    /api/v1/finance/profit-centers
POST   /api/v1/finance/profit-centers
GET    /api/v1/finance/budgets
POST   /api/v1/finance/budgets
GET    /api/v1/finance/internal-orders
POST   /api/v1/finance/internal-orders
GET    /api/v1/finance/allocations
POST   /api/v1/finance/allocations
GET    /api/v1/finance/dashboard
```

---

## Events

```text
COST_CENTER_CREATED
PROFIT_CENTER_CREATED
BUDGET_CREATED
BUDGET_REVISED
ALLOCATION_EXECUTED
INTERNAL_ORDER_OPENED
INTERNAL_ORDER_CLOSED
FINANCIAL_HEALTH_CHANGED
```

---

## Backend Structure

```text
services/finance/financial-organization/
├── cost-center/
├── profit-center/
├── budget-center/
├── revenue-center/
├── internal-order/
├── allocation/
├── budget/
├── analytics/
├── ai/
└── tests/
```

---

## Frontend Structure

```text
modules/finance/financial-organization/
├── dashboard/
├── explorer/
├── cost-centers/
├── profit-centers/
├── budgets/
├── allocations/
├── reports/
├── analytics/
├── settings/
└── components/
```

---

## Integration Matrix

- General Ledger: GL ownership
- Accounts Payable: expense booking
- Accounts Receivable: revenue ownership
- Fixed Assets: asset ownership
- Procurement: budget validation
- HRMS: payroll cost allocation
- Treasury: liquidity and funding
- Lending: product profitability
- Deposits: interest cost analysis
- Gold Loan: portfolio profitability
- Projects: internal order tracking
- BI & Analytics: financial dashboards

---

## Financial Organization 360

Every financial object has a 360° view.

### Executive View

- Revenue
- Cost
- Profit
- Budget utilization

### Budget View

- Approved budget
- Committed budget
- Actual spend
- Forecast

### Accounting View

- Linked GL accounts
- Journal entries
- Closing status

### Operations View

- Departments
- Employees
- Assets
- Projects

### Risk View

- Budget overruns
- Audit findings
- Policy violations

### AI View

- Cost optimization
- Revenue opportunities
- Forecast accuracy
- Allocation recommendations

---

## Definition of Done

Financial Organization Management is complete when it provides:

- Cost Center hierarchy
- Profit Center hierarchy
- Budget Centers
- Revenue Centers
- Responsibility Centers
- Investment Centers
- Internal Orders
- Budget versioning
- Allocation engine
- Financial calendars
- Approval workflows
- AI insights
- Audit trail
- Enterprise reporting

---

## Major Enhancement Recommendation

To distinguish ARTH.OS from SAP, Oracle, and Temenos, the platform should introduce a Financial Digital Twin.

Every Cost Center, Profit Center, and Budget Center should continuously expose:

### Financial View

- Current budget
- Spend
- Revenue
- Profitability

### Operational View

- Employees
- Assets
- Active projects
- Workload

### Strategic View

- OKRs
- Budget goals
- Growth initiatives

### Risk View

- Budget overruns
- Compliance exceptions
- Audit observations

### Predictive AI View

- Budget burn rate forecast
- Cash flow forecast
- Cost anomaly detection
- Profitability projection
- Optimization recommendations

This makes Financial Organization Management a live decision-support system rather than a static master-data model.

---

## Recommended Implementation Order

With the enterprise organization and workforce layers complete, the next platform foundation should be:

1. Identity & Access Management (IAM)
2. Document Management System (DMS)
3. Accounting & General Ledger
4. Customer Information File (CIF)
5. Loan Origination & Loan Management
6. Deposit Management
7. Gold Loan Management
8. Treasury & Forex
9. Risk, Compliance & Audit
10. CRM & Collections
11. AI & Analytics Platform

IAM should be prioritized because every downstream module depends on secure identity, authorization, approval delegation, and role management.
