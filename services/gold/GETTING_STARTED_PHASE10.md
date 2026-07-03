# Getting Started with Phase 10: Document Management

**Quick Start Guide**  
**Version:** 1.0.0  
**Last Updated:** July 3, 2026

---

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Basic Usage](#basic-usage)
4. [Common Workflows](#common-workflows)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- PostgreSQL 14+ running
- Python 3.10+
- Node.js 18+
- Storage service (AWS S3, Azure Blob, or local filesystem)

### Database Setup

1. **Run the migration:**

```bash
cd infra/migrations
psql -U nbfc_user -d nbfcsuite -f 027_document_management.sql
```

2. **Verify tables created:**

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'gold_document%';
```

Expected output:
```
gold_document_categories
gold_documents
gold_document_versions
gold_document_metadata
gold_document_templates
gold_document_workflows
gold_document_approvals
gold_document_tags
gold_document_tag_mappings
gold_document_access_logs
gold_document_retention_policies
gold_document_shares
```

### Backend Setup

1. **Install dependencies:**

```bash
cd services/gold
pip install -r requirements.txt
```

2. **Start the service:**

```bash
uvicorn app.main:app --reload --port 8013
```

3. **Verify API is running:**

```bash
curl http://localhost:8013/health
```

Expected response: `{"status": "ok", "service": "gold"}`

### Frontend Setup

1. **Install dependencies:**

```bash
cd apps/customer-app
npm install
```

2. **Configure environment:**

```bash
# .env.local
NEXT_PUBLIC_GOLD_API_URL=http://localhost:8013
```

3. **Start development server:**

```bash
npm run dev
```

4. **Access the application:**

Navigate to: `http://localhost:3000/gold-lending/documents/repository`

---

## Configuration

### Storage Configuration

#### Option 1: Local Filesystem (Development)

```python
# services/gold/app/config.py
STORAGE_TYPE = "local"
STORAGE_PATH = "/var/nbfc/documents"
```

#### Option 2: AWS S3 (Production)

```python
# services/gold/app/config.py
STORAGE_TYPE = "s3"
AWS_S3_BUCKET = "nbfc-documents"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "your-access-key"
AWS_SECRET_ACCESS_KEY = "your-secret-key"
```

#### Option 3: Azure Blob Storage

```python
# services/gold/app/config.py
STORAGE_TYPE = "azure"
AZURE_STORAGE_CONNECTION_STRING = "your-connection-string"
AZURE_CONTAINER_NAME = "documents"
```

### OCR Configuration

```python
# services/gold/app/config.py
OCR_ENABLED = True
OCR_PROVIDER = "tesseract"  # Options: tesseract, aws-textract, google-vision
OCR_LANGUAGES = ["eng", "hin"]
```

### Retention Policy Defaults

```python
# services/gold/app/config.py
DEFAULT_RETENTION_DAYS = 2555  # 7 years
DEFAULT_ARCHIVE_DAYS = 1825    # 5 years
AUTO_APPLY_RETENTION = True
```

---

## Basic Usage

### 1. Upload Your First Document

#### Using the Web Interface:

1. Navigate to **Documents → Upload**
2. Select or drag a file
3. Fill in document details:
   - Category: Select "Loan Documents"
   - Type: Select "loan"
   - Title: "Sample Loan Agreement"
4. Click **Upload Document**

#### Using the API:

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": "category-uuid",
    "document_type": "loan",
    "title": "Loan Agreement",
    "file_name": "agreement.pdf",
    "file_size_bytes": 1048576,
    "mime_type": "application/pdf",
    "storage_path": "/uploads/agreement.pdf",
    "uploaded_by": "user-id"
  }'
```

### 2. Search and Filter Documents

#### Web Interface:

1. Navigate to **Documents → Repository**
2. Use filters:
   - **Search**: Enter keywords
   - **Category**: Select category
   - **Type**: Select document type
   - **Status**: Filter by status
3. Click on a document to view details

#### API:

```bash
# Search documents
curl "http://localhost:8013/api/v1/gold/documents?search=loan&category_id=uuid&limit=20"

# Filter by entity
curl "http://localhost:8013/api/v1/gold/documents?entity_type=loan&entity_id=loan-uuid"
```

### 3. Create a Document Category

#### Web Interface:

Use the API or database insert (UI not included in current phase)

#### API:

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents/categories \
  -H "Content-Type: application/json" \
  -d '{
    "category_code": "DOC_LOAN",
    "category_name": "Loan Documents",
    "description": "All loan-related documents",
    "retention_period_days": 2555,
    "requires_approval": true,
    "created_by": "admin-id"
  }'
```

### 4. Set Up a Retention Policy

#### Web Interface:

1. Navigate to **Documents → Compliance**
2. Click **+ New Policy**
3. Fill in policy details:
   - Policy Code: "RET_LOAN"
   - Policy Name: "Loan Document Retention"
   - Retention Period: 2555 days (7 years)
   - Archive After: 1825 days (5 years)
4. Enable **Auto-apply**
5. Click **Create Policy**

#### API:

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents/retention-policies \
  -H "Content-Type: application/json" \
  -d '{
    "policy_code": "RET_LOAN",
    "policy_name": "Loan Document Retention",
    "category_id": "loan-category-uuid",
    "retention_period_days": 2555,
    "retention_trigger": "from_creation",
    "archive_after_days": 1825,
    "compliance_regulation": "RBI",
    "auto_apply": true,
    "effective_from": "2024-01-01",
    "created_by": "admin-id"
  }'
```

---

## Common Workflows

### Workflow 1: Document Approval Process

**Scenario**: A loan agreement needs approval before finalization.

#### Step 1: Create Workflow

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_code": "WF_LOAN_APPROVAL",
    "workflow_name": "Loan Document Approval",
    "category_id": "loan-category-uuid",
    "workflow_type": "approval",
    "workflow_steps": [
      {"step": 1, "role": "loan_officer", "action": "review"},
      {"step": 2, "role": "branch_manager", "action": "approve"}
    ],
    "sla_hours": 48,
    "is_mandatory": true,
    "created_by": "admin-id"
  }'
```

#### Step 2: Initiate Approval

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents/approvals \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "document-uuid",
    "workflow_id": "workflow-uuid",
    "priority": "high",
    "initiated_by": "user-id"
  }'
```

#### Step 3: Take Action (Approve/Reject)

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents/approvals/{approval_id}/action \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "comments": "Looks good",
    "action_by": "manager-id"
  }'
```

### Workflow 2: Document Version Management

**Scenario**: Update a document and maintain version history.

#### Step 1: Upload New Version

```bash
# Create new version (happens automatically on update)
curl -X PATCH http://localhost:8013/api/v1/gold/documents/{document_id} \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "agreement_v2.pdf",
    "file_size_bytes": 1100000,
    "storage_path": "/uploads/agreement_v2.pdf",
    "updated_by": "user-id"
  }'
```

#### Step 2: View Version History

```bash
curl http://localhost:8013/api/v1/gold/documents/{document_id}/versions
```

#### Step 3: Restore Previous Version

```bash
curl -X POST "http://localhost:8013/api/v1/gold/documents/{document_id}/versions/1/restore?restored_by=user-id"
```

### Workflow 3: Document Sharing

**Scenario**: Share a document with external party with limited access.

#### Step 1: Create Share Link

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents/shares \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "document-uuid",
    "share_type": "external",
    "shared_with_email": "auditor@example.com",
    "permissions": {"view": true, "download": false},
    "max_access_count": 3,
    "expires_at": "2026-08-01T00:00:00Z",
    "is_password_protected": true,
    "password": "secure-password",
    "shared_by": "user-id"
  }'
```

#### Step 2: Get Share Link

Response includes `share_token`:
```json
{
  "share_id": "uuid",
  "share_token": "abc123xyz789",
  "share_url": "https://app.nbfc.com/shared/abc123xyz789"
}
```

#### Step 3: Access Document (External User)

```bash
curl http://localhost:8013/api/v1/gold/documents/shares/token/abc123xyz789
```

#### Step 4: Revoke Access

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents/shares/{share_id}/revoke \
  -H "Content-Type: application/json" \
  -d '{
    "revoked_by": "user-id",
    "revocation_reason": "Access no longer needed"
  }'
```

### Workflow 4: Bulk Document Operations

**Scenario**: Apply tags to multiple documents at once.

#### Step 1: Create Tags

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents/tags \
  -H "Content-Type: application/json" \
  -d '{
    "tag_name": "Q1-2026",
    "tag_category": "period",
    "tag_color": "#3B82F6",
    "created_by": "user-id"
  }'
```

#### Step 2: Bulk Tag Documents

```bash
curl -X POST http://localhost:8013/api/v1/gold/documents/bulk/tag \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": ["uuid1", "uuid2", "uuid3"],
    "tag_ids": ["tag-uuid1", "tag-uuid2"],
    "tagged_by": "user-id"
  }'
```

### Workflow 5: OCR Text Extraction

**Scenario**: Extract text from a scanned document.

#### Step 1: Upload Document with OCR

```bash
# Upload document first, then request OCR
curl -X POST http://localhost:8013/api/v1/gold/documents/ocr/extract \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "document-uuid",
    "ocr_language": "eng",
    "extract_tables": true,
    "extract_signatures": false
  }'
```

#### Step 2: View Extracted Text

```bash
curl http://localhost:8013/api/v1/gold/documents/{document_id}
```

Response includes:
```json
{
  "document_id": "uuid",
  "title": "Scanned Agreement",
  "ocr_text": "This is the extracted text from the document...",
  "extracted_data": {
    "language": "eng",
    "pages": 5,
    "words_count": 1500,
    "confidence": 0.95
  }
}
```

---

## Best Practices

### 1. Document Organization

**Use Hierarchical Categories:**
```
Loan Documents
├── Application Documents
├── Approval Documents
├── Disbursement Documents
└── Repayment Documents
```

**Naming Conventions:**
- Document Code: `DOC_[TYPE]_[SUBTYPE]`
- File Names: `[type]_[entity]_[date].[ext]`
- Example: `loan_agreement_L001_20260703.pdf`

### 2. Metadata Management

**Define Category-Specific Metadata:**
```json
{
  "fields": [
    {"name": "loan_number", "type": "string", "required": true},
    {"name": "customer_name", "type": "string", "required": true},
    {"name": "loan_amount", "type": "number", "required": false}
  ]
}
```

**Use Consistent Metadata Keys:**
- `customer_id` instead of `custId` or `customer`
- `loan_amount` instead of `loanAmt` or `amount`

### 3. Version Control

**When to Create New Versions:**
- ✅ Content changes
- ✅ Corrections or amendments
- ✅ Re-uploads after edits
- ❌ Metadata updates only
- ❌ Tag additions
- ❌ Status changes

**Version Descriptions:**
```
Good: "Updated loan amount from $10,000 to $12,000"
Bad: "Updated document"
```

### 4. Access Control

**Implement Role-Based Permissions:**
```python
PERMISSIONS = {
    "loan_officer": ["view", "upload", "edit"],
    "branch_manager": ["view", "download", "approve"],
    "auditor": ["view", "download"],
    "compliance_officer": ["view", "download", "delete"]
}
```

**Log All Access:**
- Always log document access
- Include user context (role, IP, device)
- Monitor failed access attempts

### 5. Retention & Compliance

**Follow Regulatory Requirements:**
- **KYC Documents**: 7 years from account closure
- **Loan Documents**: 7 years from loan closure
- **Audit Documents**: 7 years from audit date
- **Compliance Documents**: 10 years from creation

**Automate Retention:**
- Enable `auto_apply` on policies
- Set up scheduled jobs for archival
- Configure alerts for expiring documents

### 6. Performance Optimization

**File Upload:**
- Compress large files before upload
- Use chunked uploads for files > 10MB
- Validate file type and size on client side

**Search & Filtering:**
- Use pagination (`skip` and `limit`)
- Create database indexes on frequently queried fields
- Cache search results for common queries

**Storage:**
- Store files in date-based folders: `/2026/07/03/`
- Use CDN for frequently accessed documents
- Implement lazy loading for document lists

---

## Troubleshooting

### Issue: Document Upload Fails

**Symptoms:**
- Upload returns 400 Bad Request
- File doesn't appear in repository

**Solutions:**

1. **Check file size:**
```bash
# Max file size is 10MB
ls -lh document.pdf
```

2. **Verify MIME type:**
```python
import mimetypes
mime_type = mimetypes.guess_type('document.pdf')[0]
print(mime_type)  # Should be 'application/pdf'
```

3. **Check storage permissions:**
```bash
# Ensure write permissions
ls -la /var/nbfc/documents
chmod 755 /var/nbfc/documents
```

4. **Review logs:**
```bash
tail -f services/gold/logs/app.log | grep "document upload"
```

### Issue: OCR Not Extracting Text

**Symptoms:**
- `ocr_text` field is empty
- OCR status shows "failed"

**Solutions:**

1. **Check image quality:**
- Minimum 300 DPI recommended
- Clear, high-contrast text
- No skew or rotation

2. **Verify OCR service:**
```bash
# Test Tesseract
tesseract --version
tesseract test.jpg output
```

3. **Check file format:**
- Supported: PDF, JPG, PNG
- Not supported: DOCX, XLSX

4. **Review OCR logs:**
```bash
tail -f services/gold/logs/ocr.log
```

### Issue: Approval Workflow Stuck

**Symptoms:**
- Approval stays in "pending" status
- No notification to assigned user

**Solutions:**

1. **Check workflow configuration:**
```sql
SELECT workflow_steps 
FROM gold_document_workflows 
WHERE workflow_id = 'uuid';
```

2. **Verify assigned user:**
```sql
SELECT assigned_to, current_step, total_steps
FROM gold_document_approvals
WHERE approval_id = 'uuid';
```

3. **Check SLA expiration:**
```sql
SELECT approval_id, due_date, is_escalated
FROM gold_document_approvals
WHERE due_date < NOW() AND approval_status = 'pending';
```

4. **Manually reassign:**
```bash
curl -X PATCH http://localhost:8013/api/v1/gold/documents/approvals/{approval_id} \
  -H "Content-Type: application/json" \
  -d '{
    "assigned_to": "new-user-id",
    "updated_by": "admin-id"
  }'
```

### Issue: High Storage Usage

**Symptoms:**
- Disk space running low
- Slow document retrieval

**Solutions:**

1. **Check storage usage:**
```bash
du -sh /var/nbfc/documents/*
```

2. **Archive old documents:**
```sql
-- Find archivable documents
SELECT document_id, title, created_at
FROM gold_documents
WHERE created_at < NOW() - INTERVAL '5 years'
AND storage_status = 'uploaded';
```

3. **Enable compression:**
```python
# services/gold/app/config.py
COMPRESS_DOCUMENTS = True
COMPRESSION_LEVEL = 6  # 1-9, higher = better compression
```

4. **Move to cold storage:**
```bash
# Archive documents older than 5 years
aws s3 sync /var/nbfc/documents/2021 s3://archive-bucket/2021 --storage-class GLACIER
```

### Issue: Search Returns No Results

**Symptoms:**
- Known documents don't appear in search
- Search returns empty array

**Solutions:**

1. **Check search syntax:**
```bash
# Correct
curl "http://localhost:8013/api/v1/gold/documents?search=loan%20agreement"

# Incorrect (missing URL encoding)
curl "http://localhost:8013/api/v1/gold/documents?search=loan agreement"
```

2. **Verify document exists:**
```sql
SELECT document_id, title, is_deleted
FROM gold_documents
WHERE title ILIKE '%loan agreement%';
```

3. **Check filters:**
```bash
# Remove restrictive filters
curl "http://localhost:8013/api/v1/gold/documents?search=loan"
# Instead of
curl "http://localhost:8013/api/v1/gold/documents?search=loan&category_id=wrong-uuid"
```

4. **Rebuild search index:**
```sql
-- PostgreSQL full-text search
REINDEX INDEX idx_documents_search;
```

---

## Next Steps

### Explore Advanced Features

1. **Custom Workflows**: Create multi-stage approval workflows
2. **Template Generation**: Auto-generate documents from templates
3. **E-Signatures**: Integrate DocuSign or similar
4. **Automated Classification**: AI-based document classification
5. **Advanced Analytics**: Document usage and compliance reports

### Integration

1. **Connect to LMS**: Link documents to loan accounts
2. **CRM Integration**: Associate documents with customers
3. **Accounting System**: Link financial documents
4. **Notification Service**: Send alerts on document events

### Monitoring & Maintenance

1. **Set up monitoring**: Track API performance and errors
2. **Configure backups**: Regular database and storage backups
3. **Schedule cleanup**: Automated deletion of expired documents
4. **Audit reviews**: Regular compliance audits

---

## Support Resources

- **Full Documentation**: See `PHASE10_DOCUMENT_MANAGEMENT.md`
- **API Reference**: http://localhost:8013/docs
- **Support Email**: support@nbfcsuite.com
- **Community Forum**: https://forum.nbfcsuite.com

---

## Quick Reference Commands

```bash
# Health check
curl http://localhost:8013/health

# List documents
curl http://localhost:8013/api/v1/gold/documents

# Get statistics
curl http://localhost:8013/api/v1/gold/documents/statistics/overview

# List approvals
curl http://localhost:8013/api/v1/gold/documents/approvals?approval_status=pending

# List retention policies
curl http://localhost:8013/api/v1/gold/documents/retention-policies

# Check workflow statistics
curl http://localhost:8013/api/v1/gold/documents/statistics/workflows
```

---

**Version**: 1.0.0  
**Last Updated**: July 3, 2026  
**Questions?** Contact the development team at dev@nbfcsuite.com
