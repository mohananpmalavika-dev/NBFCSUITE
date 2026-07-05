"""
Workflow Template Service

Handles workflow template management including:
- Template CRUD operations
- Workflow definition validation
- Template versioning
- Template activation/deactivation
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.shared.database.workflow_models import WorkflowTemplate
from backend.shared.common.response import CustomException


class WorkflowTemplateService:
    """Service for managing workflow templates"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== CRUD OPERATIONS ====================
    
    def create_template(self, template_data: Dict[str, Any]) -> WorkflowTemplate:
        """
        Create new workflow template
        
        Args:
            template_data: Template configuration including workflow_definition
            
        Returns:
            Created template
        """
        # Check if template code already exists
        existing = self.db.query(WorkflowTemplate).filter(
            and_(
                WorkflowTemplate.tenant_id == self.tenant_id,
                WorkflowTemplate.template_code == template_data.get('template_code'),
                WorkflowTemplate.is_deleted == False
            )
        ).first()
        
        if existing:
            raise CustomException(
                status_code=400,
                message=f"Template code {template_data.get('template_code')} already exists"
            )
        
        # Validate workflow definition
        workflow_def = template_data.get('workflow_definition')
        if not workflow_def:
            raise CustomException(
                status_code=400,
                message="Workflow definition is required"
            )
        
        validation_result = self.validate_workflow_definition(workflow_def)
        if not validation_result['valid']:
            raise CustomException(
                status_code=400,
                message=f"Invalid workflow definition: {', '.join(validation_result['errors'])}"
            )
        
        # Create template
        template = WorkflowTemplate(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            **template_data
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def get_template(self, template_id: int) -> WorkflowTemplate:
        """Get template by ID"""
        template = self.db.query(WorkflowTemplate).filter(
            and_(
                WorkflowTemplate.id == template_id,
                WorkflowTemplate.tenant_id == self.tenant_id,
                WorkflowTemplate.is_deleted == False
            )
        ).first()
        
        if not template:
            raise CustomException(status_code=404, message="Template not found")
        
        return template
    
    def get_template_by_code(self, template_code: str) -> WorkflowTemplate:
        """Get template by code"""
        template = self.db.query(WorkflowTemplate).filter(
            and_(
                WorkflowTemplate.template_code == template_code,
                WorkflowTemplate.tenant_id == self.tenant_id,
                WorkflowTemplate.is_deleted == False,
                WorkflowTemplate.is_latest == True
            )
        ).first()
        
        if not template:
            raise CustomException(status_code=404, message="Template not found")
        
        return template
    
    def list_templates(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowTemplate]:
        """List templates with filters"""
        query = self.db.query(WorkflowTemplate).filter(
            and_(
                WorkflowTemplate.tenant_id == self.tenant_id,
                WorkflowTemplate.is_deleted == False,
                WorkflowTemplate.is_latest == True  # Only latest versions
            )
        )
        
        if category:
            query = query.filter(WorkflowTemplate.category == category)
        
        if status:
            query = query.filter(WorkflowTemplate.status == status)
        
        if is_active is not None:
            query = query.filter(WorkflowTemplate.is_active == is_active)
        
        templates = query.order_by(
            WorkflowTemplate.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return templates
    
    def update_template(
        self,
        template_id: int,
        update_data: Dict[str, Any]
    ) -> WorkflowTemplate:
        """Update template"""
        template = self.get_template(template_id)
        
        # If workflow definition is being updated, validate it
        if 'workflow_definition' in update_data:
            validation_result = self.validate_workflow_definition(
                update_data['workflow_definition']
            )
            if not validation_result['valid']:
                raise CustomException(
                    status_code=400,
                    message=f"Invalid workflow definition: {', '.join(validation_result['errors'])}"
                )
        
        # Don't allow updating template_code
        if 'template_code' in update_data:
            del update_data['template_code']
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def delete_template(self, template_id: int) -> bool:
        """Soft delete template"""
        template = self.get_template(template_id)
        
        # Check if template has active instances
        from backend.shared.database.workflow_models import WorkflowInstance
        active_instances = self.db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.workflow_template_id == template_id,
                WorkflowInstance.status.in_(['pending', 'in_progress']),
                WorkflowInstance.is_deleted == False
            )
        ).count()
        
        if active_instances > 0:
            raise CustomException(
                status_code=400,
                message=f"Cannot delete template with {active_instances} active instances"
            )
        
        template.is_deleted = True
        template.updated_by = self.user_id
        
        self.db.commit()
        return True
    
    # ==================== TEMPLATE OPERATIONS ====================
    
    def activate_template(self, template_id: int) -> WorkflowTemplate:
        """Activate a template"""
        template = self.get_template(template_id)
        
        # Validate workflow definition before activation
        validation_result = self.validate_workflow_definition(
            template.workflow_definition
        )
        if not validation_result['valid']:
            raise CustomException(
                status_code=400,
                message=f"Cannot activate invalid template: {', '.join(validation_result['errors'])}"
            )
        
        template.status = 'active'
        template.is_active = True
        template.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def deactivate_template(self, template_id: int) -> WorkflowTemplate:
        """Deactivate a template"""
        template = self.get_template(template_id)
        
        template.is_active = False
        template.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    def clone_template(
        self,
        template_id: int,
        new_code: str,
        new_name: str
    ) -> WorkflowTemplate:
        """Clone an existing template"""
        source_template = self.get_template(template_id)
        
        # Check if new code already exists
        existing = self.db.query(WorkflowTemplate).filter(
            and_(
                WorkflowTemplate.tenant_id == self.tenant_id,
                WorkflowTemplate.template_code == new_code,
                WorkflowTemplate.is_deleted == False
            )
        ).first()
        
        if existing:
            raise CustomException(
                status_code=400,
                message=f"Template code {new_code} already exists"
            )
        
        # Create new template
        cloned_template = WorkflowTemplate(
            tenant_id=self.tenant_id,
            template_code=new_code,
            template_name=new_name,
            description=source_template.description,
            category=source_template.category,
            workflow_type=source_template.workflow_type,
            trigger_event=source_template.trigger_event,
            workflow_definition=source_template.workflow_definition.copy(),
            default_variables=source_template.default_variables.copy() if source_template.default_variables else None,
            status='draft',
            is_active=False,
            default_sla_hours=source_template.default_sla_hours,
            escalation_enabled=source_template.escalation_enabled,
            escalation_rules=source_template.escalation_rules.copy() if source_template.escalation_rules else None,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(cloned_template)
        self.db.commit()
        self.db.refresh(cloned_template)
        
        return cloned_template
    
    def create_version(
        self,
        template_id: int,
        changes_description: str
    ) -> WorkflowTemplate:
        """Create new version of existing template"""
        current_template = self.get_template(template_id)
        
        # Mark current version as not latest
        current_template.is_latest = False
        
        # Create new version
        new_version = WorkflowTemplate(
            tenant_id=self.tenant_id,
            template_code=current_template.template_code,
            template_name=current_template.template_name,
            description=changes_description or current_template.description,
            category=current_template.category,
            workflow_type=current_template.workflow_type,
            trigger_event=current_template.trigger_event,
            workflow_definition=current_template.workflow_definition.copy(),
            default_variables=current_template.default_variables.copy() if current_template.default_variables else None,
            version=current_template.version + 1,
            parent_template_id=current_template.id,
            is_latest=True,
            status='draft',
            is_active=False,
            default_sla_hours=current_template.default_sla_hours,
            escalation_enabled=current_template.escalation_enabled,
            escalation_rules=current_template.escalation_rules.copy() if current_template.escalation_rules else None,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        return new_version
    
    def get_template_versions(self, template_code: str) -> List[WorkflowTemplate]:
        """Get all versions of a template"""
        versions = self.db.query(WorkflowTemplate).filter(
            and_(
                WorkflowTemplate.tenant_id == self.tenant_id,
                WorkflowTemplate.template_code == template_code,
                WorkflowTemplate.is_deleted == False
            )
        ).order_by(WorkflowTemplate.version.desc()).all()
        
        return versions
    
    # ==================== VALIDATION ====================
    
    def validate_workflow_definition(
        self,
        workflow_def: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate workflow definition structure
        
        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        errors = []
        warnings = []
        
        # Check required fields
        if not workflow_def.get('steps'):
            errors.append("Workflow must have at least one step")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        steps = workflow_def['steps']
        step_keys = {step.get('key') for step in steps if step.get('key')}
        
        # Validate steps
        has_start = False
        has_end = False
        
        for step in steps:
            # Check required step fields
            if not step.get('key'):
                errors.append("Each step must have a unique key")
            if not step.get('name'):
                errors.append(f"Step {step.get('key')} must have a name")
            if not step.get('type'):
                errors.append(f"Step {step.get('key')} must have a type")
            
            # Check step types
            step_type = step.get('type')
            if step_type == 'start':
                has_start = True
            elif step_type == 'end':
                has_end = True
            
            # Validate transitions
            if step_type not in ['end']:
                # Non-end steps should have next steps
                if 'next' not in step and 'transitions' not in step and 'conditions' not in step:
                    warnings.append(f"Step {step.get('key')} has no outgoing transitions")
                
                # Validate next step exists
                if 'next' in step and step['next'] not in step_keys:
                    errors.append(f"Step {step.get('key')} references non-existent step: {step['next']}")
                
                # Validate transitions
                if 'transitions' in step:
                    for transition in step['transitions']:
                        if transition.get('next') and transition['next'] not in step_keys:
                            errors.append(
                                f"Step {step.get('key')} transition references non-existent step: {transition['next']}"
                            )
                
                # Validate conditions
                if 'conditions' in step:
                    for condition in step['conditions']:
                        if condition.get('next') and condition['next'] not in step_keys:
                            errors.append(
                                f"Step {step.get('key')} condition references non-existent step: {condition['next']}"
                            )
        
        # Check for start and end steps
        if not has_start:
            warnings.append("Workflow should have a start step")
        if not has_end:
            warnings.append("Workflow should have at least one end step")
        
        # Check for cycles (basic check)
        # TODO: Implement proper cycle detection algorithm
        
        # Check for unreachable steps
        # TODO: Implement reachability analysis
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    # ==================== STATISTICS ====================
    
    def get_template_statistics(self, template_id: int) -> Dict[str, Any]:
        """Get usage statistics for a template"""
        from backend.shared.database.workflow_models import WorkflowInstance
        from sqlalchemy import func
        
        template = self.get_template(template_id)
        
        # Get instance statistics
        stats = self.db.query(
            func.count(WorkflowInstance.id).label('total_instances'),
            func.count(WorkflowInstance.id).filter(
                WorkflowInstance.status == 'completed'
            ).label('completed_instances'),
            func.count(WorkflowInstance.id).filter(
                WorkflowInstance.status == 'in_progress'
            ).label('in_progress_instances'),
            func.count(WorkflowInstance.id).filter(
                WorkflowInstance.status == 'failed'
            ).label('failed_instances')
        ).filter(
            and_(
                WorkflowInstance.workflow_template_id == template_id,
                WorkflowInstance.is_deleted == False
            )
        ).first()
        
        # Get status breakdown
        status_counts = self.db.query(
            WorkflowInstance.status,
            func.count(WorkflowInstance.id)
        ).filter(
            and_(
                WorkflowInstance.workflow_template_id == template_id,
                WorkflowInstance.is_deleted == False
            )
        ).group_by(WorkflowInstance.status).all()
        
        # Get average completion time
        avg_completion_time = self.db.query(
            func.avg(
                func.extract('epoch', WorkflowInstance.completed_at - WorkflowInstance.started_at) / 3600
            )
        ).filter(
            and_(
                WorkflowInstance.workflow_template_id == template_id,
                WorkflowInstance.status == 'completed',
                WorkflowInstance.started_at.isnot(None),
                WorkflowInstance.completed_at.isnot(None)
            )
        ).scalar()
        
        return {
            "template": {
                "id": template.id,
                "code": template.template_code,
                "name": template.template_name,
                "version": template.version,
                "status": template.status
            },
            "statistics": {
                "total_instances": stats.total_instances or 0,
                "completed_instances": stats.completed_instances or 0,
                "in_progress_instances": stats.in_progress_instances or 0,
                "failed_instances": stats.failed_instances or 0,
                "average_completion_hours": round(avg_completion_time or 0, 2)
            },
            "status_breakdown": {
                status: count for status, count in status_counts
            }
        }
    
    def get_categories(self) -> List[str]:
        """Get all workflow categories"""
        categories = self.db.query(WorkflowTemplate.category).filter(
            and_(
                WorkflowTemplate.tenant_id == self.tenant_id,
                WorkflowTemplate.is_deleted == False,
                WorkflowTemplate.category.isnot(None)
            )
        ).distinct().all()
        
        return [cat[0] for cat in categories if cat[0]]
