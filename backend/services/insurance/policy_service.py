"""
Insurance Policy Service

Handles all business logic for insurance policy management including:
- Policy CRUD operations
- Policy issuance and activation
- Policy lifecycle management (lapse, surrender, maturity)
- Premium schedule generation
- Policy statistics and reports
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from backend.services.insurance.models import (
    InsurancePolicy, InsurancePremium, PolicyStatus, PolicyType, 
    PremiumFrequency, PremiumStatus
)
from backend.shared.common.response import CustomException


class PolicyService:
    """Service for managing insurance policies"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== CRUD OPERATIONS ====================
    
    def create_policy(self, policy_data: Dict[str, Any]) -> InsurancePolicy:
        """
        Create new insurance policy
        
        Args:
            policy_data: Policy information
            
        Returns:
            Created policy
        """
        # Generate policy number
        policy_number = self._generate_policy_number(policy_data.get('policy_type'))
        
        # Validate dates
        self._validate_policy_dates(
            policy_data.get('policy_start_date'),
            policy_data.get('policy_end_date'),
            policy_data.get('first_premium_date')
        )
        
        # Calculate next premium due date
        next_premium_due = self._calculate_next_premium_date(
            policy_data.get('first_premium_date'),
            policy_data.get('premium_frequency')
        )
        
        # Calculate maturity date if not provided
        if not policy_data.get('maturity_date'):
            maturity_date = self._calculate_maturity_date(
                policy_data.get('policy_start_date'),
                policy_data.get('policy_term_years')
            )
        else:
            maturity_date = policy_data.get('maturity_date')
        
        # Create policy
        policy = InsurancePolicy(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            policy_number=policy_number,
            next_premium_due_date=next_premium_due,
            maturity_date=maturity_date,
            policy_status=PolicyStatus.DRAFT,
            **policy_data
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def get_policy(self, policy_id: uuid.UUID) -> Optional[InsurancePolicy]:
        """Get policy by ID"""
        policy = self.db.query(InsurancePolicy).filter(
            and_(
                InsurancePolicy.id == policy_id,
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False
            )
        ).first()
        
        if not policy:
            raise CustomException(status_code=404, message="Policy not found")
        
        return policy
    
    def get_policy_by_number(self, policy_number: str) -> Optional[InsurancePolicy]:
        """Get policy by policy number"""
        policy = self.db.query(InsurancePolicy).filter(
            and_(
                InsurancePolicy.policy_number == policy_number,
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False
            )
        ).first()
        
        if not policy:
            raise CustomException(status_code=404, message="Policy not found")
        
        return policy
    
    def list_policies(
        self,
        policy_type: Optional[PolicyType] = None,
        policy_status: Optional[PolicyStatus] = None,
        customer_id: Optional[uuid.UUID] = None,
        agent_id: Optional[uuid.UUID] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InsurancePolicy]:
        """List policies with filters"""
        query = self.db.query(InsurancePolicy).filter(
            and_(
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False
            )
        )
        
        if policy_type:
            query = query.filter(InsurancePolicy.policy_type == policy_type)
        
        if policy_status:
            query = query.filter(InsurancePolicy.policy_status == policy_status)
        
        if customer_id:
            query = query.filter(InsurancePolicy.customer_id == customer_id)
        
        if agent_id:
            query = query.filter(InsurancePolicy.agent_id == agent_id)
        
        if is_active is not None:
            query = query.filter(InsurancePolicy.is_active == is_active)
        
        policies = query.order_by(InsurancePolicy.created_at.desc()).offset(skip).limit(limit).all()
        return policies
    
    def update_policy(self, policy_id: uuid.UUID, update_data: Dict[str, Any]) -> InsurancePolicy:
        """Update policy"""
        policy = self.get_policy(policy_id)
        
        # Don't allow status change through update - use specific methods
        if 'policy_status' in update_data:
            del update_data['policy_status']
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        policy.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def delete_policy(self, policy_id: uuid.UUID) -> bool:
        """Soft delete policy"""
        policy = self.get_policy(policy_id)
        
        # Only allow deletion of draft policies
        if policy.policy_status != PolicyStatus.DRAFT:
            raise CustomException(
                status_code=400,
                message="Only draft policies can be deleted"
            )
        
        policy.is_deleted = True
        policy.deleted_at = datetime.utcnow()
        policy.deleted_by = self.user_id
        
        self.db.commit()
        return True
    
    # ==================== POLICY LIFECYCLE ====================
    
    def activate_policy(self, policy_id: uuid.UUID) -> InsurancePolicy:
        """Activate a policy"""
        policy = self.get_policy(policy_id)
        
        if policy.policy_status != PolicyStatus.DRAFT:
            raise CustomException(
                status_code=400,
                message=f"Cannot activate policy with status {policy.policy_status}"
            )
        
        # Generate premium schedule
        self._generate_premium_schedule(policy)
        
        policy.policy_status = PolicyStatus.ACTIVE
        policy.is_active = True
        policy.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def lapse_policy(self, policy_id: uuid.UUID, reason: Optional[str] = None) -> InsurancePolicy:
        """Mark policy as lapsed"""
        policy = self.get_policy(policy_id)
        
        if policy.policy_status != PolicyStatus.ACTIVE:
            raise CustomException(
                status_code=400,
                message="Only active policies can be lapsed"
            )
        
        policy.policy_status = PolicyStatus.LAPSED
        policy.is_lapsed = True
        policy.lapsed_date = datetime.utcnow()
        policy.is_active = False
        if reason:
            policy.remarks = f"Lapsed: {reason}"
        policy.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def revive_policy(self, policy_id: uuid.UUID, payment_data: Dict[str, Any]) -> InsurancePolicy:
        """Revive a lapsed policy"""
        policy = self.get_policy(policy_id)
        
        if policy.policy_status != PolicyStatus.LAPSED:
            raise CustomException(
                status_code=400,
                message="Only lapsed policies can be revived"
            )
        
        # Check if within revival period (typically 2-3 years)
        if policy.lapsed_date:
            days_lapsed = (datetime.utcnow() - policy.lapsed_date).days
            if days_lapsed > 730:  # 2 years
                raise CustomException(
                    status_code=400,
                    message="Policy cannot be revived after 2 years of lapse"
                )
        
        # Calculate arrear premiums and interest
        arrear_amount = payment_data.get('arrear_amount', policy.outstanding_premium)
        
        # Revive policy
        policy.policy_status = PolicyStatus.ACTIVE
        policy.is_lapsed = False
        policy.lapsed_date = None
        policy.is_active = True
        policy.remarks = f"Policy revived on {datetime.utcnow().date()}"
        policy.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def surrender_policy(self, policy_id: uuid.UUID, surrender_data: Dict[str, Any]) -> InsurancePolicy:
        """Surrender a policy"""
        policy = self.get_policy(policy_id)
        
        if policy.policy_status not in [PolicyStatus.ACTIVE, PolicyStatus.LAPSED]:
            raise CustomException(
                status_code=400,
                message="Only active or lapsed policies can be surrendered"
            )
        
        # Calculate surrender value
        surrender_value = self._calculate_surrender_value(policy)
        
        policy.policy_status = PolicyStatus.SURRENDERED
        policy.is_active = False
        policy.surrender_value = surrender_value
        policy.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def mature_policy(self, policy_id: uuid.UUID) -> InsurancePolicy:
        """Mark policy as matured"""
        policy = self.get_policy(policy_id)
        
        if policy.policy_status != PolicyStatus.ACTIVE:
            raise CustomException(
                status_code=400,
                message="Only active policies can be matured"
            )
        
        # Calculate maturity value
        maturity_value = self._calculate_maturity_value(policy)
        
        policy.policy_status = PolicyStatus.MATURED
        policy.is_active = False
        policy.maturity_value = maturity_value
        policy.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    # ==================== PREMIUM SCHEDULE ====================
    
    def _generate_premium_schedule(self, policy: InsurancePolicy) -> None:
        """Generate premium payment schedule"""
        if policy.premium_frequency == PremiumFrequency.SINGLE:
            # Single premium - create one premium entry
            self._create_premium_entry(policy, 1, policy.first_premium_date)
        else:
            # Generate schedule based on frequency
            total_premiums = self._calculate_total_premiums(
                policy.premium_paying_term_years,
                policy.premium_frequency
            )
            
            current_date = policy.first_premium_date
            for i in range(1, total_premiums + 1):
                self._create_premium_entry(policy, i, current_date)
                current_date = self._calculate_next_premium_date(
                    current_date,
                    policy.premium_frequency
                )
    
    def _create_premium_entry(self, policy: InsurancePolicy, installment: int, due_date: datetime) -> None:
        """Create a premium entry"""
        premium_number = f"{policy.policy_number}-P{installment:03d}"
        grace_period_end = due_date + timedelta(days=policy.grace_period_days)
        
        premium = InsurancePremium(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            policy_id=policy.id,
            policy_number=policy.policy_number,
            premium_number=premium_number,
            premium_amount=policy.premium_amount,
            premium_due_date=due_date,
            premium_frequency=policy.premium_frequency,
            installment_number=installment,
            grace_period_end_date=grace_period_end,
            premium_status=PremiumStatus.DUE
        )
        
        self.db.add(premium)
        
        # Update policy counts
        policy.premiums_due_count += 1
        policy.total_premium_due += policy.premium_amount
        policy.outstanding_premium += policy.premium_amount
    
    # ==================== HELPER METHODS ====================
    
    def _generate_policy_number(self, policy_type: PolicyType) -> str:
        """Generate unique policy number"""
        # Format: POL-TYPE-YYYYMMDD-XXXX
        prefix = f"POL-{policy_type.value.upper()}"
        date_str = datetime.utcnow().strftime("%Y%m%d")
        
        # Get count of policies created today
        count = self.db.query(func.count(InsurancePolicy.id)).filter(
            and_(
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.policy_type == policy_type,
                func.date(InsurancePolicy.created_at) == datetime.utcnow().date()
            )
        ).scalar()
        
        sequence = str(count + 1).zfill(4)
        return f"{prefix}-{date_str}-{sequence}"
    
    def _validate_policy_dates(self, start_date: datetime, end_date: datetime, first_premium_date: datetime) -> None:
        """Validate policy dates"""
        if end_date <= start_date:
            raise CustomException(
                status_code=400,
                message="Policy end date must be after start date"
            )
        
        if first_premium_date < start_date:
            raise CustomException(
                status_code=400,
                message="First premium date cannot be before policy start date"
            )
    
    def _calculate_next_premium_date(self, current_date: datetime, frequency: PremiumFrequency) -> datetime:
        """Calculate next premium due date"""
        if frequency == PremiumFrequency.MONTHLY:
            return current_date + timedelta(days=30)
        elif frequency == PremiumFrequency.QUARTERLY:
            return current_date + timedelta(days=90)
        elif frequency == PremiumFrequency.HALF_YEARLY:
            return current_date + timedelta(days=180)
        elif frequency == PremiumFrequency.ANNUALLY:
            return current_date + timedelta(days=365)
        else:  # SINGLE
            return None
    
    def _calculate_maturity_date(self, start_date: datetime, term_years: int) -> datetime:
        """Calculate policy maturity date"""
        return start_date + timedelta(days=term_years * 365)
    
    def _calculate_total_premiums(self, term_years: int, frequency: PremiumFrequency) -> int:
        """Calculate total number of premiums"""
        if frequency == PremiumFrequency.MONTHLY:
            return term_years * 12
        elif frequency == PremiumFrequency.QUARTERLY:
            return term_years * 4
        elif frequency == PremiumFrequency.HALF_YEARLY:
            return term_years * 2
        elif frequency == PremiumFrequency.ANNUALLY:
            return term_years
        else:  # SINGLE
            return 1
    
    def _calculate_surrender_value(self, policy: InsurancePolicy) -> Decimal:
        """Calculate policy surrender value"""
        # Simplified calculation - typically 30-90% of premiums paid depending on policy year
        years_completed = (datetime.utcnow() - policy.policy_start_date).days / 365
        
        if years_completed < 3:
            # No surrender value in first 3 years typically
            return Decimal(0)
        elif years_completed < 5:
            surrender_rate = Decimal('0.30')  # 30%
        elif years_completed < 7:
            surrender_rate = Decimal('0.50')  # 50%
        else:
            surrender_rate = Decimal('0.70')  # 70%
        
        return policy.total_premium_paid * surrender_rate
    
    def _calculate_maturity_value(self, policy: InsurancePolicy) -> Decimal:
        """Calculate policy maturity value"""
        # Simplified - typically sum assured + bonuses
        # For endowment: sum assured + accrued bonuses
        # For term: death benefit only
        if policy.policy_type in [PolicyType.TERM]:
            return Decimal(0)  # Term policies don't have maturity benefit
        else:
            # Endowment, ULIP, etc. return sum assured + bonuses
            # Simplified: return sum assured (actual calculation would include bonuses)
            return policy.sum_assured
    
    # ==================== STATISTICS ====================
    
    def get_policy_statistics(self) -> Dict[str, Any]:
        """Get policy statistics for tenant"""
        total_policies = self.db.query(func.count(InsurancePolicy.id)).filter(
            and_(
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False
            )
        ).scalar()
        
        active_policies = self.db.query(func.count(InsurancePolicy.id)).filter(
            and_(
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False,
                InsurancePolicy.is_active == True
            )
        ).scalar()
        
        lapsed_policies = self.db.query(func.count(InsurancePolicy.id)).filter(
            and_(
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False,
                InsurancePolicy.is_lapsed == True
            )
        ).scalar()
        
        # Sum assured and premiums
        sums = self.db.query(
            func.sum(InsurancePolicy.sum_assured),
            func.sum(InsurancePolicy.total_premium_paid),
            func.sum(InsurancePolicy.outstanding_premium)
        ).filter(
            and_(
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False
            )
        ).first()
        
        total_sum_assured = sums[0] or Decimal(0)
        total_premium_collected = sums[1] or Decimal(0)
        outstanding_premium = sums[2] or Decimal(0)
        
        # Policies by type
        policies_by_type = {}
        for policy_type in PolicyType:
            count = self.db.query(func.count(InsurancePolicy.id)).filter(
                and_(
                    InsurancePolicy.tenant_id == self.tenant_id,
                    InsurancePolicy.is_deleted == False,
                    InsurancePolicy.policy_type == policy_type
                )
            ).scalar()
            policies_by_type[policy_type.value] = count
        
        # Policies by status
        policies_by_status = {}
        for status in PolicyStatus:
            count = self.db.query(func.count(InsurancePolicy.id)).filter(
                and_(
                    InsurancePolicy.tenant_id == self.tenant_id,
                    InsurancePolicy.is_deleted == False,
                    InsurancePolicy.policy_status == status
                )
            ).scalar()
            policies_by_status[status.value] = count
        
        return {
            "total_policies": total_policies,
            "active_policies": active_policies,
            "lapsed_policies": lapsed_policies,
            "matured_policies": policies_by_status.get('matured', 0),
            "total_sum_assured": float(total_sum_assured),
            "total_premium_collected": float(total_premium_collected),
            "outstanding_premium": float(outstanding_premium),
            "policies_by_type": policies_by_type,
            "policies_by_status": policies_by_status
        }
