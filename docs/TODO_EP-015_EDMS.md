# TODO_EP-015_EDMS

## Goal
Implement EP-015 — Enterprise Document Management System (EDMS) core lifecycle in `services/document`.

## Steps
1. Refactor `services/document/app/main.py` into router/service/model structure.
2. Implement DB schema for EDMS core:
   - document (stable identity)
   - document_version (V1/V2/… + rollback)
   - document_metadata (initial)
   - document_ocr (initial)
   - document_ai (initial)
   - document_workflow (initial)
   - document_signature (initial)
   - document_retention (initial)
   - document_audit (initial)
3. Add migrations to support the schema changes (or compatible staging if needed).
4. Update API:
   - POST /api/v1/documents (register)
   - POST /api/v1/documents/{id}/upload (creates version)
   - POST /api/v1/documents/{id}/ocr (stub pipeline + store outputs)
   - POST /api/v1/documents/{id}/classify (stub + store outputs)
   - POST /api/v1/documents/{id}/approve (workflow transition)
   - POST /api/v1/documents/{id}/sign (signature transition)
   - PUT /api/v1/documents/{id}/archive or retention evaluation
   - GET  /api/v1/documents/{id}/versions
   - GET  /api/v1/documents/{id}/360
   - GET  /api/v1/documents/search (MVP)
5. Add event/audit writes on each transition.
6. Ensure backward compatibility where possible (existing endpoints should either delegate or remain working).
7. Update `design/openapi-document.yaml` to reflect new routes.
8. Add/extend tests for the core lifecycle endpoints.
9. Run the document service locally and smoke-test the main flows.

