# Business Rules Engine - Design Document

**Module**: Business Rules Engine  
**Version**: 1.0  
**Date**: July 5, 2026  
**Status**: Design Phase  

---

## 📋 EXECUTIVE SUMMARY

The Business Rules Engine is a critical component that enables dynamic configuration and evaluation of business rules across the NBFC platform. It separates business logic from code, allowing non-technical users to define and modify rules without development intervention.

### Purpose
- Define business rules without code changes
- Enable dynamic credit policy management
- Support product-specific rules
- Provide real-time rule evaluation
- Maintain rule version history and audit trail

### Scope
- Rule definition and management
- Rule evaluation engine
- Decision management
- Rule versioning
- Rule testing and simulation
- Integration with all modules

---

## 🎯 BUSINESS REQUIREMENTS

### Core Functionality

1. **Rule Management**
   - Create, update, delete rules
   - Rule categorization (credit policy, eligibility, pricing, etc.)
   - Rule versioning and history
   - Rule activation/deactivation
   - Rule priority and ordering

2. **Rule Evaluation**
   - Real-time rule execution
   - Multiple evaluation strategies
   - Condition-based logic
   - Support for complex expressions
   - Rule chaining and dependencies

3. **Decision Management**
   - Automated decision-making
   - Decision audit trail
   - Decision explanations
   - Override management

4. **Rule Testing**
   - Rule simulation with test data
   - Validation before activation
   - Impact analysis

### Use Cases

1. **Credit Policy Rules**
   - Minimum income requirements
   - Maximum loan-to-value ratio
   - Age criteria (min/max)
   - Employment stability
   - Credit score thresholds
   - Debt-to-income ratio

2. **Product Eligibility Rules**
   - Customer type restrictions
   - Geographic restrictions
   - Product-specific criteria
   - Cross-sell eligibility

3. **Pricing Rules**
   - Interest rate determination
   - Fee calculation rules
   - Discount eligibility
   - Risk-based pricing

4. **Approval Rules**
   - Auto-approval criteria
   - Manual review triggers
   - Escalation rules
   - Authority matrix

5. **Risk Assessment Rules**
   - Risk scoring
   - Fraud detection indicators
   - Red flag identification
   - Early warning signals

---

## 🏗️ ARCHITECTURE

### Components

```
┌─────────────────────────────────────────┐
│         Rules Engine Module             │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    Rule Repository              │   │
│  │  - Rule Definitions             │   │
│  │  - Rule Categories              │   │
│  │  - Rule Versions                │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    Evaluation Engine            │   │
│  │  - Expression Parser            │   │
│  │  - Condition Evaluator          │   │
│  │  - Decision Manager             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    Decision Log                 │   │
│  │  - Evaluation History           │   │
│  │  - Decision Audit Trail         │   │
│  │  - Override Tracking            │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Rule Structure

```json
{
  "rule_code": "CREDIT_MIN_INCOME",
  "rule_name": "Minimum Income Requirement",
  "category": "credit_policy",
  "rule_type": "eligibility",
  "priority": 100,
  "conditions": [
    {
      "field": "customer.monthly_income",
      "operator": ">=",
      "value": 25000,
      "data_type": "number"
    }
  ],
  "logical_operator": "AND",
  "action": {
    "type": "reject",
    "message": "Minimum income requirement not met",
    "reason_code": "MIN_INCOME_FAIL"
  },
  "active": true
}
```

---

## 💾 DATABASE DESIGN

### Tables

#### 1. rule_categories
Master table for rule categories

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| category_code | VARCHAR(50) UNIQUE | Category code |
| category_name | VARCHAR(200) | Category name |
| description | TEXT | Description |
| parent_category_id | INTEGER FK | Parent category (for hierarchy) |
| is_active | BOOLEAN | Active status |
| tenant_id | INTEGER | Tenant ID |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Update timestamp |

**Categories**:
- credit_policy
- eligibility
- pricing
- approval
- risk_assessment
- fraud_detection
- compliance

#### 2. business_rules
Core rule definitions

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| rule_code | VARCHAR(100) UNIQUE | Rule code |
| rule_name | VARCHAR(200) | Rule name |
| category_id | INTEGER FK | Category reference |
| rule_type | VARCHAR(50) | Type (eligibility, scoring, etc.) |
| description | TEXT | Rule description |
| priority | INTEGER | Execution priority (1-1000) |
| rule_definition | JSONB | Complete rule definition |
| evaluation_strategy | VARCHAR(50) | first_match, all_match, priority |
| version | INTEGER | Version number |
| is_active | BOOLEAN | Active status |
| effective_from | DATE | Effective start date |
| effective_to | DATE | Effective end date |
| created_by | INTEGER | Creator user ID |
| updated_by | INTEGER | Updater user ID |
| tenant_id | INTEGER | Tenant ID |
| is_deleted | BOOLEAN | Soft delete flag |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Update timestamp |

**Indexes**:
- idx_rules_code (rule_code, tenant_id)
- idx_rules_category (category_id, is_active)
- idx_rules_priority (priority, is_active)

#### 3. rule_conditions
Individual conditions within rules

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| rule_id | INTEGER FK | Rule reference |
| condition_group | INTEGER | Group number (for OR logic) |
| field_path | VARCHAR(200) | JSON path to field |
| operator | VARCHAR(20) | Comparison operator |
| value | TEXT | Comparison value |
| data_type | VARCHAR(20) | Data type |
| is_negated | BOOLEAN | NOT condition |
| tenant_id | INTEGER | Tenant ID |

**Operators**:
- Comparison: =, !=, <, <=, >, >=
- String: contains, starts_with, ends_with, matches (regex)
- List: in, not_in
- Null: is_null, is_not_null
- Logical: between, exists

#### 4. rule_actions
Actions to take when rule matches

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| rule_id | INTEGER FK | Rule reference |
| action_type | VARCHAR(50) | Action type |
| action_config | JSONB | Action configuration |
| execution_order | INTEGER | Order of execution |
| tenant_id | INTEGER | Tenant ID |

**Action Types**:
- approve / reject
- set_value (set a field value)
- calculate (perform calculation)
- trigger_workflow
- send_notification
- log_event

#### 5. rule_evaluations
Audit trail of rule evaluations

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| evaluation_id | UUID | Unique evaluation ID |
| rule_id | INTEGER FK | Rule evaluated |
| entity_type | VARCHAR(50) | Entity being evaluated |
| entity_id | INTEGER | Entity ID |
| input_data | JSONB | Input data snapshot |
| evaluation_result | VARCHAR(20) | pass, fail, error |
| matched | BOOLEAN | Rule matched or not |
| output_data | JSONB | Result data |
| execution_time_ms | INTEGER | Execution time |
| error_message | TEXT | Error if any |
| evaluated_by | INTEGER | User who triggered |
| tenant_id | INTEGER | Tenant ID |
| evaluated_at | TIMESTAMP | Evaluation timestamp |

**Indexes**:
- idx_eval_entity (entity_type, entity_id)
- idx_eval_rule (rule_id, evaluated_at)
- idx_eval_result (evaluation_result, evaluated_at)

#### 6. rule_decisions
Final decisions made by rules engine

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| decision_id | UUID | Unique decision ID |
| entity_type | VARCHAR(50) | Entity type |
| entity_id | INTEGER | Entity ID |
| decision_type | VARCHAR(50) | Decision type |
| decision_result | VARCHAR(50) | Final decision |
| confidence_score | DECIMAL(5,2) | Confidence (0-100) |
| rules_applied | JSONB | List of rules applied |
| decision_factors | JSONB | Key factors in decision |
| override_applied | BOOLEAN | Manual override |
| override_by | INTEGER | User who overrode |
| override_reason | TEXT | Override reason |
| decided_by | INTEGER | User who triggered |
| tenant_id | INTEGER | Tenant ID |
| decided_at | TIMESTAMP | Decision timestamp |

#### 7. rule_versions
Version history of rules

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Primary key |
| rule_id | INTEGER FK | Rule reference |
| version_number | INTEGER | Version number |
| rule_snapshot | JSONB | Complete rule at that version |
| change_summary | TEXT | What changed |
| changed_by | INTEGER | User who made changes |
| changed_at | TIMESTAMP | Change timestamp |
| tenant_id | INTEGER | Tenant ID |

---

## 🔧 RULE DEFINITION FORMAT

### Complete Rule Schema

```json
{
  "rule_code": "LOAN_AGE_CRITERIA",
  "rule_name": "Loan Applicant Age Criteria",
  "category": "credit_policy",
  "rule_type": "eligibility",
  "description": "Age must be between 21 and 65 years",
  "priority": 100,
  
  "conditions": [
    {
      "field": "customer.age",
      "operator": ">=",
      "value": 21,
      "data_type": "number"
    },
    {
      "field": "customer.age",
      "operator": "<=",
      "value": 65,
      "data_type": "number"
    }
  ],
  
  "logical_operator": "AND",
  
  "actions": [
    {
      "type": "reject",
      "message": "Age criteria not met. Must be between 21-65 years.",
      "reason_code": "AGE_CRITERIA_FAIL",
      "severity": "error"
    }
  ],
  
  "metadata": {
    "applicable_products": ["personal_loan", "business_loan"],
    "documentation_required": false,
    "can_override": false,
    "tags": ["age", "eligibility", "mandatory"]
  }
}
```

### Rule with Complex Conditions

```json
{
  "rule_code": "HIGH_RISK_ASSESSMENT",
  "rule_name": "High Risk Customer Identification",
  "category": "risk_assessment",
  "rule_type": "scoring",
  "priority": 200,
  
  "condition_groups": [
    {
      "group_id": 1,
      "operator": "AND",
      "conditions": [
        {
          "field": "customer.credit_score",
          "operator": "<",
          "value": 650
        },
        {
          "field": "loan.amount",
          "operator": ">",
          "value": 500000
        }
      ]
    },
    {
      "group_id": 2,
      "operator": "AND",
      "conditions": [
        {
          "field": "customer.employment_type",
          "operator": "in",
          "value": ["self_employed", "freelance"]
        },
        {
          "field": "customer.business_vintage",
          "operator": "<",
          "value": 24
        }
      ]
    }
  ],
  
  "group_operator": "OR",
  
  "actions": [
    {
      "type": "set_value",
      "field": "risk_category",
      "value": "high"
    },
    {
      "type": "trigger_workflow",
      "workflow_code": "ENHANCED_DUE_DILIGENCE"
    },
    {
      "type": "send_notification",
      "recipient_roles": ["risk_manager"],
      "template": "high_risk_alert"
    }
  ]
}
```

---

## 🔍 EVALUATION ENGINE

### Evaluation Flow

```
Input Data
    ↓
Fetch Applicable Rules (by category, active status)
    ↓
Sort by Priority
    ↓
For Each Rule:
  ↓
  Parse Conditions
  ↓
  Evaluate Conditions against Input Data
  ↓
  Match? → Execute Actions
  ↓
  Log Evaluation
    ↓
Aggregate Results
    ↓
Make Final Decision
    ↓
Log Decision
    ↓
Return Result
```

### Evaluation Strategies

1. **First Match**
   - Stop at first matching rule
   - Use for mutually exclusive rules
   - Fast execution

2. **All Match**
   - Evaluate all rules
   - Collect all matches
   - Use for scoring/accumulation

3. **Priority Based**
   - Evaluate by priority order
   - Can stop on critical failure
   - Use for approval workflows

4. **Best Match**
   - Evaluate all, return best result
   - Use for pricing/optimization

---

## 📡 API ENDPOINTS

### Rule Management (15 endpoints)

**Category Management**
```
GET    /api/v1/rules/categories              # List categories
POST   /api/v1/rules/categories              # Create category
GET    /api/v1/rules/categories/{id}         # Get category
PUT    /api/v1/rules/categories/{id}         # Update category
DELETE /api/v1/rules/categories/{id}         # Delete category
```

**Rule CRUD**
```
POST   /api/v1/rules                         # Create rule
GET    /api/v1/rules                         # List rules
GET    /api/v1/rules/{id}                    # Get rule details
PUT    /api/v1/rules/{id}                    # Update rule
DELETE /api/v1/rules/{id}                    # Delete rule (soft)
```

**Rule Operations**
```
POST   /api/v1/rules/{id}/activate           # Activate rule
POST   /api/v1/rules/{id}/deactivate         # Deactivate rule
POST   /api/v1/rules/{id}/clone              # Clone rule
GET    /api/v1/rules/{id}/versions           # Version history
POST   /api/v1/rules/{id}/revert/{version}   # Revert to version
```

### Rule Evaluation (8 endpoints)

**Evaluation**
```
POST   /api/v1/rules/evaluate                # Evaluate rules
POST   /api/v1/rules/evaluate-batch          # Batch evaluation
POST   /api/v1/rules/test                    # Test rule with data
POST   /api/v1/rules/simulate                # Simulate rule changes
```

**Evaluation History**
```
GET    /api/v1/rules/evaluations             # List evaluations
GET    /api/v1/rules/evaluations/{id}        # Get evaluation details
GET    /api/v1/rules/decisions               # List decisions
GET    /api/v1/rules/decisions/{id}          # Get decision details
```

### Decision Management (5 endpoints)

**Decisions**
```
POST   /api/v1/rules/decisions/{id}/override # Override decision
GET    /api/v1/rules/decisions/entity/{type}/{id}  # Get entity decisions
GET    /api/v1/rules/decisions/statistics    # Decision statistics
```

**Analytics**
```
GET    /api/v1/rules/analytics/performance   # Rule performance
GET    /api/v1/rules/analytics/usage         # Rule usage stats
```

---

## 🔐 SECURITY & PERMISSIONS

### Permission Matrix

| Action | Required Permission |
|--------|-------------------|
| View Rules | rules.view |
| Create Rules | rules.create |
| Update Rules | rules.update |
| Delete Rules | rules.delete |
| Activate/Deactivate | rules.manage |
| Evaluate Rules | rules.evaluate |
| Override Decisions | decisions.override |
| View Evaluations | evaluations.view |
| Manage Categories | categories.manage |

### Audit Requirements
- All rule changes logged
- All evaluations recorded
- All decisions auditable
- Override trail maintained

---

## 🎨 FRONTEND COMPONENTS

### Pages Needed

1. **Rules Dashboard**
   - Active rules count
   - Recent evaluations
   - Decision statistics
   - Rule performance metrics

2. **Rule List**
   - Filterable by category
   - Search by rule name/code
   - Quick activate/deactivate
   - Bulk operations

3. **Rule Builder**
   - Visual condition builder
   - Drag-and-drop interface
   - Template selection
   - Real-time validation

4. **Rule Details**
   - Rule information
   - Condition display
   - Action configuration
   - Version history
   - Test interface

5. **Evaluation History**
   - Timeline view
   - Filter by entity/result
   - Drill-down to details
   - Export capability

6. **Decision Log**
   - Decision timeline
   - Override management
   - Decision factors display
   - Analytics dashboard

---

## 🧪 TESTING STRATEGY

### Unit Tests
- Condition evaluation logic
- Operator implementations
- Data type conversions
- Expression parsing

### Integration Tests
- Rule evaluation flow
- Database operations
- API endpoints
- Decision logging

### Performance Tests
- Large ruleset evaluation
- Concurrent evaluations
- Complex condition performance
- Database query optimization

### Test Data Requirements
- Sample rules for all categories
- Test input data sets
- Expected outputs
- Edge cases

---

## 📈 SUCCESS METRICS

### Performance Metrics
- Rule evaluation time < 100ms
- Support 1000+ active rules
- Handle 100+ concurrent evaluations
- 99.9% evaluation accuracy

### Business Metrics
- Reduced manual review time
- Faster decision-making
- Improved compliance
- Audit trail completeness

---

## 🔄 INTEGRATION POINTS

### Module Integration

**Loan Module**
- Credit policy evaluation
- Loan eligibility check
- Auto-approval decisions
- Pricing calculations

**Customer Module**
- Customer eligibility
- KYC rule validation
- Risk assessment

**Deposit Module**
- Product eligibility
- Interest rate rules
- Limit validation

**Workflow Module**
- Rule-based routing
- Auto-assignment rules
- Escalation triggers

---

## 📚 RULE EXAMPLES

### Example 1: Minimum Income Rule
```json
{
  "rule_code": "MIN_INCOME_25K",
  "rule_name": "Minimum Income ₹25,000",
  "category": "credit_policy",
  "priority": 100,
  "conditions": [{
    "field": "customer.monthly_income",
    "operator": ">=",
    "value": 25000
  }],
  "actions": [{
    "type": "reject",
    "message": "Minimum income not met"
  }]
}
```

### Example 2: Risk-Based Pricing
```json
{
  "rule_code": "RISK_BASED_RATE",
  "rule_name": "Interest Rate by Credit Score",
  "category": "pricing",
  "priority": 50,
  "conditions": [
    {
      "field": "customer.credit_score",
      "operator": "between",
      "value": [700, 750]
    }
  ],
  "actions": [{
    "type": "set_value",
    "field": "interest_rate",
    "value": 10.5
  }]
}
```

### Example 3: Auto-Approval Rule
```json
{
  "rule_code": "AUTO_APPROVE_SMALL_LOAN",
  "rule_name": "Auto Approve Small Loans",
  "category": "approval",
  "priority": 10,
  "conditions": [
    {"field": "loan.amount", "operator": "<=", "value": 50000},
    {"field": "customer.credit_score", "operator": ">", "value": 750},
    {"field": "customer.existing_loans", "operator": "=", "value": 0}
  ],
  "logical_operator": "AND",
  "actions": [{
    "type": "approve",
    "auto_disburse": true
  }]
}
```

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Foundation (Week 1)
- Database models
- Basic CRUD services
- Category management
- Rule storage

### Phase 2: Evaluation Engine (Week 2)
- Condition parser
- Expression evaluator
- Operator implementations
- Basic evaluation API

### Phase 3: Decision Management (Week 3)
- Decision logging
- Evaluation history
- Override management
- Analytics

### Phase 4: Integration (Week 4)
- Loan module integration
- Customer module integration
- API finalization
- Testing

### Phase 5: UI & Polish (Week 5)
- Rule builder UI
- Dashboard
- Documentation
- Training materials

---

## 📝 NOTES

### Design Decisions
1. **JSON-based rules**: Flexibility without schema changes
2. **Separate conditions table**: Better queryability
3. **Version history**: Complete audit trail
4. **Evaluation logging**: Compliance and debugging
5. **Multi-strategy evaluation**: Different use cases

### Future Enhancements
- Machine learning rule suggestions
- A/B testing framework
- Rule conflict detection
- Visual rule designer
- Rule marketplace/templates
- Advanced analytics

---

**Document Version**: 1.0  
**Last Updated**: July 5, 2026  
**Status**: Design Complete, Ready for Implementation  
**Estimated Implementation**: 3-4 weeks  
**Target Completion**: August 2026
