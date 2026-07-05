"""
Loan Approval Workflow Service
Multi-level approval management for loan applications
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict
from datetime import datetime, date
from decimal import Decimal

from backend.shared.database.loan_models import (
    LoanApplication, LoanApprovalWorkflow, LoanProduct
)
from backend.shared.database.customer_models import Customer
from .schemas import ApplicationStatus
from .credit_scoring_service import CreditScoringService


class ApprovalService:
    """Service for loan approval workflow management"""
    
    # Approval matrix configuration
    APPROVAL_MATRIX = {
        'level_1': {
            'role': 'credit_officer',
            'max_amount': Decimal('500000'),  # 5 lakhs
            'name': 'Credit Officer'
        },
        'level_2': {
            'role': 'manager',
            'max_amount': Decimal('2500000'),  # 25 lakhs
            'name': 'Branch Manager'
        },
        'level_3': {
            'role': 'senior_manager',
            'max_amount': None,  # No limit
            'name': 'Senior Manager'
        }
    }
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.credit_service = CreditScoringService(db, tenant_id)
    
    def determine_approval_levels(
        self,
        loan_amount: Decimal
    ) -> List[Dict]:
        """
        Determine required approval levels based on loan amount
        
        Returns list of required approval levels
        """
        required_levels = []
        
        # Level 1: Credit Officer (always required)
        required_levels.append({
            'level': 1,
            'role': self.APPROVAL_MATRIX['level_1']['role'],
            'name': self.APPROVAL_MATRIX['level_1']['name'],
            'max_amount': self.APPROVAL_MATRIX['level_1']['max_amount']
        })
        
        # Level 2: Manager (if amount > 5 lakhs)
        if loan_amount > self.APPROVAL_MATRIX['level_1']['max_amount']:
            required_levels.append({
                'level': 2,
                'role': self.APPROVAL_MATRIX['level_2']['role'],
                'name': self.APPROVAL_MATRIX['level_2']['name'],
                'max_amount': self.APPROVAL_MATRIX['level_2']['max_amount']
            })
        
        # Level 3: Senior Manager (if amount > 25 lakhs)
        if loan_amount > self.APPROVAL_MATRIX['level_2']['max_amount']:
            required_levels.append({
                'level': 3,
                'role': self.APPROVAL_MATRIX['level_3']['role'],
                'name': self.APPROVAL_MATRIX['level_3']['name'],
                'max_amount': self.APPROVAL_MATRIX['level_3']['max_amount']
            })
        
        return required_levels
    
    def create_approval_workflow(
        self,
        application_id: int,
        user_id: int
    ) -> List[LoanApprovalWorkflow]:
        """
        Create approval workflow for application
        
        Determines required levels and creates workflow records
        """
        # Get application
        application = self.db.query(LoanApplication).filter(
            and_(
                LoanApplication.id == application_id,
                LoanApplication.tenant_id == self.tenant_id,
                LoanApplication.is_deleted == False
            )
        ).first()
        
        if not application:
            raise ValueError("Application not found")
        
        # Check if workflow already exists
        existing = self.db.query(LoanApprovalWorkflow).filter(
            LoanApprovalWorkflow.loan_application_id == application_id
        ).first()
        
        if existing:
            raise ValueError("Approval workflow already exists for this application")
        
        # Determine required approval levels
        required_levels = self.determine_approval_levels(application.requested_amount)
        
        # Create workflow records
        workflows = []
        for level_config in required_levels:
            workflow = LoanApprovalWorkflow(
                tenant_id=self.tenant_id,
                loan_application_id=application_id,
                approval_level=level_config['level'],
                approver_role=level_config['role'],
                max_approval_amount=level_config['max_amount'],
                status='pending'
            )
            self.db.add(workflow)
            workflows.append(workflow)
        
        # Update application status
        application.status = ApplicationStatus.PENDING_APPROVAL.value
        application.approval_level = 0  # Start at level 0
        application.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # Refresh all workflows
        for workflow in workflows:
            self.db.refresh(workflow)
        
        return workflows
    
    def get_pending_approvals(
        self,
        approver_role: Optional[str] = None,
        approver_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get pending applications requiring approval
        
        Can filter by approver role or specific approver
        """
        query = self.db.query(LoanApprovalWorkflow).join(
            LoanApplication
        ).filter(
            and_(
                LoanApprovalWorkflow.tenant_id == self.tenant_id,
                LoanApprovalWorkflow.status == 'pending'
            )
        )
        
        if approver_role:
            query = query.filter(LoanApprovalWorkflow.approver_role == approver_role)
        
        if approver_id:
            query = query.filter(LoanApprovalWorkflow.approver_id == approver_id)
        
        workflows = query.all()
        
        # Build response with application details
        result = []
        for workflow in workflows:
            app = workflow.application
            
            # Check if previous levels are approved
            previous_approved = True
            if workflow.approval_level > 1:
                previous_workflows = self.db.query(LoanApprovalWorkflow).filter(
                    and_(
                        LoanApprovalWorkflow.loan_application_id == app.id,
                        LoanApprovalWorkflow.approval_level < workflow.approval_level
                    )
                ).all()
                
                previous_approved = all(w.status == 'approved' for w in previous_workflows)
            
            # Only include if previous levels are approved
            if previous_approved:
                result.append({
                    'workflow_id': workflow.id,
                    'application_id': app.id,
                    'application_number': app.application_number,
                    'customer_name': app.customer.full_name if app.customer else None,
                    'customer_code': app.customer.customer_code if app.customer else None,
                    'requested_amount': float(app.requested_amount),
                    'tenure_months': app.tenure_months,
                    'product_name': app.loan_product.product_name if app.loan_product else None,
                    'credit_score': app.credit_score,
                    'risk_rating': app.risk_rating,
                    'approval_level': workflow.approval_level,
                    'approver_role': workflow.approver_role,
                    'application_date': app.application_date.isoformat(),
                    'submission_date': app.submission_date.isoformat() if app.submission_date else None,
                    'pending_days': (date.today() - (app.submission_date or app.application_date)).days
                })
        
        return result
    
    def approve_application(
        self,
        workflow_id: int,
        approver_id: int,
        comments: Optional[str] = None,
        conditions: Optional[List[str]] = None,
        approved_amount: Optional[Decimal] = None
    ) -> LoanApprovalWorkflow:
        """
        Approve application at current level
        
        If all levels approved, moves application to approved status
        """
        # Get workflow
        workflow = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.id == workflow_id,
                LoanApprovalWorkflow.tenant_id == self.tenant_id
            )
        ).first()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        if workflow.status != 'pending':
            raise ValueError(f"Workflow is already {workflow.status}")
        
        # Get application
        application = workflow.application
        
        # Verify previous levels are approved
        if workflow.approval_level > 1:
            previous_workflows = self.db.query(LoanApprovalWorkflow).filter(
                and_(
                    LoanApprovalWorkflow.loan_application_id == application.id,
                    LoanApprovalWorkflow.approval_level < workflow.approval_level
                )
            ).all()
            
            if not all(w.status == 'approved' for w in previous_workflows):
                raise ValueError("Previous approval levels must be approved first")
        
        # Update workflow
        workflow.status = 'approved'
        workflow.decision = 'approve'
        workflow.approver_id = approver_id
        workflow.action_date = datetime.utcnow()
        workflow.comments = comments
        workflow.conditions = conditions
        
        # Update application approval level
        application.approval_level = workflow.approval_level
        
        # Set approved amount (can be different from requested)
        if approved_amount:
            application.approved_amount = approved_amount
        else:
            application.approved_amount = application.requested_amount
        
        # Check if all levels are approved
        all_workflows = self.db.query(LoanApprovalWorkflow).filter(
            LoanApprovalWorkflow.loan_application_id == application.id
        ).all()
        
        all_approved = all(w.status == 'approved' for w in all_workflows)
        
        if all_approved:
            # All levels approved - move to approved status
            application.status = ApplicationStatus.APPROVED.value
            application.approval_date = date.today()
            application.sub_status = 'ready_for_disbursement'
        else:
            # Move to next level
            application.sub_status = f'pending_level_{workflow.approval_level + 1}_approval'
        
        application.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(workflow)
        
        return workflow
    
    def reject_application(
        self,
        workflow_id: int,
        approver_id: int,
        rejection_reason: str,
        comments: Optional[str] = None
    ) -> LoanApprovalWorkflow:
        """
        Reject application
        
        Rejection at any level stops the entire workflow
        """
        # Get workflow
        workflow = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.id == workflow_id,
                LoanApprovalWorkflow.tenant_id == self.tenant_id
            )
        ).first()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        if workflow.status != 'pending':
            raise ValueError(f"Workflow is already {workflow.status}")
        
        # Update workflow
        workflow.status = 'rejected'
        workflow.decision = 'reject'
        workflow.approver_id = approver_id
        workflow.action_date = datetime.utcnow()
        workflow.comments = comments
        
        # Update application
        application = workflow.application
        application.status = ApplicationStatus.REJECTED.value
        application.rejection_date = date.today()
        application.rejection_reason = rejection_reason
        application.sub_status = f'rejected_at_level_{workflow.approval_level}'
        application.updated_at = datetime.utcnow()
        
        # Mark all pending workflows as cancelled
        pending_workflows = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.loan_application_id == application.id,
                LoanApprovalWorkflow.status == 'pending',
                LoanApprovalWorkflow.id != workflow_id
            )
        ).all()
        
        for w in pending_workflows:
            w.status = 'cancelled'
        
        self.db.commit()
        self.db.refresh(workflow)
        
        return workflow
    
    def return_application(
        self,
        workflow_id: int,
        approver_id: int,
        return_reason: str,
        comments: Optional[str] = None
    ) -> LoanApprovalWorkflow:
        """
        Return application to applicant for more information
        """
        # Get workflow
        workflow = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.id == workflow_id,
                LoanApprovalWorkflow.tenant_id == self.tenant_id
            )
        ).first()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        if workflow.status != 'pending':
            raise ValueError(f"Workflow is already {workflow.status}")
        
        # Update workflow
        workflow.status = 'returned'
        workflow.decision = 'return'
        workflow.approver_id = approver_id
        workflow.action_date = datetime.utcnow()
        workflow.comments = comments
        
        # Update application
        application = workflow.application
        application.status = ApplicationStatus.UNDER_REVIEW.value
        application.sub_status = 'returned_for_clarification'
        application.status_reason = return_reason
        application.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(workflow)
        
        return workflow
    
    def get_approval_history(
        self,
        application_id: int
    ) -> List[Dict]:
        """
        Get complete approval history for application
        """
        workflows = self.db.query(LoanApprovalWorkflow).filter(
            LoanApprovalWorkflow.loan_application_id == application_id
        ).order_by(LoanApprovalWorkflow.approval_level.asc()).all()
        
        history = []
        for workflow in workflows:
            history.append({
                'workflow_id': workflow.id,
                'level': workflow.approval_level,
                'role': workflow.approver_role,
                'status': workflow.status,
                'decision': workflow.decision,
                'approver_id': workflow.approver_id,
                'action_date': workflow.action_date.isoformat() if workflow.action_date else None,
                'comments': workflow.comments,
                'conditions': workflow.conditions,
                'created_at': workflow.created_at.isoformat()
            })
        
        return history
    
    def get_approval_statistics(self) -> Dict:
        """
        Get approval workflow statistics
        """
        # Pending approvals by level
        pending_level_1 = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.tenant_id == self.tenant_id,
                LoanApprovalWorkflow.approval_level == 1,
                LoanApprovalWorkflow.status == 'pending'
            )
        ).count()
        
        pending_level_2 = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.tenant_id == self.tenant_id,
                LoanApprovalWorkflow.approval_level == 2,
                LoanApprovalWorkflow.status == 'pending'
            )
        ).count()
        
        pending_level_3 = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.tenant_id == self.tenant_id,
                LoanApprovalWorkflow.approval_level == 3,
                LoanApprovalWorkflow.status == 'pending'
            )
        ).count()
        
        # Total approvals and rejections
        total_approved = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.tenant_id == self.tenant_id,
                LoanApprovalWorkflow.status == 'approved'
            )
        ).count()
        
        total_rejected = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.tenant_id == self.tenant_id,
                LoanApprovalWorkflow.status == 'rejected'
            )
        ).count()
        
        total_returned = self.db.query(LoanApprovalWorkflow).filter(
            and_(
                LoanApprovalWorkflow.tenant_id == self.tenant_id,
                LoanApprovalWorkflow.status == 'returned'
            )
        ).count()
        
        return {
            'pending_approvals': {
                'level_1': pending_level_1,
                'level_2': pending_level_2,
                'level_3': pending_level_3,
                'total': pending_level_1 + pending_level_2 + pending_level_3
            },
            'total_approved': total_approved,
            'total_rejected': total_rejected,
            'total_returned': total_returned,
            'approval_rate': round(
                (total_approved / (total_approved + total_rejected) * 100)
                if (total_approved + total_rejected) > 0 else 0,
                2
            )
        }
    
    def auto_move_to_approval(
        self,
        application_id: int,
        user_id: int
    ) -> Dict:
        """
        Automatically assess and move application to approval workflow
        
        Combines credit scoring and workflow creation
        """
        # Run credit assessment
        assessment = self.credit_service.assess_application(application_id)
        
        # Create approval workflow
        workflows = self.create_approval_workflow(application_id, user_id)
        
        return {
            'application_id': application_id,
            'credit_assessment': assessment,
            'approval_workflow': {
                'levels_required': len(workflows),
                'workflows': [
                    {
                        'level': w.approval_level,
                        'role': w.approver_role,
                        'status': w.status
                    }
                    for w in workflows
                ]
            },
            'message': f'Application moved to approval with {len(workflows)} level(s) required'
        }
