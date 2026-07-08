/**
 * Payroll Type Definitions
 * TypeScript types for payroll management module
 */

// ============ Enums ============

export enum ComponentType {
  EARNING = 'EARNING',
  DEDUCTION = 'DEDUCTION',
  EMPLOYER_CONTRIBUTION = 'EMPLOYER_CONTRIBUTION',
}

export enum CalculationType {
  FIXED = 'FIXED',
  PERCENTAGE_OF_BASIC = 'PERCENTAGE_OF_BASIC',
  PERCENTAGE_OF_GROSS = 'PERCENTAGE_OF_GROSS',
  PERCENTAGE_OF_CTC = 'PERCENTAGE_OF_CTC',
  FORMULA = 'FORMULA',
}

export enum PayrollStatus {
  DRAFT = 'DRAFT',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  APPROVED = 'APPROVED',
  PAID = 'PAID',
  CANCELLED = 'CANCELLED',
}

export enum PaymentMode {
  BANK_TRANSFER = 'BANK_TRANSFER',
  CHEQUE = 'CHEQUE',
  CASH = 'CASH',
  UPI = 'UPI',
}

export enum PaymentStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  REVERSED = 'REVERSED',
}

export enum TaxRegime {
  OLD = 'OLD',
  NEW = 'NEW',
}

export enum StatutoryType {
  PF = 'PF',
  ESI = 'ESI',
  PT = 'PT',
  TDS = 'TDS',
  LWF = 'LWF',
}

// ============ Interfaces ============

// Salary Component
export interface SalaryComponent {
  id: number;
  tenant_id: number;
  component_code: string;
  component_name: string;
  component_type: ComponentType;
  calculation_type: CalculationType;
  default_value: number;
  percentage?: number;
  formula?: string;
  display_order: number;
  is_taxable: boolean;
  is_part_of_ctc: boolean;
  is_statutory: boolean;
  statutory_type?: StatutoryType;
  is_active: boolean;
  is_system_component: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface SalaryComponentCreate {
  component_code: string;
  component_name: string;
  component_type: ComponentType;
  calculation_type: CalculationType;
  default_value?: number;
  percentage?: number;
  formula?: string;
  display_order?: number;
  is_taxable?: boolean;
  is_part_of_ctc?: boolean;
  is_statutory?: boolean;
  statutory_type?: StatutoryType;
  is_active?: boolean;
  description?: string;
}

export interface SalaryComponentUpdate {
  component_name?: string;
  component_type?: ComponentType;
  calculation_type?: CalculationType;
  default_value?: number;
  percentage?: number;
  formula?: string;
  display_order?: number;
  is_taxable?: boolean;
  is_part_of_ctc?: boolean;
  is_statutory?: boolean;
  statutory_type?: StatutoryType;
  is_active?: boolean;
  description?: string;
}

// Salary Structure
export interface SalaryStructureComponentData {
  component_id: number;
  calculation_type: CalculationType;
  default_value?: number;
  percentage?: number;
  formula?: string;
  is_mandatory: boolean;
  display_order: number;
}

export interface SalaryStructure {
  id: number;
  tenant_id: number;
  structure_code: string;
  structure_name: string;
  grade_level?: string;
  department?: string;
  designation?: string;
  effective_from: string;
  effective_to?: string;
  is_active: boolean;
  is_default: boolean;
  description?: string;
  components: any[];
  created_at: string;
  updated_at: string;
}

export interface SalaryStructureCreate {
  structure_code: string;
  structure_name: string;
  grade_level?: string;
  department?: string;
  designation?: string;
  effective_from: string;
  effective_to?: string;
  is_active?: boolean;
  is_default?: boolean;
  description?: string;
  components: SalaryStructureComponentData[];
}

// Employee Salary
export interface EmployeeSalaryComponentData {
  component_id: number;
  monthly_amount: number;
  annual_amount: number;
}

export interface EmployeeSalary {
  id: number;
  tenant_id: number;
  employee_id: number;
  structure_id: number;
  ctc_annual: number;
  gross_monthly: number;
  net_monthly: number;
  bank_name?: string;
  bank_account_number?: string;
  bank_ifsc_code?: string;
  bank_branch?: string;
  payment_mode: PaymentMode;
  tax_regime: TaxRegime;
  pan_number?: string;
  effective_from: string;
  effective_to?: string;
  is_active: boolean;
  components: any[];
  created_at: string;
  updated_at: string;
}

export interface EmployeeSalaryCreate {
  employee_id: number;
  structure_id: number;
  ctc_annual: number;
  gross_monthly: number;
  net_monthly: number;
  bank_name?: string;
  bank_account_number?: string;
  bank_ifsc_code?: string;
  bank_branch?: string;
  payment_mode?: PaymentMode;
  tax_regime?: TaxRegime;
  pan_number?: string;
  effective_from: string;
  effective_to?: string;
  is_active?: boolean;
  components: EmployeeSalaryComponentData[];
}

// Payroll Run
export interface PayrollRun {
  id: number;
  tenant_id: number;
  run_code: string;
  run_name: string;
  payroll_month: number;
  payroll_year: number;
  pay_date: string;
  period_start_date: string;
  period_end_date: string;
  total_employees: number;
  processed_employees: number;
  total_gross: number;
  total_deductions: number;
  total_net_pay: number;
  status: PayrollStatus;
  processing_started_at?: string;
  processing_completed_at?: string;
  approved_by?: number;
  approved_at?: string;
  approval_remarks?: string;
  include_arrears: boolean;
  include_bonus: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface PayrollRunCreate {
  run_name: string;
  payroll_month: number;
  payroll_year: number;
  pay_date: string;
  period_start_date: string;
  period_end_date: string;
  include_arrears?: boolean;
  include_bonus?: boolean;
  description?: string;
}

export interface PayrollRunProcessRequest {
  payroll_run_id: number;
  employee_ids?: number[];
}

export interface PayrollRunApproveRequest {
  approval_remarks?: string;
}

// Payslip
export interface Payslip {
  id: number;
  tenant_id: number;
  payroll_run_id: number;
  employee_id: number;
  payslip_number: string;
  payroll_month: number;
  payroll_year: number;
  pay_date: string;
  employee_code?: string;
  employee_name?: string;
  designation?: string;
  department?: string;
  pan_number?: string;
  uan_number?: string;
  esi_number?: string;
  days_in_month: number;
  days_worked: number;
  days_lop: number;
  basic_salary: number;
  gross_earnings: number;
  total_deductions: number;
  net_salary: number;
  pf_employee: number;
  pf_employer: number;
  esi_employee: number;
  esi_employer: number;
  pt_deduction: number;
  tds_deduction: number;
  payment_mode: PaymentMode;
  payment_status: PaymentStatus;
  payment_date?: string;
  payment_reference?: string;
  bank_account_number?: string;
  bank_ifsc_code?: string;
  payslip_pdf_url?: string;
  is_hold: boolean;
  hold_reason?: string;
  components: any[];
  created_at: string;
}

// Statutory Compliance
export interface StatutoryCompliance {
  id: number;
  tenant_id: number;
  payroll_run_id?: number;
  compliance_month: number;
  compliance_year: number;
  statutory_type: StatutoryType;
  employee_contribution: number;
  employer_contribution: number;
  total_amount: number;
  challan_number?: string;
  payment_date?: string;
  due_date?: string;
  is_paid: boolean;
  return_filed: boolean;
  return_file_date?: string;
  return_acknowledgement?: string;
  challan_pdf_url?: string;
  return_pdf_url?: string;
  remarks?: string;
  created_at: string;
  updated_at: string;
}

// Form 16
export interface Form16 {
  id: number;
  tenant_id: number;
  employee_id: number;
  financial_year: string;
  form16_number: string;
  employee_code?: string;
  employee_name?: string;
  pan_number: string;
  designation?: string;
  employer_name?: string;
  employer_tan?: string;
  gross_salary: number;
  exemptions: number;
  taxable_salary: number;
  deduction_80c: number;
  deduction_80d: number;
  deduction_80g: number;
  deduction_80e: number;
  other_deductions: number;
  total_deductions: number;
  total_income: number;
  tax_on_total_income: number;
  surcharge: number;
  education_cess: number;
  total_tax_payable: number;
  relief_under_89: number;
  net_tax_payable: number;
  total_tds_deposited: number;
  tds_deducted: number;
  tax_regime: TaxRegime;
  generated_date: string;
  is_issued: boolean;
  issued_date?: string;
  is_digitally_signed: boolean;
  form16_pdf_url?: string;
  created_at: string;
  updated_at: string;
}

// Payment File
export interface PaymentFile {
  id: number;
  tenant_id: number;
  payroll_run_id: number;
  file_code: string;
  file_name: string;
  file_format: string;
  file_path?: string;
  file_size?: number;
  total_records: number;
  total_amount: number;
  bank_name?: string;
  payment_month: number;
  payment_year: number;
  payment_date: string;
  status: PaymentStatus;
  uploaded_to_bank: boolean;
  upload_date?: string;
  uploaded_by?: number;
  bank_reference_number?: string;
  bank_response_date?: string;
  bank_response_message?: string;
  remarks?: string;
  created_at: string;
  updated_at: string;
}

// Dashboard & Statistics
export interface PayrollDashboardStats {
  total_employees: number;
  active_salary_structures: number;
  pending_payroll_runs: number;
  current_month_processed: boolean;
  total_payroll_this_month: number;
  total_statutory_pending: number;
  pending_form16_count: number;
  pending_payment_files: number;
}

export interface PayrollSummary {
  month: number;
  year: number;
  total_employees: number;
  total_gross: number;
  total_deductions: number;
  total_net: number;
  pf_total: number;
  esi_total: number;
  pt_total: number;
  tds_total: number;
}

export interface EmployeeSalaryBreakdown {
  employee_id: number;
  employee_code: string;
  employee_name: string;
  ctc_annual: number;
  gross_monthly: number;
  net_monthly: number;
  earnings: any[];
  deductions: any[];
  employer_contributions: any[];
}

// List Response Interfaces
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export type SalaryComponentListResponse = PaginatedResponse<SalaryComponent>;
export type SalaryStructureListResponse = PaginatedResponse<SalaryStructure>;
export type EmployeeSalaryListResponse = PaginatedResponse<EmployeeSalary>;
export type PayrollRunListResponse = PaginatedResponse<PayrollRun>;
export type PayslipListResponse = PaginatedResponse<Payslip>;
export type StatutoryComplianceListResponse = PaginatedResponse<StatutoryCompliance>;
export type Form16ListResponse = PaginatedResponse<Form16>;
export type PaymentFileListResponse = PaginatedResponse<PaymentFile>;

// Utility Types
export interface PayrollFilterParams {
  component_type?: ComponentType;
  is_active?: boolean;
  is_statutory?: boolean;
  status?: PayrollStatus;
  year?: number;
  month?: number;
  employee_id?: number;
  search?: string;
  page?: number;
  page_size?: number;
}
