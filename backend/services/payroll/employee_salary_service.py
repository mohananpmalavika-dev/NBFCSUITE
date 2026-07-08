"""
Employee Salary Service
Handles employee salary assignments and component calculations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from backend.shared.database.payroll_models import (
    EmployeeSalary, EmployeeSalaryComponent, SalaryStructure, 
    SalaryStructureComponent, SalaryComponent, ComponentType
)
from backend.services.payroll.schemas import (
    EmployeeSalaryCreate, EmployeeSalaryUpdate,
    EmployeeSalaryResponse, EmployeeSalaryListResponse
)


class EmployeeSalaryService:
    """Service class for employee salary operations"""
    
    @staticmethod
    async def calculate_component_amount(
        base_amount: Decimal,
        calculation_type: str,
        default_value: Optional[Decimal],
        percentage: Optional[Decimal]
    ) -> Decimal:
        """Calculate component amount based on calculation type"""
        
        if calculation_type == "FIXED":
            return default_value or Decimal("0.00")
        elif calculation_type == "PERCENTAGE_OF_BASIC":
            return (base_amount * (percentage or Decimal("0.00")) / 100).quantize(Decimal('0.01'))
        elif calculation_type == "PERCENTAGE_OF_GROSS":
            return (base_amount * (percentage or Decimal("0.00")) / 100).quantize(Decimal('0.01'))
        elif calculation_type == "PERCENTAGE_OF_CTC":
            return (base_amount * (percentage or Decimal("0.00")) / 100).quantize(Decimal('0.01'))
        else:
            return Decimal("0.00")
    
    @staticmethod
    async def assign_salary(
        db: Session,
        salary_data: EmployeeSalaryCreate,
        created_by: int
    ) -> EmployeeSalary:
        """Assign salary structure to an employee"""
        
        # Check if employee already has an active salary
        existing = db.query(EmployeeSalary).filter(
            and_(
                EmployeeSalary.tenant_id == salary_data.tenant_id,
                EmployeeSalary.employee_id == salary_data.employee_id,
                EmployeeSalary.is_active == True,
                EmployeeSalary.is_deleted == False
            )
        ).first()
        
        if existing:
            # Deactivate existing salary
            existing.is_active = False
            existing.effective_to = salary_data.effective_from
            existing.updated_by = created_by
            existing.updated_at = datetime.utcnow()
        
        # Create new salary assignment
        salary_dict = salary_data.dict(exclude={'components'})
        employee_salary = EmployeeSalary(
            **salary_dict,
            created_by=created_by,
            updated_by=created_by
        )
        
        db.add(employee_salary)
        db.flush()
        
        # Add component values
        for comp_data in salary_data.components:
            emp_comp = EmployeeSalaryComponent(
                tenant_id=salary_data.tenant_id,
                employee_salary_id=employee_salary.id,
                **comp_data.dict()
            )
            db.add(emp_comp)
        
        db.commit()
        db.refresh(employee_salary)
        
        return employee_salary
    
    @staticmethod
    async def get_employee_salary(
        db: Session,
        salary_id: int,
        tenant_id: int
    ) -> Optional[EmployeeSalary]:
        """Get employee salary by ID"""
        salary = db.query(EmployeeSalary).filter(
            and_(
                EmployeeSalary.id == salary_id,
                EmployeeSalary.tenant_id == tenant_id,
                EmployeeSalary.is_deleted == False
            )
        ).first()
        
        if salary:
            # Load components
            components = db.query(EmployeeSalaryComponent).filter(
                and_(
                    EmployeeSalaryComponent.employee_salary_id == salary_id,
                    EmployeeSalaryComponent.is_deleted == False
                )
            ).all()
            
            salary.components = components
        
        return salary
    
    @staticmethod
    async def get_employee_current_salary(
        db: Session,
        employee_id: int,
        tenant_id: int,
        as_of_date: Optional[date] = None
    ) -> Optional[EmployeeSalary]:
        """Get employee's current active salary"""
        
        if as_of_date is None:
            as_of_date = date.today()
        
        salary = db.query(EmployeeSalary).filter(
            and_(
                EmployeeSalary.tenant_id == tenant_id,
                EmployeeSalary.employee_id == employee_id,
                EmployeeSalary.is_active == True,
                EmployeeSalary.effective_from <= as_of_date,
                EmployeeSalary.is_deleted == False
            )
        ).filter(
            (EmployeeSalary.effective_to.is_(None)) |
            (EmployeeSalary.effective_to >= as_of_date)
        ).first()
        
        if salary:
            # Load components
            components = db.query(EmployeeSalaryComponent).filter(
                and_(
                    EmployeeSalaryComponent.employee_salary_id == salary.id,
                    EmployeeSalaryComponent.is_deleted == False
                )
            ).all()
            
            salary.components = components
        
        return salary
    
    @staticmethod
    async def list_employee_salaries(
        db: Session,
        tenant_id: int,
        employee_id: Optional[int] = None,
        structure_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> EmployeeSalaryListResponse:
        """List employee salaries with filters"""
        
        query = db.query(EmployeeSalary).filter(
            and_(
                EmployeeSalary.tenant_id == tenant_id,
                EmployeeSalary.is_deleted == False
            )
        )
        
        # Apply filters
        if employee_id:
            query = query.filter(EmployeeSalary.employee_id == employee_id)
        
        if structure_id:
            query = query.filter(EmployeeSalary.structure_id == structure_id)
        
        if is_active is not None:
            query = query.filter(EmployeeSalary.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        salaries = query.order_by(
            EmployeeSalary.effective_from.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return EmployeeSalaryListResponse(
            items=salaries,
            total=total,
            page=page,
            page_size=page_size
        )
    
    @staticmethod
    async def update_employee_salary(
        db: Session,
        salary_id: int,
        tenant_id: int,
        salary_data: EmployeeSalaryUpdate,
        updated_by: int
    ) -> Optional[EmployeeSalary]:
        """Update employee salary"""
        
        salary = await EmployeeSalaryService.get_employee_salary(db, salary_id, tenant_id)
        
        if not salary:
            return None
        
        # Update fields
        update_data = salary_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(salary, field, value)
        
        salary.updated_by = updated_by
        salary.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(salary)
        
        return salary
    
    @staticmethod
    async def calculate_salary_from_structure(
        db: Session,
        structure_id: int,
        ctc_annual: Decimal,
        tenant_id: int
    ) -> dict:
        """Calculate salary breakdown from structure and CTC"""
        
        # Get structure with components
        structure = db.query(SalaryStructure).filter(
            and_(
                SalaryStructure.id == structure_id,
                SalaryStructure.tenant_id == tenant_id,
                SalaryStructure.is_deleted == False
            )
        ).first()
        
        if not structure:
            raise ValueError("Salary structure not found")
        
        # Get structure components
        structure_components = db.query(SalaryStructureComponent).filter(
            and_(
                SalaryStructureComponent.structure_id == structure_id,
                SalaryStructureComponent.is_deleted == False
            )
        ).order_by(SalaryStructureComponent.display_order).all()
        
        # Calculate components
        components = []
        basic_salary = Decimal("0.00")
        gross_monthly = Decimal("0.00")
        total_deductions = Decimal("0.00")
        
        for struct_comp in structure_components:
            component = db.query(SalaryComponent).filter(
                SalaryComponent.id == struct_comp.component_id
            ).first()
            
            if not component:
                continue
            
            # Calculate amount
            if component.component_type == ComponentType.EARNING:
                if "BASIC" in component.component_code.upper():
                    # Basic is typically a percentage of CTC
                    monthly_amount = await EmployeeSalaryService.calculate_component_amount(
                        ctc_annual / 12, struct_comp.calculation_type,
                        struct_comp.default_value, struct_comp.percentage
                    )
                    basic_salary = monthly_amount
                else:
                    monthly_amount = await EmployeeSalaryService.calculate_component_amount(
                        basic_salary, struct_comp.calculation_type,
                        struct_comp.default_value, struct_comp.percentage
                    )
                
                gross_monthly += monthly_amount
            
            elif component.component_type == ComponentType.DEDUCTION:
                monthly_amount = await EmployeeSalaryService.calculate_component_amount(
                    basic_salary if "BASIC" in struct_comp.calculation_type else gross_monthly,
                    struct_comp.calculation_type,
                    struct_comp.default_value, struct_comp.percentage
                )
                total_deductions += monthly_amount
            
            else:  # EMPLOYER_CONTRIBUTION
                monthly_amount = await EmployeeSalaryService.calculate_component_amount(
                    basic_salary, struct_comp.calculation_type,
                    struct_comp.default_value, struct_comp.percentage
                )
            
            components.append({
                "component_id": component.id,
                "component_code": component.component_code,
                "component_name": component.component_name,
                "component_type": component.component_type,
                "monthly_amount": monthly_amount,
                "annual_amount": monthly_amount * 12
            })
        
        net_monthly = gross_monthly - total_deductions
        
        return {
            "ctc_annual": ctc_annual,
            "gross_monthly": gross_monthly,
            "net_monthly": net_monthly,
            "basic_salary": basic_salary,
            "total_deductions": total_deductions,
            "components": components
        }
