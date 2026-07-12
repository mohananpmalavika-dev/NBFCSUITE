"""
Exit Management API Routes
RESTful endpoints for Exit Management operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_current_tenant
from backend.services.hrms.services.exit_service import ExitManagementService
from backend.services.hrms.schemas.exit_schemas import (
    # Resignation schemas
    ResignationCreate, ResignationUpdate, ResignationResponse,
    ManagerReviewSchema, HRReviewSchema, ResignationApprovalSchema,
    ResignationRejectionSchema, ResignationWithdrawalSchema,
    ExitInterviewSchema, HandoverSchema, ResignationFilter,
    # Clearance schemas
    ClearanceCreate, ClearanceUpdate, ClearanceResponse,
    ClearanceCompleteSchema, ClearanceFilter,
    # Settlement schemas
    SettlementCreate, SettlementCalculationSchema, SettlementResponse,
    SettlementApprovalSchema, SettlementPaymentSchema, SettlementHoldSchema,
    SettlementComponentCreate, SettlementComponentUpdate, SettlementComponentResponse,
    SettlementFilter,
    # Document schemas
    DocumentCreate, DocumentGenerateSchema, DocumentResponse,
    DocumentApprovalSchema, DocumentIssuanceSchema, DocumentFilter,
    # Common schemas
    PaginationParams, PaginatedResponse, ExitDashboardStats
)

router = APIRouter()


def get_exit_service(
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    current_user_id: UUID = Depends(get_current_user)
) -> ExitManagementService:
    """Dependency to get exit management service"""
    return ExitManagementService(db, tenant_id, current_user_id)


# ============================================================================
# RESIGNATION ENDPOINTS
# ============================================================================

@router.post("/resignations", response_model=ResignationResponse, status_code=status.HTTP_201_CREATED)
def create_resignation(
    data: ResignationCreate,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Create a new resignation request
    
    - **employee_id**: Employee submitting resignation
    - **resignation_date**: Date of resignation submission
    - **last_working_date**: Intended last working date
    - **notice_period_days**: Notice period as per policy
    - **reason_details**: Detailed reason for resignation
    """
    return service.create_resignation(data)


@router.get("/resignations/{resignation_id}", response_model=ResignationResponse)
def get_resignation(
    resignation_id: UUID,
    service: ExitManagementService = Depends(get_exit_service)
):
    """Get resignation details by ID"""
    resignation = service.get_resignation(resignation_id)
    if not resignation:
        raise HTTPException(status_code=404, detail="Resignation not found")
    return resignation


@router.get("/resignations", response_model=PaginatedResponse)
def list_resignations(
    employee_id: Optional[UUID] = Query(None),
    resignation_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    reporting_manager_id: Optional[UUID] = Query(None),
    resignation_date_from: Optional[str] = Query(None),
    resignation_date_to: Optional[str] = Query(None),
    last_working_date_from: Optional[str] = Query(None),
    last_working_date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    List resignations with filters and pagination
    
    - **employee_id**: Filter by employee
    - **status**: Filter by resignation status
    - **search**: Search in resignation code or reason
    """
    filters = ResignationFilter(
        employee_id=employee_id,
        resignation_type=resignation_type,
        status=status,
        reporting_manager_id=reporting_manager_id,
        resignation_date_from=resignation_date_from,
        resignation_date_to=resignation_date_to,
        last_working_date_from=last_working_date_from,
        last_working_date_to=last_working_date_to,
        search=search
    )
    
    pagination = PaginationParams(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    items, total = service.list_resignations(filters, pagination)
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.put("/resignations/{resignation_id}", response_model=ResignationResponse)
def update_resignation(
    resignation_id: UUID,
    data: ResignationUpdate,
    service: ExitManagementService = Depends(get_exit_service)
):
    """Update resignation details (only in SUBMITTED or UNDER_REVIEW status)"""
    return service.update_resignation(resignation_id, data)


@router.post("/resignations/{resignation_id}/manager-review", response_model=ResignationResponse)
def manager_review_resignation(
    resignation_id: UUID,
    data: ManagerReviewSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Manager review of resignation
    
    - **manager_comments**: Manager's comments on resignation
    - **manager_recommendation**: approve, reject, or counter_offer
    - **counter_offer_details**: Details if making counter offer
    """
    return service.manager_review(resignation_id, data)


@router.post("/resignations/{resignation_id}/hr-review", response_model=ResignationResponse)
def hr_review_resignation(
    resignation_id: UUID,
    data: HRReviewSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    HR review of resignation
    
    - **hr_comments**: HR's comments
    - **re_employment_eligible**: Whether eligible for re-employment
    - **blacklist_flag**: Whether to blacklist employee
    """
    return service.hr_review(resignation_id, data)


@router.post("/resignations/{resignation_id}/approve", response_model=ResignationResponse)
def approve_resignation(
    resignation_id: UUID,
    data: ResignationApprovalSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Approve resignation
    
    - **approval_comments**: Comments on approval
    - **actual_last_working_date**: Confirmed last working date
    """
    return service.approve_resignation(resignation_id, data)


@router.post("/resignations/{resignation_id}/reject", response_model=ResignationResponse)
def reject_resignation(
    resignation_id: UUID,
    data: ResignationRejectionSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """Reject resignation with reason"""
    return service.reject_resignation(resignation_id, data)


@router.post("/resignations/{resignation_id}/withdraw", response_model=ResignationResponse)
def withdraw_resignation(
    resignation_id: UUID,
    data: ResignationWithdrawalSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """Withdraw resignation (employee initiated)"""
    return service.withdraw_resignation(resignation_id, data)


@router.post("/resignations/{resignation_id}/exit-interview", response_model=ResignationResponse)
def conduct_exit_interview(
    resignation_id: UUID,
    data: ExitInterviewSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Conduct exit interview
    
    - **exit_interview_date**: Date/time of interview
    - **exit_interview_notes**: Notes from interview
    - **feedback**: Additional feedback from employee
    """
    return service.conduct_exit_interview(resignation_id, data)


@router.post("/resignations/{resignation_id}/handover", response_model=ResignationResponse)
def complete_handover(
    resignation_id: UUID,
    data: HandoverSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Complete handover process
    
    - **handover_to_employee_id**: Employee receiving handover
    - **handover_notes**: Handover details
    - **handover_document_path**: Path to handover document
    """
    return service.complete_handover(resignation_id, data)


@router.post("/resignations/{resignation_id}/complete", response_model=ResignationResponse)
def complete_exit(
    resignation_id: UUID,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Mark exit as completed
    
    Requires all mandatory clearances to be completed and settlement to be paid
    """
    return service.complete_exit(resignation_id)


# ============================================================================
# CLEARANCE ENDPOINTS
# ============================================================================

@router.post("/clearances", response_model=ClearanceResponse, status_code=status.HTTP_201_CREATED)
def create_clearance(
    data: ClearanceCreate,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Create a clearance item
    
    - **resignation_id**: Associated resignation
    - **clearance_from**: Department/function (IT, Admin, Finance, etc.)
    - **clearance_type**: Type of clearance (asset_return, accounts_clearance, etc.)
    - **is_mandatory**: Whether clearance is mandatory
    """
    return service.create_clearance(data)


@router.get("/clearances/{clearance_id}", response_model=ClearanceResponse)
def get_clearance(
    clearance_id: UUID,
    service: ExitManagementService = Depends(get_exit_service)
):
    """Get clearance details by ID"""
    clearance = service.get_clearance(clearance_id)
    if not clearance:
        raise HTTPException(status_code=404, detail="Clearance not found")
    return clearance


@router.get("/clearances", response_model=PaginatedResponse)
def list_clearances(
    resignation_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    assigned_to_id: Optional[UUID] = Query(None),
    clearance_from: Optional[str] = Query(None),
    is_overdue: Optional[bool] = Query(None),
    is_mandatory: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    List clearances with filters
    
    - **resignation_id**: Filter by resignation
    - **status**: Filter by clearance status
    - **assigned_to_id**: Filter by assigned employee
    - **is_overdue**: Filter overdue clearances
    """
    filters = ClearanceFilter(
        resignation_id=resignation_id,
        status=status,
        assigned_to_id=assigned_to_id,
        clearance_from=clearance_from,
        is_overdue=is_overdue,
        is_mandatory=is_mandatory
    )
    
    pagination = PaginationParams(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    items, total = service.list_clearances(filters, pagination)
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.put("/clearances/{clearance_id}", response_model=ClearanceResponse)
def update_clearance(
    clearance_id: UUID,
    data: ClearanceUpdate,
    service: ExitManagementService = Depends(get_exit_service)
):
    """Update clearance details"""
    return service.update_clearance(clearance_id, data)


@router.post("/clearances/{clearance_id}/complete", response_model=ClearanceResponse)
def complete_clearance(
    clearance_id: UUID,
    data: ClearanceCompleteSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Mark clearance as completed
    
    - **clearance_remarks**: Remarks on clearance completion
    - **supporting_documents**: Supporting document paths (JSON)
    """
    return service.complete_clearance(clearance_id, data)


# ============================================================================
# SETTLEMENT ENDPOINTS
# ============================================================================

@router.post("/settlements", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
def create_settlement(
    data: SettlementCreate,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Create settlement record manually
    
    - **resignation_id**: Associated resignation
    - **employee_id**: Employee
    - **settlement_from_date**: Settlement period start date
    - **settlement_to_date**: Settlement period end date
    """
    return service.create_settlement(data)


@router.get("/settlements/{settlement_id}", response_model=SettlementResponse)
def get_settlement(
    settlement_id: UUID,
    service: ExitManagementService = Depends(get_exit_service)
):
    """Get settlement details by ID"""
    settlement = service.get_settlement(settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    return settlement


@router.get("/resignations/{resignation_id}/settlement", response_model=SettlementResponse)
def get_settlement_by_resignation(
    resignation_id: UUID,
    service: ExitManagementService = Depends(get_exit_service)
):
    """Get settlement by resignation ID"""
    settlement = service.get_settlement_by_resignation(resignation_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found for this resignation")
    return settlement


@router.post("/settlements/{settlement_id}/calculate", response_model=SettlementResponse)
def calculate_settlement(
    settlement_id: UUID,
    data: SettlementCalculationSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Calculate settlement amounts
    
    - **basic_salary_amount**: Pending salary amount
    - **leave_encashment_amount**: Leave encashment
    - **gratuity_amount**: Gratuity payment
    - **loan_recovery**: Loan recovery amount
    - **notice_pay_recovery**: Notice pay shortfall recovery
    """
    return service.calculate_settlement(settlement_id, data)


@router.post("/settlements/{settlement_id}/approve", response_model=SettlementResponse)
def approve_settlement(
    settlement_id: UUID,
    data: SettlementApprovalSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Approve calculated settlement
    
    - **approval_remarks**: Comments on approval
    """
    return service.approve_settlement(settlement_id, data)


@router.post("/settlements/{settlement_id}/payment", response_model=SettlementResponse)
def process_settlement_payment(
    settlement_id: UUID,
    data: SettlementPaymentSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Process settlement payment
    
    - **payment_date**: Date of payment
    - **payment_mode**: bank_transfer, cheque, cash
    - **payment_reference**: Reference number
    - **bank_account_number**: Employee's bank account
    """
    return service.process_settlement_payment(settlement_id, data)


@router.post("/settlements/{settlement_id}/hold", response_model=SettlementResponse)
def hold_settlement(
    settlement_id: UUID,
    data: SettlementHoldSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Put settlement on hold
    
    - **hold_reason**: Reason for holding
    - **hold_until_date**: Hold until this date (optional)
    """
    return service.hold_settlement(settlement_id, data)


# ============================================================================
# SETTLEMENT COMPONENTS ENDPOINTS
# ============================================================================

@router.post("/settlement-components", response_model=SettlementComponentResponse, status_code=status.HTTP_201_CREATED)
def add_settlement_component(
    data: SettlementComponentCreate,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Add component to settlement
    
    - **settlement_id**: Associated settlement
    - **component_type**: salary, leave_encashment, bonus, gratuity, recovery, etc.
    - **amount**: Component amount
    - **is_deduction**: Whether this is a deduction (recovery)
    """
    return service.add_settlement_component(data)


@router.get("/settlements/{settlement_id}/components", response_model=List[SettlementComponentResponse])
def list_settlement_components(
    settlement_id: UUID,
    service: ExitManagementService = Depends(get_exit_service)
):
    """List all components of a settlement"""
    return service.list_settlement_components(settlement_id)


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    data: DocumentCreate,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Create exit document manually
    
    - **resignation_id**: Associated resignation
    - **employee_id**: Employee
    - **document_type**: experience_letter, relieving_letter, etc.
    - **document_name**: Document name
    """
    return service.create_document(data)


@router.post("/resignations/{resignation_id}/generate-document", response_model=DocumentResponse)
def generate_document(
    resignation_id: UUID,
    data: DocumentGenerateSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Generate exit document from template
    
    - **document_type**: Type of document to generate
    - **template_name**: Template to use (optional)
    - **document_number**: Reference number (optional)
    """
    return service.generate_document(resignation_id, data)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    service: ExitManagementService = Depends(get_exit_service)
):
    """Get document details by ID"""
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/documents", response_model=PaginatedResponse)
def list_documents(
    resignation_id: Optional[UUID] = Query(None),
    employee_id: Optional[UUID] = Query(None),
    document_type: Optional[str] = Query(None),
    is_generated: Optional[bool] = Query(None),
    is_approved: Optional[bool] = Query(None),
    is_issued: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    List documents with filters
    
    - **resignation_id**: Filter by resignation
    - **document_type**: Filter by document type
    - **is_issued**: Filter by issuance status
    """
    filters = DocumentFilter(
        resignation_id=resignation_id,
        employee_id=employee_id,
        document_type=document_type,
        is_generated=is_generated,
        is_approved=is_approved,
        is_issued=is_issued
    )
    
    pagination = PaginationParams(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    items, total = service.list_documents(filters, pagination)
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.post("/documents/{document_id}/approve", response_model=DocumentResponse)
def approve_document(
    document_id: UUID,
    data: DocumentApprovalSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Approve exit document
    
    - **approval_remarks**: Comments on approval
    """
    return service.approve_document(document_id, data)


@router.post("/documents/{document_id}/issue", response_model=DocumentResponse)
def issue_document(
    document_id: UUID,
    data: DocumentIssuanceSchema,
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Issue document to employee
    
    - **issue_remarks**: Issuance remarks
    - **delivery_mode**: email, hard_copy, courier, portal
    - **recipient_email**: Employee's email
    - **recipient_address**: Delivery address
    """
    return service.issue_document(document_id, data)


# ============================================================================
# DASHBOARD AND STATISTICS
# ============================================================================

@router.get("/dashboard/stats", response_model=ExitDashboardStats)
def get_dashboard_stats(
    service: ExitManagementService = Depends(get_exit_service)
):
    """
    Get exit management dashboard statistics
    
    Returns:
    - Total resignations count
    - Pending/approved resignations
    - Clearances status
    - Settlements status
    - Documents status
    """
    return service.get_dashboard_stats()
