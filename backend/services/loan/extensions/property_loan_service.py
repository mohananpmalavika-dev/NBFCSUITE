"""
Property Loan Extension Service
Business logic for property/mortgage loan operations (LAP/Home Loan)
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from backend.shared.database.property_loan_models import (
    PropertyLoanDetails, PropertyLegalVerification, PropertyTechnicalVerification,
    PropertyDocument, PropertyMortgage,
    PropertyType, PropertyOwnershipType, PropertyStatus,
    LegalVerificationStatus, TechnicalVerificationStatus, MortgageStatus
)
from backend.shared.database.loan_models import LoanApplication

logger = logging.getLogger(__name__)


class PropertyLoanService:
    """Service for property loan operations"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    # ============================================
    # Property Details Management
    # ============================================
    
    def create_property_details(
        self,
        loan_application_id: int,
        property_data: dict,
        user_id: str
    ) -> PropertyLoanDetails:
        """Create property details for loan application"""
        
        # Validate loan application exists
        loan_app = self.db.query(LoanApplication).filter(
            and_(
                LoanApplication.id == loan_application_id,
                LoanApplication.tenant_id == self.tenant_id
            )
        ).first()
        
        if not loan_app:
            raise ValueError("Loan application not found")
        
        # Check if property details already exist
        existing = self.db.query(PropertyLoanDetails).filter(
            and_(
                PropertyLoanDetails.loan_application_id == loan_application_id,
                PropertyLoanDetails.tenant_id == self.tenant_id
            )
        ).first()
        
        if existing:
            raise ValueError("Property details already exist for this loan application")
        
        # Create property details
        property_details = PropertyLoanDetails(
            tenant_id=self.tenant_id,
            loan_application_id=loan_application_id,
            created_by=user_id,
            updated_by=user_id,
            **property_data
        )
        
        self.db.add(property_details)
        self.db.commit()
        self.db.refresh(property_details)
        
        logger.info(f"Property details created for loan application {loan_application_id}")
        
        return property_details
    
    def get_property_details(self, loan_application_id: int) -> Optional[PropertyLoanDetails]:
        """Get property details by loan application ID"""
        return self.db.query(PropertyLoanDetails).filter(
            and_(
                PropertyLoanDetails.loan_application_id == loan_application_id,
                PropertyLoanDetails.tenant_id == self.tenant_id
            )
        ).first()
    
    def update_property_details(
        self,
        property_id: int,
        property_data: dict,
        user_id: str
    ) -> Optional[PropertyLoanDetails]:
        """Update property details"""
        
        property_loan = self.db.query(PropertyLoanDetails).filter(
            and_(
                PropertyLoanDetails.id == property_id,
                PropertyLoanDetails.tenant_id == self.tenant_id
            )
        ).first()
        
        if not property_loan:
            return None
        
        # Update fields
        for field, value in property_data.items():
            if hasattr(property_loan, field):
                setattr(property_loan, field, value)
        
        property_loan.updated_by = user_id
        property_loan.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(property_loan)
        
        logger.info(f"Property details updated for ID {property_id}")
        
        return property_loan
    
    def calculate_ltv(
        self,
        market_value: Decimal,
        loan_amount: Decimal
    ) -> Decimal:
        """Calculate Loan-to-Value ratio"""
        if market_value == 0:
            return Decimal("0")
        return (loan_amount / market_value) * 100
    
    # ============================================
    # Legal Verification Management
    # ============================================
    
    def create_legal_verification(
        self,
        property_loan_id: int,
        loan_application_id: int,
        legal_data: dict,
        user_id: str
    ) -> PropertyLegalVerification:
        """Initialize legal verification for property"""
        
        # Check if already exists
        existing = self.db.query(PropertyLegalVerification).filter(
            and_(
                PropertyLegalVerification.property_loan_id == property_loan_id,
                PropertyLegalVerification.tenant_id == self.tenant_id
            )
        ).first()
        
        if existing:
            raise ValueError("Legal verification already exists for this property loan")
        
        legal_verification = PropertyLegalVerification(
            tenant_id=self.tenant_id,
            property_loan_id=property_loan_id,
            loan_application_id=loan_application_id,
            created_by=user_id,
            updated_by=user_id,
            **legal_data
        )
        
        self.db.add(legal_verification)
        self.db.commit()
        self.db.refresh(legal_verification)
        
        logger.info(f"Legal verification created for property loan {property_loan_id}")
        
        return legal_verification
    
    def update_legal_verification(
        self,
        legal_id: int,
        updates: dict,
        user_id: str
    ) -> Optional[PropertyLegalVerification]:
        """Update legal verification details"""
        
        legal_verification = self.db.query(PropertyLegalVerification).filter(
            and_(
                PropertyLegalVerification.id == legal_id,
                PropertyLegalVerification.tenant_id == self.tenant_id
            )
        ).first()
        
        if not legal_verification:
            return None
        
        # Update fields
        for field, value in updates.items():
            if hasattr(legal_verification, field):
                setattr(legal_verification, field, value)
        
        legal_verification.updated_by = user_id
        legal_verification.updated_at = datetime.utcnow()
        
        # Auto-update property loan status if approval given
        if updates.get('approved'):
            property_loan = self.db.query(PropertyLoanDetails).filter(
                PropertyLoanDetails.id == legal_verification.property_loan_id
            ).first()
            if property_loan:
                property_loan.legal_verification_status = LegalVerificationStatus.CLEAR
                property_loan.has_clear_title = True
        
        self.db.commit()
        self.db.refresh(legal_verification)
        
        logger.info(f"Legal verification updated for ID {legal_id}")
        
        return legal_verification
    
    def get_pending_legal_verifications(self) -> List[PropertyLegalVerification]:
        """Get all pending legal verification cases"""
        return self.db.query(PropertyLegalVerification).filter(
            and_(
                PropertyLegalVerification.tenant_id == self.tenant_id,
                PropertyLegalVerification.legal_opinion_status.in_([
                    LegalVerificationStatus.PENDING,
                    LegalVerificationStatus.IN_PROGRESS
                ])
            )
        ).order_by(PropertyLegalVerification.created_at.asc()).all()
    
    # ============================================
    # Technical Verification Management
    # ============================================
    
    def create_technical_verification(
        self,
        property_loan_id: int,
        loan_application_id: int,
        technical_data: dict,
        user_id: str
    ) -> PropertyTechnicalVerification:
        """Initialize technical verification for property"""
        
        # Check if already exists
        existing = self.db.query(PropertyTechnicalVerification).filter(
            and_(
                PropertyTechnicalVerification.property_loan_id == property_loan_id,
                PropertyTechnicalVerification.tenant_id == self.tenant_id
            )
        ).first()
        
        if existing:
            raise ValueError("Technical verification already exists for this property loan")
        
        technical_verification = PropertyTechnicalVerification(
            tenant_id=self.tenant_id,
            property_loan_id=property_loan_id,
            loan_application_id=loan_application_id,
            created_by=user_id,
            updated_by=user_id,
            **technical_data
        )
        
        self.db.add(technical_verification)
        self.db.commit()
        self.db.refresh(technical_verification)
        
        logger.info(f"Technical verification created for property loan {property_loan_id}")
        
        return technical_verification
    
    def update_technical_verification(
        self,
        technical_id: int,
        updates: dict,
        user_id: str
    ) -> Optional[PropertyTechnicalVerification]:
        """Update technical verification details"""
        
        technical_verification = self.db.query(PropertyTechnicalVerification).filter(
            and_(
                PropertyTechnicalVerification.id == technical_id,
                PropertyTechnicalVerification.tenant_id == self.tenant_id
            )
        ).first()
        
        if not technical_verification:
            return None
        
        # Update fields
        for field, value in updates.items():
            if hasattr(technical_verification, field):
                setattr(technical_verification, field, value)
        
        technical_verification.updated_by = user_id
        technical_verification.updated_at = datetime.utcnow()
        
        # Auto-update property loan status if approval given
        if updates.get('approved'):
            property_loan = self.db.query(PropertyLoanDetails).filter(
                PropertyLoanDetails.id == technical_verification.property_loan_id
            ).first()
            if property_loan:
                property_loan.technical_verification_status = TechnicalVerificationStatus.COMPLETED
                # Update bank valuation
                if updates.get('market_value_assessed'):
                    property_loan.bank_valuation = updates['market_value_assessed']
        
        self.db.commit()
        self.db.refresh(technical_verification)
        
        logger.info(f"Technical verification updated for ID {technical_id}")
        
        return technical_verification
    
    def schedule_site_visit(
        self,
        technical_id: int,
        inspection_date: date,
        engineer_name: str,
        user_id: str
    ) -> Optional[PropertyTechnicalVerification]:
        """Schedule site visit for technical verification"""
        
        technical_verification = self.db.query(PropertyTechnicalVerification).filter(
            and_(
                PropertyTechnicalVerification.id == technical_id,
                PropertyTechnicalVerification.tenant_id == self.tenant_id
            )
        ).first()
        
        if not technical_verification:
            return None
        
        technical_verification.status = TechnicalVerificationStatus.SCHEDULED
        technical_verification.inspection_date = inspection_date
        technical_verification.engineer_name = engineer_name
        technical_verification.updated_by = user_id
        technical_verification.updated_at = datetime.utcnow()
        
        # Update property loan status
        property_loan = self.db.query(PropertyLoanDetails).filter(
            PropertyLoanDetails.id == technical_verification.property_loan_id
        ).first()
        if property_loan:
            property_loan.technical_verification_status = TechnicalVerificationStatus.SCHEDULED
        
        self.db.commit()
        self.db.refresh(technical_verification)
        
        logger.info(f"Site visit scheduled for technical verification {technical_id} on {inspection_date}")
        
        return technical_verification
    
    def get_pending_technical_verifications(self) -> List[PropertyTechnicalVerification]:
        """Get all pending technical verification cases"""
        return self.db.query(PropertyTechnicalVerification).filter(
            and_(
                PropertyTechnicalVerification.tenant_id == self.tenant_id,
                PropertyTechnicalVerification.status.in_([
                    TechnicalVerificationStatus.PENDING,
                    TechnicalVerificationStatus.SCHEDULED,
                    TechnicalVerificationStatus.IN_PROGRESS
                ])
            )
        ).order_by(PropertyTechnicalVerification.created_at.asc()).all()
    
    # ============================================
    # Document Management
    # ============================================
    
    def upload_property_document(
        self,
        property_loan_id: int,
        loan_application_id: int,
        document_data: dict,
        user_id: str
    ) -> PropertyDocument:
        """Upload property document"""
        
        document = PropertyDocument(
            tenant_id=self.tenant_id,
            property_loan_id=property_loan_id,
            loan_application_id=loan_application_id,
            uploaded_by=user_id,
            **document_data
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"Document uploaded: {document.document_type} for property loan {property_loan_id}")
        
        return document
    
    def verify_document(
        self,
        document_id: int,
        verified: bool,
        remarks: str,
        user_id: str
    ) -> Optional[PropertyDocument]:
        """Verify property document"""
        
        document = self.db.query(PropertyDocument).filter(
            and_(
                PropertyDocument.id == document_id,
                PropertyDocument.tenant_id == self.tenant_id,
                PropertyDocument.is_deleted == False
            )
        ).first()
        
        if not document:
            return None
        
        document.is_verified = verified
        document.verified_by = user_id
        document.verified_date = date.today()
        document.verification_remarks = remarks
        document.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(document)
        
        logger.info(f"Document {document_id} verification status: {verified}")
        
        return document
    
    def get_property_documents(
        self,
        property_loan_id: int,
        document_type: Optional[str] = None
    ) -> List[PropertyDocument]:
        """Get property documents"""
        
        query = self.db.query(PropertyDocument).filter(
            and_(
                PropertyDocument.property_loan_id == property_loan_id,
                PropertyDocument.tenant_id == self.tenant_id,
                PropertyDocument.is_deleted == False
            )
        )
        
        if document_type:
            query = query.filter(PropertyDocument.document_type == document_type)
        
        return query.order_by(PropertyDocument.created_at.desc()).all()
    
    def check_mandatory_documents(self, property_loan_id: int) -> dict:
        """Check if all mandatory documents are uploaded and verified"""
        
        mandatory_docs = [
            "sale_deed",
            "ec",  # Encumbrance Certificate
            "property_card",
            "tax_receipt",
            "building_plan"
        ]
        
        documents = self.get_property_documents(property_loan_id)
        doc_types = {doc.document_type for doc in documents if doc.is_verified}
        
        missing_docs = [doc for doc in mandatory_docs if doc not in doc_types]
        
        return {
            "all_uploaded": len(missing_docs) == 0,
            "missing_documents": missing_docs,
            "uploaded_count": len(doc_types),
            "required_count": len(mandatory_docs)
        }
    
    # ============================================
    # Mortgage Management
    # ============================================
    
    def create_mortgage(
        self,
        property_loan_id: int,
        loan_application_id: int,
        mortgage_data: dict,
        user_id: str
    ) -> PropertyMortgage:
        """Create mortgage entry for property"""
        
        # Check if already exists
        existing = self.db.query(PropertyMortgage).filter(
            and_(
                PropertyMortgage.property_loan_id == property_loan_id,
                PropertyMortgage.tenant_id == self.tenant_id
            )
        ).first()
        
        if existing:
            raise ValueError("Mortgage already exists for this property loan")
        
        mortgage = PropertyMortgage(
            tenant_id=self.tenant_id,
            property_loan_id=property_loan_id,
            loan_application_id=loan_application_id,
            created_by=user_id,
            updated_by=user_id,
            **mortgage_data
        )
        
        self.db.add(mortgage)
        self.db.commit()
        self.db.refresh(mortgage)
        
        logger.info(f"Mortgage created for property loan {property_loan_id}")
        
        return mortgage
    
    def update_mortgage_status(
        self,
        mortgage_id: int,
        status: MortgageStatus,
        updates: dict,
        user_id: str
    ) -> Optional[PropertyMortgage]:
        """Update mortgage status"""
        
        mortgage = self.db.query(PropertyMortgage).filter(
            and_(
                PropertyMortgage.id == mortgage_id,
                PropertyMortgage.tenant_id == self.tenant_id
            )
        ).first()
        
        if not mortgage:
            return None
        
        # Update status
        mortgage.mortgage_status = status
        
        # Update related fields based on status
        if status == MortgageStatus.DOCUMENTS_SUBMITTED:
            mortgage.original_documents_submitted = True
            mortgage.documents_submission_date = updates.get('submission_date', date.today())
        
        elif status == MortgageStatus.REGISTERED:
            mortgage.registration_date = updates.get('registration_date', date.today())
            mortgage.lien_marked = True
            mortgage.lien_marked_date = date.today()
            
            # Update property loan status
            property_loan = self.db.query(PropertyLoanDetails).filter(
                PropertyLoanDetails.id == mortgage.property_loan_id
            ).first()
            if property_loan:
                property_loan.mortgage_status = MortgageStatus.REGISTERED
        
        elif status == MortgageStatus.DISCHARGED:
            mortgage.discharge_registered = True
            mortgage.discharge_registration_date = updates.get('discharge_date', date.today())
            
            # Update property loan status
            property_loan = self.db.query(PropertyLoanDetails).filter(
                PropertyLoanDetails.id == mortgage.property_loan_id
            ).first()
            if property_loan:
                property_loan.mortgage_status = MortgageStatus.DISCHARGED
        
        # Update additional fields
        for field, value in updates.items():
            if hasattr(mortgage, field):
                setattr(mortgage, field, value)
        
        mortgage.updated_by = user_id
        mortgage.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(mortgage)
        
        logger.info(f"Mortgage status updated to {status} for mortgage {mortgage_id}")
        
        return mortgage
    
    def initiate_discharge(
        self,
        mortgage_id: int,
        loan_closed_date: date,
        user_id: str
    ) -> Optional[PropertyMortgage]:
        """Initiate mortgage discharge process"""
        
        mortgage = self.db.query(PropertyMortgage).filter(
            and_(
                PropertyMortgage.id == mortgage_id,
                PropertyMortgage.tenant_id == self.tenant_id
            )
        ).first()
        
        if not mortgage:
            return None
        
        if mortgage.mortgage_status != MortgageStatus.REGISTERED:
            raise ValueError("Mortgage must be registered before discharge can be initiated")
        
        mortgage.loan_closed_date = loan_closed_date
        mortgage.discharge_initiated = True
        mortgage.discharge_initiated_date = date.today()
        mortgage.updated_by = user_id
        mortgage.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(mortgage)
        
        logger.info(f"Discharge initiated for mortgage {mortgage_id}")
        
        return mortgage
    
    def get_pending_mortgages(self) -> List[PropertyMortgage]:
        """Get pending mortgage registrations"""
        return self.db.query(PropertyMortgage).filter(
            and_(
                PropertyMortgage.tenant_id == self.tenant_id,
                PropertyMortgage.mortgage_status.in_([
                    MortgageStatus.PENDING,
                    MortgageStatus.DOCUMENTS_SUBMITTED
                ])
            )
        ).order_by(PropertyMortgage.created_at.asc()).all()
    
    def get_discharge_pending_cases(self) -> List[PropertyMortgage]:
        """Get cases where loan is closed but discharge pending"""
        return self.db.query(PropertyMortgage).filter(
            and_(
                PropertyMortgage.tenant_id == self.tenant_id,
                PropertyMortgage.loan_closed_date.isnot(None),
                PropertyMortgage.discharge_registered == False,
                PropertyMortgage.mortgage_status == MortgageStatus.REGISTERED
            )
        ).all()
    
    # ============================================
    # Reporting & Analytics
    # ============================================
    
    def get_property_loan_summary(self, loan_application_id: int) -> dict:
        """Get complete summary of property loan"""
        
        property_loan = self.get_property_details(loan_application_id)
        if not property_loan:
            return {}
        
        legal_verification = self.db.query(PropertyLegalVerification).filter(
            PropertyLegalVerification.property_loan_id == property_loan.id
        ).first()
        
        technical_verification = self.db.query(PropertyTechnicalVerification).filter(
            PropertyTechnicalVerification.property_loan_id == property_loan.id
        ).first()
        
        mortgage = self.db.query(PropertyMortgage).filter(
            PropertyMortgage.property_loan_id == property_loan.id
        ).first()
        
        documents = self.get_property_documents(property_loan.id)
        doc_status = self.check_mandatory_documents(property_loan.id)
        
        return {
            "property_details": property_loan,
            "legal_verification": legal_verification,
            "technical_verification": technical_verification,
            "mortgage": mortgage,
            "documents": documents,
            "document_compliance": doc_status,
            "verification_status": self._get_verification_status(property_loan, legal_verification, technical_verification),
            "is_ready_for_disbursement": self._check_disbursement_readiness(
                property_loan, legal_verification, technical_verification, mortgage, doc_status
            )
        }
    
    def _get_verification_status(
        self,
        property_loan: PropertyLoanDetails,
        legal: Optional[PropertyLegalVerification],
        technical: Optional[PropertyTechnicalVerification]
    ) -> dict:
        """Get verification status summary"""
        
        return {
            "legal_status": legal.legal_opinion_status if legal else LegalVerificationStatus.PENDING,
            "legal_approved": legal.approved if legal else False,
            "technical_status": technical.status if technical else TechnicalVerificationStatus.PENDING,
            "technical_approved": technical.approved if technical else False,
            "both_approved": (legal and legal.approved) and (technical and technical.approved)
        }
    
    def _check_disbursement_readiness(
        self,
        property_loan: PropertyLoanDetails,
        legal: Optional[PropertyLegalVerification],
        technical: Optional[PropertyTechnicalVerification],
        mortgage: Optional[PropertyMortgage],
        doc_status: dict
    ) -> dict:
        """Check if property loan is ready for disbursement"""
        
        issues = []
        
        # Check legal verification
        if not legal or not legal.approved:
            issues.append("Legal verification not approved")
        
        # Check technical verification
        if not technical or not technical.approved:
            issues.append("Technical verification not approved")
        
        # Check documents
        if not doc_status['all_uploaded']:
            issues.append(f"Missing documents: {', '.join(doc_status['missing_documents'])}")
        
        # Check mortgage (optional, can be done post-disbursement)
        # if not mortgage or mortgage.mortgage_status != MortgageStatus.REGISTERED:
        #     issues.append("Mortgage not registered")
        
        return {
            "is_ready": len(issues) == 0,
            "issues": issues
        }
    
    def get_property_statistics(self) -> dict:
        """Get property loan statistics"""
        
        total_properties = self.db.query(PropertyLoanDetails).filter(
            PropertyLoanDetails.tenant_id == self.tenant_id
        ).count()
        
        pending_legal = self.db.query(PropertyLegalVerification).filter(
            and_(
                PropertyLegalVerification.tenant_id == self.tenant_id,
                PropertyLegalVerification.approved == False
            )
        ).count()
        
        pending_technical = self.db.query(PropertyTechnicalVerification).filter(
            and_(
                PropertyTechnicalVerification.tenant_id == self.tenant_id,
                PropertyTechnicalVerification.approved == False
            )
        ).count()
        
        pending_mortgages = len(self.get_pending_mortgages())
        pending_discharges = len(self.get_discharge_pending_cases())
        
        return {
            "total_property_loans": total_properties,
            "pending_legal_verifications": pending_legal,
            "pending_technical_verifications": pending_technical,
            "pending_mortgage_registrations": pending_mortgages,
            "pending_discharges": pending_discharges
        }
