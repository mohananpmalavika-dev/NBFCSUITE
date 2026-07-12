"""
CRM Opportunity Pipeline & Analytics Service
Sales pipeline tracking and win/loss analysis
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract, desc
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from backend.shared.database.crm_opportunity_models import CRMOpportunity, OpportunityStage
from backend.shared.common.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)


class CRMPipelineService:
    """Service for pipeline tracking and analytics"""
    
    @staticmethod
    def get_pipeline_overview(
        db: Session,
        tenant_id: str,
        owner_id: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> dict:
        """Get sales pipeline overview with stage-wise breakdown"""
        try:
            query = db.query(CRMOpportunity).filter(
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False,
                CRMOpportunity.is_won == False,
                CRMOpportunity.is_lost == False
            )
            
            if owner_id:
                query = query.filter(CRMOpportunity.opportunity_owner_id == owner_id)
            
            if from_date:
                query = query.filter(CRMOpportunity.expected_close_date >= from_date)
            
            if to_date:
                query = query.filter(CRMOpportunity.expected_close_date <= to_date)
            
            # Get stage-wise statistics
            stage_stats = db.query(
                CRMOpportunity.stage,
                func.count(CRMOpportunity.id).label('count'),
                func.sum(CRMOpportunity.estimated_value).label('total_value'),
                func.sum(CRMOpportunity.weighted_value).label('weighted_value'),
                func.avg(CRMOpportunity.probability).label('avg_probability')
            ).filter(
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False,
                CRMOpportunity.is_won == False,
                CRMOpportunity.is_lost == False
            )
            
            if owner_id:
                stage_stats = stage_stats.filter(CRMOpportunity.opportunity_owner_id == owner_id)
            
            if from_date:
                stage_stats = stage_stats.filter(CRMOpportunity.expected_close_date >= from_date)
            
            if to_date:
                stage_stats = stage_stats.filter(CRMOpportunity.expected_close_date <= to_date)
            
            stage_stats = stage_stats.group_by(CRMOpportunity.stage).all()
            
            # Format stages
            stages = []
            total_value = Decimal("0")
            weighted_pipeline_value = Decimal("0")
            total_opportunities = 0
            
            stage_names = {
                "prospecting": "Prospecting",
                "qualification": "Qualification",
                "needs_analysis": "Needs Analysis",
                "proposal": "Proposal",
                "negotiation": "Negotiation"
            }
            
            for stat in stage_stats:
                stage_value = Decimal(str(stat.total_value or 0))
                stage_weighted = Decimal(str(stat.weighted_value or 0))
                
                stages.append({
                    "stage": stat.stage,
                    "stage_name": stage_names.get(stat.stage, stat.stage.replace("_", " ").title()),
                    "count": stat.count,
                    "total_value": float(stage_value),
                    "weighted_value": float(stage_weighted),
                    "avg_probability": float(stat.avg_probability or 0)
                })
                
                total_value += stage_value
                weighted_pipeline_value += stage_weighted
                total_opportunities += stat.count
            
            avg_deal_size = total_value / Decimal(str(total_opportunities)) if total_opportunities > 0 else Decimal("0")
            
            return success_response(data={
                "total_opportunities": total_opportunities,
                "total_value": float(total_value),
                "weighted_pipeline_value": float(weighted_pipeline_value),
                "avg_deal_size": float(avg_deal_size),
                "stages": stages
            })
        
        except Exception as e:
            logger.error(f"Error getting pipeline overview: {str(e)}")
            return error_response(message=f"Failed to get pipeline overview: {str(e)}")
    
    @staticmethod
    def get_win_loss_analysis(
        db: Session,
        tenant_id: str,
        owner_id: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> dict:
        """Get win/loss analysis with detailed breakdown"""
        try:
            base_query = db.query(CRMOpportunity).filter(
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False,
                or_(
                    CRMOpportunity.is_won == True,
                    CRMOpportunity.is_lost == True
                )
            )
            
            if owner_id:
                base_query = base_query.filter(CRMOpportunity.opportunity_owner_id == owner_id)
            
            if from_date:
                base_query = base_query.filter(CRMOpportunity.actual_close_date >= from_date)
            
            if to_date:
                base_query = base_query.filter(CRMOpportunity.actual_close_date <= to_date)
            
            # Won opportunities
            won_stats = db.query(
                func.count(CRMOpportunity.id).label('count'),
                func.sum(CRMOpportunity.estimated_value).label('total_value'),
                func.avg(CRMOpportunity.estimated_value).label('avg_value')
            ).filter(
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False,
                CRMOpportunity.is_won == True
            )
            
            if owner_id:
                won_stats = won_stats.filter(CRMOpportunity.opportunity_owner_id == owner_id)
            
            if from_date:
                won_stats = won_stats.filter(CRMOpportunity.actual_close_date >= from_date)
            
            if to_date:
                won_stats = won_stats.filter(CRMOpportunity.actual_close_date <= to_date)
            
            won_result = won_stats.first()
            
            # Lost opportunities
            lost_stats = db.query(
                func.count(CRMOpportunity.id).label('count'),
                func.sum(CRMOpportunity.estimated_value).label('total_value'),
                func.avg(CRMOpportunity.estimated_value).label('avg_value')
            ).filter(
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False,
                CRMOpportunity.is_lost == True
            )
            
            if owner_id:
                lost_stats = lost_stats.filter(CRMOpportunity.opportunity_owner_id == owner_id)
            
            if from_date:
                lost_stats = lost_stats.filter(CRMOpportunity.actual_close_date >= from_date)
            
            if to_date:
                lost_stats = lost_stats.filter(CRMOpportunity.actual_close_date <= to_date)
            
            lost_result = lost_stats.first()
            
            # Loss reasons breakdown
            loss_reasons = db.query(
                CRMOpportunity.loss_reason,
                func.count(CRMOpportunity.id).label('count')
            ).filter(
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False,
                CRMOpportunity.is_lost == True,
                CRMOpportunity.loss_reason.isnot(None)
            )
            
            if owner_id:
                loss_reasons = loss_reasons.filter(CRMOpportunity.opportunity_owner_id == owner_id)
            
            if from_date:
                loss_reasons = loss_reasons.filter(CRMOpportunity.actual_close_date >= from_date)
            
            if to_date:
                loss_reasons = loss_reasons.filter(CRMOpportunity.actual_close_date <= to_date)
            
            loss_reasons = loss_reasons.group_by(CRMOpportunity.loss_reason).all()
            
            # Top competitors
            competitors = db.query(
                CRMOpportunity.competitor_name,
                func.count(CRMOpportunity.id).label('count'),
                func.sum(CRMOpportunity.estimated_value).label('total_value')
            ).filter(
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False,
                CRMOpportunity.is_lost == True,
                CRMOpportunity.competitor_name.isnot(None)
            )
            
            if owner_id:
                competitors = competitors.filter(CRMOpportunity.opportunity_owner_id == owner_id)
            
            if from_date:
                competitors = competitors.filter(CRMOpportunity.actual_close_date >= from_date)
            
            if to_date:
                competitors = competitors.filter(CRMOpportunity.actual_close_date <= to_date)
            
            competitors = competitors.group_by(CRMOpportunity.competitor_name).order_by(desc('count')).limit(10).all()
            
            # Calculate metrics
            won_count = won_result.count or 0
            lost_count = lost_result.count or 0
            total_closed = won_count + lost_count
            
            win_rate = (Decimal(str(won_count)) / Decimal(str(total_closed)) * Decimal("100")) if total_closed > 0 else Decimal("0")
            
            return success_response(data={
                "total_closed": total_closed,
                "won_count": won_count,
                "lost_count": lost_count,
                "win_rate": float(win_rate),
                "total_won_value": float(won_result.total_value or 0),
                "total_lost_value": float(lost_result.total_value or 0),
                "avg_won_deal_size": float(won_result.avg_value or 0),
                "avg_lost_deal_size": float(lost_result.avg_value or 0),
                "loss_reasons": {reason: count for reason, count in loss_reasons},
                "top_competitors": [
                    {"name": comp, "count": count, "total_value": float(value or 0)}
                    for comp, count, value in competitors
                ]
            })
        
        except Exception as e:
            logger.error(f"Error getting win/loss analysis: {str(e)}")
            return error_response(message=f"Failed to get win/loss analysis: {str(e)}")
