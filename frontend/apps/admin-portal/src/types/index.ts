/**
 * TypeScript types for NBFC Suite Admin Portal
 */

// ============================================
// Common Types
// ============================================

export interface User {
  id: string
  username: string
  email: string
  full_name: string
  role: string
  tenant_id: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Tenant {
  id: string
  name: string
  code: string
  is_active: boolean
}

export interface PaginationParams {
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
  has_prev: boolean
}

// ============================================
// Customer Types
// ============================================

export interface Customer {
  id: string
  customer_code: string
  first_name: string
  middle_name?: string
  last_name: string
  full_name: string
  date_of_birth: string
  gender: 'Male' | 'Female' | 'Other'
  marital_status: 'Single' | 'Married' | 'Divorced' | 'Widowed'
  mobile_number: string
  email?: string
  pan_number?: string
  aadhaar_number?: string
  kyc_status: 'Pending' | 'Verified' | 'Rejected'
  customer_status: 'Active' | 'Inactive' | 'Blocked'
  tenant_id: string
  created_at: string
  updated_at: string
}

export interface CustomerAddress {
  id: string
  customer_id: string
  address_type: 'Permanent' | 'Current' | 'Office'
  address_line1: string
  address_line2?: string
  city: string
  state: string
  pincode: string
  is_primary: boolean
}

export interface CustomerDocument {
  id: string
  customer_id: string
  document_type: string
  document_number?: string
  file_path: string
  file_name: string
  verification_status: 'Pending' | 'Verified' | 'Rejected'
  verified_at?: string
  verified_by?: string
  remarks?: string
}

// ============================================
// Loan Types
// ============================================

export interface LoanProduct {
  id: string
  product_code: string
  product_name: string
  product_type: string
  min_amount: number
  max_amount: number
  min_tenure_months: number
  max_tenure_months: number
  interest_rate: number
  processing_fee_percent: number
  is_active: boolean
}

export interface LoanApplication {
  id: string
  application_number: string
  customer_id: string
  customer_name?: string
  product_id: string
  product_name?: string
  loan_amount: number
  tenure_months: number
  interest_rate: number
  emi_amount: number
  purpose: string
  application_status: 'Draft' | 'Submitted' | 'Under Review' | 'Approved' | 'Rejected' | 'Cancelled'
  created_at: string
  updated_at: string
}

export interface LoanAccount {
  id: string
  loan_account_number: string
  application_id: string
  customer_id: string
  customer_name?: string
  product_name?: string
  principal_amount: number
  interest_rate: number
  tenure_months: number
  emi_amount: number
  disbursed_amount: number
  outstanding_principal: number
  outstanding_interest: number
  total_outstanding: number
  loan_status: 'Active' | 'Closed' | 'Written Off' | 'NPA'
  disbursement_date: string
  maturity_date: string
  next_due_date?: string
  overdue_days: number
}

export interface LoanRepayment {
  id: string
  loan_account_id: string
  payment_date: string
  payment_amount: number
  principal_paid: number
  interest_paid: number
  charges_paid: number
  payment_mode: string
  receipt_number: string
  remarks?: string
}

// ============================================
// Deposit Types
// ============================================

export interface DepositProduct {
  id: string
  product_code: string
  product_name: string
  deposit_type: 'Savings' | 'Fixed' | 'Recurring' | 'MIS'
  min_deposit_amount: number
  max_deposit_amount?: number
  interest_rate: number
  interest_calculation_type: string
  min_tenure_months?: number
  max_tenure_months?: number
  status: string
  is_active: boolean
}

export interface DepositAccount {
  id: string
  account_number: string
  customer_id: string
  customer_name?: string
  product_id: string
  product_name?: string
  deposit_type: string
  deposit_amount: number
  interest_rate: number
  tenure_months?: number
  maturity_date?: string
  maturity_amount?: number
  account_balance: number
  account_status: 'Active' | 'Matured' | 'Closed' | 'Premature Closed'
  opening_date: string
}

// ============================================
// Workflow Types
// ============================================

export interface WorkflowTemplate {
  id: string
  template_code: string
  template_name: string
  description?: string
  workflow_type: 'sequential' | 'parallel' | 'conditional'
  workflow_definition: any
  is_active: boolean
  version: number
}

export interface WorkflowInstance {
  id: string
  instance_number: string
  template_id: string
  template_name?: string
  entity_type?: string
  entity_id?: string
  current_step?: string
  instance_status: 'pending' | 'in_progress' | 'completed' | 'cancelled' | 'failed'
  started_at: string
  completed_at?: string
}

export interface WorkflowTask {
  id: string
  instance_id: string
  task_name: string
  task_type: string
  assigned_to?: string
  assigned_to_role?: string
  task_status: 'pending' | 'claimed' | 'in_progress' | 'completed' | 'rejected'
  due_date?: string
  completed_at?: string
  completed_by?: string
  comments?: string
}

// ============================================
// Notification Types
// ============================================

export interface NotificationTemplate {
  id: string
  template_code: string
  template_name: string
  channel: 'SMS' | 'Email' | 'WhatsApp'
  category: string
  subject?: string
  template_content: string
  is_active: boolean
}

export interface Notification {
  id: string
  template_id?: string
  recipient: string
  channel: string
  subject?: string
  content: string
  status: 'pending' | 'sent' | 'delivered' | 'failed'
  priority: 'high' | 'medium' | 'low'
  scheduled_at?: string
  sent_at?: string
  delivered_at?: string
  error_message?: string
}

// ============================================
// Accounting Types
// ============================================

export interface ChartOfAccount {
  id: string
  account_code: string
  account_name: string
  account_type: 'Asset' | 'Liability' | 'Equity' | 'Income' | 'Expense'
  account_sub_type: string
  parent_id?: string
  level: number
  is_group: boolean
  is_system_account: boolean
  current_balance: number
  is_active: boolean
}

export interface JournalEntry {
  id: string
  entry_number: string
  entry_date: string
  description: string
  entry_type: 'Manual' | 'System'
  reference_type?: string
  reference_id?: string
  entry_status: 'draft' | 'posted' | 'reversed'
  total_debit: number
  total_credit: number
  created_at: string
  posted_at?: string
}

// ============================================
// Dashboard Types
// ============================================

export interface DashboardStats {
  total_customers: number
  active_loans: number
  total_disbursed: number
  total_outstanding: number
  overdue_amount: number
  overdue_accounts: number
  collection_efficiency: number
  total_deposits: number
}

export interface RecentActivity {
  id: string
  type: string
  description: string
  timestamp: string
  user?: string
  status?: string
}

// ============================================
// Form Types
// ============================================

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface CreateCustomerRequest {
  first_name: string
  middle_name?: string
  last_name: string
  date_of_birth: string
  gender: string
  marital_status: string
  mobile_number: string
  email?: string
  pan_number?: string
  aadhaar_number?: string
}

export interface CreateLoanApplicationRequest {
  customer_id: string
  product_id: string
  loan_amount: number
  tenure_months: number
  purpose: string
}

// ============================================
// API Response Types
// ============================================

export interface ApiError {
  code: string
  message: string
  details?: any
}
