# AFC-009 — Enterprise Accounts Payable (AP)

**Priority:** ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ (20/10)

**Estimated Development:** 12–16 Weeks

**Estimated UI Screens:** 220+

**Estimated APIs:** 750+

**Estimated Database Tables:** 220+

---

## Vision

Accounts Payable is much more than Vendor Payments — it manages the entire Procure-to-Pay (P2P) lifecycle:

Vendor ↓ Purchase Request ↓ Purchase Order ↓ Goods Receipt ↓ Vendor Invoice ↓ Invoice Verification ↓ Approval ↓ Payment ↓ General Ledger

The General Ledger must never contain vendor business logic — vendor accounting belongs to the AP sub-ledger and publishes accounting events to the Accounting Event Engine that drive Journal creation and GL posting.

---

## Enterprise Architecture

```
Procurement ↓ Vendor Master ↓ Purchase Order ↓ Goods Receipt ↓ Invoice ↓ Accounts Payable ↓ Payment Engine ↓ Accounting Event Engine ↓ Journal Engine ↓ General Ledger
```

---

## AP Modules

- Vendor Management
- Purchase Invoice
- Debit Notes
- Credit Notes
- Advance Payments
- Invoice Matching (2-way / 3-way / 4-way)
- Approval Workflow
- Payment Proposal
- Payment Processing
- Tax Engine (GST / Withholding Tax / TDS)
- Vendor Ledger
- Aging & Reconciliation
- Dispute Management
- Vendor Portal (Self-service)
- Analytics & Reporting
- AI & Anomaly Detection
- Integration adapters (Procurement, EDMS, Bank Files)

---

## AP Dashboard

### KPIs

- Total Vendors
- Outstanding Payables
- Invoices Pending
- Invoices Approved
- Payments Due Today
- Overdue Invoices
- Average Payment Days (DPO)
- Early Payment Discounts Captured
- Blocked Invoices
- Vendor Risk Score

### Charts

- Outstanding Payables (trend)
- Invoice Aging by Bucket
- Payment Trend
- Vendor Spend Distribution
- GST Input Credit Trend
- Top Vendors (by spend)
- Due Calendar

---

## Workspace

Dashboard ↓ Vendor Explorer ↓ Invoices ↓ Approvals ↓ Payment Proposal ↓ Payments ↓ Vendor Ledger ↓ Reconciliation ↓ Reports

---

## Vendor Master

Each vendor record contains structured sections for:

- General (name, codes, identifiers)
- Finance (ledger account, payment terms, credit limits)
- Tax (GSTIN, TDS applicability)
- Bank Accounts
- Contracts
- Contacts
- Compliance (KYC, sanctions)
- Documents (EDMS links)
- Performance & SLAs
- Risk Indicators
- Audit trail & AI-derived signals

---

## Vendor Categories

- Goods Supplier
- Service Provider
- Contractor
- Consultant
- Law Firm
- Insurance Company
- Technology Vendor
- Courier
- Marketing Agency
- Utility Provider
- Government
- Intercompany Vendor

---

## Vendor 360

Tabs: Overview | Invoices | Payments | Purchase Orders | Contracts | Bank Accounts | GST/TDS | Documents | Performance | Risk | Audit | AI Insights

---

## Vendor Registration Workflow

Draft ↓ Procurement Review ↓ Finance Review ↓ Compliance Review ↓ Approval ↓ Vendor Activated

---

## Purchase Invoice

Header fields:

- Invoice Number
- Vendor
- Invoice Date
- Due Date
- Currency
- Business Unit
- Branch
- Linked Purchase Order (optional)
- Total Amount

---

## Invoice Lines

Each invoice line carries:

- Expense / GL Account
- Cost Center
- Profit Center
- Department
- GST / Tax codes
- Quantity
- Unit Price
- Line Amount
- Free-form description

Unlimited lines per invoice supported.

---

## Invoice Matching Engine

Supports:

- 2-Way Match: Purchase Order ↔ Invoice
- 3-Way Match: Purchase Order ↔ Goods Receipt ↔ Invoice
- 4-Way Match: Purchase Order ↔ Goods Receipt ↔ Inspection ↔ Invoice

Automatic exception detection with rules for tolerance, quantity/price variance, and block reasons.

---

## Invoice Lifecycle

Created ↓ OCR extraction ↓ Validation ↓ Matching ↓ Approval ↓ Payment Proposal ↓ Paid ↓ Closed

Audit trails and status history recorded at every step.

---

## OCR Integration

OCR extracts: Vendor Name, GSTIN, Invoice Number, Invoice Date, Amount, Tax lines, Bank details. OCR output is stored alongside original document in EDMS; human verification workflows available.

---

## Tax Engine

Supports: GST (CGST/SGST/IGST), CESS, TDS, Reverse Charge, Input Credit processing, and localized tax rulesets. Tax is computed per-line and at invoice totals; tax-ledger entries flow to AP tax accounts and feed the Accounting Event Engine.

---

## Payment Proposal Engine

Suggests payment candidates using rules and optimizers:

- Invoices due today
- High priority invoices (SLA, business-critical)
- Early discount opportunities
- Cash availability / treasury constraints
- Batch grouping for bank formats

Supports manual intervention, approval, and split allocations.

---

## Payment Methods

- NEFT / RTGS / IMPS
- UPI
- Cheque / DD
- Cash
- Internal Transfer
- SWIFT / International payments
- Bank file exports (NACH, SEPA, NACHA-like formats)

---

## Payment Workflow

Payment Proposal ↓ Treasury Review ↓ Finance Approval ↓ Bank File Generation ↓ Payment Execution ↓ Confirmation ↓ GL Posting

End-to-end traceability and reconciliation against bank statements.

---

## Vendor Ledger

Tracks: Opening Balance, Invoices, Payments, Credit Notes, Debit Notes, Adjustments, Closing Balance. Provides running balance and transaction-level drilldown.

---

## Aging Analysis

Buckets: Current | 1–30 Days | 31–60 Days | 61–90 Days | 91–180 Days | 180+ Days

---

## Vendor Risk Engine

Signals:

- Late Deliveries
- Invoice Disputes
- Compliance or KYC issues
- Payment Delays
- Contract Violations
- Fraud Indicators

Risk score feeds vendor selection, payment prioritization, and procurement alerts.

---

## AI Features

- Duplicate invoice detection
- Cash requirement forecasting
- Suggested payment dates and optimal batching
- Fraud and anomaly detection (collusion, unusual amounts)
- Early discount optimization suggestions
- Predictive aging and dispute likelihood

---

## Reports

Standard reports:

- Vendor Register
- Invoice Register
- Outstanding Payables
- Aging Analysis
- Payment Register
- GST Input Credit Report
- TDS Report
- Vendor Performance
- Vendor Risk Report
- AP Health Report

---

## AP Health Score

Computed from overdue invoices, matching exceptions, duplicates, SLA compliance, disputes, and audit findings. Example: "Accounts Payable Health — 97% ★★★★★"

---

## Database Tables (representative)

- vendor
- vendor_bank_account
- vendor_contact
- vendor_contract
- vendor_tax
- vendor_document
- purchase_invoice
- purchase_invoice_line
- invoice_match
- invoice_exception
- payment_proposal
- payment_batch
- payment_transaction
- vendor_ledger
- vendor_aging
- vendor_performance
- vendor_risk
- ap_ai (AI artifacts)
- ap_audit

---

## APIs (representative)

- GET    /api/v1/ap/vendors
- POST   /api/v1/ap/vendors
- GET    /api/v1/ap/vendors/{id}
- POST   /api/v1/ap/invoices
- GET    /api/v1/ap/invoices
- GET    /api/v1/ap/invoices/{id}
- POST   /api/v1/ap/payment-proposals
- POST   /api/v1/ap/payments
- GET    /api/v1/ap/vendor-ledger
- GET    /api/v1/ap/aging
- GET    /api/v1/ap/dashboard

AP design should follow enterprise EDS contracts: typed request/response shapes, pagination, filtering, and event-driven acknowledgment where appropriate.

---

## Events

- VENDOR_CREATED
- VENDOR_APPROVED
- INVOICE_RECEIVED
- INVOICE_MATCHED
- INVOICE_APPROVED
- PAYMENT_PROPOSAL_CREATED
- PAYMENT_EXECUTED
- PAYMENT_FAILED
- VENDOR_RECONCILED

AP systems MUST publish accounting events to the Accounting Event Engine (standard event schema) instead of directly writing GL rows.

---

## Backend Structure (recommended)

```
services/accounting/accounts-payable/
├── vendor/
├── invoice/
├── matching/
├── payments/
├── ledger/
├── reconciliation/
├── tax/
├── analytics/
├── ai/
├── workflow/
└── tests/
```

Each bounded context should own its data and provide well-documented API endpoints and events.

---

## Frontend Structure (recommended)

```
modules/accounting/accounts-payable/
├── dashboard/
├── vendors/
├── invoices/
├── matching/
├── payment-proposals/
├── payments/
├── ledger/
├── reports/
├── settings/
└── components/
```

---

## Integration Matrix (high level)

- Procurement: Purchase Orders & Goods Receipts
- EDMS: Invoice OCR & attachments
- Tax Engine: GST, TDS, localized tax rules
- Treasury/Bank: Payment execution and confirmation
- General Ledger: Journal posting via Accounting Event Engine
- Budget Control: Budget availability checks
- Vendor Portal: Self-service invoice tracking
- IAM: Role-based approvals and segregation of duties

---

## Accounts Payable 360

Views to expose for every vendor and invoice:

- Financial View: outstanding balance, credit limit, payment history, aging
- Procurement View: purchase orders, goods receipts, contracts, delivery performance
- Compliance View: GST registrations, TDS compliance, KYC, documents
- Operational View: invoice lifecycle, approval status, payment batches, disputes
- AI View: fraud risk, duplicate probability, payment optimization suggestions

---

## Definition of Done

AP is complete when it supports:

- Enterprise Vendor Management and onboarding
- Invoice OCR and validation
- 2-way, 3-way, and 4-way matching
- GST/TDS processing and tax-ledger posting
- Payment proposal & multi-bank payment processing
- Vendor ledger and aging analysis
- Vendor risk scoring and AI anomaly detection
- Full audit trail for every action and event
- Publish accounting events for Journal/GL via Accounting Event Engine

---

## Major Architectural Recommendation — Smart Payment Optimization Engine

Instead of naive batch payments, implement a Smart Payment Optimization Engine that evaluates:

```
Approved Invoices│Cash Position│Due Dates│Early Payment Discounts│Vendor Priority│Credit Terms│Treasury Limits│AI Optimizer → Optimized Payment Schedule
```

Benefits:

- Maximize early payment discounts
- Avoid late-payment penalties
- Optimize daily cash flow
- Prioritize strategic vendors
- Automatically generate treasury-friendly payment batches

This capability is a strong enterprise differentiator.

---

## Next Module

AFC-010 — Enterprise Accounts Receivable (AR) (recommended next)

AR for an NBFC requires special capabilities: loan EMIs, interest calculations, auto-allocation of receipts, dunning, collections, gateway integration, and tight integration with lending and deposits modules.

---

*Document created for ARTH.OS Enterprise Financial Core — Accounts Payable (AFC-009).*