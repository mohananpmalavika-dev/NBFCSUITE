# ALM Module - Quick Start Guide 🚀

## Overview
This guide will help you run and test the complete ALM (Asset Liability Management) frontend that has been integrated with the backend.

---

## 📋 Prerequisites

### Backend Requirements
- ✅ Python 3.10+
- ✅ PostgreSQL database
- ✅ All backend dependencies installed
- ✅ Database migrations applied

### Frontend Requirements
- ✅ Node.js 18+
- ✅ npm or yarn
- ✅ All frontend dependencies installed

---

## 🚀 Starting the Application

### Step 1: Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already active)
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Run database migrations (if not already done)
alembic upgrade head

# Start the backend server
uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 2: Start Frontend Server

Open a new terminal:

```bash
# Navigate to frontend admin portal
cd frontend/apps/admin-portal

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 14.0.4
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

---

## 🧪 Testing the ALM Module

### Access Points

1. **Main Entry:** http://localhost:3000/treasury/alm
2. **Dashboard:** http://localhost:3000/treasury/alm/dashboard
3. **Maturity Ladder:** http://localhost:3000/treasury/alm/maturity-ladder
4. **Gap Analysis:** http://localhost:3000/treasury/alm/gap-analysis
5. **Liquidity Ratios:** http://localhost:3000/treasury/alm/liquidity-ratios
6. **Interest Rate Risk:** http://localhost:3000/treasury/alm/interest-rate-risk
7. **Quarterly Returns:** http://localhost:3000/treasury/alm/quarterly-returns
8. **Alerts:** http://localhost:3000/treasury/alm/alerts

### Recommended Testing Flow

#### 1️⃣ Start at the Landing Page
```
URL: http://localhost:3000/treasury/alm
```
**What to Check:**
- ✅ Page loads without errors
- ✅ 7 module cards are visible
- ✅ Navigation works on click
- ✅ Quick start guide is readable
- ✅ Responsive layout on different screen sizes

#### 2️⃣ Test the Dashboard
```
URL: http://localhost:3000/treasury/alm/dashboard
```
**What to Check:**
- ✅ 8 summary KPI cards load
- ✅ Data displays correctly
- ✅ Refresh button works
- ✅ Navigation to detail pages works
- ✅ Date selector functions
- ✅ Active alerts section shows alerts

**Expected Data:**
- LCR, NSFR, SLR ratios
- Maturity ladder summary
- Gap analysis overview
- Key metrics with proper formatting

#### 3️⃣ Test Maturity Ladder
```
URL: http://localhost:3000/treasury/alm/maturity-ladder
```
**What to Check:**
- ✅ Date selector works
- ✅ 12 time buckets displayed
- ✅ Assets and liabilities shown
- ✅ Gap calculations correct
- ✅ Cumulative gap updates
- ✅ Progress bars render
- ✅ Export button present
- ✅ Risk indicators show correctly

**Test Cases:**
1. Change date and verify data updates
2. Check all 12 buckets have data
3. Verify gap calculations (Assets - Liabilities)
4. Check percentage calculations
5. Test export functionality

#### 4️⃣ Test Gap Analysis
```
URL: http://localhost:3000/treasury/alm/gap-analysis
```
**What to Check:**
- ✅ All 4 gap types accessible via tabs/cards
- ✅ Liquidity gap data loads
- ✅ Interest rate gap data loads
- ✅ Maturity gap data loads
- ✅ Duration gap data loads
- ✅ Period-wise breakdown tabs work
- ✅ Recommendations display
- ✅ Risk level badges show correctly

**Test Cases:**
1. Switch between all 4 gap types
2. Verify inflows and outflows display
3. Check net gap calculation
4. Test period breakdown tabs
5. Verify risk level indicators

#### 5️⃣ Test Liquidity Ratios
```
URL: http://localhost:3000/treasury/alm/liquidity-ratios
```
**What to Check:**
- ✅ 3 key regulatory ratio cards (LCR, NSFR, SLR)
- ✅ Traditional ratios section with 6+ ratios
- ✅ Reserve ratios (CRR, SLR) with balances
- ✅ Basel III metrics with details
- ✅ Additional metrics (12+ ratios)
- ✅ Maturity mismatch indicators
- ✅ Compliance status section
- ✅ All progress bars render

**Test Cases:**
1. Check threshold indicators (compliant/non-compliant)
2. Verify LCR components (HQLA, net outflows)
3. Verify NSFR components (ASF, RSF)
4. Check all ratio calculations
5. Test compliance status indicators

#### 6️⃣ Test Interest Rate Risk
```
URL: http://localhost:3000/treasury/alm/interest-rate-risk
```
**What to Check:**
- ✅ All 7 scenario tabs accessible
- ✅ Base scenario loads by default
- ✅ NII impact displays correctly
- ✅ EVE impact displays correctly
- ✅ Duration gap shows
- ✅ Repricing gap analysis present
- ✅ Scenario comparison table works
- ✅ Recommendations display

**Test Cases:**
1. Switch between all 7 scenarios
2. Verify impact calculations
3. Check duration analysis
4. Test scenario comparison table
5. Verify risk level indicators change per scenario

#### 7️⃣ Test Quarterly Returns
```
URL: http://localhost:3000/treasury/alm/quarterly-returns
```
**What to Check:**
- ✅ Summary cards show counts
- ✅ Create new return button works
- ✅ Returns list displays
- ✅ Status badges show correctly
- ✅ Submit dialog opens
- ✅ Approve dialog opens
- ✅ Reject dialog opens
- ✅ Export button works

**Test Cases:**
1. Create a new quarterly return
2. Submit a draft return (with comments)
3. Approve a submitted return
4. Reject a submitted return (requires reason)
5. Export a return
6. Check workflow state transitions
7. Verify all status badges

#### 8️⃣ Test Alerts
```
URL: http://localhost:3000/treasury/alm/alerts
```
**What to Check:**
- ✅ Summary cards with alert counts
- ✅ 3 tabs (Active, Acknowledged, Resolved)
- ✅ Alert cards display with severity
- ✅ Acknowledge button works
- ✅ Resolve dialog opens
- ✅ Resolution requires text
- ✅ Alert guidelines section present

**Test Cases:**
1. View active alerts
2. Acknowledge an alert
3. Resolve an alert (with resolution text)
4. Switch between tabs
5. Verify severity color coding
6. Check empty states

---

## 🐛 Troubleshooting

### Issue: Pages show "No data available"

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/treasury/alm/dashboard

# Check database has data
# Run data seeding script if needed
```

### Issue: API calls fail with CORS error

**Solution:**
Check `backend/main.py` for CORS configuration:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Components not rendering

**Solution:**
```bash
# Check if all dependencies are installed
cd frontend/apps/admin-portal
npm install

# Clear Next.js cache
rm -rf .next
npm run dev
```

### Issue: TypeScript errors

**Solution:**
```bash
# Run type checking
npm run type-check

# Check for missing type definitions
```

### Issue: 404 on API calls

**Solution:**
- Verify backend router is registered in `main.py`
- Check ALM router prefix: `/api/v1/treasury/alm`
- Verify backend is running on port 8000

---

## 📊 Sample Test Data

### Creating Test Data via API

You can use the backend directly to create test data:

```bash
# Create maturity ladder data
curl -X POST http://localhost:8000/api/v1/treasury/alm/maturity-ladder \
  -H "Content-Type: application/json" \
  -d '{
    "reporting_date": "2024-01-31",
    "bucket": "days_2_7",
    "asset_amount": 1000000,
    "liability_amount": 800000
  }'

# Create an alert
curl -X POST http://localhost:8000/api/v1/treasury/alm/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "LCR Breach",
    "severity": "high",
    "message": "LCR has fallen below 100%",
    "threshold_value": "100",
    "actual_value": "95"
  }'
```

---

## 🔍 Verification Checklist

### Functional Testing
- [ ] All 8 pages load without errors
- [ ] Navigation works correctly
- [ ] Date selectors function
- [ ] Data displays correctly
- [ ] Charts/visualizations render
- [ ] Buttons trigger actions
- [ ] Dialogs open and close
- [ ] Forms validate input
- [ ] Export functionality works
- [ ] Refresh updates data

### UI/UX Testing
- [ ] Responsive on mobile (375px)
- [ ] Responsive on tablet (768px)
- [ ] Responsive on desktop (1920px)
- [ ] Colors are consistent
- [ ] Icons display correctly
- [ ] Loading states show
- [ ] Empty states show
- [ ] Error states handle gracefully
- [ ] Tooltips are helpful
- [ ] Typography is readable

### Performance Testing
- [ ] Pages load within 2 seconds
- [ ] No console errors
- [ ] No console warnings
- [ ] Images optimized
- [ ] API calls are efficient
- [ ] No memory leaks

### Accessibility Testing
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast meets WCAG
- [ ] Focus indicators visible
- [ ] Alt text on images
- [ ] ARIA labels present

---

## 📈 Performance Benchmarks

### Expected Load Times
- Landing Page: < 1 second
- Dashboard: < 2 seconds
- Detail Pages: < 1.5 seconds
- API Calls: < 500ms

### Browser Compatibility
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## 🔐 Security Considerations

### Authentication
- All pages should require authentication
- Tokens should be validated
- Session timeout should work

### Authorization
- Only authorized users can access ALM
- Treasury role required
- Approval actions need senior permissions

### Data Protection
- Sensitive data masked where appropriate
- API calls use HTTPS in production
- No sensitive data in logs

---

## 📝 Testing Scripts

### Automated API Testing (Optional)

Create a test script `test-alm-api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api/v1/treasury/alm"
DATE="2024-01-31"

echo "Testing ALM API Endpoints..."

echo "\n1. Testing Dashboard..."
curl -s "$BASE_URL/dashboard?date=$DATE" | jq

echo "\n2. Testing Maturity Ladder..."
curl -s "$BASE_URL/maturity-ladder?date=$DATE" | jq

echo "\n3. Testing Gap Analysis..."
curl -s "$BASE_URL/gap-analysis?date=$DATE" | jq

echo "\n4. Testing Liquidity Ratios..."
curl -s "$BASE_URL/liquidity-ratios?date=$DATE" | jq

echo "\n5. Testing Interest Rate Risk..."
curl -s "$BASE_URL/interest-rate-risk?date=$DATE" | jq

echo "\n6. Testing Quarterly Returns..."
curl -s "$BASE_URL/quarterly-returns" | jq

echo "\n7. Testing Alerts..."
curl -s "$BASE_URL/alerts" | jq

echo "\nAll API tests completed!"
```

Run with:
```bash
chmod +x test-alm-api.sh
./test-alm-api.sh
```

---

## 🎯 Success Criteria

### Minimum Viable Product (MVP)
- ✅ All 8 pages accessible
- ✅ Core functionality works
- ✅ Data displays correctly
- ✅ No critical bugs

### Production Ready
- ✅ All features tested
- ✅ Performance optimized
- ✅ Security reviewed
- ✅ Documentation complete
- ✅ User acceptance testing passed

---

## 📞 Getting Help

### Common Questions

**Q: Where is the API documentation?**
A: Backend API docs at http://localhost:8000/docs (Swagger UI)

**Q: How do I add new ALM metrics?**
A: 
1. Add to backend schema
2. Update frontend types
3. Update service layer
4. Add to UI components

**Q: Can I customize thresholds?**
A: Yes, thresholds are configurable in the backend service layer.

**Q: How do I generate reports?**
A: Use the export functionality on each page to download Excel reports.

---

## 🎉 Next Steps

After testing is complete:

1. **Deploy to Staging**
   ```bash
   # Build frontend
   npm run build
   
   # Deploy to staging server
   ```

2. **User Acceptance Testing**
   - Get feedback from treasury team
   - Test with real data
   - Refine based on feedback

3. **Production Deployment**
   - Final QA round
   - Deploy to production
   - Monitor for issues

4. **Training**
   - Train users on ALM features
   - Provide user documentation
   - Set up support process

---

## 📚 Additional Resources

### Documentation
- `ALM_FRONTEND_COMPLETE.md` - Complete implementation details
- `ALM_README.md` - Module overview
- `docs/ALM_ASSET_LIABILITY_MANAGEMENT.md` - User guide

### Code References
- Backend: `backend/services/treasury/alm_*`
- Frontend: `frontend/apps/admin-portal/src/app/treasury/alm/*`
- Types: `frontend/apps/admin-portal/src/types/alm.ts`
- Services: `frontend/apps/admin-portal/src/services/almService.ts`

---

**Happy Testing! 🚀**

If you encounter any issues, check the troubleshooting section or review the backend logs and browser console for detailed error messages.
