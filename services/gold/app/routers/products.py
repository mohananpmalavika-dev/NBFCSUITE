"""
Gold Product Configuration API
Phase 1: Product Engine
"""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from ..models.product import (
    GoldProduct,
    GoldProductInterest,
    GoldProductTenure,
    GoldProductLimits,
    GoldProductCharge,
    GoldProductDocument,
    GoldProductEligibility,
    GoldProductWorkflow,
    GoldProductChannel,
    GoldProductTax
)
from ..schemas.product import (
    GoldProductCreate,
    GoldProductUpdate,
    GoldProductResponse,
    GoldProductSummary,
    InterestConfig,
    TenureConfig,
    LimitsConfig,
    ChargeConfig,
    DocumentConfig,
    EligibilityRule,
    WorkflowStage,
    ChannelConfig,
    TaxConfig,
    InterestConfigResponse,
    TenureConfigResponse,
    LimitsConfigResponse,
    ChargeConfigResponse,
    DocumentConfigResponse,
    EligibilityRuleResponse,
    WorkflowStageResponse,
    ChannelConfigResponse,
    TaxConfigResponse
)

router = APIRouter(prefix="/products", tags=["Gold Products"])


def get_db():
    """Placeholder for database session - will be injected"""
    pass


@router.post("", response_model=GoldProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: GoldProductCreate, db: Session = Depends(get_db)):
    """
    Create a new gold loan product with complete configuration.
    
    This endpoint allows creating a product with all related configurations
    (interest, tenure, limits, charges, documents, eligibility, workflow, channels, taxes)
    in a single API call.
    """
    # Check for duplicate product code
    existing = db.query(GoldProduct).filter(GoldProduct.product_code == product_data.product_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product code '{product_data.product_code}' already exists"
        )
    
    # Create main product
    product = GoldProduct(
        id=str(uuid4()),
        product_code=product_data.product_code,
        product_name=product_data.product_name,
        product_type=product_data.product_type,
        description=product_data.description,
        is_active=product_data.is_active,
        display_order=product_data.display_order,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(product)
    db.flush()  # Get the product ID
    
    # Create interest configuration
    if product_data.interest:
        interest = GoldProductInterest(
            id=str(uuid4()),
            product_id=product.id,
            **product_data.interest.model_dump()
        )
        db.add(interest)
    
    # Create tenure configuration
    if product_data.tenure:
        tenure = GoldProductTenure(
            id=str(uuid4()),
            product_id=product.id,
            **product_data.tenure.model_dump()
        )
        db.add(tenure)
    
    # Create limits configuration
    if product_data.limits:
        limits = GoldProductLimits(
            id=str(uuid4()),
            product_id=product.id,
            **product_data.limits.model_dump()
        )
        db.add(limits)
    
    # Create charges
    if product_data.charges:
        for charge_data in product_data.charges:
            charge = GoldProductCharge(
                id=str(uuid4()),
                product_id=product.id,
                **charge_data.model_dump()
            )
            db.add(charge)
    
    # Create documents
    if product_data.documents:
        for doc_data in product_data.documents:
            document = GoldProductDocument(
                id=str(uuid4()),
                product_id=product.id,
                **doc_data.model_dump()
            )
            db.add(document)
    
    # Create eligibility rules
    if product_data.eligibility:
        for rule_data in product_data.eligibility:
            rule = GoldProductEligibility(
                id=str(uuid4()),
                product_id=product.id,
                **rule_data.model_dump()
            )
            db.add(rule)
    
    # Create workflow stages
    if product_data.workflow:
        for stage_data in product_data.workflow:
            stage = GoldProductWorkflow(
                id=str(uuid4()),
                product_id=product.id,
                **stage_data.model_dump()
            )
            db.add(stage)
    
    # Create channel configurations
    if product_data.channels:
        for channel_data in product_data.channels:
            channel = GoldProductChannel(
                id=str(uuid4()),
                product_id=product.id,
                **channel_data.model_dump()
            )
            db.add(channel)
    
    # Create tax configurations
    if product_data.taxes:
        for tax_data in product_data.taxes:
            tax = GoldProductTax(
                id=str(uuid4()),
                product_id=product.id,
                **tax_data.model_dump()
            )
            db.add(tax)
    
    db.commit()
    db.refresh(product)
    
    # Load all relationships
    product = db.query(GoldProduct).options(
        joinedload(GoldProduct.interest),
        joinedload(GoldProduct.tenure),
        joinedload(GoldProduct.limits),
        joinedload(GoldProduct.charges),
        joinedload(GoldProduct.documents),
        joinedload(GoldProduct.eligibility),
        joinedload(GoldProduct.workflow),
        joinedload(GoldProduct.channels),
        joinedload(GoldProduct.taxes)
    ).filter(GoldProduct.id == product.id).first()
    
    return product


@router.get("", response_model=List[GoldProductSummary])
async def list_products(
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    List all gold loan products with summary information.
    
    Returns a lightweight list of products for dropdowns and listings.
    """
    query = db.query(GoldProduct).options(
        joinedload(GoldProduct.interest),
        joinedload(GoldProduct.limits)
    )
    
    if product_type:
        query = query.filter(GoldProduct.product_type == product_type)
    if is_active is not None:
        query = query.filter(GoldProduct.is_active == is_active)
    
    products = query.order_by(GoldProduct.display_order, GoldProduct.product_name).all()
    
    # Build summary response
    summaries = []
    for product in products:
        summary = GoldProductSummary(
            id=product.id,
            product_code=product.product_code,
            product_name=product.product_name,
            product_type=product.product_type,
            is_active=product.is_active,
            base_rate=product.interest.base_rate if product.interest else None,
            ltv_percent=product.limits.ltv_percent if product.limits else None,
            min_amount=product.limits.min_loan_amount if product.limits else None,
            max_amount=product.limits.max_loan_amount if product.limits else None
        )
        summaries.append(summary)
    
    return summaries


@router.get("/{product_id}", response_model=GoldProductResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """
    Get complete product configuration by ID.
    
    Returns full product details with all related configurations.
    """
    product = db.query(GoldProduct).options(
        joinedload(GoldProduct.interest),
        joinedload(GoldProduct.tenure),
        joinedload(GoldProduct.limits),
        joinedload(GoldProduct.charges),
        joinedload(GoldProduct.documents),
        joinedload(GoldProduct.eligibility),
        joinedload(GoldProduct.workflow),
        joinedload(GoldProduct.channels),
        joinedload(GoldProduct.taxes)
    ).filter(GoldProduct.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    
    return product


@router.get("/code/{product_code}", response_model=GoldProductResponse)
async def get_product_by_code(product_code: str, db: Session = Depends(get_db)):
    """
    Get complete product configuration by product code.
    """
    product = db.query(GoldProduct).options(
        joinedload(GoldProduct.interest),
        joinedload(GoldProduct.tenure),
        joinedload(GoldProduct.limits),
        joinedload(GoldProduct.charges),
        joinedload(GoldProduct.documents),
        joinedload(GoldProduct.eligibility),
        joinedload(GoldProduct.workflow),
        joinedload(GoldProduct.channels),
        joinedload(GoldProduct.taxes)
    ).filter(GoldProduct.product_code == product_code).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product code '{product_code}' not found"
        )
    
    return product


@router.patch("/{product_id}", response_model=GoldProductResponse)
async def update_product(
    product_id: str,
    product_data: GoldProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update product master details.
    
    Use specific endpoints to update interest, tenure, limits, etc.
    """
    product = db.query(GoldProduct).filter(GoldProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """
    Delete a product and all its configurations.
    
    This is a soft delete - sets is_active to False.
    """
    product = db.query(GoldProduct).filter(GoldProduct.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    
    product.is_active = False
    product.updated_at = datetime.utcnow()
    db.commit()


# Interest Configuration Endpoints
@router.put("/{product_id}/interest", response_model=InterestConfigResponse)
async def set_interest_config(
    product_id: str,
    config: InterestConfig,
    db: Session = Depends(get_db)
):
    """Set or update interest configuration for a product"""
    product = db.query(GoldProduct).filter(GoldProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing = db.query(GoldProductInterest).filter(
        GoldProductInterest.product_id == product_id
    ).first()
    
    if existing:
        for field, value in config.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_config = GoldProductInterest(
            id=str(uuid4()),
            product_id=product_id,
            **config.model_dump()
        )
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config


# Tenure Configuration Endpoints
@router.put("/{product_id}/tenure", response_model=TenureConfigResponse)
async def set_tenure_config(
    product_id: str,
    config: TenureConfig,
    db: Session = Depends(get_db)
):
    """Set or update tenure configuration for a product"""
    product = db.query(GoldProduct).filter(GoldProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing = db.query(GoldProductTenure).filter(
        GoldProductTenure.product_id == product_id
    ).first()
    
    if existing:
        for field, value in config.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_config = GoldProductTenure(
            id=str(uuid4()),
            product_id=product_id,
            **config.model_dump()
        )
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config


# Limits Configuration Endpoints
@router.put("/{product_id}/limits", response_model=LimitsConfigResponse)
async def set_limits_config(
    product_id: str,
    config: LimitsConfig,
    db: Session = Depends(get_db)
):
    """Set or update limits configuration for a product"""
    product = db.query(GoldProduct).filter(GoldProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing = db.query(GoldProductLimits).filter(
        GoldProductLimits.product_id == product_id
    ).first()
    
    if existing:
        for field, value in config.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_config = GoldProductLimits(
            id=str(uuid4()),
            product_id=product_id,
            **config.model_dump()
        )
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config


# Charges Endpoints
@router.post("/{product_id}/charges", response_model=ChargeConfigResponse, status_code=201)
async def add_charge(
    product_id: str,
    charge: ChargeConfig,
    db: Session = Depends(get_db)
):
    """Add a charge to a product"""
    product = db.query(GoldProduct).filter(GoldProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_charge = GoldProductCharge(
        id=str(uuid4()),
        product_id=product_id,
        **charge.model_dump()
    )
    db.add(new_charge)
    db.commit()
    db.refresh(new_charge)
    return new_charge


@router.get("/{product_id}/charges", response_model=List[ChargeConfigResponse])
async def list_charges(product_id: str, db: Session = Depends(get_db)):
    """List all charges for a product"""
    charges = db.query(GoldProductCharge).filter(
        GoldProductCharge.product_id == product_id
    ).all()
    return charges


@router.delete("/{product_id}/charges/{charge_id}", status_code=204)
async def delete_charge(product_id: str, charge_id: str, db: Session = Depends(get_db)):
    """Remove a charge from a product"""
    charge = db.query(GoldProductCharge).filter(
        GoldProductCharge.id == charge_id,
        GoldProductCharge.product_id == product_id
    ).first()
    
    if not charge:
        raise HTTPException(status_code=404, detail="Charge not found")
    
    db.delete(charge)
    db.commit()


# Documents Endpoints
@router.post("/{product_id}/documents", response_model=DocumentConfigResponse, status_code=201)
async def add_document(
    product_id: str,
    document: DocumentConfig,
    db: Session = Depends(get_db)
):
    """Add a document requirement to a product"""
    product = db.query(GoldProduct).filter(GoldProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_doc = GoldProductDocument(
        id=str(uuid4()),
        product_id=product_id,
        **document.model_dump()
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


@router.get("/{product_id}/documents", response_model=List[DocumentConfigResponse])
async def list_documents(product_id: str, db: Session = Depends(get_db)):
    """List all document requirements for a product"""
    documents = db.query(GoldProductDocument).filter(
        GoldProductDocument.product_id == product_id
    ).all()
    return documents


# Eligibility Rules Endpoints
@router.post("/{product_id}/eligibility", response_model=EligibilityRuleResponse, status_code=201)
async def add_eligibility_rule(
    product_id: str,
    rule: EligibilityRule,
    db: Session = Depends(get_db)
):
    """Add an eligibility rule to a product"""
    product = db.query(GoldProduct).filter(GoldProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_rule = GoldProductEligibility(
        id=str(uuid4()),
        product_id=product_id,
        **rule.model_dump()
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule


@router.get("/{product_id}/eligibility", response_model=List[EligibilityRuleResponse])
async def list_eligibility_rules(product_id: str, db: Session = Depends(get_db)):
    """List all eligibility rules for a product"""
    rules = db.query(GoldProductEligibility).filter(
        GoldProductEligibility.product_id == product_id
    ).all()
    return rules


# Workflow Endpoints
@router.post("/{product_id}/workflow", response_model=WorkflowStageResponse, status_code=201)
async def add_workflow_stage(
    product_id: str,
    stage: WorkflowStage,
    db: Session = Depends(get_db)
):
    """Add a workflow stage to a product"""
    product = db.query(GoldProduct).filter(GoldProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_stage = GoldProductWorkflow(
        id=str(uuid4()),
        product_id=product_id,
        **stage.model_dump()
    )
    db.add(new_stage)
    db.commit()
    db.refresh(new_stage)
    return new_stage


@router.get("/{product_id}/workflow", response_model=List[WorkflowStageResponse])
async def list_workflow_stages(product_id: str, db: Session = Depends(get_db)):
    """List all workflow stages for a product"""
    stages = db.query(GoldProductWorkflow).filter(
        GoldProductWorkflow.product_id == product_id
    ).order_by(GoldProductWorkflow.stage_order).all()
    return stages
