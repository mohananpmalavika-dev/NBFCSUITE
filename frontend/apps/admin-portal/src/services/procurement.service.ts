/**
 * Procurement API Service
 * Handles all API calls for procurement module
 */

import axios from 'axios';
import type {
  Vendor,
  VendorFormData,
  VendorRating,
  PurchaseRequisition,
  PurchaseRequisitionFormData,
  PurchaseOrder,
  ApiResponse,
  PaginatedResponse,
  DashboardMetrics,
  VendorStatus,
  VendorType,
  RequisitionStatus,
  RequisitionPriority,
  POStatus,
} from '@/types/procurement';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const PROCUREMENT_API = `${API_BASE_URL}/api/v1/procurement`;

// ============================================================================
// VENDOR APIs
// ============================================================================

export const vendorApi = {
  /**
   * Get all vendors with filters
   */
  list: async (params?: {
    status?: VendorStatus;
    vendor_type?: VendorType;
    search?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await axios.get<ApiResponse<PaginatedResponse<Vendor>>>(
      `${PROCUREMENT_API}/vendors`,
      { params }
    );
    return response.data;
  },

  /**
   * Get vendor by ID
   */
  getById: async (vendorId: string) => {
    const response = await axios.get<ApiResponse<Vendor>>(
      `${PROCUREMENT_API}/vendors/${vendorId}`
    );
    return response.data;
  },

  /**
   * Create new vendor
   */
  create: async (data: VendorFormData) => {
    const response = await axios.post<ApiResponse<Vendor>>(
      `${PROCUREMENT_API}/vendors`,
      data
    );
    return response.data;
  },

  /**
   * Update vendor
   */
  update: async (vendorId: string, data: Partial<VendorFormData>) => {
    const response = await axios.put<ApiResponse<Vendor>>(
      `${PROCUREMENT_API}/vendors/${vendorId}`,
      data
    );
    return response.data;
  },

  /**
   * Delete vendor
   */
  delete: async (vendorId: string) => {
    const response = await axios.delete<ApiResponse<void>>(
      `${PROCUREMENT_API}/vendors/${vendorId}`
    );
    return response.data;
  },

  /**
   * Change vendor status
   */
  changeStatus: async (vendorId: string, status: VendorStatus, reason?: string) => {
    const response = await axios.patch<ApiResponse<Vendor>>(
      `${PROCUREMENT_API}/vendors/${vendorId}/status`,
      { status, reason }
    );
    return response.data;
  },

  /**
   * Create vendor rating
   */
  createRating: async (vendorId: string, rating: Partial<VendorRating>) => {
    const response = await axios.post<ApiResponse<VendorRating>>(
      `${PROCUREMENT_API}/vendors/${vendorId}/ratings`,
      rating
    );
    return response.data;
  },

  /**
   * Get vendor ratings
   */
  getRatings: async (vendorId: string) => {
    const response = await axios.get<ApiResponse<VendorRating[]>>(
      `${PROCUREMENT_API}/vendors/${vendorId}/ratings`
    );
    return response.data;
  },

  /**
   * Get top vendors
   */
  getTopVendors: async (limit: number = 10) => {
    const response = await axios.get<ApiResponse<Vendor[]>>(
      `${PROCUREMENT_API}/vendors/top`,
      { params: { limit } }
    );
    return response.data;
  },
};

// ============================================================================
// REQUISITION APIs
// ============================================================================

export const requisitionApi = {
  /**
   * Get all requisitions with filters
   */
  list: async (params?: {
    status?: RequisitionStatus;
    priority?: RequisitionPriority;
    department?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await axios.get<ApiResponse<PaginatedResponse<PurchaseRequisition>>>(
      `${PROCUREMENT_API}/requisitions`,
      { params }
    );
    return response.data;
  },

  /**
   * Get requisition by ID
   */
  getById: async (requisitionId: string) => {
    const response = await axios.get<ApiResponse<PurchaseRequisition>>(
      `${PROCUREMENT_API}/requisitions/${requisitionId}`
    );
    return response.data;
  },

  /**
   * Create new requisition
   */
  create: async (data: PurchaseRequisitionFormData) => {
    const response = await axios.post<ApiResponse<PurchaseRequisition>>(
      `${PROCUREMENT_API}/requisitions`,
      data
    );
    return response.data;
  },

  /**
   * Update requisition
   */
  update: async (requisitionId: string, data: Partial<PurchaseRequisitionFormData>) => {
    const response = await axios.put<ApiResponse<PurchaseRequisition>>(
      `${PROCUREMENT_API}/requisitions/${requisitionId}`,
      data
    );
    return response.data;
  },

  /**
   * Delete requisition
   */
  delete: async (requisitionId: string) => {
    const response = await axios.delete<ApiResponse<void>>(
      `${PROCUREMENT_API}/requisitions/${requisitionId}`
    );
    return response.data;
  },

  /**
   * Submit requisition for approval
   */
  submit: async (requisitionId: string) => {
    const response = await axios.post<ApiResponse<PurchaseRequisition>>(
      `${PROCUREMENT_API}/requisitions/${requisitionId}/submit`
    );
    return response.data;
  },

  /**
   * Approve or reject requisition
   */
  approve: async (requisitionId: string, approved: boolean, remarks?: string) => {
    const response = await axios.post<ApiResponse<PurchaseRequisition>>(
      `${PROCUREMENT_API}/requisitions/${requisitionId}/approve`,
      { approved, approval_remarks: remarks }
    );
    return response.data;
  },

  /**
   * Cancel requisition
   */
  cancel: async (requisitionId: string, reason: string) => {
    const response = await axios.post<ApiResponse<PurchaseRequisition>>(
      `${PROCUREMENT_API}/requisitions/${requisitionId}/cancel`,
      { cancellation_reason: reason }
    );
    return response.data;
  },

  /**
   * Get requisition statistics
   */
  getStats: async () => {
    const response = await axios.get<ApiResponse<any>>(
      `${PROCUREMENT_API}/requisitions/statistics`
    );
    return response.data;
  },
};

// ============================================================================
// PURCHASE ORDER APIs
// ============================================================================

export const purchaseOrderApi = {
  /**
   * Get all purchase orders with filters
   */
  getAll: async (params?: {
    status?: POStatus;
    vendor_id?: string;
    page?: number;
    page_size?: number;
  }) => {
    const response = await axios.get<ApiResponse<PurchaseOrder[]>>(
      `${PROCUREMENT_API}/purchase-orders`,
      { params }
    );
    return response.data;
  },

  /**
   * Get purchase order by ID
   */
  getById: async (poId: string) => {
    const response = await axios.get<ApiResponse<PurchaseOrder>>(
      `${PROCUREMENT_API}/purchase-orders/${poId}`
    );
    return response.data;
  },

  /**
   * Create purchase order
   */
  create: async (data: any) => {
    const response = await axios.post<ApiResponse<PurchaseOrder>>(
      `${PROCUREMENT_API}/purchase-orders`,
      data
    );
    return response.data;
  },

  /**
   * Approve purchase order
   */
  approve: async (poId: string) => {
    const response = await axios.post<ApiResponse<PurchaseOrder>>(
      `${PROCUREMENT_API}/purchase-orders/${poId}/approve`
    );
    return response.data;
  },

  /**
   * Send PO to vendor
   */
  send: async (poId: string) => {
    const response = await axios.post<ApiResponse<PurchaseOrder>>(
      `${PROCUREMENT_API}/purchase-orders/${poId}/send`
    );
    return response.data;
  },

  /**
   * Vendor acknowledges PO
   */
  acknowledge: async (poId: string) => {
    const response = await axios.post<ApiResponse<PurchaseOrder>>(
      `${PROCUREMENT_API}/purchase-orders/${poId}/acknowledge`
    );
    return response.data;
  },

  /**
   * Cancel purchase order
   */
  cancel: async (poId: string, reason: string) => {
    const response = await axios.post<ApiResponse<PurchaseOrder>>(
      `${PROCUREMENT_API}/purchase-orders/${poId}/cancel`,
      { cancellation_reason: reason }
    );
    return response.data;
  },

  /**
   * Get PO statistics
   */
  getStats: async () => {
    const response = await axios.get<ApiResponse<any>>(
      `${PROCUREMENT_API}/purchase-orders/statistics`
    );
    return response.data;
  },
};

// ============================================================================
// DASHBOARD APIs
// ============================================================================

export const dashboardApi = {
  /**
   * Get dashboard statistics
   */
  getStats: async () => {
    const response = await axios.get<ApiResponse<any>>(
      `${PROCUREMENT_API}/dashboard`
    );
    return response.data;
  },
};

// Export all APIs
export const procurementService = {
  vendor: vendorApi,
  requisition: requisitionApi,
  purchaseOrder: purchaseOrderApi,
  dashboard: dashboardApi,
};

export default procurementService;
