# Locker Compliance Module - Quick Reference Guide

## 🎯 Quick Access

**Module Location**: Admin Portal → Lockers → Compliance  
**Auto-Refresh**: 60 seconds  
**User Roles**: Branch Manager, Compliance Officer, Auditor

---

## 📊 Dashboard Overview

### Key Metrics (4 KPI Cards)
1. **Overall Compliance Score** - Percentage compliance across all areas
2. **Pending Audits** - Number of audits scheduled
3. **Open Issues** - Number of unresolved compliance issues (+ critical count)
4. **Upcoming Inspections** - Inspections scheduled in next 30 days

---

## 🔍 RBI Compliance Areas (6 Areas)

| Area | Description |
|------|-------------|
| **RBI Guidelines** | Adherence to master directions |
| **Fair Allocation** | Transparent allocation process |
| **Rent Transparency** | Clear rent structure |
| **Customer Education** | Terms explained to customers |
| **Complaint Redressal** | Complaint mechanism |
| **Agreement Format** | RBI-compliant format |

---

## 📋 Audit Types (5 Types)

1. **Internal Audit** - Regular internal review
2. **Concurrent Audit** - Ongoing concurrent review
3. **Statutory Audit** - Annual statutory requirement
4. **RBI Inspection** - RBI regulatory inspection
5. **Special Audit** - Ad-hoc special purpose audit

### Audit Statuses
- 🔵 Scheduled
- 🟡 In Progress
- 🟢 Completed
- 🟠 Report Pending
- ⚫ Closed

---

## 🔎 Inspection Types (6 Types)

1. **Access Log Verification** - Verify locker access records
2. **Rent Collection Verification** - Verify rent collection
3. **Physical Verification** - Physical check of lockers
4. **Agreement Verification** - Check agreement compliance
5. **Insurance Verification** - Verify insurance coverage
6. **Maintenance Verification** - Check maintenance records

---

## ⚠️ Issue Severity Levels (4 Levels)

| Severity | Color | Description | Target Resolution |
|----------|-------|-------------|-------------------|
| **Critical** | 🔴 Red | Immediate action required | 7 days |
| **High** | 🟠 Orange | Urgent attention needed | 15 days |
| **Medium** | 🟡 Yellow | Should be addressed | 30 days |
| **Low** | 🔵 Blue | Minor issue | 60 days |

---

## 🚀 Common Actions

### Perform Compliance Check
1. Click **"Check Compliance"**
2. Select branch
3. Choose areas (optional - leave empty for all)
4. Click **"Check Compliance"**

### Schedule an Audit
1. Click **"Schedule Audit"**
2. Select audit type
3. Choose branch
4. Set date
5. Enter auditor name
6. Define scope
7. Click **"Schedule Audit"**

### Conduct Inspection
1. Click **"Conduct Inspection"**
2. Select inspection type
3. Choose branch
4. Enter inspector name
5. Add findings and recommendations
6. Click **"Submit Inspection"**

### Record Compliance Issue
1. Click **"Record Issue"** (from any tab)
2. Select compliance type
3. Choose branch
4. Set severity
5. Enter description
6. Add remediation plan
7. Set target date
8. Click **"Record Issue"**

---

## 📊 Tab Navigation

| Tab | Purpose | Key Features |
|-----|---------|--------------|
| **Dashboard** | Overview | KPIs, compliance areas status |
| **Compliance** | RBI Checks | Checklist, scores, details |
| **Audits** | Audit Management | Schedule, track, reports |
| **Inspections** | Verification | Conduct, track findings |
| **Issues** | Issue Tracking | Record, monitor, resolve |
| **Statistics** | Analytics | Trends, breakdowns, charts |

---

## 🎨 Status Badge Colors

### Compliance Status
- 🟢 **Green** - Compliant
- 🔴 **Red** - Non-Compliant
- 🟡 **Yellow** - Partially Compliant
- 🔵 **Blue** - Under Review
- 🟠 **Orange** - Remediation in Progress

### Issue Status
- 🔵 **Blue** - Open
- 🟡 **Yellow** - In Progress
- 🟢 **Green** - Resolved

---

## 📱 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + C` | Check Compliance |
| `Ctrl + A` | Schedule Audit |
| `Ctrl + I` | Conduct Inspection |
| `Ctrl + R` | Record Issue |
| `Tab` | Navigate tabs |
| `Esc` | Close dialog |

---

## 🔔 Important Reminders

### Monthly Tasks
- ✅ Perform comprehensive compliance check
- ✅ Review open compliance issues
- ✅ Verify rent collection
- ✅ Check access logs

### Quarterly Tasks
- ✅ Conduct physical verification
- ✅ Schedule internal audit
- ✅ Review and update compliance checklist
- ✅ Analyze compliance trends

### Annual Tasks
- ✅ Schedule statutory audit
- ✅ Prepare for RBI inspection
- ✅ Review all compliance policies
- ✅ Update documentation

---

## 📞 Quick Support

### Common Issues

**Q: Dashboard not loading?**  
A: Check internet connection, refresh page (F5)

**Q: Can't schedule audit?**  
A: Verify you have `locker.audit.schedule` permission

**Q: Issue not appearing in list?**  
A: Check branch filter, ensure correct tab selected

**Q: Statistics showing zero?**  
A: Verify date range, check if data exists for period

---

## 📈 Compliance Score Calculation

```
Overall Score = Average of all compliance area scores

Area Score = (Compliant Items / Total Items) × 100

Example:
- RBI Guidelines: 100%
- Fair Allocation: 95%
- Rent Transparency: 85%
- Customer Education: 90%
- Complaint Redressal: 92%
- Agreement Format: 60%

Overall Score = (100 + 95 + 85 + 90 + 92 + 60) / 6 = 87%
```

---

## ✅ Best Practices Checklist

### Daily
- [ ] Monitor critical issues
- [ ] Review new compliance alerts
- [ ] Check pending action items

### Weekly  
- [ ] Review open issues
- [ ] Update issue progress
- [ ] Check upcoming audits/inspections

### Monthly
- [ ] Perform compliance check
- [ ] Conduct scheduled inspections
- [ ] Review compliance trends
- [ ] Close resolved issues

---

## 🔗 Related Modules

- **Locker Master** - Locker inventory management
- **Locker Allocation** - Customer allocation
- **Locker Maintenance** - Maintenance tracking
- **Safety & Security** - Security monitoring

---

## 📄 Document Templates

### Audit Checklist Template
```
□ Documentation Review
  □ Agreement format compliance
  □ KYC verification status
  □ Rent receipt maintenance
  
□ Physical Security
  □ Vault condition
  □ Key management system
  □ CCTV functionality
  
□ Process Compliance
  □ Allocation process
  □ Rent collection process
  □ Customer communication
```

### Inspection Report Template
```
Inspection Type: [Type]
Date: [Date]
Inspector: [Name]
Branch: [Branch]

Items Checked: [Count]
Issues Found: [Count]
Discrepancies: [List]

Recommendations:
1. [Recommendation 1]
2. [Recommendation 2]

Follow-up Required: [Yes/No]
```

---

**Version**: 1.0.0  
**Last Updated**: July 15, 2026  
**Print Friendly**: Yes  
**Page Count**: 4

