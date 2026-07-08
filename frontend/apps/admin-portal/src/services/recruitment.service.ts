/**
 * Recruitment & Onboarding API Service
 * Handles all API calls for recruitment module
 */

import axios from 'axios';
import {
  JobRequisition,
  JobRequisitionCreate,
  JobPosting,
  JobPostingCreate,
  JobApplication,
  JobApplicationCreate,
  Interview,
  InterviewCreate,
  Onboarding,
  OnboardingCreate,
  BackgroundVerification,
  BackgroundVerificationCreate,
  PaginatedResponse,
  RequisitionDashboardStats,
  PostingStatistics,
  KanbanColumn,
  ApplicationStatus,
  InterviewRecommendation,
  VerificationResult
} from '../types/recruitment.types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ============================================================================
// JOB REQUISITION API
// ============================================================================

export const requisitionApi = {
  // Get dashboard statistics
  async getDashboardStats(): Promise<RequisitionDashboardStats> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/requisitions/dashboard/stats`);
    return response.data;
  },

  // List requisitions with filters
  async list(params: {
    page?: number;
    page_size?: number;
    search?: string;
    status?: string;
    department_id?: string;
    priority?: string;
  }): Promise<PaginatedResponse<JobRequisition>> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/requisitions`, { params });
    return response.data;
  },

  // Get single requisition
  async get(id: string): Promise<JobRequisition> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/requisitions/${id}`);
    return response.data;
  },

  // Create requisition
  async create(data: JobRequisitionCreate): Promise<JobRequisition> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/requisitions`, data);
    return response.data;
  },

  // Update requisition
  async update(id: string, data: Partial<JobRequisitionCreate>): Promise<JobRequisition> {
    const response = await axios.put(`${API_BASE_URL}/recruitment/requisitions/${id}`, data);
    return response.data;
  },

  // Submit for approval
  async submit(id: string): Promise<JobRequisition> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/requisitions/${id}/submit`);
    return response.data;
  },

  // Approve/Reject requisition
  async approve(id: string, approved: boolean, rejection_reason?: string): Promise<JobRequisition> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/requisitions/${id}/approve`, {
      approved,
      rejection_reason
    });
    return response.data;
  },

  // Close requisition
  async close(id: string): Promise<JobRequisition> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/requisitions/${id}/close`);
    return response.data;
  },

  // Delete requisition
  async delete(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/recruitment/requisitions/${id}`);
  }
};

// ============================================================================
// JOB POSTING API
// ============================================================================

export const postingApi = {
  // List postings with filters
  async list(params: {
    page?: number;
    page_size?: number;
    search?: string;
    status?: string;
    is_featured?: boolean;
    include_expired?: boolean;
  }): Promise<PaginatedResponse<JobPosting>> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/postings`, { params });
    return response.data;
  },

  // Get public postings (for career page)
  async listPublic(params: {
    page?: number;
    page_size?: number;
    search?: string;
    employment_type?: string;
    location?: string;
  }): Promise<PaginatedResponse<JobPosting>> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/postings/public`, { params });
    return response.data;
  },

  // Get single posting
  async get(id: string): Promise<JobPosting> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/postings/${id}`);
    return response.data;
  },

  // Get posting statistics
  async getStatistics(id: string): Promise<PostingStatistics> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/postings/${id}/statistics`);
    return response.data;
  },

  // Create posting
  async create(data: JobPostingCreate): Promise<JobPosting> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/postings`, data);
    return response.data;
  },

  // Update posting
  async update(id: string, data: Partial<JobPostingCreate>): Promise<JobPosting> {
    const response = await axios.put(`${API_BASE_URL}/recruitment/postings/${id}`, data);
    return response.data;
  },

  // Publish posting
  async publish(id: string): Promise<JobPosting> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/postings/${id}/publish`);
    return response.data;
  },

  // Unpublish posting
  async unpublish(id: string): Promise<JobPosting> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/postings/${id}/unpublish`);
    return response.data;
  },

  // Close posting
  async close(id: string): Promise<JobPosting> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/postings/${id}/close`);
    return response.data;
  },

  // Increment view count
  async incrementViews(id: string): Promise<JobPosting> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/postings/${id}/view`);
    return response.data;
  },

  // Delete posting
  async delete(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/recruitment/postings/${id}`);
  }
};

// ============================================================================
// JOB APPLICATION API (Applicant Tracking System)
// ============================================================================

export const applicationApi = {
  // List applications with filters
  async list(params: {
    page?: number;
    page_size?: number;
    search?: string;
    posting_id?: string;
    status?: string;
    source?: string;
  }): Promise<PaginatedResponse<JobApplication>> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/applications`, { params });
    return response.data;
  },

  // Get applications in kanban format
  async getKanban(posting_id?: string): Promise<KanbanColumn[]> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/applications/kanban`, {
      params: { posting_id }
    });
    return response.data;
  },

  // Get single application
  async get(id: string): Promise<JobApplication> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/applications/${id}`);
    return response.data;
  },

  // Create application
  async create(data: JobApplicationCreate): Promise<JobApplication> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/applications`, data);
    return response.data;
  },

  // Update application
  async update(id: string, data: Partial<JobApplicationCreate>): Promise<JobApplication> {
    const response = await axios.put(`${API_BASE_URL}/recruitment/applications/${id}`, data);
    return response.data;
  },

  // Change application status
  async changeStatus(id: string, status: ApplicationStatus, notes?: string): Promise<JobApplication> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/applications/${id}/status`, {
      status,
      notes
    });
    return response.data;
  },

  // Shortlist application
  async shortlist(id: string): Promise<JobApplication> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/applications/${id}/shortlist`);
    return response.data;
  },

  // Reject application
  async reject(id: string, rejection_reason: string): Promise<JobApplication> {
    const response = await axios.post(
      `${API_BASE_URL}/recruitment/applications/${id}/reject?rejection_reason=${encodeURIComponent(rejection_reason)}`
    );
    return response.data;
  },

  // Bulk actions
  async bulkAction(action: string, application_ids: string[], new_status?: ApplicationStatus, notes?: string): Promise<void> {
    await axios.post(`${API_BASE_URL}/recruitment/applications/bulk-action`, {
      action,
      application_ids,
      new_status,
      notes
    });
  },

  // Upload resume
  async uploadResume(id: string, file: File): Promise<{ file_url: string; filename: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(`${API_BASE_URL}/recruitment/applications/${id}/resume/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // Delete application
  async delete(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/recruitment/applications/${id}`);
  }
};

// ============================================================================
// INTERVIEW API
// ============================================================================

export const interviewApi = {
  // List interviews with filters
  async list(params: {
    page?: number;
    page_size?: number;
    application_id?: string;
    interviewer_id?: string;
    status?: string;
    interview_type?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<PaginatedResponse<Interview>> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/interviews`, { params });
    return response.data;
  },

  // Get interviews for calendar view
  async getCalendar(from_date: string, to_date: string, interviewer_id?: string): Promise<Interview[]> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/interviews/calendar`, {
      params: { from_date, to_date, interviewer_id }
    });
    return response.data;
  },

  // Get single interview
  async get(id: string): Promise<Interview> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/interviews/${id}`);
    return response.data;
  },

  // Schedule interview
  async create(data: InterviewCreate): Promise<Interview> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/interviews`, data);
    return response.data;
  },

  // Update interview
  async update(id: string, data: Partial<InterviewCreate>): Promise<Interview> {
    const response = await axios.put(`${API_BASE_URL}/recruitment/interviews/${id}`, data);
    return response.data;
  },

  // Reschedule interview
  async reschedule(
    id: string,
    new_scheduled_date: string,
    new_start_time: string,
    new_end_time: string,
    reschedule_reason?: string
  ): Promise<Interview> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/interviews/${id}/reschedule`, {
      new_scheduled_date,
      new_start_time,
      new_end_time,
      reschedule_reason
    });
    return response.data;
  },

  // Complete interview
  async complete(id: string): Promise<Interview> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/interviews/${id}/complete`);
    return response.data;
  },

  // Cancel interview
  async cancel(id: string, cancellation_reason: string): Promise<Interview> {
    const response = await axios.post(
      `${API_BASE_URL}/recruitment/interviews/${id}/cancel?cancellation_reason=${encodeURIComponent(cancellation_reason)}`
    );
    return response.data;
  },

  // Submit feedback
  async submitFeedback(
    id: string,
    rating: number,
    feedback_notes: string,
    recommendation: InterviewRecommendation
  ): Promise<Interview> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/interviews/${id}/feedback`, {
      rating,
      feedback_notes,
      recommendation
    });
    return response.data;
  },

  // Delete interview
  async delete(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/recruitment/interviews/${id}`);
  }
};

// ============================================================================
// ONBOARDING API
// ============================================================================

export const onboardingApi = {
  // List onboarding records with filters
  async list(params: {
    page?: number;
    page_size?: number;
    search?: string;
    status?: string;
  }): Promise<PaginatedResponse<Onboarding>> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/onboarding`, { params });
    return response.data;
  },

  // Get single onboarding
  async get(id: string): Promise<Onboarding> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/onboarding/${id}`);
    return response.data;
  },

  // Create onboarding
  async create(data: OnboardingCreate): Promise<Onboarding> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/onboarding`, data);
    return response.data;
  },

  // Update onboarding
  async update(id: string, data: Partial<OnboardingCreate>): Promise<Onboarding> {
    const response = await axios.put(`${API_BASE_URL}/recruitment/onboarding/${id}`, data);
    return response.data;
  },

  // Start onboarding
  async start(id: string): Promise<Onboarding> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/onboarding/${id}/start`);
    return response.data;
  },

  // Complete onboarding
  async complete(id: string): Promise<Onboarding> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/onboarding/${id}/complete`);
    return response.data;
  },

  // Update checklist item
  async updateChecklistItem(id: string, item_key: string, completed: boolean): Promise<Onboarding> {
    const response = await axios.put(`${API_BASE_URL}/recruitment/onboarding/${id}/checklist-item`, {
      item_key,
      completed
    });
    return response.data;
  },

  // Delete onboarding
  async delete(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/recruitment/onboarding/${id}`);
  }
};

// ============================================================================
// BACKGROUND VERIFICATION API
// ============================================================================

export const verificationApi = {
  // List verifications with filters
  async list(params: {
    page?: number;
    page_size?: number;
    onboarding_id?: string;
    status?: string;
  }): Promise<PaginatedResponse<BackgroundVerification>> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/onboarding/verifications`, { params });
    return response.data;
  },

  // Get single verification
  async get(id: string): Promise<BackgroundVerification> {
    const response = await axios.get(`${API_BASE_URL}/recruitment/onboarding/verifications/${id}`);
    return response.data;
  },

  // Create verification
  async create(data: BackgroundVerificationCreate): Promise<BackgroundVerification> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/onboarding/verifications`, data);
    return response.data;
  },

  // Update verification
  async update(id: string, data: Partial<BackgroundVerificationCreate>): Promise<BackgroundVerification> {
    const response = await axios.put(`${API_BASE_URL}/recruitment/onboarding/verifications/${id}`, data);
    return response.data;
  },

  // Start verification
  async start(id: string): Promise<BackgroundVerification> {
    const response = await axios.post(`${API_BASE_URL}/recruitment/onboarding/verifications/${id}/start`);
    return response.data;
  },

  // Complete verification
  async complete(id: string, verified: boolean, verification_notes?: string): Promise<BackgroundVerification> {
    const response = await axios.post(
      `${API_BASE_URL}/recruitment/onboarding/verifications/${id}/complete?verified=${verified}` +
      (verification_notes ? `&verification_notes=${encodeURIComponent(verification_notes)}` : '')
    );
    return response.data;
  },

  // Delete verification
  async delete(id: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/recruitment/onboarding/verifications/${id}`);
  }
};

// Export all APIs
export default {
  requisition: requisitionApi,
  posting: postingApi,
  application: applicationApi,
  interview: interviewApi,
  onboarding: onboardingApi,
  verification: verificationApi
};
