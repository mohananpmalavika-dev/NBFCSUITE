/**
 * Exit Management API Service
 * Frontend API client for Resignation, Clearance, Settlement & Exit Documents
 */

import { apiClient } from '@/lib/api-client';
import {
  // Resignation types
  Resignation,
  ResignationCreate,
  ResignationUpdate,
  ManagerReview,
  HRReview,
  ResignationApproval,
  ResignationRejection,
  ResignationWithdrawal,
  ExitInterview,
  Handover,
  ResignationFilters,
  
  // Clearance types
  ExitClearance,
  ClearanceCreate,
  ClearanceUpdate,
  ClearanceComplete,
  ClearanceFilters,
  
  // Settlement types
  ExitSettlement,
  SettlementCreate,
  SettlementCalculation,
  SettlementApproval,
  SettlementPayment,
  SettlementHold,
  SettlementFilters,
  
  // Settlement Component types
  SettlementComponent,
  SettlementComponentCreate,
  SettlementComponentUpdate,
  
  // Document types
  ExitDocument,
  DocumentCreate,
  DocumentGenerate,
  DocumentApproval,
  DocumentIssuance,
  DocumentFilters,
  
  // Common types
  PaginatedResponse,
  MessageResponse,
  ExitDashboardStats,
  BulkClearanceCreate,
  BulkDocumentGenerate
} from '../types/exit.types';

const BASE_URL = '/api/v1/hrms/exit';

// ============================================================================
// RESIGNATION API
// ============================================================================

export const resignationService = {
  /**
   * Create a new resignation
   */
  create: async (data: ResignationCreate): Promise<Resignation> => {
    const response = await apiClient.post<Resignation>(`${BASE_URL}/resignations`, data);
    return response.data;
  },

  /**
   * Get all resignations with filters
   */
  list: async (filters?: ResignationFilters): Promise<PaginatedResponse<Resignation>> => {
    const response = await apiClient.get<PaginatedResponse<Resignation>>(`${BASE_URL}/resignations`, {
      params: filters
    });
    return response.data;
  },

  /**
   * Get resignation by ID
   */
  getById: async (resignationId: string): Promise<Resignation> => {
    const response = await apiClient.get<Resignation>(`${BASE_URL}/resignations/${resignationId}`);
    return response.data;
  },

  /**
   * Update resignation
   */
  update: async (resignationId: string, data: ResignationUpdate): Promise<Resignation> => {
    const response = await apiClient.put<Resignation>(`${BASE_URL}/resignations/${resignationId}`, data);
    return response.data;
  },

  /**
   * Submit manager review for resignation
   */
  managerReview: async (resignationId: string, data: ManagerReview): Promise<Resignation> => {
    const response = await apiClient.post<Resignation>(
      `${BASE_URL}/resignations/${resignationId}/manager-review`,
      data
    );
    return response.data;
  },

  /**
   * Submit HR review for resignation
   */
  hrReview: async (resignationId: string, data: HRReview): Promise<Resignation> => {
    const response = await apiClient.post<Resignation>(
      `${BASE_URL}/resignations/${resignationId}/hr-review`,
      data
    );
    return response.data;
  },

  /**
   * Approve resignation
   */
  approve: async (resignationId: string, data: ResignationApproval): Promise<Resignation> => {
    const response = await apiClient.post<Resignation>(
      `${BASE_URL}/resignations/${resignationId}/approve`,
      data
    );
    return response.data;
  },

  /**
   * Reject resignation
   */
  reject: async (resignationId: string, data: ResignationRejection): Promise<Resignation> => {
    const response = await apiClient.post<Resignation>(
      `${BASE_URL}/resignations/${resignationId}/reject`,
      data
    );
    return response.data;
  },

  /**
   * Withdraw resignation
   */
  withdraw: async (resignationId: string, data: ResignationWithdrawal): Promise<Resignation> => {
    const response = await apiClient.post<Resignation>(
      `${BASE_URL}/resignations/${resignationId}/withdraw`,
      data
    );
    return response.data;
  },

  /**
   * Conduct exit interview
   */
  conductExitInterview: async (resignationId: string, data: ExitInterview): Promise<Resignation> => {
    const response = await apiClient.post<Resignation>(
      `${BASE_URL}/resignations/${resignationId}/exit-interview`,
      data
    );
    return response.data;
  },

  /**
   * Complete handover
   */
  completeHandover: async (resignationId: string, data: Handover): Promise<Resignation> => {
    const response = await apiClient.post<Resignation>(
      `${BASE_URL}/resignations/${resignationId}/handover`,
      data
    );
    return response.data;
  },

  /**
   * Complete exit process
   */
  completeExit: async (resignationId: string): Promise<Resignation> => {
    const response = await apiClient.post<Resignation>(
      `${BASE_URL}/resignations/${resignationId}/complete`
    );
    return response.data;
  }
};

// ============================================================================
// CLEARANCE API
// ============================================================================

export const clearanceService = {
  /**
   * Create a new clearance
   */
  create: async (data: ClearanceCreate): Promise<ExitClearance> => {
    const response = await apiClient.post<ExitClearance>(`${BASE_URL}/clearances`, data);
    return response.data;
  },

  /**
   * Get all clearances with filters
   */
  list: async (filters?: ClearanceFilters): Promise<PaginatedResponse<ExitClearance>> => {
    const response = await apiClient.get<PaginatedResponse<ExitClearance>>(`${BASE_URL}/clearances`, {
      params: filters
    });
    return response.data;
  },

  /**
   * Get clearance by ID
   */
  getById: async (clearanceId: string): Promise<ExitClearance> => {
    const response = await apiClient.get<ExitClearance>(`${BASE_URL}/clearances/${clearanceId}`);
    return response.data;
  },

  /**
   * Update clearance
   */
  update: async (clearanceId: string, data: ClearanceUpdate): Promise<ExitClearance> => {
    const response = await apiClient.put<ExitClearance>(`${BASE_URL}/clearances/${clearanceId}`, data);
    return response.data;
  },

  /**
   * Complete clearance
   */
  complete: async (clearanceId: string, data: ClearanceComplete): Promise<ExitClearance> => {
    const response = await apiClient.post<ExitClearance>(
      `${BASE_URL}/clearances/${clearanceId}/complete`,
      data
    );
    return response.data;
  },

  /**
   * Create bulk clearances for resignation
   */
  createBulk: async (data: BulkClearanceCreate): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>(`${BASE_URL}/clearances/bulk`, data);
    return response.data;
  }
};

// ============================================================================
// SETTLEMENT API
// ============================================================================

export const settlementService = {
  /**
   * Create a new settlement
   */
  create: async (data: SettlementCreate): Promise<ExitSettlement> => {
    const response = await apiClient.post<ExitSettlement>(`${BASE_URL}/settlements`, data);
    return response.data;
  },

  /**
   * Get all settlements with filters
   */
  list: async (filters?: SettlementFilters): Promise<PaginatedResponse<ExitSettlement>> => {
    const response = await apiClient.get<PaginatedResponse<ExitSettlement>>(`${BASE_URL}/settlements`, {
      params: filters
    });
    return response.data;
  },

  /**
   * Get settlement by ID
   */
  getById: async (settlementId: string): Promise<ExitSettlement> => {
    const response = await apiClient.get<ExitSettlement>(`${BASE_URL}/settlements/${settlementId}`);
    return response.data;
  },

  /**
   * Get settlement by resignation ID
   */
  getByResignationId: async (resignationId: string): Promise<ExitSettlement> => {
    const response = await apiClient.get<ExitSettlement>(`${BASE_URL}/settlements/resignation/${resignationId}`);
    return response.data;
  },

  /**
   * Calculate settlement
   */
  calculate: async (settlementId: string, data: SettlementCalculation): Promise<ExitSettlement> => {
    const response = await apiClient.post<ExitSettlement>(
      `${BASE_URL}/settlements/${settlementId}/calculate`,
      data
    );
    return response.data;
  },

  /**
   * Approve settlement
   */
  approve: async (settlementId: string, data: SettlementApproval): Promise<ExitSettlement> => {
    const response = await apiClient.post<ExitSettlement>(
      `${BASE_URL}/settlements/${settlementId}/approve`,
      data
    );
    return response.data;
  },

  /**
   * Process settlement payment
   */
  processPayment: async (settlementId: string, data: SettlementPayment): Promise<ExitSettlement> => {
    const response = await apiClient.post<ExitSettlement>(
      `${BASE_URL}/settlements/${settlementId}/payment`,
      data
    );
    return response.data;
  },

  /**
   * Put settlement on hold
   */
  hold: async (settlementId: string, data: SettlementHold): Promise<ExitSettlement> => {
    const response = await apiClient.post<ExitSettlement>(
      `${BASE_URL}/settlements/${settlementId}/hold`,
      data
    );
    return response.data;
  }
};

// ============================================================================
// SETTLEMENT COMPONENT API
// ============================================================================

export const settlementComponentService = {
  /**
   * Add settlement component
   */
  add: async (data: SettlementComponentCreate): Promise<SettlementComponent> => {
    const response = await apiClient.post<SettlementComponent>(`${BASE_URL}/settlement-components`, data);
    return response.data;
  },

  /**
   * List settlement components by settlement ID
   */
  listBySettlement: async (settlementId: string): Promise<SettlementComponent[]> => {
    const response = await apiClient.get<SettlementComponent[]>(
      `${BASE_URL}/settlements/${settlementId}/components`
    );
    return response.data;
  },

  /**
   * Update settlement component
   */
  update: async (componentId: string, data: SettlementComponentUpdate): Promise<SettlementComponent> => {
    const response = await apiClient.put<SettlementComponent>(
      `${BASE_URL}/settlement-components/${componentId}`,
      data
    );
    return response.data;
  },

  /**
   * Delete settlement component
   */
  delete: async (componentId: string): Promise<MessageResponse> => {
    const response = await apiClient.delete<MessageResponse>(
      `${BASE_URL}/settlement-components/${componentId}`
    );
    return response.data;
  }
};

// ============================================================================
// DOCUMENT API
// ============================================================================

export const documentService = {
  /**
   * Create a new document
   */
  create: async (data: DocumentCreate): Promise<ExitDocument> => {
    const response = await apiClient.post<ExitDocument>(`${BASE_URL}/documents`, data);
    return response.data;
  },

  /**
   * Get all documents with filters
   */
  list: async (filters?: DocumentFilters): Promise<PaginatedResponse<ExitDocument>> => {
    const response = await apiClient.get<PaginatedResponse<ExitDocument>>(`${BASE_URL}/documents`, {
      params: filters
    });
    return response.data;
  },

  /**
   * Get document by ID
   */
  getById: async (documentId: string): Promise<ExitDocument> => {
    const response = await apiClient.get<ExitDocument>(`${BASE_URL}/documents/${documentId}`);
    return response.data;
  },

  /**
   * Generate document from template
   */
  generate: async (resignationId: string, data: DocumentGenerate): Promise<ExitDocument> => {
    const response = await apiClient.post<ExitDocument>(
      `${BASE_URL}/resignations/${resignationId}/documents/generate`,
      data
    );
    return response.data;
  },

  /**
   * Approve document
   */
  approve: async (documentId: string, data: DocumentApproval): Promise<ExitDocument> => {
    const response = await apiClient.post<ExitDocument>(
      `${BASE_URL}/documents/${documentId}/approve`,
      data
    );
    return response.data;
  },

  /**
   * Issue document
   */
  issue: async (documentId: string, data: DocumentIssuance): Promise<ExitDocument> => {
    const response = await apiClient.post<ExitDocument>(
      `${BASE_URL}/documents/${documentId}/issue`,
      data
    );
    return response.data;
  },

  /**
   * Generate multiple documents for resignation
   */
  generateBulk: async (data: BulkDocumentGenerate): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>(`${BASE_URL}/documents/bulk-generate`, data);
    return response.data;
  },

  /**
   * Download document
   */
  download: async (documentId: string): Promise<Blob> => {
    const response = await apiClient.get<Blob>(
      `${BASE_URL}/documents/${documentId}/download`,
      { responseType: 'blob' }
    );
    return response.data;
  }
};

// ============================================================================
// DASHBOARD API
// ============================================================================

export const exitDashboardService = {
  /**
   * Get dashboard statistics
   */
  getStats: async (): Promise<ExitDashboardStats> => {
    const response = await apiClient.get<ExitDashboardStats>(`${BASE_URL}/dashboard/stats`);
    return response.data;
  }
};

// ============================================================================
// COMBINED EXPORT
// ============================================================================

export const exitManagementService = {
  resignations: resignationService,
  clearances: clearanceService,
  settlements: settlementService,
  settlementComponents: settlementComponentService,
  documents: documentService,
  dashboard: exitDashboardService
};

export default exitManagementService;
