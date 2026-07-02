# Phase 2: Gold Customer Journey

## Overview

The Customer Journey phase implements the complete flow from walk-in customer to gold loan application creation, integrating seamlessly with the Customer/CIF service and the Product Configuration Engine built in Phase 1.

## Features Implemented

### 1. **Session Management**
- Session tracking for every customer interaction
- Multi-channel support (Branch, Mobile, Web, Partner)
- Session types (New loan, Renewal, Release, Inquiry)
- Session lifecycle management (Initiated → Completed/Abandoned)
- Unique session numbers for tracking

### 2. **Customer Search & Selection**
- Multi-criteria search (Phone, Aadhar, PAN, Name, Customer ID)
- Integration with Customer/CIF service
- Search history logging for analytics
- Customer 360 view integration
- Existing gold loan history display

### 3. **Product Recommendation Engine**
- AI-powered product recommendations
- Score-based ranking
- Context-aware suggestions (customer segment, amount, history)
- Eligibility pre-screening
- Recommendation reasoning

### 4. **Eligibility Validation**
- Rule-based eligibility checking
- Age, income, CIBIL, segment validation
- Pass/fail tracking per rule
- Detailed failure reasons
- Mandatory vs optional rule handling

### 5. **Journey Step Tracking**
- Detailed step-by-step tracking
- Duration calculation per step
- Success/failure logging
- Error message capture
- Step-level analytics data

### 6. **Customer Interactions**
- Officer notes and observations
- Interaction categorization
- Sentiment tracking
- Follow-up management
- Conversation history

### 7. **KYC Verification Tracking**
- Document verification status
- Multiple verification methods (OTP, Digilocker, API, Manual)
- Verification response storage
- Expiry date tracking

## Journey Flow

```
1. Create Session
   ↓
2. Search Customer
   ├─ Found → Select Customer
   └─ Not Found → Create CIF
   ↓
3. Get Product Recommendations
   ↓
4. Select Product
   ↓
5. Check Eligibility
   ├─ Passed → Proceed to Appraisal
   └─ Failed → Show reasons / Select alternate product
   ↓
6. Create Application
```

## Database Schema

### Core Tables
- `gold_customer_sessions` - Session tracking
- `gold_customer_search_log` - Search history
- `gold_product_selections` - Product selection tracking
- `gold_eligibility_checks` - Eligibility validation results
- `gold_kyc_verifications` - KYC verification status
- `gold_journey_steps` - Detailed step tracking
- `gold_customer_interactions` - Officer notes

## API Endpoints

### Session Management
```
POST   /api/v1/gold/journey/sessions              # Create new session
GET    /api/v1/gold/journey/sessions/{id}         # Get session details
PATCH  /api/v1/gold/journey/sessions/{id}         # Update session
GET    /api/v1/gold/journey/sessions              # List sessions
```

### Customer Search
```
POST   /api/v1/gold/journey/search-customer       # Search customer
POST   /api/v1/gold/journey/select-customer/{session_id}/{customer_id}  # Select customer
```

### Product Recommendation
```
GET    /api/v1/gold/journey/recommend-products/{session_id}  # Get recommendations
POST   /api/v1/gold/journey/select-product                   # Select product
```

### Eligibility
```
POST   /api/v1/gold/journey/check-eligibility/{session_id}/{product_id}  # Check eligibility
```

### Journey Steps
```
POST   /api/v1/gold/journey/steps          # Create step
PATCH  /api/v1/gold/journey/steps/{id}     # Update step
```

### Interactions
```
POST   /api/v1/gold/journey/interactions              # Create interaction
GET    /api/v1/gold/journey/interactions/{session_id} # List interactions
```

## Frontend Features

### New Journey Page (`/gold-lending/journey/new`)
- **Progressive UI with 5 Steps**:
  1. Start Session - Channel selection
  2. Customer Search - Multi-criteria search with results
  3. Product Selection - AI recommendations with scoring
  4. Eligibility Check - Real-time validation
  5. Application Creation - Proceed to appraisal

- **Visual Progress Indicator**
- **Session Information Display**
- **Error Handling & User Feedback**
- **Smart Defaults & Auto-population**

## Integration with Customer Service

### Expected Customer Service Endpoints
```
GET  /customers/{id}                    # Get customer details
POST /customers/search                  # Search customers
GET  /customers/{id}/gold-loans         # Get existing gold loans
GET  /customers/{id}/360                # Customer 360 view
```

### Customer Data Structure
```json
{
  "id": "customer_id",
  "name": "Customer Name",
  "phone": "9876543210",
  "email": "customer@example.com",
  "pan": "ABCDE1234F",
  "aadhar_masked": "XXXX-XXXX-1234",
  "age": 35,
  "segment": "premium",
  "kyc_status": "verified",
  "cibil_score": 750,
  "gold_loans_count": 2,
  "gold_outstanding": 150000
}
```

## Product Recommendation Algorithm

### Scoring Factors
1. **Amount Match** (30% weight)
   - Within product limits → +0.3
   - Outside limits → -0.2

2. **Customer Segment** (20% weight)
   - Premium customers → Premium products +0.2
   - Regular customers → Standard products +0.1

3. **Eligibility** (30% weight)
   - All mandatory rules passed → +0.3
   - Some mandatory rules failed → -0.5

4. **Product Type Suitability** (20% weight)
   - Instant loan for small amounts → +0.3
   - OD for business customers → +0.2

### Recommendation Response
```json
{
  "product_id": "uuid",
  "product_code": "GL-JEWEL-001",
  "product_name": "Gold Jewel Loan",
  "recommendation_score": 0.85,
  "recommendation_reason": "Amount within range; Suitable for premium segment",
  "suggested_amount": 100000,
  "is_eligible": true
}
```

## Eligibility Validation

### Supported Rule Types
- **Age**: Min/max age validation
- **Income**: Minimum income requirement
- **CIBIL**: Minimum credit score
- **Segment**: Customer segment matching
- **Geography**: Location-based eligibility
- **Existing Loans**: Maximum concurrent loans

### Rule Operators
- `eq` - Equal to
- `ne` - Not equal to
- `gt` - Greater than
- `lt` - Less than
- `gte` - Greater than or equal
- `lte` - Less than or equal
- `in` - Value in list
- `not_in` - Value not in list
- `contains` - String contains

### Eligibility Result
```json
{
  "product_id": "uuid",
  "product_name": "Gold Jewel Loan",
  "is_eligible": true,
  "passed_checks": 5,
  "total_checks": 5,
  "failed_checks": [],
  "can_proceed": true
}
```

## Analytics & Tracking

### Journey Analytics
- **Conversion Funnel**
  - Sessions initiated
  - Customers searched
  - Products selected
  - Eligibility passed
  - Applications created
  - Conversion rate per step

- **Drop-off Analysis**
  - Abandonment reasons
  - Average time per step
  - Bottleneck identification

- **Product Performance**
  - Recommendation frequency
  - Selection rate
  - Eligibility pass rate
  - Conversion to application

- **Customer Insights**
  - Search patterns
  - Product preferences
  - Interaction types
  - Officer performance

## Setup & Usage

### 1. Run Migration
```bash
psql -U nbfc_user -d nbfcsuite -f infra/migrations/019_gold_customer_journey.sql
```

### 2. Update Dependencies
```bash
cd services/gold
pip install httpx  # For customer service API calls
```

### 3. Start Gold Service
```bash
cd services/gold
uvicorn app.main:app --reload --port 8013
```

### 4. Configure Customer Service URL
Update in `services/gold/app/routers/journey.py`:
```python
customer_api_url = "http://localhost:8002"  # Your customer service URL
```

### 5. Access Frontend
Navigate to: `http://localhost:3000/gold-lending/journey/new`

## Example: Complete Journey Flow

### Step 1: Create Session
```bash
curl -X POST http://localhost:8013/api/v1/gold/journey/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "branch",
    "session_type": "new_loan",
    "branch_id": "BRANCH-001",
    "initiated_by_user_id": "USER-001"
  }'
```

Response:
```json
{
  "id": "session-uuid",
  "session_number": "GLS-20260703120000-A1B2C3",
  "status": "initiated",
  "channel": "branch",
  "initiated_at": "2026-07-03T12:00:00Z"
}
```

### Step 2: Search Customer
```bash
curl -X POST http://localhost:8013/api/v1/gold/journey/search-customer \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "phone": "9876543210"
  }'
```

### Step 3: Select Customer
```bash
curl -X POST http://localhost:8013/api/v1/gold/journey/select-customer/session-uuid/customer-uuid
```

### Step 4: Get Recommendations
```bash
curl http://localhost:8013/api/v1/gold/journey/recommend-products/session-uuid?requested_amount=100000
```

### Step 5: Select Product
```bash
curl -X POST http://localhost:8013/api/v1/gold/journey/select-product \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "product_id": "product-uuid",
    "requested_amount": 100000,
    "selection_source": "ai_recommendation"
  }'
```

### Step 6: Check Eligibility
```bash
curl -X POST http://localhost:8013/api/v1/gold/journey/check-eligibility/session-uuid/product-uuid
```

## Key Advantages

### vs Traditional Approach
❌ **Before**: Manual process, no tracking, paper-based  
✅ **After**: Digital journey, complete tracking, analytics-driven

### Business Benefits
1. **Complete Visibility**: Track every customer interaction
2. **Conversion Optimization**: Identify and fix bottlenecks
3. **Personalization**: AI-driven product recommendations
4. **Compliance**: Audit trail for every decision
5. **Officer Productivity**: Guided workflow reduces errors
6. **Customer Experience**: Faster, smoother journey

## Security & Compliance

- All customer searches logged for audit
- PII data masked in logs (Aadhar)
- Session timeout handling
- User authentication required
- Role-based access control (to be implemented)
- GDPR-compliant data handling

## Performance Considerations

- Customer service calls are asynchronous
- 5-second timeout on external API calls
- Caching of product recommendations
- Indexed queries for fast search
- Session cleanup job (implement scheduled cleanup)

## Future Enhancements (Phase 3+)

1. **Real-time Customer Service Integration**
   - WebSocket for live updates
   - Push notifications

2. **Advanced AI Recommendations**
   - FinDNA behavioral analysis
   - Seasonal pattern detection
   - Cross-sell opportunities

3. **Mobile-First Journey**
   - QR code customer identification
   - Offline mode support
   - GPS-based branch check-in

4. **Video KYC Integration**
   - Live video verification
   - Document capture via camera
   - Liveness detection

## Testing

### API Testing
```bash
# Run journey flow
./test_journey_flow.sh

# Test customer search
curl -X POST http://localhost:8013/api/v1/gold/journey/search-customer \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "phone": "9876543210"}'
```

### Frontend Testing
1. Navigate to `/gold-lending/journey/new`
2. Click "Walk-in at Branch"
3. Search for customer by phone
4. Select customer from results
5. View product recommendations
6. Select eligible product
7. Verify eligibility check passes

## Troubleshooting

### Customer Service Not Responding
- Check customer service is running
- Verify URL in `journey.py`
- Check network connectivity
- Review timeout settings

### Eligibility Always Failing
- Verify customer data is complete
- Check product eligibility rules
- Review rule operators
- Test with known-good customer

### Session Not Updating
- Check database connection
- Verify session ID is valid
- Review transaction commits

## Files Created/Modified

### Backend
- `infra/migrations/019_gold_customer_journey.sql`
- `services/gold/app/models/journey.py`
- `services/gold/app/schemas/journey.py`
- `services/gold/app/routers/journey.py`
- `services/gold/app/main.py` (updated)

### Frontend
- `apps/customer-app/app/gold-lending/journey/new/page.tsx`
- `apps/customer-app/app/gold-lending/goldApi.ts` (updated)

---

**Phase 2 Status**: ✅ **COMPLETE**  
**Sessions**: Tracked end-to-end  
**Customer Search**: Multi-criteria with CIF integration  
**Product Recommendations**: AI-powered scoring  
**Eligibility**: Rule-based validation engine  
**Journey Steps**: 7 tables, 15+ API endpoints, complete frontend flow
