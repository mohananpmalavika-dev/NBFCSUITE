"""
STR (Suspicious Transaction Report) Service
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID, uuid4

from backend.shared.database.aml_models import (
    AMLSTRReport,
    AMLAlert,
    ReportStatus,
    AMLAuditLog
)
from backend.services.aml.schemas import (
    STRReportCreate,
    STRReportUpdate,
    STRReportApproval,
    STRFIUSubmission
)


class STRService:
    """Service for Suspicious Transaction Reports (STR)"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def create_str_report(
        self,
        data: STRReportCreate,
        user_id: UUID
    ) -> AMLSTRReport:
        """Create a new STR report"""
        str_number = self._generate_str_number()
        
        str_report = AMLSTRReport(
            id=uuid4(),
            tenant_id=self.tenant_id,
            str_number=str_number,
            report_date=date.today(),
            customer_id=data.customer_id,
            customer_name=data.customer_name,
            customer_type=data.customer_type,
            pan_number=data.pan_number,
            aadhaar_number=data.aadhaar_number,
            passport_number=data.passport_number,
            customer_address=data.customer_address,
            customer_phone=data.customer_phone,
            customer_email=data.customer_email,
            date_of_birth=data.date_of_birth,
            nationality=data.nationality,
            occupation=data.occupation,
            account_numbers=data.account_numbers,
            suspicious_activity_type=data.suspicious_activity_type,
            activity_start_date=data.activity_start_date,
            activity_end_date=data.activity_end_date,
            total_amount_involved=data.total_amount_involved,
            number_of_transactions=data.number_of_transactions,
            suspicious_activity_description=data.suspicious_activity_description,
            reason_for_suspicion=data.reason_for_suspicion,
            transaction_ids=data.transaction_ids,
            alert_ids=data.alert_ids,
            risk_level=data.risk_level,
            risk_indicators=data.risk_indicators,
            investigation_summary=data.investigation_summary,
            supporting_documents=data.supporting_documents,
            related_parties=data.related_parties,
            status=ReportStatus.DRAFT,
            prepared_by=user_id,
            prepared_at=datetime.utcnow(),
            is_confidential=True,
            customer_notified=False,  # Must never be True as per regulations
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(str_report)
        
        # Update related alerts
        if data.alert_ids:
            for alert_id in data.alert_ids:
                alert = self.db.query(AMLAlert).filter(
                    AMLAlert.tenant_id == self.tenant_id,
                    AMLAlert.id == alert_id
                ).first()
                if alert:
                    alert.str_filed = True
                    alert.str_id = str_report.id
        
        # Log creation
        self._log_audit(
            event_type='str_created',
            user_id=user_id,
            reference_id=str(str_report.id),
            action=f"Created STR report {str_number}",
            action_details={
                'str_number': str_number,
                'customer_name': data.customer_name,
                'activity_type': data.suspicious_activity_type,
                'amount_involved': float(data.total_amount_involved)
            }
        )
        
        self.db.commit()
        self.db.refresh(str_report)
        
        return str_report
    
    def get_str_report(self, str_id: UUID) -> Optional[AMLSTRReport]:
        """Get STR report by ID"""
        return self.db.query(AMLSTRReport).filter(
            AMLSTRReport.tenant_id == self.tenant_id,
            AMLSTRReport.id == str_id
        ).first()
    
    def list_str_reports(
        self,
        status: Optional[str] = None,
        customer_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        submitted_to_fiu: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AMLSTRReport]:
        """List STR reports with filters"""
        query = self.db.query(AMLSTRReport).filter(
            AMLSTRReport.tenant_id == self.tenant_id
        )
        
        if status:
            query = query.filter(AMLSTRReport.status == status)
        
        if customer_id:
            query = query.filter(AMLSTRReport.customer_id == customer_id)
        
        if start_date:
            query = query.filter(AMLSTRReport.report_date >= start_date)
        
        if end_date:
            query = query.filter(AMLSTRReport.report_date <= end_date)
        
        if submitted_to_fiu is not None:
            query = query.filter(AMLSTRReport.submitted_to_fiu == submitted_to_fiu)
        
        query = query.order_by(desc(AMLSTRReport.report_date))
        
        return query.offset(skip).limit(limit).all()
    
    def update_str_report(
        self,
        str_id: UUID,
        data: STRReportUpdate,
        user_id: UUID
    ) -> Optional[AMLSTRReport]:
        """Update STR report (only in draft status)"""
        str_report = self.get_str_report(str_id)
        
        if not str_report:
            return None
        
        if str_report.status != ReportStatus.DRAFT:
            raise ValueError("Can only update STR reports in draft status")
        
        if data.suspicious_activity_description:
            str_report.suspicious_activity_description = data.suspicious_activity_description
        
        if data.reason_for_suspicion:
            str_report.reason_for_suspicion = data.reason_for_suspicion
        
        if data.investigation_summary:
            str_report.investigation_summary = data.investigation_summary
        
        if data.supporting_documents:
            str_report.supporting_documents = data.supporting_documents
        
        str_report.updated_by = user_id
        str_report.updated_at = datetime.utcnow()
        
        self._log_audit(
            event_type='str_updated',
            user_id=user_id,
            reference_id=str(str_report.id),
            action=f"Updated STR report {str_report.str_number}"
        )
        
        self.db.commit()
        self.db.refresh(str_report)
        
        return str_report
    
    def submit_for_review(
        self,
        str_id: UUID,
        user_id: UUID
    ) -> Optional[AMLSTRReport]:
        """Submit STR report for review"""
        str_report = self.get_str_report(str_id)
        
        if not str_report:
            return None
        
        str_report.status = ReportStatus.PENDING_REVIEW
        str_report.updated_by = user_id
        str_report.updated_at = datetime.utcnow()
        
        self._log_audit(
            event_type='str_submitted_for_review',
            user_id=user_id,
            reference_id=str(str_report.id),
            action=f"Submitted STR report {str_report.str_number} for review"
        )
        
        self.db.commit()
        self.db.refresh(str_report)
        
        return str_report
    
    def review_str_report(
        self,
        str_id: UUID,
        user_id: UUID
    ) -> Optional[AMLSTRReport]:
        """Review STR report"""
        str_report = self.get_str_report(str_id)
        
        if not str_report:
            return None
        
        str_report.reviewed_by = user_id
        str_report.reviewed_at = datetime.utcnow()
        str_report.updated_by = user_id
        str_report.updated_at = datetime.utcnow()
        
        self._log_audit(
            event_type='str_reviewed',
            user_id=user_id,
            reference_id=str(str_report.id),
            action=f"Reviewed STR report {str_report.str_number}"
        )
        
        self.db.commit()
        self.db.refresh(str_report)
        
        return str_report
    
    def approve_str_report(
        self,
        str_id: UUID,
        approval: STRReportApproval,
        user_id: UUID
    ) -> Optional[AMLSTRReport]:
        """Approve STR report for submission to FIU"""
        str_report = self.get_str_report(str_id)
        
        if not str_report:
            return None
        
        str_report.status = ReportStatus.APPROVED
        str_report.approved_by = user_id
        str_report.approved_at = datetime.utcnow()
        str_report.approval_remarks = approval.approval_remarks
        str_report.updated_by = user_id
        str_report.updated_at = datetime.utcnow()
        
        self._log_audit(
            event_type='str_approved',
            user_id=user_id,
            reference_id=str(str_report.id),
            action=f"Approved STR report {str_report.str_number}",
            action_details={
                'remarks': approval.approval_remarks
            }
        )
        
        self.db.commit()
        self.db.refresh(str_report)
        
        return str_report
    
    def reject_str_report(
        self,
        str_id: UUID,
        reason: str,
        user_id: UUID
    ) -> Optional[AMLSTRReport]:
        """Reject STR report"""
        str_report = self.get_str_report(str_id)
        
        if not str_report:
            return None
        
        str_report.status = ReportStatus.REJECTED
        str_report.approval_remarks = reason
        str_report.updated_by = user_id
        str_report.updated_at = datetime.utcnow()
        
        self._log_audit(
            event_type='str_rejected',
            user_id=user_id,
            reference_id=str(str_report.id),
            action=f"Rejected STR report {str_report.str_number}",
            action_details={
                'reason': reason
            }
        )
        
        self.db.commit()
        self.db.refresh(str_report)
        
        return str_report
    
    def submit_to_fiu(
        self,
        str_id: UUID,
        submission: STRFIUSubmission,
        user_id: UUID
    ) -> Optional[AMLSTRReport]:
        """Submit STR report to FIU-IND"""
        str_report = self.get_str_report(str_id)
        
        if not str_report:
            return None
        
        if str_report.status != ReportStatus.APPROVED:
            raise ValueError("STR report must be approved before submission")
        
        str_report.status = ReportStatus.SUBMITTED
        str_report.submitted_to_fiu = True
        str_report.fiu_submission_date = datetime.utcnow()
        str_report.fiu_reference_number = submission.fiu_reference_number
        str_report.updated_by = user_id
        str_report.updated_at = datetime.utcnow()
        
        self._log_audit(
            event_type='str_submitted_to_fiu',
            user_id=user_id,
            reference_id=str(str_report.id),
            action=f"Submitted STR report {str_report.str_number} to FIU-IND",
            action_details={
                'fiu_reference': submission.fiu_reference_number
            }
        )
        
        self.db.commit()
        self.db.refresh(str_report)
        
        return str_report
    
    def get_str_statistics(self) -> Dict[str, Any]:
        """Get STR statistics"""
        total = self.db.query(AMLSTRReport).filter(
            AMLSTRReport.tenant_id == self.tenant_id
        ).count()
        
        draft = self.db.query(AMLSTRReport).filter(
            AMLSTRReport.tenant_id == self.tenant_id,
            AMLSTRReport.status == ReportStatus.DRAFT
        ).count()
        
        pending = self.db.query(AMLSTRReport).filter(
            AMLSTRReport.tenant_id == self.tenant_id,
            AMLSTRReport.status == ReportStatus.PENDING_REVIEW
        ).count()
        
        approved = self.db.query(AMLSTRReport).filter(
            AMLSTRReport.tenant_id == self.tenant_id,
            AMLSTRReport.status == ReportStatus.APPROVED
        ).count()
        
        submitted = self.db.query(AMLSTRReport).filter(
            AMLSTRReport.tenant_id == self.tenant_id,
            AMLSTRReport.status == ReportStatus.SUBMITTED
        ).count()
        
        total_amount = self.db.query(
            func.sum(AMLSTRReport.total_amount_involved)
        ).filter(
            AMLSTRReport.tenant_id == self.tenant_id
        ).scalar() or Decimal('0')
        
        # STRs by activity type
        by_activity_type = dict(
            self.db.query(
                AMLSTRReport.suspicious_activity_type,
                func.count(AMLSTRReport.id)
            ).filter(
                AMLSTRReport.tenant_id == self.tenant_id
            ).group_by(AMLSTRReport.suspicious_activity_type).all()
        )
        
        return {
            'total_reports': total,
            'draft': draft,
            'pending_review': pending,
            'approved': approved,
            'submitted': submitted,
            'total_amount_involved': total_amount,
            'by_activity_type': by_activity_type
        }
    
    def _generate_str_number(self) -> str:
        """Generate unique STR number"""
        prefix = "STR"
        date_str = datetime.utcnow().strftime("%Y%m%d")
        
        # Get count for today
        count = self.db.query(func.count(AMLSTRReport.id)).filter(
            AMLSTRReport.tenant_id == self.tenant_id,
            func.date(AMLSTRReport.created_at) == date.today()
        ).scalar() or 0
        
        return f"{prefix}{date_str}{count + 1:05d}"
    
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
            reference_type='str',
            reference_id=reference_id,
            action=action,
            action_details=action_details,
            result='success'
        )
        
        self.db.add(log)
