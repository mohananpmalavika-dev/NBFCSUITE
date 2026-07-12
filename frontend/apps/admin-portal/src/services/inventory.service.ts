/**
 * Inventory Management API Service
 * Handles all API calls for inventory module
 */

import axios from 'axios';
import type {
  ItemMaster,
  ItemMasterFormData,
  StockTransaction,
  StockTransactionFormData,
  StockVerification,
  StockVerificationFormData,
  InventoryValuation,
  InventoryValuationFormData,
  InventoryDashboardMetrics,
  StockLedgerEntry,
  LowStockAlert,
  ApiResponse,
  PaginatedResponse,
  ItemType,
  ItemStatus,
  TransactionType,
  TransactionStatus,
  VerificationStatus,
} from '@/types/inventory';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const INVENTORY_API = `${API_BASE_URL}/api/v1/inventory`;

// ============================================================================
// ITEM MASTER APIs
// ============================================================================

export const itemMasterApi = {
  /**
   * Get all items with filters
   */
  list: async (params?: {
    item_type?: ItemType;
    item_status?: ItemStatus;
    category?: string;
    search?: string;
    low_stock_only?: boolean;
    page?: number;
    page_size?: number;
  }) => {
    const response = await axios.get<ApiResponse<PaginatedResponse<ItemMaster>>>(
      `${INVENTORY_API}/items`,
      { params }
    );
    return response.data;
  },

  /**
   * Get item by ID
   */
  getById: async (itemId: string) => {
    const response = await axios.get<ApiResponse<ItemMaster>>(
      `${INVENTORY_API}/items/${itemId}`
    );
    return response.data;
  },

  /**
   * Create new item
   */
  create: async (data: ItemMasterFormData) => {
    const response = await axios.post<ApiResponse<ItemMaster>>(
      `${INVENTORY_API}/items`,
      data
    );
    return response.data;
  },

  /**
   * Update item
   */
  update: async (itemId: string, data: Partial<ItemMasterFormData>) => {
    const response = await axios.put<ApiResponse<ItemMaster>>(
      `${INVENTORY_API}/items/${itemId}`,
      data
    );
    return response.data;
  },

  /**
   * Delete item
   */
  delete: async (itemId: string) => {
    const response = await axios.delete<ApiResponse<void>>(
      `${INVENTORY_API}/items/${itemId}`
    );
    return response.data;
  },

  /**
   * Get low stock items
   */
  getLowStockAlerts: async () => {
    const response = await axios.get<ApiResponse<LowStockAlert[]>>(
      `${INVENTORY_API}/items/alerts/low-stock`
    );
    return response.data;
  },
};


// ============================================================================
// STOCK TRANSACTION APIs
// ============================================================================

export const stockTransactionApi = {
  /**
   * Get all transactions with filters
   */
  list: async (params?: {
    transaction_type?: TransactionType;
    transaction_status?: TransactionStatus;
    item_id?: string;
    from_date?: string;
    to_date?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await axios.get<ApiResponse<PaginatedResponse<StockTransaction>>>(
      `${INVENTORY_API}/transactions`,
      { params }
    );
    return response.data;
  },

  /**
   * Get transaction by ID
   */
  getById: async (transactionId: string) => {
    const response = await axios.get<ApiResponse<StockTransaction>>(
      `${INVENTORY_API}/transactions/${transactionId}`
    );
    return response.data;
  },

  /**
   * Create new transaction
   */
  create: async (data: StockTransactionFormData) => {
    const response = await axios.post<ApiResponse<StockTransaction>>(
      `${INVENTORY_API}/transactions`,
      data
    );
    return response.data;
  },

  /**
   * Approve transaction
   */
  approve: async (transactionId: string) => {
    const response = await axios.post<ApiResponse<StockTransaction>>(
      `${INVENTORY_API}/transactions/${transactionId}/approve`
    );
    return response.data;
  },

  /**
   * Post transaction
   */
  post: async (transactionId: string) => {
    const response = await axios.post<ApiResponse<StockTransaction>>(
      `${INVENTORY_API}/transactions/${transactionId}/post`
    );
    return response.data;
  },

  /**
   * Cancel transaction
   */
  cancel: async (transactionId: string, reason: string) => {
    const response = await axios.post<ApiResponse<StockTransaction>>(
      `${INVENTORY_API}/transactions/${transactionId}/cancel`,
      null,
      { params: { reason } }
    );
    return response.data;
  },

  /**
   * Get stock ledger for an item
   */
  getStockLedger: async (
    itemId: string,
    from_date?: string,
    to_date?: string
  ) => {
    const response = await axios.get<ApiResponse<StockLedgerEntry[]>>(
      `${INVENTORY_API}/transactions/item/${itemId}/ledger`,
      { params: { from_date, to_date } }
    );
    return response.data;
  },
};


// ============================================================================
// STOCK VERIFICATION APIs
// ============================================================================

export const stockVerificationApi = {
  /**
   * Get all verifications with filters
   */
  list: async (params?: {
    verification_status?: VerificationStatus;
    from_date?: string;
    to_date?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await axios.get<ApiResponse<PaginatedResponse<StockVerification>>>(
      `${INVENTORY_API}/verifications`,
      { params }
    );
    return response.data;
  },

  /**
   * Get verification by ID
   */
  getById: async (verificationId: string) => {
    const response = await axios.get<ApiResponse<StockVerification>>(
      `${INVENTORY_API}/verifications/${verificationId}`
    );
    return response.data;
  },

  /**
   * Create new verification
   */
  create: async (data: StockVerificationFormData) => {
    const response = await axios.post<ApiResponse<StockVerification>>(
      `${INVENTORY_API}/verifications`,
      data
    );
    return response.data;
  },

  /**
   * Update verification item physical quantity
   */
  updateItem: async (
    itemId: string,
    physical_quantity: number,
    remarks?: string
  ) => {
    const response = await axios.put<ApiResponse<any>>(
      `${INVENTORY_API}/verifications/items/${itemId}`,
      { physical_quantity, remarks }
    );
    return response.data;
  },

  /**
   * Complete verification
   */
  complete: async (verificationId: string) => {
    const response = await axios.post<ApiResponse<StockVerification>>(
      `${INVENTORY_API}/verifications/${verificationId}/complete`
    );
    return response.data;
  },

  /**
   * Reconcile variance
   */
  reconcileVariance: async (itemId: string, reconciliation_notes: string) => {
    const response = await axios.post<ApiResponse<any>>(
      `${INVENTORY_API}/verifications/items/${itemId}/reconcile`,
      null,
      { params: { reconciliation_notes } }
    );
    return response.data;
  },
};


// ============================================================================
// INVENTORY VALUATION APIs
// ============================================================================

export const inventoryValuationApi = {
  /**
   * Get all valuations with filters
   */
  list: async (params?: {
    financial_year?: number;
    from_date?: string;
    to_date?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await axios.get<ApiResponse<PaginatedResponse<InventoryValuation>>>(
      `${INVENTORY_API}/valuations`,
      { params }
    );
    return response.data;
  },

  /**
   * Get valuation by ID
   */
  getById: async (valuationId: string) => {
    const response = await axios.get<ApiResponse<InventoryValuation>>(
      `${INVENTORY_API}/valuations/${valuationId}`
    );
    return response.data;
  },

  /**
   * Create new valuation
   */
  create: async (data: InventoryValuationFormData) => {
    const response = await axios.post<ApiResponse<InventoryValuation>>(
      `${INVENTORY_API}/valuations`,
      data
    );
    return response.data;
  },

  /**
   * Finalize valuation
   */
  finalize: async (valuationId: string) => {
    const response = await axios.post<ApiResponse<InventoryValuation>>(
      `${INVENTORY_API}/valuations/${valuationId}/finalize`
    );
    return response.data;
  },

  /**
   * Get valuation summary for financial year
   */
  getSummary: async (financial_year: number) => {
    const response = await axios.get<ApiResponse<any>>(
      `${INVENTORY_API}/valuations/summary/${financial_year}`
    );
    return response.data;
  },
};

// ============================================================================
// DASHBOARD & REPORTS APIs
// ============================================================================

export const inventoryDashboardApi = {
  /**
   * Get dashboard metrics
   */
  getMetrics: async () => {
    const response = await axios.get<ApiResponse<InventoryDashboardMetrics>>(
      `${INVENTORY_API}/dashboard/metrics`
    );
    return response.data;
  },
};

// ============================================================================
// Export combined service
// ============================================================================

export const inventoryService = {
  items: itemMasterApi,
  transactions: stockTransactionApi,
  verifications: stockVerificationApi,
  valuations: inventoryValuationApi,
  dashboard: inventoryDashboardApi,
};

export default inventoryService;
