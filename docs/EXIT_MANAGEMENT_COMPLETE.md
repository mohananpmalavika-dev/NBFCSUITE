# Exit Management System - Complete Technical Documentation

**Module**: HRMS - Exit Management  
**Version**: 1.0.0  
**Last Updated**: December 2024  
**Status**: Production Ready ✅

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [Backend Implementation](#backend-implementation)
5. [Frontend Implementation](#frontend-implementation)
6. [API Endpoints](#api-endpoints)
7. [Business Logic](#business-logic)
8. [Security & Authentication](#security--authentication)
9. [Testing](#testing)
10. [Deployment](#deployment)

---

## Overview

The Exit Management System is a comprehensive module for managing employee resignations, exit clearances, Full & Final settlements, and exit documentation. It provides end-to-end workflow automation from resignation submission to final settlement payment.

### Key Features

- **Resignation Workflow Management**
  - Multi-stage approval process (Employee → Manager → HR → Final Approval)
  - Counter offer management
  - Resignation withdrawal support
  - Notice period tracking

- **Exit Clearance Tracking**
  - 5 default clearance types (IT, Admin, Finance, HR, Manager)
  - Customizable clearance checklists
  - Overdue detection and escalation
  - Dependency management between clearances

- **Full & Final Settlement**
  - Automated calculation of earnings and deductions
  - Components: Salary, Leave encashment, Gratuity, Bonus, Recoveries, Tax
  - Multi-level approval workflow
  - Payment tracking and reconciliation

- **Document Management**
  - Automated document generation from templates
  - Experience Letter, Relieving Letter, Service Certificate
  - Digital signature support
  - Delivery tracking and employee acknowledgment

- **Dashboard & Analytics**
  - Real-time statistics
  - Resignation trends
  - Settlement summaries
  - Clearance status overview

---

## Architecture

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL 13+
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Authentication**: JWT with role-based access control
- **Architecture**: Multi-tenant (tenant isolation at database level)

#### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript 5.0+
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **Routing**: Next.js App Router

### System Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│   API Layer     │
│   (FastAPI)     │
└────────┬────────┘
         │
         │ SQLAlchemy
         │
┌────────▼────────┐
│   Database      │
│  (PostgreSQL)   │
└─────────────────┘
```

---

## Database Schema

### Tables (5 Total)

#### 1. exit_resignations
Primary table storing all resignation records.

**Key Columns:**
- `id` (UUID, PK)
- `tenant_id` (UUID)
- `resignation_code` (VARCHAR, Unique)
- `employee_id` (UUID, FK)
- `resignation_type` (ENUM)
- `resignation_date` (DATE)
- `last_working_date` (DATE)
- `status` (ENUM)
- Workflow fields (manager_review, hr_review, approval, etc.)
- Exit interview and handover fields
- Audit fields

**Indexes:**
- idx_exit_resignations_tenant
- idx_exit_resignations_employee
- idx_exit_resignations_status
- idx_exit_resignations_dates

#### 2. exit_clearances
Stores clearance records for each resignation.

**Key Columns:**
- `id` (UUID, PK)
- `resignation_id` (UUID, FK)
- `clearance_from` (VARCHAR)
- `clearance_type` (VARCHAR)
- `status` (ENUM)
- `is_mandatory` (BOOLEAN)
- `due_date` (DATE)
- `is_overdue` (BOOLEAN)
- Checklist and completion fields

**Indexes:**
- idx_exit_clearances_resignation
- idx_exit_clearances_status
- idx_exit_clearances_assigned

#### 3. exit_settlements
Stores Full & Final settlement records.

**Key Columns:**
- `id` (UUID, PK)
- `resignation_id` (UUID, FK)
- `settlement_code` (VARCHAR, Unique)
- `status` (ENUM)
- Earnings fields (salary, leaves, gratuity, bonus)
- Deduction fields (recoveries, tax)
- Calculated totals (gross_payable, total_deductions, net_payable)
- Workflow and payment fields

**Indexes:**
- idx_exit_settlements_resignation
- idx_exit_settlements_employee
- idx_exit_settlements_status

#### 4. exit_settlement_components
Stores individual settlement components.

**Key Columns:**
- `id` (UUID, PK)
- `settlement_id` (UUID, FK)
- `component_type` (ENUM)
- `component_name` (VARCHAR)
- `amount` (DECIMAL)
- `is_deduction` (BOOLEAN)
- `is_taxable` (BOOLEAN)

#### 5. exit_documents
Stores exit-related documents.

**Key Columns:**
- `id` (UUID, PK)
- `resignation_id` (UUID, FK)
- `document_code` (VARCHAR, Unique)
- `document_type` (ENUM)
- `is_generated` (BOOLEAN)
- `is_approved` (BOOLEAN)
- `is_issued` (BOOLEAN)
- Generation, approval, and issuance fields

### Enums (6 Total)

1. **resignation_type**: voluntary, involuntary, retirement, absconding, end_of_contract, mutual_consent
2. **resignation_status**: submitted, under_review, approved, rejected, withdrawn, completed, cancelled
3. **clearance_status**: pending, in_progress, completed, not_applicable, waived
4. **settlement_status**: pending, calculated, approved, processing, paid, on_hold, rejected
5. **settlement_component_type**: salary, leave_encashment, notice_pay, bonus, gratuity, reimbursement, recovery, other
6. **exit_document_type**: resignation_letter, acceptance_letter, experience_letter, relieving_letter, service_certificate, noc, clearance_form, fnf_statement, form_16, pf_withdrawal, gratuity_form, other

### Helper Functions (3 Total)

1. **calculate_settlement_net_payable()**: Automatically calculates net payable on settlement updates
2. **check_all_clearances_completed()**: Verifies if all mandatory clearances are completed
3. **update_clearance_overdue_status()**: Updates overdue status for clearances past due date

---

## Backend Implementation

### Project Structure

```
backend/
├── shared/
│   └── database/
│       └── hrms_models.py          # Database models
├── services/
│   └── hrms/
│       ├── schemas/
│       │   └── exit_schemas.py      # Pydantic schemas (45+)
│       ├── services/
│       │   └── exit_service.py      # Business logic (43+ methods)
│       └── routes/
│           └── exit_routes.py       # API routes (33 endpoints)
└── main.py                          # Route registration
```

### Service Layer Methods

#### Resignation Service (12 methods)
- `create_resignation()` - Create new resignation
- `get_resignation()` - Get resignation by ID
- `list_resignations()` - List with filters and pagination
- `update_resignation()` - Update resignation details
- `manager_review()` - Submit manager review
- `hr_review()` - Submit HR review
- `approve_resignation()` - Approve resignation
- `reject_resignation()` - Reject resignation
- `withdraw_resignation()` - Withdraw resignation
- `conduct_exit_interview()` - Record exit interview
- `complete_handover()` - Mark handover complete
- `complete_exit()` - Complete entire exit process

#### Clearance Service (5 methods)
- `create_clearance()` - Create new clearance
- `get_clearance()` - Get clearance by ID
- `list_clearances()` - List with filters
- `update_clearance()` - Update clearance
- `complete_clearance()` - Mark clearance complete

#### Settlement Service (7 methods)
- `create_settlement()` - Create new settlement
- `get_settlement()` - Get settlement by ID
- `get_settlement_by_resignation()` - Get by resignation ID
- `calculate_settlement()` - Calculate amounts
- `approve_settlement()` - Approve settlement
- `process_payment()` - Process payment
- `hold_settlement()` - Put settlement on hold

#### Document Service (6 methods)
- `create_document()` - Create document record
- `generate_document()` - Generate from template
- `approve_document()` - Approve document
- `issue_document()` - Issue document to employee
- `get_document()` - Get document by ID
- `list_documents()` - List with filters

---

## Frontend Implementation

### Project Structure

```
frontend/apps/admin-portal/src/
├── types/
│   └── exit.types.ts               # TypeScript types (45+ interfaces)
├── services/
│   └── exit.service.ts             # API service layer (39 methods)
└── components/
    └── exit/
        ├── ExitStatusBadge.tsx
        ├── ResignationWorkflowStepper.tsx
        ├── ClearanceChecklist.tsx
        ├── SettlementBreakdown.tsx
        ├── DocumentPreview.tsx
        └── index.ts
```

### UI Components

#### 1. ExitStatusBadge
Color-coded status badges for all entity types.

**Props:**
- `status`: Status value
- `type`: 'resignation' | 'clearance' | 'settlement'
- `size`: 'sm' | 'md' | 'lg'

#### 2. ResignationWorkflowStepper
Visual workflow stepper showing progress through resignation stages.

**Props:**
- `currentStatus`: Current resignation status
- `className`: Optional CSS classes

#### 3. ClearanceChecklist
Interactive checklist for managing exit clearances.

**Props:**
- `clearances`: Array of clearance objects
- `onComplete`: Callback for clearance completion
- `readOnly`: Boolean for view-only mode

#### 4. SettlementBreakdown
Comprehensive settlement breakdown display.

**Props:**
- `settlement`: Settlement object
- `components`: Array of settlement components
- `showDetails`: Boolean to show/hide details

#### 5. DocumentPreview
Document preview and management card.

**Props:**
- `document`: Document object
- `onDownload`: Download callback
- `onApprove`: Approve callback
- `onIssue`: Issue callback
- `readOnly`: Boolean for view-only mode

---

## API Endpoints

### Base URL: `/api/v1/hrms/exit`

### Resignations (12 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/resignations` | Create resignation |
| GET | `/resignations` | List resignations (with filters) |
| GET | `/resignations/{id}` | Get resignation by ID |
| PUT | `/resignations/{id}` | Update resignation |
| POST | `/resignations/{id}/manager-review` | Manager review |
| POST | `/resignations/{id}/hr-review` | HR review |
| POST | `/resignations/{id}/approve` | Approve resignation |
| POST | `/resignations/{id}/reject` | Reject resignation |
| POST | `/resignations/{id}/withdraw` | Withdraw resignation |
| POST | `/resignations/{id}/exit-interview` | Exit interview |
| POST | `/resignations/{id}/handover` | Complete handover |
| POST | `/resignations/{id}/complete` | Complete exit |

### Clearances (5 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/clearances` | Create clearance |
| GET | `/clearances` | List clearances (with filters) |
| GET | `/clearances/{id}` | Get clearance by ID |
| PUT | `/clearances/{id}` | Update clearance |
| POST | `/clearances/{id}/complete` | Complete clearance |

### Settlements (7 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/settlements` | Create settlement |
| GET | `/settlements` | List settlements (with filters) |
| GET | `/settlements/{id}` | Get settlement by ID |
| GET | `/settlements/resignation/{id}` | Get by resignation |
| POST | `/settlements/{id}/calculate` | Calculate settlement |
| POST | `/settlements/{id}/approve` | Approve settlement |
| POST | `/settlements/{id}/payment` | Process payment |
| POST | `/settlements/{id}/hold` | Put on hold |

### Documents (6 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents` | Create document |
| GET | `/documents` | List documents (with filters) |
| GET | `/documents/{id}` | Get document by ID |
| POST | `/resignations/{id}/documents/generate` | Generate document |
| POST | `/documents/{id}/approve` | Approve document |
| POST | `/documents/{id}/issue` | Issue document |

### Dashboard (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/stats` | Get dashboard statistics |

---

## Business Logic

### Resignation Workflow

```
1. Employee submits resignation
   ↓
2. Manager reviews (approve/reject/counter-offer)
   ↓
3. HR reviews (eligibility check)
   ↓
4. Final approval
   ↓
5. Clearances initiated
   ↓
6. Settlement calculated
   ↓
7. Documents generated
   ↓
8. Exit interview conducted
   ↓
9. Handover completed
   ↓
10. Settlement paid
    ↓
11. Documents issued
    ↓
12. Exit completed
```

### Settlement Calculation Logic

**Earnings:**
- Basic Salary (pro-rata for partial month)
- Leave Encashment (encashable leaves × daily rate)
- Gratuity (if eligible: years of service × formula)
- Bonus & Incentives
- Pending Reimbursements

**Deductions:**
- Notice Pay Recovery (shortfall days × daily rate)
- Loan Recovery
- Advance Recovery
- Asset Loss Recovery
- TDS (as per tax slab)
- Professional Tax

**Formula:**
```
Net Payable = Gross Payable - Total Deductions
```

### Clearance Dependencies

Clearances can have dependencies. For example:
- Finance clearance depends on Manager clearance
- HR clearance depends on all other clearances

### Document Templates

Pre-built templates for:
1. **Experience Letter**: Employment duration, designation, responsibilities
2. **Relieving Letter**: Official relieving confirmation
3. **Service Certificate**: Service record summary

---

## Security & Authentication

### Authentication
- JWT token-based authentication
- Token expiration: Configurable (default 24 hours)
- Refresh token support

### Authorization
- Role-based access control (RBAC)
- Roles: Employee, Manager, HR, Finance, Admin
- Permission checks at service layer

### Data Security
- Tenant isolation at database level
- Encrypted sensitive fields
- Audit trails on all operations
- Soft delete support

### API Security
- Input validation at Pydantic schema level
- SQL injection prevention (parameterized queries)
- XSS protection
- CORS configuration
- Rate limiting support

---

## Testing

### Unit Tests
Location: `tests/unit/hrms/exit/`

Test coverage:
- Service layer methods
- Schema validation
- Business logic calculations

### Integration Tests
Location: `tests/integration/hrms/exit/`

Test coverage:
- API endpoint responses
- Database transactions
- Workflow state transitions

### API Tests
Script: `scripts/test_exit_api.py`

Features:
- 33 endpoint tests
- Request/response validation
- Status code verification
- Success rate tracking

### Manual Testing
Use seed script to create test data:
```bash
python scripts/seed_exit_data.py
```

---

## Deployment

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Node.js 18+ (for frontend)

### Backend Deployment

1. **Run Configuration Script**
```bash
python scripts/configure_exit_management.py
```

2. **Run Migration**
```bash
psql -U postgres -d nbfc_db -f database/migrations/add_exit_management_tables.sql
```

3. **Verify Deployment**
```bash
python scripts/verify_exit_deployment.py
```

4. **Seed Test Data** (optional)
```bash
python scripts/seed_exit_data.py
```

### Frontend Deployment

1. **Install Dependencies**
```bash
cd frontend/apps/admin-portal
npm install
```

2. **Build**
```bash
npm run build
```

3. **Start**
```bash
npm start
```

### Environment Variables

**.env (Backend)**
```bash
DATABASE_URL=postgresql://user:pass@localhost/dbname
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
API_V1_PREFIX=/api/v1
```

**.env.local (Frontend)**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000
```

### Health Checks

1. Database: Check table existence
2. API: GET `/health` or `/docs`
3. Frontend: Access dashboard

### Monitoring

Recommended metrics to monitor:
- API response times
- Database query performance
- Error rates
- Active resignations count
- Pending clearances
- Settlement processing time

---

## Performance Optimization

### Database
- 20+ indexes for fast queries
- Connection pooling
- Query optimization with select_related

### API
- Pagination on all list endpoints
- Lazy loading of related data
- Caching for dashboard statistics

### Frontend
- Code splitting
- Lazy loading of components
- Memoization of expensive calculations

---

## Troubleshooting

### Common Issues

**1. Migration fails**
- Check PostgreSQL version (13+ required)
- Verify database permissions
- Check if tables already exist

**2. API returns 401**
- Verify JWT token is valid
- Check token expiration
- Ensure Authorization header is set

**3. Settlement calculation incorrect**
- Verify employee salary data
- Check leave balance accuracy
- Review calculation parameters

**4. Documents not generating**
- Check template availability
- Verify document type enum
- Review generation logs

---

## Support & Maintenance

### Logs
- Backend: `logs/exit_management.log`
- Database: PostgreSQL logs
- Frontend: Browser console

### Backup
Regular backup of:
- `exit_resignations` table
- `exit_settlements` table
- Generated documents directory

### Updates
- Schema changes: Create new migration scripts
- API changes: Update OpenAPI spec
- Frontend changes: Update TypeScript types

---

## Appendix

### File Locations

**Backend:**
- Models: `backend/shared/database/hrms_models.py`
- Migration: `database/migrations/add_exit_management_tables.sql`
- Schemas: `backend/services/hrms/schemas/exit_schemas.py`
- Services: `backend/services/hrms/services/exit_service.py`
- Routes: `backend/services/hrms/routes/exit_routes.py`

**Frontend:**
- Types: `frontend/apps/admin-portal/src/types/exit.types.ts`
- Services: `frontend/apps/admin-portal/src/services/exit.service.ts`
- Components: `frontend/apps/admin-portal/src/components/exit/`

**Scripts:**
- Configure: `scripts/configure_exit_management.py`
- Seed: `scripts/seed_exit_data.py`
- Test: `scripts/test_exit_api.py`
- Verify: `scripts/verify_exit_deployment.py`

**Documentation:**
- This file: `docs/EXIT_MANAGEMENT_COMPLETE.md`
- Setup Guide: `docs/EXIT_MANAGEMENT_SETUP_GUIDE.md`
- User Guide: `docs/EXIT_MANAGEMENT_USER_GUIDE.md`
- Quick Reference: `docs/EXIT_MANAGEMENT_QUICK_REFERENCE.md`

---

**Document Version**: 1.0.0  
**Last Updated**: December 2024  
**Maintained By**: NBFC Suite Development Team
