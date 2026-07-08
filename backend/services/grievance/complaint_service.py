"""
Grievance & Complaint Management - Complaint Service
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status

from .models import (
    Complaint,
    ComplaintChannel,
    ComplaintStatus,
    ComplaintPriority,
    ComplaintCategory,
    ChannelType,
    EscalationLevel,
)
from .schemas import (
    ComplaintCreate,
    ComplaintUpdate,
    ComplaintAssign,
    ComplaintAcknowledge,
    ComplaintResolve,
    ComplaintClose,
    ComplaintReopen,
    ComplaintResponse,
    ComplaintFilter,
    ComplaintStatistics,
)


class ComplaintService:
    """Service class for complaint management operations"""

    def __init__(self, db: Session):
        self.db = db

    def generate_complaint_number(self) -> str:
        """Generate unique complaint number"""
        # Format: CMP-YYYYMMDD-XXXX
        today = datetime.now().strftime("%Y%m%d")
        
        # Get count of complaints created today
        count = self.db.query(Complaint).filter(
            func.date(Complaint.registered_date) == datetime.now().date()
        ).count()
        
        return f"CMP-{today}-{count + 1:04d}"

    def calculate_sla_hours(
        self,
        category: ComplaintCategory,
        priority: ComplaintPriority,
        channel: ChannelType
    ) -> int:
        """Calculate SLA hours based on complaint attributes"""
        # Base SLA mapping
        priority_hours = {
            ComplaintPriority.CRITICAL: 4,
            ComplaintPriority.URGENT: 12,
            ComplaintPriority.HIGH: 24,
            ComplaintPriority.MEDIUM: 48,
            ComplaintPriority.LOW: 72,
        }
        
        # Regulatory complaints have stricter SLA (30 days = 720 hours)
        regulatory_categories = [ComplaintCategory.REGULATORY, ComplaintCategory.FRAUD_SECURITY]
        if category in regulatory_categories:
            return 720  # 30 days as per RBI guidelines
        
        return priority_hours.get(priority, 48)

    def calculate_target_resolution_date(self, registered_date: datetime, sla_hours: int) -> datetime:
        """Calculate target resolution date excluding weekends"""
        target_date = registered_date + timedelta(hours=sla_hours)
        return target_date

    def check_sla_breach(self, complaint: Complaint) -> tuple[bool, int]:
        """Check if SLA is breached and calculate breach hours"""
        if complaint.status in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
            # Already resolved
            if complaint.actual_resolution_date and complaint.target_resolution_date:
                if complaint.actual_resolution_date > complaint.target_resolution_date:
                    breach_delta = complaint.actual_resolution_date - complaint.target_resolution_date
                    return True, int(breach_delta.total_seconds() / 3600)
            return False, 0
        
        # Still open - check current time
        current_time = datetime.utcnow()
        if complaint.target_resolution_date and current_time > complaint.target_resolution_date:
            breach_delta = current_time - complaint.target_resolution_date
            return True, int(breach_delta.total_seconds() / 3600)
        
        return False, 0

    def create_complaint(
        self,
        complaint_data: ComplaintCreate,
        created_by: Optional[int] = None
    ) -> Complaint:
        """Register a new complaint"""
        
        # Generate complaint number
        complaint_number = self.generate_complaint_number()
        
        # Calculate SLA
        sla_hours = self.calculate_sla_hours(
            complaint_data.category,
            complaint_data.priority,
            complaint_data.channel
        )
        
        registered_date = datetime.utcnow()
        target_resolution_date = self.calculate_target_resolution_date(registered_date, sla_hours)
        
        # Check if this is a repeat complaint
        is_repeat = False
        if complaint_data.customer_id:
            previous_complaints = self.db.query(Complaint).filter(
                Complaint.customer_id == complaint_data.customer_id,
                Complaint.category == complaint_data.category,
                Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])
            ).count()
            is_repeat = previous_complaints > 0
        
        # Determine if regulatory
        is_regulatory = complaint_data.category in [
            ComplaintCategory.REGULATORY,
            ComplaintCategory.FRAUD_SECURITY,
            ComplaintCategory.COLLECTION_HARASSMENT
        ]
        
        # Create complaint
        complaint = Complaint(
            complaint_number=complaint_number,
            **complaint_data.model_dump(),
            status=ComplaintStatus.REGISTERED,
            registered_date=registered_date,
            target_resolution_date=target_resolution_date,
            sla_hours=sla_hours,
            sla_breach=False,
            sla_breach_hours=0,
            is_repeat=is_repeat,
            is_regulatory=is_regulatory,
            escalation_level=EscalationLevel.LEVEL_0,
            created_by=created_by,
            updated_by=created_by,
        )
        
        self.db.add(complaint)
        self.db.commit()
        self.db.refresh(complaint)
        
        # Log initial channel communication
        self._log_channel_communication(
            complaint_id=complaint.id,
            channel_type=complaint_data.channel,
            direction="INBOUND",
            message=complaint_data.description,
            from_address=complaint_data.source_reference,
            is_customer_initiated=True
        )
        
        return complaint

    def get_complaint(self, complaint_id: int) -> Optional[Complaint]:
        """Get complaint by ID"""
        complaint = self.db.query(Complaint).filter(Complaint.id == complaint_id).first()
        
        if complaint:
            # Update SLA breach status
            is_breach, breach_hours = self.check_sla_breach(complaint)
            if is_breach != complaint.sla_breach:
                complaint.sla_breach = is_breach
                complaint.sla_breach_hours = breach_hours
                self.db.commit()
        
        return complaint

    def get_complaint_by_number(self, complaint_number: str) -> Optional[Complaint]:
        """Get complaint by complaint number"""
        return self.db.query(Complaint).filter(
            Complaint.complaint_number == complaint_number
        ).first()

    def list_complaints(self, filters: ComplaintFilter) -> tuple[List[Complaint], int]:
        """List complaints with filters and pagination"""
        query = self.db.query(Complaint)
        
        # Apply filters
        if filters.status:
            query = query.filter(Complaint.status == filters.status)
        
        if filters.priority:
            query = query.filter(Complaint.priority == filters.priority)
        
        if filters.category:
            query = query.filter(Complaint.category == filters.category)
        
        if filters.channel:
            query = query.filter(Complaint.channel == filters.channel)
        
        if filters.assigned_to:
            query = query.filter(Complaint.assigned_to == filters.assigned_to)
        
        if filters.customer_id:
            query = query.filter(Complaint.customer_id == filters.customer_id)
        
        if filters.escalation_level:
            query = query.filter(Complaint.escalation_level == filters.escalation_level)
        
        if filters.sla_breach is not None:
            query = query.filter(Complaint.sla_breach == filters.sla_breach)
        
        if filters.is_regulatory is not None:
            query = query.filter(Complaint.is_regulatory == filters.is_regulatory)
        
        if filters.date_from:
            query = query.filter(Complaint.registered_date >= filters.date_from)
        
        if filters.date_to:
            query = query.filter(Complaint.registered_date <= filters.date_to)
        
        if filters.search_text:
            search_pattern = f"%{filters.search_text}%"
            query = query.filter(
                or_(
                    Complaint.complaint_number.ilike(search_pattern),
                    Complaint.subject.ilike(search_pattern),
                    Complaint.description.ilike(search_pattern),
                    Complaint.customer_name.ilike(search_pattern),
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        complaints = query.order_by(Complaint.registered_date.desc()).offset(filters.skip).limit(filters.limit).all()
        
        return complaints, total

    def update_complaint(
        self,
        complaint_id: int,
        complaint_data: ComplaintUpdate,
        updated_by: Optional[int] = None
    ) -> Complaint:
        """Update complaint details"""
        complaint = self.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        # Update fields
        update_data = complaint_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(complaint, field, value)
        
        complaint.updated_by = updated_by
        complaint.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(complaint)
        
        return complaint

    def assign_complaint(
        self,
        complaint_id: int,
        assignment_data: ComplaintAssign,
        assigned_by: Optional[int] = None
    ) -> Complaint:
        """Assign complaint to user/department"""
        complaint = self.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        if complaint.status == ComplaintStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign closed complaint"
            )
        
        complaint.assigned_to = assignment_data.assigned_to
        complaint.assigned_department = assignment_data.assigned_department
        complaint.assigned_at = datetime.utcnow()
        complaint.updated_by = assigned_by
        complaint.updated_at = datetime.utcnow()
        
        # Change status to IN_PROGRESS if still REGISTERED
        if complaint.status == ComplaintStatus.REGISTERED:
            complaint.status = ComplaintStatus.IN_PROGRESS
        
        self.db.commit()
        self.db.refresh(complaint)
        
        return complaint

    def acknowledge_complaint(
        self,
        complaint_id: int,
        acknowledgement_data: ComplaintAcknowledge,
        acknowledged_by: Optional[int] = None
    ) -> Complaint:
        """Acknowledge receipt of complaint"""
        complaint = self.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        if complaint.acknowledged_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Complaint already acknowledged"
            )
        
        complaint.acknowledged_date = datetime.utcnow()
        complaint.status = ComplaintStatus.ACKNOWLEDGED
        complaint.updated_by = acknowledged_by
        complaint.updated_at = datetime.utcnow()
        
        # Log acknowledgement communication
        self._log_channel_communication(
            complaint_id=complaint.id,
            channel_type=complaint.channel,
            direction="OUTBOUND",
            message=acknowledgement_data.acknowledgement_message,
            to_address=complaint.customer_email or complaint.customer_phone,
            is_customer_initiated=False,
            response_sent=True
        )
        
        self.db.commit()
        self.db.refresh(complaint)
        
        return complaint

    def resolve_complaint(
        self,
        complaint_id: int,
        resolution_data: ComplaintResolve,
        resolved_by: Optional[int] = None
    ) -> Complaint:
        """Resolve a complaint"""
        complaint = self.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        if complaint.status in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Complaint already {complaint.status.value.lower()}"
            )
        
        resolution_date = datetime.utcnow()
        complaint.resolution = resolution_data.resolution
        complaint.resolution_remarks = resolution_data.resolution_remarks
        complaint.compensation_amount = resolution_data.compensation_amount
        complaint.actual_resolution_date = resolution_date
        complaint.status = ComplaintStatus.RESOLVED
        complaint.updated_by = resolved_by
        complaint.updated_at = resolution_date
        
        # Update SLA breach
        is_breach, breach_hours = self.check_sla_breach(complaint)
        complaint.sla_breach = is_breach
        complaint.sla_breach_hours = breach_hours
        
        self.db.commit()
        self.db.refresh(complaint)
        
        return complaint

    def close_complaint(
        self,
        complaint_id: int,
        closure_data: ComplaintClose,
        closed_by: Optional[int] = None
    ) -> Complaint:
        """Close a resolved complaint"""
        complaint = self.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        if complaint.status != ComplaintStatus.RESOLVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only close resolved complaints"
            )
        
        complaint.closed_date = datetime.utcnow()
        complaint.status = ComplaintStatus.CLOSED
        complaint.customer_satisfaction = closure_data.customer_satisfaction
        complaint.updated_by = closed_by
        complaint.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(complaint)
        
        return complaint

    def reopen_complaint(
        self,
        complaint_id: int,
        reopen_data: ComplaintReopen,
        reopened_by: Optional[int] = None
    ) -> Complaint:
        """Reopen a closed complaint"""
        complaint = self.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        if complaint.status not in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only reopen resolved or closed complaints"
            )
        
        # Reset dates and status
        complaint.status = ComplaintStatus.REOPENED
        complaint.actual_resolution_date = None
        complaint.closed_date = None
        complaint.resolution = None
        complaint.resolution_remarks = reopen_data.reopen_reason
        complaint.updated_by = reopened_by
        complaint.updated_at = datetime.utcnow()
        
        # Extend SLA
        complaint.target_resolution_date = self.calculate_target_resolution_date(
            datetime.utcnow(),
            complaint.sla_hours
        )
        
        self.db.commit()
        self.db.refresh(complaint)
        
        return complaint

    def delete_complaint(self, complaint_id: int) -> bool:
        """Delete a complaint (soft delete by marking as deleted)"""
        complaint = self.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        # Only allow deletion of REGISTERED complaints
        if complaint.status != ComplaintStatus.REGISTERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only delete newly registered complaints"
            )
        
        self.db.delete(complaint)
        self.db.commit()
        
        return True

    def get_statistics(self, filters: Optional[ComplaintFilter] = None) -> ComplaintStatistics:
        """Get complaint statistics for dashboard"""
        query = self.db.query(Complaint)
        
        # Apply date filters if provided
        if filters and filters.date_from:
            query = query.filter(Complaint.registered_date >= filters.date_from)
        if filters and filters.date_to:
            query = query.filter(Complaint.registered_date <= filters.date_to)
        
        total_complaints = query.count()
        
        # Status breakdown
        registered = query.filter(Complaint.status == ComplaintStatus.REGISTERED).count()
        in_progress = query.filter(Complaint.status == ComplaintStatus.IN_PROGRESS).count()
        resolved = query.filter(Complaint.status == ComplaintStatus.RESOLVED).count()
        closed = query.filter(Complaint.status == ComplaintStatus.CLOSED).count()
        escalated = query.filter(Complaint.status == ComplaintStatus.ESCALATED).count()
        
        # SLA tracking
        sla_breached = query.filter(Complaint.sla_breach == True).count()
        within_sla = total_complaints - sla_breached
        
        # Group by priority
        by_priority = {}
        for priority in ComplaintPriority:
            count = query.filter(Complaint.priority == priority).count()
            by_priority[priority.value] = count
        
        # Group by category
        by_category = {}
        for category in ComplaintCategory:
            count = query.filter(Complaint.category == category).count()
            by_category[category.value] = count
        
        # Group by channel
        by_channel = {}
        for channel in ChannelType:
            count = query.filter(Complaint.channel == channel).count()
            by_channel[channel.value] = count
        
        # Calculate average resolution time
        resolved_complaints = query.filter(
            Complaint.actual_resolution_date.isnot(None)
        ).all()
        
        if resolved_complaints:
            total_hours = sum([
                (c.actual_resolution_date - c.registered_date).total_seconds() / 3600
                for c in resolved_complaints
            ])
            avg_resolution_hours = total_hours / len(resolved_complaints)
        else:
            avg_resolution_hours = 0
        
        # Customer satisfaction
        satisfied_complaints = query.filter(
            Complaint.customer_satisfaction.isnot(None)
        ).all()
        
        if satisfied_complaints:
            avg_satisfaction = sum([c.customer_satisfaction for c in satisfied_complaints]) / len(satisfied_complaints)
        else:
            avg_satisfaction = 0
        
        # Escalation and ombudsman
        escalation_rate = (escalated / total_complaints * 100) if total_complaints > 0 else 0
        ombudsman_cases = query.filter(Complaint.escalated_to_ombudsman == True).count()
        
        return ComplaintStatistics(
            total_complaints=total_complaints,
            registered=registered,
            in_progress=in_progress,
            resolved=resolved,
            closed=closed,
            escalated=escalated,
            sla_breached=sla_breached,
            within_sla=within_sla,
            by_priority=by_priority,
            by_category=by_category,
            by_channel=by_channel,
            avg_resolution_hours=avg_resolution_hours,
            customer_satisfaction_avg=avg_satisfaction,
            escalation_rate=escalation_rate,
            ombudsman_cases=ombudsman_cases,
        )

    def _log_channel_communication(
        self,
        complaint_id: int,
        channel_type: ChannelType,
        direction: str,
        message: str,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
        is_customer_initiated: bool = True,
        response_sent: bool = False
    ):
        """Internal method to log channel communications"""
        channel_log = ComplaintChannel(
            complaint_id=complaint_id,
            channel_type=channel_type,
            direction=direction,
            message=message,
            from_address=from_address,
            to_address=to_address,
            is_customer_initiated=is_customer_initiated,
            response_sent=response_sent,
        )
        self.db.add(channel_log)
        # Note: Commit is done by caller
