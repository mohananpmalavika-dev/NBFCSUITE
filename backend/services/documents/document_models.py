"""
Document Checklist Models
Defines data models for document requirements, templates, and verification
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator


# ============================================================================
# ENUMERATIONS
# ============================================================================

class DocumentType(str, Enum):
    """Document types"""
    # Identity documents
    PAN_CARD = "PAN_CARD"
    AADHAAR_CARD = "AADHAAR_CARD"
    PASSPORT = "PASSPORT"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    VOTER_ID = "VOTER_ID"
    
    # Address proof
    ADDRESS_PROOF = "ADDRESS_PROOF"
    UTILITY_BILL = "UTILITY_BILL"
    BANK_STATEMENT = "BANK_STATEMENT"
    RENT_AGREEMENT = "RENT_AGREEMENT"
    
    # Income documents
    SALARY_SLIP = "SALARY_SLIP"
    FORM_16 = "FORM_16"
    ITR = "ITR"
    BANK_STATEMENT_INCOME = "BANK_STATEMENT_INCOME"
    
    # Business documents
    GST_CERTIFICATE = "GST_CERTIFICATE"
    BUSINESS_REGISTRATION = "BUSINESS_REGISTRATION"
    UDYAM_CERTIFICATE = "UDYAM_CERTIFICATE"
    SHOP_ESTABLISHMENT = "SHOP_ESTABLISHMENT"
    FINANCIALS = "FINANCIALS"
    BALANCE_SHEET = "BALANCE_SHEET"
    PROFIT_LOSS = "PROFIT_LOSS"
    
    # Property documents
    PROPERTY_PAPERS = "PROPERTY_PAPERS"
    SALE_DEED = "SALE_DEED"
    ENCUMBRANCE_CERTIFICATE = "ENCUMBRANCE_CERTIFICATE"
    PROPERTY_TAX_RECEIPT = "PROPERTY_TAX_RECEIPT"
    
    # Other
    PHOTOGRAPH = "PHOTOGRAPH"
    SIGNATURE = "SIGNATURE"
    CHEQUE = "CHEQUE"
    CREDIT_REPORT = "CREDIT_REPORT"
    OTHER = "OTHER"


class DocumentFormat(str, Enum):
    """Allowed document formats"""
    PDF = "PDF"
    JPG = "JPG"
    JPEG = "JPEG"
    PNG = "PNG"
    TIFF = "TIFF"
    DOC = "DOC"
    DOCX = "DOCX"


class VerificationStatus(str, Enum):
    """Document verification status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    RESUBMIT_REQUIRED = "RESUBMIT_REQUIRED"


class CustomerType(str, Enum):
    """Customer types"""
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    BUSINESS = "BUSINESS"
    PROFESSIONAL = "PROFESSIONAL"
    PENSIONER = "PENSIONER"


class ChecklistStatus(str, Enum):
    """Checklist status"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


# ============================================================================
# CONDITIONAL LOGIC MODELS
# ============================================================================

class ConditionOperator(str, Enum):
    """Operators for conditions"""
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    IN = "IN"
    NOT_IN = "NOT_IN"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    CONTAINS = "CONTAINS"


class DocumentCondition(BaseModel):
    """Condition for document requirement"""
    field: str = Field(description="Field to check (e.g., employment_type, loan_amount)")
    operator: ConditionOperator
    value: Any = Field(description="Value to compare against")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "employment_type",
                "operator": "EQUALS",
                "value": "SELF_EMPLOYED"
            }
        }


class ConditionalRule(BaseModel):
    """Conditional rule for document requirement"""
    conditions: List[DocumentCondition]
    logic: str = Field("AND", description="AND or OR logic for multiple conditions")
    
    @validator('logic')
    def validate_logic(cls, v):
        if v not in ['AND', 'OR']:
            raise ValueError('logic must be AND or OR')
        return v


# ============================================================================
# VERIFICATION CHECKLIST MODELS
# ============================================================================

class VerificationCheckItem(BaseModel):
    """Individual verification check item"""
    check_name: str
    description: str
    mandatory: bool = True
    check_type: str = Field(description="VISUAL, OCR, API, MANUAL")
    expected_value: Optional[Any] = None


class VerificationChecklist(BaseModel):
    """Verification checklist for a document"""
    document_type: DocumentType
    check_items: List[VerificationCheckItem] = []
    auto_verify_enabled: bool = False
    ocr_enabled: bool = False
    api_verification_enabled: bool = False


# ============================================================================
# DOCUMENT TEMPLATE MODELS
# ============================================================================

class OCRField(BaseModel):
    """OCR extraction field configuration"""
    field_name: str
    field_type: str = Field(description="TEXT, NUMBER, DATE, etc.")
    required: bool = True
    validation_regex: Optional[str] = None
    extraction_zone: Optional[Dict[str, float]] = None  # x, y, width, height


class DocumentTemplate(BaseModel):
    """Document template configuration"""
    id: Optional[str] = None
    tenant_id: str
    
    # Template information
    template_code: str
    template_name: str
    document_type: DocumentType
    description: str
    
    # Format requirements
    allowed_formats: List[DocumentFormat] = [DocumentFormat.PDF, DocumentFormat.JPG, DocumentFormat.PNG]
    max_file_size_mb: float = Field(5.0, ge=0.1, le=50)
    min_resolution_dpi: Optional[int] = None
    
    # OCR configuration
    ocr_fields: List[OCRField] = []
    
    # Verification
    verification_checklist: Optional[VerificationChecklist] = None
    
    # Validity
    has_validity_period: bool = False
    validity_days: Optional[int] = None
    
    # Metadata
    status: ChecklistStatus = ChecklistStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


# ============================================================================
# DOCUMENT REQUIREMENT MODELS
# ============================================================================

class DocumentRequirement(BaseModel):
    """Document requirement configuration"""
    id: Optional[str] = None
    
    # Document information
    document_type: DocumentType
    document_name: str
    template_id: Optional[str] = None
    
    # Requirement flags
    mandatory: bool = True
    conditional: bool = False
    conditional_rule: Optional[ConditionalRule] = None
    
    # Customer type specific
    customer_types: List[CustomerType] = []  # Empty means all types
    
    # Document count
    min_count: int = Field(1, ge=0)
    max_count: int = Field(1, ge=1)
    
    # Validity
    check_validity: bool = False
    validity_days: Optional[int] = None
    
    # Instructions
    instructions: Optional[str] = None
    sample_document_url: Optional[str] = None
    
    # Metadata
    display_order: int = Field(1, ge=1)


# ============================================================================
# DOCUMENT CHECKLIST MODELS
# ============================================================================

class DocumentChecklist(BaseModel):
    """Main document checklist model"""
    id: Optional[str] = None
    tenant_id: str
    
    # Checklist information
    checklist_code: str = Field(description="Unique checklist code")
    checklist_name: str
    description: str
    status: ChecklistStatus = ChecklistStatus.DRAFT
    
    # Product association
    product_id: Optional[str] = None
    product_code: Optional[str] = None
    apply_to_all_products: bool = False
    
    # Document requirements
    requirements: List[DocumentRequirement] = []
    
    # Configuration
    allow_additional_documents: bool = True
    auto_request_missing: bool = True
    send_reminders: bool = True
    reminder_frequency_days: int = Field(3, ge=1)
    
    # Verification settings
    require_verification: bool = True
    auto_verify_eligible_docs: bool = False
    verification_sla_hours: Optional[int] = None
    
    # Metadata
    effective_date: date
    expiry_date: Optional[date] = None
    priority: int = Field(10, ge=1, le=100)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


# ============================================================================
# HELPER MODELS
# ============================================================================

class DocumentEvaluationContext(BaseModel):
    """Context for evaluating conditional documents"""
    customer_type: CustomerType
    employment_type: Optional[str] = None
    loan_amount: Optional[float] = None
    loan_type: Optional[str] = None
    property_value: Optional[float] = None
    custom_fields: Dict[str, Any] = {}


class EvaluatedRequirement(BaseModel):
    """Evaluated document requirement"""
    requirement: DocumentRequirement
    is_required: bool
    reason: str


class ChecklistEvaluationResult(BaseModel):
    """Result of checklist evaluation"""
    checklist_id: str
    checklist_code: str
    checklist_name: str
    total_requirements: int
    mandatory_requirements: int
    conditional_requirements: int
    evaluated_requirements: List[EvaluatedRequirement]
    required_documents: List[DocumentType]


class DocumentChecklistFilter(BaseModel):
    """Filter for listing checklists"""
    status: Optional[ChecklistStatus] = None
    product_id: Optional[str] = None
    product_code: Optional[str] = None
    search_term: Optional[str] = None


class DocumentChecklistStats(BaseModel):
    """Statistics for document checklists"""
    total_checklists: int = 0
    active_checklists: int = 0
    draft_checklists: int = 0
    total_templates: int = 0
    checklists_by_product: Dict[str, int] = {}


class DocumentChecklistClone(BaseModel):
    """Clone checklist request"""
    new_checklist_code: str
    new_checklist_name: Optional[str] = None
    new_product_id: Optional[str] = None
