/**
 * HRMS Loan & Advances Service
 * API calls for employee loan management
 */

import api from '../api';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export enum LoanType {
  PERSONAL = 'personal',
  VEHICLE = 'vehicle',
  HOME = 'home',
  EDUCATION = 'education',
  MEDICAL = 'medical',
  MARRIAGE = 'marriage',
  SALARY_ADVANCE = 'salary_advance',
  EMERGENCY = 'emergency',
  FESTIVAL_ADVANCE = 'festival_advance',
  OTHER = 'other',
}

export enum LoanStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  DISBURSED = 'disbursed',
  ACTIVE = 'active',
  CLOSED = 'closed',
  CANCELLED = 'cancelled',
}

export enum EMIStatus {
  PENDING = 'pending',
  PAID = 'paid',
  OVERDUE = 'overdue',
  PARTIALLY_PAID = 'partially_paid',
  WAIVED = 'waived',
}

export interface LoanEligibilityRequest {
  loan_type: LoanType;
  requested_amount: number;
  tenure_months: number;
}

export interface LoanEligibilityResponse {
  is_eligible: boolean;
  eligible_amount: number;
  max_loan_amount: number;
  max_emi_amount: number;
  suggested_tenure_months: number;
  interest_rate: number;
  reasons: string[];
  policy_id?: string;
}

export interface EMICalculationRequest {
  principal_amount: number;
  interest_rate: number;
  tenure_months: number;
}

export interface EMICalculationResponse {
  emi_amount: number;
  total_interest: number;
  total_repayment_amount: number;
  monthly_emi: number;
  effective_rate: number;
}

export interface LoanApplicationCreate {
  loan_type: LoanType;
  loan_amount: number;
  tenure_months: number;
  purpose: string;
  reason_for_loan?: string;
  repayment_frequency?: string;
  bank_name?: string;
  bank_account_number?: string;
  bank_ifsc_code?: string;
  guarantor_employee_id?: string;
  guarantor_name?: string;
  guarantor_relation?: string;
  guarantor_contact?: string;
  attachment_urls?: string[];
}

export interface LoanApplicationUpdate {
  loan_amount?: number;
  tenure_months?: number;
  purpose?: string;
  reason_for_loan?: string;
  bank_name?: string;
  bank_account_number?: string;
  bank_ifsc_code?: string;
}

export interface LoanApprovalAction {
  action: 'approve' | 'reject';
  comments?: string;
  approved_amount?: number;
  approved_tenure?: number;
}

export interface LoanDisbursementRequest {
  disbursement_date: string;
  disbursement_mode: 'bank_transfer' | 'cheque' | 'cash';
  disbursement_reference?: string;
  disbursed_amount?: number;
  repayment_start_date: string;
}

export interface Loan {
  id: string;
  loan_code: string;
  employee_id: string;
  employee_code: string;
  employee_name: string;
  loan_type: LoanType;
  loan_amount: number;
  interest_rate: number;
  tenure_months: number;
  emi_amount: number;
  total_interest: number;
  total_repayment_amount: number;
  processing_fee: number;
  application_date: string;
  purpose: string;
  status: LoanStatus;
  disbursement_date?: string;
  disbursed_amount?: number;
  repayment_start_date?: string;
  first_emi_date?: string;
  last_emi_date?: string;
  principal_outstanding: number;
  interest_outstanding: number;
  total_outstanding: number;
  principal_paid: number;
  interest_paid: number;
  total_paid: number;
  manager_approval_status?: string;
  hr_approval_status?: string;
  finance_approval_status?: string;
  approved_date?: string;
  rejected_date?: string;
  rejection_reason?: string;
  is_deducting_from_salary: boolean;
  is_overdue: boolean;
  days_overdue: number;
  created_at: string;
  updated_at: string;
}

export interface EMIScheduleItem {
  emi_number: number;
  emi_due_date: string;
  emi_amount: number;
  principal_component: number;
  interest_component: number;
  opening_balance: number;
  closing_balance: number;
  status: EMIStatus;
  payment_date?: string;
  amount_paid: number;
  is_overdue: boolean;
  days_overdue: number;
}

export interface EMISchedule {
  loan_id: string;
  loan_code: string;
  total_emis: number;
  schedule: EMIScheduleItem[];
  total_principal: number;
  total_interest: number;
  total_amount: number;
  paid_emis: number;
  pending_emis: number;
  overdue_emis: number;
}

export interface EmployeeLoanSummary {
  total_loans: number;
  active_loans: number;
  closed_loans: number;
  total_borrowed: number;
  total_outstanding: number;
  total_paid: number;
  current_monthly_emi: number;
  next_emi_date?: string;
  next_emi_amount: number;
  overdue_emis: number;
  overdue_amount: number;
}

export interface LoanDashboardStats {
  total_active_loans: number;
  total_disbursed_amount: number;
  total_outstanding_amount: number;
  total_collected_amount: number;
  pending_approvals: number;
  overdue_loans: number;
  total_overdue_amount: number;
  loans_this_month: number;
  disbursements_this_month: number;
  collections_this_month: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}


// ============================================================================
// API SERVICE METHODS
// ============================================================================

const loanService = {
  // Eligibility & Calculation
  checkEligibility: async (request: LoanEligibilityRequest): Promise<LoanEligibilityResponse> => {
    const response = await api.post('/api/v1/hrms/loans/check-eligibility', request);
    return response.data;
  },

  calculateEMI: async (request: EMICalculationRequest): Promise<EMICalculationResponse> => {
    const response = await api.post('/api/v1/hrms/loans/calculate-emi', request);
    return response.data;
  },

  // Loan Applications (Employee)
  createApplication: async (data: LoanApplicationCreate): Promise<Loan> => {
    const response = await api.post('/api/v1/hrms/loans/applications', data);
    return response.data;
  },

  getMyApplications: async (params?: {
    status?: LoanStatus;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Loan>> => {
    const response = await api.get('/api/v1/hrms/loans/applications', { params });
    return response.data;
  },

  getApplication: async (loanId: string): Promise<Loan> => {
    const response = await api.get(`/api/v1/hrms/loans/applications/${loanId}`);
    return response.data;
  },

  updateApplication: async (loanId: string, data: LoanApplicationUpdate): Promise<Loan> => {
    const response = await api.put(`/api/v1/hrms/loans/applications/${loanId}`, data);
    return response.data;
  },

  submitApplication: async (loanId: string): Promise<Loan> => {
    const response = await api.post(`/api/v1/hrms/loans/applications/${loanId}/submit`);
    return response.data;
  },

  cancelApplication: async (loanId: string): Promise<Loan> => {
    const response = await api.post(`/api/v1/hrms/loans/applications/${loanId}/cancel`);
    return response.data;
  },

  // Approval Workflow
  approveByManager: async (loanId: string, action: LoanApprovalAction): Promise<Loan> => {
    const response = await api.post(`/api/v1/hrms/loans/approvals/${loanId}/manager`, action);
    return response.data;
  },

  approveByHR: async (loanId: string, action: LoanApprovalAction): Promise<Loan> => {
    const response = await api.post(`/api/v1/hrms/loans/approvals/${loanId}/hr`, action);
    return response.data;
  },

  approveByFinance: async (loanId: string, action: LoanApprovalAction): Promise<Loan> => {
    const response = await api.post(`/api/v1/hrms/loans/approvals/${loanId}/finance`, action);
    return response.data;
  },

  // Disbursement
  disburseLoan: async (loanId: string, data: LoanDisbursementRequest): Promise<Loan> => {
    const response = await api.post(`/api/v1/hrms/loans/disbursements/${loanId}`, data);
    return response.data;
  },

  // EMI Schedule
  getEMISchedule: async (loanId: string): Promise<EMISchedule> => {
    const response = await api.get(`/api/v1/hrms/loans/applications/${loanId}/emi-schedule`);
    return response.data;
  },

  // Loan Closure
  forecloseLoan: async (loanId: string, data: { closure_date: string; closure_reason: string; closure_remarks?: string }): Promise<Loan> => {
    const response = await api.post(`/api/v1/hrms/loans/applications/${loanId}/foreclose`, data);
    return response.data;
  },

  // Employee Dashboard
  getMySummary: async (): Promise<EmployeeLoanSummary> => {
    const response = await api.get('/api/v1/hrms/loans/my-summary');
    return response.data;
  },

  // Admin/HR Routes
  getAllLoans: async (params?: {
    status?: LoanStatus;
    loan_type?: LoanType;
    employee_id?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Loan>> => {
    const response = await api.get('/api/v1/hrms/loans/all', { params });
    return response.data;
  },

  getDashboardStats: async (): Promise<LoanDashboardStats> => {
    const response = await api.get('/api/v1/hrms/loans/dashboard-stats');
    return response.data;
  },
};

export default loanService;
