"""
CRM Lead Management Router
FastAPI endpoints for lead management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, get_current_tenant
from .service import CRMLeadService
from .schemas import (
    LeadCreate, LeadUpdate, LeadResponse, LeadListItem,
    LeadFilters, PaginatedLeadResponse, LeadDashboardStats,
    LeadAssignRequest, LeadQualifyRequest, LeadConvertRequest,
    LeadLostRequest, BulkLeadAssignRequest, BulkLeadStatusUpdate,
    LeadFollowUpCreate, LeadFollowUpUpdate, LeadFollowUpComplete,
    LeadFollowUpResponse, PaginatedFollowUpResponse,
    LeadActivityResponse, PaginatedActivityResponse,
    LeadStatusEnum, LeadSourceEnum, LeadPriorityEnum, LeadTemperatureEnum
)


router = APIRouter(prefix="/api/crm/leads", tags=["CRM - Lead Management"])


# ============================================================================
# LEAD CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_data: LeadCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """
    Create new lead from any channel
    Multi-channel lead capture with auto-scoring and assignment
    """
    service = CRMLeadService(db)
    
    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    lead = service.create_lead(
        lead_data=lead_data,
        user_id=current_user.id,
        tenant_id=tenant_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return lead


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get lead by ID"""
    service = CRMLeadService(db)
    lead = service.get_lead(lead_id, tenant_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead



@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Update lead details"""
    service = CRMLeadService(db)
    lead = service.update_lead(lead_id, lead_data, current_user.id, tenant_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.get("/", response_model=PaginatedLeadResponse)
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    source: Optional[LeadSourceEnum] = None,
    status: Optional[LeadStatusEnum] = None,
    priority: Optional[LeadPriorityEnum] = None,
    temperature: Optional[LeadTemperatureEnum] = None,
    assigned_to_user_id: Optional[int] = None,
    is_qualified: Optional[bool] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    created_from: Optional[date] = None,
    created_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """
    List leads with filters and pagination
    Supports search, status, source, priority, temperature filters
    """
    service = CRMLeadService(db)
    
    filters = LeadFilters(
        page=page,
        page_size=page_size,
        search=search,
        source=source,
        status=status,
        priority=priority,
        temperature=temperature,
        assigned_to_user_id=assigned_to_user_id,
        is_qualified=is_qualified,
        min_score=min_score,
        max_score=max_score,
        created_from=created_from,
        created_to=created_to
    )
    
    leads, total = service.list_leads(filters, tenant_id)
    
    return {
        "items": leads,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }



# ============================================================================
# LEAD ACTIONS
# ============================================================================

@router.post("/{lead_id}/assign", response_model=LeadResponse)
def assign_lead(
    lead_id: int,
    request_data: LeadAssignRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Assign lead to user"""
    service = CRMLeadService(db)
    lead = service.assign_lead(lead_id, request_data, current_user.id, tenant_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.post("/{lead_id}/qualify", response_model=LeadResponse)
def qualify_lead(
    lead_id: int,
    request_data: LeadQualifyRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Qualify or disqualify lead"""
    service = CRMLeadService(db)
    lead = service.qualify_lead(lead_id, request_data, current_user.id, tenant_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.post("/{lead_id}/convert")
def convert_lead(
    lead_id: int,
    request_data: LeadConvertRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Convert lead to customer"""
    service = CRMLeadService(db)
    result = service.convert_lead(lead_id, request_data, current_user.id, tenant_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return {"success": True, **result}



@router.post("/{lead_id}/mark-lost", response_model=LeadResponse)
def mark_lead_lost(
    lead_id: int,
    request_data: LeadLostRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Mark lead as lost"""
    service = CRMLeadService(db)
    lead = service.mark_lead_lost(lead_id, request_data, current_user.id, tenant_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.post("/{lead_id}/recalculate-score", response_model=LeadResponse)
def recalculate_score(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Manually recalculate lead score"""
    service = CRMLeadService(db)
    lead = service.recalculate_lead_score(lead_id, tenant_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/bulk/assign")
def bulk_assign_leads(
    request_data: BulkLeadAssignRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Bulk assign multiple leads to a user"""
    service = CRMLeadService(db)
    result = service.bulk_assign_leads(request_data, current_user.id, tenant_id)
    return result



# ============================================================================
# FOLLOW-UP MANAGEMENT
# ============================================================================

@router.post("/follow-ups", response_model=LeadFollowUpResponse, status_code=status.HTTP_201_CREATED)
def create_follow_up(
    follow_up_data: LeadFollowUpCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Create follow-up activity for a lead"""
    service = CRMLeadService(db)
    follow_up = service.create_follow_up(follow_up_data, current_user.id, tenant_id)
    
    if not follow_up:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return follow_up


@router.post("/follow-ups/{follow_up_id}/complete", response_model=LeadFollowUpResponse)
def complete_follow_up(
    follow_up_id: int,
    completion_data: LeadFollowUpComplete,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Complete a follow-up activity"""
    service = CRMLeadService(db)
    follow_up = service.complete_follow_up(follow_up_id, completion_data, current_user.id, tenant_id)
    
    if not follow_up:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )
    
    return follow_up


@router.get("/{lead_id}/follow-ups", response_model=PaginatedFollowUpResponse)
def get_lead_follow_ups(
    lead_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get all follow-ups for a lead"""
    service = CRMLeadService(db)
    follow_ups, total = service.get_lead_follow_ups(lead_id, page, page_size, tenant_id)
    
    return {
        "items": follow_ups,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }



@router.get("/follow-ups/overdue", response_model=List[LeadFollowUpResponse])
def get_overdue_follow_ups(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get overdue follow-ups"""
    service = CRMLeadService(db)
    
    # If no user_id provided, get for current user
    if user_id is None:
        user_id = current_user.id
    
    overdue = service.get_overdue_follow_ups(user_id, tenant_id)
    return overdue


# ============================================================================
# ACTIVITY LOG
# ============================================================================

@router.get("/{lead_id}/activities", response_model=PaginatedActivityResponse)
def get_lead_activities(
    lead_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get lead activity history"""
    service = CRMLeadService(db)
    activities, total = service.get_lead_activities(lead_id, page, page_size, tenant_id)
    
    return {
        "items": activities,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


# ============================================================================
# DASHBOARD & ANALYTICS
# ============================================================================

@router.get("/dashboard/stats", response_model=LeadDashboardStats)
def get_dashboard_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """
    Get lead dashboard statistics
    If user_id not provided, returns stats for current user
    """
    service = CRMLeadService(db)
    
    # If no user_id provided, get stats for current user
    if user_id is None:
        user_id = current_user.id
    
    stats = service.get_dashboard_stats(user_id, tenant_id)
    return stats
