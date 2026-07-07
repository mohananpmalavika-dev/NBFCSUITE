"""
HRMS Designation Service Layer
Business logic for designation operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import Optional, List, Tuple
from datetime import datetime

from backend.shared.database.hrms_models import Designation, Employee
from .schemas import DesignationCreate, DesignationUpdate, DesignationStats


class DesignationService:
    """Service for designation operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_designation_code(self) -> str:
        """Generate unique designation code: DESIG-XXXX"""
        # Get count of designations
        count_query = select(func.count(Designation.id)).where(
            Designation.tenant_id == self.tenant_id
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        # Generate code
        sequence = str(count + 1).zfill(4)
        return f"DESIG-{sequence}"
    
    async def create_designation(self, data: DesignationCreate) -> Designation:
        """Create new designation with auto-generated code"""
        
        # Generate designation code
        designation_code = await self.generate_designation_code()
        
        # Create designation
        designation = Designation(
            tenant_id=self.tenant_id,
            designation_code=designation_code,
            designation_name=data.designation_name,
            description=data.description,
            level=data.level,
            grade=data.grade,
            min_salary=data.min_salary,
            max_salary=data.max_salary,
            min_experience_years=data.min_experience_years,
            required_qualification=data.required_qualification,
            is_active=data.is_active,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(designation)
        await self.db.commit()
        await self.db.refresh(designation)
        
        return designation
    
    async def get_designation(self, designation_id: str) -> Optional[Designation]:
        """Get designation by ID"""
        query = select(Designation).where(
            and_(
                Designation.id == designation_id,
                Designation.tenant_id == self.tenant_id,
                Designation.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_designation_by_code(self, designation_code: str) -> Optional[Designation]:
        """Get designation by code"""
        query = select(Designation).where(
            and_(
                Designation.designation_code == designation_code,
                Designation.tenant_id == self.tenant_id,
                Designation.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_designations(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        level: Optional[int] = None,
        grade: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Designation], int]:
        """Get paginated list of designations with filters"""
        
        # Base query
        query = select(Designation).where(
            and_(
                Designation.tenant_id == self.tenant_id,
                Designation.is_deleted == False
            )
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Designation.designation_name.ilike(search_term),
                    Designation.designation_code.ilike(search_term),
                    Designation.description.ilike(search_term)
                )
            )
        
        if level is not None:
            query = query.where(Designation.level == level)
        
        if grade:
            query = query.where(Designation.grade == grade)
        
        if is_active is not None:
            query = query.where(Designation.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and sorting
        query = query.order_by(Designation.level, Designation.designation_name)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        designations = result.scalars().all()
        
        return designations, total
    
    async def update_designation(self, designation_id: str, data: DesignationUpdate) -> Designation:
        """Update designation details"""
        designation = await self.get_designation(designation_id)
        if not designation:
            raise ValueError("Designation not found")
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(designation, field, value)
        
        designation.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(designation)
        
        return designation
    
    async def delete_designation(self, designation_id: str) -> bool:
        """Soft delete designation"""
        designation = await self.get_designation(designation_id)
        if not designation:
            raise ValueError("Designation not found")
        
        # Check if designation has employees
        emp_count_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.designation_id == designation_id,
                Employee.is_deleted == False
            )
        )
        emp_result = await self.db.execute(emp_count_query)
        emp_count = emp_result.scalar() or 0
        
        if emp_count > 0:
            raise ValueError(f"Cannot delete designation with {emp_count} employees")
        
        designation.is_deleted = True
        designation.deleted_at = datetime.utcnow()
        designation.deleted_by = self.user_id
        designation.is_active = False
        
        await self.db.commit()
        return True
    
    async def get_employee_count(self, designation_id: str) -> int:
        """Get count of employees with this designation"""
        count_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.designation_id == designation_id,
                Employee.is_deleted == False,
                Employee.is_active == True
            )
        )
        result = await self.db.execute(count_query)
        return result.scalar() or 0
    
    async def get_stats(self) -> DesignationStats:
        """Get designation statistics"""
        # Total designations
        total_query = select(func.count(Designation.id)).where(
            and_(
                Designation.tenant_id == self.tenant_id,
                Designation.is_deleted == False
            )
        )
        total_result = await self.db.execute(total_query)
        total_designations = total_result.scalar() or 0
        
        # Active designations
        active_query = select(func.count(Designation.id)).where(
            and_(
                Designation.tenant_id == self.tenant_id,
                Designation.is_deleted == False,
                Designation.is_active == True
            )
        )
        active_result = await self.db.execute(active_query)
        active_designations = active_result.scalar() or 0
        
        # Employees by designation
        emp_desig_query = select(
            Designation.designation_name,
            func.count(Employee.id).label('count')
        ).join(
            Employee, Employee.designation_id == Designation.id
        ).where(
            and_(
                Designation.tenant_id == self.tenant_id,
                Designation.is_deleted == False,
                Employee.is_deleted == False,
                Employee.is_active == True
            )
        ).group_by(Designation.designation_name).order_by(desc('count'))
        
        emp_desig_result = await self.db.execute(emp_desig_query)
        employees_by_designation = [
            {"designation": row[0], "count": row[1]} 
            for row in emp_desig_result
        ]
        
        return DesignationStats(
            total_designations=total_designations,
            active_designations=active_designations,
            employees_by_designation=employees_by_designation
        )
