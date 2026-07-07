/**
 * Collection Management API Client
 * API functions for all collection endpoints
 */

import { apiClient } from "./client";
import type {
  CollectionStrategy,
  CommunicationTemplate,
  CollectionAction,
  Territory,
  FieldAgent,
  FieldVisit,
  VisitTarget,
  AgentDashboard,
  PaymentPromise,
  PromiseAnalytics,
  LegalNotice,
  LegalCase,
  RecoveryAgency,
  RecoveryAction,
  WaiverPolicy,
  SettlementProposal,
  SettlementAgreement,
  ListResponse
} from "@/types/collection";

const BASE_URL = "/api/v1/collection";

// ============================================================================
// COLLECTION STRATEGY APIs
// ============================================================================

export const collectionStrategyApi = {
  // List strategies
  list: async (params?: { is_active?: boolean; skip?: number; limit?: number }) => {
    const response = await apiClient.get<ListResponse<CollectionStrategy>>(
      `${BASE_URL}/strategies`,
      { params }
    );
    return response.data;
  },

  // Get strategy by ID
  get: async (id: number) => {
    const response = await apiClient.get<CollectionStrategy>(
      `${BASE_URL}/strategies/${id}`
    );
    return response.data;
  },

  // Create strategy
  create: async (data: Partial<CollectionStrategy>) => {
    const response = await apiClient.post<CollectionStrategy>(
      `${BASE_URL}/strategies`,
      data
    );
    return response.data;
  },

  // Update strategy
  update: async (id: number, data: Partial<CollectionStrategy>) => {
    const response = await apiClient.put<CollectionStrategy>(
      `${BASE_URL}/strategies/${id}`,
      data
    );
    return response.data;
  },

  // Delete strategy
  delete: async (id: number) => {
    const response = await apiClient.delete(`${BASE_URL}/strategies/${id}`);
    return response.data;
  },

  // Execute strategies
  execute: async (loan_account_id?: number, force_execution?: boolean) => {
    const response = await apiClient.post(`${BASE_URL}/strategies/execute`, {
      loan_account_id,
      force_execution
    });
    return response.data;
  },

  // Get pending actions
  getPendingActions: async (action_type?: string, skip?: number, limit?: number) => {
    const response = await apiClient.get<ListResponse<CollectionAction>>(
      `${BASE_URL}/actions/pending`,
      { params: { action_type, skip, limit } }
    );
    return response.data;
  },

  // Update action status
  updateActionStatus: async (id: number, data: {
    status: string;
    response_details?: string;
    next_action_date?: string;
  }) => {
    const response = await apiClient.put(
      `${BASE_URL}/actions/${id}/status`,
      data
    );
    return response.data;
  }
};

// ============================================================================
// TEMPLATE APIs
// ============================================================================

export const templateApi = {
  // List templates
  list: async (params?: { template_type?: string; category?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<ListResponse<CommunicationTemplate>>(
      `${BASE_URL}/templates`,
      { params }
    );
    return response.data;
  },

  // Get template by ID
  get: async (id: number) => {
    const response = await apiClient.get<CommunicationTemplate>(
      `${BASE_URL}/templates/${id}`
    );
    return response.data;
  },

  // Create template
  create: async (data: Partial<CommunicationTemplate>) => {
    const response = await apiClient.post<CommunicationTemplate>(
      `${BASE_URL}/templates`,
      data
    );
    return response.data;
  },

  // Update template
  update: async (id: number, data: Partial<CommunicationTemplate>) => {
    const response = await apiClient.put<CommunicationTemplate>(
      `${BASE_URL}/templates/${id}`,
      data
    );
    return response.data;
  }
};

// ============================================================================
// FIELD AGENT APIs
// ============================================================================

export const fieldAgentApi = {
  // List agents
  listAgents: async (params?: { territory_id?: number; is_active?: boolean; skip?: number; limit?: number }) => {
    const response = await apiClient.get<ListResponse<FieldAgent>>(
      `${BASE_URL}/field-agents`,
      { params }
    );
    return response.data;
  },

  // Get agent by ID
  getAgent: async (id: number) => {
    const response = await apiClient.get<FieldAgent>(
      `${BASE_URL}/field-agents/${id}`
    );
    return response.data;
  },

  // Create agent
  createAgent: async (data: Partial<FieldAgent>) => {
    const response = await apiClient.post<FieldAgent>(
      `${BASE_URL}/field-agents`,
      data
    );
    return response.data;
  },

  // Update agent
  updateAgent: async (id: number, data: Partial<FieldAgent>) => {
    const response = await apiClient.put<FieldAgent>(
      `${BASE_URL}/field-agents/${id}`,
      data
    );
    return response.data;
  },

  // Get agent dashboard
  getDashboard: async (agent_id: number) => {
    const response = await apiClient.get<AgentDashboard>(
      `${BASE_URL}/field-agents/${agent_id}/dashboard`
    );
    return response.data;
  },

  // List territories
  listTerritories: async (skip?: number, limit?: number) => {
    const response = await apiClient.get<ListResponse<Territory>>(
      `${BASE_URL}/territories`,
      { params: { skip, limit } }
    );
    return response.data;
  },

  // Create territory
  createTerritory: async (data: Partial<Territory>) => {
    const response = await apiClient.post<Territory>(
      `${BASE_URL}/territories`,
      data
    );
    return response.data;
  }
};

// ============================================================================
// VISIT APIs
// ============================================================================

export const visitApi = {
  // List visits
  list: async (params?: { agent_id?: number; visit_date?: string; status?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<ListResponse<FieldVisit>>(
      `${BASE_URL}/visits`,
      { params }
    );
    return response.data;
  },

  // Get visit by ID
  get: async (id: number) => {
    const response = await apiClient.get<FieldVisit>(
      `${BASE_URL}/visits/${id}`
    );
    return response.data;
  },

  // Create visit
  create: async (data: Partial<FieldVisit>) => {
    const response = await apiClient.post<FieldVisit>(
      `${BASE_URL}/visits`,
      data
    );
    return response.data;
  },

  // Update visit
  update: async (id: number, data: Partial<FieldVisit>) => {
    const response = await apiClient.put<FieldVisit>(
      `${BASE_URL}/visits/${id}`,
      data
    );
    return response.data;
  },

  // Record payment from visit
  recordPayment: async (visit_id: number, data: {
    amount: number;
    payment_mode: string;
    promise_amount?: number;
    promise_date?: string;
  }) => {
    const response = await apiClient.post(
      `${BASE_URL}/visits/${visit_id}/payment`,
      data
    );
    return response.data;
  },

  // Allocate visits to agent
  allocateVisits: async (agent_id: number, visit_date: string, max_visits?: number) => {
    const response = await apiClient.post(
      `${BASE_URL}/visits/allocate`,
      { agent_id, visit_date, max_visits }
    );
    return response.data;
  }
};

// ============================================================================
// PAYMENT PROMISE APIs
// ============================================================================

export const promiseApi = {
  // List promises
  list: async (params?: { loan_account_id?: number; status?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<ListResponse<PaymentPromise>>(
      `${BASE_URL}/promises`,
      { params }
    );
    return response.data;
  },

  // Get promise by ID
  get: async (id: number) => {
    const response = await apiClient.get<PaymentPromise>(
      `${BASE_URL}/promises/${id}`
    );
    return response.data;
  },

  // Create promise
  create: async (data: Partial<PaymentPromise>) => {
    const response = await apiClient.post<PaymentPromise>(
      `${BASE_URL}/promises`,
      data
    );
    return response.data;
  },

  // Update promise status
  updateStatus: async (id: number, data: {
    new_status: string;
    actual_payment_amount?: number;
    actual_payment_date?: string;
    broken_reason?: string;
    remarks?: string;
  }) => {
    const response = await apiClient.put(
      `${BASE_URL}/promises/${id}/status`,
      data
    );
    return response.data;
  },

  // Reschedule promise
  reschedule: async (id: number, data: {
    new_promise_date: string;
    new_promise_amount?: number;
    remarks?: string;
  }) => {
    const response = await apiClient.post(
      `${BASE_URL}/promises/${id}/reschedule`,
      data
    );
    return response.data;
  },

  // Get promise analytics
  getAnalytics: async (from_date?: string, to_date?: string) => {
    const response = await apiClient.get<PromiseAnalytics>(
      `${BASE_URL}/promises/analytics`,
      { params: { from_date, to_date } }
    );
    return response.data;
  },

  // Check promise fulfillment
  checkFulfillment: async () => {
    const response = await apiClient.post(
      `${BASE_URL}/promises/check-fulfillment`
    );
    return response.data;
  }
};

// ============================================================================
// LEGAL & RECOVERY APIs
// ============================================================================

export const legalApi = {
  // List notices
  listNotices: async (params?: { loan_account_id?: number; notice_type?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<ListResponse<LegalNotice>>(
      `${BASE_URL}/legal/notices`,
      { params }
    );
    return response.data;
  },

  // Create notice
  createNotice: async (data: Partial<LegalNotice>) => {
    const response = await apiClient.post<LegalNotice>(
      `${BASE_URL}/legal/notices`,
      data
    );
    return response.data;
  },

  // Update notice delivery
  updateNoticeDelivery: async (id: number, data: {
    delivery_status: string;
    delivery_date?: string;
    delivered_to?: string;
  }) => {
    const response = await apiClient.put(
      `${BASE_URL}/legal/notices/${id}/delivery`,
      data
    );
    return response.data;
  },

  // List cases
  listCases: async (params?: { case_status?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<ListResponse<LegalCase>>(
      `${BASE_URL}/legal/cases`,
      { params }
    );
    return response.data;
  },

  // Get case by ID
  getCase: async (id: number) => {
    const response = await apiClient.get<LegalCase>(
      `${BASE_URL}/legal/cases/${id}`
    );
    return response.data;
  },

  // File case
  fileCase: async (data: Partial<LegalCase>) => {
    const response = await apiClient.post<LegalCase>(
      `${BASE_URL}/legal/cases`,
      data
    );
    return response.data;
  },

  // Update case status
  updateCaseStatus: async (id: number, data: {
    case_status: string;
    next_hearing_date?: string;
    remarks?: string;
  }) => {
    const response = await apiClient.put(
      `${BASE_URL}/legal/cases/${id}/status`,
      data
    );
    return response.data;
  },

  // List recovery agencies
  listAgencies: async (skip?: number, limit?: number) => {
    const response = await apiClient.get<ListResponse<RecoveryAgency>>(
      `${BASE_URL}/legal/agencies`,
      { params: { skip, limit } }
    );
    return response.data;
  },

  // Create agency
  createAgency: async (data: Partial<RecoveryAgency>) => {
    const response = await apiClient.post<RecoveryAgency>(
      `${BASE_URL}/legal/agencies`,
      data
    );
    return response.data;
  },

  // Assign to agency
  assignToAgency: async (data: {
    agency_id: number;
    loan_account_id: number;
    customer_id: number;
    outstanding_amount: number;
  }) => {
    const response = await apiClient.post(
      `${BASE_URL}/legal/agencies/assign`,
      data
    );
    return response.data;
  }
};

// ============================================================================
// SETTLEMENT/OTS APIs
// ============================================================================

export const settlementApi = {
  // List waiver policies
  listPolicies: async (skip?: number, limit?: number) => {
    const response = await apiClient.get<ListResponse<WaiverPolicy>>(
      `${BASE_URL}/settlement/policies`,
      { params: { skip, limit } }
    );
    return response.data;
  },

  // Create waiver policy
  createPolicy: async (data: Partial<WaiverPolicy>) => {
    const response = await apiClient.post<WaiverPolicy>(
      `${BASE_URL}/settlement/policies`,
      data
    );
    return response.data;
  },

  // List proposals
  listProposals: async (params?: { proposal_status?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<ListResponse<SettlementProposal>>(
      `${BASE_URL}/settlement/proposals`,
      { params }
    );
    return response.data;
  },

  // Get proposal by ID
  getProposal: async (id: number) => {
    const response = await apiClient.get<SettlementProposal>(
      `${BASE_URL}/settlement/proposals/${id}`
    );
    return response.data;
  },

  // Create proposal
  createProposal: async (data: Partial<SettlementProposal>) => {
    const response = await apiClient.post<SettlementProposal>(
      `${BASE_URL}/settlement/proposals`,
      data
    );
    return response.data;
  },

  // Calculate NPV
  calculateNPV: async (proposal_id: number, discount_rate?: number) => {
    const response = await apiClient.get(
      `${BASE_URL}/settlement/proposals/${proposal_id}/npv`,
      { params: { discount_rate } }
    );
    return response.data;
  },

  // Submit for approval
  submitForApproval: async (proposal_id: number, approver_user_id: number, approval_level?: number) => {
    const response = await apiClient.post(
      `${BASE_URL}/settlement/proposals/${proposal_id}/submit`,
      { approver_user_id, approval_level }
    );
    return response.data;
  },

  // Approve settlement
  approve: async (approval_id: number, remarks?: string, forward_to_next_level?: boolean, next_approver_user_id?: number) => {
    const response = await apiClient.post(
      `${BASE_URL}/settlement/approvals/${approval_id}/approve`,
      { remarks, forward_to_next_level, next_approver_user_id }
    );
    return response.data;
  },

  // Reject settlement
  reject: async (approval_id: number, remarks: string) => {
    const response = await apiClient.post(
      `${BASE_URL}/settlement/approvals/${approval_id}/reject`,
      { remarks }
    );
    return response.data;
  },

  // Create agreement
  createAgreement: async (data: {
    proposal_id: number;
    payment_deadline: string;
    terms_and_conditions: string;
    breach_clause?: string;
    breach_penalty?: number;
  }) => {
    const response = await apiClient.post<SettlementAgreement>(
      `${BASE_URL}/settlement/agreements`,
      data
    );
    return response.data;
  },

  // Record payment
  recordPayment: async (agreement_id: number, data: {
    installment_number: number;
    paid_amount: number;
    payment_date?: string;
    transaction_id?: number;
  }) => {
    const response = await apiClient.post(
      `${BASE_URL}/settlement/agreements/${agreement_id}/payment`,
      data
    );
    return response.data;
  },

  // Get settlement statistics
  getStatistics: async (from_date?: string, to_date?: string) => {
    const response = await apiClient.get(
      `${BASE_URL}/settlement/statistics`,
      { params: { from_date, to_date } }
    );
    return response.data;
  }
};
