# AFC-004 — Enterprise Posting Rule Engine (PRE)

## Overview

The Posting Rule Engine is the accountant of the financial core. It translates accounting events into balanced debit and credit journal entries using configurable posting rules rather than hardcoded accounting logic.

This module makes ARTH.OS configurable. Finance teams—not developers—can define how each business event posts to the general ledger.

---

## Vision

Business modules should never contain debit and credit logic.

Instead:

```text
Business Event
↓
Accounting Event
↓
Posting Rule Engine
↓
Journal Engine
↓
General Ledger
```

A finance administrator can change accounting behavior without a code deployment.

---

## Architecture

```text
Loan Module
Deposit Module
Gold Loan
Forex
Treasury
HRMS
Assets
Procurement
↓
Accounting Event
↓
Rule Selection Engine
↓
Posting Rule
↓
Validation
↓
Journal Builder
↓
Journal Engine
```

---

## Rule Components

Every posting rule consists of:

```text
Rule Header
↓
Conditions
↓
Debit Lines
↓
Credit Lines
↓
Dimensions
↓
Taxes
↓
Validation
↓
Approval
↓
Version
```

---

## Example Rule

### Event

```text
LOAN_DISBURSED
```

### Rule

```text
Debit  : Loan Principal Outstanding
Credit : Branch Cash Account
```

### Amount

```text
Loan Amount
```

---

## Gold Loan Example

```text
GOLD_INTEREST_ACCRUED
```

Debit:

```text
Interest Receivable
```

Credit:

```text
Interest Income
```

---

## Deposit Example

```text
FD_INTEREST_PAID
```

Debit:

```text
Interest Expense
```

Credit:

```text
Customer Deposit
```

---

## Rule Hierarchy

```text
Enterprise
↓
Legal Entity
↓
Business Unit
↓
Product
↓
Branch
↓
Rule
```

The engine should support inheritance and overrides.

---

## Rule Dashboard

### KPIs

- Posting Rules
- Active Rules
- Draft Rules
- Failed Rules
- Average Execution Time
- Rule Coverage
- Unused Rules
- AI Recommendations

### Charts

- rules by product
- execution frequency
- rule success rate
- rule changes
- rule performance

---

## Workspace

```text
Dashboard
↓
Rule Explorer
↓
Rule Designer
↓
Rule Testing
↓
Simulation
↓
Versions
↓
Reports
```

---

## Rule Explorer

Columns:

- Rule Code
- Rule Name
- Accounting Event
- Product
- Version
- Status
- Priority
- Effective Date

Features:

- search
- filters
- clone
- export
- compare versions

---

## Rule Designer

### Tabs

- Overview
- Conditions
- Debit Entries
- Credit Entries
- Dimensions
- Taxes
- Validation
- Workflow
- Simulation
- Audit
- AI

---

## Create Rule Wizard

### Step 1 — General

Fields:

- Rule Code
- Rule Name
- Accounting Event
- Priority
- Status

### Step 2 — Conditions

Examples:

```text
Loan Product = Gold Loan
Branch Type = Urban
Currency = INR
Loan Amount > 5,00,000
Customer Type = Corporate
```

### Step 3 — Debit Builder

Fields:

- GL Account
- Amount Formula
- Currency
- Dimensions
- Description

Supports multiple debit lines.

### Step 4 — Credit Builder

Same structure as debit builder.

Supports multiple credit lines.

### Step 5 — Amount Expressions

Examples:

```text
Principal
Interest
Penalty
Tax
Principal + Interest
Interest * GST
Amount * Exchange Rate
```

An expression language should be supported.

### Step 6 — Dimensions

Automatically populate dimensions such as:

```text
Branch
Cost Center
Profit Center
Department
Customer
Employee
Project
Product
```

### Step 7 — Validation Rules

Examples:

```text
Debits = Credits
Currency Exists
GL Active
Accounting Period Open
Dimensions Complete
Customer Active
```

### Step 8 — Approval Workflow

```text
Finance Officer
↓
Finance Manager
↓
Controller
↓
CFO
↓
Publish
```

### Step 9 — Simulation

Test example:

```text
Loan: ₹10,00,000
Gold Loan
Branch 101
```

Expected journal:

```text
Account        Debit      Credit
Loan Principal 10,00,000
Branch Cash              10,00,000
```

### Step 10 — Review

- review summary
- publish

---

## Rule Execution Flow

```text
Accounting Event
↓
Rule Matching
↓
Conditions Evaluated
↓
Rule Selected
↓
Amount Calculated
↓
GL Accounts Resolved
↓
Validation
↓
Journal Generated
```

---

## Rule Versioning

Supports:

```text
Version 1
↓
Version 2
↓
Version 3
```

Historical journals should continue to reference the rule version that was used at posting time.

---

## Effective Dating

Each rule should support:

```text
Valid From
Valid To
```

Future-dated accounting policies should be possible.

---

## Rule Priorities

Example:

```text
Priority  Scope
1         Branch Override
2         Product
3         Business Unit
4         Enterprise Default
```

---

## Rule Simulation Lab

Supports:

- single transaction simulation
- batch simulation
- compare rule versions
- compare accounting impact
- multi-currency simulation

---

## AI Features

Examples:

```text
Recommend posting rule
↓
Detect conflicting rules
↓
Suggest GL mappings
↓
Detect duplicate rules
↓
Recommend simplification
↓
Predict rule failures
↓
Explain accounting impact
```

---

## Reports

Standard reports:

- Posting Rule Register
- Rule Coverage
- Unused Rules
- Rule Performance
- Version Comparison
- Simulation Report
- GL Mapping Report
- Rule Audit Report

---

## Rule Health Score

Calculated from:

- execution success
- validation failures
- duplicate rules
- simulation results
- audit observations

Example:

```text
Rule Health: 98% ★★★★★
```

---

## Database Tables

```text
posting_rule
posting_rule_version
posting_condition
posting_debit_line
posting_credit_line
posting_formula
posting_dimension
posting_validation
posting_simulation
posting_execution_log
posting_ai
posting_audit
```

---

## APIs

```text
GET    /api/v1/accounting/posting-rules
POST   /api/v1/accounting/posting-rules
GET    /api/v1/accounting/posting-rules/{id}
PUT    /api/v1/accounting/posting-rules/{id}
POST   /api/v1/accounting/posting-rules/{id}/simulate
POST   /api/v1/accounting/posting-rules/{id}/publish
GET    /api/v1/accounting/posting-rules/{id}/versions
GET    /api/v1/accounting/posting-rules/dashboard
```

---

## Events

```text
POSTING_RULE_CREATED
POSTING_RULE_UPDATED
POSTING_RULE_PUBLISHED
POSTING_RULE_RETIRED
POSTING_RULE_EXECUTED
POSTING_RULE_FAILED
POSTING_RULE_SIMULATED
POSTING_RULE_VERSION_CREATED
```

---

## Backend Structure

```text
services/accounting/posting-rule-engine/
├── domain/
├── application/
├── infrastructure/
├── api/
├── rule-engine/
├── formula-engine/
├── simulation/
├── analytics/
├── ai/
└── tests/
```

---

## Frontend Structure

```text
modules/accounting/posting-rules/
├── dashboard/
├── explorer/
├── designer/
├── simulation/
├── versions/
├── reports/
├── settings/
└── components/
```

---

## Integration Matrix

- Accounting Event Engine: supplies business events
- Chart of Accounts: resolves GL accounts
- Journal Engine: receives generated journal lines
- General Ledger: stores posted journals
- Tax Engine: calculates tax postings
- Multi-Currency: resolves exchange gains/losses
- Budget Control: validates budget before posting
- Workflow: handles rule approval lifecycle

---

## Posting Rule 360

Each posting rule should provide a complete view.

### Business View

- triggering events
- supported products
- effective dates

### Accounting View

- debit / credit mappings
- formula definitions
- validation rules

### Operations View

- execution frequency
- success / failure rate
- average processing time

### Governance View

- versions
- approval history
- change log
- impact analysis

### AI View

- rule optimization suggestions
- conflict detection
- missing scenario identification
- predicted accounting impact

---

## Definition of Done

The Posting Rule Engine is complete when it supports:

- event-driven posting rules
- configurable debit and credit builders
- formula-based amount calculations
- multi-level rule inheritance
- versioning and effective dating
- simulation and testing
- approval workflows
- AI-assisted recommendations
- full audit trail

---

## Critical Recommendation

Separate business events from accounting policies.

```text
Business Event
↓
Accounting Event
↓
Posting Rule
↓
Accounting Policy
↓
GL Resolver
↓
Journal Builder
```

This allows:

- one posting rule to support multiple accounting policies
- different legal entities to use different accounting books
- regulatory changes to become configuration changes
- easier international expansion

---

## Recommended Next Module

The next package should be AFC-005 — Enterprise Journal Engine, which will generate balanced journal entries from posting rules and feed the general ledger.
