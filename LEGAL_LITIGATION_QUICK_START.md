# Legal - Litigation Management Quick Start Guide

## 🎯 What's Implemented

A complete **Litigation Management** system with:
- ✅ **Case Tracking** - Full lifecycle management
- ✅ **Hearing Management** - Schedule, track, and document hearings
- ✅ **Legal Expense Tracking** - Approve, pay, and monitor expenses
- ✅ **Party Management** - Track all parties and legal representatives
- ✅ **Statistics & Analytics** - Real-time insights

---

## 🚀 Quick Start

### 1. Backend Setup

The litigation module is already integrated into the main application.

**Check Registration:**
```python
# backend/main.py already includes:
from backend.services.legal.litigation_router import router as litigation_router
app.include_router(litigation_router, tags=["Legal - Litigation Management"])
```

**Database Tables:**
The following tables will be auto-created on app startup:
- `legal_litigation_cases`
- `legal_case_hearings`
- `legal_expenses`
- `legal_case_parties`
- `legal_case_documents`

### 2. Start Backend Server

```bash
cd backend
python main.py
```

API will be available at: `http://localhost:8000`  
Swagger Docs: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend
npm install  # If not already done
npm start
```

Frontend will run at: `http://localhost:3000`

### 4. Access the Module

Navigate to:
- Dashboard: `/legal/litigation`
- Create Case: `/legal/litigation/cases/new`
- Case Details: `/legal/litigation/cases/{caseId}`

---

## 📋 API Endpoints

### Cases
```
POST   /api/v1/legal/litigation/cases              # Create case
GET    /api/v1/legal/litigation/cases              # List cases
GET    /api/v1/legal/litigation/cases/{id}         # Get case
PUT    /api/v1/legal/litigation/cases/{id}         # Update case
DELETE /api/v1/legal/litigation/cases/{id}         # Delete case
```

### Hearings
```
POST   /api/v1/legal/litigation/hearings           # Schedule hearing
GET    /api/v1/legal/litigation/cases/{id}/hearings  # List hearings
GET    /api/v1/legal/litigation/hearings/upcoming  # Upcoming hearings
PUT    /api/v1/legal/litigation/hearings/{id}      # Update hearing
```

### Expenses
```
POST   /api/v1/legal/litigation/expenses           # Create expense
GET    /api/v1/legal/litigation/cases/{id}/expenses  # List expenses
PUT    /api/v1/legal/litigation/expenses/{id}      # Update expense
POST   /api/v1/legal/litigation/expenses/{id}/approve  # Approve
POST   /api/v1/legal/litigation/expenses/{id}/mark-paid  # Mark paid
```

### Parties
```
POST   /api/v1/legal/litigation/parties            # Add party
GET    /api/v1/legal/litigation/cases/{id}/parties # List parties
```

### Statistics
```
GET    /api/v1/legal/litigation/statistics         # Get statistics
```

---

## 🧪 Test the API

### 1. Create a Test Case

```bash
curl -X POST http://localhost:8000/api/v1/legal/litigation/cases \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "case_number": "CS/001/2024",
    "case_title": "ABC Bank vs XYZ Company",
    "case_type": "banking",
    "priority": "high",
    "court_name": "High Court of Delhi",
    "filing_date": "2024-01-15",
    "claim_amount": 5000000,
    "primary_advocate": "John Doe"
  }'
```

### 2. Schedule a Hearing

```bash
curl -X POST http://localhost:8000/api/v1/legal/litigation/hearings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "case_id": "CASE_UUID_HERE",
    "hearing_type": "regular_hearing",
    "scheduled_date": "2024-02-15T10:00:00",
    "court_room": "Court Room 3",
    "purpose": "Regular hearing for case progress"
  }'
```

### 3. Add an Expense

```bash
curl -X POST http://localhost:8000/api/v1/legal/litigation/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "case_id": "CASE_UUID_HERE",
    "expense_category": "advocate_fees",
    "description": "Professional fees for January 2024",
    "amount": 50000,
    "tax_amount": 9000,
    "expense_date": "2024-01-31",
    "payee_name": "John Doe Law Associates"
  }'
```

### 4. Get Statistics

```bash
curl -X GET http://localhost:8000/api/v1/legal/litigation/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Frontend Components

### LitigationDashboard
**Location:** `frontend/src/components/legal/LitigationDashboard.jsx`

**Features:**
- Statistics cards (total cases, active, won/lost, expenses)
- Cases table with filters (status, type, priority, search)
- Upcoming hearings section
- Pagination

### CaseDetails
**Location:** `frontend/src/components/legal/CaseDetails.jsx`

**Features:**
- Complete case information
- Tabs: Details, Hearings, Expenses, Parties
- Add hearing/expense/party modals
- Approve expenses
- Mark expenses as paid

### CreateCase
**Location:** `frontend/src/components/legal/CreateCase.jsx`

**Features:**
- Multi-step form (4 steps)
- Form validation
- Progress indicator

---

## 🔧 Configuration

### Backend Configuration

**Database:** Already configured in `.env`
```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

**Multi-tenant:** Already enabled
```python
TENANT_ISOLATION_ENABLED=True
```

### Frontend Configuration

**API URL:** Update in `frontend/.env`
```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 📁 File Structure

```
backend/
├── shared/database/
│   └── legal_models.py                    # Litigation models (UPDATED)
├── services/legal/
│   ├── litigation_schemas.py              # Pydantic schemas (NEW)
│   ├── litigation_service.py              # Business logic (NEW)
│   └── litigation_router.py               # API endpoints (NEW)
└── main.py                                # Router registration (UPDATED)

frontend/
├── src/
│   ├── services/legal/
│   │   └── litigationService.js           # API service (NEW)
│   └── components/legal/
│       ├── LitigationDashboard.jsx        # Dashboard (NEW)
│       ├── CaseDetails.jsx                # Case details (NEW)
│       ├── CreateCase.jsx                 # Create form (NEW)
│       └── index.js                       # Exports (NEW)
```

---

## 🎨 UI Features

### Dashboard
- **Statistics Cards:** Overview of cases, hearings, expenses
- **Filters:** Status, Type, Priority, Search
- **Tables:** Sortable, paginated cases list
- **Actions:** View, Edit, Delete

### Case Details
- **Overview:** All case information in organized tabs
- **Hearings:** Schedule and track hearings
- **Expenses:** Add, approve, and pay expenses
- **Parties:** Manage all parties involved

### Forms
- **Multi-step:** Guided case creation process
- **Validation:** Real-time form validation
- **Responsive:** Mobile-friendly design

---

## 🐛 Troubleshooting

### Database Tables Not Created
```bash
# Manually trigger table creation
curl -X POST http://localhost:8000/init-db
```

### Check Tables in Database
```bash
# Access database and run:
SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE '%legal%';
```

### CORS Issues
Ensure `CORS_ORIGINS` in `.env` includes your frontend URL:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Authentication Required
Get JWT token first:
```bash
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "password"
}
```

Use the `access_token` in subsequent requests.

---

## 📚 Additional Resources

- **Full Documentation:** `LEGAL_LITIGATION_IMPLEMENTATION.md`
- **API Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## ✅ Verification Checklist

Backend:
- [ ] Models imported in `main.py`
- [ ] Router registered in `main.py`
- [ ] Database tables created
- [ ] API endpoints accessible
- [ ] Swagger documentation visible

Frontend:
- [ ] Components created in `frontend/src/components/legal/`
- [ ] API service created in `frontend/src/services/legal/`
- [ ] Routes configured
- [ ] Dependencies installed (`antd`, `axios`, `react-router-dom`)

---

## 🎉 You're Ready!

The Legal - Litigation Management module is fully implemented and ready to use.

**Next Steps:**
1. Start the backend server
2. Start the frontend server
3. Navigate to `/legal/litigation`
4. Create your first case!

For detailed information, refer to `LEGAL_LITIGATION_IMPLEMENTATION.md`.

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Date:** January 11, 2025
