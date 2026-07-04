# EDS-009 — Enterprise Form & Wizard Framework (EFWF)

## Plan Steps
1. Analyze repo + existing EDS-009 wizard implementation.
2. Extend wizard types to support a unified API contract for drafts/resume/validation/submit/review.
3. Upgrade `EnterpriseWizard` component props to accept draft/session + optional API handler.
4. Fix build issues introduced during refactor.
5. Wire autosave/save draft to `apiHandler` when provided; keep simulated fallback otherwise.
6. Add validation execution flow (client/business/server) before next-step/submit.
7. Ensure attachments + document checklist are driven by wizard state (not only props).
8. Integrate review + approval states with audit events.
9. Add responsive/mobile improvements where needed.
10. Run `apps/customer-app` lint/typecheck/build.

## Progress
- [x] Step 1: Analyzed existing EDS-009 wizard components.
- [x] Step 2: Extended `types.ts` with draft/api handler types.
- [x] Step 3: Updated `EnterpriseWizard` props to accept `initialDraftId` and `apiHandler`.
- [!] Step 4: Fix build issues from refactor (currently `WizardApiHandler` import removed).


