"""
HRMS Pydantic Schemas
Request/Response models for HRMS API
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS (matching database)
# ============================================================================

class EmploymentTypeEnum(str, Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    PROBATION = "probation"
    INTERN = "intern"
    CONSULTANT = "consultant"


class EmploymentStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESIGNED = "resigned"
    TERMINATED = "terminated"
    ABSCONDED = "absconded"
    RETIRED = "retired"


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroupEnum(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"


class MaritalStatusEnum(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class DepartmentTypeEnum(str, Enum):
    OPERATIONS = "operations"
    FINANCE = "finance"
    IT = "it"
    HR = "hr"
    MARKETING = "marketing"
    SALES = "sales"
    ADMIN = "admin"
    LEGAL = "legal"
    COMPLIANCE = "compliance"
    AUDIT = "audit"
    RISK = "risk"
    CREDIT = "credit"
    COLLECTIONS = "collections"
    CUSTOMER_SERVICE = "customer_service"
    OTHER = "other"


class ReportingTypeEnum(str, Enum):
    DIRECT = "direct"
    DOTTED = "dotted"
    FUNCTIONAL = "functional"


# ============================================================================
# ORGANIZATION SCHEMAS
# ============================================================================

class OrganizationBase(BaseModel):
    """Base organization fields"""
    organization_name: str
    short_name: Optional[str] = None
    legal_name: Optional[str] = None
    pan_number: Optional[str] = None
    tan_number: Optional[str] = None
    gstin: Optional[str] = None
    cin_number: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    registered_address_line1: Optional[str] = None
    registered_address_line2: Optional[str] = None
    registered_city: Optional[str] = None
    registered_state: Optional[str] = None
    registered_pincode: Optional[str] = None
    established_date: Optional[date] = None
    is_active: bool = True


class OrganizationCreate(OrganizationBase):
    """Create organization"""
    pass


class OrganizationUpdate(BaseModel):
    """Update organization (all fields optional)"""
    organization_name: Optional[str] = None
    short_name: Optional[str] = None
    legal_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    """Organization response"""
    id: int
    organization_code: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrganizationListItem(BaseModel):
    """Simplified organization for lists"""
    id: int
    organization_code: str
    organization_name: str
    short_name: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# DEPARTMENT SCHEMAS
# ============================================================================

class DepartmentBase(BaseModel):
    """Base department fields"""
    department_name: str
    department_type: DepartmentTypeEnum = DepartmentTypeEnum.OTHER
    description: Optional[str] = None
    organization_id: int
    parent_department_id: Optional[int] = None
    hod_employee_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    extension: Optional[str] = None
    location: Optional[str] = None
    floor: Optional[str] = None
    cost_center_code: Optional[str] = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    """Create department"""
    pass


class DepartmentUpdate(BaseModel):
    """Update department (all fields optional)"""
    department_name: Optional[str] = None
    department_type: Optional[DepartmentTypeEnum] = None
    description: Optional[str] = None
    parent_department_id: Optional[int] = None
    hod_employee_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    """Department response"""
    id: int
    department_code: str
    organization_name: Optional[str] = None
    parent_department_name: Optional[str] = None
    hod_name: Optional[str] = None
    employee_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DepartmentListItem(BaseModel):
    """Simplified department for lists"""
    id: int
    department_code: str
    department_name: str
    department_type: DepartmentTypeEnum
    hod_name: Optional[str] = None
    employee_count: int = 0
    is_active: bool
    
    class Config:
        from_attributes = True


class DepartmentTreeNode(BaseModel):
    """Department tree node for org chart"""
    id: int
    department_code: str
    department_name: str
    department_type: DepartmentTypeEnum
    parent_department_id: Optional[int] = None
    hod_employee_id: Optional[int] = None
    hod_name: Optional[str] = None
    employee_count: int = 0
    children: List['DepartmentTreeNode'] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# DESIGNATION SCHEMAS
# ============================================================================

class DesignationBase(BaseModel):
    """Base designation fields"""
    designation_name: str
    description: Optional[str] = None
    level: Optional[int] = None
    grade: Optional[str] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    min_experience_years: Optional[int] = None
    required_qualification: Optional[str] = None
    is_active: bool = True


class DesignationCreate(DesignationBase):
    """Create designation"""
    pass


class DesignationUpdate(BaseModel):
    """Update designation (all fields optional)"""
    designation_name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    grade: Optional[str] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    is_active: Optional[bool] = None


class DesignationResponse(DesignationBase):
    """Designation response"""
    id: int
    designation_code: str
    employee_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DesignationListItem(BaseModel):
    """Simplified designation for lists"""
    id: int
    designation_code: str
    designation_name: str
    level: Optional[int] = None
    grade: Optional[str] = None
    employee_count: int = 0
    is_active: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# EMPLOYEE SCHEMAS
# ============================================================================

class EmployeeBase(BaseModel):
    """Base employee fields"""
    # Employment Information
    organization_id: int
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    reporting_manager_id: Optional[int] = None
    employment_type: EmploymentTypeEnum = EmploymentTypeEnum.PERMANENT
    employment_status: EmploymentStatusEnum = EmploymentStatusEnum.ACTIVE
    date_of_joining: date
    date_of_confirmation: Optional[date] = None
    work_location: Optional[str] = None
    shift_type: Optional[str] = None
    
    # Personal Information
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    blood_group: Optional[BloodGroupEnum] = None
    marital_status: Optional[MaritalStatusEnum] = None
    
    # Family Details
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    spouse_name: Optional[str] = None
    number_of_children: int = 0
    
    # Contact Information
    personal_email: Optional[EmailStr] = None
    official_email: Optional[EmailStr] = None
    mobile: str
    alternate_mobile: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    
    # Current Address
    current_address_line1: Optional[str] = None
    current_address_line2: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_pincode: Optional[str] = None
    
    # Permanent Address
    permanent_address_line1: Optional[str] = None
    permanent_address_line2: Optional[str] = None
    permanent_city: Optional[str] = None
    permanent_state: Optional[str] = None
    permanent_pincode: Optional[str] = None
    is_permanent_same_as_current: bool = False
    
    # Identity Documents
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    passport_number: Optional[str] = None
    driving_license_number: Optional[str] = None
    
    # Bank Details
    salary_bank_name: Optional[str] = None
    salary_account_number: Optional[str] = None
    salary_ifsc_code: Optional[str] = None
    pf_number: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None
    
    # Salary
    current_ctc: Optional[Decimal] = None
    basic_salary: Optional[Decimal] = None
    
    # Education
    highest_qualification: Optional[str] = None
    specialization: Optional[str] = None
    university: Optional[str] = None
    year_of_passing: Optional[int] = None
    total_experience_years: Optional[int] = None
    
    # Status
    is_active: bool = True
    notice_period_days: int = 30
    
    @validator('mobile', 'alternate_mobile', 'emergency_contact_number')
    def validate_mobile(cls, v):
        if v and len(v) != 10:
            raise ValueError('Mobile must be 10 digits')
        return v
    
    @validator('pan_number')
    def validate_pan(cls, v):
        if v and len(v) != 10:
            raise ValueError('PAN must be 10 characters')
        return v.upper() if v else v
    
    @validator('aadhaar_number')
    def validate_aadhaar(cls, v):
        if v and len(v) != 12:
            raise ValueError('Aadhaar must be 12 digits')
        return v


class EmployeeCreate(EmployeeBase):
    """Create employee"""
    pass


class EmployeeUpdate(BaseModel):
    """Update employee (all fields optional)"""
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    reporting_manager_id: Optional[int] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    employment_status: Optional[EmploymentStatusEnum] = None
    date_of_confirmation: Optional[date] = None
    mobile: Optional[str] = None
    personal_email: Optional[EmailStr] = None
    official_email: Optional[EmailStr] = None
    current_address_line1: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_ctc: Optional[Decimal] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    """Employee response with all details"""
    id: int
    employee_code: str
    full_name: str
    age: Optional[int] = None
    organization_name: Optional[str] = None
    department_name: Optional[str] = None
    designation_name: Optional[str] = None
    reporting_manager_name: Optional[str] = None
    gross_salary: Optional[Decimal] = None
    net_salary: Optional[Decimal] = None
    is_on_probation: bool = False
    probation_end_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EmployeeListItem(BaseModel):
    """Simplified employee for lists"""
    id: int
    employee_code: str
    full_name: str
    official_email: Optional[str] = None
    mobile: str
    department_name: Optional[str] = None
    designation_name: Optional[str] = None
    employment_type: EmploymentTypeEnum
    employment_status: EmploymentStatusEnum
    date_of_joining: date
    is_active: bool
    
    class Config:
        from_attributes = True


class EmployeeCardView(BaseModel):
    """Employee card view for dashboards"""
    id: int
    employee_code: str
    full_name: str
    designation_name: Optional[str] = None
    department_name: Optional[str] = None
    photo_url: Optional[str] = None
    official_email: Optional[str] = None
    mobile: str
    reporting_manager_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# REPORTING HIERARCHY SCHEMAS
# ============================================================================

class ReportingHierarchyBase(BaseModel):
    """Base reporting hierarchy fields"""
    employee_id: int
    manager_id: int
    reporting_type: ReportingTypeEnum = ReportingTypeEnum.DIRECT
    is_primary: bool = True
    effective_from: date
    effective_to: Optional[date] = None
    is_current: bool = True
    change_reason: Optional[str] = None


class ReportingHierarchyCreate(ReportingHierarchyBase):
    """Create reporting hierarchy"""
    pass


class ReportingHierarchyUpdate(BaseModel):
    """Update reporting hierarchy"""
    effective_to: Optional[date] = None
    is_current: Optional[bool] = None


class ReportingHierarchyResponse(ReportingHierarchyBase):
    """Reporting hierarchy response"""
    id: int
    employee_name: Optional[str] = None
    manager_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrgChartNode(BaseModel):
    """Organization chart node"""
    id: int
    employee_code: str
    full_name: str
    designation_name: Optional[str] = None
    department_name: Optional[str] = None
    photo_url: Optional[str] = None
    reporting_manager_id: Optional[int] = None
    subordinates: List['OrgChartNode'] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# PAGINATION & FILTERING
# ============================================================================

class PaginatedEmployeeResponse(BaseModel):
    """Paginated employee response"""
    items: List[EmployeeListItem]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedDepartmentResponse(BaseModel):
    """Paginated department response"""
    items: List[DepartmentListItem]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedDesignationResponse(BaseModel):
    """Paginated designation response"""
    items: List[DesignationListItem]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# DASHBOARD & STATISTICS
# ============================================================================

class EmployeeDashboardStats(BaseModel):
    """Employee dashboard statistics"""
    total_employees: int = 0
    active_employees: int = 0
    inactive_employees: int = 0
    on_probation: int = 0
    permanent_employees: int = 0
    contract_employees: int = 0
    new_joiners_this_month: int = 0
    resignations_this_month: int = 0
    
    # Department-wise count
    by_department: List[dict] = []
    
    # Designation-wise count
    by_designation: List[dict] = []
    
    # Employment type distribution
    by_employment_type: dict = {}
    
    # Gender distribution
    by_gender: dict = {}


class DepartmentStats(BaseModel):
    """Department statistics"""
    total_departments: int = 0
    active_departments: int = 0
    employees_by_department: List[dict] = []


class DesignationStats(BaseModel):
    """Designation statistics"""
    total_designations: int = 0
    active_designations: int = 0
    employees_by_designation: List[dict] = []


# ============================================================================
# SEARCH & FILTERS
# ============================================================================

class EmployeeFilters(BaseModel):
    """Employee filter parameters"""
    page: int = 1
    page_size: int = 20
    search: Optional[str] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    employment_status: Optional[EmploymentStatusEnum] = None
    reporting_manager_id: Optional[int] = None
    is_active: Optional[bool] = None


class EmployeeSearchParams(BaseModel):
    """Employee search parameters"""
    employee_code: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    pan_number: Optional[str] = None


# Enable forward references
DepartmentTreeNode.model_rebuild()
OrgChartNode.model_rebuild()
