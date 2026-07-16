"""
Workflow Engine Integrations

Connect workflow engine with existing NBFC modules:
- Loan Application Workflow
- Deposit Account Workflow
- Customer Onboarding Workflow
- Compliance Review Workflow
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from backend.services.workflow.execution_service import WorkflowExecutionService


class WorkflowIntegration:
    """Helper class for integrating workflows with NBFC modules"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.workflow_service = WorkflowExecutionService(db, tenant_id, user_id)
    
    # ==================== LOAN MODULE ====================
    
    def start_loan_approval_workflow(
        self,
        loan_application_id: int,
        loan_amount: float,
        customer_id: int,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Start loan approval workflow for a loan application
        
        Args:
            loan_application_id: Loan application ID
            loan_amount: Requested loan amount
            customer_id: Customer ID
            priority: Workflow priority (low, normal, high, urgent)
        
        Returns:
            Workflow instance details
        """
        variables = {
            "loan_application_id": loan_application_id,
            "loan_amount": loan_amount,
            "customer_id": customer_id,
            "approval_status": "pending"
        }
        
        instance = self.workflow_service.start_workflow(
            template_code="loan_approval_workflow",
            entity_type="loan_application",
            entity_id=loan_application_id,
            variables=variables,
            priority=priority
        )
        
        return {
            "success": True,
            "instance_id": instance.id,
            "instance_number": instance.instance_number,
            "message": "Loan approval workflow started"
        }
    
    def get_loan_workflow_status(
        self,
        loan_application_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get workflow status for a loan application"""
        from backend.shared.database.workflow_models import WorkflowInstance
        
        instance = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == self.tenant_id,
            WorkflowInstance.entity_type == "loan_application",
            WorkflowInstance.entity_id == loan_application_id,
            WorkflowInstance.is_deleted == False
        ).order_by(WorkflowInstance.created_at.desc()).first()
        
        if not instance:
            return None
        
        return {
            "instance_id": instance.id,
            "instance_number": instance.instance_number,
            "status": instance.status,
            "current_step": instance.current_step_id,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "result": instance.result
        }
    
    # ==================== DEPOSIT MODULE ====================
    
    def start_deposit_approval_workflow(
        self,
        account_id: int,
        customer_id: int,
        customer_email: str,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Start deposit account approval workflow"""
        variables = {
            "account_id": account_id,
            "customer_id": customer_id,
            "customer_email": customer_email,
            "approval_status": "pending"
        }
        
        instance = self.workflow_service.start_workflow(
            template_code="deposit_approval_workflow",
            entity_type="deposit_account",
            entity_id=account_id,
            variables=variables,
            priority=priority
        )
        
        return {
            "success": True,
            "instance_id": instance.id,
            "instance_number": instance.instance_number,
            "message": "Deposit approval workflow started"
        }
    
    # ==================== CUSTOMER MODULE ====================
    
    def start_kyc_verification_workflow(
        self,
        customer_id: int,
        priority: str = "high"
    ) -> Dict[str, Any]:
        """Start KYC verification workflow for customer"""
        variables = {
            "customer_id": customer_id,
            "documents_verified": False,
            "kyc_status": "pending"
        }
        
        instance = self.workflow_service.start_workflow(
            template_code="kyc_verification_workflow",
            entity_type="customer",
            entity_id=customer_id,
            variables=variables,
            priority=priority
        )
        
        return {
            "success": True,
            "instance_id": instance.id,
            "instance_number": instance.instance_number,
            "message": "KYC verification workflow started"
        }
    
    # ==================== GENERIC WORKFLOW ====================
    
    def start_custom_workflow(
        self,
        workflow_code: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        variables: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Start any custom workflow"""
        instance = self.workflow_service.start_workflow(
            template_code=workflow_code,
            entity_type=entity_type,
            entity_id=entity_id,
            variables=variables or {},
            priority=priority
        )
        
        return {
            "success": True,
            "instance_id": instance.id,
            "instance_number": instance.instance_number,
            "message": f"Workflow {workflow_code} started"
        }
    
    # ==================== WORKFLOW UTILITIES ====================
    
    def get_entity_workflows(
        self,
        entity_type: str,
        entity_id: int
    ) -> list:
        """Get all workflows for a specific entity"""
        from backend.shared.database.workflow_models import WorkflowInstance
        
        instances = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == self.tenant_id,
            WorkflowInstance.entity_type == entity_type,
            WorkflowInstance.entity_id == entity_id,
            WorkflowInstance.is_deleted == False
        ).order_by(WorkflowInstance.created_at.desc()).all()
        
        return [
            {
                "instance_id": inst.id,
                "instance_number": inst.instance_number,
                "status": inst.status,
                "started_at": inst.started_at.isoformat() if inst.started_at else None,
                "completed_at": inst.completed_at.isoformat() if inst.completed_at else None
            }
            for inst in instances
        ]
    
    def cancel_entity_workflows(
        self,
        entity_type: str,
        entity_id: int,
        reason: str
    ) -> Dict[str, Any]:
        """Cancel all active workflows for an entity"""
        from backend.shared.database.workflow_models import WorkflowInstance
        
        instances = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == self.tenant_id,
            WorkflowInstance.entity_type == entity_type,
            WorkflowInstance.entity_id == entity_id,
            WorkflowInstance.status.in_(['pending', 'in_progress']),
            WorkflowInstance.is_deleted == False
        ).all()
        
        cancelled_count = 0
        for instance in instances:
            result = self.workflow_service.cancel_workflow(instance.id, reason)
            if result:
                cancelled_count += 1
        
        return {
            "success": True,
            "cancelled_count": cancelled_count,
            "message": f"Cancelled {cancelled_count} workflows"
        }


# ==================== WORKFLOW HOOKS ====================

def on_loan_application_created(
    db: Session,
    tenant_id: int,
    user_id: int,
    loan_application_id: int,
    loan_amount: float,
    customer_id: int
) -> Dict[str, Any]:
    """
    Hook: Called when a loan application is created
    Automatically starts the loan approval workflow
    """
    integration = WorkflowIntegration(db, tenant_id, user_id)
    
    # Determine priority based on amount
    priority = "urgent" if loan_amount > 1000000 else "normal"
    
    return integration.start_loan_approval_workflow(
        loan_application_id=loan_application_id,
        loan_amount=loan_amount,
        customer_id=customer_id,
        priority=priority
    )


def on_deposit_account_created(
    db: Session,
    tenant_id: int,
    user_id: int,
    account_id: int,
    customer_id: int,
    customer_email: str
) -> Dict[str, Any]:
    """
    Hook: Called when a deposit account is created
    Automatically starts the deposit approval workflow
    """
    integration = WorkflowIntegration(db, tenant_id, user_id)
    
    return integration.start_deposit_approval_workflow(
        account_id=account_id,
        customer_id=customer_id,
        customer_email=customer_email
    )


def on_customer_registered(
    db: Session,
    tenant_id: int,
    user_id: int,
    customer_id: int
) -> Dict[str, Any]:
    """
    Hook: Called when a new customer is registered
    Automatically starts KYC verification workflow
    """
    integration = WorkflowIntegration(db, tenant_id, user_id)
    
    return integration.start_kyc_verification_workflow(
        customer_id=customer_id,
        priority="high"
    )
