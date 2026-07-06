"""
Vault Management Router
API endpoints for vault management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.gold.vault_service import VaultService
from backend.services.gold.schemas import (
    VaultLocationCreateRequest,
    VaultLocationUpdateRequest,
    VaultLocationResponse,
    VaultInventoryCreateRequest,
    VaultInventoryResponse,
    VaultTransferCreateRequest,
    VaultTransferResponse
)

router = APIRouter(prefix="/vaults", tags=["Vault Management"])


# ==================== Vault Location Endpoints ====================

@router.post("/locations", response_model=VaultLocationResponse)
async def create_vault_location(
    vault_data: VaultLocationCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Create new vault location"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    vault = service.create_vault_location(vault_data)
    return VaultLocationResponse.from_orm(vault)


@router.put("/locations/{vault_id}", response_model=VaultLocationResponse)
async def update_vault_location(
    vault_id: str,
    vault_data: VaultLocationUpdateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Update vault location"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    vault = service.update_vault_location(vault_id, vault_data)
    return VaultLocationResponse.from_orm(vault)


@router.get("/locations/{vault_id}", response_model=VaultLocationResponse)
async def get_vault_location(
    vault_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get vault location by ID"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    vault = service.get_vault_location(vault_id)
    
    if not vault:
        raise HTTPException(status_code=404, detail="Vault location not found")
    
    return VaultLocationResponse.from_orm(vault)


@router.get("/locations", response_model=List[VaultLocationResponse])
async def list_vault_locations(
    branch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    location_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List vault locations with filters"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    vaults = service.list_vault_locations(branch_id, status, location_type)
    return [VaultLocationResponse.from_orm(vault) for vault in vaults]


@router.get("/locations/{vault_id}/capacity")
async def get_vault_capacity_status(
    vault_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get vault capacity utilization status"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    return service.get_vault_capacity_status(vault_id)


# ==================== Vault Inventory Endpoints ====================

@router.post("/inventory/check-in", response_model=VaultInventoryResponse)
async def check_in_ornament(
    inventory_data: VaultInventoryCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Check in gold ornament to vault"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    inventory = service.check_in_ornament(inventory_data)
    return VaultInventoryResponse.from_orm(inventory)


@router.post("/inventory/{inventory_id}/check-out", response_model=VaultInventoryResponse)
async def check_out_ornament(
    inventory_id: str,
    verified_by: Optional[str] = Query(None),
    photo_url: Optional[str] = Query(None),
    remarks: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Check out gold ornament from vault"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    inventory = service.check_out_ornament(inventory_id, verified_by, photo_url, remarks)
    return VaultInventoryResponse.from_orm(inventory)


@router.get("/inventory/{inventory_id}", response_model=VaultInventoryResponse)
async def get_inventory_item(
    inventory_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get inventory item by ID"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    inventory = service.get_inventory_item(inventory_id)
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    return VaultInventoryResponse.from_orm(inventory)


@router.get("/inventory", response_model=List[VaultInventoryResponse])
async def list_vault_inventory(
    vault_id: Optional[str] = Query(None),
    loan_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List vault inventory with filters"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    inventory = service.list_vault_inventory(vault_id, loan_id, customer_id, status)
    return [VaultInventoryResponse.from_orm(item) for item in inventory]


@router.get("/inventory/search/barcode/{barcode}", response_model=VaultInventoryResponse)
async def search_inventory_by_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Search inventory by barcode"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    inventory = service.search_inventory_by_barcode(barcode)
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    return VaultInventoryResponse.from_orm(inventory)


@router.post("/inventory/audit/{vault_id}")
async def perform_vault_audit(
    vault_id: str,
    audit_results: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform vault audit
    audit_results: [{"inventory_id": "...", "audit_status": "OK/Discrepancy/Missing", "remarks": "..."}]
    """
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    return service.perform_vault_audit(vault_id, audit_results)


# ==================== Vault Transfer Endpoints ====================

@router.post("/transfers", response_model=VaultTransferResponse)
async def create_vault_transfer(
    transfer_data: VaultTransferCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Create vault transfer request"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    transfer = service.create_transfer(transfer_data)
    return VaultTransferResponse.from_orm(transfer)


@router.post("/transfers/{transfer_id}/approve", response_model=VaultTransferResponse)
async def approve_vault_transfer(
    transfer_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Approve vault transfer"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    transfer = service.approve_transfer(transfer_id, current_user.get("user_id"))
    return VaultTransferResponse.from_orm(transfer)


@router.post("/transfers/{transfer_id}/dispatch", response_model=VaultTransferResponse)
async def dispatch_vault_transfer(
    transfer_id: str,
    dispatch_reference: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Dispatch vault transfer"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    transfer = service.dispatch_transfer(transfer_id, dispatch_reference)
    return VaultTransferResponse.from_orm(transfer)


@router.post("/transfers/{transfer_id}/receive", response_model=VaultTransferResponse)
async def receive_vault_transfer(
    transfer_id: str,
    receipt_reference: Optional[str] = Query(None),
    verification_status: str = Query(default="OK"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Receive and complete vault transfer"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    transfer = service.receive_transfer(transfer_id, receipt_reference, verification_status)
    return VaultTransferResponse.from_orm(transfer)


@router.get("/transfers", response_model=List[VaultTransferResponse])
async def list_vault_transfers(
    vault_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List vault transfers"""
    service = VaultService(db, tenant_id, current_user.get("user_id"))
    transfers = service.list_transfers(vault_id, status)
    return [VaultTransferResponse.from_orm(transfer) for transfer in transfers]
