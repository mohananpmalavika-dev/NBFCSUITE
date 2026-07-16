"""
Locker Key Handover Service

Handles dual key system management including:
- Key issuance and tracking (customer key + bank master key)
- Key return processing
- Duplicate key management
- Lost key handling with indemnity
- Biometric capture and verification
- Key register maintenance
- Security and audit trail
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from backend.shared.database.locker_models import (
    LockerKeyHandover,
    LockerAllocation,
    LockerMaster,
    Customer
)
from backend.services.locker.schemas import (
    LockerKeyHandoverCreate,
    LockerKeyHandoverUpdate,
    LockerKeyHandoverResponse,
    KeyLostReportRequest,
    KeyReturnRequest,
    KeyHandoverFilter,
    HandoverType,
    KeyStatus,
    KeyType,
    KeyHandoverStatistics
)
from backend.shared.utils import generate_reference_number


class KeyHandoverService:
    """Service for managing locker key handovers"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def issue_keys(
        self,
        data: LockerKeyHandoverCreate
    ) -> LockerKeyHandover:
        """
        Issue locker keys (customer key + bank master key)
        """
        # Verify allocation exists and is active
        allocation = self.db.query(LockerAllocation).filter(
            and_(
                LockerAllocation.id == data.allocation_id,
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.status == "active",
                LockerAllocation.is_deleted == False
            )
        ).first()
        
        if not allocation:
            raise ValueError("Active allocation not found")
        
        # Check if keys already issued
        existing = self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.allocation_id == data.allocation_id,
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.status.in_([KeyStatus.ACTIVE, KeyStatus.ACTIVE]),
                LockerKeyHandover.is_deleted == False
            )
        ).first()
        
        if existing and data.handover_type == HandoverType.INITIAL_ISSUE:
            raise ValueError("Keys already issued for this allocation")
        
        # Generate reference numbers
        handover_id = generate_reference_number("KH")
        key_register_number = generate_reference_number("KR")
        
        # Verify customer key number is unique
        duplicate_check = self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.customer_key_number == data.customer_key_number,
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.status == KeyStatus.ACTIVE,
                LockerKeyHandover.is_deleted == False
            )
        ).first()
        
        if duplicate_check:
            raise ValueError(f"Customer key number {data.customer_key_number} already in use")
        
        # Create key handover record
        handover = LockerKeyHandover(
            handover_id=handover_id,
            key_register_number=key_register_number,
            tenant_id=self.tenant_id,
            allocation_id=data.allocation_id,
            locker_id=data.locker_id,
            customer_id=data.customer_id,
            handover_type=data.handover_type,
            handover_date=data.handover_date,
            customer_key_number=data.customer_key_number,
            customer_key_type=data.customer_key_type,
            customer_key_issued=True,
            customer_key_issue_date=data.handover_date,
            bank_key_number=data.bank_key_number,
            bank_key_location=data.bank_key_location,
            bank_key_custodian=data.bank_key_custodian,
            bank_key_status="available",
            requires_dual_key=data.requires_dual_key,
            dual_key_policy=data.dual_key_policy,
            duplicate_key_issued=data.duplicate_key_issued,
            duplicate_key_number=data.duplicate_key_number,
            duplicate_key_reason=data.duplicate_key_reason,
            duplicate_key_charges=data.duplicate_key_charges,
            duplicate_key_authorization=data.duplicate_key_authorization,
            number_of_duplicate_keys=data.number_of_duplicate_keys,
            received_by=data.received_by,
            received_by_relation=data.received_by_relation,
            received_by_id_proof=data.received_by_id_proof,
            received_by_id_number=data.received_by_id_number,
            witness_1_name=data.witness_1_name,
            witness_1_employee_id=data.witness_1_employee_id,
            witness_2_name=data.witness_2_name,
            witness_2_employee_id=data.witness_2_employee_id,
            issued_by=data.issued_by,
            issued_by_name=data.issued_by_name,
            biometric_captured=data.biometric_captured,
            biometric_type=data.biometric_type,
            biometric_reference=data.biometric_reference,
            key_tested=data.key_tested,
            key_working_condition=data.key_working_condition,
            lock_tested=data.lock_tested,
            lock_condition=data.lock_condition,
            key_security_deposit=data.key_security_deposit,
            customer_acknowledgment=data.customer_acknowledgment,
            acknowledgment_date=data.acknowledgment_date,
            status=KeyStatus.ACTIVE,
            key_lost=False,
            indemnity_bond_executed=False,
            locker_breaking_required=False,
            deposit_refunded=False,
            special_instructions=data.special_instructions,
            remarks=data.remarks,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(handover)
        
        # Update allocation with key numbers
        allocation.customer_key_number = data.customer_key_number
        allocation.bank_key_number = data.bank_key_number
        
        if data.duplicate_key_issued:
            allocation.duplicate_key_issued = True
            allocation.duplicate_key_charges = data.duplicate_key_charges
        
        allocation.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(handover)
        
        return handover
    
    async def get_handover(
        self,
        handover_id: uuid.UUID
    ) -> Optional[LockerKeyHandover]:
        """Get key handover by ID"""
        return self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.id == handover_id,
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.is_deleted == False
            )
        ).first()
    
    async def get_handover_by_allocation(
        self,
        allocation_id: uuid.UUID
    ) -> Optional[LockerKeyHandover]:
        """Get active key handover for allocation"""
        return self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.allocation_id == allocation_id,
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.status == KeyStatus.ACTIVE,
                LockerKeyHandover.is_deleted == False
            )
        ).first()
    
    async def get_handover_by_key_number(
        self,
        customer_key_number: str
    ) -> Optional[LockerKeyHandover]:
        """Get handover by customer key number"""
        return self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.customer_key_number == customer_key_number,
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.is_deleted == False
            )
        ).first()
    
    async def list_handovers(
        self,
        filters: KeyHandoverFilter,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[LockerKeyHandover], int]:
        """List key handovers with filters"""
        query = self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.is_deleted == False
            )
        )
        
        # Apply filters
        if filters.allocation_id:
            query = query.filter(LockerKeyHandover.allocation_id == filters.allocation_id)
        
        if filters.locker_id:
            query = query.filter(LockerKeyHandover.locker_id == filters.locker_id)
        
        if filters.customer_id:
            query = query.filter(LockerKeyHandover.customer_id == filters.customer_id)
        
        if filters.handover_type:
            query = query.filter(LockerKeyHandover.handover_type == filters.handover_type)
        
        if filters.status:
            query = query.filter(LockerKeyHandover.status == filters.status)
        
        if filters.key_lost is not None:
            query = query.filter(LockerKeyHandover.key_lost == filters.key_lost)
        
        # Get total count
        total = query.count()
        
        # Order by handover date (most recent first)
        query = query.order_by(desc(LockerKeyHandover.handover_date))
        
        # Pagination
        handovers = query.offset(skip).limit(limit).all()
        
        return handovers, total
    
    async def update_handover(
        self,
        handover_id: uuid.UUID,
        data: LockerKeyHandoverUpdate
    ) -> Optional[LockerKeyHandover]:
        """Update key handover details"""
        handover = await self.get_handover(handover_id)
        if not handover:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(handover, field, value)
        
        handover.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(handover)
        
        return handover
    
    async def return_keys(
        self,
        handover_id: uuid.UUID,
        return_data: KeyReturnRequest
    ) -> Optional[LockerKeyHandover]:
        """
        Process key return from customer
        """
        handover = await self.get_handover(handover_id)
        if not handover:
            return None
        
        if handover.status != KeyStatus.ACTIVE:
            raise ValueError("Keys are not in active status")
        
        # Update key return details
        handover.customer_key_returned = True
        handover.customer_key_return_date = return_data.return_date
        handover.customer_key_condition = return_data.key_condition
        handover.status = KeyStatus.RETURNED
        
        # Check duplicate keys
        if handover.duplicate_key_issued and not return_data.all_duplicate_keys_returned:
            handover.remarks = (handover.remarks or "") + f"\nWarning: Not all duplicate keys returned."
        
        # Refund security deposit if applicable
        if handover.key_security_deposit > 0:
            handover.deposit_refunded = True
            handover.deposit_refund_date = return_data.return_date
            handover.deposit_refund_amount = handover.key_security_deposit
        
        handover.remarks = (handover.remarks or "") + f"\n{return_data.remarks}"
        handover.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(handover)
        
        return handover
    
    async def report_lost_key(
        self,
        handover_id: uuid.UUID,
        report: KeyLostReportRequest
    ) -> Optional[LockerKeyHandover]:
        """
        Report lost key and initiate recovery process
        """
        handover = await self.get_handover(handover_id)
        if not handover:
            return None
        
        if handover.status != KeyStatus.ACTIVE:
            raise ValueError("Keys are not in active status")
        
        # Update lost key details
        handover.key_lost = True
        handover.key_lost_date = report.key_lost_date
        handover.key_lost_reported_date = date.today()
        handover.fir_number = report.fir_number
        handover.indemnity_bond_executed = True
        handover.indemnity_bond_path = report.indemnity_bond_path
        handover.locker_breaking_required = report.locker_breaking_required
        handover.status = KeyStatus.LOST
        
        # Calculate locker breaking charges if required
        if report.locker_breaking_required:
            locker = self.db.query(LockerMaster).filter(
                LockerMaster.id == handover.locker_id
            ).first()
            
            if locker:
                # Standard breaking charge from rent structure
                handover.locker_breaking_charges = Decimal("2000.00")
        
        # Issue duplicate key if requested
        if report.duplicate_key_required:
            handover.duplicate_key_issued = True
            handover.number_of_duplicate_keys += 1
            
            # Generate new duplicate key number
            new_key_number = f"{handover.customer_key_number}-D{handover.number_of_duplicate_keys}"
            
            # Update duplicate keys list
            duplicate_keys = []
            if handover.duplicate_keys_list:
                import json
                duplicate_keys = json.loads(handover.duplicate_keys_list)
            
            duplicate_keys.append({
                "key_number": new_key_number,
                "issued_date": date.today().isoformat(),
                "reason": "Lost key replacement"
            })
            
            import json
            handover.duplicate_keys_list = json.dumps(duplicate_keys)
            handover.duplicate_key_charges = Decimal("500.00") * handover.number_of_duplicate_keys
        
        handover.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(handover)
        
        return handover
    
    async def issue_duplicate_key(
        self,
        handover_id: uuid.UUID,
        reason: str,
        authorization: str
    ) -> Optional[LockerKeyHandover]:
        """
        Issue duplicate key with proper authorization
        """
        handover = await self.get_handover(handover_id)
        if not handover:
            return None
        
        # Generate duplicate key number
        handover.number_of_duplicate_keys += 1
        new_key_number = f"{handover.customer_key_number}-D{handover.number_of_duplicate_keys}"
        
        # Update duplicate keys list
        duplicate_keys = []
        if handover.duplicate_keys_list:
            import json
            duplicate_keys = json.loads(handover.duplicate_keys_list)
        
        duplicate_keys.append({
            "key_number": new_key_number,
            "issued_date": date.today().isoformat(),
            "reason": reason,
            "authorization": authorization
        })
        
        import json
        handover.duplicate_keys_list = json.dumps(duplicate_keys)
        handover.duplicate_key_issued = True
        handover.duplicate_key_number = new_key_number
        handover.duplicate_key_reason = reason
        handover.duplicate_key_authorization = authorization
        handover.duplicate_key_charges = Decimal("500.00") * handover.number_of_duplicate_keys
        handover.updated_by = self.user_id
        
        # Update allocation
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == handover.allocation_id
        ).first()
        
        if allocation:
            allocation.duplicate_key_issued = True
            allocation.duplicate_key_charges = handover.duplicate_key_charges
            allocation.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(handover)
        
        return handover
    
    async def process_locker_breaking(
        self,
        handover_id: uuid.UUID,
        breaking_date: date,
        charges: Decimal
    ) -> Optional[LockerKeyHandover]:
        """
        Record locker breaking due to lost keys
        """
        handover = await self.get_handover(handover_id)
        if not handover:
            return None
        
        if not handover.key_lost:
            raise ValueError("Locker breaking only allowed for lost keys")
        
        handover.locker_breaking_required = True
        handover.locker_breaking_date = breaking_date
        handover.locker_breaking_charges = charges
        handover.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(handover)
        
        return handover
    
    async def verify_biometric(
        self,
        handover_id: uuid.UUID,
        biometric_type: str,
        biometric_reference: str
    ) -> Optional[LockerKeyHandover]:
        """
        Record biometric verification
        """
        handover = await self.get_handover(handover_id)
        if not handover:
            return None
        
        handover.biometric_captured = True
        handover.biometric_type = biometric_type
        handover.biometric_reference = biometric_reference
        handover.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(handover)
        
        return handover
    
    async def test_key_and_lock(
        self,
        handover_id: uuid.UUID,
        key_condition: str,
        lock_condition: str
    ) -> Optional[LockerKeyHandover]:
        """
        Record key and lock testing results
        """
        handover = await self.get_handover(handover_id)
        if not handover:
            return None
        
        handover.key_tested = True
        handover.key_working_condition = key_condition
        handover.lock_tested = True
        handover.lock_condition = lock_condition
        handover.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(handover)
        
        return handover
    
    async def get_active_keys_by_customer(
        self,
        customer_id: uuid.UUID
    ) -> List[LockerKeyHandover]:
        """Get all active key handovers for customer"""
        return self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.customer_id == customer_id,
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.status == KeyStatus.ACTIVE,
                LockerKeyHandover.is_deleted == False
            )
        ).all()
    
    async def get_lost_keys_pending_action(
        self
    ) -> List[LockerKeyHandover]:
        """Get lost keys pending recovery action"""
        return self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.key_lost == True,
                LockerKeyHandover.status == KeyStatus.LOST,
                LockerKeyHandover.locker_breaking_required == True,
                LockerKeyHandover.locker_breaking_date.is_(None),
                LockerKeyHandover.is_deleted == False
            )
        ).all()
    
    async def get_keys_pending_return(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> List[LockerKeyHandover]:
        """Get keys that should be returned (allocation closed)"""
        query = self.db.query(LockerKeyHandover).join(
            LockerAllocation
        ).filter(
            and_(
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.status == KeyStatus.ACTIVE,
                LockerKeyHandover.customer_key_returned == False,
                LockerAllocation.status.in_(["closed", "surrendered"]),
                LockerKeyHandover.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )
        
        return query.all()
    
    async def get_statistics(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> KeyHandoverStatistics:
        """Get key handover statistics"""
        query = self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )
        
        total_handovers = query.count()
        
        active_keys = query.filter(
            LockerKeyHandover.status == KeyStatus.ACTIVE
        ).count()
        
        lost_keys = query.filter(
            LockerKeyHandover.key_lost == True
        ).count()
        
        duplicate_keys_issued = query.filter(
            LockerKeyHandover.duplicate_key_issued == True
        ).count()
        
        keys_returned = query.filter(
            LockerKeyHandover.customer_key_returned == True
        ).count()
        
        pending_returns = query.join(LockerAllocation).filter(
            and_(
                LockerKeyHandover.status == KeyStatus.ACTIVE,
                LockerKeyHandover.customer_key_returned == False,
                LockerAllocation.status.in_(["closed", "surrendered"])
            )
        ).count()
        
        return KeyHandoverStatistics(
            total_handovers=total_handovers,
            active_keys=active_keys,
            lost_keys=lost_keys,
            duplicate_keys_issued=duplicate_keys_issued,
            keys_returned=keys_returned,
            pending_returns=pending_returns
        )
    
    async def get_handover_history(
        self,
        allocation_id: uuid.UUID
    ) -> List[LockerKeyHandover]:
        """Get complete key handover history for allocation"""
        return self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.allocation_id == allocation_id,
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.is_deleted == False
            )
        ).order_by(desc(LockerKeyHandover.handover_date)).all()
    
    async def verify_dual_key_availability(
        self,
        locker_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Verify both customer and bank keys are available for access
        """
        # Get active handover for locker
        handover = self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.locker_id == locker_id,
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.status == KeyStatus.ACTIVE,
                LockerKeyHandover.is_deleted == False
            )
        ).first()
        
        if not handover:
            return {
                "available": False,
                "reason": "No active key handover found"
            }
        
        if handover.key_lost:
            return {
                "available": False,
                "reason": "Customer key is reported lost"
            }
        
        if handover.customer_key_returned:
            return {
                "available": False,
                "reason": "Customer key has been returned"
            }
        
        if handover.bank_key_status != "available":
            return {
                "available": False,
                "reason": f"Bank master key is {handover.bank_key_status}"
            }
        
        return {
            "available": True,
            "customer_key": handover.customer_key_number,
            "bank_key": handover.bank_key_number,
            "requires_dual_key": handover.requires_dual_key
        }
    
    async def update_bank_key_status(
        self,
        handover_id: uuid.UUID,
        status: str
    ) -> Optional[LockerKeyHandover]:
        """
        Update bank master key status (available, in_use, maintenance)
        """
        handover = await self.get_handover(handover_id)
        if not handover:
            return None
        
        handover.bank_key_status = status
        handover.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(handover)
        
        return handover
    
    async def get_duplicate_keys_report(
        self,
        branch_id: Optional[uuid.UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate report of all duplicate keys issued
        """
        query = self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.duplicate_key_issued == True,
                LockerKeyHandover.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )
        
        if date_from:
            query = query.filter(LockerKeyHandover.handover_date >= date_from)
        
        if date_to:
            query = query.filter(LockerKeyHandover.handover_date <= date_to)
        
        handovers = query.all()
        
        report = []
        for handover in handovers:
            import json
            duplicate_keys = []
            if handover.duplicate_keys_list:
                duplicate_keys = json.loads(handover.duplicate_keys_list)
            
            report.append({
                "handover_id": handover.handover_id,
                "customer_id": str(handover.customer_id),
                "locker_id": str(handover.locker_id),
                "original_key": handover.customer_key_number,
                "duplicate_count": handover.number_of_duplicate_keys,
                "duplicate_keys": duplicate_keys,
                "total_charges": float(handover.duplicate_key_charges or 0),
                "issue_date": handover.handover_date.isoformat()
            })
        
        return report
    
    async def get_lost_keys_report(
        self,
        branch_id: Optional[uuid.UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate report of all lost keys
        """
        query = self.db.query(LockerKeyHandover).filter(
            and_(
                LockerKeyHandover.tenant_id == self.tenant_id,
                LockerKeyHandover.key_lost == True,
                LockerKeyHandover.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.join(LockerMaster).filter(
                LockerMaster.branch_id == branch_id
            )
        
        if date_from:
            query = query.filter(LockerKeyHandover.key_lost_date >= date_from)
        
        if date_to:
            query = query.filter(LockerKeyHandover.key_lost_date <= date_to)
        
        handovers = query.all()
        
        report = []
        for handover in handovers:
            report.append({
                "handover_id": handover.handover_id,
                "customer_id": str(handover.customer_id),
                "locker_id": str(handover.locker_id),
                "key_number": handover.customer_key_number,
                "lost_date": handover.key_lost_date.isoformat() if handover.key_lost_date else None,
                "reported_date": handover.key_lost_reported_date.isoformat() if handover.key_lost_reported_date else None,
                "fir_number": handover.fir_number,
                "indemnity_executed": handover.indemnity_bond_executed,
                "locker_breaking_required": handover.locker_breaking_required,
                "locker_breaking_date": handover.locker_breaking_date.isoformat() if handover.locker_breaking_date else None,
                "breaking_charges": float(handover.locker_breaking_charges or 0)
            })
        
        return report
    
    async def bulk_update_bank_key_locations(
        self,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Bulk update bank key storage locations
        """
        successful = []
        failed = []
        
        for update in updates:
            try:
                handover_id = uuid.UUID(update["handover_id"])
                handover = await self.get_handover(handover_id)
                
                if handover:
                    handover.bank_key_location = update["location"]
                    if "custodian" in update:
                        handover.bank_key_custodian = uuid.UUID(update["custodian"])
                    
                    handover.updated_by = self.user_id
                    successful.append(str(handover_id))
                else:
                    failed.append({
                        "id": update["handover_id"],
                        "reason": "Not found"
                    })
            except Exception as e:
                failed.append({
                    "id": update.get("handover_id"),
                    "reason": str(e)
                })
        
        if successful:
            self.db.commit()
        
        return {
            "total": len(updates),
            "successful": len(successful),
            "failed": len(failed),
            "successful_ids": successful,
            "failed_items": failed
        }
