"""
HRMS Employee Service Layer
Business logic for employee operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from backend.shared.database.hrms_models import (
    Employee, Department, Designation, HRMSOrganization, ReportingHierarchy,
    EmploymentType, EmploymentStatus
)
from .schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeListItem,
    EmployeeDashboardStats, EmployeeCardView, OrgChartNode
)


class EmployeeService:
    """Service for employee operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_employee_code(self) -> str:
        """Generate unique employee code: EMP-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        # Get count of employees this month
        count_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.employee_code.like(f"EMP-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        # Generate code
        sequence = str(count + 1).zfill(4)
        return f"EMP-{year_month}-{sequence}"
    
    def _calculate_age(self, date_of_birth: date) -> int:
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        today = date.today()
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    def _build_full_name(self, first_name: str, middle_name: Optional[str], last_name: str) -> str:
        """Build full name from components"""
        parts = [first_name]
        if middle_name:
            parts.append(middle_name)
        parts.append(last_name)
        return " ".join(parts)
    
    async def create_employee(self, data: EmployeeCreate) -> Employee:
        """Create new employee with auto-generated code"""
        
        # Generate employee code
        employee_code = await self.generate_employee_code()
        
        # Calculate full name
        full_name = self._build_full_name(data.first_name, data.middle_name, data.last_name)
        
        # Calculate age
        age = self._calculate_age(data.date_of_birth) if data.date_of_birth else None
        
        # Determine probation status
        is_on_probation = data.employment_type == EmploymentType.PROBATION
        probation_end_date = None
        if is_on_probation and data.date_of_joining:
            # Default 3 months probation
            probation_end_date = data.date_of_joining + relativedelta(months=3)
        
        # Create employee
        employee = Employee(
            tenant_id=self.tenant_id,
            employee_code=employee_code,
            organization_id=data.organization_id,
            department_id=data.department_id,
            designation_id=data.designation_id,
            reporting_manager_id=data.reporting_manager_id,
            employment_type=data.employment_type,
            employment_status=data.employment_status,
            date_of_joining=data.date_of_joining,
            date_of_confirmation=data.date_of_confirmation,
            work_location=data.work_location,
            shift_type=data.shift_type,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            full_name=full_name,
            date_of_birth=data.date_of_birth,
            age=age,
            gender=data.gender,
            blood_group=data.blood_group,
            marital_status=data.marital_status,
            father_name=data.father_name,
            mother_name=data.mother_name,
            spouse_name=data.spouse_name,
            number_of_children=data.number_of_children,
            personal_email=data.personal_email,
            official_email=data.official_email,
            mobile=data.mobile,
            alternate_mobile=data.alternate_mobile,
            emergency_contact_name=data.emergency_contact_name,
            emergency_contact_number=data.emergency_contact_number,
            emergency_contact_relation=data.emergency_contact_relation,
            current_address_line1=data.current_address_line1,
            current_address_line2=data.current_address_line2,
            current_city=data.current_city,
            current_state=data.current_state,
            current_pincode=data.current_pincode,
            permanent_address_line1=data.permanent_address_line1,
            permanent_address_line2=data.permanent_address_line2,
            permanent_city=data.permanent_city,
            permanent_state=data.permanent_state,
            permanent_pincode=data.permanent_pincode,
            is_permanent_same_as_current=data.is_permanent_same_as_current,
            pan_number=data.pan_number,
            aadhaar_number=data.aadhaar_number,
            passport_number=data.passport_number,
            driving_license_number=data.driving_license_number,
            salary_bank_name=data.salary_bank_name,
            salary_account_number=data.salary_account_number,
            salary_ifsc_code=data.salary_ifsc_code,
            pf_number=data.pf_number,
            uan_number=data.uan_number,
            esi_number=data.esi_number,
            current_ctc=data.current_ctc,
            basic_salary=data.basic_salary,
            highest_qualification=data.highest_qualification,
            specialization=data.specialization,
            university=data.university,
            year_of_passing=data.year_of_passing,
            total_experience_years=data.total_experience_years,
            is_on_probation=is_on_probation,
            probation_end_date=probation_end_date,
            notice_period_days=data.notice_period_days,
            is_active=data.is_active,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        
        # Create reporting hierarchy record if manager assigned
        if data.reporting_manager_id:
            await self._create_reporting_hierarchy(
                employee_id=employee.id,
                manager_id=data.reporting_manager_id,
                effective_from=data.date_of_joining
            )
        
        return employee
    
    async def _create_reporting_hierarchy(
        self, employee_id: str, manager_id: str, effective_from: date
    ):
        """Create reporting hierarchy record"""
        hierarchy = ReportingHierarchy(
            tenant_id=self.tenant_id,
            employee_id=employee_id,
            manager_id=manager_id,
            reporting_type="direct",
            is_primary=True,
            effective_from=effective_from,
            is_current=True,
            created_by=self.user_id
        )
        self.db.add(hierarchy)
        await self.db.commit()
    
    async def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID with relationships"""
        query = select(Employee).where(
            and_(
                Employee.id == employee_id,
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        ).options(
            selectinload(Employee.organization),
            selectinload(Employee.department),
            selectinload(Employee.designation),
            selectinload(Employee.reporting_manager)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_employee_by_code(self, employee_code: str) -> Optional[Employee]:
        """Get employee by employee code"""
        query = select(Employee).where(
            and_(
                Employee.employee_code == employee_code,
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_employees(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        department_id: Optional[str] = None,
        designation_id: Optional[str] = None,
        employment_type: Optional[EmploymentType] = None,
        employment_status: Optional[EmploymentStatus] = None,
        reporting_manager_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Employee], int]:
        """Get paginated list of employees with filters"""
        
        # Base query
        query = select(Employee).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        ).options(
            selectinload(Employee.department),
            selectinload(Employee.designation)
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Employee.full_name.ilike(search_term),
                    Employee.employee_code.ilike(search_term),
                    Employee.mobile.like(search_term),
                    Employee.official_email.ilike(search_term),
                    Employee.pan_number.ilike(search_term)
                )
            )
        
        if department_id:
            query = query.where(Employee.department_id == department_id)
        
        if designation_id:
            query = query.where(Employee.designation_id == designation_id)
        
        if employment_type:
            query = query.where(Employee.employment_type == employment_type)
        
        if employment_status:
            query = query.where(Employee.employment_status == employment_status)
        
        if reporting_manager_id:
            query = query.where(Employee.reporting_manager_id == reporting_manager_id)
        
        if is_active is not None:
            query = query.where(Employee.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and sorting
        query = query.order_by(desc(Employee.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        employees = result.scalars().all()
        
        return employees, total
    
    async def update_employee(self, employee_id: str, data: EmployeeUpdate) -> Employee:
        """Update employee details"""
        employee = await self.get_employee(employee_id)
        if not employee:
            raise ValueError("Employee not found")
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        employee.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(employee)
        
        return employee
    
    async def delete_employee(self, employee_id: str) -> bool:
        """Soft delete employee"""
        employee = await self.get_employee(employee_id)
        if not employee:
            raise ValueError("Employee not found")
        
        employee.is_deleted = True
        employee.deleted_at = datetime.utcnow()
        employee.deleted_by = self.user_id
        employee.is_active = False
        
        await self.db.commit()
        return True
    
    async def get_dashboard_stats(self) -> EmployeeDashboardStats:
        """Get employee dashboard statistics"""
        
        # Total employees
        total_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        )
        total_result = await self.db.execute(total_query)
        total_employees = total_result.scalar() or 0
        
        # Active employees
        active_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False,
                Employee.is_active == True,
                Employee.employment_status == EmploymentStatus.ACTIVE
            )
        )
        active_result = await self.db.execute(active_query)
        active_employees = active_result.scalar() or 0
        
        # Inactive employees
        inactive_employees = total_employees - active_employees
        
        # On probation
        probation_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False,
                Employee.is_on_probation == True
            )
        )
        probation_result = await self.db.execute(probation_query)
        on_probation = probation_result.scalar() or 0
        
        # Permanent employees
        permanent_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False,
                Employee.employment_type == EmploymentType.PERMANENT
            )
        )
        permanent_result = await self.db.execute(permanent_query)
        permanent_employees = permanent_result.scalar() or 0
        
        # Contract employees
        contract_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False,
                Employee.employment_type == EmploymentType.CONTRACT
            )
        )
        contract_result = await self.db.execute(contract_query)
        contract_employees = contract_result.scalar() or 0
        
        # New joiners this month
        first_day_of_month = date.today().replace(day=1)
        new_joiners_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False,
                Employee.date_of_joining >= first_day_of_month
            )
        )
        new_joiners_result = await self.db.execute(new_joiners_query)
        new_joiners_this_month = new_joiners_result.scalar() or 0
        
        # Resignations this month
        resignations_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False,
                Employee.employment_status == EmploymentStatus.RESIGNED,
                Employee.date_of_resignation >= first_day_of_month
            )
        )
        resignations_result = await self.db.execute(resignations_query)
        resignations_this_month = resignations_result.scalar() or 0
        
        # By department
        dept_query = select(
            Department.department_name,
            func.count(Employee.id).label('count')
        ).join(
            Employee, Employee.department_id == Department.id
        ).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False,
                Employee.is_active == True
            )
        ).group_by(Department.department_name)
        
        dept_result = await self.db.execute(dept_query)
        by_department = [{"department": row[0], "count": row[1]} for row in dept_result]
        
        # By designation
        desig_query = select(
            Designation.designation_name,
            func.count(Employee.id).label('count')
        ).join(
            Employee, Employee.designation_id == Designation.id
        ).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False,
                Employee.is_active == True
            )
        ).group_by(Designation.designation_name)
        
        desig_result = await self.db.execute(desig_query)
        by_designation = [{"designation": row[0], "count": row[1]} for row in desig_result]
        
        return EmployeeDashboardStats(
            total_employees=total_employees,
            active_employees=active_employees,
            inactive_employees=inactive_employees,
            on_probation=on_probation,
            permanent_employees=permanent_employees,
            contract_employees=contract_employees,
            new_joiners_this_month=new_joiners_this_month,
            resignations_this_month=resignations_this_month,
            by_department=by_department,
            by_designation=by_designation
        )
    
    async def get_subordinates(self, manager_id: str) -> List[Employee]:
        """Get all subordinates of a manager"""
        query = select(Employee).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False,
                Employee.reporting_manager_id == manager_id,
                Employee.is_active == True
            )
        ).options(
            selectinload(Employee.department),
            selectinload(Employee.designation)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def build_org_chart(self, root_employee_id: Optional[str] = None) -> OrgChartNode:
        """Build organization chart tree"""
        # If no root specified, find top-level employees (no manager)
        if not root_employee_id:
            query = select(Employee).where(
                and_(
                    Employee.tenant_id == self.tenant_id,
                    Employee.is_deleted == False,
                    Employee.reporting_manager_id == None,
                    Employee.is_active == True
                )
            ).limit(1)
            result = await self.db.execute(query)
            root_employee = result.scalar_one_or_none()
            if not root_employee:
                return None
            root_employee_id = root_employee.id
        
        # Recursive function to build tree
        async def build_node(employee_id: str) -> OrgChartNode:
            employee = await self.get_employee(employee_id)
            if not employee:
                return None
            
            # Get subordinates
            subordinates = await self.get_subordinates(employee_id)
            
            # Build subordinate nodes recursively
            subordinate_nodes = []
            for sub in subordinates:
                node = await build_node(sub.id)
                if node:
                    subordinate_nodes.append(node)
            
            return OrgChartNode(
                id=employee.id,
                employee_code=employee.employee_code,
                full_name=employee.full_name,
                designation_name=employee.designation.designation_name if employee.designation else None,
                department_name=employee.department.department_name if employee.department else None,
                photo_url=employee.photo_url,
                reporting_manager_id=employee.reporting_manager_id,
                subordinates=subordinate_nodes
            )
        
        return await build_node(root_employee_id)
    
    async def search_employees(
        self,
        employee_code: Optional[str] = None,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        pan_number: Optional[str] = None
    ) -> List[Employee]:
        """Search employees by specific fields"""
        query = select(Employee).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        )
        
        conditions = []
        if employee_code:
            conditions.append(Employee.employee_code == employee_code)
        if mobile:
            conditions.append(Employee.mobile == mobile)
        if email:
            conditions.append(
                or_(
                    Employee.official_email == email,
                    Employee.personal_email == email
                )
            )
        if pan_number:
            conditions.append(Employee.pan_number == pan_number.upper())
        
        if conditions:
            query = query.where(or_(*conditions))
        
        result = await self.db.execute(query)
        return result.scalars().all()
