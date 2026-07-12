/**
 * CRM Lead Management Service
 * API client for lead management operations
 */

import { apiClient as api } from '@/lib/api-client';
import {
  Lead,
  LeadCreate,
  LeadUpdate,
  LeadFollowUp,
  LeadFollowUpCreate,
  LeadFollowUpComplete,
  LeadActivity,
  LeadDashboardStats,
  LeadFilters,
  PaginatedLeadResponse,
  LeadAssignRequest,
  LeadQualifyRequest,
  LeadConvertRequest,
  LeadLostRequest
} from '../types/crm.types';

const BASE_URL = '/api/crm/leads';

export const crmService = {
  // ============================================================================
  // LEAD CRUD
  // ============================================================================

  /**
   * Create new lead
   */
  createLead: async (data: LeadCreate): Promise<Lead> => {
    const response = await api.post<Lead>(BASE_URL, data);
    return response.data;
  },

  /**
   * Get lead by ID
   */
  getLead: async (id: number): Promise<Lead> => {
    const response = await api.get<Lead>(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Update lead
   */
  updateLead: async (id: number, data: LeadUpdate): Promise<Lead> => {
    const response = await api.put<Lead>(`${BASE_URL}/${id}`, data);
    return response.data;
  },

  /**
   * List leads with filters
   */
  listLeads: async (filters: LeadFilters): Promise<PaginatedLeadResponse> => {
    const response = await api.get<PaginatedLeadResponse>(BASE_URL, {
      params: filters
    });
    return response.data;
  },


  // ============================================================================
  // LEAD ACTIONS
  // ============================================================================

  /**
   * Assign lead to user
   */
  assignLead: async (id: number, data: LeadAssignRequest): Promise<Lead> => {
    const response = await api.post<Lead>(`${BASE_URL}/${id}/assign`, data);
    return response.data;
  },

  /**
   * Qualify or disqualify lead
   */
  qualifyLead: async (id: number, data: LeadQualifyRequest): Promise<Lead> => {
    const response = await api.post<Lead>(`${BASE_URL}/${id}/qualify`, data);
    return response.data;
  },

  /**
   * Convert lead to customer
   */
  convertLead: async (id: number, data: LeadConvertRequest): Promise<any> => {
    const response = await api.post(`${BASE_URL}/${id}/convert`, data);
    return response.data;
  },

  /**
   * Mark lead as lost
   */
  markLeadLost: async (id: number, data: LeadLostRequest): Promise<Lead> => {
    const response = await api.post<Lead>(`${BASE_URL}/${id}/mark-lost`, data);
    return response.data;
  },

  /**
   * Recalculate lead score
   */
  recalculateScore: async (id: number): Promise<Lead> => {
    const response = await api.post<Lead>(`${BASE_URL}/${id}/recalculate-score`);
    return response.data;
  },

  // ============================================================================
  // BULK OPERATIONS
  // ============================================================================

  /**
   * Bulk assign leads
   */
  bulkAssignLeads: async (leadIds: number[], userId: number, notes?: string): Promise<any> => {
    const response = await api.post(`${BASE_URL}/bulk/assign`, {
      lead_ids: leadIds,
      user_id: userId,
      notes
    });
    return response.data;
  },

  // ============================================================================
  // FOLLOW-UPS
  // ============================================================================

  /**
   * Create follow-up
   */
  createFollowUp: async (data: LeadFollowUpCreate): Promise<LeadFollowUp> => {
    const response = await api.post<LeadFollowUp>(`${BASE_URL}/follow-ups`, data);
    return response.data;
  },

  /**
   * Complete follow-up
   */
  completeFollowUp: async (id: number, data: LeadFollowUpComplete): Promise<LeadFollowUp> => {
    const response = await api.post<LeadFollowUp>(`${BASE_URL}/follow-ups/${id}/complete`, data);
    return response.data;
  },

  /**
   * Get lead follow-ups
   */
  getLeadFollowUps: async (leadId: number, page = 1, pageSize = 20): Promise<any> => {
    const response = await api.get(`${BASE_URL}/${leadId}/follow-ups`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  },

  /**
   * Get overdue follow-ups
   */
  getOverdueFollowUps: async (userId?: number): Promise<LeadFollowUp[]> => {
    const response = await api.get<LeadFollowUp[]>(`${BASE_URL}/follow-ups/overdue`, {
      params: userId ? { user_id: userId } : {}
    });
    return response.data;
  },

  // ============================================================================
  // ACTIVITIES
  // ============================================================================

  /**
   * Get lead activities
   */
  getLeadActivities: async (leadId: number, page = 1, pageSize = 50): Promise<any> => {
    const response = await api.get(`${BASE_URL}/${leadId}/activities`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  },

  // ============================================================================
  // DASHBOARD
  // ============================================================================

  /**
   * Get dashboard statistics
   */
  getDashboardStats: async (userId?: number): Promise<LeadDashboardStats> => {
    const response = await api.get<LeadDashboardStats>(`${BASE_URL}/dashboard/stats`, {
      params: userId ? { user_id: userId } : {}
    });
    return response.data;
  }
};

export default crmService;
