# ALM (Asset Liability Management) Module

## Overview

The ALM module provides comprehensive Asset Liability Management capabilities for NBFCs, including:

- **Maturity Ladder Analysis** - Track assets and liabilities across time buckets
- **Gap Analysis** - Liquidity, interest rate, and maturity gap tracking
- **Liquidity Ratios** - Key metrics including LCR, NSFR, and regulatory ratios
- **Interest Rate Risk** - Scenario analysis and stress testing
- **Quarterly Returns** - Regulatory reporting (SLS, IRS statements)

## Features

### 1. Maturity Ladder

Track assets and liabilities across 12 maturity buckets:

**Time Buckets:**
- Up to 1 day
- Up to 7 days
- Up to 14 days
- Up to 1 month
- Up to 2 months
- Up to 3 months
- Up to 6 months
- Up to 1 year
- Up to 2 years
- Up to 3 years
- Up to 5 years
- Above 5 years

**Asset Categories:**
- Cash and bank balances
- Investments
- Loans and advances
- Fixed assets
- Other assets

**Liability Categories:**
- Deposits
- Borrowings
- Debt securities
- Other liabilities

**Gap Metrics:**
- Gap amount (Assets - Liabilities)
- Cumulative gap
- Gap percentage
- Interest rate sensitive gap
- Duration gap

### 2. Gap Analysis

Four types of gap analysis:

1. **Liquidity Gap** - Ability to meet short-term obligations
2. **Interest Rate Gap** - Exposure to interest rate changes
3. **Maturity Gap** - Mismatch between asset and liability maturities
4. **Duration Gap** - Weighted average time to cash flows

**Components:**
- Contractual inflows/outflows
- Behavioral inflows/outflows
- Gap ratios
- Risk assessment
- Limit monitoring
- Mitigation strategies

### 3. Liquidity Ratios

**Basic Ratios:**
- Current Ratio
- Quick Ratio
- Cash Ratio

**Regulatory Ratios:**
- Liquidity Coverage Ratio (LCR)
- Net Stable Funding Ratio (NSFR)
- Statutory Liquidity Ratio (SLR)

**NBFC-Specific Ratios:**
- Liquid assets to total assets
- Liquid assets to deposits
- Liquid assets to short-term liabilities
- Loan to deposit ratio
- Deposit concentration ratio
- Large deposits ratio

**Funding Stability:**
- Stable funding ratio
- Core deposit ratio
- Volatile liability ratio
- Liquidity stress index
- Funding gap ratio

### 4. Interest Rate Risk

**Scenario Analysis:**
- Base scenario
- Parallel shift up 100 bps
- Parallel shift down 100 bps
- Parallel shift up 200 bps
- Parallel shift down 200 bps
- Yield curve steepening
- Yield curve flattening

**Risk Metrics:**
- Net interest income impact
- Market value of equity impact
- Modified duration (assets & liabilities)
- Duration gap
- Repricing gap (1M, 3M, 6M, 1Y)
- Rate sensitive assets/liabilities
- Earnings at Risk (EaR)
- Value at Risk (VaR)

**Risk Management:**
- Risk level assessment
- Limit breach detection
- Hedging requirements
- Hedge effectiveness tracking

### 5. Quarterly Returns

**Components:**
- Structural Liquidity Statement (SLS)
- Interest Rate Sensitivity (IRS) statement
- Behavioral pattern analysis
- Summary metrics
- Key ratios
- Interest rate shock impact

**Workflow:**
1. Prepare return
2. Review return
3. Approve return
4. File with regulator

**Compliance Tracking:**
- Compliance status
- Issue identification
- Filing status
- Filing reference

### 6. ALM Limits

**Limit Types:**
- Liquidity ratios
- Gap limits
- Duration limits
- Concentration limits

**Features:**
- Minimum/maximum values
- Target values
- Warning thresholds
- Regulatory vs internal limits
- Time-based effectiveness
- Maturity bucket specific

### 7. ALM Alerts

**Alert Types:**
- Limit breaches
- Risk alerts
- Compliance violations

**Severity Levels:**
- Low
- Medium
- High
- Critical

**Alert Management:**
- Acknowledgment
- Resolution tracking
- Recommendations
- Notification system

## API Endpoints

### Maturity Ladder

```
POST   /api/treasury/alm/maturity-ladder
GET    /api/treasury/alm/maturity-ladder/{report_date}
GET    /api/treasury/alm/maturity-ladder/{report_date}/summary
PUT    /api/treasury/alm/maturity-ladder/{entry_id}
```

### Gap Analysis

```
POST   /api/treasury/alm/gap-analysis
GET    /api/treasury/alm/gap-analysis/{report_date}/{analysis_type}
GET    /api/treasury/alm/gap-analysis/{report_date}/{analysis_type}/summary
```

### Liquidity Ratios

```
POST   /api/treasury/alm/liquidity-ratios
GET    /api/treasury/alm/liquidity-ratios/{report_date}
GET    /api/treasury/alm/liquidity-ratios/trends/{metric_name}
```

### Interest Rate Risk

```
POST   /api/treasury/alm/interest-rate-risk
GET    /api/treasury/alm/interest-rate-risk/{report_date}
GET    /api/treasury/alm/interest-rate-risk/{report_date}/summary
```

### Quarterly Returns

```
POST   /api/treasury/alm/quarterly-returns
GET    /api/treasury/alm/quarterly-returns/{year}/{quarter}
GET    /api/treasury/alm/quarterly-returns
POST   /api/treasury/alm/quarterly-returns/{return_id}/approve
POST   /api/treasury/alm/quarterly-returns/{return_id}/file
```

### Alerts

```
GET    /api/treasury/alm/alerts
POST   /api/treasury/alm/alerts/{alert_id}/acknowledge
POST   /api/treasury/alm/alerts/{alert_id}/resolve
```

### Dashboard

```
GET    /api/treasury/alm/dashboard/{as_of_date}
```

## Usage Examples

### 1. Create Maturity Ladder Entry

```python
POST /api/treasury/alm/maturity-ladder
{
  "report_date": "2024-01-31",
  "bucket": "upto_1_month",
  "cash_and_bank_balance": 50000000.00,
  "investments": 100000000.00,
  "loans_and_advances": 800000000.00,
  "fixed_assets": 50000000.00,
  "other_assets": 20000000.00,
  "deposits": 600000000.00,
  "borrowings": 300000000.00,
  "debt_securities": 50000000.00,
  "other_liabilities": 30000000.00,
  "interest_sensitive_assets": 750000000.00,
  "interest_sensitive_liabilities": 500000000.00,
  "avg_asset_duration": 2.5,
  "avg_liability_duration": 1.8
}
```

### 2. Create Gap Analysis

```python
POST /api/treasury/alm/gap-analysis
{
  "report_date": "2024-01-31",
  "analysis_type": "liquidity_gap",
  "bucket": "upto_1_month",
  "contractual_inflows": 150000000.00,
  "behavioral_inflows": 20000000.00,
  "contractual_outflows": 120000000.00,
  "behavioral_outflows": 30000000.00,
  "risk_level": "medium",
  "risk_score": 45.0,
  "mitigation_required": false,
  "limit_value": 10000000.00
}
```

### 3. Create Liquidity Ratios

```python
POST /api/treasury/alm/liquidity-ratios
{
  "report_date": "2024-01-31",
  "current_ratio": 1.25,
  "quick_ratio": 1.10,
  "cash_ratio": 0.85,
  "liquidity_coverage_ratio": 125.5,
  "net_stable_funding_ratio": 110.2,
  "slr_ratio": 22.5,
  "slr_requirement": 20.0,
  "loan_to_deposit_ratio": 85.5,
  "high_quality_liquid_assets": 250000000.00,
  "total_net_cash_outflows": 200000000.00
}
```

### 4. Create Interest Rate Risk Analysis

```python
POST /api/treasury/alm/interest-rate-risk
{
  "report_date": "2024-01-31",
  "scenario": "parallel_up_100",
  "net_interest_income_base": 80000000.00,
  "market_value_equity_base": 500000000.00,
  "interest_rate_change_bps": 100,
  "net_interest_income_change": -5000000.00,
  "net_interest_income_change_pct": -6.25,
  "market_value_equity_change": -20000000.00,
  "market_value_equity_change_pct": -4.0,
  "modified_duration_assets": 3.2,
  "modified_duration_liabilities": 2.1,
  "duration_gap": 1.1,
  "rate_sensitive_assets": 750000000.00,
  "rate_sensitive_liabilities": 500000000.00,
  "earnings_at_risk": 6000000.00,
  "risk_level": "medium",
  "hedging_required": false
}
```

### 5. Create Quarterly Return

```python
POST /api/treasury/alm/quarterly-returns
{
  "quarter": 1,
  "year": 2024,
  "report_date": "2024-03-31",
  "total_assets": 1200000000.00,
  "total_liabilities": 900000000.00,
  "net_worth": 300000000.00,
  "liquidity_coverage_ratio": 125.5,
  "cumulative_gap_1_year": 50000000.00,
  "cumulative_gap_1_year_pct": 4.17,
  "interest_rate_shock_impact_100bps": -5000000.00,
  "interest_rate_shock_impact_200bps": -10000000.00,
  "earnings_at_risk": 6000000.00,
  "sls_data": { /* SLS statement data */ },
  "irs_data": { /* IRS statement data */ }
}
```

### 6. Get ALM Dashboard

```python
GET /api/treasury/alm/dashboard/2024-01-31

Response:
{
  "as_of_date": "2024-01-31",
  "maturity_summary": {
    "report_date": "2024-01-31",
    "total_assets": 1200000000.00,
    "total_liabilities": 900000000.00,
    "overall_gap": 300000000.00,
    "short_term_gap": 100000000.00,
    "medium_term_gap": 150000000.00,
    "long_term_gap": 50000000.00,
    "risk_level": "medium",
    "largest_gap_bucket": "upto_1_year",
    "largest_gap_amount": 80000000.00
  },
  "liquidity_gap_summary": {
    "report_date": "2024-01-31",
    "analysis_type": "liquidity_gap",
    "total_gap": 50000000.00,
    "critical_buckets": ["upto_7_days"],
    "limit_breaches": 0,
    "mitigation_required": false,
    "overall_risk_level": "low"
  },
  "current_ratio": 1.25,
  "lcr": 125.5,
  "nsfr": 110.2,
  "active_alerts": 5,
  "critical_alerts": 1,
  "all_limits_compliant": true,
  "breached_limits": []
}
```

## Best Practices

### 1. Data Collection

- Update maturity ladder daily/weekly
- Run gap analysis at least monthly
- Calculate liquidity ratios daily
- Perform interest rate risk analysis monthly
- Prepare quarterly returns on time

### 2. Limit Setting

- Define regulatory limits first
- Set internal limits more conservative
- Review limits quarterly
- Update limits based on market conditions
- Document limit rationale

### 3. Alert Management

- Acknowledge alerts promptly
- Investigate root causes
- Document mitigation actions
- Resolve alerts systematically
- Review alert patterns

### 4. Reporting

- Automate data collection
- Validate data accuracy
- Review reports before submission
- Maintain audit trail
- Archive reports securely

### 5. Risk Management

- Monitor gaps continuously
- Stress test regularly
- Develop contingency plans
- Review hedging strategies
- Update risk models

## Regulatory Compliance

### RBI Guidelines

1. **DNBR (Systemic) Directions, 2016**
   - ALM system requirements
   - Liquidity risk management
   - Interest rate risk management

2. **Master Direction - Non-Banking Financial Company - Systemically Important Non-Deposit taking Company and Deposit taking Company (Reserve Bank) Directions, 2016**
   - ALM reporting requirements
   - Structural liquidity statement
   - Interest rate sensitivity statement

3. **ALM Guidelines for NBFCs**
   - Asset Liability Management System
   - Structural Liquidity Statement (SLS)
   - Interest Rate Sensitivity (IRS)
   - Maturity Ladder
   - Gap Analysis

### Reporting Requirements

**Quarterly Returns:**
- Structural Liquidity Statement (SLS)
- Interest Rate Sensitivity (IRS)
- Behavioral Pattern Analysis
- Submit within 15 days of quarter end

**Annual Requirements:**
- ALM Policy document
- ALCO meeting minutes
- Risk management framework
- Stress testing results

## Technical Architecture

### Database Schema

**Tables:**
1. `alm_maturity_ladder` - Maturity bucket analysis
2. `alm_gap_analysis` - Gap analysis data
3. `alm_liquidity_ratios` - Liquidity metrics
4. `alm_interest_rate_risk` - IRR scenarios
5. `alm_quarterly_returns` - Regulatory returns
6. `alm_limits` - Limit definitions
7. `alm_alerts` - Alert management

### Services

1. **MaturityLadderService** - Maturity ladder operations
2. **GapAnalysisService** - Gap analysis calculations
3. **LiquidityRatioService** - Ratio calculations
4. **InterestRateRiskService** - IRR analysis
5. **QuarterlyReturnService** - Return generation
6. **ALMAlertService** - Alert management
7. **ALMDashboardService** - Dashboard aggregation

### Integration Points

- **Accounting Module** - GL balances
- **Loan Module** - Loan portfolio data
- **Deposit Module** - Deposit portfolio data
- **Treasury Module** - Investment data
- **Reporting Module** - Report generation

## Implementation Checklist

- [x] Database models created
- [x] Migration files added
- [x] Service layer implemented
- [x] API endpoints created
- [x] Schemas defined
- [x] Alert system configured
- [x] Dashboard created
- [ ] Frontend components
- [ ] Report templates
- [ ] User documentation
- [ ] Training materials
- [ ] Testing completed

## Next Steps

1. Build frontend components
2. Create report templates
3. Implement data automation
4. Setup monitoring dashboards
5. Conduct user training
6. Perform UAT
7. Go live

## Support

For questions or issues:
- Email: support@nbfcsuite.com
- Documentation: /docs/alm
- API Reference: /api/docs#alm

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Module Status:** ✅ Backend Complete
