/**
 * HRMS Training & Development TypeScript Types
 * Training Calendar, Courses, Delivery, Assessment, Certification, LMS Integration, Skill Matrix
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum TrainingType {
  CLASSROOM = "classroom",
  ONLINE = "online",
  WEBINAR = "webinar",
  WORKSHOP = "workshop",
  SEMINAR = "seminar",
  CONFERENCE = "conference",
  ON_THE_JOB = "on_the_job",
  MENTORING = "mentoring",
  SELF_PACED = "self_paced",
  BLENDED = "blended",
}

export enum TrainingCategory {
  TECHNICAL = "technical",
  SOFT_SKILLS = "soft_skills",
  LEADERSHIP = "leadership",
  COMPLIANCE = "compliance",
  PRODUCT = "product",
  SALES = "sales",
  CUSTOMER_SERVICE = "customer_service",
  SAFETY = "safety",
  INDUCTION = "induction",
  PROFESSIONAL = "professional",
}

export enum TrainingStatus {
  DRAFT = "draft",
  SCHEDULED = "scheduled",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  POSTPONED = "postponed",
}

export enum ParticipantStatus {
  NOMINATED = "nominated",
  REGISTERED = "registered",
  CONFIRMED = "confirmed",
  ATTENDED = "attended",
  ABSENT = "absent",
  CANCELLED = "cancelled",
  WAITLISTED = "waitlisted",
}

export enum AssessmentType {
  PRE_TEST = "pre_test",
  POST_TEST = "post_test",
  QUIZ = "quiz",
  ASSIGNMENT = "assignment",
  PRACTICAL = "practical",
  PROJECT = "project",
  VIVA = "viva",
  CASE_STUDY = "case_study",
}

export enum CertificationStatus {
  PENDING = "pending",
  ISSUED = "issued",
  EXPIRED = "expired",
  REVOKED = "revoked",
  RENEWED = "renewed",
}

export enum SkillLevel {
  BEGINNER = "beginner",
  INTERMEDIATE = "intermediate",
  ADVANCED = "advanced",
  EXPERT = "expert",
}

export enum TrainingDeliveryMode {
  INSTRUCTOR_LED = "instructor_led",
  SELF_PACED = "self_paced",
  BLENDED = "blended",
  VIRTUAL = "virtual",
}

// ============================================================================
// TRAINING COURSE TYPES
// ============================================================================

export interface TrainingCourse {
  id: string;
  course_code: string;
  course_name: string;
  course_description?: string;
  training_type: TrainingType;
  training_category: TrainingCategory;
  delivery_mode: TrainingDeliveryMode;
  duration_hours: number;
  duration_days?: number;
  max_participants?: number;
  min_participants?: number;
  target_designation_ids?: string[];
  target_department_ids?: string[];
  experience_level_required?: string;
  prerequisites?: string;
  prerequisite_course_ids?: string[];
  learning_objectives?: string;
  syllabus?: string;
  internal_trainer_id?: string;
  external_trainer_name?: string;
  external_trainer_organization?: string;
  lms_course_id?: string;
  lms_course_url?: string;
  cost_per_participant?: number;
  currency: string;
  provides_certificate: boolean;
  certificate_validity_months?: number;
  is_mandatory: boolean;
  is_compliance_training: boolean;
  is_active: boolean;
  is_published: boolean;
  average_rating?: number;
  total_ratings: number;
  created_at: string;
  updated_at?: string;
}

export interface TrainingCourseCreate {
  course_name: string;
  course_description?: string;
  training_type: TrainingType;
  training_category: TrainingCategory;
  delivery_mode?: TrainingDeliveryMode;
  duration_hours: number;
  duration_days?: number;
  max_participants?: number;
  min_participants?: number;
  target_designation_ids?: string[];
  target_department_ids?: string[];
  prerequisites?: string;
  learning_objectives?: string;
  syllabus?: string;
  internal_trainer_id?: string;
  external_trainer_name?: string;
  lms_course_url?: string;
  cost_per_participant?: number;
  provides_certificate?: boolean;
  certificate_validity_months?: number;
  is_mandatory?: boolean;
  is_compliance_training?: boolean;
  is_active?: boolean;
  is_published?: boolean;
}

export interface TrainingCourseUpdate {
  course_name?: string;
  course_description?: string;
  duration_hours?: number;
  max_participants?: number;
  internal_trainer_id?: string;
  external_trainer_name?: string;
  cost_per_participant?: number;
  is_active?: boolean;
  is_published?: boolean;
}

export interface TrainingCourseListItem {
  id: string;
  course_code: string;
  course_name: string;
  training_type: TrainingType;
  training_category: TrainingCategory;
  duration_hours: number;
  is_active: boolean;
  is_published: boolean;
}

// ============================================================================
// TRAINING SESSION TYPES
// ============================================================================

export interface TrainingSession {
  id: string;
  session_code: string;
  session_name: string;
  course_id: string;
  start_date: string;
  end_date: string;
  start_time?: string;
  end_time?: string;
  location_type: string;
  venue?: string;
  city?: string;
  address?: string;
  virtual_meeting_link?: string;
  trainer_id?: string;
  external_trainer_name?: string;
  max_participants: number;
  enrolled_count: number;
  confirmed_count: number;
  attended_count: number;
  status: TrainingStatus;
  budget_allocated?: number;
  average_feedback_rating?: number;
  created_at: string;
}

export interface TrainingSessionCreate {
  session_name: string;
  course_id: string;
  start_date: string;
  end_date: string;
  start_time?: string;
  end_time?: string;
  location_type?: string;
  venue?: string;
  city?: string;
  address?: string;
  virtual_meeting_link?: string;
  trainer_id?: string;
  external_trainer_name?: string;
  max_participants: number;
  budget_allocated?: number;
  status?: TrainingStatus;
}

export interface TrainingSessionUpdate {
  session_name?: string;
  start_date?: string;
  end_date?: string;
  venue?: string;
  trainer_id?: string;
  status?: TrainingStatus;
  cancellation_reason?: string;
}

export interface TrainingSessionListItem {
  id: string;
  session_code: string;
  session_name: string;
  course_name: string;
  start_date: string;
  end_date: string;
  status: TrainingStatus;
  enrolled_count: number;
  max_participants: number;
}

// ============================================================================
// PARTICIPANT TYPES
// ============================================================================

export interface TrainingParticipant {
  id: string;
  session_id: string;
  employee_id: string;
  employee_name: string;
  employee_code: string;
  nominated_by_id?: string;
  nomination_reason?: string;
  status: ParticipantStatus;
  attended: boolean;
  final_score?: number;
  passed: boolean;
  certificate_issued: boolean;
}

export interface TrainingParticipantCreate {
  session_id: string;
  employee_id: string;
  nominated_by_id?: string;
  nomination_reason?: string;
  status?: ParticipantStatus;
}

export interface TrainingParticipantUpdate {
  status?: ParticipantStatus;
  attended?: boolean;
  attendance_percentage?: number;
  feedback_rating?: number;
  feedback_comments?: string;
}

// ============================================================================
// ASSESSMENT TYPES
// ============================================================================

export interface TrainingAssessment {
  id: string;
  assessment_code: string;
  assessment_name: string;
  assessment_description?: string;
  course_id?: string;
  session_id?: string;
  assessment_type: AssessmentType;
  total_marks: number;
  passing_marks: number;
  duration_minutes?: number;
  scheduled_date?: string;
  question_count?: number;
  is_published: boolean;
  created_at: string;
}

export interface TrainingAssessmentCreate {
  assessment_name: string;
  assessment_description?: string;
  course_id?: string;
  session_id?: string;
  assessment_type: AssessmentType;
  total_marks?: number;
  passing_marks: number;
  duration_minutes?: number;
  scheduled_date?: string;
}

// ============================================================================
// CERTIFICATION TYPES
// ============================================================================

export interface TrainingCertification {
  id: string;
  certificate_number: string;
  certificate_name: string;
  course_id?: string;
  session_id?: string;
  employee_id: string;
  employee_name: string;
  course_name?: string;
  issue_date: string;
  expiry_date?: string;
  status: CertificationStatus;
  certificate_url?: string;
  verification_code?: string;
}

export interface TrainingCertificationCreate {
  certificate_name: string;
  course_id?: string;
  session_id?: string;
  employee_id: string;
  issue_date: string;
  expiry_date?: string;
  status?: CertificationStatus;
}

// ============================================================================
// SKILL MATRIX TYPES
// ============================================================================

export interface Skill {
  id: string;
  skill_code: string;
  skill_name: string;
  skill_description?: string;
  skill_category?: string;
  skill_type?: string;
  parent_skill_id?: string;
  is_active: boolean;
  created_at: string;
}

export interface SkillCreate {
  skill_name: string;
  skill_description?: string;
  skill_category?: string;
  skill_type?: string;
  parent_skill_id?: string;
  is_active?: boolean;
}

export interface EmployeeSkill {
  id: string;
  employee_id: string;
  skill_id: string;
  skill_name: string;
  skill_category?: string;
  proficiency_level: SkillLevel;
  proficiency_percentage?: number;
  is_certified: boolean;
  certification_name?: string;
  years_of_experience?: number;
  is_verified: boolean;
}

export interface EmployeeSkillCreate {
  employee_id: string;
  skill_id: string;
  proficiency_level: SkillLevel;
  proficiency_percentage?: number;
  is_certified?: boolean;
  certification_name?: string;
  years_of_experience?: number;
}

// ============================================================================
// DASHBOARD & STATISTICS
// ============================================================================

export interface TrainingDashboardStats {
  total_courses: number;
  active_courses: number;
  total_sessions: number;
  upcoming_sessions: number;
  ongoing_sessions: number;
  completed_sessions: number;
  total_participants: number;
  certifications_issued: number;
  average_training_rating?: number;
  compliance_completion_rate?: number;
  by_category?: Record<string, number>;
  by_type?: Record<string, number>;
}

export interface TrainingCalendarItem {
  id: string;
  session_code: string;
  session_name: string;
  course_name: string;
  start_date: string;
  end_date: string;
  start_time?: string;
  venue?: string;
  trainer_name?: string;
  enrolled_count: number;
  max_participants: number;
  status: TrainingStatus;
}

// ============================================================================
// PAGINATION
// ============================================================================

export interface PaginatedTrainingCourseResponse {
  items: TrainingCourse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface PaginatedTrainingSessionResponse {
  items: TrainingSession[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface PaginatedParticipantResponse {
  items: TrainingParticipant[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// ============================================================================
// FILTERS
// ============================================================================

export interface TrainingCourseFilters {
  search?: string;
  training_type?: TrainingType;
  training_category?: TrainingCategory;
  is_active?: boolean;
  is_published?: boolean;
  is_mandatory?: boolean;
}

export interface TrainingSessionFilters {
  course_id?: string;
  status?: TrainingStatus;
  start_date_from?: string;
  start_date_to?: string;
}
