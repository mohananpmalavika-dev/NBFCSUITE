"""
Salary Component Service
Handles CRUD operations for salary components (earnings, deductions, employer contributions)
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from backend.shared.database.payroll_models import (
    SalaryComponent,
    ComponentType
)
from backend.services.payroll.schemas import (
    SalaryComponentCreate,
    SalaryComponentUpdate,
    SalaryComponentResponse,
    SalaryComponentListResponse
)


class SalaryComponentService:
    """Service class for salary component operations"""
    
    @staticmethod
    async def create_component(
        db: Session,
        component_data: SalaryComponentCreate,
        created_by: int
    ) -> SalaryComponent:
        """Create a new salary component"""
        
        # Check if component code already exists
        existing = db.query(SalaryComponent).filter(
            and_(
                SalaryComponent.component_code == component_data.component_code,
                SalaryComponent.tenant_id == component_data.tenant_id,
                SalaryComponent.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Component code {component_data.component_code} already exists")
        
        # Create component
        component = SalaryComponent(
            **component_data.dict(),
            created_by=created_by,
            updated_by=created_by
        )
        
        db.add(component)
        db.commit()
        db.refresh(component)
        
        return component
    
    @staticmethod
    async def get_component(
        db: Session,
        component_id: int,
        tenant_id: int
    ) -> Optional[SalaryComponent]:
        """Get a salary component by ID"""
        return db.query(SalaryComponent).filter(
            and_(
                SalaryComponent.id == component_id,
                SalaryComponent.tenant_id == tenant_id,
                SalaryComponent.is_deleted == False
            )
        ).first()

    
    @staticmethod
    async def list_components(
        db: Session,
        tenant_id: int,
        component_type: Optional[ComponentType] = None,
        is_active: Optional[bool] = None,
        is_statutory: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> SalaryComponentListResponse:
        """List salary components with filters"""
        
        query = db.query(SalaryComponent).filter(
            and_(
                SalaryComponent.tenant_id == tenant_id,
                SalaryComponent.is_deleted == False
            )
        )
        
        # Apply filters
        if component_type:
            query = query.filter(SalaryComponent.component_type == component_type)
        
        if is_active is not None:
            query = query.filter(SalaryComponent.is_active == is_active)
        
        if is_statutory is not None:
            query = query.filter(SalaryComponent.is_statutory == is_statutory)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (SalaryComponent.component_code.ilike(search_filter)) |
                (SalaryComponent.component_name.ilike(search_filter))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        components = query.order_by(
            SalaryComponent.display_order,
            SalaryComponent.component_name
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return SalaryComponentListResponse(
            items=components,
            total=total,
            page=page,
            page_size=page_size
        )

    
    @staticmethod
    async def update_component(
        db: Session,
        component_id: int,
        tenant_id: int,
        component_data: SalaryComponentUpdate,
        updated_by: int
    ) -> Optional[SalaryComponent]:
        """Update a salary component"""
        
        component = await SalaryComponentService.get_component(db, component_id, tenant_id)
        
        if not component:
            return None
        
        # Check if system component
        if component.is_system_component:
            raise ValueError("System components cannot be modified")
        
        # Update fields
        update_data = component_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(component, field, value)
        
        component.updated_by = updated_by
        component.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(component)
        
        return component
    
    @staticmethod
    async def delete_component(
        db: Session,
        component_id: int,
        tenant_id: int,
        deleted_by: int
    ) -> bool:
        """Soft delete a salary component"""
        
        component = await SalaryComponentService.get_component(db, component_id, tenant_id)
        
        if not component:
            return False
        
        # Check if system component
        if component.is_system_component:
            raise ValueError("System components cannot be deleted")
        
        # Check if component is used in any active salary structure
        # (This check would be implemented based on your business rules)
        
        component.is_deleted = True
        component.updated_by = deleted_by
        component.updated_at = datetime.utcnow()
        
        db.commit()
        
        return True
    
    @staticmethod
    async def get_active_components_by_type(
        db: Session,
        tenant_id: int,
        component_type: ComponentType
    ) -> List[SalaryComponent]:
        """Get all active components by type"""
        return db.query(SalaryComponent).filter(
            and_(
                SalaryComponent.tenant_id == tenant_id,
                SalaryComponent.component_type == component_type,
                SalaryComponent.is_active == True,
                SalaryComponent.is_deleted == False
            )
        ).order_by(SalaryComponent.display_order).all()
