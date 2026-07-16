"""
Business Rules Engine Models

Comprehensive rule models for:
- Decision rules (IF-THEN-ELSE)
- Validation rules
- Calculation rules
- Routing rules
- Pricing rules
- Eligibility rules
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class RuleType(str, Enum):
    """Rule types"""
    DECISION = "decision"
    VALIDATION = "validation"
    CALCULATION = "calculation"
    ROUTING = "routing"
    PRICING = "pricing"
    ELIGIBILITY = "eligibility"
    DECISION_TABLE = "decision_table"


class ExecutionMode(str, Enum):
    """Rule execution modes"""
    REAL_TIME = "real_time"  # Execute on every transaction
    BATCH = "batch"  # Execute at scheduled intervals
    ON_DEMAND = "on_demand"  # Execute on user trigger


class ExecutionStrategy(str, Enum):
    """Execution strategies for rule chaining"""
    STOP_ON_FIRST_FAILURE = "stop_on_first_failure"  # Stop when any rule fails
    CONTINUE_ON_FAILURE = "continue_on_failure"  # Continue even if rules fail
    COLLECT_ALL_VIOLATIONS = "collect_all_violations"  # Collect all validation errors


class RulePriority(str, Enum):
    """Rule priority levels"""
    CRITICAL = "critical"  # Priority 1000
    HIGH = "high"  # Priority 750
    MEDIUM = "medium"  # Priority 500
    LOW = "low"  # Priority 250
    LOWEST = "lowest"  # Priority 100


class OperatorType(str, Enum):
    """Comparison operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    BETWEEN = "between"
    MATCHES_REGEX = "matches_regex"


class LogicalOperator(str, Enum):
    """Logical operators for combining conditions"""
    AND = "and"
    OR = "or"
    NOT = "not"


class ActionType(str, Enum):
    """Action types"""
    SET_VALUE = "set_value"
    CALCULATE = "calculate"
    SHOW_MESSAGE = "show_message"
    SHOW_ERROR = "show_error"
    SHOW_WARNING = "show_warning"
    ROUTE_TO = "route_to"
    CALL_API = "call_api"
    SEND_EMAIL = "send_email"
    SEND_NOTIFICATION = "send_notification"
    LOG_EVENT = "log_event"
    TRIGGER_WORKFLOW = "trigger_workflow"
    STOP_EXECUTION = "stop_execution"


class FieldType(str, Enum):
    """Field data types"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"


# ==================== CONDITION MODELS ====================

class Condition(BaseModel):
    """Single condition"""
    condition_id: str
    field: str
    field_type: FieldType
    operator: OperatorType
    value: Any
    value2: Optional[Any] = None  # For BETWEEN operator
    
    # Nested field support (e.g., "customer.address.city")
    field_path: Optional[List[str]] = None


class ConditionGroup(BaseModel):
    """Group of conditions with logical operator"""
    group_id: str
    logical_operator: LogicalOperator = LogicalOperator.AND
    conditions: List[Union[Condition, 'ConditionGroup']] = []
    
    # Nesting support
    parent_group_id: Optional[str] = None


ConditionGroup.update_forward_refs()


# ==================== ACTION MODELS ====================

class Action(BaseModel):
    """Action to execute"""
    action_id: str
    action_type: ActionType
    
    # For SET_VALUE
    target_field: Optional[str] = None
    target_value: Any = None
    
    # For CALCULATE
    formula: Optional[str] = None
    formula_fields: Optional[List[str]] = None
    
    # For messages
    message: Optional[str] = None
    message_type: Optional[str] = None  # info, warning, error, success
    
    # For routing
    route_to: Optional[str] = None
    route_params: Optional[Dict[str, Any]] = None
    
    # For API calls
    api_url: Optional[str] = None
    api_method: Optional[str] = None
    api_headers: Optional[Dict[str, str]] = None
    api_body: Optional[Dict[str, Any]] = None
    
    # For email/notification
    recipients: Optional[List[str]] = None
    template_id: Optional[str] = None
    template_vars: Optional[Dict[str, Any]] = None
    
    # For workflow
    workflow_id: Optional[str] = None
    workflow_params: Optional[Dict[str, Any]] = None
    
    # Action order
    order: int = 0


# ==================== RULE MODELS ====================

class DecisionRule(BaseModel):
    """Decision rule (IF-THEN-ELSE)"""
    rule_id: str
    rule_name: str
    description: Optional[str] = None
    
    # Conditions
    if_condition: ConditionGroup
    
    # Actions
    then_actions: List[Action]
    else_actions: Optional[List[Action]] = []
    
    # Execution priority
    priority: int = 500  # Default medium priority
    priority_level: RulePriority = RulePriority.MEDIUM
    
    # Metadata
    is_active: bool = True
    tags: List[str] = []


class ValidationRule(BaseModel):
    """Validation rule"""
    rule_id: str
    rule_name: str
    description: Optional[str] = None
    
    # Validation conditions
    conditions: ConditionGroup
    
    # Error handling
    error_message: str
    error_field: Optional[str] = None
    severity: str = "error"  # error, warning, info
    
    # Execution priority
    priority: int = 500  # Default medium priority
    priority_level: RulePriority = RulePriority.MEDIUM
    
    # Metadata
    is_active: bool = True
    stop_on_error: bool = True
    tags: List[str] = []


class CalculationRule(BaseModel):
    """Calculation rule"""
    rule_id: str
    rule_name: str
    description: Optional[str] = None
    
    # Calculation
    target_field: str
    formula: str
    formula_fields: List[str]
    
    # Conditions (optional - calculate only if conditions met)
    conditions: Optional[ConditionGroup] = None
    
    # Rounding
    decimal_places: Optional[int] = None
    rounding_mode: str = "round"  # round, floor, ceil
    
    # Execution priority
    priority: int = 500  # Default medium priority
    priority_level: RulePriority = RulePriority.MEDIUM
    
    # Metadata
    is_active: bool = True
    tags: List[str] = []


class RoutingRule(BaseModel):
    """Routing rule"""
    rule_id: str
    rule_name: str
    description: Optional[str] = None
    
    # Routing conditions and destinations
    routes: List[Dict[str, Any]]  # [{conditions, destination, priority}]
    default_route: Optional[str] = None
    
    # Execution priority
    priority: int = 500  # Default medium priority
    priority_level: RulePriority = RulePriority.MEDIUM
    
    # Metadata
    is_active: bool = True
    tags: List[str] = []


class PricingRule(BaseModel):
    """Pricing rule"""
    rule_id: str
    rule_name: str
    description: Optional[str] = None
    
    # Base price
    base_price_field: str
    
    # Pricing tiers
    tiers: List[Dict[str, Any]]  # [{conditions, multiplier, addition}]
    
    # Discounts
    discounts: Optional[List[Dict[str, Any]]] = []
    
    # Surcharges
    surcharges: Optional[List[Dict[str, Any]]] = []
    
    # Final calculation
    final_formula: Optional[str] = None
    
    # Execution priority
    priority: int = 500  # Default medium priority
    priority_level: RulePriority = RulePriority.MEDIUM
    
    # Metadata
    is_active: bool = True
    tags: List[str] = []


class EligibilityRule(BaseModel):
    """Eligibility rule"""
    rule_id: str
    rule_name: str
    description: Optional[str] = None
    
    # Eligibility criteria
    criteria: List[ConditionGroup]
    all_must_pass: bool = True  # AND vs OR logic
    
    # Scoring (optional)
    scoring_enabled: bool = False
    criteria_scores: Optional[Dict[str, int]] = None
    minimum_score: Optional[int] = None
    
    # Result
    eligible_message: Optional[str] = None
    ineligible_message: Optional[str] = None
    
    # Execution priority
    priority: int = 500  # Default medium priority
    priority_level: RulePriority = RulePriority.MEDIUM
    
    # Metadata
    is_active: bool = True
    tags: List[str] = []


# ==================== DECISION TABLE MODELS ====================

class TableColumnType(str, Enum):
    """Decision table column types"""
    INPUT = "input"  # Input column (condition)
    OUTPUT = "output"  # Output column (result)


class TableColumn(BaseModel):
    """Decision table column definition"""
    column_id: str
    column_name: str
    column_type: TableColumnType
    field_name: str  # Field in data to match/set
    field_type: FieldType
    
    # For INPUT columns
    operator: Optional[OperatorType] = OperatorType.EQUALS
    
    # Display
    display_order: int = 0
    width: Optional[int] = None  # Column width in pixels
    
    # Metadata
    description: Optional[str] = None
    is_required: bool = True


class TableCell(BaseModel):
    """Decision table cell value"""
    column_id: str
    value: Any
    
    # For range values (e.g., "750-900", ">1000", "50K-1L")
    value_min: Optional[Any] = None
    value_max: Optional[Any] = None
    is_range: bool = False
    
    # Special values
    is_any: bool = False  # Matches any value (wildcard)
    is_reject: bool = False  # Special reject value


class TableRow(BaseModel):
    """Decision table row"""
    row_id: str
    cells: List[TableCell]
    
    # Row order (priority)
    row_order: int = 0
    
    # Conditions
    is_active: bool = True
    is_default: bool = False  # Default/fallback row
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = []


class DecisionTable(BaseModel):
    """Decision table rule"""
    table_id: str
    table_name: str
    description: Optional[str] = None
    
    # Table structure
    columns: List[TableColumn]
    rows: List[TableRow]
    
    # Matching behavior
    match_first: bool = True  # Return first match or collect all
    match_all_inputs: bool = True  # All input columns must match
    
    # Default values for output columns when no match
    default_values: Optional[Dict[str, Any]] = None
    
    # Actions on match
    on_match_actions: Optional[List[Action]] = []
    on_no_match_actions: Optional[List[Action]] = []
    
    # Metadata
    is_active: bool = True
    version: str = "1.0"
    tags: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DecisionTableMatchResult(BaseModel):
    """Result of decision table evaluation"""
    matched: bool
    matched_row_ids: List[str]
    output_values: Dict[str, Any]  # Field name -> value
    match_count: int
    is_default: bool = False  # Whether default row was used


# ==================== RULE SET MODELS ====================

class RuleSet(BaseModel):
    """Collection of rules"""
    ruleset_id: str
    ruleset_name: str
    description: Optional[str] = None
    
    # Rules
    decision_rules: List[DecisionRule] = []
    validation_rules: List[ValidationRule] = []
    calculation_rules: List[CalculationRule] = []
    routing_rules: List[RoutingRule] = []
    pricing_rules: List[PricingRule] = []
    eligibility_rules: List[EligibilityRule] = []
    decision_tables: List[DecisionTable] = []
    
    # Execution
    execution_order: List[str] = []  # Rule IDs in order
    stop_on_first_match: bool = False
    
    # Execution Engine Configuration
    execution_config: Optional[ExecutionEngineConfig] = None
    
    # Context
    entity_type: str
    applicable_to: Optional[List[str]] = None
    
    # Metadata
    version: str = "1.0"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None


# ==================== EXECUTION ENGINE MODELS ====================

class BatchSchedule(BaseModel):
    """Batch execution schedule configuration"""
    schedule_id: str
    schedule_name: str
    ruleset_id: str
    
    # Schedule configuration
    cron_expression: str  # e.g., "0 0 * * *" for daily at midnight
    timezone: str = "UTC"
    
    # Execution settings
    enabled: bool = True
    max_execution_time_seconds: int = 300  # 5 minutes default
    
    # Data source
    data_source_type: str  # database, api, file
    data_source_config: Dict[str, Any]
    
    # Batch processing
    batch_size: int = 100
    parallel_execution: bool = False
    max_parallel_threads: int = 5
    
    # Notifications
    notify_on_completion: bool = False
    notify_on_failure: bool = True
    notification_emails: List[str] = []
    
    # Metadata
    last_execution_at: Optional[datetime] = None
    last_execution_status: Optional[str] = None
    next_execution_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None


class RuleChainStep(BaseModel):
    """Single step in rule chain"""
    step_id: str
    step_name: str
    step_order: int
    
    # Rule reference
    rule_id: str
    rule_type: RuleType
    
    # Execution control
    is_active: bool = True
    skip_on_condition: Optional[str] = None  # Formula to skip this step
    
    # Pass-through configuration
    pass_output_to_next: bool = True
    output_field_mappings: Optional[Dict[str, str]] = None  # Map output fields to next step inputs
    
    # Error handling
    stop_on_failure: bool = True
    failure_action: Optional[str] = None  # "skip_remaining", "continue", "retry"
    max_retries: int = 0
    retry_delay_seconds: int = 0
    
    # Metadata
    description: Optional[str] = None


class RuleChain(BaseModel):
    """Chain of rules to execute in sequence"""
    chain_id: str
    chain_name: str
    description: Optional[str] = None
    
    # Chain steps
    steps: List[RuleChainStep]
    
    # Execution strategy
    execution_strategy: ExecutionStrategy = ExecutionStrategy.STOP_ON_FIRST_FAILURE
    
    # Input/Output
    required_inputs: List[str] = []  # Required input fields
    expected_outputs: List[str] = []  # Expected output fields
    
    # Execution context
    share_context: bool = True  # Share execution context across steps
    initial_context: Optional[Dict[str, Any]] = None
    
    # Metadata
    is_active: bool = True
    version: str = "1.0"
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    tags: List[str] = []


class ExecutionEngineConfig(BaseModel):
    """Execution engine configuration"""
    config_id: str
    config_name: str
    
    # Execution mode
    execution_mode: ExecutionMode = ExecutionMode.ON_DEMAND
    
    # Real-time configuration
    trigger_events: Optional[List[str]] = []  # Events that trigger execution
    trigger_conditions: Optional[Dict[str, Any]] = None
    
    # Batch configuration
    batch_schedule: Optional[BatchSchedule] = None
    
    # Priority configuration
    enable_priority_execution: bool = False
    priority_rules: Optional[Dict[str, int]] = None  # rule_id -> priority number
    
    # Chaining configuration
    enable_rule_chaining: bool = False
    rule_chains: List[RuleChain] = []
    
    # Performance settings
    max_execution_time_seconds: int = 60
    enable_caching: bool = False
    cache_ttl_seconds: int = 300
    
    # Monitoring
    enable_execution_logging: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    enable_metrics: bool = False
    
    # Metadata
    ruleset_id: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ExecutionHistory(BaseModel):
    """History record of rule execution"""
    history_id: str
    execution_id: str
    ruleset_id: str
    
    # Execution details
    execution_mode: ExecutionMode
    execution_type: str  # "single", "batch", "chain"
    
    # Timing
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_ms: float = 0
    
    # Results
    status: str  # "success", "failure", "partial", "timeout"
    rules_executed_count: int = 0
    rules_passed_count: int = 0
    rules_failed_count: int = 0
    
    # Data
    input_data_sample: Optional[Dict[str, Any]] = None
    output_data_sample: Optional[Dict[str, Any]] = None
    
    # Errors
    error_count: int = 0
    error_summary: Optional[str] = None
    
    # Context
    tenant_id: int
    user_id: Optional[int] = None
    triggered_by: Optional[str] = None  # "user", "schedule", "event", "api"
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None


class RuleChainExecutionResult(BaseModel):
    """Result of rule chain execution"""
    chain_id: str
    chain_name: str
    execution_id: str
    
    # Overall results
    success: bool
    steps_completed: int
    steps_failed: int
    steps_skipped: int
    
    # Step results
    step_results: List[Dict[str, Any]] = []  # [{step_id, step_name, success, output, errors}]
    
    # Final output
    final_output: Dict[str, Any]
    
    # Execution details
    execution_strategy: ExecutionStrategy
    stopped_early: bool = False
    stop_reason: Optional[str] = None
    
    # Timing
    execution_time_ms: float
    executed_at: datetime
    
    # Logs
    execution_log: List[str] = []


# ==================== EXECUTION MODELS ====================

class RuleExecutionContext(BaseModel):
    """Context for rule execution"""
    context_id: str
    entity_type: str
    entity_id: Optional[int] = None
    
    # Input data
    data: Dict[str, Any]
    
    # User context
    user_id: Optional[int] = None
    tenant_id: int
    
    # Additional context
    metadata: Optional[Dict[str, Any]] = None


class RuleExecutionResult(BaseModel):
    """Result of rule execution"""
    execution_id: str
    ruleset_id: str
    context_id: str
    
    # Results
    success: bool
    rules_executed: List[str]
    rules_matched: List[str]
    
    # Actions performed
    actions_executed: List[Dict[str, Any]]
    
    # Validation results
    validation_errors: List[Dict[str, str]] = []
    validation_warnings: List[Dict[str, str]] = []
    
    # Calculated values
    calculated_fields: Dict[str, Any] = {}
    
    # Routing
    route_destination: Optional[str] = None
    
    # Eligibility
    is_eligible: Optional[bool] = None
    eligibility_score: Optional[int] = None
    
    # Output data (modified)
    output_data: Dict[str, Any]
    
    # Execution metrics
    execution_time_ms: float
    executed_at: datetime
    
    # Logs
    execution_log: List[str] = []


# ==================== RULE TEMPLATE MODELS ====================

class RuleTemplate(BaseModel):
    """Pre-built rule template"""
    template_id: str
    template_name: str
    description: str
    rule_type: RuleType
    
    # Template structure
    template_structure: Dict[str, Any]
    
    # Configurable parameters
    parameters: List[Dict[str, Any]]
    
    # Category
    category: str
    industry: Optional[str] = None
    
    # Usage
    use_cases: List[str] = []
    example: Optional[str] = None


# ==================== FORMULA MODELS ====================

# ==================== RULE MANAGEMENT MODELS ====================

class VersionStatus(str, Enum):
    """Version status"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ChangeType(str, Enum):
    """Type of change in version"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    RESTORED = "restored"


class RuleVersion(BaseModel):
    """Rule version record"""
    version_id: str
    ruleset_id: str
    version_number: str  # e.g., "1.0", "1.1", "2.0"
    version_name: Optional[str] = None
    
    # Version content
    ruleset_data: Dict[str, Any]  # Complete ruleset snapshot
    
    # Version metadata
    status: VersionStatus = VersionStatus.DRAFT
    is_current: bool = False
    
    # Activation
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    
    # Change tracking
    change_type: ChangeType
    change_summary: Optional[str] = None
    changed_by: Optional[int] = None
    changed_at: datetime
    
    # Parent version
    parent_version_id: Optional[str] = None
    
    # Tags and categorization
    tags: List[str] = []
    notes: Optional[str] = None


class VersionComparison(BaseModel):
    """Comparison between two versions"""
    version1_id: str
    version1_number: str
    version2_id: str
    version2_number: str
    
    # Differences
    added_rules: List[Dict[str, Any]] = []
    modified_rules: List[Dict[str, Any]] = []
    deleted_rules: List[Dict[str, Any]] = []
    
    # Summary
    total_changes: int
    rules_added_count: int
    rules_modified_count: int
    rules_deleted_count: int
    
    # Detailed changes
    field_changes: List[Dict[str, Any]] = []
    
    # Comparison metadata
    compared_at: datetime
    compared_by: Optional[int] = None


class RuleTestCase(BaseModel):
    """Test case for rule testing"""
    test_case_id: str
    test_case_name: str
    description: Optional[str] = None
    
    # Test data
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]] = None
    
    # Test configuration
    ruleset_id: str
    version_id: Optional[str] = None
    
    # Test type
    test_type: str = "unit"  # unit, integration, regression
    
    # Assertions
    assertions: List[Dict[str, Any]] = []
    
    # Tags
    tags: List[str] = []
    
    # Metadata
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None


class RuleTestResult(BaseModel):
    """Result of rule test execution"""
    test_result_id: str
    test_case_id: str
    ruleset_id: str
    version_id: Optional[str] = None
    
    # Execution details
    execution_mode: str = "dry_run"  # dry_run, what_if, impact_assessment
    
    # Results
    passed: bool
    execution_result: RuleExecutionResult
    
    # Assertions results
    assertions_passed: int = 0
    assertions_failed: int = 0
    assertion_details: List[Dict[str, Any]] = []
    
    # Performance
    execution_time_ms: float
    
    # Comparison with expected
    matches_expected: Optional[bool] = None
    output_diff: Optional[Dict[str, Any]] = None
    
    # Metadata
    executed_at: datetime
    executed_by: Optional[int] = None


class ImpactAssessment(BaseModel):
    """Impact assessment for rule changes"""
    assessment_id: str
    ruleset_id: str
    version_id: str
    
    # Assessment type
    assessment_type: str = "before_activation"
    
    # Sample data
    sample_size: int
    sample_data: List[Dict[str, Any]]
    
    # Current vs New results
    current_results: List[Dict[str, Any]]
    new_results: List[Dict[str, Any]]
    
    # Impact summary
    affected_count: int
    affected_percentage: float
    
    # Change details
    result_changes: List[Dict[str, Any]] = []
    output_differences: List[Dict[str, Any]] = []
    
    # Risk analysis
    risk_level: str = "low"  # low, medium, high, critical
    risk_factors: List[str] = []
    recommendations: List[str] = []
    
    # Metadata
    assessed_at: datetime
    assessed_by: Optional[int] = None


class RuleTemplate(BaseModel):
    """Rule template from library"""
    template_id: str
    template_name: str
    description: str
    
    # Template category
    category: str  # validation, calculation, decision, etc.
    industry: Optional[str] = None  # banking, lending, insurance, etc.
    
    # Template content
    rule_type: RuleType
    template_structure: Dict[str, Any]
    
    # Customization
    customizable_fields: List[str] = []
    required_fields: List[str] = []
    
    # Usage
    use_cases: List[str] = []
    example: Optional[str] = None
    
    # Compliance
    compliance_tags: List[str] = []  # RBI, SEBI, etc.
    regulation_reference: Optional[str] = None
    
    # Metadata
    is_official: bool = False  # Official template vs user-created
    is_public: bool = True
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    usage_count: int = 0
    rating: Optional[float] = None


class RuleClone(BaseModel):
    """Clone operation record"""
    clone_id: str
    source_rule_id: str
    source_ruleset_id: str
    target_rule_id: str
    target_ruleset_id: str
    
    # Clone configuration
    clone_type: str = "full"  # full, structure_only, template
    customizations: Optional[Dict[str, Any]] = None
    
    # Metadata
    cloned_by: Optional[int] = None
    cloned_at: datetime


class AuditTrail(BaseModel):
    """Audit trail entry for rule changes"""
    audit_id: str
    entity_type: str  # ruleset, rule, version, etc.
    entity_id: str
    
    # Action
    action: str  # create, update, delete, activate, deactivate
    action_details: Optional[str] = None
    
    # Changes
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    changed_fields: List[str] = []
    
    # Context
    user_id: Optional[int] = None
    tenant_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Metadata
    timestamp: datetime
    session_id: Optional[str] = None


class FormulaFunction(BaseModel):
    """Available formula functions"""
    function_name: str
    description: str
    syntax: str
    parameters: List[Dict[str, str]]
    return_type: str
    example: str
    category: str


# Built-in formula functions
FORMULA_FUNCTIONS = [
    FormulaFunction(
        function_name="SUM",
        description="Sum of values",
        syntax="SUM(field1, field2, ...)",
        parameters=[{"name": "values", "type": "number[]", "description": "Values to sum"}],
        return_type="number",
        example="SUM(price, tax, fees)",
        category="Math"
    ),
    FormulaFunction(
        function_name="AVG",
        description="Average of values",
        syntax="AVG(field1, field2, ...)",
        parameters=[{"name": "values", "type": "number[]", "description": "Values to average"}],
        return_type="number",
        example="AVG(score1, score2, score3)",
        category="Math"
    ),
    FormulaFunction(
        function_name="MIN",
        description="Minimum value",
        syntax="MIN(field1, field2, ...)",
        parameters=[{"name": "values", "type": "number[]", "description": "Values to compare"}],
        return_type="number",
        example="MIN(price1, price2)",
        category="Math"
    ),
    FormulaFunction(
        function_name="MAX",
        description="Maximum value",
        syntax="MAX(field1, field2, ...)",
        parameters=[{"name": "values", "type": "number[]", "description": "Values to compare"}],
        return_type="number",
        example="MAX(price1, price2)",
        category="Math"
    ),
    FormulaFunction(
        function_name="IF",
        description="Conditional expression",
        syntax="IF(condition, true_value, false_value)",
        parameters=[
            {"name": "condition", "type": "boolean", "description": "Condition to evaluate"},
            {"name": "true_value", "type": "any", "description": "Value if true"},
            {"name": "false_value", "type": "any", "description": "Value if false"}
        ],
        return_type="any",
        example="IF(amount > 1000, 0.1, 0.05)",
        category="Logical"
    ),
    FormulaFunction(
        function_name="ROUND",
        description="Round to decimal places",
        syntax="ROUND(value, decimals)",
        parameters=[
            {"name": "value", "type": "number", "description": "Value to round"},
            {"name": "decimals", "type": "number", "description": "Decimal places"}
        ],
        return_type="number",
        example="ROUND(price * 1.18, 2)",
        category="Math"
    ),
]
