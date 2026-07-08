# Attendance & Leave Management - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### 1. Run Database Migration
```bash
# Execute migration script
psql -U postgres -d nbfc_suite < database/migrations/add_attendance_leave_tables_migration.sql
```

### 2. Start Backend Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 3. Start Frontend Server
```bash
cd frontend/apps/admin-portal
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Attendance Dashboard: http://localhost:3000/attendance/dashboard
- Leave Management: http://localhost:3000/leave

---

## 📱 Common User Tasks

### Mark Attendance (Check-In)
1. Go to Attendance Dashboard
2. Click **"Check In"** button
3. Allow location permissions
4. Attendance marked with GPS location

### Apply for Leave
1. Go to Leave menu → **Apply Leave**
2. Select leave type
3. Choose dates (start & end)
4. Enter reason
5. Click **Submit Application**

### Approve Leave (Manager/HR)
1. Go to Leave menu
2. Filter by "Pending" status
3. Click **Approve** on application
4. Confirm approval

### View Leave Balance
1. Go to Leave menu → **View Balance**
2. See all leave types and balances
3. Check available, used, pending days

### Create Shift
1. Go to Attendance → **Shifts**
2. Click **Create Shift**
3. Enter details (name, timing, grace period)
4. Select week-off days
5. Save shift

---

## 🔧 API Quick Reference

### Base URL
```
http://localhost:8000/api
```

### Authentication
```bash
# Add Authorization header
Authorization: Bearer <token>
```

### Common Endpoints

#### Check-In
```bash
POST /attendance/check-in
{
  "latitude": 12.9716,
  "longitude": 77.5946,
  "device_info": "Mozilla/5.0..."
}
```

#### Check-Out
```bash
POST /attendance/check-out
{
  "latitude": 12.9716,
  "longitude": 77.5946,
  "device_info": "Mozilla/5.0..."
}
```

#### Apply Leave
```bash
POST /leave/applications
{
  "leave_type_id": 1,
  "start_date": "2026-07-15",
  "end_date": "2026-07-17",
  "is_half_day": false,
  "reason": "Family function",
  "contact_details": "+91-9876543210"
}
```

#### Approve Leave
```bash
POST /leave/applications/{id}/approve
{
  "remarks": "Approved"
}
```

#### Get Attendance Stats
```bash
GET /attendance/stats?date=2026-07-08
```

---

## 📊 Dashboard Overview

### Attendance Dashboard
- **Statistics Cards:** Total, Present, Absent, On Leave
- **Today's Attendance:** List with filters
- **Quick Actions:** Check-in, Check-out buttons
- **Filters:** Date, Status, Employee search

### Leave Balance
- **Summary Cards:** Total, Available, Used, Pending
- **Balance by Type:** Detailed breakdown per leave type
- **Year Selector:** View previous years

### Shift Management
- **Shift List:** All configured shifts
- **Create/Edit:** Modal form
- **Filters:** Type, Status, Search
- **Actions:** Edit, Delete, Assign

---

## 🎯 Key Features

### Attendance
✅ Biometric integration  
✅ Mobile check-in/out with GPS  
✅ Auto-calculate hours & overtime  
✅ Late arrival detection  
✅ Attendance regularization  
✅ Real-time dashboard  

### Leave Management
✅ Multiple leave types  
✅ Leave accrual (monthly/yearly)  
✅ Multi-level approval workflow  
✅ Balance tracking  
✅ Carry-forward & lapse  
✅ Leave encashment  

### Shift Management
✅ 4 shift types (Regular, Night, Rotational, Flexible)  
✅ Configurable timings  
✅ Grace period setup  
✅ Week-off configuration  
✅ Employee assignment  

---

## 🔐 Default Configuration

### Shift Settings
- Grace Period: 15 minutes
- Full Day Hours: 8 hours
- Half Day Hours: 4 hours
- Week Offs: Saturday & Sunday

### Leave Settings
- Leave Year: January to December
- Accrual Frequency: Monthly
- Carry Forward: As per policy
- Approval Levels: Manager → HR

### Attendance Settings
- Check-in Time: As per shift
- Late Marking: After grace period
- Overtime: After full day hours
- Regularization: Within 7 days

---

## 📝 Sample Data

### Create Sample Shift
```json
{
  "shift_name": "Morning Shift",
  "shift_code": "SHIFT-001",
  "shift_type": "REGULAR",
  "start_time": "09:00",
  "end_time": "18:00",
  "grace_period_minutes": 15,
  "half_day_hours": 4.0,
  "full_day_hours": 8.0,
  "week_off_days": [0, 6],
  "is_active": true
}
```

### Create Sample Leave Type
```json
{
  "leave_type_name": "Casual Leave",
  "leave_type_code": "CL",
  "max_days_per_year": 12,
  "is_carry_forward_allowed": true,
  "max_carry_forward_days": 5,
  "accrual_frequency": "MONTHLY",
  "is_active": true
}
```

### Initialize Leave Balance
```json
{
  "employee_id": 123,
  "leave_type_id": 1,
  "year": 2026,
  "opening_balance": 12.0
}
```

---

## 🐛 Quick Troubleshooting

### Check-in not working?
- Enable location permissions
- Check if shift is assigned
- Verify employee is active

### Leave application fails?
- Check leave balance
- Verify dates are valid
- Ensure reason is provided

### Balance not showing?
- Initialize balance for employee
- Check leave type is active
- Verify year selection

### Shift assignment issue?
- Ensure shift is active
- Check effective dates
- Verify employee exists

---

## 📞 Need Help?

### Documentation
- Full Documentation: `ATTENDANCE_MODULE_COMPLETE.md`
- API Reference: http://localhost:8000/docs

### Common URLs
- Dashboard: `/attendance/dashboard`
- Shifts: `/attendance/shifts`
- Leave List: `/leave`
- Apply Leave: `/leave/apply`
- Balance: `/leave/balance`

---

## ✅ Pre-Flight Checklist

Before going live:
- [ ] Database migration completed
- [ ] Sample shifts created
- [ ] Leave types configured
- [ ] Employee shifts assigned
- [ ] Leave balances initialized
- [ ] Test check-in/check-out
- [ ] Test leave application flow
- [ ] Test approval workflow
- [ ] Verify statistics
- [ ] Train users

---

**Quick Start Version:** 1.0  
**Last Updated:** July 8, 2026  
**Status:** Ready to Use
