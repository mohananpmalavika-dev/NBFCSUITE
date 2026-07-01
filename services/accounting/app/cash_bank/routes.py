from datetime import datetime
from uuid import uuid4
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.cash_bank.models import CashDrawer, CashTransfer, BankAccount
from app.cash_bank.schemas import (
    BankAccountCreate,
    BankAccountResponse,
    CashDrawerCreate,
    CashDrawerResponse,
    CashTransferCreate,
    CashTransferResponse,
    LiquidityDashboardResponse,
)


def _get_db():
    from app.main import get_db

    return get_db()


router = APIRouter(tags=["cash bank"])


def _cash_drawer_response(drawer: CashDrawer) -> CashDrawerResponse:
    return CashDrawerResponse(
        id=drawer.id,
        tenant_id=drawer.tenant_id,
        branch_id=drawer.branch_id,
        drawer_code=drawer.drawer_code,
        drawer_name=drawer.drawer_name,
        capacity=drawer.capacity,
        status=drawer.status,
        opening_balance=drawer.opening_balance,
        closing_balance=drawer.closing_balance,
        currency=drawer.currency,
        custodian=drawer.custodian,
        approval_limit=drawer.approval_limit,
        metadata=drawer.metadata_json,
        created_by=drawer.created_by,
        created_at=drawer.created_at,
        updated_at=drawer.updated_at,
    )


def _bank_account_response(account: BankAccount) -> BankAccountResponse:
    return BankAccountResponse(
        id=account.id,
        tenant_id=account.tenant_id,
        bank_name=account.bank_name,
        branch_name=account.branch_name,
        ifsc_code=account.ifsc_code,
        swift_code=account.swift_code,
        account_number=account.account_number,
        account_type=account.account_type,
        currency=account.currency,
        balance=account.balance,
        status=account.status,
        metadata=account.metadata_json,
        created_by=account.created_by,
        created_at=account.created_at,
    )


@router.post("/cash/drawers", response_model=CashDrawerResponse)
async def create_cash_drawer(drawer: CashDrawerCreate, db: Session = Depends(_get_db)):
    existing = db.query(CashDrawer).filter(
        CashDrawer.tenant_id == drawer.tenant_id,
        CashDrawer.drawer_code == drawer.drawer_code,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cash drawer already exists")

    entity = CashDrawer(
        id=str(uuid4()),
        tenant_id=drawer.tenant_id,
        branch_id=drawer.branch_id,
        drawer_code=drawer.drawer_code,
        drawer_name=drawer.drawer_name,
        capacity=drawer.capacity,
        opening_balance=drawer.opening_balance,
        closing_balance=drawer.opening_balance,
        currency=drawer.currency,
        custodian=drawer.custodian,
        approval_limit=drawer.approval_limit,
        metadata_json=drawer.metadata,
        created_by=drawer.created_by,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return _cash_drawer_response(entity)


@router.get("/cash/drawers", response_model=List[CashDrawerResponse])
async def list_cash_drawers(
    tenant_id: str = Query(...),
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(_get_db),
):
    query = db.query(CashDrawer).filter(CashDrawer.tenant_id == tenant_id)
    if branch_id:
        query = query.filter(CashDrawer.branch_id == branch_id)
    return [_cash_drawer_response(item) for item in query.all()]


@router.post("/bank/accounts", response_model=BankAccountResponse)
async def create_bank_account(account: BankAccountCreate, db: Session = Depends(_get_db)):
    existing = db.query(BankAccount).filter(
        BankAccount.tenant_id == account.tenant_id,
        BankAccount.account_number == account.account_number,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bank account already exists")

    entity = BankAccount(
        id=str(uuid4()),
        tenant_id=account.tenant_id,
        bank_name=account.bank_name,
        branch_name=account.branch_name,
        ifsc_code=account.ifsc_code,
        swift_code=account.swift_code,
        account_number=account.account_number,
        account_type=account.account_type,
        currency=account.currency,
        balance=account.balance,
        status=account.status,
        metadata_json=account.metadata,
        created_by=account.created_by,
        created_at=datetime.utcnow(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return _bank_account_response(entity)


@router.get("/bank/accounts", response_model=List[BankAccountResponse])
async def list_bank_accounts(
    tenant_id: str = Query(...),
    bank_name: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
    db: Session = Depends(_get_db),
):
    query = db.query(BankAccount).filter(BankAccount.tenant_id == tenant_id)
    if bank_name:
        query = query.filter(BankAccount.bank_name == bank_name)
    if account_type:
        query = query.filter(BankAccount.account_type == account_type)
    return [_bank_account_response(item) for item in query.all()]


@router.post("/cash/transfers", response_model=CashTransferResponse)
async def create_cash_transfer(transfer: CashTransferCreate, db: Session = Depends(_get_db)):
    if transfer.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be greater than zero")

    entity = CashTransfer(
        id=str(uuid4()),
        tenant_id=transfer.tenant_id,
        source_drawer_id=transfer.source_drawer_id,
        destination_drawer_id=transfer.destination_drawer_id,
        source_bank_account_id=transfer.source_bank_account_id,
        destination_bank_account_id=transfer.destination_bank_account_id,
        transfer_type=transfer.transfer_type,
        transfer_reference=transfer.transfer_reference,
        amount=round(transfer.amount, 2),
        currency=transfer.currency,
        status="completed",
        description=transfer.description,
        metadata_json=transfer.metadata,
        created_by=transfer.created_by,
        created_at=datetime.utcnow(),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return CashTransferResponse(**transfer.dict(), id=entity.id, status=entity.status, created_at=entity.created_at)


@router.get("/cash/dashboard", response_model=LiquidityDashboardResponse)
async def cash_dashboard(tenant_id: str = Query(...), db: Session = Depends(_get_db)):
    total_cash_balance = sum(item.closing_balance for item in db.query(CashDrawer).filter(CashDrawer.tenant_id == tenant_id).all())
    total_bank_balance = sum(item.balance for item in db.query(BankAccount).filter(BankAccount.tenant_id == tenant_id).all())
    total_transfers = sum(item.amount for item in db.query(CashTransfer).filter(CashTransfer.tenant_id == tenant_id).all())
    cash_drawer_count = db.query(CashDrawer).filter(CashDrawer.tenant_id == tenant_id).count()
    bank_account_count = db.query(BankAccount).filter(BankAccount.tenant_id == tenant_id).count()

    return LiquidityDashboardResponse(
        tenant_id=tenant_id,
        total_cash_balance=round(total_cash_balance, 2),
        total_bank_balance=round(total_bank_balance, 2),
        total_transfers=round(total_transfers, 2),
        cash_drawer_count=cash_drawer_count,
        bank_account_count=bank_account_count,
    )
