"""
GRN and Invoice Processing Service
Business logic for goods receipt notes and vendor invoice management
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
import uuid

from backend.shared.database.procurement_models import (
    GoodsReceiptNote,
    GRNItem,
    VendorInvoice,
    VendorInvoiceItem,
    PurchaseOrder,
    PurchaseOrderItem,
    Vendor,
    GRNStatus,
    InvoiceStatus,
    InvoiceMatchingStatus,
    POStatus
)
from .schemas import (
    GoodsReceiptNoteCreate,
    GoodsReceiptNoteUpdate,
    QualityCheckRequest,
    VendorInvoiceCreate,
    VendorInvoiceUpdate,
    InvoiceMatchingResult
)


class GRNInvoiceService:
    """Service for managing GRN and Invoice operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # GRN Operations
    # ========================================================================
    
    async def generate_grn_number(self) -> str:
        """Generate unique GRN number"""
        # Format: GRN-YYYYMM-NNNN
        current_date = date.today()
        prefix = f"GRN-{current_date.strftime('%Y%m')}"
        
        query = select(GoodsReceiptNote.grn_number).where(
            and_(
                GoodsReceiptNote.tenant_id == self.tenant_id,
                GoodsReceiptNote.grn_number.like(f"{prefix}%")
            )
        ).order_by(desc(GoodsReceiptNote.created_at)).limit(1)
        
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
    
    async def create_grn(self, grn_data: GoodsReceiptNoteCreate) -> GoodsReceiptNote:
        """Create new GRN"""
        
        # Validate purchase order
        po_query = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.items)
        ).where(
            and_(
                PurchaseOrder.id == grn_data.po_id,
                PurchaseOrder.tenant_id == self.tenant_id,
                PurchaseOrder.status.in_([
                    POStatus.SENT_TO_VENDOR,
                    POStatus.ACKNOWLEDGED,
                    POStatus.IN_PROGRESS,
                    POStatus.PARTIALLY_RECEIVED
                ])
            )
        )
        po_result = await self.db.execute(po_query)
        po = po_result.unique().scalar_one_or_none()
        
        if not po:
            raise ValueError("Purchase order not found or not in correct status")
        
        # Generate GRN number
        grn_number = await self.generate_grn_number()
        
        # Create GRN
        grn = GoodsReceiptNote(
            tenant_id=self.tenant_id,
            grn_number=grn_number,
            grn_date=date.today(),
            receipt_date=grn_data.receipt_date,
            status=GRNStatus.DRAFT,
            po_id=grn_data.po_id,
            challan_number=grn_data.challan_number,
            challan_date=grn_data.challan_date,
            transporter_name=grn_data.transporter_name,
            vehicle_number=grn_data.vehicle_number,
            lr_number=grn_data.lr_number,
            quality_check_required=grn_data.quality_check_required,
            warehouse_location=grn_data.warehouse_location,
            remarks=grn_data.remarks,
            created_by=self.user_id
        )
        
        self.db.add(grn)
        await self.db.flush()
        
        # Create GRN items
        for item_data in grn_data.items:
            # Validate PO item
            po_item = next(
                (item for item in po.items if item.id == item_data.po_item_id),
                None
            )
            if not po_item:
                raise ValueError(f"PO item {item_data.po_item_id} not found")
            
            item = GRNItem(
                grn_id=grn.id,
                po_item_id=item_data.po_item_id,
                item_code=item_data.item_code,
                item_name=item_data.item_name,
                ordered_quantity=item_data.ordered_quantity,
                received_quantity=item_data.received_quantity,
                accepted_quantity=item_data.accepted_quantity,
                rejected_quantity=item_data.rejected_quantity,
                unit_of_measure=item_data.unit_of_measure,
                quality_status=item_data.quality_status,
                quality_remarks=item_data.quality_remarks,
                batch_number=item_data.batch_number,
                serial_numbers=item_data.serial_numbers,
                remarks=item_data.remarks
            )
            self.db.add(item)
        
        await self.db.commit()
        await self.db.refresh(grn)
        await self.db.refresh(grn, ['items'])
        
        return grn
    
    async def get_grn(self, grn_id: uuid.UUID) -> Optional[GoodsReceiptNote]:
        """Get GRN by ID"""
        query = select(GoodsReceiptNote).options(
            joinedload(GoodsReceiptNote.items)
        ).where(
            and_(
                GoodsReceiptNote.id == grn_id,
                GoodsReceiptNote.tenant_id == self.tenant_id,
                GoodsReceiptNote.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def list_grns(
        self,
        status: Optional[GRNStatus] = None,
        po_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[GoodsReceiptNote], int]:
        """List GRNs with filters"""
        conditions = [
            GoodsReceiptNote.tenant_id == self.tenant_id,
            GoodsReceiptNote.is_deleted == False
        ]
        
        if status:
            conditions.append(GoodsReceiptNote.status == status)
        if po_id:
            conditions.append(GoodsReceiptNote.po_id == po_id)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                GoodsReceiptNote.grn_number.ilike(search_pattern)
            )
        
        # Count total
        count_query = select(func.count(GoodsReceiptNote.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get GRNs
        query = select(GoodsReceiptNote).options(
            joinedload(GoodsReceiptNote.items)
        ).where(and_(*conditions)).order_by(
            desc(GoodsReceiptNote.created_at)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        grns = result.unique().scalars().all()
        
        return list(grns), total
    
    async def perform_quality_check(
        self,
        grn_id: uuid.UUID,
        quality_data: QualityCheckRequest
    ) -> GoodsReceiptNote:
        """Perform quality check on GRN"""
        grn = await self.get_grn(grn_id)
        if not grn:
            raise ValueError("GRN not found")
        
        if grn.status not in [GRNStatus.RECEIVED, GRNStatus.QUALITY_CHECK_PENDING]:
            raise ValueError("GRN not in correct status for quality check")
        
        # Update GRN items with quality check results
        for item_data in quality_data.items:
            item_query = select(GRNItem).where(
                and_(
                    GRNItem.id == item_data.get('grn_item_id'),
                    GRNItem.grn_id == grn_id
                )
            )
            item_result = await self.db.execute(item_query)
            item = item_result.scalar_one_or_none()
            
            if item:
                item.accepted_quantity = Decimal(str(item_data.get('accepted_quantity', 0)))
                item.rejected_quantity = Decimal(str(item_data.get('rejected_quantity', 0)))
                item.quality_status = item_data.get('quality_status')
                item.quality_remarks = item_data.get('quality_remarks')
        
        # Update GRN status
        if quality_data.passed:
            grn.status = GRNStatus.QUALITY_CHECK_PASSED
        else:
            grn.status = GRNStatus.QUALITY_CHECK_FAILED
        
        grn.quality_checked_by = self.user_id
        grn.quality_checked_at = datetime.utcnow()
        grn.quality_remarks = quality_data.quality_remarks
        grn.updated_by = self.user_id
        grn.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(grn)
        
        return grn
    
    async def accept_grn(self, grn_id: uuid.UUID) -> GoodsReceiptNote:
        """Accept GRN after quality check"""
        grn = await self.get_grn(grn_id)
        if not grn:
            raise ValueError("GRN not found")
        
        if grn.status != GRNStatus.QUALITY_CHECK_PASSED:
            raise ValueError("GRN must pass quality check before acceptance")
        
        grn.status = GRNStatus.ACCEPTED
        grn.updated_by = self.user_id
        grn.updated_at = datetime.utcnow()
        
        # Update PO item received quantities
        from .rfq_po_service import RFQPOService
        po_service = RFQPOService(self.db, self.tenant_id, self.user_id)
        
        for grn_item in grn.items:
            if grn_item.accepted_quantity > 0:
                await po_service.update_po_item_received_quantity(
                    grn_item.po_item_id,
                    grn_item.accepted_quantity
                )
        
        await self.db.commit()
        await self.db.refresh(grn)
        
        return grn
    
    # ========================================================================
    # Vendor Invoice Operations
    # ========================================================================
    
    async def generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        # Format: INV-YYYYMM-NNNN
        current_date = date.today()
        prefix = f"INV-{current_date.strftime('%Y%m')}"
        
        query = select(VendorInvoice.invoice_number).where(
            and_(
                VendorInvoice.tenant_id == self.tenant_id,
                VendorInvoice.invoice_number.like(f"{prefix}%")
            )
        ).order_by(desc(VendorInvoice.created_at)).limit(1)
        
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
    
    async def create_vendor_invoice(
        self,
        invoice_data: VendorInvoiceCreate
    ) -> VendorInvoice:
        """Create new vendor invoice"""
        
        # Validate purchase order
        po_query = select(PurchaseOrder).where(
            and_(
                PurchaseOrder.id == invoice_data.po_id,
                PurchaseOrder.tenant_id == self.tenant_id
            )
        )
        po_result = await self.db.execute(po_query)
        po = po_result.scalar_one_or_none()
        
        if not po:
            raise ValueError("Purchase order not found")
        
        # Validate vendor
        vendor_query = select(Vendor).where(
            and_(
                Vendor.id == invoice_data.vendor_id,
                Vendor.tenant_id == self.tenant_id
            )
        )
        vendor_result = await self.db.execute(vendor_query)
        if not vendor_result.scalar_one_or_none():
            raise ValueError("Vendor not found")
        
        # Check for duplicate vendor invoice number
        dup_query = select(VendorInvoice).where(
            and_(
                VendorInvoice.vendor_id == invoice_data.vendor_id,
                VendorInvoice.vendor_invoice_number == invoice_data.vendor_invoice_number,
                VendorInvoice.is_deleted == False
            )
        )
        dup_result = await self.db.execute(dup_query)
        if dup_result.scalar_one_or_none():
            raise ValueError(f"Invoice {invoice_data.vendor_invoice_number} already exists for this vendor")
        
        # Generate internal invoice number
        invoice_number = await self.generate_invoice_number()
        
        # Create invoice
        invoice = VendorInvoice(
            tenant_id=self.tenant_id,
            invoice_number=invoice_number,
            vendor_invoice_number=invoice_data.vendor_invoice_number,
            invoice_date=invoice_data.invoice_date,
            due_date=invoice_data.due_date,
            status=InvoiceStatus.DRAFT,
            matching_status=InvoiceMatchingStatus.NOT_MATCHED,
            po_id=invoice_data.po_id,
            grn_id=invoice_data.grn_id,
            vendor_id=invoice_data.vendor_id,
            subtotal=invoice_data.subtotal,
            tax_amount=invoice_data.tax_amount,
            other_charges=invoice_data.other_charges,
            discount_amount=invoice_data.discount_amount,
            total_amount=invoice_data.total_amount,
            balance_amount=invoice_data.total_amount,
            gst_number=invoice_data.gst_number,
            cgst_amount=invoice_data.cgst_amount,
            sgst_amount=invoice_data.sgst_amount,
            igst_amount=invoice_data.igst_amount,
            tolerance_percentage=invoice_data.tolerance_percentage,
            invoice_file_url=invoice_data.invoice_file_url,
            supporting_documents=invoice_data.supporting_documents,
            remarks=invoice_data.remarks,
            created_by=self.user_id
        )
        
        self.db.add(invoice)
        await self.db.flush()
        
        # Create invoice items
        for item_data in invoice_data.items:
            item = VendorInvoiceItem(
                invoice_id=invoice.id,
                po_item_id=item_data.po_item_id,
                item_code=item_data.item_code,
                item_name=item_data.item_name,
                description=item_data.description,
                quantity=item_data.quantity,
                unit_of_measure=item_data.unit_of_measure,
                unit_price=item_data.unit_price,
                total_price=item_data.total_price,
                tax_percentage=item_data.tax_percentage,
                tax_amount=item_data.tax_amount,
                discount_percentage=item_data.discount_percentage,
                discount_amount=item_data.discount_amount,
                net_amount=item_data.net_amount
            )
            self.db.add(item)
        
        await self.db.commit()
        await self.db.refresh(invoice)
        await self.db.refresh(invoice, ['items'])
        
        return invoice
    
    async def get_vendor_invoice(self, invoice_id: uuid.UUID) -> Optional[VendorInvoice]:
        """Get vendor invoice by ID"""
        query = select(VendorInvoice).options(
            joinedload(VendorInvoice.items)
        ).where(
            and_(
                VendorInvoice.id == invoice_id,
                VendorInvoice.tenant_id == self.tenant_id,
                VendorInvoice.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def list_vendor_invoices(
        self,
        status: Optional[InvoiceStatus] = None,
        matching_status: Optional[InvoiceMatchingStatus] = None,
        vendor_id: Optional[uuid.UUID] = None,
        po_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[VendorInvoice], int]:
        """List vendor invoices with filters"""
        conditions = [
            VendorInvoice.tenant_id == self.tenant_id,
            VendorInvoice.is_deleted == False
        ]
        
        if status:
            conditions.append(VendorInvoice.status == status)
        if matching_status:
            conditions.append(VendorInvoice.matching_status == matching_status)
        if vendor_id:
            conditions.append(VendorInvoice.vendor_id == vendor_id)
        if po_id:
            conditions.append(VendorInvoice.po_id == po_id)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    VendorInvoice.invoice_number.ilike(search_pattern),
                    VendorInvoice.vendor_invoice_number.ilike(search_pattern)
                )
            )
        
        # Count total
        count_query = select(func.count(VendorInvoice.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get invoices
        query = select(VendorInvoice).options(
            joinedload(VendorInvoice.items)
        ).where(and_(*conditions)).order_by(
            desc(VendorInvoice.created_at)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        invoices = result.unique().scalars().all()
        
        return list(invoices), total
    
    async def perform_3way_matching(
        self,
        invoice_id: uuid.UUID
    ) -> InvoiceMatchingResult:
        """Perform 3-way matching: Invoice vs PO vs GRN"""
        invoice = await self.get_vendor_invoice(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        
        # Get PO
        po_query = select(PurchaseOrder).options(
            joinedload(PurchaseOrder.items)
        ).where(PurchaseOrder.id == invoice.po_id)
        
        po_result = await self.db.execute(po_query)
        po = po_result.unique().scalar_one_or_none()
        
        if not po:
            raise ValueError("Purchase order not found")
        
        issues = []
        matched = True
        matching_status = InvoiceMatchingStatus.THREE_WAY_MATCHED
        
        # Check amount variance with PO
        po_amount_variance = invoice.total_amount - po.total_amount
        invoice.po_amount_variance = po_amount_variance
        
        tolerance_amount = (po.total_amount * invoice.tolerance_percentage) / Decimal("100.0")
        
        if abs(po_amount_variance) > tolerance_amount:
            matched = False
            matching_status = InvoiceMatchingStatus.PRICE_MISMATCH
            issues.append(
                f"Invoice amount ({invoice.total_amount}) exceeds PO amount ({po.total_amount}) "
                f"by {abs(po_amount_variance)} (tolerance: {tolerance_amount})"
            )
        
        # If GRN exists, perform 3-way matching
        if invoice.grn_id:
            grn_query = select(GoodsReceiptNote).options(
                joinedload(GoodsReceiptNote.items)
            ).where(GoodsReceiptNote.id == invoice.grn_id)
            
            grn_result = await self.db.execute(grn_query)
            grn = grn_result.unique().scalar_one_or_none()
            
            if grn:
                # Check quantity variance
                total_invoice_qty = sum(item.quantity for item in invoice.items)
                total_grn_qty = sum(item.accepted_quantity for item in grn.items)
                
                quantity_variance = total_invoice_qty - total_grn_qty
                invoice.grn_quantity_variance = quantity_variance
                
                if abs(quantity_variance) > Decimal("0.01"):
                    matched = False
                    matching_status = InvoiceMatchingStatus.QUANTITY_MISMATCH
                    issues.append(
                        f"Invoice quantity ({total_invoice_qty}) does not match "
                        f"GRN accepted quantity ({total_grn_qty})"
                    )
        else:
            # 2-way matching only (Invoice vs PO)
            if matched:
                matching_status = InvoiceMatchingStatus.TWO_WAY_MATCHED
        
        # Update invoice matching status
        invoice.matching_status = matching_status
        
        if matched:
            invoice.status = InvoiceStatus.MATCHED
        else:
            invoice.status = InvoiceStatus.MISMATCH
        
        invoice.updated_by = self.user_id
        invoice.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        return InvoiceMatchingResult(
            matched=matched,
            matching_status=matching_status,
            po_amount_variance=po_amount_variance,
            grn_quantity_variance=invoice.grn_quantity_variance,
            issues=issues
        )
    
    async def approve_invoice(self, invoice_id: uuid.UUID) -> VendorInvoice:
        """Approve vendor invoice"""
        invoice = await self.get_vendor_invoice(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        
        if invoice.status not in [InvoiceStatus.MATCHED, InvoiceStatus.UNDER_VERIFICATION]:
            raise ValueError("Only matched or verified invoices can be approved")
        
        invoice.status = InvoiceStatus.APPROVED
        invoice.approved_by = self.user_id
        invoice.approved_at = datetime.utcnow()
        invoice.updated_by = self.user_id
        invoice.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(invoice)
        
        return invoice
    
    async def reject_invoice(
        self,
        invoice_id: uuid.UUID,
        reason: str
    ) -> VendorInvoice:
        """Reject vendor invoice"""
        invoice = await self.get_vendor_invoice(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        
        invoice.status = InvoiceStatus.REJECTED
        invoice.rejection_reason = reason
        invoice.updated_by = self.user_id
        invoice.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(invoice)
        
        return invoice
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    async def get_invoice_statistics(self) -> dict:
        """Get invoice statistics for dashboard"""
        
        # Count by status
        status_query = select(
            VendorInvoice.status,
            func.count(VendorInvoice.id).label('count'),
            func.sum(VendorInvoice.total_amount).label('total_value')
        ).where(
            and_(
                VendorInvoice.tenant_id == self.tenant_id,
                VendorInvoice.is_deleted == False
            )
        ).group_by(VendorInvoice.status)
        
        status_result = await self.db.execute(status_query)
        status_data = {}
        
        for row in status_result:
            status_data[row.status] = {
                'count': row.count,
                'value': float(row.total_value or 0)
            }
        
        # Pending payments
        pending_query = select(
            func.sum(VendorInvoice.balance_amount)
        ).where(
            and_(
                VendorInvoice.tenant_id == self.tenant_id,
                VendorInvoice.is_deleted == False,
                VendorInvoice.status.in_([
                    InvoiceStatus.APPROVED,
                    InvoiceStatus.PARTIALLY_PAID
                ])
            )
        )
        
        pending_result = await self.db.execute(pending_query)
        pending_amount = pending_result.scalar() or Decimal("0.00")
        
        return {
            "total_invoices": sum(data['count'] for data in status_data.values()),
            "by_status": status_data,
            "pending_payment_amount": float(pending_amount)
        }
