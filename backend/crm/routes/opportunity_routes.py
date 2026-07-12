"""
CRM Opportunity Management Routes
FastAPI endpoints for opportunity operations, pipeline tracking, and analytics
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.schemas.crm_opportunity_schemas import (
    CRMOpportunityCreate, CRMOpportunityUpdate,
    CRMOpportunityActivityCreate, CRMOpportunityActivityUpdate,
    CRMOpportunityStageTransition, CRMOpportunityCloseWon, CRMOpportunityCloseLost
)
from backend.crm.services.opportunity_service import CRMOpportunityService
from backend.crm.services.opportunity_pipeline_service import CRMPipelineService

router = APIRouter(prefix="/crm/opportunities", tags=["CRM - Opportunity Management"])


# ============================================================================
# OPPORTUNITY CRUD ROUTES
# ============================================================================

@router.post("", response_model=dict, status_code=201)
def create_opportunity(
    opportunity_data: CRMOpportunityCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new sales opportunity
    
    - **opportunity_name**: Name of the opportunity (required)
    - **account_id**: Associated account ID (required)
    - **stage**: Current stage in pipeline (default: prospecting)
    - **estimated_value**: Expected deal value
    - **probability**: Win probability percentage (0-100)
    """
    user_id = current_user.get("id")
    return CRMOpportunityService.create_opportunity(db, opportunity_data, tenant_id, user_id)


@router.get("", response_model=dict)
def list_opportunities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in opportunity name, number, description"),
    stage: Optional[str] = Query(None, description="Filter by stage"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    opportunity_owner_id: Optional[UUID] = Query(None, description="Filter by owner"),
    account_id: Optional[UUID] = Query(None, description="Filter by account"),
    from_date: Optional[datetime] = Query(None, description="Filter from expected close date"),
    to_date: Optional[datetime] = Query(None, description="Filter to expected close date"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    List all opportunities with pagination and filters
    
    Supports:
    - Pagination with skip/limit
    - Search by name, number, description
    - Filter by stage, priority, owner, account, date range
    """
    return CRMOpportunityService.list_opportunities(
        db, tenant_id, skip, limit, search, stage, priority,
        opportunity_owner_id, account_id, from_date, to_date
    )


@router.get("/{opportunity_id}", response_model=dict)
def get_opportunity(
    opportunity_id: UUID = Path(..., description="Opportunity ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed opportunity information
    
    Includes products, activities, and complete history
    """
    return CRMOpportunityService.get_opportunity(db, opportunity_id, tenant_id)


@router.put("/{opportunity_id}", response_model=dict)
def update_opportunity(
    opportunity_id: UUID = Path(..., description="Opportunity ID"),
    opportunity_data: CRMOpportunityUpdate = ...,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Update opportunity details
    
    All fields are optional. Only provided fields will be updated.
    """
    user_id = current_user.get("id")
    return CRMOpportunityService.update_opportunity(db, opportunity_id, opportunity_data, tenant_id, user_id)


@router.delete("/{opportunity_id}", response_model=dict)
def delete_opportunity(
    opportunity_id: UUID = Path(..., description="Opportunity ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Delete an opportunity (soft delete)"""
    user_id = current_user.get("id")
    return CRMOpportunityService.delete_opportunity(db, opportunity_id, tenant_id, user_id)


# ============================================================================
# PIPELINE & ANALYTICS ROUTES
# ============================================================================

@router.get("/pipeline/overview", response_model=dict)
def get_pipeline_overview(
    owner_id: Optional[UUID] = Query(None, description="Filter by owner"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get sales pipeline overview with stage-wise breakdown
    
    Includes:
    - Total opportunities and values by stage
    - Weighted pipeline value
    - Average deal size
    - Stage progression metrics
    """
    return CRMPipelineService.get_pipeline_overview(db, tenant_id, owner_id, from_date, to_date)


@router.get("/analytics/win-loss", response_model=dict)
def get_win_loss_analysis(
    owner_id: Optional[UUID] = Query(None, description="Filter by owner"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive win/loss analysis
    
    Includes:
    - Win rate and closed deal counts
    - Average deal sizes for won/lost
    - Loss reasons breakdown
    - Top competitors
    - Revenue impact analysis
    """
    return CRMPipelineService.get_win_loss_analysis(db, tenant_id, owner_id, from_date, to_date)
