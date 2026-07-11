"""
Asset Transfer Service
Handles asset transfers and movements
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from backend.shared.database.asset_models import (
    AssetTransfer, FixedAsset,
    TransferStatus, AssetStatus
)
from backend.services.fixed_assets.schemas import (
    AssetTransferCreate, AssetTransferUpdate, AssetTransferApproval
)


class TransferService:
    """Service for asset transfer operations"""
    
    @staticmethod
    def generate_transfer_number(db: Session, tenant_id: int, prefix: str = "TRF") -> str:
        """Generate unique transfer number"""
        last_transfer = db.query(AssetTransfer).filter(
            AssetTransfer.tenant_id == tenant_id,
            AssetTransfer.transfer_number.like(f"{prefix}%")
        ).order_by(AssetTransfer.id.desc()).first()
        
        if last_transfer and last_transfer.transfer_number:
            try:
                last_num = int(last_transfer.transfer_number.replace(prefix, ""))
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:06d}"
    
    @staticmethod
    def create_transfer(
        db: Session,
        tenant_id: int,
        user_id: int,
        transfer_data: AssetTransferCreate
    ) -> AssetTransfer:
        """Create an asset transfer"""
        
        # Verify asset exists and is active
        asset = db.query(FixedAsset).filter(
            FixedAsset.id == transfer_data.asset_id,
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        if asset.asset_status not in [AssetStatus.ACTIVE, AssetStatus.IDLE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transfer asset with status {asset.asset_status.value}"
            )
        
        # Check for pending transfers
        pending_transfer = db.query(AssetTransfer).filter(
            AssetTransfer.tenant_id == tenant_id,
            AssetTransfer.asset_id == transfer_data.asset_id,
            AssetTransfer.status.in_([TransferStatus.INITIATED, TransferStatus.APPROVED, TransferStatus.IN_TRANSIT]),
            AssetTransfer.is_deleted == False
        ).first()
        
        if pending_transfer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Asset has a pending transfer"
            )
        
        # Generate transfer number
        transfer_number = TransferService.generate_transfer_number(db, tenant_id)
        
        # Calculate total cost
        total_cost = (
            transfer_data.transfer_cost +
            transfer_data.insurance_cost +
            transfer_data.other_charges
        )
        
        # Get current asset details as 'from' details if not provided
        from_location_id = transfer_data.from_location_id or asset.location_id
        from_location_name = transfer_data.from_location_name or asset.location_name
        from_department_id = transfer_data.from_department_id or asset.department_id
        from_department_name = transfer_data.from_department_name or asset.department_name
        from_custodian_id = transfer_data.from_custodian_id or asset.custodian_id
        from_custodian_name = transfer_data.from_custodian_name or asset.custodian_name
        
        # Create transfer record
        transfer = AssetTransfer(
            tenant_id=tenant_id,
            transfer_number=transfer_number,
            **transfer_data.model_dump(exclude={'document_urls', 'from_location_id', 'from_location_name',
                                                  'from_department_id', 'from_department_name',
                                                  'from_custodian_id', 'from_custodian_name'}),
            from_location_id=from_location_id,
            from_location_name=from_location_name,
            from_department_id=from_department_id,
            from_department_name=from_department_name,
            from_custodian_id=from_custodian_id,
            from_custodian_name=from_custodian_name,
            total_cost=total_cost,
            status=TransferStatus.INITIATED,
            initiated_by=user_id,
            created_by=user_id,
            updated_by=user_id
        )
        
        # Handle JSON fields
        if transfer_data.document_urls:
            import json
            transfer.document_urls = json.dumps(transfer_data.document_urls)
        
        db.add(transfer)
        
        # Update asset status
        asset.asset_status = AssetStatus.TRANSFERRED
        asset.status_change_date = transfer_data.transfer_date
        asset.updated_by = user_id
        asset.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transfer)
        
        return transfer
    
    @staticmethod
    def approve_transfer(
        db: Session,
        tenant_id: int,
        user_id: int,
        transfer_id: int,
        approval: AssetTransferApproval
    ) -> AssetTransfer:
        """Approve or reject a transfer"""
        
        transfer = db.query(AssetTransfer).filter(
            AssetTransfer.id == transfer_id,
            AssetTransfer.tenant_id == tenant_id,
            AssetTransfer.is_deleted == False
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status != TransferStatus.INITIATED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve transfer with status {transfer.status.value}"
            )
        
        if approval.approve:
            transfer.status = TransferStatus.APPROVED
            transfer.approved_by = user_id
            transfer.approved_at = datetime.utcnow()
            transfer.approval_notes = approval.notes
        else:
            transfer.status = TransferStatus.REJECTED
            transfer.rejected_by = user_id
            transfer.rejected_at = datetime.utcnow()
            transfer.rejection_reason = approval.notes
            
            # Restore asset status
            asset = transfer.asset
            asset.asset_status = AssetStatus.ACTIVE
            asset.updated_by = user_id
            asset.updated_at = datetime.utcnow()
        
        transfer.updated_by = user_id
        transfer.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transfer)
        
        return transfer
    
    @staticmethod
    def mark_in_transit(
        db: Session,
        tenant_id: int,
        user_id: int,
        transfer_id: int,
        handover_date: date
    ) -> AssetTransfer:
        """Mark transfer as in transit"""
        
        transfer = db.query(AssetTransfer).filter(
            AssetTransfer.id == transfer_id,
            AssetTransfer.tenant_id == tenant_id,
            AssetTransfer.is_deleted == False
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status != TransferStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only approved transfers can be marked as in transit"
            )
        
        transfer.status = TransferStatus.IN_TRANSIT
        transfer.handover_date = handover_date
        transfer.handover_by = user_id
        transfer.updated_by = user_id
        transfer.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transfer)
        
        return transfer
    
    @staticmethod
    def complete_transfer(
        db: Session,
        tenant_id: int,
        user_id: int,
        transfer_id: int,
        received_date: date,
        condition_at_receipt: Optional[str] = None,
        notes: Optional[str] = None
    ) -> AssetTransfer:
        """Complete a transfer"""
        
        transfer = db.query(AssetTransfer).filter(
            AssetTransfer.id == transfer_id,
            AssetTransfer.tenant_id == tenant_id,
            AssetTransfer.is_deleted == False
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status not in [TransferStatus.APPROVED, TransferStatus.IN_TRANSIT]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete transfer with status {transfer.status.value}"
            )
        
        transfer.status = TransferStatus.COMPLETED
        transfer.received_date = received_date
        transfer.actual_arrival_date = received_date
        transfer.received_by = user_id
        transfer.condition_at_receipt = condition_at_receipt
        if notes:
            transfer.notes = notes
        transfer.updated_by = user_id
        transfer.updated_at = datetime.utcnow()
        
        # Update asset location and custodian
        asset = transfer.asset
        asset.location_id = transfer.to_location_id
        asset.location_name = transfer.to_location_name
        asset.department_id = transfer.to_department_id
        asset.department_name = transfer.to_department_name
        asset.custodian_id = transfer.to_custodian_id
        asset.custodian_name = transfer.to_custodian_name
        asset.asset_status = AssetStatus.ACTIVE
        asset.updated_by = user_id
        asset.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transfer)
        
        return transfer
    
    @staticmethod
    def update_transfer(
        db: Session,
        tenant_id: int,
        user_id: int,
        transfer_id: int,
        transfer_data: AssetTransferUpdate
    ) -> AssetTransfer:
        """Update transfer details"""
        
        transfer = db.query(AssetTransfer).filter(
            AssetTransfer.id == transfer_id,
            AssetTransfer.tenant_id == tenant_id,
            AssetTransfer.is_deleted == False
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        # Update fields
        update_data = transfer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transfer, field, value)
        
        transfer.updated_by = user_id
        transfer.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transfer)
        
        return transfer
    
    @staticmethod
    def get_transfer(
        db: Session,
        tenant_id: int,
        transfer_id: int
    ) -> Optional[AssetTransfer]:
        """Get transfer by ID"""
        return db.query(AssetTransfer).filter(
            AssetTransfer.id == transfer_id,
            AssetTransfer.tenant_id == tenant_id,
            AssetTransfer.is_deleted == False
        ).first()
    
    @staticmethod
    def list_transfers(
        db: Session,
        tenant_id: int,
        asset_id: Optional[int] = None,
        status: Optional[TransferStatus] = None,
        from_location_id: Optional[int] = None,
        to_location_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple:
        """List transfers with filters"""
        
        query = db.query(AssetTransfer).filter(
            AssetTransfer.tenant_id == tenant_id,
            AssetTransfer.is_deleted == False
        )
        
        if asset_id:
            query = query.filter(AssetTransfer.asset_id == asset_id)
        
        if status:
            query = query.filter(AssetTransfer.status == status)
        
        if from_location_id:
            query = query.filter(AssetTransfer.from_location_id == from_location_id)
        
        if to_location_id:
            query = query.filter(AssetTransfer.to_location_id == to_location_id)
        
        if from_date:
            query = query.filter(AssetTransfer.transfer_date >= from_date)
        
        if to_date:
            query = query.filter(AssetTransfer.transfer_date <= to_date)
        
        total = query.count()
        
        query = query.order_by(AssetTransfer.transfer_date.desc())
        
        offset = (page - 1) * page_size
        transfers = query.offset(offset).limit(page_size).all()
        
        return transfers, total
    
    @staticmethod
    def cancel_transfer(
        db: Session,
        tenant_id: int,
        user_id: int,
        transfer_id: int,
        reason: str
    ) -> AssetTransfer:
        """Cancel a transfer"""
        
        transfer = db.query(AssetTransfer).filter(
            AssetTransfer.id == transfer_id,
            AssetTransfer.tenant_id == tenant_id,
            AssetTransfer.is_deleted == False
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status in [TransferStatus.COMPLETED, TransferStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel transfer with status {transfer.status.value}"
            )
        
        transfer.status = TransferStatus.CANCELLED
        transfer.status_notes = reason
        transfer.updated_by = user_id
        transfer.updated_at = datetime.utcnow()
        
        # Restore asset status
        asset = transfer.asset
        asset.asset_status = AssetStatus.ACTIVE
        asset.updated_by = user_id
        asset.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transfer)
        
        return transfer
