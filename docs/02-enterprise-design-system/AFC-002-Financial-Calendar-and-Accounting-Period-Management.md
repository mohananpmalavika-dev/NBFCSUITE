# AFC-002 — Financial Calendar & Accounting Period Management (FCPM)

## Overview

Financial Calendar & Accounting Period Management controls when accounting is allowed. It governs financial years, accounting periods, posting windows, business days, close procedures, holidays, and regulatory calendars across the enterprise.

This module is the financial heartbeat of ARTH.OS. Without it, posting engines, ledgers, and reporting cannot operate safely or consistently.

---

## Vision

A financial calendar is much more than a financial year. It controls:

- financial year
- accounting periods
- EOD (End of Day)
- EOM (End of Month)
- EOQ (End of Quarter)
- EOHY (Half Year)
- EOY (End of Year)
- holiday calendar
- posting windows
- regulatory calendar
- branch calendar
- treasury calendar
- forex calendar

---

## Architecture

```text
Enterprise Calendar
│
├── Legal Entity Calendar
├── Business Unit Calendar
├── Branch Calendar
├── Accounting Period
├── Posting Window
└── Financial Close
```

---

## Calendar Hierarchy

```text
Enterprise
↓
Financial Year
↓
Quarter
↓
Month
↓
Week
↓
Business Day
↓
Business Session
```

---

## Financial Year

Supports:

- calendar year
- fiscal year
- custom year
- multi-year

Examples:

```text
2026-2027
01-Apr-2026 → 31-Mar-2027
```

or

```text
01-Jan-2026 → 31-Dec-2026
```

---

## Accounting Period

Period states:

```text
Future
↓
Open
↓
Soft Close
↓
Hard Close
↓
Archived
```

---

## Posting Windows

Example:

```text
Accounting Date: 01-Apr
Posting Allowed: 01-Apr to 05-May
```

Late adjustments should be configurable.

---

## Multi Calendar Support

Different calendars can coexist:

```text
Corporate
Treasury
Forex
Payroll
Tax
Audit
```

Each calendar can have independent schedules.

---

## Dashboard

### KPIs

- Current Financial Year
- Open Periods
- Closed Periods
- Pending EOD
- Pending EOM
- Pending EOY
- Late Journals
- Calendar Exceptions

### Charts

- period status
- close progress
- posting activity
- calendar exceptions
- closing SLA

---

## Workspace

```text
Dashboard
↓
Financial Years
↓
Accounting Periods
↓
Business Calendar
↓
Holiday Calendar
↓
Closing Monitor
↓
Reports
```

---

## Financial Year Profile

### Tabs

- Overview
- Periods
- Closing
- Audit
- Workflow
- Documents
- Timeline
- AI

---

## Create Financial Year Wizard

### Step 1 — General

Fields:

- Year Code
- Description
- Start Date
- End Date
- Calendar Type

### Step 2 — Periods

Generate:

```text
12 Months
↓
4 Quarters
↓
52 Weeks
↓
Business Days
```

### Step 3 — Calendars

Assign calendars such as:

```text
Corporate
Payroll
Treasury
Forex
Tax
```

### Step 4 — Close Schedule

Configure:

- daily close
- month close
- quarter close
- year close

### Step 5 — Review

- review summary
- approval
- activate

---

## Business Day

Each day should have a lifecycle:

```text
Open
↓
Transactions
↓
Validation
↓
EOD
↓
Closed
```

---

## End of Day (EOD)

Every branch executes a close sequence such as:

```text
Cash Verification
↓
Vault Verification
↓
Pending Transactions
↓
Interest Accrual
↓
Accounting Posting
↓
Reconciliation
↓
Close Branch
```

---

## End of Month (EOM)

```text
Interest Accrual
↓
Depreciation
↓
Payroll Accrual
↓
Provisioning
↓
Revaluation
↓
GL Reconciliation
↓
Trial Balance
↓
Close Month
```

---

## End of Quarter (EOQ)

```text
Financial Review
↓
Tax Review
↓
Budget Review
↓
Compliance
↓
Quarter Close
```

---

## End of Year (EOY)

```text
Close Journals
↓
Final Trial Balance
↓
Profit Transfer
↓
Opening Balance
↓
New Financial Year
↓
Archive
```

---

## Holiday Calendar

Supports:

- national holidays
- state holidays
- branch holidays
- optional holidays
- weekend rules

---

## Treasury Calendar

Supports:

```text
Settlement Holidays
Market Holidays
Bank Holidays
Currency Holidays
```

---

## Forex Calendar

Supports:

- currency holidays
- market sessions
- trading hours
- settlement dates

---

## Tax Calendar

Tracks:

```text
GST
TDS
TCS
Income Tax
RBI Returns
ROC Returns
```

---

## Close Checklist

Example:

```text
Cash Verified ✓
Interest Posted ✓
GL Balanced ✓
Branch Closed ✓
Pending Approvals 0
```

---

## Close Workflow

```text
Initiate
↓
Operations
↓
Finance
↓
Compliance
↓
Approval
↓
Close
```

---

## Reopen Workflow

Requires:

```text
Request
↓
Finance
↓
CFO
↓
Approval
↓
Reopen
```

Every reopen should be audited.

---

## AI Features

Examples:

```text
Predict delayed close
↓
Detect unposted transactions
↓
Recommend close order
↓
Identify bottlenecks
↓
Forecast EOY issues
↓
Detect unusual posting patterns
↓
Estimate close completion time
```

---

## Reports

Standard reports:

- Financial Calendar
- Period Status
- Close Report
- Reopen Report
- Holiday Calendar
- Posting Window
- Close SLA
- EOD Summary
- EOM Summary
- EOY Summary

---

## Calendar Health Score

Calculated using:

- close timeliness
- reopen frequency
- posting exceptions
- unposted journals
- SLA compliance
- audit observations

Example:

```text
Calendar Health: 99% ★★★★★
```

---

## Database Tables

```text
financial_year
financial_period
business_day
holiday_calendar
posting_window
calendar_exception
period_close
close_checklist
close_workflow
reopen_request
calendar_ai
calendar_audit
```

---

## APIs

```text
GET    /api/v1/accounting/calendar/years
POST   /api/v1/accounting/calendar/years
GET    /api/v1/accounting/calendar/periods
POST   /api/v1/accounting/calendar/periods/{id}/open
POST   /api/v1/accounting/calendar/periods/{id}/soft-close
POST   /api/v1/accounting/calendar/periods/{id}/hard-close
POST   /api/v1/accounting/calendar/periods/{id}/reopen
GET    /api/v1/accounting/calendar/eod
POST   /api/v1/accounting/calendar/eod/execute
POST   /api/v1/accounting/calendar/eom/execute
POST   /api/v1/accounting/calendar/eoy/execute
```

---

## Events

```text
FINANCIAL_YEAR_CREATED
PERIOD_OPENED
PERIOD_SOFT_CLOSED
PERIOD_HARD_CLOSED
EOD_COMPLETED
EOM_COMPLETED
EOQ_COMPLETED
EOY_COMPLETED
PERIOD_REOPENED
CALENDAR_EXCEPTION_RAISED
```

---

## Backend Structure

```text
services/accounting/financial-calendar/
├── domain/
├── application/
├── infrastructure/
├── api/
├── close-engine/
├── workflow/
├── analytics/
├── ai/
└── tests/
```

---

## Frontend Structure

```text
modules/accounting/financial-calendar/
├── dashboard/
├── financial-years/
├── periods/
├── close-monitor/
├── holidays/
├── reports/
├── settings/
└── components/
```

---

## Integration Matrix

- General Ledger: period validation
- Journal Engine: posting window validation
- Accounts Payable: invoice posting
- Accounts Receivable: receipt posting
- Lending: interest accrual and EOD
- Deposits: interest accrual and maturity
- Gold Loan: daily valuation and interest
- Treasury: settlement calendar
- Payroll: payroll periods
- Tax Engine: return schedules
- Fixed Assets: depreciation runs
- Workflow: period close approvals

---

## Financial Calendar 360

Each financial year and period should provide an operational view.

### Calendar View

- financial year
- current period
- open / closed status
- business day status

### Operational View

- EOD progress
- EOM progress
- pending close activities
- outstanding validations

### Financial View

- journals posted
- trial balance status
- GL balancing
- reconciliation completion

### Compliance View

- regulatory deadlines
- tax filings
- audit checkpoints
- policy exceptions

### AI View

- close readiness score
- delay prediction
- unposted transaction alerts
- recommended corrective actions

---

## Definition of Done

The Financial Calendar module is complete when it supports:

- multi-calendar architecture
- multi-company fiscal years
- configurable accounting periods
- posting windows
- EOD / EOM / EOQ / EOY orchestration
- holiday management
- reopen workflows
- close checklists
- audit trail
- AI-assisted close management

---

## Enterprise Recommendation

Do not treat EOD, EOM, and EOY as simple scheduled jobs. Build a Financial Close Orchestration Engine.

Every close process should be composed of configurable tasks such as:

```text
Start Close
↓
Validate Pending Transactions
↓
Post Accounting Events
↓
Generate Journals
↓
Run Reconciliations
↓
Calculate Interest and Provisions
↓
Execute Depreciation
↓
Generate Trial Balance
↓
Perform Validation Rules
↓
Collect Approvals
↓
Lock Period
↓
Publish Close Certificate
```

This allows different legal entities, products, or countries to have different close procedures without code changes.

---

## Recommended Next Module

The next module should be AFC-003 — Enterprise Accounting Event Engine, which converts every business action into standardized accounting events that flow through posting rules and journals into the general ledger.
