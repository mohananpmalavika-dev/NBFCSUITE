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
