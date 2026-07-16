"""
Locker Surrender Service

Handles voluntary locker surrender operations:
- Surrender application
- Clearance of dues
- Key return
- Locker inspection
- Security deposit refund
- Closure certificate
- Final settlement
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid

from backend.shared.database.locker_models import (
    LockerAllocation, LockerSurrender, LockerKeyHandover,
    LockerRentPayment, LockerMaster
)
from backend.shared.common.exceptions import ValidationError, NotFoundError


class LockerSurrenderService:
    """Service for voluntary locker surrender operations"""

    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    # ============================================
    # Surrender Application
    # ============================================

    def check_surrender_eligibility(
        self,
        allocation_id: str
    ) -> Dict[str, Any]:
        """Check if allocation is eligible for surrender"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()

        if not allocation:
            raise NotFoundError(f"Allocation {allocation_id} not found")

        # Check if allocation is active
        if allocation.status != "active":
            return {
                "eligible": False,
                "reason": f"Allocation status is {allocation.status}, must be active",
                "allocation_status": allocation.status
            }

        # Calculate outstanding dues
        outstanding_rent = allocation.outstanding_rent or Decimal('0')
        
        # Check for pending payments
        pending_payments = self.db.query(LockerRentPayment).filter(
            LockerRentPayment.allocation_id == allocation_id,
            LockerRentPayment.payment_status == "pending"
        ).count()

        return {
            "eligible": True,
            "allocation_id": allocation_id,
            "outstanding_rent": float(outstanding_rent),
            "pending_payments": pending_payments,
            "security_deposit": float(allocation.security_deposit),
            "security_deposit_refundable": True,
            "estimated_refund": float(allocation.security_deposit - outstanding_rent)
        }

    async def submit_surrender_application(
        self,
        allocation_id: str,
        surrender_reason: str,
        surrender_date: date,
        applicant_name: str,
        applicant_signature_path: str,
        remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit surrender application"""
        # Check eligibility
        eligibility = self.check_surrender_eligibility(allocation_id)
        
        if not eligibility.get("eligible"):
            raise ValidationError(eligibility.get("reason", "Not eligible for surrender"))

        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id
        ).first()

        # Generate surrender number
        surrender_number = self._generate_surrender_number()

        # Create surrender record
        surrender = LockerSurrender(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            surrender_number=surrender_number,
            allocation_id=allocation_id,
            locker_id=allocation.locker_id,
            customer_id=allocation.customer_id,
            surrender_reason=surrender_reason,
            application_date=datetime.now().date(),
            requested_surrender_date=surrender_date,
            applicant_name=applicant_name,
            applicant_signature_path=applicant_signature_path,
            outstanding_rent=allocation.outstanding_rent or Decimal('0'),
            security_deposit_amount=allocation.security_deposit,
            keys_returned=False,
            locker_inspected=False,
            dues_cleared=False,
            deposit_refunded=False,
            closure_certificate_issued=False,
            status="pending_approval",
            remarks=remarks,
            created_by=self.user_id
        )

        self.db.add(surrender)
        self.db.commit()
        self.db.refresh(surrender)

        return {
            "surrender_id": surrender.id,
            "surrender_number": surrender.surrender_number,
            "allocation_id": allocation_id,
            "application_date": surrender.application_date.isoformat(),
            "requested_date": surrender_date.isoformat(),
            "status": "pending_approval",
            "outstanding_dues": float(surrender.outstanding_rent),
            "security_deposit": float(surrender.security_deposit_amount),
            "next_steps": [
                "Clear outstanding dues",
                "Return locker keys",
                "Locker inspection",
                "Security deposit refund processing"
            ]
        }

    # ============================================
    # Surrender Process Steps
    # ============================================

    async def approve_surrender_application(
        self,
        surrender_id: str,
        approved_by: str,
        approval_remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve surrender application"""
        surrender = self.db.query(LockerSurrender).filter(
            LockerSurrender.id == surrender_id,
            LockerSurrender.tenant_id == self.tenant_id
        ).first()

        if not surrender:
            raise NotFoundError(f"Surrender record {surrender_id} not found")

        if surrender.status != "pending_approval":
            raise ValidationError(f"Surrender already {surrender.status}")

        surrender.status = "approved"
        surrender.approved_by = approved_by
        surrender.approval_date = datetime.now().date()
        surrender.approval_remarks = approval_remarks

        self.db.commit()

        return {
            "surrender_id": surrender_id,
            "status": "approved",
            "approved_by": approved_by,
            "approval_date": surrender.approval_date.isoformat()
        }

    async def clear_dues(
        self,
        surrender_id: str,
        payment_id: str,
        amount_paid: Decimal
    ) -> Dict[str, Any]:
        """Mark dues as cleared"""
        surrender = self.db.query(LockerSurrender).filter(
            LockerSurrender.id == surrender_id,
            LockerSurrender.tenant_id == self.tenant_id
        ).first()

        if not surrender:
            raise NotFoundError(f"Surrender record {surrender_id} not found")

        surrender.dues_cleared = True
        surrender.dues_clearance_date = datetime.now().date()
        surrender.clearance_payment_id = payment_id
        surrender.amount_paid = amount_paid

        self.db.commit()

        return {
            "surrender_id": surrender_id,
            "dues_cleared": True,
            "amount_paid": float(amount_paid),
            "clearance_date": surrender.dues_clearance_date.isoformat()
        }

    async def return_keys(
        self,
        surrender_id: str,
        customer_key_returned: bool,
        bank_key_verified: bool,
        key_condition: str,
        returned_by: str
    ) -> Dict[str, Any]:
        """Record key return"""
        surrender = self.db.query(LockerSurrender).filter(
            LockerSurrender.id == surrender_id,
            LockerSurrender.tenant_id == self.tenant_id
        ).first()

        if not surrender:
            raise NotFoundError(f"Surrender record {surrender_id} not found")

        surrender.keys_returned = customer_key_returned and bank_key_verified
        surrender.key_return_date = datetime.now().date()
        surrender.key_condition = key_condition
        surrender.key_returned_by = returned_by

        self.db.commit()

        return {
            "surrender_id": surrender_id,
            "keys_returned": surrender.keys_returned,
            "customer_key": customer_key_returned,
            "bank_key_verified": bank_key_verified,
            "condition": key_condition,
            "return_date": surrender.key_return_date.isoformat()
        }

    async def conduct_inspection(
        self,
        surrender_id: str,
        inspected_by: str,
        locker_condition: str,
        damage_found: bool,
        damage_description: Optional[str] = None,
        damage_charges: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Conduct locker inspection"""
        surrender = self.db.query(LockerSurrender).filter(
            LockerSurrender.id == surrender_id,
            LockerSurrender.tenant_id == self.tenant_id
        ).first()

        if not surrender:
            raise NotFoundError(f"Surrender record {surrender_id} not found")

        surrender.locker_inspected = True
        surrender.inspection_date = datetime.now().date()
        surrender.inspected_by = inspected_by
        surrender.locker_condition = locker_condition
        surrender.damage_found = damage_found
        surrender.damage_description = damage_description
        surrender.damage_charges = damage_charges or Decimal('0')

        self.db.commit()

        return {
            "surrender_id": surrender_id,
            "inspection_completed": True,
            "locker_condition": locker_condition,
            "damage_found": damage_found,
            "damage_charges": float(surrender.damage_charges),
            "inspection_date": surrender.inspection_date.isoformat()
        }

    async def process_refund(
        self,
        surrender_id: str,
        refund_mode: str,
        refund_reference: str
    ) -> Dict[str, Any]:
        """Process security deposit refund"""
        surrender = self.db.query(LockerSurrender).filter(
            LockerSurrender.id == surrender_id,
            LockerSurrender.tenant_id == self.tenant_id
        ).first()

        if not surrender:
            raise NotFoundError(f"Surrender record {surrender_id} not found")

        # Calculate refund amount
        refund_amount = (
            surrender.security_deposit_amount -
            surrender.outstanding_rent -
            (surrender.damage_charges or Decimal('0'))
        )

        if refund_amount < 0:
            raise ValidationError("Refund amount cannot be negative. Additional charges due.")

        surrender.deposit_refunded = True
        surrender.refund_amount = refund_amount
        surrender.refund_date = datetime.now().date()
        surrender.refund_mode = refund_mode
        surrender.refund_reference = refund_reference

        self.db.commit()

        return {
            "surrender_id": surrender_id,
            "refund_processed": True,
            "refund_amount": float(refund_amount),
            "refund_mode": refund_mode,
            "refund_reference": refund_reference,
            "refund_date": surrender.refund_date.isoformat()
        }

    async def issue_closure_certificate(
        self,
        surrender_id: str,
        certificate_number: str,
        issued_by: str
    ) -> Dict[str, Any]:
        """Issue closure certificate"""
        surrender = self.db.query(LockerSurrender).filter(
            LockerSurrender.id == surrender_id,
            LockerSurrender.tenant_id == self.tenant_id
        ).first()

        if not surrender:
            raise NotFoundError(f"Surrender record {surrender_id} not found")

        # Validate all steps completed
        if not surrender.keys_returned:
            raise ValidationError("Keys not returned")
        if not surrender.locker_inspected:
            raise ValidationError("Locker inspection not completed")
        if not surrender.dues_cleared:
            raise ValidationError("Dues not cleared")
        if not surrender.deposit_refunded:
            raise ValidationError("Deposit not refunded")

        surrender.closure_certificate_issued = True
        surrender.closure_certificate_number = certificate_number
        surrender.closure_certificate_date = datetime.now().date()
        surrender.closure_certificate_issued_by = issued_by

        self.db.commit()

        return {
            "surrender_id": surrender_id,
            "certificate_issued": True,
            "certificate_number": certificate_number,
            "issue_date": surrender.closure_certificate_date.isoformat()
        }

    async def complete_surrender(
        self,
        surrender_id: str,
        final_remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete surrender process"""
        surrender = self.db.query(LockerSurrender).filter(
            LockerSurrender.id == surrender_id,
            LockerSurrender.tenant_id == self.tenant_id
        ).first()

        if not surrender:
            raise NotFoundError(f"Surrender record {surrender_id} not found")

        # Validate all requirements met
        if not surrender.closure_certificate_issued:
            raise ValidationError("Closure certificate not issued")

        surrender.status = "completed"
        surrender.completion_date = datetime.now().date()
        surrender.final_remarks = final_remarks

        # Update allocation status
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == surrender.allocation_id
        ).first()
        
        if allocation:
            allocation.status = "surrendered"

        # Update locker status
        locker = self.db.query(LockerMaster).filter(
            LockerMaster.id == surrender.locker_id
        ).first()
        
        if locker:
            locker.status = "available"
            locker.is_available = True

        self.db.commit()

        return {
            "surrender_id": surrender_id,
            "status": "completed",
            "completion_date": surrender.completion_date.isoformat(),
            "locker_status": "available",
            "allocation_status": "surrendered"
        }

    # ============================================
    # Final Settlement
    # ============================================

    def calculate_final_settlement(
        self,
        surrender_id: str
    ) -> Dict[str, Any]:
        """Calculate final settlement amount"""
        surrender = self.db.query(LockerSurrender).filter(
            LockerSurrender.id == surrender_id,
            LockerSurrender.tenant_id == self.tenant_id
        ).first()

        if not surrender:
            raise NotFoundError(f"Surrender record {surrender_id} not found")

        security_deposit = surrender.security_deposit_amount
        outstanding_rent = surrender.outstanding_rent or Decimal('0')
        damage_charges = surrender.damage_charges or Decimal('0')
        
        # Calculate any additional charges
        processing_charges = Decimal('500')  # Fixed processing fee
        
        total_deductions = outstanding_rent + damage_charges + processing_charges
        net_refund = security_deposit - total_deductions

        return {
            "surrender_id": surrender_id,
            "security_deposit": float(security_deposit),
            "deductions": {
                "outstanding_rent": float(outstanding_rent),
                "damage_charges": float(damage_charges),
                "processing_charges": float(processing_charges),
                "total_deductions": float(total_deductions)
            },
            "net_refund_amount": float(net_refund),
            "refund_status": "processed" if surrender.deposit_refunded else "pending"
        }

    # ============================================
    # Surrender Records
    # ============================================

    def get_surrender_record(
        self,
        surrender_id: str
    ) -> Dict[str, Any]:
        """Get surrender record details"""
        surrender = self.db.query(LockerSurrender).filter(
            LockerSurrender.id == surrender_id,
            LockerSurrender.tenant_id == self.tenant_id,
            LockerSurrender.is_deleted == False
        ).first()

        if not surrender:
            raise NotFoundError(f"Surrender record {surrender_id} not found")

        return {
            "surrender_id": surrender.id,
            "surrender_number": surrender.surrender_number,
            "allocation_id": surrender.allocation_id,
            "locker_id": surrender.locker_id,
            "customer_id": surrender.customer_id,
            "surrender_reason": surrender.surrender_reason,
            "application_date": surrender.application_date.isoformat(),
            "requested_surrender_date": surrender.requested_surrender_date.isoformat(),
            "status": surrender.status,
            "approval": {
                "approved": surrender.status in ["approved", "completed"],
                "approved_by": surrender.approved_by,
                "approval_date": surrender.approval_date.isoformat() if surrender.approval_date else None
            },
            "dues": {
                "cleared": surrender.dues_cleared,
                "outstanding_amount": float(surrender.outstanding_rent),
                "amount_paid": float(surrender.amount_paid) if surrender.amount_paid else 0,
                "clearance_date": surrender.dues_clearance_date.isoformat() if surrender.dues_clearance_date else None
            },
            "keys": {
                "returned": surrender.keys_returned,
                "condition": surrender.key_condition,
                "return_date": surrender.key_return_date.isoformat() if surrender.key_return_date else None
            },
            "inspection": {
                "completed": surrender.locker_inspected,
                "locker_condition": surrender.locker_condition,
                "damage_found": surrender.damage_found,
                "damage_charges": float(surrender.damage_charges) if surrender.damage_charges else 0,
                "inspection_date": surrender.inspection_date.isoformat() if surrender.inspection_date else None
            },
            "refund": {
                "processed": surrender.deposit_refunded,
                "refund_amount": float(surrender.refund_amount) if surrender.refund_amount else 0,
                "refund_date": surrender.refund_date.isoformat() if surrender.refund_date else None
            },
            "closure_certificate": {
                "issued": surrender.closure_certificate_issued,
                "certificate_number": surrender.closure_certificate_number,
                "issue_date": surrender.closure_certificate_date.isoformat() if surrender.closure_certificate_date else None
            },
            "completion_date": surrender.completion_date.isoformat() if surrender.completion_date else None
        }

    def list_surrender_records(
        self,
        status: Optional[str] = None,
        branch_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List surrender records with filters"""
        query = self.db.query(LockerSurrender).filter(
            LockerSurrender.tenant_id == self.tenant_id,
            LockerSurrender.is_deleted == False
        )

        if status:
            query = query.filter(LockerSurrender.status == status)

        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)

        surrender_records = query.order_by(LockerSurrender.application_date.desc()).offset(skip).limit(limit).all()

        return [
            {
                "surrender_id": s.id,
                "surrender_number": s.surrender_number,
                "locker_id": s.locker_id,
                "customer_id": s.customer_id,
                "application_date": s.application_date.isoformat(),
                "status": s.status,
                "refund_amount": float(s.refund_amount) if s.refund_amount else 0
            }
            for s in surrender_records
        ]

    # ============================================
    # Helper Methods
    # ============================================

    def _generate_surrender_number(self) -> str:
        """Generate unique surrender number"""
        prefix = "SRD"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        count = self.db.query(func.count(LockerSurrender.id)).filter(
            LockerSurrender.tenant_id == self.tenant_id,
            func.date(LockerSurrender.created_at) == datetime.now().date()
        ).scalar()

        return f"{prefix}{timestamp}{count + 1:04d}"
