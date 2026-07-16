"""
Document Checklist API Router
RESTful API endpoints for document checklist management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from .document_models import (
    DocumentChecklist, DocumentChecklistFilter, DocumentChecklistStats,
    DocumentChecklistClone, ChecklistStatus, DocumentTemplate,
    DocumentType, DocumentEvaluationContext, ChecklistEvaluationResult
)
from .document_service import document_service

# Create router
router = APIRouter(prefix="/document-checklists", tags=["Document Checklists"])


# ============================================================================
# AUTHENTICATION & TENANT HELPERS (Placeholder)
# ============================================================================

async def get_current_user():
    """Get current authenticated user"""
    return {"user_id": "USER001", "tenant_id": "TENANT001"}


async def get_tenant_id(user: dict = Depends(get_current_user)) -> str:
    """Extract tenant ID from current user"""
    return user["tenant_id"]


async def get_user_id(user: dict = Depends(get_current_user)) -> str:
    """Extract user ID from current user"""
    return user["user_id"]


# ============================================================================
# CRUD ENDPOINTS - CHECKLISTS
# ============================================================================

@router.post("/", response_model=DocumentChecklist, status_code=status.HTTP_201_CREATED)
async def create_checklist(
    checklist_data: dict,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Create new document checklist
    
    **Parameters:**
    - checklist_data: Checklist configuration with requirements
    
    **Returns:**
    - Created document checklist
    """
    try:
        checklist = document_service.create_checklist(checklist_data, tenant_id, user_id)
        return checklist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checklist: {str(e)}")


@router.get("/", response_model=List[DocumentChecklist])
async def list_checklists(
    tenant_id: str = Depends(get_tenant_id),
    status: Optional[ChecklistStatus] = None,
    product_id: Optional[str] = None,
    product_code: Optional[str] = None,
    search_term: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    List document checklists with filters
    
    **Query Parameters:**
    - status: Filter by checklist status
    - product_id: Filter by product ID
    - product_code: Filter by product code
    - search_term: Search in code, name, description
    - skip: Number of records to skip
    - limit: Maximum records to return
    
    **Returns:**
    - List of document checklists
    """
    try:
        filters = DocumentChecklistFilter(
            status=status,
            product_id=product_id,
            product_code=product_code,
            search_term=search_term
        )
        checklists = document_service.list_checklists(tenant_id, filters, skip, limit)
        return checklists
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list checklists: {str(e)}")


@router.get("/{checklist_id}", response_model=DocumentChecklist)
async def get_checklist(
    checklist_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get checklist by ID
    
    **Parameters:**
    - checklist_id: Checklist ID
    
    **Returns:**
    - Document checklist details
    """
    try:
        checklist = document_service.get_checklist(checklist_id, tenant_id)
        return checklist
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get checklist: {str(e)}")


@router.get("/by-code/{checklist_code}", response_model=DocumentChecklist)
async def get_checklist_by_code(
    checklist_code: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get checklist by code
    
    **Parameters:**
    - checklist_code: Checklist code
    
    **Returns:**
    - Document checklist details
    """
    try:
        checklist = document_service.get_checklist_by_code(checklist_code, tenant_id)
        return checklist
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get checklist: {str(e)}")


@router.put("/{checklist_id}", response_model=DocumentChecklist)
async def update_checklist(
    checklist_id: str,
    checklist_data: dict,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Update document checklist
    
    **Parameters:**
    - checklist_id: Checklist ID
    - checklist_data: Updated checklist data
    
    **Returns:**
    - Updated checklist
    """
    try:
        checklist = document_service.update_checklist(checklist_id, checklist_data, tenant_id, user_id)
        return checklist
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update checklist: {str(e)}")


@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist(
    checklist_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Delete document checklist
    
    **Parameters:**
    - checklist_id: Checklist ID
    
    **Returns:**
    - 204 No Content
    """
    try:
        document_service.delete_checklist(checklist_id, tenant_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete checklist: {str(e)}")


# ============================================================================
# CHECKLIST OPERATIONS
# ============================================================================

@router.post("/{checklist_id}/clone", response_model=DocumentChecklist, status_code=status.HTTP_201_CREATED)
async def clone_checklist(
    checklist_id: str,
    clone_data: DocumentChecklistClone,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Clone document checklist
    
    **Parameters:**
    - checklist_id: Checklist ID to clone
    - clone_data: Clone configuration
    
    **Returns:**
    - Cloned checklist
    """
    try:
        checklist = document_service.clone_checklist(checklist_id, clone_data, tenant_id, user_id)
        return checklist
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone checklist: {str(e)}")


@router.post("/{checklist_id}/activate", response_model=DocumentChecklist)
async def activate_checklist(
    checklist_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Activate checklist
    
    **Parameters:**
    - checklist_id: Checklist ID
    
    **Returns:**
    - Activated checklist
    """
    try:
        checklist = document_service.activate_checklist(checklist_id, tenant_id, user_id)
        return checklist
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate checklist: {str(e)}")


@router.post("/{checklist_id}/deactivate", response_model=DocumentChecklist)
async def deactivate_checklist(
    checklist_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Deactivate checklist
    
    **Parameters:**
    - checklist_id: Checklist ID
    
    **Returns:**
    - Deactivated checklist
    """
    try:
        checklist = document_service.deactivate_checklist(checklist_id, tenant_id, user_id)
        return checklist
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate checklist: {str(e)}")


# ============================================================================
# CHECKLIST EVALUATION
# ============================================================================

@router.post("/{checklist_id}/evaluate", response_model=ChecklistEvaluationResult)
async def evaluate_checklist(
    checklist_id: str,
    context: DocumentEvaluationContext,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Evaluate checklist and determine required documents
    
    **Parameters:**
    - checklist_id: Checklist ID
    - context: Evaluation context (customer type, employment, loan details, etc.)
    
    **Returns:**
    - Evaluation result with required documents
    """
    try:
        result = document_service.evaluate_checklist(checklist_id, context, tenant_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate checklist: {str(e)}")


# ============================================================================
# TEMPLATE MANAGEMENT
# ============================================================================

@router.post("/templates", response_model=DocumentTemplate, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: dict,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Create document template
    
    **Parameters:**
    - template_data: Template configuration
    
    **Returns:**
    - Created template
    """
    try:
        template = document_service.create_template(template_data, tenant_id, user_id)
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.get("/templates", response_model=List[DocumentTemplate])
async def list_templates(
    tenant_id: str = Depends(get_tenant_id),
    document_type: Optional[DocumentType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    List document templates
    
    **Query Parameters:**
    - document_type: Filter by document type
    - skip: Number of records to skip
    - limit: Maximum records to return
    
    **Returns:**
    - List of templates
    """
    try:
        templates = document_service.list_templates(tenant_id, document_type, skip, limit)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")


@router.get("/templates/{template_id}", response_model=DocumentTemplate)
async def get_template(
    template_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get template by ID
    
    **Parameters:**
    - template_id: Template ID
    
    **Returns:**
    - Template details
    """
    try:
        template = document_service.get_template(template_id, tenant_id)
        return template
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")


@router.put("/templates/{template_id}", response_model=DocumentTemplate)
async def update_template(
    template_id: str,
    template_data: dict,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Update document template
    
    **Parameters:**
    - template_id: Template ID
    - template_data: Updated template data
    
    **Returns:**
    - Updated template
    """
    try:
        template = document_service.update_template(template_id, template_data, tenant_id, user_id)
        return template
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Delete document template
    
    **Parameters:**
    - template_id: Template ID
    
    **Returns:**
    - 204 No Content
    """
    try:
        document_service.delete_template(template_id, tenant_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")


# ============================================================================
# STATISTICS & UTILITIES
# ============================================================================

@router.get("/stats/summary", response_model=DocumentChecklistStats)
async def get_stats(
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get document checklist statistics
    
    **Returns:**
    - Statistics including total checklists, templates, etc.
    """
    try:
        stats = document_service.get_stats(tenant_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/validation/validate", response_model=dict)
async def validate_checklist_data(checklist_data: dict):
    """
    Validate checklist data
    
    **Parameters:**
    - checklist_data: Checklist data to validate
    
    **Returns:**
    - Validation result with errors and warnings
    """
    try:
        validation = document_service.validate_checklist_data(checklist_data)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate: {str(e)}")


@router.get("/validation/check-code/{checklist_code}", response_model=dict)
async def check_checklist_code(
    checklist_code: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Check if checklist code is available
    
    **Parameters:**
    - checklist_code: Checklist code to check
    
    **Returns:**
    - Availability status
    """
    try:
        exists = any(
            c.checklist_code == checklist_code 
            for c in document_service.checklists_storage.values() 
            if c.tenant_id == tenant_id
        )
        
        return {
            "available": not exists,
            "message": f"Checklist code '{checklist_code}' is {'already in use' if exists else 'available'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check code: {str(e)}")
