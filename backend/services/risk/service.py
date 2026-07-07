"""
Risk Management Service
Business logic for credit policies, risk-based pricing, exposure limits, risk ratings, and early warning signals
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
import uuid

from backend.shared.database.risk_models import (
    CreditPolicy, RiskPricingRule, ExposureLimit, ExposureTransaction,
    RiskRating, EarlyWarningSignal, EarlyWarningAlert
)
from backend.shared.database.loan_models import LoanApplication, LoanAccount
from backend.shared.database.customer_models import Customer
from . import schemas

logger = logging.getLogger(__name__)


class RiskManagementService:
    """Service for risk management operations"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    # ============================================
    # Credit Policy Management
    # ============================================
    
    def create_credit_policy(
        self,
        data: schemas.CreditPolicyCreate,
        user_id: str
    ) -> CreditPolicy:
        """Create new credit policy"""
        
        # Check for duplicate policy code
        existing = self.db.query(CreditPolicy).filter(
            and_(
                CreditPolicy.tenant_id == self.tenant_id,
                CreditPolicy.policy_code == data.policy_code,
                CreditPolicy.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Credit policy with code '{data.policy_code}' already exists")
        
        policy = CreditPolicy(
            tenant_id=self.tenant_id,
            **data.model_dump(),
            created_by=uuid.UUID(user_id),
            updated_by=uuid.UUID(user_id)
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        logger.info(f"Credit policy created: {policy.policy_code}")
        return policy
    
    def get_credit_policy(self, policy_id: int) -> Optional[CreditPolicy]:
        """Get credit policy by ID"""
        return self.db.query(CreditPolicy).filter(
            and_(
                CreditPolicy.id == policy_id,
                CreditPolicy.tenant_id == self.tenant_id,
                CreditPolicy.is_deleted == False
            )
        ).first()
    
    def get_credit_policy_by_code(self, policy_code: str) -> Optional[CreditPolicy]:
        """Get credit policy by code"""
        return self.db.query(CreditPolicy).filter(
            and_(
                CreditPolicy.policy_code == policy_code,
                CreditPolicy.tenant_id == self.tenant_id,
                CreditPolicy.is_deleted == False
            )
        ).first()
    
    def list_credit_policies(
        self,
        page: int = 1,
        page_size: int = 50,
        is_active: Optional[bool] = None,
        product_type: Optional[str] = None
    ) -> schemas.CreditPolicyListResponse:
        """List credit policies with pagination"""
        
        query = self.db.query(CreditPolicy).filter(
            and_(
                CreditPolicy.tenant_id == self.tenant_id,
                CreditPolicy.is_deleted == False
            )
        )
        
        if is_active is not None:
            query = query.filter(CreditPolicy.is_active == is_active)
        
        if product_type:
            query = query.filter(CreditPolicy.product_types.contains([product_type]))
        
        total = query.count()
        
        policies = query.order_by(desc(CreditPolicy.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return schemas.CreditPolicyListResponse(
            items=[schemas.CreditPolicyResponse.model_validate(p) for p in policies],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    def update_credit_policy(
        self,
        policy_id: int,
        data: schemas.CreditPolicyUpdate,
        user_id: str
    ) -> Optional[CreditPolicy]:
        """Update credit policy"""
        
        policy = self.get_credit_policy(policy_id)
        if not policy:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(policy, key, value)
        
        policy.updated_by = uuid.UUID(user_id)
        policy.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(policy)
        
        logger.info(f"Credit policy updated: {policy.policy_code}")
        return policy
    
    def delete_credit_policy(self, policy_id: int, user_id: str) -> bool:
        """Soft delete credit policy"""
        
        policy = self.get_credit_policy(policy_id)
        if not policy:
            return False
        
        policy.is_deleted = True
        policy.updated_by = uuid.UUID(user_id)
        policy.updated_at = datetime.utcnow()
        
        self.db.commit()
        logger.info(f"Credit policy deleted: {policy.policy_code}")
        return True
    
    def evaluate_policy(
        self,
        request: schemas.PolicyEvaluationRequest
    ) -> schemas.PolicyEvaluationResponse:
        """Evaluate loan application against credit policies"""
        
        passed_checks = []
        failed_checks = []
        warnings = []
        
        # Find applicable policies
        policies = self.db.query(CreditPolicy).filter(
            and_(
                CreditPolicy.tenant_id == self.tenant_id,
                CreditPolicy.is_active == True,
                CreditPolicy.is_deleted == False,
                CreditPolicy.effective_from <= date.today()
            )
        ).all()
        
        applicable_policy = None
        for policy in policies:
            # Check product type
            if policy.product_types and request.product_type not in policy.product_types:
                continue
            
            # Check loan category
            if policy.loan_categories and request.loan_category not in policy.loan_categories:
                continue
            
            # Check customer segment
            if policy.customer_segments and request.customer_segment not in policy.customer_segments:
                continue
            
            applicable_policy = policy
            break
        
        if not applicable_policy:
            return schemas.PolicyEvaluationResponse(
                eligible=False,
                passed_checks=[],
                failed_checks=["No applicable credit policy found"],
                warnings=[],
                debt_to_income_ratio=Decimal("0"),
                recommendations=["Contact credit team for policy assignment"]
            )
        
        # Calculate DTI
        dti = (request.existing_obligations / request.monthly_income) * 100 if request.monthly_income > 0 else Decimal("100")
        
        # Evaluate against policy criteria
        eligible = True
        
        # Credit score check
        if request.credit_score < applicable_policy.min_cibil_score:
            failed_checks.append(f"Credit score {request.credit_score} below minimum {applicable_policy.min_cibil_score}")
            eligible = False
        else:
            passed_checks.append(f"Credit score {request.credit_score} meets minimum requirement")
        
        # DTI check
        if dti > applicable_policy.max_debt_to_income_ratio:
            failed_checks.append(f"DTI {dti:.2f}% exceeds maximum {applicable_policy.max_debt_to_income_ratio}%")
            eligible = False
        else:
            passed_checks.append(f"DTI {dti:.2f}% within acceptable range")
        
        # Loan amount check
        if request.loan_amount < applicable_policy.min_loan_amount:
            failed_checks.append(f"Loan amount below minimum {applicable_policy.min_loan_amount}")
            eligible = False
        elif request.loan_amount > applicable_policy.max_loan_amount:
            failed_checks.append(f"Loan amount exceeds maximum {applicable_policy.max_loan_amount}")
            eligible = False
        else:
            passed_checks.append("Loan amount within policy limits")
        
        # Age check
        if request.age < applicable_policy.min_age:
            failed_checks.append(f"Age {request.age} below minimum {applicable_policy.min_age}")
            eligible = False
        elif request.age > applicable_policy.max_age:
            failed_checks.append(f"Age {request.age} exceeds maximum {applicable_policy.max_age}")
            eligible = False
        else:
            passed_checks.append("Age meets policy requirements")
        
        # Income check
        if applicable_policy.min_monthly_income and request.monthly_income < applicable_policy.min_monthly_income:
            failed_checks.append(f"Monthly income below minimum {applicable_policy.min_monthly_income}")
            eligible = False
        else:
            passed_checks.append("Income meets minimum requirement")
        
        # Employment type check
        if applicable_policy.allowed_employment_types and request.employment_type not in applicable_policy.allowed_employment_types:
            failed_checks.append(f"Employment type '{request.employment_type}' not allowed")
            eligible = False
        else:
            passed_checks.append("Employment type is acceptable")
        
        # Determine risk grade based on credit score
        risk_grade = self._calculate_risk_grade(request.credit_score)
        
        # Get suggested interest rate
        suggested_rate = self._get_risk_based_pricing(
            credit_score=request.credit_score,
            loan_amount=request.loan_amount,
            tenure_months=request.tenure_months,
            customer_segment=request.customer_segment,
            employment_type=request.employment_type,
            loan_category=request.loan_category,
            risk_grade=risk_grade,
            policy_id=applicable_policy.id
        )
        
        recommendations = []
        if not eligible:
            recommendations.append("Application does not meet credit policy criteria")
            if dti > applicable_policy.max_debt_to_income_ratio:
                recommendations.append("Consider co-applicant to improve DTI ratio")
        else:
            recommendations.append("Application meets all credit policy criteria")
            if dti > 40:
                warnings.append("DTI ratio is on the higher side, monitor closely")
        
        return schemas.PolicyEvaluationResponse(
            eligible=eligible,
            applicable_policy_code=applicable_policy.policy_code,
            applicable_policy_name=applicable_policy.policy_name,
            risk_grade=risk_grade,
            suggested_interest_rate=suggested_rate,
            max_eligible_amount=applicable_policy.max_loan_amount if eligible else None,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            debt_to_income_ratio=dti,
            foir=dti,
            recommendations=recommendations
        )
    
    # ============================================
    # Risk-Based Pricing
    # ============================================
    
    def create_pricing_rule(
        self,
        data: schemas.RiskPricingRuleCreate,
        user_id: str
    ) -> RiskPricingRule:
        """Create risk-based pricing rule"""
        
        # Check for duplicate rule code
        existing = self.db.query(RiskPricingRule).filter(
            and_(
                RiskPricingRule.tenant_id == self.tenant_id,
                RiskPricingRule.rule_code == data.rule_code,
                RiskPricingRule.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Pricing rule with code '{data.rule_code}' already exists")
        
        rule = RiskPricingRule(
            tenant_id=self.tenant_id,
            **data.model_dump(),
            created_by=uuid.UUID(user_id),
            updated_by=uuid.UUID(user_id)
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        logger.info(f"Pricing rule created: {rule.rule_code}")
        return rule
    
    def list_pricing_rules(
        self,
        page: int = 1,
        page_size: int = 50,
        policy_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> schemas.RiskPricingRuleListResponse:
        """List pricing rules with pagination"""
        
        query = self.db.query(RiskPricingRule).filter(
            and_(
                RiskPricingRule.tenant_id == self.tenant_id,
                RiskPricingRule.is_deleted == False
            )
        )
        
        if policy_id:
            query = query.filter(RiskPricingRule.credit_policy_id == policy_id)
        
        if is_active is not None:
            query = query.filter(RiskPricingRule.is_active == is_active)
        
        total = query.count()
        
        rules = query.order_by(
            desc(RiskPricingRule.rule_priority),
            desc(RiskPricingRule.created_at)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return schemas.RiskPricingRuleListResponse(
            items=[schemas.RiskPricingRuleResponse.model_validate(r) for r in rules],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    def calculate_pricing(
        self,
        request: schemas.PricingCalculationRequest
    ) -> schemas.PricingCalculationResponse:
        """Calculate risk-based pricing for a loan"""
        
        risk_grade = self._calculate_risk_grade(request.credit_score)
        
        # Find matching pricing rules (ordered by priority)
        rules = self.db.query(RiskPricingRule).filter(
            and_(
                RiskPricingRule.tenant_id == self.tenant_id,
                RiskPricingRule.is_active == True,
                RiskPricingRule.is_deleted == False,
                RiskPricingRule.effective_from <= date.today()
            )
        ).order_by(desc(RiskPricingRule.rule_priority)).all()
        
        applicable_rule = None
        for rule in rules:
            # Check all conditions
            if rule.min_credit_score and request.credit_score < rule.min_credit_score:
                continue
            if rule.max_credit_score and request.credit_score > rule.max_credit_score:
                continue
            if rule.min_loan_amount and request.loan_amount < rule.min_loan_amount:
                continue
            if rule.max_loan_amount and request.loan_amount > rule.max_loan_amount:
                continue
            if rule.min_tenure_months and request.tenure_months < rule.min_tenure_months:
                continue
            if rule.max_tenure_months and request.tenure_months > rule.max_tenure_months:
                continue
            if rule.customer_segment and request.customer_segment != rule.customer_segment:
                continue
            if rule.employment_type and request.employment_type != rule.employment_type:
                continue
            if rule.loan_category and request.loan_category != rule.loan_category:
                continue
            if rule.risk_ratings and risk_grade not in rule.risk_ratings:
                continue
            
            applicable_rule = rule
            break
        
        if not applicable_rule:
            # Return default pricing
            return schemas.PricingCalculationResponse(
                base_rate=Decimal("12.00"),
                risk_adjustment=Decimal("0.00"),
                final_rate=Decimal("12.00"),
                waive_prepayment_charges=False
            )
        
        return schemas.PricingCalculationResponse(
            base_rate=applicable_rule.base_interest_rate,
            risk_adjustment=applicable_rule.rate_adjustment,
            final_rate=applicable_rule.final_interest_rate,
            processing_fee_adjustment=applicable_rule.processing_fee_adjustment,
            applicable_rule_code=applicable_rule.rule_code,
            applicable_rule_name=applicable_rule.rule_name,
            cashback_percentage=applicable_rule.cashback_percentage,
            loyalty_discount=applicable_rule.loyalty_discount,
            waive_prepayment_charges=applicable_rule.waive_prepayment_charges
        )
    
    def _get_risk_based_pricing(
        self,
        credit_score: int,
        loan_amount: Decimal,
        tenure_months: int,
        customer_segment: str,
        employment_type: str,
        loan_category: str,
        risk_grade: str,
        policy_id: int
    ) -> Decimal:
        """Internal method to get risk-based pricing"""
        
        rules = self.db.query(RiskPricingRule).filter(
            and_(
                RiskPricingRule.tenant_id == self.tenant_id,
                RiskPricingRule.credit_policy_id == policy_id,
                RiskPricingRule.is_active == True,
                RiskPricingRule.is_deleted == False
            )
        ).order_by(desc(RiskPricingRule.rule_priority)).all()
        
        for rule in rules:
            if rule.min_credit_score and credit_score < rule.min_credit_score:
                continue
            if rule.max_credit_score and credit_score > rule.max_credit_score:
                continue
            if rule.risk_ratings and risk_grade not in rule.risk_ratings:
                continue
            
            return rule.final_interest_rate
        
        return Decimal("12.00")  # Default rate
    
    # ============================================
    # Exposure Limit Management
    # ============================================
    
    def create_exposure_limit(
        self,
        data: schemas.ExposureLimitCreate,
        user_id: str
    ) -> ExposureLimit:
        """Create exposure limit"""
        
        # Check for duplicate limit code
        existing = self.db.query(ExposureLimit).filter(
            and_(
                ExposureLimit.tenant_id == self.tenant_id,
                ExposureLimit.limit_code == data.limit_code,
                ExposureLimit.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Exposure limit with code '{data.limit_code}' already exists")
        
        limit = ExposureLimit(
            tenant_id=self.tenant_id,
            **data.model_dump(),
            utilized_amount=Decimal("0.00"),
            available_amount=data.limit_amount,
            utilization_percentage=Decimal("0.00"),
            created_by=uuid.UUID(user_id),
            updated_by=uuid.UUID(user_id)
        )
        
        self.db.add(limit)
        self.db.commit()
        self.db.refresh(limit)
        
        logger.info(f"Exposure limit created: {limit.limit_code}")
        return limit
    
    def get_exposure_limit(self, limit_id: int) -> Optional[ExposureLimit]:
        """Get exposure limit by ID"""
        return self.db.query(ExposureLimit).filter(
            and_(
                ExposureLimit.id == limit_id,
                ExposureLimit.tenant_id == self.tenant_id,
                ExposureLimit.is_deleted == False
            )
        ).first()
    
    def list_exposure_limits(
        self,
        page: int = 1,
        page_size: int = 50,
        limit_type: Optional[str] = None,
        is_breached: Optional[bool] = None
    ) -> schemas.ExposureLimitListResponse:
        """List exposure limits with pagination"""
        
        query = self.db.query(ExposureLimit).filter(
            and_(
                ExposureLimit.tenant_id == self.tenant_id,
                ExposureLimit.is_deleted == False
            )
        )
        
        if limit_type:
            query = query.filter(ExposureLimit.limit_type == limit_type)
        
        if is_breached is not None:
            query = query.filter(ExposureLimit.is_breached == is_breached)
        
        total = query.count()
        
        limits = query.order_by(desc(ExposureLimit.utilization_percentage)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return schemas.ExposureLimitListResponse(
            items=[schemas.ExposureLimitResponse.model_validate(l) for l in limits],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    def utilize_exposure(
        self,
        limit_id: int,
        request: schemas.ExposureUtilizationRequest,
        user_id: str
    ) -> ExposureTransaction:
        """Utilize exposure limit"""
        
        limit = self.get_exposure_limit(limit_id)
        if not limit:
            raise ValueError("Exposure limit not found")
        
        if not limit.is_active:
            raise ValueError("Exposure limit is not active")
        
        # Check if utilization would breach limit
        new_utilized = limit.utilized_amount + request.amount
        if new_utilized > limit.limit_amount:
            raise ValueError(f"Utilization would breach limit. Available: {limit.available_amount}")
        
        # Create transaction
        transaction = ExposureTransaction(
            tenant_id=self.tenant_id,
            exposure_limit_id=limit_id,
            transaction_type="utilization",
            transaction_reference=request.transaction_reference,
            loan_application_id=request.loan_application_id,
            loan_account_id=request.loan_account_id,
            amount=request.amount,
            previous_utilized=limit.utilized_amount,
            new_utilized=new_utilized,
            remarks=request.remarks,
            processed_by=uuid.UUID(user_id)
        )
        
        self.db.add(transaction)
        
        # Update limit
        limit.utilized_amount = new_utilized
        limit.available_amount = limit.limit_amount - new_utilized
        limit.utilization_percentage = (new_utilized / limit.limit_amount) * 100
        
        # Check for breach
        if limit.utilization_percentage >= 100:
            limit.is_breached = True
            limit.breach_date = datetime.utcnow()
            limit.breach_remarks = "Limit fully utilized"
        elif limit.utilization_percentage >= limit.critical_threshold_percentage:
            logger.warning(f"Exposure limit {limit.limit_code} reached critical threshold")
        elif limit.utilization_percentage >= limit.warning_threshold_percentage:
            logger.info(f"Exposure limit {limit.limit_code} reached warning threshold")
        
        limit.updated_at = datetime.utcnow()
        limit.updated_by = uuid.UUID(user_id)
        
        self.db.commit()
        self.db.refresh(transaction)
        
        logger.info(f"Exposure utilized: {limit.limit_code}, Amount: {request.amount}")
        return transaction
    
    def release_exposure(
        self,
        limit_id: int,
        request: schemas.ExposureUtilizationRequest,
        user_id: str
    ) -> ExposureTransaction:
        """Release exposure limit"""
        
        limit = self.get_exposure_limit(limit_id)
        if not limit:
            raise ValueError("Exposure limit not found")
        
        if request.amount > limit.utilized_amount:
            raise ValueError(f"Release amount exceeds utilized amount: {limit.utilized_amount}")
        
        # Create transaction
        new_utilized = limit.utilized_amount - request.amount
        
        transaction = ExposureTransaction(
            tenant_id=self.tenant_id,
            exposure_limit_id=limit_id,
            transaction_type="release",
            transaction_reference=request.transaction_reference,
            loan_application_id=request.loan_application_id,
            loan_account_id=request.loan_account_id,
            amount=request.amount,
            previous_utilized=limit.utilized_amount,
            new_utilized=new_utilized,
            remarks=request.remarks,
            processed_by=uuid.UUID(user_id)
        )
        
        self.db.add(transaction)
        
        # Update limit
        limit.utilized_amount = new_utilized
        limit.available_amount = limit.limit_amount - new_utilized
        limit.utilization_percentage = (new_utilized / limit.limit_amount) * 100 if limit.limit_amount > 0 else Decimal("0")
        
        # Clear breach if applicable
        if limit.is_breached and limit.utilization_percentage < 100:
            limit.is_breached = False
            limit.breach_date = None
            limit.breach_remarks = None
        
        limit.updated_at = datetime.utcnow()
        limit.updated_by = uuid.UUID(user_id)
        
        self.db.commit()
        self.db.refresh(transaction)
        
        logger.info(f"Exposure released: {limit.limit_code}, Amount: {request.amount}")
        return transaction
    
    # ============================================
    # Risk Rating Management
    # ============================================
    
    def create_risk_rating(
        self,
        data: schemas.RiskRatingCreate,
        user_id: str
    ) -> RiskRating:
        """Create risk rating"""
        
        # Calculate expected loss if PD, LGD, EAD provided
        expected_loss = None
        if data.pd_percentage and data.lgd_percentage and data.ead_amount:
            expected_loss = (data.pd_percentage / 100) * (data.lgd_percentage / 100) * data.ead_amount
        
        rating = RiskRating(
            tenant_id=self.tenant_id,
            **data.model_dump(),
            expected_loss=expected_loss,
            created_by=uuid.UUID(user_id),
            updated_by=uuid.UUID(user_id)
        )
        
        self.db.add(rating)
        self.db.commit()
        self.db.refresh(rating)
        
        logger.info(f"Risk rating created for customer: {data.customer_id}")
        return rating
    
    def get_latest_risk_rating(
        self,
        customer_id: str,
        rating_type: str = "customer"
    ) -> Optional[RiskRating]:
        """Get latest risk rating for customer"""
        return self.db.query(RiskRating).filter(
            and_(
                RiskRating.tenant_id == self.tenant_id,
                RiskRating.customer_id == uuid.UUID(customer_id),
                RiskRating.rating_type == rating_type,
                RiskRating.is_deleted == False
            )
        ).order_by(desc(RiskRating.rating_date)).first()
    
    def list_risk_ratings(
        self,
        page: int = 1,
        page_size: int = 50,
        customer_id: Optional[str] = None,
        risk_grade: Optional[str] = None,
        rating_type: Optional[str] = None
    ) -> schemas.RiskRatingListResponse:
        """List risk ratings with pagination"""
        
        query = self.db.query(RiskRating).filter(
            and_(
                RiskRating.tenant_id == self.tenant_id,
                RiskRating.is_deleted == False
            )
        )
        
        if customer_id:
            query = query.filter(RiskRating.customer_id == uuid.UUID(customer_id))
        
        if risk_grade:
            query = query.filter(RiskRating.risk_grade == risk_grade)
        
        if rating_type:
            query = query.filter(RiskRating.rating_type == rating_type)
        
        total = query.count()
        
        ratings = query.order_by(desc(RiskRating.rating_date)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return schemas.RiskRatingListResponse(
            items=[schemas.RiskRatingResponse.model_validate(r) for r in ratings],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    def override_risk_rating(
        self,
        rating_id: int,
        request: schemas.RiskRatingOverrideRequest,
        user_id: str
    ) -> Optional[RiskRating]:
        """Override risk rating with approval"""
        
        rating = self.db.query(RiskRating).filter(
            and_(
                RiskRating.id == rating_id,
                RiskRating.tenant_id == self.tenant_id,
                RiskRating.is_deleted == False
            )
        ).first()
        
        if not rating:
            return None
        
        # Store original values
        rating.original_risk_grade = rating.risk_grade
        rating.original_risk_score = rating.risk_score
        
        # Apply override
        rating.risk_grade = request.new_risk_grade
        rating.risk_score = request.new_risk_score
        rating.rating_override = True
        rating.override_reason = request.override_reason
        rating.override_approved_by = uuid.UUID(user_id)
        rating.override_date = datetime.utcnow()
        rating.updated_by = uuid.UUID(user_id)
        rating.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(rating)
        
        logger.info(f"Risk rating overridden: {rating_id}")
        return rating
    
    def get_risk_rating_stats(self) -> schemas.RiskRatingStats:
        """Get risk rating statistics"""
        
        # Total rated customers
        total = self.db.query(func.count(func.distinct(RiskRating.customer_id))).filter(
            and_(
                RiskRating.tenant_id == self.tenant_id,
                RiskRating.rating_type == "customer",
                RiskRating.is_deleted == False
            )
        ).scalar() or 0
        
        # Rating distribution
        distribution_query = self.db.query(
            RiskRating.risk_grade,
            func.count(func.distinct(RiskRating.customer_id))
        ).filter(
            and_(
                RiskRating.tenant_id == self.tenant_id,
                RiskRating.rating_type == "customer",
                RiskRating.is_deleted == False
            )
        ).group_by(RiskRating.risk_grade).all()
        
        rating_distribution = {grade: count for grade, count in distribution_query}
        
        # Average score
        avg_score = self.db.query(func.avg(RiskRating.risk_score)).filter(
            and_(
                RiskRating.tenant_id == self.tenant_id,
                RiskRating.rating_type == "customer",
                RiskRating.is_deleted == False
            )
        ).scalar() or 0.0
        
        # High risk count (C+, C, D grades)
        high_risk = self.db.query(func.count(func.distinct(RiskRating.customer_id))).filter(
            and_(
                RiskRating.tenant_id == self.tenant_id,
                RiskRating.rating_type == "customer",
                RiskRating.risk_grade.in_(["C+", "C", "D"]),
                RiskRating.is_deleted == False
            )
        ).scalar() or 0
        
        high_risk_pct = (high_risk / total * 100) if total > 0 else 0.0
        
        # Average PD
        avg_pd = self.db.query(func.avg(RiskRating.pd_percentage)).filter(
            and_(
                RiskRating.tenant_id == self.tenant_id,
                RiskRating.pd_percentage.isnot(None),
                RiskRating.is_deleted == False
            )
        ).scalar()
        
        # Total expected loss
        total_el = self.db.query(func.sum(RiskRating.expected_loss)).filter(
            and_(
                RiskRating.tenant_id == self.tenant_id,
                RiskRating.expected_loss.isnot(None),
                RiskRating.is_deleted == False
            )
        ).scalar()
        
        return schemas.RiskRatingStats(
            total_rated_customers=total,
            rating_distribution=rating_distribution,
            average_score=float(avg_score),
            high_risk_count=high_risk,
            high_risk_percentage=high_risk_pct,
            avg_pd_percentage=float(avg_pd) if avg_pd else None,
            total_expected_loss=total_el
        )
    
    def _calculate_risk_grade(self, credit_score: int) -> str:
        """Calculate risk grade based on credit score"""
        if credit_score >= 800:
            return "A+"
        elif credit_score >= 750:
            return "A"
        elif credit_score >= 700:
            return "B+"
        elif credit_score >= 650:
            return "B"
        elif credit_score >= 600:
            return "C+"
        elif credit_score >= 550:
            return "C"
        else:
            return "D"
    
    # ============================================
    # Early Warning Signals
    # ============================================
    
    def create_ews_signal(
        self,
        data: schemas.EarlyWarningSignalCreate,
        user_id: str
    ) -> EarlyWarningSignal:
        """Create early warning signal configuration"""
        
        # Check for duplicate signal code
        existing = self.db.query(EarlyWarningSignal).filter(
            and_(
                EarlyWarningSignal.tenant_id == self.tenant_id,
                EarlyWarningSignal.signal_code == data.signal_code,
                EarlyWarningSignal.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"EWS signal with code '{data.signal_code}' already exists")
        
        signal = EarlyWarningSignal(
            tenant_id=self.tenant_id,
            **data.model_dump(),
            created_by=uuid.UUID(user_id),
            updated_by=uuid.UUID(user_id)
        )
        
        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)
        
        logger.info(f"EWS signal created: {signal.signal_code}")
        return signal
    
    def list_ews_signals(
        self,
        page: int = 1,
        page_size: int = 50,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> schemas.EarlyWarningSignalListResponse:
        """List early warning signals with pagination"""
        
        query = self.db.query(EarlyWarningSignal).filter(
            and_(
                EarlyWarningSignal.tenant_id == self.tenant_id,
                EarlyWarningSignal.is_deleted == False
            )
        )
        
        if category:
            query = query.filter(EarlyWarningSignal.signal_category == category)
        
        if is_active is not None:
            query = query.filter(EarlyWarningSignal.is_active == is_active)
        
        total = query.count()
        
        signals = query.order_by(desc(EarlyWarningSignal.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return schemas.EarlyWarningSignalListResponse(
            items=[schemas.EarlyWarningSignalResponse.model_validate(s) for s in signals],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    def create_ews_alert(
        self,
        signal_id: int,
        customer_id: str,
        loan_account_id: int,
        detected_value: Optional[Decimal] = None,
        threshold_value: Optional[Decimal] = None,
        alert_data: Optional[Dict[str, Any]] = None
    ) -> EarlyWarningAlert:
        """Create early warning alert"""
        
        signal = self.db.query(EarlyWarningSignal).filter(
            and_(
                EarlyWarningSignal.id == signal_id,
                EarlyWarningSignal.tenant_id == self.tenant_id,
                EarlyWarningSignal.is_deleted == False
            )
        ).first()
        
        if not signal:
            raise ValueError("EWS signal not found")
        
        # Generate alert number
        alert_number = f"EWS-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate variance
        variance = None
        if detected_value and threshold_value and threshold_value > 0:
            variance = ((detected_value - threshold_value) / threshold_value) * 100
        
        alert = EarlyWarningAlert(
            tenant_id=self.tenant_id,
            signal_id=signal_id,
            alert_number=alert_number,
            customer_id=uuid.UUID(customer_id),
            loan_account_id=loan_account_id,
            signal_category=signal.signal_category,
            severity_level=signal.severity_level,
            detected_value=detected_value,
            threshold_value=threshold_value,
            variance_percentage=variance,
            status="open",
            first_occurrence_date=datetime.utcnow(),
            last_occurrence_date=datetime.utcnow(),
            alert_data=alert_data
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"EWS alert created: {alert_number}")
        return alert
    
    def list_ews_alerts(
        self,
        page: int = 1,
        page_size: int = 50,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> schemas.EarlyWarningAlertListResponse:
        """List early warning alerts with pagination"""
        
        query = self.db.query(EarlyWarningAlert).filter(
            and_(
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.is_deleted == False
            )
        )
        
        if status:
            query = query.filter(EarlyWarningAlert.status == status)
        
        if severity:
            query = query.filter(EarlyWarningAlert.severity_level == severity)
        
        if category:
            query = query.filter(EarlyWarningAlert.signal_category == category)
        
        if customer_id:
            query = query.filter(EarlyWarningAlert.customer_id == uuid.UUID(customer_id))
        
        total = query.count()
        
        alerts = query.order_by(
            desc(EarlyWarningAlert.severity_level == "critical"),
            desc(EarlyWarningAlert.alert_date)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # Enrich with customer and account info
        enriched_alerts = []
        for alert in alerts:
            alert_dict = schemas.EarlyWarningAlertResponse.model_validate(alert).model_dump()
            
            # Get customer name
            customer = self.db.query(Customer).filter(
                Customer.id == alert.customer_id
            ).first()
            if customer:
                alert_dict['customer_name'] = customer.full_name
            
            # Get loan account number
            account = self.db.query(LoanAccount).filter(
                LoanAccount.id == alert.loan_account_id
            ).first()
            if account:
                alert_dict['loan_account_number'] = account.loan_account_number
            
            # Get signal details
            signal = self.db.query(EarlyWarningSignal).filter(
                EarlyWarningSignal.id == alert.signal_id
            ).first()
            if signal:
                alert_dict['signal_code'] = signal.signal_code
                alert_dict['signal_name'] = signal.signal_name
            
            enriched_alerts.append(schemas.EarlyWarningAlertResponse(**alert_dict))
        
        return schemas.EarlyWarningAlertListResponse(
            items=enriched_alerts,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    def take_alert_action(
        self,
        alert_id: int,
        request: schemas.AlertActionRequest,
        user_id: str
    ) -> Optional[EarlyWarningAlert]:
        """Take action on early warning alert"""
        
        alert = self.db.query(EarlyWarningAlert).filter(
            and_(
                EarlyWarningAlert.id == alert_id,
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.is_deleted == False
            )
        ).first()
        
        if not alert:
            return None
        
        user_uuid = uuid.UUID(user_id)
        
        if request.action == "acknowledge":
            alert.status = "acknowledged"
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_uuid
        
        elif request.action == "assign":
            if not request.assigned_to:
                raise ValueError("assigned_to is required for assign action")
            alert.assigned_to = uuid.UUID(request.assigned_to)
            alert.assigned_at = datetime.utcnow()
            alert.status = "investigating"
        
        elif request.action == "resolve":
            alert.status = "resolved"
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = user_uuid
            alert.resolution_remarks = request.resolution_remarks
        
        elif request.action == "escalate":
            alert.status = "escalated"
            alert.escalation_level += 1
            alert.escalated_at = datetime.utcnow()
            if request.assigned_to:
                alert.escalated_to = uuid.UUID(request.assigned_to)
            alert.escalation_remarks = request.remarks
        
        elif request.action == "mark_false_positive":
            alert.status = "false_positive"
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = user_uuid
            alert.resolution_remarks = request.remarks or "Marked as false positive"
        
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Alert action taken: {alert.alert_number}, Action: {request.action}")
        return alert
    
    def get_ews_alert_stats(self) -> schemas.EarlyWarningAlertStats:
        """Get early warning alert statistics"""
        
        # Total alerts
        total = self.db.query(func.count(EarlyWarningAlert.id)).filter(
            and_(
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.is_deleted == False
            )
        ).scalar() or 0
        
        # Open alerts
        open_alerts = self.db.query(func.count(EarlyWarningAlert.id)).filter(
            and_(
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.status == "open",
                EarlyWarningAlert.is_deleted == False
            )
        ).scalar() or 0
        
        # Critical alerts
        critical = self.db.query(func.count(EarlyWarningAlert.id)).filter(
            and_(
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.severity_level == "critical",
                EarlyWarningAlert.status.in_(["open", "acknowledged", "investigating"]),
                EarlyWarningAlert.is_deleted == False
            )
        ).scalar() or 0
        
        # High alerts
        high = self.db.query(func.count(EarlyWarningAlert.id)).filter(
            and_(
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.severity_level == "high",
                EarlyWarningAlert.status.in_(["open", "acknowledged", "investigating"]),
                EarlyWarningAlert.is_deleted == False
            )
        ).scalar() or 0
        
        # Resolved today
        today = date.today()
        resolved_today = self.db.query(func.count(EarlyWarningAlert.id)).filter(
            and_(
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.status == "resolved",
                func.date(EarlyWarningAlert.resolved_at) == today,
                EarlyWarningAlert.is_deleted == False
            )
        ).scalar() or 0
        
        # Alerts by category
        category_query = self.db.query(
            EarlyWarningAlert.signal_category,
            func.count(EarlyWarningAlert.id)
        ).filter(
            and_(
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.is_deleted == False
            )
        ).group_by(EarlyWarningAlert.signal_category).all()
        
        alerts_by_category = {cat: count for cat, count in category_query}
        
        # Alerts by severity
        severity_query = self.db.query(
            EarlyWarningAlert.severity_level,
            func.count(EarlyWarningAlert.id)
        ).filter(
            and_(
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.is_deleted == False
            )
        ).group_by(EarlyWarningAlert.severity_level).all()
        
        alerts_by_severity = {sev: count for sev, count in severity_query}
        
        # Average resolution time
        avg_resolution = self.db.query(
            func.avg(
                func.extract('epoch', EarlyWarningAlert.resolved_at - EarlyWarningAlert.alert_date) / 3600
            )
        ).filter(
            and_(
                EarlyWarningAlert.tenant_id == self.tenant_id,
                EarlyWarningAlert.status == "resolved",
                EarlyWarningAlert.resolved_at.isnot(None),
                EarlyWarningAlert.is_deleted == False
            )
        ).scalar()
        
        return schemas.EarlyWarningAlertStats(
            total_alerts=total,
            open_alerts=open_alerts,
            critical_alerts=critical,
            high_alerts=high,
            resolved_today=resolved_today,
            avg_resolution_time_hours=float(avg_resolution) if avg_resolution else None,
            alerts_by_category=alerts_by_category,
            alerts_by_severity=alerts_by_severity
        )
    
    # ============================================
    # Portfolio Monitoring & Detection
    # ============================================
    
    def detect_early_warnings(self, loan_account_id: int) -> List[EarlyWarningAlert]:
        """Detect and create early warning alerts for a loan account"""
        
        # Get active EWS signals
        signals = self.db.query(EarlyWarningSignal).filter(
            and_(
                EarlyWarningSignal.tenant_id == self.tenant_id,
                EarlyWarningSignal.is_active == True,
                EarlyWarningSignal.is_deleted == False
            )
        ).all()
        
        # Get loan account
        account = self.db.query(LoanAccount).filter(
            and_(
                LoanAccount.id == loan_account_id,
                LoanAccount.tenant_id == self.tenant_id
            )
        ).first()
        
        if not account:
            return []
        
        created_alerts = []
        
        for signal in signals:
            rule = signal.detection_rule
            
            # Evaluate detection rule
            triggered = False
            detected_value = None
            threshold_value = signal.trigger_threshold
            
            # Example: DPD-based detection
            if rule.get("condition") == "dpd":
                operator = rule.get("operator", ">=")
                value = rule.get("value", 30)
                
                if operator == ">=" and account.days_past_due >= value:
                    triggered = True
                    detected_value = Decimal(str(account.days_past_due))
                    threshold_value = Decimal(str(value))
            
            # Example: Outstanding amount increase
            elif rule.get("condition") == "outstanding_increase":
                # Logic for detecting increase in outstanding
                pass
            
            # Example: Multiple bounces
            elif rule.get("condition") == "bounces":
                # Logic for detecting bounces
                pass
            
            if triggered:
                # Check if alert already exists for this account and signal
                existing = self.db.query(EarlyWarningAlert).filter(
                    and_(
                        EarlyWarningAlert.tenant_id == self.tenant_id,
                        EarlyWarningAlert.signal_id == signal.id,
                        EarlyWarningAlert.loan_account_id == loan_account_id,
                        EarlyWarningAlert.status.in_(["open", "acknowledged", "investigating"]),
                        EarlyWarningAlert.is_deleted == False
                    )
                ).first()
                
                if existing:
                    # Update recurrence
                    existing.is_recurring = True
                    existing.occurrence_count += 1
                    existing.last_occurrence_date = datetime.utcnow()
                    self.db.commit()
                else:
                    # Create new alert
                    alert = self.create_ews_alert(
                        signal_id=signal.id,
                        customer_id=str(account.customer_id),
                        loan_account_id=loan_account_id,
                        detected_value=detected_value,
                        threshold_value=threshold_value
                    )
                    created_alerts.append(alert)
        
        return created_alerts
