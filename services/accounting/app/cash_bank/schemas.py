from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CashDrawerCreate(BaseModel):
    tenant_id: str
    branch_id: str
    drawer_code: str
    drawer_name: str
    capacity: Optional[float] = None
    opening_balance: Optional[float] = 0.0
    currency: Optional[str] = "INR"
    custodian: Optional[str] = None
    approval_limit: Optional[float] = 0.0
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class CashDrawerResponse(CashDrawerCreate):
    id: str
    status: str
    closing_balance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CashTransferCreate(BaseModel):
    tenant_id: str
    transfer_type: str
    transfer_reference: str
    amount: float
    currency: Optional[str] = "INR"
    source_drawer_id: Optional[str] = None
    destination_drawer_id: Optional[str] = None
    source_bank_account_id: Optional[str] = None
    destination_bank_account_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class CashTransferResponse(CashTransferCreate):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BankAccountCreate(BaseModel):
    tenant_id: str
    bank_name: str
    branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    swift_code: Optional[str] = None
    account_number: str
    account_type: str
    currency: Optional[str] = "INR"
    balance: Optional[float] = 0.0
    status: Optional[str] = "active"
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class BankAccountResponse(BankAccountCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class LiquidityDashboardResponse(BaseModel):
    tenant_id: str
    total_cash_balance: float
    total_bank_balance: float
    total_transfers: float
    cash_drawer_count: int
    bank_account_count: int

    class Config:
        from_attributes = True
