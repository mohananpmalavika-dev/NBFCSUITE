"""
CRM Marketing Automation Service
Business logic for campaign management, segmentation, and execution
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from backend.shared.database.crm_marketing_models import (
    MarketingCampaign, CustomerSegment, SegmentMember, LandingPage,
    CampaignExecution, LandingPageSubmission, CampaignTemplate
)
from backend.shared.schemas.crm_marketing_schemas import (
    MarketingCampaignCreate, MarketingCampaignUpdate,
    CustomerSegmentCreate, CustomerSegmentUpdate,
    LandingPageCreate, LandingPageUpdate,
    LandingPageSubmissionCreate,
    CampaignTemplateCreate, CampaignTemplateUpdate
)
from backend.shared.common.response import success_response, error_response


class MarketingCampaignService:
    """Service for Marketing Campaign operations"""
    
    @staticmethod
    def generate_campaign_number(db: Session, tenant_id: str) -> str:
        """Generate unique campaign number"""
        count = db.query(func.count(MarketingCampaign.id)).filter(
            MarketingCampaign.tenant_id == tenant_id,
            MarketingCampaign.is_deleted == False
        ).scalar()
        
        today = datetime.now().strftime("%Y%m%d")
        campaign_number = f"CAMP-{today}-{str(count + 1).zfill(4)}"
        
        while db.query(MarketingCampaign).filter(
            MarketingCampaign.tenant_id == tenant_id,
            MarketingCampaign.campaign_number == campaign_number
        ).first():
            count += 1
            campaign_number = f"CAMP-{today}-{str(count + 1).zfill(4)}"
        
        return campaign_number

    
    @staticmethod
    def create_campaign(
        db: Session,
        campaign_data: MarketingCampaignCreate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new marketing campaign"""
        try:
            campaign_number = MarketingCampaignService.generate_campaign_number(db, tenant_id)
            
            campaign = MarketingCampaign(
                tenant_id=tenant_id,
                campaign_number=campaign_number,
                **campaign_data.dict(exclude_unset=True),
                created_by=user_id,
                updated_by=user_id
            )
            
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            
            return success_response(
                data=campaign.dict(),
                message="Campaign created successfully"
            )
            
        except Exception as e:
            db.rollback()
            return error_response(message=f"Failed to create campaign: {str(e)}")

    
    @staticmethod
    def get_campaign(
        db: Session,
        campaign_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get campaign by ID"""
        try:
            campaign = db.query(MarketingCampaign).filter(
                MarketingCampaign.id == campaign_id,
                MarketingCampaign.tenant_id == tenant_id,
                MarketingCampaign.is_deleted == False
            ).first()
            
            if not campaign:
                return error_response(message="Campaign not found", status_code=404)
            
            return success_response(data=campaign.dict())
            
        except Exception as e:
            return error_response(message=f"Failed to get campaign: {str(e)}")
    
    @staticmethod
    def list_campaigns(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        status: Optional[str] = None,
        campaign_type: Optional[str] = None,
        campaign_owner_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """List campaigns with filters"""
        try:
            query = db.query(MarketingCampaign).filter(
                MarketingCampaign.tenant_id == tenant_id,
                MarketingCampaign.is_deleted == False
            )
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        MarketingCampaign.campaign_name.ilike(search_filter),
                        MarketingCampaign.campaign_number.ilike(search_filter)
                    )
                )
            
            if status:
                query = query.filter(MarketingCampaign.status == status)

            
            if campaign_type:
                query = query.filter(MarketingCampaign.campaign_type == campaign_type)
            
            if campaign_owner_id:
                query = query.filter(MarketingCampaign.campaign_owner_id == campaign_owner_id)
            
            total = query.count()
            campaigns = query.order_by(MarketingCampaign.created_at.desc()).offset(skip).limit(limit).all()
            
            return success_response(
                data={
                    "total": total,
                    "page": skip // limit + 1,
                    "page_size": limit,
                    "campaigns": [campaign.dict() for campaign in campaigns]
                }
            )
            
        except Exception as e:
            return error_response(message=f"Failed to list campaigns: {str(e)}")
    
    @staticmethod
    def update_campaign(
        db: Session,
        campaign_id: UUID,
        campaign_data: MarketingCampaignUpdate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Update campaign"""
        try:
            campaign = db.query(MarketingCampaign).filter(
                MarketingCampaign.id == campaign_id,
                MarketingCampaign.tenant_id == tenant_id,
                MarketingCampaign.is_deleted == False
            ).first()
            
            if not campaign:
                return error_response(message="Campaign not found", status_code=404)
            
            update_data = campaign_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(campaign, field, value)

            
            campaign.updated_by = user_id
            campaign.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(campaign)
            
            return success_response(
                data=campaign.dict(),
                message="Campaign updated successfully"
            )
            
        except Exception as e:
            db.rollback()
            return error_response(message=f"Failed to update campaign: {str(e)}")
    
    @staticmethod
    def delete_campaign(
        db: Session,
        campaign_id: UUID,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Soft delete campaign"""
        try:
            campaign = db.query(MarketingCampaign).filter(
                MarketingCampaign.id == campaign_id,
                MarketingCampaign.tenant_id == tenant_id,
                MarketingCampaign.is_deleted == False
            ).first()
            
            if not campaign:
                return error_response(message="Campaign not found", status_code=404)
            
            campaign.is_deleted = True
            campaign.deleted_at = datetime.utcnow()
            campaign.deleted_by = user_id
            
            db.commit()
            
            return success_response(message="Campaign deleted successfully")
            
        except Exception as e:
            db.rollback()
            return error_response(message=f"Failed to delete campaign: {str(e)}")
    
    @staticmethod
    def launch_campaign(
        db: Session,
        campaign_id: UUID,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Launch a campaign"""
        try:
            campaign = db.query(MarketingCampaign).filter(
                MarketingCampaign.id == campaign_id,
                MarketingCampaign.tenant_id == tenant_id,
                MarketingCampaign.is_deleted == False
            ).first()
            
            if not campaign:
                return error_response(message="Campaign not found", status_code=404)
            
            if campaign.status != "draft" and campaign.status != "paused":
                return error_response(message="Can only launch draft or paused campaigns")
            
            campaign.status = "running"
            campaign.start_date = datetime.utcnow()
            campaign.updated_by = user_id
            
            db.commit()
            
            return success_response(message="Campaign launched successfully")
            
        except Exception as e:
            db.rollback()
            return error_response(message=f"Failed to launch campaign: {str(e)}")


class CustomerSegmentService:
    """Service for Customer Segment operations"""
    
    @staticmethod
    def generate_segment_number(db: Session, tenant_id: str) -> str:
        """Generate unique segment number"""
        count = db.query(func.count(CustomerSegment.id)).filter(
            CustomerSegment.tenant_id == tenant_id,
            CustomerSegment.is_deleted == False
        ).scalar()
        
        today = datetime.now().strftime("%Y%m%d")
        segment_number = f"SEG-{today}-{str(count + 1).zfill(4)}"
        
        while db.query(CustomerSegment).filter(
            CustomerSegment.tenant_id == tenant_id,
            CustomerSegment.segment_number == segment_number
        ).first():
            count += 1
            segment_number = f"SEG-{today}-{str(count + 1).zfill(4)}"
        
        return segment_number
    
    @staticmethod
    def create_segment(
        db: Session,
        segment_data: CustomerSegmentCreate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new customer segment"""
        try:
            segment_number = CustomerSegmentService.generate_segment_number(db, tenant_id)
            
            segment = CustomerSegment(
                tenant_id=tenant_id,
                segment_number=segment_number,
                **segment_data.dict(exclude_unset=True),
                created_by=user_id,
                updated_by=user_id
            )
            
            db.add(segment)
            db.commit()
            db.refresh(segment)
            
            return success_response(
                data=segment.dict(),
                message="Segment created successfully"
            )
            
        except Exception as e:
            db.rollback()
            return error_response(message=f"Failed to create segment: {str(e)}")

    
    @staticmethod
    def get_segment(
        db: Session,
        segment_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get segment by ID"""
        try:
            segment = db.query(CustomerSegment).filter(
                CustomerSegment.id == segment_id,
                CustomerSegment.tenant_id == tenant_id,
                CustomerSegment.is_deleted == False
            ).first()
            
            if not segment:
                return error_response(message="Segment not found", status_code=404)
            
            return success_response(data=segment.dict())
            
        except Exception as e:
            return error_response(message=f"Failed to get segment: {str(e)}")
    
    @staticmethod
    def list_segments(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        segmentation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """List segments with filters"""
        try:
            query = db.query(CustomerSegment).filter(
                CustomerSegment.tenant_id == tenant_id,
                CustomerSegment.is_deleted == False
            )
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        CustomerSegment.segment_name.ilike(search_filter),
                        CustomerSegment.segment_number.ilike(search_filter)
                    )
                )
            
            if segmentation_type:
                query = query.filter(CustomerSegment.segmentation_type == segmentation_type)
            
            total = query.count()
            segments = query.order_by(CustomerSegment.created_at.desc()).offset(skip).limit(limit).all()
            
            return success_response(
                data={
                    "total": total,
                    "page": skip // limit + 1,
                    "page_size": limit,
                    "segments": [segment.dict() for segment in segments]
                }
            )
            
        except Exception as e:
            return error_response(message=f"Failed to list segments: {str(e)}")


class LandingPageService:
    """Service for Landing Page operations"""
    
    @staticmethod
    def generate_page_number(db: Session, tenant_id: str) -> str:
        """Generate unique page number"""
        count = db.query(func.count(LandingPage.id)).filter(
            LandingPage.tenant_id == tenant_id,
            LandingPage.is_deleted == False
        ).scalar()
        
        today = datetime.now().strftime("%Y%m%d")
        page_number = f"LP-{today}-{str(count + 1).zfill(4)}"
        
        while db.query(LandingPage).filter(
            LandingPage.tenant_id == tenant_id,
            LandingPage.page_number == page_number
        ).first():
            count += 1
            page_number = f"LP-{today}-{str(count + 1).zfill(4)}"
        
        return page_number
    
    @staticmethod
    def create_landing_page(
        db: Session,
        page_data: LandingPageCreate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new landing page"""
        try:
            page_number = LandingPageService.generate_page_number(db, tenant_id)
            
            # Generate full URL
            full_url = f"/landing/{page_data.slug}"
            
            page = LandingPage(
                tenant_id=tenant_id,
                page_number=page_number,
                full_url=full_url,
                **page_data.dict(exclude_unset=True),
                created_by=user_id,
                updated_by=user_id
            )
            
            db.add(page)
            db.commit()
            db.refresh(page)
            
            return success_response(
                data=page.dict(),
                message="Landing page created successfully"
            )
            
        except Exception as e:
            db.rollback()
            return error_response(message=f"Failed to create landing page: {str(e)}")
    
    @staticmethod
    def publish_landing_page(
        db: Session,
        page_id: UUID,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Publish a landing page"""
        try:
            page = db.query(LandingPage).filter(
                LandingPage.id == page_id,
                LandingPage.tenant_id == tenant_id,
                LandingPage.is_deleted == False
            ).first()
            
            if not page:
                return error_response(message="Landing page not found", status_code=404)
            
            page.status = "published"
            page.published_at = datetime.utcnow()
            page.published_by = user_id
            page.updated_by = user_id
            
            db.commit()
            
            return success_response(message="Landing page published successfully")
            
        except Exception as e:
            db.rollback()
            return error_response(message=f"Failed to publish landing page: {str(e)}")
