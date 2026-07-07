# Treasury & Cash Management - Implementation Quick Start Guide

## 🎯 Purpose

This guide provides a step-by-step plan to implement the Treasury & Cash Management module from scratch.

**Target Audience:** Development team, project managers  
**Timeline:** 4 weeks  
**Prerequisites:** Accounting module complete, team allocated  

---

## 📅 Week-by-Week Implementation Plan

### WEEK 1: Foundation & Core Infrastructure

#### Day 1: Project Setup
**Backend Tasks:**
- [ ] Create database models file: `backend/shared/database/treasury_models.py`
- [ ] Define all 10 table models (use accounting_models.py as reference)
- [ ] Add proper indexes and foreign keys
- [ ] Include audit fields (created_by, created_at, updated_by, updated_at)

**Models to Create:**
1. `TreasuryBankAccount` - Bank accounts master
2. `CashPosition` - Daily cash position tracking
3. `BankStatement` - Imported bank statements
4. `BankReconciliation` - Reconciliation headers
5. `ReconciliationItem` - Reconciliation line items
6. `FundTransfer` - Fund transfer requests
7. `LiquidityPosition` - Liquidity metrics
8. `Investment` - Investment portfolio
9. `InvestmentTransaction` - Investment movements
10. `CashFlowForecast` - Forecast data

**Estimated Time:** 8 hours

---

#### Day 2: Database Migration
**Backend Tasks:**
- [ ] Create migration file: `backend/alembic/versions/008_add_treasury_module.py`
- [ ] Write upgrade() function to create all tables
- [ ] Write downgrade() function for rollback
- [ ] Test migration in development environment
- [ ] Verify all indexes created
- [ ] Verify foreign keys working

**Migration Template:**
```python
"""Add treasury module tables

Revision ID: 008
Revises: 007
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '008'
down_revision = '007'

def upgrade():
    # Create treasury_bank_accounts table
    op.create_table(
        'treasury_bank_accounts',
        # ... columns ...
    )
    # Create other 9 tables
    # Add indexes
    # Add foreign keys

def downgrade():
    # Drop all tables in reverse order
    op.drop_table('cash_flow_forecasts')
    # ... drop other tables ...
```

**Estimated Time:** 6 hours

---

#### Day 3-4: Bank Accounts Service
**Backend Tasks:**
- [ ] Create: `backend/services/treasury/bank_account_service.py`
- [ ] Create: `backend/services/treasury/bank_account_schemas.py`
- [ ] Create: `backend/services/treasury/bank_account_router.py`

**Key Functions:**
```python
# bank_account_service.py
- create_bank_account()
- get_bank_account()
- list_bank_accounts()
- update_bank_account()
- activate/deactivate_account()
- get_current_balance()
- record_balance_update()
```

**API Endpoints (~12):**
```
POST   /api/v1/treasury/bank-accounts
GET    /api/v1/treasury/bank-accounts/{id}
GET    /api/v1/treasury/bank-accounts
PATCH  /api/v1/treasury/bank-accounts/{id}
DELETE /api/v1/treasury/bank-accounts/{id}
GET    /api/v1/treasury/bank-accounts/active
GET    /api/v1/treasury/bank-accounts/{id}/balance
POST   /api/v1/treasury/bank-accounts/{id}/update-balance
GET    /api/v1/treasury/bank-accounts/{id}/transactions
GET    /api/v1/treasury/bank-accounts/statistics
POST   /api/v1/treasury/bank-accounts/bulk-create
GET    /api/v1/treasury/bank-accounts/{id}/history
```

**Estimated Time:** 12 hours

---

#### Day 5: Cash Position Service
**Backend Tasks:**
- [ ] Create: `backend/services/treasury/cash_position_service.py`
- [ ] Create: `backend/services/treasury/cash_position_schemas.py`
- [ ] Create: `backend/services/treasury/cash_position_router.py`

**Key Functions:**
```python
# cash_position_service.py
- record_cash_position()
- get_current_position()
- get_branch_position()
- get_denomination_details()
- create_cash_transfer()
- get_cash_alerts()
- generate_cash_report()
```

**API Endpoints (~15):**
```
POST   /api/v1/treasury/cash-position/record
GET    /api/v1/treasury/cash-position/current
GET    /api/v1/treasury/cash-position/branch/{id}
GET    /api/v1/treasury/cash-position/date/{date}
GET    /api/v1/treasury/cash-position/denomination/{branch_id}
GET    /api/v1/treasury/cash-position/history
POST   /api/v1/treasury/cash-position/transfer
GET    /api/v1/treasury/cash-position/alerts
GET    /api/v1/treasury/cash-position/report
GET    /api/v1/treasury/cash-position/dashboard
```

**Estimated Time:** 10 hours

---

**Week 1 Deliverables:**
- ✅ 10 database tables created
- ✅ Database migration complete
- ✅ Bank accounts CRUD complete (~12 APIs)
- ✅ Cash position tracking complete (~15 APIs)
- ✅ ~27 API endpoints functional

**Total Week 1 Effort:** ~36 hours

---

### WEEK 2: Bank Reconciliation (Most Critical Feature)

#### Day 6-7: Reconciliation Service
**Backend Tasks:**
- [ ] Create: `backend/services/treasury/reconciliation_service.py`
- [ ] Create: `backend/services/treasury/reconciliation_schemas.py`
- [ ] Create: `backend/services/treasury/reconciliation_router.py`

**Key Functions:**
```python
# reconciliation_service.py
- upload_bank_statement()  # Parse Excel/CSV
- parse_statement_file()
- create_reconciliation()
- auto_match_transactions()  # Match with GL entries
- manual_match_transaction()
- mark_outstanding_items()
- generate_brs_report()
- approve_reconciliation()
- get_unmatched_items()
```

**Auto-Matching Logic:**
```python
def auto_match_transactions(reconciliation_id):
    # Match criteria (in priority order):
    # 1. Exact amount + date + reference number
    # 2. Exact amount + date within ±2 days
    # 3. Amount within ±₹10 + date match
    # 4. Reference number partial match
    
    # Mark matched items
    # Create reconciliation_items records
    # Return match statistics
```

**API Endpoints (~20):**
```
POST   /api/v1/treasury/reconciliation/create
POST   /api/v1/treasury/reconciliation/upload-statement
POST   /api/v1/treasury/reconciliation/auto-match
POST   /api/v1/treasury/reconciliation/manual-match
GET    /api/v1/treasury/reconciliation/{id}
GET    /api/v1/treasury/reconciliation/list
GET    /api/v1/treasury/reconciliation/unmatched
GET    /api/v1/treasury/reconciliation/outstanding-items
POST   /api/v1/treasury/reconciliation/approve
POST   /api/v1/treasury/reconciliation/reject
GET    /api/v1/treasury/reconciliation/report/{id}
POST   /api/v1/treasury/reconciliation/mark-cleared
GET    /api/v1/treasury/reconciliation/statistics
GET    /api/v1/treasury/reconciliation/pending-approval
PATCH  /api/v1/treasury/reconciliation/{id}
DELETE /api/v1/treasury/reconciliation/{id}
```

**Estimated Time:** 16 hours

---

#### Day 8-9: Reconciliation Frontend
**Frontend Tasks:**
- [ ] Create: `frontend/apps/admin-portal/src/services/treasury/reconciliation.service.ts`
- [ ] Create: `frontend/apps/admin-portal/src/app/treasury/reconciliation/page.tsx`
- [ ] Create: `frontend/apps/admin-portal/src/app/treasury/reconciliation/[id]/page.tsx`

**UI Components:**
1. **Reconciliation List Page**
   - List of all reconciliations (table)
   - Filters: date, bank account, status
   - Statistics cards: Total, Matched, Unmatched, Pending
   - New reconciliation button

2. **Reconciliation Detail Page**
   - Bank statement items (left side)
   - GL entries (right side)
   - Matching interface (drag & drop or click)
   - Auto-match button
   - Outstanding items section
   - Approve/Reject buttons
   - BRS report preview

3. **Upload Statement Modal**
   - File upload (Excel/CSV)
   - Bank account selection
   - Date range
   - Preview uploaded data
   - Submit button

**Key Features:**
```typescript
// reconciliation.service.ts
export class ReconciliationService {
  uploadStatement(file: File, accountId: string)
  autoMatch(reconciliationId: string)
  manualMatch(itemId: string, glEntryId: string)
  getUnmatched(reconciliationId: string)
  approveReconciliation(reconciliationId: string)
  generateReport(reconciliationId: string)
}
```

**Estimated Time:** 16 hours

---

#### Day 10: Testing & Refinement
**Tasks:**
- [ ] Test bank statement upload (Excel, CSV formats)
- [ ] Test auto-matching algorithm with sample data
- [ ] Test manual matching interface
- [ ] Verify reconciliation approval workflow
- [ ] Test report generation
- [ ] Fix any bugs found
- [ ] Performance optimization

**Estimated Time:** 8 hours

---

**Week 2 Deliverables:**
- ✅ Bank reconciliation backend complete (~20 APIs)
- ✅ Statement upload & parsing working
- ✅ Auto-matching engine functional (80%+ accuracy)
- ✅ Manual matching interface complete
- ✅ Reconciliation approval workflow
- ✅ BRS report generation
- ✅ Complete UI with all features

**Total Week 2 Effort:** ~40 hours

---

### WEEK 3: Fund Transfers & Operations

#### Day 11-12: Fund Transfer Service
**Backend Tasks:**
- [ ] Create: `backend/services/treasury/fund_transfer_service.py`
- [ ] Create: `backend/services/treasury/fund_transfer_schemas.py`
- [ ] Create: `backend/services/treasury/fund_transfer_router.py`

**Key Functions:**
```python
# fund_transfer_service.py
- create_transfer_request()
- approve_transfer()
- reject_transfer()
- execute_transfer()  # Integrate with payment gateway
- schedule_transfer()
- bulk_transfer()
- get_transfer_status()
- retry_failed_transfer()
- cancel_transfer()
```

**Transfer Types:**
1. Internal (Branch to Branch)
2. NEFT (National Electronic Funds Transfer)
3. RTGS (Real Time Gross Settlement)
4. IMPS (Immediate Payment Service)

**API Endpoints (~18):**
```
POST   /api/v1/treasury/transfers/create
GET    /api/v1/treasury/transfers/{id}
GET    /api/v1/treasury/transfers/list
POST   /api/v1/treasury/transfers/approve
POST   /api/v1/treasury/transfers/reject
POST   /api/v1/treasury/transfers/execute
POST   /api/v1/treasury/transfers/cancel
POST   /api/v1/treasury/transfers/schedule
POST   /api/v1/treasury/transfers/bulk
GET    /api/v1/treasury/transfers/pending
GET    /api/v1/treasury/transfers/status/{id}
POST   /api/v1/treasury/transfers/retry
GET    /api/v1/treasury/transfers/limits
GET    /api/v1/treasury/transfers/report
GET    /api/v1/treasury/transfers/statistics
```

**Estimated Time:** 12 hours

---

#### Day 13: Fund Transfer Frontend
**Frontend Tasks:**
- [ ] Create: `frontend/apps/admin-portal/src/services/treasury/transfer.service.ts`
- [ ] Create: `frontend/apps/admin-portal/src/app/treasury/transfers/page.tsx`
- [ ] Create: Transfer creation form component
- [ ] Create: Transfer approval modal
- [ ] Create: Bulk transfer upload

**UI Components:**
1. **Transfers List Page**
   - All transfers table
   - Tabs: All, Pending, Approved, Executed, Failed
   - Filters: date, type, amount range
   - Statistics cards
   - New transfer button

2. **Create Transfer Form**
   - Transfer type selection
   - Source account dropdown
   - Destination account (internal) or beneficiary details (external)
   - Amount
   - Purpose
   - Schedule date (optional)
   - Submit for approval

3. **Approval Queue**
   - List of pending transfers
   - Transfer details modal
   - Approve/Reject with remarks
   - Bulk approval

**Estimated Time:** 12 hours

---

#### Day 14-15: Treasury Dashboard
**Frontend Tasks:**
- [ ] Create: `frontend/apps/admin-portal/src/app/treasury/dashboard/page.tsx`
- [ ] Create: Dashboard service
- [ ] Add charts library (recharts/chart.js)

**Dashboard Components:**
1. **Summary Cards** (Top row)
   - Total cash position
   - Total bank balances
   - Pending transfers
   - Outstanding reconciliation items

2. **Cash Position Chart**
   - Branch-wise bar chart
   - Denomination pie chart
   - Trend line (last 30 days)

3. **Bank Balances**
   - Account-wise balance table
   - Low balance alerts
   - Account status

4. **Recent Activities**
   - Latest transfers
   - Recent reconciliations
   - Pending approvals

5. **Alerts & Notifications**
   - Cash shortage alerts
   - Reconciliation pending
   - Transfer failures
   - Investment maturities

**Estimated Time:** 12 hours

---

**Week 3 Deliverables:**
- ✅ Fund transfer module complete (~18 APIs)
- ✅ Transfer creation & approval workflow
- ✅ Internal & external transfers
- ✅ Bulk transfer capability
- ✅ Treasury dashboard with visualizations
- ✅ Complete UI for all operations

**Total Week 3 Effort:** ~36 hours

---

### WEEK 4: Liquidity, Investments & Forecasting

#### Day 16-17: Liquidity Management
**Backend Tasks:**
- [ ] Create: `backend/services/treasury/liquidity_service.py`
- [ ] Create: `backend/services/treasury/liquidity_schemas.py`
- [ ] Create: `backend/services/treasury/liquidity_router.py`

**Key Functions:**
```python
# liquidity_service.py
- calculate_liquidity_ratios()  # LCR, NSFR, etc.
- generate_maturity_ladder()
- calculate_gaps()
- forecast_liquidity()
- run_stress_test()
- generate_alm_report()
```

**Calculations:**
```python
# Liquidity Coverage Ratio (LCR)
LCR = (High Quality Liquid Assets) / (Net Cash Outflows over 30 days) × 100
Target: ≥ 100%

# Net Stable Funding Ratio (NSFR)
NSFR = (Available Stable Funding) / (Required Stable Funding) × 100
Target: ≥ 100%

# Maturity Ladder
Buckets: 0-7 days, 8-14 days, 15-30 days, 1-3 months, 3-6 months, 6-12 months, 1-3 years, 3-5 years, >5 years
```

**API Endpoints (~12):**
```
GET    /api/v1/treasury/liquidity/current
GET    /api/v1/treasury/liquidity/ratios
GET    /api/v1/treasury/liquidity/maturity-ladder
GET    /api/v1/treasury/liquidity/gaps
POST   /api/v1/treasury/liquidity/forecast
GET    /api/v1/treasury/liquidity/stress-test
GET    /api/v1/treasury/liquidity/dashboard
GET    /api/v1/treasury/liquidity/regulatory-report
GET    /api/v1/treasury/liquidity/alerts
```

**Estimated Time:** 12 hours

---

#### Day 18: Investment Tracking
**Backend Tasks:**
- [ ] Create: `backend/services/treasury/investment_service.py`
- [ ] Create: `backend/services/treasury/investment_schemas.py`
- [ ] Create: `backend/services/treasury/investment_router.py`

**Key Functions:**
```python
# investment_service.py
- create_investment()
- record_purchase()
- record_sale()
- record_income()  # Interest, dividend
- calculate_mtm()  # Mark-to-Market
- get_portfolio_performance()
- get_maturing_investments()
- approve_investment()
```

**Investment Types:**
- Fixed Deposits
- Government Securities (G-Sec)
- Corporate Bonds
- Mutual Funds
- Commercial Papers
- Certificate of Deposits

**API Endpoints (~20):**
```
POST   /api/v1/treasury/investments/create
GET    /api/v1/treasury/investments/{id}
GET    /api/v1/treasury/investments/list
PATCH  /api/v1/treasury/investments/{id}
POST   /api/v1/treasury/investments/{id}/mature
POST   /api/v1/treasury/investments/{id}/sell
POST   /api/v1/treasury/investments/income
GET    /api/v1/treasury/investments/portfolio
GET    /api/v1/treasury/investments/maturing/{days}
GET    /api/v1/treasury/investments/performance
POST   /api/v1/treasury/investments/mtm-valuation
GET    /api/v1/treasury/investments/alerts
GET    /api/v1/treasury/investments/report
POST   /api/v1/treasury/investments/approve
GET    /api/v1/treasury/investments/pending-approval
```

**Estimated Time:** 12 hours

---

#### Day 19: Cash Flow Forecasting
**Backend Tasks:**
- [ ] Create: `backend/services/treasury/forecast_service.py`
- [ ] Create: `backend/services/treasury/forecast_schemas.py`
- [ ] Create: `backend/services/treasury/forecast_router.py`

**Key Functions:**
```python
# forecast_service.py
- create_forecast()
- record_inflows()  # Expected loan repayments, deposit maturities
- record_outflows()  # Expected loan disbursements, withdrawals
- calculate_net_position()
- create_scenario()  # Best case, worst case, expected
- calculate_variance()  # Actual vs forecast
- generate_forecast_report()
```

**Forecast Periods:**
- Daily (next 30 days)
- Weekly (next 12 weeks)
- Monthly (next 12 months)
- Quarterly (next 8 quarters)

**API Endpoints (~15):**
```
POST   /api/v1/treasury/forecast/create
GET    /api/v1/treasury/forecast/{id}
GET    /api/v1/treasury/forecast/list
GET    /api/v1/treasury/forecast/current-period
POST   /api/v1/treasury/forecast/scenario
POST   /api/v1/treasury/forecast/inflows
POST   /api/v1/treasury/forecast/outflows
GET    /api/v1/treasury/forecast/variance
GET    /api/v1/treasury/forecast/dashboard
GET    /api/v1/treasury/forecast/stress-test
GET    /api/v1/treasury/forecast/report
```

**Estimated Time:** 10 hours

---

#### Day 20: Frontend Pages & Testing
**Frontend Tasks:**
- [ ] Create liquidity management page
- [ ] Create investment portfolio page
- [ ] Create cash flow forecast page
- [ ] Integration testing (all modules)
- [ ] Performance testing
- [ ] Bug fixes
- [ ] Documentation updates

**Pages to Create:**
1. `/treasury/liquidity` - Ratios, maturity ladder, gaps
2. `/treasury/investments` - Portfolio list, performance
3. `/treasury/forecast` - Forecast dashboard, variance

**Final Testing:**
- [ ] Test all API endpoints
- [ ] Test all UI pages
- [ ] Test integrations (accounting GL)
- [ ] Test approvals workflow
- [ ] Test multi-tenant isolation
- [ ] Performance testing (load 1000+ transactions)
- [ ] Security testing
- [ ] UAT preparation

**Estimated Time:** 12 hours

---

**Week 4 Deliverables:**
- ✅ Liquidity management complete (~12 APIs)
- ✅ Investment tracking complete (~20 APIs)
- ✅ Cash flow forecasting complete (~15 APIs)
- ✅ All frontend pages complete
- ✅ Complete testing & bug fixes
- ✅ Documentation updated

**Total Week 4 Effort:** ~46 hours

---

## 📊 Complete Implementation Summary

### Total Deliverables (4 Weeks)

**Backend:**
- ✅ 10 database tables
- ✅ 1 database migration
- ✅ 6 service files (~2,500 lines)
- ✅ 6 router files (~2,500 lines)
- ✅ 6 schema files (~2,000 lines)
- ✅ ~100 API endpoints
- ✅ Integration with accounting GL

**Frontend:**
- ✅ 6 service files (~2,500 lines)
- ✅ 7 pages (~3,500 lines)
- ✅ 15+ forms
- ✅ Dashboard with charts
- ✅ All CRUD operations

**Total Code:** ~13,000+ lines of production-ready code

**Total Effort:**
- Week 1: 36 hours (Foundation)
- Week 2: 40 hours (Reconciliation)
- Week 3: 36 hours (Transfers & Dashboard)
- Week 4: 46 hours (Liquidity, Investment, Forecast)
- **Total: 158 hours (~20 working days)**

---

## 🔧 Technical Stack

### Backend
```python
# Required packages (already in requirements.txt)
- FastAPI
- SQLAlchemy
- Pydantic
- pandas (for Excel/CSV parsing)
- openpyxl (for Excel)
- python-multipart (for file upload)
```

### Frontend
```typescript
// Required packages
- React 18+
- TypeScript
- TailwindCSS
- Shadcn/ui components
- React Hook Form
- Zod validation
- Recharts (for charts)
- xlsx (for Excel export)
```

---

## 💻 Code Templates

### Backend Service Template
```python
# backend/services/treasury/example_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
import logging

from backend.shared.database.treasury_models import TreasuryBankAccount
from . import example_schemas as schemas

logger = logging.getLogger(__name__)

class ExampleService:
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def create_item(self, data: schemas.ItemCreate) -> TreasuryBankAccount:
        """Create new item"""
        try:
            db_item = TreasuryBankAccount(
                tenant_id=self.tenant_id,
                created_by=self.user_id,
                **data.dict()
            )
            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)
            
            logger.info(f"Created item: {db_item.id}")
            return db_item
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating item: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_item(self, item_id: int) -> TreasuryBankAccount:
        """Get item by ID"""
        item = self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.id == item_id,
            TreasuryBankAccount.tenant_id == self.tenant_id
        ).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return item
    
    def list_items(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[TreasuryBankAccount]:
        """List items with filters"""
        query = self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.tenant_id == self.tenant_id
        )
        
        if status:
            query = query.filter(TreasuryBankAccount.status == status)
        
        return query.offset(skip).limit(limit).all()
```

### Backend Router Template
```python
# backend/services/treasury/example_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from . import example_service as service
from . import example_schemas as schemas

router = APIRouter(prefix="/example", tags=["Treasury Example"])

@router.post("/", response_model=schemas.ItemResponse)
def create_item(
    data: schemas.ItemCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new item"""
    svc = service.ExampleService(db, current_user.tenant_id, current_user.id)
    return svc.create_item(data)

@router.get("/{item_id}", response_model=schemas.ItemResponse)
def get_item(
    item_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get item by ID"""
    svc = service.ExampleService(db, current_user.tenant_id, current_user.id)
    return svc.get_item(item_id)

@router.get("/", response_model=List[schemas.ItemResponse])
def list_items(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List items with filters"""
    svc = service.ExampleService(db, current_user.tenant_id, current_user.id)
    return svc.list_items(skip, limit, status)
```

### Frontend Service Template
```typescript
// frontend/apps/admin-portal/src/services/treasury/example.service.ts
import { api } from '@/lib/api';

export interface ItemCreate {
  name: string;
  description?: string;
  status: string;
}

export interface ItemResponse {
  id: number;
  tenant_id: number;
  name: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export class ExampleService {
  private baseUrl = '/api/v1/treasury/example';

  async createItem(data: ItemCreate): Promise<ItemResponse> {
    const response = await api.post<ItemResponse>(this.baseUrl, data);
    return response.data;
  }

  async getItem(id: number): Promise<ItemResponse> {
    const response = await api.get<ItemResponse>(`${this.baseUrl}/${id}`);
    return response.data;
  }

  async listItems(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<ItemResponse[]> {
    const response = await api.get<ItemResponse[]>(this.baseUrl, { params });
    return response.data;
  }

  async updateItem(id: number, data: Partial<ItemCreate>): Promise<ItemResponse> {
    const response = await api.patch<ItemResponse>(`${this.baseUrl}/${id}`, data);
    return response.data;
  }

  async deleteItem(id: number): Promise<void> {
    await api.delete(`${this.baseUrl}/${id}`);
  }
}

export const exampleService = new ExampleService();
```

---

## ✅ Daily Checklist Template

Use this for daily standup and tracking:

```markdown
## Day X: [Feature Name]

### Tasks
- [ ] Backend: Service implementation
- [ ] Backend: Schema definitions
- [ ] Backend: Router endpoints
- [ ] Frontend: Service file
- [ ] Frontend: UI page
- [ ] Testing: API testing
- [ ] Testing: UI testing
- [ ] Documentation: API docs update

### Progress
- Completed: [list]
- In Progress: [list]
- Blocked: [list]

### Metrics
- APIs Implemented: X/Y
- Lines of Code: ~Z
- Time Spent: A hours
- Issues Found: N

### Notes
- [Any important notes or decisions]
```

---

## 🎯 Success Criteria

### Ready for UAT When:
- [ ] All 100+ APIs functional
- [ ] All 7 frontend pages working
- [ ] Bank statement upload working
- [ ] Auto-matching achieving 75%+ accuracy
- [ ] Fund transfer approval workflow functional
- [ ] Dashboard showing real-time data
- [ ] All integrations tested
- [ ] No critical bugs
- [ ] Performance acceptable (<2s page load)
- [ ] Documentation complete

### Ready for Production When:
- [ ] UAT sign-off received
- [ ] All bugs fixed
- [ ] Performance optimized
- [ ] Security review passed
- [ ] User training completed
- [ ] Rollback plan tested
- [ ] Monitoring setup
- [ ] Support team briefed

---

## 📞 Support & Resources

**Reference Implementations:**
- Accounting module: `backend/services/accounting/`
- LMS extensions: `backend/services/lms/`
- Collection module: `backend/services/collection/`

**Documentation:**
- Master Index: `docs/MASTER_INDEX.md`
- Gap Analysis: `docs/TREASURY_CASH_MANAGEMENT_GAP_ANALYSIS.md`
- Status Report: `TREASURY_MODULE_STATUS.md`

**Tools:**
- Swagger UI: http://localhost:8000/docs
- Database viewer: pgAdmin/DBeaver
- API testing: Postman/Thunder Client

---

## 🚀 Getting Started

1. **Review Documents**
   - Read gap analysis
   - Review status report
   - Study this quick start guide

2. **Set Up Environment**
   - Pull latest code
   - Create feature branch: `feature/treasury-module`
   - Set up database for migration

3. **Start Week 1**
   - Create models file
   - Write migration
   - Implement bank accounts service
   - Begin cash position service

4. **Daily Standup**
   - Share progress
   - Identify blockers
   - Request help if needed

---

**READY TO START IMPLEMENTATION? LET'S BUILD! 🚀**

**First Task:** Create `backend/shared/database/treasury_models.py`

Good luck! 💪
