"""
Job Application Service Layer
Business logic for applicant tracking operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple, Dict
from datetime import datetime, date

from backend.shared.database.recruitment_models import (
    JobApplication, ApplicationStatus, ApplicationSource, JobPosting
)
from .schemas import (
    JobApplicationCreate, JobApplicationUpdate, 
    ApplicationStatusEnum, RecruitmentDashboardStats
)


class ApplicationService:
    """Service for job application operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_application_code(self) -> str:
        """Generate unique application code: APP-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(JobApplication.id)).where(
            and_(
                JobApplication.tenant_id == self.tenant_id,
                JobApplication.application_code.like(f"APP-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"APP-{year_month}-{sequence}"
    
    def _build_full_name(self, first_name: str, middle_name: Optional[str], last_name: str) -> str:
        """Build full name"""
        parts = [first_name]
        if middle_name:
            parts.append(middle_name)
        parts.append(last_name)
        return " ".join(parts)
    
    async def create_application(self, data: JobApplicationCreate) -> JobApplication:
        """Create new job application"""
        application_code = await self.generate_application_code()
        full_name = self._build_full_name(data.first_name, data.middle_name, data.last_name)
        
        application = JobApplication(
            tenant_id=self.tenant_id,
            application_code=application_code,
            posting_id=data.posting_id,
            application_date=date.today(),
            source=data.source,
            referrer_employee_id=data.referrer_employee_id,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            full_name=full_name,
            email=data.email,
            mobile=data.mobile,
            alternate_mobile=data.alternate_mobile,
            current_city=data.current_city,
            current_state=data.current_state,
            current_designation=data.current_designation,
            current_employer=data.current_employer,
            total_experience_years=data.total_experience_years,
            relevant_experience_years=data.relevant_experience_years,
            current_ctc=data.current_ctc,
            expected_ctc=data.expected_ctc,
            notice_period_days=data.notice_period_days,
            highest_qualification=data.highest_qualification,
            specialization=data.specialization,
            university=data.university,
            year_of_passing=data.year_of_passing,
            resume_url=data.resume_url,
            cover_letter=data.cover_letter,
            portfolio_url=data.portfolio_url,
            linkedin_url=data.linkedin_url,
            status=ApplicationStatus.NEW,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(application)
        
        # Update posting applications count
        posting_query = select(JobPosting).where(JobPosting.id == data.posting_id)
        posting_result = await self.db.execute(posting_query)
        posting = posting_result.scalar_one_or_none()
        if posting:
            posting.applications_count += 1
        
        await self.db.commit()
        await self.db.refresh(application)
        
        return application
    
    async def get_application(self, application_id: str) -> Optional[JobApplication]:
        """Get application by ID"""
        query = select(JobApplication).where(
            and_(
                JobApplication.id == application_id,
                JobApplication.tenant_id == self.tenant_id,
                JobApplication.is_deleted == False
            )
        ).options(
            selectinload(JobApplication.posting),
            selectinload(JobApplication.assigned_to),
            selectinload(JobApplication.referrer)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_applications(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[ApplicationStatusEnum] = None,
        posting_id: Optional[str] = None,
        source: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> Tuple[List[JobApplication], int]:
        """Get paginated list of applications"""
        query = select(JobApplication).where(
            and_(
                JobApplication.tenant_id == self.tenant_id,
                JobApplication.is_deleted == False
            )
        ).options(
            selectinload(JobApplication.posting),
            selectinload(JobApplication.assigned_to)
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    JobApplication.full_name.ilike(search_term),
                    JobApplication.email.ilike(search_term),
                    JobApplication.mobile.like(search_term),
                    JobApplication.application_code.ilike(search_term)
                )
            )
        
        if status:
            query = query.where(JobApplication.status == status)
        
        if posting_id:
            query = query.where(JobApplication.posting_id == posting_id)
        
        if source:
            query = query.where(JobApplication.source == source)
        
        if assigned_to:
            query = query.where(JobApplication.assigned_to_employee_id == assigned_to)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(desc(JobApplication.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        applications = result.scalars().all()
        
        return applications, total
    
    async def update_application(
        self, application_id: str, data: JobApplicationUpdate
    ) -> JobApplication:
        """Update application"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Application not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)
        
        # Set rejection details if rejecting
        if data.status == ApplicationStatusEnum.REJECTED and not application.rejected_date:
            application.rejected_by_employee_id = self.user_id
            application.rejected_date = date.today()
        
        application.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(application)
        
        return application
    
    async def change_status(
        self, application_id: str, status: ApplicationStatusEnum, notes: Optional[str] = None
    ) -> JobApplication:
        """Change application status"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Application not found")
        
        application.status = status
        if notes:
            application.screening_notes = notes
        application.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(application)
        
        return application
    
    async def shortlist_application(self, application_id: str) -> JobApplication:
        """Shortlist an application"""
        return await self.change_status(application_id, ApplicationStatusEnum.SHORTLISTED)
    
    async def reject_application(self, application_id: str, reason: str) -> JobApplication:
        """Reject an application"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Application not found")
        
        application.status = ApplicationStatusEnum.REJECTED
        application.rejection_reason = reason
        application.rejected_by_employee_id = self.user_id
        application.rejected_date = date.today()
        application.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(application)
        
        return application
    
    async def assign_to_recruiter(
        self, application_id: str, recruiter_id: str
    ) -> JobApplication:
        """Assign application to recruiter"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Application not found")
        
        application.assigned_to_employee_id = recruiter_id
        application.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(application)
        
        return application
    
    async def delete_application(self, application_id: str) -> bool:
        """Soft delete application"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Application not found")
        
        application.is_deleted = True
        application.deleted_at = datetime.utcnow()
        application.deleted_by = self.user_id
        
        await self.db.commit()
        return True
    
    async def get_dashboard_stats(self) -> RecruitmentDashboardStats:
        """Get recruitment dashboard statistics"""
        # Total applications
        total_query = select(func.count(JobApplication.id)).where(
            and_(
                JobApplication.tenant_id == self.tenant_id,
                JobApplication.is_deleted == False
            )
        )
        total_result = await self.db.execute(total_query)
        total_applications = total_result.scalar() or 0
        
        # Applications this month
        first_day = date.today().replace(day=1)
        month_query = select(func.count(JobApplication.id)).where(
            and_(
                JobApplication.tenant_id == self.tenant_id,
                JobApplication.is_deleted == False,
                JobApplication.application_date >= first_day
            )
        )
        month_result = await self.db.execute(month_query)
        applications_this_month = month_result.scalar() or 0
        
        # By status
        status_query = select(
            JobApplication.status,
            func.count(JobApplication.id)
        ).where(
            and_(
                JobApplication.tenant_id == self.tenant_id,
                JobApplication.is_deleted == False
            )
        ).group_by(JobApplication.status)
        
        status_result = await self.db.execute(status_query)
        by_status = {str(row[0]): row[1] for row in status_result}
        
        # By source
        source_query = select(
            JobApplication.source,
            func.count(JobApplication.id)
        ).where(
            and_(
                JobApplication.tenant_id == self.tenant_id,
                JobApplication.is_deleted == False
            )
        ).group_by(JobApplication.source)
        
        source_result = await self.db.execute(source_query)
        by_source = {str(row[0]): row[1] for row in source_result}
        
        return RecruitmentDashboardStats(
            total_applications=total_applications,
            applications_this_month=applications_this_month,
            by_status=by_status,
            by_source=by_source
        )
