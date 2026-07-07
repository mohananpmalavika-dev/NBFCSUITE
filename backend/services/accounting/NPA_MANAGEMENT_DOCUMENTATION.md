# NPA Management Module - Complete Documentation

## Overview

The NPA (Non-Performing Asset) Management module provides comprehensive functionality for:
- **Auto-classification** of loan assets based on Days Past Due (DPD)
- **Provisioning calculation** as per RBI norms for NBFCs
- **Asset Classification Register** generation
- **Movement Reports** for tracking NPA changes over time
- **Regulatory reporting** (RBI returns, PCR calculations)

## Features

### 1. Auto-Classification (90 DPD Rule)

The system automatically classifies loans into categories based on overdue days:

#### Classification Categories

| Category | DPD Range | Description |
|----------|-----------|-------------|
| **STANDARD** | 0 DPD | Performing assets, no delays |
| **SMA-0** | 1-30 DPD | Special Mention Account - 0 |
| **SMA-1** | 31-60 DPD | Special Mention Account - 1 |
| **SMA-2** | 61-90 DPD | Special Mention Account - 2 |
| **SUBSTANDARD** | 91-365 DPD | NPA for less than 12 months |
| **DOUBTFUL-1** | 366-730 DPD | NPA for 1-2 years |
| **DOUBTFUL-2** | 731-1095 DPD | NPA for 2-3 years |
| **DOUBTFUL-3** | 1096+ DPD | NPA for more than 3 years |
| **LOSS** | Any | Identified as loss by bank/NBFC |

#### RBI Norms
- An asset becomes NPA when it crosses **90 days past due (DPD)**
- SMA categories (0, 1, 2) are **early warning indicators**
- NPA classification requires immediate action and provisioning

### 2. Provisioning Calculation

Provisioning rates as per RBI prudential norms:

#### Standard Assets
- **0.25%** on outstanding principal

#### Special Mention Accounts (SMA)
- **0%** - No provisioning required
- Used for monitoring and early intervention

#### Substandard Assets (91-365 DPD)
- **Secured**: 15% of outstanding
- **Unsecured**: 25% of outstanding

#### Doubtful Assets

**Doubtful-1 (1-2 years NPA)**
- Secured portion: 25%
- Unsecured portion: 100%

**Doubtful-2 (2-3 years NPA)**
- Secured portion: 40%
- Unsecured portion: 100%

**Doubtful-3 (3+ years NPA)**
- 100% on entire outstanding

#### Loss Assets
- **100%** provisioning required
- Typically written off

#### Security Coverage Calculation

For partially secured loans:
```
Secured Portion = min(Security Value / Outstanding, 100%)
Unsecured Portion = 100% - Secured Portion

Total Provisioning = (Secured % × Secured Rate) + (Unsecured % × Unsecured Rate)
```

### 3. Asset Classification Register

Comprehensive register showing:
- All loans classified by NPA category
- Outstanding principal amounts
- Required provisions
- Existing provisions
- Provisioning shortfall/surplus
- Account-level details

#### Register Summary Includes
- Total number of accounts by category
- Total outstanding by category
- Total provisions by category
- NPA ratio (Gross and Net)
- Category-wise distribution

### 4. Movement Reports

Track changes in NPA portfolio over time:

#### Opening Balance
- NPA accounts at start of period
- Outstanding amounts

#### Additions
- **Fresh NPAs**: New accounts crossing 90 DPD
- **Downgrades**: Accounts moving to worse categories
- **Increased Provisioning**: Due to aging

#### Reductions
- **Upgrades**: Accounts becoming performing
- **Recoveries**: Collections reducing NPA
- **Write-offs**: Loss assets removed from books

#### Closing Balance
- NPA accounts at end of period
- Net movement analysis

### 5. Key Metrics & Ratios

#### Gross NPA Ratio
```
Gross NPA Ratio = (Gross NPAs / Gross Advances) × 100
```

#### Net NPA Ratio
```
Net NPA Ratio = ((Gross NPAs - Provisions) / Gross Advances) × 100
```

#### Provisioning Coverage Ratio (PCR)
```
PCR = (Provisions Held / Gross NPAs) × 100
```
- Higher PCR indicates better cushion against losses
- RBI expects PCR of 70%+ for banks/NBFCs

## API Endpoints

### Classification

#### POST `/accounting/npa/classify`
Classify an asset based on DPD
```json
Request:
{
  "days_past_due": 120,
  "is_restructured": false,
  "is_written_off": false
}

Response:
{
  "npa_category": "SUBSTANDARD",
  "days_past_due": 120,
  "is_npa": true,
  "is_sma": false,
  "classification_date": "2026-07-07"
}
```

#### GET `/accounting/npa/classify/loan/{loan_account_id}`
Get classification for specific loan
- Query param: `as_of_date` (optional, defaults to today)

### Provisioning

#### POST `/accounting/npa/provisioning/calculate`
Calculate required provisioning
```json
Request:
{
  "outstanding_principal": 100000.00,
  "npa_category": "DOUBTFUL_1",
  "is_secured": true,
  "security_coverage_ratio": 60.00,
  "existing_provision": 5000.00
}

Response:
{
  "outstanding_principal": 100000.00,
  "provisioning_rate": 55.00,
  "required_provision": 55000.00,
  "existing_provision": 5000.00,
  "additional_provision": 50000.00
}
```

#### POST `/accounting/npa/provisioning/create`
Create provisioning journal entry
```json
Request:
{
  "loan_account_id": 123,
  "provision_amount": 50000.00,
  "npa_category": "DOUBTFUL_1",
  "as_of_date": "2026-07-07",
  "narration": "Monthly provisioning for loan account"
}
```

#### POST `/accounting/npa/provisioning/reverse`
Reverse provisioning (on upgrade/recovery)

#### POST `/accounting/npa/write-off`
Write off a loan
```json
Request:
{
  "loan_account_id": 123,
  "write_off_amount": 100000.00,
  "provision_available": 55000.00,
  "as_of_date": "2026-07-07"
}
```

### Reports

#### POST `/accounting/npa/register`
Generate Asset Classification Register
```json
Request:
{
  "as_of_date": "2026-07-07",
  "category_filter": null  // Optional: filter by specific category
}
```

#### GET `/accounting/npa/summary`
Get NPA summary statistics
- Query param: `as_of_date` (optional)

#### POST `/accounting/npa/movement-report`
Generate NPA movement report
```json
Request:
{
  "from_date": "2026-06-01",
  "to_date": "2026-06-30"
}
```

#### POST `/accounting/npa/vintage-analysis`
Vintage analysis by cohort
```json
Request:
{
  "as_of_date": "2026-07-07",
  "cohort_by": "month"  // month, quarter, or year
}
```

### Regulatory Reports

#### POST `/accounting/npa/reports/rbi-return`
Generate RBI NPA return

#### POST `/accounting/npa/reports/provisioning-coverage-ratio`
Calculate Provisioning Coverage Ratio

### Batch Processing

#### POST `/accounting/npa/batch/monthly-classification`
Run monthly NPA classification for entire portfolio
```json
Request:
{
  "as_of_date": "2026-07-31"
}
```

## Accounting Entries

### Provisioning Entry
```
Dr. Provision Expense (6050)           50,000
    Cr. Provision for Loan Losses (2400)      50,000
```

### Provision Reversal Entry
```
Dr. Provision for Loan Losses (2400)   50,000
    Cr. Provision Reversal Income (4020)      50,000
```

### Write-off Entry (with provision)
```
Dr. Provision for Loan Losses (2400)   55,000
Dr. Bad Debt Expense (6060)            45,000
    Cr. Loan Asset (1100)                    100,000
```

## System Accounts Required

| Account Code | Account Name | Type | Purpose |
|--------------|--------------|------|---------|
| 1100 | Loan Assets | Asset | Loan portfolio |
| 2400 | Provision for Loan Losses | Liability | Provisioning reserve |
| 4020 | Provision Reversal Income | Income | Provision write-back |
| 6050 | Provision Expense | Expense | Provisioning charge |
| 6060 | Bad Debt Expense | Expense | Write-offs |

## Business Rules

### Classification Rules
1. Classification runs automatically on a daily/monthly basis
2. DPD is calculated from last payment due date
3. Restructured loans have special classification rules
4. One-time settlements require board approval

### Provisioning Rules
1. Provisions are calculated at month-end
2. Additional provisions are created if shortfall exists
3. Excess provisions can be reversed (with approval)
4. Write-offs require exhaustion of legal remedies

### Upgrade Rules
1. Account must be "standard" for 12 months continuously
2. All overdues must be cleared
3. Future installments must be regular
4. Requires credit committee approval

### Write-off Rules
1. Only LOSS category can be written off
2. Requires CEO/Board approval
3. Legal process must be completed
4. Recovery efforts continue post write-off

## Integration Points

### With LMS (Loan Management System)
- Fetch loan accounts and overdue status
- Update loan classification status
- Track provision amounts
- Write-off processing

### With Accounting Module
- Auto-create journal entries
- Update general ledger
- Financial reporting integration

### With Collections Module
- Track recovery efforts
- Update on payments
- Trigger upgrades on clearance

## Compliance & Audit

### RBI Compliance
- Classification as per RBI master circular
- Provisioning rates aligned with norms
- Quarterly NPA reporting
- Board review of NPAs

### Audit Trail
- All classifications logged with timestamp
- Provisioning entries traceable
- Write-off approvals documented
- Movement tracked with reasons

### Key Reports for Auditors
1. Asset Classification Register
2. NPA Movement Report
3. Provisioning Coverage Report
4. Vintage Analysis
5. Write-off Register

## Best Practices

### Monthly Process
1. **Day 1-5**: Calculate DPD for all loans
2. **Day 6-10**: Run auto-classification
3. **Day 11-15**: Review classifications
4. **Day 16-20**: Calculate provisions
5. **Day 21-25**: Create provision entries
6. **Day 26-30**: Generate reports
7. **Day 31**: Submit to management/board

### Monitoring
- Weekly SMA monitoring for early intervention
- Daily tracking of slippages from SMA-2 to NPA
- Monthly NPA review meetings
- Quarterly board presentations

### Documentation
- Classification rationale documented
- Write-off decisions with justification
- Recovery efforts recorded
- Provision adequacy reviews

## Performance Optimization

### Database Indexes
```sql
CREATE INDEX idx_loan_dpd ON loan_accounts(days_past_due);
CREATE INDEX idx_loan_status ON loan_accounts(npa_category);
CREATE INDEX idx_provision_date ON journal_entries(entry_date) 
    WHERE entry_type = 'PROVISION';
```

### Batch Processing
- Process loans in batches of 1000
- Use async processing for large portfolios
- Schedule during off-peak hours
- Cache frequently accessed data

## Future Enhancements

1. **AI/ML Integration**
   - Predict future NPAs
   - Early warning system
   - Recovery probability scoring

2. **Advanced Analytics**
   - Heat maps for NPA concentration
   - Segment-wise analysis
   - Geographic distribution

3. **Automated Actions**
   - Auto-trigger collection workflows
   - Escalation based on aging
   - Notification to stakeholders

4. **Integration**
   - Credit bureau reporting
   - Regulatory filing automation
   - Real-time dashboards

## Support & Maintenance

### Regular Updates
- Review classification rules annually
- Update provisioning rates per RBI circulars
- Enhance reporting as per requirements

### Troubleshooting
- Verify DPD calculations
- Check system account mappings
- Validate provisioning rates
- Review journal entry postings

---

## Summary

The NPA Management module provides:
✅ **Automatic 90-DPD classification**
✅ **RBI-compliant provisioning**
✅ **Comprehensive asset register**
✅ **Detailed movement tracking**
✅ **Regulatory reporting**
✅ **Full audit trail**

This ensures regulatory compliance, financial prudence, and effective portfolio management.
