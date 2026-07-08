"""
Interview Service Layer
Business logic for interview scheduling operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date

from backend.shared.database.recruitment_models import (
    Interview, InterviewStatus, InterviewResult, JobApplication
)
from .schemas import (
    InterviewCreate, InterviewUpdate, InterviewFeedback,
    InterviewStatusEnum
)


class InterviewService:
    """Service for interview operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_interview_code(self) -> str:
        """Generate unique interview code: INT-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(Interview.id)).where(
            and_(
                Interview.tenant_id == self.tenant_id,
                Interview.interview_code.like(f"INT-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"INT-{year_month}-{sequence}"
    
    async def create_interview(self, data: InterviewCreate) -> Interview:
        """Create new interview"""
        interview_code = await self.generate_interview_code()
        
        interview = Interview(
            tenant_id=self.tenant_id,
            interview_code=interview_code,
            application_id=data.application_id,
            interview_type=data.interview_type,
            round_number=data.round_number,
            scheduled_date=data.scheduled_date,
            duration_minutes=data.duration_minutes,
            location=data.location,
            meeting_link=data.meeting_link,
            interviewer_employee_ids=data.interviewer_employee_ids,
            panel_lead_employee_id=data.panel_lead_employee_id,
            status=InterviewStatus.SCHEDULED,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(interview)
        
        # Update application status
        app_query = select(JobApplication).where(JobApplication.id == data.application_id)
        app_result = await self.db.execute(app_query)
        application = app_result.scalar_one_or_none()
        if application:
            application.status = "interview_scheduled"
        
        await self.db.commit()
        await self.db.refresh(interview)
        
        return interview
    
    async def get_interview(self, interview_id: str) -> Optional[Interview]:
        """Get interview by ID"""
        query = select(Interview).where(
            and_(
                Interview.id == interview_id,
                Interview.tenant_id == self.tenant_id,
                Interview.is_deleted == False
            )
        ).options(
            selectinload(Interview.application),
            selectinload(Interview.panel_lead)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_interviews(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[InterviewStatusEnum] = None,
        interview_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        panel_lead_id: Optional[str] = None
    ) -> Tuple[List[Interview], int]:
        """Get paginated list of interviews"""
        query = select(Interview).where(
            and_(
                Interview.tenant_id == self.tenant_id,
                Interview.is_deleted == False
            )
        ).options(
            selectinload(Interview.application),
            selectinload(Interview.panel_lead)
        )
        
        if status:
            query = query.where(Interview.status == status)
        
        if interview_type:
            query = query.where(Interview.interview_type == interview_type)
        
        if from_date:
            query = query.where(Interview.scheduled_date >= from_date)
        
        if to_date:
            query = query.where(Interview.scheduled_date <= to_date)
        
        if panel_lead_id:
            query = query.where(Interview.panel_lead_employee_id == panel_lead_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(Interview.scheduled_date)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        interviews = result.scalars().all()
        
        return interviews, total
    
    async def update_interview(
        self, interview_id: str, data: InterviewUpdate
    ) -> Interview:
        """Update interview"""
        interview = await self.get_interview(interview_id)
        if not interview:
            raise ValueError("Interview not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(interview, field, value)
        
        interview.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(interview)
        
        return interview
    
    async def reschedule_interview(
        self, interview_id: str, new_date: datetime, reason: Optional[str] = None
    ) -> Interview:
        """Reschedule interview"""
        interview = await self.get_interview(interview_id)
        if not interview:
            raise ValueError("Interview not found")
        
        if not interview.original_scheduled_date:
            interview.original_scheduled_date = interview.scheduled_date
        
        interview.scheduled_date = new_date
        interview.status = InterviewStatus.RESCHEDULED
        interview.reschedule_count += 1
        interview.reschedule_reason = reason
        interview.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(interview)
        
        return interview
    
    async def submit_feedback(
        self, interview_id: str, feedback: InterviewFeedback
    ) -> Interview:
        """Submit interview feedback"""
        interview = await self.get_interview(interview_id)
        if not interview:
            raise ValueError("Interview not found")
        
        interview.feedback = feedback.feedback
        interview.technical_rating = feedback.technical_rating
        interview.communication_rating = feedback.communication_rating
        interview.cultural_fit_rating = feedback.cultural_fit_rating
        interview.overall_rating = feedback.overall_rating
        interview.result = feedback.result
        interview.result_notes = feedback.result_notes
        interview.status = InterviewStatus.COMPLETED
        interview.completed_date = datetime.utcnow()
        interview.updated_by = self.user_id
        
        # Update application status based on result
        app_query = select(JobApplication).where(Interview.application_id == interview.application_id)
        app_result = await self.db.execute(app_query)
        application = app_result.scalar_one_or_none()
        if application:
            if feedback.result == InterviewResultEnum.SELECTED:
                application.status = "interviewed"
            elif feedback.result == InterviewResultEnum.REJECTED:
                application.status = "rejected"
        
        await self.db.commit()
        await self.db.refresh(interview)
        
        return interview
    
    async def cancel_interview(
        self, interview_id: str, reason: Optional[str] = None
    ) -> Interview:
        """Cancel interview"""
        interview = await self.get_interview(interview_id)
        if not interview:
            raise ValueError("Interview not found")
        
        interview.status = InterviewStatus.CANCELLED
        interview.result_notes = reason
        interview.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(interview)
        
        return interview
    
    async def mark_no_show(self, interview_id: str) -> Interview:
        """Mark interview as no show"""
        interview = await self.get_interview(interview_id)
        if not interview:
            raise ValueError("Interview not found")
        
        interview.status = InterviewStatus.NO_SHOW
        interview.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(interview)
        
        return interview
