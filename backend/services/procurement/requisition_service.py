"""
Purchase Requisition Service
Business logic for purchase requisition management
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
import uuid

from backend.shared.database.procurement_models import (
    PurchaseRequisition,
    PurchaseRequisitionItem,
    Vendor,
    RequisitionStatus,
    RequisitionPriority
)
from .schemas import (
    PurchaseRequisitionCreate,
    PurchaseRequisitionUpdate,
    PurchaseRequisitionApproval
)


class RequisitionService:
    """Service for managing purchase requisition operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: uuid.UUID, user_name: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.user_name = user_name
    
    # ========================================================================
    # Purchase Requisition Operations
    # ========================================================================
    
    async def generate_requisition_number(self) -> str:
        """Generate unique requisition number"""
        # Format: PR-YYYYMM-NNNN
        current_date = date.today()
        prefix = f"PR-{current_date.strftime('%Y%m')}"
        
        # Get the latest requisition number for this month
        query = select(PurchaseRequisition.requisition_number).where(
            and_(
                PurchaseRequisition.tenant_id == self.tenant_id,
                PurchaseRequisition.requisition_number.like(f"{prefix}%")
            )
        ).order_by(desc(PurchaseRequisition.created_at)).limit(1)
        
        result = await self.db.execute(query)
        last_number = result.scalar_one_or_none()
        
        if last_number:
            try:
                last_seq = int(last_number.split('-')[-1])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1
        
        return f"{prefix}-{new_seq:04d}"
    
    async def create_requisition(
        self,
        requisition_data: PurchaseRequisitionCreate
    ) -> PurchaseRequisition:
        """Create new purchase requisition"""
        
        # Validate preferred vendor if provided
        if requisition_data.preferred_vendor_id:
            vendor_query = select(Vendor).where(
                and_(
                    Vendor.id == requisition_data.preferred_vendor_id,
                    Vendor.tenant_id == self.tenant_id,
                    Vendor.is_deleted == False
                )
            )
            vendor_result = await self.db.execute(vendor_query)
            if not vendor_result.scalar_one_or_none():
                raise ValueError("Preferred vendor not found")
        
        # Generate requisition number
        requisition_number = await self.generate_requisition_number()
        
        # Calculate estimated total from items
        estimated_total = sum(
            item.estimated_total_price or Decimal("0.00")
            for item in requisition_data.items
        )
        
        # Create requisition
        requisition = PurchaseRequisition(
            tenant_id=self.tenant_id,
            requisition_number=requisition_number,
            requisition_date=date.today(),
            required_by_date=requisition_data.required_by_date,
            status=RequisitionStatus.DRAFT,
            priority=requisition_data.priority,
            department=requisition_data.department,
            requester_id=self.user_id,
            requester_name=self.user_name,
            purpose=requisition_data.purpose,
            justification=requisition_data.justification,
            budget_code=requisition_data.budget_code,
            estimated_total=estimated_total,
            preferred_vendor_id=requisition_data.preferred_vendor_id,
            created_by=self.user_id
        )
        
        self.db.add(requisition)
        await self.db.flush()
        
        # Create requisition items
        for item_data in requisition_data.items:
            item = PurchaseRequisitionItem(
                requisition_id=requisition.id,
                item_code=item_data.item_code,
                item_name=item_data.item_name,
                description=item_data.description,
                specification=item_data.specification,
                quantity=item_data.quantity,
                unit_of_measure=item_data.unit_of_measure,
                estimated_unit_price=item_data.estimated_unit_price,
                estimated_total_price=item_data.estimated_total_price,
                notes=item_data.notes
            )
            self.db.add(item)
        
        await self.db.commit()
        await self.db.refresh(requisition)
        
        # Load items
        await self.db.refresh(requisition, ['items'])
        
        return requisition
    
    async def get_requisition(self, requisition_id: uuid.UUID) -> Optional[PurchaseRequisition]:
        """Get requisition by ID"""
        query = select(PurchaseRequisition).options(
            joinedload(PurchaseRequisition.items)
        ).where(
            and_(
                PurchaseRequisition.id == requisition_id,
                PurchaseRequisition.tenant_id == self.tenant_id,
                PurchaseRequisition.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def list_requisitions(
        self,
        status: Optional[RequisitionStatus] = None,
        priority: Optional[RequisitionPriority] = None,
        department: Optional[str] = None,
        requester_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[PurchaseRequisition], int]:
        """List requisitions with filters"""
        conditions = [
            PurchaseRequisition.tenant_id == self.tenant_id,
            PurchaseRequisition.is_deleted == False
        ]
        
        if status:
            conditions.append(PurchaseRequisition.status == status)
        if priority:
            conditions.append(PurchaseRequisition.priority == priority)
        if department:
            conditions.append(PurchaseRequisition.department == department)
        if requester_id:
            conditions.append(PurchaseRequisition.requester_id == requester_id)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    PurchaseRequisition.requisition_number.ilike(search_pattern),
                    PurchaseRequisition.purpose.ilike(search_pattern),
                    PurchaseRequisition.department.ilike(search_pattern)
                )
            )
        
        # Count total
        count_query = select(func.count(PurchaseRequisition.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get requisitions
        query = select(PurchaseRequisition).options(
            joinedload(PurchaseRequisition.items)
        ).where(and_(*conditions)).order_by(
            desc(PurchaseRequisition.created_at)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        requisitions = result.unique().scalars().all()
        
        return list(requisitions), total
    
    async def update_requisition(
        self,
        requisition_id: uuid.UUID,
        requisition_data: PurchaseRequisitionUpdate
    ) -> PurchaseRequisition:
        """Update requisition (only if in DRAFT status)"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        if requisition.status != RequisitionStatus.DRAFT:
            raise ValueError("Only draft requisitions can be updated")
        
        # Update fields
        update_data = requisition_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(requisition, field, value)
        
        requisition.updated_by = self.user_id
        requisition.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(requisition)
        
        return requisition
    
    async def submit_requisition(self, requisition_id: uuid.UUID) -> PurchaseRequisition:
        """Submit requisition for approval"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        if requisition.status != RequisitionStatus.DRAFT:
            raise ValueError("Only draft requisitions can be submitted")
        
        if not requisition.items:
            raise ValueError("Requisition must have at least one item")
        
        requisition.status = RequisitionStatus.SUBMITTED
        requisition.updated_by = self.user_id
        requisition.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(requisition)
        
        return requisition
    
    async def approve_requisition(
        self,
        requisition_id: uuid.UUID,
        approval_data: PurchaseRequisitionApproval
    ) -> PurchaseRequisition:
        """Approve or reject requisition"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        if requisition.status != RequisitionStatus.SUBMITTED:
            raise ValueError("Only submitted requisitions can be approved/rejected")
        
        if approval_data.approved:
            requisition.status = RequisitionStatus.APPROVED
            requisition.approved_by = self.user_id
            requisition.approved_at = datetime.utcnow()
        else:
            requisition.status = RequisitionStatus.REJECTED
            requisition.rejection_reason = approval_data.rejection_reason
        
        requisition.updated_by = self.user_id
        requisition.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(requisition)
        
        return requisition
    
    async def cancel_requisition(self, requisition_id: uuid.UUID) -> PurchaseRequisition:
        """Cancel requisition"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        if requisition.status in [RequisitionStatus.CONVERTED_TO_PO, RequisitionStatus.PARTIALLY_CONVERTED]:
            raise ValueError("Cannot cancel requisition that is already converted to PO")
        
        requisition.status = RequisitionStatus.CANCELLED
        requisition.updated_by = self.user_id
        requisition.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(requisition)
        
        return requisition
    
    async def delete_requisition(self, requisition_id: uuid.UUID) -> bool:
        """Soft delete requisition (only if DRAFT or REJECTED)"""
        requisition = await self.get_requisition(requisition_id)
        if not requisition:
            raise ValueError("Requisition not found")
        
        if requisition.status not in [RequisitionStatus.DRAFT, RequisitionStatus.REJECTED]:
            raise ValueError("Only draft or rejected requisitions can be deleted")
        
        requisition.is_deleted = True
        requisition.deleted_at = datetime.utcnow()
        requisition.deleted_by = self.user_id
        
        await self.db.commit()
        return True
    
    async def update_item_conversion_quantity(
        self,
        item_id: uuid.UUID,
        converted_quantity: Decimal
    ):
        """Update quantity converted to PO for a requisition item"""
        query = select(PurchaseRequisitionItem).where(
            PurchaseRequisitionItem.id == item_id
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError("Requisition item not found")
        
        item.quantity_converted = converted_quantity
        
        # Check if all items are converted
        req_query = select(PurchaseRequisition).options(
            joinedload(PurchaseRequisition.items)
        ).where(
            PurchaseRequisition.id == item.requisition_id
        )
        req_result = await self.db.execute(req_query)
        requisition = req_result.unique().scalar_one_or_none()
        
        if requisition:
            all_converted = all(
                item.quantity_converted >= item.quantity
                for item in requisition.items
            )
            any_converted = any(
                item.quantity_converted > 0
                for item in requisition.items
            )
            
            if all_converted:
                requisition.status = RequisitionStatus.CONVERTED_TO_PO
            elif any_converted:
                requisition.status = RequisitionStatus.PARTIALLY_CONVERTED
        
        await self.db.commit()
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    async def get_requisition_statistics(self) -> dict:
        """Get requisition statistics for dashboard"""
        
        # Count by status
        status_query = select(
            PurchaseRequisition.status,
            func.count(PurchaseRequisition.id).label('count')
        ).where(
            and_(
                PurchaseRequisition.tenant_id == self.tenant_id,
                PurchaseRequisition.is_deleted == False
            )
        ).group_by(PurchaseRequisition.status)
        
        status_result = await self.db.execute(status_query)
        status_counts = {row.status: row.count for row in status_result}
        
        # Count by priority
        priority_query = select(
            PurchaseRequisition.priority,
            func.count(PurchaseRequisition.id).label('count')
        ).where(
            and_(
                PurchaseRequisition.tenant_id == self.tenant_id,
                PurchaseRequisition.is_deleted == False,
                PurchaseRequisition.status.in_([
                    RequisitionStatus.SUBMITTED,
                    RequisitionStatus.APPROVED
                ])
            )
        ).group_by(PurchaseRequisition.priority)
        
        priority_result = await self.db.execute(priority_query)
        priority_counts = {row.priority: row.count for row in priority_result}
        
        # Total estimated value
        value_query = select(
            func.sum(PurchaseRequisition.estimated_total).label('total_value')
        ).where(
            and_(
                PurchaseRequisition.tenant_id == self.tenant_id,
                PurchaseRequisition.is_deleted == False,
                PurchaseRequisition.status == RequisitionStatus.APPROVED
            )
        )
        
        value_result = await self.db.execute(value_query)
        total_value = value_result.scalar() or Decimal("0.00")
        
        return {
            "total_requisitions": sum(status_counts.values()),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "total_estimated_value": float(total_value),
            "pending_approvals": status_counts.get(RequisitionStatus.SUBMITTED, 0)
        }
