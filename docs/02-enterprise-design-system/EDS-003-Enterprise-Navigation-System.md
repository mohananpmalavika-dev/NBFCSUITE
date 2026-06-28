# EDS-003: Enterprise Navigation System

**Version:** 1.0

**Priority:** ⭐⭐⭐⭐⭐

**Owner:** Platform Team

---

## Goal

Build a navigation system where:

- A new employee can find any feature in under 10 seconds.
- No feature is more than 3 clicks away.
- The UI adapts to the user's role.
- The navigation scales from 50 screens to 1,000+ screens without becoming confusing.

---

## Navigation Architecture

Five navigation layers:

```
Global Navigation │ Workspace Navigation │ Module Navigation │ Page Navigation │ Context Navigation
```

---

## Level 1 — Global Navigation

Persistent left sidebar.

```
🏠 Dashboard
👥 Customers
💰 Lending
🏦 Deposits
🪙 Gold Loans
💵 Treasury
📒 Accounting
👨‍💼 HRMS
🤝 CRM
⚠ Risk
✔ Compliance
📊 Reports
⚙ Administration
🤖 AI
🔌 Integration
```

Never more than 15 items.

---

## Sidebar Behaviour

### Expanded

```
LOGO
Dashboard
Customers
Lending
Accounting
HRMS
Reports
Settings
```

Width: 280px.

### Collapsed

```
🏠 👥 💰 📒 👨‍💼
```

Width: 72px.

Hover expands.

---

## Workspace Header

Every workspace starts with:

```
Breadcrumb
Workspace Title
Description
Primary Actions
Secondary Actions
```

Example:

```
HRMS Employee Management
Manage employees across all branches.
+ New Employee
Import
Export
```

---

## Top Navigation

Contains:

```
Global Search
AI Assistant
Notifications
Approvals
Tasks
Help
Profile
Tenant
Branch
```

Never place business menus here.

---

## Global Search

Universal search.

Shortcut: `Ctrl + K` or `⌘ + K`.

Searches:

```
Customer
Employee
Loan
Branch
Voucher
GL
Department
Reports
Screens
Settings
```

---

## Search UI

```
────────────────────────────Search ARTH.OS────────────────────────────
Customers Loans Employees Screens Reports Actions
────────────────────────────
```

---

## Command Palette

Like VS Code.

Example: Typing `Employee` shows:

```
Create Employee
Employee Directory
Employee Reports
Attendance
Payroll
```

Typing `GL` shows:

```
General Ledger
GL Reports
GL Posting
GL Accounts
```

---

## Mega Navigation

Some modules need mega menus.

Example: Accounting

```
Accounting
├── Dashboard
├── Master
│   ├── COA
│   ├── Fiscal Year
│   └── Period
├── Transactions
│   ├── Journal
│   ├── Voucher
│   ├── Cash
│   └── Bank
├── Ledger
│   ├── GL
│   └── Sub Ledger
├── Reports
│   ├── Trial Balance
│   ├── Balance Sheet
│   ├── P&L
└── Settings
```

---

## HR Navigation

```
HRMS
├── Dashboard
├── Organization
│   ├── Departments
│   ├── Designation
│   ├── Grades
│   └── Positions
├── Employees
│   ├── Directory
│   ├── Onboarding
│   ├── Transfers
│   ├── Exit
├── Attendance
├── Leave
├── Payroll
├── Performance
├── Assets
├── Reports
└── Settings
```

---

## Customer Navigation

```
Customers
Dashboard
Prospects
Customer Directory
Customer 360
Relationships
Behavior
KYC
Documents
Reports
```

---

## Lending Navigation

```
Lending
Dashboard
Applications
Approvals
Disbursement
Repayment
Collections
Recovery
NPA
Reports
```

---

## Navigation Rules

Every module: maximum 9 menus.
Every submenu: maximum 9 items.
If more, split.

---

## Breadcrumb Rules

Example:

```
Home > HRMS > Employees > Employee Profile
```

Maximum 4 levels.

---

## Context Navigation

Inside Employee:

```
Overview
Employment
Attendance
Leave
Payroll
Performance
Assets
Documents
Timeline
Audit
```

Tabs.

---

## Right Drawer

Click Employee → Drawer opens.
No page reload.

---

## Favorites

Every user can pin:

```
Employee
Customer
Journal
GL
Attendance
```

---

## Recent

Automatically shows:

```
Employee
Payroll
Loan
Voucher
Report
```

---

## Workspace Switcher

User can switch:

```
Operations
Month End
Collections
HR
Accounting
```

Each workspace remembers:

- Filters
- Tables
- Layout

---

## Notifications

Grouped:

```
Approvals
Alerts
Tasks
Mentions
System
```

---

## Approval Inbox

```
Pending
In Progress
Approved
Rejected
```

---

## Task Center

My Tasks:

- Today
- Tomorrow
- Overdue
- Completed

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl + K | Search |
| G D | Dashboard |
| G H | HRMS |
| G C | Customers |
| G L | Lending |
| G A | Accounting |
| N E | New Employee |
| N C | New Customer |
| N L | New Loan |
| ? | Shortcut Help |

---

## Mobile Navigation

Bottom navigation:

```
Home
Search
Tasks
Notifications
Profile
```

Everything else in More.

---

## Permission Navigation

CEO:

```
Dashboard
Reports
Accounting
HR
AI
```

Loan Officer:

```
Customers
Applications
Collections
```

HR:

```
Employees
Attendance
Payroll
Leave
```

Users never see menus they cannot access.

---

## AI Navigation

Always visible:

```
Ask FinDNA
```

Examples:

- Explain customer risk.
- Draft an approval note.
- Find today's overdue collections.
- Explain this GL posting.
- Summarize employee performance.

---

## Navigation Principles

- Maximum 3 clicks for common tasks.
- Global search available everywhere.
- Consistent icons and labels.
- No duplicate menu items.
- Context preserved when drilling into records.
- Favorites, recent items, and personalized workspaces supported.

---

## Navigation Component Hierarchy

```
<AppShell>
├── Sidebar
│   ├── NavigationSection
│   ├── NavigationItem
│   ├── Favorites
│   └── Recent
├── Header
│   ├── Breadcrumb
│   ├── Search
│   ├── Notifications
│   ├── Approvals
│   ├── Tasks
│   ├── Profile
│   └── BranchSwitcher
├── Workspace
│   ├── WorkspaceHeader
│   ├── ActionBar
│   ├── Content
│   └── RightDrawer
└── AI Assistant
```

---

## Next.js Folder Structure

```
packages/
└── design-system/
    ├── navigation/
    │   ├── Sidebar/
    │   ├── Header/
    │   ├── Breadcrumb/
    │   ├── Search/
    │   ├── CommandPalette/
    │   ├── Favorites/
    │   ├── Recent/
    │   ├── WorkspaceSwitcher/
    │   ├── BranchSwitcher/
    │   ├── Notifications/
    │   └── TaskCenter/
    ├── layouts/
    ├── hooks/
    ├── types/
    └── utils/
```

---

## Enterprise UX Scorecard

Before implementing any navigation change, verify:

- Can the user reach common tasks in three clicks or fewer?
- Are menu labels business-oriented and consistent?
- Is navigation filtered by permissions?
- Are keyboard shortcuts available for power users?
- Does the same navigation pattern work across HRMS, Accounting, Lending, and Customer modules?
- Does the design support future growth without restructuring menus?

---

## Deliverable Status

- ✅ EDS-001 Design Principles — Complete
- ✅ EDS-002 Information Architecture — Complete
- ✅ EDS-003 Enterprise Navigation System — Complete
- ⏳ EDS-004 Enterprise App Shell — Next
- ⏳ EDS-005 Design Tokens — Pending

---

## Recommendation

Before writing a single React component, the next deliverable should be EDS-004 – Enterprise App Shell. That specification will define the exact page layout, responsive behavior, header, sidebar interactions, right-side context panel, workspace container, and extension points. Once the App Shell is complete, every module in ARTH.OS can plug into the same framework without inventing its own layout.
