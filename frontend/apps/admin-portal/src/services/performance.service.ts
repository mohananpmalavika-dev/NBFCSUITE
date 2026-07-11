/**
 * Performance Management API Service
 * Frontend API client for Goal Setting, Appraisals, 360 Feedback, Ratings & IDP
 */

import apiClient from './api-client';
import {
  AppraisalCycle,
  AppraisalCycleCreate,
  AppraisalCycleUpdate,
  AppraisalCycleFilters,
  PerformanceGoal,
  PerformanceGoalCreate,
  PerformanceGoalUpdate,
  PerformanceGoalFilters,
  EmployeeAppraisal,
  EmployeeAppraisalCreate,
  EmployeeAppraisalFilters,
  SelfAssessmentSubmit,
  ManagerReviewSubmit,
  HRReviewSubmit,
  FeedbackRequest,
  FeedbackRequestCreate,
  FeedbackRequestFilters,
  FeedbackResponse,
  FeedbackResponseSubmit,
  PerformanceIncrement,
  PerformanceIncrementCreate,
  PerformanceIncrementUpdate,
  IncrementFilters,
  IndividualDevelopmentPlan,
  IndividualDevelopmentPlanCreate,
  IndividualDevelopmentPlanUpdate,
  IDPFilters,
  DevelopmentActivity,
  DevelopmentActivityCreate,
  DevelopmentActivityUpdate,
  PaginatedResponse,
  MessageResponse
} from '../types/performance.types';

const BASE_URL = '/performance';

// ============================================================================
// APPRAISAL CYCLE API
// ============================================================================

export const appraisalCycleService = {
  /**
   * Create a new appraisal cycle
   */
  create: async (data: AppraisalCycleCreate): Promise<AppraisalCycle> => {
    const response = await apiClient.post<AppraisalCycle>(`${BASE_URL}/cycles`, data);
    return response.data;
  },

  /**
   * Get all appraisal cycles with filters
   */
  list: async (filters?: AppraisalCycleFilters): Promise<PaginatedResponse<AppraisalCycle>> => {
    const response = await apiClient.get<PaginatedResponse<AppraisalCycle>>(`${BASE_URL}/cycles`, {
      params: filters
    });
    return response.data;
  },


  /**
   * Get appraisal cycle by ID
   */
  getById: async (cycleId: string): Promise<AppraisalCycle> => {
    const response = await apiClient.get<AppraisalCycle>(`${BASE_URL}/cycles/${cycleId}`);
    return response.data;
  },

  /**
   * Update appraisal cycle
   */
  update: async (cycleId: string, data: AppraisalCycleUpdate): Promise<AppraisalCycle> => {
    const response = await apiClient.patch<AppraisalCycle>(`${BASE_URL}/cycles/${cycleId}`, data);
    return response.data;
  },

  /**
   * Delete appraisal cycle
   */
  delete: async (cycleId: string): Promise<MessageResponse> => {
    const response = await apiClient.delete<MessageResponse>(`${BASE_URL}/cycles/${cycleId}`);
    return response.data;
  }
};

// ============================================================================
// PERFORMANCE GOAL API (KRA/KPI)
// ============================================================================

export const performanceGoalService = {
  /**
   * Create a new performance goal
   */
  create: async (data: PerformanceGoalCreate): Promise<PerformanceGoal> => {
    const response = await apiClient.post<PerformanceGoal>(`${BASE_URL}/goals`, data);
    return response.data;
  },

  /**
   * Get performance goal by ID
   */
  getById: async (goalId: string): Promise<PerformanceGoal> => {
    const response = await apiClient.get<PerformanceGoal>(`${BASE_URL}/goals/${goalId}`);
    return response.data;
  },

  /**
   * List goals for an employee
   */
  listByEmployee: async (employeeId: string, filters?: PerformanceGoalFilters): Promise<PerformanceGoal[]> => {
    const response = await apiClient.get<PerformanceGoal[]>(`${BASE_URL}/employees/${employeeId}/goals`, {
      params: filters
    });
    return response.data;
  },

  /**
   * Update performance goal
   */
  update: async (goalId: string, data: PerformanceGoalUpdate): Promise<PerformanceGoal> => {
    const response = await apiClient.patch<PerformanceGoal>(`${BASE_URL}/goals/${goalId}`, data);
    return response.data;
  },

  /**
   * Submit all goals for approval
   */
  submit: async (employeeId: string, appraisalCycleId: string): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>(
      `${BASE_URL}/employees/${employeeId}/goals/submit`,
      null,
      { params: { appraisal_cycle_id: appraisalCycleId } }
    );
    return response.data;
  },

  /**
   * Approve a goal
   */
  approve: async (goalId: string, comments?: string): Promise<PerformanceGoal> => {
    const response = await apiClient.post<PerformanceGoal>(
      `${BASE_URL}/goals/${goalId}/approve`,
      null,
      { params: { comments } }
    );
    return response.data;
  },

  /**
   * Reject a goal
   */
  reject: async (goalId: string, reason: string): Promise<PerformanceGoal> => {
    const response = await apiClient.post<PerformanceGoal>(
      `${BASE_URL}/goals/${goalId}/reject`,
      null,
      { params: { reason } }
    );
    return response.data;
  }
};


// ============================================================================
// EMPLOYEE APPRAISAL API
// ============================================================================

export const employeeAppraisalService = {
  /**
   * Create a new employee appraisal
   */
  create: async (data: EmployeeAppraisalCreate): Promise<EmployeeAppraisal> => {
    const response = await apiClient.post<EmployeeAppraisal>(`${BASE_URL}/appraisals`, data);
    return response.data;
  },

  /**
   * List employee appraisals with filters
   */
  list: async (filters?: EmployeeAppraisalFilters): Promise<PaginatedResponse<EmployeeAppraisal>> => {
    const response = await apiClient.get<PaginatedResponse<EmployeeAppraisal>>(`${BASE_URL}/appraisals`, {
      params: filters
    });
    return response.data;
  },

  /**
   * Get employee appraisal by ID
   */
  getById: async (appraisalId: string): Promise<EmployeeAppraisal> => {
    const response = await apiClient.get<EmployeeAppraisal>(`${BASE_URL}/appraisals/${appraisalId}`);
    return response.data;
  },

  /**
   * Submit self assessment
   */
  submitSelfAssessment: async (appraisalId: string, data: SelfAssessmentSubmit): Promise<EmployeeAppraisal> => {
    const response = await apiClient.post<EmployeeAppraisal>(
      `${BASE_URL}/appraisals/${appraisalId}/self-assessment`,
      data
    );
    return response.data;
  },

  /**
   * Submit manager review
   */
  submitManagerReview: async (appraisalId: string, data: ManagerReviewSubmit): Promise<EmployeeAppraisal> => {
    const response = await apiClient.post<EmployeeAppraisal>(
      `${BASE_URL}/appraisals/${appraisalId}/manager-review`,
      data
    );
    return response.data;
  },

  /**
   * Submit HR review and finalize appraisal
   */
  submitHRReview: async (appraisalId: string, data: HRReviewSubmit): Promise<EmployeeAppraisal> => {
    const response = await apiClient.post<EmployeeAppraisal>(
      `${BASE_URL}/appraisals/${appraisalId}/hr-review`,
      data
    );
    return response.data;
  }
};

// ============================================================================
// 360 FEEDBACK API
// ============================================================================

export const feedbackService = {
  /**
   * Create a new feedback request
   */
  createRequest: async (data: FeedbackRequestCreate): Promise<FeedbackRequest> => {
    const response = await apiClient.post<FeedbackRequest>(`${BASE_URL}/feedback/requests`, data);
    return response.data;
  },

  /**
   * List feedback requests for a reviewer
   */
  listRequestsForReviewer: async (reviewerId: string, filters?: FeedbackRequestFilters): Promise<FeedbackRequest[]> => {
    const response = await apiClient.get<FeedbackRequest[]>(
      `${BASE_URL}/feedback/requests/reviewer/${reviewerId}`,
      { params: filters }
    );
    return response.data;
  },

  /**
   * Submit feedback response
   */
  submitResponse: async (requestId: string, data: FeedbackResponseSubmit): Promise<FeedbackResponse> => {
    const response = await apiClient.post<FeedbackResponse>(
      `${BASE_URL}/feedback/requests/${requestId}/respond`,
      data
    );
    return response.data;
  },

  /**
   * List feedback responses for an employee
   */
  listFeedbackForEmployee: async (employeeId: string, appraisalCycleId?: string): Promise<FeedbackResponse[]> => {
    const response = await apiClient.get<FeedbackResponse[]>(
      `${BASE_URL}/feedback/employee/${employeeId}`,
      { params: { appraisal_cycle_id: appraisalCycleId } }
    );
    return response.data;
  }
};


// ============================================================================
// PERFORMANCE INCREMENT API
// ============================================================================

export const performanceIncrementService = {
  /**
   * Create a new performance increment
   */
  create: async (data: PerformanceIncrementCreate): Promise<PerformanceIncrement> => {
    const response = await apiClient.post<PerformanceIncrement>(`${BASE_URL}/increments`, data);
    return response.data;
  },

  /**
   * List increments for an employee
   */
  listByEmployee: async (employeeId: string, filters?: IncrementFilters): Promise<PerformanceIncrement[]> => {
    const response = await apiClient.get<PerformanceIncrement[]>(
      `${BASE_URL}/employees/${employeeId}/increments`,
      { params: filters }
    );
    return response.data;
  },

  /**
   * Approve performance increment
   */
  approve: async (incrementId: string): Promise<PerformanceIncrement> => {
    const response = await apiClient.post<PerformanceIncrement>(
      `${BASE_URL}/increments/${incrementId}/approve`
    );
    return response.data;
  },

  /**
   * Mark increment as processed
   */
  process: async (incrementId: string): Promise<PerformanceIncrement> => {
    const response = await apiClient.post<PerformanceIncrement>(
      `${BASE_URL}/increments/${incrementId}/process`
    );
    return response.data;
  }
};

// ============================================================================
// INDIVIDUAL DEVELOPMENT PLAN (IDP) API
// ============================================================================

export const idpService = {
  /**
   * Create a new Individual Development Plan
   */
  create: async (data: IndividualDevelopmentPlanCreate): Promise<IndividualDevelopmentPlan> => {
    const response = await apiClient.post<IndividualDevelopmentPlan>(`${BASE_URL}/idp`, data);
    return response.data;
  },

  /**
   * Get IDP by ID
   */
  getById: async (idpId: string): Promise<IndividualDevelopmentPlan> => {
    const response = await apiClient.get<IndividualDevelopmentPlan>(`${BASE_URL}/idp/${idpId}`);
    return response.data;
  },

  /**
   * List IDPs for an employee
   */
  listByEmployee: async (employeeId: string, filters?: IDPFilters): Promise<IndividualDevelopmentPlan[]> => {
    const response = await apiClient.get<IndividualDevelopmentPlan[]>(
      `${BASE_URL}/employees/${employeeId}/idp`,
      { params: filters }
    );
    return response.data;
  },

  /**
   * Update IDP
   */
  update: async (idpId: string, data: IndividualDevelopmentPlanUpdate): Promise<IndividualDevelopmentPlan> => {
    const response = await apiClient.patch<IndividualDevelopmentPlan>(`${BASE_URL}/idp/${idpId}`, data);
    return response.data;
  },

  /**
   * Submit IDP for approval
   */
  submit: async (idpId: string): Promise<IndividualDevelopmentPlan> => {
    const response = await apiClient.post<IndividualDevelopmentPlan>(`${BASE_URL}/idp/${idpId}/submit`);
    return response.data;
  },

  /**
   * Approve IDP
   */
  approve: async (idpId: string): Promise<IndividualDevelopmentPlan> => {
    const response = await apiClient.post<IndividualDevelopmentPlan>(`${BASE_URL}/idp/${idpId}/approve`);
    return response.data;
  }
};

// ============================================================================
// DEVELOPMENT ACTIVITY API
// ============================================================================

export const developmentActivityService = {
  /**
   * Create a new development activity
   */
  create: async (data: DevelopmentActivityCreate): Promise<DevelopmentActivity> => {
    const response = await apiClient.post<DevelopmentActivity>(`${BASE_URL}/idp/activities`, data);
    return response.data;
  },

  /**
   * List activities for an IDP
   */
  listByIDP: async (idpId: string): Promise<DevelopmentActivity[]> => {
    const response = await apiClient.get<DevelopmentActivity[]>(`${BASE_URL}/idp/${idpId}/activities`);
    return response.data;
  },

  /**
   * Get development activity by ID
   */
  getById: async (activityId: string): Promise<DevelopmentActivity> => {
    const response = await apiClient.get<DevelopmentActivity>(`${BASE_URL}/idp/activities/${activityId}`);
    return response.data;
  },

  /**
   * Update development activity
   */
  update: async (activityId: string, data: DevelopmentActivityUpdate): Promise<DevelopmentActivity> => {
    const response = await apiClient.patch<DevelopmentActivity>(
      `${BASE_URL}/idp/activities/${activityId}`,
      data
    );
    return response.data;
  }
};

// ============================================================================
// COMBINED EXPORT
// ============================================================================

export const performanceManagementService = {
  cycles: appraisalCycleService,
  goals: performanceGoalService,
  appraisals: employeeAppraisalService,
  feedback: feedbackService,
  increments: performanceIncrementService,
  idp: idpService,
  activities: developmentActivityService
};

export default performanceManagementService;
