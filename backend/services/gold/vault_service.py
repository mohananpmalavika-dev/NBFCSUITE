"""
Vault Management Service
Manages vault locations, inventory, and transfers
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
import json
from fastapi import HTTPException

from backend.shared.database.gold_loan_models import (
    VaultLocation,
    VaultInventory,
    VaultTransfer,
    GoldLoanAccount,
    GoldOrnament
)
from backend.services.gold.schemas import (
    VaultLocationCreateRequest,
    VaultLocationUpdateRequest,
    VaultInventoryCreateRequest,
    VaultTransferCreateRequest,
    VaultLocationResponse,
    VaultInventoryResponse,
    VaultTransferResponse
)


class VaultService:
    """Service for vault management"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== Vault Location Management ====================
    
    def create_vault_location(self, vault_data: VaultLocationCreateRequest) -> VaultLocation:
        """Create a new vault location"""
        # Check for duplicate vault code
        existing = self.db.query(VaultLocation).filter(
            and_(
                VaultLocation.tenant_id == self.tenant_id,
                VaultLocation.vault_code == vault_data.vault_code
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Vault code {vault_data.vault_code} already exists"
            )
        
        vault = VaultLocation(
            tenant_id=self.tenant_id,
            vault_code=vault_data.vault_code,
            vault_name=vault_data.vault_name,
            branch_id=vault_data.branch_id,
            location_type=vault_data.location_type,
            building=vault_data.building,
            floor=vault_data.floor,
            room=vault_data.room,
            rack_number=vault_data.rack_number,
            shelf_number=vault_data.shelf_number,
            max_capacity_items=vault_data.max_capacity_items,
            max_capacity_weight_kg=vault_data.max_capacity_weight_kg,
            security_level=vault_data.security_level or "High",
            access_control=vault_data.access_control,
            surveillance=vault_data.surveillance,
            insured=vault_data.insured,
            insurance_value=vault_data.insurance_value,
            status="Active",
            custodian_name=vault_data.custodian_name,
            custodian_contact=vault_data.custodian_contact,
            remarks=vault_data.remarks
        )
        
        self.db.add(vault)
        self.db.commit()
        self.db.refresh(vault)
        
        return vault
    
    def update_vault_location(
        self,
        vault_id: str,
        vault_data: VaultLocationUpdateRequest
    ) -> VaultLocation:
        """Update vault location details"""
        vault = self.db.query(VaultLocation).filter(
            and_(
                VaultLocation.id == vault_id,
                VaultLocation.tenant_id == self.tenant_id
            )
        ).first()
        
        if not vault:
            raise HTTPException(status_code=404, detail="Vault location not found")
        
        # Update fields
        if vault_data.vault_name is not None:
            vault.vault_name = vault_data.vault_name
        if vault_data.location_type is not None:
            vault.location_type = vault_data.location_type
        if vault_data.max_capacity_items is not None:
            vault.max_capacity_items = vault_data.max_capacity_items
        if vault_data.max_capacity_weight_kg is not None:
            vault.max_capacity_weight_kg = vault_data.max_capacity_weight_kg
        if vault_data.status is not None:
            vault.status = vault_data.status
        if vault_data.custodian_name is not None:
            vault.custodian_name = vault_data.custodian_name
        if vault_data.custodian_contact is not None:
            vault.custodian_contact = vault_data.custodian_contact
        if vault_data.remarks is not None:
            vault.remarks = vault_data.remarks
        
        self.db.add(vault)
        self.db.commit()
        self.db.refresh(vault)
        
        return vault
    
    def get_vault_location(self, vault_id: str) -> Optional[VaultLocation]:
        """Get vault location by ID"""
        return self.db.query(VaultLocation).filter(
            and_(
                VaultLocation.id == vault_id,
                VaultLocation.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_vault_locations(
        self,
        branch_id: Optional[str] = None,
        status: Optional[str] = None,
        location_type: Optional[str] = None
    ) -> List[VaultLocation]:
        """List vault locations with filters"""
        query = self.db.query(VaultLocation).filter(
            VaultLocation.tenant_id == self.tenant_id
        )
        
        if branch_id:
            query = query.filter(VaultLocation.branch_id == branch_id)
        if status:
            query = query.filter(VaultLocation.status == status)
        if location_type:
            query = query.filter(VaultLocation.location_type == location_type)
        
        return query.order_by(VaultLocation.vault_code).all()
    
    def get_vault_capacity_status(self, vault_id: str) -> Dict[str, Any]:
        """Get vault capacity utilization status"""
        vault = self.get_vault_location(vault_id)
        if not vault:
            raise HTTPException(status_code=404, detail="Vault location not found")
        
        # Calculate utilization percentages
        items_utilization = 0
        weight_utilization = 0
        
        if vault.max_capacity_items:
            items_utilization = (vault.current_items_count / vault.max_capacity_items) * 100
        
        if vault.max_capacity_weight_kg:
            weight_utilization = (float(vault.current_weight_kg) / float(vault.max_capacity_weight_kg)) * 100
        
        return {
            "vault_id": vault.id,
            "vault_code": vault.vault_code,
            "vault_name": vault.vault_name,
            "current_items": vault.current_items_count,
            "max_items": vault.max_capacity_items,
            "items_utilization_percentage": round(items_utilization, 2),
            "current_weight_kg": float(vault.current_weight_kg),
            "max_weight_kg": float(vault.max_capacity_weight_kg) if vault.max_capacity_weight_kg else None,
            "weight_utilization_percentage": round(weight_utilization, 2),
            "status": vault.status,
            "is_full": items_utilization >= 100 or weight_utilization >= 100
        }
    
    # ==================== Vault Inventory Management ====================
    
    def check_in_ornament(
        self,
        inventory_data: VaultInventoryCreateRequest
    ) -> VaultInventory:
        """Check in gold ornament to vault"""
        # Validate vault location
        vault = self.get_vault_location(inventory_data.vault_location_id)
        if not vault:
            raise HTTPException(status_code=404, detail="Vault location not found")
        
        if vault.status != "Active":
            raise HTTPException(
                status_code=400,
                detail=f"Vault is not active (current status: {vault.status})"
            )
        
        # Check capacity
        if vault.max_capacity_items and vault.current_items_count >= vault.max_capacity_items:
            raise HTTPException(status_code=400, detail="Vault capacity exceeded")
        
        # Get ornament details
        ornament = self.db.query(GoldOrnament).filter(
            and_(
                GoldOrnament.id == inventory_data.ornament_id,
                GoldOrnament.tenant_id == self.tenant_id
            )
        ).first()
        
        if not ornament:
            raise HTTPException(status_code=404, detail="Ornament not found")
        
        # Generate inventory number
        inventory_number = self._generate_inventory_number(vault.vault_code)
        
        # Create inventory record
        inventory = VaultInventory(
            tenant_id=self.tenant_id,
            inventory_number=inventory_number,
            vault_location_id=inventory_data.vault_location_id,
            gold_loan_id=inventory_data.gold_loan_id,
            customer_id=inventory_data.customer_id,
            ornament_id=inventory_data.ornament_id,
            package_number=inventory_data.package_number,
            seal_number=inventory_data.seal_number,
            barcode=inventory_data.barcode,
            rfid_tag=inventory_data.rfid_tag,
            rack_position=inventory_data.rack_position,
            shelf_position=inventory_data.shelf_position,
            slot_position=inventory_data.slot_position,
            item_description=f"{ornament.ornament_type} - {ornament.ornament_description or ''}",
            total_weight_grams=ornament.net_weight_grams,
            total_value=ornament.appraised_value,
            check_in_date=datetime.utcnow(),
            check_in_by=self.user_id,
            check_in_verified_by=inventory_data.verified_by,
            check_in_photo_url=inventory_data.photo_url,
            status="In Vault",
            remarks=inventory_data.remarks
        )
        
        self.db.add(inventory)
        
        # Update vault capacity
        vault.current_items_count += 1
        vault.current_weight_kg += (ornament.net_weight_grams / 1000)
        self.db.add(vault)
        
        self.db.commit()
        self.db.refresh(inventory)
        
        return inventory
    
    def check_out_ornament(
        self,
        inventory_id: str,
        verified_by: Optional[str] = None,
        photo_url: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> VaultInventory:
        """Check out gold ornament from vault"""
        inventory = self.db.query(VaultInventory).filter(
            and_(
                VaultInventory.id == inventory_id,
                VaultInventory.tenant_id == self.tenant_id
            )
        ).first()
        
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        if inventory.status != "In Vault":
            raise HTTPException(
                status_code=400,
                detail=f"Item is not in vault (current status: {inventory.status})"
            )
        
        # Update check-out details
        inventory.check_out_date = datetime.utcnow()
        inventory.check_out_by = self.user_id
        inventory.check_out_verified_by = verified_by
        inventory.check_out_photo_url = photo_url
        inventory.status = "Released"
        if remarks:
            inventory.remarks = f"{inventory.remarks or ''}\nCheck-out: {remarks}"
        
        self.db.add(inventory)
        
        # Update vault capacity
        vault = self.get_vault_location(inventory.vault_location_id)
        if vault:
            vault.current_items_count = max(0, vault.current_items_count - 1)
            vault.current_weight_kg = max(Decimal('0.000'), 
                                         vault.current_weight_kg - (inventory.total_weight_grams / 1000))
            self.db.add(vault)
        
        self.db.commit()
        self.db.refresh(inventory)
        
        return inventory
    
    def get_inventory_item(self, inventory_id: str) -> Optional[VaultInventory]:
        """Get inventory item by ID"""
        return self.db.query(VaultInventory).filter(
            and_(
                VaultInventory.id == inventory_id,
                VaultInventory.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_vault_inventory(
        self,
        vault_id: Optional[str] = None,
        loan_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[VaultInventory]:
        """List vault inventory with filters"""
        query = self.db.query(VaultInventory).filter(
            VaultInventory.tenant_id == self.tenant_id
        )
        
        if vault_id:
            query = query.filter(VaultInventory.vault_location_id == vault_id)
        if loan_id:
            query = query.filter(VaultInventory.gold_loan_id == loan_id)
        if customer_id:
            query = query.filter(VaultInventory.customer_id == customer_id)
        if status:
            query = query.filter(VaultInventory.status == status)
        
        return query.order_by(desc(VaultInventory.check_in_date)).all()
    
    def search_inventory_by_barcode(self, barcode: str) -> Optional[VaultInventory]:
        """Search inventory by barcode"""
        return self.db.query(VaultInventory).filter(
            and_(
                VaultInventory.tenant_id == self.tenant_id,
                VaultInventory.barcode == barcode
            )
        ).first()
    
    def perform_vault_audit(
        self,
        vault_id: str,
        audit_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform vault audit and record results
        audit_results: List of {inventory_id, audit_status, remarks}
        """
        vault = self.get_vault_location(vault_id)
        if not vault:
            raise HTTPException(status_code=404, detail="Vault location not found")
        
        audit_summary = {
            "vault_id": vault_id,
            "audit_date": datetime.utcnow(),
            "audited_by": self.user_id,
            "total_items": 0,
            "items_ok": 0,
            "items_discrepancy": 0,
            "items_missing": 0,
            "details": []
        }
        
        for result in audit_results:
            inventory = self.get_inventory_item(result["inventory_id"])
            if inventory:
                inventory.last_audit_date = datetime.utcnow()
                inventory.last_audit_by = self.user_id
                inventory.audit_status = result.get("audit_status", "OK")
                
                if result.get("remarks"):
                    inventory.remarks = f"{inventory.remarks or ''}\nAudit: {result['remarks']}"
                
                self.db.add(inventory)
                
                audit_summary["total_items"] += 1
                if inventory.audit_status == "OK":
                    audit_summary["items_ok"] += 1
                elif inventory.audit_status == "Discrepancy":
                    audit_summary["items_discrepancy"] += 1
                elif inventory.audit_status == "Missing":
                    audit_summary["items_missing"] += 1
                    inventory.status = "Missing"
                
                audit_summary["details"].append({
                    "inventory_number": inventory.inventory_number,
                    "status": inventory.audit_status,
                    "remarks": result.get("remarks")
                })
        
        self.db.commit()
        
        return audit_summary
    
    # ==================== Vault Transfer Management ====================
    
    def create_transfer(
        self,
        transfer_data: VaultTransferCreateRequest
    ) -> VaultTransfer:
        """Create vault transfer request"""
        # Validate vaults
        from_vault = self.get_vault_location(transfer_data.from_vault_id)
        to_vault = self.get_vault_location(transfer_data.to_vault_id)
        
        if not from_vault:
            raise HTTPException(status_code=404, detail="Source vault not found")
        if not to_vault:
            raise HTTPException(status_code=404, detail="Destination vault not found")
        
        if from_vault.id == to_vault.id:
            raise HTTPException(
                status_code=400,
                detail="Source and destination vaults cannot be the same"
            )
        
        # Validate inventory items
        inventory_ids = transfer_data.inventory_ids
        total_weight = Decimal('0.000')
        total_value = Decimal('0.00')
        
        for inv_id in inventory_ids:
            inventory = self.get_inventory_item(inv_id)
            if not inventory:
                raise HTTPException(
                    status_code=404,
                    detail=f"Inventory item {inv_id} not found"
                )
            if inventory.vault_location_id != from_vault.id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Inventory item {inv_id} is not in source vault"
                )
            if inventory.status != "In Vault":
                raise HTTPException(
                    status_code=400,
                    detail=f"Inventory item {inv_id} is not available for transfer"
                )
            
            total_weight += inventory.total_weight_grams
            total_value += inventory.total_value
        
        # Generate transfer number
        transfer_number = self._generate_transfer_number()
        
        # Create transfer record
        transfer = VaultTransfer(
            tenant_id=self.tenant_id,
            transfer_number=transfer_number,
            transfer_date=transfer_data.transfer_date or datetime.utcnow(),
            from_vault_id=transfer_data.from_vault_id,
            to_vault_id=transfer_data.to_vault_id,
            inventory_ids=json.dumps(inventory_ids),
            total_items_count=len(inventory_ids),
            total_weight_grams=total_weight,
            total_value=total_value,
            initiated_by=self.user_id,
            seal_number=transfer_data.seal_number,
            transport_mode=transfer_data.transport_mode,
            status="Pending",
            remarks=transfer_data.remarks
        )
        
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        
        return transfer
    
    def approve_transfer(
        self,
        transfer_id: str,
        approved_by: str
    ) -> VaultTransfer:
        """Approve transfer request"""
        transfer = self._get_transfer(transfer_id)
        
        if transfer.status != "Pending":
            raise HTTPException(
                status_code=400,
                detail=f"Transfer cannot be approved (current status: {transfer.status})"
            )
        
        transfer.approved_by = approved_by
        transfer.status = "Approved"
        
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        
        return transfer
    
    def dispatch_transfer(
        self,
        transfer_id: str,
        dispatch_reference: Optional[str] = None
    ) -> VaultTransfer:
        """Dispatch transfer"""
        transfer = self._get_transfer(transfer_id)
        
        if transfer.status not in ["Approved", "Pending"]:
            raise HTTPException(
                status_code=400,
                detail=f"Transfer cannot be dispatched (current status: {transfer.status})"
            )
        
        transfer.dispatched_date = datetime.utcnow()
        transfer.dispatched_by = self.user_id
        transfer.dispatch_reference = dispatch_reference
        transfer.status = "In Transit"
        
        # Update inventory items status
        inventory_ids = json.loads(transfer.inventory_ids)
        for inv_id in inventory_ids:
            inventory = self.get_inventory_item(inv_id)
            if inventory:
                inventory.status = "Transferred"
                self.db.add(inventory)
        
        # Update source vault capacity
        from_vault = self.get_vault_location(transfer.from_vault_id)
        if from_vault:
            from_vault.current_items_count -= transfer.total_items_count
            from_vault.current_weight_kg -= (transfer.total_weight_grams / 1000)
            self.db.add(from_vault)
        
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        
        return transfer
    
    def receive_transfer(
        self,
        transfer_id: str,
        receipt_reference: Optional[str] = None,
        verification_status: str = "OK"
    ) -> VaultTransfer:
        """Receive and complete transfer"""
        transfer = self._get_transfer(transfer_id)
        
        if transfer.status != "In Transit":
            raise HTTPException(
                status_code=400,
                detail=f"Transfer cannot be received (current status: {transfer.status})"
            )
        
        transfer.received_date = datetime.utcnow()
        transfer.received_by = self.user_id
        transfer.receipt_reference = receipt_reference
        transfer.verified_by = self.user_id
        transfer.verification_date = datetime.utcnow()
        transfer.verification_status = verification_status
        transfer.status = "Completed" if verification_status == "OK" else "Received"
        
        # Update inventory items vault location
        inventory_ids = json.loads(transfer.inventory_ids)
        for inv_id in inventory_ids:
            inventory = self.get_inventory_item(inv_id)
            if inventory:
                inventory.vault_location_id = transfer.to_vault_id
                inventory.status = "In Vault"
                self.db.add(inventory)
        
        # Update destination vault capacity
        to_vault = self.get_vault_location(transfer.to_vault_id)
        if to_vault:
            to_vault.current_items_count += transfer.total_items_count
            to_vault.current_weight_kg += (transfer.total_weight_grams / 1000)
            self.db.add(to_vault)
        
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        
        return transfer
    
    def list_transfers(
        self,
        vault_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[VaultTransfer]:
        """List vault transfers"""
        query = self.db.query(VaultTransfer).filter(
            VaultTransfer.tenant_id == self.tenant_id
        )
        
        if vault_id:
            query = query.filter(
                or_(
                    VaultTransfer.from_vault_id == vault_id,
                    VaultTransfer.to_vault_id == vault_id
                )
            )
        if status:
            query = query.filter(VaultTransfer.status == status)
        
        return query.order_by(desc(VaultTransfer.transfer_date)).all()
    
    # ==================== Helper Methods ====================
    
    def _get_transfer(self, transfer_id: str) -> VaultTransfer:
        """Get transfer by ID with error handling"""
        transfer = self.db.query(VaultTransfer).filter(
            and_(
                VaultTransfer.id == transfer_id,
                VaultTransfer.tenant_id == self.tenant_id
            )
        ).first()
        
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found")
        
        return transfer
    
    def _generate_inventory_number(self, vault_code: str) -> str:
        """Generate unique inventory number"""
        count = self.db.query(func.count(VaultInventory.id)).filter(
            VaultInventory.tenant_id == self.tenant_id
        ).scalar()
        
        return f"INV-{vault_code}-{datetime.utcnow().strftime('%Y%m%d')}-{count + 1:05d}"
    
    def _generate_transfer_number(self) -> str:
        """Generate unique transfer number"""
        count = self.db.query(func.count(VaultTransfer.id)).filter(
            VaultTransfer.tenant_id == self.tenant_id
        ).scalar()
        
        return f"TRF-{datetime.utcnow().strftime('%Y%m%d')}-{count + 1:05d}"
