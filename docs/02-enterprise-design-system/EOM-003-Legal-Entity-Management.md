# EOM-003 — Legal Entity Management

## Overview

Legal Entity Management is one of the most important financial foundations of ARTH.OS. It defines which legal company owns assets, liabilities, accounting books, tax registrations, banking licenses, and regulatory obligations.

Without this module, a true enterprise banking or NBFC platform cannot be constructed properly.

---

## Purpose

A legal entity is a legally registered company.

Examples:

- ARTH Holdings Pvt Ltd
- ARTH Finance Ltd
- ARTH Gold Finance Ltd
- ARTH Housing Finance Ltd
- ARTH Forex Pvt Ltd
- ARTH Insurance Broking Pvt Ltd

Each legal entity has its own:

- PAN
- GST
- CIN
- RBI license
- Financial statements
- Bank accounts
- Tax returns
- Employees
- Branches
- Accounting books

---

## Enterprise Hierarchy

The hierarchy for this module is:

Enterprise → Brand → Legal Entity → Business Unit → Zone → Region → Area → Branch

Every transaction should belong to one legal entity.

---

## Business Objectives

The module should support:

- Multi-company structures
- Multi-country operations
- Multi-currency processing
- Multi-tax jurisdictions
- Multi-book accounting
- Inter-company accounting
- Consolidated reporting

---

## Legal Entity Dashboard

Suggested KPIs:

- Legal entities
- Countries
- Licenses
- Branches
- Employees
- Revenue
- Assets
- Liabilities
- Compliance score

Suggested charts:

- Revenue by entity
- Assets by entity
- Branch distribution
- License status
- Tax filing calendar
- Regulatory health

---

## Workspace

The standard workspace should include:

- Dashboard
- Legal entity directory
- Entity profile
- Licenses
- Registrations
- Accounting
- Compliance
- Reports

---

## Entity Profile

The profile should be organized into tabs:

- Overview
- Corporate registrations
- Licenses
- Accounting
- Taxation
- Bank accounts
- Branches
- Business units
- Contacts
- Documents
- Timeline
- Audit
- AI insights

---

## Create Legal Entity Wizard

### Step 1 — General

Fields:

- Entity code
- Entity name
- Display name
- Legal type
- Status
- Country
- Date of incorporation

### Step 2 — Corporate Registration

Fields:

- CIN
- Registration number
- Registrar
- Incorporation date
- Corporate office
- Authorized capital
- Paid-up capital

### Step 3 — Tax Registration

Fields:

- PAN
- GST
- TAN
- VAT
- Service tax
- Import export code
- Professional tax

Multiple registrations should be supported.

### Step 4 — Regulatory Licenses

Fields:

- RBI license
- NBFC type
- SEBI
- IRDA
- FIU registration
- DPIIT
- ISO certifications
- Other licenses

Each license should include:

- Issue date
- Expiry date
- Renewal reminder

### Step 5 — Accounting

Fields:

- Base currency
- Chart of accounts
- Financial year
- Accounting standard
- Tax regime
- Reporting currency
- Consolidation method

### Step 6 — Banking

Fields:

- Primary bank
- Settlement bank
- Escrow account
- Current accounts
- Nostro/Vostro accounts
- Treasury accounts

### Step 7 — Contacts

Fields:

- Registered office
- Corporate office
- Phone
- Email
- Website
- Authorized signatories

### Step 8 — Compliance

Fields:

- AML
- KYC
- Internal audit
- External audit
- Data retention
- Record retention
- Risk rating

### Step 9 — Documents

Supporting documents:

- Certificate of incorporation
- PAN
- GST
- RBI license
- Board resolution
- MOA
- AOA
- Tax certificates
- Audit reports

OCR should be supported where applicable.

### Step 10 — Review and Submit

The review step should validate completeness and submit the entity for approval.

---

## Legal Entity Health

The entity health score should be calculated from:

- Missing registrations
- Expired licenses
- Tax pending
- Audit pending
- Missing bank accounts
- Compliance issues

Example:

Health score: 91%

---

## Business Relationships

A legal entity should own:

- Business units
- Branches
- Employees
- Customers
- Bank accounts
- Products
- Accounting books
- Assets
- Contracts

---

## Inter-Company Relationships

The platform should support relationships such as:

- Holding company
- Subsidiary
- Associate
- Joint venture

These should be available for accounting and reporting purposes.

---

## Banking Relationships

The module should maintain:

- Banks
- Accounts
- SWIFT codes
- IFSC codes
- Settlement structures
- Treasury relationships

---

## Accounting Relationships

Every legal entity should have:

- Chart of accounts
- Fiscal calendar
- Accounting books
- Cost centers
- Profit centers
- Budgets
- Financial statements

---

## Tax Management

The module should support tax structures such as:

- GST
- PAN
- TDS
- CST
- VAT
- Corporate tax
- Professional tax
- Withholding tax

These should be configurable by country and entity.

---

## Regulatory Management

The module should track:

- License lifecycle
- Renewal dates
- Inspections
- Regulator details
- Compliance status
- Penalties

---

## Branch Assignment

A branch should belong to one legal entity only. The legal entity then owns the associated business units and branches.

---

## AI Features

Suggested AI use cases:

- Show expiring licenses
- Predict compliance risk
- Compare entities
- Highlight missing registrations
- Audit readiness
- Tax optimization opportunities

---

## Reports

Suggested reports:

- Legal entity register
- License register
- Tax register
- Compliance register
- Bank account register
- Corporate structure
- Entity performance
- Entity health
- Regulatory calendar

---

## Permissions

Suggested access model:

- Enterprise admin: full access
- Legal head: legal entity oversight
- Compliance officer: compliance access
- CFO: finance-related access
- Auditor: read-only
- Branch manager: no access unless delegated

---

## Workflow

Legal entity creation should use the shared workflow framework:

Draft → Legal review → Finance review → Compliance review → Enterprise approval → Active

---

## Database Tables

Suggested tables:

- legal_entity
- legal_entity_registration
- legal_entity_license
- legal_entity_tax
- legal_entity_bank
- legal_entity_contact
- legal_entity_document
- legal_entity_compliance
- legal_entity_finance
- legal_entity_relationship
- legal_entity_settings
- legal_entity_audit
- legal_entity_timeline

---

## API Structure

Suggested endpoints:

- GET /api/v1/eom/legal-entities
- POST /api/v1/eom/legal-entities
- GET /api/v1/eom/legal-entities/{id}
- PUT /api/v1/eom/legal-entities/{id}
- PATCH /api/v1/eom/legal-entities/{id}/status
- GET /api/v1/eom/legal-entities/{id}/licenses
- GET /api/v1/eom/legal-entities/{id}/registrations
- GET /api/v1/eom/legal-entities/{id}/health
- GET /api/v1/eom/legal-entities/{id}/timeline

---

## Events

Suggested events:

- LEGAL_ENTITY_CREATED
- LEGAL_ENTITY_UPDATED
- LEGAL_ENTITY_ACTIVATED
- LICENSE_ADDED
- LICENSE_RENEWED
- LICENSE_EXPIRED
- TAX_UPDATED
- BANK_ACCOUNT_ADDED
- COMPLIANCE_UPDATED
- ENTITY_HEALTH_CHANGED

---

## Backend Structure

services/eom/legal-entity/
├── domain/
├── application/
├── infrastructure/
├── api/
├── integrations/
├── events/
└── tests/

---

## Frontend Structure

modules/eom/legal-entity/
├── dashboard/
├── list/
├── create/
├── details/
├── compliance/
├── accounting/
├── reports/
├── settings/
└── components/

---

## Integration Points

This module should integrate with:

- Accounting for books and financial statements
- HRMS for employer entity relationships
- Customer module for ownership and onboarding
- Lending for licensed products
- Deposits for deposit-taking entity setup
- Treasury for bank account management
- Risk and compliance
- Document management
- Workflow engine
- Notification engine

---

## Definition of Done

The module is complete when it supports:

- Multi-company management
- Multi-country registrations
- Multi-tax jurisdictions
- Regulatory license lifecycle
- Bank account management
- Accounting defaults
- Inter-company relationships
- Audit trail
- Workflow approvals
- AI-driven compliance insights

---

## Enterprise Recommendation

This should not be treated as a simple master data record. Each legal entity should become a financial governance hub that exposes:

- Corporate view
- Financial view
- Regulatory view
- Operational view
- Risk view
- AI view

This transforms Legal Entity Management into the governance center for the entire enterprise.

---

## Next Package

The next package should be EOM-004 — Business Unit Management.
