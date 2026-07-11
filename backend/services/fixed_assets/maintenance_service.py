"""
Asset Maintenance Service
Handles maintenance tracking and scheduling
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status

from backend.shared.database.asset_models import (
    AssetMaintenance, FixedAsset,
    MaintenanceType, MaintenanceStatus, AssetStatus
)
from backend.services.fixed_assets.schemas import (
    AssetMaintenanceCreate, AssetMaintenanceUpdate
)


class MaintenanceService:
    """Service for asset maintenance operations"""
    
    @staticmethod
    def generate_maintenance_number(db: Session, tenant_id: int, prefix: str = "MNT") -> str:
        """Generate unique maintenance number"""
        last_maintenance = db.query(AssetMaintenance).filter(
            AssetMaintenance.tenant_id == tenant_id,
            AssetMaintenance.maintenance_number.like(f"{prefix}%")
        ).order_by(AssetMaintenance.id.desc()).first()
        
        if last_maintenance and last_maintenance.maintenance_number:
            try:
                last_num = int(last_maintenance.maintenance_number.replace(prefix, ""))
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:06d}"
    
    @staticmethod
    def create_maintenance(
        db: Session,
        tenant_id: int,
        user_id: int,
        maintenance_data: AssetMaintenanceCreate
    ) -> AssetMaintenance:
        """Create a maintenance record"""
        
        # Verify asset exists
        asset = db.query(FixedAsset).filter(
            FixedAsset.id == maintenance_data.asset_id,
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        # Generate maintenance number
        maintenance_number = MaintenanceService.generate_maintenance_number(db, tenant_id)
        
        # Calculate total cost
        total_cost = (
            maintenance_data.labor_cost +
            maintenance_data.parts_cost +
            maintenance_data.other_charges
        )
        
        # Create maintenance record
        maintenance = AssetMaintenance(
            tenant_id=tenant_id,
            maintenance_number=maintenance_number,
            **maintenance_data.model_dump(exclude={'document_urls'}),
            total_cost=total_cost,
            requested_by=user_id,
            created_by=user_id,
            updated_by=user_id
        )
        
        # Handle JSON fields
        if maintenance_data.document_urls:
            import json
            maintenance.document_urls = json.dumps(maintenance_data.document_urls)
        
        db.add(maintenance)
        
        # Update asset status if needed
        if maintenance_data.maintenance_type in [MaintenanceType.BREAKDOWN, MaintenanceType.CORRECTIVE]:
            asset.asset_status = AssetStatus.UNDER_REPAIR
            asset.updated_by = user_id
            asset.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(maintenance)
        
        return maintenance
    
    @staticmethod
    def update_maintenance(
        db: Session,
        tenant_id: int,
        user_id: int,
        maintenance_id: int,
        maintenance_data: AssetMaintenanceUpdate
    ) -> AssetMaintenance:
        """Update maintenance record"""
        
        maintenance = db.query(AssetMaintenance).filter(
            AssetMaintenance.id == maintenance_id,
            AssetMaintenance.tenant_id == tenant_id,
            AssetMaintenance.is_deleted == False
        ).first()
        
        if not maintenance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maintenance record not found"
            )
        
        # Update fields
        update_data = maintenance_data.model_dump(exclude_unset=True, exclude={'document_urls'})
        for field, value in update_data.items():
            setattr(maintenance, field, value)
        
        # Recalculate total cost if any cost field changed
        if any(k in update_data for k in ['labor_cost', 'parts_cost', 'other_charges']):
            maintenance.total_cost = (
                maintenance.labor_cost +
                maintenance.parts_cost +
                maintenance.other_charges
            )
        
        # Calculate downtime cost if downtime hours provided
        if maintenance_data.downtime_hours is not None and maintenance_data.downtime_hours > 0:
            # You can set a standard hourly downtime cost or calculate based on asset value
            hourly_cost = Decimal('100.00')  # Example rate
            maintenance.downtime_cost = maintenance_data.downtime_hours * hourly_cost
        
        # Handle JSON fields
        if maintenance_data.document_urls is not None:
            import json
            maintenance.document_urls = json.dumps(maintenance_data.document_urls)
        
        maintenance.updated_by = user_id
        maintenance.updated_at = datetime.utcnow()
        
        # Update asset status based on maintenance status
        if maintenance_data.status == MaintenanceStatus.COMPLETED:
            asset = maintenance.asset
            if asset.asset_status in [AssetStatus.UNDER_REPAIR, AssetStatus.IN_MAINTENANCE]:
                asset.asset_status = AssetStatus.ACTIVE
                asset.updated_by = user_id
                asset.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(maintenance)
        
        return maintenance
    
    @staticmethod
    def approve_maintenance(
        db: Session,
        tenant_id: int,
        user_id: int,
        maintenance_id: int,
        approval_notes: Optional[str] = None
    ) -> AssetMaintenance:
        """Approve a maintenance request"""
        
        maintenance = db.query(AssetMaintenance).filter(
            AssetMaintenance.id == maintenance_id,
            AssetMaintenance.tenant_id == tenant_id,
            AssetMaintenance.is_deleted == False
        ).first()
        
        if not maintenance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maintenance record not found"
            )
        
        if maintenance.status != MaintenanceStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending maintenance can be approved"
            )
        
        maintenance.status = MaintenanceStatus.SCHEDULED
        maintenance.approved_by = user_id
        maintenance.approved_at = datetime.utcnow()
        maintenance.approval_notes = approval_notes
        maintenance.updated_by = user_id
        maintenance.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(maintenance)
        
        return maintenance
    
    @staticmethod
    def get_maintenance(
        db: Session,
        tenant_id: int,
        maintenance_id: int
    ) -> Optional[AssetMaintenance]:
        """Get maintenance record by ID"""
        return db.query(AssetMaintenance).filter(
            AssetMaintenance.id == maintenance_id,
            AssetMaintenance.tenant_id == tenant_id,
            AssetMaintenance.is_deleted == False
        ).first()
    
    @staticmethod
    def list_maintenance(
        db: Session,
        tenant_id: int,
        asset_id: Optional[int] = None,
        status: Optional[MaintenanceStatus] = None,
        maintenance_type: Optional[MaintenanceType] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple:
        """List maintenance records with filters"""
        
        query = db.query(AssetMaintenance).filter(
            AssetMaintenance.tenant_id == tenant_id,
            AssetMaintenance.is_deleted == False
        )
        
        if asset_id:
            query = query.filter(AssetMaintenance.asset_id == asset_id)
        
        if status:
            query = query.filter(AssetMaintenance.status == status)
        
        if maintenance_type:
            query = query.filter(AssetMaintenance.maintenance_type == maintenance_type)
        
        if from_date:
            query = query.filter(AssetMaintenance.scheduled_date >= from_date)
        
        if to_date:
            query = query.filter(AssetMaintenance.scheduled_date <= to_date)
        
        total = query.count()
        
        query = query.order_by(AssetMaintenance.scheduled_date.desc())
        
        offset = (page - 1) * page_size
        maintenance_records = query.offset(offset).limit(page_size).all()
        
        return maintenance_records, total
    
    @staticmethod
    def get_upcoming_maintenance(
        db: Session,
        tenant_id: int,
        days_ahead: int = 30
    ) -> List[AssetMaintenance]:
        """Get upcoming scheduled maintenance"""
        
        from_date = date.today()
        to_date = from_date + datetime.timedelta(days=days_ahead)
        
        return db.query(AssetMaintenance).filter(
            AssetMaintenance.tenant_id == tenant_id,
            AssetMaintenance.is_deleted == False,
            AssetMaintenance.status.in_([MaintenanceStatus.SCHEDULED, MaintenanceStatus.PENDING]),
            AssetMaintenance.scheduled_date >= from_date,
            AssetMaintenance.scheduled_date <= to_date
        ).order_by(AssetMaintenance.scheduled_date.asc()).all()
    
    @staticmethod
    def get_maintenance_report(
        db: Session,
        tenant_id: int,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """Generate maintenance report"""
        
        query = db.query(AssetMaintenance).filter(
            AssetMaintenance.tenant_id == tenant_id,
            AssetMaintenance.is_deleted == False,
            AssetMaintenance.scheduled_date >= from_date,
            AssetMaintenance.scheduled_date <= to_date
        )
        
        maintenance_records = query.all()
        
        total_cost = sum(m.total_cost for m in maintenance_records)
        total_downtime = sum(m.downtime_hours or Decimal('0.00') for m in maintenance_records)
        
        # Group by type
        by_type = {}
        for m in maintenance_records:
            mtype = m.maintenance_type.value
            if mtype not in by_type:
                by_type[mtype] = {"type": mtype, "count": 0, "total_cost": Decimal('0.00')}
            by_type[mtype]["count"] += 1
            by_type[mtype]["total_cost"] += m.total_cost
        
        # Group by status
        by_status = {}
        for m in maintenance_records:
            status = m.status.value
            if status not in by_status:
                by_status[status] = {"status": status, "count": 0}
            by_status[status]["count"] += 1
        
        # Top maintained assets
        asset_maintenance = {}
        for m in maintenance_records:
            aid = m.asset_id
            if aid not in asset_maintenance:
                asset_maintenance[aid] = {
                    "asset_id": aid,
                    "asset_code": m.asset.asset_code,
                    "asset_name": m.asset.asset_name,
                    "count": 0,
                    "total_cost": Decimal('0.00')
                }
            asset_maintenance[aid]["count"] += 1
            asset_maintenance[aid]["total_cost"] += m.total_cost
        
        top_assets = sorted(
            asset_maintenance.values(),
            key=lambda x: x["count"],
            reverse=True
        )[:10]
        
        return {
            "period_start": from_date,
            "period_end": to_date,
            "total_maintenance_cost": float(total_cost),
            "total_maintenance_requests": len(maintenance_records),
            "total_downtime_hours": float(total_downtime),
            "maintenance_by_type": [
                {
                    "type": v["type"],
                    "count": v["count"],
                    "total_cost": float(v["total_cost"])
                }
                for v in by_type.values()
            ],
            "maintenance_by_status": list(by_status.values()),
            "top_maintained_assets": [
                {
                    "asset_id": a["asset_id"],
                    "asset_code": a["asset_code"],
                    "asset_name": a["asset_name"],
                    "maintenance_count": a["count"],
                    "total_cost": float(a["total_cost"])
                }
                for a in top_assets
            ]
        }
