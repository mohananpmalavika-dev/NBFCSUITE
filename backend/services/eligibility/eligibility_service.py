"""
Eligibility Rules Service
Business logic for managing and evaluating eligibility rules
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import uuid

from .eligibility_models import (
    EligibilityRule, EligibilityRuleFilter, EligibilityRuleSummary,
    EligibilityStats, EligibilityRuleClone, RuleStatus,
    EligibilityCheckRequest, EligibilityCheckResponse,
    CustomerData, EligibilityResult, EligibilityCriteriaResult,
    BulkEligibilityCheckRequest, BulkEligibilityCheckResponse,
    EmploymentType, ResidencyStatus
)


class EligibilityService:
    """Service for eligibility rule management and evaluation"""
    
    def __init__(self):
        """Initialize service"""
        self.rules_storage: Dict[str, EligibilityRule] = {}
        self.checks_performed: int = 0
    
    # ========================================================================
    # CRUD OPERATIONS
    # ========================================================================
    
    def create_rule(
        self,
        rule_data: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> EligibilityRule:
        """Create new eligibility rule"""
        # Generate ID
        rule_id = str(uuid.uuid4())
        
        # Check if rule code already exists
        if any(r.rule_code == rule_data.get('rule_code') 
               for r in self.rules_storage.values() 
               if r.tenant_id == tenant_id):
            raise ValueError(f"Rule code {rule_data.get('rule_code')} already exists")
        
        # Create rule
        rule = EligibilityRule(
            id=rule_id,
            tenant_id=tenant_id,
            **rule_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        
        # Store rule
        self.rules_storage[rule_id] = rule
        
        return rule
    
    def get_rule(self, rule_id: str, tenant_id: str) -> EligibilityRule:
        """Get eligibility rule by ID"""
        rule = self.rules_storage.get(rule_id)
        if not rule or rule.tenant_id != tenant_id:
            raise ValueError(f"Rule {rule_id} not found")
        return rule
    
    def get_rule_by_code(self, rule_code: str, tenant_id: str) -> EligibilityRule:
        """Get eligibility rule by code"""
        for rule in self.rules_storage.values():
            if rule.tenant_id == tenant_id and rule.rule_code == rule_code:
                return rule
        raise ValueError(f"Rule with code {rule_code} not found")
    
    def update_rule(
        self,
        rule_id: str,
        rule_data: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> EligibilityRule:
        """Update eligibility rule"""
        rule = self.get_rule(rule_id, tenant_id)
        
        # Update fields
        for key, value in rule_data.items():
            if hasattr(rule, key) and key not in ['id', 'tenant_id', 'created_at', 'created_by']:
                setattr(rule, key, value)
        
        rule.updated_at = datetime.utcnow()
        rule.updated_by = user_id
        
        self.rules_storage[rule_id] = rule
        return rule
    
    def delete_rule(self, rule_id: str, tenant_id: str) -> None:
        """Delete eligibility rule"""
        rule = self.get_rule(rule_id, tenant_id)
        del self.rules_storage[rule_id]
    
    def list_rules(
        self,
        tenant_id: str,
        filters: Optional[EligibilityRuleFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[EligibilityRule]:
        """List eligibility rules with filters"""
        rules = [r for r in self.rules_storage.values() if r.tenant_id == tenant_id]
        
        # Apply filters
        if filters:
            if filters.status:
                rules = [r for r in rules if r.status == filters.status]
            if filters.product_id:
                rules = [r for r in rules if r.product_id == filters.product_id]
            if filters.product_code:
                rules = [r for r in rules if r.product_code == filters.product_code]
            if filters.effective_date_from:
                rules = [r for r in rules if r.effective_date >= filters.effective_date_from]
            if filters.effective_date_to:
                rules = [r for r in rules if r.effective_date <= filters.effective_date_to]
            if filters.search_term:
                term = filters.search_term.lower()
                rules = [r for r in rules if 
                        term in r.rule_code.lower() or 
                        term in r.rule_name.lower() or 
                        term in r.description.lower()]
        
        # Sort by priority and date
        rules.sort(key=lambda r: (r.priority, r.created_at), reverse=False)
        
        return rules[skip:skip + limit]
    
    # ========================================================================
    # RULE OPERATIONS
    # ========================================================================
    
    def clone_rule(
        self,
        rule_id: str,
        clone_data: EligibilityRuleClone,
        tenant_id: str,
        user_id: str
    ) -> EligibilityRule:
        """Clone eligibility rule"""
        original_rule = self.get_rule(rule_id, tenant_id)
        
        # Create new rule data
        rule_data = original_rule.dict(exclude={'id', 'created_at', 'updated_at', 'created_by', 'updated_by'})
        rule_data['rule_code'] = clone_data.new_rule_code
        rule_data['rule_name'] = clone_data.new_rule_name or f"{original_rule.rule_name} (Copy)"
        if clone_data.new_product_id:
            rule_data['product_id'] = clone_data.new_product_id
        rule_data['status'] = RuleStatus.DRAFT
        
        return self.create_rule(rule_data, tenant_id, user_id)
    
    def activate_rule(self, rule_id: str, tenant_id: str, user_id: str) -> EligibilityRule:
        """Activate eligibility rule"""
        rule = self.get_rule(rule_id, tenant_id)
        rule.status = RuleStatus.ACTIVE
        rule.updated_at = datetime.utcnow()
        rule.updated_by = user_id
        self.rules_storage[rule_id] = rule
        return rule
    
    def deactivate_rule(self, rule_id: str, tenant_id: str, user_id: str) -> EligibilityRule:
        """Deactivate eligibility rule"""
        rule = self.get_rule(rule_id, tenant_id)
        rule.status = RuleStatus.INACTIVE
        rule.updated_at = datetime.utcnow()
        rule.updated_by = user_id
        self.rules_storage[rule_id] = rule
        return rule
    
    # ========================================================================
    # ELIGIBILITY CHECKING ENGINE
    # ========================================================================
    
    def check_eligibility(
        self,
        request: EligibilityCheckRequest,
        tenant_id: str,
        user_id: Optional[str] = None
    ) -> EligibilityCheckResponse:
        """Check customer eligibility against rule"""
        # Get rule
        if request.rule_id:
            rule = self.get_rule(request.rule_id, tenant_id)
        elif request.rule_code:
            rule = self.get_rule_by_code(request.rule_code, tenant_id)
        elif request.product_id:
            # Find rule by product
            rule = self._find_rule_by_product(request.product_id, tenant_id)
        else:
            raise ValueError("Must provide rule_id, rule_code, or product_id")
        
        # Increment check counter
        self.checks_performed += 1
        
        # Perform checks
        customer_results = self._check_customer_eligibility(
            rule.customer_eligibility,
            request.customer_data
        )
        
        financial_results = self._check_financial_eligibility(
            rule.financial_eligibility,
            request.customer_data,
            request.loan_amount,
            request.proposed_emi
        )
        
        geographic_results = self._check_geographic_eligibility(
            rule.geographic_eligibility,
            request.customer_data
        )
        
        # Combine results
        all_results = customer_results + financial_results + geographic_results
        total_count = len(all_results)
        passed_count = sum(1 for r in all_results if r.passed)
        failed_count = sum(1 for r in all_results if not r.passed and r.severity == "ERROR")
        warning_count = sum(1 for r in all_results if not r.passed and r.severity == "WARNING")
        
        # Calculate overall score
        overall_score = (passed_count / total_count * 100) if total_count > 0 else 0
        
        # Determine result
        if failed_count == 0:
            if warning_count > 0:
                result = EligibilityResult.CONDITIONAL
            else:
                result = EligibilityResult.ELIGIBLE
        else:
            if rule.allow_manual_override:
                result = EligibilityResult.MANUAL_REVIEW
            else:
                result = EligibilityResult.NOT_ELIGIBLE
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_results, request.customer_data)
        
        # Generate required documents
        required_documents = self._generate_required_documents(rule, request.customer_data)
        
        return EligibilityCheckResponse(
            rule_id=rule.id,
            rule_code=rule.rule_code,
            rule_name=rule.rule_name,
            result=result,
            overall_score=round(overall_score, 2),
            customer_criteria_results=customer_results,
            financial_criteria_results=financial_results,
            geographic_criteria_results=geographic_results,
            total_criteria_count=total_count,
            passed_criteria_count=passed_count,
            failed_criteria_count=failed_count,
            warning_criteria_count=warning_count,
            recommendations=recommendations,
            required_documents=required_documents,
            can_override=rule.allow_manual_override,
            override_approval_required=rule.override_approval_required,
            checked_at=datetime.utcnow(),
            checked_by=user_id
        )
    
    def _check_customer_eligibility(
        self,
        criteria: Any,
        customer_data: CustomerData
    ) -> List[EligibilityCriteriaResult]:
        """Check customer eligibility criteria"""
        results = []
        
        # Age check
        age = self._calculate_age(customer_data.date_of_birth)
        age_check = EligibilityCriteriaResult(
            criteria_name="Age Requirement",
            passed=(criteria.age_criteria.min_age <= age <= criteria.age_criteria.max_age),
            actual_value=age,
            required_value=f"{criteria.age_criteria.min_age}-{criteria.age_criteria.max_age} years",
            message=f"Customer age is {age} years",
            severity="ERROR"
        )
        results.append(age_check)
        
        # Income check
        if criteria.income_criteria.min_monthly_income:
            income_check = EligibilityCriteriaResult(
                criteria_name="Minimum Income",
                passed=(customer_data.monthly_income or 0) >= criteria.income_criteria.min_monthly_income,
                actual_value=customer_data.monthly_income,
                required_value=criteria.income_criteria.min_monthly_income,
                message=f"Monthly income: ₹{customer_data.monthly_income or 0:,.2f}",
                severity="ERROR"
            )
            results.append(income_check)
        
        # Employment type check
        if criteria.employment_types:
            emp_check = EligibilityCriteriaResult(
                criteria_name="Employment Type",
                passed=customer_data.employment_type in criteria.employment_types,
                actual_value=customer_data.employment_type.value,
                required_value=[e.value for e in criteria.employment_types],
                message=f"Employment type: {customer_data.employment_type.value}",
                severity="ERROR"
            )
            results.append(emp_check)
        
        # Credit score check
        if criteria.credit_score_criteria and criteria.credit_score_criteria.mandatory:
            if customer_data.credit_score:
                score_check = EligibilityCriteriaResult(
                    criteria_name="Credit Score",
                    passed=customer_data.credit_score >= (criteria.credit_score_criteria.min_credit_score or 0),
                    actual_value=customer_data.credit_score,
                    required_value=criteria.credit_score_criteria.min_credit_score,
                    message=f"Credit score: {customer_data.credit_score}",
                    severity="ERROR"
                )
            else:
                score_check = EligibilityCriteriaResult(
                    criteria_name="Credit Score",
                    passed=criteria.credit_score_criteria.allow_no_history,
                    actual_value=None,
                    required_value=criteria.credit_score_criteria.min_credit_score,
                    message="No credit history available",
                    severity="WARNING" if criteria.credit_score_criteria.allow_no_history else "ERROR"
                )
            results.append(score_check)
        
        # Existing customer check
        if criteria.existing_customer_required:
            existing_check = EligibilityCriteriaResult(
                criteria_name="Existing Customer",
                passed=customer_data.is_existing_customer,
                actual_value=customer_data.is_existing_customer,
                required_value=True,
                message="Existing customer status",
                severity="ERROR"
            )
            results.append(existing_check)
        
        # Nationality check
        if criteria.allowed_nationalities:
            nationality_check = EligibilityCriteriaResult(
                criteria_name="Nationality",
                passed=customer_data.nationality in criteria.allowed_nationalities,
                actual_value=customer_data.nationality,
                required_value=criteria.allowed_nationalities,
                message=f"Nationality: {customer_data.nationality}",
                severity="ERROR"
            )
            results.append(nationality_check)
        
        # Residency status check
        if criteria.allowed_residency_status:
            residency_check = EligibilityCriteriaResult(
                criteria_name="Residency Status",
                passed=customer_data.residency_status in criteria.allowed_residency_status,
                actual_value=customer_data.residency_status.value,
                required_value=[r.value for r in criteria.allowed_residency_status],
                message=f"Residency: {customer_data.residency_status.value}",
                severity="ERROR"
            )
            results.append(residency_check)
        
        # Blacklist check
        if criteria.blacklist_check:
            blacklist_check = EligibilityCriteriaResult(
                criteria_name="Blacklist Check",
                passed=not customer_data.is_blacklisted,
                actual_value=customer_data.is_blacklisted,
                required_value=False,
                message="Blacklist status",
                severity="ERROR"
            )
            results.append(blacklist_check)
        
        # PEP check
        if criteria.politically_exposed_person_check:
            pep_check = EligibilityCriteriaResult(
                criteria_name="PEP Check",
                passed=not customer_data.is_pep,
                actual_value=customer_data.is_pep,
                required_value=False,
                message="PEP status requires additional verification",
                severity="WARNING"
            )
            results.append(pep_check)
        
        # Co-applicant check
        if criteria.co_applicant_rules and criteria.co_applicant_rules.required:
            co_app_check = EligibilityCriteriaResult(
                criteria_name="Co-applicant Required",
                passed=customer_data.has_co_applicant and 
                       customer_data.co_applicant_count >= criteria.co_applicant_rules.min_count,
                actual_value=customer_data.co_applicant_count,
                required_value=criteria.co_applicant_rules.min_count,
                message=f"Co-applicants: {customer_data.co_applicant_count}",
                severity="ERROR"
            )
            results.append(co_app_check)
        
        # Guarantor check
        if criteria.guarantor_rules and criteria.guarantor_rules.required:
            guarantor_check = EligibilityCriteriaResult(
                criteria_name="Guarantor Required",
                passed=customer_data.has_guarantor and 
                       customer_data.guarantor_count >= criteria.guarantor_rules.min_count,
                actual_value=customer_data.guarantor_count,
                required_value=criteria.guarantor_rules.min_count,
                message=f"Guarantors: {customer_data.guarantor_count}",
                severity="ERROR"
            )
            results.append(guarantor_check)
        
        return results
    
    def _check_financial_eligibility(
        self,
        criteria: Any,
        customer_data: CustomerData,
        loan_amount: Optional[float],
        proposed_emi: Optional[float]
    ) -> List[EligibilityCriteriaResult]:
        """Check financial eligibility criteria"""
        results = []
        
        # FOIR check
        if criteria.foir_criteria:
            monthly_income = customer_data.monthly_income or 0
            existing_obligations = customer_data.monthly_obligations or 0
            
            if criteria.foir_criteria.include_proposed_emi and proposed_emi:
                total_obligations = existing_obligations + proposed_emi
            else:
                total_obligations = existing_obligations
            
            foir = (total_obligations / monthly_income * 100) if monthly_income > 0 else 999
            
            foir_check = EligibilityCriteriaResult(
                criteria_name="FOIR (Fixed Obligation to Income Ratio)",
                passed=foir <= criteria.foir_criteria.max_foir_percentage,
                actual_value=round(foir, 2),
                required_value=f"<= {criteria.foir_criteria.max_foir_percentage}%",
                message=f"FOIR: {foir:.2f}%",
                severity="ERROR"
            )
            results.append(foir_check)
        
        # DTI check
        if criteria.dti_criteria:
            annual_income = customer_data.annual_income or (customer_data.monthly_income or 0) * 12
            annual_obligations = (customer_data.monthly_obligations or 0) * 12
            
            if loan_amount:
                annual_obligations += loan_amount  # Simplified - should include interest
            
            dti = (annual_obligations / annual_income * 100) if annual_income > 0 else 999
            
            dti_check = EligibilityCriteriaResult(
                criteria_name="DTI (Debt-to-Income Ratio)",
                passed=dti <= criteria.dti_criteria.max_dti_percentage,
                actual_value=round(dti, 2),
                required_value=f"<= {criteria.dti_criteria.max_dti_percentage}%",
                message=f"DTI: {dti:.2f}%",
                severity="ERROR"
            )
            results.append(dti_check)
        
        # Existing obligations check
        if criteria.existing_obligations:
            if criteria.existing_obligations.max_existing_loans is not None:
                loans_check = EligibilityCriteriaResult(
                    criteria_name="Existing Loans",
                    passed=(customer_data.existing_loan_count or 0) <= criteria.existing_obligations.max_existing_loans,
                    actual_value=customer_data.existing_loan_count,
                    required_value=f"<= {criteria.existing_obligations.max_existing_loans}",
                    message=f"Existing loans: {customer_data.existing_loan_count or 0}",
                    severity="ERROR"
                )
                results.append(loans_check)
            
            if criteria.existing_obligations.max_existing_emi is not None:
                emi_check = EligibilityCriteriaResult(
                    criteria_name="Existing EMI",
                    passed=(customer_data.existing_emi or 0) <= criteria.existing_obligations.max_existing_emi,
                    actual_value=customer_data.existing_emi,
                    required_value=f"<= ₹{criteria.existing_obligations.max_existing_emi:,.2f}",
                    message=f"Existing EMI: ₹{customer_data.existing_emi or 0:,.2f}",
                    severity="ERROR"
                )
                results.append(emi_check)
        
        # Banking turnover check
        if criteria.banking_turnover and criteria.banking_turnover.required:
            if criteria.banking_turnover.min_monthly_turnover:
                turnover_check = EligibilityCriteriaResult(
                    criteria_name="Banking Turnover",
                    passed=(customer_data.average_banking_turnover or 0) >= criteria.banking_turnover.min_monthly_turnover,
                    actual_value=customer_data.average_banking_turnover,
                    required_value=criteria.banking_turnover.min_monthly_turnover,
                    message=f"Avg turnover: ₹{customer_data.average_banking_turnover or 0:,.2f}",
                    severity="ERROR"
                )
                results.append(turnover_check)
            
            if criteria.banking_turnover.min_average_balance:
                balance_check = EligibilityCriteriaResult(
                    criteria_name="Average Bank Balance",
                    passed=(customer_data.average_bank_balance or 0) >= criteria.banking_turnover.min_average_balance,
                    actual_value=customer_data.average_bank_balance,
                    required_value=criteria.banking_turnover.min_average_balance,
                    message=f"Avg balance: ₹{customer_data.average_bank_balance or 0:,.2f}",
                    severity="ERROR"
                )
                results.append(balance_check)
        
        # ITR check
        if criteria.itr_criteria and criteria.itr_criteria.required:
            itr_years_check = EligibilityCriteriaResult(
                criteria_name="ITR Filing Years",
                passed=(customer_data.itr_filed_years or 0) >= criteria.itr_criteria.min_years,
                actual_value=customer_data.itr_filed_years,
                required_value=criteria.itr_criteria.min_years,
                message=f"ITR filed for {customer_data.itr_filed_years or 0} years",
                severity="ERROR"
            )
            results.append(itr_years_check)
            
            if criteria.itr_criteria.min_annual_income and customer_data.itr_annual_income:
                itr_income_check = EligibilityCriteriaResult(
                    criteria_name="ITR Income",
                    passed=customer_data.itr_annual_income >= criteria.itr_criteria.min_annual_income,
                    actual_value=customer_data.itr_annual_income,
                    required_value=criteria.itr_criteria.min_annual_income,
                    message=f"ITR income: ₹{customer_data.itr_annual_income:,.2f}",
                    severity="ERROR"
                )
                results.append(itr_income_check)
        
        # Net worth check
        if criteria.min_net_worth:
            net_worth_check = EligibilityCriteriaResult(
                criteria_name="Net Worth",
                passed=(customer_data.net_worth or 0) >= criteria.min_net_worth,
                actual_value=customer_data.net_worth,
                required_value=criteria.min_net_worth,
                message=f"Net worth: ₹{customer_data.net_worth or 0:,.2f}",
                severity="ERROR"
            )
            results.append(net_worth_check)
        
        # Liquid assets check
        if criteria.min_liquid_assets:
            liquid_check = EligibilityCriteriaResult(
                criteria_name="Liquid Assets",
                passed=(customer_data.liquid_assets or 0) >= criteria.min_liquid_assets,
                actual_value=customer_data.liquid_assets,
                required_value=criteria.min_liquid_assets,
                message=f"Liquid assets: ₹{customer_data.liquid_assets or 0:,.2f}",
                severity="ERROR"
            )
            results.append(liquid_check)
        
        return results
    
    def _check_geographic_eligibility(
        self,
        criteria: Any,
        customer_data: CustomerData
    ) -> List[EligibilityCriteriaResult]:
        """Check geographic eligibility criteria"""
        results = []
        
        # PIN code check
        if criteria.pin_code_restriction:
            pin_code = customer_data.pin_code
            restriction = criteria.pin_code_restriction
            
            if restriction.type == "INCLUDE":
                passed = pin_code in restriction.pin_codes if pin_code else False
                message = f"PIN {pin_code} must be in serviceable list"
            else:  # EXCLUDE
                passed = pin_code not in restriction.pin_codes if pin_code else True
                message = f"PIN {pin_code} must not be in excluded list"
            
            pin_check = EligibilityCriteriaResult(
                criteria_name="PIN Code Serviceability",
                passed=passed,
                actual_value=pin_code,
                required_value=f"{restriction.type}: {len(restriction.pin_codes)} PINs",
                message=message,
                severity="ERROR"
            )
            results.append(pin_check)
        
        # State check
        if criteria.state_restriction:
            state = customer_data.state
            restriction = criteria.state_restriction
            
            if restriction.type == "INCLUDE":
                passed = state in restriction.states if state else False
                message = f"State {state} must be in serviceable list"
            else:  # EXCLUDE
                passed = state not in restriction.states if state else True
                message = f"State {state} must not be in excluded list"
            
            state_check = EligibilityCriteriaResult(
                criteria_name="State Serviceability",
                passed=passed,
                actual_value=state,
                required_value=f"{restriction.type}: {len(restriction.states)} states",
                message=message,
                severity="ERROR"
            )
            results.append(state_check)
        
        # City check
        if criteria.city_restriction:
            city = customer_data.city
            restriction = criteria.city_restriction
            
            if restriction.type == "INCLUDE":
                passed = city in restriction.cities if city else False
                message = f"City {city} must be in serviceable list"
            else:  # EXCLUDE
                passed = city not in restriction.cities if city else True
                message = f"City {city} must not be in excluded list"
            
            city_check = EligibilityCriteriaResult(
                criteria_name="City Serviceability",
                passed=passed,
                actual_value=city,
                required_value=f"{restriction.type}: {len(restriction.cities)} cities",
                message=message,
                severity="ERROR"
            )
            results.append(city_check)
        
        # Branch availability check
        if criteria.branch_availability and criteria.branch_availability.enabled:
            branch_code = customer_data.branch_code
            branch_list = criteria.branch_availability.branch_codes
            
            branch_check = EligibilityCriteriaResult(
                criteria_name="Branch Availability",
                passed=branch_code in branch_list if branch_code else False,
                actual_value=branch_code,
                required_value=f"Must be in {len(branch_list)} available branches",
                message=f"Branch: {branch_code or 'Not specified'}",
                severity="ERROR"
            )
            results.append(branch_check)
        
        return results
    
    def _calculate_age(self, date_of_birth: date) -> int:
        """Calculate age from date of birth"""
        today = date.today()
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    def _find_rule_by_product(self, product_id: str, tenant_id: str) -> EligibilityRule:
        """Find active rule by product ID"""
        for rule in self.rules_storage.values():
            if (rule.tenant_id == tenant_id and 
                rule.status == RuleStatus.ACTIVE and
                (rule.product_id == product_id or rule.apply_to_all_products)):
                return rule
        raise ValueError(f"No active eligibility rule found for product {product_id}")
    
    def _generate_recommendations(
        self,
        results: List[EligibilityCriteriaResult],
        customer_data: CustomerData
    ) -> List[str]:
        """Generate recommendations based on check results"""
        recommendations = []
        
        for result in results:
            if not result.passed:
                if "Age" in result.criteria_name:
                    recommendations.append("Customer does not meet age requirements")
                elif "Income" in result.criteria_name:
                    recommendations.append("Consider requesting co-applicant to meet income requirement")
                elif "Credit Score" in result.criteria_name:
                    recommendations.append("Improve credit score or provide additional collateral")
                elif "FOIR" in result.criteria_name or "DTI" in result.criteria_name:
                    recommendations.append("Reduce existing obligations or increase income proof")
                elif "ITR" in result.criteria_name:
                    recommendations.append("Submit required ITR documents")
                elif "serviceability" in result.criteria_name.lower():
                    recommendations.append("Location not serviceable - consider different address")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_required_documents(
        self,
        rule: EligibilityRule,
        customer_data: CustomerData
    ) -> List[str]:
        """Generate list of required documents"""
        documents = []
        
        # Identity documents
        documents.extend(["PAN Card", "Aadhaar Card", "Address Proof"])
        
        # Income documents
        if customer_data.employment_type == EmploymentType.SALARIED:
            documents.extend(["Salary Slips (3 months)", "Bank Statement (6 months)", "Form 16"])
        elif customer_data.employment_type == EmploymentType.SELF_EMPLOYED:
            documents.extend(["ITR (2 years)", "Bank Statement (12 months)", "Business Proof"])
        elif customer_data.employment_type == EmploymentType.BUSINESS:
            documents.extend(["ITR (3 years)", "Financial Statements", "GST Returns", "Bank Statement (12 months)"])
        
        # Credit documents
        if rule.customer_eligibility.credit_score_criteria:
            documents.append("Credit Report")
        
        # Property documents (if applicable)
        if customer_data.pin_code:
            documents.extend(["Property Documents", "Valuation Report"])
        
        return list(set(documents))  # Remove duplicates
    
    # ========================================================================
    # BULK OPERATIONS
    # ========================================================================
    
    def bulk_check_eligibility(
        self,
        request: BulkEligibilityCheckRequest,
        tenant_id: str,
        user_id: Optional[str] = None
    ) -> BulkEligibilityCheckResponse:
        """Check eligibility for multiple customers"""
        results = []
        
        for customer_data in request.customer_data_list:
            check_request = EligibilityCheckRequest(
                rule_id=request.rule_id,
                customer_data=customer_data,
                loan_amount=request.loan_amount,
                loan_tenure=request.loan_tenure
            )
            
            try:
                result = self.check_eligibility(check_request, tenant_id, user_id)
                results.append(result)
            except Exception as e:
                # Log error and continue
                print(f"Error checking eligibility: {e}")
        
        # Calculate summary
        eligible_count = sum(1 for r in results if r.result == EligibilityResult.ELIGIBLE)
        not_eligible_count = sum(1 for r in results if r.result == EligibilityResult.NOT_ELIGIBLE)
        conditional_count = sum(1 for r in results if r.result == EligibilityResult.CONDITIONAL)
        manual_review_count = sum(1 for r in results if r.result == EligibilityResult.MANUAL_REVIEW)
        
        avg_score = sum(r.overall_score for r in results) / len(results) if results else 0
        
        summary = {
            "average_score": round(avg_score, 2),
            "pass_rate": round(eligible_count / len(results) * 100, 2) if results else 0,
            "common_failures": self._get_common_failures(results)
        }
        
        return BulkEligibilityCheckResponse(
            total_customers=len(request.customer_data_list),
            eligible_count=eligible_count,
            not_eligible_count=not_eligible_count,
            conditional_count=conditional_count,
            manual_review_count=manual_review_count,
            results=results,
            summary=summary
        )
    
    def _get_common_failures(self, results: List[EligibilityCheckResponse]) -> Dict[str, int]:
        """Get most common failure criteria"""
        failures = {}
        
        for result in results:
            all_criteria = (result.customer_criteria_results + 
                          result.financial_criteria_results + 
                          result.geographic_criteria_results)
            
            for criteria in all_criteria:
                if not criteria.passed:
                    failures[criteria.criteria_name] = failures.get(criteria.criteria_name, 0) + 1
        
        # Sort by frequency and return top 5
        sorted_failures = sorted(failures.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_failures[:5])
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_stats(self, tenant_id: str) -> EligibilityStats:
        """Get eligibility rules statistics"""
        rules = [r for r in self.rules_storage.values() if r.tenant_id == tenant_id]
        
        active_rules = sum(1 for r in rules if r.status == RuleStatus.ACTIVE)
        draft_rules = sum(1 for r in rules if r.status == RuleStatus.DRAFT)
        inactive_rules = sum(1 for r in rules if r.status == RuleStatus.INACTIVE)
        archived_rules = sum(1 for r in rules if r.status == RuleStatus.ARCHIVED)
        
        # Rules by product
        rules_by_product = {}
        for rule in rules:
            if rule.product_code:
                rules_by_product[rule.product_code] = rules_by_product.get(rule.product_code, 0) + 1
        
        return EligibilityStats(
            total_rules=len(rules),
            active_rules=active_rules,
            draft_rules=draft_rules,
            inactive_rules=inactive_rules,
            archived_rules=archived_rules,
            rules_by_product=rules_by_product,
            total_checks_performed=self.checks_performed,
            eligible_count=0,  # Would come from check history
            not_eligible_count=0,
            conditional_count=0
        )
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def validate_rule_data(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate eligibility rule data"""
        errors = []
        warnings = []
        
        # Basic validation
        if not rule_data.get('rule_code'):
            errors.append("Rule code is required")
        if not rule_data.get('rule_name'):
            errors.append("Rule name is required")
        
        # Date validation
        effective_date = rule_data.get('effective_date')
        expiry_date = rule_data.get('expiry_date')
        
        if effective_date and expiry_date:
            if expiry_date <= effective_date:
                errors.append("Expiry date must be after effective date")
        
        # Customer eligibility validation
        customer_elig = rule_data.get('customer_eligibility')
        if customer_elig:
            age_criteria = customer_elig.get('age_criteria')
            if age_criteria:
                if age_criteria.get('min_age', 0) < 18:
                    errors.append("Minimum age cannot be less than 18")
                if age_criteria.get('max_age', 0) > 100:
                    warnings.append("Maximum age is unusually high")
        
        # Financial eligibility validation
        financial_elig = rule_data.get('financial_eligibility')
        if financial_elig:
            foir = financial_elig.get('foir_criteria')
            if foir and foir.get('max_foir_percentage', 0) > 80:
                warnings.append("FOIR percentage above 80% is very high")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


# Create service instance
eligibility_service = EligibilityService()
