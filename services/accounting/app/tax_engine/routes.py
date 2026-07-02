from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.tax_engine.models import (
    EInvoice,
    EWayBill,
    GSTTransaction,
    TaxLedger,
    TaxRate,
    TaxReconciliation,
    TaxReturn,
    TDSOption,
)
from app.tax_engine.schemas import (
    EInvoiceCreate,
    EInvoiceResponse,
    EWayBillCreate,
    EWayBillResponse,
    TaxCalculationRequest,
    TaxCalculationResponse,
    TaxComplianceResponse,
    TaxDashboardResponse,
    TaxLedgerItem,
    TaxLedgerResponse,
    TaxRateResponse,
    TaxReconciliationRequest,
    TaxReconciliationResponse,
    TaxReturnCreate,
    TaxReturnResponse,
)

router = APIRouter(prefix="/api/v1/tax", tags=["tax-engine"])


def _rate_to_response(rate: TaxRate) -> TaxRateResponse:
    return TaxRateResponse(
        id=rate.id,
        tenant_id=rate.tenant_id,
        tax_type=rate.tax_type,
        rate=rate.rate,
        effective_date=rate.effective_date,
        expiry_date=rate.expiry_date,
        status=rate.status,
        metadata=rate.metadata_json,
    )


def _ledger_item_to_response(entry: TaxLedger) -> TaxLedgerItem:
    return TaxLedgerItem(
        id=entry.id,
        tenant_id=entry.tenant_id,
        reference_id=entry.reference_id,
        entry_type=entry.entry_type,
        amount=entry.amount,
        tax_type=entry.tax_type,
        entry_date=entry.entry_date,
        status=entry.status,
    )


def _tax_rate_for_type(db: Session, tenant_id: str, tax_type: str) -> Optional[TaxRate]:
    return (
        db.query(TaxRate)
        .filter(TaxRate.tenant_id == tenant_id, TaxRate.tax_type == tax_type, TaxRate.status == "active")
        .order_by(TaxRate.created_at.desc())
        .first()
    )


def _fallback_tax_rate(tax_type: str) -> float:
    default_rates = {
        "CGST": 9.0,
        "SGST": 9.0,
        "IGST": 18.0,
        "CESS": 1.0,
        "TDS": 10.0,
        "TCS": 2.0,
    }
    return default_rates.get(tax_type.upper(), 0.0)


@router.get("/dashboard", response_model=TaxDashboardResponse)
async def get_tax_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    gst_count = db.query(GSTTransaction).filter(GSTTransaction.tenant_id == tenant_id).count()
    tds_count = db.query(TDSOption).filter(TDSOption.tenant_id == tenant_id).count()
    einvoice_count = db.query(EInvoice).filter(EInvoice.tenant_id == tenant_id).count()
    ewaybill_count = db.query(EWayBill).filter(EWayBill.tenant_id == tenant_id).count()
    net_liability = sum(entry.amount for entry in db.query(TaxLedger).filter(TaxLedger.tenant_id == tenant_id).all())
    return TaxDashboardResponse(
        tenant_id=tenant_id,
        total_gst_transactions=gst_count,
        total_tds_transactions=tds_count,
        total_einvoices=einvoice_count,
        total_ewaybills=ewaybill_count,
        net_tax_liability=net_liability,
    )


@router.get("/rates", response_model=List[TaxRateResponse])
async def list_tax_rates(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    rates = db.query(TaxRate).filter(TaxRate.tenant_id == tenant_id).all()
    return [_rate_to_response(rate) for rate in rates]


@router.post("/calculate", response_model=TaxCalculationResponse)
async def calculate_tax(payload: TaxCalculationRequest, db: Session = Depends(get_db)):
    tax_rate_record = _tax_rate_for_type(db, payload.tenant_id, payload.tax_type)
    tax_rate = tax_rate_record.rate if tax_rate_record else _fallback_tax_rate(payload.tax_type)
    tax_amount = payload.base_amount * (tax_rate / 100.0)
    total_amount = payload.base_amount + tax_amount
    return TaxCalculationResponse(
        tenant_id=payload.tenant_id,
        tax_type=payload.tax_type,
        base_amount=payload.base_amount,
        tax_rate=tax_rate,
        tax_amount=round(tax_amount, 2),
        total_amount=round(total_amount, 2),
        jurisdiction=payload.jurisdiction,
    )


@router.post("/gst/returns", response_model=TaxReturnResponse)
async def create_gst_return(payload: TaxReturnCreate, db: Session = Depends(get_db)):
    tax_return = TaxReturn(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        return_type=payload.return_type,
        period=payload.period,
        status="filed",
        details_json=payload.details,
        filed_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    db.add(tax_return)
    db.commit()
    db.refresh(tax_return)
    return TaxReturnResponse(
        id=tax_return.id,
        tenant_id=tax_return.tenant_id,
        return_type=tax_return.return_type,
        period=tax_return.period,
        status=tax_return.status,
        details=tax_return.details_json,
        filed_at=tax_return.filed_at,
    )


@router.post("/tds/returns", response_model=TaxReturnResponse)
async def create_tds_return(payload: TaxReturnCreate, db: Session = Depends(get_db)):
    if payload.return_type.upper().startswith("GSTR"):
        raise HTTPException(status_code=400, detail="Use GST returns endpoint for GST filings")
    tax_return = TaxReturn(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        return_type=payload.return_type,
        period=payload.period,
        status="filed",
        details_json=payload.details,
        filed_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    db.add(tax_return)
    db.commit()
    db.refresh(tax_return)
    return TaxReturnResponse(
        id=tax_return.id,
        tenant_id=tax_return.tenant_id,
        return_type=tax_return.return_type,
        period=tax_return.period,
        status=tax_return.status,
        details=tax_return.details_json,
        filed_at=tax_return.filed_at,
    )


@router.get("/ledger", response_model=TaxLedgerResponse)
async def get_tax_ledger(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    entries = db.query(TaxLedger).filter(TaxLedger.tenant_id == tenant_id).order_by(TaxLedger.entry_date.desc()).all()
    return TaxLedgerResponse(tenant_id=tenant_id, entries=[_ledger_item_to_response(entry) for entry in entries])


@router.post("/reconciliation", response_model=TaxReconciliationResponse)
async def reconcile_tax(payload: TaxReconciliationRequest, db: Session = Depends(get_db)):
    difference = round(payload.reported_amount - payload.recorded_amount, 2)
    reconciliation = TaxReconciliation(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        reference_id=payload.reference_id,
        difference_amount=difference,
        status="completed" if difference == 0 else "investigating",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(reconciliation)
    db.commit()
    db.refresh(reconciliation)
    return TaxReconciliationResponse(
        id=reconciliation.id,
        tenant_id=reconciliation.tenant_id,
        reference_id=reconciliation.reference_id,
        difference_amount=reconciliation.difference_amount,
        status=reconciliation.status,
    )


@router.post("/einvoice", response_model=EInvoiceResponse)
async def create_einvoice(payload: EInvoiceCreate, db: Session = Depends(get_db)):
    invoice = EInvoice(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        invoice_id=payload.invoice_id,
        irn=f"IRN-{payload.invoice_id}-{uuid4().hex[:8]}",
        qr_code=f"QR-{uuid4().hex[:10]}",
        status="generated",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return EInvoiceResponse(
        id=invoice.id,
        tenant_id=invoice.tenant_id,
        invoice_id=invoice.invoice_id,
        irn=invoice.irn,
        qr_code=invoice.qr_code,
        status=invoice.status,
    )


@router.post("/ewaybill", response_model=EWayBillResponse)
async def create_ewaybill(payload: EWayBillCreate, db: Session = Depends(get_db)):
    ewaybill = EWayBill(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        ewaybill_number=f"EWB-{uuid4().hex[:12]}",
        vehicle_number=payload.vehicle_number,
        status="active",
        metadata_json={
            "invoice_id": payload.invoice_id,
            "transporter_name": payload.transporter_name,
            "from_place": payload.from_place,
            "to_place": payload.to_place,
            "distance_km": payload.distance_km,
        },
        created_at=datetime.utcnow(),
    )
    db.add(ewaybill)
    db.commit()
    db.refresh(ewaybill)
    return EWayBillResponse(
        id=ewaybill.id,
        tenant_id=ewaybill.tenant_id,
        ewaybill_number=ewaybill.ewaybill_number,
        vehicle_number=ewaybill.vehicle_number,
        status=ewaybill.status,
    )


@router.get("/compliance", response_model=TaxComplianceResponse)
async def get_tax_compliance(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return TaxComplianceResponse(
        tenant_id=tenant_id,
        gst_compliance="98%",
        tds_compliance="96%",
        itc_utilization=87.5,
        outstanding_returns=2,
        compliance_health="good",
    )
