"""
Business Rules Execution Engine

Executes rules and evaluates conditions
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re
import operator
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, ROUND_UP

from backend.services.rules.rule_models import (
    RuleSet, DecisionRule, ValidationRule, CalculationRule,
    RoutingRule, PricingRule, EligibilityRule, DecisionTable,
    Condition, ConditionGroup, Action, TableColumn, TableRow, TableCell,
    OperatorType, LogicalOperator, ActionType, TableColumnType,
    RuleExecutionContext, RuleExecutionResult, DecisionTableMatchResult,
    ExecutionMode, ExecutionStrategy, RulePriority, ExecutionEngineConfig,
    RuleChain, RuleChainStep, RuleChainExecutionResult, ExecutionHistory
)


class RuleEngine:
    """Business rules execution engine"""
    
    def __init__(self):
        self.execution_log: List[str] = []
        self.execution_mode: ExecutionMode = ExecutionMode.ON_DEMAND
        self.execution_config: Optional[ExecutionEngineConfig] = None
    
    # ==================== EXECUTION MODE HANDLERS ====================
    
    def execute_with_mode(
        self,
        ruleset: RuleSet,
        context: RuleExecutionContext,
        execution_mode: Optional[ExecutionMode] = None
    ) -> RuleExecutionResult:
        """Execute ruleset with specified execution mode"""
        # Determine execution mode
        if execution_mode:
            self.execution_mode = execution_mode
        elif ruleset.execution_config:
            self.execution_mode = ruleset.execution_config.execution_mode
        else:
            self.execution_mode = ExecutionMode.ON_DEMAND
        
        self.execution_config = ruleset.execution_config
        
        self.execution_log.append(f"Execution mode: {self.execution_mode.value}")
        
        # Execute based on mode
        if self.execution_mode == ExecutionMode.REAL_TIME:
            return self._execute_real_time(ruleset, context)
        elif self.execution_mode == ExecutionMode.BATCH:
            return self._execute_batch(ruleset, context)
        else:  # ON_DEMAND
            return self._execute_on_demand(ruleset, context)
    
    def _execute_real_time(
        self,
        ruleset: RuleSet,
        context: RuleExecutionContext
    ) -> RuleExecutionResult:
        """Execute in real-time mode (optimized for speed)"""
        self.execution_log.append("Real-time execution: Optimized for speed")
        
        # Check trigger conditions if configured
        if self.execution_config and self.execution_config.trigger_conditions:
            trigger_met = self._check_trigger_conditions(
                self.execution_config.trigger_conditions,
                context.data
            )
            if not trigger_met:
                self.execution_log.append("Trigger conditions not met, skipping execution")
                return self._create_empty_result(ruleset, context)
        
        # Execute with priority if enabled
        if self.execution_config and self.execution_config.enable_priority_execution:
            return self._execute_with_priority(ruleset, context)
        
        # Execute with chaining if enabled
        if self.execution_config and self.execution_config.enable_rule_chaining:
            return self._execute_with_chaining(ruleset, context)
        
        # Standard execution
        return self.execute_ruleset(ruleset, context)
    
    def _execute_batch(
        self,
        ruleset: RuleSet,
        context: RuleExecutionContext
    ) -> RuleExecutionResult:
        """Execute in batch mode (scheduled execution)"""
        self.execution_log.append("Batch execution: Processing scheduled rules")
        
        # Execute with priority if enabled
        if self.execution_config and self.execution_config.enable_priority_execution:
            return self._execute_with_priority(ruleset, context)
        
        # Standard execution
        return self.execute_ruleset(ruleset, context)
    
    def _execute_on_demand(
        self,
        ruleset: RuleSet,
        context: RuleExecutionContext
    ) -> RuleExecutionResult:
        """Execute in on-demand mode (user-triggered)"""
        self.execution_log.append("On-demand execution: User-triggered")
        
        # Execute with chaining if enabled
        if self.execution_config and self.execution_config.enable_rule_chaining:
            return self._execute_with_chaining(ruleset, context)
        
        # Execute with priority if enabled
        if self.execution_config and self.execution_config.enable_priority_execution:
            return self._execute_with_priority(ruleset, context)
        
        # Standard execution
        return self.execute_ruleset(ruleset, context)
    
    def _check_trigger_conditions(
        self,
        trigger_conditions: Dict[str, Any],
        data: Dict[str, Any]
    ) -> bool:
        """Check if trigger conditions are met"""
        try:
            # Convert trigger conditions to ConditionGroup
            if 'conditions' in trigger_conditions:
                condition_group = ConditionGroup(**trigger_conditions)
                return self.evaluate_condition_group(condition_group, data)
            return True
        except Exception as e:
            self.execution_log.append(f"Trigger condition check failed: {str(e)}")
            return False
    
    def _create_empty_result(
        self,
        ruleset: RuleSet,
        context: RuleExecutionContext
    ) -> RuleExecutionResult:
        """Create empty result when execution is skipped"""
        return RuleExecutionResult(
            execution_id=f"exec_{datetime.utcnow().timestamp()}",
            ruleset_id=ruleset.ruleset_id,
            context_id=context.context_id,
            success=True,
            rules_executed=[],
            rules_matched=[],
            actions_executed=[],
            output_data=context.data.copy(),
            execution_time_ms=0,
            executed_at=datetime.utcnow(),
            execution_log=["Execution skipped - trigger conditions not met"]
        )
    
    # ==================== PRIORITY-BASED EXECUTION ====================
    
    def _execute_with_priority(
        self,
        ruleset: RuleSet,
        context: RuleExecutionContext
    ) -> RuleExecutionResult:
        """Execute rules based on priority"""
        start_time = datetime.utcnow()
        self.execution_log.append("Executing with priority-based ordering")
        
        result = RuleExecutionResult(
            execution_id=f"exec_{datetime.utcnow().timestamp()}",
            ruleset_id=ruleset.ruleset_id,
            context_id=context.context_id,
            success=True,
            rules_executed=[],
            rules_matched=[],
            actions_executed=[],
            output_data=context.data.copy(),
            execution_time_ms=0,
            executed_at=start_time
        )
        
        try:
            # Collect all rules with their priorities
            prioritized_rules = self._collect_and_prioritize_rules(ruleset)
            
            # Execute in priority order
            for rule_entry in prioritized_rules:
                rule_type = rule_entry['type']
                rule = rule_entry['rule']
                priority = rule_entry['priority']
                
                self.execution_log.append(
                    f"Executing {rule_type} rule '{rule.rule_name}' (priority: {priority})"
                )
                
                # Execute based on rule type
                if rule_type == 'validation':
                    self._execute_validation_rules([rule], context, result)
                elif rule_type == 'calculation':
                    self._execute_calculation_rules([rule], context, result)
                elif rule_type == 'decision':
                    self._execute_decision_rules([rule], context, result)
                elif rule_type == 'routing':
                    self._execute_routing_rules([rule], context, result)
                elif rule_type == 'pricing':
                    self._execute_pricing_rules([rule], context, result)
                elif rule_type == 'eligibility':
                    self._execute_eligibility_rules([rule], context, result)
                
                # Check for early termination
                if result.validation_errors and any(
                    r.stop_on_error for r in ruleset.validation_rules if r.rule_id in result.rules_executed
                ):
                    result.success = False
                    self.execution_log.append("Stopping execution due to validation errors")
                    break
            
            # Execute decision tables last
            if ruleset.decision_tables:
                self._execute_decision_tables(ruleset.decision_tables, context, result)
        
        except Exception as e:
            result.success = False
            self.execution_log.append(f"ERROR: {str(e)}")
        
        # Calculate execution time
        end_time = datetime.utcnow()
        result.execution_time_ms = (end_time - start_time).total_seconds() * 1000
        result.execution_log = self.execution_log
        
        return result
    
    def _collect_and_prioritize_rules(self, ruleset: RuleSet) -> List[Dict[str, Any]]:
        """Collect all rules and sort by priority"""
        all_rules = []
        
        # Collect validation rules
        for rule in ruleset.validation_rules:
            if rule.is_active:
                all_rules.append({
                    'type': 'validation',
                    'rule': rule,
                    'priority': rule.priority
                })
        
        # Collect calculation rules
        for rule in ruleset.calculation_rules:
            if rule.is_active:
                all_rules.append({
                    'type': 'calculation',
                    'rule': rule,
                    'priority': rule.priority
                })
        
        # Collect decision rules
        for rule in ruleset.decision_rules:
            if rule.is_active:
                all_rules.append({
                    'type': 'decision',
                    'rule': rule,
                    'priority': rule.priority
                })
        
        # Collect routing rules
        for rule in ruleset.routing_rules:
            if rule.is_active:
                all_rules.append({
                    'type': 'routing',
                    'rule': rule,
                    'priority': rule.priority
                })
        
        # Collect pricing rules
        for rule in ruleset.pricing_rules:
            if rule.is_active:
                all_rules.append({
                    'type': 'pricing',
                    'rule': rule,
                    'priority': rule.priority
                })
        
        # Collect eligibility rules
        for rule in ruleset.eligibility_rules:
            if rule.is_active:
                all_rules.append({
                    'type': 'eligibility',
                    'rule': rule,
                    'priority': rule.priority
                })
        
        # Sort by priority (highest first)
        all_rules.sort(key=lambda x: x['priority'], reverse=True)
        
        return all_rules
    
    # ==================== RULE CHAINING ====================
    
    def _execute_with_chaining(
        self,
        ruleset: RuleSet,
        context: RuleExecutionContext
    ) -> RuleExecutionResult:
        """Execute rules with chaining enabled"""
        self.execution_log.append("Executing with rule chaining")
        
        if not self.execution_config or not self.execution_config.rule_chains:
            self.execution_log.append("No rule chains configured, using standard execution")
            return self.execute_ruleset(ruleset, context)
        
        # Execute the first active chain
        for chain in self.execution_config.rule_chains:
            if chain.is_active:
                chain_result = self.execute_rule_chain(ruleset, chain, context)
                
                # Convert chain result to standard execution result
                return self._convert_chain_result_to_execution_result(
                    chain_result,
                    ruleset,
                    context
                )
        
        # No active chains, use standard execution
        return self.execute_ruleset(ruleset, context)
    
    def execute_rule_chain(
        self,
        ruleset: RuleSet,
        chain: RuleChain,
        context: RuleExecutionContext
    ) -> RuleChainExecutionResult:
        """Execute a rule chain"""
        start_time = datetime.utcnow()
        self.execution_log.append(f"Executing rule chain: {chain.chain_name}")
        
        chain_result = RuleChainExecutionResult(
            chain_id=chain.chain_id,
            chain_name=chain.chain_name,
            execution_id=f"chain_{datetime.utcnow().timestamp()}",
            success=True,
            steps_completed=0,
            steps_failed=0,
            steps_skipped=0,
            step_results=[],
            final_output={},
            execution_strategy=chain.execution_strategy,
            stopped_early=False,
            execution_time_ms=0,
            executed_at=start_time,
            execution_log=[]
        )
        
        # Initialize context
        current_context = context.data.copy()
        if chain.initial_context:
            current_context.update(chain.initial_context)
        
        # Sort steps by order
        sorted_steps = sorted(chain.steps, key=lambda s: s.step_order)
        
        # Execute each step
        for step in sorted_steps:
            if not step.is_active:
                chain_result.steps_skipped += 1
                self.execution_log.append(f"Step '{step.step_name}' is inactive, skipping")
                continue
            
            # Check skip condition
            if step.skip_on_condition:
                try:
                    should_skip = eval(step.skip_on_condition, {"__builtins__": {}}, current_context)
                    if should_skip:
                        chain_result.steps_skipped += 1
                        self.execution_log.append(f"Step '{step.step_name}' skipped by condition")
                        continue
                except Exception as e:
                    self.execution_log.append(f"Skip condition evaluation failed: {str(e)}")
            
            # Execute step
            step_result = self._execute_chain_step(
                step,
                ruleset,
                current_context,
                context.tenant_id
            )
            
            chain_result.step_results.append(step_result)
            
            if step_result['success']:
                chain_result.steps_completed += 1
                
                # Pass output to next step if configured
                if step.pass_output_to_next and step_result.get('output'):
                    if step.output_field_mappings:
                        # Map specific fields
                        for source_field, target_field in step.output_field_mappings.items():
                            if source_field in step_result['output']:
                                current_context[target_field] = step_result['output'][source_field]
                    else:
                        # Pass all outputs
                        current_context.update(step_result['output'])
            else:
                chain_result.steps_failed += 1
                
                # Handle failure based on strategy
                if chain.execution_strategy == ExecutionStrategy.STOP_ON_FIRST_FAILURE:
                    chain_result.stopped_early = True
                    chain_result.stop_reason = f"Step '{step.step_name}' failed"
                    chain_result.success = False
                    self.execution_log.append(f"Stopping chain due to step failure: {step.step_name}")
                    break
                elif chain.execution_strategy == ExecutionStrategy.COLLECT_ALL_VIOLATIONS:
                    # Continue collecting all failures
                    self.execution_log.append(f"Step '{step.step_name}' failed, continuing to collect violations")
                    continue
        
        # Set final output
        chain_result.final_output = current_context
        chain_result.execution_log = self.execution_log.copy()
        
        # Calculate execution time
        end_time = datetime.utcnow()
        chain_result.execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return chain_result
    
    def _execute_chain_step(
        self,
        step: RuleChainStep,
        ruleset: RuleSet,
        context_data: Dict[str, Any],
        tenant_id: int
    ) -> Dict[str, Any]:
        """Execute a single chain step"""
        self.execution_log.append(f"Executing step: {step.step_name}")
        
        step_result = {
            'step_id': step.step_id,
            'step_name': step.step_name,
            'success': False,
            'output': {},
            'errors': []
        }
        
        try:
            # Find the rule
            rule = self._find_rule_by_id(ruleset, step.rule_id, step.rule_type)
            
            if not rule:
                step_result['errors'].append(f"Rule not found: {step.rule_id}")
                return step_result
            
            # Create execution context
            exec_context = RuleExecutionContext(
                context_id=f"step_{step.step_id}",
                entity_type=ruleset.entity_type,
                data=context_data,
                tenant_id=tenant_id
            )
            
            # Execute based on rule type
            exec_result = RuleExecutionResult(
                execution_id=f"step_{step.step_id}",
                ruleset_id=ruleset.ruleset_id,
                context_id=exec_context.context_id,
                success=True,
                rules_executed=[],
                rules_matched=[],
                actions_executed=[],
                output_data=context_data.copy(),
                execution_time_ms=0,
                executed_at=datetime.utcnow()
            )
            
            if step.rule_type == 'validation':
                self._execute_validation_rules([rule], exec_context, exec_result)
                step_result['success'] = len(exec_result.validation_errors) == 0
                step_result['errors'] = exec_result.validation_errors
            elif step.rule_type == 'calculation':
                self._execute_calculation_rules([rule], exec_context, exec_result)
                step_result['success'] = True
            elif step.rule_type == 'decision':
                self._execute_decision_rules([rule], exec_context, exec_result)
                step_result['success'] = True
            elif step.rule_type == 'routing':
                self._execute_routing_rules([rule], exec_context, exec_result)
                step_result['success'] = True
            elif step.rule_type == 'pricing':
                self._execute_pricing_rules([rule], exec_context, exec_result)
                step_result['success'] = True
            elif step.rule_type == 'eligibility':
                self._execute_eligibility_rules([rule], exec_context, exec_result)
                step_result['success'] = exec_result.is_eligible if exec_result.is_eligible is not None else True
            
            step_result['output'] = exec_result.output_data
            
        except Exception as e:
            step_result['errors'].append(str(e))
            self.execution_log.append(f"Step execution error: {str(e)}")
        
        return step_result
    
    def _find_rule_by_id(
        self,
        ruleset: RuleSet,
        rule_id: str,
        rule_type: str
    ) -> Optional[Union[DecisionRule, ValidationRule, CalculationRule, RoutingRule, PricingRule, EligibilityRule]]:
        """Find a rule by ID and type"""
        if rule_type == 'decision':
            return next((r for r in ruleset.decision_rules if r.rule_id == rule_id), None)
        elif rule_type == 'validation':
            return next((r for r in ruleset.validation_rules if r.rule_id == rule_id), None)
        elif rule_type == 'calculation':
            return next((r for r in ruleset.calculation_rules if r.rule_id == rule_id), None)
        elif rule_type == 'routing':
            return next((r for r in ruleset.routing_rules if r.rule_id == rule_id), None)
        elif rule_type == 'pricing':
            return next((r for r in ruleset.pricing_rules if r.rule_id == rule_id), None)
        elif rule_type == 'eligibility':
            return next((r for r in ruleset.eligibility_rules if r.rule_id == rule_id), None)
        return None
    
    def _convert_chain_result_to_execution_result(
        self,
        chain_result: RuleChainExecutionResult,
        ruleset: RuleSet,
        context: RuleExecutionContext
    ) -> RuleExecutionResult:
        """Convert chain result to standard execution result"""
        # Collect all executed rules
        rules_executed = []
        validation_errors = []
        
        for step_result in chain_result.step_results:
            rules_executed.append(step_result['step_id'])
            if step_result.get('errors'):
                validation_errors.extend(step_result['errors'])
        
        return RuleExecutionResult(
            execution_id=chain_result.execution_id,
            ruleset_id=ruleset.ruleset_id,
            context_id=context.context_id,
            success=chain_result.success,
            rules_executed=rules_executed,
            rules_matched=[],
            actions_executed=[],
            validation_errors=validation_errors,
            output_data=chain_result.final_output,
            execution_time_ms=chain_result.execution_time_ms,
            executed_at=chain_result.executed_at,
            execution_log=chain_result.execution_log
        )
    
    def execute_ruleset(
        self,
        ruleset: RuleSet,
        context: RuleExecutionContext
    ) -> RuleExecutionResult:
        """Execute complete rule set"""
        start_time = datetime.utcnow()
        self.execution_log = []
        
        result = RuleExecutionResult(
            execution_id=f"exec_{datetime.utcnow().timestamp()}",
            ruleset_id=ruleset.ruleset_id,
            context_id=context.context_id,
            success=True,
            rules_executed=[],
            rules_matched=[],
            actions_executed=[],
            output_data=context.data.copy(),
            execution_time_ms=0,
            executed_at=start_time
        )
        
        try:
            # Execute in order: validation → calculation → decision → routing → pricing → eligibility → decision tables
            
            # 1. Validation rules
            self._execute_validation_rules(ruleset.validation_rules, context, result)
            
            # Stop if validation errors and stop_on_error
            if result.validation_errors and any(
                r.stop_on_error for r in ruleset.validation_rules if r.rule_id in result.rules_executed
            ):
                result.success = False
                return result
            
            # 2. Calculation rules
            self._execute_calculation_rules(ruleset.calculation_rules, context, result)
            
            # 3. Decision rules
            self._execute_decision_rules(ruleset.decision_rules, context, result)
            
            # 4. Routing rules
            self._execute_routing_rules(ruleset.routing_rules, context, result)
            
            # 5. Pricing rules
            self._execute_pricing_rules(ruleset.pricing_rules, context, result)
            
            # 6. Eligibility rules
            self._execute_eligibility_rules(ruleset.eligibility_rules, context, result)
            
            # 7. Decision tables
            self._execute_decision_tables(ruleset.decision_tables, context, result)
            
        except Exception as e:
            result.success = False
            self.execution_log.append(f"ERROR: {str(e)}")
        
        # Calculate execution time
        end_time = datetime.utcnow()
        result.execution_time_ms = (end_time - start_time).total_seconds() * 1000
        result.execution_log = self.execution_log
        
        return result
    
    # ==================== VALIDATION RULES ====================
    
    def _execute_validation_rules(
        self,
        rules: List[ValidationRule],
        context: RuleExecutionContext,
        result: RuleExecutionResult
    ):
        """Execute validation rules"""
        for rule in rules:
            if not rule.is_active:
                continue
            
            result.rules_executed.append(rule.rule_id)
            self.execution_log.append(f"Executing validation rule: {rule.rule_name}")
            
            # Evaluate conditions
            is_valid = self.evaluate_condition_group(rule.conditions, result.output_data)
            
            if not is_valid:
                error_entry = {
                    "rule_id": rule.rule_id,
                    "field": rule.error_field,
                    "message": rule.error_message,
                    "severity": rule.severity
                }
                
                if rule.severity == "error":
                    result.validation_errors.append(error_entry)
                else:
                    result.validation_warnings.append(error_entry)
                
                self.execution_log.append(f"Validation failed: {rule.error_message}")
    
    # ==================== CALCULATION RULES ====================
    
    def _execute_calculation_rules(
        self,
        rules: List[CalculationRule],
        context: RuleExecutionContext,
        result: RuleExecutionResult
    ):
        """Execute calculation rules"""
        for rule in rules:
            if not rule.is_active:
                continue
            
            result.rules_executed.append(rule.rule_id)
            self.execution_log.append(f"Executing calculation rule: {rule.rule_name}")
            
            # Check conditions (if any)
            if rule.conditions:
                if not self.evaluate_condition_group(rule.conditions, result.output_data):
                    self.execution_log.append("Conditions not met, skipping calculation")
                    continue
            
            # Calculate value
            try:
                calculated_value = self.evaluate_formula(rule.formula, result.output_data)
                
                # Apply rounding
                if rule.decimal_places is not None:
                    calculated_value = self._round_value(
                        calculated_value,
                        rule.decimal_places,
                        rule.rounding_mode
                    )
                
                # Set value
                result.output_data[rule.target_field] = calculated_value
                result.calculated_fields[rule.target_field] = calculated_value
                
                self.execution_log.append(
                    f"Calculated {rule.target_field} = {calculated_value}"
                )
                result.rules_matched.append(rule.rule_id)
                
            except Exception as e:
                self.execution_log.append(f"Calculation error: {str(e)}")
    
    # ==================== DECISION RULES ====================
    
    def _execute_decision_rules(
        self,
        rules: List[DecisionRule],
        context: RuleExecutionContext,
        result: RuleExecutionResult
    ):
        """Execute decision rules"""
        for rule in rules:
            if not rule.is_active:
                continue
            
            result.rules_executed.append(rule.rule_id)
            self.execution_log.append(f"Executing decision rule: {rule.rule_name}")
            
            # Evaluate IF condition
            condition_met = self.evaluate_condition_group(rule.if_condition, result.output_data)
            
            if condition_met:
                result.rules_matched.append(rule.rule_id)
                self.execution_log.append("IF condition met, executing THEN actions")
                
                # Execute THEN actions
                for action in sorted(rule.then_actions, key=lambda a: a.order):
                    self._execute_action(action, result)
            else:
                self.execution_log.append("IF condition not met, executing ELSE actions")
                
                # Execute ELSE actions
                if rule.else_actions:
                    for action in sorted(rule.else_actions, key=lambda a: a.order):
                        self._execute_action(action, result)
    
    # ==================== ROUTING RULES ====================
    
    def _execute_routing_rules(
        self,
        rules: List[RoutingRule],
        context: RuleExecutionContext,
        result: RuleExecutionResult
    ):
        """Execute routing rules"""
        for rule in rules:
            if not rule.is_active:
                continue
            
            result.rules_executed.append(rule.rule_id)
            self.execution_log.append(f"Executing routing rule: {rule.rule_name}")
            
            # Check routes in priority order
            for route in sorted(rule.routes, key=lambda r: r.get('priority', 0), reverse=True):
                conditions = route.get('conditions')
                if conditions:
                    # Convert dict to ConditionGroup
                    condition_group = ConditionGroup(**conditions)
                    if self.evaluate_condition_group(condition_group, result.output_data):
                        result.route_destination = route['destination']
                        result.rules_matched.append(rule.rule_id)
                        self.execution_log.append(f"Routed to: {route['destination']}")
                        return
            
            # Use default route if no match
            if rule.default_route:
                result.route_destination = rule.default_route
                self.execution_log.append(f"Using default route: {rule.default_route}")
    
    # ==================== PRICING RULES ====================
    
    def _execute_pricing_rules(
        self,
        rules: List[PricingRule],
        context: RuleExecutionContext,
        result: RuleExecutionResult
    ):
        """Execute pricing rules"""
        for rule in rules:
            if not rule.is_active:
                continue
            
            result.rules_executed.append(rule.rule_id)
            self.execution_log.append(f"Executing pricing rule: {rule.rule_name}")
            
            # Get base price
            base_price = result.output_data.get(rule.base_price_field, 0)
            final_price = base_price
            
            # Apply tiers
            for tier in rule.tiers:
                conditions = tier.get('conditions')
                if conditions:
                    condition_group = ConditionGroup(**conditions)
                    if self.evaluate_condition_group(condition_group, result.output_data):
                        multiplier = tier.get('multiplier', 1.0)
                        addition = tier.get('addition', 0)
                        final_price = (final_price * multiplier) + addition
                        self.execution_log.append(
                            f"Applied tier: multiplier={multiplier}, addition={addition}"
                        )
                        break
            
            # Apply discounts
            if rule.discounts:
                for discount in rule.discounts:
                    conditions = discount.get('conditions')
                    if conditions:
                        condition_group = ConditionGroup(**conditions)
                        if self.evaluate_condition_group(condition_group, result.output_data):
                            discount_amount = discount.get('amount', 0)
                            discount_percent = discount.get('percent', 0)
                            
                            if discount_percent:
                                final_price = final_price * (1 - discount_percent / 100)
                            if discount_amount:
                                final_price = final_price - discount_amount
                            
                            self.execution_log.append(f"Applied discount: {discount_percent}%")
            
            # Apply surcharges
            if rule.surcharges:
                for surcharge in rule.surcharges:
                    conditions = surcharge.get('conditions')
                    if conditions:
                        condition_group = ConditionGroup(**conditions)
                        if self.evaluate_condition_group(condition_group, result.output_data):
                            surcharge_amount = surcharge.get('amount', 0)
                            surcharge_percent = surcharge.get('percent', 0)
                            
                            if surcharge_percent:
                                final_price = final_price * (1 + surcharge_percent / 100)
                            if surcharge_amount:
                                final_price = final_price + surcharge_amount
                            
                            self.execution_log.append(f"Applied surcharge: {surcharge_percent}%")
            
            # Store final price
            result.output_data['final_price'] = round(final_price, 2)
            result.calculated_fields['final_price'] = round(final_price, 2)
            result.rules_matched.append(rule.rule_id)
    
    # ==================== ELIGIBILITY RULES ====================
    
    def _execute_eligibility_rules(
        self,
        rules: List[EligibilityRule],
        context: RuleExecutionContext,
        result: RuleExecutionResult
    ):
        """Execute eligibility rules"""
        for rule in rules:
            if not rule.is_active:
                continue
            
            result.rules_executed.append(rule.rule_id)
            self.execution_log.append(f"Executing eligibility rule: {rule.rule_name}")
            
            # Evaluate criteria
            criteria_results = []
            total_score = 0
            
            for criterion in rule.criteria:
                criterion_met = self.evaluate_condition_group(criterion, result.output_data)
                criteria_results.append(criterion_met)
                
                # Calculate score if enabled
                if rule.scoring_enabled and rule.criteria_scores:
                    criterion_id = criterion.group_id
                    if criterion_met and criterion_id in rule.criteria_scores:
                        total_score += rule.criteria_scores[criterion_id]
            
            # Determine eligibility
            if rule.all_must_pass:
                is_eligible = all(criteria_results)
            else:
                is_eligible = any(criteria_results)
            
            # Check score threshold
            if rule.scoring_enabled and rule.minimum_score:
                is_eligible = is_eligible and (total_score >= rule.minimum_score)
            
            result.is_eligible = is_eligible
            result.eligibility_score = total_score if rule.scoring_enabled else None
            result.rules_matched.append(rule.rule_id)
            
            self.execution_log.append(
                f"Eligibility: {is_eligible}, Score: {total_score}"
            )
    
    # ==================== CONDITION EVALUATION ====================
    
    def evaluate_condition_group(
        self,
        group: ConditionGroup,
        data: Dict[str, Any]
    ) -> bool:
        """Evaluate condition group"""
        results = []
        
        for item in group.conditions:
            if isinstance(item, Condition):
                result = self.evaluate_condition(item, data)
            elif isinstance(item, ConditionGroup):
                result = self.evaluate_condition_group(item, data)
            else:
                result = False
            
            results.append(result)
        
        # Apply logical operator
        if not results:
            return True
        
        if group.logical_operator == LogicalOperator.AND:
            return all(results)
        elif group.logical_operator == LogicalOperator.OR:
            return any(results)
        elif group.logical_operator == LogicalOperator.NOT:
            return not results[0] if results else True
        
        return False
    
    def evaluate_condition(self, condition: Condition, data: Dict[str, Any]) -> bool:
        """Evaluate single condition"""
        # Get field value
        field_value = self._get_nested_value(data, condition.field)
        compare_value = condition.value
        
        # Handle operators
        op = condition.operator
        
        if op == OperatorType.EQUALS:
            return field_value == compare_value
        elif op == OperatorType.NOT_EQUALS:
            return field_value != compare_value
        elif op == OperatorType.GREATER_THAN:
            return field_value > compare_value
        elif op == OperatorType.GREATER_THAN_OR_EQUAL:
            return field_value >= compare_value
        elif op == OperatorType.LESS_THAN:
            return field_value < compare_value
        elif op == OperatorType.LESS_THAN_OR_EQUAL:
            return field_value <= compare_value
        elif op == OperatorType.CONTAINS:
            return compare_value in str(field_value)
        elif op == OperatorType.NOT_CONTAINS:
            return compare_value not in str(field_value)
        elif op == OperatorType.STARTS_WITH:
            return str(field_value).startswith(str(compare_value))
        elif op == OperatorType.ENDS_WITH:
            return str(field_value).endswith(str(compare_value))
        elif op == OperatorType.IN:
            return field_value in compare_value
        elif op == OperatorType.NOT_IN:
            return field_value not in compare_value
        elif op == OperatorType.IS_NULL:
            return field_value is None
        elif op == OperatorType.IS_NOT_NULL:
            return field_value is not None
        elif op == OperatorType.BETWEEN:
            return compare_value <= field_value <= condition.value2
        elif op == OperatorType.MATCHES_REGEX:
            return bool(re.match(str(compare_value), str(field_value)))
        
        return False
    
    # ==================== ACTION EXECUTION ====================
    
    def _execute_action(self, action: Action, result: RuleExecutionResult):
        """Execute action"""
        self.execution_log.append(f"Executing action: {action.action_type}")
        
        if action.action_type == ActionType.SET_VALUE:
            result.output_data[action.target_field] = action.target_value
            
        elif action.action_type == ActionType.CALCULATE:
            calculated = self.evaluate_formula(action.formula, result.output_data)
            result.output_data[action.target_field] = calculated
            result.calculated_fields[action.target_field] = calculated
            
        elif action.action_type in [ActionType.SHOW_MESSAGE, ActionType.SHOW_ERROR, ActionType.SHOW_WARNING]:
            # Store message in result
            message_entry = {
                "type": action.action_type.value,
                "message": action.message
            }
            if action.action_type == ActionType.SHOW_ERROR:
                result.validation_errors.append(message_entry)
            else:
                result.validation_warnings.append(message_entry)
        
        result.actions_executed.append({
            "action_id": action.action_id,
            "action_type": action.action_type.value,
            "details": {"target_field": action.target_field, "value": action.target_value}
        })
    
    # ==================== FORMULA EVALUATION ====================
    
    def evaluate_formula(self, formula: str, data: Dict[str, Any]) -> Any:
        """Evaluate formula"""
        # Replace field names with values
        formula_eval = formula
        
        # Extract field names (alphanumeric + underscore)
        field_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        fields = re.findall(field_pattern, formula)
        
        for field in fields:
            if field in data:
                value = data[field]
                formula_eval = formula_eval.replace(field, str(value))
        
        # Safe evaluation (limited functions)
        try:
            # Replace formula functions
            formula_eval = self._replace_formula_functions(formula_eval, data)
            
            # Evaluate
            result = eval(formula_eval, {"__builtins__": {}}, {
                "abs": abs, "min": min, "max": max, "round": round,
                "sum": sum, "len": len
            })
            return result
        except Exception as e:
            self.execution_log.append(f"Formula evaluation error: {str(e)}")
            return 0
    
    def _replace_formula_functions(self, formula: str, data: Dict[str, Any]) -> str:
        """Replace custom formula functions"""
        # IF function
        if_pattern = r'IF\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)'
        formula = re.sub(if_pattern, r'(\2 if \1 else \3)', formula)
        
        return formula
    
    # ==================== HELPER METHODS ====================
    
    def _get_nested_value(self, data: Dict[str, Any], field: str) -> Any:
        """Get nested field value (e.g., 'customer.address.city')"""
        parts = field.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        
        return value
    
    def _round_value(self, value: float, decimals: int, mode: str) -> float:
        """Round value"""
        d = Decimal(str(value))
        
        if mode == "round":
            rounding = ROUND_HALF_UP
        elif mode == "floor":
            rounding = ROUND_DOWN
        elif mode == "ceil":
            rounding = ROUND_UP
        else:
            rounding = ROUND_HALF_UP
        
        quantizer = Decimal('0.1') ** decimals
        return float(d.quantize(quantizer, rounding=rounding))
    
    # ==================== DECISION TABLES ====================
    
    def _execute_decision_tables(
        self,
        tables: List[DecisionTable],
        context: RuleExecutionContext,
        result: RuleExecutionResult
    ):
        """Execute decision tables"""
        for table in tables:
            if not table.is_active:
                continue
            
            result.rules_executed.append(table.table_id)
            self.execution_log.append(f"Executing decision table: {table.table_name}")
            
            # Evaluate table
            table_result = self.evaluate_decision_table(table, result.output_data)
            
            if table_result.matched:
                result.rules_matched.append(table.table_id)
                
                # Apply output values
                for field_name, value in table_result.output_values.items():
                    result.output_data[field_name] = value
                    result.calculated_fields[field_name] = value
                
                self.execution_log.append(
                    f"Matched {table_result.match_count} row(s), "
                    f"applied {len(table_result.output_values)} output(s)"
                )
                
                # Execute on-match actions
                if table.on_match_actions:
                    for action in sorted(table.on_match_actions, key=lambda a: a.order):
                        self._execute_action(action, result)
            else:
                # No match - apply default values
                if table.default_values:
                    for field_name, value in table.default_values.items():
                        result.output_data[field_name] = value
                    self.execution_log.append("No match, applied default values")
                
                # Execute on-no-match actions
                if table.on_no_match_actions:
                    for action in sorted(table.on_no_match_actions, key=lambda a: a.order):
                        self._execute_action(action, result)
    
    def evaluate_decision_table(
        self,
        table: DecisionTable,
        data: Dict[str, Any]
    ) -> DecisionTableMatchResult:
        """Evaluate decision table and find matching rows"""
        matched_row_ids = []
        output_values = {}
        
        # Get input and output columns
        input_columns = [col for col in table.columns if col.column_type == TableColumnType.INPUT]
        output_columns = [col for col in table.columns if col.column_type == TableColumnType.OUTPUT]
        
        # Sort rows by order (priority)
        sorted_rows = sorted(table.rows, key=lambda r: r.row_order)
        
        # Evaluate each row
        for row in sorted_rows:
            if not row.is_active:
                continue
            
            # Check if row matches
            row_matches = self._evaluate_table_row(row, input_columns, data, table.match_all_inputs)
            
            if row_matches:
                matched_row_ids.append(row.row_id)
                
                # Extract output values from this row
                row_outputs = self._extract_row_outputs(row, output_columns)
                output_values.update(row_outputs)
                
                # If match_first, stop after first match
                if table.match_first:
                    break
        
        # Check for default row if no matches
        is_default = False
        if not matched_row_ids:
            default_row = next((r for r in sorted_rows if r.is_default), None)
            if default_row:
                matched_row_ids.append(default_row.row_id)
                row_outputs = self._extract_row_outputs(default_row, output_columns)
                output_values.update(row_outputs)
                is_default = True
        
        return DecisionTableMatchResult(
            matched=len(matched_row_ids) > 0,
            matched_row_ids=matched_row_ids,
            output_values=output_values,
            match_count=len(matched_row_ids),
            is_default=is_default
        )
    
    def _evaluate_table_row(
        self,
        row: TableRow,
        input_columns: List[TableColumn],
        data: Dict[str, Any],
        match_all: bool
    ) -> bool:
        """Check if a table row matches the data"""
        match_results = []
        
        for column in input_columns:
            # Find cell for this column
            cell = next((c for c in row.cells if c.column_id == column.column_id), None)
            
            if not cell:
                match_results.append(False)
                continue
            
            # Check if cell matches
            cell_matches = self._evaluate_table_cell(cell, column, data)
            match_results.append(cell_matches)
        
        # Apply match logic
        if match_all:
            return all(match_results) if match_results else False
        else:
            return any(match_results) if match_results else False
    
    def _evaluate_table_cell(
        self,
        cell: TableCell,
        column: TableColumn,
        data: Dict[str, Any]
    ) -> bool:
        """Check if a cell value matches the data"""
        # Get field value from data
        field_value = self._get_nested_value(data, column.field_name)
        
        # Handle special values
        if cell.is_any:
            return True  # Wildcard matches anything
        
        if cell.is_reject:
            return False  # Reject never matches
        
        # Handle range values
        if cell.is_range:
            return self._match_range(field_value, cell.value_min, cell.value_max)
        
        # Handle regular comparison
        return self._match_cell_value(field_value, cell.value, column.operator)
    
    def _match_range(self, value: Any, min_val: Any, max_val: Any) -> bool:
        """Check if value is in range"""
        try:
            if min_val is not None and max_val is not None:
                return min_val <= value <= max_val
            elif min_val is not None:
                return value >= min_val
            elif max_val is not None:
                return value <= max_val
            return False
        except (TypeError, ValueError):
            return False
    
    def _match_cell_value(
        self,
        field_value: Any,
        cell_value: Any,
        operator: OperatorType
    ) -> bool:
        """Match cell value using operator"""
        try:
            if operator == OperatorType.EQUALS:
                return field_value == cell_value
            elif operator == OperatorType.NOT_EQUALS:
                return field_value != cell_value
            elif operator == OperatorType.GREATER_THAN:
                return field_value > cell_value
            elif operator == OperatorType.GREATER_THAN_OR_EQUAL:
                return field_value >= cell_value
            elif operator == OperatorType.LESS_THAN:
                return field_value < cell_value
            elif operator == OperatorType.LESS_THAN_OR_EQUAL:
                return field_value <= cell_value
            elif operator == OperatorType.CONTAINS:
                return cell_value in str(field_value)
            elif operator == OperatorType.IN:
                return field_value in cell_value
            elif operator == OperatorType.BETWEEN:
                # For BETWEEN, cell_value should be tuple/list [min, max]
                if isinstance(cell_value, (list, tuple)) and len(cell_value) == 2:
                    return cell_value[0] <= field_value <= cell_value[1]
            return False
        except (TypeError, ValueError):
            return False
    
    def _extract_row_outputs(
        self,
        row: TableRow,
        output_columns: List[TableColumn]
    ) -> Dict[str, Any]:
        """Extract output values from row"""
        outputs = {}
        
        for column in output_columns:
            cell = next((c for c in row.cells if c.column_id == column.column_id), None)
            if cell and not cell.is_reject:
                outputs[column.field_name] = cell.value
        
        return outputs
