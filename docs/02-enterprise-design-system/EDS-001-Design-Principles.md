# EDS-001: Design Principles

## Phase 0 — Enterprise Design System Foundation

This document defines the core design principles for ARTH.OS and establishes the foundation for every screen, workspace, and component across the platform.

### Product Philosophy

Vision

> Every employee should be able to use ARTH.OS without training.

ARTH.OS should feel like a modern enterprise suite with a simple, consistent, and human-centered experience.

### UX Principles

#### Principle 1 — Workspace Driven

The platform is organized around workspaces, not abstract form pages.

Preferred flow:

- Workspace
- Dashboard
- Lists
- Details
- Wizard

Do not design around "Forms" as the primary starting point.

#### Principle 2 — Dashboard First

Every module begins with metrics, insights, and actions, not data entry.

Preferred flow:

- Open HR
- Dashboard
- Insights
- KPIs
- Actions

Bad:

- Open HR
- 100 Fields

#### Principle 3 — Contextual Navigation

Navigation should expose related workflow tabs in context rather than forcing deep back-and-forth paths.

Preferred model:

- Employee Overview
- Payroll
- Leave
- Attendance
- Performance
- Documents
- Audit

This is a tab-driven experience, not a breadcrumb of repeated back actions.

#### Principle 4 — Progressive Disclosure

Avoid overwhelming users with too much information at once.

Preferred pattern:

- Step 1
- Step 2
- Step 3

Use wizards and step flows instead of long pages with 100 fields.

#### Principle 5 — Single Responsibility Screen

Each screen must serve one clear purpose.

Examples:

- Department List
- Employee List
- Employee Details
- Attendance
- Payroll

Never mix multiple unrelated responsibilities in one screen.

#### Principle 6 — Global Search

Provide a single, enterprise-wide search that spans all domains.

Search should cover:

- Customer
- Employee
- Loan
- Deposit
- Voucher
- GL
- Branch
- Product

One search to find everything.

#### Principle 7 — AI Everywhere

Every screen should include contextual intelligence.

Examples:

- Customer: explain repayment behavior
- Accounting: explain this journal entry
- HR: summarize employee performance

Contextual AI is a first-class interface element.

#### Principle 8 — No Popup Hell

Avoid modal overload and page reloads.

Preferred pattern:

- List
- Right drawer
- Edit
- Save

Use drawers and inline panels instead of nested popups.

#### Principle 9 — Never Lose Context

Lists remain visible while editing or reviewing details.

The list stays, and the drawer opens. The user should not lose their place.

#### Principle 10 — Mobile First

Every screen must work on desktop, tablet, and mobile.

Design for responsive layouts from the start.

### Navigation Principles

- Maximum 3 clicks to reach any destination.

Good example:

- HR
- Employees
- Create

Bad example:

- HR
- Administration
- Organization
- Employee
- Setup
- Create

### Enterprise Layout

The enterprise shell should support a clear and consistent layout:

- Logo
- Global search
- AI assistant
- Notifications
- Tasks
- Profile
- Branch selector
- Sidebar navigation for core modules
- Workspace header with contextual actions
- KPI cards and insights
- Search + filters
- Enterprise grid
- Timeline / AI panel

### Color Philosophy

Use an enterprise palette with restrained color usage.

- Primary: Blue
- Success: Green
- Warning: Amber
- Error: Red
- Neutral: Gray

Reserve color for meaning and keep 95% whitespace.

### Typography

- Headings: Inter SemiBold
- Body: Inter Regular
- Numbers: Tabular figures

### Icons

- Only Lucide icons
- No mixed icon packs

### Radius

- 12px corner radius everywhere

### Shadows

- Soft, subtle shadows
- Never heavy or aggressive

### Animation

- Fast and purposeful
- 150–200ms duration

### Data Tables

Every table must support:

- Search
- Filter
- Sort
- Export
- Column chooser
- Saved views
- Bulk actions
- Pagination

No exceptions.

### Forms

Keep multi-step forms short.

- Maximum 8–10 fields per step

### Wizards

Use wizards for every business object:

- Employee
- Customer
- Loan
- Deposit
- Branch
- Department
- Product

### Dashboard Rules

Every module should start with:

- KPIs
- Charts
- Recent activity
- Pending approvals
- Quick actions

Do not start a module with forms.

### Definition of Enterprise UI

A screen is enterprise-ready when it answers:

- Can the user complete the primary task in three clicks or fewer?
- Is the page focused on a single responsibility?
- Are key metrics visible before data entry?
- Are destructive actions protected with confirmations and audit logging?
- Does it work well on desktop, tablet, and mobile?
- Is it accessible and keyboard-friendly?
- Does it reuse shared components instead of custom one-off widgets?

---

## Deliverable Status

- ✅ EDS-001 Design Principles — Complete
- ⏳ EDS-002 Information Architecture — Next
- ⏳ EDS-003 Navigation System — Pending
- ⏳ EDS-004 App Shell — Pending
- ⏳ EDS-005 Theme & Design Tokens — Pending

## Next Step

EDS-002 should define:

- The complete navigation tree for every product
- User personas (CEO, Branch Manager, HR, Teller, Auditor, Collections Officer, etc.)
- Workspace hierarchy
- Cross-module navigation
- Global search behavior
- Menu permissions by role

This information architecture becomes the blueprint for every ARTH.OS screen before implementation begins.
