"""
Job Posting Service Layer
Business logic for job posting operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date

from backend.shared.database.recruitment_models import (
    JobPosting, JobRequisition, PostingStatus, PostingChannel
)
from .schemas import (
    JobPostingCreate, JobPostingUpdate, PostingStatusEnum
)


class JobPostingService:
    """Service for job posting operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_posting_code(self) -> str:
        """Generate unique posting code: POST-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(JobPosting.id)).where(
            and_(
                JobPosting.tenant_id == self.tenant_id,
                JobPosting.posting_code.like(f"POST-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"POST-{year_month}-{sequence}"
    
    async def create_posting(self, data: JobPostingCreate) -> JobPosting:
        """Create new job posting from requisition"""
        # Verify requisition exists and is approved
        req_query = select(JobRequisition).where(
            and_(
                JobRequisition.id == data.requisition_id,
                JobRequisition.tenant_id == self.tenant_id,
                JobRequisition.is_deleted == False
            )
        )
        req_result = await self.db.execute(req_query)
        requisition = req_result.scalar_one_or_none()
        
        if not requisition:
            raise ValueError("Requisition not found")
        
        posting_code = await self.generate_posting_code()
        
        posting = JobPosting(
            tenant_id=self.tenant_id,
            posting_code=posting_code,
            requisition_id=data.requisition_id,
            title=data.title,
            job_description=data.job_description,
            responsibilities=data.responsibilities,
            required_qualifications=data.required_qualifications,
            preferred_qualifications=data.preferred_qualifications,
            required_experience_years=data.required_experience_years,
            employment_type=data.employment_type,
            work_location=data.work_location,
            salary_range=data.salary_range,
            benefits=data.benefits,
            application_deadline=data.application_deadline,
            posting_channels=data.posting_channels,
            external_job_board_urls=data.external_job_board_urls,
            is_internal_only=data.is_internal_only,
            is_featured=data.is_featured,
            status=PostingStatus.DRAFT,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(posting)
        await self.db.commit()
        await self.db.refresh(posting)
        
        return posting
    
    async def get_posting(self, posting_id: str) -> Optional[JobPosting]:
        """Get posting by ID"""
        query = select(JobPosting).where(
            and_(
                JobPosting.id == posting_id,
                JobPosting.tenant_id == self.tenant_id,
                JobPosting.is_deleted == False
            )
        ).options(
            selectinload(JobPosting.requisition),
            selectinload(JobPosting.applications)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_postings(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[PostingStatusEnum] = None,
        is_featured: Optional[bool] = None,
        include_expired: bool = False
    ) -> Tuple[List[JobPosting], int]:
        """Get paginated list of postings"""
        query = select(JobPosting).where(
            and_(
                JobPosting.tenant_id == self.tenant_id,
                JobPosting.is_deleted == False
            )
        ).options(
            selectinload(JobPosting.requisition)
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    JobPosting.title.ilike(search_term),
                    JobPosting.posting_code.ilike(search_term)
                )
            )
        
        if status:
            query = query.where(JobPosting.status == status)
        
        if is_featured is not None:
            query = query.where(JobPosting.is_featured == is_featured)
        
        if not include_expired:
            query = query.where(
                or_(
                    JobPosting.application_deadline >= date.today(),
                    JobPosting.application_deadline.is_(None)
                )
            )
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(desc(JobPosting.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        postings = result.scalars().all()
        
        return postings, total
    
    async def get_public_postings(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        employment_type: Optional[str] = None,
        location: Optional[str] = None
    ) -> Tuple[List[JobPosting], int]:
        """Get public job postings (for career page)"""
        query = select(JobPosting).where(
            and_(
                JobPosting.tenant_id == self.tenant_id,
                JobPosting.is_deleted == False,
                JobPosting.status == PostingStatus.PUBLISHED,
                JobPosting.is_internal_only == False,
                or_(
                    JobPosting.application_deadline >= date.today(),
                    JobPosting.application_deadline.is_(None)
                )
            )
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    JobPosting.title.ilike(search_term),
                    JobPosting.job_description.ilike(search_term)
                )
            )
        
        if employment_type:
            query = query.where(JobPosting.employment_type == employment_type)
        
        if location:
            query = query.where(JobPosting.work_location.ilike(f"%{location}%"))
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(
            desc(JobPosting.is_featured),
            desc(JobPosting.published_date)
        )
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        postings = result.scalars().all()
        
        return postings, total
    
    async def update_posting(
        self, posting_id: str, data: JobPostingUpdate
    ) -> JobPosting:
        """Update posting"""
        posting = await self.get_posting(posting_id)
        if not posting:
            raise ValueError("Posting not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(posting, field, value)
        
        posting.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(posting)
        
        return posting
    
    async def publish_posting(self, posting_id: str) -> JobPosting:
        """Publish job posting"""
        posting = await self.get_posting(posting_id)
        if not posting:
            raise ValueError("Posting not found")
        
        if posting.status not in [PostingStatus.DRAFT, PostingStatus.UNPUBLISHED]:
            raise ValueError("Only draft or unpublished postings can be published")
        
        posting.status = PostingStatus.PUBLISHED
        posting.published_date = date.today()
        posting.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(posting)
        
        return posting
    
    async def unpublish_posting(self, posting_id: str) -> JobPosting:
        """Unpublish job posting"""
        posting = await self.get_posting(posting_id)
        if not posting:
            raise ValueError("Posting not found")
        
        if posting.status != PostingStatus.PUBLISHED:
            raise ValueError("Only published postings can be unpublished")
        
        posting.status = PostingStatus.UNPUBLISHED
        posting.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(posting)
        
        return posting
    
    async def close_posting(self, posting_id: str) -> JobPosting:
        """Close job posting"""
        posting = await self.get_posting(posting_id)
        if not posting:
            raise ValueError("Posting not found")
        
        posting.status = PostingStatus.CLOSED
        posting.closed_date = date.today()
        posting.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(posting)
        
        return posting
    
    async def increment_views(self, posting_id: str) -> JobPosting:
        """Increment posting view count"""
        posting = await self.get_posting(posting_id)
        if not posting:
            raise ValueError("Posting not found")
        
        posting.view_count = (posting.view_count or 0) + 1
        
        await self.db.commit()
        await self.db.refresh(posting)
        
        return posting
    
    async def delete_posting(self, posting_id: str) -> bool:
        """Soft delete posting"""
        posting = await self.get_posting(posting_id)
        if not posting:
            raise ValueError("Posting not found")
        
        posting.is_deleted = True
        posting.deleted_at = datetime.utcnow()
        posting.deleted_by = self.user_id
        
        await self.db.commit()
        return True
    
    async def get_posting_statistics(self, posting_id: str) -> dict:
        """Get statistics for a posting"""
        posting = await self.get_posting(posting_id)
        if not posting:
            raise ValueError("Posting not found")
        
        from backend.shared.database.recruitment_models import JobApplication, ApplicationStatus
        
        # Count applications by status
        app_query = select(
            JobApplication.status,
            func.count(JobApplication.id)
        ).where(
            and_(
                JobApplication.posting_id == posting_id,
                JobApplication.tenant_id == self.tenant_id,
                JobApplication.is_deleted == False
            )
        ).group_by(JobApplication.status)
        
        result = await self.db.execute(app_query)
        status_counts = dict(result.all())
        
        return {
            "posting_id": posting_id,
            "posting_code": posting.posting_code,
            "title": posting.title,
            "status": posting.status,
            "views": posting.view_count or 0,
            "total_applications": sum(status_counts.values()),
            "applications_by_status": {
                status.value: count 
                for status, count in status_counts.items()
            },
            "published_date": posting.published_date,
            "application_deadline": posting.application_deadline,
            "days_active": (date.today() - posting.published_date).days if posting.published_date else 0
        }
