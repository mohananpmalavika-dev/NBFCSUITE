# EDS-007 — Enterprise Dashboard Framework

## Overview

ARTH.OS dashboards are the operational control center for the enterprise financial platform. They are designed to help users answer three questions in seconds:

1. What is happening now?
2. What needs my attention?
3. What should I do next?

A dashboard is not a report. It is a decision surface that supports monitoring, understanding, action, and follow-through.

---

## Design Philosophy

Every dashboard follows the same flow:

Monitor → Understand → Decide → Act

This creates a consistent experience across executive, operations, risk, lending, treasury, accounting, HR, and customer-facing workspaces.

### Core Principles

- Lead with status, not with tables or forms.
- Surface actionable information only.
- Keep the emotional load low by prioritizing urgency and relevance.
- Support role-based relevance without fragmenting the core experience.
- Provide a consistent navigation and drill-down model for every widget.

---

## Dashboard Architecture

Every dashboard shares the same high-level structure:

Workspace Header → Business KPIs → Alerts → Quick Actions → Business Charts → Tasks → Pending Approvals → Recent Activities → AI Insights

### Intent

This structure ensures a predictable pattern for every persona:

- Executive users see strategic health and critical risks.
- Operations users see workflow bottlenecks and pending work.
- Managers see team performance and action queues.
- Analysts see visualized business trends and emerging concerns.

---

## Layout and Grid System

The framework uses a responsive 12-column grid.

- Desktop: 12 columns
- Tablet: 8 columns
- Mobile: 4 columns

### Layout Rules

- Widgets snap to the grid.
- Widgets can resize and reorder cleanly.
- Dashboards should remain legible without requiring horizontal scrolling.
- The primary viewport should prioritize the most important business signals first.

---

## Widget Categories

### 1. KPI Widgets

KPI widgets expose the most important business metrics in a compact visual format.

Typical examples:

- Total Customers
- Loan Portfolio
- Deposits
- Collections
- Revenue
- Profit
- Employees
- Attendance

Each KPI widget should include:

- Current value
- Trend vs previous period
- Percentage change
- Drill-down path

### 2. Alert Widgets

Alert widgets display only actionable items.

Examples:

- NPA increased
- Cash limit exceeded
- KYC expiring
- Payroll pending
- Gold auction scheduled

These widgets should avoid informational noise and focus on what demands action.

### 3. Quick Actions

Quick actions provide role-specific shortcuts.

Examples:

- HR: New Employee, Approve Leave, Run Payroll, Attendance
- Accounting: Create Journal, Post Voucher, Close Day, Trial Balance

### 4. Charts

Charts should visualize business performance and operational state.

Recommended chart types:

- Line chart for monthly trend
- Bar chart for branch comparison
- Donut chart for portfolio mix
- Area chart for daily activity
- Waterfall chart for cash flow
- Heatmap for collections intensity
- Map for regional distributions

Rules:

- Max 6 charts per dashboard
- Every chart supports drill-down
- Charts should support both summary and detailed views

### 5. Task Center

Task widgets group work by urgency.

Suggested states:

- Overdue
- Today
- This Week
- Completed

Each task should show:

- Priority
- Due date
- Owner
- Related entity

### 6. Approval Center

Approval widgets surface pending decisions.

Examples:

- Loan Approval
- Leave Approval
- Journal Approval
- Expense Approval
- Branch Approval

Each card should include:

- Request summary
- SLA timer
- Approve / Reject / View actions

### 7. Activity Feed

Activity feeds show recent business and system events.

Examples:

- Loan approved
- Voucher posted
- Employee joined
- Alert acknowledged

### 8. AI Insights

AI insights should explain why something happened, not just describe what changed.

Examples:

- Branch collections are down 8% due to delayed payment behavior in one region.
- Payroll cost increased 6% because of revised headcount and overtime.
- Gold loan renewals are likely next week based on maturity patterns.

---

## Widget Library

The dashboard framework should support a reusable library of widgets:

- KPI Widget
- Chart Widget
- Task Widget
- Approval Widget
- Alert Widget
- Activity Widget
- Calendar Widget
- Performance Widget
- Map Widget
- AI Summary Widget
- Risk Widget
- Forecast Widget
- Leaderboard Widget
- Goal Widget
- Announcement Widget

This ensures the platform can compose dashboards without bespoke UI patterns for each module.

---

## Dashboard Types

### Executive Dashboard

Audience:

- CEO
- MD
- CFO

Primary KPIs:

- Revenue
- Profit
- Loan Book
- Deposits
- NPA
- Cash Position
- Customer Growth

Typical charts:

- Revenue trend
- Branch ranking
- Portfolio mix

### Branch Dashboard

Audience:

- Branch Manager

Primary KPIs:

- Customers today
- Loans
- Collections
- Cash balance
- Pending approvals

Quick actions:

- Open account
- Create loan
- Receive payment

### HR Dashboard

Primary KPIs:

- Employees
- Attendance
- Leave
- Recruitment
- Payroll

Typical charts:

- Headcount trend
- Attrition
- Attendance

### Accounting Dashboard

Primary KPIs:

- Cash
- Bank
- GL balance
- Receivables
- Payables

Typical charts:

- Cash flow
- Expense analysis
- Budget vs Actual

### Lending Dashboard

Primary KPIs:

- Applications
- Approvals
- Disbursements
- Collections
- NPA

Typical charts:

- Approval funnel
- Collection trend
- Branch comparison

### Customer Dashboard

Primary KPIs:

- New customers
- Active customers
- Dormant customers
- KYC pending

Typical charts:

- Customer growth
- Segment mix

### Treasury Dashboard

Primary KPIs:

- Cash
- Vault
- Liquidity
- Forex
- Investments

Typical charts:

- Liquidity trend
- Cash forecast

### Risk Dashboard

Primary KPIs:

- AML alerts
- Fraud alerts
- Compliance exceptions
- Audit findings

Typical charts:

- Risk heatmap
- Incident trend

---

## Personalization and Configuration

Dashboards should be configurable by user and by role.

Users can:

- Move widgets
- Resize widgets
- Hide widgets
- Save layouts
- Create multiple dashboard layouts

Examples:

- Collections workspace
- Accounting workspace

Users can also:

- Pin favorite widgets
- Set a default dashboard
- Save filters
- Choose chart type
- Configure refresh interval

Administrators may publish organization-wide dashboards for standard operating views.

---

## Refresh Strategy

Refresh behavior should be tuned by widget type.

- KPI widgets: 30–60 seconds
- Charts: 1–5 minutes
- Tasks: 30 seconds
- Approvals: 30 seconds
- Reports: on demand

Manual refresh should be supported at all times.

---

## Performance Targets

The dashboard framework should meet the following targets:

- Initial load: under 2 seconds
- Widget load: under 500 ms
- Dashboard refresh: under 1 second for cached metrics
- Lazy-load widgets below the fold

---

## Dashboard Events

The framework should emit standard events for analytics and usage reporting.

Examples:

- DASHBOARD_OPENED
- WIDGET_OPENED
- WIDGET_MOVED
- FILTER_APPLIED
- REFRESH_REQUESTED
- AI_INSIGHT_OPENED
- DRILLDOWN_OPENED

---

## Folder Structure

A reference implementation should follow this structure:

packages/design-system/dashboard/
├── DashboardLayout/
├── DashboardGrid/
├── WidgetContainer/
├── KPIWidget/
├── ChartWidget/
├── AlertWidget/
├── TaskWidget/
├── ApprovalWidget/
├── ActivityWidget/
├── AISummaryWidget/
├── hooks/
├── types/
└── utils/

---

## Widget API Contract

Each widget should implement a common contract so the framework can register new widgets without introducing bespoke wiring.

Recommended fields:

- Widget ID
- Title
- Description
- Icon
- Category
- Permissions
- Data source
- Refresh policy
- Drill-down target
- Export support
- Supported sizes

---

## Acceptance Criteria

The dashboard framework is complete when:

- All dashboards share the same core layout
- Widgets are reusable and configurable
- Role-based dashboards are supported
- Users can personalize layouts
- Every widget supports loading, empty, and error states
- Drill-down navigation is consistent
- Performance targets are met

---

## Deliverable Status

- EDS-001 Design Principles: Complete
- EDS-002 Information Architecture: Complete
- EDS-003 Enterprise Navigation: Complete
- EDS-004 Enterprise App Shell: Complete
- EDS-005 Design Tokens: Complete
- EDS-006 Component Library: Complete
- EDS-007 Enterprise Dashboard Framework: Complete
- EDS-008 Enterprise Data Grid Framework: Next

---

## Recommendation

The next deliverable should be EDS-008 — Enterprise Data Grid Framework. In an enterprise financial platform, the data grid is one of the most heavily used interfaces. A single, powerful grid framework will provide consistent filtering, saved views, bulk actions, inline editing, exports, virtualization, and audit-awareness across every ARTH.OS module.
