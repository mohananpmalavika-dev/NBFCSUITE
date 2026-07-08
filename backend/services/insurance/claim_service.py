"""
Insurance Claim Service

Handles all business logic for claims processing including:
- Claim registration and CRUD
- Claim assessment and approval workflow
- Document verification
- Settlement processing
- Claim statistics and reports
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from backend.services.insurance.models import (
    InsuranceClaim, InsurancePolicy, ClaimStatus, ClaimType, PolicyStatus
)
from backend.shared.common.response import CustomException


class ClaimService:
    """Service for managing insurance claims"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== CRUD OPERATIONS ====================
    
    def create_claim(self, claim_data: Dict[str, Any]) -> InsuranceClaim:
        """
        Register new insurance claim
        
        Args:
            claim_data: Claim information
            
        Returns:
            Created claim
        """
        # Verify policy exists and is eligible for claims
        policy = self.db.query(InsurancePolicy).filter(
            and_(
                InsurancePolicy.id == claim_data.get('policy_id'),
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False
            )
        ).first()
        
        if not policy:
            raise CustomException(status_code=404, message="Policy not found")
        
        # Validate policy status for claim eligibility
        if policy.policy_status not in [PolicyStatus.ACTIVE, PolicyStatus.MATURED]:
            raise CustomException(
                status_code=400,
                message=f"Claims cannot be filed for policies with status: {policy.policy_status}"
            )
        
        # Generate claim number
        claim_number = self._generate_claim_number(claim_data.get('claim_type'))
        
        # Set claimed date if not provided
        claimed_date = claim_data.get('claimed_date', datetime.utcnow())
        
        # Create claim
        claim = InsuranceClaim(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            policy_number=policy.policy_number,
            claim_number=claim_number,
            claimed_date=claimed_date,
            claim_status=ClaimStatus.REGISTERED,
            **claim_data
        )
        
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    def get_claim(self, claim_id: uuid.UUID) -> Optional[InsuranceClaim]:
        """Get claim by ID"""
        claim = self.db.query(InsuranceClaim).filter(
            and_(
                InsuranceClaim.id == claim_id,
                InsuranceClaim.tenant_id == self.tenant_id,
                InsuranceClaim.is_deleted == False
            )
        ).first()
        
        if not claim:
            raise CustomException(status_code=404, message="Claim not found")
        
        return claim
    
    def get_claim_by_number(self, claim_number: str) -> Optional[InsuranceClaim]:
        """Get claim by claim number"""
        claim = self.db.query(InsuranceClaim).filter(
            and_(
                InsuranceClaim.claim_number == claim_number,
                InsuranceClaim.tenant_id == self.tenant_id,
                InsuranceClaim.is_deleted == False
            )
        ).first()
        
        if not claim:
            raise CustomException(status_code=404, message="Claim not found")
        
        return claim
    
    def list_claims(
        self,
        policy_id: Optional[uuid.UUID] = None,
        claim_type: Optional[ClaimType] = None,
        claim_status: Optional[ClaimStatus] = None,
        from_claimed_date: Optional[datetime] = None,
        to_claimed_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InsuranceClaim]:
        """List claims with filters"""
        query = self.db.query(InsuranceClaim).filter(
            and_(
                InsuranceClaim.tenant_id == self.tenant_id,
                InsuranceClaim.is_deleted == False
            )
        )
        
        if policy_id:
            query = query.filter(InsuranceClaim.policy_id == policy_id)
        
        if claim_type:
            query = query.filter(InsuranceClaim.claim_type == claim_type)
        
        if claim_status:
            query = query.filter(InsuranceClaim.claim_status == claim_status)
        
        if from_claimed_date:
            query = query.filter(InsuranceClaim.claimed_date >= from_claimed_date)
        
        if to_claimed_date:
            query = query.filter(InsuranceClaim.claimed_date <= to_claimed_date)
        
        claims = query.order_by(InsuranceClaim.claimed_date.desc()).offset(skip).limit(limit).all()
        return claims
    
    def update_claim(self, claim_id: uuid.UUID, update_data: Dict[str, Any]) -> InsuranceClaim:
        """Update claim information"""
        claim = self.get_claim(claim_id)
        
        # Don't allow status changes through update - use workflow methods
        if 'claim_status' in update_data:
            del update_data['claim_status']
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(claim, key):
                setattr(claim, key, value)
        
        claim.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    # ==================== CLAIM WORKFLOW ====================
    
    def assess_claim(self, claim_id: uuid.UUID, assessment_data: Dict[str, Any]) -> InsuranceClaim:
        """Assess claim and determine eligible amount"""
        claim = self.get_claim(claim_id)
        
        if claim.claim_status not in [ClaimStatus.REGISTERED, ClaimStatus.UNDER_REVIEW, ClaimStatus.DOCUMENTS_PENDING]:
            raise CustomException(
                status_code=400,
                message=f"Cannot assess claim with status: {claim.claim_status}"
            )
        
        # Update assessment details
        claim.assessed_by = self.user_id
        claim.assessed_by_name = assessment_data.get('assessed_by_name')
        claim.assessment_date = datetime.utcnow()
        claim.assessed_amount = assessment_data.get('assessed_amount')
        claim.assessment_remarks = assessment_data.get('assessment_remarks')
        claim.documents_verified = assessment_data.get('documents_verified', False)
        claim.deductions = assessment_data.get('deductions', 0)
        claim.deduction_details = assessment_data.get('deduction_details')
        claim.investigation_status = assessment_data.get('investigation_status')
        claim.investigation_remarks = assessment_data.get('investigation_remarks')
        
        # Calculate net payable
        assessed_amount = Decimal(str(assessment_data.get('assessed_amount', 0)))
        deductions = Decimal(str(assessment_data.get('deductions', 0)))
        claim.net_payable = assessed_amount - deductions
        
        claim.claim_status = ClaimStatus.ASSESSMENT_COMPLETE
        claim.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    def approve_claim(self, claim_id: uuid.UUID, approval_data: Dict[str, Any]) -> InsuranceClaim:
        """Approve claim for settlement"""
        claim = self.get_claim(claim_id)
        
        if claim.claim_status != ClaimStatus.ASSESSMENT_COMPLETE:
            raise CustomException(
                status_code=400,
                message="Claim must be assessed before approval"
            )
        
        claim.approved_by = self.user_id
        claim.approved_by_name = approval_data.get('approved_by_name')
        claim.approval_date = datetime.utcnow()
        claim.approved_amount = approval_data.get('approved_amount')
        claim.approval_remarks = approval_data.get('approval_remarks')
        claim.target_settlement_date = approval_data.get('target_settlement_date')
        
        claim.claim_status = ClaimStatus.APPROVED
        claim.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    def reject_claim(self, claim_id: uuid.UUID, rejection_data: Dict[str, Any]) -> InsuranceClaim:
        """Reject claim"""
        claim = self.get_claim(claim_id)
        
        if claim.claim_status in [ClaimStatus.SETTLED, ClaimStatus.CANCELLED]:
            raise CustomException(
                status_code=400,
                message=f"Cannot reject claim with status: {claim.claim_status}"
            )
        
        claim.claim_status = ClaimStatus.REJECTED
        claim.rejection_reason = rejection_data.get('rejection_reason')
        claim.rejection_date = datetime.utcnow()
        claim.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    def settle_claim(self, claim_id: uuid.UUID, settlement_data: Dict[str, Any]) -> InsuranceClaim:
        """Settle approved claim"""
        claim = self.get_claim(claim_id)
        
        if claim.claim_status != ClaimStatus.APPROVED:
            raise CustomException(
                status_code=400,
                message="Only approved claims can be settled"
            )
        
        claim.settlement_date = settlement_data.get('settlement_date', datetime.utcnow())
        claim.settlement_amount = settlement_data.get('settlement_amount')
        claim.settlement_method = settlement_data.get('settlement_method')
        claim.settlement_reference = settlement_data.get('settlement_reference')
        claim.settlement_remarks = settlement_data.get('settlement_remarks')
        
        # Calculate processing days
        if claim.claimed_date:
            claim.processing_days = (claim.settlement_date - claim.claimed_date).days
        
        claim.claim_status = ClaimStatus.SETTLED
        claim.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    def mark_documents_pending(self, claim_id: uuid.UUID, remarks: Optional[str] = None) -> InsuranceClaim:
        """Mark claim as documents pending"""
        claim = self.get_claim(claim_id)
        
        claim.claim_status = ClaimStatus.DOCUMENTS_PENDING
        if remarks:
            claim.remarks = remarks
        claim.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    def mark_under_review(self, claim_id: uuid.UUID, remarks: Optional[str] = None) -> InsuranceClaim:
        """Mark claim as under review"""
        claim = self.get_claim(claim_id)
        
        if claim.claim_status != ClaimStatus.REGISTERED:
            raise CustomException(
                status_code=400,
                message="Only registered claims can be marked under review"
            )
        
        claim.claim_status = ClaimStatus.UNDER_REVIEW
        if remarks:
            claim.remarks = remarks
        claim.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(claim)
        
        return claim
    
    # ==================== HELPER METHODS ====================
    
    def _generate_claim_number(self, claim_type: ClaimType) -> str:
        """Generate unique claim number"""
        # Format: CLM-TYPE-YYYYMMDD-XXXX
        prefix = f"CLM-{claim_type.value.upper()}"
        date_str = datetime.utcnow().strftime("%Y%m%d")
        
        # Get count of claims created today
        count = self.db.query(func.count(InsuranceClaim.id)).filter(
            and_(
                InsuranceClaim.tenant_id == self.tenant_id,
                InsuranceClaim.claim_type == claim_type,
                func.date(InsuranceClaim.created_at) == datetime.utcnow().date()
            )
        ).scalar()
        
        sequence = str(count + 1).zfill(4)
        return f"{prefix}-{date_str}-{sequence}"
    
    # ==================== STATISTICS ====================
    
    def get_claim_statistics(
        self,
        policy_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get claim statistics"""
        query = self.db.query(InsuranceClaim).filter(
            and_(
                InsuranceClaim.tenant_id == self.tenant_id,
                InsuranceClaim.is_deleted == False
            )
        )
        
        if policy_id:
            query = query.filter(InsuranceClaim.policy_id == policy_id)
        
        total_claims = query.count()
        
        # Claims by status
        claims_by_status = {}
        for status in ClaimStatus:
            count = query.filter(InsuranceClaim.claim_status == status).count()
            claims_by_status[status.value] = count
        
        # Claims by type
        claims_by_type = {}
        for claim_type in ClaimType:
            count = query.filter(InsuranceClaim.claim_type == claim_type).count()
            claims_by_type[claim_type.value] = count
        
        # Amount calculations
        claimed_amount = query.with_entities(
            func.sum(InsuranceClaim.claim_amount)
        ).scalar() or Decimal(0)
        
        assessed_amount = query.filter(
            InsuranceClaim.assessed_amount.isnot(None)
        ).with_entities(
            func.sum(InsuranceClaim.assessed_amount)
        ).scalar() or Decimal(0)
        
        approved_amount = query.filter(
            InsuranceClaim.approved_amount.isnot(None)
        ).with_entities(
            func.sum(InsuranceClaim.approved_amount)
        ).scalar() or Decimal(0)
        
        settled_amount = query.filter(
            InsuranceClaim.claim_status == ClaimStatus.SETTLED
        ).with_entities(
            func.sum(InsuranceClaim.settlement_amount)
        ).scalar() or Decimal(0)
        
        # Average processing days
        avg_processing = query.filter(
            InsuranceClaim.processing_days.isnot(None)
        ).with_entities(
            func.avg(InsuranceClaim.processing_days)
        ).scalar()
        
        avg_processing_days = int(avg_processing) if avg_processing else None
        
        # Settlement rate
        settled_claims = claims_by_status.get('settled', 0)
        settlement_rate = (settled_claims / total_claims * 100) if total_claims > 0 else 0
        
        return {
            "total_claims": total_claims,
            "claims_by_status": claims_by_status,
            "claims_by_type": claims_by_type,
            "total_claimed_amount": float(claimed_amount),
            "total_assessed_amount": float(assessed_amount),
            "total_approved_amount": float(approved_amount),
            "total_settled_amount": float(settled_amount),
            "average_processing_days": avg_processing_days,
            "settlement_rate": round(settlement_rate, 2)
        }
