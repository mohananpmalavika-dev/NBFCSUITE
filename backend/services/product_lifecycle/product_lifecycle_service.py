"""
Product Lifecycle Management Service
Service for product variants, promotional products, seasonal products, and product sunset
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from .product_lifecycle_models import (
    ProductVariant, PromotionalProduct, SeasonalProduct,
    GeographySpecificProduct, SegmentSpecificProduct,
    ProductSunset, CustomerMigration,
    VariantType, VariantStatus, Season, CustomerSegment,
    SunsetStatus, MigrationStatus,
    ProductVariantCreate, ProductVariantUpdate,
    PromotionalProductSchema, SeasonalProductSchema,
    GeographySpecificProductSchema, SegmentSpecificProductSchema,
    ProductSunsetCreate, ProductSunsetUpdate
)


class ProductLifecycleService:
    """Service for product lifecycle management"""
    
    def __init__(self, db: Session, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
    
    # =====================================================================
    # PRODUCT VARIANT CRUD
    # =====================================================================
    
    def create_variant(
        self,
        variant_data: ProductVariantCreate,
        user_id: UUID
    ) -> ProductVariant:
        """Create new product variant"""
        variant = ProductVariant(
            tenant_id=self.tenant_id,
            **variant_data.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(variant)
        self.db.commit()
        self.db.refresh(variant)
        return variant
    
    def get_variant(self, variant_id: UUID) -> Optional[ProductVariant]:
        """Get product variant by ID"""
        return self.db.query(ProductVariant).filter(
            and_(
                ProductVariant.id == variant_id,
                ProductVariant.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_variants(
        self,
        base_product_id: Optional[UUID] = None,
        variant_type: Optional[VariantType] = None,
        status: Optional[VariantStatus] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductVariant]:
        """List product variants with filters"""
        query = self.db.query(ProductVariant).filter(
            ProductVariant.tenant_id == self.tenant_id
        )
        
        if base_product_id:
            query = query.filter(ProductVariant.base_product_id == base_product_id)
        if variant_type:
            query = query.filter(ProductVariant.variant_type == variant_type)
        if status:
            query = query.filter(ProductVariant.status == status)
        if is_active is not None:
            query = query.filter(ProductVariant.is_active == is_active)
        
        return query.order_by(
            ProductVariant.priority.desc(),
            ProductVariant.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def update_variant(
        self,
        variant_id: UUID,
        variant_data: ProductVariantUpdate,
        user_id: UUID
    ) -> Optional[ProductVariant]:
        """Update product variant"""
        variant = self.get_variant(variant_id)
        if not variant:
            return None
        
        update_data = variant_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(variant, field, value)
        
        variant.updated_by = user_id
        variant.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(variant)
        return variant
    
    def activate_variant(self, variant_id: UUID, user_id: UUID) -> Optional[ProductVariant]:
        """Activate product variant"""
        variant = self.get_variant(variant_id)
        if not variant:
            return None
        
        # Check if valid_from is in the past or today
        if variant.valid_from > date.today():
            raise ValueError("Cannot activate variant before valid_from date")
        
        variant.is_active = True
        variant.status = VariantStatus.ACTIVE
        variant.updated_by = user_id
        variant.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(variant)
        return variant
    
    def deactivate_variant(self, variant_id: UUID, user_id: UUID) -> Optional[ProductVariant]:
        """Deactivate product variant"""
        variant = self.get_variant(variant_id)
        if not variant:
            return None
        
        variant.is_active = False
        variant.status = VariantStatus.INACTIVE
        variant.updated_by = user_id
        variant.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(variant)
        return variant
    
    def delete_variant(self, variant_id: UUID) -> bool:
        """Delete product variant"""
        variant = self.get_variant(variant_id)
        if not variant:
            return False
        
        # Check if variant has applications
        if variant.application_count > 0:
            raise ValueError("Cannot delete variant with applications. Deactivate instead.")
        
        self.db.delete(variant)
        self.db.commit()
        return True
    
    def clone_variant(
        self,
        variant_id: UUID,
        new_code: str,
        new_name: str,
        user_id: UUID
    ) -> Optional[ProductVariant]:
        """Clone an existing variant"""
        original = self.get_variant(variant_id)
        if not original:
            return None
        
        # Create new variant with same configuration
        new_variant = ProductVariant(
            tenant_id=self.tenant_id,
            base_product_id=original.base_product_id,
            variant_code=new_code,
            variant_name=new_name,
            variant_type=original.variant_type,
            description=f"Cloned from {original.variant_name}",
            status=VariantStatus.DRAFT,
            is_active=False,
            valid_from=date.today(),
            valid_to=original.valid_to,
            interest_rate_override=original.interest_rate_override,
            tenure_override=original.tenure_override,
            amount_override=original.amount_override,
            fee_override=original.fee_override,
            eligibility_override=original.eligibility_override,
            priority=original.priority,
            marketing_name=original.marketing_name,
            tagline=original.tagline,
            promotional_message=original.promotional_message,
            terms_and_conditions=original.terms_and_conditions,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(new_variant)
        self.db.commit()
        self.db.refresh(new_variant)
        return new_variant
    
    # =====================================================================
    # PROMOTIONAL PRODUCT MANAGEMENT
    # =====================================================================
    
    def create_promotional_product(
        self,
        variant_id: UUID,
        promo_data: PromotionalProductSchema
    ) -> PromotionalProduct:
        """Create promotional product configuration"""
        # Check if variant exists
        variant = self.get_variant(variant_id)
        if not variant:
            raise ValueError("Variant not found")
        
        # Create promotional config
        promo = PromotionalProduct(
            variant_id=variant_id,
            tenant_id=self.tenant_id,
            **promo_data.dict()
        )
        
        self.db.add(promo)
        self.db.commit()
        self.db.refresh(promo)
        return promo
    
    def get_promotional_product(self, variant_id: UUID) -> Optional[PromotionalProduct]:
        """Get promotional product configuration"""
        return self.db.query(PromotionalProduct).filter(
            and_(
                PromotionalProduct.variant_id == variant_id,
                PromotionalProduct.tenant_id == self.tenant_id
            )
        ).first()
    
    def check_promotional_eligibility(
        self,
        variant_id: UUID,
        customer_id: UUID,
        loan_amount: float,
        credit_score: Optional[int] = None
    ) -> Dict[str, Any]:
        """Check if customer is eligible for promotional product"""
        promo = self.get_promotional_product(variant_id)
        if not promo:
            return {"eligible": False, "reason": "No promotional configuration found"}
        
        # Check if promotion is active
        today = date.today()
        if today < promo.promotion_start_date or today > promo.promotion_end_date:
            return {"eligible": False, "reason": "Promotion not active"}
        
        # Check max applications limit
        if promo.max_applications and promo.current_applications >= promo.max_applications:
            return {"eligible": False, "reason": "Promotion limit reached"}
        
        # Check max disbursement amount
        if promo.max_disbursement_amount and \
           promo.current_disbursement_amount >= promo.max_disbursement_amount:
            return {"eligible": False, "reason": "Promotion disbursement limit reached"}
        
        # Check credit score requirement
        if promo.min_credit_score and credit_score and credit_score < promo.min_credit_score:
            return {"eligible": False, "reason": f"Credit score below {promo.min_credit_score}"}
        
        # Check min loan amount
        if promo.min_loan_amount and loan_amount < promo.min_loan_amount:
            return {"eligible": False, "reason": f"Loan amount below minimum {promo.min_loan_amount}"}
        
        # Check applications per customer (would query actual data in production)
        # For now, assume eligible
        
        return {
            "eligible": True,
            "benefits": {
                "rate_discount": promo.special_rate_discount,
                "fee_waiver": promo.fee_waiver,
                "cashback_amount": promo.cashback_amount,
                "cashback_percentage": promo.cashback_percentage
            },
            "promotion_name": promo.promotion_name,
            "valid_until": promo.promotion_end_date.isoformat()
        }
    
    # =====================================================================
    # SEASONAL PRODUCT MANAGEMENT
    # =====================================================================
    
    def create_seasonal_product(
        self,
        variant_id: UUID,
        seasonal_data: SeasonalProductSchema
    ) -> SeasonalProduct:
        """Create seasonal product configuration"""
        variant = self.get_variant(variant_id)
        if not variant:
            raise ValueError("Variant not found")
        
        seasonal = SeasonalProduct(
            variant_id=variant_id,
            tenant_id=self.tenant_id,
            **seasonal_data.dict()
        )
        
        self.db.add(seasonal)
        self.db.commit()
        self.db.refresh(seasonal)
        return seasonal
    
    def get_seasonal_product(self, variant_id: UUID) -> Optional[SeasonalProduct]:
        """Get seasonal product configuration"""
        return self.db.query(SeasonalProduct).filter(
            and_(
                SeasonalProduct.variant_id == variant_id,
                SeasonalProduct.tenant_id == self.tenant_id
            )
        ).first()
    
    def get_active_seasonal_products(
        self,
        season: Optional[Season] = None
    ) -> List[SeasonalProduct]:
        """Get active seasonal products"""
        today = date.today()
        query = self.db.query(SeasonalProduct).filter(
            and_(
                SeasonalProduct.tenant_id == self.tenant_id,
                SeasonalProduct.season_start_date <= today,
                SeasonalProduct.season_end_date >= today
            )
        )
        
        if season:
            query = query.filter(SeasonalProduct.season == season)
        
        return query.all()
    
    # =====================================================================
    # GEOGRAPHY-SPECIFIC PRODUCT MANAGEMENT
    # =====================================================================
    
    def create_geography_specific_product(
        self,
        variant_id: UUID,
        geo_data: GeographySpecificProductSchema
    ) -> GeographySpecificProduct:
        """Create geography-specific product configuration"""
        variant = self.get_variant(variant_id)
        if not variant:
            raise ValueError("Variant not found")
        
        geo_product = GeographySpecificProduct(
            variant_id=variant_id,
            tenant_id=self.tenant_id,
            **geo_data.dict()
        )
        
        self.db.add(geo_product)
        self.db.commit()
        self.db.refresh(geo_product)
        return geo_product
    
    def get_geography_specific_product(self, variant_id: UUID) -> Optional[GeographySpecificProduct]:
        """Get geography-specific product configuration"""
        return self.db.query(GeographySpecificProduct).filter(
            and_(
                GeographySpecificProduct.variant_id == variant_id,
                GeographySpecificProduct.tenant_id == self.tenant_id
            )
        ).first()
    
    def check_geography_eligibility(
        self,
        variant_id: UUID,
        state: Optional[str] = None,
        city: Optional[str] = None,
        pincode: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check if geography is eligible for variant"""
        geo_product = self.get_geography_specific_product(variant_id)
        if not geo_product:
            return {"eligible": True, "reason": "No geography restrictions"}
        
        # Check allowed states
        if geo_product.allowed_states and state:
            if state not in geo_product.allowed_states:
                return {"eligible": False, "reason": f"State {state} not allowed"}
        
        # Check allowed cities
        if geo_product.allowed_cities and city:
            if city not in geo_product.allowed_cities:
                return {"eligible": False, "reason": f"City {city} not allowed"}
        
        # Check allowed pincodes
        if geo_product.allowed_pincodes and pincode:
            if pincode not in geo_product.allowed_pincodes:
                return {"eligible": False, "reason": f"Pincode {pincode} not allowed"}
        
        # Check excluded areas
        if geo_product.excluded_areas:
            if state in geo_product.excluded_areas or \
               city in geo_product.excluded_areas or \
               pincode in geo_product.excluded_areas:
                return {"eligible": False, "reason": "Area is excluded"}
        
        return {
            "eligible": True,
            "adjustments": {
                "rate_adjustment": geo_product.regional_rate_adjustment,
                "amount_adjustment": geo_product.regional_amount_adjustment,
                "ltv_adjustment": geo_product.regional_ltv_adjustment
            },
            "requires_local_verification": geo_product.requires_local_verification
        }
    
    # =====================================================================
    # SEGMENT-SPECIFIC PRODUCT MANAGEMENT
    # =====================================================================
    
    def create_segment_specific_product(
        self,
        variant_id: UUID,
        segment_data: SegmentSpecificProductSchema
    ) -> SegmentSpecificProduct:
        """Create segment-specific product configuration"""
        variant = self.get_variant(variant_id)
        if not variant:
            raise ValueError("Variant not found")
        
        segment_product = SegmentSpecificProduct(
            variant_id=variant_id,
            tenant_id=self.tenant_id,
            **segment_data.dict()
        )
        
        self.db.add(segment_product)
        self.db.commit()
        self.db.refresh(segment_product)
        return segment_product
    
    def get_segment_specific_product(self, variant_id: UUID) -> Optional[SegmentSpecificProduct]:
        """Get segment-specific product configuration"""
        return self.db.query(SegmentSpecificProduct).filter(
            and_(
                SegmentSpecificProduct.variant_id == variant_id,
                SegmentSpecificProduct.tenant_id == self.tenant_id
            )
        ).first()
    
    def check_segment_eligibility(
        self,
        variant_id: UUID,
        customer_segment: str,
        age: Optional[int] = None,
        income: Optional[float] = None,
        employment_type: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check if customer segment is eligible for variant"""
        segment_product = self.get_segment_specific_product(variant_id)
        if not segment_product:
            return {"eligible": True, "reason": "No segment restrictions"}
        
        # Check target segments
        if customer_segment not in segment_product.target_segments:
            return {"eligible": False, "reason": f"Segment {customer_segment} not targeted"}
        
        # Check age range
        if segment_product.min_age and age and age < segment_product.min_age:
            return {"eligible": False, "reason": f"Age below minimum {segment_product.min_age}"}
        if segment_product.max_age and age and age > segment_product.max_age:
            return {"eligible": False, "reason": f"Age above maximum {segment_product.max_age}"}
        
        # Check income range
        if segment_product.min_income and income and income < segment_product.min_income:
            return {"eligible": False, "reason": f"Income below minimum"}
        if segment_product.max_income and income and income > segment_product.max_income:
            return {"eligible": False, "reason": f"Income above maximum"}
        
        # Check employment type
        if segment_product.employment_types and employment_type:
            if employment_type not in segment_product.employment_types:
                return {"eligible": False, "reason": f"Employment type {employment_type} not allowed"}
        
        # Check industry
        if segment_product.allowed_industries and industry:
            if industry not in segment_product.allowed_industries:
                return {"eligible": False, "reason": f"Industry {industry} not allowed"}
        
        if segment_product.excluded_industries and industry:
            if industry in segment_product.excluded_industries:
                return {"eligible": False, "reason": f"Industry {industry} is excluded"}
        
        # Check segment exposure limit
        if segment_product.max_segment_exposure:
            if segment_product.current_segment_exposure >= segment_product.max_segment_exposure:
                return {"eligible": False, "reason": "Segment exposure limit reached"}
        
        return {
            "eligible": True,
            "benefits": {
                "rate_benefit": segment_product.segment_rate_benefit,
                "fee_waiver": segment_product.segment_fee_waiver,
                "priority_processing": segment_product.priority_processing,
                "dedicated_rm": segment_product.dedicated_relationship_manager
            },
            "special_features": segment_product.special_features,
            "loyalty_benefits": segment_product.loyalty_benefits
        }
    
    # =====================================================================
    # PRODUCT SUNSET MANAGEMENT
    # =====================================================================
    
    def create_product_sunset(
        self,
        sunset_data: ProductSunsetCreate,
        user_id: UUID
    ) -> ProductSunset:
        """Create product sunset/discontinuation plan"""
        # Validate dates
        if sunset_data.no_new_applications_date < sunset_data.announcement_date:
            raise ValueError("No new applications date must be after announcement date")
        
        sunset = ProductSunset(
            tenant_id=self.tenant_id,
            **sunset_data.dict(),
            created_by=user_id,
            sunset_status=SunsetStatus.ANNOUNCED
        )
        
        self.db.add(sunset)
        self.db.commit()
        self.db.refresh(sunset)
        return sunset
    
    def get_product_sunset(self, sunset_id: UUID) -> Optional[ProductSunset]:
        """Get product sunset by ID"""
        return self.db.query(ProductSunset).filter(
            and_(
                ProductSunset.id == sunset_id,
                ProductSunset.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_product_sunsets(
        self,
        product_id: Optional[UUID] = None,
        status: Optional[SunsetStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductSunset]:
        """List product sunsets with filters"""
        query = self.db.query(ProductSunset).filter(
            ProductSunset.tenant_id == self.tenant_id
        )
        
        if product_id:
            query = query.filter(ProductSunset.product_id == product_id)
        if status:
            query = query.filter(ProductSunset.sunset_status == status)
        
        return query.order_by(ProductSunset.announcement_date.desc()).offset(skip).limit(limit).all()
    
    def update_product_sunset(
        self,
        sunset_id: UUID,
        sunset_data: ProductSunsetUpdate
    ) -> Optional[ProductSunset]:
        """Update product sunset"""
        sunset = self.get_product_sunset(sunset_id)
        if not sunset:
            return None
        
        update_data = sunset_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sunset, field, value)
        
        sunset.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(sunset)
        return sunset
    
    def announce_sunset(self, sunset_id: UUID) -> Optional[ProductSunset]:
        """Announce product sunset to customers"""
        sunset = self.get_product_sunset(sunset_id)
        if not sunset:
            return None
        
        sunset.sunset_status = SunsetStatus.ANNOUNCED
        sunset.customer_notification_sent = True
        sunset.notification_date = date.today()
        sunset.updated_at = datetime.utcnow()
        
        # In production, trigger customer notifications here
        # (email, SMS, in-app notifications, etc.)
        
        self.db.commit()
        self.db.refresh(sunset)
        return sunset
    
    def close_for_new_applications(self, sunset_id: UUID) -> Optional[ProductSunset]:
        """Close product for new applications"""
        sunset = self.get_product_sunset(sunset_id)
        if not sunset:
            return None
        
        sunset.sunset_status = SunsetStatus.NO_NEW_APPLICATIONS
        sunset.updated_at = datetime.utcnow()
        
        # In production, disable the product for new applications
        
        self.db.commit()
        self.db.refresh(sunset)
        return sunset
    
    def complete_sunset(self, sunset_id: UUID) -> Optional[ProductSunset]:
        """Mark product sunset as complete"""
        sunset = self.get_product_sunset(sunset_id)
        if not sunset:
            return None
        
        sunset.sunset_status = SunsetStatus.FULLY_DISCONTINUED
        sunset.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(sunset)
        return sunset
    
    def get_sunset_impact_assessment(self, sunset_id: UUID) -> Dict[str, Any]:
        """Get impact assessment for product sunset"""
        sunset = self.get_product_sunset(sunset_id)
        if not sunset:
            return {}
        
        # In production, these would query actual loan/application data
        assessment = {
            "sunset_id": str(sunset.id),
            "product_id": str(sunset.product_id),
            "sunset_status": sunset.sunset_status.value,
            "timeline": {
                "announcement_date": sunset.announcement_date.isoformat(),
                "no_new_applications_date": sunset.no_new_applications_date.isoformat(),
                "existing_customers_cutoff_date": sunset.existing_customers_cutoff_date.isoformat() if sunset.existing_customers_cutoff_date else None,
                "full_discontinuation_date": sunset.full_discontinuation_date.isoformat() if sunset.full_discontinuation_date else None
            },
            "impact": {
                "total_active_accounts": sunset.total_active_accounts,
                "total_outstanding_amount": sunset.total_outstanding_amount,
                "applications_in_pipeline": sunset.applications_in_pipeline
            },
            "migration": {
                "has_migration_plan": sunset.has_migration_plan,
                "target_product_id": str(sunset.target_product_id) if sunset.target_product_id else None,
                "customers_notified": sunset.customers_notified,
                "customers_migrated": sunset.customers_migrated,
                "customers_remaining": sunset.customers_remaining,
                "migration_deadline": sunset.migration_deadline.isoformat() if sunset.migration_deadline else None
            },
            "grandfathering": {
                "grandfather_existing": sunset.grandfather_existing_customers,
                "grandfather_pipeline": sunset.grandfather_in_pipeline,
                "pipeline_cutoff_stage": sunset.pipeline_cutoff_stage
            }
        }
        
        return assessment
    
    # =====================================================================
    # CUSTOMER MIGRATION MANAGEMENT
    # =====================================================================
    
    def create_customer_migration(
        self,
        sunset_id: UUID,
        customer_id: UUID,
        old_account_id: UUID,
        from_product_id: UUID,
        to_product_id: UUID,
        migration_terms: Optional[Dict[str, Any]] = None
    ) -> CustomerMigration:
        """Create customer migration record"""
        sunset = self.get_product_sunset(sunset_id)
        if not sunset:
            raise ValueError("Sunset plan not found")
        
        migration = CustomerMigration(
            sunset_id=sunset_id,
            tenant_id=self.tenant_id,
            customer_id=customer_id,
            old_account_id=old_account_id,
            from_product_id=from_product_id,
            to_product_id=to_product_id,
            eligible_from=date.today(),
            migration_deadline=sunset.migration_deadline,
            migration_terms=migration_terms,
            migration_status=MigrationStatus.NOT_STARTED
        )
        
        self.db.add(migration)
        self.db.commit()
        self.db.refresh(migration)
        return migration
    
    def get_customer_migration(self, migration_id: UUID) -> Optional[CustomerMigration]:
        """Get customer migration by ID"""
        return self.db.query(CustomerMigration).filter(
            and_(
                CustomerMigration.id == migration_id,
                CustomerMigration.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_customer_migrations(
        self,
        sunset_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        migration_status: Optional[MigrationStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CustomerMigration]:
        """List customer migrations with filters"""
        query = self.db.query(CustomerMigration).filter(
            CustomerMigration.tenant_id == self.tenant_id
        )
        
        if sunset_id:
            query = query.filter(CustomerMigration.sunset_id == sunset_id)
        if customer_id:
            query = query.filter(CustomerMigration.customer_id == customer_id)
        if migration_status:
            query = query.filter(CustomerMigration.migration_status == migration_status)
        
        return query.order_by(CustomerMigration.created_at.desc()).offset(skip).limit(limit).all()
    
    def initiate_migration(
        self,
        migration_id: UUID,
        outstanding_balance: float,
        rate_benefit: Optional[float] = None,
        fee_waiver: Optional[Dict[str, float]] = None
    ) -> Optional[CustomerMigration]:
        """Initiate customer migration process"""
        migration = self.get_customer_migration(migration_id)
        if not migration:
            return None
        
        migration.migration_status = MigrationStatus.IN_PROGRESS
        migration.outstanding_balance = outstanding_balance
        migration.customer_contacted_date = date.today()
        migration.rate_benefit_offered = rate_benefit
        migration.fee_waiver_offered = fee_waiver
        migration.updated_at = datetime.utcnow()
        
        # In production, trigger customer communication here
        
        self.db.commit()
        self.db.refresh(migration)
        return migration
    
    def complete_migration(
        self,
        migration_id: UUID,
        new_account_id: UUID,
        approved_by: UUID
    ) -> Optional[CustomerMigration]:
        """Complete customer migration"""
        migration = self.get_customer_migration(migration_id)
        if not migration:
            return None
        
        migration.migration_status = MigrationStatus.MIGRATED
        migration.new_account_id = new_account_id
        migration.migration_completed_date = date.today()
        migration.customer_accepted_terms = True
        migration.migration_approved_by = approved_by
        migration.approval_date = date.today()
        migration.updated_at = datetime.utcnow()
        
        # Update sunset statistics
        sunset = self.get_product_sunset(migration.sunset_id)
        if sunset:
            sunset.customers_migrated += 1
            sunset.customers_remaining = max(0, sunset.customers_remaining - 1)
        
        self.db.commit()
        self.db.refresh(migration)
        return migration
    
    def decline_migration(
        self,
        migration_id: UUID,
        decline_reason: str
    ) -> Optional[CustomerMigration]:
        """Mark migration as declined by customer"""
        migration = self.get_customer_migration(migration_id)
        if not migration:
            return None
        
        migration.migration_status = MigrationStatus.DECLINED
        migration.decline_reason = decline_reason
        migration.customer_accepted_terms = False
        migration.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(migration)
        return migration
    
    def get_migration_statistics(self, sunset_id: UUID) -> Dict[str, Any]:
        """Get migration statistics for a sunset plan"""
        migrations = self.list_customer_migrations(sunset_id=sunset_id, limit=10000)
        
        stats = {
            "total_customers": len(migrations),
            "by_status": {
                "not_started": len([m for m in migrations if m.migration_status == MigrationStatus.NOT_STARTED]),
                "in_progress": len([m for m in migrations if m.migration_status == MigrationStatus.IN_PROGRESS]),
                "migrated": len([m for m in migrations if m.migration_status == MigrationStatus.MIGRATED]),
                "declined": len([m for m in migrations if m.migration_status == MigrationStatus.DECLINED]),
                "failed": len([m for m in migrations if m.migration_status == MigrationStatus.FAILED])
            },
            "completion_rate": 0.0,
            "decline_rate": 0.0
        }
        
        if stats["total_customers"] > 0:
            stats["completion_rate"] = (stats["by_status"]["migrated"] / stats["total_customers"]) * 100
            stats["decline_rate"] = (stats["by_status"]["declined"] / stats["total_customers"]) * 100
        
        return stats
    
    # =====================================================================
    # VARIANT RECOMMENDATION ENGINE
    # =====================================================================
    
    def recommend_variants(
        self,
        base_product_id: UUID,
        customer_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend suitable product variants for customer"""
        # Get all active variants for the base product
        variants = self.list_variants(
            base_product_id=base_product_id,
            is_active=True
        )
        
        recommendations = []
        
        for variant in variants:
            score = 0
            eligibility_reasons = []
            benefits = []
            
            # Check validity period
            today = date.today()
            if variant.valid_from > today or (variant.valid_to and variant.valid_to < today):
                continue
            
            # Check promotional eligibility
            if variant.variant_type == VariantType.PROMOTIONAL:
                promo_check = self.check_promotional_eligibility(
                    variant.id,
                    customer_data.get("customer_id"),
                    customer_data.get("loan_amount", 0),
                    customer_data.get("credit_score")
                )
                if not promo_check["eligible"]:
                    continue
                score += 10
                benefits.extend([
                    f"Rate discount: {promo_check['benefits']['rate_discount']}%" if promo_check['benefits'].get('rate_discount') else None,
                    f"Cashback: ₹{promo_check['benefits']['cashback_amount']}" if promo_check['benefits'].get('cashback_amount') else None
                ])
                eligibility_reasons.append("Promotional offer")
            
            # Check geography eligibility
            if variant.variant_type == VariantType.GEOGRAPHY_SPECIFIC:
                geo_check = self.check_geography_eligibility(
                    variant.id,
                    customer_data.get("state"),
                    customer_data.get("city"),
                    customer_data.get("pincode")
                )
                if not geo_check["eligible"]:
                    continue
                score += 5
                if geo_check.get("adjustments", {}).get("rate_adjustment"):
                    benefits.append(f"Regional rate adjustment: {geo_check['adjustments']['rate_adjustment']}%")
                eligibility_reasons.append("Geography-specific")
            
            # Check segment eligibility
            if variant.variant_type == VariantType.SEGMENT_SPECIFIC:
                segment_check = self.check_segment_eligibility(
                    variant.id,
                    customer_data.get("customer_segment", "RETAIL"),
                    customer_data.get("age"),
                    customer_data.get("income"),
                    customer_data.get("employment_type"),
                    customer_data.get("industry")
                )
                if not segment_check["eligible"]:
                    continue
                score += 8
                if segment_check.get("benefits", {}).get("rate_benefit"):
                    benefits.append(f"Segment benefit: {segment_check['benefits']['rate_benefit']}%")
                if segment_check.get("benefits", {}).get("priority_processing"):
                    benefits.append("Priority processing")
                eligibility_reasons.append("Segment-specific")
            
            # Check seasonal eligibility
            if variant.variant_type == VariantType.SEASONAL:
                seasonal = self.get_seasonal_product(variant.id)
                if seasonal:
                    if seasonal.season_start_date <= today <= seasonal.season_end_date:
                        score += 7
                        if seasonal.festive_bonus:
                            benefits.append(f"Festive bonus: ₹{seasonal.festive_bonus}")
                        if seasonal.holiday_moratorium:
                            benefits.append(f"EMI holiday: {seasonal.moratorium_months} months")
                        eligibility_reasons.append(f"Seasonal offer ({seasonal.season.value})")
                    else:
                        continue
            
            # Priority boost
            score += variant.priority
            
            # Filter benefits (remove None values)
            benefits = [b for b in benefits if b]
            
            recommendations.append({
                "variant_id": str(variant.id),
                "variant_code": variant.variant_code,
                "variant_name": variant.variant_name,
                "variant_type": variant.variant_type.value,
                "marketing_name": variant.marketing_name,
                "tagline": variant.tagline,
                "score": score,
                "benefits": benefits,
                "eligibility_reasons": eligibility_reasons,
                "interest_rate_override": variant.interest_rate_override,
                "amount_override": variant.amount_override,
                "tenure_override": variant.tenure_override
            })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    
    # =====================================================================
    # ANALYTICS & REPORTING
    # =====================================================================
    
    def get_variant_performance(self, variant_id: UUID) -> Dict[str, Any]:
        """Get performance metrics for a variant"""
        variant = self.get_variant(variant_id)
        if not variant:
            return {}
        
        performance = {
            "variant_id": str(variant.id),
            "variant_code": variant.variant_code,
            "variant_name": variant.variant_name,
            "status": variant.status.value,
            "is_active": variant.is_active,
            "validity": {
                "valid_from": variant.valid_from.isoformat(),
                "valid_to": variant.valid_to.isoformat() if variant.valid_to else None,
                "days_active": (date.today() - variant.valid_from).days if variant.is_active else 0
            },
            "usage": {
                "application_count": variant.application_count,
                "disbursement_count": variant.disbursement_count,
                "total_disbursed_amount": variant.total_disbursed_amount,
                "conversion_rate": (variant.disbursement_count / variant.application_count * 100) if variant.application_count > 0 else 0,
                "average_disbursement": variant.total_disbursed_amount / variant.disbursement_count if variant.disbursement_count > 0 else 0
            }
        }
        
        # Add variant-specific metrics
        if variant.variant_type == VariantType.PROMOTIONAL:
            promo = self.get_promotional_product(variant.id)
            if promo:
                performance["promotional"] = {
                    "promotion_name": promo.promotion_name,
                    "current_applications": promo.current_applications,
                    "max_applications": promo.max_applications,
                    "utilization_rate": (promo.current_applications / promo.max_applications * 100) if promo.max_applications else 0,
                    "current_disbursement": promo.current_disbursement_amount,
                    "max_disbursement": promo.max_disbursement_amount
                }
        
        return performance
    
    def get_lifecycle_dashboard(self) -> Dict[str, Any]:
        """Get overall product lifecycle dashboard metrics"""
        # Get all variants
        all_variants = self.list_variants(limit=10000)
        
        # Get all sunsets
        all_sunsets = self.list_product_sunsets(limit=10000)
        
        dashboard = {
            "variants": {
                "total": len(all_variants),
                "active": len([v for v in all_variants if v.is_active]),
                "by_type": {
                    "standard": len([v for v in all_variants if v.variant_type == VariantType.STANDARD]),
                    "promotional": len([v for v in all_variants if v.variant_type == VariantType.PROMOTIONAL]),
                    "seasonal": len([v for v in all_variants if v.variant_type == VariantType.SEASONAL]),
                    "geography_specific": len([v for v in all_variants if v.variant_type == VariantType.GEOGRAPHY_SPECIFIC]),
                    "segment_specific": len([v for v in all_variants if v.variant_type == VariantType.SEGMENT_SPECIFIC])
                },
                "by_status": {
                    "draft": len([v for v in all_variants if v.status == VariantStatus.DRAFT]),
                    "active": len([v for v in all_variants if v.status == VariantStatus.ACTIVE]),
                    "inactive": len([v for v in all_variants if v.status == VariantStatus.INACTIVE]),
                    "expired": len([v for v in all_variants if v.status == VariantStatus.EXPIRED])
                },
                "total_applications": sum(v.application_count for v in all_variants),
                "total_disbursements": sum(v.disbursement_count for v in all_variants),
                "total_disbursed_amount": sum(v.total_disbursed_amount for v in all_variants)
            },
            "sunsets": {
                "total": len(all_sunsets),
                "by_status": {
                    "announced": len([s for s in all_sunsets if s.sunset_status == SunsetStatus.ANNOUNCED]),
                    "no_new_applications": len([s for s in all_sunsets if s.sunset_status == SunsetStatus.NO_NEW_APPLICATIONS]),
                    "grandfathered_only": len([s for s in all_sunsets if s.sunset_status == SunsetStatus.GRANDFATHERED_ONLY]),
                    "fully_discontinued": len([s for s in all_sunsets if s.sunset_status == SunsetStatus.FULLY_DISCONTINUED])
                },
                "total_affected_accounts": sum(s.total_active_accounts for s in all_sunsets),
                "total_outstanding": sum(s.total_outstanding_amount for s in all_sunsets),
                "total_migrations": sum(s.customers_migrated for s in all_sunsets)
            }
        }
        
        return dashboard
