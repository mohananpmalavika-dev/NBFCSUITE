"""
Business Rules Engine Pydantic Schemas

Request and response schemas for the rules engine API.
Includes validation, serialization, and type safety.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from uuid import UUID


# ==================== ENUMS ====================

class RuleType(str, Enum):
    """Types of business rules"""
    ELIGIBILITY = "eligibility"
    SCORING = "scoring"
    PRICING = "pricing"
    APPROVAL = "approval"
    RISK_ASSESSMENT = "risk_assessment"
    FRAUD_DETECTION = "fraud_detection"
    COMPLIANCE = "compliance"
    VALIDATION = "validation"


class EvaluationStrategy(str, Enum):
    """Rule evaluation strategies"""
    FIRST_MATCH = "first_match"  # Stop at first matching rule
    ALL_MATCH = "all_match"  # Evaluate all rules
    PRIORITY = "priority"  # Evaluate by priority, can stop on critical
    BEST_MATCH = "best_match"  # Evaluate all, return best result


class ConditionOperator(str, Enum):
    """Operators for rule conditions"""
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"  # Regex
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    EXISTS = "exists"


class DataType(str, Enum):
    """Data types for condition values"""
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"


class LogicalOperator(str, Enum):
    """Logical operators for combining conditions"""
    AND = "AND"
    OR = "OR"


class ActionType(str, Enum):
    """Types of rule actions"""
    APPROVE = "approve"
    REJECT = "reject"
    SET_VALUE = "set_value"
    CALCULATE = "calculate"
    TRIGGER_WORKFLOW = "trigger_workflow"
    SEND_NOTIFICATION = "send_notification"
    LOG_EVENT = "log_event"
    MANUAL_REVIEW = "manual_review"


class EvaluationResult(str, Enum):
    """Results of rule evaluation"""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


class DecisionResult(str, Enum):
    """Final decision results"""
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"
    PENDING = "pending"
    ERROR = "error"


# ==================== RULE CATEGORY SCHEMAS ====================

class RuleCategoryCreate(BaseModel):
    """Schema for creating a rule category"""
    category_code: str = Field(..., max_length=50, description="Unique category code")
    category_name: str = Field(..., max_length=200, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    parent_category_id: Optional[int] = Field(None, description="Parent category ID for hierarchy")
    is_active: bool = Field(True, description="Active status")


class RuleCategoryUpdate(BaseModel):
    """Schema for updating a rule category"""
    category_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    is_active: Optional[bool] = None


class RuleCategoryResponse(BaseModel):
    """Schema for rule category response"""
    id: int
    category_code: str
    category_name: str
    description: Optional[str]
    parent_category_id: Optional[int]
    is_active: bool
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== RULE CONDITION SCHEMAS ====================

class RuleConditionSchema(BaseModel):
    """Schema for a single rule condition"""
    field_path: str = Field(..., description="JSON path to field (e.g., customer.age)")
    operator: ConditionOperator = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Value to compare against")
    data_type: DataType = Field(..., description="Data type of value")
    is_negated: bool = Field(False, description="Negate the condition (NOT)")


class ConditionGroup(BaseModel):
    """Schema for a group of conditions"""
    group_id: int = Field(..., description="Group identifier")
    operator: LogicalOperator = Field(LogicalOperator.AND, description="Operator within group")
    conditions: List[RuleConditionSchema] = Field(..., description="Conditions in this group")


# ==================== RULE ACTION SCHEMAS ====================

class RuleActionSchema(BaseModel):
    """Schema for a rule action"""
    action_type: ActionType = Field(..., description="Type of action")
    action_config: Dict[str, Any] = Field(..., description="Action configuration")
    execution_order: int = Field(1, description="Order of execution")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "reject",
                "action_config": {
                    "message": "Age criteria not met",
                    "reason_code": "AGE_FAIL",
                    "severity": "error"
                },
                "execution_order": 1
            }
        }


# ==================== RULE DEFINITION SCHEMAS ====================

class RuleDefinition(BaseModel):
    """Complete rule definition structure"""
    conditions: Optional[List[RuleConditionSchema]] = Field(None, description="Simple conditions list")
    condition_groups: Optional[List[ConditionGroup]] = Field(None, description="Grouped conditions")
    logical_operator: LogicalOperator = Field(LogicalOperator.AND, description="Operator between conditions")
    group_operator: Optional[LogicalOperator] = Field(None, description="Operator between groups")
    actions: List[RuleActionSchema] = Field(..., description="Actions to execute")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('conditions', 'condition_groups')
    def validate_conditions_or_groups(cls, v, values):
        """Ensure either conditions or condition_groups is provided, not both"""
        if 'conditions' in values and values.get('conditions') and 'condition_groups' in values and v:
            raise ValueError("Provide either 'conditions' or 'condition_groups', not both")
        return v


# ==================== BUSINESS RULE SCHEMAS ====================

class BusinessRuleCreate(BaseModel):
    """Schema for creating a business rule"""
    rule_code: str = Field(..., max_length=100, description="Unique rule code")
    rule_name: str = Field(..., max_length=200, description="Rule name")
    category_id: int = Field(..., description="Category ID")
    rule_type: RuleType = Field(..., description="Type of rule")
    description: Optional[str] = Field(None, description="Rule description")
    priority: int = Field(100, ge=1, le=1000, description="Priority (1-1000, lower = higher)")
    rule_definition: RuleDefinition = Field(..., description="Complete rule definition")
    evaluation_strategy: EvaluationStrategy = Field(EvaluationStrategy.FIRST_MATCH, description="Evaluation strategy")
    effective_from: Optional[date] = Field(None, description="Effective start date")
    effective_to: Optional[date] = Field(None, description="Effective end date")


class BusinessRuleUpdate(BaseModel):
    """Schema for updating a business rule"""
    rule_name: Optional[str] = Field(None, max_length=200)
    category_id: Optional[int] = None
    rule_type: Optional[RuleType] = None
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=1000)
    rule_definition: Optional[RuleDefinition] = None
    evaluation_strategy: Optional[EvaluationStrategy] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class BusinessRuleResponse(BaseModel):
    """Schema for business rule response"""
    id: int
    rule_code: str
    rule_name: str
    category_id: int
    rule_type: str
    description: Optional[str]
    priority: int
    rule_definition: Dict[str, Any]
    evaluation_strategy: str
    version: int
    is_active: bool
    effective_from: Optional[date]
    effective_to: Optional[date]
    tenant_id: int
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BusinessRuleDetails(BusinessRuleResponse):
    """Extended rule details with relationships"""
    category: Optional[RuleCategoryResponse] = None
    total_evaluations: int = 0
    last_evaluated_at: Optional[datetime] = None


# ==================== RULE EVALUATION SCHEMAS ====================

class EvaluationRequest(BaseModel):
    """Schema for rule evaluation request"""
    rule_codes: Optional[List[str]] = Field(None, description="Specific rules to evaluate")
    category_code: Optional[str] = Field(None, description="Evaluate all rules in category")
    entity_type: str = Field(..., description="Type of entity being evaluated")
    entity_id: int = Field(..., description="Entity ID")
    input_data: Dict[str, Any] = Field(..., description="Data to evaluate against")
    evaluation_strategy: Optional[EvaluationStrategy] = Field(None, description="Override strategy")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category_code": "credit_policy",
                "entity_type": "loan_application",
                "entity_id": 12345,
                "input_data": {
                    "customer": {
                        "age": 35,
                        "monthly_income": 50000,
                        "credit_score": 720
                    },
                    "loan": {
                        "amount": 500000,
                        "tenure": 36
                    }
                }
            }
        }


class RuleEvaluationResult(BaseModel):
    """Result of a single rule evaluation"""
    rule_id: int
    rule_code: str
    rule_name: str
    matched: bool
    evaluation_result: EvaluationResult
    output_data: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None


class EvaluationResponse(BaseModel):
    """Schema for evaluation response"""
    evaluation_id: UUID
    entity_type: str
    entity_id: int
    total_rules_evaluated: int
    rules_matched: int
    evaluation_results: List[RuleEvaluationResult]
    overall_result: EvaluationResult
    execution_time_ms: int
    evaluated_at: datetime


# ==================== DECISION SCHEMAS ====================

class DecisionRequest(BaseModel):
    """Schema for decision request"""
    decision_type: str = Field(..., description="Type of decision")
    entity_type: str = Field(..., description="Entity type")
    entity_id: int = Field(..., description="Entity ID")
    input_data: Dict[str, Any] = Field(..., description="Input data")
    category_codes: Optional[List[str]] = Field(None, description="Categories to evaluate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_type": "credit_approval",
                "entity_type": "loan_application",
                "entity_id": 12345,
                "input_data": {
                    "customer": {"age": 35, "income": 50000},
                    "loan": {"amount": 500000}
                },
                "category_codes": ["credit_policy", "risk_assessment"]
            }
        }


class DecisionFactor(BaseModel):
    """A factor that influenced the decision"""
    factor_name: str
    factor_value: Any
    impact: str  # positive, negative, neutral
    weight: Optional[float] = None


class DecisionResponse(BaseModel):
    """Schema for decision response"""
    decision_id: UUID
    entity_type: str
    entity_id: int
    decision_type: str
    decision_result: DecisionResult
    confidence_score: Optional[float] = None
    rules_applied: List[Dict[str, Any]]
    decision_factors: List[DecisionFactor]
    recommendation: Optional[str] = None
    decided_at: datetime


class DecisionOverrideRequest(BaseModel):
    """Schema for overriding a decision"""
    new_result: DecisionResult = Field(..., description="New decision result")
    reason: str = Field(..., min_length=10, description="Reason for override")


# ==================== RULE VERSION SCHEMAS ====================

class RuleVersionResponse(BaseModel):
    """Schema for rule version response"""
    id: int
    rule_id: int
    version_number: int
    rule_snapshot: Dict[str, Any]
    change_summary: Optional[str]
    changed_by: int
    changed_at: datetime
    
    class Config:
        from_attributes = True


# ==================== VALIDATION & TESTING SCHEMAS ====================

class RuleValidationRequest(BaseModel):
    """Schema for validating a rule definition"""
    rule_definition: RuleDefinition = Field(..., description="Rule definition to validate")


class RuleValidationResponse(BaseModel):
    """Schema for validation response"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class RuleTestRequest(BaseModel):
    """Schema for testing a rule"""
    rule_id: int = Field(..., description="Rule to test")
    test_data: Dict[str, Any] = Field(..., description="Test input data")


class RuleTestResponse(BaseModel):
    """Schema for test response"""
    rule_id: int
    rule_code: str
    matched: bool
    evaluation_result: EvaluationResult
    output_data: Optional[Dict[str, Any]]
    execution_time_ms: int


# ==================== ANALYTICS SCHEMAS ====================

class RuleStatistics(BaseModel):
    """Statistics for a rule"""
    rule_id: int
    rule_code: str
    total_evaluations: int
    total_matches: int
    match_rate: float
    avg_execution_time_ms: float
    last_evaluated_at: Optional[datetime]


class CategoryStatistics(BaseModel):
    """Statistics for a category"""
    category_id: int
    category_code: str
    total_rules: int
    active_rules: int
    total_evaluations: int
    avg_execution_time_ms: float


class DecisionStatistics(BaseModel):
    """Decision statistics"""
    decision_type: str
    total_decisions: int
    approved: int
    rejected: int
    manual_review: int
    approval_rate: float
    avg_confidence_score: float


# ==================== CLONE & BULK OPERATIONS ====================

class RuleCloneRequest(BaseModel):
    """Schema for cloning a rule"""
    new_rule_code: str = Field(..., max_length=100, description="Code for cloned rule")
    new_rule_name: str = Field(..., max_length=200, description="Name for cloned rule")
    copy_version_history: bool = Field(False, description="Copy version history")


class BulkActivateRequest(BaseModel):
    """Schema for bulk activation"""
    rule_ids: List[int] = Field(..., description="Rule IDs to activate")


class BulkDeactivateRequest(BaseModel):
    """Schema for bulk deactivation"""
    rule_ids: List[int] = Field(..., description="Rule IDs to deactivate")
