# Decision Engine - Design Document

**Module**: Decision Engine  
**Version**: 1.0  
**Date**: July 5, 2026  
**Status**: 🚧 In Progress  

---

## 📋 EXECUTIVE SUMMARY

The Decision Engine is an intelligent, real-time decision-making system that provides instant approvals/rejections for financial products. It integrates with the Rules Engine to apply business rules and provides cached decisions for high-volume scenarios.

### Key Capabilities
- Instant decision API (< 200ms response time)
- Integration with Rules Engine for policy enforcement
- Decision caching for repeat customers
- Pre-approved limit calculations
- Credit score-based instant offers
- Configurable decision strategies
- Complete audit trail
- A/B testing support

---

## 🎯 BUSINESS OBJECTIVES

### Primary Goals
1. **Speed**: Provide instant decisions (< 200ms)
2. **Accuracy**: Apply all relevant business rules
3. **Scalability**: Handle high-volume requests
4. **Flexibility**: Support multiple decision types
5. **Transparency**: Explain every decision

### Use Cases
1. **Instant Loan Approval**
   - Customer applies for ₹50,000 personal loan
   - System evaluates in real-time
   - Returns approved/rejected/manual_review

2. **Pre-Approved Offers**
   - System calculates pre-approved limit
   - Based on customer profile and history
   - Displayed in customer portal

3. **Credit Limit Increase**
   - Existing customer requests limit increase
   - System evaluates automatically
   - Returns new approved limit

4. **Product Eligibility**
   - Customer views product
   - System shows instant eligibility
   - Personalized product recommendations

5. **Quick Quote**
   - Customer enters loan details
   - System returns instant quote
   - Interest rate, EMI, fees

---

## 🏗️ ARCHITECTURE

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Decision Engine                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Decision   │  │  Strategy    │  │   Cache      │  │
│  │   Service    │  │  Manager     │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Offer     │  │   Limit      │  │  Analytics   │  │
│  │   Service    │  │  Calculator  │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │    Rules    │ │  Customer   │ │    Loan     │
    │   Engine    │ │   Module    │ │   Module    │
    └─────────────┘ └─────────────┘ └─────────────┘
```

### Integration Points
- **Rules Engine**: Apply business rules and policies
- **Customer Module**: Fetch customer data and history
- **Loan Module**: Retrieve loan history and performance
- **Accounting Module**: Check financial status
- **Credit Bureau**: External credit score integration (ready)

---

## 📊 DATABASE SCHEMA

### 1. InstantDecision
Stores instant decision requests and responses.

```python
class InstantDecision(Base):
    __tablename__ = "instant_decisions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    decision_number = Column(String(50), unique=True, nullable=False)
    
    # Decision Details
    decision_type = Column(String(50), nullable=False)  # loan_approval, pre_approved, limit_increase, eligibility, quick_quote
    entity_type = Column(String(50), nullable=False)  # loan_application, customer, product
    entity_id = Column(Integer, nullable=True)
    
    # Customer Information
    customer_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=True)
    
    # Request Data
    request_data = Column(JSON, nullable=False)  # Input parameters
    
    # Decision Result
    decision_result = Column(String(50), nullable=False)  # approved, rejected, manual_review, pending
    approved_amount = Column(Numeric(15, 2), nullable=True)
    approved_tenure = Column(Integer, nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)
    
    # Decision Factors
    decision_factors = Column(JSON, nullable=True)  # Factors that influenced decision
    rules_applied = Column(JSON, nullable=True)  # Rules evaluated
    confidence_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    
    # Explanation
    decision_reason = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    
    # Strategy
    strategy_used = Column(String(50), nullable=False)  # instant, cached, rule_based, ml_based
    
    # Performance
    evaluation_time_ms = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False)
    
    # Status
    status = Column(String(50), default="active")  # active, expired, superseded, accepted, rejected
    valid_until = Column(DateTime, nullable=True)  # Offer validity
    
    # Acceptance
    accepted_at = Column(DateTime, nullable=True)
    accepted_by = Column(Integer, nullable=True)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
```

### 2. PreApprovedOffer
Pre-calculated offers for customers.

```python
class PreApprovedOffer(Base):
    __tablename__ = "pre_approved_offers"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_code = Column(String(50), unique=True, nullable=False)
    
    # Customer & Product
    customer_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    
    # Offer Details
    offer_type = Column(String(50), nullable=False)  # pre_approved_loan, limit_increase, special_rate
    approved_amount = Column(Numeric(15, 2), nullable=False)
    min_amount = Column(Numeric(15, 2), nullable=True)
    max_amount = Column(Numeric(15, 2), nullable=False)
    
    # Terms
    interest_rate = Column(Numeric(5, 2), nullable=False)
    min_tenure = Column(Integer, nullable=True)
    max_tenure = Column(Integer, nullable=False)
    processing_fee_waiver = Column(Boolean, default=False)
    
    # Validity
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    
    # Status
    status = Column(String(50), default="active")  # active, expired, used, cancelled
    
    # Usage
    used_at = Column(DateTime, nullable=True)
    used_by = Column(Integer, nullable=True)
    application_id = Column(Integer, nullable=True)  # If used
    
    # Calculation
    calculation_factors = Column(JSON, nullable=True)
    credit_score = Column(Integer, nullable=True)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
```

### 3. DecisionStrategy
Configurable decision strategies.

```python
class DecisionStrategy(Base):
    __tablename__ = "decision_strategies"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_code = Column(String(50), unique=True, nullable=False)
    
    # Strategy Details
    strategy_name = Column(String(200), nullable=False)
    decision_type = Column(String(50), nullable=False)  # loan_approval, eligibility, etc.
    description = Column(Text, nullable=True)
    
    # Configuration
    strategy_config = Column(JSON, nullable=False)
    # {
    #   "rule_categories": ["credit_policy", "risk_assessment"],
    #   "evaluation_strategy": "all_match",
    #   "auto_approve_threshold": 80,
    #   "manual_review_threshold": 60,
    #   "cache_ttl_minutes": 30,
    #   "max_amount_auto_approve": 500000
    # }
    
    # Priority
    priority = Column(Integer, default=100)  # Lower = higher priority
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
```

### 4. DecisionCache
Cache for instant decision results.

```python
class DecisionCache(Base):
    __tablename__ = "decision_cache"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    
    # Cache Details
    decision_type = Column(String(50), nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)
    
    # Cached Data
    cached_decision = Column(JSON, nullable=False)
    
    # Cache Metadata
    hit_count = Column(Integer, default=0)
    last_hit_at = Column(DateTime, nullable=True)
    
    # TTL
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 5. DecisionAnalytics
Analytics and metrics for decisions.

```python
class DecisionAnalytics(Base):
    __tablename__ = "decision_analytics"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Period
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=True)  # For hourly metrics
    
    # Decision Type
    decision_type = Column(String(50), nullable=False, index=True)
    strategy_code = Column(String(50), nullable=True)
    
    # Metrics
    total_requests = Column(Integer, default=0)
    approved_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    manual_review_count = Column(Integer, default=0)
    
    # Performance
    avg_evaluation_time_ms = Column(Integer, default=0)
    cache_hit_count = Column(Integer, default=0)
    cache_hit_rate = Column(Numeric(5, 2), default=0)
    
    # Amounts
    total_approved_amount = Column(Numeric(15, 2), default=0)
    avg_approved_amount = Column(Numeric(15, 2), default=0)
    
    # Conversion
    acceptance_count = Column(Integer, default=0)
    acceptance_rate = Column(Numeric(5, 2), default=0)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 🔧 SERVICE LAYER

### 1. DecisionService
Core decision-making logic.

**Methods**:
- `make_instant_decision(request)` - Main decision endpoint
- `get_decision(decision_id)` - Retrieve decision
- `accept_decision(decision_id, user_id)` - Accept offer
- `reject_decision(decision_id, user_id, reason)` - Reject offer
- `get_customer_decisions(customer_id)` - Customer history
- `recalculate_decision(decision_id)` - Recalculate

### 2. StrategyService
Manage decision strategies.

**Methods**:
- `create_strategy(data)` - Create strategy
- `update_strategy(strategy_id, data)` - Update strategy
- `get_strategy(decision_type)` - Get active strategy
- `execute_strategy(strategy, input_data)` - Execute strategy logic
- `get_strategy_stats(strategy_code)` - Performance stats

### 3. CacheService
Decision caching for performance.

**Methods**:
- `get_cached_decision(cache_key)` - Retrieve from cache
- `set_cached_decision(cache_key, decision, ttl)` - Store in cache
- `invalidate_cache(customer_id)` - Clear customer cache
- `cleanup_expired_cache()` - Remove expired entries
- `get_cache_stats()` - Cache performance metrics

### 4. OfferService
Pre-approved offer management.

**Methods**:
- `calculate_pre_approved_offer(customer_id)` - Calculate offer
- `create_offer(offer_data)` - Create offer
- `get_customer_offers(customer_id)` - Active offers
- `use_offer(offer_id, application_id)` - Mark offer as used
- `expire_offers()` - Expire old offers
- `get_offer_stats()` - Offer analytics

### 5. LimitCalculatorService
Credit limit calculations.

**Methods**:
- `calculate_eligible_amount(customer_id, product_id)` - Calculate limit
- `calculate_interest_rate(customer_data)` - Rate calculation
- `calculate_emi(amount, rate, tenure)` - EMI calculation
- `calculate_processing_fee(amount, product_id)` - Fee calculation

### 6. AnalyticsService
Decision analytics and reporting.

**Methods**:
- `record_decision(decision)` - Record for analytics
- `get_decision_metrics(date_range)` - Metrics
- `get_approval_rate(decision_type)` - Approval rate
- `get_avg_response_time()` - Performance
- `get_cache_efficiency()` - Cache stats

---

## 📡 API ENDPOINTS

### Decision Management (8 endpoints)

```
POST   /decisions/instant               - Make instant decision
GET    /decisions/{id}                  - Get decision details
POST   /decisions/{id}/accept           - Accept decision/offer
POST   /decisions/{id}/reject           - Reject decision/offer
POST   /decisions/{id}/recalculate      - Recalculate decision
GET    /decisions/customer/{id}         - Customer decisions
GET    /decisions                       - List decisions (with filters)
GET    /decisions/{id}/explain          - Explain decision
```

### Pre-Approved Offers (6 endpoints)

```
POST   /offers/calculate                - Calculate pre-approved offer
POST   /offers                          - Create offer
GET    /offers                          - List offers
GET    /offers/{id}                     - Get offer details
GET    /offers/customer/{id}            - Customer active offers
POST   /offers/{id}/use                 - Use offer (create application)
```

### Decision Strategies (5 endpoints)

```
POST   /strategies                      - Create strategy
GET    /strategies                      - List strategies
GET    /strategies/{id}                 - Get strategy
PUT    /strategies/{id}                 - Update strategy
DELETE /strategies/{id}                 - Delete strategy
```

### Analytics (5 endpoints)

```
GET    /decisions/analytics/metrics     - Overall metrics
GET    /decisions/analytics/approval-rate - Approval rate trends
GET    /decisions/analytics/performance - Performance metrics
GET    /decisions/analytics/cache-stats - Cache statistics
GET    /decisions/analytics/by-type     - Metrics by decision type
```

**Total**: 24 endpoints

---

## 🔄 DECISION FLOW

### Instant Decision Flow

```
1. Request Received
   ↓
2. Validate Input
   ↓
3. Check Cache (if enabled)
   ↓ (cache miss)
4. Load Customer Data
   ↓
5. Load Strategy Config
   ↓
6. Evaluate Rules (via Rules Engine)
   ↓
7. Calculate Limits
   ↓
8. Apply Strategy Logic
   ↓
9. Generate Decision
   ↓
10. Cache Result (if applicable)
    ↓
11. Record Analytics
    ↓
12. Return Response
```

### Decision Logic

```python
# Pseudo-code for decision logic

if confidence_score >= auto_approve_threshold:
    if amount <= max_auto_approve_amount:
        return "approved"
    else:
        return "manual_review"  # High amount needs manual review
        
elif confidence_score >= manual_review_threshold:
    return "manual_review"  # Borderline case
    
else:
    return "rejected"  # Low confidence
```

---

## 📝 REQUEST/RESPONSE SCHEMAS

### Instant Decision Request

```json
{
  "decision_type": "loan_approval",
  "customer_id": 12345,
  "product_id": 1,
  "request_data": {
    "loan_amount": 500000,
    "tenure": 36,
    "purpose": "personal",
    "customer_data": {
      "monthly_income": 75000,
      "existing_emi": 15000,
      "employment_type": "salaried",
      "employer_name": "ABC Corp",
      "work_experience_months": 48
    }
  },
  "use_cache": true
}
```

### Instant Decision Response

```json
{
  "success": true,
  "data": {
    "decision_id": 123,
    "decision_number": "DEC-202607-00123",
    "decision_result": "approved",
    "approved_amount": 500000,
    "approved_tenure": 36,
    "interest_rate": 12.5,
    "processing_fee": 5000,
    "emi": 16625,
    "confidence_score": 87.5,
    "decision_reason": "Customer meets all eligibility criteria",
    "recommendation": "Pre-approved for instant disbursement",
    "decision_factors": [
      {
        "factor": "Credit Score",
        "value": 750,
        "impact": "positive",
        "weight": 0.3
      },
      {
        "factor": "Monthly Income",
        "value": 75000,
        "impact": "positive",
        "weight": 0.25
      },
      {
        "factor": "Existing EMI",
        "value": 15000,
        "impact": "neutral",
        "weight": 0.15
      }
    ],
    "valid_until": "2026-07-12T23:59:59Z",
    "evaluation_time_ms": 145,
    "cache_hit": false,
    "strategy_used": "instant"
  }
}
```

---

## 🎯 DECISION STRATEGIES

### Strategy 1: Instant Auto-Approval
**For**: Small loans to existing good customers

```json
{
  "strategy_code": "instant_auto_approval",
  "strategy_name": "Instant Auto Approval",
  "decision_type": "loan_approval",
  "strategy_config": {
    "rule_categories": ["credit_policy", "existing_customer"],
    "evaluation_strategy": "all_match",
    "auto_approve_threshold": 85,
    "manual_review_threshold": 70,
    "max_amount_auto_approve": 100000,
    "cache_ttl_minutes": 30,
    "enable_cache": true
  }
}
```

### Strategy 2: Comprehensive Evaluation
**For**: Large loans or new customers

```json
{
  "strategy_code": "comprehensive_eval",
  "strategy_name": "Comprehensive Evaluation",
  "decision_type": "loan_approval",
  "strategy_config": {
    "rule_categories": ["credit_policy", "risk_assessment", "fraud_detection"],
    "evaluation_strategy": "all_match",
    "auto_approve_threshold": 90,
    "manual_review_threshold": 75,
    "max_amount_auto_approve": 500000,
    "cache_ttl_minutes": 0,
    "enable_cache": false,
    "require_credit_bureau": true
  }
}
```

---

## 🔐 INTEGRATION POINTS

### With Rules Engine
```python
# Evaluate rules via Rules Engine
evaluation_result = await rules_service.evaluate_rules(
    category_codes=strategy_config["rule_categories"],
    entity_type="loan_application",
    entity_id=application_id,
    input_data=request_data
)

# Extract confidence from rules evaluation
confidence_score = evaluation_result.confidence_score
```

### With Customer Module
```python
# Fetch customer data
customer = await customer_service.get_customer(customer_id)
customer_stats = await customer_service.get_customer_stats(customer_id)

# Check existing loans
existing_loans = await loan_service.get_customer_loans(
    customer_id=customer_id,
    status="active"
)
```

### With Loan Module
```python
# Check repayment history
repayment_history = await loan_service.get_repayment_history(customer_id)
dpd_stats = await collection_service.get_dpd_stats(customer_id)
```

---

## 📈 PERFORMANCE TARGETS

### Response Time
- **Target**: < 200ms for 95th percentile
- **Max**: < 500ms for 99th percentile

### Throughput
- **Target**: 1,000 requests/second
- **Peak**: 2,000 requests/second

### Cache Performance
- **Hit Rate**: > 60%
- **TTL**: Configurable (15-60 minutes)

### Accuracy
- **Approval Accuracy**: > 95%
- **False Positive Rate**: < 5%
- **False Negative Rate**: < 3%

---

## 🔒 SECURITY & COMPLIANCE

### Data Security
- ✅ All decisions logged
- ✅ PII encrypted at rest
- ✅ Audit trail maintained
- ✅ Access control enforced

### Compliance
- ✅ Decision explainability
- ✅ Non-discriminatory algorithms
- ✅ Override tracking
- ✅ Regulatory reporting ready

---

## 📊 MONITORING & ANALYTICS

### Key Metrics
1. **Volume Metrics**
   - Total decisions per day/hour
   - Decisions by type
   - Decisions by strategy

2. **Quality Metrics**
   - Approval rate
   - Rejection rate
   - Manual review rate
   - Confidence score distribution

3. **Performance Metrics**
   - Average response time
   - 95th/99th percentile response time
   - Cache hit rate
   - Error rate

4. **Business Metrics**
   - Total approved amount
   - Average approved amount
   - Offer acceptance rate
   - Time to acceptance

---

## 🎯 SUCCESS CRITERIA

- ✅ 24 REST API endpoints
- ✅ < 200ms response time (p95)
- ✅ Integration with Rules Engine
- ✅ Decision caching implemented
- ✅ Pre-approved offer system
- ✅ Complete audit trail
- ✅ Analytics and reporting
- ✅ Multi-tenant support
- ✅ Production-ready code
- ✅ Complete documentation

---

## 📝 IMPLEMENTATION PHASES

### Phase 1: Foundation (30%)
- ✅ Design document
- ⏳ Database models
- ⏳ Pydantic schemas

### Phase 2: Core Services (40%)
- ⏳ DecisionService
- ⏳ StrategyService
- ⏳ CacheService
- ⏳ OfferService

### Phase 3: API Layer (20%)
- ⏳ Decision endpoints
- ⏳ Offer endpoints
- ⏳ Strategy endpoints

### Phase 4: Integration (10%)
- ⏳ Rules Engine integration
- ⏳ Customer Module integration
- ⏳ Main.py registration

---

## 📚 DOCUMENTATION DELIVERABLES

1. ✅ `DECISION_ENGINE_DESIGN.md` (This document)
2. ⏳ `DECISION_ENGINE_PROGRESS.md` (Progress tracker)
3. ⏳ `DECISION_ENGINE_COMPLETE.md` (Final documentation)
4. ⏳ API endpoint examples
5. ⏳ Integration guide

---

**Design Status**: ✅ Complete  
**Next Step**: Build database models  
**Target Completion**: Today (July 5, 2026)  
**Platform Impact**: 95% → 98%

---

*Design Document Created: July 5, 2026*  
*NBFC Financial Suite - Decision Engine Module*  
*"Instant Decisions, Intelligent Approvals"*
