"""
Fixed Asset Service
Business logic for asset management operations
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from fastapi import HTTPException, status

from backend.shared.database.asset_models import (
    FixedAsset, AssetDepreciation, AssetMaintenance, AssetTransfer,
    AssetVerification, AssetVerificationCycle,
    AssetCategory, AssetStatus, DepreciationMethod, MaintenanceStatus,
    TransferStatus, DisposalMethod, VerificationStatus
)
from backend.services.fixed_assets.schemas import (
    FixedAssetCreate, FixedAssetUpdate, FixedAssetResponse,
    AssetDisposalRequest, AssetFilterParams
)


class AssetService:
    """Service for fixed asset operations"""
    
    @staticmethod
    def generate_asset_code(db: Session, tenant_id: int, prefix: str = "AST") -> str:
        """Generate unique asset code"""
        last_asset = db.query(FixedAsset).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.asset_code.like(f"{prefix}%")
        ).order_by(FixedAsset.id.desc()).first()
        
        if last_asset and last_asset.asset_code:
            try:
                last_num = int(last_asset.asset_code.replace(prefix, ""))
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:06d}"
    
    @staticmethod
    def create_asset(
        db: Session,
        tenant_id: int,
        user_id: int,
        asset_data: FixedAssetCreate
    ) -> FixedAsset:
        """Create a new fixed asset"""
        
        # Check for duplicate asset code
        existing = db.query(FixedAsset).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.asset_code == asset_data.asset_code,
            FixedAsset.is_deleted == False
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset with code {asset_data.asset_code} already exists"
            )
        
        # Calculate total cost
        total_cost = (
            asset_data.purchase_cost +
            asset_data.installation_cost +
            asset_data.transportation_cost +
            asset_data.other_costs
        )
        
        # Calculate initial net book value
        net_book_value = total_cost - asset_data.salvage_value
        
        # Create asset
        asset = FixedAsset(
            tenant_id=tenant_id,
            **asset_data.model_dump(exclude={'document_urls', 'tags', 'custom_fields'}),
            total_cost=total_cost,
            accumulated_depreciation=Decimal('0.00'),
            net_book_value=net_book_value,
            current_value=total_cost,
            created_by=user_id,
            updated_by=user_id
        )
        
        # Handle JSON fields
        if asset_data.document_urls:
            import json
            asset.document_urls = json.dumps(asset_data.document_urls)
        if asset_data.tags:
            import json
            asset.tags = json.dumps(asset_data.tags)
        if asset_data.custom_fields:
            import json
            asset.custom_fields = json.dumps(asset_data.custom_fields)
        
        db.add(asset)
        db.commit()
        db.refresh(asset)
        
        return asset
    
    @staticmethod
    def update_asset(
        db: Session,
        tenant_id: int,
        user_id: int,
        asset_id: int,
        asset_data: FixedAssetUpdate
    ) -> FixedAsset:
        """Update existing asset"""
        
        asset = db.query(FixedAsset).filter(
            FixedAsset.id == asset_id,
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        # Update fields
        update_data = asset_data.model_dump(exclude_unset=True, exclude={'document_urls', 'tags', 'custom_fields'})
        for field, value in update_data.items():
            setattr(asset, field, value)
        
        # Handle JSON fields
        if asset_data.document_urls is not None:
            import json
            asset.document_urls = json.dumps(asset_data.document_urls)
        if asset_data.tags is not None:
            import json
            asset.tags = json.dumps(asset_data.tags)
        if asset_data.custom_fields is not None:
            import json
            asset.custom_fields = json.dumps(asset_data.custom_fields)
        
        asset.updated_by = user_id
        asset.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(asset)
        
        return asset
    
    @staticmethod
    def get_asset(db: Session, tenant_id: int, asset_id: int) -> Optional[FixedAsset]:
        """Get asset by ID"""
        return db.query(FixedAsset).filter(
            FixedAsset.id == asset_id,
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).first()
    
    @staticmethod
    def list_assets(
        db: Session,
        tenant_id: int,
        filters: AssetFilterParams
    ) -> Tuple[List[FixedAsset], int]:
        """List assets with filtering and pagination"""
        
        query = db.query(FixedAsset).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        )
        
        # Apply filters
        if filters.category:
            query = query.filter(FixedAsset.asset_category == filters.category)
        
        if filters.status:
            query = query.filter(FixedAsset.asset_status == filters.status)
        
        if filters.location_id:
            query = query.filter(FixedAsset.location_id == filters.location_id)
        
        if filters.department_id:
            query = query.filter(FixedAsset.department_id == filters.department_id)
        
        if filters.custodian_id:
            query = query.filter(FixedAsset.custodian_id == filters.custodian_id)
        
        if filters.acquisition_date_from:
            query = query.filter(FixedAsset.acquisition_date >= filters.acquisition_date_from)
        
        if filters.acquisition_date_to:
            query = query.filter(FixedAsset.acquisition_date <= filters.acquisition_date_to)
        
        if filters.purchase_cost_min:
            query = query.filter(FixedAsset.purchase_cost >= filters.purchase_cost_min)
        
        if filters.purchase_cost_max:
            query = query.filter(FixedAsset.purchase_cost <= filters.purchase_cost_max)
        
        if filters.search_query:
            search = f"%{filters.search_query}%"
            query = query.filter(
                or_(
                    FixedAsset.asset_code.ilike(search),
                    FixedAsset.asset_name.ilike(search),
                    FixedAsset.asset_description.ilike(search),
                    FixedAsset.serial_number.ilike(search),
                    FixedAsset.barcode.ilike(search)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(FixedAsset, filters.sort_by, FixedAsset.asset_code)
        if filters.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        assets = query.offset(offset).limit(filters.page_size).all()
        
        return assets, total
    
    @staticmethod
    def delete_asset(db: Session, tenant_id: int, user_id: int, asset_id: int) -> bool:
        """Soft delete an asset"""
        
        asset = db.query(FixedAsset).filter(
            FixedAsset.id == asset_id,
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        # Check if asset can be deleted
        if asset.asset_status in [AssetStatus.DISPOSED, AssetStatus.SOLD]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete disposed or sold assets"
            )
        
        asset.is_deleted = True
        asset.deleted_at = datetime.utcnow()
        asset.deleted_by = user_id
        
        db.commit()
        return True
    
    @staticmethod
    def dispose_asset(
        db: Session,
        tenant_id: int,
        user_id: int,
        disposal_data: AssetDisposalRequest
    ) -> Dict[str, Any]:
        """Dispose an asset"""
        
        asset = db.query(FixedAsset).filter(
            FixedAsset.id == disposal_data.asset_id,
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        if asset.asset_status in [AssetStatus.DISPOSED, AssetStatus.SOLD]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Asset already disposed"
            )
        
        # Calculate gain/loss
        net_book_value = asset.net_book_value or Decimal('0.00')
        disposal_proceeds = disposal_data.disposal_value - disposal_data.disposal_cost
        disposal_gain_loss = disposal_proceeds - net_book_value
        
        # Update asset
        asset.asset_status = AssetStatus.DISPOSED if disposal_data.disposal_method != DisposalMethod.SALE else AssetStatus.SOLD
        asset.disposal_date = disposal_data.disposal_date
        asset.disposal_method = disposal_data.disposal_method
        asset.disposal_value = disposal_data.disposal_value
        asset.disposal_cost = disposal_data.disposal_cost
        asset.disposal_gain_loss = disposal_gain_loss
        asset.disposal_approved_by = user_id
        asset.disposal_notes = disposal_data.disposal_notes
        asset.status_change_date = disposal_data.disposal_date
        asset.in_use = False
        asset.updated_by = user_id
        asset.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(asset)
        
        return {
            "asset_id": asset.id,
            "disposal_date": disposal_data.disposal_date,
            "disposal_method": disposal_data.disposal_method,
            "net_book_value": net_book_value,
            "disposal_value": disposal_data.disposal_value,
            "disposal_cost": disposal_data.disposal_cost,
            "disposal_gain_loss": disposal_gain_loss,
            "message": "Asset disposed successfully"
        }
    
    @staticmethod
    def calculate_depreciation(
        asset: FixedAsset,
        calculation_date: date,
        period_start: date,
        period_end: date
    ) -> Decimal:
        """Calculate depreciation for an asset"""
        
        if asset.depreciation_method == DepreciationMethod.NO_DEPRECIATION:
            return Decimal('0.00')
        
        # Get current WDV
        current_wdv = asset.net_book_value or asset.total_cost
        
        # Skip if already fully depreciated
        if current_wdv <= asset.salvage_value:
            return Decimal('0.00')
        
        # Calculate based on method
        if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            # SLM: (Cost - Salvage) / Useful Life
            if not asset.useful_life_years or asset.useful_life_years == 0:
                return Decimal('0.00')
            
            depreciable_amount = asset.total_cost - asset.salvage_value
            annual_depreciation = depreciable_amount / Decimal(asset.useful_life_years)
            
            # Calculate for period (pro-rata if partial year)
            days_in_period = (period_end - period_start).days + 1
            period_depreciation = (annual_depreciation / Decimal('365')) * Decimal(days_in_period)
            
            return round(period_depreciation, 2)
        
        elif asset.depreciation_method == DepreciationMethod.WRITTEN_DOWN_VALUE:
            # WDV: Rate applied on WDV
            if not asset.depreciation_rate:
                return Decimal('0.00')
            
            rate = asset.depreciation_rate / Decimal('100')
            
            # Calculate for period (pro-rata if partial year)
            days_in_period = (period_end - period_start).days + 1
            annual_depreciation = current_wdv * rate
            period_depreciation = (annual_depreciation / Decimal('365')) * Decimal(days_in_period)
            
            # Ensure not below salvage value
            if current_wdv - period_depreciation < asset.salvage_value:
                period_depreciation = current_wdv - asset.salvage_value
            
            return round(period_depreciation, 2)
        
        elif asset.depreciation_method == DepreciationMethod.DOUBLE_DECLINING:
            # Double declining balance
            if not asset.useful_life_years or asset.useful_life_years == 0:
                return Decimal('0.00')
            
            rate = (Decimal('2') / Decimal(asset.useful_life_years))
            
            days_in_period = (period_end - period_start).days + 1
            annual_depreciation = current_wdv * rate
            period_depreciation = (annual_depreciation / Decimal('365')) * Decimal(days_in_period)
            
            # Ensure not below salvage value
            if current_wdv - period_depreciation < asset.salvage_value:
                period_depreciation = current_wdv - asset.salvage_value
            
            return round(period_depreciation, 2)
        
        return Decimal('0.00')
    
    @staticmethod
    def get_asset_summary(db: Session, tenant_id: int) -> Dict[str, Any]:
        """Get summary statistics for assets"""
        
        # Total counts
        total_assets = db.query(func.count(FixedAsset.id)).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).scalar()
        
        active_assets = db.query(func.count(FixedAsset.id)).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.asset_status == AssetStatus.ACTIVE,
            FixedAsset.is_deleted == False
        ).scalar()
        
        # Financial summary
        financial_summary = db.query(
            func.sum(FixedAsset.total_cost).label('total_cost'),
            func.sum(FixedAsset.accumulated_depreciation).label('total_depreciation'),
            func.sum(FixedAsset.net_book_value).label('total_nbv')
        ).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).first()
        
        # Assets by category
        by_category = db.query(
            FixedAsset.asset_category,
            func.count(FixedAsset.id).label('count'),
            func.sum(FixedAsset.total_cost).label('total_cost')
        ).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).group_by(FixedAsset.asset_category).all()
        
        # Assets by status
        by_status = db.query(
            FixedAsset.asset_status,
            func.count(FixedAsset.id).label('count')
        ).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False
        ).group_by(FixedAsset.asset_status).all()
        
        return {
            "total_assets": total_assets or 0,
            "active_assets": active_assets or 0,
            "total_cost": float(financial_summary.total_cost or 0),
            "total_depreciation": float(financial_summary.total_depreciation or 0),
            "total_net_book_value": float(financial_summary.total_nbv or 0),
            "assets_by_category": [
                {
                    "category": cat.value,
                    "count": count,
                    "total_cost": float(total_cost or 0)
                }
                for cat, count, total_cost in by_category
            ],
            "assets_by_status": [
                {"status": status.value, "count": count}
                for status, count in by_status
            ]
        }
