"""
Rule Library

Pre-built rule templates, RBI guidelines, and template management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import copy

from backend.services.rules.rule_models import (
    RuleSet, RuleTemplate, RuleClone, DecisionRule, ValidationRule,
    CalculationRule, RoutingRule, PricingRule, EligibilityRule,
    RulePriority
)


class RuleLibrary:
    """Library of pre-built rule templates"""
    
    def __init__(self):
        self.templates: Dict[str, RuleTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize pre-built templates"""
        # RBI Guideline Templates
        self._add_rbi_templates()
        
        # Loan Eligibility Templates
        self._add_loan_eligibility_templates()
        
        # Credit Assessment Templates
        self._add_credit_assessment_templates()
        
        # Compliance Templates
        self._add_compliance_templates()
        
        # Pricing Templates
        self._add_pricing_templates()
        
        # Risk Assessment Templates
        self._add_risk_assessment_templates()
    
    def _add_rbi_templates(self):
        """Add RBI guideline rule templates"""
        
        # RBI - Age Validation
        self._create_template(
            template_id="rbi_age_validation",
            template_name="RBI Age Validation",
            category="rbi_compliance",
            description="Validates borrower age as per RBI guidelines (18-70 years)",
            rule_template={
                "rule_type": "validation",
                "entity_type": "loan_application",
                "priority": RulePriority.CRITICAL.value,
                "conditions": [
                    {
                        "field": "applicant.age",
                        "operator": ">=",
                        "value": 18
                    },
                    {
                        "field": "applicant.age",
                        "operator": "<=",
                        "value": 70
                    }
                ],
                "error_message": "Applicant age must be between 18-70 years as per RBI guidelines",
                "severity": "error"
            },
            tags=["rbi", "compliance", "age", "eligibility"],
            compliance_tags=["RBI_NBFC_Guidelines", "KYC_Requirements"]
        )
        
        # RBI - Income Validation
        self._create_template(
            template_id="rbi_income_validation",
            template_name="RBI Minimum Income Validation",
            category="rbi_compliance",
            description="Validates minimum income requirements for loan eligibility",
            rule_template={
                "rule_type": "validation",
                "entity_type": "loan_application",
                "priority": RulePriority.HIGH.value,
                "conditions": [
                    {
                        "field": "applicant.monthly_income",
                        "operator": ">=",
                        "value": 15000
                    }
                ],
                "error_message": "Minimum monthly income of ₹15,000 required",
                "severity": "error"
            },
            tags=["rbi", "compliance", "income", "eligibility"],
            compliance_tags=["RBI_NBFC_Guidelines", "Income_Requirements"]
        )
        
        # RBI - FOIR (Fixed Obligation to Income Ratio)
        self._create_template(
            template_id="rbi_foir_check",
            template_name="RBI FOIR Compliance Check",
            category="rbi_compliance",
            description="Validates FOIR does not exceed 50% as per RBI guidelines",
            rule_template={
                "rule_type": "calculation",
                "entity_type": "loan_application",
                "priority": RulePriority.CRITICAL.value,
                "output_field": "foir_percentage",
                "formula": "(applicant.monthly_obligations / applicant.monthly_income) * 100",
                "validation": {
                    "max_value": 50,
                    "error_message": "FOIR exceeds 50% limit as per RBI guidelines"
                }
            },
            tags=["rbi", "compliance", "foir", "dti"],
            compliance_tags=["RBI_NBFC_Guidelines", "FOIR_Limits"]
        )
        
        # RBI - LTV Ratio
        self._create_template(
            template_id="rbi_ltv_ratio",
            template_name="RBI LTV Ratio Check",
            category="rbi_compliance",
            description="Validates Loan-to-Value ratio as per RBI norms",
            rule_template={
                "rule_type": "calculation",
                "entity_type": "loan_application",
                "priority": RulePriority.CRITICAL.value,
                "output_field": "ltv_ratio",
                "formula": "(loan_amount / property_value) * 100",
                "validation": {
                    "max_value": 90,
                    "error_message": "LTV ratio exceeds 90% limit"
                }
            },
            tags=["rbi", "compliance", "ltv", "property_loan"],
            compliance_tags=["RBI_NBFC_Guidelines", "LTV_Limits"]
        )
    
    def _add_loan_eligibility_templates(self):
        """Add loan eligibility rule templates"""
        
        # Credit Score Eligibility
        self._create_template(
            template_id="credit_score_eligibility",
            template_name="Credit Score Eligibility Check",
            category="loan_eligibility",
            description="Validates minimum credit score for loan approval",
            rule_template={
                "rule_type": "eligibility",
                "entity_type": "loan_application",
                "priority": RulePriority.HIGH.value,
                "criteria": [
                    {
                        "field": "applicant.credit_score",
                        "operator": ">=",
                        "value": 650,
                        "weight": 40
                    }
                ],
                "approval_threshold": 70,
                "rejection_message": "Credit score below minimum requirement (650)"
            },
            tags=["eligibility", "credit_score", "loan"],
            compliance_tags=[]
        )
        
        # Employment Stability
        self._create_template(
            template_id="employment_stability",
            template_name="Employment Stability Check",
            category="loan_eligibility",
            description="Validates minimum employment tenure",
            rule_template={
                "rule_type": "eligibility",
                "entity_type": "loan_application",
                "priority": RulePriority.MEDIUM.value,
                "criteria": [
                    {
                        "field": "applicant.employment_months",
                        "operator": ">=",
                        "value": 12,
                        "weight": 30
                    }
                ],
                "approval_threshold": 60,
                "rejection_message": "Minimum 12 months employment required"
            },
            tags=["eligibility", "employment", "stability"],
            compliance_tags=[]
        )
    
    def _add_credit_assessment_templates(self):
        """Add credit assessment rule templates"""
        
        # Risk-Based Pricing
        self._create_template(
            template_id="risk_based_pricing",
            template_name="Risk-Based Interest Rate",
            category="credit_assessment",
            description="Calculates interest rate based on credit risk",
            rule_template={
                "rule_type": "decision",
                "entity_type": "loan_application",
                "priority": RulePriority.HIGH.value,
                "conditions": [
                    {
                        "field": "applicant.credit_score",
                        "operator": ">=",
                        "value": 750
                    }
                ],
                "output_field": "interest_rate",
                "output_value": 10.5,
                "else_conditions": [
                    {
                        "conditions": [{"field": "applicant.credit_score", "operator": ">=", "value": 700}],
                        "output_value": 11.5
                    },
                    {
                        "conditions": [{"field": "applicant.credit_score", "operator": ">=", "value": 650}],
                        "output_value": 12.5
                    }
                ],
                "default_output": 14.0
            },
            tags=["pricing", "interest_rate", "credit_risk"],
            compliance_tags=[]
        )
    
    def _add_compliance_templates(self):
        """Add compliance rule templates"""
        
        # KYC Completeness Check
        self._create_template(
            template_id="kyc_completeness",
            template_name="KYC Completeness Validation",
            category="compliance",
            description="Validates all KYC documents are submitted",
            rule_template={
                "rule_type": "validation",
                "entity_type": "loan_application",
                "priority": RulePriority.CRITICAL.value,
                "conditions": [
                    {"field": "kyc.pan_card", "operator": "is_not_null"},
                    {"field": "kyc.aadhar_card", "operator": "is_not_null"},
                    {"field": "kyc.address_proof", "operator": "is_not_null"},
                    {"field": "kyc.photo", "operator": "is_not_null"}
                ],
                "error_message": "Incomplete KYC documentation",
                "severity": "error"
            },
            tags=["compliance", "kyc", "documentation"],
            compliance_tags=["KYC_Requirements", "RBI_Guidelines"]
        )
    
    def _add_pricing_templates(self):
        """Add pricing rule templates"""
        
        # Loan Amount-Based Pricing
        self._create_template(
            template_id="loan_amount_pricing",
            template_name="Loan Amount-Based Pricing",
            category="pricing",
            description="Adjusts pricing based on loan amount tiers",
            rule_template={
                "rule_type": "pricing",
                "entity_type": "loan_application",
                "priority": RulePriority.MEDIUM.value,
                "pricing_tiers": [
                    {"min_amount": 1000000, "rate_adjustment": -0.5},
                    {"min_amount": 500000, "rate_adjustment": -0.25},
                    {"min_amount": 0, "rate_adjustment": 0}
                ],
                "base_rate_field": "base_interest_rate",
                "output_field": "final_interest_rate"
            },
            tags=["pricing", "loan_amount", "tiered_pricing"],
            compliance_tags=[]
        )
    
    def _add_risk_assessment_templates(self):
        """Add risk assessment rule templates"""
        
        # Comprehensive Risk Score
        self._create_template(
            template_id="comprehensive_risk_score",
            template_name="Comprehensive Risk Score Calculation",
            category="risk_assessment",
            description="Calculates overall risk score from multiple factors",
            rule_template={
                "rule_type": "calculation",
                "entity_type": "loan_application",
                "priority": RulePriority.HIGH.value,
                "output_field": "risk_score",
                "formula": """
                    (credit_score_weight * normalize(applicant.credit_score, 300, 900)) +
                    (income_weight * normalize(applicant.monthly_income, 15000, 200000)) +
                    (employment_weight * normalize(applicant.employment_months, 0, 120)) +
                    (foir_weight * (100 - foir_percentage))
                """,
                "parameters": {
                    "credit_score_weight": 0.4,
                    "income_weight": 0.25,
                    "employment_weight": 0.15,
                    "foir_weight": 0.2
                }
            },
            tags=["risk", "score", "assessment"],
            compliance_tags=[]
        )
    
    def _create_template(
        self,
        template_id: str,
        template_name: str,
        category: str,
        description: str,
        rule_template: Dict[str, Any],
        tags: List[str],
        compliance_tags: List[str]
    ):
        """Create and store a template"""
        template = RuleTemplate(
            template_id=template_id,
            template_name=template_name,
            description=description,
            category=category,
            rule_template=rule_template,
            tags=tags,
            compliance_tags=compliance_tags,
            usage_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.templates[template_id] = template
    
    # ==================== PUBLIC METHODS ====================
    
    def get_all_templates(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[RuleTemplate]:
        """Get all templates with optional filtering"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if tags:
            templates = [
                t for t in templates
                if any(tag in t.tags for tag in tags)
            ]
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[RuleTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def search_templates(
        self,
        search_term: str,
        categories: Optional[List[str]] = None
    ) -> List[RuleTemplate]:
        """Search templates by name or description"""
        search_lower = search_term.lower()
        results = []
        
        for template in self.templates.values():
            if categories and template.category not in categories:
                continue
            
            if (search_lower in template.template_name.lower() or
                search_lower in template.description.lower() or
                any(search_lower in tag for tag in template.tags)):
                results.append(template)
        
        return results
    
    def clone_template(
        self,
        template_id: str,
        new_name: str,
        modifications: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> RuleClone:
        """Clone a template with optional modifications"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Create clone record
        clone_id = f"clone_{uuid.uuid4().hex[:12]}"
        cloned_template = copy.deepcopy(template.rule_template)
        
        # Apply modifications
        if modifications:
            cloned_template.update(modifications)
        
        clone = RuleClone(
            clone_id=clone_id,
            source_template_id=template_id,
            cloned_name=new_name,
            cloned_rule=cloned_template,
            modifications=modifications or {},
            cloned_at=datetime.utcnow(),
            cloned_by=user_id
        )
        
        # Increment usage count
        template.usage_count += 1
        template.updated_at = datetime.utcnow()
        
        return clone
    
    def create_ruleset_from_template(
        self,
        template_id: str,
        ruleset_name: str,
        entity_type: str,
        modifications: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> RuleSet:
        """Create a complete ruleset from template"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        rule_template = copy.deepcopy(template.rule_template)
        
        # Apply modifications
        if modifications:
            rule_template.update(modifications)
        
        # Create appropriate rule based on type
        rule_type = rule_template.get("rule_type")
        rule_id = f"rule_{uuid.uuid4().hex[:12]}"
        
        rules_dict = {
            "decision_rules": [],
            "validation_rules": [],
            "calculation_rules": [],
            "routing_rules": [],
            "pricing_rules": [],
            "eligibility_rules": []
        }
        
        if rule_type == "decision":
            rule = DecisionRule(
                rule_id=rule_id,
                rule_name=ruleset_name,
                entity_type=entity_type,
                priority=rule_template.get("priority", RulePriority.MEDIUM.value),
                conditions=rule_template.get("conditions", []),
                output_field=rule_template.get("output_field"),
                output_value=rule_template.get("output_value")
            )
            rules_dict["decision_rules"].append(rule)
        
        elif rule_type == "validation":
            rule = ValidationRule(
                rule_id=rule_id,
                rule_name=ruleset_name,
                entity_type=entity_type,
                priority=rule_template.get("priority", RulePriority.MEDIUM.value),
                conditions=rule_template.get("conditions", []),
                error_message=rule_template.get("error_message", "Validation failed"),
                severity=rule_template.get("severity", "error")
            )
            rules_dict["validation_rules"].append(rule)
        
        elif rule_type == "calculation":
            rule = CalculationRule(
                rule_id=rule_id,
                rule_name=ruleset_name,
                entity_type=entity_type,
                priority=rule_template.get("priority", RulePriority.MEDIUM.value),
                output_field=rule_template.get("output_field"),
                formula=rule_template.get("formula", ""),
                parameters=rule_template.get("parameters", {})
            )
            rules_dict["calculation_rules"].append(rule)
        
        elif rule_type == "eligibility":
            rule = EligibilityRule(
                rule_id=rule_id,
                rule_name=ruleset_name,
                entity_type=entity_type,
                priority=rule_template.get("priority", RulePriority.MEDIUM.value),
                criteria=rule_template.get("criteria", []),
                approval_threshold=rule_template.get("approval_threshold", 70),
                rejection_message=rule_template.get("rejection_message", "Not eligible")
            )
            rules_dict["eligibility_rules"].append(rule)
        
        elif rule_type == "pricing":
            rule = PricingRule(
                rule_id=rule_id,
                rule_name=ruleset_name,
                entity_type=entity_type,
                priority=rule_template.get("priority", RulePriority.MEDIUM.value),
                pricing_tiers=rule_template.get("pricing_tiers", []),
                base_rate_field=rule_template.get("base_rate_field"),
                output_field=rule_template.get("output_field")
            )
            rules_dict["pricing_rules"].append(rule)
        
        # Create ruleset
        ruleset = RuleSet(
            ruleset_id=f"ruleset_{uuid.uuid4().hex[:12]}",
            ruleset_name=ruleset_name,
            entity_type=entity_type,
            decision_rules=rules_dict["decision_rules"],
            validation_rules=rules_dict["validation_rules"],
            calculation_rules=rules_dict["calculation_rules"],
            routing_rules=rules_dict["routing_rules"],
            pricing_rules=rules_dict["pricing_rules"],
            eligibility_rules=rules_dict["eligibility_rules"],
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        # Increment usage count
        template.usage_count += 1
        template.updated_at = datetime.utcnow()
        
        return ruleset
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = set()
        for template in self.templates.values():
            categories.add(template.category)
        return sorted(list(categories))
    
    def get_compliance_tags(self) -> List[str]:
        """Get all unique compliance tags"""
        tags = set()
        for template in self.templates.values():
            tags.update(template.compliance_tags)
        return sorted(list(tags))
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get template library statistics"""
        total_templates = len(self.templates)
        
        category_counts = {}
        total_usage = 0
        
        for template in self.templates.values():
            category_counts[template.category] = category_counts.get(template.category, 0) + 1
            total_usage += template.usage_count
        
        return {
            "total_templates": total_templates,
            "categories": category_counts,
            "total_usage": total_usage,
            "most_used": sorted(
                self.templates.values(),
                key=lambda t: t.usage_count,
                reverse=True
            )[:5]
        }


# Global instance
rule_library = RuleLibrary()
