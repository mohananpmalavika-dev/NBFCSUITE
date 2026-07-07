/**
 * Branch & Operations Management Types
 */

export enum OrganizationLevel {
  HEAD_OFFICE = "HEAD_OFFICE",
  ZONE = "ZONE",
  REGION = "REGION",
  AREA = "AREA",
  BRANCH = "BRANCH",
}

export enum BranchType {
  FULL_SERVICE = "FULL_SERVICE",
  SATELLITE = "SATELLITE",
  COLLECTION_CENTER = "COLLECTION_CENTER",
  SERVICE_CENTER = "SERVICE_CENTER",
}

export enum BranchStatus {
  ACTIVE = "ACTIVE",
  INACTIVE = "INACTIVE",
  SUSPENDED = "SUSPENDED",
  CLOSED = "CLOSED",
}

export enum DayStatus {
  NOT_STARTED = "NOT_STARTED",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  SUSPENDED = "SUSPENDED",
}

export enum TransactionType {
  CASH_RECEIPT = "CASH_RECEIPT",
  CASH_PAYMENT = "CASH_PAYMENT",
  INTERNAL_TRANSFER = "INTERNAL_TRANSFER",
  BANK_DEPOSIT = "BANK_DEPOSIT",
  BANK_WITHDRAWAL = "BANK_WITHDRAWAL",
  COUNTER_OPENING = "COUNTER_OPENING",
  COUNTER_CLOSING = "COUNTER_CLOSING",
}

export interface Organization {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  display_name: string;
  level: OrganizationLevel;
  parent_id?: string;
  hierarchy_path?: string;
  manager_id?: string;
  manager_name?: string;
  email?: string;
  phone?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  pincode?: string;
  country: string;
  status: BranchStatus;
  is_operational: boolean;
  opening_date?: string;
  closing_date?: string;
  cash_limit: number;
  daily_transaction_limit: number;
  settings?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface OrganizationHierarchy {
  id: string;
  code: string;
  name: string;
  level: OrganizationLevel;
  parent_id?: string;
  children: OrganizationHierarchy[];
}

export interface Branch {
  id: string;
  tenant_id: string;
  organization_id: string;
  branch_code: string;
  branch_name: string;
  branch_type: BranchType;
  ifsc_code?: string;
  micr_code?: string;
  swift_code?: string;
  working_days?: string[];
  working_hours_start: string;
  working_hours_end: string;
  branch_manager_id?: string;
  branch_manager_name?: string;
  branch_manager_phone?: string;
  branch_manager_email?: string;
  latitude?: number;
  longitude?: number;
  staff_count: number;
  customer_count: number;
  active_loan_count: number;
  is_head_office: boolean;
  is_regional_office: boolean;
  created_at: string;
  updated_at: string;
}

export interface BranchDayOperation {
  id: string;
  tenant_id: string;
  branch_id: string;
  branch_code: string;
  business_date: string;
  day_begin_time?: string;
  day_begin_by?: string;
  day_begin_remarks?: string;
  day_end_time?: string;
  day_end_by?: string;
  day_end_remarks?: string;
  opening_cash_balance: number;
  opening_bank_balance: number;
  closing_cash_balance: number;
  closing_bank_balance: number;
  total_receipts: number;
  total_payments: number;
  total_transfers: number;
  transaction_count: number;
  status: DayStatus;
  is_holiday: boolean;
  pre_day_checklist?: Record<string, any>;
  post_day_checklist?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface BranchCounter {
  id: string;
  tenant_id: string;
  branch_id: string;
  counter_number: string;
  counter_name: string;
  counter_type: string;
  assigned_user_id?: string;
  assigned_user_name?: string;
  opened_at?: string;
  opened_by?: string;
  opening_balance: number;
  closed_at?: string;
  closed_by?: string;
  closing_balance: number;
  current_balance: number;
  total_receipts: number;
  total_payments: number;
  transaction_count: number;
  is_active: boolean;
  is_open: boolean;
  created_at: string;
  updated_at: string;
}

export interface CashTransaction {
  id: string;
  tenant_id: string;
  transaction_number: string;
  transaction_date: string;
  transaction_type: TransactionType;
  branch_id: string;
  counter_id?: string;
  amount: number;
  from_party_type?: string;
  from_party_id?: string;
  from_party_name?: string;
  to_party_type?: string;
  to_party_id?: string;
  to_party_name?: string;
  reference_type?: string;
  reference_id?: string;
  reference_number?: string;
  payment_mode: string;
  instrument_number?: string;
  instrument_date?: string;
  narration?: string;
  remarks?: string;
  processed_by: string;
  processed_by_name?: string;
  approved_by?: string;
  approved_at?: string;
  status: string;
  is_cancelled: boolean;
  created_at: string;
  updated_at: string;
}

export interface CashDenomination {
  note_2000: number;
  note_500: number;
  note_200: number;
  note_100: number;
  note_50: number;
  note_20: number;
  note_10: number;
  coin_10: number;
  coin_5: number;
  coin_2: number;
  coin_1: number;
  total_amount?: number;
}

export interface CashPosition {
  id: string;
  tenant_id: string;
  reference_type: string;
  reference_id: string;
  position_date: string;
  opening_balance: number;
  receipts: number;
  payments: number;
  closing_balance: number;
  physical_count?: number;
  variance: number;
  is_reconciled: boolean;
  reconciled_at?: string;
  reconciled_by?: string;
  created_at: string;
  updated_at: string;
}

export interface BranchPerformance {
  id: string;
  tenant_id: string;
  branch_id: string;
  branch_code: string;
  period_type: string;
  period_start: string;
  period_end: string;
  loans_disbursed: number;
  loans_disbursed_amount: number;
  loans_collected: number;
  loans_overdue: number;
  npa_amount: number;
  deposits_opened: number;
  deposits_amount: number;
  deposits_closed: number;
  deposits_matured: number;
  new_customers: number;
  active_customers: number;
  total_customers: number;
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  total_transactions: number;
  cash_transactions: number;
  digital_transactions: number;
  avg_processing_time: number;
  customer_satisfaction: number;
  target_disbursement: number;
  target_collection: number;
  target_achievement: number;
  calculated_at: string;
  created_at: string;
  updated_at: string;
}

export interface BranchTarget {
  id: string;
  tenant_id: string;
  branch_id: string;
  branch_code: string;
  target_period: string;
  target_month?: number;
  target_quarter?: number;
  target_year: number;
  loan_disbursement_target: number;
  loan_collection_target: number;
  loan_count_target: number;
  deposit_mobilization_target: number;
  deposit_count_target: number;
  new_customer_target: number;
  revenue_target: number;
  set_by?: string;
  set_at: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BranchDashboard {
  branch_id: string;
  branch_code: string;
  branch_name: string;
  day_status: DayStatus;
  business_date: string;
  cash_balance: number;
  total_transactions_today: number;
  total_receipts_today: number;
  total_payments_today: number;
  pending_approvals: number;
  active_counters: number;
  staff_present: number;
}

export interface BranchAuditLog {
  id: string;
  tenant_id: string;
  branch_id: string;
  event_type: string;
  event_category: string;
  event_description: string;
  user_id: string;
  user_name?: string;
  user_role?: string;
  reference_type?: string;
  reference_id?: string;
  old_value?: Record<string, any>;
  new_value?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  event_timestamp: string;
  created_at: string;
}

// Form types
export interface OrganizationFormData {
  code: string;
  name: string;
  display_name: string;
  level: OrganizationLevel;
  parent_id?: string;
  manager_id?: string;
  manager_name?: string;
  email?: string;
  phone?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  pincode?: string;
  country?: string;
  status?: BranchStatus;
  is_operational?: boolean;
  opening_date?: string;
  cash_limit?: number;
  daily_transaction_limit?: number;
  settings?: Record<string, any>;
}

export interface BranchFormData {
  organization_id: string;
  branch_code: string;
  branch_name: string;
  branch_type: BranchType;
  ifsc_code?: string;
  micr_code?: string;
  swift_code?: string;
  working_days?: string[];
  working_hours_start?: string;
  working_hours_end?: string;
  branch_manager_id?: string;
  branch_manager_name?: string;
  branch_manager_phone?: string;
  branch_manager_email?: string;
  latitude?: number;
  longitude?: number;
  is_head_office?: boolean;
  is_regional_office?: boolean;
}

export interface DayBeginFormData {
  branch_id: string;
  business_date: string;
  opening_cash_balance: number;
  opening_bank_balance: number;
  remarks?: string;
  checklist?: Record<string, any>;
}

export interface DayEndFormData {
  branch_id: string;
  business_date: string;
  closing_cash_balance: number;
  closing_bank_balance: number;
  remarks?: string;
  checklist?: Record<string, any>;
}

export interface CashTransactionFormData {
  transaction_date: string;
  transaction_type: TransactionType;
  branch_id: string;
  counter_id?: string;
  amount: number;
  from_party_type?: string;
  from_party_id?: string;
  from_party_name?: string;
  to_party_type?: string;
  to_party_id?: string;
  to_party_name?: string;
  reference_type?: string;
  reference_id?: string;
  reference_number?: string;
  payment_mode?: string;
  instrument_number?: string;
  instrument_date?: string;
  narration?: string;
  remarks?: string;
}

export interface CounterFormData {
  branch_id: string;
  counter_number: string;
  counter_name: string;
  counter_type?: string;
  assigned_user_id?: string;
  assigned_user_name?: string;
}

export interface BranchTargetFormData {
  branch_id: string;
  target_period: string;
  target_month?: number;
  target_quarter?: number;
  target_year: number;
  loan_disbursement_target: number;
  loan_collection_target: number;
  loan_count_target: number;
  deposit_mobilization_target: number;
  deposit_count_target: number;
  new_customer_target: number;
  revenue_target: number;
}
