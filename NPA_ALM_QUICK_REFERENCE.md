# NPA & ALM Modules - Quick Reference Guide

## 🚀 Quick Start

### NPA Management
**Access:** Accounting → NPA Management  
**Route:** `/accounting/npa`

### ALM
**Access:** Treasury → ALM (Asset-Liability)  
**Route:** `/treasury/alm`

---

## 📊 NPA Management - 9 Pages

| Page | Route | Purpose |
|------|-------|---------|
| Dashboard | `/accounting/npa` | Overview & KPIs |
| Classification | `/accounting/npa/classify` | Classify loans by DPD |
| Calculator | `/accounting/npa/calculator` | Calculate provisioning |
| Register | `/accounting/npa/register` | Asset classification register |
| Provisions | `/accounting/npa/provisions` | Manage provisions |
| Movement | `/accounting/npa/movement` | NPA movement report |
| Vintage | `/accounting/npa/vintage` | Cohort analysis |
| RBI Return | `/accounting/npa/rbi-return` | Regulatory return |
| PCR | `/accounting/npa/pcr` | Provisioning coverage ratio |

### NPA Categories (RBI Guidelines)
1. **STANDARD** - 0 DPD → 0.25% provision
2. **SMA-0** - 1-30 DPD → 0% provision
3. **SMA-1** - 31-60 DPD → 0% provision
4. **SMA-2** - 61-90 DPD → 0% provision
5. **SUBSTANDARD** - 91-365 DPD → 15-25% provision
6. **DOUBTFUL-1** - 366-730 DPD → 25-100% provision
7. **DOUBTFUL-2** - 731-1095 DPD → 40-100% provision
8. **DOUBTFUL-3** - 1096+ DPD → 100% provision
9. **LOSS** - Identified loss → 100% provision

---

## 💼 ALM Module - 7 Pages

| Page | Route | Purpose |
|------|-------|---------|
| Dashboard | `/treasury/alm` | Overview & metrics |
| Maturity Ladder | `/treasury/alm/maturity-ladder` | 12 time buckets |
| Gap Analysis | `/treasury/alm/gap-analysis` | 4 gap types |
| Liquidity Ratios | `/treasury/alm/liquidity-ratios` | 6 key ratios |
| Interest Rate Risk | `/treasury/alm/interest-rate-risk` | 7 scenarios |
| Quarterly Returns | `/treasury/alm/quarterly-returns` | SLS & IRS |
| Alerts | `/treasury/alm/alerts` | Risk alerts |

### Maturity Buckets (12 Time Periods)
1. Up to 1 day
2. Up to 7 days
3. Up to 14 days
4. Up to 1 month
5. Up to 2 months
6. Up to 3 months
7. Up to 6 months
8. Up to 1 year
9. Up to 2 years
10. Up to 3 years
11. Up to 5 years
12. Above 5 years

### Liquidity Ratios (6 Metrics)
1. **LCR** - Liquidity Coverage Ratio (Target: ≥100%)
2. **NSFR** - Net Stable Funding Ratio (Target: ≥100%)
3. **Current Ratio** (Target: ≥1.0)
4. **Quick Ratio** (Target: ≥1.0)
5. **Cash Ratio** (Target: ≥0.5)
6. **Liquid Asset Ratio** (Target: 15-20%)

### Interest Rate Scenarios (7 Stress Tests)
1. Base Scenario
2. Parallel Up 100 bps
3. Parallel Down 100 bps
4. Parallel Up 200 bps
5. Parallel Down 200 bps
6. Yield Curve Steepening
7. Yield Curve Flattening

### Gap Analysis Types (4 Types)
1. **Liquidity Gap** - Cash flow mismatches
2. **Interest Rate Gap** - Rate-sensitive assets vs liabilities
3. **Maturity Gap** - Maturity mismatches
4. **Duration Gap** - Duration-weighted gap

---

## 🔧 Technical Reference

### TypeScript Services
```typescript
// NPA Service
import { npaService } from '@/services/npa.service'
// Methods: classifyAsset, getLoanClassification, calculateProvisioning,
// createProvision, reverseProvision, writeOffLoan, getAssetClassificationRegister,
// getNPASummary, getNPAMovementReport, getVintageAnalysis, getRBINPAReturn,
// getProvisioningCoverageRatio, runMonthlyClassification

// ALM Service
import { almService } from '@/services/alm.service'
// Methods: createMaturityLadder, getMaturityLadder, createGapAnalysis,
// getGapAnalysis, createLiquidityRatios, getLiquidityRatios,
// createInterestRateRisk, getInterestRateRisk, createQuarterlyReturn,
// getQuarterlyReturn, getAlerts, acknowledgeAlert, resolveAlert, getDashboard
```

### API Base URLs
```
NPA: /api/v1/accounting/npa
ALM: /api/v1/treasury/alm
```

---

## 📋 Common Workflows

### NPA Workflow
1. **Classify Loan** → Enter DPD → Get category
2. **Calculate Provision** → Enter details → Get amount
3. **Create Provision** → Submit → GL entry created
4. **Monitor Register** → Review all NPAs
5. **Generate Reports** → RBI return, PCR, Vintage

### ALM Workflow
1. **View Dashboard** → Check key metrics
2. **Update Maturity Ladder** → Enter assets/liabilities
3. **Analyze Gaps** → Identify mismatches
4. **Calculate Ratios** → Check compliance
5. **Run IRR Scenarios** → Assess risk
6. **Prepare Returns** → SLS/IRS quarterly
7. **Monitor Alerts** → Address breaches

---

## 🎯 Key Features

### NPA Management
✅ Auto-classification by DPD  
✅ Provisioning calculator  
✅ Secured/unsecured logic  
✅ Batch processing  
✅ Write-off management  
✅ RBI-compliant reporting  
✅ PCR tracking  
✅ Vintage analysis  

### ALM
✅ 12-bucket maturity ladder  
✅ 4 gap analysis types  
✅ 6 liquidity ratios  
✅ 7 IRR stress scenarios  
✅ Quarterly return preparation  
✅ Real-time alerts  
✅ Compliance monitoring  
✅ Dashboard analytics  

---

## 🔍 Quick Checks

### To verify NPA is working:
1. Navigate to `/accounting/npa`
2. Click "Classify Loan"
3. Enter DPD (e.g., 95)
4. Should show "SUBSTANDARD" category

### To verify ALM is working:
1. Navigate to `/treasury/alm`
2. Check dashboard loads with metrics
3. Click "Maturity Ladder"
4. Should show 12 time buckets

---

## 📞 Support & Documentation

- **Full Documentation:** `NPA_ALM_IMPLEMENTATION_COMPLETE.md`
- **Backend Services:** Already implemented and functional
- **Frontend Pages:** All 16 pages created and integrated
- **Navigation:** Sidebar updated with menu items

---

## 🚦 Status Indicators

### NPA Module
- Backend: ✅ Complete
- Frontend: ✅ Complete
- Navigation: ✅ Integrated
- Testing: ⏭️ Ready for UAT

### ALM Module
- Backend: ✅ Complete
- Frontend: ✅ Complete
- Navigation: ✅ Integrated
- Testing: ⏭️ Ready for UAT

---

**Last Updated:** January 15, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
