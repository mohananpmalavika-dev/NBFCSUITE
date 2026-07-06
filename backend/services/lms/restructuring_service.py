"""
Loan Restructuring Service
Business logic for loan restructuring management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import logging

from backend.shared.database.lms_extended_models import (
    LoanRestructuring, RestructuringType, RestructuringStatus, AssetClassification
)
from backend.shared.database.loan_models import LoanAccount

logger = logging.getLogger(__name__)


class RestructuringService:
    """Service for loan restructuring operations"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    def create_restructuring_request(
        self,
        loan_account_id: int,
        customer_id: str,
        request_data: dict,
        user_id: str
    ) -> LoanRestructuring:
        """Create restructuring request"""
        
        loan_account = self.db.query(LoanAccount).filter(
            and_(
                LoanAccount.id == loan_account_id,
                LoanAccount.tenant_id == self.tenant_id
            )
        ).first()
        
        if not loan_account:
            raise ValueError("Loan account not found")
        
        request_number = self._generate_request_number()
        
        restructuring = LoanRestructuring(
            tenant_id=self.tenant_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            request_number=request_number,
            request_date=date.today(),
            created_by=user_id,
            updated_by=user_id,
            **request_data
        )
        
        self.db.add(restructuring)
        self.db.commit()
        self.db.refresh(restructuring)
        
        logger.info(f"Restructuring request created: {request_number}")
        
        return restructuring
    
    def approve_restructuring(
        self,
        restructuring_id: int,
        approval_data: dict,
        user_id: str
    ) -> LoanRestructuring:
        """Approve restructuring request"""
        
        restructuring = self.db.query(LoanRestructuring).filter(
            and_(
                LoanRestructuring.id == restructuring_id,
                LoanRestructuring.tenant_id == self.tenant_id
            )
        ).first()
        
        if not restructuring:
            raise ValueError("Restructuring not found")
        
        restructuring.status = RestructuringStatus.APPROVED
        restructuring.approved_by = user_id
        restructuring.approved_date = date.today()
        
        for field, value in approval_data.items():
            if hasattr(restructuring, field):
                setattr(restructuring, field, value)
        
        self.db.commit()
        self.db.refresh(restructuring)
        
        logger.info(f"Restructuring approved: {restructuring.request_number}")
        
        return restructuring
    
    def implement_restructuring(
        self,
        restructuring_id: int,
        user_id: str
    ) -> LoanRestructuring:
        """Implement approved restructuring"""
        
        restructuring = self.db.query(LoanRestructuring).filter(
            and_(
                LoanRestructuring.id == restructuring_id,
                LoanRestructuring.tenant_id == self.tenant_id
            )
        ).first()
        
        if not restructuring:
            raise ValueError("Restructuring not found")
        
        if restructuring.status != RestructuringStatus.APPROVED:
            raise ValueError("Restructuring must be approved before implementation")
        
        restructuring.status = RestructuringStatus.IMPLEMENTED
        restructuring.implemented_date = date.today()
        restructuring.effective_date = date.today()
        restructuring.updated_by = user_id
        
        # TODO: Update loan account with new terms
        
        self.db.commit()
        self.db.refresh(restructuring)
        
        logger.info(f"Restructuring implemented: {restructuring.request_number}")
        
        return restructuring
    
    def _generate_request_number(self) -> str:
        """Generate unique request number"""
        now = datetime.utcnow()
        prefix = f"RST{now.strftime('%Y%m')}"
        
        last = self.db.query(LoanRestructuring).filter(
            and_(
                LoanRestructuring.tenant_id == self.tenant_id,
                LoanRestructuring.request_number.like(f"{prefix}%")
            )
        ).order_by(LoanRestructuring.id.desc()).first()
        
        if last:
            last_num = int(last.request_number.split(prefix)[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:05d}"
