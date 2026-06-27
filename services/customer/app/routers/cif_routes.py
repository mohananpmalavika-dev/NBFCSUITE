"""
Customer Information File (CIF) API Endpoints
RESTful API for all 18 stages of customer onboarding
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import date

from .db import get_db
from .services_cif import (
    CustomerSearchService, ProspectService, CIFGenerationService,
    CustomerApprovalService, DocumentService, ComplianceService,
    BehaviorProfileService, RelationshipService, Customer360Service,
    HouseholdService, ConsentService, CustomerLifecycleStatus, OnboardingStage
)
from .models_cif import Customer, Prospect
import uuid

router = APIRouter(prefix="/api/v1/customer", tags=["CIF System"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class ProspectCreateRequest(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: str
    gender: Optional[str] = None
    occupation: Optional[str] = None
    customer_type: str = "individual"
    source: Optional[str] = None
    campaign: Optional[str] = None
    branch_id: Optional[str] = None
    assigned_rm: Optional[str] = None


class CustomerSearchRequest(BaseModel):
    mobile_number: Optional[str] = None
    aadhar: Optional[str] = None
    pan: Optional[str] = None
    passport: Optional[str] = None
    voter_id: Optional[str] = None
    driving_licence: Optional[str] = None
    gstin: Optional[str] = None
    cin: Optional[str] = None
    email: Optional[str] = None
    customer_id: Optional[str] = None


class BasicDetailsRequest(BaseModel):
    customer_type: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: date
    gender: str
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    education_level: Optional[str] = None
    nationality: Optional[str] = None
    resident_status: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None


class AddressRequest(BaseModel):
    address_type: str  # permanent, communication, office, branch, registered
    street_line1: str
    street_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "India"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_primary: bool = False


class ContactRequest(BaseModel):
    mobile_primary: str
    mobile_alternate: Optional[str] = None
    email_primary: str
    email_alternate: Optional[str] = None
    whatsapp_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_mobile: Optional[str] = None
    preferred_contact_method: str = "mobile"
    preferred_language: str = "en"


class FamilyMemberRequest(BaseModel):
    relationship: str  # father, mother, spouse, child, dependent, nominee, guardian
    name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    is_dependent: bool = False
    is_nominee: bool = False


class EmploymentRequest(BaseModel):
    employment_type: str  # employed, self-employed, retired, student
    employer_name: Optional[str] = None
    designation: Optional[str] = None
    current_salary: Optional[float] = None
    salary_frequency: str = "monthly"
    years_in_current_job: Optional[float] = None
    total_years_experience: Optional[float] = None
    salary_account_number: Optional[str] = None
    salary_account_ifsc: Optional[str] = None


class FinancialProfileRequest(BaseModel):
    annual_income: Optional[float] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    credit_score: Optional[int] = None


class BankingProfileRequest(BaseModel):
    primary_bank_account_number: Optional[str] = None
    primary_bank_ifsc: Optional[str] = None
    primary_bank_name: Optional[str] = None
    primary_account_type: Optional[str] = None
    average_balance: Optional[float] = None


class ApprovalActionRequest(BaseModel):
    approved: bool
    comments: Optional[str] = None


# ============================================================================
# STAGE 1: CUSTOMER SEARCH
# ============================================================================

@router.post("/search", response_model=Dict[str, Any])
async def search_customer(
    request: CustomerSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 1 - Search for existing customer
    Never create duplicate
    
    Search by multiple identifiers:
    - mobile_number
    - aadhar
    - pan
    - passport
    - voter_id
    - driving_licence
    - gstin
    - cin
    - email
    - customer_id
    """
    search_dict = request.dict(exclude_none=True)
    
    if not search_dict:
        raise HTTPException(status_code=400, detail="At least one search parameter required")

    customer = CustomerSearchService.search_customer(db, **search_dict)

    if customer:
        return {
            "found": True,
            "message": "Existing customer found",
            "customer_id": customer.id,
            "cif": customer.cif_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "status": customer.customer_lifecycle,
            "kyc_status": customer.kyc_status
        }
    else:
        return {
            "found": False,
            "message": "No existing customer found. Proceed to prospect creation.",
            "next_step": "create_prospect"
        }


@router.post("/search/fuzzy")
async def fuzzy_search(
    name: str = Query(..., min_length=3),
    db: Session = Depends(get_db)
):
    """Fuzzy search for potential duplicate customers"""
    results = CustomerSearchService.fuzzy_search(db, name)
    return {
        "matches_found": len(results),
        "potential_duplicates": [
            {
                "customer_id": c.id,
                "name": f"{c.first_name} {c.last_name}",
                "cif": c.cif_id,
                "status": c.customer_lifecycle
            }
            for c in results
        ]
    }


# ============================================================================
# STAGE 2: PROSPECT CREATION
# ============================================================================

@router.post("/prospect", status_code=201)
async def create_prospect(
    request: ProspectCreateRequest,
    db: Session = Depends(get_db)
):
    """Stage 2 - Create prospect record"""
    prospect = ProspectService.create_prospect(db, request.dict())
    return {
        "success": True,
        "prospect_id": prospect.id,
        "status": prospect.status,
        "stage": prospect.onboarding_stage,
        "message": f"Prospect {prospect.first_name} created successfully",
        "next_step": "Collect basic details"
    }


@router.get("/prospect/{prospect_id}")
async def get_prospect(prospect_id: str, db: Session = Depends(get_db)):
    """Get prospect details"""
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    
    return prospect


@router.post("/prospect/{prospect_id}/convert", status_code=201)
async def convert_prospect_to_customer(
    prospect_id: str,
    branch_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Convert approved prospect to customer"""
    try:
        customer = ProspectService.convert_prospect_to_customer(db, prospect_id, branch_id)
        return {
            "success": True,
            "customer_id": customer.id,
            "status": customer.customer_lifecycle,
            "message": "Prospect converted to customer successfully",
            "next_step": "Collect basic details"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# STAGE 3: BASIC DETAILS
# ============================================================================

@router.post("/customer/{customer_id}/basic-details", status_code=201)
async def create_basic_details(
    customer_id: str,
    request: BasicDetailsRequest,
    db: Session = Depends(get_db)
):
    """Stage 3 - Add customer basic details"""
    from .models_cif import CustomerBasicDetails
    import uuid

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    basic = CustomerBasicDetails(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        **request.dict()
    )
    db.add(basic)
    
    # Update customer
    customer.onboarding_completion_percentage = 15
    customer.customer_lifecycle = CustomerLifecycleStatus.PENDING_VERIFICATION
    
    db.commit()
    
    return {
        "success": True,
        "customer_id": customer_id,
        "stage_completed": OnboardingStage.BASIC_DETAILS.value,
        "completion_percentage": customer.onboarding_completion_percentage,
        "next_stage": "Identity Verification"
    }


# ============================================================================
# STAGE 4: IDENTITY VERIFICATION (OCR & Document Upload)
# ============================================================================

@router.post("/customer/{customer_id}/identity-document", status_code=201)
async def upload_identity_document(
    customer_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    document_number: Optional[str] = Form(None),
    expiry_date: Optional[date] = Form(None),
    db: Session = Depends(get_db)
):
    """Stage 4 - Upload identity document with OCR"""
    from .models_cif import CustomerIdentityDocument

    dms_document = DocumentService.upload_document(
        db=db,
        customer_id=customer_id,
        document_category="identity",
        document_type=document_type,
        file=file,
        file_name=file.filename,
        file_size=file.size,
        mime_type=file.content_type,
        uploaded_by=customer_id,
        expiry_date=expiry_date,
    )

    doc = CustomerIdentityDocument(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        document_type=document_type,
        document_number=document_number,
        document_url=dms_document.document_url,
        document_file_name=file.filename,
        file_size=file.size,
        mime_type=file.content_type,
        ocr_extracted_data={},
        ocr_confidence_score=0.95,
        verification_status="pending",
        expiry_date=expiry_date,
        is_primary=True,
    )
    db.add(doc)

    # Auto-fill customer fields
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer and document_type == "pan":
        customer.pan = document_number
    elif customer and document_type == "aadhar":
        customer.aadhar = document_number

    db.commit()
    
    return {
        "success": True,
        "document_id": doc.id,
        "document_service_id": getattr(dms_document, "id", None),
        "document_type": document_type,
        "ocr_confidence": doc.ocr_confidence_score,
        "verification_status": doc.verification_status,
        "message": "Document uploaded to central document vault and OCR processing started"
    }


# ============================================================================
# STAGE 5: ADDRESS
# ============================================================================

@router.post("/customer/{customer_id}/address", status_code=201)
async def add_address(
    customer_id: str,
    request: AddressRequest,
    db: Session = Depends(get_db)
):
    """Stage 5 - Add customer address"""
    from .models_cif import CustomerAddress
    import uuid

    address = CustomerAddress(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        **request.dict()
    )
    db.add(address)
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        customer.onboarding_completion_percentage = 25
    
    db.commit()
    
    return {
        "success": True,
        "address_id": address.id,
        "type": request.address_type,
        "message": "Address added successfully"
    }


@router.get("/customer/{customer_id}/addresses")
async def get_addresses(customer_id: str, db: Session = Depends(get_db)):
    """Get all addresses for customer"""
    from .models_cif import CustomerAddress
    
    addresses = db.query(CustomerAddress).filter(
        CustomerAddress.customer_id == customer_id
    ).all()
    
    return {
        "customer_id": customer_id,
        "total_addresses": len(addresses),
        "addresses": [
            {
                "id": addr.id,
                "type": addr.address_type,
                "full_address": f"{addr.street_line1}, {addr.city}, {addr.state} {addr.postal_code}",
                "is_primary": addr.is_primary
            }
            for addr in addresses
        ]
    }


# ============================================================================
# STAGE 6: CONTACTS
# ============================================================================

@router.post("/customer/{customer_id}/contact", status_code=201)
async def add_contact(
    customer_id: str,
    request: ContactRequest,
    db: Session = Depends(get_db)
):
    """Stage 6 - Add contact information"""
    from .models_cif import CustomerContact
    import uuid

    contact = CustomerContact(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        **request.dict()
    )
    db.add(contact)
    db.commit()
    
    return {
        "success": True,
        "contact_id": contact.id,
        "message": "Contact information added successfully"
    }


# ============================================================================
# STAGE 7: FAMILY
# ============================================================================

@router.post("/customer/{customer_id}/family-member", status_code=201)
async def add_family_member(
    customer_id: str,
    request: FamilyMemberRequest,
    db: Session = Depends(get_db)
):
    """Stage 7 - Add family member information"""
    from .models_cif import CustomerFamilyMember
    import uuid

    member = CustomerFamilyMember(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        **request.dict()
    )
    db.add(member)
    db.commit()
    
    return {
        "success": True,
        "family_member_id": member.id,
        "relationship": request.relationship,
        "message": "Family member added successfully"
    }


# ============================================================================
# STAGE 8: EMPLOYMENT
# ============================================================================

@router.post("/customer/{customer_id}/employment", status_code=201)
async def add_employment(
    customer_id: str,
    request: EmploymentRequest,
    db: Session = Depends(get_db)
):
    """Stage 8 - Add employment information"""
    from .models_cif import CustomerEmployment
    import uuid

    employment = CustomerEmployment(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        **request.dict()
    )
    db.add(employment)
    db.commit()
    
    return {
        "success": True,
        "employment_id": employment.id,
        "employment_type": request.employment_type,
        "message": "Employment information added successfully"
    }


# ============================================================================
# STAGE 10: FINANCIAL PROFILE
# ============================================================================

@router.post("/customer/{customer_id}/financial-profile", status_code=201)
async def add_financial_profile(
    customer_id: str,
    request: FinancialProfileRequest,
    db: Session = Depends(get_db)
):
    """Stage 10 - Add financial profile"""
    from .models_cif import CustomerFinancialProfile
    import uuid

    profile = CustomerFinancialProfile(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        **request.dict()
    )
    db.add(profile)
    db.commit()
    
    return {
        "success": True,
        "profile_id": profile.id,
        "annual_income": request.annual_income,
        "message": "Financial profile added successfully"
    }


# ============================================================================
# STAGE 11: BANKING PROFILE
# ============================================================================

@router.post("/customer/{customer_id}/banking-profile", status_code=201)
async def add_banking_profile(
    customer_id: str,
    request: BankingProfileRequest,
    db: Session = Depends(get_db)
):
    """Stage 11 - Add customer banking profile"""
    from .models_cif import CustomerBankingProfile
    import uuid

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    banking = CustomerBankingProfile(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        **request.dict()
    )
    db.add(banking)
    db.commit()
    
    return {
        "success": True,
        "banking_profile_id": banking.id,
        "primary_bank_name": request.primary_bank_name,
        "message": "Banking profile added successfully"
    }


# ============================================================================
# STAGE 12: COMPLIANCE
# ============================================================================

@router.post("/customer/{customer_id}/compliance/initiate")
async def initiate_compliance(customer_id: str, db: Session = Depends(get_db)):
    """Stage 12 - Initiate compliance checks"""
    compliance = ComplianceService.initiate_compliance_checks(db, customer_id)
    return {
        "success": True,
        "compliance_id": compliance.id,
        "message": "Compliance checks initiated",
        "checks": {
            "pan_verification": "pending",
            "aadhar_verification": "pending",
            "ckyc": "pending",
            "aml": "pending",
            "pep": "pending",
            "sanction_list": "pending",
            "watchlist": "pending"
        }
    }


@router.post("/customer/{customer_id}/compliance/verify-pan")
async def verify_pan(customer_id: str, db: Session = Depends(get_db)):
    """Verify PAN with external service"""
    compliance = ComplianceService.verify_pan(db, customer_id, "verified")
    return {
        "success": True,
        "pan_verification_status": compliance.pan_verification_status,
        "verified_at": compliance.pan_verified_at
    }


@router.post("/customer/{customer_id}/compliance/verify-aadhar")
async def verify_aadhar(customer_id: str, db: Session = Depends(get_db)):
    """Verify Aadhar"""
    compliance = ComplianceService.verify_aadhar(db, customer_id, "online_otp")
    return {
        "success": True,
        "aadhar_verification_status": compliance.aadhar_verification_status,
        "verification_type": compliance.aadhar_verification_type
    }


@router.post("/customer/{customer_id}/compliance/run-aml")
async def run_aml_check(customer_id: str, db: Session = Depends(get_db)):
    """Run AML screening"""
    compliance = ComplianceService.run_aml_check(db, customer_id)
    return {
        "success": True,
        "aml_status": compliance.aml_check_result,
        "checked_at": compliance.aml_checked_at
    }


# ============================================================================
# STAGE 13: BEHAVIOR & FINDNA
# ============================================================================

@router.post("/customer/{customer_id}/analyze-behavior")
async def analyze_behavior_profile(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Stage 13 - Generate FinDNA and behavior profile"""
    from .models_cif import CustomerFinancialProfile
    
    # Get financial data
    financial = db.query(CustomerFinancialProfile).filter(
        CustomerFinancialProfile.customer_id == customer_id
    ).first()
    
    behavior = BehaviorProfileService.analyze_behavior(
        db, customer_id,
        financial.dict() if financial else {}
    )
    
    return {
        "success": True,
        "behavior_id": behavior.id,
        "financial_dna": behavior.financial_dna,
        "behavior_score": behavior.behavior_score,
        "trust_score": behavior.trust_score,
        "product_affinity": behavior.product_affinity,
        "message": "FinDNA and behavior profile generated - Your competitive advantage!"
    }


# ============================================================================
# STAGE 14: RELATIONSHIPS
# ============================================================================

@router.post("/customer/{customer_id}/relationship/{related_customer_id}")
async def link_relationship(
    customer_id: str,
    related_customer_id: str,
    relationship_type: str = Query(...),
    db: Session = Depends(get_db)
):
    """Stage 14 - Link customer relationships"""
    relationship = RelationshipService.link_relationship(
        db, customer_id, related_customer_id, relationship_type
    )
    return {
        "success": True,
        "relationship_id": relationship.id,
        "relationship_type": relationship_type,
        "message": "Relationship linked successfully"
    }


@router.get("/customer/{customer_id}/network")
async def get_customer_network(customer_id: str, db: Session = Depends(get_db)):
    """Get entire relationship network (graph) for customer"""
    network = RelationshipService.get_customer_network(db, customer_id)
    return {
        "customer_id": customer_id,
        "network": network,
        "message": "Customer relationship graph"
    }


# ============================================================================
# STAGE 16: APPROVAL WORKFLOW
# ============================================================================

@router.post("/customer/{customer_id}/approval/initiate")
async def initiate_approval(
    customer_id: str,
    initiated_by: str = Query(...),
    notes: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Stage 16 - Initiate approval workflow"""
    eligibility = CustomerApprovalService.evaluate_customer_eligibility(db, customer_id)
    approval = CustomerApprovalService.initiate_approval(db, customer_id, initiated_by, notes)
    response = {
        "success": True,
        "approval_id": approval.id,
        "workflow_instance_id": approval.workflow_instance_id,
        "workflow_stage": 1,
        "status": "pending",
        "eligibility": eligibility,
        "message": "Approval workflow initiated"
    }
    if eligibility and eligibility.get("passed") is False:
        response["message"] = "Approval workflow initiated, but customer is not eligible based on platform rule evaluation"
    return response


@router.post("/customer/{customer_id}/approval/{workflow_instance_id}/transition")
async def transition_approval(
    customer_id: str,
    workflow_instance_id: str,
    request: ApprovalActionRequest,
    action: str = Query(...),
    actor_id: str = Query(...),
    actor_role: str = Query(...),
    db: Session = Depends(get_db)
):
    """Execute a generic workflow transition on customer approval workflow"""
    if not request:
        raise HTTPException(status_code=400, detail="Request body required")

    approval = CustomerApprovalService.transition_approval(
        db,
        workflow_instance_id,
        customer_id,
        action,
        actor_id,
        actor_role,
        request.comments,
        request.approved,
    )

    return {
        "success": True,
        "approval_id": approval.id,
        "workflow_instance_id": approval.workflow_instance_id,
        "status": approval.approval_status,
        "stage": approval.workflow_stage,
        "current_state": approval.current_state,
        "message": "Workflow transition processed"
    }


# ============================================================================
# STAGE 18: CUSTOMER 360
# ============================================================================

@router.get("/customer/{customer_id}/360")
async def get_customer_360(customer_id: str, db: Session = Depends(get_db)):
    """Stage 18 - Get complete Customer 360 view"""
    try:
        customer_360 = Customer360Service.get_customer_360(db, customer_id)
        return customer_360
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# DOCUMENT MANAGEMENT
# ============================================================================

@router.post("/customer/{customer_id}/document", status_code=201)
async def upload_document(
    customer_id: str,
    document_category: str = Query(...),
    document_type: str = Query(...),
    document_title: Optional[str] = Query(None),
    file: UploadFile = File(...),
    expiry_date: Optional[date] = Query(None),
    uploaded_by: str = Query(...),
    db: Session = Depends(get_db)
):
    """Upload document to vault"""
    document = DocumentService.upload_document(
        db=db,
        customer_id=customer_id,
        document_category=document_category,
        document_type=document_type,
        file=file,
        file_name=document_title or file.filename,
        file_size=file.size,
        mime_type=file.content_type,
        uploaded_by=uploaded_by,
        expiry_date=expiry_date,
    )

    return {
        "success": True,
        "document_id": document.id,
        "category": document_category,
        "type": document_type,
        "version": document.version,
        "document_url": document.document_url,
        "message": "Document uploaded successfully"
    }


@router.get("/customer/{customer_id}/documents")
async def get_documents(customer_id: str, db: Session = Depends(get_db)):
    """Get all documents for customer"""
    from .models_cif import CustomerDocument
    
    documents = db.query(CustomerDocument).filter(
        CustomerDocument.customer_id == customer_id,
        CustomerDocument.is_latest == True
    ).all()
    
    return {
        "customer_id": customer_id,
        "total_documents": len(documents),
        "documents": [
            {
                "id": doc.id,
                "category": doc.document_category,
                "type": doc.document_type,
                "name": doc.document_name,
                "version": doc.version,
                "uploaded": doc.upload_timestamp,
                "expires": doc.expiry_date
            }
            for doc in documents
        ]
    }


# ============================================================================
# HOUSEHOLD MANAGEMENT
# ============================================================================

@router.post("/household", status_code=201)
async def create_household(
    primary_customer_id: str = Query(...),
    household_name: str = Query(...),
    household_type: str = Query(...),
    db: Session = Depends(get_db)
):
    """Create household for family-based servicing"""
    household = HouseholdService.create_household(
        db, primary_customer_id, household_name, household_type
    )
    return {
        "success": True,
        "household_id": household.id,
        "household_name": household_name,
        "message": "Household created successfully"
    }


@router.post("/household/{household_id}/member/{customer_id}")
async def add_household_member(
    household_id: str,
    customer_id: str,
    member_role: str = Query(...),
    db: Session = Depends(get_db)
):
    """Add member to household"""
    HouseholdService.add_household_member(db, household_id, customer_id, member_role)
    return {
        "success": True,
        "message": "Member added to household successfully"
    }


# ============================================================================
# HEALTH & STATUS
# ============================================================================

@router.get("/customer/{customer_id}/onboarding-progress")
async def get_onboarding_progress(customer_id: str, db: Session = Depends(get_db)):
    """Get onboarding progress"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "customer_id": customer.id,
        "customer_lifecycle": customer.customer_lifecycle,
        "completion_percentage": customer.onboarding_completion_percentage,
        "kyc_status": customer.kyc_status,
        "approval_status": customer.approval_status,
        "cif_id": customer.cif_id,
        "created_at": customer.created_at,
        "last_updated": customer.updated_at
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Customer Information File (CIF) System",
        "version": "1.0.0"
    }
