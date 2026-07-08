"""
Grievance & Complaint Management - Ombudsman Service
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .models import Complaint, OmbudsmanCase, OmbudsmanStatus, ComplaintStatus
from .schemas import (
    OmbudsmanCaseCreate,
    OmbudsmanCaseUpdate,
    OmbudsmanCaseSubmit,
    OmbudsmanCaseHearing,
    OmbudsmanCaseAward,
)


class OmbudsmanService:
    """Service class for ombudsman case management"""

    def __init__(self, db: Session):
        self.db = db

    def create_ombudsman_case(
        self,
        case_data: OmbudsmanCaseCreate,
        created_by: Optional[int] = None
    ) -> OmbudsmanCase:
        """Create a new ombudsman case"""
        
        # Check if complaint exists
        complaint = self.db.query(Complaint).filter(
            Complaint.id == case_data.complaint_id
        ).first()
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found"
            )
        
        # Check if ombudsman case already exists for this complaint
        existing_case = self.db.query(OmbudsmanCase).filter(
            OmbudsmanCase.complaint_id == case_data.complaint_id
        ).first()
        
        if existing_case:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ombudsman case already exists for this complaint"
            )
        
        # Create ombudsman case
        ombudsman_case = OmbudsmanCase(
            **case_data.model_dump(),
            status=OmbudsmanStatus.PENDING,
            created_by=created_by,
        )
        
        self.db.add(ombudsman_case)
        
        # Update complaint
        complaint.escalated_to_ombudsman = True
        complaint.status = ComplaintStatus.ESCALATED
        
        self.db.commit()
        self.db.refresh(ombudsman_case)
        
        return ombudsman_case

    def get_ombudsman_case(self, case_id: int) -> Optional[OmbudsmanCase]:
        """Get ombudsman case by ID"""
        return self.db.query(OmbudsmanCase).filter(
            OmbudsmanCase.id == case_id
        ).first()

    def get_ombudsman_case_by_complaint(self, complaint_id: int) -> Optional[OmbudsmanCase]:
        """Get ombudsman case by complaint ID"""
        return self.db.query(OmbudsmanCase).filter(
            OmbudsmanCase.complaint_id == complaint_id
        ).first()

    def list_ombudsman_cases(
        self,
        status: Optional[OmbudsmanStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[OmbudsmanCase], int]:
        """List ombudsman cases with filters"""
        
        query = self.db.query(OmbudsmanCase)
        
        if status:
            query = query.filter(OmbudsmanCase.status == status)
        
        total = query.count()
        cases = query.order_by(
            OmbudsmanCase.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return cases, total

    def update_ombudsman_case(
        self,
        case_id: int,
        case_data: OmbudsmanCaseUpdate,
        updated_by: Optional[int] = None
    ) -> OmbudsmanCase:
        """Update ombudsman case"""
        
        ombudsman_case = self.get_ombudsman_case(case_id)
        
        if not ombudsman_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ombudsman case not found"
            )
        
        # Update fields
        update_data = case_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ombudsman_case, field, value)
        
        ombudsman_case.updated_by = updated_by
        ombudsman_case.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ombudsman_case)
        
        return ombudsman_case

    def submit_to_ombudsman(
        self,
        case_id: int,
        submission_data: OmbudsmanCaseSubmit,
        submitted_by: Optional[int] = None
    ) -> OmbudsmanCase:
        """Submit case to ombudsman"""
        
        ombudsman_case = self.get_ombudsman_case(case_id)
        
        if not ombudsman_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ombudsman case not found"
            )
        
        if ombudsman_case.status != OmbudsmanStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case already submitted"
            )
        
        ombudsman_case.submitted_date = submission_data.submitted_date
        ombudsman_case.submission_reference = submission_data.submission_reference
        ombudsman_case.status = OmbudsmanStatus.SUBMITTED
        ombudsman_case.updated_by = submitted_by
        ombudsman_case.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ombudsman_case)
        
        return ombudsman_case

    def schedule_hearing(
        self,
        case_id: int,
        hearing_data: OmbudsmanCaseHearing,
        scheduled_by: Optional[int] = None
    ) -> OmbudsmanCase:
        """Schedule ombudsman hearing"""
        
        ombudsman_case = self.get_ombudsman_case(case_id)
        
        if not ombudsman_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ombudsman case not found"
            )
        
        ombudsman_case.hearing_date = hearing_data.hearing_date
        ombudsman_case.bank_representative = hearing_data.bank_representative
        ombudsman_case.status = OmbudsmanStatus.HEARING_SCHEDULED
        ombudsman_case.updated_by = scheduled_by
        ombudsman_case.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ombudsman_case)
        
        return ombudsman_case

    def record_award(
        self,
        case_id: int,
        award_data: OmbudsmanCaseAward,
        recorded_by: Optional[int] = None
    ) -> OmbudsmanCase:
        """Record ombudsman award"""
        
        ombudsman_case = self.get_ombudsman_case(case_id)
        
        if not ombudsman_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ombudsman case not found"
            )
        
        ombudsman_case.award_date = award_data.award_date
        ombudsman_case.award_details = award_data.award_details
        ombudsman_case.compensation_awarded = award_data.compensation_awarded
        ombudsman_case.status = OmbudsmanStatus.AWARD_ISSUED
        ombudsman_case.updated_by = recorded_by
        ombudsman_case.updated_at = datetime.utcnow()
        
        # Check if resolved within 30 days
        if ombudsman_case.submitted_date:
            days_taken = (ombudsman_case.award_date - ombudsman_case.submitted_date).days
            ombudsman_case.resolution_within_30_days = days_taken <= 30
        
        self.db.commit()
        self.db.refresh(ombudsman_case)
        
        return ombudsman_case

    def close_case(
        self,
        case_id: int,
        closed_by: Optional[int] = None
    ) -> OmbudsmanCase:
        """Close ombudsman case"""
        
        ombudsman_case = self.get_ombudsman_case(case_id)
        
        if not ombudsman_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ombudsman case not found"
            )
        
        ombudsman_case.closure_date = datetime.utcnow()
        ombudsman_case.status = OmbudsmanStatus.CLOSED
        ombudsman_case.updated_by = closed_by
        ombudsman_case.updated_at = datetime.utcnow()
        
        # Update related complaint
        complaint = self.db.query(Complaint).filter(
            Complaint.id == ombudsman_case.complaint_id
        ).first()
        
        if complaint:
            complaint.status = ComplaintStatus.CLOSED
            complaint.closed_date = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ombudsman_case)
        
        return ombudsman_case

    def delete_ombudsman_case(self, case_id: int) -> bool:
        """Delete ombudsman case (only if pending)"""
        
        ombudsman_case = self.get_ombudsman_case(case_id)
        
        if not ombudsman_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ombudsman case not found"
            )
        
        if ombudsman_case.status != OmbudsmanStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only delete pending ombudsman cases"
            )
        
        self.db.delete(ombudsman_case)
        self.db.commit()
        
        return True
