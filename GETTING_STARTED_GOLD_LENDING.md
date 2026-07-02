# Getting Started with Gold Lending Platform

## 🎉 Congratulations!

You now have a **production-ready enterprise Gold Lending Platform** with 3 complete phases:
- ✅ Product Configuration Engine
- ✅ Customer Journey Management
- ✅ Advanced Appraisal Engine

---

## 🚀 Next Steps to Get Running

### Step 1: Database Setup (5 minutes)

```bash
# Start PostgreSQL (if not running)
# Windows:
net start postgresql-x64-14

# Run all migrations in sequence
cd C:\NBFCSUITE

psql -U nbfc_user -d nbfcsuite -f infra\migrations\018_gold_product_configuration.sql
psql -U nbfc_user -d nbfcsuite -f infra\migrations\019_gold_customer_journey.sql
psql -U nbfc_user -d nbfcsuite -f infra\migrations\020_gold_appraisal_engine.sql
```

**Expected Output**: 25 new tables created

### Step 2: Backend Setup (3 minutes)

```bash
cd C:\NBFCSUITE\services\gold

# Install Python dependencies
pip install -r requirements.txt

# Seed initial gold loan products
python app\seed_products.py

# Start the service
uvicorn app.main:app --reload --port 8013
```

**Expected Output**: 
```
INFO:     Uvicorn running on http://127.0.0.1:8013
INFO:     Application startup complete
```

### Step 3: Frontend Setup (2 minutes)

```bash
# Open new terminal
cd C:\NBFCSUITE\apps\customer-app

# Install dependencies (if not done)
npm install

# Start development server
npm run dev
```

**Expected Output**:
```
Ready - started server on 0.0.0.0:3000
```

### Step 4: Verify Installation (2 minutes)

Open your browser and test:

1. **API Health Check**
   - http://localhost:8013/health
   - Should see: `{"status": "ok", "service": "gold"}`

2. **API Documentation**
   - http://localhost:8013/docs
   - Should see: Interactive Swagger UI

3. **Products Page**
   - http://localhost:3000/gold-lending/products
   - Should see: 4 seeded products (Jewel, Bullet, OD, Instant)

4. **Journey Page**
   - http://localhost:3000/gold-lending/journey/new
   - Should see: "Start Gold Loan Journey" screen

---

## 📋 Quick Test Workflow

### Test 1: View Products (1 minute)
```bash
# List all products
curl http://localhost:8013/api/v1/gold/products

# Or visit in browser:
# http://localhost:3000/gold-lending/products
```

### Test 2: Start Customer Journey (3 minutes)
1. Go to: http://localhost:3000/gold-lending/journey/new
2. Click "Walk-in at Branch"
3. Enter phone: 9876543210
4. Click "Search Customer"
5. View product recommendations
6. Select a product

### Test 3: Create Market Rate (1 minute)
```bash
curl -X POST http://localhost:8013/api/v1/gold/appraisal/market-rates \
  -H "Content-Type: application/json" \
  -d "{
    \"rate_date\": \"2026-07-03\",
    \"rate_source\": \"manual\",
    \"purity_karat\": 22.0,
    \"rate_per_gram\": 6000,
    \"effective_from\": \"2026-07-03T00:00:00Z\"
  }"
```

### Test 4: View API Documentation
Visit: http://localhost:8013/docs

Try these endpoints:
- `GET /api/v1/gold/products`
- `GET /api/v1/gold/appraisal/ornament-types`
- `GET /api/v1/gold/appraisal/market-rates/current`

---

## 🎯 What You Can Do Now

### Product Management
✅ Create unlimited gold loan products  
✅ Configure interest rates, tenure, LTV  
✅ Set up charges and fees  
✅ Define eligibility rules  
✅ Create approval workflows  

**Try It**: Create a new "Gold Wedding Loan" product with 14% interest and 80% LTV

### Customer Journey
✅ Track walk-in customers  
✅ Search existing customers  
✅ Get AI product recommendations  
✅ Validate eligibility  
✅ Log customer interactions  

**Try It**: Start a new journey and search for a customer

### Appraisal
✅ Create appraisal sessions  
✅ Catalog ornaments (15 types)  
✅ Record purity tests  
✅ Calculate valuations automatically  
✅ Track anomalies  

**Try It**: Create an appraisal session and add a gold chain

---

## 📊 Database Overview

You now have **25 tables** organized in 3 groups:

### Product Tables (10)
- gold_products
- gold_product_interest
- gold_product_tenure
- gold_product_limits
- gold_product_charges
- gold_product_documents
- gold_product_eligibility
- gold_product_workflow
- gold_product_channel
- gold_product_tax

### Journey Tables (7)
- gold_customer_sessions
- gold_customer_search_log
- gold_product_selections
- gold_eligibility_checks
- gold_kyc_verifications
- gold_journey_steps
- gold_customer_interactions

### Appraisal Tables (8)
- gold_ornament_types
- gold_ornaments (enhanced)
- gold_purity_tests
- gold_market_rates
- gold_appraisal_sessions
- gold_ornament_valuations
- gold_weight_verifications
- gold_appraisal_anomalies

**Check it**: 
```sql
psql -U nbfc_user -d nbfcsuite -c "\dt gold_*"
```

---

## 🔍 Explore the Platform

### Frontend Pages
1. **Products List**: http://localhost:3000/gold-lending/products
   - View all products
   - Filter by active/inactive
   - See key metrics (interest, LTV, amount range)

2. **Product Details**: http://localhost:3000/gold-lending/products/{id}
   - 8 comprehensive tabs
   - Interest & Tenure configuration
   - Limits & LTV
   - Charges & Fees
   - Documents required
   - Eligibility rules
   - Workflow stages
   - Available channels

3. **New Journey**: http://localhost:3000/gold-lending/journey/new
   - 5-step progressive flow
   - Customer search
   - Product recommendations
   - Eligibility checking

4. **Appraisal**: http://localhost:3000/gold-lending/appraisal/{sessionId}
   - Summary cards
   - Market rates display
   - Ornament cataloging
   - Real-time valuation

### API Endpoints (50+)
- **Products**: 20+ endpoints
- **Journey**: 15+ endpoints
- **Appraisal**: 15+ endpoints

**Explore**: http://localhost:8013/docs

---

## 💡 Quick Wins

### 1. Create Your First Custom Product (5 min)
```bash
curl -X POST http://localhost:8013/api/v1/gold/products \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "GL-CUSTOM-001",
    "product_name": "My Custom Gold Loan",
    "product_type": "jewel_loan",
    "is_active": true,
    "interest": {
      "interest_type": "reducing",
      "rate_type": "fixed",
      "base_rate": 11.5,
      "penal_interest": 2.0,
      "compounding_frequency": "monthly"
    },
    "tenure": {
      "min_tenure_months": 6,
      "max_tenure_months": 36,
      "default_tenure_months": 12,
      "renewal_allowed": true
    },
    "limits": {
      "min_loan_amount": 10000,
      "max_loan_amount": 1000000,
      "ltv_percent": 75.0,
      "min_gold_weight_grams": 5.0
    }
  }'
```

Then view it: http://localhost:3000/gold-lending/products

### 2. Set Today's Gold Rates (2 min)
```bash
# 22K Gold
curl -X POST http://localhost:8013/api/v1/gold/appraisal/market-rates \
  -H "Content-Type: application/json" \
  -d "{
    \"rate_date\": \"$(date +%Y-%m-%d)\",
    \"rate_source\": \"india_bullion\",
    \"purity_karat\": 22.0,
    \"rate_per_gram\": 6000,
    \"effective_from\": \"$(date +%Y-%m-%d)T00:00:00Z\"
  }"

# 24K Gold
curl -X POST http://localhost:8013/api/v1/gold/appraisal/market-rates \
  -H "Content-Type: application/json" \
  -d "{
    \"rate_date\": \"$(date +%Y-%m-%d)\",
    \"rate_source\": \"india_bullion\",
    \"purity_karat\": 24.0,
    \"rate_per_gram\": 6500,
    \"effective_from\": \"$(date +%Y-%m-%d)T00:00:00Z\"
  }"
```

### 3. Test Complete Journey (5 min)
1. Create journey session
2. Search/select customer
3. Get recommendations
4. Select product
5. Check eligibility
6. Create appraisal
7. Add ornament
8. Complete appraisal

---

## 🐛 Common Issues & Fixes

### Issue 1: Database Connection Failed
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string
# Should be: postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite
```

### Issue 2: Import Errors in Python
```bash
# Reinstall dependencies
cd C:\NBFCSUITE\services\gold
pip install -r requirements.txt --force-reinstall
```

### Issue 3: Frontend Not Loading
```bash
# Clear Next.js cache
cd C:\NBFCSUITE\apps\customer-app
rm -rf .next
npm run dev
```

### Issue 4: Port Already in Use
```bash
# Backend (8013)
netstat -ano | findstr :8013
taskkill /PID <process_id> /F

# Frontend (3000)
netstat -ano | findstr :3000
taskkill /PID <process_id> /F
```

---

## 📖 Learn More

### Documentation
- **README**: `services/gold/README.md`
- **Phase 1**: `services/gold/PHASE1_PRODUCT_ENGINE.md`
- **Phase 2**: `services/gold/PHASE2_CUSTOMER_JOURNEY.md`
- **Phase 3**: `services/gold/PHASE3_APPRAISAL_ENGINE.md`
- **Summary**: `services/gold/GOLD_LENDING_PLATFORM_SUMMARY.md`

### API Documentation
- **Swagger UI**: http://localhost:8013/docs
- **ReDoc**: http://localhost:8013/redoc

### Code Structure
```
services/gold/
├── app/
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routers/        # API endpoints
│   └── main.py         # Application entry
├── tests/              # Test files
└── requirements.txt    # Dependencies

apps/customer-app/
└── app/
    └── gold-lending/
        ├── products/   # Product pages
        ├── journey/    # Journey pages
        ├── appraisal/  # Appraisal pages
        └── goldApi.ts  # API client
```

---

## 🎓 Best Practices

### When Creating Products
- ✅ Use descriptive product codes (GL-JEWEL-001)
- ✅ Set realistic LTV limits (70-80%)
- ✅ Configure all charges upfront
- ✅ Define clear eligibility rules
- ✅ Test with various customer scenarios

### When Using Journey
- ✅ Always search before creating new CIF
- ✅ Log important customer interactions
- ✅ Follow eligibility failures with explanations
- ✅ Track session IDs for audit

### When Conducting Appraisals
- ✅ Use latest market rates
- ✅ Photograph all ornaments
- ✅ Record multiple purity tests
- ✅ Implement maker-checker for weights
- ✅ Investigate anomalies immediately

---

## 🚀 What's Next?

### Immediate (This Week)
1. ✅ Set up your development environment
2. ✅ Run all migrations
3. ✅ Seed initial data
4. ✅ Test all 3 phases
5. 📝 Customize products for your NBFC

### Short Term (This Month)
1. 📝 Configure your actual gold products
2. 📝 Set up daily gold rates (manual or API)
3. 📝 Train staff on new system
4. 📝 Start pilot with one branch
5. 📝 Gather feedback

### Medium Term (Next 3 Months)
1. 🔄 Implement Phase 4: Ornament Catalog
2. 🔄 Implement Phase 5: Vault Management
3. 🔄 Implement Phase 6: Disbursement
4. 🔄 Roll out to multiple branches
5. 🔄 Integrate with existing systems

### Long Term (6+ Months)
1. 🔮 Complete all 15 phases
2. 🔮 Mobile apps for staff and customers
3. 🔮 AI-powered intelligence
4. 🔮 Partner integrations
5. 🔮 Full production deployment

---

## 💪 You're Ready!

You now have:
- ✅ **50+ API endpoints** ready to use
- ✅ **25 database tables** with data
- ✅ **5 frontend pages** fully functional
- ✅ **Complete documentation** for reference
- ✅ **Production-ready code** with best practices

### Start Building!
1. **Test** the platform thoroughly
2. **Customize** products for your needs
3. **Train** your team
4. **Deploy** to staging
5. **Launch** your first gold loan

### Need Help?
- 📖 Read the documentation
- 🔍 Check API docs at /docs
- 🐛 Review troubleshooting guide
- 💬 Ask questions in your team

---

## 🎯 Success Metrics

Track these as you go live:
- **Appraisal Time**: Target < 10 minutes
- **Journey Completion**: Target > 80%
- **Data Accuracy**: Target 100% (maker-checker)
- **User Adoption**: Train all branch staff
- **Customer Satisfaction**: Survey after each loan

---

**You're all set! Start exploring the Gold Lending Platform! 🚀**

**Version**: 1.0.0 | **Date**: July 3, 2026 | **Status**: Ready to Use
