# AFC-003 — Enterprise Accounting Event Engine (AEE)

## Overview

The Accounting Event Engine is the brain of the enterprise accounting system. It transforms business transactions from loans, deposits, gold loans, treasury, forex, HRMS, procurement, assets, and other modules into standardized accounting events that can be validated, queued, replayed, and posted through the accounting pipeline.

This is the architectural layer that separates a world-class core banking or NBFC ERP from a traditional accounting package.

---

## Vision

Every business transaction should become a standardized accounting event.

Example:

```text
Loan Disbursement
↓
Accounting Event
↓
Posting Rule Engine
↓
Journal Engine
↓
General Ledger
```

Business modules should know nothing about debit and credit entries.

---

## Architecture

```text
Business Modules
├── Loan
├── Deposit
├── Gold Loan
├── Forex
├── Treasury
├── HRMS
├── Procurement
├── Assets
└── CRM
↓
Accounting Event Engine
↓
Validation Engine
↓
Posting Rule Engine
↓
Journal Engine
↓
General Ledger
```

---

## Event Categories

### Customer

```text
Customer Created
Customer Updated
Customer Closed
```

### Loan

```text
Loan Applied
Loan Approved
Loan Disbursed
EMI Due
EMI Paid
Interest Accrued
Penalty Charged
Loan Closed
Loan Written Off
Loan Recovered
```

### Gold Loan

```text
Gold Received
Gold Appraised
Gold Loan Released
Interest Posted
Auction Initiated
Auction Completed
Surplus Returned
```

### Deposit

```text
FD Opened
Interest Accrued
Interest Paid
FD Matured
FD Closed
```

### Treasury

```text
Investment Purchased
Investment Sold
Interest Earned
MTM Revaluation
```

### Forex

```text
Currency Purchased
Currency Sold
Revaluation
Settlement
```

### HR

```text
Salary Processed
Salary Paid
PF Posted
ESI Posted
Gratuity Posted
```

### Procurement

```text
Purchase Order Approved
Goods Received
Invoice Received
Payment Released
```

### Assets

```text
Asset Purchased
Depreciation Posted
Asset Sold
Asset Scrapped
```

---

## Event Lifecycle

```text
Created
↓
Validated
↓
Approved
↓
Queued
↓
Posted
↓
Completed
↓
Archived
```

---

## Event Dashboard

### KPIs

- Today’s Events
- Pending
- Failed
- Posted
- Average Processing Time
- Retry Queue
- Dead Letter Queue

### Charts

- events by module
- success rate
- processing time
- failure analysis

---

## Workspace

```text
Dashboard
↓
Event Explorer
↓
Queue Monitor
↓
Validation
↓
Retry Queue
↓
Dead Letter Queue
↓
Reports
```

---

## Event Explorer

Columns:

- Event ID
- Event Type
- Module
- Reference Number
- Status
- Priority
- Created By
- Created Time

Features:

- search
- filters
- replay
- retry
- cancel

---

## Event Payload

Every event should contain a structured payload such as:

```json
{
  "eventId": "...",
  "eventType": "LOAN_DISBURSED",
  "sourceModule": "Loan",
  "referenceId": "...",
  "businessDate": "...",
  "currency": "INR",
  "amount": 250000,
  "dimensions": {},
  "metadata": {}
}
```

---

## Universal Dimensions

Every event should carry dimensions such as:

```text
Enterprise
Legal Entity
Business Unit
Branch
Department
Cost Center
Profit Center
Customer
Product
Currency
Employee
Channel
```

These dimensions should be inherited automatically.

---

## Validation Engine

Checks:

- mandatory fields
- business rules
- accounting period
- currency
- dimensions
- reference integrity
- duplicate detection

---

## Event Queue

Supports:

```text
Priority Queue
Normal Queue
Retry Queue
Dead Letter Queue
```

---

## Retry Engine

Automatically retries events using backoff intervals such as:

```text
1 minute
5 minutes
15 minutes
30 minutes
Manual review
```

---

## Dead Letter Queue

Failed events are routed here for manual review.

Example:

```text
Loan Disbursed
↓
Posting Rule Missing
↓
Dead Letter Queue
↓
Finance Fixes Rule
↓
Replay Event
↓
Success
```

---

## Event Replay

Supports:

```text
Single event
Batch
Date range
Module
Customer
```

No manual journal should be required.

---

## Event Versioning

Supports:

```text
Version 1
↓
Version 2
↓
Version 3
```

Versioning should be backward compatible.

---

## AI Features

Examples:

```text
Predict failed events
↓
Detect duplicate postings
↓
Suggest posting rules
↓
Recommend retries
↓
Find unusual event patterns
↓
Forecast event volume
```

---

## Event Monitoring

Displays:

```text
Queue Size
Average Latency
Throughput
Success %
Error %
Retry Count
```

Monitoring should be real-time.

---

## Reports

Standard reports:

- Event Register
- Event Failures
- Retry Report
- Dead Letter Queue
- Throughput Report
- Processing Time
- Module-wise Events
- AI Prediction Report

---

## Event Health Score

Calculated using:

- success rate
- retry percentage
- queue latency
- validation errors
- processing speed
- replay success

Example:

```text
Health: 99% ★★★★★
```

---

## Database Tables

```text
accounting_event
event_payload
event_validation
event_queue
retry_queue
dead_letter_queue
event_version
event_dimension
event_status_history
event_ai
event_audit
```

---

## APIs

```text
POST   /api/v1/accounting/events
GET    /api/v1/accounting/events
GET    /api/v1/accounting/events/{id}
POST   /api/v1/accounting/events/{id}/validate
POST   /api/v1/accounting/events/{id}/retry
POST   /api/v1/accounting/events/{id}/replay
GET    /api/v1/accounting/events/queue
GET    /api/v1/accounting/events/dashboard
```

---

## Events

```text
ACCOUNTING_EVENT_CREATED
ACCOUNTING_EVENT_VALIDATED
ACCOUNTING_EVENT_QUEUED
ACCOUNTING_EVENT_POSTED
ACCOUNTING_EVENT_FAILED
ACCOUNTING_EVENT_RETRIED
ACCOUNTING_EVENT_REPLAYED
ACCOUNTING_EVENT_ARCHIVED
```

---

## Backend Structure

```text
services/accounting/event-engine/
├── domain/
├── application/
├── infrastructure/
├── api/
├── validation/
├── queue/
├── replay/
├── monitoring/
├── analytics/
├── ai/
└── tests/
```

---

## Frontend Structure

```text
modules/accounting/event-engine/
├── dashboard/
├── explorer/
├── queue/
├── retries/
├── dead-letter/
├── monitoring/
├── reports/
├── settings/
└── components/
```

---

## Integration Matrix

- Customer: customer lifecycle events
- Lending: loan lifecycle events
- Deposits: deposit lifecycle events
- Gold Loan: gold lifecycle events
- Treasury: investment lifecycle events
- Forex: FX lifecycle events
- HRMS: payroll events
- Procurement: purchasing events
- Assets: asset lifecycle events
- CRM: fee and service events

---

## Accounting Event 360

Every accounting event should provide a complete operational view.

### Business View

- source module
- business transaction
- customer
- product

### Processing View

- validation status
- queue status
- retry history
- processing time

### Financial View

- posting rule selected
- journal generated
- GL impact
- financial period

### Audit View

- creator
- approver
- workflow
- replay history

### AI View

- failure prediction
- duplicate risk
- posting recommendation
- processing anomaly

---

## Definition of Done

The Accounting Event Engine is complete when it supports:

- universal accounting event model
- validation engine
- event queues
- retry and replay
- dead letter queue
- versioned event schema
- multi-dimensional context
- real-time monitoring
- AI-assisted diagnostics
- immutable audit trail

---

## Critical Enterprise Recommendation

Introduce an Enterprise Event Bus so that business modules do not call posting logic directly.

```text
Loan Module
↓
Deposit Module
↓
Gold Loan Module
↓
Treasury Module
↓
HRMS Module
↓
Enterprise Event Bus
↓
Accounting Event Engine
↓
Posting Rule Engine
↓
Journal Engine
↓
General Ledger
```

This provides:

- loose coupling
- scalability
- reliability
- extensibility
- future integration with partners and external systems

---

## Recommended Next Module

The next package should be AFC-004 — Enterprise Posting Rule Engine (PRE), which configures how each accounting event is translated into balanced debit and credit journal entries.
