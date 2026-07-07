# NPA Management - Practical Examples

## Example 1: Standard Loan Classification

### Scenario
- Loan Amount: ₹1,00,000
- Days Past Due: 15 days
- Security: Fully secured (Gold jewelry worth ₹1,20,000)

### Classification
```python
# API Call
POST /accounting/npa/classify
{
  "days_past_due": 15,
  "is_restructured": false,
  "is_written_off": false
}

# Response
{
  "npa_category": "SPECIAL_MENTION_0",  # SMA-0
  "days_past_due": 15,
  "is_npa": false,
  "is_sma": true,
  "classification_date": "2026-07-07"
}
```

### Provisioning Calculation
```python
POST /accounting/npa/provisioning/calculate
{
  "outstanding_principal": 100000.00,
  "npa_category": "SPECIAL_MENTION_0",
  "is_secured": true,
  "security_coverage_ratio": 100.00,
  "existing_provision": 0.00
}

# Response
{
  "outstanding_principal": 100000.00,
  "provisioning_rate": 0.00,        # No provisioning for SMA
  "required_provision": 0.00,
  "existing_provision": 0.00,
  "additional_provision": 0.00
}
```

### Action Required
- Monitor closely
- Contact customer for payment
- No provisioning needed yet

---

## Example 2: Fresh NPA (Substandard)

### Scenario
- Loan Amount: ₹5,00,000
- Days Past Due: 120 days (crossed 90 DPD threshold)
- Security: Vehicle worth ₹4,00,000
- Security Coverage: 80%

### Classification
```python
POST /accounting/npa/classify
{
  "days_past_due": 120,
  "is_restructured": false,
  "is_written_off": false
}

# Response
{
  "npa_category": "SUBSTANDARD",
  "days_past_due": 120,
  "is_npa": true,
  "is_sma": false,
  "classification_date": "2026-07-07"
}
```

### Provisioning Calculation
```python
POST /accounting/npa/provisioning/calculate
{
  "outstanding_principal": 500000.00,
  "npa_category": "SUBSTANDARD",
  "is_secured": true,
  "security_coverage_ratio": 80.00,
  "existing_provision": 0.00
}

# Response
{
  "outstanding_principal": 500000.00,
  "provisioning_rate": 15.00,           # 15% for secured substandard
  "required_provision": 75000.00,        # ₹75,000
  "existing_provision": 0.00,
  "additional_provision": 75000.00
}
```

### Create Provisioning Entry
```python
POST /accounting/npa/provisioning/create
{
  "loan_account_id": 1001,
  "provision_amount": 75000.00,
  "npa_category": "SUBSTANDARD",
  "as_of_date": "2026-07-31",
  "narration": "Provisioning for substandard asset - Loan #1001"
}

# Accounting Entry Created:
# Dr. Provision Expense (6050)              75,000
#     Cr. Provision for Loan Losses (2400)         75,000
```

---

## Example 3: Doubtful Asset with Partial Security

### Scenario
- Loan Amount: ₹10,00,000
- Days Past Due: 450 days (1.2 years NPA)
- Security: Property worth ₹6,00,000
- Security Coverage: 60%
- Existing Provision: ₹1,50,000

### Classification
```python
# Response
{
  "npa_category": "DOUBTFUL_1",
  "days_past_due": 450,
  "is_npa": true
}
```

### Provisioning Calculation
```python
POST /accounting/npa/provisioning/calculate
{
  "outstanding_principal": 1000000.00,
  "npa_category": "DOUBTFUL_1",
  "is_secured": true,
  "security_coverage_ratio": 60.00,
  "existing_provision": 150000.00
}

# Calculation:
# Secured portion (60%): ₹6,00,000 @ 25% = ₹1,50,000
# Unsecured portion (40%): ₹4,00,000 @ 100% = ₹4,00,000
# Total required provision = ₹5,50,000

# Response
{
  "outstanding_principal": 1000000.00,
  "provisioning_rate": 55.00,              # Weighted average
  "required_provision": 550000.00,
  "existing_provision": 150000.00,
  "additional_provision": 400000.00        # Need to add ₹4,00,000
}
```

### Create Additional Provision
```python
POST /accounting/npa/provisioning/create
{
  "loan_account_id": 1002,
  "provision_amount": 400000.00,
  "npa_category": "DOUBTFUL_1",
  "as_of_date": "2026-07-31",
  "narration": "Additional provisioning for doubtful asset"
}
```

---

## Example 4: Write-off of Loss Asset

### Scenario
- Loan Amount: ₹2,00,000
- Days Past Due: 1200 days (3+ years)
- Legal remedies exhausted
- Existing Provision: ₹2,00,000 (100%)
- Classification: LOSS

### Write-off Process
```python
POST /accounting/npa/write-off
{
  "loan_account_id": 1003,
  "write_off_amount": 200000.00,
  "provision_available": 200000.00,
  "as_of_date": "2026-07-31",
  "narration": "Write-off of loan account #1003 - Legal remedies exhausted"
}

# Accounting Entry Created:
# Dr. Provision for Loan Losses (2400)     2,00,000
#     Cr. Loan Asset (1100)                         2,00,000
```

### Impact on Books
- Loan asset reduced by ₹2,00,000
- Provision utilized (no P&L impact as fully provisioned)
- Loan account marked as written-off
- Recovery efforts continue off-books

---

## Example 5: Upgrade from NPA to Standard

### Scenario
- Loan was NPA (Substandard) for 6 months
- Customer cleared all overdues
- Regular for 12 months
- Outstanding: ₹3,00,000
- Existing Provision: ₹45,000 (15%)

### Upgrade Process
1. **Verify Eligibility**
   - All overdues cleared ✓
   - Regular for 12 months ✓
   - Credit committee approval ✓

2. **Reclassify**
```python
# New classification
{
  "npa_category": "STANDARD",
  "days_past_due": 0
}
```

3. **Reverse Excess Provision**
```python
POST /accounting/npa/provisioning/calculate
{
  "outstanding_principal": 300000.00,
  "npa_category": "STANDARD",
  "is_secured": true,
  "security_coverage_ratio": 100.00,
  "existing_provision": 45000.00
}

# New provision required
# Standard asset: 0.25% of ₹3,00,000 = ₹750
# Excess provision: ₹45,000 - ₹750 = ₹44,250

POST /accounting/npa/provisioning/reverse
{
  "loan_account_id": 1004,
  "provision_amount": 44250.00,
  "as_of_date": "2026-07-31",
  "narration": "Reversal of excess provision on upgrade to standard"
}

# Accounting Entry:
# Dr. Provision for Loan Losses (2400)     44,250
#     Cr. Provision Reversal Income (4020)         44,250
```

---

## Example 6: Monthly Batch Classification

### Scenario
Portfolio of 500 loans as of July 31, 2026

### Run Monthly Classification
```python
POST /accounting/npa/batch/monthly-classification
{
  "as_of_date": "2026-07-31"
}

# Response
{
  "as_of_date": "2026-07-31",
  "processed_at": "2026-07-31T23:45:00Z",
  "total_accounts_processed": 500,
  "classifications": {
    "STANDARD": 420,
    "SPECIAL_MENTION_0": 25,
    "SPECIAL_MENTION_1": 18,
    "SPECIAL_MENTION_2": 12,
    "SUBSTANDARD": 15,
    "DOUBTFUL_1": 7,
    "DOUBTFUL_2": 2,
    "DOUBTFUL_3": 1,
    "LOSS": 0
  },
  "provisions_created": 2850000.00,
  "journal_entries": [10001, 10002, 10003, ...],
  "summary": {
    "new_npas": 3,
    "upgrades": 1,
    "total_npa_ratio": 5.0,
    "provision_coverage": 72.5
  }
}
```

---

## Example 7: Asset Classification Register

### Generate Register
```python
POST /accounting/npa/register
{
  "as_of_date": "2026-07-31",
  "category_filter": null
}

# Response (excerpt)
{
  "as_of_date": "2026-07-31",
  "generated_at": "2026-08-01T10:00:00Z",
  "summary": {
    "total_accounts": 500,
    "total_outstanding": 50000000.00,
    "total_provision": 2850000.00,
    "npa_ratio": 5.0
  },
  "categories": {
    "STANDARD": {
      "category": "STANDARD",
      "account_count": 420,
      "total_outstanding": 42000000.00,
      "total_provision": 105000.00,
      "provisioning_rate": 0.25,
      "accounts": [...]
    },
    "SUBSTANDARD": {
      "category": "SUBSTANDARD",
      "account_count": 15,
      "total_outstanding": 3000000.00,
      "total_provision": 450000.00,
      "provisioning_rate": 15.00,
      "accounts": [
        {
          "loan_account_id": 1001,
          "loan_account_number": "LA-2025-1001",
          "customer_name": "ABC Enterprises",
          "outstanding_principal": 500000.00,
          "days_past_due": 120,
          "npa_category": "SUBSTANDARD",
          "provisioning_rate": 15.00,
          "required_provision": 75000.00,
          "existing_provision": 75000.00,
          "last_payment_date": "2026-03-01"
        }
      ]
    }
  }
}
```

---

## Example 8: NPA Movement Report

### Generate Movement Report
```python
POST /accounting/npa/movement-report
{
  "from_date": "2026-06-01",
  "to_date": "2026-06-30"
}

# Response
{
  "from_date": "2026-06-01",
  "to_date": "2026-06-30",
  "opening_balance": {
    "npa_accounts": 22,
    "npa_amount": 4500000.00
  },
  "additions": {
    "fresh_npa": {
      "account_count": 3,
      "amount": 750000.00,
      "accounts": [
        {
          "loan_account_id": 1005,
          "loan_account_number": "LA-2025-1005",
          "customer_name": "XYZ Traders",
          "outstanding_amount": 250000.00,
          "previous_category": "SPECIAL_MENTION_2",
          "current_category": "SUBSTANDARD",
          "movement_date": "2026-06-15"
        }
      ]
    },
    "increased_provision": {
      "account_count": 2,
      "amount": 500000.00
    }
  },
  "reductions": {
    "upgrades": {
      "account_count": 1,
      "amount": 300000.00,
      "accounts": [...]
    },
    "recoveries": {
      "account_count": 0,
      "amount": 0.00
    },
    "write_offs": {
      "account_count": 1,
      "amount": 200000.00
    }
  },
  "closing_balance": {
    "npa_accounts": 25,
    "npa_amount": 5250000.00
  },
  "movements_by_category": {
    "SUBSTANDARD": {
      "opening": 15,
      "additions": 3,
      "upgrades": 1,
      "downgrades": 2,
      "closing": 19
    }
  }
}
```

---

## Example 9: RBI NPA Return

### Generate Regulatory Report
```python
POST /accounting/npa/reports/rbi-return
{
  "as_of_date": "2026-06-30"
}

# Response
{
  "reporting_date": "2026-06-30",
  "reporting_entity": "NBFC",
  "gross_advances": 50000000.00,
  "gross_npa": 2500000.00,
  "gross_npa_ratio": 5.00,
  "provisions_held": 1875000.00,
  "net_npa": 625000.00,
  "net_npa_ratio": 1.25,
  "category_wise_npa": {
    "substandard": 1500000.00,
    "doubtful": 900000.00,
    "loss": 100000.00
  },
  "sector_wise_npa": {
    "retail": 1200000.00,
    "msme": 800000.00,
    "corporate": 500000.00
  },
  "security_wise_npa": {
    "secured": 2000000.00,
    "unsecured": 500000.00
  }
}
```

---

## Example 10: Provisioning Coverage Ratio

### Calculate PCR
```python
POST /accounting/npa/reports/provisioning-coverage-ratio
{
  "as_of_date": "2026-06-30"
}

# Response
{
  "as_of_date": "2026-06-30",
  "gross_npa": 2500000.00,
  "provisions_held": 1875000.00,
  "pcr_percentage": 75.00,              # Good! Above 70% threshold
  "category_wise_pcr": {
    "substandard": 15.00,
    "doubtful_1": 55.00,
    "doubtful_2": 70.00,
    "doubtful_3": 100.00,
    "loss": 100.00
  },
  "required_provision": 1875000.00,
  "shortfall": 0.00                     # Fully provisioned
}
```

---

## Key Takeaways

### For Standard Loans (0-30 DPD)
- Monitor through SMA categories
- No provisioning required for SMA
- Early intervention is key

### For NPAs (90+ DPD)
- Immediate classification required
- Create provisions as per norms
- Initiate recovery process
- Report to management

### For Doubtful Assets
- Higher provisioning rates
- Security valuation critical
- Legal action may be needed
- Consider settlement options

### For Loss Assets
- 100% provisioning
- Write-off after approvals
- Continue recovery efforts
- Off-book tracking

### Monthly Checklist
1. ✅ Calculate DPD for all loans
2. ✅ Run auto-classification
3. ✅ Review new NPAs
4. ✅ Calculate provisions
5. ✅ Create journal entries
6. ✅ Generate reports
7. ✅ Management review
8. ✅ Board presentation (quarterly)

---

## Common Scenarios

### Scenario: Customer Makes Partial Payment
- Recalculate DPD
- May not upgrade immediately
- Continue monitoring
- Update classification if fully regular

### Scenario: Security Value Decreases
- Revalue security
- Recalculate provisioning
- May need additional provision
- Consider legal options

### Scenario: Customer Disputes Amount
- Keep as NPA during dispute
- Maintain provisioning
- Document dispute details
- Update on resolution

### Scenario: OTS (One Time Settlement)
- Requires credit committee approval
- Calculate NPV of settlement
- Write off difference
- Release excess provision

---

This examples guide demonstrates real-world usage of the NPA Management module for comprehensive portfolio management and regulatory compliance.
