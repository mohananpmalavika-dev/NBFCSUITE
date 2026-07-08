"""
Insurance Premium Service

Handles all business logic for premium collection including:
- Premium payment recording
- Due premium tracking
- Overdue premium identification
- Premium waiver and discount management
- Batch premium generation
- Premium statistics
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from backend.services.insurance.models import (
    InsurancePremium, InsurancePolicy, PremiumStatus, 
    PremiumFrequency, PolicyStatus
)
from backend.shared.common.response import CustomException


class PremiumService:
    """Service for managing insurance premiums"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== CRUD OPERATIONS ====================
    
    def get_premium(self, premium_id: uuid.UUID) -> Optional[InsurancePremium]:
        """Get premium by ID"""
        premium = self.db.query(InsurancePremium).filter(
            and_(
                InsurancePremium.id == premium_id,
                InsurancePremium.tenant_id == self.tenant_id,
                InsurancePremium.is_deleted == False
            )
        ).first()
        
        if not premium:
            raise CustomException(status_code=404, message="Premium not found")
        
        return premium
    
    def get_premium_by_number(self, premium_number: str) -> Optional[InsurancePremium]:
        """Get premium by premium number"""
        premium = self.db.query(InsurancePremium).filter(
            and_(
                InsurancePremium.premium_number == premium_number,
                InsurancePremium.tenant_id == self.tenant_id,
                InsurancePremium.is_deleted == False
            )
        ).first()
        
        if not premium:
            raise CustomException(status_code=404, message="Premium not found")
        
        return premium
    
    def list_premiums(
        self,
        policy_id: Optional[uuid.UUID] = None,
        premium_status: Optional[PremiumStatus] = None,
        from_due_date: Optional[datetime] = None,
        to_due_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InsurancePremium]:
        """List premiums with filters"""
        query = self.db.query(InsurancePremium).filter(
            and_(
                InsurancePremium.tenant_id == self.tenant_id,
                InsurancePremium.is_deleted == False
            )
        )
        
        if policy_id:
            query = query.filter(InsurancePremium.policy_id == policy_id)
        
        if premium_status:
            query = query.filter(InsurancePremium.premium_status == premium_status)
        
        if from_due_date:
            query = query.filter(InsurancePremium.premium_due_date >= from_due_date)
        
        if to_due_date:
            query = query.filter(InsurancePremium.premium_due_date <= to_due_date)
        
        premiums = query.order_by(InsurancePremium.premium_due_date).offset(skip).limit(limit).all()
        return premiums
    
    # ==================== PAYMENT OPERATIONS ====================
    
    def record_payment(self, premium_id: uuid.UUID, payment_data: Dict[str, Any]) -> InsurancePremium:
        """Record premium payment"""
        premium = self.get_premium(premium_id)
        
        # Validate premium status
        if premium.premium_status == PremiumStatus.PAID:
            raise CustomException(
                status_code=400,
                message="Premium already paid"
            )
        
        if premium.premium_status == PremiumStatus.CANCELLED:
            raise CustomException(
                status_code=400,
                message="Cannot pay cancelled premium"
            )
        
        # Get policy
        policy = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.id == premium.policy_id
        ).first()
        
        if not policy:
            raise CustomException(status_code=404, message="Policy not found")
        
        # Calculate late fee if applicable
        late_fee = payment_data.get('late_fee', 0)
        if datetime.utcnow() > premium.grace_period_end_date:
            days_late = (datetime.utcnow() - premium.grace_period_end_date).days
            premium.late_days = days_late
            if late_fee == 0:
                # Calculate default late fee (e.g., 1% per month)
                late_fee = float(premium.premium_amount) * 0.01 * (days_late / 30)
        
        # Update premium record
        premium.premium_status = PremiumStatus.PAID
        premium.payment_date = payment_data.get('payment_date', datetime.utcnow())
        premium.payment_amount = payment_data.get('payment_amount')
        premium.payment_method = payment_data.get('payment_method')
        premium.payment_reference = payment_data.get('payment_reference')
        premium.transaction_id = payment_data.get('transaction_id')
        premium.receipt_number = payment_data.get('receipt_number')
        premium.collected_by = payment_data.get('collected_by', self.user_id)
        premium.collected_by_name = payment_data.get('collected_by_name')
        premium.collection_branch = payment_data.get('collection_branch')
        premium.late_fee = Decimal(str(late_fee))
        premium.remarks = payment_data.get('remarks')
        premium.updated_by = self.user_id
        
        # Update policy financial tracking
        policy.total_premium_paid += premium.payment_amount
        policy.outstanding_premium -= premium.premium_amount
        policy.premiums_paid_count += 1
        policy.premiums_due_count -= 1
        
        # Update next premium due date
        next_premium = self.db.query(InsurancePremium).filter(
            and_(
                InsurancePremium.policy_id == policy.id,
                InsurancePremium.premium_status == PremiumStatus.DUE,
                InsurancePremium.premium_due_date > premium.premium_due_date
            )
        ).order_by(InsurancePremium.premium_due_date).first()
        
        if next_premium:
            policy.next_premium_due_date = next_premium.premium_due_date
        else:
            policy.next_premium_due_date = None
        
        # If policy was lapsed and payment made, consider for revival
        if policy.is_lapsed:
            policy.remarks = f"Premium paid on {premium.payment_date}. Consider for revival."
        
        self.db.commit()
        self.db.refresh(premium)
        
        return premium
    
    def waive_premium(self, premium_id: uuid.UUID, waiver_data: Dict[str, Any]) -> InsurancePremium:
        """Waive premium payment"""
        premium = self.get_premium(premium_id)
        
        if premium.premium_status == PremiumStatus.PAID:
            raise CustomException(
                status_code=400,
                message="Cannot waive already paid premium"
            )
        
        waived_amount = waiver_data.get('waived_amount', premium.premium_amount)
        
        premium.premium_status = PremiumStatus.WAIVED
        premium.waived_amount = waived_amount
        premium.waived_reason = waiver_data.get('waived_reason')
        premium.remarks = waiver_data.get('remarks')
        premium.updated_by = self.user_id
        
        # Update policy
        policy = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.id == premium.policy_id
        ).first()
        
        if policy:
            policy.outstanding_premium -= waived_amount
            policy.premiums_due_count -= 1
        
        self.db.commit()
        self.db.refresh(premium)
        
        return premium
    
    def apply_discount(self, premium_id: uuid.UUID, discount_data: Dict[str, Any]) -> InsurancePremium:
        """Apply discount to premium"""
        premium = self.get_premium(premium_id)
        
        if premium.premium_status == PremiumStatus.PAID:
            raise CustomException(
                status_code=400,
                message="Cannot apply discount to paid premium"
            )
        
        discount_amount = discount_data.get('discount_amount', 0)
        
        premium.discount_amount = discount_amount
        premium.discount_reason = discount_data.get('discount_reason')
        premium.updated_by = self.user_id
        
        # Adjust premium amount
        # Note: Actual payment will be premium_amount - discount_amount
        
        self.db.commit()
        self.db.refresh(premium)
        
        return premium
    
    # ==================== DUE PREMIUM TRACKING ====================
    
    def get_due_premiums(
        self,
        policy_id: Optional[uuid.UUID] = None,
        include_overdue: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[InsurancePremium]:
        """Get all due premiums"""
        query = self.db.query(InsurancePremium).filter(
            and_(
                InsurancePremium.tenant_id == self.tenant_id,
                InsurancePremium.is_deleted == False,
                InsurancePremium.premium_status.in_([PremiumStatus.DUE, PremiumStatus.OVERDUE])
            )
        )
        
        if policy_id:
            query = query.filter(InsurancePremium.policy_id == policy_id)
        
        if not include_overdue:
            query = query.filter(InsurancePremium.premium_status == PremiumStatus.DUE)
        
        premiums = query.order_by(InsurancePremium.premium_due_date).offset(skip).limit(limit).all()
        return premiums
    
    def get_overdue_premiums(
        self,
        policy_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[InsurancePremium]:
        """Get all overdue premiums"""
        query = self.db.query(InsurancePremium).filter(
            and_(
                InsurancePremium.tenant_id == self.tenant_id,
                InsurancePremium.is_deleted == False,
                InsurancePremium.premium_status == PremiumStatus.DUE,
                InsurancePremium.grace_period_end_date < datetime.utcnow()
            )
        )
        
        if policy_id:
            query = query.filter(InsurancePremium.policy_id == policy_id)
        
        premiums = query.order_by(InsurancePremium.premium_due_date).offset(skip).limit(limit).all()
        return premiums
    
    def mark_overdue_premiums(self) -> int:
        """Mark premiums as overdue (batch process)"""
        overdue_premiums = self.db.query(InsurancePremium).filter(
            and_(
                InsurancePremium.tenant_id == self.tenant_id,
                InsurancePremium.is_deleted == False,
                InsurancePremium.premium_status == PremiumStatus.DUE,
                InsurancePremium.grace_period_end_date < datetime.utcnow()
            )
        ).all()
        
        count = 0
        for premium in overdue_premiums:
            premium.premium_status = PremiumStatus.OVERDUE
            days_overdue = (datetime.utcnow() - premium.grace_period_end_date).days
            premium.late_days = days_overdue
            count += 1
        
        self.db.commit()
        return count
    
    # ==================== BATCH OPERATIONS ====================
    
    def generate_premiums_for_period(
        self,
        generation_date: datetime,
        frequency: PremiumFrequency
    ) -> Dict[str, Any]:
        """
        Generate premium entries for all eligible policies
        (This is typically run as a scheduled job)
        """
        # Get active policies with matching frequency
        policies = self.db.query(InsurancePolicy).filter(
            and_(
                InsurancePolicy.tenant_id == self.tenant_id,
                InsurancePolicy.is_deleted == False,
                InsurancePolicy.is_active == True,
                InsurancePolicy.policy_status == PolicyStatus.ACTIVE,
                InsurancePolicy.premium_frequency == frequency
            )
        ).all()
        
        generated_count = 0
        errors = []
        
        for policy in policies:
            try:
                # Check if premium for this period already exists
                existing = self.db.query(InsurancePremium).filter(
                    and_(
                        InsurancePremium.policy_id == policy.id,
                        InsurancePremium.premium_due_date == generation_date
                    )
                ).first()
                
                if not existing:
                    # Calculate next installment number
                    last_premium = self.db.query(InsurancePremium).filter(
                        InsurancePremium.policy_id == policy.id
                    ).order_by(InsurancePremium.installment_number.desc()).first()
                    
                    next_installment = (last_premium.installment_number + 1) if last_premium else 1
                    
                    # Create premium entry (similar to policy_service._create_premium_entry)
                    premium_number = f"{policy.policy_number}-P{next_installment:03d}"
                    grace_period_end = generation_date + timedelta(days=policy.grace_period_days)
                    
                    premium = InsurancePremium(
                        tenant_id=self.tenant_id,
                        created_by=self.user_id,
                        updated_by=self.user_id,
                        policy_id=policy.id,
                        policy_number=policy.policy_number,
                        premium_number=premium_number,
                        premium_amount=policy.premium_amount,
                        premium_due_date=generation_date,
                        premium_frequency=policy.premium_frequency,
                        installment_number=next_installment,
                        grace_period_end_date=grace_period_end,
                        premium_status=PremiumStatus.DUE
                    )
                    
                    self.db.add(premium)
                    generated_count += 1
                    
            except Exception as e:
                errors.append({
                    "policy_id": str(policy.id),
                    "policy_number": policy.policy_number,
                    "error": str(e)
                })
        
        self.db.commit()
        
        return {
            "generated": generated_count,
            "total_policies": len(policies),
            "errors": errors
        }
    
    # ==================== STATISTICS ====================
    
    def get_premium_statistics(
        self,
        policy_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get premium statistics"""
        query = self.db.query(InsurancePremium).filter(
            and_(
                InsurancePremium.tenant_id == self.tenant_id,
                InsurancePremium.is_deleted == False
            )
        )
        
        if policy_id:
            query = query.filter(InsurancePremium.policy_id == policy_id)
        
        total_premiums = query.count()
        
        paid_premiums = query.filter(
            InsurancePremium.premium_status == PremiumStatus.PAID
        ).count()
        
        due_premiums = query.filter(
            InsurancePremium.premium_status == PremiumStatus.DUE
        ).count()
        
        overdue_premiums = query.filter(
            InsurancePremium.premium_status == PremiumStatus.OVERDUE
        ).count()
        
        # Amount calculations
        total_amount = query.with_entities(
            func.sum(InsurancePremium.premium_amount)
        ).scalar() or Decimal(0)
        
        collected_amount = query.filter(
            InsurancePremium.premium_status == PremiumStatus.PAID
        ).with_entities(
            func.sum(InsurancePremium.payment_amount)
        ).scalar() or Decimal(0)
        
        outstanding_amount = query.filter(
            InsurancePremium.premium_status.in_([PremiumStatus.DUE, PremiumStatus.OVERDUE])
        ).with_entities(
            func.sum(InsurancePremium.premium_amount)
        ).scalar() or Decimal(0)
        
        # Collection rate
        collection_rate = (float(collected_amount) / float(total_amount) * 100) if total_amount > 0 else 0
        
        return {
            "total_premiums": total_premiums,
            "paid_premiums": paid_premiums,
            "due_premiums": due_premiums,
            "overdue_premiums": overdue_premiums,
            "total_premium_amount": float(total_amount),
            "total_collected": float(collected_amount),
            "total_outstanding": float(outstanding_amount),
            "collection_rate": round(collection_rate, 2)
        }
