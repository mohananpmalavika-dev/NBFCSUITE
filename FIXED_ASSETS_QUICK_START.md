# Fixed Asset Management - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Access the Module

**URL:** `/accounting/assets`

Navigate to: **Accounting → Fixed Assets**

### 2. Key Features Overview

| Feature | What It Does | URL |
|---------|-------------|-----|
| **Dashboard** | Overview & quick actions | `/accounting/assets` |
| **Asset Register** | View & manage all assets | `/accounting/assets/list` |
| **Depreciation** | Calculate depreciation | `/accounting/assets/depreciation` |
| **Maintenance** | Track maintenance | `/accounting/assets/maintenance` |
| **Transfers** | Manage asset movements | `/accounting/assets/transfers` |
| **Verification** | Physical verification | `/accounting/assets/verification` |

---

## 📝 Common Tasks

### Add a New Asset

1. Go to `/accounting/assets/list`
2. Click **"Add Asset"** button
3. Fill in:
   - Asset Code (auto-generated or manual)
   - Asset Name
   - Category
   - Purchase Cost
   - Acquisition Date
   - Depreciation Method & Rate
   - Location & Custodian
4. Click **Save**

**API:**
```bash
POST /api/v1/fixed-assets/assets
```

### Run Monthly Depreciation

1. Go to `/accounting/assets/depreciation`
2. Select:
   - Financial Year
   - Financial Month
   - Calculation Date
3. Check **"Auto-post Journal Entries"**
4. Click **"Calculate Depreciation"**

**API:**
```bash
POST /api/v1/fixed-assets/depreciation/calculate
```

### Schedule Maintenance

1. Go to `/accounting/assets/maintenance`
2. Click **"Schedule Maintenance"**
3. Fill in:
   - Asset
   - Maintenance Type
   - Scheduled Date
   - Priority
   - Description
4. Click **Save**

**API:**
```bash
POST /api/v1/fixed-assets/maintenance
```

### Transfer an Asset

1. Go to `/accounting/assets/transfers`
2. Click **"Initiate Transfer"**
3. Fill in:
   - Asset
   - From Location/Custodian
   - To Location/Custodian
   - Transfer Date
   - Reason
4. **Workflow:**
   - Initiated → Approve → Mark In Transit → Complete

**API:**
```bash
POST /api/v1/fixed-assets/transfers
```

### Physical Verification

1. Go to `/accounting/assets/verification`
2. Click **"Create Verification Cycle"**
3. Set:
   - Cycle Name
   - Financial Year
   - Date Range
   - Scope (All/Category/Location)
4. Click **"Start Cycle"**
5. Record verifications for each asset

**API:**
```bash
POST /api/v1/fixed-assets/verification/cycles
```

---

## 🎯 Depreciation Methods

### Straight Line (SLM)
```
Annual Depreciation = (Cost - Salvage) / Useful Life
```
- Equal depreciation every year
- Simple and widely used

### Written Down Value (WDV)
```
Annual Depreciation = Opening WDV × Rate%
```
- Higher depreciation initially
- Common for tax purposes in India

### Double Declining Balance
```
Rate = 2 / Useful Life
Annual Depreciation = Opening WDV × Rate
```
- Accelerated depreciation
- Good for rapidly obsolescing assets

---

## 📊 Reports Available

| Report | Description | Endpoint |
|--------|-------------|----------|
| **Asset Register** | Complete asset listing | GET `/assets` |
| **Depreciation Report** | Period-wise depreciation | GET `/depreciation/report/{year}` |
| **Maintenance Report** | Maintenance cost analysis | GET `/maintenance/report/period` |
| **Verification Report** | Cycle results | GET `/verification/cycles/{id}/report` |
| **Asset Summary** | Statistics | GET `/assets/summary/statistics` |

---

## 🔍 Search & Filter

### Asset List Filters

- **Search:** Asset code, name, serial number, barcode
- **Category:** Land, Building, Vehicles, Computers, etc.
- **Status:** Active, Maintenance, Disposed, etc.
- **Location:** By branch/office
- **Date Range:** Acquisition date
- **Cost Range:** Min/max purchase cost

### Maintenance Filters

- **Status:** Pending, Scheduled, In Progress, Completed
- **Type:** Preventive, Corrective, Breakdown
- **Priority:** Low, Medium, High, Critical

### Transfer Filters

- **Status:** Initiated, Approved, In Transit, Completed
- **Date Range:** Transfer date
- **Location:** Source/destination

---

## 📱 Mobile-Friendly Features

### Physical Verification
- ✅ GPS location capture
- ✅ Photo capture
- ✅ Barcode scanning (ready)
- ✅ Offline mode (ready)

---

## 🔐 Security & Permissions

### Multi-Tenant
- Automatic tenant isolation
- Data filtered by tenant context

### Audit Trail
- All operations logged
- Who, what, when tracked
- Soft deletes (recovery possible)

### Approval Workflows
- Transfer approvals
- Maintenance approvals
- Multi-level support

---

## ⚙️ Configuration

### Asset Categories
1. Land
2. Building
3. Plant & Machinery
4. Furniture & Fixtures
5. Vehicles
6. Computer Equipment
7. Office Equipment
8. Leasehold Improvements
9. Intangible Assets
10. Other

### Status Lifecycle
- **Active** → Asset in use
- **In Maintenance** → Under maintenance
- **Under Repair** → Being repaired
- **Idle** → Not in use
- **Transferred** → Being transferred
- **Disposed** → Disposed/sold

### Maintenance Types
- **Preventive** - Scheduled maintenance
- **Corrective** - Fix identified issues
- **Breakdown** - Emergency repair
- **Scheduled** - Regular servicing
- **Inspection** - Safety/compliance check

---

## 💡 Best Practices

### Asset Management
1. ✅ Use consistent naming conventions
2. ✅ Assign unique asset codes
3. ✅ Update location immediately on movement
4. ✅ Attach purchase documents
5. ✅ Tag with barcode/QR codes

### Depreciation
1. ✅ Run depreciation monthly
2. ✅ Review before posting
3. ✅ Check for errors
4. ✅ Verify calculations
5. ✅ Generate reports for audit

### Maintenance
1. ✅ Schedule preventive maintenance
2. ✅ Track costs accurately
3. ✅ Document work performed
4. ✅ Maintain service history
5. ✅ Set up recurring schedules

### Verification
1. ✅ Conduct quarterly verifications
2. ✅ Assign dedicated teams
3. ✅ Use mobile devices
4. ✅ Capture photos
5. ✅ Report discrepancies immediately

---

## 🆘 Troubleshooting

### Issue: Depreciation not calculating
**Solution:** Check that:
- Asset status is "Active"
- Depreciation method is set
- Rate/useful life is defined
- Asset acquired before calculation date

### Issue: Transfer stuck
**Solution:** 
- Check current status
- Ensure proper approvals
- Verify workflow state
- Check user permissions

### Issue: Asset not found in verification
**Solution:**
- Check asset status (active?)
- Verify it's in cycle scope
- Check location filters
- Ensure not already verified

---

## 📞 Quick Reference

### Important URLs
```
Dashboard:     /accounting/assets
Asset List:    /accounting/assets/list
Depreciation:  /accounting/assets/depreciation
Maintenance:   /accounting/assets/maintenance
Transfers:     /accounting/assets/transfers
Verification:  /accounting/assets/verification
```

### API Base URL
```
/api/v1/fixed-assets
```

### Key Endpoints
```
GET    /assets                    - List assets
POST   /assets                    - Create asset
GET    /assets/{id}               - Get asset
PUT    /assets/{id}               - Update asset
DELETE /assets/{id}               - Delete asset
POST   /depreciation/calculate    - Run depreciation
POST   /maintenance               - Create maintenance
POST   /transfers                 - Create transfer
POST   /verification              - Record verification
```

---

## 🎓 Training Materials

### Video Tutorials (Coming Soon)
- [ ] Asset Registration
- [ ] Running Depreciation
- [ ] Scheduling Maintenance
- [ ] Processing Transfers
- [ ] Physical Verification

### Documentation
- ✅ Complete Implementation Guide
- ✅ API Documentation
- ✅ User Manual
- ✅ Quick Start Guide (this document)

---

## ✅ Checklist: First-Time Setup

- [ ] Access the module at `/accounting/assets`
- [ ] Review the dashboard
- [ ] Add first asset
- [ ] Configure depreciation settings
- [ ] Schedule first maintenance
- [ ] Create verification cycle
- [ ] Test search and filters
- [ ] Generate a report
- [ ] Review audit trail

---

## 🚀 Ready to Go!

You're all set to start managing your fixed assets. For detailed information, refer to:

- 📖 `FIXED_ASSETS_IMPLEMENTATION_COMPLETE.md` - Technical details
- 📋 `FIXED_ASSETS_COMPLETE_SUMMARY.md` - Comprehensive overview
- 🔧 API Documentation at `/docs`

**Happy Asset Managing!** 🎉
