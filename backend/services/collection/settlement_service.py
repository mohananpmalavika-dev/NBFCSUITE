"""
Settlement & OTS Service
Manages One Time Settlement proposals, approvals, and agreements
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.collection_models import (
    SettlementProposal,
    SettlementApproval,
    SettlementAgreement,
    SettlementPayment,
    WaiverPolicy,
    SettlementType,
    SettlementStatus,
    PaymentTerms
)
from backend.shared.database.loan_models import LoanAccount


class SettlementService:
    """Service for settlement and OTS management"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # WAIVER POLICY MANAGEMENT
    # ========================================================================
    
    async def create_waiver_policy(
        self,
        policy_code: str,
        policy_name: str,
        min_dpd: int,
        max_dpd: int,
        max_waiver_percentage_interest: Decimal,
        max_waiver_percentage_penal: Decimal,
        min_recovery_percentage: Decimal,
        loan_product_ids: Optional[List[int]] = None,
        description: Optional[str] = None,
        approval_required: bool = True,
        approval_authority: Optional[str] = None
    ) -> WaiverPolicy:
        """Create waiver policy"""
        policy = WaiverPolicy(
            tenant_id=self.tenant_id,
            policy_code=policy_code,
            policy_name=policy_name,
            description=description,
            min_dpd=min_dpd,
            max_dpd=max_dpd,
            loan_product_ids=loan_product_ids or [],
            max_waiver_percentage_interest=max_waiver_percentage_interest,
            max_waiver_percentage_penal=max_waiver_percentage_penal,
            min_recovery_percentage=min_recovery_percentage,
            approval_required=approval_required,
            approval_authority=approval_authority,
            created_by=self.user_id
        )
        
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        
        return policy
    
    async def get_applicable_waiver_policy(
        self,
        dpd: int,
        loan_product_id: Optional[int] = None
    ) -> Optional[WaiverPolicy]:
        """Get applicable waiver policy for given DPD"""
        conditions = [
            WaiverPolicy.tenant_id == self.tenant_id,
            WaiverPolicy.is_deleted == False,
            WaiverPolicy.is_active == True,
            WaiverPolicy.min_dpd <= dpd,
            WaiverPolicy.max_dpd >= dpd
        ]
        
        query = select(WaiverPolicy).where(and_(*conditions)).order_by(
            desc(WaiverPolicy.created_at)
        ).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    # ========================================================================
    # SETTLEMENT PROPOSAL MANAGEMENT
    # ========================================================================
    
    async def create_settlement_proposal(
        self,
        loan_account_id: int,
        customer_id: int,
        proposal_type: SettlementType,
        proposed_settlement_amount: Decimal,
        requested_by: str = "customer",
        waiver_policy_id: Optional[int] = None,
        payment_terms: PaymentTerms = PaymentTerms.LUMP_SUM,
        installment_count: Optional[int] = None,
        justification: Optional[str] = None,
        financial_hardship_details: Optional[str] = None
    ) -> Tuple[SettlementProposal, Dict[str, Any]]:
        """Create settlement proposal with calculations"""
        # Get loan account details
        loan_query = select(LoanAccount).where(LoanAccount.id == loan_account_id)
        loan_result = await self.db.execute(loan_query)
        loan = loan_result.scalar_one_or_none()
        
        if not loan:
            raise ValueError("Loan account not found")
        
        # Calculate outstanding amounts
        total_outstanding = loan.total_outstanding
        outstanding_principal = loan.outstanding_principal
        outstanding_interest = loan.outstanding_interest
        penal_charges = loan.penal_interest_outstanding
        
        # Calculate waivers
        waiver_on_interest = outstanding_interest
        waiver_on_penal = penal_charges
        total_waiver = waiver_on_interest + waiver_on_penal
        waiver_percentage = (total_waiver / total_outstanding * 100) if total_outstanding > 0 else Decimal("0")
        
        # Validate against waiver policy if provided
        if waiver_policy_id:
            policy = await self.get_applicable_waiver_policy(loan.dpd, loan.loan_product_id)
            if policy:
                # Validate waiver limits
                interest_waiver_pct = (waiver_on_interest / outstanding_interest * 100) if outstanding_interest > 0 else Decimal("0")
                penal_waiver_pct = (waiver_on_penal / penal_charges * 100) if penal_charges > 0 else Decimal("0")
                
                if interest_waiver_pct > policy.max_waiver_percentage_interest:
                    raise ValueError(f"Interest waiver exceeds policy limit of {policy.max_waiver_percentage_interest}%")
                if penal_waiver_pct > policy.max_waiver_percentage_penal:
                    raise ValueError(f"Penal waiver exceeds policy limit of {policy.max_waiver_percentage_penal}%")
        
        # Generate proposal number
        proposal_number = await self._generate_proposal_number(proposal_type)
        
        # Calculate installment amount if applicable
        installment_amount = None
        if payment_terms == PaymentTerms.INSTALLMENTS and installment_count:
            installment_amount = proposed_settlement_amount / installment_count
        
        # Create proposal
        proposal = SettlementProposal(
            tenant_id=self.tenant_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            waiver_policy_id=waiver_policy_id,
            proposal_number=proposal_number,
            proposal_type=proposal_type,
            requested_by=requested_by,
            request_date=date.today(),
            total_outstanding=total_outstanding,
            outstanding_principal=outstanding_principal,
            outstanding_interest=outstanding_interest,
            penal_charges=penal_charges,
            proposed_settlement_amount=proposed_settlement_amount,
            waiver_on_interest=waiver_on_interest,
            waiver_on_penal=waiver_on_penal,
            waiver_percentage=waiver_percentage,
            payment_terms=payment_terms,
            installment_count=installment_count,
            installment_amount=installment_amount,
            justification=justification,
            financial_hardship_details=financial_hardship_details,
            proposal_status=SettlementStatus.SUBMITTED,
            created_by=self.user_id
        )
        
        self.db.add(proposal)
        await self.db.commit()
        await self.db.refresh(proposal)
        
        # Calculation summary
        calculation = {
            "total_outstanding": float(total_outstanding),
            "outstanding_principal": float(outstanding_principal),
            "outstanding_interest": float(outstanding_interest),
            "penal_charges": float(penal_charges),
            "proposed_settlement_amount": float(proposed_settlement_amount),
            "total_waiver": float(total_waiver),
            "waiver_percentage": float(waiver_percentage),
            "recovery_percentage": float(proposed_settlement_amount / total_outstanding * 100) if total_outstanding > 0 else 0
        }
        
        return proposal, calculation
    
    async def _generate_proposal_number(self, proposal_type: SettlementType) -> str:
        """Generate unique proposal number"""
        today = date.today()
        prefix = f"STL/{proposal_type.value[:3].upper()}/{today.year}/{today.month:02d}"
        
        count_query = select(func.count(SettlementProposal.id)).where(
            and_(
                SettlementProposal.tenant_id == self.tenant_id,
                SettlementProposal.proposal_number.like(f"{prefix}%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        return f"{prefix}/{count + 1:04d}"
    
    async def get_settlement_proposal(self, proposal_id: int) -> Optional[SettlementProposal]:
        """Get settlement proposal by ID"""
        query = select(SettlementProposal).where(
            and_(
                SettlementProposal.id == proposal_id,
                SettlementProposal.tenant_id == self.tenant_id,
                SettlementProposal.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def calculate_settlement_npv(
        self,
        proposal_id: int,
        discount_rate: Decimal = Decimal("12")
    ) -> Dict[str, Any]:
        """Calculate NPV of settlement vs continuing recovery"""
        proposal = await self.get_settlement_proposal(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")
        
        # Simplified NPV calculation
        # Present value of settlement (immediate)
        pv_settlement = proposal.proposed_settlement_amount
        
        # Estimated recovery if continue (assume 60% recovery over 12 months)
        estimated_recovery = proposal.total_outstanding * Decimal("0.6")
        months = 12
        monthly_rate = discount_rate / 12 / 100
        
        # Present value of future recovery
        pv_recovery = estimated_recovery / ((1 + monthly_rate) ** months)
        
        # NPV of settlement
        npv = pv_settlement - pv_recovery
        
        return {
            "proposal_id": proposal_id,
            "settlement_amount": float(pv_settlement),
            "estimated_recovery_amount": float(estimated_recovery),
            "present_value_recovery": float(pv_recovery),
            "npv": float(npv),
            "recommendation": "Accept" if npv > 0 else "Reject"
        }
    
    # ========================================================================
    # APPROVAL WORKFLOW
    # ========================================================================
    
    async def submit_for_approval(
        self,
        proposal_id: int,
        approver_user_id: int,
        approval_level: int = 1
    ) -> SettlementApproval:
        """Submit proposal for approval"""
        proposal = await self.get_settlement_proposal(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")
        
        # Update proposal status
        proposal.proposal_status = SettlementStatus.UNDER_REVIEW
        proposal.current_approval_level = approval_level
        
        # Create approval entry
        approval = SettlementApproval(
            tenant_id=self.tenant_id,
            proposal_id=proposal_id,
            approval_level=approval_level,
            approver_user_id=approver_user_id,
            approval_status="pending"
        )
        
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        
        return approval
    
    async def approve_settlement(
        self,
        approval_id: int,
        approver_user_id: int,
        remarks: Optional[str] = None,
        forward_to_next_level: bool = False,
        next_approver_user_id: Optional[int] = None
    ) -> SettlementApproval:
        """Approve settlement proposal"""
        query = select(SettlementApproval).where(
            and_(
                SettlementApproval.id == approval_id,
                SettlementApproval.tenant_id == self.tenant_id,
                SettlementApproval.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        approval = result.scalar_one_or_none()
        
        if not approval:
            raise ValueError("Approval not found")
        
        if approval.approver_user_id != approver_user_id:
            raise ValueError("Unauthorized approver")
        
        approval.approval_status = "approved"
        approval.approval_date = datetime.now()
        approval.approval_remarks = remarks
        
        # Get proposal
        proposal = await self.get_settlement_proposal(approval.proposal_id)
        
        if forward_to_next_level and next_approver_user_id:
            # Forward to next approval level
            approval.forwarded_to_user_id = next_approver_user_id
            await self.submit_for_approval(
                approval.proposal_id,
                next_approver_user_id,
                approval.approval_level + 1
            )
        else:
            # Final approval - mark as approved
            proposal.proposal_status = SettlementStatus.APPROVED
        
        await self.db.commit()
        await self.db.refresh(approval)
        
        return approval
    
    async def reject_settlement(
        self,
        approval_id: int,
        approver_user_id: int,
        remarks: str
    ) -> SettlementApproval:
        """Reject settlement proposal"""
        query = select(SettlementApproval).where(
            and_(
                SettlementApproval.id == approval_id,
                SettlementApproval.tenant_id == self.tenant_id,
                SettlementApproval.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        approval = result.scalar_one_or_none()
        
        if not approval:
            raise ValueError("Approval not found")
        
        if approval.approver_user_id != approver_user_id:
            raise ValueError("Unauthorized approver")
        
        approval.approval_status = "rejected"
        approval.approval_date = datetime.now()
        approval.approval_remarks = remarks
        
        # Update proposal status
        proposal = await self.get_settlement_proposal(approval.proposal_id)
        proposal.proposal_status = SettlementStatus.REJECTED
        
        await self.db.commit()
        await self.db.refresh(approval)
        
        return approval
    
    # ========================================================================
    # AGREEMENT MANAGEMENT
    # ========================================================================
    
    async def create_settlement_agreement(
        self,
        proposal_id: int,
        payment_deadline: date,
        terms_and_conditions: str,
        breach_clause: Optional[str] = None,
        breach_penalty: Optional[Decimal] = None
    ) -> SettlementAgreement:
        """Create settlement agreement after approval"""
        proposal = await self.get_settlement_proposal(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")
        
        if proposal.proposal_status != SettlementStatus.APPROVED:
            raise ValueError("Proposal must be approved before creating agreement")
        
        # Generate agreement number
        agreement_number = await self._generate_agreement_number()
        
        # Build payment schedule for installments
        payment_schedule = None
        if proposal.payment_terms == PaymentTerms.INSTALLMENTS and proposal.installment_count:
            payment_schedule = self._build_payment_schedule(
                proposal.proposed_settlement_amount,
                proposal.installment_count,
                payment_deadline
            )
        
        # Create agreement
        agreement = SettlementAgreement(
            tenant_id=self.tenant_id,
            proposal_id=proposal_id,
            agreement_number=agreement_number,
            agreement_date=date.today(),
            settlement_amount=proposal.proposed_settlement_amount,
            payment_deadline=payment_deadline,
            payment_schedule=payment_schedule,
            terms_and_conditions=terms_and_conditions,
            breach_clause=breach_clause,
            breach_penalty=breach_penalty,
            bank_signed_date=date.today(),
            agreement_status="active",
            created_by=self.user_id
        )
        
        self.db.add(agreement)
        
        # Create payment records if installments
        if payment_schedule:
            for installment in payment_schedule:
                payment = SettlementPayment(
                    tenant_id=self.tenant_id,
                    agreement_id=agreement.id,
                    installment_number=installment["installment_number"],
                    due_date=installment["due_date"],
                    due_amount=Decimal(str(installment["amount"])),
                    payment_status="pending"
                )
                self.db.add(payment)
        
        # Update proposal status
        proposal.proposal_status = SettlementStatus.CUSTOMER_ACCEPTED
        
        await self.db.commit()
        await self.db.refresh(agreement)
        
        return agreement
    
    async def _generate_agreement_number(self) -> str:
        """Generate unique agreement number"""
        today = date.today()
        prefix = f"AGR/{today.year}/{today.month:02d}"
        
        count_query = select(func.count(SettlementAgreement.id)).where(
            and_(
                SettlementAgreement.tenant_id == self.tenant_id,
                SettlementAgreement.agreement_number.like(f"{prefix}%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        return f"{prefix}/{count + 1:05d}"
    
    def _build_payment_schedule(
        self,
        total_amount: Decimal,
        installment_count: int,
        first_payment_date: date
    ) -> List[Dict[str, Any]]:
        """Build payment schedule for installments"""
        installment_amount = total_amount / installment_count
        schedule = []
        
        for i in range(installment_count):
            due_date = first_payment_date + timedelta(days=30 * i)
            schedule.append({
                "installment_number": i + 1,
                "due_date": due_date.isoformat(),
                "amount": float(installment_amount)
            })
        
        return schedule
    
    async def record_settlement_payment(
        self,
        agreement_id: int,
        installment_number: int,
        paid_amount: Decimal,
        payment_date: Optional[date] = None,
        transaction_id: Optional[int] = None
    ) -> Optional[SettlementPayment]:
        """Record settlement payment"""
        query = select(SettlementPayment).where(
            and_(
                SettlementPayment.agreement_id == agreement_id,
                SettlementPayment.installment_number == installment_number,
                SettlementPayment.tenant_id == self.tenant_id,
                SettlementPayment.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        payment = result.scalar_one_or_none()
        
        if not payment:
            return None
        
        payment.paid_amount = paid_amount
        payment.payment_date = payment_date or date.today()
        payment.transaction_id = transaction_id
        
        # Determine payment status
        if paid_amount >= payment.due_amount:
            payment.payment_status = "paid"
        elif paid_amount > 0:
            payment.payment_status = "partially_paid"
        
        payment.updated_at = datetime.now()
        
        # Check if all payments completed
        await self._check_agreement_completion(agreement_id)
        
        await self.db.commit()
        await self.db.refresh(payment)
        
        return payment
    
    async def _check_agreement_completion(self, agreement_id: int):
        """Check if all payments completed and close agreement"""
        # Get all payments
        query = select(SettlementPayment).where(
            and_(
                SettlementPayment.agreement_id == agreement_id,
                SettlementPayment.tenant_id == self.tenant_id,
                SettlementPayment.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        payments = result.scalars().all()
        
        # Check if all paid
        all_paid = all(p.payment_status == "paid" for p in payments)
        
        if all_paid:
            # Get agreement and mark as completed
            agreement_query = select(SettlementAgreement).where(
                SettlementAgreement.id == agreement_id
            )
            agreement_result = await self.db.execute(agreement_query)
            agreement = agreement_result.scalar_one_or_none()
            
            if agreement:
                agreement.agreement_status = "completed"
                agreement.updated_at = datetime.now()
                
                # Update proposal status
                proposal = await self.get_settlement_proposal(agreement.proposal_id)
                if proposal:
                    proposal.proposal_status = SettlementStatus.COMPLETED
    
    async def mark_agreement_breached(
        self,
        agreement_id: int,
        breach_reason: str
    ) -> Optional[SettlementAgreement]:
        """Mark agreement as breached"""
        query = select(SettlementAgreement).where(
            and_(
                SettlementAgreement.id == agreement_id,
                SettlementAgreement.tenant_id == self.tenant_id,
                SettlementAgreement.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        agreement = result.scalar_one_or_none()
        
        if not agreement:
            return None
        
        agreement.agreement_status = "breached"
        agreement.updated_at = datetime.now()
        
        # Update proposal status
        proposal = await self.get_settlement_proposal(agreement.proposal_id)
        if proposal:
            proposal.proposal_status = SettlementStatus.BREACHED
        
        await self.db.commit()
        await self.db.refresh(agreement)
        
        return agreement
    
    # ========================================================================
    # ANALYTICS & REPORTING
    # ========================================================================
    
    async def get_settlement_statistics(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get settlement statistics"""
        if not from_date:
            from_date = date.today() - timedelta(days=90)
        if not to_date:
            to_date = date.today()
        
        # Query proposals by status
        query = select(
            SettlementProposal.proposal_status,
            func.count(SettlementProposal.id).label("count"),
            func.sum(SettlementProposal.total_outstanding).label("total_outstanding"),
            func.sum(SettlementProposal.proposed_settlement_amount).label("settlement_amount"),
            func.sum(SettlementProposal.waiver_on_interest + SettlementProposal.waiver_on_penal).label("total_waiver")
        ).where(
            and_(
                SettlementProposal.tenant_id == self.tenant_id,
                SettlementProposal.is_deleted == False,
                SettlementProposal.request_date >= from_date,
                SettlementProposal.request_date <= to_date
            )
        ).group_by(SettlementProposal.proposal_status)
        
        result = await self.db.execute(query)
        stats = result.all()
        
        status_breakdown = {}
        total_proposals = 0
        total_outstanding = Decimal("0")
        total_settlement = Decimal("0")
        total_waiver = Decimal("0")
        
        for row in stats:
            status_breakdown[row.proposal_status.value] = {
                "count": row.count,
                "total_outstanding": float(row.total_outstanding or 0),
                "settlement_amount": float(row.settlement_amount or 0),
                "waiver_amount": float(row.total_waiver or 0)
            }
            total_proposals += row.count
            total_outstanding += (row.total_outstanding or Decimal("0"))
            total_settlement += (row.settlement_amount or Decimal("0"))
            total_waiver += (row.total_waiver or Decimal("0"))
        
        # Calculate approval rate
        approved_count = status_breakdown.get(SettlementStatus.APPROVED.value, {}).get("count", 0)
        completed_count = status_breakdown.get(SettlementStatus.COMPLETED.value, {}).get("count", 0)
        rejected_count = status_breakdown.get(SettlementStatus.REJECTED.value, {}).get("count", 0)
        
        approval_rate = (
            (approved_count + completed_count) / total_proposals * 100
            if total_proposals > 0 else 0
        )
        
        return {
            "period": {
                "from_date": from_date.isoformat(),
                "to_date": to_date.isoformat()
            },
            "summary": {
                "total_proposals": total_proposals,
                "total_outstanding_amount": float(total_outstanding),
                "total_settlement_amount": float(total_settlement),
                "total_waiver_amount": float(total_waiver),
                "approval_rate": round(approval_rate, 2),
                "average_recovery_rate": round(
                    float(total_settlement / total_outstanding * 100) if total_outstanding > 0 else 0,
                    2
                )
            },
            "status_breakdown": status_breakdown
        }
    
    async def get_pending_approvals(
        self,
        approver_user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get pending settlement approvals"""
        conditions = [
            SettlementApproval.tenant_id == self.tenant_id,
            SettlementApproval.is_deleted == False,
            SettlementApproval.approval_status == "pending"
        ]
        
        if approver_user_id:
            conditions.append(SettlementApproval.approver_user_id == approver_user_id)
        
        query = select(SettlementApproval).where(and_(*conditions)).order_by(
            SettlementApproval.created_at
        )
        
        result = await self.db.execute(query)
        approvals = result.scalars().all()
        
        # Enrich with proposal details
        pending_list = []
        for approval in approvals:
            proposal = await self.get_settlement_proposal(approval.proposal_id)
            if proposal:
                pending_list.append({
                    "approval_id": approval.id,
                    "proposal_id": proposal.id,
                    "proposal_number": proposal.proposal_number,
                    "loan_account_id": proposal.loan_account_id,
                    "customer_id": proposal.customer_id,
                    "total_outstanding": float(proposal.total_outstanding),
                    "settlement_amount": float(proposal.proposed_settlement_amount),
                    "waiver_percentage": float(proposal.waiver_percentage),
                    "approval_level": approval.approval_level,
                    "request_date": proposal.request_date.isoformat()
                })
        
        return pending_list
