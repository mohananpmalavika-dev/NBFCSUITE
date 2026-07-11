/**
 * HRMS Training & Development API Service
 * Complete service layer for Training operations
 */

import { apiClient } from "@/lib/api/client";
import type {
  // Training Course
  TrainingCourse,
  TrainingCourseCreate,
  TrainingCourseUpdate,
  TrainingCourseListItem,
  PaginatedTrainingCourseResponse,
  TrainingCourseFilters,
  
  // Training Session
  TrainingSession,
  TrainingSessionCreate,
  TrainingSessionUpdate,
  TrainingSessionListItem,
  PaginatedTrainingSessionResponse,
  TrainingSessionFilters,
  
  // Participant
  TrainingParticipant,
  TrainingParticipantCreate,
  TrainingParticipantUpdate,
  PaginatedParticipantResponse,
  
  // Assessment
  TrainingAssessment,
  TrainingAssessmentCreate,
  
  // Certification
  TrainingCertification,
  TrainingCertificationCreate,
  
  // Skill Matrix
  Skill,
  SkillCreate,
  EmployeeSkill,
  EmployeeSkillCreate,
  
  // Dashboard
  TrainingDashboardStats,
  TrainingCalendarItem,
} from "@/types/training.types";

const BASE_URL = "/api/v1";

// ============================================================================
// TRAINING COURSE OPERATIONS
// ============================================================================

/**
 * Create new training course
 */
export const createTrainingCourse = async (
  data: TrainingCourseCreate
): Promise<TrainingCourse> => {
  const response = await apiClient.post<TrainingCourse>(
    `${BASE_URL}/hrms/training/courses`,
    data
  );
  return response.data;
};

/**
 * Get paginated list of training courses
 */
export const getTrainingCourses = async (
  page: number = 1,
  page_size: number = 20,
  filters?: TrainingCourseFilters
): Promise<PaginatedTrainingCourseResponse> => {
  const params = new URLSearchParams();
  params.append("page", page.toString());
  params.append("page_size", page_size.toString());
  
  if (filters) {
    if (filters.search) params.append("search", filters.search);
    if (filters.training_type) params.append("training_type", filters.training_type);
    if (filters.training_category) params.append("training_category", filters.training_category);
    if (filters.is_active !== undefined) params.append("is_active", filters.is_active.toString());
    if (filters.is_published !== undefined) params.append("is_published", filters.is_published.toString());
    if (filters.is_mandatory !== undefined) params.append("is_mandatory", filters.is_mandatory.toString());
  }
  
  const response = await apiClient.get<PaginatedTrainingCourseResponse>(
    `${BASE_URL}/hrms/training/courses?${params.toString()}`
  );
  return response.data;
};

/**
 * Get training course by ID
 */
export const getTrainingCourseById = async (
  courseId: string
): Promise<TrainingCourse> => {
  const response = await apiClient.get<TrainingCourse>(
    `${BASE_URL}/hrms/training/courses/${courseId}`
  );
  return response.data;
};

/**
 * Update training course
 */
export const updateTrainingCourse = async (
  courseId: string,
  data: TrainingCourseUpdate
): Promise<TrainingCourse> => {
  const response = await apiClient.put<TrainingCourse>(
    `${BASE_URL}/hrms/training/courses/${courseId}`,
    data
  );
  return response.data;
};

/**
 * Delete training course
 */
export const deleteTrainingCourse = async (courseId: string): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/hrms/training/courses/${courseId}`);
};

// ============================================================================
// TRAINING SESSION OPERATIONS
// ============================================================================

/**
 * Create new training session
 */
export const createTrainingSession = async (
  data: TrainingSessionCreate
): Promise<TrainingSession> => {
  const response = await apiClient.post<TrainingSession>(
    `${BASE_URL}/hrms/training/sessions`,
    data
  );
  return response.data;
};

/**
 * Get paginated list of training sessions
 */
export const getTrainingSessions = async (
  page: number = 1,
  page_size: number = 20,
  filters?: TrainingSessionFilters
): Promise<PaginatedTrainingSessionResponse> => {
  const params = new URLSearchParams();
  params.append("page", page.toString());
  params.append("page_size", page_size.toString());
  
  if (filters) {
    if (filters.course_id) params.append("course_id", filters.course_id);
    if (filters.status) params.append("status", filters.status);
    if (filters.start_date_from) params.append("start_date_from", filters.start_date_from);
    if (filters.start_date_to) params.append("start_date_to", filters.start_date_to);
  }
  
  const response = await apiClient.get<PaginatedTrainingSessionResponse>(
    `${BASE_URL}/hrms/training/sessions?${params.toString()}`
  );
  return response.data;
};

/**
 * Get training session by ID
 */
export const getTrainingSessionById = async (
  sessionId: string
): Promise<TrainingSession> => {
  const response = await apiClient.get<TrainingSession>(
    `${BASE_URL}/hrms/training/sessions/${sessionId}`
  );
  return response.data;
};

/**
 * Update training session
 */
export const updateTrainingSession = async (
  sessionId: string,
  data: TrainingSessionUpdate
): Promise<TrainingSession> => {
  const response = await apiClient.put<TrainingSession>(
    `${BASE_URL}/hrms/training/sessions/${sessionId}`,
    data
  );
  return response.data;
};

/**
 * Get training calendar for date range
 */
export const getTrainingCalendar = async (
  startDate: string,
  endDate: string
): Promise<TrainingCalendarItem[]> => {
  const params = new URLSearchParams();
  params.append("start_date", startDate);
  params.append("end_date", endDate);
  
  const response = await apiClient.get<TrainingCalendarItem[]>(
    `${BASE_URL}/hrms/training/calendar?${params.toString()}`
  );
  return response.data;
};

// ============================================================================
// PARTICIPANT OPERATIONS
// ============================================================================

/**
 * Create/nominate participant for training
 */
export const createTrainingParticipant = async (
  data: TrainingParticipantCreate
): Promise<TrainingParticipant> => {
  const response = await apiClient.post<TrainingParticipant>(
    `${BASE_URL}/hrms/training/participants`,
    data
  );
  return response.data;
};

/**
 * Get participants for a training session
 */
export const getSessionParticipants = async (
  sessionId: string,
  status?: string
): Promise<TrainingParticipant[]> => {
  const params = new URLSearchParams();
  if (status) params.append("status", status);
  
  const response = await apiClient.get<TrainingParticipant[]>(
    `${BASE_URL}/hrms/training/sessions/${sessionId}/participants?${params.toString()}`
  );
  return response.data;
};

/**
 * Update participant status
 */
export const updateTrainingParticipant = async (
  participantId: string,
  data: TrainingParticipantUpdate
): Promise<TrainingParticipant> => {
  const response = await apiClient.put<TrainingParticipant>(
    `${BASE_URL}/hrms/training/participants/${participantId}`,
    data
  );
  return response.data;
};

// ============================================================================
// CERTIFICATION OPERATIONS
// ============================================================================

/**
 * Issue training certificate
 */
export const issueTrainingCertificate = async (
  employeeId: string,
  courseId: string,
  sessionId?: string,
  validityMonths?: number
): Promise<TrainingCertification> => {
  const params = new URLSearchParams();
  params.append("employee_id", employeeId);
  params.append("course_id", courseId);
  if (sessionId) params.append("session_id", sessionId);
  if (validityMonths) params.append("validity_months", validityMonths.toString());
  
  const response = await apiClient.post<TrainingCertification>(
    `${BASE_URL}/hrms/training/certifications?${params.toString()}`
  );
  return response.data;
};

/**
 * Get employee certifications
 */
export const getEmployeeCertifications = async (
  employeeId: string
): Promise<TrainingCertification[]> => {
  const response = await apiClient.get<TrainingCertification[]>(
    `${BASE_URL}/hrms/training/employees/${employeeId}/certifications`
  );
  return response.data;
};

// ============================================================================
// SKILL MATRIX OPERATIONS
// ============================================================================

/**
 * Create new skill
 */
export const createSkill = async (data: SkillCreate): Promise<Skill> => {
  const response = await apiClient.post<Skill>(
    `${BASE_URL}/hrms/training/skills`,
    data
  );
  return response.data;
};

/**
 * Add skill to employee
 */
export const addEmployeeSkill = async (
  data: EmployeeSkillCreate
): Promise<EmployeeSkill> => {
  const response = await apiClient.post<EmployeeSkill>(
    `${BASE_URL}/hrms/training/employee-skills`,
    data
  );
  return response.data;
};

/**
 * Get employee skills
 */
export const getEmployeeSkills = async (
  employeeId: string
): Promise<EmployeeSkill[]> => {
  const response = await apiClient.get<EmployeeSkill[]>(
    `${BASE_URL}/hrms/training/employees/${employeeId}/skills`
  );
  return response.data;
};

// ============================================================================
// DASHBOARD & STATISTICS
// ============================================================================

/**
 * Get training dashboard statistics
 */
export const getTrainingStats = async (): Promise<TrainingDashboardStats> => {
  const response = await apiClient.get<TrainingDashboardStats>(
    `${BASE_URL}/hrms/training/stats`
  );
  return response.data;
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get active training courses (for dropdowns)
 */
export const getActiveTrainingCourses = async (): Promise<TrainingCourseListItem[]> => {
  const response = await getTrainingCourses(1, 1000, { is_active: true });
  return response.items;
};

/**
 * Get upcoming training sessions
 */
export const getUpcomingTrainingSessions = async (): Promise<TrainingSessionListItem[]> => {
  const today = new Date().toISOString().split('T')[0];
  const response = await getTrainingSessions(1, 100, {
    start_date_from: today,
    status: "scheduled" as any
  });
  return response.items;
};
