/**
 * Recruitment & Onboarding Module TypeScript Types
 * Maps to backend recruitment models
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum RequisitionStatus {
  DRAFT = 'DRAFT',
  PENDING_APPROVAL = 'PENDING_APPROVAL',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  CLOSED = 'CLOSED'
}

export enum RequisitionPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  URGENT = 'URGENT'
}

export enum EmploymentType {
  FULL_TIME = 'FULL_TIME',
  PART_TIME = 'PART_TIME',
  CONTRACT = 'CONTRACT',
  INTERNSHIP = 'INTERNSHIP'
}

export enum PostingStatus {
  DRAFT = 'DRAFT',
  PUBLISHED = 'PUBLISHED',
  UNPUBLISHED = 'UNPUBLISHED',
  CLOSED = 'CLOSED'
}

export enum PostingChannel {
  CAREER_SITE = 'CAREER_SITE',
  LINKEDIN = 'LINKEDIN',
  NAUKRI = 'NAUKRI',
  INDEED = 'INDEED',
  MONSTER = 'MONSTER',
  INTERNAL = 'INTERNAL'
}

export enum ApplicationStatus {
  NEW = 'NEW',
  SCREENING = 'SCREENING',
  SHORTLISTED = 'SHORTLISTED',
  INTERVIEW = 'INTERVIEW',
  OFFERED = 'OFFERED',
  HIRED = 'HIRED',
  REJECTED = 'REJECTED'
}

export enum ApplicationSource {
  CAREER_SITE = 'CAREER_SITE',
  LINKEDIN = 'LINKEDIN',
  NAUKRI = 'NAUKRI',
  INDEED = 'INDEED',
  REFERRAL = 'REFERRAL',
  WALK_IN = 'WALK_IN',
  CAMPUS = 'CAMPUS',
  CONSULTANT = 'CONSULTANT'
}

export enum InterviewType {
  SCREENING = 'SCREENING',
  TECHNICAL = 'TECHNICAL',
  HR = 'HR',
  MANAGERIAL = 'MANAGERIAL',
  FINAL = 'FINAL'
}

export enum InterviewMode {
  IN_PERSON = 'IN_PERSON',
  VIDEO = 'VIDEO',
  PHONE = 'PHONE'
}

export enum InterviewStatus {
  SCHEDULED = 'SCHEDULED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
  NO_SHOW = 'NO_SHOW',
  RESCHEDULED = 'RESCHEDULED'
}

export enum InterviewRecommendation {
  STRONG_HIRE = 'STRONG_HIRE',
  HIRE = 'HIRE',
  MAYBE = 'MAYBE',
  NO_HIRE = 'NO_HIRE'
}

export enum OnboardingStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED'
}

export enum VerificationStatus {
  INITIATED = 'INITIATED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  ON_HOLD = 'ON_HOLD'
}

export enum VerificationType {
  EDUCATION = 'EDUCATION',
  EMPLOYMENT = 'EMPLOYMENT',
  ADDRESS = 'ADDRESS',
  CRIMINAL = 'CRIMINAL',
  CREDIT = 'CREDIT',
  REFERENCE = 'REFERENCE'
}

export enum VerificationResult {
  CLEAR = 'CLEAR',
  DISCREPANCY = 'DISCREPANCY',
  MAJOR_DISCREPANCY = 'MAJOR_DISCREPANCY',
  UNABLE_TO_VERIFY = 'UNABLE_TO_VERIFY'
}

// ============================================================================
// JOB REQUISITION TYPES
// ============================================================================

export interface JobRequisition {
  id: string;
  tenant_id: string;
  requisition_code: string;
  title: string;
  department_id: string;
  designation_id: string;
  number_of_positions: number;
  employment_type: EmploymentType;
  work_location: string;
  reporting_to_employee_id?: string;
  job_description?: string;
  responsibilities?: string;
  required_qualifications?: string;
  preferred_qualifications?: string;
  required_experience_years?: number;
  min_salary?: number;
  max_salary?: number;
  priority: RequisitionPriority;
  required_by_date?: string;
  justification?: string;
  is_replacement: boolean;
  replacement_for_employee_id?: string;
  requested_by_employee_id?: string;
  requested_date: string;
  status: RequisitionStatus;
  approved_by_employee_id?: string;
  approved_date?: string;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
  
  // Relations
  department?: any;
  designation?: any;
  requested_by?: any;
  approved_by?: any;
  reporting_to?: any;
}

export interface JobRequisitionCreate {
  title: string;
  department_id: string;
  designation_id: string;
  number_of_positions: number;
  employment_type: EmploymentType;
  work_location: string;
  reporting_to_employee_id?: string;
  job_description?: string;
  responsibilities?: string;
  required_qualifications?: string;
  preferred_qualifications?: string;
  required_experience_years?: number;
  min_salary?: number;
  max_salary?: number;
  priority: RequisitionPriority;
  required_by_date?: string;
  justification?: string;
  is_replacement?: boolean;
  replacement_for_employee_id?: string;
  requested_by_employee_id?: string;
}

// ============================================================================
// JOB POSTING TYPES
// ============================================================================

export interface JobPosting {
  id: string;
  tenant_id: string;
  posting_code: string;
  requisition_id: string;
  title: string;
  job_description: string;
  responsibilities?: string;
  required_qualifications?: string;
  preferred_qualifications?: string;
  required_experience_years?: number;
  employment_type: EmploymentType;
  work_location: string;
  salary_range?: string;
  benefits?: string;
  application_deadline?: string;
  posting_channels?: PostingChannel[];
  external_job_board_urls?: Record<string, string>;
  is_internal_only: boolean;
  is_featured: boolean;
  status: PostingStatus;
  published_date?: string;
  closed_date?: string;
  view_count: number;
  created_at: string;
  updated_at: string;
  
  // Relations
  requisition?: JobRequisition;
  applications?: JobApplication[];
}

export interface JobPostingCreate {
  requisition_id: string;
  title: string;
  job_description: string;
  responsibilities?: string;
  required_qualifications?: string;
  preferred_qualifications?: string;
  required_experience_years?: number;
  employment_type: EmploymentType;
  work_location: string;
  salary_range?: string;
  benefits?: string;
  application_deadline?: string;
  posting_channels?: PostingChannel[];
  external_job_board_urls?: Record<string, string>;
  is_internal_only?: boolean;
  is_featured?: boolean;
}

// ============================================================================
// JOB APPLICATION TYPES
// ============================================================================

export interface JobApplication {
  id: string;
  tenant_id: string;
  application_code: string;
  posting_id: string;
  applicant_name: string;
  email: string;
  phone: string;
  current_location?: string;
  current_company?: string;
  current_designation?: string;
  total_experience_years?: number;
  current_salary?: number;
  expected_salary?: number;
  notice_period_days?: number;
  resume_url?: string;
  cover_letter?: string;
  portfolio_url?: string;
  source: ApplicationSource;
  referrer_employee_id?: string;
  applied_date: string;
  screening_score?: number;
  screening_notes?: string;
  assessment_results?: Record<string, any>;
  status: ApplicationStatus;
  current_stage?: string;
  rejection_reason?: string;
  last_activity_date?: string;
  assigned_to_employee_id?: string;
  created_at: string;
  updated_at: string;
  
  // Relations
  posting?: JobPosting;
  referrer?: any;
  assigned_to?: any;
  interviews?: Interview[];
}

export interface JobApplicationCreate {
  posting_id: string;
  applicant_name: string;
  email: string;
  phone: string;
  current_location?: string;
  current_company?: string;
  current_designation?: string;
  total_experience_years?: number;
  current_salary?: number;
  expected_salary?: number;
  notice_period_days?: number;
  resume_url?: string;
  cover_letter?: string;
  portfolio_url?: string;
  source: ApplicationSource;
  referrer_employee_id?: string;
}

// ============================================================================
// INTERVIEW TYPES
// ============================================================================

export interface Interview {
  id: string;
  tenant_id: string;
  interview_code: string;
  application_id: string;
  interview_type: InterviewType;
  round_number: number;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  duration_minutes?: number;
  interview_mode: InterviewMode;
  location?: string;
  meeting_link?: string;
  meeting_id?: string;
  interviewer_ids: string[];
  panel_size: number;
  instructions_for_candidate?: string;
  instructions_for_interviewer?: string;
  status: InterviewStatus;
  cancellation_reason?: string;
  reschedule_count: number;
  feedback_notes?: string;
  rating?: number;
  recommendation?: InterviewRecommendation;
  created_at: string;
  updated_at: string;
  
  // Relations
  application?: JobApplication;
  interviewers?: any[];
}

export interface InterviewCreate {
  application_id: string;
  interview_type: InterviewType;
  round_number: number;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  interview_mode: InterviewMode;
  location?: string;
  meeting_link?: string;
  meeting_id?: string;
  interviewer_ids: string[];
  instructions_for_candidate?: string;
  instructions_for_interviewer?: string;
}

// ============================================================================
// ONBOARDING TYPES
// ============================================================================

export interface ChecklistItem {
  key: string;
  label: string;
  completed: boolean;
  completed_date?: string;
  notes?: string;
}

export interface Onboarding {
  id: string;
  tenant_id: string;
  onboarding_code: string;
  application_id: string;
  employee_id?: string;
  joining_date: string;
  department_id: string;
  designation_id: string;
  reporting_to_employee_id?: string;
  work_location: string;
  offered_salary: number;
  probation_period_months: number;
  checklist_items?: ChecklistItem[];
  documents_required?: string[];
  documents_submitted?: Array<{ document_type: string; url: string; submitted_date: string }>;
  assets_assigned?: string[];
  status: OnboardingStatus;
  completion_percentage: number;
  started_date?: string;
  completed_date?: string;
  buddy_employee_id?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  
  // Relations
  application?: JobApplication;
  employee?: any;
  department?: any;
  designation?: any;
  reporting_to?: any;
  buddy?: any;
  verifications?: BackgroundVerification[];
}

export interface OnboardingCreate {
  application_id: string;
  joining_date: string;
  department_id: string;
  designation_id: string;
  reporting_to_employee_id?: string;
  work_location: string;
  offered_salary: number;
  probation_period_months?: number;
  documents_required?: string[];
  assets_assigned?: string[];
  buddy_employee_id?: string;
  notes?: string;
}

// ============================================================================
// BACKGROUND VERIFICATION TYPES
// ============================================================================

export interface BackgroundVerification {
  id: string;
  tenant_id: string;
  verification_code: string;
  onboarding_id: string;
  verification_type: VerificationType;
  verification_agency?: string;
  agency_reference_id?: string;
  candidate_name: string;
  candidate_email?: string;
  candidate_phone?: string;
  document_type?: string;
  document_url?: string;
  verification_details?: Record<string, any>;
  status: VerificationStatus;
  initiated_date: string;
  completed_date?: string;
  is_verified?: boolean;
  verification_result?: VerificationResult;
  discrepancy_notes?: string;
  verification_report_url?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  
  // Relations
  onboarding?: Onboarding;
}

export interface BackgroundVerificationCreate {
  onboarding_id: string;
  verification_type: VerificationType;
  verification_agency?: string;
  candidate_name: string;
  candidate_email?: string;
  candidate_phone?: string;
  document_type?: string;
  document_url?: string;
  verification_details?: Record<string, any>;
  notes?: string;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface RequisitionDashboardStats {
  total_requisitions: number;
  draft: number;
  pending_approval: number;
  approved: number;
  rejected: number;
  closed: number;
  by_status: Record<string, number>;
}

export interface PostingStatistics {
  posting_id: string;
  posting_code: string;
  title: string;
  status: PostingStatus;
  views: number;
  total_applications: number;
  applications_by_status: Record<string, number>;
  published_date?: string;
  application_deadline?: string;
  days_active: number;
}

// ============================================================================
// KANBAN VIEW TYPES
// ============================================================================

export interface KanbanColumn {
  status: ApplicationStatus;
  label: string;
  applications: JobApplication[];
  count: number;
}
