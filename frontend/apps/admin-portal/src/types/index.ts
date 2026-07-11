/**
 * TypeScript types for NBFC Suite Admin Portal
 */

// Export customer types
export * from './customer.types'

// Export exit management types
export * from './exit.types'

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


// ============================================
// Risk Management Types
// ============================================

export type CustomerSegment = 'retail' | 'msme' | 'corporate'
export type LoanCategory = 'secured' | 'unsecured'
export type EmploymentType = 'salaried' | 'self_employed' | 'business' | 'professional'
export type RiskGrade = 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D'
export type ExposureLimitType = 'customer' | 'group' | 'industry' | 'geography' | 'product' | 'collateral_type' | 'dealer'
export type BreachAction = 'alert' | 'block' | 'require_approval'
export type SignalCategory = 'payment_behavior' | 'financial_stress' | 'credit_bureau' | 'banking_behavior' | 'business_performance' | 'external_factors' | 'relationship_changes'
export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical'
export type AlertStatus = 'open' | 'acknowledged' | 'investigating' | 'resolved' | 'false_positive' | 'escalated'
export type RatingType = 'customer' | 'application' | 'account'

export interface CreditPolicy {
  id: number
  tenant_id: string
  policy_code: string
  policy_name: string
  policy_version: string
  product_types: string[]
  customer_segments: string[]
  loan_categories: string[]
  min_cibil_score: number
  min_experian_score?: number
  min_equifax_score?: number
  min_crif_score?: number
  bureau_vintage_months: number
  min_monthly_income?: number
  max_debt_to_income_ratio: number
  min_foir?: number
  min_loan_amount: number
  max_loan_amount: number
  ltv_ratio?: number
  min_age: number
  max_age: number
  max_age_at_maturity: number
  allowed_employment_types: string[]
  min_employment_months: number
  min_business_vintage_months: number
  allowed_states?: string[]
  restricted_pincodes?: string[]
  tier_restrictions?: string[]
  max_active_loans: number
  max_enquiries_last_3months: number
  allow_defaults: boolean
  allow_settlements: boolean
  allow_write_offs: boolean
  min_months_since_default?: number
  requires_co_applicant: boolean
  requires_guarantor: boolean
  co_applicant_min_income?: number
  mandatory_document_types?: number[]
  requires_bank_statement_months: number
  requires_itr_years: number
  approval_matrix?: Record<string, any>
  requires_credit_committee: boolean
  credit_committee_threshold?: number
  is_active: boolean
  effective_from: string
  effective_to?: string
  description?: string
  terms_and_conditions?: string
  deviation_policy?: string
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
  approved_by?: string
  approved_at?: string
}

export interface RiskPricingRule {
  id: number
  tenant_id: string
  credit_policy_id: number
  rule_code: string
  rule_name: string
  rule_priority: number
  min_credit_score?: number
  max_credit_score?: number
  min_loan_amount?: number
  max_loan_amount?: number
  min_tenure_months?: number
  max_tenure_months?: number
  customer_segment?: string
  employment_type?: string
  loan_category?: string
  risk_ratings?: string[]
  base_interest_rate: number
  rate_adjustment: number
  final_interest_rate: number
  processing_fee_adjustment?: number
  reduce_documentation_charges: boolean
  waive_prepayment_charges: boolean
  max_ltv_override?: number
  grace_period_days?: number
  penal_interest_adjustment?: number
  cashback_percentage?: number
  loyalty_discount?: number
  is_active: boolean
  effective_from: string
  effective_to?: string
  created_at: string
  updated_at: string
}

export interface ExposureLimit {
  id: number
  tenant_id: string
  limit_code: string
  limit_name: string
  limit_type: ExposureLimitType
  customer_id?: string
  industry_id?: string
  state_code?: string
  product_type?: string
  collateral_type?: string
  dealer_id?: string
  group_identifier?: string
  limit_amount: number
  utilized_amount: number
  available_amount: number
  utilization_percentage: number
  warning_threshold_percentage: number
  critical_threshold_percentage: number
  breach_action: BreachAction
  limit_period: string
  period_start_date: string
  period_end_date: string
  regulatory_limit: boolean
  regulatory_reference?: string
  capital_charge_percentage?: number
  review_frequency_days: number
  is_active: boolean
  is_breached: boolean
  breach_date?: string
  breach_remarks?: string
  last_review_date?: string
  next_review_date?: string
  created_at: string
  updated_at: string
}

export interface ExposureTransaction {
  id: number
  exposure_limit_id: number
  transaction_type: string
  transaction_reference: string
  amount: number
  previous_utilized: number
  new_utilized: number
  transaction_date: string
  remarks?: string
}

export interface RiskRating {
  id: number
  tenant_id: string
  customer_id: string
  loan_application_id?: number
  loan_account_id?: number
  rating_type: RatingType
  rating_date: string
  rating_valid_until?: string
  risk_grade: RiskGrade
  risk_score: number
  pd_percentage?: number
  lgd_percentage?: number
  ead_amount?: number
  expected_loss?: number
  bureau_score?: number
  bureau_score_weightage?: number
  income_stability_score?: number
  income_stability_weightage?: number
  debt_burden_score?: number
  debt_burden_weightage?: number
  repayment_history_score?: number
  repayment_history_weightage?: number
  employment_stability_score?: number
  employment_stability_weightage?: number
  banking_behavior_score?: number
  banking_behavior_weightage?: number
  demographic_score?: number
  demographic_weightage?: number
  delinquency_flag: boolean
  fraud_flag: boolean
  litigation_flag: boolean
  negative_area_flag: boolean
  dpd_max_last_12months?: number
  dpd_max_last_24months?: number
  active_loans_count?: number
  enquiries_last_3months?: number
  credit_utilization_percentage?: number
  rating_override: boolean
  override_reason?: string
  original_risk_grade?: string
  original_risk_score?: number
  rating_model_code?: string
  rating_model_version?: string
  created_at: string
  updated_at: string
}

export interface EarlyWarningSignal {
  id: number
  tenant_id: string
  signal_code: string
  signal_name: string
  signal_category: SignalCategory
  severity_level: SeverityLevel
  risk_weight: number
  detection_rule: Record<string, any>
  trigger_threshold?: number
  monitoring_period_days: number
  auto_escalate: boolean
  escalation_level?: string
  notification_template?: string
  is_active: boolean
  description?: string
  recommended_action?: string
  created_at: string
  updated_at: string
}

export interface EarlyWarningAlert {
  id: number
  tenant_id: string
  signal_id: number
  alert_number: string
  alert_date: string
  customer_id: string
  loan_account_id: number
  customer_name?: string
  loan_account_number?: string
  signal_code?: string
  signal_name?: string
  signal_category: string
  severity_level: string
  detected_value?: number
  threshold_value?: number
  variance_percentage?: number
  status: AlertStatus
  acknowledged_at?: string
  resolved_at?: string
  resolution_remarks?: string
  action_taken?: string
  action_date?: string
  escalation_level: number
  escalated_at?: string
  is_recurring: boolean
  occurrence_count: number
  created_at: string
  updated_at: string
}

export interface PolicyEvaluationRequest {
  customer_id: string
  loan_amount: number
  tenure_months: number
  product_type: string
  loan_category: string
  customer_segment?: string
  credit_score: number
  monthly_income: number
  existing_obligations: number
  age: number
  employment_type: string
}

export interface PolicyEvaluationResponse {
  eligible: boolean
  applicable_policy_code?: string
  applicable_policy_name?: string
  risk_grade?: string
  suggested_interest_rate?: number
  max_eligible_amount?: number
  passed_checks: string[]
  failed_checks: string[]
  warnings: string[]
  debt_to_income_ratio: number
  foir?: number
  recommendations: string[]
}

export interface PricingCalculationRequest {
  customer_id: string
  loan_amount: number
  tenure_months: number
  credit_score: number
  employment_type: string
  loan_category: string
  customer_segment?: string
  product_type: string
}

export interface PricingCalculationResponse {
  base_rate: number
  risk_adjustment: number
  final_rate: number
  processing_fee_adjustment?: number
  applicable_rule_code?: string
  applicable_rule_name?: string
  cashback_percentage?: number
  loyalty_discount?: number
  waive_prepayment_charges: boolean
}

export interface RiskRatingStats {
  total_rated_customers: number
  rating_distribution: Record<string, number>
  average_score: number
  high_risk_count: number
  high_risk_percentage: number
  avg_pd_percentage?: number
  total_expected_loss?: number
}

export interface EarlyWarningAlertStats {
  total_alerts: number
  open_alerts: number
  critical_alerts: number
  high_alerts: number
  resolved_today: number
  avg_resolution_time_hours?: number
  alerts_by_category: Record<string, number>
  alerts_by_severity: Record<string, number>
}

export interface RiskDashboardSummary {
  risk_ratings: RiskRatingStats
  early_warning_alerts: EarlyWarningAlertStats
  exposure_limits: {
    total_limits: number
    breached_limits: number
    high_utilization_limits: number
  }
}
