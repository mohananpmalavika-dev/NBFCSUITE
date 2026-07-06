"""
Legal & Recovery Service
Manages legal notices, court cases, recovery actions, and agencies
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.collection_models import (
    LegalNotice,
    LegalCase,
    CaseHearing,
    RecoveryAgency,
    AgencyAssignment,
    RecoveryAction,
    CommunicationTemplate,
    LegalNoticeType,
    NoticeStage,
    DeliveryStatus,
    CaseType,
    CaseStatus,
    CaseOutcome,
    RecoveryActionType
)
from backend.shared.database.loan_models import LoanAccount
from backend.shared.database.customer_models import Customer


class LegalService:
    """Service for legal and recovery operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # LEGAL NOTICE MANAGEMENT
    # ========================================================================
    
    async def create_legal_notice(
        self,
        loan_account_id: int,
        customer_id: int,
        notice_type: LegalNoticeType,
        notice_stage: NoticeStage,
        notice_amount_demanded: Decimal,
        template_id: Optional[int] = None,
        dispatch_mode: str = "registered_post"
    ) -> LegalNotice:
        """Generate and create legal notice"""
        # Generate notice number
        notice_number = await self._generate_notice_number(notice_type)
        
        notice = LegalNotice(
            tenant_id=self.tenant_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            notice_type=notice_type,
            notice_stage=notice_stage,
            notice_number=notice_number,
            notice_date=date.today(),
            notice_amount_demanded=notice_amount_demanded,
            template_id=template_id,
            dispatch_mode=dispatch_mode,
            delivery_status=DeliveryStatus.PENDING,
            created_by=self.user_id
        )
        
        self.db.add(notice)
        await self.db.commit()
        await self.db.refresh(notice)
        
        # TODO: Generate PDF from template
        # notice.generated_pdf_url = await self._generate_notice_pdf(notice)
        
        return notice
    
    async def _generate_notice_number(self, notice_type: LegalNoticeType) -> str:
        """Generate unique notice number"""
        today = date.today()
        prefix = f"LN/{notice_type.value[:3].upper()}/{today.year}/{today.month:02d}"
        
        # Get count of notices this month
        count_query = select(func.count(LegalNotice.id)).where(
            and_(
                LegalNotice.tenant_id == self.tenant_id,
                LegalNotice.notice_number.like(f"{prefix}%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        return f"{prefix}/{count + 1:04d}"
    
    async def get_legal_notice(self, notice_id: int) -> Optional[LegalNotice]:
        """Get legal notice by ID"""
        query = select(LegalNotice).where(
            and_(
                LegalNotice.id == notice_id,
                LegalNotice.tenant_id == self.tenant_id,
                LegalNotice.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_notice_delivery(
        self,
        notice_id: int,
        delivery_status: DeliveryStatus,
        delivery_date: Optional[date] = None,
        delivered_to: Optional[str] = None,
        tracking_number: Optional[str] = None
    ) -> Optional[LegalNotice]:
        """Update notice delivery status"""
        notice = await self.get_legal_notice(notice_id)
        if not notice:
            return None
        
        notice.delivery_status = delivery_status
        if delivery_date:
            notice.delivery_date = delivery_date
        if delivered_to:
            notice.delivered_to = delivered_to
        if tracking_number:
            notice.tracking_number = tracking_number
        
        notice.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(notice)
        
        return notice
    
    async def record_notice_response(
        self,
        notice_id: int,
        response_details: str,
        response_date: Optional[date] = None,
        next_action: Optional[str] = None
    ) -> Optional[LegalNotice]:
        """Record customer response to notice"""
        notice = await self.get_legal_notice(notice_id)
        if not notice:
            return None
        
        notice.response_received = True
        notice.response_details = response_details
        notice.response_date = response_date or date.today()
        if next_action:
            notice.next_action = next_action
        
        notice.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(notice)
        
        return notice
    
    # ========================================================================
    # LEGAL CASE MANAGEMENT
    # ========================================================================
    
    async def file_legal_case(
        self,
        loan_account_id: int,
        customer_id: int,
        case_type: CaseType,
        claim_amount: Decimal,
        court_name: Optional[str] = None,
        lawyer_id: Optional[int] = None,
        lawyer_name: Optional[str] = None
    ) -> LegalCase:
        """File a new legal case"""
        case_number = await self._generate_case_number(case_type)
        
        case = LegalCase(
            tenant_id=self.tenant_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            case_number=case_number,
            case_type=case_type,
            court_name=court_name,
            filing_date=date.today(),
            claim_amount=claim_amount,
            lawyer_id=lawyer_id,
            lawyer_name=lawyer_name,
            case_status=CaseStatus.FILED,
            total_legal_cost=Decimal("0"),
            created_by=self.user_id
        )
        
        self.db.add(case)
        await self.db.commit()
        await self.db.refresh(case)
        
        return case
    
    async def _generate_case_number(self, case_type: CaseType) -> str:
        """Generate unique case number"""
        today = date.today()
        prefix = f"CASE/{case_type.value[:3].upper()}/{today.year}"
        
        count_query = select(func.count(LegalCase.id)).where(
            and_(
                LegalCase.tenant_id == self.tenant_id,
                LegalCase.case_number.like(f"{prefix}%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        return f"{prefix}/{count + 1:05d}"
    
    async def get_legal_case(self, case_id: int) -> Optional[LegalCase]:
        """Get legal case by ID"""
        query = select(LegalCase).where(
            and_(
                LegalCase.id == case_id,
                LegalCase.tenant_id == self.tenant_id,
                LegalCase.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_case_status(
        self,
        case_id: int,
        case_status: CaseStatus,
        next_hearing_date: Optional[date] = None,
        remarks: Optional[str] = None
    ) -> Optional[LegalCase]:
        """Update case status"""
        case = await self.get_legal_case(case_id)
        if not case:
            return None
        
        case.case_status = case_status
        if next_hearing_date:
            case.next_hearing_date = next_hearing_date
        if remarks:
            case.remarks = remarks
        
        case.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(case)
        
        return case
    
    async def record_judgement(
        self,
        case_id: int,
        judgement_details: str,
        judgement_amount: Optional[Decimal] = None,
        case_outcome: CaseOutcome = CaseOutcome.PENDING
    ) -> Optional[LegalCase]:
        """Record case judgement"""
        case = await self.get_legal_case(case_id)
        if not case:
            return None
        
        case.judgement_details = judgement_details
        case.judgement_date = date.today()
        if judgement_amount:
            case.judgement_amount = judgement_amount
        case.case_outcome = case_outcome
        case.case_status = CaseStatus.JUDGEMENT
        
        case.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(case)
        
        return case
    
    async def add_case_hearing(
        self,
        case_id: int,
        hearing_date: date,
        hearing_time: Optional[str] = None,
        judge_name: Optional[str] = None,
        hearing_notes: Optional[str] = None,
        next_hearing_date: Optional[date] = None
    ) -> CaseHearing:
        """Add hearing record"""
        hearing = CaseHearing(
            tenant_id=self.tenant_id,
            case_id=case_id,
            hearing_date=hearing_date,
            hearing_time=hearing_time,
            judge_name=judge_name,
            hearing_notes=hearing_notes,
            next_hearing_date=next_hearing_date
        )
        
        self.db.add(hearing)
        
        # Update case hearing count and next hearing
        case = await self.get_legal_case(case_id)
        if case:
            case.total_hearings += 1
            if next_hearing_date:
                case.next_hearing_date = next_hearing_date
        
        await self.db.commit()
        await self.db.refresh(hearing)
        
        return hearing
    
    # ========================================================================
    # RECOVERY AGENCY MANAGEMENT
    # ========================================================================
    
    async def create_recovery_agency(
        self,
        agency_code: str,
        agency_name: str,
        mobile: str,
        commission_percentage: Decimal,
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None
    ) -> RecoveryAgency:
        """Register recovery agency"""
        agency = RecoveryAgency(
            tenant_id=self.tenant_id,
            agency_code=agency_code,
            agency_name=agency_name,
            contact_person=contact_person,
            mobile=mobile,
            email=email,
            address=address,
            commission_percentage=commission_percentage,
            created_by=self.user_id
        )
        
        self.db.add(agency)
        await self.db.commit()
        await self.db.refresh(agency)
        
        return agency
    
    async def assign_to_agency(
        self,
        agency_id: int,
        loan_account_id: int,
        customer_id: int,
        outstanding_amount: Decimal,
        commission_agreed: Optional[Decimal] = None
    ) -> AgencyAssignment:
        """Assign loan to recovery agency"""
        # Get agency commission if not specified
        if not commission_agreed:
            agency_query = select(RecoveryAgency).where(RecoveryAgency.id == agency_id)
            agency_result = await self.db.execute(agency_query)
            agency = agency_result.scalar_one_or_none()
            commission_agreed = agency.commission_percentage if agency else Decimal("10")
        
        assignment = AgencyAssignment(
            tenant_id=self.tenant_id,
            agency_id=agency_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            assigned_date=date.today(),
            outstanding_amount=outstanding_amount,
            commission_agreed=commission_agreed,
            status="assigned"
        )
        
        self.db.add(assignment)
        
        # Update agency stats
        await self._update_agency_stats(agency_id, 1, Decimal("0"))
        
        await self.db.commit()
        await self.db.refresh(assignment)
        
        return assignment
    
    async def record_agency_recovery(
        self,
        assignment_id: int,
        recovery_amount: Decimal,
        commission_amount: Optional[Decimal] = None
    ) -> Optional[AgencyAssignment]:
        """Record recovery by agency"""
        query = select(AgencyAssignment).where(
            and_(
                AgencyAssignment.id == assignment_id,
                AgencyAssignment.tenant_id == self.tenant_id,
                AgencyAssignment.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        assignment = result.scalar_one_or_none()
        
        if not assignment:
            return None
        
        assignment.recovery_amount = recovery_amount
        assignment.recovery_date = date.today()
        assignment.status = "recovered"
        
        # Calculate commission if not provided
        if not commission_amount:
            commission_amount = recovery_amount * assignment.commission_agreed / 100
        
        assignment.commission_amount = commission_amount
        
        # Update agency stats
        await self._update_agency_stats(assignment.agency_id, 0, recovery_amount)
        
        assignment.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(assignment)
        
        return assignment
    
    async def _update_agency_stats(
        self,
        agency_id: int,
        cases_increment: int,
        recovery_amount: Decimal
    ):
        """Update agency statistics"""
        query = select(RecoveryAgency).where(RecoveryAgency.id == agency_id)
        result = await self.db.execute(query)
        agency = result.scalar_one_or_none()
        
        if agency:
            agency.total_cases_assigned += cases_increment
            agency.total_amount_recovered += recovery_amount
            agency.updated_at = datetime.now()
            await self.db.commit()
    
    # ========================================================================
    # RECOVERY ACTIONS
    # ========================================================================
    
    async def create_recovery_action(
        self,
        loan_account_id: int,
        customer_id: int,
        action_type: RecoveryActionType,
        assigned_to_internal: bool = True,
        assigned_user_id: Optional[int] = None,
        assigned_agency_id: Optional[int] = None,
        remarks: Optional[str] = None
    ) -> RecoveryAction:
        """Initiate recovery action"""
        action = RecoveryAction(
            tenant_id=self.tenant_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            action_type=action_type,
            action_date=date.today(),
            assigned_to_internal=assigned_to_internal,
            assigned_user_id=assigned_user_id,
            assigned_agency_id=assigned_agency_id,
            action_status="initiated",
            remarks=remarks,
            created_by=self.user_id
        )
        
        self.db.add(action)
        await self.db.commit()
        await self.db.refresh(action)
        
        return action
    
    async def update_recovery_action(
        self,
        action_id: int,
        action_status: str,
        recovery_amount: Optional[Decimal] = None,
        recovery_cost: Optional[Decimal] = None,
        remarks: Optional[str] = None
    ) -> Optional[RecoveryAction]:
        """Update recovery action status"""
        query = select(RecoveryAction).where(
            and_(
                RecoveryAction.id == action_id,
                RecoveryAction.tenant_id == self.tenant_id,
                RecoveryAction.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        action = result.scalar_one_or_none()
        
        if not action:
            return None
        
        action.action_status = action_status
        
        if recovery_amount is not None:
            action.recovery_amount = recovery_amount
        if recovery_cost is not None:
            action.recovery_cost = recovery_cost
            action.net_recovery = (action.recovery_amount or Decimal("0")) - recovery_cost
        if remarks:
            action.remarks = remarks
        
        action.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(action)
        
        return action
    
    # ========================================================================
    # ANALYTICS & REPORTING
    # ========================================================================
    
    async def get_legal_dashboard(self) -> Dict[str, Any]:
        """Get legal department dashboard metrics"""
        # Total notices sent
        notices_query = select(func.count(LegalNotice.id)).where(
            and_(
                LegalNotice.tenant_id == self.tenant_id,
                LegalNotice.is_deleted == False
            )
        )
        notices_result = await self.db.execute(notices_query)
        total_notices = notices_result.scalar()
        
        # Active cases
        cases_query = select(func.count(LegalCase.id)).where(
            and_(
                LegalCase.tenant_id == self.tenant_id,
                LegalCase.is_deleted == False,
                LegalCase.case_status.in_([CaseStatus.FILED, CaseStatus.PENDING, CaseStatus.HEARING])
            )
        )
        cases_result = await self.db.execute(cases_query)
        active_cases = cases_result.scalar()
        
        # Recovery through agencies
        recovery_query = select(
            func.sum(AgencyAssignment.recovery_amount)
        ).where(
            and_(
                AgencyAssignment.tenant_id == self.tenant_id,
                AgencyAssignment.is_deleted == False,
                AgencyAssignment.status == "recovered"
            )
        )
        recovery_result = await self.db.execute(recovery_query)
        total_recovery = recovery_result.scalar() or Decimal("0")
        
        return {
            "total_notices_sent": total_notices,
            "active_legal_cases": active_cases,
            "total_recovery_amount": float(total_recovery),
            "timestamp": datetime.now().isoformat()
        }
