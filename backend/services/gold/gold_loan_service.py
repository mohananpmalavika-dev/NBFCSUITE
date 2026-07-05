"""
Gold Loan Service
Business logic for gold loan management
"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from fastapi import HTTPException, status
import uuid

from backend.shared.database.gold_loan_models import (
    GoldLoanProduct,
    GoldOrnament,
    GoldLoanAccount,
    GoldLoanTransaction,
    GoldReleaseRequest,
    GoldAuction
)
from backend.services.gold import schemas


class GoldLoanService:
    """Service for gold loan operations"""

    def __init__(self, db: AsyncSession, user_id: str, tenant_id: str):
        self.db = db
        self.user_id = user_id
        self.tenant_id = tenant_id

    # ============================================
    # Gold Loan Product Management
    # ============================================

    async def create_product(self, product_data: schemas.GoldLoanProductCreate) -> GoldLoanProduct:
        """Create new gold loan product"""
        
        # Check if product code already exists
        existing = await self.db.execute(
            select(GoldLoanProduct).where(
                and_(
                    GoldLoanProduct.tenant_id == self.tenant_id,
                    GoldLoanProduct.product_code == product_data.product_code
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product code already exists"
            )

        product = GoldLoanProduct(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            **product_data.model_dump()
        )
        
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        
        return product

    async def get_product(self, product_id: str) -> Optional[GoldLoanProduct]:
        """Get product by ID"""
        result = await self.db.execute(
            select(GoldLoanProduct).where(
                and_(
                    GoldLoanProduct.id == product_id,
                    GoldLoanProduct.tenant_id == self.tenant_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_products(self, is_active: Optional[bool] = None) -> List[GoldLoanProduct]:
        """List all gold loan products"""
        query = select(GoldLoanProduct).where(
            GoldLoanProduct.tenant_id == self.tenant_id
        )
        
        if is_active is not None:
            query = query.where(GoldLoanProduct.is_active == is_active)
        
        query = query.order_by(GoldLoanProduct.product_name)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_product(
        self, 
        product_id: str, 
        product_data: schemas.GoldLoanProductUpdate
    ) -> GoldLoanProduct:
        """Update gold loan product"""
        product = await self.get_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        await self.db.commit()
        await self.db.refresh(product)
        
        return product

    # ============================================
    # Gold Loan Account Management
    # ============================================

    async def create_gold_loan(
        self, 
        loan_data: schemas.GoldLoanAccountCreate
    ) -> Tuple[GoldLoanAccount, List[GoldOrnament]]:
        """Create new gold loan with ornaments"""
        
        # Get product
        product = await self.get_product(loan_data.product_id)
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive product"
            )

        # Calculate gold totals
        total_weight = sum(o.net_weight_grams for o in loan_data.ornaments)
        total_value = sum(o.appraised_value for o in loan_data.ornaments)
        avg_rate = total_value / total_weight if total_weight > 0 else 0

        # Calculate LTV and sanctioned amount
        ltv_ratio = product.ltv_ratio
        max_loan = total_value * (ltv_ratio / 100)
        sanctioned_amount = min(loan_data.loan_amount, max_loan)

        # Validate loan amount
        if sanctioned_amount < product.min_loan_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Loan amount must be at least ₹{product.min_loan_amount}"
            )
        
        if sanctioned_amount > product.max_loan_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Loan amount cannot exceed ₹{product.max_loan_amount}"
            )

        # Calculate charges
        processing_fee = (sanctioned_amount * product.processing_fee_percentage / 100) + product.processing_fee_flat
        valuation_charges = product.valuation_charges
        documentation_charges = product.documentation_charges
        insurance_charges = sanctioned_amount * (product.insurance_percentage / 100) if product.insurance_required else 0

        # Calculate EMI (for monthly/quarterly repayment)
        emi_amount = None
        if loan_data.repayment_frequency != "Bullet":
            # Simple EMI calculation (can be enhanced)
            monthly_rate = product.default_interest_rate / 12 / 100
            n_payments = loan_data.tenure_months if loan_data.repayment_frequency == "Monthly" else loan_data.tenure_months // 3
            if monthly_rate > 0 and n_payments > 0:
                emi_amount = sanctioned_amount * monthly_rate * ((1 + monthly_rate) ** n_payments) / (((1 + monthly_rate) ** n_payments) - 1)

        # Generate loan account number
        loan_account_number = f"GL{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}"

        # Create loan account
        start_date = datetime.utcnow()
        maturity_date = start_date + timedelta(days=loan_data.tenure_months * 30)

        loan = GoldLoanAccount(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            loan_account_number=loan_account_number,
            customer_id=loan_data.customer_id,
            product_id=loan_data.product_id,
            application_date=start_date,
            loan_amount=loan_data.loan_amount,
            sanctioned_amount=sanctioned_amount,
            disbursed_amount=sanctioned_amount,
            total_gold_weight_grams=total_weight,
            total_gold_value=total_value,
            average_gold_rate=avg_rate,
            ltv_ratio=ltv_ratio,
            interest_rate=product.default_interest_rate,
            penal_interest_rate=product.penal_interest_rate,
            tenure_months=loan_data.tenure_months,
            start_date=start_date,
            maturity_date=maturity_date,
            repayment_frequency=loan_data.repayment_frequency,
            emi_amount=emi_amount,
            processing_fee=processing_fee,
            valuation_charges=valuation_charges,
            documentation_charges=documentation_charges,
            insurance_charges=insurance_charges,
            principal_outstanding=sanctioned_amount,
            total_outstanding=sanctioned_amount,
            status="Active",
            branch_id=loan_data.branch_id,
            approval_date=start_date,
            disbursement_date=start_date,
            is_active=True,
            is_npa=False,
            remarks=loan_data.remarks
        )

        self.db.add(loan)

        # Create ornament records
        ornaments = []
        for idx, ornament_data in enumerate(loan_data.ornaments, 1):
            ornament = GoldOrnament(
                id=str(uuid.uuid4()),
                tenant_id=self.tenant_id,
                gold_loan_id=loan.id,
                item_number=idx,
                remaining_weight_grams=ornament_data.net_weight_grams,
                **ornament_data.model_dump()
            )
            self.db.add(ornament)
            ornaments.append(ornament)

        # Create disbursement transaction
        await self._create_transaction(
            gold_loan_id=loan.id,
            transaction_type="Disbursement",
            amount=sanctioned_amount,
            principal_amount=sanctioned_amount,
            principal_balance=sanctioned_amount,
            interest_balance=0,
            total_balance=sanctioned_amount
        )

        await self.db.commit()
        await self.db.refresh(loan)

        return loan, ornaments

    async def get_gold_loan(self, loan_id: str) -> Optional[GoldLoanAccount]:
        """Get gold loan by ID"""
        result = await self.db.execute(
            select(GoldLoanAccount).where(
                and_(
                    GoldLoanAccount.id == loan_id,
                    GoldLoanAccount.tenant_id == self.tenant_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_gold_loan_with_ornaments(
        self, 
        loan_id: str
    ) -> Optional[Tuple[GoldLoanAccount, List[GoldOrnament]]]:
        """Get gold loan with ornaments"""
        loan = await self.get_gold_loan(loan_id)
        if not loan:
            return None

        # Get ornaments
        result = await self.db.execute(
            select(GoldOrnament).where(
                and_(
                    GoldOrnament.gold_loan_id == loan_id,
                    GoldOrnament.tenant_id == self.tenant_id,
                    GoldOrnament.is_active == True
                )
            ).order_by(GoldOrnament.item_number)
        )
        ornaments = result.scalars().all()

        return loan, ornaments

    async def list_gold_loans(
        self,
        params: schemas.GoldLoanListParams
    ) -> Tuple[List[GoldLoanAccount], int]:
        """List gold loans with filters and pagination"""
        
        query = select(GoldLoanAccount).where(
            GoldLoanAccount.tenant_id == self.tenant_id
        )

        # Apply filters
        if params.status:
            query = query.where(GoldLoanAccount.status == params.status)
        
        if params.customer_id:
            query = query.where(GoldLoanAccount.customer_id == params.customer_id)
        
        if params.branch_id:
            query = query.where(GoldLoanAccount.branch_id == params.branch_id)
        
        if params.is_npa is not None:
            query = query.where(GoldLoanAccount.is_npa == params.is_npa)
        
        if params.from_date:
            query = query.where(GoldLoanAccount.application_date >= params.from_date)
        
        if params.to_date:
            query = query.where(GoldLoanAccount.application_date <= params.to_date)
        
        if params.search:
            search_term = f"%{params.search}%"
            query = query.where(
                or_(
                    GoldLoanAccount.loan_account_number.ilike(search_term),
                    GoldLoanAccount.customer_id.ilike(search_term)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.order_by(desc(GoldLoanAccount.created_at))
        query = query.offset((params.page - 1) * params.page_size).limit(params.page_size)

        result = await self.db.execute(query)
        loans = result.scalars().all()

        return loans, total

    # ============================================
    # Payment Management
    # ============================================

    async def record_payment(
        self,
        payment_data: schemas.GoldLoanTransactionCreate
    ) -> GoldLoanTransaction:
        """Record a payment transaction"""
        
        loan = await self.get_gold_loan(payment_data.gold_loan_id)
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gold loan not found"
            )

        if loan.status not in ["Active", "Overdue"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot record payment for loan in current status"
            )

        # Calculate balance after payment
        new_principal = loan.principal_outstanding - payment_data.principal_amount
        new_interest = loan.interest_outstanding - payment_data.interest_amount
        new_penal = loan.penal_interest_outstanding - payment_data.penal_interest_amount
        new_total = new_principal + new_interest + new_penal

        # Create transaction
        transaction = await self._create_transaction(
            gold_loan_id=loan.id,
            transaction_type="Payment",
            amount=payment_data.amount,
            principal_amount=payment_data.principal_amount,
            interest_amount=payment_data.interest_amount,
            penal_interest_amount=payment_data.penal_interest_amount,
            charges_amount=payment_data.charges_amount,
            payment_mode=payment_data.payment_mode,
            payment_reference=payment_data.payment_reference,
            bank_name=payment_data.bank_name,
            cheque_number=payment_data.cheque_number,
            transaction_id=payment_data.transaction_id,
            principal_balance=new_principal,
            interest_balance=new_interest,
            total_balance=new_total,
            remarks=payment_data.remarks
        )

        # Update loan outstanding
        loan.principal_outstanding = new_principal
        loan.interest_outstanding = new_interest
        loan.penal_interest_outstanding = new_penal
        loan.total_outstanding = new_total
        loan.last_payment_date = datetime.utcnow()
        loan.last_payment_amount = payment_data.amount

        # Update status if fully paid
        if new_total <= 0:
            loan.status = "Closed"
            loan.closure_date = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(transaction)

        return transaction

    # ============================================
    # Gold Release Management
    # ============================================

    async def create_release_request(
        self,
        request_data: schemas.GoldReleaseRequestCreate
    ) -> GoldReleaseRequest:
        """Create gold release request"""
        
        loan = await self.get_gold_loan(request_data.gold_loan_id)
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gold loan not found"
            )

        # Get ornaments to release
        ornaments_result = await self.db.execute(
            select(GoldOrnament).where(
                and_(
                    GoldOrnament.id.in_(request_data.ornament_ids),
                    GoldOrnament.tenant_id == self.tenant_id,
                    GoldOrnament.status == "Pledged"
                )
            )
        )
        ornaments = ornaments_result.scalars().all()

        if len(ornaments) != len(request_data.ornament_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some ornaments not found or already released"
            )

        # Calculate release totals
        release_weight = sum(o.remaining_weight_grams for o in ornaments)
        release_value = sum(o.appraised_value for o in ornaments)

        # Generate request number
        request_number = f"GR{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}"

        # Calculate new loan details for partial release
        new_gold_weight = None
        new_gold_value = None
        new_loan_amount = None
        new_ltv = None

        if request_data.release_type == "Partial":
            new_gold_weight = loan.total_gold_weight_grams - release_weight
            new_gold_value = loan.total_gold_value - release_value
            new_loan_amount = loan.principal_outstanding - request_data.payment_amount
            new_ltv = (new_loan_amount / new_gold_value * 100) if new_gold_value > 0 else 0

        release_request = GoldReleaseRequest(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            request_number=request_number,
            gold_loan_id=loan.id,
            customer_id=loan.customer_id,
            release_type=request_data.release_type,
            ornament_ids=",".join(request_data.ornament_ids),
            total_release_weight_grams=release_weight,
            total_release_value=release_value,
            payment_amount=request_data.payment_amount,
            payment_mode=request_data.payment_mode,
            payment_reference=request_data.payment_reference,
            new_gold_weight_grams=new_gold_weight,
            new_gold_value=new_gold_value,
            new_loan_amount=new_loan_amount,
            new_ltv_ratio=new_ltv,
            request_date=datetime.utcnow(),
            requested_by=self.user_id,
            approval_status="Pending",
            status="Pending",
            remarks=request_data.remarks
        )

        self.db.add(release_request)
        await self.db.commit()
        await self.db.refresh(release_request)

        return release_request

    # ============================================
    # Statistics & Reports
    # ============================================

    async def get_statistics(self) -> schemas.GoldLoanStatistics:
        """Get gold loan statistics"""
        
        # Total loans
        total_result = await self.db.execute(
            select(func.count()).select_from(GoldLoanAccount).where(
                GoldLoanAccount.tenant_id == self.tenant_id
            )
        )
        total_loans = total_result.scalar()

        # Active loans
        active_result = await self.db.execute(
            select(func.count()).select_from(GoldLoanAccount).where(
                and_(
                    GoldLoanAccount.tenant_id == self.tenant_id,
                    GoldLoanAccount.status == "Active"
                )
            )
        )
        active_loans = active_result.scalar()

        # Disbursed and outstanding amounts
        amounts_result = await self.db.execute(
            select(
                func.sum(GoldLoanAccount.disbursed_amount),
                func.sum(GoldLoanAccount.total_outstanding),
                func.sum(GoldLoanAccount.total_gold_weight_grams),
                func.avg(GoldLoanAccount.ltv_ratio)
            ).where(
                and_(
                    GoldLoanAccount.tenant_id == self.tenant_id,
                    GoldLoanAccount.is_active == True
                )
            )
        )
        amounts = amounts_result.first()

        # NPA loans
        npa_result = await self.db.execute(
            select(
                func.count(),
                func.sum(GoldLoanAccount.total_outstanding)
            ).where(
                and_(
                    GoldLoanAccount.tenant_id == self.tenant_id,
                    GoldLoanAccount.is_npa == True
                )
            )
        )
        npa_data = npa_result.first()

        # Overdue loans
        overdue_result = await self.db.execute(
            select(
                func.count(),
                func.sum(GoldLoanAccount.overdue_amount)
            ).where(
                and_(
                    GoldLoanAccount.tenant_id == self.tenant_id,
                    GoldLoanAccount.days_past_due > 0
                )
            )
        )
        overdue_data = overdue_result.first()

        return schemas.GoldLoanStatistics(
            total_loans=total_loans,
            active_loans=active_loans,
            total_disbursed=amounts[0] or 0,
            total_outstanding=amounts[1] or 0,
            total_gold_weight_kg=(amounts[2] or 0) / 1000,
            average_ltv_ratio=amounts[3] or 0,
            npa_count=npa_data[0] or 0,
            npa_amount=npa_data[1] or 0,
            overdue_count=overdue_data[0] or 0,
            overdue_amount=overdue_data[1] or 0
        )

    # ============================================
    # Helper Methods
    # ============================================

    async def _create_transaction(
        self,
        gold_loan_id: str,
        transaction_type: str,
        amount: Decimal,
        principal_amount: Decimal = Decimal("0.00"),
        interest_amount: Decimal = Decimal("0.00"),
        penal_interest_amount: Decimal = Decimal("0.00"),
        charges_amount: Decimal = Decimal("0.00"),
        payment_mode: Optional[str] = None,
        payment_reference: Optional[str] = None,
        bank_name: Optional[str] = None,
        cheque_number: Optional[str] = None,
        transaction_id: Optional[str] = None,
        principal_balance: Decimal = Decimal("0.00"),
        interest_balance: Decimal = Decimal("0.00"),
        total_balance: Decimal = Decimal("0.00"),
        remarks: Optional[str] = None
    ) -> GoldLoanTransaction:
        """Helper to create transaction record"""
        
        transaction_number = f"GT{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}"

        transaction = GoldLoanTransaction(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            transaction_number=transaction_number,
            gold_loan_id=gold_loan_id,
            transaction_date=datetime.utcnow(),
            transaction_type=transaction_type,
            amount=amount,
            principal_amount=principal_amount,
            interest_amount=interest_amount,
            penal_interest_amount=penal_interest_amount,
            charges_amount=charges_amount,
            payment_mode=payment_mode,
            payment_reference=payment_reference,
            bank_name=bank_name,
            cheque_number=cheque_number,
            transaction_id=transaction_id,
            principal_balance=principal_balance,
            interest_balance=interest_balance,
            total_balance=total_balance,
            created_by=self.user_id,
            status="Completed",
            remarks=remarks
        )

        self.db.add(transaction)
        return transaction
