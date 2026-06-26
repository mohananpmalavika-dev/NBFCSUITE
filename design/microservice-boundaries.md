# Microservice Boundaries — NBFCSUITE

This document lists the initial set of microservices, their responsibilities, and top-level REST API contracts to guide implementation and integration.

Core services (short descriptions + key endpoints):

- Auth Service (`services/auth`)
  - Responsibilities: Authentication, authorization, token issuance (JWT/OIDC), user management, role & permission management, SSO integration.
  - Key endpoints:
    - `POST /auth/login` — exchange credentials for access token
    - `POST /auth/refresh` — refresh token
    - `GET /auth/users/{id}` — get user profile (admin)
    - `POST /auth/users` — create user

- Customer Service (`services/customer`) — Customer 360
  - Responsibilities: single canonical CIF (Customer Information File), KYC, contact details, addresses, identity documents, linked accounts and relationships.
  - Key endpoints: `GET /customers/{id}`, `POST /customers`, `PUT /customers/{id}`

- LOS (Loan Origination System) (`services/los`)
  - Responsibilities: application intake, document ingestion, OCR orchestration, initial scoring, workflow orchestration for underwriting.
  - Key endpoints:
    - `POST /applications` — submit loan application
    - `GET /applications/{id}` — get application status
    - `POST /applications/{id}/documents` — upload doc
    - `POST /applications/{id}/submit` — send for underwriting

- LMS (Loan Management System) (`services/lms`)
  - Responsibilities: loan booking, amortization schedules, EMI calculation, interest posting, charges, prepayment and foreclosure handling.
  - Key endpoints: `POST /loans`, `GET /loans/{id}`, `POST /loans/{id}/payment`

- Collections Service (`services/collections`)
  - Responsibilities: buckets, collector assignment, reminders, call logging, promise-to-pay tracking, settlement engine.
  - Key endpoints: `GET /buckets`, `POST /collections/assign`, `POST /collections/{id}/note`

- FinDNA / AI Service (`services/findna`)
  - Responsibilities: behavioral scoring, explainable risk signals, feature store, AI models orchestration, embeddings + vector search.
  - Key endpoints: `POST /score/behavior`, `GET /explanations/{id}`

- Accounts & Deposits (`services/accounts` / `services/deposits`)
  - Responsibilities: CASA, term deposits, passbook entries, standing instructions.

- Payments & Gateway (`services/payments`)
  - Responsibilities: UPI/IMPS/NEFT/RTGS integration, gateway, reconciliation, virtual accounts.

- Treasury & Forex (`services/treasury`)
  - Responsibilities: FX rates, hedging, cash position, nostro/vostro.

- Document Management (`services/docstore`)
  - Responsibilities: secure storage, versioning, eSign integration, expiry alerts.

- Reporting & Analytics (`services/reporting`, `services/analytics`)
  - Responsibilities: scheduled reports, BI data pipelines, exec dashboards.

- Notifications (`services/notifications`)
  - Responsibilities: email, SMS, WhatsApp, push notifications, templating.

- Workflow & Rules Engine (`services/workflow`)
  - Responsibilities: configurable workflows, state machines, rule execution, audit trail.

- Accounting (`services/accounting`)
  - Responsibilities: general ledger, postings, bank reconciliation, trial balance, P&L, balance sheet.

- Identity & Integration Gateway (`services/gateway`)
  - Responsibilities: API gateway, routing, rate-limiting, service discovery, auth delegation.

Design notes:
- Each service owns its data (database per service). Communication via REST + events (Kafka/RabbitMQ) for domain events.
- FinDNA should be a pluggable AI service used by underwriting, collections, and CRM.
- Start with a minimal set: `auth`, `customer`, `los`, `lms`, `collections`, `findna`, `notifications`, `gateway` and expand iteratively.

Next steps:
- Create OpenAPI contracts for core services (auth, los, lms, collections) and start implementing the `auth` service.
