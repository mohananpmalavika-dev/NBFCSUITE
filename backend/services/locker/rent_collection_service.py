"""
Locker Rent Collection Service

Handles rent management operations:
- Annual rent calculation
- Rent due date tracking
- Advance rent collection
- Pro-rata calculation
- Rent receipt generation
- Auto-debit from customer account
- Rent reminders
- Overdue rent tracking
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid

from backend.shared.database.locker_models import (
    LockerAllocation, LockerRentPayment, LockerRentReminder,
    LockerMaster
)
from backend.shared.common.exceptions import ValidationError, NotFoundError


class LockerRentCollectionService:
    """Service for locker rent collection and management"""

    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    # ============================================
    # Rent Calculation
    # ============================================

    def calculate_annual_rent(
        self,
        allocation_id: str,
        for_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Calculate annual rent for an allocation"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()

        if not allocation:
            raise NotFoundError(f"Allocation {allocation_id} not found")

        year = for_year or datetime.now().year
        base_rent = Decimal(str(allocation.annual_rent))
        
        # Apply GST if applicable
        gst_rate = Decimal('0.18')  # 18% GST
        gst_amount = base_rent * gst_rate
        
        total_rent = base_rent + gst_amount

        return {
            "allocation_id": allocation_id,
            "year": year,
            "base_rent": float(base_rent),
            "gst_rate": float(gst_rate * 100),
            "gst_amount": float(gst_amount),
            "total_annual_rent": float(total_rent),
            "rent_frequency": allocation.rent_frequency,
            "last_payment_date": allocation.rent_paid_upto_date.isoformat() if allocation.rent_paid_upto_date else None,
            "next_due_date": allocation.next_rent_due_date.isoformat() if allocation.next_rent_due_date else None
        }

    def calculate_prorata_rent(
        self,
        allocation_id: str,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """Calculate pro-rata rent for partial period"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()

        if not allocation:
            raise NotFoundError(f"Allocation {allocation_id} not found")

        if from_date >= to_date:
            raise ValidationError("From date must be before to date")

        # Calculate number of days
        days = (to_date - from_date).days + 1
        days_in_year = 365

        # Pro-rata calculation
        annual_rent = Decimal(str(allocation.annual_rent))
        prorata_rent = (annual_rent / days_in_year) * days

        # Apply GST
        gst_rate = Decimal('0.18')
        gst_amount = prorata_rent * gst_rate
        total_rent = prorata_rent + gst_amount

        return {
            "allocation_id": allocation_id,
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
            "number_of_days": days,
            "annual_rent": float(annual_rent),
            "prorata_rent": float(prorata_rent),
            "gst_rate": float(gst_rate * 100),
            "gst_amount": float(gst_amount),
            "total_amount": float(total_rent)
        }

    def calculate_advance_rent(
        self,
        allocation_id: str,
        number_of_years: int
    ) -> Dict[str, Any]:
        """Calculate advance rent for multiple years"""
        if number_of_years < 1 or number_of_years > 5:
            raise ValidationError("Advance rent can be collected for 1-5 years only")

        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()

        if not allocation:
            raise NotFoundError(f"Allocation {allocation_id} not found")

        annual_rent = Decimal(str(allocation.annual_rent))
        
        # Calculate total for multiple years
        total_base_rent = annual_rent * number_of_years
        
        # Apply discount for advance payment (e.g., 5% discount)
        discount_rate = Decimal('0.05')
        discount_amount = total_base_rent * discount_rate
        rent_after_discount = total_base_rent - discount_amount
        
        # Apply GST
        gst_rate = Decimal('0.18')
        gst_amount = rent_after_discount * gst_rate
        total_amount = rent_after_discount + gst_amount

        return {
            "allocation_id": allocation_id,
            "number_of_years": number_of_years,
            "annual_rent": float(annual_rent),
            "total_base_rent": float(total_base_rent),
            "discount_rate": float(discount_rate * 100),
            "discount_amount": float(discount_amount),
            "rent_after_discount": float(rent_after_discount),
            "gst_rate": float(gst_rate * 100),
            "gst_amount": float(gst_amount),
            "total_amount": float(total_amount),
            "valid_upto": (datetime.now().date() + timedelta(days=365 * number_of_years)).isoformat()
        }

    # ============================================
    # Rent Collection
    # ============================================

    async def collect_rent(
        self,
        allocation_id: str,
        payment_data: Dict[str, Any]
    ) -> LockerRentPayment:
        """Collect rent payment"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()

        if not allocation:
            raise NotFoundError(f"Allocation {allocation_id} not found")

        # Generate receipt number
        receipt_number = self._generate_receipt_number()

        # Create payment record
        payment = LockerRentPayment(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            receipt_number=receipt_number,
            allocation_id=allocation_id,
            customer_id=allocation.customer_id,
            payment_date=payment_data.get('payment_date', datetime.now().date()),
            payment_type=payment_data['payment_type'],
            payment_mode=payment_data['payment_mode'],
            total_amount=payment_data['total_amount'],
            rent_amount=payment_data.get('rent_amount', payment_data['total_amount']),
            gst_amount=payment_data.get('gst_amount', 0),
            penalty_amount=payment_data.get('penalty_amount', 0),
            late_fee_amount=payment_data.get('late_fee_amount', 0),
            payment_status='completed',
            period_from=payment_data.get('period_from'),
            period_to=payment_data.get('period_to'),
            transaction_reference=payment_data.get('transaction_reference'),
            remarks=payment_data.get('remarks'),
            created_by=self.user_id
        )

        self.db.add(payment)

        # Update allocation rent tracking
        if payment_data.get('period_to'):
            allocation.rent_paid_upto_date = payment_data['period_to']
            allocation.next_rent_due_date = payment_data['period_to'] + timedelta(days=1)
            allocation.total_rent_paid = (allocation.total_rent_paid or 0) + payment_data['total_amount']
            
            # Recalculate outstanding rent
            allocation.outstanding_rent = max(0, (allocation.outstanding_rent or 0) - payment_data['total_amount'])

        self.db.commit()
        self.db.refresh(payment)

        return payment

    async def auto_debit_rent(
        self,
        allocation_id: str,
        customer_account_id: str
    ) -> Dict[str, Any]:
        """Auto-debit rent from customer account"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()

        if not allocation:
            raise NotFoundError(f"Allocation {allocation_id} not found")

        # Check if rent is due
        if not allocation.next_rent_due_date or allocation.next_rent_due_date > datetime.now().date():
            raise ValidationError("No rent due for auto-debit")

        # Calculate rent amount
        rent_calc = self.calculate_annual_rent(allocation_id)
        
        # Simulate auto-debit (in real implementation, integrate with banking system)
        auto_debit_result = {
            "allocation_id": allocation_id,
            "customer_account_id": customer_account_id,
            "debit_amount": rent_calc['total_annual_rent'],
            "debit_date": datetime.now().date().isoformat(),
            "status": "success",
            "transaction_id": f"AD{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "message": "Rent auto-debited successfully"
        }

        # Create payment record
        await self.collect_rent(allocation_id, {
            "payment_type": "rent",
            "payment_mode": "auto_debit",
            "total_amount": rent_calc['total_annual_rent'],
            "rent_amount": rent_calc['base_rent'],
            "gst_amount": rent_calc['gst_amount'],
            "period_from": allocation.next_rent_due_date,
            "period_to": allocation.next_rent_due_date + timedelta(days=365),
            "transaction_reference": auto_debit_result['transaction_id'],
            "remarks": "Auto-debit rent payment"
        })

        return auto_debit_result

    # ============================================
    # Rent Reminders
    # ============================================

    async def send_rent_reminder(
        self,
        allocation_id: str,
        reminder_type: str,
        days_before_due: int
    ) -> Dict[str, Any]:
        """Send rent payment reminder"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()

        if not allocation:
            raise NotFoundError(f"Allocation {allocation_id} not found")

        # Create reminder record
        reminder = LockerRentReminder(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            allocation_id=allocation_id,
            customer_id=allocation.customer_id,
            reminder_type=reminder_type,
            due_date=allocation.next_rent_due_date,
            reminder_date=datetime.now().date(),
            days_before_due=days_before_due,
            rent_amount=allocation.annual_rent,
            sent_via="email,sms",
            status="sent",
            created_by=self.user_id
        )

        self.db.add(reminder)
        self.db.commit()

        return {
            "reminder_id": reminder.id,
            "allocation_id": allocation_id,
            "customer_id": allocation.customer_id,
            "reminder_type": reminder_type,
            "due_date": allocation.next_rent_due_date.isoformat(),
            "rent_amount": float(allocation.annual_rent),
            "days_before_due": days_before_due,
            "status": "sent"
        }

    async def send_bulk_reminders(
        self,
        reminder_type: str,
        days_before_due: int
    ) -> Dict[str, Any]:
        """Send reminders to all allocations with rent due"""
        target_date = datetime.now().date() + timedelta(days=days_before_due)

        # Find allocations with rent due on target date
        allocations = self.db.query(LockerAllocation).filter(
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False,
            LockerAllocation.status == 'active',
            LockerAllocation.next_rent_due_date == target_date
        ).all()

        sent_count = 0
        failed_count = 0
        results = []

        for allocation in allocations:
            try:
                result = await self.send_rent_reminder(
                    allocation.id,
                    reminder_type,
                    days_before_due
                )
                results.append(result)
                sent_count += 1
            except Exception as e:
                failed_count += 1
                results.append({
                    "allocation_id": allocation.id,
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "reminder_type": reminder_type,
            "days_before_due": days_before_due,
            "target_date": target_date.isoformat(),
            "total_allocations": len(allocations),
            "sent_count": sent_count,
            "failed_count": failed_count,
            "results": results
        }

    # ============================================
    # Rent Receipt Generation
    # ============================================

    def generate_rent_receipt(
        self,
        payment_id: str
    ) -> Dict[str, Any]:
        """Generate rent receipt"""
        payment = self.db.query(LockerRentPayment).filter(
            LockerRentPayment.id == payment_id,
            LockerRentPayment.tenant_id == self.tenant_id,
            LockerRentPayment.is_deleted == False
        ).first()

        if not payment:
            raise NotFoundError(f"Payment {payment_id} not found")

        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == payment.allocation_id
        ).first()

        locker = self.db.query(LockerMaster).filter(
            LockerMaster.id == allocation.locker_id
        ).first()

        receipt = {
            "receipt_number": payment.receipt_number,
            "receipt_date": payment.payment_date.isoformat(),
            "customer_id": payment.customer_id,
            "allocation_id": payment.allocation_id,
            "locker_number": locker.locker_number if locker else None,
            "locker_size": locker.locker_size if locker else None,
            "payment_details": {
                "payment_type": payment.payment_type,
                "payment_mode": payment.payment_mode,
                "payment_date": payment.payment_date.isoformat(),
                "transaction_reference": payment.transaction_reference
            },
            "rent_breakdown": {
                "rent_amount": float(payment.rent_amount),
                "gst_amount": float(payment.gst_amount),
                "penalty_amount": float(payment.penalty_amount),
                "late_fee_amount": float(payment.late_fee_amount),
                "total_amount": float(payment.total_amount)
            },
            "period": {
                "from_date": payment.period_from.isoformat() if payment.period_from else None,
                "to_date": payment.period_to.isoformat() if payment.period_to else None
            },
            "remarks": payment.remarks
        }

        return receipt

    # ============================================
    # Overdue Tracking
    # ============================================

    def get_overdue_allocations(
        self,
        branch_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get allocations with overdue rent"""
        query = self.db.query(LockerAllocation).filter(
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False,
            LockerAllocation.status == 'active',
            LockerAllocation.next_rent_due_date < datetime.now().date()
        )

        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)

        allocations = query.all()
        
        overdue_list = []
        for allocation in allocations:
            days_overdue = (datetime.now().date() - allocation.next_rent_due_date).days
            
            overdue_list.append({
                "allocation_id": allocation.id,
                "allocation_number": allocation.allocation_number,
                "customer_id": allocation.customer_id,
                "locker_id": allocation.locker_id,
                "rent_due_date": allocation.next_rent_due_date.isoformat(),
                "days_overdue": days_overdue,
                "annual_rent": float(allocation.annual_rent),
                "outstanding_rent": float(allocation.outstanding_rent or 0),
                "last_payment_date": allocation.rent_paid_upto_date.isoformat() if allocation.rent_paid_upto_date else None
            })

        return overdue_list

    def get_rent_collection_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get rent collection summary"""
        start = start_date or datetime.now().date().replace(day=1)
        end = end_date or datetime.now().date()

        query = self.db.query(LockerRentPayment).filter(
            LockerRentPayment.tenant_id == self.tenant_id,
            LockerRentPayment.is_deleted == False,
            LockerRentPayment.payment_date >= start,
            LockerRentPayment.payment_date <= end,
            LockerRentPayment.payment_status == 'completed'
        )

        if branch_id:
            query = query.join(LockerAllocation).join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )

        payments = query.all()

        total_collected = sum(p.total_amount for p in payments)
        rent_amount = sum(p.rent_amount for p in payments)
        gst_amount = sum(p.gst_amount for p in payments)
        penalty_amount = sum(p.penalty_amount for p in payments)
        late_fee_amount = sum(p.late_fee_amount for p in payments)

        # Payment mode breakdown
        by_mode = {}
        for payment in payments:
            mode = payment.payment_mode
            by_mode[mode] = by_mode.get(mode, 0) + payment.total_amount

        # Payment type breakdown
        by_type = {}
        for payment in payments:
            ptype = payment.payment_type
            by_type[ptype] = by_type.get(ptype, 0) + payment.total_amount

        return {
            "period": {
                "start_date": start.isoformat(),
                "end_date": end.isoformat()
            },
            "summary": {
                "total_payments": len(payments),
                "total_collected": float(total_collected),
                "rent_amount": float(rent_amount),
                "gst_amount": float(gst_amount),
                "penalty_amount": float(penalty_amount),
                "late_fee_amount": float(late_fee_amount)
            },
            "by_payment_mode": {k: float(v) for k, v in by_mode.items()},
            "by_payment_type": {k: float(v) for k, v in by_type.items()}
        }

    # ============================================
    # Helper Methods
    # ============================================

    def _generate_receipt_number(self) -> str:
        """Generate unique receipt number"""
        prefix = "RCP"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Get count of receipts today
        today = datetime.now().date()
        count = self.db.query(func.count(LockerRentPayment.id)).filter(
            LockerRentPayment.tenant_id == self.tenant_id,
            func.date(LockerRentPayment.created_at) == today
        ).scalar()

        return f"{prefix}{timestamp}{count + 1:04d}"

    async def get_upcoming_due_dates(
        self,
        days_ahead: int = 30,
        branch_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get allocations with rent due in upcoming days"""
        target_date = datetime.now().date() + timedelta(days=days_ahead)

        query = self.db.query(LockerAllocation).filter(
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False,
            LockerAllocation.status == 'active',
            LockerAllocation.next_rent_due_date <= target_date,
            LockerAllocation.next_rent_due_date >= datetime.now().date()
        )

        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)

        allocations = query.all()

        upcoming = []
        for allocation in allocations:
            days_until_due = (allocation.next_rent_due_date - datetime.now().date()).days
            
            upcoming.append({
                "allocation_id": allocation.id,
                "allocation_number": allocation.allocation_number,
                "customer_id": allocation.customer_id,
                "locker_id": allocation.locker_id,
                "rent_due_date": allocation.next_rent_due_date.isoformat(),
                "days_until_due": days_until_due,
                "annual_rent": float(allocation.annual_rent),
                "auto_renewal": allocation.auto_renewal
            })

        return upcoming
