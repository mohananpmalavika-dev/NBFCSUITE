"""
HRMS Department Service Layer
Business logic for department operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime

from backend.shared.database.hrms_models import Department, Employee, Organization
from .schemas import DepartmentCreate, DepartmentUpdate, DepartmentTreeNode, DepartmentStats


class DepartmentService:
    """Service for department operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_department_code(self) -> str:
        """Generate unique department code: DEPT-XXXX"""
        # Get count of departments
        count_query = select(func.count(Department.id)).where(
            Department.tenant_id == self.tenant_id
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        # Generate code
        sequence = str(count + 1).zfill(4)
        return f"DEPT-{sequence}"
    
    async def create_department(self, data: DepartmentCreate) -> Department:
        """Create new department with auto-generated code"""
        
        # Generate department code
        department_code = await self.generate_department_code()
        
        # Create department
        department = Department(
            tenant_id=self.tenant_id,
            department_code=department_code,
            department_name=data.department_name,
            department_type=data.department_type,
            description=data.description,
            organization_id=data.organization_id,
            parent_department_id=data.parent_department_id,
            hod_employee_id=data.hod_employee_id,
            email=data.email,
            phone=data.phone,
            extension=data.extension,
            location=data.location,
            floor=data.floor,
            cost_center_code=data.cost_center_code,
            is_active=data.is_active,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(department)
        await self.db.commit()
        await self.db.refresh(department)
        
        return department
    
    async def get_department(self, department_id: str) -> Optional[Department]:
        """Get department by ID with relationships"""
        query = select(Department).where(
            and_(
                Department.id == department_id,
                Department.tenant_id == self.tenant_id,
                Department.is_deleted == False
            )
        ).options(
            selectinload(Department.organization),
            selectinload(Department.parent_department),
            selectinload(Department.hod)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_department_by_code(self, department_code: str) -> Optional[Department]:
        """Get department by code"""
        query = select(Department).where(
            and_(
                Department.department_code == department_code,
                Department.tenant_id == self.tenant_id,
                Department.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_departments(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        organization_id: Optional[str] = None,
        parent_department_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Department], int]:
        """Get paginated list of departments with filters"""
        
        # Base query
        query = select(Department).where(
            and_(
                Department.tenant_id == self.tenant_id,
                Department.is_deleted == False
            )
        ).options(
            selectinload(Department.organization),
            selectinload(Department.hod)
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Department.department_name.ilike(search_term),
                    Department.department_code.ilike(search_term),
                    Department.description.ilike(search_term)
                )
            )
        
        if organization_id:
            query = query.where(Department.organization_id == organization_id)
        
        if parent_department_id:
            query = query.where(Department.parent_department_id == parent_department_id)
        
        if is_active is not None:
            query = query.where(Department.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and sorting
        query = query.order_by(Department.department_name)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        departments = result.scalars().all()
        
        return departments, total
    
    async def update_department(self, department_id: str, data: DepartmentUpdate) -> Department:
        """Update department details"""
        department = await self.get_department(department_id)
        if not department:
            raise ValueError("Department not found")
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(department, field, value)
        
        department.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(department)
        
        return department
    
    async def delete_department(self, department_id: str) -> bool:
        """Soft delete department"""
        department = await self.get_department(department_id)
        if not department:
            raise ValueError("Department not found")
        
        # Check if department has employees
        emp_count_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.department_id == department_id,
                Employee.is_deleted == False
            )
        )
        emp_result = await self.db.execute(emp_count_query)
        emp_count = emp_result.scalar() or 0
        
        if emp_count > 0:
            raise ValueError(f"Cannot delete department with {emp_count} employees")
        
        department.is_deleted = True
        department.deleted_at = datetime.utcnow()
        department.deleted_by = self.user_id
        department.is_active = False
        
        await self.db.commit()
        return True
    
    async def get_employee_count(self, department_id: str) -> int:
        """Get count of employees in department"""
        count_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.department_id == department_id,
                Employee.is_deleted == False,
                Employee.is_active == True
            )
        )
        result = await self.db.execute(count_query)
        return result.scalar() or 0
    
    async def build_department_tree(self, organization_id: Optional[str] = None) -> List[DepartmentTreeNode]:
        """Build department hierarchy tree"""
        # Get all departments
        query = select(Department).where(
            and_(
                Department.tenant_id == self.tenant_id,
                Department.is_deleted == False,
                Department.is_active == True
            )
        )
        
        if organization_id:
            query = query.where(Department.organization_id == organization_id)
        
        result = await self.db.execute(query)
        all_departments = result.scalars().all()
        
        # Build department map
        dept_map = {}
        for dept in all_departments:
            emp_count = await self.get_employee_count(dept.id)
            dept_map[dept.id] = DepartmentTreeNode(
                id=dept.id,
                department_code=dept.department_code,
                department_name=dept.department_name,
                department_type=dept.department_type,
                parent_department_id=dept.parent_department_id,
                hod_employee_id=dept.hod_employee_id,
                hod_name=dept.hod.full_name if dept.hod else None,
                employee_count=emp_count,
                children=[]
            )
        
        # Build tree structure
        root_nodes = []
        for dept_id, node in dept_map.items():
            if node.parent_department_id and node.parent_department_id in dept_map:
                dept_map[node.parent_department_id].children.append(node)
            else:
                root_nodes.append(node)
        
        return root_nodes
    
    async def get_stats(self) -> DepartmentStats:
        """Get department statistics"""
        # Total departments
        total_query = select(func.count(Department.id)).where(
            and_(
                Department.tenant_id == self.tenant_id,
                Department.is_deleted == False
            )
        )
        total_result = await self.db.execute(total_query)
        total_departments = total_result.scalar() or 0
        
        # Active departments
        active_query = select(func.count(Department.id)).where(
            and_(
                Department.tenant_id == self.tenant_id,
                Department.is_deleted == False,
                Department.is_active == True
            )
        )
        active_result = await self.db.execute(active_query)
        active_departments = active_result.scalar() or 0
        
        # Employees by department
        emp_dept_query = select(
            Department.department_name,
            func.count(Employee.id).label('count')
        ).join(
            Employee, Employee.department_id == Department.id
        ).where(
            and_(
                Department.tenant_id == self.tenant_id,
                Department.is_deleted == False,
                Employee.is_deleted == False,
                Employee.is_active == True
            )
        ).group_by(Department.department_name).order_by(desc('count'))
        
        emp_dept_result = await self.db.execute(emp_dept_query)
        employees_by_department = [
            {"department": row[0], "count": row[1]} 
            for row in emp_dept_result
        ]
        
        return DepartmentStats(
            total_departments=total_departments,
            active_departments=active_departments,
            employees_by_department=employees_by_department
        )
