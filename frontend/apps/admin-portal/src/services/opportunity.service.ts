/**
 * CRM Opportunity Management Service
 * API client for opportunity management operations
 */

import api from './api';
import {
  Opportunity,
  OpportunityCreate,
  OpportunityUpdate,
  OpportunityFilters,
  PaginatedOpportunityResponse,
  StageTransitionRequest,
  StageHistory,
  OpportunityWinRequest,
  OpportunityLossRequest,
  OpportunityActivity,
  OpportunityActivityCreate,
  PaginatedActivityResponse,
  OpportunityProduct,
  OpportunityProductCreate,
  OpportunityCompetitor,
  OpportunityCompetitorCreate,
  OpportunityNote,
  OpportunityNoteCreate,
  OpportunityDashboardStats,
  PipelineAnalytics,
  WinLossAnalysis,
  ForecastData
} from '../types/crm.types';

const BASE_URL = '/api/crm/opportunities';

export const opportunityService = {
  // ============================================================================
  // OPPORTUNITY CRUD
  // ============================================================================

  /**
   * Create new opportunity
   */
  createOpportunity: async (data: OpportunityCreate): Promise<Opportunity> => {
    const response = await api.post<Opportunity>(BASE_URL, data);
    return response.data;
  },

  /**
   * Get opportunity by ID
   */
  getOpportunity: async (id: number): Promise<Opportunity> => {
    const response = await api.get<Opportunity>(`${BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Update opportunity
   */
  updateOpportunity: async (id: number, data: OpportunityUpdate): Promise<Opportunity> => {
    const response = await api.put<Opportunity>(`${BASE_URL}/${id}`, data);
    return response.data;
  },

  /**
   * List opportunities with filters
   */
  listOpportunities: async (filters: OpportunityFilters): Promise<PaginatedOpportunityResponse> => {
    const response = await api.get<PaginatedOpportunityResponse>(BASE_URL, {
      params: filters
    });
    return response.data;
  },

  // ============================================================================
  // PIPELINE STAGE MANAGEMENT
  // ============================================================================

  /**
   * Move opportunity to new stage
   */
  transitionStage: async (id: number, data: StageTransitionRequest): Promise<Opportunity> => {
    const response = await api.post<Opportunity>(`${BASE_URL}/${id}/transition`, data);
    return response.data;
  },

  /**
   * Get stage transition history
   */
  getStageHistory: async (id: number): Promise<StageHistory[]> => {
    const response = await api.get<StageHistory[]>(`${BASE_URL}/${id}/stage-history`);
    return response.data;
  },

  // ============================================================================
  // WIN/LOSS MANAGEMENT
  // ============================================================================

  /**
   * Mark opportunity as won
   */
  markWon: async (id: number, data: OpportunityWinRequest): Promise<Opportunity> => {
    const response = await api.post<Opportunity>(`${BASE_URL}/${id}/mark-won`, data);
    return response.data;
  },

  /**
   * Mark opportunity as lost
   */
  markLost: async (id: number, data: OpportunityLossRequest): Promise<Opportunity> => {
    const response = await api.post<Opportunity>(`${BASE_URL}/${id}/mark-lost`, data);
    return response.data;
  },

  // ============================================================================
  // ACTIVITY MANAGEMENT
  // ============================================================================

  /**
   * Create opportunity activity
   */
  createActivity: async (data: OpportunityActivityCreate): Promise<OpportunityActivity> => {
    const response = await api.post<OpportunityActivity>(`${BASE_URL}/activities`, data);
    return response.data;
  },

  /**
   * Get opportunity activities
   */
  getActivities: async (
    opportunityId: number,
    page = 1,
    pageSize = 50
  ): Promise<PaginatedActivityResponse> => {
    const response = await api.get<PaginatedActivityResponse>(
      `${BASE_URL}/${opportunityId}/activities`,
      {
        params: { page, page_size: pageSize }
      }
    );
    return response.data;
  },

  // ============================================================================
  // PRODUCT MANAGEMENT
  // ============================================================================

  /**
   * Add product to opportunity
   */
  addProduct: async (data: OpportunityProductCreate): Promise<OpportunityProduct> => {
    const response = await api.post<OpportunityProduct>(`${BASE_URL}/products`, data);
    return response.data;
  },

  /**
   * Get opportunity products
   */
  getProducts: async (opportunityId: number): Promise<OpportunityProduct[]> => {
    const response = await api.get<OpportunityProduct[]>(
      `${BASE_URL}/${opportunityId}/products`
    );
    return response.data;
  },

  // ============================================================================
  // COMPETITOR MANAGEMENT
  // ============================================================================

  /**
   * Add competitor to opportunity
   */
  addCompetitor: async (data: OpportunityCompetitorCreate): Promise<OpportunityCompetitor> => {
    const response = await api.post<OpportunityCompetitor>(`${BASE_URL}/competitors`, data);
    return response.data;
  },

  /**
   * Get opportunity competitors
   */
  getCompetitors: async (opportunityId: number): Promise<OpportunityCompetitor[]> => {
    const response = await api.get<OpportunityCompetitor[]>(
      `${BASE_URL}/${opportunityId}/competitors`
    );
    return response.data;
  },

  // ============================================================================
  // DASHBOARD & ANALYTICS
  // ============================================================================

  /**
   * Get dashboard statistics
   */
  getDashboardStats: async (ownerUserId?: number): Promise<OpportunityDashboardStats> => {
    const response = await api.get<OpportunityDashboardStats>(`${BASE_URL}/dashboard/stats`, {
      params: ownerUserId ? { owner_user_id: ownerUserId } : {}
    });
    return response.data;
  },

  /**
   * Get pipeline analytics by stage
   */
  getPipelineAnalytics: async (ownerUserId?: number): Promise<PipelineAnalytics[]> => {
    const response = await api.get<PipelineAnalytics[]>(`${BASE_URL}/analytics/pipeline`, {
      params: ownerUserId ? { owner_user_id: ownerUserId } : {}
    });
    return response.data;
  },

  /**
   * Get win/loss analysis
   */
  getWinLossAnalysis: async (
    period: string,
    ownerUserId?: number
  ): Promise<WinLossAnalysis> => {
    const response = await api.get<WinLossAnalysis>(`${BASE_URL}/analytics/win-loss`, {
      params: {
        period,
        ...(ownerUserId ? { owner_user_id: ownerUserId } : {})
      }
    });
    return response.data;
  },

  // ============================================================================
  // BULK OPERATIONS
  // ============================================================================

  /**
   * Bulk update opportunities
   */
  bulkUpdate: async (data: {
    opportunity_ids: number[];
    owner_user_id?: number;
    priority?: string;
    stage?: string;
    tags?: string[];
  }): Promise<any> => {
    const response = await api.post(`${BASE_URL}/bulk/update`, data);
    return response.data;
  },

  /**
   * Bulk delete opportunities
   */
  bulkDelete: async (opportunityIds: number[], reason?: string): Promise<any> => {
    const response = await api.delete(`${BASE_URL}/bulk/delete`, {
      data: {
        opportunity_ids: opportunityIds,
        reason
      }
    });
    return response.data;
  }
};

export default opportunityService;
