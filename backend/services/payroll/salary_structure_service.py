"""
Salary Structure Service
Handles CRUD operations for salary structures and component mappings
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from backend.shared.database.payroll_models import (
    SalaryStructure, SalaryStructureComponent, SalaryComponent
)
from backend.services.payroll.schemas import (
    SalaryStructureCreate, SalaryStructureUpdate,
    SalaryStructureResponse, SalaryStructureListResponse
)


class SalaryStructureService:
    """Service class for salary structure operations"""
    
    @staticmethod
    async def create_structure(
        db: Session,
        structure_data: SalaryStructureCreate,
        created_by: int
    ) -> SalaryStructure:
        """Create a new salary structure with components"""
        
        # Check if structure code already exists
        existing = db.query(SalaryStructure).filter(
            and_(
                SalaryStructure.structure_code == structure_data.structure_code,
                SalaryStructure.tenant_id == structure_data.tenant_id,
                SalaryStructure.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Structure code {structure_data.structure_code} already exists")
        
        # Create structure
        structure_dict = structure_data.dict(exclude={'components'})
        structure = SalaryStructure(
            **structure_dict,
            created_by=created_by,
            updated_by=created_by
        )
        
        db.add(structure)
        db.flush()
        
        # Add components
        for comp_data in structure_data.components:
            structure_comp = SalaryStructureComponent(
                tenant_id=structure_data.tenant_id,
                structure_id=structure.id,
                **comp_data.dict()
            )
            db.add(structure_comp)
        
        db.commit()
        db.refresh(structure)
        
        return structure
    
    @staticmethod
    async def get_structure(
        db: Session,
        structure_id: int,
        tenant_id: int
    ) -> Optional[SalaryStructure]:
        """Get a salary structure by ID with components"""
        structure = db.query(SalaryStructure).filter(
            and_(
                SalaryStructure.id == structure_id,
                SalaryStructure.tenant_id == tenant_id,
                SalaryStructure.is_deleted == False
            )
        ).first()
        
        if structure:
            # Load components
            components = db.query(SalaryStructureComponent).filter(
                and_(
                    SalaryStructureComponent.structure_id == structure_id,
                    SalaryStructureComponent.is_deleted == False
                )
            ).all()
            
            structure.components = components
        
        return structure
    
    @staticmethod
    async def list_structures(
        db: Session,
        tenant_id: int,
        is_active: Optional[bool] = None,
        department: Optional[str] = None,
        designation: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> SalaryStructureListResponse:
        """List salary structures with filters"""
        
        query = db.query(SalaryStructure).filter(
            and_(
                SalaryStructure.tenant_id == tenant_id,
                SalaryStructure.is_deleted == False
            )
        )
        
        # Apply filters
        if is_active is not None:
            query = query.filter(SalaryStructure.is_active == is_active)
        
        if department:
            query = query.filter(SalaryStructure.department == department)
        
        if designation:
            query = query.filter(SalaryStructure.designation == designation)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (SalaryStructure.structure_code.ilike(search_filter)) |
                (SalaryStructure.structure_name.ilike(search_filter))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        structures = query.order_by(
            SalaryStructure.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return SalaryStructureListResponse(
            items=structures,
            total=total,
            page=page,
            page_size=page_size
        )
    
    @staticmethod
    async def update_structure(
        db: Session,
        structure_id: int,
        tenant_id: int,
        structure_data: SalaryStructureUpdate,
        updated_by: int
    ) -> Optional[SalaryStructure]:
        """Update a salary structure"""
        
        structure = await SalaryStructureService.get_structure(db, structure_id, tenant_id)
        
        if not structure:
            return None
        
        # Update fields
        update_data = structure_data.dict(exclude_unset=True, exclude={'components'})
        for field, value in update_data.items():
            setattr(structure, field, value)
        
        structure.updated_by = updated_by
        structure.updated_at = datetime.utcnow()
        
        # Update components if provided
        if structure_data.components is not None:
            # Delete existing components
            db.query(SalaryStructureComponent).filter(
                SalaryStructureComponent.structure_id == structure_id
            ).update({"is_deleted": True})
            
            # Add new components
            for comp_data in structure_data.components:
                structure_comp = SalaryStructureComponent(
                    tenant_id=tenant_id,
                    structure_id=structure.id,
                    **comp_data.dict()
                )
                db.add(structure_comp)
        
        db.commit()
        db.refresh(structure)
        
        return structure
    
    @staticmethod
    async def delete_structure(
        db: Session,
        structure_id: int,
        tenant_id: int,
        deleted_by: int
    ) -> bool:
        """Soft delete a salary structure"""
        
        structure = await SalaryStructureService.get_structure(db, structure_id, tenant_id)
        
        if not structure:
            return False
        
        # Check if structure is used by any active employee
        from backend.shared.database.payroll_models import EmployeeSalary
        active_assignments = db.query(EmployeeSalary).filter(
            and_(
                EmployeeSalary.structure_id == structure_id,
                EmployeeSalary.is_active == True,
                EmployeeSalary.is_deleted == False
            )
        ).count()
        
        if active_assignments > 0:
            raise ValueError(f"Cannot delete structure. {active_assignments} active employee(s) are using this structure.")
        
        structure.is_deleted = True
        structure.updated_by = deleted_by
        structure.updated_at = datetime.utcnow()
        
        db.commit()
        
        return True
    
    @staticmethod
    async def get_default_structure(
        db: Session,
        tenant_id: int
    ) -> Optional[SalaryStructure]:
        """Get the default salary structure"""
        return db.query(SalaryStructure).filter(
            and_(
                SalaryStructure.tenant_id == tenant_id,
                SalaryStructure.is_default == True,
                SalaryStructure.is_active == True,
                SalaryStructure.is_deleted == False
            )
        ).first()
