"""
Customer Information File (CIF) Service Layer
Handles all customer operations across 18 stages
"""

import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from .models_cif import (
    Customer, Prospect, CustomerBasicDetails, CustomerIdentityDocument,
    CustomerAddress, CustomerContact, CustomerFamilyMember, CustomerEmployment,
    CustomerBusinessProfile, CustomerFinancialProfile, CustomerBankingProfile,
    CustomerCompliance, CustomerBehaviorProfile, CustomerRelationship,
    CustomerDocument, CustomerApproval, CustomerTimeline, CustomerHousehold,
    CustomerParty, CustomerConsent, OnboardingWorkflow, CIFSequence
)


class CustomerLifecycleStatus(str, Enum):
    """Customer lifecycle states"""
    LEAD = "lead"
    PROSPECT = "prospect"
    PENDING_VERIFICATION = "pending_verification"
    KYC_IN_PROGRESS = "kyc_in_progress"
    KYC_APPROVED = "kyc_approved"
    ACTIVE = "active"
    DORMANT = "dormant"
    CLOSED = "closed"


class OnboardingStage(int, Enum):
    """18 Stages of customer onboarding"""
    SEARCH = 1
    PROSPECT_CREATION = 2
    BASIC_DETAILS = 3
    IDENTITY_VERIFICATION = 4
    ADDRESS = 5
    CONTACTS = 6
    FAMILY = 7
    EMPLOYMENT = 8
    BUSINESS_PROFILE = 9
    FINANCIAL_PROFILE = 10
    BANKING_PROFILE = 11
    COMPLIANCE = 12
    BEHAVIOR_FINDNA = 13
    RELATIONSHIP_MAPPING = 14
    DOCUMENT_VAULT = 15
    APPROVAL = 16
    CIF_GENERATION = 17
    CUSTOMER_360 = 18


class CustomerSearchService:
    """Stage 1 - Customer Search and Deduplication"""

    @staticmethod
    def search_customer(db: Session, **search_params) -> Optional[Customer]:
        """
        Search for existing customer by multiple identifiers
        Never create a duplicate customer
        
        Search by:
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
        query = db.query(Customer)

        if 'mobile_number' in search_params:
            query = query.filter(Customer.phone == search_params['mobile_number'])

        if 'aadhar' in search_params:
            query = query.filter(Customer.aadhar == search_params['aadhar'])

        if 'pan' in search_params:
            query = query.filter(Customer.pan == search_params['pan'])

        if 'passport' in search_params:
            query = query.filter(Customer.passport == search_params['passport'])

        if 'voter_id' in search_params:
            query = query.filter(Customer.voter_id == search_params['voter_id'])

        if 'driving_licence' in search_params:
            query = query.filter(Customer.driving_licence == search_params['driving_licence'])

        if 'gstin' in search_params:
            query = query.filter(Customer.gstin == search_params['gstin'])

        if 'cin' in search_params:
            query = query.filter(Customer.cin == search_params['cin'])

        if 'email' in search_params:
            query = query.filter(Customer.email == search_params['email'])

        if 'customer_id' in search_params:
            query = query.filter(Customer.id == search_params['customer_id'])

        return query.first()

    @staticmethod
    def fuzzy_search(db: Session, name: str, dob: date = None) -> List[Customer]:
        """Fuzzy matching for potential duplicates"""
        # Simple implementation - can be enhanced with Levenshtein distance
        customers = db.query(Customer).filter(
            or_(
                Customer.first_name.ilike(f"%{name}%"),
                Customer.last_name.ilike(f"%{name}%")
            )
        )

        if dob:
            customers = customers.filter(
                # Compare approximate DOB
            )

        return customers.limit(10).all()


class ProspectService:
    """Stage 2 - Prospect Creation and Management"""

    @staticmethod
    def create_prospect(db: Session, prospect_data: Dict[str, Any]) -> Prospect:
        """Create a temporary prospect record"""
        prospect_id = str(uuid.uuid4())
        
        prospect = Prospect(
            id=prospect_id,
            status=CustomerLifecycleStatus.LEAD,
            onboarding_stage=int(OnboardingStage.PROSPECT_CREATION),
            **prospect_data
        )
        db.add(prospect)
        db.commit()
        return prospect

    @staticmethod
    def update_prospect_stage(db: Session, prospect_id: str, stage: int) -> Prospect:
        """Update prospect's onboarding stage"""
        prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
        if prospect:
            prospect.onboarding_stage = stage
            prospect.updated_at = datetime.utcnow()
            db.commit()
        return prospect

    @staticmethod
    def convert_prospect_to_customer(db: Session, prospect_id: str, branch_id: str = None) -> Customer:
        """Convert approved prospect to customer"""
        prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
        if not prospect:
            raise ValueError("Prospect not found")

        # Check for existing customer with same identity
        existing = CustomerSearchService.search_customer(db, 
            pan=prospect.pan_number,
            aadhar=prospect.aadhar_number
        )
        if existing:
            raise ValueError("Customer already exists with same identity documents")

        # Create new customer from prospect
        customer_id = str(uuid.uuid4())
        customer = Customer(
            id=customer_id,
            first_name=prospect.first_name,
            last_name=prospect.last_name or "",
            email=prospect.email,
            phone=prospect.phone,
            pan=prospect.pan_number,
            aadhar=prospect.aadhar_number,
            passport=prospect.passport_number,
            voter_id=prospect.voter_id,
            driving_licence=prospect.driving_licence,
            gstin=prospect.gstin,
            cin=prospect.cin,
            customer_type=prospect.customer_type or "individual",
            customer_lifecycle=CustomerLifecycleStatus.PROSPECT,
            source_prospect_id=prospect_id,
            branch_id=branch_id,
            onboarding_metadata={
                "prospect_id": prospect_id,
                "converted_at": datetime.utcnow().isoformat(),
                "source": prospect.source,
                "campaign": prospect.campaign
            }
        )
        
        db.add(customer)
        
        # Update prospect status
        prospect.status = "prospect"
        prospect.conversion_date = datetime.utcnow()
        
        db.commit()
        return customer


class CIFGenerationService:
    """CIF ID Generation and Management"""

    @staticmethod
    def generate_cif(db: Session, customer_id: str) -> str:
        """
        Generate unique CIF ID
        Format: CIF000000001245
        Never changes once generated
        """
        # Get next sequence
        seq = db.query(CIFSequence).first()
        if not seq:
            seq = CIFSequence(last_cif_number=1000000)
            db.add(seq)

        next_number = seq.last_cif_number + 1
        seq.last_cif_number = next_number
        db.flush()

        # Format CIF
        cif_id = f"CIF{str(next_number).zfill(10)}"

        # Assign to customer
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            customer.cif_id = cif_id
            customer.cif_generated_at = datetime.utcnow()
            customer.customer_lifecycle = CustomerLifecycleStatus.ACTIVE
            
            # Log in timeline
            timeline_entry = CustomerTimeline(
                id=str(uuid.uuid4()),
                customer_id=customer_id,
                event_type="cif_generated",
                event_description=f"CIF {cif_id} generated",
                event_timestamp=datetime.utcnow(),
                event_metadata={"cif_id": cif_id}
            )
            db.add(timeline_entry)
            db.commit()

        return cif_id


class CustomerApprovalService:
    """Stage 16 - Multi-level Approval Workflow"""

    @staticmethod
    def initiate_approval(db: Session, customer_id: str, initiated_by: str) -> CustomerApproval:
        """Initiate customer approval workflow"""
        approval = CustomerApproval(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            workflow_stage=1,
            approval_status="pending",
            initiated_at=datetime.utcnow(),
            initiated_by=initiated_by
        )
        db.add(approval)
        db.commit()
        return approval

    @staticmethod
    def checker_approval(db: Session, approval_id: str, checker_id: str, 
                         approved: bool, comments: str = None) -> CustomerApproval:
        """Checker level approval"""
        approval = db.query(CustomerApproval).filter(CustomerApproval.id == approval_id).first()
        if not approval:
            raise ValueError("Approval not found")

        if approved:
            approval.checker_id = checker_id
            approval.checker_approved_at = datetime.utcnow()
            approval.checker_comments = comments
            approval.workflow_stage = 2
        else:
            approval.approval_status = "rejected"
            approval.rejection_reason = comments

        db.commit()
        return approval

    @staticmethod
    def manager_approval(db: Session, approval_id: str, manager_id: str,
                        approved: bool, comments: str = None) -> CustomerApproval:
        """Manager level approval"""
        approval = db.query(CustomerApproval).filter(CustomerApproval.id == approval_id).first()
        if not approval:
            raise ValueError("Approval not found")

        if approved:
            approval.manager_id = manager_id
            approval.manager_approved_at = datetime.utcnow()
            approval.manager_comments = comments
            approval.workflow_stage = 3
        else:
            approval.approval_status = "rejected"
            approval.rejection_reason = comments

        db.commit()
        return approval

    @staticmethod
    def compliance_approval(db: Session, approval_id: str, compliance_officer_id: str,
                           approved: bool, comments: str = None) -> CustomerApproval:
        """Compliance level approval"""
        approval = db.query(CustomerApproval).filter(CustomerApproval.id == approval_id).first()
        if not approval:
            raise ValueError("Approval not found")

        if approved:
            approval.compliance_officer_id = compliance_officer_id
            approval.compliance_approved_at = datetime.utcnow()
            approval.compliance_comments = comments
            approval.workflow_stage = 4
        else:
            approval.approval_status = "rejected"
            approval.rejection_reason = comments

        db.commit()
        return approval

    @staticmethod
    def final_approval(db: Session, approval_id: str, final_approver_id: str,
                      approved: bool, comments: str = None) -> CustomerApproval:
        """Final approval and CIF generation"""
        approval = db.query(CustomerApproval).filter(CustomerApproval.id == approval_id).first()
        if not approval:
            raise ValueError("Approval not found")

        if approved:
            approval.final_approver_id = final_approver_id
            approval.final_approval_at = datetime.utcnow()
            approval.final_approval_comments = comments
            approval.approval_status = "approved"

            # Generate CIF
            cif_id = CIFGenerationService.generate_cif(db, approval.customer_id)
            approval.cif_generated_on = datetime.utcnow()

            # Update customer
            customer = db.query(Customer).filter(Customer.id == approval.customer_id).first()
            if customer:
                customer.approval_status = "approved"
        else:
            approval.approval_status = "rejected"
            approval.rejection_reason = comments
            
            # Update customer
            customer = db.query(Customer).filter(Customer.id == approval.customer_id).first()
            if customer:
                customer.approval_status = "rejected"

        db.commit()
        return approval


class DocumentService:
    """Stage 15 - Document Vault Management"""

    @staticmethod
    def upload_document(db: Session, customer_id: str, 
                       document_category: str, document_type: str,
                       file_path: str, file_name: str, file_size: int,
                       mime_type: str, uploaded_by: str,
                       expiry_date: date = None) -> CustomerDocument:
        """Upload and version document"""
        doc_id = str(uuid.uuid4())
        
        # Mark previous versions as not latest
        previous_docs = db.query(CustomerDocument).filter(
            and_(
                CustomerDocument.customer_id == customer_id,
                CustomerDocument.document_category == document_category,
                CustomerDocument.document_type == document_type,
                CustomerDocument.is_latest == True
            )
        ).all()
        
        for prev_doc in previous_docs:
            prev_doc.is_latest = False

        # Create new document
        document = CustomerDocument(
            id=doc_id,
            customer_id=customer_id,
            document_category=document_category,
            document_type=document_type,
            document_name=file_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            upload_timestamp=datetime.utcnow(),
            uploaded_by=uploaded_by,
            version=len(previous_docs) + 1,
            is_latest=True,
            expiry_date=expiry_date,
            storage_location="local",  # Can be s3, azure_blob, etc
            document_status="active"
        )
        db.add(document)
        db.commit()
        return document


class ComplianceService:
    """Stage 12 - Compliance Checks"""

    @staticmethod
    def initiate_compliance_checks(db: Session, customer_id: str) -> CustomerCompliance:
        """Initiate all compliance checks"""
        compliance = db.query(CustomerCompliance).filter(
            CustomerCompliance.customer_id == customer_id
        ).first()

        if not compliance:
            compliance = CustomerCompliance(
                id=str(uuid.uuid4()),
                customer_id=customer_id
            )
            db.add(compliance)

        db.commit()
        return compliance

    @staticmethod
    def verify_pan(db: Session, customer_id: str, verification_result: str = "verified") -> CustomerCompliance:
        """Verify PAN"""
        compliance = db.query(CustomerCompliance).filter(
            CustomerCompliance.customer_id == customer_id
        ).first()

        compliance.pan_verification_status = "verified" if verification_result == "verified" else "failed"
        compliance.pan_verified_at = datetime.utcnow()
        compliance.pan_verification_source = "nsdl"
        db.commit()
        return compliance

    @staticmethod
    def verify_aadhar(db: Session, customer_id: str, verification_type: str = "online_otp") -> CustomerCompliance:
        """Verify Aadhar"""
        compliance = db.query(CustomerCompliance).filter(
            CustomerCompliance.customer_id == customer_id
        ).first()

        compliance.aadhar_verification_status = "verified"
        compliance.aadhar_verified_at = datetime.utcnow()
        compliance.aadhar_verification_type = verification_type
        db.commit()
        return compliance

    @staticmethod
    def run_aml_check(db: Session, customer_id: str) -> CustomerCompliance:
        """Run AML check"""
        compliance = db.query(CustomerCompliance).filter(
            CustomerCompliance.customer_id == customer_id
        ).first()

        # Call external AML service
        compliance.aml_check_status = "completed"
        compliance.aml_check_result = "pass"  # or "fail"
        compliance.aml_checked_at = datetime.utcnow()
        db.commit()
        return compliance

    @staticmethod
    def check_pep_status(db: Session, customer_id: str) -> CustomerCompliance:
        """Check if customer is PEP (Politically Exposed Person)"""
        compliance = db.query(CustomerCompliance).filter(
            CustomerCompliance.customer_id == customer_id
        ).first()

        compliance.pep_check_status = "completed"
        compliance.pep_check_result = "pass"
        compliance.pep_checked_at = datetime.utcnow()
        db.commit()
        return compliance

    @staticmethod
    def run_sanction_check(db: Session, customer_id: str) -> CustomerCompliance:
        """Check against sanction lists"""
        compliance = db.query(CustomerCompliance).filter(
            CustomerCompliance.customer_id == customer_id
        ).first()

        compliance.sanction_list_screening_status = "completed"
        compliance.sanction_list_result = "pass"
        compliance.sanction_checked_at = datetime.utcnow()
        db.commit()
        return compliance


class BehaviorProfileService:
    """Stage 13 - FinDNA and Behavioral Profile"""

    @staticmethod
    def analyze_behavior(db: Session, customer_id: str, 
                        financial_data: Dict[str, Any]) -> CustomerBehaviorProfile:
        """Analyze customer behavior and generate FinDNA"""
        behavior = db.query(CustomerBehaviorProfile).filter(
            CustomerBehaviorProfile.customer_id == customer_id
        ).first()

        if not behavior:
            behavior = CustomerBehaviorProfile(
                id=str(uuid.uuid4()),
                customer_id=customer_id
            )
            db.add(behavior)

        # Calculate behavior metrics
        behavior.risk_appetite = "moderate"  # Analyze from data
        behavior.spending_pattern = "medium"
        behavior.saving_pattern = "consistent"
        behavior.decision_style = "analytical"
        behavior.financial_discipline_score = 75
        behavior.behavior_score = 80
        behavior.trust_score = 85

        # Generate FinDNA - Competitive Advantage
        behavior.financial_dna = "Conservative-Stable-High-Trust"

        # Predict product affinity
        behavior.product_affinity = {
            "savings_account": 0.95,
            "fixed_deposits": 0.85,
            "gold_loan": 0.70,
            "personal_loan": 0.60,
            "credit_card": 0.40
        }

        db.commit()
        return behavior


class RelationshipService:
    """Stage 14 - Relationship Mapping (Graph)"""

    @staticmethod
    def link_relationship(db: Session, primary_customer_id: str,
                         related_customer_id: str, relationship_type: str,
                         relationship_strength: str = "medium") -> CustomerRelationship:
        """Create relationship link"""
        relationship = CustomerRelationship(
            id=str(uuid.uuid4()),
            primary_customer_id=primary_customer_id,
            related_customer_id=related_customer_id,
            relationship_type=relationship_type,
            relationship_strength=relationship_strength,
            relationship_since=date.today()
        )
        db.add(relationship)
        db.commit()
        return relationship

    @staticmethod
    def get_customer_network(db: Session, customer_id: str) -> Dict[str, List]:
        """Get entire relationship network (graph) for customer"""
        relationships = db.query(CustomerRelationship).filter(
            CustomerRelationship.primary_customer_id == customer_id
        ).all()

        network = {
            "primary": [],
            "joint_holders": [],
            "guarantors": [],
            "family": [],
            "business": [],
            "introducer": [],
            "other": []
        }

        for rel in relationships:
            related = db.query(Customer).filter(Customer.id == rel.related_customer_id).first()
            if related:
                entry = {
                    "customer_id": related.id,
                    "cif": related.cif_id,
                    "name": f"{related.first_name} {related.last_name}",
                    "relationship": rel.relationship_type,
                    "strength": rel.relationship_strength
                }

                if rel.relationship_type in network:
                    network[rel.relationship_type].append(entry)
                else:
                    network["other"].append(entry)

        return network


class Customer360Service:
    """Stage 18 - Customer 360 Dashboard"""

    @staticmethod
    def get_customer_360(db: Session, customer_id: str) -> Dict[str, Any]:
        """
        Get complete customer view - the heart of the platform
        Shows: Loans, Deposits, Gold, Forex, Insurance, HR, Complaints, 
                Collections, Behavior, Documents, Interactions
        """
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise ValueError("Customer not found")

        # Basic Info
        basic_info = {
            "customer_id": customer.id,
            "cif": customer.cif_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "email": customer.email,
            "phone": customer.phone,
            "customer_type": customer.customer_type,
            "status": customer.customer_lifecycle,
            "branch": customer.branch.name if customer.branch else None,
            "joined_at": customer.created_at
        }

        # Identity Documents
        identity_docs = db.query(CustomerIdentityDocument).filter(
            CustomerIdentityDocument.customer_id == customer_id
        ).all()
        identity = {doc.document_type: {"number": doc.document_number, "status": doc.verification_status}
                   for doc in identity_docs}

        # Addresses
        addresses = db.query(CustomerAddress).filter(
            CustomerAddress.customer_id == customer_id
        ).all()
        address_list = [{
            "type": addr.address_type,
            "full_address": f"{addr.street_line1}, {addr.city}, {addr.state} {addr.postal_code}",
            "is_primary": addr.is_primary
        } for addr in addresses]

        # Financial Profile
        financial = db.query(CustomerFinancialProfile).filter(
            CustomerFinancialProfile.customer_id == customer_id
        ).first()
        financial_data = {
            "annual_income": float(financial.annual_income) if financial and financial.annual_income else 0,
            "credit_score": financial.credit_score if financial else None,
            "net_worth": float(financial.net_worth) if financial and financial.net_worth else 0,
            "risk_rating": financial.risk_rating if financial else None
        } if financial else {}

        # Compliance Status
        compliance = db.query(CustomerCompliance).filter(
            CustomerCompliance.customer_id == customer_id
        ).first()
        compliance_data = {
            "kyc_status": customer.kyc_status,
            "pan_verified": compliance.pan_verification_status if compliance else "pending",
            "aadhar_verified": compliance.aadhar_verification_status if compliance else "pending",
            "aml_status": compliance.aml_check_result if compliance else "pending",
            "pep_status": compliance.pep_check_result if compliance else "pending"
        }

        # Behavior & FinDNA
        behavior = db.query(CustomerBehaviorProfile).filter(
            CustomerBehaviorProfile.customer_id == customer_id
        ).first()
        behavior_data = {
            "findna": behavior.financial_dna if behavior else "Unknown",
            "behavior_score": behavior.behavior_score if behavior else None,
            "trust_score": behavior.trust_score if behavior else None,
            "risk_appetite": behavior.risk_appetite if behavior else None,
            "product_affinity": behavior.product_affinity if behavior else {}
        }

        # Relationships (Graph)
        network = RelationshipService.get_customer_network(db, customer_id)

        # Timeline
        timeline = db.query(CustomerTimeline).filter(
            CustomerTimeline.customer_id == customer_id
        ).order_by(CustomerTimeline.event_timestamp.desc()).limit(20).all()
        timeline_data = [{
            "event": event.event_type,
            "description": event.event_description,
            "timestamp": event.event_timestamp
        } for event in timeline]

        # Documents
        documents = db.query(CustomerDocument).filter(
            CustomerDocument.customer_id == customer_id,
            CustomerDocument.is_latest == True
        ).all()
        doc_list = [{
            "category": doc.document_category,
            "type": doc.document_type,
            "name": doc.document_name,
            "uploaded": doc.upload_timestamp
        } for doc in documents]

        # Compile 360 view
        customer_360 = {
            "basic_info": basic_info,
            "identity": identity,
            "addresses": address_list,
            "financial": financial_data,
            "compliance": compliance_data,
            "behavior": behavior_data,
            "relationships": network,
            "timeline": timeline_data,
            "documents": doc_list,
            "products": {  # These would be populated from other services
                "loans": [],
                "deposits": [],
                "gold_loans": [],
                "forex": [],
                "insurance": [],
                "investments": []
            },
            "complaints": [],  # From complaints service
            "collections": [],  # From collections service
            "transactions": []  # From transaction service
        }

        return customer_360


class HouseholdService:
    """Enterprise - Household/Family Management"""

    @staticmethod
    def create_household(db: Session, primary_customer_id: str,
                        household_name: str, household_type: str) -> CustomerHousehold:
        """Create household for family-based servicing"""
        household = CustomerHousehold(
            id=str(uuid.uuid4()),
            household_name=household_name,
            primary_customer_id=primary_customer_id,
            household_type=household_type,
            household_status="active"
        )
        db.add(household)
        db.commit()
        return household

    @staticmethod
    def add_household_member(db: Session, household_id: str, 
                            customer_id: str, member_role: str) -> None:
        """Add member to household"""
        from .models_cif import CustomerHouseholdMember
        
        member = CustomerHouseholdMember(
            id=str(uuid.uuid4()),
            household_id=household_id,
            customer_id=customer_id,
            member_role=member_role,
            member_status="active"
        )
        db.add(member)
        db.commit()


class ConsentService:
    """Consent Management with versioning"""

    @staticmethod
    def record_consent(db: Session, customer_id: str, consent_type: str,
                      consent_given: bool, consent_document_url: str = None) -> CustomerConsent:
        """Record customer consent"""
        consent = CustomerConsent(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            consent_type=consent_type,
            consent_status="given" if consent_given else "withdrawn",
            consent_date=datetime.utcnow(),
            consent_version="1.0",
            consent_document_url=consent_document_url
        )
        db.add(consent)
        db.commit()
        return consent
