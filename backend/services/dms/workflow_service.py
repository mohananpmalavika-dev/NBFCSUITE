"""
Workflow Service
Manages document approval workflows
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from backend.shared.database.dms_models import (
    DocumentWorkflow, WorkflowTemplate, DocumentApproval,
    WorkflowStatus, ApprovalStatus, Document
)
from .schemas import (
    WorkflowCreate, WorkflowResponse, WorkflowTemplateCreate,
    ApprovalAction, ApprovalResponse
)


class WorkflowService:
    """Service for workflow management"""

    def __init__(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        tenant_id: str
    ):
        self.db = db
        self.user_id = user_id
        self.tenant_id = tenant_id

    async def create_workflow(
        self,
        document_id: uuid.UUID,
        workflow_data: WorkflowCreate
    ) -> WorkflowResponse:
        """
        Create a new workflow for a document
        
        Args:
            document_id: Document ID
            workflow_data: Workflow configuration
            
        Returns:
            WorkflowResponse: Created workflow
        """
        # Verify document exists
        doc_query = select(Document).where(
            and_(
                Document.id == document_id,
                Document.tenant_id == self.tenant_id,
                Document.is_deleted == False
            )
        )
        doc_result = await self.db.execute(doc_query)
        document = doc_result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Create workflow
        workflow = DocumentWorkflow(
            tenant_id=self.tenant_id,
            document_id=document_id,
            workflow_name=workflow_data.workflow_name,
            workflow_type=workflow_data.workflow_type,
            description=workflow_data.description,
            status=WorkflowStatus.PENDING,
            current_step=1,
            total_steps=len(workflow_data.steps),
            initiated_by=self.user_id,
            priority=workflow_data.priority,
            due_date=workflow_data.due_date,
            is_sequential=workflow_data.is_sequential,
            require_all_approvals=workflow_data.require_all_approvals,
            created_by=self.user_id
        )
        self.db.add(workflow)
        await self.db.flush()

        # Create approval steps
        approvals = []
        for step_data in workflow_data.steps:
            approval = DocumentApproval(
                tenant_id=self.tenant_id,
                workflow_id=workflow.id,
                step_number=step_data.step_number,
                step_name=step_data.step_name,
                approver_id=step_data.approver_id,
                approver_role=step_data.approver_role,
                status=ApprovalStatus.PENDING,
                due_date=step_data.due_date,
                created_by=self.user_id
            )
            self.db.add(approval)
            approvals.append(approval)

        await self.db.commit()
        await self.db.refresh(workflow)

        # Load approvals for response
        workflow.approvals = approvals

        # Update document status
        document.status = "pending_review"
        await self.db.commit()

        return WorkflowResponse.model_validate(workflow)

    async def get_workflow(self, workflow_id: uuid.UUID) -> WorkflowResponse:
        """Get workflow by ID"""
        query = select(DocumentWorkflow).options(
            selectinload(DocumentWorkflow.approvals)
        ).where(
            and_(
                DocumentWorkflow.id == workflow_id,
                DocumentWorkflow.tenant_id == self.tenant_id,
                DocumentWorkflow.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )

        return WorkflowResponse.model_validate(workflow)

    async def get_document_workflows(
        self,
        document_id: uuid.UUID
    ) -> List[WorkflowResponse]:
        """Get all workflows for a document"""
        query = select(DocumentWorkflow).options(
            selectinload(DocumentWorkflow.approvals)
        ).where(
            and_(
                DocumentWorkflow.document_id == document_id,
                DocumentWorkflow.tenant_id == self.tenant_id,
                DocumentWorkflow.is_deleted == False
            )
        ).order_by(DocumentWorkflow.created_at.desc())

        result = await self.db.execute(query)
        workflows = result.scalars().all()

        return [WorkflowResponse.model_validate(w) for w in workflows]

    async def get_pending_approvals(
        self,
        approver_id: Optional[uuid.UUID] = None
    ) -> List[ApprovalResponse]:
        """Get pending approvals for a user"""
        target_user = approver_id or self.user_id

        query = select(DocumentApproval).where(
            and_(
                DocumentApproval.approver_id == target_user,
                DocumentApproval.status == ApprovalStatus.PENDING,
                DocumentApproval.tenant_id == self.tenant_id,
                DocumentApproval.is_deleted == False
            )
        ).order_by(DocumentApproval.due_date.asc())

        result = await self.db.execute(query)
        approvals = result.scalars().all()

        return [ApprovalResponse.model_validate(a) for a in approvals]

    async def process_approval(
        self,
        approval_id: uuid.UUID,
        action: ApprovalAction
    ) -> ApprovalResponse:
        """
        Process an approval (approve/reject)
        
        Args:
            approval_id: Approval ID
            action: Approval action
            
        Returns:
            ApprovalResponse: Updated approval
        """
        # Get approval
        query = select(DocumentApproval).where(
            and_(
                DocumentApproval.id == approval_id,
                DocumentApproval.tenant_id == self.tenant_id,
                DocumentApproval.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        approval = result.scalar_one_or_none()

        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found"
            )

        # Check if user is the approver
        if approval.approver_id != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to process this approval"
            )

        # Check if already processed
        if approval.status != ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Approval already {approval.status}"
            )

        # Update approval
        approval.status = action.status
        approval.comments = action.comments
        approval.attachments = action.attachments
        approval.response_date = datetime.utcnow()
        approval.updated_by = self.user_id

        await self.db.commit()
        await self.db.refresh(approval)

        # Update workflow status
        await self._update_workflow_status(approval.workflow_id)

        return ApprovalResponse.model_validate(approval)

    async def _update_workflow_status(self, workflow_id: uuid.UUID):
        """Update workflow status based on approval states"""
        # Get workflow with approvals
        query = select(DocumentWorkflow).options(
            selectinload(DocumentWorkflow.approvals)
        ).where(
            and_(
                DocumentWorkflow.id == workflow_id,
                DocumentWorkflow.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        workflow = result.scalar_one_or_none()

        if not workflow:
            return

        # Check approval states
        approvals = workflow.approvals
        all_approved = all(a.status == ApprovalStatus.APPROVED for a in approvals)
        any_rejected = any(a.status == ApprovalStatus.REJECTED for a in approvals)
        pending_count = sum(1 for a in approvals if a.status == ApprovalStatus.PENDING)

        # Update workflow status
        if any_rejected:
            workflow.status = WorkflowStatus.REJECTED
            workflow.completed_at = datetime.utcnow()
            workflow.completed_by = self.user_id
            
            # Update document status
            doc_query = select(Document).where(Document.id == workflow.document_id)
            doc_result = await self.db.execute(doc_query)
            document = doc_result.scalar_one_or_none()
            if document:
                document.status = "rejected"
                
        elif all_approved:
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            workflow.completed_by = self.user_id
            
            # Update document status
            doc_query = select(Document).where(Document.id == workflow.document_id)
            doc_result = await self.db.execute(doc_query)
            document = doc_result.scalar_one_or_none()
            if document:
                document.status = "approved"
                
        elif pending_count > 0:
            workflow.status = WorkflowStatus.IN_PROGRESS
            
            # Update current step
            for approval in sorted(approvals, key=lambda a: a.step_number):
                if approval.status == ApprovalStatus.PENDING:
                    workflow.current_step = approval.step_number
                    break

        await self.db.commit()

    async def cancel_workflow(
        self,
        workflow_id: uuid.UUID,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel a workflow"""
        query = select(DocumentWorkflow).where(
            and_(
                DocumentWorkflow.id == workflow_id,
                DocumentWorkflow.tenant_id == self.tenant_id,
                DocumentWorkflow.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        workflow = result.scalar_one_or_none()

        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )

        # Check if user is initiator or has permission
        if workflow.initiated_by != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workflow initiator can cancel"
            )

        # Cancel workflow
        workflow.status = WorkflowStatus.CANCELLED
        workflow.cancellation_reason = reason
        workflow.completed_at = datetime.utcnow()
        workflow.completed_by = self.user_id

        await self.db.commit()
        return True

    async def create_workflow_template(
        self,
        template_data: WorkflowTemplateCreate
    ) -> dict:
        """Create a reusable workflow template"""
        template = WorkflowTemplate(
            tenant_id=self.tenant_id,
            name=template_data.name,
            description=template_data.description,
            workflow_type=template_data.workflow_type,
            applicable_document_types=template_data.applicable_document_types,
            applicable_categories=template_data.applicable_categories,
            steps=template_data.steps,
            is_sequential=template_data.is_sequential,
            require_all_approvals=template_data.require_all_approvals,
            created_by=self.user_id
        )
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        return {
            "id": str(template.id),
            "name": template.name,
            "description": template.description,
            "workflow_type": template.workflow_type,
            "steps": template.steps,
            "created_at": template.created_at
        }

    async def get_workflow_templates(
        self,
        workflow_type: Optional[str] = None
    ) -> List[dict]:
        """Get workflow templates"""
        query = select(WorkflowTemplate).where(
            and_(
                WorkflowTemplate.tenant_id == self.tenant_id,
                WorkflowTemplate.is_active == True,
                WorkflowTemplate.is_deleted == False
            )
        )

        if workflow_type:
            query = query.where(WorkflowTemplate.workflow_type == workflow_type)

        result = await self.db.execute(query)
        templates = result.scalars().all()

        return [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "workflow_type": t.workflow_type,
                "steps": t.steps,
                "usage_count": t.usage_count,
                "created_at": t.created_at
            }
            for t in templates
        ]

    async def delegate_approval(
        self,
        approval_id: uuid.UUID,
        delegate_to: uuid.UUID,
        reason: Optional[str] = None
    ) -> ApprovalResponse:
        """Delegate an approval to another user"""
        # Get approval
        query = select(DocumentApproval).where(
            and_(
                DocumentApproval.id == approval_id,
                DocumentApproval.tenant_id == self.tenant_id,
                DocumentApproval.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        approval = result.scalar_one_or_none()

        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found"
            )

        # Check if user is the approver
        if approval.approver_id != self.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delegate this approval"
            )

        # Delegate
        approval.delegated_to = delegate_to
        approval.delegated_at = datetime.utcnow()
        approval.delegation_reason = reason
        approval.status = ApprovalStatus.DELEGATED
        approval.updated_by = self.user_id

        await self.db.commit()
        await self.db.refresh(approval)

        return ApprovalResponse.model_validate(approval)
