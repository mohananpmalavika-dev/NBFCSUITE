/**
 * RBI Returns Automation Types
 * NBS-7, Statutory Returns, XBRL, Compliance Calendar
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum RBIReturnType {
  NBS_7_MONTHLY = 'nbs_7_monthly',
  NBS_7_QUARTERLY = 'nbs_7_quarterly',
  ALM_RETURN = 'alm_return',
  NPA_RETURN = 'npa_return',
  EXPOSURE_RETURN = 'exposure_return',
  CRILC_RETURN = 'crilc_return',
  SMA_RETURN = 'sma_return',
  PRUDENTIAL_NORMS = 'prudential_norms',
  CAPITAL_ADEQUACY = 'capital_adequacy',
  LIQUIDITY_RETURN = 'liquidity_return',
  SECTORAL_DEPLOYMENT = 'sectoral_deployment',
  OTHER = 'other',
}

export enum XBRLTaxonomy {
  RBI_NBFC_2023 = 'rbi_nbfc_2023',
  RBI_NBFC_2024 = 'rbi_nbfc_2024',
  RBI_NBFC_ND_SI = 'rbi_nbfc_nd_si',
  RBI_NBFC_D = 'rbi_nbfc_d',
  CUSTOM = 'custom',
}

export enum SubmissionStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  PENDING_REVIEW = 'pending_review',
  PENDING_APPROVAL = 'pending_approval',
  APPROVED = 'approved',
  SUBMITTED = 'submitted',
  ACKNOWLEDGED = 'acknowledged',
  REJECTED = 'rejected',
  REVISED = 'revised',
}

export enum ComplianceEventType {
  RETURN_DUE = 'return_due',
  AUDIT_SCHEDULED = 'audit_scheduled',
  BOARD_MEETING = 'board_meeting',
  REGULATORY_FILING = 'regulatory_filing',
  LICENSE_RENEWAL = 'license_renewal',
  INSPECTION = 'inspection',
  OTHER = 'other',
}

export enum EventPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum ReturnFrequency {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  FORTNIGHTLY = 'fortnightly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  HALF_YEARLY = 'half_yearly',
  ANNUAL = 'annual',
  ON_DEMAND = 'on_demand',
}

// ============================================================================
// RBI RETURN MASTER TYPES
// ============================================================================

export interface RBIReturnMaster {
  id: string
  tenant_id: string
  return_code: string
  return_name: string
  return_type: RBIReturnType
  description?: string
  applicable_to?: string[]
  is_mandatory: boolean
  effective_from?: string
  effective_to?: string
  frequency: ReturnFrequency
  due_day_of_month?: number
  due_days_after_period?: number
  grace_period_days: number
  file_formats?: string[]
  has_xbrl: boolean
  xbrl_taxonomy?: XBRLTaxonomy
  submission_portal?: string
  submission_method?: string
  is_active: boolean
  created_at: string
}

export interface CreateRBIReturnMasterRequest {
  return_code: string
  return_name: string
  return_type: string
  description?: string
  applicable_to?: string[]
  is_mandatory?: boolean
  effective_from?: string
  effective_to?: string
  frequency: string
  due_day_of_month?: number
  due_days_after_period?: number
  grace_period_days?: number
  file_formats?: string[]
  has_xbrl?: boolean
  xbrl_taxonomy?: string
  submission_portal?: string
  submission_method?: string
}

// ============================================================================
// NBS-7 RETURN TYPES
// ============================================================================

export interface NBS7Return {
  id: string
  tenant_id: string
  return_number: string
  return_master_id?: string
  reporting_period: string
  period_start_date: string
  period_end_date: string
  as_on_date: string
  financial_year: string
  quarter?: string
  status: SubmissionStatus
  
  // Calculated Totals
  total_loans: number
  total_provisions: number
  net_loans_advances: number
  total_investments: number
  fixed_assets_net: number
  cash_bank_balances: number
  total_assets: number
  
  share_capital: number
  reserves_surplus: number
  total_capital_reserves: number
  total_borrowings: number
  public_deposits: number
  total_liabilities: number
  
  total_income: number
  total_expenditure: number
  profit_before_tax: number
  tax_provision: number
  profit_after_tax: number
  
  gross_npa: number
  net_npa: number
  npa_ratio: number
  
  crar_percentage: number
  tier1_capital: number
  tier2_capital: number
  total_capital: number
  risk_weighted_assets: number
  
  excel_file_url?: string
  pdf_file_url?: string
  
  prepared_date?: string
  reviewed_date?: string
  approved_date?: string
  submitted_date?: string
  
  due_date: string
  is_overdue: boolean
  days_overdue: number
  
  submission_reference?: string
  acknowledgement_number?: string
  
  remarks?: string
  
  created_at: string
  updated_at: string
}

export interface NBS7ReturnGenerateRequest {
  reporting_period: string
  period_start_date: string
  period_end_date: string
  as_on_date: string
  financial_year: string
  quarter?: string
  include_sectoral?: boolean
  include_geographic?: boolean
  remarks?: string
}

export interface NBS7ReturnUpdateRequest {
  term_loans?: number
  hire_purchase?: number
  leasing?: number
  bills_discounted?: number
  other_loans?: number
  provision_standard_assets?: number
  provision_npa?: number
  government_securities?: number
  corporate_bonds?: number
  mutual_funds?: number
  shares_equity?: number
  other_investments?: number
  fixed_assets_gross?: number
  accumulated_depreciation?: number
  cash_bank_balances?: number
  other_assets?: number
  share_capital?: number
  reserves_surplus?: number
  bank_borrowings?: number
  debentures?: number
  commercial_paper?: number
  subordinated_debt?: number
  other_borrowings?: number
  public_deposits?: number
  other_liabilities?: number
  provisions_liabilities?: number
  interest_income?: number
  other_income?: number
  interest_expenditure?: number
  operating_expenses?: number
  provisions_write_offs?: number
  tax_provision?: number
  gross_npa?: number
  net_npa?: number
  tier1_capital?: number
  tier2_capital?: number
  risk_weighted_assets?: number
  remarks?: string
  internal_notes?: string
}

// ============================================================================
// STATUTORY RETURN TYPES
// ============================================================================

export interface StatutoryReturn {
  id: string
  tenant_id: string
  return_number: string
  return_master_id: string
  return_type: string
  reporting_period: string
  period_start_date: string
  period_end_date: string
  as_on_date: string
  financial_year: string
  status: SubmissionStatus
  
  return_data: Record<string, any>
  schedules?: Record<string, any>
  summary_data?: Record<string, any>
  
  validation_status: string
  validation_errors?: Array<{ field: string; message: string }>
  validation_warnings?: Array<{ field: string; message: string }>
  
  excel_file_url?: string
  pdf_file_url?: string
  
  prepared_date?: string
  reviewed_date?: string
  approved_date?: string
  submitted_date?: string
  
  due_date: string
  is_overdue: boolean
  days_overdue: number
  
  submission_reference?: string
  acknowledgement_number?: string
  
  revision_number: number
  parent_return_id?: string
  
  remarks?: string
  
  created_at: string
  updated_at: string
}

export interface CreateStatutoryReturnRequest {
  return_master_id: string
  return_type: string
  reporting_period: string
  period_start_date: string
  period_end_date: string
  as_on_date: string
  financial_year: string
  return_data: Record<string, any>
  schedules?: Record<string, any>
  summary_data?: Record<string, any>
  remarks?: string
  internal_notes?: string
}

// ============================================================================
// XBRL DOCUMENT TYPES
// ============================================================================

export interface XBRLDocument {
  id: string
  tenant_id: string
  document_number: string
  document_name: string
  return_type: string
  nbs7_return_id?: string
  statutory_return_id?: string
  taxonomy_version: string
  taxonomy_url?: string
  schema_version?: string
  reporting_period: string
  period_start_date: string
  period_end_date: string
  is_valid: boolean
  validation_errors?: Array<{ message: string }>
  validation_date?: string
  xbrl_file_url?: string
  xbrl_file_size?: number
  entity_identifier?: string
  entity_name?: string
  status: string
  generated_date?: string
  submitted_date?: string
  submission_reference?: string
  remarks?: string
  created_at: string
}

export interface XBRLGenerateRequest {
  return_type: string
  return_id: string
  taxonomy_version: string
  entity_identifier: string
  entity_name: string
  include_validation?: boolean
}

export interface XBRLValidationResponse {
  is_valid: boolean
  errors: Array<{ message: string }>
  warnings: Array<{ message: string }>
  validation_date: string
}

// ============================================================================
// COMPLIANCE CALENDAR TYPES
// ============================================================================

export interface ComplianceCalendarEvent {
  id: string
  tenant_id: string
  event_code?: string
  event_title: string
  event_type: ComplianceEventType
  description?: string
  requirements?: string
  event_date: string
  event_time?: string
  due_date?: string
  priority: EventPriority
  category?: string
  return_master_id?: string
  nbs7_return_id?: string
  statutory_return_id?: string
  is_recurring: boolean
  recurrence_pattern?: string
  recurrence_day?: number
  status: string
  completion_date?: string
  completed_by?: string
  assigned_to?: string
  assigned_by?: string
  assigned_date?: string
  reminder_enabled: boolean
  reminder_days_before?: number[]
  last_reminder_sent?: string
  notification_sent: boolean
  notification_date?: string
  attachments?: string[]
  notes?: string
  internal_comments?: string
  start_date?: string
  estimated_effort_hours?: number
  actual_effort_hours?: number
  created_at: string
  updated_at: string
}

export interface CreateComplianceCalendarRequest {
  event_code?: string
  event_title: string
  event_type: string
  description?: string
  requirements?: string
  event_date: string
  event_time?: string
  due_date?: string
  priority?: string
  category?: string
  return_master_id?: string
  nbs7_return_id?: string
  statutory_return_id?: string
  is_recurring?: boolean
  recurrence_pattern?: string
  recurrence_day?: number
  assigned_to?: string
  reminder_enabled?: boolean
  reminder_days_before?: number[]
  notes?: string
}

export interface UpdateComplianceCalendarRequest {
  event_title?: string
  description?: string
  requirements?: string
  event_date?: string
  event_time?: string
  due_date?: string
  priority?: string
  category?: string
  status?: string
  assigned_to?: string
  reminder_enabled?: boolean
  reminder_days_before?: number[]
  notes?: string
  internal_comments?: string
}

export interface CompleteCalendarEventRequest {
  completion_notes?: string
  actual_effort_hours?: number
}

// ============================================================================
// DASHBOARD & ANALYTICS TYPES
// ============================================================================

export interface RBIReturnsDashboardStats {
  total_returns_due: number
  overdue_returns: number
  submitted_this_month: number
  pending_approval: number
  draft_returns: number
  
  nbs7_monthly_status: Record<string, number>
  nbs7_quarterly_status: Record<string, number>
  statutory_returns_status: Record<string, number>
  
  upcoming_deadlines: Array<{
    event_title: string
    due_date: string
    priority: string
    days_remaining: number
  }>
  
  recent_submissions: Array<{
    return_number: string
    reporting_period: string
    submitted_date: string
    is_overdue: boolean
  }>
  
  compliance_score: number
  on_time_submission_rate: number
}

export interface ComplianceCalendarSummary {
  total_events: number
  upcoming_events: number
  overdue_events: number
  completed_events: number
  events_this_month: number
  events_this_quarter: number
  
  by_priority: Record<string, number>
  by_category: Record<string, number>
  by_status: Record<string, number>
  
  upcoming_critical: ComplianceCalendarEvent[]
}

export interface ReturnSubmissionHistory {
  id: string
  tenant_id: string
  return_type: string
  nbs7_return_id?: string
  statutory_return_id?: string
  xbrl_document_id?: string
  action: string
  previous_status?: string
  new_status?: string
  action_by: string
  action_date: string
  action_details?: Record<string, any>
  comments?: string
  ip_address?: string
  created_at: string
}

// ============================================================================
// FILTER TYPES
// ============================================================================

export interface RBIReturnsFilter {
  return_type?: string
  financial_year?: string
  quarter?: string
  status?: string
  is_overdue?: boolean
  from_date?: string
  to_date?: string
}

export interface ComplianceCalendarFilter {
  event_type?: string
  priority?: string
  category?: string
  status?: string
  assigned_to?: string
  from_date?: string
  to_date?: string
  is_overdue?: boolean
}

// ============================================================================
// PAGINATION TYPES
// ============================================================================

export interface PaginationParams {
  page?: number
  page_size?: number
  skip?: number
  limit?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}
