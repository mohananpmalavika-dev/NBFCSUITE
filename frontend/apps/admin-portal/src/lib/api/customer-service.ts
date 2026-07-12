/**
 * Customer Service API Client
 * Handles all API calls for ticket management, knowledge base, and SLA
 */

import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ==================== TICKET MANAGEMENT ====================

export const customerServiceApi = {
  // Tickets
  async createTicket(data: any) {
    const response = await apiClient.post("/api/v1/crm/customer-service/tickets", data);
    return response.data;
  },

  async getTicket(ticketId: string) {
    const response = await apiClient.get(`/api/v1/crm/customer-service/tickets/${ticketId}`);
    return response.data;
  },

  async getTicketByNumber(ticketNumber: string) {
    const response = await apiClient.get(`/api/v1/crm/customer-service/tickets/number/${ticketNumber}`);
    return response.data;
  },

  async listTickets(params?: any) {
    const response = await apiClient.get("/api/v1/crm/customer-service/tickets", { params });
    return response.data;
  },

  async updateTicket(ticketId: string, data: any) {
    const response = await apiClient.put(`/api/v1/crm/customer-service/tickets/${ticketId}`, data);
    return response.data;
  },

  async assignTicket(ticketId: string, data: any) {
    const response = await apiClient.post(`/api/v1/crm/customer-service/tickets/${ticketId}/assign`, data);
    return response.data;
  },

  async resolveTicket(ticketId: string, data: any) {
    const response = await apiClient.post(`/api/v1/crm/customer-service/tickets/${ticketId}/resolve`, data);
    return response.data;
  },

  async closeTicket(ticketId: string, data?: any) {
    const response = await apiClient.post(`/api/v1/crm/customer-service/tickets/${ticketId}/close`, data || {});
    return response.data;
  },

  async reopenTicket(ticketId: string, data: any) {
    const response = await apiClient.post(`/api/v1/crm/customer-service/tickets/${ticketId}/reopen`, data);
    return response.data;
  },

  async rateTicket(ticketId: string, data: any) {
    const response = await apiClient.post(`/api/v1/crm/customer-service/tickets/${ticketId}/rating`, data);
    return response.data;
  },

  // Comments
  async addComment(ticketId: string, data: any) {
    const response = await apiClient.post(`/api/v1/crm/customer-service/tickets/${ticketId}/comments`, data);
    return response.data;
  },

  async getComments(ticketId: string, includeInternal: boolean = true) {
    const response = await apiClient.get(`/api/v1/crm/customer-service/tickets/${ticketId}/comments`, {
      params: { include_internal: includeInternal }
    });
    return response.data;
  },

  // Statistics
  async getStatistics(fromDate?: string, toDate?: string) {
    const response = await apiClient.get("/api/v1/crm/customer-service/statistics", {
      params: { from_date: fromDate, to_date: toDate }
    });
    return response.data;
  },

  async getDashboard(fromDate?: string, toDate?: string) {
    const response = await apiClient.get("/api/v1/crm/customer-service/dashboard", {
      params: { from_date: fromDate, to_date: toDate }
    });
    return response.data;
  },

  // ==================== SLA MANAGEMENT ====================

  async createSLAPolicy(data: any) {
    const response = await apiClient.post("/api/v1/crm/customer-service/sla-policies", data);
    return response.data;
  },

  async getSLAPolicy(policyId: string) {
    const response = await apiClient.get(`/api/v1/crm/customer-service/sla-policies/${policyId}`);
    return response.data;
  },

  async listSLAPolicies(activeOnly: boolean = true) {
    const response = await apiClient.get("/api/v1/crm/customer-service/sla-policies", {
      params: { active_only: activeOnly }
    });
    return response.data;
  },

  async updateSLAPolicy(policyId: string, data: any) {
    const response = await apiClient.put(`/api/v1/crm/customer-service/sla-policies/${policyId}`, data);
    return response.data;
  },

  async getSLAMetrics(fromDate?: string) {
    const response = await apiClient.get("/api/v1/crm/customer-service/sla-metrics", {
      params: { from_date: fromDate }
    });
    return response.data;
  },

  // ==================== KNOWLEDGE BASE ====================

  async createArticle(data: any) {
    const response = await apiClient.post("/api/v1/crm/customer-service/knowledge-base", data);
    return response.data;
  },

  async getArticle(articleId: string) {
    const response = await apiClient.get(`/api/v1/crm/customer-service/knowledge-base/${articleId}`);
    return response.data;
  },

  async getArticleBySlug(slug: string) {
    const response = await apiClient.get(`/api/v1/crm/customer-service/knowledge-base/slug/${slug}`);
    return response.data;
  },

  async listKnowledgeBase(params?: any) {
    const response = await apiClient.get("/api/v1/crm/customer-service/knowledge-base", { params });
    return response.data;
  },

  async updateArticle(articleId: string, data: any) {
    const response = await apiClient.put(`/api/v1/crm/customer-service/knowledge-base/${articleId}`, data);
    return response.data;
  },

  async publishArticle(articleId: string) {
    const response = await apiClient.post(`/api/v1/crm/customer-service/knowledge-base/${articleId}/publish`);
    return response.data;
  },

  async searchKnowledgeBase(query: string, category?: string, publicOnly: boolean = false) {
    const response = await apiClient.get("/api/v1/crm/customer-service/knowledge-base/search", {
      params: { q: query, category, public_only: publicOnly }
    });
    return response.data;
  },

  async addArticleFeedback(articleId: string, data: any) {
    const response = await apiClient.post(`/api/v1/crm/customer-service/knowledge-base/${articleId}/feedback`, data);
    return response.data;
  },

  async deleteArticle(articleId: string) {
    const response = await apiClient.delete(`/api/v1/crm/customer-service/knowledge-base/${articleId}`);
    return response.data;
  },
};

export default customerServiceApi;
