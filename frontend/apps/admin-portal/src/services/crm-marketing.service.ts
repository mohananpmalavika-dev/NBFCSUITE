/**
 * CRM Marketing Automation Service
 * API client for campaign management, segmentation, and landing pages
 */

import api from './api';

// ============================================================================
// TYPES
// ============================================================================

export interface MarketingCampaign {
  id: string;
  campaign_number: string;
  campaign_name: string;
  campaign_type: string;
  status: string;
  description?: string;
  objective?: string;
  target_segment_id?: string;
  target_audience_size: number;
  subject_line?: string;
  email_content?: string;
  sms_content?: string;
  sender_name?: string;
  sender_email?: string;
  landing_page_id?: string;
  start_date?: string;
  end_date?: string;
  scheduled_send_time?: string;
  budget?: number;
  budget_currency?: string;
  target_conversions?: number;
  campaign_owner_id?: string;
  total_sent: number;
  total_delivered: number;
  total_opened: number;
  total_clicked: number;
  total_converted: number;
  total_bounced: number;
  open_rate?: number;
  click_rate?: number;
  conversion_rate?: number;
  bounce_rate?: number;
  revenue_generated?: number;
  roi?: number;
  is_ab_test: boolean;
  tags?: string;
  category?: string;
  notes?: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
}

export interface MarketingCampaignCreate {
  campaign_name: string;
  campaign_type?: string;
  status?: string;
  description?: string;
  objective?: string;
  target_segment_id?: string;
  subject_line?: string;
  email_content?: string;
  sms_content?: string;
  sender_name?: string;
  sender_email?: string;
  reply_to_email?: string;
  landing_page_id?: string;
  start_date?: string;
  end_date?: string;
  scheduled_send_time?: string;
  budget?: number;
  budget_currency?: string;
  target_conversions?: number;
  campaign_owner_id?: string;
  is_ab_test?: boolean;
  tags?: string;
  category?: string;
  notes?: string;
}

export interface CustomerSegment {
  id: string;
  segment_number: string;
  segment_name: string;
  segmentation_type: string;
  description?: string;
  criteria_type?: string;
  rules?: any;
  total_customers: number;
  active_customers: number;
  segment_owner_id?: string;
  is_active: boolean;
  auto_refresh: boolean;
  last_refreshed_at?: string;
  tags?: string;
  notes?: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
}

export interface CustomerSegmentCreate {
  segment_name: string;
  segmentation_type?: string;
  description?: string;
  criteria_type?: string;
  rules?: any;
  segment_owner_id?: string;
  is_active?: boolean;
  auto_refresh?: boolean;
  tags?: string;
  notes?: string;
}

export interface LandingPage {
  id: string;
  page_number: string;
  page_name: string;
  page_title: string;
  status: string;
  slug: string;
  custom_domain?: string;
  full_url?: string;
  description?: string;
  html_content?: string;
  css_content?: string;
  meta_title?: string;
  meta_description?: string;
  has_form: boolean;
  form_fields?: any[];
  submit_button_text: string;
  thank_you_message?: string;
  redirect_url?: string;
  page_owner_id?: string;
  total_visits: number;
  unique_visits: number;
  total_submissions: number;
  conversion_rate?: number;
  published_at?: string;
  tags?: string;
  notes?: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
}

export interface LandingPageCreate {
  page_name: string;
  page_title: string;
  status?: string;
  slug: string;
  custom_domain?: string;
  description?: string;
  html_content?: string;
  css_content?: string;
  meta_title?: string;
  meta_description?: string;
  has_form?: boolean;
  form_fields?: any[];
  submit_button_text?: string;
  thank_you_message?: string;
  redirect_url?: string;
  page_owner_id?: string;
  tags?: string;
  notes?: string;
}

export interface MarketingStats {
  total_campaigns: number;
  active_campaigns: number;
  total_segments: number;
  total_landing_pages: number;
  by_status: Record<string, number>;
}

export interface CampaignFilters {
  skip?: number;
  limit?: number;
  search?: string;
  status?: string;
  campaign_type?: string;
  campaign_owner_id?: string;
}

export interface SegmentFilters {
  skip?: number;
  limit?: number;
  search?: string;
  segmentation_type?: string;
}

// ============================================================================
// API SERVICE
// ============================================================================

const BASE_URL = '/api/v1/crm/marketing';

export const crmMarketingService = {
  // ============================================================================
  // CAMPAIGN OPERATIONS
  // ============================================================================

  createCampaign: async (data: MarketingCampaignCreate) => {
    const response = await api.post(`${BASE_URL}/campaigns`, data);
    return response.data;
  },

  getCampaign: async (id: string) => {
    const response = await api.get(`${BASE_URL}/campaigns/${id}`);
    return response.data;
  },

  listCampaigns: async (filters: CampaignFilters = {}) => {
    const response = await api.get(`${BASE_URL}/campaigns`, { params: filters });
    return response.data;
  },

  updateCampaign: async (id: string, data: Partial<MarketingCampaignCreate>) => {
    const response = await api.put(`${BASE_URL}/campaigns/${id}`, data);
    return response.data;
  },

  deleteCampaign: async (id: string) => {
    const response = await api.delete(`${BASE_URL}/campaigns/${id}`);
    return response.data;
  },

  launchCampaign: async (id: string) => {
    const response = await api.post(`${BASE_URL}/campaigns/${id}/launch`);
    return response.data;
  },

  // ============================================================================
  // SEGMENT OPERATIONS
  // ============================================================================

  createSegment: async (data: CustomerSegmentCreate) => {
    const response = await api.post(`${BASE_URL}/segments`, data);
    return response.data;
  },

  getSegment: async (id: string) => {
    const response = await api.get(`${BASE_URL}/segments/${id}`);
    return response.data;
  },

  listSegments: async (filters: SegmentFilters = {}) => {
    const response = await api.get(`${BASE_URL}/segments`, { params: filters });
    return response.data;
  },

  // ============================================================================
  // LANDING PAGE OPERATIONS
  // ============================================================================

  createLandingPage: async (data: LandingPageCreate) => {
    const response = await api.post(`${BASE_URL}/landing-pages`, data);
    return response.data;
  },

  publishLandingPage: async (id: string) => {
    const response = await api.post(`${BASE_URL}/landing-pages/${id}/publish`);
    return response.data;
  },

  // ============================================================================
  // STATISTICS
  // ============================================================================

  getMarketingStats: async (): Promise<{ success: boolean; data: MarketingStats }> => {
    const response = await api.get(`${BASE_URL}/stats/summary`);
    return response.data;
  }
};

export default crmMarketingService;
