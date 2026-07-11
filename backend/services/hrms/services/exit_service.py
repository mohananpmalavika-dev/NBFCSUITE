"""
Exit Management Service
Business logic for Exit Management operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID
import json

from backend.shared.database.hrms_models import (
    Resignation, ExitClearance, ExitSettlement, SettlementComponent,
    ExitDocument, Employee, ResignationType, ResignationStatus,
    ClearanceStatus, SettlementStatus, SettlementComponentType,
    ExitDocumentType
)
from backend.services.hrms.schemas.exit_schemas import (
    ResignationCreate, ResignationUpdate, ManagerReviewSchema,
    HRReviewSchema, ResignationApprovalSchema, ResignationRejectionSchema,
    ResignationWithdrawalSchema, ExitInterviewSchema, HandoverSchema,
    ClearanceCreate, ClearanceUpdate, ClearanceCompleteSchema,
    SettlementCreate, SettlementCalculationSchema, SettlementApprovalSchema,
    SettlementPaymentSchema, SettlementHoldSchema,
    SettlementComponentCreate, SettlementComponentUpdate,
    DocumentCreate, DocumentGenerateSchema, DocumentApprovalSchema,
    DocumentIssuanceSchema, ResignationFilter, ClearanceFilter,
    SettlementFilter, DocumentFilter, PaginationParams
)
from fastapi import HTTPException


class ExitManagementService:
    """Service class for Exit Management operations"""
    
    def __init__(self, db: Session, tenant_id: UUID, current_user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.current_user_id = current_user_id
    
    # ========================================================================
    # RESIGNATION MANAGEMENT
    # ========================================================================
    
    def create_resignation(self, data: ResignationCreate) -> Resignation:
        """Create a new resignation request"""
        # Generate resignation code
        resignation_code = self._generate_resignation_code()
        
        # Get employee details
        employee = self.db.query(Employee).filter(
            Employee.id == data.employee_id,
            Employee.tenant_id == self.tenant_id,
            Employee.is_deleted == False
        ).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Create resignation
        resignation = Resignation(
            tenant_id=self.tenant_id,
            resignation_code=resignation_code,
            employee_id=data.employee_id,
            resignation_type=data.resignation_type,
            resignation_date=data.resignation_date,
            last_working_date=data.last_working_date,
            notice_period_days=data.notice_period_days,
            reason_category=data.reason_category,
            reason_details=data.reason_details,
            feedback=data.feedback,
            resignation_letter_path=data.resignation_letter_path,
            supporting_documents=data.supporting_documents,
            reporting_manager_id=employee.reporting_manager_id,
            status=ResignationStatus.SUBMITTED,
            created_by=self.current_user_id,
            updated_by=self.current_user_id
        )
        
        self.db.add(resignation)
        self.db.commit()
        self.db.refresh(resignation)
        
        # Create default clearances
        self._create_default_clearances(resignation.id)
        
        return resignation
    
    def get_resignation(self, resignation_id: UUID) -> Optional[Resignation]:
        """Get resignation by ID"""
        return self.db.query(Resignation).filter(
            Resignation.id == resignation_id,
            Resignation.tenant_id == self.tenant_id,
            Resignation.is_deleted == False
        ).first()
    
    def list_resignations(
        self,
        filters: ResignationFilter,
        pagination: PaginationParams
    ) -> Tuple[List[Resignation], int]:
        """List resignations with filters and pagination"""
        query = self.db.query(Resignation).filter(
            Resignation.tenant_id == self.tenant_id,
            Resignation.is_deleted == False
        )
        
        # Apply filters
        if filters.employee_id:
            query = query.filter(Resignation.employee_id == filters.employee_id)
        if filters.resignation_type:
            query = query.filter(Resignation.resignation_type == filters.resignation_type)
        if filters.status:
            query = query.filter(Resignation.status == filters.status)
        if filters.reporting_manager_id:
            query = query.filter(Resignation.reporting_manager_id == filters.reporting_manager_id)
        if filters.resignation_date_from:
            query = query.filter(Resignation.resignation_date >= filters.resignation_date_from)
        if filters.resignation_date_to:
            query = query.filter(Resignation.resignation_date <= filters.resignation_date_to)
        if filters.last_working_date_from:
            query = query.filter(Resignation.last_working_date >= filters.last_working_date_from)
        if filters.last_working_date_to:
            query = query.filter(Resignation.last_working_date <= filters.last_working_date_to)
        if filters.search:
            query = query.filter(
                or_(
                    Resignation.resignation_code.ilike(f"%{filters.search}%"),
                    Resignation.reason_details.ilike(f"%{filters.search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if pagination.sort_order == "desc":
            query = query.order_by(desc(getattr(Resignation, pagination.sort_by, Resignation.created_at)))
        else:
            query = query.order_by(asc(getattr(Resignation, pagination.sort_by, Resignation.created_at)))
        
        # Apply pagination
        offset = (pagination.page - 1) * pagination.per_page
        items = query.offset(offset).limit(pagination.per_page).all()
        
        return items, total
    
    def update_resignation(
        self,
        resignation_id: UUID,
        data: ResignationUpdate
    ) -> Resignation:
        """Update resignation details"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        # Only allow updates if status is SUBMITTED or UNDER_REVIEW
        if resignation.status not in [ResignationStatus.SUBMITTED, ResignationStatus.UNDER_REVIEW]:
            raise HTTPException(
                status_code=400,
                detail="Cannot update resignation in current status"
            )
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(resignation, field, value)
        
        resignation.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(resignation)
        
        return resignation
    
    def manager_review(
        self,
        resignation_id: UUID,
        data: ManagerReviewSchema
    ) -> Resignation:
        """Manager review of resignation"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        if resignation.status != ResignationStatus.SUBMITTED:
            raise HTTPException(
                status_code=400,
                detail="Resignation not in submitted status"
            )
        
        resignation.manager_comments = data.manager_comments
        resignation.manager_recommendation = data.manager_recommendation
        resignation.manager_reviewed_date = datetime.utcnow()
        
        if data.manager_recommendation == "counter_offer":
            resignation.counter_offer_made = True
            resignation.counter_offer_details = data.counter_offer_details
        
        resignation.status = ResignationStatus.UNDER_REVIEW
        resignation.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(resignation)
        
        return resignation
    
    def hr_review(
        self,
        resignation_id: UUID,
        data: HRReviewSchema
    ) -> Resignation:
        """HR review of resignation"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        resignation.hr_comments = data.hr_comments
        resignation.hr_reviewed_date = datetime.utcnow()
        resignation.hr_reviewer_id = self.current_user_id
        resignation.re_employment_eligible = data.re_employment_eligible
        resignation.blacklist_flag = data.blacklist_flag
        resignation.blacklist_reason = data.blacklist_reason
        resignation.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(resignation)
        
        return resignation
    
    def approve_resignation(
        self,
        resignation_id: UUID,
        data: ResignationApprovalSchema
    ) -> Resignation:
        """Approve resignation"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        if resignation.status not in [ResignationStatus.SUBMITTED, ResignationStatus.UNDER_REVIEW]:
            raise HTTPException(
                status_code=400,
                detail="Cannot approve resignation in current status"
            )
        
        resignation.status = ResignationStatus.APPROVED
        resignation.approved_by_id = self.current_user_id
        resignation.approved_date = datetime.utcnow()
        resignation.approval_comments = data.approval_comments
        resignation.actual_last_working_date = data.actual_last_working_date
        resignation.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(resignation)
        
        # Create settlement record
        self._create_settlement(resignation)
        
        return resignation
    
    def reject_resignation(
        self,
        resignation_id: UUID,
        data: ResignationRejectionSchema
    ) -> Resignation:
        """Reject resignation"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        resignation.status = ResignationStatus.REJECTED
        resignation.rejected_date = datetime.utcnow()
        resignation.rejection_reason = data.rejection_reason
        resignation.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(resignation)
        
        return resignation
    
    def withdraw_resignation(
        self,
        resignation_id: UUID,
        data: ResignationWithdrawalSchema
    ) -> Resignation:
        """Withdraw resignation"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        if resignation.status not in [ResignationStatus.SUBMITTED, ResignationStatus.UNDER_REVIEW]:
            raise HTTPException(
                status_code=400,
                detail="Cannot withdraw resignation in current status"
            )
        
        resignation.status = ResignationStatus.WITHDRAWN
        resignation.withdrawn_date = datetime.utcnow()
        resignation.withdrawal_reason = data.withdrawal_reason
        resignation.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(resignation)
        
        return resignation
    
    def conduct_exit_interview(
        self,
        resignation_id: UUID,
        data: ExitInterviewSchema
    ) -> Resignation:
        """Conduct exit interview"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        resignation.exit_interview_scheduled = True
        resignation.exit_interview_date = data.exit_interview_date
        resignation.exit_interview_conducted_by_id = self.current_user_id
        resignation.exit_interview_notes = data.exit_interview_notes
        if data.feedback:
            resignation.feedback = data.feedback
        resignation.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(resignation)
        
        return resignation
    
    def complete_handover(
        self,
        resignation_id: UUID,
        data: HandoverSchema
    ) -> Resignation:
        """Complete handover process"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        resignation.handover_completed = True
        resignation.handover_to_employee_id = data.handover_to_employee_id
        resignation.handover_notes = data.handover_notes
        resignation.handover_document_path = data.handover_document_path
        resignation.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(resignation)
        
        return resignation
    
    def complete_exit(self, resignation_id: UUID) -> Resignation:
        """Mark exit as completed"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        if resignation.status != ResignationStatus.APPROVED:
            raise HTTPException(
                status_code=400,
                detail="Resignation must be approved before completion"
            )
        
        # Check if all clearances are completed
        pending_clearances = self.db.query(ExitClearance).filter(
            ExitClearance.resignation_id == resignation_id,
            ExitClearance.is_mandatory == True,
            ExitClearance.status.notin_([
                ClearanceStatus.COMPLETED,
                ClearanceStatus.NOT_APPLICABLE,
                ClearanceStatus.WAIVED
            ]),
            ExitClearance.is_deleted == False
        ).count()
        
        if pending_clearances > 0:
            raise HTTPException(
                status_code=400,
                detail=f"{pending_clearances} mandatory clearances are still pending"
            )
        
        # Check if settlement is paid
        settlement = self.db.query(ExitSettlement).filter(
            ExitSettlement.resignation_id == resignation_id,
            ExitSettlement.tenant_id == self.tenant_id,
            ExitSettlement.is_deleted == False
        ).first()
        
        if not settlement or settlement.status != SettlementStatus.PAID:
            raise HTTPException(
                status_code=400,
                detail="Settlement must be paid before exit completion"
            )
        
        resignation.status = ResignationStatus.COMPLETED
        resignation.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(resignation)
        
        return resignation
    
    # ========================================================================
    # CLEARANCE MANAGEMENT
    # ========================================================================
    
    def create_clearance(self, data: ClearanceCreate) -> ExitClearance:
        """Create a clearance"""
        # Verify resignation exists
        resignation = self.get_resignation(data.resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        clearance = ExitClearance(
            tenant_id=self.tenant_id,
            resignation_id=data.resignation_id,
            clearance_from=data.clearance_from,
            clearance_type=data.clearance_type,
            description=data.description,
            checklist_items=data.checklist_items,
            is_mandatory=data.is_mandatory,
            due_date=data.due_date,
            assigned_to_id=data.assigned_to_id,
            depends_on_clearance_id=data.depends_on_clearance_id,
            status=ClearanceStatus.PENDING,
            created_by=self.current_user_id,
            updated_by=self.current_user_id
        )
        
        if clearance.assigned_to_id:
            clearance.assigned_date = datetime.utcnow()
        
        self.db.add(clearance)
        self.db.commit()
        self.db.refresh(clearance)
        
        return clearance
    
    def get_clearance(self, clearance_id: UUID) -> Optional[ExitClearance]:
        """Get clearance by ID"""
        return self.db.query(ExitClearance).filter(
            ExitClearance.id == clearance_id,
            ExitClearance.tenant_id == self.tenant_id,
            ExitClearance.is_deleted == False
        ).first()
    
    def list_clearances(
        self,
        filters: ClearanceFilter,
        pagination: PaginationParams
    ) -> Tuple[List[ExitClearance], int]:
        """List clearances with filters"""
        query = self.db.query(ExitClearance).filter(
            ExitClearance.tenant_id == self.tenant_id,
            ExitClearance.is_deleted == False
        )
        
        if filters.resignation_id:
            query = query.filter(ExitClearance.resignation_id == filters.resignation_id)
        if filters.status:
            query = query.filter(ExitClearance.status == filters.status)
        if filters.assigned_to_id:
            query = query.filter(ExitClearance.assigned_to_id == filters.assigned_to_id)
        if filters.clearance_from:
            query = query.filter(ExitClearance.clearance_from.ilike(f"%{filters.clearance_from}%"))
        if filters.is_overdue is not None:
            query = query.filter(ExitClearance.is_overdue == filters.is_overdue)
        if filters.is_mandatory is not None:
            query = query.filter(ExitClearance.is_mandatory == filters.is_mandatory)
        
        total = query.count()
        
        if pagination.sort_order == "desc":
            query = query.order_by(desc(getattr(ExitClearance, pagination.sort_by, ExitClearance.created_at)))
        else:
            query = query.order_by(asc(getattr(ExitClearance, pagination.sort_by, ExitClearance.created_at)))
        
        offset = (pagination.page - 1) * pagination.per_page
        items = query.offset(offset).limit(pagination.per_page).all()
        
        return items, total
    
    def update_clearance(
        self,
        clearance_id: UUID,
        data: ClearanceUpdate
    ) -> ExitClearance:
        """Update clearance"""
        clearance = self.get_clearance(clearance_id)
        if not clearance:
            raise HTTPException(status_code=404, detail="Clearance not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(clearance, field, value)
        
        clearance.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(clearance)
        
        return clearance
    
    def complete_clearance(
        self,
        clearance_id: UUID,
        data: ClearanceCompleteSchema
    ) -> ExitClearance:
        """Mark clearance as completed"""
        clearance = self.get_clearance(clearance_id)
        if not clearance:
            raise HTTPException(status_code=404, detail="Clearance not found")
        
        if clearance.status == ClearanceStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Clearance already completed")
        
        clearance.status = ClearanceStatus.COMPLETED
        clearance.cleared_by_id = self.current_user_id
        clearance.cleared_date = datetime.utcnow()
        clearance.clearance_remarks = data.clearance_remarks
        clearance.supporting_documents = data.supporting_documents
        clearance.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(clearance)
        
        return clearance
    
    # ========================================================================
    # SETTLEMENT MANAGEMENT
    # ========================================================================
    
    def create_settlement(self, data: SettlementCreate) -> ExitSettlement:
        """Create settlement manually"""
        return self._create_settlement_internal(
            data.resignation_id,
            data.employee_id,
            data.settlement_from_date,
            data.settlement_to_date
        )
    
    def get_settlement(self, settlement_id: UUID) -> Optional[ExitSettlement]:
        """Get settlement by ID"""
        return self.db.query(ExitSettlement).filter(
            ExitSettlement.id == settlement_id,
            ExitSettlement.tenant_id == self.tenant_id,
            ExitSettlement.is_deleted == False
        ).first()
    
    def get_settlement_by_resignation(self, resignation_id: UUID) -> Optional[ExitSettlement]:
        """Get settlement by resignation ID"""
        return self.db.query(ExitSettlement).filter(
            ExitSettlement.resignation_id == resignation_id,
            ExitSettlement.tenant_id == self.tenant_id,
            ExitSettlement.is_deleted == False
        ).first()
    
    def calculate_settlement(
        self,
        settlement_id: UUID,
        data: SettlementCalculationSchema
    ) -> ExitSettlement:
        """Calculate settlement amounts"""
        settlement = self.get_settlement(settlement_id)
        if not settlement:
            raise HTTPException(status_code=404, detail="Settlement not found")
        
        # Update calculation fields
        settlement.basic_salary_days = data.basic_salary_days
        settlement.basic_salary_amount = data.basic_salary_amount
        settlement.total_leave_balance = data.total_leave_balance
        settlement.encashable_leaves = data.encashable_leaves
        settlement.leave_encashment_amount = data.leave_encashment_amount
        settlement.notice_period_shortfall_days = data.notice_period_shortfall_days
        settlement.notice_pay_recovery = data.notice_pay_recovery
        settlement.years_of_service = data.years_of_service
        settlement.gratuity_eligible = data.gratuity_eligible
        settlement.gratuity_amount = data.gratuity_amount
        settlement.bonus_amount = data.bonus_amount
        settlement.incentive_amount = data.incentive_amount
        settlement.pending_reimbursement_amount = data.pending_reimbursement_amount
        settlement.loan_recovery = data.loan_recovery
        settlement.advance_recovery = data.advance_recovery
        settlement.asset_loss_recovery = data.asset_loss_recovery
        settlement.other_recovery = data.other_recovery
        settlement.recovery_remarks = data.recovery_remarks
        settlement.tds_amount = data.tds_amount
        settlement.professional_tax = data.professional_tax
        settlement.calculation_remarks = data.calculation_remarks
        
        # Calculate totals
        settlement.gross_payable = (
            data.basic_salary_amount +
            data.leave_encashment_amount +
            data.gratuity_amount +
            data.bonus_amount +
            data.incentive_amount +
            data.pending_reimbursement_amount
        )
        
        settlement.total_deductions = (
            data.notice_pay_recovery +
            data.loan_recovery +
            data.advance_recovery +
            data.asset_loss_recovery +
            data.other_recovery +
            data.tds_amount +
            data.professional_tax
        )
        
        settlement.net_payable = settlement.gross_payable - settlement.total_deductions
        
        settlement.status = SettlementStatus.CALCULATED
        settlement.calculated_by_id = self.current_user_id
        settlement.calculated_date = datetime.utcnow()
        settlement.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(settlement)
        
        return settlement
    
    def approve_settlement(
        self,
        settlement_id: UUID,
        data: SettlementApprovalSchema
    ) -> ExitSettlement:
        """Approve settlement"""
        settlement = self.get_settlement(settlement_id)
        if not settlement:
            raise HTTPException(status_code=404, detail="Settlement not found")
        
        if settlement.status != SettlementStatus.CALCULATED:
            raise HTTPException(
                status_code=400,
                detail="Settlement must be calculated before approval"
            )
        
        settlement.status = SettlementStatus.APPROVED
        settlement.approved_by_id = self.current_user_id
        settlement.approved_date = datetime.utcnow()
        settlement.approval_remarks = data.approval_remarks
        settlement.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(settlement)
        
        return settlement
    
    def process_settlement_payment(
        self,
        settlement_id: UUID,
        data: SettlementPaymentSchema
    ) -> ExitSettlement:
        """Process settlement payment"""
        settlement = self.get_settlement(settlement_id)
        if not settlement:
            raise HTTPException(status_code=404, detail="Settlement not found")
        
        if settlement.status != SettlementStatus.APPROVED:
            raise HTTPException(
                status_code=400,
                detail="Settlement must be approved before payment"
            )
        
        settlement.status = SettlementStatus.PAID
        settlement.payment_date = data.payment_date
        settlement.payment_mode = data.payment_mode
        settlement.payment_reference = data.payment_reference
        settlement.bank_account_number = data.bank_account_number
        settlement.bank_name = data.bank_name
        settlement.bank_ifsc_code = data.bank_ifsc_code
        settlement.finance_processor_id = self.current_user_id
        settlement.finance_processed_date = datetime.utcnow()
        settlement.finance_remarks = data.finance_remarks
        settlement.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(settlement)
        
        return settlement
    
    def hold_settlement(
        self,
        settlement_id: UUID,
        data: SettlementHoldSchema
    ) -> ExitSettlement:
        """Put settlement on hold"""
        settlement = self.get_settlement(settlement_id)
        if not settlement:
            raise HTTPException(status_code=404, detail="Settlement not found")
        
        settlement.status = SettlementStatus.ON_HOLD
        settlement.hold_reason = data.hold_reason
        settlement.hold_until_date = data.hold_until_date
        settlement.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(settlement)
        
        return settlement
    
    # ========================================================================
    # SETTLEMENT COMPONENTS
    # ========================================================================
    
    def add_settlement_component(
        self,
        data: SettlementComponentCreate
    ) -> SettlementComponent:
        """Add component to settlement"""
        settlement = self.get_settlement(data.settlement_id)
        if not settlement:
            raise HTTPException(status_code=404, detail="Settlement not found")
        
        component = SettlementComponent(
            tenant_id=self.tenant_id,
            settlement_id=data.settlement_id,
            component_type=data.component_type,
            component_name=data.component_name,
            description=data.description,
            amount=data.amount,
            is_deduction=data.is_deduction,
            calculation_basis=data.calculation_basis,
            quantity=data.quantity,
            rate=data.rate,
            is_taxable=data.is_taxable,
            tax_amount=data.tax_amount,
            remarks=data.remarks,
            created_by=self.current_user_id,
            updated_by=self.current_user_id
        )
        
        self.db.add(component)
        self.db.commit()
        self.db.refresh(component)
        
        # Recalculate settlement totals
        self._recalculate_settlement_totals(data.settlement_id)
        
        return component
    
    def list_settlement_components(
        self,
        settlement_id: UUID
    ) -> List[SettlementComponent]:
        """List all components of a settlement"""
        return self.db.query(SettlementComponent).filter(
            SettlementComponent.settlement_id == settlement_id,
            SettlementComponent.tenant_id == self.tenant_id,
            SettlementComponent.is_deleted == False
        ).all()
    
    # ========================================================================
    # DOCUMENT MANAGEMENT
    # ========================================================================
    
    def create_document(self, data: DocumentCreate) -> ExitDocument:
        """Create exit document"""
        # Generate document code
        document_code = self._generate_document_code(data.document_type)
        
        document = ExitDocument(
            tenant_id=self.tenant_id,
            document_code=document_code,
            resignation_id=data.resignation_id,
            employee_id=data.employee_id,
            document_type=data.document_type,
            document_name=data.document_name,
            description=data.description,
            template_name=data.template_name,
            document_content=data.document_content,
            document_path=data.document_path,
            document_url=data.document_url,
            created_by=self.current_user_id,
            updated_by=self.current_user_id
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def generate_document(
        self,
        resignation_id: UUID,
        data: DocumentGenerateSchema
    ) -> ExitDocument:
        """Generate exit document from template"""
        resignation = self.get_resignation(resignation_id)
        if not resignation:
            raise HTTPException(status_code=404, detail="Resignation not found")
        
        # Generate document code
        document_code = self._generate_document_code(data.document_type)
        
        # Generate document content based on type
        document_content = self._generate_document_content(
            resignation,
            data.document_type,
            data.template_name
        )
        
        document = ExitDocument(
            tenant_id=self.tenant_id,
            document_code=document_code,
            resignation_id=resignation_id,
            employee_id=resignation.employee_id,
            document_type=data.document_type,
            document_name=self._get_document_name(data.document_type),
            template_name=data.template_name,
            template_version=data.template_version,
            document_content=document_content,
            document_number=data.document_number,
            issue_place=data.issue_place,
            validity_date=data.validity_date,
            is_generated=True,
            generated_by_id=self.current_user_id,
            generated_date=datetime.utcnow(),
            created_by=self.current_user_id,
            updated_by=self.current_user_id
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def approve_document(
        self,
        document_id: UUID,
        data: DocumentApprovalSchema
    ) -> ExitDocument:
        """Approve exit document"""
        document = self.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document.is_approved = True
        document.approved_by_id = self.current_user_id
        document.approved_date = datetime.utcnow()
        document.approval_remarks = data.approval_remarks
        document.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def issue_document(
        self,
        document_id: UUID,
        data: DocumentIssuanceSchema
    ) -> ExitDocument:
        """Issue exit document"""
        document = self.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.is_approved:
            raise HTTPException(
                status_code=400,
                detail="Document must be approved before issuance"
            )
        
        document.is_issued = True
        document.issued_by_id = self.current_user_id
        document.issued_date = datetime.utcnow()
        document.issue_remarks = data.issue_remarks
        document.delivery_mode = data.delivery_mode
        document.recipient_email = data.recipient_email
        document.recipient_address = data.recipient_address
        document.delivered_date = datetime.utcnow()
        document.updated_by = self.current_user_id
        
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def get_document(self, document_id: UUID) -> Optional[ExitDocument]:
        """Get document by ID"""
        return self.db.query(ExitDocument).filter(
            ExitDocument.id == document_id,
            ExitDocument.tenant_id == self.tenant_id,
            ExitDocument.is_deleted == False
        ).first()
    
    def list_documents(
        self,
        filters: DocumentFilter,
        pagination: PaginationParams
    ) -> Tuple[List[ExitDocument], int]:
        """List documents with filters"""
        query = self.db.query(ExitDocument).filter(
            ExitDocument.tenant_id == self.tenant_id,
            ExitDocument.is_deleted == False
        )
        
        if filters.resignation_id:
            query = query.filter(ExitDocument.resignation_id == filters.resignation_id)
        if filters.employee_id:
            query = query.filter(ExitDocument.employee_id == filters.employee_id)
        if filters.document_type:
            query = query.filter(ExitDocument.document_type == filters.document_type)
        if filters.is_generated is not None:
            query = query.filter(ExitDocument.is_generated == filters.is_generated)
        if filters.is_approved is not None:
            query = query.filter(ExitDocument.is_approved == filters.is_approved)
        if filters.is_issued is not None:
            query = query.filter(ExitDocument.is_issued == filters.is_issued)
        
        total = query.count()
        
        if pagination.sort_order == "desc":
            query = query.order_by(desc(getattr(ExitDocument, pagination.sort_by, ExitDocument.created_at)))
        else:
            query = query.order_by(asc(getattr(ExitDocument, pagination.sort_by, ExitDocument.created_at)))
        
        offset = (pagination.page - 1) * pagination.per_page
        items = query.offset(offset).limit(pagination.per_page).all()
        
        return items, total
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _generate_resignation_code(self) -> str:
        """Generate unique resignation code"""
        today = date.today()
        prefix = f"RES-{today.strftime('%Y%m')}"
        
        # Get last resignation code for this month
        last_resignation = self.db.query(Resignation).filter(
            Resignation.tenant_id == self.tenant_id,
            Resignation.resignation_code.like(f"{prefix}%")
        ).order_by(desc(Resignation.resignation_code)).first()
        
        if last_resignation:
            last_seq = int(last_resignation.resignation_code.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f"{prefix}-{new_seq:04d}"
    
    def _generate_document_code(self, document_type: ExitDocumentType) -> str:
        """Generate unique document code"""
        today = date.today()
        type_prefix = {
            ExitDocumentType.EXPERIENCE_LETTER: "EXP",
            ExitDocumentType.RELIEVING_LETTER: "REL",
            ExitDocumentType.SERVICE_CERTIFICATE: "SVC",
            ExitDocumentType.FNF_STATEMENT: "FNF",
        }.get(document_type, "DOC")
        
        prefix = f"{type_prefix}-{today.strftime('%Y%m')}"
        
        last_document = self.db.query(ExitDocument).filter(
            ExitDocument.tenant_id == self.tenant_id,
            ExitDocument.document_code.like(f"{prefix}%")
        ).order_by(desc(ExitDocument.document_code)).first()
        
        if last_document:
            last_seq = int(last_document.document_code.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f"{prefix}-{new_seq:04d}"
    
    def _create_default_clearances(self, resignation_id: UUID):
        """Create default clearance items"""
        default_clearances = [
            {
                "clearance_from": "IT Department",
                "clearance_type": "asset_return",
                "description": "Return of laptop, mobile, access cards, and other IT assets",
                "is_mandatory": True
            },
            {
                "clearance_from": "Admin Department",
                "clearance_type": "asset_return",
                "description": "Return of office keys, ID card, and other admin assets",
                "is_mandatory": True
            },
            {
                "clearance_from": "Finance Department",
                "clearance_type": "accounts_clearance",
                "description": "Settlement of advances, loans, and pending expenses",
                "is_mandatory": True
            },
            {
                "clearance_from": "HR Department",
                "clearance_type": "document_submission",
                "description": "Submission of exit interview form and other HR documents",
                "is_mandatory": True
            },
            {
                "clearance_from": "Reporting Manager",
                "clearance_type": "handover",
                "description": "Knowledge transfer and project handover",
                "is_mandatory": True
            }
        ]
        
        for clearance_data in default_clearances:
            clearance = ExitClearance(
                tenant_id=self.tenant_id,
                resignation_id=resignation_id,
                **clearance_data,
                status=ClearanceStatus.PENDING,
                created_by=self.current_user_id,
                updated_by=self.current_user_id
            )
            self.db.add(clearance)
        
        self.db.commit()
    
    def _create_settlement(self, resignation: Resignation):
        """Create settlement for approved resignation"""
        settlement_code = self._generate_settlement_code()
        
        # Calculate settlement period
        settlement_from_date = resignation.resignation_date
        settlement_to_date = resignation.actual_last_working_date or resignation.last_working_date
        
        settlement = ExitSettlement(
            tenant_id=self.tenant_id,
            settlement_code=settlement_code,
            resignation_id=resignation.id,
            employee_id=resignation.employee_id,
            settlement_from_date=settlement_from_date,
            settlement_to_date=settlement_to_date,
            status=SettlementStatus.PENDING,
            created_by=self.current_user_id,
            updated_by=self.current_user_id
        )
        
        self.db.add(settlement)
        self.db.commit()
    
    def _create_settlement_internal(
        self,
        resignation_id: UUID,
        employee_id: UUID,
        from_date: date,
        to_date: date
    ) -> ExitSettlement:
        """Internal method to create settlement"""
        settlement_code = self._generate_settlement_code()
        
        settlement = ExitSettlement(
            tenant_id=self.tenant_id,
            settlement_code=settlement_code,
            resignation_id=resignation_id,
            employee_id=employee_id,
            settlement_from_date=from_date,
            settlement_to_date=to_date,
            status=SettlementStatus.PENDING,
            created_by=self.current_user_id,
            updated_by=self.current_user_id
        )
        
        self.db.add(settlement)
        self.db.commit()
        self.db.refresh(settlement)
        
        return settlement
    
    def _generate_settlement_code(self) -> str:
        """Generate unique settlement code"""
        today = date.today()
        prefix = f"FNF-{today.strftime('%Y%m')}"
        
        last_settlement = self.db.query(ExitSettlement).filter(
            ExitSettlement.tenant_id == self.tenant_id,
            ExitSettlement.settlement_code.like(f"{prefix}%")
        ).order_by(desc(ExitSettlement.settlement_code)).first()
        
        if last_settlement:
            last_seq = int(last_settlement.settlement_code.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f"{prefix}-{new_seq:04d}"
    
    def _recalculate_settlement_totals(self, settlement_id: UUID):
        """Recalculate settlement totals based on components"""
        settlement = self.get_settlement(settlement_id)
        if not settlement:
            return
        
        components = self.list_settlement_components(settlement_id)
        
        gross_payable = sum(
            c.amount for c in components if not c.is_deduction
        )
        total_deductions = sum(
            c.amount for c in components if c.is_deduction
        )
        
        settlement.gross_payable = gross_payable
        settlement.total_deductions = total_deductions
        settlement.net_payable = gross_payable - total_deductions
        settlement.updated_by = self.current_user_id
        
        self.db.commit()
    
    def _generate_document_content(
        self,
        resignation: Resignation,
        document_type: ExitDocumentType,
        template_name: Optional[str]
    ) -> str:
        """Generate document content based on type"""
        # Fetch employee details
        employee = self.db.query(Employee).filter(
            Employee.id == resignation.employee_id,
            Employee.tenant_id == self.tenant_id
        ).first()
        
        if not employee:
            return ""
        
        # Basic templates - in production, these would come from a template engine
        if document_type == ExitDocumentType.EXPERIENCE_LETTER:
            return self._generate_experience_letter(employee, resignation)
        elif document_type == ExitDocumentType.RELIEVING_LETTER:
            return self._generate_relieving_letter(employee, resignation)
        elif document_type == ExitDocumentType.SERVICE_CERTIFICATE:
            return self._generate_service_certificate(employee, resignation)
        else:
            return f"Document content for {document_type.value}"
    
    def _generate_experience_letter(self, employee: Employee, resignation: Resignation) -> str:
        """Generate experience letter content"""
        return f"""
EXPERIENCE CERTIFICATE

This is to certify that {employee.first_name} {employee.last_name} 
(Employee ID: {employee.employee_code}) was employed with our organization 
from {employee.date_of_joining.strftime('%d-%b-%Y')} to {resignation.actual_last_working_date.strftime('%d-%b-%Y')}.

During their tenure, they worked as {employee.designation.designation_name if employee.designation else 'Employee'} 
in the {employee.department.department_name if employee.department else 'Department'}.

We wish them success in their future endeavors.

For [Company Name]
Authorized Signatory
"""
    
    def _generate_relieving_letter(self, employee: Employee, resignation: Resignation) -> str:
        """Generate relieving letter content"""
        return f"""
RELIEVING LETTER

Date: {datetime.now().strftime('%d-%b-%Y')}

This is to inform that {employee.first_name} {employee.last_name} 
(Employee ID: {employee.employee_code}) has been relieved from the services 
of [Company Name] effective {resignation.actual_last_working_date.strftime('%d-%b-%Y')}.

During their employment, they have completed all formalities and clearances.

We wish them all the best in their future career.

For [Company Name]
HR Department
"""
    
    def _generate_service_certificate(self, employee: Employee, resignation: Resignation) -> str:
        """Generate service certificate content"""
        return f"""
SERVICE CERTIFICATE

This is to certify that {employee.first_name} {employee.last_name}
(Employee ID: {employee.employee_code}) served [Company Name] 
from {employee.date_of_joining.strftime('%d-%b-%Y')} to {resignation.actual_last_working_date.strftime('%d-%b-%Y')}.

During the period of service, their conduct and performance were satisfactory.

This certificate is issued upon their request.

For [Company Name]
Authorized Signatory
"""
    
    def _get_document_name(self, document_type: ExitDocumentType) -> str:
        """Get human-readable document name"""
        names = {
            ExitDocumentType.RESIGNATION_LETTER: "Resignation Letter",
            ExitDocumentType.ACCEPTANCE_LETTER: "Resignation Acceptance Letter",
            ExitDocumentType.EXPERIENCE_LETTER: "Experience Certificate",
            ExitDocumentType.RELIEVING_LETTER: "Relieving Letter",
            ExitDocumentType.SERVICE_CERTIFICATE: "Service Certificate",
            ExitDocumentType.NOC: "No Objection Certificate",
            ExitDocumentType.CLEARANCE_FORM: "Clearance Form",
            ExitDocumentType.FNF_STATEMENT: "Full & Final Settlement Statement",
            ExitDocumentType.FORM_16: "Form 16",
            ExitDocumentType.PF_WITHDRAWAL: "PF Withdrawal Form",
            ExitDocumentType.GRATUITY_FORM: "Gratuity Form",
        }
        return names.get(document_type, "Exit Document")
    
    # ========================================================================
    # DASHBOARD AND STATISTICS
    # ========================================================================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get exit management dashboard statistics"""
        today = date.today()
        month_start = today.replace(day=1)
        
        # Resignations stats
        total_resignations = self.db.query(func.count(Resignation.id)).filter(
            Resignation.tenant_id == self.tenant_id,
            Resignation.is_deleted == False
        ).scalar()
        
        pending_resignations = self.db.query(func.count(Resignation.id)).filter(
            Resignation.tenant_id == self.tenant_id,
            Resignation.status.in_([ResignationStatus.SUBMITTED, ResignationStatus.UNDER_REVIEW]),
            Resignation.is_deleted == False
        ).scalar()
        
        approved_resignations = self.db.query(func.count(Resignation.id)).filter(
            Resignation.tenant_id == self.tenant_id,
            Resignation.status == ResignationStatus.APPROVED,
            Resignation.is_deleted == False
        ).scalar()
        
        resignations_this_month = self.db.query(func.count(Resignation.id)).filter(
            Resignation.tenant_id == self.tenant_id,
            Resignation.resignation_date >= month_start,
            Resignation.is_deleted == False
        ).scalar()
        
        # Clearances stats
        pending_clearances = self.db.query(func.count(ExitClearance.id)).filter(
            ExitClearance.tenant_id == self.tenant_id,
            ExitClearance.status == ClearanceStatus.PENDING,
            ExitClearance.is_deleted == False
        ).scalar()
        
        overdue_clearances = self.db.query(func.count(ExitClearance.id)).filter(
            ExitClearance.tenant_id == self.tenant_id,
            ExitClearance.is_overdue == True,
            ExitClearance.is_deleted == False
        ).scalar()
        
        # Settlements stats
        pending_settlements = self.db.query(func.count(ExitSettlement.id)).filter(
            ExitSettlement.tenant_id == self.tenant_id,
            ExitSettlement.status.in_([SettlementStatus.PENDING, SettlementStatus.CALCULATED]),
            ExitSettlement.is_deleted == False
        ).scalar()
        
        total_settlement_amount = self.db.query(func.sum(ExitSettlement.net_payable)).filter(
            ExitSettlement.tenant_id == self.tenant_id,
            ExitSettlement.status == SettlementStatus.PAID,
            ExitSettlement.is_deleted == False
        ).scalar() or Decimal('0.00')
        
        # Documents stats
        pending_documents = self.db.query(func.count(ExitDocument.id)).filter(
            ExitDocument.tenant_id == self.tenant_id,
            ExitDocument.is_issued == False,
            ExitDocument.is_deleted == False
        ).scalar()
        
        return {
            "total_resignations": total_resignations,
            "pending_resignations": pending_resignations,
            "approved_resignations": approved_resignations,
            "resignations_this_month": resignations_this_month,
            "pending_clearances": pending_clearances,
            "overdue_clearances": overdue_clearances,
            "pending_settlements": pending_settlements,
            "total_settlement_amount": float(total_settlement_amount),
            "pending_documents": pending_documents
        }
