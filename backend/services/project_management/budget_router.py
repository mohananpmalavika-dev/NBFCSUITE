"""
Budget Management API Router
FastAPI routes for budget operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.shared.middleware.auth import get_current_user
from .budget_service import BudgetService
from .schemas import (
    ProjectBudgetCreate, ProjectBudgetUpdate, ProjectBudgetDetail,
    BudgetExpenseLineCreate, BudgetExpenseLineUpdate, BudgetExpenseLineResponse,
    PaginatedResponse, BudgetStatus
)


router = APIRouter(prefix="/budgets", tags=["Project Management - Budget"])


@router.post("/", response_model=ProjectBudgetDetail, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: ProjectBudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new project budget"""
    service = BudgetService(db, current_user["tenant_id"], str(current_user["id"]))
    budget = await service.create_budget(data)
    return await service.get_budget_detail(budget.id)


@router.get("/", response_model=PaginatedResponse)
async def list_budgets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    fiscal_year: Optional[str] = None,
    status: Optional[List[BudgetStatus]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List budgets with filters and pagination"""
    service = BudgetService(db, current_user["tenant_id"], str(current_user["id"]))
    
    items, total = await service.list_budgets(
        page=page,
        page_size=page_size,
        project_id=project_id,
        fiscal_year=fiscal_year,
        status=status
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{budget_id}", response_model=ProjectBudgetDetail)
async def get_budget(
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get budget details"""
    service = BudgetService(db, current_user["tenant_id"], str(current_user["id"]))
    budget = await service.get_budget_detail(budget_id)
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return budget


@router.put("/{budget_id}", response_model=ProjectBudgetDetail)
async def update_budget(
    budget_id: UUID,
    data: ProjectBudgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update budget"""
    service = BudgetService(db, current_user["tenant_id"], str(current_user["id"]))
    budget = await service.update_budget(budget_id, data)
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return await service.get_budget_detail(budget.id)


@router.post("/{budget_id}/approve", response_model=ProjectBudgetDetail)
async def approve_budget(
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve budget"""
    service = BudgetService(db, current_user["tenant_id"], str(current_user["id"]))
    budget = await service.approve_budget(budget_id)
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return await service.get_budget_detail(budget.id)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete budget"""
    service = BudgetService(db, current_user["tenant_id"], str(current_user["id"]))
    
    try:
        success = await service.delete_budget(budget_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Budget not found")
        
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========================================
# EXPENSE LINE ENDPOINTS
# ========================================

@router.post("/{budget_id}/expense-lines", response_model=BudgetExpenseLineResponse, status_code=status.HTTP_201_CREATED)
async def add_expense_line(
    budget_id: UUID,
    data: BudgetExpenseLineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add expense line to budget"""
    service = BudgetService(db, current_user["tenant_id"], str(current_user["id"]))
    expense_line = await service.add_expense_line(budget_id, data)
    
    return BudgetExpenseLineResponse(
        id=expense_line.id,
        budget_id=expense_line.budget_id,
        expense_category=expense_line.expense_category,
        description=expense_line.description,
        planned_amount=expense_line.planned_amount,
        committed_amount=expense_line.committed_amount,
        actual_amount=expense_line.actual_amount,
        variance=expense_line.variance,
        status=expense_line.status,
        expense_month=expense_line.expense_month
    )


@router.put("/expense-lines/{expense_line_id}", response_model=BudgetExpenseLineResponse)
async def update_expense_line(
    expense_line_id: UUID,
    data: BudgetExpenseLineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update expense line"""
    service = BudgetService(db, current_user["tenant_id"], str(current_user["id"]))
    expense_line = await service.update_expense_line(expense_line_id, data)
    
    if not expense_line:
        raise HTTPException(status_code=404, detail="Expense line not found")
    
    return BudgetExpenseLineResponse(
        id=expense_line.id,
        budget_id=expense_line.budget_id,
        expense_category=expense_line.expense_category,
        description=expense_line.description,
        planned_amount=expense_line.planned_amount,
        committed_amount=expense_line.committed_amount,
        actual_amount=expense_line.actual_amount,
        variance=expense_line.variance,
        status=expense_line.status,
        expense_month=expense_line.expense_month
    )


@router.delete("/expense-lines/{expense_line_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_line(
    expense_line_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete expense line"""
    service = BudgetService(db, current_user["tenant_id"], str(current_user["id"]))
    success = await service.delete_expense_line(expense_line_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Expense line not found")
    
    return None
