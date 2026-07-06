# Gold Loan Management - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Node.js 18+ installed
- Python 3.11+ installed
- PostgreSQL database (local or cloud)
- Git for version control

---

## Backend Setup

### 1. Configure Database
```bash
# Option 1: Local PostgreSQL
# Install PostgreSQL and create a database

# Option 2: Free Cloud Database (Recommended)
# Sign up at: render.com, railway.app, or supabase.com
# Get your PostgreSQL connection string
```

### 2. Environment Configuration
```bash
cd backend

# Copy example env file
copy .env.example .env

# Edit .env and add your database URL
# DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 3. Install Dependencies
```bash
# Windows
pip install -r requirements.windows.txt

# Linux/Mac
pip install -r requirements.txt
```

### 4. Run Database Migration
```bash
# Apply all migrations including gold loan features
alembic upgrade head

# Verify migration
alembic current
```

### 5. Start Backend Server
```bash
python main.py

# Backend will start at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

---

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend/apps/admin-portal
npm install
```

### 2. Configure API Endpoint
Check that `lib/api-client.ts` points to your backend:
```typescript
// Should be: http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev

# Frontend will start at http://localhost:3000
```

---

## 🎯 Access the Gold Loan Features

### Main Dashboard
Navigate to: **http://localhost:3000/gold-loans**

You'll see 5 quick access cards:

### 1. Gold Rates (Yellow Card)
**URL**: `/gold-loans/gold-rates`

**What You Can Do**:
- View current gold rates (24K, 22K, 18K)
- Update live rates from IBJA/MCX/MetalAPI
- Enter manual rates
- View 30-day statistics
- Calculate gold value

**Try This**:
1. Click "Update Live Rates"
2. Use the gold value calculator
3. Enter manual rates if needed

### 2. Vault Management (Blue Card)
**URL**: `/gold-loans/vault-management`

**What You Can Do**:
- Create vault locations
- Check-in ornaments with barcode/RFID
- Check-out ornaments
- Track capacity
- View inventory

**Try This**:
1. Click "New Vault Location"
2. Fill in vault details (code, name, capacity)
3. Navigate to "Inventory" tab
4. Check in an ornament

### 3. Purity Testing (Green Card)
**URL**: `/gold-loans/purity-testing`

**What You Can Do**:
- Create individual purity tests
- Bulk test all ornaments in a loan
- Generate certificates
- Flag discrepancies
- View statistics

**Try This**:
1. Click "New Test"
2. Select test method (XRF recommended)
3. Enter claimed and tested purity
4. View variance calculation
5. Generate certificate

### 4. Appraisals (Purple Card)
**URL**: `/gold-loans/appraisals`

**What You Can Do**:
- Create appraisal reports
- Submit for verification
- Approve/reject appraisals
- Generate certificates
- Track appraisal history

**Try This**:
1. Click "New Appraisal"
2. Fill in ornament details
3. Enter weight and purity
4. Select condition
5. Submit for verification

### 5. Auctions (Red Card)
**URL**: `/gold-loans/auctions`

**What You Can Do**:
- Create auctions for defaulted loans
- Auto-generate legal notices
- Register bidders with EMD
- Accept bids
- Select winner and complete

**Try This**:
1. Click "Create Auction"
2. Link to a gold loan
3. Set auction date and venue
4. Start auction when ready
5. Accept bids and select winner

---

## 📊 Sample Data Flow

### Complete Gold Loan Workflow

#### Step 1: Check Current Gold Rates
```
1. Go to Gold Rates page
2. Update live rates
3. Note the 22K rate (most common)
```

#### Step 2: Create Vault Location (First Time)
```
1. Go to Vault Management
2. Create a vault location
   - Vault Code: VAULT-001
   - Vault Name: Main Branch Vault
   - Max Capacity: 1000 items, 100 kg
   - Security Level: High
```

#### Step 3: Process New Gold Loan
```
1. Create gold loan (existing feature)
2. Record ornament details
3. Check-in to vault
4. Perform purity test
5. Create appraisal
```

#### Step 4: Regular Operations
```
1. Monitor vault capacity
2. Run periodic purity tests
3. Update appraisals annually
4. Handle check-outs for payments
```

#### Step 5: Default Handling (If Needed)
```
1. Create auction for defaulted loan
2. System auto-generates legal notice
3. Register bidders with EMD
4. Conduct auction
5. Complete with winner selection
6. System calculates refund to customer
```

---

## 🔍 Testing the Features

### Gold Rates Test
```bash
# Test live rate update
POST http://localhost:8000/gold-loans/gold-rates/update-live?source=IBJA

# Expected: Current gold rates returned
```

### Vault Management Test
```bash
# Create vault
POST http://localhost:8000/gold-loans/vaults/locations
{
  "vault_code": "VAULT-TEST",
  "vault_name": "Test Vault",
  "vault_type": "Main",
  "location_type": "Branch",
  "max_capacity_items": 100,
  "max_capacity_weight_kg": 10.0,
  "security_level": "High"
}

# Check-in ornament
POST http://localhost:8000/gold-loans/vaults/inventory/check-in
{
  "vault_location_id": "vault-id",
  "gold_loan_id": "loan-id",
  "customer_id": "customer-id",
  "ornament_id": "ornament-id",
  "barcode": "BC-12345"
}
```

### Purity Test
```bash
# Create test
POST http://localhost:8000/gold-loans/purity-tests/
{
  "gold_loan_id": "loan-id",
  "ornament_id": "ornament-id",
  "test_method": "XRF",
  "claimed_purity_karat": 22,
  "claimed_purity_percentage": 91.67,
  "tested_purity_karat": 22,
  "tested_purity_percentage": 91.50,
  "tester_name": "John Doe"
}
```

### Appraisal Test
```bash
# Create appraisal
POST http://localhost:8000/gold-loans/appraisals/
{
  "customer_id": "customer-id",
  "ornament_type": "Necklace",
  "appraisal_type": "Initial",
  "verified_karat": 22,
  "purity_percentage": 91.67,
  "gross_weight_grams": 50.0,
  "net_weight_grams": 48.0,
  "condition": "Excellent",
  "appraiser_name": "Jane Smith"
}
```

### Auction Test
```bash
# Create auction
POST http://localhost:8000/gold-loans/auctions/
{
  "gold_loan_id": "loan-id",
  "auction_date": "2025-02-01T10:00:00Z",
  "auction_venue": "Main Branch",
  "notice_period_days": 30
}
```

---

## 🐛 Troubleshooting

### Backend Issues

#### Issue: Database Connection Error
```
Solution:
1. Check DATABASE_URL in .env
2. Verify PostgreSQL is running
3. Test connection: psql <DATABASE_URL>
4. Check firewall rules
```

#### Issue: Migration Fails
```
Solution:
1. Check current version: alembic current
2. Downgrade one step: alembic downgrade -1
3. Upgrade again: alembic upgrade head
4. If stuck, check migration file syntax
```

#### Issue: Module Not Found
```
Solution:
1. Activate virtual environment
2. Reinstall: pip install -r requirements.txt
3. Check Python version: python --version (should be 3.11+)
```

### Frontend Issues

#### Issue: API Connection Error
```
Solution:
1. Check backend is running: http://localhost:8000/docs
2. Check CORS settings in backend
3. Verify API_URL in frontend config
4. Check browser console for errors
```

#### Issue: Page Not Found (404)
```
Solution:
1. Check the URL path is correct
2. Restart frontend: npm run dev
3. Clear browser cache
4. Check Next.js routing files exist
```

#### Issue: TypeScript Errors
```
Solution:
1. Check all imports are correct
2. Run: npm install
3. Restart VS Code
4. Check tsconfig.json
```

---

## 📚 API Documentation

### Interactive API Docs
Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints Summary

#### Gold Rates (10 endpoints)
```
GET    /gold-loans/gold-rates/current
POST   /gold-loans/gold-rates/update-live
POST   /gold-loans/gold-rates/
GET    /gold-loans/gold-rates/
GET    /gold-loans/gold-rates/statistics/summary
GET    /gold-loans/gold-rates/calculate/value
```

#### Vault Management (20 endpoints)
```
POST   /gold-loans/vaults/locations
GET    /gold-loans/vaults/locations
GET    /gold-loans/vaults/locations/{id}
POST   /gold-loans/vaults/inventory/check-in
POST   /gold-loans/vaults/inventory/{id}/check-out
GET    /gold-loans/vaults/inventory
POST   /gold-loans/vaults/transfers
POST   /gold-loans/vaults/transfers/{id}/approve
GET    /gold-loans/vaults/locations/{id}/capacity
POST   /gold-loans/vaults/inventory/audit/{vault_id}
```

#### Purity Testing (12 endpoints)
```
POST   /gold-loans/purity-tests/
POST   /gold-loans/purity-tests/bulk-test/{loan_id}
GET    /gold-loans/purity-tests/
POST   /gold-loans/purity-tests/{id}/certificate
POST   /gold-loans/purity-tests/{id}/discrepancy
GET    /gold-loans/purity-tests/statistics/summary
```

#### Appraisals (12 endpoints)
```
POST   /gold-loans/appraisals/
POST   /gold-loans/appraisals/{id}/submit
POST   /gold-loans/appraisals/{id}/verify
POST   /gold-loans/appraisals/{id}/certificate
POST   /gold-loans/appraisals/{id}/reappraise
GET    /gold-loans/appraisals/
GET    /gold-loans/appraisals/ornament/{id}/history
GET    /gold-loans/appraisals/compare/{id1}/{id2}
```

#### Auctions (23 endpoints)
```
POST   /gold-loans/auctions/
GET    /gold-loans/auctions/
GET    /gold-loans/auctions/{id}
POST   /gold-loans/auctions/{id}/start
POST   /gold-loans/auctions/{id}/register-bidder
POST   /gold-loans/auctions/bids
POST   /gold-loans/auctions/{id}/complete
POST   /gold-loans/auctions/notices
POST   /gold-loans/auctions/notices/{id}/send
GET    /gold-loans/auctions/upcoming/scheduled
```

---

## 🎓 Training Resources

### For Operations Staff

#### Gold Rate Management
1. Update rates daily from trusted sources
2. Verify rates before creating loans
3. Use calculator for quick valuations
4. Monitor 30-day trends

#### Vault Operations
1. Always record check-ins with barcode
2. Verify ornament details before check-in
3. Monitor capacity warnings
4. Perform monthly audits

#### Purity Testing
1. Use XRF for most accurate results
2. Document equipment calibration
3. Always record tester license
4. Generate certificates for customers

#### Appraisals
1. Take clear photos of ornaments
2. Assess condition honestly
3. Submit for verification before finalizing
4. Generate certificates for records

#### Auction Management
1. Send notices 30 days before auction
2. Track delivery proof
3. Verify EMD before bidder registration
4. Document all bids with timestamps

### For Technical Staff

#### Backend Maintenance
- Monitor database performance
- Check API response times
- Review error logs daily
- Backup database regularly

#### Frontend Maintenance
- Monitor user sessions
- Check for console errors
- Update dependencies quarterly
- Test on multiple browsers

---

## 📞 Support & Help

### Documentation
- Backend API: http://localhost:8000/docs
- Frontend Components: See component source files
- Database Schema: Check migration files

### Common Questions

**Q: Can I use a different database?**
A: Yes, but PostgreSQL is recommended. Update DATABASE_URL in .env.

**Q: Can I change the port numbers?**
A: Yes, update PORT in backend and API_URL in frontend config.

**Q: How do I deploy to production?**
A: Use services like Render.com, Railway.app, or Vercel. See deployment guides.

**Q: Can I customize the UI?**
A: Yes, all frontend components can be modified. They use Tailwind CSS.

**Q: How do I add more test methods?**
A: Update the purity test dropdown options in the frontend and add backend validation.

---

## ✅ Launch Checklist

Before going live with the system:

### Backend
- [ ] Database properly configured
- [ ] All migrations applied
- [ ] Environment variables set
- [ ] API accessible via network
- [ ] SSL certificate configured (production)
- [ ] Error logging enabled
- [ ] Backup system in place

### Frontend
- [ ] Connected to backend
- [ ] Authentication working
- [ ] All pages loading
- [ ] Forms validated
- [ ] Error handling tested
- [ ] Responsive on mobile
- [ ] Browser compatibility checked

### Data
- [ ] Initial gold rates loaded
- [ ] Vault locations created
- [ ] Test users created
- [ ] Sample data for training
- [ ] Backup procedures documented

### Training
- [ ] Staff trained on gold rates
- [ ] Vault procedures documented
- [ ] Purity testing workflow clear
- [ ] Appraisal process understood
- [ ] Auction procedures reviewed

### Testing
- [ ] Create test gold loan
- [ ] Check-in to vault
- [ ] Run purity test
- [ ] Create appraisal
- [ ] Test auction workflow
- [ ] Verify all reports

---

## 🎉 You're Ready!

Your Gold Loan Management System is now fully functional with:

✅ **Live Gold Rates** - Always up-to-date pricing
✅ **Vault Management** - Secure ornament storage
✅ **Purity Testing** - Accurate gold verification
✅ **Appraisal Workflow** - Professional valuations
✅ **Auction System** - Complete auction lifecycle

**Start using the system and process your first gold loan!**

Navigate to: **http://localhost:3000/gold-loans**

---

**Need Help?**
- Check API docs: http://localhost:8000/docs
- Review code comments in source files
- Check migration files for database schema
- Review the GOLD_LOAN_FRONTEND_COMPLETE.md for details

**Happy Gold Loaning! 🏆**
