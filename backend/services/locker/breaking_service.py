"""
Locker Breaking Service

Handles forced locker opening operations:
- Breaking reasons validation
- Authorization workflow
- Police intimation
- Witness presence
- Videography tracking
- Content inventory
- Valuation
- Content storage
- Breaking charges
- Legal documentation
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid

from backend.shared.database.locker_models import (
    LockerAllocation, LockerBreaking, LockerInventory,
    LockerMaster
)
from backend.shared.common.exceptions import ValidationError, NotFoundError


class LockerBreakingService:
    """Service for locker breaking (forced opening) operations"""

    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    # Breaking reasons
    BREAKING_REASONS = [
        "non_payment_of_rent",
        "death_of_sole_holder",
        "court_order",
        "suspicious_activity",
        "emergency_fire",
        "emergency_flood",
        "structural_damage"
    ]

    # ============================================
    # Breaking Authorization
    # ============================================

    def check_breaking_authorization(
        self,
        allocation_id: str,
        breaking_reason: str
    ) -> Dict[str, Any]:
        """Check if locker breaking is authorized"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id,
            LockerAllocation.tenant_id == self.tenant_id,
            LockerAllocation.is_deleted == False
        ).first()

        if not allocation:
            raise NotFoundError(f"Allocation {allocation_id} not found")

        if breaking_reason not in self.BREAKING_REASONS:
            raise ValidationError(f"Invalid breaking reason: {breaking_reason}")

        # Check authorization requirements based on reason
        authorization_required = {
            "branch_manager": True,
            "regional_head": True,
            "police_intimation": breaking_reason in [
                "suspicious_activity", "death_of_sole_holder", "court_order"
            ],
            "court_order_required": breaking_reason == "court_order",
            "witness_count_required": 2,
            "videography_required": True,
            "legal_notice_required": breaking_reason == "non_payment_of_rent"
        }

        # Additional validation for non-payment
        if breaking_reason == "non_payment_of_rent":
            # Check if 3 years overdue and all notices sent
            if allocation.next_rent_due_date:
                overdue_days = (datetime.now().date() - allocation.next_rent_due_date).days
                if overdue_days < 1095:  # 3 years
                    return {
                        "authorized": False,
                        "reason": "Breaking allowed only after 3 years of non-payment",
                        "overdue_days": overdue_days,
                        "days_remaining": 1095 - overdue_days
                    }

        return {
            "authorized": True,
            "allocation_id": allocation_id,
            "breaking_reason": breaking_reason,
            "authorization_requirements": authorization_required,
            "locker_number": allocation.locker_id
        }

    async def initiate_breaking_process(
        self,
        allocation_id: str,
        breaking_reason: str,
        branch_manager_id: str,
        regional_head_id: str,
        witnesses: List[str],
        court_order_number: Optional[str] = None,
        police_reference_number: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiate locker breaking process"""
        # Check authorization
        auth_check = self.check_breaking_authorization(allocation_id, breaking_reason)
        
        if not auth_check.get("authorized"):
            raise ValidationError(auth_check.get("reason", "Breaking not authorized"))

        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id
        ).first()

        # Validate witnesses
        if len(witnesses) < auth_check["authorization_requirements"]["witness_count_required"]:
            raise ValidationError(
                f"Minimum {auth_check['authorization_requirements']['witness_count_required']} witnesses required"
            )

        # Validate police intimation if required
        if auth_check["authorization_requirements"]["police_intimation"] and not police_reference_number:
            raise ValidationError("Police intimation required for this breaking reason")

        # Validate court order if required
        if auth_check["authorization_requirements"]["court_order_required"] and not court_order_number:
            raise ValidationError("Court order required for this breaking reason")

        # Generate breaking number
        breaking_number = self._generate_breaking_number()

        # Create breaking record
        breaking = LockerBreaking(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            breaking_number=breaking_number,
            allocation_id=allocation_id,
            locker_id=allocation.locker_id,
            customer_id=allocation.customer_id,
            breaking_reason=breaking_reason,
            breaking_date=datetime.now().date(),
            breaking_time=datetime.now().time(),
            branch_manager_id=branch_manager_id,
            regional_head_id=regional_head_id,
            witnesses=",".join(witnesses),
            police_intimation_done=auth_check["authorization_requirements"]["police_intimation"],
            police_reference_number=police_reference_number,
            court_order_number=court_order_number,
            videography_done=False,  # Will be updated later
            videography_file_path=None,
            inventory_prepared=False,
            valuation_done=False,
            contents_stored=False,
            breaking_charges=Decimal('0'),  # Will be calculated
            status="initiated",
            remarks=remarks,
            created_by=self.user_id
        )

        self.db.add(breaking)
        self.db.commit()
        self.db.refresh(breaking)

        return {
            "breaking_id": breaking.id,
            "breaking_number": breaking.breaking_number,
            "allocation_id": allocation_id,
            "locker_id": allocation.locker_id,
            "breaking_reason": breaking_reason,
            "breaking_date": breaking.breaking_date.isoformat(),
            "authorized_by": {
                "branch_manager": branch_manager_id,
                "regional_head": regional_head_id
            },
            "witnesses": witnesses,
            "status": "initiated",
            "next_steps": [
                "Complete videography",
                "Prepare content inventory",
                "Conduct valuation if required",
                "Store contents securely",
                "Calculate breaking charges"
            ]
        }

    # ============================================
    # Breaking Process Steps
    # ============================================

    async def record_videography(
        self,
        breaking_id: str,
        video_file_path: str,
        video_duration_minutes: int
    ) -> Dict[str, Any]:
        """Record videography completion"""
        breaking = self.db.query(LockerBreaking).filter(
            LockerBreaking.id == breaking_id,
            LockerBreaking.tenant_id == self.tenant_id
        ).first()

        if not breaking:
            raise NotFoundError(f"Breaking record {breaking_id} not found")

        breaking.videography_done = True
        breaking.videography_file_path = video_file_path
        breaking.videography_duration = video_duration_minutes

        self.db.commit()

        return {
            "breaking_id": breaking_id,
            "videography_completed": True,
            "video_path": video_file_path,
            "duration_minutes": video_duration_minutes
        }

    async def prepare_inventory(
        self,
        breaking_id: str,
        inventory_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare content inventory"""
        breaking = self.db.query(LockerBreaking).filter(
            LockerBreaking.id == breaking_id,
            LockerBreaking.tenant_id == self.tenant_id
        ).first()

        if not breaking:
            raise NotFoundError(f"Breaking record {breaking_id} not found")

        # Create inventory records
        inventory_records = []
        total_items = 0

        for item in inventory_items:
            inventory = LockerInventory(
                id=str(uuid.uuid4()),
                tenant_id=self.tenant_id,
                breaking_id=breaking_id,
                allocation_id=breaking.allocation_id,
                locker_id=breaking.locker_id,
                item_number=item.get("item_number"),
                item_description=item.get("description"),
                item_category=item.get("category"),
                quantity=item.get("quantity", 1),
                estimated_value=item.get("estimated_value"),
                condition=item.get("condition", "good"),
                photo_path=item.get("photo_path"),
                remarks=item.get("remarks"),
                created_by=self.user_id
            )
            self.db.add(inventory)
            inventory_records.append(inventory)
            total_items += 1

        breaking.inventory_prepared = True
        breaking.total_items_found = total_items

        self.db.commit()

        return {
            "breaking_id": breaking_id,
            "inventory_completed": True,
            "total_items": total_items,
            "items": [
                {
                    "item_number": inv.item_number,
                    "description": inv.item_description,
                    "category": inv.item_category,
                    "quantity": inv.quantity,
                    "estimated_value": float(inv.estimated_value) if inv.estimated_value else None
                }
                for inv in inventory_records
            ]
        }

    async def conduct_valuation(
        self,
        breaking_id: str,
        valuer_name: str,
        valuer_license_number: str,
        total_valuation: Decimal,
        valuation_report_path: str
    ) -> Dict[str, Any]:
        """Record valuation of contents"""
        breaking = self.db.query(LockerBreaking).filter(
            LockerBreaking.id == breaking_id,
            LockerBreaking.tenant_id == self.tenant_id
        ).first()

        if not breaking:
            raise NotFoundError(f"Breaking record {breaking_id} not found")

        breaking.valuation_done = True
        breaking.valuer_name = valuer_name
        breaking.valuer_license_number = valuer_license_number
        breaking.total_valuation = total_valuation
        breaking.valuation_report_path = valuation_report_path
        breaking.valuation_date = datetime.now().date()

        self.db.commit()

        return {
            "breaking_id": breaking_id,
            "valuation_completed": True,
            "total_valuation": float(total_valuation),
            "valuer": valuer_name,
            "valuation_date": breaking.valuation_date.isoformat()
        }

    async def store_contents(
        self,
        breaking_id: str,
        storage_location: str,
        storage_reference: str,
        custodian_name: str
    ) -> Dict[str, Any]:
        """Record storage of locker contents"""
        breaking = self.db.query(LockerBreaking).filter(
            LockerBreaking.id == breaking_id,
            LockerBreaking.tenant_id == self.tenant_id
        ).first()

        if not breaking:
            raise NotFoundError(f"Breaking record {breaking_id} not found")

        breaking.contents_stored = True
        breaking.storage_location = storage_location
        breaking.storage_reference = storage_reference
        breaking.custodian_name = custodian_name
        breaking.storage_date = datetime.now().date()

        self.db.commit()

        return {
            "breaking_id": breaking_id,
            "contents_stored": True,
            "storage_location": storage_location,
            "storage_reference": storage_reference,
            "custodian": custodian_name
        }

    async def calculate_breaking_charges(
        self,
        breaking_id: str
    ) -> Dict[str, Any]:
        """Calculate breaking charges"""
        breaking = self.db.query(LockerBreaking).filter(
            LockerBreaking.id == breaking_id,
            LockerBreaking.tenant_id == self.tenant_id
        ).first()

        if not breaking:
            raise NotFoundError(f"Breaking record {breaking_id} not found")

        # Breaking charges calculation
        base_breaking_charge = Decimal('5000')
        videography_charge = Decimal('2000')
        inventory_charge = Decimal('1000')
        valuation_charge = Decimal('3000') if breaking.valuation_done else Decimal('0')
        storage_charge = Decimal('1000')
        
        # Add legal charges for specific reasons
        legal_charge = Decimal('5000') if breaking.court_order_number else Decimal('0')

        total_charges = (
            base_breaking_charge +
            videography_charge +
            inventory_charge +
            valuation_charge +
            storage_charge +
            legal_charge
        )

        # Apply GST
        gst_rate = Decimal('0.18')
        gst_amount = total_charges * gst_rate
        total_with_gst = total_charges + gst_amount

        breaking.breaking_charges = total_with_gst
        breaking.breaking_charges_breakdown = {
            "base_charge": float(base_breaking_charge),
            "videography": float(videography_charge),
            "inventory": float(inventory_charge),
            "valuation": float(valuation_charge),
            "storage": float(storage_charge),
            "legal": float(legal_charge),
            "subtotal": float(total_charges),
            "gst_rate": float(gst_rate * 100),
            "gst_amount": float(gst_amount),
            "total": float(total_with_gst)
        }

        self.db.commit()

        return breaking.breaking_charges_breakdown

    async def complete_breaking_process(
        self,
        breaking_id: str,
        completion_remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete the breaking process"""
        breaking = self.db.query(LockerBreaking).filter(
            LockerBreaking.id == breaking_id,
            LockerBreaking.tenant_id == self.tenant_id
        ).first()

        if not breaking:
            raise NotFoundError(f"Breaking record {breaking_id} not found")

        # Validate all steps completed
        if not breaking.videography_done:
            raise ValidationError("Videography not completed")
        if not breaking.inventory_prepared:
            raise ValidationError("Inventory not prepared")
        if not breaking.contents_stored:
            raise ValidationError("Contents not stored")

        breaking.status = "completed"
        breaking.completion_date = datetime.now().date()
        breaking.completion_remarks = completion_remarks

        # Update allocation status
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == breaking.allocation_id
        ).first()
        
        if allocation:
            allocation.status = "broken"

        # Update locker status
        locker = self.db.query(LockerMaster).filter(
            LockerMaster.id == breaking.locker_id
        ).first()
        
        if locker:
            locker.status = "available"
            locker.is_available = True

        self.db.commit()

        return {
            "breaking_id": breaking_id,
            "status": "completed",
            "completion_date": breaking.completion_date.isoformat(),
            "total_items": breaking.total_items_found,
            "total_valuation": float(breaking.total_valuation) if breaking.total_valuation else 0,
            "breaking_charges": float(breaking.breaking_charges),
            "locker_status": "available",
            "allocation_status": "broken"
        }

    # ============================================
    # Breaking Records
    # ============================================

    def get_breaking_record(
        self,
        breaking_id: str
    ) -> Dict[str, Any]:
        """Get breaking record details"""
        breaking = self.db.query(LockerBreaking).filter(
            LockerBreaking.id == breaking_id,
            LockerBreaking.tenant_id == self.tenant_id,
            LockerBreaking.is_deleted == False
        ).first()

        if not breaking:
            raise NotFoundError(f"Breaking record {breaking_id} not found")

        # Get inventory items
        inventory_items = self.db.query(LockerInventory).filter(
            LockerInventory.breaking_id == breaking_id,
            LockerInventory.is_deleted == False
        ).all()

        return {
            "breaking_id": breaking.id,
            "breaking_number": breaking.breaking_number,
            "allocation_id": breaking.allocation_id,
            "locker_id": breaking.locker_id,
            "customer_id": breaking.customer_id,
            "breaking_reason": breaking.breaking_reason,
            "breaking_date": breaking.breaking_date.isoformat(),
            "breaking_time": breaking.breaking_time.isoformat() if breaking.breaking_time else None,
            "authorized_by": {
                "branch_manager": breaking.branch_manager_id,
                "regional_head": breaking.regional_head_id
            },
            "witnesses": breaking.witnesses.split(",") if breaking.witnesses else [],
            "police_intimation": {
                "done": breaking.police_intimation_done,
                "reference": breaking.police_reference_number
            },
            "court_order": breaking.court_order_number,
            "videography": {
                "done": breaking.videography_done,
                "file_path": breaking.videography_file_path,
                "duration_minutes": breaking.videography_duration
            },
            "inventory": {
                "prepared": breaking.inventory_prepared,
                "total_items": breaking.total_items_found,
                "items": [
                    {
                        "item_number": inv.item_number,
                        "description": inv.item_description,
                        "category": inv.item_category,
                        "quantity": inv.quantity,
                        "estimated_value": float(inv.estimated_value) if inv.estimated_value else None,
                        "condition": inv.condition
                    }
                    for inv in inventory_items
                ]
            },
            "valuation": {
                "done": breaking.valuation_done,
                "valuer": breaking.valuer_name,
                "total_valuation": float(breaking.total_valuation) if breaking.total_valuation else None,
                "valuation_date": breaking.valuation_date.isoformat() if breaking.valuation_date else None
            },
            "storage": {
                "done": breaking.contents_stored,
                "location": breaking.storage_location,
                "reference": breaking.storage_reference,
                "custodian": breaking.custodian_name
            },
            "charges": breaking.breaking_charges_breakdown if breaking.breaking_charges_breakdown else None,
            "status": breaking.status,
            "completion_date": breaking.completion_date.isoformat() if breaking.completion_date else None,
            "remarks": breaking.remarks
        }

    def list_breaking_records(
        self,
        status: Optional[str] = None,
        breaking_reason: Optional[str] = None,
        branch_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List breaking records with filters"""
        query = self.db.query(LockerBreaking).filter(
            LockerBreaking.tenant_id == self.tenant_id,
            LockerBreaking.is_deleted == False
        )

        if status:
            query = query.filter(LockerBreaking.status == status)
        
        if breaking_reason:
            query = query.filter(LockerBreaking.breaking_reason == breaking_reason)

        if branch_id:
            query = query.join(LockerMaster).filter(LockerMaster.branch_id == branch_id)

        breaking_records = query.order_by(LockerBreaking.breaking_date.desc()).offset(skip).limit(limit).all()

        return [
            {
                "breaking_id": b.id,
                "breaking_number": b.breaking_number,
                "locker_id": b.locker_id,
                "customer_id": b.customer_id,
                "breaking_reason": b.breaking_reason,
                "breaking_date": b.breaking_date.isoformat(),
                "status": b.status,
                "total_items": b.total_items_found,
                "breaking_charges": float(b.breaking_charges) if b.breaking_charges else 0
            }
            for b in breaking_records
        ]

    # ============================================
    # Helper Methods
    # ============================================

    def _generate_breaking_number(self) -> str:
        """Generate unique breaking number"""
        prefix = "BRK"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        count = self.db.query(func.count(LockerBreaking.id)).filter(
            LockerBreaking.tenant_id == self.tenant_id,
            func.date(LockerBreaking.created_at) == datetime.now().date()
        ).scalar()

        return f"{prefix}{timestamp}{count + 1:04d}"
