/**
 * Collection Management Type Definitions
 * Matches backend models and schemas
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum ActionType {
  CALL = "call",
  SMS = "sms",
  EMAIL = "email",
  WHATSAPP = "whatsapp",
  FIELD_VISIT = "field_visit",
  LEGAL_NOTICE = "legal_notice",
  LEGAL_ACTION = "legal_action"
}

export enum ActionStatus {
  PENDING = "pending",
  SCHEDULED = "scheduled",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled"
}

export enum TemplateType {
  SMS = "sms",
  EMAIL = "email",
  WHATSAPP = "whatsapp",
  LETTER = "letter",
  NOTICE = "notice"
}

export enum VisitStatus {
  SCHEDULED = "scheduled",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  CUSTOMER_NOT_FOUND = "customer_not_found",
  REFUSED_TO_MEET = "refused_to_meet"
}

export enum VisitDisposition {
  MET_CUSTOMER = "met_customer",
  NOT_HOME = "not_home",
  REFUSED_TO_MEET = "refused_to_meet",
  PAID = "paid",
  PROMISED_TO_PAY = "promised_to_pay",
  REQUESTED_SETTLEMENT = "requested_settlement",
  CUSTOMER_RELOCATED = "customer_relocated",
  HOSTILE = "hostile"
}

export enum PromiseStatus {
  PENDING = "pending",
  KEPT = "kept",
  PARTIALLY_KEPT = "partially_kept",
  BROKEN = "broken",
  RESCHEDULED = "rescheduled"
}

export enum PromiseSource {
  CALL = "call",
  FIELD_VISIT = "field_visit",
  EMAIL = "email",
  CUSTOMER_PORTAL = "customer_portal",
  BRANCH_VISIT = "branch_visit"
}

export enum LegalNoticeType {
  DEMAND_NOTICE = "demand_notice",
  SECTION_13 = "section_13",
  SARFAESI_NOTICE = "sarfaesi_notice",
  FINAL_NOTICE = "final_notice",
  LEGAL_NOTICE = "legal_notice"
}

export enum NoticeStage {
  FIRST = "first",
  SECOND = "second",
  FINAL = "final"
}

export enum DeliveryStatus {
  PENDING = "pending",
  DISPATCHED = "dispatched",
  DELIVERED = "delivered",
  RETURNED = "returned",
  UNCLAIMED = "unclaimed"
}

export enum CaseType {
  CIVIL_SUIT = "civil_suit",
  ARBITRATION = "arbitration",
  DRT = "drt",
  SARFAESI = "sarfaesi",
  CRIMINAL = "criminal"
}

export enum CaseStatus {
  FILED = "filed",
  PENDING = "pending",
  HEARING = "hearing",
  JUDGEMENT = "judgement",
  CLOSED = "closed",
  WITHDRAWN = "withdrawn"
}

export enum CaseOutcome {
  WON = "won",
  LOST = "lost",
  SETTLED = "settled",
  WITHDRAWN = "withdrawn",
  PENDING = "pending"
}

export enum SettlementType {
  ONE_TIME_SETTLEMENT = "one_time_settlement",
  COMPROMISE_SETTLEMENT = "compromise_settlement",
  COURT_SETTLEMENT = "court_settlement",
  PRE_CLOSURE = "pre_closure",
  NEGOTIATED = "negotiated"
}

export enum SettlementStatus {
  SUBMITTED = "submitted",
  UNDER_REVIEW = "under_review",
  APPROVED = "approved",
  REJECTED = "rejected",
  CUSTOMER_ACCEPTED = "customer_accepted",
  CUSTOMER_REJECTED = "customer_rejected",
  COMPLETED = "completed",
  BREACHED = "breached"
}

export enum PaymentTerms {
  LUMP_SUM = "lump_sum",
  INSTALLMENTS = "installments"
}

// ============================================================================
// COLLECTION STRATEGY TYPES
// ============================================================================

export interface CollectionStrategy {
  id: number;
  strategy_name: string;
  strategy_code: string;
  description?: string;
  dpd_min: number;
  dpd_max: number;
  action_type: string;
  frequency_days: number;
  max_attempts: number;
  template_id?: number;
  is_active: boolean;
  priority: number;
  created_at: string;
}

export interface CommunicationTemplate {
  id: number;
  template_code: string;
  template_name: string;
  template_type: string;
  content: string;
  subject?: string;
  language: string;
  variables?: string[];
  dpd_bucket?: string;
  category?: string;
  is_active: boolean;
  created_at: string;
}

export interface CollectionAction {
  id: number;
  loan_account_id: number;
  customer_id: number;
  action_type: string;
  action_date: string;
  status: string;
  response_received: boolean;
  response_details?: string;
  next_action_date?: string;
  notes?: string;
  created_at: string;
}

// ============================================================================
// FIELD AGENT TYPES
// ============================================================================

export interface Territory {
  id: number;
  territory_code: string;
  territory_name: string;
  state?: string;
  district?: string;
  city?: string;
  pincode_list?: string[];
  is_active: boolean;
  created_at: string;
}

export interface FieldAgent {
  id: number;
  agent_code: string;
  full_name: string;
  mobile: string;
  email?: string;
  territory_id: number;
  employment_type: string;
  monthly_collection_target: number;
  monthly_visit_target: number;
  total_collection_amount: number;
  total_visits_completed: number;
  success_rate: number;
  is_active: boolean;
  created_at: string;
}

export interface FieldVisit {
  id: number;
  loan_account_id: number;
  customer_id: number;
  agent_id: number;
  visit_date: string;
  scheduled_time?: string;
  visit_status: string;
  visit_type: string;
  disposition?: string;
  amount_collected: number;
  payment_mode?: string;
  location_lat?: number;
  location_lng?: number;
  visit_notes?: string;
  next_visit_date?: string;
  created_at: string;
}

export interface VisitTarget {
  id: number;
  agent_id: number;
  month: number;
  year: number;
  target_collection_amount: number;
  target_visit_count: number;
  achieved_collection_amount: number;
  achieved_visit_count: number;
  achievement_percentage: number;
}

export interface AgentDashboard {
  agent: {
    id: number;
    name: string;
    code: string;
    mobile: string;
  };
  today: {
    date: string;
    total_visits: number;
    pending_visits: number;
    completed_visits: number;
    collection_amount: number;
  };
  monthly_performance: {
    agent_id: number;
    month: number;
    year: number;
    target_collection_amount: number;
    achieved_collection_amount: number;
    collection_achievement_percentage: number;
    target_visit_count: number;
    achieved_visit_count: number;
    visit_achievement_percentage: number;
  };
  upcoming_visits: Array<{
    id: number;
    loan_account_id: number;
    customer_id: number;
    scheduled_time?: string;
    visit_type: string;
    status: string;
  }>;
}

// ============================================================================
// PAYMENT PROMISE TYPES
// ============================================================================

export interface PaymentPromise {
  id: number;
  loan_account_id: number;
  customer_id: number;
  promise_amount: number;
  promise_date: string;
  promised_on_date: string;
  promised_by: string;
  promise_source: string;
  promise_status: string;
  actual_payment_amount?: number;
  actual_payment_date?: string;
  notes?: string;
  reminder_sent: boolean;
  created_at: string;
}

export interface PromiseAnalytics {
  period: {
    from_date: string;
    to_date: string;
  };
  summary: {
    total_promises: number;
    total_promised_amount: number;
    total_collected_amount: number;
    fulfillment_rate: number;
  };
  status_breakdown: Record<string, {
    count: number;
    promised_amount: number;
    collected_amount: number;
  }>;
}

// ============================================================================
// LEGAL & RECOVERY TYPES
// ============================================================================

export interface LegalNotice {
  id: number;
  loan_account_id: number;
  customer_id: number;
  notice_type: string;
  notice_stage: string;
  notice_number: string;
  notice_date: string;
  notice_amount_demanded: number;
  dispatch_mode: string;
  delivery_status: string;
  delivery_date?: string;
  response_received: boolean;
  response_date?: string;
  created_at: string;
}

export interface LegalCase {
  id: number;
  loan_account_id: number;
  customer_id: number;
  case_number: string;
  case_type: string;
  court_name?: string;
  filing_date: string;
  claim_amount: number;
  case_status: string;
  next_hearing_date?: string;
  total_hearings: number;
  case_outcome?: string;
  total_legal_cost: number;
  created_at: string;
}

export interface RecoveryAgency {
  id: number;
  agency_code: string;
  agency_name: string;
  contact_person?: string;
  mobile: string;
  email?: string;
  commission_percentage: number;
  total_cases_assigned: number;
  total_amount_recovered: number;
  performance_rating?: number;
  is_active: boolean;
  created_at: string;
}

export interface RecoveryAction {
  id: number;
  loan_account_id: number;
  customer_id: number;
  action_type: string;
  action_date: string;
  action_status: string;
  recovery_amount: number;
  recovery_cost: number;
  net_recovery: number;
  created_at: string;
}

// ============================================================================
// SETTLEMENT/OTS TYPES
// ============================================================================

export interface WaiverPolicy {
  id: number;
  policy_code: string;
  policy_name: string;
  description?: string;
  min_dpd: number;
  max_dpd: number;
  max_waiver_percentage_interest: number;
  max_waiver_percentage_penal: number;
  min_recovery_percentage: number;
  is_active: boolean;
  created_at: string;
}

export interface SettlementProposal {
  id: number;
  loan_account_id: number;
  customer_id: number;
  customer_name?: string;
  customer_contact?: string;
  proposal_number: string;
  proposal_type?: string;
  
  // Outstanding amounts
  original_outstanding: number;
  principal_outstanding: number;
  interest_outstanding: number;
  penalty_outstanding: number;
  other_charges: number;
  
  // Settlement terms
  settlement_amount: number;
  waiver_amount: number;
  payment_terms: string;
  number_of_installments?: number;
  installment_frequency?: string;
  valid_until?: string;
  
  // NPV Analysis (optional)
  npv_analysis?: {
    npv_without_settlement: number;
    npv_with_settlement: number;
    npv_benefit: number;
    estimated_recovery_time: number;
    estimated_recovery_amount: number;
    discount_rate: number;
  };
  
  // Justification
  reason: string;
  justification?: string;
  internal_notes?: string;
  
  // Status and workflow
  status: string;
  created_at: string;
  created_by: string;
  approved_at?: string;
  approved_by?: string;
  rejected_at?: string;
  rejected_by?: string;
  completed_at?: string;
  approval_notes?: string;
  rejection_reason?: string;
}

export interface SettlementAgreement {
  id: number;
  proposal_id: number;
  agreement_number: string;
  agreement_date: string;
  settlement_amount: number;
  payment_deadline: string;
  payment_schedule?: Array<{
    installment_number: number;
    due_date: string;
    amount: number;
  }>;
  agreement_status: string;
  customer_signed_date?: string;
  bank_signed_date?: string;
  created_at: string;
}

// ============================================================================
// COMMON TYPES
// ============================================================================

export interface PaginationInfo {
  total: number;
  skip: number;
  limit: number;
  pages: number;
}

export interface ListResponse<T> {
  items: T[];
  pagination: PaginationInfo;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
}
