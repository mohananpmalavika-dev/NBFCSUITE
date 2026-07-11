/**
 * Exit Management TypeScript Types
 * Types for Resignation, Clearance, Settlement & Exit Documents
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum ResignationType {
  VOLUNTARY = 'voluntary',
  INVOLUNTARY = 'involuntary',
  RETIREMENT = 'retirement',
  ABSCONDING = 'absconding',
  END_OF_CONTRACT = 'end_of_contract',
  MUTUAL_CONSENT = 'mutual_consent'
}

export enum ResignationStatus {
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  WITHDRAWN = 'withdrawn',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum ClearanceStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  NOT_APPLICABLE = 'not_applicable',
  WAIVED = 'waived'
}

export enum SettlementStatus {
  PENDING = 'pending',
  CALCULATED = 'calculated',
  APPROVED = 'approved',
  PROCESSING = 'processing',
  PAID = 'paid',
  ON_HOLD = 'on_hold',
  REJECTED = 'rejected'
}

export enum SettlementComponentType {
  SALARY = 'salary',
  LEAVE_ENCASHMENT = 'leave_encashment',
  NOTICE_PAY = 'notice_pay',
  BONUS = 'bonus',
  GRATUITY = 'gratuity',
  REIMBURSEMENT = 'reimbursement',
  RECOVERY = 'recovery',
  OTHER = 'other'
}

export enum ExitDocumentType {
  RESIGNATION_LETTER = 'resignation_letter',
  ACCEPTANCE_LETTER = 'acceptance_letter',
  EXPERIENCE_LETTER = 'experience_letter',
  RELIEVING_LETTER = 'relieving_letter',
  SERVICE_CERTIFICATE = 'service_certificate',
  NOC = 'noc',
  CLEARANCE_FORM = 'clearance_form',
  FNF_STATEMENT = 'fnf_statement',
  FORM_16 = 'form_16',
  PF_WITHDRAWAL = 'pf_withdrawal',
  GRATUITY_FORM = 'gratuity_form',
  OTHER = 'other'
}

// ============================================================================
// RESIGNATION TYPES
// ============================================================================

export interface Resignation {
  id: string;
  tenant_id: string;
  resignation_code: string;
  employee_id: string;
  resignation_type: ResignationType;
  resignation_date: string;
  last_working_date: string;
  actual_last_working_date?: string;
  notice_period_days: number;
  notice_period_served?: number;
  is_notice_period_waived: boolean;
  notice_waiver_reason?: string;
  status: ResignationStatus;
  
  reason_category?: string;
  reason_details: string;
  feedback?: string;
  
  // Workflow
  reporting_manager_id?: string;
  manager_reviewed_date?: string;
  manager_comments?: string;
  manager_recommendation?: string;
  
  hr_reviewer_id?: string;
  hr_reviewed_date?: string;
  hr_comments?: string;
  
  approved_by_id?: string;
  approved_date?: string;
  approval_comments?: string;
  
  rejected_date?: string;
  rejection_reason?: string;
  withdrawn_date?: string;
  withdrawal_reason?: string;
  
  // Counter offer
  counter_offer_made: boolean;
  counter_offer_details?: string;
  counter_offer_accepted?: boolean;
  
  // Exit interview
  exit_interview_scheduled: boolean;
  exit_interview_date?: string;
  exit_interview_conducted_by_id?: string;
  exit_interview_notes?: string;
  
  // Handover
  handover_completed: boolean;
  handover_to_employee_id?: string;
  handover_notes?: string;
  handover_document_path?: string;
  
  // Additional
  re_employment_eligible: boolean;
  blacklist_flag: boolean;
  blacklist_reason?: string;
  
  resignation_letter_path?: string;
  supporting_documents?: string;
  
  // Audit
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface ResignationCreate {
  employee_id: string;
  resignation_type?: ResignationType;
  resignation_date: string;
  last_working_date: string;
  notice_period_days?: number;
  reason_category?: string;
  reason_details: string;
  feedback?: string;
  resignation_letter_path?: string;
  supporting_documents?: string;
}

export interface ResignationUpdate {
  resignation_type?: ResignationType;
  last_working_date?: string;
  actual_last_working_date?: string;
  notice_period_days?: number;
  notice_period_served?: number;
  is_notice_period_waived?: boolean;
  notice_waiver_reason?: string;
  reason_category?: string;
  reason_details?: string;
  feedback?: string;
  resignation_letter_path?: string;
  supporting_documents?: string;
}

export interface ManagerReview {
  manager_comments: string;
  manager_recommendation: string; // approve, reject, counter_offer
  counter_offer_details?: string;
}

export interface HRReview {
  hr_comments: string;
  re_employment_eligible?: boolean;
  blacklist_flag?: boolean;
  blacklist_reason?: string;
}

export interface ResignationApproval {
  approval_comments: string;
  actual_last_working_date: string;
}

export interface ResignationRejection {
  rejection_reason: string;
}

export interface ResignationWithdrawal {
  withdrawal_reason: string;
}

export interface ExitInterview {
  exit_interview_date: string;
  exit_interview_notes: string;
  feedback?: string;
}

export interface Handover {
  handover_to_employee_id: string;
  handover_notes: string;
  handover_document_path?: string;
}

// ============================================================================
// CLEARANCE TYPES
// ============================================================================

export interface ExitClearance {
  id: string;
  tenant_id: string;
  resignation_id: string;
  clearance_from: string;
  clearance_type: string;
  description?: string;
  checklist_items?: string;
  status: ClearanceStatus;
  is_mandatory: boolean;
  
  assigned_to_id?: string;
  assigned_date?: string;
  
  pending_items?: string;
  
  cleared_by_id?: string;
  cleared_date?: string;
  clearance_remarks?: string;
  
  supporting_documents?: string;
  
  due_date?: string;
  depends_on_clearance_id?: string;
  
  is_overdue: boolean;
  escalated: boolean;
  escalation_level: number;
  
  // Audit
  created_at: string;
  updated_at: string;
}

export interface ClearanceCreate {
  resignation_id: string;
  clearance_from: string;
  clearance_type: string;
  description?: string;
  checklist_items?: string;
  is_mandatory?: boolean;
  assigned_to_id?: string;
  due_date?: string;
  depends_on_clearance_id?: string;
}

export interface ClearanceUpdate {
  clearance_from?: string;
  clearance_type?: string;
  description?: string;
  status?: ClearanceStatus;
  checklist_items?: string;
  pending_items?: string;
  assigned_to_id?: string;
  due_date?: string;
  is_mandatory?: boolean;
  depends_on_clearance_id?: string;
}

export interface ClearanceComplete {
  clearance_remarks: string;
  supporting_documents?: string;
}

// ============================================================================
// SETTLEMENT TYPES
// ============================================================================

export interface SettlementComponent {
  id: string;
  settlement_id: string;
  component_type: SettlementComponentType;
  component_name: string;
  description?: string;
  amount: number;
  is_deduction: boolean;
  calculation_basis?: string;
  quantity?: number;
  rate?: number;
  is_taxable: boolean;
  tax_amount: number;
  remarks?: string;
  
  // Audit
  created_at: string;
  updated_at: string;
}

export interface SettlementComponentCreate {
  settlement_id: string;
  component_type: SettlementComponentType;
  component_name: string;
  description?: string;
  amount: number;
  is_deduction?: boolean;
  calculation_basis?: string;
  quantity?: number;
  rate?: number;
  is_taxable?: boolean;
  tax_amount?: number;
  remarks?: string;
}

export interface SettlementComponentUpdate {
  component_name?: string;
  description?: string;
  amount?: number;
  is_deduction?: boolean;
  calculation_basis?: string;
  quantity?: number;
  rate?: number;
  is_taxable?: boolean;
  tax_amount?: number;
  remarks?: string;
}

export interface ExitSettlement {
  id: string;
  tenant_id: string;
  settlement_code: string;
  resignation_id: string;
  employee_id: string;
  status: SettlementStatus;
  
  settlement_from_date: string;
  settlement_to_date: string;
  
  // Calculation details
  basic_salary_days?: number;
  basic_salary_amount: number;
  
  total_leave_balance: number;
  encashable_leaves: number;
  leave_encashment_amount: number;
  
  notice_period_shortfall_days: number;
  notice_pay_recovery: number;
  
  years_of_service?: number;
  gratuity_eligible: boolean;
  gratuity_amount: number;
  
  bonus_amount: number;
  incentive_amount: number;
  
  pending_reimbursement_amount: number;
  
  loan_recovery: number;
  advance_recovery: number;
  asset_loss_recovery: number;
  other_recovery: number;
  recovery_remarks?: string;
  
  gross_payable: number;
  total_deductions: number;
  net_payable: number;
  
  tds_amount: number;
  professional_tax: number;
  
  // Workflow
  calculated_by_id?: string;
  calculated_date?: string;
  calculation_remarks?: string;
  
  approved_by_id?: string;
  approved_date?: string;
  approval_remarks?: string;
  
  finance_processor_id?: string;
  finance_processed_date?: string;
  finance_remarks?: string;
  
  // Payment
  payment_date?: string;
  payment_mode?: string;
  payment_reference?: string;
  bank_account_number?: string;
  bank_name?: string;
  bank_ifsc_code?: string;
  
  // Hold/Rejection
  hold_reason?: string;
  hold_until_date?: string;
  rejected_date?: string;
  rejection_reason?: string;
  
  fnf_statement_path?: string;
  supporting_documents?: string;
  
  // Audit
  created_at: string;
  updated_at: string;
}

export interface SettlementCreate {
  resignation_id: string;
  employee_id: string;
  settlement_from_date: string;
  settlement_to_date: string;
}

export interface SettlementCalculation {
  // Salary
  basic_salary_days?: number;
  basic_salary_amount?: number;
  
  // Leave
  total_leave_balance?: number;
  encashable_leaves?: number;
  leave_encashment_amount?: number;
  
  // Notice period
  notice_period_shortfall_days?: number;
  notice_pay_recovery?: number;
  
  // Gratuity
  years_of_service?: number;
  gratuity_eligible?: boolean;
  gratuity_amount?: number;
  
  // Bonus
  bonus_amount?: number;
  incentive_amount?: number;
  
  // Reimbursements
  pending_reimbursement_amount?: number;
  
  // Recoveries
  loan_recovery?: number;
  advance_recovery?: number;
  asset_loss_recovery?: number;
  other_recovery?: number;
  recovery_remarks?: string;
  
  // Tax
  tds_amount?: number;
  professional_tax?: number;
  
  calculation_remarks?: string;
}

export interface SettlementApproval {
  approval_remarks: string;
}

export interface SettlementPayment {
  payment_date: string;
  payment_mode: string; // bank_transfer, cheque, cash
  payment_reference: string;
  bank_account_number?: string;
  bank_name?: string;
  bank_ifsc_code?: string;
  finance_remarks?: string;
}

export interface SettlementHold {
  hold_reason: string;
  hold_until_date?: string;
}

// ============================================================================
// DOCUMENT TYPES
// ============================================================================

export interface ExitDocument {
  id: string;
  tenant_id: string;
  document_code: string;
  resignation_id: string;
  employee_id: string;
  document_type: ExitDocumentType;
  document_name: string;
  description?: string;
  
  template_name?: string;
  template_version?: string;
  
  document_content?: string;
  document_path?: string;
  document_url?: string;
  
  is_generated: boolean;
  is_approved: boolean;
  is_issued: boolean;
  
  generated_by_id?: string;
  generated_date?: string;
  
  approved_by_id?: string;
  approved_date?: string;
  approval_remarks?: string;
  
  issued_by_id?: string;
  issued_date?: string;
  issue_remarks?: string;
  
  document_number?: string;
  issue_place?: string;
  validity_date?: string;
  
  is_digitally_signed: boolean;
  digital_signature_info?: string;
  
  delivery_mode?: string;
  delivered_date?: string;
  recipient_email?: string;
  recipient_address?: string;
  tracking_number?: string;
  
  acknowledged_by_employee: boolean;
  acknowledgment_date?: string;
  
  // Audit
  created_at: string;
  updated_at: string;
}

export interface DocumentCreate {
  resignation_id: string;
  employee_id: string;
  document_type: ExitDocumentType;
  document_name: string;
  description?: string;
  template_name?: string;
  document_content?: string;
  document_path?: string;
  document_url?: string;
}

export interface DocumentGenerate {
  document_type: ExitDocumentType;
  template_name?: string;
  template_version?: string;
  document_number?: string;
  issue_place?: string;
  validity_date?: string;
}

export interface DocumentApproval {
  approval_remarks: string;
}

export interface DocumentIssuance {
  issue_remarks: string;
  delivery_mode: string; // email, hard_copy, courier, portal
  recipient_email?: string;
  recipient_address?: string;
}

// ============================================================================
// FILTER & QUERY TYPES
// ============================================================================

export interface ResignationFilters {
  employee_id?: string;
  resignation_type?: ResignationType;
  status?: ResignationStatus;
  reporting_manager_id?: string;
  resignation_date_from?: string;
  resignation_date_to?: string;
  last_working_date_from?: string;
  last_working_date_to?: string;
  search?: string;
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ClearanceFilters {
  resignation_id?: string;
  status?: ClearanceStatus;
  assigned_to_id?: string;
  clearance_from?: string;
  is_overdue?: boolean;
  is_mandatory?: boolean;
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface SettlementFilters {
  employee_id?: string;
  resignation_id?: string;
  status?: SettlementStatus;
  payment_date_from?: string;
  payment_date_to?: string;
  search?: string;
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface DocumentFilters {
  resignation_id?: string;
  employee_id?: string;
  document_type?: ExitDocumentType;
  is_generated?: boolean;
  is_approved?: boolean;
  is_issued?: boolean;
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// ============================================================================
// PAGINATION TYPES
// ============================================================================

export interface PaginationParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// ============================================================================
// DASHBOARD & STATISTICS TYPES
// ============================================================================

export interface ExitDashboardStats {
  // Resignations
  total_resignations: number;
  pending_resignations: number;
  approved_resignations: number;
  rejected_resignations: number;
  
  // By type
  voluntary_resignations: number;
  involuntary_resignations: number;
  
  // This month
  resignations_this_month: number;
  exits_this_month: number;
  
  // Clearances
  pending_clearances: number;
  overdue_clearances: number;
  
  // Settlements
  pending_settlements: number;
  approved_settlements: number;
  total_settlement_amount: number;
  
  // Documents
  pending_documents: number;
  issued_documents: number;
}

export interface ExitAnalytics {
  period: string; // month, quarter, year
  total_exits: number;
  voluntary_exits: number;
  involuntary_exits: number;
  avg_tenure_years: number;
  top_resignation_reasons: Array<{
    reason: string;
    count: number;
    percentage: number;
  }>;
  department_wise_exits: Array<{
    department: string;
    count: number;
    percentage: number;
  }>;
  avg_settlement_amount: number;
}

// ============================================================================
// BULK OPERATIONS TYPES
// ============================================================================

export interface BulkClearanceCreate {
  resignation_id: string;
  clearances: ClearanceCreate[];
}

export interface BulkDocumentGenerate {
  resignation_id: string;
  document_types: ExitDocumentType[];
}

// ============================================================================
// NOTIFICATION TYPES
// ============================================================================

export interface ExitNotification {
  notification_type: string;
  recipient_ids: string[];
  subject: string;
  message: string;
  data?: Record<string, any>;
}

// ============================================================================
// COMMON TYPES
// ============================================================================

export interface MessageResponse {
  message: string;
  success?: boolean;
}

export interface ErrorResponse {
  detail: string;
  status_code?: number;
}

// ============================================================================
// UTILITY TYPES & CONSTANTS
// ============================================================================

export const RESIGNATION_TYPE_LABELS: Record<ResignationType, string> = {
  [ResignationType.VOLUNTARY]: 'Voluntary',
  [ResignationType.INVOLUNTARY]: 'Involuntary',
  [ResignationType.RETIREMENT]: 'Retirement',
  [ResignationType.ABSCONDING]: 'Absconding',
  [ResignationType.END_OF_CONTRACT]: 'End of Contract',
  [ResignationType.MUTUAL_CONSENT]: 'Mutual Consent'
};

export const RESIGNATION_STATUS_LABELS: Record<ResignationStatus, string> = {
  [ResignationStatus.SUBMITTED]: 'Submitted',
  [ResignationStatus.UNDER_REVIEW]: 'Under Review',
  [ResignationStatus.APPROVED]: 'Approved',
  [ResignationStatus.REJECTED]: 'Rejected',
  [ResignationStatus.WITHDRAWN]: 'Withdrawn',
  [ResignationStatus.COMPLETED]: 'Completed',
  [ResignationStatus.CANCELLED]: 'Cancelled'
};

export const CLEARANCE_STATUS_LABELS: Record<ClearanceStatus, string> = {
  [ClearanceStatus.PENDING]: 'Pending',
  [ClearanceStatus.IN_PROGRESS]: 'In Progress',
  [ClearanceStatus.COMPLETED]: 'Completed',
  [ClearanceStatus.NOT_APPLICABLE]: 'Not Applicable',
  [ClearanceStatus.WAIVED]: 'Waived'
};

export const SETTLEMENT_STATUS_LABELS: Record<SettlementStatus, string> = {
  [SettlementStatus.PENDING]: 'Pending',
  [SettlementStatus.CALCULATED]: 'Calculated',
  [SettlementStatus.APPROVED]: 'Approved',
  [SettlementStatus.PROCESSING]: 'Processing',
  [SettlementStatus.PAID]: 'Paid',
  [SettlementStatus.ON_HOLD]: 'On Hold',
  [SettlementStatus.REJECTED]: 'Rejected'
};

export const SETTLEMENT_COMPONENT_TYPE_LABELS: Record<SettlementComponentType, string> = {
  [SettlementComponentType.SALARY]: 'Salary',
  [SettlementComponentType.LEAVE_ENCASHMENT]: 'Leave Encashment',
  [SettlementComponentType.NOTICE_PAY]: 'Notice Pay',
  [SettlementComponentType.BONUS]: 'Bonus',
  [SettlementComponentType.GRATUITY]: 'Gratuity',
  [SettlementComponentType.REIMBURSEMENT]: 'Reimbursement',
  [SettlementComponentType.RECOVERY]: 'Recovery',
  [SettlementComponentType.OTHER]: 'Other'
};

export const EXIT_DOCUMENT_TYPE_LABELS: Record<ExitDocumentType, string> = {
  [ExitDocumentType.RESIGNATION_LETTER]: 'Resignation Letter',
  [ExitDocumentType.ACCEPTANCE_LETTER]: 'Acceptance Letter',
  [ExitDocumentType.EXPERIENCE_LETTER]: 'Experience Letter',
  [ExitDocumentType.RELIEVING_LETTER]: 'Relieving Letter',
  [ExitDocumentType.SERVICE_CERTIFICATE]: 'Service Certificate',
  [ExitDocumentType.NOC]: 'No Objection Certificate',
  [ExitDocumentType.CLEARANCE_FORM]: 'Clearance Form',
  [ExitDocumentType.FNF_STATEMENT]: 'Full & Final Statement',
  [ExitDocumentType.FORM_16]: 'Form 16',
  [ExitDocumentType.PF_WITHDRAWAL]: 'PF Withdrawal',
  [ExitDocumentType.GRATUITY_FORM]: 'Gratuity Form',
  [ExitDocumentType.OTHER]: 'Other'
};

export const RESIGNATION_STATUS_COLORS: Record<ResignationStatus, string> = {
  [ResignationStatus.SUBMITTED]: 'blue',
  [ResignationStatus.UNDER_REVIEW]: 'yellow',
  [ResignationStatus.APPROVED]: 'green',
  [ResignationStatus.REJECTED]: 'red',
  [ResignationStatus.WITHDRAWN]: 'gray',
  [ResignationStatus.COMPLETED]: 'purple',
  [ResignationStatus.CANCELLED]: 'gray'
};

export const CLEARANCE_STATUS_COLORS: Record<ClearanceStatus, string> = {
  [ClearanceStatus.PENDING]: 'yellow',
  [ClearanceStatus.IN_PROGRESS]: 'blue',
  [ClearanceStatus.COMPLETED]: 'green',
  [ClearanceStatus.NOT_APPLICABLE]: 'gray',
  [ClearanceStatus.WAIVED]: 'orange'
};

export const SETTLEMENT_STATUS_COLORS: Record<SettlementStatus, string> = {
  [SettlementStatus.PENDING]: 'gray',
  [SettlementStatus.CALCULATED]: 'blue',
  [SettlementStatus.APPROVED]: 'green',
  [SettlementStatus.PROCESSING]: 'yellow',
  [SettlementStatus.PAID]: 'purple',
  [SettlementStatus.ON_HOLD]: 'orange',
  [SettlementStatus.REJECTED]: 'red'
};

// Default clearance types
export const DEFAULT_CLEARANCE_TYPES = [
  { clearance_from: 'IT Department', clearance_type: 'IT Assets', description: 'Return laptop, mobile, access cards', is_mandatory: true },
  { clearance_from: 'Admin Department', clearance_type: 'Administrative', description: 'Return keys, ID card, office supplies', is_mandatory: true },
  { clearance_from: 'Finance Department', clearance_type: 'Financial', description: 'Settle advances, expenses, loans', is_mandatory: true },
  { clearance_from: 'HR Department', clearance_type: 'HR', description: 'Exit interview, documentation', is_mandatory: true },
  { clearance_from: 'Reporting Manager', clearance_type: 'Handover', description: 'Knowledge transfer and handover', is_mandatory: true }
];

// Payment modes
export const PAYMENT_MODES = [
  { value: 'bank_transfer', label: 'Bank Transfer' },
  { value: 'cheque', label: 'Cheque' },
  { value: 'cash', label: 'Cash' }
];

// Delivery modes
export const DELIVERY_MODES = [
  { value: 'email', label: 'Email' },
  { value: 'hard_copy', label: 'Hard Copy' },
  { value: 'courier', label: 'Courier' },
  { value: 'portal', label: 'Employee Portal' }
];

// Manager recommendations
export const MANAGER_RECOMMENDATIONS = [
  { value: 'approve', label: 'Approve' },
  { value: 'reject', label: 'Reject' },
  { value: 'counter_offer', label: 'Counter Offer' }
];

// Reason categories
export const RESIGNATION_REASON_CATEGORIES = [
  'Better Opportunity',
  'Higher Salary',
  'Work-Life Balance',
  'Career Growth',
  'Relocation',
  'Personal Reasons',
  'Health Issues',
  'Family Commitments',
  'Further Education',
  'Retirement',
  'Job Satisfaction',
  'Management Issues',
  'Other'
];
