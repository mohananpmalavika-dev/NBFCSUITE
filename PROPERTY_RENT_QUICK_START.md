# Property & Rent Management - Quick Start Guide 🚀

## 📋 Quick Access

### Frontend URLs
```
Dashboard:         /property-management
Properties:        /property-management/properties
Leases:           /property-management/leases
Rent Collection:  /property-management/rent
Utilities:        /property-management/utilities
Spaces:           /property-management/spaces
Maintenance:      /property-management/maintenance
```

### API Base Paths
```
Properties:   /api/v1/properties
Leases:       /api/v1/leases
Rent:         /api/v1/rent-payments
Utilities:    /api/v1/utility-bills
Spaces:       /api/v1/property-spaces
Maintenance:  /api/v1/property-maintenance
```

---

## 🎯 Common Workflows

### 1. Add a New Property
```
1. Navigate to: /property-management/properties
2. Click "Add Property" button
3. Fill property details:
   - Property code (unique)
   - Property name
   - Type (office/residential/commercial)
   - Location details
   - Area specifications
   - Ownership details
   - Utility connections
4. Submit to create
```

### 2. Create a Lease Agreement
```
1. Navigate to: /property-management/leases
2. Click "New Lease" button
3. Select property
4. Enter tenant details
5. Set lease period and rent amount
6. Configure payment terms
7. Allocate spaces (from available spaces)
8. Set security deposit
9. Submit to create lease
```

### 3. Record Rent Payment
```
1. Navigate to: /property-management/rent
2. Click "Record Payment" button
3. Select lease
4. Enter payment month
5. Enter paid amount
6. Select payment mode
7. Add payment reference
8. System calculates outstanding automatically
9. Submit to record
```

### 4. Add Utility Bill
```
1. Navigate to: /property-management/utilities
2. Click "Add Bill" button
3. Select property
4. Choose utility type (electricity/water/gas)
5. Enter meter readings (if applicable)
6. Enter bill amount
7. Optionally allocate to tenant
8. Submit to create
```

### 5. Create Space/Unit
```
1. Navigate to: /property-management/spaces
2. Click "Add Space" button
3. Select parent property
4. Enter space details (code, name, type)
5. Set floor and unit number
6. Enter area and rent
7. Mark furnishing status
8. Submit to create
```

### 6. Raise Maintenance Request
```
1. Navigate to: /property-management/maintenance
2. Click "New Request" button
3. Select property
4. Choose maintenance type
5. Set priority (low/medium/high/urgent)
6. Describe issue
7. Add vendor details (optional)
8. Set estimated cost
9. Submit to create ticket
```

---

## 🔍 Quick Search & Filters

### Properties
- **Search**: Property code, name, address
- **Filters**: Type, Status, Occupancy, City, Ownership

### Leases
- **Search**: Lease number, tenant name
- **Filters**: Status, Property, Lease type

### Rent Payments
- **Filters**: Lease, Payment status, Month

### Utilities
- **Filters**: Property, Utility type, Payment status

### Spaces
- **Filters**: Property, Status, Space type

### Maintenance
- **Filters**: Property, Status, Priority, Type

---

## 📊 Key Statistics (Dashboard)

### Available Metrics
- Total Properties
- Active Leases
- Monthly Revenue (Expected)
- Occupancy Rate
- Current Month Collection
- Overdue Payments
- Open Maintenance Requests
- Urgent Tickets

---

## 🎨 Status Colors Reference

### Property Status
- 🟢 **Active** - Green
- ⚫ **Inactive** - Gray
- 🟡 **Under Maintenance** - Yellow
- 🔵 **Under Construction** - Blue
- 🔴 **Sold** - Red

### Lease Status
- ⚫ **Draft** - Gray
- 🟢 **Active** - Green
- 🟡 **Expired** - Yellow
- 🔴 **Terminated** - Red
- 🔵 **Renewed** - Blue

### Payment Status
- 🟡 **Pending** - Yellow
- 🟠 **Partial** - Orange
- 🟢 **Paid** - Green
- 🔴 **Overdue** - Red

### Space Status
- 🟢 **Available** - Green
- 🔵 **Occupied** - Blue
- 🟡 **Reserved** - Yellow
- 🔴 **Under Maintenance** - Red

### Maintenance Priority
- ⚫ **Low** - Gray
- 🔵 **Medium** - Blue
- 🟠 **High** - Orange
- 🔴 **Urgent** - Red (with alert icon)

---

## 🔐 User Permissions

### Required Roles
- **Property Manager**: Full access to all features
- **Accountant**: Rent collection, utility bills
- **Maintenance Staff**: Maintenance requests only
- **Admin**: Full system access

---

## 💡 Best Practices

### Property Management
1. Use consistent naming conventions for property codes
2. Keep utility connection details updated
3. Regularly update property valuations
4. Maintain comprehensive photo documentation

### Lease Management
1. Always verify tenant identity documents
2. Set realistic lock-in periods
3. Configure rent escalation at lease start
4. Document all special terms and conditions
5. Send lease expiry reminders 60 days in advance

### Rent Collection
1. Record payments on the same day
2. Always provide payment receipts
3. Follow up on overdue payments within 7 days
4. Apply late fees consistently per policy
5. Deduct TDS as per regulations

### Utility Management
1. Record meter readings monthly
2. Verify bills against consumption patterns
3. Allocate costs to tenants transparently
4. Pay utility bills before due date
5. Track consumption trends

### Space Allocation
1. Keep space status updated in real-time
2. Document all amenities per space
3. Regular inspections for maintenance needs
4. Maintain floor plans and layouts
5. Track furnishing inventory

### Maintenance Tracking
1. Prioritize urgent requests immediately
2. Assign qualified vendors
3. Get cost estimates before work begins
4. Document with before/after photos
5. Collect tenant feedback on completion

---

## 🆘 Troubleshooting

### Cannot Create Lease
- ✅ Check if property exists
- ✅ Verify spaces are available
- ✅ Ensure no overlapping leases
- ✅ Check user permissions

### Payment Not Reflecting
- ✅ Verify payment date is correct
- ✅ Check lease is active
- ✅ Ensure payment month format (YYYY-MM)
- ✅ Refresh the page

### Space Not Showing as Available
- ✅ Check if linked to active lease
- ✅ Verify status is not "Under Maintenance"
- ✅ Ensure space is not deleted

### Statistics Not Updating
- ✅ Refresh the dashboard page
- ✅ Check if data is synced
- ✅ Verify tenant_id permissions
- ✅ Clear browser cache

---

## 📱 Mobile Access

All pages are fully responsive and work on:
- ✅ Desktop (1920px+)
- ✅ Laptop (1366px+)
- ✅ Tablet (768px+)
- ✅ Mobile (375px+)

---

## 🔗 Integration with Other Modules

### Accounting Module
- Rent payments create accounting entries
- TDS deductions tracked for compliance
- Utility costs allocated to expense accounts

### Customer Module
- Tenants linked to customer records
- Customer 360 view includes lease history

### HRMS Module
- Employee leases tracked separately
- Employee ID linked to lease records

---

## 📞 Support

For issues or questions:
1. Check this quick start guide
2. Review API documentation at `/docs`
3. Contact system administrator
4. Raise support ticket

---

## 🚀 Pro Tips

1. **Bulk Operations**: Use filters to work with multiple records
2. **Export Data**: Use browser print or PDF export for reports
3. **Search Shortcuts**: Use property code for fastest search
4. **Dashboard Widgets**: Bookmark dashboard for quick metrics
5. **Keyboard Navigation**: Use Tab for form navigation
6. **Status Filters**: Combine multiple filters for precise results
7. **Date Ranges**: Filter payments by month for accurate reports

---

**Module**: Property & Rent Management  
**Version**: 1.0.0  
**Last Updated**: July 11, 2026  
**Status**: ✅ Production Ready
