# Phase 10: Document Management - Technical Documentation

**Version:** 1.0.0  
**Date:** July 3, 2026  
**Status:** Complete

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Frontend Components](#frontend-components)
6. [Security & Compliance](#security--compliance)
7. [Integration Guide](#integration-guide)

---

## Overview

Phase 10 implements a comprehensive enterprise-grade document management system with version control, OCR capabilities, approval workflows, retention policies, and compliance tracking.

### Key Features

- **Centralized Repository**: Unified document storage with advanced search and filtering
- **Version Control**: Complete version history with restore capabilities
- **OCR & Data Extraction**: Automated text extraction from documents
- **Workflow Management**: Configurable approval workflows with escalation
- **Template Management**: Document generation from templates
- **Compliance & Retention**: Automated retention policies per regulatory requirements
- **Access Control & Audit**: Complete audit trail of all document access
- **Sharing & Collaboration**: Secure document sharing with expiration and access limits

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Management Layer                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Repository  │  │   Workflow   │  │  Compliance  │      │
│  │  Management  │  │   Engine     │  │   Engine     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Version    │  │     OCR      │  │   Template   │      │
│  │   Control    │  │   Service    │  │   Generator  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                      Storage Layer                           │
│  ┌──────────────────────────────────────────────────┐       │
│  │  PostgreSQL (Metadata) + Cloud Storage (Files)   │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema Overview

**11 Core Tables:**
1. `gold_document_categories` - Document classification
2. `gold_documents` - Core document records
3. `gold_document_versions` - Version history
4. `gold_document_metadata` - Flexible metadata
5. `gold_document_templates` - Document templates
6. `gold_document_workflows` - Workflow definitions
7. `gold_document_approvals` - Approval tracking
8. `gold_document_tags` - Document tags
9. `gold_document_tag_mappings` - Document-tag relationships
10. `gold_document_access_logs` - Access audit trail
11. `gold_document_retention_policies` - Compliance policies
12. `gold_document_shares` - Sharing and external access

---

## Database Schema

### 1. Document Categories

```sql
CREATE TABLE gold_document_categories (
    category_id UUID PRIMARY KEY,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(200) NOT NULL,
    parent_category_id UUID REFERENCES gold_document_categories(category_id),
    retention_period_days INTEGER,
    requires_approval BOOLEAN DEFAULT FALSE,
    requires_ocr BOOLEAN DEFAULT FALSE,
    metadata_schema JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features:**
- Hierarchical category structure
- Configurable retention periods
- Custom metadata schemas per category
- Approval and OCR requirements

### 2. Documents

```sql
CREATE TABLE gold_documents (
    document_id UUID PRIMARY KEY,
    document_number VARCHAR(50) UNIQUE NOT NULL,
    category_id UUID REFERENCES gold_document_categories(category_id),
    document_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    file_name VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(128),
    storage_path VARCHAR(1000) NOT NULL,
    storage_status VARCHAR(20) DEFAULT 'uploaded',
    current_version INTEGER DEFAULT 1,
    entity_type VARCHAR(50),
    entity_id UUID,
    ocr_text TEXT,
    extracted_data JSONB,
    expiry_date DATE,
    is_encrypted BOOLEAN DEFAULT FALSE,
    encryption_key_id VARCHAR(100),
    is_deleted BOOLEAN DEFAULT FALSE,
    uploaded_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_documents_number` on document_number
- `idx_documents_category` on category_id
- `idx_documents_type` on document_type
- `idx_documents_entity` on (entity_type, entity_id)
- `idx_documents_storage_status` on storage_status
- `idx_documents_deleted` on is_deleted
- `idx_documents_expiry` on expiry_date

### 3. Document Versions

```sql
CREATE TABLE gold_document_versions (
    version_id UUID PRIMARY KEY,
    document_id UUID REFERENCES gold_documents(document_id),
    version_number INTEGER NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    file_hash VARCHAR(128),
    storage_path VARCHAR(1000) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    change_description TEXT,
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, version_number)
);
```

**Features:**
- Complete version history
- Change tracking
- Version restoration
- Storage optimization

### 4. Document Workflows

```sql
CREATE TABLE gold_document_workflows (
    workflow_id UUID PRIMARY KEY,
    workflow_code VARCHAR(50) UNIQUE NOT NULL,
    workflow_name VARCHAR(200) NOT NULL,
    category_id UUID REFERENCES gold_document_categories(category_id),
    workflow_type VARCHAR(50) NOT NULL,
    workflow_steps JSONB NOT NULL,
    escalation_rules JSONB,
    sla_hours INTEGER,
    is_mandatory BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Workflow Step Structure:**
```json
{
  "steps": [
    {
      "step": 1,
      "role": "loan_officer",
      "action": "review",
      "sequence": 1,
      "is_parallel": false
    },
    {
      "step": 2,
      "role": "branch_manager",
      "action": "approve",
      "sequence": 2,
      "is_parallel": false
    }
  ]
}
```

### 5. Document Approvals

```sql
CREATE TABLE gold_document_approvals (
    approval_id UUID PRIMARY KEY,
    document_id UUID REFERENCES gold_documents(document_id),
    workflow_id UUID REFERENCES gold_document_workflows(workflow_id),
    approval_number VARCHAR(50) UNIQUE NOT NULL,
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER NOT NULL,
    approval_status VARCHAR(20) DEFAULT 'pending',
    initiated_by UUID NOT NULL,
    assigned_to UUID,
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    approval_steps JSONB,
    is_escalated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Status Values:**
- `pending` - Awaiting review
- `approved` - Approved
- `rejected` - Rejected
- `returned` - Returned for revision

### 6. Retention Policies

```sql
CREATE TABLE gold_document_retention_policies (
    policy_id UUID PRIMARY KEY,
    policy_code VARCHAR(50) UNIQUE NOT NULL,
    policy_name VARCHAR(200) NOT NULL,
    category_id UUID,
    document_type VARCHAR(50),
    retention_period_days INTEGER NOT NULL,
    retention_trigger VARCHAR(50) NOT NULL,
    archive_after_days INTEGER,
    delete_after_retention BOOLEAN DEFAULT FALSE,
    compliance_regulation VARCHAR(100),
    auto_apply BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Retention Triggers:**
- `from_creation` - Start from document creation
- `from_loan_closure` - Start from loan closure date
- `from_last_access` - Start from last access date

---

## API Endpoints

### Document Categories

#### Create Category
```http
POST /api/v1/gold/documents/categories
Content-Type: application/json

{
  "category_code": "DOC_LOAN",
  "category_name": "Loan Documents",
  "description": "All loan-related documents",
  "retention_period_days": 2555,
  "requires_approval": true,
  "created_by": "user-id"
}
```

#### List Categories
```http
GET /api/v1/gold/documents/categories?is_active=true&skip=0&limit=50
```

#### Get Category
```http
GET /api/v1/gold/documents/categories/{category_id}
```

#### Update Category
```http
PUT /api/v1/gold/documents/categories/{category_id}
```

#### Delete Category
```http
DELETE /api/v1/gold/documents/categories/{category_id}
```

### Documents

#### Create Document
```http
POST /api/v1/gold/documents
Content-Type: application/json

{
  "category_id": "uuid",
  "document_type": "loan",
  "title": "Loan Agreement",
  "description": "Standard loan agreement",
  "file_name": "agreement.pdf",
  "file_size_bytes": 1048576,
  "mime_type": "application/pdf",
  "storage_path": "/uploads/2026/07/agreement.pdf",
  "entity_type": "loan",
  "entity_id": "loan-uuid",
  "uploaded_by": "user-id"
}
```

#### List Documents
```http
GET /api/v1/gold/documents?category_id=uuid&document_type=loan&skip=0&limit=50
```

**Query Parameters:**
- `category_id` - Filter by category
- `document_type` - Filter by type
- `entity_type` - Filter by entity type
- `entity_id` - Filter by entity ID
- `storage_status` - Filter by status
- `is_deleted` - Include deleted documents
- `search` - Full-text search
- `from_date` - Created after date
- `to_date` - Created before date
- `skip` - Pagination offset
- `limit` - Results per page

#### Get Document
```http
GET /api/v1/gold/documents/{document_id}
```

#### Update Document
```http
PATCH /api/v1/gold/documents/{document_id}
```

#### Delete Document (Soft Delete)
```http
DELETE /api/v1/gold/documents/{document_id}?deleted_by=user-id
```

### Document Versions

#### List Versions
```http
GET /api/v1/gold/documents/{document_id}/versions
```

#### Get Version
```http
GET /api/v1/gold/documents/{document_id}/versions/{version_number}
```

#### Restore Version
```http
POST /api/v1/gold/documents/{document_id}/versions/{version_number}/restore?restored_by=user-id
```

### Document Workflows

#### Create Workflow
```http
POST /api/v1/gold/documents/workflows
Content-Type: application/json

{
  "workflow_code": "WF_LOAN_APPROVAL",
  "workflow_name": "Loan Document Approval",
  "category_id": "uuid",
  "workflow_type": "approval",
  "workflow_steps": [...],
  "sla_hours": 48,
  "is_mandatory": true,
  "created_by": "user-id"
}
```

#### List Workflows
```http
GET /api/v1/gold/documents/workflows?category_id=uuid&is_active=true
```

### Document Approvals

#### Create Approval
```http
POST /api/v1/gold/documents/approvals
Content-Type: application/json

{
  "document_id": "uuid",
  "workflow_id": "uuid",
  "priority": "high",
  "initiated_by": "user-id"
}
```

#### List Approvals
```http
GET /api/v1/gold/documents/approvals?approval_status=pending&assigned_to=user-id
```

#### Take Action
```http
POST /api/v1/gold/documents/approvals/{approval_id}/action
Content-Type: application/json

{
  "action": "approve",
  "comments": "Approved",
  "action_by": "user-id"
}
```

**Actions:** `approve`, `reject`, `return`

### Bulk Operations

#### Bulk Tag Documents
```http
POST /api/v1/gold/documents/bulk/tag
Content-Type: application/json

{
  "document_ids": ["uuid1", "uuid2"],
  "tag_ids": ["tag-uuid1", "tag-uuid2"],
  "tagged_by": "user-id"
}
```

#### Bulk Delete Documents
```http
POST /api/v1/gold/documents/bulk/delete
Content-Type: application/json

{
  "document_ids": ["uuid1", "uuid2"],
  "deleted_by": "user-id",
  "deletion_reason": "Bulk deletion"
}
```

#### Bulk Move Documents
```http
POST /api/v1/gold/documents/bulk/move
Content-Type: application/json

{
  "document_ids": ["uuid1", "uuid2"],
  "target_category_id": "uuid",
  "moved_by": "user-id"
}
```

### OCR Operations

#### Extract Text (OCR)
```http
POST /api/v1/gold/documents/ocr/extract
Content-Type: application/json

{
  "document_id": "uuid",
  "ocr_language": "eng",
  "extract_tables": false,
  "extract_signatures": false
}
```

#### Reprocess OCR
```http
POST /api/v1/gold/documents/{document_id}/ocr/reprocess?ocr_language=eng
```

### Statistics

#### Document Statistics
```http
GET /api/v1/gold/documents/statistics/overview
```

**Response:**
```json
{
  "total_documents": 1250,
  "total_size_mb": 5420.5,
  "documents_by_category": {
    "Loan Documents": 450,
    "KYC Documents": 300
  },
  "documents_by_type": {
    "loan": 450,
    "kyc": 300
  },
  "recent_uploads": 45,
  "pending_approvals": 12,
  "documents_expiring_soon": 8
}
```

#### Workflow Statistics
```http
GET /api/v1/gold/documents/statistics/workflows
```

---

## Frontend Components

### 1. Document Repository (`/documents/repository`)

**Features:**
- Advanced search and filtering
- Multi-select with bulk operations
- Category, type, and status filters
- Date range filtering
- Pagination
- Download and share actions

**Key Components:**
- Search bar with full-text search
- Filter panel with multiple criteria
- Document table with sorting
- Bulk action toolbar
- Pagination controls

### 2. Document Upload (`/documents/upload`)

**Features:**
- Drag-and-drop file upload
- File validation
- Category and type selection
- Entity association (customer, loan, etc.)
- Tag assignment
- OCR option
- Metadata input

**Supported File Types:**
- PDF (.pdf)
- Word (.doc, .docx)
- Excel (.xls, .xlsx)
- Images (.jpg, .jpeg, .png)

**Validation:**
- File size limit: 10MB
- Allowed extensions check
- Required field validation

### 3. Document Viewer (`/documents/viewer`)

**Features:**
- Document preview (placeholder for actual implementation)
- Tabbed interface for details
- Version history with restore
- Metadata display
- Tag management
- Activity logs
- Download and print actions

**Tabs:**
- **Details**: Document properties
- **Versions**: Version history
- **Metadata**: Custom metadata
- **Tags**: Assigned tags
- **Activity**: Access logs

### 4. Workflow Management (`/documents/workflows`)

**Features:**
- Workflow dashboard with statistics
- Approval queue management
- Priority-based filtering
- Workflow progress tracking
- Action modal for review
- Escalation indicators

**Statistics:**
- Pending approvals
- Approved today
- Average approval time
- Escalated workflows

### 5. Template Management (`/documents/templates`)

**Features:**
- Template library
- Create/edit templates
- Template variables configuration
- Category and type assignment
- Template activation/deactivation

**Template Properties:**
- Template code and name
- Category and type
- File format (PDF, DOCX, XLSX, HTML)
- Storage path
- Variable definitions (JSON)

### 6. Compliance & Retention (`/documents/compliance`)

**Features:**
- Retention policy management
- Compliance dashboard
- Policy configuration
- Auto-apply rules
- Document compliance status

**Compliance Metrics:**
- Compliant documents
- Archivable documents
- Expired documents
- Unknown status

---

## Security & Compliance

### Access Control

**Document Permissions:**
- `view` - View document
- `download` - Download document
- `edit` - Modify document
- `delete` - Delete document
- `share` - Share with others
- `approve` - Approve in workflows

**Role-Based Access:**
```json
{
  "loan_officer": ["view", "download", "edit"],
  "branch_manager": ["view", "download", "approve"],
  "compliance_officer": ["view", "download", "delete"]
}
```

### Audit Trail

All document operations are logged:
- Document access (view, download, print)
- Modifications (create, update, delete)
- Approval actions
- Version changes
- Sharing activities

**Access Log Fields:**
- Action type
- User ID and role
- IP address and location
- Device information
- Timestamp
- Result (success/failure)

### Encryption

**At Rest:**
- Documents encrypted in storage
- AES-256 encryption
- Key management via KMS

**In Transit:**
- HTTPS/TLS 1.3
- Certificate pinning

### Compliance Features

**Regulatory Compliance:**
- RBI guidelines for document retention
- GDPR data protection
- SOC 2 audit requirements
- ISO 27001 compliance

**Retention Policies:**
- Automated retention rules
- Legal hold support
- Archive and deletion
- Compliance reporting

---

## Integration Guide

### External Document Storage

Connect to cloud storage providers:

```python
# Example: AWS S3 Integration
import boto3

s3_client = boto3.client('s3')

def upload_to_s3(file_path, bucket, key):
    s3_client.upload_file(file_path, bucket, key)
    return f"s3://{bucket}/{key}"

def download_from_s3(bucket, key, destination):
    s3_client.download_file(bucket, key, destination)
```

### OCR Service Integration

Integrate with OCR providers:

```python
# Example: Tesseract OCR
import pytesseract
from PIL import Image

def extract_text(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text
```

### E-Signature Integration

Connect to e-signature platforms:

```python
# Example: DocuSign Integration
from docusign_esign import ApiClient

def create_envelope(document_id, signers):
    api_client = ApiClient()
    # Configure envelope and send
    return envelope_id
```

### Webhook Notifications

Configure webhooks for document events:

```json
{
  "event": "document.uploaded",
  "document_id": "uuid",
  "category": "loan",
  "uploaded_by": "user-id",
  "timestamp": "2026-07-03T10:30:00Z"
}
```

**Supported Events:**
- `document.uploaded`
- `document.approved`
- `document.expired`
- `document.shared`
- `workflow.completed`

---

## Performance Considerations

### Optimization Strategies

1. **Pagination**: Use `skip` and `limit` for large result sets
2. **Caching**: Cache frequently accessed documents
3. **Lazy Loading**: Load document preview on demand
4. **Compression**: Compress large files before storage
5. **Indexing**: Proper database indexes for fast queries
6. **CDN**: Use CDN for document delivery

### Scalability

- **Horizontal Scaling**: Stateless API design
- **Load Balancing**: Distribute requests across servers
- **Database Sharding**: Partition by document category
- **Async Processing**: Queue-based OCR and uploads

---

## Troubleshooting

### Common Issues

**Issue: Document upload fails**
- Check file size limits
- Verify allowed file types
- Check storage permissions
- Review network connectivity

**Issue: OCR not working**
- Verify OCR service configuration
- Check image quality
- Ensure supported file format
- Review OCR logs

**Issue: Workflow stuck**
- Check workflow configuration
- Verify assigned users
- Review escalation rules
- Check SLA settings

---

## API Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 413 | Payload Too Large | File size exceeds limit |
| 500 | Internal Server Error | Server error |

---

## Support & Resources

- **API Documentation**: `/api/v1/gold/docs`
- **Support Email**: support@nbfcsuite.com
- **Developer Forum**: https://forum.nbfcsuite.com
- **Status Page**: https://status.nbfcsuite.com

---

**Document Version**: 1.0.0  
**Last Updated**: July 3, 2026  
**Maintained By**: NBFC Suite Development Team
