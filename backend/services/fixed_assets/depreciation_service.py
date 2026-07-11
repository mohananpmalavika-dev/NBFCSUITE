"""
Asset Depreciation Service
Handles depreciation calculations and postings
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func
from fastapi import HTTPException, status

from backend.shared.database.asset_models import (
    FixedAsset, AssetDepreciation,
    AssetStatus, DepreciationMethod
)
from backend.services.fixed_assets.schemas import (
    DepreciationCalculationRequest,
    AssetDepreciationCreate
)


class DepreciationService:
    """Service for depreciation operations"""
    
    @staticmethod
    def calculate_and_post_depreciation(
        db: Session,
        tenant_id: int,
        user_id: int,
        request: DepreciationCalculationRequest
    ) -> Dict[str, Any]:
        """Calculate and optionally post depreciation for assets"""
        
        # Determine period dates
        if request.financial_month:
            # Monthly depreciation
            period_start = date(request.financial_year, request.financial_month, 1)
            if request.financial_month == 12:
                period_end = date(request.financial_year, 12, 31)
            else:
                next_month = date(request.financial_year, request.financial_month + 1, 1)
                period_end = next_month - datetime.timedelta(days=1)
        else:
            # Annual depreciation
            period_start = date(request.financial_year, 1, 1)
            period_end = date(request.financial_year, 12, 31)
        
        # Get assets to depreciate
        query = db.query(FixedAsset).filter(
            FixedAsset.tenant_id == tenant_id,
            FixedAsset.is_deleted == False,
            FixedAsset.asset_status == AssetStatus.ACTIVE,
            FixedAsset.depreciation_method != DepreciationMethod.NO_DEPRECIATION,
            FixedAsset.acquisition_date <= period_end
        )
        
        if request.asset_ids:
            query = query.filter(FixedAsset.id.in_(request.asset_ids))
        
        assets = query.all()
        
        results = {
            "total_assets": len(assets),
            "assets_depreciated": 0,
            "total_depreciation": Decimal('0.00'),
            "posted_entries": 0,
            "errors": []
        }
        
        for asset in assets:
            try:
                # Check if already depreciated for this period
                existing = db.query(AssetDepreciation).filter(
                    AssetDepreciation.tenant_id == tenant_id,
                    AssetDepreciation.asset_id == asset.id,
                    AssetDepreciation.financial_year == request.financial_year,
                    AssetDepreciation.financial_month == request.financial_month,
                    AssetDepreciation.is_reversed == False
                ).first()
                
                if existing:
                    results["errors"].append({
                        "asset_id": asset.id,
                        "asset_code": asset.asset_code,
                        "error": "Depreciation already calculated for this period"
                    })
                    continue
                
                # Calculate depreciation
                opening_wdv = asset.net_book_value or asset.total_cost
                
                # Skip if already fully depreciated
                if opening_wdv <= asset.salvage_value:
                    continue
                
                depreciation_amount = DepreciationService._calculate_depreciation(
                    asset, period_start, period_end
                )
                
                if depreciation_amount <= 0:
                    continue
                
                # Calculate closing WDV
                accumulated_depreciation = (asset.accumulated_depreciation or Decimal('0.00')) + depreciation_amount
                closing_wdv = opening_wdv - depreciation_amount
                
                # Ensure not below salvage value
                if closing_wdv < asset.salvage_value:
                    depreciation_amount = opening_wdv - asset.salvage_value
                    closing_wdv = asset.salvage_value
                    accumulated_depreciation = asset.total_cost - asset.salvage_value
                
                # Create depreciation entry
                days_in_period = (period_end - period_start).days + 1
                is_partial = days_in_period < 365
                
                depreciation_entry = AssetDepreciation(
                    tenant_id=tenant_id,
                    asset_id=asset.id,
                    financial_year=request.financial_year,
                    financial_month=request.financial_month,
                    period_start_date=period_start,
                    period_end_date=period_end,
                    depreciation_date=request.calculation_date,
                    depreciation_method=asset.depreciation_method,
                    depreciation_rate=asset.depreciation_rate,
                    opening_wdv=opening_wdv,
                    depreciation_amount=depreciation_amount,
                    accumulated_depreciation=accumulated_depreciation,
                    closing_wdv=closing_wdv,
                    days_in_period=days_in_period,
                    is_partial_year=is_partial,
                    is_posted=request.auto_post,
                    created_by=user_id,
                    updated_by=user_id
                )
                
                if request.auto_post:
                    depreciation_entry.posted_at = datetime.utcnow()
                    depreciation_entry.posted_by = user_id
                
                db.add(depreciation_entry)
                
                # Update asset
                asset.accumulated_depreciation = accumulated_depreciation
                asset.net_book_value = closing_wdv
                asset.current_value = closing_wdv
                asset.last_depreciation_date = request.calculation_date
                asset.updated_by = user_id
                asset.updated_at = datetime.utcnow()
                
                results["assets_depreciated"] += 1
                results["total_depreciation"] += depreciation_amount
                if request.auto_post:
                    results["posted_entries"] += 1
                
            except Exception as e:
                results["errors"].append({
                    "asset_id": asset.id,
                    "asset_code": asset.asset_code,
                    "error": str(e)
                })
        
        db.commit()
        
        return results
    
    @staticmethod
    def _calculate_depreciation(
        asset: FixedAsset,
        period_start: date,
        period_end: date
    ) -> Decimal:
        """Calculate depreciation for an asset"""
        
        current_wdv = asset.net_book_value or asset.total_cost
        
        # Skip if already at salvage value
        if current_wdv <= asset.salvage_value:
            return Decimal('0.00')
        
        days_in_period = (period_end - period_start).days + 1
        
        if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            # SLM: (Cost - Salvage) / Useful Life
            if not asset.useful_life_years or asset.useful_life_years == 0:
                return Decimal('0.00')
            
            depreciable_amount = asset.total_cost - asset.salvage_value
            annual_depreciation = depreciable_amount / Decimal(asset.useful_life_years)
            
            # Pro-rata for period
            period_depreciation = (annual_depreciation / Decimal('365')) * Decimal(days_in_period)
            
            return round(period_depreciation, 2)
        
        elif asset.depreciation_method == DepreciationMethod.WRITTEN_DOWN_VALUE:
            # WDV: Rate applied on WDV
            if not asset.depreciation_rate:
                return Decimal('0.00')
            
            rate = asset.depreciation_rate / Decimal('100')
            annual_depreciation = current_wdv * rate
            
            # Pro-rata for period
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
            annual_depreciation = current_wdv * rate
            
            # Pro-rata for period
            period_depreciation = (annual_depreciation / Decimal('365')) * Decimal(days_in_period)
            
            # Ensure not below salvage value
            if current_wdv - period_depreciation < asset.salvage_value:
                period_depreciation = current_wdv - asset.salvage_value
            
            return round(period_depreciation, 2)
        
        elif asset.depreciation_method == DepreciationMethod.SUM_OF_YEARS:
            # Sum of years digits
            if not asset.useful_life_years or asset.useful_life_years == 0:
                return Decimal('0.00')
            
            # Calculate asset age in years
            if not asset.depreciation_start_date:
                asset_start = asset.acquisition_date
            else:
                asset_start = asset.depreciation_start_date
            
            years_used = (period_end.year - asset_start.year)
            remaining_life = max(asset.useful_life_years - years_used, 1)
            
            sum_of_years = (asset.useful_life_years * (asset.useful_life_years + 1)) / 2
            
            depreciable_amount = asset.total_cost - asset.salvage_value
            annual_depreciation = (Decimal(remaining_life) / Decimal(sum_of_years)) * depreciable_amount
            
            # Pro-rata for period
            period_depreciation = (annual_depreciation / Decimal('365')) * Decimal(days_in_period)
            
            return round(period_depreciation, 2)
        
        return Decimal('0.00')
    
    @staticmethod
    def get_depreciation_schedule(
        db: Session,
        tenant_id: int,
        asset_id: int
    ) -> List[AssetDepreciation]:
        """Get depreciation schedule for an asset"""
        
        return db.query(AssetDepreciation).filter(
            AssetDepreciation.tenant_id == tenant_id,
            AssetDepreciation.asset_id == asset_id,
            AssetDepreciation.is_reversed == False
        ).order_by(AssetDepreciation.depreciation_date.desc()).all()
    
    @staticmethod
    def reverse_depreciation(
        db: Session,
        tenant_id: int,
        user_id: int,
        depreciation_id: int,
        reason: str
    ) -> bool:
        """Reverse a depreciation entry"""
        
        depreciation = db.query(AssetDepreciation).filter(
            AssetDepreciation.id == depreciation_id,
            AssetDepreciation.tenant_id == tenant_id,
            AssetDepreciation.is_reversed == False
        ).first()
        
        if not depreciation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Depreciation entry not found"
            )
        
        if not depreciation.is_posted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reverse unposted depreciation"
            )
        
        # Mark as reversed
        depreciation.is_reversed = True
        depreciation.reversed_at = datetime.utcnow()
        depreciation.reversed_by = user_id
        depreciation.reversal_reason = reason
        
        # Update asset
        asset = depreciation.asset
        asset.accumulated_depreciation = (asset.accumulated_depreciation or Decimal('0.00')) - depreciation.depreciation_amount
        asset.net_book_value = (asset.net_book_value or Decimal('0.00')) + depreciation.depreciation_amount
        asset.current_value = asset.net_book_value
        asset.updated_by = user_id
        asset.updated_at = datetime.utcnow()
        
        db.commit()
        
        return True
    
    @staticmethod
    def get_depreciation_report(
        db: Session,
        tenant_id: int,
        financial_year: int,
        financial_month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate depreciation report"""
        
        query = db.query(AssetDepreciation).filter(
            AssetDepreciation.tenant_id == tenant_id,
            AssetDepreciation.financial_year == financial_year,
            AssetDepreciation.is_reversed == False
        )
        
        if financial_month:
            query = query.filter(AssetDepreciation.financial_month == financial_month)
        
        depreciation_entries = query.all()
        
        total_depreciation = sum(entry.depreciation_amount for entry in depreciation_entries)
        
        # Group by category
        by_category = {}
        for entry in depreciation_entries:
            category = entry.asset.asset_category.value
            if category not in by_category:
                by_category[category] = {
                    "category": category,
                    "count": 0,
                    "total_depreciation": Decimal('0.00')
                }
            by_category[category]["count"] += 1
            by_category[category]["total_depreciation"] += entry.depreciation_amount
        
        # Group by method
        by_method = {}
        for entry in depreciation_entries:
            method = entry.depreciation_method.value
            if method not in by_method:
                by_method[method] = {
                    "method": method,
                    "count": 0,
                    "total_depreciation": Decimal('0.00')
                }
            by_method[method]["count"] += 1
            by_method[method]["total_depreciation"] += entry.depreciation_amount
        
        return {
            "financial_year": financial_year,
            "financial_month": financial_month,
            "total_depreciation": float(total_depreciation),
            "assets_depreciated": len(depreciation_entries),
            "depreciation_by_category": [
                {
                    "category": v["category"],
                    "count": v["count"],
                    "total_depreciation": float(v["total_depreciation"])
                }
                for v in by_category.values()
            ],
            "depreciation_by_method": [
                {
                    "method": v["method"],
                    "count": v["count"],
                    "total_depreciation": float(v["total_depreciation"])
                }
                for v in by_method.values()
            ]
        }
