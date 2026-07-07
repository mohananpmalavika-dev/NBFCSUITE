/**
 * Compliance & Regulatory Reporting Types
 * CRILC & SMA Types
 */

export type BorrowerType =
  | 'individual'
  | 'sole_proprietor'
  | 'partnership'
  | 'private_limited'
  | 'public_limited'
  | 'trust'
  | 'society'
  | 'government'
  | 'huf'

export type SMAStatus =
  | 'standard'
  | 'sma_0'
  | 'sma_1'
  | 'sma_2'
  | 'npa_substandard'
  | 'npa_doubtful'
  | 'npa_loss'

export type AssetClassification =
  | 'standard'
  | 'sub_standard'
  | 'doubtful_1'
  | 'doubtful_2'
  | 'doubtful_3'
  | 'loss'

export type FacilityType =
  | 'term_loan'
  | 'cash_credit'
  | 'overdraft'
  | 'working_capital'
  | 'bill_discounting'
  | 'bank_guarantee'
  | 'letter_of_credit'
  | 'other'

export type ExposureType = 'funded' | 'non_funded'

export type ReportStatus =
  | 'draft'
  | 'pending_review'
  | 'approved'
  | 'submitted'
  | 'rejected'

export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical'

export type AlertStatus = 'open' | 'acknowledged' | 'resolved' | 'dismissed'

// ============================================================================
// CRILC BORROWER
// ============================================================================

export interface CRILCBorrower {
  id: string
  tenant_id: string
  borrower_code: string
  borrower_name: string
  borrower_type: BorrowerType
  pan_number?: string
  cin_number?: string
  gstin?: string
  registered_address?: string
  city?: string
  state?: string
  pincode?: string
  country?: string
  industry_code?: string
  industry_name?: string
  nature_of_business?: string
  year_of_incorporation?: number
  annual_turnover?: number
  net_worth?: number
  financial_year?: string
  total_credit_exposure: number
  funded_exposure?: number
  non_funded_exposure?: number
  is_large_credit: boolean
  large_credit_since?: string
  is_part_of_group: boolean
  group_name?: string
  group_exposure?: number
  current_sma_status: SMAStatus
  current_asset_classification: AssetClassification
  days_past_due: number
  internal_rating?: string
  external_rating?: string
  rating_agency?: string
  rating_date?: string
  customer_id?: string
  is_active: boolean
  last_reported_quarter?: string
  created_at: string
  updated_at: string
}

export interface CreateCRILCBorrowerRequest {
  borrower_name: string
  borrower_type: BorrowerType
  pan_number?: string
  cin_number?: string
  gstin?: string
  registered_address?: string
  city?: string
  state?: string
  pincode?: string
  industry_code?: string
  industry_name?: string
  nature_of_business?: string
  year_of_incorporation?: number
  annual_turnover?: number
  net_worth?: number
  financial_year?: string
  customer_id?: string
  is_part_of_group?: boolean
  group_name?: string
  internal_rating?: string
  external_rating?: string
  rating_agency?: string
  rating_date?: string
}

export interface UpdateCRILCBorrowerRequest {
  borrower_name?: string
  registered_address?: string
  city?: string
  state?: string
  pincode?: string
  industry_code?: string
  industry_name?: string
  annual_turnover?: number
  net_worth?: number
  financial_year?: string
  is_part_of_group?: boolean
  group_name?: string
  internal_rating?: string
  external_rating?: string
  rating_agency?: string
  rating_date?: string
}

// ============================================================================
// CRILC FACILITY
// ============================================================================

export interface CRILCFacility {
  id: string
  tenant_id: string
  borrower_id: string
  loan_account_id?: string
  facility_id: string
  facility_type: FacilityType
  exposure_type: ExposureType
  sanctioned_amount: number
  outstanding_amount: number
  overdue_amount: number
  sanction_date: string
  disbursement_date?: string
  maturity_date?: string
  security_type?: string
  security_value?: number
  collateral_details?: Record<string, any>
  days_past_due: number
  asset_classification: AssetClassification
  interest_rate?: number
  interest_overdue: number
  is_active: boolean
  closure_date?: string
  created_at: string
}

export interface CreateCRILCFacilityRequest {
  borrower_id: string
  loan_account_id?: string
  facility_type: FacilityType
  exposure_type: ExposureType
  sanctioned_amount: number
  outstanding_amount: number
  overdue_amount?: number
  sanction_date: string
  disbursement_date?: string
  maturity_date?: string
  security_type?: string
  security_value?: number
  collateral_details?: Record<string, any>
  interest_rate?: number
}

// ============================================================================
// SMA TRACKING
// ============================================================================

export interface SMATracking {
  id: string
  tenant_id: string
  borrower_id: string
  loan_account_id: string
  as_on_date: string
  reporting_quarter?: string
  current_sma_status: SMAStatus
  previous_sma_status?: SMAStatus
  status_change_date?: string
  days_past_due: number
  days_in_current_status: number
  principal_outstanding: number
  interest_outstanding: number
  total_outstanding: number
  principal_overdue: number
  interest_overdue: number
  total_overdue: number
  installment_amount?: number
  last_payment_date?: string
  last_payment_amount?: number
  next_due_date?: string
  asset_classification: AssetClassification
  provision_required: number
  provision_percentage: number
  alert_triggered: boolean
  follow_up_required: boolean
  created_at: string
}

export interface SMAStatusHistory {
  id: string
  tenant_id: string
  borrower_id: string
  loan_account_id: string
  from_status: SMAStatus
  to_status: SMAStatus
  change_date: string
  dpd_at_change?: number
  outstanding_at_change?: number
  overdue_at_change?: number
  change_reason?: string
  triggered_by?: string
  created_at: string
}

export interface SMACalculationRequest {
  as_on_date: string
  loan_account_ids?: string[]
  calculate_provisions: boolean
}

export interface SMACalculationResponse {
  as_on_date: string
  accounts_processed: number
  status_changes: number
  alerts_created: number
  results: Array<{
    loan_account_id: string
    loan_account_number: string
    borrower_name: string
    sma_status: SMAStatus
    dpd: number
    total_outstanding: number
    total_overdue: number
    provision_required: number
  }>
  status_changes_detail: Array<{
    loan_account_number: string
    from_status: SMAStatus
    to_status: SMAStatus
    dpd: number
  }>
}

export interface SMADashboardStats {
  total_accounts: number
  standard_count: number
  standard_amount: number
  sma_0_count: number
  sma_0_amount: number
  sma_1_count: number
  sma_1_amount: number
  sma_2_count: number
  sma_2_amount: number
  npa_count: number
  npa_amount: number
  total_exposure: number
  provision_required: number
  alerts_open: number
}

// ============================================================================
// QUARTERLY RETURNS
// ============================================================================

export interface CRILCQuarterlyReturn {
  id: string
  tenant_id: string
  return_number: string
  reporting_quarter: string
  reporting_year: string
  as_on_date: string
  status: ReportStatus
  total_large_borrowers: number
  total_funded_exposure: number
  total_non_funded_exposure: number
  total_exposure: number
  sma_0_count: number
  sma_0_amount: number
  sma_1_count: number
  sma_1_amount: number
  sma_2_count: number
  sma_2_amount: number
  npa_count: number
  npa_amount: number
  report_file_path?: string
  report_file_url?: string
  report_format?: string
  prepared_date?: string
  approved_date?: string
  submitted_date?: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface CreateCRILCQuarterlyReturnRequest {
  reporting_quarter: string
  reporting_year: string
  as_on_date: string
  remarks?: string
}

export interface SMAQuarterlyReport {
  id: string
  tenant_id: string
  report_number: string
  reporting_quarter: string
  reporting_year: string
  as_on_date: string
  status: ReportStatus
  sma_0_accounts: number
  sma_0_amount: number
  sma_0_new_additions: number
  sma_0_regularized: number
  sma_0_upgraded_to_sma1: number
  sma_1_accounts: number
  sma_1_amount: number
  sma_1_new_additions: number
  sma_1_regularized: number
  sma_1_upgraded_to_sma2: number
  sma_2_accounts: number
  sma_2_amount: number
  sma_2_new_additions: number
  sma_2_regularized: number
  sma_2_slipped_to_npa: number
  report_file_path?: string
  prepared_date?: string
  approved_date?: string
  submitted_date?: string
  created_at: string
}

export interface CreateSMAQuarterlyReportRequest {
  reporting_quarter: string
  reporting_year: string
  as_on_date: string
  remarks?: string
}

// ============================================================================
// COMPLIANCE ALERTS
// ============================================================================

export interface ComplianceAlert {
  id: string
  tenant_id: string
  alert_type: string
  alert_category: string
  severity: AlertSeverity
  borrower_id?: string
  loan_account_id?: string
  alert_message: string
  alert_details?: Record<string, any>
  status: AlertStatus
  acknowledged_at?: string
  resolved_at?: string
  due_date?: string
  is_overdue: boolean
  created_at: string
}

// ============================================================================
// LARGE CREDIT IDENTIFICATION
// ============================================================================

export interface LargeCreditIdentificationRequest {
  threshold_amount?: number
  as_on_date: string
  include_group_exposure: boolean
}

export interface LargeCreditIdentificationResponse {
  threshold_amount: number
  as_on_date: string
  total_large_credits: number
  newly_identified: number
  removed_from_list: number
  identified_borrowers: Array<{
    borrower_id: string
    borrower_name: string
    total_exposure: number
    threshold: number
  }>
  removed_borrowers: Array<{
    borrower_id: string
    borrower_name: string
    total_exposure: number
  }>
}

// ============================================================================
// FILTER TYPES
// ============================================================================

export interface LargeCreditFilter {
  sma_status?: SMAStatus
  asset_classification?: AssetClassification
  min_exposure?: number
  max_exposure?: number
  industry_code?: string
  state?: string
  is_active?: boolean
  reporting_quarter?: string
}

export interface ComplianceAlertFilter {
  status?: AlertStatus
  alert_type?: string
  severity?: AlertSeverity
  is_overdue?: boolean
}
