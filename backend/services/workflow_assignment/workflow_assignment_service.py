"""
Workflow Assignment Service
Business logic for workflow assignment and approval routing
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

from .workflow_assignment_models import (
    WorkflowAssignment, WorkflowAssignmentFilter, WorkflowAssignmentStats,
    WorkflowAssignmentClone, AssignmentStatus, ApprovalRouting, StageAssignment,
    ApprovalLevel, CommitteeType, StageType, SLAUnit
)


class WorkflowAssignmentService:
    """Service for workflow assignment management"""
    
    def __init__(self):
        """Initialize service"""
        self.assignments_storage: Dict[str, WorkflowAssignment] = {}
    
    # ========================================================================
    # CRUD OPERATIONS
    # ========================================================================
    
    def create_assignment(
        self,
        assignment_data: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> WorkflowAssignment:
        """Create new workflow assignment"""
        assignment_id = str(uuid.uuid4())
        
        # Check if assignment code exists
        if any(a.assignment_code == assignment_data.get('assignment_code') 
               for a in self.assignments_storage.values() 
               if a.tenant_id == tenant_id):
            raise ValueError(f"Assignment code {assignment_data.get('assignment_code')} already exists")
        
        # Create assignment
        assignment = WorkflowAssignment(
            id=assignment_id,
            tenant_id=tenant_id,
            **assignment_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.assignments_storage[assignment_id] = assignment
        return assignment
    
    def get_assignment(self, assignment_id: str, tenant_id: str) -> WorkflowAssignment:
        """Get assignment by ID"""
        assignment = self.assignments_storage.get(assignment_id)
        if not assignment or assignment.tenant_id != tenant_id:
            raise ValueError(f"Assignment {assignment_id} not found")
        return assignment
    
    def update_assignment(
        self,
        assignment_id: str,
        assignment_data: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> WorkflowAssignment:
        """Update assignment"""
        assignment = self.get_assignment(assignment_id, tenant_id)
        
        for key, value in assignment_data.items():
            if hasattr(assignment, key) and key not in ['id', 'tenant_id', 'created_at', 'created_by']:
                setattr(assignment, key, value)
        
        assignment.updated_at = datetime.utcnow()
        assignment.updated_by = user_id
        
        self.assignments_storage[assignment_id] = assignment
        return assignment
    
    def delete_assignment(self, assignment_id: str, tenant_id: str) -> None:
        """Delete assignment"""
        assignment = self.get_assignment(assignment_id, tenant_id)
        del self.assignments_storage[assignment_id]
    
    def list_assignments(
        self,
        tenant_id: str,
        filters: Optional[WorkflowAssignmentFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowAssignment]:
        """List assignments with filters"""
        assignments = [a for a in self.assignments_storage.values() if a.tenant_id == tenant_id]
        
        if filters:
            if filters.status:
                assignments = [a for a in assignments if a.status == filters.status]
            if filters.product_id:
                assignments = [a for a in assignments if a.product_id == filters.product_id]
            if filters.product_code:
                assignments = [a for a in assignments if a.product_code == filters.product_code]
            if filters.workflow_template_id:
                assignments = [a for a in assignments if a.workflow_template_id == filters.workflow_template_id]
            if filters.search_term:
                term = filters.search_term.lower()
                assignments = [a for a in assignments if 
                            term in a.assignment_code.lower() or 
                            term in a.assignment_name.lower() or 
                            term in a.description.lower()]
        
        assignments.sort(key=lambda a: (a.priority, a.created_at), reverse=False)
        return assignments[skip:skip + limit]
    
    # ========================================================================
    # ASSIGNMENT OPERATIONS
    # ========================================================================
    
    def clone_assignment(
        self,
        assignment_id: str,
        clone_data: WorkflowAssignmentClone,
        tenant_id: str,
        user_id: str
    ) -> WorkflowAssignment:
        """Clone assignment"""
        original = self.get_assignment(assignment_id, tenant_id)
        
        assignment_data = original.dict(exclude={'id', 'created_at', 'updated_at', 'created_by', 'updated_by'})
        assignment_data['assignment_code'] = clone_data.new_assignment_code
        assignment_data['assignment_name'] = clone_data.new_assignment_name or f"{original.assignment_name} (Copy)"
        if clone_data.new_product_id:
            assignment_data['product_id'] = clone_data.new_product_id
        assignment_data['status'] = AssignmentStatus.DRAFT
        
        return self.create_assignment(assignment_data, tenant_id, user_id)
    
    def activate_assignment(self, assignment_id: str, tenant_id: str, user_id: str) -> WorkflowAssignment:
        """Activate assignment"""
        assignment = self.get_assignment(assignment_id, tenant_id)
        assignment.status = AssignmentStatus.ACTIVE
        assignment.updated_at = datetime.utcnow()
        assignment.updated_by = user_id
        self.assignments_storage[assignment_id] = assignment
        return assignment
    
    def deactivate_assignment(self, assignment_id: str, tenant_id: str, user_id: str) -> WorkflowAssignment:
        """Deactivate assignment"""
        assignment = self.get_assignment(assignment_id, tenant_id)
        assignment.status = AssignmentStatus.INACTIVE
        assignment.updated_at = datetime.utcnow()
        assignment.updated_by = user_id
        self.assignments_storage[assignment_id] = assignment
        return assignment
    
    # ========================================================================
    # APPROVAL ROUTING
    # ========================================================================
    
    def get_approval_routing(
        self,
        assignment_id: str,
        loan_amount: float,
        tenant_id: str
    ) -> ApprovalRouting:
        """Determine approval routing based on loan amount"""
        assignment = self.get_assignment(assignment_id, tenant_id)
        
        required_approvers = []
        required_committees = []
        estimated_sla_days = 0
        stages_to_execute = []
        
        # Determine required approvers from approval matrix
        for approval_config in assignment.approval_matrix:
            min_amt = approval_config.min_amount or 0
            max_amt = approval_config.max_amount or float('inf')
            
            if min_amt <= loan_amount <= max_amt:
                required_approvers.append(approval_config.level)
        
        # Determine required committees
        for committee in assignment.credit_committees:
            if committee.min_amount <= loan_amount:
                if committee.max_amount is None or loan_amount <= committee.max_amount:
                    required_committees.append(committee.committee_type)
        
        # Calculate estimated SLA
        for stage in assignment.stages:
            # Check if stage applies
            if stage.skip_if_amount_below and loan_amount < stage.skip_if_amount_below:
                continue
            
            stages_to_execute.append(stage.stage_name)
            
            # Add stage SLA
            sla_value = stage.sla_config.sla_value
            if stage.sla_config.sla_unit == SLAUnit.HOURS:
                estimated_sla_days += sla_value / 24
            elif stage.sla_config.sla_unit == SLAUnit.DAYS:
                estimated_sla_days += sla_value
            elif stage.sla_config.sla_unit == SLAUnit.BUSINESS_DAYS:
                estimated_sla_days += sla_value * 1.4  # Rough conversion
        
        return ApprovalRouting(
            loan_amount=loan_amount,
            product_code=assignment.product_code or "N/A",
            required_approvers=required_approvers,
            required_committees=required_committees,
            estimated_sla_days=int(estimated_sla_days),
            stages_to_execute=stages_to_execute
        )
    
    def get_stage_assignments(
        self,
        assignment_id: str,
        tenant_id: str
    ) -> List[StageAssignment]:
        """Get stage assignments"""
        assignment = self.get_assignment(assignment_id, tenant_id)
        
        stage_assignments = []
        
        for stage in assignment.stages:
            # Calculate SLA in hours
            sla_hours = stage.sla_config.sla_value
            if stage.sla_config.sla_unit == SLAUnit.DAYS:
                sla_hours = sla_hours * 24
            elif stage.sla_config.sla_unit == SLAUnit.BUSINESS_DAYS:
                sla_hours = sla_hours * 8  # 8 business hours per day
            
            stage_assignment = StageAssignment(
                stage_name=stage.stage_name,
                assigned_to_role=stage.assigned_role,
                assigned_to_user=stage.assigned_user_id,
                sla_hours=sla_hours,
                checker_required=stage.maker_checker_required,
                checker_level=stage.checker_level
            )
            
            stage_assignments.append(stage_assignment)
        
        return stage_assignments
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_stats(self, tenant_id: str) -> WorkflowAssignmentStats:
        """Get statistics"""
        assignments = [a for a in self.assignments_storage.values() if a.tenant_id == tenant_id]
        
        active_count = sum(1 for a in assignments if a.status == AssignmentStatus.ACTIVE)
        draft_count = sum(1 for a in assignments if a.status == AssignmentStatus.DRAFT)
        
        assignments_by_product = {}
        for assignment in assignments:
            if assignment.product_code:
                assignments_by_product[assignment.product_code] = assignments_by_product.get(assignment.product_code, 0) + 1
        
        total_stages = sum(len(a.stages) for a in assignments)
        avg_stages = total_stages / len(assignments) if assignments else 0
        
        return WorkflowAssignmentStats(
            total_assignments=len(assignments),
            active_assignments=active_count,
            draft_assignments=draft_count,
            assignments_by_product=assignments_by_product,
            avg_stages_per_workflow=round(avg_stages, 1)
        )
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    def validate_assignment_data(self, assignment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate assignment data"""
        errors = []
        warnings = []
        
        if not assignment_data.get('assignment_code'):
            errors.append("Assignment code is required")
        if not assignment_data.get('assignment_name'):
            errors.append("Assignment name is required")
        
        stages = assignment_data.get('stages', [])
        if len(stages) == 0:
            warnings.append("No workflow stages defined")
        
        # Check for duplicate stage orders
        stage_orders = [s.get('stage_order') for s in stages]
        if len(stage_orders) != len(set(stage_orders)):
            errors.append("Duplicate stage orders found")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


# Create service instance
workflow_assignment_service = WorkflowAssignmentService()
