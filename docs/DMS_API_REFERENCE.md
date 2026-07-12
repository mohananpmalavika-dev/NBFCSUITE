# DMS API Reference

## Base URL
```
http://localhost:8000/api/v1/dms
```

## Authentication
All endpoints require JWT Bearer token:
```http
Authorization: Bearer <jwt_token>
```

---

## 📄 Document Operations

### Create Document
```http
POST /documents
Content-Type: multipart/form-data
```

**Form Parameters:**
- `title` (required): Document title
- `document_type` (required): contract|policy|procedure|form|report|invoice|receipt|certificate|letter|memorandum|agreement|notice|circular|other
- `category` (required): legal|financial|hr|operations|compliance|marketing|it|customer|vendor|internal
- `access_level` (optional): public|internal|confidential|restricted|secret (default: internal)
- `description` (optional): Document description
- `department` (optional): Department name
- `reference_number` (optional): External reference
- `file` (optional): File to upload

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "document_number": "DOC-20260712123456-ABC123",
    "title": "Contract Agreement",
    "document_type": "contract",
    "category": "legal",
    "status": "draft",
    "version_number": 1,
    "file_name": "contract.pdf",
    "file_size": 1024000,
    "owner_id": "uuid",
    "created_at": "2026-07-12T10:30:00Z"
  }
}
```

### Get Document
```http
GET /documents/{id}
```

**Response:** Same as create document response

### Update Document
```http
PUT /documents/{id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "status": "approved",
  "tags": ["important", "urgent"]
}
```

### Delete Document (Soft Delete)
```http
DELETE /documents/{id}
```

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

### Search Documents
```http
POST /documents/search
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "contract",
  "document_type": "contract",
  "category": "legal",
  "status": "approved",
  "access_level": "confidential",
  "department": "Legal",
  "owner_id": "uuid",
  "from_date": "2026-01-01T00:00:00Z",
  "to_date": "2026-12-31T23:59:59Z",
  "expiring_soon": false,
  "page": 1,
  "page_size": 20
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "documents": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### List Documents
```http
GET /documents?query=contract&document_type=contract&page=1&page_size=20
```

### Download Document
```http
GET /documents/{id}/download
```

**Response:** File stream with headers:
- `Content-Type`: application/pdf (or appropriate MIME type)
- `Content-Disposition`: attachment; filename="document.pdf"

---

## 🔄 Version Management

### Upload New Version
```http
POST /documents/{id}/versions
Content-Type: multipart/form-data
```

**Form Parameters:**
- `file` (required): File to upload
- `version_notes` (optional): Notes about this version
- `is_major_version` (optional): true|false (default: false)
- `changes_summary` (optional): Summary of changes

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "document_id": "uuid",
    "version_number": 2,
    "file_name": "document.pdf",
    "file_size": 1024000,
    "version_notes": "Updated section 5",
    "is_major_version": true,
    "uploaded_by": "uuid",
    "created_at": "2026-07-12T10:30:00Z"
  }
}
```

### Get All Versions
```http
GET /documents/{id}/versions
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "version_number": 2,
      "file_name": "document.pdf",
      "file_size": 1024000,
      "is_major_version": true,
      "created_at": "2026-07-12T10:30:00Z"
    },
    {
      "id": "uuid",
      "version_number": 1,
      "file_name": "document.pdf",
      "file_size": 900000,
      "is_major_version": true,
      "created_at": "2026-07-01T10:30:00Z"
    }
  ]
}
```

---

## ⚙️ Workflow Operations

### Create Workflow
```http
POST /workflows?document_id={uuid}
Content-Type: application/json
```

**Request Body:**
```json
{
  "workflow_name": "Contract Approval",
  "workflow_type": "approval",
  "description": "Standard contract approval process",
  "steps": [
    {
      "step_number": 1,
      "step_name": "Legal Review",
      "approver_id": "uuid",
      "approver_role": "Legal Manager",
      "due_date": "2026-07-15T23:59:59Z"
    },
    {
      "step_number": 2,
      "step_name": "Management Approval",
      "approver_id": "uuid",
      "due_date": "2026-07-20T23:59:59Z"
    }
  ],
  "is_sequential": true,
  "require_all_approvals": true,
  "priority": "high",
  "due_date": "2026-07-20T23:59:59Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "document_id": "uuid",
    "workflow_name": "Contract Approval",
    "status": "pending",
    "current_step": 1,
    "total_steps": 2,
    "initiated_by": "uuid",
    "approvals": [...]
  }
}
```

### Get Workflow
```http
GET /workflows/{id}
```

### Get Document Workflows
```http
GET /documents/{id}/workflows
```

### Get Pending Approvals
```http
GET /workflows/pending-approvals?approver_id={uuid}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "workflow_id": "uuid",
      "step_number": 1,
      "step_name": "Legal Review",
      "approver_id": "uuid",
      "status": "pending",
      "due_date": "2026-07-15T23:59:59Z",
      "created_at": "2026-07-12T10:30:00Z"
    }
  ]
}
```

### Process Approval
```http
POST /approvals/{id}/process
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "approved",
  "comments": "Approved with minor suggestions",
  "attachments": ["file1.pdf", "file2.pdf"]
}
```

**Status Options:** `approved`, `rejected`, `delegated`, `skipped`

### Delegate Approval
```http
POST /approvals/{id}/delegate
Content-Type: application/json
```

**Request Body:**
```json
{
  "delegate_to": "uuid",
  "reason": "Out of office"
}
```

### Cancel Workflow
```http
DELETE /workflows/{id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "reason": "Document no longer required"
}
```

---

## 🔐 Workflow Templates

### Create Template
```http
POST /workflow-templates
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Standard Contract Approval",
  "description": "3-step contract approval process",
  "workflow_type": "approval",
  "applicable_document_types": ["contract", "agreement"],
  "applicable_categories": ["legal", "financial"],
  "steps": [
    {"step_number": 1, "step_name": "Legal Review", "role": "Legal Manager"},
    {"step_number": 2, "step_name": "Finance Review", "role": "Finance Manager"},
    {"step_number": 3, "step_name": "Final Approval", "role": "Director"}
  ],
  "is_sequential": true,
  "require_all_approvals": true
}
```

### Get Templates
```http
GET /workflow-templates?workflow_type=approval
```

---

## ✍️ Signature Operations

### Request Signature
```http
POST /signatures
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_id": "uuid",
  "signer_id": "uuid",
  "signature_type": "simple",
  "expires_at": "2026-07-19T23:59:59Z"
}
```

**Signature Types:** `simple`, `basic`, `advanced`, `qualified`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "document_id": "uuid",
    "signer_id": "uuid",
    "signer_name": "John Doe",
    "signer_email": "john@example.com",
    "signature_type": "simple",
    "status": "pending",
    "requested_at": "2026-07-12T10:30:00Z",
    "expires_at": "2026-07-19T23:59:59Z"
  }
}
```

### Get Signature
```http
GET /signatures/{id}
```

### Process Signature
```http
POST /signatures/{id}/process
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "signed",
  "signature_data": "base64_encoded_signature",
  "verification_method": "otp"
}
```

**Status Options:** `signed`, `rejected`

### Get Document Signatures
```http
GET /documents/{id}/signatures
```

### Get Pending Signatures
```http
GET /signatures/pending?signer_id={uuid}
```

### Cancel Signature Request
```http
DELETE /signatures/{id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "reason": "Document changed"
}
```

### Resend Signature Request
```http
POST /signatures/{id}/resend
```

### Verify Signature
```http
GET /signatures/{id}/verify
```

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "signature_id": "uuid",
    "signer_name": "John Doe",
    "signed_at": "2026-07-12T15:30:00Z",
    "hash_valid": true,
    "certificate_valid": true
  }
}
```

---

## 🔒 Permission Operations

### Grant Permission
```http
POST /permissions
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_id": "uuid",
  "user_id": "uuid",
  "role_id": null,
  "department": null,
  "can_view": true,
  "can_download": true,
  "can_edit": false,
  "can_delete": false,
  "can_share": false,
  "can_approve": false,
  "valid_from": "2026-07-12T00:00:00Z",
  "valid_until": "2026-12-31T23:59:59Z",
  "grant_reason": "Required for review"
}
```

**Note:** At least one of `user_id`, `role_id`, or `department` must be specified.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "document_id": "uuid",
    "user_id": "uuid",
    "can_view": true,
    "can_download": true,
    "granted_by": "uuid",
    "created_at": "2026-07-12T10:30:00Z"
  }
}
```

### Revoke Permission
```http
DELETE /permissions/{id}
```

### Get Document Permissions
```http
GET /documents/{id}/permissions
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "can_view": true,
      "can_download": true,
      "can_edit": false,
      "valid_until": "2026-12-31T23:59:59Z"
    }
  ]
}
```

### Check Permission
```http
GET /permissions/check?document_id={uuid}&user_id={uuid}&permission_type=view
```

**Permission Types:** `view`, `download`, `edit`, `delete`, `share`, `approve`

**Response:**
```json
{
  "success": true,
  "data": {
    "has_permission": true
  }
}
```

### Bulk Grant Permissions
```http
POST /permissions/bulk-grant
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_ids": ["uuid1", "uuid2", "uuid3"],
  "user_id": "uuid",
  "can_view": true,
  "can_download": true,
  "can_edit": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "permissions_created": 3
  }
}
```

---

## 💬 Comment Operations

### Add Comment
```http
POST /comments
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_id": "uuid",
  "version_id": "uuid",
  "parent_comment_id": null,
  "comment_text": "Please review section 3",
  "comment_type": "general",
  "page_number": 5,
  "position_x": 100,
  "position_y": 200
}
```

**Comment Types:** `general`, `question`, `issue`, `suggestion`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "document_id": "uuid",
    "comment_text": "Please review section 3",
    "author_id": "uuid",
    "is_resolved": false,
    "created_at": "2026-07-12T10:30:00Z"
  }
}
```

---

## 📊 Statistics & Dashboard

### Get Statistics
```http
GET /statistics
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_documents": 500,
    "by_status": {
      "draft": 50,
      "approved": 400,
      "rejected": 30,
      "archived": 20
    },
    "by_type": {
      "contract": 100,
      "policy": 80,
      "report": 200
    },
    "by_category": {
      "legal": 150,
      "financial": 200,
      "hr": 150
    },
    "expiring_soon": 15,
    "pending_approvals": 25,
    "pending_signatures": 10
  }
}
```

### Get My Documents
```http
GET /my-documents?page=1&page_size=20
```

### Get Dashboard
```http
GET /dashboard
```

**Response:**
```json
{
  "success": true,
  "data": {
    "statistics": {...},
    "pending_approvals_count": 5,
    "pending_signatures_count": 3,
    "recent_documents": {
      "documents": [...],
      "total": 10
    }
  }
}
```

---

## 🔍 Search Query Examples

### Search by Text
```json
{
  "query": "contract agreement",
  "page": 1,
  "page_size": 20
}
```

### Filter by Type & Status
```json
{
  "document_type": "contract",
  "status": "approved",
  "page": 1
}
```

### Filter by Date Range
```json
{
  "from_date": "2026-01-01T00:00:00Z",
  "to_date": "2026-06-30T23:59:59Z"
}
```

### Find Expiring Documents
```json
{
  "expiring_soon": true,
  "status": "approved"
}
```

### Filter by Owner & Department
```json
{
  "owner_id": "uuid",
  "department": "Legal",
  "category": "legal"
}
```

---

## 📝 Response Format

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {...}
  }
}
```

### Common Error Codes
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (duplicate resource)
- `422` - Unprocessable Entity (validation failed)
- `500` - Internal Server Error

---

## 🔄 Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 🎯 Rate Limiting

- **Rate Limit:** 1000 requests per hour per user
- **Burst Limit:** 100 requests per minute

**Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1689161234
```

---

## 🔗 Interactive Documentation

**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

Test all endpoints interactively with your JWT token!

---

**Version:** 1.0.0  
**Last Updated:** July 12, 2026  
**Base URL:** /api/v1/dms
