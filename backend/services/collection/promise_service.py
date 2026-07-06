"""
Payment Promise Service
Manages payment promises (PTP) tracking and fulfillment
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.collection_models import (
    PaymentPromise,
    PromiseHistory,
    PromiseStatus,
    PromiseSource
)
from backend.shared.database.loan_models import LoanAccount


class PaymentPromiseService:
    """Service for payment promise management"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_promise(
        self,
        loan_account_id: int,
        customer_id: int,
        promise_amount: Decimal,
        promise_date: date,
        promised_by: PromiseSource,
        agent_id: Optional[int] = None,
        field_visit_id: Optional[int] = None,
        collection_action_id: Optional[int] = None,
        notes: Optional[str] = None,
        customer_remarks: Optional[str] = None
    ) -> PaymentPromise:
        """Create a new payment promise"""
        promise = PaymentPromise(
            tenant_id=self.tenant_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            promise_amount=promise_amount,
            promise_date=promise_date,
            promised_on_date=date.today(),
            promised_by=promised_by,
            recorded_by_user_id=self.user_id,
            agent_id=agent_id,
            field_visit_id=field_visit_id,
            collection_action_id=collection_action_id,
            promise_status=PromiseStatus.PENDING,
            notes=notes,
            customer_remarks=customer_remarks
        )
        
        self.db.add(promise)
        await self.db.commit()
        await self.db.refresh(promise)
        
        # Create history entry
        await self._create_history(promise.id, None, PromiseStatus.PENDING, "Promise created")
        
        return promise
    
    async def get_promise(self, promise_id: int) -> Optional[PaymentPromise]:
        """Get promise by ID"""
        query = select(PaymentPromise).where(
            and_(
                PaymentPromise.id == promise_id,
                PaymentPromise.tenant_id == self.tenant_id,
                PaymentPromise.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_loan_promises(
        self,
        loan_account_id: int,
        status: Optional[PromiseStatus] = None
    ) -> List[PaymentPromise]:
        """Get all promises for a loan account"""
        conditions = [
            PaymentPromise.tenant_id == self.tenant_id,
            PaymentPromise.loan_account_id == loan_account_id,
            PaymentPromise.is_deleted == False
        ]
        
        if status:
            conditions.append(PaymentPromise.promise_status == status)
        
        query = select(PaymentPromise).where(and_(*conditions)).order_by(
            desc(PaymentPromise.promise_date)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_pending_promises(
        self,
        due_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get pending promises (for follow-up)"""
        conditions = [
            PaymentPromise.tenant_id == self.tenant_id,
            PaymentPromise.is_deleted == False,
            PaymentPromise.promise_status == PromiseStatus.PENDING
        ]
        
        if due_date:
            conditions.append(PaymentPromise.promise_date <= due_date)
        else:
            # Default to next 7 days
            conditions.append(
                PaymentPromise.promise_date <= date.today() + timedelta(days=7)
            )
        
        # Count total
        count_query = select(func.count(PaymentPromise.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get promises
        query = select(PaymentPromise).where(and_(*conditions)).order_by(
            PaymentPromise.promise_date
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        promises = result.scalars().all()
        
        return {
            "promises": promises,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            }
        }
    
    async def update_promise_status(
        self,
        promise_id: int,
        new_status: PromiseStatus,
        actual_payment_amount: Optional[Decimal] = None,
        actual_payment_date: Optional[date] = None,
        payment_transaction_id: Optional[int] = None,
        broken_reason: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> Optional[PaymentPromise]:
        """Update promise status"""
        promise = await self.get_promise(promise_id)
        if not promise:
            return None
        
        old_status = promise.promise_status
        promise.promise_status = new_status
        
        if actual_payment_amount:
            promise.actual_payment_amount = actual_payment_amount
        if actual_payment_date:
            promise.actual_payment_date = actual_payment_date
        if payment_transaction_id:
            promise.payment_transaction_id = payment_transaction_id
        if broken_reason:
            promise.broken_reason = broken_reason
        
        promise.updated_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(promise)
        
        # Create history entry
        await self._create_history(promise_id, old_status, new_status, remarks)
        
        return promise
    
    async def reschedule_promise(
        self,
        promise_id: int,
        new_promise_date: date,
        new_promise_amount: Optional[Decimal] = None,
        remarks: Optional[str] = None
    ) -> PaymentPromise:
        """Reschedule a promise"""
        old_promise = await self.get_promise(promise_id)
        if not old_promise:
            raise ValueError("Promise not found")
        
        # Mark old promise as rescheduled
        await self.update_promise_status(
            promise_id,
            PromiseStatus.RESCHEDULED,
            remarks=remarks
        )
        
        # Create new promise
        new_promise = await self.create_promise(
            loan_account_id=old_promise.loan_account_id,
            customer_id=old_promise.customer_id,
            promise_amount=new_promise_amount or old_promise.promise_amount,
            promise_date=new_promise_date,
            promised_by=old_promise.promised_by,
            agent_id=old_promise.agent_id,
            notes=f"Rescheduled from promise #{promise_id}"
        )
        
        # Link the promises
        old_promise.rescheduled_promise_id = new_promise.id
        await self.db.commit()
        
        return new_promise
    
    async def check_promise_fulfillment(self) -> Dict[str, Any]:
        """
        Check all pending promises and mark as kept/broken
        Should be run daily
        """
        today = date.today()
        
        # Get promises due today or earlier
        query = select(PaymentPromise).where(
            and_(
                PaymentPromise.tenant_id == self.tenant_id,
                PaymentPromise.is_deleted == False,
                PaymentPromise.promise_status == PromiseStatus.PENDING,
                PaymentPromise.promise_date <= today
            )
        )
        
        result = await self.db.execute(query)
        promises = result.scalars().all()
        
        kept_count = 0
        broken_count = 0
        
        for promise in promises:
            # Check if payment received on promise date
            # This would need to check loan transactions
            # Simplified: mark as broken if overdue by 2 days
            if (today - promise.promise_date).days > 2:
                await self.update_promise_status(
                    promise.id,
                    PromiseStatus.BROKEN,
                    broken_reason="Payment not received within grace period",
                    remarks="Auto-marked by system"
                )
                broken_count += 1
        
        return {
            "total_promises_checked": len(promises),
            "kept_count": kept_count,
            "broken_count": broken_count,
            "check_date": today.isoformat()
        }
    
    async def get_promise_analytics(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get promise analytics and metrics"""
        if not from_date:
            from_date = date.today() - timedelta(days=30)
        if not to_date:
            to_date = date.today()
        
        # Overall promise statistics
        query = select(
            PaymentPromise.promise_status,
            func.count(PaymentPromise.id).label("count"),
            func.sum(PaymentPromise.promise_amount).label("total_amount"),
            func.sum(PaymentPromise.actual_payment_amount).label("actual_amount")
        ).where(
            and_(
                PaymentPromise.tenant_id == self.tenant_id,
                PaymentPromise.is_deleted == False,
                PaymentPromise.promised_on_date >= from_date,
                PaymentPromise.promised_on_date <= to_date
            )
        ).group_by(PaymentPromise.promise_status)
        
        result = await self.db.execute(query)
        stats = result.all()
        
        status_breakdown = {}
        total_promises = 0
        total_promised_amount = Decimal("0")
        total_collected_amount = Decimal("0")
        
        for row in stats:
            status_breakdown[row.promise_status.value] = {
                "count": row.count,
                "promised_amount": float(row.total_amount or 0),
                "collected_amount": float(row.actual_amount or 0)
            }
            total_promises += row.count
            total_promised_amount += (row.total_amount or Decimal("0"))
            total_collected_amount += (row.actual_amount or Decimal("0"))
        
        # Calculate fulfillment rate
        kept_count = status_breakdown.get(PromiseStatus.KEPT.value, {}).get("count", 0)
        partially_kept_count = status_breakdown.get(PromiseStatus.PARTIALLY_KEPT.value, {}).get("count", 0)
        broken_count = status_breakdown.get(PromiseStatus.BROKEN.value, {}).get("count", 0)
        
        fulfillment_rate = (
            (kept_count + partially_kept_count) / total_promises * 100
            if total_promises > 0 else 0
        )
        
        return {
            "period": {
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat()
            },
            "summary": {
                "total_promises": total_promises,
                "total_promised_amount": float(total_promised_amount),
                "total_collected_amount": float(total_collected_amount),
                "fulfillment_rate": round(fulfillment_rate, 2)
            },
            "status_breakdown": status_breakdown
        }
    
    async def _create_history(
        self,
        promise_id: int,
        old_status: Optional[PromiseStatus],
        new_status: PromiseStatus,
        remarks: Optional[str] = None
    ):
        """Create promise history entry"""
        history = PromiseHistory(
            tenant_id=self.tenant_id,
            promise_id=promise_id,
            status_changed_from=old_status,
            status_changed_to=new_status,
            changed_by=self.user_id,
            remarks=remarks
        )
        
        self.db.add(history)
        await self.db.commit()
    
    async def send_promise_reminder(self, promise_id: int) -> bool:
        """
        Send reminder for upcoming promise
        This would integrate with notification service
        """
        promise = await self.get_promise(promise_id)
        if not promise:
            return False
        
        # Mark reminder as sent
        promise.reminder_sent = True
        promise.reminder_sent_date = datetime.now()
        await self.db.commit()
        
        # TODO: Integrate with notification service to send SMS/Email
        
        return True
