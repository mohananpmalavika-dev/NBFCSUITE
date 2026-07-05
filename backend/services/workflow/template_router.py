"""
Workflow Template Router

API endpoints for workflow template management including:
- Template CRUD operations
- Template validation
- Template activation
- Template versioning and cloning
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .template_service import WorkflowTemplateService
from .schemas import (
    WorkflowTemplateCreate,
    WorkflowTemplateUpdate,
    WorkflowTemplateResponse,
    TemplateValidationResponse,
    TemplateStatistics,
    CloneTemplateRequest,
    CreateVersionRequest,
    TemplateVersionListResponse,
    TemplateListResponse,
    WorkflowStatus
)

router = APIRouter(prefix="/workflows/templates", tags=["Workflow Templates"])


# ==================== CRUD OPERATIONS ====================

@router.post("", response_model=dict, status_code=201)
def create_template(
    template_data: WorkflowTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Create new workflow template
    
    Creates a reusable workflow definition that can be instantiated multiple times.
    Template starts in 'draft' status and must be activated before use.
    
    **Required**:
    - template_code: Unique identifier
    - template_name: Display name
    - workflow_type: sequential, parallel, or conditional
    - workflow_definition: Complete workflow graph (JSON)
    
    **Optional**:
    - category: For grouping templates
    - default_sla_hours: Default SLA for instances
    - escalation_rules: Escalation configuration
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.create_template(template_data.dict())
    
    return success_response(
        message="Workflow template created successfully",
        data=WorkflowTemplateResponse.from_orm(template).dict()
    )


@router.get("", response_model=dict)
def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[WorkflowStatus] = Query(None, description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List workflow templates
    
    Returns all templates (latest versions only) with optional filters.
    
    **Filters**:
    - category: Template category
    - status: draft, active, archived
    - is_active: Boolean flag
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    templates = service.list_templates(
        category=category,
        status=status,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(templates)} templates",
        data={
            "templates": [WorkflowTemplateResponse.from_orm(t).dict() for t in templates],
            "total": len(templates),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{template_id}", response_model=dict)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get workflow template by ID
    
    Returns complete template details including workflow definition.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.get_template(template_id)
    
    return success_response(
        message="Template retrieved successfully",
        data=WorkflowTemplateResponse.from_orm(template).dict()
    )


@router.get("/code/{template_code}", response_model=dict)
def get_template_by_code(
    template_code: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get workflow template by code
    
    Returns latest version of template with given code.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.get_template_by_code(template_code)
    
    return success_response(
        message="Template retrieved successfully",
        data=WorkflowTemplateResponse.from_orm(template).dict()
    )


@router.put("/{template_id}", response_model=dict)
def update_template(
    template_id: int,
    update_data: WorkflowTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Update workflow template
    
    Only templates in 'draft' status should be updated directly.
    For active templates, create a new version instead.
    
    **Note**: template_code cannot be changed
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.update_template(
        template_id,
        update_data.dict(exclude_unset=True)
    )
    
    return success_response(
        message="Template updated successfully",
        data=WorkflowTemplateResponse.from_orm(template).dict()
    )


@router.delete("/{template_id}", response_model=dict)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Delete workflow template (soft delete)
    
    Cannot delete template with active workflow instances.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    service.delete_template(template_id)
    
    return success_response(
        message="Template deleted successfully",
        data={"template_id": template_id, "deleted": True}
    )


# ==================== TEMPLATE OPERATIONS ====================

@router.post("/{template_id}/activate", response_model=dict)
def activate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Activate workflow template
    
    Makes template available for creating instances.
    Template must have valid workflow definition.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.activate_template(template_id)
    
    return success_response(
        message="Template activated successfully",
        data=WorkflowTemplateResponse.from_orm(template).dict()
    )


@router.post("/{template_id}/deactivate", response_model=dict)
def deactivate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Deactivate workflow template
    
    Prevents creation of new instances.
    Existing instances continue to run.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.deactivate_template(template_id)
    
    return success_response(
        message="Template deactivated successfully",
        data=WorkflowTemplateResponse.from_orm(template).dict()
    )


@router.post("/{template_id}/clone", response_model=dict)
def clone_template(
    template_id: int,
    clone_request: CloneTemplateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Clone workflow template
    
    Creates a copy of existing template with new code and name.
    Cloned template starts in 'draft' status.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.clone_template(
        template_id,
        clone_request.new_code,
        clone_request.new_name
    )
    
    return success_response(
        message="Template cloned successfully",
        data=WorkflowTemplateResponse.from_orm(template).dict()
    )


@router.post("/{template_id}/version", response_model=dict)
def create_version(
    template_id: int,
    version_request: CreateVersionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Create new version of template
    
    Creates a new version while preserving the original.
    New version starts in 'draft' status with incremented version number.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.create_version(
        template_id,
        version_request.changes_description
    )
    
    return success_response(
        message="New version created successfully",
        data=WorkflowTemplateResponse.from_orm(template).dict()
    )


@router.get("/{template_id}/versions", response_model=dict)
def get_template_versions(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get all versions of a template
    
    Returns all versions ordered by version number (latest first).
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.get_template(template_id)
    versions = service.get_template_versions(template.template_code)
    
    return success_response(
        message=f"Retrieved {len(versions)} versions",
        data={
            "template_code": template.template_code,
            "versions": [WorkflowTemplateResponse.from_orm(v).dict() for v in versions],
            "total_versions": len(versions)
        }
    )


# ==================== VALIDATION ====================

@router.post("/{template_id}/validate", response_model=dict)
def validate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Validate workflow definition
    
    Checks workflow definition for:
    - Required fields
    - Valid step references
    - Valid transitions
    - Start/end steps
    
    Returns validation result with errors and warnings.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.get_template(template_id)
    result = service.validate_workflow_definition(template.workflow_definition)
    
    return success_response(
        message="Validation completed",
        data=result
    )


@router.post("/validate-definition", response_model=dict)
def validate_definition(
    workflow_definition: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Validate workflow definition (without saving)
    
    Validates a workflow definition JSON before creating template.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    result = service.validate_workflow_definition(workflow_definition)
    
    return success_response(
        message="Validation completed",
        data=result
    )


# ==================== STATISTICS ====================

@router.get("/{template_id}/statistics", response_model=dict)
def get_template_statistics(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get template usage statistics
    
    Returns:
    - Total instances created
    - Instances by status
    - Average completion time
    - Success rate
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    stats = service.get_template_statistics(template_id)
    
    return success_response(
        message="Statistics retrieved successfully",
        data=stats
    )


# ==================== CATEGORIES ====================

@router.get("/categories/list", response_model=dict)
def get_categories(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get all template categories
    
    Returns list of unique category names used in templates.
    """
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    categories = service.get_categories()
    
    return success_response(
        message=f"Retrieved {len(categories)} categories",
        data={"categories": categories}
    )


# ==================== TEST EXECUTION ====================

@router.post("/{template_id}/test", response_model=dict)
def test_template(
    template_id: int,
    test_variables: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Test workflow template
    
    Creates a test instance to verify workflow execution.
    Test instances are marked for easy identification.
    
    **Note**: This is for testing purposes. Test instances should be cleaned up.
    """
    from .execution_service import WorkflowExecutionService
    
    service = WorkflowTemplateService(db, tenant_id, current_user["id"])
    template = service.get_template(template_id)
    
    # Create test instance
    exec_service = WorkflowExecutionService(db, tenant_id, current_user["id"])
    instance = exec_service.start_workflow(
        template_code=template.template_code,
        entity_type="test",
        entity_id=0,
        variables=test_variables or {},
        priority="normal",
        instance_name=f"TEST - {template.template_name}"
    )
    
    return success_response(
        message="Test instance created successfully",
        data={
            "template_id": template_id,
            "instance_id": instance.id,
            "instance_number": instance.instance_number,
            "status": instance.status
        }
    )
