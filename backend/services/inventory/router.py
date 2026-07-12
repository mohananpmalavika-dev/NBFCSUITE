"""
Inventory Management Main Router
Combines all inventory sub-routers
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import uuid

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id

from backend.services.inventory.item_service import ItemMasterService
from backend.services.inventory.transaction_service import StockTransactionService
from backend.services.inventory.verification_service import StockVerificationService
from backend.services.inventory.valuation_service import InventoryValuationService
from backend.services.inventory import schemas
from backend.shared.database.inventory_models import (
    ItemType, ItemStatus, TransactionType, TransactionStatus,
    VerificationStatus, ValuationMethod
)


router = APIRouter(prefix="/inventory", tags=["Inventory"])


# Dependency functions
def get_item_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> ItemMasterService:
    return ItemMasterService(db, current_user["tenant_id"], uuid.UUID(current_user["id"]))


def get_transaction_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> StockTransactionService:
    return StockTransactionService(db, current_user["tenant_id"], uuid.UUID(current_user["id"]))


def get_verification_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> StockVerificationService:
    return StockVerificationService(db, current_user["tenant_id"], uuid.UUID(current_user["id"]))


def get_valuation_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> InventoryValuationService:
    return InventoryValuationService(db, current_user["tenant_id"], uuid.UUID(current_user["id"]))


# ============================================================================
# ITEM MASTER ENDPOINTS
# ============================================================================

@router.post("/items", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: schemas.ItemMasterCreate,
    service: ItemMasterService = Depends(get_item_service)
):
    """Create new item"""
    try:
        item = await service.create_item(item_data)
        return success_response(
            data=schemas.ItemMasterResponse.from_orm(item),
            message="Item created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/items", response_model=dict)
async def list_items(
    item_type: Optional[ItemType] = None,
    item_status: Optional[ItemStatus] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    low_stock_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: ItemMasterService = Depends(get_item_service)
):
    """List items with filters"""
    skip = (page - 1) * page_size
    items, total = await service.list_items(
        item_type, item_status, category, search, low_stock_only, skip, page_size
    )
    
    return success_response(
        data=schemas.ItemMasterListResponse(
            items=[schemas.ItemMasterResponse.from_orm(i) for i in items],
            total=total, page=page, page_size=page_size
        )
    )


@router.get("/items/{item_id}", response_model=dict)
async def get_item(
    item_id: uuid.UUID,
    service: ItemMasterService = Depends(get_item_service)
):
    """Get item by ID"""
    item = await service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return success_response(data=schemas.ItemMasterResponse.from_orm(item))


@router.put("/items/{item_id}", response_model=dict)
async def update_item(
    item_id: uuid.UUID,
    item_data: schemas.ItemMasterUpdate,
    service: ItemMasterService = Depends(get_item_service)
):
    """Update item"""
    try:
        item = await service.update_item(item_id, item_data)
        return success_response(
            data=schemas.ItemMasterResponse.from_orm(item),
            message="Item updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/items/{item_id}", response_model=dict)
async def delete_item(
    item_id: uuid.UUID,
    service: ItemMasterService = Depends(get_item_service)
):
    """Delete item"""
    try:
        await service.delete_item(item_id)
        return success_response(message="Item deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/items/alerts/low-stock", response_model=dict)
async def get_low_stock_items(
    service: ItemMasterService = Depends(get_item_service)
):
    """Get items below reorder level"""
    items = await service.get_low_stock_items()
    return success_response(
        data=[schemas.ItemMasterResponse.from_orm(i) for i in items]
    )



# ============================================================================
# STOCK TRANSACTION ENDPOINTS
# ============================================================================

@router.post("/transactions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    txn_data: schemas.StockTransactionCreate,
    service: StockTransactionService = Depends(get_transaction_service)
):
    """Create stock transaction"""
    try:
        transaction = await service.create_transaction(txn_data)
        return success_response(
            data=schemas.StockTransactionResponse.from_orm(transaction),
            message="Transaction created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=dict)
async def list_transactions(
    transaction_type: Optional[TransactionType] = None,
    transaction_status: Optional[TransactionStatus] = None,
    item_id: Optional[uuid.UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: StockTransactionService = Depends(get_transaction_service)
):
    """List transactions with filters"""
    skip = (page - 1) * page_size
    transactions, total = await service.list_transactions(
        transaction_type, transaction_status, item_id, from_date, to_date, skip, page_size
    )
    
    return success_response(
        data=schemas.StockTransactionListResponse(
            transactions=[schemas.StockTransactionResponse.from_orm(t) for t in transactions],
            total=total, page=page, page_size=page_size
        )
    )


@router.get("/transactions/{txn_id}", response_model=dict)
async def get_transaction(
    txn_id: uuid.UUID,
    service: StockTransactionService = Depends(get_transaction_service)
):
    """Get transaction by ID"""
    transaction = await service.get_transaction(txn_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return success_response(data=schemas.StockTransactionResponse.from_orm(transaction))


@router.post("/transactions/{txn_id}/approve", response_model=dict)
async def approve_transaction(
    txn_id: uuid.UUID,
    service: StockTransactionService = Depends(get_transaction_service)
):
    """Approve transaction"""
    try:
        transaction = await service.approve_transaction(txn_id)
        return success_response(
            data=schemas.StockTransactionResponse.from_orm(transaction),
            message="Transaction approved successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transactions/{txn_id}/post", response_model=dict)
async def post_transaction(
    txn_id: uuid.UUID,
    service: StockTransactionService = Depends(get_transaction_service)
):
    """Post transaction to update stock"""
    try:
        transaction = await service.post_transaction(txn_id)
        return success_response(
            data=schemas.StockTransactionResponse.from_orm(transaction),
            message="Transaction posted successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transactions/{txn_id}/cancel", response_model=dict)
async def cancel_transaction(
    txn_id: uuid.UUID,
    reason: str = Query(..., min_length=1),
    service: StockTransactionService = Depends(get_transaction_service)
):
    """Cancel transaction"""
    try:
        transaction = await service.cancel_transaction(txn_id, reason)
        return success_response(
            data=schemas.StockTransactionResponse.from_orm(transaction),
            message="Transaction cancelled"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions/item/{item_id}/ledger", response_model=dict)
async def get_stock_ledger(
    item_id: uuid.UUID,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    service: StockTransactionService = Depends(get_transaction_service)
):
    """Get stock ledger for an item"""
    ledger = await service.get_stock_ledger(item_id, from_date, to_date)
    return success_response(
        data=[schemas.StockLedgerEntry.from_orm(entry) for entry in ledger]
    )



# ============================================================================
# STOCK VERIFICATION ENDPOINTS
# ============================================================================

@router.post("/verifications", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_verification(
    verification_data: schemas.StockVerificationCreate,
    service: StockVerificationService = Depends(get_verification_service)
):
    """Create stock verification"""
    try:
        verification = await service.create_verification(verification_data)
        return success_response(
            data=schemas.StockVerificationResponse.from_orm(verification),
            message="Verification created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/verifications", response_model=dict)
async def list_verifications(
    verification_status: Optional[VerificationStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: StockVerificationService = Depends(get_verification_service)
):
    """List verifications with filters"""
    skip = (page - 1) * page_size
    verifications, total = await service.list_verifications(
        verification_status, from_date, to_date, skip, page_size
    )
    
    return success_response(
        data=schemas.StockVerificationListResponse(
            verifications=[schemas.StockVerificationResponse.from_orm(v) for v in verifications],
            total=total, page=page, page_size=page_size
        )
    )


@router.get("/verifications/{verification_id}", response_model=dict)
async def get_verification(
    verification_id: uuid.UUID,
    service: StockVerificationService = Depends(get_verification_service)
):
    """Get verification by ID"""
    verification = await service.get_verification(verification_id)
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    return success_response(data=schemas.StockVerificationResponse.from_orm(verification))


@router.put("/verifications/items/{item_id}", response_model=dict)
async def update_verification_item(
    item_id: uuid.UUID,
    update_data: schemas.StockVerificationItemUpdate,
    service: StockVerificationService = Depends(get_verification_service)
):
    """Update physical quantity for verification item"""
    try:
        verification_item = await service.update_verification_item(
            item_id, update_data.physical_quantity, update_data.remarks
        )
        return success_response(
            data=schemas.StockVerificationItemResponse.from_orm(verification_item),
            message="Verification item updated"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verifications/{verification_id}/complete", response_model=dict)
async def complete_verification(
    verification_id: uuid.UUID,
    service: StockVerificationService = Depends(get_verification_service)
):
    """Complete verification"""
    try:
        verification = await service.complete_verification(verification_id)
        return success_response(
            data=schemas.StockVerificationResponse.from_orm(verification),
            message="Verification completed"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verifications/items/{item_id}/reconcile", response_model=dict)
async def reconcile_variance(
    item_id: uuid.UUID,
    reconciliation_notes: str = Query(..., min_length=1),
    service: StockVerificationService = Depends(get_verification_service)
):
    """Reconcile variance"""
    try:
        verification_item = await service.reconcile_variance(item_id, reconciliation_notes)
        return success_response(
            data=schemas.StockVerificationItemResponse.from_orm(verification_item),
            message="Variance reconciled"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============================================================================
# INVENTORY VALUATION ENDPOINTS
# ============================================================================

@router.post("/valuations", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_valuation(
    valuation_data: schemas.InventoryValuationCreate,
    service: InventoryValuationService = Depends(get_valuation_service)
):
    """Create inventory valuation"""
    try:
        valuation = await service.create_valuation(valuation_data)
        return success_response(
            data=schemas.InventoryValuationResponse.from_orm(valuation),
            message="Valuation created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/valuations", response_model=dict)
async def list_valuations(
    financial_year: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: InventoryValuationService = Depends(get_valuation_service)
):
    """List valuations with filters"""
    skip = (page - 1) * page_size
    valuations, total = await service.list_valuations(
        financial_year, from_date, to_date, skip, page_size
    )
    
    return success_response(
        data=schemas.InventoryValuationListResponse(
            valuations=[schemas.InventoryValuationResponse.from_orm(v) for v in valuations],
            total=total, page=page, page_size=page_size
        )
    )


@router.get("/valuations/{valuation_id}", response_model=dict)
async def get_valuation(
    valuation_id: uuid.UUID,
    service: InventoryValuationService = Depends(get_valuation_service)
):
    """Get valuation by ID"""
    valuation = await service.get_valuation(valuation_id)
    if not valuation:
        raise HTTPException(status_code=404, detail="Valuation not found")
    return success_response(data=schemas.InventoryValuationResponse.from_orm(valuation))


@router.post("/valuations/{valuation_id}/finalize", response_model=dict)
async def finalize_valuation(
    valuation_id: uuid.UUID,
    service: InventoryValuationService = Depends(get_valuation_service)
):
    """Finalize valuation"""
    try:
        valuation = await service.finalize_valuation(valuation_id)
        return success_response(
            data=schemas.InventoryValuationResponse.from_orm(valuation),
            message="Valuation finalized"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/valuations/summary/{financial_year}", response_model=dict)
async def get_valuation_summary(
    financial_year: int,
    service: InventoryValuationService = Depends(get_valuation_service)
):
    """Get valuation summary for financial year"""
    summary = await service.get_valuation_summary(financial_year)
    return success_response(data=summary)


# ============================================================================
# DASHBOARD & REPORTS ENDPOINTS
# ============================================================================

@router.get("/dashboard/metrics", response_model=dict)
async def get_dashboard_metrics(
    service: ItemMasterService = Depends(get_item_service)
):
    """Get inventory dashboard metrics"""
    summary = await service.get_stock_summary()
    return success_response(data=summary)
