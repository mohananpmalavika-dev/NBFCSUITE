from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TaxRateResponse(BaseModel):
    id: str
    tenant_id: str
    tax_type: str
    rate: float
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    status: str
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class TaxCalculationRequest(BaseModel):
    tenant_id: str
    tax_type: str
    jurisdiction: Optional[str] = None
    base_amount: float
    invoice_type: Optional[str] = None
    inclusive: Optional[bool] = False


class TaxCalculationResponse(BaseModel):
    tenant_id: str
    tax_type: str
    base_amount: float
    tax_rate: float
    tax_amount: float
    total_amount: float
    jurisdiction: Optional[str] = None


class TaxDashboardResponse(BaseModel):
    tenant_id: str
    total_gst_transactions: int
    total_tds_transactions: int
    total_einvoices: int
    total_ewaybills: int
    net_tax_liability: float


class TaxReturnCreate(BaseModel):
    tenant_id: str
    return_type: str
    period: str
    details: Optional[Dict[str, Any]] = None


class TaxReturnResponse(BaseModel):
    id: str
    tenant_id: str
    return_type: str
    period: str
    status: str
    details: Optional[Dict[str, Any]] = None
    filed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaxLedgerItem(BaseModel):
    id: str
    tenant_id: str
    reference_id: Optional[str] = None
    entry_type: str
    amount: float
    tax_type: Optional[str] = None
    entry_date: datetime
    status: str

    class Config:
        from_attributes = True


class TaxLedgerResponse(BaseModel):
    tenant_id: str
    entries: List[TaxLedgerItem]


class TaxReconciliationRequest(BaseModel):
    tenant_id: str
    reference_id: Optional[str] = None
    reported_amount: float
    recorded_amount: float
    metadata: Optional[Dict[str, Any]] = None


class TaxReconciliationResponse(BaseModel):
    id: str
    tenant_id: str
    reference_id: Optional[str] = None
    difference_amount: float
    status: str

    class Config:
        from_attributes = True


class EInvoiceCreate(BaseModel):
    tenant_id: str
    invoice_id: str
    invoice_date: datetime
    amount: float
    metadata: Optional[Dict[str, Any]] = None


class EInvoiceResponse(BaseModel):
    id: str
    tenant_id: str
    invoice_id: str
    irn: str
    qr_code: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class EWayBillCreate(BaseModel):
    tenant_id: str
    invoice_id: str
    vehicle_number: Optional[str] = None
    transporter_name: Optional[str] = None
    from_place: Optional[str] = None
    to_place: Optional[str] = None
    distance_km: Optional[float] = None


class EWayBillResponse(BaseModel):
    id: str
    tenant_id: str
    ewaybill_number: str
    vehicle_number: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class TaxComplianceResponse(BaseModel):
    tenant_id: str
    gst_compliance: str
    tds_compliance: str
    itc_utilization: float
    outstanding_returns: int
    compliance_health: str
