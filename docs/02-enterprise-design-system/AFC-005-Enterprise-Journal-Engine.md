# AFC-005 — Enterprise Journal Engine (EJE)

## Overview

The Journal Engine is the execution layer of the enterprise accounting core. It transforms validated posting rules into immutable, balanced accounting journals that can be approved, posted, reversed, and audited with complete traceability.

This module is one of the fastest and most critical services in ARTH.OS because every financial transaction passes through it. It must be designed for reliability, traceability, and enterprise-scale throughput.

---

## Vision

The Journal Engine is responsible for converting validated accounting intent into financial reality.

It must guarantee:

- Balanced entries
- Atomic posting
- Idempotent processing
- Complete auditability
- High throughput
- Regulatory compliance

The architecture should ensure that the posting rule decides what should happen, while the journal engine executes it safely and consistently.

---

## Enterprise Architecture

```text
Business Modules
↓
Accounting Event Engine
↓
Posting Rule Engine
↓
Journal Engine
↓
General Ledger
↓
Trial Balance
↓
Financial Statements
```

---

## Journal Lifecycle

```text
Accounting Event
↓
Posting Rule
↓
Journal Draft
↓
Validation
↓
Approval
↓
Posting
↓
General Ledger
↓
Archive
```

---

## Journal Types

The engine must support:

- Standard Journal
- Manual Journal
- Automatic Journal
- Recurring Journal
- Accrual Journal
- Reversal Journal
- Adjustment Journal
- Allocation Journal
- Intercompany Journal
- Foreign Currency Journal
- Opening Balance Journal
- Closing Journal
- Consolidation Journal
- Correction Journal

Each type should be configurable and traceable through a common workflow.

---

## Journal Dashboard

### KPIs

- Today’s Journals
- Posted
- Draft
- Pending Approval
- Rejected
- Reversed
- Recurring
- Failed
- Processing Time
- Journal Health

### Charts

- Journals by Type
- Posting Volume
- Approval Status
- Module Distribution
- Daily Throughput

---

## Workspace

```text
Dashboard
↓
Journal Explorer
↓
Draft Journals
↓
Approval Queue
↓
Recurring Journals
↓
Reversals
↓
Reports
```

---

## Journal Explorer

### Columns

- Journal Number
- Business Event
- Journal Type
- Branch
- Amount
- Currency
- Status
- Created By
- Posting Date

### Supports

- Search
- Filters
- Drill-down
- Export
- Clone
- Reverse
- Print

---

## Journal 360

Every journal should expose a complete operational view through a digital journal twin.

### Tabs

- Overview
- Header
- Lines
- Source Transaction
- Approvals
- Dimensions
- Attachments
- Timeline
- Audit
- AI

---

## Journal Header

Each journal header must contain:

- Journal Number
- Business Event
- Reference Number
- Posting Date
- Accounting Date
- Branch
- Currency
- Legal Entity
- Business Unit
- Description
- Status

---

## Journal Lines

Each journal line must contain:

- GL Account
- Debit
- Credit
- Currency
- Exchange Rate
- Branch
- Department
- Cost Center
- Profit Center
- Project
- Customer
- Vendor
- Employee
- Product

The engine should support unlimited dimensional analysis and extensible accounting dimensions.

---

## Example Journal

### Scenario

Loan disbursement of ₹5,00,000

### Journal Entry

- Debit: Loan Principal Outstanding — ₹5,00,000
- Credit: Branch Cash — ₹5,00,000

### Status

- Balanced
- Posted

---

## Journal Validation

The engine must enforce all validation checks before posting. No validation may be skipped.

### Checks

- Debit = Credit
- Period Open
- GL Active
- Dimensions Valid
- Currency Valid
- Posting Rules Valid
- Budget Validation
- Fraud Rules

### Validation Rules

- Validation must be deterministic and repeatable
- Validation outcomes should be visible at the line level
- Failed journals must be quarantined and explainable
- Re-validation must be possible after corrections

---

## Journal Numbering

Journal numbers must be configurable and support enterprise numbering standards.

### Example

```text
JV2026Branch001000001
```

### Output

```text
JV-2026-B001-000001
```

### Requirements

- Configurable prefix and suffix
- Branch-based sequence support
- Entity-based sequence support
- High-volume concurrency-safe numbering
- Restart-safe numbering

---

## Approval Workflow

```text
Draft
↓
Finance Officer
↓
Finance Manager
↓
Financial Controller
↓
CFO
↓
Posted
```

### Approval Rules

- Threshold-based approvals
- Role-based approvers
- Delegation support
- Escalation for delays
- Parallel or sequential approvals

---

## Maker–Checker

Mandatory for:

- Manual Journals
- Adjustments
- Write-offs
- High-value Entries
- Inter-company Journals

This should be enforced as a policy layer and not as an optional workflow.

---

## Multi-Currency Support

Every journal must support:

- Transaction Currency
- Functional Currency
- Reporting Currency

### Requirements

- Automatic FX calculations
- FX rate versioning
- Rate approval workflow
- Currency rounding policy
- Multi-book reporting support

---

## Recurring Journals

The engine should support recurring journals for predictable financial activity.

### Examples

- Rent
- Monthly Salary Provision
- Insurance
- Quarterly Accruals

### Scheduler Features

- Daily, weekly, monthly, quarterly schedules
- Holiday-aware scheduling
- Preview before generation
- Automatic reversal support
- Retry on generation failure

---

## Reversal Journals

The engine must support:

- Automatic reversal
- Manual reversal
- Scheduled reversal
- Partial reversal
- Full reversal

### Example

- Interest Accrual on 31 March
- Auto reverse on 1 April

---

## Intercompany Journals

The engine should support intercompany transactions with automatic balancing across legal entities.

### Example

```text
Company A
↓
Receivable
↓
Company B
↓
Payable
```

### Requirements

- Cross-entity balancing
- Settlement tracking
- Elimination support
- Approval rules for cross-company entries

---

## Journal Attachments

Journals should support:

- PDF
- Excel
- Images
- Contracts
- Loan Documents
- Invoices
- Audit Evidence

Attachments should integrate with the EDMS platform for versioning, retention, and search.

---

## Journal Timeline

The journal timeline should expose the complete state progression:

```text
Created
↓
Validated
↓
Approved
↓
Posted
↓
Reconciled
↓
Closed
```

---

## AI Features

The engine should include AI capabilities such as:

- Detect duplicate journals
- Suggest corrections
- Explain posting logic in plain language
- Detect fraud or unusual patterns
- Recommend approval routing
- Find unusual patterns
- Predict posting failures

AI should support finance users without replacing the control layer.

---

## Journal Search

The search experience should support natural language and traditional filters.

### Search by

- Journal Number
- Customer
- Loan
- Branch
- GL Account
- Amount
- Reference
- Voucher
- Narration

### Example Queries

- Show journals above ₹10 Lakhs
- Show Gold Loan journals yesterday
- Find reversed payroll journals

---

## Reports

### Standard Reports

- Journal Register
- Posted Journals
- Pending Journals
- Reversal Register
- Adjustment Register
- Intercompany Register
- Currency Register
- Approval Register
- Journal Aging
- Journal Health

---

## Journal Health Score

Journal health should be calculated using:

- Validation errors
- Reversal percentage
- Approval delays
- Duplicate risk
- Processing latency
- Audit exceptions

### Example

```text
Journal Health: 99% ★★★★★
```

---

## Database Tables

The module should be backed by a strong transactional model with tables such as:

- journal_header
- journal_line
- journal_dimension
- journal_attachment
- journal_approval
- journal_reversal
- journal_recurring
- journal_batch
- journal_sequence
- journal_audit
- journal_ai
- journal_status_history
- journal_lock

---

## APIs

### Core APIs

- POST /api/v1/accounting/journals
- GET /api/v1/accounting/journals
- GET /api/v1/accounting/journals/{id}
- PUT /api/v1/accounting/journals/{id}
- POST /api/v1/accounting/journals/{id}/approve
- POST /api/v1/accounting/journals/{id}/post
- POST /api/v1/accounting/journals/{id}/reverse
- GET /api/v1/accounting/journals/search
- GET /api/v1/accounting/journals/dashboard

---

## Events

The engine should emit enterprise events such as:

- JOURNAL_CREATED
- JOURNAL_VALIDATED
- JOURNAL_APPROVED
- JOURNAL_POSTED
- JOURNAL_REVERSED
- JOURNAL_RECURRING_GENERATED
- JOURNAL_FAILED
- JOURNAL_ARCHIVED

---

## Backend Structure

```text
services/accounting/journal-engine/
├── domain/
├── application/
├── infrastructure/
├── api/
├── validation/
├── numbering/
├── approvals/
├── recurring/
├── reversals/
├── analytics/
├── ai/
└── tests/
```

---

## Frontend Structure

```text
modules/accounting/journal-engine/
├── dashboard/
├── explorer/
├── create/
├── approvals/
├── recurring/
├── reversals/
├── reports/
├── settings/
└── components/
```

---

## Integration Matrix

| Module | Journal Usage |
| --- | --- |
| Accounting Event Engine | Creates journal requests |
| Posting Rule Engine | Supplies debit and credit lines |
| General Ledger | Receives posted journals |
| Budget Control | Budget validation |
| Tax Engine | Tax journal creation |
| Treasury | FX journals |
| Loans | Disbursement and repayment journals |
| Deposits | Interest and maturity journals |
| HRMS | Payroll journals |
| Fixed Assets | Depreciation journals |

---

## Journal 360 — Digital Journal Twin

Every journal should expose a complete operational view.

### Business View

- Source transaction
- Customer
- Product
- Business event

### Accounting View

- Journal header
- Journal lines
- Posting rules
- GL accounts

### Financial View

- Currency
- Exchange rate
- Financial impact
- Budget impact

### Compliance View

- Approvals
- Audit trail
- Attachments
- Regulatory references

### AI View

- Anomaly score
- Duplicate detection
- Fraud indicators
- Suggested corrections
- Plain-language explanation of the accounting

---

## Performance Targets

To support enterprise-scale NBFC operations:

- 5,000+ journal entries per minute sustained throughput
- Sub-200 ms average journal validation
- Horizontal scalability
- Idempotent posting with no duplicate journals on retries
- ACID transactions for financial integrity
- Immutable audit logs

---

## Definition of Done

The Journal Engine is complete when it supports:

- Automatic and manual journals
- Multi-line journals
- Multi-currency journals
- Recurring journals
- Reversals and adjustments
- Intercompany journals
- Approval workflows
- Maker-checker
- Attachment support
- Journal 360
- AI insights
- Immutable audit trail

---

## Enterprise Recommendation

Rather than making journals the source of truth, ARTH.OS should introduce an immutable financial ledger pattern.

### Recommended Architecture

```text
Business Event
↓
Accounting Event
↓
Posting Rule
↓
Journal (Business Representation)
↓
Immutable Ledger Entries
↓
General Ledger Views
↓
Financial Statements
```

This approach provides:

- Immutable financial history
- Easier forensic audits
- Stronger fraud resistance
- Event replay capability
- Reconstruction of financial state at any point in time
- Better support for future distributed and cloud-native architectures

---

## Next Module

The next package is AFC-006 — Enterprise General Ledger (GL).

This module will provide:

- Real-time ledger balances
- Multi-book accounting
- Multi-currency ledgers
- Parallel accounting
- Balance calculations
- Trial Balance generation
- Financial statement feeds
- Consolidation support
- Ledger partitioning for enterprise scale
- GL 360 drill-down to every originating transaction
