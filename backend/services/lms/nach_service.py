"""
NACH/eNACH Mandate Management Service
Business logic for NACH mandate registration and auto-debit management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
import hashlib
import json

from backend.shared.database.lms_extended_models import (
    NACHMandate, NACHDebitTransaction,
    MandateType, MandateStatus, MandateFrequency, DebitStatus
)
from backend.shared.database.loan_models import LoanAccount

logger = logging.getLogger(__name__)


class NACHService:
    """Service for NACH/eNACH mandate operations"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    # ============================================
    # Mandate Management
    # ============================================
    
    def create_mandate(
        self,
        loan_account_id: int,
        customer_id: str,
        mandate_data: dict,
        user_id: str
    ) -> NACHMandate:
        """Create NACH/eNACH mandate"""
        
        # Validate loan account
        loan_account = self.db.query(LoanAccount).filter(
            and_(
                LoanAccount.id == loan_account_id,
                LoanAccount.tenant_id == self.tenant_id
            )
        ).first()
        
        if not loan_account:
            raise ValueError("Loan account not found")
        
        # Check if mandate already exists
        existing = self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.loan_account_id == loan_account_id,
                NACHMandate.tenant_id == self.tenant_id,
                NACHMandate.status.in_([
                    MandateStatus.PENDING,
                    MandateStatus.SUBMITTED,
                    MandateStatus.APPROVED,
                    MandateStatus.ACTIVE
                ])
            )
        ).first()
        
        if existing:
            raise ValueError(f"Active mandate already exists: {existing.mandate_number}")
        
        # Generate mandate number
        mandate_number = self._generate_mandate_number()
        
        # Create mandate
        mandate = NACHMandate(
            tenant_id=self.tenant_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            mandate_number=mandate_number,
            created_by=user_id,
            updated_by=user_id,
            **mandate_data
        )
        
        self.db.add(mandate)
        self.db.commit()
        self.db.refresh(mandate)
        
        logger.info(f"NACH mandate created: {mandate_number}")
        
        return mandate
    
    def initiate_enach(
        self,
        mandate_id: int,
        return_url: str,
        user_id: str
    ) -> dict:
        """Initiate eNACH mandate registration"""
        
        mandate = self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.id == mandate_id,
                NACHMandate.tenant_id == self.tenant_id
            )
        ).first()
        
        if not mandate:
            raise ValueError("Mandate not found")
        
        if mandate.mandate_type != MandateType.ENACH:
            raise ValueError("Mandate is not eNACH type")
        
        # Generate eNACH URL (mock implementation)
        enach_url = self._generate_enach_url(mandate, return_url)
        
        mandate.enach_url = enach_url
        mandate.enach_initiated_date = datetime.utcnow()
        mandate.status = MandateStatus.PENDING
        mandate.updated_by = user_id
        mandate.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(mandate)
        
        logger.info(f"eNACH initiated for mandate: {mandate.mandate_number}")
        
        return {
            "mandate_id": mandate.id,
            "mandate_number": mandate.mandate_number,
            "enach_url": enach_url,
            "expires_in": 900  # 15 minutes
        }
    
    def authenticate_enach(
        self,
        mandate_id: int,
        authentication_mode: str,
        authentication_ref: str,
        user_id: str
    ) -> NACHMandate:
        """Process eNACH authentication response"""
        
        mandate = self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.id == mandate_id,
                NACHMandate.tenant_id == self.tenant_id
            )
        ).first()
        
        if not mandate:
            raise ValueError("Mandate not found")
        
        mandate.enach_authenticated_date = datetime.utcnow()
        mandate.authentication_mode = authentication_mode
        mandate.status = MandateStatus.SUBMITTED
        mandate.submission_date = date.today()
        mandate.submission_reference = authentication_ref
        mandate.updated_by = user_id
        mandate.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(mandate)
        
        logger.info(f"eNACH authenticated for mandate: {mandate.mandate_number}")
        
        return mandate
    
    def submit_physical_mandate(
        self,
        mandate_id: int,
        form_number: str,
        form_date: date,
        user_id: str
    ) -> NACHMandate:
        """Submit physical NACH mandate form"""
        
        mandate = self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.id == mandate_id,
                NACHMandate.tenant_id == self.tenant_id
            )
        ).first()
        
        if not mandate:
            raise ValueError("Mandate not found")
        
        if mandate.mandate_type != MandateType.NACH:
            raise ValueError("Mandate is not physical NACH type")
        
        mandate.nach_form_number = form_number
        mandate.nach_form_date = form_date
        mandate.physical_mandate_received = True
        mandate.status = MandateStatus.SUBMITTED
        mandate.submission_date = date.today()
        mandate.updated_by = user_id
        mandate.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(mandate)
        
        logger.info(f"Physical NACH submitted: {mandate.mandate_number}")
        
        return mandate
    
    def approve_mandate(
        self,
        mandate_id: int,
        umrn: str,
        approval_ref: str,
        user_id: str
    ) -> NACHMandate:
        """Approve NACH mandate (from bank/NPCI)"""
        
        mandate = self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.id == mandate_id,
                NACHMandate.tenant_id == self.tenant_id
            )
        ).first()
        
        if not mandate:
            raise ValueError("Mandate not found")
        
        mandate.umrn = umrn
        mandate.status = MandateStatus.APPROVED
        mandate.approval_date = date.today()
        mandate.approval_reference = approval_ref
        mandate.updated_by = user_id
        mandate.updated_at = datetime.utcnow()
        
        # Activate if start date is today or past
        if mandate.start_date <= date.today():
            mandate.status = MandateStatus.ACTIVE
        
        self.db.commit()
        self.db.refresh(mandate)
        
        logger.info(f"Mandate approved: {mandate.mandate_number}, UMRN: {umrn}")
        
        return mandate
    
    def cancel_mandate(
        self,
        mandate_id: int,
        reason: str,
        user_id: str
    ) -> NACHMandate:
        """Cancel NACH mandate"""
        
        mandate = self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.id == mandate_id,
                NACHMandate.tenant_id == self.tenant_id
            )
        ).first()
        
        if not mandate:
            raise ValueError("Mandate not found")
        
        mandate.status = MandateStatus.CANCELLED
        mandate.cancellation_date = date.today()
        mandate.cancellation_reason = reason
        mandate.cancellation_initiated_by = user_id
        mandate.auto_debit_enabled = False
        mandate.updated_by = user_id
        mandate.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(mandate)
        
        logger.info(f"Mandate cancelled: {mandate.mandate_number}")
        
        return mandate
    
    # ============================================
    # Auto-Debit Management
    # ============================================
    
    def initiate_auto_debit(
        self,
        mandate_id: int,
        installment_number: int,
        emi_due_date: date,
        debit_amount: Decimal,
        user_id: str = None
    ) -> NACHDebitTransaction:
        """Initiate auto-debit transaction"""
        
        mandate = self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.id == mandate_id,
                NACHMandate.tenant_id == self.tenant_id
            )
        ).first()
        
        if not mandate:
            raise ValueError("Mandate not found")
        
        if mandate.status != MandateStatus.ACTIVE:
            raise ValueError(f"Mandate not active: {mandate.status}")
        
        if not mandate.auto_debit_enabled:
            raise ValueError("Auto-debit is disabled for this mandate")
        
        if debit_amount > mandate.max_amount:
            raise ValueError(f"Debit amount {debit_amount} exceeds max amount {mandate.max_amount}")
        
        # Generate transaction reference
        transaction_ref = self._generate_transaction_reference(mandate, installment_number)
        
        # Create debit transaction
        debit_txn = NACHDebitTransaction(
            tenant_id=self.tenant_id,
            mandate_id=mandate_id,
            loan_account_id=mandate.loan_account_id,
            transaction_reference=transaction_ref,
            presentation_date=emi_due_date,
            debit_amount=debit_amount,
            installment_number=installment_number,
            emi_due_date=emi_due_date,
            status=DebitStatus.INITIATED,
            initiated_date=datetime.utcnow()
        )
        
        self.db.add(debit_txn)
        
        # Update mandate statistics
        mandate.total_debits_attempted += 1
        mandate.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(debit_txn)
        
        logger.info(f"Auto-debit initiated: {transaction_ref} for mandate {mandate.mandate_number}")
        
        # TODO: Send to NPCI/Bank for processing
        
        return debit_txn
    
    def process_debit_response(
        self,
        transaction_id: int,
        success: bool,
        response_data: dict
    ) -> NACHDebitTransaction:
        """Process debit response from bank/NPCI"""
        
        debit_txn = self.db.query(NACHDebitTransaction).filter(
            and_(
                NACHDebitTransaction.id == transaction_id,
                NACHDebitTransaction.tenant_id == self.tenant_id
            )
        ).first()
        
        if not debit_txn:
            raise ValueError("Transaction not found")
        
        debit_txn.processed_date = datetime.utcnow()
        debit_txn.response_code = response_data.get('response_code')
        debit_txn.response_message = response_data.get('response_message')
        debit_txn.bank_reference = response_data.get('bank_reference')
        debit_txn.npci_reference = response_data.get('npci_reference')
        
        # Get mandate
        mandate = self.db.query(NACHMandate).filter(
            NACHMandate.id == debit_txn.mandate_id
        ).first()
        
        if success:
            debit_txn.status = DebitStatus.SUCCESS
            debit_txn.settlement_date = response_data.get('settlement_date', date.today())
            debit_txn.utr_number = response_data.get('utr_number')
            
            # Update mandate statistics
            mandate.total_debits_success += 1
            mandate.total_amount_debited += debit_txn.debit_amount
            mandate.last_debit_date = date.today()
            mandate.last_debit_status = 'success'
            mandate.consecutive_failures = 0
            
            logger.info(f"Debit successful: {debit_txn.transaction_reference}")
            
        else:
            debit_txn.status = DebitStatus.FAILED
            debit_txn.failure_reason = response_data.get('failure_reason')
            debit_txn.failure_category = response_data.get('failure_category')
            
            # Update mandate statistics
            mandate.total_debits_failed += 1
            mandate.last_debit_date = date.today()
            mandate.last_debit_status = 'failed'
            mandate.consecutive_failures += 1
            
            # Check if retry is possible
            if mandate.retry_on_failure and debit_txn.retry_attempt < mandate.max_retry_attempts:
                debit_txn.can_retry = True
                debit_txn.retry_scheduled_date = date.today() + timedelta(days=mandate.retry_interval_days)
            else:
                debit_txn.can_retry = False
            
            # Suspend mandate after too many consecutive failures
            if mandate.consecutive_failures >= 5:
                mandate.status = MandateStatus.SUSPENDED
                logger.warning(f"Mandate suspended due to consecutive failures: {mandate.mandate_number}")
            
            logger.warning(f"Debit failed: {debit_txn.transaction_reference}, reason: {debit_txn.failure_reason}")
        
        debit_txn.updated_at = datetime.utcnow()
        mandate.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(debit_txn)
        
        return debit_txn
    
    def retry_failed_debit(
        self,
        transaction_id: int
    ) -> NACHDebitTransaction:
        """Retry a failed debit transaction"""
        
        original_txn = self.db.query(NACHDebitTransaction).filter(
            and_(
                NACHDebitTransaction.id == transaction_id,
                NACHDebitTransaction.tenant_id == self.tenant_id
            )
        ).first()
        
        if not original_txn:
            raise ValueError("Transaction not found")
        
        if original_txn.status != DebitStatus.FAILED:
            raise ValueError("Can only retry failed transactions")
        
        if not original_txn.can_retry:
            raise ValueError("Transaction cannot be retried")
        
        # Create retry transaction
        retry_txn = NACHDebitTransaction(
            tenant_id=self.tenant_id,
            mandate_id=original_txn.mandate_id,
            loan_account_id=original_txn.loan_account_id,
            transaction_reference=f"{original_txn.transaction_reference}-R{original_txn.retry_attempt + 1}",
            presentation_date=original_txn.retry_scheduled_date,
            debit_amount=original_txn.debit_amount,
            installment_number=original_txn.installment_number,
            emi_due_date=original_txn.emi_due_date,
            status=DebitStatus.INITIATED,
            initiated_date=datetime.utcnow(),
            is_retry=True,
            retry_attempt=original_txn.retry_attempt + 1,
            original_transaction_id=original_txn.id
        )
        
        self.db.add(retry_txn)
        
        # Update original transaction
        original_txn.can_retry = False
        
        self.db.commit()
        self.db.refresh(retry_txn)
        
        logger.info(f"Retry transaction created: {retry_txn.transaction_reference}")
        
        return retry_txn
    
    # ============================================
    # Query Methods
    # ============================================
    
    def get_mandate(self, mandate_id: int) -> Optional[NACHMandate]:
        """Get mandate by ID"""
        return self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.id == mandate_id,
                NACHMandate.tenant_id == self.tenant_id
            )
        ).first()
    
    def get_active_mandate_for_loan(self, loan_account_id: int) -> Optional[NACHMandate]:
        """Get active mandate for a loan account"""
        return self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.loan_account_id == loan_account_id,
                NACHMandate.tenant_id == self.tenant_id,
                NACHMandate.status == MandateStatus.ACTIVE,
                NACHMandate.start_date <= date.today(),
                NACHMandate.end_date >= date.today()
            )
        ).first()
    
    def get_pending_mandates(self) -> List[NACHMandate]:
        """Get all pending mandate registrations"""
        return self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.tenant_id == self.tenant_id,
                NACHMandate.status.in_([MandateStatus.PENDING, MandateStatus.SUBMITTED])
            )
        ).order_by(NACHMandate.created_at.asc()).all()
    
    def get_failed_debits_for_retry(self) -> List[NACHDebitTransaction]:
        """Get failed debits that can be retried"""
        today = date.today()
        return self.db.query(NACHDebitTransaction).filter(
            and_(
                NACHDebitTransaction.tenant_id == self.tenant_id,
                NACHDebitTransaction.status == DebitStatus.FAILED,
                NACHDebitTransaction.can_retry == True,
                NACHDebitTransaction.retry_scheduled_date <= today
            )
        ).all()
    
    def get_mandate_statistics(self, mandate_id: int) -> dict:
        """Get mandate statistics"""
        mandate = self.get_mandate(mandate_id)
        if not mandate:
            return {}
        
        success_rate = 0
        if mandate.total_debits_attempted > 0:
            success_rate = (mandate.total_debits_success / mandate.total_debits_attempted) * 100
        
        return {
            "mandate_number": mandate.mandate_number,
            "status": mandate.status,
            "total_attempts": mandate.total_debits_attempted,
            "successful": mandate.total_debits_success,
            "failed": mandate.total_debits_failed,
            "success_rate": round(success_rate, 2),
            "total_amount_debited": mandate.total_amount_debited,
            "last_debit_date": mandate.last_debit_date,
            "last_debit_status": mandate.last_debit_status,
            "consecutive_failures": mandate.consecutive_failures
        }
    
    # ============================================
    # Helper Methods
    # ============================================
    
    def _generate_mandate_number(self) -> str:
        """Generate unique mandate number"""
        now = datetime.utcnow()
        prefix = f"NACH{now.strftime('%Y%m')}"
        
        last_mandate = self.db.query(NACHMandate).filter(
            and_(
                NACHMandate.tenant_id == self.tenant_id,
                NACHMandate.mandate_number.like(f"{prefix}%")
            )
        ).order_by(NACHMandate.id.desc()).first()
        
        if last_mandate:
            last_num = int(last_mandate.mandate_number.split(prefix)[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:06d}"
    
    def _generate_transaction_reference(self, mandate: NACHMandate, installment: int) -> str:
        """Generate unique transaction reference"""
        base = f"{mandate.mandate_number}-{installment}-{date.today().strftime('%Y%m%d')}"
        hash_val = hashlib.md5(base.encode()).hexdigest()[:8].upper()
        return f"TXN{hash_val}"
    
    def _generate_enach_url(self, mandate: NACHMandate, return_url: str) -> str:
        """Generate eNACH URL (mock implementation)"""
        # In production, this would call actual NPCI eNACH API
        params = {
            "mandate_id": mandate.id,
            "mandate_number": mandate.mandate_number,
            "customer_id": str(mandate.customer_id),
            "bank_ifsc": mandate.bank_ifsc,
            "account_number": mandate.bank_account_number,
            "max_amount": str(mandate.max_amount),
            "return_url": return_url
        }
        
        # Mock URL
        return f"https://enach-gateway.npci.org.in/authenticate?params={json.dumps(params)}"
