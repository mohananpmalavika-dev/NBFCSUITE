/**
 * Performance Management TypeScript Types
 * Types for Goal Setting, Appraisals, 360 Feedback, Ratings & IDP
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum GoalType {
  KRA = 'kra',
  KPI = 'kpi',
  OBJECTIVE = 'objective',
  PROJECT = 'project'
}

export enum GoalStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum GoalPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum AppraisalCycleStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  GOAL_SETTING = 'goal_setting',
  SELF_ASSESSMENT = 'self_assessment',
  MANAGER_REVIEW = 'manager_review',
  NORMALIZATION = 'normalization',
  HR_REVIEW = 'hr_review',
  COMPLETED = 'completed',
  CLOSED = 'closed',
  CANCELLED = 'cancelled'
}

export enum AppraisalStatus {
  NOT_STARTED = 'not_started',
  GOAL_SETTING_PENDING = 'goal_setting_pending',
  GOAL_SETTING_SUBMITTED = 'goal_setting_submitted',
  GOALS_APPROVED = 'goals_approved',
  SELF_ASSESSMENT_PENDING = 'self_assessment_pending',
  SELF_ASSESSMENT_SUBMITTED = 'self_assessment_submitted',
  MANAGER_REVIEW_PENDING = 'manager_review_pending',
  MANAGER_REVIEW_SUBMITTED = 'manager_review_submitted',
  HR_REVIEW_PENDING = 'hr_review_pending',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}


export enum RatingScale {
  OUTSTANDING = 'outstanding',
  EXCEEDS_EXPECTATIONS = 'exceeds_expectations',
  MEETS_EXPECTATIONS = 'meets_expectations',
  NEEDS_IMPROVEMENT = 'needs_improvement',
  UNSATISFACTORY = 'unsatisfactory'
}

export enum FeedbackType {
  SELF = 'self',
  MANAGER = 'manager',
  PEER = 'peer',
  SUBORDINATE = 'subordinate',
  CUSTOMER = 'customer',
  OTHER = 'other'
}

export enum FeedbackStatus {
  PENDING = 'pending',
  SUBMITTED = 'submitted',
  ACKNOWLEDGED = 'acknowledged'
}

export enum IncrementType {
  ANNUAL = 'annual',
  PROMOTION = 'promotion',
  SPECIAL = 'special',
  PERFORMANCE_BASED = 'performance_based',
  MARKET_CORRECTION = 'market_correction'
}

export enum IDPStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum DevelopmentActivityType {
  TRAINING = 'training',
  CERTIFICATION = 'certification',
  WORKSHOP = 'workshop',
  MENTORING = 'mentoring',
  JOB_ROTATION = 'job_rotation',
  SELF_LEARNING = 'self_learning',
  CONFERENCE = 'conference',
  PROJECT = 'project'
}

// ============================================================================
// APPRAISAL CYCLE TYPES
// ============================================================================

export interface AppraisalCycle {
  id: string;
  tenant_id: string;
  cycle_code: string;
  cycle_name: string;
  cycle_description?: string;
  fiscal_year: string;
  start_date: string;
  end_date: string;
  goal_setting_start?: string;
  goal_setting_end?: string;
  self_assessment_start?: string;
  self_assessment_end?: string;
  manager_review_start?: string;
  manager_review_end?: string;
  normalization_start?: string;
  normalization_end?: string;
  hr_review_start?: string;
  hr_review_end?: string;
  status: AppraisalCycleStatus;
  enable_360_feedback: boolean;
  enable_self_assessment: boolean;
  enable_goal_setting: boolean;
  total_employees: number;
  completed_appraisals: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AppraisalCycleCreate {
  cycle_code: string;
  cycle_name: string;
  cycle_description?: string;
  fiscal_year: string;
  start_date: string;
  end_date: string;
  goal_setting_start?: string;
  goal_setting_end?: string;
  self_assessment_start?: string;
  self_assessment_end?: string;
  manager_review_start?: string;
  manager_review_end?: string;
  normalization_start?: string;
  normalization_end?: string;
  hr_review_start?: string;
  hr_review_end?: string;
  enable_360_feedback?: boolean;
  enable_self_assessment?: boolean;
  enable_goal_setting?: boolean;
}

export interface AppraisalCycleUpdate {
  cycle_name?: string;
  cycle_description?: string;
  status?: AppraisalCycleStatus;
  goal_setting_start?: string;
  goal_setting_end?: string;
  self_assessment_start?: string;
  self_assessment_end?: string;
  manager_review_start?: string;
  manager_review_end?: string;
  normalization_start?: string;
  normalization_end?: string;
  hr_review_start?: string;
  hr_review_end?: string;
  enable_360_feedback?: boolean;
  enable_self_assessment?: boolean;
  enable_goal_setting?: boolean;
}


// ============================================================================
// PERFORMANCE GOAL TYPES (KRA/KPI)
// ============================================================================

export interface PerformanceGoal {
  id: string;
  tenant_id: string;
  goal_code: string;
  goal_title: string;
  goal_description?: string;
  goal_type: GoalType;
  goal_priority: GoalPriority;
  employee_id: string;
  appraisal_cycle_id: string;
  measurement_criteria?: string;
  target_value?: string;
  achieved_value?: string;
  uom?: string;
  weightage?: number;
  start_date: string;
  target_date: string;
  completion_date?: string;
  progress_percentage: number;
  status: GoalStatus;
  submitted_date?: string;
  approved_by_id?: string;
  approved_date?: string;
  rejection_reason?: string;
  employee_comments?: string;
  manager_comments?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PerformanceGoalCreate {
  goal_code: string;
  goal_title: string;
  goal_description?: string;
  goal_type: GoalType;
  goal_priority: GoalPriority;
  employee_id: string;
  appraisal_cycle_id: string;
  measurement_criteria?: string;
  target_value?: string;
  uom?: string;
  weightage?: number;
  start_date: string;
  target_date: string;
}

export interface PerformanceGoalUpdate {
  goal_title?: string;
  goal_description?: string;
  goal_priority?: GoalPriority;
  measurement_criteria?: string;
  target_value?: string;
  achieved_value?: string;
  uom?: string;
  weightage?: number;
  target_date?: string;
  completion_date?: string;
  progress_percentage?: number;
  status?: GoalStatus;
  employee_comments?: string;
  manager_comments?: string;
}

// ============================================================================
// EMPLOYEE APPRAISAL TYPES
// ============================================================================

export interface EmployeeAppraisal {
  id: string;
  tenant_id: string;
  appraisal_code: string;
  employee_id: string;
  appraisal_cycle_id: string;
  reviewer_id?: string;
  status: AppraisalStatus;
  goals_submitted_date?: string;
  goals_approved_date?: string;
  self_assessment_submitted_date?: string;
  self_rating?: RatingScale;
  self_rating_numeric?: number;
  self_comments?: string;
  key_achievements?: string;
  areas_of_improvement?: string;
  manager_review_submitted_date?: string;
  manager_rating?: RatingScale;
  manager_rating_numeric?: number;
  manager_comments?: string;
  manager_strengths?: string;
  manager_development_areas?: string;
  hr_review_submitted_date?: string;
  hr_comments?: string;
  final_rating?: RatingScale;
  final_rating_numeric?: number;
  normalized_rating?: RatingScale;
  normalized_rating_numeric?: number;
  overall_goal_achievement_percentage?: number;
  recommended_increment_percentage?: number;
  recommended_promotion: boolean;
  recommended_promotion_designation_id?: string;
  completed_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmployeeAppraisalCreate {
  appraisal_code: string;
  employee_id: string;
  appraisal_cycle_id: string;
  reviewer_id?: string;
}

export interface SelfAssessmentSubmit {
  self_rating: RatingScale;
  self_rating_numeric: number;
  self_comments?: string;
  key_achievements?: string;
  areas_of_improvement?: string;
}

export interface ManagerReviewSubmit {
  manager_rating: RatingScale;
  manager_rating_numeric: number;
  manager_comments?: string;
  manager_strengths?: string;
  manager_development_areas?: string;
  recommended_increment_percentage?: number;
  recommended_promotion: boolean;
  recommended_promotion_designation_id?: string;
}

export interface HRReviewSubmit {
  hr_comments?: string;
  final_rating: RatingScale;
  final_rating_numeric: number;
  normalized_rating?: RatingScale;
  normalized_rating_numeric?: number;
}


// ============================================================================
// 360 FEEDBACK TYPES
// ============================================================================

export interface FeedbackRequest {
  id: string;
  tenant_id: string;
  request_code: string;
  employee_id: string;
  reviewer_id: string;
  appraisal_cycle_id: string;
  feedback_type: FeedbackType;
  requested_date: string;
  due_date?: string;
  status: FeedbackStatus;
  reminder_sent_count: number;
  last_reminder_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FeedbackRequestCreate {
  request_code: string;
  employee_id: string;
  reviewer_id: string;
  appraisal_cycle_id: string;
  feedback_type: FeedbackType;
  due_date?: string;
}

export interface FeedbackResponse {
  id: string;
  tenant_id: string;
  feedback_request_id: string;
  employee_appraisal_id?: string;
  overall_rating?: RatingScale;
  overall_rating_numeric?: number;
  technical_skills_rating?: number;
  communication_skills_rating?: number;
  teamwork_rating?: number;
  leadership_rating?: number;
  problem_solving_rating?: number;
  strengths?: string;
  areas_for_improvement?: string;
  additional_comments?: string;
  submitted_date: string;
  acknowledged_date?: string;
  is_anonymous: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FeedbackResponseSubmit {
  overall_rating?: RatingScale;
  overall_rating_numeric?: number;
  technical_skills_rating?: number;
  communication_skills_rating?: number;
  teamwork_rating?: number;
  leadership_rating?: number;
  problem_solving_rating?: number;
  strengths?: string;
  areas_for_improvement?: string;
  additional_comments?: string;
  is_anonymous: boolean;
}

// ============================================================================
// PERFORMANCE INCREMENT TYPES
// ============================================================================

export interface PerformanceIncrement {
  id: string;
  tenant_id: string;
  increment_code: string;
  employee_id: string;
  employee_appraisal_id?: string;
  appraisal_cycle_id?: string;
  increment_type: IncrementType;
  current_ctc: number;
  increment_percentage: number;
  increment_amount: number;
  revised_ctc: number;
  effective_from: string;
  recommended_by_id?: string;
  approved_by_id?: string;
  approved_date?: string;
  is_approved: boolean;
  is_processed: boolean;
  processed_date?: string;
  remarks?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PerformanceIncrementCreate {
  increment_code: string;
  employee_id: string;
  employee_appraisal_id?: string;
  appraisal_cycle_id?: string;
  increment_type: IncrementType;
  current_ctc: number;
  increment_percentage: number;
  increment_amount: number;
  revised_ctc: number;
  effective_from: string;
  recommended_by_id?: string;
  remarks?: string;
}

export interface PerformanceIncrementUpdate {
  increment_percentage?: number;
  increment_amount?: number;
  revised_ctc?: number;
  effective_from?: string;
  remarks?: string;
  is_approved?: boolean;
  is_processed?: boolean;
}

// ============================================================================
// INDIVIDUAL DEVELOPMENT PLAN (IDP) TYPES
// ============================================================================

export interface IndividualDevelopmentPlan {
  id: string;
  tenant_id: string;
  idp_code: string;
  idp_title: string;
  employee_id: string;
  appraisal_cycle_id?: string;
  career_goal?: string;
  target_role?: string;
  target_designation_id?: string;
  current_skills?: string;
  required_skills?: string;
  skill_gaps?: string;
  plan_start_date: string;
  plan_end_date: string;
  status: IDPStatus;
  submitted_date?: string;
  approved_by_id?: string;
  approved_date?: string;
  overall_progress_percentage: number;
  employee_notes?: string;
  manager_notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface IndividualDevelopmentPlanCreate {
  idp_code: string;
  idp_title: string;
  employee_id: string;
  appraisal_cycle_id?: string;
  career_goal?: string;
  target_role?: string;
  target_designation_id?: string;
  current_skills?: string;
  required_skills?: string;
  skill_gaps?: string;
  plan_start_date: string;
  plan_end_date: string;
}

export interface IndividualDevelopmentPlanUpdate {
  idp_title?: string;
  career_goal?: string;
  target_role?: string;
  target_designation_id?: string;
  current_skills?: string;
  required_skills?: string;
  skill_gaps?: string;
  plan_end_date?: string;
  status?: IDPStatus;
  overall_progress_percentage?: number;
  employee_notes?: string;
  manager_notes?: string;
}

// ============================================================================
// DEVELOPMENT ACTIVITY TYPES
// ============================================================================

export interface DevelopmentActivity {
  id: string;
  tenant_id: string;
  activity_code: string;
  activity_title: string;
  activity_description?: string;
  idp_id: string;
  activity_type: DevelopmentActivityType;
  provider_name?: string;
  course_name?: string;
  duration_hours?: number;
  cost?: number;
  planned_start_date?: string;
  planned_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  is_completed: boolean;
  completion_percentage: number;
  certification_obtained?: string;
  certificate_url?: string;
  learning_outcome?: string;
  employee_feedback?: string;
  manager_feedback?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DevelopmentActivityCreate {
  activity_code: string;
  activity_title: string;
  activity_description?: string;
  idp_id: string;
  activity_type: DevelopmentActivityType;
  provider_name?: string;
  course_name?: string;
  duration_hours?: number;
  cost?: number;
  planned_start_date?: string;
  planned_end_date?: string;
}

export interface DevelopmentActivityUpdate {
  activity_title?: string;
  activity_description?: string;
  provider_name?: string;
  course_name?: string;
  duration_hours?: number;
  cost?: number;
  planned_start_date?: string;
  planned_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  is_completed?: boolean;
  completion_percentage?: number;
  certification_obtained?: string;
  certificate_url?: string;
  learning_outcome?: string;
  employee_feedback?: string;
  manager_feedback?: string;
}

// ============================================================================
// COMMON TYPES
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface MessageResponse {
  message: string;
  success: boolean;
}

// ============================================================================
// FILTER & QUERY TYPES
// ============================================================================

export interface AppraisalCycleFilters {
  status?: AppraisalCycleStatus;
  fiscal_year?: string;
  skip?: number;
  limit?: number;
}

export interface PerformanceGoalFilters {
  employee_id?: string;
  appraisal_cycle_id?: string;
  status?: GoalStatus;
}

export interface EmployeeAppraisalFilters {
  employee_id?: string;
  appraisal_cycle_id?: string;
  status?: AppraisalStatus;
  skip?: number;
  limit?: number;
}

export interface FeedbackRequestFilters {
  reviewer_id?: string;
  status?: FeedbackStatus;
}

export interface IncrementFilters {
  employee_id?: string;
  appraisal_cycle_id?: string;
}

export interface IDPFilters {
  employee_id?: string;
  status?: IDPStatus;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export const RATING_SCALE_LABELS: Record<RatingScale, string> = {
  [RatingScale.OUTSTANDING]: 'Outstanding (5)',
  [RatingScale.EXCEEDS_EXPECTATIONS]: 'Exceeds Expectations (4)',
  [RatingScale.MEETS_EXPECTATIONS]: 'Meets Expectations (3)',
  [RatingScale.NEEDS_IMPROVEMENT]: 'Needs Improvement (2)',
  [RatingScale.UNSATISFACTORY]: 'Unsatisfactory (1)'
};

export const RATING_SCALE_VALUES: Record<RatingScale, number> = {
  [RatingScale.OUTSTANDING]: 5,
  [RatingScale.EXCEEDS_EXPECTATIONS]: 4,
  [RatingScale.MEETS_EXPECTATIONS]: 3,
  [RatingScale.NEEDS_IMPROVEMENT]: 2,
  [RatingScale.UNSATISFACTORY]: 1
};

export const GOAL_TYPE_LABELS: Record<GoalType, string> = {
  [GoalType.KRA]: 'Key Result Area (KRA)',
  [GoalType.KPI]: 'Key Performance Indicator (KPI)',
  [GoalType.OBJECTIVE]: 'Objective',
  [GoalType.PROJECT]: 'Project'
};

export const FEEDBACK_TYPE_LABELS: Record<FeedbackType, string> = {
  [FeedbackType.SELF]: 'Self',
  [FeedbackType.MANAGER]: 'Manager',
  [FeedbackType.PEER]: 'Peer',
  [FeedbackType.SUBORDINATE]: 'Subordinate',
  [FeedbackType.CUSTOMER]: 'Customer',
  [FeedbackType.OTHER]: 'Other'
};

export const ACTIVITY_TYPE_LABELS: Record<DevelopmentActivityType, string> = {
  [DevelopmentActivityType.TRAINING]: 'Training',
  [DevelopmentActivityType.CERTIFICATION]: 'Certification',
  [DevelopmentActivityType.WORKSHOP]: 'Workshop',
  [DevelopmentActivityType.MENTORING]: 'Mentoring',
  [DevelopmentActivityType.JOB_ROTATION]: 'Job Rotation',
  [DevelopmentActivityType.SELF_LEARNING]: 'Self Learning',
  [DevelopmentActivityType.CONFERENCE]: 'Conference',
  [DevelopmentActivityType.PROJECT]: 'Project'
};
