# HRMS Employee Self-Service - Deployment Guide

## Quick Deployment Steps

### Step 1: Install Dependencies

#### Backend
The backend dependencies are already in `requirements.txt`. ReportLab is included.

```bash
cd backend
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend/apps/admin-portal
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled @mui/x-date-pickers
```

### Step 2: Database Migration

#### Option A: Using Alembic (Recommended)
```bash
cd backend
alembic revision --autogenerate -m "Add ESS tables"
alembic upgrade head
```

#### Option B: Direct Table Creation
The models will auto-create tables on first run if you have `create_all()` enabled in main.py.

### Step 3: Routes Configuration

Routes are already configured! The Next.js App Router files have been created:

- `/hrms/ess` → Dashboard
- `/hrms/ess/payslips` → Payslips
- `/hrms/ess/leaves` → Leave Management
- `/hrms/ess/investments` → Investment Declarations
- `/hrms/ess/reimbursements` → Reimbursement Claims
- `/hrms/ess/profile` → Profile Update

### Step 4: Environment Variables

Ensure these are set:

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/nbfcsuite
JWT_SECRET=your-secret-key
TENANT_ISOLATION_ENABLED=true

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 5: Start Services

#### Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend/apps/admin-portal
npm run dev
```

### Step 6: Access ESS

Navigate to: `http://localhost:3000/hrms/ess`

---

## Database Tables Created

1. **hrms_leave_balances** - Leave balance tracking
2. **hrms_leave_applications** - Leave applications
3. **hrms_investment_declarations** - Investment declarations
4. **hrms_investment_declaration_items** - Declaration line items
5. **hrms_reimbursement_claims** - Reimbursement claims

---

## API Endpoints Available

### Dashboard
- `GET /api/hrms/ess/dashboard`

### Payslips
- `GET /api/hrms/ess/payslips`
- `GET /api/hrms/ess/payslips/{month}/{year}`
- `GET /api/hrms/ess/payslips/{id}/download`

### Leave Management
- `GET /api/hrms/ess/leave/balances`
- `POST /api/hrms/ess/leave/applications`
- `POST /api/hrms/ess/leave/applications/{id}/submit`
- `POST /api/hrms/ess/leave/applications/{id}/cancel`
- `GET /api/hrms/ess/leave/applications`

### Investment Declarations
- `POST /api/hrms/ess/investment/declarations`
- `POST /api/hrms/ess/investment/declarations/{id}/submit`
- `GET /api/hrms/ess/investment/declarations`

### Reimbursement Claims
- `POST /api/hrms/ess/reimbursement/claims`
- `POST /api/hrms/ess/reimbursement/claims/{id}/submit`
- `GET /api/hrms/ess/reimbursement/claims`

### Profile
- `GET /api/hrms/ess/profile`
- `PUT /api/hrms/ess/profile`

---

## Testing

### 1. Test API Endpoints
Access Swagger UI: `http://localhost:8000/docs`

### 2. Test Frontend Pages
- Dashboard: `http://localhost:3000/hrms/ess`
- Payslips: `http://localhost:3000/hrms/ess/payslips`
- Leaves: `http://localhost:3000/hrms/ess/leaves`
- Investments: `http://localhost:3000/hrms/ess/investments`
- Reimbursements: `http://localhost:3000/hrms/ess/reimbursements`
- Profile: `http://localhost:3000/hrms/ess/profile`

---

## Troubleshooting

### Issue: Tables not created
**Solution:** Run Alembic migrations or check that `Base.metadata.create_all()` is called in main.py

### Issue: 401 Unauthorized
**Solution:** Ensure JWT token is valid and employee_id is linked to user

### Issue: PDF generation fails
**Solution:** Install reportlab: `pip install reportlab`

### Issue: Frontend build errors
**Solution:** Install MUI dependencies: `npm install @mui/material @mui/icons-material @emotion/react @emotion/styled @mui/x-date-pickers`

### Issue: Navigation doesn't work
**Solution:** Routes are already created in `/app/hrms/ess/` directory. Just restart dev server.

---

## Production Deployment Checklist

- [ ] Run database migrations
- [ ] Install all dependencies
- [ ] Set production environment variables
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up file storage for attachments (S3/MinIO)
- [ ] Configure email notifications
- [ ] Set up monitoring and logging
- [ ] Test all features end-to-end
- [ ] Train users
- [ ] Create user documentation

---

## Files Created

### Backend (5 files)
✅ `backend/shared/database/hrms_models.py` - Updated with ESS models
✅ `backend/services/hrms/ess_schemas.py` - Pydantic schemas
✅ `backend/services/hrms/ess_service.py` - Business logic
✅ `backend/services/hrms/ess_router.py` - API endpoints
✅ `backend/main.py` - Updated with ESS router

### Frontend (13 files)
✅ `frontend/apps/admin-portal/src/pages/ess/Dashboard.tsx`
✅ `frontend/apps/admin-portal/src/pages/ess/Payslips.tsx`
✅ `frontend/apps/admin-portal/src/pages/ess/Leaves.tsx`
✅ `frontend/apps/admin-portal/src/pages/ess/Investments.tsx`
✅ `frontend/apps/admin-portal/src/pages/ess/Reimbursements.tsx`
✅ `frontend/apps/admin-portal/src/pages/ess/Profile.tsx`
✅ `frontend/apps/admin-portal/src/pages/ess/index.tsx`
✅ `frontend/apps/admin-portal/src/app/hrms/ess/page.tsx`
✅ `frontend/apps/admin-portal/src/app/hrms/ess/payslips/page.tsx`
✅ `frontend/apps/admin-portal/src/app/hrms/ess/leaves/page.tsx`
✅ `frontend/apps/admin-portal/src/app/hrms/ess/investments/page.tsx`
✅ `frontend/apps/admin-portal/src/app/hrms/ess/reimbursements/page.tsx`
✅ `frontend/apps/admin-portal/src/app/hrms/ess/profile/page.tsx`
✅ `frontend/apps/admin-portal/package.json` - Updated with MUI deps

---

## Support

For issues or questions:
- Check logs: `backend/logs/` and browser console
- Review API docs: `http://localhost:8000/docs`
- Test individual endpoints in Swagger UI
- Check database for data

---

**Status:** ✅ Ready for Deployment
**Date:** July 10, 2026
