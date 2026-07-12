"""
Stock Verification Service
Business logic for physical stock verification
"""

from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from uuid import UUID
import uuid

from backend.shared.database.inventory_models import (
    StockVerification, StockVerificationItem, ItemMaster, VerificationStatus
)
from backend.services.inventory import schemas


class StockVerificationService:
    """Service for stock verification operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_verification_number(self) -> str:
        """Generate unique verification number"""
        query = select(func.count(StockVerification.id)).where(
            and_(
                StockVerification.tenant_id == self.tenant_id,
                StockVerification.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        
        return f"SV-{(count + 1):06d}"
    
    async def create_verification(
        self, 
        verification_data: schemas.StockVerificationCreate
    ) -> StockVerification:
        """Create stock verification"""
        # Generate verification number
        verification_number = await self.generate_verification_number()
        
        # Create verification header
        verification = StockVerification(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            verification_number=verification_number,
            verification_date=verification_data.verification_date,
            scheduled_date=verification_data.scheduled_date,
            verification_status=VerificationStatus.PLANNED,
            warehouse=verification_data.warehouse,
            location=verification_data.location,
            item_category=verification_data.item_category,
            supervisor_id=verification_data.supervisor_id,
            supervisor_name=verification_data.supervisor_name,
            purpose=verification_data.purpose,
            remarks=verification_data.remarks,
            total_items=0,
            items_verified=0,
            items_with_variance=0,
            total_variance_value=Decimal("0.00"),
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(verification)
        
        # Add verification items
        for item_data in verification_data.items:
            # Get item to capture system stock
            item_query = await self.db.execute(
                select(ItemMaster).where(
                    and_(
                        ItemMaster.id == item_data.item_id,
                        ItemMaster.tenant_id == self.tenant_id,
                        ItemMaster.is_deleted == False
                    )
                )
            )
            item = item_query.scalar_one_or_none()
            if not item:
                continue
            
            verification_item = StockVerificationItem(
                id=uuid.uuid4(),
                verification_id=verification.id,
                item_id=item.id,
                system_quantity=item.current_stock,
                system_rate=item.average_cost,
                system_value=item.total_value,
                physical_quantity=item_data.physical_quantity,
                batch_number=item_data.batch_number,
                serial_number=item_data.serial_number,
                remarks=item_data.remarks,
                is_verified=False,
                has_variance=False,
                is_reconciled=False
            )
            self.db.add(verification_item)
            verification.total_items += 1
        
        await self.db.commit()
        await self.db.refresh(verification)
        
        return verification
    
    async def get_verification(self, verification_id: UUID) -> Optional[StockVerification]:
        """Get verification by ID"""
        result = await self.db.execute(
            select(StockVerification)
            .options(selectinload(StockVerification.items))
            .where(
                and_(
                    StockVerification.id == verification_id,
                    StockVerification.tenant_id == self.tenant_id,
                    StockVerification.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_verifications(
        self,
        verification_status: Optional[VerificationStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[StockVerification], int]:
        """List verifications with filters"""
        query = select(StockVerification).where(
            and_(
                StockVerification.tenant_id == self.tenant_id,
                StockVerification.is_deleted == False
            )
        )
        
        if verification_status:
            query = query.where(StockVerification.verification_status == verification_status)
        if from_date:
            query = query.where(StockVerification.verification_date >= from_date)
        if to_date:
            query = query.where(StockVerification.verification_date <= to_date)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get verifications with pagination
        query = query.order_by(StockVerification.verification_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        verifications = result.scalars().all()
        
        return list(verifications), total
    
    async def update_verification_item(
        self, 
        item_id: UUID, 
        physical_quantity: Decimal,
        remarks: Optional[str] = None
    ) -> StockVerificationItem:
        """Update physical quantity for verification item"""
        result = await self.db.execute(
            select(StockVerificationItem).where(StockVerificationItem.id == item_id)
        )
        verification_item = result.scalar_one_or_none()
        if not verification_item:
            raise ValueError("Verification item not found")
        
        # Update physical quantity
        verification_item.physical_quantity = physical_quantity
        verification_item.physical_rate = verification_item.system_rate
        verification_item.physical_value = physical_quantity * verification_item.system_rate
        
        # Calculate variance
        verification_item.variance_quantity = physical_quantity - verification_item.system_quantity
        verification_item.variance_value = verification_item.physical_value - verification_item.system_value
        
        if verification_item.system_quantity > 0:
            verification_item.variance_percentage = (
                (verification_item.variance_quantity / verification_item.system_quantity) * 100
            )
        
        verification_item.has_variance = abs(verification_item.variance_quantity) > Decimal("0.001")
        verification_item.is_verified = True
        verification_item.verified_at = datetime.utcnow()
        verification_item.verified_by = self.user_id
        if remarks:
            verification_item.remarks = remarks
        
        await self.db.commit()
        await self.db.refresh(verification_item)
        
        return verification_item
    
    async def complete_verification(self, verification_id: UUID) -> StockVerification:
        """Complete verification and calculate summary"""
        verification = await self.get_verification(verification_id)
        if not verification:
            raise ValueError("Verification not found")
        
        if verification.verification_status != VerificationStatus.IN_PROGRESS:
            # Start if planned
            if verification.verification_status == VerificationStatus.PLANNED:
                verification.verification_status = VerificationStatus.IN_PROGRESS
        
        # Calculate summary from items
        items_verified = 0
        items_with_variance = 0
        total_variance_value = Decimal("0.00")
        
        for item in verification.items:
            if item.is_verified:
                items_verified += 1
                if item.has_variance:
                    items_with_variance += 1
                    total_variance_value += abs(item.variance_value)
        
        verification.items_verified = items_verified
        verification.items_with_variance = items_with_variance
        verification.total_variance_value = total_variance_value
        
        # Update status
        if items_with_variance > 0:
            verification.verification_status = VerificationStatus.VARIANCE_FOUND
        else:
            verification.verification_status = VerificationStatus.COMPLETED
        
        verification.completed_date = date.today()
        verification.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(verification)
        
        return verification
    
    async def reconcile_variance(
        self, 
        verification_item_id: UUID,
        reconciliation_notes: str
    ) -> StockVerificationItem:
        """Reconcile variance for verification item"""
        result = await self.db.execute(
            select(StockVerificationItem).where(StockVerificationItem.id == verification_item_id)
        )
        verification_item = result.scalar_one_or_none()
        if not verification_item:
            raise ValueError("Verification item not found")
        
        verification_item.is_reconciled = True
        verification_item.reconciliation_notes = reconciliation_notes
        verification_item.reconciled_by = self.user_id
        verification_item.reconciled_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(verification_item)
        
        return verification_item
