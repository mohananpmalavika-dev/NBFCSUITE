"""
Legal - Litigation Management Service
Business logic for case tracking, hearing management, and legal expense tracking
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, extract
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal

from backend.shared.database.legal_models import (
    LitigationCase, CaseHearing, LegalExpense, CaseParty, CaseDocument,
    CaseStatus, CaseType, CasePriority, HearingStatus, ExpenseCategory
)
from backend.services.legal.litigation_schemas import (
    LitigationCaseCreate, LitigationCaseUpdate, LitigationCaseResponse,
    CaseHearingCreate, CaseHearingUpdate, CaseHearingResponse,
    LegalExpenseCreate, LegalExpenseUpdate, LegalExpenseResponse,
    CasePartyCreate, CasePartyUpdate, CasePartyResponse,
    CaseDocumentCreate, CaseDocumentUpdate, CaseDocumentResponse,
    CaseStatistics, ExpenseStatistics, HearingStatistics
)
from backend.shared.exceptions import NotFoundException, ValidationException


class LitigationService:
    """Service for litigation management operations"""

    # ========================================================================
    # CASE MANAGEMENT
    # ========================================================================

    @staticmethod
    async def create_case(
        db: AsyncSession,
        case_data: LitigationCaseCreate,
        tenant_id: str,
        user_id: UUID
    ) -> LitigationCase:
        """Create a new litigation case"""
        
        # Check if case number already exists
        result = await db.execute(
            select(LitigationCase).where(
                and_(
                    LitigationCase.case_number == case_data.case_number,
                    LitigationCase.tenant_id == tenant_id,
                    LitigationCase.is_deleted == False
                )
            )
        )
        existing_case = result.scalar_one_or_none()
        if existing_case:
            raise ValidationException(f"Case number {case_data.case_number} already exists")
        
        # Create case
        case = LitigationCase(
            **case_data.model_dump(exclude_unset=True),
            tenant_id=tenant_id,
            status=CaseStatus.FILED,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(case)
        await db.commit()
        await db.refresh(case)
        
        return case

    @staticmethod
    async def get_case(
        db: AsyncSession,
        case_id: UUID,
        tenant_id: str,
        include_details: bool = False
    ) -> Optional[LitigationCase]:
        """Get a litigation case by ID"""
        query = select(LitigationCase).where(
            and_(
                LitigationCase.id == case_id,
                LitigationCase.tenant_id == tenant_id,
                LitigationCase.is_deleted == False
            )
        )
        
        if include_details:
            query = query.options(
                selectinload(LitigationCase.hearings),
                selectinload(LitigationCase.expenses),
                selectinload(LitigationCase.parties),
                selectinload(LitigationCase.documents)
            )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_cases(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        case_type: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[LitigationCase], int]:
        """Get all litigation cases with filters"""
        query = select(LitigationCase).where(
            and_(
                LitigationCase.tenant_id == tenant_id,
                LitigationCase.is_deleted == False
            )
        )
        
        # Apply filters
        if status:
            query = query.where(LitigationCase.status == status)
        if case_type:
            query = query.where(LitigationCase.case_type == case_type)
        if priority:
            query = query.where(LitigationCase.priority == priority)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    LitigationCase.case_number.ilike(search_pattern),
                    LitigationCase.case_title.ilike(search_pattern),
                    LitigationCase.court_name.ilike(search_pattern)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        # Apply pagination and order
        query = query.order_by(LitigationCase.filing_date.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        cases = result.scalars().all()
        
        return list(cases), total or 0

    @staticmethod
    async def update_case(
        db: AsyncSession,
        case_id: UUID,
        case_data: LitigationCaseUpdate,
        tenant_id: str,
        user_id: UUID
    ) -> Optional[LitigationCase]:
        """Update a litigation case"""
        case = await LitigationService.get_case(db, case_id, tenant_id)
        if not case:
            raise NotFoundException(f"Case with ID {case_id} not found")
        
        # Update fields
        update_data = case_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(case, field, value)
        
        case.updated_by = user_id
        case.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(case)
        
        return case

    @staticmethod
    async def delete_case(
        db: AsyncSession,
        case_id: UUID,
        tenant_id: str,
        user_id: UUID
    ) -> bool:
        """Soft delete a litigation case"""
        case = await LitigationService.get_case(db, case_id, tenant_id)
        if not case:
            raise NotFoundException(f"Case with ID {case_id} not found")
        
        case.is_deleted = True
        case.deleted_at = datetime.utcnow()
        case.deleted_by = user_id
        
        await db.commit()
        return True

    # ========================================================================
    # HEARING MANAGEMENT
    # ========================================================================

    @staticmethod
    async def create_hearing(
        db: AsyncSession,
        hearing_data: CaseHearingCreate,
        tenant_id: str,
        user_id: UUID
    ) -> CaseHearing:
        """Create a new case hearing"""
        
        # Verify case exists
        case = await LitigationService.get_case(db, hearing_data.case_id, tenant_id)
        if not case:
            raise NotFoundException(f"Case with ID {hearing_data.case_id} not found")
        
        # Get next hearing number
        result = await db.execute(
            select(func.max(CaseHearing.hearing_number)).where(
                CaseHearing.case_id == hearing_data.case_id
            )
        )
        max_hearing_number = result.scalar() or 0
        
        # Create hearing
        hearing = CaseHearing(
            **hearing_data.model_dump(exclude_unset=True),
            hearing_number=max_hearing_number + 1,
            hearing_status=HearingStatus.SCHEDULED,
            created_by=user_id
        )
        
        db.add(hearing)
        
        # Update case next hearing date
        case.next_hearing_date = hearing_data.scheduled_date
        
        await db.commit()
        await db.refresh(hearing)
        
        return hearing

    @staticmethod
    async def get_hearing(
        db: AsyncSession,
        hearing_id: UUID
    ) -> Optional[CaseHearing]:
        """Get a case hearing by ID"""
        result = await db.execute(
            select(CaseHearing).where(CaseHearing.id == hearing_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_case_hearings(
        db: AsyncSession,
        case_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[CaseHearing], int]:
        """Get all hearings for a case"""
        query = select(CaseHearing).where(CaseHearing.case_id == case_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        # Apply pagination and order
        query = query.order_by(CaseHearing.scheduled_date.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        hearings = result.scalars().all()
        
        return list(hearings), total or 0

    @staticmethod
    async def get_upcoming_hearings(
        db: AsyncSession,
        tenant_id: str,
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[CaseHearing], int]:
        """Get upcoming hearings across all cases"""
        end_date = datetime.utcnow() + timedelta(days=days)
        
        query = select(CaseHearing).join(LitigationCase).where(
            and_(
                LitigationCase.tenant_id == tenant_id,
                LitigationCase.is_deleted == False,
                CaseHearing.hearing_status == HearingStatus.SCHEDULED,
                CaseHearing.scheduled_date >= datetime.utcnow(),
                CaseHearing.scheduled_date <= end_date
            )
        )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        # Apply pagination and order
        query = query.order_by(CaseHearing.scheduled_date.asc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        hearings = result.scalars().all()
        
        return list(hearings), total or 0

    @staticmethod
    async def update_hearing(
        db: AsyncSession,
        hearing_id: UUID,
        hearing_data: CaseHearingUpdate,
        user_id: UUID
    ) -> Optional[CaseHearing]:
        """Update a case hearing"""
        hearing = await LitigationService.get_hearing(db, hearing_id)
        if not hearing:
            raise NotFoundException(f"Hearing with ID {hearing_id} not found")
        
        # Update fields
        update_data = hearing_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(hearing, field, value)
        
        hearing.updated_at = datetime.utcnow()
        
        # If next hearing date is set, update case
        if hearing_data.next_hearing_date:
            case = await LitigationService.get_case(db, hearing.case_id, "default")  # Simplified
            if case:
                case.next_hearing_date = hearing_data.next_hearing_date
        
        await db.commit()
        await db.refresh(hearing)
        
        return hearing

    # ========================================================================
    # EXPENSE MANAGEMENT
    # ========================================================================

    @staticmethod
    async def create_expense(
        db: AsyncSession,
        expense_data: LegalExpenseCreate,
        tenant_id: str,
        user_id: UUID
    ) -> LegalExpense:
        """Create a new legal expense"""
        
        # Verify case exists
        case = await LitigationService.get_case(db, expense_data.case_id, tenant_id)
        if not case:
            raise NotFoundException(f"Case with ID {expense_data.case_id} not found")
        
        # Generate expense number
        year = datetime.utcnow().year
        result = await db.execute(
            select(func.count()).where(
                and_(
                    LegalExpense.tenant_id == tenant_id,
                    extract('year', LegalExpense.created_at) == year
                )
            )
        )
        count = (result.scalar() or 0) + 1
        expense_number = f"EXP-{year}-{count:06d}"
        
        # Calculate total amount
        total_amount = expense_data.amount + (expense_data.tax_amount or Decimal(0))
        
        # Create expense
        expense = LegalExpense(
            **expense_data.model_dump(exclude_unset=True),
            tenant_id=tenant_id,
            expense_number=expense_number,
            total_amount=total_amount,
            created_by=user_id
        )
        
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        
        return expense

    @staticmethod
    async def get_expense(
        db: AsyncSession,
        expense_id: UUID,
        tenant_id: str
    ) -> Optional[LegalExpense]:
        """Get a legal expense by ID"""
        result = await db.execute(
            select(LegalExpense).where(
                and_(
                    LegalExpense.id == expense_id,
                    LegalExpense.tenant_id == tenant_id,
                    LegalExpense.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_case_expenses(
        db: AsyncSession,
        case_id: UUID,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None
    ) -> tuple[List[LegalExpense], int]:
        """Get all expenses for a case"""
        query = select(LegalExpense).where(
            and_(
                LegalExpense.case_id == case_id,
                LegalExpense.tenant_id == tenant_id,
                LegalExpense.is_deleted == False
            )
        )
        
        if category:
            query = query.where(LegalExpense.expense_category == category)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        
        # Apply pagination and order
        query = query.order_by(LegalExpense.expense_date.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        expenses = result.scalars().all()
        
        return list(expenses), total or 0

    @staticmethod
    async def update_expense(
        db: AsyncSession,
        expense_id: UUID,
        expense_data: LegalExpenseUpdate,
        tenant_id: str
    ) -> Optional[LegalExpense]:
        """Update a legal expense"""
        expense = await LitigationService.get_expense(db, expense_id, tenant_id)
        if not expense:
            raise NotFoundException(f"Expense with ID {expense_id} not found")
        
        # Update fields
        update_data = expense_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)
        
        # Recalculate total if amount or tax changed
        if 'amount' in update_data or 'tax_amount' in update_data:
            expense.total_amount = expense.amount + (expense.tax_amount or Decimal(0))
        
        expense.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(expense)
        
        return expense

    @staticmethod
    async def approve_expense(
        db: AsyncSession,
        expense_id: UUID,
        tenant_id: str,
        user_id: UUID,
        remarks: Optional[str] = None
    ) -> Optional[LegalExpense]:
        """Approve a legal expense"""
        expense = await LitigationService.get_expense(db, expense_id, tenant_id)
        if not expense:
            raise NotFoundException(f"Expense with ID {expense_id} not found")
        
        expense.is_approved = True
        expense.approved_by = user_id
        expense.approval_date = datetime.utcnow()
        expense.approval_remarks = remarks
        
        await db.commit()
        await db.refresh(expense)
        
        return expense

    @staticmethod
    async def mark_expense_paid(
        db: AsyncSession,
        expense_id: UUID,
        tenant_id: str,
        user_id: UUID,
        payment_date: date,
        payment_reference: Optional[str] = None
    ) -> Optional[LegalExpense]:
        """Mark an expense as paid"""
        expense = await LitigationService.get_expense(db, expense_id, tenant_id)
        if not expense:
            raise NotFoundException(f"Expense with ID {expense_id} not found")
        
        if not expense.is_approved:
            raise ValidationException("Expense must be approved before marking as paid")
        
        expense.is_paid = True
        expense.paid_by = user_id
        expense.payment_date = payment_date
        if payment_reference:
            expense.payment_reference = payment_reference
        
        await db.commit()
        await db.refresh(expense)
        
        return expense

    # ========================================================================
    # PARTY MANAGEMENT
    # ========================================================================

    @staticmethod
    async def create_party(
        db: AsyncSession,
        party_data: CasePartyCreate,
        tenant_id: str
    ) -> CaseParty:
        """Create a new case party"""
        
        # Verify case exists
        case = await LitigationService.get_case(db, party_data.case_id, tenant_id)
        if not case:
            raise NotFoundException(f"Case with ID {party_data.case_id} not found")
        
        party = CaseParty(**party_data.model_dump(exclude_unset=True))
        
        db.add(party)
        await db.commit()
        await db.refresh(party)
        
        return party

    @staticmethod
    async def get_case_parties(
        db: AsyncSession,
        case_id: UUID
    ) -> List[CaseParty]:
        """Get all parties for a case"""
        result = await db.execute(
            select(CaseParty).where(CaseParty.case_id == case_id)
        )
        return list(result.scalars().all())

    # ========================================================================
    # STATISTICS & ANALYTICS
    # ========================================================================

    @staticmethod
    async def get_case_statistics(
        db: AsyncSession,
        tenant_id: str
    ) -> CaseStatistics:
        """Get case statistics"""
        
        # Total cases
        total_cases = await db.scalar(
            select(func.count()).where(
                and_(
                    LitigationCase.tenant_id == tenant_id,
                    LitigationCase.is_deleted == False
                )
            )
        ) or 0
        
        # Active cases
        active_cases = await db.scalar(
            select(func.count()).where(
                and_(
                    LitigationCase.tenant_id == tenant_id,
                    LitigationCase.status.in_([CaseStatus.IN_PROGRESS, CaseStatus.ADMITTED, CaseStatus.FILED]),
                    LitigationCase.is_deleted == False
                )
            )
        ) or 0
        
        # Cases by outcome
        won_cases = await db.scalar(
            select(func.count()).where(
                and_(
                    LitigationCase.tenant_id == tenant_id,
                    LitigationCase.status == CaseStatus.WON,
                    LitigationCase.is_deleted == False
                )
            )
        ) or 0
        
        lost_cases = await db.scalar(
            select(func.count()).where(
                and_(
                    LitigationCase.tenant_id == tenant_id,
                    LitigationCase.status == CaseStatus.LOST,
                    LitigationCase.is_deleted == False
                )
            )
        ) or 0
        
        settled_cases = await db.scalar(
            select(func.count()).where(
                and_(
                    LitigationCase.tenant_id == tenant_id,
                    LitigationCase.status == CaseStatus.SETTLED,
                    LitigationCase.is_deleted == False
                )
            )
        ) or 0
        
        # Financial totals
        claim_amount = await db.scalar(
            select(func.sum(LitigationCase.claim_amount)).where(
                and_(
                    LitigationCase.tenant_id == tenant_id,
                    LitigationCase.is_deleted == False
                )
            )
        ) or Decimal(0)
        
        awarded_amount = await db.scalar(
            select(func.sum(LitigationCase.awarded_amount)).where(
                and_(
                    LitigationCase.tenant_id == tenant_id,
                    LitigationCase.is_deleted == False
                )
            )
        ) or Decimal(0)
        
        # Total expenses
        total_expenses = await db.scalar(
            select(func.sum(LegalExpense.total_amount)).where(
                and_(
                    LegalExpense.tenant_id == tenant_id,
                    LegalExpense.is_deleted == False
                )
            )
        ) or Decimal(0)
        
        # Upcoming hearings
        upcoming_hearings = await db.scalar(
            select(func.count()).select_from(CaseHearing).join(LitigationCase).where(
                and_(
                    LitigationCase.tenant_id == tenant_id,
                    LitigationCase.is_deleted == False,
                    CaseHearing.hearing_status == HearingStatus.SCHEDULED,
                    CaseHearing.scheduled_date >= datetime.utcnow()
                )
            )
        ) or 0
        
        return CaseStatistics(
            total_cases=total_cases,
            active_cases=active_cases,
            won_cases=won_cases,
            lost_cases=lost_cases,
            settled_cases=settled_cases,
            pending_cases=active_cases,
            total_claim_amount=claim_amount,
            total_awarded_amount=awarded_amount,
            total_legal_expenses=total_expenses,
            cases_by_type={},
            cases_by_status={},
            cases_by_priority={},
            upcoming_hearings=upcoming_hearings
        )
