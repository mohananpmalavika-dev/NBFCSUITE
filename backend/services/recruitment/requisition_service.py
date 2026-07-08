"""
Job Requisition Service Layer
Business logic for job requisition operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date

from backend.shared.database.recruitment_models import (
    JobRequisition, RequisitionStatus, RequisitionPriority
)
from .schemas import (
    JobRequisitionCreate, JobRequisitionUpdate, 
    RequisitionStatusEnum, JobRequisitionApproval
)


class RequisitionService:
    """Service for job requisition operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_requisition_code(self) -> str:
        """Generate unique requisition code: REQ-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(JobRequisition.id)).where(
            and_(
                JobRequisition.tenant_id == self.tenant_id,
                JobRequisition.requisition_code.like(f"REQ-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"REQ-{year_month}-{sequence}"
    
    async def create_requisition(self, data: JobRequisitionCreate) -> JobRequisition:
        """Create new job requisition"""
        requisition_code = await self.generate_requisition_code()
        
        requisition = JobRequisition(
            tenant_id=self.tenant_id,
            requisition_code=requisition_code,
            title=data.title,
            department_id=data.department_id,
            designation_id=data.designation_id,
            number_of_positions=data.number_of_positions,
            employment_type=data.employment_type,
            work_location=data.work_location,
            reporting_to_employee_id=data.reporting_to_employee_id,
            job_description=data.job_description,
            responsibilities=data.responsibilities,
            required_qualifications=data.required_qualifications,
            preferred_qualifications=data.preferred_qualifications,
            required_experience_years=data.required_experience_years,
            min_salary=data.min_salary,
            max_salary=data.max_salary,
            priority=data.priority,
            required_by_date=data.required_by_date,
            justification=data.justification,
            is_replacement=data.is_replacement,
            replacement_for_employee_id=data.replacement_for_employee_id,
            requested_by_employee_id=data.requested_by_employee_id,
            requested_date=date.today(),
            status=RequisitionStatus.DRAFT,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(requisition)
        await self.db.commit()
        await self.db.refresh(requisition)
        
        return requisition
    
    async def get_requisition(self, requisition_id: str) -> Optional[JobRequisition]:
        """Get requisition by ID"""
        query = select(JobRequisition).where(
            and_(
                JobRequisition.id == requisition_id,
                JobRequisition.tenant_id == self.tenant_id,
                JobRequisition.is_deleted == False
            )
        ).options(
            selectinload(JobRequisition.department),
            selectinload(JobRequisition.designation),
            selectinload(JobRequisition.requested_by),
            selectinload(JobRequisition.approved_by)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_requisitions(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[RequisitionStatusEnum] = None,
        department_id: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Tuple[List[JobRequisition], int]:
        """Get paginated list of requisitions"""
        query = select(JobRequisition).where(
            and_(
                JobRequisition.tenant_id == self.tenant_id,
                JobRequisition.is_deleted == False
            )
        ).options(
            selectinload(JobRequisition.department),
            selectinload(JobRequisition.designation),
            selectinload(JobRequisition.requested_by)
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    JobRequisition.title.ilike(search_term),
                    JobRequisition.requisition_code.ilike(search_term)
                )
            )
        
        if status:
            query = query.where(JobRequisition.status == status)
        
        if department_id:
            query = query.where(JobRequisition.department_id == department_id)
        
        if priority:
            query = query.where(JobRequisition.priority == priority)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(desc(JobRequisition.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        requisitions = result.scalars().all()
        
        return requisitions, total
    
    async def update_requisition(
        self, requisition_id: str, data: JobRequisitionUpdate
    ) -> JobRequisition:
        """Update requisition"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(requisition, field, value)
        
        requisition.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(requisition)
        
        return requisition
    
    async def submit_for_approval(self, requisition_id: str) -> JobRequisition:
        """Submit requisition for approval"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        if requisition.status != RequisitionStatus.DRAFT:
            raise ValueError("Only draft requisitions can be submitted")
        
        requisition.status = RequisitionStatus.PENDING_APPROVAL
        requisition.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(requisition)
        
        return requisition
    
    async def approve_requisition(
        self, requisition_id: str, approval: JobRequisitionApproval
    ) -> JobRequisition:
        """Approve or reject requisition"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        if requisition.status != RequisitionStatus.PENDING_APPROVAL:
            raise ValueError("Only pending requisitions can be approved/rejected")
        
        if approval.approved:
            requisition.status = RequisitionStatus.APPROVED
            requisition.approved_by_employee_id = self.user_id
            requisition.approved_date = date.today()
        else:
            requisition.status = RequisitionStatus.REJECTED
            requisition.rejection_reason = approval.rejection_reason
        
        requisition.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(requisition)
        
        return requisition
    
    async def close_requisition(self, requisition_id: str) -> JobRequisition:
        """Close requisition"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        requisition.status = RequisitionStatus.CLOSED
        requisition.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(requisition)
        
        return requisition
    
    async def delete_requisition(self, requisition_id: str) -> bool:
        """Soft delete requisition"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        requisition.is_deleted = True
        requisition.deleted_at = datetime.utcnow()
        requisition.deleted_by = self.user_id
        
        await self.db.commit()
        return True
