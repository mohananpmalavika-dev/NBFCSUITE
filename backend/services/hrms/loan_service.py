"""
HRMS Loan & Advances Service Layer
Business logic for loan management, eligibility checks, EMI calculation, and approval workflow
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import calendar
from dateutil.relativedelta import relativedelta

from backend.shared.database.hrms_loan_models import (
    EmployeeLoan, LoanPolicy, LoanEMISchedule, LoanTransaction,
    LoanType, LoanStatus, RepaymentFrequency, EMIStatus, TransactionType
)
from backend.shared.database.hrms_models import Employee
from backend.shared.database.payroll_models import EmployeeSalary
from .loan_schemas import (
    LoanApplicationCreate, LoanApplicationUpdate, LoanApprovalAction,
    LoanDisbursementRequest, LoanEligibilityRequest, LoanEligibilityResponse,
    EMICalculationRequest, EMICalculationResponse, EMIScheduleItem,
    LoanTransactionCreate, LoanClosureRequest, EmployeeLoanSummary
)


class LoanService:
    """Service for loan management operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str, employee_id: Optional[str] = None):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.employee_id = employee_id
    
    # ========================================================================
    # ELIGIBILITY CHECKING
    # ========================================================================
    
    async def check_eligibility(self, request: LoanEligibilityRequest) -> LoanEligibilityResponse:
        """Check if employee is eligible for loan"""
        
        if not self.employee_id:
            return LoanEligibilityResponse(
                is_eligible=False,
                eligible_amount=Decimal("0.00"),
                max_loan_amount=Decimal("0.00"),
                max_emi_amount=Decimal("0.00"),
                suggested_tenure_months=12,
                interest_rate=Decimal("0.00"),
                reasons=["Employee ID not provided"]
            )
        
        # Get employee details
        emp_query = select(Employee).where(
            and_(
                Employee.id == self.employee_id,
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        )
        result = await self.db.execute(emp_query)
        employee = result.scalar_one_or_none()
        
        if not employee:
            return LoanEligibilityResponse(
                is_eligible=False,
                eligible_amount=Decimal("0.00"),
                max_loan_amount=Decimal("0.00"),
                max_emi_amount=Decimal("0.00"),
                suggested_tenure_months=12,
                interest_rate=Decimal("0.00"),
                reasons=["Employee not found"]
            )
        
        # Get applicable loan policy
        policy_query = select(LoanPolicy).where(
            and_(
                LoanPolicy.tenant_id == self.tenant_id,
                LoanPolicy.loan_type == request.loan_type,
                LoanPolicy.is_active == True,
                LoanPolicy.is_deleted == False
            )
        )
        result = await self.db.execute(policy_query)
        policy = result.scalar_one_or_none()
        
        if not policy:
            return LoanEligibilityResponse(
                is_eligible=False,
                eligible_amount=Decimal("0.00"),
                max_loan_amount=Decimal("0.00"),
                max_emi_amount=Decimal("0.00"),
                suggested_tenure_months=12,
                interest_rate=Decimal("0.00"),
                reasons=["No active loan policy found for this loan type"]
            )
        
        reasons = []
        
        # Check service duration
        if employee.date_of_joining:
            service_months = (date.today() - employee.date_of_joining).days // 30
            if service_months < policy.min_service_months:
                reasons.append(f"Minimum {policy.min_service_months} months of service required. You have {service_months} months.")
        
        # Check employment status
        if employee.employment_status.value not in ["active"]:
            reasons.append(f"Loan not available for employment status: {employee.employment_status.value}")
        
        # Check active loans count
        active_loans_query = select(func.count(EmployeeLoan.id)).where(
            and_(
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.employee_id == self.employee_id,
                EmployeeLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.DISBURSED]),
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(active_loans_query)
        active_loans_count = result.scalar() or 0
        
        if active_loans_count >= policy.max_active_loans_per_employee:
            reasons.append(f"Maximum {policy.max_active_loans_per_employee} active loan(s) allowed. You have {active_loans_count}.")
        
        # Get employee current salary
        salary_query = select(EmployeeSalary).where(
            and_(
                EmployeeSalary.tenant_id == self.tenant_id,
                EmployeeSalary.employee_id == self.employee_id,
                EmployeeSalary.is_active == True,
                EmployeeSalary.is_deleted == False
            )
        )
        result = await self.db.execute(salary_query)
        emp_salary = result.scalar_one_or_none()
        
        if not emp_salary:
            reasons.append("No active salary record found")
            return LoanEligibilityResponse(
                is_eligible=False,
                eligible_amount=Decimal("0.00"),
                max_loan_amount=Decimal("0.00"),
                max_emi_amount=Decimal("0.00"),
                suggested_tenure_months=12,
                interest_rate=policy.interest_rate,
                reasons=reasons,
                policy_id=str(policy.id)
            )
        
        gross_monthly = emp_salary.gross_monthly
        
        # Calculate maximum loan amount based on policy
        max_loan_policy = policy.max_loan_amount
        max_loan_salary_multiple = Decimal("0.00")
        
        if policy.max_loan_as_salary_multiple:
            max_loan_salary_multiple = gross_monthly * policy.max_loan_as_salary_multiple
        
        max_loan_amount = min(max_loan_policy, max_loan_salary_multiple) if max_loan_salary_multiple > 0 else max_loan_policy
        
        # Calculate maximum EMI (based on salary percentage)
        max_emi_percentage = policy.max_emi_as_salary_percentage / Decimal("100")
        max_emi_amount = gross_monthly * max_emi_percentage
        
        # Calculate maximum loan based on EMI capacity
        if policy.interest_rate > 0:
            monthly_rate = policy.interest_rate / Decimal("1200")  # Annual to monthly
            n = request.tenure_months
            # Loan = EMI * [(1 - (1 + r)^-n) / r]
            discount_factor = (Decimal("1") - (Decimal("1") + monthly_rate) ** (-n)) / monthly_rate
            max_loan_emi_based = max_emi_amount * discount_factor
        else:
            max_loan_emi_based = max_emi_amount * request.tenure_months
        
        # Final eligible amount
        eligible_amount = min(max_loan_amount, max_loan_emi_based)
        
        # Check if requested amount is within limits
        if request.requested_amount > eligible_amount:
            reasons.append(f"Requested amount ₹{request.requested_amount:,.2f} exceeds eligible amount ₹{eligible_amount:,.2f}")
        
        if request.requested_amount < policy.min_loan_amount:
            reasons.append(f"Minimum loan amount is ₹{policy.min_loan_amount:,.2f}")
        
        is_eligible = len(reasons) == 0
        
        return LoanEligibilityResponse(
            is_eligible=is_eligible,
            eligible_amount=eligible_amount,
            max_loan_amount=max_loan_amount,
            max_emi_amount=max_emi_amount,
            suggested_tenure_months=policy.max_tenure_months,
            interest_rate=policy.interest_rate,
            reasons=reasons,
            policy_id=str(policy.id)
        )
    
    # ========================================================================
    # EMI CALCULATION
    # ========================================================================
    
    @staticmethod
    def calculate_emi(
        principal: Decimal,
        annual_rate: Decimal,
        tenure_months: int
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculate EMI using reducing balance method
        Returns: (emi_amount, total_interest, total_amount)
        """
        if annual_rate == 0:
            emi = principal / tenure_months
            total_interest = Decimal("0.00")
            total_amount = principal
        else:
            monthly_rate = annual_rate / Decimal("1200")
            
            # EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
            one_plus_r = Decimal("1") + monthly_rate
            power_n = one_plus_r ** tenure_months
            
            emi = principal * monthly_rate * power_n / (power_n - Decimal("1"))
            emi = emi.quantize(Decimal('0.01'))
            
            total_amount = emi * tenure_months
            total_interest = total_amount - principal
        
        return emi, total_interest, total_amount
    
    async def calculate_emi_schedule(
        self,
        principal: Decimal,
        interest_rate: Decimal,
        tenure_months: int,
        start_date: date
    ) -> List[dict]:
        """Generate detailed EMI schedule"""
        
        emi, _, _ = self.calculate_emi(principal, interest_rate, tenure_months)
        
        schedule = []
        outstanding = principal
        monthly_rate = interest_rate / Decimal("1200") if interest_rate > 0 else Decimal("0")
        
        current_date = start_date
        
        for emi_num in range(1, tenure_months + 1):
            # Calculate interest and principal components
            interest_component = (outstanding * monthly_rate).quantize(Decimal('0.01'))
            principal_component = emi - interest_component
            
            # Adjust last EMI for rounding differences
            if emi_num == tenure_months:
                principal_component = outstanding
                emi = principal_component + interest_component
            
            closing_balance = outstanding - principal_component
            
            schedule.append({
                "emi_number": emi_num,
                "emi_due_date": current_date,
                "emi_amount": emi,
                "principal_component": principal_component,
                "interest_component": interest_component,
                "opening_balance": outstanding,
                "closing_balance": closing_balance
            })
            
            outstanding = closing_balance
            current_date = current_date + relativedelta(months=1)
        
        return schedule
    
    # ========================================================================
    # LOAN APPLICATION
    # ========================================================================
    
    async def _generate_loan_code(self) -> str:
        """Generate unique loan code"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(EmployeeLoan.id)).where(
            and_(
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.loan_code.like(f"LOAN-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"LOAN-{year_month}-{sequence}"
    
    async def create_loan_application(self, data: LoanApplicationCreate) -> EmployeeLoan:
        """Create new loan application"""
        
        if not self.employee_id:
            raise ValueError("Employee ID is required")
        
        # Check eligibility
        eligibility_request = LoanEligibilityRequest(
            loan_type=data.loan_type,
            requested_amount=data.loan_amount,
            tenure_months=data.tenure_months
        )
        eligibility = await self.check_eligibility(eligibility_request)
        
        if not eligibility.is_eligible:
            raise ValueError(f"Not eligible for loan: {', '.join(eligibility.reasons)}")
        
        # Get loan policy
        policy_query = select(LoanPolicy).where(
            and_(
                LoanPolicy.tenant_id == self.tenant_id,
                LoanPolicy.loan_type == data.loan_type,
                LoanPolicy.is_active == True,
                LoanPolicy.is_deleted == False
            )
        )
        result = await self.db.execute(policy_query)
        policy = result.scalar_one_or_none()
        
        if not policy:
            raise ValueError("No active loan policy found")
        
        # Get employee with manager details
        emp_query = select(Employee).where(
            and_(
                Employee.id == self.employee_id,
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        )
        result = await self.db.execute(emp_query)
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise ValueError("Employee not found")
        
        # Calculate EMI
        emi_amount, total_interest, total_repayment = self.calculate_emi(
            data.loan_amount,
            policy.interest_rate,
            data.tenure_months
        )
        
        # Calculate processing fee
        processing_fee = (data.loan_amount * policy.processing_fee_percentage / Decimal("100")).quantize(Decimal('0.01'))
        
        # Generate loan code
        loan_code = await self._generate_loan_code()
        
        # Create loan application
        loan = EmployeeLoan(
            tenant_id=self.tenant_id,
            loan_code=loan_code,
            employee_id=self.employee_id,
            policy_id=policy.id,
            loan_type=data.loan_type,
            loan_amount=data.loan_amount,
            interest_rate=policy.interest_rate,
            tenure_months=data.tenure_months,
            repayment_frequency=data.repayment_frequency,
            emi_amount=emi_amount,
            total_interest=total_interest,
            total_repayment_amount=total_repayment,
            processing_fee=processing_fee,
            application_date=date.today(),
            purpose=data.purpose,
            reason_for_loan=data.reason_for_loan,
            attachment_urls=",".join(data.attachment_urls) if data.attachment_urls else None,
            status=LoanStatus.DRAFT,
            bank_name=data.bank_name,
            bank_account_number=data.bank_account_number,
            bank_ifsc_code=data.bank_ifsc_code,
            guarantor_employee_id=data.guarantor_employee_id,
            guarantor_name=data.guarantor_name,
            guarantor_relation=data.guarantor_relation,
            guarantor_contact=data.guarantor_contact,
            manager_approver_id=employee.reporting_manager_id,
            principal_outstanding=Decimal("0.00"),
            interest_outstanding=Decimal("0.00"),
            total_outstanding=Decimal("0.00"),
            prepayment_allowed_after_months=policy.min_tenure_months // 2,
            prepayment_penalty_percentage=policy.prepayment_penalty_percentage,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(loan)
        await self.db.commit()
        await self.db.refresh(loan)
        
        return loan
    
    async def submit_loan_application(self, loan_id: str) -> EmployeeLoan:
        """Submit loan application for approval"""
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.id == loan_id,
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.employee_id == self.employee_id,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        loan = result.scalar_one_or_none()
        
        if not loan:
            raise ValueError("Loan application not found")
        
        if loan.status != LoanStatus.DRAFT:
            raise ValueError("Only draft applications can be submitted")
        
        loan.status = LoanStatus.PENDING_APPROVAL
        loan.submitted_date = datetime.utcnow()
        loan.manager_approval_status = "pending"
        loan.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(loan)
        
        return loan
    
    async def update_loan_application(self, loan_id: str, data: LoanApplicationUpdate) -> EmployeeLoan:
        """Update draft loan application"""
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.id == loan_id,
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.employee_id == self.employee_id,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        loan = result.scalar_one_or_none()
        
        if not loan:
            raise ValueError("Loan application not found")
        
        if loan.status != LoanStatus.DRAFT:
            raise ValueError("Only draft applications can be updated")
        
        # Update fields
        if data.loan_amount is not None:
            loan.loan_amount = data.loan_amount
            # Recalculate EMI
            emi, total_interest, total_repayment = self.calculate_emi(
                data.loan_amount,
                loan.interest_rate,
                loan.tenure_months
            )
            loan.emi_amount = emi
            loan.total_interest = total_interest
            loan.total_repayment_amount = total_repayment
        
        if data.tenure_months is not None:
            loan.tenure_months = data.tenure_months
            # Recalculate EMI
            emi, total_interest, total_repayment = self.calculate_emi(
                loan.loan_amount,
                loan.interest_rate,
                data.tenure_months
            )
            loan.emi_amount = emi
            loan.total_interest = total_interest
            loan.total_repayment_amount = total_repayment
        
        if data.purpose is not None:
            loan.purpose = data.purpose
        if data.reason_for_loan is not None:
            loan.reason_for_loan = data.reason_for_loan
        if data.bank_name is not None:
            loan.bank_name = data.bank_name
        if data.bank_account_number is not None:
            loan.bank_account_number = data.bank_account_number
        if data.bank_ifsc_code is not None:
            loan.bank_ifsc_code = data.bank_ifsc_code
        
        loan.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(loan)
        
        return loan
    
    async def cancel_loan_application(self, loan_id: str) -> EmployeeLoan:
        """Cancel loan application"""
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.id == loan_id,
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.employee_id == self.employee_id,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        loan = result.scalar_one_or_none()
        
        if not loan:
            raise ValueError("Loan application not found")
        
        if loan.status not in [LoanStatus.DRAFT, LoanStatus.PENDING_APPROVAL]:
            raise ValueError("Only draft or pending applications can be cancelled")
        
        loan.status = LoanStatus.CANCELLED
        loan.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(loan)
        
        return loan
    
    # ========================================================================
    # APPROVAL WORKFLOW
    # ========================================================================
    
    async def approve_by_manager(self, loan_id: str, action: LoanApprovalAction) -> EmployeeLoan:
        """Manager approval"""
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.id == loan_id,
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.manager_approver_id == self.employee_id,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        loan = result.scalar_one_or_none()
        
        if not loan:
            raise ValueError("Loan not found or you are not the approver")
        
        if loan.manager_approval_status != "pending":
            raise ValueError("Loan is not pending manager approval")
        
        if action.action == "approve":
            loan.manager_approval_status = "approved"
            loan.manager_approval_date = datetime.utcnow()
            loan.manager_comments = action.comments
            loan.hr_approval_status = "pending"
        else:
            loan.manager_approval_status = "rejected"
            loan.manager_approval_date = datetime.utcnow()
            loan.manager_comments = action.comments
            loan.status = LoanStatus.REJECTED
            loan.rejected_date = datetime.utcnow()
            loan.rejected_by = self.employee_id
            loan.rejection_reason = action.comments
        
        loan.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(loan)
        
        return loan
    
    async def approve_by_hr(self, loan_id: str, action: LoanApprovalAction) -> EmployeeLoan:
        """HR approval"""
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.id == loan_id,
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        loan = result.scalar_one_or_none()
        
        if not loan:
            raise ValueError("Loan not found")
        
        if loan.hr_approval_status != "pending":
            raise ValueError("Loan is not pending HR approval")
        
        if action.action == "approve":
            loan.hr_approver_id = self.employee_id
            loan.hr_approval_status = "approved"
            loan.hr_approval_date = datetime.utcnow()
            loan.hr_comments = action.comments
            loan.finance_approval_status = "pending"
        else:
            loan.hr_approver_id = self.employee_id
            loan.hr_approval_status = "rejected"
            loan.hr_approval_date = datetime.utcnow()
            loan.hr_comments = action.comments
            loan.status = LoanStatus.REJECTED
            loan.rejected_date = datetime.utcnow()
            loan.rejected_by = self.employee_id
            loan.rejection_reason = action.comments
        
        loan.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(loan)
        
        return loan
    
    async def approve_by_finance(self, loan_id: str, action: LoanApprovalAction) -> EmployeeLoan:
        """Finance approval (final approval)"""
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.id == loan_id,
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        loan = result.scalar_one_or_none()
        
        if not loan:
            raise ValueError("Loan not found")
        
        if loan.finance_approval_status != "pending":
            raise ValueError("Loan is not pending finance approval")
        
        if action.action == "approve":
            loan.finance_approver_id = self.employee_id
            loan.finance_approval_status = "approved"
            loan.finance_approval_date = datetime.utcnow()
            loan.finance_comments = action.comments
            loan.status = LoanStatus.APPROVED
            loan.approved_date = datetime.utcnow()
            loan.approved_by = self.employee_id
            
            # Adjust amount if approved amount is different
            if action.approved_amount and action.approved_amount != loan.loan_amount:
                loan.loan_amount = action.approved_amount
                # Recalculate EMI
                emi, total_interest, total_repayment = self.calculate_emi(
                    action.approved_amount,
                    loan.interest_rate,
                    loan.tenure_months
                )
                loan.emi_amount = emi
                loan.total_interest = total_interest
                loan.total_repayment_amount = total_repayment
        else:
            loan.finance_approver_id = self.employee_id
            loan.finance_approval_status = "rejected"
            loan.finance_approval_date = datetime.utcnow()
            loan.finance_comments = action.comments
            loan.status = LoanStatus.REJECTED
            loan.rejected_date = datetime.utcnow()
            loan.rejected_by = self.employee_id
            loan.rejection_reason = action.comments
        
        loan.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(loan)
        
        return loan
    
    # ========================================================================
    # LOAN DISBURSEMENT
    # ========================================================================
    
    async def disburse_loan(self, loan_id: str, data: LoanDisbursementRequest) -> EmployeeLoan:
        """Disburse approved loan and generate EMI schedule"""
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.id == loan_id,
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        loan = result.scalar_one_or_none()
        
        if not loan:
            raise ValueError("Loan not found")
        
        if loan.status != LoanStatus.APPROVED:
            raise ValueError("Only approved loans can be disbursed")
        
        # Update disbursement details
        disbursed_amount = data.disbursed_amount or loan.loan_amount
        
        loan.disbursement_date = data.disbursement_date
        loan.disbursement_mode = data.disbursement_mode
        loan.disbursement_reference = data.disbursement_reference
        loan.disbursed_amount = disbursed_amount
        loan.repayment_start_date = data.repayment_start_date
        loan.status = LoanStatus.DISBURSED
        
        # Set outstanding amounts
        loan.principal_outstanding = disbursed_amount
        loan.total_outstanding = loan.total_repayment_amount
        
        # Generate EMI schedule
        schedule = await self.calculate_emi_schedule(
            disbursed_amount,
            loan.interest_rate,
            loan.tenure_months,
            data.repayment_start_date
        )
        
        loan.first_emi_date = schedule[0]["emi_due_date"]
        loan.last_emi_date = schedule[-1]["emi_due_date"]
        
        # Create EMI schedule records
        for sch in schedule:
            emi_record = LoanEMISchedule(
                tenant_id=self.tenant_id,
                loan_id=loan.id,
                emi_number=sch["emi_number"],
                emi_due_date=sch["emi_due_date"],
                emi_amount=sch["emi_amount"],
                principal_component=sch["principal_component"],
                interest_component=sch["interest_component"],
                opening_principal_balance=sch["opening_balance"],
                closing_principal_balance=sch["closing_balance"],
                status=EMIStatus.PENDING,
                created_by=self.user_id,
                updated_by=self.user_id
            )
            self.db.add(emi_record)
        
        # Create disbursement transaction
        txn_code = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        transaction = LoanTransaction(
            tenant_id=self.tenant_id,
            transaction_code=txn_code,
            loan_id=loan.id,
            transaction_type=TransactionType.DISBURSEMENT,
            transaction_date=data.disbursement_date,
            transaction_amount=disbursed_amount,
            principal_amount=disbursed_amount,
            interest_amount=Decimal("0.00"),
            principal_outstanding=disbursed_amount,
            interest_outstanding=loan.total_interest,
            total_outstanding=loan.total_repayment_amount,
            payment_mode=data.disbursement_mode,
            payment_reference=data.disbursement_reference,
            remarks="Loan disbursement",
            processed_by=self.employee_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        self.db.add(transaction)
        
        # Update loan status to active
        loan.status = LoanStatus.ACTIVE
        loan.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(loan)
        
        return loan
    
    # ========================================================================
    # EMI PAYMENT & TRACKING
    # ========================================================================
    
    async def record_emi_payment(
        self,
        emi_schedule_id: str,
        payment_date: date,
        amount_paid: Decimal,
        payment_mode: str = "salary_deduction",
        payment_reference: Optional[str] = None,
        payroll_run_id: Optional[str] = None
    ) -> LoanEMISchedule:
        """Record EMI payment"""
        
        query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.id == emi_schedule_id,
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.is_deleted == False
            )
        ).options(selectinload(LoanEMISchedule.loan))
        
        result = await self.db.execute(query)
        emi = result.scalar_one_or_none()
        
        if not emi:
            raise ValueError("EMI record not found")
        
        if emi.status == EMIStatus.PAID:
            raise ValueError("EMI already paid")
        
        loan = emi.loan
        
        # Update EMI record
        emi.payment_date = payment_date
        emi.amount_paid = amount_paid
        emi.principal_paid = emi.principal_component
        emi.interest_paid = emi.interest_component
        emi.status = EMIStatus.PAID
        emi.payment_reference = payment_reference
        emi.payroll_run_id = payroll_run_id
        emi.updated_by = self.user_id
        
        # Update loan outstanding
        loan.principal_outstanding -= emi.principal_component
        loan.interest_outstanding -= emi.interest_component
        loan.total_outstanding = loan.principal_outstanding + loan.interest_outstanding
        
        loan.principal_paid += emi.principal_component
        loan.interest_paid += emi.interest_component
        loan.total_paid += amount_paid
        
        # Create transaction record
        txn_code = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        transaction = LoanTransaction(
            tenant_id=self.tenant_id,
            transaction_code=txn_code,
            loan_id=loan.id,
            emi_schedule_id=emi.id,
            transaction_type=TransactionType.EMI_PAYMENT,
            transaction_date=payment_date,
            transaction_amount=amount_paid,
            principal_amount=emi.principal_component,
            interest_amount=emi.interest_component,
            principal_outstanding=loan.principal_outstanding,
            interest_outstanding=loan.interest_outstanding,
            total_outstanding=loan.total_outstanding,
            payment_mode=payment_mode,
            payment_reference=payment_reference,
            payroll_run_id=payroll_run_id,
            remarks=f"EMI #{emi.emi_number} payment",
            processed_by=self.employee_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        self.db.add(transaction)
        
        # Check if loan is fully repaid
        if loan.total_outstanding <= Decimal("0.01"):
            loan.status = LoanStatus.CLOSED
            loan.closure_date = payment_date
            loan.closure_reason = "fully_paid"
        
        loan.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(emi)
        
        return emi
    
    async def get_pending_emis_for_month(self, year: int, month: int) -> List[LoanEMISchedule]:
        """Get all pending EMIs for a specific month (for payroll integration)"""
        
        # Get first and last day of month
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        
        query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.emi_due_date >= first_day,
                LoanEMISchedule.emi_due_date <= last_day,
                LoanEMISchedule.status == EMIStatus.PENDING,
                LoanEMISchedule.is_deleted == False
            )
        ).options(selectinload(LoanEMISchedule.loan))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # ========================================================================
    # LOAN CLOSURE & SETTLEMENT
    # ========================================================================
    
    async def foreclose_loan(self, loan_id: str, data: LoanClosureRequest) -> EmployeeLoan:
        """Foreclose loan (early settlement)"""
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.id == loan_id,
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        loan = result.scalar_one_or_none()
        
        if not loan:
            raise ValueError("Loan not found")
        
        if loan.status != LoanStatus.ACTIVE:
            raise ValueError("Only active loans can be foreclosed")
        
        settlement_amount = data.settlement_amount or loan.total_outstanding
        
        # Calculate prepayment penalty if applicable
        penalty = Decimal("0.00")
        if loan.prepayment_penalty_percentage > 0:
            penalty = (loan.principal_outstanding * loan.prepayment_penalty_percentage / Decimal("100")).quantize(Decimal('0.01'))
            settlement_amount += penalty
        
        # Update loan
        loan.status = LoanStatus.CLOSED
        loan.closure_date = data.closure_date
        loan.closure_reason = data.closure_reason
        loan.closure_remarks = data.closure_remarks
        loan.updated_by = self.user_id
        
        # Create foreclosure transaction
        txn_code = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        transaction = LoanTransaction(
            tenant_id=self.tenant_id,
            transaction_code=txn_code,
            loan_id=loan.id,
            transaction_type=TransactionType.FORECLOSURE,
            transaction_date=data.closure_date,
            transaction_amount=settlement_amount,
            principal_amount=loan.principal_outstanding,
            interest_amount=Decimal("0.00"),
            penalty_amount=penalty,
            principal_outstanding=Decimal("0.00"),
            interest_outstanding=Decimal("0.00"),
            total_outstanding=Decimal("0.00"),
            remarks=f"Loan foreclosure. {data.closure_remarks or ''}",
            processed_by=self.employee_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        self.db.add(transaction)
        
        # Update outstanding to zero
        loan.principal_paid += loan.principal_outstanding
        loan.principal_outstanding = Decimal("0.00")
        loan.interest_outstanding = Decimal("0.00")
        loan.total_outstanding = Decimal("0.00")
        
        # Mark all pending EMIs as waived
        pending_emis_query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.loan_id == loan.id,
                LoanEMISchedule.status == EMIStatus.PENDING,
                LoanEMISchedule.is_deleted == False
            )
        )
        result = await self.db.execute(pending_emis_query)
        pending_emis = result.scalars().all()
        
        for emi in pending_emis:
            emi.status = EMIStatus.WAIVED
            emi.is_waived = True
            emi.waived_amount = emi.emi_amount
            emi.waiver_reason = "Loan foreclosed"
            emi.waived_by = self.employee_id
            emi.waived_date = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(loan)
        
        return loan
    
    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================
    
    async def get_employee_loans(
        self,
        status: Optional[LoanStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[EmployeeLoan], int]:
        """Get employee's loans"""
        
        if not self.employee_id:
            return [], 0
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.employee_id == self.employee_id,
                EmployeeLoan.is_deleted == False
            )
        )
        
        if status:
            query = query.where(EmployeeLoan.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(desc(EmployeeLoan.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        loans = result.scalars().all()
        
        return loans, total
    
    async def get_loan_by_id(self, loan_id: str) -> Optional[EmployeeLoan]:
        """Get loan details by ID"""
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.id == loan_id,
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.is_deleted == False
            )
        ).options(
            selectinload(EmployeeLoan.employee),
            selectinload(EmployeeLoan.policy)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_emi_schedule(self, loan_id: str) -> List[LoanEMISchedule]:
        """Get EMI schedule for a loan"""
        
        query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.loan_id == loan_id,
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.is_deleted == False
            )
        ).order_by(LoanEMISchedule.emi_number)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_employee_loan_summary(self) -> EmployeeLoanSummary:
        """Get employee's loan summary"""
        
        if not self.employee_id:
            return EmployeeLoanSummary(
                total_loans=0,
                active_loans=0,
                closed_loans=0,
                total_borrowed=Decimal("0.00"),
                total_outstanding=Decimal("0.00"),
                total_paid=Decimal("0.00"),
                current_monthly_emi=Decimal("0.00"),
                overdue_emis=0,
                overdue_amount=Decimal("0.00")
            )
        
        # Get all loans
        loans_query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.tenant_id == self.tenant_id,
                EmployeeLoan.employee_id == self.employee_id,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await self.db.execute(loans_query)
        all_loans = result.scalars().all()
        
        total_loans = len(all_loans)
        active_loans = len([l for l in all_loans if l.status in [LoanStatus.ACTIVE, LoanStatus.DISBURSED]])
        closed_loans = len([l for l in all_loans if l.status == LoanStatus.CLOSED])
        
        total_borrowed = sum(l.disbursed_amount or Decimal("0.00") for l in all_loans)
        total_outstanding = sum(l.total_outstanding for l in all_loans if l.status == LoanStatus.ACTIVE)
        total_paid = sum(l.total_paid for l in all_loans)
        current_monthly_emi = sum(l.emi_amount for l in all_loans if l.status == LoanStatus.ACTIVE)
        
        # Get next EMI details
        next_emi_query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.status == EMIStatus.PENDING,
                LoanEMISchedule.is_deleted == False
            )
        ).join(
            EmployeeLoan, EmployeeLoan.id == LoanEMISchedule.loan_id
        ).where(
            EmployeeLoan.employee_id == self.employee_id
        ).order_by(LoanEMISchedule.emi_due_date).limit(1)
        
        result = await self.db.execute(next_emi_query)
        next_emi = result.scalar_one_or_none()
        
        next_emi_date = next_emi.emi_due_date if next_emi else None
        next_emi_amount = next_emi.emi_amount if next_emi else Decimal("0.00")
        
        # Get overdue EMIs
        overdue_query = select(
            func.count(LoanEMISchedule.id),
            func.sum(LoanEMISchedule.emi_amount)
        ).where(
            and_(
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.status == EMIStatus.PENDING,
                LoanEMISchedule.emi_due_date < date.today(),
                LoanEMISchedule.is_deleted == False
            )
        ).join(
            EmployeeLoan, EmployeeLoan.id == LoanEMISchedule.loan_id
        ).where(
            EmployeeLoan.employee_id == self.employee_id
        )
        
        result = await self.db.execute(overdue_query)
        overdue_count, overdue_amount = result.first()
        
        return EmployeeLoanSummary(
            total_loans=total_loans,
            active_loans=active_loans,
            closed_loans=closed_loans,
            total_borrowed=total_borrowed,
            total_outstanding=total_outstanding,
            total_paid=total_paid,
            current_monthly_emi=current_monthly_emi,
            next_emi_date=next_emi_date,
            next_emi_amount=next_emi_amount,
            overdue_emis=overdue_count or 0,
            overdue_amount=overdue_amount or Decimal("0.00")
        )
