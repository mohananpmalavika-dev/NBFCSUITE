# Phase 3: Gold Appraisal Engine

## Overview

The Appraisal Engine is the technical heart of the gold lending platform. It handles ornament cataloging, multi-step purity testing, weight verification with maker-checker controls, market rate management, automated valuation, and fraud detection through anomaly tracking.

## Features Implemented

### 1. **Ornament Type Master**
- **15 Pre-configured Types**: Chain, Ring, Bangle, Bracelet, Coin, Necklace, Ear Ring, Pendant, Anklet, Mangalsutra, Waist Belt, Nose Pin, Toe Ring, Gold Coin, Gold Biscuit, Gold Bar
- **Categories**: Jewellery, Coin, Biscuit, Bar
- **Typical Stone Percentages**: Pre-configured for accurate weight calculations
- **Extensible**: Add new ornament types as needed

### 2. **Enhanced Ornament Cataloging**
- **Barcode Generation**: Unique barcode for each ornament
- **QR Code Support**: For mobile scanning
- **Photo Management**: Multiple photos per ornament (general, hallmark, close-up, damage)
- **Hallmark Tracking**: Hallmark ID and center information
- **Stone Details**: Comprehensive stone information (type, count, weight)
- **Making Charges & Wastage**: Track additional value components
- **Status Lifecycle**: received → appraised → verified → vaulted → released
- **Tags & Metadata**: Flexible JSON-based tagging system

### 3. **Multi-Step Purity Testing**
- **Test Methods**:
  - Touchstone (traditional)
  - XRF (X-Ray Fluorescence)
  - Fire Assay (most accurate)
  - Acid Test
- **Multiple Tests Per Ornament**: Quality assurance through redundancy
- **Test Location Tracking**: Which part of ornament was tested
- **Equipment Tracking**: Which device was used
- **Verification Workflow**: Maker-checker for test results
- **Certificate Storage**: Link to test certificates
- **Variance Detection**: Automatic flagging of inconsistent results

### 4. **Gold Market Rate Management**
- **Multi-Purity Support**: 24K, 22K, 20K, 18K rates
- **Rate Sources**: India Bullion, MCX, International, Manual
- **Geographic Rates**: City-specific and branch-specific rates
- **Rate History**: Complete historical tracking
- **Effective Date Ranges**: Time-based rate activation
- **Rate Per Gram & Per 10 Gram**: Flexible rate display
- **Auto-deactivation**: Old rates automatically deactivated

### 5. **Appraisal Sessions**
- **Session-Based Workflow**: Group multiple ornaments per application
- **Real-time Calculations**: Auto-calculate totals as ornaments are added
- **Average Purity Tracking**: Weighted average across all ornaments
- **LTV Application**: Configurable Loan-to-Value ratio
- **Eligible Loan Calculation**: Automatic based on total value and LTV
- **Session Status**: in_progress → completed → verified
- **Appraiser Tracking**: Who performed the appraisal
- **Verifier Support**: Second-level verification

### 6. **Automated Valuation Engine**
```
Valuation Formula:
Net Weight (g) × Gold Rate (₹/g) × Purity (%) ÷ 100 = Appraised Value

Net Weight = Gross Weight - Stone Weight
Purity % = (Karat ÷ 24) × 100

Example:
50g gross weight, 2g stone, 22K purity, ₹6,000/g rate
Net = 48g
Purity = (22/24) × 100 = 91.67%
Value = 48 × 6,000 × 91.67 ÷ 100 = ₹2,64,019
```

### 7. **Weight Verification (Maker-Checker)**
- **Three-Step Process**:
  1. Maker measures weight
  2. Checker verifies weight
  3. System calculates variance
- **Measurement Types**: Gross weight, Net weight, Stone weight
- **Weighing Scale Tracking**: Which scale was used
- **Variance Calculation**: Automatic difference calculation
- **Tolerance Limits**: Flag variances > 0.1g
- **Accept/Reject Workflow**: Checker can accept or reject measurement
- **Rejection Reasons**: Document why measurement was rejected

### 8. **Anomaly Detection & Fraud Prevention**
- **Anomaly Types**:
  - **Weight Mismatch**: Maker-checker variance
  - **Purity Variance**: Different test results
  - **Hallmark Fake**: Suspicious hallmark patterns
  - **Duplicate Barcode**: Same barcode used twice
  - **Suspicious Pattern**: AI-detected unusual patterns
- **Severity Levels**: Low, Medium, High, Critical
- **Detection Sources**: System, User, AI
- **Investigation Workflow**: Open → Investigating → Resolved/False Positive
- **Resolution Tracking**: Who resolved, when, and notes

### 9. **Valuation History**
- **Valuation Types**:
  - Initial (at appraisal)
  - Periodic (revaluation)
  - Pre-auction (before auction)
  - Release (at loan closure)
- **Multiple Values**:
  - Calculated Value (formula-based)
  - Market Value (current market)
  - Forced Sale Value (distress sale/auction)
- **Historical Tracking**: Complete value history per ornament
- **Trend Analysis**: Track gold value changes over time

### 10. **Quick Appraisal (Instant Loans)**
- **Simplified Process**: For small-value instant loans
- **Instant Valuation**: Immediate estimate without full process
- **Conservative LTV**: Lower LTV (70%) for risk mitigation
- **Approval Limits**: Up to ₹50,000 instant approval
- **Full Appraisal Flag**: Indicates if full appraisal needed
- **Photo Upload**: Single photo for documentation

## Database Schema

### Core Tables
- `gold_ornament_types` - Master ornament type catalog (15 types)
- `gold_ornaments` - Enhanced ornament records (expanded from Phase 1)
- `gold_purity_tests` - Multi-step purity testing records
- `gold_market_rates` - Daily gold rates by purity and location
- `gold_appraisal_sessions` - Session-based appraisal tracking
- `gold_ornament_valuations` - Historical valuation tracking
- `gold_weight_verifications` - Maker-checker weight verification
- `gold_appraisal_anomalies` - Fraud detection and anomaly tracking

## API Endpoints

### Ornament Types
```
GET    /api/v1/gold/appraisal/ornament-types              # List types
```

### Market Rates
```
POST   /api/v1/gold/appraisal/market-rates                # Create rate
GET    /api/v1/gold/appraisal/market-rates/current        # Get current rates
GET    /api/v1/gold/appraisal/market-rates/{id}           # Get specific rate
```

### Appraisal Sessions
```
POST   /api/v1/gold/appraisal/sessions                    # Create session
GET    /api/v1/gold/appraisal/sessions/{id}               # Get session details
PATCH  /api/v1/gold/appraisal/sessions/{id}               # Update session
POST   /api/v1/gold/appraisal/sessions/{id}/complete      # Complete appraisal
```

### Purity Tests
```
POST   /api/v1/gold/appraisal/purity-tests                # Record test
PATCH  /api/v1/gold/appraisal/purity-tests/{id}/verify    # Verify test
GET    /api/v1/gold/appraisal/purity-tests/ornament/{id}  # List tests
```

### Weight Verification
```
POST   /api/v1/gold/appraisal/weight-measurements         # Maker: measure
POST   /api/v1/gold/appraisal/weight-measurements/{id}/verify  # Checker: verify
```

### Anomalies
```
POST   /api/v1/gold/appraisal/anomalies                   # Create anomaly
PATCH  /api/v1/gold/appraisal/anomalies/{id}/resolve      # Resolve anomaly
GET    /api/v1/gold/appraisal/anomalies                   # List anomalies
```

### Quick Appraisal
```
POST   /api/v1/gold/appraisal/quick-appraisal             # Instant valuation
```

## Frontend Features

### Appraisal Dashboard (`/gold-lending/appraisal/{sessionId}`)
- **Summary Cards**: Ornaments, Net Weight, Total Value, Eligible Loan
- **Current Market Rates Display**: Real-time rates for all purities
- **Ornaments List**: All ornaments with details
- **Add Ornament Modal**: Capture ornament details
- **Photo Upload**: Multiple photos per ornament
- **Purity Selection**: 24K, 22K, 20K, 18K
- **Hallmark Tracking**: Optional hallmark information
- **Auto-calculation**: Real-time value calculation
- **Complete Appraisal**: Finalize and calculate totals

## Barcode System

### Barcode Format
```
GLO-YYYYMMDDHHMMSS-RANDOM
Example: GLO-20260703120000-A1B2C3
```

### Barcode Usage
- Unique identifier for each ornament
- Used for vault tracking
- Printed on packet labels
- Scanned during release
- Links to complete ornament history

## Purity Testing Workflow

### Single Ornament - Multiple Tests
```
Test 1: Touchstone → 22.1K
Test 2: XRF → 22.0K
Test 3: Fire Assay → 21.9K

Average: 22.0K (within tolerance)
Status: Verified ✓
```

### Variance Detection
```
Test 1: 22.0K
Test 2: 20.5K  ← Variance: 1.5K

Action: Flag Anomaly
Severity: High
Investigation Required
```

## Weight Verification Workflow

### Maker-Checker Process
```
Step 1: Officer A (Maker)
  - Measures gross weight: 50.125g
  - Uses Scale ID: SC-001
  - Status: Pending Verification

Step 2: Officer B (Checker)
  - Verifies gross weight: 50.120g
  - Variance: 0.005g
  - Within Tolerance (< 0.1g)
  - Status: Accepted ✓

Step 3: System
  - Records both measurements
  - Calculates variance
  - Updates ornament record
```

### High Variance Scenario
```
Maker: 50.125g
Checker: 50.550g
Variance: 0.425g (> 0.1g tolerance)

Action:
1. Create Anomaly (weight_mismatch, High severity)
2. Require third measurement
3. Manager investigation
```

## Market Rate Management

### Daily Rate Update Process
```sql
-- Deactivate old rates
UPDATE gold_market_rates 
SET is_active = false 
WHERE rate_date < CURRENT_DATE;

-- Insert new rates
INSERT INTO gold_market_rates (
  rate_date, purity_karat, rate_per_gram, rate_source
) VALUES
  ('2026-07-03', 24.0, 6500, 'india_bullion'),
  ('2026-07-03', 22.0, 6000, 'india_bullion'),
  ('2026-07-03', 18.0, 4900, 'india_bullion');
```

### Branch-Specific Rates
```
Global Rate (22K): ₹6,000/g
Branch Override (Mumbai): ₹6,050/g  ← Higher due to local market
Branch Override (Rural): ₹5,950/g   ← Lower due to logistics
```

## Anomaly Detection Examples

### 1. Purity Variance
```json
{
  "anomaly_type": "purity_variance",
  "severity": "high",
  "description": "Test variance of 2.5K detected between XRF and Fire Assay",
  "detection_data": {
    "test_1": {"method": "xrf", "result": "22.0K"},
    "test_2": {"method": "fire_assay", "result": "19.5K"},
    "variance": 2.5
  }
}
```

### 2. Duplicate Barcode
```json
{
  "anomaly_type": "duplicate_barcode",
  "severity": "critical",
  "description": "Barcode GLO-20260703-A1B2C3 already exists",
  "detection_data": {
    "existing_ornament_id": "uuid-1",
    "attempted_ornament_id": "uuid-2",
    "barcode": "GLO-20260703-A1B2C3"
  }
}
```

### 3. Suspicious Pattern (AI-Detected)
```json
{
  "anomaly_type": "suspicious_pattern",
  "severity": "medium",
  "description": "Customer pledging same ornament type 3 times in 7 days",
  "detection_data": {
    "customer_id": "CUST-001",
    "ornament_type": "chain",
    "count": 3,
    "days": 7,
    "ai_confidence": 0.85
  }
}
```

## Valuation Example

### Complete Valuation Calculation
```
Input:
- Ornament: Gold Necklace
- Gross Weight: 100.000g
- Stone Weight: 8.500g
- Purity: 22K
- Gold Rate (22K): ₹6,000/g
- Making Charges: ₹5,000
- Wastage: 2g

Calculations:
1. Net Weight = 100.000 - 8.500 = 91.500g
2. Effective Weight = 91.500 + 2.000 = 93.500g
3. Purity % = (22 ÷ 24) × 100 = 91.67%
4. Gold Value = 93.500 × 6,000 × 91.67 ÷ 100 = ₹5,14,044
5. Total Value = ₹5,14,044 + ₹5,000 = ₹5,19,044

LTV @ 75%:
Eligible Loan = ₹5,19,044 × 75 ÷ 100 = ₹3,89,283
```

## Setup & Usage

### 1. Run Migration
```bash
psql -U nbfc_user -d nbfcsuite -f infra/migrations/020_gold_appraisal_engine.sql
```

### 2. Seed Ornament Types
Ornament types are automatically seeded in the migration (15 types).

### 3. Add Market Rates
```bash
curl -X POST http://localhost:8013/api/v1/gold/appraisal/market-rates \
  -H "Content-Type: application/json" \
  -d '{
    "rate_date": "2026-07-03",
    "rate_source": "india_bullion",
    "purity_karat": 22.0,
    "rate_per_gram": 6000,
    "effective_from": "2026-07-03T00:00:00Z"
  }'
```

### 4. Create Appraisal Session
```bash
curl -X POST http://localhost:8013/api/v1/gold/appraisal/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "app-uuid",
    "customer_id": "customer-uuid",
    "appraiser_user_id": "user-uuid",
    "ltv_percent": 75.0
  }'
```

### 5. Access Frontend
Navigate to: `http://localhost:3000/gold-lending/appraisal/{sessionId}`

## Integration Points

### With Phase 1 (Product Engine)
- ✅ LTV from product configuration
- ✅ Min/max weight limits
- ✅ Purity threshold validation

### With Phase 2 (Customer Journey)
- ✅ Session links to journey session
- ✅ Customer context available
- ✅ Product selection determines LTV

### Future Integrations
- **Phase 4**: Ornament catalog enhancement
- **Phase 5**: Vault packet creation after appraisal
- **Phase 6**: LMS loan creation with appraised value
- **Phase 10**: AI-powered fraud detection

## Key Advantages

### vs Traditional Manual Appraisal
❌ **Before**: Paper-based, prone to errors, no audit trail  
✅ **After**: Digital, automated calculations, complete audit trail

### Enterprise Benefits
1. **Accuracy**: Automated calculations eliminate human errors
2. **Speed**: Real-time valuation as ornaments are added
3. **Transparency**: Complete visibility into appraisal process
4. **Fraud Prevention**: Multi-layered anomaly detection
5. **Compliance**: Complete audit trail for regulators
6. **Quality Assurance**: Maker-checker and multi-test verification
7. **Scalability**: Handle high-volume appraisals efficiently

## Security & Compliance

### Maker-Checker Controls
- Weight measurements require dual verification
- Purity tests can be verified by supervisors
- Anomalies tracked with resolution workflow

### Audit Trail
- Every measurement recorded with timestamp and user
- Historical valuations maintained
- Photo evidence stored permanently

### Fraud Detection
- Automatic variance detection
- Pattern recognition for suspicious activity
- Critical anomalies escalated immediately

## Performance Considerations

- Ornament photos stored in blob storage (not database)
- Market rates cached in Redis for fast lookups
- Valuation calculations optimized for bulk operations
- Indexes on frequently queried fields (barcode, session_id)

## Testing

### API Testing
```bash
# Create appraisal session
./scripts/test_appraisal_session.sh

# Add ornament
curl -X POST http://localhost:8013/api/v1/gold/appraisal/sessions/{session_id}/ornaments

# Complete appraisal
curl -X POST http://localhost:8013/api/v1/gold/appraisal/sessions/{session_id}/complete
```

### Frontend Testing
1. Navigate to `/gold-lending/appraisal/{sessionId}`
2. Add ornament with valid weight and purity
3. Verify auto-calculation of value
4. Add multiple ornaments
5. Complete appraisal
6. Verify eligible loan amount calculation

## Troubleshooting

### Valuation Not Calculating
- Check if market rates exist for selected purity
- Verify net weight > 0 (gross weight > stone weight)
- Check purity karat is between 10-24

### Anomalies Being Created
- Review tolerance thresholds in code
- Check if variances are genuine or too strict
- Adjust variance limits if needed

### Weight Verification Failing
- Ensure checker is different from maker
- Verify variance calculation logic
- Check scale calibration

## Files Created/Modified

### Backend
- `infra/migrations/020_gold_appraisal_engine.sql`
- `services/gold/app/models/appraisal.py`
- `services/gold/app/schemas/appraisal.py`
- `services/gold/app/routers/appraisal.py`
- `services/gold/app/main.py` (updated)

### Frontend
- `apps/customer-app/app/gold-lending/appraisal/[sessionId]/page.tsx`
- `apps/customer-app/app/gold-lending/goldApi.ts` (updated)

---

**Phase 3 Status**: ✅ **COMPLETE**  
**Ornament Types**: 15 pre-configured types  
**Market Rates**: Multi-purity with geographic support  
**Appraisal Sessions**: Complete workflow with auto-calculation  
**Purity Testing**: Multi-method with verification  
**Weight Verification**: Maker-checker controls  
**Anomaly Detection**: 5 types with severity levels  
**API Endpoints**: 15+ appraisal endpoints  
**Frontend**: Complete appraisal UI with real-time calculations
