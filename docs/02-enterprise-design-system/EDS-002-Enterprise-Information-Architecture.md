# EDS-002: Enterprise Information Architecture

**Version:** 1.0

**Status:** Draft

---

## 1. Product Hierarchy

ARTH.OS is organized into:

- Products
- Modules
- Features
- Screens

Top-level product tree:

```
ARTH.OS
├── Home
├── Workspace
├── Customers
├── Lending
├── Deposits
├── Gold Loans
├── Treasury
├── Accounting
├── HRMS
├── CRM
├── Risk
├── Compliance
├── Reports
├── Administration
└── AI
```

No module should have more than 7–9 top-level menu items.

---

## 2. User Personas

The UI adapts by role so users see the workflows they need.

### Executive

- CEO
- MD
- CFO
- COO
- CRO

Home:

```
Executive Dashboard
Business KPIs
Approvals
Alerts
AI Insights
```

### Branch Operations

- Branch Manager
- Assistant Manager

Home:

```
Branch Dashboard
Today's Business
Customers
Collections
Cash Position
Approvals
```

### Loan Officer

Home:

```
My Leads
Applications
Pending Documents
Disbursements
Tasks
```

### Gold Appraiser

Home:

```
Gold Valuation
Gold Packets
Renewals
Auction Queue
Today's Customers
```

### HR Executive

Home:

```
Employees
Attendance
Leave
Recruitment
Payroll
Approvals
```

### Finance Officer

Home:

```
General Ledger
Vouchers
Bank Book
Cash Book
Reports
```

### Auditor

Home:

```
Audit Dashboard
Exceptions
Pending Reviews
Logs
Compliance
```

---

## 3. Navigation Model

The navigation model is limited to three levels only:

```
Level 1 Product
Level 2 Module
Level 3 Screen
```

Example:

```
HRMS ↓ Employees ↓ Employee Profile
```

Not:

```
HRMS ↓ Administration ↓ Organization ↓ Employee ↓ Management ↓ Profile
```

---

## 4. Workspace Pattern

Every module follows a consistent workspace pattern:

```
Dashboard ↓ List ↓ Detail ↓ Create/Edit Wizard ↓ Reports ↓ Settings
```

Example:

```
Employees Dashboard
Employee List
Employee Profile
Employee Wizard
Reports
Settings
```

---

## 5. Dashboard Architecture

Every dashboard contains:

```
Header
KPIs
Quick Actions
Charts
Recent Activity
Pending Approvals
Tasks
AI Insights
```

Dashboards never contain forms.

---

## 6. Global Search

There is one global search experience for the entire platform.

Searchable entities include:

```
Customer
Employee
Loan
Deposit
Gold Packet
Voucher
Journal
Branch
Department
Vendor
Invoice
Asset
Policy
```

Results are grouped by category.

---

## 7. Breadcrumb Standard

Example:

```
Home > HRMS > Employees > Employee Profile
```

Maximum breadcrumb depth: 4 levels.

---

## 8. Screen Types

The platform defines only six screen types:

### Dashboard

Business overview.

### List

Searchable grid.

### Details

Complete record view.

### Wizard

Create/Edit flow.

### Analytics

Charts and business intelligence.

### Settings

Configuration screens.

Nothing else.

---

## 9. Right Drawer Pattern

Use right-hand drawers instead of full navigation away from list context.

Example:

```
Employee List ↓ Click Employee ↓ Right Drawer Opens
Overview
Attendance
Leave
Payroll
```

The list remains visible.

---

## 10. Workspace Header

Every screen begins with:

```
Title
Breadcrumb
Primary Action
Secondary Actions
Search
Filters
```

---

## 11. Action Hierarchy

Buttons are ordered:

```
Primary
Secondary
Danger
```

Example:

```
Create Employee
Export
Delete
```

---

## 12. Menu Structure

### Customers

```
Dashboard
Prospects
Customers
Customer 360
Relationships
Documents
KYC
Reports
```

### Lending

```
Dashboard
Applications
Approvals
Disbursement
Repayments
Collections
Recovery
Reports
```

### Accounting

```
Dashboard
Chart of Accounts
Journals
General Ledger
Sub Ledger
Cash Book
Bank Book
Reports
```

### HRMS

```
Dashboard
Organization
Employees
Recruitment
Attendance
Leave
Payroll
Performance
Assets
Reports
```

---

## 13. Mobile Navigation

Mobile supports a maximum of 5 bottom tabs.

Example:

```
Home
Tasks
Search
Notifications
Profile
```

Everything else lives in a More menu.

---

## 14. Permission-Based Navigation

Users only see authorized modules.

Example:

CEO:

```
Dashboard
Reports
Accounting
HRMS
AI
```

Loan Officer:

```
Dashboard
Customers
Applications
Collections
```

This keeps navigation simple and secure.

---

## 15. Cross-Module Links

Users should not need to search manually to move between related records.

Example: Customer Profile

```
Overview
Loans
Deposits
Gold Loans
Documents
Behavior
Timeline
```

Example: Employee Profile

```
Overview
Payroll
Attendance
Leave
Performance
Assets
```

---

## 16. Navigation Rules

1. Maximum 3 clicks to any common task.
2. Maximum 4 breadcrumb levels.
3. Never show more than 9 items in a menu section.
4. Dashboards never contain data-entry forms.
5. Creation always uses a wizard.
6. Details always include timeline and audit information.
7. Navigation is filtered by user role and permissions.

---

## Recommended Improvement

Introduce workspace personalization early:

- Pin frequently used screens
- Save favorite reports and searches
- Reorder dashboard widgets
- Create personal shortcuts
- Save table layouts and filters
- Switch between multiple workspaces (Operations, Month End, Collections)

This improves usability without changing the underlying IA.

---

## Deliverable Status

- ✅ EDS-001 Design Principles — Complete
- ✅ EDS-002 Information Architecture — Complete
- ⏳ EDS-003 Navigation System — Next
- ⏳ EDS-004 Enterprise App Shell — Pending
- ⏳ EDS-005 Design Tokens — Pending

---

## Next Deliverable

EDS-003: Enterprise Navigation System — define sidebar behavior, global search experience, breadcrumbs, quick actions, keyboard shortcuts, and role-based navigation rules.
