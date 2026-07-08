"""
Payroll Pydantic Schemas
Request/Response models for payroll management
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# Enums matching database
class ComponentType(str, Enum):
    EARNING = "EARNING"
    DEDUCTION = "DEDUCTION"
    EMPLOYER_CONTRIBUTION = "EMPLOYER_CONTRIBUTION"


class CalculationType(str, Enum):
    FIXED = "FIXED"
    PERCENTAGE_OF_BASIC = "PERCENTAGE_OF_BASIC"
    PERCENTAGE_OF_GROSS = "PERCENTAGE_OF_GROSS"
    PERCENTAGE_OF_CTC = "PERCENTAGE_OF_CTC"
    FORMULA = "FORMULA"


class PayrollStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    APPROVED = "APPROVED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PaymentMode(str, Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    CHEQUE = "CHEQUE"
    CASH = "CASH"
    UPI = "UPI"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"



class TaxRegime(str, Enum):
    OLD = "OLD"
    NEW = "NEW"


class StatutoryType(str, Enum):
    PF = "PF"
    ESI = "ESI"
    PT = "PT"
    TDS = "TDS"
    LWF = "LWF"


# ============ Salary Component Schemas ============

class SalaryComponentBase(BaseModel):
    component_code: str = Field(..., max_length=50)
    component_name: str = Field(..., max_length=200)
    component_type: ComponentType
    calculation_type: CalculationType
    default_value: Optional[Decimal] = Field(default=0.00)
    percentage: Optional[Decimal] = Field(default=None)
    formula: Optional[str] = None
    display_order: int = 0
    is_taxable: bool = True
    is_part_of_ctc: bool = True
    is_statutory: bool = False
    statutory_type: Optional[StatutoryType] = None
    is_active: bool = True
    description: Optional[str] = None


class SalaryComponentCreate(SalaryComponentBase):
    tenant_id: int


class SalaryComponentUpdate(BaseModel):
    component_name: Optional[str] = None
    component_type: Optional[ComponentType] = None
    calculation_type: Optional[CalculationType] = None
    default_value: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    formula: Optional[str] = None

    display_order: Optional[int] = None
    is_taxable: Optional[bool] = None
    is_part_of_ctc: Optional[bool] = None
    is_statutory: Optional[bool] = None
    statutory_type: Optional[StatutoryType] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class SalaryComponentResponse(SalaryComponentBase):
    id: int
    tenant_id: int
    is_system_component: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SalaryComponentListResponse(BaseModel):
    items: List[SalaryComponentResponse]
    total: int
    page: int
    page_size: int


# ============ Salary Structure Schemas ============

class SalaryStructureComponentData(BaseModel):
    component_id: int
    calculation_type: CalculationType
    default_value: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    formula: Optional[str] = None
    is_mandatory: bool = True
    display_order: int = 0


class SalaryStructureBase(BaseModel):
    structure_code: str = Field(..., max_length=50)
    structure_name: str = Field(..., max_length=200)
    grade_level: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True
    is_default: bool = False
    description: Optional[str] = None


class SalaryStructureCreate(SalaryStructureBase):
    tenant_id: int
    components: List[SalaryStructureComponentData] = []


class SalaryStructureUpdate(BaseModel):
    structure_name: Optional[str] = None
    grade_level: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    description: Optional[str] = None
    components: Optional[List[SalaryStructureComponentData]] = None


class SalaryStructureResponse(SalaryStructureBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    components: List[dict] = []

    class Config:
        from_attributes = True


class SalaryStructureListResponse(BaseModel):
    items: List[SalaryStructureResponse]
    total: int
    page: int
    page_size: int


# ============ Employee Salary Schemas ============

class EmployeeSalaryComponentData(BaseModel):
    component_id: int
    monthly_amount: Decimal
    annual_amount: Decimal



class EmployeeSalaryBase(BaseModel):
    employee_id: int
    structure_id: int
    ctc_annual: Decimal
    gross_monthly: Decimal
    net_monthly: Decimal
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    bank_branch: Optional[str] = None
    payment_mode: PaymentMode = PaymentMode.BANK_TRANSFER
    tax_regime: TaxRegime = TaxRegime.OLD
    pan_number: Optional[str] = None
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True


class EmployeeSalaryCreate(EmployeeSalaryBase):
    tenant_id: int
    components: List[EmployeeSalaryComponentData] = []


class EmployeeSalaryUpdate(BaseModel):
    structure_id: Optional[int] = None
    ctc_annual: Optional[Decimal] = None
    gross_monthly: Optional[Decimal] = None
    net_monthly: Optional[Decimal] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    bank_branch: Optional[str] = None
    payment_mode: Optional[PaymentMode] = None
    tax_regime: Optional[TaxRegime] = None
    pan_number: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None


class EmployeeSalaryResponse(EmployeeSalaryBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    components: List[dict] = []

    class Config:
        from_attributes = True



class EmployeeSalaryListResponse(BaseModel):
    items: List[EmployeeSalaryResponse]
    total: int
    page: int
    page_size: int


# ============ Payroll Run Schemas ============

class PayrollRunBase(BaseModel):
    run_name: str = Field(..., max_length=200)
    payroll_month: int = Field(..., ge=1, le=12)
    payroll_year: int
    pay_date: date
    period_start_date: date
    period_end_date: date
    include_arrears: bool = False
    include_bonus: bool = False
    description: Optional[str] = None


class PayrollRunCreate(PayrollRunBase):
    tenant_id: int


class PayrollRunUpdate(BaseModel):
    run_name: Optional[str] = None
    pay_date: Optional[date] = None
    description: Optional[str] = None


class PayrollRunResponse(PayrollRunBase):
    id: int
    tenant_id: int
    run_code: str
    total_employees: int
    processed_employees: int
    total_gross: Decimal
    total_deductions: Decimal
    total_net_pay: Decimal
    status: PayrollStatus
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PayrollRunListResponse(BaseModel):
    items: List[PayrollRunResponse]
    total: int
    page: int
    page_size: int



class PayrollRunProcessRequest(BaseModel):
    payroll_run_id: int
    employee_ids: Optional[List[int]] = None  # If None, process all active employees


class PayrollRunApproveRequest(BaseModel):
    approval_remarks: Optional[str] = None


# ============ Payslip Schemas ============

class PayslipBase(BaseModel):
    employee_id: int
    payroll_month: int
    payroll_year: int
    pay_date: date
    days_in_month: int
    days_worked: Decimal
    days_lop: Decimal = Decimal("0.00")
    basic_salary: Decimal
    gross_earnings: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    pf_employee: Decimal = Decimal("0.00")
    pf_employer: Decimal = Decimal("0.00")
    esi_employee: Decimal = Decimal("0.00")
    esi_employer: Decimal = Decimal("0.00")
    pt_deduction: Decimal = Decimal("0.00")
    tds_deduction: Decimal = Decimal("0.00")
    payment_mode: PaymentMode = PaymentMode.BANK_TRANSFER
    is_hold: bool = False
    hold_reason: Optional[str] = None


class PayslipResponse(PayslipBase):
    id: int
    tenant_id: int
    payroll_run_id: int
    payslip_number: str
    employee_code: Optional[str]
    employee_name: Optional[str]
    designation: Optional[str]
    department: Optional[str]
    payment_status: PaymentStatus
    payment_date: Optional[date]
    payment_reference: Optional[str]
    payslip_pdf_url: Optional[str]
    created_at: datetime
    components: List[dict] = []

    class Config:
        from_attributes = True


class PayslipListResponse(BaseModel):
    items: List[PayslipResponse]
    total: int
    page: int
    page_size: int



class PayslipDownloadRequest(BaseModel):
    payslip_id: int
    include_watermark: bool = False


# ============ Statutory Compliance Schemas ============

class StatutoryComplianceBase(BaseModel):
    compliance_month: int = Field(..., ge=1, le=12)
    compliance_year: int
    statutory_type: StatutoryType
    employee_contribution: Decimal = Decimal("0.00")
    employer_contribution: Decimal = Decimal("0.00")
    total_amount: Decimal
    challan_number: Optional[str] = None
    payment_date: Optional[date] = None
    due_date: Optional[date] = None
    is_paid: bool = False
    return_filed: bool = False
    remarks: Optional[str] = None


class StatutoryComplianceCreate(StatutoryComplianceBase):
    tenant_id: int
    payroll_run_id: Optional[int] = None


class StatutoryComplianceUpdate(BaseModel):
    challan_number: Optional[str] = None
    payment_date: Optional[date] = None
    is_paid: Optional[bool] = None
    return_filed: Optional[bool] = None
    return_file_date: Optional[date] = None
    return_acknowledgement: Optional[str] = None
    remarks: Optional[str] = None


class StatutoryComplianceResponse(StatutoryComplianceBase):
    id: int
    tenant_id: int
    payroll_run_id: Optional[int]
    return_file_date: Optional[date]
    return_acknowledgement: Optional[str]
    challan_pdf_url: Optional[str]
    return_pdf_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StatutoryComplianceListResponse(BaseModel):
    items: List[StatutoryComplianceResponse]
    total: int
    page: int
    page_size: int



class StatutoryReportRequest(BaseModel):
    statutory_type: StatutoryType
    month: int = Field(..., ge=1, le=12)
    year: int
    format: str = "PDF"  # PDF, EXCEL, CSV


# ============ Form 16 Schemas ============

class Form16Base(BaseModel):
    employee_id: int
    financial_year: str = Field(..., max_length=10)
    pan_number: str = Field(..., max_length=20)
    gross_salary: Decimal
    exemptions: Decimal = Decimal("0.00")
    taxable_salary: Decimal
    deduction_80c: Decimal = Decimal("0.00")
    deduction_80d: Decimal = Decimal("0.00")
    deduction_80g: Decimal = Decimal("0.00")
    deduction_80e: Decimal = Decimal("0.00")
    other_deductions: Decimal = Decimal("0.00")
    total_deductions: Decimal = Decimal("0.00")
    total_income: Decimal
    tax_on_total_income: Decimal
    surcharge: Decimal = Decimal("0.00")
    education_cess: Decimal = Decimal("0.00")
    total_tax_payable: Decimal
    relief_under_89: Decimal = Decimal("0.00")
    net_tax_payable: Decimal
    total_tds_deposited: Decimal = Decimal("0.00")
    tds_deducted: Decimal
    tax_regime: TaxRegime = TaxRegime.OLD


class Form16Create(Form16Base):
    tenant_id: int


class Form16Response(Form16Base):
    id: int
    tenant_id: int
    form16_number: str
    employee_code: Optional[str]
    employee_name: Optional[str]
    designation: Optional[str]
    employer_name: Optional[str]
    employer_tan: Optional[str]
    generated_date: date
    is_issued: bool
    issued_date: Optional[date]
    is_digitally_signed: bool
    form16_pdf_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class Form16ListResponse(BaseModel):
    items: List[Form16Response]
    total: int
    page: int
    page_size: int


class Form16GenerateRequest(BaseModel):
    financial_year: str
    employee_ids: Optional[List[int]] = None  # If None, generate for all employees


class Form16IssueRequest(BaseModel):
    form16_id: int
    issue_to_email: bool = True


# ============ Payment File Schemas ============

class PaymentFileBase(BaseModel):
    payroll_run_id: int
    file_name: str = Field(..., max_length=200)
    file_format: str = Field(..., max_length=20)
    total_records: int
    total_amount: Decimal
    bank_name: Optional[str] = None
    payment_month: int = Field(..., ge=1, le=12)
    payment_year: int
    payment_date: date
    remarks: Optional[str] = None


class PaymentFileCreate(PaymentFileBase):
    tenant_id: int


class PaymentFileUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    uploaded_to_bank: Optional[bool] = None
    bank_reference_number: Optional[str] = None
    bank_response_message: Optional[str] = None
    remarks: Optional[str] = None


class PaymentFileResponse(PaymentFileBase):
    id: int
    tenant_id: int
    file_code: str
    file_path: Optional[str]
    file_size: Optional[int]
    status: PaymentStatus
    uploaded_to_bank: bool
    upload_date: Optional[datetime]
    uploaded_by: Optional[int]
    bank_reference_number: Optional[str]
    bank_response_date: Optional[datetime]
    bank_response_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class PaymentFileListResponse(BaseModel):
    items: List[PaymentFileResponse]
    total: int
    page: int
    page_size: int


class PaymentFileGenerateRequest(BaseModel):
    payroll_run_id: int
    file_format: str = "NEFT"  # NEFT, RTGS, CSV, EXCEL
    bank_name: Optional[str] = None
    include_employees: Optional[List[int]] = None


class PaymentFileDownloadRequest(BaseModel):
    payment_file_id: int


# ============ Dashboard & Statistics Schemas ============

class PayrollDashboardStats(BaseModel):
    total_employees: int
    active_salary_structures: int
    pending_payroll_runs: int
    current_month_processed: bool
    total_payroll_this_month: Decimal
    total_statutory_pending: Decimal
    pending_form16_count: int
    pending_payment_files: int


class PayrollSummary(BaseModel):
    month: int
    year: int
    total_employees: int
    total_gross: Decimal
    total_deductions: Decimal
    total_net: Decimal
    pf_total: Decimal
    esi_total: Decimal
    pt_total: Decimal
    tds_total: Decimal


class EmployeeSalaryBreakdown(BaseModel):
    employee_id: int
    employee_code: str
    employee_name: str
    ctc_annual: Decimal
    gross_monthly: Decimal
    net_monthly: Decimal
    earnings: List[dict]
    deductions: List[dict]
    employer_contributions: List[dict]


# ============ Utility Schemas ============

class BulkOperationResponse(BaseModel):
    success_count: int
    failure_count: int
    errors: List[dict] = []
    message: str
