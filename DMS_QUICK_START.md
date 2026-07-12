# DMS Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Run Migration (1 minute)
```bash
cd backend
alembic upgrade head
```
**Expected Output:** `✅ DMS Module tables created successfully!`

### Step 2: Start Server (30 seconds)
```bash
uvicorn main:app --reload --port 8000
```
**Server starts at:** http://localhost:8000

### Step 3: Test API (2 minutes)

#### Get JWT Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

#### Create Your First Document
```bash
curl -X POST "http://localhost:8000/api/v1/dms/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=My First Document" \
  -F "document_type=other" \
  -F "category=internal" \
  -F "description=Test document" \
  -F "file=@path/to/file.pdf"
```

#### Search Documents
```bash
curl -X GET "http://localhost:8000/api/v1/dms/documents?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### View Dashboard
```bash
curl -X GET "http://localhost:8000/api/v1/dms/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 4: Explore API (1 minute)
Open browser: http://localhost:8000/docs

Browse all 40+ DMS endpoints with interactive testing!

---

## 📋 Common Operations

### Upload Document with Metadata
```bash
curl -X POST "http://localhost:8000/api/v1/dms/documents" \
  -H "Authorization: Bearer TOKEN" \
  -F "title=Contract Agreement" \
  -F "document_type=contract" \
  -F "category=legal" \
  -F "access_level=confidential" \
  -F "department=Legal" \
  -F "reference_number=CONT-2026-001" \
  -F "file=@contract.pdf"
```

### Create Approval Workflow
```bash
curl -X POST "http://localhost:8000/api/v1/dms/workflows?document_id=DOC_UUID" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "Contract Approval",
    "workflow_type": "approval",
    "steps": [
      {"step_number": 1, "step_name": "Legal Review", "approver_id": "USER_UUID"},
      {"step_number": 2, "step_name": "Final Approval", "approver_id": "USER_UUID"}
    ]
  }'
```

### Request E-Signature
```bash
curl -X POST "http://localhost:8000/api/v1/dms/signatures" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "DOC_UUID",
    "signer_id": "USER_UUID",
    "signature_type": "simple"
  }'
```

### Grant Document Access
```bash
curl -X POST "http://localhost:8000/api/v1/dms/permissions" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "DOC_UUID",
    "user_id": "USER_UUID",
    "can_view": true,
    "can_download": true,
    "can_edit": false
  }'
```

---

## 🎯 Key Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create Document | POST | `/api/v1/dms/documents` |
| Search Documents | POST | `/api/v1/dms/documents/search` |
| Get Document | GET | `/api/v1/dms/documents/{id}` |
| Download File | GET | `/api/v1/dms/documents/{id}/download` |
| Upload Version | POST | `/api/v1/dms/documents/{id}/versions` |
| Create Workflow | POST | `/api/v1/dms/workflows` |
| Pending Approvals | GET | `/api/v1/dms/workflows/pending-approvals` |
| Approve/Reject | POST | `/api/v1/dms/approvals/{id}/process` |
| Request Signature | POST | `/api/v1/dms/signatures` |
| Sign Document | POST | `/api/v1/dms/signatures/{id}/process` |
| Grant Permission | POST | `/api/v1/dms/permissions` |
| Dashboard | GET | `/api/v1/dms/dashboard` |

---

## 🔐 Authentication

All requests require JWT token in header:
```
Authorization: Bearer <your_jwt_token>
```

Get token from login endpoint:
```bash
POST /api/v1/auth/login
{
  "username": "your_username",
  "password": "your_password"
}
```

---

## 📁 File Organization

**Uploads are stored in:**
```
dms_storage/
└── {tenant_id}/
    └── {document_id}/
        └── v{version}/
            └── filename.ext
```

**Example:**
```
dms_storage/default/abc123.../v1/contract.pdf
dms_storage/default/abc123.../v2/contract.pdf
```

---

## 🎨 Document Types & Categories

### Document Types (14)
- `contract`, `policy`, `procedure`, `form`
- `report`, `invoice`, `receipt`, `certificate`
- `letter`, `memorandum`, `agreement`, `notice`
- `circular`, `other`

### Categories (10)
- `legal`, `financial`, `hr`, `operations`
- `compliance`, `marketing`, `it`, `customer`
- `vendor`, `internal`

### Access Levels (5)
- `public`, `internal`, `confidential`
- `restricted`, `secret`

---

## ✅ Quick Health Check

### 1. Check Server
```bash
curl http://localhost:8000/health
```

### 2. Check DMS Statistics
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/dms/statistics
```

### 3. Check My Documents
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/dms/my-documents
```

---

## 🚨 Troubleshooting

**Problem:** "Table doesn't exist"  
**Solution:** Run `alembic upgrade head`

**Problem:** "File too large"  
**Solution:** File limit is 50MB by default

**Problem:** "Permission denied"  
**Solution:** Check document access level and permissions

**Problem:** "Invalid token"  
**Solution:** Get fresh token from `/auth/login`

---

## 📚 Next Steps

1. ✅ **Backend Setup** - Complete!
2. 📋 **Test API** - Use Swagger at `/docs`
3. 💻 **Build Frontend** - See `DMS_IMPLEMENTATION_COMPLETE.md`
4. 🚀 **Deploy** - Use Docker or cloud platform
5. 📊 **Monitor** - Track usage and performance

---

**Full Documentation:** See `DMS_IMPLEMENTATION_COMPLETE.md`

**API Documentation:** http://localhost:8000/docs

**Support:** See troubleshooting section in main documentation
