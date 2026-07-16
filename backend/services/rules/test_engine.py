"""
Rule Testing Engine

Handles dry-run, what-if analysis, and impact assessment
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import copy

from backend.services.rules.rule_models import (
    RuleSet, RuleTestCase, RuleTestResult, ImpactAssessment,
    RuleExecutionContext, RuleExecutionResult
)
from backend.services.rules.rule_engine import RuleEngine


class TestEngine:
    """Engine for testing rules"""
    
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.test_cases: Dict[str, RuleTestCase] = {}
        self.test_results: List[RuleTestResult] = []
    
    def execute_dry_run(
        self,
        ruleset: RuleSet,
        test_case: RuleTestCase,
        user_id: Optional[int] = None
    ) -> RuleTestResult:
        """Execute test in dry-run mode (no side effects)"""
        
        # Create execution context
        context = RuleExecutionContext(
            context_id=f"test_{test_case.test_case_id}",
            entity_type=ruleset.entity_type,
            data=copy.deepcopy(test_case.input_data),
            tenant_id=1  # Test tenant
        )
        
        # Execute rules
        start_time = datetime.utcnow()
        execution_result = self.rule_engine.execute_ruleset(ruleset, context)
        end_time = datetime.utcnow()
        
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        # Evaluate assertions
        assertions_passed, assertions_failed, assertion_details = self._evaluate_assertions(
            test_case.assertions,
            execution_result
        )
        
        # Compare with expected output
        matches_expected = None
        output_diff = None
        if test_case.expected_output:
            matches_expected, output_diff = self._compare_with_expected(
                execution_result.output_data,
                test_case.expected_output
            )
        
        # Create test result
        test_result = RuleTestResult(
            test_result_id=f"result_{uuid.uuid4().hex[:12]}",
            test_case_id=test_case.test_case_id,
            ruleset_id=ruleset.ruleset_id,
            version_id=test_case.version_id,
            execution_mode="dry_run",
            passed=assertions_failed == 0 and (matches_expected if matches_expected is not None else True),
            execution_result=execution_result,
            assertions_passed=assertions_passed,
            assertions_failed=assertions_failed,
            assertion_details=assertion_details,
            execution_time_ms=execution_time,
            matches_expected=matches_expected,
            output_diff=output_diff,
            executed_at=datetime.utcnow(),
            executed_by=user_id
        )
        
        self.test_results.append(test_result)
        return test_result
    
    def execute_what_if(
        self,
        ruleset: RuleSet,
        input_data: Dict[str, Any],
        modifications: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute what-if analysis with data modifications"""
        
        # Create base execution
        base_context = RuleExecutionContext(
            context_id=f"whatif_base_{uuid.uuid4().hex[:8]}",
            entity_type=ruleset.entity_type,
            data=copy.deepcopy(input_data),
            tenant_id=1
        )
        base_result = self.rule_engine.execute_ruleset(ruleset, base_context)
        
        # Create modified execution
        modified_data = copy.deepcopy(input_data)
        modified_data.update(modifications)
        
        modified_context = RuleExecutionContext(
            context_id=f"whatif_mod_{uuid.uuid4().hex[:8]}",
            entity_type=ruleset.entity_type,
            data=modified_data,
            tenant_id=1
        )
        modified_result = self.rule_engine.execute_ruleset(ruleset, modified_context)
        
        # Compare results
        comparison = self._compare_execution_results(base_result, modified_result)
        
        return {
            'base_result': base_result.dict(),
            'modified_result': modified_result.dict(),
            'modifications': modifications,
            'comparison': comparison,
            'impact_summary': self._summarize_impact(comparison)
        }
    
    def execute_impact_assessment(
        self,
        current_ruleset: RuleSet,
        new_ruleset: RuleSet,
        sample_data: List[Dict[str, Any]],
        user_id: Optional[int] = None
    ) -> ImpactAssessment:
        """Assess impact of rule changes on sample data"""
        
        assessment_id = f"assess_{uuid.uuid4().hex[:12]}",
        
        # Execute with current ruleset
        current_results = []
        for data in sample_data:
            context = RuleExecutionContext(
                context_id=f"current_{uuid.uuid4().hex[:8]}",
                entity_type=current_ruleset.entity_type,
                data=copy.deepcopy(data),
                tenant_id=1
            )
            result = self.rule_engine.execute_ruleset(current_ruleset, context)
            current_results.append(result.output_data)
        
        # Execute with new ruleset
        new_results = []
        for data in sample_data:
            context = RuleExecutionContext(
                context_id=f"new_{uuid.uuid4().hex[:8]}",
                entity_type=new_ruleset.entity_type,
                data=copy.deepcopy(data),
                tenant_id=1
            )
            result = self.rule_engine.execute_ruleset(new_ruleset, context)
            new_results.append(result.output_data)
        
        # Analyze differences
        affected_count = 0
        result_changes = []
        output_differences = []
        
        for i, (current, new) in enumerate(zip(current_results, new_results)):
            if current != new:
                affected_count += 1
                
                differences = self._get_output_differences(current, new)
                if differences:
                    result_changes.append({
                        'sample_index': i,
                        'input_data': sample_data[i],
                        'changes': differences
                    })
                    output_differences.extend(differences)
        
        affected_percentage = (affected_count / len(sample_data)) * 100 if sample_data else 0
        
        # Assess risk
        risk_level, risk_factors = self._assess_risk(
            affected_percentage,
            result_changes,
            current_ruleset,
            new_ruleset
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level,
            affected_percentage,
            result_changes
        )
        
        assessment = ImpactAssessment(
            assessment_id=assessment_id[0] if isinstance(assessment_id, tuple) else assessment_id,
            ruleset_id=new_ruleset.ruleset_id,
            version_id=new_ruleset.version if hasattr(new_ruleset, 'version') else '1.0',
            assessment_type="before_activation",
            sample_size=len(sample_data),
            sample_data=sample_data,
            current_results=[{'output': r} for r in current_results],
            new_results=[{'output': r} for r in new_results],
            affected_count=affected_count,
            affected_percentage=affected_percentage,
            result_changes=result_changes,
            output_differences=output_differences,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
            assessed_at=datetime.utcnow(),
            assessed_by=user_id
        )
        
        return assessment
    
    def batch_test(
        self,
        ruleset: RuleSet,
        test_cases: List[RuleTestCase],
        user_id: Optional[int] = None
    ) -> List[RuleTestResult]:
        """Execute multiple test cases"""
        results = []
        
        for test_case in test_cases:
            result = self.execute_dry_run(ruleset, test_case, user_id)
            results.append(result)
        
        return results
    
    def create_test_case(
        self,
        test_case_name: str,
        ruleset_id: str,
        input_data: Dict[str, Any],
        expected_output: Optional[Dict[str, Any]] = None,
        assertions: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[int] = None
    ) -> RuleTestCase:
        """Create new test case"""
        
        test_case = RuleTestCase(
            test_case_id=f"test_{uuid.uuid4().hex[:12]}",
            test_case_name=test_case_name,
            input_data=input_data,
            expected_output=expected_output,
            ruleset_id=ruleset_id,
            assertions=assertions or [],
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        self.test_cases[test_case.test_case_id] = test_case
        return test_case
    
    # ==================== HELPER METHODS ====================
    
    def _evaluate_assertions(
        self,
        assertions: List[Dict[str, Any]],
        execution_result: RuleExecutionResult
    ) -> tuple:
        """Evaluate test assertions"""
        passed = 0
        failed = 0
        details = []
        
        for assertion in assertions:
            assertion_type = assertion.get('type')
            field = assertion.get('field')
            expected = assertion.get('expected')
            operator = assertion.get('operator', 'equals')
            
            actual = execution_result.output_data.get(field)
            
            result = self._evaluate_assertion(actual, expected, operator)
            
            if result:
                passed += 1
            else:
                failed += 1
            
            details.append({
                'assertion': assertion,
                'passed': result,
                'actual_value': actual,
                'expected_value': expected
            })
        
        return passed, failed, details
    
    def _evaluate_assertion(
        self,
        actual: Any,
        expected: Any,
        operator: str
    ) -> bool:
        """Evaluate single assertion"""
        if operator == 'equals':
            return actual == expected
        elif operator == 'not_equals':
            return actual != expected
        elif operator == 'greater_than':
            return actual > expected
        elif operator == 'greater_than_or_equal':
            return actual >= expected
        elif operator == 'less_than':
            return actual < expected
        elif operator == 'less_than_or_equal':
            return actual <= expected
        elif operator == 'contains':
            return expected in str(actual)
        elif operator == 'not_contains':
            return expected not in str(actual)
        elif operator == 'is_null':
            return actual is None
        elif operator == 'is_not_null':
            return actual is not None
        else:
            return actual == expected
    
    def _compare_with_expected(
        self,
        actual: Dict[str, Any],
        expected: Dict[str, Any]
    ) -> tuple:
        """Compare actual output with expected"""
        matches = True
        diff = {}
        
        all_keys = set(actual.keys()) | set(expected.keys())
        
        for key in all_keys:
            actual_value = actual.get(key)
            expected_value = expected.get(key)
            
            if actual_value != expected_value:
                matches = False
                diff[key] = {
                    'actual': actual_value,
                    'expected': expected_value
                }
        
        return matches, diff if not matches else None
    
    def _compare_execution_results(
        self,
        result1: RuleExecutionResult,
        result2: RuleExecutionResult
    ) -> Dict[str, Any]:
        """Compare two execution results"""
        comparison = {
            'output_changed': result1.output_data != result2.output_data,
            'rules_executed_changed': result1.rules_executed != result2.rules_executed,
            'validation_changed': result1.validation_errors != result2.validation_errors,
            'field_changes': {}
        }
        
        # Compare output fields
        all_keys = set(result1.output_data.keys()) | set(result2.output_data.keys())
        for key in all_keys:
            val1 = result1.output_data.get(key)
            val2 = result2.output_data.get(key)
            if val1 != val2:
                comparison['field_changes'][key] = {
                    'before': val1,
                    'after': val2
                }
        
        return comparison
    
    def _summarize_impact(self, comparison: Dict[str, Any]) -> str:
        """Summarize impact of changes"""
        if not comparison['output_changed']:
            return "No impact on output"
        
        changed_fields = len(comparison['field_changes'])
        
        if changed_fields == 0:
            return "Output structure changed but values remain same"
        elif changed_fields == 1:
            return f"1 field affected"
        else:
            return f"{changed_fields} fields affected"
    
    def _get_output_differences(
        self,
        current: Dict[str, Any],
        new: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get differences between outputs"""
        differences = []
        
        all_keys = set(current.keys()) | set(new.keys())
        
        for key in all_keys:
            current_value = current.get(key)
            new_value = new.get(key)
            
            if current_value != new_value:
                differences.append({
                    'field': key,
                    'current_value': current_value,
                    'new_value': new_value,
                    'change_type': 'modified' if key in current and key in new else ('added' if key not in current else 'removed')
                })
        
        return differences
    
    def _assess_risk(
        self,
        affected_percentage: float,
        result_changes: List[Dict[str, Any]],
        current_ruleset: RuleSet,
        new_ruleset: RuleSet
    ) -> tuple:
        """Assess risk level"""
        risk_factors = []
        
        # Check affected percentage
        if affected_percentage > 50:
            risk_factors.append(f"High impact: {affected_percentage:.1f}% of samples affected")
        elif affected_percentage > 25:
            risk_factors.append(f"Medium impact: {affected_percentage:.1f}% of samples affected")
        
        # Check for critical field changes
        critical_fields = ['approved', 'eligible', 'amount', 'rate', 'status']
        for change in result_changes:
            for diff in change.get('changes', []):
                if diff['field'] in critical_fields:
                    risk_factors.append(f"Critical field changed: {diff['field']}")
        
        # Check number of rule changes
        current_rule_count = len(current_ruleset.decision_rules) + len(current_ruleset.validation_rules)
        new_rule_count = len(new_ruleset.decision_rules) + len(new_ruleset.validation_rules)
        
        if abs(new_rule_count - current_rule_count) > 5:
            risk_factors.append(f"Significant rule count change: {current_rule_count} → {new_rule_count}")
        
        # Determine risk level
        if len(risk_factors) >= 3 or affected_percentage > 75:
            risk_level = "critical"
        elif len(risk_factors) >= 2 or affected_percentage > 50:
            risk_level = "high"
        elif len(risk_factors) >= 1 or affected_percentage > 25:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return risk_level, risk_factors
    
    def _generate_recommendations(
        self,
        risk_level: str,
        affected_percentage: float,
        result_changes: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on risk"""
        recommendations = []
        
        if risk_level == "critical":
            recommendations.append("⚠️ CRITICAL: Conduct thorough review before activation")
            recommendations.append("Perform extensive testing with production-like data")
            recommendations.append("Consider gradual rollout strategy")
            recommendations.append("Have rollback plan ready")
        elif risk_level == "high":
            recommendations.append("⚠️ HIGH RISK: Additional testing recommended")
            recommendations.append("Review all affected scenarios carefully")
            recommendations.append("Notify stakeholders before activation")
        elif risk_level == "medium":
            recommendations.append("⚠️ MODERATE RISK: Standard testing procedures apply")
            recommendations.append("Document expected changes")
        else:
            recommendations.append("✅ LOW RISK: Changes appear safe to activate")
        
        if affected_percentage > 0:
            recommendations.append(f"Test with larger sample size (current: affected {affected_percentage:.1f}%)")
        
        return recommendations


# Global instance
test_engine = TestEngine()
