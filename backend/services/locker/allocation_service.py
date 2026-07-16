"""
Locker Allocation Service

Handles customer locker allocation lifecycle including:
- Allocation creation and validation
- Rent tracking and calculations
- Renewal processing
- Closure and refund handling
- Expiry alerts
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from backend.shared.database.locker_models import (
    LockerMaster, LockerAllocation, LockerRentPayment
)
from backend.shared.database.customer_models import Customer
from backend.shared.common.response import CustomException


class AllocationService:
    """Service for managing locker allocations"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== ALLOCATION CRUD ====================
    
    def create_allocation(self, allocation_data: Dict[str, Any]) -> LockerAllocation:
        """
        Create new locker allocation
        
        Args:
            allocation_data: Allocation details including customer, locker, terms
            
        Returns:
            Created allocation
        """
        # Validate locker exists and is available
        locker = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.id == allocation_data['locker_id'],
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.is_deleted == False
            )
        ).first()
        
        if not locker:
            raise CustomException(status_code=404, message="Locker not found")
        
        if locker.status != 'available' or not locker.is_available:
            raise CustomException(
                status_code=400,
                message=f"Locker {locker.locker_number} is not available for allocation"
            )
        
        # Validate customer exists
        customer = self.db.query(Customer).filter(
            and_(
                Customer.id == allocation_data['customer_id'],
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False
            )
        ).first()
        
        if not customer:
            raise CustomException(status_code=404, message="Customer not found")
        
        # Check if customer already has an active locker
        existing_allocation = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.customer_id == allocation_data['customer_id'],
                LockerAllocation.status == 'active',
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.is_deleted == False
            )
        ).first()
        
        if existing_allocation:
            raise CustomException(
                status_code=400,
                message=f"Customer already has active allocation: {existing_allocation.allocation_number}"
            )
        
        # Validate dates
        start_date = allocation_data['agreement_start_date']
        end_date = allocation_data['agreement_end_date']
        
        if end_date <= start_date:
            raise CustomException(
                status_code=400,
                message="Agreement end date must be after start date"
            )
        
        # Calculate next rent due date based on frequency
        rent_frequency = allocation_data.get('rent_frequency', 'annual')
        next_rent_due = self._calculate_next_rent_due(start_date, rent_frequency)
        
        # Extract nominee details if provided
        nominee_details = allocation_data.pop('nominee_details', None)
        
        # Create allocation
        allocation = LockerAllocation(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            next_rent_due_date=next_rent_due,
            **allocation_data
        )
        
        # Add nominee details
        if nominee_details:
            allocation.nominee_name = nominee_details.get('nominee_name')
            allocation.nominee_relationship = nominee_details.get('nominee_relationship')
            allocation.nominee_dob = nominee_details.get('nominee_dob')
            allocation.nominee_address = nominee_details.get('nominee_address')
            allocation.nominee_id_proof_type = nominee_details.get('nominee_id_proof_type')
            allocation.nominee_id_proof_number = nominee_details.get('nominee_id_proof_number')
            allocation.nominee_percentage = nominee_details.get('nominee_percentage', 100)
        
        self.db.add(allocation)
        
        # Update locker status
        locker.status = 'allocated'
        locker.is_available = False
        locker.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(allocation)
        
        return allocation
    
    def get_allocation(self, allocation_id: uuid.UUID) -> Optional[LockerAllocation]:
        """Get allocation by ID"""
        allocation = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.id == allocation_id,
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.is_deleted == False
            )
        ).first()
        
        if not allocation:
            raise CustomException(status_code=404, message="Allocation not found")
        
        return allocation
    
    def get_allocation_by_number(self, allocation_number: str) -> Optional[LockerAllocation]:
        """Get allocation by allocation number"""
        allocation = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.allocation_number == allocation_number,
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.is_deleted == False
            )
        ).first()
        
        if not allocation:
            raise CustomException(status_code=404, message="Allocation not found")
        
        return allocation
    
    def list_allocations(
        self,
        customer_id: Optional[uuid.UUID] = None,
        locker_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        branch_id: Optional[uuid.UUID] = None,
        allocation_date_from: Optional[date] = None,
        allocation_date_to: Optional[date] = None,
        expiring_within_days: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LockerAllocation]:
        """List allocations with filters"""
        query = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.is_deleted == False
            )
        )
        
        if customer_id:
            query = query.filter(LockerAllocation.customer_id == customer_id)
        
        if locker_id:
            query = query.filter(LockerAllocation.locker_id == locker_id)
        
        if status:
            query = query.filter(LockerAllocation.status == status)
        
        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)
        
        if allocation_date_from:
            query = query.filter(LockerAllocation.allocation_date >= allocation_date_from)
        
        if allocation_date_to:
            query = query.filter(LockerAllocation.allocation_date <= allocation_date_to)
        
        if expiring_within_days:
            expiry_date = date.today() + timedelta(days=expiring_within_days)
            query = query.filter(
                and_(
                    LockerAllocation.agreement_end_date <= expiry_date,
                    LockerAllocation.status == 'active'
                )
            )
        
        allocations = query.order_by(LockerAllocation.allocation_date.desc()).offset(skip).limit(limit).all()
        return allocations
    
    def update_allocation(
        self,
        allocation_id: uuid.UUID,
        update_data: Dict[str, Any]
    ) -> LockerAllocation:
        """Update allocation details"""
        allocation = self.get_allocation(allocation_id)
        
        # Validate status change
        if 'status' in update_data:
            new_status = update_data['status']
            if allocation.status == 'closed' and new_status != 'closed':
                raise CustomException(
                    status_code=400,
                    message="Cannot reopen closed allocation"
                )
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(allocation, key) and value is not None:
                setattr(allocation, key, value)
        
        allocation.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(allocation)
        
        return allocation
    
    # ==================== RENT CALCULATIONS ====================
    
    def calculate_rent(
        self,
        allocation_id: uuid.UUID,
        period_from: date,
        period_to: date,
        include_gst: bool = True,
        include_penalty: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate rent for a period
        
        Args:
            allocation_id: Allocation to calculate rent for
            period_from: Start date
            period_to: End date
            include_gst: Whether to include GST
            include_penalty: Whether to calculate penalty for overdue
            
        Returns:
            Rent calculation breakdown
        """
        allocation = self.get_allocation(allocation_id)
        
        # Calculate number of days
        days = (period_to - period_from).days + 1
        
        if days <= 0:
            raise CustomException(
                status_code=400,
                message="Period end date must be after start date"
            )
        
        # Annual rent
        annual_rent = float(allocation.annual_rent)
        
        # Calculate prorated rent
        prorated_rent = (annual_rent / 365) * days
        
        # Calculate GST
        gst_amount = 0
        if include_gst and allocation.gst_applicable:
            gst_amount = prorated_rent * (float(allocation.gst_rate) / 100)
        
        # Calculate penalty if overdue
        penalty_amount = 0
        late_fee = 0
        days_overdue = 0
        
        if include_penalty and allocation.next_rent_due_date:
            if period_from > allocation.next_rent_due_date:
                days_overdue = (period_from - allocation.next_rent_due_date).days
                
                if days_overdue > 0:
                    # 2% penalty per month on outstanding rent
                    penalty_rate = 0.02
                    months_overdue = days_overdue / 30
                    penalty_amount = prorated_rent * penalty_rate * months_overdue
                    
                    # Fixed late fee
                    late_fee = 100.0  # ₹100 late fee
        
        total_amount = prorated_rent + gst_amount + penalty_amount + late_fee
        
        return {
            'allocation_number': allocation.allocation_number,
            'period_from': period_from,
            'period_to': period_to,
            'days': days,
            'base_rent': annual_rent,
            'prorated_rent': round(prorated_rent, 2),
            'gst_amount': round(gst_amount, 2),
            'penalty_amount': round(penalty_amount, 2),
            'late_fee': round(late_fee, 2),
            'total_amount': round(total_amount, 2),
            'gst_rate': float(allocation.gst_rate),
            'penalty_rate': 2.0,
            'days_overdue': days_overdue
        }
    
    def _calculate_next_rent_due(self, start_date: date, frequency: str) -> date:
        """Calculate next rent due date based on frequency"""
        if frequency == 'monthly':
            return start_date + timedelta(days=30)
        elif frequency == 'quarterly':
            return start_date + timedelta(days=90)
        elif frequency == 'semi_annual':
            return start_date + timedelta(days=180)
        else:  # annual
            return start_date + timedelta(days=365)
    
    # ==================== RENEWAL ====================
    
    def renew_allocation(
        self,
        allocation_id: uuid.UUID,
        new_end_date: date,
        annual_rent: Decimal,
        adjust_security_deposit: bool = False,
        additional_deposit: Decimal = Decimal('0'),
        remarks: Optional[str] = None
    ) -> LockerAllocation:
        """
        Renew an expiring or expired allocation
        
        Args:
            allocation_id: Allocation to renew
            new_end_date: New agreement end date
            annual_rent: Rent for renewed period
            adjust_security_deposit: Whether to adjust deposit
            additional_deposit: Additional deposit amount
            remarks: Renewal notes
            
        Returns:
            Renewed allocation
        """
        allocation = self.get_allocation(allocation_id)
        
        # Validate can be renewed
        if allocation.status == 'closed':
            raise CustomException(
                status_code=400,
                message="Cannot renew closed allocation"
            )
        
        # Check for outstanding rent
        if allocation.outstanding_rent > 0:
            raise CustomException(
                status_code=400,
                message=f"Cannot renew with outstanding rent: ₹{allocation.outstanding_rent}"
            )
        
        # Create new allocation record
        new_allocation = LockerAllocation(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            
            # Generate new numbers
            allocation_number=f"RENEW-{allocation.allocation_number}",
            agreement_number=f"AGR-RENEW-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            
            # Copy from original
            locker_id=allocation.locker_id,
            customer_id=allocation.customer_id,
            
            # New terms
            allocation_date=date.today(),
            agreement_start_date=allocation.agreement_end_date + timedelta(days=1),
            agreement_end_date=new_end_date,
            annual_rent=annual_rent,
            security_deposit=allocation.security_deposit + additional_deposit,
            
            # Copy settings
            rent_frequency=allocation.rent_frequency,
            gst_applicable=allocation.gst_applicable,
            gst_rate=allocation.gst_rate,
            operation_mode=allocation.operation_mode,
            
            # Keys carry over
            customer_key_number=allocation.customer_key_number,
            bank_key_number=allocation.bank_key_number,
            
            # Nominee carries over
            nominee_name=allocation.nominee_name,
            nominee_relationship=allocation.nominee_relationship,
            nominee_dob=allocation.nominee_dob,
            nominee_address=allocation.nominee_address,
            nominee_id_proof_type=allocation.nominee_id_proof_type,
            nominee_id_proof_number=allocation.nominee_id_proof_number,
            nominee_percentage=allocation.nominee_percentage,
            
            # Joint holders carry over
            joint_holder_1_id=allocation.joint_holder_1_id,
            joint_holder_2_id=allocation.joint_holder_2_id,
            
            # Renewal tracking
            parent_allocation_id=allocation.id,
            auto_renewal=allocation.auto_renewal,
            
            # Status
            status='active',
            
            # Notes
            remarks=remarks or f"Renewed from {allocation.allocation_number}"
        )
        
        # Calculate next rent due
        new_allocation.next_rent_due_date = self._calculate_next_rent_due(
            new_allocation.agreement_start_date,
            new_allocation.rent_frequency
        )
        
        self.db.add(new_allocation)
        
        # Close old allocation
        allocation.status = 'expired'
        allocation.closure_date = allocation.agreement_end_date
        allocation.closure_reason = 'Renewed'
        allocation.updated_by = self.user_id
        
        # Update renewal count
        new_allocation.renewal_count = allocation.renewal_count + 1
        
        self.db.commit()
        self.db.refresh(new_allocation)
        
        return new_allocation
    
    # ==================== CLOSURE ====================
    
    def close_allocation(
        self,
        allocation_id: uuid.UUID,
        closure_date: date,
        closure_reason: str,
        refund_security_deposit: bool = True,
        closure_charges: Decimal = Decimal('0'),
        final_settlement_amount: Optional[Decimal] = None,
        remarks: Optional[str] = None
    ) -> Tuple[LockerAllocation, Dict[str, Any]]:
        """
        Close allocation and calculate settlement
        
        Args:
            allocation_id: Allocation to close
            closure_date: Date of closure
            closure_reason: Reason for closure
            refund_security_deposit: Whether to refund deposit
            closure_charges: Any closure charges
            final_settlement_amount: Override calculated settlement
            remarks: Additional notes
            
        Returns:
            Tuple of (closed allocation, settlement breakdown)
        """
        allocation = self.get_allocation(allocation_id)
        
        if allocation.status == 'closed':
            raise CustomException(
                status_code=400,
                message="Allocation is already closed"
            )
        
        # Calculate settlement
        security_deposit = float(allocation.security_deposit)
        outstanding_rent = float(allocation.outstanding_rent)
        closure_charges_amt = float(closure_charges)
        
        # Calculate prorated rent if closing mid-period
        prorated_rent = 0
        if allocation.rent_paid_upto_date and closure_date > allocation.rent_paid_upto_date:
            days_used = (closure_date - allocation.rent_paid_upto_date).days
            annual_rent = float(allocation.annual_rent)
            prorated_rent = (annual_rent / 365) * days_used
        
        # Settlement calculation
        total_dues = outstanding_rent + prorated_rent + closure_charges_amt
        refund_amount = 0
        
        if refund_security_deposit:
            refund_amount = max(0, security_deposit - total_dues)
        
        if final_settlement_amount is not None:
            refund_amount = float(final_settlement_amount)
        
        # Update allocation
        allocation.status = 'closed'
        allocation.closure_date = closure_date
        allocation.closure_reason = closure_reason
        allocation.security_deposit_refunded = refund_security_deposit
        allocation.security_deposit_refund_date = closure_date if refund_security_deposit else None
        allocation.security_deposit_refund_amount = refund_amount
        allocation.closure_charges = closure_charges
        allocation.remarks = remarks
        allocation.updated_by = self.user_id
        
        # Free up the locker
        locker = self.db.query(LockerMaster).filter(
            LockerMaster.id == allocation.locker_id
        ).first()
        
        if locker:
            locker.status = 'available'
            locker.is_available = True
            locker.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(allocation)
        
        settlement = {
            'allocation_number': allocation.allocation_number,
            'closure_date': closure_date,
            'security_deposit': security_deposit,
            'outstanding_rent': outstanding_rent,
            'prorated_rent': round(prorated_rent, 2),
            'closure_charges': closure_charges_amt,
            'total_dues': round(total_dues, 2),
            'refund_amount': round(refund_amount, 2)
        }
        
        return allocation, settlement
    
    # ==================== ALERTS & REPORTS ====================
    
    def get_expiring_allocations(
        self,
        days_threshold: int = 30,
        branch_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Get allocations expiring soon
        
        Args:
            days_threshold: Consider allocations expiring within this many days
            branch_id: Filter by branch
            
        Returns:
            List of expiring allocations
        """
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)
        
        query = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.status == 'active',
                LockerAllocation.agreement_end_date <= threshold_date,
                LockerAllocation.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)
        
        allocations = query.order_by(LockerAllocation.agreement_end_date).all()
        
        result = []
        for allocation in allocations:
            days_to_expiry = (allocation.agreement_end_date - today).days
            
            # Get customer name
            customer = self.db.query(Customer).filter(Customer.id == allocation.customer_id).first()
            customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown"
            
            # Get locker number
            locker = self.db.query(LockerMaster).filter(LockerMaster.id == allocation.locker_id).first()
            locker_number = locker.locker_number if locker else "Unknown"
            
            result.append({
                'allocation_id': str(allocation.id),
                'allocation_number': allocation.allocation_number,
                'customer_name': customer_name,
                'locker_number': locker_number,
                'agreement_end_date': allocation.agreement_end_date,
                'days_to_expiry': days_to_expiry,
                'outstanding_rent': float(allocation.outstanding_rent),
                'auto_renewal': allocation.auto_renewal
            })
        
        return result
    
    def get_overdue_rents(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get allocations with overdue rent"""
        today = date.today()
        
        query = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.status == 'active',
                or_(
                    LockerAllocation.next_rent_due_date < today,
                    LockerAllocation.outstanding_rent > 0
                ),
                LockerAllocation.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)
        
        allocations = query.all()
        
        result = []
        for allocation in allocations:
            days_overdue = 0
            if allocation.next_rent_due_date:
                days_overdue = (today - allocation.next_rent_due_date).days
            
            customer = self.db.query(Customer).filter(Customer.id == allocation.customer_id).first()
            customer_name = f"{customer.first_name} {customer.last_name}" if customer else "Unknown"
            
            locker = self.db.query(LockerMaster).filter(LockerMaster.id == allocation.locker_id).first()
            locker_number = locker.locker_number if locker else "Unknown"
            
            result.append({
                'allocation_id': str(allocation.id),
                'allocation_number': allocation.allocation_number,
                'customer_name': customer_name,
                'locker_number': locker_number,
                'next_rent_due_date': allocation.next_rent_due_date,
                'days_overdue': days_overdue,
                'outstanding_rent': float(allocation.outstanding_rent)
            })
        
        return result
