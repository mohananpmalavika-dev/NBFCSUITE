"""
CRM Opportunity Management Service
Business logic for opportunity tracking, pipeline management, and win/loss analysis
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, case, desc, extract
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from decimal import Decimal
import math

from backend.shared.database.crm_opportunity_models import (
    Opportunity, OpportunityStageHistory, OpportunityActivity,
    OpportunityProduct, OpportunityCompetitor, OpportunityNote,
    OpportunityStageEnum, OpportunityType, OpportunityPriority,
    OpportunitySource, LossReason, CompetitorPosition
)
from .opportunity_schemas import (
    OpportunityCreate, OpportunityUpdate, OpportunityFilters,
    StageTransitionRequest, OpportunityWinRequest, OpportunityLossRequest,
    OpportunityActivityCreate, OpportunityActivityUpdate,
    OpportunityProductCreate, OpportunityProductUpdate,
    OpportunityCompetitorCreate, OpportunityCompetitorUpdate,
    OpportunityNoteCreate, OpportunityNoteUpdate,
    OpportunityDashboardStats, PipelineAnalytics, WinLossAnalysis, ForecastData
)


class OpportunityService:
    """Opportunity Management Service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # OPPORTUNITY CRUD
    # ========================================================================
    
    def create_opportunity(
        self,
        opp_data: OpportunityCreate,
        user_id: int,
        tenant_id: str
    ) -> Opportunity:
        """Create new opportunity"""
        # Generate unique opportunity code
        opp_code = self._generate_opportunity_code()
        
        # Set owner to current user if not specified
        owner_id = opp_data.owner_user_id or user_id
        
        # Create opportunity
        opportunity = Opportunity(
            **opp_data.dict(exclude={'owner_user_id', 'sales_team_ids'}),
            opportunity_code=opp_code,
            owner_user_id=owner_id,
            sales_team_ids=opp_data.sales_team_ids,
            tenant_id=tenant_id,
            stage_entered_date=datetime.utcnow(),
            first_contact_date=date.today()
        )
        
        self.db.add(opportunity)
        self.db.flush()
        
        # Create initial stage history
        self._create_stage_history(
            opportunity_id=opportunity.id,
            to_stage=opportunity.current_stage,
            probability_after=opportunity.win_probability,
            value_after=opportunity.estimated_value,
            changed_by_user_id=user_id,
            notes="Opportunity created"
        )
        
        # Log activity
        self._log_activity(
            opportunity_id=opportunity.id,
            activity_type="opportunity_created",
            activity_title=f"Opportunity created: {opportunity.name}",
            performed_by_user_id=user_id,
            is_system=True
        )
        
        self.db.commit()
        self.db.refresh(opportunity)
        
        return opportunity
    
    def get_opportunity(
        self,
        opportunity_id: int,
        tenant_id: str
    ) -> Optional[Opportunity]:
        """Get opportunity by ID"""
        return self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id,
            Opportunity.tenant_id == tenant_id
        ).first()
    
    def update_opportunity(
        self,
        opportunity_id: int,
        opp_data: OpportunityUpdate,
        user_id: int,
        tenant_id: str
    ) -> Optional[Opportunity]:
        """Update opportunity"""
        opportunity = self.get_opportunity(opportunity_id, tenant_id)
        if not opportunity:
            return None
        
        # Track changes
        changes = {}
        update_data = opp_data.dict(exclude_unset=True)
        
        for field, new_value in update_data.items():
            old_value = getattr(opportunity, field, None)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
                setattr(opportunity, field, new_value)
        
        # Log significant changes
        if changes:
            for field, change in changes.items():
                self._log_activity(
                    opportunity_id=opportunity.id,
                    activity_type="opportunity_updated",
                    activity_title=f"{field.replace('_', ' ').title()} updated",
                    activity_description=f"Changed from {change['old']} to {change['new']}",
                    performed_by_user_id=user_id,
                    old_value={"value": str(change["old"])},
                    new_value={"value": str(change["new"])},
                    is_system=True
                )
        
        self.db.commit()
        self.db.refresh(opportunity)
        
        return opportunity
    
    def list_opportunities(
        self,
        filters: OpportunityFilters,
        tenant_id: str
    ) -> Tuple[List[Opportunity], int]:
        """List opportunities with filters and pagination"""
        query = self.db.query(Opportunity).filter(
            Opportunity.tenant_id == tenant_id
        )
        
        # Apply filters
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Opportunity.name.ilike(search_term),
                    Opportunity.opportunity_code.ilike(search_term),
                    Opportunity.contact_name.ilike(search_term),
                    Opportunity.contact_mobile.ilike(search_term),
                    Opportunity.company_name.ilike(search_term)
                )
            )
        
        if filters.stage:
            query = query.filter(Opportunity.current_stage == filters.stage)
        
        if filters.opportunity_type:
            query = query.filter(Opportunity.opportunity_type == filters.opportunity_type)
        
        if filters.source:
            query = query.filter(Opportunity.source == filters.source)
        
        if filters.priority:
            query = query.filter(Opportunity.priority == filters.priority)
        
        if filters.owner_user_id:
            query = query.filter(Opportunity.owner_user_id == filters.owner_user_id)
        
        if filters.is_won is not None:
            query = query.filter(Opportunity.is_won == filters.is_won)
        
        if filters.is_lost is not None:
            query = query.filter(Opportunity.is_lost == filters.is_lost)
        
        if filters.is_active is not None:
            query = query.filter(Opportunity.is_active == filters.is_active)
        
        if filters.min_value:
            query = query.filter(Opportunity.estimated_value >= filters.min_value)
        
        if filters.max_value:
            query = query.filter(Opportunity.estimated_value <= filters.max_value)
        
        if filters.min_probability:
            query = query.filter(Opportunity.win_probability >= filters.min_probability)
        
        if filters.max_probability:
            query = query.filter(Opportunity.win_probability <= filters.max_probability)
        
        if filters.close_date_from:
            query = query.filter(Opportunity.expected_close_date >= filters.close_date_from)
        
        if filters.close_date_to:
            query = query.filter(Opportunity.expected_close_date <= filters.close_date_to)
        
        if filters.created_from:
            query = query.filter(func.date(Opportunity.created_at) >= filters.created_from)
        
        if filters.created_to:
            query = query.filter(func.date(Opportunity.created_at) <= filters.created_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        opportunities = query.order_by(desc(Opportunity.created_at)).offset(
            (filters.page - 1) * filters.page_size
        ).limit(filters.page_size).all()
        
        return opportunities, total
    
    # ========================================================================
    # PIPELINE STAGE MANAGEMENT
    # ========================================================================
    
    def transition_stage(
        self,
        opportunity_id: int,
        transition: StageTransitionRequest,
        user_id: int,
        tenant_id: str
    ) -> Optional[Opportunity]:
        """Move opportunity to new stage"""
        opportunity = self.get_opportunity(opportunity_id, tenant_id)
        if not opportunity:
            return None
        
        old_stage = opportunity.current_stage
        new_stage = transition.to_stage
        
        # Mark current stage history as exited
        self._exit_current_stage(opportunity_id)
        
        # Update opportunity
        opportunity.previous_stage = old_stage
        opportunity.current_stage = new_stage
        opportunity.stage_entered_date = datetime.utcnow()
        opportunity.stage_changes_count += 1
        
        # Update probability if provided
        old_probability = opportunity.win_probability
        if transition.win_probability is not None:
            opportunity.win_probability = transition.win_probability
        else:
            # Auto-adjust probability based on stage
            opportunity.win_probability = self._get_stage_probability(new_stage)
        
        # Recalculate metrics
        self._update_opportunity_metrics(opportunity)
        
        # Create stage history
        self._create_stage_history(
            opportunity_id=opportunity.id,
            from_stage=old_stage,
            to_stage=new_stage,
            probability_before=old_probability,
            probability_after=opportunity.win_probability,
            value_before=opportunity.estimated_value,
            value_after=opportunity.estimated_value,
            changed_by_user_id=user_id,
            change_reason=transition.change_reason,
            notes=transition.notes
        )
        
        # Log activity
        self._log_activity(
            opportunity_id=opportunity.id,
            activity_type="stage_changed",
            activity_title=f"Stage changed from {old_stage.value} to {new_stage.value}",
            activity_description=transition.notes,
            performed_by_user_id=user_id,
            old_value={"stage": old_stage.value, "probability": old_probability},
            new_value={"stage": new_stage.value, "probability": opportunity.win_probability},
            is_system=False,
            is_key_milestone=True
        )
        
        self.db.commit()
        self.db.refresh(opportunity)
        
        return opportunity
    
    # ========================================================================
    # WIN/LOSS MANAGEMENT
    # ========================================================================
    
    def mark_won(
        self,
        opportunity_id: int,
        win_request: OpportunityWinRequest,
        user_id: int,
        tenant_id: str
    ) -> Optional[Opportunity]:
        """Mark opportunity as won"""
        opportunity = self.get_opportunity(opportunity_id, tenant_id)
        if not opportunity:
            return None
        
        # Exit current stage
        self._exit_current_stage(opportunity_id)
        
        # Update opportunity
        old_stage = opportunity.current_stage
        opportunity.previous_stage = old_stage
        opportunity.current_stage = OpportunityStageEnum.CLOSED_WON
        opportunity.is_won = True
        opportunity.is_lost = False
        opportunity.is_active = False
        opportunity.won_date = datetime.utcnow()
        opportunity.won_value = win_request.won_value
        opportunity.actual_value = win_request.won_value
        opportunity.won_reason = win_request.won_reason
        opportunity.actual_close_date = win_request.actual_close_date or date.today()
        opportunity.win_probability = 100
        
        self._update_opportunity_metrics(opportunity)
        
        # Create stage history
        self._create_stage_history(
            opportunity_id=opportunity.id,
            from_stage=old_stage,
            to_stage=OpportunityStageEnum.CLOSED_WON,
            probability_before=opportunity.win_probability,
            probability_after=100,
            value_before=opportunity.estimated_value,
            value_after=win_request.won_value,
            changed_by_user_id=user_id,
            notes=win_request.notes or "Opportunity won"
        )
        
        # Log activity
        self._log_activity(
            opportunity_id=opportunity.id,
            activity_type="opportunity_won",
            activity_title=f"Opportunity won - ₹{win_request.won_value:,.2f}",
            activity_description=win_request.won_reason,
            performed_by_user_id=user_id,
            is_system=False,
            is_key_milestone=True
        )
        
        self.db.commit()
        self.db.refresh(opportunity)
        
        return opportunity
    
    def mark_lost(
        self,
        opportunity_id: int,
        loss_request: OpportunityLossRequest,
        user_id: int,
        tenant_id: str
    ) -> Optional[Opportunity]:
        """Mark opportunity as lost"""
        opportunity = self.get_opportunity(opportunity_id, tenant_id)
        if not opportunity:
            return None
        
        # Exit current stage
        self._exit_current_stage(opportunity_id)
        
        # Update opportunity
        old_stage = opportunity.current_stage
        opportunity.previous_stage = old_stage
        opportunity.current_stage = OpportunityStageEnum.CLOSED_LOST
        opportunity.is_lost = True
        opportunity.is_won = False
        opportunity.is_active = False
        opportunity.lost_date = datetime.utcnow()
        opportunity.loss_reason = loss_request.loss_reason
        opportunity.loss_reason_details = loss_request.loss_reason_details
        opportunity.competitor_name = loss_request.competitor_name
        opportunity.actual_close_date = loss_request.actual_close_date or date.today()
        opportunity.win_probability = 0
        
        self._update_opportunity_metrics(opportunity)
        
        # Create stage history
        self._create_stage_history(
            opportunity_id=opportunity.id,
            from_stage=old_stage,
            to_stage=OpportunityStageEnum.CLOSED_LOST,
            probability_before=opportunity.win_probability,
            probability_after=0,
            value_before=opportunity.estimated_value,
            value_after=opportunity.estimated_value,
            changed_by_user_id=user_id,
            notes=loss_request.notes or f"Lost: {loss_request.loss_reason.value}"
        )
        
        # Log activity
        self._log_activity(
            opportunity_id=opportunity.id,
            activity_type="opportunity_lost",
            activity_title=f"Opportunity lost - {loss_request.loss_reason.value}",
            activity_description=loss_request.loss_reason_details,
            performed_by_user_id=user_id,
            is_system=False,
            is_key_milestone=True
        )
        
        self.db.commit()
        self.db.refresh(opportunity)
        
        return opportunity
    
    # ========================================================================
    # ACTIVITY MANAGEMENT
    # ========================================================================
    
    def create_activity(
        self,
        activity_data: OpportunityActivityCreate,
        user_id: int,
        tenant_id: str
    ) -> OpportunityActivity:
        """Create opportunity activity"""
        activity = OpportunityActivity(
            **activity_data.dict(exclude={'activity_date'}),
            activity_date=activity_data.activity_date or datetime.utcnow(),
            performed_by_user_id=user_id,
            tenant_id=tenant_id
        )
        
        self.db.add(activity)
        
        # Update opportunity activity metrics
        opportunity = self.get_opportunity(activity_data.opportunity_id, tenant_id)
        if opportunity:
            opportunity.activities_count += 1
            opportunity.last_activity_date = activity.activity_date
        
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    def get_opportunity_activities(
        self,
        opportunity_id: int,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[OpportunityActivity], int]:
        """Get opportunity activities"""
        query = self.db.query(OpportunityActivity).filter(
            OpportunityActivity.opportunity_id == opportunity_id,
            OpportunityActivity.tenant_id == tenant_id
        )
        
        total = query.count()
        
        activities = query.order_by(desc(OpportunityActivity.activity_date)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return activities, total
    
    # ========================================================================
    # PRODUCT MANAGEMENT
    # ========================================================================
    
    def add_product(
        self,
        product_data: OpportunityProductCreate,
        user_id: int,
        tenant_id: str
    ) -> OpportunityProduct:
        """Add product to opportunity"""
        # Calculate line total
        line_total = (product_data.quantity * product_data.unit_price) - product_data.discount_amount
        
        product = OpportunityProduct(
            **product_data.dict(),
            line_total=line_total,
            tenant_id=tenant_id
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def get_opportunity_products(
        self,
        opportunity_id: int,
        tenant_id: str
    ) -> List[OpportunityProduct]:
        """Get opportunity products"""
        return self.db.query(OpportunityProduct).filter(
            OpportunityProduct.opportunity_id == opportunity_id,
            OpportunityProduct.tenant_id == tenant_id
        ).order_by(OpportunityProduct.sort_order).all()
    
    # ========================================================================
    # COMPETITOR MANAGEMENT
    # ========================================================================
    
    def add_competitor(
        self,
        competitor_data: OpportunityCompetitorCreate,
        user_id: int,
        tenant_id: str
    ) -> OpportunityCompetitor:
        """Add competitor to opportunity"""
        competitor = OpportunityCompetitor(
            **competitor_data.dict(),
            tenant_id=tenant_id
        )
        
        self.db.add(competitor)
        self.db.commit()
        self.db.refresh(competitor)
        
        return competitor
    
    def get_opportunity_competitors(
        self,
        opportunity_id: int,
        tenant_id: str
    ) -> List[OpportunityCompetitor]:
        """Get opportunity competitors"""
        return self.db.query(OpportunityCompetitor).filter(
            OpportunityCompetitor.opportunity_id == opportunity_id,
            OpportunityCompetitor.tenant_id == tenant_id,
            OpportunityCompetitor.is_active == True
        ).all()
    
    # ========================================================================
    # DASHBOARD & ANALYTICS
    # ========================================================================
    
    def get_dashboard_stats(
        self,
        tenant_id: str,
        owner_user_id: Optional[int] = None
    ) -> OpportunityDashboardStats:
        """Get dashboard statistics"""
        query = self.db.query(Opportunity).filter(
            Opportunity.tenant_id == tenant_id
        )
        
        if owner_user_id:
            query = query.filter(Opportunity.owner_user_id == owner_user_id)
        
        # Total and active opportunities
        total_opportunities = query.count()
        active_opportunities = query.filter(Opportunity.is_active == True).count()
        
        # Pipeline value
        pipeline_query = query.filter(Opportunity.is_active == True)
        total_pipeline_value = pipeline_query.with_entities(
            func.coalesce(func.sum(Opportunity.estimated_value), 0)
        ).scalar() or Decimal(0)
        
        # Weighted pipeline (value * probability)
        weighted_pipeline_value = self.db.query(
            func.coalesce(
                func.sum(Opportunity.estimated_value * Opportunity.win_probability / 100), 0
            )
        ).filter(
            Opportunity.tenant_id == tenant_id,
            Opportunity.is_active == True
        ).scalar() or Decimal(0)
        
        # Stage distribution
        stage_counts = dict(
            self.db.query(
                Opportunity.current_stage,
                func.count(Opportunity.id)
            ).filter(
                Opportunity.tenant_id == tenant_id,
                Opportunity.is_active == True
            ).group_by(Opportunity.current_stage).all()
        )
        
        # Won/Lost metrics
        won_query = query.filter(Opportunity.is_won == True)
        won_count = won_query.count()
        won_value = won_query.with_entities(
            func.coalesce(func.sum(Opportunity.won_value), 0)
        ).scalar() or Decimal(0)
        
        lost_query = query.filter(Opportunity.is_lost == True)
        lost_count = lost_query.count()
        lost_value = lost_query.with_entities(
            func.coalesce(func.sum(Opportunity.estimated_value), 0)
        ).scalar() or Decimal(0)
        
        # Win rate
        closed_count = won_count + lost_count
        win_rate = (won_count / closed_count * 100) if closed_count > 0 else 0
        
        # Timeline metrics
        avg_days = self.db.query(
            func.avg(Opportunity.days_in_pipeline)
        ).filter(
            Opportunity.tenant_id == tenant_id,
            Opportunity.is_active == True
        ).scalar() or 0
        
        # Closing this month
        today = date.today()
        month_end = date(today.year, today.month + 1, 1) if today.month < 12 else date(today.year + 1, 1, 1)
        
        closing_query = query.filter(
            Opportunity.is_active == True,
            Opportunity.expected_close_date >= today,
            Opportunity.expected_close_date < month_end
        )
        closing_this_month_count = closing_query.count()
        closing_this_month_value = closing_query.with_entities(
            func.coalesce(func.sum(Opportunity.estimated_value), 0)
        ).scalar() or Decimal(0)
        
        # Overdue opportunities
        overdue_count = query.filter(
            Opportunity.is_active == True,
            Opportunity.expected_close_date < today
        ).count()
        
        # Activity metrics
        week_ago = datetime.utcnow() - timedelta(days=7)
        activities_this_week = self.db.query(OpportunityActivity).filter(
            OpportunityActivity.tenant_id == tenant_id,
            OpportunityActivity.activity_date >= week_ago
        ).count()
        
        opportunities_without_activity = query.filter(
            Opportunity.is_active == True,
            or_(
                Opportunity.last_activity_date.is_(None),
                Opportunity.last_activity_date < week_ago
            )
        ).count()
        
        # High probability opportunities
        high_prob_query = query.filter(
            Opportunity.is_active == True,
            Opportunity.win_probability >= 70
        )
        high_probability_count = high_prob_query.count()
        high_probability_value = high_prob_query.with_entities(
            func.coalesce(func.sum(Opportunity.estimated_value), 0)
        ).scalar() or Decimal(0)
        
        return OpportunityDashboardStats(
            total_opportunities=total_opportunities,
            active_opportunities=active_opportunities,
            total_pipeline_value=total_pipeline_value,
            weighted_pipeline_value=weighted_pipeline_value,
            prospecting_count=stage_counts.get(OpportunityStageEnum.PROSPECTING, 0),
            qualification_count=stage_counts.get(OpportunityStageEnum.QUALIFICATION, 0),
            needs_analysis_count=stage_counts.get(OpportunityStageEnum.NEEDS_ANALYSIS, 0),
            proposal_count=stage_counts.get(OpportunityStageEnum.PROPOSAL, 0),
            negotiation_count=stage_counts.get(OpportunityStageEnum.NEGOTIATION, 0),
            won_count=won_count,
            won_value=won_value,
            lost_count=lost_count,
            lost_value=lost_value,
            win_rate=win_rate,
            avg_days_in_pipeline=float(avg_days),
            closing_this_month_count=closing_this_month_count,
            closing_this_month_value=closing_this_month_value,
            overdue_count=overdue_count,
            activities_this_week=activities_this_week,
            opportunities_without_activity_7days=opportunities_without_activity,
            high_probability_count=high_probability_count,
            high_probability_value=high_probability_value
        )
    
    def get_pipeline_analytics(
        self,
        tenant_id: str,
        owner_user_id: Optional[int] = None
    ) -> List[PipelineAnalytics]:
        """Get pipeline analytics by stage"""
        query = self.db.query(Opportunity).filter(
            Opportunity.tenant_id == tenant_id,
            Opportunity.is_active == True
        )
        
        if owner_user_id:
            query = query.filter(Opportunity.owner_user_id == owner_user_id)
        
        analytics = []
        
        for stage in OpportunityStageEnum:
            if stage in [OpportunityStageEnum.CLOSED_WON, OpportunityStageEnum.CLOSED_LOST]:
                continue
            
            stage_query = query.filter(Opportunity.current_stage == stage)
            
            count = stage_query.count()
            if count == 0:
                continue
            
            total_value = stage_query.with_entities(
                func.sum(Opportunity.estimated_value)
            ).scalar() or Decimal(0)
            
            avg_value = total_value / count if count > 0 else Decimal(0)
            
            avg_days = stage_query.with_entities(
                func.avg(Opportunity.days_in_current_stage)
            ).scalar() or 0
            
            # Calculate conversion rate (simplified)
            conversion_rate = 0.0
            
            analytics.append(PipelineAnalytics(
                stage=stage,
                count=count,
                total_value=total_value,
                avg_value=avg_value,
                avg_days_in_stage=float(avg_days),
                conversion_rate=conversion_rate
            ))
        
        return analytics
    
    def get_win_loss_analysis(
        self,
        tenant_id: str,
        period: str,
        owner_user_id: Optional[int] = None
    ) -> WinLossAnalysis:
        """Get win/loss analysis for a period"""
        # Parse period (e.g., "2024-Q1", "2024-01")
        query = self.db.query(Opportunity).filter(
            Opportunity.tenant_id == tenant_id
        )
        
        if owner_user_id:
            query = query.filter(Opportunity.owner_user_id == owner_user_id)
        
        # Won opportunities
        won_query = query.filter(Opportunity.is_won == True)
        won_count = won_query.count()
        won_value = won_query.with_entities(
            func.coalesce(func.sum(Opportunity.won_value), 0)
        ).scalar() or Decimal(0)
        
        avg_won_value = won_value / won_count if won_count > 0 else Decimal(0)
        
        avg_days_to_win = won_query.with_entities(
            func.avg(Opportunity.days_in_pipeline)
        ).scalar() or 0
        
        # Lost opportunities
        lost_query = query.filter(Opportunity.is_lost == True)
        lost_count = lost_query.count()
        lost_value = lost_query.with_entities(
            func.coalesce(func.sum(Opportunity.estimated_value), 0)
        ).scalar() or Decimal(0)
        
        # Win rate
        total_closed = won_count + lost_count
        win_rate = (won_count / total_closed * 100) if total_closed > 0 else 0
        
        # Loss reasons breakdown
        loss_reasons = dict(
            lost_query.with_entities(
                Opportunity.loss_reason,
                func.count(Opportunity.id)
            ).group_by(Opportunity.loss_reason).all()
        )
        loss_reasons_dict = {str(k.value) if k else "unknown": v for k, v in loss_reasons.items()}
        
        # Top competitors
        competitors = self.db.query(
            Opportunity.competitor_name,
            func.count(Opportunity.id).label('count')
        ).filter(
            Opportunity.tenant_id == tenant_id,
            Opportunity.is_lost == True,
            Opportunity.competitor_name.isnot(None)
        ).group_by(Opportunity.competitor_name).order_by(desc('count')).limit(5).all()
        
        top_competitors = [
            {"name": name, "losses": count} for name, count in competitors
        ]
        
        return WinLossAnalysis(
            period=period,
            won_count=won_count,
            won_value=won_value,
            avg_won_value=avg_won_value,
            avg_days_to_win=float(avg_days_to_win),
            lost_count=lost_count,
            lost_value=lost_value,
            win_rate=win_rate,
            loss_reasons=loss_reasons_dict,
            top_competitors=top_competitors
        )
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _generate_opportunity_code(self) -> str:
        """Generate unique opportunity code"""
        today = date.today()
        prefix = f"OPP{today.strftime('%y%m')}"
        
        # Get count for this month
        count = self.db.query(Opportunity).filter(
            Opportunity.opportunity_code.like(f"{prefix}%")
        ).count()
        
        return f"{prefix}{count + 1:04d}"
    
    def _create_stage_history(
        self,
        opportunity_id: int,
        to_stage: OpportunityStageEnum,
        from_stage: Optional[OpportunityStageEnum] = None,
        probability_before: Optional[int] = None,
        probability_after: Optional[int] = None,
        value_before: Optional[Decimal] = None,
        value_after: Optional[Decimal] = None,
        changed_by_user_id: Optional[int] = None,
        change_reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> OpportunityStageHistory:
        """Create stage history entry"""
        # Get opportunity tenant_id
        opportunity = self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id
        ).first()
        
        is_forward = True
        if from_stage and to_stage:
            stage_order = {
                OpportunityStageEnum.PROSPECTING: 1,
                OpportunityStageEnum.QUALIFICATION: 2,
                OpportunityStageEnum.NEEDS_ANALYSIS: 3,
                OpportunityStageEnum.PROPOSAL: 4,
                OpportunityStageEnum.NEGOTIATION: 5,
                OpportunityStageEnum.CLOSED_WON: 6,
                OpportunityStageEnum.CLOSED_LOST: 6
            }
            is_forward = stage_order.get(to_stage, 0) >= stage_order.get(from_stage, 0)
        
        history = OpportunityStageHistory(
            opportunity_id=opportunity_id,
            from_stage=from_stage,
            to_stage=to_stage,
            probability_before=probability_before,
            probability_after=probability_after,
            value_before=value_before,
            value_after=value_after,
            changed_by_user_id=changed_by_user_id,
            change_reason=change_reason,
            notes=notes,
            is_forward=is_forward,
            is_current=True,
            tenant_id=opportunity.tenant_id if opportunity else "default"
        )
        
        self.db.add(history)
        return history
    
    def _exit_current_stage(self, opportunity_id: int):
        """Mark current stage as exited"""
        current_history = self.db.query(OpportunityStageHistory).filter(
            OpportunityStageHistory.opportunity_id == opportunity_id,
            OpportunityStageHistory.is_current == True
        ).first()
        
        if current_history:
            current_history.is_current = False
            current_history.stage_exited_date = datetime.utcnow()
            
            # Calculate days in stage
            if current_history.stage_entered_date:
                delta = datetime.utcnow() - current_history.stage_entered_date
                current_history.days_in_stage = delta.days
    
    def _update_opportunity_metrics(self, opportunity: Opportunity):
        """Update opportunity metrics"""
        # Days in pipeline
        if opportunity.created_at:
            delta = datetime.utcnow() - opportunity.created_at
            opportunity.days_in_pipeline = delta.days
        
        # Days in current stage
        if opportunity.stage_entered_date:
            delta = datetime.utcnow() - opportunity.stage_entered_date
            opportunity.days_in_current_stage = delta.days
    
    def _get_stage_probability(self, stage: OpportunityStageEnum) -> int:
        """Get default probability for stage"""
        probabilities = {
            OpportunityStageEnum.PROSPECTING: 10,
            OpportunityStageEnum.QUALIFICATION: 20,
            OpportunityStageEnum.NEEDS_ANALYSIS: 40,
            OpportunityStageEnum.PROPOSAL: 60,
            OpportunityStageEnum.NEGOTIATION: 80,
            OpportunityStageEnum.CLOSED_WON: 100,
            OpportunityStageEnum.CLOSED_LOST: 0
        }
        return probabilities.get(stage, 10)
    
    def _log_activity(
        self,
        opportunity_id: int,
        activity_type: str,
        activity_title: str,
        performed_by_user_id: int,
        activity_description: Optional[str] = None,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        is_system: bool = False,
        is_key_milestone: bool = False
    ):
        """Log system activity"""
        opportunity = self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id
        ).first()
        
        if not opportunity:
            return
        
        activity = OpportunityActivity(
            opportunity_id=opportunity_id,
            activity_type=activity_type,
            activity_title=activity_title,
            activity_description=activity_description,
            performed_by_user_id=performed_by_user_id,
            old_value=old_value,
            new_value=new_value,
            is_system_generated=is_system,
            is_key_milestone=is_key_milestone,
            tenant_id=opportunity.tenant_id
        )
        
        self.db.add(activity)
