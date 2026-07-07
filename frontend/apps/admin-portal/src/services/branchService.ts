/**
 * Branch & Operations Management Service
 */

import { apiClient } from '@/lib/api-client';
import type {
  Organization,
  OrganizationFormData,
  OrganizationHierarchy,
  Branch,
  BranchFormData,
  BranchDayOperation,
  DayBeginFormData,
  DayEndFormData,
  BranchCounter,
  CounterFormData,
  CashTransaction,
  CashTransactionFormData,
  CashDenomination,
  CashPosition,
  BranchPerformance,
  BranchTarget,
  BranchTargetFormData,
  BranchDashboard,
  BranchAuditLog,
} from '@/types/branch';

// ============================================
// ORGANIZATION APIs
// ============================================

export const organizationService = {
  /**
   * Create organization
   */
  create: async (data: OrganizationFormData): Promise<Organization> => {
    const response = await apiClient.post('/branch/organizations', data);
    return response.data.data;
  },

  /**
   * Get organizations list
   */
  list: async (params?: {
    level?: string;
    parent_id?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ items: Organization[]; total: number }> => {
    const response = await apiClient.get('/branch/organizations', { params });
    return response.data.data;
  },

  /**
   * Get organization hierarchy
   */
  getHierarchy: async (): Promise<OrganizationHierarchy[]> => {
    const response = await apiClient.get('/branch/organizations/hierarchy');
    return response.data.data;
  },

  /**
   * Get organization by ID
   */
  getById: async (id: string): Promise<Organization> => {
    const response = await apiClient.get(`/branch/organizations/${id}`);
    return response.data.data;
  },

  /**
   * Update organization
   */
  update: async (id: string, data: Partial<OrganizationFormData>): Promise<Organization> => {
    const response = await apiClient.put(`/branch/organizations/${id}`, data);
    return response.data.data;
  },

  /**
   * Delete organization
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/branch/organizations/${id}`);
  },
};

// ============================================
// BRANCH APIs
// ============================================

export const branchService = {
  /**
   * Create branch
   */
  create: async (data: BranchFormData): Promise<Branch> => {
    const response = await apiClient.post('/branch/branches', data);
    return response.data.data;
  },

  /**
   * Get branches list
   */
  list: async (params?: {
    organization_id?: string;
    branch_type?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ items: Branch[]; total: number }> => {
    const response = await apiClient.get('/branch/branches', { params });
    return response.data.data;
  },

  /**
   * Get branch by ID
   */
  getById: async (id: string): Promise<Branch> => {
    const response = await apiClient.get(`/branch/branches/${id}`);
    return response.data.data;
  },

  /**
   * Get branch by code
   */
  getByCode: async (code: string): Promise<Branch> => {
    const response = await apiClient.get(`/branch/branches/code/${code}`);
    return response.data.data;
  },

  /**
   * Update branch
   */
  update: async (id: string, data: Partial<BranchFormData>): Promise<Branch> => {
    const response = await apiClient.put(`/branch/branches/${id}`, data);
    return response.data.data;
  },

  /**
   * Delete branch
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/branch/branches/${id}`);
  },

  /**
   * Get branch dashboard
   */
  getDashboard: async (branchId: string): Promise<BranchDashboard> => {
    const response = await apiClient.get(`/branch/branches/${branchId}/dashboard`);
    return response.data.data;
  },
};

// ============================================
// DAY OPERATIONS APIs
// ============================================

export const dayOperationService = {
  /**
   * Begin day operations
   */
  dayBegin: async (data: DayBeginFormData): Promise<BranchDayOperation> => {
    const response = await apiClient.post('/branch/day-operations/day-begin', data);
    return response.data.data;
  },

  /**
   * End day operations
   */
  dayEnd: async (data: DayEndFormData): Promise<BranchDayOperation> => {
    const response = await apiClient.post('/branch/day-operations/day-end', data);
    return response.data.data;
  },

  /**
   * Get day operations list
   */
  list: async (params?: {
    branch_id?: string;
    from_date?: string;
    to_date?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ items: BranchDayOperation[]; total: number }> => {
    const response = await apiClient.get('/branch/day-operations', { params });
    return response.data.data;
  },

  /**
   * Get day operation by ID
   */
  getById: async (id: string): Promise<BranchDayOperation> => {
    const response = await apiClient.get(`/branch/day-operations/${id}`);
    return response.data.data;
  },
};

// ============================================
// COUNTER APIs
// ============================================

export const counterService = {
  /**
   * Create counter
   */
  create: async (data: CounterFormData): Promise<BranchCounter> => {
    const response = await apiClient.post('/branch/day-operations/counters', data);
    return response.data.data;
  },

  /**
   * Get counters list
   */
  list: async (params?: {
    branch_id?: string;
    is_open?: boolean;
  }): Promise<BranchCounter[]> => {
    const response = await apiClient.get('/branch/day-operations/counters', { params });
    return response.data.data;
  },

  /**
   * Open counter
   */
  open: async (counterId: string, openingBalance: number): Promise<BranchCounter> => {
    const response = await apiClient.post(
      `/branch/day-operations/counters/${counterId}/open`,
      { opening_balance: openingBalance }
    );
    return response.data.data;
  },

  /**
   * Close counter
   */
  close: async (
    counterId: string,
    closingBalance: number,
    physicalCount?: number
  ): Promise<BranchCounter> => {
    const response = await apiClient.post(
      `/branch/day-operations/counters/${counterId}/close`,
      { closing_balance: closingBalance, physical_count: physicalCount }
    );
    return response.data.data;
  },
};

// ============================================
// CASH TRANSACTION APIs
// ============================================

export const cashTransactionService = {
  /**
   * Create cash transaction
   */
  create: async (data: CashTransactionFormData): Promise<CashTransaction> => {
    const response = await apiClient.post('/branch/cash/transactions', data);
    return response.data.data;
  },

  /**
   * Get cash transactions list
   */
  list: async (params?: {
    branch_id?: string;
    counter_id?: string;
    transaction_type?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ items: CashTransaction[]; total: number }> => {
    const response = await apiClient.get('/branch/cash/transactions', { params });
    return response.data.data;
  },

  /**
   * Get cash transaction by ID
   */
  getById: async (id: string): Promise<CashTransaction> => {
    const response = await apiClient.get(`/branch/cash/transactions/${id}`);
    return response.data.data;
  },

  /**
   * Cancel cash transaction
   */
  cancel: async (id: string, reason: string): Promise<CashTransaction> => {
    const response = await apiClient.post(
      `/branch/cash/transactions/${id}/cancel?reason=${encodeURIComponent(reason)}`
    );
    return response.data.data;
  },

  /**
   * Get cash summary
   */
  getSummary: async (branchId: string, summaryDate?: string): Promise<any> => {
    const params = summaryDate ? { summary_date: summaryDate } : {};
    const response = await apiClient.get(`/branch/cash/summary`, {
      params: { branch_id: branchId, ...params },
    });
    return response.data.data;
  },
};

// ============================================
// CASH DENOMINATION APIs
// ============================================

export const cashDenominationService = {
  /**
   * Record cash denominations
   */
  create: async (data: {
    reference_type: string;
    reference_id: string;
    branch_id: string;
  } & CashDenomination): Promise<any> => {
    const response = await apiClient.post('/branch/cash/denominations', data);
    return response.data.data;
  },

  /**
   * Get cash denominations
   */
  get: async (referenceType: string, referenceId: string): Promise<any[]> => {
    const response = await apiClient.get('/branch/cash/denominations', {
      params: { reference_type: referenceType, reference_id: referenceId },
    });
    return response.data.data;
  },
};

// ============================================
// CASH POSITION APIs
// ============================================

export const cashPositionService = {
  /**
   * Get cash position
   */
  get: async (
    referenceType: string,
    referenceId: string,
    positionDate?: string
  ): Promise<CashPosition> => {
    const params = positionDate ? { position_date: positionDate } : {};
    const response = await apiClient.get('/branch/cash/position', {
      params: { reference_type: referenceType, reference_id: referenceId, ...params },
    });
    return response.data.data;
  },
};

// ============================================
// PERFORMANCE APIs
// ============================================

export const performanceService = {
  /**
   * Get branch performance
   */
  get: async (params: {
    branch_id: string;
    period_type: string;
    period_start: string;
    period_end: string;
  }): Promise<BranchPerformance> => {
    const response = await apiClient.get('/branch/performance', { params });
    return response.data.data;
  },

  /**
   * List branch performance records
   */
  list: async (params?: {
    branch_id?: string;
    period_type?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ items: BranchPerformance[]; total: number }> => {
    const response = await apiClient.get('/branch/performance/list', { params });
    return response.data.data;
  },

  /**
   * Calculate branch performance
   */
  calculate: async (params: {
    branch_id: string;
    period_type: string;
    period_start: string;
    period_end: string;
  }): Promise<BranchPerformance> => {
    const response = await apiClient.post('/branch/performance/calculate', null, { params });
    return response.data.data;
  },

  /**
   * Compare branch performance
   */
  compare: async (params: {
    period_type: string;
    period_start: string;
    period_end: string;
  }): Promise<any> => {
    const response = await apiClient.get('/branch/performance/comparison', { params });
    return response.data.data;
  },
};

// ============================================
// TARGET APIs
// ============================================

export const targetService = {
  /**
   * Create branch target
   */
  create: async (data: BranchTargetFormData): Promise<BranchTarget> => {
    const response = await apiClient.post('/branch/performance/targets', data);
    return response.data.data;
  },

  /**
   * Get branch targets list
   */
  list: async (params?: {
    branch_id?: string;
    target_period?: string;
    target_year?: number;
  }): Promise<BranchTarget[]> => {
    const response = await apiClient.get('/branch/performance/targets', { params });
    return response.data.data;
  },

  /**
   * Get branch target by ID
   */
  getById: async (id: string): Promise<BranchTarget> => {
    const response = await apiClient.get(`/branch/performance/targets/${id}`);
    return response.data.data;
  },

  /**
   * Update branch target
   */
  update: async (id: string, data: Partial<BranchTargetFormData>): Promise<BranchTarget> => {
    const response = await apiClient.put(`/branch/performance/targets/${id}`, data);
    return response.data.data;
  },

  /**
   * Delete branch target
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/branch/performance/targets/${id}`);
  },
};

// ============================================
// AUDIT LOG APIs
// ============================================

export const auditLogService = {
  /**
   * Get branch audit logs
   */
  list: async (params: {
    branch_id: string;
    event_type?: string;
    from_date?: string;
    to_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ items: BranchAuditLog[]; total: number }> => {
    const response = await apiClient.get('/branch/performance/audit-logs', { params });
    return response.data.data;
  },
};
