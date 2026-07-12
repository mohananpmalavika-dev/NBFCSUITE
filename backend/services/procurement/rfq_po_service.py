"""
RFQ and Purchase Order Service
Business logic for RFQ and PO management
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
import uuid

from backend.shared.database.procurement_models import (
    RFQ,
    RFQItem,
    RFQVendor,
    VendorQuote,
    PurchaseOrder,
    PurchaseOrderItem,
    Vendor,
    PurchaseRequisition,
    RFQStatus,
    POStatus,
    RequisitionStatus,
    VendorStatus
)
from .schemas import (
    RFQCreate,
    RFQUpdate,
    VendorQuoteCreate,
    PurchaseOrderCreate,
    PurchaseOrderUpdate
)


class RFQPOService:
    """Service for managing RFQ and Purchase Order operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # RFQ Operations
    # ========================================================================
    
    async def generate_rfq_number(self) -> str:
        """Generate unique RFQ number"""
        # Format: RFQ-YYYYMM-NNNN
        current_date = date.today()
        prefix = f"RFQ-{current_date.strftime('%Y%m')}"
        
        query = select(RFQ.rfq_number).where(
            and_(
                RFQ.tenant_id == self.tenant_id,
                RFQ.rfq_number.like(f"{prefix}%")
            )
        ).order_by(desc(RFQ.created_at)).limit(1)
        
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
    
    async def create_rfq(self, rfq_data: RFQCreate) -> RFQ:
        """Create new RFQ"""
        
        # Validate requisition if provided
        if rfq_data.requisition_id:
            req_query = select(PurchaseRequisition).where(
                and_(
                    PurchaseRequisition.id == rfq_data.requisition_id,
                    PurchaseRequisition.tenant_id == self.tenant_id,
                    PurchaseRequisition.status == RequisitionStatus.APPROVED
                )
            )
            req_result = await self.db.execute(req_query)
            if not req_result.scalar_one_or_none():
                raise ValueError("Requisition not found or not approved")
        
        # Validate vendors
        for vendor_id in rfq_data.vendor_ids:
            vendor_query = select(Vendor).where(
                and_(
                    Vendor.id == vendor_id,
                    Vendor.tenant_id == self.tenant_id,
                    Vendor.status == VendorStatus.ACTIVE,
                    Vendor.is_deleted == False
                )
            )
            vendor_result = await self.db.execute(vendor_query)
            if not vendor_result.scalar_one_or_none():
                raise ValueError(f"Vendor {vendor_id} not found or not active")
        
        # Generate RFQ number
        rfq_number = await self.generate_rfq_number()
        
        # Create RFQ
        rfq = RFQ(
            tenant_id=self.tenant_id,
            rfq_number=rfq_number,
            rfq_date=date.today(),
            due_date=rfq_data.due_date,
            status=RFQStatus.DRAFT,
            requisition_id=rfq_data.requisition_id,
            title=rfq_data.title,
            description=rfq_data.description,
            terms_and_conditions=rfq_data.terms_and_conditions,
            created_by=self.user_id
        )
        
        self.db.add(rfq)
        await self.db.flush()
        
        # Create RFQ items
        for item_data in rfq_data.items:
            item = RFQItem(
                rfq_id=rfq.id,
                item_code=item_data.item_code,
                item_name=item_data.item_name,
                description=item_data.description,
                specification=item_data.specification,
                quantity=item_data.quantity,
                unit_of_measure=item_data.unit_of_measure,
                requisition_item_id=item_data.requisition_item_id
            )
            self.db.add(item)
        
        # Add vendors to RFQ
        for vendor_id in rfq_data.vendor_ids:
            rfq_vendor = RFQVendor(
                rfq_id=rfq.id,
                vendor_id=vendor_id,
                invited_at=datetime.utcnow()
            )
            self.db.add(rfq_vendor)
        
        await self.db.commit()
        await self.db.refresh(rfq)
        await self.db.refresh(rfq, ['items', 'vendors'])
        
        return rfq
    
    async def get_rfq(self, rfq_id: uuid.UUID) -> Optional[RFQ]:
        """Get RFQ by ID"""
        query = select(RFQ).options(
            joinedload(RFQ.items),
            joinedload(RFQ.vendors)
        ).where(
            and_(
                RFQ.id == rfq_id,
                RFQ.tenant_id == self.tenant_id,
                RFQ.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def list_rfqs(
        self,
        status: Optional[RFQStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[RFQ], int]:
        """List RFQs with filters"""
        conditions = [
            RFQ.tenant_id == self.tenant_id,
            RFQ.is_deleted == False
        ]
        
        if status:
            conditions.append(RFQ.status == status)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    RFQ.rfq_number.ilike(search_pattern),
                    RFQ.title.ilike(search_pattern)
                )
            )
        
        # Count total
        count_query = select(func.count(RFQ.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get RFQs
        query = select(RFQ).options(
            joinedload(RFQ.items),
            joinedload(RFQ.vendors)
        ).where(and_(*conditions)).order_by(
            desc(RFQ.created_at)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        rfqs = result.unique().scalars().all()
        
        return list(rfqs), total
    
    async def send_rfq(self, rfq_id: uuid.UUID) -> RFQ:
        """Send RFQ to vendors"""
        rfq = await self.get_rfq(rfq_id)
        if not rfq:
            raise ValueError("RFQ not found")
        
        if rfq.status != RFQStatus.DRAFT:
            raise ValueError("Only draft RFQs can be sent")
        
        if not rfq.items:
            raise ValueError("RFQ must have at least one item")
        
        if not rfq.vendors:
            raise ValueError("RFQ must have at least one vendor")
        
        rfq.status = RFQStatus.SENT
        rfq.updated_by = self.user_id
        rfq.updated_at = datetime.utcnow()
        
        # TODO: Send email notifications to vendors
        
        await self.db.commit()
        await self.db.refresh(rfq)
        
        return rfq
    
    async def submit_vendor_quote(self, quote_data: VendorQuoteCreate) -> VendorQuote:
        """Submit vendor quote for RFQ item"""
        
        # Verify RFQ item exists and RFQ is sent
        item_query = select(RFQItem).options(
            joinedload(RFQItem.rfq)
        ).where(RFQItem.id == quote_data.rfq_item_id)
        
        item_result = await self.db.execute(item_query)
        rfq_item = item_result.unique().scalar_one_or_none()
        
        if not rfq_item:
            raise ValueError("RFQ item not found")
        
        if rfq_item.rfq.status not in [RFQStatus.SENT, RFQStatus.RESPONSE_RECEIVED]:
            raise ValueError("RFQ must be sent to receive quotes")
        
        # Create quote
        quote = VendorQuote(
            rfq_item_id=quote_data.rfq_item_id,
            vendor_id=quote_data.vendor_id,
            unit_price=quote_data.unit_price,
            total_price=quote_data.total_price,
            delivery_days=quote_data.delivery_days,
            warranty_months=quote_data.warranty_months,
            tax_percentage=quote_data.tax_percentage,
            tax_amount=quote_data.tax_amount,
            total_with_tax=quote_data.total_with_tax,
            remarks=quote_data.remarks,
            attachments=quote_data.attachments
        )
        
        self.db.add(quote)
        
        # Update RFQ vendor response status
        rfq_vendor_query = select(RFQVendor).where(
            and_(
                RFQVendor.rfq_id == rfq_item.rfq.id,
                RFQVendor.vendor_id == quote_data.vendor_id
            )
        )
        rfq_vendor_result = await self.db.execute(rfq_vendor_query)
        rfq_vendor = rfq_vendor_result.scalar_one_or_none()
        
        if rfq_vendor:
            rfq_vendor.is_responded = True
            rfq_vendor.responded_at = datetime.utcnow()
        
        # Update RFQ status
        rfq_item.rfq.status = RFQStatus.RESPONSE_RECEIVED
        
        await self.db.commit()
        await self.db.refresh(quote)
        
        return quote
    
    async def close_rfq(self, rfq_id: uuid.UUID) -> RFQ:
        """Close RFQ"""
        rfq = await self.get_rfq(rfq_id)
        if not rfq:
            raise ValueError("RFQ not found")
        
        rfq.status = RFQStatus.CLOSED
        rfq.updated_by = self.user_id
        rfq.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(rfq)
        
        return rfq
    
    # ========================================================================
    # Purchase Order Operations
    # ========================================================================
    
    async def generate_po_number(self) -> str:
        """Generate unique PO number"""
        # Format: PO-YYYYMM-NNNN
        current_date = date.today()
        prefix = f"PO-{current_date.strftime('%Y%m')}"
        
        query = select(PurchaseOrder.po_number).where(
            and_(
                PurchaseOrder.tenant_id == self.tenant_id,
                PurchaseOrder.po_number.like(f"{prefix}%")
            )
        ).order_by(desc(PurchaseOrder.created_at)).limit(1)
        
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
    
    async def create_purchase_order(self, po_data: PurchaseOrderCreate) -> PurchaseOrder:
        """Create new purchase order"""
        
        # Validate vendor
        vendor_query = select(Vendor).where(
            and_(
                Vendor.id == po_data.vendor_id,
                Vendor.tenant_id == self.tenant_id,
                Vendor.status == VendorStatus.ACTIVE,
                Vendor.is_deleted == False
            )
        )
        vendor_result = await self.db.execute(vendor_query)
        vendor = vendor_result.scalar_one_or_none()
        if not vendor:
            raise ValueError("Vendor not found or not active")
        
        # Validate RFQ if provided
        if po_data.rfq_id:
            rfq_query = select(RFQ).where(
                and_(
                    RFQ.id == po_data.rfq_id,
                    RFQ.tenant_id == self.tenant_id
                )
            )
            rfq_result = await self.db.execute(rfq_query)
            if not rfq_result.scalar_one_or_none():
                raise ValueError("RFQ not found")
        
        # Generate PO number
        po_number = await self.generate_po_number()
        
        # Create PO
        po = PurchaseOrder(
            tenant_id=self.tenant_id,
            po_number=po_number,
            po_date=date.today(),
            expected_delivery_date=po_data.expected_delivery_date,
            status=POStatus.DRAFT,
            vendor_id=po_data.vendor_id,
            rfq_id=po_data.rfq_id,
            requisition_id=po_data.requisition_id,
            delivery_address_line1=po_data.delivery_address_line1,
            delivery_address_line2=po_data.delivery_address_line2,
            delivery_city=po_data.delivery_city,
            delivery_state=po_data.delivery_state,
            delivery_pincode=po_data.delivery_pincode,
            delivery_country=po_data.delivery_country,
            delivery_contact_person=po_data.delivery_contact_person,
            delivery_contact_phone=po_data.delivery_contact_phone,
            subtotal=po_data.subtotal,
            tax_amount=po_data.tax_amount,
            discount_amount=po_data.discount_amount,
            total_amount=po_data.total_amount,
            payment_terms=po_data.payment_terms,
            advance_payment_percentage=po_data.advance_payment_percentage,
            advance_payment_amount=po_data.advance_payment_amount,
            terms_and_conditions=po_data.terms_and_conditions,
            special_instructions=po_data.special_instructions,
            created_by=self.user_id
        )
        
        self.db.add(po)
        await self.db.flush()
        
        # Create PO items
        for item_data in po_data.items:
            item = PurchaseOrderItem(
                po_id=po.id,
                item_code=item_data.item_code,
                item_name=item_data.item_name,
                description=item_data.description,
                specification=item_data.specification,
                ordered_quantity=item_data.ordered_quantity,
                unit_of_measure=item_data.unit_of_measure,
                unit_price=item_data.unit_price,
                total_price=item_data.total_price,
                tax_percentage=item_data.tax_percentage,
                tax_amount=item_data.tax_amount,
                discount_percentage=item_data.discount_percentage,
                discount_amount=item_data.discount_amount,
                net_amount=item_data.net_amount,
                rfq_item_id=item_data.rfq_item_id,
                requisition_item_id=item_data.requisition_item_id
            )
            self.db.add(item)
        
        # Update vendor total orders
        vendor.total_orders += 1
        
        await self.db.commit()
        await self.db.refresh(po)
        await self.db.refresh(po, ['items'])
        
        return po
    
    async def get_purchase_order(self, po_id: uuid.UUID) -> Optional[PurchaseOrder]:
        """Get purchase order by ID"""
        query = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.items)
        ).where(
            and_(
                PurchaseOrder.id == po_id,
                PurchaseOrder.tenant_id == self.tenant_id,
                PurchaseOrder.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def list_purchase_orders(
        self,
        status: Optional[POStatus] = None,
        vendor_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[PurchaseOrder], int]:
        """List purchase orders with filters"""
        conditions = [
            PurchaseOrder.tenant_id == self.tenant_id,
            PurchaseOrder.is_deleted == False
        ]
        
        if status:
            conditions.append(PurchaseOrder.status == status)
        if vendor_id:
            conditions.append(PurchaseOrder.vendor_id == vendor_id)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                PurchaseOrder.po_number.ilike(search_pattern)
            )
        
        # Count total
        count_query = select(func.count(PurchaseOrder.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get POs
        query = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.items)
        ).where(and_(*conditions)).order_by(
            desc(PurchaseOrder.created_at)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        pos = result.unique().scalars().all()
        
        return list(pos), total
    
    async def approve_purchase_order(self, po_id: uuid.UUID) -> PurchaseOrder:
        """Approve purchase order"""
        po = await self.get_purchase_order(po_id)
        if not po:
            raise ValueError("Purchase order not found")
        
        if po.status != POStatus.DRAFT:
            raise ValueError("Only draft purchase orders can be approved")
        
        po.status = POStatus.APPROVED
        po.approved_by = self.user_id
        po.approved_at = datetime.utcnow()
        po.updated_by = self.user_id
        po.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(po)
        
        return po
    
    async def send_po_to_vendor(self, po_id: uuid.UUID) -> PurchaseOrder:
        """Send PO to vendor"""
        po = await self.get_purchase_order(po_id)
        if not po:
            raise ValueError("Purchase order not found")
        
        if po.status != POStatus.APPROVED:
            raise ValueError("Only approved purchase orders can be sent")
        
        po.status = POStatus.SENT_TO_VENDOR
        po.updated_by = self.user_id
        po.updated_at = datetime.utcnow()
        
        # TODO: Send email to vendor
        
        await self.db.commit()
        await self.db.refresh(po)
        
        return po
    
    async def acknowledge_po(self, po_id: uuid.UUID) -> PurchaseOrder:
        """Vendor acknowledges PO"""
        po = await self.get_purchase_order(po_id)
        if not po:
            raise ValueError("Purchase order not found")
        
        if po.status != POStatus.SENT_TO_VENDOR:
            raise ValueError("PO must be sent to vendor before acknowledgment")
        
        po.status = POStatus.ACKNOWLEDGED
        po.acknowledged_by_vendor = True
        po.acknowledged_at = datetime.utcnow()
        po.updated_by = self.user_id
        po.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(po)
        
        return po
    
    async def cancel_purchase_order(self, po_id: uuid.UUID, reason: str) -> PurchaseOrder:
        """Cancel purchase order"""
        po = await self.get_purchase_order(po_id)
        if not po:
            raise ValueError("Purchase order not found")
        
        if po.status in [POStatus.FULLY_RECEIVED, POStatus.CLOSED]:
            raise ValueError("Cannot cancel completed or closed purchase orders")
        
        po.status = POStatus.CANCELLED
        po.special_instructions = f"{po.special_instructions or ''}\nCancellation Reason: {reason}"
        po.updated_by = self.user_id
        po.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(po)
        
        return po
    
    async def update_po_item_received_quantity(
        self,
        po_item_id: uuid.UUID,
        received_qty: Decimal
    ):
        """Update received quantity for PO item"""
        query = select(PurchaseOrderItem).where(
            PurchaseOrderItem.id == po_item_id
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError("PO item not found")
        
        item.received_quantity = received_qty
        
        # Check if all items are received
        po_query = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.items)
        ).where(PurchaseOrder.id == item.po_id)
        
        po_result = await self.db.execute(po_query)
        po = po_result.unique().scalar_one_or_none()
        
        if po:
            all_received = all(
                po_item.received_quantity >= po_item.ordered_quantity
                for po_item in po.items
            )
            any_received = any(
                po_item.received_quantity > 0
                for po_item in po.items
            )
            
            if all_received:
                po.status = POStatus.FULLY_RECEIVED
            elif any_received:
                po.status = POStatus.PARTIALLY_RECEIVED
        
        await self.db.commit()
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    async def get_po_statistics(self) -> dict:
        """Get purchase order statistics for dashboard"""
        
        # Count by status
        status_query = select(
            PurchaseOrder.status,
            func.count(PurchaseOrder.id).label('count'),
            func.sum(PurchaseOrder.total_amount).label('total_value')
        ).where(
            and_(
                PurchaseOrder.tenant_id == self.tenant_id,
                PurchaseOrder.is_deleted == False
            )
        ).group_by(PurchaseOrder.status)
        
        status_result = await self.db.execute(status_query)
        status_data = {}
        total_value = Decimal("0.00")
        
        for row in status_result:
            status_data[row.status] = {
                'count': row.count,
                'value': float(row.total_value or 0)
            }
            total_value += (row.total_value or Decimal("0.00"))
        
        # Count active POs
        active_count_query = select(
            func.count(PurchaseOrder.id)
        ).where(
            and_(
                PurchaseOrder.tenant_id == self.tenant_id,
                PurchaseOrder.is_deleted == False,
                PurchaseOrder.status.in_([
                    POStatus.APPROVED,
                    POStatus.SENT_TO_VENDOR,
                    POStatus.ACKNOWLEDGED,
                    POStatus.IN_PROGRESS,
                    POStatus.PARTIALLY_RECEIVED
                ])
            )
        )
        
        active_result = await self.db.execute(active_count_query)
        active_count = active_result.scalar()
        
        return {
            "total_pos": sum(data['count'] for data in status_data.values()),
            "by_status": status_data,
            "active_pos": active_count,
            "total_value": float(total_value)
        }
