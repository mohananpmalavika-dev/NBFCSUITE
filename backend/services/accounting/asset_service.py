"""
Asset Management Service
Fixed Assets, Depreciation, Transfers, Disposal, Maintenance
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil.relativedelta import relativedelta

from backend.shared.database.asset_models import (
    FixedAsset,
    AssetDepreciationSchedule,
    AssetTransfer,
    AssetMaintenance
)
from backend.shared.database.accounting_extended_models import (
    AssetCategory,
    DepreciationMethod,
    AssetStatus
)


class AssetService:
    """Service for asset management"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_asset_code(self, category: AssetCategory) -> str:
        """Generate unique asset code"""
        category_prefix = {
            AssetCategory.LAND: "LND",
            AssetCategory.BUILDING: "BLD",
            AssetCategory.PLANT_MACHINERY: "PLT",
            AssetCategory.FURNITURE_FIXTURES: "FRN",
            AssetCategory.OFFICE_EQUIPMENT: "OFC",
            AssetCategory.COMPUTERS: "CMP",
            AssetCategory.VEHICLES: "VEH",
            AssetCategory.SOFTWARE: "SFT",
            AssetCategory.INTANGIBLE: "INT"
        }
        
        prefix = category_prefix.get(category, "AST")
        year = datetime.now().year
        
        query = select(FixedAsset).where(
            and_(
                FixedAsset.tenant_id == self.tenant_id,
                FixedAsset.asset_code.like(f"{prefix}-{year}-%")
            )
        ).order_by(desc(FixedAsset.asset_code)).limit(1)
        
        result = await self.db.execute(query)
        last_asset = result.scalar_one_or_none()
        
        if last_asset:
            last_number = int(last_asset.asset_code.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{year}-{new_number:04d}"
    
    async def create_asset(
        self,
        asset_name: str,
        category: AssetCategory,
        purchase_date: date,
        purchase_cost: Decimal,
        depreciation_method: DepreciationMethod,
        depreciation_rate: Decimal,
        useful_life_years: int,
        salvage_value: Decimal = Decimal("0.00"),
        description: Optional[str] = None,
        location: Optional[str] = None,
        department: Optional[str] = None,
        vendor_name: Optional[str] = None,
        invoice_number: Optional[str] = None
    ) -> FixedAsset:
        """Create new fixed asset"""
        
        asset_code = await self.generate_asset_code(category)
        
        asset = FixedAsset(
            tenant_id=self.tenant_id,
            asset_code=asset_code,
            asset_name=asset_name,
            description=description,
            category=category,
            purchase_date=purchase_date,
            purchase_cost=purchase_cost,
            vendor_name=vendor_name,
            invoice_number=invoice_number,
            location=location,
            department=department,
            depreciation_method=depreciation_method,
            depreciation_rate=depreciation_rate,
            useful_life_years=useful_life_years,
            salvage_value=salvage_value,
            accumulated_depreciation=Decimal("0.00"),
            written_down_value=purchase_cost,
            status=AssetStatus.ACTIVE,
            created_by=self.user_id
        )
        
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        
        return asset
    
    def calculate_depreciation_straight_line(
        self,
        cost: Decimal,
        salvage_value: Decimal,
        useful_life_months: int,
        months_in_period: int = 1
    ) -> Decimal:
        """Calculate straight-line depreciation"""
        depreciable_amount = cost - salvage_value
        monthly_depreciation = depreciable_amount / useful_life_months
        return (monthly_depreciation * months_in_period).quantize(Decimal("0.01"))
    
    def calculate_depreciation_wdv(
        self,
        opening_wdv: Decimal,
        rate: Decimal,
        months_in_period: int = 12
    ) -> Decimal:
        """Calculate Written Down Value depreciation"""
        annual_depreciation = opening_wdv * rate / Decimal("100")
        if months_in_period < 12:
            return (annual_depreciation * months_in_period / 12).quantize(Decimal("0.01"))
        return annual_depreciation.quantize(Decimal("0.01"))
    
    async def calculate_monthly_depreciation(
        self,
        asset: FixedAsset,
        depreciation_date: date
    ) -> Decimal:
        """Calculate depreciation for a month"""
        
        if asset.status != AssetStatus.ACTIVE:
            return Decimal("0.00")
        
        # Check if already fully depreciated
        if asset.written_down_value <= asset.salvage_value:
            return Decimal("0.00")
        
        if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            total_months = asset.useful_life_years * 12 + asset.useful_life_months
            depreciation = self.calculate_depreciation_straight_line(
                asset.purchase_cost,
                asset.salvage_value,
                total_months,
                1
            )
        elif asset.depreciation_method == DepreciationMethod.WRITTEN_DOWN_VALUE:
            depreciation = self.calculate_depreciation_wdv(
                asset.written_down_value,
                asset.depreciation_rate,
                1
            )
        else:
            # Default to straight line
            total_months = asset.useful_life_years * 12
            depreciation = self.calculate_depreciation_straight_line(
                asset.purchase_cost,
                asset.salvage_value,
                total_months,
                1
            )
        
        # Don't depreciate below salvage value
        if asset.written_down_value - depreciation < asset.salvage_value:
            depreciation = asset.written_down_value - asset.salvage_value
        
        return depreciation
    
    async def post_depreciation(
        self,
        asset_id: int,
        depreciation_date: date,
        journal_entry_id: Optional[int] = None
    ) -> AssetDepreciationSchedule:
        """Post depreciation for an asset"""
        
        asset = await self.get_asset(asset_id)
        if not asset:
            raise ValueError("Asset not found")
        
        # Check if already posted for this period
        existing = await self.db.execute(
            select(AssetDepreciationSchedule).where(
                and_(
                    AssetDepreciationSchedule.asset_id == asset_id,
                    AssetDepreciationSchedule.depreciation_date == depreciation_date
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Depreciation already posted for this period")
        
        depreciation_amount = await self.calculate_monthly_depreciation(asset, depreciation_date)
        
        opening_wdv = asset.written_down_value
        new_accumulated = asset.accumulated_depreciation + depreciation_amount
        closing_wdv = asset.purchase_cost - new_accumulated
        
        # Create schedule entry
        schedule = AssetDepreciationSchedule(
            tenant_id=self.tenant_id,
            asset_id=asset_id,
            depreciation_date=depreciation_date,
            financial_year=depreciation_date.year if depreciation_date.month >= 4 else depreciation_date.year - 1,
            month=depreciation_date.month,
            opening_wdv=opening_wdv,
            depreciation_amount=depreciation_amount,
            accumulated_depreciation=new_accumulated,
            closing_wdv=closing_wdv,
            journal_entry_id=journal_entry_id,
            is_posted=journal_entry_id is not None,
            created_by=self.user_id
        )
        
        self.db.add(schedule)
        
        # Update asset
        asset.accumulated_depreciation = new_accumulated
        asset.written_down_value = closing_wdv
        asset.last_depreciation_date = depreciation_date
        
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return schedule
    
    async def get_asset(self, asset_id: int) -> Optional[FixedAsset]:
        """Get asset by ID"""
        query = select(FixedAsset).where(
            and_(
                FixedAsset.id == asset_id,
                FixedAsset.tenant_id == self.tenant_id,
                FixedAsset.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_assets(
        self,
        category: Optional[AssetCategory] = None,
        status: Optional[AssetStatus] = None,
        location: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[FixedAsset], int]:
        """List assets with filters"""
        conditions = [
            FixedAsset.tenant_id == self.tenant_id,
            FixedAsset.is_deleted == False
        ]
        
        if category:
            conditions.append(FixedAsset.category == category)
        if status:
            conditions.append(FixedAsset.status == status)
        if location:
            conditions.append(FixedAsset.location == location)
        
        count_query = select(func.count(FixedAsset.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        query = select(FixedAsset).where(and_(*conditions)).order_by(
            desc(FixedAsset.purchase_date)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        assets = result.scalars().all()
        
        return assets, total
    
    async def transfer_asset(
        self,
        asset_id: int,
        to_location: Optional[str],
        to_department: Optional[str],
        to_custodian: Optional[str],
        transfer_reason: Optional[str]
    ) -> AssetTransfer:
        """Transfer asset to new location/department"""
        
        asset = await self.get_asset(asset_id)
        if not asset:
            raise ValueError("Asset not found")
        
        transfer_number = f"TRF-{datetime.now().year}{datetime.now().month:02d}-{asset_id:05d}"
        
        transfer = AssetTransfer(
            tenant_id=self.tenant_id,
            asset_id=asset_id,
            transfer_number=transfer_number,
            transfer_date=date.today(),
            from_location=asset.location,
            from_department=asset.department,
            from_custodian=asset.custodian,
            to_location=to_location,
            to_department=to_department,
            to_custodian=to_custodian,
            transfer_reason=transfer_reason,
            created_by=self.user_id
        )
        
        self.db.add(transfer)
        
        # Update asset
        if to_location:
            asset.location = to_location
        if to_department:
            asset.department = to_department
        if to_custodian:
            asset.custodian = to_custodian
        
        await self.db.commit()
        await self.db.refresh(transfer)
        
        return transfer
    
    async def dispose_asset(
        self,
        asset_id: int,
        disposal_date: date,
        disposal_amount: Decimal,
        disposal_reason: str
    ) -> FixedAsset:
        """Dispose/sell asset"""
        
        asset = await self.get_asset(asset_id)
        if not asset:
            raise ValueError("Asset not found")
        
        # Calculate gain/loss
        gain_loss = disposal_amount - asset.written_down_value
        
        asset.status = AssetStatus.SOLD
        asset.disposal_date = disposal_date
        asset.disposal_amount = disposal_amount
        asset.gain_loss_on_disposal = gain_loss
        
        await self.db.commit()
        await self.db.refresh(asset)
        
        return asset
    
    async def record_maintenance(
        self,
        asset_id: int,
        maintenance_date: date,
        maintenance_type: str,
        description: str,
        cost: Decimal,
        vendor_name: Optional[str] = None
    ) -> AssetMaintenance:
        """Record asset maintenance"""
        
        maintenance = AssetMaintenance(
            tenant_id=self.tenant_id,
            asset_id=asset_id,
            maintenance_date=maintenance_date,
            maintenance_type=maintenance_type,
            description=description,
            vendor_name=vendor_name,
            maintenance_cost=cost,
            is_completed=True,
            completion_date=maintenance_date,
            created_by=self.user_id
        )
        
        self.db.add(maintenance)
        await self.db.commit()
        await self.db.refresh(maintenance)
        
        return maintenance
    
    async def get_depreciation_schedule(
        self,
        asset_id: Optional[int] = None,
        financial_year: Optional[int] = None,
        month: Optional[int] = None
    ) -> List[AssetDepreciationSchedule]:
        """Get depreciation schedule"""
        conditions = [AssetDepreciationSchedule.tenant_id == self.tenant_id]
        
        if asset_id:
            conditions.append(AssetDepreciationSchedule.asset_id == asset_id)
        if financial_year:
            conditions.append(AssetDepreciationSchedule.financial_year == financial_year)
        if month:
            conditions.append(AssetDepreciationSchedule.month == month)
        
        query = select(AssetDepreciationSchedule).where(and_(*conditions)).order_by(
            AssetDepreciationSchedule.depreciation_date
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
