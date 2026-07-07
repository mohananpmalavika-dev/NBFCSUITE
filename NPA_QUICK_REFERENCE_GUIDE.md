# NPA Management - Quick Reference Guide

## 🚀 Quick Start (5 Minutes)

### Access the Module
```
URL: http://localhost:3000/accounting/npa
Navigation: Accounting → NPA Management
```

### Key Pages
1. **Dashboard** - `/accounting/npa`
2. **Classify Loan** - `/accounting/npa/classify`
3. **Calculate Provisioning** - `/accounting/npa/calculator`
4. **View Register** - `/accounting/npa/register`
5. **Movement Report** - `/accounting/npa/movement`
6. **Batch Process** - `/accounting/npa/batch-classification`

---

## 📋 Common Tasks

### 1. Classify a Single Loan (2 minutes)
```
1. Go to: /accounting/npa/classify
2. Enter: Days Past Due (e.g., 120)
3. Check: Restructured? Written-off?
4. Click: "Classify"
5. Result: NPA category displayed
```

**Example Output:**
```
Category: SUBSTANDARD
DPD: 120 days
Is NPA: Yes
Classification Date: 2026-07-07
```

### 2. Calculate Provisioning (3 minutes)
```
1. Go to: /accounting/npa/calculator
2. Enter Outstanding: ₹5,00,000
3. Select Category: Substandard
4. Select Security: Secured
5. Enter Coverage: 80%
6. Enter Existing Provision: ₹0
7. Click: "Calculate Provisioning"
```

**Example Output:**
```
Provisioning Rate: 15%
Required Provision: ₹75,000
Additional Provision: ₹75,000
```

### 3. Run Monthly Classification (10 minutes)
```
1. Go to: /accounting/npa/batch-classification
2. Select Date: Last day of month
3. Click: "Run Classification"
4. Wait: Progress bar (1-5 minutes)
5. Review: Results and statistics
```

**Expected Output:**
```
Total Processed: 500 accounts
Provisions Created: ₹28,50,000
New NPAs: 3 accounts
NPA Ratio: 5.0%
```

### 4. Generate Asset Register (5 minutes)
```
1. Go to: /accounting/npa/register
2. Select Date: As of date
3. Select Category: All or specific
4. Click: "Generate Register"
5. Export: Download report
```

### 5. View Movement Report (5 minutes)
```
1. Go to: /accounting/npa/movement
2. Enter From Date: Start of month
3. Enter To Date: End of month
4. Click: "Generate Report"
5. Review: Additions, Reductions, Net Change
```

---

## 📊 RBI Classification Quick Reference

### Categories & DPD
```
Category          DPD Range        Action Required
─────────────────────────────────────────────────────────
STANDARD          0 DPD            Regular monitoring
SMA-0            1-30 DPD         Contact customer
SMA-1            31-60 DPD        Intensify collection
SMA-2            61-90 DPD        Alert management
SUBSTANDARD      91-365 DPD       Create provision + NPA
DOUBTFUL-1       366-730 DPD      Increase provision
DOUBTFUL-2       731-1095 DPD     Legal action
DOUBTFUL-3       1096+ DPD        Consider write-off
LOSS             Identified       Write-off process
```

### Provisioning Rates
```
Category          Secured    Unsecured
─────────────────────────────────────────
Standard          0.25%      0.25%
SMA              0%         0%
Substandard      15%        25%
Doubtful-1       25-100%    100%
Doubtful-2       40-100%    100%
Doubtful-3       100%       100%
Loss             100%       100%
```

---

## 🎯 Key Metrics to Monitor

### Daily
- [ ] SMA-2 accounts (high risk)
- [ ] Fresh NPA slippages
- [ ] Collection performance

### Weekly
- [ ] SMA pipeline (0, 1, 2)
- [ ] Recovery rates
- [ ] Provision adequacy

### Monthly
- [ ] Run batch classification
- [ ] Generate movement report
- [ ] Review NPA ratio
- [ ] Calculate PCR
- [ ] Management presentation

### Quarterly
- [ ] RBI NPA return
- [ ] Board presentation
- [ ] Audit preparation
- [ ] Trend analysis

---

## ⚡ API Quick Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
```javascript
Headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN',
  'Content-Type': 'application/json',
  'X-Tenant-ID': 'YOUR_TENANT_ID'
}
```

### Key Endpoints

**Classify Loan**
```bash
POST /accounting/npa/classify
{
  "days_past_due": 120,
  "is_restructured": false,
  "is_written_off": false
}
```

**Calculate Provisioning**
```bash
POST /accounting/npa/provisioning/calculate
{
  "outstanding_principal": 500000,
  "npa_category": "SUBSTANDARD",
  "is_secured": true,
  "security_coverage_ratio": 80,
  "existing_provision": 0
}
```

**Get NPA Summary**
```bash
GET /accounting/npa/summary?as_of_date=2026-07-31
```

**Run Batch Classification**
```bash
POST /accounting/npa/batch/monthly-classification
{
  "as_of_date": "2026-07-31"
}
```

---

## 🔍 Troubleshooting

### Issue: Classification not working
**Solution:**
- Check DPD is correctly calculated
- Verify loan account is active
- Check date is valid

### Issue: Provisioning calculation wrong
**Solution:**
- Verify NPA category is correct
- Check security coverage ratio
- Ensure outstanding amount is correct

### Issue: Batch process fails
**Solution:**
- Check all loans have valid DPD
- Ensure sufficient system resources
- Run during off-peak hours

### Issue: Reports not generating
**Solution:**
- Check date range is valid
- Verify data exists for period
- Clear browser cache

---

## 📱 Mobile Access

### Responsive URLs (Same as Desktop)
```
Dashboard:    /accounting/npa
Classify:     /accounting/npa/classify
Calculator:   /accounting/npa/calculator
Register:     /accounting/npa/register
```

### Mobile-Optimized Features
- ✅ Touch-friendly buttons
- ✅ Simplified forms
- ✅ Horizontal scrolling tables
- ✅ Responsive charts

---

## 🎓 Training Checklist

### Operations Team
- [ ] Navigate NPA dashboard
- [ ] Classify individual loans
- [ ] Interpret category badges
- [ ] Generate basic reports
- [ ] Export data

### Finance Team
- [ ] Calculate provisioning
- [ ] Create provision entries
- [ ] Run monthly batch
- [ ] Generate movement reports
- [ ] Prepare RBI returns

### Management
- [ ] Read dashboard metrics
- [ ] Understand key ratios
- [ ] Review trend reports
- [ ] Approve write-offs
- [ ] Board presentations

---

## 💡 Pro Tips

### Best Practices
1. **Run batch on last day of month** for accurate month-end
2. **Review SMA accounts daily** to prevent NPAs
3. **Export reports regularly** for audit trail
4. **Monitor PCR weekly** to ensure adequacy
5. **Document all write-offs** with justification

### Keyboard Shortcuts
```
Ctrl + /     - Search
Ctrl + K     - Quick navigation
Esc          - Close modal
Tab          - Next field
Shift + Tab  - Previous field
```

### Time-Saving Tips
- Use filters to narrow down accounts
- Bookmark frequently used pages
- Set up scheduled reports
- Use batch processing for bulk operations
- Export to Excel for offline analysis

---

## 🆘 Getting Help

### Documentation
- **User Guide**: `NPA_MANAGEMENT_DOCUMENTATION.md`
- **Examples**: `NPA_MANAGEMENT_EXAMPLES.md`
- **Integration**: `NPA_INTEGRATION_GUIDE.md`
- **API Docs**: http://api.nbfcsuite.com/docs

### Support Channels
- **Email**: support@nbfcsuite.com
- **Phone**: +91-XXXX-XXXXX (24/7)
- **Chat**: In-app support button
- **Forum**: https://forum.nbfcsuite.com

### Self-Service
- **Knowledge Base**: https://kb.nbfcsuite.com
- **Video Tutorials**: https://learn.nbfcsuite.com
- **FAQs**: https://help.nbfcsuite.com
- **Community**: https://community.nbfcsuite.com

---

## 📊 Performance Targets

### System Performance
- Page Load: < 2 seconds
- API Response: < 500ms
- Batch Processing: < 5 minutes (for 1000 loans)
- Report Generation: < 10 seconds

### Business Metrics
- Gross NPA Ratio: < 5%
- Net NPA Ratio: < 2.5%
- PCR: > 70%
- SMA to NPA Conversion: < 10%

---

## 🔐 Security Best Practices

### Access Control
- ✅ Use strong passwords
- ✅ Enable 2FA
- ✅ Log out after use
- ✅ Don't share credentials
- ✅ Review access logs

### Data Protection
- ✅ Export sensitive data securely
- ✅ Use encrypted connections (HTTPS)
- ✅ Backup regularly
- ✅ Follow retention policies
- ✅ Report suspicious activity

---

## 📅 Monthly Checklist

### Week 1
- [ ] Monitor SMA accounts daily
- [ ] Track collection performance
- [ ] Review fresh NPAs

### Week 2
- [ ] Mid-month review
- [ ] Update projections
- [ ] Escalate high-risk accounts

### Week 3
- [ ] Pre-closing preparation
- [ ] Verify all payments posted
- [ ] Review pending cases

### Week 4
- [ ] Run batch classification (last day)
- [ ] Generate all reports
- [ ] Management review
- [ ] Board presentation (if quarterly)

---

## 🎯 Success Criteria

### Daily
✅ All SMA accounts reviewed  
✅ Fresh NPAs escalated  
✅ Collections tracked

### Weekly
✅ Movement report reviewed  
✅ Trends identified  
✅ Actions taken

### Monthly
✅ Batch classification completed  
✅ Provisions accurate  
✅ Reports generated  
✅ Management informed

### Quarterly
✅ RBI returns submitted  
✅ Board presentation done  
✅ Audit ready  
✅ Targets met

---

## 📞 Emergency Contacts

### Technical Issues
**IT Support**: +91-XXXX-XXXX1  
**Email**: tech@nbfcsuite.com  
**Available**: 24/7

### Business Issues
**Operations Head**: +91-XXXX-XXXX2  
**Finance Head**: +91-XXXX-XXXX3  
**Compliance Head**: +91-XXXX-XXXX4

### Escalation
**Level 1**: Support team (0-2 hours)  
**Level 2**: Technical lead (2-4 hours)  
**Level 3**: Product manager (4-8 hours)  
**Level 4**: CTO (8-24 hours)

---

## ✅ Quick Checklist Before Month-End

**Day -3 (Three days before month-end)**
- [ ] Verify all payments posted
- [ ] Update security valuations
- [ ] Review pending restructurings
- [ ] Check data accuracy

**Day -1 (Day before month-end)**
- [ ] Final payment posting
- [ ] Resolve discrepancies
- [ ] Backup current data
- [ ] Notify team

**Month-End Day**
- [ ] Run batch classification
- [ ] Review results
- [ ] Generate reports
- [ ] Create provisions
- [ ] Update management

**Day +1 (Next day)**
- [ ] Verify journal entries
- [ ] Review exceptions
- [ ] Final report distribution
- [ ] Archive documentation

---

## 🎉 You're Ready!

This quick reference covers all essential operations for the NPA Management module. For detailed information, refer to the comprehensive documentation.

**Remember:**
- Start with the dashboard
- Use the classifier for quick checks
- Run batch monthly
- Monitor metrics daily
- Report issues promptly

**Need Help?** Contact support@nbfcsuite.com

---

**Last Updated**: July 7, 2026  
**Version**: 1.0.0  
**Status**: Production Ready

**END OF QUICK REFERENCE GUIDE**
