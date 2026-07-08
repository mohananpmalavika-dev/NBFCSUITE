"""
Insurance Commission Service

Handles all business logic for commission tracking including:
- Commission calculation and CRUD
- Agent commission management
- Approval and payment workflow
- Commission statistics and reports
- Batch commission calculation
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from backend.services.insurance.models import (
    InsuranceCommission, InsurancePolicy, InsuranceAgent, 
    InsurancePremium, CommissionStatus, PolicyStatus, PremiumStatus
)
from backend.shared.common.response import CustomException


class CommissionService:
    """Service for managing insurance commissions"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== CRUD OPERATIONS ====================
    
    def create_commission(self, commission_data: Dict[str, Any]) -> InsuranceCommission:
        """
        Create new commission entry
        
        Args:
            commission_data: Commission information
            
        Returns:
            Created commission
        """
        # Verify policy exists
        policy = self.db.query(InsurancePolicy).filter(
            and_(
                InsurancePolicy.id == commission_data.get('policy_id'),
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False
            )
        ).first()
        
        if not policy:
            raise CustomException(status_code=404, message="Policy not found")
        
        # Verify agent exists
        agent = self.db.query(InsuranceAgent).filter(
            and_(
                InsuranceAgent.id == commission_data.get('agent_id'),
                InsuranceAgent.tenant_id == self.tenant_id,
                InsuranceAgent.is_deleted == False
            )
        ).first()
        
        if not agent:
            raise CustomException(status_code=404, message="Agent not found")
        
        # Generate commission number
        commission_number = self._generate_commission_number()
        
        # Calculate commission amount
        base_amount = Decimal(str(commission_data.get('base_amount')))
        commission_rate = Decimal(str(commission_data.get('commission_rate')))
        commission_amount = base_amount * (commission_rate / 100)
        
        # Calculate TDS and net payable
        tds_percentage = Decimal(str(commission_data.get('tds_percentage', 0)))
        tds_amount = commission_amount * (tds_percentage / 100)
        other_deductions = Decimal(str(commission_data.get('other_deductions', 0)))
        bonus_amount = Decimal(str(commission_data.get('bonus_amount', 0)))
        penalty_amount = Decimal(str(commission_data.get('penalty_amount', 0)))
        
        net_payable = commission_amount + bonus_amount - tds_amount - other_deductions - penalty_amount
        
        # Create commission
        commission = InsuranceCommission(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            policy_number=policy.policy_number,
            commission_number=commission_number,
            commission_amount=commission_amount,
            tds_amount=tds_amount,
            net_payable=net_payable,
            calculation_date=datetime.utcnow(),
            commission_status=CommissionStatus.PENDING,
            **commission_data
        )
        
        self.db.add(commission)
        self.db.commit()
        self.db.refresh(commission)
        
        return commission
    
    def get_commission(self, commission_id: uuid.UUID) -> Optional[InsuranceCommission]:
        """Get commission by ID"""
        commission = self.db.query(InsuranceCommission).filter(
            and_(
                InsuranceCommission.id == commission_id,
                InsuranceCommission.tenant_id == self.tenant_id,
                InsuranceCommission.is_deleted == False
            )
        ).first()
        
        if not commission:
            raise CustomException(status_code=404, message="Commission not found")
        
        return commission
    
    def get_commission_by_number(self, commission_number: str) -> Optional[InsuranceCommission]:
        """Get commission by commission number"""
        commission = self.db.query(InsuranceCommission).filter(
            and_(
                InsuranceCommission.commission_number == commission_number,
                InsuranceCommission.tenant_id == self.tenant_id,
                InsuranceCommission.is_deleted == False
            )
        ).first()
        
        if not commission:
            raise CustomException(status_code=404, message="Commission not found")
        
        return commission
    
    def list_commissions(
        self,
        policy_id: Optional[uuid.UUID] = None,
        agent_id: Optional[uuid.UUID] = None,
        commission_status: Optional[CommissionStatus] = None,
        commission_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InsuranceCommission]:
        """List commissions with filters"""
        query = self.db.query(InsuranceCommission).filter(
            and_(
                InsuranceCommission.tenant_id == self.tenant_id,
                InsuranceCommission.is_deleted == False
            )
        )
        
        if policy_id:
            query = query.filter(InsuranceCommission.policy_id == policy_id)
        
        if agent_id:
            query = query.filter(InsuranceCommission.agent_id == agent_id)
        
        if commission_status:
            query = query.filter(InsuranceCommission.commission_status == commission_status)
        
        if commission_type:
            query = query.filter(InsuranceCommission.commission_type == commission_type)
        
        commissions = query.order_by(InsuranceCommission.calculation_date.desc()).offset(skip).limit(limit).all()
        return commissions
    
    # ==================== WORKFLOW OPERATIONS ====================
    
    def approve_commission(self, commission_id: uuid.UUID, approval_data: Dict[str, Any]) -> InsuranceCommission:
        """Approve commission for payment"""
        commission = self.get_commission(commission_id)
        
        if commission.commission_status not in [CommissionStatus.PENDING, CommissionStatus.CALCULATED]:
            raise CustomException(
                status_code=400,
                message=f"Cannot approve commission with status: {commission.commission_status}"
            )
        
        commission.approved_by = self.user_id
        commission.approved_by_name = approval_data.get('approved_by_name')
        commission.approval_date = datetime.utcnow()
        commission.commission_status = CommissionStatus.APPROVED
        commission.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(commission)
        
        return commission
    
    def pay_commission(self, commission_id: uuid.UUID, payment_data: Dict[str, Any]) -> InsuranceCommission:
        """Record commission payment"""
        commission = self.get_commission(commission_id)
        
        if commission.commission_status != CommissionStatus.APPROVED:
            raise CustomException(
                status_code=400,
                message="Only approved commissions can be paid"
            )
        
        commission.payment_date = payment_data.get('payment_date', datetime.utcnow())
        commission.payment_method = payment_data.get('payment_method')
        commission.payment_reference = payment_data.get('payment_reference')
        commission.paid_amount = payment_data.get('paid_amount')
        commission.commission_status = CommissionStatus.PAID
        commission.updated_by = self.user_id
        
        # Update agent statistics
        agent = self.db.query(InsuranceAgent).filter(
            InsuranceAgent.id == commission.agent_id
        ).first()
        
        if agent:
            agent.total_commission_earned += commission.paid_amount
        
        self.db.commit()
        self.db.refresh(commission)
        
        return commission
    
    def cancel_commission(self, commission_id: uuid.UUID, reason: Optional[str] = None) -> InsuranceCommission:
        """Cancel commission"""
        commission = self.get_commission(commission_id)
        
        if commission.commission_status == CommissionStatus.PAID:
            raise CustomException(
                status_code=400,
                message="Cannot cancel paid commission"
            )
        
        commission.commission_status = CommissionStatus.CANCELLED
        if reason:
            commission.remarks = f"Cancelled: {reason}"
        commission.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(commission)
        
        return commission
    
    # ==================== CALCULATION METHODS ====================
    
    def calculate_first_year_commission(
        self,
        policy_id: uuid.UUID,
        agent_id: uuid.UUID
    ) -> InsuranceCommission:
        """Calculate first year commission for new policy"""
        policy = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.id == policy_id
        ).first()
        
        if not policy:
            raise CustomException(status_code=404, message="Policy not found")
        
        agent = self.db.query(InsuranceAgent).filter(
            InsuranceAgent.id == agent_id
        ).first()
        
        if not agent:
            raise CustomException(status_code=404, message="Agent not found")
        
        # Use agent's commission rate or default
        commission_rate = agent.default_commission_rate or Decimal('5.0')
        
        # First year commission on annual premium
        annual_premium = policy.premium_amount * self._get_frequency_multiplier(policy.premium_frequency)
        
        commission_data = {
            'policy_id': policy.id,
            'agent_id': agent.id,
            'agent_name': agent.agent_name,
            'agent_code': agent.agent_code,
            'agent_type': agent.agent_type,
            'commission_type': 'first_year',
            'base_amount': annual_premium,
            'commission_rate': commission_rate,
            'commission_period': f"FY-{datetime.utcnow().year}",
            'branch_id': policy.branch_id,
            'branch_name': policy.branch_name,
            'tds_percentage': 10.0 if agent.tds_applicable else 0.0
        }
        
        return self.create_commission(commission_data)
    
    def calculate_renewal_commission(
        self,
        premium_id: uuid.UUID
    ) -> InsuranceCommission:
        """Calculate renewal commission for premium payment"""
        premium = self.db.query(InsurancePremium).filter(
            InsurancePremium.id == premium_id
        ).first()
        
        if not premium:
            raise CustomException(status_code=404, message="Premium not found")
        
        policy = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.id == premium.policy_id
        ).first()
        
        if not policy or not policy.agent_id:
            raise CustomException(status_code=404, message="Policy or agent not found")
        
        agent = self.db.query(InsuranceAgent).filter(
            InsuranceAgent.id == policy.agent_id
        ).first()
        
        if not agent:
            raise CustomException(status_code=404, message="Agent not found")
        
        # Renewal commission is typically lower (e.g., 2-3%)
        commission_rate = (agent.default_commission_rate or Decimal('5.0')) / 2
        
        commission_data = {
            'policy_id': policy.id,
            'agent_id': agent.id,
            'agent_name': agent.agent_name,
            'agent_code': agent.agent_code,
            'agent_type': agent.agent_type,
            'commission_type': 'renewal',
            'base_amount': premium.premium_amount,
            'commission_rate': commission_rate,
            'premium_id': premium.id,
            'premium_number': premium.premium_number,
            'commission_period': premium.premium_due_date.strftime('%b-%Y'),
            'branch_id': policy.branch_id,
            'branch_name': policy.branch_name,
            'tds_percentage': 10.0 if agent.tds_applicable else 0.0
        }
        
        return self.create_commission(commission_data)
    
    # ==================== BATCH OPERATIONS ====================
    
    def calculate_commissions_for_period(
        self,
        commission_period: str,
        commission_type: str,
        agent_ids: Optional[List[uuid.UUID]] = None
    ) -> Dict[str, Any]:
        """
        Calculate commissions for all eligible agents in a period
        (This is typically run as a scheduled job)
        """
        generated_count = 0
        errors = []
        
        if commission_type == 'renewal':
            # Get all paid premiums for the period
            # Period format: Jan-2024 or Q1-2024
            query = self.db.query(InsurancePremium).filter(
                and_(
                    InsurancePremium.tenant_id == self.tenant_id,
                    InsurancePremium.is_deleted == False,
                    InsurancePremium.premium_status == PremiumStatus.PAID,
                    InsurancePremium.payment_date.isnot(None)
                )
            )
            
            if agent_ids:
                # Filter by agent through policy
                query = query.join(InsurancePolicy).filter(
                    InsurancePolicy.agent_id.in_(agent_ids)
                )
            
            premiums = query.all()
            
            for premium in premiums:
                try:
                    # Check if commission already exists
                    existing = self.db.query(InsuranceCommission).filter(
                        and_(
                            InsuranceCommission.premium_id == premium.id,
                            InsuranceCommission.commission_type == 'renewal'
                        )
                    ).first()
                    
                    if not existing:
                        self.calculate_renewal_commission(premium.id)
                        generated_count += 1
                        
                except Exception as e:
                    errors.append({
                        "premium_id": str(premium.id),
                        "premium_number": premium.premium_number,
                        "error": str(e)
                    })
        
        return {
            "generated": generated_count,
            "errors": errors
        }
    
    # ==================== HELPER METHODS ====================
    
    def _generate_commission_number(self) -> str:
        """Generate unique commission number"""
        # Format: COM-YYYYMMDD-XXXX
        prefix = "COM"
        date_str = datetime.utcnow().strftime("%Y%m%d")
        
        # Get count of commissions created today
        count = self.db.query(func.count(InsuranceCommission.id)).filter(
            and_(
                InsuranceCommission.tenant_id == self.tenant_id,
                func.date(InsuranceCommission.created_at) == datetime.utcnow().date()
            )
        ).scalar()
        
        sequence = str(count + 1).zfill(4)
        return f"{prefix}-{date_str}-{sequence}"
    
    def _get_frequency_multiplier(self, frequency) -> int:
        """Get multiplier to calculate annual premium"""
        from backend.services.insurance.models import PremiumFrequency
        
        if frequency == PremiumFrequency.MONTHLY:
            return 12
        elif frequency == PremiumFrequency.QUARTERLY:
            return 4
        elif frequency == PremiumFrequency.HALF_YEARLY:
            return 2
        elif frequency == PremiumFrequency.ANNUALLY:
            return 1
        else:  # SINGLE
            return 1
    
    # ==================== STATISTICS ====================
    
    def get_commission_statistics(
        self,
        agent_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get commission statistics"""
        query = self.db.query(InsuranceCommission).filter(
            and_(
                InsuranceCommission.tenant_id == self.tenant_id,
                InsuranceCommission.is_deleted == False
            )
        )
        
        if agent_id:
            query = query.filter(InsuranceCommission.agent_id == agent_id)
        
        total_commissions = query.count()
        
        # Commissions by status
        pending_commissions = query.filter(
            InsuranceCommission.commission_status == CommissionStatus.PENDING
        ).count()
        
        approved_commissions = query.filter(
            InsuranceCommission.commission_status == CommissionStatus.APPROVED
        ).count()
        
        paid_commissions = query.filter(
            InsuranceCommission.commission_status == CommissionStatus.PAID
        ).count()
        
        # Amount calculations
        total_amount = query.with_entities(
            func.sum(InsuranceCommission.commission_amount)
        ).scalar() or Decimal(0)
        
        paid_amount = query.filter(
            InsuranceCommission.commission_status == CommissionStatus.PAID
        ).with_entities(
            func.sum(InsuranceCommission.paid_amount)
        ).scalar() or Decimal(0)
        
        outstanding_amount = total_amount - paid_amount
        
        # Commissions by type
        commissions_by_type = {}
        for comm_type in ['first_year', 'renewal', 'performance']:
            count = query.filter(InsuranceCommission.commission_type == comm_type).count()
            commissions_by_type[comm_type] = count
        
        # Top agents (if not filtered by agent)
        commissions_by_agent = []
        if not agent_id:
            top_agents = self.db.query(
                InsuranceCommission.agent_id,
                InsuranceCommission.agent_name,
                func.sum(InsuranceCommission.commission_amount).label('total_commission')
            ).filter(
                and_(
                    InsuranceCommission.tenant_id == self.tenant_id,
                    InsuranceCommission.is_deleted == False
                )
            ).group_by(
                InsuranceCommission.agent_id,
                InsuranceCommission.agent_name
            ).order_by(
                func.sum(InsuranceCommission.commission_amount).desc()
            ).limit(10).all()
            
            commissions_by_agent = [
                {
                    "agent_id": str(agent[0]),
                    "agent_name": agent[1],
                    "total_commission": float(agent[2])
                }
                for agent in top_agents
            ]
        
        return {
            "total_commissions": total_commissions,
            "pending_commissions": pending_commissions,
            "approved_commissions": approved_commissions,
            "paid_commissions": paid_commissions,
            "total_commission_amount": float(total_amount),
            "total_paid_amount": float(paid_amount),
            "total_outstanding": float(outstanding_amount),
            "commissions_by_type": commissions_by_type,
            "commissions_by_agent": commissions_by_agent
        }
