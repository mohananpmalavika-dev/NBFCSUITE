"""
Locker Rent Payment Service

Handles rent payment processing including:
- Payment recording and validation
- Receipt generation
- Outstanding tracking
- Payment history
- Revenue analytics
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from backend.shared.database.locker_models import (
    LockerAllocation, LockerRentPayment, LockerMaster
)
from backend.shared.database.customer_models import Customer
from backend.shared.common.response import CustomException


class PaymentService:
    """Service for managing rent payments"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== PAYMENT CRUD ====================
    
    def record_payment(self, payment_data: Dict[str, Any]) -> LockerRentPayment:
        """
        Record a rent payment
        
        Args:
            payment_data: Payment details
            
        Returns:
            Created payment record
        """
        # Validate allocation exists
        allocation = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.id == payment_data['allocation_id'],
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.is_deleted == False
            )
        ).first()
        
        if not allocation:
            raise CustomException(status_code=404, message="Allocation not found")
        
        # Validate customer matches
        if str(allocation.customer_id) != str(payment_data['customer_id']):
            raise CustomException(
                status_code=400,
                message="Customer does not match allocation"
            )
        
        # Check for duplicate receipt number
        existing = self.db.query(LockerRentPayment).filter(
            and_(
                LockerRentPayment.receipt_number == payment_data['receipt_number'],
                LockerRentPayment.tenant_id == self.tenant_id,
                LockerRentPayment.is_deleted == False
            )
        ).first()
        
        if existing:
            raise CustomException(
                status_code=400,
                message=f"Receipt number {payment_data['receipt_number']} already exists"
            )
        
        # Create payment
        payment = LockerRentPayment(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            received_by=self.user_id,
            **payment_data
        )
        
        self.db.add(payment)
        
        # Update allocation based on payment type
        if payment_data['payment_type'] == 'security_deposit':
            allocation.security_deposit_paid = True
            allocation.security_deposit_paid_date = payment_data['payment_date']
            allocation.security_deposit_receipt_number = payment_data['receipt_number']
        
        elif payment_data['payment_type'] == 'rent':
            # Update rent tracking
            allocation.total_rent_paid += payment_data['total_amount']
            
            # Update rent paid upto date
            if payment_data.get('period_to'):
                allocation.rent_paid_upto_date = payment_data['period_to']
                
                # Calculate next rent due
                next_due = self._calculate_next_rent_due(
                    payment_data['period_to'],
                    allocation.rent_frequency
                )
                allocation.next_rent_due_date = next_due
            
            # Reduce outstanding rent
            if allocation.outstanding_rent > 0:
                reduction = min(
                    float(allocation.outstanding_rent),
                    float(payment_data['rent_amount'])
                )
                allocation.outstanding_rent -= Decimal(str(reduction))
        
        elif payment_data['payment_type'] in ['penalty', 'late_fee']:
            allocation.total_penalties_paid += payment_data['total_amount']
        
        allocation.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def get_payment(self, payment_id: uuid.UUID) -> Optional[LockerRentPayment]:
        """Get payment by ID"""
        payment = self.db.query(LockerRentPayment).filter(
            and_(
                LockerRentPayment.id == payment_id,
                LockerRentPayment.tenant_id == self.tenant_id,
                LockerRentPayment.is_deleted == False
            )
        ).first()
        
        if not payment:
            raise CustomException(status_code=404, message="Payment not found")
        
        return payment
    
    def get_payment_by_receipt(self, receipt_number: str) -> Optional[LockerRentPayment]:
        """Get payment by receipt number"""
        payment = self.db.query(LockerRentPayment).filter(
            and_(
                LockerRentPayment.receipt_number == receipt_number,
                LockerRentPayment.tenant_id == self.tenant_id,
                LockerRentPayment.is_deleted == False
            )
        ).first()
        
        if not payment:
            raise CustomException(status_code=404, message="Payment not found")
        
        return payment
    
    def list_payments(
        self,
        allocation_id: Optional[uuid.UUID] = None,
        customer_id: Optional[uuid.UUID] = None,
        payment_type: Optional[str] = None,
        payment_mode: Optional[str] = None,
        payment_status: Optional[str] = None,
        payment_date_from: Optional[date] = None,
        payment_date_to: Optional[date] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LockerRentPayment]:
        """List payments with filters"""
        query = self.db.query(LockerRentPayment).filter(
            and_(
                LockerRentPayment.tenant_id == self.tenant_id,
                LockerRentPayment.is_deleted == False
            )
        )
        
        if allocation_id:
            query = query.filter(LockerRentPayment.allocation_id == allocation_id)
        
        if customer_id:
            query = query.filter(LockerRentPayment.customer_id == customer_id)
        
        if payment_type:
            query = query.filter(LockerRentPayment.payment_type == payment_type)
        
        if payment_mode:
            query = query.filter(LockerRentPayment.payment_mode == payment_mode)
        
        if payment_status:
            query = query.filter(LockerRentPayment.payment_status == payment_status)
        
        if payment_date_from:
            query = query.filter(LockerRentPayment.payment_date >= payment_date_from)
        
        if payment_date_to:
            query = query.filter(LockerRentPayment.payment_date <= payment_date_to)
        
        if min_amount:
            query = query.filter(LockerRentPayment.total_amount >= min_amount)
        
        if max_amount:
            query = query.filter(LockerRentPayment.total_amount <= max_amount)
        
        payments = query.order_by(LockerRentPayment.payment_date.desc()).offset(skip).limit(limit).all()
        return payments
    
    def update_payment(
        self,
        payment_id: uuid.UUID,
        update_data: Dict[str, Any]
    ) -> LockerRentPayment:
        """Update payment details"""
        payment = self.get_payment(payment_id)
        
        # Only allow updating certain fields
        allowed_fields = ['payment_status', 'clearance_date', 'remarks']
        
        for key, value in update_data.items():
            if key in allowed_fields and hasattr(payment, key) and value is not None:
                setattr(payment, key, value)
        
        payment.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def cancel_payment(
        self,
        payment_id: uuid.UUID,
        reason: str
    ) -> LockerRentPayment:
        """Cancel a payment"""
        payment = self.get_payment(payment_id)
        
        if payment.payment_status == 'cancelled':
            raise CustomException(
                status_code=400,
                message="Payment is already cancelled"
            )
        
        # Update payment status
        payment.payment_status = 'cancelled'
        payment.remarks = f"Cancelled: {reason}"
        payment.updated_by = self.user_id
        
        # Reverse allocation updates
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == payment.allocation_id
        ).first()
        
        if allocation:
            if payment.payment_type == 'rent':
                allocation.total_rent_paid -= payment.total_amount
                allocation.outstanding_rent += payment.rent_amount
            elif payment.payment_type in ['penalty', 'late_fee']:
                allocation.total_penalties_paid -= payment.total_amount
            
            allocation.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    # ==================== PAYMENT HELPERS ====================
    
    def _calculate_next_rent_due(self, paid_upto: date, frequency: str) -> date:
        """Calculate next rent due date"""
        if frequency == 'monthly':
            return paid_upto + timedelta(days=30)
        elif frequency == 'quarterly':
            return paid_upto + timedelta(days=90)
        elif frequency == 'semi_annual':
            return paid_upto + timedelta(days=180)
        else:  # annual
            return paid_upto + timedelta(days=365)
    
    # ==================== PAYMENT HISTORY ====================
    
    def get_payment_history(
        self,
        allocation_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Get complete payment history for an allocation
        
        Returns:
            Payment history with summary
        """
        allocation = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.id == allocation_id,
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.is_deleted == False
            )
        ).first()
        
        if not allocation:
            raise CustomException(status_code=404, message="Allocation not found")
        
        # Get all payments
        payments = self.db.query(LockerRentPayment).filter(
            and_(
                LockerRentPayment.allocation_id == allocation_id,
                LockerRentPayment.tenant_id == self.tenant_id,
                LockerRentPayment.is_deleted == False
            )
        ).order_by(LockerRentPayment.payment_date).all()
        
        # Calculate totals by type
        total_rent = sum(
            float(p.rent_amount) for p in payments
            if p.payment_type == 'rent' and p.payment_status == 'completed'
        )
        total_penalties = sum(
            float(p.penalty_amount) + float(p.late_fee_amount) for p in payments
            if p.payment_status == 'completed'
        )
        total_paid = sum(
            float(p.total_amount) for p in payments
            if p.payment_status == 'completed'
        )
        
        payment_list = []
        for p in payments:
            payment_list.append({
                'id': str(p.id),
                'receipt_number': p.receipt_number,
                'payment_date': p.payment_date,
                'payment_type': p.payment_type,
                'payment_mode': p.payment_mode,
                'total_amount': float(p.total_amount),
                'rent_amount': float(p.rent_amount),
                'gst_amount': float(p.gst_amount),
                'penalty_amount': float(p.penalty_amount),
                'late_fee_amount': float(p.late_fee_amount),
                'payment_status': p.payment_status,
                'period_from': p.period_from,
                'period_to': p.period_to
            })
        
        return {
            'allocation_number': allocation.allocation_number,
            'total_payments': len(payments),
            'total_rent_paid': round(total_rent, 2),
            'total_penalties_paid': round(total_penalties, 2),
            'total_amount_paid': round(total_paid, 2),
            'outstanding_rent': float(allocation.outstanding_rent),
            'payments': payment_list
        }
    
    # ==================== REVENUE ANALYTICS ====================
    
    def get_revenue_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        branch_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Get revenue statistics for a period
        
        Returns:
            Revenue breakdown and analytics
        """
        # Default to current year
        if not start_date:
            start_date = date(date.today().year, 1, 1)
        if not end_date:
            end_date = date.today()
        
        query = self.db.query(LockerRentPayment).filter(
            and_(
                LockerRentPayment.tenant_id == self.tenant_id,
                LockerRentPayment.payment_date >= start_date,
                LockerRentPayment.payment_date <= end_date,
                LockerRentPayment.payment_status == 'completed',
                LockerRentPayment.is_deleted == False
            )
        )
        
        # Filter by branch if provided
        if branch_id:
            query = query.join(LockerAllocation).join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )
        
        payments = query.all()
        
        # Calculate totals
        total_revenue = sum(float(p.total_amount) for p in payments)
        rent_revenue = sum(float(p.rent_amount) for p in payments)
        deposit_revenue = sum(
            float(p.total_amount) for p in payments
            if p.payment_type == 'security_deposit'
        )
        penalty_revenue = sum(
            float(p.penalty_amount) + float(p.late_fee_amount) for p in payments
        )
        other_revenue = sum(
            float(p.other_charges) for p in payments
        )
        
        # Revenue by month
        revenue_by_month = []
        monthly_data = {}
        
        for p in payments:
            month_key = p.payment_date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = 0
            monthly_data[month_key] += float(p.total_amount)
        
        for month, amount in sorted(monthly_data.items()):
            revenue_by_month.append({
                'month': month,
                'revenue': round(amount, 2)
            })
        
        # Revenue by branch
        revenue_by_branch = []
        if not branch_id:
            branch_data = {}
            for p in payments:
                allocation = self.db.query(LockerAllocation).filter(
                    LockerAllocation.id == p.allocation_id
                ).first()
                if allocation:
                    locker = self.db.query(LockerMaster).filter(
                        LockerMaster.id == allocation.locker_id
                    ).first()
                    if locker:
                        branch = locker.branch_name or 'Unknown'
                        if branch not in branch_data:
                            branch_data[branch] = 0
                        branch_data[branch] += float(p.total_amount)
            
            for branch, amount in branch_data.items():
                revenue_by_branch.append({
                    'branch': branch,
                    'revenue': round(amount, 2)
                })
        
        # Calculate outstanding rent across all active allocations
        outstanding_query = self.db.query(
            func.sum(LockerAllocation.outstanding_rent)
        ).filter(
            and_(
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.status == 'active',
                LockerAllocation.is_deleted == False
            )
        )
        
        if branch_id:
            outstanding_query = outstanding_query.join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )
        
        outstanding_rent = outstanding_query.scalar() or 0
        
        # Calculate expected annual revenue (from active allocations)
        expected_query = self.db.query(
            func.sum(LockerAllocation.annual_rent)
        ).filter(
            and_(
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.status == 'active',
                LockerAllocation.is_deleted == False
            )
        )
        
        if branch_id:
            expected_query = expected_query.join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )
        
        expected_annual_revenue = expected_query.scalar() or 0
        
        return {
            'total_revenue': round(total_revenue, 2),
            'rent_revenue': round(rent_revenue, 2),
            'deposit_revenue': round(deposit_revenue, 2),
            'penalty_revenue': round(penalty_revenue, 2),
            'other_revenue': round(other_revenue, 2),
            'outstanding_rent': float(outstanding_rent),
            'expected_annual_revenue': float(expected_annual_revenue),
            'revenue_by_month': revenue_by_month,
            'revenue_by_branch': revenue_by_branch,
            'period_start': start_date,
            'period_end': end_date
        }
    
    def get_collection_efficiency(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Calculate collection efficiency metrics
        
        Returns:
            Collection efficiency statistics
        """
        # Get active allocations
        query = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.status == 'active',
                LockerAllocation.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)
        
        allocations = query.all()
        
        total_allocations = len(allocations)
        on_time_payments = 0
        overdue_payments = 0
        total_expected = 0
        total_collected = 0
        total_outstanding = 0
        
        today = date.today()
        
        for allocation in allocations:
            total_expected += float(allocation.annual_rent)
            total_collected += float(allocation.total_rent_paid)
            total_outstanding += float(allocation.outstanding_rent)
            
            if allocation.next_rent_due_date:
                if allocation.next_rent_due_date >= today:
                    on_time_payments += 1
                else:
                    overdue_payments += 1
        
        collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0
        on_time_rate = (on_time_payments / total_allocations * 100) if total_allocations > 0 else 0
        
        return {
            'total_active_allocations': total_allocations,
            'on_time_payments': on_time_payments,
            'overdue_payments': overdue_payments,
            'total_expected_revenue': round(total_expected, 2),
            'total_collected_revenue': round(total_collected, 2),
            'total_outstanding': round(total_outstanding, 2),
            'collection_rate': round(collection_rate, 2),
            'on_time_payment_rate': round(on_time_rate, 2)
        }
    
    # ==================== BULK OPERATIONS ====================
    
    def bulk_record_payments(
        self,
        payments_data: List[Dict[str, Any]]
    ) -> List[LockerRentPayment]:
        """
        Record multiple payments at once
        
        Args:
            payments_data: List of payment records
            
        Returns:
            List of created payments
        """
        created_payments = []
        
        for payment_data in payments_data:
            try:
                payment = self.record_payment(payment_data)
                created_payments.append(payment)
            except CustomException as e:
                # Log error but continue with other payments
                continue
        
        return created_payments
