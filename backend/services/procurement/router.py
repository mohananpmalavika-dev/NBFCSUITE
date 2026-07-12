"""
Procurement Module Main Router
Combines all procurement sub-routers
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user

from backend.services.procurement.vendor_service import VendorService
from backend.services.procurement.requisition_service import RequisitionService
from backend.services.procurement.rfq_po_service import RFQPOService
from backend.services.procurement.grn_invoice_service import GRNInvoiceService
from backend.services.procurement import schemas
from backend.shared.database.procurement_models import (
    VendorStatus, VendorType, RequisitionStatus, RequisitionPriority,
    RFQStatus, POStatus, GRNStatus, InvoiceStatus, InvoiceMatchingStatus
)


router = APIRouter(prefix="/procurement", tags=["Procurement"])


# Dependency functions
def get_vendor_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> VendorService:
    return VendorService(db, current_user["tenant_id"], uuid.UUID(current_user["id"]))


def get_requisition_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> RequisitionService:
    return RequisitionService(
        db, current_user["tenant_id"], 
        uuid.UUID(current_user["id"]), 
        current_user.get("name", "Unknown")
    )


def get_rfq_po_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> RFQPOService:
    return RFQPOService(db, current_user["tenant_id"], uuid.UUID(current_user["id"]))


def get_grn_invoice_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> GRNInvoiceService:
    return GRNInvoiceService(db, current_user["tenant_id"], uuid.UUID(current_user["id"]))


# ============================================================================
# VENDOR ENDPOINTS
# ============================================================================

@router.post("/vendors", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: schemas.VendorCreate,
    service: VendorService = Depends(get_vendor_service)
):
    """Create new vendor"""
    try:
        vendor = await service.create_vendor(vendor_data)
        return success_response(
            data=schemas.VendorResponse.from_orm(vendor),
            message="Vendor created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/vendors", response_model=dict)
async def list_vendors(
    status: Optional[VendorStatus] = None,
    vendor_type: Optional[VendorType] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: VendorService = Depends(get_vendor_service)
):
    """List vendors with filters"""
    skip = (page - 1) * page_size
    vendors, total = await service.list_vendors(status, vendor_type, search, skip, page_size)
    
    return success_response(
        data=schemas.VendorListResponse(
            vendors=[schemas.VendorResponse.from_orm(v) for v in vendors],
            total=total, page=page, page_size=page_size
        )
    )


@router.get("/vendors/{vendor_id}", response_model=dict)
async def get_vendor(
    vendor_id: uuid.UUID,
    service: VendorService = Depends(get_vendor_service)
):
    """Get vendor by ID"""
    vendor = await service.get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return success_response(data=schemas.VendorResponse.from_orm(vendor))


@router.put("/vendors/{vendor_id}", response_model=dict)
async def update_vendor(
    vendor_id: uuid.UUID,
    vendor_data: schemas.VendorUpdate,
    service: VendorService = Depends(get_vendor_service)
):
    """Update vendor"""
    try:
        vendor = await service.update_vendor(vendor_id, vendor_data)
        return success_response(data=schemas.VendorResponse.from_orm(vendor), message="Vendor updated")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============================================================================
# PURCHASE REQUISITION ENDPOINTS
# ============================================================================

@router.post("/requisitions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_requisition(
    req_data: schemas.PurchaseRequisitionCreate,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Create purchase requisition"""
    try:
        requisition = await service.create_requisition(req_data)
        return success_response(
            data=schemas.PurchaseRequisitionResponse.from_orm(requisition),
            message="Requisition created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requisitions", response_model=dict)
async def list_requisitions(
    status: Optional[RequisitionStatus] = None,
    priority: Optional[RequisitionPriority] = None,
    department: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: RequisitionService = Depends(get_requisition_service)
):
    """List requisitions with filters"""
    skip = (page - 1) * page_size
    requisitions, total = await service.list_requisitions(
        status, priority, department, None, None, skip, page_size
    )
    
    return success_response(
        data=schemas.PurchaseRequisitionListResponse(
            requisitions=[schemas.PurchaseRequisitionResponse.from_orm(r) for r in requisitions],
            total=total, page=page, page_size=page_size
        )
    )


@router.get("/requisitions/{req_id}", response_model=dict)
async def get_requisition(
    req_id: uuid.UUID,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Get requisition by ID"""
    requisition = await service.get_requisition(req_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    return success_response(data=schemas.PurchaseRequisitionResponse.from_orm(requisition))


@router.post("/requisitions/{req_id}/submit", response_model=dict)
async def submit_requisition(
    req_id: uuid.UUID,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Submit requisition for approval"""
    try:
        requisition = await service.submit_requisition(req_id)
        return success_response(
            data=schemas.PurchaseRequisitionResponse.from_orm(requisition),
            message="Requisition submitted for approval"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/requisitions/{req_id}/approve", response_model=dict)
async def approve_requisition(
    req_id: uuid.UUID,
    approval_data: schemas.PurchaseRequisitionApproval,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Approve or reject requisition"""
    try:
        requisition = await service.approve_requisition(req_id, approval_data)
        return success_response(
            data=schemas.PurchaseRequisitionResponse.from_orm(requisition),
            message="Requisition processed"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# RFQ ENDPOINTS
# ============================================================================

@router.post("/rfqs", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_rfq(
    rfq_data: schemas.RFQCreate,
    service: RFQPOService = Depends(get_rfq_po_service)
):
    """Create RFQ"""
    try:
        rfq = await service.create_rfq(rfq_data)
        return success_response(
            data=schemas.RFQResponse.from_orm(rfq),
            message="RFQ created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rfqs", response_model=dict)
async def list_rfqs(
    status: Optional[RFQStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: RFQPOService = Depends(get_rfq_po_service)
):
    """List RFQs"""
    skip = (page - 1) * page_size
    rfqs, total = await service.list_rfqs(status, None, skip, page_size)
    
    return success_response(
        data=schemas.RFQListResponse(
            rfqs=[schemas.RFQResponse.from_orm(r) for r in rfqs],
            total=total, page=page, page_size=page_size
        )
    )


@router.post("/rfqs/{rfq_id}/send", response_model=dict)
async def send_rfq(
    rfq_id: uuid.UUID,
    service: RFQPOService = Depends(get_rfq_po_service)
):
    """Send RFQ to vendors"""
    try:
        rfq = await service.send_rfq(rfq_id)
        return success_response(data=schemas.RFQResponse.from_orm(rfq), message="RFQ sent to vendors")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============================================================================
# PURCHASE ORDER ENDPOINTS
# ============================================================================

@router.post("/purchase-orders", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    po_data: schemas.PurchaseOrderCreate,
    service: RFQPOService = Depends(get_rfq_po_service)
):
    """Create purchase order"""
    try:
        po = await service.create_purchase_order(po_data)
        return success_response(
            data=schemas.PurchaseOrderResponse.from_orm(po),
            message="Purchase order created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/purchase-orders", response_model=dict)
async def list_purchase_orders(
    status: Optional[POStatus] = None,
    vendor_id: Optional[uuid.UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: RFQPOService = Depends(get_rfq_po_service)
):
    """List purchase orders"""
    skip = (page - 1) * page_size
    pos, total = await service.list_purchase_orders(status, vendor_id, None, skip, page_size)
    
    return success_response(
        data=schemas.PurchaseOrderListResponse(
            purchase_orders=[schemas.PurchaseOrderResponse.from_orm(po) for po in pos],
            total=total, page=page, page_size=page_size
        )
    )


@router.get("/purchase-orders/{po_id}", response_model=dict)
async def get_purchase_order(
    po_id: uuid.UUID,
    service: RFQPOService = Depends(get_rfq_po_service)
):
    """Get purchase order by ID"""
    po = await service.get_purchase_order(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return success_response(data=schemas.PurchaseOrderResponse.from_orm(po))


@router.post("/purchase-orders/{po_id}/approve", response_model=dict)
async def approve_purchase_order(
    po_id: uuid.UUID,
    service: RFQPOService = Depends(get_rfq_po_service)
):
    """Approve purchase order"""
    try:
        po = await service.approve_purchase_order(po_id)
        return success_response(data=schemas.PurchaseOrderResponse.from_orm(po), message="PO approved")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/purchase-orders/{po_id}/send", response_model=dict)
async def send_po_to_vendor(
    po_id: uuid.UUID,
    service: RFQPOService = Depends(get_rfq_po_service)
):
    """Send PO to vendor"""
    try:
        po = await service.send_po_to_vendor(po_id)
        return success_response(data=schemas.PurchaseOrderResponse.from_orm(po), message="PO sent to vendor")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# GRN ENDPOINTS
# ============================================================================

@router.post("/grns", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_grn(
    grn_data: schemas.GoodsReceiptNoteCreate,
    service: GRNInvoiceService = Depends(get_grn_invoice_service)
):
    """Create goods receipt note"""
    try:
        grn = await service.create_grn(grn_data)
        return success_response(
            data=schemas.GoodsReceiptNoteResponse.from_orm(grn),
            message="GRN created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/grns", response_model=dict)
async def list_grns(
    status: Optional[GRNStatus] = None,
    po_id: Optional[uuid.UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: GRNInvoiceService = Depends(get_grn_invoice_service)
):
    """List GRNs"""
    skip = (page - 1) * page_size
    grns, total = await service.list_grns(status, po_id, None, skip, page_size)
    
    return success_response(
        data=schemas.GoodsReceiptNoteListResponse(
            grns=[schemas.GoodsReceiptNoteResponse.from_orm(g) for g in grns],
            total=total, page=page, page_size=page_size
        )
    )


@router.post("/grns/{grn_id}/quality-check", response_model=dict)
async def perform_quality_check(
    grn_id: uuid.UUID,
    quality_data: schemas.QualityCheckRequest,
    service: GRNInvoiceService = Depends(get_grn_invoice_service)
):
    """Perform quality check on GRN"""
    try:
        grn = await service.perform_quality_check(grn_id, quality_data)
        return success_response(data=schemas.GoodsReceiptNoteResponse.from_orm(grn), message="Quality check completed")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/grns/{grn_id}/accept", response_model=dict)
async def accept_grn(
    grn_id: uuid.UUID,
    service: GRNInvoiceService = Depends(get_grn_invoice_service)
):
    """Accept GRN"""
    try:
        grn = await service.accept_grn(grn_id)
        return success_response(data=schemas.GoodsReceiptNoteResponse.from_orm(grn), message="GRN accepted")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============================================================================
# VENDOR INVOICE ENDPOINTS
# ============================================================================

@router.post("/invoices", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_vendor_invoice(
    invoice_data: schemas.VendorInvoiceCreate,
    service: GRNInvoiceService = Depends(get_grn_invoice_service)
):
    """Create vendor invoice"""
    try:
        invoice = await service.create_vendor_invoice(invoice_data)
        return success_response(
            data=schemas.VendorInvoiceResponse.from_orm(invoice),
            message="Invoice created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/invoices", response_model=dict)
async def list_invoices(
    status: Optional[InvoiceStatus] = None,
    matching_status: Optional[InvoiceMatchingStatus] = None,
    vendor_id: Optional[uuid.UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: GRNInvoiceService = Depends(get_grn_invoice_service)
):
    """List vendor invoices"""
    skip = (page - 1) * page_size
    invoices, total = await service.list_vendor_invoices(
        status, matching_status, vendor_id, None, None, skip, page_size
    )
    
    return success_response(
        data=schemas.VendorInvoiceListResponse(
            invoices=[schemas.VendorInvoiceResponse.from_orm(inv) for inv in invoices],
            total=total, page=page, page_size=page_size
        )
    )


@router.post("/invoices/{invoice_id}/match", response_model=dict)
async def perform_invoice_matching(
    invoice_id: uuid.UUID,
    service: GRNInvoiceService = Depends(get_grn_invoice_service)
):
    """Perform 3-way matching on invoice"""
    try:
        result = await service.perform_3way_matching(invoice_id)
        return success_response(data=result, message="Invoice matching completed")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invoices/{invoice_id}/approve", response_model=dict)
async def approve_invoice(
    invoice_id: uuid.UUID,
    service: GRNInvoiceService = Depends(get_grn_invoice_service)
):
    """Approve invoice"""
    try:
        invoice = await service.approve_invoice(invoice_id)
        return success_response(data=schemas.VendorInvoiceResponse.from_orm(invoice), message="Invoice approved")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# DASHBOARD & STATISTICS ENDPOINTS
# ============================================================================

@router.get("/dashboard/metrics", response_model=dict)
async def get_dashboard_metrics(
    vendor_service: VendorService = Depends(get_vendor_service),
    requisition_service: RequisitionService = Depends(get_requisition_service),
    po_service: RFQPOService = Depends(get_rfq_po_service),
    invoice_service: GRNInvoiceService = Depends(get_grn_invoice_service)
):
    """Get procurement dashboard metrics"""
    try:
        vendor_stats = await vendor_service.get_vendor_statistics()
        requisition_stats = await requisition_service.get_requisition_statistics()
        po_stats = await po_service.get_po_statistics()
        invoice_stats = await invoice_service.get_invoice_statistics()
        
        dashboard_metrics = schemas.ProcurementDashboardMetrics(
            total_vendors=vendor_stats.get("total_vendors", 0),
            active_vendors=vendor_stats.get("by_status", {}).get("active", 0),
            total_requisitions=requisition_stats.get("total_requisitions", 0),
            pending_approvals=requisition_stats.get("pending_approvals", 0),
            active_rfqs=0,  # TODO: Add RFQ stats
            open_purchase_orders=po_stats.get("active_pos", 0),
            pending_grns=0,  # TODO: Add GRN stats
            pending_invoices=invoice_stats.get("total_invoices", 0),
            total_procurement_value=po_stats.get("total_value", 0),
            monthly_procurement_value=0  # TODO: Add monthly calculation
        )
        
        return success_response(data=dashboard_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
