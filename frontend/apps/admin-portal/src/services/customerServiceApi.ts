/**
 * CRM Customer Service API Client
 * Ticket Management, Knowledge Base, SLA Tracking
 */

import { apiClient } from './apiClient'

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent' | 'critical'
export type TicketStatus = 'new' | 'open' | 'in_progress' | 'pending_customer' | 'pending_internal' | 'resolved' | 'closed' | 'cancelled'
export type TicketCategory = 'technical' | 'billing' | 'account' | 'product' | 'complaint' | 'feature_request' | 'general' | 'other'
export type TicketChannel = 'email' | 'phone' | 'web' | 'chat' | 'social_media' | 'walk_in'

export type ArticleStatus = 'draft' | 'published' | 'archived' | 'under_review'
export type ArticleCategory = 'faq' | 'how_to' | 'troubleshooting' | 'policy' | 'announcement' | 'guide'

export type SLAStatus = 'active' | 'inactive'

export interface TicketComment {
  id: string
  ticket_id: string
  comment_type: string
  content: string
  is_internal: boolean
  is_system: boolean
  created_at: string
  updated_at: string
  created_by?: string
}

export interface TicketAttachment {
  id: string
  ticket_id: string
  file_name: string
  file_path: string
  file_size?: number
  file_type?: string
  mime_type?: string
  created_at: string
}

export interface Ticket {
  id: string
  ticket_number: string
  subject: string
  description: string
  category: TicketCategory
  priority: TicketPriority
  status: TicketStatus
  channel: TicketChannel
  account_id?: string
  contact_name?: string
  contact_email?: string
  contact_phone?: string
  assigned_to?: string
  assigned_team?: string
  sla_id?: string
  first_response_due?: string
  resolution_due?: string
  first_response_at?: string
  resolved_at?: string
  closed_at?: string
  sla_breached: boolean
  parent_ticket_id?: string
  related_article_id?: string
  satisfaction_rating?: number
  satisfaction_comment?: string
  tags: string[]
  custom_fields?: string
  created_at: string
  updated_at: string
  created_by?: string
  comments?: TicketComment[]
  attachments?: TicketAttachment[]
  account_name?: string
  assigned_to_name?: string
}

export interface TicketCreate {
  subject: string
  description: string
  category: TicketCategory
  priority?: TicketPriority
  status?: TicketStatus
  channel?: TicketChannel
  account_id?: string
  contact_name?: string
  contact_email?: string
  contact_phone?: string
  assigned_to?: string
  assigned_team?: string
  sla_id?: string
  parent_ticket_id?: string
  related_article_id?: string
  tags?: string[]
  custom_fields?: string
}

export interface TicketUpdate {
  subject?: string
  description?: string
  category?: TicketCategory
  priority?: TicketPriority
  status?: TicketStatus
  channel?: TicketChannel
  account_id?: string
  contact_name?: string
  contact_email?: string
  contact_phone?: string
  assigned_to?: string
  assigned_team?: string
  sla_id?: string
  parent_ticket_id?: string
  related_article_id?: string
  tags?: string[]
  custom_fields?: string
  first_response_at?: string
  resolved_at?: string
  closed_at?: string
}

export interface TicketListParams {
  skip?: number
  limit?: number
  search?: string
  status?: TicketStatus
  priority?: TicketPriority
  category?: TicketCategory
  assigned_to?: string
  account_id?: string
  sla_breached?: boolean
  created_from?: string
  created_to?: string
}

export interface TicketListResponse {
  tickets: Ticket[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface TicketCommentCreate {
  ticket_id: string
  comment_type?: string
  content: string
  is_internal?: boolean
  is_system?: boolean
}


export interface ArticleAttachment {
  id: string
  article_id: string
  file_name: string
  file_path: string
  file_size?: number
  file_type?: string
  mime_type?: string
  display_order: number
  created_at: string
}

export interface KnowledgeArticle {
  id: string
  article_number: string
  title: string
  slug: string
  content: string
  excerpt?: string
  category: ArticleCategory
  status: ArticleStatus
  tags: string[]
  related_products: string[]
  meta_description?: string
  keywords: string[]
  author_id: string
  reviewer_id?: string
  published_at?: string
  view_count: number
  helpful_count: number
  not_helpful_count: number
  version: number
  is_featured: boolean
  display_order: number
  parent_article_id?: string
  created_at: string
  updated_at: string
  attachments?: ArticleAttachment[]
  author_name?: string
  reviewer_name?: string
}

export interface KnowledgeArticleCreate {
  title: string
  slug?: string
  content: string
  excerpt?: string
  category: ArticleCategory
  status?: ArticleStatus
  tags?: string[]
  related_products?: string[]
  meta_description?: string
  keywords?: string[]
  parent_article_id?: string
  is_featured?: boolean
  display_order?: number
}

export interface KnowledgeArticleUpdate {
  title?: string
  slug?: string
  content?: string
  excerpt?: string
  category?: ArticleCategory
  status?: ArticleStatus
  tags?: string[]
  related_products?: string[]
  meta_description?: string
  keywords?: string[]
  parent_article_id?: string
  is_featured?: boolean
  display_order?: number
  reviewer_id?: string
}

export interface KnowledgeArticleListParams {
  skip?: number
  limit?: number
  search?: string
  category?: ArticleCategory
  status?: ArticleStatus
  tags?: string[]
  is_featured?: boolean
  author_id?: string
}

export interface KnowledgeArticleListResponse {
  articles: KnowledgeArticle[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface SLA {
  id: string
  name: string
  description?: string
  status: SLAStatus
  priority?: TicketPriority
  category?: TicketCategory
  first_response_time: number
  resolution_time: number
  escalation_time?: number
  use_business_hours: boolean
  business_hours_start: string
  business_hours_end: string
  business_days: number[]
  escalation_enabled: boolean
  escalate_to?: string
  is_default: boolean
  display_order: number
  created_at: string
  updated_at: string
  created_by?: string
  escalate_to_name?: string
}

export interface SLACreate {
  name: string
  description?: string
  status?: SLAStatus
  priority?: TicketPriority
  category?: TicketCategory
  first_response_time: number
  resolution_time: number
  escalation_time?: number
  use_business_hours?: boolean
  business_hours_start?: string
  business_hours_end?: string
  business_days?: number[]
  escalation_enabled?: boolean
  escalate_to?: string
  is_default?: boolean
  display_order?: number
}

export interface SLAUpdate extends Partial<SLACreate> {}

export interface SLAListParams {
  skip?: number
  limit?: number
  status?: SLAStatus
  priority?: TicketPriority
  category?: TicketCategory
}

export interface SLAListResponse {
  slas: SLA[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface TicketStats {
  total_tickets: number
  new_tickets: number
  open_tickets: number
  in_progress_tickets: number
  pending_tickets: number
  resolved_tickets: number
  closed_tickets: number
  sla_breached_tickets: number
  avg_first_response_time?: number
  avg_resolution_time?: number
  avg_satisfaction_rating?: number
}

export interface ApiResponse<T> {
  success: boolean
  message?: string
  data?: T
  errors?: Record<string, any>
}


// ============================================================================
// API CLIENT
// ============================================================================

export const customerServiceApi = {
  // Ticket Management
  tickets: {
    async create(data: TicketCreate): Promise<ApiResponse<Ticket>> {
      return apiClient.post('/tickets', data)
    },

    async list(params?: TicketListParams): Promise<ApiResponse<TicketListResponse>> {
      return apiClient.get('/tickets', { params })
    },

    async get(id: string): Promise<ApiResponse<Ticket>> {
      return apiClient.get(`/tickets/${id}`)
    },

    async update(id: string, data: TicketUpdate): Promise<ApiResponse<Ticket>> {
      return apiClient.put(`/tickets/${id}`, data)
    },

    async delete(id: string): Promise<ApiResponse<void>> {
      return apiClient.delete(`/tickets/${id}`)
    },

    async addComment(id: string, data: TicketCommentCreate): Promise<ApiResponse<TicketComment>> {
      return apiClient.post(`/tickets/${id}/comments`, data)
    },

    async getStats(): Promise<ApiResponse<TicketStats>> {
      return apiClient.get('/tickets/stats/overview')
    },
  },

  // Knowledge Base
  knowledge: {
    async create(data: KnowledgeArticleCreate): Promise<ApiResponse<KnowledgeArticle>> {
      return apiClient.post('/knowledge/articles', data)
    },

    async list(params?: KnowledgeArticleListParams): Promise<ApiResponse<KnowledgeArticleListResponse>> {
      return apiClient.get('/knowledge/articles', { params })
    },

    async get(id: string, incrementView: boolean = false): Promise<ApiResponse<KnowledgeArticle>> {
      return apiClient.get(`/knowledge/articles/${id}`, {
        params: { increment_view: incrementView }
      })
    },

    async getBySlug(slug: string): Promise<ApiResponse<KnowledgeArticle>> {
      return apiClient.get(`/knowledge/articles/slug/${slug}`)
    },

    async update(id: string, data: KnowledgeArticleUpdate): Promise<ApiResponse<KnowledgeArticle>> {
      return apiClient.put(`/knowledge/articles/${id}`, data)
    },

    async delete(id: string): Promise<ApiResponse<void>> {
      return apiClient.delete(`/knowledge/articles/${id}`)
    },

    async recordFeedback(id: string, helpful: boolean): Promise<ApiResponse<void>> {
      return apiClient.post(`/knowledge/articles/${id}/feedback`, { helpful })
    },
  },

  // SLA Management
  slas: {
    async create(data: SLACreate): Promise<ApiResponse<SLA>> {
      return apiClient.post('/slas', data)
    },

    async list(params?: SLAListParams): Promise<ApiResponse<SLAListResponse>> {
      return apiClient.get('/slas', { params })
    },

    async get(id: string): Promise<ApiResponse<SLA>> {
      return apiClient.get(`/slas/${id}`)
    },

    async update(id: string, data: SLAUpdate): Promise<ApiResponse<SLA>> {
      return apiClient.put(`/slas/${id}`, data)
    },

    async delete(id: string): Promise<ApiResponse<void>> {
      return apiClient.delete(`/slas/${id}`)
    },

    async getViolations(ticketId?: string): Promise<ApiResponse<any[]>> {
      return apiClient.get('/slas/violations/list', {
        params: { ticket_id: ticketId }
      })
    },
  },
}

export default customerServiceApi
