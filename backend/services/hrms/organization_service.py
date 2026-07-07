"""
HRMS Organization Service Layer
Business logic for organization operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List, Tuple
from datetime import datetime

from backend.shared.database.hrms_models import Organization, Department, Employee
from .schemas import OrganizationCreate, OrganizationUpdate


class OrganizationService:
    """Service for organization operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_organization_code(self) -> str:
        """Generate unique organization code: ORG-XXXX"""
        # Get count of organizations
        count_query = select(func.count(Organization.id)).where(
            Organization.tenant_id == self.tenant_id
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        # Generate code
        sequence = str(count + 1).zfill(4)
        return f"ORG-{sequence}"
    
    async def create_organization(self, data: OrganizationCreate) -> Organization:
        """Create new organization with auto-generated code"""
        
        # Generate organization code
        organization_code = await self.generate_organization_code()
        
        # Create organization
        organization = Organization(
            tenant_id=self.tenant_id,
            organization_code=organization_code,
            organization_name=data.organization_name,
            short_name=data.short_name,
            legal_name=data.legal_name,
            pan_number=data.pan_number,
            tan_number=data.tan_number,
            gstin=data.gstin,
            cin_number=data.cin_number,
            email=data.email,
            phone=data.phone,
            website=data.website,
            registered_address_line1=data.registered_address_line1,
            registered_address_line2=data.registered_address_line2,
            registered_city=data.registered_city,
            registered_state=data.registered_state,
            registered_pincode=data.registered_pincode,
            established_date=data.established_date,
            is_active=data.is_active,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(organization)
        await self.db.commit()
        await self.db.refresh(organization)
        
        return organization
    
    async def get_organization(self, organization_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        query = select(Organization).where(
            and_(
                Organization.id == organization_id,
                Organization.tenant_id == self.tenant_id,
                Organization.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_organization_by_code(self, organization_code: str) -> Optional[Organization]:
        """Get organization by code"""
        query = select(Organization).where(
            and_(
                Organization.organization_code == organization_code,
                Organization.tenant_id == self.tenant_id,
                Organization.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_organizations(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Organization], int]:
        """Get paginated list of organizations with filters"""
        
        # Base query
        query = select(Organization).where(
            and_(
                Organization.tenant_id == self.tenant_id,
                Organization.is_deleted == False
            )
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Organization.organization_name.ilike(search_term),
                    Organization.organization_code.ilike(search_term),
                    Organization.short_name.ilike(search_term)
                )
            )
        
        if is_active is not None:
            query = query.where(Organization.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and sorting
        query = query.order_by(Organization.organization_name)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        organizations = result.scalars().all()
        
        return organizations, total
    
    async def update_organization(self, organization_id: str, data: OrganizationUpdate) -> Organization:
        """Update organization details"""
        organization = await self.get_organization(organization_id)
        if not organization:
            raise ValueError("Organization not found")
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(organization, field, value)
        
        organization.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(organization)
        
        return organization
    
    async def delete_organization(self, organization_id: str) -> bool:
        """Soft delete organization"""
        organization = await self.get_organization(organization_id)
        if not organization:
            raise ValueError("Organization not found")
        
        # Check if organization has departments or employees
        dept_count_query = select(func.count(Department.id)).where(
            and_(
                Department.tenant_id == self.tenant_id,
                Department.organization_id == organization_id,
                Department.is_deleted == False
            )
        )
        dept_result = await self.db.execute(dept_count_query)
        dept_count = dept_result.scalar() or 0
        
        emp_count_query = select(func.count(Employee.id)).where(
            and_(
                Employee.tenant_id == self.tenant_id,
                Employee.organization_id == organization_id,
                Employee.is_deleted == False
            )
        )
        emp_result = await self.db.execute(emp_count_query)
        emp_count = emp_result.scalar() or 0
        
        if dept_count > 0 or emp_count > 0:
            raise ValueError(
                f"Cannot delete organization with {dept_count} departments and {emp_count} employees"
            )
        
        organization.is_deleted = True
        organization.deleted_at = datetime.utcnow()
        organization.deleted_by = self.user_id
        organization.is_active = False
        
        await self.db.commit()
        return True
    
    async def get_all_active(self) -> List[Organization]:
        """Get all active organizations (for dropdowns)"""
        query = select(Organization).where(
            and_(
                Organization.tenant_id == self.tenant_id,
                Organization.is_deleted == False,
                Organization.is_active == True
            )
        ).order_by(Organization.organization_name)
        
        result = await self.db.execute(query)
        return result.scalars().all()
