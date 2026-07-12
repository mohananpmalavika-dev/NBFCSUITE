"""
CRM Opportunity Management Router
FastAPI endpoints for opportunity management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_current_tenant
from .opportunity_service import OpportunityService
from .opportunity_schemas import (
    OpportunityCreate, OpportunityUpdate, OpportunityResponse, OpportunityListItem,
    OpportunityFilters, PaginatedOpportunityResponse,
    StageTransitionRequest, StageHistoryResponse,
    OpportunityWinRequest, OpportunityLossRequest,
    OpportunityActivityCreate, OpportunityActivityUpdate, OpportunityActivityResponse,
    PaginatedActivityResponse,
    OpportunityProductCreate, OpportunityProductUpdate, OpportunityProductResponse,
    OpportunityCompetitorCreate, OpportunityCompetitorUpdate, OpportunityCompetitorResponse,
    OpportunityNoteCreate, OpportunityNoteUpdate, OpportunityNoteResponse,
    OpportunityDashboardStats, PipelineAnalytics, WinLossAnalysis, ForecastData,
    BulkOpportunityUpdate, BulkDeleteRequest,
    OpportunityStageEnum, OpportunityTypeEnum, OpportunitySourceEnum,
    OpportunityPriorityEnum, LossReasonEnum
)


router = APIRouter(prefix="/api/crm/opportunities", tags=["CRM - Opportunity Management"])


# ============================================================================
# OPPORTUNITY CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    opp_data: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Create new opportunity
    Captures deal from lead or direct prospecting
    """
    service = OpportunityService(db)
    
    opportunity = service.create_opportunity(
        opp_data=opp_data,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    return opportunity



@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get opportunity by ID"""
    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id, tenant_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(
    opportunity_id: int,
    opp_data: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Update opportunity details"""
    service = OpportunityService(db)
    opportunity = service.update_opportunity(
        opportunity_id, opp_data, current_user.id, tenant_id
    )
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity


@router.get("/", response_model=PaginatedOpportunityResponse)
def list_opportunities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    stage: Optional[OpportunityStageEnum] = None,
    opportunity_type: Optional[OpportunityTypeEnum] = None,
    source: Optional[OpportunitySourceEnum] = None,
    priority: Optional[OpportunityPriorityEnum] = None,
    owner_user_id: Optional[int] = None,
    is_won: Optional[bool] = None,
    is_lost: Optional[bool] = None,
    is_active: Optional[bool] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    min_probability: Optional[int] = None,
    max_probability: Optional[int] = None,
    close_date_from: Optional[date] = None,
    close_date_to: Optional[date] = None,
    created_from: Optional[date] = None,
    created_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    List opportunities with filters and pagination
    Supports search, stage, type, source, priority, and value filters
    """
    service = OpportunityService(db)
    
    filters = OpportunityFilters(
        page=page,
        page_size=page_size,
        search=search,
        stage=stage,
        opportunity_type=opportunity_type,
        source=source,
        priority=priority,
        owner_user_id=owner_user_id,
        is_won=is_won,
        is_lost=is_lost,
        is_active=is_active,
        min_value=min_value,
        max_value=max_value,
        min_probability=min_probability,
        max_probability=max_probability,
        close_date_from=close_date_from,
        close_date_to=close_date_to,
        created_from=created_from,
        created_to=created_to
    )
    
    opportunities, total = service.list_opportunities(filters, tenant_id)
    
    return {
        "items": opportunities,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


# ============================================================================
# PIPELINE STAGE MANAGEMENT
# ============================================================================

@router.post("/{opportunity_id}/transition", response_model=OpportunityResponse)
def transition_stage(
    opportunity_id: int,
    transition: StageTransitionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Move opportunity to new pipeline stage
    Tracks stage history and updates probability
    """
    service = OpportunityService(db)
    opportunity = service.transition_stage(
        opportunity_id, transition, current_user.id, tenant_id
    )
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity



@router.get("/{opportunity_id}/stage-history", response_model=List[StageHistoryResponse])
def get_stage_history(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get opportunity stage transition history"""
    from backend.shared.database.crm_opportunity_models import OpportunityStageHistory
    
    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id, tenant_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    history = db.query(OpportunityStageHistory).filter(
        OpportunityStageHistory.opportunity_id == opportunity_id,
        OpportunityStageHistory.tenant_id == tenant_id
    ).order_by(OpportunityStageHistory.stage_entered_date.desc()).all()
    
    return history


# ============================================================================
# WIN/LOSS MANAGEMENT
# ============================================================================

@router.post("/{opportunity_id}/mark-won", response_model=OpportunityResponse)
def mark_opportunity_won(
    opportunity_id: int,
    win_request: OpportunityWinRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Mark opportunity as won
    Records won value and closes the deal
    """
    service = OpportunityService(db)
    opportunity = service.mark_won(
        opportunity_id, win_request, current_user.id, tenant_id
    )
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity


@router.post("/{opportunity_id}/mark-lost", response_model=OpportunityResponse)
def mark_opportunity_lost(
    opportunity_id: int,
    loss_request: OpportunityLossRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Mark opportunity as lost
    Records loss reason and competitor for analysis
    """
    service = OpportunityService(db)
    opportunity = service.mark_lost(
        opportunity_id, loss_request, current_user.id, tenant_id
    )
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity



# ============================================================================
# ACTIVITY MANAGEMENT
# ============================================================================

@router.post("/activities", response_model=OpportunityActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_data: OpportunityActivityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Create opportunity activity
    Logs calls, meetings, emails, demos, etc.
    """
    service = OpportunityService(db)
    activity = service.create_activity(activity_data, current_user.id, tenant_id)
    
    return activity


@router.get("/{opportunity_id}/activities", response_model=PaginatedActivityResponse)
def get_opportunity_activities(
    opportunity_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get all activities for an opportunity"""
    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id, tenant_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    activities, total = service.get_opportunity_activities(
        opportunity_id, tenant_id, page, page_size
    )
    
    return {
        "items": activities,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


# ============================================================================
# PRODUCT MANAGEMENT
# ============================================================================

@router.post("/products", response_model=OpportunityProductResponse, status_code=status.HTTP_201_CREATED)
def add_product(
    product_data: OpportunityProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Add product/service to opportunity"""
    service = OpportunityService(db)
    product = service.add_product(product_data, current_user.id, tenant_id)
    
    return product


@router.get("/{opportunity_id}/products", response_model=List[OpportunityProductResponse])
def get_opportunity_products(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get all products in an opportunity"""
    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id, tenant_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    products = service.get_opportunity_products(opportunity_id, tenant_id)
    
    return products



# ============================================================================
# COMPETITOR MANAGEMENT
# ============================================================================

@router.post("/competitors", response_model=OpportunityCompetitorResponse, status_code=status.HTTP_201_CREATED)
def add_competitor(
    competitor_data: OpportunityCompetitorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Add competitor to opportunity for competitive analysis"""
    service = OpportunityService(db)
    competitor = service.add_competitor(competitor_data, current_user.id, tenant_id)
    
    return competitor


@router.get("/{opportunity_id}/competitors", response_model=List[OpportunityCompetitorResponse])
def get_opportunity_competitors(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """Get all competitors for an opportunity"""
    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id, tenant_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    competitors = service.get_opportunity_competitors(opportunity_id, tenant_id)
    
    return competitors


# ============================================================================
# DASHBOARD & ANALYTICS
# ============================================================================

@router.get("/dashboard/stats", response_model=OpportunityDashboardStats)
def get_dashboard_stats(
    owner_user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Get opportunity dashboard statistics
    Pipeline metrics, win/loss rates, activity stats
    """
    service = OpportunityService(db)
    stats = service.get_dashboard_stats(tenant_id, owner_user_id)
    
    return stats


@router.get("/analytics/pipeline", response_model=List[PipelineAnalytics])
def get_pipeline_analytics(
    owner_user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Get pipeline analytics by stage
    Stage-wise counts, values, conversion rates
    """
    service = OpportunityService(db)
    analytics = service.get_pipeline_analytics(tenant_id, owner_user_id)
    
    return analytics


@router.get("/analytics/win-loss", response_model=WinLossAnalysis)
def get_win_loss_analysis(
    period: str = Query(..., description="Period format: YYYY-Q# or YYYY-MM"),
    owner_user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Get win/loss analysis for a period
    Win rates, loss reasons, top competitors
    """
    service = OpportunityService(db)
    analysis = service.get_win_loss_analysis(tenant_id, period, owner_user_id)
    
    return analysis



# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/bulk/update", status_code=status.HTTP_200_OK)
def bulk_update_opportunities(
    bulk_update: BulkOpportunityUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Bulk update opportunities
    Change owner, priority, stage, or tags for multiple opportunities
    """
    service = OpportunityService(db)
    updated_count = 0
    
    for opp_id in bulk_update.opportunity_ids:
        opportunity = service.get_opportunity(opp_id, tenant_id)
        if not opportunity:
            continue
        
        update_data = {}
        if bulk_update.owner_user_id:
            update_data['owner_user_id'] = bulk_update.owner_user_id
        if bulk_update.priority:
            update_data['priority'] = bulk_update.priority
        if bulk_update.tags:
            update_data['tags'] = bulk_update.tags
        
        if update_data:
            for key, value in update_data.items():
                setattr(opportunity, key, value)
            updated_count += 1
        
        # Handle stage change separately
        if bulk_update.stage:
            from .opportunity_schemas import StageTransitionRequest
            transition = StageTransitionRequest(
                to_stage=bulk_update.stage,
                notes="Bulk stage update"
            )
            service.transition_stage(opp_id, transition, current_user.id, tenant_id)
            updated_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Updated {updated_count} opportunities",
        "updated_count": updated_count
    }


@router.delete("/bulk/delete", status_code=status.HTTP_200_OK)
def bulk_delete_opportunities(
    bulk_delete: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """
    Bulk delete opportunities
    Soft delete multiple opportunities at once
    """
    from backend.shared.database.crm_opportunity_models import Opportunity
    
    deleted_count = 0
    
    for opp_id in bulk_delete.opportunity_ids:
        opportunity = db.query(Opportunity).filter(
            Opportunity.id == opp_id,
            Opportunity.tenant_id == tenant_id
        ).first()
        
        if opportunity:
            db.delete(opportunity)
            deleted_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Deleted {deleted_count} opportunities",
        "deleted_count": deleted_count
    }
