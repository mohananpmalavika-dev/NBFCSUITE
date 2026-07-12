"""
CRM Opportunity Service
Business logic for opportunity management, pipeline tracking, and win/loss analysis
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, case, extract, desc
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from backend.shared.database.crm_opportunity_models import (
    CRMOpportunity, CRMOpportunityProduct, CRMOpportunityActivity,
    OpportunityStage, OpportunityType, OpportunityPriority, LossReason
)
from backend.shared.database.crm_account_models import CRMAccount, CRMContact
from backend.shared.schemas.crm_opportunity_schemas import (
    CRMOpportunityCreate, CRMOpportunityUpdate,
    CRMOpportunityProductCreate, CRMOpportunityActivityCreate
)
from backend.shared.utils.response import create_response, error_response
from backend.shared.utils.logger import logger


class CRMOpportunityService:
    """Service for CRM Opportunity operations"""
    
    @staticmethod
    def _generate_opportunity_number(db: Session, tenant_id: str) -> str:
        """Generate unique opportunity number"""
        try:
            # Get the last opportunity number for this tenant
            last_opportunity = db.query(CRMOpportunity).filter(
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.opportunity_number.like(f"OPP-{datetime.now().year}-%")
            ).order_by(CRMOpportunity.created_at.desc()).first()
            
            if last_opportunity and last_opportunity.opportunity_number:
                # Extract the sequence number
                parts = last_opportunity.opportunity_number.split('-')
                if len(parts) == 3:
                    sequence = int(parts[2]) + 1
                else:
                    sequence = 1
            else:
                sequence = 1
            
            return f"OPP-{datetime.now().year}-{sequence:05d}"
        
        except Exception as e:
            # Fallback to timestamp-based number
            timestamp = int(datetime.now().timestamp())
            return f"OPP-{datetime.now().year}-{timestamp}"
    
    @staticmethod
    def _calculate_weighted_value(estimated_value: Decimal, probability: Decimal) -> Decimal:
        """Calculate weighted opportunity value"""
        return (estimated_value * probability) / Decimal("100.0")
    
    @staticmethod
    def create_opportunity(
        db: Session,
        opportunity_data: CRMOpportunityCreate,
        tenant_id: str,
        user_id: str
    ) -> dict:
        """Create a new opportunity"""
        try:
            # Verify account exists
            account = db.query(CRMAccount).filter(
                CRMAccount.id == opportunity_data.account_id,
                CRMAccount.tenant_id == tenant_id,
                CRMAccount.is_deleted == False
            ).first()
            
            if not account:
                return error_response(message="Account not found", status_code=404)
            
            # Verify contact if provided
            if opportunity_data.primary_contact_id:
                contact = db.query(CRMContact).filter(
                    CRMContact.id == opportunity_data.primary_contact_id,
                    CRMContact.account_id == opportunity_data.account_id,
                    CRMContact.tenant_id == tenant_id,
                    CRMContact.is_deleted == False
                ).first()
                
                if not contact:
                    return error_response(message="Contact not found or not associated with account", status_code=404)
            
            # Generate opportunity number
            opportunity_number = CRMOpportunityService._generate_opportunity_number(db, tenant_id)
            
            # Calculate weighted value
            weighted_value = CRMOpportunityService._calculate_weighted_value(
                opportunity_data.estimated_value,
                opportunity_data.probability
            )
            
            # Create opportunity
            new_opportunity = CRMOpportunity(
                tenant_id=tenant_id,
                opportunity_number=opportunity_number,
                opportunity_name=opportunity_data.opportunity_name,
                account_id=opportunity_data.account_id,
                primary_contact_id=opportunity_data.primary_contact_id,
                opportunity_type=opportunity_data.opportunity_type,
                stage=opportunity_data.stage,
                priority=opportunity_data.priority,
                estimated_value=opportunity_data.estimated_value,
                currency=opportunity_data.currency,
                probability=opportunity_data.probability,
                weighted_value=weighted_value,
                expected_close_date=opportunity_data.expected_close_date,
                lead_source=opportunity_data.lead_source,
                campaign_id=opportunity_data.campaign_id,
                opportunity_owner_id=opportunity_data.opportunity_owner_id,
                sales_team=opportunity_data.sales_team,
                description=opportunity_data.description,
                next_step=opportunity_data.next_step,
                internal_notes=opportunity_data.internal_notes,
                tags=opportunity_data.tags or [],
                custom_fields=opportunity_data.custom_fields or {},
                stage_history=[{
                    "stage": opportunity_data.stage,
                    "changed_at": datetime.utcnow().isoformat(),
                    "changed_by": str(user_id),
                    "probability": float(opportunity_data.probability)
                }],
                created_by=user_id
            )
            
            db.add(new_opportunity)
            db.flush()
            
            # Add products if provided
            if opportunity_data.products:
                for product_data in opportunity_data.products:
                    # Calculate line total
                    subtotal = product_data.quantity * product_data.unit_price
                    discount = product_data.discount_amount or (subtotal * product_data.discount_percentage / Decimal("100.0"))
                    taxable_amount = subtotal - discount
                    tax = product_data.tax_amount or (taxable_amount * product_data.tax_percentage / Decimal("100.0"))
                    total = taxable_amount + tax
                    
                    new_product = CRMOpportunityProduct(
                        tenant_id=tenant_id,
                        opportunity_id=new_opportunity.id,
                        product_code=product_data.product_code,
                        product_name=product_data.product_name,
                        description=product_data.description,
                        quantity=product_data.quantity,
                        unit_price=product_data.unit_price,
                        discount_percentage=product_data.discount_percentage,
                        discount_amount=discount,
                        tax_percentage=product_data.tax_percentage,
                        tax_amount=tax,
                        total_amount=total,
                        product_category=product_data.product_category,
                        line_notes=product_data.line_notes,
                        custom_fields=product_data.custom_fields or {},
                        created_by=user_id
                    )
                    db.add(new_product)
            
            db.commit()
            db.refresh(new_opportunity)
            
            logger.info(f"Opportunity created: {opportunity_number} for tenant {tenant_id}")
            
            return create_response(
                data={
                    "id": str(new_opportunity.id),
                    "opportunity_number": new_opportunity.opportunity_number,
                    "opportunity_name": new_opportunity.opportunity_name,
                    "stage": new_opportunity.stage,
                    "estimated_value": float(new_opportunity.estimated_value),
                    "weighted_value": float(new_opportunity.weighted_value)
                },
                message="Opportunity created successfully"
            )
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating opportunity: {str(e)}")
            return error_response(message=f"Failed to create opportunity: {str(e)}")
    
    @staticmethod
    def list_opportunities(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        stage: Optional[str] = None,
        priority: Optional[str] = None,
        opportunity_owner_id: Optional[UUID] = None,
        account_id: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> dict:
        """List opportunities with filters"""
        try:
            query = db.query(CRMOpportunity).filter(
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False
            )
            
            # Apply filters
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        CRMOpportunity.opportunity_name.ilike(search_pattern),
                        CRMOpportunity.opportunity_number.ilike(search_pattern),
                        CRMOpportunity.description.ilike(search_pattern)
                    )
                )
            
            if stage:
                query = query.filter(CRMOpportunity.stage == stage)
            
            if priority:
                query = query.filter(CRMOpportunity.priority == priority)
            
            if opportunity_owner_id:
                query = query.filter(CRMOpportunity.opportunity_owner_id == opportunity_owner_id)
            
            if account_id:
                query = query.filter(CRMOpportunity.account_id == account_id)
            
            if from_date:
                query = query.filter(CRMOpportunity.expected_close_date >= from_date)
            
            if to_date:
                query = query.filter(CRMOpportunity.expected_close_date <= to_date)
            
            # Get total count
            total = query.count()
            
            # Get paginated results with relationships
            opportunities = query.options(
                joinedload(CRMOpportunity.account),
                joinedload(CRMOpportunity.primary_contact)
            ).order_by(
                CRMOpportunity.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            # Format response
            items = []
            for opp in opportunities:
                items.append({
                    "id": str(opp.id),
                    "opportunity_number": opp.opportunity_number,
                    "opportunity_name": opp.opportunity_name,
                    "account_id": str(opp.account_id),
                    "account_name": opp.account.account_name if opp.account else None,
                    "stage": opp.stage,
                    "priority": opp.priority,
                    "estimated_value": float(opp.estimated_value),
                    "weighted_value": float(opp.weighted_value),
                    "probability": float(opp.probability),
                    "expected_close_date": opp.expected_close_date.isoformat() if opp.expected_close_date else None,
                    "opportunity_owner_id": str(opp.opportunity_owner_id),
                    "is_won": opp.is_won,
                    "is_lost": opp.is_lost,
                    "created_at": opp.created_at.isoformat()
                })
            
            return create_response(data={
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total
            })
        
        except Exception as e:
            logger.error(f"Error listing opportunities: {str(e)}")
            return error_response(message=f"Failed to list opportunities: {str(e)}")
    
    @staticmethod
    def get_opportunity(db: Session, opportunity_id: UUID, tenant_id: str) -> dict:
        """Get opportunity details with products and activities"""
        try:
            opportunity = db.query(CRMOpportunity).options(
                joinedload(CRMOpportunity.account),
                joinedload(CRMOpportunity.primary_contact),
                joinedload(CRMOpportunity.products),
                joinedload(CRMOpportunity.activities)
            ).filter(
                CRMOpportunity.id == opportunity_id,
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False
            ).first()
            
            if not opportunity:
                return error_response(message="Opportunity not found", status_code=404)
            
            # Format response
            data = {
                "id": str(opportunity.id),
                "opportunity_number": opportunity.opportunity_number,
                "opportunity_name": opportunity.opportunity_name,
                "account_id": str(opportunity.account_id),
                "account_name": opportunity.account.account_name if opportunity.account else None,
                "primary_contact_id": str(opportunity.primary_contact_id) if opportunity.primary_contact_id else None,
                "contact_name": f"{opportunity.primary_contact.first_name} {opportunity.primary_contact.last_name}" if opportunity.primary_contact else None,
                "opportunity_type": opportunity.opportunity_type,
                "stage": opportunity.stage,
                "priority": opportunity.priority,
                "estimated_value": float(opportunity.estimated_value),
                "weighted_value": float(opportunity.weighted_value),
                "probability": float(opportunity.probability),
                "currency": opportunity.currency,
                "expected_close_date": opportunity.expected_close_date.isoformat() if opportunity.expected_close_date else None,
                "actual_close_date": opportunity.actual_close_date.isoformat() if opportunity.actual_close_date else None,
                "lead_source": opportunity.lead_source,
                "opportunity_owner_id": str(opportunity.opportunity_owner_id),
                "sales_team": opportunity.sales_team,
                "description": opportunity.description,
                "next_step": opportunity.next_step,
                "internal_notes": opportunity.internal_notes,
                "is_won": opportunity.is_won,
                "is_lost": opportunity.is_lost,
                "close_reason": opportunity.close_reason,
                "loss_reason": opportunity.loss_reason,
                "competitor_name": opportunity.competitor_name,
                "stage_history": opportunity.stage_history or [],
                "tags": opportunity.tags or [],
                "custom_fields": opportunity.custom_fields or {},
                "products": [{
                    "id": str(p.id),
                    "product_name": p.product_name,
                    "quantity": float(p.quantity),
                    "unit_price": float(p.unit_price),
                    "total_amount": float(p.total_amount)
                } for p in opportunity.products if not p.is_deleted],
                "activities": [{
                    "id": str(a.id),
                    "activity_type": a.activity_type,
                    "activity_subject": a.activity_subject,
                    "activity_date": a.activity_date.isoformat(),
                    "status": a.status
                } for a in opportunity.activities if not a.is_deleted][-10:],  # Last 10 activities
                "created_at": opportunity.created_at.isoformat(),
                "updated_at": opportunity.updated_at.isoformat() if opportunity.updated_at else None
            }
            
            return create_response(data=data)
        
        except Exception as e:
            logger.error(f"Error getting opportunity: {str(e)}")
            return error_response(message=f"Failed to get opportunity: {str(e)}")
    
    @staticmethod
    def update_opportunity(
        db: Session,
        opportunity_id: UUID,
        opportunity_data: CRMOpportunityUpdate,
        tenant_id: str,
        user_id: str
    ) -> dict:
        """Update opportunity details"""
        try:
            opportunity = db.query(CRMOpportunity).filter(
                CRMOpportunity.id == opportunity_id,
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False
            ).first()
            
            if not opportunity:
                return error_response(message="Opportunity not found", status_code=404)
            
            # Track stage changes
            old_stage = opportunity.stage
            update_data = opportunity_data.dict(exclude_unset=True)
            
            # Handle stage change
            if "stage" in update_data and update_data["stage"] != old_stage:
                new_stage_entry = {
                    "stage": update_data["stage"],
                    "changed_at": datetime.utcnow().isoformat(),
                    "changed_by": str(user_id),
                    "probability": float(update_data.get("probability", opportunity.probability)),
                    "reason": "Manual stage update"
                }
                
                stage_history = opportunity.stage_history or []
                stage_history.append(new_stage_entry)
                opportunity.stage_history = stage_history
            
            # Update probability if provided
            if "probability" in update_data or "estimated_value" in update_data:
                new_prob = update_data.get("probability", opportunity.probability)
                new_value = update_data.get("estimated_value", opportunity.estimated_value)
                opportunity.weighted_value = CRMOpportunityService._calculate_weighted_value(
                    new_value, new_prob
                )
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(opportunity, field):
                    setattr(opportunity, field, value)
            
            opportunity.updated_by = user_id
            opportunity.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(opportunity)
            
            return create_response(
                data={
                    "id": str(opportunity.id),
                    "opportunity_number": opportunity.opportunity_number,
                    "opportunity_name": opportunity.opportunity_name,
                    "stage": opportunity.stage
                },
                message="Opportunity updated successfully"
            )
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating opportunity: {str(e)}")
            return error_response(message=f"Failed to update opportunity: {str(e)}")
    
    @staticmethod
    def delete_opportunity(
        db: Session,
        opportunity_id: UUID,
        tenant_id: str,
        user_id: str
    ) -> dict:
        """Delete opportunity (soft delete)"""
        try:
            opportunity = db.query(CRMOpportunity).filter(
                CRMOpportunity.id == opportunity_id,
                CRMOpportunity.tenant_id == tenant_id,
                CRMOpportunity.is_deleted == False
            ).first()
            
            if not opportunity:
                return error_response(message="Opportunity not found", status_code=404)
            
            opportunity.is_deleted = True
            opportunity.deleted_at = datetime.utcnow()
            opportunity.deleted_by = user_id
            
            db.commit()
            
            return create_response(message="Opportunity deleted successfully")
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting opportunity: {str(e)}")
            return error_response(message=f"Failed to delete opportunity: {str(e)}")
