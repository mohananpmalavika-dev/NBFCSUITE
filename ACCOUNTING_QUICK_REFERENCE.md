# Accounting Module - Quick Reference Card

**Version:** 1.0 | **Date:** 2026-07-07

---

## 🔗 Quick Links

| Resource | URL/Path |
|----------|----------|
| **Backend API Docs** | http://localhost:8000/docs |
| **TDS Dashboard** | http://localhost:3000/accounting/tds |
| **GST Dashboard** | http://localhost:3000/accounting/gst |
| **Full Documentation** | `ACCOUNTING_MODULE_COMPLETE.md` |

---

## 📁 File Locations

### Backend Files
```
backend/
├── services/accounting/
│   ├── tds_service.py          # TDS business logic
│   ├── tds_router.py           # TDS API endpoints
│   ├── gst_service.py          # GST business logic
│   ├── gst_router.py           # GST API endpoints
│   └── asset_service.py        # Asset management
├── shared/database/
│   └── accounting_extended_models.py  # Database models
└── alembic/versions/
    └── 009_add_accounting_extended_features.py  # Migration
```

### Frontend Files
```
frontend/apps/admin-portal/src/
├── services/
│   └── accounting.service.ts   # API client
├── app/accounting/
│   ├── tds/                    # TDS module (8 pages)
│   └── gst/                    # GST module (8 pages)
└── components/layout/
    └── sidebar.tsx             # Navigation menu
```

---

## 🚀 Quick Commands

### Backend
```bash
# Run migration
cd backend && alembic upgrade head

# Start server
python -m uvicorn main:app --reload --port 8000

# Check migration status
alembic current

# Rollback migration
alembic downgrade -1
```

### Frontend
```bash
# Install dependencies
cd frontend/apps/admin-portal && npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Clear cache
rm -rf .next && npm run dev
```

---

## 📊 API Endpoints

### TDS Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/accounting/tds/sections` | List sections |
| POST | `/api/v1/accounting/tds/sections` | Create section |
| GET | `/api/v1/accounting/tds/deductions` | List deductions |
| POST | `/api/v1/accounting/tds/deductions` | Create deduction |
| POST | `/api/v1/accounting/tds/deductions/calculate` | Calculate TDS |
| GET | `/api/v1/accounting/tds/challans` | List challans |
| POST | `/api/v1/accounting/tds/challans` | Create challan |
| GET | `/api/v1/accounting/tds/certificates` | List certificates |
| POST | `/api/v1/accounting/tds/certificates/{id}/generate` | Generate Form 16A |
| POST | `/api/v1/accounting/tds/returns/prepare` | Prepare Form 26Q |

### GST Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/accounting/gst/configuration` | Get GSTIN config |
| POST | `/api/v1/accounting/gst/configuration` | Setup GSTIN |
| GET | `/api/v1/accounting/gst/hsn-sac` | List codes |
| POST | `/api/v1/accounting/gst/hsn-sac` | Create code |
| GET | `/api/v1/accounting/gst/transactions` | List invoices |
| POST | `/api/v1/accounting/gst/transactions` | Create invoice |
| POST | `/api/v1/accounting/gst/transactions/calculate` | Calculate GST |
| GET | `/api/v1/accounting/gst/itc` | Get ITC |
| POST | `/api/v1/accounting/gst/returns/gstr1` | Prepare GSTR-1 |
| POST | `/api/v1/accounting/gst/returns/gstr3b` | Prepare GSTR-3B |

---

## 🗄️ Database Tables

### TDS Tables
- `tds_section_master` - Section codes and rates
- `tds_deductions` - Deduction records
- `tds_challans` - Payment challans
- `tds_certificates` - Form 16A certificates
- `tds_returns` - Form 26Q returns

### GST Tables
- `gst_configuration` - GSTIN setup
- `hsn_sac_master` - Product/service codes
- `gst_transactions` - Invoice records
- `gst_input_credit` - ITC tracking
- `gst_returns` - GSTR-1/3B returns

### Asset Tables
- `fixed_assets` - Asset master
- `asset_depreciation_schedule` - Depreciation
- `asset_transfers` - Transfer history
- `asset_maintenance` - Maintenance logs

---

## 💡 Common Tasks

### Add New TDS Section
```typescript
// Frontend
await tdsService.createSection({
  section_code: "194C",
  section_name: "Contractor",
  rate_percentage: 2.0,
  threshold_amount: 30000,
  is_active: true
});
```

### Calculate TDS
```typescript
const result = await tdsService.calculateTDS({
  section_code: "194A",
  taxable_amount: 100000,
  deductee_type: "individual",
  has_pan: true
});
// Returns: { tds_amount: 10000, rate: 10, total_amount: 10000 }
```

### Create GST Transaction
```typescript
await gstService.createTransaction({
  transaction_type: "sale",
  supply_type: "B2B",
  invoice_number: "INV/2024/001",
  party_gstin: "27XXXXX1234X1X5",
  taxable_amount: 100000,
  cgst_amount: 9000,
  sgst_amount: 9000,
  total_amount: 118000
});
```

---

## 🔍 Debugging Tips

### Backend Issues
```python
# Check logs
tail -f backend/logs/app.log

# Test endpoint directly
curl http://localhost:8000/api/v1/accounting/tds/sections

# Check database
psql -d nbfc_db -c "SELECT * FROM tds_section_master;"
```

### Frontend Issues
```javascript
// Check console
console.log('API Response:', data);

// Check network tab
// Filter by: accounting

// Test API service
import { tdsService } from '@/services/accounting.service';
const sections = await tdsService.getSections();
console.log(sections);
```

---

## ⚡ Performance Tips

### Backend
- Use pagination for large lists
- Add indexes on frequently queried columns
- Cache configuration data
- Use async/await properly

### Frontend
- Lazy load components
- Use React.memo for expensive components
- Debounce search inputs
- Cache API responses

---

## 🔐 Security Notes

### PAN/GSTIN Validation
```typescript
// PAN: 10 characters (ABCDE1234F)
const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;

// GSTIN: 15 characters (27AABCT1234C1Z5)
const gstinRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
```

### Data Access
- All endpoints require authentication
- Tenant isolation enforced
- Audit trail for compliance changes

---

## 📅 Compliance Deadlines

### TDS
- **Challan Payment:** 7th of next month
- **Certificate Issue:** 15 days after return filing
- **Return Filing (Form 26Q):**
  - Q1: 31 July
  - Q2: 31 October
  - Q3: 31 January
  - Q4: 31 May

### GST
- **GSTR-1:** 11th of next month
- **GSTR-3B:** 20th of next month
- **Tax Payment:** Before filing GSTR-3B
- **Late Fee:** ₹50/day per Act (max ₹5,000)

---

## 🎯 Key Features

### TDS Module
✅ Section-wise rate management  
✅ Automatic TDS calculation  
✅ Challan tracking with BSR code  
✅ Form 16A certificate generation  
✅ Form 26Q return preparation  
✅ PAN/TAN validation  

### GST Module
✅ GSTIN configuration  
✅ HSN/SAC code master  
✅ B2B/B2C/Export classification  
✅ CGST/SGST/IGST calculation  
✅ ITC eligibility tracking  
✅ GSTR-1 & GSTR-3B preparation  

---

## 🆘 Quick Fixes

### Migration Failed
```bash
alembic downgrade 008
alembic upgrade head
```

### Frontend 404
```bash
rm -rf .next
npm run dev
```

### API Not Found
- Check router registration in main.py
- Restart backend server
- Clear browser cache

### Calculation Wrong
- Verify master data (sections/rates)
- Check input values
- Review calculation logic

---

## 📞 Support

### Documentation
- `ACCOUNTING_MODULE_COMPLETE.md` - Full implementation
- `ACCOUNTING_DEPLOYMENT_FINAL.md` - Deployment steps
- `ACCOUNTING_FEATURES_SUMMARY.md` - Feature overview

### Logs
- Backend: `backend/logs/app.log`
- Frontend: Browser console (F12)
- Database: PostgreSQL logs

---

## ✅ Health Check

```bash
# Backend
curl http://localhost:8000/health

# Database
psql -d nbfc_db -c "SELECT COUNT(*) FROM tds_section_master;"

# Frontend
curl http://localhost:3000/accounting/tds
```

---

**Quick Reference Version:** 1.0  
**Last Updated:** 2026-07-07

**Print this card for quick access!**
