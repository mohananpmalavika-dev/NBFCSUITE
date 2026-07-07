# AML/CFT Module - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Run Database Migration

```bash
cd backend
alembic upgrade head
```

### Step 2: Register AML Router

Edit `backend/main.py`:

```python
from backend.services.aml.router import router as aml_router

# Add to your FastAPI app
app.include_router(aml_router, prefix="/api", tags=["AML/CFT"])
```

### Step 3: Add Navigation Menu

Edit your navigation file (e.g., `frontend/apps/admin-portal/src/components/Navigation.tsx`):

```tsx
{
  title: "AML/CFT",
  icon: Shield,
  href: "/aml",
  items: [
    { title: "Dashboard", href: "/aml" },
    { title: "Alerts", href: "/aml/alerts" },
    { title: "Transaction Monitoring", href: "/aml/transaction-monitoring" },
    { title: "CTR Reports", href: "/aml/ctr" },
    { title: "STR Reports", href: "/aml/str" },
    { title: "PEP Screening", href: "/aml/pep-screening" },
    { title: "Sanction Screening", href: "/aml/sanction-screening" },
  ]
}
```

### Step 4: Configure Initial Monitoring Rules

Create default monitoring rules via API or admin panel:

```python
# Example: Large Cash Transaction Rule
POST /api/aml/monitoring-rules
{
  "rule_code": "LARGE_CASH",
  "rule_name": "Large Cash Transaction",
  "rule_type": "threshold",
  "description": "Alert on cash transactions >= 5 Lakhs",
  "threshold_amount": 500000,
  "risk_score_addition": 30,
  "auto_risk_level": "high",
  "generate_alert": true,
  "require_review": true,
  "is_active": true,
  "priority": 9
}
```

## 📋 Common Tasks

### Monitor a Transaction

```typescript
import { amlService } from '@/services/aml.service';

const result = await amlService.monitorTransaction({
  transaction_id: "TXN20260707001",
  transaction_type: "cash_deposit",
  transaction_date: new Date().toISOString(),
  posting_date: new Date().toISOString().split('T')[0],
  customer_id: customerId,
  customer_name: "John Doe",
  customer_type: "individual",
  transaction_amount: 1500000, // ₹15 Lakhs
  transaction_currency: "INR",
  is_cash_transaction: true,
  account_number: "1234567890"
});
```

### Auto-Generate CTRs for Month

```typescript
const result = await amlService.autoGenerateCTRs("2026-07");
// Automatically creates CTR for all cash transactions >= 10 Lakhs
```

### Create STR Report

```typescript
const str = await amlService.createSTRReport({
  customer_id: customerId,
  customer_name: "Suspicious Customer",
  customer_type: "individual",
  account_numbers: ["1234567890"],
  suspicious_activity_type: "structuring",
  activity_start_date: "2026-07-01",
  activity_end_date: "2026-07-07",
  total_amount_involved: 5000000,
  number_of_transactions: 10,
  suspicious_activity_description: "Multiple transactions just below CTR threshold",
  reason_for_suspicion: "Possible structuring to avoid CTR reporting"
});
```

### Screen Customer for PEP

```typescript
const screening = await amlService.createPEPScreening({
  customer_id: customerId,
  customer_name: "Customer Name",
  date_of_birth: "1980-01-01",
  nationality: "India",
  screening_type: "onboarding",
  trigger_event: "new_customer"
});
```

### Screen Against Sanctions

```typescript
const screening = await amlService.createSanctionScreening({
  customer_id: customerId,
  customer_name: "Customer Name",
  screening_type: "onboarding",
  trigger_event: "new_customer"
});
```

## 🎯 Default Monitoring Rules to Configure

### 1. Large Cash Transactions
- **Threshold**: ₹5,00,000+
- **Risk Score**: +30
- **Action**: Generate alert, require review

### 2. CTR Threshold
- **Threshold**: ₹10,00,000+
- **Risk Score**: +20
- **Action**: Auto-generate CTR, generate alert

### 3. Velocity Check
- **Pattern**: >10 transactions in 24 hours
- **Risk Score**: +25
- **Action**: Generate alert

### 4. Structuring Detection
- **Pattern**: Multiple transactions 80-90% of CTR threshold
- **Risk Score**: +50
- **Action**: High priority alert, require review

### 5. Cross-Border High Risk
- **Countries**: Configure high-risk country list
- **Risk Score**: +40
- **Action**: Generate alert, require review

### 6. Round Amount Detection
- **Pattern**: Round amounts (₹1,00,000, ₹5,00,000, etc.)
- **Risk Score**: +15
- **Action**: Generate alert

## 📊 Dashboard Access

Navigate to: `http://your-domain/aml`

You'll see:
- Real-time transaction monitoring stats
- Open alerts requiring attention
- Pending CTR/STR reports
- PEP screening summary
- Sanction screening results

## ⚡ API Endpoints Quick Reference

### Transaction Monitoring
- `POST /api/aml/transaction-monitoring` - Monitor transaction
- `GET /api/aml/transaction-monitoring` - List transactions

### Alerts
- `GET /api/aml/alerts` - List alerts
- `POST /api/aml/alerts/{id}/assign` - Assign alert
- `POST /api/aml/alerts/{id}/review` - Review alert
- `POST /api/aml/alerts/{id}/close` - Close alert

### CTR
- `POST /api/aml/ctr` - Create CTR
- `POST /api/aml/ctr/auto-generate?reporting_month=YYYY-MM` - Auto-generate
- `POST /api/aml/ctr/{id}/approve` - Approve

### STR
- `POST /api/aml/str` - Create STR
- `POST /api/aml/str/{id}/approve` - Approve
- `POST /api/aml/str/{id}/submit-fiu` - Submit to FIU

### PEP/Sanctions
- `POST /api/aml/pep-screening` - Screen for PEP
- `POST /api/aml/sanction-screening` - Screen against sanctions

### Dashboard
- `GET /api/aml/dashboard` - Get all statistics

## 🔐 Permissions Setup

Create these roles/permissions:

1. **AML Analyst**
   - View all AML data
   - Create and review alerts
   - Create CTR/STR reports

2. **AML Manager**
   - All Analyst permissions
   - Approve CTR/STR reports
   - Configure monitoring rules
   - View audit logs

3. **Compliance Officer**
   - All Manager permissions
   - Submit reports to FIU
   - Access to all sensitive data

## 🧪 Testing the Setup

### 1. Test Transaction Monitoring
```bash
curl -X POST http://localhost:8000/api/aml/transaction-monitoring \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "transaction_id": "TEST001",
    "transaction_type": "cash_deposit",
    "transaction_date": "2026-07-07T10:00:00Z",
    "posting_date": "2026-07-07",
    "customer_id": "customer-uuid",
    "customer_name": "Test Customer",
    "customer_type": "individual",
    "transaction_amount": 1500000,
    "is_cash_transaction": true
  }'
```

### 2. Check Dashboard
```bash
curl http://localhost:8000/api/aml/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. List Alerts
```bash
curl http://localhost:8000/api/aml/alerts?status=open \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📈 Monitoring & Maintenance

### Daily Tasks
- Review open alerts
- Check overdue items
- Monitor high-risk transactions

### Weekly Tasks
- Review closed alerts for patterns
- Update monitoring rules if needed
- Generate CTRs for submission

### Monthly Tasks
- Submit CTRs to FIU
- Review PEP screenings
- Update sanction lists
- Generate compliance reports

## 🆘 Troubleshooting

### Issue: Transactions not being monitored
**Check:**
1. Are monitoring rules active?
2. Is the transaction within rule parameters?
3. Check logs for errors

### Issue: Alerts not generating
**Check:**
1. Rule configuration: `generate_alert: true`
2. Risk score threshold met
3. Alert service running

### Issue: Dashboard showing zero stats
**Check:**
1. Database connection
2. Data in tables
3. API authentication

## 📚 Next Steps

1. ✅ Configure all monitoring rules
2. ✅ Import sanction lists
3. ✅ Set up PEP database
4. ✅ Train compliance team
5. ✅ Configure FIU submission
6. ✅ Set up email notifications
7. ✅ Create operational procedures
8. ✅ Schedule regular reviews

## 🎓 Training Resources

### For Users
- Dashboard walkthrough
- Alert management process
- CTR/STR filing procedures
- PEP screening guidelines

### For Administrators
- Rule configuration
- System monitoring
- Integration setup
- Troubleshooting guide

---

**Need Help?**
- Check `AML_CFT_IMPLEMENTATION_COMPLETE.md` for detailed documentation
- Review API documentation
- Check service logs for detailed errors

**Version**: 1.0.0  
**Last Updated**: July 7, 2026
