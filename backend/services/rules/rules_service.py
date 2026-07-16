"""
Business Rules Engine Service
Enterprise-grade rules execution and decision table processing
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import json
import re
from decimal import Decimal

from backend.services.rules.rules_models import (
    RuleSet, Rule, Condition, Action, DecisionTable, DecisionTableRow,
    RuleExecution, RuleVersion,
    RuleType, RuleStatus, ConditionOperator, LogicalOperator, ActionType,
    DataType, ExecutionMode,
    RuleSetCreate, RuleCreate, ConditionCreate, ActionCreate,
    DecisionTableCreate, DecisionTableRowCreate,
    ExecuteRuleRequest, ExecuteRuleResponse, TestRuleRequest, TestRuleResponse,
    RuleStats, DecisionTableLookupRequest, DecisionTableLookupResponse
)


class RulesService:
    """Service for rules management and execution"""
    
    def __init__(self, db: Session, tenant_id: UUID, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # =====================================================================
    # RULE SET MANAGEMENT
    # =====================================================================
    
    def create_rule_set(self, data: RuleSetCreate) -> RuleSet:
        """Create a new rule set"""
        rule_set = RuleSet(
            tenant_id=self.tenant_id,
            name=data.name,
            code=data.code,
            description=data.description,
            category=data.category,
            version=data.version,
            execution_mode=data.execution_mode,
            priority=data.priority,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        self.db.add(rule_set)
        self.db.commit()
        self.db.refresh(rule_set)
        return rule_set

    
    def get_rule_set(self, rule_set_id: UUID) -> Optional[RuleSet]:
        """Get rule set by ID"""
        return self.db.query(RuleSet).filter(
            and_(
                RuleSet.id == rule_set_id,
                RuleSet.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_rule_sets(
        self,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        status: Optional[RuleStatus] = None,
        search: Optional[str] = None
    ) -> List[RuleSet]:
        """List rule sets with filters"""
        query = self.db.query(RuleSet).filter(
            RuleSet.tenant_id == self.tenant_id
        )
        
        if category:
            query = query.filter(RuleSet.category == category)
        
        if status:
            query = query.filter(RuleSet.status == status)
        
        if search:
            query = query.filter(
                or_(
                    RuleSet.name.ilike(f"%{search}%"),
                    RuleSet.code.ilike(f"%{search}%"),
                    RuleSet.description.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(desc(RuleSet.created_at)).offset(skip).limit(limit).all()
    
    def update_rule_set(self, rule_set_id: UUID, data: Dict[str, Any]) -> Optional[RuleSet]:
        """Update rule set"""
        rule_set = self.get_rule_set(rule_set_id)
        if not rule_set:
            return None
        
        for key, value in data.items():
            if hasattr(rule_set, key) and key not in ['id', 'tenant_id', 'created_at', 'created_by']:
                setattr(rule_set, key, value)
        
        rule_set.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(rule_set)
        return rule_set
    
    def delete_rule_set(self, rule_set_id: UUID) -> bool:
        """Delete rule set"""
        rule_set = self.get_rule_set(rule_set_id)
        if not rule_set:
            return False
        
        self.db.delete(rule_set)
        self.db.commit()
        return True
    
    def activate_rule_set(self, rule_set_id: UUID) -> Optional[RuleSet]:
        """Activate rule set"""
        rule_set = self.get_rule_set(rule_set_id)
        if not rule_set:
            return None
        
        rule_set.status = RuleStatus.ACTIVE
        rule_set.is_active = True
        rule_set.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(rule_set)
        return rule_set
    
    def deactivate_rule_set(self, rule_set_id: UUID) -> Optional[RuleSet]:
        """Deactivate rule set"""
        rule_set = self.get_rule_set(rule_set_id)
        if not rule_set:
            return None
        
        rule_set.is_active = False
        rule_set.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(rule_set)
        return rule_set

    
    # =====================================================================
    # RULE MANAGEMENT
    # =====================================================================
    
    def create_rule(self, rule_set_id: UUID, data: RuleCreate) -> Rule:
        """Create a new rule"""
        rule_set = self.get_rule_set(rule_set_id)
        if not rule_set:
            raise ValueError("Rule set not found")
        
        rule = Rule(
            rule_set_id=rule_set_id,
            tenant_id=self.tenant_id,
            name=data.name,
            code=data.code,
            description=data.description,
            rule_type=data.rule_type,
            priority=data.priority,
            execution_order=data.execution_order,
            logical_operator=data.logical_operator,
            stop_on_match=data.stop_on_match,
            continue_on_error=data.continue_on_error,
            tags=data.tags
        )
        self.db.add(rule)
        self.db.flush()
        
        # Add conditions
        if data.conditions:
            for cond_data in data.conditions:
                condition = Condition(
                    rule_id=rule.id,
                    tenant_id=self.tenant_id,
                    **cond_data.dict()
                )
                self.db.add(condition)
        
        # Add actions
        if data.actions:
            for action_data in data.actions:
                action = Action(
                    rule_id=rule.id,
                    tenant_id=self.tenant_id,
                    **action_data.dict()
                )
                self.db.add(action)
        
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def get_rule(self, rule_id: UUID) -> Optional[Rule]:
        """Get rule by ID"""
        return self.db.query(Rule).filter(
            and_(
                Rule.id == rule_id,
                Rule.tenant_id == self.tenant_id
            )
        ).first()
    
    def update_rule(self, rule_id: UUID, data: Dict[str, Any]) -> Optional[Rule]:
        """Update rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        for key, value in data.items():
            if hasattr(rule, key) and key not in ['id', 'rule_set_id', 'tenant_id', 'created_at']:
                setattr(rule, key, value)
        
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def delete_rule(self, rule_id: UUID) -> bool:
        """Delete rule"""
        rule = self.get_rule(rule_id)
        if not rule:
            return False
        
        self.db.delete(rule)
        self.db.commit()
        return True

    
    # =====================================================================
    # RULE EXECUTION ENGINE
    # =====================================================================
    
    def execute_rule_set(self, request: ExecuteRuleRequest) -> ExecuteRuleResponse:
        """Execute rule set against input data"""
        start_time = datetime.utcnow()
        
        rule_set = self.get_rule_set(request.rule_set_id)
        if not rule_set:
            raise ValueError("Rule set not found")
        
        if not rule_set.is_active:
            raise ValueError("Rule set is not active")
        
        # Initialize execution tracking
        output_data = request.input_data.copy()
        rules_evaluated = 0
        rules_matched = 0
        actions_executed = 0
        matched_rules = []
        error_message = None
        status = "SUCCESS"
        
        try:
            # Get rules sorted by priority and execution order
            rules = sorted(
                [r for r in rule_set.rules if r.is_active],
                key=lambda r: (r.priority, r.execution_order or 0),
                reverse=True
            )
            
            for rule in rules:
                rules_evaluated += 1
                
                # Evaluate rule conditions
                if self._evaluate_rule(rule, output_data):
                    rules_matched += 1
                    matched_rules.append(str(rule.id))
                    
                    # Execute actions
                    action_count = self._execute_actions(rule, output_data)
                    actions_executed += action_count
                    
                    # Stop if rule has stop_on_match flag
                    if rule.stop_on_match:
                        break
        
        except Exception as e:
            status = "FAILURE"
            error_message = str(e)
        
        # Calculate execution time
        end_time = datetime.utcnow()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Create execution record
        execution = RuleExecution(
            rule_set_id=request.rule_set_id,
            tenant_id=self.tenant_id,
            execution_context=request.execution_context,
            business_key=request.business_key,
            input_data=request.input_data,
            output_data=output_data,
            rules_evaluated=rules_evaluated,
            rules_matched=rules_matched,
            actions_executed=actions_executed,
            matched_rules=matched_rules,
            started_at=start_time,
            completed_at=end_time,
            execution_time_ms=execution_time_ms,
            status=status,
            error_message=error_message
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        return ExecuteRuleResponse(
            execution_id=str(execution.id),
            status=status,
            output_data=output_data,
            rules_evaluated=rules_evaluated,
            rules_matched=rules_matched,
            actions_executed=actions_executed,
            matched_rules=matched_rules,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )

    
    def _evaluate_rule(self, rule: Rule, data: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions match"""
        if not rule.conditions:
            return True  # No conditions means always match
        
        # Group conditions by logical operator
        if rule.logical_operator == LogicalOperator.AND:
            return all(self._evaluate_condition(cond, data) for cond in rule.conditions)
        elif rule.logical_operator == LogicalOperator.OR:
            return any(self._evaluate_condition(cond, data) for cond in rule.conditions)
        else:  # NOT
            return not all(self._evaluate_condition(cond, data) for cond in rule.conditions)
    
    def _evaluate_condition(self, condition: Condition, data: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        # Get field value from data
        field_value = self._get_field_value(condition.field_name, data)
        
        # Get comparison value
        if condition.is_dynamic and condition.dynamic_field_name:
            compare_value = self._get_field_value(condition.dynamic_field_name, data)
        else:
            compare_value = condition.value
        
        # Evaluate based on operator
        operator = condition.operator
        
        if operator == ConditionOperator.EQUALS:
            return self._convert_value(field_value, condition.field_type) == self._convert_value(compare_value, condition.field_type)
        
        elif operator == ConditionOperator.NOT_EQUALS:
            return self._convert_value(field_value, condition.field_type) != self._convert_value(compare_value, condition.field_type)
        
        elif operator == ConditionOperator.GREATER_THAN:
            return self._convert_value(field_value, condition.field_type) > self._convert_value(compare_value, condition.field_type)
        
        elif operator == ConditionOperator.GREATER_THAN_OR_EQUAL:
            return self._convert_value(field_value, condition.field_type) >= self._convert_value(compare_value, condition.field_type)
        
        elif operator == ConditionOperator.LESS_THAN:
            return self._convert_value(field_value, condition.field_type) < self._convert_value(compare_value, condition.field_type)
        
        elif operator == ConditionOperator.LESS_THAN_OR_EQUAL:
            return self._convert_value(field_value, condition.field_type) <= self._convert_value(compare_value, condition.field_type)
        
        elif operator == ConditionOperator.IN:
            return field_value in (condition.value_list or [])
        
        elif operator == ConditionOperator.NOT_IN:
            return field_value not in (condition.value_list or [])
        
        elif operator == ConditionOperator.CONTAINS:
            return str(compare_value) in str(field_value)
        
        elif operator == ConditionOperator.NOT_CONTAINS:
            return str(compare_value) not in str(field_value)
        
        elif operator == ConditionOperator.STARTS_WITH:
            return str(field_value).startswith(str(compare_value))
        
        elif operator == ConditionOperator.ENDS_WITH:
            return str(field_value).endswith(str(compare_value))
        
        elif operator == ConditionOperator.BETWEEN:
            value = self._convert_value(field_value, condition.field_type)
            from_value = self._convert_value(condition.value_from, condition.field_type)
            to_value = self._convert_value(condition.value_to, condition.field_type)
            return from_value <= value <= to_value
        
        elif operator == ConditionOperator.IS_NULL:
            return field_value is None or field_value == ''
        
        elif operator == ConditionOperator.IS_NOT_NULL:
            return field_value is not None and field_value != ''
        
        elif operator == ConditionOperator.MATCHES_REGEX:
            if compare_value:
                return bool(re.match(str(compare_value), str(field_value)))
        
        return False

    
    def _get_field_value(self, field_name: str, data: Dict[str, Any]) -> Any:
        """Get field value from data, supporting nested fields"""
        if '.' in field_name:
            # Nested field access (e.g., "customer.age")
            parts = field_name.split('.')
            value = data
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return None
            return value
        else:
            return data.get(field_name)
    
    def _convert_value(self, value: Any, data_type: DataType) -> Any:
        """Convert value to specified data type"""
        if value is None:
            return None
        
        try:
            if data_type == DataType.INTEGER:
                return int(value)
            elif data_type == DataType.FLOAT:
                return float(value)
            elif data_type == DataType.BOOLEAN:
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ['true', '1', 'yes']
            elif data_type == DataType.STRING:
                return str(value)
            else:
                return value
        except:
            return value
    
    def _execute_actions(self, rule: Rule, data: Dict[str, Any]) -> int:
        """Execute rule actions"""
        if not rule.actions:
            return 0
        
        actions_executed = 0
        
        # Sort actions by execution order
        sorted_actions = sorted(rule.actions, key=lambda a: a.action_order)
        
        for action in sorted_actions:
            try:
                # Check if action should be executed
                if action.execute_if_condition:
                    if not self._evaluate_expression(action.execute_if_condition, data):
                        continue
                
                # Execute based on action type
                if action.action_type == ActionType.SET_VALUE:
                    if action.target_field:
                        if action.expression:
                            value = self._evaluate_expression(action.expression, data)
                        else:
                            value = action.value
                        data[action.target_field] = value
                
                elif action.action_type == ActionType.CALCULATE:
                    if action.target_field and action.calculation_formula:
                        result = self._calculate_formula(action.calculation_formula, data)
                        data[action.target_field] = result
                
                elif action.action_type == ActionType.LOG_EVENT:
                    # Log event (placeholder - implement actual logging)
                    pass
                
                elif action.action_type == ActionType.RAISE_ALERT:
                    # Raise alert (placeholder - implement actual alerting)
                    data['_alert'] = {
                        'severity': action.alert_severity,
                        'message': action.alert_message
                    }
                
                # Add more action types as needed
                
                actions_executed += 1
            
            except Exception as e:
                if not rule.continue_on_error:
                    raise
        
        return actions_executed

    
    def _evaluate_expression(self, expression: str, data: Dict[str, Any]) -> Any:
        """Evaluate expression with data context (simplified)"""
        try:
            # Replace field references with values
            for key, value in data.items():
                expression = expression.replace(f"${{{key}}}", str(value))
            
            # Simple expression evaluation (UNSAFE - use proper parser in production)
            return eval(expression)
        except:
            return None
    
    def _calculate_formula(self, formula: str, data: Dict[str, Any]) -> Any:
        """Calculate formula with data context"""
        try:
            # Replace field references
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    formula = formula.replace(f"${{{key}}}", str(value))
            
            # Evaluate mathematical expression
            return eval(formula)
        except:
            return None
    
    # =====================================================================
    # DECISION TABLE MANAGEMENT
    # =====================================================================
    
    def create_decision_table(self, rule_set_id: UUID, data: DecisionTableCreate) -> DecisionTable:
        """Create decision table"""
        rule_set = self.get_rule_set(rule_set_id)
        if not rule_set:
            raise ValueError("Rule set not found")
        
        table = DecisionTable(
            rule_set_id=rule_set_id,
            tenant_id=self.tenant_id,
            name=data.name,
            code=data.code,
            description=data.description,
            input_columns=data.input_columns,
            output_columns=data.output_columns,
            hit_policy=data.hit_policy
        )
        self.db.add(table)
        self.db.commit()
        self.db.refresh(table)
        return table
    
    def get_decision_table(self, table_id: UUID) -> Optional[DecisionTable]:
        """Get decision table by ID"""
        return self.db.query(DecisionTable).filter(
            and_(
                DecisionTable.id == table_id,
                DecisionTable.tenant_id == self.tenant_id
            )
        ).first()
    
    def add_table_row(self, table_id: UUID, data: DecisionTableRowCreate) -> DecisionTableRow:
        """Add row to decision table"""
        table = self.get_decision_table(table_id)
        if not table:
            raise ValueError("Decision table not found")
        
        row = DecisionTableRow(
            decision_table_id=table_id,
            tenant_id=self.tenant_id,
            row_number=data.row_number,
            priority=data.priority,
            input_values=data.input_values,
            output_values=data.output_values,
            description=data.description
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
    
    def update_table_row(self, row_id: UUID, data: Dict[str, Any]) -> Optional[DecisionTableRow]:
        """Update decision table row"""
        row = self.db.query(DecisionTableRow).filter(
            and_(
                DecisionTableRow.id == row_id,
                DecisionTableRow.tenant_id == self.tenant_id
            )
        ).first()
        
        if not row:
            return None
        
        for key, value in data.items():
            if hasattr(row, key) and key not in ['id', 'decision_table_id', 'tenant_id', 'created_at']:
                setattr(row, key, value)
        
        self.db.commit()
        self.db.refresh(row)
        return row
    
    def delete_table_row(self, row_id: UUID) -> bool:
        """Delete decision table row"""
        row = self.db.query(DecisionTableRow).filter(
            and_(
                DecisionTableRow.id == row_id,
                DecisionTableRow.tenant_id == self.tenant_id
            )
        ).first()
        
        if not row:
            return False
        
        self.db.delete(row)
        self.db.commit()
        return True

    
    def lookup_decision_table(self, request: DecisionTableLookupRequest) -> DecisionTableLookupResponse:
        """Lookup decision table with input values"""
        table = self.get_decision_table(request.decision_table_id)
        if not table:
            raise ValueError("Decision table not found")
        
        if not table.is_active:
            raise ValueError("Decision table is not active")
        
        # Get all active rows
        rows = [r for r in table.rows if r.is_active]
        
        # Sort rows by priority and row_number
        rows = sorted(rows, key=lambda r: (r.priority, r.row_number), reverse=True)
        
        matched_rows = []
        output_values = {}
        
        for row in rows:
            if self._match_table_row(row, request.input_values, table.input_columns):
                matched_rows.append({
                    'row_number': row.row_number,
                    'input_values': row.input_values,
                    'output_values': row.output_values,
                    'priority': row.priority
                })
                
                # Apply hit policy
                if table.hit_policy == "FIRST":
                    # Take first match and stop
                    output_values = row.output_values
                    break
                
                elif table.hit_policy == "ANY":
                    # Take any match (first one)
                    if not output_values:
                        output_values = row.output_values
                    break
                
                elif table.hit_policy == "PRIORITY":
                    # Take highest priority match (already sorted)
                    if not output_values:
                        output_values = row.output_values
                    break
                
                elif table.hit_policy == "COLLECT":
                    # Collect all matches
                    if not output_values:
                        output_values = row.output_values
                    else:
                        # Merge outputs (last wins for duplicates)
                        output_values.update(row.output_values)
        
        return DecisionTableLookupResponse(
            matched=len(matched_rows) > 0,
            matched_rows=matched_rows,
            output_values=output_values
        )
    
    def _match_table_row(
        self,
        row: DecisionTableRow,
        input_values: Dict[str, Any],
        input_columns: List[Dict[str, Any]]
    ) -> bool:
        """Check if row matches input values"""
        for column in input_columns:
            column_name = column.get('name')
            column_type = column.get('type', 'STRING')
            
            # Get values
            row_value = row.input_values.get(column_name)
            input_value = input_values.get(column_name)
            
            # Handle wildcard (- or * means any value)
            if row_value in ['-', '*', 'ANY']:
                continue
            
            # Handle ranges (e.g., "100-500")
            if isinstance(row_value, str) and '-' in row_value and row_value not in ['-', '*']:
                try:
                    parts = row_value.split('-')
                    if len(parts) == 2:
                        from_val = float(parts[0])
                        to_val = float(parts[1])
                        input_num = float(input_value)
                        if not (from_val <= input_num <= to_val):
                            return False
                        continue
                except:
                    pass
            
            # Handle lists (e.g., "A,B,C")
            if isinstance(row_value, str) and ',' in row_value:
                allowed_values = [v.strip() for v in row_value.split(',')]
                if input_value not in allowed_values:
                    return False
                continue
            
            # Exact match
            if self._convert_value(row_value, DataType[column_type]) != self._convert_value(input_value, DataType[column_type]):
                return False
        
        return True
    
    # =====================================================================
    # RULE TESTING
    # =====================================================================
    
    def test_rule(self, rule_id: UUID, request: TestRuleRequest) -> TestRuleResponse:
        """Test a single rule with sample data"""
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError("Rule not found")
        
        conditions_met = []
        conditions_failed = []
        
        # Evaluate each condition
        for condition in rule.conditions:
            if self._evaluate_condition(condition, request.input_data):
                conditions_met.append(f"{condition.field_name} {condition.operator.value}")
            else:
                conditions_failed.append(f"{condition.field_name} {condition.operator.value}")
        
        # Check if rule matches
        matched = self._evaluate_rule(rule, request.input_data)
        
        # Get actions that would execute
        actions_to_execute = []
        output_data = request.input_data.copy()
        
        if matched:
            for action in sorted(rule.actions, key=lambda a: a.action_order):
                actions_to_execute.append({
                    'action_type': action.action_type.value,
                    'target_field': action.target_field,
                    'value': action.value
                })
            
            # Simulate action execution
            self._execute_actions(rule, output_data)
        
        return TestRuleResponse(
            matched=matched,
            conditions_met=conditions_met,
            conditions_failed=conditions_failed,
            actions_to_execute=actions_to_execute,
            output_data=output_data
        )

    
    # =====================================================================
    # RULE VERSIONING
    # =====================================================================
    
    def create_version(self, rule_set_id: UUID, version_name: str, description: str = None) -> RuleVersion:
        """Create a version snapshot of rule set"""
        rule_set = self.get_rule_set(rule_set_id)
        if not rule_set:
            raise ValueError("Rule set not found")
        
        # Create snapshot
        snapshot = {
            'rule_set': {
                'name': rule_set.name,
                'code': rule_set.code,
                'description': rule_set.description,
                'category': rule_set.category,
                'version': rule_set.version
            },
            'rules': [
                {
                    'name': r.name,
                    'code': r.code,
                    'rule_type': r.rule_type.value,
                    'priority': r.priority,
                    'conditions': [
                        {
                            'field_name': c.field_name,
                            'operator': c.operator.value,
                            'value': c.value
                        }
                        for c in r.conditions
                    ],
                    'actions': [
                        {
                            'action_type': a.action_type.value,
                            'target_field': a.target_field,
                            'value': a.value
                        }
                        for a in r.actions
                    ]
                }
                for r in rule_set.rules
            ]
        }
        
        # Mark previous versions as not current
        self.db.query(RuleVersion).filter(
            and_(
                RuleVersion.rule_set_id == rule_set_id,
                RuleVersion.tenant_id == self.tenant_id,
                RuleVersion.is_current == True
            )
        ).update({'is_current': False})
        
        # Create new version
        version = RuleVersion(
            rule_set_id=rule_set_id,
            tenant_id=self.tenant_id,
            version_number=rule_set.version,
            version_name=version_name,
            description=description,
            rule_set_snapshot=snapshot,
            is_current=True,
            created_by=self.user_id
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version
    
    def list_versions(self, rule_set_id: UUID) -> List[RuleVersion]:
        """List all versions of a rule set"""
        return self.db.query(RuleVersion).filter(
            and_(
                RuleVersion.rule_set_id == rule_set_id,
                RuleVersion.tenant_id == self.tenant_id
            )
        ).order_by(desc(RuleVersion.created_at)).all()
    
    # =====================================================================
    # ANALYTICS
    # =====================================================================
    
    def get_rule_stats(self) -> RuleStats:
        """Get rule statistics"""
        total_rule_sets = self.db.query(RuleSet).filter(
            RuleSet.tenant_id == self.tenant_id
        ).count()
        
        active_rule_sets = self.db.query(RuleSet).filter(
            and_(
                RuleSet.tenant_id == self.tenant_id,
                RuleSet.is_active == True
            )
        ).count()
        
        total_rules = self.db.query(Rule).filter(
            Rule.tenant_id == self.tenant_id
        ).count()
        
        total_executions = self.db.query(RuleExecution).filter(
            RuleExecution.tenant_id == self.tenant_id
        ).count()
        
        # Average execution time
        avg_time = self.db.query(func.avg(RuleExecution.execution_time_ms)).filter(
            RuleExecution.tenant_id == self.tenant_id
        ).scalar() or 0.0
        
        # Success rate
        successful = self.db.query(RuleExecution).filter(
            and_(
                RuleExecution.tenant_id == self.tenant_id,
                RuleExecution.status == "SUCCESS"
            )
        ).count()
        
        success_rate = (successful / total_executions * 100) if total_executions > 0 else 0.0
        
        return RuleStats(
            total_rule_sets=total_rule_sets,
            active_rule_sets=active_rule_sets,
            total_rules=total_rules,
            total_executions=total_executions,
            avg_execution_time_ms=round(avg_time, 2),
            success_rate=round(success_rate, 2)
        )
    
    def get_rule_execution_history(
        self,
        rule_set_id: Optional[UUID] = None,
        business_key: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[RuleExecution]:
        """Get rule execution history"""
        query = self.db.query(RuleExecution).filter(
            RuleExecution.tenant_id == self.tenant_id
        )
        
        if rule_set_id:
            query = query.filter(RuleExecution.rule_set_id == rule_set_id)
        
        if business_key:
            query = query.filter(RuleExecution.business_key == business_key)
        
        return query.order_by(desc(RuleExecution.created_at)).offset(skip).limit(limit).all()
