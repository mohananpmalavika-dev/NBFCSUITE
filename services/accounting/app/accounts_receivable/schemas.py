from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class CustomerSummaryResponse(BaseModel):
    customer_id: str
    customer_name: Optional[str] = None
    outstanding_balance: float
    total_receivables: int

    class Config:
        from_attributes = True


class CustomerReceivableCreate(BaseModel):
    tenant_id: str
    customer_id: str
    customer_name: Optional[str] = None
    receivable_number: str
    product_type: str
    amount: float
    currency: Optional[str] = "INR"
    due_date: Optional[datetime] = None
    status: Optional[str] = "pending"
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class CustomerReceivableResponse(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    receivable_number: str
    product_type: str
    amount: float
    currency: str
    due_date: Optional[datetime]
    status: str
    posted_to_accounting: str
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReceiptCreate(BaseModel):
    tenant_id: str
    customer_id: str
    receipt_number: str
    payment_method: str
    amount: float
    currency: Optional[str] = "INR"
    receipt_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class ReceiptResponse(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    receipt_number: str
    payment_method: str
    amount: float
    currency: str
    receipt_date: datetime
    status: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AllocationItem(BaseModel):
    receipt_id: str
    receivable_id: str
    amount: float


class AllocationRequest(BaseModel):
    tenant_id: str
    items: List[AllocationItem]


class AllocationResponse(BaseModel):
    allocations_created: int
    allocated_amount: float


class LedgerSummaryResponse(BaseModel):
    tenant_id: str
    customer_id: str
    outstanding_balance: float
    total_receivables: int
    total_receipts: float
    receivables: List[CustomerReceivableResponse]
    receipts: List[ReceiptResponse]


class AgingBucket(BaseModel):
    bucket: str
    amount: float
    receivables: int


class AgingResponse(BaseModel):
    tenant_id: str
    aging_buckets: List[AgingBucket]


class SettlementRequest(BaseModel):
    tenant_id: str
    customer_id: str
    receivable_id: Optional[str] = None
    settlement_amount: float
    settlement_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class SettlementResponse(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    receivable_id: Optional[str] = None
    settlement_amount: float
    settlement_date: datetime
    status: str
    created_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WriteOffRequest(BaseModel):
    tenant_id: str
    customer_id: str
    receivable_id: Optional[str] = None
    write_off_amount: float
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class WriteOffResponse(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    receivable_id: Optional[str] = None
    write_off_amount: float
    reason: Optional[str] = None
    status: str
    created_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ARDashboardResponse(BaseModel):
    tenant_id: str
    total_receivables: int
    total_outstanding: float
    total_receipts: float
    overdue_receivables: int
    current_receivables: int


class PagedReceivableResponse(BaseModel):
    items: List[CustomerReceivableResponse]
    total: int
