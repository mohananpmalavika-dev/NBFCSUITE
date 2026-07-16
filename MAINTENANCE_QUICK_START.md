# Locker Maintenance - Quick Start Guide

**For**: Developers joining the project  
**Purpose**: Get up to speed quickly on the Maintenance module  
**Time to read**: 10 minutes  

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Navigate to maintenance page
cd frontend/apps/admin-portal/src/app/lockers/maintenance

# 2. Key files
page.tsx              # Main UI (2,500 lines)
../../services/locker.service.ts  # API client

# 3. Backend files
backend/services/locker/maintenance_service.py  # Business logic
backend/services/locker/router.py              # API endpoints
```

---

## 📂 File Structure

```
NBFCSUITE/
├── backend/services/locker/
│   ├── maintenance_service.py    # Core business logic (800 lines)
│   └── router.py                 # 20 API endpoints
│
├── frontend/apps/admin-portal/src/
│   ├── app/lockers/maintenance/
│   │   └── page.tsx              # Complete UI (2,500 lines)
│   │
│   └── services/
│       └── locker.service.ts     # TypeScript client (20 methods)
│
└── docs/
    ├── LOCKER_MAINTENANCE_COMPLETE.md           # Full specs
    ├── LOCKER_MAINTENANCE_UI_COMPLETE.md        # UI details
    ├── MAINTENANCE_FORMS_GUIDE.md               # Form guide
    ├── MAINTENANCE_MODULE_FINAL_STATUS.md       # Final status
    └── MAINTENANCE_QUICK_START.md               # This file
```

---

## 🎯 What This Module Does

### Two Types of Maintenance:

**1. Preventive (Scheduled)**:
- Lock servicing every 6 months
- Key duplication when needed
- Locker cleaning quarterly
- Vault maintenance (humidity control)
- Fire protection checks annually

**2. Breakdown (Emergency)**:
- Lock jamming (can't open)
- Key lost by customer
- Lock replacement needed
- Master key regeneration
- Locker repair (damage)

### Key Features:
- ✅ Auto-recurring maintenance (schedule once, repeats automatically)
- ✅ Cost tracking (bank cost vs customer charges)
- ✅ Quality checks before completion
- ✅ Customer satisfaction ratings
- ✅ Priority management (5 levels)
- ✅ Multi-tenant support

---

## 🏗️ Architecture (Simple View)

```
User clicks "Schedule Maintenance"
         ↓
React Form (page.tsx)
         ↓
API Call (locker.service.ts)
         ↓
FastAPI Endpoint (router.py)
         ↓
Business Logic (maintenance_service.py)
         ↓
Database (PostgreSQL)
         ↓
Response back to UI
         ↓
Success message shown
```

---

## 📋 Main Components (UI)

### 1. MaintenanceManagementPage
**Location**: Main export from `page.tsx`  
**Purpose**: Container for entire page  
**Key Parts**:
- Header with "Schedule" and "Report" buttons
- Statistics cards (4 KPIs)
- Tab navigation (7 tabs)
- Three dialogs (Schedule, Report, Details)

### 2. Schedule Maintenance Dialog
**Trigger**: "Schedule Maintenance" button  
**Fields**:
- Locker selection
- Maintenance type (5 options)
- Date & time
- Recurring checkbox + frequency
- Technician assignment
- Description

### 3. Report Breakdown Dialog
**Trigger**: "Report Breakdown" button  
**Fields**:
- Locker selection
- Issue type (6 breakdown types)
- Priority (5 levels - shows warning for URGENT/EMERGENCY)
- Description (10-1000 chars)
- Customer reported checkbox
- Customer ID (if reported by customer)
- Technician assignment

### 4. Maintenance Details Dialog (4 Tabs)
**Trigger**: Click "View" on any maintenance record  

**Tab 1: Details** (read-only)
- All maintenance information
- Schedule, cost, quality data

**Tab 2: Action** (10 forms based on type)
- Lock Servicing
- Key Duplication
- Cleaning
- Vault Maintenance
- Fire Protection Check
- Resolve Lock Jamming
- Handle Lost Key
- Replace Lock
- Regenerate Master Key
- Repair Locker

**Tab 3: Cost** (editable)
- Labor cost
- Material cost
- External service cost
- Customer charges with GST

**Tab 4: Completion** (final step)
- Quality check
- Customer satisfaction rating
- Completion confirmation

---

## 🔧 Common Tasks

### Add a New Maintenance Type

**Step 1**: Update Backend Enum
```python
# backend/services/locker/maintenance_service.py
class MaintenanceType(str, Enum):
    # ... existing types
    NEW_TYPE = "new_type"
```

**Step 2**: Update TypeScript Enum
```typescript
// frontend/.../locker.service.ts
export enum MaintenanceType {
  // ... existing types
  NEW_TYPE = 'new_type'
}
```

**Step 3**: Add Service Method
```python
# backend/services/locker/maintenance_service.py
async def perform_new_type(self, maintenance_id: str, data: dict):
    # Implementation
    pass
```

**Step 4**: Add API Endpoint
```python
# backend/services/locker/router.py
@router.post("/{maintenance_id}/new-type")
async def perform_new_type_endpoint(
    maintenance_id: str,
    data: dict,
    service: LockerMaintenanceService = Depends()
):
    return await service.perform_new_type(maintenance_id, data)
```

**Step 5**: Add TypeScript Method
```typescript
// frontend/.../locker.service.ts
performNewType: async (maintenanceId: string, data: any) => {
  return apiClient.post(`/locker/maintenance/${maintenanceId}/new-type`, data)
}
```

**Step 6**: Add UI Form
```typescript
// frontend/.../maintenance/page.tsx
function NewTypeForm({ maintenance, onUpdate }) {
  // Form implementation
  return <form>...</form>
}

// Add to MaintenanceActionTab switch
case MaintenanceType.NEW_TYPE:
  return <NewTypeForm maintenance={maintenance} onUpdate={onUpdate} />
```

---

## 🧪 Testing Quick Guide

### Test Schedule Flow:
```typescript
1. Open page: http://localhost:3000/lockers/maintenance
2. Click "Schedule Maintenance"
3. Fill form:
   - Locker: Select any
   - Type: Lock Servicing
   - Date: Tomorrow
   - Recurring: Yes, Quarterly
   - Technician: Test User
4. Submit
5. Verify appears in "Scheduled" tab
```

### Test Breakdown Flow:
```typescript
1. Click "Report Breakdown"
2. Fill form:
   - Locker: Select any
   - Issue: Lock Jamming
   - Priority: EMERGENCY (confirm warning)
   - Description: "Lock completely jammed, customer locked out"
   - Technician: Test User
3. Submit
4. Verify appears in "Breakdowns" tab with red/orange styling
```

### Test Complete Flow:
```typescript
1. Click "View" on in-progress maintenance
2. Go to Action tab
3. Fill appropriate form for the type
4. Submit action
5. Go to Cost tab
6. Click "Edit Costs"
7. Enter costs (labor: 500, material: 200)
8. Save
9. Go to Completion tab
10. Enable quality check
11. Fill quality details
12. Rate customer 5 stars
13. Click "Complete Maintenance"
14. Verify status changed to "Completed"
```

---

## 🔍 Debugging Tips

### Issue: Form not submitting
```typescript
// Check browser console for errors
// Verify all required fields filled
// Check network tab for API call
// Look for validation error toasts
```

### Issue: API returns error
```typescript
// Check backend logs
// Verify tenant_id in request
// Check database connection
// Verify data types match
```

### Issue: Cost calculation wrong
```typescript
// Check MaintenanceCostTab component
// Formulas:
//   totalMaintenanceCost = labor + material + external
//   customerGST = customerChargeAmount * 0.18
//   customerTotalCharge = customerChargeAmount + customerGST
//   netCostToBank = totalMaintenanceCost - customerTotalCharge
```

### Issue: Recurring not creating next record
```typescript
// Check backend _schedule_next_recurring() method
// Verify is_recurring = true
// Verify recurring_frequency set
// Check completed_date exists
// Look for errors in backend logs
```

---

## 📊 Key Data Flows

### Auto-Recurring Logic:
```
1. User schedules maintenance with recurring=true, frequency=quarterly
2. Maintenance performed and completed
3. Backend calculates: next_date = completed_date + 90 days
4. Backend creates new maintenance record:
   - scheduled_date = next_date
   - status = scheduled
   - parent_maintenance_id = original_id
   - Same locker, type, technician
5. New record appears in "Scheduled" tab automatically
```

### Customer Charge Calculation:
```
1. User enables "customer charged" in Cost tab
2. Enters reason: "Customer damage"
3. Enters amount: 5000
4. System calculates:
   - GST = 5000 × 0.18 = 900
   - Total = 5000 + 900 = 5900
5. Net cost to bank = Total Maintenance - 5900
```

### Quality Check Flow:
```
1. Maintenance action completed
2. User goes to Completion tab
3. Checks "Quality Check Performed"
4. Fills:
   - Checked by: Supervisor Name
   - Passed: Yes/No
   - Remarks: Details
5. If failed, warning shows but can still complete
6. Quality data stored for analytics
```

---

## 🎨 UI Component Patterns

### Standard Form Pattern:
```typescript
function MyForm({ maintenance, onUpdate }) {
  const [formData, setFormData] = useState({ /* initial */ })
  
  const mutation = useMutation({
    mutationFn: (data) => maintenanceService.performAction(maintenance.id, data),
    onSuccess: () => {
      toast({ title: 'Success' })
      onUpdate()
    },
    onError: (error) => {
      toast({ title: 'Error', description: error.message, variant: 'destructive' })
    }
  })
  
  const handleSubmit = (e) => {
    e.preventDefault()
    // Validation
    mutation.mutate(formData)
  }
  
  return <form onSubmit={handleSubmit}>...</form>
}
```

### Conditional Field Pattern:
```typescript
<Checkbox onChange={(e) => setEnabled(e.target.checked)} />

{enabled && (
  <Input /* conditional field */ />
)}
```

### Auto-Calculation Pattern:
```typescript
const total = formData.labor + formData.material + formData.external
const gst = formData.customerCharge * 0.18
const customerTotal = formData.customerCharge + gst
```

---

## 🔐 Security Checklist

✅ All API calls require authentication (JWT)  
✅ Multi-tenant filtering (tenant_id)  
✅ Input validation client and server  
✅ SQL injection prevented (ORM)  
✅ XSS prevented (React escaping)  
✅ CSRF tokens (FastAPI)  
✅ File uploads validated  
✅ Sensitive operations logged  

---

## 📈 Performance Tips

✅ React Query caches API responses  
✅ Invalidate queries after mutations  
✅ Use optimistic updates for instant feedback  
✅ Lazy load details dialog  
✅ Paginate large lists  
✅ Debounce search inputs  
✅ Virtual scroll for 1000+ records  

---

## 🚨 Common Pitfalls

### ❌ Don't:
```typescript
// Don't use 'any' types
const data: any = { ... }

// Don't skip validation
mutation.mutate(formData) // Without checking required fields

// Don't forget error handling
const result = await api.call() // No try-catch

// Don't invalidate wrong queries
queryClient.invalidateQueries({ queryKey: ['wrong-key'] })
```

### ✅ Do:
```typescript
// Use proper types
const data: MaintenanceData = { ... }

// Validate before submit
if (!formData.required) return
mutation.mutate(formData)

// Handle errors
try {
  const result = await api.call()
} catch (error) {
  toast({ title: 'Error', variant: 'destructive' })
}

// Invalidate correct queries
queryClient.invalidateQueries({ queryKey: ['maintenance'] })
```

---

## 📚 Documentation Links

1. **LOCKER_MAINTENANCE_COMPLETE.md** - Read this for full technical details
2. **MAINTENANCE_FORMS_GUIDE.md** - Reference when building forms
3. **LOCKER_MAINTENANCE_UI_COMPLETE.md** - UI implementation details
4. **MAINTENANCE_MODULE_FINAL_STATUS.md** - Overall status and metrics

---

## 🎯 Quick Commands

### Development:
```bash
# Start frontend dev server
cd frontend/apps/admin-portal
npm run dev

# Start backend server
cd backend
uvicorn main:app --reload

# Run tests
npm run test
pytest

# Build for production
npm run build
```

### Git:
```bash
# Current branch should have all changes
git status

# Files modified:
# - frontend/apps/admin-portal/src/app/lockers/maintenance/page.tsx
# - frontend/apps/admin-portal/src/services/locker.service.ts
# - backend/services/locker/maintenance_service.py
# - backend/services/locker/router.py
```

---

## 💡 Pro Tips

1. **Use existing patterns**: Copy from Breaking or Surrender modules
2. **Check types first**: Look at enums and interfaces in locker.service.ts
3. **Read backend code**: Business logic is well-documented
4. **Test incrementally**: Test each form as you build
5. **Use React DevTools**: Inspect component state
6. **Check Network tab**: Verify API calls
7. **Use TypeScript**: Let the compiler catch errors
8. **Follow conventions**: Match existing code style

---

## 🆘 Need Help?

### Questions About:
- **Backend Logic**: Read `maintenance_service.py` docstrings
- **API Endpoints**: Check `router.py` endpoint definitions
- **TypeScript Types**: Review `locker.service.ts` interfaces
- **UI Components**: Look at `page.tsx` implementations
- **Forms**: Reference `MAINTENANCE_FORMS_GUIDE.md`
- **Overall Flow**: See `MAINTENANCE_MODULE_FINAL_STATUS.md`

### Still Stuck?
1. Check browser console for errors
2. Check backend logs for exceptions
3. Review similar working features (Breaking/Surrender)
4. Read the comprehensive documentation
5. Ask team members with context of what you tried

---

## ✅ Checklist for New Developers

Before starting work:
- [ ] Read this Quick Start (10 min)
- [ ] Skim LOCKER_MAINTENANCE_COMPLETE.md (20 min)
- [ ] Clone repo and setup environment
- [ ] Run the application locally
- [ ] Test scheduling a maintenance
- [ ] Test reporting a breakdown
- [ ] Test completing a maintenance
- [ ] Review the code structure
- [ ] Identify the component you'll work on
- [ ] Read relevant documentation section

Now you're ready to contribute! 🚀

---

**Document Version**: 1.0  
**Last Updated**: Current Session  
**Estimated Read Time**: 10 minutes  
**Target Audience**: New developers joining the project

---

*This guide gets you started quickly. For deep dives, refer to the comprehensive documentation files listed above.*
