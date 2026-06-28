# EP-015 — Enterprise Document Management System (EDMS)

## Overview

Enterprise Document Management System is the enterprise content platform for ARTH.OS. It is not just a file upload module. It is the shared document backbone used by customer onboarding, lending, gold loan, deposits, HRMS, accounting, treasury, forex, legal, compliance, audit, and operations.

The design principle is simple:

```text
Every document in ARTH.OS should exist only once.
Every business module should reference EDMS.
```

---

## Vision

EDMS becomes the enterprise knowledge and evidence platform for the suite.

It provides:

- Central document repository
- OCR and metadata extraction
- AI classification
- Version control
- Digital signatures
- Workflow-driven review and approval
- Retention and archival policies
- Enterprise search
- IAM-integrated security
- Auditability

---

## EDMS Architecture

```text
Upload
↓
OCR
↓
AI Classification
↓
Metadata Extraction
↓
Validation
↓
Storage
↓
Version Control
↓
Workflow
↓
Digital Signature
↓
Archive
```

---

## Document Categories

### Customer

- Aadhaar
- PAN
- Passport
- Driving License
- Utility Bill
- Bank Statement
- Income Proof
- Photograph
- Signature

### Loan

- Application
- Agreement
- Sanction Letter
- Mortgage
- Guarantor
- Insurance
- EMI Schedule

### Gold Loan

- Gold Images
- Gold Packet Photos
- Appraisal Sheet
- Packet Labels
- Valuation Certificate

### Deposits

- FD Receipt
- Nomination
- KYC
- Deposit Agreement

### HR

- Resume
- Offer Letter
- Appointment
- Certificates
- Experience
- Salary Revision
- Performance Review

### Accounting

- Invoice
- Voucher
- Receipt
- Payment Advice
- Bank Statement

### Treasury

- Deal Ticket
- Confirmation
- Settlement Advice
- SWIFT Copy

### Compliance

- RBI Returns
- Audit Reports
- Inspection Notes
- Risk Register

---

## Dashboard

### KPIs

- Documents
- OCR Success
- Digital Signatures
- Pending Review
- Expired Documents
- Storage Used
- AI Accuracy
- Retention Compliance

### Charts

- Upload trend
- Document types
- OCR accuracy
- Storage growth
- Expiry calendar

---

## Workspace

```text
Dashboard
↓
Document Explorer
↓
Inbox
↓
OCR Queue
↓
Approvals
↓
Templates
↓
Archive
↓
Reports
```

---

## Document Explorer

### Enterprise grid columns

- Document ID
- Title
- Category
- Owner
- Status
- Version
- Created By
- Created On
- Retention
- AI Confidence

### Features

- Search
- AI search
- Filters
- Saved views
- Bulk actions
- Export

---

## Document Profile

### Tabs

- Overview
- Preview
- Versions
- Metadata
- Workflow
- Approvals
- OCR
- AI
- Audit
- Timeline

---

## Upload Wizard

### Step 1 — General

Fields:

- Category
- Type
- Owner
- Branch
- Department
- Tags

### Step 2 — Upload

Supported formats:

- PDF
- Images
- Word
- Excel
- PowerPoint
- ZIP
- Email

Multiple upload should be supported.

### Step 3 — OCR

Automatic pipeline:

```text
Extract → Validate → Correct → Save
```

### Step 4 — Metadata

Example fields:

- Customer
- Loan Number
- PAN
- Date
- Expiry
- Reference

### Step 5 — Classification

AI-driven classification such as:

```text
KYC
Agreement
Invoice
Voucher
Certificate
Legal
HR
Unknown
```

### Step 6 — Security

Access classification:

- Confidential
- Internal
- Public
- Restricted
- Highly Confidential

### Step 7 — Workflow

Assign review and approval, then signature, publication, and archival.

### Step 8 — Review

- Review summary
- Submit

---

## OCR Engine

Supports:

- English
- Hindi
- Malayalam
- Tamil
- Kannada
- Telugu
- Arabic

Extracts fields such as:

```text
Name
PAN
Aadhaar
Address
DOB
Invoice Number
Amount
GST
IFSC
Account Number
```

---

## AI Classification

Automatically identifies document types such as:

```text
KYC
Invoice
Agreement
Cheque
Passport
Salary Slip
Gold Appraisal
Bank Statement
```

---

## Document Versioning

```text
V1
↓
V2
↓
V3
↓
Archive
```

Rollback should be supported.

---

## Digital Signature

Supports:

- Aadhaar eSign
- USB Token
- DSC
- PKI
- Internal approval signature

---

## Retention Policy

Examples:

```text
KYC → 10 years
HR Records → 7 years
Accounting → 8 years
Audit → Permanent
```

Automatic archival should be supported.

---

## Document Workflow

```text
Upload
↓
OCR
↓
Review
↓
Approval
↓
Signature
↓
Published
↓
Archive
```

---

## AI Features

Examples:

```text
Summarize document
↓
Extract clauses
↓
Find missing signatures
↓
Compare versions
↓
Detect fraud
↓
Suggest category
↓
Recommend retention
```

---

## Enterprise Search

Search by:

- Text
- OCR
- Metadata
- Customer
- Loan
- Employee
- PAN
- Aadhaar
- Agreement Number

Natural language search should be supported, for example:

```text
Show me all expired RBI licenses.
Find all PAN cards uploaded today.
Show invoices above ₹5 Lakhs.
```

---

## Document Templates

Supports document templates such as:

- Offer Letter
- Loan Agreement
- FD Receipt
- Gold Loan Packet
- Sanction Letter
- NOC
- Legal Notice

Merge fields should support:

```text
{{Customer}}
{{Loan}}
{{Branch}}
{{Amount}}
```

---

## Reports

Standard reports:

- Upload Report
- OCR Accuracy
- Missing Documents
- Expiring Documents
- Storage Report
- Retention Report
- Version Report
- Workflow Report
- AI Accuracy Report

---

## Security

Integrated with IAM.

Supports:

- View
- Download
- Print
- Edit
- Share
- Sign
- Delete

Watermarking should be supported:

```text
CONFIDENTIAL
Downloaded by Rahul
01-Jan-2026
```

---

## Database

```text
document
document_version
document_metadata
document_category
document_tag
document_owner
document_workflow
document_signature
document_ocr
document_ai
document_storage
document_permission
document_retention
document_audit
```

---

## APIs

```text
POST /api/v1/documents
GET /api/v1/documents
GET /api/v1/documents/{id}
PUT /api/v1/documents/{id}
POST /api/v1/documents/{id}/ocr
POST /api/v1/documents/{id}/sign
POST /api/v1/documents/{id}/approve
GET /api/v1/documents/search
GET /api/v1/documents/{id}/versions
```

---

## Events

```text
DOCUMENT_UPLOADED
OCR_COMPLETED
METADATA_EXTRACTED
DOCUMENT_APPROVED
DOCUMENT_SIGNED
DOCUMENT_ARCHIVED
DOCUMENT_EXPIRED
RETENTION_COMPLETED
```

---

## Backend Structure

```text
services/document/
├── upload/
├── ocr/
├── classification/
├── metadata/
├── workflow/
├── signature/
├── storage/
├── search/
├── archive/
├── retention/
├── ai/
└── audit/
```

---

## Frontend Structure

```text
modules/document/
├── dashboard/
├── explorer/
├── upload/
├── viewer/
├── ocr/
├── workflow/
├── templates/
├── archive/
├── reports/
└── components/
```

---

## Integration Matrix

- Customer: KYC, identity, address
- Loan: agreements, collateral
- Gold Loan: packet photos, valuation
- Deposits: FD receipts, nominations
- HRMS: employee files
- Accounting: invoices, vouchers
- Treasury: deal confirmations
- Forex: compliance documents
- Procurement: purchase orders
- Audit: evidence and reports

---

## Document 360

Every document should have a full lifecycle view.

### Content View

- Preview
- OCR text
- Metadata

### Business View

- Linked customer
- Linked loan
- Linked employee
- Linked transaction

### Workflow View

- Review
- Approval
- Signature

### Security View

- Permissions
- Downloads
- Watermarks
- Access history

### Compliance View

- Retention
- Expiry
- Legal hold
- Audit

### AI View

- Summary
- Risk indicators
- Missing fields
- Duplicate detection
- Fraud indicators

---

## Definition of Done

EDMS is complete when it supports:

- Enterprise document repository
- OCR with multilingual support
- AI classification
- Metadata extraction
- Version control
- Digital signatures
- Workflow integration
- Retention management
- Enterprise search
- IAM integration
- Audit trail
- Document 360

---

## Major Architectural Recommendation

ARTH.OS should evolve EDMS into an Enterprise Knowledge & Evidence Platform.

Every document should become an intelligent object with:

### Content Layer

- OCR text
- Structured metadata
- Embedded thumbnails

### Business Layer

- Linked customer, loan, employee, branch, GL entries, workflows

### Compliance Layer

- Retention policy
- Regulatory classification
- Legal hold
- Audit evidence

### AI Layer

- Automatic summaries
- Clause extraction
- Similar-document search
- Duplicate detection
- Fraud and tampering analysis
- Q&A over document content

### Knowledge Layer

- Semantic indexing
- Enterprise-wide search
- Cross-reference relationships
- Retrieval for AI assistants

This turns EDMS into the knowledge backbone of ARTH.OS rather than a simple storage layer.

---

## Recommended Next Step

With EDMS complete, the next major platform service should be Accounting & General Ledger, which becomes the financial engine for the full suite.
