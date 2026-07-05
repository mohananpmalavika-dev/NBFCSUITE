/**
 * Loan Service
 * API calls for loan management
 */

import { apiClient } from '@/lib/api-client'
import type { 
  LoanProduct,
  LoanApplication,
  LoanAccount,
  LoanRepayment,
  CreateLoanApplicationRequest,
  PaginatedResponse,
  PaginationParams 
} from '@/types'

export const loanService = {
  // ============================================
  // Loan Products
  // ============================================

  async getProducts(params?: PaginationParams) {
    return apiClient.get<PaginatedResponse<LoanProduct>>('/loan-products', { params })
  },

  async getProduct(id: string) {
    return apiClient.get<LoanProduct>(`/loan-products/${id}`)
  },

  // ============================================
  // Loan Applications
  // ============================================

  async getApplications(params?: PaginationParams & { status?: string; customer_id?: string }) {
    return apiClient.get<PaginatedResponse<LoanApplication>>('/loan-applications', { params })
  },

  async getApplication(id: string) {
    return apiClient.get<LoanApplication>(`/loan-applications/${id}`)
  },

  async createApplication(data: CreateLoanApplicationRequest) {
    return apiClient.post<LoanApplication>('/loan-applications', data)
  },

  async updateApplication(id: string, data: Partial<CreateLoanApplicationRequest>) {
    return apiClient.put<LoanApplication>(`/loan-applications/${id}`, data)
  },

  async submitApplication(id: string) {
    return apiClient.post(`/loan-applications/${id}/submit`)
  },

  async approveApplication(id: string, remarks?: string) {
    return apiClient.post(`/loan-applications/${id}/approve`, { remarks })
  },

  async rejectApplication(id: string, remarks: string) {
    return apiClient.post(`/loan-applications/${id}/reject`, { remarks })
  },

  // ============================================
  // Loan Accounts
  // ============================================

  async getAccounts(params?: PaginationParams & { status?: string; customer_id?: string }) {
    return apiClient.get<PaginatedResponse<LoanAccount>>('/loan-accounts', { params })
  },

  async getAccount(id: string) {
    return apiClient.get<LoanAccount>(`/loan-accounts/${id}`)
  },

  async getAccountByNumber(accountNumber: string) {
    return apiClient.get<LoanAccount>(`/loan-accounts/by-number/${accountNumber}`)
  },

  // ============================================
  // Loan Repayments
  // ============================================

  async getRepayments(loanAccountId: string, params?: PaginationParams) {
    return apiClient.get<PaginatedResponse<LoanRepayment>>(
      `/loan-accounts/${loanAccountId}/repayments`,
      { params }
    )
  },

  async createRepayment(loanAccountId: string, data: any) {
    return apiClient.post<LoanRepayment>(
      `/loan-accounts/${loanAccountId}/repayments`,
      data
    )
  },

  // ============================================
  // Statistics
  // ============================================

  async getLoanStats() {
    return apiClient.get('/loans/statistics')
  },

  async getCollectionStats() {
    return apiClient.get('/collections/statistics')
  },
}
