# CRILC & SMA Compliance - Quick Reference Guide

## 🚀 Quick Start

### 1. Identify Large Credits (Monthly)
```bash
curl -X POST http://localhost:8000/api/v1/compliance/crilc/identify-large-credits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "threshold_amount": 50000000,
    "as_on_date": "2024-03-31",
    "include_group_exposure": true
  }'
```

### 2. Calculate SMA Status (Daily)
```bash
curl -X POST http://localhost:8000/api/v1/compliance/sma/calculate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "as_on_date": "2024-03-31",
    "calculate_provisions": true
  }'
```

### 3. Generate Quarterly Return (Quarterly)
```bash
# Step 1: Generate CRILC return
curl -X POST http://localhost:8000/api/v1/compliance/crilc/quarterly-returns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "reporting_quarter": "Q4FY24",
    "reporting_year": "FY2023-24",
    "as_on_date": "2024-03-31"
  }'

# Step 2: Approve return
curl -X POST http://localhost:8000/api/v1/compliance/crilc/quarterly-returns/{id}/approve \
  -H "Authorization: Bearer {token}"

# Step 3: Submit return
curl -X POST http://localhost:8000/api/v1/compliance/crilc/quarterly-returns/{id}/submit \
  -H "Authorization: Bearer {token}" \
  -d '{"submission_reference": "RBI-2024-Q4-001"}'
```

### 4. View Dashboard
```bash
curl -X GET http://localhost:8000/api/v1/compliance/sma/dashboard?as_on_date=2024-03-31 \
  -H "Authorization: Bearer {token}"
```

---

## 📊 SMA Classification Rules

| Status | DPD Range | Action Required | Provision |
|--------|-----------|-----------------|-----------|
| **Standard** | 0 | Monitor | 0.40% |
| **SMA-0** | 1-30 days | Early contact | 0.40% |
| **SMA-1** | 31-60 days | Follow-up + restructure discussion | 0.40% |
| **SMA-2** | 61-90 days | Urgent action + legal notice | 0.40% |
| **Sub-Standard** | 91-365 days | Legal action | 15% |
| **Doubtful-1** | 366-730 days | Recovery proceedings | 25% |
| **Doubtful-2** | 731-1095 days | Asset disposal | 40% |
| **Doubtful-3** | >1095 days | Write-off consideration | 100% |

---

## 🎯 Large Credit Criteria

| Borrower Type | Aggregate Exposure Threshold |
|---------------|------------------------------|
| **All Borrowers** | ≥ ₹5 Crore (₹50,000,000) |
| **Group Borrowers** | Combined exposure ≥ ₹5 Crore |

**Exposure Calculation:**
```
Total Exposure = Funded Exposure + Non-Funded Exposure

Funded: Term Loans, Cash Credit, Overdraft, etc.
Non-Funded: Bank Guarantees, Letter of Credit, etc.
```

---

## 📅 Reporting Calendar

### Monthly Tasks
- **1st**: Identify large credits
- **Daily**: Calculate SMA status
- **Weekly**: Review alerts

### Quarterly Tasks (Due: 15th of month following quarter-end)

| Quarter | Period | Due Date | Return Generation Date |
|---------|--------|----------|------------------------|
| **Q1** | Apr-Jun | July 15 | July 1-7 |
| **Q2** | Jul-Sep | Oct 15 | Oct 1-7 |
| **Q3** | Oct-Dec | Jan 15 | Jan 1-7 |
| **Q4** | Jan-Mar | Apr 15 | Apr 1-7 |

---

## 🔔 Alert Severity Matrix

| Alert Type | Severity | Response Time | Escalation |
|------------|----------|---------------|------------|
| SMA-0 entry | Low | 3 days | Team Lead |
| SMA-1 entry | Medium | 2 days | Manager |
| SMA-2 entry | High | 1 day | Senior Manager |
| NPA slippage | Critical | Immediate | CRO/CEO |
| Large credit breach | Medium | 2 days | Compliance Head |

---

## 📋 Common Queries

### Get All SMA-2 Accounts
```sql
SELECT 
  b.borrower_name,
  l.loan_account_number,
  s.days_past_due,
  s.total_outstanding,
  s.total_overdue
FROM sma_tracking s
JOIN crilc_borrowers b ON s.borrower_id = b.id
JOIN loan_accounts l ON s.loan_account_id = l.id
WHERE s.current_sma_status = 'sma_2'
  AND s.tenant_id = '{tenant_id}'
ORDER BY s.total_outstanding DESC;
```

### Get Provision Requirements
```sql
SELECT 
  asset_classification,
  COUNT(*) as account_count,
  SUM(total_outstanding) as total_exposure,
  SUM(provision_required) as total_provision
FROM sma_tracking
WHERE tenant_id = '{tenant_id}'
  AND as_on_date = CURRENT_DATE
GROUP BY asset_classification;
```

### Get Large Credits by Industry
```sql
SELECT 
  industry_name,
  COUNT(*) as borrower_count,
  SUM(total_credit_exposure) as total_exposure
FROM crilc_borrowers
WHERE is_large_credit = true
  AND tenant_id = '{tenant_id}'
GROUP BY industry_name
ORDER BY total_exposure DESC;
```

---

## 🛠️ Troubleshooting

### Issue: SMA status not updating
**Solution:**
```bash
# Manually trigger calculation
POST /api/v1/compliance/sma/calculate
{
  "as_on_date": "2024-03-31",
  "loan_account_ids": ["uuid-here"]
}
```

### Issue: Large credit not identified
**Check:**
1. Is aggregate exposure ≥ ₹5 Cr?
2. Are all facilities added?
3. Run identification manually:
```bash
POST /api/v1/compliance/crilc/identify-large-credits
```

### Issue: Provision calculation incorrect
**Verify:**
1. Asset classification is correct
2. DPD is accurate
3. Check provision rates in SMAService

---

## 📞 Contact Information

**Compliance Team**: compliance@nbfc.com  
**Technical Support**: tech-support@nbfc.com  
**Emergency Hotline**: +91-XXXX-XXXXXX

---

## 📚 Additional Resources

- [Full Documentation](./backend/services/compliance/README.md)
- [RBI CRILC Guidelines](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=9900)
- [RBI SMA Norms](https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=10598)
- [Provisioning Norms](https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=9857)

---

*Quick Reference v1.0 - January 2024*
