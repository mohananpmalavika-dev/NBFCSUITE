"""
CRM Marketing Automation Routes
FastAPI endpoints for campaign management, segmentation, and landing pages
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.schemas.crm_marketing_schemas import (
    MarketingCampaignCreate, MarketingCampaignUpdate,
    CustomerSegmentCreate, CustomerSegmentUpdate,
    LandingPageCreate, LandingPageUpdate,
    CampaignLaunchRequest, CampaignPauseRequest
)
from backend.crm.services.marketing_service import (
    MarketingCampaignService, CustomerSegmentService, LandingPageService
)

router = APIRouter(prefix="/crm/marketing", tags=["CRM - Marketing Automation"])


# ============================================================================
# CAMPAIGN ROUTES
# ============================================================================

@router.post("/campaigns", response_model=dict, status_code=201)
def create_campaign(
    campaign_data: MarketingCampaignCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new marketing campaign
    
    - **campaign_name**: Campaign name (required)
    - **campaign_type**: email, sms, whatsapp, push_notification, social_media, multi_channel
    - **status**: draft, scheduled, running, paused, completed, cancelled, failed
    """
    user_id = current_user.get("id")
    return MarketingCampaignService.create_campaign(db, campaign_data, tenant_id, user_id)


@router.get("/campaigns", response_model=dict)
def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    campaign_owner_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List all marketing campaigns with filters"""
    return MarketingCampaignService.list_campaigns(
        db, tenant_id, skip, limit, search, status, campaign_type, campaign_owner_id
    )



@router.get("/campaigns/{campaign_id}", response_model=dict)
def get_campaign(
    campaign_id: UUID = Path(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get campaign details by ID"""
    return MarketingCampaignService.get_campaign(db, campaign_id, tenant_id)


@router.put("/campaigns/{campaign_id}", response_model=dict)
def update_campaign(
    campaign_id: UUID = Path(...),
    campaign_data: MarketingCampaignUpdate = ...,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Update campaign details"""
    user_id = current_user.get("id")
    return MarketingCampaignService.update_campaign(db, campaign_id, campaign_data, tenant_id, user_id)


@router.delete("/campaigns/{campaign_id}", response_model=dict)
def delete_campaign(
    campaign_id: UUID = Path(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Delete a campaign (soft delete)"""
    user_id = current_user.get("id")
    return MarketingCampaignService.delete_campaign(db, campaign_id, tenant_id, user_id)


@router.post("/campaigns/{campaign_id}/launch", response_model=dict)
def launch_campaign(
    campaign_id: UUID = Path(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Launch a campaign"""
    user_id = current_user.get("id")
    return MarketingCampaignService.launch_campaign(db, campaign_id, tenant_id, user_id)


# ============================================================================
# SEGMENT ROUTES
# ============================================================================

@router.post("/segments", response_model=dict, status_code=201)
def create_segment(
    segment_data: CustomerSegmentCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new customer segment
    
    - **segment_name**: Segment name (required)
    - **segmentation_type**: static or dynamic
    - **rules**: JSON rules for dynamic segments
    """
    user_id = current_user.get("id")
    return CustomerSegmentService.create_segment(db, segment_data, tenant_id, user_id)


@router.get("/segments", response_model=dict)
def list_segments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    segmentation_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List all customer segments with filters"""
    return CustomerSegmentService.list_segments(
        db, tenant_id, skip, limit, search, segmentation_type
    )


@router.get("/segments/{segment_id}", response_model=dict)
def get_segment(
    segment_id: UUID = Path(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get segment details by ID"""
    return CustomerSegmentService.get_segment(db, segment_id, tenant_id)


# ============================================================================
# LANDING PAGE ROUTES
# ============================================================================

@router.post("/landing-pages", response_model=dict, status_code=201)
def create_landing_page(
    page_data: LandingPageCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new landing page
    
    - **page_name**: Page name (required)
    - **page_title**: Page title (required)
    - **slug**: URL-friendly identifier (required)
    """
    user_id = current_user.get("id")
    return LandingPageService.create_landing_page(db, page_data, tenant_id, user_id)


@router.post("/landing-pages/{page_id}/publish", response_model=dict)
def publish_landing_page(
    page_id: UUID = Path(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Publish a landing page"""
    user_id = current_user.get("id")
    return LandingPageService.publish_landing_page(db, page_id, tenant_id, user_id)


# ============================================================================
# STATISTICS ROUTES
# ============================================================================

@router.get("/stats/summary", response_model=dict)
def get_marketing_stats(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get marketing automation summary statistics"""
    from sqlalchemy import func
    from backend.shared.database.crm_marketing_models import MarketingCampaign, CustomerSegment, LandingPage
    
    try:
        # Total campaigns
        total_campaigns = db.query(func.count(MarketingCampaign.id)).filter(
            MarketingCampaign.tenant_id == tenant_id,
            MarketingCampaign.is_deleted == False
        ).scalar()
        
        # Active campaigns
        active_campaigns = db.query(func.count(MarketingCampaign.id)).filter(
            MarketingCampaign.tenant_id == tenant_id,
            MarketingCampaign.status == "running",
            MarketingCampaign.is_deleted == False
        ).scalar()
        
        # Total segments
        total_segments = db.query(func.count(CustomerSegment.id)).filter(
            CustomerSegment.tenant_id == tenant_id,
            CustomerSegment.is_deleted == False
        ).scalar()
        
        # Total landing pages
        total_landing_pages = db.query(func.count(LandingPage.id)).filter(
            LandingPage.tenant_id == tenant_id,
            LandingPage.is_deleted == False
        ).scalar()
        
        # Campaigns by status
        status_counts = db.query(
            MarketingCampaign.status,
            func.count(MarketingCampaign.id)
        ).filter(
            MarketingCampaign.tenant_id == tenant_id,
            MarketingCampaign.is_deleted == False
        ).group_by(MarketingCampaign.status).all()
        
        from backend.shared.common.response import create_response
        return create_response(
            data={
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "total_segments": total_segments,
                "total_landing_pages": total_landing_pages,
                "by_status": {status: count for status, count in status_counts}
            }
        )
        
    except Exception as e:
        from backend.shared.common.response import error_response
        return error_response(message=f"Failed to get statistics: {str(e)}")
