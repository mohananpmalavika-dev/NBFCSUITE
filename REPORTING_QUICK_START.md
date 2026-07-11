# Reporting & Analytics - Quick Start Guide

Get up and running with the Reporting & Analytics module in 5 minutes!

---

## 🚀 Quick Start

### Step 1: Access the Module

Navigate to the Reports section:
```
http://localhost:3000/reports
```

You'll see the reporting hub with all available features.

---

### Step 2: Generate Your First Report

#### Using Pre-built Templates

1. **Go to Report Templates**
   ```
   Click "Report Templates" or navigate to /reports/templates
   ```

2. **Browse Reports**
   - Use category filters (Portfolio, Collection, Risk, etc.)
   - Search by name
   - View report descriptions

3. **Generate a Report**
   - Click "Generate" on any report
   - Set parameters (date range, filters)
   - Choose output format (PDF/Excel/CSV)
   - Click "Generate Report"

**Example: Portfolio Summary Report**
```
1. Go to /reports/templates
2. Find "Portfolio Summary Report"
3. Click "Generate"
4. Set date range: Last 30 days
5. Click "Generate"
6. Download or view online
```

---

### Step 3: View Executive Dashboard

See real-time metrics at a glance:

```
1. Navigate to /reports/dashboards
2. Click "Executive Dashboard"
3. View KPIs:
   - Total Portfolio
   - Collection Efficiency
   - NPA Ratio
   - Total Customers
4. Widgets auto-refresh every 5 minutes
```

---

### Step 4: Build a Custom Report

Create your own report without SQL:

```
1. Go to /reports/builder
2. Enter report name: "My Custom Report"
3. Select data source: "Loan Accounts"
4. Choose fields:
   ☑ Account Number
   ☑ Sanctioned Amount
   ☑ Status
   ☑ Branch
5. Add filter: Status = "Active"
6. Select visualization: Bar Chart
7. Click "Save Report"
8. Click "Generate" to run
```

---

### Step 5: Try Predictive Analytics

Make your first ML prediction:

```
1. Navigate to /reports/analytics
2. Select "Credit Risk Scoring" use case
3. Input customer features:
   - Credit Score: 750
   - Income: 50,000
   - Existing Loans: 2
   - Payment History: Good
4. Click "Predict"
5. View result:
   - Risk Grade: LOW_RISK
   - Confidence: 85%
   - Explanation provided
```

---

## 📊 Common Use Cases

### Use Case 1: Daily Portfolio Report

**Objective**: Generate daily portfolio summary for management

**Steps**:
1. Go to `/reports/templates`
2. Find "Portfolio Summary Report"
3. Click "Generate"
4. Set yesterday's date
5. Download as PDF
6. Email to management

**Pro Tip**: Schedule this report to run automatically every morning at 9 AM.

---

### Use Case 2: Collection Efficiency Tracking

**Objective**: Monitor collection performance

**Steps**:
1. Go to `/reports/dashboards`
2. Open "Collection Dashboard"
3. View real-time metrics:
   - Collection efficiency %
   - Overdue amount
   - Collector performance
4. Drill down into specific collectors
5. Export data if needed

---

### Use Case 3: Risk Assessment

**Objective**: Identify high-risk accounts

**Steps**:
1. Go to `/reports/templates`
2. Select "Early Warning Signals"
3. Generate report
4. Review flagged accounts
5. Take action on high-risk cases

---

### Use Case 4: Custom Branch Report

**Objective**: Create branch-specific performance report

**Steps**:
1. Go to `/reports/builder`
2. Name: "Branch Performance Report"
3. Data source: "Loan Accounts"
4. Add fields:
   - Branch Name
   - Total Disbursements
   - Active Loans
   - Collection Rate
5. Group by: Branch
6. Aggregations:
   - SUM(disbursements)
   - COUNT(loans)
7. Visualization: Table
8. Save and generate

---

### Use Case 5: Churn Prediction

**Objective**: Identify customers likely to churn

**Steps**:
1. Go to `/reports/analytics`
2. Select "Customer Churn" model
3. Run predictions on customer list
4. Filter: Churn probability > 70%
5. Export high-risk customers
6. Plan retention campaigns

---

## 🎯 Best Practices

### 1. Report Organization
- Use consistent naming conventions
- Add clear descriptions
- Tag reports with categories
- Share useful reports with team

### 2. Dashboard Design
- Keep KPIs above the fold
- Use appropriate visualizations
- Set reasonable refresh intervals
- Avoid clutter

### 3. Custom Reports
- Start simple, add complexity gradually
- Test with small data sets first
- Document complex calculations
- Save frequently used filters

### 4. Predictive Analytics
- Understand model limitations
- Don't rely solely on predictions
- Combine ML with human judgment
- Monitor model accuracy

---

## 🔧 Tips & Tricks

### Quick Access
- Bookmark frequently used reports
- Set a default dashboard
- Use keyboard shortcuts
- Pin favorite reports

### Performance
- Use date range filters to limit data
- Schedule large reports for off-peak hours
- Download vs view online for big reports
- Clear old generated reports regularly

### Collaboration
- Share custom reports with colleagues
- Comment on dashboard widgets
- Export for presentations
- Schedule regular report distribution

---

## 📱 Mobile Access

Access reports on mobile:
```
http://localhost:3000/reports (mobile-optimized)
```

Features on mobile:
- View dashboards
- Generate reports
- Check scheduled reports
- View predictions

---

## 🆘 Troubleshooting

### Report Generation Fails

**Problem**: Report shows "Failed" status

**Solution**:
1. Check date range is valid
2. Ensure you have data for selected filters
3. Try with simpler parameters
4. Check error message in report history

---

### Dashboard Not Loading

**Problem**: Dashboard widgets show loading spinner

**Solution**:
1. Refresh the page
2. Check your internet connection
3. Verify you have necessary permissions
4. Clear browser cache

---

### Prediction Errors

**Problem**: ML prediction fails

**Solution**:
1. Verify all required features are provided
2. Check feature value ranges
3. Ensure model is deployed
4. Try a different model

---

### Slow Performance

**Problem**: Reports take too long

**Solution**:
1. Reduce date range
2. Add more specific filters
3. Run during off-peak hours
4. Consider scheduling instead of on-demand

---

## 📚 Next Steps

### Learn More
1. **Advanced Features**
   - Custom SQL in report builder
   - Complex dashboard layouts
   - ML model training
   - Report API integration

2. **Automation**
   - Schedule daily/weekly reports
   - Set up email distribution
   - Configure webhooks
   - Batch report generation

3. **Integration**
   - Export to BI tools
   - Embed reports in applications
   - API consumption
   - Mobile app integration

---

## 🎓 Training Resources

### Video Tutorials
- Introduction to Reporting (5 min)
- Custom Report Builder (10 min)
- Dashboard Creation (8 min)
- Predictive Analytics (12 min)

### Documentation
- Full API Reference
- Report Template Guide
- Dashboard Widget Library
- ML Model Documentation

### Support
- Email: support@nbfc.com
- Slack: #reporting-help
- Office Hours: Mon-Fri 9 AM - 6 PM

---

## ✅ Checklist

Before going live, ensure:

- [ ] Generated at least 3 different reports
- [ ] Created one custom report
- [ ] Viewed executive dashboard
- [ ] Made at least one prediction
- [ ] Scheduled one recurring report
- [ ] Shared a report with team member
- [ ] Exported a report to Excel
- [ ] Understood error messages
- [ ] Bookmarked frequently used reports
- [ ] Configured email notifications

---

## 🎉 You're Ready!

Congratulations! You now know how to:
✅ Generate reports from templates  
✅ Build custom reports  
✅ View and create dashboards  
✅ Use predictive analytics  
✅ Schedule automated reports  

Start exploring the 100+ pre-built reports and create your own insights!

---

**Need Help?**  
Contact Support: support@nbfc.com  
Documentation: /docs/reporting  
API Reference: /docs/api/reporting

---

**Last Updated**: July 9, 2026  
**Version**: 1.0.0
