/**
 * CRM Opportunity Management Service
 * API calls for opportunity tracking, sales pipeline, and analytics
 */

import { apiClient as api } from '@/lib/api-client';

export interface Opportunity {
  id: string;
  opportunity_number: string;
  opportunity_name: string;
  account_id: string;
  account_name?: string;
  primary_contact_id?: string;
  contact_name?: string;
  opportunity_type: string;
  stage: string;
  priority: string;
  estimated_value: number;
  weighted_value: number;
  probability: number;
  currency: string;
  expected_close_date?: string;
  actual_close_date?: string;
  lead_source?: string;
  opportunity_owner_id: string;
  owner_name?: string;
  sales_team?: string;
  description?: string;
  next_step?: string;
  internal_notes?: string;
  is_won: boolean;
  is_lost: boolean;
  close_reason?: string;
  loss_reason?: string;
  competitor_name?: string;
  stage_history?: Array<any>;
  products?: Array<OpportunityProduct>;
  activities?: Array<OpportunityActivity>;
  tags?: string[];
  custom_fields?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface OpportunityProduct {
  id?: string;
  product_code?: string;
  product_name: string;
  description?: string;
  quantity: number;
  unit_price: number;
  discount_percentage: number;
  discount_amount: number;
  tax_percentage: number;
  tax_amount: number;
  total_amount?: number;
  product_category?: string;
  line_notes?: string;
}

export interface OpportunityActivity {
  id?: string;
  activity_type: string;
  activity_subject: string;
  activity_description?: string;
  activity_date: string;
  duration_minutes?: number;
  status: string;
  participants?: string[];
  outcome?: string;
  next_action?: string;
}

export interface CreateOpportunityRequest {
  opportunity_name: string;
  account_id: string;
  primary_contact_id?: string;
  opportunity_type?: string;
  stage?: string;
  priority?: string;
  estimated_value?: number;
  currency?: string;
  probability?: number;
  expected_close_date?: string;
  lead_source?: string;
  campaign_id?: string;
  opportunity_owner_id: string;
  sales_team?: string;
  description?: string;
  next_step?: string;
  internal_notes?: string;
  tags?: string[];
  custom_fields?: Record<string, any>;
  products?: OpportunityProduct[];
}

export interface OpportunityFilters {
  search?: string;
  stage?: string;
  priority?: string;
  opportunity_owner_id?: string;
  account_id?: string;
  from_date?: string;
  to_date?: string;
  skip?: number;
  limit?: number;
}

export interface PipelineOverview {
  total_opportunities: number;
  total_value: number;
  weighted_pipeline_value: number;
  avg_deal_size: number;
  stages: PipelineStageStats[];
}

export interface PipelineStageStats {
  stage: string;
  stage_name: string;
  count: number;
  total_value: number;
  weighted_value: number;
  avg_probability: number;
}

export interface WinLossAnalysis {
  total_closed: number;
  won_count: number;
  lost_count: number;
  win_rate: number;
  total_won_value: number;
  total_lost_value: number;
  avg_won_deal_size: number;
  avg_lost_deal_size: number;
  loss_reasons: Record<string, number>;
  top_competitors: Array<{
    name: string;
    count: number;
    total_value: number;
  }>;
}

class OpportunityService {
  /**
   * Create a new opportunity
   */
  async createOpportunity(data: CreateOpportunityRequest): Promise<Opportunity> {
    const response = await api.post('/crm/opportunities', data);
    return response.data.data;
  }

  /**
   * Get list of opportunities with filters
   */
  async getOpportunities(filters?: OpportunityFilters): Promise<{
    items: Opportunity[];
    total: number;
    skip: number;
    limit: number;
    has_more: boolean;
  }> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, value.toString());
        }
      });
    }

    const response = await api.get(`/crm/opportunities?${params.toString()}`);
    return response.data.data;
  }

  /**
   * Get opportunity details by ID
   */
  async getOpportunityById(opportunityId: string): Promise<Opportunity> {
    const response = await api.get(`/crm/opportunities/${opportunityId}`);
    return response.data.data;
  }

  /**
   * Update opportunity
   */
  async updateOpportunity(opportunityId: string, data: Partial<CreateOpportunityRequest>): Promise<Opportunity> {
    const response = await api.put(`/crm/opportunities/${opportunityId}`, data);
    return response.data.data;
  }

  /**
   * Delete opportunity
   */
  async deleteOpportunity(opportunityId: string): Promise<void> {
    await api.delete(`/crm/opportunities/${opportunityId}`);
  }

  /**
   * Get pipeline overview
   */
  async getPipelineOverview(filters?: {
    owner_id?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<PipelineOverview> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }

    const response = await api.get(`/crm/opportunities/pipeline/overview?${params.toString()}`);
    return response.data.data;
  }

  /**
   * Get win/loss analysis
   */
  async getWinLossAnalysis(filters?: {
    owner_id?: string;
    from_date?: string;
    to_date?: string;
  }): Promise<WinLossAnalysis> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }

    const response = await api.get(`/crm/opportunities/analytics/win-loss?${params.toString()}`);
    return response.data.data;
  }

  /**
   * Add activity to opportunity
   */
  async addActivity(opportunityId: string, activity: Omit<OpportunityActivity, 'id'>): Promise<OpportunityActivity> {
    const response = await api.post(`/crm/opportunities/${opportunityId}/activities`, activity);
    return response.data.data;
  }

  /**
   * Add product to opportunity
   */
  async addProduct(opportunityId: string, product: Omit<OpportunityProduct, 'id' | 'total_amount'>): Promise<OpportunityProduct> {
    const response = await api.post(`/crm/opportunities/${opportunityId}/products`, product);
    return response.data.data;
  }

  /**
   * Update opportunity stage
   */
  async updateStage(opportunityId: string, newStage: string, reason?: string): Promise<Opportunity> {
    const response = await api.put(`/crm/opportunities/${opportunityId}/stage`, {
      new_stage: newStage,
      reason
    });
    return response.data.data;
  }

  /**
   * Mark opportunity as won
   */
  async markAsWon(opportunityId: string, data: {
    actual_close_date?: string;
    close_reason?: string;
    actual_value?: number;
  }): Promise<Opportunity> {
    const response = await api.post(`/crm/opportunities/${opportunityId}/close-won`, data);
    return response.data.data;
  }

  /**
   * Mark opportunity as lost
   */
  async markAsLost(opportunityId: string, data: {
    actual_close_date?: string;
    loss_reason: string;
    close_reason?: string;
    competitor_name?: string;
  }): Promise<Opportunity> {
    const response = await api.post(`/crm/opportunities/${opportunityId}/close-lost`, data);
    return response.data.data;
  }
}

export const opportunityService = new OpportunityService();
export default opportunityService;
