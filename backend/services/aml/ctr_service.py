"""
CTR (Cash Transaction Report) Service
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID, uuid4

from backend.shared.database.aml_models import (
    AMLCTRReport,
    ReportStatus,
    AMLAuditLog
)
from backend.services.aml.schemas import (
    CTRReportCreate,
    CTRBulkSubmit
)


class CTRService:
    """Service for Cash Transaction Reports (CTR)"""
    
    # CTR threshold in INR (10 Lakhs)
    CTR_THRESHOLD = Decimal('1000000')
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def create_ctr_report(
        self,
        data: CTRReportCreate,
        user_id: Optional[UUID] = None
    ) -> AMLCTRReport:
        """Create a new CTR report"""
        ctr_number = self._generate_ctr_number(data.reporting_month)
        
        ctr = AMLCTRReport(
            id=uuid4(),
            tenant_id=self.tenant_id,
            ctr_number=ctr_number,
            reporting_month=data.reporting_month,
            reporting_date=date.today(),
            transaction_date=data.transaction_date,
            transaction_type=data.transaction_type,
            transaction_amount=data.transaction_amount,
            customer_id=data.customer_id,
            customer_name=data.customer_name,
            customer_type=data.customer_type,
            pan_number=data.pan_number,
            aadhaar_number=data.aadhaar_number,
            passport_number=data.passport_number,
            customer_address=data.customer_address,
            customer_phone=data.customer_phone,
            occupation=data.occupation,
            nature_of_business=data.nature_of_business,
            account_number=data.account_number,
            account_type=data.account_type,
            branch_code=data.branch_code,
            branch_name=data.branch_name,
            mode_of_transaction=data.mode_of_transaction,
            currency=data.currency,
            identity_verified=data.identity_verified,
            verification_document_type=data.verification_document_type,
            verification_document_number=data.verification_document_number,
            remarks=data.remarks,
            status=ReportStatus.DRAFT,
            prepared_by=user_id,
            prepared_at=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(ctr)
        
        # Log creation
        self._log_audit(
            event_type='ctr_created',
            user_id=user_id,
            reference_id=str(ctr.id),
            action=f"Created CTR report {ctr_number}",
            action_details={
                'ctr_number': ctr_number,
                'transaction_amount': float(data.transaction_amount),
                'customer_name': data.customer_name
            }
        )
        
        self.db.commit()
        self.db.refresh(ctr)
        
        return ctr
    
    def get_ctr_report(self, ctr_id: UUID) -> Optional[AMLCTRReport]:
        """Get CTR report by ID"""
        return self.db.query(AMLCTRReport).filter(
            AMLCTRReport.tenant_id == self.tenant_id,
            AMLCTRReport.id == ctr_id
        ).first()
    
    def list_ctr_reports(
        self,
        reporting_month: Optional[str] = None,
        status: Optional[str] = None,
        customer_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        submitted_to_fiu: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AMLCTRReport]:
        """List CTR reports with filters"""
        query = self.db.query(AMLCTRReport).filter(
            AMLCTRReport.tenant_id == self.tenant_id
        )
        
        if reporting_month:
            query = query.filter(AMLCTRReport.reporting_month == reporting_month)
        
        if status:
            query = query.filter(AMLCTRReport.status == status)
        
        if customer_id:
            query = query.filter(AMLCTRReport.customer_id == customer_id)
        
        if start_date:
            query = query.filter(AMLCTRReport.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(AMLCTRReport.transaction_date <= end_date)
        
        if submitted_to_fiu is not None:
            query = query.filter(AMLCTRReport.submitted_to_fiu == submitted_to_fiu)
        
        query = query.order_by(desc(AMLCTRReport.transaction_date))
        
        return query.offset(skip).limit(limit).all()
    
    def review_ctr_report(
        self,
        ctr_id: UUID,
        user_id: UUID
    ) -> Optional[AMLCTRReport]:
        """Review CTR report"""
        ctr = self.get_ctr_report(ctr_id)
        
        if not ctr:
            return None
        
        ctr.status = ReportStatus.PENDING_REVIEW
        ctr.reviewed_by = user_id
        ctr.reviewed_at = datetime.utcnow()
        ctr.updated_by = user_id
        ctr.updated_at = datetime.utcnow()
        
        self._log_audit(
            event_type='ctr_reviewed',
            user_id=user_id,
            reference_id=str(ctr.id),
            action=f"Reviewed CTR report {ctr.ctr_number}"
        )
        
        self.db.commit()
        self.db.refresh(ctr)
        
        return ctr
    
    def approve_ctr_report(
        self,
        ctr_id: UUID,
        user_id: UUID
    ) -> Optional[AMLCTRReport]:
        """Approve CTR report for submission"""
        ctr = self.get_ctr_report(ctr_id)
        
        if not ctr:
            return None
        
        ctr.status = ReportStatus.APPROVED
        ctr.updated_by = user_id
        ctr.updated_at = datetime.utcnow()
        
        self._log_audit(
            event_type='ctr_approved',
            user_id=user_id,
            reference_id=str(ctr.id),
            action=f"Approved CTR report {ctr.ctr_number}"
        )
        
        self.db.commit()
        self.db.refresh(ctr)
        
        return ctr
    
    def submit_to_fiu(
        self,
        ctr_id: UUID,
        fiu_reference_number: str,
        user_id: UUID
    ) -> Optional[AMLCTRReport]:
        """Submit CTR report to FIU-IND"""
        ctr = self.get_ctr_report(ctr_id)
        
        if not ctr:
            return None
        
        if ctr.status != ReportStatus.APPROVED:
            raise ValueError("CTR report must be approved before submission")
        
        ctr.status = ReportStatus.SUBMITTED
        ctr.submitted_to_fiu = True
        ctr.fiu_submission_date = datetime.utcnow()
        ctr.fiu_reference_number = fiu_reference_number
        ctr.updated_by = user_id
        ctr.updated_at = datetime.utcnow()
        
        self._log_audit(
            event_type='ctr_submitted_to_fiu',
            user_id=user_id,
            reference_id=str(ctr.id),
            action=f"Submitted CTR report {ctr.ctr_number} to FIU",
            action_details={
                'fiu_reference': fiu_reference_number
            }
        )
        
        self.db.commit()
        self.db.refresh(ctr)
        
        return ctr
    
    def bulk_submit_to_fiu(
        self,
        bulk_submit: CTRBulkSubmit,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Bulk submit CTR reports to FIU"""
        submitted = []
        failed = []
        
        for ctr_id in bulk_submit.ctr_ids:
            try:
                ctr = self.get_ctr_report(ctr_id)
                if ctr and ctr.status == ReportStatus.APPROVED:
                    # Generate FIU reference for each
                    fiu_ref = f"FIU-CTR-{bulk_submit.reporting_month}-{ctr.ctr_number}"
                    self.submit_to_fiu(ctr_id, fiu_ref, user_id)
                    submitted.append(str(ctr_id))
                else:
                    failed.append({
                        'ctr_id': str(ctr_id),
                        'reason': 'Not approved or not found'
                    })
            except Exception as e:
                failed.append({
                    'ctr_id': str(ctr_id),
                    'reason': str(e)
                })
        
        return {
            'submitted_count': len(submitted),
            'failed_count': len(failed),
            'submitted_ids': submitted,
            'failed': failed
        }
    
    def auto_generate_ctrs_for_month(
        self,
        reporting_month: str,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Auto-generate CTR reports for cash transactions above threshold
        """
        from backend.shared.database.aml_models import AMLTransactionMonitoring
        
        # Parse reporting month (YYYY-MM format)
        year, month = reporting_month.split('-')
        start_date = date(int(year), int(month), 1)
        
        # Calculate end date
        if int(month) == 12:
            end_date = date(int(year) + 1, 1, 1)
        else:
            end_date = date(int(year), int(month) + 1, 1)
        
        # Find cash transactions above threshold
        transactions = self.db.query(AMLTransactionMonitoring).filter(
            AMLTransactionMonitoring.tenant_id == self.tenant_id,
            AMLTransactionMonitoring.is_cash_transaction == True,
            AMLTransactionMonitoring.transaction_amount >= self.CTR_THRESHOLD,
            AMLTransactionMonitoring.posting_date >= start_date,
            AMLTransactionMonitoring.posting_date < end_date
        ).all()
        
        created_count = 0
        skipped_count = 0
        
        for txn in transactions:
            # Check if CTR already exists for this transaction
            existing = self.db.query(AMLCTRReport).filter(
                AMLCTRReport.tenant_id == self.tenant_id,
                AMLCTRReport.customer_id == txn.customer_id,
                AMLCTRReport.transaction_date == txn.posting_date,
                AMLCTRReport.transaction_amount == txn.transaction_amount
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # Create CTR report
            ctr_data = CTRReportCreate(
                reporting_month=reporting_month,
                transaction_date=txn.posting_date,
                transaction_type=txn.transaction_type,
                transaction_amount=txn.transaction_amount,
                customer_id=txn.customer_id,
                customer_name=txn.customer_name,
                customer_type=txn.customer_type,
                account_number=txn.account_number or "N/A",
                branch_code=txn.branch_code,
                identity_verified=False
            )
            
            self.create_ctr_report(ctr_data, user_id)
            created_count += 1
        
        return {
            'reporting_month': reporting_month,
            'total_transactions': len(transactions),
            'created_count': created_count,
            'skipped_count': skipped_count
        }
    
    def get_ctr_statistics(
        self,
        reporting_month: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get CTR statistics"""
        query = self.db.query(AMLCTRReport).filter(
            AMLCTRReport.tenant_id == self.tenant_id
        )
        
        if reporting_month:
            query = query.filter(AMLCTRReport.reporting_month == reporting_month)
        
        total = query.count()
        
        draft = query.filter(AMLCTRReport.status == ReportStatus.DRAFT).count()
        pending = query.filter(AMLCTRReport.status == ReportStatus.PENDING_REVIEW).count()
        approved = query.filter(AMLCTRReport.status == ReportStatus.APPROVED).count()
        submitted = query.filter(AMLCTRReport.status == ReportStatus.SUBMITTED).count()
        
        total_amount = self.db.query(
            func.sum(AMLCTRReport.transaction_amount)
        ).filter(
            AMLCTRReport.tenant_id == self.tenant_id
        ).scalar() or Decimal('0')
        
        if reporting_month:
            total_amount = self.db.query(
                func.sum(AMLCTRReport.transaction_amount)
            ).filter(
                AMLCTRReport.tenant_id == self.tenant_id,
                AMLCTRReport.reporting_month == reporting_month
            ).scalar() or Decimal('0')
        
        return {
            'total_reports': total,
            'draft': draft,
            'pending_review': pending,
            'approved': approved,
            'submitted': submitted,
            'total_amount': total_amount
        }
    
    def _generate_ctr_number(self, reporting_month: str) -> str:
        """Generate unique CTR number"""
        prefix = "CTR"
        month_str = reporting_month.replace('-', '')
        
        # Get count for this month
        count = self.db.query(func.count(AMLCTRReport.id)).filter(
            AMLCTRReport.tenant_id == self.tenant_id,
            AMLCTRReport.reporting_month == reporting_month
        ).scalar() or 0
        
        return f"{prefix}{month_str}{count + 1:05d}"
    
    def _log_audit(
        self,
        event_type: str,
        user_id: Optional[UUID],
        reference_id: str,
        action: str,
        action_details: Optional[Dict] = None
    ):
        """Log audit entry"""
        log = AMLAuditLog(
            id=uuid4(),
            tenant_id=self.tenant_id,
            event_type=event_type,
            event_category='reporting',
            event_date=datetime.utcnow(),
            user_id=user_id,
            reference_type='ctr',
            reference_id=reference_id,
            action=action,
            action_details=action_details,
            result='success'
        )
        
        self.db.add(log)
