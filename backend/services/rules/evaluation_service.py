"""
Rule Evaluation Service

Core evaluation engine for business rules including:
- Condition parsing and evaluation
- Operator implementations
- Expression evaluation
- Multiple evaluation strategies
- Performance optimization
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
import json
import re
import time
import uuid

from backend.shared.database.rules_models import (
    BusinessRule,
    RuleCondition,
    RuleAction,
    RuleEvaluation
)
from backend.shared.common.response import CustomException
from .schemas import (
    EvaluationRequest,
    EvaluationStrategy,
    ConditionOperator,
    DataType,
    EvaluationResult,
    RuleEvaluationResult
)


class EvaluationService:
    """Service for evaluating business rules"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== MAIN EVALUATION METHODS ====================
    
    def evaluate_rules(self, request: EvaluationRequest) -> Dict[str, Any]:
        """
        Evaluate rules against input data
        
        Args:
            request: Evaluation request with input data
            
        Returns:
            Evaluation results with matched rules and actions
        """
        start_time = time.time()
        evaluation_id = uuid.uuid4()
        
        # Fetch applicable rules
        rules = self._fetch_applicable_rules(
            rule_codes=request.rule_codes,
            category_code=request.category_code
        )
        
        if not rules:
            return {
                "evaluation_id": evaluation_id,
                "entity_type": request.entity_type,
                "entity_id": request.entity_id,
                "total_rules_evaluated": 0,
                "rules_matched": 0,
                "evaluation_results": [],
                "overall_result": EvaluationResult.PASS,
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "evaluated_at": datetime.utcnow()
            }
        
        # Determine evaluation strategy
        strategy = request.evaluation_strategy or EvaluationStrategy.ALL_MATCH
        
        # Evaluate rules
        evaluation_results = []
        rules_matched = 0
        overall_result = EvaluationResult.PASS
        
        for rule in rules:
            rule_start = time.time()
            
            try:
                # Evaluate rule
                matched, output_data = self._evaluate_rule(rule, request.input_data)
                result = EvaluationResult.PASS if matched else EvaluationResult.FAIL
                
                if matched:
                    rules_matched += 1
                    # For reject/fail actions, overall result is fail
                    if self._has_fail_action(rule):
                        overall_result = EvaluationResult.FAIL
                
                rule_result = RuleEvaluationResult(
                    rule_id=rule.id,
                    rule_code=rule.rule_code,
                    rule_name=rule.rule_name,
                    matched=matched,
                    evaluation_result=result,
                    output_data=output_data,
                    execution_time_ms=int((time.time() - rule_start) * 1000),
                    error_message=None
                )
                
                evaluation_results.append(rule_result)
                
                # Log evaluation
                self._log_evaluation(
                    evaluation_id=evaluation_id,
                    rule=rule,
                    entity_type=request.entity_type,
                    entity_id=request.entity_id,
                    input_data=request.input_data,
                    matched=matched,
                    result=result,
                    output_data=output_data,
                    execution_time_ms=rule_result.execution_time_ms
                )
                
                # Apply strategy
                if strategy == EvaluationStrategy.FIRST_MATCH and matched:
                    break
                elif strategy == EvaluationStrategy.PRIORITY and matched and self._is_critical_failure(rule):
                    break
                
            except Exception as e:
                # Log error
                rule_result = RuleEvaluationResult(
                    rule_id=rule.id,
                    rule_code=rule.rule_code,
                    rule_name=rule.rule_name,
                    matched=False,
                    evaluation_result=EvaluationResult.ERROR,
                    output_data=None,
                    execution_time_ms=int((time.time() - rule_start) * 1000),
                    error_message=str(e)
                )
                
                evaluation_results.append(rule_result)
                overall_result = EvaluationResult.ERROR
                
                self._log_evaluation(
                    evaluation_id=evaluation_id,
                    rule=rule,
                    entity_type=request.entity_type,
                    entity_id=request.entity_id,
                    input_data=request.input_data,
                    matched=False,
                    result=EvaluationResult.ERROR,
                    output_data=None,
                    execution_time_ms=rule_result.execution_time_ms,
                    error_message=str(e)
                )
        
        total_time = int((time.time() - start_time) * 1000)
        
        return {
            "evaluation_id": evaluation_id,
            "entity_type": request.entity_type,
            "entity_id": request.entity_id,
            "total_rules_evaluated": len(evaluation_results),
            "rules_matched": rules_matched,
            "evaluation_results": [r.dict() for r in evaluation_results],
            "overall_result": overall_result,
            "execution_time_ms": total_time,
            "evaluated_at": datetime.utcnow()
        }
    
    def test_rule(
        self,
        rule_id: int,
        test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test a single rule with test data
        
        Args:
            rule_id: Rule to test
            test_data: Test input data
            
        Returns:
            Test result
        """
        rule = self._get_rule(rule_id)
        
        start_time = time.time()
        
        try:
            matched, output_data = self._evaluate_rule(rule, test_data)
            result = EvaluationResult.PASS if matched else EvaluationResult.FAIL
            error_message = None
        except Exception as e:
            matched = False
            output_data = None
            result = EvaluationResult.ERROR
            error_message = str(e)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return {
            "rule_id": rule.id,
            "rule_code": rule.rule_code,
            "matched": matched,
            "evaluation_result": result,
            "output_data": output_data,
            "execution_time_ms": execution_time,
            "error_message": error_message
        }
    
    # ==================== RULE EVALUATION LOGIC ====================
    
    def _evaluate_rule(
        self,
        rule: BusinessRule,
        input_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Evaluate a single rule
        
        Returns:
            Tuple of (matched, output_data)
        """
        rule_def = rule.rule_definition
        
        # Evaluate conditions
        if 'conditions' in rule_def and rule_def['conditions']:
            matched = self._evaluate_conditions(
                rule_def['conditions'],
                rule_def.get('logical_operator', 'AND'),
                input_data
            )
        elif 'condition_groups' in rule_def and rule_def['condition_groups']:
            matched = self._evaluate_condition_groups(
                rule_def['condition_groups'],
                rule_def.get('group_operator', 'OR'),
                input_data
            )
        else:
            # No conditions means always match
            matched = True
        
        # If matched, prepare output data from actions
        output_data = None
        if matched:
            output_data = self._execute_actions(rule, input_data)
        
        return matched, output_data
    
    def _evaluate_conditions(
        self,
        conditions: List[Dict[str, Any]],
        logical_operator: str,
        input_data: Dict[str, Any]
    ) -> bool:
        """Evaluate a list of conditions with logical operator"""
        results = []
        
        for condition in conditions:
            result = self._evaluate_single_condition(condition, input_data)
            
            # Handle negation
            if condition.get('is_negated', False):
                result = not result
            
            results.append(result)
            
            # Short-circuit evaluation
            if logical_operator == 'AND' and not result:
                return False
            elif logical_operator == 'OR' and result:
                return True
        
        # Final result
        if logical_operator == 'AND':
            return all(results)
        else:  # OR
            return any(results)
    
    def _evaluate_condition_groups(
        self,
        groups: List[Dict[str, Any]],
        group_operator: str,
        input_data: Dict[str, Any]
    ) -> bool:
        """Evaluate condition groups"""
        group_results = []
        
        for group in groups:
            conditions = group.get('conditions', [])
            operator = group.get('operator', 'AND')
            
            group_result = self._evaluate_conditions(conditions, operator, input_data)
            group_results.append(group_result)
            
            # Short-circuit
            if group_operator == 'OR' and group_result:
                return True
            elif group_operator == 'AND' and not group_result:
                return False
        
        if group_operator == 'AND':
            return all(group_results)
        else:  # OR
            return any(group_results)
    
    def _evaluate_single_condition(
        self,
        condition: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> bool:
        """Evaluate a single condition"""
        field_path = condition['field_path']
        operator = condition['operator']
        expected_value = condition['value']
        data_type = condition['data_type']
        
        # Get actual value from input data
        actual_value = self._get_field_value(input_data, field_path)
        
        # Convert values to proper types
        actual_value = self._convert_value(actual_value, data_type)
        expected_value = self._convert_value(expected_value, data_type)
        
        # Apply operator
        return self._apply_operator(operator, actual_value, expected_value, data_type)
    
    # ==================== OPERATOR IMPLEMENTATIONS ====================
    
    def _apply_operator(
        self,
        operator: str,
        actual: Any,
        expected: Any,
        data_type: str
    ) -> bool:
        """Apply comparison operator"""
        try:
            if operator == '=':
                return actual == expected
            elif operator == '!=':
                return actual != expected
            elif operator == '<':
                return actual < expected
            elif operator == '<=':
                return actual <= expected
            elif operator == '>':
                return actual > expected
            elif operator == '>=':
                return actual >= expected
            elif operator == 'in':
                return actual in expected
            elif operator == 'not_in':
                return actual not in expected
            elif operator == 'between':
                if isinstance(expected, list) and len(expected) == 2:
                    return expected[0] <= actual <= expected[1]
                return False
            elif operator == 'contains':
                return expected in str(actual)
            elif operator == 'starts_with':
                return str(actual).startswith(str(expected))
            elif operator == 'ends_with':
                return str(actual).endswith(str(expected))
            elif operator == 'matches':
                return bool(re.match(str(expected), str(actual)))
            elif operator == 'is_null':
                return actual is None
            elif operator == 'is_not_null':
                return actual is not None
            elif operator == 'exists':
                return actual is not None
            else:
                raise ValueError(f"Unknown operator: {operator}")
        except Exception as e:
            # Log error but return False
            return False
    
    # ==================== VALUE HANDLING ====================
    
    def _get_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        Get value from nested dictionary using dot notation
        Example: customer.age -> data['customer']['age']
        """
        parts = field_path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return None
            else:
                return None
        
        return value
    
    def _convert_value(self, value: Any, data_type: str) -> Any:
        """Convert value to specified data type"""
        if value is None:
            return None
        
        try:
            if data_type == 'number':
                if isinstance(value, (int, float)):
                    return value
                return float(value)
            elif data_type == 'string':
                return str(value)
            elif data_type == 'boolean':
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', '1', 'yes')
            elif data_type == 'date':
                if isinstance(value, date):
                    return value
                # Parse date string
                return datetime.strptime(str(value), '%Y-%m-%d').date()
            elif data_type == 'datetime':
                if isinstance(value, datetime):
                    return value
                return datetime.fromisoformat(str(value))
            elif data_type == 'array':
                if isinstance(value, list):
                    return value
                # Try to parse JSON
                if isinstance(value, str):
                    return json.loads(value)
                return list(value)
            elif data_type == 'object':
                if isinstance(value, dict):
                    return value
                if isinstance(value, str):
                    return json.loads(value)
                return value
            else:
                return value
        except Exception:
            return value
    
    # ==================== ACTION EXECUTION ====================
    
    def _execute_actions(
        self,
        rule: BusinessRule,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute rule actions and return output data
        
        Note: This prepares output data. Actual execution (like triggering workflows)
        should be done by the calling service.
        """
        actions = rule.rule_definition.get('actions', [])
        output = {
            "rule_id": rule.id,
            "rule_code": rule.rule_code,
            "actions": []
        }
        
        for action in sorted(actions, key=lambda x: x.get('execution_order', 1)):
            action_type = action['action_type']
            action_config = action['action_config']
            
            action_output = {
                "action_type": action_type,
                "config": action_config
            }
            
            # Prepare action-specific output
            if action_type == 'set_value':
                action_output['field'] = action_config.get('field')
                action_output['value'] = action_config.get('value')
            elif action_type == 'calculate':
                # Perform calculation if formula provided
                formula = action_config.get('formula')
                if formula:
                    try:
                        # Safe evaluation (limited)
                        result = self._evaluate_formula(formula, input_data)
                        action_output['calculated_value'] = result
                    except Exception as e:
                        action_output['error'] = str(e)
            
            output['actions'].append(action_output)
        
        return output
    
    def _evaluate_formula(self, formula: str, data: Dict[str, Any]) -> Any:
        """
        Safely evaluate a simple formula
        
        Note: This is a basic implementation. For production,
        consider using a proper expression parser library.
        """
        # Very basic - just handle simple arithmetic
        # Replace field references with values
        import ast
        import operator as op
        
        # Allowed operators
        operators = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Mod: op.mod,
            ast.Pow: op.pow
        }
        
        # This is a simplified implementation
        # Production version should use a proper expression evaluator
        return formula
    
    # ==================== HELPER METHODS ====================
    
    def _fetch_applicable_rules(
        self,
        rule_codes: Optional[List[str]] = None,
        category_code: Optional[str] = None
    ) -> List[BusinessRule]:
        """Fetch rules that should be evaluated"""
        from backend.shared.database.rules_models import RuleCategory
        
        query = self.db.query(BusinessRule).filter(
            and_(
                BusinessRule.tenant_id == self.tenant_id,
                BusinessRule.is_active == True,
                BusinessRule.is_deleted == False
            )
        )
        
        # Filter by specific rules
        if rule_codes:
            query = query.filter(BusinessRule.rule_code.in_(rule_codes))
        
        # Filter by category
        if category_code:
            category = self.db.query(RuleCategory).filter(
                and_(
                    RuleCategory.category_code == category_code,
                    RuleCategory.tenant_id == self.tenant_id
                )
            ).first()
            
            if category:
                query = query.filter(BusinessRule.category_id == category.id)
        
        # Check effective dates
        today = date.today()
        query = query.filter(
            or_(
                BusinessRule.effective_from.is_(None),
                BusinessRule.effective_from <= today
            )
        ).filter(
            or_(
                BusinessRule.effective_to.is_(None),
                BusinessRule.effective_to >= today
            )
        )
        
        # Order by priority
        query = query.order_by(BusinessRule.priority)
        
        return query.all()
    
    def _get_rule(self, rule_id: int) -> BusinessRule:
        """Get rule by ID"""
        rule = self.db.query(BusinessRule).filter(
            and_(
                BusinessRule.id == rule_id,
                BusinessRule.tenant_id == self.tenant_id,
                BusinessRule.is_deleted == False
            )
        ).first()
        
        if not rule:
            raise CustomException(status_code=404, message="Rule not found")
        
        return rule
    
    def _has_fail_action(self, rule: BusinessRule) -> bool:
        """Check if rule has a fail/reject action"""
        actions = rule.rule_definition.get('actions', [])
        for action in actions:
            if action['action_type'] in ['reject', 'fail']:
                return True
        return False
    
    def _is_critical_failure(self, rule: BusinessRule) -> bool:
        """Check if rule represents a critical failure"""
        actions = rule.rule_definition.get('actions', [])
        for action in actions:
            if action['action_type'] == 'reject':
                severity = action.get('action_config', {}).get('severity', 'normal')
                if severity == 'critical':
                    return True
        return False
    
    def _log_evaluation(
        self,
        evaluation_id: uuid.UUID,
        rule: BusinessRule,
        entity_type: str,
        entity_id: int,
        input_data: Dict[str, Any],
        matched: bool,
        result: EvaluationResult,
        output_data: Optional[Dict[str, Any]],
        execution_time_ms: int,
        error_message: Optional[str] = None
    ):
        """Log evaluation to database"""
        evaluation = RuleEvaluation(
            evaluation_id=evaluation_id,
            rule_id=rule.id,
            entity_type=entity_type,
            entity_id=entity_id,
            input_data=input_data,
            evaluation_result=result.value,
            matched=matched,
            output_data=output_data,
            execution_time_ms=execution_time_ms,
            error_message=error_message,
            tenant_id=self.tenant_id,
            evaluated_by=self.user_id
        )
        
        self.db.add(evaluation)
        self.db.flush()
    
    # ==================== EVALUATION HISTORY ====================
    
    def get_evaluations(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        rule_id: Optional[int] = None,
        result: Optional[EvaluationResult] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RuleEvaluation]:
        """Get evaluation history"""
        query = self.db.query(RuleEvaluation).filter(
            RuleEvaluation.tenant_id == self.tenant_id
        )
        
        if entity_type:
            query = query.filter(RuleEvaluation.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(RuleEvaluation.entity_id == entity_id)
        
        if rule_id:
            query = query.filter(RuleEvaluation.rule_id == rule_id)
        
        if result:
            query = query.filter(RuleEvaluation.evaluation_result == result.value)
        
        query = query.order_by(RuleEvaluation.evaluated_at.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def get_evaluation_by_id(self, evaluation_id: uuid.UUID) -> Optional[RuleEvaluation]:
        """Get specific evaluation"""
        return self.db.query(RuleEvaluation).filter(
            and_(
                RuleEvaluation.evaluation_id == evaluation_id,
                RuleEvaluation.tenant_id == self.tenant_id
            )
        ).first()
