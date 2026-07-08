"""
Grievance & Complaint Management - Escalation Service
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .models import (
    Complaint,
    ComplaintEscalation,
    ComplaintStatus,
    EscalationLevel,
)
from .schemas import (
    ComplaintEscalationCreate,
    ComplaintEscalationAcknowledge,
    ComplaintEscalationResolve,
)


class EscalationService:
    """Service class for complaint escalation management"""

    def __init__(self, db: Session):
        self.db = db

    def get_next_escalation_level(self, current_level: EscalationLevel) -> Optional[EscalationLevel]:
        """Get next escalation level in hierarchy"""
        escalation_hierarchy = [
            EscalationLevel.LEVEL_0,
            EscalationLevel.LEVEL_1,
            EscalationLevel.LEVEL_2,
            EscalationLevel.LEVEL_3,
            EscalationLevel.LEVEL_4,
            EscalationLevel.LEVEL_5,
            EscalationLevel.OMBUDSMAN,
        ]
        
        try:
            current_index = escalation_hierarchy.index(current_level)
            if current_index < len(escalation_hierarchy) - 1:
                return escalation_hierarchy[current_index + 1]
        except ValueError:
            pass
        
        return None

    def check_auto_escalation(self, complaint: Complaint) -> tuple[bool, str]:
        """Check if complaint should be auto-escalated based on SLA breach"""
        if not complaint.sla_breach:
            return False, ""
        
        # Check if already at max escalation
        if complaint.escalation_level == EscalationLevel.OMBUDSMAN:
            return False, "Already at maximum escalation level"
        
        # Calculate hours since registration
        hours_elapsed = (datetime.utcnow() - complaint.registered_date).total_seconds() / 3600
        
        # Auto-escalate if SLA breached by more than 24 hours
        if complaint.sla_breach_hours >= 24:
            return True, f"SLA breached by {complaint.sla_breach_hours} hours"
        
        return False, ""

    def create_escalation(
        self,
        escalation_data: ComplaintEscalationCreate,
        created_by: Optional[int] = None
    ) -> ComplaintEscalation:
        """Create a complaint escalation"""
        
        # Get complaint
        complaint = self.db.query(Complaint).filter(
            Complaint.id == escalation_data.complaint_id
        ).first()
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        # Check if complaint can be escalated
        if complaint.status in [ComplaintStatus.CLOSED, ComplaintStatus.RESOLVED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot escalate resolved or closed complaints"
            )
        
        # Get escalation count for this complaint
        escalation_count = self.db.query(ComplaintEscalation).filter(
            ComplaintEscalation.complaint_id == escalation_data.complaint_id
        ).count()
        
        # Determine SLA for escalation (shorter than original)
        escalation_sla_hours = 24  # Default 24 hours for escalated complaints
        if escalation_data.escalation_level == EscalationLevel.OMBUDSMAN:
            escalation_sla_hours = 720  # 30 days for ombudsman
        elif escalation_data.escalation_level in [EscalationLevel.LEVEL_4, EscalationLevel.LEVEL_5]:
            escalation_sla_hours = 12  # 12 hours for executive level
        
        # Create escalation record
        escalation = ComplaintEscalation(
            complaint_id=escalation_data.complaint_id,
            escalation_level=escalation_data.escalation_level,
            escalation_number=escalation_count + 1,
            escalation_reason=escalation_data.escalation_reason,
            reason_details=escalation_data.reason_details,
            is_auto_escalated=escalation_data.is_auto_escalated,
            escalated_from=complaint.assigned_to,
            escalated_to=escalation_data.escalated_to,
            escalated_to_department=escalation_data.escalated_to_department,
            escalation_sla_hours=escalation_sla_hours,
            status="PENDING",
            created_by=created_by,
        )
        
        self.db.add(escalation)
        
        # Update complaint
        complaint.escalation_level = escalation_data.escalation_level
        complaint.status = ComplaintStatus.ESCALATED
        complaint.assigned_to = escalation_data.escalated_to
        complaint.assigned_department = escalation_data.escalated_to_department
        complaint.updated_at = datetime.utcnow()
        
        # If escalated to ombudsman, mark flag
        if escalation_data.escalation_level == EscalationLevel.OMBUDSMAN:
            complaint.escalated_to_ombudsman = True
        
        self.db.commit()
        self.db.refresh(escalation)
        
        return escalation

    def auto_escalate_complaint(
        self,
        complaint_id: int,
        escalated_to: int,
        system_user_id: Optional[int] = None
    ) -> ComplaintEscalation:
        """Auto-escalate a complaint due to SLA breach"""
        
        complaint = self.db.query(Complaint).filter(Complaint.id == complaint_id).first()
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        # Check if should be auto-escalated
        should_escalate, reason = self.check_auto_escalation(complaint)
        
        if not should_escalate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Complaint does not meet auto-escalation criteria. {reason}"
            )
        
        # Get next escalation level
        next_level = self.get_next_escalation_level(complaint.escalation_level)
        
        if not next_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No higher escalation level available"
            )
        
        # Create escalation
        escalation_data = ComplaintEscalationCreate(
            complaint_id=complaint_id,
            escalation_level=next_level,
            escalation_reason="SLA_BREACH",
            reason_details=reason,
            is_auto_escalated=True,
            escalated_to=escalated_to,
        )
        
        return self.create_escalation(escalation_data, created_by=system_user_id)

    def acknowledge_escalation(
        self,
        escalation_id: int,
        acknowledgement_data: ComplaintEscalationAcknowledge,
        acknowledged_by: Optional[int] = None
    ) -> ComplaintEscalation:
        """Acknowledge an escalation"""
        
        escalation = self.db.query(ComplaintEscalation).filter(
            ComplaintEscalation.id == escalation_id
        ).first()
        
        if not escalation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Escalation not found"
            )
        
        if escalation.acknowledged_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Escalation already acknowledged"
            )
        
        escalation.acknowledged_at = datetime.utcnow()
        escalation.status = "ACKNOWLEDGED"
        escalation.resolution_notes = acknowledgement_data.acknowledgement_notes
        
        self.db.commit()
        self.db.refresh(escalation)
        
        return escalation

    def resolve_escalation(
        self,
        escalation_id: int,
        resolution_data: ComplaintEscalationResolve,
        resolved_by: Optional[int] = None
    ) -> ComplaintEscalation:
        """Resolve an escalation"""
        
        escalation = self.db.query(ComplaintEscalation).filter(
            ComplaintEscalation.id == escalation_id
        ).first()
        
        if not escalation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Escalation not found"
            )
        
        if escalation.status == "RESOLVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Escalation already resolved"
            )
        
        resolved_at = datetime.utcnow()
        escalation.resolved_at = resolved_at
        escalation.status = "RESOLVED"
        escalation.resolution_notes = resolution_data.resolution_notes
        escalation.action_taken = resolution_data.action_taken
        
        # Check if escalation SLA breached
        escalation_duration = (resolved_at - escalation.escalated_at).total_seconds() / 3600
        if escalation_duration > escalation.escalation_sla_hours:
            escalation.escalation_sla_breach = True
        
        self.db.commit()
        self.db.refresh(escalation)
        
        return escalation

    def get_escalation(self, escalation_id: int) -> Optional[ComplaintEscalation]:
        """Get escalation by ID"""
        return self.db.query(ComplaintEscalation).filter(
            ComplaintEscalation.id == escalation_id
        ).first()

    def list_escalations(
        self,
        complaint_id: Optional[int] = None,
        escalation_level: Optional[EscalationLevel] = None,
        escalated_to: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ComplaintEscalation], int]:
        """List escalations with filters"""
        
        query = self.db.query(ComplaintEscalation)
        
        if complaint_id:
            query = query.filter(ComplaintEscalation.complaint_id == complaint_id)
        
        if escalation_level:
            query = query.filter(ComplaintEscalation.escalation_level == escalation_level)
        
        if escalated_to:
            query = query.filter(ComplaintEscalation.escalated_to == escalated_to)
        
        if status:
            query = query.filter(ComplaintEscalation.status == status)
        
        total = query.count()
        escalations = query.order_by(
            ComplaintEscalation.escalated_at.desc()
        ).offset(skip).limit(limit).all()
        
        return escalations, total

    def get_pending_escalations(
        self,
        user_id: Optional[int] = None
    ) -> List[ComplaintEscalation]:
        """Get pending escalations for a user"""
        
        query = self.db.query(ComplaintEscalation).filter(
            ComplaintEscalation.status == "PENDING"
        )
        
        if user_id:
            query = query.filter(ComplaintEscalation.escalated_to == user_id)
        
        return query.order_by(ComplaintEscalation.escalated_at.asc()).all()

    def get_sla_breach_escalations(self) -> List[ComplaintEscalation]:
        """Get escalations that have breached SLA"""
        
        current_time = datetime.utcnow()
        
        escalations = self.db.query(ComplaintEscalation).filter(
            ComplaintEscalation.status.in_(["PENDING", "ACKNOWLEDGED"]),
            ComplaintEscalation.resolved_at.is_(None)
        ).all()
        
        breached = []
        for escalation in escalations:
            hours_elapsed = (current_time - escalation.escalated_at).total_seconds() / 3600
            if hours_elapsed > escalation.escalation_sla_hours:
                breached.append(escalation)
        
        return breached

    def delete_escalation(self, escalation_id: int) -> bool:
        """Delete an escalation (only if pending)"""
        
        escalation = self.get_escalation(escalation_id)
        
        if not escalation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Escalation not found"
            )
        
        if escalation.status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only delete pending escalations"
            )
        
        self.db.delete(escalation)
        self.db.commit()
        
        return True
