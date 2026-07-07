# Treasury Module - Quick Reference Guide

**For Developers & Stakeholders**  
**Last Updated:** January 7, 2026

---

## 🚀 Quick Start

### Access Treasury Module
```
URL: http://localhost:3000/treasury
Login with your admin credentials
Navigate: Sidebar → Treasury → Bank Accounts
```

### Current Features Available
✅ **Bank Account Management** - Fully operational  
⏳ Cash Position - Coming soon  
⏳ Bank Reconciliation - Coming soon  
⏳ Fund Transfers - Coming soon  

---

## 📊 Current Status at a Glance

```
┌────────────────────────────────────────┐
│  TREASURY MODULE STATUS                │
│                                        │
│  Overall Progress:      40%  ████░░░░░ │
│  Bank Accounts:        100%  ██████████ │
│  Cash Position:          0%  ░░░░░░░░░░ │
│  Reconciliation:         0%  ░░░░░░░░░░ │
│  Fund Transfers:         0%  ░░░░░░░░░░ │
│                                        │
│  Backend APIs:      12/112    11%      │
│  Frontend Pages:     6/10     60%      │
│  Database Tables:   10/10    100%      │
│                                        │
│  Status: ✅ Week 1 Complete            │
└────────────────────────────────────────┘
```

---

## 🗂️ File Locations

### Backend Files
```
backend/
├── shared/database/treasury_models.py         # 10 database models
├── alembic/versions/008_add_treasury_module.py  # Migration
└── services/treasury/
    ├── bank_account_schemas.py   # Pydantic models
    ├── bank_account_service.py   # Business logic
    └── bank_account_router.py    # API endpoints
```

### Frontend Files
```
frontend/apps/admin-portal/src/
├── services/treasury.service.ts              # API client
├── app/treasury/
│   ├── dashboard/page.tsx                    # Main dashboard
│   └── bank-accounts/
│       ├── page.tsx                          # List view
│       ├── create/page.tsx                   # Create form
│       └── [id]/
│           ├── page.tsx                      # Detail view
│           └── edit/page.tsx                 # Edit form
└── components/layout/sidebar.tsx             # Navigation (modified)
```

### Documentation Files
```
docs/
├── TREASURY_CASH_MANAGEMENT_GAP_ANALYSIS.md  # Complete analysis (25 pages)
├── TREASURY_IMPLEMENTATION_QUICKSTART.md     # Developer guide (30 pages)
└── MASTER_INDEX.md                           # Updated with Treasury

Root:
├── TREASURY_MODULE_STATUS.md                 # Executive summary
├── TREASURY_IMPLEMENTATION_PROGRESS.md       # Detailed progress
├── TREASURY_FRONTEND_COMPLETE.md             # Frontend docs
├── TREASURY_IMPLEMENTATION_SUMMARY_FINAL.md  # Final summary
└── TREASURY_QUICK_REFERENCE.md               # This file
```

---

## 🔌 API Endpoints (All Working)

### Base URL
```
http://localhost:8000/api/v1/treasury/bank-accounts
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create new bank account |
| GET | `/{id}` | Get account by ID |
| GET | `/` | List all accounts (with filters) |
| PATCH | `/{id}` | Update account |
| DELETE | `/{id}` | Delete account |
| GET | `/active/list` | Get active accounts |
| GET | `/{id}/balance` | Get account balance |
| POST | `/{id}/update-balance` | Update balance |
| GET | `/branch/{id}/accounts` | Get accounts by branch |
| GET | `/statistics/summary` | Get statistics |
| POST | `/bulk/create` | Bulk create accounts |
| GET | `/{id}/history` | Get balance history |

### API Documentation
```
Swagger UI: http://localhost:8000/docs
ReDoc:      http://localhost:8000/redoc
```

---

## 💻 Common Code Patterns

### Backend: Create New Service

```python
# 1. Create schemas (bank_account_schemas.py pattern)
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    description: str

class ItemResponse(ItemCreate):
    id: int
    created_at: datetime

# 2. Create service (bank_account_service.py pattern)
class ItemService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_item(self, data: ItemCreate) -> Item:
        item = Item(**data.dict())
        self.db.add(item)
        self.db.commit()
        return item

# 3. Create router (bank_account_router.py pattern)
router = APIRouter()

@router.post("/", response_model=ItemResponse)
async def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db)
):
    service = ItemService(db)
    return await service.create_item(data)
```

### Frontend: Create New Page

```typescript
// 1. Add API method to service (treasury.service.ts pattern)
export const treasuryService = {
  async getItems() {
    const response = await apiClient.get<Item[]>('/treasury/items');
    return response.data;
  }
};

// 2. Create page component
'use client';

import { useState, useEffect } from 'react';
import { treasuryService } from '@/services/treasury.service';

export default function ItemsPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      const data = await treasuryService.getItems();
      setItems(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Items</h1>
      {/* Add your UI here */}
    </div>
  );
}
```

---

## 🎨 UI Component Patterns

### Statistics Card
```tsx
<div className="bg-white border border-gray-200 rounded-lg p-4">
  <div className="text-sm text-gray-600 mb-1">Label</div>
  <div className="text-2xl font-bold text-gray-900">Value</div>
</div>
```

### Status Badge
```tsx
<span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
  status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
}`}>
  {status}
</span>
```

### Form Input
```tsx
<div>
  <label className="block text-sm font-medium text-gray-700 mb-1">
    Field Name <span className="text-red-500">*</span>
  </label>
  <input
    type="text"
    name="fieldName"
    value={formData.fieldName}
    onChange={handleChange}
    required
    className="w-full px-3 py-2 border border-gray-300 rounded-lg 
               focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  />
</div>
```

### Action Button
```tsx
<button
  onClick={handleClick}
  disabled={loading}
  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 
             rounded-lg hover:bg-blue-700 disabled:opacity-50"
>
  {loading ? 'Loading...' : 'Submit'}
</button>
```

---

## 🧪 Testing Commands

### Backend Testing
```bash
# Start backend server
cd backend
python main.py

# Run tests (when available)
pytest tests/treasury/

# Check API docs
open http://localhost:8000/docs
```

### Frontend Testing
```bash
# Start frontend dev server
cd frontend/apps/admin-portal
npm run dev

# Run tests (when available)
npm test

# Build for production
npm run build

# Start production server
npm start
```

### Database Operations
```bash
# Apply migrations
cd backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback migration
alembic downgrade -1
```

---

## 🔍 Troubleshooting

### Backend Issues

**Problem:** Database connection error
```bash
# Check PostgreSQL is running
# Verify DATABASE_URL in .env
# Test connection:
psql $DATABASE_URL
```

**Problem:** Migration fails
```bash
# Check current version
alembic current

# View migration history
alembic history

# Rollback and retry
alembic downgrade -1
alembic upgrade head
```

**Problem:** API returns 401 Unauthorized
```bash
# Check auth token in request headers
# Verify tenant_id is set
# Check token expiry
```

### Frontend Issues

**Problem:** Page shows blank/white screen
```bash
# Check browser console for errors
# Verify API_URL in .env.local
# Check backend is running
# Clear cache and refresh
```

**Problem:** API calls fail with CORS error
```bash
# Verify backend allows frontend origin
# Check CORS middleware configuration
# Verify API URL is correct
```

**Problem:** Data not loading
```bash
# Open browser DevTools → Network tab
# Check API response status
# Verify response format matches TypeScript interface
# Check for JavaScript errors in console
```

---

## 📋 Common Tasks

### Add New Field to Bank Account

1. **Update Database Model** (`treasury_models.py`)
```python
new_field = Column(String(255), nullable=True)
```

2. **Create Migration**
```bash
alembic revision --autogenerate -m "add new_field to bank_account"
alembic upgrade head
```

3. **Update Pydantic Schemas** (`bank_account_schemas.py`)
```python
class TreasuryBankAccountBase(BaseModel):
    # ... existing fields
    new_field: Optional[str] = None
```

4. **Update TypeScript Interface** (`treasury.service.ts`)
```typescript
export interface BankAccount {
  // ... existing fields
  new_field?: string;
}
```

5. **Add to Forms** (`create/page.tsx`, `edit/page.tsx`)
```tsx
<input
  type="text"
  name="new_field"
  value={formData.new_field}
  onChange={handleChange}
/>
```

### Add New API Endpoint

1. **Add Service Method** (`bank_account_service.py`)
```python
async def new_method(self, param: str) -> Result:
    # Implementation
    return result
```

2. **Add Router Endpoint** (`bank_account_router.py`)
```python
@router.get("/new-endpoint")
async def new_endpoint(param: str, db: Session = Depends(get_db)):
    service = BankAccountService(db)
    return await service.new_method(param)
```

3. **Add Frontend Method** (`treasury.service.ts`)
```typescript
async newMethod(param: string) {
  const response = await apiClient.get(`/treasury/bank-accounts/new-endpoint?param=${param}`);
  return response.data;
}
```

### Add New Page

1. **Create Page File**
```bash
# Create directory and file
mkdir -p frontend/apps/admin-portal/src/app/treasury/new-feature
touch frontend/apps/admin-portal/src/app/treasury/new-feature/page.tsx
```

2. **Add Page Component**
```tsx
'use client';
export default function NewFeaturePage() {
  return <div>New Feature</div>;
}
```

3. **Add to Navigation** (`sidebar.tsx`)
```tsx
{ title: 'New Feature', href: '/treasury/new-feature' }
```

---

## 📞 Quick Support

### For Issues
1. Check browser console for errors
2. Check backend logs
3. Verify API is returning correct data (use Swagger UI)
4. Check database for data integrity
5. Review documentation for similar examples

### For Questions
- **Backend**: Check `bank_account_service.py` for patterns
- **Frontend**: Check `bank-accounts/page.tsx` for patterns
- **Database**: Check `treasury_models.py` for schema
- **API**: Check Swagger UI at `/docs`

### Resources
- **Full Gap Analysis**: `docs/TREASURY_CASH_MANAGEMENT_GAP_ANALYSIS.md`
- **Developer Guide**: `docs/TREASURY_IMPLEMENTATION_QUICKSTART.md`
- **Frontend Docs**: `TREASURY_FRONTEND_COMPLETE.md`
- **Progress Tracker**: `TREASURY_IMPLEMENTATION_PROGRESS.md`

---

## 🎯 Next Development Tasks

### Immediate (Week 2)
1. **Cash Position Service** - Backend + Frontend
2. **Cash Position Dashboard** - Real-time tracking

### Short Term (Week 2-3)
3. **Bank Reconciliation** - Automated matching
4. **Reconciliation UI** - Statement upload & matching

### Medium Term (Week 3-4)
5. **Fund Transfers** - NEFT/RTGS/IMPS integration
6. **Transfer UI** - Request and approval workflow

### Long Term (Month 2+)
7. **Liquidity Management** - Position tracking
8. **Investment Tracking** - Portfolio management
9. **Cash Flow Forecasting** - Predictive analytics
10. **Advanced Reporting** - Custom reports

---

## 💡 Best Practices

### Code Quality
- ✅ Use TypeScript for type safety
- ✅ Follow existing patterns and conventions
- ✅ Write descriptive variable and function names
- ✅ Add comments for complex logic
- ✅ Handle errors gracefully
- ✅ Use async/await for API calls

### Git Workflow
- ✅ Create feature branches
- ✅ Write meaningful commit messages
- ✅ Pull latest before starting work
- ✅ Test before committing
- ✅ Review your own code before PR

### Testing
- ✅ Test happy path
- ✅ Test error scenarios
- ✅ Test edge cases
- ✅ Test on different screen sizes
- ✅ Test in different browsers

---

## 📈 Performance Tips

### Backend
- Use pagination for large datasets
- Add database indexes for frequently queried columns
- Use SELECT to fetch only needed columns
- Cache frequently accessed data (Redis)
- Use connection pooling

### Frontend
- Lazy load components
- Debounce search inputs
- Use React.memo for expensive renders
- Optimize images
- Code splitting with Next.js dynamic imports

---

## 🔐 Security Checklist

- ✅ Validate all user inputs (backend + frontend)
- ✅ Use parameterized queries (SQLAlchemy ORM)
- ✅ Implement CSRF protection
- ✅ Use HTTPS in production
- ✅ Store secrets in environment variables
- ✅ Implement rate limiting
- ✅ Sanitize HTML output
- ✅ Use secure headers
- ✅ Implement proper authentication
- ✅ Log security events

---

## 📌 Quick Commands Cheat Sheet

```bash
# Backend
cd backend && python main.py              # Start server
alembic upgrade head                      # Run migrations
alembic revision --autogenerate -m "msg" # Create migration

# Frontend
cd frontend/apps/admin-portal && npm run dev  # Start dev server
npm run build                                  # Production build
npm run lint                                   # Lint code

# Database
psql $DATABASE_URL                        # Connect to DB
alembic current                           # Check migration status
alembic history                           # View migration history

# Git
git checkout -b feature/treasury-cash     # Create feature branch
git add .                                 # Stage changes
git commit -m "Add cash position"         # Commit
git push origin feature/treasury-cash     # Push to remote
```

---

**Quick Reference Version:** 1.0  
**Last Updated:** January 7, 2026  
**Status:** Current for Treasury v1 (Bank Accounts Complete)

---

**Need more details?** Check the full documentation suite listed above! 📚
