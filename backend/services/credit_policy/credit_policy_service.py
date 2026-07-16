"""
Credit Policy Integration Service
Risk-based pricing and credit decisioning service
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from .credit_policy_models import (
    CreditPolicy, RiskBasedPricing, ScoreBasedRate, LTVRatio,
    ExposureLimit, ConcentrationLimit, SectoralCap,
    AutoApprovalCriteria, ManualReviewTrigger, DecisionMatrix,
    CounterOfferRule,
    PolicyStatus, DecisionOutcome, PricingTier, DeclineReason,
    CreditPolicyCreate, CreditPolicyUpdate,
    PricingCalculationRequest, PricingCalculationResponse,
    CreditDecisionRequest, CreditDecisionResponse,
    ExposureCheckRequest, ExposureCheckResponse
)


class CreditPolicyService:
    """Service for credit policy management"""
    
    def __init__(self, db: Session, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
    
    # =====================================================================
    # CREDIT POLICY CRUD
    # =====================================================================
    
    def create_policy(
        self,
        policy_data: CreditPolicyCreate,
        user_id: UUID
    ) -> CreditPolicy:
        """Create new credit policy"""
        policy = CreditPolicy(
            tenant_id=self.tenant_id,
            **policy_data.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def get_policy(self, policy_id: UUID) -> Optional[CreditPolicy]:
        """Get credit policy by ID"""
        return self.db.query(CreditPolicy).filter(
            and_(
                CreditPolicy.id == policy_id,
                CreditPolicy.tenant_id == self.tenant_id
            )
        ).first()

    
    def list_policies(
        self,
        product_id: Optional[UUID] = None,
        status: Optional[PolicyStatus] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CreditPolicy]:
        """List credit policies with filters"""
        query = self.db.query(CreditPolicy).filter(
            CreditPolicy.tenant_id == self.tenant_id
        )
        
        if product_id:
            query = query.filter(CreditPolicy.product_id == product_id)
        if status:
            query = query.filter(CreditPolicy.status == status)
        if is_active is not None:
            query = query.filter(CreditPolicy.is_active == is_active)
        
        return query.order_by(CreditPolicy.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_policy(
        self,
        policy_id: UUID,
        policy_data: CreditPolicyUpdate,
        user_id: UUID
    ) -> Optional[CreditPolicy]:
        """Update credit policy"""
        policy = self.get_policy(policy_id)
        if not policy:
            return None
        
        update_data = policy_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(policy, field, value)
        
        policy.updated_by = user_id
        policy.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def activate_policy(self, policy_id: UUID, user_id: UUID) -> Optional[CreditPolicy]:
        """Activate credit policy"""
        policy = self.get_policy(policy_id)
        if not policy:
            return None
        
        policy.is_active = True
        policy.status = PolicyStatus.ACTIVE
        policy.updated_by = user_id
        policy.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def deactivate_policy(self, policy_id: UUID, user_id: UUID) -> Optional[CreditPolicy]:
        """Deactivate credit policy"""
        policy = self.get_policy(policy_id)
        if not policy:
            return None
        
        policy.is_active = False
        policy.status = PolicyStatus.INACTIVE
        policy.updated_by = user_id
        policy.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(policy)
        return policy

    
    # =====================================================================
    # RISK-BASED PRICING CALCULATION
    # =====================================================================
    
    def calculate_pricing(
        self,
        request: PricingCalculationRequest
    ) -> PricingCalculationResponse:
        """Calculate risk-based pricing"""
        policy = self.get_policy(request.policy_id)
        if not policy or not policy.is_active:
            raise ValueError("Policy not found or inactive")
        
        # Get risk-based pricing configuration
        risk_pricing = policy.risk_pricing
        if not risk_pricing:
            raise ValueError("Risk pricing not configured for policy")
        
        # Calculate LTV ratio
        ltv_ratio = None
        if request.collateral_value and request.collateral_value > 0:
            ltv_ratio = (request.loan_amount / request.collateral_value) * 100
        
        # Calculate DTI ratio
        dti_ratio = (request.monthly_obligations / request.monthly_income) * 100
        
        # Find matching score-based rate
        score_rate = self._find_score_based_rate(policy, request.credit_score)
        if not score_rate:
            raise ValueError("No rate configuration found for credit score")
        
        # Start with base rate
        base_rate = score_rate.base_rate
        risk_adjusted_rate = base_rate
        rate_breakdown = {
            "base_rate": base_rate,
            "score_adjustment": score_rate.rate_adjustment
        }
        
        # Apply score adjustment
        risk_adjusted_rate += score_rate.rate_adjustment
        
        # Apply LTV adjustment
        ltv_adjustment = 0.0
        if ltv_ratio:
            ltv_adjustment = self._calculate_ltv_adjustment(policy, ltv_ratio)
            risk_adjusted_rate += ltv_adjustment
            rate_breakdown["ltv_adjustment"] = ltv_adjustment
        
        # Apply DTI adjustment
        dti_adjustment = self._calculate_dti_adjustment(dti_ratio)
        risk_adjusted_rate += dti_adjustment
        rate_breakdown["dti_adjustment"] = dti_adjustment
        
        # Apply other factors
        other_adjustment = 0.0
        if request.other_factors:
            other_adjustment = self._calculate_other_factors_adjustment(
                request.other_factors,
                request.employment_type
            )
            risk_adjusted_rate += other_adjustment
            rate_breakdown["other_factors_adjustment"] = other_adjustment

        
        # Ensure final rate is within bounds
        final_rate = max(
            risk_pricing.min_interest_rate,
            min(risk_adjusted_rate, risk_pricing.max_interest_rate)
        )
        
        # Calculate processing fee
        processing_fee = score_rate.processing_fee_percent or \
            risk_pricing.processing_fee_range.get("min", 1.0)
        
        # Calculate risk premium
        risk_premium = score_rate.risk_premium_percent or \
            risk_pricing.risk_premium_range.get("min", 0.0)
        
        return PricingCalculationResponse(
            base_rate=base_rate,
            risk_adjusted_rate=risk_adjusted_rate,
            final_interest_rate=final_rate,
            processing_fee_percent=processing_fee,
            risk_premium_percent=risk_premium,
            pricing_tier=score_rate.pricing_tier,
            ltv_ratio=ltv_ratio,
            dti_ratio=dti_ratio,
            rate_breakdown=rate_breakdown,
            pricing_factors={
                "credit_score": request.credit_score,
                "loan_amount": request.loan_amount,
                "employment_type": request.employment_type
            }
        )
    
    def _find_score_based_rate(
        self,
        policy: CreditPolicy,
        credit_score: int
    ) -> Optional[ScoreBasedRate]:
        """Find matching score-based rate"""
        matching_rates = [
            rate for rate in policy.score_rates
            if rate.min_score <= credit_score <= rate.max_score
        ]
        
        if not matching_rates:
            return None
        
        # Return highest priority rate
        return max(matching_rates, key=lambda r: r.priority)
    
    def _calculate_ltv_adjustment(
        self,
        policy: CreditPolicy,
        ltv_ratio: float
    ) -> float:
        """Calculate LTV-based rate adjustment"""
        adjustment = 0.0
        
        for ltv_config in policy.ltv_ratios:
            if ltv_config.ltv_rate_adjustments:
                for range_key, rate_adj in ltv_config.ltv_rate_adjustments.items():
                    # Parse range like "60-80"
                    if "-" in range_key:
                        min_ltv, max_ltv = map(float, range_key.split("-"))
                        if min_ltv <= ltv_ratio <= max_ltv:
                            adjustment = max(adjustment, rate_adj)
        
        return adjustment

    
    def _calculate_dti_adjustment(self, dti_ratio: float) -> float:
        """Calculate DTI-based rate adjustment"""
        # Standard DTI adjustments
        if dti_ratio <= 30:
            return 0.0
        elif dti_ratio <= 40:
            return 0.25
        elif dti_ratio <= 50:
            return 0.5
        else:
            return 1.0
    
    def _calculate_other_factors_adjustment(
        self,
        other_factors: Dict[str, Any],
        employment_type: str
    ) -> float:
        """Calculate adjustment for other factors"""
        adjustment = 0.0
        
        # Employment type adjustment
        if employment_type == "SELF_EMPLOYED":
            adjustment += 0.5
        elif employment_type == "SELF_EMPLOYED_PROFESSIONAL":
            adjustment += 0.25
        
        # Additional factors from request
        if other_factors.get("has_existing_relationship"):
            adjustment -= 0.25
        
        if other_factors.get("high_value_customer"):
            adjustment -= 0.5
        
        return adjustment
    
    # =====================================================================
    # CREDIT DECISIONING
    # =====================================================================
    
    def evaluate_credit_decision(
        self,
        request: CreditDecisionRequest
    ) -> CreditDecisionResponse:
        """Evaluate credit decision based on policy"""
        policy = self.get_policy(request.policy_id)
        if not policy or not policy.is_active:
            raise ValueError("Policy not found or inactive")
        
        decision_reasons = []
        matched_rules = []
        risk_assessment = {}
        
        # Calculate DTI ratio
        dti_ratio = (request.monthly_obligations / request.monthly_income) * 100
        risk_assessment["dti_ratio"] = dti_ratio
        
        # Calculate LTV ratio
        ltv_ratio = None
        if request.collateral_value and request.collateral_value > 0:
            ltv_ratio = (request.loan_amount / request.collateral_value) * 100
            risk_assessment["ltv_ratio"] = ltv_ratio
        
        # Check auto-approval criteria first
        auto_approved, auto_reasons = self._check_auto_approval(
            policy, request, dti_ratio, ltv_ratio
        )
        
        if auto_approved:
            decision_reasons.extend(auto_reasons)
            matched_rules.append("auto_approval_criteria")
            
            # Calculate pricing for approved amount
            pricing = self.calculate_pricing(
                PricingCalculationRequest(
                    policy_id=request.policy_id,
                    credit_score=request.credit_score,
                    loan_amount=request.loan_amount,
                    collateral_value=request.collateral_value,
                    monthly_income=request.monthly_income,
                    monthly_obligations=request.monthly_obligations,
                    employment_type=request.employment_type
                )
            )
            
            return CreditDecisionResponse(
                decision_outcome=DecisionOutcome.AUTO_APPROVED,
                approved_amount=request.loan_amount,
                interest_rate=pricing.final_interest_rate,
                decision_reasons=decision_reasons,
                matched_rules=matched_rules,
                risk_assessment=risk_assessment
            )

        
        # Check manual review triggers
        triggered_review, review_reasons, review_level = self._check_manual_review_triggers(
            policy, request, dti_ratio, ltv_ratio
        )
        
        if triggered_review:
            decision_reasons.extend(review_reasons)
            matched_rules.append("manual_review_triggers")
            
            return CreditDecisionResponse(
                decision_outcome=DecisionOutcome.MANUAL_REVIEW,
                review_level=review_level,
                review_instructions="; ".join(review_reasons),
                decision_reasons=decision_reasons,
                matched_rules=matched_rules,
                risk_assessment=risk_assessment
            )
        
        # Check decision matrix
        matrix_decision = self._evaluate_decision_matrix(
            policy, request, dti_ratio, ltv_ratio
        )
        
        if matrix_decision:
            matched_rules.append(f"decision_matrix_{matrix_decision.get('rule_name')}")
            
            outcome = matrix_decision["outcome"]
            
            if outcome == DecisionOutcome.DECLINED:
                return CreditDecisionResponse(
                    decision_outcome=DecisionOutcome.DECLINED,
                    decline_reason=matrix_decision.get("decline_reason"),
                    decline_message=matrix_decision.get("decline_message"),
                    decision_reasons=matrix_decision.get("reasons", []),
                    matched_rules=matched_rules,
                    risk_assessment=risk_assessment
                )
            
            elif outcome == DecisionOutcome.COUNTER_OFFER:
                # Generate counter-offer
                counter_offer = self._generate_counter_offer(
                    policy, request, dti_ratio, ltv_ratio
                )
                
                return CreditDecisionResponse(
                    decision_outcome=DecisionOutcome.COUNTER_OFFER,
                    counter_offer=counter_offer,
                    decision_reasons=matrix_decision.get("reasons", []),
                    matched_rules=matched_rules,
                    risk_assessment=risk_assessment
                )
            
            elif outcome == DecisionOutcome.MANUAL_REVIEW:
                return CreditDecisionResponse(
                    decision_outcome=DecisionOutcome.MANUAL_REVIEW,
                    review_level=matrix_decision.get("review_level"),
                    review_instructions=matrix_decision.get("review_instructions"),
                    decision_reasons=matrix_decision.get("reasons", []),
                    matched_rules=matched_rules,
                    risk_assessment=risk_assessment
                )
        
        # Default to manual review if no clear decision
        return CreditDecisionResponse(
            decision_outcome=DecisionOutcome.MANUAL_REVIEW,
            review_level="L1",
            review_instructions="No matching decision rules found",
            decision_reasons=["Default escalation - requires manual review"],
            matched_rules=matched_rules,
            risk_assessment=risk_assessment
        )

    
    def _check_auto_approval(
        self,
        policy: CreditPolicy,
        request: CreditDecisionRequest,
        dti_ratio: float,
        ltv_ratio: Optional[float]
    ) -> tuple[bool, List[str]]:
        """Check if application meets auto-approval criteria"""
        criteria = policy.auto_approval_criteria
        if not criteria:
            return False, ["No auto-approval criteria configured"]
        
        reasons = []
        
        # Credit score check
        if criteria.min_credit_score and request.credit_score < criteria.min_credit_score:
            reasons.append(f"Credit score {request.credit_score} below minimum {criteria.min_credit_score}")
            return False, reasons
        
        # Income check
        if criteria.min_monthly_income and request.monthly_income < criteria.min_monthly_income:
            reasons.append(f"Monthly income below minimum")
            return False, reasons
        
        # DTI check
        if criteria.max_dti_ratio and dti_ratio > criteria.max_dti_ratio:
            reasons.append(f"DTI ratio {dti_ratio:.2f}% exceeds maximum {criteria.max_dti_ratio}%")
            return False, reasons
        
        # Employment type check
        if criteria.allowed_employment_types and \
           request.employment_type not in criteria.allowed_employment_types:
            reasons.append(f"Employment type {request.employment_type} not allowed")
            return False, reasons
        
        # Employment duration check
        if criteria.min_employment_months and \
           request.employment_months < criteria.min_employment_months:
            reasons.append(f"Employment duration below minimum")
            return False, reasons
        
        # Loan amount check
        if criteria.max_loan_amount and request.loan_amount > criteria.max_loan_amount:
            reasons.append(f"Loan amount exceeds auto-approval limit")
            return False, reasons
        
        # LTV check
        if criteria.max_ltv_ratio and ltv_ratio and ltv_ratio > criteria.max_ltv_ratio:
            reasons.append(f"LTV ratio {ltv_ratio:.2f}% exceeds maximum {criteria.max_ltv_ratio}%")
            return False, reasons
        
        # Residence duration check
        if criteria.min_residence_months and \
           request.residence_months < criteria.min_residence_months:
            reasons.append(f"Residence duration below minimum")
            return False, reasons
        
        # Geography check
        if criteria.allowed_geographies and \
           request.geography not in criteria.allowed_geographies:
            reasons.append(f"Geography {request.geography} not in allowed list")
            return False, reasons
        
        # Bureau checks
        bureau_data = request.bureau_data or {}
        
        if criteria.max_active_loans:
            active_loans = bureau_data.get("active_loans", 0)
            if active_loans > criteria.max_active_loans:
                reasons.append(f"Active loans {active_loans} exceeds maximum {criteria.max_active_loans}")
                return False, reasons
        
        if criteria.max_dpd_days:
            max_dpd = bureau_data.get("max_dpd_last_12_months", 0)
            if max_dpd > criteria.max_dpd_days:
                reasons.append(f"DPD history exceeds threshold")
                return False, reasons
        
        if not criteria.allow_restructured_accounts:
            has_restructured = bureau_data.get("has_restructured_accounts", False)
            if has_restructured:
                reasons.append("Restructured accounts not allowed")
                return False, reasons
        
        # All checks passed
        reasons.append("Meets all auto-approval criteria")
        return True, reasons

    
    def _check_manual_review_triggers(
        self,
        policy: CreditPolicy,
        request: CreditDecisionRequest,
        dti_ratio: float,
        ltv_ratio: Optional[float]
    ) -> tuple[bool, List[str], Optional[str]]:
        """Check if any manual review triggers are activated"""
        if not policy.manual_review_triggers:
            return False, [], None
        
        triggered_reasons = []
        highest_review_level = None
        priority_order = {"LOW": 0, "NORMAL": 1, "HIGH": 2, "URGENT": 3}
        highest_priority = -1
        
        for trigger in policy.manual_review_triggers:
            if not trigger.is_active:
                continue
            
            # Get field value
            field_value = self._get_field_value(request, trigger.condition_field, dti_ratio, ltv_ratio)
            
            # Evaluate condition
            if self._evaluate_condition(
                field_value,
                trigger.condition_operator,
                trigger.condition_value
            ):
                triggered_reasons.append(trigger.trigger_name)
                
                # Track highest priority review level
                trigger_priority = priority_order.get(trigger.priority, 1)
                if trigger_priority > highest_priority:
                    highest_priority = trigger_priority
                    highest_review_level = trigger.review_level or "L1"
        
        return len(triggered_reasons) > 0, triggered_reasons, highest_review_level
    
    def _evaluate_decision_matrix(
        self,
        policy: CreditPolicy,
        request: CreditDecisionRequest,
        dti_ratio: float,
        ltv_ratio: Optional[float]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate decision matrix rules"""
        if not policy.decision_matrix:
            return None
        
        # Sort by priority (highest first)
        sorted_rules = sorted(
            [rule for rule in policy.decision_matrix if rule.is_active],
            key=lambda r: r.rule_priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            if self._matches_decision_rule(rule, request, dti_ratio, ltv_ratio):
                return {
                    "rule_name": rule.rule_name,
                    "outcome": rule.decision_outcome,
                    "decline_reason": rule.decline_reason,
                    "decline_message": rule.decline_message,
                    "review_level": rule.review_level,
                    "review_instructions": rule.review_instructions,
                    "reasons": [f"Matched rule: {rule.rule_name}"]
                }
        
        return None

    
    def _matches_decision_rule(
        self,
        rule: DecisionMatrix,
        request: CreditDecisionRequest,
        dti_ratio: float,
        ltv_ratio: Optional[float]
    ) -> bool:
        """Check if request matches decision rule conditions"""
        # Credit score range
        if rule.credit_score_range:
            min_score = rule.credit_score_range.get("min", 0)
            max_score = rule.credit_score_range.get("max", 999)
            if not (min_score <= request.credit_score <= max_score):
                return False
        
        # Loan amount range
        if rule.loan_amount_range:
            min_amount = rule.loan_amount_range.get("min", 0)
            max_amount = rule.loan_amount_range.get("max", float('inf'))
            if not (min_amount <= request.loan_amount <= max_amount):
                return False
        
        # LTV range
        if rule.ltv_range and ltv_ratio:
            min_ltv = rule.ltv_range.get("min", 0)
            max_ltv = rule.ltv_range.get("max", 100)
            if not (min_ltv <= ltv_ratio <= max_ltv):
                return False
        
        # DTI range
        if rule.dti_range:
            min_dti = rule.dti_range.get("min", 0)
            max_dti = rule.dti_range.get("max", 100)
            if not (min_dti <= dti_ratio <= max_dti):
                return False
        
        # Employment types
        if rule.employment_types and request.employment_type not in rule.employment_types:
            return False
        
        # Income range
        if rule.income_range:
            min_income = rule.income_range.get("min", 0)
            max_income = rule.income_range.get("max", float('inf'))
            if not (min_income <= request.monthly_income <= max_income):
                return False
        
        # Bureau conditions
        if rule.bureau_conditions:
            bureau_data = request.bureau_data or {}
            
            max_dpd = rule.bureau_conditions.get("max_dpd")
            if max_dpd is not None:
                actual_dpd = bureau_data.get("max_dpd_last_12_months", 0)
                if actual_dpd > max_dpd:
                    return False
            
            max_enquiries = rule.bureau_conditions.get("max_enquiries")
            if max_enquiries is not None:
                actual_enquiries = bureau_data.get("enquiries_last_6_months", 0)
                if actual_enquiries > max_enquiries:
                    return False
        
        # All conditions matched
        return True
    
    def _generate_counter_offer(
        self,
        policy: CreditPolicy,
        request: CreditDecisionRequest,
        dti_ratio: float,
        ltv_ratio: Optional[float]
    ) -> Dict[str, Any]:
        """Generate counter-offer based on rules"""
        if not policy.counter_offer_rules:
            return {}
        
        # Find matching counter-offer rule (highest priority)
        sorted_rules = sorted(
            [rule for rule in policy.counter_offer_rules if rule.is_active],
            key=lambda r: r.rule_priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            # Check if trigger conditions match
            if self._matches_counter_offer_trigger(rule, request, dti_ratio, ltv_ratio):
                offer = {
                    "rule_name": rule.rule_name,
                    "original_request": {
                        "loan_amount": request.loan_amount,
                        "requested_tenure": request.additional_data.get("tenure") if request.additional_data else None
                    }
                }
                
                # Apply loan amount adjustment
                if rule.loan_amount_adjustment:
                    adj = rule.loan_amount_adjustment
                    if adj.get("type") == "PERCENTAGE":
                        offer["offered_loan_amount"] = request.loan_amount * (adj.get("value", 100) / 100)
                    elif adj.get("type") == "FIXED":
                        offer["offered_loan_amount"] = adj.get("value")
                
                # Apply interest rate adjustment
                if rule.interest_rate_adjustment:
                    # Calculate original pricing first
                    pricing = self.calculate_pricing(
                        PricingCalculationRequest(
                            policy_id=request.policy_id,
                            credit_score=request.credit_score,
                            loan_amount=request.loan_amount,
                            collateral_value=request.collateral_value,
                            monthly_income=request.monthly_income,
                            monthly_obligations=request.monthly_obligations,
                            employment_type=request.employment_type
                        )
                    )
                    
                    adj = rule.interest_rate_adjustment
                    if adj.get("type") == "ADD":
                        offer["offered_interest_rate"] = pricing.final_interest_rate + adj.get("value", 0)
                    elif adj.get("type") == "FIXED":
                        offer["offered_interest_rate"] = adj.get("value")
                
                # Additional requirements
                offer["require_guarantor"] = rule.require_guarantor
                offer["require_collateral"] = rule.require_collateral
                offer["additional_documents"] = rule.additional_documents or []
                offer["message"] = rule.counter_offer_message
                offer["terms_and_conditions"] = rule.terms_and_conditions
                offer["valid_until"] = (datetime.utcnow() + timedelta(days=rule.offer_validity_days)).isoformat()
                
                return offer
        
        return {}

    
    def _matches_counter_offer_trigger(
        self,
        rule: CounterOfferRule,
        request: CreditDecisionRequest,
        dti_ratio: float,
        ltv_ratio: Optional[float]
    ) -> bool:
        """Check if counter-offer trigger conditions match"""
        conditions = rule.trigger_conditions or {}
        
        # Check each condition
        for field, condition_spec in conditions.items():
            field_value = self._get_field_value(request, field, dti_ratio, ltv_ratio)
            
            if isinstance(condition_spec, dict):
                operator = condition_spec.get("operator", "=")
                value = condition_spec.get("value")
                
                if not self._evaluate_condition(field_value, operator, value):
                    return False
            else:
                # Simple equality check
                if field_value != condition_spec:
                    return False
        
        return True
    
    def _get_field_value(
        self,
        request: CreditDecisionRequest,
        field: str,
        dti_ratio: float,
        ltv_ratio: Optional[float]
    ) -> Any:
        """Get field value from request"""
        # Direct fields
        if field == "credit_score":
            return request.credit_score
        elif field == "loan_amount":
            return request.loan_amount
        elif field == "monthly_income":
            return request.monthly_income
        elif field == "employment_type":
            return request.employment_type
        elif field == "employment_months":
            return request.employment_months
        elif field == "dti_ratio":
            return dti_ratio
        elif field == "ltv_ratio":
            return ltv_ratio
        elif field == "residence_type":
            return request.residence_type
        elif field == "geography":
            return request.geography
        
        # Bureau data fields
        if field.startswith("bureau."):
            bureau_field = field.replace("bureau.", "")
            return request.bureau_data.get(bureau_field) if request.bureau_data else None
        
        # Additional data fields
        if field.startswith("additional."):
            additional_field = field.replace("additional.", "")
            return request.additional_data.get(additional_field) if request.additional_data else None
        
        return None
    
    def _evaluate_condition(
        self,
        field_value: Any,
        operator: str,
        condition_value: Any
    ) -> bool:
        """Evaluate a condition"""
        if field_value is None:
            return False
        
        if operator == "=" or operator == "==":
            return field_value == condition_value
        elif operator == "!=":
            return field_value != condition_value
        elif operator == "<":
            return field_value < condition_value
        elif operator == "<=":
            return field_value <= condition_value
        elif operator == ">":
            return field_value > condition_value
        elif operator == ">=":
            return field_value >= condition_value
        elif operator == "IN":
            return field_value in condition_value
        elif operator == "NOT IN":
            return field_value not in condition_value
        
        return False

    
    # =====================================================================
    # EXPOSURE CHECKING
    # =====================================================================
    
    def check_exposure_limits(
        self,
        request: ExposureCheckRequest
    ) -> ExposureCheckResponse:
        """Check exposure limits"""
        policy = self.get_policy(request.policy_id)
        if not policy or not policy.is_active:
            raise ValueError("Policy not found or inactive")
        
        exceeded_limits = []
        current_exposure = {}
        available_limit = {}
        warnings = []
        
        # Check each relevant exposure limit
        for limit in policy.exposure_limits:
            # Determine if this limit applies
            applies = False
            
            if limit.exposure_type.value == "CUSTOMER" and request.customer_id:
                applies = True
                exposure_key = f"customer_{request.customer_id}"
            elif limit.exposure_type.value == "GROUP" and request.group_id:
                applies = True
                exposure_key = f"group_{request.group_id}"
            elif limit.exposure_type.value == "INDUSTRY" and request.industry:
                if limit.exposure_name == request.industry:
                    applies = True
                    exposure_key = f"industry_{request.industry}"
            elif limit.exposure_type.value == "GEOGRAPHY" and request.geography:
                if limit.exposure_name == request.geography:
                    applies = True
                    exposure_key = f"geography_{request.geography}"
            elif limit.exposure_type.value == "PRODUCT" and request.product_id:
                applies = True
                exposure_key = f"product_{request.product_id}"
            
            if applies:
                # Calculate current exposure (would query actual loan data in production)
                curr_exp = limit.current_exposure
                new_total = curr_exp + request.loan_amount
                
                current_exposure[exposure_key] = curr_exp
                available_limit[exposure_key] = limit.max_exposure_amount - curr_exp
                
                # Check if limit exceeded
                if new_total > limit.max_exposure_amount:
                    exceeded_limits.append({
                        "exposure_type": limit.exposure_type.value,
                        "exposure_name": limit.exposure_name,
                        "limit": limit.max_exposure_amount,
                        "current": curr_exp,
                        "requested": request.loan_amount,
                        "new_total": new_total,
                        "exceeded_by": new_total - limit.max_exposure_amount
                    })
                
                # Check warning threshold
                utilization = (new_total / limit.max_exposure_amount) * 100
                if utilization >= limit.warning_threshold_percentage:
                    warnings.append(
                        f"{limit.exposure_type.value} {limit.exposure_name} "
                        f"at {utilization:.1f}% utilization (threshold: {limit.warning_threshold_percentage}%)"
                    )
        
        is_within_limits = len(exceeded_limits) == 0
        
        return ExposureCheckResponse(
            is_within_limits=is_within_limits,
            exceeded_limits=exceeded_limits,
            current_exposure=current_exposure,
            available_limit=available_limit,
            warnings=warnings
        )
    
    # =====================================================================
    # ANALYTICS & REPORTING
    # =====================================================================
    
    def get_policy_statistics(self, policy_id: UUID) -> Dict[str, Any]:
        """Get policy statistics"""
        policy = self.get_policy(policy_id)
        if not policy:
            return {}
        
        # In production, these would query actual application/loan data
        stats = {
            "policy_id": str(policy_id),
            "policy_name": policy.name,
            "is_active": policy.is_active,
            "effective_from": policy.effective_from.isoformat() if policy.effective_from else None,
            "configuration": {
                "has_risk_pricing": policy.risk_pricing is not None,
                "score_rate_tiers": len(policy.score_rates) if policy.score_rates else 0,
                "ltv_configurations": len(policy.ltv_ratios) if policy.ltv_ratios else 0,
                "exposure_limits": len(policy.exposure_limits) if policy.exposure_limits else 0,
                "manual_review_triggers": len(policy.manual_review_triggers) if policy.manual_review_triggers else 0,
                "decision_rules": len(policy.decision_matrix) if policy.decision_matrix else 0,
                "counter_offer_rules": len(policy.counter_offer_rules) if policy.counter_offer_rules else 0
            },
            "pricing_range": {
                "min_rate": policy.risk_pricing.min_interest_rate if policy.risk_pricing else None,
                "max_rate": policy.risk_pricing.max_interest_rate if policy.risk_pricing else None
            }
        }
        
        return stats
    
    def test_policy(
        self,
        policy_id: UUID,
        test_scenarios: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Test policy with multiple scenarios"""
        results = []
        
        for scenario in test_scenarios:
            try:
                # Convert scenario to request
                decision_request = CreditDecisionRequest(**scenario)
                
                # Evaluate decision
                decision = self.evaluate_credit_decision(decision_request)
                
                results.append({
                    "scenario": scenario.get("name", "Unnamed"),
                    "success": True,
                    "decision": decision.dict()
                })
            except Exception as e:
                results.append({
                    "scenario": scenario.get("name", "Unnamed"),
                    "success": False,
                    "error": str(e)
                })
        
        return results

    
    def delete_policy(self, policy_id: UUID) -> bool:
        """Delete credit policy"""
        policy = self.get_policy(policy_id)
        if not policy:
            return False
        
        # In production, check if policy is in use before deleting
        self.db.delete(policy)
        self.db.commit()
        return True
    
    def clone_policy(
        self,
        policy_id: UUID,
        new_name: str,
        new_code: str,
        user_id: UUID
    ) -> Optional[CreditPolicy]:
        """Clone an existing policy"""
        original = self.get_policy(policy_id)
        if not original:
            return None
        
        # Create new policy with same configuration
        new_policy = CreditPolicy(
            tenant_id=self.tenant_id,
            product_id=original.product_id,
            name=new_name,
            code=new_code,
            description=f"Cloned from {original.name}",
            version="1.0",
            status=PolicyStatus.DRAFT,
            is_active=False,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(new_policy)
        self.db.flush()  # Get the new policy ID
        
        # Clone related configurations would go here
        # (risk_pricing, score_rates, ltv_ratios, etc.)
        # For brevity, not implementing full clone logic
        
        self.db.commit()
        self.db.refresh(new_policy)
        return new_policy
