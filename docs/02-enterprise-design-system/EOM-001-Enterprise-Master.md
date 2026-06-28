# EOM-001 — Enterprise Master

## Overview

Enterprise Master is the root object of the ARTH.OS platform. It represents the top-most organizational entity that owns all downstream entities, products, services, workflows, and business operations.

This is the first real enterprise module in the platform and the foundation for all other organizational and business domain modules.

---

## Purpose

The Enterprise Master exists to represent the overall organization that owns:

- Multiple brands
- Multiple legal entities
- Multiple business units
- Multiple countries and zones
- Thousands of branches and departments
- A shared operating model for all business modules

Examples:

- Muthoot Finance
- Manappuram Finance
- Bajaj Finance
- HDB Financial Services
- Federal Bank
- ICICI Bank

---

## Business Goals

The Enterprise Master should:

- Define the organization clearly
- Define enterprise-wide policies
- Define enterprise branding
- Define financial defaults
- Define compliance defaults
- Define localization settings
- Provide tenant isolation for multi-tenant SaaS deployments
- Act as the parent object for all modules and entities

---

## Entity Model

The Enterprise Master should be modeled as a rich aggregate with the following concern areas:

- General
- Branding
- Legal
- Finance
- Compliance
- Localization
- Contact
- Documents
- Settings
- Integrations
- AI
- Audit

This should be implemented as a composite domain rather than a single oversized table.

---

## Enterprise Dashboard

The Enterprise Master should provide an executive dashboard with the following high-value indicators:

- Enterprise name
- Status
- Country
- Legal entities
- Business units
- Branches
- Employees
- Customers
- Assets
- AI score

Suggested charts:

- Branch growth
- Employee growth
- Revenue trend
- Compliance status
- License expiry
- Enterprise health

---

## Workspace

The main workspace should follow a clear structure:

- Dashboard
- Enterprise profile
- Business overview
- Financial overview
- Compliance
- Settings
- Audit
- Reports

---

## Enterprise Profile

The profile should be organized into tabs:

- Overview
- Brand
- Legal
- Finance
- Compliance
- Localization
- Contacts
- Documents
- Integrations
- AI insights
- Timeline
- Audit

---

## Create Enterprise Wizard

The creation flow should be a guided wizard rather than a flat form.

### Step 1 — General Information

Fields:

- Enterprise code
- Enterprise name
- Short name
- Display name
- Enterprise type
- Industry
- Business category
- Business model
- Status

### Step 2 — Branding

Fields:

- Logo
- Primary color
- Secondary color
- Theme
- Website
- Email domain
- Mobile app name
- Portal name

Live preview should be supported.

### Step 3 — Legal

Fields:

- Country
- Registration number
- Incorporation date
- Tax number
- GST or VAT number
- PAN
- Corporate identity number
- Regulatory license

Multiple registrations should be supported.

### Step 4 — Finance

Fields:

- Base currency
- Financial year
- Accounting standard
- Tax system
- Default GL
- Default cost center
- Default profit center

### Step 5 — Localization

Fields:

- Language
- Time zone
- Date format
- Number format
- Fiscal calendar
- Holiday calendar

### Step 6 — Contact

Fields:

- Corporate address
- Head office
- Email
- Phone
- Website
- Support contact

### Step 7 — Compliance

Fields:

- AML enabled
- KYC policy
- Data retention
- Audit retention
- Password policy
- Session policy

### Step 8 — Integrations

Fields:

- Core banking
- SMS
- Email
- WhatsApp
- Payment gateway
- OCR
- AML
- Credit bureau
- Identity verification
- ERP
- CRM

### Step 9 — Documents

Upload documents such as:

- Certificate
- GST
- PAN
- Trade license
- Incorporation documents
- Board resolution
- Logo files
- Policy documents

OCR should extract metadata where applicable.

### Step 10 — Review

The review screen should show consolidated sections for:

- General
- Branding
- Legal
- Finance
- Localization
- Compliance
- Integrations
- Documents

### Step 11 — Submit

The submit step should use the workflow framework:

Draft → Review → Admin approval → Enterprise created

---

## Enterprise Detail Page

The detail page should provide a rich operational overview:

- Overview
- Business metrics
- Branches
- Legal entities
- Business units
- Financial settings
- Compliance
- Documents
- Audit timeline
- AI insights

---

## Enterprise Health Score

A unique and valuable feature should be the Enterprise Health Score.

It should be calculated from metrics such as:

- Missing configuration
- Missing licenses
- Expired certificates
- Branch readiness
- Policy coverage
- Security posture
- Integration status

Example:

Enterprise Health: 93% with a strong score indicator

---

## Digital Enterprise Twin

Every enterprise object should expose multiple perspectives:

### Operational

- Branches
- Employees
- Departments
- Business units

### Financial

- Revenue
- Expenses
- Budget
- Assets
- GL mappings
- Profit centers

### Compliance

- Licenses
- Policies
- Regulatory matters
- Audit exceptions

### Technology

- API status
- Integrations
- Infrastructure health
- Security posture
- Backups

### AI

- Enterprise summary
- Growth forecast
- Risk analysis
- Optimization suggestions

---

## Enterprise Settings

Settings should be organized into logical groups:

- General
- Branding
- Finance
- HR
- Customer
- Accounting
- Loans
- Deposits
- Treasury
- Forex
- Security
- Notifications
- Workflow
- AI
- Reports

These settings should become the default values inherited by downstream modules.

---

## Permission Matrix

Suggested role access model:

- Super admin: full access
- Enterprise admin: enterprise-wide access
- Compliance head: compliance-related access
- CFO: finance-related access
- CIO: technology-related access
- Auditor: read-only access
- Branch manager: no access unless explicitly delegated

---

## Workflow

The Enterprise Master should support a standard lifecycle workflow:

Create → Validate → Approval → Configuration → Activation

---

## AI Features

The module should include AI-assisted capabilities such as:

- Explain enterprise configuration
- Find missing settings
- Compare against industry best practices
- Identify compliance gaps
- Recommend organizational improvements
- Predict branch expansion requirements

---

## Reports

Suggested reports:

- Enterprise profile
- Enterprise health report
- Compliance report
- License register
- Configuration report
- Integration status
- Branding report
- Localization report

---

## Database Schema (Core)

The core data model should include the following primary tables:

- enterprise
- enterprise_branding
- enterprise_legal
- enterprise_finance
- enterprise_localization
- enterprise_compliance
- enterprise_contacts
- enterprise_documents
- enterprise_integrations
- enterprise_settings
- enterprise_audit

The design should avoid one oversized table and instead keep each concern domain separate.

Suggested core columns for the enterprise table:

- id
- code
- name
- display_name
- short_name
- type
- status
- industry
- currency_code
- timezone
- language
- fiscal_year_start
- created_at
- updated_at

---

## API Structure

Suggested API endpoints:

- GET /api/v1/eom/enterprises
- POST /api/v1/eom/enterprises
- GET /api/v1/eom/enterprises/{id}
- PUT /api/v1/eom/enterprises/{id}
- PATCH /api/v1/eom/enterprises/{id}/status
- GET /api/v1/eom/enterprises/{id}/health
- GET /api/v1/eom/enterprises/{id}/timeline
- GET /api/v1/eom/enterprises/{id}/audit

---

## Events

Suggested events:

- ENTERPRISE_CREATED
- ENTERPRISE_UPDATED
- ENTERPRISE_ACTIVATED
- ENTERPRISE_DEACTIVATED
- ENTERPRISE_CONFIGURATION_CHANGED
- ENTERPRISE_BRANDING_UPDATED
- ENTERPRISE_LICENSE_EXPIRED
- ENTERPRISE_HEALTH_CHANGED

---

## Suggested Backend Structure

services/eom/src/enterprise/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── repositories/
│   ├── services/
│   └── events/
├── application/
│   ├── commands/
│   ├── queries/
│   ├── handlers/
│   ├── dto/
│   └── validators/
├── infrastructure/
│   ├── persistence/
│   ├── messaging/
│   ├── cache/
│   └── integrations/
├── api/
│   ├── routers/
│   ├── schemas/
│   └── dependencies/
└── tests/

---

## Suggested Frontend Structure

apps/admin-portal/modules/eom/enterprise/
├── dashboard/
├── list/
├── create/
├── details/
├── settings/
├── reports/
├── components/
├── hooks/
├── services/
├── types/
└── routes/

---

## Definition of Done

EOM-001 is complete only when it includes:

- Enterprise dashboard
- Enterprise wizard
- Enterprise profile
- Enterprise settings
- Health score
- Workflow integration
- Audit trail
- Document management
- Role-based access
- AI insights
- Reports
- APIs
- Unit tests
- Integration tests

---

## Architecture Recommendation

This should not be treated as a static setup screen. It should become a living digital enterprise profile that continuously exposes:

- Business health
- Financial health
- Operational health
- Compliance health
- Technology health
- AI health

That transforms Enterprise Master into an executive control center that all other modules can build upon.

---

## Next Implementation Package

The next package should be EOM-002 — Brand Management, which will cover:

- Multi-brand architecture
- Brand inheritance rules
- White-label support
- Theme and logo management
- Brand-specific products
- Brand-level documents
- Brand governance
- Approval workflows
