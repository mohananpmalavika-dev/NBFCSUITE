"""
Product Lifecycle Management Router
API endpoints for product variants and sunset management
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auth import get_current_user, get_tenant_id
from .product_lifecycle_service import ProductLifecycleService
from .product_lifecycle_models import (
    ProductVariantCreate, ProductVariantUpdate, ProductVariantResponse,
    PromotionalProductSchema, SeasonalProductSchema,
    GeographySpecificProductSchema, SegmentSpecificProductSchema,
    ProductSunsetCreate, ProductSunsetUpdate, ProductSunsetResponse,
    VariantType, VariantStatus, Season, SunsetStatus, MigrationStatus
)

router = APIRouter(prefix="/api/product-lifecycle", tags=["Product Lifecycle"])


# =====================================================================
# PRODUCT VARIANT ENDPOINTS
# =====================================================================

@router.post("/variants", response_model=ProductVariantResponse)
def create_variant(
    variant_data: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Create new product variant"""
    service = ProductLifecycleService(db, tenant_id)
    return service.create_variant(variant_data, current_user.id)


@router.get("/variants", response_model=List[ProductVariantResponse])
def list_variants(
    base_product_id: Optional[UUID] = Query(None),
    variant_type: Optional[VariantType] = Query(None),
    status: Optional[VariantStatus] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """List product variants with filters"""
    service = ProductLifecycleService(db, tenant_id)
    return service.list_variants(base_product_id, variant_type, status, is_active, skip, limit)


@router.get("/variants/{variant_id}", response_model=ProductVariantResponse)
def get_variant(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get product variant by ID"""
    service = ProductLifecycleService(db, tenant_id)
    variant = service.get_variant(variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant


@router.put("/variants/{variant_id}", response_model=ProductVariantResponse)
def update_variant(
    variant_id: UUID,
    variant_data: ProductVariantUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Update product variant"""
    service = ProductLifecycleService(db, tenant_id)
    variant = service.update_variant(variant_id, variant_data, current_user.id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant


@router.post("/variants/{variant_id}/activate", response_model=ProductVariantResponse)
def activate_variant(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Activate product variant"""
    service = ProductLifecycleService(db, tenant_id)
    try:
        variant = service.activate_variant(variant_id, current_user.id)
        if not variant:
            raise HTTPException(status_code=404, detail="Variant not found")
        return variant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/variants/{variant_id}/deactivate", response_model=ProductVariantResponse)
def deactivate_variant(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Deactivate product variant"""
    service = ProductLifecycleService(db, tenant_id)
    variant = service.deactivate_variant(variant_id, current_user.id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant


@router.delete("/variants/{variant_id}")
def delete_variant(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Delete product variant"""
    service = ProductLifecycleService(db, tenant_id)
    try:
        success = service.delete_variant(variant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Variant not found")
        return {"message": "Variant deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/variants/{variant_id}/clone", response_model=ProductVariantResponse)
def clone_variant(
    variant_id: UUID,
    new_code: str,
    new_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Clone existing variant"""
    service = ProductLifecycleService(db, tenant_id)
    variant = service.clone_variant(variant_id, new_code, new_name, current_user.id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant


@router.get("/variants/{variant_id}/performance")
def get_variant_performance(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get variant performance metrics"""
    service = ProductLifecycleService(db, tenant_id)
    return service.get_variant_performance(variant_id)


# =====================================================================
# PROMOTIONAL PRODUCT ENDPOINTS
# =====================================================================

@router.post("/variants/{variant_id}/promotional")
def create_promotional_product(
    variant_id: UUID,
    promo_data: PromotionalProductSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Create promotional product configuration"""
    service = ProductLifecycleService(db, tenant_id)
    try:
        promo = service.create_promotional_product(variant_id, promo_data)
        return promo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/variants/{variant_id}/promotional")
def get_promotional_product(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get promotional product configuration"""
    service = ProductLifecycleService(db, tenant_id)
    promo = service.get_promotional_product(variant_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promotional configuration not found")
    return promo


@router.post("/variants/{variant_id}/promotional/check-eligibility")
def check_promotional_eligibility(
    variant_id: UUID,
    customer_id: UUID,
    loan_amount: float,
    credit_score: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Check promotional product eligibility"""
    service = ProductLifecycleService(db, tenant_id)
    return service.check_promotional_eligibility(variant_id, customer_id, loan_amount, credit_score)


# =====================================================================
# SEASONAL PRODUCT ENDPOINTS
# =====================================================================

@router.post("/variants/{variant_id}/seasonal")
def create_seasonal_product(
    variant_id: UUID,
    seasonal_data: SeasonalProductSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Create seasonal product configuration"""
    service = ProductLifecycleService(db, tenant_id)
    try:
        seasonal = service.create_seasonal_product(variant_id, seasonal_data)
        return seasonal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/variants/{variant_id}/seasonal")
def get_seasonal_product(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get seasonal product configuration"""
    service = ProductLifecycleService(db, tenant_id)
    seasonal = service.get_seasonal_product(variant_id)
    if not seasonal:
        raise HTTPException(status_code=404, detail="Seasonal configuration not found")
    return seasonal


@router.get("/seasonal/active")
def get_active_seasonal_products(
    season: Optional[Season] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get active seasonal products"""
    service = ProductLifecycleService(db, tenant_id)
    return service.get_active_seasonal_products(season)


# =====================================================================
# GEOGRAPHY-SPECIFIC PRODUCT ENDPOINTS
# =====================================================================


@router.post("/variants/{variant_id}/geography")
def create_geography_specific_product(
    variant_id: UUID,
    geo_data: GeographySpecificProductSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Create geography-specific product configuration"""
    service = ProductLifecycleService(db, tenant_id)
    try:
        geo_product = service.create_geography_specific_product(variant_id, geo_data)
        return geo_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/variants/{variant_id}/geography")
def get_geography_specific_product(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get geography-specific product configuration"""
    service = ProductLifecycleService(db, tenant_id)
    geo_product = service.get_geography_specific_product(variant_id)
    if not geo_product:
        raise HTTPException(status_code=404, detail="Geography configuration not found")
    return geo_product


@router.post("/variants/{variant_id}/geography/check-eligibility")
def check_geography_eligibility(
    variant_id: UUID,
    state: Optional[str] = None,
    city: Optional[str] = None,
    pincode: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Check geography eligibility"""
    service = ProductLifecycleService(db, tenant_id)
    return service.check_geography_eligibility(variant_id, state, city, pincode)


# =====================================================================
# SEGMENT-SPECIFIC PRODUCT ENDPOINTS
# =====================================================================

@router.post("/variants/{variant_id}/segment")
def create_segment_specific_product(
    variant_id: UUID,
    segment_data: SegmentSpecificProductSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Create segment-specific product configuration"""
    service = ProductLifecycleService(db, tenant_id)
    try:
        segment_product = service.create_segment_specific_product(variant_id, segment_data)
        return segment_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/variants/{variant_id}/segment")
def get_segment_specific_product(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get segment-specific product configuration"""
    service = ProductLifecycleService(db, tenant_id)
    segment_product = service.get_segment_specific_product(variant_id)
    if not segment_product:
        raise HTTPException(status_code=404, detail="Segment configuration not found")
    return segment_product


@router.post("/variants/{variant_id}/segment/check-eligibility")
def check_segment_eligibility(
    variant_id: UUID,
    customer_segment: str,
    age: Optional[int] = None,
    income: Optional[float] = None,
    employment_type: Optional[str] = None,
    industry: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Check segment eligibility"""
    service = ProductLifecycleService(db, tenant_id)
    return service.check_segment_eligibility(
        variant_id, customer_segment, age, income, employment_type, industry
    )


# =====================================================================
# VARIANT RECOMMENDATION ENDPOINTS
# =====================================================================

@router.post("/variants/recommend")
def recommend_variants(
    base_product_id: UUID,
    customer_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Recommend suitable variants for customer"""
    service = ProductLifecycleService(db, tenant_id)
    return service.recommend_variants(base_product_id, customer_data)


# =====================================================================
# PRODUCT SUNSET ENDPOINTS
# =====================================================================

@router.post("/sunsets", response_model=ProductSunsetResponse)
def create_product_sunset(
    sunset_data: ProductSunsetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Create product sunset plan"""
    service = ProductLifecycleService(db, tenant_id)
    try:
        return service.create_product_sunset(sunset_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sunsets", response_model=List[ProductSunsetResponse])
def list_product_sunsets(
    product_id: Optional[UUID] = Query(None),
    status: Optional[SunsetStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """List product sunsets with filters"""
    service = ProductLifecycleService(db, tenant_id)
    return service.list_product_sunsets(product_id, status, skip, limit)


@router.get("/sunsets/{sunset_id}", response_model=ProductSunsetResponse)
def get_product_sunset(
    sunset_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get product sunset by ID"""
    service = ProductLifecycleService(db, tenant_id)
    sunset = service.get_product_sunset(sunset_id)
    if not sunset:
        raise HTTPException(status_code=404, detail="Sunset plan not found")
    return sunset


@router.put("/sunsets/{sunset_id}", response_model=ProductSunsetResponse)
def update_product_sunset(
    sunset_id: UUID,
    sunset_data: ProductSunsetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Update product sunset"""
    service = ProductLifecycleService(db, tenant_id)
    sunset = service.update_product_sunset(sunset_id, sunset_data)
    if not sunset:
        raise HTTPException(status_code=404, detail="Sunset plan not found")
    return sunset


@router.post("/sunsets/{sunset_id}/announce", response_model=ProductSunsetResponse)
def announce_sunset(
    sunset_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Announce product sunset to customers"""
    service = ProductLifecycleService(db, tenant_id)
    sunset = service.announce_sunset(sunset_id)
    if not sunset:
        raise HTTPException(status_code=404, detail="Sunset plan not found")
    return sunset


@router.post("/sunsets/{sunset_id}/close-new-applications", response_model=ProductSunsetResponse)
def close_for_new_applications(
    sunset_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Close product for new applications"""
    service = ProductLifecycleService(db, tenant_id)
    sunset = service.close_for_new_applications(sunset_id)
    if not sunset:
        raise HTTPException(status_code=404, detail="Sunset plan not found")
    return sunset


@router.post("/sunsets/{sunset_id}/complete", response_model=ProductSunsetResponse)
def complete_sunset(
    sunset_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Complete product sunset"""
    service = ProductLifecycleService(db, tenant_id)
    sunset = service.complete_sunset(sunset_id)
    if not sunset:
        raise HTTPException(status_code=404, detail="Sunset plan not found")
    return sunset


@router.get("/sunsets/{sunset_id}/impact-assessment")
def get_sunset_impact_assessment(
    sunset_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get sunset impact assessment"""
    service = ProductLifecycleService(db, tenant_id)
    return service.get_sunset_impact_assessment(sunset_id)


# =====================================================================
# CUSTOMER MIGRATION ENDPOINTS
# =====================================================================

@router.post("/migrations")
def create_customer_migration(
    sunset_id: UUID,
    customer_id: UUID,
    old_account_id: UUID,
    from_product_id: UUID,
    to_product_id: UUID,
    migration_terms: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Create customer migration"""
    service = ProductLifecycleService(db, tenant_id)
    try:
        return service.create_customer_migration(
            sunset_id, customer_id, old_account_id,
            from_product_id, to_product_id, migration_terms
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/migrations")
def list_customer_migrations(
    sunset_id: Optional[UUID] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    migration_status: Optional[MigrationStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """List customer migrations"""
    service = ProductLifecycleService(db, tenant_id)
    return service.list_customer_migrations(sunset_id, customer_id, migration_status, skip, limit)


@router.get("/migrations/{migration_id}")
def get_customer_migration(
    migration_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get customer migration by ID"""
    service = ProductLifecycleService(db, tenant_id)
    migration = service.get_customer_migration(migration_id)
    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")
    return migration


@router.post("/migrations/{migration_id}/initiate")
def initiate_migration(
    migration_id: UUID,
    outstanding_balance: float,
    rate_benefit: Optional[float] = None,
    fee_waiver: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Initiate customer migration"""
    service = ProductLifecycleService(db, tenant_id)
    migration = service.initiate_migration(migration_id, outstanding_balance, rate_benefit, fee_waiver)
    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")
    return migration


@router.post("/migrations/{migration_id}/complete")
def complete_migration(
    migration_id: UUID,
    new_account_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Complete customer migration"""
    service = ProductLifecycleService(db, tenant_id)
    migration = service.complete_migration(migration_id, new_account_id, current_user.id)
    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")
    return migration



@router.post("/migrations/{migration_id}/decline")
def decline_migration(
    migration_id: UUID,
    decline_reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Decline customer migration"""
    service = ProductLifecycleService(db, tenant_id)
    migration = service.decline_migration(migration_id, decline_reason)
    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")
    return migration


@router.get("/migrations/statistics/{sunset_id}")
def get_migration_statistics(
    sunset_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get migration statistics for sunset"""
    service = ProductLifecycleService(db, tenant_id)
    return service.get_migration_statistics(sunset_id)


# =====================================================================
# ANALYTICS & DASHBOARD ENDPOINTS
# =====================================================================

@router.get("/dashboard")
def get_lifecycle_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    tenant_id: UUID = Depends(get_tenant_id)
):
    """Get product lifecycle dashboard metrics"""
    service = ProductLifecycleService(db, tenant_id)
    return service.get_lifecycle_dashboard()
