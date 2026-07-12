"""
Vendor Service
Business logic for vendor management operations
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
import uuid

from backend.shared.database.procurement_models import (
    Vendor,
    VendorRating,
    VendorStatus,
    VendorType,
    PaymentTerms
)
from .schemas import (
    VendorCreate,
    VendorUpdate,
    VendorRatingCreate,
    VendorPerformanceMetrics
)


class VendorService:
    """Service for managing vendor operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # Vendor CRUD Operations
    # ========================================================================
    
    async def generate_vendor_code(self) -> str:
        """Generate unique vendor code"""
        # Get the latest vendor code
        query = select(Vendor.vendor_code).where(
            Vendor.tenant_id == self.tenant_id
        ).order_by(desc(Vendor.created_at)).limit(1)
        
        result = await self.db.execute(query)
        last_code = result.scalar_one_or_none()
        
        if last_code and last_code.startswith('VEN'):
            try:
                last_number = int(last_code[3:])
                new_number = last_number + 1
            except ValueError:
                new_number = 1
        else:
            new_number = 1
        
        return f"VEN{new_number:06d}"
    
    async def create_vendor(self, vendor_data: VendorCreate) -> Vendor:
        """Create new vendor"""
        
        # Check if GST number already exists (if provided)
        if vendor_data.gst_number:
            existing_query = select(Vendor).where(
                and_(
                    Vendor.tenant_id == self.tenant_id,
                    Vendor.gst_number == vendor_data.gst_number,
                    Vendor.is_deleted == False
                )
            )
            result = await self.db.execute(existing_query)
            if result.scalar_one_or_none():
                raise ValueError(f"Vendor with GST number {vendor_data.gst_number} already exists")
        
        # Generate vendor code
        vendor_code = await self.generate_vendor_code()
        
        # Create vendor
        vendor = Vendor(
            tenant_id=self.tenant_id,
            vendor_code=vendor_code,
            vendor_name=vendor_data.vendor_name,
            vendor_type=vendor_data.vendor_type,
            status=vendor_data.status,
            contact_person=vendor_data.contact_person,
            email=vendor_data.email,
            phone=vendor_data.phone,
            mobile=vendor_data.mobile,
            website=vendor_data.website,
            address_line1=vendor_data.address_line1,
            address_line2=vendor_data.address_line2,
            city=vendor_data.city,
            state=vendor_data.state,
            pincode=vendor_data.pincode,
            country=vendor_data.country,
            pan_number=vendor_data.pan_number,
            gst_number=vendor_data.gst_number,
            tan_number=vendor_data.tan_number,
            msme_registration=vendor_data.msme_registration,
            bank_name=vendor_data.bank_name,
            bank_branch=vendor_data.bank_branch,
            account_number=vendor_data.account_number,
            ifsc_code=vendor_data.ifsc_code,
            account_holder_name=vendor_data.account_holder_name,
            payment_terms=vendor_data.payment_terms,
            credit_limit=vendor_data.credit_limit,
            credit_period_days=vendor_data.credit_period_days,
            products_services=vendor_data.products_services,
            notes=vendor_data.notes,
            created_by=self.user_id
        )
        
        self.db.add(vendor)
        await self.db.commit()
        await self.db.refresh(vendor)
        
        return vendor
    
    async def get_vendor(self, vendor_id: uuid.UUID) -> Optional[Vendor]:
        """Get vendor by ID"""
        query = select(Vendor).where(
            and_(
                Vendor.id == vendor_id,
                Vendor.tenant_id == self.tenant_id,
                Vendor.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_vendor_by_code(self, vendor_code: str) -> Optional[Vendor]:
        """Get vendor by code"""
        query = select(Vendor).where(
            and_(
                Vendor.vendor_code == vendor_code,
                Vendor.tenant_id == self.tenant_id,
                Vendor.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_vendors(
        self,
        status: Optional[VendorStatus] = None,
        vendor_type: Optional[VendorType] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Vendor], int]:
        """List vendors with filters"""
        conditions = [
            Vendor.tenant_id == self.tenant_id,
            Vendor.is_deleted == False
        ]
        
        if status:
            conditions.append(Vendor.status == status)
        if vendor_type:
            conditions.append(Vendor.vendor_type == vendor_type)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    Vendor.vendor_name.ilike(search_pattern),
                    Vendor.vendor_code.ilike(search_pattern),
                    Vendor.email.ilike(search_pattern),
                    Vendor.gst_number.ilike(search_pattern)
                )
            )
        
        # Count total
        count_query = select(func.count(Vendor.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get vendors
        query = select(Vendor).where(and_(*conditions)).order_by(
            desc(Vendor.created_at)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        vendors = result.scalars().all()
        
        return list(vendors), total
    
    async def update_vendor(
        self,
        vendor_id: uuid.UUID,
        vendor_data: VendorUpdate
    ) -> Vendor:
        """Update vendor"""
        vendor = await self.get_vendor(vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")
        
        # Check GST number uniqueness if being updated
        if vendor_data.gst_number and vendor_data.gst_number != vendor.gst_number:
            existing_query = select(Vendor).where(
                and_(
                    Vendor.tenant_id == self.tenant_id,
                    Vendor.gst_number == vendor_data.gst_number,
                    Vendor.id != vendor_id,
                    Vendor.is_deleted == False
                )
            )
            result = await self.db.execute(existing_query)
            if result.scalar_one_or_none():
                raise ValueError(f"Vendor with GST number {vendor_data.gst_number} already exists")
        
        # Update fields
        update_data = vendor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)
        
        vendor.updated_by = self.user_id
        vendor.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(vendor)
        
        return vendor
    
    async def delete_vendor(self, vendor_id: uuid.UUID) -> bool:
        """Soft delete vendor"""
        vendor = await self.get_vendor(vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")
        
        # Check if vendor has active orders
        # TODO: Add check for active orders
        
        vendor.is_deleted = True
        vendor.deleted_at = datetime.utcnow()
        vendor.deleted_by = self.user_id
        
        await self.db.commit()
        return True
    
    async def change_vendor_status(
        self,
        vendor_id: uuid.UUID,
        new_status: VendorStatus,
        reason: Optional[str] = None
    ) -> Vendor:
        """Change vendor status (activate, suspend, blacklist)"""
        vendor = await self.get_vendor(vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")
        
        vendor.status = new_status
        if new_status == VendorStatus.BLACKLISTED and reason:
            vendor.blacklist_reason = reason
        
        vendor.updated_by = self.user_id
        vendor.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(vendor)
        
        return vendor
    
    # ========================================================================
    # Vendor Rating Operations
    # ========================================================================
    
    async def create_vendor_rating(
        self,
        rating_data: VendorRatingCreate,
        rated_by_name: str
    ) -> VendorRating:
        """Create vendor rating"""
        
        # Verify vendor exists
        vendor = await self.get_vendor(rating_data.vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")
        
        # Calculate overall rating
        overall_rating = (
            rating_data.quality_rating +
            rating_data.delivery_rating +
            rating_data.price_rating +
            rating_data.service_rating +
            rating_data.communication_rating
        ) / Decimal("5.0")
        
        # Create rating
        rating = VendorRating(
            tenant_id=self.tenant_id,
            vendor_id=rating_data.vendor_id,
            po_id=rating_data.po_id,
            rating_date=date.today(),
            rating_period_start=rating_data.rating_period_start,
            rating_period_end=rating_data.rating_period_end,
            quality_rating=rating_data.quality_rating,
            delivery_rating=rating_data.delivery_rating,
            price_rating=rating_data.price_rating,
            service_rating=rating_data.service_rating,
            communication_rating=rating_data.communication_rating,
            overall_rating=overall_rating,
            delivery_status=rating_data.delivery_status,
            days_late=rating_data.days_late,
            defect_percentage=rating_data.defect_percentage,
            rejection_percentage=rating_data.rejection_percentage,
            positive_points=rating_data.positive_points,
            improvement_areas=rating_data.improvement_areas,
            remarks=rating_data.remarks,
            rated_by=self.user_id,
            rated_by_name=rated_by_name
        )
        
        self.db.add(rating)
        
        # Update vendor's average ratings
        await self._update_vendor_ratings(rating_data.vendor_id)
        
        await self.db.commit()
        await self.db.refresh(rating)
        
        return rating
    
    async def _update_vendor_ratings(self, vendor_id: uuid.UUID):
        """Update vendor's aggregate ratings"""
        vendor = await self.get_vendor(vendor_id)
        if not vendor:
            return
        
        # Calculate average ratings from all vendor ratings
        query = select(
            func.avg(VendorRating.overall_rating).label('avg_overall'),
            func.avg(VendorRating.quality_rating).label('avg_quality'),
            func.avg(VendorRating.delivery_rating).label('avg_delivery'),
            func.avg(VendorRating.price_rating).label('avg_price'),
            func.avg(VendorRating.service_rating).label('avg_service'),
            func.count(VendorRating.id).label('total_ratings')
        ).where(
            and_(
                VendorRating.vendor_id == vendor_id,
                VendorRating.tenant_id == self.tenant_id
            )
        )
        
        result = await self.db.execute(query)
        ratings = result.one()
        
        vendor.overall_rating = ratings.avg_overall or Decimal("0.00")
        vendor.quality_rating = ratings.avg_quality or Decimal("0.00")
        vendor.delivery_rating = ratings.avg_delivery or Decimal("0.00")
        vendor.price_rating = ratings.avg_price or Decimal("0.00")
        vendor.service_rating = ratings.avg_service or Decimal("0.00")
    
    async def get_vendor_ratings(
        self,
        vendor_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[VendorRating], int]:
        """Get vendor ratings"""
        conditions = [
            VendorRating.vendor_id == vendor_id,
            VendorRating.tenant_id == self.tenant_id
        ]
        
        # Count total
        count_query = select(func.count(VendorRating.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get ratings
        query = select(VendorRating).where(and_(*conditions)).order_by(
            desc(VendorRating.rating_date)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        ratings = result.scalars().all()
        
        return list(ratings), total
    
    async def get_vendor_performance_metrics(
        self,
        vendor_id: uuid.UUID
    ) -> VendorPerformanceMetrics:
        """Get vendor performance metrics"""
        vendor = await self.get_vendor(vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")
        
        # Calculate on-time delivery percentage
        on_time_percentage = Decimal("0.00")
        if vendor.total_orders > 0:
            on_time_percentage = (
                Decimal(vendor.on_time_deliveries) / Decimal(vendor.total_orders)
            ) * Decimal("100.0")
        
        return VendorPerformanceMetrics(
            vendor_id=vendor.id,
            vendor_name=vendor.vendor_name,
            total_orders=vendor.total_orders,
            on_time_deliveries=vendor.on_time_deliveries,
            on_time_percentage=on_time_percentage,
            average_rating=vendor.overall_rating,
            quality_rating=vendor.quality_rating,
            delivery_rating=vendor.delivery_rating,
            price_rating=vendor.price_rating,
            service_rating=vendor.service_rating
        )
    
    async def get_top_vendors(
        self,
        limit: int = 10,
        min_orders: int = 5
    ) -> List[Vendor]:
        """Get top-rated vendors with minimum orders"""
        query = select(Vendor).where(
            and_(
                Vendor.tenant_id == self.tenant_id,
                Vendor.status == VendorStatus.ACTIVE,
                Vendor.is_deleted == False,
                Vendor.total_orders >= min_orders
            )
        ).order_by(
            desc(Vendor.overall_rating),
            desc(Vendor.total_orders)
        ).limit(limit)
        
        result = await self.db.execute(query)
        vendors = result.scalars().all()
        
        return list(vendors)
    
    # ========================================================================
    # Vendor Statistics
    # ========================================================================
    
    async def get_vendor_statistics(self) -> dict:
        """Get vendor statistics for dashboard"""
        
        # Total vendors by status
        status_query = select(
            Vendor.status,
            func.count(Vendor.id).label('count')
        ).where(
            and_(
                Vendor.tenant_id == self.tenant_id,
                Vendor.is_deleted == False
            )
        ).group_by(Vendor.status)
        
        status_result = await self.db.execute(status_query)
        status_counts = {row.status: row.count for row in status_result}
        
        # Total vendors by type
        type_query = select(
            Vendor.vendor_type,
            func.count(Vendor.id).label('count')
        ).where(
            and_(
                Vendor.tenant_id == self.tenant_id,
                Vendor.is_deleted == False
            )
        ).group_by(Vendor.vendor_type)
        
        type_result = await self.db.execute(type_query)
        type_counts = {row.vendor_type: row.count for row in type_result}
        
        # Average ratings
        avg_query = select(
            func.avg(Vendor.overall_rating).label('avg_rating'),
            func.count(Vendor.id).label('total_vendors')
        ).where(
            and_(
                Vendor.tenant_id == self.tenant_id,
                Vendor.is_deleted == False,
                Vendor.total_orders > 0
            )
        )
        
        avg_result = await self.db.execute(avg_query)
        avg_data = avg_result.one()
        
        return {
            "total_vendors": sum(status_counts.values()),
            "by_status": status_counts,
            "by_type": type_counts,
            "average_rating": float(avg_data.avg_rating or 0),
            "rated_vendors": avg_data.total_vendors
        }
