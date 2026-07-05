"""
Loan Product Service
Manages loan product configuration and operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import math

from backend.shared.database.loan_models import LoanProduct
from .schemas import (
    LoanProductCreate, LoanProductUpdate, LoanProductResponse,
    LoanProductListResponse, EMICalculationRequest, EMICalculationResponse,
    EMIScheduleResponse, EMIScheduleRow, InterestRateType
)


class LoanProductService:
    """Service for loan product operations"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    def create_product(self, data: LoanProductCreate, user_id: int) -> LoanProduct:
        """Create new loan product"""
        
        # Check if product code already exists
        existing = self.db.query(LoanProduct).filter(
            and_(
                LoanProduct.tenant_id == self.tenant_id,
                LoanProduct.product_code == data.product_code,
                LoanProduct.is_deleted == False
            )
        ).first()
        
        if existing:
            raise ValueError(f"Product code '{data.product_code}' already exists")
        
        # Create product
        product = LoanProduct(
            tenant_id=self.tenant_id,
            **data.model_dump(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def get_product(self, product_id: int) -> Optional[LoanProduct]:
        """Get loan product by ID"""
        return self.db.query(LoanProduct).filter(
            and_(
                LoanProduct.id == product_id,
                LoanProduct.tenant_id == self.tenant_id,
                LoanProduct.is_deleted == False
            )
        ).first()
    
    def get_product_by_code(self, product_code: str) -> Optional[LoanProduct]:
        """Get loan product by code"""
        return self.db.query(LoanProduct).filter(
            and_(
                LoanProduct.product_code == product_code,
                LoanProduct.tenant_id == self.tenant_id,
                LoanProduct.is_deleted == False
            )
        ).first()
    
    def list_products(
        self,
        page: int = 1,
        page_size: int = 50,
        product_type: Optional[str] = None,
        loan_category: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> LoanProductListResponse:
        """List loan products with filters"""
        
        query = self.db.query(LoanProduct).filter(
            and_(
                LoanProduct.tenant_id == self.tenant_id,
                LoanProduct.is_deleted == False
            )
        )
        
        # Apply filters
        if product_type:
            query = query.filter(LoanProduct.product_type == product_type)
        
        if loan_category:
            query = query.filter(LoanProduct.loan_category == loan_category)
        
        if is_active is not None:
            query = query.filter(LoanProduct.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    LoanProduct.product_name.ilike(search_term),
                    LoanProduct.product_code.ilike(search_term),
                    LoanProduct.description.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and sorting
        query = query.order_by(
            LoanProduct.display_order.asc(),
            LoanProduct.product_name.asc()
        )
        
        products = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return LoanProductListResponse(
            items=[LoanProductResponse.model_validate(p) for p in products],
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total > 0 else 0
        )
    
    def update_product(
        self,
        product_id: int,
        data: LoanProductUpdate,
        user_id: int
    ) -> Optional[LoanProduct]:
        """Update loan product"""
        
        product = self.get_product(product_id)
        if not product:
            return None
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        product.updated_by = user_id
        product.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete loan product"""
        
        product = self.get_product(product_id)
        if not product:
            return False
        
        # Check if product has active applications
        from backend.shared.database.loan_models import LoanApplication
        active_applications = self.db.query(LoanApplication).filter(
            and_(
                LoanApplication.loan_product_id == product_id,
                LoanApplication.status.in_(['submitted', 'under_review', 
                                           'credit_assessment', 'pending_approval']),
                LoanApplication.is_deleted == False
            )
        ).count()
        
        if active_applications > 0:
            raise ValueError(
                f"Cannot delete product with {active_applications} active applications"
            )
        
        product.is_deleted = True
        product.is_active = False
        product.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def get_active_products(self) -> List[LoanProduct]:
        """Get all active loan products"""
        return self.db.query(LoanProduct).filter(
            and_(
                LoanProduct.tenant_id == self.tenant_id,
                LoanProduct.is_active == True,
                LoanProduct.is_deleted == False
            )
        ).order_by(
            LoanProduct.display_order.asc(),
            LoanProduct.product_name.asc()
        ).all()
    
    def get_featured_products(self) -> List[LoanProduct]:
        """Get featured loan products"""
        return self.db.query(LoanProduct).filter(
            and_(
                LoanProduct.tenant_id == self.tenant_id,
                LoanProduct.is_active == True,
                LoanProduct.is_featured == True,
                LoanProduct.is_deleted == False
            )
        ).order_by(
            LoanProduct.display_order.asc()
        ).all()
    
    def calculate_emi(
        self,
        request: EMICalculationRequest,
        product: Optional[LoanProduct] = None
    ) -> EMICalculationResponse:
        """Calculate EMI for given loan parameters"""
        
        principal = float(request.loan_amount)
        rate = float(request.interest_rate)
        tenure = request.tenure_months
        
        if request.interest_rate_type == InterestRateType.FLAT:
            # Flat rate calculation
            total_interest = (principal * rate * tenure) / (12 * 100)
            total_repayment = principal + total_interest
            emi = total_repayment / tenure
        
        elif request.interest_rate_type == InterestRateType.REDUCING:
            # Reducing balance method
            monthly_rate = rate / (12 * 100)
            if monthly_rate == 0:
                emi = principal / tenure
                total_interest = 0
            else:
                emi = principal * monthly_rate * math.pow(1 + monthly_rate, tenure) / \
                      (math.pow(1 + monthly_rate, tenure) - 1)
                total_interest = (emi * tenure) - principal
            
            total_repayment = principal + total_interest
        
        else:
            # Compound interest (similar to reducing)
            monthly_rate = rate / (12 * 100)
            if monthly_rate == 0:
                emi = principal / tenure
                total_interest = 0
            else:
                emi = principal * monthly_rate * math.pow(1 + monthly_rate, tenure) / \
                      (math.pow(1 + monthly_rate, tenure) - 1)
                total_interest = (emi * tenure) - principal
            
            total_repayment = principal + total_interest
        
        # Calculate processing fee if product provided
        processing_fee = Decimal("0")
        if product:
            if product.processing_fee_type == "fixed":
                processing_fee = product.processing_fee_value
            else:  # percentage
                processing_fee = (request.loan_amount * product.processing_fee_value) / 100
        
        net_disbursement = request.loan_amount - processing_fee
        
        return EMICalculationResponse(
            loan_amount=request.loan_amount,
            interest_rate=request.interest_rate,
            tenure_months=tenure,
            emi_amount=Decimal(str(round(emi, 2))),
            total_interest=Decimal(str(round(total_interest, 2))),
            total_repayment=Decimal(str(round(total_repayment, 2))),
            processing_fee=processing_fee if product else None,
            net_disbursement=net_disbursement if product else None
        )
    
    def generate_emi_schedule(
        self,
        loan_amount: Decimal,
        interest_rate: Decimal,
        tenure_months: int,
        start_date: datetime,
        interest_rate_type: InterestRateType = InterestRateType.REDUCING
    ) -> EMIScheduleResponse:
        """Generate complete EMI schedule"""
        
        # Calculate EMI
        emi_calc = self.calculate_emi(
            EMICalculationRequest(
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                tenure_months=tenure_months,
                interest_rate_type=interest_rate_type
            )
        )
        
        schedule = []
        principal = float(loan_amount)
        emi = float(emi_calc.emi_amount)
        monthly_rate = float(interest_rate) / (12 * 100)
        
        for month in range(1, tenure_months + 1):
            # Calculate due date (add month to start date)
            from dateutil.relativedelta import relativedelta
            due_date = start_date + relativedelta(months=month)
            
            if interest_rate_type == InterestRateType.FLAT:
                # Flat rate: equal principal, equal interest
                interest_component = (float(loan_amount) * float(interest_rate) * 1) / (12 * 100)
                principal_component = emi - interest_component
            
            else:  # Reducing balance
                # Interest on outstanding principal
                interest_component = principal * monthly_rate
                principal_component = emi - interest_component
            
            opening_principal = principal
            principal -= principal_component
            closing_principal = principal
            
            schedule.append(EMIScheduleRow(
                installment_number=month,
                due_date=due_date.date(),
                emi_amount=Decimal(str(round(emi, 2))),
                principal_component=Decimal(str(round(principal_component, 2))),
                interest_component=Decimal(str(round(interest_component, 2))),
                opening_principal=Decimal(str(round(opening_principal, 2))),
                closing_principal=Decimal(str(round(max(0, closing_principal), 2)))
            ))
        
        return EMIScheduleResponse(
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure_months=tenure_months,
            emi_amount=emi_calc.emi_amount,
            total_interest=emi_calc.total_interest,
            total_repayment=emi_calc.total_repayment,
            schedule=schedule
        )
    
    def check_eligibility(
        self,
        product: LoanProduct,
        customer_age: int,
        customer_income: Decimal,
        customer_cibil: int,
        requested_amount: Decimal
    ) -> tuple[bool, List[str]]:
        """Check customer eligibility for loan product"""
        
        errors = []
        
        # Age check
        if customer_age < product.min_age:
            errors.append(f"Age must be at least {product.min_age} years")
        if customer_age > product.max_age:
            errors.append(f"Age must not exceed {product.max_age} years")
        
        # Income check
        if product.min_monthly_income and customer_income < product.min_monthly_income:
            errors.append(
                f"Monthly income must be at least ₹{product.min_monthly_income:,.2f}"
            )
        
        # CIBIL check
        if customer_cibil < product.min_cibil_score:
            errors.append(
                f"CIBIL score must be at least {product.min_cibil_score}"
            )
        
        # Loan amount check
        if requested_amount < product.min_loan_amount:
            errors.append(
                f"Loan amount must be at least ₹{product.min_loan_amount:,.2f}"
            )
        if requested_amount > product.max_loan_amount:
            errors.append(
                f"Loan amount must not exceed ₹{product.max_loan_amount:,.2f}"
            )
        
        is_eligible = len(errors) == 0
        return is_eligible, errors
