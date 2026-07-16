"""
Business Rules Engine Module
Enterprise-grade configurable rules engine with decision tables
"""
from backend.services.rules.rules_models import (
    # Enums
    RuleType,
    RuleStatus,
    ConditionOperator,
    LogicalOperator,
    ActionType,
    DataType,
    AggregationFunction,
    ExecutionMode,
    
    # Database Models
    RuleSet,
    Rule,
    Condition,
    Action,
    DecisionTable,
    DecisionTableRow,
    RuleExecution,
    RuleVersion,
    
    # Pydantic Schemas
    RuleSetCreate,
    RuleCreate,
    ConditionCreate,
    ActionCreate,
    DecisionTableCreate,
    DecisionTableRowCreate,
    ExecuteRuleRequest,
    ExecuteRuleResponse,
    TestRuleRequest,
    TestRuleResponse,
    RuleStats,
    DecisionTableLookupRequest,
    DecisionTableLookupResponse
)

from backend.services.rules.rules_service import RulesService
from backend.services.rules.rules_router import router as rules_router

__all__ = [
    # Enums
    "RuleType",
    "RuleStatus",
    "ConditionOperator",
    "LogicalOperator",
    "ActionType",
    "DataType",
    "AggregationFunction",
    "ExecutionMode",
    
    # Models
    "RuleSet",
    "Rule",
    "Condition",
    "Action",
    "DecisionTable",
    "DecisionTableRow",
    "RuleExecution",
    "RuleVersion",
    
    # Schemas
    "RuleSetCreate",
    "RuleCreate",
    "ConditionCreate",
    "ActionCreate",
    "DecisionTableCreate",
    "DecisionTableRowCreate",
    "ExecuteRuleRequest",
    "ExecuteRuleResponse",
    "TestRuleRequest",
    "TestRuleResponse",
    "RuleStats",
    "DecisionTableLookupRequest",
    "DecisionTableLookupResponse",
    
    # Service & Router
    "RulesService",
    "rules_router"
]
