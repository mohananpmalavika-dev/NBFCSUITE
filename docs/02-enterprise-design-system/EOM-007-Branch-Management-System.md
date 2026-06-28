# EP-007 — Branch Management System (BMS)

## Overview

Branch Management is one of the most critical modules in ARTH.OS because almost every other module depends on the concept of a branch. Customer, loan, deposit, gold loan, accounting, HRMS, treasury, forex, CRM, inventory, collections, reporting, and AI all operate through a branch context.

This is the operational heart of the enterprise.

---

## Why Branch Management is Critical

Every module references branch:

```text
Customer
Loan
Deposit
Gold Loan
Accounting
HRMS
Treasury
Forex
CRM
Inventory
Collections
Reports
AI
```

Everything belongs to a branch.

---

## Enterprise Hierarchy

```text
Enterprise
↓
Brand
↓
Legal Entity
↓
Business Unit
↓
Geography
↓
Branch
↓
Department
↓
Employee
```

---

## What is a Branch?

A branch is not merely an address. It is an independent operating unit with:

- Employees
- Customers
- Cash
- Vault
- Gold
- Documents
- Accounting
- Assets
- Inventory
- Security
- Business KPIs

---

## Branch Dashboard

### KPIs

- Active Customers
- Loans
- Deposits
- Gold Loan
- Cash Balance
- Vault Balance
- Forex Position
- Revenue
- Expenses
- Profit
- Employees
- Attendance
- Assets
- Complaints
- Audit Score
- AI Health Score

### Charts

- Loan portfolio
- Deposit trend
- Customer growth
- Collections
- Cash position
- Employee distribution
- Branch performance

---

## Branch Workspace

```text
Dashboard
↓
Branch Directory
↓
Branch Profile
↓
Operations
↓
Financials
↓
HR
↓
Vault
↓
Assets
↓
Reports
↓
Audit
```

---

## Branch Directory

### Enterprise grid columns

- Code
- Name
- Branch Type
- Status
- Region
- Manager
- Employees
- Customers
- Revenue
- Health

### Features

- Saved views
- Search
- Filters
- Bulk update
- Export
- AI search

---

## Branch Profile

### Tabs

- Overview
- Organization
- Operations
- Finance
- Customers
- Employees
- Vault
- Cash
- Inventory
- Assets
- Documents
- Security
- Risk
- Audit
- Timeline
- AI

---

## Create Branch Wizard

### Step 1 — General

Fields:

- Branch Code
- Branch Name
- Display Name
- Branch Type
- Status
- Business Unit
- Legal Entity

### Step 2 — Geography

Fields:

- Country
- State
- District
- City
- Zone
- Region
- Area
- Cluster
- Latitude
- Longitude

### Step 3 — Contact

Fields:

- Address
- Phone
- Email
- Website
- Google Location
- Emergency Contact

### Step 4 — Operations

Fields:

- Working Days
- Business Hours
- Cash Hours
- Gold Loan Enabled
- Deposit Enabled
- Forex Enabled
- ATM
- Locker
- Kiosk

### Step 5 — Finance

Fields:

- Cost Center
- Profit Center
- GL Mapping
- Cash Limit
- Vault Limit
- Approval Matrix

### Step 6 — Infrastructure

Fields:

- Building
- Floor
- Parking
- ATM
- Generator
- UPS
- Strong Room
- Vault

### Step 7 — Security

Fields:

- Biometric
- CCTV
- Alarm
- Fire Insurance
- Access Control

### Step 8 — Staff

Fields:

- Branch Manager
- Operations Manager
- Cashier
- Gold Appraiser
- Relationship Manager
- Security Officer

### Step 9 — Products

Enable products such as:

- Gold Loan
- Vehicle Loan
- MSME
- Personal Loan
- Deposit
- Forex
- Insurance
- Mutual Fund

### Step 10 — Documents

Upload:

- Branch License
- Rental Agreement
- Insurance
- Fire Certificate
- Building Plan
- GST
- Photos

### Step 11 — Review and Create

Flow:

```text
Review
↓
Validation
↓
Workflow
↓
Create
```

---

## Branch 360

The primary branch experience should be a complete operational screen with:

```text
Overview
↓
Finance
↓
Operations
↓
HR
↓
Customers
↓
Inventory
↓
Audit
↓
Risk
↓
AI
```

---

## Branch Finance

Displays:

- Today’s Collection
- Today’s Disbursement
- Cash
- Vault
- Expenses
- Revenue
- Profit
- Budget
- GL
- Bank Balance

---

## Branch Operations

Shows:

- Customer Visits
- Loans
- Deposits
- Gold Collections
- Pending Approvals
- Service Queue
- Appointments

---

## Branch HR

Shows:

- Employees
- Attendance
- Leave
- Payroll
- Vacancies
- Training
- Performance

---

## Branch Vault

Displays:

- Gold Packets
- Cash
- Seals
- Keys
- Vault Capacity
- Insurance
- Audit

---

## Branch Asset

Displays:

- Computers
- Furniture
- Printers
- Cash Counter
- UPS
- Generator
- Vehicle
- Biometric

---

## Branch Performance

### KPIs

- Revenue
- Profit
- Customers
- Loan Growth
- Deposit Growth
- Collection Efficiency
- Cross Sell
- Customer Satisfaction
- Audit Score

---

## Branch Health Score

Calculated from:

- Audit
- Cash mismatch
- SLA
- Employee shortage
- Compliance
- Revenue
- Customer complaints
- Security alerts

Example:

```text
Branch Health: 94%
Rating: ★★★★★
```

---

## Branch Workflow

```text
Draft
↓
Operations
↓
Finance
↓
HR
↓
IT
↓
Compliance
↓
Approval
↓
Active
```

---

## Branch Calendar

Supports:

- Working days
- Holidays
- Local holidays
- Cash closing
- Gold audit
- EOD
- EOM

---

## Branch AI

Example capabilities:

```text
Show branch summary.
↓
Predict cash shortage.
↓
Recommend more staff.
↓
Find idle employees.
↓
Predict gold demand.
↓
Predict customer walk-in.
↓
Recommend branch expansion.
```

---

## Branch Reports

Standard reports:

- Branch Register
- Branch Performance
- Branch Revenue
- Branch Expenses
- Cash Position
- Vault Report
- Gold Register
- Employee Register
- Customer Register
- Audit Report
- Health Report

---

## Branch Events

```text
BRANCH_CREATED
BRANCH_OPENED
BRANCH_CLOSED
MANAGER_CHANGED
VAULT_OPENED
VAULT_CLOSED
CASH_LIMIT_CHANGED
PRODUCT_ENABLED
HEALTH_CHANGED
```

---

## Branch Database

```text
branch
branch_contact
branch_business
branch_finance
branch_security
branch_infrastructure
branch_manager
branch_product
branch_service
branch_document
branch_asset
branch_calendar
branch_health
branch_ai
branch_audit
```

---

## APIs

```text
GET    /api/v1/branches
POST   /api/v1/branches
GET    /api/v1/branches/{id}
PUT    /api/v1/branches/{id}
PATCH  /api/v1/branches/{id}/status
GET    /api/v1/branches/{id}/dashboard
GET    /api/v1/branches/{id}/health
GET    /api/v1/branches/{id}/timeline
GET    /api/v1/branches/{id}/analytics
```

---

## Permissions

| Role | Access |
| --- | --- |
| Enterprise Admin | All |
| Branch Manager | Own Branch |
| Operations Manager | Operations |
| Cashier | Cash Only |
| Gold Appraiser | Gold Module |
| HR Manager | HR |
| Auditor | Read Only |
| Compliance Officer | Compliance |

---

## Backend Structure

```text
services/eom/branch/
├── domain/
├── application/
├── infrastructure/
├── api/
├── integrations/
├── analytics/
├── ai/
├── events/
└── tests/
```

---

## Frontend Structure

```text
modules/eom/branch/
├── dashboard/
├── list/
├── create/
├── profile/
├── operations/
├── finance/
├── hr/
├── vault/
├── analytics/
├── reports/
├── settings/
├── components/
└── hooks/
```

---

## Integrations

Branch Management should integrate with:

- Customer Management
- Loan Origination
- Gold Loan
- Deposits
- Accounting & GL
- Treasury
- Cash Management
- Vault Management
- Forex
- HRMS
- CRM
- Collections
- Procurement
- Asset Management
- Risk & Compliance
- BI & Analytics
- AI Platform

---

## Definition of Done

Branch Management is complete when it provides:

- Branch 360
- Multi-entity support
- Financial configuration
- Operational configuration
- Security and infrastructure management
- Product enablement
- Workflow and approvals
- Audit trail
- AI insights
- Analytics dashboard
- Health scoring
- GIS integration

---

## Enterprise Recommendation

Rather than treating a branch as just an office, it should be modeled as a Digital Branch Twin.

Every branch should expose ten synchronized views:

- Executive: KPIs and health score
- Customer: Customer mix and satisfaction
- Lending: Loan pipeline, disbursement, collections, and NPA
- Deposits: Deposit portfolio and maturity schedule
- Treasury: Cash position, vault, liquidity, and transfers
- HR: Staffing, attendance, performance, vacancies
- Operations: Queue, SLA, turnaround time, appointments
- Assets: Fixed assets, maintenance, warranties
- Risk & Compliance: Audit findings, AML alerts, incidents
- AI: Predictions, recommendations, anomaly detection

This turns each branch into a live operational control center for executives, branch managers, auditors, and operations teams.

---

## Next Recommended Module

With Branch Management complete, the next recommended module is EOM-008 — Department Management.

Rather than making it just a list of departments, it should be built as a Business Capability Model with:

- Department hierarchy
- Sections and teams
- Position planning
- Cost center mapping
- Profit center mapping
- Budget ownership
- SLA ownership
- Workflow ownership
- KPI ownership
- Service catalog
- Cross-department dependencies
- AI-driven workload and capacity analysis

This creates the organizational backbone shared by HRMS, Accounting, Procurement, ITSM, and Workflow Engine.
