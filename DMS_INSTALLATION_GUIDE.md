# DMS Installation & Deployment Guide

## Quick Start (5 Minutes)

### Step 1: Install Frontend Dependencies

```bash
cd frontend/apps/admin-portal
npm install react-signature-canvas @types/react-signature-canvas @ant-design/plots antd @ant-design/icons
```

Or with yarn:
```bash
yarn add react-signature-canvas @ant-design/plots antd @ant-design/icons
yarn add -D @types/react-signature-canvas
```

### Step 2: Run Database Migration

```bash
cd backend
alembic upgrade head
```

This will create all 11 DMS tables in your database.

### Step 3: Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 4: Start Frontend

```bash
cd frontend/apps/admin-portal
npm run dev
```

### Step 5: Access DMS

Open your browser and navigate to:
- **Dashboard**: http://localhost:3000/dms
- **Documents**: http://localhost:3000/dms/documents
- **Approvals**: http://localhost:3000/dms/approvals
- **Signatures**: http://localhost:3000/dms/signatures

---

## Detailed Installation

### Backend Setup

#### 1. Verify Backend Files
Ensure these files exist:
- `backend/services/dms/router.py`
- `backend/services/dms/service.py`
- `backend/services/dms/workflow_service.py`
- `backend/services/dms/signature_service.py`
- `backend/services/dms/permission_service.py`
- `backend/services/dms/schemas.py`
- `backend/shared/database/dms_models.py`
- `backend/alembic/versions/014_add_dms_module.py`

#### 2. Check Backend Registration
In `backend/main.py`, verify:
```python
# DMS Models Import
from shared.database.dms_models import (
    Document, DocumentVersion, DocumentWorkflow,
    WorkflowTemplate, DocumentApproval, DocumentPermission,
    DocumentSignature, DocumentComment, DocumentAuditLog
)

# DMS Router Registration
from services.dms.router import router as dms_router
app.include_router(dms_router, prefix="/api/v1/dms", tags=["DMS"])
```

#### 3. Run Migration
```bash
cd backend
alembic upgrade head
```

Verify tables created:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_name LIKE 'dms_%' OR table_name IN ('documents', 'document_versions', 'workflow_templates');
```

#### 4. Create Storage Directory
```bash
mkdir -p dms_storage
chmod 755 dms_storage
```

#### 5. Configure Environment
Add to `.env`:
```env
DMS_STORAGE_PATH=./dms_storage
DMS_MAX_FILE_SIZE=52428800  # 50MB in bytes
DMS_ALLOWED_EXTENSIONS=pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif
```

---

### Frontend Setup

#### 1. Verify Frontend Files
Ensure these files exist:

**Types & Services:**
- `frontend/apps/admin-portal/src/types/dms.types.ts`
- `frontend/apps/admin-portal/src/services/dms.service.ts`
- `frontend/apps/admin-portal/src/lib/utils.ts`

**Pages:**
- `frontend/apps/admin-portal/src/pages/dms/DocumentsPage.tsx`
- `frontend/apps/admin-portal/src/pages/dms/DocumentDetailPage.tsx`
- `frontend/apps/admin-portal/src/pages/dms/ApprovalsPage.tsx`
- `frontend/apps/admin-portal/src/pages/dms/SignaturesPage.tsx`
- `frontend/apps/admin-portal/src/pages/dms/DMSDashboard.tsx`

**Components:**
- `frontend/apps/admin-portal/src/pages/dms/components/UploadDocumentModal.tsx`

**Routes:**
- `frontend/apps/admin-portal/src/app/dms/layout.tsx`
- `frontend/apps/admin-portal/src/app/dms/page.tsx`
- `frontend/apps/admin-portal/src/app/dms/documents/page.tsx`
- `frontend/apps/admin-portal/src/app/dms/documents/[id]/page.tsx`
- `frontend/apps/admin-portal/src/app/dms/approvals/page.tsx`
- `frontend/apps/admin-portal/src/app/dms/signatures/page.tsx`

#### 2. Install Dependencies

Check if Ant Design is already installed:
```bash
npm list antd
```

If not installed, install all required packages:
```bash
npm install antd @ant-design/icons @ant-design/plots react-signature-canvas
npm install --save-dev @types/react-signature-canvas
```

#### 3. Configure API Base URL

Check `frontend/apps/admin-portal/src/services/api.ts`:
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

// Add JWT interceptor if needed
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

#### 4. Add Navigation Menu

Update your navigation configuration (e.g., `src/components/Layout/Sidebar.tsx`):

```typescript
import { FileOutlined, FolderOutlined, CheckCircleOutlined, EditOutlined } from '@ant-design/icons';

const menuItems = [
  // ... existing items
  {
    key: 'dms',
    icon: <FolderOutlined />,
    label: 'Documents',
    children: [
      {
        key: 'dms-dashboard',
        label: 'Dashboard',
        path: '/dms',
        icon: <FileOutlined />
      },
      {
        key: 'dms-documents',
        label: 'All Documents',
        path: '/dms/documents',
        icon: <FolderOutlined />
      },
      {
        key: 'dms-approvals',
        label: 'Approvals',
        path: '/dms/approvals',
        icon: <CheckCircleOutlined />
      },
      {
        key: 'dms-signatures',
        label: 'Signatures',
        path: '/dms/signatures',
        icon: <EditOutlined />
      }
    ]
  }
];
```

---

## Testing

### Backend API Tests

#### Test Document Upload
```bash
curl -X POST http://localhost:8000/api/v1/dms/documents \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "title=Test Document" \
  -F "document_type=loan_application" \
  -F "file=@/path/to/file.pdf"
```

#### Test Document List
```bash
curl http://localhost:8000/api/v1/dms/documents?page=1&page_size=10 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Test Statistics
```bash
curl http://localhost:8000/api/v1/dms/statistics \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Frontend Tests

1. **Upload Document**
   - Navigate to http://localhost:3000/dms/documents
   - Click "Upload Document"
   - Fill form and upload file
   - Verify success message

2. **View Document**
   - Click on any document in the list
   - Verify all tabs load (Versions, Comments, Workflows, Permissions)
   - Test download

3. **Approve Document**
   - Navigate to http://localhost:3000/dms/approvals
   - Click "Approve" on any pending workflow
   - Add comments and submit
   - Verify success

4. **Sign Document**
   - Navigate to http://localhost:3000/dms/signatures
   - Click "Sign" on pending signature
   - Draw signature on canvas
   - Submit and verify

5. **Dashboard**
   - Navigate to http://localhost:3000/dms
   - Verify all statistics load
   - Check charts display correctly

---

## Troubleshooting

### Issue: "Module not found: Can't resolve 'antd'"

**Solution:**
```bash
npm install antd @ant-design/icons
```

### Issue: "Cannot find module 'react-signature-canvas'"

**Solution:**
```bash
npm install react-signature-canvas @types/react-signature-canvas
```

### Issue: Backend 404 on /api/v1/dms

**Solution:**
- Check `backend/main.py` has DMS router registered
- Verify backend is running: `curl http://localhost:8000/docs`
- Check FastAPI docs at http://localhost:8000/docs for DMS endpoints

### Issue: Database table doesn't exist

**Solution:**
```bash
cd backend
alembic upgrade head
```

### Issue: Permission denied on file upload

**Solution:**
```bash
chmod 755 dms_storage
chown -R youruser:yourgroup dms_storage
```

### Issue: File size too large

**Solution:**
Update `backend/.env`:
```env
DMS_MAX_FILE_SIZE=104857600  # 100MB
```

### Issue: CORS error

**Solution:**
In `backend/main.py`, ensure CORS middleware allows frontend origin:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Production Deployment

### Backend Deployment

#### 1. Environment Variables
Create `.env.production`:
```env
DATABASE_URL=postgresql://user:pass@prod-db:5432/nbfc
DMS_STORAGE_PATH=/var/dms_storage
DMS_MAX_FILE_SIZE=52428800
REDIS_URL=redis://prod-redis:6379
```

#### 2. Storage Configuration
Use cloud storage in production:
```python
# backend/services/dms/storage.py
import boto3

class S3Storage:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket = os.getenv('DMS_S3_BUCKET')
    
    def save_file(self, file_data, path):
        self.s3.put_object(
            Bucket=self.bucket,
            Key=path,
            Body=file_data
        )
```

#### 3. Docker Deployment
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/nbfc
      - DMS_STORAGE_PATH=/var/dms_storage
    volumes:
      - dms-storage:/var/dms_storage

volumes:
  dms-storage:
```

### Frontend Deployment

#### 1. Build for Production
```bash
cd frontend/apps/admin-portal
npm run build
```

#### 2. Environment Variables
Create `.env.production`:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

#### 3. Serve with PM2
```bash
pm2 start npm --name "admin-portal" -- start
```

#### 4. Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

---

## Security Checklist

### Backend
- [ ] JWT authentication enabled
- [ ] File type validation active
- [ ] File size limits enforced
- [ ] Virus scanning integrated
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] XSS prevention (Pydantic validation)
- [ ] Rate limiting configured
- [ ] HTTPS only in production
- [ ] Database encryption at rest
- [ ] Audit logs enabled

### Frontend
- [ ] API calls use HTTPS
- [ ] JWT stored securely (httpOnly cookies preferred)
- [ ] Input validation on forms
- [ ] XSS prevention (React escaping)
- [ ] CSRF tokens for state-changing operations
- [ ] Content Security Policy headers
- [ ] Regular dependency updates

---

## Performance Optimization

### Backend
```python
# Add Redis caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@router.get("/statistics")
@cache(expire=300)  # Cache for 5 minutes
async def get_statistics():
    ...
```

### Frontend
```typescript
// Add React Query caching
import { useQuery } from '@tanstack/react-query';

const { data } = useQuery({
  queryKey: ['documents'],
  queryFn: () => dmsService.listDocuments(),
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

---

## Monitoring

### Backend Logging
```python
import logging

logger = logging.getLogger(__name__)

@router.post("/documents")
async def create_document():
    logger.info(f"User {user_id} uploading document")
    ...
    logger.info(f"Document {doc_id} created successfully")
```

### Error Tracking
Integrate Sentry:
```python
import sentry_sdk

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
```

### Metrics
Track key metrics:
- Document upload success rate
- Average file size
- Workflow approval time
- Signature completion rate
- API response times

---

## Backup & Recovery

### Database Backup
```bash
pg_dump -U user nbfc > backup_$(date +%Y%m%d).sql
```

### File Storage Backup
```bash
rsync -av /var/dms_storage/ /backup/dms_storage/
```

### Automated Backups
```bash
# crontab -e
0 2 * * * /scripts/backup_dms.sh
```

---

## Support

For issues or questions:
1. Check logs: `backend/logs/dms.log`
2. Review documentation: `DMS_IMPLEMENTATION_COMPLETE.md`
3. Test API: http://localhost:8000/docs
4. Frontend dev tools: React DevTools

---

**Installation guide version**: 1.0
**Last updated**: December 2024
