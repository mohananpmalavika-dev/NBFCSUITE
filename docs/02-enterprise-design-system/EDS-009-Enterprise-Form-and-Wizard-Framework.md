# EDS-009 — Enterprise Form & Wizard Framework (EFWF)

## Overview

Enterprise business processes rarely fit into a single screen. In modern financial platforms, creation and update flows are usually guided experiences that move the user through a clear sequence of decisions, validations, review steps, and approvals.

This framework defines how ARTH.OS should structure forms and wizards so that every create, edit, onboarding, and approval experience feels consistent, guided, and professional.

---

## Philosophy

Enterprise users should not face long, intimidating forms with 150 fields on a single page.

Instead, the system should guide the user through a business process:

Business Process → Business Wizard → Review → Approval → Complete

The experience should feel like a structured workflow rather than a data-entry chore.

---

## Universal Wizard Architecture

Every wizard should follow the same structure:

Wizard → Steps → Sections → Fields → Validation → Review → Submit

This allows the platform to reuse the same interaction model across employee onboarding, customer onboarding, loan origination, branch creation, journal posting, and more.

---

## Universal Layout

A standard wizard layout should include:

- Breadcrumb or process context
- Header with title and progress
- Current step body
- Optional sidebar for guidance, checklist, warnings, attachments, and AI tips
- Footer with cancel, save draft, previous, next, and submit actions

This layout should adapt smoothly between desktop and mobile.

---

## Wizard Types

### Linear Wizard

Used when the process follows a fixed sequence.

Example:

Employee onboarding

### Branching Wizard

Used when the next step depends on earlier answers.

Example:

Loan origination with gold loan vs non-gold loan branching

### Nested Wizard

Used when a business object contains smaller child objects that must be completed in a logical sequence.

Example:

Customer → Nominees → Addresses → Employment

### Review Wizard

Used when an explicit review and approval stage is required before completion.

Example:

Summary → Validation → Approval → Submit

---

## Standard Wizard Structure

Every wizard should include the following regions:

- Header
- Progress indicator
- Body
- Sidebar
- Footer

### Header

The header should include:

- Title
- Description
- Progress status
- Save draft action

### Progress

Progress should be shown in a compact and clear way:

- Desktop: step indicator with numbered steps
- Mobile: short summary such as “Step 2 of 5”

### Body

The body should contain:

- Sections
- Fields
- Validation feedback
- Help content

### Sidebar

The sidebar should show:

- Checklist
- Completion status
- Warnings
- Attachments
- AI guidance tips

On mobile this should be collapsed or hidden.

### Footer

The footer should always include:

- Cancel
- Save draft
- Previous
- Next
- Submit

---

## Standard Wizard Flow

A typical wizard should follow this flow:

Information → Validation → Review → Approval → Submit

---

## Step Rules

Each step should remain concise and focused.

Recommended maximum:

- 8–10 fields per step

This avoids long scrolling and improves completion rates.

---

## Sections

The framework should encourage logical grouping of fields.

Examples:

### Employee wizard

- Personal
- Employment
- Organization
- Salary
- Documents
- Review

### Customer wizard

- Basic
- Address
- Identity
- KYC
- Nominee
- Review

### Loan wizard

- Customer
- Loan
- Collateral
- Documents
- Approval
- Review

---

## Validation

Validation should happen at three levels.

### Client Validation

Immediate feedback for common input issues:

- Required field
- Length checks
- Format checks
- Email validation
- Phone validation

### Business Validation

Rules that reflect business logic:

- Age > 18
- Salary > loan amount
- Branch exists

### Server Validation

Rules that depend on backend state or uniqueness:

- PAN duplicate
- Aadhaar duplicate
- Customer already exists

---

## Autosave

Every wizard should autosave every 30 seconds.

The experience should support:

- Automatic saving in the background
- Recovery of draft content
- Resume from a previous draft

---

## Drafts and Resume

Every wizard should support draft creation.

Users should be able to:

- Save a draft
- Resume later
- Continue from an unfinished process

Example:

Employee wizard draft → Continue later

---

## Attachments

Every wizard should support attachments when needed.

Examples:

- Upload
- Camera capture
- Scanner support
- OCR preview
- Attachment list

---

## Document Checklist

A wizard should show a clear checklist of required documents.

Example for employee onboarding:

- Photo
- Aadhaar
- PAN
- Offer letter
- Degree

The checklist should be visually clear and update as documents are uploaded.

---

## AI Assistant

Every step should optionally include an AI assistant.

Examples:

- Explain this field
- Suggest designation
- Validate salary
- Summarize information

AI guidance should assist the user without overpowering the core workflow.

---

## Dynamic Forms

The framework should support dynamic form behavior.

Example:

- If nationality = Indian, show PAN and Aadhaar fields.
- If nationality = Foreign, show Passport and Visa fields.

Dynamic content should reduce unnecessary questions and improve completion quality.

---

## Smart Defaults

The framework should use intelligent defaults when available.

Examples:

- Branch auto-selects department
- Department auto-selects manager
- Standard values are prefilled when appropriate

This should improve speed while preserving user control.

---

## Review Screen

The review screen should present a grouped summary of everything entered.

Suggested grouping:

- Personal
- Employment
- Salary
- Documents

The review step should clearly show:

- Completed sections
- Validation status
- Warnings
- Missing information

---

## Approval

If the process requires approval, the wizard should support a workflow handoff.

Flow:

Submit → Workflow → Pending → Approved → Created

If approval is not required, the wizard can complete directly.

---

## Success State

On completion, the wizard should show a clear success state.

Example:

Employee created successfully.

Actions may include:

- Open profile
- Print
- Create another

---

## Wizard Components

The reusable component library should include:

- Wizard
- WizardHeader
- WizardSteps
- WizardSidebar
- WizardFooter
- WizardReview
- WizardSummary
- WizardValidation
- WizardAttachments
- WizardApproval
- WizardSuccess
- WizardError

---

## Form Components

The form system should include reusable building blocks such as:

- FormProvider
- Section
- Field
- FieldGroup
- Address
- Contact
- Money
- Percentage
- Interest
- Currency
- Phone
- Email
- DateTime
- OTP
- Signature
- Upload
- Barcode
- QR
- OCR

---

## Field States

Every field should support standard interaction states:

- Default
- Hover
- Focus
- Error
- Success
- Disabled
- Readonly

---

## Error Handling

Errors should be helpful and human-readable.

Instead of a generic error, the system should say things like:

- Employee code already exists. Please choose another code.

This improves trust and reduces user confusion.

---

## Accessibility

The framework should support:

- Keyboard navigation
- Screen readers
- High contrast mode
- Labels and descriptions
- Clear error messaging
- Logical focus order

---

## Keyboard Support

Suggested shortcuts:

- Tab: next field
- Shift + Tab: previous field
- Ctrl + S: save draft
- Ctrl + Enter: submit
- Esc: cancel or close dialog

---

## Mobile Experience

On desktop, the wizard should use a wider horizontal layout.

On mobile, it should shift to a vertical, single-stepper experience with minimal friction.

---

## Performance Targets

The framework should target:

- Next step: under 200 ms
- Validation: under 100 ms
- Autosave: background process
- Draft resume: under 1 second
- Submit: under 2 seconds

---

## Folder Structure

A reference implementation should follow this structure:

packages/design-system/wizard/
├── Wizard/
├── WizardHeader/
├── WizardSteps/
├── WizardSidebar/
├── WizardFooter/
├── WizardReview/
├── WizardValidation/
├── WizardAttachments/
├── WizardApproval/
├── WizardSuccess/
├── WizardError/
├── hooks/
├── types/
├── utils/
└── stories/

---

## Backend Contract

Every wizard should use a common API pattern:

- GET /draft/{id}
- POST /draft
- PUT /step/{id}
- POST /validate
- POST /submit
- GET /review

This keeps the flow consistent across modules and avoids one-off implementations.

---

## Workflow Integration

Every wizard should support optional workflow integration.

Two common modes:

- Create → Submit → Approval → Complete
- Create → Complete

The framework should support both depending on the business rule.

---

## Banking Extensions

The core framework should support specialized templates for:

- Customer onboarding
- Employee onboarding
- Loan origination
- Gold loan intake
- Deposit opening
- Journal entry
- Branch creation
- Vendor onboarding
- Asset registration

These templates should inherit the shared wizard system while adding domain-specific steps and validations.

---

## Acceptance Checklist

A wizard is complete when it:

- Uses the shared wizard framework
- Supports drafts and autosave
- Validates at client, business, and server levels
- Supports attachments and document checklists
- Integrates with workflows and approvals
- Is fully keyboard accessible
- Works on desktop, tablet, and mobile
- Publishes audit events for create, update, submit, and approval

---

## Deliverable Status

- EDS-001 Design Principles: Complete
- EDS-002 Information Architecture: Complete
- EDS-003 Enterprise Navigation: Complete
- EDS-004 Enterprise App Shell: Complete
- EDS-005 Design Tokens: Complete
- EDS-006 Enterprise Component Library: Complete
- EDS-007 Dashboard Framework: Complete
- EDS-008 Enterprise Data Grid: Complete
- EDS-009 Enterprise Form & Wizard Framework: Complete
- EDS-010 Workflow & Approval UX Framework: Next

---

## Recommendation

The next specification should be EDS-010 — Workflow & Approval UX Framework. This is where ARTH.OS begins to differentiate itself from conventional NBFC software by defining a consistent approval experience for complex enterprise processes.
