# EDS-010 — Workflow & Approval UX Framework

## Overview

A strong workflow and approval framework is one of the clearest differentiators between conventional NBFC software and a mature enterprise platform. In ARTH.OS, approval logic should not be hardcoded inside each business module. Instead, HRMS, Accounting, Lending, Deposits, Procurement, Treasury, Forex, Risk, and other modules should all use the same workflow engine.

This framework defines how approvals should be represented, configured, executed, monitored, and audited across the platform.

---

## Vision

Every business transaction in ARTH.OS should be represented as a configurable workflow.

Examples:

- Employee creation
- Customer creation
- Loan approval
- Gold loan release
- Journal approval
- Branch creation
- Leave approval
- Payroll approval
- Expense approval
- Vendor approval
- Treasury transfer

No approval logic should be hardcoded into individual modules.

---

## Workflow Architecture

The platform should treat workflow execution as a shared service layer composed of the following capabilities:

- Workflow engine
- Rules engine
- Approval engine
- Notification engine
- Audit engine

This keeps approval behavior consistent and configurable across all business domains.

---

## Workflow Lifecycle

A workflow should move through a standard lifecycle:

Draft → Submit → Validation → Workflow Started → Approval → Approved → Business Action → Completed

Alternative paths should include:

- Rejected
- Returned
- Cancelled
- Expired
- Escalated

---

## Workflow Types

### Sequential Workflow

Used when approvals happen one after another.

Example:

Employee → Manager → HR → Finance → CEO

### Parallel Workflow

Used when multiple reviewers act at the same time.

Example:

Loan → Legal, Risk, Finance (parallel) → Disbursement

### Conditional Workflow

Used when the approval path changes based on business conditions.

Example:

If loan amount is below threshold, approve with branch manager. If above threshold, escalate to regional manager and credit committee.

### Dynamic Workflow

Used when the workflow is generated from runtime context such as:

- Rules
- Branch
- Product
- Amount
- Customer risk
- Role

---

## Workflow Components

Every workflow should be composed of:

- Workflow
- Stages
- Tasks
- Approvers
- Actions
- Conditions
- Notifications
- Audit trail

---

## Approval Inbox

Every user should have a single approval inbox that centralizes pending work.

Suggested sections:

- Approvals
- Today’s items
- Overdue items
- Delegated items
- Completed items
- Rejected items

---

## Approval Card

Each approval should appear as a compact card with the following information:

- Transaction title
- Transaction ID
- Submitter
- Current stage
- SLA status
- Approve / Reject / Return / Delegate actions

Example:

Employee Creation

Submitted by Rahul

Pending Manager Approval

SLA: 18 hours left

---

## Approval Timeline

Each workflow should show a visible timeline.

Suggested states:

- Submitted
- Manager reviewed
- HR reviewed
- Finance reviewed
- Completed

Visual treatment:

- Completed stages: green
- Current stage: blue
- Rejected: red
- Pending: gray

---

## Workflow Viewer

Every transaction should be able to display its workflow in context.

Suggested sections:

- Workflow
- Timeline
- Audit trail
- Comments
- Attachments

---

## Workflow Designer

The platform should include a low-code workflow designer for business users and administrators.

Example flow:

Start → Validation → Manager Approval → HR Approval → Finance Approval → Complete

The designer should support drag-and-drop nodes and configuration panels.

---

## Workflow Nodes

A standard workflow designer should support node types such as:

- Start
- Task
- Approval
- Decision
- Parallel Merge
- Notification
- Delay
- Script
- End

---

## Approval Actions

Approvers should be able to perform standard actions:

- Approve
- Reject
- Return
- Request changes
- Delegate
- Escalate
- Put on hold

Every action should be audited and visible in the timeline.

---

## Delegation

The system should support delegation for temporary or permanent absences.

Examples:

- Manager on leave → delegate to assistant manager
- Temporary delegation for a date range
- Automatic expiry after the delegation period

---

## Escalation

The framework should support escalation logic for delayed approvals.

Example:

If a manager does not act within 24 hours, send reminders and escalate to a regional manager.

Multiple escalation levels should be supported.

---

## SLA Indicators

Every approval should show SLA state clearly.

Suggested visual states:

- Green: safe
- Amber: approaching SLA
- Red: breached

Examples:

- 12 hours remaining
- 2 hours remaining
- SLA breached

---

## Workflow Comments

Approvers should be able to add comments and collaborate on a transaction.

Examples:

- Need additional KYC
- Uploaded supporting documents
- Approved

Users should also be able to:

- Mention other users
- Attach files
- Link related documents

---

## Audit Timeline

Every workflow change should be stored in an immutable audit log.

Example:

- 09:10 Submitted
- 09:22 Approved
- 09:24 Finance assigned
- 10:01 Completed

---

## Notification Integration

Workflow events should automatically trigger notifications through:

- In-app notification
- Email
- SMS
- WhatsApp (optional)
- Push notification

These should be configurable by workflow and event type.

---

## Workflow Search

Users should be able to search workflow items by:

- Workflow ID
- Transaction
- Customer
- Employee
- Status
- Approver
- Branch
- Date

---

## Dashboard Widgets

The framework should provide reusable dashboard widgets such as:

- My approvals
- Pending approvals
- Overdue approvals
- Workflow status
- Escalations
- Rejected today
- Average approval time

---

## Workflow Analytics

Standard analytics should include:

- Average approval time
- SLA compliance
- Approval rate
- Rejection rate
- Escalation count
- Bottleneck stage
- Workflow volume
- Approval by user
- Approval by branch

---

## AI Integration

Workflow screens should expose AI-supported assistance.

Examples:

- Summarize this workflow
- Explain why it is delayed
- Recommend the next approver
- Predict an SLA breach
- Identify bottlenecks

---

## Security

Only authorized users should be able to:

- View a workflow
- Approve or reject a workflow
- Delegate work
- Configure workflow definitions

Approval actions should always require permission checks.

---

## Events

The framework should publish standardized workflow events such as:

- WORKFLOW_CREATED
- WORKFLOW_STARTED
- TASK_ASSIGNED
- TASK_COMPLETED
- APPROVAL_GRANTED
- APPROVAL_REJECTED
- APPROVAL_RETURNED
- WORKFLOW_ESCALATED
- WORKFLOW_CANCELLED
- WORKFLOW_COMPLETED

---

## API Contract

Every module should use a common workflow API contract:

- POST /workflow/start
- GET /workflow/{id}
- POST /workflow/action
- GET /workflow/tasks
- GET /workflow/history
- POST /workflow/delegate
- POST /workflow/escalate

---

## Folder Structure

A reference implementation should follow this structure:

packages/design-system/workflow/
├── WorkflowViewer/
├── WorkflowTimeline/
├── ApprovalCard/
├── ApprovalInbox/
├── ApprovalActions/
├── WorkflowDesigner/
├── WorkflowAnalytics/
├── SLAIndicator/
├── Comments/
├── Attachments/
├── AuditTimeline/
├── hooks/
├── types/
└── stories/

---

## UX Standards

Every workflow screen should include:

- Workflow status badge
- Timeline
- Current approver
- SLA indicator
- Action buttons
- Comments
- Attachments
- Audit history
- AI summary

---

## Acceptance Criteria

The workflow framework is complete when:

- Every module uses the same workflow engine
- Workflow definitions are configurable
- Sequential, parallel, conditional, and dynamic workflows are supported
- Approval actions are standardized
- SLA monitoring and escalation are built in
- Audit logs are immutable
- Notifications are automatic
- Workflow analytics are available

---

## Deliverable Status

- EDS-001 Design Principles: Complete
- EDS-002 Information Architecture: Complete
- EDS-003 Enterprise Navigation: Complete
- EDS-004 Enterprise App Shell: Complete
- EDS-005 Design Tokens: Complete
- EDS-006 Component Library: Complete
- EDS-007 Dashboard Framework: Complete
- EDS-008 Enterprise Data Grid: Complete
- EDS-009 Form & Wizard Framework: Complete
- EDS-010 Workflow & Approval UX Framework: Complete

---

## Phase 0 Status

The design-system phase is now complete at approximately 70% overall progress. The next step is to move into platform foundations and enterprise modules.

---

## Platform Next Steps

The next platform milestone should be:

1. EOM — Enterprise Organization Management
2. IAM — Identity & Access Management
3. Workflow engine backend
4. Rules engine
5. Notification engine
6. Document management
7. Audit engine
8. Scheduler and job engine

## Recommendation

The next module to implement should be EOM v2.0, redesigned around the new enterprise design system. This will create the organizational hierarchy and shared platform foundation that all other modules can reuse.
