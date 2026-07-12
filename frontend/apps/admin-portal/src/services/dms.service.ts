/**
 * Document Management System (DMS) Service
 * API client for document management operations
 */

import { apiClient as api } from '@/lib/api-client';
import {
  Document,
  DocumentCreate,
  DocumentUpdate,
  DocumentVersion,
  DocumentVersionCreate,
  DocumentFilters,
  PaginatedDocumentResponse,
  DocumentWorkflow,
  WorkflowCreate,
  WorkflowTemplate,
  DocumentApproval,
  ApprovalAction,
  ApprovalDelegation,
  DocumentSignature,
  SignatureRequest,
  SignatureData,
  DocumentPermission,
  PermissionGrant,
  BulkPermissionGrant,
  PermissionType,
  DocumentComment,
  CommentCreate,
  DocumentStatistics,
  DMSDashboardStats
} from '../types/dms.types';

const BASE_URL = '/api/v1/dms';

export const dmsService = {
  // ============================================================================
  // DOCUMENT CRUD
  // ============================================================================

  /**
   * Create new document with file upload
   */
  createDocument: async (data: DocumentCreate): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('title', data.title);
    if (data.description) formData.append('description', data.description);
    formData.append('document_type', data.document_type);
    if (data.status) formData.append('status', data.status);
    if (data.access_level) formData.append('access_level', data.access_level);
    if (data.customer_id) formData.append('customer_id', data.customer_id.toString());
    if (data.loan_id) formData.append('loan_id', data.loan_id.toString());
    if (data.policy_id) formData.append('policy_id', data.policy_id.toString());
    if (data.reference_type) formData.append('reference_type', data.reference_type);
    if (data.reference_id) formData.append('reference_id', data.reference_id.toString());
    if (data.expiry_date) formData.append('expiry_date', data.expiry_date);
    if (data.tags) formData.append('tags', JSON.stringify(data.tags));
    if (data.metadata) formData.append('metadata', JSON.stringify(data.metadata));

    const response = await api.post<Document>(`${BASE_URL}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Get document by ID
   */
  getDocument: async (id: number): Promise<Document> => {
    const response = await api.get<Document>(`${BASE_URL}/documents/${id}`);
    return response.data;
  },

  /**
   * Update document metadata
   */
  updateDocument: async (id: number, data: DocumentUpdate): Promise<Document> => {
    const response = await api.put<Document>(`${BASE_URL}/documents/${id}`, data);
    return response.data;
  },

  /**
   * Delete document (soft delete)
   */
  deleteDocument: async (id: number): Promise<void> => {
    await api.delete(`${BASE_URL}/documents/${id}`);
  },

  /**
   * List documents with filters and pagination
   */
  listDocuments: async (filters: DocumentFilters = {}): Promise<PaginatedDocumentResponse> => {
    const response = await api.get<PaginatedDocumentResponse>(`${BASE_URL}/documents`, {
      params: {
        ...filters,
        tags: filters.tags ? JSON.stringify(filters.tags) : undefined,
      },
    });
    return response.data;
  },

  /**
   * Search documents
   */
  searchDocuments: async (query: string, filters: Partial<DocumentFilters> = {}): Promise<PaginatedDocumentResponse> => {
    const response = await api.get<PaginatedDocumentResponse>(`${BASE_URL}/documents/search`, {
      params: {
        q: query,
        ...filters,
      },
    });
    return response.data;
  },

  /**
   * Download document file
   */
  downloadDocument: async (id: number, versionId?: number): Promise<Blob> => {
    const url = versionId 
      ? `${BASE_URL}/documents/${id}/download?version_id=${versionId}`
      : `${BASE_URL}/documents/${id}/download`;
    
    const response = await api.get(url, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Helper to trigger file download in browser
   */
  triggerDownload: (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  // ============================================================================
  // VERSION MANAGEMENT
  // ============================================================================

  /**
   * Upload new version of document
   */
  uploadVersion: async (documentId: number, data: DocumentVersionCreate): Promise<DocumentVersion> => {
    const formData = new FormData();
    formData.append('file', data.file);
    if (data.change_description) formData.append('change_description', data.change_description);

    const response = await api.post<DocumentVersion>(
      `${BASE_URL}/documents/${documentId}/versions`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * List all versions of a document
   */
  listVersions: async (documentId: number): Promise<DocumentVersion[]> => {
    const response = await api.get<DocumentVersion[]>(`${BASE_URL}/documents/${documentId}/versions`);
    return response.data;
  },

  // ============================================================================
  // WORKFLOW MANAGEMENT
  // ============================================================================

  /**
   * Create workflow for document
   */
  createWorkflow: async (data: WorkflowCreate): Promise<DocumentWorkflow> => {
    const response = await api.post<DocumentWorkflow>(`${BASE_URL}/workflows`, data);
    return response.data;
  },

  /**
   * Get workflow by ID
   */
  getWorkflow: async (id: number): Promise<DocumentWorkflow> => {
    const response = await api.get<DocumentWorkflow>(`${BASE_URL}/workflows/${id}`);
    return response.data;
  },

  /**
   * Approve workflow stage
   */
  approveWorkflow: async (workflowId: number, data: ApprovalAction): Promise<DocumentApproval> => {
    const response = await api.post<DocumentApproval>(`${BASE_URL}/workflows/${workflowId}/approve`, data);
    return response.data;
  },

  /**
   * Reject workflow stage
   */
  rejectWorkflow: async (workflowId: number, data: ApprovalAction): Promise<DocumentApproval> => {
    const response = await api.post<DocumentApproval>(`${BASE_URL}/workflows/${workflowId}/reject`, data);
    return response.data;
  },

  /**
   * Delegate workflow approval
   */
  delegateWorkflow: async (workflowId: number, data: ApprovalDelegation): Promise<DocumentApproval> => {
    const response = await api.post<DocumentApproval>(`${BASE_URL}/workflows/${workflowId}/delegate`, data);
    return response.data;
  },

  /**
   * Cancel workflow
   */
  cancelWorkflow: async (workflowId: number): Promise<DocumentWorkflow> => {
    const response = await api.post<DocumentWorkflow>(`${BASE_URL}/workflows/${workflowId}/cancel`);
    return response.data;
  },

  /**
   * Get pending approvals for current user
   */
  getPendingApprovals: async (page = 1, pageSize = 20): Promise<any> => {
    const response = await api.get(`${BASE_URL}/workflows/pending-approvals`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  /**
   * Get document workflows
   */
  getDocumentWorkflows: async (documentId: number): Promise<DocumentWorkflow[]> => {
    const response = await api.get<DocumentWorkflow[]>(`${BASE_URL}/workflows/document/${documentId}`);
    return response.data;
  },

  // ============================================================================
  // WORKFLOW TEMPLATES
  // ============================================================================

  /**
   * List workflow templates
   */
  listWorkflowTemplates: async (): Promise<WorkflowTemplate[]> => {
    const response = await api.get<WorkflowTemplate[]>(`${BASE_URL}/workflows/templates`);
    return response.data;
  },

  /**
   * Create workflow template
   */
  createWorkflowTemplate: async (data: Partial<WorkflowTemplate>): Promise<WorkflowTemplate> => {
    const response = await api.post<WorkflowTemplate>(`${BASE_URL}/workflows/templates`, data);
    return response.data;
  },

  /**
   * Get workflow template by ID
   */
  getWorkflowTemplate: async (id: number): Promise<WorkflowTemplate> => {
    const response = await api.get<WorkflowTemplate>(`${BASE_URL}/workflows/templates/${id}`);
    return response.data;
  },

  // ============================================================================
  // E-SIGNATURE MANAGEMENT
  // ============================================================================

  /**
   * Request signatures for document
   */
  requestSignatures: async (data: SignatureRequest): Promise<DocumentSignature[]> => {
    const response = await api.post<DocumentSignature[]>(`${BASE_URL}/signatures/request`, data);
    return response.data;
  },

  /**
   * Sign document
   */
  signDocument: async (signatureId: number, data: SignatureData): Promise<DocumentSignature> => {
    const response = await api.post<DocumentSignature>(`${BASE_URL}/signatures/${signatureId}/sign`, data);
    return response.data;
  },

  /**
   * Decline signature request
   */
  declineSignature: async (signatureId: number, reason: string): Promise<DocumentSignature> => {
    const response = await api.post<DocumentSignature>(`${BASE_URL}/signatures/${signatureId}/decline`, {
      reason,
    });
    return response.data;
  },

  /**
   * Get pending signatures for current user
   */
  getPendingSignatures: async (page = 1, pageSize = 20): Promise<any> => {
    const response = await api.get(`${BASE_URL}/signatures/pending`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  /**
   * Get document signatures
   */
  getDocumentSignatures: async (documentId: number): Promise<DocumentSignature[]> => {
    const response = await api.get<DocumentSignature[]>(`${BASE_URL}/signatures/document/${documentId}`);
    return response.data;
  },

  /**
   * Verify signature
   */
  verifySignature: async (signatureId: number): Promise<any> => {
    const response = await api.get(`${BASE_URL}/signatures/${signatureId}/verify`);
    return response.data;
  },

  /**
   * Resend signature request
   */
  resendSignatureRequest: async (signatureId: number): Promise<void> => {
    await api.post(`${BASE_URL}/signatures/${signatureId}/resend`);
  },

  // ============================================================================
  // PERMISSION MANAGEMENT
  // ============================================================================

  /**
   * Grant permission to user/role
   */
  grantPermission: async (data: PermissionGrant): Promise<DocumentPermission> => {
    const response = await api.post<DocumentPermission>(`${BASE_URL}/permissions/grant`, data);
    return response.data;
  },

  /**
   * Revoke permission
   */
  revokePermission: async (permissionId: number): Promise<void> => {
    await api.delete(`${BASE_URL}/permissions/${permissionId}`);
  },

  /**
   * Check user permission for document
   */
  checkPermission: async (documentId: number, permissionType: PermissionType): Promise<boolean> => {
    const response = await api.get<{ has_permission: boolean }>(
      `${BASE_URL}/permissions/check/${documentId}`,
      {
        params: { permission_type: permissionType },
      }
    );
    return response.data.has_permission;
  },

  /**
   * Get document permissions
   */
  getDocumentPermissions: async (documentId: number): Promise<DocumentPermission[]> => {
    const response = await api.get<DocumentPermission[]>(`${BASE_URL}/permissions/document/${documentId}`);
    return response.data;
  },

  /**
   * Get user's accessible documents
   */
  getUserAccessibleDocuments: async (userId: number, filters: DocumentFilters = {}): Promise<PaginatedDocumentResponse> => {
    const response = await api.get<PaginatedDocumentResponse>(`${BASE_URL}/permissions/user/${userId}/documents`, {
      params: filters,
    });
    return response.data;
  },

  /**
   * Bulk grant permissions
   */
  bulkGrantPermissions: async (data: BulkPermissionGrant): Promise<DocumentPermission[]> => {
    const response = await api.post<DocumentPermission[]>(`${BASE_URL}/permissions/bulk-grant`, data);
    return response.data;
  },

  // ============================================================================
  // COMMENTS
  // ============================================================================

  /**
   * Add comment to document
   */
  addComment: async (data: CommentCreate): Promise<DocumentComment> => {
    const response = await api.post<DocumentComment>(`${BASE_URL}/comments`, data);
    return response.data;
  },

  /**
   * Get document comments
   */
  getDocumentComments: async (documentId: number): Promise<DocumentComment[]> => {
    const response = await api.get<DocumentComment[]>(`${BASE_URL}/comments/document/${documentId}`);
    return response.data;
  },

  // ============================================================================
  // STATISTICS & DASHBOARD
  // ============================================================================

  /**
   * Get document statistics
   */
  getStatistics: async (): Promise<DocumentStatistics> => {
    const response = await api.get<DocumentStatistics>(`${BASE_URL}/statistics`);
    return response.data;
  },

  /**
   * Get dashboard data
   */
  getDashboard: async (): Promise<DMSDashboardStats> => {
    const response = await api.get<DMSDashboardStats>(`${BASE_URL}/dashboard`);
    return response.data;
  },
};

export default dmsService;
