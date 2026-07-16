"""
Product Configuration API Router

REST API endpoints for product management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, get_tenant_id
from backend.services.products.product_models import (
    Product, ProductSummary, ProductFilter, ProductCalculation,
    ProductCalculationResult, ProductStatus, ProductCategory
)
from backend.services.products.product_service import product_service


router = APIRouter(prefix="/api/products", tags=["Products"])


# ==================== PRODUCT CRUD ====================

@router.post("/")
def create_product(
    product: Product,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create new product"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    try:
        # Set tenant and user
        product.tenant_id = tenant_id
        
        # Create product
        created_product = product_service.create_product(
            product=product,
            user_id=current_user['id']
        )
        
        # Store in database
        template = WorkflowTemplate(
            tenant_id=tenant_id,
            template_key=created_product.product_id,
            template_name=created_product.product_name,
            template_type='product',
            definition={'product': created_product.dict()},
            is_active=created_product.product_status == ProductStatus.ACTIVE,
            created_by=current_user['id']
        )
        
        db.add(template)
        db.commit()
        
        return {
            "success": True,
            "data": created_product.dict(),
            "message": "Product created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")


@router.get("/")
def list_products(
    category: Optional[ProductCategory] = None,
    status: Optional[ProductStatus] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List products with optional filtering"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    try:
        # Get products from database
        query = db.query(WorkflowTemplate).filter(
            WorkflowTemplate.tenant_id == tenant_id,
            WorkflowTemplate.template_type == 'product',
            WorkflowTemplate.is_deleted == False
        )
        
        templates = query.all()
        
        # Load products into service
        product_service.products = {}
        for template in templates:
            product_data = template.definition.get('product', {})
            product = Product(**product_data)
            product_service.products[product.product_id] = product
        
        # Build filter
        filters = ProductFilter(
            category=category,
            status=status,
            min_amount=min_amount,
            max_amount=max_amount,
            is_featured=is_featured,
            search_query=search
        )
        
        # Get filtered products
        summaries = product_service.list_products(filters, skip, limit)
        
        return {
            "success": True,
            "data": [s.dict() for s in summaries],
            "total": len(summaries),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list products: {str(e)}")


@router.get("/{product_id}")
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get product by ID"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == product_id,
        WorkflowTemplate.template_type == 'product',
        WorkflowTemplate.is_deleted == False
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "success": True,
        "data": template.definition.get('product', {})
    }


@router.put("/{product_id}")
def update_product(
    product_id: str,
    product: Product,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Update product"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == product_id,
        WorkflowTemplate.template_type == 'product',
        WorkflowTemplate.is_deleted == False
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Set tenant and user
        product.tenant_id = tenant_id
        product.updated_at = datetime.utcnow()
        product.updated_by = current_user['id']
        
        # Update in database
        template.definition = {'product': product.dict()}
        template.is_active = product.product_status == ProductStatus.ACTIVE
        template.updated_by = current_user['id']
        
        db.commit()
        
        return {
            "success": True,
            "data": product.dict(),
            "message": "Product updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")


@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Delete product (soft delete)"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == product_id,
        WorkflowTemplate.template_type == 'product'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Soft delete
    template.is_deleted = True
    template.updated_by = current_user['id']
    
    db.commit()
    
    return {
        "success": True,
        "message": "Product deleted successfully"
    }


# ==================== PRODUCT OPERATIONS ====================

@router.post("/{product_id}/clone")
def clone_product(
    product_id: str,
    new_product_code: str,
    new_product_name: str,
    modifications: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Clone an existing product"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Get source product
    source_template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == product_id,
        WorkflowTemplate.template_type == 'product',
        WorkflowTemplate.is_deleted == False
    ).first()
    
    if not source_template:
        raise HTTPException(status_code=404, detail="Source product not found")
    
    try:
        # Load source product
        source_product = Product(**source_template.definition.get('product', {}))
        product_service.products[source_product.product_id] = source_product
        
        # Clone product
        cloned_product = product_service.clone_product(
            source_product_id=product_id,
            new_product_code=new_product_code,
            new_product_name=new_product_name,
            modifications=modifications or {},
            user_id=current_user['id']
        )
        
        cloned_product.tenant_id = tenant_id
        
        # Store cloned product
        template = WorkflowTemplate(
            tenant_id=tenant_id,
            template_key=cloned_product.product_id,
            template_name=cloned_product.product_name,
            template_type='product',
            definition={'product': cloned_product.dict()},
            is_active=False,
            created_by=current_user['id']
        )
        
        db.add(template)
        db.commit()
        
        return {
            "success": True,
            "data": cloned_product.dict(),
            "message": "Product cloned successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone product: {str(e)}")


@router.post("/{product_id}/activate")
def activate_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Activate a product"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == product_id,
        WorkflowTemplate.template_type == 'product',
        WorkflowTemplate.is_deleted == False
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Load product
        product = Product(**template.definition.get('product', {}))
        product_service.products[product.product_id] = product
        
        # Activate
        activated_product = product_service.activate_product(product_id, current_user['id'])
        
        # Update database
        template.definition = {'product': activated_product.dict()}
        template.is_active = True
        template.updated_by = current_user['id']
        
        db.commit()
        
        return {
            "success": True,
            "data": activated_product.dict(),
            "message": "Product activated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate product: {str(e)}")


@router.post("/{product_id}/deactivate")
def deactivate_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Deactivate a product"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == product_id,
        WorkflowTemplate.template_type == 'product',
        WorkflowTemplate.is_deleted == False
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Load product
        product = Product(**template.definition.get('product', {}))
        product_service.products[product.product_id] = product
        
        # Deactivate
        deactivated_product = product_service.deactivate_product(product_id, current_user['id'])
        
        # Update database
        template.definition = {'product': deactivated_product.dict()}
        template.is_active = False
        template.updated_by = current_user['id']
        
        db.commit()
        
        return {
            "success": True,
            "data": deactivated_product.dict(),
            "message": "Product deactivated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate product: {str(e)}")


# ==================== PRODUCT CALCULATIONS ====================

@router.post("/{product_id}/calculate")
def calculate_product(
    product_id: str,
    calculation: ProductCalculation,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Calculate EMI and generate amortization schedule"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == product_id,
        WorkflowTemplate.template_type == 'product',
        WorkflowTemplate.is_deleted == False
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Load product
        product = Product(**template.definition.get('product', {}))
        product_service.products[product.product_id] = product
        
        # Calculate
        result = product_service.calculate_emi(
            product_id=product_id,
            principal_amount=calculation.principal_amount,
            tenure_months=calculation.tenure_months,
            interest_rate=calculation.interest_rate
        )
        
        return {
            "success": True,
            "data": result.dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate: {str(e)}")


# ==================== PRODUCT QUERIES ====================

@router.get("/by-code/{product_code}")
def get_product_by_code(
    product_code: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get product by code"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    templates = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'product',
        WorkflowTemplate.is_deleted == False
    ).all()
    
    for template in templates:
        product_data = template.definition.get('product', {})
        if product_data.get('product_code') == product_code:
            return {
                "success": True,
                "data": product_data
            }
    
    raise HTTPException(status_code=404, detail="Product not found")


@router.get("/categories/list")
def get_product_categories():
    """Get list of product categories"""
    categories = [
        {"value": cat.value, "label": cat.value.replace('_', ' ').title()}
        for cat in ProductCategory
    ]
    
    return {
        "success": True,
        "data": categories
    }


@router.get("/stats/summary")
def get_product_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get product statistics"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    templates = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'product',
        WorkflowTemplate.is_deleted == False
    ).all()
    
    stats = {
        "total_products": len(templates),
        "active_products": 0,
        "inactive_products": 0,
        "draft_products": 0,
        "by_category": {}
    }
    
    for template in templates:
        product_data = template.definition.get('product', {})
        status = product_data.get('product_status')
        category = product_data.get('product_category')
        
        if status == 'active':
            stats['active_products'] += 1
        elif status == 'inactive':
            stats['inactive_products'] += 1
        elif status == 'draft':
            stats['draft_products'] += 1
        
        if category:
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
    
    return {
        "success": True,
        "data": stats
    }


# ==================== HELPER ENDPOINTS ====================

@router.get("/validation/check-code/{product_code}")
def check_product_code(
    product_code: str,
    exclude_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Check if product code is available"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    templates = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'product',
        WorkflowTemplate.is_deleted == False
    ).all()
    
    for template in templates:
        product_data = template.definition.get('product', {})
        if (product_data.get('product_code') == product_code and 
            product_data.get('product_id') != exclude_id):
            return {
                "success": True,
                "available": False,
                "message": f"Product code '{product_code}' is already in use"
            }
    
    return {
        "success": True,
        "available": True,
        "message": f"Product code '{product_code}' is available"
    }
