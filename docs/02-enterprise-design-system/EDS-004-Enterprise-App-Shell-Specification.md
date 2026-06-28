# EDS-004: Enterprise App Shell Specification

**Version:** 1.0

**Priority:** ⭐⭐⭐⭐⭐

**Owner:** Platform Team

---

## Purpose

The App Shell is the permanent framework that every ARTH.OS module lives inside.

HRMS

Accounting

Customer

Loans

Treasury

CRM

Risk

AI

...all use the exact same shell.

Think of it as the Windows desktop for ARTH.OS.

---

## Enterprise Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│ LOGO │ Search │ AI │ Tasks │ Notifications │ Help │ Profile │ Branch ▼     │
│───────────────┬────────────────────────────────────────────────────────────┤
│               │ Breadcrumb                                                 │
│               ├────────────────────────────────────────────────────────────┤
│               │ Workspace Header                                           │
│ Sidebar       ├────────────────────────────────────────────────────────────┤
│               │ KPI Cards                                                  │
│               ├────────────────────────────────────────────────────────────┤
│               │ Action Bar                                                 │
│               ├────────────────────────────────────────────────────────────┤
│               │ Search + Filters                                           │
│               ├────────────────────────────────────────────────────────────┤
│               │                                                            │
│               │ Enterprise Workspace                                       │
│               │                                                            │
│               │                                                            │
│               ├────────────────────────────────────────────────────────────┤
│               │ Status Bar                                                 │
└───────────────┴────────────────────────────────────────────────────────────┘
```

---

## Shell Architecture

```
<AppShell>
  Header
  Sidebar
  Workspace
  Right Panel
  Status Bar
  Floating AI
  Global Dialogs
  Notifications
  Toast
</AppShell>
```

---

## Header

Height: `64px`

Contains:

- Logo
- Search
- AI Assistant
- Notifications
- Approvals
- Tasks
- Help
- Theme
- Profile
- Branch Switcher

Never changes.

---

## Sidebar

Expanded width: `280px`

Collapsed width: `72px`

Contains:

- Dashboard
- Customers
- Lending
- Deposits
- Accounting
- HRMS
- Reports
- Administration

Supports:

- Pinning
- Favorites
- Recent
- Drag to reorder favorites

---

## Workspace

The center area.

Every module plugs into this.

```
Workspace ↓ Dashboard ↓ List ↓ Details ↓ Wizard ↓ Reports
```

---

## Workspace Header

Every page includes:

- Title
- Description
- Breadcrumb
- Primary Action
- Secondary Action

Example:

```
Employee Management
Manage employees across all branches.
+ New Employee
Export
```

---

## KPI Strip

Always below the header.

Example:

```
Employees 1284  Departments 16  Attendance 97%  Payroll ₹4.3Cr  Pending Leave 18
```

Hidden automatically if no KPIs exist.

---

## Action Bar

Contains:

- Primary Action
- Secondary Action
- Import
- Export
- Bulk Action

Example:

```
+ Employee  Import  Export  Archive
```

---

## Search & Filters

Unified component.

Example:

```
Search Employees  Department  Branch  Status  Grade  Date Joined  Reset  Save View
```

---

## Enterprise Workspace

Contains:

- Grid
- Cards
- Charts
- Calendar
- Timeline

Depends on the page.

---

## Right Context Panel

Instead of popup windows.

Opens from the right.

Used for:

- Quick View
- Quick Edit
- Comments
- Activity
- Documents
- Audit
- AI Summary

Width: `420px`

Resizable.

---

## AI Dock

Always available.

Floating button:

```
Ask FinDNA
```

Expands into:

- Chat
- Insights
- Suggested Actions
- Recent Queries

---

## Notifications

Slide-over panel.

Tabs:

```
Alerts  Tasks  Approvals  Mentions  System
```

---

## Status Bar

Bottom of the shell.

Shows:

- Tenant
- Branch
- Environment
- API Status
- Sync Status
- Time
- Version

Example:

```
ARTH.OS v1.0  Production  Branch 1204  Connected
```

---

## Modal Standard

Modals are only for:

- Confirmations
- Small forms
- Warnings

Never for:

- Employee creation
- Loan creation
- Customer creation

Those always use wizards.

---

## Drawer Standard

Use drawers for:

- Quick View
- Edit
- Comments
- History
- Audit

Never navigate away.

---

## Responsive Behaviour

### Desktop

```
Sidebar Expanded
```

### Tablet

```
Sidebar Collapsed
```

### Mobile

Sidebar becomes:

```
Bottom Navigation + Hamburger
```

---

## Loading States

Never blank.

Use skeleton loading instead of spinner.

---

## Error States

Every page contains:

- Illustration
- Message
- Retry
- Contact Support

---

## Empty State

Example:

```
No Employees Yet
Create your first employee.
[ Create Employee ]
```

---

## Offline Mode

Shows:

```
Offline  Changes Saved Locally  Sync Pending
```

Useful for field officers and mobile users.

---

## Theme System

Supports:

- Light
- Dark
- High Contrast

Brand colors configurable by tenant.

---

## Multi-Tenant Support

Every tenant can configure:

- Logo
- Primary Color
- Login Screen
- Email Templates
- Reports
- Footer
- Domain
- Time Zone
- Currency
- Locale

without changing code.

---

## Shell Events

The App Shell publishes events that modules can react to:

```
USER_SWITCHED_BRANCH
USER_CHANGED_THEME
NOTIFICATION_RECEIVED
TASK_ASSIGNED
AI_PANEL_OPENED
WORKSPACE_CHANGED
SEARCH_EXECUTED
```

---

## Performance Targets

| Metric | Target |
|---|---|
| Initial shell render | < 2s |
| Route change | < 300ms |
| Sidebar expand/collapse | < 150ms |
| Command palette open | < 100ms |
| Global search suggestions | < 250ms |
| Drawer open | < 200ms |

---

## Component Tree

```
<AppShell>
  Header
    Logo
    Search
    AI
    Tasks
    Notifications
    Profile
    BranchSwitcher
  Sidebar
    Navigation
    Favorites
    Recent
  Workspace
    Breadcrumb
    WorkspaceHeader
    KPIStrip
    ActionBar
    FilterBar
    Content
  RightDrawer
  NotificationPanel
  TaskPanel
  AIAssistant
  ToastProvider
  StatusBar
</AppShell>
```

---

## Suggested Next.js Structure

```
packages/design-system/app-shell/
  ├── AppShell/
  ├── Header/
  ├── Sidebar/
  ├── Workspace/
  ├── WorkspaceHeader/
  ├── KPIStrip/
  ├── ActionBar/
  ├── FilterBar/
  ├── RightDrawer/
  ├── StatusBar/
  ├── NotificationPanel/
  ├── TaskPanel/
  ├── CommandPalette/
  ├── AIAssistant/
  └── hooks/
```

---

## Acceptance Criteria

The App Shell is complete when:

- One shell is shared across all products.
- Layout adapts to desktop, tablet, and mobile.
- Global search is available everywhere.
- Notifications, tasks, and approvals are accessible from every page.
- Right-side drawer supports contextual work without losing navigation state.
- Tenant branding can be changed without modifying code.
- Accessibility and keyboard navigation are supported.

---

## Deliverable Status

- ✅ EDS-001 Design Principles — Complete
- ✅ EDS-002 Information Architecture — Complete
- ✅ EDS-003 Enterprise Navigation System — Complete
- ✅ EDS-004 Enterprise App Shell — Complete
- ⏳ EDS-005 Design Tokens — Next

---

## Architecture Recommendation

Before implementing any module, create a `packages/design-system` package that contains the App Shell, navigation, and shared UI components. All applications should consume this package instead of implementing their own layouts. This ensures a consistent enterprise experience, simplifies maintenance, and allows UX or branding changes to roll out across the entire platform from one place.
