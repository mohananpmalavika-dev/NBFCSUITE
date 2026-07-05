"""
Loan Disbursement Service
Handles loan account creation, sanction letter generation, and fund disbursement
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.loan_models import (
    LoanApplication,
    LoanAccount,
    LoanEMISchedule,
    LoanProduct
)
from backend.shared.database.customer_models import Customer, CustomerBankAccount
from backend.shared.database.models import User
from backend.services.loan.product_service import LoanProductService


class LoanDisbursementService:
    """Service for managing loan disbursement and account creation"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.product_service = LoanProductService(db, tenant_id, user_id)
    
    async def generate_loan_account_number(self) -> str:
        """Generate unique loan account number: LN-YYYYMM-XXXX"""
        now = datetime.now()
        prefix = f"LN-{now.year}{now.month:02d}"
        
        # Get the last loan account number for this month
        query = select(LoanAccount).where(
            and_(
                LoanAccount.tenant_id == self.tenant_id,
                LoanAccount.loan_account_number.like(f"{prefix}-%")
            )
        ).order_by(desc(LoanAccount.loan_account_number)).limit(1)
        
        result = await self.db.execute(query)
        last_account = result.scalar_one_or_none()
        
        if last_account:
            last_number = int(last_account.loan_account_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    async def generate_sanction_letter(
        self,
        application_id: int
    ) -> Dict[str, Any]:
        """
        Generate sanction letter for approved loan application
        
        Args:
            application_id: Loan application ID
            
        Returns:
            Dict with sanction letter details
        """
        # Get application with related data
        query = select(LoanApplication).where(
            and_(
                LoanApplication.id == application_id,
                LoanApplication.tenant_id == self.tenant_id,
                LoanApplication.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        application = result.scalar_one_or_none()
        
        if not application:
            raise ValueError("Loan application not found")
        
        if application.status != "approved":
            raise ValueError("Loan application is not approved")
        
        # Get customer details
        customer_query = select(Customer).where(Customer.id == application.customer_id)
        customer_result = await self.db.execute(customer_query)
        customer = customer_result.scalar_one_or_none()
        
        # Get product details
        product_query = select(LoanProduct).where(LoanProduct.id == application.loan_product_id)
        product_result = await self.db.execute(product_query)
        product = product_result.scalar_one_or_none()
        
        # Generate sanction letter data
        sanction_letter = {
            "sanction_number": f"SL-{datetime.now().year}{datetime.now().month:02d}-{application.id:06d}",
            "sanction_date": date.today().isoformat(),
            "application_number": application.application_number,
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "customer_id": customer.customer_id,
            "product_name": product.product_name,
            "sanctioned_amount": float(application.approved_amount),
            "tenure_months": application.tenure_months,
            "interest_rate": float(application.interest_rate),
            "emi_amount": float(application.emi_amount),
            "processing_fee": float(application.processing_fee or 0),
            "documentation_charges": float(application.documentation_charges or 0),
            "insurance_amount": float(application.insurance_amount or 0),
            "total_deductions": float(application.total_deductions or 0),
            "net_disbursement": float(application.net_disbursement),
            "first_emi_date": None,  # Will be set during disbursement
            "last_emi_date": None,
            "total_interest": float(application.total_interest),
            "total_repayment": float(application.total_repayment),
            "terms_and_conditions": product.terms_and_conditions,
            "validity_days": 30,  # Sanction valid for 30 days
            "expiry_date": (date.today() + timedelta(days=30)).isoformat()
        }
        
        return sanction_letter
    
    async def create_loan_account(
        self,
        application_id: int,
        disbursement_date: date,
        emi_start_day: int = 5,
        remarks: Optional[str] = None
    ) -> LoanAccount:
        """
        Create loan account from approved application
        
        Args:
            application_id: Loan application ID
            disbursement_date: Date of disbursement
            emi_start_day: Day of month for EMI (default: 5)
            remarks: Optional remarks
            
        Returns:
            Created loan account
        """
        # Get application
        query = select(LoanApplication).where(
            and_(
                LoanApplication.id == application_id,
                LoanApplication.tenant_id == self.tenant_id,
                LoanApplication.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        application = result.scalar_one_or_none()
        
        if not application:
            raise ValueError("Loan application not found")
        
        if application.status != "approved":
            raise ValueError("Loan application is not approved")
        
        # Check if loan account already exists
        existing_query = select(LoanAccount).where(
            and_(
                LoanAccount.loan_application_id == application_id,
                LoanAccount.tenant_id == self.tenant_id,
                LoanAccount.is_deleted == False
            )
        )
        existing_result = await self.db.execute(existing_query)
        existing_account = existing_result.scalar_one_or_none()
        
        if existing_account:
            raise ValueError("Loan account already exists for this application")
        
        # Generate account number
        account_number = await self.generate_loan_account_number()
        
        # Calculate EMI dates
        first_emi_date = disbursement_date.replace(day=emi_start_day)
        if first_emi_date <= disbursement_date:
            # If EMI day is before/same as disbursement, start next month
            if first_emi_date.month == 12:
                first_emi_date = first_emi_date.replace(year=first_emi_date.year + 1, month=1)
            else:
                first_emi_date = first_emi_date.replace(month=first_emi_date.month + 1)
        
        # Calculate last EMI date
        last_emi_date = first_emi_date
        months_to_add = application.tenure_months - 1
        for _ in range(months_to_add):
            if last_emi_date.month == 12:
                last_emi_date = last_emi_date.replace(year=last_emi_date.year + 1, month=1)
            else:
                last_emi_date = last_emi_date.replace(month=last_emi_date.month + 1)
        
        # Create loan account
        loan_account = LoanAccount(
            tenant_id=self.tenant_id,
            loan_account_number=account_number,
            loan_application_id=application.id,
            customer_id=application.customer_id,
            loan_product_id=application.loan_product_id,
            sanctioned_amount=application.approved_amount,
            disbursed_amount=application.net_disbursement,
            outstanding_principal=application.approved_amount,
            outstanding_interest=Decimal("0.00"),
            outstanding_charges=Decimal("0.00"),
            total_outstanding=application.approved_amount,
            tenure_months=application.tenure_months,
            interest_rate=application.interest_rate,
            emi_amount=application.emi_amount,
            emi_day=emi_start_day,
            disbursement_date=disbursement_date,
            first_emi_date=first_emi_date,
            last_emi_date=last_emi_date,
            maturity_date=last_emi_date,
            status="active",
            overdue_days=0,
            dpd=0,
            next_due_date=first_emi_date,
            next_due_amount=application.emi_amount,
            prepayment_allowed=True,
            prepayment_charges_percentage=Decimal("2.00"),  # Default 2%
            penal_interest_outstanding=Decimal("0.00"),
            interest_accrued=Decimal("0.00"),
            interest_received=Decimal("0.00"),
            principal_received=Decimal("0.00"),
            internal_notes=remarks,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(loan_account)
        await self.db.flush()
        
        # Generate EMI schedule
        await self._generate_emi_schedule(loan_account, application)
        
        # Update application status
        application.status = "disbursed"
        application.disbursement_date = disbursement_date
        application.updated_by = self.user_id
        application.updated_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(loan_account)
        
        return loan_account
    
    async def _generate_emi_schedule(
        self,
        loan_account: LoanAccount,
        application: LoanApplication
    ) -> None:
        """
        Generate EMI schedule for loan account
        
        Args:
            loan_account: Loan account object
            application: Loan application object
        """
        # Get product to determine calculation method
        product_query = select(LoanProduct).where(LoanProduct.id == application.loan_product_id)
        product_result = await self.db.execute(product_query)
        product = product_result.scalar_one_or_none()
        
        # Calculate EMI schedule using product service
        emi_schedule_data = await self.product_service.calculate_emi_schedule(
            principal=float(application.approved_amount),
            interest_rate=float(application.interest_rate),
            tenure_months=application.tenure_months,
            calculation_method=product.interest_rate_type,
            emi_start_date=loan_account.first_emi_date
        )
        
        # Create EMI schedule records
        for idx, schedule_item in enumerate(emi_schedule_data["schedule"], start=1):
            emi_record = LoanEMISchedule(
                tenant_id=self.tenant_id,
                loan_account_id=loan_account.id,
                installment_number=idx,
                due_date=datetime.strptime(schedule_item["due_date"], "%Y-%m-%d").date(),
                emi_amount=Decimal(str(schedule_item["emi_amount"])),
                principal_component=Decimal(str(schedule_item["principal"])),
                interest_component=Decimal(str(schedule_item["interest"])),
                opening_principal=Decimal(str(schedule_item["opening_balance"])),
                closing_principal=Decimal(str(schedule_item["closing_balance"])),
                status="pending",
                paid_amount=Decimal("0.00"),
                paid_principal=Decimal("0.00"),
                paid_interest=Decimal("0.00"),
                overdue_days=0,
                penal_interest=Decimal("0.00")
            )
            self.db.add(emi_record)
        
        await self.db.flush()
    
    async def approve_disbursement(
        self,
        application_id: int,
        bank_account_id: int,
        disbursement_date: date,
        disbursement_mode: str,
        emi_start_day: int = 5,
        remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve and process loan disbursement
        
        Args:
            application_id: Loan application ID
            bank_account_id: Customer bank account ID for disbursement
            disbursement_date: Date of disbursement
            disbursement_mode: Mode of disbursement (neft, rtgs, imps, cheque)
            emi_start_day: Day of month for EMI
            remarks: Optional remarks
            
        Returns:
            Dict with disbursement details and loan account
        """
        # Get application
        query = select(LoanApplication).where(
            and_(
                LoanApplication.id == application_id,
                LoanApplication.tenant_id == self.tenant_id,
                LoanApplication.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        application = result.scalar_one_or_none()
        
        if not application:
            raise ValueError("Loan application not found")
        
        if application.status != "approved":
            raise ValueError("Loan application is not approved")
        
        # Verify bank account
        bank_query = select(CustomerBankAccount).where(
            and_(
                CustomerBankAccount.id == bank_account_id,
                CustomerBankAccount.customer_id == application.customer_id,
                CustomerBankAccount.tenant_id == self.tenant_id,
                CustomerBankAccount.is_deleted == False
            )
        )
        bank_result = await self.db.execute(bank_query)
        bank_account = bank_result.scalar_one_or_none()
        
        if not bank_account:
            raise ValueError("Bank account not found or does not belong to customer")
        
        if not bank_account.is_primary and bank_account.status != "verified":
            raise ValueError("Bank account must be verified for disbursement")
        
        # Update application with disbursement details
        application.disbursement_bank_account_id = bank_account_id
        application.disbursement_mode = disbursement_mode
        application.disbursement_reference = f"DISB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        application.updated_by = self.user_id
        application.updated_at = datetime.now()
        
        # Create loan account
        loan_account = await self.create_loan_account(
            application_id=application_id,
            disbursement_date=disbursement_date,
            emi_start_day=emi_start_day,
            remarks=remarks
        )
        
        # Prepare disbursement response
        disbursement_details = {
            "loan_account_number": loan_account.loan_account_number,
            "application_number": application.application_number,
            "customer_id": application.customer_id,
            "disbursement_amount": float(loan_account.disbursed_amount),
            "disbursement_date": disbursement_date.isoformat(),
            "disbursement_mode": disbursement_mode,
            "disbursement_reference": application.disbursement_reference,
            "bank_account": {
                "account_number": bank_account.account_number,
                "bank_name": bank_account.bank_name,
                "ifsc_code": bank_account.ifsc_code,
                "account_holder_name": bank_account.account_holder_name
            },
            "emi_details": {
                "emi_amount": float(loan_account.emi_amount),
                "first_emi_date": loan_account.first_emi_date.isoformat(),
                "last_emi_date": loan_account.last_emi_date.isoformat(),
                "emi_day": loan_account.emi_day,
                "total_emis": loan_account.tenure_months
            },
            "status": "disbursed",
            "message": "Loan disbursed successfully"
        }
        
        return disbursement_details
    
    async def get_loan_account(
        self,
        account_id: Optional[int] = None,
        account_number: Optional[str] = None,
        include_schedule: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get loan account details
        
        Args:
            account_id: Loan account ID
            account_number: Loan account number
            include_schedule: Include EMI schedule
            
        Returns:
            Loan account details with optional EMI schedule
        """
        if not account_id and not account_number:
            raise ValueError("Either account_id or account_number must be provided")
        
        # Build query
        conditions = [
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False
        ]
        
        if account_id:
            conditions.append(LoanAccount.id == account_id)
        if account_number:
            conditions.append(LoanAccount.loan_account_number == account_number)
        
        query = select(LoanAccount).where(and_(*conditions))
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            return None
        
        # Build response
        account_data = {
            "id": account.id,
            "loan_account_number": account.loan_account_number,
            "customer_id": account.customer_id,
            "loan_product_id": account.loan_product_id,
            "loan_application_id": account.loan_application_id,
            "sanctioned_amount": float(account.sanctioned_amount),
            "disbursed_amount": float(account.disbursed_amount),
            "outstanding_principal": float(account.outstanding_principal),
            "outstanding_interest": float(account.outstanding_interest),
            "outstanding_charges": float(account.outstanding_charges),
            "total_outstanding": float(account.total_outstanding),
            "tenure_months": account.tenure_months,
            "interest_rate": float(account.interest_rate),
            "emi_amount": float(account.emi_amount),
            "emi_day": account.emi_day,
            "disbursement_date": account.disbursement_date.isoformat(),
            "first_emi_date": account.first_emi_date.isoformat(),
            "last_emi_date": account.last_emi_date.isoformat(),
            "maturity_date": account.maturity_date.isoformat(),
            "closure_date": account.closure_date.isoformat() if account.closure_date else None,
            "status": account.status,
            "overdue_days": account.overdue_days,
            "dpd": account.dpd,
            "last_payment_date": account.last_payment_date.isoformat() if account.last_payment_date else None,
            "last_payment_amount": float(account.last_payment_amount) if account.last_payment_amount else None,
            "next_due_date": account.next_due_date.isoformat() if account.next_due_date else None,
            "next_due_amount": float(account.next_due_amount) if account.next_due_amount else None,
            "npa_status": account.npa_status,
            "npa_date": account.npa_date.isoformat() if account.npa_date else None,
            "prepayment_allowed": account.prepayment_allowed,
            "prepayment_charges_percentage": float(account.prepayment_charges_percentage) if account.prepayment_charges_percentage else None,
            "penal_interest_outstanding": float(account.penal_interest_outstanding),
            "interest_accrued": float(account.interest_accrued),
            "interest_received": float(account.interest_received),
            "principal_received": float(account.principal_received),
            "internal_notes": account.internal_notes,
            "created_at": account.created_at.isoformat(),
            "updated_at": account.updated_at.isoformat()
        }
        
        # Include EMI schedule if requested
        if include_schedule:
            schedule_query = select(LoanEMISchedule).where(
                and_(
                    LoanEMISchedule.loan_account_id == account.id,
                    LoanEMISchedule.tenant_id == self.tenant_id
                )
            ).order_by(LoanEMISchedule.installment_number)
            
            schedule_result = await self.db.execute(schedule_query)
            schedules = schedule_result.scalars().all()
            
            account_data["emi_schedule"] = [
                {
                    "installment_number": sch.installment_number,
                    "due_date": sch.due_date.isoformat(),
                    "emi_amount": float(sch.emi_amount),
                    "principal_component": float(sch.principal_component),
                    "interest_component": float(sch.interest_component),
                    "opening_principal": float(sch.opening_principal),
                    "closing_principal": float(sch.closing_principal),
                    "status": sch.status,
                    "paid_amount": float(sch.paid_amount),
                    "paid_principal": float(sch.paid_principal),
                    "paid_interest": float(sch.paid_interest),
                    "payment_date": sch.payment_date.isoformat() if sch.payment_date else None,
                    "overdue_days": sch.overdue_days,
                    "penal_interest": float(sch.penal_interest)
                }
                for sch in schedules
            ]
        
        return account_data
    
    async def list_loan_accounts(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        product_id: Optional[int] = None,
        overdue_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        List loan accounts with filters
        
        Args:
            customer_id: Filter by customer
            status: Filter by status
            product_id: Filter by product
            overdue_only: Show only overdue accounts
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            Dict with accounts list and pagination info
        """
        # Build query conditions
        conditions = [
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False
        ]
        
        if customer_id:
            conditions.append(LoanAccount.customer_id == customer_id)
        if status:
            conditions.append(LoanAccount.status == status)
        if product_id:
            conditions.append(LoanAccount.loan_product_id == product_id)
        if overdue_only:
            conditions.append(LoanAccount.overdue_days > 0)
        
        # Count total
        count_query = select(func.count(LoanAccount.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get accounts
        query = select(LoanAccount).where(and_(*conditions)).order_by(
            desc(LoanAccount.created_at)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        
        # Build response
        accounts_data = []
        for account in accounts:
            accounts_data.append({
                "id": account.id,
                "loan_account_number": account.loan_account_number,
                "customer_id": account.customer_id,
                "sanctioned_amount": float(account.sanctioned_amount),
                "disbursed_amount": float(account.disbursed_amount),
                "total_outstanding": float(account.total_outstanding),
                "outstanding_principal": float(account.outstanding_principal),
                "outstanding_interest": float(account.outstanding_interest),
                "emi_amount": float(account.emi_amount),
                "tenure_months": account.tenure_months,
                "interest_rate": float(account.interest_rate),
                "disbursement_date": account.disbursement_date.isoformat(),
                "next_due_date": account.next_due_date.isoformat() if account.next_due_date else None,
                "status": account.status,
                "overdue_days": account.overdue_days,
                "dpd": account.dpd,
                "created_at": account.created_at.isoformat()
            })
        
        return {
            "accounts": accounts_data,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }
