"""
Legal - Litigation Management Router
API endpoints for case tracking, hearing management, and legal expense tracking
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.responses import success_response, error_response
from backend.services.legal.litigation_service import LitigationService
from backend.services.legal.litigation_schemas import (
    LitigationCaseCreate, LitigationCaseUpdate, LitigationCaseResponse,
    CaseHearingCreate, CaseHearingUpdate, CaseHearingResponse,
    LegalExpenseCreate, LegalExpenseUpdate, LegalExpenseResponse,
    CasePartyCreate, CasePartyUpdate, CasePartyResponse,
    CaseDocumentCreate, CaseDocumentUpdate, CaseDocumentResponse,
    CaseStatistics
)
from backend.shared.exceptions import NotFoundException, ValidationException


router = APIRouter(prefix="/api/v1/legal/litigation", tags=["Legal - Litigation Management"])


# ============================================================================
# CASE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/cases", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: LitigationCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new litigation case"""
    try:
        case = await LitigationService.create_case(
            db=db,
            case_data=case_data,
            tenant_id=tenant_id,
            user_id=UUID(current_user["id"])
        )
        return success_response(
            data={
                "id": str(case.id),
                "case_number": case.case_number,
                "case_title": case.case_title,
                "status": case.status.value
            },
            message="Litigation case created successfully"
        )
    except ValidationException as e:
        return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return error_response(message=f"Failed to create case: {str(e)}")


@router.get("/cases/{case_id}", response_model=dict)
async def get_case(
    case_id: UUID,
    include_details: bool = Query(False, description="Include hearings, expenses, parties, and documents"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get a litigation case by ID"""
    try:
        case = await LitigationService.get_case(
            db=db,
            case_id=case_id,
            tenant_id=tenant_id,
            include_details=include_details
        )
        if not case:
            return error_response(
                message=f"Case with ID {case_id} not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Build response
        case_data = {
            "id": str(case.id),
            "case_number": case.case_number,
            "case_title": case.case_title,
            "case_type": case.case_type.value,
            "status": case.status.value,
            "priority": case.priority.value,
            "court_name": case.court_name,
            "court_location": case.court_location,
            "judge_name": case.judge_name,
            "filing_date": str(case.filing_date),
            "next_hearing_date": str(case.next_hearing_date) if case.next_hearing_date else None,
            "claim_amount": float(case.claim_amount) if case.claim_amount else None,
            "awarded_amount": float(case.awarded_amount) if case.awarded_amount else None,
            "primary_advocate": case.primary_advocate,
            "advocate_firm": case.advocate_firm,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat()
        }
        
        if include_details:
            case_data["hearings"] = len(case.hearings) if hasattr(case, 'hearings') else 0
            case_data["expenses"] = len(case.expenses) if hasattr(case, 'expenses') else 0
            case_data["parties"] = len(case.parties) if hasattr(case, 'parties') else 0
            case_data["documents"] = len(case.documents) if hasattr(case, 'documents') else 0
        
        return success_response(data=case_data)
    except Exception as e:
        return error_response(message=f"Failed to fetch case: {str(e)}")


@router.get("/cases", response_model=dict)
async def get_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by case status"),
    case_type: Optional[str] = Query(None, description="Filter by case type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in case number, title, or court"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all litigation cases with filters"""
    try:
        cases, total = await LitigationService.get_cases(
            db=db,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
            status=status,
            case_type=case_type,
            priority=priority,
            search=search
        )
        
        cases_data = [{
            "id": str(case.id),
            "case_number": case.case_number,
            "case_title": case.case_title,
            "case_type": case.case_type.value,
            "status": case.status.value,
            "priority": case.priority.value,
            "court_name": case.court_name,
            "filing_date": str(case.filing_date),
            "next_hearing_date": str(case.next_hearing_date) if case.next_hearing_date else None,
            "primary_advocate": case.primary_advocate,
            "created_at": case.created_at.isoformat()
        } for case in cases]
        
        return success_response(
            data={
                "cases": cases_data,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        return error_response(message=f"Failed to fetch cases: {str(e)}")


@router.put("/cases/{case_id}", response_model=dict)
async def update_case(
    case_id: UUID,
    case_data: LitigationCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update a litigation case"""
    try:
        case = await LitigationService.update_case(
            db=db,
            case_id=case_id,
            case_data=case_data,
            tenant_id=tenant_id,
            user_id=UUID(current_user["id"])
        )
        return success_response(
            data={
                "id": str(case.id),
                "case_number": case.case_number,
                "status": case.status.value
            },
            message="Case updated successfully"
        )
    except NotFoundException as e:
        return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f"Failed to update case: {str(e)}")


@router.delete("/cases/{case_id}", response_model=dict)
async def delete_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete a litigation case"""
    try:
        await LitigationService.delete_case(
            db=db,
            case_id=case_id,
            tenant_id=tenant_id,
            user_id=UUID(current_user["id"])
        )
        return success_response(message="Case deleted successfully")
    except NotFoundException as e:
        return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f"Failed to delete case: {str(e)}")


# ============================================================================
# HEARING MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/hearings", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_hearing(
    hearing_data: CaseHearingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new case hearing"""
    try:
        hearing = await LitigationService.create_hearing(
            db=db,
            hearing_data=hearing_data,
            tenant_id=tenant_id,
            user_id=UUID(current_user["id"])
        )
        return success_response(
            data={
                "id": str(hearing.id),
                "hearing_number": hearing.hearing_number,
                "scheduled_date": hearing.scheduled_date.isoformat(),
                "hearing_type": hearing.hearing_type.value
            },
            message="Hearing scheduled successfully"
        )
    except NotFoundException as e:
        return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f"Failed to create hearing: {str(e)}")


@router.get("/cases/{case_id}/hearings", response_model=dict)
async def get_case_hearings(
    case_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get all hearings for a case"""
    try:
        hearings, total = await LitigationService.get_case_hearings(
            db=db,
            case_id=case_id,
            skip=skip,
            limit=limit
        )
        
        hearings_data = [{
            "id": str(hearing.id),
            "hearing_number": hearing.hearing_number,
            "hearing_type": hearing.hearing_type.value,
            "hearing_status": hearing.hearing_status.value,
            "scheduled_date": hearing.scheduled_date.isoformat(),
            "actual_date": hearing.actual_date.isoformat() if hearing.actual_date else None,
            "judge_name": hearing.judge_name,
            "next_hearing_date": hearing.next_hearing_date.isoformat() if hearing.next_hearing_date else None,
            "created_at": hearing.created_at.isoformat()
        } for hearing in hearings]
        
        return success_response(
            data={
                "hearings": hearings_data,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        return error_response(message=f"Failed to fetch hearings: {str(e)}")


@router.get("/hearings/upcoming", response_model=dict)
async def get_upcoming_hearings(
    days: int = Query(30, ge=1, le=365, description="Number of days to look ahead"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get upcoming hearings across all cases"""
    try:
        hearings, total = await LitigationService.get_upcoming_hearings(
            db=db,
            tenant_id=tenant_id,
            days=days,
            skip=skip,
            limit=limit
        )
        
        hearings_data = [{
            "id": str(hearing.id),
            "case_id": str(hearing.case_id),
            "hearing_number": hearing.hearing_number,
            "hearing_type": hearing.hearing_type.value,
            "scheduled_date": hearing.scheduled_date.isoformat(),
            "court_room": hearing.court_room,
            "judge_name": hearing.judge_name,
            "purpose": hearing.purpose
        } for hearing in hearings]
        
        return success_response(
            data={
                "hearings": hearings_data,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        return error_response(message=f"Failed to fetch upcoming hearings: {str(e)}")


@router.put("/hearings/{hearing_id}", response_model=dict)
async def update_hearing(
    hearing_id: UUID,
    hearing_data: CaseHearingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a case hearing"""
    try:
        hearing = await LitigationService.update_hearing(
            db=db,
            hearing_id=hearing_id,
            hearing_data=hearing_data,
            user_id=UUID(current_user["id"])
        )
        return success_response(
            data={
                "id": str(hearing.id),
                "hearing_status": hearing.hearing_status.value
            },
            message="Hearing updated successfully"
        )
    except NotFoundException as e:
        return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f"Failed to update hearing: {str(e)}")


# ============================================================================
# EXPENSE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/expenses", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: LegalExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new legal expense"""
    try:
        expense = await LitigationService.create_expense(
            db=db,
            expense_data=expense_data,
            tenant_id=tenant_id,
            user_id=UUID(current_user["id"])
        )
        return success_response(
            data={
                "id": str(expense.id),
                "expense_number": expense.expense_number,
                "amount": float(expense.total_amount),
                "category": expense.expense_category.value
            },
            message="Legal expense created successfully"
        )
    except NotFoundException as e:
        return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f"Failed to create expense: {str(e)}")


@router.get("/cases/{case_id}/expenses", response_model=dict)
async def get_case_expenses(
    case_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None, description="Filter by expense category"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all expenses for a case"""
    try:
        expenses, total = await LitigationService.get_case_expenses(
            db=db,
            case_id=case_id,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
            category=category
        )
        
        expenses_data = [{
            "id": str(expense.id),
            "expense_number": expense.expense_number,
            "expense_category": expense.expense_category.value,
            "description": expense.description,
            "amount": float(expense.amount),
            "tax_amount": float(expense.tax_amount) if expense.tax_amount else 0,
            "total_amount": float(expense.total_amount),
            "expense_date": str(expense.expense_date),
            "payee_name": expense.payee_name,
            "is_approved": expense.is_approved,
            "is_paid": expense.is_paid,
            "created_at": expense.created_at.isoformat()
        } for expense in expenses]
        
        # Calculate totals
        total_amount = sum(float(e.total_amount) for e in expenses)
        
        return success_response(
            data={
                "expenses": expenses_data,
                "total": total,
                "total_amount": total_amount,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        return error_response(message=f"Failed to fetch expenses: {str(e)}")


@router.put("/expenses/{expense_id}", response_model=dict)
async def update_expense(
    expense_id: UUID,
    expense_data: LegalExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update a legal expense"""
    try:
        expense = await LitigationService.update_expense(
            db=db,
            expense_id=expense_id,
            expense_data=expense_data,
            tenant_id=tenant_id
        )
        return success_response(
            data={
                "id": str(expense.id),
                "expense_number": expense.expense_number,
                "total_amount": float(expense.total_amount)
            },
            message="Expense updated successfully"
        )
    except NotFoundException as e:
        return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f"Failed to update expense: {str(e)}")


@router.post("/expenses/{expense_id}/approve", response_model=dict)
async def approve_expense(
    expense_id: UUID,
    remarks: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Approve a legal expense"""
    try:
        expense = await LitigationService.approve_expense(
            db=db,
            expense_id=expense_id,
            tenant_id=tenant_id,
            user_id=UUID(current_user["id"]),
            remarks=remarks
        )
        return success_response(
            data={
                "id": str(expense.id),
                "expense_number": expense.expense_number,
                "is_approved": expense.is_approved
            },
            message="Expense approved successfully"
        )
    except NotFoundException as e:
        return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f"Failed to approve expense: {str(e)}")


@router.post("/expenses/{expense_id}/mark-paid", response_model=dict)
async def mark_expense_paid(
    expense_id: UUID,
    payment_date: date,
    payment_reference: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Mark an expense as paid"""
    try:
        expense = await LitigationService.mark_expense_paid(
            db=db,
            expense_id=expense_id,
            tenant_id=tenant_id,
            user_id=UUID(current_user["id"]),
            payment_date=payment_date,
            payment_reference=payment_reference
        )
        return success_response(
            data={
                "id": str(expense.id),
                "expense_number": expense.expense_number,
                "is_paid": expense.is_paid
            },
            message="Expense marked as paid successfully"
        )
    except (NotFoundException, ValidationException) as e:
        return error_response(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND if isinstance(e, NotFoundException) else status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return error_response(message=f"Failed to mark expense as paid: {str(e)}")


# ============================================================================
# PARTY MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/parties", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_party(
    party_data: CasePartyCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new case party"""
    try:
        party = await LitigationService.create_party(
            db=db,
            party_data=party_data,
            tenant_id=tenant_id
        )
        return success_response(
            data={
                "id": str(party.id),
                "party_name": party.party_name,
                "party_role": party.party_role.value
            },
            message="Case party added successfully"
        )
    except NotFoundException as e:
        return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(message=f"Failed to create party: {str(e)}")


@router.get("/cases/{case_id}/parties", response_model=dict)
async def get_case_parties(
    case_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all parties for a case"""
    try:
        parties = await LitigationService.get_case_parties(
            db=db,
            case_id=case_id
        )
        
        parties_data = [{
            "id": str(party.id),
            "party_role": party.party_role.value,
            "party_name": party.party_name,
            "organization_name": party.organization_name,
            "email": party.email,
            "phone": party.phone,
            "is_represented": party.is_represented,
            "advocate_name": party.advocate_name,
            "advocate_firm": party.advocate_firm
        } for party in parties]
        
        return success_response(data={"parties": parties_data, "total": len(parties_data)})
    except Exception as e:
        return error_response(message=f"Failed to fetch parties: {str(e)}")


# ============================================================================
# STATISTICS & ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/statistics", response_model=dict)
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get litigation statistics"""
    try:
        stats = await LitigationService.get_case_statistics(
            db=db,
            tenant_id=tenant_id
        )
        
        return success_response(
            data={
                "total_cases": stats.total_cases,
                "active_cases": stats.active_cases,
                "won_cases": stats.won_cases,
                "lost_cases": stats.lost_cases,
                "settled_cases": stats.settled_cases,
                "pending_cases": stats.pending_cases,
                "total_claim_amount": float(stats.total_claim_amount),
                "total_awarded_amount": float(stats.total_awarded_amount),
                "total_legal_expenses": float(stats.total_legal_expenses),
                "upcoming_hearings": stats.upcoming_hearings
            }
        )
    except Exception as e:
        return error_response(message=f"Failed to fetch statistics: {str(e)}")
