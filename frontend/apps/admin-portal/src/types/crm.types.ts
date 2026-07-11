/**
 * CRM Lead Management Types
 * TypeScript types for lead management
 */

export enum LeadSource {
  WEBSITE = "website",
  MOBILE_APP = "mobile_app",
  PHONE_CALL = "phone_call",
  WALK_IN = "walk_in",
  EMAIL = "email",
  SMS = "sms",
  WHATSAPP = "whatsapp",
  SOCIAL_MEDIA = "social_media",
  REFERRAL = "referral",
  PARTNER = "partner",
  CAMPAIGN = "campaign",
  EVENT = "event",
  DIRECT = "direct",
  OTHER = "other"
}

export enum LeadStatus {
  NEW = "new",
  CONTACTED = "contacted",
  QUALIFIED = "qualified",
  UNQUALIFIED = "unqualified",
  NURTURING = "nurturing",
  CONVERTED = "converted",
  LOST = "lost",
  DUPLICATE = "duplicate",
  INVALID = "invalid"
}

export enum LeadPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  URGENT = "urgent"
}

export enum LeadTemperature {
  COLD = "cold",
  WARM = "warm",
  HOT = "hot"
}

export enum FollowUpStatus {
  PENDING = "pending",
  COMPLETED = "completed",
  OVERDUE = "overdue",
  CANCELLED = "cancelled"
}

export enum FollowUpType {
  PHONE_CALL = "phone_call",
  EMAIL = "email",
  SMS = "sms",
  WHATSAPP = "whatsapp",
  MEETING = "meeting",
  SITE_VISIT = "site_visit",
  DOCUMENT_COLLECTION = "document_collection",
  OTHER = "other"
}


export interface Lead {
  id: number;
  lead_code: string;
  source: LeadSource;
  source_details?: string;
  first_name: string;
  last_name?: string;
  full_name: string;
  email?: string;
  mobile: string;
  alternate_mobile?: string;
  city_id?: number;
  state_id?: number;
  pincode?: string;
  product_interest?: string;
  loan_amount_required?: number;
  monthly_income?: number;
  occupation?: string;
  company_name?: string;
  lead_score: number;
  score_breakdown?: Record<string, number>;
  lead_temperature: LeadTemperature;
  status: LeadStatus;
  priority: LeadPriority;
  is_qualified: boolean;
  qualification_reason?: string;
  assigned_to_user_id?: number;
  assigned_to_name?: string;
  assigned_date?: string;
  last_contacted_date?: string;
  next_follow_up_date?: string;
  follow_up_count: number;
  response_time_hours?: number;
  is_converted: boolean;
  converted_date?: string;
  conversion_time_hours?: number;
  is_lost: boolean;
  lost_reason?: string;
  is_duplicate: boolean;
  is_active: boolean;
  remarks?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface LeadCreate {
  source: LeadSource;
  source_details?: string;
  first_name: string;
  last_name?: string;
  email?: string;
  mobile: string;
  alternate_mobile?: string;
  city_id?: number;
  state_id?: number;
  pincode?: string;
  product_interest?: string;
  loan_amount_required?: number;
  monthly_income?: number;
  occupation?: string;
  company_name?: string;
  remarks?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  metadata?: Record<string, any>;
}

export interface LeadUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  mobile?: string;
  alternate_mobile?: string;
  city_id?: number;
  state_id?: number;
  pincode?: string;
  product_interest?: string;
  loan_amount_required?: number;
  monthly_income?: number;
  occupation?: string;
  company_name?: string;
  status?: LeadStatus;
  priority?: LeadPriority;
  remarks?: string;
}


export interface LeadFollowUp {
  id: number;
  lead_id: number;
  follow_up_type: FollowUpType;
  scheduled_date: string;
  completed_date?: string;
  status: FollowUpStatus;
  subject: string;
  description?: string;
  outcome?: string;
  next_action?: string;
  customer_interested?: boolean;
  customer_response?: string;
  duration_minutes?: number;
  assigned_to_user_id: number;
  assigned_to_name?: string;
  is_cancelled: boolean;
  created_at: string;
}

export interface LeadFollowUpCreate {
  lead_id: number;
  follow_up_type: FollowUpType;
  scheduled_date: string;
  subject: string;
  description?: string;
  assigned_to_user_id?: number;
}

export interface LeadFollowUpComplete {
  outcome: string;
  next_action?: string;
  customer_interested?: boolean;
  customer_response?: string;
  duration_minutes?: number;
}

export interface LeadActivity {
  id: number;
  lead_id: number;
  activity_type: string;
  activity_title: string;
  activity_description?: string;
  activity_date: string;
  performed_by_name?: string;
  old_value?: Record<string, any>;
  new_value?: Record<string, any>;
  metadata?: Record<string, any>;
  is_system_generated: boolean;
}

export interface LeadDashboardStats {
  total_leads: number;
  new_leads: number;
  contacted_leads: number;
  qualified_leads: number;
  converted_leads: number;
  lost_leads: number;
  hot_leads: number;
  overdue_follow_ups: number;
  avg_lead_score: number;
  avg_conversion_time_hours?: number;
  conversion_rate: number;
  today_follow_ups: number;
}

export interface LeadFilters {
  page?: number;
  page_size?: number;
  search?: string;
  source?: LeadSource;
  status?: LeadStatus;
  priority?: LeadPriority;
  temperature?: LeadTemperature;
  assigned_to_user_id?: number;
  is_qualified?: boolean;
  min_score?: number;
  max_score?: number;
  created_from?: string;
  created_to?: string;
}

export interface PaginatedLeadResponse {
  items: Lead[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface LeadAssignRequest {
  user_id: number;
  notes?: string;
}

export interface LeadQualifyRequest {
  is_qualified: boolean;
  reason: string;
}

export interface LeadConvertRequest {
  create_customer: boolean;
  create_loan_application?: boolean;
  loan_product_id?: number;
  notes?: string;
}

export interface LeadLostRequest {
  reason: string;
  remarks?: string;
}


// ============================================================================
// OPPORTUNITY MANAGEMENT TYPES
// ============================================================================

export enum OpportunityStage {
  PROSPECTING = "prospecting",
  QUALIFICATION = "qualification",
  NEEDS_ANALYSIS = "needs_analysis",
  PROPOSAL = "proposal",
  NEGOTIATION = "negotiation",
  CLOSED_WON = "closed_won",
  CLOSED_LOST = "closed_lost"
}

export enum OpportunityType {
  NEW_BUSINESS = "new_business",
  EXISTING_CUSTOMER = "existing_customer",
  UPSELL = "upsell",
  CROSS_SELL = "cross_sell",
  RENEWAL = "renewal"
}

export enum OpportunityPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

export enum OpportunitySource {
  INBOUND_LEAD = "inbound_lead",
  OUTBOUND_PROSPECTING = "outbound_prospecting",
  REFERRAL = "referral",
  PARTNER = "partner",
  MARKETING_CAMPAIGN = "marketing_campaign",
  TRADE_SHOW = "trade_show",
  WEBSITE = "website",
  EXISTING_CUSTOMER = "existing_customer",
  OTHER = "other"
}

export enum LossReason {
  PRICE_TOO_HIGH = "price_too_high",
  LOST_TO_COMPETITOR = "lost_to_competitor",
  NO_BUDGET = "no_budget",
  NO_DECISION = "no_decision",
  TIMING_NOT_RIGHT = "timing_not_right",
  PRODUCT_NOT_FIT = "product_not_fit",
  WENT_WITH_INCUMBENT = "went_with_incumbent",
  PROJECT_CANCELLED = "project_cancelled",
  UNRESPONSIVE = "unresponsive",
  OTHER = "other"
}

export enum CompetitorPosition {
  UNKNOWN = "unknown",
  WEAK = "weak",
  MODERATE = "moderate",
  STRONG = "strong",
  INCUMBENT = "incumbent"
}

export enum ActivityOutcome {
  POSITIVE = "positive",
  NEUTRAL = "neutral",
  NEGATIVE = "negative",
  NO_ANSWER = "no_answer"
}

export interface Opportunity {
  id: number;
  opportunity_code: string;
  name: string;
  description?: string;
  opportunity_type: OpportunityType;
  source: OpportunitySource;
  
  customer_id?: number;
  lead_id?: number;
  contact_name: string;
  contact_email?: string;
  contact_mobile: string;
  company_name?: string;
  
  estimated_value: number;
  expected_revenue?: number;
  actual_value?: number;
  currency: string;
  
  current_stage: OpportunityStage;
  stage_entered_date: string;
  previous_stage?: OpportunityStage;
  
  win_probability: number;
  priority: OpportunityPriority;
  
  expected_close_date: string;
  actual_close_date?: string;
  first_contact_date?: string;
  
  owner_user_id: number;
  owner_name?: string;
  sales_team_ids?: number[];
  
  is_active: boolean;
  is_won: boolean;
  is_lost: boolean;
  
  won_date?: string;
  won_value?: number;
  won_reason?: string;
  
  lost_date?: string;
  loss_reason?: LossReason;
  loss_reason_details?: string;
  competitor_name?: string;
  
  days_in_pipeline: number;
  days_in_current_stage: number;
  stage_changes_count: number;
  activities_count: number;
  last_activity_date?: string;
  
  next_step?: string;
  pain_points?: string[];
  decision_makers?: Array<{name: string; role: string; email?: string}>;
  buying_process?: string;
  
  budget_confirmed: boolean;
  authority_confirmed: boolean;
  need_confirmed: boolean;
  timeline_confirmed: boolean;
  
  tags?: string[];
  custom_fields?: Record<string, any>;
  
  created_at: string;
  updated_at?: string;
}

export interface OpportunityCreate {
  name: string;
  description?: string;
  opportunity_type: OpportunityType;
  source: OpportunitySource;
  
  customer_id?: number;
  lead_id?: number;
  contact_name: string;
  contact_email?: string;
  contact_mobile: string;
  company_name?: string;
  
  estimated_value: number;
  expected_revenue?: number;
  currency?: string;
  
  current_stage?: OpportunityStage;
  win_probability?: number;
  priority?: OpportunityPriority;
  
  expected_close_date: string;
  
  owner_user_id?: number;
  sales_team_ids?: number[];
  
  next_step?: string;
  pain_points?: string[];
  decision_makers?: Array<{name: string; role: string; email?: string}>;
  buying_process?: string;
  
  budget_confirmed?: boolean;
  authority_confirmed?: boolean;
  need_confirmed?: boolean;
  timeline_confirmed?: boolean;
  
  tags?: string[];
  custom_fields?: Record<string, any>;
}

export interface OpportunityUpdate {
  name?: string;
  description?: string;
  opportunity_type?: OpportunityType;
  
  contact_name?: string;
  contact_email?: string;
  contact_mobile?: string;
  company_name?: string;
  
  estimated_value?: number;
  expected_revenue?: number;
  
  priority?: OpportunityPriority;
  expected_close_date?: string;
  
  next_step?: string;
  pain_points?: string[];
  decision_makers?: Array<{name: string; role: string; email?: string}>;
  buying_process?: string;
  
  budget_confirmed?: boolean;
  authority_confirmed?: boolean;
  need_confirmed?: boolean;
  timeline_confirmed?: boolean;
  
  tags?: string[];
}

export interface OpportunityFilters {
  page?: number;
  page_size?: number;
  search?: string;
  stage?: OpportunityStage;
  opportunity_type?: OpportunityType;
  source?: OpportunitySource;
  priority?: OpportunityPriority;
  owner_user_id?: number;
  is_won?: boolean;
  is_lost?: boolean;
  is_active?: boolean;
  min_value?: number;
  max_value?: number;
  min_probability?: number;
  max_probability?: number;
  close_date_from?: string;
  close_date_to?: string;
  created_from?: string;
  created_to?: string;
}

export interface PaginatedOpportunityResponse {
  items: Opportunity[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface StageTransitionRequest {
  to_stage: OpportunityStage;
  win_probability?: number;
  change_reason?: string;
  notes?: string;
}

export interface StageHistory {
  id: number;
  opportunity_id: number;
  from_stage?: OpportunityStage;
  to_stage: OpportunityStage;
  stage_entered_date: string;
  stage_exited_date?: string;
  days_in_stage?: number;
  probability_before?: number;
  probability_after?: number;
  value_before?: number;
  value_after?: number;
  changed_by_name?: string;
  change_reason?: string;
  notes?: string;
  is_forward: boolean;
  is_current: boolean;
  created_at: string;
}

export interface OpportunityWinRequest {
  won_value: number;
  won_reason?: string;
  actual_close_date?: string;
  notes?: string;
}

export interface OpportunityLossRequest {
  loss_reason: LossReason;
  loss_reason_details: string;
  competitor_name?: string;
  actual_close_date?: string;
  notes?: string;
}

export interface OpportunityActivity {
  id: number;
  opportunity_id: number;
  activity_type: string;
  activity_title: string;
  activity_description?: string;
  activity_date: string;
  duration_minutes?: number;
  outcome?: string;
  outcome_details?: string;
  next_action?: string;
  performed_by_name?: string;
  attendees?: Array<{name: string; email?: string}>;
  is_key_milestone: boolean;
  is_system_generated: boolean;
  created_at: string;
}

export interface OpportunityActivityCreate {
  opportunity_id: number;
  activity_type: string;
  activity_title: string;
  activity_description?: string;
  activity_date?: string;
  duration_minutes?: number;
  outcome?: ActivityOutcome;
  outcome_details?: string;
  next_action?: string;
  attendees?: Array<{name: string; email?: string}>;
  is_key_milestone?: boolean;
}

export interface PaginatedActivityResponse {
  items: OpportunityActivity[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface OpportunityProduct {
  id: number;
  opportunity_id: number;
  product_name: string;
  product_code?: string;
  product_category?: string;
  description?: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  discount_amount: number;
  line_total: number;
  loan_product_id?: number;
  loan_amount?: number;
  loan_tenure_months?: number;
  interest_rate?: number;
  notes?: string;
  sort_order: number;
  created_at: string;
}

export interface OpportunityProductCreate {
  opportunity_id: number;
  product_name: string;
  product_code?: string;
  product_category?: string;
  description?: string;
  quantity?: number;
  unit_price: number;
  discount_percent?: number;
  discount_amount?: number;
  loan_product_id?: number;
  loan_amount?: number;
  loan_tenure_months?: number;
  interest_rate?: number;
  notes?: string;
}

export interface OpportunityCompetitor {
  id: number;
  opportunity_id: number;
  competitor_name: string;
  competitor_product?: string;
  position: CompetitorPosition;
  strengths?: string[];
  weaknesses?: string[];
  competitor_price?: number;
  win_strategy?: string;
  notes?: string;
  is_active: boolean;
  eliminated_date?: string;
  elimination_reason?: string;
  created_at: string;
}

export interface OpportunityCompetitorCreate {
  opportunity_id: number;
  competitor_name: string;
  competitor_product?: string;
  position?: CompetitorPosition;
  strengths?: string[];
  weaknesses?: string[];
  competitor_price?: number;
  win_strategy?: string;
  notes?: string;
}

export interface OpportunityNote {
  id: number;
  opportunity_id: number;
  title?: string;
  content: string;
  note_type?: string;
  is_pinned: boolean;
  created_by_name?: string;
  created_at: string;
  updated_at?: string;
}

export interface OpportunityNoteCreate {
  opportunity_id: number;
  title?: string;
  content: string;
  note_type?: string;
  is_pinned?: boolean;
}

export interface OpportunityDashboardStats {
  total_opportunities: number;
  active_opportunities: number;
  total_pipeline_value: number;
  weighted_pipeline_value: number;
  
  prospecting_count: number;
  qualification_count: number;
  needs_analysis_count: number;
  proposal_count: number;
  negotiation_count: number;
  
  won_count: number;
  won_value: number;
  lost_count: number;
  lost_value: number;
  win_rate: number;
  
  avg_days_in_pipeline: number;
  closing_this_month_count: number;
  closing_this_month_value: number;
  overdue_count: number;
  
  activities_this_week: number;
  opportunities_without_activity_7days: number;
  
  high_probability_count: number;
  high_probability_value: number;
}

export interface PipelineAnalytics {
  stage: OpportunityStage;
  count: number;
  total_value: number;
  avg_value: number;
  avg_days_in_stage: number;
  conversion_rate: number;
}

export interface WinLossAnalysis {
  period: string;
  
  won_count: number;
  won_value: number;
  avg_won_value: number;
  avg_days_to_win: number;
  
  lost_count: number;
  lost_value: number;
  
  win_rate: number;
  
  loss_reasons: Record<string, number>;
  top_competitors: Array<{name: string; losses: number}>;
}

export interface ForecastData {
  period: string;
  best_case: number;
  commit: number;
  most_likely: number;
  pipeline: number;
  opportunities_closing: number;
}
