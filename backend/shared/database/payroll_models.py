"""
Payroll Management Database Models
Handles salary structures, payroll processing, statutory compliance, and Form 16
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .connection import Base


# Enums
class ComponentType(str, enum.Enum):
    EARNING = "EARNING"
    DEDUCTION = "DEDUCTION"
    EMPLOYER_CONTRIBUTION = "EMPLOYER_CONTRIBUTION"


class CalculationType(str, enum.Enum):
    FIXED = "FIXED"
    PERCENTAGE_OF_BASIC = "PERCENTAGE_OF_BASIC"
    PERCENTAGE_OF_GROSS = "PERCENTAGE_OF_GROSS"
    PERCENTAGE_OF_CTC = "PERCENTAGE_OF_CTC"
    FORMULA = "FORMULA"


class PayrollStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    APPROVED = "APPROVED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PaymentMode(str, enum.Enum):
    BANK_TRANSFER = "BANK_TRANSFER"
    CHEQUE = "CHEQUE"
    CASH = "CASH"
    UPI = "UPI"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class TaxRegime(str, enum.Enum):
    OLD = "OLD"
    NEW = "NEW"


class StatutoryType(str, enum.Enum):
    PF = "PF"  # Provident Fund
    ESI = "ESI"  # Employee State Insurance
    PT = "PT"  # Professional Tax
    TDS = "TDS"  # Tax Deducted at Source
    LWF = "LWF"  # Labour Welfare Fund


# Model 1: Salary Components Master
class SalaryComponent(Base):
    __tablename__ = "salary_components"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    component_code = Column(String(50), unique=True, nullable=False, index=True)
    component_name = Column(String(200), nullable=False)
    component_type = Column(SQLEnum(ComponentType), nullable=False, index=True)
    calculation_type = Column(SQLEnum(CalculationType), nullable=False)
    
    # Calculation details
    default_value = Column(Numeric(15, 2), default=0.00)
    percentage = Column(Numeric(5, 2))  # For percentage-based calculations
    formula = Column(Text)  # For complex formulas
    
    # Display settings
    display_order = Column(Integer, default=0)
    is_taxable = Column(Boolean, default=True)
    is_part_of_ctc = Column(Boolean, default=True)
    is_statutory = Column(Boolean, default=False)
    statutory_type = Column(SQLEnum(StatutoryType))
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_system_component = Column(Boolean, default=False)  # Cannot be deleted
    description = Column(Text)

    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)


# Model 2: Salary Structure
class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    structure_code = Column(String(50), unique=True, nullable=False, index=True)
    structure_name = Column(String(200), nullable=False)
    
    # Applicable for
    grade_level = Column(String(50))
    department = Column(String(100))
    designation = Column(String(100))
    
    # Validity
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    description = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    components = relationship("SalaryStructureComponent", back_populates="structure")



# Model 3: Salary Structure Components (Junction Table)
class SalaryStructureComponent(Base):
    __tablename__ = "salary_structure_components"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    structure_id = Column(Integer, ForeignKey("salary_structures.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("salary_components.id"), nullable=False, index=True)
    
    # Component configuration for this structure
    calculation_type = Column(SQLEnum(CalculationType), nullable=False)
    default_value = Column(Numeric(15, 2))
    percentage = Column(Numeric(5, 2))
    formula = Column(Text)
    is_mandatory = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    structure = relationship("SalaryStructure", back_populates="components")


# Model 4: Employee Salary Assignment
class EmployeeSalary(Base):
    __tablename__ = "employee_salaries"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    employee_id = Column(Integer, nullable=False, index=True)
    structure_id = Column(Integer, ForeignKey("salary_structures.id"), nullable=False)
    
    # Salary details
    ctc_annual = Column(Numeric(15, 2), nullable=False)
    gross_monthly = Column(Numeric(15, 2), nullable=False)
    net_monthly = Column(Numeric(15, 2), nullable=False)

    
    # Bank details
    bank_name = Column(String(200))
    bank_account_number = Column(String(50))
    bank_ifsc_code = Column(String(20))
    bank_branch = Column(String(200))
    
    # Payment preferences
    payment_mode = Column(SQLEnum(PaymentMode), default=PaymentMode.BANK_TRANSFER)
    
    # Tax settings
    tax_regime = Column(SQLEnum(TaxRegime), default=TaxRegime.OLD)
    pan_number = Column(String(20))
    
    # Validity
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    components = relationship("EmployeeSalaryComponent", back_populates="employee_salary")


# Model 5: Employee Salary Components (Individual component values)
class EmployeeSalaryComponent(Base):
    __tablename__ = "employee_salary_components"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    employee_salary_id = Column(Integer, ForeignKey("employee_salaries.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("salary_components.id"), nullable=False)

    
    # Component values
    monthly_amount = Column(Numeric(15, 2), nullable=False)
    annual_amount = Column(Numeric(15, 2), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    employee_salary = relationship("EmployeeSalary", back_populates="components")


# Model 6: Payroll Run
class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    run_code = Column(String(50), unique=True, nullable=False, index=True)
    run_name = Column(String(200), nullable=False)
    
    # Period details
    payroll_month = Column(Integer, nullable=False)  # 1-12
    payroll_year = Column(Integer, nullable=False)  # YYYY
    pay_date = Column(Date, nullable=False)
    
    # Period range
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    
    # Statistics
    total_employees = Column(Integer, default=0)
    processed_employees = Column(Integer, default=0)
    total_gross = Column(Numeric(15, 2), default=0.00)
    total_deductions = Column(Numeric(15, 2), default=0.00)
    total_net_pay = Column(Numeric(15, 2), default=0.00)

    
    # Status
    status = Column(SQLEnum(PayrollStatus), default=PayrollStatus.DRAFT, index=True)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # Approval
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    approval_remarks = Column(Text)
    
    # Configuration
    include_arrears = Column(Boolean, default=False)
    include_bonus = Column(Boolean, default=False)
    description = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    payslips = relationship("Payslip", back_populates="payroll_run")


# Model 7: Payslip
class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False, index=True)
    employee_id = Column(Integer, nullable=False, index=True)
    payslip_number = Column(String(50), unique=True, nullable=False, index=True)

    
    # Period
    payroll_month = Column(Integer, nullable=False)
    payroll_year = Column(Integer, nullable=False)
    pay_date = Column(Date, nullable=False)
    
    # Employee details (snapshot)
    employee_code = Column(String(50))
    employee_name = Column(String(200))
    designation = Column(String(100))
    department = Column(String(100))
    pan_number = Column(String(20))
    uan_number = Column(String(20))  # Universal Account Number for PF
    esi_number = Column(String(20))
    
    # Attendance details
    days_in_month = Column(Integer, nullable=False)
    days_worked = Column(Numeric(5, 2), nullable=False)
    days_lop = Column(Numeric(5, 2), default=0.00)  # Loss of Pay
    
    # Salary breakdown
    basic_salary = Column(Numeric(15, 2), nullable=False)
    gross_earnings = Column(Numeric(15, 2), nullable=False)
    total_deductions = Column(Numeric(15, 2), nullable=False)
    net_salary = Column(Numeric(15, 2), nullable=False)
    
    # Statutory amounts
    pf_employee = Column(Numeric(15, 2), default=0.00)
    pf_employer = Column(Numeric(15, 2), default=0.00)
    esi_employee = Column(Numeric(15, 2), default=0.00)
    esi_employer = Column(Numeric(15, 2), default=0.00)
    pt_deduction = Column(Numeric(15, 2), default=0.00)
    tds_deduction = Column(Numeric(15, 2), default=0.00)

    
    # Payment details
    payment_mode = Column(SQLEnum(PaymentMode), default=PaymentMode.BANK_TRANSFER)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_date = Column(Date)
    payment_reference = Column(String(100))
    bank_account_number = Column(String(50))
    bank_ifsc_code = Column(String(20))
    
    # Document
    payslip_pdf_url = Column(String(500))
    
    # Status
    is_hold = Column(Boolean, default=False)
    hold_reason = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    payroll_run = relationship("PayrollRun", back_populates="payslips")
    components = relationship("PayslipComponent", back_populates="payslip")


# Model 8: Payslip Components (Detailed breakdown)
class PayslipComponent(Base):
    __tablename__ = "payslip_components"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    payslip_id = Column(Integer, ForeignKey("payslips.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("salary_components.id"), nullable=False)

    
    # Component details (snapshot)
    component_code = Column(String(50), nullable=False)
    component_name = Column(String(200), nullable=False)
    component_type = Column(SQLEnum(ComponentType), nullable=False)
    
    # Amount
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    payslip = relationship("Payslip", back_populates="components")


# Model 9: Statutory Compliance Records
class StatutoryCompliance(Base):
    __tablename__ = "statutory_compliance"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), index=True)
    
    # Period
    compliance_month = Column(Integer, nullable=False)
    compliance_year = Column(Integer, nullable=False)
    
    # Statutory type
    statutory_type = Column(SQLEnum(StatutoryType), nullable=False, index=True)
    
    # Amounts
    employee_contribution = Column(Numeric(15, 2), default=0.00)
    employer_contribution = Column(Numeric(15, 2), default=0.00)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment details
    challan_number = Column(String(100))
    payment_date = Column(Date)
    due_date = Column(Date)

    
    # Status
    is_paid = Column(Boolean, default=False)
    payment_reference = Column(String(100))
    
    # Return filing
    return_filed = Column(Boolean, default=False)
    return_file_date = Column(Date)
    return_acknowledgement = Column(String(100))
    
    # Documents
    challan_pdf_url = Column(String(500))
    return_pdf_url = Column(String(500))
    
    # Remarks
    remarks = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)


# Model 10: Form 16
class Form16(Base):
    __tablename__ = "form16"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    employee_id = Column(Integer, nullable=False, index=True)
    financial_year = Column(String(10), nullable=False, index=True)  # e.g., "2023-24"
    form16_number = Column(String(50), unique=True, nullable=False)
    
    # Employee details (snapshot)
    employee_code = Column(String(50))
    employee_name = Column(String(200))
    pan_number = Column(String(20), nullable=False)
    designation = Column(String(100))

    
    # Employer details
    employer_name = Column(String(200))
    employer_tan = Column(String(20))
    employer_address = Column(Text)
    
    # Part A - TDS Certificate
    total_tds_deposited = Column(Numeric(15, 2), default=0.00)
    
    # Part B - Salary and Tax Details
    gross_salary = Column(Numeric(15, 2), nullable=False)
    exemptions = Column(Numeric(15, 2), default=0.00)
    taxable_salary = Column(Numeric(15, 2), nullable=False)
    
    # Deductions under Chapter VI-A
    deduction_80c = Column(Numeric(15, 2), default=0.00)  # PPF, LIC, ELSS, etc.
    deduction_80d = Column(Numeric(15, 2), default=0.00)  # Medical Insurance
    deduction_80g = Column(Numeric(15, 2), default=0.00)  # Donations
    deduction_80e = Column(Numeric(15, 2), default=0.00)  # Education Loan Interest
    other_deductions = Column(Numeric(15, 2), default=0.00)
    total_deductions = Column(Numeric(15, 2), default=0.00)
    
    # Total Income
    total_income = Column(Numeric(15, 2), nullable=False)
    
    # Tax Computation
    tax_on_total_income = Column(Numeric(15, 2), nullable=False)
    surcharge = Column(Numeric(15, 2), default=0.00)
    education_cess = Column(Numeric(15, 2), default=0.00)
    total_tax_payable = Column(Numeric(15, 2), nullable=False)
    relief_under_89 = Column(Numeric(15, 2), default=0.00)
    net_tax_payable = Column(Numeric(15, 2), nullable=False)

    
    # TDS Details
    tds_deducted = Column(Numeric(15, 2), nullable=False)
    
    # Tax regime
    tax_regime = Column(SQLEnum(TaxRegime), default=TaxRegime.OLD)
    
    # Generation details
    generated_date = Column(Date, nullable=False)
    generated_by = Column(Integer)
    
    # Document
    form16_pdf_url = Column(String(500))
    
    # Status
    is_issued = Column(Boolean, default=False)
    issued_date = Column(Date)
    
    # Digital signature
    is_digitally_signed = Column(Boolean, default=False)
    signature_date = Column(DateTime)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)


# Model 11: Payment Files (Bank transfer files)
class PaymentFile(Base):
    __tablename__ = "payment_files"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False, index=True)
    file_code = Column(String(50), unique=True, nullable=False)

    
    # File details
    file_name = Column(String(200), nullable=False)
    file_format = Column(String(20), nullable=False)  # NEFT, RTGS, CSV, EXCEL
    file_path = Column(String(500))
    file_size = Column(Integer)  # in bytes
    
    # Payment details
    total_records = Column(Integer, default=0)
    total_amount = Column(Numeric(15, 2), default=0.00)
    bank_name = Column(String(200))
    
    # Period
    payment_month = Column(Integer, nullable=False)
    payment_year = Column(Integer, nullable=False)
    payment_date = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    uploaded_to_bank = Column(Boolean, default=False)
    upload_date = Column(DateTime)
    uploaded_by = Column(Integer)
    
    # Bank response
    bank_reference_number = Column(String(100))
    bank_response_date = Column(DateTime)
    bank_response_message = Column(Text)
    
    # Remarks
    remarks = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)
