"""
Locker Rent Arrears Service

Handles rent arrears and penalty operations:
- Overdue notification
- Penalty calculation
- Final notice before locker breaking
- Legal notice
- Breaking procedure (after 3 years non-payment)
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid

from backend.shared.database.locker_models import (
    LockerAllocation, LockerRentPayment, LockerArrears,
    LockerNotice, LockerMaster
)
from backend.shared.common.exceptions import ValidationError, NotFoundError


class LockerRentArrearsService:
    """Service for rent arrears and overdue management"""

    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    # ============================================
    # Penalty Calculation
    # ============================================

    def calculate_penalty(
        self,
        allocation_id: str,
        overdue_days: int,
        overdue_amount: Decimal
    ) -> Dict[str, Any]:
        """Calculate penalty for overdue rent"""
        # Penalty structure:
        # 1-30 days: 2% per month
        # 31-60 days: 3% per month
        # 61-90 days: 4% per month
        # 91+ days: 5% per month

        if overdue_days <= 0:
            return {
                "overdue_days": 0,
                "penalty_rate": 0,
                "penalty_amount": 0,
                "late_fee": 0,
                "total_penalty": 0
            }

        # Determine penalty rate
        if overdue_days <= 30:
            penalty_rate = Decimal('0.02')
        elif overdue_days <= 60:
            penalty_rate = Decimal('0.03')
        elif overdue_days <= 90:
            penalty_rate = Decimal('0.04')
        else:
            penalty_rate = Decimal('0.05')

        # Calculate penalty (monthly rate, pro-rated for days)
        months_overdue = Decimal(str(overdue_days)) / Decimal('30')
        penalty_amount = overdue_amount * penalty_rate * months_overdue

        # Add flat late fee after 30 days
        late_fee = Decimal('500') if overdue_days > 30 else Decimal('0')

        total_penalty = penalty_amount + late_fee

        return {
            "overdue_days": overdue_days,
            "penalty_rate": float(penalty_rate * 100),
            "penalty_amount": float(penalty_amount),
            "late_fee": float(late_fee),
            "total_penalty": float(total_penalty),
            "overdue_amount": float(overdue_amount),
            "total_payable": float(overdue_amount + total_penalty)
        }

    def get_allocation_arrears(
        self,
        allocation_id: str
    ) -> Dict[str, Any]:
        """Get arrears details for an allocation"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()

        if not allocation:
            raise NotFoundError(f"Allocation {allocation_id} not found")

        if not allocation.next_rent_due_date or allocation.next_rent_due_date >= datetime.now().date():
            return {
                "allocation_id": allocation_id,
                "has_arrears": False,
                "message": "No arrears"
            }

        overdue_days = (datetime.now().date() - allocation.next_rent_due_date).days
        overdue_amount = Decimal(str(allocation.annual_rent))

        penalty_calc = self.calculate_penalty(allocation_id, overdue_days, overdue_amount)

        # Get existing notices
        notices = self.db.query(LockerNotice).filter(
            LockerNotice.allocation_id == allocation_id,
            LockerNotice.tenant_id == self.tenant_id,
            LockerNotice.is_deleted == False
        ).order_by(LockerNotice.notice_date.desc()).all()

        return {
            "allocation_id": allocation_id,
            "has_arrears": True,
            "rent_due_date": allocation.next_rent_due_date.isoformat(),
            "overdue_days": overdue_days,
            "overdue_amount": float(overdue_amount),
            "penalty_details": penalty_calc,
            "total_outstanding": float(overdue_amount + Decimal(str(penalty_calc['total_penalty']))),
            "notices_sent": len(notices),
            "last_notice_date": notices[0].notice_date.isoformat() if notices else None,
            "last_notice_type": notices[0].notice_type if notices else None
        }

    # ============================================
    # Notice Generation
    # ============================================

    async def send_overdue_notification(
        self,
        allocation_id: str,
        notification_type: str = "first_reminder"
    ) -> Dict[str, Any]:
        """Send overdue rent notification"""
        arrears = self.get_allocation_arrears(allocation_id)

        if not arrears.get('has_arrears'):
            raise ValidationError("No arrears found for this allocation")

        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id
        ).first()

        # Create notice record
        notice = LockerNotice(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            notice_number=self._generate_notice_number(),
            allocation_id=allocation_id,
            customer_id=allocation.customer_id,
            notice_type=notification_type,
            notice_date=datetime.now().date(),
            due_amount=arrears['overdue_amount'],
            penalty_amount=arrears['penalty_details']['total_penalty'],
            total_amount=arrears['total_outstanding'],
            overdue_days=arrears['overdue_days'],
            notice_content=self._generate_notice_content(notification_type, arrears),
            sent_via="email,sms,post",
            status="sent",
            created_by=self.user_id
        )

        self.db.add(notice)
        self.db.commit()

        return {
            "notice_id": notice.id,
            "notice_number": notice.notice_number,
            "allocation_id": allocation_id,
            "notice_type": notification_type,
            "notice_date": notice.notice_date.isoformat(),
            "total_amount": float(notice.total_amount),
            "status": "sent"
        }

    async def send_final_notice(
        self,
        allocation_id: str
    ) -> Dict[str, Any]:
        """Send final notice before locker breaking"""
        arrears = self.get_allocation_arrears(allocation_id)

        if not arrears.get('has_arrears'):
            raise ValidationError("No arrears found for this allocation")

        if arrears['overdue_days'] < 90:
            raise ValidationError("Final notice can only be sent after 90 days of overdue")

        return await self.send_overdue_notification(allocation_id, "final_notice")

    async def send_legal_notice(
        self,
        allocation_id: str
    ) -> Dict[str, Any]:
        """Send legal notice for long-term non-payment"""
        arrears = self.get_allocation_arrears(allocation_id)

        if not arrears.get('has_arrears'):
            raise ValidationError("No arrears found for this allocation")

        if arrears['overdue_days'] < 180:
            raise ValidationError("Legal notice can only be sent after 180 days of overdue")

        return await self.send_overdue_notification(allocation_id, "legal_notice")

    # ============================================
    # Locker Breaking Procedure
    # ============================================

    def check_breaking_eligibility(
        self,
        allocation_id: str
    ) -> Dict[str, Any]:
        """Check if locker is eligible for breaking (3 years non-payment)"""
        arrears = self.get_allocation_arrears(allocation_id)

        if not arrears.get('has_arrears'):
            return {
                "eligible": False,
                "reason": "No arrears"
            }

        # Check if 3 years (1095 days) have passed
        three_years_days = 1095
        is_eligible = arrears['overdue_days'] >= three_years_days

        # Check if all notices have been sent
        notices = self.db.query(LockerNotice).filter(
            LockerNotice.allocation_id == allocation_id,
            LockerNotice.tenant_id == self.tenant_id,
            LockerNotice.is_deleted == False
        ).all()

        required_notices = ['first_reminder', 'second_reminder', 'final_notice', 'legal_notice']
        sent_notice_types = [n.notice_type for n in notices]
        all_notices_sent = all(nt in sent_notice_types for nt in required_notices)

        return {
            "allocation_id": allocation_id,
            "eligible": is_eligible and all_notices_sent,
            "overdue_days": arrears['overdue_days'],
            "years_overdue": arrears['overdue_days'] / 365,
            "three_year_threshold": three_years_days,
            "days_until_eligible": max(0, three_years_days - arrears['overdue_days']),
            "all_notices_sent": all_notices_sent,
            "missing_notices": [nt for nt in required_notices if nt not in sent_notice_types],
            "total_outstanding": arrears['total_outstanding']
        }

    async def initiate_breaking_procedure(
        self,
        allocation_id: str,
        authorized_by: str,
        witnesses: List[str]
    ) -> Dict[str, Any]:
        """Initiate locker breaking procedure"""
        eligibility = self.check_breaking_eligibility(allocation_id)

        if not eligibility['eligible']:
            raise ValidationError(
                f"Locker not eligible for breaking. Missing notices: {eligibility.get('missing_notices', [])}. "
                f"Days until eligible: {eligibility.get('days_until_eligible', 0)}"
            )

        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id
        ).first()

        # Create breaking notice
        breaking_notice = LockerNotice(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            notice_number=self._generate_notice_number(),
            allocation_id=allocation_id,
            customer_id=allocation.customer_id,
            notice_type="breaking_notice",
            notice_date=datetime.now().date(),
            due_amount=eligibility['total_outstanding'],
            total_amount=eligibility['total_outstanding'],
            overdue_days=eligibility['overdue_days'],
            notice_content=f"Notice for locker breaking due to non-payment for {eligibility['years_overdue']:.1f} years",
            authorized_by=authorized_by,
            witnesses=",".join(witnesses),
            sent_via="registered_post,email",
            status="sent",
            created_by=self.user_id
        )

        self.db.add(breaking_notice)
        self.db.commit()

        return {
            "breaking_notice_id": breaking_notice.id,
            "notice_number": breaking_notice.notice_number,
            "allocation_id": allocation_id,
            "breaking_scheduled": True,
            "authorized_by": authorized_by,
            "witnesses": witnesses,
            "total_outstanding": eligibility['total_outstanding'],
            "message": "Breaking procedure initiated. Locker will be opened in presence of witnesses and contents inventoried."
        }

    # ============================================
    # Arrears Statistics
    # ============================================

    def get_arrears_summary(
        self,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get arrears summary and statistics"""
        query = self.db.query(LockerAllocation).filter(
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False,
            LockerAllocation.status == 'active',
            LockerAllocation.next_rent_due_date < datetime.now().date()
        )

        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)

        overdue_allocations = query.all()

        # Categorize by overdue period
        categories = {
            "0-30_days": [],
            "31-60_days": [],
            "61-90_days": [],
            "91-180_days": [],
            "181-365_days": [],
            "1-2_years": [],
            "2-3_years": [],
            "3+_years": []
        }

        total_outstanding = Decimal('0')
        total_penalties = Decimal('0')

        for allocation in overdue_allocations:
            overdue_days = (datetime.now().date() - allocation.next_rent_due_date).days
            overdue_amount = Decimal(str(allocation.annual_rent))
            penalty_calc = self.calculate_penalty(allocation.id, overdue_days, overdue_amount)

            total_outstanding += overdue_amount
            total_penalties += Decimal(str(penalty_calc['total_penalty']))

            record = {
                "allocation_id": allocation.id,
                "allocation_number": allocation.allocation_number,
                "customer_id": allocation.customer_id,
                "overdue_days": overdue_days,
                "overdue_amount": float(overdue_amount),
                "penalty": float(penalty_calc['total_penalty'])
            }

            if overdue_days <= 30:
                categories["0-30_days"].append(record)
            elif overdue_days <= 60:
                categories["31-60_days"].append(record)
            elif overdue_days <= 90:
                categories["61-90_days"].append(record)
            elif overdue_days <= 180:
                categories["91-180_days"].append(record)
            elif overdue_days <= 365:
                categories["181-365_days"].append(record)
            elif overdue_days <= 730:
                categories["1-2_years"].append(record)
            elif overdue_days <= 1095:
                categories["2-3_years"].append(record)
            else:
                categories["3+_years"].append(record)

        return {
            "total_overdue_allocations": len(overdue_allocations),
            "total_outstanding_amount": float(total_outstanding),
            "total_penalties": float(total_penalties),
            "grand_total": float(total_outstanding + total_penalties),
            "by_overdue_period": {
                "0-30_days": {
                    "count": len(categories["0-30_days"]),
                    "allocations": categories["0-30_days"]
                },
                "31-60_days": {
                    "count": len(categories["31-60_days"]),
                    "allocations": categories["31-60_days"]
                },
                "61-90_days": {
                    "count": len(categories["61-90_days"]),
                    "allocations": categories["61-90_days"]
                },
                "91-180_days": {
                    "count": len(categories["91-180_days"]),
                    "allocations": categories["91-180_days"]
                },
                "181-365_days": {
                    "count": len(categories["181-365_days"]),
                    "allocations": categories["181-365_days"]
                },
                "1-2_years": {
                    "count": len(categories["1-2_years"]),
                    "allocations": categories["1-2_years"]
                },
                "2-3_years": {
                    "count": len(categories["2-3_years"]),
                    "allocations": categories["2-3_years"]
                },
                "3+_years": {
                    "count": len(categories["3+_years"]),
                    "allocations": categories["3+_years"],
                    "breaking_eligible": len(categories["3+_years"])
                }
            }
        }

    def get_breaking_eligible_lockers(
        self,
        branch_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get lockers eligible for breaking (3+ years overdue)"""
        query = self.db.query(LockerAllocation).filter(
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False,
            LockerAllocation.status == 'active',
            LockerAllocation.next_rent_due_date < (datetime.now().date() - timedelta(days=1095))
        )

        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)

        allocations = query.all()

        eligible_list = []
        for allocation in allocations:
            eligibility = self.check_breaking_eligibility(allocation.id)
            
            if eligibility['eligible']:
                eligible_list.append({
                    "allocation_id": allocation.id,
                    "allocation_number": allocation.allocation_number,
                    "customer_id": allocation.customer_id,
                    "locker_id": allocation.locker_id,
                    "overdue_days": eligibility['overdue_days'],
                    "years_overdue": eligibility['years_overdue'],
                    "total_outstanding": eligibility['total_outstanding'],
                    "all_notices_sent": eligibility['all_notices_sent']
                })

        return eligible_list

    # ============================================
    # Helper Methods
    # ============================================

    def _generate_notice_number(self) -> str:
        """Generate unique notice number"""
        prefix = "NOT"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Get count of notices today
        today = datetime.now().date()
        count = self.db.query(func.count(LockerNotice.id)).filter(
            LockerNotice.tenant_id == self.tenant_id,
            func.date(LockerNotice.created_at) == today
        ).scalar()

        return f"{prefix}{timestamp}{count + 1:04d}"

    def _generate_notice_content(
        self,
        notice_type: str,
        arrears: Dict[str, Any]
    ) -> str:
        """Generate notice content based on type"""
        templates = {
            "first_reminder": f"""
                Dear Customer,
                
                This is a reminder that your locker rent payment of Rs. {arrears['overdue_amount']} 
                was due on {arrears['rent_due_date']} and is now {arrears['overdue_days']} days overdue.
                
                Please make the payment at your earliest convenience to avoid penalty charges.
                
                Current Outstanding: Rs. {arrears['total_outstanding']}
                (Including penalty: Rs. {arrears['penalty_details']['total_penalty']})
            """,
            "second_reminder": f"""
                Dear Customer,
                
                This is a second reminder regarding your overdue locker rent payment.
                
                Amount Due: Rs. {arrears['overdue_amount']}
                Penalty: Rs. {arrears['penalty_details']['total_penalty']}
                Total Outstanding: Rs. {arrears['total_outstanding']}
                Overdue Days: {arrears['overdue_days']}
                
                Please settle this immediately to avoid further action.
            """,
            "final_notice": f"""
                FINAL NOTICE
                
                Dear Customer,
                
                This is the FINAL NOTICE regarding your long overdue locker rent payment.
                
                Your locker rent has been overdue for {arrears['overdue_days']} days.
                
                Total Outstanding: Rs. {arrears['total_outstanding']}
                
                If payment is not received within 15 days, we will be forced to initiate 
                locker breaking procedure as per banking regulations.
                
                Please contact us immediately to resolve this matter.
            """,
            "legal_notice": f"""
                LEGAL NOTICE
                
                Dear Customer,
                
                Despite multiple reminders, your locker rent remains unpaid for over {arrears['overdue_days']} days.
                
                Total Outstanding: Rs. {arrears['total_outstanding']}
                
                As per banking regulations and our locker agreement terms, we are initiating 
                legal proceedings. You are required to settle the outstanding amount within 
                30 days of receiving this notice.
                
                Failure to comply will result in locker breaking and legal action for recovery.
            """,
            "breaking_notice": f"""
                LOCKER BREAKING NOTICE
                
                Dear Customer,
                
                As per banking regulations, due to non-payment of rent for over 3 years,
                we are proceeding with locker breaking procedure.
                
                Total Outstanding: Rs. {arrears['total_outstanding']}
                
                The locker will be opened in presence of bank officials and witnesses.
                Contents will be inventoried and stored securely.
                
                You may still settle the outstanding amount to reclaim your belongings.
            """
        }

        return templates.get(notice_type, "Notice content not available")
