"""
BPMN Workflow API Router

Comprehensive REST API for BPMN workflow management:
- Workflow definition CRUD
- Workflow execution
- Visual designer support
- Template library
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.shared.database.connection import get_db
from backend.shared.common.dependencies import get_current_user
from backend.shared.database.models import User
from backend.shared.database.workflow_models import (
    WorkflowTemplate, WorkflowInstance
)
from backend.services.workflow.bpmn_models import (
    BPMNWorkflowDefinition, BPMNProcess, WorkflowCanvas,
    WorkflowTemplateDefinition, ValidationResult
)
from backend.services.workflow.bpmn_engine import (
    BPMNExecutionEngine, BPMNValidator
)
from backend.services.workflow.template_service import WorkflowTemplateService

router = APIRouter(prefix="/api/v1/bpmn", tags=["BPMN Workflow"])


# ==================== REQUEST/RESPONSE SCHEMAS ====================

class CreateBPMNWorkflowRequest(BaseModel):
    """Request to create BPMN workflow"""
    workflow_name: str
    workflow_description: Optional[str] = None
    category: Optional[str] = None
    process: BPMNProcess


class UpdateBPMNWorkflowRequest(BaseModel):
    """Request to update BPMN workflow"""
    workflow_name: Optional[str] = None
    workflow_description: Optional[str] = None
    category: Optional[str] = None
    process: Optional[BPMNProcess] = None


class StartWorkflowRequest(BaseModel):
    """Request to start workflow"""
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    variables: Optional[Dict[str, Any]] = None
    priority: str = "normal"


class SaveCanvasRequest(BaseModel):
    """Request to save workflow canvas"""
    canvas: WorkflowCanvas


# ==================== WORKFLOW DEFINITION ENDPOINTS ====================

@router.post("/workflows")
def create_bpmn_workflow(
    request: CreateBPMNWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new BPMN workflow definition"""
    # Validate process
    validation = BPMNValidator.validate_process(request.process)
    if not validation['valid']:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid workflow definition",
                "errors": validation['errors']
            }
        )
    
    # Create workflow definition
    workflow_def = BPMNWorkflowDefinition(
        workflow_id=f"wf_{request.workflow_name.lower().replace(' ', '_')}",
        workflow_name=request.workflow_name,
        workflow_description=request.workflow_description,
        process=request.process,
        category=request.category
    )
    
    # Create template
    service = WorkflowTemplateService(
        db, 
        current_user.tenant_id,
        current_user.id
    )
    
    template_data = {
        'template_code': workflow_def.workflow_id,
        'template_name': request.workflow_name,
        'description': request.workflow_description,
        'category': request.category or 'general',
        'workflow_type': 'bpmn',
        'workflow_definition': workflow_def.dict(),
        'is_active': False
    }
    
    template = service.create_template(template_data)
    
    return {
        "success": True,
        "message": "BPMN workflow created successfully",
        "workflow_id": workflow_def.workflow_id,
        "template_id": template.id
    }


@router.get("/workflows/{workflow_id}")
def get_bpmn_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get BPMN workflow definition"""
    service = WorkflowTemplateService(
        db,
        current_user.tenant_id,
        current_user.id
    )
    
    template = service.get_template_by_code(workflow_id)
    
    # Parse BPMN definition
    workflow_def = BPMNWorkflowDefinition(**template.workflow_definition)
    
    return {
        "success": True,
        "workflow": workflow_def.dict(),
        "template": {
            "id": template.id,
            "status": template.status,
            "is_active": template.is_active,
            "version": template.version
        }
    }


@router.put("/workflows/{workflow_id}")
def update_bpmn_workflow(
    workflow_id: str,
    request: UpdateBPMNWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update BPMN workflow definition"""
    service = WorkflowTemplateService(
        db,
        current_user.tenant_id,
        current_user.id
    )
    
    template = service.get_template_by_code(workflow_id)
    
    # Get current definition
    workflow_def = BPMNWorkflowDefinition(**template.workflow_definition)
    
    # Update fields
    if request.workflow_name:
        workflow_def.workflow_name = request.workflow_name
    if request.workflow_description:
        workflow_def.workflow_description = request.workflow_description
    if request.process:
        # Validate new process
        validation = BPMNValidator.validate_process(request.process)
        if not validation['valid']:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid workflow definition",
                    "errors": validation['errors']
                }
            )
        workflow_def.process = request.process
    
    # Update template
    update_data = {
        'workflow_definition': workflow_def.dict()
    }
    if request.workflow_name:
        update_data['template_name'] = request.workflow_name
    if request.workflow_description:
        update_data['description'] = request.workflow_description
    if request.category:
        update_data['category'] = request.category
    
    service.update_template(template.id, update_data)
    
    return {
        "success": True,
        "message": "Workflow updated successfully"
    }


@router.post("/workflows/{workflow_id}/validate")
def validate_bpmn_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate BPMN workflow definition"""
    service = WorkflowTemplateService(
        db,
        current_user.tenant_id,
        current_user.id
    )
    
    template = service.get_template_by_code(workflow_id)
    workflow_def = BPMNWorkflowDefinition(**template.workflow_definition)
    
    validation = BPMNValidator.validate_process(workflow_def.process)
    
    return {
        "success": True,
        "validation": validation
    }


@router.get("/workflows")
def list_bpmn_workflows(
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all BPMN workflows"""
    service = WorkflowTemplateService(
        db,
        current_user.tenant_id,
        current_user.id
    )
    
    templates = service.list_templates(
        category=category,
        is_active=True,
        skip=skip,
        limit=limit
    )
    
    workflows = []
    for template in templates:
        workflow_def = BPMNWorkflowDefinition(**template.workflow_definition)
        workflows.append({
            "workflow_id": workflow_def.workflow_id,
            "workflow_name": workflow_def.workflow_name,
            "description": workflow_def.workflow_description,
            "category": template.category,
            "version": template.version,
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat()
        })
    
    return {
        "success": True,
        "workflows": workflows,
        "total": len(workflows)
    }


# ==================== WORKFLOW EXECUTION ENDPOINTS ====================

@router.post("/workflows/{workflow_id}/start")
def start_bpmn_workflow(
    workflow_id: str,
    request: StartWorkflowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start BPMN workflow execution"""
    service = WorkflowTemplateService(
        db,
        current_user.tenant_id,
        current_user.id
    )
    
    # Get template
    template = service.get_template_by_code(workflow_id)
    workflow_def = BPMNWorkflowDefinition(**template.workflow_definition)
    
    # Create workflow instance
    from backend.services.workflow.execution_service import WorkflowExecutionService
    exec_service = WorkflowExecutionService(
        db,
        current_user.tenant_id,
        current_user.id
    )
    
    instance = exec_service.start_workflow(
        template_code=workflow_id,
        entity_type=request.entity_type,
        entity_id=request.entity_id,
        variables=request.variables,
        priority=request.priority
    )
    
    # Execute workflow
    engine = BPMNExecutionEngine(db, current_user.tenant_id, current_user.id)
    status, message = engine.start_workflow(
        workflow_def.process,
        instance,
        request.variables
    )
    
    return {
        "success": True,
        "message": message,
        "instance_id": instance.id,
        "instance_number": instance.instance_number,
        "status": status.value
    }


# ==================== VISUAL DESIGNER ENDPOINTS ====================

@router.post("/workflows/{workflow_id}/canvas")
def save_workflow_canvas(
    workflow_id: str,
    request: SaveCanvasRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save workflow canvas (visual layout)"""
    service = WorkflowTemplateService(
        db,
        current_user.tenant_id,
        current_user.id
    )
    
    template = service.get_template_by_code(workflow_id)
    workflow_def = BPMNWorkflowDefinition(**template.workflow_definition)
    
    # Store canvas settings in process
    workflow_def.process.canvas_settings = request.canvas.dict()
    
    # Update template
    service.update_template(
        template.id,
        {'workflow_definition': workflow_def.dict()}
    )
    
    return {
        "success": True,
        "message": "Canvas saved successfully"
    }


@router.get("/workflows/{workflow_id}/canvas")
def get_workflow_canvas(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow canvas (visual layout)"""
    service = WorkflowTemplateService(
        db,
        current_user.tenant_id,
        current_user.id
    )
    
    template = service.get_template_by_code(workflow_id)
    workflow_def = BPMNWorkflowDefinition(**template.workflow_definition)
    
    # Convert BPMN to canvas format
    canvas = _convert_bpmn_to_canvas(workflow_def.process)
    
    return {
        "success": True,
        "canvas": canvas
    }


# ==================== TEMPLATE LIBRARY ====================

@router.get("/templates/library")
def get_template_library(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pre-built workflow templates"""
    from backend.services.workflow.workflow_templates import WorkflowTemplates
    
    templates = WorkflowTemplates.get_all_templates()
    
    return {
        "success": True,
        "templates": templates,
        "total": len(templates)
    }


@router.post("/templates/library/{template_id}/instantiate")
def instantiate_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a workflow from template"""
    from backend.services.workflow.workflow_templates import WorkflowTemplates
    
    template_def = WorkflowTemplates.get_template_by_id(template_id)
    
    if not template_def:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create workflow from template
    service = WorkflowTemplateService(
        db,
        current_user.tenant_id,
        current_user.id
    )
    
    template_data = {
        'template_code': template_def['workflow_id'],
        'template_name': template_def['workflow_name'],
        'description': template_def['workflow_description'],
        'category': template_def['category'],
        'workflow_type': 'bpmn',
        'workflow_definition': template_def,
        'is_active': False
    }
    
    template = service.create_template(template_data)
    
    return {
        "success": True,
        "message": "Workflow created from template",
        "workflow_id": template_def['workflow_id'],
        "template_id": template.id
    }


# ==================== HELPER FUNCTIONS ====================

def _convert_bpmn_to_canvas(process: BPMNProcess) -> Dict[str, Any]:
    """Convert BPMN process to canvas format"""
    nodes = []
    edges = []
    
    # Convert nodes
    all_nodes = (
        process.start_events +
        process.end_events +
        process.user_tasks +
        process.service_tasks +
        process.script_tasks +
        process.send_tasks +
        process.gateways +
        process.intermediate_events
    )
    
    for node in all_nodes:
        canvas_node = {
            "id": node.id,
            "type": node.type.value,
            "data": {
                "label": node.name,
                "description": node.description
            },
            "position": node.position.dict() if node.position else {"x": 0, "y": 0}
        }
        nodes.append(canvas_node)
    
    # Convert edges
    for flow in process.sequence_flows:
        edge = {
            "id": flow.id,
            "source": flow.source_ref,
            "target": flow.target_ref,
            "label": flow.name,
            "data": {
                "condition": flow.condition.dict() if flow.condition else None
            }
        }
        edges.append(edge)
    
    return {
        "nodes": nodes,
        "edges": edges,
        "viewport": process.canvas_settings.get("viewport") if process.canvas_settings else None
    }
