"""
HRMS Employee Schemas
Pydantic schemas for employee operations
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class EmploymentTypeEnum(str, Enum):
    """Employment type"""
    PERMANENT = "permanent"
    CONTRACT = "contract"
    PROBATION = "probation"
    INTERN = "intern"
    CONSULTANT = "consultant"


class EmploymentStatusEnum(str, Enum):
    """Employment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESIGNED = "resigned"
    TERMINATED = "terminated"
    ABSCONDED = "absconded"
    RETIRED = "retired"


class GenderEnum(str, Enum):
    """Gender"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroupEnum(str, Enum):
    """Blood group"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"


class MaritalStatusEnum(str, Enum):
    """Marital status"""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class EmployeeBase(BaseModel):
    """Base employee schema with common fields"""
    
    # Employment Information
    organization_id: str = Field(..., description="Organization ID")
    department_id: Optional[str] = Field(None, description="Department ID")
    designation_id: Optional[str] = Field(None, description="Designation ID")
    reporting_manager_id: Optional[str] = Field(None, description="Reporting Manager ID")
    employment_type: EmploymentTypeEnum = Field(EmploymentTypeEnum.PERMANENT, description="Employment type")
    employment_status: EmploymentStatusEnum = Field(EmploymentStatusEnum.ACTIVE, description="Employment status")
    date_of_joining: date = Field(..., description="Date of joining")
    date_of_confirmation: Optional[date] = Field(None, description="Date of confirmation")
    work_location: Optional[str] = Field(None, max_length=100, description="Work location")
    shift_type: Optional[str] = Field(None, max_length=20, description="Shift type")
    work_schedule: Optional[str] = Field(None, max_length=50, description="Work schedule")
    
    # Personal Information
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    middle_name: Optional[str] = Field(None, max_length=100, description="Middle name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    gender: Optional[GenderEnum] = Field(None, description="Gender")
    blood_group: Optional[BloodGroupEnum] = Field(None, description="Blood group")
    marital_status: Optional[MaritalStatusEnum] = Field(None, description="Marital status")
    
    # Family Details
    father_name: Optional[str] = Field(None, max_length=200, description="Father's name")
    mother_name: Optional[str] = Field(None, max_length=200, description="Mother's name")
    spouse_name: Optional[str] = Field(None, max_length=200, description="Spouse's name")
    number_of_children: int = Field(0, ge=0, description="Number of children")
    
    # Contact Information
    personal_email: Optional[str] = Field(None, max_length=100, description="Personal email")
    official_email: Optional[str] = Field(None, max_length=100, description="Official email")
    mobile: str = Field(..., min_length=10, max_length=20, description="Mobile number")
    alternate_mobile: Optional[str] = Field(None, max_length=20, description="Alternate mobile")
    emergency_contact_name: Optional[str] = Field(None, max_length=200, description="Emergency contact name")
    emergency_contact_number: Optional[str] = Field(None, max_length=20, description="Emergency contact number")
    emergency_contact_relation: Optional[str] = Field(None, max_length=50, description="Emergency contact relation")
    
    # Current Address
    current_address_line1: Optional[str] = Field(None, max_length=200, description="Current address line 1")
    current_address_line2: Optional[str] = Field(None, max_length=200, description="Current address line 2")
    current_city: Optional[str] = Field(None, max_length=100, description="Current city")
    current_state: Optional[str] = Field(None, max_length=100, description="Current state")
    current_pincode: Optional[str] = Field(None, max_length=10, description="Current pincode")
    current_country: str = Field("India", max_length=100, description="Current country")
    
    # Permanent Address
    is_permanent_same_as_current: bool = Field(False, description="Is permanent address same as current")
    permanent_address_line1: Optional[str] = Field(None, max_length=200, description="Permanent address line 1")
    permanent_address_line2: Optional[str] = Field(None, max_length=200, description="Permanent address line 2")
    permanent_city: Optional[str] = Field(None, max_length=100, description="Permanent city")
    permanent_state: Optional[str] = Field(None, max_length=100, description="Permanent state")
    permanent_pincode: Optional[str] = Field(None, max_length=10, description="Permanent pincode")
    permanent_country: str = Field("India", max_length=100, description="Permanent country")
    
    # Identity Documents
    pan_number: Optional[str] = Field(None, max_length=10, description="PAN number")
    aadhaar_number: Optional[str] = Field(None, max_length=12, description="Aadhaar number")
    passport_number: Optional[str] = Field(None, max_length=20, description="Passport number")
    driving_license_number: Optional[str] = Field(None, max_length=20, description="Driving license number")
    voter_id_number: Optional[str] = Field(None, max_length=20, description="Voter ID number")
    
    # Bank & Salary Information
    salary_bank_name: Optional[str] = Field(None, max_length=100, description="Salary bank name")
    salary_account_number: Optional[str] = Field(None, max_length=30, description="Salary account number")
    salary_ifsc_code: Optional[str] = Field(None, max_length=11, description="Salary IFSC code")
    salary_account_holder_name: Optional[str] = Field(None, max_length=200, description="Salary account holder name")
    pf_number: Optional[str] = Field(None, max_length=30, description="PF number")
    uan_number: Optional[str] = Field(None, max_length=12, description="UAN number")
    pf_join_date: Optional[date] = Field(None, description="PF join date")
    esi_number: Optional[str] = Field(None, max_length=20, description="ESI number")
    current_ctc: Optional[Decimal] = Field(None, description="Current CTC")
    basic_salary: Optional[Decimal] = Field(None, description="Basic salary")
    gross_salary: Optional[Decimal] = Field(None, description="Gross salary")
    net_salary: Optional[Decimal] = Field(None, description="Net salary")
    
    # Education & Experience
    highest_qualification: Optional[str] = Field(None, max_length=100, description="Highest qualification")
    specialization: Optional[str] = Field(None, max_length=100, description="Specialization")
    university: Optional[str] = Field(None, max_length=200, description="University")
    year_of_passing: Optional[int] = Field(None, description="Year of passing")
    total_experience_years: Optional[int] = Field(None, ge=0, description="Total experience in years")
    previous_employer: Optional[str] = Field(None, max_length=200, description="Previous employer")
    previous_designation: Optional[str] = Field(None, max_length=100, description="Previous designation")
    
    # Documents & Compliance
    photo_url: Optional[str] = Field(None, max_length=500, description="Photo URL")
    signature_url: Optional[str] = Field(None, max_length=500, description="Signature URL")
    is_background_verified: bool = Field(False, description="Background verified")
    background_verification_date: Optional[date] = Field(None, description="Background verification date")
    background_verification_agency: Optional[str] = Field(None, max_length=200, description="Background verification agency")
    is_police_verified: bool = Field(False, description="Police verified")
    police_verification_date: Optional[date] = Field(None, description="Police verification date")
    is_medical_done: bool = Field(False, description="Medical done")
    medical_examination_date: Optional[date] = Field(None, description="Medical examination date")
    is_medical_fit: bool = Field(True, description="Medical fit")
    
    # Status & Flags
    is_active: bool = Field(True, description="Is active")
    is_on_probation: bool = Field(False, description="Is on probation")
    probation_end_date: Optional[date] = Field(None, description="Probation end date")
    notice_period_days: int = Field(30, ge=0, description="Notice period in days")
    
    # Additional Information
    remarks: Optional[str] = Field(None, description="Remarks")
    skills: Optional[str] = Field(None, description="Skills (JSON array or comma-separated)")
    certifications: Optional[str] = Field(None, description="Certifications (JSON array)")
    languages_known: Optional[str] = Field(None, description="Languages known (JSON array)")


# ============================================================================
# CREATE/UPDATE SCHEMAS
# ============================================================================

class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee"""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee (all fields optional)"""
    
    # Employment Information
    department_id: Optional[str] = None
    designation_id: Optional[str] = None
    reporting_manager_id: Optional[str] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    employment_status: Optional[EmploymentStatusEnum] = None
    date_of_confirmation: Optional[date] = None
    date_of_resignation: Optional[date] = None
    date_of_relieving: Optional[date] = None
    last_working_day: Optional[date] = None
    work_location: Optional[str] = None
    shift_type: Optional[str] = None
    work_schedule: Optional[str] = None
    
    # Personal Information
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    blood_group: Optional[BloodGroupEnum] = None
    marital_status: Optional[MaritalStatusEnum] = None
    
    # Family Details
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    spouse_name: Optional[str] = None
    number_of_children: Optional[int] = None
    
    # Contact Information
    personal_email: Optional[str] = None
    official_email: Optional[str] = None
    mobile: Optional[str] = None
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
    current_country: Optional[str] = None
    
    # Permanent Address
    is_permanent_same_as_current: Optional[bool] = None
    permanent_address_line1: Optional[str] = None
    permanent_address_line2: Optional[str] = None
    permanent_city: Optional[str] = None
    permanent_state: Optional[str] = None
    permanent_pincode: Optional[str] = None
    permanent_country: Optional[str] = None
    
    # Identity Documents
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    passport_number: Optional[str] = None
    driving_license_number: Optional[str] = None
    voter_id_number: Optional[str] = None
    
    # Bank & Salary Information
    salary_bank_name: Optional[str] = None
    salary_account_number: Optional[str] = None
    salary_ifsc_code: Optional[str] = None
    salary_account_holder_name: Optional[str] = None
    pf_number: Optional[str] = None
    uan_number: Optional[str] = None
    pf_join_date: Optional[date] = None
    esi_number: Optional[str] = None
    current_ctc: Optional[Decimal] = None
    basic_salary: Optional[Decimal] = None
    gross_salary: Optional[Decimal] = None
    net_salary: Optional[Decimal] = None
    
    # Education & Experience
    highest_qualification: Optional[str] = None
    specialization: Optional[str] = None
    university: Optional[str] = None
    year_of_passing: Optional[int] = None
    total_experience_years: Optional[int] = None
    previous_employer: Optional[str] = None
    previous_designation: Optional[str] = None
    
    # Documents & Compliance
    photo_url: Optional[str] = None
    signature_url: Optional[str] = None
    is_background_verified: Optional[bool] = None
    background_verification_date: Optional[date] = None
    background_verification_agency: Optional[str] = None
    is_police_verified: Optional[bool] = None
    police_verification_date: Optional[date] = None
    is_medical_done: Optional[bool] = None
    medical_examination_date: Optional[date] = None
    is_medical_fit: Optional[bool] = None
    
    # Status & Flags
    is_active: Optional[bool] = None
    is_on_probation: Optional[bool] = None
    probation_end_date: Optional[date] = None
    notice_period_days: Optional[int] = None
    
    # Additional Information
    remarks: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None
    languages_known: Optional[str] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class EmployeeResponse(EmployeeBase):
    """Full employee response with all details"""
    id: str
    tenant_id: str
    employee_code: str
    employee_id_display: Optional[str] = None
    user_id: Optional[str] = None
    full_name: str
    age: Optional[int] = None
    date_of_resignation: Optional[date] = None
    date_of_relieving: Optional[date] = None
    last_working_day: Optional[date] = None
    branch_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class EmployeeListItem(BaseModel):
    """Lightweight employee item for list views"""
    id: str
    employee_code: str
    full_name: str
    official_email: Optional[str] = None
    mobile: str
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    designation_id: Optional[str] = None
    designation_name: Optional[str] = None
    employment_type: EmploymentTypeEnum
    employment_status: EmploymentStatusEnum
    date_of_joining: date
    photo_url: Optional[str] = None
    is_active: bool
    reporting_manager_id: Optional[str] = None
    reporting_manager_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class EmployeeCardView(BaseModel):
    """Card view for employee display (dashboard, org chart)"""
    id: str
    employee_code: str
    full_name: str
    designation_name: Optional[str] = None
    department_name: Optional[str] = None
    photo_url: Optional[str] = None
    official_email: Optional[str] = None
    mobile: str
    employment_type: EmploymentTypeEnum
    is_active: bool
    
    class Config:
        from_attributes = True


class PaginatedEmployeeResponse(BaseModel):
    """Paginated employee list response"""
    items: List[EmployeeListItem]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# DASHBOARD & STATS SCHEMAS
# ============================================================================

class EmployeeDashboardStats(BaseModel):
    """Dashboard statistics for employees"""
    total_employees: int
    active_employees: int
    inactive_employees: int
    on_probation: int
    permanent: int
    contract: int
    consultant: int
    intern: int
    new_joiners_this_month: int
    resignations_this_month: int
    upcoming_confirmations: int
    birthday_today: int
    birthday_this_week: int
    birthday_this_month: int


class OrgChartNode(BaseModel):
    """Organization chart node"""
    id: str
    employee_code: str
    full_name: str
    designation_name: Optional[str] = None
    department_name: Optional[str] = None
    photo_url: Optional[str] = None
    reporting_manager_id: Optional[str] = None
    children: List['OrgChartNode'] = []
    
    class Config:
        from_attributes = True


# Update forward reference
OrgChartNode.model_rebuild()


# ============================================================================
# SEARCH PARAMS
# ============================================================================

class EmployeeSearchParams(BaseModel):
    """Search parameters for employee filtering"""
    search: Optional[str] = Field(None, description="Search by name, code, mobile, email")
    department_id: Optional[str] = Field(None, description="Filter by department")
    designation_id: Optional[str] = Field(None, description="Filter by designation")
    employment_type: Optional[EmploymentTypeEnum] = Field(None, description="Filter by employment type")
    employment_status: Optional[EmploymentStatusEnum] = Field(None, description="Filter by status")
    reporting_manager_id: Optional[str] = Field(None, description="Filter by reporting manager")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
