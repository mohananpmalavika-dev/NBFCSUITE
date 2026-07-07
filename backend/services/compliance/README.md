# CRILC & SMA Compliance Reporting Module

## Overview

Complete implementation of CRILC (Central Repository of Information on Large Credits) and SMA (Special Mention Account) reporting as per RBI guidelines for NBFCs.

## Features Implemented

### 1. **CRILC - Large Credit Identification**

#### Borrower Management
- **Large Credit Threshold**: Automatic identification of borrowers with aggregate exposure ≥ ₹5 Crore
- **Borrower Types**: Individual, Partnership, Private/Public Limited, Trust, Society, HUF, etc.
- **Comprehensive Details**:
  - PAN, CIN, GSTIN tracking
  - Industry classification (NIC codes)
  - Financial metrics (turnover, net worth)
  - Group exposure tracking
  - Internal/external credit ratings

#### Facility Management
- **Facility Types**: Term Loan, Cash Credit, Overdraft, Working Capital, Bank Guarantee, LC
- **Exposure Classification**:
  - Funded exposure
  - Non-funded exposure
- **Tracking**:
  - Sanctioned vs outstanding amounts
  - Security/collateral details
  - DPD (Days Past Due)
  - Asset classification

#### Large Credit Identification
- Automated threshold monitoring (configurable, default ₹5 Crore)
- Group exposure aggregation
- Real-time status updates
- Historical tracking

### 2. **SMA (Special Mention Account) Classification**

#### RBI-Compliant Classification
- **Standard**: 0 DPD
- **SMA-0**: 1-30 days overdue
- **SMA-1**: 31-60 days overdue
- **SMA-2**: 61-90 days overdue
- **NPA**: >90 days overdue

#### Real-time SMA Tracking
- Automated DPD calculation
- Daily/on-demand status updates
- Outstanding & overdue breakdown:
  - Principal outstanding/overdue
  - Interest outstanding/overdue
- Status change history with audit trail

#### Asset Classification & Provisioning
- **Standard**: 0.40% provision
- **Sub-Standard** (>90 days): 15% provision
- **Doubtful-1** (1-2 years): 25% provision
- **Doubtful-2** (2-3 years): 40% provision
- **Doubtful-3** (>3 years): 100% provision
- **Loss**: 100% provision

### 3. **Quarterly Return Generation**

#### CRILC Quarterly Returns
- Large borrower list with complete details
- SMA-wise classification (SMA-0, SMA-1, SMA-2, NPA)
- Funded vs non-funded exposure breakdown
- Industry and geographic distribution
- Approval workflow (Draft → Review → Approved → Submitted)
- Data snapshot for audit trail

#### SMA Quarterly Reports
- Account count and amount by SMA category
- Movement tracking:
  - New additions
  - Regularizations
  - Upgradations/degradations
  - Slippages to NPA
- Sectoral and geographic analysis
- Trend analysis support

### 4. **Compliance Alerts**

- **Alert Types**:
  - SMA status change
  - Large credit threshold breach
  - Overdue breach
  - NPA risk
- **Severity Levels**: Low, Medium, High, Critical
- **Alert Management**:
  - Acknowledgment workflow
  - Resolution tracking
  - Due date monitoring
  - Overdue flagging

## API Endpoints

### CRILC Borrowers
```
POST   /api/v1/compliance/crilc/borrowers              # Create borrower
GET    /api/v1/compliance/crilc/borrowers/{id}        # Get borrower
PUT    /api/v1/compliance/crilc/borrowers/{id}        # Update borrower
GET    /api/v1/compliance/crilc/borrowers             # List borrowers
```

### CRILC Facilities
```
POST   /api/v1/compliance/crilc/facilities             # Add facility
PUT    /api/v1/compliance/crilc/facilities/{id}       # Update facility
GET    /api/v1/compliance/crilc/borrowers/{id}/facilities  # Get borrower facilities
```

### Large Credit Identification
```
POST   /api/v1/compliance/crilc/identify-large-credits  # Identify large credits
```

### CRILC Quarterly Returns
```
POST   /api/v1/compliance/crilc/quarterly-returns      # Generate return
GET    /api/v1/compliance/crilc/quarterly-returns/{id} # Get return
GET    /api/v1/compliance/crilc/quarterly-returns      # List returns
POST   /api/v1/compliance/crilc/quarterly-returns/{id}/approve  # Approve
POST   /api/v1/compliance/crilc/quarterly-returns/{id}/submit   # Submit
```

### SMA Tracking
```
POST   /api/v1/compliance/sma/calculate                # Calculate SMA status
GET    /api/v1/compliance/sma/tracking/{id}           # Get tracking record
GET    /api/v1/compliance/sma/tracking                # List tracking
GET    /api/v1/compliance/sma/loan/{id}/history       # Get loan SMA history
GET    /api/v1/compliance/sma/status-changes          # Get status change history
GET    /api/v1/compliance/sma/dashboard               # Get dashboard stats
```

### SMA Quarterly Reports
```
POST   /api/v1/compliance/sma/quarterly-reports        # Generate report
```

### Compliance Alerts
```
GET    /api/v1/compliance/alerts                      # List alerts
POST   /api/v1/compliance/alerts/{id}/acknowledge     # Acknowledge alert
POST   /api/v1/compliance/alerts/{id}/resolve         # Resolve alert
```

## Usage Examples

### 1. Identify Large Credits

```python
POST /api/v1/compliance/crilc/identify-large-credits
{
  "threshold_amount": 50000000,  // ₹5 Crore
  "as_on_date": "2024-03-31",
  "include_group_exposure": true
}

Response:
{
  "threshold_amount": 50000000,
  "as_on_date": "2024-03-31",
  "total_large_credits": 145,
  "newly_identified": 12,
  "removed_from_list": 3,
  "identified_borrowers": [...]
}
```

### 2. Calculate SMA Status

```python
POST /api/v1/compliance/sma/calculate
{
  "as_on_date": "2024-03-31",
  "loan_account_ids": null,  // null = all accounts
  "calculate_provisions": true
}

Response:
{
  "as_on_date": "2024-03-31",
  "accounts_processed": 1250,
  "status_changes": 45,
  "alerts_created": 23,
  "results": [
    {
      "loan_account_number": "LN2024001234",
      "borrower_name": "ABC Industries Pvt Ltd",
      "sma_status": "sma_1",
      "dpd": 45,
      "total_outstanding": 75000000,
      "total_overdue": 5000000,
      "provision_required": 11250000
    }
  ]
}
```

### 3. Generate CRILC Quarterly Return

```python
POST /api/v1/compliance/crilc/quarterly-returns
{
  "reporting_quarter": "Q4FY24",
  "reporting_year": "FY2023-24",
  "as_on_date": "2024-03-31",
  "remarks": "Q4 FY24 CRILC Return"
}

Response:
{
  "id": "uuid",
  "return_number": "CRILCQ4FY24001",
  "reporting_quarter": "Q4FY24",
  "status": "draft",
  "total_large_borrowers": 145,
  "total_exposure": 9850000000,
  "sma_0_count": 5,
  "sma_0_amount": 125000000,
  "sma_1_count": 3,
  "sma_1_amount": 85000000,
  "sma_2_count": 2,
  "sma_2_amount": 60000000,
  "npa_count": 1,
  "npa_amount": 35000000
}
```

### 4. Get SMA Dashboard

```python
GET /api/v1/compliance/sma/dashboard?as_on_date=2024-03-31

Response:
{
  "total_accounts": 1250,
  "standard_count": 1195,
  "standard_amount": 15750000000,
  "sma_0_count": 25,
  "sma_0_amount": 450000000,
  "sma_1_count": 18,
  "sma_1_amount": 325000000,
  "sma_2_count": 10,
  "sma_2_amount": 180000000,
  "npa_count": 2,
  "npa_amount": 45000000,
  "total_exposure": 16750000000,
  "provision_required": 125000000,
  "alerts_open": 15
}
```

## RBI Guidelines Compliance

### CRILC Reporting
- ✅ Quarterly reporting for aggregate exposure ≥ ₹5 Crore
- ✅ Borrower identification (PAN, CIN, GSTIN)
- ✅ Facility-wise details
- ✅ Funded and non-funded exposure segregation
- ✅ SMA classification
- ✅ Suit filed accounts tracking

### SMA Classification
- ✅ SMA-0: 1-30 DPD
- ✅ SMA-1: 31-60 DPD
- ✅ SMA-2: 61-90 DPD
- ✅ Daily monitoring requirement
- ✅ Status change reporting
- ✅ Quarterly movement tracking

### Provisioning Norms
- ✅ Standard assets: 0.40%
- ✅ Sub-standard: 15%
- ✅ Doubtful-1: 25%
- ✅ Doubtful-2: 40%
- ✅ Doubtful-3/Loss: 100%

## Database Schema

### Core Tables
1. **crilc_borrowers** - Large credit borrower master
2. **crilc_facilities** - Facility-wise exposure details
3. **sma_tracking** - Real-time SMA status tracking
4. **sma_status_history** - Historical status changes
5. **crilc_quarterly_returns** - CRILC quarterly submissions
6. **sma_quarterly_reports** - SMA quarterly reports
7. **compliance_alerts** - Compliance alert management

## Migration

```bash
# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Scheduled Jobs

Recommended cron jobs:

```bash
# Daily SMA calculation (2 AM)
0 2 * * * python -m backend.jobs.calculate_daily_sma

# Update overdue alerts (6 AM)
0 6 * * * python -m backend.jobs.update_compliance_alerts

# Monthly large credit identification (1st of month, 3 AM)
0 3 1 * * python -m backend.jobs.identify_large_credits
```

## Security & Permissions

Required permissions:
- `compliance.read` - View compliance data
- `compliance.write` - Create/update compliance data
- `compliance.approve` - Approve quarterly returns
- `compliance.submit` - Submit returns to RBI

## Audit Trail

All operations tracked:
- Created by/at
- Updated by/at
- Status change history
- Data snapshots for quarterly returns

## Integration Points

1. **Loan Management**: Automatic borrower/facility sync
2. **Customer Management**: PAN, GSTIN validation
3. **Accounting**: Provision calculations
4. **Notifications**: Alert distribution
5. **Reports**: Export to Excel/CSV/PDF

## Future Enhancements

1. Direct integration with RBI CRILC portal
2. Automated email notifications to RBI
3. Predictive analytics for SMA slippage
4. Early warning system for large credit stress
5. Mobile dashboard for real-time monitoring

## Support

For issues or questions, contact the Compliance Team.

## Version History

- **v1.0.0** (2024-01-20): Initial implementation
  - CRILC large credit identification
  - SMA classification and tracking
  - Quarterly return generation
  - Compliance alerts
