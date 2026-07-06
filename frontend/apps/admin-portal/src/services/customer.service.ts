/**
 * Customer Service
 * API calls for customer management
 */

import { apiClient } from '@/lib/api-client'
import type { 
  Customer, 
  CreateCustomerRequest,
  PaginatedResponse,
  PaginationParams,
  CustomerDocument,
  CustomerFamily,
  CustomerBankAccount,
  CustomerTimeline,
  BureauReport,
  CustomerKYC,
  DigiLockerDocument
} from '@/types'

export const customerService = {
  /**
   * Get all customers with pagination
   */
  async getCustomers(params?: PaginationParams & { search?: string; status?: string; kyc_status?: string; risk_rating?: string }) {
    return apiClient.get<PaginatedResponse<Customer>>('/customers', { params })
  },

  /**
   * Get customer by ID
   */
  async getCustomer(id: string) {
    return apiClient.get<Customer>(`/customers/${id}`)
  },

  /**
   * Create new customer
   */
  async createCustomer(data: CreateCustomerRequest) {
    return apiClient.post<Customer>('/customers', data)
  },

  /**
   * Update customer
   */
  async updateCustomer(id: string, data: Partial<CreateCustomerRequest>) {
    return apiClient.put<Customer>(`/customers/${id}`, data)
  },

  /**
   * Delete customer (soft delete)
   */
  async deleteCustomer(id: string) {
    return apiClient.delete(`/customers/${id}`)
  },

  /**
   * Search customers
   */
  async searchCustomers(query: string) {
    return apiClient.get<Customer[]>('/customers/search', { 
      params: { q: query } 
    })
  },

  /**
   * Get customer statistics
   */
  async getCustomerStats() {
    return apiClient.get('/customers/stats')
  },

  /**
   * Blacklist customer
   */
  async blacklistCustomer(id: string, reason: string) {
    return apiClient.post<Customer>(`/customers/${id}/blacklist`, null, { params: { reason } })
  },

  /**
   * Unblacklist customer
   */
  async unblacklistCustomer(id: string) {
    return apiClient.post<Customer>(`/customers/${id}/unblacklist`)
  },

  // ============================================================================
  // DOCUMENT MANAGEMENT
  // ============================================================================

  /**
   * Get customer documents
   */
  async getDocuments(customerId: string, params?: { document_type_id?: number; status?: string }) {
    return apiClient.get<CustomerDocument[]>(`/customers/${customerId}/documents`, { params })
  },

  /**
   * Upload document
   */
  async uploadDocument(customerId: string, data: FormData) {
    return apiClient.post<CustomerDocument>(`/customers/${customerId}/documents`, data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  /**
   * Get document by ID
   */
  async getDocument(customerId: string, documentId: number) {
    return apiClient.get<CustomerDocument>(`/customers/${customerId}/documents/${documentId}`)
  },

  /**
   * Verify document
   */
  async verifyDocument(customerId: string, documentId: number, status: 'verified' | 'rejected', remarks?: string) {
    return apiClient.post<CustomerDocument>(
      `/customers/${customerId}/documents/${documentId}/verify`,
      null,
      { params: { status, remarks } }
    )
  },

  /**
   * Delete document
   */
  async deleteDocument(customerId: string, documentId: number) {
    return apiClient.delete(`/customers/${customerId}/documents/${documentId}`)
  },

  // ============================================================================
  // FAMILY MEMBERS
  // ============================================================================

  /**
   * Get family members
   */
  async getFamilyMembers(customerId: string, params?: { is_nominee?: boolean; is_emergency_contact?: boolean }) {
    return apiClient.get<CustomerFamily[]>(`/customers/${customerId}/family`, { params })
  },

  /**
   * Add family member
   */
  async addFamilyMember(customerId: string, data: Partial<CustomerFamily>) {
    return apiClient.post<CustomerFamily>(`/customers/${customerId}/family`, data)
  },

  /**
   * Update family member
   */
  async updateFamilyMember(customerId: string, memberId: number, data: Partial<CustomerFamily>) {
    return apiClient.put<CustomerFamily>(`/customers/${customerId}/family/${memberId}`, data)
  },

  /**
   * Delete family member
   */
  async deleteFamilyMember(customerId: string, memberId: number) {
    return apiClient.delete(`/customers/${customerId}/family/${memberId}`)
  },

  /**
   * Validate nominees
   */
  async validateNominees(customerId: string) {
    return apiClient.get<{ valid: boolean; total_percentage: number; message: string }>(
      `/customers/${customerId}/family/validate-nominees`
    )
  },

  // ============================================================================
  // BANK ACCOUNTS
  // ============================================================================

  /**
   * Get bank accounts
   */
  async getBankAccounts(customerId: string, params?: { is_primary?: boolean; is_active?: boolean }) {
    return apiClient.get<CustomerBankAccount[]>(`/customers/${customerId}/accounts`, { params })
  },

  /**
   * Add bank account
   */
  async addBankAccount(customerId: string, data: Partial<CustomerBankAccount>) {
    return apiClient.post<CustomerBankAccount>(`/customers/${customerId}/accounts`, data)
  },

  /**
   * Update bank account
   */
  async updateBankAccount(customerId: string, accountId: number, data: Partial<CustomerBankAccount>) {
    return apiClient.put<CustomerBankAccount>(`/customers/${customerId}/accounts/${accountId}`, data)
  },

  /**
   * Set primary account
   */
  async setPrimaryAccount(customerId: string, accountId: number) {
    return apiClient.post<CustomerBankAccount>(`/customers/${customerId}/accounts/${accountId}/set-primary`)
  },

  /**
   * Verify account
   */
  async verifyAccount(customerId: string, accountId: number, method: string, remarks?: string) {
    return apiClient.post<CustomerBankAccount>(
      `/customers/${customerId}/accounts/${accountId}/verify`,
      null,
      { params: { verification_method: method, remarks } }
    )
  },

  /**
   * Delete bank account
   */
  async deleteBankAccount(customerId: string, accountId: number) {
    return apiClient.delete(`/customers/${customerId}/accounts/${accountId}`)
  },

  // ============================================================================
  // CREDIT BUREAU
  // ============================================================================

  /**
   * Pull credit report
   */
  async pullCreditReport(customerId: string, bureauProvider: string, requestPurpose?: string) {
    return apiClient.post<BureauReport>(`/customers/${customerId}/bureau/pull`, {
      bureau_provider: bureauProvider,
      request_purpose: requestPurpose
    })
  },

  /**
   * Get bureau history
   */
  async getBureauHistory(customerId: string, limit?: number) {
    return apiClient.get<BureauReport[]>(`/customers/${customerId}/bureau/history`, { 
      params: { limit } 
    })
  },

  /**
   * Get latest credit score
   */
  async getLatestCreditScore(customerId: string) {
    return apiClient.get<{ customer_id: number; credit_score: number }>(
      `/customers/${customerId}/bureau/latest-score`
    )
  },

  // ============================================================================
  // TIMELINE
  // ============================================================================

  /**
   * Get customer timeline
   */
  async getTimeline(customerId: string, params?: { 
    page?: number; 
    page_size?: number;
    activity_types?: string[];
    event_category?: string;
    important_only?: boolean;
  }) {
    return apiClient.get<PaginatedResponse<CustomerTimeline>>(`/customers/${customerId}/timeline`, { params })
  },

  /**
   * Get recent activities
   */
  async getRecentActivities(customerId: string, limit?: number) {
    return apiClient.get<CustomerTimeline[]>(`/customers/${customerId}/timeline/recent`, { 
      params: { limit } 
    })
  },

  /**
   * Get activity summary
   */
  async getActivitySummary(customerId: string, days?: number) {
    return apiClient.get<{ customer_id: number; days: number; activity_counts: Record<string, number> }>(
      `/customers/${customerId}/timeline/summary`,
      { params: { days } }
    )
  },

  /**
   * Log manual activity
   */
  async logActivity(customerId: string, data: {
    activity_type: string;
    title: string;
    description?: string;
    event_category?: string;
    is_important?: boolean;
  }) {
    return apiClient.post<CustomerTimeline>(`/customers/${customerId}/timeline`, data)
  },

  // ============================================================================
  // eKYC / AADHAAR
  // ============================================================================

  /**
   * Initiate Aadhaar OTP
   */
  async initiateAadhaarOTP(customerId: string, aadhaarNumber: string) {
    return apiClient.post<{ success: boolean; request_id: string; message: string; expires_at: string }>(
      `/customers/${customerId}/ekyc/aadhaar/otp/initiate`,
      { aadhaar_number: aadhaarNumber }
    )
  },

  /**
   * Verify Aadhaar OTP
   */
  async verifyAadhaarOTP(customerId: string, data: { aadhaar_number: string; otp: string; request_id: string }) {
    return apiClient.post<{ success: boolean; verified: boolean; message: string; ekyc_data?: any }>(
      `/customers/${customerId}/ekyc/aadhaar/otp/verify`,
      data
    )
  },

  /**
   * Biometric verification
   */
  async biometricVerification(customerId: string, data: { aadhaar_number: string; biometric_data: string; biometric_type: string }) {
    return apiClient.post<{ success: boolean; verified: boolean; message: string; ekyc_data?: any }>(
      `/customers/${customerId}/ekyc/aadhaar/biometric`,
      data
    )
  },

  // ============================================================================
  // DIGILOCKER
  // ============================================================================

  /**
   * Initiate DigiLocker authorization
   */
  async initiateDigiLocker(customerId: string, redirectUri: string) {
    return apiClient.post<{ authorization_url: string; state: string }>(
      `/customers/${customerId}/digilocker/authorize`,
      null,
      { params: { redirect_uri: redirectUri } }
    )
  },

  /**
   * Complete DigiLocker authorization
   */
  async completeDigiLocker(customerId: string, code: string, redirectUri: string) {
    return apiClient.post<{ success: boolean; access_token: string; expires_in: number; documents: any[] }>(
      `/customers/${customerId}/digilocker/complete`,
      { code, redirect_uri: redirectUri }
    )
  },

  /**
   * Get DigiLocker documents
   */
  async getDigiLockerDocuments(customerId: string, accessToken: string) {
    return apiClient.get<DigiLockerDocument[]>(
      `/customers/${customerId}/digilocker/documents`,
      { params: { access_token: accessToken } }
    )
  },

  /**
   * Fetch and store DigiLocker document
   */
  async fetchDigiLockerDocument(customerId: string, data: { access_token: string; document_uri: string; document_type_id: string }) {
    return apiClient.post<CustomerDocument>(`/customers/${customerId}/digilocker/documents/fetch`, data)
  },
}
