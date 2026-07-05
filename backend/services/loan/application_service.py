"""
Loan Application Service
Manages loan application lifecycle
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
import math

from backend.shared.database.loan_models import (
    LoanApplication, LoanApplicationCoApplicant, LoanApplicationDocument,
    LoanProduct
)
from backend.shared.database.customer_models import Customer, CustomerFamily
from .schemas import (
    LoanApplicationCreate, LoanApplicationUpdate, LoanApplicationResponse,
    LoanApplicationListResponse, LoanApplicationStats, ApplicationStatus,
    RiskRating, EMICalculationRequest
)
from .product_service import LoanProductService


class LoanApplicationService:
    """Service for loan application operations"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.product_service = LoanProductService(db, tenant_id)
    
    def generate_application_number(self) -> str:
        """Generate unique application number: APP-YYYYMM-XXXX"""
        now = datetime.utcnow()
        prefix = f"APP-{now.strftime('%Y%m')}"
        
        # Get last application number for this month
        last_app = self.db.query(LoanApplication).filter(
            and_(
                LoanApplication.tenant_id == self.tenant_id,
                LoanApplication.application_number.like(f"{prefix}%")
            )
        ).order_by(LoanApplication.id.desc()).first()
        
        if last_app:
            last_number = int(last_app.application_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    def create_application(
        self,
        data: LoanApplicationCreate,
        user_id: int
    ) -> LoanApplication:
        """Create new loan application"""
        
        # Validate customer exists
        customer = self.db.query(Customer).filter(
            and_(
                Customer.id == data.customer_id,
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False
            )
        ).first()
        
        if not customer:
            raise ValueError("Customer not found")
        
        # Validate product exists and is active
        product = self.product_service.get_product(data.loan_product_id)
        if not product or not product.is_active:
            raise ValueError("Loan product not found or inactive")
        
        # Check eligibility
        customer_age = customer.age or 0
        customer_income = customer.monthly_income or Decimal("0")
        customer_cibil = customer.cibil_score or 0
        
        is_eligible, errors = self.product_service.check_eligibility(
            product=product,
            customer_age=customer_age,
            customer_income=customer_income,
            customer_cibil=customer_cibil,
            requested_amount=data.requested_amount
        )
        
        if not is_eligible:
            raise ValueError(f"Customer not eligible: {', '.join(errors)}")
        
        # Validate tenure
        if data.tenure_months < product.min_tenure_months or \
           data.tenure_months > product.max_tenure_months:
            raise ValueError(
                f"Tenure must be between {product.min_tenure_months} "
                f"and {product.max_tenure_months} months"
            )
        
        # Calculate EMI
        emi_calc = self.product_service.calculate_emi(
            EMICalculationRequest(
                loan_amount=data.requested_amount,
                interest_rate=product.default_interest_rate,
                tenure_months=data.tenure_months,
                interest_rate_type=product.interest_rate_type
            ),
            product=product
        )
        
        # Calculate fees and deductions
        processing_fee = emi_calc.processing_fee or Decimal("0")
        documentation_charges = product.documentation_charges or Decimal("0")
        insurance_amount = Decimal("0")
        
        if product.insurance_applicable and product.insurance_percentage:
            insurance_amount = (data.requested_amount * product.insurance_percentage) / 100
        
        total_deductions = processing_fee + documentation_charges + insurance_amount
        net_disbursement = data.requested_amount - total_deductions
        
        # Create application
        application = LoanApplication(
            tenant_id=self.tenant_id,
            application_number=self.generate_application_number(),
            customer_id=data.customer_id,
            loan_product_id=data.loan_product_id,
            requested_amount=data.requested_amount,
            tenure_months=data.tenure_months,
            interest_rate=product.default_interest_rate,
            emi_amount=emi_calc.emi_amount,
            total_interest=emi_calc.total_interest,
            total_repayment=emi_calc.total_repayment,
            loan_purpose_id=data.loan_purpose_id,
            purpose_description=data.purpose_description,
            disbursement_bank_account_id=data.disbursement_bank_account_id,
            disbursement_mode=data.disbursement_mode.value if data.disbursement_mode else None,
            applicant_remarks=data.applicant_remarks,
            status=ApplicationStatus.DRAFT.value,
            application_date=date.today(),
            processing_fee=processing_fee,
            documentation_charges=documentation_charges,
            insurance_amount=insurance_amount,
            total_deductions=total_deductions,
            net_disbursement=net_disbursement,
            monthly_income=customer_income,
            credit_score=customer_cibil,
            risk_rating=customer.risk_rating.value if customer.risk_rating else None,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(application)
        self.db.flush()  # Get application ID
        
        # Add co-applicants
        if data.co_applicants:
            for co_app_data in data.co_applicants:
                # Validate family member exists
                family_member = self.db.query(CustomerFamilyMember).filter(
                    and_(
                        CustomerFamilyMember.id == co_app_data.family_member_id,
                        CustomerFamilyMember.customer_id == data.customer_id,
                        CustomerFamilyMember.is_deleted == False
                    )
                ).first()
                
                if not family_member:
                    raise ValueError(f"Family member {co_app_data.family_member_id} not found")
                
                co_applicant = LoanApplicationCoApplicant(
                    tenant_id=self.tenant_id,
                    loan_application_id=application.id,
                    family_member_id=co_app_data.family_member_id,
                    co_applicant_type=co_app_data.co_applicant_type,
                    is_primary=co_app_data.is_primary,
                    relationship=family_member.relationship_name,
                    monthly_income=co_app_data.monthly_income,
                    occupation=co_app_data.occupation,
                    consent_given=co_app_data.consent_given,
                    consent_date=co_app_data.consent_date
                )
                self.db.add(co_applicant)
        
        # Add documents
        if data.documents:
            for doc_data in data.documents:
                document = LoanApplicationDocument(
                    tenant_id=self.tenant_id,
                    loan_application_id=application.id,
                    document_type_id=doc_data.document_type_id,
                    customer_document_id=doc_data.customer_document_id,
                    document_number=doc_data.document_number,
                    file_path=doc_data.file_path,
                    file_url=doc_data.file_url,
                    remarks=doc_data.remarks
                )
                self.db.add(document)
        
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    def get_application(self, application_id: int) -> Optional[LoanApplication]:
        """Get application by ID with related data"""
        return self.db.query(LoanApplication).options(
            joinedload(LoanApplication.customer),
            joinedload(LoanApplication.loan_product),
            joinedload(LoanApplication.co_applicants),
            joinedload(LoanApplication.documents)
        ).filter(
            and_(
                LoanApplication.id == application_id,
                LoanApplication.tenant_id == self.tenant_id,
                LoanApplication.is_deleted == False
            )
        ).first()
    
    def get_application_by_number(self, application_number: str) -> Optional[LoanApplication]:
        """Get application by application number"""
        return self.db.query(LoanApplication).options(
            joinedload(LoanApplication.customer),
            joinedload(LoanApplication.loan_product),
            joinedload(LoanApplication.co_applicants),
            joinedload(LoanApplication.documents)
        ).filter(
            and_(
                LoanApplication.application_number == application_number,
                LoanApplication.tenant_id == self.tenant_id,
                LoanApplication.is_deleted == False
            )
        ).first()
    
    def list_applications(
        self,
        page: int = 1,
        page_size: int = 50,
        customer_id: Optional[int] = None,
        product_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> LoanApplicationListResponse:
        """List applications with filters"""
        
        query = self.db.query(LoanApplication).options(
            joinedload(LoanApplication.customer),
            joinedload(LoanApplication.loan_product)
        ).filter(
            and_(
                LoanApplication.tenant_id == self.tenant_id,
                LoanApplication.is_deleted == False
            )
        )
        
        # Apply filters
        if customer_id:
            query = query.filter(LoanApplication.customer_id == customer_id)
        
        if product_id:
            query = query.filter(LoanApplication.loan_product_id == product_id)
        
        if status:
            query = query.filter(LoanApplication.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.join(Customer).filter(
                or_(
                    LoanApplication.application_number.ilike(search_term),
                    Customer.full_name.ilike(search_term),
                    Customer.customer_code.ilike(search_term),
                    Customer.mobile.ilike(search_term)
                )
            )
        
        if from_date:
            query = query.filter(LoanApplication.application_date >= from_date)
        
        if to_date:
            query = query.filter(LoanApplication.application_date <= to_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and sorting
        query = query.order_by(LoanApplication.application_date.desc())
        applications = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # Build response with enriched data
        items = []
        for app in applications:
            app_dict = LoanApplicationResponse.model_validate(app).model_dump()
            
            # Add customer details
            if app.customer:
                app_dict['customer_name'] = app.customer.full_name
                app_dict['customer_code'] = app.customer.customer_code
                app_dict['customer_mobile'] = app.customer.mobile
                app_dict['customer_cibil_score'] = app.customer.cibil_score
            
            # Add product details
            if app.loan_product:
                app_dict['product_name'] = app.loan_product.product_name
                app_dict['product_type'] = app.loan_product.product_type
            
            items.append(LoanApplicationResponse(**app_dict))
        
        return LoanApplicationListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total > 0 else 0
        )
    
    def update_application(
        self,
        application_id: int,
        data: LoanApplicationUpdate,
        user_id: int
    ) -> Optional[LoanApplication]:
        """Update loan application"""
        
        application = self.get_application(application_id)
        if not application:
            return None
        
        # Can only update if status is draft or submitted
        if application.status not in [ApplicationStatus.DRAFT.value, 
                                     ApplicationStatus.SUBMITTED.value]:
            raise ValueError(
                f"Cannot update application in {application.status} status"
            )
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        
        # Recalculate EMI if amount or tenure changed
        if 'requested_amount' in update_data or 'tenure_months' in update_data:
            product = application.loan_product
            
            new_amount = update_data.get('requested_amount', application.requested_amount)
            new_tenure = update_data.get('tenure_months', application.tenure_months)
            
            emi_calc = self.product_service.calculate_emi(
                EMICalculationRequest(
                    loan_amount=new_amount,
                    interest_rate=application.interest_rate,
                    tenure_months=new_tenure,
                    interest_rate_type=product.interest_rate_type
                ),
                product=product
            )
            
            update_data['emi_amount'] = emi_calc.emi_amount
            update_data['total_interest'] = emi_calc.total_interest
            update_data['total_repayment'] = emi_calc.total_repayment
        
        for field, value in update_data.items():
            setattr(application, field, value)
        
        application.updated_by = user_id
        application.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    def submit_application(
        self,
        application_id: int,
        user_id: int
    ) -> Optional[LoanApplication]:
        """Submit application for review"""
        
        application = self.get_application(application_id)
        if not application:
            return None
        
        if application.status != ApplicationStatus.DRAFT.value:
            raise ValueError("Only draft applications can be submitted")
        
        # Validate required fields
        if not application.disbursement_bank_account_id:
            raise ValueError("Disbursement bank account is required")
        
        # Update status
        application.status = ApplicationStatus.SUBMITTED.value
        application.submission_date = date.today()
        application.updated_by = user_id
        application.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    def get_stats(self) -> LoanApplicationStats:
        """Get application statistics"""
        
        query = self.db.query(LoanApplication).filter(
            and_(
                LoanApplication.tenant_id == self.tenant_id,
                LoanApplication.is_deleted == False
            )
        )
        
        total = query.count()
        
        # Status counts
        draft = query.filter(LoanApplication.status == ApplicationStatus.DRAFT.value).count()
        submitted = query.filter(LoanApplication.status == ApplicationStatus.SUBMITTED.value).count()
        under_review = query.filter(LoanApplication.status == ApplicationStatus.UNDER_REVIEW.value).count()
        pending_approval = query.filter(LoanApplication.status == ApplicationStatus.PENDING_APPROVAL.value).count()
        approved = query.filter(LoanApplication.status == ApplicationStatus.APPROVED.value).count()
        rejected = query.filter(LoanApplication.status == ApplicationStatus.REJECTED.value).count()
        disbursed = query.filter(LoanApplication.status == ApplicationStatus.DISBURSED.value).count()
        
        # Amount aggregations
        total_requested = query.with_entities(
            func.sum(LoanApplication.requested_amount)
        ).scalar() or Decimal("0")
        
        total_approved_amount = query.filter(
            LoanApplication.status.in_([
                ApplicationStatus.APPROVED.value,
                ApplicationStatus.DISBURSED.value
            ])
        ).with_entities(
            func.sum(LoanApplication.approved_amount)
        ).scalar() or Decimal("0")
        
        avg_amount = query.with_entities(
            func.avg(LoanApplication.requested_amount)
        ).scalar() or Decimal("0")
        
        # Calculate approval rate
        total_processed = approved + rejected + disbursed
        approval_rate = (approved + disbursed) / total_processed * 100 if total_processed > 0 else 0
        
        return LoanApplicationStats(
            total_applications=total,
            draft=draft,
            submitted=submitted,
            under_review=under_review,
            pending_approval=pending_approval,
            approved=approved,
            rejected=rejected,
            disbursed=disbursed,
            total_requested_amount=total_requested,
            total_approved_amount=total_approved_amount,
            average_loan_amount=avg_amount,
            approval_rate=round(approval_rate, 2)
        )
