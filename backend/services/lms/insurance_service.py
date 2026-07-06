"""
Loan Insurance Tracking Service
Business logic for insurance policy management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from backend.shared.database.lms_extended_models import (
    LoanInsurancePolicy, InsurancePremiumPayment, InsuranceClaim,
    InsurancePolicyType, InsurancePolicyStatus
)
from backend.shared.database.loan_models import LoanAccount

logger = logging.getLogger(__name__)


class InsuranceService:
    """Service for insurance operations"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    def create_policy(
        self,
        loan_account_id: int,
        customer_id: str,
        policy_data: dict,
        user_id: str
    ) -> LoanInsurancePolicy:
        """Create insurance policy"""
        
        policy = LoanInsurancePolicy(
            tenant_id=self.tenant_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            created_by=user_id,
            updated_by=user_id,
            **policy_data
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        logger.info(f"Insurance policy created: {policy.policy_number}")
        
        return policy
    
    def get_expiring_policies(self, days: int = 30) -> List[LoanInsurancePolicy]:
        """Get policies expiring in next X days"""
        today = date.today()
        expiry_date = today + timedelta(days=days)
        
        return self.db.query(LoanInsurancePolicy).filter(
            and_(
                LoanInsurancePolicy.tenant_id == self.tenant_id,
                LoanInsurancePolicy.status == InsurancePolicyStatus.ACTIVE,
                LoanInsurancePolicy.policy_end_date >= today,
                LoanInsurancePolicy.policy_end_date <= expiry_date,
                LoanInsurancePolicy.is_deleted == False
            )
        ).order_by(LoanInsurancePolicy.policy_end_date.asc()).all()
    
    def send_renewal_reminder(self, policy_id: int) -> bool:
        """Send renewal reminder"""
        
        policy = self.db.query(LoanInsurancePolicy).filter(
            and_(
                LoanInsurancePolicy.id == policy_id,
                LoanInsurancePolicy.tenant_id == self.tenant_id
            )
        ).first()
        
        if not policy:
            return False
        
        policy.renewal_notice_sent = True
        policy.renewal_notice_date = date.today()
        policy.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Renewal reminder sent for policy: {policy.policy_number}")
        
        return True
    
    def create_claim(
        self,
        policy_id: int,
        loan_account_id: int,
        claim_data: dict,
        user_id: str
    ) -> InsuranceClaim:
        """Create insurance claim"""
        
        claim = InsuranceClaim(
            tenant_id=self.tenant_id,
            policy_id=policy_id,
            loan_account_id=loan_account_id,
            created_by=user_id,
            updated_by=user_id,
            **claim_data
        )
        
        self.db.add(claim)
        
        # Update policy
        policy = self.db.query(LoanInsurancePolicy).filter(
            LoanInsurancePolicy.id == policy_id
        ).first()
        if policy:
            policy.claims_count += 1
            policy.last_claim_date = claim_data.get('claim_date', date.today())
        
        self.db.commit()
        self.db.refresh(claim)
        
        logger.info(f"Insurance claim created: {claim.claim_number}")
        
        return claim
