"""
Budget Management Service Layer
Business logic for budget operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from backend.shared.database.project_management_models import (
    ProjectBudget, BudgetExpenseLine, BudgetStatus, ExpenseCategory, ExpenseStatus
)
from .schemas import (
    ProjectBudgetCreate, ProjectBudgetUpdate, ProjectBudgetDetail,
    BudgetExpenseLineCreate, BudgetExpenseLineUpdate, BudgetExpenseLineResponse
)


class BudgetService:
    """Service for budget management operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_budget_code(self) -> str:
        """Generate unique budget code: BDG-YYYY-XXXX"""
        year = datetime.now().year
        
        # Get count of budgets this year
        count_query = select(func.count(ProjectBudget.id)).where(
            and_(
                ProjectBudget.tenant_id == self.tenant_id,
                ProjectBudget.budget_code.like(f"BDG-{year}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        # Generate code
        sequence = str(count + 1).zfill(4)
        return f"BDG-{year}-{sequence}"
    
    async def create_budget(self, data: ProjectBudgetCreate) -> ProjectBudget:
        """Create new project budget"""
        
        # Generate budget code
        budget_code = await self.generate_budget_code()
        
        # Create budget
        budget = ProjectBudget(
            tenant_id=self.tenant_id,
            budget_code=budget_code,
            project_id=data.project_id,
            budget_name=data.budget_name,
            description=data.description,
            fiscal_year=data.fiscal_year,
            start_date=data.start_date,
            end_date=data.end_date,
            planned_budget=data.planned_budget,
            currency=data.currency,
            alert_threshold_percentage=data.alert_threshold_percentage,
            status=BudgetStatus.DRAFT,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        # Calculate available budget
        budget.available_budget = budget.planned_budget
        
        self.db.add(budget)
        await self.db.commit()
        await self.db.refresh(budget)
        
        return budget
    
    async def get_budget(self, budget_id: UUID) -> Optional[ProjectBudget]:
        """Get budget by ID"""
        query = select(ProjectBudget).where(
            and_(
                ProjectBudget.id == budget_id,
                ProjectBudget.tenant_id == self.tenant_id
            )
        ).options(
            joinedload(ProjectBudget.project),
            joinedload(ProjectBudget.approved_by),
            selectinload(ProjectBudget.expense_lines)
        )
        
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_budget_detail(self, budget_id: UUID) -> Optional[ProjectBudgetDetail]:
        """Get detailed budget view"""
        budget = await self.get_budget(budget_id)
        
        if not budget:
            return None
        
        # Build expense lines
        expense_lines = [
            BudgetExpenseLineResponse(
                id=line.id,
                budget_id=line.budget_id,
                expense_category=line.expense_category,
                description=line.description,
                planned_amount=line.planned_amount,
                committed_amount=line.committed_amount,
                actual_amount=line.actual_amount,
                variance=line.variance,
                status=line.status,
                expense_month=line.expense_month
            )
            for line in budget.expense_lines
        ]
        
        return ProjectBudgetDetail(
            id=budget.id,
            budget_code=budget.budget_code,
            project_id=budget.project_id,
            project_name=budget.project.project_name if budget.project else "",
            budget_name=budget.budget_name,
            description=budget.description,
            fiscal_year=budget.fiscal_year,
            start_date=budget.start_date,
            end_date=budget.end_date,
            planned_budget=budget.planned_budget,
            approved_budget=budget.approved_budget,
            revised_budget=budget.revised_budget,
            committed_cost=budget.committed_cost,
            actual_cost=budget.actual_cost,
            available_budget=budget.available_budget,
            budget_variance=budget.budget_variance,
            variance_percentage=budget.variance_percentage,
            status=budget.status,
            currency=budget.currency,
            alert_threshold_percentage=budget.alert_threshold_percentage,
            is_threshold_exceeded=budget.is_threshold_exceeded,
            expense_lines=expense_lines,
            created_at=budget.created_at,
            updated_at=budget.updated_at
        )
    
    async def list_budgets(
        self,
        page: int = 1,
        page_size: int = 20,
        project_id: Optional[UUID] = None,
        fiscal_year: Optional[str] = None,
        status: Optional[List[BudgetStatus]] = None
    ) -> Tuple[List[ProjectBudgetDetail], int]:
        """List budgets with filters and pagination"""
        
        # Build base query
        query = select(ProjectBudget).where(ProjectBudget.tenant_id == self.tenant_id)
        
        # Apply filters
        if project_id:
            query = query.where(ProjectBudget.project_id == project_id)
        
        if fiscal_year:
            query = query.where(ProjectBudget.fiscal_year == fiscal_year)
        
        if status:
            query = query.where(ProjectBudget.status.in_(status))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        query = query.options(
            joinedload(ProjectBudget.project),
            selectinload(ProjectBudget.expense_lines)
        ).order_by(desc(ProjectBudget.created_at)).offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        budgets = result.unique().scalars().all()
        
        # Build response items
        items = []
        for budget in budgets:
            expense_lines = [
                BudgetExpenseLineResponse(
                    id=line.id,
                    budget_id=line.budget_id,
                    expense_category=line.expense_category,
                    description=line.description,
                    planned_amount=line.planned_amount,
                    committed_amount=line.committed_amount,
                    actual_amount=line.actual_amount,
                    variance=line.variance,
                    status=line.status,
                    expense_month=line.expense_month
                )
                for line in budget.expense_lines
            ]
            
            items.append(ProjectBudgetDetail(
                id=budget.id,
                budget_code=budget.budget_code,
                project_id=budget.project_id,
                project_name=budget.project.project_name if budget.project else "",
                budget_name=budget.budget_name,
                description=budget.description,
                fiscal_year=budget.fiscal_year,
                start_date=budget.start_date,
                end_date=budget.end_date,
                planned_budget=budget.planned_budget,
                approved_budget=budget.approved_budget,
                revised_budget=budget.revised_budget,
                committed_cost=budget.committed_cost,
                actual_cost=budget.actual_cost,
                available_budget=budget.available_budget,
                budget_variance=budget.budget_variance,
                variance_percentage=budget.variance_percentage,
                status=budget.status,
                currency=budget.currency,
                alert_threshold_percentage=budget.alert_threshold_percentage,
                is_threshold_exceeded=budget.is_threshold_exceeded,
                expense_lines=expense_lines,
                created_at=budget.created_at,
                updated_at=budget.updated_at
            ))
        
        return items, total
    
    async def update_budget(self, budget_id: UUID, data: ProjectBudgetUpdate) -> Optional[ProjectBudget]:
        """Update budget"""
        budget = await self.get_budget(budget_id)
        
        if not budget:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(budget, field, value)
        
        # Recalculate available budget and variance
        budget.available_budget = (budget.approved_budget or budget.planned_budget) - budget.committed_cost - budget.actual_cost
        budget.budget_variance = (budget.approved_budget or budget.planned_budget) - budget.actual_cost
        
        # Calculate variance percentage
        budget_amount = budget.approved_budget or budget.planned_budget
        if budget_amount > 0:
            budget.variance_percentage = (budget.budget_variance / budget_amount) * 100
        
        # Check if threshold exceeded
        if budget_amount > 0:
            utilization = (budget.actual_cost / budget_amount) * 100
            budget.is_threshold_exceeded = utilization >= budget.alert_threshold_percentage
        
        budget.updated_by = self.user_id
        budget.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(budget)
        
        return budget
    
    async def approve_budget(self, budget_id: UUID) -> Optional[ProjectBudget]:
        """Approve budget"""
        budget = await self.get_budget(budget_id)
        
        if not budget:
            return None
        
        budget.status = BudgetStatus.APPROVED
        budget.approved_budget = budget.planned_budget
        budget.approved_by_id = self.user_id
        budget.approved_date = datetime.utcnow()
        budget.updated_by = self.user_id
        budget.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(budget)
        
        return budget
    
    async def delete_budget(self, budget_id: UUID) -> bool:
        """Delete budget"""
        budget = await self.get_budget(budget_id)
        
        if not budget:
            return False
        
        # Only allow deletion if in DRAFT status
        if budget.status != BudgetStatus.DRAFT:
            raise ValueError("Cannot delete budget that is approved or active")
        
        await self.db.delete(budget)
        await self.db.commit()
        
        return True
    
    # ========================================
    # EXPENSE LINE OPERATIONS
    # ========================================
    
    async def add_expense_line(self, budget_id: UUID, data: BudgetExpenseLineCreate) -> BudgetExpenseLine:
        """Add expense line to budget"""
        
        expense_line = BudgetExpenseLine(
            tenant_id=self.tenant_id,
            budget_id=budget_id,
            expense_category=data.expense_category,
            description=data.description,
            planned_amount=data.planned_amount,
            expense_month=data.expense_month,
            reference_number=data.reference_number,
            vendor_name=data.vendor_name,
            status=ExpenseStatus.PLANNED,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(expense_line)
        await self.db.commit()
        await self.db.refresh(expense_line)
        
        # Recalculate budget totals
        await self._recalculate_budget_totals(budget_id)
        
        return expense_line
    
    async def update_expense_line(
        self,
        expense_line_id: UUID,
        data: BudgetExpenseLineUpdate
    ) -> Optional[BudgetExpenseLine]:
        """Update expense line"""
        query = select(BudgetExpenseLine).where(
            and_(
                BudgetExpenseLine.id == expense_line_id,
                BudgetExpenseLine.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        expense_line = result.scalar_one_or_none()
        
        if not expense_line:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense_line, field, value)
        
        # Calculate variance
        expense_line.variance = expense_line.planned_amount - expense_line.actual_amount
        
        expense_line.updated_by = self.user_id
        expense_line.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(expense_line)
        
        # Recalculate budget totals
        await self._recalculate_budget_totals(expense_line.budget_id)
        
        return expense_line
    
    async def delete_expense_line(self, expense_line_id: UUID) -> bool:
        """Delete expense line"""
        query = select(BudgetExpenseLine).where(
            and_(
                BudgetExpenseLine.id == expense_line_id,
                BudgetExpenseLine.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        expense_line = result.scalar_one_or_none()
        
        if not expense_line:
            return False
        
        budget_id = expense_line.budget_id
        
        await self.db.delete(expense_line)
        await self.db.commit()
        
        # Recalculate budget totals
        await self._recalculate_budget_totals(budget_id)
        
        return True
    
    async def _recalculate_budget_totals(self, budget_id: UUID):
        """Recalculate budget totals from expense lines"""
        # Get all expense lines for this budget
        query = select(
            func.sum(BudgetExpenseLine.committed_amount),
            func.sum(BudgetExpenseLine.actual_amount)
        ).where(
            and_(
                BudgetExpenseLine.budget_id == budget_id,
                BudgetExpenseLine.tenant_id == self.tenant_id
            )
        )
        
        result = await self.db.execute(query)
        row = result.first()
        
        committed_total = row[0] or Decimal('0.00')
        actual_total = row[1] or Decimal('0.00')
        
        # Update budget
        budget_query = select(ProjectBudget).where(
            and_(
                ProjectBudget.id == budget_id,
                ProjectBudget.tenant_id == self.tenant_id
            )
        )
        budget_result = await self.db.execute(budget_query)
        budget = budget_result.scalar_one_or_none()
        
        if budget:
            budget.committed_cost = committed_total
            budget.actual_cost = actual_total
            
            # Recalculate available budget and variance
            budget.available_budget = (budget.approved_budget or budget.planned_budget) - committed_total - actual_total
            budget.budget_variance = (budget.approved_budget or budget.planned_budget) - actual_total
            
            # Calculate variance percentage
            budget_amount = budget.approved_budget or budget.planned_budget
            if budget_amount > 0:
                budget.variance_percentage = (budget.budget_variance / budget_amount) * 100
            
            # Check if threshold exceeded
            if budget_amount > 0:
                utilization = (actual_total / budget_amount) * 100
                budget.is_threshold_exceeded = utilization >= budget.alert_threshold_percentage
            
            # Update status if exceeded
            if budget.is_threshold_exceeded and budget.status == BudgetStatus.ACTIVE:
                budget.status = BudgetStatus.EXCEEDED
            
            await self.db.commit()
