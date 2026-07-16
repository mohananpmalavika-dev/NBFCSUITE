"""
Business Rules Engine Models
Enterprise-grade configurable rules engine with decision tables
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from backend.core.database import Base


# =====================================================================
# ENUMS
# =====================================================================

class RuleType(str, Enum):
    """Rule types"""
    DECISION = "DECISION"              # IF-THEN-ELSE logic
    VALIDATION = "VALIDATION"          # Data quality checks
    CALCULATION = "CALCULATION"        # Formula-based computation
    ROUTING = "ROUTING"                # Workflow routing logic
    PRICING = "PRICING"                # Dynamic pricing
    ELIGIBILITY = "ELIGIBILITY"        # Qualification checks
    SCORING = "SCORING"                # Score calculation
    DERIVATION = "DERIVATION"          # Derive new values


class RuleStatus(str, Enum):
    """Rule execution status"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
    TESTING = "TESTING"


class ConditionOperator(str, Enum):
    """Condition operators for rule evaluation"""
    EQUALS = "EQUALS"                  # ==
    NOT_EQUALS = "NOT_EQUALS"          # !=
    GREATER_THAN = "GREATER_THAN"      # >
    GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"  # >=
    LESS_THAN = "LESS_THAN"            # <
    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"        # <=
    IN = "IN"                          # in list
    NOT_IN = "NOT_IN"                  # not in list
    CONTAINS = "CONTAINS"              # string contains
    NOT_CONTAINS = "NOT_CONTAINS"      # string not contains
    STARTS_WITH = "STARTS_WITH"        # string starts with
    ENDS_WITH = "ENDS_WITH"            # string ends with
    BETWEEN = "BETWEEN"                # between range
    IS_NULL = "IS_NULL"                # is null
    IS_NOT_NULL = "IS_NOT_NULL"        # is not null
    MATCHES_REGEX = "MATCHES_REGEX"    # regex pattern match



class LogicalOperator(str, Enum):
    """Logical operators for combining conditions"""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class ActionType(str, Enum):
    """Action types for rule execution"""
    SET_VALUE = "SET_VALUE"            # Set a variable value
    CALCULATE = "CALCULATE"            # Perform calculation
    CALL_API = "CALL_API"              # Call external API
    SEND_NOTIFICATION = "SEND_NOTIFICATION"  # Send email/SMS
    TRIGGER_WORKFLOW = "TRIGGER_WORKFLOW"    # Start workflow
    LOG_EVENT = "LOG_EVENT"            # Log to audit trail
    RAISE_ALERT = "RAISE_ALERT"        # Raise alert
    STOP_EXECUTION = "STOP_EXECUTION"  # Stop rule execution
    EXECUTE_SCRIPT = "EXECUTE_SCRIPT"  # Run custom script


class DataType(str, Enum):
    """Data types for rule variables"""
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    DATETIME = "DATETIME"
    LIST = "LIST"
    OBJECT = "OBJECT"


class AggregationFunction(str, Enum):
    """Aggregation functions for rule calculations"""
    SUM = "SUM"
    AVERAGE = "AVERAGE"
    MIN = "MIN"
    MAX = "MAX"
    COUNT = "COUNT"
    MEDIAN = "MEDIAN"


class ExecutionMode(str, Enum):
    """Rule execution modes"""
    REAL_TIME = "REAL_TIME"            # Execute immediately
    BATCH = "BATCH"                    # Execute in batch
    ON_DEMAND = "ON_DEMAND"            # Execute on trigger


# =====================================================================
# DATABASE MODELS
# =====================================================================

class RuleSet(Base):
    """Container for related rules"""
    __tablename__ = "rule_sets"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(100))
    version = Column(String(20), default="1.0")
    
    # Status
    status = Column(SQLEnum(RuleStatus), default=RuleStatus.DRAFT)
    is_active = Column(Boolean, default=False)
    
    # Execution configuration
    execution_mode = Column(SQLEnum(ExecutionMode), default=ExecutionMode.REAL_TIME)
    priority = Column(Integer, default=5)  # 1-10, higher = more priority
    
    # Effective dates
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)
    
    # Relationships
    rules = relationship("Rule", back_populates="rule_set", cascade="all, delete-orphan")
    decision_tables = relationship("DecisionTable", back_populates="rule_set", cascade="all, delete-orphan")
    executions = relationship("RuleExecution", back_populates="rule_set")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))
    updated_by = Column(PGUUID(as_uuid=True))



class Rule(Base):
    """Individual rule definition"""
    __tablename__ = "rules"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_set_id = Column(PGUUID(as_uuid=True), ForeignKey("rule_sets.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    rule_type = Column(SQLEnum(RuleType), nullable=False)
    
    # Execution configuration
    priority = Column(Integer, default=5)  # Within rule set
    is_active = Column(Boolean, default=True)
    execution_order = Column(Integer)  # Order within rule set
    
    # Rule logic
    logical_operator = Column(SQLEnum(LogicalOperator), default=LogicalOperator.AND)
    
    # Stop on first match
    stop_on_match = Column(Boolean, default=False)
    
    # Error handling
    continue_on_error = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Metadata
    tags = Column(JSON)  # List of tags
    custom_properties = Column(JSON)  # Additional properties
    
    # Relationships
    rule_set = relationship("RuleSet", back_populates="rules")
    conditions = relationship("Condition", back_populates="rule", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="rule", cascade="all, delete-orphan")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Condition(Base):
    """Condition for rule evaluation"""
    __tablename__ = "conditions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_id = Column(PGUUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Parent condition (for nested conditions)
    parent_condition_id = Column(PGUUID(as_uuid=True), ForeignKey("conditions.id"))
    
    # Condition configuration
    condition_group = Column(String(50))  # Group name for UI
    condition_order = Column(Integer, default=0)
    
    # Condition logic
    field_name = Column(String(255), nullable=False)  # Variable/field to check
    field_type = Column(SQLEnum(DataType), default=DataType.STRING)
    operator = Column(SQLEnum(ConditionOperator), nullable=False)
    
    # Comparison value
    value = Column(Text)  # Single value
    value_list = Column(JSON)  # List of values for IN/NOT_IN
    value_from = Column(Text)  # Range start for BETWEEN
    value_to = Column(Text)  # Range end for BETWEEN
    
    # Dynamic value reference
    is_dynamic = Column(Boolean, default=False)  # Value from another field
    dynamic_field_name = Column(String(255))  # Field name for dynamic value
    
    # Expression evaluation
    expression = Column(Text)  # Custom expression
    
    # Logical operator with next condition
    logical_operator = Column(SQLEnum(LogicalOperator), default=LogicalOperator.AND)
    
    # Relationships
    rule = relationship("Rule", back_populates="conditions")
    child_conditions = relationship("Condition", backref="parent_condition", remote_side=[id])
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)



class Action(Base):
    """Action to execute when rule matches"""
    __tablename__ = "actions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_id = Column(PGUUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Action configuration
    action_type = Column(SQLEnum(ActionType), nullable=False)
    action_order = Column(Integer, default=0)  # Order of execution
    
    # Action parameters
    target_field = Column(String(255))  # Field to set/update
    value = Column(Text)  # Static value
    expression = Column(Text)  # Expression to evaluate
    
    # Calculation configuration
    calculation_formula = Column(Text)  # Formula for CALCULATE
    aggregation_function = Column(SQLEnum(AggregationFunction))
    
    # API call configuration
    api_endpoint = Column(String(500))
    api_method = Column(String(10))  # GET, POST, etc.
    api_headers = Column(JSON)
    api_body = Column(JSON)
    
    # Notification configuration
    notification_template = Column(String(255))
    notification_recipients = Column(JSON)  # List of recipients
    notification_subject = Column(String(500))
    notification_body = Column(Text)
    
    # Workflow configuration
    workflow_template_id = Column(PGUUID(as_uuid=True))
    workflow_variables = Column(JSON)
    
    # Script configuration
    script_language = Column(String(50))  # python, javascript
    script_content = Column(Text)
    
    # Alert configuration
    alert_severity = Column(String(50))  # LOW, MEDIUM, HIGH, CRITICAL
    alert_message = Column(Text)
    
    # Conditional execution
    execute_if_condition = Column(Text)  # Execute action only if this is true
    
    # Relationships
    rule = relationship("Rule", back_populates="actions")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class DecisionTable(Base):
    """Decision table for tabular rule configuration"""
    __tablename__ = "decision_tables"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_set_id = Column(PGUUID(as_uuid=True), ForeignKey("rule_sets.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Table configuration
    input_columns = Column(JSON, nullable=False)  # List of input column definitions
    output_columns = Column(JSON, nullable=False)  # List of output column definitions
    
    # Hit policy (how to handle multiple matches)
    hit_policy = Column(String(20), default="FIRST")  # FIRST, ANY, PRIORITY, COLLECT
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    rule_set = relationship("RuleSet", back_populates="decision_tables")
    rows = relationship("DecisionTableRow", back_populates="decision_table", cascade="all, delete-orphan")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class DecisionTableRow(Base):
    """Row in decision table"""
    __tablename__ = "decision_table_rows"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_table_id = Column(PGUUID(as_uuid=True), ForeignKey("decision_tables.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Row configuration
    row_number = Column(Integer, nullable=False)  # Order in table
    priority = Column(Integer, default=5)  # Priority if multiple matches
    
    # Input values (conditions)
    input_values = Column(JSON, nullable=False)  # Dict of column_name: value
    
    # Output values (results)
    output_values = Column(JSON, nullable=False)  # Dict of column_name: value
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Description
    description = Column(Text)
    
    # Relationships
    decision_table = relationship("DecisionTable", back_populates="rows")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class RuleExecution(Base):
    """Rule execution tracking"""
    __tablename__ = "rule_executions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_set_id = Column(PGUUID(as_uuid=True), ForeignKey("rule_sets.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Execution context
    execution_context = Column(String(255))  # What triggered the execution
    business_key = Column(String(255), index=True)  # Reference to business entity
    
    # Input/Output
    input_data = Column(JSON)  # Input variables
    output_data = Column(JSON)  # Output variables
    
    # Execution details
    rules_evaluated = Column(Integer, default=0)  # Number of rules evaluated
    rules_matched = Column(Integer, default=0)  # Number of rules matched
    actions_executed = Column(Integer, default=0)  # Number of actions executed
    
    # Matched rules
    matched_rules = Column(JSON)  # List of rule IDs that matched
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    execution_time_ms = Column(Integer)  # Execution time in milliseconds
    
    # Status
    status = Column(String(50))  # SUCCESS, FAILURE, PARTIAL
    error_message = Column(Text)
    
    # Relationships
    rule_set = relationship("RuleSet", back_populates="executions")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class RuleVersion(Base):
    """Rule version tracking"""
    __tablename__ = "rule_versions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_set_id = Column(PGUUID(as_uuid=True), ForeignKey("rule_sets.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Version info
    version_number = Column(String(20), nullable=False)
    version_name = Column(String(255))
    description = Column(Text)
    
    # Version content
    rule_set_snapshot = Column(JSON, nullable=False)  # Full rule set JSON
    
    # Status
    is_current = Column(Boolean, default=False)
    
    # Metadata
    change_summary = Column(Text)
    tags = Column(JSON)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))



# =====================================================================
# PYDANTIC SCHEMAS (for API validation)
# =====================================================================

class RuleSetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    category: Optional[str] = None
    version: str = "1.0"
    execution_mode: ExecutionMode = ExecutionMode.REAL_TIME
    priority: int = Field(default=5, ge=1, le=10)
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None


class ConditionCreate(BaseModel):
    condition_group: Optional[str] = None
    condition_order: int = 0
    field_name: str = Field(..., min_length=1)
    field_type: DataType = DataType.STRING
    operator: ConditionOperator
    value: Optional[str] = None
    value_list: Optional[List[Any]] = None
    value_from: Optional[str] = None
    value_to: Optional[str] = None
    is_dynamic: bool = False
    dynamic_field_name: Optional[str] = None
    expression: Optional[str] = None
    logical_operator: LogicalOperator = LogicalOperator.AND


class ActionCreate(BaseModel):
    action_type: ActionType
    action_order: int = 0
    target_field: Optional[str] = None
    value: Optional[str] = None
    expression: Optional[str] = None
    calculation_formula: Optional[str] = None
    aggregation_function: Optional[AggregationFunction] = None
    api_endpoint: Optional[str] = None
    api_method: Optional[str] = None
    api_headers: Optional[Dict[str, Any]] = None
    api_body: Optional[Dict[str, Any]] = None
    notification_template: Optional[str] = None
    notification_recipients: Optional[List[str]] = None
    notification_subject: Optional[str] = None
    notification_body: Optional[str] = None
    workflow_template_id: Optional[UUID] = None
    workflow_variables: Optional[Dict[str, Any]] = None
    script_language: Optional[str] = None
    script_content: Optional[str] = None
    alert_severity: Optional[str] = None
    alert_message: Optional[str] = None
    execute_if_condition: Optional[str] = None


class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    rule_type: RuleType
    priority: int = Field(default=5, ge=1, le=10)
    execution_order: Optional[int] = None
    logical_operator: LogicalOperator = LogicalOperator.AND
    stop_on_match: bool = False
    continue_on_error: bool = True
    tags: Optional[List[str]] = None
    conditions: Optional[List[ConditionCreate]] = None
    actions: Optional[List[ActionCreate]] = None


class DecisionTableCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    input_columns: List[Dict[str, Any]] = Field(..., min_items=1)
    output_columns: List[Dict[str, Any]] = Field(..., min_items=1)
    hit_policy: str = "FIRST"


class DecisionTableRowCreate(BaseModel):
    row_number: int = Field(..., ge=1)
    priority: int = Field(default=5, ge=1, le=10)
    input_values: Dict[str, Any]
    output_values: Dict[str, Any]
    description: Optional[str] = None


class ExecuteRuleRequest(BaseModel):
    rule_set_id: UUID
    input_data: Dict[str, Any]
    execution_context: Optional[str] = None
    business_key: Optional[str] = None


class ExecuteRuleResponse(BaseModel):
    execution_id: str
    status: str
    output_data: Dict[str, Any]
    rules_evaluated: int
    rules_matched: int
    actions_executed: int
    matched_rules: List[str]
    execution_time_ms: int
    error_message: Optional[str] = None


class TestRuleRequest(BaseModel):
    input_data: Dict[str, Any]


class TestRuleResponse(BaseModel):
    matched: bool
    conditions_met: List[str]
    conditions_failed: List[str]
    actions_to_execute: List[Dict[str, Any]]
    output_data: Dict[str, Any]


class RuleStats(BaseModel):
    total_rule_sets: int
    active_rule_sets: int
    total_rules: int
    total_executions: int
    avg_execution_time_ms: float
    success_rate: float


class DecisionTableLookupRequest(BaseModel):
    decision_table_id: UUID
    input_values: Dict[str, Any]


class DecisionTableLookupResponse(BaseModel):
    matched: bool
    matched_rows: List[Dict[str, Any]]
    output_values: Dict[str, Any]
