from datetime import datetime
from typing import List, Optional
from uuid import uuid4
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, JSON, String, UniqueConstraint, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Vendor(Base):
    __tablename__ = "procurement_vendors"
    __table_args__ = (UniqueConstraint("tenant_id", "vendor_code", name="uq_vendor_tenant_code"),)

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    vendor_code = Column(String, index=True, nullable=False)
    vendor_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    gstin = Column(String, nullable=True)
    payment_terms = Column(String, default="net_30")
    status = Column(String, default="active")
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    __table_args__ = (UniqueConstraint("tenant_id", "po_number", name="uq_po_tenant_number"),)

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    po_number = Column(String, index=True, nullable=False)
    vendor_id = Column(String, index=True, nullable=False)
    department = Column(String, index=True, nullable=True)
    requested_by = Column(String, nullable=True)
    items = Column(JSON, nullable=False)
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    status = Column(String, default="draft", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    po_id = Column(String, index=True, nullable=False)
    received_by = Column(String)
    received_items = Column(JSON, nullable=False)
    status = Column(String, default="received")
    received_at = Column(DateTime, default=datetime.utcnow)


class VendorInvoice(Base):
    __tablename__ = "vendor_invoices"
    __table_args__ = (UniqueConstraint("tenant_id", "invoice_number", name="uq_vendor_invoice_tenant_number"),)

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    vendor_id = Column(String, index=True, nullable=False)
    po_id = Column(String, index=True, nullable=True)
    invoice_number = Column(String, index=True, nullable=False)
    invoice_date = Column(DateTime)
    amount = Column(Float)
    tax_amount = Column(Float, default=0.0)
    status = Column(String, default="submitted", index=True)
    payment_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class VendorCreate(BaseModel):
    tenant_id: str
    vendor_code: str
    vendor_name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    gstin: Optional[str] = None
    payment_terms: str = "net_30"
    metadata: Optional[dict] = None


class VendorResponse(BaseModel):
    id: str
    tenant_id: str
    vendor_code: str
    vendor_name: str
    contact_email: Optional[str]
    phone: Optional[str]
    gstin: Optional[str]
    payment_terms: str
    status: str
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class PurchaseOrderItem(BaseModel):
    sku: Optional[str] = None
    description: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(gt=0)
    tax_rate_percent: float = Field(default=0.0, ge=0)


class PurchaseOrderCreate(BaseModel):
    tenant_id: str
    vendor_code: str
    department: Optional[str] = None
    requested_by: Optional[str] = None
    items: List[PurchaseOrderItem]


class PurchaseOrderResponse(BaseModel):
    id: str
    tenant_id: str
    po_number: str
    vendor_id: str
    department: Optional[str]
    requested_by: Optional[str]
    items: list
    subtotal: float
    tax_amount: float
    total_amount: float
    status: str
    created_at: datetime
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True


class GoodsReceiptCreate(BaseModel):
    tenant_id: str
    received_by: str
    received_items: List[dict]


class GoodsReceiptResponse(BaseModel):
    id: str
    tenant_id: str
    po_id: str
    received_by: str
    received_items: list
    status: str
    received_at: datetime

    class Config:
        from_attributes = True


class VendorInvoiceCreate(BaseModel):
    tenant_id: str
    vendor_code: str
    invoice_number: str
    invoice_date: Optional[datetime] = None
    amount: float = Field(gt=0)
    tax_amount: float = Field(default=0.0, ge=0)
    po_id: Optional[str] = None


class VendorInvoiceResponse(BaseModel):
    id: str
    tenant_id: str
    vendor_id: str
    po_id: Optional[str]
    invoice_number: str
    invoice_date: datetime
    amount: float
    tax_amount: float
    status: str
    payment_reference: Optional[str]

    class Config:
        from_attributes = True


class InvoicePaymentRequest(BaseModel):
    tenant_id: str
    payment_reference: str


app = FastAPI(title="procurement-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "procurement"}


@app.get("/ready")
async def ready():
    return {"ready": True}


def _vendor_by_code(tenant_id: str, vendor_code: str, db: Session) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.tenant_id == tenant_id, Vendor.vendor_code == vendor_code).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found for tenant")
    if vendor.status != "active":
        raise HTTPException(status_code=400, detail="Vendor is not active")
    return vendor


def _po(po_id: str, tenant_id: str, db: Session) -> PurchaseOrder:
    record = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id, PurchaseOrder.tenant_id == tenant_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Purchase order not found for tenant")
    return record


def _vendor_response(vendor: Vendor) -> dict:
    return {
        "id": vendor.id,
        "tenant_id": vendor.tenant_id,
        "vendor_code": vendor.vendor_code,
        "vendor_name": vendor.vendor_name,
        "contact_email": vendor.contact_email,
        "phone": vendor.phone,
        "gstin": vendor.gstin,
        "payment_terms": vendor.payment_terms,
        "status": vendor.status,
        "metadata": vendor.metadata_json,
    }


def _totals(items: List[PurchaseOrderItem]) -> tuple[float, float, float, list[dict]]:
    rows = []
    subtotal = 0.0
    tax_amount = 0.0
    for item in items:
        line_subtotal = round(item.quantity * item.unit_price, 2)
        line_tax = round(line_subtotal * item.tax_rate_percent / 100, 2)
        subtotal += line_subtotal
        tax_amount += line_tax
        row = item.model_dump()
        row["line_subtotal"] = line_subtotal
        row["line_tax"] = line_tax
        row["line_total"] = round(line_subtotal + line_tax, 2)
        rows.append(row)
    return round(subtotal, 2), round(tax_amount, 2), round(subtotal + tax_amount, 2), rows


@app.post("/vendors", response_model=VendorResponse)
async def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    existing = db.query(Vendor).filter(Vendor.tenant_id == payload.tenant_id, Vendor.vendor_code == payload.vendor_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vendor code already exists for tenant")
    vendor = Vendor(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        vendor_code=payload.vendor_code,
        vendor_name=payload.vendor_name,
        contact_email=payload.contact_email,
        phone=payload.phone,
        gstin=payload.gstin,
        payment_terms=payload.payment_terms,
        metadata_json=payload.metadata,
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return _vendor_response(vendor)


@app.get("/vendors", response_model=List[VendorResponse])
async def list_vendors(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Vendor).filter(Vendor.tenant_id == tenant_id)
    if status:
        query = query.filter(Vendor.status == status)
    return [_vendor_response(vendor) for vendor in query.order_by(Vendor.vendor_name.asc()).all()]


@app.post("/purchase-orders", response_model=PurchaseOrderResponse)
async def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Purchase order must include at least one item")
    vendor = _vendor_by_code(payload.tenant_id, payload.vendor_code, db)
    subtotal, tax_amount, total_amount, items = _totals(payload.items)
    po = PurchaseOrder(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        po_number=f"PO-{str(uuid4())[:10].upper()}",
        vendor_id=vendor.id,
        department=payload.department,
        requested_by=payload.requested_by,
        items=items,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
    )
    db.add(po)
    db.commit()
    db.refresh(po)
    return po


@app.post("/purchase-orders/{po_id}/approve", response_model=PurchaseOrderResponse)
async def approve_purchase_order(po_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    po = _po(po_id, tenant_id, db)
    if po.status not in {"draft", "submitted"}:
        raise HTTPException(status_code=400, detail="Purchase order is not approvable")
    po.status = "approved"
    po.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(po)
    return po


@app.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    tenant_id: str = Query(...),
    vendor_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PurchaseOrder).filter(PurchaseOrder.tenant_id == tenant_id)
    if vendor_id:
        query = query.filter(PurchaseOrder.vendor_id == vendor_id)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    return query.order_by(PurchaseOrder.created_at.desc()).all()


@app.post("/purchase-orders/{po_id}/goods-receipts", response_model=GoodsReceiptResponse)
async def receive_goods(po_id: str, payload: GoodsReceiptCreate, db: Session = Depends(get_db)):
    po = _po(po_id, payload.tenant_id, db)
    if po.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved purchase orders can receive goods")
    receipt = GoodsReceipt(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        po_id=po.id,
        received_by=payload.received_by,
        received_items=payload.received_items,
    )
    po.status = "received"
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


@app.post("/vendor-invoices", response_model=VendorInvoiceResponse)
async def create_vendor_invoice(payload: VendorInvoiceCreate, db: Session = Depends(get_db)):
    vendor = _vendor_by_code(payload.tenant_id, payload.vendor_code, db)
    existing = db.query(VendorInvoice).filter(
        VendorInvoice.tenant_id == payload.tenant_id,
        VendorInvoice.invoice_number == payload.invoice_number,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Invoice number already exists for tenant")
    if payload.po_id:
        _po(payload.po_id, payload.tenant_id, db)
    invoice = VendorInvoice(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        vendor_id=vendor.id,
        po_id=payload.po_id,
        invoice_number=payload.invoice_number,
        invoice_date=payload.invoice_date or datetime.utcnow(),
        amount=payload.amount,
        tax_amount=payload.tax_amount,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@app.post("/vendor-invoices/{invoice_id}/mark-paid", response_model=VendorInvoiceResponse)
async def mark_invoice_paid(invoice_id: str, payload: InvoicePaymentRequest, db: Session = Depends(get_db)):
    invoice = db.query(VendorInvoice).filter(VendorInvoice.id == invoice_id, VendorInvoice.tenant_id == payload.tenant_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Vendor invoice not found for tenant")
    invoice.status = "paid"
    invoice.payment_reference = payload.payment_reference
    db.commit()
    db.refresh(invoice)
    return invoice


@app.get("/vendor-invoices", response_model=List[VendorInvoiceResponse])
async def list_vendor_invoices(
    tenant_id: str = Query(...),
    vendor_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(VendorInvoice).filter(VendorInvoice.tenant_id == tenant_id)
    if vendor_id:
        query = query.filter(VendorInvoice.vendor_id == vendor_id)
    if status:
        query = query.filter(VendorInvoice.status == status)
    return query.order_by(VendorInvoice.created_at.desc()).all()


@app.get("/")
async def root():
    return {"service": "procurement", "version": "0.1.0"}
