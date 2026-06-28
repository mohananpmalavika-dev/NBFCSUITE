# AFC-001 — Enterprise Chart of Accounts (COA)

## Overview

The Chart of Accounts is the financial taxonomy of ARTH.OS. It is not merely a list of GL codes. It is the foundational map that connects every business transaction to accounting structure, reporting, compliance, and analytics.

This module is the foundation of the accounting engine and should be designed as a metadata-driven, hierarchical, dimension-aware accounting model.

---

## Vision

The Chart of Accounts should provide the enterprise backbone for:

- multi-company accounting
- multi-book accounting
- multi-currency accounting
- multi-GAAP support
- hierarchical account structures
- dimension-aware posting
- product-specific accounting
- regulatory reporting
- AI-assisted account mapping

---

## Financial Architecture

```text
Business Event
↓
Accounting Event
↓
Posting Rule
↓
Chart of Accounts
↓
Journal
↓
General Ledger
↓
Financial Statements
```

---

## COA Objectives

The COA should support:

- multi-company operations
- multi-book accounting
- multi-currency transactions
- Ind AS / IFRS / local GAAP
- hierarchical accounts
- dimension accounting
- product-specific accounting
- regulatory reporting
- AI-assisted account mapping

---

## COA Hierarchy

```text
Assets
├── Current Assets
│   ├── Cash
│   ├── Bank
│   ├── Loans
│   ├── Gold Loan Receivable
│   └── Interest Receivable
├── Fixed Assets
└── Other Assets

Liabilities
Equity
Income
Expenses
Memo Accounts
```

Hierarchy should be unlimited and configurable.

---

## Account Types

```text
Asset
Liability
Equity
Income
Expense
Contra Asset
Contra Liability
Statistical
Memo
Control
```

---

## Account Categories

Examples:

```text
Cash
Bank
Loan
Deposit
Gold Loan
Forex
Treasury
Investment
Payroll
Tax
Interest
Penalty
Fees
Commission
Depreciation
```

---

## GL Numbering Strategy

A recommended numbering pattern is:

```text
AAAA-BB-CCC-DD
```

Example:

```text
1000-01-101-01
```

Where:

```text
1000 = Assets
01   = Cash
101  = Branch
01   = Local Currency
```

The numbering strategy should be configurable.

---

## Universal Account Dimensions

Every account should support configurable dimensions such as:

```text
Legal Entity
Business Unit
Branch
Department
Cost Center
Profit Center
Product
Customer
Vendor
Project
Employee
Currency
Channel
```

---

## Account Master

Each account should contain the following domains:

```text
General
Financial
Dimensions
Posting
Tax
Workflow
Security
Reporting
AI
```

---

## COA Dashboard

### KPIs

- Total Accounts
- Active Accounts
- Control Accounts
- Posting Accounts
- Parent Accounts
- Inactive Accounts
- Pending Approvals
- AI Health

### Charts

- Account growth
- Accounts by type
- Accounts by product
- Accounts by entity
- Usage frequency

---

## Workspace

```text
Dashboard
↓
Chart Explorer
↓
Account Directory
↓
Account Profile
↓
Posting Rules
↓
Reports
```

---

## Chart Explorer

Interactive tree structure such as:

```text
Assets
↓
Cash
↓
Branch Cash
↓
Cash Counter
↓
Cash Drawer
```

Features:

- expand / collapse
- drag and drop
- search
- drill-down

---

## Account Directory

Columns:

- GL Code
- Account Name
- Type
- Category
- Parent
- Posting Allowed
- Currency
- Status

---

## Account Profile

### Tabs

- Overview
- Hierarchy
- Dimensions
- Posting Rules
- Tax
- Workflow
- Usage
- Security
- Audit
- AI

---

## Create Account Wizard

### Step 1 — General

Fields:

- GL Code
- Name
- Short Name
- Account Type
- Category
- Parent Account
- Status

### Step 2 — Financial

Fields:

- Normal Balance
- Currency
- Revaluation
- Interest Applicable
- Tax Applicable
- Control Account
- Reconciliation Required

### Step 3 — Dimensions

Select required dimensions, for example:

```text
✓ Branch
✓ Cost Center
✓ Product
✓ Customer
✗ Employee
```

### Step 4 — Posting Rules

Fields:

- Posting Allowed
- Manual Journal Allowed
- Automatic Posting
- Opening Balance
- Closing Account

### Step 5 — Security

Fields:

- Who can view
- Who can post
- Who can approve
- Who can close

### Step 6 — Reporting

Map to:

- Trial Balance
- Balance Sheet
- Profit & Loss
- Cash Flow
- RBI Return
- GST
- MIS

### Step 7 — Review

- Review summary
- Approval
- Publish

---

## Parent & Child Accounts

Example:

```text
Loans
↓
Gold Loan
↓
Gold Loan Principal
↓
Gold Loan Interest
↓
Gold Loan Penalty
```

Supports unlimited depth.

---

## Posting Controls

Each account can control:

- manual posting
- automatic posting
- reversal allowed
- negative balance
- backdated posting
- multi-currency
- inter-company

---

## Currency Handling

Supports:

```text
Local Currency
Reporting Currency
Transaction Currency
Functional Currency
```

Automatic revaluation should be supported.

---

## Tax Mapping

Every account can map to:

```text
GST
TDS
CSV
VAT
Withholding
Corporate Tax
```

---

## Product Mapping

Example:

```text
Gold Loan
↓
Principal Outstanding
Interest Receivable
Penalty Income
Auction Income
Processing Fee
```

No duplicate account definitions should be required for every product variant.

---

## Reporting Mapping

One account can be mapped to:

```text
Balance Sheet
P&L
Cash Flow
RBI Returns
Management Reports
Regulatory Reports
```

---

## Account Workflow

```text
Draft
↓
Finance Review
↓
CFO Review
↓
Approved
↓
Published
```

---

## AI Features

Examples:

```text
Suggest account classification
↓
Find duplicate accounts
↓
Recommend hierarchy improvements
↓
Detect unused accounts
↓
Suggest account merge
↓
Predict reporting impact
↓
Explain account usage
```

---

## Account Health

Calculated using:

- usage frequency
- duplicate risk
- posting errors
- mapping completeness
- reconciliation status
- audit findings

Example:

```text
Health: 98% ★★★★★
```

---

## Reports

Standard reports:

- Chart of Accounts
- Account Hierarchy
- Posting Accounts
- Control Accounts
- Unused Accounts
- Product Mapping
- Tax Mapping
- Dimension Usage
- Account Health

---

## Database Tables

```text
gl_account
gl_account_hierarchy
gl_account_category
gl_dimension
gl_dimension_rule
gl_currency_rule
gl_tax_mapping
gl_product_mapping
gl_reporting_mapping
gl_posting_control
gl_usage
gl_ai
gl_audit
```

---

## APIs

```text
GET    /api/v1/gl/accounts
POST   /api/v1/gl/accounts
GET    /api/v1/gl/accounts/{id}
PUT    /api/v1/gl/accounts/{id}
PATCH  /api/v1/gl/accounts/{id}/status
GET    /api/v1/gl/accounts/tree
GET    /api/v1/gl/accounts/search
GET    /api/v1/gl/accounts/{id}/usage
```

---

## Events

```text
GL_ACCOUNT_CREATED
GL_ACCOUNT_UPDATED
GL_ACCOUNT_ACTIVATED
GL_ACCOUNT_DEACTIVATED
GL_ACCOUNT_MERGED
GL_MAPPING_UPDATED
GL_REVALUATION_COMPLETED
```

---

## Backend Structure

```text
services/accounting/chart-of-accounts/
├── domain/
├── application/
├── infrastructure/
├── api/
├── analytics/
├── ai/
├── events/
└── tests/
```

---

## Frontend Structure

```text
modules/accounting/chart-of-accounts/
├── dashboard/
├── explorer/
├── directory/
├── profile/
├── hierarchy/
├── reports/
├── settings/
├── components/
└── hooks/
```

---

## Integration Matrix

- Loan: principal, interest, fees
- Deposit: liability, interest expense
- Gold Loan: gold inventory, receivables
- Treasury: investments, liquidity
- Forex: currency gains/losses
- HRMS: payroll expenses
- Procurement: expense and payable accounts
- Fixed Assets: asset and depreciation accounts
- Tax Engine: tax accounts
- Budgeting: budget control accounts

---

## GL Account 360

Every GL account should have a 360° view.

### Financial View

- current balance
- opening balance
- closing balance
- period movement

### Transaction View

- journal entries
- source modules
- posting frequency
- last activity

### Reporting View

- trial balance
- P&L
- balance sheet
- regulatory mapping

### Control View

- posting restrictions
- reconciliation status
- approval requirements

### AI View

- usage anomalies
- suggested merges
- classification improvements
- forecasted balance

---

## Definition of Done

The Chart of Accounts module is complete when it provides:

- configurable account hierarchy
- multi-dimensional accounting
- product and tax mappings
- posting controls
- reporting mappings
- approval workflows
- AI-assisted management
- audit trail
- enterprise search
- GL Account 360

---

## Critical Architectural Recommendation

Do not embed GL account numbers directly in business code.

Every product should instead use accounting posting templates.

Example:

```text
Loan Disbursement
↓
Posting Template
Debit  : Loan Principal Outstanding
Credit : Branch Cash
↓
GL Resolver
↓
Actual GL Accounts based on Branch, Product, Currency, Legal Entity
↓
Journal Entry
```

This design provides:

- different GL mappings for different legal entities or products
- easier regulatory changes
- new products without code changes
- support for multiple accounting books
- cleaner separation between business logic and accounting

---

## Recommended Next Package

The next module should be AFC-002 — Financial Calendar & Accounting Period Management, which will define:

- financial years
- accounting periods
- period open / close controls
- EOD / EOM / EOY processing
- holiday calendars
- posting windows
- fiscal calendars
- multi-company period management
- year-end closing
- AI-driven close readiness and bottleneck analysis
